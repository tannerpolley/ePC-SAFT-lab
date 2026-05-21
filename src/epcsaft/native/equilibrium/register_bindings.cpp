#include "bindings/equilibrium_bindings.h"

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include <cmath>
#include <memory>
#include <string>
#include <vector>

#include "equilibrium/blocks/association_block.h"
#include "equilibrium/blocks/electrolyte_block.h"
#include "equilibrium/blocks/eos_phase_block.h"
#include "equilibrium/blocks/gibbs_blocks.h"
#include "equilibrium/blocks/reaction_block.h"
#include "equilibrium/core/activation_matrix.h"
#include "equilibrium/core/second_order.h"
#include "equilibrium/core/selector_core.h"
#include "equilibrium/results/result_builder.h"
#include "equilibrium/results/route_result_bridge.h"
#include "equilibrium/solvers/ipopt_adapter.h"
#include "model/native_types.h"

namespace py = pybind11;

namespace {

using epcsaft::native::equilibrium_nlp::route_result_bridge::apply_eos_route_metadata_fields;
using epcsaft::native::equilibrium_nlp::route_result_bridge::apply_ipopt_route_solution_fields;
using epcsaft::native::equilibrium_nlp::route_result_bridge::apply_ipopt_route_status_fields;

std::string diagnostic_string_or(
    const epcsaft::native::equilibrium_nlp::IpoptSolveResult& result,
    const std::string& key,
    const std::string& default_value
) {
    const auto item = result.diagnostics_string.find(key);
    return item == result.diagnostics_string.end() ? default_value : item->second;
}

int diagnostic_int_or(
    const epcsaft::native::equilibrium_nlp::IpoptSolveResult& result,
    const std::string& key,
    int default_value
) {
    const auto item = result.diagnostics_int.find(key);
    return item == result.diagnostics_int.end() ? default_value : item->second;
}

double diagnostic_double_or(
    const epcsaft::native::equilibrium_nlp::IpoptSolveResult& result,
    const std::string& key,
    double default_value
) {
    const auto item = result.diagnostics_double.find(key);
    return item == result.diagnostics_double.end() ? default_value : item->second;
}

bool diagnostic_bool_or(
    const epcsaft::native::equilibrium_nlp::IpoptSolveResult& result,
    const std::string& key,
    bool default_value
) {
    const auto item = result.diagnostics_bool.find(key);
    return item == result.diagnostics_bool.end() ? default_value : item->second;
}

py::list ipopt_iteration_history_to_list(
    const std::vector<epcsaft::native::equilibrium_nlp::IpoptIterationRecord>& history
) {
    py::list out;
    for (const auto& record : history) {
        py::dict row;
        row["iteration"] = record.iteration;
        row["objective"] = record.objective;
        row["primal_infeasibility"] = record.primal_infeasibility;
        row["dual_infeasibility"] = record.dual_infeasibility;
        row["barrier_parameter"] = record.barrier_parameter;
        row["step_size_primal"] = record.step_size_primal;
        row["step_size_dual"] = record.step_size_dual;
        row["regularization_size"] = record.regularization_size;
        row["step_trial_count"] = record.step_trial_count;
        row["restoration_phase"] = record.restoration_phase;
        out.append(row);
    }
    return out;
}

py::list route_seed_attempts_to_list(
    const std::vector<epcsaft::native::equilibrium_nlp::RouteSeedAttempt>& attempts
) {
    py::list out;
    for (const auto& attempt : attempts) {
        py::dict row;
        row["seed_name"] = attempt.seed_name;
        row["status"] = attempt.status;
        row["solver_status"] = attempt.solver_status;
        row["application_status"] = attempt.application_status;
        row["solver_accepted"] = attempt.solver_accepted;
        row["accepted"] = attempt.accepted;
        row["stable"] = attempt.stable;
        row["iteration_count"] = attempt.iteration_count;
        row["objective"] = attempt.objective;
        row["phase_distance"] = attempt.phase_distance;
        row["material_balance_norm"] = attempt.material_balance_norm;
        row["conserved_balance_norm"] = attempt.conserved_balance_norm;
        row["charge_balance_norm"] = attempt.charge_balance_norm;
        row["pressure_consistency_norm"] = attempt.pressure_consistency_norm;
        row["chemical_potential_consistency_norm"] = attempt.chemical_potential_consistency_norm;
        row["phase_equilibrium_norm"] = attempt.phase_equilibrium_norm;
        row["reaction_stationarity_norm"] = attempt.reaction_stationarity_norm;
        row["min_tpd"] = attempt.min_tpd;
        out.append(row);
    }
    return out;
}

py::dict ipopt_continuation_state_to_dict(
    const epcsaft::native::equilibrium_nlp::IpoptSolveResult& result
) {
    py::dict out;
    out["variables"] = result.variables;
    out["bound_lower_multipliers"] = result.bound_lower_multipliers;
    out["bound_upper_multipliers"] = result.bound_upper_multipliers;
    out["constraint_multipliers"] = result.constraint_multipliers;
    return out;
}

py::dict ipopt_continuation_state_to_dict(
    const std::vector<double>& variables,
    const std::vector<double>& bound_lower_multipliers,
    const std::vector<double>& bound_upper_multipliers,
    const std::vector<double>& constraint_multipliers
) {
    py::dict out;
    out["variables"] = variables;
    out["bound_lower_multipliers"] = bound_lower_multipliers;
    out["bound_upper_multipliers"] = bound_upper_multipliers;
    out["constraint_multipliers"] = constraint_multipliers;
    return out;
}

void apply_ipopt_continuation_state(
    epcsaft::native::equilibrium_nlp::IpoptSolveOptions& options,
    const py::object& continuation_state
) {
    if (continuation_state.is_none()) {
        return;
    }
    const py::dict state = continuation_state.cast<py::dict>();
    if (state.contains("variables")) {
        options.initial_variables = state["variables"].cast<std::vector<double>>();
    }
    if (state.contains("bound_lower_multipliers")) {
        options.initial_bound_lower_multipliers =
            state["bound_lower_multipliers"].cast<std::vector<double>>();
    }
    if (state.contains("bound_upper_multipliers")) {
        options.initial_bound_upper_multipliers =
            state["bound_upper_multipliers"].cast<std::vector<double>>();
    }
    if (state.contains("constraint_multipliers")) {
        options.initial_constraint_multipliers =
            state["constraint_multipliers"].cast<std::vector<double>>();
    }
}

py::dict eos_phase_block_to_dict(const epcsaft::native::equilibrium_nlp::EosPhaseBlockResult& result) {
    py::dict out;
    out["block"] = result.block;
    out["derivative_backend"] = result.derivative_backend;
    out["variable_names"] = result.variable_names;
    out["constraint_names"] = result.constraint_names;
    out["temperature"] = result.temperature;
    out["target_pressure"] = result.target_pressure;
    out["gas_constant_temperature"] = result.gas_constant_temperature;
    out["total_amount"] = result.total_amount;
    out["volume"] = result.volume;
    out["density"] = result.density;
    out["composition"] = result.composition;
    out["residual_helmholtz"] = result.residual_helmholtz;
    out["eos_pressure"] = result.eos_pressure;
    out["compressibility_factor"] = result.compressibility_factor;
    py::dict objective_terms;
    objective_terms["ideal_helmholtz"] = result.ideal_helmholtz;
    objective_terms["residual_helmholtz"] = result.residual_helmholtz_term;
    objective_terms["pressure_work"] = result.pressure_work;
    out["objective_terms"] = objective_terms;
    py::dict electrolyte_terms;
    electrolyte_terms["block"] = result.electrolyte_contribution.block;
    electrolyte_terms["value_backend"] = result.electrolyte_contribution.value_backend;
    electrolyte_terms["term_basis"] = result.electrolyte_contribution.term_basis;
    electrolyte_terms["active"] = result.electrolyte_contribution.active;
    electrolyte_terms["temperature"] = result.electrolyte_contribution.temperature;
    electrolyte_terms["density"] = result.electrolyte_contribution.density;
    electrolyte_terms["composition"] = result.electrolyte_contribution.composition;
    electrolyte_terms["amounts"] = result.electrolyte_contribution.amounts;
    electrolyte_terms["charges"] = result.electrolyte_contribution.charges;
    electrolyte_terms["phase_charge_residual"] = result.electrolyte_contribution.phase_charge_residual;
    electrolyte_terms["ion_residual_helmholtz"] = result.electrolyte_contribution.ion_residual_helmholtz;
    electrolyte_terms["born_residual_helmholtz"] = result.electrolyte_contribution.born_residual_helmholtz;
    electrolyte_terms["electrolyte_residual_helmholtz"] =
        result.electrolyte_contribution.electrolyte_residual_helmholtz;
    electrolyte_terms["total_residual_helmholtz"] = result.electrolyte_contribution.total_residual_helmholtz;
    out["electrolyte_terms"] = electrolyte_terms;
    out["objective"] = result.objective;
    out["gradient"] = result.gradient;
    out["objective_curvature_backend"] = result.objective_curvature_backend;
    out["objective_curvature_shape"] =
        py::make_tuple(result.objective_curvature_rows, result.objective_curvature_cols);
    out["objective_curvature_row_major"] = result.objective_curvature_row_major;
    out["pressure_hessian_backend"] = result.pressure_hessian_backend;
    out["pressure_hessian_shape"] = py::make_tuple(result.pressure_hessian_rows, result.pressure_hessian_cols);
    out["pressure_hessian_row_major"] = result.pressure_hessian_row_major;
    out["pressure_consistency_residual"] = result.pressure_consistency_residual;
    out["constraint_jacobian_backend"] = result.constraint_jacobian_backend;
    out["constraint_jacobian_shape"] = py::make_tuple(result.constraint_jacobian_rows, result.constraint_jacobian_cols);
    out["constraint_jacobian_row_major"] = result.constraint_jacobian_row_major;
    out["pressure_jacobian_backend"] = result.pressure_jacobian_backend;
    out["pressure_jacobian_shape"] = py::make_tuple(result.pressure_jacobian_rows, result.pressure_jacobian_cols);
    out["pressure_jacobian"] = result.pressure_jacobian_row_major;
    out["pressure_density_derivative"] = result.pressure_density_derivative;
    return out;
}

py::dict electrolyte_contribution_block_to_dict(
    const epcsaft::native::equilibrium_nlp::ElectrolyteContributionBlockResult& result
) {
    py::dict out;
    out["block"] = result.block;
    out["value_backend"] = result.value_backend;
    out["term_basis"] = result.term_basis;
    out["active"] = result.active;
    out["temperature"] = result.temperature;
    out["density"] = result.density;
    out["composition"] = result.composition;
    out["amounts"] = result.amounts;
    out["charges"] = result.charges;
    out["phase_charge_residual"] = result.phase_charge_residual;
    out["ion_residual_helmholtz"] = result.ion_residual_helmholtz;
    out["born_residual_helmholtz"] = result.born_residual_helmholtz;
    out["electrolyte_residual_helmholtz"] = result.electrolyte_residual_helmholtz;
    out["total_residual_helmholtz"] = result.total_residual_helmholtz;
    return out;
}

py::dict eos_phase_system_to_dict(const epcsaft::native::equilibrium_nlp::EosPhaseSystemResult& result) {
    py::dict out;
    out["block"] = result.block;
    out["derivative_backend"] = result.derivative_backend;
    out["phase_count"] = result.phase_count;
    out["species_count"] = result.species_count;
    out["variable_names"] = result.variable_names;
    out["constraint_names"] = result.constraint_names;
    out["temperature"] = result.temperature;
    out["target_pressure"] = result.target_pressure;
    out["feed_amounts"] = result.feed_amounts;
    out["objective"] = result.objective;
    out["association_objective"] = result.association_objective;
    out["phase_association_objectives"] = result.phase_association_objectives;
    out["gradient"] = result.gradient;
    out["objective_hessian_backend"] = result.objective_hessian_backend;
    out["objective_hessian_shape"] = py::make_tuple(result.objective_hessian_rows, result.objective_hessian_cols);
    out["objective_hessian_row_major"] = result.objective_hessian_row_major;
    out["constraints"] = result.constraints;
    out["phase_charge_residuals"] = result.phase_charge_residuals;
    out["phase_association_residuals"] = result.phase_association_residuals;
    out["constraint_jacobian_backend"] = result.constraint_jacobian_backend;
    out["constraint_jacobian_shape"] =
        py::make_tuple(result.constraint_jacobian_rows, result.constraint_jacobian_cols);
    out["constraint_jacobian_row_major"] = result.constraint_jacobian_row_major;
    out["constraint_hessian_backend"] = result.constraint_hessian_backend;
    out["constraint_hessian_shape"] =
        py::make_tuple(result.constraint_hessian_rows, result.constraint_hessian_cols);
    out["constraint_hessian_tensor_row_major"] = result.constraint_hessian_tensor_row_major;
    out["constraint_has_hessian"] = result.constraint_has_hessian;
    py::list phase_blocks;
    for (const auto& block : result.phase_blocks) {
        phase_blocks.append(eos_phase_block_to_dict(block));
    }
    out["phase_blocks"] = phase_blocks;
    return out;
}

py::dict association_mass_action_block_to_dict(
    const epcsaft::native::equilibrium_nlp::AssociationMassActionBlockResult& result
) {
    py::dict out;
    out["block"] = result.block;
    out["derivative_backend"] = result.derivative_backend;
    out["site_count"] = result.site_count;
    out["constraint_names"] = result.constraint_names;
    out["residuals"] = result.residuals;
    out["density_derivative"] = result.density_derivative;
    out["jacobian_shape"] = py::make_tuple(result.jacobian_rows, result.jacobian_cols);
    out["site_fraction_jacobian_row_major"] = result.site_fraction_jacobian_row_major;
    out["site_composition_jacobian_row_major"] = result.site_composition_jacobian_row_major;
    return out;
}

py::dict neutral_two_phase_eos_nlp_contract_to_dict(
    const epcsaft::native::equilibrium_nlp::NeutralTwoPhaseEosNlpContract& result
) {
    py::dict out;
    out["problem_name"] = result.problem_name;
    out["derivative_backend"] = result.derivative_backend;
    out["variable_model"] = result.variable_model;
    out["density_backend"] = result.density_backend;
    out["residual_families"] = result.residual_families;
    out["constraint_families"] = result.constraint_families;
    out["phase_count"] = result.phase_count;
    out["species_count"] = result.species_count;
    out["balance_row_count"] = result.balance_row_count;
    out["reaction_count"] = result.reaction_count;
    out["variable_count"] = result.variable_count;
    out["constraint_count"] = result.constraint_count;
    out["jacobian_nonzero_count"] = result.jacobian_nonzero_count;
    out["standard_mu_rt"] = result.standard_mu_rt;
    out["initial_point"] = result.initial_point;
    out["variable_lower_bounds"] = result.variable_lower_bounds;
    out["variable_upper_bounds"] = result.variable_upper_bounds;
    out["constraint_lower_bounds"] = result.constraint_lower_bounds;
    out["constraint_upper_bounds"] = result.constraint_upper_bounds;
    out["objective_at_initial"] = result.objective_at_initial;
    out["gradient_at_initial"] = result.gradient_at_initial;
    out["constraints_at_initial"] = result.constraints_at_initial;
    out["jacobian_rows"] = result.jacobian_rows;
    out["jacobian_cols"] = result.jacobian_cols;
    out["jacobian_values_at_initial"] = result.jacobian_values_at_initial;
    return out;
}

py::dict neutral_two_phase_eos_postsolve_to_dict(
    const epcsaft::native::equilibrium_nlp::NeutralTwoPhaseEosPostsolve& result
) {
    py::dict out;
    out["accepted"] = result.accepted;
    out["rejection_reason"] = result.rejection_reason;
    out["derivative_backend"] = result.derivative_backend;
    out["residual_families"] = result.residual_families;
    out["constraint_families"] = result.constraint_families;
    out["phase_count"] = result.phase_count;
    out["species_count"] = result.species_count;
    out["material_balance_norm"] = result.material_balance_norm;
    out["pressure_consistency_norm"] = result.pressure_consistency_norm;
    out["chemical_potential_consistency_norm"] = result.chemical_potential_consistency_norm;
    out["ln_fugacity_consistency_norm"] = result.ln_fugacity_consistency_norm;
    out["charge_balance_norm"] = result.charge_balance_norm;
    out["fixed_composition_norm"] = result.fixed_composition_norm;
    out["phase_amount_total_norm"] = result.phase_amount_total_norm;
    out["phase_distance"] = result.phase_distance;
    out["objective"] = result.objective;
    out["gibbs_feed"] = result.gibbs_feed;
    out["gibbs_split"] = result.gibbs_split;
    out["gibbs_delta"] = result.gibbs_delta;
    out["minimum_phase_fraction"] = result.minimum_phase_fraction;
    out["density_backend"] = result.density_backend;
    out["constraints"] = result.constraints;
    out["phase_amount_totals"] = result.phase_amount_totals;
    out["phase_volumes"] = result.phase_volumes;
    out["phase_densities"] = result.phase_densities;
    out["phase_compositions"] = result.phase_compositions;
    out["phase_ln_fugacity_coefficients"] = result.phase_ln_fugacity_coefficients;
    return out;
}

py::dict neutral_two_phase_eos_route_result_to_dict(
    const epcsaft::native::equilibrium_nlp::NeutralTwoPhaseEosRouteResult& result
) {
    py::dict out;
    apply_ipopt_route_status_fields(out, result);
    apply_eos_route_metadata_fields(out, result);
    out["solver_feasible_point"] = result.solver_feasible_point;
    apply_ipopt_route_solution_fields(out, result);
    out["continuation_state"] = ipopt_continuation_state_to_dict(
        result.variables,
        result.bound_lower_multipliers,
        result.bound_upper_multipliers,
        result.constraint_multipliers
    );
    out["iteration_history"] = ipopt_iteration_history_to_list(result.iteration_history);
    out["seed_attempts"] = route_seed_attempts_to_list(result.seed_attempts);
    out["phase_amounts"] = result.phase_amounts;
    out["phase_volumes"] = result.phase_volumes;
    out["postsolve"] = neutral_two_phase_eos_postsolve_to_dict(result.postsolve);
    return out;
}

py::dict activation_to_dict(const epcsaft::native::equilibrium::ProblemFamilyActivation& activation) {
    py::dict out;
    out["key"] = activation.key;
    out["display_name"] = activation.display_name;
    out["direct_transfer"] = activation.direct_transfer;
    out["reaction_equilibrium"] = activation.reaction_equilibrium;
    out["conservation_basis"] = activation.conservation_basis;
    out["phase_charge"] = activation.phase_charge;
    out["split_variables"] = activation.split_variables;
    out["stability_prelayer"] = activation.stability_prelayer;
    out["postsolve_certification"] = activation.postsolve_certification;
    out["derivative_requirement"] = activation.derivative_requirement;
    out["production_exposed"] = activation.production_exposed;
    out["exposure_status"] = activation.exposure_status;
    out["residual_families"] = activation.residual_families;
    out["constraint_families"] = activation.constraint_families;
    out["proof_routes"] = activation.proof_routes;
    out["variable_model"] = activation.variable_model;
    out["density_backend"] = activation.density_backend;
    return out;
}

py::dict selector_input_classification_to_dict(
    const epcsaft::native::equilibrium::SelectorInputClassification& classification
) {
    py::dict out;
    out["neutral"] = classification.neutral;
    out["nonreactive"] = classification.nonreactive;
    out["nonelectrolyte"] = classification.nonelectrolyte;
    out["nonassociating"] = classification.nonassociating;
    return out;
}

py::dict selector_contract_to_dict(const epcsaft::native::equilibrium::SelectorContract& contract) {
    py::dict out = neutral_two_phase_eos_nlp_contract_to_dict(contract.nlp_contract);
    out["selector_family"] = contract.selector_family;
    out["route"] = contract.route;
    out["activation"] = activation_to_dict(contract.activation);
    out["production_exposed"] = contract.production_exposed;
    out["certification_required"] = contract.certification_required;
    out["density_closure_required"] = contract.density_closure_required;
    out["exact_derivatives_required"] = contract.exact_derivatives_required;
    out["input_classification"] = selector_input_classification_to_dict(contract.input_classification);
    return out;
}

void apply_selector_metadata(
    py::dict& out,
    const epcsaft::native::equilibrium::SelectorContract& contract
) {
    out["selector_family"] = contract.selector_family;
    out["route"] = contract.route;
    out["activation"] = activation_to_dict(contract.activation);
    out["production_exposed"] = contract.production_exposed;
    out["certification_required"] = contract.certification_required;
    out["density_closure_required"] = contract.density_closure_required;
    out["exact_derivatives_required"] = contract.exact_derivatives_required;
    out["input_classification"] = selector_input_classification_to_dict(contract.input_classification);
    py::dict stability_certificate;
    stability_certificate["accepted"] = out["accepted"].cast<bool>();
    stability_certificate["method"] = contract.activation.postsolve_certification;
    py::object postsolve = out["postsolve"];
    if (!postsolve.is_none()) {
        py::dict postsolve_dict = postsolve.cast<py::dict>();
        if (postsolve_dict.contains("phase_distance")) {
            stability_certificate["phase_distance"] = postsolve_dict["phase_distance"];
        }
    }
    out["stability_certificate"] = stability_certificate;
}

py::dict neutral_two_phase_eos_phase_payload_to_dict(
    const epcsaft::native::equilibrium_nlp::NeutralTwoPhaseEosPhasePayload& phase
) {
    py::dict diagnostics;
    diagnostics["amount_total"] = phase.amount_total;
    diagnostics["volume"] = phase.volume;
    diagnostics["eos_pressure"] = phase.eos_pressure;
    diagnostics["pressure_consistency_residual"] = phase.pressure_consistency_residual;
    diagnostics["compressibility_factor"] = phase.compressibility_factor;

    py::dict out;
    out["label"] = phase.label;
    out["composition"] = phase.composition;
    out["density"] = phase.density;
    out["temperature"] = phase.temperature;
    out["pressure"] = phase.pressure;
    out["phase_fraction"] = phase.phase_fraction;
    out["ln_fugacity_coefficient"] = phase.ln_fugacity_coefficient;
    out["fugacity_coefficient"] = phase.fugacity_coefficient;
    out["amount_total"] = phase.amount_total;
    out["volume"] = phase.volume;
    out["eos_pressure"] = phase.eos_pressure;
    out["diagnostics"] = diagnostics;
    return out;
}

py::dict neutral_two_phase_eos_result_payload_to_dict(
    const epcsaft::native::equilibrium_nlp::NeutralTwoPhaseEosResultPayload& result
) {
    py::list phases;
    py::list labels;
    for (const auto& phase : result.phases) {
        phases.append(neutral_two_phase_eos_phase_payload_to_dict(phase));
        labels.append(phase.label);
    }

    py::dict diagnostics;
    diagnostics["derivative_backend"] = result.derivative_backend;
    diagnostics["rejection_reason"] = result.rejection_reason;
    diagnostics["objective"] = result.objective;
    diagnostics["material_balance_norm"] = result.material_balance_norm;
    diagnostics["pressure_consistency_norm"] = result.pressure_consistency_norm;
    diagnostics["chemical_potential_consistency_norm"] = result.chemical_potential_consistency_norm;
    diagnostics["ln_fugacity_consistency_norm"] = result.ln_fugacity_consistency_norm;
    diagnostics["phase_distance"] = result.phase_distance;
    diagnostics["constraints"] = result.constraints;
    diagnostics["feed_amounts"] = result.feed_amounts;

    py::dict out;
    out["accepted"] = result.accepted;
    out["backend"] = result.backend;
    out["problem_kind"] = result.problem_kind;
    out["phase_labels"] = labels;
    out["phases"] = phases;
    out["stable"] = result.stable;
    out["split_detected"] = result.split_detected;
    out["derivative_backend"] = result.derivative_backend;
    out["rejection_reason"] = result.rejection_reason;
    out["objective"] = result.objective;
    out["material_balance_norm"] = result.material_balance_norm;
    out["pressure_consistency_norm"] = result.pressure_consistency_norm;
    out["chemical_potential_consistency_norm"] = result.chemical_potential_consistency_norm;
    out["ln_fugacity_consistency_norm"] = result.ln_fugacity_consistency_norm;
    out["phase_distance"] = result.phase_distance;
    out["constraints"] = result.constraints;
    out["diagnostics"] = diagnostics;
    return out;
}

epcsaft::native::equilibrium_nlp::IpoptSolveOptions ipopt_solve_options_from_scalars(
    int max_iterations,
    double tolerance,
    double timeout_seconds,
    const std::string& hessian_mode = "auto",
    int iteration_history_limit = 20,
    const std::string& linear_solver = "auto",
    double acceptable_tolerance = 0.0,
    double constraint_violation_tolerance = 0.0,
    double dual_infeasibility_tolerance = 0.0,
    double complementarity_tolerance = 0.0
) {
    epcsaft::native::equilibrium_nlp::IpoptSolveOptions options;
    options.max_iterations = max_iterations;
    options.tolerance = tolerance;
    options.acceptable_tolerance = acceptable_tolerance;
    options.constraint_violation_tolerance = constraint_violation_tolerance;
    options.dual_infeasibility_tolerance = dual_infeasibility_tolerance;
    options.complementarity_tolerance = complementarity_tolerance;
    options.max_wall_time_seconds = timeout_seconds;
    options.hessian_mode = hessian_mode;
    options.iteration_history_limit = iteration_history_limit;
    options.linear_solver = linear_solver;
    return options;
}

void apply_ipopt_control_kwargs(
    epcsaft::native::equilibrium_nlp::IpoptSolveOptions& options,
    const py::kwargs& kwargs
) {
    for (const auto& item : kwargs) {
        const std::string key = py::cast<std::string>(item.first);
        if (key == "linear_solver") {
            options.linear_solver = py::cast<std::string>(item.second);
            continue;
        }
        if (key == "acceptable_tolerance") {
            options.acceptable_tolerance = py::cast<double>(item.second);
            continue;
        }
        if (key == "constraint_violation_tolerance") {
            options.constraint_violation_tolerance = py::cast<double>(item.second);
            continue;
        }
        if (key == "dual_infeasibility_tolerance") {
            options.dual_infeasibility_tolerance = py::cast<double>(item.second);
            continue;
        }
        if (key == "complementarity_tolerance") {
            options.complementarity_tolerance = py::cast<double>(item.second);
            continue;
        }
        if (key == "print_level") {
            options.print_level = py::cast<int>(item.second);
            continue;
        }
        throw ValueError("Unknown Ipopt solve option keyword: " + key);
    }
}

}  // namespace

