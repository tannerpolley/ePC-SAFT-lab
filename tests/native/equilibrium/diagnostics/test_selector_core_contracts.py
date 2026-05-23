from __future__ import annotations

import pytest

import epcsaft._core as _core
from tests.support.equilibrium_cases import (
    _ionic_mixture,
    _methanol_cyclohexane_mixture,
    _neutral_binary_mixture,
    _nonideal_lle_binary_mixture,
)


@pytest.mark.parametrize(
    ("selector_request", "family", "problem_name", "composition_role", "specified_temperature", "specified_pressure"),
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
    assert payload["specified_temperature"] is specified_temperature
    assert payload["specified_pressure"] is specified_pressure
    assert payload["production_exposed"] is True
    assert payload["certification_required"] is True
    assert payload["density_closure_required"] is True
    assert payload["exact_derivatives_required"] is True
    assert payload["input_classification"] == {
        "neutral": True,
        "nonreactive": True,
        "nonelectrolyte": True,
        "nonassociating": True,
    }
    assert payload["residual_families"] == activation["residual_families"]
    assert payload["constraint_families"] == activation["constraint_families"]
    assert payload["variable_model"] == activation["variable_model"]
    assert payload["density_backend"] == activation["density_backend"]


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
    assert plan["variable_model"] == activation["variable_model"]
    assert plan["density_backend"] == activation["density_backend"]
    assert plan["feed_composition"] == pytest.approx([0.35, 0.65])
    assert plan["temperature"] == pytest.approx(300.0)
    assert plan["pressure"] == pytest.approx(1.0e6)

    assert layout["family_key"] == "neutral_tp_flash"
    assert layout["route"] == "neutral_tp_flash"
    assert layout["phase_count"] == 2
    assert layout["species_count"] == 2
    assert layout["variable_count"] == payload["variable_count"]
    assert layout["phase_amount_indices"] == [[0, 1], [3, 4]]
    assert layout["phase_volume_indices"] == [2, 5]
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
    assert plan["variable_model"] == activation["variable_model"]
    assert plan["density_backend"] == activation["density_backend"]
    assert plan["feed_composition"] == pytest.approx([0.5, 0.5])
    assert plan["temperature"] == pytest.approx(300.0)
    assert plan["pressure"] == pytest.approx(1.0e6)

    assert layout["family_key"] == "neutral_lle"
    assert layout["route"] == "neutral_lle"
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
    assert activated["hessian_backend"] == trusted["hessian_backend"]


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
