from __future__ import annotations

import math

import numpy as np
import pytest


def test_modified_coordinates_round_trip_charge_and_galvani_invariance() -> None:
    from cython_held2_experiment import (
        modified_fraction,
        modified_potentials,
        recover_explicit_composition,
    )

    amounts = (0.8, 0.1, 0.1)
    u = modified_fraction(amounts)
    recovered = recover_explicit_composition(u)

    assert u == pytest.approx(0.2)
    assert recovered == pytest.approx(amounts)
    assert recovered[1] - recovered[2] == pytest.approx(0.0, abs=1.0e-15)

    baseline = modified_potentials((2.0, -3.0, 7.0), 0.0)
    shifted = modified_potentials((2.0, -3.0, 7.0), 19.0)
    assert shifted == pytest.approx(baseline, abs=1.0e-15)


@pytest.mark.parametrize(
    ("case", "outcome", "selected_y", "classes"),
    (
        ("three_root", "selected", 2.0, ("strict_stable", "unstable", "strict_stable")),
        ("marginal", "indeterminate_marginal_root", None, ()),
        ("tied", "indeterminate_objective_tie", None, ()),
        ("boundary", "indeterminate_boundary_root", None, ()),
    ),
)
def test_manufactured_reference_topologies_fail_closed(
    case: str,
    outcome: str,
    selected_y: float | None,
    classes: tuple[str, ...],
) -> None:
    from cython_held2_experiment import manufactured_reference_demo

    result = manufactured_reference_demo(case)
    assert result["outcome"] == outcome
    assert result["scan_status"] == "completed_finite"
    assert "globality_certificate" not in result
    if selected_y is not None:
        assert result["selected"]["log_volume"] == pytest.approx(selected_y, abs=2.0e-9)
        assert tuple(root["mechanical_class"] for root in result["roots"]) == classes


def test_real_tpd_callback_uses_exact_thermodynamic_derivatives() -> None:
    from cython_held2_experiment import stage1_tpd_callback

    temperature = 298.15
    pressure = 100_000.0
    reference_amounts = (0.964, 0.018, 0.018)
    reference_volume = 8.0e-5
    trial = np.array((0.05, math.log(7.5e-5)))

    observed = stage1_tpd_callback(
        temperature,
        pressure,
        reference_amounts,
        reference_volume,
        trial,
    )
    gradient = np.asarray(observed["gradient"])
    hessian = np.asarray(observed["hessian"])
    assert observed["jacobian_nonzeros"] == 0
    assert observed["hessian_lower_nonzeros"] == 3
    assert np.allclose(hessian, hessian.T, rtol=2.0e-13, atol=2.0e-8)

    step = np.array((2.0e-6, 2.0e-6))
    for coordinate in range(2):
        lower = trial.copy()
        upper = trial.copy()
        lower[coordinate] -= step[coordinate]
        upper[coordinate] += step[coordinate]
        lower_result = stage1_tpd_callback(
            temperature,
            pressure,
            reference_amounts,
            reference_volume,
            lower,
        )
        upper_result = stage1_tpd_callback(
            temperature,
            pressure,
            reference_amounts,
            reference_volume,
            upper,
        )
        finite_gradient = (upper_result["objective"] - lower_result["objective"]) / (2.0 * step[coordinate])
        finite_hessian_column = (np.asarray(upper_result["gradient"]) - np.asarray(lower_result["gradient"])) / (
            2.0 * step[coordinate]
        )
        assert gradient[coordinate] == pytest.approx(finite_gradient, rel=2.0e-7, abs=2.0e-7)
        assert hessian[:, coordinate] == pytest.approx(finite_hessian_column, rel=5.0e-6, abs=2.0e-5)


def test_manufactured_stage1_stable_and_negative_witness_precedence() -> None:
    from cython_held2_experiment import manufactured_stage1_demo

    stable = manufactured_stage1_demo("stable")
    assert stable["outcome"] == "no_negative_witness_detected"
    assert stable["search_status"] == "completed_finite"
    assert all(attempt["numerical_convergence"] == "passed" for attempt in stable["attempts"])
    assert "globality_certificate" not in stable

    unstable = manufactured_stage1_demo("unstable", inject_failed_start=True)
    assert unstable["outcome"] == "negative_tpd"
    assert unstable["search_status"] == "partial"
    assert any(attempt["solver_convergence"] == "failed" for attempt in unstable["attempts"])
    witness = unstable["negative_witness"]
    assert witness["tpd"] < -1.0e-6
    assert witness["distinct"] is True
    assert witness["numerical_convergence"] == "passed"
    assert witness["physical_validity"] == "passed"


def test_real_stage1_controller_selects_reference_and_reports_finite_search() -> None:
    from cython_held2_experiment import evaluate_state, solve_stage1

    temperature = 298.15
    feed = (0.964, 0.018, 0.018)
    reference_volume = 0.08
    pressure = evaluate_state(temperature, feed, reference_volume)["pressure_pa"]
    result = solve_stage1(
        temperature,
        pressure,
        feed,
        (0.05, 0.12),
        ((0.036, math.log(reference_volume)), (0.05, math.log(0.07))),
        129,
    )

    assert result["reference"]["outcome"] == "selected"
    assert result["reference"]["selected"]["volume"] == pytest.approx(reference_volume, rel=2.0e-12)
    assert result["outcome"] == "no_negative_witness_detected"
    assert result["search_status"] == "completed_finite"
    assert all(attempt["solver_convergence"] == "passed" for attempt in result["attempts"])
    assert all(attempt["numerical_convergence"] == "passed" for attempt in result["attempts"])
    assert all(attempt["physical_validity"] == "passed" for attempt in result["attempts"])
    assert "globality_certificate" not in result
