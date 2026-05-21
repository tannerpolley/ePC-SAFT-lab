from __future__ import annotations

import numpy as np
import pytest

import epcsaft
from epcsaft.epcsaft import ePCSAFTMixture
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


def test_reactive_electrolyte_lle_eos_route_builder_uses_liquid_root_residual_route() -> None:
    species = ["A", "B", "C+", "D-"]
    feed = np.asarray([0.535, 0.25, 0.1075, 0.1075], dtype=float)
    mix = ePCSAFTMixture.from_params(
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
    charges = np.asarray(mix.parameters["z"], dtype=float)
    balance_matrix = [
        1.0,
        1.0,
        0.0,
        0.0,
        0.0,
        0.0,
        1.0,
        0.0,
        0.0,
        0.0,
        0.0,
        1.0,
    ]
    totals = [float(feed[0] + feed[1]), float(feed[2]), float(feed[3])]
    reaction = [-1.0, 1.0, 0.0, 0.0]

    contract = _core._native_reactive_electrolyte_lle_eos_nlp_contract(
        mix._native,
        298.15,
        1.013e5,
        feed.tolist(),
        3,
        balance_matrix,
        totals,
        1,
        reaction,
        [float(np.log(0.2))],
    )
    initial = np.asarray(contract["initial_point"], dtype=float)
    first = np.exp(initial[:4])
    second = np.exp(initial[4:8])

    assert contract["problem_name"] == "reactive_liquid_root_eos"
    assert contract["derivative_backend"] == "cppad_explicit_density"
    assert contract["density_backend"] == "explicit_log_density_pressure_constraint"
    assert contract["variable_model"] == "log_phase_species_amounts_plus_log_density"
    assert contract["residual_families"] == [
        "conserved_balance",
        "reaction_stationarity",
        "phase_equilibrium",
        "phase_charge",
    ]
    assert contract["constraint_families"] == [
        "conserved_balance",
        "phase_charge",
        "phase_pressure_consistency",
        "phase_distance",
    ]
    assert contract["variable_count"] == 2 * contract["species_count"] + 2
    assert contract["constraint_count"] == 8
    assert contract["jacobian_nonzero_count"] == 40
    assert contract["balance_row_count"] == 3
    assert contract["reaction_count"] == 1
    assert contract["constraint_lower_bounds"][:3] == pytest.approx([0.0, 0.0, 0.0])
    assert contract["constraint_upper_bounds"][:3] == pytest.approx([0.0, 0.0, 0.0])
    assert contract["constraint_lower_bounds"][3:7] == pytest.approx([0.0, 0.0, 0.0, 0.0])
    assert contract["constraint_upper_bounds"][3:7] == pytest.approx([0.0, 0.0, 0.0, 0.0])
    assert contract["constraint_lower_bounds"][-1] == pytest.approx(1.0e-8)
    assert contract["constraint_upper_bounds"][-1] > 1.0e6
    assert contract["constraints_at_initial"][:7] == pytest.approx(
        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        abs=1.0e-10,
    )
    assert contract["constraints_at_initial"][-1] >= contract["constraint_lower_bounds"][-1]
    assert np.all(np.asarray(contract["variable_upper_bounds"], dtype=float) < 50.0)
    assert np.asarray(contract["jacobian_values_at_initial"], dtype=float).shape == (
        contract["jacobian_nonzero_count"],
    )
    assert np.count_nonzero(np.asarray(contract["jacobian_values_at_initial"], dtype=float)) > 0
    assert np.dot(first, charges) == pytest.approx(0.0, abs=1.0e-14)
    assert np.dot(second, charges) == pytest.approx(0.0, abs=1.0e-14)

    payload = _core._native_reactive_electrolyte_lle_eos_route_result(
        mix._native,
        298.15,
        1.013e5,
        feed.tolist(),
        3,
        balance_matrix,
        totals,
        1,
        reaction,
        [float(np.log(0.2))],
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
        linear_solver="mumps",
        acceptable_tolerance=9.0e-7,
        constraint_violation_tolerance=8.0e-8,
        dual_infeasibility_tolerance=7.0e-8,
        complementarity_tolerance=6.0e-8,
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
        "phase_charge",
    ]
    assert payload["constraint_families"] == [
        "conserved_balance",
        "phase_charge",
        "phase_pressure_consistency",
        "phase_distance",
    ]
    assert payload["balance_row_count"] == 3
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

def test_reactive_electrolyte_lle_eos_route_uses_exact_hessian_when_requested() -> None:
    species = ["A", "B", "C+", "D-"]
    feed = np.asarray([0.535, 0.25, 0.1075, 0.1075], dtype=float)
    mix = ePCSAFTMixture.from_params(
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
    balance_matrix = [
        1.0,
        1.0,
        0.0,
        0.0,
        0.0,
        0.0,
        1.0,
        0.0,
        0.0,
        0.0,
        0.0,
        1.0,
    ]
    payload = _core._native_reactive_electrolyte_lle_eos_route_result(
        mix._native,
        298.15,
        1.013e5,
        feed.tolist(),
        3,
        balance_matrix,
        [float(feed[0] + feed[1]), float(feed[2]), float(feed[3])],
        1,
        [-1.0, 1.0, 0.0, 0.0],
        [float(np.log(0.2))],
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
