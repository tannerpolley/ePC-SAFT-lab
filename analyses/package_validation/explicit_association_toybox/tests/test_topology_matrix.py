from __future__ import annotations

import csv
from pathlib import Path

import pytest

from analyses.package_validation.explicit_association_toybox.scripts.run_topology_matrix import (
    TOPOLOGY_MATRIX_COLUMNS,
    run_topology_matrix,
)


def test_run_topology_matrix_writes_paper_metadata_columns(tmp_path: Path) -> None:
    output = tmp_path / "topology_matrix.csv"

    run_topology_matrix(
        output_path=output,
        topology_types=("2B",),
        closure_names=("exact_2b_reduction", "damped_picard_7_05"),
        density_grid=(0.2,),
        strength_grid=(3.0,),
    )

    with output.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))

    assert rows
    assert set(TOPOLOGY_MATRIX_COLUMNS) <= set(rows[0])
    assert {
        "topology_id",
        "closure_name",
        "rho_delta",
        "ares_assoc_rel_error",
        "mass_action_residual_inf",
        "exact_implicit_elapsed_seconds",
        "evidence_band",
    } <= set(rows[0])
    names = {row["closure"] for row in rows}
    assert "topology_reduction_huang_radosz_2b" in names
    assert "exact_2b_reduction" in names
    topology_row = next(row for row in rows if row["closure"] == "topology_reduction_huang_radosz_2b")
    assert topology_row["topology_id"] == "hr_2b"
    assert topology_row["closure_name"] == topology_row["closure"]
    assert float(topology_row["rho_delta"]) == pytest.approx(0.6)
    assert float(topology_row["ares_assoc_rel_error"]) <= 1.0e-12
    assert float(topology_row["mass_action_residual_inf"]) <= 1.0e-10
    assert float(topology_row["exact_implicit_elapsed_seconds"]) > 0.0
    assert topology_row["source_formula_family"] == "huang_radosz_table_vii"
    assert topology_row["source_formula_id"] == "huang_radosz_table_vii_2b"
    assert topology_row["comparison_role"] == "exact_topology_reduction"
    assert topology_row["evidence_band"] == "exact_reduction_verified"
