#include "eos/properties/residual_helmholtz_internal.h"
#include "eos/properties/residual_association_sensitivities.h"
#include "eos/properties/residual_backend_helpers.h"
#include <algorithm>
#include <cmath>
#include <string>
#include <vector>
void eos_phase_objective_derivatives_cpp(
    double t,
    double target_pressure,
    const vector<double> &amounts,
    double volume,
    const add_args &cppargs,
    double *objective,
    vector<double> *gradient,
    vector<double> *hessian_row_major,
    vector<double> *third_derivative_tensor_row_major
) {
#ifdef EPCSAFT_HAS_CPPAD
    using CppADScalar = CppAD::AD<double>;
    if (!objective || !gradient || !hessian_row_major) {
        throw ValueError("EOS phase objective derivative output buffers must be valid.");
    }
    if (!cppargs.assoc_num.empty()) {
        for (int sites : cppargs.assoc_num) {
            if (sites > 0) {
                throw ValueError("unsupported: EOS phase objective Hessian requires association implicit variables.");
            }
        }
    }
    if (!cppargs.z.empty() && cppargs.born_model > 1) {
        throw ValueError("unsupported: EOS phase objective Hessian supports direct Born model=1 formulas only.");
    }
    const int ncomp = static_cast<int>(amounts.size());
    const int nvars = ncomp + 1;
    std::vector<CppADScalar> variables(static_cast<std::size_t>(nvars));
    for (int index = 0; index < ncomp; ++index) {
        variables[static_cast<std::size_t>(index)] = amounts[static_cast<std::size_t>(index)];
    }
    variables[static_cast<std::size_t>(ncomp)] = volume;
    CppAD::Independent(variables);

    CppADScalar total_amount = scalar_constant<CppADScalar>(0.0);
    for (int index = 0; index < ncomp; ++index) {
        total_amount += variables[static_cast<std::size_t>(index)];
    }
    const CppADScalar phase_volume = variables[static_cast<std::size_t>(ncomp)];
    const CppADScalar rho = total_amount / phase_volume;
    std::vector<CppADScalar> composition(static_cast<std::size_t>(ncomp));
    for (int index = 0; index < ncomp; ++index) {
        composition[static_cast<std::size_t>(index)] = variables[static_cast<std::size_t>(index)] / total_amount;
    }

    CppADScalar ideal = scalar_constant<CppADScalar>(0.0);
    for (int index = 0; index < ncomp; ++index) {
        const CppADScalar amount = variables[static_cast<std::size_t>(index)];
        ideal += amount * (CppAD::log(amount / phase_volume) - scalar_constant<CppADScalar>(1.0));
    }
    const auto contributions = ares_detail::ares_contributions_scalar_cpp(t, rho, composition, cppargs);
    const CppADScalar residual = total_amount
        * (contributions.hc + contributions.disp + contributions.assoc + contributions.ion + contributions.born);
    const CppADScalar pressure_work = target_pressure * phase_volume / (kb * N_AV * t);
    std::vector<CppADScalar> outputs(1);
    outputs[0] = ideal + residual + pressure_work;

    CppAD::ADFun<double> function(variables, outputs);
    std::vector<double> point(amounts.begin(), amounts.end());
    point.push_back(volume);
    auto value = function.Forward(0, point);
    auto jacobian = function.Jacobian(point);
    auto hessian = function.Hessian(point, 0);
    if (third_derivative_tensor_row_major) {
        *third_derivative_tensor_row_major =
            ares_detail::scalar_function_third_derivative_tensor_cppad(function, point);
    }

    *objective = value.at(0);
    *gradient = std::move(jacobian);
    *hessian_row_major = std::move(hessian);
#else
    (void)t;
    (void)target_pressure;
    (void)amounts;
    (void)volume;
    (void)cppargs;
    (void)objective;
    (void)gradient;
    (void)hessian_row_major;
    (void)third_derivative_tensor_row_major;
    throw ValueError("EOS phase objective Hessian requires CppAD support.");
#endif
}

