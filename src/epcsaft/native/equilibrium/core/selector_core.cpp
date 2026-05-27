#include "equilibrium/core/selector_core.h"

#include "model/native_types.h"

#include <algorithm>
#include <cmath>
#include <cctype>
#include <numeric>
#include <sstream>

namespace epcsaft::native::equilibrium {
namespace {

std::string normalized_token(std::string value) {
    std::transform(value.begin(), value.end(), value.begin(), [](unsigned char ch) {
        return static_cast<char>(std::tolower(ch));
    });
    return value;
}

const ProblemFamilyActivation& activation_row(const std::string& key) {
    const auto& matrix = problem_family_activation_matrix();
    const auto found = std::find_if(
        matrix.begin(),
        matrix.end(),
        [&](const ProblemFamilyActivation& row) { return row.key == key; }
    );
    if (found == matrix.end()) {
        throw ValueError("selector-ineligible: activation row is missing for " + key + ".");
    }
    return *found;
}

std::string selector_family_for_route(const std::string& route) {
    if (route == "bubble_pressure" || route == "bubble_temperature" || route == "dew_pressure"
        || route == "dew_temperature") {
        return "bubble_dew_derived_routes";
    }
    if (route == "neutral_tp_flash") {
        return "neutral_tp_flash";
    }
    if (route == "neutral_lle") {
        return "neutral_lle";
    }
    throw ValueError("selector-ineligible: route family is declared-not-exposed or unsupported by the production selector.");
}

bool all_zero_or_empty(const std::vector<double>& values) {
    return std::all_of(values.begin(), values.end(), [](double value) {
        return std::isfinite(value) && std::abs(value) <= 1.0e-12;
    });
}

std::vector<int> all_species_indices(std::size_t count) {
    std::vector<int> out(count, 0);
    std::iota(out.begin(), out.end(), 0);
    return out;
}

bool no_association_sites(const add_args& args) {
    return std::all_of(args.assoc_num.begin(), args.assoc_num.end(), [](int value) { return value == 0; })
        && args.assoc_matrix.empty()
        && all_zero_or_empty(args.k_hb)
        && all_zero_or_empty(args.e_assoc)
        && all_zero_or_empty(args.vol_a);
}

bool active_association_for_species(const add_args& args, std::size_t species) {
    if (species < args.assoc_num.size() && args.assoc_num[species] > 0) {
        return true;
    }
    if (species < args.e_assoc.size() && std::isfinite(args.e_assoc[species]) && args.e_assoc[species] != 0.0) {
        return true;
    }
    if (species < args.vol_a.size() && std::isfinite(args.vol_a[species]) && args.vol_a[species] != 0.0) {
        return true;
    }
    return false;
}

SelectorInputClassification classify_selector_input(const add_args& args) {
    SelectorInputClassification out;
    const std::size_t species_count = args.m.size();
    out.phase_eligible_species_indices = all_species_indices(species_count);
    out.transferable_species_indices = out.phase_eligible_species_indices;
    for (std::size_t species = 0; species < species_count; ++species) {
        const double charge = species < args.z.size() ? args.z[species] : 0.0;
        if (std::isfinite(charge) && std::abs(charge) > 1.0e-12) {
            out.ionic_species_indices.push_back(static_cast<int>(species));
            out.ionic_species_charges.push_back(charge);
        } else {
            out.neutral_species_indices.push_back(static_cast<int>(species));
        }
        if (active_association_for_species(args, species)) {
            out.associating_species_indices.push_back(static_cast<int>(species));
        }
    }
    out.nonelectrolyte = out.ionic_species_indices.empty() && all_zero_or_empty(args.z);
    out.nonassociating = no_association_sites(args);
    out.nonreactive = true;
    out.neutral = out.nonelectrolyte && out.nonassociating && out.nonreactive;
    if (out.neutral) {
        out.active_family_markers.push_back("neutral");
    }
    if (!out.nonelectrolyte) {
        out.active_family_markers.push_back("electrolyte");
    }
    if (!out.nonassociating) {
        out.active_family_markers.push_back("associating");
    }
    if (!out.nonreactive) {
        out.active_family_markers.push_back("reactive");
    }
    if (out.nonreactive) {
        out.active_family_markers.push_back("nonreactive");
    }
    return out;
}

void require_eligible_input(const SelectorInputClassification& classification) {
    if (classification.neutral && classification.nonreactive && classification.nonelectrolyte
        && classification.nonassociating) {
        return;
    }
    throw ValueError(
        "selector-ineligible: production selector routes support only neutral, non-reactive, "
        "non-electrolyte, non-associating mixtures."
    );
}

void require_positive_finite(double value, const std::string& label) {
    if (std::isfinite(value) && value > 0.0) {
        return;
    }
    throw ValueError("selector-ineligible: " + label + " must be positive and finite.");
}

void require_composition(const add_args& args, const std::vector<double>& composition) {
    const std::size_t expected = args.m.size();
    if (composition.size() != expected) {
        throw ValueError("selector-ineligible: composition length must match mixture component count.");
    }
    double total = 0.0;
    for (double value : composition) {
        require_positive_finite(value, "composition value");
        total += value;
    }
    require_positive_finite(total, "composition total");
}

std::vector<double> normalized_composition(const std::vector<double>& composition) {
    const double total = std::accumulate(composition.begin(), composition.end(), 0.0);
    require_positive_finite(total, "composition total");
    std::vector<double> out;
    out.reserve(composition.size());
    for (double value : composition) {
        out.push_back(value / total);
    }
    return out;
}

std::string temperature_role_for_route(const SelectorRouteRequest& request) {
    if (request.route == "bubble_temperature" || request.route == "dew_temperature") {
        return "solved_boundary_temperature";
    }
    return request.has_temperature ? "fixed_temperature" : "not_specified";
}

std::string pressure_role_for_route(const SelectorRouteRequest& request) {
    if (request.route == "bubble_pressure" || request.route == "dew_pressure") {
        return "solved_boundary_pressure";
    }
    return request.has_pressure ? "fixed_pressure" : "not_specified";
}

SelectorRequestPretreatment pretreat_selector_request(
    const add_args& args,
    const SelectorRouteRequest& request
) {
    SelectorRequestPretreatment out;
    out.route = request.route;
    out.composition_role = request.composition_role;
    out.temperature_role = temperature_role_for_route(request);
    out.pressure_role = pressure_role_for_route(request);
    out.species_count = static_cast<int>(args.m.size());
    out.composition_length = static_cast<int>(request.composition.size());
    out.composition_original_sum =
        std::accumulate(request.composition.begin(), request.composition.end(), 0.0);
    const std::vector<double> normalized = normalized_composition(request.composition);
    out.composition_normalized_sum = std::accumulate(normalized.begin(), normalized.end(), 0.0);
    out.composition_was_normalized =
        std::abs(out.composition_original_sum - 1.0) > out.composition_normalization_tolerance;
    out.finite_numeric_inputs = std::isfinite(out.composition_original_sum)
        && (!request.has_temperature || std::isfinite(request.temperature))
        && (!request.has_pressure || std::isfinite(request.pressure));
    out.route_shape_validated = true;
    return out;
}

SelectorThermodynamicInput build_thermodynamic_input(
    const add_args& args,
    const SelectorRouteRequest& request
) {
    SelectorThermodynamicInput out;
    out.temperature_kelvin = request.temperature;
    out.pressure_pascal = request.pressure;
    out.composition_role = request.composition_role;
    out.temperature_role = temperature_role_for_route(request);
    out.pressure_role = pressure_role_for_route(request);
    out.species_indices = all_species_indices(args.m.size());
    out.normalized_composition = normalized_composition(request.composition);
    out.extensive_amounts = out.normalized_composition;
    return out;
}

bool positive_finite_vector(const std::vector<double>& values, std::size_t expected) {
    if (values.size() != expected) {
        return false;
    }
    return std::all_of(values.begin(), values.end(), [](double value) {
        return std::isfinite(value) && value > 0.0;
    });
}

bool dense_pair_matrix_present(const std::vector<double>& values, std::size_t species_count) {
    if (species_count <= 1) {
        return true;
    }
    return values.size() == species_count * species_count
        && std::all_of(values.begin(), values.end(), [](double value) { return std::isfinite(value); });
}

bool any_nonzero_finite(const std::vector<double>& values) {
    return std::any_of(values.begin(), values.end(), [](double value) {
        return std::isfinite(value) && std::abs(value) > 1.0e-12;
    });
}

SelectorParameterReadiness evaluate_parameter_readiness(
    const add_args& args,
    const ProblemFamilyActivation& activation
) {
    SelectorParameterReadiness out;
    const std::size_t species_count = args.m.size();
    out.parameter_source_label = args.parameter_source_label;
    out.parameter_provenance_status = args.parameter_provenance_status;
    out.binary_interaction_provenance_status = args.binary_interaction_provenance_status;
    out.parameter_provenance_fields = args.parameter_provenance_fields;
    out.source_backed_parameter_provenance_present =
        args.parameter_provenance_status == "source_backed_parameter_metadata";
    out.required_parameter_families.push_back("pure_neutral_pcsaft");
    if (species_count > 1) {
        out.required_parameter_families.push_back("binary_interaction_matrix");
    }
    out.pure_neutral_parameters_present =
        positive_finite_vector(args.m, species_count)
        && positive_finite_vector(args.s, species_count)
        && positive_finite_vector(args.e, species_count);
    out.binary_interaction_matrix_present = dense_pair_matrix_present(args.k_ij, species_count);
    out.explicit_zero_binary_interaction_convention =
        out.binary_interaction_matrix_present
        && species_count > 1
        && all_zero_or_empty(args.k_ij)
        && args.binary_interaction_provenance_status == "explicit_binary_records"
        && out.source_backed_parameter_provenance_present;
    out.association_parameters_active = !no_association_sites(args);
    out.electrolyte_parameters_active = !all_zero_or_empty(args.z);
    out.born_terms_active = args.include_born_model != 0
        || args.born_model != 0
        || any_nonzero_finite(args.d_born)
        || any_nonzero_finite(args.f_solv);
    out.active_residual_families = activation.residual_families;
    if (!out.pure_neutral_parameters_present) {
        out.missing_required_parameter_families.push_back("pure_neutral_pcsaft");
    }
    if (!out.binary_interaction_matrix_present) {
        out.missing_required_parameter_families.push_back("binary_interaction_matrix");
    } else if (
        species_count > 1
        && all_zero_or_empty(args.k_ij)
        && !out.explicit_zero_binary_interaction_convention
    ) {
        out.missing_required_parameter_families.push_back("source_backed_zero_binary_interaction_convention");
    }
    out.required_parameter_families_present = out.missing_required_parameter_families.empty();
    out.derivative_gate = activation.derivative_requirement;
    return out;
}

void require_parameter_readiness(const SelectorParameterReadiness& readiness) {
    if (readiness.required_parameter_families_present) {
        return;
    }
    std::ostringstream msg;
    msg << "selector-ineligible: missing required parameter families:";
    for (const std::string& family : readiness.missing_required_parameter_families) {
        msg << " " << family;
    }
    msg << ".";
    throw ValueError(msg.str());
}

void require_present(bool present, const std::string& label, const std::string& route) {
    if (present) {
        return;
    }
    throw ValueError("selector-ineligible: " + route + " requires " + label + ".");
}

void require_absent(bool present, const std::string& label, const std::string& route) {
    if (!present) {
        return;
    }
    throw ValueError("selector-ineligible: " + route + " must not specify " + label + ".");
}

void require_role(const SelectorRouteRequest& request, const std::string& expected) {
    if (request.composition_role == expected) {
        return;
    }
    throw ValueError(
        "selector-ineligible: " + request.route + " requires composition_role='" + expected + "'."
    );
}

void require_request_shape(const add_args& args, const SelectorRouteRequest& request) {
    require_composition(args, request.composition);
    if (request.route == "bubble_pressure") {
        require_present(request.has_temperature, "temperature", request.route);
        require_absent(request.has_pressure, "pressure", request.route);
        require_positive_finite(request.temperature, "temperature");
        require_role(request, "liquid");
        return;
    }
    if (request.route == "bubble_temperature") {
        require_absent(request.has_temperature, "temperature", request.route);
        require_present(request.has_pressure, "pressure", request.route);
        require_positive_finite(request.pressure, "pressure");
        require_role(request, "liquid");
        return;
    }
    if (request.route == "dew_pressure") {
        require_present(request.has_temperature, "temperature", request.route);
        require_absent(request.has_pressure, "pressure", request.route);
        require_positive_finite(request.temperature, "temperature");
        require_role(request, "vapor");
        return;
    }
    if (request.route == "dew_temperature") {
        require_absent(request.has_temperature, "temperature", request.route);
        require_present(request.has_pressure, "pressure", request.route);
        require_positive_finite(request.pressure, "pressure");
        require_role(request, "vapor");
        return;
    }
    if (request.route == "neutral_tp_flash" || request.route == "neutral_lle") {
        require_present(request.has_temperature, "temperature", request.route);
        require_present(request.has_pressure, "pressure", request.route);
        require_positive_finite(request.temperature, "temperature");
        require_positive_finite(request.pressure, "pressure");
        require_role(request, "feed");
        return;
    }
    throw ValueError("selector-ineligible: route family is declared-not-exposed or unsupported by the production selector.");
}

bool exact_derivatives_required(const ProblemFamilyActivation& activation) {
    return activation.derivative_requirement == "exact_gradient_jacobian_and_hessian_for_exposed_ipopt_routes";
}

void require_same_text(const std::string& actual, const std::string& expected, const std::string& label) {
    if (actual == expected) {
        return;
    }
    throw ValueError("selector-ineligible: activation metadata mismatch for " + label + ".");
}

void require_same_families(
    const std::vector<std::string>& actual,
    const std::vector<std::string>& expected,
    const std::string& label
) {
    if (actual == expected) {
        return;
    }
    throw ValueError("selector-ineligible: activation metadata mismatch for " + label + ".");
}

void require_contract_matches_activation(
    const epcsaft::native::equilibrium_nlp::NeutralTwoPhaseEosNlpContract& contract,
    const ProblemFamilyActivation& activation
) {
    require_same_text(contract.variable_model, activation.variable_model, "variable_model");
    require_same_text(contract.density_backend, activation.density_backend, "density_backend");
    require_same_families(contract.residual_families, activation.residual_families, "residual_families");
    require_same_families(contract.constraint_families, activation.constraint_families, "constraint_families");
}

void require_result_matches_activation(
    const epcsaft::native::equilibrium_nlp::NeutralTwoPhaseEosRouteResult& result,
    const ProblemFamilyActivation& activation
) {
    if (result.variable_model != activation.variable_model
        || result.density_backend != activation.density_backend
        || result.residual_families != activation.residual_families
        || result.constraint_families != activation.constraint_families) {
        throw SolutionError("selector-certification: route result metadata diverged from activation matrix.");
    }
}

epcsaft::native::equilibrium_nlp::NeutralTwoPhaseEosNlpContract evaluate_route_contract(
    const add_args& args,
    const SelectorRouteRequest& request
) {
    if (request.route == "bubble_pressure") {
        return epcsaft::native::equilibrium_nlp::evaluate_neutral_bubble_p_eos_nlp_contract(
            args,
            request.temperature,
            request.composition
        );
    }
    if (request.route == "bubble_temperature") {
        return epcsaft::native::equilibrium_nlp::evaluate_neutral_bubble_t_eos_nlp_contract(
            args,
            request.pressure,
            request.composition
        );
    }
    if (request.route == "dew_pressure") {
        return epcsaft::native::equilibrium_nlp::evaluate_neutral_dew_p_eos_nlp_contract(
            args,
            request.temperature,
            request.composition
        );
    }
    if (request.route == "dew_temperature") {
        return epcsaft::native::equilibrium_nlp::evaluate_neutral_dew_t_eos_nlp_contract(
            args,
            request.pressure,
            request.composition
        );
    }
    if (request.route == "neutral_tp_flash") {
        return epcsaft::native::equilibrium_nlp::evaluate_neutral_tp_flash_eos_nlp_contract(
            args,
            request.temperature,
            request.pressure,
            request.composition
        );
    }
    if (request.route == "neutral_lle") {
        const ActivationPlan plan = build_activation_plan(args, request);
        const VariableLayout layout = build_variable_layout(plan, static_cast<int>(args.m.size()));
        return epcsaft::native::equilibrium_nlp::evaluate_activated_neutral_lle_nlp_contract(
            args,
            plan,
            layout
        );
    }
    throw ValueError("selector-ineligible: route family is declared-not-exposed or unsupported by the production selector.");
}

epcsaft::native::equilibrium_nlp::NeutralTwoPhaseEosRouteResult solve_route(
    const add_args& args,
    const SelectorRouteRequest& request,
    const epcsaft::native::equilibrium_nlp::IpoptSolveOptions& options,
    double phase_total_tolerance,
    double pressure_tolerance,
    double chemical_potential_tolerance,
    double phase_distance_tolerance
) {
    if (request.route == "bubble_pressure") {
        return epcsaft::native::equilibrium_nlp::solve_neutral_bubble_p_eos_route(
            args,
            request.temperature,
            request.composition,
            options,
            phase_total_tolerance,
            pressure_tolerance,
            chemical_potential_tolerance,
            phase_distance_tolerance
        );
    }
    if (request.route == "bubble_temperature") {
        return epcsaft::native::equilibrium_nlp::solve_neutral_bubble_t_eos_route(
            args,
            request.pressure,
            request.composition,
            options,
            phase_total_tolerance,
            pressure_tolerance,
            chemical_potential_tolerance,
            phase_distance_tolerance
        );
    }
    if (request.route == "dew_pressure") {
        return epcsaft::native::equilibrium_nlp::solve_neutral_dew_p_eos_route(
            args,
            request.temperature,
            request.composition,
            options,
            phase_total_tolerance,
            pressure_tolerance,
            chemical_potential_tolerance,
            phase_distance_tolerance
        );
    }
    if (request.route == "dew_temperature") {
        return epcsaft::native::equilibrium_nlp::solve_neutral_dew_t_eos_route(
            args,
            request.pressure,
            request.composition,
            options,
            phase_total_tolerance,
            pressure_tolerance,
            chemical_potential_tolerance,
            phase_distance_tolerance
        );
    }
    if (request.route == "neutral_tp_flash") {
        return epcsaft::native::equilibrium_nlp::solve_activated_neutral_tp_flash_eos_route(
            args,
            request.temperature,
            request.pressure,
            request.composition,
            options,
            phase_total_tolerance,
            pressure_tolerance,
            chemical_potential_tolerance,
            phase_distance_tolerance
        );
    }
    if (request.route == "neutral_lle") {
        return epcsaft::native::equilibrium_nlp::solve_activated_neutral_lle_eos_route(
            args,
            request.temperature,
            request.pressure,
            request.composition,
            options,
            phase_total_tolerance,
            pressure_tolerance,
            chemical_potential_tolerance,
            phase_distance_tolerance
        );
    }
    throw ValueError("selector-ineligible: route family is declared-not-exposed or unsupported by the production selector.");
}

}  // namespace

// AlgID: bubble_dew_ipopt
SelectorContract evaluate_selector_contract(
    const add_args& args,
    const SelectorRouteRequest& raw_request
) {
    SelectorRouteRequest request = raw_request;
    request.route = normalized_token(request.route);
    request.composition_role = normalized_token(request.composition_role);
    const std::string family = selector_family_for_route(request.route);
    const ProblemFamilyActivation& activation = activation_row(family);
    if (!activation.production_exposed || activation.exposure_status != "production_exposed") {
        throw ValueError("selector-ineligible: activation row is not production exposed.");
    }
    require_request_shape(args, request);

    SelectorContract out;
    out.selector_family = family;
    out.route = request.route;
    out.composition_role = request.composition_role;
    out.specified_temperature = request.has_temperature;
    out.specified_pressure = request.has_pressure;
    out.activation = activation;
    out.request_pretreatment = pretreat_selector_request(args, request);
    out.thermodynamic_input = build_thermodynamic_input(args, request);
    out.parameter_readiness = evaluate_parameter_readiness(args, out.activation);
    require_parameter_readiness(out.parameter_readiness);
    out.input_classification = classify_selector_input(args);
    require_eligible_input(out.input_classification);
    out.production_exposed = out.activation.production_exposed;
    out.certification_required = out.activation.postsolve_certification == "on"
        || out.activation.postsolve_certification == "tpd_postsolve";
    out.density_closure_required = true;
    out.exact_derivatives_required = exact_derivatives_required(out.activation);
    if (request.route == "neutral_tp_flash" || request.route == "neutral_lle") {
        out.has_activation_plan = true;
        out.activation_plan = build_activation_plan(args, request);
        out.variable_layout = build_variable_layout(
            out.activation_plan,
            static_cast<int>(args.m.size())
        );
        out.nlp_contract = request.route == "neutral_lle"
            ? epcsaft::native::equilibrium_nlp::evaluate_activated_neutral_lle_nlp_contract(
                args,
                out.activation_plan,
                out.variable_layout
            )
            : epcsaft::native::equilibrium_nlp::evaluate_activated_neutral_tp_flash_nlp_contract(
                args,
                out.activation_plan,
                out.variable_layout
            );
    } else {
        out.nlp_contract = evaluate_route_contract(args, request);
    }
    require_contract_matches_activation(out.nlp_contract, out.activation);
    return out;
}

// AlgID: bubble_dew_ipopt
epcsaft::native::equilibrium_nlp::NeutralTwoPhaseEosRouteResult solve_selector_route(
    const add_args& args,
    const SelectorRouteRequest& raw_request,
    const epcsaft::native::equilibrium_nlp::IpoptSolveOptions& options,
    double phase_total_tolerance,
    double pressure_tolerance,
    double chemical_potential_tolerance,
    double phase_distance_tolerance
) {
    SelectorRouteRequest request = raw_request;
    request.route = normalized_token(request.route);
    request.composition_role = normalized_token(request.composition_role);
    const SelectorContract contract = evaluate_selector_contract(args, request);
    if (!contract.production_exposed || !contract.certification_required || !contract.exact_derivatives_required) {
        throw ValueError("selector-ineligible: activation row is not production certified.");
    }
    epcsaft::native::equilibrium_nlp::NeutralTwoPhaseEosRouteResult result = solve_route(
        args,
        request,
        options,
        phase_total_tolerance,
        pressure_tolerance,
        chemical_potential_tolerance,
        phase_distance_tolerance
    );
    require_result_matches_activation(result, contract.activation);
    return result;
}

}  // namespace epcsaft::native::equilibrium
