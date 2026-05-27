from __future__ import annotations

import argparse
import itertools
import json
import math
import os
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = REPO_ROOT / "src"
for import_root in (REPO_ROOT, SRC_ROOT):
    import_path = str(import_root)
    if import_path not in sys.path:
        sys.path.insert(0, import_path)

from scripts.dev.native_runtime_env import apply_native_runtime_env

apply_native_runtime_env(os.environ)

import epcsaft._core as _core
from scripts.validation import check_equilibrium_benchmark_readiness as readiness
from scripts.validation import check_stage9_phase_discovery_evidence as phase_discovery_checker
from scripts.validation import equilibrium_validation_runtime as runtime

DEFAULT_CASE_DIR = runtime.DEFAULT_NEUTRAL_TP_FLASH_CASE_DIR


def _phase_totals(route_payload: dict[str, Any]) -> list[float]:
    postsolve = route_payload.get("postsolve")
    if isinstance(postsolve, dict) and isinstance(postsolve.get("phase_amount_totals"), list):
        return [float(value) for value in postsolve["phase_amount_totals"]]
    return [float(sum(phase_amounts)) for phase_amounts in route_payload.get("phase_amounts", [])]


def _best_phase_match(
    actual_compositions: list[list[float]],
    actual_fractions: list[float],
    expected_compositions: dict[str, list[float]],
    expected_fractions: dict[str, float],
) -> dict[str, Any]:
    labels = list(expected_compositions)
    best: dict[str, Any] | None = None
    for permutation in itertools.permutations(range(len(actual_compositions)), len(labels)):
        composition_errors = []
        fraction_errors = []
        mapping: dict[str, int] = {}
        for label, actual_index in zip(labels, permutation, strict=True):
            mapping[label] = actual_index
            expected = expected_compositions[label]
            actual = actual_compositions[actual_index]
            composition_errors.append(max(abs(left - right) for left, right in zip(expected, actual, strict=True)))
            fraction_errors.append(abs(expected_fractions[label] - actual_fractions[actual_index]))
        candidate = {
            "phase_index_by_expected_label": mapping,
            "max_composition_abs_error": max(composition_errors),
            "max_phase_fraction_abs_error": max(fraction_errors),
        }
        if best is None or (
            candidate["max_composition_abs_error"] + candidate["max_phase_fraction_abs_error"]
            < best["max_composition_abs_error"] + best["max_phase_fraction_abs_error"]
        ):
            best = candidate
    if best is None:
        raise ValueError("No phase match could be constructed")
    return best


def _run_route_payload(case_dir: Path, metadata: dict[str, Any], *, debug: bool) -> dict[str, Any]:
    rows = runtime.case_rows(case_dir)
    species = runtime.species(rows, metadata)
    mix = runtime.mixture(case_dir, species)
    feed = rows["feed"]
    request = {
        "route": "neutral_tp_flash",
        "temperature": float(feed["temperature_K"]),
        "pressure": float(feed["pressure_MPa"]) * 1.0e6,
        "composition": runtime.composition(feed),
        "composition_role": "feed",
    }
    return dict(
        _core._native_equilibrium_selector_route_result(
            mix._native,
            request,
            260,
            1.0e-8,
            0.0,
            "auto",
            50 if debug else 8,
            1.0e-8,
            1.0e-3,
            1.0e-8,
            1.0e-8,
            {},
            linear_solver="auto",
            print_level=5 if debug else 0,
        )
    )


def _run_route(
    case_dir: Path,
    metadata: dict[str, Any],
    *,
    debug: bool,
    show_native_output: bool,
    redirect_native_output_to_stderr: bool,
) -> dict[str, Any]:
    if show_native_output:
        return _run_route_payload(case_dir, metadata, debug=debug)
    if redirect_native_output_to_stderr:
        with runtime.redirect_native_stdout_to_stderr():
            return _run_route_payload(case_dir, metadata, debug=debug)
    with runtime.suppress_native_stdout():
        return _run_route_payload(case_dir, metadata, debug=debug)


