#include "eos/residual/implicit_association/sensitivities.h"
#include "autodiff/implicit_sensitivity.h"
namespace residual_association_detail {
#ifdef EPCSAFT_HAS_CPPAD
ares_detail::AssociationDensityResponse association_density_response_cppad_cpp(
    double t,
    double rho,
    const vector<double> &x,
    const ProviderParameterAccessV1<double> &cppargs
) {
    using CppADScalar = CppAD::AD<double>;
    const int ncomp = static_cast<int>(x.size());
    MixtureState thermo = mixture_state_cpp(t, rho, x, cppargs, false);
    HardChainState hc_state = hard_chain_state_cpp(thermo, x, cppargs);
    AssociationIntermediateState assoc_state = association_intermediate_state_cpp(thermo, hc_state, t, x, cppargs, false, false);

    ares_detail::AssociationDensityResponse out;
    out.mu.assign(static_cast<size_t>(ncomp), 0.0);
    out.dmu_drho.assign(static_cast<size_t>(ncomp), 0.0);
    if (!assoc_state.active) {
        return out;
    }

    const int num_sites = static_cast<int>(assoc_state.XA.size());
    const int var_count = 1 + num_sites;
    std::vector<CppADScalar> avars(static_cast<size_t>(var_count));
    avars[0] = rho;
    for (int i = 0; i < num_sites; ++i) {
        avars[static_cast<size_t>(1 + i)] = assoc_state.XA[static_cast<size_t>(i)];
    }
    CppAD::Independent(avars);

    std::vector<CppADScalar> ax(static_cast<size_t>(ncomp));
    for (int i = 0; i < ncomp; ++i) {
        ax[static_cast<size_t>(i)] = CppADScalar(x[static_cast<size_t>(i)]);
    }

    ares_detail::MixtureStateScalar<CppADScalar> scalar_thermo = ares_detail::mixture_state_scalar_cpp(
        t,
        avars[0],
        ax,
        cppargs
    );
    ares_detail::HardChainStateScalar<CppADScalar> scalar_hc = ares_detail::hard_chain_state_scalar_cpp(
        scalar_thermo,
        ax,
        cppargs
    );
    std::vector<CppADScalar> site_vars(static_cast<size_t>(num_sites));
    for (int i = 0; i < num_sites; ++i) {
        site_vars[static_cast<size_t>(i)] = avars[static_cast<size_t>(1 + i)];
    }
    auto assoc_terms = ares_detail::association_implicit_terms_scalar_cpp(
        scalar_thermo,
        scalar_hc,
        t,
        ax,
        cppargs,
        site_vars
    );

    std::vector<CppADScalar> ay;
    ay.reserve(static_cast<size_t>(1 + ncomp + num_sites));
    ay.push_back(assoc_terms.zraw);
    for (int i = 0; i < ncomp; ++i) {
        ay.push_back(assoc_terms.mu[static_cast<size_t>(i)]);
    }
    for (int i = 0; i < num_sites; ++i) {
        ay.push_back(assoc_terms.residuals[static_cast<size_t>(i)]);
    }

    CppAD::ADFun<double> function(avars, ay);
    std::vector<double> point(static_cast<size_t>(var_count), 0.0);
    point[0] = rho;
    for (int i = 0; i < num_sites; ++i) {
        point[static_cast<size_t>(1 + i)] = assoc_state.XA[static_cast<size_t>(i)];
    }
    auto values = function.Forward(0, point);
    auto jacobian = function.Jacobian(point);
    const int residual_row0 = 1 + ncomp;
    epcsaft::native::implicit_sensitivity::ImplicitSensitivityProblem problem;
    problem.explicit_variable_count = 1;
    problem.solved_variable_count = num_sites;
    problem.output_count = 1 + ncomp;
    problem.residual_row0 = residual_row0;
    problem.backend = out.backend;
    problem.helper_name = out.helper;
    problem.values = values;
    problem.jacobian_row_major = jacobian;
    const auto sensitivity = epcsaft::native::implicit_sensitivity::solve_implicit_sensitivity(problem, false);

    out.site_count = num_sites;
    out.site_sensitivity_row_major = sensitivity.solved_first_row_major;
    out.zraw = sensitivity.output_values[0];
    out.dzraw_drho = sensitivity.output_first_row_major[0];
    for (int i = 0; i < ncomp; ++i) {
        const int output_row = 1 + i;
        out.mu[static_cast<size_t>(i)] = sensitivity.output_values[static_cast<size_t>(output_row)];
        out.dmu_drho[static_cast<size_t>(i)] =
            sensitivity.output_first_row_major[static_cast<size_t>(output_row)];
    }
    return out;
}

ares_detail::AssociationPhaseStateResponse association_phase_state_response_cppad_cpp(
    double t,
    double rho,
    const vector<double> &x,
    const ProviderParameterAccessV1<double> &cppargs
) {
    using CppADScalar = CppAD::AD<double>;
    const int ncomp = static_cast<int>(x.size());
    const int base_var_count = 1 + ncomp;
    MixtureState thermo = mixture_state_cpp(t, rho, x, cppargs, false);
    HardChainState hc_state = hard_chain_state_cpp(thermo, x, cppargs);
    AssociationIntermediateState assoc_state = association_intermediate_state_cpp(thermo, hc_state, t, x, cppargs, false, false);

    ares_detail::AssociationPhaseStateResponse out;
    out.ncomp = ncomp;
    out.base_var_count = base_var_count;
    out.mu.assign(static_cast<size_t>(ncomp), 0.0);
    out.dzraw_dvar.assign(static_cast<size_t>(base_var_count), 0.0);
    out.dmu_dvar_row_major.assign(static_cast<size_t>(ncomp * base_var_count), 0.0);
    out.d2zraw_dvar2_row_major.assign(static_cast<size_t>(base_var_count * base_var_count), 0.0);
    out.d2mu_dvar2_tensor_row_major.assign(
        static_cast<size_t>(ncomp * base_var_count * base_var_count),
        0.0
    );
    if (!assoc_state.active) {
        return out;
    }
    out.active = true;

    const int num_sites = static_cast<int>(assoc_state.XA.size());
    const int var_count = base_var_count + num_sites;
    std::vector<CppADScalar> avars(static_cast<size_t>(var_count));
    avars[0] = rho;
    for (int i = 0; i < ncomp; ++i) {
        avars[static_cast<size_t>(1 + i)] = x[static_cast<size_t>(i)];
    }
    for (int i = 0; i < num_sites; ++i) {
        avars[static_cast<size_t>(base_var_count + i)] = assoc_state.XA[static_cast<size_t>(i)];
    }
    CppAD::Independent(avars);

    std::vector<CppADScalar> ax(static_cast<size_t>(ncomp));
    for (int i = 0; i < ncomp; ++i) {
        ax[static_cast<size_t>(i)] = avars[static_cast<size_t>(1 + i)];
    }
    ares_detail::MixtureStateScalar<CppADScalar> scalar_thermo = ares_detail::mixture_state_scalar_cpp(
        t,
        avars[0],
        ax,
        cppargs
    );
    ares_detail::HardChainStateScalar<CppADScalar> scalar_hc = ares_detail::hard_chain_state_scalar_cpp(
        scalar_thermo,
        ax,
        cppargs
    );
    std::vector<CppADScalar> site_vars(static_cast<size_t>(num_sites));
    for (int i = 0; i < num_sites; ++i) {
        site_vars[static_cast<size_t>(i)] = avars[static_cast<size_t>(base_var_count + i)];
    }
    auto assoc_terms = ares_detail::association_implicit_terms_scalar_cpp(
        scalar_thermo,
        scalar_hc,
        t,
        ax,
        cppargs,
        site_vars
    );

    std::vector<CppADScalar> ay;
    ay.reserve(static_cast<size_t>(1 + ncomp + num_sites));
    ay.push_back(assoc_terms.zraw);
    for (int i = 0; i < ncomp; ++i) {
        ay.push_back(assoc_terms.mu[static_cast<size_t>(i)]);
    }
    for (int i = 0; i < num_sites; ++i) {
        ay.push_back(assoc_terms.residuals[static_cast<size_t>(i)]);
    }

    CppAD::ADFun<double> function(avars, ay);
    std::vector<double> point(static_cast<size_t>(var_count), 0.0);
    point[0] = rho;
    for (int i = 0; i < ncomp; ++i) {
        point[static_cast<size_t>(1 + i)] = x[static_cast<size_t>(i)];
    }
    for (int i = 0; i < num_sites; ++i) {
        point[static_cast<size_t>(base_var_count + i)] = assoc_state.XA[static_cast<size_t>(i)];
    }
    auto values = function.Forward(0, point);
    auto jacobian = function.Jacobian(point);
    std::vector<std::vector<double>> output_hessians;
    output_hessians.reserve(static_cast<std::size_t>(1 + ncomp + num_sites));
    for (int output = 0; output < 1 + ncomp + num_sites; ++output) {
        output_hessians.push_back(ares_detail::vector_output_component_hessian_cppad(
            function,
            point,
            static_cast<std::size_t>(output)
        ));
    }
    std::vector<double> hessian_tensor;
    hessian_tensor.reserve(static_cast<std::size_t>((1 + ncomp + num_sites) * var_count * var_count));
    for (const auto& output_hessian : output_hessians) {
        hessian_tensor.insert(hessian_tensor.end(), output_hessian.begin(), output_hessian.end());
    }
    const int residual_row0 = 1 + ncomp;
    epcsaft::native::implicit_sensitivity::ImplicitSensitivityProblem problem;
    problem.explicit_variable_count = base_var_count;
    problem.solved_variable_count = num_sites;
    problem.output_count = 1 + ncomp;
    problem.residual_row0 = residual_row0;
    problem.backend = out.backend;
    problem.helper_name = out.helper;
    problem.values = values;
    problem.jacobian_row_major = jacobian;
    problem.hessian_tensor_row_major = hessian_tensor;
    const auto sensitivity = epcsaft::native::implicit_sensitivity::solve_implicit_sensitivity(problem, true);

    out.site_count = num_sites;
    out.site_sensitivity_row_major = sensitivity.solved_first_row_major;
    out.site_second_sensitivity_tensor_row_major = sensitivity.solved_second_tensor_row_major;
    out.zraw = sensitivity.output_values[0];
    out.dzraw_dvar.assign(
        sensitivity.output_first_row_major.begin(),
        sensitivity.output_first_row_major.begin() + base_var_count
    );
    out.d2zraw_dvar2_row_major.assign(
        sensitivity.output_second_tensor_row_major.begin(),
        sensitivity.output_second_tensor_row_major.begin() + base_var_count * base_var_count
    );
    for (int i = 0; i < ncomp; ++i) {
        const int output_row = 1 + i;
        out.mu[static_cast<size_t>(i)] = sensitivity.output_values[static_cast<size_t>(output_row)];
        std::copy_n(
            sensitivity.output_first_row_major.begin() + output_row * base_var_count,
            base_var_count,
            out.dmu_dvar_row_major.begin() + i * base_var_count
        );
        std::copy_n(
            sensitivity.output_second_tensor_row_major.begin() + output_row * base_var_count * base_var_count,
            base_var_count * base_var_count,
            out.d2mu_dvar2_tensor_row_major.begin() + i * base_var_count * base_var_count
        );
    }
    return out;
}

ares_detail::AssociationPhaseStateResponse association_phase_state_temperature_response_cppad_cpp(
    double t,
    double rho,
    const vector<double> &x,
    const ProviderParameterAccessV1<double> &cppargs
) {
    using CppADScalar = CppAD::AD<double>;
    const int ncomp = static_cast<int>(x.size());
    const int base_var_count = 2 + ncomp;  // [T, rho, x_0, ..., x_n]
    MixtureState thermo = mixture_state_cpp(t, rho, x, cppargs, false);
    HardChainState hc_state = hard_chain_state_cpp(thermo, x, cppargs);
    AssociationIntermediateState assoc_state = association_intermediate_state_cpp(thermo, hc_state, t, x, cppargs, false, false);

    ares_detail::AssociationPhaseStateResponse out;
    out.ncomp = ncomp;
    out.base_var_count = base_var_count;
    out.mu.assign(static_cast<size_t>(ncomp), 0.0);
    out.dzraw_dvar.assign(static_cast<size_t>(base_var_count), 0.0);
    out.dmu_dvar_row_major.assign(static_cast<size_t>(ncomp * base_var_count), 0.0);
    out.d2zraw_dvar2_row_major.assign(static_cast<size_t>(base_var_count * base_var_count), 0.0);
    out.d2mu_dvar2_tensor_row_major.assign(
        static_cast<size_t>(ncomp * base_var_count * base_var_count),
        0.0
    );
    if (!assoc_state.active) {
        return out;
    }
    out.active = true;

    const int num_sites = static_cast<int>(assoc_state.XA.size());
    const int var_count = base_var_count + num_sites;
    std::vector<CppADScalar> avars(static_cast<size_t>(var_count));
    avars[0] = t;
    avars[1] = rho;
    for (int i = 0; i < ncomp; ++i) {
        avars[static_cast<size_t>(2 + i)] = x[static_cast<size_t>(i)];
    }
    for (int i = 0; i < num_sites; ++i) {
        avars[static_cast<size_t>(base_var_count + i)] = assoc_state.XA[static_cast<size_t>(i)];
    }
    CppAD::Independent(avars);

    std::vector<CppADScalar> ax(static_cast<size_t>(ncomp));
    for (int i = 0; i < ncomp; ++i) {
        ax[static_cast<size_t>(i)] = avars[static_cast<size_t>(2 + i)];
    }
    ares_detail::MixtureStateScalar<CppADScalar> scalar_thermo = ares_detail::mixture_state_scalar_cpp(
        avars[0],
        avars[1],
        ax,
        cppargs
    );
    ares_detail::HardChainStateScalar<CppADScalar> scalar_hc = ares_detail::hard_chain_state_scalar_cpp(
        scalar_thermo,
        ax,
        cppargs
    );
    std::vector<CppADScalar> site_vars(static_cast<size_t>(num_sites));
    for (int i = 0; i < num_sites; ++i) {
        site_vars[static_cast<size_t>(i)] = avars[static_cast<size_t>(base_var_count + i)];
    }
    auto assoc_terms = ares_detail::association_implicit_terms_scalar_cpp(
        scalar_thermo,
        scalar_hc,
        avars[0],
        ax,
        cppargs,
        site_vars
    );

    std::vector<CppADScalar> ay;
    ay.reserve(static_cast<size_t>(1 + ncomp + num_sites));
    ay.push_back(assoc_terms.zraw);
    for (int i = 0; i < ncomp; ++i) {
        ay.push_back(assoc_terms.mu[static_cast<size_t>(i)]);
    }
    for (int i = 0; i < num_sites; ++i) {
        ay.push_back(assoc_terms.residuals[static_cast<size_t>(i)]);
    }

    CppAD::ADFun<double> function(avars, ay);
    std::vector<double> point(static_cast<size_t>(var_count), 0.0);
    point[0] = t;
    point[1] = rho;
    for (int i = 0; i < ncomp; ++i) {
        point[static_cast<size_t>(2 + i)] = x[static_cast<size_t>(i)];
    }
    for (int i = 0; i < num_sites; ++i) {
        point[static_cast<size_t>(base_var_count + i)] = assoc_state.XA[static_cast<size_t>(i)];
    }
    auto values = function.Forward(0, point);
    auto jacobian = function.Jacobian(point);
    std::vector<std::vector<double>> output_hessians;
    output_hessians.reserve(static_cast<std::size_t>(1 + ncomp + num_sites));
    for (int output = 0; output < 1 + ncomp + num_sites; ++output) {
        output_hessians.push_back(ares_detail::vector_output_component_hessian_cppad(
            function,
            point,
            static_cast<std::size_t>(output)
        ));
    }
    std::vector<double> hessian_tensor;
    hessian_tensor.reserve(static_cast<std::size_t>((1 + ncomp + num_sites) * var_count * var_count));
    for (const auto& output_hessian : output_hessians) {
        hessian_tensor.insert(hessian_tensor.end(), output_hessian.begin(), output_hessian.end());
    }
    const int residual_row0 = 1 + ncomp;
    epcsaft::native::implicit_sensitivity::ImplicitSensitivityProblem problem;
    problem.explicit_variable_count = base_var_count;
    problem.solved_variable_count = num_sites;
    problem.output_count = 1 + ncomp;
    problem.residual_row0 = residual_row0;
    problem.backend = out.backend;
    problem.helper_name = out.helper;
    problem.values = values;
    problem.jacobian_row_major = jacobian;
    problem.hessian_tensor_row_major = hessian_tensor;
    const auto sensitivity = epcsaft::native::implicit_sensitivity::solve_implicit_sensitivity(problem, true);

    out.site_count = num_sites;
    out.site_sensitivity_row_major = sensitivity.solved_first_row_major;
    out.site_second_sensitivity_tensor_row_major = sensitivity.solved_second_tensor_row_major;
    out.zraw = sensitivity.output_values[0];
    out.dzraw_dvar.assign(
        sensitivity.output_first_row_major.begin(),
        sensitivity.output_first_row_major.begin() + base_var_count
    );
    out.d2zraw_dvar2_row_major.assign(
        sensitivity.output_second_tensor_row_major.begin(),
        sensitivity.output_second_tensor_row_major.begin() + base_var_count * base_var_count
    );
    for (int i = 0; i < ncomp; ++i) {
        const int output_row = 1 + i;
        out.mu[static_cast<size_t>(i)] = sensitivity.output_values[static_cast<size_t>(output_row)];
        std::copy_n(
            sensitivity.output_first_row_major.begin() + output_row * base_var_count,
            base_var_count,
            out.dmu_dvar_row_major.begin() + i * base_var_count
        );
        std::copy_n(
            sensitivity.output_second_tensor_row_major.begin() + output_row * base_var_count * base_var_count,
            base_var_count * base_var_count,
            out.d2mu_dvar2_tensor_row_major.begin() + i * base_var_count * base_var_count
        );
    }
    return out;
}
#endif
}  // namespace residual_association_detail
