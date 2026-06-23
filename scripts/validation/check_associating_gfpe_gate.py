from __future__ import annotations

import argparse
import json
import math
import os
import sys
from pathlib import Path
from typing import Any

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = REPO_ROOT / "packages" / "epcsaft" / "src"
EQUILIBRIUM_SRC_ROOT = REPO_ROOT / "packages" / "epcsaft-equilibrium" / "src"
for import_root in (REPO_ROOT, SRC_ROOT, EQUILIBRIUM_SRC_ROOT):
    import_path = str(import_root)
    if import_path not in sys.path:
        sys.path.insert(0, import_path)

from scripts.validation import check_associating_lle_gross_2002 as gross_2002_checker

DEFAULT_CASE_DIR = gross_2002_checker.DEFAULT_CASE_DIR
PUBLIC_PROOF_ROUTE = "associating_neutral_lle_gross_2002_public_exact_hessian"
SOURCE_CONFIGURATION = "Gross2002 Figure8 methanol-cyclohexane"
SOURCE_LABEL = "Gross/Sadowski 2002 Figure 8"
SOURCE_FIXTURE = "data/reference/equilibrium_benchmarks/associating_lle/methanol_cyclohexane"
TEMPERATURE_K = 289.65
PRESSURE_PA = 101_300.0
METHANOL_LEAN_LIQUID = [0.081, 0.919]
METHANOL_RICH_LIQUID = [0.856, 0.144]
LLE_FEED = (
    0.5 * (np.asarray(METHANOL_LEAN_LIQUID, dtype=float) + np.asarray(METHANOL_RICH_LIQUID, dtype=float))
).tolist()


def _jsonable(value: Any) -> Any:
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    return value


def _gross_2002_parameter_set(
    *,
    source_backed: bool = True,
    k_ij: float = 0.051,
    charges: tuple[float, float] = (0.0, 0.0),
):
    from epcsaft.model.parameters import ParameterSet

    return ParameterSet.from_dict(
        {
            "MW": np.asarray([32.042e-3, 84.147e-3]),
            "m": np.asarray([1.5255, 2.5303]),
            "s": np.asarray([3.2300, 3.8499]),
            "e": np.asarray([188.90, 278.11]),
            "e_assoc": np.asarray([2899.5, 0.0]),
            "vol_a": np.asarray([0.035176, 0.0]),
            "assoc_scheme": ["2B", None],
            "k_ij": np.asarray([[0.0, k_ij], [k_ij, 0.0]]),
            "z": np.asarray(charges, dtype=float),
            "dielc": np.asarray([33.05, 2.02]),
        },
        species=["Methanol", "Cyclohexane"],
        metadata={
            "source": SOURCE_LABEL,
            "paper": "Gross and Sadowski 2002",
            "table": "Tables 1 and 2",
            "figure": "Figure 8",
            "source_path": SOURCE_FIXTURE,
            "source_backed": source_backed,
        },
    )


