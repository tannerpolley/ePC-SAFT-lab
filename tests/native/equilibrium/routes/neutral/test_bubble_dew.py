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


def test_neutral_bubble_pressure_workbook_seed_uses_phase_density_roots() -> None:
    mix = _hydrocarbon_workbook_mixture()
    temperature = WORKBOOK_TEMPERATURE
    liquid_composition = np.asarray(WORKBOOK_LIQUID_COMPOSITION, dtype=float)

    payload = _core._native_neutral_bubble_p_eos_nlp_contract(
        mix._native,
        temperature,
        liquid_composition.tolist(),
    )

    initial = np.asarray(payload["initial_point"], dtype=float)
    local_variable_count = liquid_composition.size + 1
    liquid_amounts = initial[: liquid_composition.size]
    vapor_amounts = initial[local_variable_count : local_variable_count + liquid_composition.size]
    liquid_volume = initial[local_variable_count - 1]
    vapor_volume = initial[2 * local_variable_count - 1]
    seed_pressure = initial[-1]
    liquid_x = liquid_amounts / liquid_amounts.sum()
    vapor_y = vapor_amounts / vapor_amounts.sum()
    densities = np.asarray([liquid_amounts.sum() / liquid_volume, vapor_amounts.sum() / vapor_volume])
    expected_densities = np.asarray(
        [
            mix.state(T=temperature, P=seed_pressure, x=liquid_x, phase="liq").density(),
            mix.state(T=temperature, P=seed_pressure, x=vapor_y, phase="vap").density(),
        ]
    )
    pressure_residuals = np.asarray(payload["constraints_at_initial"], dtype=float)[4:6]

    assert payload["problem_name"] == "neutral_bubble_p_eos"
    assert seed_pressure == pytest.approx(1.0e5)
    assert liquid_x == pytest.approx(liquid_composition)
    assert densities == pytest.approx(expected_densities, rel=1.0e-10)
    assert densities[0] > 10_000.0
    assert 1.0 < densities[1] < 200.0
    assert densities[0] > densities[1]
    assert np.max(np.abs(pressure_residuals)) / seed_pressure <= 1.0e-11

def test_neutral_bubble_pressure_workbook_accepted_point_runs_postsolve() -> None:
    mix = _hydrocarbon_workbook_mixture()
    liquid_composition = WORKBOOK_LIQUID_COMPOSITION

    payload = _core._native_neutral_bubble_p_eos_route_result(
        mix._native,
        WORKBOOK_TEMPERATURE,
        liquid_composition,
        200,
        1.0e-8,
        0.0,
        "auto",
        4,
        1.0e-8,
        1.0e-3,
        1.0e-8,
        1.0e-8,
        None,
    )

    if not payload["compiled"]:
        assert payload["status"] == "ipopt_dependency_required"
        return

    phase_amounts = np.asarray(payload["phase_amounts"], dtype=float)
    phase_volumes = np.asarray(payload["phase_volumes"], dtype=float)
    vapor_composition = phase_amounts[1] / np.sum(phase_amounts[1])
    densities = phase_amounts.sum(axis=1) / phase_volumes

    assert payload["status"] == "accepted"
    assert payload["accepted"] is True
    assert payload["solver_status"] in {"success", "acceptable_point", "feasible_point_found"}
    assert payload["solver_accepted"] is True
    assert payload["seed_name"] in {"canonical_phase_density_root", "mirrored_phase_density_root"}
    assert payload["hessian_approximation"] == "exact"
    assert payload["exact_hessian_available"] is True
    assert payload["eval_h_calls"] > 0
    assert payload["variables"][-1] == pytest.approx(WORKBOOK_BUBBLE_PRESSURE, rel=5.0e-5)
    assert phase_amounts[0] / np.sum(phase_amounts[0]) == pytest.approx(liquid_composition, abs=1.0e-10)
    assert vapor_composition == pytest.approx(WORKBOOK_VAPOR_COMPOSITION, rel=5.0e-5, abs=5.0e-7)
    assert densities == pytest.approx([WORKBOOK_LIQUID_DENSITY, WORKBOOK_VAPOR_DENSITY], rel=5.0e-5)

