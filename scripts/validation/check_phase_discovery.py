from __future__ import annotations

import argparse
import json
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

from scripts.dev.native_runtime_env import apply_native_runtime_env

apply_native_runtime_env(os.environ)

from epcsaft_equilibrium._native import extension_native_core
from epcsaft.state.native_adapter import ePCSAFTMixture
from scripts.validation import equilibrium_validation_runtime as runtime

_core = extension_native_core()

PHASE_DISCOVERY_REQUIREMENTS = (
    "deterministic_screening",
    "continuous_tpd_minimization",
    "held_stage_i_stability",
    "held_stage_ii_dual_phase_discovery",
    "held_stage_iii_ipopt_refinement",
)

STAGE_II_REPLAY_SOURCE = "stage_ii_dual_loop_selected_candidates"
STAGE_II_REPLAY_SEED_NAME = "held_stage_ii_dual_loop_candidate_pair"
STAGE_III_REPLAY_SOURCE = "stage_ii_dual_loop_candidate_seed"


def _nonideal_lle_binary_mixture() -> ePCSAFTMixture:
    params = {
        "m": np.asarray([1.0, 2.0]),
        "s": np.asarray([3.5, 4.0]),
        "e": np.asarray([150.0, 250.0]),
        "k_ij": np.asarray([[0.0, 0.5], [0.5, 0.0]]),
    }
    return ePCSAFTMixture.from_params(params, species=["A", "B"])


def _equilibrium_debug_enabled() -> bool:
    return os.environ.get("EPCSAFT_EQUILIBRIUM_DEBUG", "").strip().lower() in {"1", "true", "yes", "on"}


def _native_ipopt_compiled(*, show_native_output: bool = False) -> bool:
    try:
        if show_native_output:
            return bool(_core._native_ipopt_smoke()["compiled"])
        with runtime.suppress_native_stdout():
            return bool(_core._native_ipopt_smoke()["compiled"])
    except Exception:
        return False


def _phase_discovery_payload(mix: ePCSAFTMixture) -> dict[str, Any]:
    return dict(
        _core._native_neutral_tpd_phase_discovery(
            mix._native,
            225.0,
            1.0e6,
            [0.5, 0.5],
            [0, 0],
            1.0e-6,
            1.0e-6,
        )
    )


def _route_refinement_payload(mix: ePCSAFTMixture) -> dict[str, Any]:
    return dict(
        _core._native_equilibrium_selector_route_result(
            mix._native,
            {
                "route": "neutral_lle",
                "temperature": 225.0,
                "pressure": 1.0e6,
                "composition": [0.5, 0.5],
                "composition_role": "feed",
            },
            260,
            1.0e-6,
            0.0,
            "auto",
            50 if _equilibrium_debug_enabled() else 8,
            1.0e-8,
            1.0e-3,
            1.0e-6,
            1.0e-6,
            {},
            linear_solver="auto",
            option_profile="held_refinement",
            print_level=5 if _equilibrium_debug_enabled() else 0,
            acceptable_tolerance=1.0e-7,
            constraint_violation_tolerance=1.0e-7,
            dual_infeasibility_tolerance=1.0e-8,
            complementarity_tolerance=1.0e-8,
        )
    )


def _route_refinement_result(
    mix: ePCSAFTMixture,
    *,
    show_native_output: bool = False,
    redirect_native_output_to_stderr: bool = False,
) -> dict[str, Any] | None:
    if not _native_ipopt_compiled(show_native_output=show_native_output):
        return None
    if show_native_output:
        route = _route_refinement_payload(mix)
    elif redirect_native_output_to_stderr:
        with runtime.redirect_native_stdout_to_stderr():
            route = _route_refinement_payload(mix)
    else:
        with runtime.suppress_native_stdout():
            route = _route_refinement_payload(mix)
    return dict(route)


def _continuous_candidates(discovery: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        dict(candidate)
        for candidate in discovery.get("candidates", ())
        if dict(candidate).get("tpd_backend") == "continuous_coordinate_search"
    ]


def _route_solver_converged(route_payload: dict[str, Any]) -> bool:
    return (
        route_payload.get("solver_status") == "success"
        and route_payload.get("application_status") == "solve_succeeded"
    )


def _float_sequence(payload: dict[str, Any], key: str) -> list[float]:
    value = payload.get(key)
    if not isinstance(value, list):
        return []
    return [float(item) for item in value]


