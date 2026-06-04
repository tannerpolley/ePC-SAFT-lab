from __future__ import annotations

import pytest

jax = pytest.importorskip("jax")

from analyses.package_validation.explicit_association_toybox.scripts.jax_picard_derivatives import (
    generate_jax_picard_derivatives,
    jax_picard_association_scalar,
    run_jax_picard_derivative_cases,
)


def test_jax_picard_association_value_is_differentiable_for_pure_2b() -> None:
    import jax.numpy as jnp

    value = jax.grad(
        lambda rho: jax_picard_association_scalar(
            density=rho,
            strength=10.0,
            composition=jnp.asarray([1.0], dtype=jnp.float64),
            site_component_index=(0, 0),
            active_pairs=((0, 1), (1, 0)),
            site_count=2,
        )
    )(0.05)

    assert float(value) < 0.0


def test_jax_picard_derivative_rows_retain_backend_and_exact_baseline() -> None:
    rows = run_jax_picard_derivative_cases()

    assert rows
    assert {
        "exact_implicit_value",
        "picard_jax_value",
        "exact_implicit_elapsed_seconds",
        "picard_jax_elapsed_seconds",
        "speedup_vs_exact_implicit",
        "autodiff_backend",
        "exact_baseline",
        "implicit_jacobian_condition_number",
        "mass_action_residual_inf",
    } <= set(rows[0])
    assert {row["autodiff_backend"] for row in rows} == {"jax"}
    assert all(float(row["implicit_jacobian_condition_number"]) >= 1.0 for row in rows)
    assert all(float(row["mass_action_residual_inf"]) <= 1.0e-10 for row in rows)


def test_generate_jax_picard_derivatives_writes_csv(tmp_path) -> None:
    output = tmp_path / "jax_picard_derivatives.csv"

    generated = generate_jax_picard_derivatives(output)

    assert generated == output
    text = output.read_text(encoding="utf-8")
    assert "picard_jax_value" in text
    assert "autodiff_backend" in text
