from __future__ import annotations

import math

import numpy as np
import pytest


def test_real_stage2_phase_callback_has_exact_lower_derivatives() -> None:
    from cython_held2_experiment import stage2_lower_callback

    temperature = 298.15
    pressure = 100_000.0
    feed_u = 0.036
    lagrange = 0.75
    point = np.array((0.05, math.log(7.5e-5)))
    observed = stage2_lower_callback(temperature, pressure, feed_u, lagrange, point)
    gradient = np.asarray(observed["gradient"])
    hessian = np.asarray(observed["hessian"])

    assert observed["jacobian_nonzeros"] == 0
    assert observed["hessian_lower_nonzeros"] == 3
    assert np.allclose(hessian, hessian.T, rtol=2.0e-13, atol=2.0e-8)

    step = 2.0e-6
    for coordinate in range(2):
        lower = point.copy()
        upper = point.copy()
        lower[coordinate] -= step
        upper[coordinate] += step
        lower_result = stage2_lower_callback(temperature, pressure, feed_u, lagrange, lower)
        upper_result = stage2_lower_callback(temperature, pressure, feed_u, lagrange, upper)
        finite_gradient = (upper_result["objective"] - lower_result["objective"]) / (2.0 * step)
        finite_hessian_column = (np.asarray(upper_result["gradient"]) - np.asarray(lower_result["gradient"])) / (
            2.0 * step
        )
        assert gradient[coordinate] == pytest.approx(finite_gradient, rel=2.0e-7, abs=2.0e-7)
        assert hessian[:, coordinate] == pytest.approx(finite_hessian_column, rel=5.0e-6, abs=2.0e-5)


def test_manufactured_stage2_reaches_expected_mstar_with_ordered_ledger() -> None:
    from cython_held2_experiment import manufactured_stage2_demo

    result = manufactured_stage2_demo("two_phase")

    assert result["outcome"] == "ready_stage3"
    assert result["stage3_status"] == "ready"
    assert result["physical_status"] == "not_adjudicated"
    assert result["search_status"] == "completed_finite"
    assert result["cut_order"] == ["feed", "witness", "C1"]
    assert [candidate["modified_fraction"] for candidate in result["mstar"]] == pytest.approx((0.2, 0.8), abs=2.0e-6)

    major = result["majors"][0]
    assert major["event_order"] == (
        "upper_lp",
        "lower_search",
        "cut_admission",
        "step6",
    )
    assert major["upper_lp"]["solver_convergence"] == "passed"
    assert major["upper_lp"]["primal_feasibility"] == "passed"
    assert major["upper_lp"]["duality"] == "passed"
    assert major["step6"]["upper_objective"] == major["upper_lp"]["upper_objective"]
    assert major["step6"]["lagrange"] == major["upper_lp"]["lagrange"]
    assert major["admitted_cut"] == "C1"

    final_major = result["majors"][-1]
    assert final_major["step6"]["candidate_ids"] == ["witness", "C1"]
    assert all(
        predicate["passed_local_predicates"]
        for predicate in final_major["step6"]["predicates"]
        if predicate["id"] in {"witness", "C1"}
    )

    required_attempt_fields = {
        "solver_convergence",
        "feasibility_inf_norm",
        "projected_kkt_inf_norm",
        "complementarity_inf_norm",
        "coordinate_domain",
        "charge_residual",
        "relative_pressure_residual",
        "final_eos_evaluation",
        "numerical_convergence",
        "physical_validity",
    }
    assert major["lower_attempts"]
    assert all(required_attempt_fields <= set(attempt) for attempt in major["lower_attempts"])
    admitted = next(attempt for attempt in major["lower_attempts"] if attempt.get("admitted") is True)
    assert admitted["numerical_convergence"] == "passed"
    assert admitted["physical_validity"] == "passed"
    assert admitted["improving"] is True
    assert admitted["distinct"] is True


def test_real_stage2_controller_runs_one_certified_major() -> None:
    from cython_held2_experiment import solve_stage2, stage2_lower_callback

    temperature = 298.15
    pressure = 30_223.300708045346
    feed = (0.964, 0.018, 0.018)
    feed_u = 0.036
    volume = 0.08
    point = (feed_u, math.log(volume))
    phase = stage2_lower_callback(temperature, pressure, feed_u, 0.0, point)
    lagrange = phase["composition_gradient_fixed_volume"]

    result = solve_stage2(
        temperature,
        pressure,
        feed,
        ({"id": "feed", "modified_fraction": feed_u, "volume": volume},),
        (0.05, 0.1),
        (point, (0.1, math.log(volume))),
        (lagrange - 1.0e-6, lagrange + 1.0e-6),
        max_major=1,
    )

    assert result["outcome"] == "mstar_empty"
    assert result["stage3_status"] == "not_run"
    attempts = result["majors"][0]["lower_attempts"]
    assert len(attempts) == 2
    assert all(attempt["numerical_convergence"] == "passed" for attempt in attempts)
    assert all(attempt["physical_validity"] == "passed" for attempt in attempts)
    assert max(abs(attempt["relative_pressure_residual"]) for attempt in attempts) < 1.0e-8


@pytest.mark.parametrize(
    ("case", "outcome"),
    (
        ("resource_limited", "resource_limited"),
        ("no_certified_cut", "no_certified_improving_cut"),
        ("mstar_empty", "mstar_empty"),
    ),
)
def test_incomplete_stage2_outcomes_do_not_run_stage3(case: str, outcome: str) -> None:
    from cython_held2_experiment import manufactured_stage2_demo

    result = manufactured_stage2_demo(case)
    assert result["outcome"] == outcome
    assert result["stage3_status"] == "not_run"
    assert result["physical_status"] == "not_adjudicated"
    assert result["search_status"] in {"partial", "completed_finite"}
    assert "globality_certificate" not in result
