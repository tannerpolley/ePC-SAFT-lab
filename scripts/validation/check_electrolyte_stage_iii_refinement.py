from __future__ import annotations

import argparse
import copy
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

from scripts.validation import (
    check_electrolyte_gfpe_gate,
    check_electrolyte_held2_phase_discovery,
    check_electrolyte_tpd_gate,
)

ALGORITHM_SCOPE = "held2_stage_iii_reduced_variable_refinement_only"
HELD2_SCOPE = check_electrolyte_held2_phase_discovery.ALGORITHM_SCOPE
CHARGE_TOLERANCE = check_electrolyte_tpd_gate.CHARGE_TOLERANCE
TPD_TOLERANCE = check_electrolyte_tpd_gate.TPD_TOLERANCE
CANDIDATE_MASS_BALANCE_TOLERANCE = check_electrolyte_tpd_gate.CANDIDATE_MASS_BALANCE_TOLERANCE
NATIVE_SPECIES = check_electrolyte_tpd_gate.NATIVE_SPECIES
CHARGE_VECTOR = check_electrolyte_tpd_gate.CHARGE_VECTOR.astype(float)
RESIDUAL_TOLERANCE = 1.0e-4
PHASE_DISTANCE_TOLERANCE = 1.0e-8
ACTIVE_BOUND_TOLERANCE = 1.0e-8


def _jsonable(value: Any) -> Any:
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    return value


def _finite_nested(values: Any) -> bool:
    if isinstance(values, (list, tuple)):
        return all(_finite_nested(value) for value in values)
    try:
        value = float(values)
    except (TypeError, ValueError):
        return False
    return math.isfinite(value)


def _native_stage_iii_payload(case_dir: Path, checker_command: list[str] | None) -> dict[str, Any]:
    from scripts.dev.native_runtime_env import apply_native_runtime_env

    apply_native_runtime_env(os.environ)
    from epcsaft_equilibrium._native import extension_native_core

    from scripts.validation import native_freshness

    mixture, feed, temperature, pressure = check_electrolyte_tpd_gate._khudaida_mixture_and_feed(case_dir)
    core = extension_native_core()
    stage_iii = core._native_electrolyte_stage_iii_refinement(
        mixture._native,
        temperature,
        pressure,
        feed.tolist(),
        CHARGE_VECTOR.tolist(),
        NATIVE_SPECIES,
        [0, 0],
        CHARGE_TOLERANCE,
        TPD_TOLERANCE,
        CANDIDATE_MASS_BALANCE_TOLERANCE,
        RESIDUAL_TOLERANCE,
        PHASE_DISTANCE_TOLERANCE,
        ACTIVE_BOUND_TOLERANCE,
    )
    stage_iii = dict(stage_iii)
    receipt = native_freshness.build_equilibrium_native_receipt(
        native_module=core,
        checker_command=checker_command
        or [
            "uv",
            "run",
            "--no-sync",
            "python",
            "scripts/validation/check_electrolyte_stage_iii_refinement.py",
            "--json",
            "--require-complete",
        ],
    )
    stage_iii["native_freshness_receipt"] = native_freshness.receipt_to_jsonable(receipt)
    return _jsonable(stage_iii)


