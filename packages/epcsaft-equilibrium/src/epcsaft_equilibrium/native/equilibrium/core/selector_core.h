#pragma once

#include "equilibrium/core/activation_plan.h"
#include "equilibrium/core/activation_matrix.h"
#include "equilibrium/core/two_phase_eos_route.h"
#include "equilibrium/core/variable_layout.h"

#include <string>
#include <vector>

struct add_args;

namespace epcsaft::native::equilibrium {

struct SelectorInputClassification {
    bool neutral = false;
    bool nonreactive = true;
    bool nonelectrolyte = false;
    bool nonassociating = false;
    std::vector<int> neutral_species_indices;
    std::vector<int> ionic_species_indices;
    std::vector<double> ionic_species_charges;
    std::vector<int> associating_species_indices;
    std::vector<int> reactive_species_indices;
    std::vector<int> phase_eligible_species_indices;
    std::vector<int> transferable_species_indices;
    std::vector<int> fixed_species_indices;
    std::vector<std::string> active_family_markers;
};

struct SelectorRequestPretreatment {
    std::string request_source = "native_selector_payload";
    std::string route;
    std::string composition_role;
    std::string temperature_role;
    std::string pressure_role;
    std::string composition_basis = "mole_fraction";
    std::string feed_amount_basis = "unit_total_moles";
    bool route_shape_validated = false;
    bool finite_numeric_inputs = false;
    int species_count = 0;
    int composition_length = 0;
    double composition_original_sum = 0.0;
    double composition_normalized_sum = 0.0;
    bool composition_was_normalized = false;
    double composition_normalization_tolerance = 1.0e-12;
};

struct SelectorThermodynamicInput {
    double temperature_kelvin = 0.0;
    double pressure_pascal = 0.0;
    double total_amount_basis = 1.0;
    std::string composition_role;
    std::string composition_basis = "mole_fraction";
    std::string amount_basis = "unit_total_moles";
    std::string temperature_role;
    std::string pressure_role;
    std::vector<int> species_indices;
    std::vector<double> normalized_composition;
    std::vector<double> extensive_amounts;
};

struct SelectorParameterReadiness {
    std::string parameter_basis = "add_args";
    std::string parameter_source_label = "runtime_payload";
    std::string parameter_provenance_status = "runtime_payload_without_source_provenance";
    std::string binary_interaction_provenance_status = "runtime_payload_binary_matrix";
    bool pure_neutral_parameters_present = false;
    bool binary_interaction_matrix_present = false;
    bool source_backed_parameter_provenance_present = false;
    bool explicit_zero_binary_interaction_convention = false;
    bool association_parameters_active = false;
    bool electrolyte_parameters_active = false;
    bool born_terms_active = false;
    bool required_parameter_families_present = false;
    std::vector<std::string> required_parameter_families;
    std::vector<std::string> missing_required_parameter_families;
    std::vector<std::string> active_residual_families;
    std::vector<std::string> parameter_provenance_fields;
    std::string derivative_gate;
    std::string associating_admission_proof_route;
    std::string associating_admission_fixture;
    std::string associating_admission_backend;
};

struct SelectorRouteRequest {
    std::string route;
    bool has_temperature = false;
    bool has_pressure = false;
    double temperature = 0.0;
    double pressure = 0.0;
    std::vector<double> composition;
    std::string composition_role;
    std::vector<std::string> phase_kinds;
};

struct SelectorContract {
    std::string selector_family;
    std::string route;
    std::string composition_role;
    std::vector<std::string> phase_labels;
    std::vector<std::string> phase_roles;
    bool specified_temperature = false;
    bool specified_pressure = false;
    bool production_exposed = false;
    bool certification_required = false;
    bool density_closure_required = false;
    bool exact_derivatives_required = false;
    SelectorRequestPretreatment request_pretreatment;
    SelectorThermodynamicInput thermodynamic_input;
    SelectorParameterReadiness parameter_readiness;
    SelectorInputClassification input_classification;
    ProblemFamilyActivation activation;
    bool has_activation_plan = false;
    ActivationPlan activation_plan;
    VariableLayout variable_layout;
    epcsaft::native::equilibrium_nlp::NeutralTwoPhaseEosNlpContract nlp_contract;
};

SelectorContract evaluate_selector_contract(
    const add_args& args,
    const SelectorRouteRequest& request
);

epcsaft::native::equilibrium_nlp::NeutralTwoPhaseEosRouteResult solve_selector_route(
    const add_args& args,
    const SelectorRouteRequest& request,
    const epcsaft::native::equilibrium_nlp::IpoptSolveOptions& options,
    double phase_total_tolerance,
    double pressure_tolerance,
    double chemical_potential_tolerance,
    double phase_distance_tolerance
);

}  // namespace epcsaft::native::equilibrium
