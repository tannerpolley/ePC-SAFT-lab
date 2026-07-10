from __future__ import annotations

import csv
import subprocess
import sys
from copy import deepcopy
from pathlib import Path

import epcsaft_equilibrium
import epcsaft_equilibrium.workflows as equilibrium_workflows
import pytest
from epcsaft_equilibrium._native import extension_native_core
from epcsaft_equilibrium.capability_evidence import (
    CAPABILITY_EVIDENCE_BY_FAMILY,
    DEVELOPMENT_COMPONENT_EVIDENCE,
    PROOF_EVIDENCE_BY_ID,
    complete_evidence_families,
    production_capability_evidence,
    validate_proof_collection,
    validate_repo_evidence_targets,
)
from epcsaft_equilibrium.equilibrium_activation import (
    EQUILIBRIUM_PROOF_EXECUTION_RECEIPTS,
)
from epcsaft_equilibrium.workflows import _EQUILIBRIUM_ROUTE_SPECS

_core = extension_native_core()
REPO_ROOT = Path(__file__).resolve().parents[4]

PUBLIC_ROUTE_FAMILIES = {
    "bubble_pressure": "bubble_dew_derived_routes",
    "dew_pressure": "bubble_dew_derived_routes",
    "single_component_vle": "single_component_vle",
}
PRODUCTION_FAMILIES = {
    "bubble_dew_derived_routes",
    "single_component_vle",
}
CLOSED_UNPROVEN_FAMILIES = {
    "electrolyte_lle",
    "neutral_lle",
    "neutral_multiphase_nonassoc",
    "neutral_tp_flash",
    "reactive_electrolyte_lle",
    "reactive_lle",
    "reactive_speciation",
}


def _admitted_public_route_map(rows: list[dict[str, object]]) -> dict[str, str]:
    route_map: dict[str, str] = {}
    for row in rows:
        family_key = str(row["key"])
        if not bool(row["production_exposed"]):
            assert row["public_routes"] == []
            assert row["proof_routes"] == []
            continue
        for route in row["public_routes"]:
            assert str(route) not in route_map
            route_map[str(route)] = family_key
    return route_map


def test_generated_activation_mirror_matches_native_source_of_truth() -> None:
    try:
        from epcsaft_equilibrium.equilibrium_activation import (
            EQUILIBRIUM_ACTIVATION_MATRIX,
            EQUILIBRIUM_SELECTOR_ROUTE_CONTRACTS,
        )
    except ModuleNotFoundError as exc:
        pytest.fail(f"missing generated activation mirror: {exc}")

    assert EQUILIBRIUM_ACTIVATION_MATRIX == list(_core._native_equilibrium_activation_matrix())
    assert EQUILIBRIUM_SELECTOR_ROUTE_CONTRACTS == list(
        _core._native_equilibrium_selector_route_contracts()
    )


def test_native_selector_route_registry_is_route_granular_and_truthful() -> None:
    contracts = list(_core._native_equilibrium_selector_route_contracts())
    by_route = {str(contract["public_route"]): contract for contract in contracts}

    assert set(by_route) == {
        "bubble_pressure",
        "bubble_temperature",
        "dew_pressure",
        "dew_temperature",
        "flash",
        "lle",
        "single_component_vle",
    }
    assert {
        route: str(contract["selector_family"])
        for route, contract in by_route.items()
        if bool(contract["production_exposed"])
    } == PUBLIC_ROUTE_FAMILIES
    assert by_route["bubble_pressure"]["proof_routes"] == [
        "associating_neutral_vle_gross_2002_bubble_pressure_figures_2_9_public_exact_hessian"
    ]
    assert by_route["dew_pressure"]["proof_routes"] == [
        "associating_neutral_vle_gross_2002_dew_pressure_figures_2_9_public_exact_hessian"
    ]
    assert by_route["lle"]["proof_routes"] == []
    assert by_route["single_component_vle"]["proof_routes"] == [
        "single_component_vle_hydrocarbon_nist_saturation_exact_hessian"
    ]
    for route in ("bubble_temperature", "dew_temperature", "flash", "lle"):
        assert by_route[route]["production_exposed"] is False
        assert by_route[route]["proof_routes"] == []


