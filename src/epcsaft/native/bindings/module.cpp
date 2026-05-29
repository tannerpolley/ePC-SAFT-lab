#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include <cmath>
#include <map>
#include <memory>
#include <string>
#include <vector>

#include "autodiff/cppad_smoke_checks.h"
#include "eos/core_internal.h"
#include "eos/contributions/contribution_internal.h"

epcsaft::native::cppad_support::CppADDerivativeResult cppad_eos_contribution_derivatives_cpp(
    double t,
    double rho,
    const std::vector<double>& x,
    const add_args& cppargs
);
epcsaft::native::cppad_support::CppADDerivativeResult cppad_pressure_density_derivative_cpp(
    double t,
    double rho,
    const std::vector<double>& x,
    const add_args& cppargs
);
PhaseStateCompositionSensitivityResult phase_state_ln_fugacity_composition_sensitivity_cpp(
    double t,
    double p,
    std::vector<double> x,
    int phase,
    const add_args& cppargs
);
NeutralBinaryKijPhaseDerivatives neutral_binary_pair_parameter_phase_derivatives_cpp(
    double t,
    double rho,
    const std::vector<double>& x,
    const add_args& cppargs,
    int parameter_index,
    const std::string& parameter_name
);
NeutralBinaryKijPhaseDerivatives generic_component_parameter_phase_derivatives_cpp(
    double t,
    double rho,
    const std::vector<double>& x,
    const add_args& cppargs,
    int target_kind,
    int target_index
);

namespace py = pybind11;

