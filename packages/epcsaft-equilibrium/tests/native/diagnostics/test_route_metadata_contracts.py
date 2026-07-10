from __future__ import annotations

import numpy as np
import pytest
from epcsaft.state.native_adapter import ePCSAFTMixture
from epcsaft_equilibrium._native import extension_native_core

_core = extension_native_core()
from equilibrium_support.equilibrium_cases import (
    _neutral_binary_mixture,
)

pytestmark = pytest.mark.native_contract


def test_selector_contract_declares_production_route_metadata_without_solving() -> None:
    mix = _neutral_binary_mixture()

    payload = _core._native_equilibrium_selector_contract(
        mix._native,
        {
            "route": "bubble_pressure",
            "temperature": 300.0,
            "composition": [0.35, 0.65],
            "composition_role": "liquid",
        },
    )

    assert payload["selector_family"] == "bubble_dew_derived_routes"
    assert payload["route"] == "bubble_pressure"
    assert payload["composition_role"] == "liquid"
    assert payload["specified_temperature"] is True
    assert payload["specified_pressure"] is False
    assert payload["problem_name"] == "neutral_bubble_p_eos"
    assert payload["variable_model"] == "phase_species_amounts_plus_phase_volume_plus_route_scalar"
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


def test_activation_matrix_retains_neutral_lle_as_closed_internal_inventory() -> None:
    rows = {row["key"]: row for row in _core._native_equilibrium_activation_matrix()}
    neutral_lle = rows["neutral_lle"]

    assert neutral_lle["production_exposed"] is False
    assert neutral_lle["exposure_status"] == "declared_not_exposed"
    assert neutral_lle["proof_routes"] == []
    assert neutral_lle["public_routes"] == []
    assert neutral_lle["variable_model"] == "phase_species_amounts_plus_phase_volume"
    assert neutral_lle["density_backend"] == "explicit_phase_volume_pressure_constraint"


def test_selector_contract_declares_single_component_vle_shared_pressure_route_metadata() -> None:
    mix = ePCSAFTMixture.from_params(
        {
            "m": np.asarray([1.6069]),
            "s": np.asarray([3.5206]),
            "e": np.asarray([191.42]),
        },
        species=["Ethane"],
    )

    payload = _core._native_equilibrium_selector_contract(
        mix._native,
        {
            "route": "single_component_vle",
            "temperature": 233.15,
            "composition": [1.0],
            "composition_role": "pure",
        },
    )

    assert payload["selector_family"] == "single_component_vle"
    assert payload["route"] == "single_component_vle"
    assert payload["composition_role"] == "pure"
    assert payload["specified_temperature"] is True
    assert payload["specified_pressure"] is False
    assert payload["problem_name"] == "single_component_vle_eos"
    assert payload["variable_model"] == "phase_species_amounts_plus_phase_volume_plus_route_scalar"
    assert payload["density_backend"] == "explicit_phase_volume_pressure_constraint"
    assert payload["exact_derivatives_required"] is True
    assert payload["certification_required"] is True
    assert payload["activation"]["stability_prelayer"] == "postsolve_local_only"
    assert payload["activation"]["split_variables"] == "on"
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
