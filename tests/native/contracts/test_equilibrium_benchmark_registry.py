from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
REGISTRY_PATH = REPO_ROOT / "docs" / "roadmaps" / "equilibrium_benchmark_registry.yaml"


def _registry() -> dict[str, Any]:
    return yaml.safe_load(REGISTRY_PATH.read_text(encoding="utf-8"))


def _family_labels() -> set[str]:
    return {row["family_label"] for row in _registry()["family_rows"]}


def _benchmark_by_label() -> dict[str, dict[str, Any]]:
    return {case["case_label"]: case for case in _registry()["benchmark_cases"]}


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
    assert benchmarks["Gross/Sadowski 2002 methanol/cyclohexane"]["family_labels"] == [
        "PE-Associating TP Flash"
    ]
    assert benchmarks["Khudaida 2026 electrolyte LLE"]["priority_rank"] == 1
    assert benchmarks["Held 2014 Figure 6"]["priority_rank"] == 2
    assert benchmarks["Ascani/Sadowski/Held 2022 mixed-solvent LLE"]["priority_rank"] == 3


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
