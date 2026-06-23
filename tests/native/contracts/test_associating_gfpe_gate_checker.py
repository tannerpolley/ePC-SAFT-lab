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


def test_associating_gfpe_gate_reports_public_narrow_admission_complete() -> None:
    payload = checker.evaluate_case_dir(
        CASE_DIR,
        require_source_data=True,
        require_public_admission=True,
        require_exact_association_hessian=True,
        require_capability_evidence=True,
        require_electrolyte_closed=True,
    )

    assert payload["complete"] is True
    assert payload["blockers"] == []
    assert payload["prerequisite_proof"]["association_hessian"]["status"] == "verified_exact"

    public = payload["public_admission"]
    assert public["status"] == "public_route_admitted"
    assert public["public_route"] == "lle"
    assert public["selector_route"] == "neutral_lle"
    assert public["activation_key"] == "neutral_lle"
    assert public["hessian_approximation"] == "exact"
    assert public["exact_hessian_available"] is True
    assert public["postsolve_accepted"] is True
    assert public["phase_distance"] > 0.5

    rejected_cases = {
        case["case_key"]: case["status"]
        for case in payload["unsupported_route_rejections"]["cases"]
    }
    assert rejected_cases == {
        "missing_source_proof": "rejected",
        "altered_binary_interaction": "rejected",
        "ionic_associating_lle": "rejected",
        "associating_tp_flash": "rejected",
        "associating_generalized_phase_set": "rejected",
        "electrolyte_route_key": "rejected",
        "reactive_route_key": "rejected",
    }

    capability = payload["capability_evidence"]
    assert capability["status"] == "capability_evidence_verified"
    assert checker.PUBLIC_PROOF_ROUTE in capability["neutral_lle_proof_routes"]
    proof_row = capability["proof_row"]
    assert proof_row["classification"] == "production_supported"
    assert proof_row["public_admission_state"] == "public_route_open"
    assert proof_row["backend"] == "cppad_implicit_association"
    assert proof_row["source_configuration"] == checker.SOURCE_CONFIGURATION
    assert proof_row["assoc_scheme"] == "2B"
    assert proof_row["k_ij"] == 0.051
    assert "electrolyte_lle" not in capability["public_routes"]
    assert "reactive_lle" not in capability["public_routes"]


def test_cli_json_missing_fixture_reports_named_blockers(tmp_path: Path, capsys) -> None:
    exit_code = checker.main(
        [
            "--case-dir",
            str(tmp_path / "missing_gross_2002_fixture"),
            "--json",
            "--require-source-data",
            "--require-exact-association-hessian",
            "--require-complete",
        ]
    )

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert exit_code == 2
    assert "source_data_missing" in payload["blockers"]
    assert "exact_association_hessian_missing" in payload["blockers"]
