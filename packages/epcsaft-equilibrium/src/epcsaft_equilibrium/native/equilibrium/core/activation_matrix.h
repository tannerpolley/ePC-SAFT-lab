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
};

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
            true,
            "production_exposed",
            {"material_balance", "phase_pressure_consistency", "phase_equilibrium", "phase_distance"},
            {
                "material_balance",
                "phase_pressure_consistency",
                "phase_equilibrium",
                "phase_volume_gap",
            },
            {"neutral_tp_flash_hydrocarbon_ipopt_exact_hessian"},
            {"flash"},
            "phase_species_amounts_plus_phase_volume",
            "explicit_phase_volume_pressure_constraint",
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
            true,
            "production_exposed",
            {"material_balance", "phase_pressure_consistency", "phase_equilibrium", "phase_distance"},
            {"material_balance", "phase_pressure_consistency", "phase_distance"},
            {"neutral_lle_binary_nonassociating_ipopt_exact_hessian"},
            {"lle"},
            "phase_species_amounts_plus_phase_volume",
            "explicit_phase_volume_pressure_constraint",
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
            true,
            "production_exposed",
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
            {"single_component_vle_ethane_ipopt_exact_hessian"},
            {"single_component_vle"},
            "phase_species_amounts_plus_phase_volume_plus_route_scalar",
            "explicit_phase_volume_pressure_constraint",
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
            {"reaction_stationarity"},
            {"conserved_balance", "reaction_stationarity", "phase_charge"},
            {},
            {},
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
            true,
            "production_exposed",
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
            {"neutral_bubble_pressure_hydrocarbon_ipopt_exact_hessian"},
            {"bubble_pressure", "bubble_temperature", "dew_pressure", "dew_temperature"},
            "phase_species_amounts_plus_phase_volume_plus_route_scalar",
            "explicit_phase_volume_pressure_constraint",
        },
    };
    return matrix;
}

}  // namespace epcsaft::native::equilibrium
