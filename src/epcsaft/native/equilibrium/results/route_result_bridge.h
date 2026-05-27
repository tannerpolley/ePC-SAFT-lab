#pragma once

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

namespace epcsaft::native::equilibrium_nlp::route_result_bridge {

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

}  // namespace epcsaft::native::equilibrium_nlp::route_result_bridge
