from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

import epcsaft
import epcsaft_equilibrium
from scripts.validation import check_electrolyte_public_admission as checker

REPO_ROOT = Path(__file__).resolve().parents[5]
CHECKER_PATH = REPO_ROOT / "scripts" / "validation" / "check_electrolyte_public_admission.py"
PARAMETER_DIR = REPO_ROOT / "analyses" / "paper_validation" / "2026_khudaida" / "parameters"
SPECIES = ["H2O", "Ethanol", "Butanol", "Na+", "Cl-"]
FEED = [
    0.7295582904360921,
    0.013336215598851259,
    0.20495308450174898,
    0.026076204731653927,
    0.026076204731653927,
]


def _khudaida_public_mixture() -> epcsaft.Mixture:
    return epcsaft.Mixture.from_folder(
        PARAMETER_DIR,
        components=SPECIES,
        reference_temperature=293.15,
        reference_composition=FEED,
    )


def test_electrolyte_held2_public_route_checker_requires_stage_ii_replay() -> None:
    payload = checker.minimal_complete_payload_for_tests()
    result = checker.evaluate_payload(
        payload,
        require_held2_stage_ii=True,
        require_stage_iii=True,
        require_postsolve_certification=True,
        require_public_admission=True,
    )

    assert result["complete"] is True, result["blockers"]

    mutated = copy.deepcopy(payload)
    tpd = mutated["held2_phase_discovery"]["tpd_discovery"]
    tpd["held_stage_ii_status"] = "pending"
    tpd["held_stage_ii_replay_ready"] = False
    tpd["held_stage_ii_replay_phase_fractions"] = []
    tpd["held_stage_ii_replay_phase_kinds"] = []
    tpd["held_stage_ii_replay_phase_compositions"] = []

    rejected = checker.evaluate_payload(mutated, require_held2_stage_ii=True)

    assert rejected["complete"] is False
    assert "held2_stage_ii_replay_missing" in rejected["blockers"]


def test_electrolyte_held2_public_route_result_retains_stage_ii_to_stage_iii_provenance() -> None:
    result = epcsaft_equilibrium.Equilibrium(
        _khudaida_public_mixture(),
        route="electrolyte_lle",
        T=293.15,
        P=100000.0,
        z=FEED,
    ).solve(
        solver_options={
            "max_iterations": 180,
            "tolerance": 1.0e-6,
            "hessian_mode": "auto",
            "ipopt_iteration_history_limit": 8,
            "ipopt_acceptable_tolerance": 1.0e-7,
            "ipopt_constraint_violation_tolerance": 1.0e-8,
            "ipopt_dual_infeasibility_tolerance": 1.0e-8,
            "ipopt_complementarity_tolerance": 1.0e-8,
        }
    )

    diagnostics = result.diagnostics
    discovery = diagnostics["held2_phase_discovery"]
    stage_ii = discovery["tpd_discovery"]
    stage_iii = diagnostics["electrolyte_stage_iii_refinement"]
    postsolve = diagnostics["postsolve_certification"]

    assert result.route == "electrolyte_lle"
    assert diagnostics["public_admission"]["status"] == "accepted"
    assert postsolve["accepted"] is True
    assert stage_ii["held_stage_ii_status"] == "dual_loop_verified"
    assert stage_ii["held_stage_ii_replay_ready"] is True
    assert stage_iii["seed_provenance"]["native_binding"] == "_native_electrolyte_held2_phase_discovery"
    assert stage_iii["seed_provenance"]["selected_phase_fractions"] == pytest.approx(
        stage_ii["held_stage_ii_replay_phase_fractions"]
    )
    np.testing.assert_allclose(
        stage_iii["seed_provenance"]["selected_phase_compositions"],
        stage_ii["held_stage_ii_replay_phase_compositions"],
    )
    assert diagnostics["exact_hessian_available"] is True
    assert diagnostics["hessian_approximation"] == "exact"
    assert diagnostics["route_hessian_approximation"] == "limited-memory"
    assert diagnostics["charge_balance"]["max_phase_charge_residual"] <= 1.0e-8
    assert diagnostics["transfer_residuals"]["status"] == "accepted"
    assert np.max(np.abs(result.phases["liquid1"].composition - result.phases["liquid2"].composition)) > 1.0e-8


def test_electrolyte_held2_public_route_checker_command_accepts_stage_ii_flag() -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(CHECKER_PATH),
            "--json",
            "--require-held2-stage-ii",
            "--require-stage-iii",
            "--require-postsolve-certification",
            "--require-public-admission",
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
