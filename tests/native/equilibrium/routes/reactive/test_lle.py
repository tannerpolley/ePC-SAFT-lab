from __future__ import annotations

import numpy as np
import pytest

import epcsaft
from epcsaft import _core
from tests.support.equilibrium_cases import (
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


def test_reactive_lle_eos_route_builder_owns_canonical_initial_point() -> None:
    mix = _neutral_binary_mixture()
    temperature = 300.0
    target_pressure = 1.0e5
    feed = np.asarray([0.3, 0.7], dtype=float)

    contract = _core._native_reactive_lle_eos_nlp_contract(
        mix._native,
        temperature,
        target_pressure,
        feed.tolist(),
        1,
        [1.0, 1.0],
        [1.0],
        1,
        [-1.0, 1.0],
        [float(np.log(3.0))],
    )
    initial = np.asarray(contract["initial_point"], dtype=float)
    first_amounts = np.exp(initial[:2])
    second_amounts = np.exp(initial[2:4])
    first = first_amounts / np.sum(first_amounts)
    second = second_amounts / np.sum(second_amounts)

    assert contract["problem_name"] == "reactive_liquid_root_eos"
    assert contract["derivative_backend"] == "cppad_explicit_density"
    assert contract["density_backend"] == "explicit_log_density_pressure_constraint"
    assert contract["variable_model"] == "log_phase_species_amounts_plus_log_density"
    assert contract["residual_families"] == [
        "conserved_balance",
        "reaction_stationarity",
        "phase_equilibrium",
    ]
    assert contract["constraint_families"] == [
        "conserved_balance",
        "phase_pressure_consistency",
        "phase_distance",
    ]
    assert contract["variable_count"] == 2 * contract["species_count"] + 2
    assert contract["constraint_count"] == 4
    assert contract["jacobian_nonzero_count"] == 20
    assert contract["balance_row_count"] == 1
    assert contract["reaction_count"] == 1
    assert np.max(np.abs(first - second)) > 1.0e-3
    assert contract["constraint_lower_bounds"][0] == pytest.approx(0.0)
    assert contract["constraint_upper_bounds"][0] == pytest.approx(0.0)
    assert contract["constraint_lower_bounds"][1:3] == pytest.approx([0.0, 0.0])
    assert contract["constraint_upper_bounds"][1:3] == pytest.approx([0.0, 0.0])
    assert contract["constraint_lower_bounds"][-1] == pytest.approx(1.0e-8)
    assert contract["constraint_upper_bounds"][-1] > 1.0e6
    assert contract["constraints_at_initial"][0] == pytest.approx(0.0)
    assert contract["constraints_at_initial"][1:3] == pytest.approx([0.0, 0.0], abs=1.0e-12)
    assert contract["constraints_at_initial"][-1] >= contract["constraint_lower_bounds"][-1]
    assert np.all(np.asarray(contract["variable_upper_bounds"], dtype=float) < 50.0)
    assert np.asarray(contract["jacobian_values_at_initial"], dtype=float).shape == (
        contract["jacobian_nonzero_count"],
    )
    assert np.count_nonzero(np.asarray(contract["jacobian_values_at_initial"], dtype=float)) > 0

    payload = _core._native_reactive_lle_eos_route_result(
        mix._native,
        temperature,
        target_pressure,
        feed.tolist(),
        1,
        [1.0, 1.0],
        [1.0],
        1,
        [-1.0, 1.0],
        [float(np.log(3.0))],
        10,
        1.0e-8,
        0.0,
        "limited-memory",
        20,
        1.0e-8,
        1.0e-3,
        1.0e-8,
        1.0e-3,
        1.0e-12,
        [0],
        [],
        None,
    )

    assert payload["backend"] == "ipopt"
    assert payload["problem_name"] == "reactive_liquid_root_eos"
    assert payload["derivative_backend"] == "cppad_explicit_density"
    assert payload["variable_model"] == "log_phase_species_amounts_plus_log_density"
    assert payload["density_backend"] == "explicit_log_density_pressure_constraint"
    assert payload["residual_families"] == [
        "conserved_balance",
        "reaction_stationarity",
        "phase_equilibrium",
    ]
    assert payload["constraint_families"] == [
        "conserved_balance",
        "phase_pressure_consistency",
        "phase_distance",
    ]
    assert payload["exact_gradient_required"] is True
    assert payload["exact_jacobian_required"] is True
    assert payload["phase_count"] == 2
    assert payload["species_count"] == 2
    assert payload["balance_row_count"] == 1
    assert payload["reaction_count"] == 1
    if not payload["compiled"]:
        assert payload["ran"] is False
        assert payload["accepted"] is False
        assert payload["status"] == "ipopt_dependency_required"
        return

    assert payload["ran"] is True
    assert payload["status"] in {"accepted", "solver_rejected", "postsolve_rejected"}
    if payload["status"] != "solver_rejected":
        assert payload["postsolve"]["density_backend"] == "explicit_log_density_pressure_constraint"

def test_reactive_lle_eos_route_uses_exact_hessian_when_requested() -> None:
    mix = _neutral_binary_mixture()
    payload = _core._native_reactive_lle_eos_route_result(
        mix._native,
        300.0,
        1.0e5,
        [0.3, 0.7],
        1,
        [1.0, 1.0],
        [1.0],
        1,
        [-1.0, 1.0],
        [float(np.log(3.0))],
        10,
        1.0e-8,
        0.0,
        "exact",
        20,
        1.0e-8,
        1.0e-3,
        1.0e-8,
        1.0e-3,
        1.0e-12,
        [0],
        [],
        None,
    )

    if not payload["compiled"]:
        assert payload["status"] == "ipopt_dependency_required"
        return

    assert payload["ran"] is True
    assert payload["hessian_approximation"] == "exact"
    assert payload["exact_hessian_available"] is True
    assert payload["hessian_backend"] != "limited-memory"
    assert payload["eval_h_calls"] > 0
    assert payload["solver_status"] != "invalid_number_detected"
    assert payload["last_callback_exception"] == ""

def test_reactive_lle_route_records_seed_sweep_attempts_on_failure() -> None:
    mix = _neutral_binary_mixture()
    payload = _core._native_reactive_lle_eos_route_result(
        mix._native,
        300.0,
        1.0e5,
        [0.3, 0.7],
        1,
        [1.0, 1.0],
        [1.0],
        1,
        [-1.0, 1.0],
        [float(np.log(3.0))],
        0,
        1.0e-8,
        0.0,
        "limited-memory",
        2,
        1.0e-8,
        1.0e-3,
        1.0e-8,
        1.0e-3,
        1.0e-12,
        [0],
        [],
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
