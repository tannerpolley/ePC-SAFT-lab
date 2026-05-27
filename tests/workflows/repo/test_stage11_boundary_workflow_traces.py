from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
BOUNDARY_CHECKER = REPO_ROOT / "scripts" / "validation" / "check_stage11_boundary_workflow_traces.py"


def _run_boundary_checker(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(BOUNDARY_CHECKER), *args],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )


def _load_stdout_json(result: subprocess.CompletedProcess[str]) -> dict[str, object]:
    assert result.stdout, result.stderr
    return json.loads(result.stdout)


def test_boundary_workflow_contracts_keep_cloud_shadow_planned() -> None:
    result = _run_boundary_checker("--json", "--contracts-only")

    assert result.returncode == 0, result.stdout + result.stderr
    payload = _load_stdout_json(result)
    workflows = {row["label"]: row for row in payload["workflows"]}

    assert payload["boundary_status"] == "contracts_available"
    assert set(workflows) == {"Bubble point", "Dew point", "Cloud point", "Shadow point"}
    assert workflows["Bubble point"]["runtime_status"] == "executable_current_routes"
    assert workflows["Dew point"]["runtime_status"] == "executable_current_routes"
    assert workflows["Cloud point"]["runtime_status"] == "planned_not_executable"
    assert workflows["Shadow point"]["runtime_status"] == "planned_not_executable"
    assert workflows["Cloud point"]["trace_points"] == []
    assert workflows["Shadow point"]["trace_points"] == []
    assert workflows["Bubble point"]["activation_family_row"] is False
    assert workflows["Dew point"]["activation_family_row"] is False
    assert set(workflows["Bubble point"]["diagram_targets"]) == {"P-x", "T-x"}
    assert set(workflows["Dew point"]["diagram_targets"]) == {"P-x", "T-x"}


def test_boundary_checker_rejects_route_sweeps_without_explicit_opt_in() -> None:
    result = _run_boundary_checker("--json", "--run-current-boundary-route")

    assert result.returncode == 2, result.stdout + result.stderr
    payload = _load_stdout_json(result)

    assert payload["boundary_status"] == "route_sweep_rejected"
    assert payload["requested_route_point_count"] == 4
    assert "explicit_route_or_allow_route_sweep_required" in payload["blockers"]


@pytest.mark.ipopt
@pytest.mark.native_solver
@pytest.mark.slow
def test_boundary_route_reports_strict_convergence_and_debug_output() -> None:
    import epcsaft._core as _core

    if not _core._native_ipopt_smoke()["compiled"]:
        pytest.skip("native Ipopt is not compiled")

    result = _run_boundary_checker(
        "--json",
        "--run-current-boundary-route",
        "--route",
        "bubble_pressure",
        "--debug",
        "--require-complete",
    )

    assert result.returncode == 0, result.stdout + result.stderr
    payload = _load_stdout_json(result)
    workflows = {row["label"]: row for row in payload["workflows"]}

    assert "EXIT: Optimal Solution Found." in result.stderr
    assert "EXIT: Maximum Number of Iterations Exceeded." not in result.stderr
    assert payload["boundary_status"] == "complete_route_convergence"
    assert payload["complete"] is True
    assert payload["source_fixture"].endswith("hydrocarbon_workbook_flash")
    assert payload["requested_route_point_count"] == 1
    assert payload["trace_summary"]["accepted_trace_point_count"] == 1
    assert payload["trace_summary"]["failed_trace_point_count"] == 0

    workflow = workflows["Bubble point"]
    assert workflow["runtime_status"] == "executable_current_routes"
    assert workflow["trace_status"] == "complete"
    assert len(workflow["trace_points"]) == 1
    point = workflow["trace_points"][0]
    assert point["status"] == "accepted"
    assert point["route"] == "bubble_pressure"
    assert point["solver_status"] == "success"
    assert point["application_status"] == "solve_succeeded"
    assert point["route_status"] == "accepted"
    assert point["ipopt_print_level"] == 5
    assert point["iteration_history_size"] > 0
    assert point["residuals"]["pressure_consistency_norm"] <= 1.0e-2
    assert point["residuals"]["ln_fugacity_consistency_norm"] <= 1.0e-7
    assert point["strict_convergence"] is True
    assert point["iteration_limit_seed_attempts"] == []

    assert workflows["Cloud point"]["trace_status"] == "planned_not_executable"
    assert workflows["Shadow point"]["trace_status"] == "planned_not_executable"


@pytest.mark.ipopt
@pytest.mark.native_solver
@pytest.mark.slow
def test_boundary_route_points_complete_only_with_explicit_opt_in() -> None:
    import epcsaft._core as _core

    if not _core._native_ipopt_smoke()["compiled"]:
        pytest.skip("native Ipopt is not compiled")

    result = _run_boundary_checker(
        "--json",
        "--run-current-boundary-route",
        "--allow-route-sweep",
        "--trace-point-count",
        "2",
        "--require-complete",
    )

    assert result.returncode == 0, result.stdout + result.stderr
    payload = _load_stdout_json(result)
    workflows = {row["label"]: row for row in payload["workflows"]}

    assert payload["boundary_status"] == "complete_route_convergence"
    assert payload["complete"] is True
    assert payload["requested_route_point_count"] == 8
    assert payload["trace_summary"]["accepted_trace_point_count"] == 8
    assert payload["trace_summary"]["failed_trace_point_count"] == 0
    for label in ("Bubble point", "Dew point"):
        assert workflows[label]["trace_status"] == "complete"
        assert len(workflows[label]["trace_points"]) == 4
        assert {point["diagram_target"] for point in workflows[label]["trace_points"]} == {"P-x", "T-x"}
        assert {point["sample_index"] for point in workflows[label]["trace_points"]} == {0, 1}
        for point in workflows[label]["trace_points"]:
            assert point["status"] == "accepted"
            assert point["solver_status"] == "success"
            assert point["application_status"] == "solve_succeeded"
            assert point["strict_convergence"] is True
            assert point["iteration_limit_seed_attempts"] == []
            assert any(
                attempt["seed_name"] == point["seed_source"]
                and attempt["solver_status"] == "success"
                and attempt["application_status"] == "solve_succeeded"
                for attempt in point["seed_attempts"]
            )
