from __future__ import annotations

import copy
import importlib.util
import json
import math
import subprocess
import sys
from pathlib import Path

import pytest
import yaml
from epcsaft_equilibrium._native import extension_native_core

REPO_ROOT = Path(__file__).resolve().parents[3]
CHECKER_PATH = REPO_ROOT / "scripts" / "validation" / "check_standalone_ce_gate.py"
MEA_GENERATOR_PATH = (
    REPO_ROOT
    / "analyses"
    / "package_validation"
    / "standalone_ce"
    / "figures"
    / "mea_reactive_speciation_oracle_comparison"
    / "scripts"
    / "generate_data.py"
)
STANDALONE_CE_SUMMARY_PATH = (
    REPO_ROOT / "analyses" / "package_validation" / "standalone_ce" / "shared" / "results" / "summary.json"
)
MEA_RETAINED_SUMMARY_PATH = (
    REPO_ROOT
    / "analyses"
    / "package_validation"
    / "standalone_ce"
    / "figures"
    / "mea_reactive_speciation_oracle_comparison"
    / "output"
    / "mea_ce_oracle_speciation_comparison_summary.json"
)
STANDALONE_CE_ANALYSIS_PATH = REPO_ROOT / "analyses" / "package_validation" / "standalone_ce" / "analysis.yaml"

pytestmark = pytest.mark.native_contract


