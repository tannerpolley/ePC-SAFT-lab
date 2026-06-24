from __future__ import annotations

import csv
import json
from pathlib import Path

from scripts.validation import check_gross_2002_full_replication as checker


def _write(path: Path, text: str = "artifact\n") -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return str(path)


def _fit_statistics_text(
    *,
    score: float = 8.0,
    proof_status: str = "verified_exact",
    series: list[str] | None = None,
    branches: list[str] | None = None,
) -> str:
    fields = ["scope", "series", "component", "branch", *checker.CSV_STATISTIC_FIELDS]
    rows: list[dict[str, object]] = [
        {
            "scope": "figure",
            "source_point_count": 1,
            "model_point_count": 1,
            "normalized_plot_score": score,
            "branch_coverage_score": 1.0,
            checker.PROOF_STATUS_FIELD: proof_status,
            "pass": score >= 8.0,
        }
    ]
    for item in series or []:
        rows.append(
            {
                "scope": "series",
                "series": item,
                "source_point_count": 1,
                "model_point_count": 1,
                "normalized_plot_score": score,
                "branch_coverage_score": 1.0,
                checker.PROOF_STATUS_FIELD: proof_status,
                "pass": score >= 8.0,
            }
        )
    for item in branches or []:
        component, _, branch = item.partition(":")
        rows.append(
            {
                "scope": "branch",
                "component": component,
                "branch": branch,
                "source_point_count": 1,
                "model_point_count": 1,
                "normalized_plot_score": score,
                "branch_coverage_score": 1.0,
                checker.PROOF_STATUS_FIELD: proof_status,
                "pass": score >= 8.0,
            }
        )

    output = []
    writer_row = {field: "" for field in fields}
    output.append(",".join(fields))
    for row in rows:
        writer_row.update(row)
        output.append(",".join(str(writer_row.get(field, "")) for field in fields))
        writer_row = {field: "" for field in fields}
    return "\n".join(output) + "\n"


def _artifact_set(
    tmp_path: Path,
    figure_id: str,
    *,
    score: float = 8.0,
    proof_status: str = "verified_exact",
    series: list[str] | None = None,
    branches: list[str] | None = None,
) -> dict[str, str]:
    source_csv = _write(tmp_path / figure_id / "source.csv", "x,y\n0.1,1.0\n")
    source_notes_csv = _write(tmp_path / figure_id / "source_notes.csv", "section,key,value,unit,notes\n")
    model_csv = _write(tmp_path / figure_id / "model.csv", "x,y\n0.1,1.1\n")
    plotted_csv = _write(tmp_path / figure_id / "plotted.csv", "x_source,y_source,x_model,y_model\n0.1,1.0,0.1,1.1\n")
    fit_statistics_csv = _write(
        tmp_path / figure_id / "fit_statistics.csv",
        _fit_statistics_text(score=score, proof_status=proof_status, series=series, branches=branches),
    )
    png = _write(tmp_path / figure_id / "plot.png")
    svg = _write(tmp_path / figure_id / "plot.svg")
    pdf = _write(tmp_path / figure_id / "plot.pdf")
    return {
        "source_csv": source_csv,
        "source_notes_csv": source_notes_csv,
        "model_csv": model_csv,
        "plotted_csv": plotted_csv,
        "fit_statistics_csv": fit_statistics_csv,
        "png": png,
        "svg": svg,
        "pdf": pdf,
    }


