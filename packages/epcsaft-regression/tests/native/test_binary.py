from __future__ import annotations

import csv

import numpy as np
import pytest
from epcsaft._types import InputError
from epcsaft.model.datasets import _load_source_interactions
from epcsaft_regression.core import BINARY_PAIR_MODE, FitProblem, FitResult, write_fit_result
from epcsaft_regression.native_adapter import _fit_generic_native_ceres


def test_ceres_binary_kij_regression_uses_native_cppad_implicit_jacobian() -> None:
    payload = {
        "MW": np.asarray([0.016043, 0.03007], dtype=float),
        "m": np.asarray([1.0, 1.6069], dtype=float),
        "s": np.asarray([3.7039, 3.5206], dtype=float),
        "e": np.asarray([150.03, 191.42], dtype=float),
        "e_assoc": np.asarray([0.0, 0.0], dtype=float),
        "vol_a": np.asarray([0.0, 0.0], dtype=float),
        "assoc_scheme": [None, None],
        "k_ij": np.asarray([[0.0, 0.01], [0.01, 0.0]], dtype=float),
        "l_ij": np.zeros((2, 2), dtype=float),
        "k_hb": np.zeros((2, 2), dtype=float),
    }
    records = [
        {
            "term_name": "binary_vle_fugacity_balance",
            "term": 5,
            "T": 180.0,
            "P": 1.0e6,
            "x": [0.35, 0.65],
            "y": [0.74, 0.26],
            "target_index": 0,
            "target_index_2": 1,
            "scale": 1.0,
        },
        {
            "term_name": "binary_vle_fugacity_balance",
            "term": 5,
            "T": 190.0,
            "P": 1.2e6,
            "x": [0.42, 0.58],
            "y": [0.79, 0.21],
            "target_index": 0,
            "target_index_2": 1,
            "scale": 1.0,
        },
    ]

    result = _fit_generic_native_ceres(
        [payload, payload],
        records,
        np.asarray([6], dtype=int),
        np.asarray([0], dtype=int),
        np.asarray([1], dtype=int),
        np.asarray([0.01], dtype=float),
        np.asarray([-0.15], dtype=float),
        np.asarray([0.10], dtype=float),
    )

    assert result["success"] is True
    assert result["backend"] == "ceres"
    assert result["optimizer_backend"] == "ceres"
    assert result["derivative_backend"] == "cppad_implicit"
    assert result["jacobian_backend"] == "cppad_implicit"
    assert result["jacobian_available"] is True
    assert result["cost"] <= result["initial_cost"] + 1.0e-12
    assert -0.15 <= float(result["x"][0]) <= 0.10
    assert "binary_vle_fugacity_balance" in result["metrics_by_term"]


def test_ceres_binary_kij_regression_accepts_associating_neutral_rows() -> None:
    payload = {
        "MW": np.asarray([0.01801528, 0.03007], dtype=float),
        "m": np.asarray([1.2047, 1.6069], dtype=float),
        "s": np.asarray([3.0, 3.5206], dtype=float),
        "e": np.asarray([353.95, 191.42], dtype=float),
        "e_assoc": np.asarray([2425.7, 0.0], dtype=float),
        "vol_a": np.asarray([0.04509, 0.0], dtype=float),
        "assoc_scheme": ["2B", None],
        "k_ij": np.asarray([[0.0, 0.01], [0.01, 0.0]], dtype=float),
    }
    records = [
        {
            "term_name": "binary_vle_fugacity_balance",
            "term": 5,
            "T": 298.15,
            "P": 100000.0,
            "x": [0.55, 0.45],
            "y": [0.2, 0.8],
            "target_index": 0,
            "target_index_2": 1,
            "scale": 1.0,
        }
    ]

    result = _fit_generic_native_ceres(
        [payload],
        records,
        np.asarray([6], dtype=int),
        np.asarray([0], dtype=int),
        np.asarray([1], dtype=int),
        np.asarray([0.01], dtype=float),
        np.asarray([-0.15], dtype=float),
        np.asarray([0.10], dtype=float),
        max_nfev=1,
    )

    assert result["success"] is True
    assert result["backend"] == "ceres"
    assert result["optimizer_backend"] == "ceres"
    assert result["derivative_backend"] == "cppad_implicit"
    assert result["jacobian_backend"] == "cppad_implicit"
    assert result["jacobian_available"] is True
    assert result["message"].startswith("Ceres Solver Report")
    assert "without" + " optimizer" not in result["message"]
    assert result["iterations"] > 0
    assert "binary_vle_fugacity_balance" in result["metrics_by_term"]


def test_ceres_binary_kij_regression_rejects_nonpositive_iteration_limit() -> None:
    with pytest.raises(InputError, match="max_nfev >= 1"):
        _fit_generic_native_ceres(
            [],
            [],
            np.asarray([6]),
            np.asarray([0]),
            np.asarray([1]),
            [0.0],
            [-0.1],
            [0.1],
            0,
        )


def test_binary_fit_persistence_updates_manifest_and_strict_reload(tmp_path) -> None:
    binary_dir = tmp_path / "mixed" / "binary_interaction"
    binary_dir.mkdir(parents=True)
    matrix = "component,Component A,Component B\nComponent A,0,0.125\nComponent B,0.125,0\n"
    for name in ("k_ij.csv", "l_ij.csv", "k_hb_ij.csv"):
        (binary_dir / name).write_text(matrix if name == "k_ij.csv" else matrix.replace("0.125", "0"), encoding="utf-8")
    manifest = (
        "parameter,component_i,component_j,value,source,provenance_status\n"
        "k_ij,Component A,Component B,0.125,Source Table 4,source_backed\n"
        "l_ij,Component A,Component B,0,Source Eq. 5,source_backed\n"
        "k_hb_ij,Component A,Component B,0,Source Eq. 6,source_backed\n"
    )
    manifest_path = binary_dir / "source_manifest.csv"
    manifest_path.write_text(manifest, encoding="utf-8")

    problem = FitProblem(
        mode=BINARY_PAIR_MODE,
        pair=("Component A", "Component B"),
        fit_targets=("k_ij",),
    )
    result = FitResult(
        problem=problem,
        fitted_values={"k_ij": 0.25},
        rendered_values={"k_ij": 0.25},
    )

    written = write_fit_result(result, tmp_path, overwrite=True)

    assert binary_dir / "k_ij.csv" in written
    assert manifest_path in written
    with manifest_path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    fitted_row = next(row for row in rows if row["parameter"] == "k_ij")
    assert fitted_row["component_i"] == "Component A"
    assert fitted_row["component_j"] == "Component B"
    assert fitted_row["value"] == "0.25"
    assert fitted_row["provenance_status"] == "fitted"

    records = _load_source_interactions(tmp_path, ("Component A", "Component B"))
    fitted = next(record for record in records if record.family == "k_ij")
    assert fitted.value == pytest.approx(0.25)
    assert fitted.provenance.kind == "fitted"
