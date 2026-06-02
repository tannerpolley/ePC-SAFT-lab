#include "equilibrium/derivatives/phase_block_derivatives.h"

#include <exception>

#include "eos/core_internal.h"
#include "equilibrium/derivatives/route_second_order.h"

#include <algorithm>
#include <cmath>
#include <string>
#include <utility>

namespace epcsaft::native::equilibrium_nlp {

namespace phase_block_derivatives_detail {

bool has_active_association_sites(const ::add_args& args) {
    for (int sites : args.assoc_num) {
        if (sites > 0) {
            return true;
        }
    }
    return false;
}

::add_args without_solved_association(const ::add_args& original) {
    ::add_args args = original;
    args.e_assoc.clear();
    args.vol_a.clear();
    args.assoc_num.clear();
    args.assoc_matrix.clear();
    args.k_hb.clear();
    return args;
}

void require_local_phase_bundle_shape(
    const EosLocalPhaseDerivativeBundle& bundle,
    int expected_variable_count,
    const std::string& label
) {
    if (bundle.variable_count != expected_variable_count
        || bundle.gradient.size() != static_cast<std::size_t>(expected_variable_count)
        || bundle.hessian_row_major.size()
            != static_cast<std::size_t>(expected_variable_count * expected_variable_count)) {
        throw ::ValueError(label + " shape did not match the phase variable model.");
    }
    require_third_derivative_tensor(
        bundle.third_derivative_tensor_row_major,
        expected_variable_count,
        label + " third-derivative tensor"
    );
}

}  // namespace phase_block_derivatives_detail

void populate_eos_phase_block_derivatives(
    EosPhaseBlockResult& result,
    const ::add_args& args,
    double temperature,
    double target_pressure,
    const std::vector<double>& amounts,
    double volume
) {
    const int nvars = static_cast<int>(amounts.size()) + 1;
    if (phase_block_derivatives_detail::has_active_association_sites(args)) {
        const ::add_args non_associating_args = phase_block_derivatives_detail::without_solved_association(args);
        std::vector<double> base_hessian;
        std::vector<double> base_third_derivative;
        const EosLocalPhaseDerivativeBundle base_bundle = eos_local_phase_helmholtz_derivatives_cpp(
            temperature,
            amounts,
            volume,
            non_associating_args,
            false
        );
        phase_block_derivatives_detail::require_local_phase_bundle_shape(
            base_bundle,
            nvars,
            "EOS phase base local Helmholtz derivative bundle"
        );
        base_hessian = base_bundle.hessian_row_major;
        base_third_derivative = base_bundle.third_derivative_tensor_row_major;
        const EosPhaseAssociationDerivativeCorrectionResult association_corrections =
            eos_phase_association_derivative_corrections_cpp(temperature, amounts, volume, args);
        if (!association_corrections.active) {
            const std::string message = association_corrections.message.empty()
                ? "EOS phase association derivative corrections were not available."
                : association_corrections.message;
            throw ::ValueError(message);
        }
        if (association_corrections.helmholtz_hessian_row_major.size()
                != static_cast<std::size_t>(nvars * nvars)
            || association_corrections.pressure_hessian_row_major.size()
                != static_cast<std::size_t>(nvars * nvars)) {
            throw ::ValueError("EOS phase association derivative correction shape did not match variables.");
        }
        const EosPhasePressureDerivativeResult pressure_derivatives =
            eos_phase_pressure_derivatives_cpp(temperature, amounts, volume, args);
        if (!pressure_derivatives.supported) {
            const std::string message = pressure_derivatives.message.empty()
                ? "EOS phase pressure derivatives were not available for associating phase."
                : pressure_derivatives.message;
            throw ::ValueError(message);
        }
        if (pressure_derivatives.pressure_jacobian_row_major.size() != static_cast<std::size_t>(nvars)) {
            throw ::ValueError("EOS phase pressure derivative shape did not match the phase variable model.");
        }
        result.objective_curvature_backend = association_corrections.backend;
        result.objective_curvature_rows = nvars;
        result.objective_curvature_cols = nvars;
        result.objective_curvature_row_major = std::move(base_hessian);
        for (std::size_t index = 0; index < result.objective_curvature_row_major.size(); ++index) {
            result.objective_curvature_row_major[index] +=
                association_corrections.helmholtz_hessian_row_major[index];
        }
        result.constraint_jacobian_backend = pressure_derivatives.backend;
        result.constraint_jacobian_rows = 1;
        result.constraint_jacobian_cols = nvars;
        result.constraint_jacobian_row_major = pressure_derivatives.pressure_jacobian_row_major;
        result.pressure_density_derivative = pressure_derivatives.pressure_density_derivative;
        result.pressure_hessian_backend = association_corrections.backend;
        result.pressure_hessian_rows = nvars;
        result.pressure_hessian_cols = nvars;
        result.pressure_hessian_row_major.assign(static_cast<std::size_t>(nvars * nvars), 0.0);
        const int volume_row = nvars - 1;
        for (int row = 0; row < nvars; ++row) {
            for (int col = 0; col < nvars; ++col) {
                result.pressure_hessian_row_major[static_cast<std::size_t>(row * nvars + col)] =
                    -result.gas_constant_temperature * base_third_derivative[
                        static_cast<std::size_t>(volume_row * nvars * nvars + row * nvars + col)
                    ] + association_corrections.pressure_hessian_row_major[
                        static_cast<std::size_t>(row * nvars + col)
                    ];
            }
        }
        symmetrize_square_block(result.pressure_hessian_row_major, nvars);
    } else {
        double cppad_objective = 0.0;
        std::vector<double> cppad_gradient;
        std::vector<double> cppad_hessian;
        std::vector<double> cppad_third_derivative;
        const EosLocalPhaseDerivativeBundle cppad_bundle = eos_local_phase_helmholtz_derivatives_cpp(
            temperature,
            amounts,
            volume,
            args,
            false
        );
        phase_block_derivatives_detail::require_local_phase_bundle_shape(
            cppad_bundle,
            nvars,
            "EOS phase local Helmholtz derivative bundle"
        );
        cppad_objective = cppad_bundle.helmholtz + target_pressure * volume / result.gas_constant_temperature;
        cppad_gradient = cppad_bundle.gradient;
        cppad_gradient[static_cast<std::size_t>(nvars - 1)] += target_pressure / result.gas_constant_temperature;
        cppad_hessian = cppad_bundle.hessian_row_major;
        cppad_third_derivative = cppad_bundle.third_derivative_tensor_row_major;
        if (cppad_gradient.size() != result.gradient.size()) {
            throw ::ValueError("EOS phase objective CppAD derivative shape did not match the phase variable model.");
        }
        const double objective_scale = std::max(1.0, std::abs(result.objective));
        if (std::abs(cppad_objective - result.objective) > 1.0e-8 * objective_scale) {
            throw ::ValueError("EOS phase objective CppAD value did not match the analytical block value.");
        }
        result.objective_curvature_backend = "cppad";
        result.objective_curvature_rows = nvars;
        result.objective_curvature_cols = nvars;
        result.objective_curvature_row_major = std::move(cppad_hessian);
        result.objective_third_derivative_backend = "cppad";
        result.objective_third_derivative_rows = nvars;
        result.objective_third_derivative_cols = nvars;
        result.objective_third_derivative_tensor_row_major = cppad_third_derivative;
        result.constraint_jacobian_backend = "cppad";
        result.constraint_jacobian_rows = 1;
        result.constraint_jacobian_cols = nvars;
        result.constraint_jacobian_row_major.reserve(static_cast<std::size_t>(nvars));
        const int volume_row = nvars - 1;
        for (int col = 0; col < nvars; ++col) {
            result.constraint_jacobian_row_major.push_back(
                -result.gas_constant_temperature * result.objective_curvature_row_major[
                    static_cast<std::size_t>(volume_row * nvars + col)
                ]
            );
        }
        result.pressure_density_derivative =
            -result.constraint_jacobian_row_major[static_cast<std::size_t>(volume_row)]
            * result.volume / result.density;
        result.pressure_hessian_backend = "cppad";
        result.pressure_hessian_rows = nvars;
        result.pressure_hessian_cols = nvars;
        result.pressure_hessian_row_major.assign(static_cast<std::size_t>(nvars * nvars), 0.0);
        for (int row = 0; row < nvars; ++row) {
            for (int col = 0; col < nvars; ++col) {
                result.pressure_hessian_row_major[static_cast<std::size_t>(row * nvars + col)] =
                    -result.gas_constant_temperature * cppad_third_derivative[
                        static_cast<std::size_t>(volume_row * nvars * nvars + row * nvars + col)
                    ];
            }
        }
        symmetrize_square_block(result.pressure_hessian_row_major, nvars);
    }
    result.pressure_jacobian_backend = result.constraint_jacobian_backend;
    result.pressure_jacobian_rows = result.constraint_jacobian_rows;
    result.pressure_jacobian_cols = result.constraint_jacobian_cols;
    result.pressure_jacobian_row_major = result.constraint_jacobian_row_major;
}

TemperatureRoutePhaseBlock evaluate_temperature_route_phase_block(
    const ::add_args& args,
    double temperature,
    double target_pressure,
    const std::vector<double>& amounts,
    double volume
) {
    TemperatureRoutePhaseBlock out;
    out.block = evaluate_eos_phase_block(args, temperature, target_pressure, amounts, volume);
    const EosLocalPhaseDerivativeBundle cppad_bundle = eos_local_phase_helmholtz_derivatives_cpp(
        temperature,
        amounts,
        volume,
        args,
        true
    );
    const int local_variable_count = static_cast<int>(amounts.size()) + 2;
    phase_block_derivatives_detail::require_local_phase_bundle_shape(
        cppad_bundle,
        local_variable_count,
        "fixed-pressure temperature route local Helmholtz derivative bundle"
    );
    out.gradient = cppad_bundle.gradient;
    out.objective_hessian_row_major = cppad_bundle.hessian_row_major;
    out.objective_third_derivative_tensor_row_major = cppad_bundle.third_derivative_tensor_row_major;

    const int volume_row = local_variable_count - 2;
    const int temperature_col = local_variable_count - 1;
    const double gas_constant = kb * N_AV;
    const double pressure_work_scale = target_pressure / gas_constant;
    const double pressure_work = pressure_work_scale * volume / temperature;
    double cppad_objective = cppad_bundle.helmholtz + pressure_work;
    out.gradient[static_cast<std::size_t>(volume_row)] += pressure_work_scale / temperature;
    out.gradient[static_cast<std::size_t>(temperature_col)] +=
        -pressure_work_scale * volume / (temperature * temperature);
    const auto hessian_index = [local_variable_count](int row, int col) {
        return static_cast<std::size_t>(row * local_variable_count + col);
    };
    out.objective_hessian_row_major[hessian_index(volume_row, temperature_col)] +=
        -pressure_work_scale / (temperature * temperature);
    out.objective_hessian_row_major[hessian_index(temperature_col, volume_row)] +=
        -pressure_work_scale / (temperature * temperature);
    out.objective_hessian_row_major[hessian_index(temperature_col, temperature_col)] +=
        2.0 * pressure_work_scale * volume / (temperature * temperature * temperature);
    const auto third_index = [local_variable_count](int first, int second, int third) {
        return static_cast<std::size_t>(
            first * local_variable_count * local_variable_count
            + second * local_variable_count
            + third
        );
    };
    const double volume_temperature_temperature =
        2.0 * pressure_work_scale / (temperature * temperature * temperature);
    out.objective_third_derivative_tensor_row_major[
        third_index(volume_row, temperature_col, temperature_col)
    ] += volume_temperature_temperature;
    out.objective_third_derivative_tensor_row_major[
        third_index(temperature_col, volume_row, temperature_col)
    ] += volume_temperature_temperature;
    out.objective_third_derivative_tensor_row_major[
        third_index(temperature_col, temperature_col, volume_row)
    ] += volume_temperature_temperature;
    out.objective_third_derivative_tensor_row_major[
        third_index(temperature_col, temperature_col, temperature_col)
    ] += -6.0 * pressure_work_scale * volume
        / (temperature * temperature * temperature * temperature);

    const double objective_scale = std::max(1.0, std::abs(out.block.objective));
    if (std::abs(cppad_objective - out.block.objective) > 1.0e-8 * objective_scale) {
        throw ::ValueError("fixed-pressure temperature route CppAD value did not match the EOS block value.");
    }

    out.pressure_jacobian_row_major.reserve(static_cast<std::size_t>(local_variable_count));
    for (int col = 0; col < local_variable_count; ++col) {
        double value = -out.block.gas_constant_temperature
            * out.objective_hessian_row_major[static_cast<std::size_t>(volume_row * local_variable_count + col)];
        if (col == temperature_col) {
            value -= gas_constant * out.gradient[static_cast<std::size_t>(volume_row)];
        }
        out.pressure_jacobian_row_major.push_back(value);
    }
    out.pressure_hessian_row_major.assign(
        static_cast<std::size_t>(local_variable_count * local_variable_count),
        0.0
    );
    for (int row = 0; row < local_variable_count; ++row) {
        for (int col = 0; col < local_variable_count; ++col) {
            double value = -out.block.gas_constant_temperature
                * out.objective_third_derivative_tensor_row_major[
                    static_cast<std::size_t>(volume_row * local_variable_count * local_variable_count
                        + row * local_variable_count + col)
                ];
            if (row == temperature_col) {
                value -= gas_constant * out.objective_hessian_row_major[
                    static_cast<std::size_t>(volume_row * local_variable_count + col)
                ];
            }
            if (col == temperature_col) {
                value -= gas_constant * out.objective_hessian_row_major[
                    static_cast<std::size_t>(volume_row * local_variable_count + row)
                ];
            }
            out.pressure_hessian_row_major[
                static_cast<std::size_t>(row * local_variable_count + col)
            ] = value;
        }
    }
    symmetrize_square_block(out.pressure_hessian_row_major, local_variable_count);
    return out;
}

}  // namespace epcsaft::native::equilibrium_nlp