namespace {

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

py::dict born_ssmds_derivative_to_dict(const BornSSMDSDerivativeResult& result) {
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

}  // namespace

PYBIND11_MODULE(_core, m) {
    m.doc() = "pybind11 native backend for epcsaft";

    py::register_exception<ValueError>(m, "NativeValueError");
    py::register_exception<SolutionError>(m, "NativeSolutionError");

    m.def("_native_cppad_smoke", []() {
        return cppad_smoke_to_dict(epcsaft::native::cppad_support::cppad_square_smoke_derivative(3.0));
    });
    m.def("_native_provider_sdk_contract", []() {
        py::dict out;
        const bool equilibrium_native_enabled = false;
        const bool regression_native_enabled = false;
        out["contract_id"] = "provider_native_sdk_v1";
        out["provider_api_contract_id"] = "provider_api_v1";
        out["owner_package"] = "epcsaft";
        out["native_target"] = "epcsaft_provider_native";
        out["cppad_status"] = epcsaft::native::cppad_support::cppad_build_status();
        out["required_native_dependencies"] = std::vector<std::string>{"cppad", "eigen"};
        out["forbidden_native_dependencies"] = std::vector<std::string>{"ceres", "ipopt"};
        out["extension_consumers"] = std::vector<std::string>{"epcsaft-equilibrium", "epcsaft-regression"};
        out["equilibrium_native_enabled"] = equilibrium_native_enabled;
        out["regression_native_enabled"] = regression_native_enabled;
        out["provider_only_core"] = !equilibrium_native_enabled && !regression_native_enabled;
        return out;
    });
    m.def("_native_cppad_eos_contributions", [](double t, double rho, const std::vector<double>& x, const add_args& args) {
        return cppad_smoke_to_dict(cppad_eos_contribution_derivatives_cpp(t, rho, x, args));
    });
    m.def(
        "_native_association_site_fraction_solve",
        [](const std::vector<double>& delta_ij,
           double rho,
           const std::vector<double>& x_assoc,
           int max_iterations,
           double update_tolerance,
           double residual_tolerance) {
            return association_solve_result_to_dict(
                association_site_fraction_solve_result_cpp(
                    delta_ij,
                    rho,
                    x_assoc,
                    max_iterations,
                    update_tolerance,
                    residual_tolerance
                )
            );
        },
        py::arg("delta_ij"),
        py::arg("rho"),
        py::arg("x_assoc"),
        py::arg("max_iterations") = 100,
        py::arg("update_tolerance") = 1.0e-15,
        py::arg("residual_tolerance") = 1.0e-10
    );
    m.def("_native_cppad_pressure_density", [](double t, double rho, const std::vector<double>& x, const add_args& args) {
        return cppad_smoke_to_dict(cppad_pressure_density_derivative_cpp(t, rho, x, args));
    });
    m.def("_native_phase_state_ln_fugacity_composition_sensitivity", [](
        double t,
        double p,
        const std::vector<double>& x,
        int phase,
        const add_args& args
    ) {
        return phase_state_sensitivity_to_dict(
            phase_state_ln_fugacity_composition_sensitivity_cpp(t, p, x, phase, args)
        );
    });
    m.def("_native_cppad_pure_neutral_parameters", [](double t, double rho, const add_args& args) {
        return cppad_smoke_to_dict(cppad_pure_neutral_parameter_derivatives_cpp(t, rho, args));
    });
    m.def("_native_cppad_association_component_parameters", [](
        double t,
        double rho,
        const std::vector<double>& x,
        const add_args& args,
        int component_index
    ) {
        NeutralBinaryKijPhaseDerivatives e_assoc =
            generic_component_parameter_phase_derivatives_cpp(t, rho, x, args, 3, component_index);
        NeutralBinaryKijPhaseDerivatives vol_a =
            generic_component_parameter_phase_derivatives_cpp(t, rho, x, args, 4, component_index);
        return association_component_parameter_derivatives_to_dict(e_assoc, vol_a);
    });
    m.def("_native_cppad_neutral_binary_kij_properties", [](double t, double rho, const std::vector<double>& x, const add_args& args) {
        NeutralBinaryKijPhaseDerivatives forward = neutral_binary_pair_parameter_phase_derivatives_cpp(t, rho, x, args, 1, "k_ij");
        NeutralBinaryKijPhaseDerivatives reverse = neutral_binary_pair_parameter_phase_derivatives_cpp(t, rho, x, args, 2, "k_ij");
        return neutral_binary_kij_property_derivatives_to_dict(forward, reverse);
    });
    m.def("_native_cppad_neutral_binary_pair_properties", [](double t, double rho, const std::vector<double>& x, const add_args& args) {
        NeutralBinaryKijPhaseDerivatives kij_forward = neutral_binary_pair_parameter_phase_derivatives_cpp(t, rho, x, args, 1, "k_ij");
        NeutralBinaryKijPhaseDerivatives kij_reverse = neutral_binary_pair_parameter_phase_derivatives_cpp(t, rho, x, args, 2, "k_ij");
        std::unique_ptr<NeutralBinaryKijPhaseDerivatives> lij_forward;
        std::unique_ptr<NeutralBinaryKijPhaseDerivatives> lij_reverse;
        std::unique_ptr<NeutralBinaryKijPhaseDerivatives> khb_forward;
        std::unique_ptr<NeutralBinaryKijPhaseDerivatives> khb_reverse;
        if (args.l_ij.size() == 4) {
            lij_forward = std::make_unique<NeutralBinaryKijPhaseDerivatives>(
                neutral_binary_pair_parameter_phase_derivatives_cpp(t, rho, x, args, 1, "l_ij")
            );
            lij_reverse = std::make_unique<NeutralBinaryKijPhaseDerivatives>(
                neutral_binary_pair_parameter_phase_derivatives_cpp(t, rho, x, args, 2, "l_ij")
            );
        }
        if (args.k_hb.size() == 4) {
            khb_forward = std::make_unique<NeutralBinaryKijPhaseDerivatives>(
                neutral_binary_pair_parameter_phase_derivatives_cpp(t, rho, x, args, 1, "k_hb_ij")
            );
            khb_reverse = std::make_unique<NeutralBinaryKijPhaseDerivatives>(
                neutral_binary_pair_parameter_phase_derivatives_cpp(t, rho, x, args, 2, "k_hb_ij")
            );
        }
        return neutral_binary_pair_property_derivatives_to_dict(
            kij_forward,
            kij_reverse,
            lij_forward.get(),
            lij_reverse.get(),
            khb_forward.get(),
            khb_reverse.get()
        );
    });

    py::class_<add_args>(m, "NativeArgs")
        .def(py::init<>())
        .def_readwrite("m", &add_args::m)
        .def_readwrite("s", &add_args::s)
        .def_readwrite("e", &add_args::e)
        .def_readwrite("k_ij", &add_args::k_ij)
        .def_readwrite("e_assoc", &add_args::e_assoc)
        .def_readwrite("vol_a", &add_args::vol_a)
        .def_readwrite("z", &add_args::z)
        .def_readwrite("dielc", &add_args::dielc)
        .def_readwrite("mw", &add_args::mw)
        .def_readwrite("mixed_rel_perm_a", &add_args::mixed_rel_perm_a)
        .def_readwrite("mixed_rel_perm_b", &add_args::mixed_rel_perm_b)
        .def_readwrite("mixed_rel_perm_c", &add_args::mixed_rel_perm_c)
        .def_readwrite("mixed_rel_perm_mask", &add_args::mixed_rel_perm_mask)
        .def_readwrite("mixed_rel_perm_water_index", &add_args::mixed_rel_perm_water_index)
        .def_readwrite("dielc_rule", &add_args::dielc_rule)
        .def_readwrite("dielc_diff_mode", &add_args::dielc_diff_mode)
        .def_readwrite("hc_dadx_diff_mode", &add_args::hc_dadx_diff_mode)
        .def_readwrite("disp_dadx_diff_mode", &add_args::disp_dadx_diff_mode)
        .def_readwrite("assoc_dadx_diff_mode", &add_args::assoc_dadx_diff_mode)
        .def_readwrite("d_ion_mode", &add_args::d_ion_mode)
        .def_readwrite("mu_DH_diff_mode", &add_args::mu_DH_diff_mode)
        .def_readwrite("mu_DH_comp_dep_rel_perm", &add_args::mu_DH_comp_dep_rel_perm)
        .def_readwrite("mu_DH_include_sum_term", &add_args::mu_DH_include_sum_term)
        .def_readwrite("include_born_model", &add_args::include_born_model)
        .def_readwrite("d_born_mode", &add_args::d_born_mode)
        .def_readwrite("born_solvation_shell_model", &add_args::born_solvation_shell_model)
        .def_readwrite("born_dielectric_saturation", &add_args::born_dielectric_saturation)
        .def_readwrite("born_bulk_mode", &add_args::born_bulk_mode)
        .def_readwrite("mu_born_diff_mode", &add_args::mu_born_diff_mode)
        .def_readwrite("mu_born_comp_dep_rel_perm", &add_args::mu_born_comp_dep_rel_perm)
        .def_readwrite("mu_born_include_sum_term", &add_args::mu_born_include_sum_term)
        .def_readwrite("mu_born_comp_dep_delta_d", &add_args::mu_born_comp_dep_delta_d)
        .def_readwrite("d_born", &add_args::d_born)
        .def_readwrite("f_solv", &add_args::f_solv)
        .def_readwrite("born_model", &add_args::born_model)
        .def_readwrite("born_radius_model", &add_args::born_radius_model)
        .def_readwrite("born_diff_mode", &add_args::born_diff_mode)
        .def_readwrite("born_eps_mode", &add_args::born_eps_mode)
        .def_readwrite("DH_model", &add_args::DH_model)
        .def_readwrite("assoc_num", &add_args::assoc_num)
        .def_readwrite("assoc_matrix", &add_args::assoc_matrix)
        .def_readwrite("k_hb", &add_args::k_hb)
        .def_readwrite("l_ij", &add_args::l_ij)
        .def_readwrite("parameter_source_label", &add_args::parameter_source_label)
        .def_readwrite("parameter_provenance_status", &add_args::parameter_provenance_status)
        .def_readwrite("binary_interaction_provenance_status", &add_args::binary_interaction_provenance_status)
        .def_readwrite("parameter_provenance_fields", &add_args::parameter_provenance_fields);

    py::class_<ScalarContributionTerms>(m, "ScalarContributionTerms")
        .def_readonly("hc", &ScalarContributionTerms::hc)
        .def_readonly("disp", &ScalarContributionTerms::disp)
        .def_readonly("assoc", &ScalarContributionTerms::assoc)
        .def_readonly("ion", &ScalarContributionTerms::ion)
        .def_readonly("born", &ScalarContributionTerms::born)
        .def_readonly("total", &ScalarContributionTerms::total);

    py::class_<CompressibilityFactorResult>(m, "CompressibilityFactorResult")
        .def_readonly("raw", &CompressibilityFactorResult::raw)
        .def_readonly("terms", &CompressibilityFactorResult::terms);

    py::class_<VectorContributionTerms>(m, "VectorContributionTerms")
        .def_readonly("hc", &VectorContributionTerms::hc)
        .def_readonly("disp", &VectorContributionTerms::disp)
        .def_readonly("assoc", &VectorContributionTerms::assoc)
        .def_readonly("ion", &VectorContributionTerms::ion)
        .def_readonly("born", &VectorContributionTerms::born)
        .def_readonly("total", &VectorContributionTerms::total);

    py::class_<CompositionContributionResult>(m, "CompositionContributionResult")
        .def_readonly("dadx", &CompositionContributionResult::dadx)
        .def_readonly("ares", &CompositionContributionResult::ares)
        .def_readonly("sum_x_dadx", &CompositionContributionResult::sum_x_dadx)
        .def_readonly("z_raw", &CompositionContributionResult::z_raw)
        .def_readonly("z", &CompositionContributionResult::z)
        .def_readonly("derivative_backend", &CompositionContributionResult::derivative_backend)
        .def_readonly("derivative_available", &CompositionContributionResult::derivative_available);

    py::class_<ResidualChemicalPotentialResult>(m, "ResidualChemicalPotentialResult")
        .def_readonly("mu", &ResidualChemicalPotentialResult::mu)
        .def_readonly("composition", &ResidualChemicalPotentialResult::composition);

    py::class_<FugacityContributionResult>(m, "FugacityContributionResult")
        .def_readonly("mu", &FugacityContributionResult::mu)
        .def_readonly("lnfugcoef", &FugacityContributionResult::lnfugcoef)
        .def_readonly("composition", &FugacityContributionResult::composition);

    py::class_<ActivityCoefficientNative>(m, "ActivityCoefficientNative")
        .def_readonly("component_activity_coefficients", &ActivityCoefficientNative::component_activity_coefficients)
        .def_readonly("mean_ionic_activity_coefficients_mole_fraction", &ActivityCoefficientNative::mean_ionic_activity_coefficients_mole_fraction)
        .def_readonly("mean_ionic_activity_coefficients_molality", &ActivityCoefficientNative::mean_ionic_activity_coefficients_molality)
        .def_readonly("solvation_free_energy", &ActivityCoefficientNative::solvation_free_energy)
        .def_readonly("pair_molality", &ActivityCoefficientNative::pair_molality)
        .def_readonly("pair_conversion_factor", &ActivityCoefficientNative::pair_conversion_factor)
        .def_readonly("cation_indices", &ActivityCoefficientNative::cation_indices)
        .def_readonly("anion_indices", &ActivityCoefficientNative::anion_indices)
        .def_readonly("solvent_indices", &ActivityCoefficientNative::solvent_indices)
        .def_readonly("pair_cation_indices", &ActivityCoefficientNative::pair_cation_indices)
        .def_readonly("pair_anion_indices", &ActivityCoefficientNative::pair_anion_indices)
        .def_readonly("pair_nu_cation", &ActivityCoefficientNative::pair_nu_cation)
        .def_readonly("pair_nu_anion", &ActivityCoefficientNative::pair_nu_anion)
        .def_readonly("solvent_index", &ActivityCoefficientNative::solvent_index)
        .def_readonly("osmotic_coefficient", &ActivityCoefficientNative::osmotic_coefficient);

    py::class_<ePCSAFTMixtureNative, std::shared_ptr<ePCSAFTMixtureNative>>(m, "NativeMixture")
        .def(py::init<const add_args&>())
        .def("ncomp", &ePCSAFTMixtureNative::ncomp)
        .def("clear_runtime_caches", &ePCSAFTMixtureNative::clear_runtime_caches)
        .def("reset_runtime_cache_stats", &ePCSAFTMixtureNative::reset_runtime_cache_stats)
        .def("reference_state_cache_hits", &ePCSAFTMixtureNative::reference_state_cache_hits)
        .def("reference_state_cache_misses", &ePCSAFTMixtureNative::reference_state_cache_misses)
        .def("density_warm_start_hits", &ePCSAFTMixtureNative::density_warm_start_hits)
        .def("density_warm_start_rejections", &ePCSAFTMixtureNative::density_warm_start_rejections)
        .def("last_density_diagnostics", [](const ePCSAFTMixtureNative& mixture) {
            return native_density_failure_payload(mixture.last_density_diagnostics());
        });

    py::class_<ePCSAFTStateNative, std::shared_ptr<ePCSAFTStateNative>>(m, "NativeState")
        .def(py::init<
             std::shared_ptr<ePCSAFTMixtureNative>,
             double,
             std::vector<double>,
             int,
             bool,
             double,
             bool,
             double,
             bool,
             double>())
        .def("temperature", &ePCSAFTStateNative::temperature)
        .def("phase", &ePCSAFTStateNative::phase)
        .def("composition", &ePCSAFTStateNative::composition)
        .def("pressure", &ePCSAFTStateNative::pressure)
        .def("density", &ePCSAFTStateNative::density)
        .def("compressibility_factor", &ePCSAFTStateNative::compressibility_factor)
        .def("compressibility_factor_result", &ePCSAFTStateNative::compressibility_factor_result)
        .def("residual_helmholtz", &ePCSAFTStateNative::residual_helmholtz)
        .def("residual_helmholtz_result", &ePCSAFTStateNative::residual_helmholtz_result)
        .def("temperature_derivative_residual_helmholtz", &ePCSAFTStateNative::temperature_derivative_residual_helmholtz)
        .def("temperature_derivative_residual_helmholtz_result", &ePCSAFTStateNative::temperature_derivative_residual_helmholtz_result)
        .def("residual_enthalpy", &ePCSAFTStateNative::residual_enthalpy)
        .def("residual_entropy", &ePCSAFTStateNative::residual_entropy)
        .def("residual_gibbs", &ePCSAFTStateNative::residual_gibbs)
        .def("residual_chemical_potential", &ePCSAFTStateNative::residual_chemical_potential)
        .def("residual_chemical_potential_result", &ePCSAFTStateNative::residual_chemical_potential_result)
        .def("composition_derivative_residual_helmholtz_result", &ePCSAFTStateNative::composition_derivative_residual_helmholtz_result)
        .def("ln_fugacity_coefficient", &ePCSAFTStateNative::ln_fugacity_coefficient)
        .def("fugacity_coefficient", &ePCSAFTStateNative::fugacity_coefficient)
        .def("fugacity_coefficient_result", &ePCSAFTStateNative::fugacity_coefficient_result)
        .def("born_ssmds_liquid_derivatives", [](ePCSAFTStateNative& state) {
            return born_ssmds_derivative_to_dict(state.born_ssmds_liquid_derivatives());
        })
        .def("relative_permittivity", &ePCSAFTStateNative::relative_permittivity)
        .def("osmotic_coefficient", &ePCSAFTStateNative::osmotic_coefficient)
        .def("solvation_free_energy", &ePCSAFTStateNative::solvation_free_energy)
        .def(
            "activity_coefficient_native",
            &ePCSAFTStateNative::activity_coefficient_native,
            py::arg("include_aux") = true,
            py::arg("has_solvent_override") = false,
            py::arg("solvent_override_index") = -1
        );

}
