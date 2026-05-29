from __future__ import annotations

import pytest

import epcsaft._core as _core
from epcsaft.frontend import Mixture
from epcsaft.model.parameters import BinaryRecord, ParameterSet, PureRecord
from epcsaft.state.native_adapter import ePCSAFTMixture
from equilibrium_support.equilibrium_cases import (
    _ionic_mixture,
    _methanol_cyclohexane_mixture,
    _neutral_binary_mixture,
    _nonideal_lle_binary_mixture,
)


@pytest.mark.parametrize(
    (
        "selector_request",
        "family",
        "problem_name",
        "composition_role",
        "phase_labels",
        "phase_roles",
        "specified_temperature",
        "specified_pressure",
    ),
    [
        (
            {
                "route": "bubble_pressure",
                "temperature": 300.0,
                "composition": [0.35, 0.65],
                "composition_role": "liquid",
            },
            "bubble_dew_derived_routes",
            "neutral_bubble_p_eos",
            "liquid",
            ["liquid", "vapor"],
            ["liquid", "vapor"],
            True,
            False,
        ),
        (
            {
                "route": "bubble_temperature",
                "pressure": 1.0e6,
                "composition": [0.35, 0.65],
                "composition_role": "liquid",
            },
            "bubble_dew_derived_routes",
            "neutral_bubble_t_eos",
            "liquid",
            ["liquid", "vapor"],
            ["liquid", "vapor"],
            False,
            True,
        ),
        (
            {
                "route": "dew_pressure",
                "temperature": 300.0,
                "composition": [0.35, 0.65],
                "composition_role": "vapor",
            },
            "bubble_dew_derived_routes",
            "neutral_dew_p_eos",
            "vapor",
            ["liquid", "vapor"],
            ["liquid", "vapor"],
            True,
            False,
        ),
        (
            {
                "route": "dew_temperature",
                "pressure": 1.0e6,
                "composition": [0.35, 0.65],
                "composition_role": "vapor",
            },
            "bubble_dew_derived_routes",
            "neutral_dew_t_eos",
            "vapor",
            ["liquid", "vapor"],
            ["liquid", "vapor"],
            False,
            True,
        ),
        (
            {
                "route": "neutral_tp_flash",
                "temperature": 300.0,
                "pressure": 1.0e6,
                "composition": [0.35, 0.65],
                "composition_role": "feed",
            },
            "neutral_tp_flash",
            "neutral_tp_flash_eos",
            "feed",
            ["liquid", "vapor"],
            ["liquid", "vapor"],
            True,
            True,
        ),
        (
            {
                "route": "neutral_lle",
                "temperature": 300.0,
                "pressure": 1.0e6,
                "composition": [0.5, 0.5],
                "composition_role": "feed",
            },
            "neutral_lle",
            "neutral_lle_eos",
            "feed",
            ["liquid1", "liquid2"],
            ["liquid", "liquid"],
            True,
            True,
        ),
    ],
)
def test_selector_core_contract_owns_production_vle_metadata(
    selector_request: dict[str, object],
    family: str,
    problem_name: str,
    composition_role: str,
    phase_labels: list[str],
    phase_roles: list[str],
    specified_temperature: bool,
    specified_pressure: bool,
) -> None:
    mix = _nonideal_lle_binary_mixture() if selector_request["route"] == "neutral_lle" else _neutral_binary_mixture()
    payload = _core._native_equilibrium_selector_contract(mix._native, selector_request)
    matrix = {row["key"]: row for row in _core._native_equilibrium_activation_matrix()}
    activation = matrix[family]

    assert payload["selector_family"] == family
    assert payload["route"] == selector_request["route"]
    assert payload["problem_name"] == problem_name
    assert payload["composition_role"] == composition_role
    assert payload["phase_labels"] == phase_labels
    assert payload["phase_roles"] == phase_roles
    assert payload["specified_temperature"] is specified_temperature
    assert payload["specified_pressure"] is specified_pressure
    assert payload["production_exposed"] is True
    assert payload["certification_required"] is True
    assert payload["density_closure_required"] is True
    assert payload["exact_derivatives_required"] is True
    classification = payload["input_classification"]
    assert classification["neutral"] is True
    assert classification["nonreactive"] is True
    assert classification["nonelectrolyte"] is True
    assert classification["nonassociating"] is True
    assert classification["neutral_species_indices"] == [0, 1]
    assert classification["ionic_species_indices"] == []
    assert classification["associating_species_indices"] == []
    assert classification["phase_eligible_species_indices"] == [0, 1]
    assert classification["transferable_species_indices"] == [0, 1]
    assert classification["fixed_species_indices"] == []
    assert classification["active_family_markers"] == ["neutral", "nonreactive"]

    request_pretreatment = payload["request_pretreatment"]
    assert request_pretreatment["route_shape_validated"] is True
    assert request_pretreatment["finite_numeric_inputs"] is True
    assert request_pretreatment["species_count"] == 2
    assert request_pretreatment["composition_length"] == 2
    assert request_pretreatment["composition_normalized_sum"] == pytest.approx(1.0)
    assert request_pretreatment["composition_basis"] == "mole_fraction"

    thermodynamic_input = payload["thermodynamic_input"]
    assert thermodynamic_input["species_indices"] == [0, 1]
    assert thermodynamic_input["composition_role"] == composition_role
    assert thermodynamic_input["normalized_composition"] == pytest.approx(selector_request["composition"])
    assert thermodynamic_input["extensive_amounts"] == pytest.approx(selector_request["composition"])
    assert thermodynamic_input["amount_basis"] == "unit_total_moles"

    parameter_readiness = payload["parameter_readiness"]
    assert parameter_readiness["pure_neutral_parameters_present"] is True
    assert parameter_readiness["binary_interaction_matrix_present"] is True
    assert parameter_readiness["parameter_provenance_status"] == "runtime_payload_without_source_provenance"
    assert parameter_readiness["source_backed_parameter_provenance_present"] is False
    assert parameter_readiness["explicit_zero_binary_interaction_convention"] is False
    assert parameter_readiness["required_parameter_families_present"] is True
    assert parameter_readiness["missing_required_parameter_families"] == []
    assert parameter_readiness["association_parameters_active"] is False
    assert parameter_readiness["electrolyte_parameters_active"] is False
    assert payload["residual_families"] == activation["residual_families"]
    assert payload["constraint_families"] == activation["constraint_families"]
    assert payload["variable_model"] == activation["variable_model"]
    assert payload["density_backend"] == activation["density_backend"]
    if family in {"neutral_tp_flash", "neutral_lle"}:
        assert activation["stability_prelayer"] == "deterministic_tpd_candidate_screening"
        assert activation["postsolve_certification"] == "tpd_postsolve"


