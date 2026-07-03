from __future__ import annotations

import csv
import math
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[4]
FIGURE_ROOT = REPO_ROOT / "analyses" / "paper_validation" / "2026_khudaida" / "figures" / "figure_02"
KHUDAIDA_MIN_PHASE_DISTANCE = 1.0e-3
KHUDAIDA_MINOR_BETA_REVIEW = 1.0e-4


def _rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def _finite(value: str) -> bool:
    if value == "":
        return False
    return math.isfinite(float(value))


def test_khudaida_figure_02_public_route_artifacts_retain_model_or_blocker_evidence() -> None:
    source_rows = _rows(FIGURE_ROOT / "source" / "source_points.csv")
    feed_rows = _rows(FIGURE_ROOT / "source" / "feed_compositions.csv")
    model_rows = _rows(FIGURE_ROOT / "results" / "data" / "model_tielines.csv")
    stats = _rows(FIGURE_ROOT / "results" / "fit_statistics.csv")

    assert len(feed_rows) == 8
    assert len(model_rows) == 16
    assert len(stats) == 1

    source_datasets = {}
    for row in source_rows:
        source_datasets[row["dataset"]] = source_datasets.get(row["dataset"], 0) + 1
    assert source_datasets == {"experimental_tieline": 16, "feed": 8, "paper_epcsaft": 8}
    assert {row["temperature_K"] for row in source_rows} == {"293.15"}
    assert {row["salt_wtfrac"] for row in source_rows} == {"0.05"}

    model_by_tie: dict[str, set[str]] = {}
    converged_ties: set[str] = set()
    failed_ties: set[str] = set()
    for row in model_rows:
        model_by_tie.setdefault(row["tie_line"], set()).add(row["phase"])
        assert row["source"] == "epcsaft_public_electrolyte_lle"
        assert _finite(row["feed_x_water"])
        assert _finite(row["feed_x_ethanol"])
        assert _finite(row["feed_x_isobutanol"])
        assert _finite(row["feed_x_nacl"])
        if row["converged"] == "True":
            converged_ties.add(row["tie_line"])
            assert row["status"] == "accepted"
            assert row["route_status"] == "production_accepted"
            assert row["solver_status"] == "success"
            assert row["application_status"] == "solve_succeeded"
            assert row["postsolve_accepted"] == "True"
            assert row["exact_hessian_available"] == "True"
            assert row["hessian_approximation"] == "exact"
            assert row["route_hessian_approximation"] == "exact"
            assert _finite(row["x_water"])
            assert _finite(row["x_ethanol"])
            assert _finite(row["x_isobutanol"])
            assert _finite(row["x_nacl"])
            assert _finite(row["beta"])
            assert _finite(row["objective"])
            assert _finite(row["phase_distance"])
            assert float(row["phase_distance"]) >= KHUDAIDA_MIN_PHASE_DISTANCE
            assert float(row["beta"]) >= KHUDAIDA_MINOR_BETA_REVIEW
        else:
            failed_ties.add(row["tie_line"])
            assert row["message"] != ""

    assert model_by_tie == {str(tie): {"organic", "aqueous"} for tie in range(1, 9)}

    stat = stats[0]
    assert stat["series"] == "package_electrolyte_lle_vs_experimental"
    assert stat["temperature_K"] == "293.15"
    assert stat["salt_wtfrac"] == "0.05"
    assert stat["source_point_count"] == "16"
    assert stat["model_point_count"] == "16"
    assert stat["accepted_model_count"] == str(2 * len(converged_ties))
    assert _finite(stat["rmse"])
    assert _finite(stat["max_abs_error"])
    assert "formula-basis" in stat["score_basis"]
    if stat["pass"] == "True":
        assert stat["accepted_model_count"] == "16"
        assert stat["failed_tie_lines"] == ""
        assert stat["failure_reasons"] == ""
    else:
        assert stat["failed_tie_lines"] == ",".join(str(tie) for tie in range(1, 9))
        assert "objective=" in stat["failure_reasons"]
        assert "phase_distance=" in stat["failure_reasons"]
        assert failed_ties
        for tie_line in failed_ties:
            assert f"{tie_line}:Native electrolyte LLE postsolve certification did not complete." in stat["failure_reasons"]
