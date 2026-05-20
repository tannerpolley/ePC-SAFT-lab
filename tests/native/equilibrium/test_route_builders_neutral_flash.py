from __future__ import annotations

import numpy as np
import pytest

import epcsaft
from epcsaft import _core
from tests.native.equilibrium.route_builder_cases import (
    WORKBOOK_BUBBLE_PRESSURE,
    WORKBOOK_LIQUID_COMPOSITION,
    WORKBOOK_LIQUID_DENSITY,
    WORKBOOK_TEMPERATURE,
    WORKBOOK_VAPOR_COMPOSITION,
    WORKBOOK_VAPOR_DENSITY,
    _ascani_electrolyte_mixture,
    _dense_jacobian_from_sparse_contract,
    _hydrocarbon_workbook_mixture,
    _hydrocarbon_workbook_params,
    _ionic_mixture,
    _methanol_cyclohexane_lle_feed,
    _methanol_cyclohexane_mixture,
    _neutral_binary_mixture,
    _nonideal_lle_binary_mixture,
    _reactive_stability_inputs,
)

pytestmark = [pytest.mark.native_solver, pytest.mark.ipopt, pytest.mark.slow]


def test_neutral_tp_flash_route_uses_exact_hessian_when_requested() -> None:
    mix = _neutral_binary_mixture()
    payload = _core._native_neutral_tp_flash_eos_route_result(
        mix._native,
        260.0,
        5.0e6,
        [0.4, 0.6],
        180,
        1.0e-6,
        0.0,
        "exact",
        20,
        1.0e-6,
        5.0,
        1.0e-6,
        1.0e-8,
        None,
    )

    if not payload["compiled"]:
        assert payload["status"] == "ipopt_dependency_required"
        return

    assert payload["ran"] is True
    assert payload["solver_accepted"] is True
    assert payload["accepted"] is True
    assert payload["status"] == "accepted"
    assert payload["hessian_approximation"] == "exact"
    assert payload["exact_hessian_available"] is True
    assert payload["hessian_backend"] == "cppad_phase_system"
    assert payload["eval_h_calls"] > 0
    assert payload["postsolve"]["phase_distance"] > 0.1
    assert payload["postsolve"]["chemical_potential_consistency_norm"] <= 1.0e-6

def test_neutral_two_phase_eos_nlp_contract_uses_phase_system_blocks() -> None:
    mix = _neutral_binary_mixture()
    temperature = 300.0
    phase_amounts = [
        np.asarray([0.7, 0.3], dtype=float),
        np.asarray([0.1, 0.9], dtype=float),
    ]
    volumes = [float(phase_amounts[0].sum() / 80.0), float(phase_amounts[1].sum() / 140.0)]
    feed_amounts = phase_amounts[0] + phase_amounts[1]
    target_pressure = mix.state(
        T=temperature,
        rho=phase_amounts[0].sum() / volumes[0],
        x=phase_amounts[0] / phase_amounts[0].sum(),
        phase="liquid",
    ).pressure()

    payload = _core._native_neutral_two_phase_eos_nlp_contract(
        mix._native,
        temperature,
        target_pressure,
        [phase.tolist() for phase in phase_amounts],
        volumes,
        feed_amounts.tolist(),
    )
    phase_system = _core._native_eos_phase_system(
        mix._native,
        temperature,
        target_pressure,
        [phase.tolist() for phase in phase_amounts],
        volumes,
        feed_amounts.tolist(),
    )

    assert payload["problem_name"] == "neutral_two_phase_eos"
    assert payload["derivative_backend"] == "analytic_cppad"
    assert payload["variable_model"] == "phase_species_amounts_plus_phase_volume"
    assert payload["density_backend"] == "explicit_phase_volume_pressure_constraint"
    assert payload["residual_families"] == [
        "material_balance",
        "phase_pressure_consistency",
        "phase_equilibrium",
        "phase_distance",
    ]
    assert payload["constraint_families"] == ["material_balance", "phase_pressure_consistency"]
    assert payload["phase_count"] == 2
    assert payload["species_count"] == 2
    assert payload["variable_count"] == 6
    assert payload["constraint_count"] == 4
    assert payload["jacobian_nonzero_count"] == 10
    assert payload["initial_point"] == pytest.approx([0.7, 0.3, volumes[0], 0.1, 0.9, volumes[1]])
    assert payload["objective_at_initial"] == pytest.approx(phase_system["objective"])
    assert payload["gradient_at_initial"] == pytest.approx(phase_system["gradient"], rel=1.0e-12, abs=1.0e-12)
    assert payload["constraints_at_initial"] == pytest.approx(
        phase_system["constraints"],
        rel=1.0e-12,
        abs=1.0e-8,
    )
    np.testing.assert_allclose(
        _dense_jacobian_from_sparse_contract(payload),
        np.asarray(phase_system["constraint_jacobian_row_major"], dtype=float).reshape(4, 6),
        rtol=1.0e-12,
        atol=1.0e-8,
    )
    assert len(payload["variable_lower_bounds"]) == payload["variable_count"]
    assert len(payload["variable_upper_bounds"]) == payload["variable_count"]
    assert len(payload["constraint_lower_bounds"]) == payload["constraint_count"]
    assert len(payload["constraint_upper_bounds"]) == payload["constraint_count"]
    assert np.all(np.asarray(payload["variable_lower_bounds"], dtype=float) > 0.0)
    assert payload["constraint_lower_bounds"] == pytest.approx([0.0, 0.0, 0.0, 0.0])
    assert payload["constraint_upper_bounds"] == pytest.approx([0.0, 0.0, 0.0, 0.0])

