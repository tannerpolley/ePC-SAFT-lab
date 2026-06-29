from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
REGISTRY_PATH = (
    REPO_ROOT
    / "docs"
    / "superpowers"
    / "milestones"
    / "M4-equilibrium"
    / "registries"
    / "equilibrium-benchmark-registry.yaml"
)
PEREIRA_SOURCE_AUDIT_PATH = (
    REPO_ROOT / "data" / "reference" / "equilibrium_benchmarks" / "neutral_tp_flash" / "ethane_carbon_dioxide"
)


def _registry() -> dict[str, Any]:
    return yaml.safe_load(REGISTRY_PATH.read_text(encoding="utf-8"))


def _family_labels() -> set[str]:
    return {row["family_label"] for row in _registry()["family_rows"]}


def _benchmark_by_label() -> dict[str, dict[str, Any]]:
    return {case["case_label"]: case for case in _registry()["benchmark_cases"]}


def _neutral_flash_gate() -> dict[str, Any]:
    return _registry()["neutral_tp_flash_fixture_gate"]


def test_benchmark_registry_schema_v2_defines_nonproduction_evidence_tiers() -> None:
    registry = _registry()
    tiers = registry["evidence_tiers"]

    assert registry["schema_version"] == 2
    assert set(tiers) >= {"T0", "T1", "T2", "T3"}
    assert all(tier["production_eligible"] is False for tier in tiers.values())


def test_benchmark_cases_are_pe_focused_and_reference_known_families() -> None:
    family_labels = _family_labels()

    for benchmark in _registry()["benchmark_cases"]:
        assert benchmark["family_labels"], benchmark["case_label"]
        assert set(benchmark["family_labels"]) <= family_labels, benchmark["case_label"]
        assert all(label.startswith("PE-") for label in benchmark["family_labels"]), benchmark["case_label"]
        assert benchmark["priority_rank"] >= 1, benchmark["case_label"]
        assert benchmark["todo"], benchmark["case_label"]


def test_expected_pe_benchmark_ladder_is_declared() -> None:
    benchmarks = _benchmark_by_label()

    assert {
        "Hydrocarbon workbook derived TP flash",
        "Pereira 2012 System III",
        "Gross/Sadowski 2002 methanol/cyclohexane",
        "Khudaida 2026 electrolyte LLE",
        "Held 2014 Figure 6",
        "Ascani/Sadowski/Held 2022 mixed-solvent LLE",
    } <= set(benchmarks)

    assert benchmarks["Hydrocarbon workbook derived TP flash"]["family_labels"] == ["PE-Neutral TP Flash"]
    assert benchmarks["Hydrocarbon workbook derived TP flash"]["source_model_family"] == "PC-SAFT"
    assert benchmarks["Hydrocarbon workbook derived TP flash"]["fixture_status"] == "available"
    assert benchmarks["Hydrocarbon workbook derived TP flash"]["priority_rank"] == 1
    assert benchmarks["Pereira 2012 System III"]["family_labels"] == ["PE-Neutral TP Flash"]
    assert benchmarks["Pereira 2012 System III"]["source_model_family"] == "SAFT-VR"
    assert benchmarks["Pereira 2012 System III"]["current_fixture_blocker"] == "model_family_mismatch"
    assert benchmarks["Pereira 2012 System III"]["source_audit_path"] == (
        "data/reference/equilibrium_benchmarks/neutral_tp_flash/ethane_carbon_dioxide"
    )
    assert "ePC-SAFT-compatible neutral TP flash fixture" in benchmarks["Pereira 2012 System III"]["todo"]
    assert benchmarks["Gross/Sadowski 2002 methanol/cyclohexane"]["family_labels"] == [
        "PE-Associating TP Flash"
    ]
    assert benchmarks["Khudaida 2026 electrolyte LLE"]["priority_rank"] == 1
    assert benchmarks["Khudaida 2026 electrolyte LLE"]["status"] == (
        "held2_public_route_phase_discovery_admitted"
    )
    assert "Perdomo/Figiel validation" in benchmarks["Khudaida 2026 electrolyte LLE"]["todo"]
    assert "CE/CPE" in benchmarks["Khudaida 2026 electrolyte LLE"]["todo"]
    assert benchmarks["Held 2014 Figure 6"]["priority_rank"] == 2
    assert benchmarks["Ascani/Sadowski/Held 2022 mixed-solvent LLE"]["priority_rank"] == 3