@pytest.mark.parametrize(
    ("binding_name", "problem_name"),
    [
        ("_native_neutral_bubble_p_eos_nlp_contract", "neutral_bubble_p_eos"),
        ("_native_neutral_dew_p_eos_nlp_contract", "neutral_dew_p_eos"),
    ],
)
def test_neutral_fixed_temperature_pressure_route_contract_pins_specified_phase(
    binding_name: str,
    problem_name: str,
) -> None:
    mix = _neutral_binary_mixture()
    temperature = 300.0
    composition = np.asarray([0.35, 0.65], dtype=float)

    payload = getattr(_core, binding_name)(
        mix._native,
        temperature,
        composition.tolist(),
    )

    initial = np.asarray(payload["initial_point"], dtype=float)
    jacobian = _dense_jacobian_from_sparse_contract(payload)
    local_variable_count = composition.size + 1
    pressure_col = payload["variable_count"] - 1
    first_amounts = initial[: composition.size]
    second_amounts = initial[local_variable_count : local_variable_count + composition.size]
    fixed_amounts = first_amounts if "bubble" in problem_name else second_amounts
    liquid_volume_col = local_variable_count - 1
    vapor_volume_col = 2 * local_variable_count - 1
    lower_bounds = np.asarray(payload["variable_lower_bounds"], dtype=float)
    upper_bounds = np.asarray(payload["variable_upper_bounds"], dtype=float)

    assert payload["problem_name"] == problem_name
    assert payload["derivative_backend"] == "analytic_cppad"
    assert payload["variable_model"] == "phase_species_amounts_plus_phase_volume_plus_pressure"
    assert payload["density_backend"] == "explicit_phase_volume_pressure_constraint"
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
    assert payload["phase_count"] == 2
    assert payload["species_count"] == composition.size
    assert payload["variable_count"] == 2 * local_variable_count + 1
    assert payload["constraint_count"] == 2 * composition.size + 4
    assert payload["jacobian_nonzero_count"] == 28
    assert np.all(initial > 0.0)
    assert fixed_amounts / fixed_amounts.sum() == pytest.approx(composition)
    assert payload["constraints_at_initial"][: composition.size + 1] == pytest.approx([0.0, 0.0, 0.0])
    pressure_row_start = composition.size + 1
    assert jacobian[pressure_row_start, pressure_col] == pytest.approx(-1.0)
    assert jacobian[pressure_row_start + 1, pressure_col] == pytest.approx(-1.0)
    assert payload["constraint_lower_bounds"][-1] > 0.0
    assert payload["constraint_upper_bounds"][-1] > payload["constraint_lower_bounds"][-1]
    assert payload["constraints_at_initial"][-1] >= payload["constraint_lower_bounds"][-1]
    assert jacobian[-1, local_variable_count - 1] == pytest.approx(-1.0)
    assert jacobian[-1, 2 * local_variable_count - 1] == pytest.approx(1.0)
    assert lower_bounds[liquid_volume_col] <= initial[liquid_volume_col] <= upper_bounds[liquid_volume_col]
    assert lower_bounds[vapor_volume_col] <= initial[vapor_volume_col] <= upper_bounds[vapor_volume_col]
    assert upper_bounds[liquid_volume_col] < lower_bounds[vapor_volume_col]