def test_neutral_tp_flash_route_contract_builds_native_initial_point_from_feed() -> None:
    mix = _neutral_binary_mixture()
    temperature = 300.0
    target_pressure = 1.0e5
    feed_amounts = np.asarray([0.3, 0.7], dtype=float)

    payload = _core._native_neutral_tp_flash_eos_nlp_contract(
        mix._native,
        temperature,
        target_pressure,
        feed_amounts.tolist(),
    )

    initial = np.asarray(payload["initial_point"], dtype=float).reshape(2, 3)
    phase_amounts = initial[:, :2]
    volumes = initial[:, 2]
    phase_compositions = phase_amounts / np.sum(phase_amounts, axis=1, keepdims=True)

    assert payload["problem_name"] == "neutral_two_phase_eos"
    assert payload["derivative_backend"] == "analytic_cppad"
    assert payload["variable_model"] == "phase_species_amounts_plus_phase_volume"
    assert payload["density_backend"] == "explicit_phase_volume_pressure_constraint"
    assert payload["constraint_families"] == [
        "material_balance",
        "phase_pressure_consistency",
        "phase_distance",
    ]
    assert payload["phase_count"] == 2
    assert payload["species_count"] == 2
    assert np.all(phase_amounts > 0.0)
    assert np.all(volumes > 0.0)
    assert np.sum(phase_amounts, axis=0) == pytest.approx(feed_amounts)
    assert phase_compositions[0] != pytest.approx(phase_compositions[1])
    assert np.asarray(payload["constraints_at_initial"], dtype=float)[:2] == pytest.approx([0.0, 0.0])
    assert payload["constraint_lower_bounds"][-1] == pytest.approx(1.0e-8)
    assert payload["constraint_upper_bounds"][-1] > 1.0e6
    assert payload["constraints_at_initial"][-1] >= payload["constraint_lower_bounds"][-1]

def test_hydrocarbon_workbook_params_are_hc_dispersion_only() -> None:
    params = _hydrocarbon_workbook_params()

    assert set(params) == {"m", "s", "e", "k_ij"}
    assert params["m"] == pytest.approx([1.0, 1.6069, 2.0020])
    assert params["s"] == pytest.approx([3.7039, 3.5206, 3.6184])
    assert params["e"] == pytest.approx([150.03, 191.42, 208.11])
    np.testing.assert_allclose(
        params["k_ij"],
        np.asarray(
            [
                [0.0, 3.0e-4, 1.15e-2],
                [3.0e-4, 0.0, 5.10e-3],
                [1.15e-2, 5.10e-3, 0.0],
            ],
            dtype=float,
        ),
    )