def test_selector_core_rejects_old_scalar_composition_boundary() -> None:
    mix = _neutral_binary_mixture()

    with pytest.raises(TypeError):
        _core._native_equilibrium_selector_contract(
            mix._native,
            "bubble_pressure",
            300.0,
            [0.35, 0.65],
        )


def test_selector_core_rejects_invalid_route_family_before_solver_dispatch() -> None:
    mix = _neutral_binary_mixture()

    with pytest.raises(_core.NativeValueError, match="selector-ineligible"):
        _core._native_equilibrium_selector_contract(
            mix._native,
            {
                "route": "electrolyte_lle",
                "temperature": 300.0,
                "composition": [0.35, 0.65],
                "composition_role": "feed",
            },
        )


def test_selector_core_rejects_active_association_before_solver_dispatch() -> None:
    mix = _methanol_cyclohexane_mixture()

    with pytest.raises(_core.NativeValueError, match="selector-ineligible"):
        _core._native_equilibrium_selector_contract(
            mix._native,
            {
                "route": "bubble_pressure",
                "temperature": 298.15,
                "composition": [0.35, 0.65],
                "composition_role": "liquid",
            },
        )


def test_selector_core_rejects_ionic_lle_before_solver_dispatch() -> None:
    mix = _ionic_mixture()

    with pytest.raises(_core.NativeValueError, match="selector-ineligible"):
        _core._native_equilibrium_selector_contract(
            mix._native,
            {
                "route": "neutral_lle",
                "temperature": 300.0,
                "pressure": 1.0e5,
                "composition": [0.8, 0.1, 0.1],
                "composition_role": "feed",
            },
        )


def test_selector_core_rejects_missing_binary_interactions_before_solver_dispatch() -> None:
    mix = ePCSAFTMixture.from_params(
        {
            "m": [1.0, 1.6069],
            "s": [3.7039, 3.5206],
            "e": [150.03, 191.42],
        },
        species=["Methane", "Ethane"],
    )

    with pytest.raises(_core.NativeValueError, match="binary_interaction_matrix"):
        _core._native_equilibrium_selector_contract(
            mix._native,
            {
                "route": "neutral_tp_flash",
                "temperature": 300.0,
                "pressure": 1.0e6,
                "composition": [0.35, 0.65],
                "composition_role": "feed",
            },
        )


