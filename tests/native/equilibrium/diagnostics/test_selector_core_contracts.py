from __future__ import annotations

import pytest

from epcsaft import _core
from tests.support.equilibrium_cases import _neutral_binary_mixture


def test_selector_core_contract_owns_production_bubble_pressure_metadata() -> None:
    mix = _neutral_binary_mixture()
    payload = _core._native_equilibrium_selector_contract(
        mix._native,
        "bubble_pressure",
        300.0,
        [0.35, 0.65],
    )
    matrix = {row["key"]: row for row in _core._native_equilibrium_activation_matrix()}
    activation = matrix["bubble_dew_derived_routes"]

    assert payload["selector_family"] == "bubble_dew_derived_routes"
    assert payload["route"] == "bubble_pressure"
    assert payload["problem_name"] == "neutral_bubble_p_eos"
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


def test_selector_core_rejects_declared_not_exposed_family_before_solver_dispatch() -> None:
    mix = _neutral_binary_mixture()

    with pytest.raises(_core.NativeValueError, match="selector-ineligible"):
        _core._native_equilibrium_selector_contract(
            mix._native,
            "neutral_tp_flash",
            300.0,
            [0.35, 0.65],
        )
