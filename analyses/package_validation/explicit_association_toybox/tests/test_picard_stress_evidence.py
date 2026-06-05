from __future__ import annotations

from analyses.package_validation.explicit_association_toybox.scripts.picard_stress_evidence import (
    PICARD_STRESS_COLUMNS,
    run_picard_stress_evidence,
)


def test_picard_stress_evidence_retains_exact_and_picard_rows() -> None:
    rows = run_picard_stress_evidence(repeat_count=1, max_cases=2, max_policies=2)

    assert rows
    assert {row["row_kind"] for row in rows} == {"exact_baseline", "picard_policy"}
    assert set(PICARD_STRESS_COLUMNS).issubset(rows[0])


def test_picard_stress_evidence_has_property_derivative_objective_and_timing_columns() -> None:
    rows = run_picard_stress_evidence(repeat_count=1, max_cases=1, max_policies=1)
    picard_rows = [row for row in rows if row["row_kind"] == "picard_policy"]

    assert picard_rows
    row = picard_rows[0]
    for column in [
        "association_helmholtz_relative_error",
        "total_ares_proxy_relative_error",
        "pressure_proxy_relative_error",
        "derivative_max_relative_error",
        "hessian_max_relative_error",
        "objective_relative_error",
        "gradient_direction_agreement",
        "hessian_conditioning_indicator",
        "closure_elapsed_median_seconds_exact",
        "closure_elapsed_median_seconds_picard",
        "simulation_speedup_vs_exact",
    ]:
        assert column in row
