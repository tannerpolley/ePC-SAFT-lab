from __future__ import annotations

import argparse
import json
import math
import os
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = REPO_ROOT / "src"
EQUILIBRIUM_SRC_ROOT = REPO_ROOT / "packages" / "epcsaft-equilibrium" / "src"
for import_root in (REPO_ROOT, SRC_ROOT, EQUILIBRIUM_SRC_ROOT):
    import_path = str(import_root)
    if import_path not in sys.path:
        sys.path.insert(0, import_path)

from scripts.dev.native_runtime_env import apply_native_runtime_env

apply_native_runtime_env(os.environ)

from epcsaft_equilibrium._native import extension_native_core
from epcsaft_equilibrium.core.native_results import native_route_solved_pressure, native_route_solved_temperature
from scripts.validation import equilibrium_validation_runtime as runtime

_core = extension_native_core()

DEFAULT_CASE_DIR = runtime.DEFAULT_NEUTRAL_TP_FLASH_CASE_DIR

BOUNDARY_ROUTES: dict[str, dict[str, Any]] = {
    "bubble_pressure": {
        "workflow_label": "Bubble point",
        "diagram_target": "P-x",
        "source_phase": "liquid",
        "composition_role": "liquid",
        "boundary_variable": "P",
        "fixed_variables": ("T", "x"),
        "free_variables": ("P", "y", "phase_volumes"),
    },
    "bubble_temperature": {
        "workflow_label": "Bubble point",
        "diagram_target": "T-x",
        "source_phase": "liquid",
        "composition_role": "liquid",
        "boundary_variable": "T",
        "fixed_variables": ("P", "x"),
        "free_variables": ("T", "y", "phase_volumes"),
    },
    "dew_pressure": {
        "workflow_label": "Dew point",
        "diagram_target": "P-x",
        "source_phase": "vapor",
        "composition_role": "vapor",
        "boundary_variable": "P",
        "fixed_variables": ("T", "y"),
        "free_variables": ("P", "x", "phase_volumes"),
    },
    "dew_temperature": {
        "workflow_label": "Dew point",
        "diagram_target": "T-x",
        "source_phase": "vapor",
        "composition_role": "vapor",
        "boundary_variable": "T",
        "fixed_variables": ("P", "y"),
        "free_variables": ("T", "x", "phase_volumes"),
    },
}


def _workflow_contracts(route_points_by_label: dict[str, list[dict[str, Any]]] | None = None) -> list[dict[str, Any]]:
    route_points_by_label = route_points_by_label or {}
    workflows = [
        {
            "label": "Bubble point",
            "workflow_kind": "derived_boundary",
            "activation_family_row": False,
            "runtime_status": "executable_current_routes",
            "routes": ["bubble_pressure", "bubble_temperature"],
            "fixed_variables": ["temperature_or_pressure", "liquid_or_feed_composition"],
            "free_variables": ["incipient_vapor_composition", "phase_volumes", "boundary_pressure_or_temperature"],
            "diagram_targets": ["P-x", "T-x"],
        },
        {
            "label": "Dew point",
            "workflow_kind": "derived_boundary",
            "activation_family_row": False,
            "runtime_status": "executable_current_routes",
            "routes": ["dew_pressure", "dew_temperature"],
            "fixed_variables": ["temperature_or_pressure", "vapor_composition"],
            "free_variables": ["incipient_liquid_composition", "phase_volumes", "boundary_pressure_or_temperature"],
            "diagram_targets": ["P-x", "T-x"],
        },
        {
            "label": "Cloud point",
            "workflow_kind": "derived_boundary",
            "activation_family_row": False,
            "runtime_status": "planned_not_executable",
            "routes": [],
            "fixed_variables": ["temperature_or_pressure", "parent_liquid_composition"],
            "free_variables": [
                "incipient_second_liquid_composition",
                "phase_volumes",
                "boundary_pressure_or_temperature",
            ],
            "diagram_targets": ["P-x", "T-x"],
        },
        {
            "label": "Shadow point",
            "workflow_kind": "derived_boundary",
            "activation_family_row": False,
            "runtime_status": "planned_not_executable",
            "routes": [],
            "fixed_variables": ["cloud_state"],
            "free_variables": ["incipient_phase_composition", "incipient_phase_volume"],
            "diagram_targets": ["P-x", "T-x"],
        },
    ]
    for workflow in workflows:
        route_points = list(route_points_by_label.get(workflow["label"], []))
        workflow["route_points"] = route_points
        if workflow["runtime_status"] == "planned_not_executable":
            workflow["route_point_status"] = "planned_not_executable"
        elif not route_points:
            workflow["route_point_status"] = "not_requested"
        elif all(point["status"] == "accepted" for point in route_points):
            workflow["route_point_status"] = "complete"
        else:
            workflow["route_point_status"] = "blocked"
    return workflows


