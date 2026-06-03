from __future__ import annotations

from analyses.package_validation.explicit_association_toybox.scripts.closure_sensitivity import (
    rank_closure_sensitivity,
)


def test_closure_sensitivity_rows_rank_error_and_timing() -> None:
    rows = rank_closure_sensitivity(
        topology_types=("2B",),
        density_grid=(0.05,),
        strength_grid=(10.0,),
    )

    assert rows
    required = {
        "closure_variant",
        "picard_steps",
        "damping",
        "diagonal_polish",
        "max_ares_assoc_rel_error",
        "max_mass_action_residual_inf",
        "median_elapsed_seconds",
        "median_exact_implicit_elapsed_seconds",
        "speedup_vs_exact_implicit",
        "evidence_band",
    }
    assert required <= set(rows[0])
    assert {row["closure_variant"] for row in rows} >= {"damped_picard_3_05", "picard3_diag_newton1"}
    assert rows == sorted(rows, key=lambda row: float(row["max_ares_assoc_rel_error"]))
    assert all(float(row["median_exact_implicit_elapsed_seconds"]) > 0.0 for row in rows)
    assert all(float(row["speedup_vs_exact_implicit"]) > 0.0 for row in rows)
