"""Validate retained Gross-2002 associating-LLE diagnostics without public admission.

This checker proves only three bounded facts: the retained source fixture is
present, the internal association derivative diagnostic is exact, and the LLE
selector family remains closed. It does not certify a globally complete phase
set or a production route.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = REPO_ROOT / "packages" / "epcsaft" / "src"
EQUILIBRIUM_SRC_ROOT = REPO_ROOT / "packages" / "epcsaft-equilibrium" / "src"
for import_root in (REPO_ROOT, SRC_ROOT, EQUILIBRIUM_SRC_ROOT):
    import_path = str(import_root)
    if import_path not in sys.path:
        sys.path.insert(0, import_path)

from scripts.validation import check_associating_lle_gross_2002 as gross_2002_checker

DEFAULT_CASE_DIR = gross_2002_checker.DEFAULT_CASE_DIR
INTERNAL_EVIDENCE_ID = "associating_neutral_lle_gross_2002_internal_exact_hessian"
SOURCE_CONFIGURATION = "Gross2002 Figure8 methanol-cyclohexane"
SOURCE_FIXTURE = "data/reference/equilibrium_benchmarks/associating_lle/methanol_cyclohexane"


def _jsonable(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    return value


def _capability_evidence_payload() -> dict[str, Any]:
    import epcsaft_equilibrium

    capabilities = epcsaft_equilibrium.capabilities()
    activation_rows = list(capabilities["activation_matrix"]["rows"])
    neutral_lle = next((row for row in activation_rows if row.get("key") == "neutral_lle"), {})
    evidence_rows = list(capabilities["route_derivative_evidence"]["rows"])
    evidence = next(
        (row for row in evidence_rows if row.get("quantity") == INTERNAL_EVIDENCE_ID),
        {},
    )

    blockers: list[str] = []
    if neutral_lle.get("production_exposed") is not False:
        blockers.append("neutral_lle_family_not_closed")
    if neutral_lle.get("public_routes"):
        blockers.append("neutral_lle_public_routes_present")
    if neutral_lle.get("proof_routes"):
        blockers.append("neutral_lle_production_proofs_present")
    if "lle" in capabilities["public_routes"]:
        blockers.append("lle_public_route_present")
    if "neutral_lle" in capabilities["production_families"]:
        blockers.append("neutral_lle_production_family_present")
    if evidence.get("classification") != "internal_validation_evidence":
        blockers.append("associating_lle_evidence_not_internal")
    if "public_route" in evidence or "public_admission_state" in evidence:
        blockers.append("associating_lle_evidence_carries_public_claim")
    if evidence.get("backend") != "cppad_implicit_association":
        blockers.append("associating_lle_derivative_backend_mismatch")
    if evidence.get("source_configuration") != SOURCE_CONFIGURATION:
        blockers.append("associating_lle_source_configuration_mismatch")
    if evidence.get("assoc_scheme") != "2B":
        blockers.append("associating_lle_scheme_mismatch")
    if not math.isclose(float(evidence.get("k_ij", math.nan)), 0.051, abs_tol=1.0e-12):
        blockers.append("associating_lle_kij_mismatch")
    if evidence.get("source_fixture") != SOURCE_FIXTURE:
        blockers.append("associating_lle_source_fixture_mismatch")

    return {
        "status": "internal_diagnostic_evidence_verified" if not blockers else "blocked",
        "blockers": blockers,
        "family_state": {
            "production_exposed": neutral_lle.get("production_exposed"),
            "public_routes": list(neutral_lle.get("public_routes", [])),
            "proof_routes": list(neutral_lle.get("proof_routes", [])),
        },
        "evidence_id": INTERNAL_EVIDENCE_ID,
        "evidence": evidence,
    }


def evaluate_payload(
    payload: dict[str, Any],
    *,
    require_source_data: bool = False,
    require_exact_association_hessian: bool = False,
    require_internal_evidence: bool = False,
    require_route_closed: bool = False,
) -> dict[str, Any]:
    blockers = list(payload.get("blockers", []))
    diagnostic = payload.get("internal_diagnostic", {})
    if require_source_data and diagnostic.get("fixture", {}).get("status") != "source_backed":
        blockers.append("source_data_missing")
        blockers.extend(str(item) for item in diagnostic.get("blockers", []))
    if require_exact_association_hessian:
        hessian = diagnostic.get("association_hessian", {})
        if hessian.get("status") != "verified_exact":
            blockers.append("exact_association_hessian_missing")
        blockers.extend(str(item) for item in hessian.get("blockers", []))
    capability = payload.get("capability_evidence", {})
    if require_internal_evidence:
        if capability.get("status") != "internal_diagnostic_evidence_verified":
            blockers.append("internal_associating_lle_evidence_missing")
        blockers.extend(str(item) for item in capability.get("blockers", []))
    if require_route_closed:
        family_state = capability.get("family_state", {})
        if (
            family_state.get("production_exposed") is not False
            or family_state.get("public_routes")
            or family_state.get("proof_routes")
        ):
            blockers.append("neutral_lle_route_not_closed")

    result = dict(payload)
    result["blockers"] = sorted(set(blockers))
    result["complete"] = not result["blockers"]
    result["status"] = "complete" if result["complete"] else "blocked"
    return result


def evaluate_case_dir(
    case_dir: Path = DEFAULT_CASE_DIR,
    *,
    require_source_data: bool = False,
    require_exact_association_hessian: bool = False,
    require_internal_evidence: bool = False,
    require_route_closed: bool = False,
) -> dict[str, Any]:
    internal_diagnostic = gross_2002_checker.evaluate_case_dir(
        Path(case_dir),
        require_source_data=require_source_data or require_exact_association_hessian,
        require_exact_association_hessian=require_exact_association_hessian,
        require_internal_route=False,
        require_route_closed=require_route_closed,
    )
    capability_evidence = (
        _capability_evidence_payload()
        if require_internal_evidence or require_route_closed
        else {"status": "outside_current_gate", "blockers": []}
    )
    payload = {
        "checker": "associating_gfpe_internal_diagnostic_gate",
        "case_label": "Gross/Sadowski 2002 methanol/cyclohexane internal associating-LLE evidence",
        "claim_scope": "source fixture, exact association derivatives, and closed-route state only",
        "global_phase_set_certified": False,
        "production_route_admitted": False,
        "internal_diagnostic": internal_diagnostic,
        "capability_evidence": capability_evidence,
        "blockers": [],
    }
    return _jsonable(
        evaluate_payload(
            payload,
            require_source_data=require_source_data,
            require_exact_association_hessian=require_exact_association_hessian,
            require_internal_evidence=require_internal_evidence,
            require_route_closed=require_route_closed,
        )
    )


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--case-dir", type=Path, default=DEFAULT_CASE_DIR)
    parser.add_argument("--require-source-data", action="store_true")
    parser.add_argument("--require-exact-association-hessian", action="store_true")
    parser.add_argument("--require-internal-evidence", action="store_true")
    parser.add_argument("--require-route-closed", action="store_true")
    parser.add_argument("--require-complete", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    from scripts.dev.native_runtime_env import apply_native_runtime_env

    apply_native_runtime_env(os.environ)
    args = build_arg_parser().parse_args(argv)
    output = evaluate_case_dir(
        args.case_dir,
        require_source_data=args.require_source_data or args.require_complete,
        require_exact_association_hessian=(
            args.require_exact_association_hessian or args.require_complete
        ),
        require_internal_evidence=args.require_internal_evidence or args.require_complete,
        require_route_closed=args.require_route_closed or args.require_complete,
    )
    if args.json:
        print(json.dumps(output, indent=2, sort_keys=True))
    else:
        print(f"complete={output['complete']} blockers={','.join(output['blockers'])}")
    return 2 if args.require_complete and not output["complete"] else 0


if __name__ == "__main__":
    sys.exit(main())
