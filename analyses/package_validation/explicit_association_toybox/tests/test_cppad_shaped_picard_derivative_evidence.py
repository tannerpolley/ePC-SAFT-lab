from __future__ import annotations

from analyses.package_validation.explicit_association_toybox.scripts.cppad_shaped_derivative_evidence import (
    generate_cppad_shaped_derivative_evidence,
    run_cppad_shaped_derivative_evidence,
)


def test_cppad_shaped_derivative_rows_retain_expected_schema() -> None:
    rows = run_cppad_shaped_derivative_evidence()

    assert rows
    assert {
        "case_id",
        "topology_id",
        "target",
        "variable_block",
        "derivative_order",
        "backend",
        "exact_implicit_value",
        "picard_numpy_value",
        "picard_jax_value",
        "absolute_error",
        "relative_error",
        "finite_difference_step",
        "autodiff_status",
        "cppad_relevance_note",
        "admission_band",
        "baseline_status",
        "mass_action_residual_norm",
    } <= set(rows[0])
    assert {row["backend"] for row in rows} == {"jax_proxy_for_cppad_shape"}
    assert {row["autodiff_status"] for row in rows} == {"jax_x64"}
    assert any(row["target"] == "pressure_proxy_density" for row in rows)
    assert any(row["target"] == "fugacity_proxy_composition_0" for row in rows)
    assert any(row["target"] == "local_quadratic_prediction" for row in rows)
    assert all(float(row["mass_action_residual_norm"]) <= 1.0e-10 for row in rows)


def test_cppad_shaped_derivative_rows_keep_numpy_and_jax_paths_close() -> None:
    rows = run_cppad_shaped_derivative_evidence()

    exact_matches = [
        row
        for row in rows
        if row["target"] in {"a_assoc_density", "a_assoc_strength", "a_assoc_density_density"}
    ]
    assert exact_matches
    for row in exact_matches:
        difference = abs(float(row["picard_jax_value"]) - float(row["picard_numpy_value"]))
        if int(row["derivative_order"]) == 2:
            scale = max(abs(float(row["picard_jax_value"])), abs(float(row["picard_numpy_value"])), 1.0)
            assert difference <= max(1.0e-5, scale * 5.0e-7)
        else:
            assert difference <= 1.0e-6


def test_generate_cppad_shaped_derivative_evidence_writes_csv(tmp_path) -> None:
    output = tmp_path / "cppad_shaped_picard_derivative_evidence.csv"

    generated = generate_cppad_shaped_derivative_evidence(output)

    assert generated == output
    text = output.read_text(encoding="utf-8")
    assert "cppad_relevance_note" in text
    assert "local_quadratic_prediction" in text
