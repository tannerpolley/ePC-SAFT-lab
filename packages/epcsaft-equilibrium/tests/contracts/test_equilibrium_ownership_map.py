from __future__ import annotations

import re
from copy import deepcopy
from dataclasses import asdict
from pathlib import Path

import epcsaft_equilibrium.capability_evidence as capability_evidence
import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[4]
PRESERVATION_MANIFEST = (
    REPO_ROOT
    / "docs"
    / "superpowers"
    / "milestones"
    / "M4-equilibrium"
    / "equilibrium-preservation-manifest.yaml"
)

OWNER_FIELDS = {
    "request_owner",
    "condition_resolution_owner",
    "activation_owner",
    "formulation_owner",
    "nlp_owner",
    "solver_owner",
    "discovery_owner",
    "certification_owner",
    "result_owner",
    "binding_owner",
}
PRESERVATION_DECISIONS = {
    "preserve_directly",
    "preserve_concept_rewrite_owner",
    "validation_only",
    "retire",
}
VALUABLE_RESPONSIBILITIES = {
    "public_pressure_boundary_routes",
    "public_single_component_saturation",
    "local_nlp_and_ipopt_adapter",
    "exact_phase_derivatives",
    "association_mass_action_and_implicit_derivatives",
    "neutral_phase_discovery_and_local_refinement",
    "electrolyte_electroneutral_and_counterion_pair_components",
    "native_postsolve_certification",
    "standalone_chemical_equilibrium_schema_and_local_nlp",
}


def _ownership_records() -> dict[str, dict[str, object]]:
    records = getattr(capability_evidence, "EQUILIBRIUM_OWNERSHIP_BY_ID", None)
    assert isinstance(records, dict) and records
    return records


def _preservation_payload() -> dict[str, object]:
    assert PRESERVATION_MANIFEST.is_file()
    payload = yaml.safe_load(PRESERVATION_MANIFEST.read_text(encoding="utf-8"))
    assert isinstance(payload, dict)
    return payload


def _repo_path(value: str) -> Path:
    return REPO_ROOT / value.partition("::")[0]


def test_ownership_records_follow_the_documented_m0_contract_without_machine_gate() -> None:
    records = _ownership_records()
    validate = getattr(capability_evidence, "validate_equilibrium_ownership_records", None)
    validate_paths = getattr(capability_evidence, "validate_equilibrium_ownership_paths", None)
    assert callable(validate)
    assert callable(validate_paths)
    validate(records)
    validate_paths(REPO_ROOT, records)

    public_route_owners: dict[str, str] = {}
    for record_id, record in records.items():
        assert record["record_id"] == record_id
        assert record["package"] == "epcsaft-equilibrium"
        assert record["milestone"] == "M4 - Equilibrium"
        assert record["responsibility"]
        assert record["supported_scope"]
        assert set(record) >= OWNER_FIELDS
        for field in OWNER_FIELDS:
            assert isinstance(record[field], str)
            assert record[field]
        assert record["proof_nodes"]
        assert isinstance(record["strict_checkers"], tuple)
        assert isinstance(record["retained_artifacts"], tuple)

        if record["visibility"] == "production":
            assert record["public_entrypoint"]
            assert record["public_routes"]
            for route in record["public_routes"]:
                assert route not in public_route_owners
                public_route_owners[str(route)] = record_id
        else:
            assert record["visibility"] in {"internal_validation", "declared_not_exposed"}
            assert record["public_routes"] == ()
            assert str(record["public_entrypoint"]).startswith("not_applicable:")

    assert set(public_route_owners) == {
        "bubble_pressure",
        "dew_pressure",
        "single_component_vle",
    }


