from __future__ import annotations

from analyses.package_validation.explicit_association_toybox.scripts.cppad_shaped_property_evidence import (
    generate_cppad_shaped_property_evidence,
    run_cppad_shaped_property_evidence,
)


def test_cppad_shaped_property_rows_retain_expected_schema() -> None:
    rows = run_cppad_shaped_property_evidence()

    assert rows
    assert {
        "case_id",
        "topology_id",
        "component_family",
        "mixture_family",
        "temperature",
        "density",
        "composition",
        "association_strength_matrix",
        "picard_backend",
        "association_helmholtz_exact",
        "association_helmholtz_picard",
        "total_residual_helmholtz_exact",
        "total_residual_helmholtz_picard",
        "pressure_exact",
        "pressure_picard",
        "fugacity_proxy_exact",
        "fugacity_proxy_picard",
        "density_root_status",
        "mass_action_residual_norm",
        "absolute_error",
        "relative_error",
    } <= set(rows[0])
    assert {row["picard_backend"] for row in rows} == {"numpy", "jax"}
    assert {row["density_root_status"] for row in rows} == {"fixed_density_grid_point"}
    assert any(row["mixture_family"] == "binary_cross_associating" for row in rows)
    assert any(row["case_id"] == "pure_4c_labeled" for row in rows)


def test_cppad_shaped_property_rows_keep_numpy_and_jax_values_close() -> None:
    rows = run_cppad_shaped_property_evidence()
    indexed = {
        (row["case_id"], float(row["density"]), row["picard_backend"]): row
        for row in rows
    }

    for key, numpy_row in indexed.items():
        case_id, density, backend = key
        if backend != "numpy":
            continue
        jax_row = indexed[(case_id, density, "jax")]
        assert float(jax_row["association_helmholtz_picard"]) == float(numpy_row["association_helmholtz_picard"])


def test_generate_cppad_shaped_property_evidence_writes_csv(tmp_path) -> None:
    output = tmp_path / "cppad_shaped_picard_property_evidence.csv"

    generated = generate_cppad_shaped_property_evidence(output)

    assert generated == output
    text = output.read_text(encoding="utf-8")
    assert "association_helmholtz_picard" in text
    assert "picard_backend" in text
