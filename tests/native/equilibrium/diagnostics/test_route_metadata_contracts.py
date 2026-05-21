from __future__ import annotations

import pytest

from epcsaft import _core
from tests.support.equilibrium_cases import _neutral_binary_mixture

pytestmark = pytest.mark.native_contract


def test_selector_contract_declares_production_route_metadata_without_solving() -> None:
    mix = _neutral_binary_mixture()

    payload = _core._native_equilibrium_selector_contract(mix._native, "bubble_pressure", 300.0, [0.35, 0.65])

    assert payload["selector_family"] == "bubble_dew_derived_routes"
    assert payload["route"] == "bubble_pressure"
    assert payload["problem_name"] == "neutral_bubble_p_eos"
    assert payload["variable_model"] == "phase_species_amounts_plus_phase_volume_plus_pressure"
    assert payload["density_backend"] == "explicit_phase_volume_pressure_constraint"
    assert payload["exact_derivatives_required"] is True
    assert payload["certification_required"] is True
    assert payload["density_closure_required"] is True
    assert payload["residual_families"] == [
        "fixed_composition",
        "phase_amount_total",
        "phase_pressure_consistency",
        "phase_equilibrium",
        "phase_distance",
    ]
    assert payload["constraint_families"] == [
        "fixed_composition",
        "phase_amount_total",
        "phase_pressure_consistency",
        "phase_equilibrium",
        "phase_volume_gap",
    ]


def test_deleted_native_equilibrium_route_entrypoints_are_absent() -> None:
    deleted = {
        "_native_neutral_tp_flash_eos_nlp_contract",
        "_native_neutral_tp_flash_eos_route_result",
        "_native_neutral_lle_eos_nlp_contract",
        "_native_neutral_lle_eos_route_result",
        "_native_electrolyte_lle_eos_nlp_contract",
        "_native_electrolyte_lle_eos_route_result",
        "_native_electrolyte_bubble_p_eos_nlp_contract",
        "_native_electrolyte_bubble_p_eos_route_result",
        "_native_neutral_stability_tpd_nlp_contract",
        "_native_neutral_stability_tpd_route_result",
        "_native_electrolyte_stability_tpd_nlp_contract",
        "_native_electrolyte_stability_tpd_route_result",
        "_native_reactive_lle_eos_nlp_contract",
        "_native_reactive_lle_eos_route_result",
        "_native_reactive_electrolyte_lle_eos_nlp_contract",
        "_native_reactive_electrolyte_lle_eos_route_result",
        "_native_neutral_bubble_p_eos_route_result",
        "_native_neutral_dew_p_eos_route_result",
        "_native_neutral_bubble_t_eos_route_result",
        "_native_neutral_dew_t_eos_route_result",
        "_solve_chemical_equilibrium_native",
        "_evaluate_chemical_equilibrium_residual_native",
        "_evaluate_reactive_phase_equilibrium_residual_native",
        "_evaluate_electrolyte_lle_residual_native",
    }

    assert [name for name in sorted(deleted) if hasattr(_core, name)] == []


def test_selector_rejects_declared_not_exposed_route_family() -> None:
    mix = _neutral_binary_mixture()

    native_value_error = getattr(_core, "NativeValueError", ValueError)
    with pytest.raises(native_value_error, match="selector-ineligible"):
        _core._native_equilibrium_selector_contract(mix._native, "neutral_lle", 300.0, [0.35, 0.65])