def _checker_module():
    spec = importlib.util.spec_from_file_location("check_standalone_ce_gate", CHECKER_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _mea_generator_module():
    spec = importlib.util.spec_from_file_location("generate_standalone_ce_mea_data", MEA_GENERATOR_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_standalone_ce_analysis_is_active_validation_not_a_production_claim() -> None:
    metadata = yaml.safe_load(STANDALONE_CE_ANALYSIS_PATH.read_text(encoding="utf-8"))
    retained = json.loads(STANDALONE_CE_SUMMARY_PATH.read_text(encoding="utf-8"))
    mea_retained = json.loads(MEA_RETAINED_SUMMARY_PATH.read_text(encoding="utf-8"))

    assert metadata["status"] == "active_validation"
    assert metadata["scope"]["public_routes"] == []
    assert metadata["scope"]["closed_surfaces"] == [
        "reactive_speciation",
        "reactive_lle",
        "reactive_electrolyte_lle",
        "cpe",
    ]
    assert metadata["commands"]["checker"] == [
        "uv run --no-sync python scripts/validation/check_standalone_ce_gate.py --json "
        "--require-single-nlp-path --require-oracles --require-complete"
    ]
    assert metadata["re_admission"]["required_status"] == "complete"
    assert metadata["re_admission"]["limits"] == {
        "balance_inf_norm_max": 1.0e-8,
        "reaction_stationarity_inf_norm_max": 1.0e-6,
    }
    assert metadata["current_evidence"]["status"] == "failing"
    retained_mea_family = next(
        record for record in retained["validation_families"] if record["family_id"] == "mea_speciation"
    )
    assert retained_mea_family["current_live_failure"] == mea_retained["current_live_failure"]
    for field, value in metadata["current_evidence"].items():
        if field != "status":
            assert value == mea_retained["current_live_failure"][field]

    assert retained["public_routes"] == []
    assert retained["closed_surfaces"] == [
        "reactive_speciation",
        "reactive_lle",
        "reactive_electrolyte_lle",
        "cpe",
    ]
    assert retained["validation_boundary"] == {
        "status": "active_validation",
        "activation_family": "reactive_speciation",
        "closed_surfaces": [
            "reactive_speciation",
            "reactive_lle",
            "reactive_electrolyte_lle",
            "cpe",
        ],
        "re_admission_limits": {
            "balance_inf_norm_max": 1.0e-8,
            "reaction_stationarity_inf_norm_max": 1.0e-6,
        },
    }
    assert "capability_evidence" not in retained
    assert mea_retained["validation_scope"] == "internal_standalone_ce"
    assert mea_retained["validation_entrypoint"] == "epcsaft_equilibrium.workflows._run_standalone_ce_validation"
    assert "public_route" not in mea_retained
    assert "ce_workflow" not in mea_retained


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
    assert payload["public_routes"] == []
    assert payload["closed_surfaces"] == [
        "reactive_speciation",
        "reactive_lle",
        "reactive_electrolyte_lle",
        "cpe",
    ]
    assert payload["runtime_dependencies"] == []
    assert (
        payload["source_plan"] == "docs/superpowers/plans/2026-06-29-m4-ce-generic-pope-homotopy-continuation-plan.md"
    )
    assert {record["family_id"] for record in payload["validation_families"]} == {
        "analytic_ideal",
        "charged_conservation",
        "ascani_2023",
        "mea_speciation",
        "cantera_reference_oracle",
        "pope_reference_oracle",
    }
    analytic = next(record for record in payload["validation_families"] if record["family_id"] == "analytic_ideal")
    assert analytic["status"] == "complete"
    mea = next(record for record in payload["validation_families"] if record["family_id"] == "mea_speciation")
    assert mea["status"] == "blocked_live_reproduction"
    assert mea["evidence_role"] == "retained_no_oracle_standalone_ce_diagnostic_sweep"
    assert mea["source"] == "MEA-Thermodynamics Smith-Missen Phase 1 retained fixture"
    assert mea["source_path"] == retained_summary_path
    assert mea["standard_state_metadata"]["activity_convention"] == "mole_fraction_activity"
    assert mea["temperature_C"] == [20.0, 40.0]
    assert mea["loading_count"] == 161
    assert mea["seed_policy"] == "max_min_feasible_interior_no_oracle"
    assert mea["uses_source_oracle_initial_amounts"] is False
    assert mea["solver_options"] == {"max_iterations": 1000, "tolerance": 1e-8}
    live_failure = mea["current_live_failure"]
    assert live_failure == {
        "temperature_C": 40.0,
        "loading_mol_co2_per_mol_mea": 0.4,
        "accepted": False,
        "failure_class": "balance_failure",
        "balance_inf_norm": pytest.approx(2.5999999998789356),
        "reaction_stationarity_inf_norm": pytest.approx(73.79118023038392),
        "balance_inf_norm_max": 1.0e-8,
        "reaction_stationarity_inf_norm_max": 1.0e-6,
        "captured_by": (
            "uv run --no-sync python analyses/package_validation/standalone_ce/figures/"
            "mea_reactive_speciation_oracle_comparison/scripts/generate_data.py"
        ),
    }
    assert live_failure["balance_inf_norm"] > live_failure["balance_inf_norm_max"]
    assert live_failure["reaction_stationarity_inf_norm"] > live_failure["reaction_stationarity_inf_norm_max"]
    assert mea["strict_gates_passed"] is False

    historical_residuals = mea["residuals"]
    assert historical_residuals["snapshot_status"] == "superseded_by_current_live_failure"
    assert historical_residuals["state_point_count"] == 322
    assert historical_residuals["species_row_count"] == 3220
    assert historical_residuals["max_mole_fraction_abs_error"] <= 1.0e-8
    assert historical_residuals["max_balance_inf_norm"] <= mea["tolerances"]["balance_abs"]
    assert historical_residuals["max_reaction_stationarity_inf_norm"] <= mea["tolerances"]["affinity_abs"]
    continuation = mea["continuation_evidence"]
    assert continuation["snapshot_status"] == "superseded_by_current_live_failure"
    assert continuation["max_stage_count"] == 3
    assert continuation["homotopy_point_count"] == 12
    assert continuation["physical_proof_corrector_point_count"] == 322
    assert continuation["all_final_lambda_one"] is True
    assert continuation["all_final_proof_accepted"] is True
    shuffled_subset = mea["shuffled_subset"]
    assert shuffled_subset["snapshot_status"] == "superseded_by_current_live_failure"
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
    assert payload["validation_boundary"] == {
        "status": "active_validation",
        "activation_family": "reactive_speciation",
        "closed_surfaces": [
            "reactive_speciation",
            "reactive_lle",
            "reactive_electrolyte_lle",
            "cpe",
        ],
        "re_admission_limits": {
            "balance_inf_norm_max": 1.0e-8,
            "reaction_stationarity_inf_norm_max": 1.0e-6,
        },
    }


def test_standalone_ce_gate_rejects_missing_validation_ladder_evidence() -> None:
    checker = _checker_module()
    payload = json.loads(STANDALONE_CE_SUMMARY_PATH.read_text(encoding="utf-8"))
    bad_payload = copy.deepcopy(payload)
    bad_payload["validation_families"] = [
        record for record in bad_payload["validation_families"] if record["family_id"] != "mea_speciation"
    ]
    bad_payload["derivative_evidence"]["lagrangian_hessian_exact"] = False
    bad_payload["validation_boundary"]["status"] = "complete"
    bad_payload["validation_boundary"]["closed_surfaces"] = ["reactive_lle"]

    blockers = checker.validation_ladder_payload_blockers(bad_payload)

    assert "validation_family_mea_speciation_missing" in blockers
    assert "derivative_evidence_lagrangian_hessian_not_exact" in blockers
    assert "validation_boundary_status_mismatch" in blockers
    assert "validation_boundary_closed_surfaces_mismatch" in blockers


def test_standalone_ce_gate_rejects_false_live_and_unlabelled_historical_mea_evidence() -> None:
    checker = _checker_module()
    payload = json.loads(STANDALONE_CE_SUMMARY_PATH.read_text(encoding="utf-8"))
    bad_payload = copy.deepcopy(payload)
    analytic = next(record for record in bad_payload["validation_families"] if record["family_id"] == "analytic_ideal")
    analytic["status"] = "blocked_live_reproduction"
    mea = next(record for record in bad_payload["validation_families"] if record["family_id"] == "mea_speciation")
    mea["status"] = "complete"
    mea["evidence_role"] = "executable_public_reactive_speciation_sweep"
    mea["loading_count"] = 3
    mea["uses_source_oracle_initial_amounts"] = True
    mea["seed_policy"] = "source_oracle_mole_fraction_seed"
    mea["strict_gates_passed"] = True
    mea["current_live_failure"] = {
        "loading_mol_co2_per_mol_mea": 0.5,
        "failure_class": "accepted",
        "balance_inf_norm": 0.0,
        "reaction_stationarity_inf_norm": 0.0,
        "balance_inf_norm_max": 1.0,
        "reaction_stationarity_inf_norm_max": 1.0,
    }
    mea["residuals"].pop("snapshot_status")
    mea["continuation_evidence"] = {}
    mea["shuffled_subset"] = {}

    blockers = checker.validation_ladder_payload_blockers(bad_payload)

    assert "validation_family_analytic_ideal_status_mismatch" in blockers
    assert "validation_family_mea_speciation_live_status_mismatch" in blockers
    assert "validation_family_mea_speciation_evidence_role_mismatch" in blockers
    assert "validation_family_mea_speciation_source_oracle_seeded" in blockers
    assert "validation_family_mea_speciation_seed_policy_mismatch" in blockers
    assert "validation_family_mea_speciation_retained_loading_count_mismatch" in blockers
    assert "validation_family_mea_speciation_residual_snapshot_status_mismatch" in blockers
    assert "validation_family_mea_speciation_live_failure_marked_accepted" in blockers
    assert "validation_family_mea_speciation_live_failure_temperature_mismatch" in blockers
    assert "validation_family_mea_speciation_live_failure_accepted_mismatch" in blockers
    assert "validation_family_mea_speciation_live_failure_loading_mismatch" in blockers
    assert "validation_family_mea_speciation_live_failure_class_mismatch" in blockers
    assert "validation_family_mea_speciation_live_balance_failure_missing" in blockers
    assert "validation_family_mea_speciation_live_stationarity_failure_missing" in blockers
    assert "validation_family_mea_speciation_live_balance_limit_mismatch" in blockers
    assert "validation_family_mea_speciation_live_stationarity_limit_mismatch" in blockers
    assert "validation_family_mea_speciation_continuation_snapshot_status_mismatch" in blockers
    assert "validation_family_mea_speciation_shuffled_snapshot_status_mismatch" in blockers


def test_standalone_ce_gate_retains_live_mea_rejection_without_traceback() -> None:
    if not extension_native_core()._native_ipopt_smoke()["compiled"]:
        pytest.skip("native Ipopt is not compiled")

    checker = _checker_module()
    report = checker.evaluate_standalone_ce_gate(
        require_single_nlp_path=True,
        require_oracles=True,
        require_complete=True,
    )

    assert report["status"] == "blocked"
    mea = report["mea_speciation_evidence"]
    assert mea["status"] == "blocked"
    rejected = [row for row in mea["rows"] if row.get("status") == "solver_rejected"]
    assert rejected
    assert {row["accepted"] for row in rejected} == {False}
    assert {row["failure_class"] for row in rejected} <= {
        "balance_failure",
        "stationarity_failure",
        "ipopt_failure",
    }
    assert max(row["balance_inf_norm"] for row in rejected) > mea["tolerances"]["balance_abs"]
    assert max(row["reaction_stationarity_inf_norm"] for row in rejected) > mea["tolerances"]["affinity_abs"]
    loading_point = next(row for row in rejected if row["loading_mol_co2_per_mol_mea"] == pytest.approx(0.4))
    assert loading_point["failure_class"] == "balance_failure"
    assert loading_point["balance_inf_norm"] == pytest.approx(2.5999999998789356)
    assert loading_point["reaction_stationarity_inf_norm"] == pytest.approx(73.79118023038392)


def test_standalone_ce_gate_cli_emits_blocked_json_for_live_mea_rejection() -> None:
    if not extension_native_core()._native_ipopt_smoke()["compiled"]:
        pytest.skip("native Ipopt is not compiled")

    completed = subprocess.run(
        [
            sys.executable,
            str(CHECKER_PATH),
            "--json",
            "--require-single-nlp-path",
            "--require-oracles",
            "--require-complete",
        ],
        check=False,
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 1
    assert completed.stderr == ""
    report = json.loads(completed.stdout)
    assert report["status"] == "blocked"
    assert report["mea_speciation_evidence"]["status"] == "blocked"
    retained = report["mea_retained_artifact_evidence"]
    assert retained["status"] == "complete"
    assert retained["validation_status"] == "blocked_live_reproduction"
    assert retained["strict_gates_passed"] is False
    assert retained["all_accepted"] is False
    assert retained["current_live_failure"]["loading_mol_co2_per_mol_mea"] == pytest.approx(0.4)
    assert retained["historical_snapshot"]["snapshot_status"] == "superseded_by_current_live_failure"
    assert report["mea_retained_live_crosscheck"] == {
        "status": "complete",
        "blockers": [],
        "loading_mol_co2_per_mol_mea": 0.4,
        "relative_tolerance": 1.0e-13,
        "absolute_tolerance": 1.0e-12,
    }


def test_standalone_ce_gate_requires_retained_robustness_diagnostics() -> None:
    checker = _checker_module()
    payload = json.loads(MEA_RETAINED_SUMMARY_PATH.read_text(encoding="utf-8"))
    bad_payload = copy.deepcopy(payload)
    bad_payload.pop("robustness_diagnostics", None)

    blockers = checker.mea_retained_summary_payload_blockers(bad_payload)

    assert "mea_retained_summary_robustness_diagnostics_missing" in blockers

    evidence = checker._mea_retained_artifact_evidence_from_payload(payload)
    robustness = evidence["robustness_diagnostics"]
    assert robustness["snapshot_status"] == "superseded_by_current_live_failure"
    assert robustness["activity_model"] == "mole_fraction_activity"
    assert robustness["artifact"].endswith("mea_ce_unassisted_seed_audit.csv")
    assert "reaction_stationarity_inf_norm" in robustness["required_fields"]
    assert "balance_inf_norm" in robustness["required_fields"]
    assert "seed_source" in robustness["required_fields"]
    assert "stage_count" in robustness["required_fields"]
    assert "final_proof_status" in robustness["required_fields"]
    assert "failure_class" in robustness["required_fields"]
    assert robustness["failure_classes"] == ["accepted", "balance_failure", "stationarity_failure"]
    assert robustness["accepted_state_point_count"] == 314
    assert robustness["state_point_count"] == 322


def test_standalone_ce_gate_reports_retained_artifact_review_digest() -> None:
    checker = _checker_module()
    payload = json.loads(MEA_RETAINED_SUMMARY_PATH.read_text(encoding="utf-8"))

    evidence = checker._mea_retained_artifact_evidence_from_payload(payload)
    assert evidence["status"] == "complete"
    assert evidence["validation_status"] == "blocked_live_reproduction"
    assert evidence["strict_gates_passed"] is False
    assert evidence["all_accepted"] is False
    assert evidence["current_live_failure"] == payload["current_live_failure"]
    assert evidence["historical_snapshot"] == {
        "snapshot_status": "superseded_by_current_live_failure",
        "max_mole_fraction_abs_error": payload["max_abs_error"],
        "max_balance_inf_norm": payload["max_balance_inf_norm"],
        "max_reaction_stationarity_inf_norm": payload["max_reaction_stationarity_inf_norm"],
    }
    digest = evidence["artifact_review_digest"]

    assert digest["status"] == "complete"
    assert digest["artifact_count"] >= 2
    summary_digest = digest["artifacts"][MEA_RETAINED_SUMMARY_PATH.relative_to(REPO_ROOT).as_posix()]
    assert summary_digest["kind"] == "json"
    assert summary_digest["sha256"]
    assert summary_digest["top_level_keys"] == sorted(payload)

    robustness_artifact = payload["robustness_diagnostics"]["artifact"]
    robustness_digest = digest["artifacts"][robustness_artifact]
    assert robustness_digest["kind"] == "csv"
    assert robustness_digest["row_count"] == payload["robustness_diagnostics"]["state_point_count"]
    assert "failure_class" in robustness_digest["columns"]
    assert "reaction_stationarity_inf_norm" in robustness_digest["numeric_extrema"]
    stationarity = robustness_digest["numeric_extrema"]["reaction_stationarity_inf_norm"]
    assert stationarity["max"] == pytest.approx(payload["max_reaction_stationarity_inf_norm"])
    assert stationarity["max"] > checker.MEA_STRICT_TOLERANCES["affinity_abs"]


def test_standalone_ce_gate_rejects_unclassified_retained_failures() -> None:
    checker = _checker_module()
    payload = json.loads(MEA_RETAINED_SUMMARY_PATH.read_text(encoding="utf-8"))
    bad_payload = copy.deepcopy(payload)
    bad_payload["robustness_diagnostics"]["failure_classes"] = ["accepted", "unclassified_failure"]

    blockers = checker.mea_retained_summary_payload_blockers(bad_payload)

    assert "mea_retained_summary_unclassified_failure_class" in blockers


def test_standalone_ce_gate_rejects_false_live_status_and_unlabelled_historical_snapshots() -> None:
    checker = _checker_module()
    payload = json.loads(MEA_RETAINED_SUMMARY_PATH.read_text(encoding="utf-8"))
    bad_payload = copy.deepcopy(payload)
    bad_payload["validation_status"] = "complete"
    bad_payload["current_live_failure"] = {
        "loading_mol_co2_per_mol_mea": 0.5,
        "failure_class": "accepted",
        "balance_inf_norm": 0.0,
        "reaction_stationarity_inf_norm": 0.0,
        "balance_inf_norm_max": 1.0,
        "reaction_stationarity_inf_norm_max": 1.0,
    }
    bad_payload["all_solver_status_success"] = True
    bad_payload["all_application_status_succeeded"] = True
    bad_payload["all_accepted"] = True
    bad_payload["strict_gates_passed"] = True
    for section_name in (
        "pointwise_unassisted",
        "ce_owned_continuation_trace",
        "robustness_diagnostics",
        "shuffled_subset",
    ):
        bad_payload[section_name].pop("snapshot_status")

    blockers = checker.mea_retained_summary_payload_blockers(bad_payload)

    assert "mea_retained_summary_live_status_mismatch" in blockers
    assert "mea_retained_summary_live_failure_temperature_mismatch" in blockers
    assert "mea_retained_summary_live_failure_accepted_mismatch" in blockers
    assert "mea_retained_summary_live_failure_loading_mismatch" in blockers
    assert "mea_retained_summary_live_failure_class_mismatch" in blockers
    assert "mea_retained_summary_live_balance_failure_missing" in blockers
    assert "mea_retained_summary_live_stationarity_failure_missing" in blockers
    assert "mea_retained_summary_live_balance_limit_mismatch" in blockers
    assert "mea_retained_summary_live_stationarity_limit_mismatch" in blockers
    assert "mea_retained_summary_live_failure_marked_accepted" in blockers
    assert "mea_retained_summary_live_failure_marked_succeeded" in blockers
    assert "mea_retained_summary_pointwise_unassisted_snapshot_status_mismatch" in blockers
    assert "mea_retained_summary_ce_owned_continuation_trace_snapshot_status_mismatch" in blockers
    assert "mea_retained_summary_robustness_diagnostics_snapshot_status_mismatch" in blockers
    assert "mea_retained_summary_shuffled_subset_snapshot_status_mismatch" in blockers


def test_standalone_ce_gate_preserves_corrector_metrics_as_a_superseded_snapshot() -> None:
    checker = _checker_module()
    payload = json.loads(MEA_RETAINED_SUMMARY_PATH.read_text(encoding="utf-8"))

    evidence = checker._mea_retained_artifact_evidence_from_payload(payload)
    continuation = evidence["continuation_evidence"]
    assert continuation["snapshot_status"] == "superseded_by_current_live_failure"
    assert continuation["corrected_stationarity_point_count"] == 314
    assert continuation["max_initial_physical_proof_corrector_reaction_stationarity_inf_norm"] > 1.0e-6
    assert continuation["max_final_physical_proof_corrector_reaction_stationarity_inf_norm"] == pytest.approx(
        payload["current_live_failure"]["reaction_stationarity_inf_norm"]
    )
    assert continuation["max_final_physical_proof_corrector_balance_inf_norm"] == pytest.approx(
        payload["current_live_failure"]["balance_inf_norm"]
    )
    assert continuation["all_physical_proof_corrector_rejection_reasons_empty"] is False


def test_mea_generator_retains_the_live_40c_rejection() -> None:
    if not extension_native_core()._native_ipopt_smoke()["compiled"]:
        pytest.skip("native Ipopt is not compiled")

    generator = _mea_generator_module()
    outcome = generator._solve_state(
        species=generator._species(),
        reactions=generator._reactions(),
        temperature_C=40.0,
        loading=0.4,
    )

    assert outcome["result"] is None
    assert set(outcome["mole_fractions"]) == {
        *generator.SPECIES_ORDER,
        *generator.COMPOSITE_SPECIES,
    }
    assert all(math.isnan(value) for value in outcome["mole_fractions"].values())
    diagnostics = outcome["diagnostics"]
    assert diagnostics["accepted"] is False
    assert diagnostics["failure_class"] == "balance_failure"
    assert diagnostics["balance_inf_norm"] == pytest.approx(2.5999999998789356, abs=1.0e-12)
    assert diagnostics["reaction_stationarity_inf_norm"] == pytest.approx(73.79118023038392, abs=1.0e-12)


def test_mea_generator_derives_blocked_truth_metadata_from_the_fresh_trace() -> None:
    generator = _mea_generator_module()
    trace = generator.pd.DataFrame(
        [
            {
                "temperature_C": 40.0,
                "CO2_loading": 0.1,
                "accepted": True,
                "failure_class": "accepted",
                "balance_inf_norm": 1.0e-15,
                "reaction_stationarity_inf_norm": 1.0e-15,
            },
            {
                "temperature_C": 40.0,
                "CO2_loading": 0.4,
                "accepted": False,
                "failure_class": "balance_failure",
                "balance_inf_norm": 2.5999999998789356,
                "reaction_stationarity_inf_norm": 73.79118023038392,
            },
        ]
    )

    truth = generator._live_truth_metadata(trace)

    assert truth["validation_status"] == "blocked_live_reproduction"
    assert truth["snapshot_status"] == "superseded_by_current_live_failure"
    assert truth["current_live_failure"] == {
        "temperature_C": 40.0,
        "loading_mol_co2_per_mol_mea": 0.4,
        "accepted": False,
        "failure_class": "balance_failure",
        "balance_inf_norm": pytest.approx(2.5999999998789356),
        "reaction_stationarity_inf_norm": pytest.approx(73.79118023038392),
        "balance_inf_norm_max": 1.0e-8,
        "reaction_stationarity_inf_norm_max": 1.0e-6,
        "captured_by": generator.GENERATION_COMMAND,
    }


@pytest.mark.parametrize(
    ("field", "stale_value", "expected_blocker"),
    [
        (
            "loading_mol_co2_per_mol_mea",
            0.400001,
            "mea_retained_live_failure_loading_stale",
        ),
        ("failure_class", "stationarity_failure", "mea_retained_live_failure_class_stale"),
        ("accepted", True, "mea_retained_live_failure_accepted_stale"),
        ("balance_inf_norm", 2.600001, "mea_retained_live_failure_balance_stale"),
        (
            "reaction_stationarity_inf_norm",
            73.79118123038392,
            "mea_retained_live_failure_stationarity_stale",
        ),
    ],
)
def test_standalone_ce_gate_rejects_stale_retained_live_failure_fields(
    field: str,
    stale_value: object,
    expected_blocker: str,
) -> None:
    checker = _checker_module()
    retained = {
        "current_live_failure": {
            "temperature_C": 40.0,
            "loading_mol_co2_per_mol_mea": 0.4,
            "accepted": False,
            "failure_class": "balance_failure",
            "balance_inf_norm": 2.5999999998789356,
            "reaction_stationarity_inf_norm": 73.79118023038392,
        }
    }
    live = {
        "rows": [
            {
                "loading_mol_co2_per_mol_mea": 0.4,
                "status": "solver_rejected",
                "accepted": False,
                "failure_class": "balance_failure",
                "balance_inf_norm": 2.5999999998789356,
                "reaction_stationarity_inf_norm": 73.79118023038392,
            }
        ]
    }

    assert checker.retained_mea_live_comparison_blockers(retained, live) == []
    retained["current_live_failure"][field] = stale_value

    blockers = checker.retained_mea_live_comparison_blockers(retained, live)

    assert expected_blocker in blockers


def test_mea_generator_reproduces_checked_in_truth_deterministically() -> None:
    generated_names = (
        "source_oracle_speciation_curve.csv",
        "ce_reactive_speciation_curve.csv",
        "mea_ce_oracle_speciation_plot_data.csv",
        "mea_ce_oracle_speciation_errors.csv",
        "mea_ce_oracle_speciation_error_summary.csv",
        "mea_ce_continuation_trace_summary.csv",
        "mea_ce_unassisted_seed_audit.csv",
        "mea_ce_shuffled_subset_audit.csv",
        "smith_missen_reaction_constants.csv",
        "mea_ce_oracle_speciation_comparison_summary.json",
    )
    generated_paths = [MEA_RETAINED_SUMMARY_PATH.parent / name for name in generated_names]
    before = {path: path.read_bytes() for path in generated_paths}

    completed = subprocess.run(
        [sys.executable, str(MEA_GENERATOR_PATH)],
        check=False,
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=120,
    )

    assert completed.returncode == 0, completed.stderr
    after = {path: path.read_bytes() for path in generated_paths}
    assert after == before
    assert json.loads(completed.stdout) == json.loads(MEA_RETAINED_SUMMARY_PATH.read_text(encoding="utf-8"))
