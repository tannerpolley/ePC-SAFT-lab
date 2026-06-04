from __future__ import annotations

import pytest

from analyses.package_validation.explicit_association_toybox.scripts.derivative_agreement import (
    centered_slope,
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
                "exact_implicit_elapsed_seconds": 0.004,
                "closure_elapsed_seconds": 0.001,
            }
        ]
    )

    assert rows[0]["derivative_abs_error"] == pytest.approx(0.1)
    assert rows[0]["derivative_rel_error"] == pytest.approx(0.05)
    assert rows[0]["speedup_vs_exact_implicit"] == pytest.approx(4.0)