def test_production_families_are_exactly_complete_evidence_families() -> None:
    native_rows = list(_core._native_equilibrium_activation_matrix())
    evidence = production_capability_evidence(native_rows)
    native_families = {
        str(row["key"])
        for row in native_rows
        if bool(row["production_exposed"])
    }

    assert native_families == PRODUCTION_FAMILIES
    assert set(evidence) == PRODUCTION_FAMILIES
    assert complete_evidence_families() == PRODUCTION_FAMILIES
    assert set(CAPABILITY_EVIDENCE_BY_FAMILY) == PRODUCTION_FAMILIES
    for family, record in evidence.items():
        assert record["family"] == family
        assert record["owner"] == "epcsaft-equilibrium / M4"
        assert record["public_entrypoint"]
        assert record["native_owner"]
        assert record["proof_nodes"]
        assert record["strict_checkers"]
        assert record["data_sources"]
        assert record["artifact_paths"]
        assert record["acceptance_metrics"]


def test_production_evidence_requires_passing_generated_checker_receipts() -> None:
    production_proof_ids = {
        proof_id
        for record in CAPABILITY_EVIDENCE_BY_FAMILY.values()
        for proof_id in record["proof_ids"]
    }
    assert set(EQUILIBRIUM_PROOF_EXECUTION_RECEIPTS) == production_proof_ids
    for proof_id in production_proof_ids:
        receipt = EQUILIBRIUM_PROOF_EXECUTION_RECEIPTS[proof_id]
        assert receipt["status"] == "passed"
        assert receipt["strict_checkers"] == list(PROOF_EVIDENCE_BY_ID[proof_id]["strict_checkers"])
        assert receipt["checker_receipts"]
        assert len(receipt["evidence_digest"]) == 64

    mutated = deepcopy(EQUILIBRIUM_PROOF_EXECUTION_RECEIPTS)
    proof_id = next(iter(production_proof_ids))
    mutated[proof_id]["status"] = "failed"
    with pytest.raises(RuntimeError, match="passing strict-checker execution receipt"):
        complete_evidence_families(execution_receipts=mutated)


