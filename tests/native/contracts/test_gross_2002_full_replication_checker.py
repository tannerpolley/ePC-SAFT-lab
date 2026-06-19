from __future__ import annotations

import json
from pathlib import Path

from scripts.validation import check_gross_2002_full_replication as checker


def _write(path: Path, text: str = "artifact\n") -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return str(path)


def _artifact_set(
    tmp_path: Path,
    figure_id: str,
    *,
    score: float = 8.0,
    derivative_status: str = "verified_exact",
) -> dict[str, str]:
    source_csv = _write(tmp_path / figure_id / "source.csv", "x,y\n0.1,1.0\n")
    qa_overlay_path = tmp_path / figure_id / "qa_overlay.png"
    source_metadata_json = _write(
        tmp_path / figure_id / "metadata.json",
        json.dumps(
            {
                "provenance": "unit-test digitization",
                "axis_calibration": {"x": "composition", "y": "temperature_K"},
                "units": {"x": "mole_fraction", "y": "K"},
                "series_labels": ["liquid"],
                "digitization_uncertainty": {"x": 0.002, "y": 0.2},
                "qa_overlay": str(qa_overlay_path),
            },
            sort_keys=True,
        )
        + "\n",
    )
    digitization_qa_overlay = _write(qa_overlay_path)
    model_csv = _write(tmp_path / figure_id / "model.csv", "x,y\n0.1,1.1\n")
    plotted_csv = _write(tmp_path / figure_id / "plotted.csv", "x_source,y_source,x_model,y_model\n0.1,1.0,0.1,1.1\n")
    score_json = _write(
        tmp_path / figure_id / "score.json",
        json.dumps(
            {
                "source_point_count": 1,
                "model_point_count": 1,
                "rmse_axis": {"x": 0.0, "y": 0.1},
                "max_axis_error": {"x": 0.0, "y": 0.1},
                "normalized_plot_score": score,
                "branch_coverage_score": 1.0,
                "derivative_status": derivative_status,
                "pass": score >= 7.0,
            },
            sort_keys=True,
        )
        + "\n",
    )
    summary_json = _write(tmp_path / figure_id / "summary.json", "{}\n")
    png = _write(tmp_path / figure_id / "plot.png")
    svg = _write(tmp_path / figure_id / "plot.svg")
    sidecar = _write(tmp_path / figure_id / "plot.mpl.yaml", "kind: matplotlib-figure\n")
    return {
        "source_csv": source_csv,
        "source_metadata_json": source_metadata_json,
        "digitization_qa_overlay": digitization_qa_overlay,
        "model_csv": model_csv,
        "plotted_csv": plotted_csv,
        "score_json": score_json,
        "summary_json": summary_json,
        "png": png,
        "svg": svg,
        "sidecar": sidecar,
    }


def _foundation_payload() -> dict[str, object]:
    return {
        "campaign": "gross_2002_full_replication",
        "artifact_contract": {"required_artifacts": list(checker.REQUIRED_ACCEPTED_ARTIFACT_KEYS)},
        "source_metadata_schema": {"required_fields": list(checker.REQUIRED_SOURCE_METADATA_FIELDS)},
        "score_schema": {
            "required_fields": list(checker.REQUIRED_SCORE_FIELDS),
            "thresholds": dict(checker.PLOT_FAMILY_THRESHOLDS) | {"diagnostic_score_cap": checker.DIAGNOSTIC_SCORE_CAP},
        },
        "figures": [
            {
                "figure_id": f"figure_{number:02d}",
                "plot_family": "t_rho" if number == 1 else "phase_boundary" if number in (8, 10) else "vle",
                "replication_status": "planned",
                "counts_toward_completion": False,
                "acceptance_threshold": 7.0 if number not in (8, 10) else 6.5,
            }
            for number in range(1, 11)
        ],
        "blockers": [],
    }


def _complete_payload(tmp_path: Path) -> dict[str, object]:
    figures = []
    for number in range(1, 11):
        figure_id = f"figure_{number:02d}"
        plot_family = "t_rho" if number == 1 else "phase_boundary" if number in (8, 10) else "vle"
        requires_exact = number in (8, 9, 10)
        figures.append(
            {
                "figure_id": figure_id,
                "plot_family": plot_family,
                "replication_status": "accepted",
                "counts_toward_completion": True,
                "acceptance_threshold": 7.0 if plot_family != "phase_boundary" else 6.5,
                "requires_exact_association_hessian": requires_exact,
                "source_identity_status": "resolved" if figure_id == "figure_02" else "not_required",
                "artifacts": _artifact_set(tmp_path, figure_id, derivative_status="verified_exact" if requires_exact else "not_required"),
            }
        )
    payload = _foundation_payload()
    payload["figures"] = figures
    return payload