def test_neutral_tp_flash_gate_defines_executable_fixture_contract() -> None:
    gate = _neutral_flash_gate()

    assert gate["target_family_label"] == "PE-Neutral TP Flash"
    assert gate["fixture_status"] == "executable_fixture_available"
    assert gate["accepted_source_model_families"] == ["PC-SAFT", "ePC-SAFT"]
    assert gate["rejected_context_cases"]["Pereira 2012 System III"]["source_model_family"] == "SAFT-VR"
    assert gate["rejected_context_cases"]["Pereira 2012 System III"]["blocker"] == "model_family_mismatch"

    required_fields = set(gate["executable_fixture_required_fields"])
    assert {
        "species",
        "pure_component_parameters",
        "binary_interactions",
        "temperature",
        "pressure",
        "feed_composition",
        "expected_phase_count",
        "expected_phase_compositions",
        "expected_phase_fractions",
        "source_model_family",
        "source_path",
        "acceptance_tolerances",
    } <= required_fields

    assert set(gate["phase_discovery_required"]) == {
        "deterministic_screening",
        "continuous_tpd_minimization",
        "held_stage_i_stability",
        "held_stage_ii_dual_phase_discovery",
        "held_stage_iii_ipopt_refinement",
    }


def test_local_source_audit_does_not_promote_context_to_fixture() -> None:
    gate = _neutral_flash_gate()
    local_candidates = {case["case_label"]: case for case in gate["local_source_audit"]}

    assert local_candidates["Gross/Sadowski 2001 binary VLE table"]["local_artifact"].endswith(
        "analyses/paper_validation/2001_gross/tables/table_005/table_005.csv"
    )
    assert (
        local_candidates["Gross/Sadowski 2001 binary VLE table"]["status"]
        == "insufficient_no_point_phase_split_fixture"
    )
    assert local_candidates["Hydrocarbon workbook TP flash smoke"]["local_artifact"].endswith(
        "data/reference/equilibrium_benchmarks/neutral_tp_flash/methane_ethane_propane/metadata.json"
    )
    assert local_candidates["Hydrocarbon workbook TP flash smoke"]["status"] == "promoted_executable_workbook_fixture"
    assert local_candidates["Pereira 2012 System III"]["status"] == "rejected_model_family_mismatch"
    assert local_candidates["Pereira 2012 System III"]["source_audit_path"] == (
        "data/reference/equilibrium_benchmarks/neutral_tp_flash/ethane_carbon_dioxide"
    )


def test_pereira_source_audit_fixture_is_nonexecutable_and_complete() -> None:
    metadata = json.loads((PEREIRA_SOURCE_AUDIT_PATH / "metadata.json").read_text(encoding="utf-8"))
    phase_text = (PEREIRA_SOURCE_AUDIT_PATH / "phase_splits.csv").read_text(encoding="utf-8")
    parameter_text = (PEREIRA_SOURCE_AUDIT_PATH / "saft_vr_parameters.csv").read_text(encoding="utf-8")
    phase_rows = list(csv.DictReader(phase_text.splitlines()))
    parameter_rows = list(csv.DictReader(parameter_text.splitlines()))

    assert metadata["name"] == "ethane_carbon_dioxide"
    assert metadata["family_label"] == "PE-Neutral TP Flash"
    assert metadata["fixture_status"] == "source_audited_not_executable"
    assert metadata["source_model_family"] == "SAFT-VR"
    assert metadata["runtime_model_support"] == "absent_from_epcsaft"
    assert {
        "model_family_mismatch",
        "saft_vr_runtime_absent",
        "published_second_feed_composition_not_normalized",
    } <= set(metadata["blocking_reasons"])

    by_case_phase = {(row["case_key"], row["phase"]): row for row in phase_rows}
    first_feed = by_case_phase[("system_iii_22325_09mpa", "feed")]
    assert first_feed["source_status"] == "reported"
    assert float(first_feed["composition_sum"]) == 1.0

    second_feed = by_case_phase[("system_iii_29315_61mpa", "feed")]
    assert second_feed["source_status"] == "published_feed_not_normalized"
    assert float(second_feed["composition_sum"]) == 0.10

    for phase in ("vapor", "liquid"):
        assert by_case_phase[("system_iii_22325_09mpa", phase)]["source_status"] == "reported"
        assert by_case_phase[("system_iii_29315_61mpa", phase)]["source_status"] == "reported"

    assert {row["component"] for row in parameter_rows} == {"ethane", "carbon_dioxide"}
    assert all(row["source_model_family"] == "SAFT-VR" for row in parameter_rows)
    assert all(row["source_status"] == "reported" for row in parameter_rows)