def test_proof_ids_map_to_collected_nodes_and_complete_evidence() -> None:
    proof_nodes = {
        str(node)
        for proof in PROOF_EVIDENCE_BY_ID.values()
        if proof["admission"] == "production_complete"
        for node in proof["proof_nodes"]
    }
    test_files = sorted({node.partition("::")[0] for node in proof_nodes})
    completed = subprocess.run(
        [sys.executable, "-m", "pytest", "--collect-only", "-q", *test_files],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    collected_nodes = {
        line.strip()
        for line in completed.stdout.splitlines()
        if "::" in line
    }

    validate_proof_collection(collected_nodes)
    assert proof_nodes <= collected_nodes
    with pytest.raises(RuntimeError, match="uncollected proof nodes"):
        validate_proof_collection(collected_nodes - {next(iter(proof_nodes))})


def test_production_evidence_resolves_every_repo_owned_target() -> None:
    validate_repo_evidence_targets(REPO_ROOT)


def test_production_evidence_rejects_a_missing_repo_owned_target() -> None:
    mutated = deepcopy(PROOF_EVIDENCE_BY_ID)
    proof_id = "single_component_vle_hydrocarbon_nist_saturation_exact_hessian"
    mutated[proof_id]["artifact_paths"] = (
        *mutated[proof_id]["artifact_paths"],
        "analyses/package_validation/equilibrium_single_component_vle/missing-proof.csv",
    )

    with pytest.raises(RuntimeError, match=r"missing-proof\.csv"):
        validate_repo_evidence_targets(REPO_ROOT, proof_evidence=mutated)


def test_development_evidence_stays_visible_without_production_admission() -> None:
    evidence = {str(record["evidence_id"]): record for record in DEVELOPMENT_COMPONENT_EVIDENCE}

    assert {
        "neutral_tp_flash_hydrocarbon_workbook_component_check",
        "neutral_lle_sampled_candidate_validation",
        "bubble_temperature_hydrocarbon_inverse_component_check",
        "dew_temperature_hydrocarbon_inverse_component_check",
        "single_component_vle_pure_2b_source_scope",
    } <= set(evidence)
    for record in evidence.values():
        assert record["production_admissible"] is False
        assert record["blocking_reason"]
    assert "not a literature benchmark" in evidence[
        "neutral_tp_flash_hydrocarbon_workbook_component_check"
    ]["blocking_reason"]
    assert "sampled candidate" in evidence[
        "neutral_lle_sampled_candidate_validation"
    ]["blocking_reason"]
    assert "predictions" in evidence["single_component_vle_pure_2b_source_scope"][
        "blocking_reason"
    ]

    matsuda = PROOF_EVIDENCE_BY_ID[
        "neutral_lle_matsuda_2011_nist_sampled_candidate_diagnostic"
    ]
    assert matsuda["admission"] == "internal_validation"
    assert matsuda["artifact_paths"] == ()
    assert matsuda["acceptance_metrics"] == {
        "diagnostic_status": "internal_diagnostic_complete",
        "held_stage_ii_status": "sampled_candidate_audit_complete",
        "held_stage_ii_dual_loop_status": "not_performed",
        "phase_set_status": (
            "sampled_candidate_audit_complete_global_completeness_unproven"
        ),
        "candidate_completeness_accepted": False,
        "production_route_admitted": False,
        "global_phase_set_certified": False,
        "source_comparison_disposition": "validation_findings_only",
    }


def test_public_workflows_retain_no_associating_lle_admission_seam() -> None:
    assert not hasattr(equilibrium_workflows, "_has_gross_2002_associating_lle_proof")
    assert not hasattr(equilibrium_workflows, "_has_gross_2002_figure10_associating_lle_proof")


def test_single_component_vle_nist_artifact_is_an_exact_source_join() -> None:
    proof = PROOF_EVIDENCE_BY_ID[
        "single_component_vle_hydrocarbon_nist_saturation_exact_hessian"
    ]
    metrics = proof["acceptance_metrics"]
    result_path = REPO_ROOT / proof["artifact_paths"][0]
    with result_path.open(encoding="utf-8", newline="") as handle:
        result_rows = list(csv.DictReader(handle))

    reference_rows: dict[tuple[str, float], dict[str, str]] = {}
    for species in ("methane", "ethane", "propane"):
        path = (
            REPO_ROOT
            / "data/reference/pure_component/saturation_properties"
            / species
            / "saturation_properties.csv"
        )
        with path.open(encoding="utf-8", newline="") as handle:
            for row in csv.DictReader(handle):
                reference_rows[(str(row["species"]), float(row["T_K"]))] = row

    assert len(result_rows) == metrics["joined_source_row_count"] == len(reference_rows)
    assert {(str(row["species"]), float(row["T_K"])) for row in result_rows} == set(
        reference_rows
    )
    for row in result_rows:
        source = reference_rows[(str(row["species"]), float(row["T_K"]))]
        assert float(row["p_sat_nist_Pa"]) == pytest.approx(float(source["p_sat_Pa"]))
        assert float(row["rho_sat_liq_nist_kg_m3"]) == pytest.approx(
            float(source["rho_sat_liq_kg_m3"])
        )
        assert row["source"] == source["source"]
        assert row["route_status"] == "accepted"
        assert row["solver_status"] == "success"
        assert float(row["absolute_relative_error_percent"]) <= metrics[
            "max_pressure_absolute_relative_error_percent"
        ]
        assert float(row["rho_sat_liq_absolute_relative_error_percent"]) <= metrics[
            "max_liquid_density_absolute_relative_error_percent"
        ]
        assert float(row["pressure_consistency_norm"]) <= metrics[
            "max_pressure_consistency_norm"
        ]
        assert float(row["chemical_potential_consistency_norm"]) <= metrics[
            "max_chemical_potential_consistency_norm"
        ]
        assert float(row["phase_distance"]) >= metrics["min_phase_distance"]


def test_public_equilibrium_truth_contract_closes_unproven_families() -> None:
    capabilities = epcsaft_equilibrium.capabilities()
    rows = {str(row["key"]): row for row in capabilities["activation_matrix"]["rows"]}
    route_specs = {route: spec.selector_family for route, spec in _EQUILIBRIUM_ROUTE_SPECS.items()}

    assert set(capabilities["production_families"]) == PRODUCTION_FAMILIES
    assert capabilities["public_routes"] == sorted(PUBLIC_ROUTE_FAMILIES)
    assert capabilities["phase_equilibrium_certification"]["public_route_family_map"] == PUBLIC_ROUTE_FAMILIES
    assert route_specs == PUBLIC_ROUTE_FAMILIES

    for family in PRODUCTION_FAMILIES:
        assert capabilities[family]["selector_core"] is True
        assert capabilities[family]["evidence"] == capabilities["capability_evidence"][
            "production_records"
        ][family]

    production_contracts = capabilities["phase_equilibrium_certification"]["production_route_contracts"]
    assert {contract["selector_family"] for contract in production_contracts} == PRODUCTION_FAMILIES
    assert all(contract["production_evidence_quantities"] for contract in production_contracts)

    for family in CLOSED_UNPROVEN_FAMILIES:
        assert rows[family]["production_exposed"] is False
        assert rows[family]["exposure_status"] == "declared_not_exposed"
        assert rows[family]["proof_routes"] == []
        assert rows[family]["public_routes"] == []
        assert family not in capabilities

    assert not hasattr(epcsaft_equilibrium, "reactive_speciation")
    assert not hasattr(epcsaft_equilibrium, "ReactiveSpeciationResult")


def test_runtime_equilibrium_capabilities_are_activation_matrix_driven() -> None:
    native_rows = list(_core._native_equilibrium_activation_matrix())
    capabilities = epcsaft_equilibrium.capabilities()
    activation = capabilities["activation_matrix"]
    certification = capabilities["phase_equilibrium_certification"]

    assert activation["source"] == "native_cpp"
    assert activation["rows"] == native_rows
    assert activation["production_families"] == [
        "single_component_vle",
        "bubble_dew_derived_routes",
    ]
    assert activation["declared_not_exposed_families"] == [
        "neutral_tp_flash",
        "neutral_lle",
        "neutral_multiphase_nonassoc",
        "electrolyte_lle",
        "reactive_speciation",
        "reactive_lle",
        "reactive_electrolyte_lle",
    ]
    assert _admitted_public_route_map(native_rows) == PUBLIC_ROUTE_FAMILIES
    assert activation["public_routes"] == sorted(PUBLIC_ROUTE_FAMILIES)
    assert activation["public_route_family_map"] == PUBLIC_ROUTE_FAMILIES
    assert activation["public_routes_by_family"] == {
        "bubble_dew_derived_routes": ["bubble_pressure", "dew_pressure"],
        "single_component_vle": ["single_component_vle"],
    }

    assert certification["schema_version"] == 1
    assert certification["public_route_family_map"] == PUBLIC_ROUTE_FAMILIES
    assert certification["public_routes"] == sorted(PUBLIC_ROUTE_FAMILIES)
    assert [contract["selector_family"] for contract in certification["production_route_contracts"]] == [
        "single_component_vle",
        "bubble_dew_derived_routes",
    ]
    assert {row["selector_family"] for row in certification["planned_route_families"]} == {
        "neutral_tp_flash",
        "neutral_lle",
        "neutral_multiphase_nonassoc",
        "electrolyte_lle",
        "reactive_speciation",
        "reactive_lle",
        "reactive_electrolyte_lle",
    }


def test_exposed_family_capabilities_describe_only_selector_owned_routes() -> None:
    capabilities = epcsaft_equilibrium.capabilities()

    assert capabilities["bubble_dew_derived_routes"]["entrypoint"] == (
        "Equilibrium(mixture, route='bubble_pressure'/'dew_pressure', "
        "T=..., x=.../y=...).solve()"
    )
    assert capabilities["bubble_dew_derived_routes"]["public_routes"] == [
        "bubble_pressure",
        "dew_pressure",
    ]
    assert "neutral_tp_flash" not in capabilities
    assert "neutral_lle" not in capabilities
    assert capabilities["single_component_vle"]["entrypoint"] == (
        "Equilibrium(mixture, route='single_component_vle', T=...).solve()"
    )
    assert capabilities["single_component_vle"]["public_routes"] == ["single_component_vle"]
    assert capabilities["single_component_vle"]["input_scope"] == (
        "nonassociating methane, ethane, and propane within the retained NIST "
        "saturation-property ranges"
    )
    assert capabilities["problem_objects"] == {
        "available": True,
        "backend": "constructor_configured_frontend",
        "classes": ["EquilibriumProblem", "EquilibriumStructure"],
        "entrypoint": "Equilibrium(mixture, route=..., ...)",
    }

    for family in PRODUCTION_FAMILIES:
        assert capabilities[family]["available"] is capabilities["activation_matrix"]["ipopt_available"]
        assert capabilities[family]["selector_core"] is True


def test_closed_family_evidence_is_internal_and_carries_no_public_claim() -> None:
    rows = epcsaft_equilibrium.capabilities()["route_derivative_evidence"]["rows"]
    evidence = {row["quantity"]: row for row in rows}

    assert evidence["neutral_multiphase_nonassoc"]["classification"] == "internal_diagnostic_evidence"
    assert evidence["reactive_speciation_standalone_ce_validation"]["classification"] == (
        "internal_validation_evidence"
    )
    assert evidence["electrolyte_lle_khudaida_repair_evidence"]["classification"] == (
        "internal_validation_evidence"
    )

    closed_rows = [row for row in rows if row.get("selector_family") in CLOSED_UNPROVEN_FAMILIES]
    for row in closed_rows:
        assert row["classification"] != "production_supported"
        assert "public_route" not in row
        assert "public_admission_state" not in row

    associating_lle = evidence["associating_neutral_lle_gross_2002_internal_exact_hessian"]
    assert associating_lle["classification"] == "internal_validation_evidence"
    assert "public_route" not in associating_lle
    assert "public_admission_state" not in associating_lle
    assert associating_lle["component_pair"] == ["methanol", "cyclohexane"]
    assert associating_lle["k_ij"] == pytest.approx(0.051)