@pytest.mark.parametrize(
    ("binding_name", "problem_name"),
    [
        ("_native_neutral_bubble_t_eos_nlp_contract", "neutral_bubble_t_eos"),
        ("_native_neutral_dew_t_eos_nlp_contract", "neutral_dew_t_eos"),
    ],
)
def test_neutral_fixed_pressure_temperature_route_contract_pins_specified_phase(
    binding_name: str,
    problem_name: str,
) -> None:
    mix = _neutral_binary_mixture()
    pressure = 1.0e5
    composition = np.asarray([0.35, 0.65], dtype=float)

    payload = getattr(_core, binding_name)(
        mix._native,
        pressure,
        composition.tolist(),
    )

    initial = np.asarray(payload["initial_point"], dtype=float)
    jacobian = _dense_jacobian_from_sparse_contract(payload)
    local_variable_count = composition.size + 1
    temperature_col = payload["variable_count"] - 1
    first_amounts = initial[: composition.size]
    second_amounts = initial[local_variable_count : local_variable_count + composition.size]
    fixed_amounts = first_amounts if "bubble" in problem_name else second_amounts

    assert payload["problem_name"] == problem_name
    assert payload["derivative_backend"] == "analytic_cppad"
    assert payload["variable_model"] == "phase_species_amounts_plus_phase_volume_plus_temperature"
    assert payload["density_backend"] == "explicit_phase_volume_pressure_constraint"
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
    assert payload["phase_count"] == 2
    assert payload["species_count"] == composition.size
    assert payload["variable_count"] == 2 * local_variable_count + 1
    assert payload["constraint_count"] == 2 * composition.size + 4
    assert payload["jacobian_nonzero_count"] == 30
    assert np.all(initial > 0.0)
    assert initial[temperature_col] == pytest.approx(300.0)
    assert fixed_amounts / fixed_amounts.sum() == pytest.approx(composition)
    assert payload["constraints_at_initial"][: composition.size + 1] == pytest.approx([0.0, 0.0, 0.0])
    pressure_row_start = composition.size + 1
    assert np.isfinite(jacobian[pressure_row_start, temperature_col])
    assert np.isfinite(jacobian[pressure_row_start + 1, temperature_col])
    assert payload["constraint_lower_bounds"][-1] > 0.0
    assert payload["constraint_upper_bounds"][-1] > payload["constraint_lower_bounds"][-1]
    assert payload["constraints_at_initial"][-1] >= payload["constraint_lower_bounds"][-1]
    assert jacobian[-1, local_variable_count - 1] == pytest.approx(-1.0)
    assert jacobian[-1, 2 * local_variable_count - 1] == pytest.approx(1.0)

@pytest.mark.parametrize(
    ("binding_name", "problem_name"),
    [
        ("_native_neutral_bubble_p_eos_route_result", "neutral_bubble_p_eos"),
        ("_native_neutral_dew_p_eos_route_result", "neutral_dew_p_eos"),
    ],
)
def test_neutral_fixed_temperature_pressure_route_result_uses_ipopt_adapter_gate(
    binding_name: str,
    problem_name: str,
) -> None:
    mix = _neutral_binary_mixture()
    payload = getattr(_core, binding_name)(
        mix._native,
        300.0,
        [0.35, 0.65],
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
    )

    assert payload["backend"] == "ipopt"
    assert payload["problem_name"] == problem_name
    assert payload["derivative_backend"] == "analytic_cppad"
    assert payload["exact_gradient_required"] is True
    assert payload["exact_jacobian_required"] is True
    if not payload["compiled"]:
        assert payload["ran"] is False
        assert payload["solver_accepted"] is False
        assert payload["accepted"] is False
        assert payload["status"] == "ipopt_dependency_required"
        assert payload["phase_amounts"] == []
        assert payload["phase_volumes"] == []
        assert "fixed_composition_norm" in payload["postsolve"]
        assert "phase_amount_total_norm" in payload["postsolve"]
        return

    assert payload["ran"] is True
    if not payload["solver_accepted"]:
        assert payload["accepted"] is False
        assert payload["status"] == "solver_rejected"
        return

    assert np.asarray(payload["variables"], dtype=float).shape == (7,)
    assert np.asarray(payload["phase_amounts"], dtype=float).shape == (2, 2)
    assert np.asarray(payload["phase_volumes"], dtype=float).shape == (2,)
    assert payload["postsolve"]["derivative_backend"] == "analytic_cppad"
    assert payload["status"] in {"accepted", "solver_rejected", "postsolve_rejected"}

@pytest.mark.parametrize(
    ("binding_name", "problem_name"),
    [
        ("_native_neutral_bubble_p_eos_route_result", "neutral_bubble_p_eos"),
        ("_native_neutral_dew_p_eos_route_result", "neutral_dew_p_eos"),
    ],
)
def test_neutral_fixed_temperature_pressure_route_uses_exact_hessian_when_requested(
    binding_name: str,
    problem_name: str,
) -> None:
    mix = _neutral_binary_mixture()
    payload = getattr(_core, binding_name)(
        mix._native,
        300.0,
        [0.35, 0.65],
        30,
        1.0e-8,
        0.0,
        "exact",
        20,
        1.0e-7,
        1.0e-5,
        1.0e-7,
        1.0e-4,
        None,
    )

    if not payload["compiled"]:
        assert payload["status"] == "ipopt_dependency_required"
        return

    assert payload["ran"] is True
    assert payload["problem_name"] == problem_name
    assert payload["hessian_approximation"] == "exact"
    assert payload["exact_hessian_available"] is True
    assert payload["hessian_backend"] != "limited-memory"
    assert payload["eval_h_calls"] > 0
    assert payload["solver_status"] != "invalid_number_detected"
    assert payload["last_callback_exception"] == ""