void eos_phase_temperature_variable_derivatives_cpp(
    double t,
    double target_pressure,
    const vector<double> &amounts,
    double volume,
    const add_args &cppargs,
    double *objective,
    vector<double> *gradient,
    vector<double> *hessian_row_major,
    vector<double> *third_derivative_tensor_row_major
) {
#ifdef EPCSAFT_HAS_CPPAD
    using CppADScalar = CppAD::AD<double>;
    if (!objective || !gradient || !hessian_row_major) {
        throw ValueError("EOS phase variable-temperature derivative output buffers must be valid.");
    }
    if (!cppargs.assoc_num.empty()) {
        for (int sites : cppargs.assoc_num) {
            if (sites > 0) {
                throw ValueError("unsupported: EOS phase temperature route Hessian requires association implicit variables.");
            }
        }
    }
    if (!cppargs.z.empty() && cppargs.born_model > 1) {
        throw ValueError("unsupported: EOS phase temperature route Hessian supports direct Born model=1 formulas only.");
    }
    const int ncomp = static_cast<int>(amounts.size());
    const int nvars = ncomp + 2;
    std::vector<CppADScalar> variables(static_cast<std::size_t>(nvars));
    for (int index = 0; index < ncomp; ++index) {
        variables[static_cast<std::size_t>(index)] = amounts[static_cast<std::size_t>(index)];
    }
    variables[static_cast<std::size_t>(ncomp)] = volume;
    variables[static_cast<std::size_t>(ncomp + 1)] = t;
    CppAD::Independent(variables);

    CppADScalar total_amount = scalar_constant<CppADScalar>(0.0);
    for (int index = 0; index < ncomp; ++index) {
        total_amount += variables[static_cast<std::size_t>(index)];
    }
    const CppADScalar phase_volume = variables[static_cast<std::size_t>(ncomp)];
    const CppADScalar temperature = variables[static_cast<std::size_t>(ncomp + 1)];
    const CppADScalar rho = total_amount / phase_volume;
    std::vector<CppADScalar> composition(static_cast<std::size_t>(ncomp));
    for (int index = 0; index < ncomp; ++index) {
        composition[static_cast<std::size_t>(index)] = variables[static_cast<std::size_t>(index)] / total_amount;
    }

    CppADScalar ideal = scalar_constant<CppADScalar>(0.0);
    for (int index = 0; index < ncomp; ++index) {
        const CppADScalar amount = variables[static_cast<std::size_t>(index)];
        ideal += amount * (CppAD::log(amount / phase_volume) - scalar_constant<CppADScalar>(1.0));
    }
    const auto contributions = ares_detail::ares_contributions_scalar_cpp(temperature, rho, composition, cppargs);
    const CppADScalar residual = total_amount
        * (contributions.hc + contributions.disp + contributions.assoc + contributions.ion + contributions.born);
    const CppADScalar pressure_work = target_pressure * phase_volume / (kb * N_AV * temperature);
    std::vector<CppADScalar> outputs(1);
    outputs[0] = ideal + residual + pressure_work;

    CppAD::ADFun<double> function(variables, outputs);
    std::vector<double> point(amounts.begin(), amounts.end());
    point.push_back(volume);
    point.push_back(t);
    auto value = function.Forward(0, point);
    auto jacobian = function.Jacobian(point);
    auto hessian = function.Hessian(point, 0);
    if (third_derivative_tensor_row_major) {
        *third_derivative_tensor_row_major =
            ares_detail::scalar_function_third_derivative_tensor_cppad(function, point);
    }

    *objective = value.at(0);
    *gradient = std::move(jacobian);
    *hessian_row_major = std::move(hessian);
#else
    (void)t;
    (void)target_pressure;
    (void)amounts;
    (void)volume;
    (void)cppargs;
    (void)objective;
    (void)gradient;
    (void)hessian_row_major;
    (void)third_derivative_tensor_row_major;
    throw ValueError("EOS phase variable-temperature Hessian requires CppAD support.");
#endif
}

