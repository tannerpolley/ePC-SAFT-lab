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


def test_reactive_two_phase_eos_contract_uses_conserved_balances_and_standard_potentials() -> None:
    mix = _neutral_binary_mixture()
    temperature = 300.0
    phase_amounts = [
        np.asarray([0.1, 0.4], dtype=float),
        np.asarray([0.2, 0.3], dtype=float),
    ]
    volumes = [float(phase_amounts[0].sum() / 80.0), float(phase_amounts[1].sum() / 120.0)]
    species_totals = phase_amounts[0] + phase_amounts[1]
    target_pressure = mix.state(
        T=temperature,
        rho=phase_amounts[0].sum() / volumes[0],
        x=phase_amounts[0] / phase_amounts[0].sum(),
        phase="liquid",
    ).pressure()

    payload = _core._native_reactive_two_phase_eos_nlp_contract(
        mix._native,
        temperature,
        target_pressure,
        [phase.tolist() for phase in phase_amounts],
        volumes,
        1,
        [1.0, 1.0],
        [float(species_totals.sum())],
        1,
        [-1.0, 1.0],
        [float(np.log(3.0))],
    )
    phase_system = _core._native_eos_phase_system(
        mix._native,
        temperature,
        target_pressure,
        [phase.tolist() for phase in phase_amounts],
        volumes,
        species_totals.tolist(),
    )

    standard_mu = np.asarray(payload["standard_mu_rt"], dtype=float)
    base_gradient = np.asarray(phase_system["gradient"], dtype=float)
    expected_gradient = base_gradient.copy()
    expected_gradient[:2] += standard_mu
    expected_gradient[3:5] += standard_mu
    expected_objective = phase_system["objective"] + float(standard_mu @ species_totals)
    contract_jacobian = _dense_jacobian_from_sparse_contract(payload)
    phase_system_jacobian = np.asarray(phase_system["constraint_jacobian_row_major"], dtype=float).reshape(4, 6)

    assert payload["problem_name"] == "reactive_two_phase_eos"
    assert payload["derivative_backend"] == "analytic_cppad"
    assert payload["variable_model"] == "phase_species_amounts_plus_phase_volume"
    assert payload["density_backend"] == "explicit_phase_volume_pressure_constraint"
    assert payload["residual_families"] == [
        "conserved_balance",
        "reaction_stationarity",
        "phase_pressure_consistency",
        "phase_equilibrium",
        "phase_distance",
    ]
    assert payload["constraint_families"] == ["conserved_balance", "phase_pressure_consistency"]
    assert payload["phase_count"] == 2
    assert payload["species_count"] == 2
    assert payload["balance_row_count"] == 1
    assert payload["reaction_count"] == 1
    assert payload["variable_count"] == 6
    assert payload["constraint_count"] == 3
    assert payload["jacobian_nonzero_count"] == 10
    assert payload["objective_at_initial"] == pytest.approx(expected_objective, rel=1.0e-12, abs=1.0e-10)
    assert payload["gradient_at_initial"] == pytest.approx(expected_gradient, rel=1.0e-12, abs=1.0e-10)
    assert payload["constraints_at_initial"][0] == pytest.approx(0.0, abs=1.0e-12)
    assert payload["constraints_at_initial"][1:] == pytest.approx(
        phase_system["constraints"][2:],
        rel=1.0e-12,
        abs=1.0e-8,
    )
    assert standard_mu[1] - standard_mu[0] == pytest.approx(-np.log(3.0))
    assert contract_jacobian[0] == pytest.approx([1.0, 1.0, 0.0, 1.0, 1.0, 0.0])
    assert contract_jacobian[1:] == pytest.approx(phase_system_jacobian[2:], rel=1.0e-12, abs=1.0e-8)