def test_pereira_material_balance_check_does_not_promote_fixture() -> None:
    metadata = json.loads((PEREIRA_SOURCE_AUDIT_PATH / "metadata.json").read_text(encoding="utf-8"))
    check_text = (PEREIRA_SOURCE_AUDIT_PATH / "material_balance_check.csv").read_text(
        encoding="utf-8"
    )
    correction_text = (PEREIRA_SOURCE_AUDIT_PATH / "feed_correction_candidates.csv").read_text(
        encoding="utf-8"
    )
    check_rows = {row["case_key"]: row for row in csv.DictReader(check_text.splitlines())}
    correction_rows = {row["case_key"]: row for row in csv.DictReader(correction_text.splitlines())}

    assert metadata["fixture_requirements"]["executable"] is False
    assert metadata["fixture_requirements"]["phase_discovery_required"] is True
    assert metadata["fixture_requirements"]["saft_vr_runtime_required"] is True
    assert metadata["fixture_requirements"]["source_confirmed_feed_correction_required"] is True

    first_case = check_rows["system_iii_22325_09mpa"]
    assert first_case["reported_feed_status"] == "normalized"
    assert first_case["material_balance_status"] == "feasible_from_reported_feed"
    assert float(first_case["vapor_fraction"]) == pytest.approx(0.927074, rel=1.0e-5)
    assert float(first_case["liquid_fraction"]) == pytest.approx(0.072926, rel=1.0e-5)
    assert float(first_case["max_abs_material_balance_residual"]) < 1.0e-12

    second_case = check_rows["system_iii_29315_61mpa"]
    assert second_case["reported_feed_status"] == "not_normalized"
    assert second_case["material_balance_status"] == "blocked_by_published_feed"
    assert second_case["fixture_eligible"] == "false"

    inferred_second = correction_rows["system_iii_29315_61mpa"]
    assert inferred_second["correction_status"] == "inferred_not_source_confirmed"
    assert float(inferred_second["candidate_x2"]) == pytest.approx(0.91)
    assert float(inferred_second["candidate_vapor_fraction"]) == pytest.approx(0.487365, rel=1.0e-5)


def test_hydrocarbon_workbook_fixture_is_declared_as_available() -> None:
    benchmark = _benchmark_by_label()["Hydrocarbon workbook derived TP flash"]
    source_path = REPO_ROOT / benchmark["source_path"]
    metadata = json.loads((source_path / "metadata.json").read_text(encoding="utf-8"))
    phase_rows = list(csv.DictReader((source_path / "phase_splits.csv").read_text(encoding="utf-8").splitlines()))
    parameter_rows = list(
        csv.DictReader((source_path / "pc_saft_parameters.csv").read_text(encoding="utf-8").splitlines())
    )
    interaction_rows = list(
        csv.DictReader((source_path / "binary_interactions.csv").read_text(encoding="utf-8").splitlines())
    )

    assert metadata["fixture_status"] == "source_backed_executable_fixture"
    assert metadata["source_model_family"] == "PC-SAFT"
    assert metadata["fixture_requirements"]["phase_discovery_required"] is True
    assert {row["phase"] for row in phase_rows} == {"feed", "liquid", "vapor"}
    feed = next(row for row in phase_rows if row["phase"] == "feed")
    assert float(feed["composition_sum"]) == pytest.approx(1.0)
    assert [float(feed[f"x{index}"]) for index in range(1, 4)] == pytest.approx(
        benchmark["feed_composition"]
    )
    assert {row["species"] for row in parameter_rows} == {"Methane", "Ethane", "Propane"}
    assert len(interaction_rows) == 3


