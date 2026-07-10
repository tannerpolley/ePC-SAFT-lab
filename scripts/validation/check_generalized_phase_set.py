"""Audit internal sampled-candidate multiphase evidence without global certification."""

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
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
from scripts.validation import native_freshness

NEUTRAL_MULTIPHASE_ROUTE = "neutral_multiphase_nonassoc"
PUBLIC_MULTIPHASE_ROUTE = "multiphase"
SAMPLED_CANDIDATE_AUDIT_STATUS = "sampled_candidate_audit_complete_global_completeness_unproven"
STAGE_II_CANDIDATE_SET_SEED = "sampled_candidate_set_replay"
STRICT_ROUTE_REFINEMENT_KIND = "strict_fugacity_residual"
MATERIAL_BALANCE_TOLERANCE = 1.0e-8
CANDIDATE_MASS_BALANCE_TOLERANCE = 1.0e-6
PRESSURE_CONSISTENCY_TOLERANCE = 1.0e-3
LN_FUGACITY_CONSISTENCY_TOLERANCE = 1.0e-6
REQUIRED_RECORD_FIELDS = {
    "record_id",
    "phase_count",
    "phase_index",
    "phase_kind",
    "phase_role",
    "source",
    "phase_amount_total",
    "phase_fraction",
    "volume",
    "density",
    "composition",
    "objective",
    "tpd",
    "feasibility_status",
    "selection_status",
    "rejection_reason",
    "phase_set_status",
    "mass_balance_feasible",
    "stability_accepted",
    "candidate_completeness_accepted",
}
GENERIC_REJECTED_PHASE_SET_REASONS = {
    "not_selected_candidate",
    "not_selected_by_generalized_phase_set_gate",
    "not_selected",
}
LOWER_FREE_ENERGY_REASONS = {
    "lower_free_energy_omitted_candidate",
    "omitted_lower_free_energy_candidate",
}


def _as_number(value: Any) -> float | None:
    if not _finite_number(value):
        return None
    return float(value)


def _phase_kinds_from_csv(value: str) -> list[str]:
    phase_kinds = [part.strip().lower() for part in value.split(",") if part.strip()]
    if not phase_kinds:
        raise ValueError("--phase-kinds requires at least one phase kind")
    allowed = {"liquid", "vapor"}
    invalid = sorted(set(phase_kinds) - allowed)
    if invalid:
        raise ValueError("--phase-kinds contains unsupported phase kind(s): " + ", ".join(invalid))
    return phase_kinds


def _phase_kind_codes(phase_kinds: list[str]) -> list[int]:
    return [0 if phase_kind == "liquid" else 1 for phase_kind in phase_kinds]


def _public_multiphase_route_exposed(public_routes: Any) -> bool:
    if not isinstance(public_routes, list):
        return False
    return PUBLIC_MULTIPHASE_ROUTE in public_routes or NEUTRAL_MULTIPHASE_ROUTE in public_routes


def _finite_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(float(value))


def _record_energy(record: dict[str, Any]) -> float | None:
    for field in ("objective", "tpd"):
        value = record.get(field)
        if _finite_number(value):
            return float(value)
    return None


def _record_composition_key(record: dict[str, Any], *, tolerance: float = 1.0e-8) -> tuple[float, ...]:
    composition = record.get("composition")
    if not isinstance(composition, list) or not composition:
        return ()
    return tuple(round(float(value) / tolerance) * tolerance for value in composition)


