from __future__ import annotations

import csv
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from scripts.validation import check_stage9_phase_discovery_evidence as phase_discovery_checker

REPO_ROOT = Path(__file__).resolve().parents[3]
CHECKER = REPO_ROOT / "scripts" / "validation" / "check_equilibrium_benchmark_readiness.py"
PHASE_DISCOVERY_CHECKER = REPO_ROOT / "scripts" / "validation" / "check_stage9_phase_discovery_evidence.py"
NEUTRAL_FLASH_CHECKER = REPO_ROOT / "scripts" / "validation" / "check_stage10_neutral_tp_flash_proof.py"
PEREIRA_CASE_DIR = (
    REPO_ROOT / "data" / "reference" / "equilibrium_benchmarks" / "neutral_tp_flash" / "pereira_2012"
)
HYDROCARBON_CASE_DIR = (
    REPO_ROOT
    / "data"
    / "reference"
    / "equilibrium_benchmarks"
    / "neutral_tp_flash"
    / "hydrocarbon_workbook_flash"
)


def _run_checker(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(CHECKER), *args],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )


def _run_phase_discovery_checker(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(PHASE_DISCOVERY_CHECKER), *args],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )


def _run_neutral_flash_checker(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(NEUTRAL_FLASH_CHECKER), *args],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )


def _load_stdout_json(result: subprocess.CompletedProcess[str]) -> dict[str, object]:
    assert result.stdout, result.stderr
    return json.loads(result.stdout)


