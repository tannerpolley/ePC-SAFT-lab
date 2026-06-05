from __future__ import annotations

import csv

from analyses.package_validation.explicit_association_toybox.scripts.picard_stress_evidence import (
    generate_picard_stress_report,
)


def test_picard_stress_report_writes_csv_and_decision_memo(tmp_path) -> None:
    output = tmp_path / "picard_stress_evidence.csv"
    memo = tmp_path / "picard_stress_rescue_or_retire_decision.md"

    generate_picard_stress_report(output, memo, repeat_count=1, max_cases=2, max_policies=2)

    rows = list(csv.DictReader(output.open(newline="")))
    assert rows
    assert rows[0]["stress_decision"] in {
        "retire_picard",
        "keep_m8_only",
        "recommend_m3_provider_admission_issue",
    }
    assert memo.exists()
    assert "Decision" in memo.read_text(encoding="utf-8")
