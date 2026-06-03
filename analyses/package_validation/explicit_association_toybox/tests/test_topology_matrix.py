from __future__ import annotations

import csv
from pathlib import Path

from analyses.package_validation.explicit_association_toybox.scripts.run_topology_matrix import (
    TOPOLOGY_MATRIX_COLUMNS,
    run_topology_matrix,
)


def test_run_topology_matrix_writes_paper_metadata_columns(tmp_path: Path) -> None:
    output = tmp_path / "topology_matrix.csv"

    run_topology_matrix(
        output_path=output,
        topology_types=("2B",),
        closure_names=("closure_2b_exact_reduction", "explicit_picard_unroll_1"),
        density_grid=(0.2,),
        strength_grid=(3.0,),
    )

    with output.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))

    assert rows
    assert set(TOPOLOGY_MATRIX_COLUMNS) <= set(rows[0])
    names = {row["closure"] for row in rows}
    assert "topology_reduction_huang_radosz_2b" in names
    assert "closure_2b_exact_reduction" in names
    topology_row = next(row for row in rows if row["closure"] == "topology_reduction_huang_radosz_2b")
    assert topology_row["source_formula_family"] == "huang_radosz_table_vii"
    assert topology_row["source_formula_id"] == "huang_radosz_table_vii_2b"
    assert topology_row["comparison_role"] == "exact_topology_reduction"
    assert topology_row["evidence_band"] == "exact_reduction_verified"