def evaluate_payload(payload: dict[str, Any], *, expected_phase_count: int = 3) -> dict[str, Any]:
    blockers: list[str] = []
    public_routes = payload.get("public_routes", [])
    public_route_exposure = _public_multiphase_route_exposed(public_routes)
    if public_route_exposure:
        blockers.append("public_multiphase_route_exposed")

    postsolve = payload.get("postsolve")
    if not isinstance(postsolve, dict):
        blockers.append("missing_postsolve")
        postsolve = {}
    records = postsolve.get("phase_set_records")
    if not isinstance(records, list) or not records:
        blockers.append("missing_phase_set_records")
        records = []

    selected_records: list[dict[str, Any]] = []
    rejected_records: list[dict[str, Any]] = []
    selected_keys: set[tuple[float, ...]] = set()
    for record in records:
        if not isinstance(record, dict):
            blockers.append("malformed_phase_set_record:row")
            continue
        for field in sorted(REQUIRED_RECORD_FIELDS):
            if field not in record:
                blockers.append(f"malformed_phase_set_record:{field}")
                break
        if record.get("phase_count") != expected_phase_count:
            blockers.append("non_three_phase_record")
        if record.get("phase_set_status") == "phase_set_certified":
            blockers.append("global_phase_set_claim_present")
        if (
            record.get("phase_set_status") != SAMPLED_CANDIDATE_AUDIT_STATUS
            or record.get("mass_balance_feasible") is not True
            or record.get("stability_accepted") is not False
            or record.get("candidate_completeness_accepted") is not False
        ):
            blockers.append("sampled_candidate_scope_mismatch")
        composition = record.get("composition")
        if isinstance(composition, list):
            total = sum(float(value) for value in composition)
            if not math.isfinite(total) or abs(total - 1.0) > 1.0e-6:
                blockers.append("composition_not_normalized")
        status = record.get("selection_status")
        if status == "selected":
            selected_records.append(record)
            key = _record_composition_key(record)
            if key in selected_keys:
                blockers.append("duplicate_selected_phase_compositions")
            selected_keys.add(key)
        elif status == "rejected":
            rejected_records.append(record)
            if record.get("rejection_reason") in ("", None, "accepted"):
                blockers.append("missing_rejection_reason")
        else:
            blockers.append("unknown_phase_set_selection_status")

    selected_energies = [
        energy for energy in (_record_energy(record) for record in selected_records) if energy is not None
    ]
    if selected_energies:
        selected_min_energy = min(selected_energies)
        for record in rejected_records:
            rejected_energy = _record_energy(record)
            reason = str(record.get("rejection_reason", ""))
            if (
                rejected_energy is not None
                and rejected_energy < selected_min_energy - 1.0e-12
                and reason in GENERIC_REJECTED_PHASE_SET_REASONS
            ):
                blockers.append("lower_free_energy_omitted_candidate")
            if (
                rejected_energy is not None
                and rejected_energy < selected_min_energy - 1.0e-12
                and reason in LOWER_FREE_ENERGY_REASONS
            ):
                blockers.append("lower_free_energy_rejected_candidate")

    if len(selected_records) < expected_phase_count:
        blockers.append("missing_selected_three_phase_rows")
    if not rejected_records:
        blockers.append("missing_rejected_candidate_rows")
    if postsolve.get("phase_set_mass_balance_feasible") is not True:
        blockers.append("mass_balance_infeasible")
    if postsolve.get("phase_set_status") == "phase_set_certified":
        blockers.append("global_phase_set_claim_present")
    if (
        postsolve.get("phase_set_status") != SAMPLED_CANDIDATE_AUDIT_STATUS
        or postsolve.get("candidate_completeness_accepted") is not False
        or postsolve.get("stability_accepted") is not False
        or postsolve.get("deterministic_screening_is_full_held") is not False
    ):
        blockers.append("sampled_candidate_scope_mismatch")
    if float(postsolve.get("phase_distance", 0.0) or 0.0) <= 0.0:
        blockers.append("collapsed_phase_distance")

    blockers = sorted(set(blockers))
    return {
        "complete": not blockers,
        "blockers": blockers,
        "record_summary": {
            "total": len(records),
            "selected": len(selected_records),
            "rejected": len(rejected_records),
        },
        "public_route_exposure": public_route_exposure,
        "global_phase_set_certified": False,
    }


