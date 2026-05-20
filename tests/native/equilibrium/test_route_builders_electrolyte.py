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


def test_electrolyte_lle_route_contract_uses_liquid_root_transformed_variables() -> None:
    mix, feed_amounts = _ascani_electrolyte_mixture()
    temperature = 298.15
    target_pressure = 1.0e5

    payload = _core._native_electrolyte_lle_eos_nlp_contract(
        mix._native,
        temperature,
        target_pressure,
        feed_amounts,
    )

    assert payload["problem_name"] == "electrolyte_lle_eos"
    assert payload["derivative_backend"] == "cppad_explicit_density"
    assert payload["density_backend"] == "explicit_log_density_pressure_constraint"
    assert payload["residual_families"] == ["phase_equilibrium", "material_balance"]
    assert payload["constraint_families"] == [
        "phase_equilibrium",
        "phase_pressure_consistency",
        "phase_distance",
        "formula_feasibility",
    ]
    assert payload["phase_count"] == 2
    assert payload["species_count"] == 4
    assert payload["variable_model"] == "ascani_transformed_salt_pairs_explicit_density"
    assert payload["variable_count"] == 5
    assert payload["constraint_count"] == 9
    assert payload["jacobian_nonzero_count"] == 45
    assert len(payload["initial_point"]) == 5
    assert len(payload["variable_lower_bounds"]) == 5
    assert len(payload["variable_upper_bounds"]) == 5
    assert np.allclose(payload["constraint_lower_bounds"][:5], 0.0)
    assert np.allclose(payload["constraint_upper_bounds"][:5], 0.0)
    assert payload["constraint_lower_bounds"][5] >= 0.1
    assert payload["constraint_upper_bounds"][5] > 1.0e6
    assert payload["constraints_at_initial"][5] >= payload["constraint_lower_bounds"][5]
    assert np.all(np.asarray(payload["constraints_at_initial"][6:], dtype=float) > 0.0)
    payload_jacobian = np.asarray(payload["jacobian_values_at_initial"], dtype=float).reshape(
        payload["constraint_count"],
        payload["variable_count"],
    )
    assert np.all(np.isfinite(payload_jacobian))
    assert np.count_nonzero(np.abs(payload_jacobian[0]) > 0.0) > 0
    assert np.count_nonzero(np.abs(payload_jacobian[3]) > 0.0) > 0
    assert np.count_nonzero(np.abs(payload_jacobian[4]) > 0.0) > 0
    assert np.count_nonzero(np.abs(payload_jacobian[5]) > 0.0) > 0

def test_electrolyte_lle_route_result_uses_ipopt_adapter_gate_and_charge_rows() -> None:
    mix, feed = _ascani_electrolyte_mixture()
    payload = _core._native_electrolyte_lle_eos_route_result(
        mix._native,
        298.15,
        1.0e5,
        feed,
        500,
        1.0e-8,
        0.0,
        "limited-memory",
        20,
        1.0e-8,
        1.0e-3,
        1.0e-7,
        1.0e-6,
        0.1,
        None,
        linear_solver="mumps",
        acceptable_tolerance=9.0e-7,
        constraint_violation_tolerance=8.0e-8,
        dual_infeasibility_tolerance=7.0e-8,
        complementarity_tolerance=6.0e-8,
    )

    assert payload["backend"] == "ipopt"
    assert payload["problem_name"] == "electrolyte_lle_eos"
    assert payload["derivative_backend"] == "cppad_explicit_density"
    assert payload["variable_model"] == "ascani_transformed_salt_pairs_explicit_density"
    assert payload["density_backend"] == "explicit_log_density_pressure_constraint"
    assert payload["residual_families"] == ["phase_equilibrium", "material_balance"]
    assert payload["constraint_families"] == [
        "phase_equilibrium",
        "phase_pressure_consistency",
        "phase_distance",
        "formula_feasibility",
    ]
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
    assert payload["solver_accepted"] is True
    assert payload["accepted"] is True
    assert payload["status"] == "accepted"
    assert np.asarray(payload["variables"], dtype=float).shape == (5,)
    assert np.asarray(payload["constraints"], dtype=float).shape == (9,)
    assert np.asarray(payload["phase_amounts"], dtype=float).shape == (2, 4)
    assert np.asarray(payload["phase_volumes"], dtype=float).shape == (2,)
    assert payload["postsolve"]["derivative_backend"] == "cppad_explicit_density"
    assert payload["postsolve"]["density_backend"] == "explicit_log_density_pressure_constraint"
    assert payload["postsolve"]["charge_balance_norm"] <= 1.0e-8
    assert payload["postsolve"]["material_balance_norm"] <= 1.0e-8
    assert payload["postsolve"]["ln_fugacity_consistency_norm"] <= 1.0e-6
    assert payload["postsolve"]["phase_distance"] >= 0.1

    phase_compositions = np.asarray(payload["postsolve"]["phase_compositions"], dtype=float)
    phase_amounts = np.asarray(payload["phase_amounts"], dtype=float)
    phase_volumes = np.asarray(payload["phase_volumes"], dtype=float)
    route_densities = phase_amounts.sum(axis=1) / phase_volumes
    for composition, route_density in zip(phase_compositions, route_densities, strict=True):
        liquid_density = mix.state(T=298.15, P=1.0e5, x=composition, phase="liq").density()
        vapor_density = mix.state(T=298.15, P=1.0e5, x=composition, phase="vap").density()
        assert route_density == pytest.approx(liquid_density, rel=1.0e-10)
        assert route_density / vapor_density > 100.0

