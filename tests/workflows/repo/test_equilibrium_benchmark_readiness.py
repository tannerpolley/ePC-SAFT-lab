from __future__ import annotations

import csv
import json
from pathlib import Path
import shutil
import subprocess
import sys

import pytest

from scripts.validation import check_stage9_phase_discovery_evidence as stage9_checker

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


def _synthetic_stage9_discovery() -> dict[str, object]:
    return {
        "phase_discovery_backend": "deterministic_tpd_candidate_screening",
        "stage9_phase_discovery_steps": [
            "deterministic_screening",
            "continuous_tpd",
            "held_stage_i",
            "held_stage_ii",
            "held_stage_iii",
        ],
        "deterministic_screening_status": "completed",
        "deterministic_screening_is_full_held": False,
        "deterministic_candidate_count": 4,
        "continuous_tpd_status": "converged",
        "continuous_tpd_backend": "continuous_coordinate_search",
        "continuous_tpd_start_count": 2,
        "continuous_tpd_solve_count": 2,
        "continuous_tpd_converged_count": 2,
        "continuous_tpd_iteration_count_max": 8,
        "continuous_tpd_min": -2.0,
        "held_stage_i_status": "negative_tpd_candidate_found",
        "held_stage_i_start_count": 2,
        "held_stage_ii_status": "candidate_bound_gap_open",
        "held_stage_ii_major_iterations": 1,
        "held_stage_ii_candidate_count": 2,
        "held_stage_ii_lower_bound": -2.0,
        "held_stage_ii_upper_bound": -0.5,
        "held_stage_ii_bound_gap": 1.5,
        "candidates": [
            {"tpd_backend": "continuous_coordinate_search", "tpd_status": "converged"},
        ],
    }