namespace residual_phase_detail {

PhaseStateCompositionSensitivityResult phase_state_ln_fugacity_density_sensitivity_cpp(
    double t,
    double p,
    double rho,
    vector<double> x,
    const add_args &cppargs,
    bool apply_pressure_root_chain
) {
    PhaseStateCompositionSensitivityResult out;
    out.temperature = t;
    out.pressure = p;
    out.composition = x;
    out.rows = static_cast<int>(x.size());
    out.cols = static_cast<int>(x.size());

    if (!std::isfinite(rho) || !(rho > 0.0)) {
        out.message = "Phase-state fugacity sensitivity requires a positive finite explicit density.";
        return out;
    }
    out.density = rho;
    out.ln_fugacity = fugacity_coefficient_result_cpp(t, rho, x, cppargs).lnfugcoef.total;

    using CppADScalar = CppAD::AD<double>;
    const int ncomp = static_cast<int>(x.size());
    const int var_count = ncomp + 1;
    std::vector<CppADScalar> avars(static_cast<size_t>(var_count));
    avars[0] = rho;
    for (int i = 0; i < ncomp; ++i) {
        avars[static_cast<size_t>(1 + i)] = x[static_cast<size_t>(i)];
    }
    CppAD::Independent(avars);

    std::vector<CppADScalar> ax(static_cast<size_t>(ncomp));
    for (int i = 0; i < ncomp; ++i) {
        ax[static_cast<size_t>(i)] = avars[static_cast<size_t>(1 + i)];
    }
    const bool active_association = residual_backend_detail::has_association_sites(cppargs);
    add_args recording_args = cppargs;
    if (active_association) {
        recording_args.assoc_num.clear();
        recording_args.assoc_matrix.clear();
        recording_args.e_assoc.clear();
        recording_args.vol_a.clear();
        recording_args.k_hb.clear();
    }
    auto contributions = ares_detail::ares_contributions_scalar_cpp(t, avars[0], ax, recording_args);
    std::vector<CppADScalar> ay(1);
    ay[0] = contributions.hc + contributions.disp + contributions.assoc + contributions.ion + contributions.born;

    CppAD::ADFun<double> function(avars, ay);
    std::vector<double> point(static_cast<size_t>(var_count), 0.0);
    point[0] = rho;
    for (int i = 0; i < ncomp; ++i) {
        point[static_cast<size_t>(1 + i)] = x[static_cast<size_t>(i)];
    }
    auto values = function.Forward(0, point);
    auto jacobian = function.Jacobian(point);
    auto hessian = function.Hessian(point, 0);
    std::vector<double> third_tensor =
        ares_detail::scalar_function_third_derivative_tensor_cppad(function, point);
    const auto h = [&](int row, int col) {
        return hessian[static_cast<size_t>(row * var_count + col)];
    };
    const auto h3 = [&](int leading, int row, int col) {
        return third_tensor[
            static_cast<size_t>(leading * var_count * var_count + row * var_count + col)
        ];
    };
    ares_detail::AssociationPhaseStateResponse association_response;
    if (active_association) {
        association_response = residual_association_detail::association_phase_state_response_cppad_cpp(t, rho, x, cppargs);
        if (!association_response.active) {
            out.message = "Association phase-state sensitivity expected active association but received no active site fractions.";
            out.density_backend = apply_pressure_root_chain ? "selected_density_root" : "explicit_density";
            return out;
        }
        out.association_sensitivity_backend = association_response.backend;
        out.association_sensitivity_helper = association_response.helper;
        out.association_site_count = association_response.site_count;
        out.association_site_sensitivity_row_major = association_response.site_sensitivity_row_major;
        out.association_site_second_sensitivity_tensor_row_major =
            association_response.site_second_sensitivity_tensor_row_major;
    }

    (void)values;
    const double da_drho = jacobian[0];
    const double association_zraw = active_association ? association_response.zraw : 0.0;
    const double z_raw = rho * da_drho + association_zraw;
    const double z = 1.0 + z_raw;
    if (!(z > 0.0) || !std::isfinite(z)) {
        out.message = "Phase-state sensitivity produced a non-positive compressibility factor.";
        out.density_backend = apply_pressure_root_chain ? "selected_density_root" : "explicit_density";
        return out;
    }
    const double pressure_value = kb * t * N_AV * rho * z;
    if (!apply_pressure_root_chain) {
        out.pressure = pressure_value;
    }

    std::vector<double> dadx(static_cast<size_t>(ncomp), 0.0);
    double sum_x_dadx = 0.0;
    for (int i = 0; i < ncomp; ++i) {
        dadx[static_cast<size_t>(i)] = jacobian[static_cast<size_t>(1 + i)];
        sum_x_dadx += x[static_cast<size_t>(i)] * dadx[static_cast<size_t>(i)];
    }

    const auto base_dzraw_dvar = [&](int var_index) {
        double value = rho * h(0, var_index);
        if (var_index == 0) {
            value += da_drho;
        }
        return value;
    };
    const auto base_d2zraw_dvar2 = [&](int first, int second) {
        double value = rho * h3(0, first, second);
        if (first == 0) {
            value += h(0, second);
        }
        if (second == 0) {
            value += h(0, first);
        }
        return value;
    };
    const auto dzraw_dvar = [&](int var_index) {
        double value = base_dzraw_dvar(var_index);
        if (active_association) {
            value += association_response.dzraw_dvar[static_cast<size_t>(var_index)];
        }
        return value;
    };
    const auto d2zraw_dvar2 = [&](int first, int second) {
        double value = base_d2zraw_dvar2(first, second);
        if (active_association) {
            value += association_response.d2zraw_dvar2_row_major[
                static_cast<size_t>(first * var_count + second)
            ];
        }
        return value;
    };
    const auto pressure_dvar = [&](int var_index) {
        const double dzraw = dzraw_dvar(var_index);
        double value = rho * dzraw;
        if (var_index == 0) {
            value += z;
        }
        return kb * t * N_AV * value;
    };
    const auto pressure_d2var = [&](int first, int second) {
        double value = rho * d2zraw_dvar2(first, second);
        if (first == 0) {
            value += dzraw_dvar(second);
        }
        if (second == 0) {
            value += dzraw_dvar(first);
        }
        return kb * t * N_AV * value;
    };
    const auto sum_x_dadx_dvar = [&](int var_index) {
        double value = 0.0;
        if (var_index > 0) {
            value += dadx[static_cast<size_t>(var_index - 1)];
        }
        for (int k = 0; k < ncomp; ++k) {
            value += x[static_cast<size_t>(k)] * h(1 + k, var_index);
        }
        return value;
    };
    const auto d2sum_x_dadx_dvar2 = [&](int first, int second) {
        double value = 0.0;
        if (first > 0) {
            value += h(first, second);
        }
        if (second > 0) {
            value += h(second, first);
        }
        for (int k = 0; k < ncomp; ++k) {
            value += x[static_cast<size_t>(k)] * h3(1 + k, first, second);
        }
        return value;
    };
    const auto mu_direct_dvar = [&](int component, int var_index) {
        const double da_dvar = jacobian[static_cast<size_t>(var_index)];
        double dmu =
            da_dvar
            + base_dzraw_dvar(var_index)
            + h(1 + component, var_index)
            - sum_x_dadx_dvar(var_index);
        if (active_association) {
            dmu += association_response.dmu_dvar_row_major[
                static_cast<size_t>(component * var_count + var_index)
            ];
        }
        return dmu;
    };
    const auto mu_direct_d2var = [&](int component, int first, int second) {
        double value =
            h(first, second)
            + base_d2zraw_dvar2(first, second)
            + h3(1 + component, first, second)
            - d2sum_x_dadx_dvar2(first, second);
        if (active_association) {
            value += association_response.d2mu_dvar2_tensor_row_major[
                static_cast<size_t>(component * var_count * var_count + first * var_count + second)
            ];
        }
        return value;
    };
    const auto fixed_density_dlnphi_dvar = [&](int component, int var_index) {
        const double dzraw = dzraw_dvar(var_index);
        return mu_direct_dvar(component, var_index) - dzraw / z;
    };
    const auto fixed_density_d2lnphi_dvar2 = [&](int component, int first, int second) {
        const double dz_first = dzraw_dvar(first);
        const double dz_second = dzraw_dvar(second);
        const double d2z = d2zraw_dvar2(first, second);
        return mu_direct_d2var(component, first, second) - d2z / z + dz_first * dz_second / (z * z);
    };

    const double dp_drho = pressure_dvar(0);
    if (!std::isfinite(dp_drho) || std::abs(dp_drho) <= 1.0e-30) {
        out.message = "Phase-state sensitivity produced a singular pressure-density derivative.";
        out.density_backend = apply_pressure_root_chain ? "selected_density_root" : "explicit_density";
        return out;
    }

    out.pressure_density_derivative = dp_drho;
    out.pressure_density_second_derivative = pressure_d2var(0, 0);
    out.density_composition_derivative.assign(static_cast<size_t>(ncomp), 0.0);
    out.density_composition_hessian_row_major.assign(static_cast<size_t>(ncomp * ncomp), 0.0);
    out.pressure_composition_fixed_density_derivative.assign(static_cast<size_t>(ncomp), 0.0);
    out.pressure_density_composition_cross_derivative.assign(static_cast<size_t>(ncomp), 0.0);
    out.pressure_composition_fixed_density_hessian_row_major.assign(
        static_cast<size_t>(ncomp * ncomp),
        0.0
    );
    out.ln_fugacity_density_derivative.assign(static_cast<size_t>(ncomp), 0.0);
    out.ln_fugacity_density_second_derivative.assign(static_cast<size_t>(ncomp), 0.0);
    out.ln_fugacity_density_composition_cross_derivative.assign(static_cast<size_t>(ncomp * ncomp), 0.0);
    out.fixed_density_jacobian_row_major.assign(static_cast<size_t>(ncomp * ncomp), 0.0);
    out.fixed_density_hessian_tensor_row_major.assign(static_cast<size_t>(ncomp * ncomp * ncomp), 0.0);
    out.jacobian_row_major.assign(static_cast<size_t>(ncomp * ncomp), 0.0);
    out.hessian_tensor_row_major.assign(static_cast<size_t>(ncomp * ncomp * ncomp), 0.0);

    for (int j = 0; j < ncomp; ++j) {
        const int var_index = 1 + j;
        const double dp_dx_fixed = pressure_dvar(var_index);
        out.pressure_composition_fixed_density_derivative[static_cast<size_t>(j)] = dp_dx_fixed;
        out.pressure_density_composition_cross_derivative[static_cast<size_t>(j)] = pressure_d2var(0, var_index);
        out.density_composition_derivative[static_cast<size_t>(j)] = -dp_dx_fixed / dp_drho;
    }
    for (int j = 0; j < ncomp; ++j) {
        const int first = 1 + j;
        for (int k = 0; k < ncomp; ++k) {
            const int second = 1 + k;
            const double density_hessian =
                -(
                    pressure_d2var(first, second)
                    + pressure_d2var(0, first) * out.density_composition_derivative[static_cast<size_t>(k)]
                    + pressure_d2var(0, second) * out.density_composition_derivative[static_cast<size_t>(j)]
                    + pressure_d2var(0, 0)
                        * out.density_composition_derivative[static_cast<size_t>(j)]
                        * out.density_composition_derivative[static_cast<size_t>(k)]
                ) / dp_drho;
            out.density_composition_hessian_row_major[static_cast<size_t>(j * ncomp + k)] = density_hessian;
            out.pressure_composition_fixed_density_hessian_row_major[static_cast<size_t>(j * ncomp + k)] =
                pressure_d2var(first, second);
        }
    }
    for (int i = 0; i < ncomp; ++i) {
        const double dln_drho = fixed_density_dlnphi_dvar(i, 0);
        out.ln_fugacity_density_derivative[static_cast<size_t>(i)] = dln_drho;
        out.ln_fugacity_density_second_derivative[static_cast<size_t>(i)] =
            fixed_density_d2lnphi_dvar2(i, 0, 0);
        for (int j = 0; j < ncomp; ++j) {
            const double fixed = fixed_density_dlnphi_dvar(i, 1 + j);
            const double total = fixed + dln_drho * out.density_composition_derivative[static_cast<size_t>(j)];
            const size_t index = static_cast<size_t>(i * ncomp + j);
            out.fixed_density_jacobian_row_major[index] = fixed;
            out.ln_fugacity_density_composition_cross_derivative[index] =
                fixed_density_d2lnphi_dvar2(i, 0, 1 + j);
            out.jacobian_row_major[index] = total;
            for (int k = 0; k < ncomp; ++k) {
                const double fixed_hessian = fixed_density_d2lnphi_dvar2(i, 1 + j, 1 + k);
                out.fixed_density_hessian_tensor_row_major[
                    static_cast<size_t>(i * ncomp * ncomp + j * ncomp + k)
                ] = fixed_hessian;
                out.hessian_tensor_row_major[
                    static_cast<size_t>(i * ncomp * ncomp + j * ncomp + k)
                ] =
                    fixed_hessian
                    + fixed_density_d2lnphi_dvar2(i, 1 + j, 0)
                        * out.density_composition_derivative[static_cast<size_t>(k)]
                    + fixed_density_d2lnphi_dvar2(i, 1 + k, 0)
                        * out.density_composition_derivative[static_cast<size_t>(j)]
                    + fixed_density_d2lnphi_dvar2(i, 0, 0)
                        * out.density_composition_derivative[static_cast<size_t>(j)]
                        * out.density_composition_derivative[static_cast<size_t>(k)]
                    + dln_drho * out.density_composition_hessian_row_major[static_cast<size_t>(j * ncomp + k)];
            }
        }
    }

    out.supported = true;
    if (!apply_pressure_root_chain) {
        out.backend = active_association ? "cppad_explicit_density_implicit_association" : "cppad_explicit_density";
        out.density_backend = "explicit_density";
        out.jacobian_row_major = out.fixed_density_jacobian_row_major;
        out.hessian_tensor_row_major = out.fixed_density_hessian_tensor_row_major;
        out.message = (cppargs.born_model == 2)
            ? "CppAD phase-state fugacity composition sensitivities with explicit density and SSM/DS Born terms are available."
            : "CppAD phase-state fugacity composition sensitivities with explicit density are available.";
        return out;
    }
    out.backend = "cppad_implicit";
    out.density_backend = "implicit_density_root";
    out.message = (cppargs.born_model == 2)
        ? "CppAD phase-state fugacity composition sensitivities with implicit density-root routing and SSM/DS Born terms are available."
        : "CppAD phase-state fugacity composition sensitivities with implicit density-root routing are available.";
    return out;
}

}  // namespace residual_phase_detail