def test_reactive_two_phase_eos_postsolve_checks_reaction_stationarity() -> None:
    mix = _neutral_binary_mixture()
    temperature = 300.0
    phase_amounts = [
        np.asarray([0.1, 0.4], dtype=float),
        np.asarray([0.2, 0.3], dtype=float),
    ]
    volumes = [float(phase_amounts[0].sum() / 80.0), float(phase_amounts[1].sum() / 120.0)]
    species_totals = phase_amounts[0] + phase_amounts[1]
    target_pressure = mix.state(
        T=temperature,
        rho=phase_amounts[0].sum() / volumes[0],
        x=phase_amounts[0] / phase_amounts[0].sum(),
        phase="liquid",
    ).pressure()

    payload = _core._native_reactive_two_phase_eos_postsolve(
        mix._native,
        temperature,
        target_pressure,
        [phase.tolist() for phase in phase_amounts],
        volumes,
        1,
        [1.0, 1.0],
        [float(species_totals.sum())],
        1,
        [-1.0, 1.0],
        [float(np.log(3.0))],
        1.0e-12,
        1.0e12,
        1.0e-12,
        1.0e-3,
    )

    assert payload["derivative_backend"] == "analytic_cppad"
    assert payload["phase_count"] == 2
    assert payload["species_count"] == 2
    assert payload["balance_row_count"] == 1
    assert payload["reaction_count"] == 1
    assert payload["conserved_balance_norm"] == pytest.approx(0.0, abs=1.0e-12)
    assert np.isfinite(payload["pressure_consistency_norm"])
    assert payload["reaction_stationarity_norm"] > 1.0e-12
    assert payload["phase_distance"] > 1.0e-3
    assert payload["accepted"] is False
    assert payload["rejection_reason"] == "reaction_stationarity"
    assert len(payload["constraints"]) == 3
    assert len(payload["reaction_stationarity_residuals"]) == 2

def test_reactive_two_phase_eos_postsolve_accepts_candidate_under_declared_tolerances() -> None:
    mix = _neutral_binary_mixture()
    temperature = 300.0
    phase_amounts = [
        np.asarray([0.1, 0.4], dtype=float),
        np.asarray([0.2, 0.3], dtype=float),
    ]
    volumes = [float(phase_amounts[0].sum() / 80.0), float(phase_amounts[1].sum() / 120.0)]
    species_totals = phase_amounts[0] + phase_amounts[1]
    target_pressure = mix.state(
        T=temperature,
        rho=phase_amounts[0].sum() / volumes[0],
        x=phase_amounts[0] / phase_amounts[0].sum(),
        phase="liquid",
    ).pressure()

    payload = _core._native_reactive_two_phase_eos_postsolve(
        mix._native,
        temperature,
        target_pressure,
        [phase.tolist() for phase in phase_amounts],
        volumes,
        1,
        [1.0, 1.0],
        [float(species_totals.sum())],
        1,
        [-1.0, 1.0],
        [float(np.log(3.0))],
        1.0e-12,
        1.0e12,
        1.0e12,
        1.0e-3,
    )

    assert payload["derivative_backend"] == "analytic_cppad"
    assert payload["accepted"] is True
    assert payload["rejection_reason"] == "accepted"
    assert payload["conserved_balance_norm"] == pytest.approx(0.0, abs=1.0e-12)
    assert payload["phase_distance"] > 1.0e-3

def test_reactive_electrolyte_two_phase_eos_postsolve_rejects_phase_charge_imbalance() -> None:
    species = ["A", "B", "C+", "D-"]
    feed = np.asarray([0.5, 0.3, 0.1, 0.1], dtype=float)
    mix = epcsaft.ePCSAFTMixture.from_params(
        {
            "MW": np.asarray([18.0e-3, 74.0e-3, 23.0e-3, 35.5e-3]),
            "m": np.asarray([1.1, 1.4, 1.0, 1.0]),
            "s": np.asarray([3.0, 3.4, 3.0, 3.0]),
            "e": np.asarray([180.0, 220.0, 150.0, 150.0]),
            "k_ij": np.zeros((4, 4)),
            "z": np.asarray([0.0, 0.0, 1.0, -1.0]),
            "dielc": np.asarray([80.0, 12.0, 1.0, 1.0]),
        },
        species=species,
    )
    phase_amounts = [
        np.asarray([0.2, 0.1, 0.08, 0.02], dtype=float),
        feed - np.asarray([0.2, 0.1, 0.08, 0.02], dtype=float),
    ]
    volumes = [float(phase_amounts[0].sum() / 80.0), float(phase_amounts[1].sum() / 120.0)]

    payload = _core._native_reactive_electrolyte_two_phase_eos_postsolve(
        mix._native,
        298.15,
        1.013e5,
        [phase.tolist() for phase in phase_amounts],
        volumes,
        3,
        [1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0],
        [float(feed[0] + feed[1]), float(feed[2]), float(feed[3])],
        1,
        [-1.0, 1.0, 0.0, 0.0],
        [float(np.log(0.2))],
        1.0e-12,
        1.0e12,
        1.0e12,
        1.0e-3,
    )

    assert payload["derivative_backend"] == "analytic_cppad"
    assert payload["accepted"] is False
    assert payload["rejection_reason"] == "charge_balance"
    assert payload["conserved_balance_norm"] == pytest.approx(0.0, abs=1.0e-12)
    assert payload["charge_balance_norm"] > 1.0e-12