def test_foundation_payload_accepts_planned_all_figures() -> None:
    result = checker.evaluate_payload(_foundation_payload(), require_foundation=True)

    assert result["foundation_complete"] is True
    assert result["complete"] is False
    assert result["planned_figures"] == [f"figure_{number:02d}" for number in range(1, 11)]
    assert result["blockers"] == []


def test_accepted_figure_requires_all_replication_artifacts(tmp_path: Path) -> None:
    artifacts = _artifact_set(tmp_path, "figure_08")
    artifacts.pop("source_metadata_json")
    payload = _foundation_payload()
    payload["figures"] = [
        {
            "figure_id": "figure_08",
            "plot_family": "phase_boundary",
            "replication_status": "accepted",
            "counts_toward_completion": True,
            "acceptance_threshold": 6.5,
            "requires_exact_association_hessian": True,
            "artifacts": artifacts,
        }
    ]

    result = checker.evaluate_payload(payload, require_complete=True)

    assert result["complete"] is False
    assert "gross_2002_figure_08_source_metadata_json_missing" in result["blockers"]


def test_low_score_blocks_accepted_figure(tmp_path: Path) -> None:
    artifacts = _artifact_set(tmp_path, "figure_02", score=5.0, derivative_status="not_required")
    payload = _foundation_payload()
    payload["figures"] = [
        {
            "figure_id": "figure_02",
            "plot_family": "vle",
            "replication_status": "accepted",
            "counts_toward_completion": True,
            "acceptance_threshold": 7.0,
            "requires_exact_association_hessian": False,
            "artifacts": artifacts,
        }
    ]

    result = checker.evaluate_payload(payload, require_complete=True)

    assert result["complete"] is False
    assert "gross_2002_figure_02_score_below_threshold" in result["blockers"]


def test_figure_one_requires_vapor_and_liquid_branch_scores(tmp_path: Path) -> None:
    artifacts = _artifact_set(tmp_path, "figure_01", derivative_status="verified_exact")
    score_path = Path(artifacts["score_json"])
    score_payload = json.loads(score_path.read_text(encoding="utf-8"))
    score_payload["branch_scores"] = {
        "methanol:liquid": {
            "source_point_count": 6,
            "model_point_count": 30,
            "rmse_axis": {"rho": 0.1, "T": 0.1},
            "max_axis_error": {"rho": 0.2, "T": 0.2},
            "normalized_plot_score": 8.0,
            "branch_coverage_score": 1.0,
            "derivative_status": "verified_exact",
            "pass": True,
        }
    }
    score_path.write_text(json.dumps(score_payload, sort_keys=True) + "\n", encoding="utf-8")
    payload = _foundation_payload()
    payload["figures"] = [
        {
            "figure_id": "figure_01",
            "plot_family": "t_rho",
            "replication_status": "accepted",
            "counts_toward_completion": True,
            "acceptance_threshold": 7.0,
            "requires_exact_association_hessian": True,
            "required_branches": ["methanol:vapor", "methanol:liquid"],
            "artifacts": artifacts,
        }
    ]

    result = checker.evaluate_payload(payload, require_complete=True, require_exact_association_hessian=True)

    assert result["complete"] is False
    assert "gross_2002_figure_01_required_branch_methanol_vapor_missing" in result["blockers"]


def test_figure_two_identity_must_be_resolved_before_acceptance(tmp_path: Path) -> None:
    artifacts = _artifact_set(tmp_path, "figure_02", derivative_status="verified_exact")
    payload = _foundation_payload()
    payload["figures"] = [
        {
            "figure_id": "figure_02",
            "plot_family": "vle",
            "replication_status": "accepted",
            "counts_toward_completion": True,
            "acceptance_threshold": 7.0,
            "requires_exact_association_hessian": True,
            "source_identity_status": "unresolved",
            "artifacts": artifacts,
        }
    ]

    result = checker.evaluate_payload(payload, require_complete=True)

    assert result["complete"] is False
    assert "gross_2002_figure_02_source_identity_unresolved" in result["blockers"]


def test_complete_payload_accepts_all_figures(tmp_path: Path) -> None:
    result = checker.evaluate_payload(_complete_payload(tmp_path), require_complete=True)

    assert result["foundation_complete"] is True
    assert result["complete"] is True
    assert result["accepted_figures"] == [f"figure_{number:02d}" for number in range(1, 11)]
    assert result["blockers"] == []


def test_cli_foundation_passes_committed_manifest(capsys) -> None:
    exit_code = checker.main(["--json", "--require-foundation"])

    payload = json.loads(capsys.readouterr().out)
    assert exit_code == 0
    assert payload["foundation_complete"] is True
    assert payload["complete"] is False


def test_cli_require_complete_reports_planned_figure_blockers(capsys) -> None:
    exit_code = checker.main(["--json", "--require-complete"])

    payload = json.loads(capsys.readouterr().out)
    assert exit_code == 2
    assert "gross_2002_figure_02_full_replication_missing" in payload["blockers"]
    assert "gross_2002_figure_10_full_replication_missing" in payload["blockers"]