def evaluate_phase_discovery(
    *,
    include_route_refinement: bool = False,
    show_native_output: bool = False,
    redirect_native_output_to_stderr: bool = False,
) -> dict[str, Any]:
    mix = _nonideal_lle_binary_mixture()
    discovery = _phase_discovery_payload(mix)
    route_payload = (
        _route_refinement_result(
            mix,
            show_native_output=show_native_output,
            redirect_native_output_to_stderr=redirect_native_output_to_stderr,
        )
        if include_route_refinement
        else None
    )
    route_postsolve = None if route_payload is None else dict(route_payload["postsolve"])
    continuous_candidates = _continuous_candidates(discovery)
    lower_bound_history = _float_sequence(discovery, "held_stage_ii_lower_bound_history")
    upper_bound_history = _float_sequence(discovery, "held_stage_ii_upper_bound_history")
    bound_gap_history = _float_sequence(discovery, "held_stage_ii_bound_gap_history")
    stage_ii_major_iterations = int(discovery.get("held_stage_ii_major_iterations", 0))
    stage_ii_bound_tolerance = float(discovery.get("held_stage_ii_bound_tolerance", 0.0))
    stage_ii_bound_gap = float(discovery.get("held_stage_ii_bound_gap", 0.0))
    rejected_reasons = list(discovery.get("held_stage_ii_rejected_candidate_reasons", ()))
    replay_candidate_count = int(discovery.get("held_stage_ii_replay_candidate_count", 0))
    selected_candidate_count = int(discovery.get("selected_candidate_count", 0))
    route_stage_ii_replay_candidate_count = (
        0
        if route_postsolve is None
        else int(route_postsolve.get("held_stage_ii_replay_candidate_count", 0))
    )

    requirement_status = {
        "deterministic_screening": "missing",
        "continuous_tpd_minimization": "missing",
        "held_stage_i_stability": "missing",
        "held_stage_ii_dual_phase_discovery": "missing",
        "held_stage_iii_ipopt_refinement": "missing",
    }

    if (
        discovery.get("deterministic_screening_status") == "completed"
        and discovery.get("deterministic_screening_is_full_held") is False
        and int(discovery.get("deterministic_candidate_count", 0)) > 0
    ):
        requirement_status["deterministic_screening"] = "verified_not_full_held"

    if (
        discovery.get("continuous_tpd_status") == "converged"
        and discovery.get("continuous_tpd_backend") == "continuous_coordinate_search"
        and int(discovery.get("continuous_tpd_start_count", 0)) > 0
        and discovery.get("continuous_tpd_solve_count") == discovery.get("continuous_tpd_start_count")
        and discovery.get("continuous_tpd_converged_count") == discovery.get("continuous_tpd_solve_count")
        and continuous_candidates
        and all(candidate.get("tpd_status") == "converged" for candidate in continuous_candidates)
    ):
        requirement_status["continuous_tpd_minimization"] = "verified_converged"
    elif discovery.get("continuous_tpd_status") == "incomplete_iteration_limit":
        requirement_status["continuous_tpd_minimization"] = "incomplete_iteration_limit"

    if (
        discovery.get("held_stage_i_status")
        in {"negative_tpd_candidate_found", "no_negative_tpd_candidate_found"}
        and discovery.get("held_stage_i_start_count") == discovery.get("continuous_tpd_start_count")
        and discovery.get("continuous_tpd_status") == "converged"
    ):
        requirement_status["held_stage_i_stability"] = "verified_from_converged_continuous_tpd"

    stage_ii_history_complete = (
        stage_ii_major_iterations > 0
        and len(lower_bound_history) == stage_ii_major_iterations
        and len(upper_bound_history) == stage_ii_major_iterations
        and len(bound_gap_history) == stage_ii_major_iterations
        and abs(lower_bound_history[-1] - float(discovery.get("held_stage_ii_lower_bound", 0.0))) <= 1.0e-12
        and abs(upper_bound_history[-1] - float(discovery.get("held_stage_ii_upper_bound", 0.0))) <= 1.0e-12
        and abs(bound_gap_history[-1] - stage_ii_bound_gap) <= 1.0e-12
    )
    stage_ii_replay_ready = (
        discovery.get("held_stage_ii_replay_ready") is True
        and discovery.get("held_stage_ii_replay_source") == STAGE_II_REPLAY_SOURCE
        and discovery.get("held_stage_ii_replay_seed_name") == STAGE_II_REPLAY_SEED_NAME
        and replay_candidate_count >= selected_candidate_count >= 2
        and int(discovery.get("held_stage_ii_rejected_candidate_count", 0)) == len(rejected_reasons)
        and (
            not rejected_reasons
            or set(rejected_reasons) == {"not_selected_by_dual_loop_mass_balance_gate"}
        )
    )
    if (
        discovery.get("held_stage_ii_status") == "dual_loop_verified"
        and discovery.get("held_stage_ii_candidate_bound_audit_status") == "candidate_bound_gap_closed"
        and discovery.get("held_stage_ii_dual_loop_status") == "verified"
        and discovery.get("held_stage_ii_stopping_reason") == "bound_gap_closed"
        and stage_ii_bound_tolerance > 0.0
        and stage_ii_bound_gap <= stage_ii_bound_tolerance
        and stage_ii_history_complete
        and stage_ii_replay_ready
    ):
        requirement_status["held_stage_ii_dual_phase_discovery"] = "verified_dual_loop_replayable"
    elif discovery.get("held_stage_ii_candidate_bound_audit_status") == "candidate_bound_gap_open":
        requirement_status["held_stage_ii_dual_phase_discovery"] = "incomplete_candidate_bound_gap_open"
    elif discovery.get("held_stage_ii_status") == "candidate_bound_gap_closed":
        requirement_status["held_stage_ii_dual_phase_discovery"] = "incomplete_candidate_bound_audit_without_replay"

    if not include_route_refinement:
        if str(requirement_status["held_stage_ii_dual_phase_discovery"]).startswith("verified"):
            requirement_status["held_stage_iii_ipopt_refinement"] = "not_requested"
        else:
            requirement_status["held_stage_iii_ipopt_refinement"] = "not_requested_stage_ii_incomplete"
    elif route_postsolve is None:
        requirement_status["held_stage_iii_ipopt_refinement"] = "ipopt_dependency_required"
    elif (
        route_payload is not None
        and _route_solver_converged(route_payload)
        and route_postsolve.get("held_stage_iii_status") == "ipopt_refinement_completed_current_route"
        and int(route_postsolve.get("held_stage_iii_refined_phase_count", 0)) >= 2
        and route_postsolve.get("held_stage_iii_consumed_stage_ii_replay_metadata") is True
        and route_postsolve.get("held_stage_iii_replay_source") == STAGE_III_REPLAY_SOURCE
        and route_postsolve.get("held_stage_iii_replay_seed_name") == STAGE_II_REPLAY_SEED_NAME
        and route_stage_ii_replay_candidate_count >= 2
        and int(route_postsolve.get("held_stage_iii_replay_candidate_count", 0))
        == route_stage_ii_replay_candidate_count
        and route_postsolve.get("accepted") is True
    ):
        if str(requirement_status["held_stage_ii_dual_phase_discovery"]).startswith("verified"):
            requirement_status["held_stage_iii_ipopt_refinement"] = (
                "verified_current_route_refinement_consumed_stage_ii_replay"
            )
        else:
            requirement_status["held_stage_iii_ipopt_refinement"] = (
                "verified_current_route_refinement_pending_stage_ii_candidates"
            )
    elif (
        route_payload is not None
        and route_postsolve.get("held_stage_iii_status") == "ipopt_refinement_completed_current_route"
        and int(route_postsolve.get("held_stage_iii_refined_phase_count", 0)) >= 2
        and route_postsolve.get("accepted") is True
        and _route_solver_converged(route_payload)
    ):
        requirement_status["held_stage_iii_ipopt_refinement"] = "incomplete_missing_stage_ii_replay_seed"
    elif (
        route_payload is not None
        and route_postsolve.get("held_stage_iii_status") == "ipopt_refinement_completed_current_route"
        and int(route_postsolve.get("held_stage_iii_refined_phase_count", 0)) >= 2
        and route_postsolve.get("accepted") is True
    ):
        requirement_status["held_stage_iii_ipopt_refinement"] = (
            f"incomplete_ipopt_solver_status_{route_payload.get('solver_status', 'unknown')}"
        )

    complete = all(
        str(requirement_status[key]).startswith("verified")
        for key in PHASE_DISCOVERY_REQUIREMENTS
    )
    incomplete_requirements = [
        key
        for key in PHASE_DISCOVERY_REQUIREMENTS
        if not str(requirement_status[key]).startswith("verified")
    ]

    return {
        "case_label": "Synthetic neutral binary phase-discovery case",
        "family_label": "PE-Neutral TP Flash",
        "complete": complete,
        "requirement_status": requirement_status,
        "incomplete_requirements": incomplete_requirements,
        "diagnostics": {
            "equilibrium_debug_enabled": _equilibrium_debug_enabled(),
            "route_refinement_requested": include_route_refinement,
            "ipopt_print_level": 5 if _equilibrium_debug_enabled() else 0,
            "phase_discovery_backend": discovery.get("phase_discovery_backend"),
            "phase_discovery_steps": discovery.get("stage9_phase_discovery_steps"),
            "deterministic_candidate_count": discovery.get("deterministic_candidate_count"),
            "continuous_tpd_start_count": discovery.get("continuous_tpd_start_count"),
            "continuous_tpd_solve_count": discovery.get("continuous_tpd_solve_count"),
            "continuous_tpd_converged_count": discovery.get("continuous_tpd_converged_count"),
            "continuous_tpd_iteration_count_max": discovery.get("continuous_tpd_iteration_count_max"),
            "continuous_tpd_min": discovery.get("continuous_tpd_min"),
            "held_stage_i_status": discovery.get("held_stage_i_status"),
            "held_stage_ii_status": discovery.get("held_stage_ii_status"),
            "held_stage_ii_candidate_bound_audit_status": discovery.get(
                "held_stage_ii_candidate_bound_audit_status"
            ),
            "held_stage_ii_dual_loop_status": discovery.get("held_stage_ii_dual_loop_status"),
            "held_stage_ii_major_iterations": discovery.get("held_stage_ii_major_iterations"),
            "held_stage_ii_candidate_count": discovery.get("held_stage_ii_candidate_count"),
            "held_stage_ii_lower_bound": discovery.get("held_stage_ii_lower_bound"),
            "held_stage_ii_upper_bound": discovery.get("held_stage_ii_upper_bound"),
            "held_stage_ii_bound_gap": discovery.get("held_stage_ii_bound_gap"),
            "held_stage_ii_bound_tolerance": discovery.get("held_stage_ii_bound_tolerance"),
            "held_stage_ii_stopping_reason": discovery.get("held_stage_ii_stopping_reason"),
            "held_stage_ii_lower_bound_history": discovery.get("held_stage_ii_lower_bound_history"),
            "held_stage_ii_upper_bound_history": discovery.get("held_stage_ii_upper_bound_history"),
            "held_stage_ii_bound_gap_history": discovery.get("held_stage_ii_bound_gap_history"),
            "held_stage_ii_replay_ready": discovery.get("held_stage_ii_replay_ready"),
            "held_stage_ii_replay_source": discovery.get("held_stage_ii_replay_source"),
            "held_stage_ii_replay_seed_name": discovery.get("held_stage_ii_replay_seed_name"),
            "held_stage_ii_replay_candidate_count": discovery.get("held_stage_ii_replay_candidate_count"),
            "held_stage_ii_replay_candidate_ranks": discovery.get("held_stage_ii_replay_candidate_ranks"),
            "held_stage_ii_rejected_candidate_count": discovery.get("held_stage_ii_rejected_candidate_count"),
            "held_stage_ii_rejected_candidate_reasons": discovery.get("held_stage_ii_rejected_candidate_reasons"),
            "held_stage_iii_status": None if route_postsolve is None else route_postsolve.get("held_stage_iii_status"),
            "held_stage_iii_refined_phase_count": None
            if route_postsolve is None
            else route_postsolve.get("held_stage_iii_refined_phase_count"),
            "held_stage_iii_consumed_stage_ii_replay_metadata": None
            if route_postsolve is None
            else route_postsolve.get("held_stage_iii_consumed_stage_ii_replay_metadata"),
            "held_stage_iii_replay_source": None
            if route_postsolve is None
            else route_postsolve.get("held_stage_iii_replay_source"),
            "held_stage_iii_replay_seed_name": None
            if route_postsolve is None
            else route_postsolve.get("held_stage_iii_replay_seed_name"),
            "held_stage_iii_replay_candidate_count": None
            if route_postsolve is None
            else route_postsolve.get("held_stage_iii_replay_candidate_count"),
            "route_held_stage_ii_replay_candidate_count": None
            if route_postsolve is None
            else route_postsolve.get("held_stage_ii_replay_candidate_count"),
            "route_solver_status": None if route_payload is None else route_payload.get("solver_status"),
            "route_application_status": None if route_payload is None else route_payload.get("application_status"),
            "route_status": None if route_payload is None else route_payload.get("status"),
            "route_option_profile": None if route_payload is None else route_payload.get("option_profile"),
            "route_scaled_acceptance_passed": None
            if route_payload is None
            else route_payload.get("scaled_acceptance_passed"),
            "route_constraint_violation_tolerance": None
            if route_payload is None
            else route_payload.get("constraint_violation_tolerance"),
            "route_scaled_constraint_violation_inf_norm": None
            if route_payload is None
            else route_payload.get("scaled_constraint_violation_inf_norm"),
            "route_iteration_count": None if route_payload is None else route_payload.get("iteration_count"),
            "route_iteration_history_size": None
            if route_payload is None
            else route_payload.get("iteration_history_size"),
            "route_iteration_history_limit": None
            if route_payload is None
            else route_payload.get("iteration_history_limit"),
            "route_iteration_history": None if route_payload is None else route_payload.get("iteration_history", []),
            "route_seed_attempt_count": None
            if route_payload is None
            else len(route_payload.get("seed_attempts", ())),
            "route_seed_attempts": None if route_payload is None else route_payload.get("seed_attempts"),
        },
    }