@pytest.mark.parametrize(
    ("binding_name", "problem_name"),
    [
        ("_native_neutral_bubble_t_eos_route_result", "neutral_bubble_t_eos"),
        ("_native_neutral_dew_t_eos_route_result", "neutral_dew_t_eos"),
    ],
)
def test_neutral_fixed_pressure_temperature_route_result_uses_ipopt_adapter_gate(
    binding_name: str,
    problem_name: str,
) -> None:
    mix = _neutral_binary_mixture()
    payload = getattr(_core, binding_name)(
        mix._native,
        1.0e5,
        [0.35, 0.65],
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
    )

    assert payload["backend"] == "ipopt"
    assert payload["problem_name"] == problem_name
    assert payload["derivative_backend"] == "analytic_cppad"
    assert payload["exact_gradient_required"] is True
    assert payload["exact_jacobian_required"] is True
    if not payload["compiled"]:
        assert payload["ran"] is False
        assert payload["solver_accepted"] is False
        assert payload["accepted"] is False
        assert payload["status"] == "ipopt_dependency_required"
        assert payload["phase_amounts"] == []
        assert payload["phase_volumes"] == []
        assert "fixed_composition_norm" in payload["postsolve"]
        assert "phase_amount_total_norm" in payload["postsolve"]
        return

    assert payload["ran"] is True
    if not payload["solver_accepted"]:
        assert payload["accepted"] is False
        assert payload["status"] == "solver_rejected"
        return

    assert np.asarray(payload["variables"], dtype=float).shape == (7,)
    assert np.asarray(payload["phase_amounts"], dtype=float).shape == (2, 2)
    assert np.asarray(payload["phase_volumes"], dtype=float).shape == (2,)
    assert payload["postsolve"]["derivative_backend"] == "analytic_cppad"
    assert payload["status"] in {"accepted", "solver_rejected", "postsolve_rejected"}

@pytest.mark.parametrize(
    ("binding_name", "problem_name"),
    [
        ("_native_neutral_bubble_t_eos_route_result", "neutral_bubble_t_eos"),
        ("_native_neutral_dew_t_eos_route_result", "neutral_dew_t_eos"),
    ],
)
def test_neutral_fixed_pressure_temperature_route_uses_exact_hessian_when_requested(
    binding_name: str,
    problem_name: str,
) -> None:
    mix = _neutral_binary_mixture()
    payload = getattr(_core, binding_name)(
        mix._native,
        1.0e5,
        [0.35, 0.65],
        30,
        1.0e-8,
        0.0,
        "exact",
        20,
        1.0e-7,
        1.0e-5,
        1.0e-7,
        1.0e-4,
        None,
    )

    if not payload["compiled"]:
        assert payload["status"] == "ipopt_dependency_required"
        return

    assert payload["ran"] is True
    assert payload["problem_name"] == problem_name
    assert payload["hessian_approximation"] == "exact"
    assert payload["exact_hessian_available"] is True
    assert payload["hessian_backend"] != "limited-memory"
    assert payload["eval_h_calls"] > 0
    assert payload["solver_status"] != "invalid_number_detected"
    assert payload["last_callback_exception"] == ""

def test_neutral_bubble_pressure_route_records_seed_sweep_attempts_on_failure() -> None:
    mix = _neutral_binary_mixture()
    payload = _core._native_neutral_bubble_p_eos_route_result(
        mix._native,
        300.0,
        [0.35, 0.65],
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
    assert payload["seed_name"] in {
        "canonical_shifted_partner_phase",
        "mirrored_shifted_partner_phase",
    }
    attempts = payload["seed_attempts"]
    assert len(attempts) >= 2
    assert attempts[0]["seed_name"] == "canonical_shifted_partner_phase"
    assert {attempt["seed_name"] for attempt in attempts} >= {
        "canonical_shifted_partner_phase",
        "mirrored_shifted_partner_phase",
    }