def test_ownership_validator_rejects_missing_duplicate_or_misplaced_owners() -> None:
    validate = getattr(capability_evidence, "validate_equilibrium_ownership_records", None)
    assert callable(validate)
    records = _ownership_records()

    missing = deepcopy(records)
    missing["public_pressure_boundary_routes"].pop("solver_owner")
    with pytest.raises(RuntimeError, match="solver_owner"):
        validate(missing)

    duplicate_route = deepcopy(records)
    duplicate_route["public_single_component_saturation"]["public_routes"] = (
        "single_component_vle",
        "bubble_pressure",
    )
    with pytest.raises(RuntimeError, match="duplicate_public_route_owner:bubble_pressure"):
        validate(duplicate_route)

    multiple_solver_owners = deepcopy(records)
    multiple_solver_owners["public_pressure_boundary_routes"]["solver_owner"] = (
        "first.cpp",
        "second.cpp",
    )
    with pytest.raises(RuntimeError, match="exactly_one_owner"):
        validate(multiple_solver_owners)

    discovery_owned_acceptance = deepcopy(records)
    discovery_owned_acceptance["electrolyte_equilibrium_components"]["certification_owner"] = (
        discovery_owned_acceptance["electrolyte_equilibrium_components"]["discovery_owner"]
    )
    with pytest.raises(RuntimeError, match="discovery_owned_certification"):
        validate(discovery_owned_acceptance)

    paper_runtime_owner = deepcopy(records)
    paper_runtime_owner["standalone_chemical_equilibrium_components"]["formulation_owner"] = (
        "analyses/paper_validation/2023_ascani/program.py"
    )
    with pytest.raises(RuntimeError, match="non_package_runtime_owner"):
        validate(paper_runtime_owner)

    missing_package_owner = deepcopy(records)
    missing_package_owner["public_pressure_boundary_routes"]["solver_owner"] = (
        "packages/epcsaft-equilibrium/src/epcsaft_equilibrium/missing.cpp"
    )
    with pytest.raises(RuntimeError, match="missing equilibrium ownership target"):
        capability_evidence.validate_equilibrium_ownership_paths(
            REPO_ROOT, missing_package_owner
        )

    empty_public_entrypoint = deepcopy(records)
    empty_public_entrypoint["public_pressure_boundary_routes"]["public_entrypoint"] = ""
    with pytest.raises(RuntimeError, match="production_entrypoint_missing"):
        validate(empty_public_entrypoint)


def test_preservation_manifest_classifies_every_record_and_keeps_failed_outputs_non_normative() -> None:
    payload = _preservation_payload()
    records = _ownership_records()
    preservation_records = payload["records"]

    assert payload["schema_version"] == 1
    assert payload["package"] == "epcsaft-equilibrium"
    assert payload["milestone"] == "M4 - Equilibrium"
    assert payload["ownership_schema_basis"] == (
        "docs/contracts/ownership-and-maintainability.md#ownership-records"
    )
    assert set(payload["preservation_decisions"]) == PRESERVATION_DECISIONS
    assert set(record["decision"] for record in preservation_records) == PRESERVATION_DECISIONS
    assert VALUABLE_RESPONSIBILITIES <= {
        str(record["responsibility"]) for record in preservation_records
    }

    classified_ownership_ids = {
        str(ownership_id)
        for record in preservation_records
        for ownership_id in record["ownership_record_ids"]
    }
    assert classified_ownership_ids == set(records)

    preservation_by_id = {
        str(record["item_id"]): record for record in preservation_records
    }
    assert len(preservation_by_id) == len(preservation_records)
    expected_scientific_decisions = {
        "neutral_phase_discovery": "preserve_concept_rewrite_owner",
        "electrolyte_counterion_pair_components": "preserve_concept_rewrite_owner",
        "standalone_chemical_equilibrium_components": "preserve_concept_rewrite_owner",
        "failed_nonideal_mea_ce_output": "validation_only",
        "failed_khudaida_electrolyte_output": "validation_only",
        "misleading_held_and_held2_diagnostic_surface": "retire",
    }
    assert {
        item_id: preservation_by_id[item_id]["decision"]
        for item_id in expected_scientific_decisions
    } == expected_scientific_decisions

    assert payload["scientific_invariants"] == {
        "neutral_global_algorithm_identity": "held_incomplete_component_work",
        "held_stage_iii_canonical_objective": "direct_total_free_energy_minimization",
        "held_stage_iii_residual_solve_role": "optional_correction_or_diagnostic",
        "electrolyte_algorithm_identity": (
            "ascani_counterion_pair_not_perdomo_modified_mole_held2"
        ),
        "electrolyte_certificate_basis": (
            "independent_formulation_specific_modified_potential_or_mean_ionic"
        ),
        "individual_ion_equality_convention": "explicit_galvani_required",
        "chemical_equilibrium_family_boundary": "standalone_ce_separate_from_cpe",
        "failed_evidence_item_ids": [
            "failed_nonideal_mea_ce_output",
            "failed_khudaida_electrolyte_output",
        ],
        "retired_false_identity_item_ids": [
            "misleading_held_and_held2_diagnostic_surface"
        ],
    }
    assert preservation_by_id["misleading_held_and_held2_diagnostic_surface"][
        "desired_parity"
    ] is False

    for record in preservation_records:
        assert record["item_id"]
        assert record["responsibility"]
        assert record["decision"] in PRESERVATION_DECISIONS
        assert record["ownership_record_ids"]
        assert record["evidence_disposition"]
        assert record["evidence_refs"]
        assert record["scientific_guard"]
        assert record["migration_guard"]
        for path in record["evidence_refs"]:
            assert _repo_path(str(path)).exists(), f"missing evidence reference: {path}"
        inventory = record["checkpoint_inventory"]
        assert inventory["owner_paths"]
        assert inventory["caller_paths"]
        for field in ("owner_paths", "caller_paths", "binding_paths"):
            for path in inventory[field]:
                assert _repo_path(str(path)).exists(), f"missing {field}: {path}"
        for path in inventory.get("artifact_paths", ()):
            assert _repo_path(str(path)).exists(), f"missing artifact_paths: {path}"

    failed_evidence = [
        record
        for record in preservation_records
        if record["evidence_disposition"] == "failed_evidence"
    ]
    assert {record["item_id"] for record in failed_evidence} == {
        "failed_nonideal_mea_ce_output",
        "failed_khudaida_electrolyte_output",
    }
    assert all(record["decision"] == "validation_only" for record in failed_evidence)
    assert all(record["desired_parity"] is False for record in failed_evidence)