def _validate_stage_iii_payload(stage_iii: dict[str, Any]) -> list[str]:
    blockers: list[str] = []
    if stage_iii.get("algorithm_scope") != ALGORITHM_SCOPE:
        blockers.append("stage_iii_algorithm_scope_mismatch")
    if stage_iii.get("status") != "complete":
        blockers.append("stage_iii_refinement_incomplete")
    if stage_iii.get("native_binding") != "_native_electrolyte_stage_iii_refinement":
        blockers.append("stage_iii_native_binding_mismatch")

    stages = stage_iii.get("stage_statuses", {})
    if stages.get("phase_discovery") != "complete":
        blockers.append("stage_iii_source_phase_discovery_incomplete")
    if stages.get("stage_iii_refinement") != "complete":
        blockers.append("stage_iii_status_incomplete")
    if stages.get("postsolve_certification") == "complete":
        blockers.append("stage_iii_postsolve_claimed_complete")
    if stages.get("public_route_admission") != "separate_public_admission_gate":
        blockers.append("stage_iii_public_route_admission_open")

    seed = stage_iii.get("seed_provenance", {})
    if seed.get("source_gate") != "electrolyte_held2_counterion_pair_phase_discovery":
        blockers.append("stage_iii_seed_source_mismatch")
    if seed.get("native_binding") != "_native_electrolyte_held2_phase_discovery":
        blockers.append("stage_iii_seed_native_binding_mismatch")
    if int(seed.get("selected_candidate_count", 0)) < 2:
        blockers.append("stage_iii_selected_candidate_set_missing")

    residual = stage_iii.get("reduced_residual_system", {})
    if residual.get("coordinate_basis") != "counterion_pair_transformed_variables":
        blockers.append("stage_iii_reduced_basis_mismatch")
    if "raw_single_ion_residuals" in residual:
        blockers.append("stage_iii_raw_single_ion_equality_present")
    variable_labels = list(residual.get("variable_labels", []))
    equation_labels = list(residual.get("equation_labels", []))
    if not variable_labels:
        blockers.append("stage_iii_variable_labels_missing")
    if not equation_labels:
        blockers.append("stage_iii_equation_labels_missing")
    for key in ("variable_lower_bounds", "variable_upper_bounds", "variable_scaling"):
        if len(residual.get(key, [])) != len(variable_labels):
            blockers.append(f"stage_iii_{key}_shape_mismatch")
    for key in ("residual_values", "residual_scaling"):
        if len(residual.get(key, [])) != len(equation_labels):
            blockers.append(f"stage_iii_{key}_shape_mismatch")
    residual_norm = float(residual.get("residual_inf_norm", math.inf))
    residual_tolerance = float(residual.get("residual_tolerance", RESIDUAL_TOLERANCE))
    if residual_norm > residual_tolerance:
        blockers.append("stage_iii_residual_norm_exceeds_tolerance")
    if not _finite_nested(residual.get("residual_values", [])):
        blockers.append("stage_iii_residual_values_not_finite")

    derivatives = stage_iii.get("derivative_receipts", {})
    if derivatives.get("gradient_approximation") != "exact":
        blockers.append("stage_iii_gradient_not_exact")
    if derivatives.get("jacobian_approximation") != "exact":
        blockers.append("stage_iii_jacobian_not_exact")
    if derivatives.get("hessian_approximation") != "exact":
        blockers.append("stage_iii_hessian_not_exact")
    if derivatives.get("exact_reduced_jacobian_available") is not True:
        blockers.append("stage_iii_reduced_jacobian_receipt_missing")
    if derivatives.get("exact_reduced_hessian_available") is not True:
        blockers.append("stage_iii_reduced_hessian_receipt_missing")
    if int(derivatives.get("jacobian_nonzero_count", 0)) <= 0:
        blockers.append("stage_iii_jacobian_structure_missing")
    if int(derivatives.get("hessian_nonzero_count", 0)) <= 0:
        blockers.append("stage_iii_hessian_structure_missing")

    solver = stage_iii.get("solver_diagnostics", {})
    if solver.get("solver_backend") != "ipopt":
        blockers.append("stage_iii_solver_backend_mismatch")
    if solver.get("solver_accepted") is not True:
        blockers.append("stage_iii_solver_rejected")
    strict_success = (
        solver.get("ipopt_status") == "Solve_Succeeded"
        and solver.get("application_status") == "solve_succeeded"
    )
    certified_acceptable = (
        solver.get("ipopt_status") == "acceptable_point"
        and solver.get("application_status") == "solved_to_acceptable_level"
        and solver.get("solver_accepted") is True
        and solver.get("route_accepted") is True
    )
    if not (strict_success or certified_acceptable):
        blockers.append("stage_iii_ipopt_status_mismatch")
    if not (strict_success or certified_acceptable):
        blockers.append("stage_iii_application_status_mismatch")
    if float(solver.get("residual_inf_norm", math.inf)) > float(
        solver.get("residual_tolerance", RESIDUAL_TOLERANCE)
    ):
        blockers.append("stage_iii_solver_residual_norm_exceeds_tolerance")
    if float(solver.get("active_bound_violation", math.inf)) > float(
        solver.get("active_bound_tolerance", ACTIVE_BOUND_TOLERANCE)
    ):
        blockers.append("stage_iii_active_bound_violation")
    if float(solver.get("phase_distance", 0.0)) <= float(
        solver.get("phase_distance_tolerance", PHASE_DISTANCE_TOLERANCE)
    ):
        blockers.append("stage_iii_phase_collapse")
    if not _finite_nested(solver.get("phase_compositions", [])):
        blockers.append("stage_iii_phase_compositions_not_finite")
    return blockers


