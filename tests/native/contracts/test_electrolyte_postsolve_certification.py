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
CHECKER_PATH = REPO_ROOT / "scripts" / "validation" / "check_electrolyte_postsolve_certification.py"


def _load_checker() -> Any:
    assert CHECKER_PATH.is_file(), f"missing checker: {CHECKER_PATH.relative_to(REPO_ROOT)}"
    spec = importlib.util.spec_from_file_location("check_electrolyte_postsolve_certification", CHECKER_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_native_electrolyte_postsolve_certification_binding_is_exposed() -> None:
    core = extension_native_core()

    assert hasattr(core, "_native_electrolyte_postsolve_certification")


def test_postsolve_requires_stage_iii_gate() -> None:
    checker = _load_checker()
    payload = checker.minimal_complete_payload_for_tests()
    mutated = copy.deepcopy(payload)
    mutated["electrolyte_stage_iii_refinement"]["status"] = "incomplete"

    result = checker.evaluate_payload(
        mutated,
        require_stage_iii=True,
        require_postsolve_certification=True,
        require_public_routes_closed=True,
    )

    assert result["complete"] is False
    assert "stage_iii_refinement_incomplete" in result["blockers"]


def test_explicit_ion_reconstruction_closes() -> None:
    checker = _load_checker()

    payload = checker.minimal_complete_payload_for_tests()
    reconstruction = payload["electrolyte_postsolve_certification"]["explicit_ion_reconstruction"]

    assert reconstruction["status"] == "accepted"
    assert reconstruction["component_labels"] == ["water", "Na+", "Cl-"]
    assert reconstruction["reconstructed_feed_composition"] == [0.98, 0.01, 0.01]
    assert reconstruction["feed_reconstruction_inf_norm"] <= reconstruction["feed_reconstruction_tolerance"]
    assert reconstruction["component_nonnegativity_margin"] >= 0.0


def test_phase_charge_balance_closes() -> None:
    checker = _load_checker()

    payload = checker.minimal_complete_payload_for_tests()
    charges = payload["electrolyte_postsolve_certification"]["charge_balance"]

    assert charges["status"] == "accepted"
    assert charges["charge_vector"] == [0.0, 1.0, -1.0]
    assert charges["phase_charge_residuals"] == [0.0, 0.0]
    assert charges["max_phase_charge_residual"] <= charges["phase_charge_tolerance"]
    assert charges["total_charge_residual"] <= charges["total_charge_tolerance"]


def test_transfer_residual_families_are_separate() -> None:
    checker = _load_checker()

    payload = checker.minimal_complete_payload_for_tests()
    transfer = payload["electrolyte_postsolve_certification"]["transfer_residuals"]

    assert transfer["status"] == "accepted"
    assert "neutral_transfer" in transfer
    assert "mean_ionic_transfer" in transfer
    assert transfer["neutral_transfer"]["species_labels"] == ["water"]
    assert transfer["neutral_transfer"]["max_abs_residual"] <= transfer["neutral_transfer"]["tolerance"]
    assert transfer["mean_ionic_transfer"]["pair_labels"] == ["Na+/Cl-"]
    assert transfer["mean_ionic_transfer"]["max_abs_residual"] <= transfer["mean_ionic_transfer"]["tolerance"]


def test_pressure_phase_amount_and_domain_margins_are_certified() -> None:
    checker = _load_checker()

    payload = checker.minimal_complete_payload_for_tests()
    certification = payload["electrolyte_postsolve_certification"]
    pressure = certification["pressure_consistency"]
    phases = certification["phase_set"]
    domain = certification["domain_margins"]

    assert pressure["status"] == "accepted"
    assert pressure["pressure_consistency_norm"] <= pressure["pressure_tolerance"]
    assert phases["status"] == "accepted"
    assert phases["phase_count"] == 2
    assert phases["phase_amount_totals"] == [0.4, 0.6]
    assert phases["phase_fraction_sum_residual"] <= phases["phase_fraction_sum_tolerance"]
    assert phases["composition_sum_residuals"] == [0.0, 0.0]
    assert all(math.isfinite(float(value)) for row in phases["phase_compositions"] for value in row)
    assert domain["status"] == "accepted"
    assert domain["minimum_component_mole_fraction"] >= 0.0
    assert domain["minimum_phase_amount"] > 0.0
    assert domain["phase_distance"] > domain["phase_distance_tolerance"]


def test_postsolve_rejects_stage_iii_only_result() -> None:
    checker = _load_checker()
    payload = checker.minimal_complete_payload_for_tests()
    mutated = copy.deepcopy(payload)
    mutated["electrolyte_postsolve_certification"] = {}

    result = checker.evaluate_payload(
        mutated,
        require_stage_iii=True,
        require_postsolve_certification=True,
        require_public_routes_closed=True,
    )

    assert result["complete"] is False
    assert "postsolve_certification_missing" in result["blockers"]


def test_postsolve_rejects_phase_collapsed_result() -> None:
    checker = _load_checker()
    payload = checker.minimal_complete_payload_for_tests()
    mutated = copy.deepcopy(payload)
    mutated["electrolyte_postsolve_certification"]["domain_margins"]["phase_distance"] = 0.0

    result = checker.evaluate_payload(
        mutated,
        require_stage_iii=True,
        require_postsolve_certification=True,
        require_public_routes_closed=True,
    )

    assert result["complete"] is False
    assert "postsolve_phase_distance_not_certified" in result["blockers"]


def test_postsolve_rejects_charge_imbalanced_phases() -> None:
    checker = _load_checker()
    payload = checker.minimal_complete_payload_for_tests()
    mutated = copy.deepcopy(payload)
    mutated["electrolyte_postsolve_certification"]["charge_balance"]["phase_charge_residuals"] = [1.0e-3, 0.0]
    mutated["electrolyte_postsolve_certification"]["charge_balance"]["max_phase_charge_residual"] = 1.0e-3

    result = checker.evaluate_payload(
        mutated,
        require_stage_iii=True,
        require_postsolve_certification=True,
        require_public_routes_closed=True,
    )

    assert result["complete"] is False
    assert "postsolve_phase_charge_balance_not_certified" in result["blockers"]


def test_postsolve_rejects_missing_transfer_diagnostics() -> None:
    checker = _load_checker()
    payload = checker.minimal_complete_payload_for_tests()
    mutated = copy.deepcopy(payload)
    del mutated["electrolyte_postsolve_certification"]["transfer_residuals"]["mean_ionic_transfer"]

    result = checker.evaluate_payload(
        mutated,
        require_stage_iii=True,
        require_postsolve_certification=True,
        require_public_routes_closed=True,
    )

    assert result["complete"] is False
    assert "postsolve_mean_ionic_transfer_missing" in result["blockers"]


def test_postsolve_rejects_public_admission_status() -> None:
    checker = _load_checker()
    payload = checker.minimal_complete_payload_for_tests()
    mutated = copy.deepcopy(payload)
    mutated["electrolyte_postsolve_certification"]["stage_statuses"]["public_route_admission"] = "complete"

    result = checker.evaluate_payload(
        mutated,
        require_stage_iii=True,
        require_postsolve_certification=True,
        require_public_routes_closed=True,
    )

    assert result["complete"] is False
    assert "postsolve_public_route_admission_claimed" in result["blockers"]


def test_public_electrolyte_routes_stay_closed() -> None:
    checker = _load_checker()

    payload = checker.minimal_complete_payload_for_tests()
    public_state = payload["public_route_state"]["electrolyte_lle"]
    stages = payload["electrolyte_postsolve_certification"]["stage_statuses"]

    assert stages["postsolve_certification"] == "complete"
    assert stages["public_route_admission"] == "closed"
    assert public_state["production_exposed"] is False
    assert public_state["public_routes"] == []
    assert public_state["proof_routes"] == []


def test_cli_requires_complete_electrolyte_postsolve_certification() -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(CHECKER_PATH),
            "--json",
            "--require-stage-iii",
            "--require-postsolve-certification",
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
