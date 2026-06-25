from __future__ import annotations

import copy
import importlib.util
import json
import math
import subprocess
import sys
from pathlib import Path
from typing import Any

from epcsaft_equilibrium._native import extension_native_core

REPO_ROOT = Path(__file__).resolve().parents[3]
CHECKER_PATH = REPO_ROOT / "scripts" / "validation" / "check_electrolyte_stage_iii_refinement.py"


def _load_checker() -> Any:
    assert CHECKER_PATH.is_file(), f"missing checker: {CHECKER_PATH.relative_to(REPO_ROOT)}"
    spec = importlib.util.spec_from_file_location("check_electrolyte_stage_iii_refinement", CHECKER_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_native_electrolyte_stage_iii_refinement_binding_is_exposed() -> None:
    core = extension_native_core()

    assert hasattr(core, "_native_electrolyte_stage_iii_refinement")


def test_stage_iii_consumes_held2_candidate_set() -> None:
    checker = _load_checker()

    payload = checker.minimal_complete_payload_for_tests()
    stage_iii = payload["electrolyte_stage_iii_refinement"]

    assert stage_iii["status"] == "complete"
    assert stage_iii["seed_provenance"]["source_gate"] == "electrolyte_held2_counterion_pair_phase_discovery"
    assert stage_iii["seed_provenance"]["native_binding"] == "_native_electrolyte_held2_phase_discovery"
    assert stage_iii["seed_provenance"]["selected_candidate_count"] == 2
    assert stage_iii["selected_phase_labels"] == ["phase_0", "phase_1"]


def test_reduced_residual_shape_and_scaling() -> None:
    checker = _load_checker()

    payload = checker.minimal_complete_payload_for_tests()
    residual = payload["electrolyte_stage_iii_refinement"]["reduced_residual_system"]

    assert residual["coordinate_basis"] == "counterion_pair_transformed_variables"
    assert residual["variable_labels"] == [
        "phase_0:Na+/Cl-",
        "phase_1:Na+/Cl-",
        "phase_0_fraction",
    ]
    assert residual["equation_labels"] == [
        "pair_mean_ionic_equality:Na+/Cl-",
        "phase_fraction_closure",
        "phase_charge_balance:phase_0",
        "phase_charge_balance:phase_1",
    ]
    assert len(residual["variable_lower_bounds"]) == len(residual["variable_labels"])
    assert len(residual["variable_upper_bounds"]) == len(residual["variable_labels"])
    assert len(residual["variable_scaling"]) == len(residual["variable_labels"])
    assert len(residual["residual_scaling"]) == len(residual["equation_labels"])


def test_exact_reduced_derivatives_reported() -> None:
    checker = _load_checker()

    payload = checker.minimal_complete_payload_for_tests()
    derivatives = payload["electrolyte_stage_iii_refinement"]["derivative_receipts"]

    assert derivatives["gradient_approximation"] == "exact"
    assert derivatives["jacobian_approximation"] == "exact"
    assert derivatives["hessian_approximation"] == "exact"
    assert derivatives["exact_reduced_jacobian_available"] is True
    assert derivatives["exact_reduced_hessian_available"] is True
    assert derivatives["jacobian_nonzero_count"] > 0
    assert derivatives["hessian_nonzero_count"] > 0


def test_stage_iii_solver_diagnostics_are_strict() -> None:
    checker = _load_checker()

    payload = checker.minimal_complete_payload_for_tests()
    solver = payload["electrolyte_stage_iii_refinement"]["solver_diagnostics"]

    assert solver["solver_backend"] == "ipopt"
    assert solver["ipopt_status"] == "Solve_Succeeded"
    assert solver["application_status"] == "solve_succeeded"
    assert solver["residual_inf_norm"] <= solver["residual_tolerance"]
    assert solver["active_bound_violation"] <= solver["active_bound_tolerance"]
    assert solver["phase_distance"] > solver["phase_distance_tolerance"]
    assert solver["phase_compositions"]
    assert all(math.isfinite(float(value)) for row in solver["phase_compositions"] for value in row)


def test_stage_iii_rejects_missing_prerequisite_gates() -> None:
    checker = _load_checker()
    payload = checker.minimal_complete_payload_for_tests()
    mutated = copy.deepcopy(payload)
    mutated["source_gate"]["complete"] = False
    mutated["held2_readiness_gate"]["complete"] = False
    mutated["electrolyte_tpd_gate"]["complete"] = False
    mutated["held2_phase_discovery"]["complete"] = False

    result = checker.evaluate_payload(
        mutated,
        require_source_gate=True,
        require_readiness_gate=True,
        require_tpd_gate=True,
        require_held2_discovery=True,
        require_native_stage_iii=True,
        require_public_routes_closed=True,
    )

    assert result["complete"] is False
    assert "electrolyte_source_gate_incomplete" in result["blockers"]
    assert "electrolyte_held2_readiness_gate_incomplete" in result["blockers"]
    assert "electrolyte_tpd_gate_incomplete" in result["blockers"]
    assert "held2_phase_discovery_incomplete" in result["blockers"]


def test_stage_iii_rejects_phase_collapse() -> None:
    checker = _load_checker()
    payload = checker.minimal_complete_payload_for_tests()
    mutated = copy.deepcopy(payload)
    stage_iii = mutated["electrolyte_stage_iii_refinement"]
    stage_iii["solver_diagnostics"]["phase_distance"] = 0.0
    stage_iii["solver_diagnostics"]["phase_compositions"][1] = list(
        stage_iii["solver_diagnostics"]["phase_compositions"][0]
    )

    result = checker.evaluate_payload(
        mutated,
        require_source_gate=True,
        require_readiness_gate=True,
        require_tpd_gate=True,
        require_held2_discovery=True,
        require_native_stage_iii=True,
        require_public_routes_closed=True,
    )

    assert result["complete"] is False
    assert "stage_iii_phase_collapse" in result["blockers"]


def test_stage_iii_rejects_raw_single_ion_equality() -> None:
    checker = _load_checker()
    payload = checker.minimal_complete_payload_for_tests()
    mutated = copy.deepcopy(payload)
    mutated["electrolyte_stage_iii_refinement"]["reduced_residual_system"]["raw_single_ion_residuals"] = {
        "Na+": 0.0,
        "Cl-": 0.0,
    }

    result = checker.evaluate_payload(
        mutated,
        require_source_gate=True,
        require_readiness_gate=True,
        require_tpd_gate=True,
        require_held2_discovery=True,
        require_native_stage_iii=True,
        require_public_routes_closed=True,
    )

    assert result["complete"] is False
    assert "stage_iii_raw_single_ion_equality_present" in result["blockers"]


def test_public_electrolyte_routes_stay_closed() -> None:
    checker = _load_checker()

    payload = checker.minimal_complete_payload_for_tests()

    assert payload["public_route_state"]["electrolyte_lle"]["production_exposed"] is False
    assert payload["public_route_state"]["electrolyte_lle"]["public_routes"] == []
    assert payload["electrolyte_stage_iii_refinement"]["stage_statuses"]["postsolve_certification"] == "pending"
    assert payload["electrolyte_stage_iii_refinement"]["stage_statuses"]["public_route_admission"] == "closed"


def test_cli_requires_complete_electrolyte_stage_iii_refinement() -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(CHECKER_PATH),
            "--json",
            "--require-source-gate",
            "--require-readiness-gate",
            "--require-tpd-gate",
            "--require-held2-discovery",
            "--require-native-stage-iii",
            "--require-public-routes-closed",
            "--require-complete",
        ],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["complete"] is True
    assert payload["blockers"] == []
