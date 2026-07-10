#pragma once

#include <string>
#include <vector>

namespace epcsaft::native::equilibrium {

struct ProblemFamilyActivation {
    std::string key;
    std::string display_name;
    std::string direct_transfer;
    std::string reaction_equilibrium;
    std::string conservation_basis;
    std::string phase_charge;
    std::string split_variables;
    std::string stability_prelayer;
    std::string postsolve_certification;
    std::string derivative_requirement;
    bool production_exposed = false;
    std::string exposure_status;
    std::vector<std::string> residual_families;
    std::vector<std::string> constraint_families;
    std::vector<std::string> proof_routes;
    std::vector<std::string> public_routes;
    std::string variable_model;
    std::string density_backend;
    std::string solver_strategy;
    std::string initialization_strategy;
    std::string continuation_strategy;
    std::string final_proof_policy;
};

struct SelectorRouteActivation {
    std::string selector_route;
    std::string public_route;
    std::string selector_family;
    bool production_exposed = false;
    std::vector<std::string> proof_routes;
};

inline const std::vector<SelectorRouteActivation>& selector_route_activation_matrix() {
    static const std::vector<SelectorRouteActivation> matrix = {
        {
            "bubble_pressure",
            "bubble_pressure",
            "bubble_dew_derived_routes",
            true,
            {
                "associating_neutral_vle_gross_2002_bubble_pressure_figures_2_9_"
                "public_exact_hessian",
            },
        },
        {
            "bubble_temperature",
            "bubble_temperature",
            "bubble_dew_derived_routes",
            false,
            {},
        },
        {
            "dew_pressure",
            "dew_pressure",
            "bubble_dew_derived_routes",
            true,
            {
                "associating_neutral_vle_gross_2002_dew_pressure_figures_2_9_"
                "public_exact_hessian",
            },
        },
        {
            "dew_temperature",
            "dew_temperature",
            "bubble_dew_derived_routes",
            false,
            {},
        },
        {
            "neutral_tp_flash",
            "flash",
            "neutral_tp_flash",
            false,
            {},
        },
        {
            "neutral_lle",
            "lle",
            "neutral_lle",
            false,
            {},
        },
        {
            "single_component_vle",
            "single_component_vle",
            "single_component_vle",
            true,
            {"single_component_vle_hydrocarbon_nist_saturation_exact_hessian"},
        },
    };
    return matrix;
}

inline std::vector<std::string> selector_public_routes_for_family(
    const std::string& selector_family) {
    std::vector<std::string> routes;
    for (const auto& route : selector_route_activation_matrix()) {
        if (route.selector_family == selector_family && route.production_exposed) {
            routes.push_back(route.public_route);
        }
    }
    return routes;
}

inline std::vector<std::string> selector_proof_routes_for_family(
    const std::string& selector_family) {
    std::vector<std::string> proof_routes;
    for (const auto& route : selector_route_activation_matrix()) {
        if (route.selector_family != selector_family || !route.production_exposed) {
            continue;
        }
        proof_routes.insert(
            proof_routes.end(), route.proof_routes.begin(), route.proof_routes.end());
    }
    return proof_routes;
}

inline bool selector_family_production_exposed(const std::string& selector_family) {
    for (const auto& route : selector_route_activation_matrix()) {
        if (route.selector_family == selector_family && route.production_exposed) {
            return true;
        }
    }
    return false;
}

inline std::string selector_family_exposure_status(const std::string& selector_family) {
    return selector_family_production_exposed(selector_family) ? "production_exposed"
                                                                : "declared_not_exposed";
}

inline const std::vector<ProblemFamilyActivation>& problem_family_activation_matrix() {
    static const std::vector<ProblemFamilyActivation> matrix = {
        {
            "neutral_tp_flash",
            "Neutral TP flash",
            "on",
            "off",
            "species",
            "off",
            "on",
            "deterministic_tpd_candidate_screening",
            "tpd_postsolve",
            "exact_gradient_jacobian_and_hessian_for_exposed_ipopt_routes",
            selector_family_production_exposed("neutral_tp_flash"),
            selector_family_exposure_status("neutral_tp_flash"),
            {"material_balance", "phase_pressure_consistency", "phase_equilibrium", "phase_distance"},
            {
                "material_balance",
                "phase_pressure_consistency",
                "phase_equilibrium",
                "phase_volume_gap",
            },
            selector_proof_routes_for_family("neutral_tp_flash"),
            selector_public_routes_for_family("neutral_tp_flash"),
            "phase_species_amounts_plus_phase_volume",
            "explicit_phase_volume_pressure_constraint",
            {},
            {},
            {},
            {},
        },
        {
            "neutral_lle",
            "Neutral LLE",
            "on",
            "off",
            "species",
            "off",
            "on",
            "deterministic_tpd_candidate_screening",
            "tpd_postsolve",
            "exact_gradient_jacobian_and_hessian_for_exposed_ipopt_routes",
            selector_family_production_exposed("neutral_lle"),
            selector_family_exposure_status("neutral_lle"),
            {"material_balance", "phase_pressure_consistency", "phase_equilibrium", "phase_distance"},
            {"material_balance", "phase_pressure_consistency", "phase_distance"},
            selector_proof_routes_for_family("neutral_lle"),
            selector_public_routes_for_family("neutral_lle"),
            "phase_species_amounts_plus_phase_volume",
            "explicit_phase_volume_pressure_constraint",
            {},
            {},
            {},
            {},
        },
        {
            "single_component_vle",
            "Single-component VLE",
            "on",
            "off",
            "species",
            "off",
            "on",
            "postsolve_local_only",
            "on",
            "exact_gradient_jacobian_and_hessian_for_exposed_ipopt_routes",
            selector_family_production_exposed("single_component_vle"),
            selector_family_exposure_status("single_component_vle"),
            {
                "fixed_composition",
                "phase_amount_total",
                "phase_pressure_consistency",
                "phase_equilibrium",
                "phase_distance",
            },
            {
                "fixed_composition",
                "phase_amount_total",
                "phase_pressure_consistency",
                "phase_equilibrium",
                "phase_volume_gap",
            },
            selector_proof_routes_for_family("single_component_vle"),
            selector_public_routes_for_family("single_component_vle"),
            "phase_species_amounts_plus_phase_volume_plus_route_scalar",
            "explicit_phase_volume_pressure_constraint",
            {},
            {},
            {},
            {},
        },
        {
            "neutral_multiphase_nonassoc",
            "Neutral multiphase nonassociating",
            "on",
            "off",
            "species",
            "off",
            "on",
            "deterministic_tpd_candidate_screening",
            "tpd_postsolve",
            "exact_gradient_jacobian_and_hessian_for_exposed_ipopt_routes",
            false,
            "declared_not_exposed",
            {"material_balance", "phase_pressure_consistency", "phase_equilibrium", "phase_distance"},
            {"material_balance", "phase_pressure_consistency"},
            {},
            {},
            "phase_species_amounts_plus_phase_volume",
            "explicit_phase_volume_pressure_constraint",
            {},
            {},
            {},
            {},
        },
        {
            "electrolyte_lle",
            "Electrolyte LLE",
            "on_for_transferable_species",
            "off_unless_chemistry_is_modeled",
            "species_or_salt_solvent_lift_with_exact_back_lift",
            "on",
            "on",
            "on",
            "on",
            "exact_gradient_jacobian_and_hessian_for_exposed_ipopt_routes",
            false,
            "declared_not_exposed",
            {"phase_equilibrium", "material_balance", "phase_charge"},
            {"phase_equilibrium", "phase_pressure_consistency", "phase_distance", "formula_feasibility", "phase_charge"},
            {},
            {},
            "counterion_pair_reduced_phase_amounts_plus_phase_volume",
            "native_electrolyte_postsolve_certification",
            {},
            {},
            {},
            {},
        },
        {
            "reactive_speciation",
            "Reactive speciation",
            "off",
            "on",
            "element_or_moiety",
            "on_when_ionic",
            "off",
            "optional",
            "on",
            "exact_gradient_jacobian_and_hessian_for_exposed_ipopt_routes",
            false,
            "declared_not_exposed",
            {"conserved_balance", "reaction_stationarity"},
            {"conserved_balance"},
            {},
            {},
            "single_phase_species_amounts",
            "homogeneous_standard_state_activity",
            "ipopt_nlp_with_internal_continuation",
            "max_min_feasible_interior",
            "adaptive_k_scaling_homotopy",
            "true_gibbs_lambda_1_only",
        },
        {
            "reactive_lle",
            "Reactive LLE",
            "on_for_shared_species",
            "on",
            "element_or_moiety",
            "optional",
            "on",
            "on",
            "on",
            "exact_gradient_jacobian_and_hessian_for_exposed_ipopt_routes",
            false,
            "declared_not_exposed",
            {"conserved_balance", "reaction_stationarity", "phase_equilibrium"},
            {"conserved_balance", "reaction_stationarity", "phase_pressure_consistency", "phase_distance"},
            {},
            {},
            {},
            {},
            {},
            {},
            {},
            {},
        },
        {
            "reactive_electrolyte_lle",
            "Reactive electrolyte LLE",
            "on_for_shared_species",
            "on_including_cross_phase_reactions",
            "element_or_moiety",
            "on",
            "on",
            "on",
            "on",
            "exact_gradient_jacobian_and_hessian_for_exposed_ipopt_routes",
            false,
            "declared_not_exposed",
            {"conserved_balance", "reaction_stationarity", "phase_equilibrium", "phase_charge"},
            {
                "conserved_balance",
                "reaction_stationarity",
                "phase_pressure_consistency",
                "phase_distance",
                "phase_charge",
            },
            {},
            {},
            {},
            {},
            {},
            {},
            {},
            {},
        },
        {
            "bubble_dew_derived_routes",
            "Bubble/dew derived routes",
            "on",
            "off_unless_reactive_route_is_explicitly_modeled",
            "species_or_element_moiety",
            "optional",
            "one_phase_amount_removed_by_spec",
            "on",
            "on",
            "exact_gradient_jacobian_and_hessian_for_exposed_ipopt_routes",
            selector_family_production_exposed("bubble_dew_derived_routes"),
            selector_family_exposure_status("bubble_dew_derived_routes"),
            {
                "fixed_composition",
                "phase_amount_total",
                "phase_pressure_consistency",
                "phase_equilibrium",
                "phase_distance",
            },
            {
                "fixed_composition",
                "phase_amount_total",
                "phase_pressure_consistency",
                "phase_equilibrium",
                "phase_volume_gap",
            },
            selector_proof_routes_for_family("bubble_dew_derived_routes"),
            selector_public_routes_for_family("bubble_dew_derived_routes"),
            "phase_species_amounts_plus_phase_volume_plus_route_scalar",
            "explicit_phase_volume_pressure_constraint",
            {},
            {},
            {},
            {},
        },
    };
    return matrix;
}

}  // namespace epcsaft::native::equilibrium
