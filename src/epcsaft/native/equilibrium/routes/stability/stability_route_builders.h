#pragma once

#include "equilibrium/solvers/ipopt_adapter.h"

#include <string>
#include <vector>

struct add_args;

namespace epcsaft::native::equilibrium_nlp {

struct StabilityNlpContract {
    std::string problem_name;
    std::string derivative_backend;
    std::string variable_model;
    std::string density_backend;
    int species_count = 0;
    int variable_count = 0;
    int constraint_count = 0;
    int jacobian_nonzero_count = 0;
    int balance_row_count = 0;
    int reaction_count = 0;
    std::string parent_phase;
    std::string trial_phase;
    std::vector<std::string> residual_families;
    std::vector<std::string> constraint_families;
    std::vector<double> feed_composition;
    std::vector<double> parent_reduced_potential;
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
};

struct StabilityRouteResult {
    bool compiled = false;
    bool adapter_available = false;
    bool ran = false;
    bool solver_accepted = false;
    bool accepted = false;
    bool stable = false;
    bool exact_gradient_required = true;
    bool exact_jacobian_required = true;
    std::string backend = "ipopt";
    std::string adapter_kind = "native_tnlp_adapter";
    std::string problem_name = "neutral_stability_tpd";
    std::string derivative_backend = "cppad_implicit";
    std::string variable_model = "composition_plus_log_density";
    std::string density_backend = "explicit_log_density_pressure_constraint";
    std::vector<std::string> residual_families;
    std::vector<std::string> constraint_families;
    std::string gradient_approximation = "exact";
    std::string jacobian_approximation = "exact";
    std::string hessian_approximation = "unknown";
    std::string hessian_backend = "unknown";
    std::string scaling_method = "user-scaling";
    std::string linear_solver_requested = "auto";
    std::string linear_solver_selected = "default";
    std::string initial_point_strategy = "single_seed";
    std::string status;
    std::string solver_status;
    std::string application_status;
    std::string last_callback_exception;
    std::string last_callback_failure;
    std::string parent_phase;
    std::string trial_phase;
    std::string seed_name = "canonical_shifted_feed";
    int balance_row_count = 0;
    int reaction_count = 0;
    int iteration_count = 0;
    int iteration_history_limit = 0;
    int iteration_history_size = 0;
    int variable_scaling_count = 0;
    int constraint_scaling_count = 0;
    int eval_h_calls = 0;
    double objective_scaling = 1.0;
    double acceptable_tolerance = 0.0;
    double constraint_violation_tolerance = 0.0;
    double dual_infeasibility_tolerance = 0.0;
    double complementarity_tolerance = 0.0;
    double variable_scaling_min = 0.0;
    double variable_scaling_max = 0.0;
    double constraint_scaling_min = 0.0;
    double constraint_scaling_max = 0.0;
    bool exact_hessian_available = false;
    bool warm_start_requested = false;
    bool warm_start_used = false;
    double objective = 0.0;
    double min_tpd = 0.0;
    double conserved_balance_norm = 0.0;
    double charge_balance_norm = 0.0;
    double reaction_stationarity_norm = 0.0;
    std::vector<double> variables;
    std::vector<double> constraints;
    std::vector<double> reaction_residuals;
    std::vector<double> conserved_balance_residuals;
    std::vector<double> bound_lower_multipliers;
    std::vector<double> bound_upper_multipliers;
    std::vector<double> constraint_multipliers;
    std::vector<IpoptIterationRecord> iteration_history;
    std::vector<RouteSeedAttempt> seed_attempts;
    std::vector<double> trial_composition;
    std::vector<double> initial_composition;
    std::vector<double> parent_reduced_potential;
};

StabilityNlpContract evaluate_neutral_stability_tpd_nlp_contract(
    const add_args& args,
    double temperature,
    double pressure,
    const std::vector<double>& feed_composition,
    int parent_phase,
    int trial_phase
);

StabilityNlpContract evaluate_electrolyte_stability_tpd_nlp_contract(
    const add_args& args,
    double temperature,
    double pressure,
    const std::vector<double>& feed_composition
);

StabilityNlpContract evaluate_reactive_stability_tpd_nlp_contract(
    const add_args& args,
    double temperature,
    double pressure,
    const std::vector<double>& feed_composition,
    int balance_rows,
    const std::vector<double>& balance_matrix_row_major,
    const std::vector<double>& total_vector,
    int reaction_rows,
    const std::vector<double>& reaction_stoichiometry_row_major,
    const std::vector<double>& log_equilibrium_constants,
    int parent_phase,
    int trial_phase
);

StabilityRouteResult solve_neutral_stability_tpd_route(
    const add_args& args,
    double temperature,
    double pressure,
    const std::vector<double>& feed_composition,
    int parent_phase,
    int trial_phase,
    const IpoptSolveOptions& options,
    double stability_tolerance,
    const std::vector<double>& trial_initial_composition = {}
);

StabilityRouteResult solve_electrolyte_stability_tpd_route(
    const add_args& args,
    double temperature,
    double pressure,
    const std::vector<double>& feed_composition,
    const IpoptSolveOptions& options,
    double stability_tolerance,
    const std::vector<double>& trial_initial_composition = {}
);

StabilityRouteResult solve_reactive_stability_tpd_route(
    const add_args& args,
    double temperature,
    double pressure,
    const std::vector<double>& feed_composition,
    int balance_rows,
    const std::vector<double>& balance_matrix_row_major,
    const std::vector<double>& total_vector,
    int reaction_rows,
    const std::vector<double>& reaction_stoichiometry_row_major,
    const std::vector<double>& log_equilibrium_constants,
    int parent_phase,
    int trial_phase,
    const IpoptSolveOptions& options,
    double stability_tolerance,
    const std::vector<double>& trial_initial_composition = {}
);

}  // namespace epcsaft::native::equilibrium_nlp
