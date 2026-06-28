from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path

import pytest
from epcsaft_equilibrium._native import extension_native_core

REPO_ROOT = Path(__file__).resolve().parents[3]
CHECKER_PATH = REPO_ROOT / "scripts" / "validation" / "check_standalone_ce_gate.py"
STANDALONE_CE_SUMMARY_PATH = (
    REPO_ROOT / "analyses" / "paper_validation" / "standalone_ce" / "shared" / "results" / "summary.json"
)

pytestmark = pytest.mark.native_contract


def _checker_module():
    spec = importlib.util.spec_from_file_location("check_standalone_ce_gate", CHECKER_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_standalone_ce_gate_requires_single_nlp_path() -> None:
    if not extension_native_core()._native_ipopt_smoke()["compiled"]:
        pytest.skip("native Ipopt is not compiled")

    checker = _checker_module()
    report = checker.evaluate_standalone_ce_gate(require_single_nlp_path=True)

    assert report["status"] == "complete"
    assert report["blockers"] == []
    assert report["single_nlp_path"] == {
        "activation_family": "reactive_speciation",
        "activation_compiler": "activation_plan",
        "native_binding": "_native_chemical_equilibrium_nlp_activation",
        "problem_name": "reactive_speciation_ideal_gibbs_nlp",
        "solver_backend": "ipopt",
        "uses_ipopt_adapter": True,
        "uses_homogeneous_ce_block": True,
        "side_channel_bindings_absent": True,
    }
    assert report["solution"]["amounts"] == pytest.approx([0.25, 0.75], abs=1.0e-7)
    assert report["solution"]["balance_inf_norm"] < 1.0e-9
    assert report["solution"]["reaction_stationarity_inf_norm"] < 1.0e-8


def test_standalone_ce_gate_rejects_missing_single_nlp_evidence() -> None:
    checker = _checker_module()
    report = {
        "single_nlp_path": {
            "activation_family": "reactive_speciation",
            "activation_compiler": "",
            "native_binding": "_native_chemical_equilibrium_nlp_activation",
            "problem_name": "reactive_speciation_ideal_gibbs_nlp",
            "solver_backend": "ipopt",
            "uses_ipopt_adapter": True,
            "uses_homogeneous_ce_block": True,
            "side_channel_bindings_absent": True,
        },
        "solver": {"solver_status": "success", "application_status": "solve_succeeded"},
        "solution": {"balance_inf_norm": 0.0, "reaction_stationarity_inf_norm": 0.0},
    }

    blockers = checker.single_nlp_path_blockers(report)

    assert "activation_compiler_mismatch" in blockers


def test_standalone_ce_validation_ladder_summary_retains_required_families_and_boundaries() -> None:
    payload = json.loads(STANDALONE_CE_SUMMARY_PATH.read_text(encoding="utf-8"))

    assert payload["schema_version"] == "epcsaft.standalone_ce.validation_ladder.v1"
    assert payload["scope"] == "standalone_chemical_equilibrium_only"
    assert payload["claimed_equilibrium_scopes"] == ["standalone_chemical_equilibrium"]
    assert payload["public_routes"] == []
    assert payload["closed_surfaces"] == ["reactive_lle", "reactive_electrolyte_lle", "cpe"]
    assert payload["runtime_dependencies"] == []
    assert {record["family_id"] for record in payload["validation_families"]} == {
        "analytic_ideal",
        "charged_conservation",
        "ascani_2023",
        "mea_speciation",
        "cantera_reference_oracle",
        "pope_reference_oracle",
    }
    assert payload["derivative_evidence"] == {
        "status": "complete",
        "backend": "analytic",
        "objective_gradient_exact": True,
        "constraint_jacobian_exact": True,
        "lagrangian_hessian_exact": True,
        "source": "packages/epcsaft-equilibrium/tests/native/diagnostics/test_chemical_equilibrium_nlp_activation.py",
    }
    assert payload["capability_evidence"] == {
        "status": "closed_until_activation_gate",
        "activation_gate": "issue_0330",
        "production": False,
        "public_routes": [],
        "closed_surfaces": ["reactive_lle", "reactive_electrolyte_lle", "cpe"],
    }


def test_standalone_ce_gate_rejects_missing_validation_ladder_evidence() -> None:
    checker = _checker_module()
    payload = json.loads(STANDALONE_CE_SUMMARY_PATH.read_text(encoding="utf-8"))
    bad_payload = copy.deepcopy(payload)
    bad_payload["validation_families"] = [
        record for record in bad_payload["validation_families"] if record["family_id"] != "mea_speciation"
    ]
    bad_payload["derivative_evidence"]["lagrangian_hessian_exact"] = False
    bad_payload["capability_evidence"]["public_routes"] = ["reactive_speciation"]

    blockers = checker.validation_ladder_payload_blockers(bad_payload)

    assert "validation_family_mea_speciation_missing" in blockers
    assert "derivative_evidence_lagrangian_hessian_not_exact" in blockers
    assert "capability_public_routes_claimed" in blockers


def test_standalone_ce_gate_complete_mode_consumes_validation_ladder() -> None:
    if not extension_native_core()._native_ipopt_smoke()["compiled"]:
        pytest.skip("native Ipopt is not compiled")

    checker = _checker_module()
    report = checker.evaluate_standalone_ce_gate(
        require_single_nlp_path=True,
        require_oracles=True,
        require_complete=True,
    )

    assert report["status"] == "complete"
    assert report["blockers"] == []
    ladder = report["validation_ladder"]
    assert ladder["status"] == "complete"
    assert ladder["family_count"] == 6
    assert ladder["families"] == [
        "analytic_ideal",
        "charged_conservation",
        "ascani_2023",
        "mea_speciation",
        "cantera_reference_oracle",
        "pope_reference_oracle",
    ]
    assert ladder["derivative_evidence"]["lagrangian_hessian_exact"] is True
    assert ladder["capability_evidence"]["public_routes"] == []
