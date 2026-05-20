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


def test_neutral_stability_tpd_contract_builds_exact_native_nlp() -> None:
    mix = _neutral_binary_mixture()
    feed = np.asarray([0.3, 0.7], dtype=float)

    payload = _core._native_neutral_stability_tpd_nlp_contract(
        mix._native,
        300.0,
        1.0e5,
        feed.tolist(),
        "vap",
        "vap",
    )

    initial = np.asarray(payload["initial_point"], dtype=float)
    gradient = np.asarray(payload["gradient_at_initial"], dtype=float)
    jacobian = np.asarray(payload["jacobian_values_at_initial"], dtype=float)

    assert payload["problem_name"] == "neutral_stability_tpd"
    assert payload["derivative_backend"] == "cppad_explicit_density"
    assert payload["variable_model"] == "composition_plus_log_density"
    assert payload["density_backend"] == "explicit_log_density_pressure_constraint"
    assert payload["residual_families"] == ["stability_tpd"]
    assert payload["constraint_families"] == ["composition_sum", "pressure"]
    assert payload["parent_phase"] == "vap"
    assert payload["trial_phase"] == "vap"
    assert payload["species_count"] == 2
    assert payload["variable_count"] == 3
    assert payload["constraint_count"] == 2
    assert payload["jacobian_nonzero_count"] == 6
    assert payload["feed_composition"] == pytest.approx(feed)
    assert len(payload["parent_reduced_potential"]) == 2
    assert np.all(initial[:2] > 0.0)
    assert np.isfinite(initial[2])
    assert initial[:2].sum() == pytest.approx(1.0)
    assert initial[:2] != pytest.approx(feed)
    assert payload["constraints_at_initial"] == pytest.approx([0.0, 0.0], abs=1.0e-10)
    assert np.all(np.isfinite(gradient))
    assert jacobian.reshape(2, 3)[0] == pytest.approx([1.0, 1.0, 0.0])
    assert np.all(np.isfinite(jacobian.reshape(2, 3)[1]))

def test_neutral_stability_tpd_route_result_uses_ipopt_adapter_gate() -> None:
    mix = _neutral_binary_mixture()
    payload = _core._native_neutral_stability_tpd_route_result(
        mix._native,
        300.0,
        1.0e5,
        [0.3, 0.7],
        "vap",
        "vap",
        50,
        1.0e-8,
        0.0,
        "limited-memory",
        20,
        1.0e-8,
        [],
        None,
        linear_solver="mumps",
        acceptable_tolerance=9.0e-7,
        constraint_violation_tolerance=8.0e-8,
        dual_infeasibility_tolerance=7.0e-8,
        complementarity_tolerance=6.0e-8,
    )

    assert payload["backend"] == "ipopt"
    assert payload["problem_name"] == "neutral_stability_tpd"
    assert payload["derivative_backend"] == "cppad_explicit_density"
    assert payload["parent_phase"] == "vap"
    assert payload["trial_phase"] == "vap"
    assert payload["exact_gradient_required"] is True
    assert payload["exact_jacobian_required"] is True
    if not payload["compiled"]:
        assert payload["ran"] is False
        assert payload["solver_accepted"] is False
        assert payload["accepted"] is False
        assert payload["status"] == "ipopt_dependency_required"
        assert payload["trial_composition"] == []
        return

    assert payload["ran"] is True
    if not payload["solver_accepted"]:
        assert payload["accepted"] is False
        assert payload["status"] == "solver_rejected"
        return
    assert payload["accepted"] is True
    assert payload["status"] == "accepted"
    assert np.asarray(payload["trial_composition"], dtype=float).sum() == pytest.approx(1.0, abs=1.0e-7)

