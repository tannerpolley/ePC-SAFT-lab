#pragma once

#include "equilibrium/core/nlp_problem.h"
#include "equilibrium/solvers/ipopt_adapter.h"

#include <memory>
#include <string>
#include <vector>

struct add_args;

namespace epcsaft::native::equilibrium {
struct ActivationPlan;
struct VariableLayout;
}  // namespace epcsaft::native::equilibrium

namespace epcsaft::native::equilibrium_nlp {

struct NeutralTwoPhaseEosNlpContract {
    std::string problem_name;
    std::string derivative_backend;
    std::string activation_compiler;
    std::string variable_model;
    std::string density_backend;
    std::vector<std::string> residual_families;
    std::vector<std::string> constraint_families;
    int phase_count = 0;
    int species_count = 0;
    int balance_row_count = 0;
    int reaction_count = 0;
    int variable_count = 0;
    int constraint_count = 0;
    int jacobian_nonzero_count = 0;
    bool exact_hessian_available = false;
    int hessian_nonzero_count = 0;
    std::string hessian_backend;
    std::vector<double> standard_mu_rt;
    std::vector<double> initial_point;
    std::vector<double> variable_lower_bounds;
    std::vector<double> variable_upper_bounds;
    std::vector<double> constraint_lower_bounds;
    std::vector<double> constraint_upper_bounds;
    double objective_at_initial = 0.0;
    std::vector<double> gradient_at_initial;
    std::vector<double> constraints_at_initial;
    std::vector<int> jacobian_rows;
    std::vector<int> jacobian_cols;
    std::vector<double> jacobian_values_at_initial;
    std::vector<int> hessian_rows;
    std::vector<int> hessian_cols;
    std::vector<double> hessian_values_at_initial;
    double objective_scaling = 1.0;
    std::vector<double> variable_scaling;
    std::vector<double> constraint_scaling;
    double initial_variable_lower_margin = 0.0;
    double initial_variable_upper_margin = 0.0;
    double initial_variable_bound_margin = 0.0;
    double initial_amount_lower_margin = 0.0;
    double initial_volume_lower_margin = 0.0;
    double initial_constraint_bound_violation = 0.0;
    std::string domain_safety_policy = "explicit_bounds_variable_transform_ipopt_barrier";
    std::string transform_policy = "identity_physical_coordinates";
    std::string transform_backend = "analytic_identity";
    int transform_input_variable_count = 0;
    int transform_output_variable_count = 0;
    int transform_jacobian_value_count = 0;
    int transform_hessian_value_count = 0;
    std::string barrier_policy = "ipopt_internal_barrier_for_declared_bounds";
};

struct NeutralTwoPhaseEosPostsolve {
    bool accepted = false;
    bool stability_checked = false;
    bool stability_accepted = false;
    bool candidate_completeness_accepted = false;
    bool phase_set_mass_balance_feasible = false;
    std::string rejection_reason;
    std::string phase_discovery_backend = "not_checked";
    std::string stability_certificate = "not_checked";
    std::string phase_set_status = "not_checked";
    std::vector<std::string> stage9_phase_discovery_steps;
    std::string deterministic_screening_status = "pending";
    bool deterministic_screening_is_full_held = false;
    std::string continuous_tpd_status = "pending";
    std::string continuous_tpd_backend;
    std::string continuous_tpd_best_source;
    int deterministic_candidate_count = 0;
    int continuous_tpd_start_count = 0;
    int continuous_tpd_solve_count = 0;
    int continuous_tpd_converged_count = 0;
    int continuous_tpd_iteration_count_total = 0;
    int continuous_tpd_iteration_count_max = 0;
    double continuous_tpd_min = 0.0;
    double continuous_tpd_step_final_max = 0.0;
    int continuous_tpd_best_phase_kind = 0;
    double continuous_tpd_best_density = 0.0;
    double continuous_tpd_best_molar_volume = 0.0;
    std::vector<double> continuous_tpd_best_composition;
    std::string held_stage_i_status = "pending";
    int held_stage_i_start_count = 0;
    bool held_stage_i_negative_tpd_found = false;
    double held_stage_i_min_tpd = 0.0;
    std::string held_stage_ii_status = "pending";
    std::string held_stage_ii_candidate_bound_audit_status = "pending";
    std::string held_stage_ii_dual_loop_status = "pending";
    int held_stage_ii_major_iterations = 0;
    int held_stage_ii_candidate_count = 0;
    double held_stage_ii_lower_bound = 0.0;
    double held_stage_ii_upper_bound = 0.0;
    double held_stage_ii_bound_gap = 0.0;
    double held_stage_ii_bound_tolerance = 0.0;
    std::string held_stage_ii_stopping_reason;
    std::vector<double> held_stage_ii_lower_bound_history;
    std::vector<double> held_stage_ii_upper_bound_history;
    std::vector<double> held_stage_ii_bound_gap_history;
    bool held_stage_ii_replay_ready = false;
    std::string held_stage_ii_replay_source;
    std::string held_stage_ii_replay_seed_name;
    int held_stage_ii_replay_candidate_count = 0;
    std::vector<int> held_stage_ii_replay_candidate_ranks;
    std::vector<double> held_stage_ii_replay_phase_fractions;
    std::vector<int> held_stage_ii_replay_phase_kinds;
    std::vector<std::vector<double>> held_stage_ii_replay_phase_compositions;
    int held_stage_ii_rejected_candidate_count = 0;
    std::vector<int> held_stage_ii_rejected_candidate_ranks;
    std::vector<std::string> held_stage_ii_rejected_candidate_reasons;
    std::string held_stage_iii_status = "pending";
    int held_stage_iii_refined_phase_count = 0;
    bool held_stage_iii_consumed_stage_ii_replay_metadata = false;
    std::string held_stage_iii_replay_source;
    std::string held_stage_iii_replay_seed_name;
    int held_stage_iii_replay_candidate_count = 0;
    std::string derivative_backend;
    std::vector<std::string> residual_families;
    std::vector<std::string> constraint_families;
    int phase_count = 0;
    int species_count = 0;
    int tpd_candidate_count = 0;
    int unique_candidate_count = 0;
    int selected_candidate_count = 0;
    double material_balance_norm = 0.0;
    double pressure_consistency_norm = 0.0;
    double chemical_potential_consistency_norm = 0.0;
    double ln_fugacity_consistency_norm = 0.0;
    double charge_balance_norm = 0.0;
    double fixed_composition_norm = 0.0;
    double phase_amount_total_norm = 0.0;
    double phase_distance = 0.0;
    double min_tpd = 0.0;
    double candidate_mass_balance_norm = 0.0;
    double objective = 0.0;
    double gibbs_feed = 0.0;
    double gibbs_split = 0.0;
    double gibbs_delta = 0.0;
    double minimum_phase_fraction = 0.0;
    std::string density_backend;
    std::vector<double> constraints;
    std::vector<double> phase_amount_totals;
    std::vector<double> phase_volumes;
    std::vector<double> phase_densities;
    std::vector<std::vector<double>> phase_compositions;
    std::vector<std::vector<double>> phase_ln_fugacity_coefficients;
    std::vector<double> selected_phase_fractions;
    std::vector<int> selected_phase_kinds;
    std::vector<std::vector<double>> selected_phase_compositions;
    std::vector<double> tpd_candidate_values;
    std::vector<std::string> tpd_candidate_sources;
    std::vector<int> tpd_candidate_phase_kinds;
    std::vector<std::vector<double>> tpd_candidate_compositions;
    std::vector<double> tpd_candidate_pressure_residuals;
    std::vector<int> tpd_candidate_iteration_counts;
    std::vector<double> tpd_candidate_step_finals;
    std::vector<int> tpd_candidate_ranks;
    std::vector<std::string> tpd_candidate_feasibility_statuses;
    std::vector<bool> tpd_candidate_selected;
};

struct NeutralTpdCandidate {
    bool valid = false;
    std::string source;
    int phase_kind = 0;
    std::vector<double> composition;
    double density = 0.0;
    double molar_volume = 0.0;
    double tpd = 0.0;
    double transformed_objective = 0.0;
    double pressure_residual_estimate = 0.0;
    std::string tpd_backend = "deterministic_grid_evaluation";
    std::string tpd_status = "candidate_generated";
    std::string start_source;
    int tpd_iteration_count = 0;
    double tpd_step_final = 0.0;
    std::string feasibility_status = "candidate_generated";
    int candidate_rank = -1;
    bool selected = false;
};

struct NeutralPhaseDiscoveryResult {
    bool stability_checked = false;
    bool stability_accepted = false;
    bool candidate_completeness_accepted = false;
    bool phase_set_mass_balance_feasible = false;
    std::string phase_discovery_backend = "deterministic_tpd_candidate_screening";
    std::string stability_certificate = "tpd_postsolve";
    std::string phase_set_status = "not_checked";
    std::vector<std::string> stage9_phase_discovery_steps;
    std::string deterministic_screening_status = "pending";
    bool deterministic_screening_is_full_held = false;
    std::string continuous_tpd_status = "pending";
    std::string continuous_tpd_backend;
    std::string continuous_tpd_best_source;
    int deterministic_candidate_count = 0;
    int continuous_tpd_start_count = 0;
    int continuous_tpd_solve_count = 0;
    int continuous_tpd_converged_count = 0;
    int continuous_tpd_iteration_count_total = 0;
    int continuous_tpd_iteration_count_max = 0;
    double continuous_tpd_min = 0.0;
    double continuous_tpd_step_final_max = 0.0;
    int continuous_tpd_best_phase_kind = 0;
    double continuous_tpd_best_density = 0.0;
    double continuous_tpd_best_molar_volume = 0.0;
    std::vector<double> continuous_tpd_best_composition;
    std::string held_stage_i_status = "pending";
    int held_stage_i_start_count = 0;
    bool held_stage_i_negative_tpd_found = false;
    double held_stage_i_min_tpd = 0.0;
    std::string held_stage_ii_status = "pending";
    std::string held_stage_ii_candidate_bound_audit_status = "pending";
    std::string held_stage_ii_dual_loop_status = "pending";
    int held_stage_ii_major_iterations = 0;
    int held_stage_ii_candidate_count = 0;
    double held_stage_ii_lower_bound = 0.0;
    double held_stage_ii_upper_bound = 0.0;
    double held_stage_ii_bound_gap = 0.0;
    double held_stage_ii_bound_tolerance = 0.0;
    std::string held_stage_ii_stopping_reason;
    std::vector<double> held_stage_ii_lower_bound_history;
    std::vector<double> held_stage_ii_upper_bound_history;
    std::vector<double> held_stage_ii_bound_gap_history;
    bool held_stage_ii_replay_ready = false;
    std::string held_stage_ii_replay_source;
    std::string held_stage_ii_replay_seed_name;
    int held_stage_ii_replay_candidate_count = 0;
    std::vector<int> held_stage_ii_replay_candidate_ranks;
    std::vector<double> held_stage_ii_replay_phase_fractions;
    std::vector<int> held_stage_ii_replay_phase_kinds;
    std::vector<std::vector<double>> held_stage_ii_replay_phase_compositions;
    int held_stage_ii_rejected_candidate_count = 0;
    std::vector<int> held_stage_ii_rejected_candidate_ranks;
    std::vector<std::string> held_stage_ii_rejected_candidate_reasons;
    std::string held_stage_iii_status = "pending";
    int held_stage_iii_refined_phase_count = 0;
    double min_tpd = 0.0;
    double candidate_mass_balance_norm = 0.0;
    int tpd_candidate_count = 0;
    int unique_candidate_count = 0;
    int selected_candidate_count = 0;
    std::vector<double> selected_phase_fractions;
    std::vector<int> selected_phase_kinds;
    std::vector<std::vector<double>> selected_phase_compositions;
    std::vector<NeutralTpdCandidate> candidates;
};

struct RoutePhaseEvidence {
    std::string label;
    std::string role;
    int phase_kind = 0;
    double amount_total = 0.0;
    double volume = 0.0;
    double density = 0.0;
    double phase_fraction = 0.0;
    std::vector<double> composition;
    std::vector<double> ln_fugacity_coefficients;
};

struct RoutePhysicalEvidence {
    bool available = false;
    int phase_count = 0;
    int species_count = 0;
    std::vector<std::string> phase_labels;
    std::vector<std::string> phase_roles;
    double material_balance_norm = 0.0;
    double pressure_consistency_norm = 0.0;
    double chemical_potential_consistency_norm = 0.0;
    double ln_fugacity_consistency_norm = 0.0;
    double charge_balance_norm = 0.0;
    double fixed_composition_norm = 0.0;
    double phase_amount_total_norm = 0.0;
    double phase_distance = 0.0;
    double minimum_phase_fraction = 0.0;
    double min_tpd = 0.0;
    double candidate_mass_balance_norm = 0.0;
    std::string phase_discovery_backend;
    std::string stability_certificate;
    std::string phase_set_status;
    bool stability_checked = false;
    bool stability_accepted = false;
    bool candidate_completeness_accepted = false;
    bool deterministic_screening_is_full_held = false;
    std::string deterministic_screening_status;
    std::string continuous_tpd_status;
    std::string held_stage_i_status;
    std::string held_stage_ii_status;
    std::string held_stage_ii_candidate_bound_audit_status;
    std::string held_stage_ii_dual_loop_status;
    int held_stage_ii_major_iterations = 0;
    int held_stage_ii_candidate_count = 0;
    double held_stage_ii_lower_bound = 0.0;
    double held_stage_ii_upper_bound = 0.0;
    double held_stage_ii_bound_gap = 0.0;
    double held_stage_ii_bound_tolerance = 0.0;
    std::string held_stage_ii_stopping_reason;
    std::vector<double> held_stage_ii_lower_bound_history;
    std::vector<double> held_stage_ii_upper_bound_history;
    std::vector<double> held_stage_ii_bound_gap_history;
    bool held_stage_ii_replay_ready = false;
    std::string held_stage_ii_replay_source;
    std::string held_stage_ii_replay_seed_name;
    int held_stage_ii_replay_candidate_count = 0;
    std::vector<int> held_stage_ii_replay_candidate_ranks;
    std::vector<double> held_stage_ii_replay_phase_fractions;
    std::vector<int> held_stage_ii_replay_phase_kinds;
    std::vector<std::vector<double>> held_stage_ii_replay_phase_compositions;
    int held_stage_ii_rejected_candidate_count = 0;
    std::vector<int> held_stage_ii_rejected_candidate_ranks;
    std::vector<std::string> held_stage_ii_rejected_candidate_reasons;
    std::string held_stage_iii_status;
    bool held_stage_iii_consumed_stage_ii_replay_metadata = false;
    std::string held_stage_iii_replay_source;
    std::string held_stage_iii_replay_seed_name;
    int held_stage_iii_replay_candidate_count = 0;
    int tpd_candidate_count = 0;
    int unique_candidate_count = 0;
    int selected_candidate_count = 0;
    std::vector<double> tpd_candidate_values;
    std::vector<std::string> tpd_candidate_sources;
    std::vector<int> tpd_candidate_phase_kinds;
    std::vector<std::vector<double>> tpd_candidate_compositions;
    std::vector<RoutePhaseEvidence> phases;
};

struct NeutralTwoPhaseEosRouteResult {
    bool compiled = false;
    bool adapter_available = false;
    bool ran = false;
    bool solver_accepted = false;
    bool solver_feasible_point = false;
    bool postsolve_accepted = false;
    bool accepted = false;
    bool exact_gradient_required = true;
    bool exact_jacobian_required = true;
    std::string backend = "ipopt";
    std::string adapter_kind = "native_tnlp_adapter";
    std::string problem_name = "neutral_two_phase_eos";
    std::string derivative_backend = "analytic_cppad";
    std::string activation_compiler;
    std::string variable_model;
    std::string density_backend;
    std::vector<std::string> residual_families;
    std::vector<std::string> constraint_families;
    std::string gradient_approximation = "exact";
    std::string jacobian_approximation = "exact";
    std::string hessian_approximation = "unknown";
    std::string hessian_backend = "unknown";
    std::string option_profile = "proof";
    std::string solver_acceptance_policy;
    std::string exact_hessian_policy;
    std::string scaling_contract;
    std::string residual_scaling_policy;
    std::string linear_solver_policy;
    std::string barrier_policy;
    std::string scaling_method = "user-scaling";
    std::string linear_solver_requested = "auto";
    std::string linear_solver_selected = "default";
    std::string initial_point_strategy = "single_seed";
    std::string seed_name = "problem_initial_point";
    std::string status;
    std::string rejection_reason;
    std::string solver_status;
    std::string application_status;
    std::string last_callback_exception;
    std::string last_callback_failure;
    int print_level = 0;
    int max_iterations = 0;
    int acceptable_iteration_limit = 0;
    int iteration_count = 0;
    int iteration_history_limit = 0;
    int iteration_history_size = 0;
    int variable_scaling_count = 0;
    int constraint_scaling_count = 0;
    int eval_h_calls = 0;
    int active_lower_bound_count = 0;
    int active_upper_bound_count = 0;
    int active_variable_bound_count = 0;
    int step_trial_count_max = 0;
    double objective_scaling = 1.0;
    double acceptable_tolerance = 0.0;
    double constraint_violation_tolerance = 0.0;
    double ipopt_unscaled_constraint_violation_tolerance = 0.0;
    double dual_infeasibility_tolerance = 0.0;
    double complementarity_tolerance = 0.0;
    double bound_push = 0.0;
    double bound_frac = 0.0;
    double variable_scaling_min = 0.0;
    double variable_scaling_max = 0.0;
    double constraint_scaling_min = 0.0;
    double constraint_scaling_max = 0.0;
    double variable_scaling_ratio = 1.0;
    double constraint_scaling_ratio = 1.0;
    double scaled_constraint_violation_inf_norm = 0.0;
    double scaled_stationarity_inf_norm = 0.0;
    double scaled_complementarity_inf_norm = 0.0;
    double bound_complementarity_inf_norm = 0.0;
    double barrier_parameter_final = 0.0;
    double regularization_size_final = 0.0;
    double regularization_size_max = 0.0;
    bool exact_hessian_available = false;
    bool profile_exact_hessian_gate = true;
    bool variable_scaling_quality_passed = true;
    bool constraint_scaling_quality_passed = true;
    bool scaled_acceptance_passed = false;
    bool restoration_phase_observed = false;
    bool warm_start_requested = false;
    bool warm_start_used = false;
    double objective = 0.0;
    std::vector<double> variables;
    std::vector<double> constraints;
    std::vector<double> bound_lower_multipliers;
    std::vector<double> bound_upper_multipliers;
    std::vector<double> constraint_multipliers;
    std::vector<IpoptIterationRecord> iteration_history;
    std::vector<RouteSeedAttempt> seed_attempts;
    std::vector<std::vector<double>> phase_amounts;
    std::vector<double> phase_volumes;
    std::vector<std::string> phase_labels;
    std::vector<std::string> phase_roles;
    NeutralTwoPhaseEosPostsolve postsolve;
};

NeutralTwoPhaseEosNlpContract evaluate_neutral_two_phase_eos_nlp_contract(
    const add_args& args,
    double temperature,
    double target_pressure,
    const std::vector<std::vector<double>>& phase_amounts,
    const std::vector<double>& volumes,
    const std::vector<double>& feed_amounts
);

NeutralTwoPhaseEosNlpContract evaluate_neutral_multiphase_eos_nlp_contract(
    const add_args& args,
    double temperature,
    double target_pressure,
    const std::vector<std::vector<double>>& phase_amounts,
    const std::vector<double>& volumes,
    const std::vector<double>& feed_amounts
);

NeutralTwoPhaseEosNlpContract evaluate_neutral_bubble_p_eos_nlp_contract(
    const add_args& args,
    double temperature,
    const std::vector<double>& liquid_composition
);

NeutralTwoPhaseEosNlpContract evaluate_neutral_dew_p_eos_nlp_contract(
    const add_args& args,
    double temperature,
    const std::vector<double>& vapor_composition
);

NeutralTwoPhaseEosNlpContract evaluate_neutral_bubble_t_eos_nlp_contract(
    const add_args& args,
    double target_pressure,
    const std::vector<double>& liquid_composition
);

NeutralTwoPhaseEosNlpContract evaluate_neutral_dew_t_eos_nlp_contract(
    const add_args& args,
    double target_pressure,
    const std::vector<double>& vapor_composition
);

NeutralTwoPhaseEosNlpContract evaluate_neutral_tp_flash_eos_nlp_contract(
    const add_args& args,
    double temperature,
    double target_pressure,
    const std::vector<double>& feed_composition
);

NeutralTwoPhaseEosNlpContract evaluate_neutral_single_component_vle_nlp_contract(
    const add_args& args,
    double temperature
);

NeutralTwoPhaseEosNlpContract evaluate_activated_neutral_tp_flash_nlp_contract(
    const add_args& args,
    const epcsaft::native::equilibrium::ActivationPlan& plan,
    const epcsaft::native::equilibrium::VariableLayout& layout
);

NeutralTwoPhaseEosNlpContract evaluate_activated_neutral_lle_nlp_contract(
    const add_args& args,
    const epcsaft::native::equilibrium::ActivationPlan& plan,
    const epcsaft::native::equilibrium::VariableLayout& layout
);

std::unique_ptr<NlpProblem> make_neutral_tp_flash_eos_problem(
    const add_args& args,
    double temperature,
    double target_pressure,
    const std::vector<double>& feed_composition,
    const std::string& problem_name = "neutral_tp_flash_eos"
);

std::unique_ptr<NlpProblem> make_neutral_two_phase_eos_problem(
    const add_args& args,
    double temperature,
    double target_pressure,
    const std::vector<std::vector<double>>& phase_amounts,
    const std::vector<double>& volumes,
    const std::vector<double>& feed_amounts,
    const std::string& problem_name = "neutral_two_phase_eos",
    double minimum_phase_distance = 0.0
);

std::unique_ptr<NlpProblem> make_neutral_two_phase_eos_problem_from_feed(
    const add_args& args,
    double temperature,
    double target_pressure,
    const std::vector<double>& feed_composition,
    const std::vector<int>& phase_kinds,
    const std::string& problem_name = "neutral_two_phase_eos",
    double minimum_phase_distance = 0.0
);

IpoptSolveResult solve_neutral_two_phase_eos_ipopt(
    const add_args& args,
    double temperature,
    double target_pressure,
    const std::vector<std::vector<double>>& phase_amounts,
    const std::vector<double>& volumes,
    const std::vector<double>& feed_amounts,
    const IpoptSolveOptions& options,
    const std::vector<double>& charges = {},
    const std::string& problem_name = "neutral_two_phase_eos",
    double minimum_phase_distance = 0.0
);

NeutralTwoPhaseEosPostsolve evaluate_neutral_two_phase_eos_postsolve(
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
    const std::vector<double>& charges = {},
    bool phase_distance_constraint = false,
    bool stability_certification_required = false,
    std::vector<int> phase_kinds = {},
    bool continuous_tpd_required = false,
    bool ln_fugacity_consistency_required = true
);

NeutralTwoPhaseEosPostsolve evaluate_neutral_multiphase_eos_postsolve(
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
    const std::vector<int>& phase_kinds
);

NeutralPhaseDiscoveryResult evaluate_neutral_tpd_phase_discovery(
    const add_args& args,
    double temperature,
    double target_pressure,
    const std::vector<double>& feed_composition,
    const std::vector<int>& phase_kinds,
    double tpd_tolerance,
    double candidate_mass_balance_tolerance,
    bool continuous_tpd_required = true
);

NeutralPhaseDiscoveryResult evaluate_electrolyte_tpd_phase_discovery(
    const add_args& args,
    double temperature,
    double target_pressure,
    const std::vector<double>& feed_composition,
    const std::vector<double>& charges,
    const std::vector<int>& phase_kinds,
    double charge_tolerance,
    double tpd_tolerance,
    double candidate_mass_balance_tolerance
);

NeutralTwoPhaseEosRouteResult solve_neutral_two_phase_eos_route(
    const add_args& args,
    double temperature,
    double target_pressure,
    const std::vector<std::vector<double>>& phase_amounts,
    const std::vector<double>& volumes,
    const std::vector<double>& feed_amounts,
    const IpoptSolveOptions& options,
    double material_tolerance,
    double pressure_tolerance,
    double chemical_potential_tolerance,
    double phase_distance_tolerance,
    double minimum_phase_distance = 0.0,
    const std::vector<double>& charges = {},
    const std::string& problem_name = "neutral_two_phase_eos",
    double charge_tolerance = 0.0
);

NeutralTwoPhaseEosRouteResult solve_neutral_bubble_p_eos_route(
    const add_args& args,
    double temperature,
    const std::vector<double>& liquid_composition,
    const IpoptSolveOptions& options,
    double phase_total_tolerance,
    double pressure_tolerance,
    double chemical_potential_tolerance,
    double phase_distance_tolerance
);

NeutralTwoPhaseEosRouteResult solve_neutral_dew_p_eos_route(
    const add_args& args,
    double temperature,
    const std::vector<double>& vapor_composition,
    const IpoptSolveOptions& options,
    double phase_total_tolerance,
    double pressure_tolerance,
    double chemical_potential_tolerance,
    double phase_distance_tolerance
);

NeutralTwoPhaseEosRouteResult solve_neutral_bubble_t_eos_route(
    const add_args& args,
    double target_pressure,
    const std::vector<double>& liquid_composition,
    const IpoptSolveOptions& options,
    double phase_total_tolerance,
    double pressure_tolerance,
    double chemical_potential_tolerance,
    double phase_distance_tolerance
);

NeutralTwoPhaseEosRouteResult solve_neutral_dew_t_eos_route(
    const add_args& args,
    double target_pressure,
    const std::vector<double>& vapor_composition,
    const IpoptSolveOptions& options,
    double phase_total_tolerance,
    double pressure_tolerance,
    double chemical_potential_tolerance,
    double phase_distance_tolerance
);

NeutralTwoPhaseEosRouteResult solve_neutral_cloud_t_eos_route(
    const add_args& args,
    double target_pressure,
    const std::vector<double>& parent_liquid_composition,
    const IpoptSolveOptions& options,
    double phase_total_tolerance,
    double pressure_tolerance,
    double chemical_potential_tolerance,
    double phase_distance_tolerance
);

NeutralTwoPhaseEosRouteResult solve_neutral_tp_flash_eos_route(
    const add_args& args,
    double temperature,
    double target_pressure,
    const std::vector<double>& feed_composition,
    const IpoptSolveOptions& options,
    double material_tolerance,
    double pressure_tolerance,
    double chemical_potential_tolerance,
    double phase_distance_tolerance
);

NeutralTwoPhaseEosRouteResult solve_neutral_single_component_vle_route(
    const add_args& args,
    double temperature,
    const IpoptSolveOptions& options,
    double phase_total_tolerance,
    double pressure_tolerance,
    double chemical_potential_tolerance,
    double phase_distance_tolerance
);

NeutralTwoPhaseEosRouteResult solve_activated_neutral_tp_flash_eos_route(
    const add_args& args,
    double temperature,
    double target_pressure,
    const std::vector<double>& feed_composition,
    const IpoptSolveOptions& options,
    double material_tolerance,
    double pressure_tolerance,
    double chemical_potential_tolerance,
    double phase_distance_tolerance
);

NeutralTwoPhaseEosRouteResult solve_activated_neutral_lle_eos_route(
    const add_args& args,
    double temperature,
    double target_pressure,
    const std::vector<double>& feed_composition,
    const IpoptSolveOptions& options,
    double material_tolerance,
    double pressure_tolerance,
    double chemical_potential_tolerance,
    double phase_distance_tolerance
);

NeutralTwoPhaseEosRouteResult solve_neutral_multiphase_fugacity_residual_route(
    const add_args& args,
    double temperature,
    double target_pressure,
    const std::vector<double>& feed_composition,
    const std::vector<int>& phase_kinds,
    const IpoptSolveOptions& options,
    double material_tolerance,
    double pressure_tolerance,
    double ln_fugacity_tolerance,
    double phase_distance_tolerance
);

}  // namespace epcsaft::native::equilibrium_nlp
