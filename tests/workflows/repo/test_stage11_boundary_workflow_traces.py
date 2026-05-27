from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
STAGE11_CHECKER = REPO_ROOT / "scripts" / "validation" / "check_stage11_boundary_workflow_traces.py"


def _run_stage11_checker(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(STAGE11_CHECKER), *args],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )


def _load_stdout_json(result: subprocess.CompletedProcess[str]) -> dict[str, object]:
    assert result.stdout, result.stderr
    return json.loads(result.stdout)


def test_stage11_boundary_workflow_contracts_keep_cloud_shadow_planned() -> None:
    result = _run_stage11_checker("--json", "--contracts-only")

    assert result.returncode == 0, result.stdout + result.stderr
    payload = _load_stdout_json(result)
    workflows = {row["label"]: row for row in payload["workflows"]}

    assert payload["stage11_status"] == "contracts_available"
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


def test_stage11_checker_rejects_route_sweeps_without_explicit_opt_in() -> None:
    result = _run_stage11_checker("--json", "--run-current-boundary-route")

    assert result.returncode == 2, result.stdout + result.stderr
    payload = _load_stdout_json(result)

    assert payload["stage11_status"] == "route_sweep_rejected"
    assert payload["requested_route_point_count"] == 4
    assert "explicit_route_or_allow_route_sweep_required" in payload["blockers"]


@pytest.mark.ipopt
@pytest.mark.native_solver
@pytest.mark.slow
def test_stage11_current_boundary_route_requires_strict_convergence_and_debug_output() -> None:
    import epcsaft._core as _core

    if not _core._native_ipopt_smoke()["compiled"]:
        pytest.skip("native Ipopt is not compiled")

    result = _run_stage11_checker(
        "--json",
        "--run-current-boundary-route",
        "--route",
        "bubble_pressure",
        "--debug",
        "--require-complete",
    )

    assert result.returncode == 2, result.stdout + result.stderr
    payload = _load_stdout_json(result)
    workflows = {row["label"]: row for row in payload["workflows"]}

    assert "EXIT: Maximum Number of Iterations Exceeded." in result.stderr
    assert payload["stage11_status"] == "blocked_current_boundary_convergence"
    assert payload["complete"] is False
    assert payload["source_fixture"].endswith("hydrocarbon_workbook_flash")
    assert payload["requested_route_point_count"] == 1
    assert payload["trace_summary"]["accepted_trace_point_count"] == 0
    assert payload["trace_summary"]["failed_trace_point_count"] == 1

    workflow = workflows["Bubble point"]
    assert workflow["runtime_status"] == "executable_current_routes"
    assert workflow["trace_status"] == "blocked"
    assert len(workflow["trace_points"]) == 1
    point = workflow["trace_points"][0]
    assert point["status"] == "blocked_nonconverged"
    assert point["route"] == "bubble_pressure"
    assert point["solver_status"] == "max_iterations_exceeded"
    assert point["application_status"] == "maximum_iterations_exceeded"
    assert point["route_status"] == "accepted"
    assert point["ipopt_print_level"] == 5
    assert point["iteration_history_size"] > 0
    assert point["residuals"]["pressure_consistency_norm"] <= 1.0e-2
    assert point["residuals"]["ln_fugacity_consistency_norm"] <= 1.0e-7
    assert point["strict_convergence"] is False
    assert point["iteration_limit_seed_attempts"] == ["canonical_phase_density_root", "mirrored_phase_density_root"]

    assert workflows["Cloud point"]["trace_status"] == "planned_not_executable"
    assert workflows["Shadow point"]["trace_status"] == "planned_not_executable"
