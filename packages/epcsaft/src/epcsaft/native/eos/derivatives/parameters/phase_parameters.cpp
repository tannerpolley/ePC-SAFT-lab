#include "eos/residual/internal.h"
#include "eos/residual/implicit_association/sensitivities.h"
#include "eos/derivatives/backend_labels.h"
#include <array>
#include <cmath>
#include <string>
#include <vector>

// Provider parameter sensitivities reuse the phase derivative shape, but target
// component and pair parameters instead of equilibrium NLP variables.
NeutralBinaryKijPhaseDerivatives association_parameter_phase_derivatives_cpp(
    double t,
    double rho,
    const vector<double> &x,
    const add_args &cppargs,
    int parameter_index,
    const std::string &parameter_name,
    int component_target_kind,
    int component_target_index
) {
#ifdef EPCSAFT_HAS_CPPAD
    using CppADScalar = CppAD::AD<double>;
    const int ncomp = static_cast<int>(x.size());
    if (ncomp <= 0 || cppargs.m.size() != x.size() || cppargs.s.size() != x.size() || cppargs.e.size() != x.size()) {
        throw ValueError("unsupported: association parameter derivatives require aligned neutral component parameters.");
    }
    if (!cppargs.z.empty()) {
        for (double charge : cppargs.z) {
            if (std::abs(charge) > 1.0e-12) {
                throw ValueError("unsupported: association parameter derivatives do not support ionic components.");
            }
        }
    }
    if (!derivative_backend_detail::has_association_sites(cppargs)) {
        throw ValueError("unsupported: association parameter derivatives require active association sites.");
    }
    if (!(t > 0.0) || !(rho > 0.0)) {
        throw ValueError("Native association parameter derivative evaluation requires positive T and rho.");
    }
    for (double xi : x) {
        if (!(xi > 0.0)) {
            throw ValueError("Native association parameter derivative evaluation requires positive composition values.");
        }
    }

    const bool is_component_target = component_target_kind == ares_detail::kGenericTargetEAssocLocal
        || component_target_kind == ares_detail::kGenericTargetVolALocal;
    const bool is_lij = parameter_name == "l_ij";
    const bool is_khb = parameter_name == "k_hb_ij" || parameter_name == "k_hb";
    if (!is_component_target && !is_lij && !is_khb) {
        throw ValueError("Native association parameter derivative received an unsupported target kind.");
    }

    double theta0 = 0.0;
    if (is_component_target) {
        if (component_target_index < 0 || component_target_index >= ncomp) {
            throw ValueError("Native association component-parameter derivative target index is out of range.");
        }
        if (component_target_kind == ares_detail::kGenericTargetEAssocLocal) {
            if (cppargs.e_assoc.size() != x.size()) {
                throw ValueError("unsupported: e_assoc association derivatives require aligned e_assoc values.");
            }
            theta0 = cppargs.e_assoc[static_cast<size_t>(component_target_index)];
        } else {
            if (cppargs.vol_a.size() != x.size()) {
                throw ValueError("unsupported: vol_a association derivatives require aligned vol_a values.");
            }
            theta0 = cppargs.vol_a[static_cast<size_t>(component_target_index)];
        }
    } else {
        if (parameter_index < 0 || parameter_index >= ncomp * ncomp) {
            throw ValueError("Native association binary-parameter derivative index is out of range.");
        }
        const vector<double> &parameter_matrix = is_lij ? cppargs.l_ij : cppargs.k_hb;
        if (parameter_matrix.size() != static_cast<size_t>(ncomp * ncomp)) {
            throw ValueError("unsupported: native association binary-parameter derivatives require a dense parameter matrix.");
        }
        theta0 = parameter_matrix[static_cast<size_t>(parameter_index)];
    }

    const int rho_index = 0;
    const int theta_index = 1;
    const int x_start = 2;
    const int explicit_count = x_start + ncomp;
    std::vector<CppADScalar> base_vars(static_cast<size_t>(explicit_count));
    base_vars[static_cast<size_t>(rho_index)] = rho;
    base_vars[static_cast<size_t>(theta_index)] = theta0;
    for (int i = 0; i < ncomp; ++i) {
        base_vars[static_cast<size_t>(x_start + i)] = x[static_cast<size_t>(i)];
    }
    CppAD::Independent(base_vars);

    std::vector<CppADScalar> base_x(static_cast<size_t>(ncomp));
    for (int i = 0; i < ncomp; ++i) {
        base_x[static_cast<size_t>(i)] = base_vars[static_cast<size_t>(x_start + i)];
    }
    add_args recording_args = cppargs;
    recording_args.assoc_num.clear();
    recording_args.assoc_matrix.clear();
    recording_args.e_assoc.clear();
    recording_args.vol_a.clear();
    recording_args.k_hb.clear();
    const CppADScalar *no_pair_override = nullptr;
    auto base_contributions = ares_detail::ares_contributions_scalar_cpp(
        t,
        base_vars[static_cast<size_t>(rho_index)],
        base_x,
        recording_args,
        -1,
        no_pair_override,
        is_lij ? parameter_index : -1,
        is_lij ? &base_vars[static_cast<size_t>(theta_index)] : nullptr
    );
    std::vector<CppADScalar> base_outputs(1);
    base_outputs[0] = base_contributions.hc + base_contributions.disp + base_contributions.ion + base_contributions.born;
    CppAD::ADFun<double> base_function(base_vars, base_outputs);
    std::vector<double> explicit_point(static_cast<size_t>(explicit_count), 0.0);
    explicit_point[static_cast<size_t>(rho_index)] = rho;
    explicit_point[static_cast<size_t>(theta_index)] = theta0;
    for (int i = 0; i < ncomp; ++i) {
        explicit_point[static_cast<size_t>(x_start + i)] = x[static_cast<size_t>(i)];
    }
    auto base_values = base_function.Forward(0, explicit_point);
    auto base_jacobian = base_function.Jacobian(explicit_point);
    auto base_hessian = base_function.Hessian(explicit_point, 0);
    const auto base_h = [&](int row, int col) {
        return base_hessian[static_cast<size_t>(row * explicit_count + col)];
    };

    MixtureState thermo = mixture_state_cpp(t, rho, x, cppargs, false);
    HardChainState hc_state = hard_chain_state_cpp(thermo, x, cppargs);
    AssociationIntermediateState assoc_state = association_intermediate_state_cpp(
        thermo,
        hc_state,
        t,
        x,
        cppargs,
        false,
        false
    );
    if (!assoc_state.active || assoc_state.XA.empty()) {
        throw ValueError("Native association parameter derivative expected active association site fractions.");
    }
    const int num_sites = static_cast<int>(assoc_state.XA.size());
    const int var_count = explicit_count + num_sites;
    std::vector<CppADScalar> avars(static_cast<size_t>(var_count));
    for (int i = 0; i < explicit_count; ++i) {
        avars[static_cast<size_t>(i)] = explicit_point[static_cast<size_t>(i)];
    }
    for (int i = 0; i < num_sites; ++i) {
        avars[static_cast<size_t>(explicit_count + i)] = assoc_state.XA[static_cast<size_t>(i)];
    }
    CppAD::Independent(avars);

    std::vector<CppADScalar> ax(static_cast<size_t>(ncomp));
    for (int i = 0; i < ncomp; ++i) {
        ax[static_cast<size_t>(i)] = avars[static_cast<size_t>(x_start + i)];
    }
    ares_detail::MixtureStateScalar<CppADScalar> scalar_thermo = ares_detail::mixture_state_scalar_cpp(
        t,
        avars[static_cast<size_t>(rho_index)],
        ax,
        cppargs,
        -1,
        static_cast<const CppADScalar *>(nullptr),
        is_lij ? parameter_index : -1,
        is_lij ? &avars[static_cast<size_t>(theta_index)] : static_cast<const CppADScalar *>(nullptr)
    );
    ares_detail::HardChainStateScalar<CppADScalar> scalar_hc = ares_detail::hard_chain_state_scalar_cpp(
        scalar_thermo,
        ax,
        cppargs
    );
    std::vector<CppADScalar> site_vars(static_cast<size_t>(num_sites));
    for (int i = 0; i < num_sites; ++i) {
        site_vars[static_cast<size_t>(i)] = avars[static_cast<size_t>(explicit_count + i)];
    }
    auto assoc_terms = ares_detail::association_implicit_terms_scalar_cpp(
        scalar_thermo,
        scalar_hc,
        t,
        ax,
        cppargs,
        site_vars,
        component_target_kind,
        component_target_index,
        is_component_target ? &avars[static_cast<size_t>(theta_index)] : nullptr,
        is_khb ? parameter_index : -1,
        is_khb ? &avars[static_cast<size_t>(theta_index)] : nullptr
    );

    std::vector<CppADScalar> ay;
    ay.reserve(static_cast<size_t>(2 + ncomp + num_sites));
    ay.push_back(assoc_terms.ares);
    ay.push_back(assoc_terms.zraw);
    for (int i = 0; i < ncomp; ++i) {
        ay.push_back(assoc_terms.mu[static_cast<size_t>(i)]);
    }
    for (int i = 0; i < num_sites; ++i) {
        ay.push_back(assoc_terms.residuals[static_cast<size_t>(i)]);
    }

    CppAD::ADFun<double> function(avars, ay);
    std::vector<double> point(static_cast<size_t>(var_count), 0.0);
    for (int i = 0; i < explicit_count; ++i) {
        point[static_cast<size_t>(i)] = explicit_point[static_cast<size_t>(i)];
    }
    for (int i = 0; i < num_sites; ++i) {
        point[static_cast<size_t>(explicit_count + i)] = assoc_state.XA[static_cast<size_t>(i)];
    }
    auto values = function.Forward(0, point);
    auto jacobian = function.Jacobian(point);

    const int residual_row0 = 2 + ncomp;
    epcsaft::native::implicit_sensitivity::ImplicitSensitivityProblem problem;
    problem.explicit_variable_count = explicit_count;
    problem.solved_variable_count = num_sites;
    problem.output_count = 2 + ncomp;
    problem.residual_row0 = residual_row0;
    problem.backend = "cppad_implicit_association";
    problem.helper_name = "association_implicit_sensitivity";
    problem.values = values;
    problem.jacobian_row_major = jacobian;
    const auto sensitivity = epcsaft::native::implicit_sensitivity::solve_implicit_sensitivity(problem, false);

    const double base_ares = base_values[0];
    const double base_da_drho = base_jacobian[static_cast<size_t>(rho_index)];
    const double base_da_dtheta = base_jacobian[static_cast<size_t>(theta_index)];
    const double base_d2a_drho2 = base_h(rho_index, rho_index);
    const double base_d2a_drho_dtheta = base_h(rho_index, theta_index);
    const double base_zraw = rho * base_da_drho;
    const double base_dzraw_drho = base_da_drho + rho * base_d2a_drho2;
    const double base_dzraw_dtheta = rho * base_d2a_drho_dtheta;
    const double assoc_ares = sensitivity.output_values[0];
    const double assoc_zraw = sensitivity.output_values[1];
    const double assoc_dares_drho = sensitivity.output_first_row_major[static_cast<size_t>(0 * explicit_count + rho_index)];
    const double assoc_dares_dtheta = sensitivity.output_first_row_major[static_cast<size_t>(0 * explicit_count + theta_index)];
    (void)assoc_dares_drho;
    const double assoc_dzraw_drho = sensitivity.output_first_row_major[static_cast<size_t>(1 * explicit_count + rho_index)];
    const double assoc_dzraw_dtheta = sensitivity.output_first_row_major[static_cast<size_t>(1 * explicit_count + theta_index)];
    const double z_raw = base_zraw + assoc_zraw;
    const double z = 1.0 + z_raw;
    if (!(z > 0.0)) {
        throw ValueError("Native association parameter derivative evaluation produced non-positive Z.");
    }
    const double dz_drho = base_dzraw_drho + assoc_dzraw_drho;
    const double dz_dtheta = base_dzraw_dtheta + assoc_dzraw_dtheta;
    const double pressure_factor = kb * t * N_AV;
    NeutralBinaryKijPhaseDerivatives out;
    out.ares = base_ares + assoc_ares;
    out.dares_dk_fixed_rho = base_da_dtheta + assoc_dares_dtheta;
    out.rho = rho;
    out.z = z;
    out.pressure = rho * pressure_factor * z;
    out.dpdrho = pressure_factor * (z + rho * dz_drho);
    out.dpdk = rho * pressure_factor * dz_dtheta;
    if (!(std::isfinite(out.dpdrho)) || std::abs(out.dpdrho) <= 0.0) {
        throw ValueError("Native association parameter derivative evaluation produced invalid dP/drho.");
    }
    out.drhodk = -out.dpdk / out.dpdrho;
    out.mu_res.assign(static_cast<size_t>(ncomp), 0.0);
    out.dmu_res_dk_fixed_rho.assign(static_cast<size_t>(ncomp), 0.0);
    out.lnphi.assign(static_cast<size_t>(ncomp), 0.0);
    out.dlnphi_drho.assign(static_cast<size_t>(ncomp), 0.0);
    out.dlnphi_dk_fixed_rho.assign(static_cast<size_t>(ncomp), 0.0);
    out.dlnphi_dk_total.assign(static_cast<size_t>(ncomp), 0.0);

    vector<double> base_dadx(static_cast<size_t>(ncomp), 0.0);
    vector<double> base_dadx_drho(static_cast<size_t>(ncomp), 0.0);
    vector<double> base_dadx_dtheta(static_cast<size_t>(ncomp), 0.0);
    double base_sum_x_dadx = 0.0;
    double base_sum_x_dadx_drho = 0.0;
    double base_sum_x_dadx_dtheta = 0.0;
    for (int i = 0; i < ncomp; ++i) {
        const int xi = x_start + i;
        base_dadx[static_cast<size_t>(i)] = base_jacobian[static_cast<size_t>(xi)];
        base_dadx_drho[static_cast<size_t>(i)] = base_h(xi, rho_index);
        base_dadx_dtheta[static_cast<size_t>(i)] = base_h(xi, theta_index);
        base_sum_x_dadx += x[static_cast<size_t>(i)] * base_dadx[static_cast<size_t>(i)];
        base_sum_x_dadx_drho += x[static_cast<size_t>(i)] * base_dadx_drho[static_cast<size_t>(i)];
        base_sum_x_dadx_dtheta += x[static_cast<size_t>(i)] * base_dadx_dtheta[static_cast<size_t>(i)];
    }
    for (int i = 0; i < ncomp; ++i) {
        const double base_mu = base_ares + base_zraw + base_dadx[static_cast<size_t>(i)] - base_sum_x_dadx;
        const double base_dmu_drho =
            base_da_drho + base_dzraw_drho + base_dadx_drho[static_cast<size_t>(i)] - base_sum_x_dadx_drho;
        const double base_dmu_dtheta =
            base_da_dtheta + base_dzraw_dtheta + base_dadx_dtheta[static_cast<size_t>(i)]
            - base_sum_x_dadx_dtheta;
        const int output_row = 2 + i;
        const double assoc_mu = sensitivity.output_values[static_cast<size_t>(output_row)];
        const double assoc_dmu_drho =
            sensitivity.output_first_row_major[static_cast<size_t>(output_row * explicit_count + rho_index)];
        const double assoc_dmu_dtheta =
            sensitivity.output_first_row_major[static_cast<size_t>(output_row * explicit_count + theta_index)];
        const double mu = base_mu + assoc_mu;
        const double dmu_drho = base_dmu_drho + assoc_dmu_drho;
        const double dmu_dtheta = base_dmu_dtheta + assoc_dmu_dtheta;
        out.mu_res[static_cast<size_t>(i)] = mu;
        out.dmu_res_dk_fixed_rho[static_cast<size_t>(i)] = dmu_dtheta;
        out.lnphi[static_cast<size_t>(i)] = mu - std::log(z);
        out.dlnphi_drho[static_cast<size_t>(i)] = dmu_drho - dz_drho / z;
        out.dlnphi_dk_fixed_rho[static_cast<size_t>(i)] = dmu_dtheta - dz_dtheta / z;
        out.dlnphi_dk_total[static_cast<size_t>(i)] =
            out.dlnphi_dk_fixed_rho[static_cast<size_t>(i)] + out.dlnphi_drho[static_cast<size_t>(i)] * out.drhodk;
    }
    out.backend = "cppad_implicit";
    out.association_sensitivity_backend = "cppad_implicit_association";
    out.association_sensitivity_helper = "association_implicit_sensitivity";
    out.association_site_count = num_sites;
    out.association_site_sensitivity_row_major = sensitivity.solved_first_row_major;
    return out;
#else
    (void)t;
    (void)rho;
    (void)x;
    (void)cppargs;
    (void)parameter_index;
    (void)parameter_name;
    (void)component_target_kind;
    (void)component_target_index;
    throw ValueError("unsupported: CppAD support is not enabled in this native build.");
#endif
}

