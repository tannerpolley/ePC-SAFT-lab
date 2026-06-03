from __future__ import annotations

from pathlib import Path

import numpy as np

from analyses.package_validation.explicit_association_toybox.scripts.association_models import AssociationSystem
from analyses.package_validation.explicit_association_toybox.scripts.closure_models import evaluate_closure
from analyses.package_validation.explicit_association_toybox.scripts.exact_baseline import solve_exact_site_fractions
from analyses.package_validation.explicit_association_toybox.scripts.metrics import metric_row
from analyses.package_validation.explicit_association_toybox.scripts.run_grid import run_grid


REQUIRED_COLUMNS = {
    "system",
    "closure",
    "association_model",
    "exact_derivative_of",
    "density",
    "strength",
    "max_abs_x_error",
    "mass_residual_inf",
    "assoc_helmholtz_abs_error",
    "assoc_compressibility_abs_error",
    "assoc_mu_abs_error",
    "assoc_fugacity_abs_error",
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
        "explicit_damped_picard_unroll_3",
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
    run_grid(output_path=output, system_names=("symmetric_2b_pure",), closure_names=("closure_2b_exact_reduction",))
    text = output.read_text(encoding="utf-8")
    assert "system,closure," in text
    assert "symmetric_2b_pure,closure_2b_exact_reduction" in text
