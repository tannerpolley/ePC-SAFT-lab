#include "equilibrium/blocks/phase_equilibrium_residual_block.h"

#include "eos/core_internal.h"

#include <algorithm>
#include <cmath>
#include <numeric>
#include <sstream>

namespace epcsaft::native::equilibrium_nlp {

namespace {

constexpr double kNonzeroTolerance = 0.0;

void require_positive_finite(double value, const std::string& label) {
    if (std::isfinite(value) && value > 0.0) {
        return;
    }
    throw ::ValueError(label + " must be positive and finite.");
}

void validate_phase_inputs(
    const std::vector<std::vector<double>>& phase_amounts,
    const std::vector<double>& volumes
) {
    if (phase_amounts.size() < 2) {
        throw ::ValueError("Phase-equilibrium residual block requires at least two phases.");
    }
    const std::size_t species_count = phase_amounts.front().size();
    if (species_count == 0) {
        throw ::ValueError("Phase-equilibrium residual block requires at least one species.");
    }
    if (volumes.size() != phase_amounts.size()) {
        throw ::ValueError("Phase-equilibrium residual block volume count must match phase count.");
    }
    for (std::size_t phase = 0; phase < phase_amounts.size(); ++phase) {
        if (phase_amounts[phase].size() != species_count) {
            throw ::ValueError("Phase-equilibrium residual block phase amount sizes must match.");
        }
        require_positive_finite(volumes[phase], "Phase-equilibrium residual block phase volume");
        for (double amount : phase_amounts[phase]) {
            require_positive_finite(amount, "Phase-equilibrium residual block phase species amount");
        }
    }
}

std::vector<double> composition_from_amounts(const std::vector<double>& amounts, double total_amount) {
    std::vector<double> composition;
    composition.reserve(amounts.size());
    for (double amount : amounts) {
        composition.push_back(amount / total_amount);
    }
    return composition;
}

std::string sensitivity_failure_message(
    const PhaseStateCompositionSensitivityResult& sensitivity,
    std::size_t phase,
    std::size_t species_count
) {
    std::ostringstream message;
    message << "Phase-equilibrium residual block exact fugacity sensitivity failed for phase "
            << phase << " with " << species_count << " species";
    if (!sensitivity.message.empty()) {
        message << ": " << sensitivity.message;
    }
    return message.str();
}

std::size_t local_index(std::size_t species_count, std::size_t row, std::size_t col) {
    return row * (species_count + 1) + col;
}

std::size_t local_hessian_index(
    std::size_t species_count,
    std::size_t component,
    std::size_t row,
    std::size_t col
) {
    const std::size_t local_variable_count = species_count + 1;
    return component * local_variable_count * local_variable_count + row * local_variable_count + col;
}

int count_nonzero(const std::vector<double>& values) {
    return static_cast<int>(std::count_if(values.begin(), values.end(), [](double value) {
        return std::abs(value) > kNonzeroTolerance;
    }));
}

struct PhaseLocalReducedFugacity {
    std::string backend;
    std::vector<double> composition;
    std::vector<double> reduced_ln_fugacity;
    std::vector<double> jacobian_row_major;
    std::vector<double> hessian_tensor_row_major;
    std::vector<double> density_amount_jacobian;
    std::vector<double> composition_amount_jacobian;
};

PhaseLocalReducedFugacity evaluate_local_reduced_fugacity(
    const add_args& args,
    double temperature,
    const std::vector<double>& amounts,
    double volume,
    std::size_t phase_index
) {
    const std::size_t species_count = amounts.size();
    const std::size_t local_variable_count = species_count + 1;
    const double total_amount = std::accumulate(amounts.begin(), amounts.end(), 0.0);
    require_positive_finite(total_amount, "Phase-equilibrium residual block phase total amount");
    const double density = total_amount / volume;
    require_positive_finite(density, "Phase-equilibrium residual block phase molar density");
    const std::vector<double> composition = composition_from_amounts(amounts, total_amount);

    const PhaseStateCompositionSensitivityResult sensitivity =
        phase_state_ln_fugacity_explicit_density_composition_sensitivity_cpp(
            temperature,
            density,
            composition,
            args
        );
    if (!sensitivity.supported
        || sensitivity.ln_fugacity.size() != species_count
        || sensitivity.ln_fugacity_density_derivative.size() != species_count
        || sensitivity.ln_fugacity_density_second_derivative.size() != species_count
        || sensitivity.ln_fugacity_density_composition_cross_derivative.size() != species_count * species_count
        || sensitivity.fixed_density_jacobian_row_major.size() != species_count * species_count
        || sensitivity.fixed_density_hessian_tensor_row_major.size()
            != species_count * species_count * species_count) {
        throw ::ValueError(sensitivity_failure_message(sensitivity, phase_index, species_count));
    }

    std::vector<double> q_jacobian((species_count + 1) * local_variable_count, 0.0);
    std::vector<double> q_hessian(
        (species_count + 1) * local_variable_count * local_variable_count,
        0.0
    );
    const auto qj = [&](std::size_t q_index, std::size_t variable) -> double& {
        return q_jacobian[q_index * local_variable_count + variable];
    };
    const auto qh = [&](std::size_t q_index, std::size_t first, std::size_t second) -> double& {
        return q_hessian[
            q_index * local_variable_count * local_variable_count
            + first * local_variable_count
            + second
        ];
    };

    for (std::size_t species = 0; species < species_count; ++species) {
        qj(0, species) = 1.0 / volume;
        qj(1 + species, species) = (1.0 - composition[species]) / total_amount;
        for (std::size_t other = 0; other < species_count; ++other) {
            if (other != species) {
                qj(1 + other, species) = -composition[other] / total_amount;
            }
        }
    }
    qj(0, species_count) = -total_amount / (volume * volume);
    for (std::size_t amount_col = 0; amount_col < species_count; ++amount_col) {
        qh(0, amount_col, species_count) = -1.0 / (volume * volume);
        qh(0, species_count, amount_col) = -1.0 / (volume * volume);
    }
    qh(0, species_count, species_count) = 2.0 * total_amount / (volume * volume * volume);
    for (std::size_t component = 0; component < species_count; ++component) {
        for (std::size_t first = 0; first < species_count; ++first) {
            for (std::size_t second = 0; second < species_count; ++second) {
                const double delta_first = component == first ? 1.0 : 0.0;
                const double delta_second = component == second ? 1.0 : 0.0;
                qh(1 + component, first, second) =
                    (2.0 * composition[component] - delta_first - delta_second)
                    / (total_amount * total_amount);
            }
        }
    }

    PhaseLocalReducedFugacity out;
    out.backend = sensitivity.backend;
    out.composition = composition;
    out.reduced_ln_fugacity.assign(species_count, 0.0);
    out.jacobian_row_major.assign(species_count * local_variable_count, 0.0);
    out.hessian_tensor_row_major.assign(
        species_count * local_variable_count * local_variable_count,
        0.0
    );
    out.density_amount_jacobian.assign(local_variable_count, 0.0);
    for (std::size_t variable = 0; variable < local_variable_count; ++variable) {
        out.density_amount_jacobian[variable] = qj(0, variable);
    }
    out.composition_amount_jacobian.assign(species_count * local_variable_count, 0.0);
    for (std::size_t component = 0; component < species_count; ++component) {
        for (std::size_t variable = 0; variable < local_variable_count; ++variable) {
            out.composition_amount_jacobian[component * local_variable_count + variable] =
                qj(1 + component, variable);
        }
    }

    for (std::size_t component = 0; component < species_count; ++component) {
        out.reduced_ln_fugacity[component] =
            std::log(composition[component]) + sensitivity.ln_fugacity[component];
        std::vector<double> reduced_q_gradient(species_count + 1, 0.0);
        std::vector<double> reduced_q_hessian((species_count + 1) * (species_count + 1), 0.0);
        const auto rq_hessian_index = [species_count](std::size_t row, std::size_t col) {
            return row * (species_count + 1) + col;
        };
        reduced_q_gradient[0] = sensitivity.ln_fugacity_density_derivative[component];
        reduced_q_hessian[rq_hessian_index(0, 0)] =
            sensitivity.ln_fugacity_density_second_derivative[component];
        for (std::size_t species = 0; species < species_count; ++species) {
            const double ideal_gradient = component == species ? 1.0 / composition[component] : 0.0;
            const std::size_t composition_q = 1 + species;
            reduced_q_gradient[composition_q] =
                ideal_gradient
                + sensitivity.fixed_density_jacobian_row_major[component * species_count + species];
            const double density_composition_cross =
                sensitivity.ln_fugacity_density_composition_cross_derivative[
                    component * species_count + species
                ];
            reduced_q_hessian[rq_hessian_index(0, composition_q)] = density_composition_cross;
            reduced_q_hessian[rq_hessian_index(composition_q, 0)] = density_composition_cross;
            for (std::size_t other = 0; other < species_count; ++other) {
                const double ideal_hessian =
                    component == species && component == other
                    ? -1.0 / (composition[component] * composition[component])
                    : 0.0;
                reduced_q_hessian[rq_hessian_index(composition_q, 1 + other)] =
                    ideal_hessian
                    + sensitivity.fixed_density_hessian_tensor_row_major[
                        component * species_count * species_count
                        + species * species_count
                        + other
                    ];
            }
        }
        for (std::size_t variable = 0; variable < local_variable_count; ++variable) {
            double gradient_value = 0.0;
            for (std::size_t q_index = 0; q_index < species_count + 1; ++q_index) {
                gradient_value += reduced_q_gradient[q_index] * qj(q_index, variable);
            }
            out.jacobian_row_major[component * local_variable_count + variable] = gradient_value;
            for (std::size_t other_variable = 0; other_variable < local_variable_count; ++other_variable) {
                double hessian_value = 0.0;
                for (std::size_t left_q = 0; left_q < species_count + 1; ++left_q) {
                    hessian_value += reduced_q_gradient[left_q] * qh(left_q, variable, other_variable);
                    for (std::size_t right_q = 0; right_q < species_count + 1; ++right_q) {
                        hessian_value += reduced_q_hessian[rq_hessian_index(left_q, right_q)]
                            * qj(left_q, variable)
                            * qj(right_q, other_variable);
                    }
                }
                out.hessian_tensor_row_major[local_hessian_index(
                    species_count,
                    component,
                    variable,
                    other_variable
                )] = hessian_value;
            }
        }
    }
    return out;
}

}  // namespace

PhaseEquilibriumResidualBlockResult evaluate_phase_equilibrium_residual_block(
    const add_args& args,
    double temperature,
    double target_pressure,
    const std::vector<std::vector<double>>& phase_amounts,
    const std::vector<double>& volumes
) {
    (void)target_pressure;
    require_positive_finite(temperature, "Phase-equilibrium residual block temperature");
    validate_phase_inputs(phase_amounts, volumes);

    const std::size_t phase_count = phase_amounts.size();
    const std::size_t species_count = phase_amounts.front().size();
    const std::size_t local_variable_count = species_count + 1;
    const std::size_t variable_count = phase_count * local_variable_count;
    const std::size_t residual_count = (phase_count - 1) * species_count;
    std::vector<PhaseLocalReducedFugacity> phases;
    phases.reserve(phase_count);
    for (std::size_t phase = 0; phase < phase_count; ++phase) {
        phases.push_back(evaluate_local_reduced_fugacity(args, temperature, phase_amounts[phase], volumes[phase], phase));
    }

    PhaseEquilibriumResidualBlockResult result;
    result.block = "phase_equilibrium_residual";
    result.derivative_backend = phases.front().backend;
    for (const auto& phase : phases) {
        if (phase.backend != result.derivative_backend) {
            result.derivative_backend = "mixed_cppad_explicit_density";
            break;
        }
    }
    result.phase_count = static_cast<int>(phase_count);
    result.species_count = static_cast<int>(species_count);
    result.variable_count = static_cast<int>(variable_count);
    result.constraint_count = static_cast<int>(residual_count);
    result.residual_count = static_cast<int>(residual_count);
    result.full_square_constraint_count = static_cast<int>(species_count + phase_count + residual_count);
    result.local_jacobian_rows = static_cast<int>(species_count);
    result.local_jacobian_cols = static_cast<int>(local_variable_count);
    result.local_hessian_rows = static_cast<int>(species_count);
    result.local_hessian_cols = static_cast<int>(local_variable_count);
    result.local_hessian_depth = static_cast<int>(local_variable_count);
    result.global_jacobian_rows = static_cast<int>(residual_count);
    result.global_jacobian_cols = static_cast<int>(variable_count);
    result.global_hessian_rows = static_cast<int>(residual_count);
    result.global_hessian_cols = static_cast<int>(variable_count);
    result.global_hessian_depth = static_cast<int>(variable_count);
    result.exact_jacobian_available = true;
    result.exact_hessian_available = true;
    result.reduced_ln_fugacity_values.reserve(phase_count * species_count);
    result.residuals.assign(residual_count, 0.0);
    result.jacobian_row_major.assign(residual_count * variable_count, 0.0);
    result.hessian_tensor_row_major.assign(residual_count * variable_count * variable_count, 0.0);
    result.density_amount_jacobian.reserve(phase_count * local_variable_count);
    result.composition_amount_jacobian.reserve(phase_count * species_count * local_variable_count);
    result.phase_minimum_compositions.reserve(phase_count);
    for (const auto& phase : phases) {
        result.reduced_ln_fugacity_values.insert(
            result.reduced_ln_fugacity_values.end(),
            phase.reduced_ln_fugacity.begin(),
            phase.reduced_ln_fugacity.end()
        );
        result.density_amount_jacobian.insert(
            result.density_amount_jacobian.end(),
            phase.density_amount_jacobian.begin(),
            phase.density_amount_jacobian.end()
        );
        result.composition_amount_jacobian.insert(
            result.composition_amount_jacobian.end(),
            phase.composition_amount_jacobian.begin(),
            phase.composition_amount_jacobian.end()
        );
        result.phase_minimum_compositions.push_back(
            *std::min_element(phase.composition.begin(), phase.composition.end())
        );
    }

    const auto residual_row = [species_count](std::size_t phase, std::size_t species) {
        return (phase - 1) * species_count + species;
    };
    for (std::size_t phase = 1; phase < phase_count; ++phase) {
        const std::size_t phase_col_offset = phase * local_variable_count;
        for (std::size_t species = 0; species < species_count; ++species) {
            const std::size_t row = residual_row(phase, species);
            result.residual_names.push_back(
                "phase_" + std::to_string(phase)
                + ".reduced_ln_fugacity_" + std::to_string(species)
                + "_minus_phase_0"
            );
            result.residuals[row] =
                phases[phase].reduced_ln_fugacity[species] - phases[0].reduced_ln_fugacity[species];
            for (std::size_t local_col = 0; local_col < local_variable_count; ++local_col) {
                result.jacobian_row_major[row * variable_count + local_col] =
                    -phases[0].jacobian_row_major[local_index(species_count, species, local_col)];
                result.jacobian_row_major[row * variable_count + phase_col_offset + local_col] =
                    phases[phase].jacobian_row_major[local_index(species_count, species, local_col)];
            }
            for (std::size_t local_row = 0; local_row < local_variable_count; ++local_row) {
                for (std::size_t local_col = 0; local_col < local_variable_count; ++local_col) {
                    result.hessian_tensor_row_major[
                        row * variable_count * variable_count + local_row * variable_count + local_col
                    ] = -phases[0].hessian_tensor_row_major[
                        local_hessian_index(species_count, species, local_row, local_col)
                    ];
                    result.hessian_tensor_row_major[
                        row * variable_count * variable_count
                        + (phase_col_offset + local_row) * variable_count
                        + phase_col_offset
                        + local_col
                    ] = phases[phase].hessian_tensor_row_major[
                        local_hessian_index(species_count, species, local_row, local_col)
                    ];
                }
            }
        }
    }
    result.residual_jacobian_nonzero_count = count_nonzero(result.jacobian_row_major);
    result.residual_hessian_nonzero_count = count_nonzero(result.hessian_tensor_row_major);
    return result;
}

}  // namespace epcsaft::native::equilibrium_nlp
