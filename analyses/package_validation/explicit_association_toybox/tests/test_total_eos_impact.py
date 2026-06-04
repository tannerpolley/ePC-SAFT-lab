from __future__ import annotations

import pytest

from analyses.package_validation.explicit_association_toybox.scripts.total_eos_impact import (
    summarize_total_eos_impact,
)


def test_summarize_total_eos_impact_keeps_property_and_timing_columns() -> None:
    rows = summarize_total_eos_impact(
        [
            {
                "case_id": "case",
                "closure_name": "closure",
                "ares_assoc_rel_error": 0.01,
                "ares_total_abs_error": 0.02,
                "ares_total_rel_error": 0.03,
                "pressure_proxy_abs_error": 0.04,
                "pressure_proxy_rel_error": 0.05,
                "mu_proxy_max_abs_error": 0.06,
                "fugacity_proxy_max_abs_error": 0.07,
                "exact_implicit_elapsed_seconds": 0.004,
                "closure_elapsed_seconds": 0.001,
                "evidence_band": "candidate_accuracy",
            }
        ]
    )

    assert rows[0]["speedup_vs_exact_implicit"] == pytest.approx(4.0)
    assert rows[0]["evidence_band"] == "candidate_accuracy"
