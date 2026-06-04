from __future__ import annotations

import pytest

from analyses.package_validation.explicit_association_toybox.scripts.amortized_timing import (
    summarize_amortized_timing_samples,
)


def test_summarize_amortized_timing_samples_keeps_exact_baseline_columns() -> None:
    rows = summarize_amortized_timing_samples(
        [
            {
                "case_id": "two_site",
                "topology_id": "2B",
                "site_count": 2,
                "closure_name": "explicit_damped_picard_unroll_3",
                "exact_implicit_elapsed_seconds": 0.004,
                "closure_elapsed_seconds": 0.001,
                "exact_iteration_count": 20,
            },
            {
                "case_id": "two_site",
                "topology_id": "2B",
                "site_count": 2,
                "closure_name": "explicit_damped_picard_unroll_3",
                "exact_implicit_elapsed_seconds": 0.006,
                "closure_elapsed_seconds": 0.002,
                "exact_iteration_count": 22,
            },
        ]
    )

    assert rows[0]["case_id"] == "two_site"
    assert rows[0]["exact_implicit_elapsed_median_seconds"] == pytest.approx(0.005)
    assert rows[0]["closure_elapsed_median_seconds"] == pytest.approx(0.0015)
    assert rows[0]["exact_implicit_elapsed_iqr_seconds"] == pytest.approx(0.001)
    assert rows[0]["closure_elapsed_iqr_seconds"] == pytest.approx(0.0005)
    assert rows[0]["speedup_vs_exact_implicit"] == pytest.approx(0.005 / 0.0015)
    assert rows[0]["exact_iteration_count_median"] == pytest.approx(21.0)
