from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
REGISTRY_PATH = REPO_ROOT / "docs" / "roadmaps" / "equilibrium_benchmark_registry.yaml"


def _registry() -> dict[str, Any]:
    return yaml.safe_load(REGISTRY_PATH.read_text(encoding="utf-8"))


def _rows_by_key() -> dict[str, dict[str, Any]]:
    return {row["key"]: row for row in _registry()["activation_rows"]}


def test_benchmark_registry_defines_evidence_tiers() -> None:
    tiers = _registry()["evidence_tiers"]

    assert set(tiers) >= {"T0", "T1", "T2", "T3"}
    assert tiers["T0"]["production_eligible"] is False
    assert tiers["T1"]["production_eligible"] is True
    assert tiers["T2"]["production_eligible"] is True
    assert tiers["T3"]["production_eligible"] is True


def test_every_proof_case_references_known_rows_and_evidence_tier() -> None:
    registry = _registry()
    rows = {row["key"] for row in registry["activation_rows"]}
    tiers = set(registry["evidence_tiers"])

    for row in registry["activation_rows"]:
        for proof in row["proof_cases"]:
            assert proof["evidence_tier"] in tiers, (row["key"], proof["key"])
            assert set(proof["rows"]) <= rows, (row["key"], proof["key"])
            assert proof["source"], (row["key"], proof["key"])
            assert proof["acceptance_checks"], (row["key"], proof["key"])


def test_source_data_needed_benchmarks_have_todos_and_are_not_production() -> None:
    rows = _rows_by_key()

    for benchmark in _registry()["benchmark_cases"]:
        if benchmark["status"] != "source_data_needed" and benchmark["fixture_status"] != "source_data_needed":
            continue

        assert benchmark["todo"], benchmark["key"]
        for row_key in benchmark["rows"]:
            assert rows[row_key]["production_exposed"] is False, (benchmark["key"], row_key)


def test_expected_missing_source_benchmark_entries_are_declared() -> None:
    benchmarks = {case["source_path"]: case for case in _registry()["benchmark_cases"]}

    expected_source_needed = {
        "analyses/paper_validation/2022_ascani_electrolyte_lle/",
        "analyses/paper_validation/2023_ascani_reactive_lle/",
        "analyses/paper_validation/2020_koulocheris_cpe/",
        "analyses/paper_validation/2019_tsanas_electrolyte_cpe/",
        "analyses/paper_validation/2022_tsanas_reactive_electrolyte_lle/",
        "analyses/paper_validation/2022_coatleven_xrr/",
        "analyses/paper_validation/2023_belov_ipopt_ce/",
        "analyses/paper_validation/2026_rezaee_lithium_des/",
    }

    assert expected_source_needed <= set(benchmarks)
    for source_path in expected_source_needed:
        assert benchmarks[source_path]["status"] == "source_data_needed"
        assert benchmarks[source_path]["fixture_status"] == "source_data_needed"


def test_no_row_claims_production_without_executable_proof() -> None:
    tiers = _registry()["evidence_tiers"]

    for row in _registry()["activation_rows"]:
        production_proofs = [
            proof
            for proof in row["proof_cases"]
            if tiers[proof["evidence_tier"]]["production_eligible"] and proof.get("fixture_status") == "available"
        ]

        if row["production_exposed"]:
            assert production_proofs, row["key"]
        else:
            assert row["activation_status"] != "production_exposed", row["key"]


def test_benchmark_cases_do_not_define_application_specific_public_apis() -> None:
    forbidden = {
        "fit_lithium_extraction_parameters",
        "calculate_extraction_efficiency",
        "fit_mea_absorption",
        "screen_lithium_extractants",
    }

    for row in _registry()["activation_rows"]:
        assert row["route_family"] not in forbidden, row["key"]
        assert row["variable_model"] not in forbidden, row["key"]
        for proof in row["proof_cases"]:
            assert proof["key"] not in forbidden, row["key"]