void register_equilibrium_bindings(pybind11::module_& m) {
    m.def("_native_equilibrium_activation_matrix", []() {
        py::list rows;
        for (const auto& activation : epcsaft::native::equilibrium::problem_family_activation_matrix()) {
            rows.append(activation_to_dict(activation));
        }
        return rows;
    });
    // AlgID: bubble_dew_ipopt
    m.def("_native_equilibrium_selector_contract", [](
        const std::shared_ptr<ePCSAFTMixtureNative>& mixture,
        const std::string& route,
        double scalar,
        const std::vector<double>& composition
    ) {
        if (!mixture) {
            throw ValueError("Equilibrium selector contract requires a native mixture.");
        }
        return selector_contract_to_dict(epcsaft::native::equilibrium::evaluate_selector_contract(
            mixture->args(),
            route,
            scalar,
            composition
        ));
    });
    // AlgID: bubble_dew_ipopt
    m.def("_native_equilibrium_selector_route_result", [](
        const std::shared_ptr<ePCSAFTMixtureNative>& mixture,
        const std::string& route,
        double scalar,
        const std::vector<double>& composition,
        int max_iterations,
        double tolerance,
        double timeout_seconds,
        const std::string& hessian_mode,
        int iteration_history_limit,
        double phase_total_tolerance,
        double pressure_tolerance,
        double chemical_potential_tolerance,
        double phase_distance_tolerance,
        const py::object& continuation_state,
        const py::kwargs& kwargs
    ) {
        if (!mixture) {
            throw ValueError("Equilibrium selector route result requires a native mixture.");
        }
        epcsaft::native::equilibrium_nlp::IpoptSolveOptions options =
            ipopt_solve_options_from_scalars(
                max_iterations,
                tolerance,
                timeout_seconds,
                hessian_mode,
                iteration_history_limit
            );
        apply_ipopt_control_kwargs(options, kwargs);
        apply_ipopt_continuation_state(options, continuation_state);
        const auto contract = epcsaft::native::equilibrium::evaluate_selector_contract(
            mixture->args(),
            route,
            scalar,
            composition
        );
        py::dict out = neutral_two_phase_eos_route_result_to_dict(
            epcsaft::native::equilibrium::solve_selector_route(
                mixture->args(),
                route,
                scalar,
                composition,
                options,
                phase_total_tolerance,
                pressure_tolerance,
                chemical_potential_tolerance,
                phase_distance_tolerance
            )
        );
        apply_selector_metadata(out, contract);
        return out;
    });

    m.def("_native_second_order_assembly_smoke", []() {
        namespace nlp = epcsaft::native::equilibrium_nlp;
        py::dict out;

        nlp::ObjectiveSecondOrderData objective;
        objective.variable_count = 2;
        objective.hessian_row_major = {2.0, 1.0, 1.0, 4.0};
        objective.backend = "analytic";

        nlp::ConstraintSecondOrderData constraints;
        constraints.constraint_count = 2;
        constraints.variable_count = 2;
        constraints.hessian_tensor_row_major = {
            0.0, 2.0,
            2.0, 0.0,
            0.0, 0.0,
            0.0, 0.0
        };
        constraints.has_hessian = {true, false};
        constraints.backend = "analytic";

        const nlp::LagrangianHessianAssembler assembler(2);
        out["nonzero_count"] = assembler.nonzero_count();
        out["lagrangian_lower"] = assembler.values(0.5, objective, constraints, {3.0, 100.0});

        nlp::ConstraintSecondOrderData nearly_symmetric_constraints;
        nearly_symmetric_constraints.constraint_count = 1;
        nearly_symmetric_constraints.variable_count = 2;
        nearly_symmetric_constraints.hessian_tensor_row_major = {
            0.0, 1.0 + 5.0e-9,
            1.0 - 5.0e-9, 0.0,
        };
        nearly_symmetric_constraints.has_hessian = {true};
        nearly_symmetric_constraints.backend = "analytic";
        out["weighted_symmetry_lower"] =
            assembler.values(0.0, objective, nearly_symmetric_constraints, {1.0e12});

        nlp::ResidualSecondOrderData residuals;
        residuals.residual_count = 2;
        residuals.variable_count = 2;
        residuals.residuals = {2.0, -1.0};
        residuals.jacobian_row_major = {
            1.0, 2.0,
            3.0, 4.0
        };
        residuals.residual_hessian_tensor_row_major = {
            1.0, 0.0,
            0.0, 2.0,
            0.0, 1.0,
            1.0, 0.0
        };
        const nlp::ObjectiveSecondOrderData residual_quadratic =
            nlp::residual_quadratic_objective_second_order(residuals);
        out["residual_quadratic_lower"] =
            nlp::lower_triangle_values(residual_quadratic.hessian_row_major, residual_quadratic.variable_count);

        nlp::VariableTransformSecondOrderData transform;
        transform.input_variable_count = 2;
        transform.output_variable_count = 2;
        transform.jacobian_row_major = {
            4.0, 0.0,
            0.0, 1.0
        };
        transform.output_hessian_tensor_row_major = {
            2.0, 0.0,
            0.0, 0.0,
            0.0, 0.0,
            0.0, 0.0
        };
        transform.backend = "analytic";
        nlp::ObjectiveSecondOrderData output_objective;
        output_objective.variable_count = 2;
        output_objective.gradient = {3.0, 5.0};
        output_objective.hessian_row_major = {
            7.0, 11.0,
            11.0, 13.0
        };
        output_objective.backend = "analytic";
        const nlp::ObjectiveSecondOrderData transformed =
            nlp::transformed_objective_second_order(transform, output_objective);
        out["transformed_lower"] =
            nlp::lower_triangle_values(transformed.hessian_row_major, transformed.variable_count);
        return out;
    });
    m.def("_native_ipopt_smoke", []() {
        py::dict out;
        const auto adapter = epcsaft::native::equilibrium_nlp::native_ipopt_adapter_info();
        const bool compiled = adapter.compiled;
        out["backend"] = "ipopt";
        out["compiled"] = compiled;
        out["available"] = compiled;
        out["adapter_available"] = adapter.adapter_available;
        out["adapter_kind"] = adapter.adapter_kind;
        out["adapter_source_available"] = true;
        out["requires_exact_gradient"] = adapter.exact_gradient_required;
        out["requires_exact_jacobian"] = adapter.exact_jacobian_required;
#ifdef EPCSAFT_IPOPT_STATUS
        out["status"] = EPCSAFT_IPOPT_STATUS;
#else
        out["status"] = adapter.status;
#endif
        return out;
    });
    m.def("_native_ipopt_quadratic_smoke", [](
        const std::string& hessian_mode,
        int iteration_history_limit,
        const std::string& linear_solver,
        double acceptable_tolerance,
        double constraint_violation_tolerance,
        double dual_infeasibility_tolerance,
        double complementarity_tolerance,
        const py::object& continuation_state
    ) {
        py::dict out;
        const auto adapter = epcsaft::native::equilibrium_nlp::native_ipopt_adapter_info();
        out["backend"] = "ipopt";
        out["compiled"] = adapter.compiled;
        out["adapter_available"] = adapter.adapter_available;
        out["adapter_kind"] = adapter.adapter_kind;
        out["problem"] = "quadratic_linear_constraint_smoke";
        out["ran"] = false;
        out["accepted"] = false;
        if (!adapter.compiled) {
            out["status"] = "ipopt_dependency_required";
            return out;
        }
        epcsaft::native::equilibrium_nlp::IpoptSolveOptions options;
        options.max_iterations = 50;
        options.tolerance = 1.0e-10;
        options.hessian_mode = hessian_mode;
        options.iteration_history_limit = iteration_history_limit;
        options.linear_solver = linear_solver;
        options.acceptable_tolerance = acceptable_tolerance;
        options.constraint_violation_tolerance = constraint_violation_tolerance;
        options.dual_infeasibility_tolerance = dual_infeasibility_tolerance;
        options.complementarity_tolerance = complementarity_tolerance;
        apply_ipopt_continuation_state(options, continuation_state);
        const auto result = epcsaft::native::equilibrium_nlp::solve_ipopt_quadratic_smoke(options);
        out["ran"] = result.solver_ran;
        out["accepted"] = result.accepted;
        out["status"] = result.solver_status;
        out["application_status"] = result.application_status;
        out["objective"] = result.objective;
        out["variables"] = result.variables;
        out["constraints"] = result.constraints;
        out["continuation_state"] = ipopt_continuation_state_to_dict(result);
        out["iteration_history"] = ipopt_iteration_history_to_list(result.iteration_history);
        out["iteration_count"] = diagnostic_int_or(result, "iteration_count", 0);
        out["iteration_history_limit"] = diagnostic_int_or(result, "iteration_history_limit", 0);
        out["hessian_approximation"] = diagnostic_string_or(result, "hessian_approximation", "");
        out["hessian_backend"] = diagnostic_string_or(result, "hessian_backend", "");
        out["eval_h_calls"] = diagnostic_int_or(result, "eval_h_calls", 0);
        out["scaling_method"] = diagnostic_string_or(result, "scaling_method", "");
        out["variable_scaling_count"] = diagnostic_int_or(result, "variable_scaling_count", 0);
        out["constraint_scaling_count"] = diagnostic_int_or(result, "constraint_scaling_count", 0);
        out["objective_scaling"] = diagnostic_double_or(result, "objective_scaling", 1.0);
        out["acceptable_tolerance"] = diagnostic_double_or(result, "acceptable_tolerance", 0.0);
        out["constraint_violation_tolerance"] = diagnostic_double_or(result, "constraint_violation_tolerance", 0.0);
        out["dual_infeasibility_tolerance"] = diagnostic_double_or(result, "dual_infeasibility_tolerance", 0.0);
        out["complementarity_tolerance"] = diagnostic_double_or(result, "complementarity_tolerance", 0.0);
        out["variable_scaling_min"] = diagnostic_double_or(result, "variable_scaling_min", 0.0);
        out["variable_scaling_max"] = diagnostic_double_or(result, "variable_scaling_max", 0.0);
        out["constraint_scaling_min"] = diagnostic_double_or(result, "constraint_scaling_min", 0.0);
        out["constraint_scaling_max"] = diagnostic_double_or(result, "constraint_scaling_max", 0.0);
        out["linear_solver_requested"] = diagnostic_string_or(result, "linear_solver_requested", "auto");
        out["linear_solver_selected"] = diagnostic_string_or(result, "linear_solver_selected", "default");
        out["warm_start_requested"] = diagnostic_bool_or(result, "warm_start_requested", false);
        out["warm_start_used"] = diagnostic_bool_or(result, "warm_start_used", false);
        out["exact_hessian_available"] = diagnostic_bool_or(result, "exact_hessian_available", false);
        out["exact_gradient_required"] = adapter.exact_gradient_required;
        out["exact_jacobian_required"] = adapter.exact_jacobian_required;
        return out;
    },
        py::arg("hessian_mode") = "auto",
        py::arg("iteration_history_limit") = 20,
        py::arg("linear_solver") = "auto",
        py::arg("acceptable_tolerance") = 1.0e-8,
        py::arg("constraint_violation_tolerance") = 1.0e-10,
        py::arg("dual_infeasibility_tolerance") = 1.0e-10,
        py::arg("complementarity_tolerance") = 1.0e-10,
        py::arg("continuation_state") = py::none()
    );
    m.def("_native_ideal_reaction_smoke", []() {
        const double log_k = std::log(3.0);
        const std::vector<double> stoichiometry = {-1.0, 1.0};
        const std::vector<double> amounts = epcsaft::native::equilibrium_nlp::amounts_from_reaction_extents(
            {1.0, 0.0},
            1,
            stoichiometry,
            {0.75}
        );
        const std::vector<double> standard_mu_rt = epcsaft::native::equilibrium_nlp::standard_mu_rt_from_reactions(
            2,
            1,
            stoichiometry,
            {log_k}
        );
        const auto gibbs = epcsaft::native::equilibrium_nlp::evaluate_ideal_reduced_gibbs(
            amounts,
            standard_mu_rt,
            true
        );
        const auto reactions = epcsaft::native::equilibrium_nlp::evaluate_ideal_reaction_quotients(
            amounts,
            1,
            stoichiometry,
            {log_k}
        );
        py::dict out;
        out["model"] = "homogeneous_ideal_reaction";
        out["amounts"] = amounts;
        out["initial_amounts"] = std::vector<double>{1.0, 0.0};
        out["extents"] = std::vector<double>{0.75};
        out["mole_fractions"] = gibbs.mole_fractions;
        out["reduced_gibbs"] = gibbs.value;
        out["standard_mu_rt"] = standard_mu_rt;
        out["gradient"] = gibbs.gradient;
        out["hessian_row_major"] = gibbs.hessian_row_major;
        out["log_q"] = reactions.log_q;
        out["residuals"] = reactions.residuals;
        out["reaction_jacobian_row_major"] = reactions.jacobian_row_major;
        out["reaction_stationarity"] = gibbs.gradient[1] - gibbs.gradient[0];
        out["convex_kernel_scope"] = "homogeneous_ideal_reaction_validation";
        py::dict phase_residuals;
        phase_residuals["ideal_liquid"] = reactions.residuals[0];
        phase_residuals["ideal_vapor"] = reactions.residuals[0];
        out["phase_validation_residuals"] = phase_residuals;
        return out;
    });
    m.def("_native_eos_phase_block", [](
        const std::shared_ptr<ePCSAFTMixtureNative>& mixture,
        double temperature,
        double target_pressure,
        const std::vector<double>& amounts,
        double volume
    ) {
        if (!mixture) {
            throw ValueError("EOS phase block requires a native mixture.");
        }
        return eos_phase_block_to_dict(epcsaft::native::equilibrium_nlp::evaluate_eos_phase_block(
            mixture->args(),
            temperature,
            target_pressure,
            amounts,
            volume
        ));
    });
    m.def("_native_eos_phase_system", [](
        const std::shared_ptr<ePCSAFTMixtureNative>& mixture,
        double temperature,
        double target_pressure,
        const std::vector<std::vector<double>>& phase_amounts,
        const std::vector<double>& volumes,
        const std::vector<double>& feed_amounts,
        const std::vector<double>& charges,
        const std::vector<std::vector<double>>& association_site_fractions,
        const std::vector<double>& association_delta_row_major
    ) {
        if (!mixture) {
            throw ValueError("EOS phase system requires a native mixture.");
        }
        return eos_phase_system_to_dict(epcsaft::native::equilibrium_nlp::evaluate_eos_phase_system(
            mixture->args(),
            temperature,
            target_pressure,
            phase_amounts,
            volumes,
            feed_amounts,
            charges,
            association_site_fractions,
            association_delta_row_major
        ));
    },
       py::arg("mixture"),
       py::arg("temperature"),
       py::arg("target_pressure"),
       py::arg("phase_amounts"),
       py::arg("volumes"),
       py::arg("feed_amounts"),
       py::arg("charges") = std::vector<double>{},
       py::arg("association_site_fractions") = std::vector<std::vector<double>>{},
       py::arg("association_delta_row_major") = std::vector<double>{});
    m.def("_native_association_mass_action_block", [](
        double density,
        const std::vector<double>& site_fractions,
        const std::vector<double>& composition,
        const std::vector<double>& delta_row_major
    ) {
        return association_mass_action_block_to_dict(
            epcsaft::native::equilibrium_nlp::evaluate_association_mass_action_block(
                density,
                site_fractions,
                composition,
                delta_row_major
            )
        );
    });
    m.def("_native_electrolyte_contribution_block", [](
        const std::shared_ptr<ePCSAFTMixtureNative>& mixture,
        double temperature,
        double density,
        const std::vector<double>& composition,
        const std::vector<double>& amounts
    ) {
        if (!mixture) {
            throw ValueError("Electrolyte contribution block requires a native mixture.");
        }
        return electrolyte_contribution_block_to_dict(
            epcsaft::native::equilibrium_nlp::evaluate_electrolyte_contribution_block(
                mixture->args(),
                temperature,
                density,
                composition,
                amounts
            )
        );
    });
    m.def("_native_neutral_two_phase_eos_nlp_contract", [](
        const std::shared_ptr<ePCSAFTMixtureNative>& mixture,
        double temperature,
        double target_pressure,
        const std::vector<std::vector<double>>& phase_amounts,
        const std::vector<double>& volumes,
        const std::vector<double>& feed_amounts
    ) {
        if (!mixture) {
            throw ValueError("Neutral two-phase EOS NLP contract requires a native mixture.");
        }
        return neutral_two_phase_eos_nlp_contract_to_dict(
            epcsaft::native::equilibrium_nlp::evaluate_neutral_two_phase_eos_nlp_contract(
                mixture->args(),
                temperature,
                target_pressure,
                phase_amounts,
                volumes,
                feed_amounts
            )
        );
    });
    m.def("_native_neutral_two_phase_eos_postsolve", [](
        const std::shared_ptr<ePCSAFTMixtureNative>& mixture,
        double temperature,
        double target_pressure,
        const std::vector<std::vector<double>>& phase_amounts,
        const std::vector<double>& volumes,
        const std::vector<double>& feed_amounts,
        double material_tolerance,
        double pressure_tolerance,
        double chemical_potential_tolerance,
        double phase_distance_tolerance
    ) {
        if (!mixture) {
            throw ValueError("Neutral two-phase EOS postsolve requires a native mixture.");
        }
        return neutral_two_phase_eos_postsolve_to_dict(
            epcsaft::native::equilibrium_nlp::evaluate_neutral_two_phase_eos_postsolve(
                mixture->args(),
                temperature,
                target_pressure,
                phase_amounts,
                volumes,
                feed_amounts,
                material_tolerance,
                pressure_tolerance,
                chemical_potential_tolerance,
                phase_distance_tolerance
            )
        );
    });
    m.def("_native_neutral_two_phase_eos_result", [](
        const std::shared_ptr<ePCSAFTMixtureNative>& mixture,
        double temperature,
        double target_pressure,
        const std::vector<std::vector<double>>& phase_amounts,
        const std::vector<double>& volumes,
        const std::vector<double>& feed_amounts,
        double material_tolerance,
        double pressure_tolerance,
        double chemical_potential_tolerance,
        double phase_distance_tolerance
    ) {
        if (!mixture) {
            throw ValueError("Neutral two-phase EOS result builder requires a native mixture.");
        }
        return neutral_two_phase_eos_result_payload_to_dict(
            epcsaft::native::equilibrium_nlp::build_neutral_two_phase_eos_result(
                mixture->args(),
                temperature,
                target_pressure,
                phase_amounts,
                volumes,
                feed_amounts,
                material_tolerance,
                pressure_tolerance,
                chemical_potential_tolerance,
                phase_distance_tolerance
            )
        );
    });
}