PhaseStateCompositionSensitivityResult phase_state_ln_fugacity_explicit_density_composition_sensitivity_cpp(
    double t,
    double rho,
    vector<double> x,
    const add_args &cppargs
) {
    return residual_phase_detail::phase_state_ln_fugacity_density_sensitivity_cpp(
        t,
        0.0,
        rho,
        std::move(x),
        cppargs,
        false
    );
}

PhaseStateCompositionSensitivityResult phase_state_ln_fugacity_composition_sensitivity_cpp(
    double t,
    double p,
    vector<double> x,
    int phase,
    const add_args &cppargs
) {
    PhaseStateCompositionSensitivityResult out;
    out.temperature = t;
    out.pressure = p;
    out.composition = x;
    out.rows = static_cast<int>(x.size());
    out.cols = static_cast<int>(x.size());

    DensitySolveResult density = density_solve_report_cpp(t, p, x, phase, cppargs);
    if (!density.valid || !(density.rho > 0.0) || !std::isfinite(density.rho)) {
        out.message = density.diagnostics.rejection_reason.empty()
            ? "Density root was not valid for phase-state sensitivity evaluation."
            : density.diagnostics.rejection_reason;
        out.density_backend = "selected_density_root";
        return out;
    }
    return residual_phase_detail::phase_state_ln_fugacity_density_sensitivity_cpp(
        t,
        p,
        density.rho,
        std::move(x),
        cppargs,
        true
    );
}

