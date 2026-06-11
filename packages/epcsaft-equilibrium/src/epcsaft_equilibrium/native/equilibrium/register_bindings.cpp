#include "bindings/equilibrium_bindings.h"

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include <cmath>
#include <limits>
#include <memory>
#include <string>
#include <utility>
#include <vector>

#include "equilibrium/blocks/association_block.h"
#include "equilibrium/blocks/electrolyte_block.h"
#include "equilibrium/blocks/eos_phase_block.h"
#include "equilibrium/blocks/gibbs_blocks.h"
#include "equilibrium/blocks/reaction_block.h"
#include "equilibrium/blocks/saturation_block.h"
#include "equilibrium/core/activation_matrix.h"
#include "equilibrium/core/nlp_problem.h"
#include "equilibrium/core/second_order.h"
#include "equilibrium/core/selector_core.h"
#include "equilibrium/core/variable_transform.h"
#include "equilibrium/results/result_builder.h"
#include "equilibrium/results/route_result_bridge.h"
#include "equilibrium/solvers/ipopt_adapter.h"
#include "model/native_types.h"

namespace py = pybind11;

namespace {

using epcsaft::native::equilibrium_nlp::route_result_bridge::apply_eos_route_metadata_fields;
using epcsaft::native::equilibrium_nlp::route_result_bridge::apply_ipopt_route_solution_fields;
using epcsaft::native::equilibrium_nlp::route_result_bridge::apply_ipopt_route_status_fields;
namespace nlp = epcsaft::native::equilibrium_nlp;

template <typename T>
T required_native_arg_field(const py::dict& payload, const char* key) {
    if (!payload.contains(key)) {
        throw ValueError(std::string("Native mixture argument payload missing field: ") + key);
    }
    return py::cast<T>(payload[key]);
}

add_args native_args_from_payload(const py::dict& payload) {
    add_args out;
    out.m = required_native_arg_field<std::vector<double>>(payload, "m");
    out.s = required_native_arg_field<std::vector<double>>(payload, "s");
    out.e = required_native_arg_field<std::vector<double>>(payload, "e");
    out.k_ij = required_native_arg_field<std::vector<double>>(payload, "k_ij");
    out.e_assoc = required_native_arg_field<std::vector<double>>(payload, "e_assoc");
    out.vol_a = required_native_arg_field<std::vector<double>>(payload, "vol_a");
    out.z = required_native_arg_field<std::vector<double>>(payload, "z");
    out.dielc = required_native_arg_field<std::vector<double>>(payload, "dielc");
    out.mw = required_native_arg_field<std::vector<double>>(payload, "mw");
    out.mixed_rel_perm_a = required_native_arg_field<std::vector<double>>(payload, "mixed_rel_perm_a");
    out.mixed_rel_perm_b = required_native_arg_field<std::vector<double>>(payload, "mixed_rel_perm_b");
    out.mixed_rel_perm_c = required_native_arg_field<std::vector<double>>(payload, "mixed_rel_perm_c");
    out.mixed_rel_perm_mask = required_native_arg_field<std::vector<int>>(payload, "mixed_rel_perm_mask");
    out.mixed_rel_perm_water_index = required_native_arg_field<int>(payload, "mixed_rel_perm_water_index");
    out.dielc_rule = required_native_arg_field<int>(payload, "dielc_rule");
    out.dielc_diff_mode = required_native_arg_field<int>(payload, "dielc_diff_mode");
    out.hc_dadx_diff_mode = required_native_arg_field<int>(payload, "hc_dadx_diff_mode");
    out.disp_dadx_diff_mode = required_native_arg_field<int>(payload, "disp_dadx_diff_mode");
    out.assoc_dadx_diff_mode = required_native_arg_field<int>(payload, "assoc_dadx_diff_mode");
    out.d_ion_mode = required_native_arg_field<int>(payload, "d_ion_mode");
    out.mu_DH_diff_mode = required_native_arg_field<int>(payload, "mu_DH_diff_mode");
    out.mu_DH_comp_dep_rel_perm = required_native_arg_field<int>(payload, "mu_DH_comp_dep_rel_perm");
    out.mu_DH_include_sum_term = required_native_arg_field<int>(payload, "mu_DH_include_sum_term");
    out.include_born_model = required_native_arg_field<int>(payload, "include_born_model");
    out.d_born_mode = required_native_arg_field<int>(payload, "d_born_mode");
    out.born_solvation_shell_model = required_native_arg_field<int>(payload, "born_solvation_shell_model");
    out.born_dielectric_saturation = required_native_arg_field<int>(payload, "born_dielectric_saturation");
    out.born_bulk_mode = required_native_arg_field<int>(payload, "born_bulk_mode");
    out.mu_born_diff_mode = required_native_arg_field<int>(payload, "mu_born_diff_mode");
    out.mu_born_comp_dep_rel_perm = required_native_arg_field<int>(payload, "mu_born_comp_dep_rel_perm");
    out.mu_born_include_sum_term = required_native_arg_field<int>(payload, "mu_born_include_sum_term");
    out.mu_born_comp_dep_delta_d = required_native_arg_field<int>(payload, "mu_born_comp_dep_delta_d");
    out.d_born = required_native_arg_field<std::vector<double>>(payload, "d_born");
    out.f_solv = required_native_arg_field<std::vector<double>>(payload, "f_solv");
    out.born_model = required_native_arg_field<int>(payload, "born_model");
    out.born_radius_model = required_native_arg_field<int>(payload, "born_radius_model");
    out.born_diff_mode = required_native_arg_field<int>(payload, "born_diff_mode");
    out.born_eps_mode = required_native_arg_field<int>(payload, "born_eps_mode");
    out.DH_model = required_native_arg_field<int>(payload, "DH_model");
    out.assoc_num = required_native_arg_field<std::vector<int>>(payload, "assoc_num");
    out.assoc_matrix = required_native_arg_field<std::vector<int>>(payload, "assoc_matrix");
    out.k_hb = required_native_arg_field<std::vector<double>>(payload, "k_hb");
    out.l_ij = required_native_arg_field<std::vector<double>>(payload, "l_ij");
    out.parameter_source_label = required_native_arg_field<std::string>(payload, "parameter_source_label");
    out.parameter_provenance_status =
        required_native_arg_field<std::string>(payload, "parameter_provenance_status");
    out.binary_interaction_provenance_status =
        required_native_arg_field<std::string>(payload, "binary_interaction_provenance_status");
    out.parameter_provenance_fields =
        required_native_arg_field<std::vector<std::string>>(payload, "parameter_provenance_fields");
    return out;
}

add_args native_args_from_mixture_object(const py::object& mixture, const std::string& context) {
    if (mixture.is_none()) {
        throw ValueError(context + " requires a native mixture.");
    }
    if (py::hasattr(mixture, "_native_args_payload")) {
        return native_args_from_payload(py::cast<py::dict>(mixture.attr("_native_args_payload")()));
    }
    try {
        const auto local = mixture.cast<std::shared_ptr<ePCSAFTMixtureNative>>();
        if (local) {
            return local->args();
        }
    } catch (const py::cast_error& error) {
        throw ValueError(context + " requires a native mixture or argument payload snapshot: " + error.what());
    }
    throw ValueError(context + " requires a native mixture or argument payload snapshot.");
}

class NlpShapeValidationSmokeProblem final : public nlp::NlpProblem {
public:
    explicit NlpShapeValidationSmokeProblem(std::string failure_mode)
        : failure_mode_(std::move(failure_mode)) {}

    std::string name() const override {
        return "nlp_shape_validation_smoke";
    }

    int variable_count() const override {
        return 2;
    }

    int constraint_count() const override {
        return 1;
    }

    int jacobian_nonzero_count() const override {
        return 2;
    }

    nlp::NlpBounds bounds() const override {
        return {{-10.0, -10.0}, {10.0, 10.0}, {3.0}, {3.0}};
    }

    std::vector<double> initial_point() const override {
        return {1.0, 2.0};
    }

    double objective(const std::vector<double>& variables) const override {
        return variables[0] * variables[0] + variables[1] * variables[1];
    }

    std::vector<double> objective_gradient(const std::vector<double>& variables) const override {
        if (failure_mode_ == "gradient_value_size") {
            return {2.0 * variables[0]};
        }
        return {2.0 * variables[0], 2.0 * variables[1]};
    }

    std::vector<double> constraints(const std::vector<double>& variables) const override {
        return {variables[0] + variables[1]};
    }