def _solve_public_gross_2002_payload() -> dict[str, Any]:
    from epcsaft import InputError, Mixture
    from epcsaft_equilibrium import Equilibrium

    blockers: list[str] = []
    try:
        equilibrium = Equilibrium(
            Mixture(_gross_2002_parameter_set()),
            route="lle",
            T=TEMPERATURE_K,
            P=PRESSURE_PA,
            z=LLE_FEED,
        )
        structure = equilibrium.structure()
        result = equilibrium.solve(
            solver_options={
                "max_iterations": 320,
                "tolerance": 1.0e-6,
                "ipopt_iteration_history_limit": 12,
                "ipopt_acceptable_tolerance": 1.0e-7,
                "ipopt_constraint_violation_tolerance": 1.0e-7,
                "ipopt_dual_infeasibility_tolerance": 1.0e-8,
                "ipopt_complementarity_tolerance": 1.0e-8,
            }
        )
    except InputError as exc:
        return {
            "status": "blocked",
            "blockers": ["public_associating_lle_not_admitted"],
            "exception_type": type(exc).__name__,
            "message": str(exc),
        }
    except Exception as exc:  # pragma: no cover - retained for CLI diagnostics.
        return {
            "status": "blocked",
            "blockers": ["public_associating_lle_solve_failed"],
            "exception_type": type(exc).__name__,
            "message": str(exc),
        }

    diagnostics = dict(result.diagnostics)
    phase_compositions = [list(composition) for composition in result.phase_compositions.values()]
    methanol_values = sorted(float(composition[0]) for composition in phase_compositions)
    lean_error = abs(methanol_values[0] - METHANOL_LEAN_LIQUID[0])
    rich_error = abs(methanol_values[1] - METHANOL_RICH_LIQUID[0])
    phase_distance = abs(methanol_values[1] - methanol_values[0])

    if result.selector_route != "neutral_lle":
        blockers.append("public_associating_lle_selector_route_mismatch")
    if structure.activation_key != "neutral_lle":
        blockers.append("public_associating_lle_activation_mismatch")
    if diagnostics.get("hessian_approximation") != "exact":
        blockers.append("public_associating_lle_hessian_not_exact")
    if diagnostics.get("exact_hessian_available") is not True:
        blockers.append("public_associating_lle_exact_hessian_missing")
    if diagnostics.get("postsolve_accepted") is not True:
        blockers.append("public_associating_lle_postsolve_not_accepted")
    if len(phase_compositions) != 2:
        blockers.append("public_associating_lle_phase_count_mismatch")
    if not math.isfinite(phase_distance) or phase_distance <= 0.5:
        blockers.append("public_associating_lle_phase_distance_collapsed")
    if lean_error > 0.12 or rich_error > 0.12:
        blockers.append("public_associating_lle_source_branch_error_exceeds_threshold")

    return {
        "status": "public_route_admitted" if not blockers else "blocked",
        "blockers": blockers,
        "public_route": "lle",
        "selector_route": result.selector_route,
        "problem_kind": result.problem_kind,
        "activation_key": structure.activation_key,
        "expected_phase_keys": list(structure.expected_phase_keys),
        "source_configuration": SOURCE_CONFIGURATION,
        "hessian_approximation": diagnostics.get("hessian_approximation"),
        "exact_hessian_available": diagnostics.get("exact_hessian_available"),
        "postsolve_accepted": diagnostics.get("postsolve_accepted"),
        "phase_compositions": phase_compositions,
        "methanol_branch_values": methanol_values,
        "methanol_lean_abs_error": lean_error,
        "methanol_rich_abs_error": rich_error,
        "phase_distance": phase_distance,
    }


def _expect_rejection(
    *,
    case_key: str,
    route: str,
    source_backed: bool = True,
    k_ij: float = 0.051,
    charges: tuple[float, float] = (0.0, 0.0),
    phase_kinds: list[str] | None = None,
) -> dict[str, Any]:
    from epcsaft import InputError, Mixture
    from epcsaft_equilibrium import Equilibrium

    try:
        Equilibrium(
            Mixture(_gross_2002_parameter_set(source_backed=source_backed, k_ij=k_ij, charges=charges)),
            route=route,
            T=TEMPERATURE_K,
            P=PRESSURE_PA,
            z=LLE_FEED,
            phase_kinds=phase_kinds,
        )
    except InputError as exc:
        return {
            "case_key": case_key,
            "status": "rejected",
            "exception_type": type(exc).__name__,
            "message": str(exc),
            "blockers": [],
        }
    except Exception as exc:  # pragma: no cover - retained for CLI diagnostics.
        return {
            "case_key": case_key,
            "status": "unexpected_exception",
            "exception_type": type(exc).__name__,
            "message": str(exc),
            "blockers": [f"{case_key}_unexpected_exception"],
        }
    return {
        "case_key": case_key,
        "status": "admitted_unexpectedly",
        "exception_type": "",
        "message": "",
        "blockers": [f"{case_key}_not_rejected"],
    }


def _unsupported_route_rejection_payload() -> dict[str, Any]:
    cases = [
        _expect_rejection(case_key="missing_source_proof", route="lle", source_backed=False),
        _expect_rejection(case_key="altered_binary_interaction", route="lle", k_ij=0.03),
        _expect_rejection(case_key="ionic_associating_lle", route="lle", charges=(1.0, -1.0)),
        _expect_rejection(case_key="associating_tp_flash", route="flash"),
        _expect_rejection(
            case_key="associating_generalized_phase_set",
            route="multiphase",
            phase_kinds=["liquid", "liquid", "liquid"],
        ),
        _expect_rejection(case_key="electrolyte_route_key", route="electrolyte_lle"),
        _expect_rejection(case_key="reactive_route_key", route="reactive_lle"),
    ]
    blockers = [str(blocker) for case in cases for blocker in case.get("blockers", [])]
    return {
        "status": "unsupported_routes_rejected" if not blockers else "blocked",
        "cases": cases,
        "blockers": blockers,
    }


