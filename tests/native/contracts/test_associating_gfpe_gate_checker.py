from __future__ import annotations

import json
from pathlib import Path

from scripts.validation import check_associating_gfpe_gate as checker

REPO_ROOT = Path(__file__).resolve().parents[3]
CASE_DIR = (
    REPO_ROOT
    / "data"
    / "reference"
    / "equilibrium_benchmarks"
    / "associating_lle"
    / "methanol_cyclohexane"
)


def test_missing_gross_2002_fixture_reports_source_blockers(tmp_path: Path) -> None:
    payload = checker.evaluate_case_dir(
        tmp_path / "missing_gross_2002_fixture",
        require_source_data=True,
        require_exact_association_hessian=True,
    )

    assert payload["complete"] is False
    assert "source_data_missing" in payload["blockers"]
    assert "exact_association_hessian_missing" in payload["blockers"]


def test_associating_gfpe_gate_reports_internal_evidence_and_closed_route() -> None:
    payload = checker.evaluate_case_dir(
        CASE_DIR,
        require_source_data=True,
        require_exact_association_hessian=True,
        require_internal_evidence=True,
        require_route_closed=True,
    )

    assert payload["complete"] is True
    assert payload["blockers"] == []
    assert payload["global_phase_set_certified"] is False
    assert payload["production_route_admitted"] is False
    assert payload["internal_diagnostic"]["association_hessian"]["status"] == "verified_exact"

    capability = payload["capability_evidence"]
    assert capability["status"] == "internal_diagnostic_evidence_verified"
    assert capability["family_state"] == {
        "production_exposed": False,
        "public_routes": [],
        "proof_routes": [],
    }
    assert capability["evidence_id"] == checker.INTERNAL_EVIDENCE_ID
    evidence = capability["evidence"]
    assert evidence["classification"] == "internal_validation_evidence"
    assert "public_admission_state" not in evidence
    assert "public_route" not in evidence
    assert evidence["backend"] == "cppad_implicit_association"
    assert evidence["source_configuration"] == checker.SOURCE_CONFIGURATION
    assert evidence["assoc_scheme"] == "2B"
    assert evidence["k_ij"] == 0.051


def test_cli_json_missing_fixture_reports_named_blockers(tmp_path: Path, capsys) -> None:
    exit_code = checker.main(
        [
            "--case-dir",
            str(tmp_path / "missing_gross_2002_fixture"),
            "--json",
            "--require-source-data",
            "--require-exact-association-hessian",
            "--require-internal-evidence",
            "--require-route-closed",
            "--require-complete",
        ]
    )

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert exit_code == 2
    assert "source_data_missing" in payload["blockers"]
    assert "exact_association_hessian_missing" in payload["blockers"]
