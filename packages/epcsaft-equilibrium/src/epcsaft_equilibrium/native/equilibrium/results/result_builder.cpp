#include "equilibrium/results/result_builder.h"

#include "equilibrium/core/route_metadata.h"
#include "equilibrium/results/held_certification.h"

#include <algorithm>
#include <cmath>
#include <limits>
#include <numeric>
#include <utility>

namespace epcsaft::native::equilibrium_nlp {

namespace {

constexpr const char* kRouteStatusAccepted = "accepted";
constexpr const char* kRouteStatusProductionAccepted = "production_accepted";
constexpr const char* kRouteStatusPostsolveRejected = "postsolve_rejected";
constexpr const char* kRouteStatusSolverRejected = "solver_rejected";
constexpr const char* kRouteStatusIpoptDependencyRequired = "ipopt_dependency_required";
constexpr const char* kRouteStatusUnstable = "unstable";
constexpr const char* kRouteStatusOptimizerConvergedUncertified = "optimizer_converged_uncertified";
void apply_ipopt_solve_metadata(NeutralTwoPhaseEosRouteResult& out, const IpoptSolveResult& solve) {
    const RouteMetadata route_metadata = route_metadata_from_diagnostics(solve.diagnostics_string);
    if (!route_metadata.variable_model.empty()) {
        out.variable_model = route_metadata.variable_model;
    }
    if (!route_metadata.density_backend.empty()) {
        out.density_backend = route_metadata.density_backend;
    }
    if (!route_metadata.residual_families.empty()) {
        out.residual_families = route_metadata.residual_families;
    }
    if (!route_metadata.constraint_families.empty()) {
        out.constraint_families = route_metadata.constraint_families;
    }
    out.solver_feasible_point = solve.feasible_point;
    out.gradient_approximation = solve_diagnostic_string(solve, "gradient_approximation", "exact");
    out.jacobian_approximation = solve_diagnostic_string(solve, "jacobian_approximation", "exact");
    out.hessian_approximation = solve_diagnostic_string(solve, "hessian_approximation", out.hessian_approximation);
    out.hessian_backend = solve_diagnostic_string(solve, "hessian_backend", out.hessian_backend);
    out.option_profile = solve_diagnostic_string(solve, "option_profile", out.option_profile);
    out.solver_acceptance_policy =
        solve_diagnostic_string(solve, "solver_acceptance_policy", out.solver_acceptance_policy);
    out.exact_hessian_policy = solve_diagnostic_string(solve, "exact_hessian_policy", out.exact_hessian_policy);
    out.scaling_contract = solve_diagnostic_string(solve, "scaling_contract", out.scaling_contract);
    out.residual_scaling_policy =
        solve_diagnostic_string(solve, "residual_scaling_policy", out.residual_scaling_policy);
    out.linear_solver_policy = solve_diagnostic_string(solve, "linear_solver_policy", out.linear_solver_policy);
    out.barrier_policy = solve_diagnostic_string(solve, "barrier_policy", out.barrier_policy);
    out.last_callback_exception = solve_diagnostic_string(solve, "last_callback_exception", out.last_callback_exception);
    out.last_callback_failure = solve_diagnostic_string(solve, "last_callback_failure", out.last_callback_failure);
    out.scaling_method = solve_diagnostic_string(solve, "scaling_method", out.scaling_method);
    out.linear_solver_requested = solve_diagnostic_string(solve, "linear_solver_requested", out.linear_solver_requested);
    out.linear_solver_selected = solve_diagnostic_string(solve, "linear_solver_selected", out.linear_solver_selected);
    out.print_level = solve_diagnostic_int(solve, "print_level");
    out.max_iterations = solve_diagnostic_int(solve, "max_iterations");
    out.acceptable_iteration_limit = solve_diagnostic_int(solve, "acceptable_iteration_limit");
    out.iteration_count = solve_diagnostic_int(solve, "iteration_count");
    out.iteration_history_limit = solve_diagnostic_int(solve, "iteration_history_limit");
    out.iteration_history_size = solve_diagnostic_int(solve, "iteration_history_size");
    out.variable_scaling_count = solve_diagnostic_int(solve, "variable_scaling_count");
    out.constraint_scaling_count = solve_diagnostic_int(solve, "constraint_scaling_count");
    out.eval_h_calls = solve_diagnostic_int(solve, "eval_h_calls");
    out.active_lower_bound_count = solve_diagnostic_int(solve, "active_lower_bound_count");
    out.active_upper_bound_count = solve_diagnostic_int(solve, "active_upper_bound_count");
    out.active_variable_bound_count = solve_diagnostic_int(solve, "active_variable_bound_count");
    out.step_trial_count_max = solve_diagnostic_int(solve, "step_trial_count_max");
    out.objective_scaling = solve_diagnostic_double(solve, "objective_scaling", out.objective_scaling);
    out.acceptable_tolerance = solve_diagnostic_double(solve, "acceptable_tolerance", out.acceptable_tolerance);
    out.constraint_violation_tolerance =
        solve_diagnostic_double(solve, "constraint_violation_tolerance", out.constraint_violation_tolerance);
    out.ipopt_unscaled_constraint_violation_tolerance = solve_diagnostic_double(
        solve,
        "ipopt_unscaled_constraint_violation_tolerance",
        out.ipopt_unscaled_constraint_violation_tolerance
    );
    out.dual_infeasibility_tolerance =
        solve_diagnostic_double(solve, "dual_infeasibility_tolerance", out.dual_infeasibility_tolerance);
    out.complementarity_tolerance =
        solve_diagnostic_double(solve, "complementarity_tolerance", out.complementarity_tolerance);
    out.bound_push = solve_diagnostic_double(solve, "bound_push", out.bound_push);
    out.bound_frac = solve_diagnostic_double(solve, "bound_frac", out.bound_frac);
    out.variable_scaling_min = solve_diagnostic_double(solve, "variable_scaling_min", out.variable_scaling_min);
    out.variable_scaling_max = solve_diagnostic_double(solve, "variable_scaling_max", out.variable_scaling_max);
    out.constraint_scaling_min = solve_diagnostic_double(solve, "constraint_scaling_min", out.constraint_scaling_min);
    out.constraint_scaling_max = solve_diagnostic_double(solve, "constraint_scaling_max", out.constraint_scaling_max);
    out.variable_scaling_ratio = solve_diagnostic_double(solve, "variable_scaling_ratio", out.variable_scaling_ratio);
    out.constraint_scaling_ratio =
        solve_diagnostic_double(solve, "constraint_scaling_ratio", out.constraint_scaling_ratio);
    out.scaled_constraint_violation_inf_norm = solve_diagnostic_double(
        solve,
        "scaled_constraint_violation_inf_norm",
        out.scaled_constraint_violation_inf_norm
    );
    out.scaled_stationarity_inf_norm = solve_diagnostic_double(
        solve,
        "scaled_stationarity_inf_norm",
        out.scaled_stationarity_inf_norm
    );
    out.scaled_complementarity_inf_norm = solve_diagnostic_double(
        solve,
        "scaled_complementarity_inf_norm",
        out.scaled_complementarity_inf_norm
    );
    out.bound_complementarity_inf_norm = solve_diagnostic_double(
        solve,
        "bound_complementarity_inf_norm",
        out.bound_complementarity_inf_norm
    );
    out.barrier_parameter_final =
        solve_diagnostic_double(solve, "barrier_parameter_final", out.barrier_parameter_final);
    out.regularization_size_final =
        solve_diagnostic_double(solve, "regularization_size_final", out.regularization_size_final);
    out.regularization_size_max =
        solve_diagnostic_double(solve, "regularization_size_max", out.regularization_size_max);
    out.exact_hessian_available = solve_diagnostic_bool(solve, "exact_hessian_available");
    out.profile_exact_hessian_gate = solve_diagnostic_bool(solve, "profile_exact_hessian_gate", true);
    out.variable_scaling_quality_passed = solve_diagnostic_bool(solve, "variable_scaling_quality_passed", true);
    out.constraint_scaling_quality_passed = solve_diagnostic_bool(solve, "constraint_scaling_quality_passed", true);
    out.scaled_acceptance_passed = solve_diagnostic_bool(solve, "scaled_acceptance_passed");
    out.restoration_phase_observed = solve_diagnostic_bool(solve, "restoration_phase_observed");
    out.warm_start_requested = solve_diagnostic_bool(solve, "warm_start_requested");
    out.warm_start_used = solve_diagnostic_bool(solve, "warm_start_used");
    out.bound_lower_multipliers = solve.bound_lower_multipliers;
    out.bound_upper_multipliers = solve.bound_upper_multipliers;
    out.constraint_multipliers = solve.constraint_multipliers;
    out.iteration_history = solve.iteration_history;
}

std::string neutral_route_postsolve_status(
    const NeutralTwoPhaseEosPostsolve& postsolve,
    NeutralRouteCertificationLevel certification_level
) {
    if (postsolve.accepted) {
        return certification_level == NeutralRouteCertificationLevel::PhaseSetCertified
            ? kRouteStatusProductionAccepted
            : kRouteStatusAccepted;
    }
    if (postsolve.rejection_reason == "stability_tpd") {
        return kRouteStatusUnstable;
    }
    if (postsolve.rejection_reason == "candidate_completeness") {
        return kRouteStatusOptimizerConvergedUncertified;
    }
    return kRouteStatusPostsolveRejected;
}

std::string neutral_route_rejection_reason(const std::string& status, const std::string& postsolve_reason) {
    if (!postsolve_reason.empty()) {
        return postsolve_reason;
    }
    return status;
}

std::string phase_kind_role(int phase_kind) {
    if (phase_kind == 0) {
        return "liquid";
    }
    if (phase_kind == 1) {
        return "vapor";
    }
    return "phase";
}

std::string default_phase_label(std::size_t index) {
    return "phase_" + std::to_string(index);
}

std::string default_phase_role(const std::vector<int>& phase_kinds, std::size_t index) {
    if (index < phase_kinds.size()) {
        return phase_kind_role(phase_kinds[index]);
    }
    return "phase";
}

std::size_t route_evidence_phase_count(const NeutralTwoPhaseEosRouteResult& result) {
    return std::max({
        result.phase_labels.size(),
        result.phase_roles.size(),
        result.phase_amounts.size(),
        result.phase_volumes.size(),
        result.postsolve.phase_amount_totals.size(),
        result.postsolve.phase_volumes.size(),
        result.postsolve.phase_densities.size(),
        result.postsolve.phase_compositions.size(),
        result.postsolve.phase_ln_fugacity_coefficients.size(),
        result.postsolve.selected_phase_kinds.size(),
    });
}

double indexed_or_zero(const std::vector<double>& values, std::size_t index) {
    return index < values.size() ? values[index] : 0.0;
}

int indexed_or_zero(const std::vector<int>& values, std::size_t index) {
    return index < values.size() ? values[index] : 0;
}

std::vector<double> indexed_or_empty(
    const std::vector<std::vector<double>>& values,
    std::size_t index
) {
    return index < values.size() ? values[index] : std::vector<double>{};
}

}  // namespace

void mark_neutral_route_ipopt_dependency_required(NeutralTwoPhaseEosRouteResult& out) {
    out.ran = false;
    out.solver_accepted = false;
    out.postsolve_accepted = false;
    out.accepted = false;
    out.status = kRouteStatusIpoptDependencyRequired;
    out.rejection_reason = kRouteStatusIpoptDependencyRequired;
}

void mark_neutral_route_derivative_preflight_failed(
    NeutralTwoPhaseEosRouteResult& out,
    const NlpProblem& problem,
    const std::string& message
) {
    out.ran = false;
    out.solver_accepted = false;
    out.solver_feasible_point = false;
    out.postsolve_accepted = false;
    out.accepted = false;
    out.status = kRouteStatusSolverRejected;
    out.rejection_reason = "derivative_preflight_failed";
    out.solver_status = "preflight_failed";
    out.application_status = "derivative_contract_failed";
    out.last_callback_failure = "derivative_preflight_failed";
    out.last_callback_exception = message;
    out.hessian_approximation = "exact";
    out.hessian_backend = problem.hessian_backend();
    out.exact_hessian_available = false;
}

bool apply_neutral_route_solve_result(NeutralTwoPhaseEosRouteResult& out, const IpoptSolveResult& solve) {
    return apply_neutral_route_solve_result(out, solve, NeutralRouteAcceptablePointCriteria{});
}

bool apply_neutral_route_solve_result(
    NeutralTwoPhaseEosRouteResult& out,
    const IpoptSolveResult& solve,
    const NeutralRouteAcceptablePointCriteria& acceptable_point
) {
    const bool certified_acceptable_point =
        acceptable_point.enabled
        && solve.acceptable
        && solve.application_status == "solved_to_acceptable_level"
        && !solve.variables.empty()
        && solve_diagnostic_double(
               solve,
               "scaled_constraint_violation_inf_norm",
               std::numeric_limits<double>::infinity()
           ) <= acceptable_point.scaled_constraint_violation_limit
        && solve_diagnostic_double(
               solve,
               "scaled_stationarity_inf_norm",
               std::numeric_limits<double>::infinity()
           ) <= acceptable_point.scaled_stationarity_limit
        && solve_diagnostic_double(
               solve,
               "scaled_complementarity_inf_norm",
               std::numeric_limits<double>::infinity()
           ) <= acceptable_point.scaled_complementarity_limit;
    out.ran = solve.solver_ran;
    out.solver_accepted = ipopt_solve_result_allows_postsolve(solve) || certified_acceptable_point;
    out.solver_status = solve.solver_status;
    out.application_status = solve.application_status;
    apply_ipopt_solve_metadata(out, solve);
    out.objective = solve.objective;
    out.variables = solve.variables;
    out.constraints = solve.constraints;
    if (!out.solver_accepted) {
        out.postsolve_accepted = false;
        out.accepted = false;
        out.status = kRouteStatusSolverRejected;
        out.rejection_reason = kRouteStatusSolverRejected;
    }
    return out.solver_accepted;
}

void apply_neutral_route_postsolve(
    NeutralTwoPhaseEosRouteResult& out,
    NeutralTwoPhaseEosPostsolve postsolve,
    NeutralRouteCertificationLevel certification_level
) {
    out.postsolve = std::move(postsolve);
    out.postsolve_accepted = out.postsolve.accepted;
    out.accepted = out.solver_accepted && out.postsolve_accepted;
    out.status = neutral_route_postsolve_status(out.postsolve, certification_level);
    out.rejection_reason = neutral_route_rejection_reason(out.status, out.postsolve.rejection_reason);
}

void certify_neutral_phase_discovery(
    NeutralPhaseDiscoveryResult& discovery,
    NeutralPhaseDiscoveryAcceptancePolicy policy,
    double tpd_tolerance,
    double candidate_mass_balance_tolerance,
    bool negative_novel_candidate
) {
    discovery.phase_set_mass_balance_feasible =
        discovery.candidate_mass_balance_norm <= candidate_mass_balance_tolerance;

    if (policy == NeutralPhaseDiscoveryAcceptancePolicy::CandidateMassBalanceOnly) {
        discovery.candidate_completeness_accepted = discovery.phase_set_mass_balance_feasible;
        discovery.phase_set_status = discovery.phase_set_mass_balance_feasible
            ? "candidate_mass_balance_feasible"
            : "candidate_mass_balance_incomplete";
        return;
    }

    const bool tpd_stable = discovery.stability_checked && discovery.min_tpd >= -tpd_tolerance;
    if (policy == NeutralPhaseDiscoveryAcceptancePolicy::AcceptedPhaseSet) {
        discovery.stability_accepted = discovery.stability_checked && !negative_novel_candidate;
        discovery.candidate_completeness_accepted =
            discovery.phase_set_mass_balance_feasible && discovery.stability_accepted;
        if (!discovery.stability_checked) {
            discovery.phase_set_status = "stability_uncertified";
        } else if (!discovery.stability_accepted) {
            discovery.phase_set_status = "negative_tpd_candidate";
        } else if (!discovery.phase_set_mass_balance_feasible) {
            discovery.phase_set_status = "candidate_mass_balance_incomplete";
        } else {
            discovery.phase_set_status = "phase_set_certified";
        }
        return;
    }

    if (policy == NeutralPhaseDiscoveryAcceptancePolicy::GeneralizedFeed) {
        if (!discovery.stability_checked) {
            discovery.stability_accepted = false;
            discovery.candidate_completeness_accepted = false;
            discovery.phase_set_status = "stability_uncertified";
        } else if (!discovery.phase_set_mass_balance_feasible) {
            discovery.stability_accepted = tpd_stable;
            discovery.candidate_completeness_accepted = false;
            discovery.phase_set_status = "candidate_mass_balance_incomplete";
        } else if (discovery.held_stage_ii_replay_ready) {
            discovery.stability_accepted = false;
            discovery.candidate_completeness_accepted = false;
            discovery.phase_set_status =
                "sampled_candidate_audit_complete_global_completeness_unproven";
        } else if (tpd_stable) {
            discovery.stability_accepted = true;
            discovery.candidate_completeness_accepted = true;
            discovery.phase_set_status = "single_phase_stable_candidate_set";
        } else {
            discovery.stability_accepted = false;
            discovery.candidate_completeness_accepted = false;
            discovery.phase_set_status = "candidate_bound_gap_open";
        }
        return;
    }

    if (policy == NeutralPhaseDiscoveryAcceptancePolicy::ElectrolyteDeterministic) {
        discovery.held_stage_i_status = "pending_held2_dual_phase_discovery";
        mark_held_stage_ii_pending(discovery, "pending_held2_dual_phase_discovery");
        discovery.stability_accepted = tpd_stable;
        if (!discovery.stability_checked) {
            discovery.candidate_completeness_accepted = false;
            discovery.phase_set_status = "stability_uncertified";
        } else if (!discovery.phase_set_mass_balance_feasible) {
            discovery.candidate_completeness_accepted = false;
            discovery.phase_set_status = "candidate_mass_balance_incomplete";
        } else if (discovery.stability_accepted) {
            discovery.candidate_completeness_accepted = true;
            discovery.phase_set_status = "charge_neutral_tpd_screening_complete";
        } else {
            discovery.candidate_completeness_accepted = false;
            discovery.phase_set_status = "charge_neutral_tpd_negative_candidate";
        }
        return;
    }

    if (policy == NeutralPhaseDiscoveryAcceptancePolicy::ElectrolyteContinuous) {
        discovery.held_stage_i_status = "pending_stage_i_stability_certificate";
        mark_held_stage_ii_pending(discovery, "pending_held2_stage_ii_discovery");
        discovery.stability_accepted = tpd_stable;
        const bool has_converged_start = discovery.continuous_tpd_converged_count > 0;
        const bool has_rejected_start =
            discovery.continuous_tpd_converged_count < discovery.continuous_tpd_solve_count;
        if (!discovery.stability_checked) {
            discovery.candidate_completeness_accepted = false;
            discovery.phase_set_status = "stability_uncertified";
        } else if (!has_converged_start) {
            discovery.candidate_completeness_accepted = false;
            discovery.phase_set_status = "continuous_reduced_electroneutral_tpd_incomplete";
        } else if (has_rejected_start) {
            discovery.candidate_completeness_accepted = true;
            discovery.phase_set_status = "continuous_reduced_electroneutral_tpd_complete_with_rejected_starts";
        } else {
            discovery.candidate_completeness_accepted = true;
            discovery.phase_set_status = "continuous_reduced_electroneutral_tpd_complete";
        }
        return;
    }

    discovery.stability_accepted = discovery.held_stage_ii_replay_ready;
    discovery.candidate_completeness_accepted = discovery.held_stage_ii_replay_ready;
    discovery.phase_set_status = discovery.candidate_completeness_accepted
        ? "held2_stage_ii_candidate_set_verified"
        : "held2_stage_ii_candidate_set_incomplete";
}

void copy_neutral_phase_discovery_evidence(
    NeutralTwoPhaseEosPostsolve& postsolve,
    const NeutralPhaseDiscoveryResult& discovery
) {
    postsolve.stability_checked = discovery.stability_checked;
    postsolve.stability_accepted = discovery.stability_accepted;
    postsolve.candidate_completeness_accepted = discovery.candidate_completeness_accepted;
    postsolve.phase_set_mass_balance_feasible = discovery.phase_set_mass_balance_feasible;
    postsolve.phase_discovery_backend = discovery.phase_discovery_backend;
    postsolve.stability_certificate = discovery.stability_certificate;
    postsolve.phase_set_status = discovery.phase_set_status;
    postsolve.stage9_phase_discovery_steps = discovery.stage9_phase_discovery_steps;
    postsolve.deterministic_screening_status = discovery.deterministic_screening_status;
    postsolve.deterministic_screening_is_full_held = discovery.deterministic_screening_is_full_held;
    postsolve.continuous_tpd_status = discovery.continuous_tpd_status;
    postsolve.continuous_tpd_backend = discovery.continuous_tpd_backend;
    postsolve.continuous_tpd_best_source = discovery.continuous_tpd_best_source;
    postsolve.deterministic_candidate_count = discovery.deterministic_candidate_count;
    postsolve.continuous_tpd_start_count = discovery.continuous_tpd_start_count;
    postsolve.continuous_tpd_solve_count = discovery.continuous_tpd_solve_count;
    postsolve.continuous_tpd_converged_count = discovery.continuous_tpd_converged_count;
    postsolve.continuous_tpd_iteration_count_total = discovery.continuous_tpd_iteration_count_total;
    postsolve.continuous_tpd_iteration_count_max = discovery.continuous_tpd_iteration_count_max;
    postsolve.continuous_tpd_min = discovery.continuous_tpd_min;
    postsolve.continuous_tpd_step_final_max = discovery.continuous_tpd_step_final_max;
    postsolve.continuous_tpd_best_phase_kind = discovery.continuous_tpd_best_phase_kind;
    postsolve.continuous_tpd_best_density = discovery.continuous_tpd_best_density;
    postsolve.continuous_tpd_best_molar_volume = discovery.continuous_tpd_best_molar_volume;
    postsolve.continuous_tpd_best_composition = discovery.continuous_tpd_best_composition;
    postsolve.held_stage_i_status = discovery.held_stage_i_status;
    postsolve.held_stage_i_start_count = discovery.held_stage_i_start_count;
    postsolve.held_stage_i_negative_tpd_found = discovery.held_stage_i_negative_tpd_found;
    postsolve.held_stage_i_min_tpd = discovery.held_stage_i_min_tpd;
    postsolve.held_stage_ii_status = discovery.held_stage_ii_status;
    postsolve.held_stage_ii_candidate_bound_audit_status = discovery.held_stage_ii_candidate_bound_audit_status;
    postsolve.held_stage_ii_dual_loop_status = discovery.held_stage_ii_dual_loop_status;
    postsolve.held_stage_ii_major_iterations = discovery.held_stage_ii_major_iterations;
    postsolve.held_stage_ii_candidate_count = discovery.held_stage_ii_candidate_count;
    postsolve.held_stage_ii_lower_bound = discovery.held_stage_ii_lower_bound;
    postsolve.held_stage_ii_upper_bound = discovery.held_stage_ii_upper_bound;
    postsolve.held_stage_ii_bound_gap = discovery.held_stage_ii_bound_gap;
    postsolve.held_stage_ii_bound_tolerance = discovery.held_stage_ii_bound_tolerance;
    postsolve.held_stage_ii_stopping_reason = discovery.held_stage_ii_stopping_reason;
    postsolve.held_stage_ii_lower_bound_history = discovery.held_stage_ii_lower_bound_history;
    postsolve.held_stage_ii_upper_bound_history = discovery.held_stage_ii_upper_bound_history;
    postsolve.held_stage_ii_bound_gap_history = discovery.held_stage_ii_bound_gap_history;
    postsolve.held_stage_ii_replay_ready = discovery.held_stage_ii_replay_ready;
    postsolve.held_stage_ii_replay_source = discovery.held_stage_ii_replay_source;
    postsolve.held_stage_ii_replay_seed_name = discovery.held_stage_ii_replay_seed_name;
    postsolve.held_stage_ii_replay_candidate_count = discovery.held_stage_ii_replay_candidate_count;
    postsolve.held_stage_ii_replay_candidate_ranks = discovery.held_stage_ii_replay_candidate_ranks;
    postsolve.held_stage_ii_replay_phase_fractions = discovery.held_stage_ii_replay_phase_fractions;
    postsolve.held_stage_ii_replay_phase_kinds = discovery.held_stage_ii_replay_phase_kinds;
    postsolve.held_stage_ii_replay_phase_compositions = discovery.held_stage_ii_replay_phase_compositions;
    postsolve.held_stage_ii_rejected_candidate_count = discovery.held_stage_ii_rejected_candidate_count;
    postsolve.held_stage_ii_rejected_candidate_ranks = discovery.held_stage_ii_rejected_candidate_ranks;
    postsolve.held_stage_ii_rejected_candidate_reasons = discovery.held_stage_ii_rejected_candidate_reasons;
    postsolve.held_stage_iii_status = discovery.held_stage_iii_status;
    postsolve.held_stage_iii_refined_phase_count = discovery.held_stage_iii_refined_phase_count;
    postsolve.min_tpd = discovery.min_tpd;
    postsolve.candidate_mass_balance_norm = discovery.candidate_mass_balance_norm;
    postsolve.tpd_candidate_count = discovery.tpd_candidate_count;
    postsolve.unique_candidate_count = discovery.unique_candidate_count;
    postsolve.selected_candidate_count = discovery.selected_candidate_count;
    postsolve.selected_phase_fractions = discovery.selected_phase_fractions;
    postsolve.selected_phase_kinds = discovery.selected_phase_kinds;
    postsolve.selected_phase_compositions = discovery.selected_phase_compositions;
    postsolve.tpd_candidate_values.clear();
    postsolve.tpd_candidate_sources.clear();
    postsolve.tpd_candidate_phase_kinds.clear();
    postsolve.tpd_candidate_compositions.clear();
    postsolve.tpd_candidate_pressure_residuals.clear();
    postsolve.tpd_candidate_iteration_counts.clear();
    postsolve.tpd_candidate_step_finals.clear();
    postsolve.tpd_candidate_ranks.clear();
    postsolve.tpd_candidate_feasibility_statuses.clear();
    postsolve.tpd_candidate_selected.clear();
    for (const NeutralTpdCandidate& candidate : discovery.candidates) {
        postsolve.tpd_candidate_values.push_back(candidate.tpd);
        postsolve.tpd_candidate_sources.push_back(candidate.source);
        postsolve.tpd_candidate_phase_kinds.push_back(candidate.phase_kind);
        postsolve.tpd_candidate_compositions.push_back(candidate.composition);
        postsolve.tpd_candidate_pressure_residuals.push_back(candidate.pressure_residual_estimate);
        postsolve.tpd_candidate_iteration_counts.push_back(candidate.tpd_iteration_count);
        postsolve.tpd_candidate_step_finals.push_back(candidate.tpd_step_final);
        postsolve.tpd_candidate_ranks.push_back(candidate.candidate_rank);
        postsolve.tpd_candidate_feasibility_statuses.push_back(candidate.feasibility_status);
        postsolve.tpd_candidate_selected.push_back(candidate.selected);
    }
}

void certify_neutral_postsolve(
    NeutralTwoPhaseEosPostsolve& postsolve,
    const NeutralPostsolveAcceptanceCriteria& criteria
) {
    if (!criteria.stability_certification_required && !criteria.stability_evidence_pending) {
        postsolve.stability_checked = false;
        postsolve.stability_accepted = true;
        postsolve.candidate_completeness_accepted = true;
        postsolve.phase_set_mass_balance_feasible = true;
        postsolve.stability_certificate = "postsolve_local_only";
        postsolve.phase_set_status = "not_required";
    }

    const double chemical_tolerance = criteria.charged_system
        ? std::max(
              criteria.chemical_potential_tolerance,
              2.0 * std::sqrt(criteria.chemical_potential_tolerance)
          )
        : criteria.chemical_potential_tolerance;

    std::string reason;
    if (
        criteria.charge_balance_required
        && !(postsolve.charge_balance_norm <= criteria.charge_tolerance)
    ) {
        reason = "charge_balance";
    } else if (
        criteria.phase_amount_total_required
        && !(postsolve.phase_amount_total_norm <= criteria.phase_amount_total_tolerance)
    ) {
        reason = "phase_amount_total";
    } else if (
        criteria.fixed_composition_required
        && !(postsolve.fixed_composition_norm <= criteria.fixed_composition_tolerance)
    ) {
        reason = "fixed_composition";
    } else if (!(postsolve.material_balance_norm <= criteria.material_tolerance)) {
        reason = "material_balance";
    } else if (!(postsolve.pressure_consistency_norm <= criteria.pressure_tolerance)) {
        reason = "pressure_consistency";
    } else if (!(postsolve.chemical_potential_consistency_norm <= chemical_tolerance)) {
        reason = "chemical_potential_consistency";
    } else if (
        criteria.ln_fugacity_consistency_required
        && !(postsolve.ln_fugacity_consistency_norm <= chemical_tolerance)
    ) {
        reason = "ln_fugacity_consistency";
    } else if (
        criteria.phase_distance_required
        && !(criteria.phase_distance_strictly_greater
            ? postsolve.phase_distance > criteria.phase_distance_tolerance
            : postsolve.phase_distance >= criteria.phase_distance_tolerance)
    ) {
        reason = "phase_distance";
    } else if (criteria.stability_certification_unsupported) {
        postsolve.phase_set_status = "neutral_tpd_not_valid_for_charged_system";
        reason = "stability_tpd";
    } else if (criteria.stability_certification_required && !postsolve.stability_checked) {
        reason = "candidate_completeness";
    } else if (criteria.stability_certification_required && !postsolve.stability_accepted) {
        reason = "stability_tpd";
    } else if (
        criteria.stability_certification_required
        && (!postsolve.candidate_completeness_accepted || !postsolve.phase_set_mass_balance_feasible)
    ) {
        reason = "candidate_completeness";
    }

    postsolve.accepted = reason.empty();
    postsolve.rejection_reason = reason.empty() ? "accepted" : reason;
}

void reject_neutral_postsolve(NeutralTwoPhaseEosPostsolve& postsolve, const std::string& reason) {
    postsolve.accepted = false;
    postsolve.rejection_reason = reason;
}

void certify_electrolyte_postsolve(ElectrolytePostsolveCertificationResult& result) {
    result.phase_discovery_status = result.stage_iii_refinement.phase_discovery_status;
    result.stage_iii_refinement_status = result.stage_iii_refinement.stage_iii_refinement_status;
    result.explicit_ion_reconstruction_accepted =
        result.feed_reconstruction_inf_norm <= result.feed_reconstruction_tolerance
        && result.component_nonnegativity_margin >= 0.0;
    result.charge_balance_accepted =
        !result.phase_charge_residuals.empty()
        && result.max_phase_charge_residual <= result.phase_charge_tolerance
        && result.total_charge_residual <= result.total_charge_tolerance;
    result.transfer_residuals_accepted =
        !result.neutral_species_labels.empty()
        && !result.mean_ionic_pair_labels.empty()
        && result.neutral_transfer_max_abs_residual <= result.neutral_transfer_tolerance
        && result.mean_ionic_transfer_max_abs_residual <= result.mean_ionic_transfer_tolerance;
    result.pressure_consistency_accepted =
        result.pressure_consistency_norm <= result.pressure_tolerance;
    const bool composition_sums_accepted = std::all_of(
        result.composition_sum_residuals.begin(),
        result.composition_sum_residuals.end(),
        [&result](double residual) { return residual <= result.composition_sum_tolerance; }
    );
    result.phase_set_accepted =
        result.phase_count >= 2
        && !result.phase_amount_totals.empty()
        && result.phase_fraction_sum_residual <= result.phase_fraction_sum_tolerance
        && composition_sums_accepted;
    result.domain_margins_accepted =
        result.minimum_component_mole_fraction >= 0.0
        && result.minimum_phase_amount > 0.0
        && result.phase_distance > result.phase_distance_tolerance;

    const bool accepted =
        result.phase_discovery_status == "complete"
        && result.stage_iii_refinement.status == "complete"
        && result.stage_iii_refinement.route_result.postsolve.accepted
        && result.explicit_ion_reconstruction_accepted
        && result.charge_balance_accepted
        && result.transfer_residuals_accepted
        && result.pressure_consistency_accepted
        && result.phase_set_accepted
        && result.domain_margins_accepted;
    result.status = accepted ? "complete" : "incomplete";
    result.postsolve_certification_status = accepted ? "complete" : "incomplete";
}

int neutral_route_quality(const NeutralTwoPhaseEosRouteResult& result) {
    if (result.accepted) {
        return 3;
    }
    if (result.solver_accepted) {
        return 2;
    }
    if (result.ran) {
        return 1;
    }
    return 0;
}

bool neutral_route_strict_ipopt_success(const NeutralTwoPhaseEosRouteResult& result) {
    return result.accepted
        && result.solver_status == "success"
        && result.application_status == "solve_succeeded";
}

int neutral_boundary_route_quality(const NeutralTwoPhaseEosRouteResult& result) {
    if (neutral_route_strict_ipopt_success(result)) {
        return 4;
    }
    return neutral_route_quality(result);
}

RouteSeedAttempt neutral_seed_attempt_from_result(const NeutralTwoPhaseEosRouteResult& result) {
    RouteSeedAttempt out;
    out.seed_name = result.seed_name;
    out.status = result.status;
    out.solver_status = result.solver_status;
    out.application_status = result.application_status;
    out.solver_accepted = result.solver_accepted;
    out.accepted = result.accepted;
    out.stable = result.postsolve.stability_accepted;
    out.max_iterations = result.max_iterations;
    out.iteration_count = result.iteration_count;
    out.objective = result.objective;
    out.phase_distance = result.postsolve.phase_distance;
    out.material_balance_norm = result.postsolve.material_balance_norm;
    out.charge_balance_norm = result.postsolve.charge_balance_norm;
    out.pressure_consistency_norm = result.postsolve.pressure_consistency_norm;
    out.chemical_potential_consistency_norm = result.postsolve.chemical_potential_consistency_norm;
    out.phase_equilibrium_norm = result.postsolve.ln_fugacity_consistency_norm;
    out.min_tpd = result.postsolve.min_tpd;
    return out;
}

RoutePhysicalEvidence build_neutral_route_physical_evidence(const NeutralTwoPhaseEosRouteResult& result) {
    const NeutralTwoPhaseEosPostsolve& postsolve = result.postsolve;
    RoutePhysicalEvidence out;
    out.available = result.ran || !result.status.empty() || postsolve.phase_count > 0;
    out.phase_count = postsolve.phase_count;
    out.species_count = postsolve.species_count;
    out.phase_labels = result.phase_labels;
    out.phase_roles = result.phase_roles;
    out.material_balance_norm = postsolve.material_balance_norm;
    out.pressure_consistency_norm = postsolve.pressure_consistency_norm;
    out.chemical_potential_consistency_norm = postsolve.chemical_potential_consistency_norm;
    out.ln_fugacity_consistency_norm = postsolve.ln_fugacity_consistency_norm;
    out.charge_balance_norm = postsolve.charge_balance_norm;
    out.fixed_composition_norm = postsolve.fixed_composition_norm;
    out.phase_amount_total_norm = postsolve.phase_amount_total_norm;
    out.phase_distance = postsolve.phase_distance;
    out.minimum_phase_fraction = postsolve.minimum_phase_fraction;
    out.min_tpd = postsolve.min_tpd;
    out.candidate_mass_balance_norm = postsolve.candidate_mass_balance_norm;
    out.phase_discovery_backend = postsolve.phase_discovery_backend;
    out.stability_certificate = postsolve.stability_certificate;
    out.phase_set_status = postsolve.phase_set_status;
    out.stability_checked = postsolve.stability_checked;
    out.stability_accepted = postsolve.stability_accepted;
    out.candidate_completeness_accepted = postsolve.candidate_completeness_accepted;
    out.deterministic_screening_is_full_held = postsolve.deterministic_screening_is_full_held;
    out.deterministic_screening_status = postsolve.deterministic_screening_status;
    out.continuous_tpd_status = postsolve.continuous_tpd_status;
    out.held_stage_i_status = postsolve.held_stage_i_status;
    out.held_stage_ii_status = postsolve.held_stage_ii_status;
    out.held_stage_ii_candidate_bound_audit_status = postsolve.held_stage_ii_candidate_bound_audit_status;
    out.held_stage_ii_dual_loop_status = postsolve.held_stage_ii_dual_loop_status;
    out.held_stage_ii_major_iterations = postsolve.held_stage_ii_major_iterations;
    out.held_stage_ii_candidate_count = postsolve.held_stage_ii_candidate_count;
    out.held_stage_ii_lower_bound = postsolve.held_stage_ii_lower_bound;
    out.held_stage_ii_upper_bound = postsolve.held_stage_ii_upper_bound;
    out.held_stage_ii_bound_gap = postsolve.held_stage_ii_bound_gap;
    out.held_stage_ii_bound_tolerance = postsolve.held_stage_ii_bound_tolerance;
    out.held_stage_ii_stopping_reason = postsolve.held_stage_ii_stopping_reason;
    out.held_stage_ii_lower_bound_history = postsolve.held_stage_ii_lower_bound_history;
    out.held_stage_ii_upper_bound_history = postsolve.held_stage_ii_upper_bound_history;
    out.held_stage_ii_bound_gap_history = postsolve.held_stage_ii_bound_gap_history;
    out.held_stage_ii_replay_ready = postsolve.held_stage_ii_replay_ready;
    out.held_stage_ii_replay_source = postsolve.held_stage_ii_replay_source;
    out.held_stage_ii_replay_seed_name = postsolve.held_stage_ii_replay_seed_name;
    out.held_stage_ii_replay_candidate_count = postsolve.held_stage_ii_replay_candidate_count;
    out.held_stage_ii_replay_candidate_ranks = postsolve.held_stage_ii_replay_candidate_ranks;
    out.held_stage_ii_replay_phase_fractions = postsolve.held_stage_ii_replay_phase_fractions;
    out.held_stage_ii_replay_phase_kinds = postsolve.held_stage_ii_replay_phase_kinds;
    out.held_stage_ii_replay_phase_compositions = postsolve.held_stage_ii_replay_phase_compositions;
    out.held_stage_ii_rejected_candidate_count = postsolve.held_stage_ii_rejected_candidate_count;
    out.held_stage_ii_rejected_candidate_ranks = postsolve.held_stage_ii_rejected_candidate_ranks;
    out.held_stage_ii_rejected_candidate_reasons = postsolve.held_stage_ii_rejected_candidate_reasons;
    out.held_stage_iii_status = postsolve.held_stage_iii_status;
    out.held_stage_iii_consumed_stage_ii_replay_metadata =
        postsolve.held_stage_iii_consumed_stage_ii_replay_metadata;
    out.held_stage_iii_replay_source = postsolve.held_stage_iii_replay_source;
    out.held_stage_iii_replay_seed_name = postsolve.held_stage_iii_replay_seed_name;
    out.held_stage_iii_replay_candidate_count = postsolve.held_stage_iii_replay_candidate_count;
    out.tpd_candidate_count = postsolve.tpd_candidate_count;
    out.unique_candidate_count = postsolve.unique_candidate_count;
    out.selected_candidate_count = postsolve.selected_candidate_count;
    out.tpd_candidate_values = postsolve.tpd_candidate_values;
    out.tpd_candidate_sources = postsolve.tpd_candidate_sources;
    out.tpd_candidate_phase_kinds = postsolve.tpd_candidate_phase_kinds;
    out.tpd_candidate_compositions = postsolve.tpd_candidate_compositions;

    const std::size_t phase_count = route_evidence_phase_count(result);
    if (out.phase_count == 0 && phase_count > 0) {
        out.phase_count = static_cast<int>(phase_count);
    }
    if (out.phase_labels.empty()) {
        out.phase_labels.reserve(phase_count);
        for (std::size_t index = 0; index < phase_count; ++index) {
            out.phase_labels.push_back(default_phase_label(index));
        }
    }
    if (out.phase_roles.empty()) {
        out.phase_roles.reserve(phase_count);
        for (std::size_t index = 0; index < phase_count; ++index) {
            out.phase_roles.push_back(default_phase_role(postsolve.selected_phase_kinds, index));
        }
    }

    out.phases.reserve(phase_count);
    const double total_amount = std::accumulate(
        postsolve.phase_amount_totals.begin(),
        postsolve.phase_amount_totals.end(),
        0.0
    );
    for (std::size_t index = 0; index < phase_count; ++index) {
        RoutePhaseEvidence phase;
        phase.label = index < out.phase_labels.size() ? out.phase_labels[index] : default_phase_label(index);
        phase.role = index < out.phase_roles.size()
            ? out.phase_roles[index]
            : default_phase_role(postsolve.selected_phase_kinds, index);
        phase.phase_kind = indexed_or_zero(postsolve.selected_phase_kinds, index);
        phase.amount_total = indexed_or_zero(postsolve.phase_amount_totals, index);
        phase.volume = indexed_or_zero(postsolve.phase_volumes, index);
        phase.density = indexed_or_zero(postsolve.phase_densities, index);
        phase.phase_fraction = index < postsolve.selected_phase_fractions.size()
            ? postsolve.selected_phase_fractions[index]
            : (total_amount > 0.0 ? phase.amount_total / total_amount : 0.0);
        phase.composition = indexed_or_empty(postsolve.phase_compositions, index);
        phase.ln_fugacity_coefficients =
            indexed_or_empty(postsolve.phase_ln_fugacity_coefficients, index);
        out.phases.push_back(std::move(phase));
    }
    return out;
}

}  // namespace epcsaft::native::equilibrium_nlp
