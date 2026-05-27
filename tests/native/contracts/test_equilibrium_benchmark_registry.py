from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
REGISTRY_PATH = REPO_ROOT / "docs" / "roadmaps" / "equilibrium_benchmark_registry.yaml"
PEREIRA_SOURCE_AUDIT_PATH = (
    REPO_ROOT / "data" / "reference" / "equilibrium_benchmarks" / "neutral_tp_flash" / "pereira_2012"
)


def _registry() -> dict[str, Any]:
    return yaml.safe_load(REGISTRY_PATH.read_text(encoding="utf-8"))


def _family_labels() -> set[str]:
    return {row["family_label"] for row in _registry()["family_rows"]}


def _benchmark_by_label() -> dict[str, dict[str, Any]]:
    return {case["case_label"]: case for case in _registry()["benchmark_cases"]}


def _stage10_gate() -> dict[str, Any]:
    return _registry()["stage10_neutral_tp_flash_source_gate"]


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
        "Pereira 2012 System III",
        "Gross/Sadowski 2002 methanol/cyclohexane",
        "Khudaida 2026 electrolyte LLE",
        "Held 2014 Figure 6",
        "Ascani/Sadowski/Held 2022 mixed-solvent LLE",
    } <= set(benchmarks)

    assert benchmarks["Pereira 2012 System III"]["family_labels"] == ["PE-Neutral TP Flash"]
    assert benchmarks["Pereira 2012 System III"]["source_model_family"] == "SAFT-VR"
    assert benchmarks["Pereira 2012 System III"]["current_fixture_blocker"] == "model_family_mismatch"
    assert benchmarks["Pereira 2012 System III"]["source_audit_path"] == (
        "data/reference/equilibrium_benchmarks/neutral_tp_flash/pereira_2012"
    )
    assert "ePC-SAFT-compatible neutral TP flash fixture" in benchmarks["Pereira 2012 System III"]["todo"]
    assert benchmarks["Gross/Sadowski 2002 methanol/cyclohexane"]["family_labels"] == [
        "PE-Associating TP Flash"
    ]
    assert benchmarks["Khudaida 2026 electrolyte LLE"]["priority_rank"] == 1
    assert benchmarks["Held 2014 Figure 6"]["priority_rank"] == 2
    assert benchmarks["Ascani/Sadowski/Held 2022 mixed-solvent LLE"]["priority_rank"] == 3


def test_stage10_neutral_tp_flash_gate_defines_executable_fixture_contract() -> None:
    gate = _stage10_gate()

    assert gate["target_family_label"] == "PE-Neutral TP Flash"
    assert gate["proof_status"] == "source_selection_blocked"
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

    assert set(gate["stage9_evidence_required"]) == {
        "deterministic_screening",
        "continuous_tpd_minimization",
        "held_stage_i_stability",
        "held_stage_ii_dual_phase_discovery",
        "held_stage_iii_ipopt_refinement",
    }


def test_stage10_local_source_audit_does_not_promote_context_to_proof() -> None:
    gate = _stage10_gate()
    local_candidates = {case["case_label"]: case for case in gate["local_source_audit"]}

    assert local_candidates["Gross/Sadowski 2001 binary VLE table"]["local_artifact"].endswith(
        "analyses/paper_validation/2001_gross/tables/table_005/table_005.csv"
    )
    assert (
        local_candidates["Gross/Sadowski 2001 binary VLE table"]["status"]
        == "insufficient_no_point_phase_split_fixture"
    )
    assert local_candidates["Hydrocarbon workbook TP flash smoke"]["status"] == "insufficient_package_smoke"
    assert local_candidates["Pereira 2012 System III"]["status"] == "rejected_model_family_mismatch"
    assert local_candidates["Pereira 2012 System III"]["source_audit_path"] == (
        "data/reference/equilibrium_benchmarks/neutral_tp_flash/pereira_2012"
    )


def test_pereira_stage10_source_audit_fixture_is_nonexecutable_and_complete() -> None:
    metadata = json.loads((PEREIRA_SOURCE_AUDIT_PATH / "metadata.json").read_text(encoding="utf-8"))
    phase_text = (PEREIRA_SOURCE_AUDIT_PATH / "phase_splits.csv").read_text(encoding="utf-8")
    parameter_text = (PEREIRA_SOURCE_AUDIT_PATH / "saft_vr_parameters.csv").read_text(encoding="utf-8")
    phase_rows = list(csv.DictReader(phase_text.splitlines()))
    parameter_rows = list(csv.DictReader(parameter_text.splitlines()))

    assert metadata["name"] == "pereira_2012_system_iii"
    assert metadata["family_label"] == "PE-Neutral TP Flash"
    assert metadata["proof_status"] == "source_audited_not_executable"
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


def test_available_neutral_stage10_cases_must_have_full_fixture_contract() -> None:
    gate = _stage10_gate()
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


def test_stale_deleted_roadmap_sources_are_not_referenced() -> None:
    registry_text = REGISTRY_PATH.read_text(encoding="utf-8")

    stale_paths = {
        "docs/roadmaps/association_derivative_goal_roadmap.md",
        "docs/roadmaps/gross2002_associating_vle_redo_plan.md",
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
