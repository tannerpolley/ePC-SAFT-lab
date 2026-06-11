#include "equilibrium/results/result_builder.h"

#include "equilibrium/blocks/eos_phase_block.h"
#include "equilibrium/core/route_metadata.h"
#include "eos/core_internal.h"

#include <algorithm>
#include <cmath>
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

void require_positive_finite(double value, const std::string& label) {
    if (std::isfinite(value) && value > 0.0) {
        return;
    }
    throw ValueError(label + " must be positive and finite.");
}

std::vector<double> ln_fugacity_coefficients_for_block(
    const add_args& args,
    const EosPhaseBlockResult& block
) {
    FugacityContributionResult fugacity = fugacity_coefficient_result_cpp(
        block.temperature,
        block.density,
        block.composition,
        args
    );
    if (fugacity.lnfugcoef.total.size() != block.composition.size()) {
        throw ValueError("Neutral EOS result-builder fugacity payload size did not match composition.");
    }
    return fugacity.lnfugcoef.total;
}

std::vector<double> exp_values(const std::vector<double>& values) {
    std::vector<double> out;
    out.reserve(values.size());
    for (double value : values) {
        out.push_back(std::exp(value));
    }
    return out;
}

NeutralTwoPhaseEosPhasePayload phase_payload(
    const add_args& args,
    const EosPhaseBlockResult& block,
    std::size_t phase_index,
    double total_amount
) {
    require_positive_finite(total_amount, "Neutral EOS result-builder total amount");
    NeutralTwoPhaseEosPhasePayload out;
    out.label = "phase_" + std::to_string(phase_index);
    out.composition = block.composition;
    out.ln_fugacity_coefficient = ln_fugacity_coefficients_for_block(args, block);
    out.fugacity_coefficient = exp_values(out.ln_fugacity_coefficient);
    out.density = block.density;
    out.temperature = block.temperature;
    out.pressure = block.target_pressure;
    out.phase_fraction = block.total_amount / total_amount;
    out.amount_total = block.total_amount;
    out.volume = block.volume;
    out.eos_pressure = block.eos_pressure;
    out.pressure_consistency_residual = block.pressure_consistency_residual;
    out.compressibility_factor = block.compressibility_factor;
    return out;
}

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

bool apply_neutral_route_solve_result(NeutralTwoPhaseEosRouteResult& out, const IpoptSolveResult& solve) {
    out.ran = solve.solver_ran;
    out.solver_accepted = ipopt_solve_result_allows_postsolve(solve);
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

NeutralTwoPhaseEosResultPayload build_neutral_two_phase_eos_result(
    const add_args& args,
    double temperature,
    double target_pressure,
    const std::vector<std::vector<double>>& phase_amounts,
    const std::vector<double>& volumes,
    const std::vector<double>& feed_amounts,
    double material_tolerance,
    double pressure_tolerance,
    double chemical_potential_tolerance,
    double phase_distance_tolerance,
    bool phase_distance_constraint
) {
    NeutralTwoPhaseEosPostsolve postsolve = evaluate_neutral_two_phase_eos_postsolve(
        args,
        temperature,
        target_pressure,
        phase_amounts,
        volumes,
        feed_amounts,
        material_tolerance,
        pressure_tolerance,
        chemical_potential_tolerance,
        phase_distance_tolerance,
        {},
        phase_distance_constraint,
        false,
        {},
        false,
        phase_distance_constraint
    );
    NeutralTwoPhaseEosResultPayload out;
    out.accepted = postsolve.accepted;
    out.split_detected = postsolve.accepted;
    out.derivative_backend = postsolve.derivative_backend;
    out.rejection_reason = postsolve.rejection_reason;
    out.objective = postsolve.objective;
    out.material_balance_norm = postsolve.material_balance_norm;
    out.pressure_consistency_norm = postsolve.pressure_consistency_norm;
    out.chemical_potential_consistency_norm = postsolve.chemical_potential_consistency_norm;
    out.ln_fugacity_consistency_norm = postsolve.ln_fugacity_consistency_norm;
    out.phase_distance = postsolve.phase_distance;
    out.feed_amounts = feed_amounts;
    out.constraints = postsolve.constraints;

    if (!postsolve.accepted) {
        return out;
    }
    const EosPhaseSystemResult system = evaluate_eos_phase_system(
        args,
        temperature,
        target_pressure,
        phase_amounts,
        volumes,
        feed_amounts,
        {}
    );
    if (system.phase_count != 2 || system.phase_blocks.size() != 2) {
        throw ValueError("Neutral EOS result-builder currently requires exactly two phase blocks.");
    }
    const double total_amount = std::accumulate(
        postsolve.phase_amount_totals.begin(),
        postsolve.phase_amount_totals.end(),
        0.0
    );
    out.phases.reserve(system.phase_blocks.size());
    for (std::size_t index = 0; index < system.phase_blocks.size(); ++index) {
        out.phases.push_back(phase_payload(args, system.phase_blocks[index], index, total_amount));
    }
    return out;
}

}  // namespace epcsaft::native::equilibrium_nlp
