#include "equilibrium/core/selector_core.h"

#include "model/native_types.h"

#include <algorithm>
#include <cmath>

namespace epcsaft::native::equilibrium {
namespace {

const ProblemFamilyActivation& bubble_dew_activation() {
    const auto& matrix = problem_family_activation_matrix();
    const auto found = std::find_if(
        matrix.begin(),
        matrix.end(),
        [](const ProblemFamilyActivation& row) { return row.key == "bubble_dew_derived_routes"; }
    );
    if (found == matrix.end()) {
        throw ValueError("selector-ineligible: bubble_dew_derived_routes activation row is missing.");
    }
    return *found;
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

void require_production_route(const std::string& route) {
    if (route == "bubble_pressure") {
        return;
    }
    throw ValueError("selector-ineligible: route family is declared-not-exposed or unsupported by the production selector.");
}

void require_eligible_input(const SelectorInputClassification& classification) {
    if (classification.neutral && classification.nonreactive && classification.nonelectrolyte
        && classification.nonassociating) {
        return;
    }
    throw ValueError(
        "selector-ineligible: bubble_pressure supports only neutral, non-reactive, non-electrolyte, "
        "non-associating mixtures."
    );
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

}  // namespace

// AlgID: bubble_dew_ipopt
SelectorContract evaluate_selector_contract(
    const add_args& args,
    const std::string& route,
    double scalar,
    const std::vector<double>& composition
) {
    require_production_route(route);
    SelectorContract out;
    out.selector_family = "bubble_dew_derived_routes";
    out.route = route;
    out.activation = bubble_dew_activation();
    out.input_classification = classify_selector_input(args);
    require_eligible_input(out.input_classification);
    out.production_exposed = out.activation.production_exposed;
    out.certification_required = out.activation.postsolve_certification == "on";
    out.density_closure_required = true;
    out.exact_derivatives_required = exact_derivatives_required(out.activation);
    out.nlp_contract = epcsaft::native::equilibrium_nlp::evaluate_neutral_bubble_p_eos_nlp_contract(
        args,
        scalar,
        composition
    );
    require_contract_matches_activation(out.nlp_contract, out.activation);
    return out;
}

// AlgID: bubble_dew_ipopt
epcsaft::native::equilibrium_nlp::NeutralTwoPhaseEosRouteResult solve_selector_route(
    const add_args& args,
    const std::string& route,
    double scalar,
    const std::vector<double>& composition,
    const epcsaft::native::equilibrium_nlp::IpoptSolveOptions& options,
    double phase_total_tolerance,
    double pressure_tolerance,
    double chemical_potential_tolerance,
    double phase_distance_tolerance
) {
    const SelectorContract contract = evaluate_selector_contract(args, route, scalar, composition);
    if (!contract.production_exposed || !contract.certification_required || !contract.exact_derivatives_required) {
        throw ValueError("selector-ineligible: activation row is not production certified.");
    }
    epcsaft::native::equilibrium_nlp::NeutralTwoPhaseEosRouteResult result =
        epcsaft::native::equilibrium_nlp::solve_neutral_bubble_p_eos_route(
            args,
            scalar,
            composition,
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
