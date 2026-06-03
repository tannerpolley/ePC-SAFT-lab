from __future__ import annotations

import numpy as np
import pytest

from analyses.package_validation.explicit_association_toybox.scripts.association_models import AssociationSystem
from analyses.package_validation.explicit_association_toybox.scripts.closure_models import evaluate_closure
from analyses.package_validation.explicit_association_toybox.scripts.exact_baseline import solve_exact_site_fractions
from analyses.package_validation.explicit_association_toybox.scripts.metrics import metric_row


def test_metric_row_adds_total_ares_context_when_supplied() -> None:
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
        elapsed_seconds=0.002,
        exact_elapsed_seconds=0.010,
        temperature=303.15,
        pcsaft_density=0.01,
        ares_hc=0.10,
        ares_disp=-0.30,
    )

    assert row["temperature"] == pytest.approx(303.15)
    assert row["pcsaft_density"] == pytest.approx(0.01)
    assert row["ares_hc"] == pytest.approx(0.10)
    assert row["ares_disp"] == pytest.approx(-0.30)
    assert row["ares_total_exact"] == pytest.approx(0.10 - 0.30 + row["ares_assoc_exact"])
    assert row["ares_total_closure"] == pytest.approx(0.10 - 0.30 + row["ares_assoc_closure"])
    assert row["ares_total_abs_error"] == pytest.approx(abs(row["ares_total_closure"] - row["ares_total_exact"]))
    assert row["speedup_ratio"] == pytest.approx(5.0)
