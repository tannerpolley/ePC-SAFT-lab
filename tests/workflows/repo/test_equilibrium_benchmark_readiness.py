from __future__ import annotations

import csv
import json
from pathlib import Path
import shutil
import subprocess
import sys

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
CHECKER = REPO_ROOT / "scripts" / "validation" / "check_equilibrium_benchmark_readiness.py"
STAGE9_CHECKER = REPO_ROOT / "scripts" / "validation" / "check_stage9_phase_discovery_evidence.py"
PEREIRA_CASE_DIR = (
    REPO_ROOT / "data" / "reference" / "equilibrium_benchmarks" / "neutral_tp_flash" / "pereira_2012"
)


def _run_checker(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(CHECKER), *args],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )


def _run_stage9_checker(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(STAGE9_CHECKER), *args],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )


def _load_stdout_json(result: subprocess.CompletedProcess[str]) -> dict[str, object]:
    assert result.stdout, result.stderr
    return json.loads(result.stdout)


def test_pereira_readiness_checker_reports_nonexecutable_stage10_json() -> None:
    result = _run_checker("--json")

    assert result.returncode == 0, result.stdout + result.stderr
    payload = _load_stdout_json(result)

    assert payload["case_label"] == "Pereira 2012 System III"
    assert payload["family_label"] == "PE-Neutral TP Flash"
    assert payload["source_model_family"] == "SAFT-VR"
    assert payload["proof_status"] == "blocked"
    assert payload["executable"] is False
    assert payload["stage9_evidence_path_required"] is True
    assert {
        "model_family_mismatch",
        "saft_vr_runtime_absent",
        "source_confirmed_feed_correction_required",
        "stage9_evidence_path_not_verified",
    } <= set(payload["blockers"])
    assert payload["stage9_evidence"]["held_stage_ii_dual_phase_discovery"] == "required_not_verified"
    assert payload["stored_readiness_consistent"] is True

    cases = {case["case_key"]: case for case in payload["cases"]}
    first = cases["system_iii_22325_09mpa"]
    assert first["reported_feed_status"] == "normalized"
    assert first["material_balance_status"] == "feasible_from_reported_feed"
    assert first["proof_eligible"] is False
    assert first["vapor_fraction"] == pytest.approx(0.9270741305919203)
    assert first["liquid_fraction"] == pytest.approx(0.07292586940807967)

    second = cases["system_iii_29315_61mpa"]
    assert second["reported_feed_status"] == "not_normalized"
    assert second["material_balance_status"] == "blocked_by_published_feed"
    assert "published_second_feed_composition_not_normalized" in second["blockers"]


def test_pereira_readiness_checker_fails_closed_when_executable_required() -> None:
    result = _run_checker("--json", "--require-executable")

    assert result.returncode == 2
    payload = _load_stdout_json(result)
    assert payload["executable"] is False
    assert payload["proof_status"] == "blocked"
    assert "Pereira 2012 System III is not an executable Stage 10 proof fixture" in result.stderr


def test_pereira_readiness_checker_recomputes_material_balance_and_rejects_stale_csv(
    tmp_path: Path,
) -> None:
    case_dir = tmp_path / "pereira_2012"
    shutil.copytree(PEREIRA_CASE_DIR, case_dir)

    readiness_path = case_dir / "material_balance_readiness.csv"
    rows = list(csv.DictReader(readiness_path.read_text(encoding="utf-8").splitlines()))
    rows[0]["vapor_fraction"] = "0.1"
    with readiness_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    result = _run_checker("--case-dir", str(case_dir), "--json")

    assert result.returncode == 1
    payload = _load_stdout_json(result)
    assert payload["stored_readiness_consistent"] is False
    assert "stored_material_balance_readiness_mismatch" in payload["blockers"]
    assert payload["stored_readiness_mismatches"][0]["case_key"] == "system_iii_22325_09mpa"


def test_stage9_evidence_checker_reports_current_ladder_without_promoting_stage_ii() -> None:
    result = _run_stage9_checker("--json")

    assert result.returncode == 0, result.stdout + result.stderr
    payload = _load_stdout_json(result)

    assert payload["family_label"] == "PE-Neutral TP Flash"
    assert payload["complete"] is False
    assert payload["evidence_status"]["deterministic_screening"] == "verified_not_full_held"
    assert payload["evidence_status"]["continuous_tpd_minimization"] == "verified_converged"
    assert payload["evidence_status"]["held_stage_i_stability"] == "verified_from_converged_continuous_tpd"
    assert payload["evidence_status"]["held_stage_ii_dual_phase_discovery"] == "pending_dual_cutting_plane_loop"
    assert (
        payload["evidence_status"]["held_stage_iii_ipopt_refinement"]
        == "verified_current_route_refinement_pending_stage_ii_candidates"
    )
    assert payload["incomplete_requirements"] == ["held_stage_ii_dual_phase_discovery"]


def test_stage9_evidence_checker_debug_mode_exposes_trace_without_breaking_json() -> None:
    result = _run_stage9_checker("--json", "--debug")

    assert result.returncode == 0, result.stdout + result.stderr
    payload = _load_stdout_json(result)

    assert payload["diagnostics"]["equilibrium_debug_enabled"] is True
    assert payload["diagnostics"]["ipopt_print_level"] == 5
    assert "[EPCSAFT_TPD_DEBUG]" in result.stderr


def test_pereira_readiness_checker_consumes_stage9_evidence_without_faking_completion(
    tmp_path: Path,
) -> None:
    stage9_result = _run_stage9_checker("--json")
    assert stage9_result.returncode == 0, stage9_result.stdout + stage9_result.stderr
    stage9_path = tmp_path / "stage9_evidence.json"
    stage9_path.write_text(stage9_result.stdout, encoding="utf-8")

    result = _run_checker("--json", "--stage9-evidence-json", str(stage9_path))

    assert result.returncode == 0, result.stdout + result.stderr
    payload = _load_stdout_json(result)

    assert payload["stage9_evidence_path_verified"] is False
    assert payload["stage9_evidence"]["continuous_tpd_minimization"] == "verified_converged"
    assert payload["stage9_evidence"]["held_stage_ii_dual_phase_discovery"] == "pending_dual_cutting_plane_loop"
    assert payload["stage9_incomplete_requirements"] == ["held_stage_ii_dual_phase_discovery"]
    assert "stage9_evidence_path_not_verified" in payload["blockers"]


def test_pereira_readiness_checker_removes_stage9_blocker_only_for_complete_stage9_evidence(
    tmp_path: Path,
) -> None:
    stage9_path = tmp_path / "complete_stage9_evidence.json"
    stage9_path.write_text(
        json.dumps(
            {
                "complete": True,
                "evidence_status": {
                    "deterministic_screening": "verified",
                    "continuous_tpd_minimization": "verified",
                    "held_stage_i_stability": "verified",
                    "held_stage_ii_dual_phase_discovery": "verified",
                    "held_stage_iii_ipopt_refinement": "verified",
                },
            }
        ),
        encoding="utf-8",
    )

    result = _run_checker("--json", "--stage9-evidence-json", str(stage9_path))

    assert result.returncode == 0, result.stdout + result.stderr
    payload = _load_stdout_json(result)

    assert payload["stage9_evidence_path_verified"] is True
    assert "stage9_evidence_path_not_verified" not in payload["blockers"]
    assert payload["executable"] is False
    assert {"model_family_mismatch", "saft_vr_runtime_absent"} <= set(payload["blockers"])