def _write_minimal_neutral_flash_fixture(case_dir: Path) -> None:
    case_dir.mkdir(parents=True)
    (case_dir / "metadata.json").write_text(
        json.dumps(
            {
                "name": "minimal_pc_saft_binary",
                "case_label": "Minimal PC-SAFT binary TP flash",
                "family_label": "PE-Neutral TP Flash",
                "source_model_family": "PC-SAFT",
                "runtime_model_support": "available_in_epcsaft",
                "proof_readiness": {
                    "stage9_evidence_path_required": True,
                    "source_confirmed_feed_correction_required": False,
                },
                "pure_component_parameters": {
                    "source": "test fixture source table",
                    "families": ["m", "sigma", "epsilon"],
                },
                "binary_interactions": {
                    "source": "test fixture source table",
                    "k_ij": [[0.0, 0.01], [0.01, 0.0]],
                },
                "source_paths": {"paper_markdown": "docs/source.md"},
                "acceptance_tolerances": {
                    "composition_abs": 1.0e-6,
                    "phase_fraction_abs": 1.0e-6,
                },
            }
        ),
        encoding="utf-8",
    )
    (case_dir / "phase_splits.csv").write_text(
        "\n".join(
            [
                "case_key,source_table,state,phase,temperature_K,pressure_MPa,component_1,component_2,x1,x2,composition_sum,eta,molar_volume_m3_per_mol,source_status",
                "binary_300k_1mpa,Table 1,VLE,feed,300.0,1.0,A,B,0.5,0.5,1.0,,,reported",
                "binary_300k_1mpa,Table 1,VLE,vapor,300.0,1.0,A,B,0.2,0.8,1.0,0.01,1.0e-3,reported",
                "binary_300k_1mpa,Table 1,VLE,liquid,300.0,1.0,A,B,0.8,0.2,1.0,0.20,1.0e-4,reported",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (case_dir / "material_balance_readiness.csv").write_text(
        "\n".join(
            [
                "case_key,reported_feed_status,material_balance_status,vapor_fraction,liquid_fraction,max_abs_material_balance_residual,material_balance_eligible,proof_eligible,blockers",
                "binary_300k_1mpa,normalized,feasible_from_reported_feed,0.5,0.5,0.0,true,true,",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def _synthetic_phase_discovery() -> dict[str, object]:
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


def _write_complete_phase_discovery_payload(path: Path) -> None:
    path.write_text(
        json.dumps(
            {
                "complete": True,
                "evidence_status": {
                    "deterministic_screening": "verified_not_full_held",
                    "continuous_tpd_minimization": "verified_converged",
                    "held_stage_i_stability": "verified_from_converged_continuous_tpd",
                    "held_stage_ii_dual_phase_discovery": "verified_candidate_bound_gap_closed",
                    "held_stage_iii_ipopt_refinement": "verified_current_route_refinement_converged",
                },
            }
        ),
        encoding="utf-8",
    )


def test_route_refinement_requires_explicit_request(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[bool] = []

    monkeypatch.setattr(phase_discovery_checker, "_nonideal_lle_binary_mixture", lambda: object())
    monkeypatch.setattr(phase_discovery_checker, "_phase_discovery_payload", lambda mix: _synthetic_phase_discovery())
    monkeypatch.setattr(
        phase_discovery_checker,
        "_route_refinement_result",
        lambda mix, **kwargs: calls.append(bool(kwargs)) or {
            "solver_status": "success",
            "application_status": "solve_succeeded",
            "status": "production_accepted",
            "option_profile": "held_refinement",
            "scaled_acceptance_passed": True,
            "constraint_violation_tolerance": 1.0e-7,
            "scaled_constraint_violation_inf_norm": 5.0e-8,
            "iteration_count": 6,
            "iteration_history_size": 6,
            "iteration_history_limit": 8,
            "iteration_history": [
                {
                    "iteration": 6,
                    "objective": 3.0,
                    "primal_infeasibility": 1.0e-9,
                    "dual_infeasibility": 2.0e-9,
                    "barrier_parameter": 1.0e-8,
                    "step_size_primal": 1.0,
                    "step_trial_count": 1,
                }
            ],
            "seed_attempts": [],
            "accepted": True,
            "postsolve": {
                "accepted": True,
                "held_stage_iii_status": "ipopt_refinement_completed_current_route",
                "held_stage_iii_refined_phase_count": 2,
            },
        },
    )

    cheap_payload = phase_discovery_checker.evaluate_phase_discovery()
    full_payload = phase_discovery_checker.evaluate_phase_discovery(include_route_refinement=True)

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
    assert full_payload["diagnostics"]["route_option_profile"] == "held_refinement"
    assert full_payload["diagnostics"]["route_scaled_acceptance_passed"] is True
    assert full_payload["diagnostics"]["route_iteration_count"] == 6
    assert full_payload["diagnostics"]["route_iteration_history_size"] == 6
    assert full_payload["diagnostics"]["route_iteration_history"] == [
        {
            "iteration": 6,
            "objective": 3.0,
            "primal_infeasibility": 1.0e-9,
            "dual_infeasibility": 2.0e-9,
            "barrier_parameter": 1.0e-8,
            "step_size_primal": 1.0,
            "step_trial_count": 1,
        }
    ]


def test_route_refinement_requires_ipopt_convergence(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(phase_discovery_checker, "_nonideal_lle_binary_mixture", lambda: object())
    monkeypatch.setattr(phase_discovery_checker, "_phase_discovery_payload", lambda mix: _synthetic_phase_discovery())
    monkeypatch.setattr(
        phase_discovery_checker,
        "_route_refinement_result",
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

    payload = phase_discovery_checker.evaluate_phase_discovery(include_route_refinement=True)

    assert (
        payload["evidence_status"]["held_stage_iii_ipopt_refinement"]
        == "incomplete_ipopt_solver_status_tiny_step_detected"
    )
    assert "held_stage_iii_ipopt_refinement" in payload["incomplete_requirements"]
    assert payload["diagnostics"]["route_status"] == "production_accepted"
    assert payload["diagnostics"]["route_solver_status"] == "tiny_step_detected"


def test_route_refinement_rejects_acceptable_point_status(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(phase_discovery_checker, "_nonideal_lle_binary_mixture", lambda: object())
    discovery = _synthetic_phase_discovery()
    discovery["held_stage_ii_status"] = "candidate_bound_gap_closed"
    discovery["held_stage_ii_bound_gap"] = 0.0
    monkeypatch.setattr(phase_discovery_checker, "_phase_discovery_payload", lambda mix: discovery)
    monkeypatch.setattr(
        phase_discovery_checker,
        "_route_refinement_result",
        lambda mix, **kwargs: {
            "solver_status": "acceptable_point",
            "application_status": "solved_to_acceptable_level",
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

    payload = phase_discovery_checker.evaluate_phase_discovery(include_route_refinement=True)

    assert (
        payload["evidence_status"]["held_stage_iii_ipopt_refinement"]
        == "incomplete_ipopt_solver_status_acceptable_point"
    )
    assert "held_stage_iii_ipopt_refinement" in payload["incomplete_requirements"]


def test_phase_discovery_checker_require_complete_fails_incomplete_payload(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr(
        phase_discovery_checker,
        "evaluate_phase_discovery",
        lambda **kwargs: {
            "case_label": "Synthetic neutral binary phase-discovery case",
            "complete": False,
            "evidence_status": {
                "deterministic_screening": "verified_not_full_held",
                "continuous_tpd_minimization": "verified_converged",
                "held_stage_i_stability": "verified_from_converged_continuous_tpd",
                "held_stage_ii_dual_phase_discovery": "verified_candidate_bound_gap_closed",
                "held_stage_iii_ipopt_refinement": "incomplete_ipopt_solver_status_max_iterations_exceeded",
            },
            "diagnostics": {
                "route_refinement_requested": True,
                "route_solver_status": "max_iterations_exceeded",
                "route_application_status": "maximum_iterations_exceeded",
                "route_iteration_count": 260,
                "route_iteration_history": [
                    {
                        "iteration": 260,
                        "objective": 4.2,
                        "primal_infeasibility": 1.0e-3,
                        "dual_infeasibility": 2.0e-3,
                        "barrier_parameter": 1.0e-6,
                        "step_size_primal": 0.25,
                        "step_trial_count": 8,
                    }
                ],
                "route_seed_attempt_count": 1,
                "route_seed_attempts": [
                    {
                        "seed_name": "deterministic_tpd_candidate_pair",
                        "solver_status": "max_iterations_exceeded",
                        "application_status": "maximum_iterations_exceeded",
                        "accepted": False,
                        "iteration_count": 260,
                    }
                ],
            },
        },
    )

    exit_code = phase_discovery_checker.main(["--require-complete"])
    captured = capsys.readouterr()

    assert exit_code == 2
    assert "Phase-discovery validation is incomplete." in captured.err
    assert "seed_attempt: name=deterministic_tpd_candidate_pair" in captured.out
    assert "last_ipopt_iterations:" in captured.out
    assert "ipopt_iteration: iter=260 objective=4.2 inf_pr=0.001 inf_du=0.002" in captured.out


def test_pereira_readiness_checker_reports_nonexecutable_json() -> None:
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
    assert payload["executable_fixture_required_fields"] == [
        "species",
        "pure_component_parameters",
        "binary_interactions",
        "temperature",
        "pressure",
        "feed_composition",
        "expected_phase_count",
        "expected_phase_compositions",
        "expected_phase_fractions",
        "source_model_family",
        "source_path",
        "acceptance_tolerances",
    ]
    assert {
        "pure_component_parameters",
        "binary_interactions",
        "feed_composition",
        "expected_phase_fractions",
        "source_model_family",
        "acceptance_tolerances",
    } <= set(payload["unmet_executable_fixture_fields"])
    assert payload["executable_fixture_field_status"]["species"] == "present"
    assert payload["executable_fixture_field_status"]["pure_component_parameters"] == "rejected_saft_vr_parameters"
    assert payload["executable_fixture_field_status"]["binary_interactions"] == "rejected_saft_vr_binary_factors"
    assert payload["executable_fixture_field_status"]["source_model_family"] == "rejected_model_family_mismatch"
    assert "executable_fixture_contract_incomplete" in payload["blockers"]
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


def test_readiness_checker_accepts_complete_source_backed_fixture(
    tmp_path: Path,
) -> None:
    case_dir = tmp_path / "minimal_pc_saft_binary"
    _write_minimal_neutral_flash_fixture(case_dir)
    phase_discovery_path = tmp_path / "complete_phase_discovery.json"
    _write_complete_phase_discovery_payload(phase_discovery_path)

    result = _run_checker(
        "--case-dir",
        str(case_dir),
        "--stage9-evidence-json",
        str(phase_discovery_path),
        "--json",
        "--require-executable",
    )

    assert result.returncode == 0, result.stdout + result.stderr
    payload = _load_stdout_json(result)
    assert payload["proof_status"] == "executable"
    assert payload["executable"] is True
    assert payload["stage9_evidence_path_verified"] is True
    assert payload["unmet_executable_fixture_fields"] == []
    assert payload["blockers"] == []
    assert all(status == "present" for status in payload["executable_fixture_field_status"].values())


def test_hydrocarbon_workbook_fixture_is_executable_with_phase_discovery_payload(
    tmp_path: Path,
) -> None:
    phase_discovery_path = tmp_path / "complete_phase_discovery.json"
    _write_complete_phase_discovery_payload(phase_discovery_path)

    result = _run_checker(
        "--case-dir",
        str(HYDROCARBON_CASE_DIR),
        "--stage9-evidence-json",
        str(phase_discovery_path),
        "--json",
        "--require-executable",
    )

    assert result.returncode == 0, result.stdout + result.stderr
    payload = _load_stdout_json(result)
    assert payload["case_label"] == "Hydrocarbon workbook derived TP flash"
    assert payload["proof_status"] == "executable"
    assert payload["executable"] is True
    assert payload["stage9_evidence_path_verified"] is True
    assert payload["unmet_executable_fixture_fields"] == []
    assert payload["blockers"] == []


def test_neutral_flash_checker_requires_complete_phase_discovery_payload(
    tmp_path: Path,
) -> None:
    phase_discovery_path = tmp_path / "incomplete_phase_discovery.json"
    phase_discovery_path.write_text(
        json.dumps(
            {
                "complete": False,
                "evidence_status": {
                    "deterministic_screening": "verified_not_full_held",
                    "continuous_tpd_minimization": "verified_converged",
                    "held_stage_i_stability": "verified_from_converged_continuous_tpd",
                    "held_stage_ii_dual_phase_discovery": "verified_candidate_bound_gap_closed",
                    "held_stage_iii_ipopt_refinement": "incomplete_ipopt_solver_status_max_iterations_exceeded",
                },
                "incomplete_requirements": ["held_stage_iii_ipopt_refinement"],
            }
        ),
        encoding="utf-8",
    )

    result = _run_neutral_flash_checker("--stage9-evidence-json", str(phase_discovery_path), "--json", "--require-proof")

    assert result.returncode == 2
    payload = _load_stdout_json(result)
    assert payload["proof_complete"] is False
    assert payload["route"] is None
    assert "stage9_evidence_path_not_verified" in payload["blockers"]
    assert "held_stage_iii_ipopt_refinement" in payload["readiness"]["stage9_incomplete_requirements"]


def test_neutral_flash_checker_runs_source_backed_workbook_fixture(
    tmp_path: Path,
) -> None:
    import epcsaft._core as _core

    if not _core._native_ipopt_smoke()["compiled"]:
        pytest.skip("native Ipopt is not compiled")

    phase_discovery_path = tmp_path / "phase_discovery.json"
    _write_complete_phase_discovery_payload(phase_discovery_path)

    result = _run_neutral_flash_checker(
        "--stage9-evidence-json",
        str(phase_discovery_path),
        "--json",
        "--debug",
        "--require-proof",
    )

    assert result.returncode == 0, result.stdout + result.stderr
    payload = _load_stdout_json(result)
    assert "EXIT: Optimal Solution Found." in result.stderr
    assert payload["case_label"] == "Hydrocarbon workbook derived TP flash"
    assert payload["proof_status"] == "complete"
    assert payload["proof_complete"] is True
    assert payload["blockers"] == []
    assert payload["stage9_evidence_source"] == str(phase_discovery_path)
    assert payload["readiness"]["stage9_evidence_path_verified"] is True
    assert payload["route"]["solver_status"] == "success"
    assert payload["route"]["application_status"] == "solve_succeeded"
    assert payload["route"]["ipopt_print_level"] == 5
    assert payload["route"]["hessian_approximation"] == "exact"
    assert payload["route"]["exact_hessian_available"] is True
    assert payload["route"]["iteration_count"] > 0
    assert payload["route"]["iteration_history_size"] > 0
    assert payload["route"]["iteration_history"]
    assert payload["route"]["postsolve"]["stability_accepted"] is True
    assert payload["comparison"]["max_composition_abs_error"] <= 1.0e-5
    assert payload["comparison"]["max_phase_fraction_abs_error"] <= 2.0e-5


def test_pereira_readiness_checker_fails_closed_when_executable_required() -> None:
    result = _run_checker("--json", "--require-executable")

    assert result.returncode == 2
    payload = _load_stdout_json(result)
    assert payload["executable"] is False
    assert payload["proof_status"] == "blocked"
    assert "Pereira 2012 System III is not an executable equilibrium fixture" in result.stderr


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


def test_phase_discovery_checker_reports_candidate_status_without_refinement() -> None:
    result = _run_phase_discovery_checker("--json")

    assert result.returncode == 0, result.stdout + result.stderr
    payload = _load_stdout_json(result)

    assert payload["family_label"] == "PE-Neutral TP Flash"
    assert payload["complete"] is False
    assert payload["evidence_status"]["deterministic_screening"] == "verified_not_full_held"
    assert payload["evidence_status"]["continuous_tpd_minimization"] == "verified_converged"
    assert payload["evidence_status"]["held_stage_i_stability"] == "verified_from_converged_continuous_tpd"
    assert (
        payload["evidence_status"]["held_stage_ii_dual_phase_discovery"]
        == "verified_candidate_bound_gap_closed"
    )
    assert (
        payload["evidence_status"]["held_stage_iii_ipopt_refinement"]
        == "not_requested"
    )
    assert payload["incomplete_requirements"] == [
        "held_stage_iii_ipopt_refinement",
    ]
    assert payload["diagnostics"]["route_refinement_requested"] is False
    assert payload["diagnostics"]["held_stage_ii_status"] == "candidate_bound_gap_closed"
    assert payload["diagnostics"]["held_stage_ii_major_iterations"] > 0
    assert payload["diagnostics"]["held_stage_ii_bound_gap"] <= 1.0e-6


def test_phase_discovery_checker_debug_mode_preserves_json_stdout() -> None:
    result = _run_phase_discovery_checker("--json", "--debug")

    assert result.returncode == 0, result.stdout + result.stderr
    payload = _load_stdout_json(result)

    assert payload["diagnostics"]["equilibrium_debug_enabled"] is True
    assert payload["diagnostics"]["route_refinement_requested"] is False
    assert payload["diagnostics"]["ipopt_print_level"] == 5
    assert "[EPCSAFT_TPD_DEBUG]" in result.stderr


def test_phase_discovery_checker_debug_route_reports_complete_converged_path() -> None:
    result = _run_phase_discovery_checker("--json", "--debug", "--include-route-refinement")

    assert result.returncode == 0, result.stdout + result.stderr
    payload = _load_stdout_json(result)

    assert payload["complete"] is True
    assert payload["incomplete_requirements"] == []
    assert payload["evidence_status"]["held_stage_iii_ipopt_refinement"].startswith("verified")
    assert payload["diagnostics"]["route_solver_status"] == "success"
    assert payload["diagnostics"]["route_application_status"] == "solve_succeeded"
    assert payload["diagnostics"]["route_iteration_count"] > 0
    assert payload["diagnostics"]["route_iteration_history_size"] > 0
    assert payload["diagnostics"]["route_scaled_acceptance_passed"] is True
    assert payload["diagnostics"]["route_seed_attempt_count"] <= 2
    assert "[EPCSAFT_TPD_DEBUG]" in result.stderr
    assert "[EPCSAFT_ROUTE_DEBUG]" in result.stderr
    assert "event=seed_attempt_start" in result.stderr
    assert "event=seed_attempt_finish" in result.stderr
    assert "EXIT: Optimal Solution Found." in result.stderr


def test_pereira_readiness_checker_consumes_phase_discovery_payload_without_faking_completion(
    tmp_path: Path,
) -> None:
    phase_discovery_path = tmp_path / "phase_discovery.json"
    phase_discovery_path.write_text(
        json.dumps(
            {
                "complete": False,
                "evidence_status": {
                    "deterministic_screening": "verified_not_full_held",
                    "continuous_tpd_minimization": "verified_converged",
                    "held_stage_i_stability": "verified_from_converged_continuous_tpd",
                    "held_stage_ii_dual_phase_discovery": "incomplete_candidate_bound_gap_open",
                    "held_stage_iii_ipopt_refinement": "verified_current_route_refinement_pending_stage_ii_candidates",
                },
                "incomplete_requirements": [
                    "held_stage_ii_dual_phase_discovery",
                ],
            }
        ),
        encoding="utf-8",
    )

    result = _run_checker("--json", "--stage9-evidence-json", str(phase_discovery_path))

    assert result.returncode == 0, result.stdout + result.stderr
    payload = _load_stdout_json(result)

    assert payload["stage9_evidence_path_verified"] is False
    assert payload["stage9_evidence"]["continuous_tpd_minimization"] == "verified_converged"
    assert payload["stage9_evidence"]["held_stage_ii_dual_phase_discovery"] == "incomplete_candidate_bound_gap_open"
    assert payload["stage9_incomplete_requirements"] == [
        "held_stage_ii_dual_phase_discovery",
    ]
    assert "stage9_evidence_path_not_verified" in payload["blockers"]


def test_pereira_readiness_checker_removes_blocker_only_for_complete_phase_discovery_payload(
    tmp_path: Path,
) -> None:
    phase_discovery_path = tmp_path / "complete_phase_discovery.json"
    phase_discovery_path.write_text(
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

    result = _run_checker("--json", "--stage9-evidence-json", str(phase_discovery_path))

    assert result.returncode == 0, result.stdout + result.stderr
    payload = _load_stdout_json(result)

    assert payload["stage9_evidence_path_verified"] is True
    assert "stage9_evidence_path_not_verified" not in payload["blockers"]
    assert payload["executable"] is False
    assert {"model_family_mismatch", "saft_vr_runtime_absent"} <= set(payload["blockers"])