def test_selector_core_accepts_source_backed_explicit_zero_binary_convention() -> None:
    parameters = ParameterSet.from_records(
        [
            PureRecord(component="A", molar_mass=16.0e-3, m=1.0, sigma=3.7, epsilon_k=150.0),
            PureRecord(component="B", molar_mass=30.0e-3, m=1.6, sigma=3.5, epsilon_k=190.0),
        ],
        [BinaryRecord(("A", "B"), k_ij=0.0)],
        metadata={
            "source": "zero-binary-contract-fixture",
            "table": "selector-pretreatment",
            "source_backed": True,
        },
    )
    mix = Mixture(parameters).native

    payload = _core._native_equilibrium_selector_contract(
        mix._native,
        {
            "route": "neutral_tp_flash",
            "temperature": 300.0,
            "pressure": 1.0e6,
            "composition": [0.35, 0.65],
            "composition_role": "feed",
        },
    )

    readiness = payload["parameter_readiness"]
    assert readiness["binary_interaction_matrix_present"] is True
    assert readiness["binary_interaction_provenance_status"] == "explicit_binary_records"
    assert readiness["parameter_provenance_status"] == "source_backed_parameter_metadata"
    assert readiness["source_backed_parameter_provenance_present"] is True
    assert readiness["explicit_zero_binary_interaction_convention"] is True
    assert readiness["parameter_provenance_fields"] == ["source", "table"]
    assert readiness["required_parameter_families_present"] is True


def test_neutral_tp_flash_activation_plan_contract_matches_matrix() -> None:
    mix = _neutral_binary_mixture()
    request = {
        "route": "neutral_tp_flash",
        "temperature": 300.0,
        "pressure": 1.0e6,
        "composition": [0.35, 0.65],
        "composition_role": "feed",
    }

    payload = _core._native_equilibrium_selector_contract(mix._native, request)
    activation = {row["key"]: row for row in _core._native_equilibrium_activation_matrix()}["neutral_tp_flash"]
    plan = payload["activation_plan"]
    layout = payload["variable_layout"]

    assert payload["activation_compiler"] == "activation_plan"
    assert plan["family_key"] == "neutral_tp_flash"
    assert plan["route"] == "neutral_tp_flash"
    assert plan["phase_keys"] == ["liquid", "vapor"]
    assert plan["phase_kinds"] == ["liquid", "vapor"]
    assert plan["variable_blocks"] == ["phase_species_amounts", "phase_volumes"]
    assert plan["constraint_blocks"] == activation["constraint_families"]
    assert plan["residual_blocks"] == activation["residual_families"]
    assert plan["postsolve_blocks"] == [
        "material_balance",
        "phase_pressure_consistency",
        "phase_equilibrium",
        "phase_distance",
        "phase_volume_gap",
    ]
    assert activation["stability_prelayer"] == "deterministic_tpd_candidate_screening"
    assert activation["postsolve_certification"] == "tpd_postsolve"
    assert plan["variable_model"] == activation["variable_model"]
    assert plan["density_backend"] == activation["density_backend"]
    assert plan["feed_composition"] == pytest.approx([0.35, 0.65])
    assert plan["temperature"] == pytest.approx(300.0)
    assert plan["pressure"] == pytest.approx(1.0e6)

    assert layout["family_key"] == "neutral_tp_flash"
    assert layout["route"] == "neutral_tp_flash"
    assert layout["physical_basis"] == "true_species_phase_amounts_and_phase_volumes"
    assert layout["solver_coordinate_basis"] == "physical_variables"
    assert layout["lift_policy"] == "identity_true_species_lift"
    assert layout["back_lift_policy"] == "phase_amount_volume_back_lift"
    assert layout["phase_keys"] == ["liquid", "vapor"]
    assert layout["phase_kinds"] == ["liquid", "vapor"]
    assert layout["phase_count"] == 2
    assert layout["species_count"] == 2
    assert layout["variable_count"] == payload["variable_count"]
    assert layout["phase_amount_indices"] == [[0, 1], [3, 4]]
    assert layout["phase_volume_indices"] == [2, 5]
    assert layout["physical_variable_order"] == [
        "n_phase_0_species_0",
        "n_phase_0_species_1",
        "V_phase_0",
        "n_phase_1_species_0",
        "n_phase_1_species_1",
        "V_phase_1",
    ]
    assert layout["variable_blocks"] == [
        {
            "name": "phase_species_amounts",
            "offset": 0,
            "size": 4,
            "stride": 3,
        },
        {
            "name": "phase_volumes",
            "offset": 2,
            "size": 2,
            "stride": 3,
        },
    ]


