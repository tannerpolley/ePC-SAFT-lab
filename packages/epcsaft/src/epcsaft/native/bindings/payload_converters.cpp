#include "bindings/payload_converters.h"

#include <pybind11/stl.h>

#include <cmath>

namespace epcsaft::native::bindings {

py::dict cppad_smoke_to_dict(const epcsaft::native::cppad_support::CppADDerivativeResult& result) {
    py::dict out;
    out["cppad_compiled"] = epcsaft::native::cppad_support::cppad_compiled();
    out["supported"] = result.supported;
    out["cppad_used"] = result.supported && result.backend == "cppad";
    out["status"] = epcsaft::native::cppad_support::cppad_build_status();
    out["derivative_backend"] = result.backend;
    out["message"] = result.message;
    out["value"] = result.value;
    out["jacobian_row_major"] = result.jacobian_row_major;
    out["outputs"] = result.outputs;
    out["variables"] = result.variables;
    out["shape"] = py::make_tuple(result.rows, result.cols);
    return out;
}

py::dict association_solve_diagnostics_to_dict(const AssociationSolveDiagnostics& diagnostics) {
    py::dict out;
    out["converged"] = diagnostics.converged;
    out["iteration_count"] = diagnostics.iteration_count;
    out["max_iterations"] = diagnostics.max_iterations;
    out["update_norm"] = diagnostics.update_norm;
    out["update_tolerance"] = diagnostics.update_tolerance;
    out["residual_norm"] = diagnostics.residual_norm;
    out["residual_tolerance"] = diagnostics.residual_tolerance;
    out["min_XA"] = diagnostics.min_XA;
    out["max_XA"] = diagnostics.max_XA;
    out["relaxation_factor"] = diagnostics.relaxation_factor;
    out["relaxation_policy"] = diagnostics.relaxation_policy;
    return out;
}

py::dict association_solve_result_to_dict(const AssociationSolveResult& result) {
    py::dict out;
    out["site_fractions"] = result.XA;
    out["diagnostics"] = association_solve_diagnostics_to_dict(result.diagnostics);
    return out;
}

py::dict phase_state_sensitivity_to_dict(const PhaseStateCompositionSensitivityResult& result) {
    py::dict out;
    out["supported"] = result.supported;
    out["backend"] = result.backend;
    out["derivative_backend"] = result.backend;
    out["density_backend"] = result.density_backend;
    out["message"] = result.message;
    out["temperature"] = result.temperature;
    out["pressure"] = result.pressure;
    out["density"] = result.density;
    out["pressure_density_derivative"] = result.pressure_density_derivative;
    out["pressure_density_second_derivative"] = result.pressure_density_second_derivative;
    out["shape"] = py::make_tuple(result.rows, result.cols);
    out["composition"] = result.composition;
    out["ln_fugacity"] = result.ln_fugacity;
    out["density_composition_derivative"] = result.density_composition_derivative;
    out["density_composition_hessian_row_major"] = result.density_composition_hessian_row_major;
    out["pressure_composition_fixed_density_derivative"] = result.pressure_composition_fixed_density_derivative;
    out["pressure_density_composition_cross_derivative"] = result.pressure_density_composition_cross_derivative;
    out["pressure_composition_fixed_density_hessian_row_major"] =
        result.pressure_composition_fixed_density_hessian_row_major;
    out["ln_fugacity_density_derivative"] = result.ln_fugacity_density_derivative;
    out["fixed_density_jacobian_row_major"] = result.fixed_density_jacobian_row_major;
    out["fixed_density_hessian_tensor_row_major"] = result.fixed_density_hessian_tensor_row_major;
    out["jacobian_row_major"] = result.jacobian_row_major;
    out["hessian_tensor_row_major"] = result.hessian_tensor_row_major;
    out["association_sensitivity_backend"] = result.association_sensitivity_backend;
    out["association_sensitivity_helper"] = result.association_sensitivity_helper;
    out["association_site_count"] = result.association_site_count;
    out["association_site_sensitivity_shape"] = py::make_tuple(
        result.cols + 1,
        result.association_site_count
    );
    out["association_site_sensitivity_row_major"] = result.association_site_sensitivity_row_major;
    out["association_site_second_sensitivity_shape"] = py::make_tuple(
        result.cols + 1,
        result.cols + 1,
        result.association_site_count
    );
    out["association_site_second_sensitivity_tensor_row_major"] =
        result.association_site_second_sensitivity_tensor_row_major;
    return out;
}

py::dict born_parameter_derivative_to_dict(const BornDerivativeResult& result) {
    py::dict out;
    out["supported"] = result.supported;
    out["backend"] = result.backend;
    out["message"] = result.message;
    out["ncomp"] = result.ncomp;
    out["shape"] = py::make_tuple(result.ncomp, result.ncomp);
    out["a_born_d_d_born"] = result.a_born_d_d_born;
    out["a_born_d_f_solv"] = result.a_born_d_f_solv;
    out["mu_res_d_d_born_row_major"] = result.mu_res_d_d_born_row_major;
    out["mu_res_d_f_solv_row_major"] = result.mu_res_d_f_solv_row_major;
    out["lnfug_d_d_born_row_major"] = result.lnfug_d_d_born_row_major;
    out["lnfug_d_f_solv_row_major"] = result.lnfug_d_f_solv_row_major;
    out["lngamma_d_d_born_row_major"] = result.lngamma_d_d_born_row_major;
    out["lngamma_d_f_solv_row_major"] = result.lngamma_d_f_solv_row_major;
    return out;
}

py::dict neutral_binary_kij_property_derivatives_to_dict(
    const NeutralBinaryKijPhaseDerivatives& forward,
    const NeutralBinaryKijPhaseDerivatives& reverse
) {
    if (forward.lnphi.size() != reverse.lnphi.size()
        || forward.dlnphi_dk_fixed_rho.size() != reverse.dlnphi_dk_fixed_rho.size()
        || forward.mu_res.size() != reverse.mu_res.size()
        || forward.dmu_res_dk_fixed_rho.size() != reverse.dmu_res_dk_fixed_rho.size()) {
        throw ValueError("Neutral binary k_ij derivative payloads have inconsistent sizes.");
    }
    std::vector<double> dlnphi_dk;
    std::vector<double> dmu_dk;
    dlnphi_dk.reserve(forward.dlnphi_dk_fixed_rho.size());
    dmu_dk.reserve(forward.dmu_res_dk_fixed_rho.size());
    for (std::size_t i = 0; i < forward.dlnphi_dk_fixed_rho.size(); ++i) {
        dlnphi_dk.push_back(forward.dlnphi_dk_fixed_rho[i] + reverse.dlnphi_dk_fixed_rho[i]);
    }
    for (std::size_t i = 0; i < forward.dmu_res_dk_fixed_rho.size(); ++i) {
        dmu_dk.push_back(forward.dmu_res_dk_fixed_rho[i] + reverse.dmu_res_dk_fixed_rho[i]);
    }
    py::dict out;
    out["supported"] = true;
    out["backend"] = "cppad";
    out["message"] = "CppAD neutral binary k_ij property derivatives available";
    out["pressure"] = forward.pressure;
    out["pressure_d_kij"] = forward.dpdk + reverse.dpdk;
    out["residual_chemical_potential"] = forward.mu_res;
    out["residual_chemical_potential_d_kij_fixed_rho"] = dmu_dk;
    out["ln_fugacity"] = forward.lnphi;
    out["ln_fugacity_d_kij_fixed_rho"] = dlnphi_dk;
    return out;
}

void append_pair_parameter_derivatives(
    py::dict& out,
    const std::string& prefix,
    const NeutralBinaryKijPhaseDerivatives& forward,
    const NeutralBinaryKijPhaseDerivatives& reverse
) {
    if (forward.lnphi.size() != reverse.lnphi.size()
        || forward.dlnphi_dk_fixed_rho.size() != reverse.dlnphi_dk_fixed_rho.size()
        || forward.mu_res.size() != reverse.mu_res.size()
        || forward.dmu_res_dk_fixed_rho.size() != reverse.dmu_res_dk_fixed_rho.size()) {
        throw ValueError("Neutral binary pair-parameter derivative payloads have inconsistent sizes.");
    }
    std::vector<double> dlnphi;
    std::vector<double> dmu;
    dlnphi.reserve(forward.dlnphi_dk_fixed_rho.size());
    dmu.reserve(forward.dmu_res_dk_fixed_rho.size());
    for (std::size_t i = 0; i < forward.dlnphi_dk_fixed_rho.size(); ++i) {
        dlnphi.push_back(forward.dlnphi_dk_fixed_rho[i] + reverse.dlnphi_dk_fixed_rho[i]);
    }
    for (std::size_t i = 0; i < forward.dmu_res_dk_fixed_rho.size(); ++i) {
        dmu.push_back(forward.dmu_res_dk_fixed_rho[i] + reverse.dmu_res_dk_fixed_rho[i]);
    }
    out[(prefix + "_pressure").c_str()] = forward.pressure;
    out[(prefix + "_pressure_derivative").c_str()] = forward.dpdk + reverse.dpdk;
    out[(prefix + "_residual_helmholtz").c_str()] = forward.ares;
    out[(prefix + "_residual_helmholtz_derivative").c_str()] =
        forward.dares_dk_fixed_rho + reverse.dares_dk_fixed_rho;
    out[(prefix + "_residual_chemical_potential").c_str()] = forward.mu_res;
    out[(prefix + "_residual_chemical_potential_derivative").c_str()] = dmu;
    out[(prefix + "_ln_fugacity").c_str()] = forward.lnphi;
    out[(prefix + "_ln_fugacity_derivative").c_str()] = dlnphi;
    if (!forward.association_sensitivity_backend.empty()) {
        out["association_sensitivity_backend"] = forward.association_sensitivity_backend;
        out["association_sensitivity_helper"] = forward.association_sensitivity_helper;
        out["association_site_count"] = forward.association_site_count;
        out["association_site_sensitivity_row_major"] = forward.association_site_sensitivity_row_major;
    }
}

void append_component_parameter_derivatives(
    py::dict& out,
    const std::string& prefix,
    const NeutralBinaryKijPhaseDerivatives& derivative
) {
    out[(prefix + "_pressure").c_str()] = derivative.pressure;
    out[(prefix + "_pressure_derivative").c_str()] = derivative.dpdk;
    out[(prefix + "_residual_helmholtz").c_str()] = derivative.ares;
    out[(prefix + "_residual_helmholtz_derivative").c_str()] = derivative.dares_dk_fixed_rho;
    out[(prefix + "_residual_chemical_potential").c_str()] = derivative.mu_res;
    out[(prefix + "_residual_chemical_potential_derivative").c_str()] =
        derivative.dmu_res_dk_fixed_rho;
    out[(prefix + "_ln_fugacity").c_str()] = derivative.lnphi;
    out[(prefix + "_ln_fugacity_derivative").c_str()] = derivative.dlnphi_dk_fixed_rho;
    if (!derivative.association_sensitivity_backend.empty()) {
        out["association_sensitivity_backend"] = derivative.association_sensitivity_backend;
        out["association_sensitivity_helper"] = derivative.association_sensitivity_helper;
        out["association_site_count"] = derivative.association_site_count;
        out["association_site_sensitivity_row_major"] = derivative.association_site_sensitivity_row_major;
    }
}

py::dict association_component_parameter_derivatives_to_dict(
    const NeutralBinaryKijPhaseDerivatives& e_assoc,
    const NeutralBinaryKijPhaseDerivatives& vol_a
) {
    py::dict out;
    out["supported"] = true;
    out["backend"] = "cppad_implicit";
    out["message"] = "CppAD component association-parameter derivatives with implicit site-fraction sensitivities available";
    out["parameter_names"] = std::vector<std::string>{"e_assoc", "vol_a"};
    append_component_parameter_derivatives(out, "e_assoc", e_assoc);
    append_component_parameter_derivatives(out, "vol_a", vol_a);
    return out;
}

py::dict neutral_binary_pair_property_derivatives_to_dict(
    const NeutralBinaryKijPhaseDerivatives& kij_forward,
    const NeutralBinaryKijPhaseDerivatives& kij_reverse,
    const NeutralBinaryKijPhaseDerivatives* lij_forward,
    const NeutralBinaryKijPhaseDerivatives* lij_reverse,
    const NeutralBinaryKijPhaseDerivatives* khb_forward,
    const NeutralBinaryKijPhaseDerivatives* khb_reverse
) {
    py::dict out;
    out["supported"] = true;
    bool uses_implicit = kij_forward.backend == "cppad_implicit" || kij_reverse.backend == "cppad_implicit";
    if (lij_forward != nullptr && lij_reverse != nullptr) {
        uses_implicit = uses_implicit
            || lij_forward->backend == "cppad_implicit"
            || lij_reverse->backend == "cppad_implicit";
    }
    if (khb_forward != nullptr && khb_reverse != nullptr) {
        uses_implicit = uses_implicit
            || khb_forward->backend == "cppad_implicit"
            || khb_reverse->backend == "cppad_implicit";
    }
    out["backend"] = uses_implicit ? "cppad_implicit" : "cppad";
    out["message"] = uses_implicit
        ? "CppAD binary pair-parameter derivatives with implicit association value routing available"
        : "CppAD neutral binary pair-parameter property derivatives available";
    append_pair_parameter_derivatives(out, "k_ij", kij_forward, kij_reverse);
    out["parameter_names"] = std::vector<std::string>{"k_ij"};
    if (lij_forward != nullptr && lij_reverse != nullptr) {
        append_pair_parameter_derivatives(out, "l_ij", *lij_forward, *lij_reverse);
        out["parameter_names"] = std::vector<std::string>{"k_ij", "l_ij"};
    }
    if (khb_forward != nullptr && khb_reverse != nullptr) {
        append_pair_parameter_derivatives(out, "k_hb_ij", *khb_forward, *khb_reverse);
        out["parameter_names"] = (lij_forward != nullptr && lij_reverse != nullptr)
            ? std::vector<std::string>{"k_ij", "l_ij", "k_hb_ij"}
            : std::vector<std::string>{"k_ij", "k_hb_ij"};
    }
    return out;
}

py::dict native_diagnostics_to_dict(
    const std::map<std::string, double>& doubles,
    const std::map<std::string, int>& ints,
    const std::map<std::string, bool>& bools,
    const std::map<std::string, std::string>& strings,
    const std::map<std::string, std::vector<double>>& vectors
) {
    py::dict out;
    for (const auto& item : doubles) {
        out[py::str(item.first)] = item.second;
    }
    for (const auto& item : ints) {
        out[py::str(item.first)] = item.second;
    }
    for (const auto& item : bools) {
        out[py::str(item.first)] = item.second;
    }
    for (const auto& item : strings) {
        out[py::str(item.first)] = item.second;
    }
    for (const auto& item : vectors) {
        out[py::str(item.first)] = item.second;
    }
    return out;
}

double json_safe_native_double(double value) {
    return std::isfinite(value) ? value : 1.0e300;
}

py::dict native_density_candidate_to_dict(const DensityCandidateDiagnostics& candidate) {
    py::dict out;
    out["rho_sort"] = json_safe_native_double(candidate.rho_sort);
    out["rho"] = json_safe_native_double(candidate.rho);
    out["gres"] = json_safe_native_double(candidate.gres);
    out["rel_resid"] = json_safe_native_double(candidate.rel_resid);
    out["abs_p_error"] = json_safe_native_double(candidate.abs_p_error);
    out["valid"] = candidate.valid;
    return out;
}

py::dict native_density_diagnostics_to_dict(const DensitySolveDiagnostics& diagnostics) {
    py::dict out;
    out["phase_label"] = diagnostics.phase_label;
    out["phase_kind"] = diagnostics.phase_kind;
    out["T"] = json_safe_native_double(diagnostics.t);
    out["P"] = json_safe_native_double(diagnostics.p);
    out["composition"] = diagnostics.composition;
    out["scan_point_count"] = diagnostics.scan_point_count;
    out["finite_point_count"] = diagnostics.finite_point_count;
    out["coarse_bracket_count"] = diagnostics.coarse_bracket_count;
    out["refined_bracket_count"] = diagnostics.refined_bracket_count;
    out["candidate_root_count"] = diagnostics.candidate_root_count;
    out["best_near_root_pressure_error"] = json_safe_native_double(diagnostics.best_near_root.abs_p_error);
    out["best_near_root"] = native_density_candidate_to_dict(diagnostics.best_near_root);
    out["gres"] = json_safe_native_double(diagnostics.best_near_root.gres);
    out["rejection_reason"] = diagnostics.rejection_reason;
    out["density_best_candidate_refinement_used"] = diagnostics.best_candidate_refinement_used;
    out["density_best_candidate_rejection_reason"] = diagnostics.best_candidate_rejection_reason;
    out["density_warm_start_source"] = diagnostics.warm_start_source;
    out["density_validity_gate"] = diagnostics.validity_gate;
    py::list roots;
    for (const auto& candidate : diagnostics.candidate_roots) {
        roots.append(native_density_candidate_to_dict(candidate));
    }
    out["density_candidate_roots"] = roots;
    return out;
}

py::dict native_density_failure_payload(const DensitySolveDiagnostics& diagnostics) {
    py::dict out;
    py::list contexts;
    contexts.append(native_density_diagnostics_to_dict(diagnostics));
    out["density_failure_count"] = diagnostics.validity_gate == "failed" ? 1 : 0;
    out["density_failure_contexts"] = contexts;
    out["density_scan_summary"] = native_density_diagnostics_to_dict(diagnostics);
    out["density_candidate_roots"] = contexts[0].cast<py::dict>()["density_candidate_roots"];
    out["density_best_near_root"] = contexts[0].cast<py::dict>()["best_near_root"];
    out["density_best_candidate_refinement_used"] = diagnostics.best_candidate_refinement_used;
    out["density_best_candidate_rejection_reason"] = diagnostics.best_candidate_rejection_reason;
    out["density_warm_start_source"] = diagnostics.warm_start_source;
    out["density_validity_gate"] = diagnostics.validity_gate;
    return out;
}

}  // namespace epcsaft::native::bindings