def test_neutral_tp_flash_workbook_seed_uses_phase_specific_density_roots() -> None:
    mix = _hydrocarbon_workbook_mixture()
    temperature = WORKBOOK_TEMPERATURE
    target_pressure = WORKBOOK_BUBBLE_PRESSURE
    feed_amounts = np.asarray(WORKBOOK_LIQUID_COMPOSITION, dtype=float)

    payload = _core._native_neutral_tp_flash_eos_nlp_contract(
        mix._native,
        temperature,
        target_pressure,
        feed_amounts.tolist(),
    )

    initial = np.asarray(payload["initial_point"], dtype=float).reshape(2, 4)
    phase_amounts = initial[:, :3]
    volumes = initial[:, 3]
    densities = np.sum(phase_amounts, axis=1) / volumes
    pressure_residuals = np.asarray(payload["constraints_at_initial"], dtype=float)[3:5]
    ideal_density = target_pressure / (8.31446261815324 * temperature)

    assert payload["problem_name"] == "neutral_two_phase_eos"
    assert phase_amounts.sum(axis=0) == pytest.approx(feed_amounts)
    assert densities[0] > 8_000.0
    assert densities[1] < 3_000.0
    assert densities[0] / densities[1] > 5.0
    assert densities == pytest.approx([14_192.12241442391, 1_076.07578975462], rel=1.0e-10)
    assert np.max(np.abs(pressure_residuals)) / target_pressure <= 1.0e-11
    assert not np.allclose(densities, ideal_density)

def test_neutral_two_phase_eos_route_result_translates_solver_and_postsolve() -> None:
    mix = _neutral_binary_mixture()
    temperature = 300.0
    phase_amounts = [
        np.asarray([0.7, 0.3], dtype=float),
        np.asarray([0.1, 0.9], dtype=float),
    ]
    density = 120.0
    volumes = [float(phase.sum() / density) for phase in phase_amounts]
    feed_amounts = phase_amounts[0] + phase_amounts[1]
    target_pressure = mix.state(
        T=temperature,
        rho=density,
        x=phase_amounts[0] / phase_amounts[0].sum(),
        phase="liquid",
    ).pressure()

    payload = _core._native_neutral_two_phase_eos_route_result(
        mix._native,
        temperature,
        target_pressure,
        [phase.tolist() for phase in phase_amounts],
        volumes,
        feed_amounts.tolist(),
        30,
        1.0e-8,
        "limited-memory",
        20,
        1.0e-7,
        1.0e-5,
        1.0e-7,
        1.0e-4,
        None,
    )

    assert payload["backend"] == "ipopt"
    assert payload["problem_name"] == "neutral_two_phase_eos"
    assert payload["derivative_backend"] == "analytic_cppad"
    assert payload["variable_model"] == "phase_species_amounts_plus_phase_volume"
    assert payload["density_backend"] == "explicit_phase_volume_pressure_constraint"
    assert payload["residual_families"] == [
        "material_balance",
        "phase_pressure_consistency",
        "phase_equilibrium",
        "phase_distance",
    ]
    assert payload["constraint_families"] == ["material_balance", "phase_pressure_consistency"]
    assert payload["exact_gradient_required"] is True
    assert payload["exact_jacobian_required"] is True
    if not payload["compiled"]:
        assert payload["ran"] is False
        assert payload["solver_accepted"] is False
        assert payload["accepted"] is False
        assert payload["status"] == "ipopt_dependency_required"
        assert payload["phase_amounts"] == []
        assert payload["phase_volumes"] == []
        assert payload["postsolve"]["accepted"] is False
        return

    assert payload["ran"] is True
    assert np.asarray(payload["variables"], dtype=float).shape == (6,)
    assert np.asarray(payload["phase_amounts"], dtype=float).shape == (2, 2)
    assert np.asarray(payload["phase_volumes"], dtype=float).shape == (2,)
    assert payload["postsolve"]["derivative_backend"] == "analytic_cppad"
    assert payload["accepted"] == (payload["solver_accepted"] and payload["postsolve"]["accepted"])
    if payload["accepted"]:
        assert payload["status"] == "accepted"
        assert payload["postsolve"]["rejection_reason"] == "accepted"
    else:
        assert payload["status"] in {"solver_rejected", "postsolve_rejected"}