NeutralBinaryKijPhaseDerivatives neutral_binary_kij_phase_derivatives_cpp(
    double t,
    double rho,
    const vector<double> &x,
    const add_args &cppargs,
    int k_index
) {
    return neutral_binary_pair_parameter_phase_derivatives_cpp(t, rho, x, cppargs, k_index, "k_ij");
}

NeutralBinaryKijPhaseDerivatives neutral_binary_pair_parameter_phase_derivatives_cpp(
    double t,
    double rho,
    const vector<double> &x,
    const add_args &cppargs,
    int parameter_index,
    const std::string &parameter_name
) {
#ifdef EPCSAFT_HAS_CPPAD
    using CppADScalar = CppAD::AD<double>;
    const int ncomp = static_cast<int>(x.size());
    if (ncomp != 2 || cppargs.m.size() != 2 || cppargs.s.size() != 2 || cppargs.e.size() != 2) {
        throw ValueError("unsupported: native binary pair-parameter CppAD derivatives require exactly two neutral components.");
    }
    if (!cppargs.z.empty()) {
        for (double charge : cppargs.z) {
            if (std::abs(charge) > 1.0e-12) {
                throw ValueError("unsupported: native binary pair-parameter CppAD derivatives do not support ionic components.");
            }
        }
    }
    const bool is_kij = parameter_name == "k_ij";
    const bool is_lij = parameter_name == "l_ij";
    const bool is_khb = parameter_name == "k_hb_ij" || parameter_name == "k_hb";
    if (!is_kij && !is_lij && !is_khb) {
        throw ValueError("Native binary pair-parameter derivative supports only k_ij, l_ij, and k_hb_ij.");
    }
    const bool active_association = derivative_backend_detail::has_association_sites(cppargs);
    if (active_association && (is_lij || is_khb)) {
        return association_parameter_phase_derivatives_cpp(
            t,
            rho,
            x,
            cppargs,
            parameter_index,
            parameter_name,
            -1,
            -1
        );
    }
    if (active_association && !is_kij) {
        throw ValueError("unsupported: associating binary pair-parameter derivatives support k_ij only until association-size sensitivities are implemented.");
    }
    const vector<double> &parameter_matrix = is_kij ? cppargs.k_ij : cppargs.l_ij;
    if (parameter_matrix.size() != static_cast<size_t>(ncomp * ncomp)) {
        throw ValueError("unsupported: native binary pair-parameter CppAD derivatives require a dense parameter matrix.");
    }
    if (parameter_index < 0 || static_cast<size_t>(parameter_index) >= parameter_matrix.size()) {
        throw ValueError("Native binary pair-parameter derivative index is out of range.");
    }
    if (!(t > 0.0) || !(rho > 0.0) || x.size() != 2 || !(x[0] > 0.0) || !(x[1] > 0.0)) {
        throw ValueError("Native binary k_ij derivative evaluation requires positive T, rho, and composition values.");
    }

    constexpr int kRhoIndex = 0;
    constexpr int kKijIndex = 1;
    constexpr int kX0Index = 2;
    constexpr int kX1Index = 3;
    constexpr int kVarCount = 4;
    std::vector<CppADScalar> avars(kVarCount);
    avars[kRhoIndex] = rho;
    avars[kKijIndex] = parameter_matrix[static_cast<size_t>(parameter_index)];
    avars[kX0Index] = x[0];
    avars[kX1Index] = x[1];
    CppAD::Independent(avars);

    add_args recording_args = cppargs;
    if (active_association && is_kij) {
        recording_args.assoc_num.clear();
        recording_args.assoc_matrix.clear();
        recording_args.e_assoc.clear();
        recording_args.vol_a.clear();
        recording_args.k_hb.clear();
    }

    std::vector<CppADScalar> ax = {avars[kX0Index], avars[kX1Index]};
    auto contributions = ares_detail::ares_contributions_scalar_cpp(
        t,
        avars[kRhoIndex],
        ax,
        recording_args,
        is_kij ? parameter_index : -1,
        is_kij ? &avars[kKijIndex] : nullptr,
        is_lij ? parameter_index : -1,
        is_lij ? &avars[kKijIndex] : nullptr
    );
    std::vector<CppADScalar> ay(1);
    ay[0] = contributions.hc + contributions.disp + contributions.assoc + contributions.ion + contributions.born;

    CppAD::ADFun<double> function(avars, ay);
    std::vector<double> point = {rho, parameter_matrix[static_cast<size_t>(parameter_index)], x[0], x[1]};
    auto values = function.Forward(0, point);
    auto jacobian = function.Jacobian(point);
    auto hessian = function.Hessian(point, 0);

    const double ares = values[0];
    const double da_drho = jacobian[kRhoIndex];
    const double da_dk = jacobian[kKijIndex];
    const double da_dx0 = jacobian[kX0Index];
    const double da_dx1 = jacobian[kX1Index];
    const auto h = [&](int row, int col) {
        return hessian[static_cast<size_t>(row * kVarCount + col)];
    };
    const double d2a_drho2 = h(kRhoIndex, kRhoIndex);
    const double d2a_drho_dk = h(kRhoIndex, kKijIndex);
    const double d2a_dx0_drho = h(kX0Index, kRhoIndex);
    const double d2a_dx1_drho = h(kX1Index, kRhoIndex);
    const double d2a_dx0_dk = h(kX0Index, kKijIndex);
    const double d2a_dx1_dk = h(kX1Index, kKijIndex);

    const double z_raw = rho * da_drho;
    const double z = 1.0 + z_raw;
    if (!(z > 0.0)) {
        throw ValueError("Native binary k_ij derivative evaluation produced non-positive Z.");
    }
    const double dz_drho = da_drho + rho * d2a_drho2;
    const double dz_dk = rho * d2a_drho_dk;
    const double pressure_factor = kb * t * N_AV;
    double z_for_values = z;
    vector<double> mu_for_values;
    vector<double> lnfug_for_values;
    double dpdrho_for_values = pressure_factor * (z + rho * dz_drho);
    double assoc_dzraw_drho_for_values = 0.0;
    vector<double> assoc_dmu_drho_for_values;
    if (active_association && is_kij) {
        ResidualChemicalPotentialResult native_mu =
            residual_chemical_potential_result_cpp(t, rho, vector<double>(x.begin(), x.end()), cppargs);
        FugacityContributionResult native_fugacity =
            fugacity_coefficient_result_cpp(t, rho, vector<double>(x.begin(), x.end()), cppargs);
        ares_detail::AssociationDensityResponse assoc_density =
            residual_association_detail::association_density_response_cppad_cpp(t, rho, vector<double>(x.begin(), x.end()), cppargs);
        z_for_values = native_mu.composition.z.total;
        mu_for_values = native_mu.mu.total;
        lnfug_for_values = native_fugacity.lnfugcoef.total;
        assoc_dzraw_drho_for_values = assoc_density.dzraw_drho;
        assoc_dmu_drho_for_values = std::move(assoc_density.dmu_drho);
        dpdrho_for_values = pressure_factor * (z_for_values + rho * (dz_drho + assoc_dzraw_drho_for_values));
    }
    NeutralBinaryKijPhaseDerivatives out;
    out.ares = ares;
    out.dares_dk_fixed_rho = da_dk;
    out.rho = rho;
    out.z = z_for_values;
    out.pressure = rho * pressure_factor * z_for_values;
    out.dpdrho = dpdrho_for_values;
    out.dpdk = rho * pressure_factor * dz_dk;
    if (!(std::isfinite(out.dpdrho)) || std::abs(out.dpdrho) <= 0.0) {
        throw ValueError("Native binary k_ij derivative evaluation produced invalid dP/drho.");
    }
    out.drhodk = -out.dpdk / out.dpdrho;
    out.mu_res.assign(2, 0.0);
    out.dmu_res_dk_fixed_rho.assign(2, 0.0);
    out.lnphi.assign(2, 0.0);
    out.dlnphi_drho.assign(2, 0.0);
    out.dlnphi_dk_fixed_rho.assign(2, 0.0);
    out.dlnphi_dk_total.assign(2, 0.0);

    const std::array<double, 2> dadx = {da_dx0, da_dx1};
    const std::array<double, 2> dadx_drho = {d2a_dx0_drho, d2a_dx1_drho};
    const std::array<double, 2> dadx_dk = {d2a_dx0_dk, d2a_dx1_dk};
    const double sum_x_dadx = x[0] * dadx[0] + x[1] * dadx[1];
    const double sum_x_dadx_drho = x[0] * dadx_drho[0] + x[1] * dadx_drho[1];
    const double sum_x_dadx_dk = x[0] * dadx_dk[0] + x[1] * dadx_dk[1];
    for (int i = 0; i < 2; ++i) {
        const double mu = ares + z_raw + dadx[static_cast<size_t>(i)] - sum_x_dadx;
        const double dmu_drho = da_drho + dz_drho + dadx_drho[static_cast<size_t>(i)] - sum_x_dadx_drho;
        const double dmu_dk = da_dk + dz_dk + dadx_dk[static_cast<size_t>(i)] - sum_x_dadx_dk;
        out.mu_res[static_cast<size_t>(i)] =
            mu_for_values.empty() ? mu : mu_for_values[static_cast<size_t>(i)];
        out.dmu_res_dk_fixed_rho[static_cast<size_t>(i)] = dmu_dk;
        out.lnphi[static_cast<size_t>(i)] =
            lnfug_for_values.empty() ? mu - std::log(z) : lnfug_for_values[static_cast<size_t>(i)];
        out.dlnphi_drho[static_cast<size_t>(i)] = assoc_dmu_drho_for_values.empty()
            ? dmu_drho - dz_drho / z_for_values
            : dmu_drho + assoc_dmu_drho_for_values[static_cast<size_t>(i)]
                - (dz_drho + assoc_dzraw_drho_for_values) / z_for_values;
        out.dlnphi_dk_fixed_rho[static_cast<size_t>(i)] = dmu_dk - dz_dk / z_for_values;
        out.dlnphi_dk_total[static_cast<size_t>(i)] =
            out.dlnphi_dk_fixed_rho[static_cast<size_t>(i)] + out.dlnphi_drho[static_cast<size_t>(i)] * out.drhodk;
    }
    out.backend = active_association ? "cppad_implicit" : "cppad";
    if (active_association) {
        out.association_sensitivity_backend = "cppad_implicit_association";
        out.association_sensitivity_helper = "association_implicit_sensitivity";
    }
    return out;
#else
    (void)t;
    (void)rho;
    (void)x;
    (void)cppargs;
    (void)parameter_index;
    (void)parameter_name;
    throw ValueError("unsupported: CppAD support is not enabled in this native build.");
#endif
}