EosPhasePressureDerivativeResult eos_phase_pressure_derivatives_cpp(
    double t,
    const vector<double> &amounts,
    double volume,
    const add_args &cppargs
) {
    EosPhasePressureDerivativeResult out;
    using CppADScalar = CppAD::AD<double>;
    if (!(std::isfinite(t) && t > 0.0) || !(std::isfinite(volume) && volume > 0.0)) {
        out.message = "EOS phase pressure derivatives require positive finite temperature and volume.";
        return out;
    }
    const int ncomp = static_cast<int>(amounts.size());
    if (ncomp <= 0) {
        out.message = "EOS phase pressure derivatives require at least one species amount.";
        return out;
    }
    double total_amount = 0.0;
    for (double amount : amounts) {
        if (!(std::isfinite(amount) && amount > 0.0)) {
            out.message = "EOS phase pressure derivatives require positive finite species amounts.";
            return out;
        }
        total_amount += amount;
    }
    if (!(std::isfinite(total_amount) && total_amount > 0.0)) {
        out.message = "EOS phase pressure derivatives require a positive finite total amount.";
        return out;
    }

    const double rho = total_amount / volume;
    vector<double> x(static_cast<size_t>(ncomp), 0.0);
    for (int i = 0; i < ncomp; ++i) {
        x[static_cast<size_t>(i)] = amounts[static_cast<size_t>(i)] / total_amount;
    }

    const int var_count = ncomp + 1;
    std::vector<CppADScalar> avars(static_cast<size_t>(var_count));
    avars[0] = rho;
    for (int i = 0; i < ncomp; ++i) {
        avars[static_cast<size_t>(1 + i)] = x[static_cast<size_t>(i)];
    }
    CppAD::Independent(avars);

    std::vector<CppADScalar> ax(static_cast<size_t>(ncomp));
    for (int i = 0; i < ncomp; ++i) {
        ax[static_cast<size_t>(i)] = avars[static_cast<size_t>(1 + i)];
    }
    const bool active_association = residual_backend_detail::has_association_sites(cppargs);
    add_args recording_args = cppargs;
    if (active_association) {
        recording_args.assoc_num.clear();
        recording_args.assoc_matrix.clear();
        recording_args.e_assoc.clear();
        recording_args.vol_a.clear();
        recording_args.k_hb.clear();
    }
    auto contributions = ares_detail::ares_contributions_scalar_cpp(t, avars[0], ax, recording_args);
    std::vector<CppADScalar> ay(1);
    ay[0] = contributions.hc + contributions.disp + contributions.assoc + contributions.ion + contributions.born;

    CppAD::ADFun<double> function(avars, ay);
    std::vector<double> point(static_cast<size_t>(var_count), 0.0);
    point[0] = rho;
    for (int i = 0; i < ncomp; ++i) {
        point[static_cast<size_t>(1 + i)] = x[static_cast<size_t>(i)];
    }
    auto jacobian = function.Jacobian(point);
    auto hessian = function.Hessian(point, 0);
    const auto h = [&](int row, int col) {
        return hessian[static_cast<size_t>(row * var_count + col)];
    };

    ares_detail::AssociationPhaseStateResponse association_response;
    if (active_association) {
        association_response = residual_association_detail::association_phase_state_response_cppad_cpp(t, rho, x, cppargs);
        if (!association_response.active) {
            out.message =
                "Association pressure derivative expected active association but received no active site fractions.";
            return out;
        }
    }

    const double da_drho = jacobian[0];
    const double association_zraw = active_association ? association_response.zraw : 0.0;
    const double z_raw = rho * da_drho + association_zraw;
    const double z = 1.0 + z_raw;
    if (!(std::isfinite(z) && z > 0.0)) {
        out.message = "EOS phase pressure derivatives produced a non-positive compressibility factor.";
        return out;
    }

    const auto base_dzraw_dvar = [&](int var_index) {
        double value = rho * h(0, var_index);
        if (var_index == 0) {
            value += da_drho;
        }
        return value;
    };
    const auto dzraw_dvar = [&](int var_index) {
        double value = base_dzraw_dvar(var_index);
        if (active_association) {
            value += association_response.dzraw_dvar[static_cast<size_t>(var_index)];
        }
        return value;
    };
    const auto pressure_dvar = [&](int var_index) {
        const double dzraw = dzraw_dvar(var_index);
        double value = rho * dzraw;
        if (var_index == 0) {
            value += z;
        }
        return kb * t * N_AV * value;
    };

    const double dp_drho = pressure_dvar(0);
    if (!(std::isfinite(dp_drho) && std::abs(dp_drho) > 1.0e-30)) {
        out.message = "EOS phase pressure derivatives produced a singular pressure-density derivative.";
        return out;
    }

    vector<double> dpdx_fixed(static_cast<size_t>(ncomp), 0.0);
    double sum_x_dpdx = 0.0;
    for (int i = 0; i < ncomp; ++i) {
        dpdx_fixed[static_cast<size_t>(i)] = pressure_dvar(1 + i);
        if (!std::isfinite(dpdx_fixed[static_cast<size_t>(i)])) {
            out.message = "EOS phase pressure composition derivative was not finite.";
            return out;
        }
        sum_x_dpdx += x[static_cast<size_t>(i)] * dpdx_fixed[static_cast<size_t>(i)];
    }

    out.pressure_jacobian_row_major.assign(static_cast<size_t>(ncomp + 1), 0.0);
    for (int species = 0; species < ncomp; ++species) {
        out.pressure_jacobian_row_major[static_cast<size_t>(species)] =
            dp_drho / volume
            + (dpdx_fixed[static_cast<size_t>(species)] - sum_x_dpdx) / total_amount;
    }
    out.pressure_jacobian_row_major[static_cast<size_t>(ncomp)] = -dp_drho * rho / volume;
    for (double value : out.pressure_jacobian_row_major) {
        if (!std::isfinite(value)) {
            out.message = "EOS phase pressure amount-volume derivative was not finite.";
            return out;
        }
    }
    out.supported = true;
    out.backend = active_association ? "cppad_implicit" : "cppad";
    out.message = active_association
        ? "CppAD pressure derivatives with implicit association sensitivities are available."
        : "CppAD pressure derivatives are available.";
    out.pressure_density_derivative = dp_drho;
    return out;
}

