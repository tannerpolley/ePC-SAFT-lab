from __future__ import annotations

import pytest

import epcsaft._core as _core
from tests.support.equilibrium_cases import _neutral_binary_mixture


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
    mix = _neutral_binary_mixture()
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
                "route": "neutral_lle",
                "temperature": 300.0,
                "composition": [0.35, 0.65],
                "composition_role": "feed",
            },
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