NeutralBinaryKijPhaseDerivatives generic_component_parameter_phase_derivatives_cpp(
    double t,
    double rho,
    const vector<double> &x,
    const add_args &cppargs,
    int target_kind,
    int target_index
) {
#ifdef EPCSAFT_HAS_CPPAD
    using CppADScalar = CppAD::AD<double>;
    const int ncomp = static_cast<int>(x.size());
    if (ncomp <= 0 || cppargs.s.size() != x.size() || cppargs.e.size() != x.size()) {
        throw ValueError("unsupported: generic component-parameter CppAD derivatives require aligned component parameters.");
    }
    if (target_kind != ares_detail::kGenericTargetSLocal
        && target_kind != ares_detail::kGenericTargetELocal
        && target_kind != ares_detail::kGenericTargetEAssocLocal
        && target_kind != ares_detail::kGenericTargetVolALocal
        && target_kind != ares_detail::kGenericTargetDBornLocal
        && target_kind != ares_detail::kGenericTargetFSolvLocal
        && target_kind != ares_detail::kGenericTargetDielcLocal) {
        throw ValueError("unsupported: generic component-parameter CppAD derivatives support s, e, e_assoc, vol_a, d_born, f_solv, and dielc only.");
    }
    if (target_index < 0 || target_index >= ncomp) {
        throw ValueError("Native generic component-parameter derivative target index is out of range.");
    }
    if (target_kind == ares_detail::kGenericTargetDBornLocal) {
        if (cppargs.d_born.size() != x.size()) {
            throw ValueError("unsupported: d_born CppAD derivatives require aligned d_born values.");
        }
        if (cppargs.born_model != 1 && cppargs.born_model != 2) {
            throw ValueError("unsupported: d_born CppAD derivatives require a direct or SSM/DS Born model.");
        }
    }
    if (target_kind == ares_detail::kGenericTargetFSolvLocal) {
        if (cppargs.f_solv.size() != x.size()) {
            throw ValueError("unsupported: f_solv CppAD derivatives require aligned f_solv values.");
        }
        if (cppargs.born_model != 2) {
            throw ValueError("unsupported: f_solv CppAD derivatives require the SSM/DS Born model.");
        }
    }
    if (target_kind == ares_detail::kGenericTargetDielcLocal) {
        if (cppargs.dielc.size() != x.size()) {
            throw ValueError("unsupported: dielc CppAD derivatives require aligned relative-permittivity values.");
        }
        if (cppargs.dielc_rule != 1) {
            throw ValueError("unsupported: dielc CppAD derivatives require linear mole-fraction relative-permittivity mixing.");
        }
    }
    if (target_kind == ares_detail::kGenericTargetEAssocLocal
        || target_kind == ares_detail::kGenericTargetVolALocal) {
        if (!derivative_backend_detail::has_association_sites(cppargs)) {
            throw ValueError("unsupported: association component-parameter derivatives require active association.");
        }
        return association_parameter_phase_derivatives_cpp(
            t,
            rho,
            x,
            cppargs,
            -1,
            "",
            target_kind,
            target_index
        );
    }
    if (!(t > 0.0) || !(rho > 0.0)) {
        throw ValueError("Native generic component-parameter derivative evaluation requires positive T and rho.");
    }
    for (double xi : x) {
        if (!(xi >= 0.0)) {
            throw ValueError("Native generic component-parameter derivative evaluation requires nonnegative composition.");
        }
    }

    const int rho_index = 0;
    const int theta_index = 1;
    const int x_start = 2;
    const int var_count = x_start + ncomp;
    std::vector<CppADScalar> avars(static_cast<size_t>(var_count));
    avars[static_cast<size_t>(rho_index)] = rho;
    double theta0 = 0.0;
    if (target_kind == ares_detail::kGenericTargetSLocal) {
        theta0 = cppargs.s[static_cast<size_t>(target_index)];
    } else if (target_kind == ares_detail::kGenericTargetELocal) {
        theta0 = cppargs.e[static_cast<size_t>(target_index)];
    } else if (target_kind == ares_detail::kGenericTargetDBornLocal) {
        theta0 = cppargs.d_born[static_cast<size_t>(target_index)];
    } else if (target_kind == ares_detail::kGenericTargetFSolvLocal) {
        theta0 = cppargs.f_solv[static_cast<size_t>(target_index)];
    } else {
        theta0 = cppargs.dielc[static_cast<size_t>(target_index)];
    }
    avars[static_cast<size_t>(theta_index)] = theta0;
    for (int i = 0; i < ncomp; ++i) {
        avars[static_cast<size_t>(x_start + i)] = x[static_cast<size_t>(i)];
    }
    CppAD::Independent(avars);

    std::vector<CppADScalar> ax(static_cast<size_t>(ncomp));
    for (int i = 0; i < ncomp; ++i) {
        ax[static_cast<size_t>(i)] = avars[static_cast<size_t>(x_start + i)];
    }
    const bool active_association = derivative_backend_detail::has_association_sites(cppargs);
    add_args recording_args = cppargs;
    if (active_association) {
        recording_args.assoc_num.clear();
        recording_args.assoc_matrix.clear();
        recording_args.e_assoc.clear();
        recording_args.vol_a.clear();
        recording_args.k_hb.clear();
    }
    const CppADScalar *no_pair_override = nullptr;
    auto contributions = ares_detail::ares_contributions_scalar_cpp(
        t,
        avars[static_cast<size_t>(rho_index)],
        ax,
        recording_args,
        -1,
        no_pair_override,
        -1,
        no_pair_override,
        target_kind,
        target_index,
        &avars[static_cast<size_t>(theta_index)]
    );
    std::vector<CppADScalar> ay(1);
    ay[0] = contributions.hc + contributions.disp + contributions.assoc + contributions.ion + contributions.born;

    CppAD::ADFun<double> function(avars, ay);
    std::vector<double> point(static_cast<size_t>(var_count), 0.0);
    point[static_cast<size_t>(rho_index)] = rho;
    point[static_cast<size_t>(theta_index)] = theta0;
    for (int i = 0; i < ncomp; ++i) {
        point[static_cast<size_t>(x_start + i)] = x[static_cast<size_t>(i)];
    }
    auto values = function.Forward(0, point);
    auto jacobian = function.Jacobian(point);
    auto hessian = function.Hessian(point, 0);
    const auto h = [&](int row, int col) {
        return hessian[static_cast<size_t>(row * var_count + col)];
    };

    ares_detail::AssociationDensityResponse association_response;
    if (active_association) {
        association_response = residual_association_detail::association_density_response_cppad_cpp(t, rho, x, cppargs);
        if (association_response.site_count <= 0) {
            throw ValueError("Native generic component-parameter derivative expected active association site fractions.");
        }
    }

    const double base_ares = values[0];
    const double da_drho = jacobian[static_cast<size_t>(rho_index)];
    const double da_dtheta = jacobian[static_cast<size_t>(theta_index)];
    const double d2a_drho2 = h(rho_index, rho_index);
    const double d2a_drho_dtheta = h(rho_index, theta_index);
    const double base_z_raw = rho * da_drho;
    const double association_zraw = active_association ? association_response.zraw : 0.0;
    const double z_raw = base_z_raw + association_zraw;
    const double z = 1.0 + z_raw;
    if (!(z > 0.0)) {
        throw ValueError("Native generic component-parameter derivative evaluation produced non-positive Z.");
    }
    const double base_dz_drho = da_drho + rho * d2a_drho2;
    const double dz_drho = base_dz_drho + (active_association ? association_response.dzraw_drho : 0.0);
    const double dz_dtheta = rho * d2a_drho_dtheta;
    const double pressure_factor = kb * t * N_AV;
    NeutralBinaryKijPhaseDerivatives out;
    const AresContributions total_terms = ares_contributions_cpp(t, rho, x, cppargs);
    out.ares = total_terms.hc + total_terms.disp + total_terms.assoc + total_terms.ion + total_terms.born;
    out.dares_dk_fixed_rho = da_dtheta;
    out.rho = rho;
    out.z = z;
    out.pressure = rho * pressure_factor * z;
    out.dpdrho = pressure_factor * (z + rho * dz_drho);
    out.dpdk = rho * pressure_factor * dz_dtheta;
    if (!(std::isfinite(out.dpdrho)) || std::abs(out.dpdrho) <= 0.0) {
        throw ValueError("Native generic component-parameter derivative evaluation produced invalid dP/drho.");
    }
    out.drhodk = -out.dpdk / out.dpdrho;
    out.mu_res.assign(static_cast<size_t>(ncomp), 0.0);
    out.dmu_res_dk_fixed_rho.assign(static_cast<size_t>(ncomp), 0.0);
    out.lnphi.assign(static_cast<size_t>(ncomp), 0.0);
    out.dlnphi_drho.assign(static_cast<size_t>(ncomp), 0.0);
    out.dlnphi_dk_fixed_rho.assign(static_cast<size_t>(ncomp), 0.0);
    out.dlnphi_dk_total.assign(static_cast<size_t>(ncomp), 0.0);

    vector<double> dadx(static_cast<size_t>(ncomp), 0.0);
    vector<double> dadx_drho(static_cast<size_t>(ncomp), 0.0);
    vector<double> dadx_dtheta(static_cast<size_t>(ncomp), 0.0);
    double sum_x_dadx = 0.0;
    double sum_x_dadx_drho = 0.0;
    double sum_x_dadx_dtheta = 0.0;
    for (int i = 0; i < ncomp; ++i) {
        const int xi = x_start + i;
        dadx[static_cast<size_t>(i)] = jacobian[static_cast<size_t>(xi)];
        dadx_drho[static_cast<size_t>(i)] = h(xi, rho_index);
        dadx_dtheta[static_cast<size_t>(i)] = h(xi, theta_index);
        sum_x_dadx += x[static_cast<size_t>(i)] * dadx[static_cast<size_t>(i)];
        sum_x_dadx_drho += x[static_cast<size_t>(i)] * dadx_drho[static_cast<size_t>(i)];
        sum_x_dadx_dtheta += x[static_cast<size_t>(i)] * dadx_dtheta[static_cast<size_t>(i)];
    }
    for (int i = 0; i < ncomp; ++i) {
        const double base_mu = base_ares + base_z_raw + dadx[static_cast<size_t>(i)] - sum_x_dadx;
        const double mu = base_mu + (active_association ? association_response.mu[static_cast<size_t>(i)] : 0.0);
        const double base_dmu_drho =
            da_drho + base_dz_drho + dadx_drho[static_cast<size_t>(i)] - sum_x_dadx_drho;
        const double dmu_drho =
            base_dmu_drho
            + (active_association ? association_response.dmu_drho[static_cast<size_t>(i)] : 0.0);
        const double dmu_dtheta = da_dtheta + dz_dtheta + dadx_dtheta[static_cast<size_t>(i)] - sum_x_dadx_dtheta;
        out.mu_res[static_cast<size_t>(i)] = mu;
        out.dmu_res_dk_fixed_rho[static_cast<size_t>(i)] = dmu_dtheta;
        out.lnphi[static_cast<size_t>(i)] = mu - std::log(z);
        out.dlnphi_drho[static_cast<size_t>(i)] = dmu_drho - dz_drho / z;
        out.dlnphi_dk_fixed_rho[static_cast<size_t>(i)] = dmu_dtheta - dz_dtheta / z;
        out.dlnphi_dk_total[static_cast<size_t>(i)] =
            out.dlnphi_dk_fixed_rho[static_cast<size_t>(i)] + out.dlnphi_drho[static_cast<size_t>(i)] * out.drhodk;
    }
    out.backend = "cppad_implicit";
    return out;
#else
    (void)t;
    (void)rho;
    (void)x;
    (void)cppargs;
    (void)target_kind;
    (void)target_index;
    throw ValueError("unsupported: CppAD support is not enabled in this native build.");
#endif
}
