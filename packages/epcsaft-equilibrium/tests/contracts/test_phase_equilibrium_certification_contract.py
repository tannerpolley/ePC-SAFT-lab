from __future__ import annotations

from copy import deepcopy

import epcsaft_equilibrium
from epcsaft_equilibrium.phase_equilibrium_certification import (
    validate_phase_equilibrium_certification_contracts,
)

REQUIRED_SHARED_CONTRACT_KEYS = {
    "acceptance_diagnostics_required",
    "activation",
    "certification_required",
    "constraint_families",
    "density_backend",
    "derivative_requirement",
    "display_name",
    "evidence_rows",
    "exposure_status",
    "family_residual_block",
    "postsolve_certification",
    "production_evidence_quantities",
    "production_exposed",
    "proof_routes",
    "public_routes",
    "residual_families",
    "selector_family",
    "stability_prelayer",
    "variable_model",
}


def test_certification_phase_equilibrium_payload_covers_all_public_routes() -> None:
    capabilities = epcsaft_equilibrium.capabilities()

    payload = capabilities["phase_equilibrium_certification"]
    certified_routes = sorted(
        route
        for contract in payload["production_route_contracts"]
        for route in contract["public_routes"]
    )

    assert certified_routes == capabilities["public_routes"]


def test_certification_phase_equilibrium_contracts_share_one_shape() -> None:
    payload = epcsaft_equilibrium.capabilities()["phase_equilibrium_certification"]
    contracts = payload["production_route_contracts"]

    assert contracts
    assert {contract["selector_family"] for contract in contracts} == set(payload["production_families"])
    for contract in contracts:
        assert REQUIRED_SHARED_CONTRACT_KEYS <= set(contract)
        assert contract["production_exposed"] is True
        assert contract["exposure_status"] == "production_exposed"
        assert contract["certification_required"] is True
        assert contract["acceptance_diagnostics_required"]


def test_certification_phase_equilibrium_keeps_planned_routes_declared() -> None:
    payload = epcsaft_equilibrium.capabilities()["phase_equilibrium_certification"]
    planned = payload["planned_route_families"]

    assert {row["selector_family"] for row in planned} >= {
        "reactive_lle",
        "reactive_electrolyte_lle",
        "reactive_speciation",
    }
    for row in planned:
        assert row["production_exposed"] is False
        assert row["public_routes"] == []


def test_certification_phase_equilibrium_rejects_planned_public_route_overclaim() -> None:
    payload = deepcopy(epcsaft_equilibrium.capabilities()["phase_equilibrium_certification"])
    reactive = next(row for row in payload["planned_route_families"] if row["selector_family"] == "reactive_lle")
    reactive["public_routes"] = ["reactive_lle"]

    blockers = validate_phase_equilibrium_certification_contracts(payload)

    assert "reactive_lle_planned_family_publishes_public_routes" in blockers


def test_certification_phase_equilibrium_rejects_missing_production_evidence() -> None:
    payload = deepcopy(epcsaft_equilibrium.capabilities()["phase_equilibrium_certification"])
    neutral_lle = next(
        contract
        for contract in payload["production_route_contracts"]
        if contract["selector_family"] == "neutral_lle"
    )
    neutral_lle["production_evidence_quantities"] = []

    blockers = validate_phase_equilibrium_certification_contracts(payload)

    assert "neutral_lle_production_evidence_quantities_missing" in blockers


def test_certification_phase_equilibrium_rejects_evidence_for_private_family() -> None:
    payload = deepcopy(epcsaft_equilibrium.capabilities()["phase_equilibrium_certification"])
    evidence = next(
        row
        for row in payload["evidence_rows"]
        if row["quantity"] == "electrolyte_lle_khudaida_public_admission"
    )
    evidence["selector_family"] = "reactive_electrolyte_lle"
    evidence["public_route"] = "reactive_electrolyte_lle"

    blockers = validate_phase_equilibrium_certification_contracts(payload)

    assert "electrolyte_lle_khudaida_public_admission_production_evidence_family_not_exposed" in blockers
    assert "electrolyte_lle_khudaida_public_admission_reactive_electrolyte_lle_evidence_route_not_public" in blockers
