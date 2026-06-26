from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest
from epcsaft_equilibrium._native import extension_native_core

REPO_ROOT = Path(__file__).resolve().parents[3]
CHECKER_PATH = REPO_ROOT / "scripts" / "validation" / "check_standalone_ce_gate.py"

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