def _native_ipopt_compiled() -> bool:
    try:
        with runtime.suppress_native_stdout():
            return bool(_core._native_ipopt_smoke()["compiled"])
    except Exception:
        return False


def _composition_samples(base: list[float], count: int) -> list[list[float]]:
    if count < 1:
        raise ValueError("--route-point-count must be greater than zero")
    if count == 1:
        return [base]
    if len(base) < 2:
        return [base for _ in range(count)]
    span = min(0.02, 0.25 * base[0], 0.25 * base[-1])
    offsets = [-span + 2.0 * span * index / (count - 1) for index in range(count)]
    samples: list[list[float]] = []
    for offset in offsets:
        sample = list(base)
        sample[0] += offset
        sample[-1] -= offset
        total = sum(sample)
        if total <= 0.0 or any(value <= 0.0 for value in sample):
            raise ValueError("Generated boundary route-point composition left the positive simplex")
        samples.append([value / total for value in sample])
    return samples


def _route_request(
    route: str,
    spec: dict[str, Any],
    row: dict[str, str],
    composition: list[float],
) -> dict[str, Any]:
    request: dict[str, Any] = {
        "route": route,
        "composition": composition,
        "composition_role": spec["composition_role"],
    }
    if spec["boundary_variable"] == "P":
        request["temperature"] = float(row["temperature_K"])
    else:
        request["pressure"] = float(row["pressure_MPa"]) * 1.0e6
    return request


def _run_native_route(
    mix: Any,
    request: dict[str, Any],
    *,
    debug: bool,
    max_iterations: int,
) -> dict[str, Any]:
    def run() -> dict[str, Any]:
        return dict(
            _core._native_equilibrium_selector_route_result(
                mix._native,
                request,
                max_iterations,
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
                option_profile="continuation_trace",
                print_level=5 if debug else 0,
                acceptable_tolerance=1.0e-7,
                constraint_violation_tolerance=1.0e-7,
                dual_infeasibility_tolerance=1.0e-8,
                complementarity_tolerance=1.0e-8,
            )
        )

    if debug:
        with runtime.redirect_native_stdout_to_stderr():
            return run()
    with runtime.suppress_native_stdout():
        return run()


def _strict_convergence(route_payload: dict[str, Any], iteration_limit_seed_attempts: list[str]) -> bool:
    return (
        route_payload.get("solver_status") == "success"
        and route_payload.get("application_status") == "solve_succeeded"
        and not iteration_limit_seed_attempts
    )


def _residuals(route_payload: dict[str, Any]) -> dict[str, float | None]:
    postsolve = route_payload.get("postsolve")
    postsolve = postsolve if isinstance(postsolve, dict) else {}
    keys = (
        "material_balance_norm",
        "pressure_consistency_norm",
        "ln_fugacity_consistency_norm",
        "phase_equilibrium_norm",
        "scaled_constraint_violation_inf_norm",
    )
    residuals: dict[str, float | None] = {}
    for key in keys:
        value = postsolve.get(key, route_payload.get(key))
        residuals[key] = float(value) if isinstance(value, (int, float)) and math.isfinite(float(value)) else None
    return residuals


def _seed_attempt_summary(route_payload: dict[str, Any]) -> list[dict[str, Any]]:
    attempts = []
    for attempt in route_payload.get("seed_attempts") or ():
        attempt = dict(attempt)
        attempts.append(
            {
                "seed_name": attempt.get("seed_name"),
                "status": attempt.get("status"),
                "solver_status": attempt.get("solver_status"),
                "application_status": attempt.get("application_status"),
                "accepted": attempt.get("accepted"),
                "iteration_count": attempt.get("iteration_count"),
                "max_iterations": attempt.get("max_iterations"),
            }
        )
    return attempts


