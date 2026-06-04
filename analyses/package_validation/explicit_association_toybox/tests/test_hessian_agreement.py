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
from analyses.package_validation.explicit_association_toybox.scripts.jax_picard_derivatives import (
    run_jax_picard_derivative_cases,
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


def test_hessian_agreement_rows_retain_issue_schema() -> None:
    rows = run_hessian_agreement_cases(closure_names=(PICARD7_CLOSURE,))

    assert rows
    assert {
        "target_pair",
        "derivative_order",
        "exact_hessian_value",
        "picard_jax_hessian_value",
        "absolute_error",
        "relative_error",
        "finite_difference_step",
        "baseline_status",
        "autodiff_backend",
        "implicit_jacobian_condition_number",
        "mass_action_residual_inf",
    } <= set(rows[0])
    assert {row["autodiff_backend"] for row in rows} == {"jax"}
    assert {row["baseline_status"] for row in rows} == {"centered_finite_difference_exact_implicit"}
    assert all(float(row["implicit_jacobian_condition_number"]) >= 1.0 for row in rows)
    assert all(float(row["mass_action_residual_inf"]) <= 1.0e-10 for row in rows)


def test_hessian_agreement_rows_use_picard_jax_second_derivatives() -> None:
    rows = run_hessian_agreement_cases(closure_names=(PICARD7_CLOSURE,))
    jax_rows = {
        (row["case_id"], row["target"]): row
        for row in run_jax_picard_derivative_cases()
        if int(row["derivative_order"]) == 2
    }

    assert jax_rows
    for row in rows:
        key = (row["case_id"], row["target"])
        assert key in jax_rows
        assert float(row["picard_jax_hessian_value"]) == pytest.approx(float(jax_rows[key]["picard_jax_value"]))


def test_generate_hessian_agreement_writes_csv(tmp_path) -> None:
    output = tmp_path / "hessian_agreement.csv"

    generated = generate_hessian_agreement(output)

    assert generated == output
    text = output.read_text(encoding="utf-8")
    assert "picard_jax_hessian_value" in text
    assert "baseline_status" in text


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