def _requested_phase_kinds(payload: dict[str, Any]) -> list[str]:
    raw = payload.get("requested_phase_kinds")
    if isinstance(raw, list) and raw:
        out: list[str] = []
        for item in raw:
            if isinstance(item, str):
                out.append(item)
            elif item == 0:
                out.append("liquid")
            elif item == 1:
                out.append("vapor")
            else:
                out.append(str(item))
        return out
    requested_count = payload.get("requested_phase_count")
    if isinstance(requested_count, int) and requested_count > 0:
        return ["liquid"] * requested_count
    return ["liquid", "liquid", "liquid"]


def _route_seed_statuses(route_refinement: dict[str, Any]) -> list[str]:
    statuses = route_refinement.get("selected_seed_attempt_statuses")
    if isinstance(statuses, list):
        return [str(status) for status in statuses]
    attempts = route_refinement.get("seed_attempts")
    if not isinstance(attempts, list):
        return []
    out: list[str] = []
    for attempt in attempts:
        if isinstance(attempt, dict):
            status = attempt.get("status")
            if status is not None:
                out.append(str(status))
    return out


def _route_postsolve(route_refinement: dict[str, Any]) -> dict[str, Any]:
    postsolve = route_refinement.get("postsolve")
    return postsolve if isinstance(postsolve, dict) else {}


def _append_norm_blocker(
    blockers: set[str],
    payload: dict[str, Any],
    field: str,
    tolerance: float,
    blocker: str,
) -> None:
    value = _as_number(payload.get(field))
    if value is None or abs(value) > tolerance:
        blockers.add(blocker)