def _foundation_payload() -> dict[str, object]:
    return {
        "campaign": "gross_2002_full_replication",
        "artifact_contract": {"required_artifacts": list(checker.REQUIRED_ACCEPTED_ARTIFACT_KEYS)},
        "score_schema": {
            "required_fields": list(checker.CSV_STATISTIC_FIELDS),
            "thresholds": dict(checker.PLOT_FAMILY_THRESHOLDS) | {"diagnostic_score_cap": checker.DIAGNOSTIC_SCORE_CAP},
        },
        "figures": [
            {
                "figure_id": f"figure_{number:02d}",
                "plot_family": "t_rho" if number == 1 else "phase_boundary" if number in (8, 10) else "vle",
                "replication_status": "planned",
                "counts_toward_completion": False,
                "acceptance_threshold": 8.0,
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
        artifacts = _artifact_set(tmp_path, figure_id, proof_status="verified_exact" if requires_exact else "not_required")
        figures.append(
            {
                "figure_id": figure_id,
                "plot_family": plot_family,
                "replication_status": "accepted",
                "counts_toward_completion": True,
                "acceptance_threshold": 8.0,
                checker.SECOND_ORDER_REQUIRED_FIELD: requires_exact,
                "source_identity_status": "resolved" if figure_id == "figure_02" else "not_required",
                "artifacts": artifacts,
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
    artifacts.pop("source_notes_csv")
    payload = _foundation_payload()
    payload["figures"] = [
        {
            "figure_id": "figure_08",
            "plot_family": "phase_boundary",
            "replication_status": "accepted",
            "counts_toward_completion": True,
            "acceptance_threshold": 8.0,
            checker.SECOND_ORDER_REQUIRED_FIELD: True,
            "artifacts": artifacts,
        }
    ]

    result = checker.evaluate_payload(payload, require_complete=True)

    assert result["complete"] is False
    assert "gross_2002_figure_08_source_notes_csv_missing" in result["blockers"]


def test_low_score_blocks_accepted_figure(tmp_path: Path) -> None:
    artifacts = _artifact_set(tmp_path, "figure_02", score=5.0, proof_status="not_required")
    payload = _foundation_payload()
    payload["figures"] = [
        {
            "figure_id": "figure_02",
            "plot_family": "vle",
            "replication_status": "accepted",
            "counts_toward_completion": True,
            "acceptance_threshold": 8.0,
            checker.SECOND_ORDER_REQUIRED_FIELD: False,
            "source_identity_status": "resolved",
            "artifacts": artifacts,
        }
    ]

    result = checker.evaluate_payload(payload, require_complete=True)

    assert result["complete"] is False
    assert "gross_2002_figure_02_score_below_threshold" in result["blockers"]


def test_figure_one_requires_vapor_and_liquid_branch_scores(tmp_path: Path) -> None:
    artifacts = _artifact_set(tmp_path, "figure_01", proof_status="verified_exact", branches=["methanol:liquid"])
    payload = _foundation_payload()
    payload["figures"] = [
        {
            "figure_id": "figure_01",
            "plot_family": "t_rho",
            "replication_status": "accepted",
            "counts_toward_completion": True,
            "acceptance_threshold": 8.0,
            checker.SECOND_ORDER_REQUIRED_FIELD: True,
            "required_branches": ["methanol:vapor", "methanol:liquid"],
            "artifacts": artifacts,
        }
    ]

    result = checker.evaluate_payload(payload, require_complete=True, require_second_order_proof=True)

    assert result["complete"] is False
    assert "gross_2002_figure_01_required_branch_methanol_vapor_missing" in result["blockers"]


def test_figure_two_identity_must_be_resolved_before_acceptance(tmp_path: Path) -> None:
    artifacts = _artifact_set(tmp_path, "figure_02", proof_status="verified_exact")
    payload = _foundation_payload()
    payload["figures"] = [
        {
            "figure_id": "figure_02",
            "plot_family": "vle",
            "replication_status": "accepted",
            "counts_toward_completion": True,
            "acceptance_threshold": 8.0,
            checker.SECOND_ORDER_REQUIRED_FIELD: True,
            "source_identity_status": "unresolved",
            "artifacts": artifacts,
        }
    ]

    result = checker.evaluate_payload(payload, require_complete=True)

    assert result["complete"] is False
    assert "gross_2002_figure_02_source_identity_unresolved" in result["blockers"]


def test_accepted_vle_figures_require_all_series_scores(tmp_path: Path) -> None:
    figure_03_artifacts = _artifact_set(
        tmp_path,
        "figure_03",
        proof_status="verified_exact",
        series=["pressure_series_low"],
    )
    figure_05_artifacts = _artifact_set(
        tmp_path,
        "figure_05",
        proof_status="verified_exact",
        series=["1-propanol-benzene"],
    )
    payload = _foundation_payload()
    payload["figures"] = [
        {
            "figure_id": "figure_03",
            "plot_family": "vle",
            "replication_status": "accepted",
            "counts_toward_completion": True,
            "acceptance_threshold": 8.0,
            checker.SECOND_ORDER_REQUIRED_FIELD: True,
            "required_series": ["pressure_series_low", "pressure_series_high"],
            "artifacts": figure_03_artifacts,
        },
        {
            "figure_id": "figure_05",
            "plot_family": "vle",
            "replication_status": "accepted",
            "counts_toward_completion": True,
            "acceptance_threshold": 8.0,
            checker.SECOND_ORDER_REQUIRED_FIELD: True,
            "required_series": ["1-propanol-benzene", "2-propanol-benzene"],
            "artifacts": figure_05_artifacts,
        },
    ]

    result = checker.evaluate_payload(payload, require_complete=True)

    assert result["complete"] is False
    assert "gross_2002_figure_03_required_series_pressure_series_high_missing" in result["blockers"]
    assert "gross_2002_figure_05_required_series_2_propanol_benzene_missing" in result["blockers"]


def test_accepted_figure_two_requires_trace_summary_artifact(tmp_path: Path) -> None:
    artifacts = _artifact_set(
        tmp_path,
        "figure_02",
        proof_status="verified_exact",
        series=["bubble_line", "dew_line"],
    )
    payload = _foundation_payload()
    payload["figures"] = [
        {
            "figure_id": "figure_02",
            "plot_family": "vle",
            "replication_status": "accepted",
            "counts_toward_completion": True,
            "acceptance_threshold": 8.0,
            checker.SECOND_ORDER_REQUIRED_FIELD: True,
            "source_identity_status": "resolved",
            "required_series": ["bubble_line", "dew_line"],
            "requires_branch_trace": True,
            "trace_requirements": {
                "max_coordinate_gap": 0.075,
                "max_interpolation_error": 0.35,
                "required_series": ["bubble_line", "dew_line"],
            },
            "artifacts": artifacts,
        }
    ]

    result = checker.evaluate_payload(payload, require_complete=True)

    assert result["complete"] is False
    assert "gross_2002_figure_02_trace_summary_json_missing" in result["blockers"]


def test_accepted_figure_two_requires_complete_trace_series(tmp_path: Path) -> None:
    artifacts = _artifact_set(
        tmp_path,
        "figure_02",
        proof_status="verified_exact",
        series=["bubble_line", "dew_line"],
    )
    artifacts["trace_summary_json"] = _write(
        tmp_path / "figure_02" / "trace_summary.json",
        json.dumps(
            {
                "figure_id": "figure_02",
                "trace_contract": "m4_boundary_route_trace_v1",
                "traces": [
                    {
                        "series": "bubble_line",
                        "route": "bubble_pressure",
                        "complete": False,
                        "required_anchor_count": 3,
                        "solved_required_anchor_count": 2,
                        "accepted_point_count": 5,
                        "max_coordinate_gap": 0.04,
                        "max_interpolation_error": 0.1,
                        "exact_hessian_verified": True,
                        "postsolve_verified": True,
                        "blockers": ["required_anchor_incomplete"],
                    },
                    {
                        "series": "dew_line",
                        "route": "dew_pressure",
                        "complete": True,
                        "required_anchor_count": 3,
                        "solved_required_anchor_count": 3,
                        "accepted_point_count": 5,
                        "max_coordinate_gap": 0.04,
                        "max_interpolation_error": 0.1,
                        "exact_hessian_verified": True,
                        "postsolve_verified": True,
                        "blockers": [],
                    },
                ],
            }
        ),
    )
    payload = _foundation_payload()
    payload["figures"] = [
        {
            "figure_id": "figure_02",
            "plot_family": "vle",
            "replication_status": "accepted",
            "counts_toward_completion": True,
            "acceptance_threshold": 8.0,
            checker.SECOND_ORDER_REQUIRED_FIELD: True,
            "source_identity_status": "resolved",
            "required_series": ["bubble_line", "dew_line"],
            "requires_branch_trace": True,
            "trace_requirements": {
                "max_coordinate_gap": 0.075,
                "max_interpolation_error": 0.35,
                "required_series": ["bubble_line", "dew_line"],
            },
            "artifacts": artifacts,
        }
    ]

    result = checker.evaluate_payload(payload, require_complete=True)

    assert result["complete"] is False
    assert "gross_2002_figure_02_trace_bubble_line_incomplete" in result["blockers"]
    assert "gross_2002_figure_02_trace_bubble_line_required_anchors_incomplete" in result["blockers"]


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
    assert payload["complete"] is True


def test_cli_require_complete_accepts_committed_manifest(capsys) -> None:
    exit_code = checker.main(["--json", "--require-complete"])

    payload = json.loads(capsys.readouterr().out)
    assert exit_code == 0
    assert payload["complete"] is True
    assert payload["accepted_figures"] == [f"figure_{number:02d}" for number in range(1, 11)]
    assert payload["blockers"] == []
