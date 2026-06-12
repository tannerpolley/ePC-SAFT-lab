from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

import pytest

from analyses.package_validation.issue_0188_neutral_tp_flash.scripts import generate_data
from analyses.package_validation.issue_0188_neutral_tp_flash.scripts import render_figures


VERIFIED_STATUS = {
    "deterministic_screening": "verified_not_full_held",
    "continuous_tpd_minimization": "verified_converged",
    "held_stage_i_stability": "verified_from_converged_continuous_tpd",
    "held_stage_ii_dual_phase_discovery": "verified_dual_loop_replayable",
    "held_stage_iii_ipopt_refinement": "verified_current_route_refinement_consumed_stage_ii_replay",
}

RECEIPT = {
    "git_commit": "0123456789abcdef",
    "native_module_path": "C:/repo/build/epcsaft_equilibrium/_native_core.pyd",
    "build_refresh_command": "uv run --no-sync python scripts/dev/build_epcsaft.py --profile equilibrium --build-only --parallel 4",
    "checker_command": [
        "uv",
        "run",
        "--no-sync",
        "python",
        "scripts/validation/check_phase_discovery.py",
        "--json",
        "--include-route-refinement",
        "--require-complete",
    ],
}


def _phase_discovery_payload(*, receipt: dict[str, Any] | None) -> dict[str, Any]:
    payload = {
        "case_label": "Synthetic neutral binary phase-discovery case",
        "family_label": "PE-Neutral TP Flash",
        "complete": True,
        "requirement_status": VERIFIED_STATUS,
        "incomplete_requirements": [],
        "diagnostics": {},
    }
    if receipt is not None:
        payload["native_freshness_receipt"] = receipt
    return payload


def test_issue188_gate_rows_copy_native_receipt_fields(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        generate_data.check_phase_discovery,
        "evaluate_phase_discovery",
        lambda **_: _phase_discovery_payload(receipt=RECEIPT),
    )

    rows, summary = generate_data._run_held_gate_status()

    stage_ii = next(row for row in rows if row["gate"] == "held_stage_ii_dual_phase_discovery")
    stage_iii = next(row for row in rows if row["gate"] == "held_stage_iii_ipopt_refinement")
    for row in (stage_ii, stage_iii):
        assert row["native_git_commit"] == RECEIPT["git_commit"]
        assert row["native_module_path"] == RECEIPT["native_module_path"]
        assert row["native_build_refresh_command"] == RECEIPT["build_refresh_command"]
        assert row["native_checker_command"] == " ".join(RECEIPT["checker_command"])
    assert summary["native_freshness_receipt"] == RECEIPT


def test_issue188_gate_generation_rejects_verified_rows_without_receipt(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        generate_data.check_phase_discovery,
        "evaluate_phase_discovery",
        lambda **_: _phase_discovery_payload(receipt=None),
    )

    with pytest.raises(ValueError, match="native freshness"):
        generate_data._run_held_gate_status()


def test_held_gate_renderer_rejects_verified_stage_rows_without_receipts(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    results_root = tmp_path / "shared" / "results"
    results_root.mkdir(parents=True)
    rows = [
        {
            "order": "3",
            "gate": "held_stage_ii_dual_phase_discovery",
            "label": "HELD Stage II dual discovery",
            "status": "verified_dual_loop_replayable",
            "status_class": "verified",
            "accepted": "True",
        },
        {
            "order": "4",
            "gate": "held_stage_iii_ipopt_refinement",
            "label": "HELD Stage III Ipopt refinement",
            "status": "verified_current_route_refinement_consumed_stage_ii_replay",
            "status_class": "verified",
            "accepted": "True",
        },
    ]
    with (results_root / "held_1_0_gate_status.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    monkeypatch.setattr(render_figures, "SHARED_RESULTS", results_root)
    monkeypatch.setattr(render_figures, "FIGURES_ROOT", tmp_path / "figures")

    with pytest.raises(ValueError, match="native freshness"):
        render_figures.render_held_gate_status()