def test_available_neutral_cases_must_have_full_fixture_contract() -> None:
    gate = _neutral_flash_gate()
    required_fields = set(gate["executable_fixture_required_fields"])

    for benchmark in _registry()["benchmark_cases"]:
        if "PE-Neutral TP Flash" not in benchmark["family_labels"]:
            continue
        if benchmark["fixture_status"] != "available":
            continue
        assert benchmark["source_model_family"] in gate["accepted_source_model_families"], benchmark["case_label"]
        assert required_fields <= set(benchmark), benchmark["case_label"]


def test_available_benchmark_source_paths_exist_and_source_needed_cases_have_todos() -> None:
    for benchmark in _registry()["benchmark_cases"]:
        if benchmark["fixture_status"] == "available":
            source_path = REPO_ROOT / benchmark["source_path"]
            assert source_path.exists(), benchmark["case_label"]
            continue

        assert benchmark["fixture_status"] == "source_data_needed", benchmark["case_label"]
        assert benchmark["status"] == "source_data_needed", benchmark["case_label"]
        assert benchmark["todo"], benchmark["case_label"]


def test_stale_deleted_plan_sources_are_not_referenced() -> None:
    registry_text = REGISTRY_PATH.read_text(encoding="utf-8")

    stale_paths = {
        "docs/superpowers/milestones/association_derivative_goal_plan.md",
        "docs/superpowers/milestones/gross2002_associating_vle_redo_plan.md",
        "docs/adr/0005-narrow-associating-bubble-pressure-admission.md",
    }

    for path in stale_paths:
        assert path not in registry_text


def test_domain_safety_policy_requires_all_three_layers() -> None:
    policy = _registry()["policy"]
    gates = set(_registry()["generalized_production_gates"])

    assert "route-owned bounds" in policy["domain_safety_policy"]
    assert "smooth VariableTransform wrapper" in policy["domain_safety_policy"]
    assert "Ipopt internal barrier" in policy["domain_safety_policy"]
    assert "permanent custom barrier" in policy["custom_barrier_policy"]

    assert {"route_domain_bounds", "variable_transform_chain_rule", "ipopt_barrier_bounds_constraints"} <= gates


def test_current_runtime_route_keys_are_excluded_from_generalized_families() -> None:
    registry = _registry()
    excluded = set(registry["excluded_current_runtime_route_keys"])
    family_labels = _family_labels()

    assert {"bubble_pressure", "bubble_temperature", "dew_pressure", "dew_temperature"} <= excluded
    assert not (excluded & family_labels)

    for row in registry["family_rows"]:
        assert row["family_label"] not in excluded


def test_ce_and_cpe_registry_placeholders_have_explicit_blocking_gates() -> None:
    rows = {row["family_label"]: row for row in _registry()["family_rows"]}
    ce = rows["CE Chemical Equilibrium Placeholder"]
    cpe = rows["CPE Combined Phase-Chemical Placeholder"]

    assert ce["phase_discovery_status"] == "not_applicable_homogeneous_single_phase"
    assert {
        "homogeneous_single_phase_only",
        "standard_state_registry",
        "reaction_affinity_certification",
        "exact_chemical_potential_derivatives",
    } <= set(ce["required_gates"])

    dependencies = cpe["activation_dependencies"]
    assert {
        "held_stage_ii_dual_phase_discovery",
        "held_stage_iii_ipopt_refinement",
        "postsolve_phase_set_certification",
    } <= set(dependencies["phase_equilibrium"])
    assert {
        "standard_state_registry",
        "reaction_affinity_certification",
        "exact_chemical_potential_derivatives",
    } <= set(dependencies["chemical_equilibrium"])
    assert "sequential_speciation_flash_as_simultaneous_cpe" in cpe["forbidden_shortcuts"]