def test_neutral_lle_activation_plan_contract_matches_matrix() -> None:
    mix = _nonideal_lle_binary_mixture()
    request = {
        "route": "neutral_lle",
        "temperature": 300.0,
        "pressure": 1.0e6,
        "composition": [0.5, 0.5],
        "composition_role": "feed",
    }

    payload = _core._native_equilibrium_selector_contract(mix._native, request)
    activation = {row["key"]: row for row in _core._native_equilibrium_activation_matrix()}["neutral_lle"]
    plan = payload["activation_plan"]
    layout = payload["variable_layout"]

    assert payload["activation_compiler"] == "activation_plan"
    assert payload["problem_name"] == "neutral_lle_eos"
    assert plan["family_key"] == "neutral_lle"
    assert plan["route"] == "neutral_lle"
    assert plan["phase_keys"] == ["liquid1", "liquid2"]
    assert plan["phase_kinds"] == ["liquid", "liquid"]
    assert plan["variable_blocks"] == ["phase_species_amounts", "phase_volumes"]
    assert plan["constraint_blocks"] == [
        "material_balance",
        "phase_pressure_consistency",
        "phase_distance",
    ]
    assert "phase_volume_gap" not in plan["constraint_blocks"]
    assert plan["residual_blocks"] == activation["residual_families"]
    assert plan["postsolve_blocks"] == [
        "material_balance",
        "phase_pressure_consistency",
        "phase_equilibrium",
        "phase_distance",
    ]
    assert activation["stability_prelayer"] == "deterministic_tpd_candidate_screening"
    assert activation["postsolve_certification"] == "tpd_postsolve"
    assert plan["variable_model"] == activation["variable_model"]
    assert plan["density_backend"] == activation["density_backend"]
    assert plan["feed_composition"] == pytest.approx([0.5, 0.5])
    assert plan["temperature"] == pytest.approx(300.0)
    assert plan["pressure"] == pytest.approx(1.0e6)

    assert layout["family_key"] == "neutral_lle"
    assert layout["route"] == "neutral_lle"
    assert layout["physical_basis"] == "true_species_phase_amounts_and_phase_volumes"
    assert layout["lift_policy"] == "identity_true_species_lift"
    assert layout["phase_keys"] == ["liquid1", "liquid2"]
    assert layout["phase_kinds"] == ["liquid", "liquid"]
    assert layout["phase_count"] == 2
    assert layout["species_count"] == 2
    assert layout["variable_count"] == payload["variable_count"]
    assert layout["phase_amount_indices"] == [[0, 1], [3, 4]]
    assert layout["phase_volume_indices"] == [2, 5]


@pytest.mark.parametrize(
    ("route", "composition_role"),
    [
        ("bubble_pressure", "liquid"),
        ("bubble_temperature", "liquid"),
        ("dew_pressure", "vapor"),
        ("dew_temperature", "vapor"),
        ("electrolyte_lle", "feed"),
        ("reactive_speciation", "feed"),
        ("reactive_lle", "feed"),
        ("reactive_electrolyte_lle", "feed"),
    ],
)
def test_activation_plan_builder_rejects_non_activation_routes(route: str, composition_role: str) -> None:
    mix = _neutral_binary_mixture()

    with pytest.raises(_core.NativeValueError, match="activation-plan-ineligible"):
        _core._native_equilibrium_activation_plan_contract(
            mix._native,
            {
                "route": route,
                "temperature": 300.0,
                "pressure": 1.0e6,
                "composition": [0.35, 0.65],
                "composition_role": composition_role,
            },
        )