def evaluate_generalized_sampled_candidate_audit(payload: dict[str, Any]) -> dict[str, Any]:
    requested_phase_kinds = _requested_phase_kinds(payload)
    requested_phase_count = int(payload.get("requested_phase_count") or len(requested_phase_kinds))
    record_result = evaluate_payload(payload, expected_phase_count=requested_phase_count)
    blockers: set[str] = set(record_result["blockers"])

    postsolve = payload.get("postsolve")
    if not isinstance(postsolve, dict):
        postsolve = {}
    route_refinement = payload.get("route_refinement")
    if not isinstance(route_refinement, dict):
        blockers.add("missing_generalized_route_refinement")
        route_refinement = {}

    route_kind = route_refinement.get("route_refinement_kind")
    if route_refinement and route_kind != STRICT_ROUTE_REFINEMENT_KIND:
        blockers.add("strict_fugacity_residual_route_missing")
        blockers.add("gibbs_objective_only_route_not_certifying")
    if route_refinement and not route_refinement.get("residual_derivative_backend"):
        blockers.add("residual_derivative_metadata_missing")
    if route_refinement and (
        route_refinement.get("exact_hessian_available") is not True
        or route_refinement.get("residual_exact_hessian_available") is not True
        or route_refinement.get("residual_exact_jacobian_available") is not True
    ):
        blockers.add("residual_exact_hessian_missing")
    if route_refinement and route_refinement.get("solver_status") != "success":
        blockers.add("stage_iii_ipopt_status_not_success")
    if route_refinement and route_refinement.get("application_status") != "solve_succeeded":
        blockers.add("stage_iii_application_status_not_solve_succeeded")
    if route_refinement and route_refinement.get("accepted") is not True:
        blockers.add("stage_iii_postsolve_not_accepted")
    route_postsolve = _route_postsolve(route_refinement)
    if route_postsolve and route_postsolve.get("accepted") is not True:
        blockers.add("stage_iii_postsolve_not_accepted")
    if route_postsolve:
        _append_norm_blocker(
            blockers,
            route_postsolve,
            "ln_fugacity_consistency_norm",
            LN_FUGACITY_CONSISTENCY_TOLERANCE,
            "stage_iii_ln_fugacity_norm_above_tolerance",
        )

    if postsolve.get("held_stage_ii_replay_ready") is not True:
        blockers.add("held_stage_ii_candidate_set_replay_missing")
    if postsolve.get("held_stage_ii_replay_seed_name") != STAGE_II_CANDIDATE_SET_SEED:
        blockers.add("held_stage_ii_candidate_set_replay_missing")
    if postsolve.get("held_stage_iii_consumed_stage_ii_replay_metadata") is not True:
        blockers.add("held_stage_iii_candidate_set_replay_not_consumed")
    if postsolve.get("held_stage_iii_replay_seed_name") != STAGE_II_CANDIDATE_SET_SEED:
        blockers.add("held_stage_iii_candidate_set_replay_not_consumed")
    if postsolve.get("held_stage_iii_replay_candidate_count") != postsolve.get("held_stage_ii_replay_candidate_count"):
        blockers.add("held_stage_iii_candidate_set_replay_not_consumed")
    if postsolve.get("selected_candidate_count") != requested_phase_count:
        blockers.add("generalized_selected_phase_count_mismatch")
    if route_refinement and route_refinement.get("requested_phase_count") not in (None, requested_phase_count):
        blockers.add("generalized_selected_phase_count_mismatch")

    _append_norm_blocker(
        blockers,
        postsolve,
        "candidate_mass_balance_norm",
        CANDIDATE_MASS_BALANCE_TOLERANCE,
        "candidate_mass_balance_norm_above_tolerance",
    )
    _append_norm_blocker(
        blockers,
        postsolve,
        "material_balance_norm",
        MATERIAL_BALANCE_TOLERANCE,
        "material_balance_norm_above_tolerance",
    )
    _append_norm_blocker(
        blockers,
        postsolve,
        "pressure_consistency_norm",
        PRESSURE_CONSISTENCY_TOLERANCE,
        "pressure_consistency_norm_above_tolerance",
    )
    _append_norm_blocker(
        blockers,
        postsolve,
        "ln_fugacity_consistency_norm",
        LN_FUGACITY_CONSISTENCY_TOLERANCE,
        "ln_fugacity_consistency_norm_above_tolerance",
    )
    if (_as_number(postsolve.get("phase_distance")) or 0.0) <= 0.0:
        blockers.add("collapsed_phase_distance")
    if any(status == "max_iterations_exceeded" for status in _route_seed_statuses(route_refinement)):
        blockers.add("stage_iii_selected_seed_iteration_limit")
    ordered_blockers = sorted(blockers)
    return {
        "complete": not ordered_blockers,
        "blockers": ordered_blockers,
        "record_summary": record_result["record_summary"],
        "public_route_exposure": record_result["public_route_exposure"],
        "global_phase_set_certified": False,
        "requested_phase_kinds": requested_phase_kinds,
        "requested_phase_count": requested_phase_count,
        "selected_candidate_count": postsolve.get("selected_candidate_count", 0),
        "held_stage_iii_status": postsolve.get("held_stage_iii_status"),
        "route_refinement_kind": route_refinement.get("route_refinement_kind"),
        "admission_mode": "internal_sampled_candidate_audit",
        "native_freshness_receipt": payload.get("native_freshness_receipt", {}),
    }


def _symmetric_ternary_nonassociating_mixture() -> Any:
    from epcsaft.state.native_adapter import ePCSAFTMixture

    params = {
        "m": np.asarray([1.5, 1.5, 1.5], dtype=float),
        "s": np.asarray([3.7, 3.7, 3.7], dtype=float),
        "e": np.asarray([220.0, 220.0, 220.0], dtype=float),
        "k_ij": np.asarray(
            [
                [0.0, 0.8, 0.8],
                [0.8, 0.0, 0.8],
                [0.8, 0.8, 0.0],
            ],
            dtype=float,
        ),
    }
    return ePCSAFTMixture.from_params(params, species=["A", "B", "C"])


