from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
from typing import Any

import pytest
from epcsaft_equilibrium._native import extension_native_core

REPO_ROOT = Path(__file__).resolve().parents[3]
REFERENCE_PATH = (
    REPO_ROOT / "analyses" / "reference_oracles" / "chemical_equilibrium" / "cantera_pope_reference_cases.json"
)
GENERATOR_PATH = REPO_ROOT / "analyses" / "reference_oracles" / "chemical_equilibrium" / "generate_reference_cases.py"
CHECKER_PATH = REPO_ROOT / "scripts" / "validation" / "check_standalone_ce_gate.py"

pytestmark = pytest.mark.native_contract


def _module_from_path(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _reference_payload() -> dict[str, Any]:
    assert REFERENCE_PATH.exists(), "retained CE reference oracle JSON is missing"
    return json.loads(REFERENCE_PATH.read_text(encoding="utf-8"))


def test_reference_oracle_fixture_retains_cantera_and_pope_ce_only_records() -> None:
    payload = _reference_payload()

    assert payload["schema_version"] == "epcsaft.ce_reference_oracles.v1"
    assert payload["scope"] == "standalone_chemical_equilibrium_only"
    assert payload["runtime_dependencies"] == []
    cases = {case["case_id"]: case for case in payload["cases"]}
    assert set(cases) == {
        "cantera_compatible_ideal_a_to_b",
        "pope_2004_tiny_species_ideal_a_to_b",
    }

    for case in cases.values():
        assert case["ce_only"] is True
        assert case["phase_scope"] == "homogeneous_single_phase"
        assert case["claimed_equilibrium_scopes"] == ["standalone_chemical_equilibrium"]
        assert case["oracle_role"] == "reference_only"
        assert case["solver"]["runtime_dependency"] == "none"
        assert case["species_order"] == [species["label"] for species in case["reaction_set"]["species"]]
        assert case["balances"]["conservation_labels"]
        assert case["balances"]["balance_inf_norm"] <= case["tolerances"]["balance_abs"]
        assert case["affinities"]["reaction_labels"]
        assert case["affinities"]["stationarity_inf_norm"] <= case["tolerances"]["affinity_abs"]
        assert set(case["expected"]) >= {"amounts", "mole_fractions"}
        assert sum(case["expected"]["amounts"]) == pytest.approx(sum(case["reaction_set"]["feed_amounts"].values()))


def test_reference_oracle_generator_reproduces_retained_json() -> None:
    payload = _reference_payload()
    generator = _module_from_path("generate_ce_reference_cases", GENERATOR_PATH)

    assert generator.build_reference_payload() == payload


def test_checker_rejects_oracle_records_that_claim_phase_or_cpe_scope() -> None:
    checker = _module_from_path("check_standalone_ce_gate", CHECKER_PATH)
    payload = _reference_payload()
    bad_payload = copy.deepcopy(payload)
    bad_payload["cases"][0]["ce_only"] = False
    bad_payload["cases"][0]["phase_scope"] = "reactive_lle"
    bad_payload["cases"][0]["claimed_equilibrium_scopes"].append("coupled_phase_chemical_equilibrium")

    blockers = checker.reference_oracle_payload_blockers(bad_payload)

    assert "cantera_compatible_ideal_a_to_b_not_ce_only" in blockers
    assert "cantera_compatible_ideal_a_to_b_phase_scope_not_homogeneous_single_phase" in blockers
    assert "cantera_compatible_ideal_a_to_b_claims_non_ce_scope" in blockers


def test_standalone_ce_gate_consumes_reference_oracles_through_single_nlp_path() -> None:
    if not extension_native_core()._native_ipopt_smoke()["compiled"]:
        pytest.skip("native Ipopt is not compiled")

    checker = _module_from_path("check_standalone_ce_gate", CHECKER_PATH)
    report = checker.evaluate_standalone_ce_gate(
        require_single_nlp_path=True,
        require_oracles=True,
    )

    assert report["status"] == "complete"
    assert report["blockers"] == []
    oracle_evidence = report["oracle_evidence"]
    assert oracle_evidence["status"] == "complete"
    assert oracle_evidence["case_count"] == 2
    for case in oracle_evidence["cases"]:
        assert case["ce_only"] is True
        assert case["activation_family"] == "reactive_speciation"
        assert case["native_binding"] == "_native_chemical_equilibrium_nlp_activation"
        assert case["solver_backend"] == "ipopt"
        assert case["uses_homogeneous_ce_block"] is True
        assert case["amount_error_inf_norm"] <= case["tolerances"]["amount_abs"]
        assert case["balance_inf_norm"] <= case["tolerances"]["balance_abs"]
        assert case["reaction_stationarity_inf_norm"] <= case["tolerances"]["affinity_abs"]