    nlp::NlpJacobianStructure jacobian_structure() const override {
        return {{0, 0}, {0, 1}};
    }

    std::vector<double> jacobian_values(const std::vector<double>& variables) const override {
        (void)variables;
        if (failure_mode_ == "jacobian_value_size") {
            return {1.0};
        }
        if (failure_mode_ == "jacobian_value_nonfinite") {
            return {1.0, std::numeric_limits<double>::infinity()};
        }
        return {1.0, 1.0};
    }

    bool has_exact_hessian() const override {
        return true;
    }

    int hessian_nonzero_count() const override {
        return 3;
    }

    nlp::NlpHessianStructure hessian_structure() const override {
        return {{0, 1, 1}, {0, 0, 1}};
    }

    std::vector<double> hessian_values(
        const std::vector<double>& variables,
        double objective_factor,
        const std::vector<double>& constraint_multipliers
    ) const override {
        (void)variables;
        (void)constraint_multipliers;
        if (failure_mode_ == "hessian_value_size") {
            return {2.0 * objective_factor, 0.0};
        }
        return {2.0 * objective_factor, 0.0, 2.0 * objective_factor};
    }

    std::string hessian_backend() const override {
        return "analytic";
    }

    nlp::NlpScaling scaling() const override {
        return {1.0, {1.0, 1.0}, {1.0}};
    }

private:
    std::string failure_mode_;
};

py::dict nlp_shape_validation_case(const std::string& failure_mode) {
    py::dict out;
    try {
        NlpShapeValidationSmokeProblem problem(failure_mode);
        nlp::validate_nlp_problem_shape(problem);
        out["accepted"] = true;
        out["message"] = "";
    } catch (const std::exception& exc) {
        out["accepted"] = false;
        out["message"] = exc.what();
    }
    return out;
}

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
        row["max_iterations"] = attempt.max_iterations;
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
    out["objective_third_derivative_backend"] = result.objective_third_derivative_backend;
    out["objective_third_derivative_shape"] = py::make_tuple(
        result.objective_third_derivative_rows,
        result.objective_third_derivative_cols,
        result.objective_third_derivative_cols
    );
    out["objective_third_derivative_tensor_row_major"] = result.objective_third_derivative_tensor_row_major;
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

py::dict single_component_vle_block_to_dict(
    const epcsaft::native::equilibrium_nlp::SingleComponentVleBlockResult& result
) {
    py::dict out;
    out["block"] = result.block;
    out["derivative_backend"] = result.derivative_backend;
    out["jacobian_backend"] = result.jacobian_backend;
    out["variable_names"] = result.variable_names;
    out["constraint_names"] = result.constraint_names;
    out["temperature"] = result.temperature;
    out["vapor_density"] = result.vapor_density;
    out["liquid_density"] = result.liquid_density;
    out["p_sat"] = result.p_sat;
    out["vapor_pressure"] = result.vapor_pressure;
    out["liquid_pressure"] = result.liquid_pressure;
    out["vapor_reduced_chemical_potential"] = result.vapor_reduced_chemical_potential;
    out["liquid_reduced_chemical_potential"] = result.liquid_reduced_chemical_potential;
    out["vapor_pressure_density_derivative"] = result.vapor_pressure_density_derivative;
    out["liquid_pressure_density_derivative"] = result.liquid_pressure_density_derivative;
    out["residuals"] = result.residuals;
    out["jacobian_shape"] = py::make_tuple(result.jacobian_rows, result.jacobian_cols);
    out["jacobian_row_major"] = result.jacobian_row_major;
    out["constraint_scaling"] = result.constraint_scaling;
    out["vapor_phase_block"] = eos_phase_block_to_dict(result.vapor_phase_block);
    out["liquid_phase_block"] = eos_phase_block_to_dict(result.liquid_phase_block);
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
    out["association_site_count"] = result.association_site_count;
    out["association_site_component_index"] = result.association_site_component_index;
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
    out["site_fraction_hessian_backend"] = result.site_fraction_hessian_backend;
    out["site_fraction_hessian_shape"] = py::make_tuple(
        result.site_fraction_hessian_rows,
        result.site_fraction_hessian_cols,
        result.site_fraction_hessian_depth
    );
    out["site_fraction_hessian_tensor_row_major"] = result.site_fraction_hessian_tensor_row_major;
    return out;
}

bool vector_has_size(const std::vector<double>& values, int expected) {
    return expected >= 0 && values.size() == static_cast<std::size_t>(expected);
}

bool vector_has_size(const std::vector<int>& values, int expected) {
    return expected >= 0 && values.size() == static_cast<std::size_t>(expected);
}

py::dict nlp_domain_contract_to_dict(
    const epcsaft::native::equilibrium_nlp::NeutralTwoPhaseEosNlpContract& result
) {
    const bool transform_counts_declared =
        result.transform_input_variable_count > 0 && result.transform_output_variable_count > 0;
    const int expected_transform_jacobian_count = transform_counts_declared
        ? result.transform_input_variable_count * result.transform_output_variable_count
        : 0;
    const int expected_transform_hessian_count = transform_counts_declared
        ? result.transform_output_variable_count
            * result.transform_input_variable_count
            * result.transform_input_variable_count
        : 0;
    const bool transform_jacobian_declared =
        transform_counts_declared
        && result.transform_jacobian_value_count == expected_transform_jacobian_count;
    const bool transform_hessian_declared =
        transform_counts_declared
        && result.transform_hessian_value_count == expected_transform_hessian_count;

    py::dict margins;
    margins["initial_variable_lower_margin"] = result.initial_variable_lower_margin;
    margins["initial_variable_upper_margin"] = result.initial_variable_upper_margin;
    margins["initial_variable_bound_margin"] = result.initial_variable_bound_margin;
    margins["initial_amount_lower_margin"] = result.initial_amount_lower_margin;
    margins["initial_volume_lower_margin"] = result.initial_volume_lower_margin;
    margins["initial_constraint_bound_violation"] = result.initial_constraint_bound_violation;

    py::dict out;
    out["domain_safety_policy"] = result.domain_safety_policy;
    out["transform_policy"] = result.transform_policy;
    out["transform_backend"] = result.transform_backend;
    out["barrier_policy"] = result.barrier_policy;
    out["solver_to_physical_declared"] = transform_counts_declared;
    out["transform_jacobian_declared"] = transform_jacobian_declared;
    out["transform_hessian_declared"] = transform_hessian_declared;
    out["transform_chain_rule_derivatives_declared"] =
        transform_jacobian_declared && transform_hessian_declared;
    out["variable_bounds_declared"] = vector_has_size(result.variable_lower_bounds, result.variable_count)
        && vector_has_size(result.variable_upper_bounds, result.variable_count);
    out["constraint_bounds_declared"] = vector_has_size(result.constraint_lower_bounds, result.constraint_count)
        && vector_has_size(result.constraint_upper_bounds, result.constraint_count);
    out["objective_scaling"] = result.objective_scaling;
    out["variable_scaling_declared"] = vector_has_size(result.variable_scaling, result.variable_count);
    out["constraint_scaling_declared"] = vector_has_size(result.constraint_scaling, result.constraint_count);
    out["ipopt_barrier_owns_declared_bounds"] =
        result.barrier_policy == "ipopt_internal_barrier_for_declared_bounds";
    out["thermodynamic_objective_custom_barrier"] = false;
    out["margins"] = margins;
    return out;
}

py::dict nlp_sparse_contract_to_dict(
    const epcsaft::native::equilibrium_nlp::NeutralTwoPhaseEosNlpContract& result
) {
    py::dict out;
    out["jacobian_ordering_policy"] = "fixed_route_owned_row_col_value_order";
    out["jacobian_nonzero_count"] = result.jacobian_nonzero_count;
    out["jacobian_row_count"] = static_cast<int>(result.jacobian_rows.size());
    out["jacobian_col_count"] = static_cast<int>(result.jacobian_cols.size());
    out["jacobian_value_count"] = static_cast<int>(result.jacobian_values_at_initial.size());
    out["jacobian_structure_matches_values"] =
        vector_has_size(result.jacobian_rows, result.jacobian_nonzero_count)
        && vector_has_size(result.jacobian_cols, result.jacobian_nonzero_count)
        && vector_has_size(result.jacobian_values_at_initial, result.jacobian_nonzero_count);
    out["hessian_ordering_policy"] = "fixed_route_owned_lower_triangle_order";
    out["hessian_nonzero_count"] = result.hessian_nonzero_count;
    out["hessian_row_count"] = static_cast<int>(result.hessian_rows.size());
    out["hessian_col_count"] = static_cast<int>(result.hessian_cols.size());
    out["hessian_value_count"] = static_cast<int>(result.hessian_values_at_initial.size());
    out["hessian_structure_matches_values"] =
        !result.exact_hessian_available
        || (
            vector_has_size(result.hessian_rows, result.hessian_nonzero_count)
            && vector_has_size(result.hessian_cols, result.hessian_nonzero_count)
            && vector_has_size(result.hessian_values_at_initial, result.hessian_nonzero_count)
        );
    return out;
}

py::dict nlp_derivative_contract_to_dict(
    const epcsaft::native::equilibrium_nlp::NeutralTwoPhaseEosNlpContract& result
) {
    const bool gradient_exact = vector_has_size(result.gradient_at_initial, result.variable_count);
    const bool jacobian_exact = vector_has_size(result.jacobian_values_at_initial, result.jacobian_nonzero_count);
    const bool hessian_exact = result.exact_hessian_available
        && vector_has_size(result.hessian_values_at_initial, result.hessian_nonzero_count);
    std::vector<std::string> missing;
    if (!gradient_exact) {
        missing.push_back("objective_gradient");
    }
    if (!jacobian_exact) {
        missing.push_back("constraint_jacobian");
    }
    if (!hessian_exact) {
        missing.push_back("lagrangian_hessian");
    }

    py::dict out;
    out["derivative_backend"] = result.derivative_backend;
    out["objective_gradient_exact"] = gradient_exact;
    out["constraint_jacobian_exact"] = jacobian_exact;
    out["lagrangian_hessian_exact"] = hessian_exact;
    out["hessian_backend"] = result.hessian_backend;
    out["exact_hessian_available"] = result.exact_hessian_available;
    out["missing_exact_derivative_blocks"] = missing;
    return out;
}

py::dict neutral_two_phase_eos_nlp_contract_to_dict(
    const epcsaft::native::equilibrium_nlp::NeutralTwoPhaseEosNlpContract& result
) {
    py::dict out;
    out["problem_name"] = result.problem_name;
    out["derivative_backend"] = result.derivative_backend;
    out["activation_compiler"] = result.activation_compiler;
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
    out["exact_hessian_available"] = result.exact_hessian_available;
    out["hessian_nonzero_count"] = result.hessian_nonzero_count;
    out["hessian_backend"] = result.hessian_backend;
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
    out["hessian_rows"] = result.hessian_rows;
    out["hessian_cols"] = result.hessian_cols;
    out["hessian_values_at_initial"] = result.hessian_values_at_initial;
    out["objective_scaling"] = result.objective_scaling;
    out["variable_scaling"] = result.variable_scaling;
    out["constraint_scaling"] = result.constraint_scaling;
    out["initial_variable_lower_margin"] = result.initial_variable_lower_margin;
    out["initial_variable_upper_margin"] = result.initial_variable_upper_margin;
    out["initial_variable_bound_margin"] = result.initial_variable_bound_margin;
    out["initial_amount_lower_margin"] = result.initial_amount_lower_margin;
    out["initial_volume_lower_margin"] = result.initial_volume_lower_margin;
    out["initial_constraint_bound_violation"] = result.initial_constraint_bound_violation;
    out["domain_safety_policy"] = result.domain_safety_policy;
    out["transform_policy"] = result.transform_policy;
    out["transform_backend"] = result.transform_backend;
    out["transform_input_variable_count"] = result.transform_input_variable_count;
    out["transform_output_variable_count"] = result.transform_output_variable_count;
    out["transform_jacobian_value_count"] = result.transform_jacobian_value_count;
    out["transform_hessian_value_count"] = result.transform_hessian_value_count;
    out["barrier_policy"] = result.barrier_policy;
    out["domain_contract"] = nlp_domain_contract_to_dict(result);
    out["sparse_contract"] = nlp_sparse_contract_to_dict(result);
    out["derivative_contract"] = nlp_derivative_contract_to_dict(result);
    return out;
}

py::dict neutral_two_phase_eos_postsolve_to_dict(
    const epcsaft::native::equilibrium_nlp::NeutralTwoPhaseEosPostsolve& result
) {
    py::dict out;
    out["accepted"] = result.accepted;
    out["stability_checked"] = result.stability_checked;
    out["stability_accepted"] = result.stability_accepted;
    out["candidate_completeness_accepted"] = result.candidate_completeness_accepted;
    out["phase_set_mass_balance_feasible"] = result.phase_set_mass_balance_feasible;
    out["rejection_reason"] = result.rejection_reason;
    out["phase_discovery_backend"] = result.phase_discovery_backend;
    out["stability_certificate"] = result.stability_certificate;
    out["phase_set_status"] = result.phase_set_status;
    out["stage9_phase_discovery_steps"] = result.stage9_phase_discovery_steps;
    out["deterministic_screening_status"] = result.deterministic_screening_status;
    out["deterministic_screening_is_full_held"] = result.deterministic_screening_is_full_held;
    out["continuous_tpd_status"] = result.continuous_tpd_status;
    out["continuous_tpd_backend"] = result.continuous_tpd_backend;
    out["continuous_tpd_best_source"] = result.continuous_tpd_best_source;
    out["deterministic_candidate_count"] = result.deterministic_candidate_count;
    out["continuous_tpd_start_count"] = result.continuous_tpd_start_count;
    out["continuous_tpd_solve_count"] = result.continuous_tpd_solve_count;
    out["continuous_tpd_converged_count"] = result.continuous_tpd_converged_count;
    out["continuous_tpd_iteration_count_total"] = result.continuous_tpd_iteration_count_total;
    out["continuous_tpd_iteration_count_max"] = result.continuous_tpd_iteration_count_max;
    out["continuous_tpd_min"] = result.continuous_tpd_min;
    out["continuous_tpd_step_final_max"] = result.continuous_tpd_step_final_max;
    out["continuous_tpd_best_phase_kind"] = result.continuous_tpd_best_phase_kind;
    out["continuous_tpd_best_density"] = result.continuous_tpd_best_density;
    out["continuous_tpd_best_molar_volume"] = result.continuous_tpd_best_molar_volume;
    out["continuous_tpd_best_composition"] = result.continuous_tpd_best_composition;
    out["held_stage_i_status"] = result.held_stage_i_status;
    out["held_stage_i_start_count"] = result.held_stage_i_start_count;
    out["held_stage_i_negative_tpd_found"] = result.held_stage_i_negative_tpd_found;
    out["held_stage_i_min_tpd"] = result.held_stage_i_min_tpd;
    out["held_stage_ii_status"] = result.held_stage_ii_status;
    out["held_stage_ii_candidate_bound_audit_status"] = result.held_stage_ii_candidate_bound_audit_status;
    out["held_stage_ii_dual_loop_status"] = result.held_stage_ii_dual_loop_status;
    out["held_stage_ii_major_iterations"] = result.held_stage_ii_major_iterations;
    out["held_stage_ii_candidate_count"] = result.held_stage_ii_candidate_count;
    out["held_stage_ii_lower_bound"] = result.held_stage_ii_lower_bound;
    out["held_stage_ii_upper_bound"] = result.held_stage_ii_upper_bound;
    out["held_stage_ii_bound_gap"] = result.held_stage_ii_bound_gap;
    out["held_stage_ii_bound_tolerance"] = result.held_stage_ii_bound_tolerance;
    out["held_stage_ii_stopping_reason"] = result.held_stage_ii_stopping_reason;
    out["held_stage_ii_lower_bound_history"] = result.held_stage_ii_lower_bound_history;
    out["held_stage_ii_upper_bound_history"] = result.held_stage_ii_upper_bound_history;
    out["held_stage_ii_bound_gap_history"] = result.held_stage_ii_bound_gap_history;
    out["held_stage_ii_replay_ready"] = result.held_stage_ii_replay_ready;
    out["held_stage_ii_replay_source"] = result.held_stage_ii_replay_source;
    out["held_stage_ii_replay_seed_name"] = result.held_stage_ii_replay_seed_name;
    out["held_stage_ii_replay_candidate_count"] = result.held_stage_ii_replay_candidate_count;
    out["held_stage_ii_replay_candidate_ranks"] = result.held_stage_ii_replay_candidate_ranks;
    out["held_stage_ii_replay_phase_fractions"] = result.held_stage_ii_replay_phase_fractions;
    out["held_stage_ii_replay_phase_kinds"] = result.held_stage_ii_replay_phase_kinds;
    out["held_stage_ii_replay_phase_compositions"] = result.held_stage_ii_replay_phase_compositions;
    out["held_stage_ii_rejected_candidate_count"] = result.held_stage_ii_rejected_candidate_count;
    out["held_stage_ii_rejected_candidate_ranks"] = result.held_stage_ii_rejected_candidate_ranks;
    out["held_stage_ii_rejected_candidate_reasons"] = result.held_stage_ii_rejected_candidate_reasons;
    out["held_stage_iii_status"] = result.held_stage_iii_status;
    out["held_stage_iii_refined_phase_count"] = result.held_stage_iii_refined_phase_count;
    out["held_stage_iii_consumed_stage_ii_replay_metadata"] =
        result.held_stage_iii_consumed_stage_ii_replay_metadata;
    out["held_stage_iii_replay_source"] = result.held_stage_iii_replay_source;
    out["held_stage_iii_replay_seed_name"] = result.held_stage_iii_replay_seed_name;
    out["held_stage_iii_replay_candidate_count"] = result.held_stage_iii_replay_candidate_count;
    out["derivative_backend"] = result.derivative_backend;
    out["residual_families"] = result.residual_families;
    out["constraint_families"] = result.constraint_families;
    out["phase_count"] = result.phase_count;
    out["species_count"] = result.species_count;
    out["tpd_candidate_count"] = result.tpd_candidate_count;
    out["unique_candidate_count"] = result.unique_candidate_count;
    out["selected_candidate_count"] = result.selected_candidate_count;
    out["material_balance_norm"] = result.material_balance_norm;
    out["pressure_consistency_norm"] = result.pressure_consistency_norm;
    out["chemical_potential_consistency_norm"] = result.chemical_potential_consistency_norm;
    out["ln_fugacity_consistency_norm"] = result.ln_fugacity_consistency_norm;
    out["charge_balance_norm"] = result.charge_balance_norm;
    out["fixed_composition_norm"] = result.fixed_composition_norm;
    out["phase_amount_total_norm"] = result.phase_amount_total_norm;
    out["phase_distance"] = result.phase_distance;
    out["min_tpd"] = result.min_tpd;
    out["candidate_mass_balance_norm"] = result.candidate_mass_balance_norm;
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
    out["selected_phase_fractions"] = result.selected_phase_fractions;
    out["selected_phase_kinds"] = result.selected_phase_kinds;
    out["selected_phase_compositions"] = result.selected_phase_compositions;
    out["tpd_candidate_values"] = result.tpd_candidate_values;
    out["tpd_candidate_sources"] = result.tpd_candidate_sources;
    out["tpd_candidate_phase_kinds"] = result.tpd_candidate_phase_kinds;
    out["tpd_candidate_compositions"] = result.tpd_candidate_compositions;
    out["tpd_candidate_pressure_residuals"] = result.tpd_candidate_pressure_residuals;
    out["tpd_candidate_iteration_counts"] = result.tpd_candidate_iteration_counts;
    out["tpd_candidate_step_finals"] = result.tpd_candidate_step_finals;
    out["tpd_candidate_ranks"] = result.tpd_candidate_ranks;
    out["tpd_candidate_feasibility_statuses"] = result.tpd_candidate_feasibility_statuses;
    out["tpd_candidate_selected"] = result.tpd_candidate_selected;
    py::dict seed_and_stability;
    seed_and_stability["phase_discovery_backend"] = result.phase_discovery_backend;
    seed_and_stability["stability_certificate"] = result.stability_certificate;
    seed_and_stability["phase_set_status"] = result.phase_set_status;
    seed_and_stability["candidate_source_count"] = static_cast<int>(result.tpd_candidate_sources.size());
    seed_and_stability["candidate_sources"] = result.tpd_candidate_sources;
    seed_and_stability["candidate_ranks"] = result.tpd_candidate_ranks;
    seed_and_stability["candidate_iteration_counts"] = result.tpd_candidate_iteration_counts;
    seed_and_stability["candidate_step_finals"] = result.tpd_candidate_step_finals;
    seed_and_stability["candidate_feasibility_statuses"] = result.tpd_candidate_feasibility_statuses;
    seed_and_stability["candidate_selected"] = result.tpd_candidate_selected;
    seed_and_stability["candidate_mass_balance_norm"] = result.candidate_mass_balance_norm;
    seed_and_stability["min_tpd"] = result.min_tpd;
    seed_and_stability["deterministic_screening_is_full_held"] = false;
    seed_and_stability["stage9_phase_discovery_steps"] = result.stage9_phase_discovery_steps;
    seed_and_stability["deterministic_screening_status"] = result.deterministic_screening_status;
    seed_and_stability["continuous_tpd_status"] = result.continuous_tpd_status;
    seed_and_stability["held_stage_i_status"] = result.held_stage_i_status;
    seed_and_stability["held_stage_ii_status"] = result.held_stage_ii_status;
    seed_and_stability["held_stage_ii_candidate_bound_audit_status"] =
        result.held_stage_ii_candidate_bound_audit_status;
    seed_and_stability["held_stage_ii_dual_loop_status"] = result.held_stage_ii_dual_loop_status;
    seed_and_stability["held_stage_ii_stopping_reason"] = result.held_stage_ii_stopping_reason;
    seed_and_stability["held_stage_ii_replay_ready"] = result.held_stage_ii_replay_ready;
    seed_and_stability["held_stage_ii_replay_seed_name"] = result.held_stage_ii_replay_seed_name;
    seed_and_stability["held_stage_iii_status"] = result.held_stage_iii_status;
    seed_and_stability["held_stage_iii_consumed_stage_ii_replay_metadata"] =
        result.held_stage_iii_consumed_stage_ii_replay_metadata;
    out["seed_and_stability"] = seed_and_stability;
    return out;
}

py::dict neutral_tpd_candidate_to_dict(
    const epcsaft::native::equilibrium_nlp::NeutralTpdCandidate& result
) {
    py::dict out;
    out["valid"] = result.valid;
    out["source"] = result.source;
    out["phase_kind"] = result.phase_kind;
    out["composition"] = result.composition;
    out["density"] = result.density;
    out["molar_volume"] = result.molar_volume;
    out["tpd"] = result.tpd;
    out["transformed_objective"] = result.transformed_objective;
    out["pressure_residual_estimate"] = result.pressure_residual_estimate;
    out["tpd_backend"] = result.tpd_backend;
    out["tpd_status"] = result.tpd_status;
    out["start_source"] = result.start_source;
    out["tpd_iteration_count"] = result.tpd_iteration_count;
    out["tpd_step_final"] = result.tpd_step_final;
    out["feasibility_status"] = result.feasibility_status;
    out["candidate_rank"] = result.candidate_rank;
    out["selected"] = result.selected;
    return out;
}

py::dict neutral_phase_discovery_to_dict(
    const epcsaft::native::equilibrium_nlp::NeutralPhaseDiscoveryResult& result
) {
    py::dict out;
    out["stability_checked"] = result.stability_checked;
    out["stability_accepted"] = result.stability_accepted;
    out["candidate_completeness_accepted"] = result.candidate_completeness_accepted;
    out["phase_set_mass_balance_feasible"] = result.phase_set_mass_balance_feasible;
    out["phase_discovery_backend"] = result.phase_discovery_backend;
    out["stability_certificate"] = result.stability_certificate;
    out["phase_set_status"] = result.phase_set_status;
    out["stage9_phase_discovery_steps"] = result.stage9_phase_discovery_steps;
    out["deterministic_screening_status"] = result.deterministic_screening_status;
    out["deterministic_screening_is_full_held"] = result.deterministic_screening_is_full_held;
    out["continuous_tpd_status"] = result.continuous_tpd_status;
    out["continuous_tpd_backend"] = result.continuous_tpd_backend;
    out["continuous_tpd_best_source"] = result.continuous_tpd_best_source;
    out["deterministic_candidate_count"] = result.deterministic_candidate_count;
    out["continuous_tpd_start_count"] = result.continuous_tpd_start_count;
    out["continuous_tpd_solve_count"] = result.continuous_tpd_solve_count;
    out["continuous_tpd_converged_count"] = result.continuous_tpd_converged_count;
    out["continuous_tpd_iteration_count_total"] = result.continuous_tpd_iteration_count_total;
    out["continuous_tpd_iteration_count_max"] = result.continuous_tpd_iteration_count_max;
    out["continuous_tpd_min"] = result.continuous_tpd_min;
    out["continuous_tpd_step_final_max"] = result.continuous_tpd_step_final_max;
    out["continuous_tpd_best_phase_kind"] = result.continuous_tpd_best_phase_kind;
    out["continuous_tpd_best_density"] = result.continuous_tpd_best_density;
    out["continuous_tpd_best_molar_volume"] = result.continuous_tpd_best_molar_volume;
    out["continuous_tpd_best_composition"] = result.continuous_tpd_best_composition;
    out["held_stage_i_status"] = result.held_stage_i_status;
    out["held_stage_i_start_count"] = result.held_stage_i_start_count;
    out["held_stage_i_negative_tpd_found"] = result.held_stage_i_negative_tpd_found;
    out["held_stage_i_min_tpd"] = result.held_stage_i_min_tpd;
    out["held_stage_ii_status"] = result.held_stage_ii_status;
    out["held_stage_ii_candidate_bound_audit_status"] = result.held_stage_ii_candidate_bound_audit_status;
    out["held_stage_ii_dual_loop_status"] = result.held_stage_ii_dual_loop_status;
    out["held_stage_ii_major_iterations"] = result.held_stage_ii_major_iterations;
    out["held_stage_ii_candidate_count"] = result.held_stage_ii_candidate_count;
    out["held_stage_ii_lower_bound"] = result.held_stage_ii_lower_bound;
    out["held_stage_ii_upper_bound"] = result.held_stage_ii_upper_bound;
    out["held_stage_ii_bound_gap"] = result.held_stage_ii_bound_gap;
    out["held_stage_ii_bound_tolerance"] = result.held_stage_ii_bound_tolerance;
    out["held_stage_ii_stopping_reason"] = result.held_stage_ii_stopping_reason;
    out["held_stage_ii_lower_bound_history"] = result.held_stage_ii_lower_bound_history;
    out["held_stage_ii_upper_bound_history"] = result.held_stage_ii_upper_bound_history;
    out["held_stage_ii_bound_gap_history"] = result.held_stage_ii_bound_gap_history;
    out["held_stage_ii_replay_ready"] = result.held_stage_ii_replay_ready;
    out["held_stage_ii_replay_source"] = result.held_stage_ii_replay_source;
    out["held_stage_ii_replay_seed_name"] = result.held_stage_ii_replay_seed_name;
    out["held_stage_ii_replay_candidate_count"] = result.held_stage_ii_replay_candidate_count;
    out["held_stage_ii_replay_candidate_ranks"] = result.held_stage_ii_replay_candidate_ranks;
    out["held_stage_ii_replay_phase_fractions"] = result.held_stage_ii_replay_phase_fractions;
    out["held_stage_ii_replay_phase_kinds"] = result.held_stage_ii_replay_phase_kinds;
    out["held_stage_ii_replay_phase_compositions"] = result.held_stage_ii_replay_phase_compositions;
    out["held_stage_ii_rejected_candidate_count"] = result.held_stage_ii_rejected_candidate_count;
    out["held_stage_ii_rejected_candidate_ranks"] = result.held_stage_ii_rejected_candidate_ranks;
    out["held_stage_ii_rejected_candidate_reasons"] = result.held_stage_ii_rejected_candidate_reasons;
    out["held_stage_iii_status"] = result.held_stage_iii_status;
    out["held_stage_iii_refined_phase_count"] = result.held_stage_iii_refined_phase_count;
    out["min_tpd"] = result.min_tpd;
    out["candidate_mass_balance_norm"] = result.candidate_mass_balance_norm;
    out["tpd_candidate_count"] = result.tpd_candidate_count;
    out["unique_candidate_count"] = result.unique_candidate_count;
    out["selected_candidate_count"] = result.selected_candidate_count;
    out["selected_phase_fractions"] = result.selected_phase_fractions;
    out["selected_phase_kinds"] = result.selected_phase_kinds;
    out["selected_phase_compositions"] = result.selected_phase_compositions;
    py::list candidates;
    for (const auto& candidate : result.candidates) {
        candidates.append(neutral_tpd_candidate_to_dict(candidate));
    }
    out["candidates"] = candidates;
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
    out["phase_labels"] = result.phase_labels;
    out["phase_roles"] = result.phase_roles;
    out["physical_evidence"] =
        epcsaft::native::equilibrium_nlp::route_result_bridge::route_physical_evidence_to_dict(
            epcsaft::native::equilibrium_nlp::build_neutral_route_physical_evidence(result)
        );
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
    out["public_routes"] = activation.public_routes;
    out["variable_model"] = activation.variable_model;
    out["density_backend"] = activation.density_backend;
    return out;
}

py::dict activation_plan_to_dict(const epcsaft::native::equilibrium::ActivationPlan& plan) {
    py::dict out;
    out["family_key"] = plan.family_key;
    out["route"] = plan.route;
    out["phase_keys"] = plan.phase_keys;
    out["phase_kinds"] = plan.phase_kinds;
    out["variable_blocks"] = plan.variable_blocks;
    out["constraint_blocks"] = plan.constraint_blocks;
    out["residual_blocks"] = plan.residual_blocks;
    out["postsolve_blocks"] = plan.postsolve_blocks;
    out["variable_model"] = plan.variable_model;
    out["density_backend"] = plan.density_backend;
    out["feed_composition"] = plan.feed_composition;
    out["temperature"] = plan.temperature;
    out["pressure"] = plan.pressure;
    return out;
}

py::dict variable_block_layout_to_dict(
    const epcsaft::native::equilibrium::VariableBlockLayout& block
) {
    py::dict out;
    out["name"] = block.name;
    out["offset"] = block.offset;
    out["size"] = block.size;
    out["stride"] = block.stride;
    return out;
}

py::dict variable_layout_to_dict(const epcsaft::native::equilibrium::VariableLayout& layout) {
    py::dict out;
    out["family_key"] = layout.family_key;
    out["route"] = layout.route;
    out["variable_model"] = layout.variable_model;
    out["physical_basis"] = layout.physical_basis;
    out["solver_coordinate_basis"] = layout.solver_coordinate_basis;
    out["lift_policy"] = layout.lift_policy;
    out["back_lift_policy"] = layout.back_lift_policy;
    out["transform_policy"] = layout.transform_policy;
    out["phase_count"] = layout.phase_count;
    out["species_count"] = layout.species_count;
    out["variable_count"] = layout.variable_count;
    out["phase_keys"] = layout.phase_keys;
    out["phase_kinds"] = layout.phase_kinds;
    out["physical_variable_order"] = layout.physical_variable_order;
    py::list blocks;
    for (const auto& block : layout.variable_blocks) {
        blocks.append(variable_block_layout_to_dict(block));
    }
    out["variable_blocks"] = blocks;
    out["phase_amount_indices"] = layout.phase_amount_indices;
    out["phase_volume_indices"] = layout.phase_volume_indices;
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
    out["neutral_species_indices"] = classification.neutral_species_indices;
    out["ionic_species_indices"] = classification.ionic_species_indices;
    out["ionic_species_charges"] = classification.ionic_species_charges;
    out["associating_species_indices"] = classification.associating_species_indices;
    out["reactive_species_indices"] = classification.reactive_species_indices;
    out["phase_eligible_species_indices"] = classification.phase_eligible_species_indices;
    out["transferable_species_indices"] = classification.transferable_species_indices;
    out["fixed_species_indices"] = classification.fixed_species_indices;
    out["active_family_markers"] = classification.active_family_markers;
    return out;
}

py::dict selector_request_pretreatment_to_dict(
    const epcsaft::native::equilibrium::SelectorRequestPretreatment& pretreatment
) {
    py::dict out;
    out["request_source"] = pretreatment.request_source;
    out["route"] = pretreatment.route;
    out["composition_role"] = pretreatment.composition_role;
    out["temperature_role"] = pretreatment.temperature_role;
    out["pressure_role"] = pretreatment.pressure_role;
    out["composition_basis"] = pretreatment.composition_basis;
    out["feed_amount_basis"] = pretreatment.feed_amount_basis;
    out["route_shape_validated"] = pretreatment.route_shape_validated;
    out["finite_numeric_inputs"] = pretreatment.finite_numeric_inputs;
    out["species_count"] = pretreatment.species_count;
    out["composition_length"] = pretreatment.composition_length;
    out["composition_original_sum"] = pretreatment.composition_original_sum;
    out["composition_normalized_sum"] = pretreatment.composition_normalized_sum;
    out["composition_was_normalized"] = pretreatment.composition_was_normalized;
    out["composition_normalization_tolerance"] = pretreatment.composition_normalization_tolerance;
    return out;
}

py::dict selector_thermodynamic_input_to_dict(
    const epcsaft::native::equilibrium::SelectorThermodynamicInput& input
) {
    py::dict out;
    out["temperature_kelvin"] = input.temperature_kelvin;
    out["pressure_pascal"] = input.pressure_pascal;
    out["total_amount_basis"] = input.total_amount_basis;
    out["composition_role"] = input.composition_role;
    out["composition_basis"] = input.composition_basis;
    out["amount_basis"] = input.amount_basis;
    out["temperature_role"] = input.temperature_role;
    out["pressure_role"] = input.pressure_role;
    out["species_indices"] = input.species_indices;
    out["normalized_composition"] = input.normalized_composition;
    out["extensive_amounts"] = input.extensive_amounts;
    return out;
}

py::dict selector_parameter_readiness_to_dict(
    const epcsaft::native::equilibrium::SelectorParameterReadiness& readiness
) {
    py::dict out;
    out["parameter_basis"] = readiness.parameter_basis;
    out["parameter_source_label"] = readiness.parameter_source_label;
    out["parameter_provenance_status"] = readiness.parameter_provenance_status;
    out["binary_interaction_provenance_status"] = readiness.binary_interaction_provenance_status;
    out["pure_neutral_parameters_present"] = readiness.pure_neutral_parameters_present;
    out["binary_interaction_matrix_present"] = readiness.binary_interaction_matrix_present;
    out["source_backed_parameter_provenance_present"] = readiness.source_backed_parameter_provenance_present;
    out["explicit_zero_binary_interaction_convention"] =
        readiness.explicit_zero_binary_interaction_convention;
    out["association_parameters_active"] = readiness.association_parameters_active;
    out["electrolyte_parameters_active"] = readiness.electrolyte_parameters_active;
    out["born_terms_active"] = readiness.born_terms_active;
    out["required_parameter_families_present"] = readiness.required_parameter_families_present;
    out["required_parameter_families"] = readiness.required_parameter_families;
    out["missing_required_parameter_families"] = readiness.missing_required_parameter_families;
    out["active_residual_families"] = readiness.active_residual_families;
    out["parameter_provenance_fields"] = readiness.parameter_provenance_fields;
    out["derivative_gate"] = readiness.derivative_gate;
    return out;
}

py::dict selector_contract_to_dict(const epcsaft::native::equilibrium::SelectorContract& contract) {
    py::dict out = neutral_two_phase_eos_nlp_contract_to_dict(contract.nlp_contract);
    out["selector_family"] = contract.selector_family;
    out["route"] = contract.route;
    out["composition_role"] = contract.composition_role;
    out["phase_labels"] = contract.phase_labels;
    out["phase_roles"] = contract.phase_roles;
    out["specified_temperature"] = contract.specified_temperature;
    out["specified_pressure"] = contract.specified_pressure;
    out["activation"] = activation_to_dict(contract.activation);
    if (contract.has_activation_plan) {
        out["activation_compiler"] = contract.nlp_contract.activation_compiler;
        out["activation_plan"] = activation_plan_to_dict(contract.activation_plan);
        out["variable_layout"] = variable_layout_to_dict(contract.variable_layout);
    }
    out["production_exposed"] = contract.production_exposed;
    out["certification_required"] = contract.certification_required;
    out["density_closure_required"] = contract.density_closure_required;
    out["exact_derivatives_required"] = contract.exact_derivatives_required;
    out["request_pretreatment"] = selector_request_pretreatment_to_dict(contract.request_pretreatment);
    out["thermodynamic_input"] = selector_thermodynamic_input_to_dict(contract.thermodynamic_input);
    out["parameter_readiness"] = selector_parameter_readiness_to_dict(contract.parameter_readiness);
    out["input_classification"] = selector_input_classification_to_dict(contract.input_classification);
    return out;
}

void apply_selector_metadata(
    py::dict& out,
    const epcsaft::native::equilibrium::SelectorContract& contract
) {
    out["selector_family"] = contract.selector_family;
    out["route"] = contract.route;
    out["composition_role"] = contract.composition_role;
    out["phase_labels"] = contract.phase_labels;
    out["phase_roles"] = contract.phase_roles;
    out["specified_temperature"] = contract.specified_temperature;
    out["specified_pressure"] = contract.specified_pressure;
    out["activation"] = activation_to_dict(contract.activation);
    if (contract.has_activation_plan) {
        out["activation_compiler"] = contract.nlp_contract.activation_compiler;
        out["activation_plan"] = activation_plan_to_dict(contract.activation_plan);
        out["variable_layout"] = variable_layout_to_dict(contract.variable_layout);
    }
    out["production_exposed"] = contract.production_exposed;
    out["certification_required"] = contract.certification_required;
    out["density_closure_required"] = contract.density_closure_required;
    out["exact_derivatives_required"] = contract.exact_derivatives_required;
    out["request_pretreatment"] = selector_request_pretreatment_to_dict(contract.request_pretreatment);
    out["thermodynamic_input"] = selector_thermodynamic_input_to_dict(contract.thermodynamic_input);
    out["parameter_readiness"] = selector_parameter_readiness_to_dict(contract.parameter_readiness);
    out["input_classification"] = selector_input_classification_to_dict(contract.input_classification);
    const py::object postsolve = out["postsolve"];
    out["stability_certificate"] =
        epcsaft::native::equilibrium_nlp::route_result_bridge::neutral_route_stability_certificate_from_postsolve(
            postsolve,
            contract.activation.postsolve_certification,
            out["accepted"].cast<bool>()
        );
}

double selector_request_double(const py::dict& payload, const char* key) {
    if (!payload.contains(key) || payload[key].is_none()) {
        return 0.0;
    }
    return py::cast<double>(payload[key]);
}

epcsaft::native::equilibrium::SelectorRouteRequest selector_request_from_dict(const py::dict& payload) {
    epcsaft::native::equilibrium::SelectorRouteRequest out;
    if (!payload.contains("route")) {
        throw ValueError("Equilibrium selector request requires route.");
    }
    if (!payload.contains("composition")) {
        throw ValueError("Equilibrium selector request requires composition.");
    }
    if (!payload.contains("composition_role")) {
        throw ValueError("Equilibrium selector request requires composition_role.");
    }
    out.route = py::cast<std::string>(payload["route"]);
    out.composition = py::cast<std::vector<double>>(payload["composition"]);
    out.composition_role = py::cast<std::string>(payload["composition_role"]);
    out.has_temperature = payload.contains("temperature") && !payload["temperature"].is_none();
    out.has_pressure = payload.contains("pressure") && !payload["pressure"].is_none();
    out.temperature = selector_request_double(payload, "temperature");
    out.pressure = selector_request_double(payload, "pressure");
    if (payload.contains("phase_kinds") && !payload["phase_kinds"].is_none()) {
        out.phase_kinds = py::cast<std::vector<std::string>>(payload["phase_kinds"]);
    }
    return out;
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
    const std::string& option_profile = "proof",
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
    options.option_profile = option_profile;
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
        if (key == "option_profile") {
            options.option_profile = py::cast<std::string>(item.second);
            continue;
        }
        if (key == "bound_push") {
            options.bound_push = py::cast<double>(item.second);
            continue;
        }
        if (key == "bound_frac") {
            options.bound_frac = py::cast<double>(item.second);
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
    m.def("_native_equilibrium_activation_plan_contract", [](
        const py::object& mixture,
        const py::dict& request_payload
    ) {
        const add_args args = native_args_from_mixture_object(mixture, "Equilibrium activation plan contract");
        const auto request = selector_request_from_dict(request_payload);
        const auto plan = epcsaft::native::equilibrium::build_activation_plan(
            args,
            request
        );
        const auto layout = epcsaft::native::equilibrium::build_variable_layout(
            plan,
            static_cast<int>(plan.feed_composition.size())
        );
        py::dict out;
        out["activation_plan"] = activation_plan_to_dict(plan);
        out["variable_layout"] = variable_layout_to_dict(layout);
        return out;
    });
    // AlgID: bubble_dew_ipopt
    m.def("_native_equilibrium_selector_contract", [](
        const py::object& mixture,
        const py::dict& request_payload
    ) {
        const add_args args = native_args_from_mixture_object(mixture, "Equilibrium selector contract");
        const auto request = selector_request_from_dict(request_payload);
        return selector_contract_to_dict(epcsaft::native::equilibrium::evaluate_selector_contract(
            args,
            request
        ));
    });
    m.def("_native_activated_neutral_tp_flash_nlp_contract", [](
        const py::object& mixture,
        const py::dict& request_payload
    ) {
        const add_args args = native_args_from_mixture_object(mixture, "Activated neutral TP flash contract");
        const auto request = selector_request_from_dict(request_payload);
        const auto plan = epcsaft::native::equilibrium::build_activation_plan(
            args,
            request
        );
        const auto layout = epcsaft::native::equilibrium::build_variable_layout(
            plan,
            static_cast<int>(plan.feed_composition.size())
        );
        py::dict out;
        out["activation_plan"] = activation_plan_to_dict(plan);
        out["variable_layout"] = variable_layout_to_dict(layout);
        out["activated"] = neutral_two_phase_eos_nlp_contract_to_dict(
            epcsaft::native::equilibrium_nlp::evaluate_activated_neutral_tp_flash_nlp_contract(
                args,
                plan,
                layout
            )
        );
        out["trusted_reference"] = neutral_two_phase_eos_nlp_contract_to_dict(
            epcsaft::native::equilibrium_nlp::evaluate_neutral_tp_flash_eos_nlp_contract(
                args,
                plan.temperature,
                plan.pressure,
                plan.feed_composition
            )
        );
        return out;
    });
    // AlgID: bubble_dew_ipopt
    m.def("_native_equilibrium_selector_route_result", [](
        const py::object& mixture,
        const py::dict& request_payload,
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
        const add_args args = native_args_from_mixture_object(mixture, "Equilibrium selector route result");
        epcsaft::native::equilibrium_nlp::IpoptSolveOptions options =
            ipopt_solve_options_from_scalars(
                max_iterations,
                tolerance,
                timeout_seconds,
                hessian_mode,
                "proof",
                iteration_history_limit
            );
        apply_ipopt_control_kwargs(options, kwargs);
        apply_ipopt_continuation_state(options, continuation_state);
        const auto request = selector_request_from_dict(request_payload);
        const auto contract = epcsaft::native::equilibrium::evaluate_selector_contract(
            args,
            request
        );
        py::dict out = neutral_two_phase_eos_route_result_to_dict(
            epcsaft::native::equilibrium::solve_selector_route(
                args,
                request,
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
    m.def("_native_variable_transform_smoke", []() {
        py::dict out;

        const nlp::IdentityVariableTransform identity(3);
        const std::vector<double> identity_solver = {1.0, 2.0, 3.0};
        const nlp::VariableTransformEvaluation identity_eval = identity.evaluate(identity_solver);
        out["method_names"] = std::vector<std::string>{
            "solver_to_physical",
            "dx_du",
            "d2x_du2",
        };
        out["identity_policy"] = identity_eval.transform_policy;
        out["identity_backend"] = identity_eval.backend;
        out["identity_physical"] = identity.solver_to_physical(identity_solver);
        out["identity_dx_du"] = identity.dx_du(identity_solver);
        out["identity_d2x_du2"] = identity.d2x_du2(identity_solver);
        out["identity_second_order_backend"] = identity.second_order_data(identity_solver).backend;

        const nlp::PositiveLogVariableTransform positive_log(2);
        const std::vector<double> positive_solver = {std::log(2.0), std::log(3.0)};
        const nlp::VariableTransformEvaluation positive_eval = positive_log.evaluate(positive_solver);
        out["positive_log_policy"] = positive_eval.transform_policy;
        out["positive_log_backend"] = positive_eval.backend;
        out["positive_log_physical"] = positive_log.solver_to_physical(positive_solver);
        out["positive_log_dx_du"] = positive_log.dx_du(positive_solver);
        out["positive_log_d2x_du2"] = positive_log.d2x_du2(positive_solver);

        nlp::ObjectiveSecondOrderData output_objective;
        output_objective.variable_count = 2;
        output_objective.gradient = positive_eval.physical_variables;
        output_objective.hessian_row_major = {
            1.0, 0.0,
            0.0, 1.0
        };
        output_objective.backend = "analytic";
        const nlp::ObjectiveSecondOrderData transformed =
            nlp::transformed_objective_second_order(
                positive_log.second_order_data(positive_solver),
                output_objective
            );
        out["positive_log_chain_rule_gradient"] = transformed.gradient;
        out["positive_log_chain_rule_lower"] =
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
    m.def("_native_nlp_shape_validation_smoke", []() {
        py::dict out;
        out["valid"] = nlp_shape_validation_case("");
        out["gradient_value_size"] = nlp_shape_validation_case("gradient_value_size");
        out["jacobian_value_size"] = nlp_shape_validation_case("jacobian_value_size");
        out["jacobian_value_nonfinite"] = nlp_shape_validation_case("jacobian_value_nonfinite");
        out["hessian_value_size"] = nlp_shape_validation_case("hessian_value_size");
        return out;
    });
    m.def("_native_ipopt_quadratic_smoke", [](
        const std::string& hessian_mode,
        const std::string& option_profile,
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
        options.option_profile = option_profile;
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
        out["acceptable_iteration_limit"] = diagnostic_int_or(result, "acceptable_iteration_limit", 0);
        out["hessian_approximation"] = diagnostic_string_or(result, "hessian_approximation", "");
        out["hessian_backend"] = diagnostic_string_or(result, "hessian_backend", "");
        out["option_profile"] = diagnostic_string_or(result, "option_profile", "");
        out["solver_acceptance_policy"] = diagnostic_string_or(result, "solver_acceptance_policy", "");
        out["exact_hessian_policy"] = diagnostic_string_or(result, "exact_hessian_policy", "");
        out["eval_h_calls"] = diagnostic_int_or(result, "eval_h_calls", 0);
        out["scaling_method"] = diagnostic_string_or(result, "scaling_method", "");
        out["scaling_contract"] = diagnostic_string_or(result, "scaling_contract", "");
        out["residual_scaling_policy"] = diagnostic_string_or(result, "residual_scaling_policy", "");
        out["linear_solver_policy"] = diagnostic_string_or(result, "linear_solver_policy", "");
        out["barrier_policy"] = diagnostic_string_or(result, "barrier_policy", "");
        out["variable_scaling_count"] = diagnostic_int_or(result, "variable_scaling_count", 0);
        out["constraint_scaling_count"] = diagnostic_int_or(result, "constraint_scaling_count", 0);
        out["active_lower_bound_count"] = diagnostic_int_or(result, "active_lower_bound_count", 0);
        out["active_upper_bound_count"] = diagnostic_int_or(result, "active_upper_bound_count", 0);
        out["active_variable_bound_count"] = diagnostic_int_or(result, "active_variable_bound_count", 0);
        out["step_trial_count_max"] = diagnostic_int_or(result, "step_trial_count_max", 0);
        out["objective_scaling"] = diagnostic_double_or(result, "objective_scaling", 1.0);
        out["acceptable_tolerance"] = diagnostic_double_or(result, "acceptable_tolerance", 0.0);
        out["constraint_violation_tolerance"] = diagnostic_double_or(result, "constraint_violation_tolerance", 0.0);
        out["ipopt_unscaled_constraint_violation_tolerance"] =
            diagnostic_double_or(result, "ipopt_unscaled_constraint_violation_tolerance", 0.0);
        out["dual_infeasibility_tolerance"] = diagnostic_double_or(result, "dual_infeasibility_tolerance", 0.0);
        out["complementarity_tolerance"] = diagnostic_double_or(result, "complementarity_tolerance", 0.0);
        out["bound_push"] = diagnostic_double_or(result, "bound_push", 0.0);
        out["bound_frac"] = diagnostic_double_or(result, "bound_frac", 0.0);
        out["variable_scaling_min"] = diagnostic_double_or(result, "variable_scaling_min", 0.0);
        out["variable_scaling_max"] = diagnostic_double_or(result, "variable_scaling_max", 0.0);
        out["constraint_scaling_min"] = diagnostic_double_or(result, "constraint_scaling_min", 0.0);
        out["constraint_scaling_max"] = diagnostic_double_or(result, "constraint_scaling_max", 0.0);
        out["variable_scaling_ratio"] = diagnostic_double_or(result, "variable_scaling_ratio", 1.0);
        out["constraint_scaling_ratio"] = diagnostic_double_or(result, "constraint_scaling_ratio", 1.0);
        out["scaled_constraint_violation_inf_norm"] =
            diagnostic_double_or(result, "scaled_constraint_violation_inf_norm", 0.0);
        out["scaled_stationarity_inf_norm"] =
            diagnostic_double_or(result, "scaled_stationarity_inf_norm", 0.0);
        out["scaled_complementarity_inf_norm"] =
            diagnostic_double_or(result, "scaled_complementarity_inf_norm", 0.0);
        out["bound_complementarity_inf_norm"] =
            diagnostic_double_or(result, "bound_complementarity_inf_norm", 0.0);
        out["barrier_parameter_final"] = diagnostic_double_or(result, "barrier_parameter_final", 0.0);
        out["regularization_size_final"] = diagnostic_double_or(result, "regularization_size_final", 0.0);
        out["regularization_size_max"] = diagnostic_double_or(result, "regularization_size_max", 0.0);
        out["linear_solver_requested"] = diagnostic_string_or(result, "linear_solver_requested", "auto");
        out["linear_solver_selected"] = diagnostic_string_or(result, "linear_solver_selected", "default");
        out["warm_start_requested"] = diagnostic_bool_or(result, "warm_start_requested", false);
        out["warm_start_used"] = diagnostic_bool_or(result, "warm_start_used", false);
        out["exact_hessian_available"] = diagnostic_bool_or(result, "exact_hessian_available", false);
        out["profile_exact_hessian_gate"] = diagnostic_bool_or(result, "profile_exact_hessian_gate", true);
        out["variable_scaling_quality_passed"] =
            diagnostic_bool_or(result, "variable_scaling_quality_passed", false);
        out["constraint_scaling_quality_passed"] =
            diagnostic_bool_or(result, "constraint_scaling_quality_passed", false);
        out["scaled_acceptance_passed"] = diagnostic_bool_or(result, "scaled_acceptance_passed", false);
        out["restoration_phase_observed"] = diagnostic_bool_or(result, "restoration_phase_observed", false);
        out["exact_gradient_required"] = adapter.exact_gradient_required;
        out["exact_jacobian_required"] = adapter.exact_jacobian_required;
        return out;
    },
        py::arg("hessian_mode") = "auto",
        py::arg("option_profile") = "proof",
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
        const py::object& mixture,
        double temperature,
        double target_pressure,
        const std::vector<double>& amounts,
        double volume
    ) {
        const add_args args = native_args_from_mixture_object(mixture, "EOS phase block");
        return eos_phase_block_to_dict(epcsaft::native::equilibrium_nlp::evaluate_eos_phase_block(
            args,
            temperature,
            target_pressure,
            amounts,
            volume
        ));
    });
    m.def("_native_saturation_block", [](
        const py::object& mixture,
        double temperature,
        double log_vapor_density,
        double log_liquid_density,
        double log_saturation_pressure
    ) {
        const add_args args = native_args_from_mixture_object(mixture, "single-component VLE block");
        return single_component_vle_block_to_dict(
            epcsaft::native::equilibrium_nlp::evaluate_single_component_vle_block(
                args,
                temperature,
                log_vapor_density,
                log_liquid_density,
                log_saturation_pressure
            )
        );
    });
    m.def("_native_eos_phase_system", [](
        const py::object& mixture,
        double temperature,
        double target_pressure,
        const std::vector<std::vector<double>>& phase_amounts,
        const std::vector<double>& volumes,
        const std::vector<double>& feed_amounts,
        const std::vector<double>& charges,
        const std::vector<std::vector<double>>& association_site_fractions,
        const std::vector<double>& association_delta_row_major
    ) {
        const add_args args = native_args_from_mixture_object(mixture, "EOS phase system");
        return eos_phase_system_to_dict(epcsaft::native::equilibrium_nlp::evaluate_eos_phase_system(
            args,
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
        const py::object& mixture,
        double temperature,
        double density,
        const std::vector<double>& composition,
        const std::vector<double>& amounts
    ) {
        const add_args args = native_args_from_mixture_object(mixture, "Electrolyte contribution block");
        return electrolyte_contribution_block_to_dict(
            epcsaft::native::equilibrium_nlp::evaluate_electrolyte_contribution_block(
                args,
                temperature,
                density,
                composition,
                amounts
            )
        );
    });
    m.def("_native_neutral_two_phase_eos_nlp_contract", [](
        const py::object& mixture,
        double temperature,
        double target_pressure,
        const std::vector<std::vector<double>>& phase_amounts,
        const std::vector<double>& volumes,
        const std::vector<double>& feed_amounts
    ) {
        const add_args args = native_args_from_mixture_object(mixture, "Neutral two-phase EOS NLP contract");
        return neutral_two_phase_eos_nlp_contract_to_dict(
            epcsaft::native::equilibrium_nlp::evaluate_neutral_two_phase_eos_nlp_contract(
                args,
                temperature,
                target_pressure,
                phase_amounts,
                volumes,
                feed_amounts
            )
        );
    });
    m.def("_native_neutral_multiphase_eos_nlp_contract", [](
        const py::object& mixture,
        double temperature,
        double target_pressure,
        const std::vector<std::vector<double>>& phase_amounts,
        const std::vector<double>& volumes,
        const std::vector<double>& feed_amounts
    ) {
        const add_args args = native_args_from_mixture_object(mixture, "Neutral multiphase EOS NLP contract");
        return neutral_two_phase_eos_nlp_contract_to_dict(
            epcsaft::native::equilibrium_nlp::evaluate_neutral_multiphase_eos_nlp_contract(
                args,
                temperature,
                target_pressure,
                phase_amounts,
                volumes,
                feed_amounts
            )
        );
    });
    m.def("_native_neutral_two_phase_eos_postsolve", [](
        const py::object& mixture,
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
        const add_args args = native_args_from_mixture_object(mixture, "Neutral two-phase EOS postsolve");
        return neutral_two_phase_eos_postsolve_to_dict(
            epcsaft::native::equilibrium_nlp::evaluate_neutral_two_phase_eos_postsolve(
                args,
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
    m.def("_native_neutral_multiphase_eos_postsolve", [](
        const py::object& mixture,
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
    ) {
        const add_args args = native_args_from_mixture_object(mixture, "Neutral multiphase EOS postsolve");
        return neutral_two_phase_eos_postsolve_to_dict(
            epcsaft::native::equilibrium_nlp::evaluate_neutral_multiphase_eos_postsolve(
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
                phase_kinds
            )
        );
    });
    m.def("_native_neutral_tpd_phase_discovery", [](
        const py::object& mixture,
        double temperature,
        double target_pressure,
        const std::vector<double>& feed_composition,
        const std::vector<int>& phase_kinds,
        double tpd_tolerance,
        double candidate_mass_balance_tolerance,
        bool continuous_tpd_required
    ) {
        const add_args args = native_args_from_mixture_object(mixture, "Neutral TPD phase discovery");
        return neutral_phase_discovery_to_dict(
            epcsaft::native::equilibrium_nlp::evaluate_neutral_tpd_phase_discovery(
                args,
                temperature,
                target_pressure,
                feed_composition,
                phase_kinds,
                tpd_tolerance,
                candidate_mass_balance_tolerance,
                continuous_tpd_required
            )
        );
    },
        py::arg("mixture"),
        py::arg("temperature"),
        py::arg("target_pressure"),
        py::arg("feed_composition"),
        py::arg("phase_kinds"),
        py::arg("tpd_tolerance"),
        py::arg("candidate_mass_balance_tolerance"),
        py::arg("continuous_tpd_required") = true
    );
    m.def("_native_neutral_two_phase_eos_result", [](
        const py::object& mixture,
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
        const add_args args = native_args_from_mixture_object(mixture, "Neutral two-phase EOS result builder");
        return neutral_two_phase_eos_result_payload_to_dict(
            epcsaft::native::equilibrium_nlp::build_neutral_two_phase_eos_result(
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
                phase_distance_constraint
            )
        );
    },
        py::arg("mixture"),
        py::arg("temperature"),
        py::arg("target_pressure"),
        py::arg("phase_amounts"),
        py::arg("volumes"),
        py::arg("feed_amounts"),
        py::arg("material_tolerance"),
        py::arg("pressure_tolerance"),
        py::arg("chemical_potential_tolerance"),
        py::arg("phase_distance_tolerance"),
        py::arg("phase_distance_constraint") = true
    );
}
