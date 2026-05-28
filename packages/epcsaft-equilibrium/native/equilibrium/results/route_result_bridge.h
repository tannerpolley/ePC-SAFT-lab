#pragma once

#include "equilibrium/core/two_phase_eos_route.h"

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include <string>

namespace epcsaft::native::equilibrium_nlp::route_result_bridge {

inline pybind11::dict route_phase_evidence_to_dict(const RoutePhaseEvidence& phase) {
    pybind11::dict out;
    out["label"] = phase.label;
    out["role"] = phase.role;
    out["phase_kind"] = phase.phase_kind;
    out["amount_total"] = phase.amount_total;
    out["volume"] = phase.volume;
    out["density"] = phase.density;
    out["phase_fraction"] = phase.phase_fraction;
    out["composition"] = phase.composition;
    out["ln_fugacity_coefficients"] = phase.ln_fugacity_coefficients;
    return out;
}

inline pybind11::dict route_physical_evidence_to_dict(const RoutePhysicalEvidence& evidence) {
    pybind11::list phases;
    for (const RoutePhaseEvidence& phase : evidence.phases) {
        phases.append(route_phase_evidence_to_dict(phase));
    }

    pybind11::dict out;
    out["available"] = evidence.available;
    out["phase_count"] = evidence.phase_count;
    out["species_count"] = evidence.species_count;
    out["phase_labels"] = evidence.phase_labels;
    out["phase_roles"] = evidence.phase_roles;
    out["material_balance_norm"] = evidence.material_balance_norm;
    out["pressure_consistency_norm"] = evidence.pressure_consistency_norm;
    out["chemical_potential_consistency_norm"] = evidence.chemical_potential_consistency_norm;
    out["ln_fugacity_consistency_norm"] = evidence.ln_fugacity_consistency_norm;
    out["charge_balance_norm"] = evidence.charge_balance_norm;
    out["fixed_composition_norm"] = evidence.fixed_composition_norm;
    out["phase_amount_total_norm"] = evidence.phase_amount_total_norm;
    out["phase_distance"] = evidence.phase_distance;
    out["minimum_phase_fraction"] = evidence.minimum_phase_fraction;
    out["min_tpd"] = evidence.min_tpd;
    out["candidate_mass_balance_norm"] = evidence.candidate_mass_balance_norm;
    out["phase_discovery_backend"] = evidence.phase_discovery_backend;
    out["stability_certificate"] = evidence.stability_certificate;
    out["phase_set_status"] = evidence.phase_set_status;
    out["stability_checked"] = evidence.stability_checked;
    out["stability_accepted"] = evidence.stability_accepted;
    out["candidate_completeness_accepted"] = evidence.candidate_completeness_accepted;
    out["deterministic_screening_is_full_held"] = evidence.deterministic_screening_is_full_held;
    out["deterministic_screening_status"] = evidence.deterministic_screening_status;
    out["continuous_tpd_status"] = evidence.continuous_tpd_status;
    out["held_stage_i_status"] = evidence.held_stage_i_status;
    out["held_stage_ii_status"] = evidence.held_stage_ii_status;
    out["held_stage_iii_status"] = evidence.held_stage_iii_status;
    out["tpd_candidate_count"] = evidence.tpd_candidate_count;
    out["unique_candidate_count"] = evidence.unique_candidate_count;
    out["selected_candidate_count"] = evidence.selected_candidate_count;
    out["tpd_candidate_values"] = evidence.tpd_candidate_values;
    out["tpd_candidate_sources"] = evidence.tpd_candidate_sources;
    out["tpd_candidate_phase_kinds"] = evidence.tpd_candidate_phase_kinds;
    out["tpd_candidate_compositions"] = evidence.tpd_candidate_compositions;
    out["phases"] = phases;
    return out;
}

template <typename Result>
void apply_ipopt_route_status_fields(pybind11::dict& out, const Result& result) {
    out["backend"] = result.backend;
    out["compiled"] = result.compiled;
    out["adapter_available"] = result.adapter_available;
    out["adapter_kind"] = result.adapter_kind;
    out["problem_name"] = result.problem_name;
    out["derivative_backend"] = result.derivative_backend;
    out["activation_compiler"] = result.activation_compiler;
    out["ran"] = result.ran;
    out["solver_accepted"] = result.solver_accepted;
    out["postsolve_accepted"] = result.postsolve_accepted;
    out["accepted"] = result.accepted;
    out["exact_gradient_required"] = result.exact_gradient_required;
    out["exact_jacobian_required"] = result.exact_jacobian_required;
    out["gradient_approximation"] = result.gradient_approximation;
    out["jacobian_approximation"] = result.jacobian_approximation;
    out["hessian_approximation"] = result.hessian_approximation;
    out["hessian_backend"] = result.hessian_backend;
    out["option_profile"] = result.option_profile;
    out["solver_acceptance_policy"] = result.solver_acceptance_policy;
    out["exact_hessian_policy"] = result.exact_hessian_policy;
    out["scaling_contract"] = result.scaling_contract;
    out["residual_scaling_policy"] = result.residual_scaling_policy;
    out["linear_solver_policy"] = result.linear_solver_policy;
    out["barrier_policy"] = result.barrier_policy;
    out["scaling_method"] = result.scaling_method;
    out["linear_solver_requested"] = result.linear_solver_requested;
    out["linear_solver_selected"] = result.linear_solver_selected;
    out["initial_point_strategy"] = result.initial_point_strategy;
    out["seed_name"] = result.seed_name;
    out["iteration_count"] = result.iteration_count;
    out["iteration_history_limit"] = result.iteration_history_limit;
    out["iteration_history_size"] = result.iteration_history_size;
    out["variable_scaling_count"] = result.variable_scaling_count;
    out["constraint_scaling_count"] = result.constraint_scaling_count;
    out["eval_h_calls"] = result.eval_h_calls;
    out["active_lower_bound_count"] = result.active_lower_bound_count;
    out["active_upper_bound_count"] = result.active_upper_bound_count;
    out["active_variable_bound_count"] = result.active_variable_bound_count;
    out["step_trial_count_max"] = result.step_trial_count_max;
    out["objective_scaling"] = result.objective_scaling;
    out["acceptable_tolerance"] = result.acceptable_tolerance;
    out["constraint_violation_tolerance"] = result.constraint_violation_tolerance;
    out["ipopt_unscaled_constraint_violation_tolerance"] = result.ipopt_unscaled_constraint_violation_tolerance;
    out["dual_infeasibility_tolerance"] = result.dual_infeasibility_tolerance;
    out["complementarity_tolerance"] = result.complementarity_tolerance;
    out["bound_push"] = result.bound_push;
    out["bound_frac"] = result.bound_frac;
    out["variable_scaling_min"] = result.variable_scaling_min;
    out["variable_scaling_max"] = result.variable_scaling_max;
    out["constraint_scaling_min"] = result.constraint_scaling_min;
    out["constraint_scaling_max"] = result.constraint_scaling_max;
    out["variable_scaling_ratio"] = result.variable_scaling_ratio;
    out["constraint_scaling_ratio"] = result.constraint_scaling_ratio;
    out["scaled_constraint_violation_inf_norm"] = result.scaled_constraint_violation_inf_norm;
    out["scaled_stationarity_inf_norm"] = result.scaled_stationarity_inf_norm;
    out["scaled_complementarity_inf_norm"] = result.scaled_complementarity_inf_norm;
    out["bound_complementarity_inf_norm"] = result.bound_complementarity_inf_norm;
    out["barrier_parameter_final"] = result.barrier_parameter_final;
    out["regularization_size_final"] = result.regularization_size_final;
    out["regularization_size_max"] = result.regularization_size_max;
    out["exact_hessian_available"] = result.exact_hessian_available;
    out["profile_exact_hessian_gate"] = result.profile_exact_hessian_gate;
    out["variable_scaling_quality_passed"] = result.variable_scaling_quality_passed;
    out["constraint_scaling_quality_passed"] = result.constraint_scaling_quality_passed;
    out["scaled_acceptance_passed"] = result.scaled_acceptance_passed;
    out["restoration_phase_observed"] = result.restoration_phase_observed;
    out["warm_start_requested"] = result.warm_start_requested;
    out["warm_start_used"] = result.warm_start_used;
    out["ipopt_print_level"] = result.print_level;
    out["max_iterations"] = result.max_iterations;
    out["acceptable_iteration_limit"] = result.acceptable_iteration_limit;
    out["status"] = result.status;
    out["rejection_reason"] = result.rejection_reason;
    out["solver_status"] = result.solver_status;
    out["application_status"] = result.application_status;
    out["last_callback_exception"] = result.last_callback_exception;
    out["last_callback_failure"] = result.last_callback_failure;
}

template <typename Result>
void apply_eos_route_metadata_fields(pybind11::dict& out, const Result& result) {
    out["variable_model"] = result.variable_model;
    out["density_backend"] = result.density_backend;
    out["residual_families"] = result.residual_families;
    out["constraint_families"] = result.constraint_families;
}

template <typename Result>
void apply_ipopt_route_solution_fields(pybind11::dict& out, const Result& result) {
    out["objective"] = result.objective;
    out["variables"] = result.variables;
    out["constraints"] = result.constraints;
}

inline pybind11::dict neutral_route_stability_certificate_from_postsolve(
    const pybind11::object& postsolve,
    const std::string& default_method,
    bool route_accepted
) {
    pybind11::dict stability_certificate;
    stability_certificate["method"] = default_method;
    if (!postsolve.is_none()) {
        pybind11::dict postsolve_dict = postsolve.cast<pybind11::dict>();
        const bool stability_checked = postsolve_dict.contains("stability_checked")
            && postsolve_dict["stability_checked"].cast<bool>();
        const bool stability_accepted = postsolve_dict.contains("stability_accepted")
            && postsolve_dict["stability_accepted"].cast<bool>();
        const bool candidate_complete = postsolve_dict.contains("candidate_completeness_accepted")
            && postsolve_dict["candidate_completeness_accepted"].cast<bool>();
        const bool postsolve_local_only = postsolve_dict.contains("stability_certificate")
            && postsolve_dict["stability_certificate"].cast<std::string>() == "postsolve_local_only";
        stability_certificate["accepted"] = postsolve_local_only
            ? route_accepted
            : stability_checked && stability_accepted && candidate_complete;
        stability_certificate["stability_checked"] = postsolve_local_only ? true : stability_checked;
        stability_certificate["stability_accepted"] = postsolve_local_only ? true : stability_accepted;
        stability_certificate["candidate_set_complete"] = postsolve_local_only ? true : candidate_complete;
        if (postsolve_dict.contains("phase_distance")) {
            stability_certificate["phase_distance"] = postsolve_dict["phase_distance"];
        }
        if (postsolve_dict.contains("phase_discovery_backend")) {
            stability_certificate["phase_discovery_backend"] = postsolve_dict["phase_discovery_backend"];
        }
        if (postsolve_dict.contains("stability_certificate")) {
            stability_certificate["method"] = postsolve_dict["stability_certificate"];
        }
        if (postsolve_dict.contains("phase_set_status")) {
            stability_certificate["status"] = postsolve_dict["phase_set_status"];
        }
        if (postsolve_dict.contains("min_tpd")) {
            stability_certificate["min_tpd"] = postsolve_dict["min_tpd"];
        }
        if (postsolve_dict.contains("candidate_mass_balance_norm")) {
            stability_certificate["candidate_mass_balance_norm"] = postsolve_dict["candidate_mass_balance_norm"];
        }
        if (postsolve_dict.contains("tpd_candidate_count")) {
            stability_certificate["tpd_candidate_count"] = postsolve_dict["tpd_candidate_count"];
        }
        if (postsolve_dict.contains("unique_candidate_count")) {
            stability_certificate["unique_candidate_count"] = postsolve_dict["unique_candidate_count"];
        }
        if (postsolve_dict.contains("selected_candidate_count")) {
            stability_certificate["selected_candidate_count"] = postsolve_dict["selected_candidate_count"];
        }
        for (const char* key : {
                 "stage9_phase_discovery_steps",
                 "deterministic_screening_status",
                 "deterministic_screening_is_full_held",
                 "deterministic_candidate_count",
                 "continuous_tpd_status",
                 "continuous_tpd_backend",
                 "continuous_tpd_start_count",
                 "continuous_tpd_solve_count",
                 "continuous_tpd_converged_count",
                 "continuous_tpd_iteration_count_total",
                 "continuous_tpd_iteration_count_max",
                 "continuous_tpd_min",
                 "continuous_tpd_step_final_max",
                 "held_stage_i_status",
                 "held_stage_i_start_count",
                 "held_stage_i_negative_tpd_found",
                 "held_stage_i_min_tpd",
                 "held_stage_ii_status",
                 "held_stage_ii_candidate_count",
                 "held_stage_iii_status",
                 "held_stage_iii_refined_phase_count",
             }) {
            if (postsolve_dict.contains(key)) {
                stability_certificate[key] = postsolve_dict[key];
            }
        }
    } else {
        stability_certificate["accepted"] = false;
        stability_certificate["stability_checked"] = false;
        stability_certificate["stability_accepted"] = false;
        stability_certificate["candidate_set_complete"] = false;
    }
    return stability_certificate;
}

}  // namespace epcsaft::native::equilibrium_nlp::route_result_bridge
