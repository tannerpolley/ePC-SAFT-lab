from __future__ import annotations

import copy
import importlib.util
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pytest

import epcsaft
import epcsaft_equilibrium

REPO_ROOT = Path(__file__).resolve().parents[3]
CHECKER_PATH = REPO_ROOT / "scripts" / "validation" / "check_electrolyte_public_admission.py"
CASE_DIR = REPO_ROOT / "data" / "reference" / "equilibrium_benchmarks" / "electrolyte_lle" / "water_ethanol_isobutanol_nacl"
PARAMETER_DIR = REPO_ROOT / "analyses" / "paper_validation" / "2026_khudaida" / "parameters"
SPECIES = ["H2O", "Ethanol", "Butanol", "Na+", "Cl-"]
FEED = [
    0.7295582904360921,
    0.013336215598851259,
    0.20495308450174898,
    0.026076204731653927,
    0.026076204731653927,
]


def _load_checker() -> Any:
    assert CHECKER_PATH.is_file(), f"missing checker: {CHECKER_PATH.relative_to(REPO_ROOT)}"
    spec = importlib.util.spec_from_file_location("check_electrolyte_public_admission", CHECKER_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _khudaida_public_mixture() -> epcsaft.Mixture:
    return epcsaft.Mixture.from_folder(
        PARAMETER_DIR,
        components=SPECIES,
        reference_temperature=293.15,
        reference_composition=FEED,
    )


def test_public_admission_requires_all_electrolyte_gates() -> None:
    checker = _load_checker()
    payload = checker.minimal_complete_payload_for_tests()

    for key, blocker in (
        ("source_gate", "source_gate_incomplete"),
        ("held2_readiness_gate", "readiness_gate_incomplete"),
        ("electrolyte_tpd_gate", "tpd_gate_incomplete"),
        ("held2_phase_discovery", "held2_phase_discovery_incomplete"),
        ("electrolyte_stage_iii_refinement", "stage_iii_refinement_incomplete"),
        ("electrolyte_postsolve_certification", "postsolve_certification_incomplete"),
    ):
        mutated = copy.deepcopy(payload)
        mutated[key]["complete"] = False
        mutated[key]["status"] = "incomplete"

        result = checker.evaluate_payload(
            mutated,
            require_source_gate=True,
            require_readiness_gate=True,
            require_tpd_gate=True,
            require_held2_discovery=True,
            require_stage_iii=True,
            require_postsolve_certification=True,
            require_public_admission=True,
        )

        assert result["complete"] is False
        assert blocker in result["blockers"]


def test_public_route_returns_certified_electrolyte_result() -> None:
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

    assert result.route == "electrolyte_lle"
    assert result.selector_route == "electrolyte_lle"
    assert result.problem_kind == "electrolyte_lle"
    assert result.phase_labels == ["liquid1", "liquid2"]
    assert result.z == pytest.approx(FEED, rel=0.0, abs=1.0e-12)
    assert result.diagnostics["public_admission"]["status"] == "accepted"
    assert result.diagnostics["postsolve_certification"]["accepted"] is True
    assert result.diagnostics["exact_hessian_available"] is True
    assert result.diagnostics["hessian_approximation"] == "exact"
    assert result.diagnostics["route_hessian_approximation"] == "limited-memory"
    assert result.diagnostics["charge_balance"]["max_phase_charge_residual"] <= 1.0e-8
    assert result.diagnostics["pressure_consistency"]["pressure_consistency_norm"] <= 1.0e-6
    assert result.diagnostics["domain_margins"]["phase_distance"] > result.diagnostics["domain_margins"][
        "phase_distance_tolerance"
    ]
    assert np.max(np.abs(result.phases["liquid1"].composition - result.phases["liquid2"].composition)) > 1.0e-8


def test_capabilities_distinguish_scope() -> None:
    capabilities = epcsaft_equilibrium.capabilities()
    activation = capabilities["activation_matrix"]

    assert activation["public_route_family_map"]["lle"] == "neutral_lle"
    assert activation["public_route_family_map"]["electrolyte_lle"] == "electrolyte_lle"
    assert "electrolyte_lle" in activation["production_families"]
    assert "reactive_electrolyte_lle" in activation["declared_not_exposed_families"]
    assert capabilities["electrolyte_lle"]["public_routes"] == ["electrolyte_lle"]
    assert "source-backed Khudaida 2026 NaCl mixed-solvent LLE" in capabilities["electrolyte_lle"]["input_scope"]
    assert "reactive_electrolyte_lle" not in capabilities


def test_registry_records_source_and_checker_chain() -> None:
    checker = _load_checker()
    payload = checker.minimal_complete_payload_for_tests()
    registry = payload["registry_evidence"]

    assert registry["source_fixture"] == "data/reference/equilibrium_benchmarks/electrolyte_lle/water_ethanol_isobutanol_nacl"
    assert registry["parameter_bundle"] == "analyses/paper_validation/2026_khudaida/parameters"
    assert registry["public_route_status"] == "public_route_open"
    assert registry["selector_family"] == "electrolyte_lle"
    assert registry["tolerances"]["charge_balance"] == pytest.approx(1.0e-8)
    assert registry["checker_chain"] == [
        "check_electrolyte_gfpe_gate.py",
        "check_electrolyte_held2_readiness.py",
        "check_electrolyte_tpd_gate.py",
        "check_electrolyte_held2_phase_discovery.py",
        "check_electrolyte_stage_iii_refinement.py",
        "check_electrolyte_postsolve_certification.py",
        "check_electrolyte_public_admission.py",
    ]


def test_unsupported_surfaces_remain_closed() -> None:
    checker = _load_checker()
    payload = checker.minimal_complete_payload_for_tests()

    result = checker.evaluate_payload(payload, require_public_admission=True)

    assert result["complete"] is True
    assert result["unsupported_surfaces"]["reactive_electrolyte_lle"] == "closed"
    assert result["unsupported_surfaces"]["reactive_lle"] == "closed"
    assert result["unsupported_surfaces"]["ce"] == "closed"
    assert result["unsupported_surfaces"]["cpe"] == "closed"
    assert result["unsupported_surfaces"]["regression"] == "closed"
    assert result["unsupported_surfaces"]["release_claim"] == "closed"


def test_parent_issue_closeout_evidence_is_current() -> None:
    checker = _load_checker()
    payload = checker.minimal_complete_payload_for_tests()

    result = checker.evaluate_payload(payload, require_parent_closeout=True, require_public_admission=True)

    assert result["complete"] is True
    assert result["parent_closeout"]["parent_issue"] == 191
    assert result["parent_closeout"]["remaining_m4_blockers"] == []
    assert result["parent_closeout"]["next_gate"] == "M6 issue #192 downstream electrolyte evidence"


def test_cli_requires_complete_electrolyte_public_admission() -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(CHECKER_PATH),
            "--json",
            "--require-source-gate",
            "--require-readiness-gate",
            "--require-tpd-gate",
            "--require-held2-discovery",
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
