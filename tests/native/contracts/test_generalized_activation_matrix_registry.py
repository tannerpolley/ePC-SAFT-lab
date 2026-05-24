from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
REGISTRY_PATH = REPO_ROOT / "docs" / "roadmaps" / "equilibrium_benchmark_registry.yaml"

REQUIRED_ROW_FIELDS = {
    "key",
    "category",
    "objective_family",
    "variable_model",
    "derivative_contract",
    "certification_families",
    "proof_cases",
}
REQUIRED_PROOF_FIELDS = {"evidence_tier", "source", "acceptance_checks", "rows"}
PRODUCTION_TIERS = {"T1", "T2", "T3"}


def _registry() -> dict[str, Any]:
    return yaml.safe_load(REGISTRY_PATH.read_text(encoding="utf-8"))


def _rows_by_key() -> dict[str, dict[str, Any]]:
    rows = _registry()["activation_rows"]
    return {row["key"]: row for row in rows}


def test_generalized_registry_declares_all_matrix_rows() -> None:
    rows = _rows_by_key()

    assert set(rows) >= {f"PE-{index:02d}" for index in range(1, 24)}
    assert set(rows) >= {f"CE-{index:02d}" for index in range(1, 20)}
    assert set(rows) >= {f"CPE-{index:02d}" for index in range(1, 25)}


def test_every_activation_row_has_required_schema_and_proof_case() -> None:
    for row in _rows_by_key().values():
        assert REQUIRED_ROW_FIELDS <= set(row), row["key"]
        assert row["certification_families"], row["key"]
        assert row["proof_cases"], row["key"]

        for proof in row["proof_cases"]:
            assert REQUIRED_PROOF_FIELDS <= set(proof), row["key"]
            assert proof["acceptance_checks"], row["key"]
            assert row["key"] in proof["rows"], row["key"]


def test_production_rows_require_executable_exact_postsolve_evidence() -> None:
    for row in _rows_by_key().values():
        if not row.get("production_exposed"):
            continue

        assert row["activation_status"] == "production_exposed", row["key"]
        assert row["exposure"] == "public", row["key"]
        assert "exact" in row["derivative_contract"], row["key"]
        assert "postsolve_checks" in row["certification_families"], row["key"]
        assert any(
            proof["evidence_tier"] in PRODUCTION_TIERS and proof.get("fixture_status") == "available"
            for proof in row["proof_cases"]
        ), row["key"]


def test_bubble_dew_route_keys_are_excluded_from_generalized_rows() -> None:
    registry = _registry()
    excluded = set(registry["excluded_derived_utility_route_keys"])

    for row in registry["activation_rows"]:
        assert row["key"] not in excluded
        assert row["route_family"] not in excluded


def test_hydrocarbon_flash_remains_mapped_to_pe_01() -> None:
    pe01 = _rows_by_key()["PE-01"]

    assert pe01["route_family"] == "neutral_tp_flash"
    assert any(
        proof["key"] == "hydrocarbon_tp_flash_reference"
        and proof["source"] == "tests/support/hydrocarbon_cases.py"
        and proof["rows"] == ["PE-01"]
        for proof in pe01["proof_cases"]
    )


def test_blocked_and_diagnostic_rows_are_not_public_production_routes() -> None:
    for row in _rows_by_key().values():
        if row["activation_status"] == "blocked_not_implemented":
            assert row["exposure"] != "public", row["key"]
            assert row["production_exposed"] is False, row["key"]

        if row["activation_status"] == "diagnostic_only":
            assert row["exposure"] == "internal", row["key"]
            assert row["production_exposed"] is False, row["key"]


def test_charged_rows_include_charge_and_electrochemical_certification() -> None:
    for row in _rows_by_key().values():
        if "charged" not in row.get("species_classes", []):
            continue

        certification = set(row["certification_families"])
        hard_constraints = set(row.get("hard_constraints", []))
        assert "charge_balance" in certification | hard_constraints, row["key"]
        assert (
            "electrochemical_potential_equality" in certification
            or "mean_ionic_fugacity_equality" in certification
        ), row["key"]


def test_reactive_rows_include_affinity_and_constant_convention_certification() -> None:
    for row in _rows_by_key().values():
        if "reactive" not in row.get("species_classes", []):
            continue

        certification = set(row["certification_families"])
        assert "reaction_affinity" in certification, row["key"]
        assert "reaction_constant_convention" in certification, row["key"]


def test_associating_rows_require_mass_action_and_reject_approx_final_production() -> None:
    for row in _rows_by_key().values():
        if "associating" not in row.get("species_classes", []):
            continue

        declared = set(row.get("hard_constraints", [])) | set(row["certification_families"])
        assert "association_mass_action" in declared, row["key"]
        assert "explicit_approx_final_production" in row.get("forbidden_shortcuts", []), row["key"]