def _strict_route_refinement_payload(core: Any, mix: Any, phase_kinds: list[str]) -> dict[str, Any]:
    phase_kind_codes = _phase_kind_codes(phase_kinds)
    return core._native_neutral_multiphase_fugacity_residual_route_result(
        mix._native,
        200.0,
        1.0e6,
        [1.0 / len(phase_kinds) for _ in phase_kinds],
        phase_kind_codes,
        320,
        1.0e-8,
        0.0,
        "auto",
        50,
        MATERIAL_BALANCE_TOLERANCE,
        PRESSURE_CONSISTENCY_TOLERANCE,
        LN_FUGACITY_CONSISTENCY_TOLERANCE,
        LN_FUGACITY_CONSISTENCY_TOLERANCE,
        {},
        linear_solver="auto",
        option_profile="held_refinement",
        print_level=0,
        acceptable_tolerance=1.0e-8,
        constraint_violation_tolerance=1.0e-8,
        dual_infeasibility_tolerance=1.0e-8,
        complementarity_tolerance=1.0e-8,
    )


def run_generalized_sampled_candidate_audit(
    *,
    phase_kinds: list[str],
    run_route_refinement: bool,
    checker_command: list[str],
) -> dict[str, Any]:
    from scripts.dev.native_runtime_env import apply_native_runtime_env

    apply_native_runtime_env(os.environ)

    import epcsaft_equilibrium
    from epcsaft_equilibrium._native import extension_native_core

    core = extension_native_core()
    mix = _symmetric_ternary_nonassociating_mixture()
    if run_route_refinement and len(phase_kinds) >= 3:
        route_refinement = _strict_route_refinement_payload(core, mix, phase_kinds)
        postsolve = route_refinement.get("postsolve", {})
    else:
        postsolve = core._native_neutral_tpd_phase_discovery(
            mix._native,
            200.0,
            1.0e6,
            [1.0 / len(phase_kinds) for _ in phase_kinds],
            _phase_kind_codes(phase_kinds),
            1.0e-6,
            1.0e-6,
            True,
        )
        route_refinement = None
    receipt = native_freshness.build_equilibrium_native_receipt(native_module=core, checker_command=checker_command)
    payload: dict[str, Any] = {
        "requested_phase_kinds": phase_kinds,
        "requested_phase_count": len(phase_kinds),
        "public_routes": epcsaft_equilibrium.capabilities()["public_routes"],
        "native_freshness_receipt": native_freshness.receipt_to_jsonable(receipt),
        "postsolve": postsolve,
    }
    if route_refinement is not None:
        payload["route_refinement"] = route_refinement
    return payload


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--require-complete", action="store_true")
    parser.add_argument("--phase-kinds", default="liquid,liquid,liquid")
    parser.add_argument("--run-route-refinement", action="store_true")
    parser.add_argument("--require-route-refinement", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_arg_parser().parse_args(argv)
    phase_kinds = _phase_kinds_from_csv(args.phase_kinds)
    checker_command = (
        sys.argv[:]
        if argv is None
        else [
            "uv",
            "run",
            "--no-sync",
            "python",
            "scripts/validation/check_generalized_phase_set.py",
            *argv,
        ]
    )
    payload = run_generalized_sampled_candidate_audit(
        phase_kinds=phase_kinds,
        run_route_refinement=args.run_route_refinement or args.require_route_refinement,
        checker_command=checker_command,
    )
    if args.run_route_refinement or args.require_route_refinement:
        result = evaluate_generalized_sampled_candidate_audit(payload)
        if args.require_route_refinement and "missing_generalized_route_refinement" in result["blockers"]:
            result["complete"] = False
        output = {
            **result,
            "route": NEUTRAL_MULTIPHASE_ROUTE,
            "checker": "generalized_sampled_candidate_refinement_audit",
            "scope": "internal_neutral_multiphase_sampled_candidate_refinement",
        }
    else:
        result = evaluate_payload(payload)
        output = {
            **result,
            "route": NEUTRAL_MULTIPHASE_ROUTE,
            "checker": "generalized_sampled_candidate_audit",
            "scope": "internal_neutral_multiphase_sampled_candidate_diagnostics",
            "admission_mode": "internal_sampled_candidate_audit",
            "native_freshness_receipt": payload["native_freshness_receipt"],
        }
    if args.require_complete:
        try:
            native_freshness.require_equilibrium_native_fresh(dict(output.get("native_freshness_receipt", {})))
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