def _print_human(payload: dict[str, Any]) -> None:
    print(f"{payload['case_label']}: {'complete' if payload['complete'] else 'incomplete'}")
    for key in PHASE_DISCOVERY_REQUIREMENTS:
        print(f"  {key}: {payload['requirement_status'][key]}")
    diagnostics = dict(payload.get("diagnostics", {}))
    if diagnostics.get("route_refinement_requested"):
        print(
            "  route_refinement: "
            f"solver={diagnostics.get('route_solver_status')} "
            f"application={diagnostics.get('route_application_status')} "
            f"iterations={diagnostics.get('route_iteration_count')} "
            f"seed_attempts={diagnostics.get('route_seed_attempt_count')}"
        )
        for attempt in diagnostics.get("route_seed_attempts") or ():
            attempt = dict(attempt)
            print(
                "    seed_attempt: "
                f"name={attempt.get('seed_name')} "
                f"solver={attempt.get('solver_status')} "
                f"application={attempt.get('application_status')} "
                f"accepted={attempt.get('accepted')} "
                f"iterations={attempt.get('iteration_count')}"
            )
        iteration_history = list(diagnostics.get("route_iteration_history") or ())
        if iteration_history:
            print("    last_ipopt_iterations:")
            for record in iteration_history[-5:]:
                record = dict(record)
                print(
                    "      ipopt_iteration: "
                    f"iter={record.get('iteration')} "
                    f"objective={record.get('objective')} "
                    f"inf_pr={record.get('primal_infeasibility')} "
                    f"inf_du={record.get('dual_infeasibility')} "
                    f"mu={record.get('barrier_parameter')} "
                    f"alpha_pr={record.get('step_size_primal')} "
                    f"ls={record.get('step_trial_count')}"
                )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Check the current phase-discovery validation status.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    parser.add_argument(
        "--debug",
        action="store_true",
        help=(
            "Enable EPCSAFT_EQUILIBRIUM_DEBUG and continuous-TPD trace rows. When "
            "--include-route-refinement is also set, use Ipopt print_level=5 for route refinement."
        ),
    )
    parser.add_argument(
        "--include-route-refinement",
        action="store_true",
        help=(
            "Also run the current Ipopt route-refinement path. "
            "The default is the cheaper phase-discovery gate without the current-route Ipopt refinement solve."
        ),
    )
    parser.add_argument(
        "--require-complete",
        action="store_true",
        help="Return a failing exit code when any phase-discovery requirement is incomplete.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.debug:
        os.environ["EPCSAFT_EQUILIBRIUM_DEBUG"] = "1"
    payload = evaluate_phase_discovery(
        include_route_refinement=args.include_route_refinement,
        show_native_output=args.debug and not args.json,
        redirect_native_output_to_stderr=args.debug and args.json and args.include_route_refinement,
    )
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        _print_human(payload)
    if args.require_complete and not payload["complete"]:
        print("Phase-discovery validation is incomplete.", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
