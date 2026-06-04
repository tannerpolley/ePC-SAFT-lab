from __future__ import annotations

from analyses.package_validation.explicit_association_toybox.scripts.repeated_timing import (
    summarize_repeated_timings,
)


def test_summarize_repeated_timings_reports_spread_and_speedup() -> None:
    samples = [
        {"closure_name": "implicit_exact_mass_action", "elapsed_seconds": 4.0, "exact_elapsed_seconds": 4.0},
        {"closure_name": "implicit_exact_mass_action", "elapsed_seconds": 6.0, "exact_elapsed_seconds": 6.0},
        {"closure_name": "damped_picard_7_05", "elapsed_seconds": 1.0, "exact_elapsed_seconds": 5.0},
        {"closure_name": "damped_picard_7_05", "elapsed_seconds": 2.0, "exact_elapsed_seconds": 5.0},
        {"closure_name": "damped_picard_7_05", "elapsed_seconds": 3.0, "exact_elapsed_seconds": 5.0},
    ]

    rows = summarize_repeated_timings(samples)

    assert rows
    required = {
        "closure_name",
        "repeat_count",
        "elapsed_median_seconds",
        "elapsed_iqr_seconds",
        "elapsed_min_seconds",
        "elapsed_max_seconds",
        "speedup_median",
    }
    assert required <= set(rows[0])
    approx = next(row for row in rows if row["closure_name"] == "damped_picard_7_05")
    exact = next(row for row in rows if row["closure_name"] == "implicit_exact_mass_action")
    assert exact["speedup_median"] == 1.0
    assert approx["repeat_count"] == 3
    assert approx["elapsed_median_seconds"] == 2.0
    assert approx["speedup_median"] == 2.5
