from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from _paths import ANALYSIS_DIR, REPO_ROOT

SCRIPT_DIR = Path(__file__).resolve().parent
INPUT_DIR = ANALYSIS_DIR / "shared" / "source"
PROCESSED_DIR = ANALYSIS_DIR / "shared" / "results" / "processed"
REACTION_RESULTS_DIR = ANALYSIS_DIR / "shared" / "results" / "reaction_equilibrium"
SUMMARY_JSON = REACTION_RESULTS_DIR / "summary.json"

SCRIPT_SEQUENCE = (
    "rezaee_2025_target_summary.py",
    "rezaee_section32_basis_inference.py",
)
EQUILIBRIUM_SOURCE_CSV = INPUT_DIR / "rezaee_2025_extraction_equilibrium_mole_fractions.csv"
BASIS_SUMMARY_JSON = REACTION_RESULTS_DIR / "rezaee_2026_section32_basis_inference_summary.json"
EXPECTED_SOURCE_ROW_COUNT = 26


def _rel(path: Path) -> str:
    return path.relative_to(REPO_ROOT).as_posix()


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _csv_row_count(path: Path) -> int:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return sum(1 for _ in csv.DictReader(handle))


def _run_script(script_name: str) -> dict[str, Any]:
    command = [sys.executable, str(SCRIPT_DIR / script_name)]
    print("Running:", " ".join(command), flush=True)
    completed = subprocess.run(
        command,
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.stdout:
        print(completed.stdout, end="" if completed.stdout.endswith("\n") else "\n", flush=True)
    if completed.stderr:
        print(
            completed.stderr,
            end="" if completed.stderr.endswith("\n") else "\n",
            file=sys.stderr,
            flush=True,
        )
    if completed.returncode != 0:
        raise subprocess.CalledProcessError(
            completed.returncode,
            command,
            completed.stdout,
            completed.stderr,
        )
    return {"script": script_name, "returncode": completed.returncode}


def _build_summary(command_results: list[dict[str, Any]]) -> dict[str, Any]:
    source_row_count = _csv_row_count(EQUILIBRIUM_SOURCE_CSV)
    basis = _read_json(BASIS_SUMMARY_JSON)
    basis_row_count = int(basis["row_count"])
    source_evidence_complete = (
        source_row_count == EXPECTED_SOURCE_ROW_COUNT
        and basis_row_count == EXPECTED_SOURCE_ROW_COUNT
    )
    source_files = sorted(_rel(path) for path in INPUT_DIR.iterdir() if path.is_file())
    retained_outputs = [
        PROCESSED_DIR / "rezaee_2025_extraction_target_summary.csv",
        PROCESSED_DIR / "rezaee_2025_extraction_equilibrium_summary.csv",
        PROCESSED_DIR / "rezaee_2026_section32_basis_inference_rows.csv",
        BASIS_SUMMARY_JSON,
        REACTION_RESULTS_DIR / "rezaee_2026_section32_basis_inference.md",
    ]
    return {
        "schema_version": 2,
        "lane_id": "rezaee_2025_2026_source_evidence",
        "status": (
            "internal_source_evidence_only"
            if source_evidence_complete
            else "source_evidence_failed"
        ),
        "source_evidence_complete": source_evidence_complete,
        "model_validation_complete": False,
        "route_scope": "source_and_basis_diagnostics",
        "public_route_admitted": False,
        "phase_models_supported": False,
        "row_count": source_row_count,
        "source_files": source_files,
        "source_text_mismatch": {
            "available_si_equilibrium_rows": source_row_count,
            "paper_text_equilibrium_data_points": 36,
            "conclusion": (
                "The retained supporting-information table contains 26 rows; no 36-row "
                "source table is present."
            ),
        },
        "source_evidence_checks": {
            "expected_equilibrium_rows": EXPECTED_SOURCE_ROW_COUNT,
            "retained_equilibrium_rows": source_row_count,
            "basis_inference_rows": basis_row_count,
            "basis_inference_status": basis["status"],
        },
        "retained_outputs": [_rel(path) for path in retained_outputs],
        "commands": command_results,
        "blockers": [
            {
                "kind": "closed_public_surface",
                "reason": (
                    "The current package exposes no reactive-electrolyte equilibrium route."
                ),
            },
            {
                "kind": "model_validation_absent",
                "reason": (
                    "The removed provider-era equilibrium and regression APIs cannot supply "
                    "current package-model predictions."
                ),
            },
        ],
        "conclusion": (
            "The literature source rows and basis diagnostics are retained. No current "
            "package-model validation or public reactive-electrolyte capability is claimed."
        ),
    }


def main() -> int:
    command_results = [_run_script(script_name) for script_name in SCRIPT_SEQUENCE]
    summary = _build_summary(command_results)
    SUMMARY_JSON.parent.mkdir(parents=True, exist_ok=True)
    SUMMARY_JSON.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0 if summary["source_evidence_complete"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