def _capability_evidence_payload() -> dict[str, Any]:
    import epcsaft_equilibrium

    capabilities = epcsaft_equilibrium.capabilities()
    activation = capabilities["activation_matrix"]
    activation_rows = list(activation["rows"])
    neutral_lle = next((row for row in activation_rows if row.get("key") == "neutral_lle"), {})
    route_evidence_rows = list(capabilities["route_derivative_evidence"]["rows"])
    proof_row = next((row for row in route_evidence_rows if row.get("quantity") == PUBLIC_PROOF_ROUTE), {})
    quantities = [str(row.get("quantity")) for row in route_evidence_rows]
    public_routes = list(capabilities["public_routes"])
    production_families = list(capabilities["production_families"])

    blockers: list[str] = []
    if PUBLIC_PROOF_ROUTE not in neutral_lle.get("proof_routes", []):
        blockers.append("activation_matrix_missing_associating_public_proof_route")
    if "lle" not in neutral_lle.get("public_routes", []):
        blockers.append("neutral_lle_public_route_missing")
    if proof_row.get("classification") != "production_supported":
        blockers.append("capability_associating_public_proof_not_production_supported")
    if proof_row.get("public_admission_state") != "public_route_open":
        blockers.append("capability_associating_public_route_not_open")
    if proof_row.get("backend") != "cppad_implicit_association":
        blockers.append("capability_associating_backend_mismatch")
    if proof_row.get("source_configuration") != SOURCE_CONFIGURATION:
        blockers.append("capability_associating_source_configuration_mismatch")
    if proof_row.get("assoc_scheme") != "2B":
        blockers.append("capability_associating_scheme_mismatch")
    if not math.isclose(float(proof_row.get("k_ij", math.nan)), 0.051, abs_tol=1.0e-12):
        blockers.append("capability_associating_kij_mismatch")
    if proof_row.get("source_fixture") != SOURCE_FIXTURE:
        blockers.append("capability_associating_source_fixture_mismatch")
    if any(quantity.endswith("_internal_exact_hessian") for quantity in quantities):
        blockers.append("stale_internal_associating_exact_hessian_row_present")

    electrolyte = next((row for row in activation_rows if row.get("key") == "electrolyte_lle"), {})
    reactive_rows = [row for row in activation_rows if str(row.get("key", "")).startswith("reactive")]
    closed_family_rows = [electrolyte, *reactive_rows]
    for row in closed_family_rows:
        key = str(row.get("key", "missing"))
        if row.get("production_exposed") is True:
            blockers.append(f"{key}_public_route_exposed")
        if row.get("public_routes"):
            blockers.append(f"{key}_public_route_exposed")
    if "electrolyte_lle" in public_routes:
        blockers.append("electrolyte_lle_capability_public_route_exposed")
    if "electrolyte_lle" in production_families:
        blockers.append("electrolyte_lle_production_family_exposed")
    if "reactive_lle" in public_routes:
        blockers.append("reactive_lle_capability_public_route_exposed")
    if "reactive_lle" in production_families:
        blockers.append("reactive_lle_production_family_exposed")

    return {
        "status": "capability_evidence_verified" if not blockers else "blocked",
        "blockers": blockers,
        "proof_route": PUBLIC_PROOF_ROUTE,
        "neutral_lle_proof_routes": list(neutral_lle.get("proof_routes", [])),
        "public_routes": public_routes,
        "production_families": production_families,
        "route_derivative_evidence_quantities": quantities,
        "proof_row": proof_row,
    }