def evaluate_neutral_flash(
    case_dir: Path,
    phase_discovery_payload: dict[str, Any] | None,
    *,
    debug: bool = False,
    show_native_output: bool = False,
    redirect_native_output_to_stderr: bool = False,
) -> dict[str, Any]:
    metadata = json.loads((case_dir / "metadata.json").read_text(encoding="utf-8"))
    readiness_payload = readiness.evaluate_case_dir(case_dir, phase_discovery_payload=phase_discovery_payload)
    blockers = list(readiness_payload["blockers"])
    route_payload: dict[str, Any] | None = None
    comparison: dict[str, Any] | None = None
    route_accepted = False
    if readiness_payload["executable"]:
        route_payload = _run_route(
            case_dir,
            metadata,
            debug=debug,
            show_native_output=show_native_output,
            redirect_native_output_to_stderr=redirect_native_output_to_stderr,
        )
        postsolve = route_payload.get("postsolve")
        postsolve = postsolve if isinstance(postsolve, dict) else {}
        actual_compositions = [list(map(float, row)) for row in postsolve.get("phase_compositions", [])]
        phase_totals = _phase_totals(route_payload)
        total_amount = sum(phase_totals)
        actual_fractions = [amount / total_amount for amount in phase_totals] if total_amount > 0.0 else []
        case_rows = runtime.case_rows(case_dir)
        expected_compositions = {
            "liquid": runtime.composition(case_rows["liquid"]),
            "vapor": runtime.composition(case_rows["vapor"]),
        }
        expected_fractions = runtime.expected_phase_fractions(case_dir)
        comparison = _best_phase_match(
            actual_compositions,
            actual_fractions,
            expected_compositions,
            expected_fractions,
        )
        tolerances = metadata["acceptance_tolerances"]
        route_accepted = (
            route_payload.get("status") == "production_accepted"
            and route_payload.get("solver_status") == "success"
            and route_payload.get("application_status") == "solve_succeeded"
            and route_payload.get("accepted") is True
            and route_payload.get("hessian_approximation") == "exact"
            and route_payload.get("exact_hessian_available") is True
            and int(route_payload.get("eval_h_calls", 0)) > 0
            and postsolve.get("accepted") is True
            and postsolve.get("stability_accepted") is True
            and comparison["max_composition_abs_error"] <= tolerances["composition_abs"]
            and comparison["max_phase_fraction_abs_error"] <= tolerances["phase_fraction_abs"]
            and float(postsolve.get("material_balance_norm", math.inf)) <= tolerances["material_balance_abs"]
            and float(postsolve.get("pressure_consistency_norm", math.inf)) <= tolerances["pressure_abs_Pa"]
            and float(postsolve.get("ln_fugacity_consistency_norm", math.inf)) <= tolerances["ln_fugacity_abs"]
        )
        if not route_accepted:
            if route_payload.get("solver_status") != "success":
                blockers.append(f"neutral_flash_route_solver_not_converged_{route_payload.get('solver_status', 'unknown')}")
            if route_payload.get("application_status") != "solve_succeeded":
                blockers.append(
                    f"neutral_flash_route_application_not_converged_{route_payload.get('application_status', 'unknown')}"
                )
            blockers.append("neutral_flash_route_validation_failed")
    validation_complete = readiness_payload["executable"] and route_accepted and not blockers
    route_summary = None
    if route_payload is not None:
        seed_attempts = list(route_payload.get("seed_attempts") or ())
        route_summary = {
            "status": route_payload.get("status"),
            "solver_status": route_payload.get("solver_status"),
            "application_status": route_payload.get("application_status"),
            "accepted": route_payload.get("accepted"),
            "hessian_approximation": route_payload.get("hessian_approximation"),
            "hessian_backend": route_payload.get("hessian_backend"),
            "exact_hessian_available": route_payload.get("exact_hessian_available"),
            "eval_h_calls": route_payload.get("eval_h_calls"),
            "ipopt_print_level": route_payload.get("ipopt_print_level"),
            "max_iterations": route_payload.get("max_iterations"),
            "iteration_count": route_payload.get("iteration_count"),
            "iteration_history_limit": route_payload.get("iteration_history_limit"),
            "iteration_history_size": route_payload.get("iteration_history_size"),
            "iteration_history": route_payload.get("iteration_history"),
            "scaled_acceptance_passed": route_payload.get("scaled_acceptance_passed"),
            "seed_attempt_count": len(seed_attempts),
            "seed_attempts": seed_attempts,
            "postsolve": route_payload.get("postsolve"),
        }
    return {
        "case_label": metadata["case_label"],
        "family_label": metadata["family_label"],
        "proof_status": "complete" if validation_complete else "blocked",
        "proof_complete": validation_complete,
        "readiness": readiness_payload,
        "route": route_summary,
        "comparison": comparison,
        "blockers": list(dict.fromkeys(blockers)),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the neutral TP flash fixture check.")
    parser.add_argument("--case-dir", type=Path, default=DEFAULT_CASE_DIR)
    phase_discovery_source = parser.add_mutually_exclusive_group(required=True)
    phase_discovery_source.add_argument(
        "--stage9-evidence-json",
        dest="phase_discovery_json",
        type=Path,
        help="Read a previously generated phase-discovery JSON payload.",
    )
    phase_discovery_source.add_argument(
        "--generate-stage9-evidence",
        dest="generate_phase_discovery",
        action="store_true",
        help="Generate phase-discovery route-refinement data before running the fixture check.",
    )
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Use Ipopt print_level=5, retain more iteration history, and expose native iteration output.",
    )
    parser.add_argument(
        "--require-proof",
        dest="require_complete",
        action="store_true",
        help="Return a failing exit code unless the neutral TP flash check completes.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.debug:
        os.environ["EPCSAFT_EQUILIBRIUM_DEBUG"] = "1"
    show_native_output = args.debug and not args.json
    redirect_native_output_to_stderr = args.debug and args.json
    if args.generate_phase_discovery:
        phase_discovery_payload = phase_discovery_checker.evaluate_phase_discovery(
            include_route_refinement=True,
            show_native_output=show_native_output,
            redirect_native_output_to_stderr=redirect_native_output_to_stderr,
        )
        phase_discovery_source = "generated"
    else:
        phase_discovery_payload = json.loads(args.phase_discovery_json.read_text(encoding="utf-8"))
        phase_discovery_source = str(args.phase_discovery_json)
    payload = evaluate_neutral_flash(
        args.case_dir,
        phase_discovery_payload,
        debug=args.debug,
        show_native_output=show_native_output,
        redirect_native_output_to_stderr=redirect_native_output_to_stderr,
    )
    payload["stage9_evidence_source"] = phase_discovery_source
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(f"{payload['case_label']}: {payload['proof_status']}")
        if payload["blockers"]:
            print("  blockers: " + ", ".join(str(item) for item in payload["blockers"]))
        route = payload.get("route") or {}
        if route:
            print(
                "  route: "
                f"solver={route.get('solver_status')} "
                f"application={route.get('application_status')} "
                f"iterations={route.get('iteration_count')}"
            )
            iteration_history = list(route.get("iteration_history") or ())
            if iteration_history:
                print("  last_ipopt_iterations:")
                for record in iteration_history[-5:]:
                    record = dict(record)
                    print(
                        "    "
                        f"iter={record.get('iteration')} "
                        f"objective={record.get('objective')} "
                        f"inf_pr={record.get('primal_infeasibility')} "
                        f"inf_du={record.get('dual_infeasibility')} "
                        f"mu={record.get('barrier_parameter')} "
                        f"alpha_pr={record.get('step_size_primal')} "
                        f"ls={record.get('step_trial_count')}"
                    )
        comparison = payload.get("comparison") or {}
        if comparison:
            print(
                "  comparison: "
                f"composition_abs={comparison.get('max_composition_abs_error')} "
                f"phase_fraction_abs={comparison.get('max_phase_fraction_abs_error')}"
            )
    if args.require_complete and not payload["proof_complete"]:
        print(f"{payload['case_label']} did not complete the neutral TP flash check.", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
