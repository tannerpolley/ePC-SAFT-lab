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
MEA_RETAINED_SUMMARY_PATH = (
    REPO_ROOT
    / "analyses"
    / "paper_validation"
    / "standalone_ce"
    / "figures"
    / "mea_reactive_speciation_oracle_comparison"
    / "results"
    / "mea_ce_oracle_speciation_comparison_summary.json"
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
    retained_summary_path = MEA_RETAINED_SUMMARY_PATH.relative_to(REPO_ROOT).as_posix()

    assert payload["schema_version"] == "epcsaft.standalone_ce.validation_ladder.v1"
    assert payload["scope"] == "standalone_chemical_equilibrium_only"
    assert payload["claimed_equilibrium_scopes"] == ["standalone_chemical_equilibrium"]
    assert payload["public_routes"] == ["reactive_speciation"]
    assert payload["closed_surfaces"] == ["reactive_lle", "reactive_electrolyte_lle", "cpe"]
    assert payload["runtime_dependencies"] == []
    assert (
        payload["source_plan"]
        == "docs/superpowers/plans/2026-06-29-m4-ce-generic-pope-homotopy-continuation-plan.md"
    )
    assert {record["family_id"] for record in payload["validation_families"]} == {
        "analytic_ideal",
        "charged_conservation",
        "ascani_2023",
        "mea_speciation",
        "cantera_reference_oracle",
        "pope_reference_oracle",
    }
    mea = next(record for record in payload["validation_families"] if record["family_id"] == "mea_speciation")
    assert mea["evidence_role"] == "retained_no_oracle_public_reactive_speciation_sweep"
    assert mea["source"] == "MEA-Thermodynamics Smith-Missen Phase 1 retained fixture"
    assert mea["source_path"] == retained_summary_path
    assert mea["standard_state_metadata"]["activity_convention"] == "mole_fraction_activity"
    assert mea["temperature_C"] == [20.0, 40.0]
    assert mea["loading_count"] == 161
    assert mea["seed_policy"] == "max_min_feasible_interior_no_oracle"
    assert mea["uses_source_oracle_initial_amounts"] is False
    assert mea["solver_options"] == {"max_iterations": 1000, "tolerance": 1e-8}
    assert mea["residuals"]["state_point_count"] == 322
    assert mea["residuals"]["species_row_count"] == 3220
    assert mea["residuals"]["max_mole_fraction_abs_error"] <= 1.0e-8
    assert mea["residuals"]["max_balance_inf_norm"] <= mea["tolerances"]["balance_abs"]
    assert mea["residuals"]["max_reaction_stationarity_inf_norm"] <= mea["tolerances"]["affinity_abs"]
    continuation = mea["continuation_evidence"]
    assert continuation["max_stage_count"] == 3
    assert continuation["homotopy_point_count"] == 12
    assert continuation["physical_proof_corrector_point_count"] == 322
    assert continuation["all_final_lambda_one"] is True
    assert continuation["all_final_proof_accepted"] is True
    shuffled_subset = mea["shuffled_subset"]
    assert shuffled_subset["attempt_count"] == 34
    assert shuffled_subset["all_accepted"] is True
    assert shuffled_subset["all_no_source_oracle_seed"] is True
    assert payload["derivative_evidence"] == {
        "status": "complete",
        "backend": "analytic",
        "objective_gradient_exact": True,
        "constraint_jacobian_exact": True,
        "lagrangian_hessian_exact": True,
        "source": "packages/epcsaft-equilibrium/tests/native/diagnostics/test_chemical_equilibrium_nlp_activation.py",
    }
    assert payload["capability_evidence"] == {
        "status": "standalone_ce_open_cpe_closed",
        "activation_gate": "issue_0330_complete",
        "production": True,
        "public_routes": ["reactive_speciation"],
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
    bad_payload["capability_evidence"]["public_routes"] = ["reactive_lle"]

    blockers = checker.validation_ladder_payload_blockers(bad_payload)

    assert "validation_family_mea_speciation_missing" in blockers
    assert "derivative_evidence_lagrangian_hessian_not_exact" in blockers
    assert "capability_public_routes_mismatch" in blockers
    assert "capability_reactive_phase_route_claimed" in blockers


def test_standalone_ce_gate_rejects_source_seeded_or_weak_mea_validation_ladder_evidence() -> None:
    checker = _checker_module()
    payload = json.loads(STANDALONE_CE_SUMMARY_PATH.read_text(encoding="utf-8"))
    bad_payload = copy.deepcopy(payload)
    mea = next(record for record in bad_payload["validation_families"] if record["family_id"] == "mea_speciation")
    mea["evidence_role"] = "executable_public_reactive_speciation_sweep"
    mea["loading_count"] = 3
    mea["uses_source_oracle_initial_amounts"] = True
    mea["seed_policy"] = "source_oracle_mole_fraction_seed"
    mea["residuals"]["max_mole_fraction_abs_error"] = 1.0e-5
    mea["continuation_evidence"] = {}
    mea["shuffled_subset"] = {"attempt_count": 0, "all_accepted": False, "all_no_source_oracle_seed": False}

    blockers = checker.validation_ladder_payload_blockers(bad_payload)

    assert "validation_family_mea_speciation_evidence_role_mismatch" in blockers
    assert "validation_family_mea_speciation_source_oracle_seeded" in blockers
    assert "validation_family_mea_speciation_seed_policy_mismatch" in blockers
    assert "validation_family_mea_speciation_retained_loading_count_mismatch" in blockers
    assert "validation_family_mea_speciation_strict_gates_missing" in blockers
    assert "validation_family_mea_speciation_continuation_trace_missing" in blockers
    assert "validation_family_mea_speciation_shuffled_subset_missing" in blockers


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
    assert ladder["capability_evidence"]["public_routes"] == ["reactive_speciation"]
    mea = report["mea_speciation_evidence"]
    assert mea["status"] == "complete"
    assert mea["loading_grid"] == [0.1, 0.4, 0.8]
    assert mea["seed_policy"] == "max_min_feasible_interior_no_oracle"
    assert mea["uses_source_oracle_initial_amounts"] is False
    assert [row["loading_mol_co2_per_mol_mea"] for row in mea["rows"]] == [0.1, 0.4, 0.8]
    assert {row["accepted"] for row in mea["rows"]} == {True}
    assert {row["feasible_initialization_accepted"] for row in mea["rows"]} == {True}
    assert {row["uses_source_oracle_initial_amounts"] for row in mea["rows"]} == {False}
    assert {row["final_proof_status"] for row in mea["rows"]} == {"accepted"}
    assert {row["final_lambda"] for row in mea["rows"]} == {1.0}
    assert max(row["reaction_stationarity_inf_norm"] for row in mea["rows"]) <= mea["tolerances"]["affinity_abs"]
    retained = report["mea_retained_artifact_evidence"]
    assert retained["status"] == "complete"
    assert retained["artifact_path"] == MEA_RETAINED_SUMMARY_PATH.relative_to(REPO_ROOT).as_posix()
    assert retained["loading_count"] == 161
    assert retained["state_point_count"] == 322
    assert retained["strict_gates_passed"] is True
    assert retained["seed_policy"] == "max_min_feasible_interior_no_oracle"
    assert retained["uses_source_oracle_initial_amounts"] is False
    assert retained["continuation_evidence"]["all_final_lambda_one"] is True
    assert retained["continuation_evidence"]["all_final_proof_accepted"] is True


def test_standalone_ce_gate_requires_retained_robustness_diagnostics() -> None:
    checker = _checker_module()
    payload = json.loads(MEA_RETAINED_SUMMARY_PATH.read_text(encoding="utf-8"))
    bad_payload = copy.deepcopy(payload)
    bad_payload.pop("robustness_diagnostics", None)

    blockers = checker.mea_retained_summary_payload_blockers(bad_payload)

    assert "mea_retained_summary_robustness_diagnostics_missing" in blockers

    evidence = checker._mea_retained_artifact_evidence_from_payload(payload)
    robustness = evidence["robustness_diagnostics"]
    assert robustness["activity_model"] == "mole_fraction_activity"
    assert robustness["artifact"].endswith("mea_ce_unassisted_seed_audit.csv")
    assert "reaction_stationarity_inf_norm" in robustness["required_fields"]
    assert "balance_inf_norm" in robustness["required_fields"]
    assert "seed_source" in robustness["required_fields"]
    assert "stage_count" in robustness["required_fields"]
    assert "final_proof_status" in robustness["required_fields"]
    assert "failure_class" in robustness["required_fields"]
    assert robustness["failure_classes"] == ["accepted"]


def test_standalone_ce_gate_rejects_unclassified_retained_failures() -> None:
    checker = _checker_module()
    payload = json.loads(MEA_RETAINED_SUMMARY_PATH.read_text(encoding="utf-8"))
    bad_payload = copy.deepcopy(payload)
    bad_payload["robustness_diagnostics"]["failure_classes"] = ["accepted", "unclassified_failure"]

    blockers = checker.mea_retained_summary_payload_blockers(bad_payload)

    assert "mea_retained_summary_unclassified_failure_class" in blockers


def test_standalone_ce_gate_requires_physical_corrector_repair_evidence() -> None:
    checker = _checker_module()
    payload = json.loads(MEA_RETAINED_SUMMARY_PATH.read_text(encoding="utf-8"))
    bad_payload = copy.deepcopy(payload)
    bad_payload["ce_owned_continuation_trace"].pop("corrected_stationarity_point_count", None)

    blockers = checker.mea_retained_summary_payload_blockers(bad_payload)

    assert "mea_retained_summary_physical_corrector_repair_evidence_missing" in blockers

    evidence = checker._mea_retained_artifact_evidence_from_payload(payload)
    continuation = evidence["continuation_evidence"]
    assert continuation["corrected_stationarity_point_count"] >= 1
    assert continuation["max_initial_physical_proof_corrector_reaction_stationarity_inf_norm"] > 1.0e-6
    assert continuation["max_final_physical_proof_corrector_reaction_stationarity_inf_norm"] <= 1.0e-6
    assert continuation["max_final_physical_proof_corrector_balance_inf_norm"] <= 1.0e-8
    assert continuation["all_physical_proof_corrector_rejection_reasons_empty"] is True
