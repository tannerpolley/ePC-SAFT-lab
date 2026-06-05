from __future__ import annotations

from analyses.package_validation.explicit_association_toybox.scripts.picard_stress_derivatives import (
    run_picard_stress_derivative_rows,
)


def test_picard_stress_derivatives_include_jax_first_and_second_order_rows() -> None:
    rows = run_picard_stress_derivative_rows()

    assert rows
    assert {row["autodiff_backend"] for row in rows} == {"jax"}
    assert {int(row["derivative_order"]) for row in rows} >= {1, 2}
    assert all(row["stress_evidence_role"] for row in rows)