def evaluate_payload(
    payload: dict[str, Any],
    *,
    require_source_gate: bool = False,
    require_readiness_gate: bool = False,
    require_tpd_gate: bool = False,
    require_held2_discovery: bool = False,
    require_native_stage_iii: bool = False,
    require_public_routes_closed: bool = False,
) -> dict[str, Any]:
    blockers = list(payload.get("blockers", []))

    source_gate = payload.get("source_gate", {})
    if require_source_gate:
        if source_gate.get("complete") is not True:
            blockers.append("electrolyte_source_gate_incomplete")
        blockers.extend(str(item) for item in source_gate.get("blockers", []))

    readiness = payload.get("held2_readiness_gate", {})
    if require_readiness_gate:
        if readiness.get("complete") is not True:
            blockers.append("electrolyte_held2_readiness_gate_incomplete")
        blockers.extend(str(item) for item in readiness.get("blockers", []))

    tpd_gate = payload.get("electrolyte_tpd_gate", {})
    if require_tpd_gate:
        if tpd_gate.get("complete") is not True:
            blockers.append("electrolyte_tpd_gate_incomplete")
        blockers.extend(str(item) for item in tpd_gate.get("blockers", []))
        tpd = tpd_gate.get("electrolyte_tpd", {})
        if tpd.get("status") != "charge_neutral_tpd_screening_complete":
            blockers.append("electrolyte_tpd_native_gate_incomplete")

    held2 = payload.get("held2_phase_discovery", {})
    if require_held2_discovery:
        if held2.get("complete") is False or held2.get("status") != "complete":
            blockers.append("held2_phase_discovery_incomplete")
        blockers.extend(str(item) for item in held2.get("blockers", []))
        if held2.get("algorithm_scope") != HELD2_SCOPE:
            blockers.append("held2_phase_discovery_scope_mismatch")
        handoff = held2.get("stage_iii_handoff", {})
        if handoff.get("status") != "pending_stage_iii_refinement":
            blockers.append("stage_iii_handoff_status_mismatch")
        if len(handoff.get("explicit_ion_phase_compositions", [])) < 2:
            blockers.append("stage_iii_handoff_candidate_set_missing")

    stage_iii = payload.get("electrolyte_stage_iii_refinement", {})
    if require_native_stage_iii:
        blockers.extend(_validate_stage_iii_payload(stage_iii))

    public_state = payload.get("public_route_state", {})
    electrolyte = public_state.get("electrolyte_lle", {})
    if require_public_routes_closed:
        if electrolyte.get("present") is not True:
            blockers.append("electrolyte_lle_activation_row_missing")
        if electrolyte.get("production_exposed") is True:
            blockers.append("electrolyte_lle_public_route_exposed")
        if electrolyte.get("public_routes"):
            blockers.append("electrolyte_lle_public_route_exposed")
        if electrolyte.get("proof_routes"):
            blockers.append("electrolyte_lle_proof_route_exposed")
        if "electrolyte_lle" in public_state.get("capabilities_public_routes", []):
            blockers.append("electrolyte_lle_capability_public_route_exposed")
        if "electrolyte_lle" in public_state.get("production_families", []):
            blockers.append("electrolyte_lle_production_family_exposed")

    result = dict(payload)
    result["blockers"] = sorted(set(blockers))
    result["complete"] = not result["blockers"]
    return _jsonable(result)


def evaluate_stage_iii_refinement(
    case_dir: Path = check_electrolyte_gfpe_gate.DEFAULT_CASE_DIR,
    *,
    require_source_gate: bool = False,
    require_readiness_gate: bool = False,
    require_tpd_gate: bool = False,
    require_held2_discovery: bool = False,
    require_native_stage_iii: bool = False,
    require_public_routes_closed: bool = False,
    checker_command: list[str] | None = None,
) -> dict[str, Any]:
    case_dir = Path(case_dir)
    held2_payload = check_electrolyte_held2_phase_discovery.evaluate_held2_phase_discovery(
        case_dir,
        require_source_gate=True,
        require_readiness_gate=True,
        require_tpd_gate=True,
        require_native_held2_discovery=True,
        require_public_routes_closed=require_public_routes_closed,
        checker_command=checker_command,
    )
    try:
        stage_iii = _native_stage_iii_payload(case_dir, checker_command)
    except Exception as exc:
        stage_iii = {
            "status": "failed",
            "blockers": [f"stage_iii_native_receipt_failed:{exc}"],
            "algorithm_scope": ALGORITHM_SCOPE,
        }

    held2 = copy.deepcopy(held2_payload.get("held2_phase_discovery", {}))
    held2["complete"] = held2_payload.get("complete") is True
    payload = {
        "checker": "electrolyte_held2_stage_iii_refinement_gate",
        "case_label": "Khudaida 2026 electrolyte LLE Stage III refinement",
        "source_gate": held2_payload.get("source_gate", {}),
        "held2_readiness_gate": held2_payload.get("held2_readiness_gate", {}),
        "electrolyte_tpd_gate": held2_payload.get("electrolyte_tpd_gate", {}),
        "held2_phase_discovery": held2,
        "electrolyte_stage_iii_refinement": stage_iii,
        "public_route_state": held2_payload.get("public_route_state", {}),
    }
    return evaluate_payload(
        payload,
        require_source_gate=require_source_gate,
        require_readiness_gate=require_readiness_gate,
        require_tpd_gate=require_tpd_gate,
        require_held2_discovery=require_held2_discovery,
        require_native_stage_iii=require_native_stage_iii,
        require_public_routes_closed=require_public_routes_closed,
    )


