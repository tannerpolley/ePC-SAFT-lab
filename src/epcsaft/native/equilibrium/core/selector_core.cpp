#include "equilibrium/core/selector_core.h"

#include "model/native_types.h"

#include <algorithm>
#include <cmath>
#include <cctype>

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

bool no_association_sites(const add_args& args) {
    return std::all_of(args.assoc_num.begin(), args.assoc_num.end(), [](int value) { return value == 0; })
        && args.assoc_matrix.empty()
        && args.k_hb.empty()
        && args.e_assoc.empty()
        && args.vol_a.empty();
}

SelectorInputClassification classify_selector_input(const add_args& args) {
    SelectorInputClassification out;
    out.nonelectrolyte = all_zero_or_empty(args.z);
    out.neutral = out.nonelectrolyte;
    out.nonassociating = no_association_sites(args);
    out.nonreactive = true;
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
    out.input_classification = classify_selector_input(args);
    require_eligible_input(out.input_classification);
    out.production_exposed = out.activation.production_exposed;
    out.certification_required = out.activation.postsolve_certification == "on";
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
