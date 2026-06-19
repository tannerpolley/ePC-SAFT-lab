from __future__ import annotations

import json
from pathlib import Path

from scripts.validation import check_gross_2002_association_acceptance as checker


def _artifact_set(tmp_path: Path, figure_id: str) -> dict[str, str]:
    files = {}
    for suffix in ("source_csv", "model_csv", "plotted_csv", "summary_json", "png", "svg", "sidecar"):
        path = tmp_path / f"{figure_id}_{suffix}"
        path.write_text("artifact\n", encoding="utf-8")
        files[suffix] = str(path)
    return files


def test_missing_manifest_reports_campaign_blockers(tmp_path: Path) -> None:
    payload = checker.evaluate_campaign(
        manifest_path=tmp_path / "missing_manifest.json",
        require_complete=True,
        require_exact_association_hessian=True,
        require_fresh_native=True,
    )

    assert payload["complete"] is False
    assert "gross_2002_campaign_manifest_missing" in payload["blockers"]
    assert "gross_2002_figure_01_pure_association_mirror_missing" in payload["blockers"]
    assert "gross_2002_figure_10_source_data_missing" in payload["blockers"]
    assert "gross_2002_native_freshness_receipt_missing" in payload["blockers"]


def test_evaluate_payload_accepts_completed_campaign(tmp_path: Path) -> None:
    payload = {
        "figure_records": [
            {
                "figure_id": "figure_01",
                "role": "accepted_sanity_gate",
                "status": "accepted",
                "counts_toward_completion": True,
                "source_point_count": 3,
                "artifacts": _artifact_set(tmp_path, "figure_01"),
                "pure_association_sanity": {"status": "verified"},
            },
            {
                "figure_id": "figure_08",
                "role": "accepted_hard_gate",
                "status": "accepted",
                "counts_toward_completion": True,
                "source_point_count": 16,
                "artifacts": _artifact_set(tmp_path, "figure_08"),
                "exact_association_hessian": {
                    "status": "verified_exact",
                    "max_mass_action_residual": 1.0e-12,
                },
            },
            {
                "figure_id": "figure_10",
                "role": "accepted_hard_gate",
                "status": "accepted",
                "counts_toward_completion": True,
                "source_point_count": 8,
                "artifacts": _artifact_set(tmp_path, "figure_10"),
                "exact_association_hessian": {
                    "status": "verified_exact",
                    "max_mass_action_residual": 1.0e-12,
                },
                "cross_association_stress": {"status": "verified"},
            },
            *[
                {
                    "figure_id": figure_id,
                    "role": "source_requirement",
                    "status": "source_requirement_recorded",
                    "counts_toward_completion": False,
                    "source_requirements": ["retain source points before evidence can count"],
                }
                for figure_id in ("figure_02", "figure_03", "figure_04", "figure_05", "figure_06", "figure_07", "figure_09")
            ],
        ],
        "native_freshness_receipt": {
            "git_commit": "0123456789abcdef",
            "native_module_name": "epcsaft_equilibrium._native",
            "native_module_path": str(tmp_path / "_native.pyd"),
            "checker_command": [
                "uv",
                "run",
                "--no-sync",
                "python",
                "scripts/validation/check_gross_2002_association_acceptance.py",
            ],
            "build_refresh_command": "uv run --no-sync python scripts/dev/build_epcsaft.py --profile equilibrium --build-only --parallel 4",
        },
        "summary_artifacts": {
            "json": str(tmp_path / "gross_2002_association_acceptance_summary.json"),
            "csv": str(tmp_path / "gross_2002_association_acceptance_summary.csv"),
        },
    }
    for path in payload["summary_artifacts"].values():
        Path(path).write_text("summary\n", encoding="utf-8")

    result = checker.evaluate_payload(
        payload,
        require_complete=True,
        require_exact_association_hessian=True,
        require_fresh_native=True,
    )

    assert result["complete"] is True
    assert result["blockers"] == []
    assert result["accepted_figures"] == ["figure_01", "figure_08", "figure_10"]
    assert result["source_requirement_figures"] == [
        "figure_02",
        "figure_03",
        "figure_04",
        "figure_05",
        "figure_06",
        "figure_07",
        "figure_09",
    ]


def test_figure_two_source_requirement_does_not_count_as_accepted(tmp_path: Path) -> None:
    payload = {
        "figure_records": [
            {
                "figure_id": "figure_01",
                "role": "accepted_sanity_gate",
                "status": "accepted",
                "counts_toward_completion": True,
                "source_point_count": 3,
                "artifacts": _artifact_set(tmp_path, "figure_01"),
                "pure_association_sanity": {"status": "verified"},
            },
            {
                "figure_id": "figure_02",
                "role": "accepted_hard_gate",
                "status": "accepted",
                "counts_toward_completion": True,
                "source_point_count": 5,
                "artifacts": _artifact_set(tmp_path, "figure_02"),
            },
        ],
        "native_freshness_receipt": {},
        "summary_artifacts": {},
    }

    result = checker.evaluate_payload(payload, require_complete=True)

    assert result["complete"] is False
    assert "gross_2002_figure_02_source_identity_unresolved" in result["blockers"]


def test_cli_json_missing_manifest_reports_named_blockers(tmp_path: Path, capsys) -> None:
    exit_code = checker.main(
        [
            "--manifest",
            str(tmp_path / "missing_manifest.json"),
            "--json",
            "--require-complete",
            "--require-exact-association-hessian",
            "--require-fresh-native",
        ]
    )

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert exit_code == 2
    assert "gross_2002_campaign_manifest_missing" in payload["blockers"]
    assert "gross_2002_native_freshness_receipt_missing" in payload["blockers"]
