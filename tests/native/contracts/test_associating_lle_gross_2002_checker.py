from __future__ import annotations

import json
from pathlib import Path

from scripts.validation import check_associating_lle_gross_2002 as checker


REPO_ROOT = Path(__file__).resolve().parents[3]
CASE_DIR = (
    REPO_ROOT
    / "data"
    / "reference"
    / "equilibrium_benchmarks"
    / "associating_lle"
    / "gross_2002_methanol_cyclohexane"
)


def test_missing_gross_2002_fixture_reports_named_blockers(tmp_path: Path) -> None:
    payload = checker.evaluate_case_dir(
        tmp_path / "missing_gross_2002_fixture",
        require_source_data=True,
        require_route_closed=True,
    )

    assert payload["complete"] is False
    assert "source_data_missing" in payload["blockers"]
    assert "parameter_bundle_missing" in payload["blockers"]
    assert "thresholds_missing" in payload["blockers"]


def test_cli_json_missing_fixture_reports_named_blockers(tmp_path: Path, capsys) -> None:
    exit_code = checker.main(
        [
            "--case-dir",
            str(tmp_path / "missing_gross_2002_fixture"),
            "--json",
            "--require-source-data",
            "--require-route-closed",
        ]
    )

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert exit_code == 2
    assert "source_data_missing" in payload["blockers"]
    assert "parameter_bundle_missing" in payload["blockers"]
    assert "thresholds_missing" in payload["blockers"]


def test_gross_2002_fixture_reports_source_backed_closed_admission_complete() -> None:
    payload = checker.evaluate_case_dir(
        CASE_DIR,
        require_source_data=True,
        require_route_closed=True,
    )

    assert payload["complete"] is True
    assert payload["blockers"] == []
    assert payload["fixture"]["source_data"]["status"] == "source_backed"
    assert payload["fixture"]["source_data"]["paper_data_rows"] >= 6
    assert payload["fixture"]["parameter_bundle"]["status"] == "source_backed"
    assert payload["fixture"]["parameter_bundle"]["species"] == ["methanol", "cyclohexane"]
    assert payload["fixture"]["parameter_bundle"]["methanol_assoc_scheme"] == "2B"
    assert payload["fixture"]["parameter_bundle"]["cyclohexane_association_site_count"] == 0
    assert payload["fixture"]["binary_interaction"]["k_ij"] == 0.051
    assert payload["public_route_state"]["associating_lle"] == "closed_for_associating_inputs"
