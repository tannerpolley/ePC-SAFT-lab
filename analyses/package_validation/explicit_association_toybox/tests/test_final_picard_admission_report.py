from __future__ import annotations

from analyses.package_validation.explicit_association_toybox.scripts.final_picard_admission_report import (
    FINAL_REPORT_COLUMNS,
    build_final_picard_admission_rows,
)


def test_final_picard_report_contains_full_grid_and_simulation_metrics() -> None:
    rows = build_final_picard_admission_rows(repeat_count=1, max_source_rows=1)

    assert rows
    assert set(FINAL_REPORT_COLUMNS).issubset(rows[0])
    assert {int(row["step_count"]) for row in rows if row["step_count"] != ""} == {3, 5, 7, 9, 11}
    assert {float(row["damping"]) for row in rows if row["damping"] != ""} == {0.35, 0.5, 0.65, 0.8, 1.0}
    assert "implicit_exact_mass_action" in {row["policy_name"] for row in rows}
    assert all(row["issue_161_recommendation"] for row in rows)
    assert any(row["simulation_elapsed_median_seconds_picard"] != "" for row in rows)
