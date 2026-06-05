from __future__ import annotations

from analyses.package_validation.explicit_association_toybox.scripts.picard_stress_objective_probe import (
    run_picard_stress_objective_rows,
)


def test_picard_stress_objective_probe_reports_local_step_quality() -> None:
    rows = run_picard_stress_objective_rows()

    assert rows
    row = rows[0]
    assert row["probe_scope"] == "m8_fixed_state_objective_probe"
    assert "local_step_direction_agreement" in row
    assert "hessian_conditioning_indicator" in row
    assert "objective_admission_status" in row
