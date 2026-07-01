from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
CHECKER_PATH = REPO_ROOT / "scripts" / "validation" / "check_ce_robustness_followup.py"

EXPECTED_FINDINGS = {
    "eos_failure_gate_taxonomy",
    "caller_seed_rejection_evidence",
    "adaptive_eos_activity_continuation",
    "assistance_summary_diagnostics",
    "retained_artifact_review_digest",
    "followup_confidence_gate",
    "eos_nonideality_diagnostic_matrix",
}

pytestmark = pytest.mark.native_contract


def _checker_module():
    spec = importlib.util.spec_from_file_location("check_ce_robustness_followup", CHECKER_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_ce_robustness_followup_gate_reports_complete_evidence() -> None:
    checker = _checker_module()

    report = checker.evaluate_ce_robustness_followup_gate()

    assert report["status"] == "complete"
    assert report["blockers"] == []
    assert set(report["findings"]) == EXPECTED_FINDINGS
    assert all(finding["status"] == "complete" for finding in report["findings"].values())

    taxonomy = report["findings"]["eos_failure_gate_taxonomy"]
    assert taxonomy["exact_failure_classes"]["eos_stationarity"] == "stationarity_failure"
    assert taxonomy["exact_failure_classes"]["eos_balance"] == "balance_failure"
    assert taxonomy["exact_failure_classes"]["eos_ipopt"] == "ipopt_failure"

    seed = report["findings"]["caller_seed_rejection_evidence"]
    assert seed["fields"] == [
        "caller_seed_rejection_source",
        "caller_seed_rejection_reason",
        "caller_seed_exception_observed",
        "caller_seed_exception_message",
    ]

    continuation = report["findings"]["adaptive_eos_activity_continuation"]
    assert continuation["policy"]["mode"] == "adaptive_bisection"
    assert continuation["accepted_activity_steps"] == [0.0, 0.5, 1.0]
    assert continuation["rejected_activity_steps"] == []

    digest = report["findings"]["retained_artifact_review_digest"]["digest"]
    assert digest["status"] == "complete"
    assert digest["artifact_count"] >= 2

    matrix = report["findings"]["eos_nonideality_diagnostic_matrix"]
    assert set(matrix["modes"]) == {"eos_x_phi", "eos_x_gamma"}
    assert matrix["capability_boundary"] == "synthetic_eos_activity_diagnostics_not_literature_mea_nonideality"
    assert matrix["modes"]["eos_x_phi"]["derivative_backend"]
    assert matrix["modes"]["eos_x_gamma"]["derivative_backend"]


def test_ce_robustness_followup_gate_cli_require_complete() -> None:
    completed = subprocess.run(
        [sys.executable, str(CHECKER_PATH), "--json", "--require-complete"],
        check=True,
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )

    report = json.loads(completed.stdout)
    assert report["status"] == "complete"
    assert report["blockers"] == []
