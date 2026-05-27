from __future__ import annotations

import numpy as np
import pytest

import epcsaft._core as _core
from tests.support.equilibrium_cases import (
    WORKBOOK_BUBBLE_PRESSURE,
    WORKBOOK_TEMPERATURE,
    _hydrocarbon_workbook_mixture,
)


def _three_phase_hydrocarbon_case() -> tuple[object, float, float, list[list[float]], list[float], list[float]]:
    mix = _hydrocarbon_workbook_mixture()
    composition = np.asarray([0.2, 0.3, 0.5], dtype=float)
    density = 14_000.0
    target_pressure = mix.state(
        T=WORKBOOK_TEMPERATURE,
        rho=density,
        x=composition,
        phase="liquid",
    ).pressure()
    phase_totals = np.asarray([0.6, 0.3, 0.1], dtype=float)
    phase_amounts = [(total * composition).tolist() for total in phase_totals]
    volumes = [float(total / density) for total in phase_totals]
    feed_amounts = np.sum(np.asarray(phase_amounts, dtype=float), axis=0).tolist()
    return mix, WORKBOOK_TEMPERATURE, float(target_pressure), phase_amounts, volumes, feed_amounts


def test_internal_multiphase_activation_plan_contract_builds_three_phase_layout() -> None:
    mix = _hydrocarbon_workbook_mixture()

    payload = _core._native_equilibrium_activation_plan_contract(
        mix._native,
        {
            "route": "neutral_multiphase_nonassoc",
            "temperature": WORKBOOK_TEMPERATURE,
            "pressure": WORKBOOK_BUBBLE_PRESSURE,
            "composition": [0.2, 0.3, 0.5],
            "composition_role": "feed",
            "phase_kinds": ["liquid", "liquid", "vapor"],
        },
    )

    plan = payload["activation_plan"]
    layout = payload["variable_layout"]

    assert plan["family_key"] == "neutral_multiphase_nonassoc"
    assert plan["route"] == "neutral_multiphase_nonassoc"
    assert plan["phase_keys"] == ["liquid1", "liquid2", "vapor"]
    assert plan["phase_kinds"] == ["liquid", "liquid", "vapor"]
    assert plan["variable_blocks"] == ["phase_species_amounts", "phase_volumes"]
    assert plan["constraint_blocks"] == ["material_balance", "phase_pressure_consistency"]
    assert plan["residual_blocks"] == [
        "material_balance",
        "phase_pressure_consistency",
        "phase_equilibrium",
        "phase_distance",
    ]
    assert plan["variable_model"] == "phase_species_amounts_plus_phase_volume"
    assert plan["density_backend"] == "explicit_phase_volume_pressure_constraint"
    assert plan["feed_composition"] == pytest.approx([0.2, 0.3, 0.5])

    assert layout["family_key"] == "neutral_multiphase_nonassoc"
    assert layout["route"] == "neutral_multiphase_nonassoc"
    assert layout["phase_count"] == 3
    assert layout["species_count"] == 3
    assert layout["variable_count"] == 12
    assert layout["phase_amount_indices"] == [[0, 1, 2], [4, 5, 6], [8, 9, 10]]
    assert layout["phase_volume_indices"] == [3, 7, 11]


def test_internal_multiphase_eos_nlp_contract_reports_exact_hessian_for_three_phase_state() -> None:
    mix, temperature, target_pressure, phase_amounts, volumes, feed_amounts = _three_phase_hydrocarbon_case()

    payload = _core._native_neutral_multiphase_eos_nlp_contract(
        mix._native,
        temperature,
        target_pressure,
        phase_amounts,
        volumes,
        feed_amounts,
    )

    assert payload["problem_name"] == "neutral_multiphase_eos"
    assert payload["phase_count"] == 3
    assert payload["species_count"] == 3
    assert payload["variable_count"] == 12
    assert payload["constraint_count"] == 6
    assert payload["jacobian_nonzero_count"] == 21
    assert payload["exact_hessian_available"] is True
    assert payload["hessian_backend"] == "cppad_phase_system"
    assert payload["variable_model"] == "phase_species_amounts_plus_phase_volume"
    assert payload["density_backend"] == "explicit_phase_volume_pressure_constraint"
    assert payload["residual_families"] == [
        "material_balance",
        "phase_pressure_consistency",
        "phase_equilibrium",
        "phase_distance",
    ]
    assert payload["constraint_families"] == ["material_balance", "phase_pressure_consistency"]


def test_internal_multiphase_eos_postsolve_certifies_three_phase_shape_without_public_exposure() -> None:
    mix, temperature, target_pressure, phase_amounts, volumes, feed_amounts = _three_phase_hydrocarbon_case()

    payload = _core._native_neutral_multiphase_eos_postsolve(
        mix._native,
        temperature,
        target_pressure,
        phase_amounts,
        volumes,
        feed_amounts,
        1.0e-8,
        1.0e-3,
        1.0e-6,
        1.0e-6,
        [0, 0, 0],
    )

    assert payload["phase_count"] == 3
    assert payload["species_count"] == 3
    assert len(payload["phase_amount_totals"]) == 3
    assert len(payload["phase_volumes"]) == 3
    assert len(payload["phase_compositions"]) == 3
    assert payload["selected_candidate_count"] == 3
    assert payload["selected_phase_kinds"] == [0, 0, 0]
    assert len(payload["selected_phase_compositions"]) == 3
    assert payload["phase_discovery_backend"] == "deterministic_tpd_candidate_screening"
    assert payload["stability_certificate"] == "tpd_postsolve"
    assert payload["candidate_mass_balance_norm"] >= 0.0
