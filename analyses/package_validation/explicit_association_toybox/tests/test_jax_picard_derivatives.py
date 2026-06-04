from __future__ import annotations

from analyses.package_validation.explicit_association_toybox.scripts.jax_picard_derivatives import (
    generate_jax_picard_derivatives,
    run_jax_picard_derivative_cases,
)


def test_jax_picard_derivative_rows_retain_issue_schema() -> None:
    rows = run_jax_picard_derivative_cases()

    assert rows
    assert {
        "case_id",
        "closure_name",
        "target",
        "derivative_order",
        "exact_implicit_value",
        "picard_jax_value",
        "abs_error",
        "rel_error",
        "exact_implicit_elapsed_seconds",
        "picard_jax_elapsed_seconds",
        "speedup_vs_exact_implicit",
        "autodiff_backend",
        "exact_baseline",
        "baseline_status",
        "implicit_jacobian_condition_number",
        "mass_action_residual_inf",
    } <= set(rows[0])
    assert {row["autodiff_backend"] for row in rows} == {"jax"}
    assert {row["baseline_status"] for row in rows} == {
        "exact_implicit_first_derivative",
        "centered_finite_difference_exact_implicit",
    }
    assert {row["target"] for row in rows} >= {
        "density",
        "strength",
        "density_density",
        "density_strength",
        "strength_strength",
    }
    assert all(float(row["implicit_jacobian_condition_number"]) >= 1.0 for row in rows)
    assert all(float(row["mass_action_residual_inf"]) <= 1.0e-10 for row in rows)


def test_generate_jax_picard_derivatives_writes_csv(tmp_path) -> None:
    output = tmp_path / "jax_picard_derivatives.csv"

    generated = generate_jax_picard_derivatives(output)

    assert generated == output
    text = output.read_text(encoding="utf-8")
    assert "picard_jax_value" in text
    assert "autodiff_backend" in text
    assert "baseline_status" in text