def test_manifest_records_checkpoint_identity_without_making_paths_a_stable_api() -> None:
    payload = _preservation_payload()
    checkpoint = payload["checkpoint"]
    receipt = getattr(capability_evidence, "EQUILIBRIUM_CHARACTERIZATION_RECEIPT", None)

    assert isinstance(receipt, dict)
    assert checkpoint["m0_machine_schema_state"] == (
        "documented_contract_only_not_activated"
    )
    assert checkpoint["m0_documented_contract_deviation"] == {
        "scope": "stage_3_characterization_only",
        "authorization_basis": (
            "user_requested_stage_3_completion_after_approving_all_bounded_designs"
        ),
        "limitation": "No claim of validation against a landed M0 machine schema or validator.",
        "extraction_gate": "activate_the_m0_machine_schema_before_stage_5_extraction",
    }
    assert checkpoint["native_source_manifest"] == (
        "packages/epcsaft-equilibrium/cmake/equilibrium_native_sources.json"
    )
    assert checkpoint["native_freshness_owner"] == "scripts/validation/native_freshness.py"
    assert checkpoint["build_refresh_command"] == receipt["build_refresh_command"]
    assert checkpoint["runtime_receipt_required_fields"] == list(
        receipt["runtime_receipt_required_fields"]
    )
    native_receipt = checkpoint["native_runtime_receipt"]
    assert set(checkpoint["runtime_receipt_required_fields"]) <= set(native_receipt)
    assert native_receipt["build_refresh_command"] == checkpoint["build_refresh_command"]
    assert native_receipt["freshness_mode"] == "embedded_source_identity"
    assert native_receipt["source_identity_matches"] is True
    assert native_receipt["current_source_identity"] == native_receipt[
        "embedded_source_identity"
    ]
    assert native_receipt["source_identity_algorithm"] == native_receipt[
        "embedded_source_identity_algorithm"
    ]
    assert native_receipt["source_identity_scope"] == native_receipt[
        "embedded_source_identity_scope"
    ]
    assert native_receipt["source_identity_file_count"] == native_receipt[
        "embedded_source_identity_file_count"
    ]
    assert len(native_receipt["current_source_identity"]) == 64
    assert len(checkpoint["direct_ipopt_application_owners"]) == 1
    direct_ipopt_owner = checkpoint["direct_ipopt_application_owners"][0]
    assert _repo_path(direct_ipopt_owner).is_file()
    local_nlp_inventory = next(
        record["checkpoint_inventory"]
        for record in payload["records"]
        if record["responsibility"] == "local_nlp_and_ipopt_adapter"
    )
    assert direct_ipopt_owner in local_nlp_inventory["owner_paths"]
    assert checkpoint["path_inventory_role"] == "refreshable_checkpoint_evidence_not_stable_api"
    assert receipt["public_routes_unchanged"] == (
        "bubble_pressure",
        "dew_pressure",
        "single_component_vle",
    )


