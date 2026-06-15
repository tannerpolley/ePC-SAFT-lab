from __future__ import annotations

import csv
import json
import shutil
from pathlib import Path
from typing import Any

import pytest

from scripts.validation import check_boundary_workflows as checker


REPO_ROOT = Path(__file__).resolve().parents[3]
CASE_DIR = (
    REPO_ROOT
    / "data"
    / "reference"
    / "equilibrium_benchmarks"
    / "neutral_lle"
    / "matsuda_2011_pfhexane_hexane"
)


def _copy_case(tmp_path: Path) -> Path:
    case_dir = tmp_path / "matsuda_case"
    shutil.copytree(CASE_DIR, case_dir)
    return case_dir


def _read_rows(path: Path) -> list[dict[str, str]]:
    return list(csv.DictReader(path.read_text(encoding="utf-8").splitlines()))


def _write_rows(path: Path, rows: list[dict[str, str]]) -> None:
    fieldnames = list(rows[0]) if rows else [
        "source_dataset",
        "row_index",
        "temperature_K",
        "pressure_kPa",
        "component_1",
        "component_2",
        "x_perfluorohexane",
        "combined_temperature_uncertainty_K",
        "method",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _mutate_binodal(case_dir: Path, updates: dict[str, Any]) -> None:
    path = case_dir / "source_binodal_points.csv"
    rows = _read_rows(path)
    rows[0].update({key: str(value) for key, value in updates.items()})
    _write_rows(path, rows)


def test_cloud_shadow_gate_reports_retained_source_data() -> None:
    payload = checker.evaluate_cloud_shadow_gate(CASE_DIR)

    assert payload["complete"] is True
    assert payload["status"] == "source_data_gate_complete"
    assert payload["source_data_blockers"] == []
    assert payload["route_admission_blockers"] == [
        "native_cloud_point_route_absent",
        "native_shadow_point_route_absent",
    ]
    assert payload["source_fixture"] == (
        "data/reference/equilibrium_benchmarks/neutral_lle/matsuda_2011_pfhexane_hexane"
    )
    assert payload["species"] == ["perfluorohexane", "hexane"]
    assert payload["binodal_point_count"] == 14
    assert payload["paired_cloud_shadow_count"] == 1
    assert payload["pressure_kPa"] == 101.3
    assert payload["paired_pressure_Pa"] == 101300.0
    assert payload["temperature_range_K"] == [285.09, 296.26]
    assert payload["composition_range_x1"] == [0.1498, 0.7]
    assert payload["paired_branch_compositions"] == [[0.2, 0.8], [0.5497, 0.4503]]
    assert payload["branch_temperature_gap_K"] == 0.01
    assert payload["branch_temperature_gap_threshold_K"] == 0.2
    assert payload["method_set"] == ["cloud_point"]


@pytest.mark.parametrize(
    ("updates", "expected_blocker"),
    [
        ({"component_1": "hexane"}, "cloud_shadow_binodal_species_order_mismatch"),
        ({"method": "bubble_point"}, "cloud_shadow_binodal_method_rejected"),
        ({"temperature_K": "nan"}, "cloud_shadow_binodal_temperature_invalid"),
        ({"pressure_kPa": "0.0"}, "cloud_shadow_binodal_pressure_invalid"),
        ({"x_perfluorohexane": "1.25"}, "cloud_shadow_binodal_composition_invalid"),
    ],
)
def test_cloud_shadow_gate_rejects_malformed_binodal_rows(
    tmp_path: Path,
    updates: dict[str, Any],
    expected_blocker: str,
) -> None:
    case_dir = _copy_case(tmp_path)
    _mutate_binodal(case_dir, updates)

    payload = checker.evaluate_cloud_shadow_gate(case_dir)

    assert payload["complete"] is False
    assert expected_blocker in payload["source_data_blockers"]


def test_cloud_shadow_gate_rejects_missing_binodal_file(tmp_path: Path) -> None:
    case_dir = _copy_case(tmp_path)
    (case_dir / "source_binodal_points.csv").unlink()

    payload = checker.evaluate_cloud_shadow_gate(case_dir)

    assert payload["complete"] is False
    assert "missing_required_file:source_binodal_points.csv" in payload["source_data_blockers"]


def test_cloud_shadow_gate_rejects_dropped_binodal_rows(tmp_path: Path) -> None:
    case_dir = _copy_case(tmp_path)
    path = case_dir / "source_binodal_points.csv"
    rows = _read_rows(path)
    _write_rows(path, rows[:-1])

    payload = checker.evaluate_cloud_shadow_gate(case_dir)

    assert payload["complete"] is False
    assert "cloud_shadow_source_binodal_rows_count_mismatch" in payload["source_data_blockers"]


def test_cloud_shadow_gate_rejects_missing_paired_branch_row(tmp_path: Path) -> None:
    case_dir = _copy_case(tmp_path)
    path = case_dir / "experimental_tielines.csv"
    rows = _read_rows(path)
    _write_rows(path, [])

    payload = checker.evaluate_cloud_shadow_gate(case_dir)

    assert payload["complete"] is False
    assert "cloud_shadow_paired_branch_rows_missing" in payload["source_data_blockers"]


def test_cloud_shadow_gate_rejects_forbidden_physics_activation(tmp_path: Path) -> None:
    case_dir = _copy_case(tmp_path)
    path = case_dir / "metadata.json"
    metadata = json.loads(path.read_text(encoding="utf-8"))
    metadata["association_active"] = True
    path.write_text(json.dumps(metadata), encoding="utf-8")

    payload = checker.evaluate_cloud_shadow_gate(case_dir)

    assert payload["complete"] is False
    assert "cloud_shadow_forbidden_physics_active:association_active" in payload["source_data_blockers"]


def test_cloud_shadow_gate_rejects_executable_route_claims_without_route_evidence() -> None:
    workflows = [
        {"label": "Cloud point", "routes": ["cloud_pressure"]},
        {"label": "Shadow point", "routes": ["shadow_pressure"]},
    ]

    payload = checker.evaluate_cloud_shadow_gate(CASE_DIR, workflows=workflows)

    assert payload["complete"] is False
    assert "cloud_shadow_unproven_runtime_route_claim:Cloud point" in payload["source_data_blockers"]
    assert "cloud_shadow_unproven_runtime_route_claim:Shadow point" in payload["source_data_blockers"]
