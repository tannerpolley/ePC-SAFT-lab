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


def test_neutral_lle_route_uses_exact_hessian_when_requested() -> None:
    mix = _nonideal_lle_binary_mixture()
    payload = _core._native_neutral_lle_eos_route_result(
        mix._native,
        300.0,
        5.0e6,
        [0.5, 0.5],
        100,
        1.0e-8,
        0.0,
        "exact",
        20,
        1.0e-7,
        1.0e-2,
        1.0e-7,
        1.0e-4,
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
    assert payload["postsolve"]["phase_distance"] > 0.9
    assert payload["postsolve"]["chemical_potential_consistency_norm"] <= 1.0e-7

@pytest.mark.parametrize("hessian_mode", ["auto", "exact"])
def test_neutral_lle_associating_route_uses_exact_hessian(hessian_mode: str) -> None:
    mix = _methanol_cyclohexane_mixture()
    payload = _core._native_neutral_lle_eos_route_result(
        mix._native,
        298.15,
        1.013e5,
        _methanol_cyclohexane_lle_feed(),
        30,
        1.0e-8,
        0.0,
        hessian_mode,
        5,
        1.0e-7,
        1.0e-2,
        1.0e-7,
        1.0e-4,
        None,
    )

    if not payload["compiled"]:
        assert payload["status"] == "ipopt_dependency_required"
        return

    assert payload["ran"] is True
    assert payload["hessian_approximation"] == "exact"
    assert payload["exact_hessian_available"] is True
    assert payload["hessian_backend"] == "cppad_phase_system"
    assert payload["eval_h_calls"] > 0

def test_neutral_lle_route_contract_builds_native_initial_point_from_feed() -> None:
    mix = _neutral_binary_mixture()
    temperature = 298.15
    target_pressure = 1.013e5
    feed_amounts = np.asarray([0.45, 0.55], dtype=float)

    payload = _core._native_neutral_lle_eos_nlp_contract(
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
    assert np.all(phase_amounts > 0.0)
    assert np.all(volumes > 0.0)
    assert np.sum(phase_amounts, axis=0) == pytest.approx(feed_amounts)
    assert phase_compositions[0] != pytest.approx(phase_compositions[1])
    assert np.asarray(payload["constraints_at_initial"], dtype=float)[:2] == pytest.approx([0.0, 0.0])
    assert payload["constraint_lower_bounds"][-1] == pytest.approx(1.0e-8)
    assert payload["constraint_upper_bounds"][-1] > 1.0e6
    assert payload["constraints_at_initial"][-1] >= payload["constraint_lower_bounds"][-1]

def test_neutral_lle_route_result_uses_ipopt_adapter_gate() -> None:
    mix = _neutral_binary_mixture()
    payload = _core._native_neutral_lle_eos_route_result(
        mix._native,
        298.15,
        1.013e5,
        [0.45, 0.55],
        30,
        1.0e-8,
        0.0,
        "limited-memory",
        20,
        1.0e-7,
        1.0e-5,
        1.0e-7,
        1.0e-4,
        None,
        linear_solver="mumps",
        acceptable_tolerance=9.0e-7,
        constraint_violation_tolerance=8.0e-8,
        dual_infeasibility_tolerance=7.0e-8,
        complementarity_tolerance=6.0e-8,
    )

    assert payload["backend"] == "ipopt"
    assert payload["problem_name"] == "neutral_two_phase_eos"
    assert payload["derivative_backend"] == "analytic_cppad"
    assert payload["exact_gradient_required"] is True
    assert payload["exact_jacobian_required"] is True
    if not payload["compiled"]:
        assert payload["ran"] is False
        assert payload["accepted"] is False
        assert payload["status"] == "ipopt_dependency_required"
        return

    assert payload["ran"] is True
    if not payload["solver_accepted"]:
        assert payload["accepted"] is False
        assert payload["status"] == "solver_rejected"
        assert payload["phase_amounts"] == []
        assert payload["phase_volumes"] == []
        return

    assert np.asarray(payload["phase_amounts"], dtype=float).shape == (2, 2)
    assert np.asarray(payload["phase_volumes"], dtype=float).shape == (2,)
    assert payload["status"] in {"accepted", "solver_rejected", "postsolve_rejected"}

def test_neutral_lle_route_result_records_seed_sweep_attempts_on_failure() -> None:
    mix = _neutral_binary_mixture()
    payload = _core._native_neutral_lle_eos_route_result(
        mix._native,
        298.15,
        1.013e5,
        [0.45, 0.55],
        0,
        1.0e-8,
        0.0,
        "limited-memory",
        2,
        1.0e-8,
        1.0e-8,
        1.0e-8,
        1.0e-3,
        None,
    )

    if not payload["compiled"]:
        assert payload["status"] == "ipopt_dependency_required"
        return

    assert payload["initial_point_strategy"] == "deterministic_seed_sweep"
    assert payload["seed_name"] in {"canonical_shifted_feed", "mirrored_shifted_feed"}
    attempts = payload["seed_attempts"]
    assert len(attempts) >= 2
    assert attempts[0]["seed_name"] == "canonical_shifted_feed"
    assert {attempt["seed_name"] for attempt in attempts} >= {
        "canonical_shifted_feed",
        "mirrored_shifted_feed",
    }
    assert all("status" in attempt for attempt in attempts)
    assert all("iteration_count" in attempt for attempt in attempts)
