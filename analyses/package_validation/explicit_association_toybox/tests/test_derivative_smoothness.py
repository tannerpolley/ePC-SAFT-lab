from __future__ import annotations

import math

from analyses.package_validation.explicit_association_toybox.scripts.derivative_smoothness import (
    derivative_smoothness_rows,
)


def test_derivative_smoothness_rows_cover_local_coordinates() -> None:
    rows = derivative_smoothness_rows(
        closure_names=("implicit_exact_mass_action", "damped_picard_7_05"),
        density=0.05,
        strength=10.0,
        step_fraction=1.0e-3,
    )

    assert rows
    required = {
        "closure_name",
        "perturbation_axis",
        "base_value",
        "step_size",
        "first_derivative_left",
        "first_derivative_right",
        "derivative_jump_abs",
        "relative_jump",
        "smoothness_band",
    }
    assert required <= set(rows[0])
    assert {"density", "association_strength_scale", "composition_component_0"} <= {
        row["perturbation_axis"] for row in rows
    }
    assert {"implicit_exact_mass_action", "damped_picard_7_05"} <= {row["closure_name"] for row in rows}
    assert all(math.isfinite(float(row["derivative_jump_abs"])) for row in rows)