def test_activated_neutral_tp_flash_nlp_matches_trusted_contract_shape() -> None:
    mix = _neutral_binary_mixture()
    request = {
        "route": "neutral_tp_flash",
        "temperature": 300.0,
        "pressure": 1.0e6,
        "composition": [0.35, 0.65],
        "composition_role": "feed",
    }

    payload = _core._native_activated_neutral_tp_flash_nlp_contract(mix._native, request)
    activated = payload["activated"]
    trusted = payload["trusted_reference"]

    assert payload["activation_plan"]["family_key"] == "neutral_tp_flash"
    assert payload["variable_layout"]["variable_count"] == activated["variable_count"]
    assert activated["activation_compiler"] == "activation_plan"
    assert activated["variable_count"] == trusted["variable_count"]
    assert activated["constraint_count"] == trusted["constraint_count"]
    assert activated["jacobian_nonzero_count"] == trusted["jacobian_nonzero_count"]
    assert len(activated["variable_lower_bounds"]) == len(trusted["variable_lower_bounds"])
    assert len(activated["variable_upper_bounds"]) == len(trusted["variable_upper_bounds"])
    assert len(activated["constraint_lower_bounds"]) == len(trusted["constraint_lower_bounds"])
    assert len(activated["constraint_upper_bounds"]) == len(trusted["constraint_upper_bounds"])
    assert len(activated["initial_point"]) == len(trusted["initial_point"])
    assert activated["residual_families"] == trusted["residual_families"]
    assert activated["constraint_families"] == trusted["constraint_families"]
    assert activated["exact_hessian_available"] is True
    assert activated["hessian_nonzero_count"] == trusted["hessian_nonzero_count"]
    assert len(activated["hessian_rows"]) == activated["hessian_nonzero_count"]
    assert len(activated["hessian_cols"]) == activated["hessian_nonzero_count"]
    assert len(activated["hessian_values_at_initial"]) == activated["hessian_nonzero_count"]
    assert activated["hessian_backend"] == trusted["hessian_backend"]
    assert activated["sparse_contract"]["jacobian_structure_matches_values"] is True
    assert activated["sparse_contract"]["hessian_structure_matches_values"] is True
    assert activated["derivative_contract"]["objective_gradient_exact"] is True
    assert activated["derivative_contract"]["constraint_jacobian_exact"] is True
    assert activated["derivative_contract"]["lagrangian_hessian_exact"] is True
    assert activated["derivative_contract"]["missing_exact_derivative_blocks"] == []
    assert activated["objective_scaling"] > 0.0
    assert len(activated["variable_scaling"]) == activated["variable_count"]
    assert len(activated["constraint_scaling"]) == activated["constraint_count"]
    assert activated["initial_variable_bound_margin"] > 0.0
    assert activated["initial_amount_lower_margin"] > 0.0
    assert activated["initial_volume_lower_margin"] > 0.0
    assert activated["initial_constraint_bound_violation"] >= 0.0
    assert activated["domain_safety_policy"] == "explicit_bounds_variable_transform_ipopt_barrier"
    assert activated["transform_policy"] == "identity_physical_coordinates"
    assert activated["transform_backend"] == "analytic_identity"
    assert activated["transform_input_variable_count"] == activated["variable_count"]
    assert activated["transform_output_variable_count"] == activated["variable_count"]
    assert activated["transform_jacobian_value_count"] == activated["variable_count"] ** 2
    assert activated["transform_hessian_value_count"] == activated["variable_count"] ** 3
    assert activated["barrier_policy"] == "ipopt_internal_barrier_for_declared_bounds"
    domain = activated["domain_contract"]
    assert domain["variable_bounds_declared"] is True
    assert domain["constraint_bounds_declared"] is True
    assert domain["solver_to_physical_declared"] is True
    assert domain["transform_jacobian_declared"] is True
    assert domain["transform_hessian_declared"] is True
    assert domain["transform_chain_rule_derivatives_declared"] is True
    assert domain["variable_scaling_declared"] is True
    assert domain["constraint_scaling_declared"] is True
    assert domain["ipopt_barrier_owns_declared_bounds"] is True
    assert domain["thermodynamic_objective_custom_barrier"] is False
    assert domain["margins"]["initial_variable_bound_margin"] == pytest.approx(
        activated["initial_variable_bound_margin"]
    )


def test_selector_core_rejects_incompatible_composition_role_before_solver_dispatch() -> None:
    mix = _neutral_binary_mixture()

    with pytest.raises(_core.NativeValueError, match="composition_role"):
        _core._native_equilibrium_selector_contract(
            mix._native,
            {
                "route": "bubble_pressure",
                "temperature": 300.0,
                "composition": [0.35, 0.65],
                "composition_role": "vapor",
            },
        )