def evaluate_payload(
    payload: dict[str, Any],
    *,
    require_source_data: bool = False,
    require_public_admission: bool = False,
    require_exact_association_hessian: bool = False,
    require_capability_evidence: bool = False,
    require_electrolyte_closed: bool = False,
) -> dict[str, Any]:
    blockers = list(payload.get("blockers", []))
    prerequisite = payload.get("prerequisite_proof", {})
    if require_source_data and prerequisite.get("fixture", {}).get("status") != "source_backed":
        blockers.append("source_data_missing")
        blockers.extend(str(item) for item in prerequisite.get("blockers", []))
    if require_exact_association_hessian:
        hessian = prerequisite.get("association_hessian", {})
        if hessian.get("status") != "verified_exact":
            blockers.append("exact_association_hessian_missing")
        blockers.extend(str(item) for item in hessian.get("blockers", []))
    if require_public_admission:
        public_admission = payload.get("public_admission", {})
        if public_admission.get("status") != "public_route_admitted":
            blockers.append("public_associating_lle_not_admitted")
        blockers.extend(str(item) for item in public_admission.get("blockers", []))
        unsupported = payload.get("unsupported_route_rejections", {})
        if unsupported.get("status") != "unsupported_routes_rejected":
            blockers.append("unsupported_associating_routes_not_rejected")
        blockers.extend(str(item) for item in unsupported.get("blockers", []))
    if require_capability_evidence:
        capability = payload.get("capability_evidence", {})
        if capability.get("status") != "capability_evidence_verified":
            blockers.append("capability_associating_public_evidence_missing")
        blockers.extend(str(item) for item in capability.get("blockers", []))
    if require_electrolyte_closed:
        capability = payload.get("capability_evidence", {})
        blockers.extend(
            str(item)
            for item in capability.get("blockers", [])
            if "electrolyte" in str(item) or "reactive" in str(item)
        )

    unique_blockers = sorted(set(blockers))
    result = dict(payload)
    result["blockers"] = unique_blockers
    result["complete"] = not unique_blockers
    result["status"] = "complete" if result["complete"] else "blocked"
    return result


def evaluate_case_dir(
    case_dir: Path = DEFAULT_CASE_DIR,
    *,
    require_source_data: bool = False,
    require_public_admission: bool = False,
    require_exact_association_hessian: bool = False,
    require_capability_evidence: bool = False,
    require_electrolyte_closed: bool = False,
) -> dict[str, Any]:
    prerequisite_proof = gross_2002_checker.evaluate_case_dir(
        Path(case_dir),
        require_source_data=require_source_data or require_exact_association_hessian,
        require_exact_association_hessian=require_exact_association_hessian,
        require_internal_route=require_exact_association_hessian,
        require_route_closed=False,
    )
    public_admission = (
        _solve_public_gross_2002_payload()
        if require_public_admission
        else {"status": "outside_current_gate", "blockers": []}
    )
    unsupported_route_rejections = (
        _unsupported_route_rejection_payload()
        if require_public_admission
        else {"status": "outside_current_gate", "blockers": []}
    )
    capability_evidence = (
        _capability_evidence_payload()
        if require_capability_evidence or require_electrolyte_closed
        else {"status": "outside_current_gate", "blockers": []}
    )
    payload = {
        "checker": "associating_gfpe_public_admission_gate",
        "case_label": "Gross/Sadowski 2002 methanol/cyclohexane public associating LLE",
        "prerequisite_proof": prerequisite_proof,
        "public_admission": public_admission,
        "unsupported_route_rejections": unsupported_route_rejections,
        "capability_evidence": capability_evidence,
        "blockers": [],
    }
    return _jsonable(
        evaluate_payload(
            payload,
            require_source_data=require_source_data,
            require_public_admission=require_public_admission,
            require_exact_association_hessian=require_exact_association_hessian,
            require_capability_evidence=require_capability_evidence,
            require_electrolyte_closed=require_electrolyte_closed,
        )
    )


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--case-dir", type=Path, default=DEFAULT_CASE_DIR)
    parser.add_argument("--require-source-data", action="store_true")
    parser.add_argument("--require-public-admission", action="store_true")
    parser.add_argument("--require-exact-association-hessian", action="store_true")
    parser.add_argument("--require-capability-evidence", action="store_true")
    parser.add_argument("--require-electrolyte-closed", action="store_true")
    parser.add_argument("--require-complete", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    from scripts.dev.native_runtime_env import apply_native_runtime_env

    apply_native_runtime_env(os.environ)
    args = build_arg_parser().parse_args(argv)
    output = evaluate_case_dir(
        args.case_dir,
        require_source_data=args.require_source_data or args.require_complete,
        require_public_admission=args.require_public_admission or args.require_complete,
        require_exact_association_hessian=args.require_exact_association_hessian or args.require_complete,
        require_capability_evidence=args.require_capability_evidence or args.require_complete,
        require_electrolyte_closed=args.require_electrolyte_closed or args.require_complete,
    )
    if args.json:
        print(json.dumps(output, indent=2, sort_keys=True))
    else:
        print(f"complete={output['complete']} blockers={','.join(output['blockers'])}")
    if args.require_complete and not output["complete"]:
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
