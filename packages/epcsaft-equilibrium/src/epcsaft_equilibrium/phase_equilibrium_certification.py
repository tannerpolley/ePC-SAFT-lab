"""Shared phase-equilibrium production-route certification contracts."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

PRODUCTION_EVIDENCE_CLASSIFICATION = "production_supported"
PUBLIC_ROUTE_OPEN_STATE = "public_route_open"

_FAMILY_RESIDUAL_BLOCKS = {
    "bubble_dew_derived_routes": "boundary_vle",
    "electrolyte_lle": "electrolyte_lle",
    "neutral_lle": "lle",
    "neutral_multiphase_nonassoc": "flash_multiphase",
    "neutral_tp_flash": "flash",
    "single_component_vle": "vle",
}

_REQUIRED_CONTRACT_FIELDS = (
    "activation",
    "certification_required",
    "selector_family",
    "display_name",
    "production_exposed",
    "exposure_status",
    "public_routes",
    "proof_routes",
    "residual_families",
    "constraint_families",
    "variable_model",
    "density_backend",
    "derivative_requirement",
    "stability_prelayer",
    "postsolve_certification",
    "family_residual_block",
    "production_evidence_quantities",
)


def _as_list(value: object) -> list[object]:
    if value is None:
        return []
    if isinstance(value, (str, bytes)):
        return [value]
    if isinstance(value, Sequence):
        return list(value)
    return [value]


def _string_list(value: object) -> list[str]:
    return [str(item) for item in _as_list(value) if str(item)]


def _rows(value: object) -> list[dict[str, object]]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        return []
    return [dict(row) for row in value if isinstance(row, Mapping)]


def _route_tokens(public_route: object) -> list[str]:
    tokens: list[str] = []
    for chunk in _string_list(public_route):
        tokens.extend(token.strip() for token in chunk.split("/") if token.strip())
    return tokens


def _evidence_selector_family(
    row: Mapping[str, object],
    *,
    family_keys: set[str],
    public_route_family_map: Mapping[str, str],
) -> str:
    selector_family = str(row.get("selector_family", ""))
    if selector_family:
        return selector_family
    quantity = str(row.get("quantity", ""))
    if quantity in family_keys:
        return quantity
    for route in _route_tokens(row.get("public_route")):
        family = public_route_family_map.get(route)
        if family:
            return family
    return ""


def _is_public_production_evidence(row: Mapping[str, object]) -> bool:
    if row.get("classification") != PRODUCTION_EVIDENCE_CLASSIFICATION:
        return False
    state = row.get("public_admission_state")
    return state in (None, "", PUBLIC_ROUTE_OPEN_STATE)


def _contract_for_activation_row(
    row: Mapping[str, object],
    *,
    evidence_rows: Sequence[Mapping[str, object]],
    family_keys: set[str],
    public_route_family_map: Mapping[str, str],
) -> dict[str, object]:
    family = str(row["key"])
    family_evidence = [
        dict(evidence)
        for evidence in evidence_rows
        if _evidence_selector_family(
            evidence,
            family_keys=family_keys,
            public_route_family_map=public_route_family_map,
        )
        == family
    ]
    production_evidence = [evidence for evidence in family_evidence if _is_public_production_evidence(evidence)]
    residual_families = _string_list(row.get("residual_families"))
    constraint_families = _string_list(row.get("constraint_families"))
    postsolve_certification = str(row.get("postsolve_certification", ""))
    return {
        "activation": dict(row),
        "production_exposed": bool(row.get("production_exposed")),
        "exposure_status": str(row.get("exposure_status", "")),
        "certification_required": postsolve_certification in {"on", "tpd_postsolve"},
        "selector_family": family,
        "display_name": str(row.get("display_name", family)),
        "public_routes": _string_list(row.get("public_routes")),
        "proof_routes": _string_list(row.get("proof_routes")),
        "residual_families": residual_families,
        "constraint_families": constraint_families,
        "variable_model": str(row.get("variable_model", "")),
        "density_backend": str(row.get("density_backend", "")),
        "derivative_requirement": str(row.get("derivative_requirement", "")),
        "stability_prelayer": str(row.get("stability_prelayer", "")),
        "postsolve_certification": postsolve_certification,
        "family_residual_block": _FAMILY_RESIDUAL_BLOCKS.get(family, "planned_private"),
        "acceptance_diagnostics_required": sorted(
            set(residual_families)
            | set(constraint_families)
            | {"capability_evidence", "postsolve_certification", "public_route_mapping"}
        ),
        "evidence_rows": family_evidence,
        "production_evidence_quantities": sorted(str(evidence.get("quantity", "")) for evidence in production_evidence),
    }


def phase_equilibrium_certification_contracts(
    *,
    activation: Mapping[str, object],
    route_derivative_evidence: Mapping[str, object],
) -> dict[str, object]:
    """Return the shared certification payload for production PE routes."""

    activation_rows = _rows(activation.get("rows"))
    evidence_rows = _rows(route_derivative_evidence.get("rows"))
    public_route_family_map = {
        str(route): str(family)
        for route, family in dict(activation.get("public_route_family_map", {})).items()
    }
    production_families = [
        str(row["key"])
        for row in activation_rows
        if bool(row.get("production_exposed")) and str(row.get("exposure_status", "")) == "production_exposed"
    ]
    family_keys = {str(row["key"]) for row in activation_rows}
    production_contracts = [
        _contract_for_activation_row(
            row,
            evidence_rows=evidence_rows,
            family_keys=family_keys,
            public_route_family_map=public_route_family_map,
        )
        for row in activation_rows
        if str(row["key"]) in set(production_families)
    ]
    planned_route_families = [
        {
            "selector_family": str(row["key"]),
            "display_name": str(row.get("display_name", row["key"])),
            "production_exposed": bool(row.get("production_exposed")),
            "exposure_status": str(row.get("exposure_status", "")),
            "public_routes": _string_list(row.get("public_routes")),
            "proof_routes": _string_list(row.get("proof_routes")),
        }
        for row in activation_rows
        if str(row["key"]) not in set(production_families)
    ]
    return {
        "schema_version": 1,
        "source": "epcsaft_equilibrium.capabilities",
        "production_families": production_families,
        "declared_not_exposed_families": _string_list(activation.get("declared_not_exposed_families")),
        "public_routes": _string_list(activation.get("public_routes")),
        "public_route_family_map": dict(sorted(public_route_family_map.items())),
        "production_route_contracts": production_contracts,
        "planned_route_families": planned_route_families,
        "evidence_rows": evidence_rows,
    }


def validate_phase_equilibrium_certification_contracts(
    payload: Mapping[str, object],
) -> tuple[str, ...]:
    """Return named blockers for shared phase-equilibrium certification drift."""

    blockers: list[str] = []
    public_route_family_map = {
        str(route): str(family)
        for route, family in dict(payload.get("public_route_family_map", {})).items()
    }
    production_families = set(_string_list(payload.get("production_families")))
    public_routes = sorted(_string_list(payload.get("public_routes")))
    contracts = _rows(payload.get("production_route_contracts"))
    planned = _rows(payload.get("planned_route_families"))
    evidence_rows = _rows(payload.get("evidence_rows"))

    if payload.get("schema_version") != 1:
        blockers.append("certification_schema_version_mismatch")
    if not contracts:
        blockers.append("certification_production_contracts_missing")

    certified_routes = sorted(
        route
        for contract in contracts
        for route in _string_list(contract.get("public_routes"))
    )
    if certified_routes != public_routes:
        blockers.append("certification_public_route_coverage_mismatch")

    contract_families = {str(contract.get("selector_family", "")) for contract in contracts}
    if contract_families != production_families:
        blockers.append("certification_production_family_coverage_mismatch")

    for contract in contracts:
        family = str(contract.get("selector_family", ""))
        for field in _REQUIRED_CONTRACT_FIELDS:
            value = contract.get(field)
            if isinstance(value, str):
                missing = not value.strip()
            elif isinstance(value, Sequence):
                missing = len(value) == 0
            else:
                missing = value is None
            if missing:
                blockers.append(f"{family}_{field}_missing")
        if "exact" not in str(contract.get("derivative_requirement", "")):
            blockers.append(f"{family}_exact_derivative_requirement_missing")
        for route in _string_list(contract.get("public_routes")):
            if public_route_family_map.get(route) != family:
                blockers.append(f"{family}_{route}_public_route_map_mismatch")

    for row in planned:
        family = str(row.get("selector_family", ""))
        if _string_list(row.get("public_routes")):
            blockers.append(f"{family}_planned_family_publishes_public_routes")

    for row in evidence_rows:
        if row.get("classification") != PRODUCTION_EVIDENCE_CLASSIFICATION:
            continue
        family = _evidence_selector_family(
            row,
            family_keys=production_families,
            public_route_family_map=public_route_family_map,
        )
        if family not in production_families:
            blockers.append(f"{row.get('quantity', 'evidence')}_production_evidence_family_not_exposed")
        state = row.get("public_admission_state")
        if state not in (None, "", PUBLIC_ROUTE_OPEN_STATE):
            blockers.append(f"{row.get('quantity', 'evidence')}_production_evidence_state_not_public")
        for route in _route_tokens(row.get("public_route")):
            if public_route_family_map.get(route) != family:
                blockers.append(f"{row.get('quantity', 'evidence')}_{route}_evidence_route_not_public")

    return tuple(blockers)