def test_neutral_stability_tpd_route_uses_exact_hessian_when_requested() -> None:
    mix = _neutral_binary_mixture()
    payload = _core._native_neutral_stability_tpd_route_result(
        mix._native,
        300.0,
        1.0e5,
        [0.3, 0.7],
        "vap",
        "vap",
        30,
        1.0e-8,
        0.0,
        "exact",
        20,
        1.0e-8,
        [],
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
    assert payload["hessian_backend"] != "limited-memory"
    assert payload["eval_h_calls"] > 0

def test_electrolyte_stability_tpd_contract_adds_charge_constraint() -> None:
    mix = _ionic_mixture()
    feed = np.asarray([0.9998, 1.0e-4, 1.0e-4], dtype=float)
    charges = np.asarray([0.0, 1.0, -1.0], dtype=float)

    payload = _core._native_electrolyte_stability_tpd_nlp_contract(
        mix._native,
        298.15,
        1.013e5,
        feed.tolist(),
    )

    initial = np.asarray(payload["initial_point"], dtype=float)
    gradient = np.asarray(payload["gradient_at_initial"], dtype=float)
    jacobian = np.asarray(payload["jacobian_values_at_initial"], dtype=float).reshape(3, 4)

    assert payload["problem_name"] == "electrolyte_stability_tpd"
    assert payload["derivative_backend"] == "cppad_explicit_density"
    assert payload["variable_model"] == "composition_plus_log_density"
    assert payload["density_backend"] == "explicit_log_density_pressure_constraint"
    assert payload["residual_families"] == ["stability_tpd"]
    assert payload["constraint_families"] == ["composition_sum", "phase_charge", "pressure"]
    assert payload["parent_phase"] == "liq"
    assert payload["trial_phase"] == "liq"
    assert payload["species_count"] == 3
    assert payload["variable_count"] == 4
    assert payload["constraint_count"] == 3
    assert payload["jacobian_nonzero_count"] == 12
    assert payload["feed_composition"] == pytest.approx(feed)
    assert len(payload["parent_reduced_potential"]) == 3
    assert initial[:3] == pytest.approx(feed)
    assert np.isfinite(initial[3])
    assert np.dot(initial[:3], charges) == pytest.approx(0.0, abs=1.0e-14)
    assert payload["constraints_at_initial"] == pytest.approx([0.0, 0.0, 0.0], abs=1.0e-10)
    assert np.all(np.isfinite(gradient))
    assert jacobian[0] == pytest.approx([1.0, 1.0, 1.0, 0.0])
    assert jacobian[1] == pytest.approx([*charges, 0.0])
    assert np.all(np.isfinite(jacobian[2]))

def test_electrolyte_stability_tpd_route_result_uses_ipopt_adapter_gate() -> None:
    mix = _ionic_mixture()
    payload = _core._native_electrolyte_stability_tpd_route_result(
        mix._native,
        298.15,
        1.013e5,
        [0.9998, 1.0e-4, 1.0e-4],
        50,
        1.0e-8,
        0.0,
        "limited-memory",
        20,
        1.0e-8,
        [],
        None,
        linear_solver="mumps",
        acceptable_tolerance=9.0e-7,
        constraint_violation_tolerance=8.0e-8,
        dual_infeasibility_tolerance=7.0e-8,
        complementarity_tolerance=6.0e-8,
    )

    assert payload["backend"] == "ipopt"
    assert payload["problem_name"] == "electrolyte_stability_tpd"
    assert payload["derivative_backend"] == "cppad_explicit_density"
    assert payload["parent_phase"] == "liq"
    assert payload["trial_phase"] == "liq"
    assert payload["seed_name"] == "canonical_charge_neutral_feed"
    assert payload["exact_gradient_required"] is True
    assert payload["exact_jacobian_required"] is True
    if not payload["compiled"]:
        assert payload["ran"] is False
        assert payload["solver_accepted"] is False
        assert payload["accepted"] is False
        assert payload["status"] == "ipopt_dependency_required"
        assert payload["trial_composition"] == []
        return

    assert payload["ran"] is True
    if not payload["solver_accepted"]:
        assert payload["accepted"] is False
        assert payload["status"] == "solver_rejected"
        return
    assert payload["accepted"] is True
    assert payload["status"] == "accepted"
    trial = np.asarray(payload["trial_composition"], dtype=float)
    assert trial.sum() == pytest.approx(1.0, abs=1.0e-7)
    assert np.dot(trial, np.asarray([0.0, 1.0, -1.0])) == pytest.approx(0.0, abs=1.0e-7)

def test_electrolyte_stability_tpd_route_uses_exact_hessian_when_requested() -> None:
    mix = _ionic_mixture()
    payload = _core._native_electrolyte_stability_tpd_route_result(
        mix._native,
        298.15,
        1.013e5,
        [0.9998, 1.0e-4, 1.0e-4],
        60,
        1.0e-8,
        0.0,
        "exact",
        20,
        1.0e-8,
        [],
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
    assert payload["hessian_backend"] != "limited-memory"
    assert payload["eval_h_calls"] > 0

def test_reactive_stability_tpd_contract_uses_existing_stability_shape() -> None:
    mix = _neutral_binary_mixture()
    inputs = _reactive_stability_inputs()

    payload = _core._native_reactive_stability_tpd_nlp_contract(
        mix._native,
        300.0,
        1.0e5,
        inputs["feed_composition"],
        inputs["balance_rows"],
        inputs["balance_matrix_row_major"],
        inputs["total_vector"],
        inputs["reaction_rows"],
        inputs["reaction_stoichiometry_row_major"],
        inputs["log_equilibrium_constants"],
        "vap",
        "vap",
    )

    assert payload["problem_name"] == "reactive_stability_tpd"
    assert payload["derivative_backend"] == "cppad_explicit_density"
    assert payload["variable_model"] == "composition_plus_log_density"
    assert payload["density_backend"] == "explicit_log_density_pressure_constraint"
    assert payload["balance_row_count"] == 1
    assert payload["reaction_count"] == 1
    assert payload["residual_families"] == ["reaction_stationarity", "stability_tpd"]
    assert payload["constraint_families"] == ["composition_sum", "pressure"]
    assert payload["parent_phase"] == "vap"
    assert payload["trial_phase"] == "vap"
    assert payload["species_count"] == 2
    assert payload["variable_count"] == 3
    assert payload["constraint_count"] == 2

def test_reactive_stability_tpd_route_result_uses_ipopt_and_exact_hessian() -> None:
    mix = _neutral_binary_mixture()
    inputs = _reactive_stability_inputs()

    payload = _core._native_reactive_stability_tpd_route_result(
        mix._native,
        300.0,
        1.0e5,
        inputs["feed_composition"],
        inputs["balance_rows"],
        inputs["balance_matrix_row_major"],
        inputs["total_vector"],
        inputs["reaction_rows"],
        inputs["reaction_stoichiometry_row_major"],
        inputs["log_equilibrium_constants"],
        "vap",
        "vap",
        30,
        1.0e-8,
        0.0,
        "exact",
        10,
        1.0e-8,
        [],
        None,
    )

    assert payload["problem_name"] == "reactive_stability_tpd"
    assert payload["balance_row_count"] == 1
    assert payload["reaction_count"] == 1
    assert payload["residual_families"] == ["reaction_stationarity", "stability_tpd"]
    if not payload["compiled"]:
        assert payload["status"] == "ipopt_dependency_required"
        return

    assert payload["ran"] is True
    assert payload["solver_accepted"] is True
    assert payload["accepted"] is True
    assert payload["status"] == "accepted"
    assert payload["hessian_approximation"] == "exact"
    assert payload["exact_hessian_available"] is True
    assert payload["eval_h_calls"] > 0
    assert len(payload["reaction_residuals"]) == 1
    assert len(payload["conserved_balance_residuals"]) == 1

def test_electrolyte_stability_exact_hessian_dilute_salt_route_keeps_callback_finite() -> None:
    formula = np.asarray(
        [0.6732574103166201, 0.0354880934611478, 0.2323336121370503, 0.05892088408518178],
        dtype=float,
    )
    neutrals = formula[:3] / float(np.sum(formula[:3]))
    salt = 1.0e-6
    formula = np.asarray([*(neutrals * (1.0 - salt)), salt], dtype=float)
    feed = np.asarray([formula[0], formula[1], formula[2], formula[3], formula[3]], dtype=float)
    feed = feed / float(np.sum(feed))
    mix = epcsaft.ePCSAFTMixture.from_dataset(
        "2026_Khudaida",
        ["H2O", "Ethanol", "Butanol", "Na+", "Cl-"],
        feed,
        303.15,
    )

    payload = _core._native_electrolyte_stability_tpd_route_result(
        mix._native,
        303.15,
        1.0e5,
        feed.tolist(),
        60,
        1.0e-8,
        0.0,
        "exact",
        10,
        1.0e-8,
        feed.tolist(),
        None,
    )

    if not payload["compiled"]:
        assert payload["status"] == "ipopt_dependency_required"
        return

    assert payload["ran"] is True
    assert payload["hessian_approximation"] == "exact"
    assert payload["exact_hessian_available"] is True
    assert payload["eval_h_calls"] > 0
    assert payload["solver_status"] != "invalid_number_detected"
    if payload["solver_accepted"]:
        assert payload["last_callback_exception"] == ""
        assert payload["last_callback_failure"] == ""

def test_neutral_stability_route_records_seed_sweep_attempts_on_failure() -> None:
    mix = _neutral_binary_mixture()
    payload = _core._native_neutral_stability_tpd_route_result(
        mix._native,
        300.0,
        1.0e5,
        [0.3, 0.7],
        "vap",
        "vap",
        0,
        1.0e-8,
        0.0,
        "limited-memory",
        2,
        1.0e-8,
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