def test_electrolyte_lle_route_uses_exact_hessian_when_requested() -> None:
    mix, feed = _ascani_electrolyte_mixture()
    payload = _core._native_electrolyte_lle_eos_route_result(
        mix._native,
        298.15,
        1.0e5,
        feed,
        500,
        1.0e-8,
        0.0,
        "exact",
        20,
        1.0e-8,
        1.0e-3,
        1.0e-7,
        1.0e-6,
        0.1,
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

def test_electrolyte_lle_exact_hessian_dilute_salt_route_keeps_callback_finite() -> None:
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

    payload = _core._native_electrolyte_lle_eos_route_result(
        mix._native,
        303.15,
        1.0e5,
        feed.tolist(),
        20,
        1.0e-8,
        0.0,
        "exact",
        20,
        1.0e-7,
        1.0e-3,
        1.0e-7,
        1.0e-6,
        0.1,
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
    assert payload["last_callback_exception"] == ""

def test_electrolyte_bubble_pressure_contract_adds_phase_charge_rows() -> None:
    mix = _ionic_mixture()
    temperature = 298.15
    liquid_composition = np.asarray([0.9998, 1.0e-4, 1.0e-4], dtype=float)
    charges = np.asarray([0.0, 1.0, -1.0], dtype=float)

    payload = _core._native_electrolyte_bubble_p_eos_nlp_contract(
        mix._native,
        temperature,
        liquid_composition.tolist(),
    )

    initial = np.asarray(payload["initial_point"], dtype=float)
    jacobian = _dense_jacobian_from_sparse_contract(payload)
    local_variable_count = liquid_composition.size + 1
    liquid_amounts = initial[: liquid_composition.size]
    vapor_amounts = initial[local_variable_count : local_variable_count + liquid_composition.size]
    charge_row_start = liquid_composition.size - 1 + 2

    assert payload["problem_name"] == "electrolyte_bubble_p_eos"
    assert payload["derivative_backend"] == "analytic_cppad"
    assert payload["phase_count"] == 2
    assert payload["species_count"] == 3
    assert payload["variable_count"] == 9
    assert payload["constraint_count"] == 12
    assert payload["jacobian_nonzero_count"] == 52
    assert np.all(initial > 0.0)
    assert liquid_amounts / liquid_amounts.sum() == pytest.approx(liquid_composition)
    assert liquid_amounts @ charges == pytest.approx(0.0, abs=1.0e-14)
    assert vapor_amounts @ charges == pytest.approx(0.0, abs=1.0e-14)
    assert payload["constraints_at_initial"][: charge_row_start + 2] == pytest.approx(
        [0.0] * (charge_row_start + 2),
        abs=1.0e-14,
    )
    assert jacobian[charge_row_start, : liquid_composition.size] == pytest.approx(charges)
    assert jacobian[charge_row_start + 1, local_variable_count : local_variable_count + liquid_composition.size] == (
        pytest.approx(charges)
    )

def test_electrolyte_bubble_pressure_route_uses_exact_hessian_when_requested() -> None:
    mix = _ionic_mixture()
    payload = _core._native_electrolyte_bubble_p_eos_route_result(
        mix._native,
        298.15,
        [0.9998, 1.0e-4, 1.0e-4],
        30,
        1.0e-8,
        "exact",
        20,
        1.0e-7,
        1.0e-5,
        1.0e-7,
        1.0e-4,
        1.0e-7,
        None,
    )

    if not payload["compiled"]:
        assert payload["status"] == "ipopt_dependency_required"
        return

    assert payload["ran"] is True
    assert payload["problem_name"] == "electrolyte_bubble_p_eos"
    assert payload["hessian_approximation"] == "exact"
    assert payload["exact_hessian_available"] is True
    assert payload["hessian_backend"] != "limited-memory"
    assert payload["eval_h_calls"] > 0
    assert payload["solver_status"] != "invalid_number_detected"
    assert payload["last_callback_exception"] == ""

def test_electrolyte_lle_route_records_formula_seed_attempts_on_failure() -> None:
    mix, feed = _ascani_electrolyte_mixture()
    payload = _core._native_electrolyte_lle_eos_route_result(
        mix._native,
        298.15,
        1.0e5,
        feed,
        0,
        1.0e-8,
        0.0,
        "limited-memory",
        2,
        1.0e-8,
        1.0e-8,
        1.0e-8,
        1.0e-6,
        0.1,
        None,
    )

    if not payload["compiled"]:
        assert payload["status"] == "ipopt_dependency_required"
        return

    assert payload["initial_point_strategy"] == "deterministic_seed_sweep"
    assert payload["seed_name"] in {"canonical_formula_shift", "mirrored_formula_shift"}
    attempts = payload["seed_attempts"]
    assert len(attempts) >= 2
    assert attempts[0]["seed_name"] == "canonical_formula_shift"
    assert {attempt["seed_name"] for attempt in attempts} >= {
        "canonical_formula_shift",
        "mirrored_formula_shift",
    }