def minimal_complete_payload_for_tests() -> dict[str, Any]:
    source_gate = {"complete": True, "blockers": []}
    readiness_gate = {"complete": True, "blockers": []}
    tpd_gate = {
        "complete": True,
        "blockers": [],
        "electrolyte_tpd": {"status": "charge_neutral_tpd_screening_complete"},
    }
    held2 = copy.deepcopy(check_electrolyte_held2_phase_discovery.minimal_complete_payload_for_tests())
    held2_phase = held2["held2_phase_discovery"]
    held2_phase["complete"] = True
    held2_phase["reduced_tpd"]["selected_candidate_count"] = 2
    held2_phase["stage_iii_handoff"] = {
        "status": "pending_stage_iii_refinement",
        "phase_fractions": [0.4, 0.6],
        "phase_kinds": [0, 0],
        "explicit_ion_phase_compositions": [[0.97, 0.015, 0.015], [0.99, 0.005, 0.005]],
        "reduced_candidate_coordinates": [[0.005], [-0.005]],
        "counterion_pair_matrix": [[1.0, 1.0]],
        "mean_ionic_pair_labels": ["Na+/Cl-"],
        "tpd_values": [-1.0e-3, -5.0e-4],
    }
    held2_phase["tpd_discovery"] = {
        "held_stage_ii_status": "dual_loop_verified",
        "held_stage_ii_candidate_bound_audit_status": "candidate_bound_gap_closed",
        "held_stage_ii_dual_loop_status": "verified",
        "held_stage_ii_replay_ready": True,
        "held_stage_ii_replay_phase_fractions": [0.4, 0.6],
        "held_stage_ii_replay_phase_kinds": [0, 0],
        "held_stage_ii_replay_phase_compositions": [[0.97, 0.015, 0.015], [0.99, 0.005, 0.005]],
        "held_stage_ii_replay_source": "stage_ii_dual_loop_selected_candidates",
        "held_stage_ii_replay_seed_name": "held_stage_ii_dual_loop_candidate_pair",
        "held_stage_ii_replay_candidate_ranks": [0, 1],
    }
    held2_phase["electroneutral_lift"]["lifted_candidate_compositions"] = [
        [0.97, 0.015, 0.015],
        [0.99, 0.005, 0.005],
    ]
    held2_phase["electroneutral_lift"]["reduced_candidate_coordinates"] = [[0.005], [-0.005]]
    public_state = {
        "electrolyte_lle": {
            "present": True,
            "production_exposed": False,
            "public_routes": [],
            "proof_routes": [],
        },
        "capabilities_public_routes": [],
        "production_families": [],
    }
    stage_iii = {
        "algorithm_scope": ALGORITHM_SCOPE,
        "status": "complete",
        "native_binding": "_native_electrolyte_stage_iii_refinement",
        "selected_phase_labels": ["phase_0", "phase_1"],
        "stage_statuses": {
            "phase_discovery": "complete",
            "stage_iii_refinement": "complete",
            "postsolve_certification": "pending",
            "public_route_admission": "separate_public_admission_gate",
        },
        "seed_provenance": {
            "source_gate": "electrolyte_held2_counterion_pair_phase_discovery",
            "native_binding": "_native_electrolyte_held2_phase_discovery",
            "seed_name": "electrolyte_held2_counterion_pair_candidate_set",
            "selected_candidate_count": 2,
            "selected_phase_kinds": [0, 0],
            "selected_phase_fractions": [0.4, 0.6],
            "selected_phase_compositions": [[0.97, 0.015, 0.015], [0.99, 0.005, 0.005]],
            "stage_ii_replay_ready": True,
            "stage_ii_replay_source": "stage_ii_dual_loop_selected_candidates",
            "stage_ii_replay_seed_name": "held_stage_ii_dual_loop_candidate_pair",
            "stage_ii_replay_candidate_ranks": [0, 1],
        },
        "reduced_residual_system": {
            "coordinate_basis": "counterion_pair_transformed_variables",
            "variable_labels": ["phase_0:Na+/Cl-", "phase_1:Na+/Cl-", "phase_0_fraction"],
            "variable_lower_bounds": [-1.0, -1.0, 1.0e-12],
            "variable_upper_bounds": [1.0, 1.0, 1.0 - 1.0e-12],
            "variable_scaling": [1.0, 1.0, 1.0],
            "equation_labels": [
                "pair_mean_ionic_equality:Na+/Cl-",
                "phase_fraction_closure",
                "phase_charge_balance:phase_0",
                "phase_charge_balance:phase_1",
            ],
            "residual_values": [0.0, 0.0, 0.0, 0.0],
            "residual_scaling": [1.0, 1.0, 1.0, 1.0],
            "residual_inf_norm": 0.0,
            "residual_tolerance": RESIDUAL_TOLERANCE,
        },
        "derivative_receipts": {
            "derivative_backend": "cppad_phase_amount_charge_constraints_with_counterion_pair_chain_rule",
            "gradient_approximation": "exact",
            "jacobian_approximation": "exact",
            "hessian_approximation": "exact",
            "hessian_backend": "cppad",
            "exact_reduced_jacobian_available": True,
            "exact_reduced_hessian_available": True,
            "jacobian_nonzero_count": 12,
            "hessian_nonzero_count": 6,
        },
        "solver_diagnostics": {
            "solver_backend": "ipopt",
            "ipopt_status": "Solve_Succeeded",
            "solver_status": "success",
            "application_status": "solve_succeeded",
            "route_status": "local_postsolve_accepted",
            "solver_accepted": True,
            "route_accepted": True,
            "iteration_count": 4,
            "residual_inf_norm": 0.0,
            "residual_tolerance": RESIDUAL_TOLERANCE,
            "active_bound_violation": 0.0,
            "active_bound_tolerance": ACTIVE_BOUND_TOLERANCE,
            "phase_distance": 0.02,
            "phase_distance_tolerance": PHASE_DISTANCE_TOLERANCE,
            "phase_compositions": [[0.97, 0.015, 0.015], [0.99, 0.005, 0.005]],
            "phase_fractions": [0.4, 0.6],
        },
    }
    return {
        "checker": "electrolyte_held2_stage_iii_refinement_gate",
        "source_gate": source_gate,
        "held2_readiness_gate": readiness_gate,
        "electrolyte_tpd_gate": tpd_gate,
        "held2_phase_discovery": held2_phase,
        "electrolyte_stage_iii_refinement": stage_iii,
        "public_route_state": public_state,
        "blockers": [],
        "complete": True,
    }


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--case-dir", type=Path, default=check_electrolyte_gfpe_gate.DEFAULT_CASE_DIR)
    parser.add_argument("--require-source-gate", action="store_true")
    parser.add_argument("--require-readiness-gate", action="store_true")
    parser.add_argument("--require-tpd-gate", action="store_true")
    parser.add_argument("--require-held2-discovery", action="store_true")
    parser.add_argument("--require-native-stage-iii", action="store_true")
    parser.add_argument("--require-public-routes-closed", action="store_true")
    parser.add_argument("--require-complete", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    from scripts.dev.native_runtime_env import apply_native_runtime_env

    apply_native_runtime_env(os.environ)
    args = build_arg_parser().parse_args(argv)
    checker_command = sys.argv[:] if argv is None else [
        "uv",
        "run",
        "--no-sync",
        "python",
        "scripts/validation/check_electrolyte_stage_iii_refinement.py",
        *argv,
    ]
    output = evaluate_stage_iii_refinement(
        args.case_dir,
        require_source_gate=args.require_source_gate or args.require_complete,
        require_readiness_gate=args.require_readiness_gate or args.require_complete,
        require_tpd_gate=args.require_tpd_gate or args.require_complete,
        require_held2_discovery=args.require_held2_discovery or args.require_complete,
        require_native_stage_iii=args.require_native_stage_iii or args.require_complete,
        require_public_routes_closed=args.require_public_routes_closed,
        checker_command=checker_command,
    )
    if args.require_complete:
        receipt = output.get("electrolyte_stage_iii_refinement", {}).get("native_freshness_receipt", {})
        if receipt:
            from scripts.validation import native_freshness

            try:
                native_freshness.require_equilibrium_native_fresh(dict(receipt))
            except ValueError as exc:
                print(str(exc), file=sys.stderr)
                return 2
    if args.json:
        print(json.dumps(output, indent=2, sort_keys=True))
    else:
        print(f"complete={output['complete']} blockers={','.join(output['blockers'])}")
    if args.require_complete and not output["complete"]:
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