def test_reactive_two_phase_eos_route_result_uses_native_ipopt_gate() -> None:
    mix = _neutral_binary_mixture()
    temperature = 300.0
    phase_amounts = [
        np.asarray([0.1, 0.4], dtype=float),
        np.asarray([0.2, 0.3], dtype=float),
    ]
    volumes = [float(phase_amounts[0].sum() / 80.0), float(phase_amounts[1].sum() / 120.0)]
    species_totals = phase_amounts[0] + phase_amounts[1]
    target_pressure = mix.state(
        T=temperature,
        rho=phase_amounts[0].sum() / volumes[0],
        x=phase_amounts[0] / phase_amounts[0].sum(),
        phase="liquid",
    ).pressure()

    payload = _core._native_reactive_two_phase_eos_route_result(
        mix._native,
        temperature,
        target_pressure,
        [phase.tolist() for phase in phase_amounts],
        volumes,
        1,
        [1.0, 1.0],
        [float(species_totals.sum())],
        1,
        [-1.0, 1.0],
        [float(np.log(3.0))],
        10,
        1.0e-8,
        0.0,
        "limited-memory",
        20,
        1.0e-8,
        1.0e-6,
        1.0e-6,
        1.0e-3,
        None,
        linear_solver="mumps",
        acceptable_tolerance=9.0e-7,
        constraint_violation_tolerance=8.0e-8,
        dual_infeasibility_tolerance=7.0e-8,
        complementarity_tolerance=6.0e-8,
    )

    assert payload["backend"] == "ipopt"
    assert payload["problem_name"] == "reactive_two_phase_eos"
    assert payload["derivative_backend"] == "analytic_cppad"
    assert payload["variable_model"] == "phase_species_amounts_plus_phase_volume"
    assert payload["density_backend"] == "explicit_phase_volume_pressure_constraint"
    assert payload["residual_families"] == [
        "conserved_balance",
        "reaction_stationarity",
        "phase_pressure_consistency",
        "phase_equilibrium",
        "phase_distance",
    ]
    assert payload["constraint_families"] == ["conserved_balance", "phase_pressure_consistency"]
    assert payload["exact_gradient_required"] is True
    assert payload["exact_jacobian_required"] is True
    assert payload["phase_count"] == 2
    assert payload["species_count"] == 2
    assert payload["balance_row_count"] == 1
    assert payload["reaction_count"] == 1
    standard_mu = np.asarray(payload["standard_mu_rt"], dtype=float)
    assert standard_mu[1] - standard_mu[0] == pytest.approx(-np.log(3.0))
    if not payload["compiled"]:
        assert payload["ran"] is False
        assert payload["accepted"] is False
        assert payload["status"] == "ipopt_dependency_required"
        assert payload["postsolve"]["accepted"] is False
        return

    assert payload["ran"] is True
    assert payload["status"] in {"accepted", "solver_rejected"}

def test_reactive_two_phase_eos_route_uses_exact_hessian_when_requested() -> None:
    mix = _neutral_binary_mixture()
    payload = _core._native_reactive_two_phase_eos_route_result(
        mix._native,
        300.0,
        1.0e5,
        [[0.1, 0.4], [0.2, 0.3]],
        [0.005, 0.004],
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
        1.0e-6,
        1.0e-6,
        1.0e-3,
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
