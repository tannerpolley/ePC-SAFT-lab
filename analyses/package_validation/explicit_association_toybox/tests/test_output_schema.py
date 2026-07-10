from __future__ import annotations

import csv
from pathlib import Path

import numpy as np

from analyses.package_validation.explicit_association_toybox.scripts.association_models import AssociationSystem
from analyses.package_validation.explicit_association_toybox.scripts.closure_models import evaluate_closure
from analyses.package_validation.explicit_association_toybox.scripts.exact_baseline import solve_exact_site_fractions
from analyses.package_validation.explicit_association_toybox.scripts.metrics import metric_row
from analyses.package_validation.explicit_association_toybox.scripts.run_grid import run_grid
from analyses.package_validation.explicit_association_toybox.scripts.summarize_results import summarize_rows

REQUIRED_COLUMNS = {
    "system",
    "closure",
    "association_model",
    "exact_derivative_of",
    "density",
    "strength",
    "temperature",
    "pcsaft_density",
    "ares_hc",
    "ares_disp",
    "ares_assoc_exact",
    "ares_assoc_closure",
    "ares_total_exact",
    "ares_total_closure",
    "ares_total_abs_error",
    "ares_total_rel_error",
    "max_abs_x_error",
    "mass_residual_inf",
    "assoc_helmholtz_abs_error",
    "assoc_compressibility_abs_error",
    "assoc_mu_abs_error",
    "assoc_fugacity_abs_error",
    "exact_elapsed_seconds",
    "closure_elapsed_seconds",
    "speedup_ratio",
    "evidence_band",
}


def test_metric_row_contains_required_columns() -> None:
    system = AssociationSystem(
        component_count=1,
        site_component_index=np.array([0, 0], dtype=int),
        site_kind=("D", "A"),
        active_pairs=((0, 1), (1, 0)),
    )
    density = 0.1
    composition = np.array([1.0])
    delta = system.delta_matrix(strength=2.0)
    exact = solve_exact_site_fractions(density=density, x_assoc=system.x_assoc(composition), delta=delta)
    closure = evaluate_closure(
        "damped_picard_7_05",
        system=system,
        density=density,
        composition=composition,
        delta=delta,
    )

    row = metric_row(
        system_name="symmetric_2b_pure",
        system=system,
        density=density,
        strength=2.0,
        composition=composition,
        delta=delta,
        exact=exact,
        closure=closure,
        thresholds={"thermodynamic_relative_reference": 0.03, "mass_residual_loose": 1.0e-6},
    )

    assert REQUIRED_COLUMNS <= set(row)
    assert row["evidence_band"] in {
        "exact_reduction_verified",
        "promising_eos_approximation",
        "diagnostic_only",
        "reject_for_provider_path",
    }


def test_run_grid_writes_retained_csv(tmp_path: Path) -> None:
    output = tmp_path / "closure_metrics.csv"
    run_grid(output_path=output, system_names=("symmetric_2b_pure",), closure_names=("damped_picard_7_05",))
    text = output.read_text(encoding="utf-8")
    assert "system,closure," in text
    assert "symmetric_2b_pure,damped_picard_7_05" in text
    assert "ares_hc" in text
    assert "ares_disp" in text
    assert "ares_total_abs_error" in text
    assert "speedup_ratio" in text
    with output.open("r", encoding="utf-8", newline="") as handle:
        first_row = next(csv.DictReader(handle))
    assert float(first_row["pcsaft_density"]) > 0.0
    assert np.isfinite(float(first_row["ares_hc"]))
    assert np.isfinite(float(first_row["ares_disp"]))
    assert np.isfinite(float(first_row["speedup_ratio"]))


def test_summary_rows_preserve_total_ares_context(tmp_path: Path) -> None:
    output = tmp_path / "closure_metrics.csv"
    run_grid(output_path=output, system_names=("symmetric_2b_pure",), closure_names=("damped_picard_7_05",))

    rows = summarize_rows(output)

    assert rows
    row = rows[0]
    assert {
        "closure",
        "row_count",
        "max_ares_total_abs_error",
        "max_ares_total_rel_error",
        "max_ares_hc",
        "max_ares_disp",
    } <= set(row)
    assert float(row["max_ares_total_abs_error"]) >= 0.0
