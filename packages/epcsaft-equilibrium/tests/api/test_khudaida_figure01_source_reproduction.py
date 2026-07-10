from __future__ import annotations

import csv
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
FIGURE_ROOT = REPO_ROOT / "analyses" / "paper_validation" / "2026_khudaida" / "figures" / "figure_01"


def _rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def test_khudaida_figure_01_electrolyte_source_recreation_retains_traceable_rows() -> None:
    source_rows = _rows(FIGURE_ROOT / "source" / "source_points.csv")
    plotted_rows = _rows(FIGURE_ROOT / "results" / "plotted_data.csv")
    recreation_rows = _rows(FIGURE_ROOT / "results" / "model_curve.csv")
    stats = _rows(FIGURE_ROOT / "results" / "fit_statistics.csv")

    assert len(source_rows) == 42
    assert len(plotted_rows) == 42
    assert len(recreation_rows) == 42
    assert len(stats) == 1

    datasets = {row["dataset"] for row in source_rows}
    assert datasets == {"without_nacl", "with_5wt_nacl", "with_10wt_nacl"}
    assert {row["salt_wtfrac"] for row in source_rows} == {"0.0", "0.05", "0.1"}
    assert {row["phase"] for row in source_rows} == {"organic", "aqueous"}

    stat = stats[0]
    assert stat["series"] == "source_recreation"
    assert stat["source_point_count"] == "42"
    assert stat["model_point_count"] == "0"
    assert stat["accepted_model_count"] == "0"
    assert stat["pass"] == "True"
    assert "no ePC-SAFT model curve" in stat["score_basis"]


def test_khudaida_figure_01_electrolyte_scope_records_figiel_parameter_boundary() -> None:
    notes = _rows(FIGURE_ROOT / "source" / "source_notes.csv")
    by_key = {(row["section"], row["key"]): row for row in notes}

    route = by_key[("model", "route")]
    assert route["value"] == "source-data recreation"
    assert "paper caption has no ePC-SAFT model curve" in route["notes"]

    route_scope = by_key[("model", "package_route_scope")]
    assert route_scope["value"] == "figures_02_07_and_s2_s3"
    assert "Internal electrolyte diagnostics start" in route_scope["notes"]

    figiel_boundary = by_key[("parameters", "figiel_2025_snapshot")]
    assert figiel_boundary["value"] == "out_of_scope_for_figure_01_source_recreation"
    assert "does not consume fitted ePC-SAFT parameters" in figiel_boundary["notes"]