def _iteration_limit_seed_attempts(route_payload: dict[str, Any]) -> list[str]:
    blocked = []
    for attempt in route_payload.get("seed_attempts") or ():
        attempt = dict(attempt)
        if (
            attempt.get("solver_status") == "max_iterations_exceeded"
            or attempt.get("application_status") == "maximum_iterations_exceeded"
        ):
            blocked.append(str(attempt.get("seed_name", "unnamed_seed_attempt")))
    return blocked


def _solved_boundary_value(route: str, spec: dict[str, Any], route_payload: dict[str, Any]) -> float:
    if spec["boundary_variable"] == "P":
        return native_route_solved_pressure(route_payload, route)
    return native_route_solved_temperature(route_payload, route)


def _route_point_result(
    route: str,
    sample_index: int,
    composition: list[float],
    route_payload: dict[str, Any],
) -> dict[str, Any]:
    spec = BOUNDARY_ROUTES[route]
    seed_attempts = _seed_attempt_summary(route_payload)
    iteration_limit_attempts = _iteration_limit_seed_attempts(route_payload)
    strict = _strict_convergence(route_payload, iteration_limit_attempts)
    selected_seed = route_payload.get("seed_name") or next(
        (attempt["seed_name"] for attempt in seed_attempts if attempt.get("accepted")),
        None,
    )
    return {
        "route": route,
        "diagram_target": spec["diagram_target"],
        "sample_index": sample_index,
        "status": "accepted" if strict else "blocked_nonconverged",
        "fixed_composition_role": spec["composition_role"],
        "fixed_composition": composition,
        "boundary_variable": spec["boundary_variable"],
        "solved_boundary_value": _solved_boundary_value(route, spec, route_payload),
        "route_status": route_payload.get("status"),
        "solver_status": route_payload.get("solver_status"),
        "application_status": route_payload.get("application_status"),
        "strict_convergence": strict,
        "iteration_limit_seed_attempts": iteration_limit_attempts,
        "seed_source": selected_seed,
        "seed_attempts": seed_attempts,
        "max_iterations": route_payload.get("max_iterations"),
        "iteration_count": route_payload.get("iteration_count"),
        "iteration_history_limit": route_payload.get("iteration_history_limit"),
        "iteration_history_size": route_payload.get("iteration_history_size"),
        "iteration_history": route_payload.get("iteration_history", []),
        "ipopt_print_level": route_payload.get("ipopt_print_level"),
        "option_profile": route_payload.get("option_profile"),
        "residuals": _residuals(route_payload),
    }


def _selected_routes(route: str | None) -> list[str]:
    if route is None:
        return list(BOUNDARY_ROUTES)
    return [route]


def _run_route_points(args: argparse.Namespace) -> tuple[dict[str, list[dict[str, Any]]], list[str]]:
    metadata = json.loads(args.case_dir.joinpath("metadata.json").read_text(encoding="utf-8"))
    rows = runtime.case_rows(args.case_dir)
    species = runtime.species(rows, metadata)
    mix = runtime.mixture(args.case_dir, species)
    blockers: list[str] = []
    route_points_by_label: dict[str, list[dict[str, Any]]] = {}
    for route in _selected_routes(args.route):
        spec = BOUNDARY_ROUTES[route]
        row = rows[str(spec["source_phase"])]
        samples = _composition_samples(runtime.composition(row), int(args.route_point_count))
        for sample_index, composition in enumerate(samples):
            request = _route_request(route, spec, row, composition)
            payload = _run_native_route(
                mix,
                request,
                debug=bool(args.debug),
                max_iterations=int(args.max_iterations),
            )
            point = _route_point_result(route, sample_index, composition, payload)
            route_points_by_label.setdefault(str(spec["workflow_label"]), []).append(point)
            if point["status"] != "accepted":
                blockers.append(f"{route}_strict_convergence_missing")
    return route_points_by_label, list(dict.fromkeys(blockers))


def _route_point_summary(workflows: list[dict[str, Any]]) -> dict[str, int]:
    points = [point for workflow in workflows for point in workflow["route_points"]]
    accepted = [point for point in points if point["status"] == "accepted"]
    return {
        "requested_route_point_count": len(points),
        "accepted_route_point_count": len(accepted),
        "failed_route_point_count": len(points) - len(accepted),
    }