EosPhaseAssociationDerivativeCorrectionResult eos_phase_association_derivative_corrections_cpp(
    double t,
    const vector<double> &amounts,
    double volume,
    const add_args &cppargs
) {
    EosPhaseAssociationDerivativeCorrectionResult out;
    out.backend = "cppad_implicit_association";
    if (!residual_backend_detail::has_association_sites(cppargs)) {
        out.message = "No active association sites were present.";
        return out;
    }
    if (!(std::isfinite(t) && t > 0.0) || !(std::isfinite(volume) && volume > 0.0)) {
        out.message = "Association derivative corrections require positive finite temperature and volume.";
        return out;
    }
    const int ncomp = static_cast<int>(amounts.size());
    if (ncomp <= 0) {
        out.message = "Association derivative corrections require at least one species amount.";
        return out;
    }
    double total_amount = 0.0;
    for (double amount : amounts) {
        if (!(std::isfinite(amount) && amount > 0.0)) {
            out.message = "Association derivative corrections require positive finite species amounts.";
            return out;
        }
        total_amount += amount;
    }
    if (!(std::isfinite(total_amount) && total_amount > 0.0)) {
        out.message = "Association derivative corrections require a positive finite total amount.";
        return out;
    }

    const double rho = total_amount / volume;
    vector<double> x(static_cast<size_t>(ncomp), 0.0);
    for (int i = 0; i < ncomp; ++i) {
        x[static_cast<size_t>(i)] = amounts[static_cast<size_t>(i)] / total_amount;
    }

    const int base_var_count = ncomp + 1;  // [rho, x_0, ..., x_n]
    const int phase_var_count = ncomp + 1;  // [n_0, ..., n_n, V]
    const auto association_response = residual_association_detail::association_phase_state_response_cppad_cpp(t, rho, x, cppargs);
    if (!association_response.active) {
        out.message = "Association derivative corrections expected active site fractions.";
        return out;
    }
    if (association_response.base_var_count != base_var_count) {
        out.message = "Association derivative correction variable count did not match the phase model.";
        return out;
    }

    std::vector<double> q_first(static_cast<size_t>(base_var_count * phase_var_count), 0.0);
    std::vector<double> q_second(
        static_cast<size_t>(base_var_count * phase_var_count * phase_var_count),
        0.0
    );
    const auto q1 = [&](int q, int y) -> double& {
        return q_first[static_cast<size_t>(q * phase_var_count + y)];
    };
    const auto q2 = [&](int q, int y0, int y1) -> double& {
        return q_second[
            static_cast<size_t>(q * phase_var_count * phase_var_count + y0 * phase_var_count + y1)
        ];
    };
    const auto q1_value = [&](int q, int y) {
        return q_first[static_cast<size_t>(q * phase_var_count + y)];
    };
    const auto q2_value = [&](int q, int y0, int y1) {
        return q_second[
            static_cast<size_t>(q * phase_var_count * phase_var_count + y0 * phase_var_count + y1)
        ];
    };

    for (int species = 0; species < ncomp; ++species) {
        q1(0, species) = 1.0 / volume;
        q2(0, species, ncomp) = -1.0 / (volume * volume);
        q2(0, ncomp, species) = -1.0 / (volume * volume);
    }
    q1(0, ncomp) = -rho / volume;
    q2(0, ncomp, ncomp) = 2.0 * rho / (volume * volume);

    for (int component = 0; component < ncomp; ++component) {
        const int q_index = 1 + component;
        for (int species = 0; species < ncomp; ++species) {
            const double indicator = component == species ? 1.0 : 0.0;
            q1(q_index, species) = (indicator - x[static_cast<size_t>(component)]) / total_amount;
        }
        for (int first = 0; first < ncomp; ++first) {
            for (int second = 0; second < ncomp; ++second) {
                const double first_indicator = component == first ? 1.0 : 0.0;
                const double second_indicator = component == second ? 1.0 : 0.0;
                q2(q_index, first, second) =
                    (2.0 * x[static_cast<size_t>(component)] - first_indicator - second_indicator)
                    / (total_amount * total_amount);
            }
        }
    }

    const auto z_first = [&](int q) {
        return association_response.dzraw_dvar[static_cast<size_t>(q)];
    };
    const auto z_second = [&](int q0, int q1_index) {
        return association_response.d2zraw_dvar2_row_major[
            static_cast<size_t>(q0 * base_var_count + q1_index)
        ];
    };
    const auto mu_first = [&](int component, int q) {
        return association_response.dmu_dvar_row_major[
            static_cast<size_t>(component * base_var_count + q)
        ];
    };
    const auto pressure_reduced_first = [&](int q) {
        double value = rho * z_first(q);
        if (q == 0) {
            value += association_response.zraw;
        }
        return value;
    };
    const auto pressure_reduced_second = [&](int q0, int q1_index) {
        double value = rho * z_second(q0, q1_index);
        if (q0 == 0) {
            value += z_first(q1_index);
        }
        if (q1_index == 0) {
            value += z_first(q0);
        }
        return value;
    };

    out.variable_count = phase_var_count;
    out.objective_hessian_row_major.assign(static_cast<size_t>(phase_var_count * phase_var_count), 0.0);
    out.pressure_hessian_row_major.assign(static_cast<size_t>(phase_var_count * phase_var_count), 0.0);

    for (int row = 0; row < ncomp; ++row) {
        for (int col = 0; col < phase_var_count; ++col) {
            double value = 0.0;
            for (int q = 0; q < base_var_count; ++q) {
                value += mu_first(row, q) * q1_value(q, col);
            }
            out.objective_hessian_row_major[static_cast<size_t>(row * phase_var_count + col)] = value;
        }
    }
    for (int col = 0; col < phase_var_count; ++col) {
        double value = 0.0;
        for (int q = 0; q < base_var_count; ++q) {
            value -= pressure_reduced_first(q) * q1_value(q, col);
        }
        out.objective_hessian_row_major[static_cast<size_t>(ncomp * phase_var_count + col)] = value;
    }
    for (int row = 0; row < phase_var_count; ++row) {
        for (int col = 0; col < row; ++col) {
            const double symmetric = 0.5 * (
                out.objective_hessian_row_major[static_cast<size_t>(row * phase_var_count + col)]
                + out.objective_hessian_row_major[static_cast<size_t>(col * phase_var_count + row)]
            );
            out.objective_hessian_row_major[static_cast<size_t>(row * phase_var_count + col)] = symmetric;
            out.objective_hessian_row_major[static_cast<size_t>(col * phase_var_count + row)] = symmetric;
        }
    }

    const double rt = kb * N_AV * t;
    for (int first = 0; first < phase_var_count; ++first) {
        for (int second = 0; second < phase_var_count; ++second) {
            double value = 0.0;
            for (int q0 = 0; q0 < base_var_count; ++q0) {
                value += pressure_reduced_first(q0) * q2_value(q0, first, second);
                for (int q1_index = 0; q1_index < base_var_count; ++q1_index) {
                    value += pressure_reduced_second(q0, q1_index)
                        * q1_value(q0, first)
                        * q1_value(q1_index, second);
                }
            }
            out.pressure_hessian_row_major[static_cast<size_t>(first * phase_var_count + second)] =
                rt * value;
        }
    }
    for (int row = 0; row < phase_var_count; ++row) {
        for (int col = 0; col < row; ++col) {
            const double symmetric = 0.5 * (
                out.pressure_hessian_row_major[static_cast<size_t>(row * phase_var_count + col)]
                + out.pressure_hessian_row_major[static_cast<size_t>(col * phase_var_count + row)]
            );
            out.pressure_hessian_row_major[static_cast<size_t>(row * phase_var_count + col)] = symmetric;
            out.pressure_hessian_row_major[static_cast<size_t>(col * phase_var_count + row)] = symmetric;
        }
    }

    for (double value : out.objective_hessian_row_major) {
        if (!std::isfinite(value)) {
            out.message = "Association objective Hessian correction was not finite.";
            return out;
        }
    }
    for (double value : out.pressure_hessian_row_major) {
        if (!std::isfinite(value)) {
            out.message = "Association pressure Hessian correction was not finite.";
            return out;
        }
    }
    out.active = true;
    out.message = "Association implicit objective and pressure Hessian corrections are available.";
    return out;
}