def test_checkpoint_symbol_binding_serializer_and_default_inventories_match_source() -> None:
    checkpoint = _preservation_payload()["checkpoint"]

    for record in checkpoint["symbol_inventory"]:
        owner = _repo_path(str(record["owner_path"]))
        source = owner.read_text(encoding="utf-8")
        assert record["symbols"]
        assert all(str(symbol) in source for symbol in record["symbols"])
        assert record["representative_caller_paths"]
        assert all(
            _repo_path(str(path)).is_file()
            for path in record["representative_caller_paths"]
        )

    bindings = checkpoint["binding_inventory"]
    actual_bindings: list[str] = []
    for source_path in bindings["source_paths"]:
        source = _repo_path(str(source_path)).read_text(encoding="utf-8")
        actual_bindings.extend(re.findall(r'm\.def\(\s*"([^"]+)"', source))
    assert actual_bindings == bindings["all_bindings"]
    assert len(actual_bindings) == bindings["total_binding_count"]
    assert bindings["public_execution_binding"] in actual_bindings
    assert bindings["nonproduction_binding_count"] == len(actual_bindings) - 1

    serializer_records = {
        str(record["concern"]): record
        for record in checkpoint["model_serializer_and_default_inventory"]
    }
    assert set(serializer_records) == {
        "provider_model_payload_consumer",
        "selector_request_serializer",
        "standalone_ce_schema_serializer",
        "solver_option_defaults",
        "derived_tolerance_defaults",
    }
    for record in serializer_records.values():
        source = _repo_path(str(record["owner_path"])).read_text(encoding="utf-8")
        assert all(str(symbol) in source for symbol in record["symbols"])

    provider_consumer = serializer_records["provider_model_payload_consumer"]
    binding_source = _repo_path(str(provider_consumer["owner_path"])).read_text(
        encoding="utf-8"
    )
    payload_parser = binding_source[
        binding_source.index("add_args native_args_from_payload") : binding_source.index(
            "add_args native_args_from_mixture_object"
        )
    ]
    actual_payload_fields = re.findall(
        r'required_native_arg_field<[^;]+?\(payload, "([^"]+)"\)',
        payload_parser,
        flags=re.S,
    )
    assert actual_payload_fields == provider_consumer["payload_fields"]
    assert provider_consumer["default_behavior"] == (
        "every_payload_field_is_required_no_equilibrium_default"
    )

    from epcsaft_equilibrium import workflows
    from epcsaft_equilibrium.core import native_requests

    assert asdict(workflows.EquilibriumSolverOptions()) == serializer_records[
        "solver_option_defaults"
    ]["defaults"]
    assert native_requests._CHEMICAL_POTENTIAL_TOLERANCE_FLOOR == serializer_records[
        "derived_tolerance_defaults"
    ]["defaults"]["chemical_potential_tolerance_floor"]
    assert native_requests._PHASE_DISTANCE_TOLERANCE_FLOOR == serializer_records[
        "derived_tolerance_defaults"
    ]["defaults"]["phase_distance_tolerance_floor"]


def test_direct_ipopt_application_calls_have_one_declared_owner() -> None:
    payload = _preservation_payload()
    declared_owners = set(payload["checkpoint"]["direct_ipopt_application_owners"])
    native_root = (
        REPO_ROOT
        / "packages"
        / "epcsaft-equilibrium"
        / "src"
        / "epcsaft_equilibrium"
        / "native"
        / "equilibrium"
    )
    application_tokens = ("IpoptApplicationFactory", "OptimizeTNLP")
    actual_owners = {
        path.relative_to(REPO_ROOT).as_posix()
        for path in native_root.rglob("*.cpp")
        if any(token in path.read_text(encoding="utf-8") for token in application_tokens)
    }

    assert actual_owners == declared_owners

    solve_adapter_callers = {
        path.relative_to(REPO_ROOT).as_posix()
        for path in native_root.rglob("*.cpp")
        if "solve_ipopt_nlp(" in path.read_text(encoding="utf-8")
        and path.relative_to(REPO_ROOT).as_posix() not in declared_owners
    }
    assert solve_adapter_callers == set(payload["checkpoint"]["solve_adapter_callers"])