def _source_fixture(case_dir: Path) -> str:
    try:
        return str(case_dir.resolve().relative_to(REPO_ROOT.resolve()))
    except ValueError:
        return str(case_dir.resolve())


def _base_payload(args: argparse.Namespace, workflows: list[dict[str, Any]], blockers: list[str]) -> dict[str, Any]:
    summary = _route_point_summary(workflows)
    complete = summary["requested_route_point_count"] > 0 and summary["failed_route_point_count"] == 0 and not blockers
    if not args.run_current_boundary_route:
        status = "contracts_available"
    elif complete:
        status = "complete_route_convergence"
    else:
        status = "blocked_route_convergence"
    return {
        "boundary_status": status,
        "complete": complete,
        "source_fixture": _source_fixture(args.case_dir),
        "requested_route_point_count": summary["requested_route_point_count"],
        "route_point_summary": summary,
        "blockers": blockers,
        "workflows": workflows,
    }


def evaluate(args: argparse.Namespace) -> tuple[dict[str, Any], int]:
    selected_route_count = len(_selected_routes(args.route)) if args.run_current_boundary_route else 0
    requested_route_point_count = selected_route_count * int(args.route_point_count)
    if requested_route_point_count > 1 and not args.allow_route_sweep:
        workflows = _workflow_contracts()
        payload = {
            "boundary_status": "route_sweep_rejected",
            "complete": False,
            "source_fixture": _source_fixture(args.case_dir),
            "requested_route_point_count": requested_route_point_count,
            "route_point_summary": _route_point_summary(workflows),
            "blockers": ["explicit_route_or_allow_route_sweep_required"],
            "workflows": workflows,
        }
        return payload, 2

    if args.contracts_only or not args.run_current_boundary_route:
        payload = _base_payload(args, _workflow_contracts(), [])
        return payload, 0

    if not _native_ipopt_compiled():
        payload = _base_payload(args, _workflow_contracts(), ["native_ipopt_not_compiled"])
        return payload, 2 if args.require_complete else 0

    route_points_by_label, blockers = _run_route_points(args)
    workflows = _workflow_contracts(route_points_by_label)
    payload = _base_payload(args, workflows, blockers)
    if args.require_complete and not payload["complete"]:
        return payload, 2
    return payload, 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Check derived boundary workflow contracts.")
    parser.add_argument("--case-dir", type=Path, default=DEFAULT_CASE_DIR)
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    parser.add_argument("--contracts-only", action="store_true", help="Check workflow contracts without route solves.")
    parser.add_argument(
        "--run-current-boundary-route",
        action="store_true",
        help="Run current executable bubble/dew routes. Requires one route unless --allow-route-sweep is set.",
    )
    parser.add_argument("--route", choices=tuple(BOUNDARY_ROUTES), help="Run one current boundary route.")
    parser.add_argument("--route-point-count", type=int, default=1)
    parser.add_argument(
        "--allow-route-sweep",
        action="store_true",
        help="Allow multiple route points. Keep this off for routine validation and debugging.",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Use Ipopt print_level=5 and redirect native iteration output to stderr when --json is active.",
    )
    parser.add_argument("--max-iterations", type=int, default=200)
    parser.add_argument(
        "--require-complete",
        action="store_true",
        help="Return nonzero unless every requested current boundary route point strictly converges.",
    )
    return parser


def _print_text(payload: dict[str, Any]) -> None:
    print(f"Boundary status: {payload['boundary_status']}")
    print(f"source_fixture: {payload['source_fixture']}")
    print(f"requested_route_point_count: {payload['requested_route_point_count']}")
    if payload["blockers"]:
        print("blockers:")
        for blocker in payload["blockers"]:
            print(f"  - {blocker}")
    for workflow in payload["workflows"]:
        print(
            f"{workflow['label']}: runtime={workflow['runtime_status']} "
            f"route_points={workflow['route_point_status']} points={len(workflow['route_points'])}"
        )
        for point in workflow["route_points"]:
            print(
                "  route_point: "
                f"route={point['route']} "
                f"status={point['status']} "
                f"solver={point['solver_status']} "
                f"application={point['application_status']} "
                f"iterations={point['iteration_count']} "
                f"iteration_limit_seeds={point['iteration_limit_seed_attempts']}"
            )


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    payload, exit_code = evaluate(args)
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        _print_text(payload)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
