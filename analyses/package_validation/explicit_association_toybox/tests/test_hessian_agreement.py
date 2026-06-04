from __future__ import annotations

import numpy as np
import pytest

from analyses.package_validation.explicit_association_toybox.scripts.association_models import AssociationSystem
from analyses.package_validation.explicit_association_toybox.scripts.closure_models import PICARD7_CLOSURE
from analyses.package_validation.explicit_association_toybox.scripts.hessian_agreement import (
    exact_hessian_target,
    generate_hessian_agreement,
    run_hessian_agreement_cases,
)
from analyses.package_validation.explicit_association_toybox.scripts.propagation_evidence import exact_association_value


def _pure_2b_system() -> AssociationSystem:
    return AssociationSystem(
        component_count=1,
        site_component_index=np.array([0, 0], dtype=int),
        site_kind=("D", "A"),
        active_pairs=((0, 1), (1, 0)),
    )


def test_exact_density_hessian_matches_direct_second_value_difference() -> None:
    system = _pure_2b_system()
    density = 0.05
    strength = 10.0
    composition = np.array([1.0], dtype=float)

    exact_hessian = exact_hessian_target(
        "density_density",
        system=system,
        density=density,
        strength=strength,
        composition=composition,
    )
    step = density * 1.0e-4
    high = _exact_a_assoc(system, density + step, composition, strength)
    mid = _exact_a_assoc(system, density, composition, strength)
    low = _exact_a_assoc(system, density - step, composition, strength)
    direct = (high - 2.0 * mid + low) / (step * step)

    assert exact_hessian == pytest.approx(direct, rel=2.0e-4, abs=1.0e-7)


def test_hessian_agreement_rows_retain_exact_jacobian_evidence() -> None:
    rows = run_hessian_agreement_cases(closure_names=(PICARD7_CLOSURE,))

    assert rows
    assert {
        "exact_hessian_method",
        "closure_hessian_method",
        "implicit_jacobian_condition_number",
        "mass_action_residual_inf",
    } <= set(rows[0])
    assert all("implicit_first_derivative" in str(row["exact_hessian_method"]) for row in rows)
    assert all(float(row["implicit_jacobian_condition_number"]) >= 1.0 for row in rows)
    assert all(float(row["mass_action_residual_inf"]) <= 1.0e-10 for row in rows)


def test_generate_hessian_agreement_writes_csv(tmp_path) -> None:
    output = tmp_path / "hessian_agreement.csv"

    generated = generate_hessian_agreement(output)

    assert generated == output
    text = output.read_text(encoding="utf-8")
    assert "density_density" in text
    assert "strength_strength" in text


def _exact_a_assoc(
    system: AssociationSystem,
    density: float,
    composition: np.ndarray,
    strength: float,
) -> float:
    _, value, _ = exact_association_value(
        system=system,
        density=density,
        composition=composition,
        delta=system.delta_matrix(strength),
    )
    return value
