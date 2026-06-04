from __future__ import annotations

import pytest

from analyses.package_validation.explicit_association_toybox.scripts.derivative_agreement import (
    centered_slope,
    run_derivative_agreement_cases,
    summarize_derivative_agreement,
)


def test_centered_slope_uses_symmetric_samples() -> None:
    slope = centered_slope(lambda value: value * value, base_value=3.0, step_size=1.0e-5)

    assert slope == pytest.approx(6.0)


def test_summarize_derivative_agreement_reports_required_targets() -> None:
    rows = summarize_derivative_agreement(
        [
            {
                "case_id": "case",
                "closure_name": "closure",
                "target": "a_assoc_density",
                "exact_derivative": 2.0,
                "closure_derivative": 2.1,
                "exact_derivative_method": "implicit_function_theorem_first_derivative",
                "closure_derivative_method": "centered_finite_difference",
                "implicit_jacobian_condition_number": 1.2,
                "mass_action_residual_inf": 1.0e-12,
                "exact_implicit_elapsed_seconds": 0.004,
                "closure_elapsed_seconds": 0.001,
            }
        ]
    )

    assert rows[0]["derivative_abs_error"] == pytest.approx(0.1)
    assert rows[0]["derivative_rel_error"] == pytest.approx(0.05)
    assert rows[0]["speedup_vs_exact_implicit"] == pytest.approx(4.0)


def test_run_derivative_agreement_retains_implicit_sensitivity_diagnostics() -> None:
    rows = run_derivative_agreement_cases()

    assert rows
    assert {
        "exact_derivative_method",
        "closure_derivative_method",
        "implicit_jacobian_condition_number",
        "mass_action_residual_inf",
    } <= set(rows[0])
    assert "implicit_function_theorem" in str(rows[0]["exact_derivative_method"])
    assert all(float(row["implicit_jacobian_condition_number"]) >= 1.0 for row in rows)
    assert all(float(row["mass_action_residual_inf"]) <= 1.0e-10 for row in rows)