def test_stage9_evidence_route_refinement_is_explicit(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[bool] = []

    monkeypatch.setattr(stage9_checker, "_nonideal_lle_binary_mixture", lambda: object())
    monkeypatch.setattr(stage9_checker, "_stage9_discovery", lambda mix: _synthetic_stage9_discovery())
    monkeypatch.setattr(
        stage9_checker,
        "_stage9_route_result",
        lambda mix, **kwargs: calls.append(bool(kwargs)) or {
            "solver_status": "success",
            "application_status": "solve_succeeded",
            "status": "production_accepted",
            "iteration_count": 6,
            "iteration_history_size": 6,
            "iteration_history_limit": 8,
            "seed_attempts": [],
            "accepted": True,
            "postsolve": {
                "accepted": True,
                "held_stage_iii_status": "ipopt_refinement_completed_current_route",
                "held_stage_iii_refined_phase_count": 2,
            },
        },
    )

    cheap_payload = stage9_checker.evaluate_stage9_evidence()
    full_payload = stage9_checker.evaluate_stage9_evidence(include_route_refinement=True)

    assert calls == [True]
    assert cheap_payload["diagnostics"]["route_refinement_requested"] is False
    assert (
        cheap_payload["evidence_status"]["held_stage_iii_ipopt_refinement"]
        == "not_requested_stage_ii_incomplete"
    )
    assert full_payload["diagnostics"]["route_refinement_requested"] is True
    assert (
        full_payload["evidence_status"]["held_stage_iii_ipopt_refinement"]
        == "verified_current_route_refinement_pending_stage_ii_candidates"
    )
    assert full_payload["diagnostics"]["route_solver_status"] == "success"
    assert full_payload["diagnostics"]["route_iteration_count"] == 6
    assert full_payload["diagnostics"]["route_iteration_history_size"] == 6


def test_stage9_evidence_route_refinement_requires_ipopt_convergence(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(stage9_checker, "_nonideal_lle_binary_mixture", lambda: object())
    monkeypatch.setattr(stage9_checker, "_stage9_discovery", lambda mix: _synthetic_stage9_discovery())
    monkeypatch.setattr(
        stage9_checker,
        "_stage9_route_result",
        lambda mix, **kwargs: {
            "solver_status": "tiny_step_detected",
            "application_status": "search_direction_too_small",
            "status": "production_accepted",
            "iteration_count": 59,
            "iteration_history_size": 50,
            "iteration_history_limit": 50,
            "seed_attempts": [],
            "postsolve": {
                "accepted": True,
                "held_stage_iii_status": "ipopt_refinement_completed_current_route",
                "held_stage_iii_refined_phase_count": 2,
            },
        },
    )

    payload = stage9_checker.evaluate_stage9_evidence(include_route_refinement=True)

    assert (
        payload["evidence_status"]["held_stage_iii_ipopt_refinement"]
        == "incomplete_ipopt_solver_status_tiny_step_detected"
    )
    assert "held_stage_iii_ipopt_refinement" in payload["incomplete_requirements"]
    assert payload["diagnostics"]["route_status"] == "production_accepted"
    assert payload["diagnostics"]["route_solver_status"] == "tiny_step_detected"


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
    assert payload["evidence_status"]["held_stage_ii_dual_phase_discovery"] == "incomplete_candidate_bound_gap_open"
    assert (
        payload["evidence_status"]["held_stage_iii_ipopt_refinement"]
        == "not_requested_stage_ii_incomplete"
    )
    assert payload["incomplete_requirements"] == [
        "held_stage_ii_dual_phase_discovery",
        "held_stage_iii_ipopt_refinement",
    ]
    assert payload["diagnostics"]["route_refinement_requested"] is False
    assert payload["diagnostics"]["held_stage_ii_status"] == "candidate_bound_gap_open"
    assert payload["diagnostics"]["held_stage_ii_major_iterations"] > 0
    assert payload["diagnostics"]["held_stage_ii_bound_gap"] > 0.0


def test_stage9_evidence_checker_debug_mode_exposes_trace_without_breaking_json() -> None:
    result = _run_stage9_checker("--json", "--debug")

    assert result.returncode == 0, result.stdout + result.stderr
    payload = _load_stdout_json(result)

    assert payload["diagnostics"]["equilibrium_debug_enabled"] is True
    assert payload["diagnostics"]["route_refinement_requested"] is False
    assert payload["diagnostics"]["ipopt_print_level"] == 5
    assert "[EPCSAFT_TPD_DEBUG]" in result.stderr


def test_pereira_readiness_checker_consumes_stage9_evidence_without_faking_completion(
    tmp_path: Path,
) -> None:
    stage9_path = tmp_path / "stage9_evidence.json"
    stage9_path.write_text(
        json.dumps(
            {
                "complete": False,
                "evidence_status": {
                    "deterministic_screening": "verified_not_full_held",
                    "continuous_tpd_minimization": "verified_converged",
                    "held_stage_i_stability": "verified_from_converged_continuous_tpd",
                    "held_stage_ii_dual_phase_discovery": "incomplete_candidate_bound_gap_open",
                    "held_stage_iii_ipopt_refinement": "incomplete_ipopt_solver_status_tiny_step_detected",
                },
                "incomplete_requirements": [
                    "held_stage_ii_dual_phase_discovery",
                    "held_stage_iii_ipopt_refinement",
                ],
            }
        ),
        encoding="utf-8",
    )

    result = _run_checker("--json", "--stage9-evidence-json", str(stage9_path))

    assert result.returncode == 0, result.stdout + result.stderr
    payload = _load_stdout_json(result)

    assert payload["stage9_evidence_path_verified"] is False
    assert payload["stage9_evidence"]["continuous_tpd_minimization"] == "verified_converged"
    assert payload["stage9_evidence"]["held_stage_ii_dual_phase_discovery"] == "incomplete_candidate_bound_gap_open"
    assert payload["stage9_incomplete_requirements"] == [
        "held_stage_ii_dual_phase_discovery",
        "held_stage_iii_ipopt_refinement",
    ]
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