def test_neutral_two_phase_eos_postsolve_rejects_collapsed_phases() -> None:
    mix = _neutral_binary_mixture()
    temperature = 300.0
    phase_amounts = [
        np.asarray([0.4, 0.6], dtype=float),
        np.asarray([0.4, 0.6], dtype=float),
    ]
    density = 120.0
    volumes = [float(phase.sum() / density) for phase in phase_amounts]
    feed_amounts = phase_amounts[0] + phase_amounts[1]
    target_pressure = mix.state(
        T=temperature,
        rho=density,
        x=phase_amounts[0] / phase_amounts[0].sum(),
        phase="liquid",
    ).pressure()

    payload = _core._native_neutral_two_phase_eos_postsolve(
        mix._native,
        temperature,
        target_pressure,
        [phase.tolist() for phase in phase_amounts],
        volumes,
        feed_amounts.tolist(),
        1.0e-8,
        1.0e-6,
        1.0e-6,
        1.0e-3,
    )

    assert payload["accepted"] is False
    assert payload["rejection_reason"] == "phase_distance"
    assert payload["material_balance_norm"] <= 1.0e-12
    assert payload["pressure_consistency_norm"] <= 1.0e-6
    assert payload["chemical_potential_consistency_norm"] == pytest.approx(0.0, abs=1.0e-14)
    assert payload["ln_fugacity_consistency_norm"] == pytest.approx(0.0, abs=1.0e-14)
    assert payload["phase_distance"] == pytest.approx(0.0, abs=1.0e-14)

def test_neutral_two_phase_eos_postsolve_reports_pressure_gate() -> None:
    mix = _neutral_binary_mixture()
    temperature = 300.0
    phase_amounts = [
        np.asarray([0.7, 0.3], dtype=float),
        np.asarray([0.1, 0.9], dtype=float),
    ]
    volumes = [float(phase_amounts[0].sum() / 80.0), float(phase_amounts[1].sum() / 140.0)]
    feed_amounts = phase_amounts[0] + phase_amounts[1]
    target_pressure = mix.state(
        T=temperature,
        rho=phase_amounts[0].sum() / volumes[0],
        x=phase_amounts[0] / phase_amounts[0].sum(),
        phase="liquid",
    ).pressure()

    payload = _core._native_neutral_two_phase_eos_postsolve(
        mix._native,
        temperature,
        target_pressure,
        [phase.tolist() for phase in phase_amounts],
        volumes,
        feed_amounts.tolist(),
        1.0e-8,
        1.0e-6,
        1.0e-6,
        1.0e-3,
    )

    assert payload["accepted"] is False
    assert payload["rejection_reason"] == "pressure_consistency"
    assert payload["material_balance_norm"] <= 1.0e-12
    assert payload["pressure_consistency_norm"] > 1.0e-6
    assert "chemical_potential_consistency_norm" in payload
    assert "ln_fugacity_consistency_norm" in payload
    assert np.isfinite(payload["ln_fugacity_consistency_norm"])
    assert payload["phase_distance"] > 1.0e-3

def test_neutral_two_phase_eos_postsolve_reports_chemical_potential_gate() -> None:
    mix = _neutral_binary_mixture()
    temperature = 300.0
    phase_amounts = [
        np.asarray([0.7, 0.3], dtype=float),
        np.asarray([0.1, 0.9], dtype=float),
    ]
    density = 120.0
    volumes = [float(phase.sum() / density) for phase in phase_amounts]
    feed_amounts = phase_amounts[0] + phase_amounts[1]
    target_pressure = mix.state(
        T=temperature,
        rho=density,
        x=phase_amounts[0] / phase_amounts[0].sum(),
        phase="liquid",
    ).pressure()

    payload = _core._native_neutral_two_phase_eos_postsolve(
        mix._native,
        temperature,
        target_pressure,
        [phase.tolist() for phase in phase_amounts],
        volumes,
        feed_amounts.tolist(),
        1.0e-8,
        1.0e12,
        1.0e-9,
        1.0e-3,
    )

    assert payload["accepted"] is False
    assert payload["rejection_reason"] == "chemical_potential_consistency"
    assert payload["material_balance_norm"] <= 1.0e-12
    assert payload["pressure_consistency_norm"] <= 1.0e12
    assert payload["chemical_potential_consistency_norm"] > 1.0e-9
    assert payload["ln_fugacity_consistency_norm"] > 1.0e-9
    assert payload["phase_distance"] > 1.0e-3
