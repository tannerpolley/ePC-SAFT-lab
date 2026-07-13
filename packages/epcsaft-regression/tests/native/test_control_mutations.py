from __future__ import annotations

import math

import pytest
from regression_support.native_problem_cases import native_core, native_problem


@pytest.mark.parametrize(
    "mutation",
    (
        {"weight": 4.0},
        {"residual_scale": 3.0},
        {"start": 7.0},
        {"lower": -9.0},
        {"upper": 11.0},
        {"max_num_iterations": 49},
        {"function_tolerance": 2.0e-12},
        {"gradient_tolerance": 2.0e-12},
        {"parameter_tolerance": 2.0e-12},
    ),
)
def test_each_native_problem_field_mutation_changes_the_fingerprint(mutation: dict[str, float | int]) -> None:
    assert native_problem(**mutation).problem_fingerprint != native_problem().problem_fingerprint


@pytest.mark.parametrize(
    ("field", "value"),
    (
        ("max_num_iterations", 17),
        ("function_tolerance", 2.0e-10),
        ("gradient_tolerance", 3.0e-10),
        ("parameter_tolerance", 4.0e-10),
    ),
)
def test_submitted_control_is_read_back_from_the_effective_ceres_options(field: str, value: float | int) -> None:
    result = native_core()._solve_regression(native_problem(**{field: value}))

    assert result["effective_ceres_options"][field] == value


def test_weight_and_scale_change_only_packing_and_objective() -> None:
    core = native_core()
    baseline = core._evaluate_regression(native_problem(weight=1.0, residual_scale=1.0), (1.5,))
    changed = core._evaluate_regression(native_problem(weight=16.0, residual_scale=2.0), (1.5,))

    assert changed["row_diagnostics"][0]["raw_residual"] == pytest.approx(
        baseline["row_diagnostics"][0]["raw_residual"]
    )
    raw = baseline["row_diagnostics"][0]["raw_residual"]
    expected = math.sqrt(16.0) * raw / 2.0
    assert changed["row_diagnostics"][0]["weighted_residual"] == pytest.approx(expected)
    assert changed["objective"] == pytest.approx(0.5 * expected**2)
    assert changed["objective"] != pytest.approx(baseline["objective"])


def test_bounded_iteration_control_changes_solver_termination() -> None:
    core = native_core()
    bounded = core._solve_regression(native_problem(max_num_iterations=1))
    converged = core._solve_regression(native_problem(max_num_iterations=50))

    assert bounded["effective_ceres_options"]["max_num_iterations"] == 1
    assert converged["effective_ceres_options"]["max_num_iterations"] == 50
    assert bounded["termination_type"] == "NO_CONVERGENCE"
    assert converged["termination_type"] == "CONVERGENCE"
    assert bounded["iterations"] < converged["iterations"]
    assert bounded["success"] is False
    assert converged["success"] is True
