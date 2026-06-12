from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from concurrent.futures import ProcessPoolExecutor
from concurrent.futures import as_completed
from dataclasses import asdict
from dataclasses import dataclass
from dataclasses import field
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
from scripts.validation import equilibrium_validation_runtime as runtime
from scripts.validation import native_freshness

_core = extension_native_core()

DEFAULT_CONDITIONS = 100
DEFAULT_REPEATS = 100
DEFAULT_SEED = 1729
DEFAULT_JOBS = max(1, min(8, os.cpu_count() or 1))
DEFAULT_OUTPUT_DIR = Path("analyses/package_validation/held_lle_reliability/shared/results")
FEED_GRID = [round(value, 6) for value in np.linspace(0.10, 0.90, 41)]
TEMPERATURE_GRID = [215.0, 220.0, 225.0, 230.0, 235.0]
PRESSURE_GRID = [0.8e6, 1.0e6, 1.2e6]


@dataclass(frozen=True)
class ReliabilityThresholds:
    objective_spread_abs: float = 1.0e-6
    material_balance_norm: float = 1.0e-8
    pressure_consistency_norm: float = 1.0e-3
    ln_fugacity_consistency_norm: float = 1.0e-6
    phase_distance_min: float = 1.0e-6


DEFAULT_THRESHOLDS = ReliabilityThresholds()


@dataclass
class RepeatResult:
    condition_index: int
    repeat_index: int
    accepted: bool
    temperature: float = 225.0
    pressure: float = 1.0e6
    feed_composition: list[float] = field(default_factory=lambda: [0.5, 0.5])
    random_seed: int = DEFAULT_SEED
    native_module_path: str = ""
    stage_statuses: dict[str, Any] = field(default_factory=dict)
    rejection_reason: str = "accepted"
    pressure_transformed_objective: float = 0.0
    phase_count: int = 2
    selected_phase_roles: list[str] = field(default_factory=lambda: ["liquid", "liquid"])
    continuous_tpd_status: str = "converged"
    held_stage_ii_status: str = "dual_loop_verified"
    held_stage_ii_dual_loop_status: str = "verified"
    held_stage_ii_bound_gap: float = 0.0
    held_stage_ii_bound_tolerance: float = 1.0e-6
    held_stage_iii_status: str = "ipopt_refinement_completed_current_route"
    held_stage_iii_consumed_stage_ii_replay_metadata: bool = True
    solver_status: str = "success"
    application_status: str = "solve_succeeded"
    material_balance_norm: float = 0.0
    pressure_consistency_norm: float = 0.0
    ln_fugacity_consistency_norm: float = 0.0
    phase_distance: float = 1.0
    selected_candidate_count: int = 2
    run_id: str = ""
    process_id: int = 0
    native_start_policy: str = "deterministic_multistart"
    stage_i_start_count: int = 1
    candidate_start_sources: list[str] = field(default_factory=lambda: ["feed_phase_kind_0"])
    stage_ii_stopping_reason: str = "bound_gap_closed"
    hidden_state_carryover_allowed: bool = False


@dataclass
class ConditionResult:
    condition_index: int
    accepted: bool
    repeats: list[RepeatResult] = field(default_factory=list)
    temperature: float = 225.0
    pressure: float = 1.0e6
    feed_composition: list[float] = field(default_factory=lambda: [0.5, 0.5])
    rejection_reason: str = "accepted"


def accepted_repeat_for_test(
    *,
    condition_index: int = 0,
    repeat_index: int = 0,
    pressure_transformed_objective: float = 0.0,
) -> RepeatResult:
    return RepeatResult(
        condition_index=condition_index,
        repeat_index=repeat_index,
        accepted=True,
        pressure_transformed_objective=pressure_transformed_objective,
        run_id=f"condition-{condition_index:03d}-repeat-{repeat_index:03d}",
        process_id=os.getpid(),
        native_module_path="C:/repo/epcsaft_equilibrium/_native_core.pyd",
        stage_statuses={
            "continuous_tpd_status": "converged",
            "held_stage_ii_status": "dual_loop_verified",
            "held_stage_iii_status": "ipopt_refinement_completed_current_route",
        },
    )


def summarize_campaign(
    *,
    conditions: list[ConditionResult],
    required_conditions: int,
    required_repeats: int,
    thresholds: ReliabilityThresholds = DEFAULT_THRESHOLDS,
    seed: int = DEFAULT_SEED,
    native_receipt: dict[str, Any] | None = None,
) -> dict[str, Any]:
    accepted_conditions = [condition for condition in conditions if condition.accepted]
    attempted_repeats = sum(len(condition.repeats) for condition in accepted_conditions)
    failed_repeats = sum(
        1
        for condition in accepted_conditions
        for repeat in condition.repeats
        if not repeat.accepted
    )
    blockers: list[str] = []
    condition_summaries: list[dict[str, Any]] = []
    first_failure: dict[str, Any] | None = None

    if len(accepted_conditions) != required_conditions:
        blockers.append("accepted_condition_count_mismatch")
    if attempted_repeats != required_conditions * required_repeats:
        blockers.append("attempted_repeat_count_mismatch")
    if failed_repeats:
        blockers.append("failed_repeat")

    for condition in accepted_conditions:
        repeats = condition.repeats
        if len(repeats) != required_repeats:
            blockers.append("repeat_count_mismatch")

        accepted_repeats = [repeat for repeat in repeats if repeat.accepted]
        objectives = [repeat.pressure_transformed_objective for repeat in accepted_repeats]
        objective_spread = 0.0 if len(objectives) <= 1 else max(objectives) - min(objectives)
        phase_counts = sorted({repeat.phase_count for repeat in accepted_repeats})
        phase_role_sets = sorted({tuple(repeat.selected_phase_roles) for repeat in accepted_repeats})
        condition_summaries.append(
            {
                "condition_index": condition.condition_index,
                "accepted": condition.accepted,
                "repeat_count": len(repeats),
                "failed_repeats": len(repeats) - len(accepted_repeats),
                "objective_spread": objective_spread,
                "phase_counts": phase_counts,
                "selected_phase_roles": [list(item) for item in phase_role_sets],
            }
        )
        if objective_spread > thresholds.objective_spread_abs:
            blockers.append("objective_spread_above_tolerance")
        if len(phase_counts) > 1:
            blockers.append("phase_count_mismatch")
        if len(phase_role_sets) > 1:
            blockers.append("selected_phase_roles_mismatch")

        for repeat in repeats:
            if not repeat.accepted and first_failure is None:
                first_failure = _first_failure_reproduction(repeat)
                continue
            if repeat.accepted:
                blockers.extend(_accepted_repeat_blockers(repeat, thresholds))

    blockers = _dedupe(blockers)
    return {
        "complete": not blockers,
        "blockers": blockers,
        "accepted_conditions": len(accepted_conditions),
        "attempted_repeats": attempted_repeats,
        "failed_repeats": failed_repeats,
        "seed": seed,
        "thresholds": asdict(thresholds),
        "native_receipt": native_receipt,
        "first_failure": first_failure,
        "condition_summaries": condition_summaries,
    }


def run_campaign(
    *,
    conditions: int,
    repeats: int,
    seed: int,
    checker_command: list[str],
    output_dir: Path,
    jobs: int = DEFAULT_JOBS,
) -> dict[str, Any]:
    receipt = native_freshness.build_receipt(native_module=_core, checker_command=checker_command)
    results: list[ConditionResult] = []
    accepted_by_index: dict[int, ConditionResult] = {}
    accepted_count = 0
    for temperature, pressure, feed_z0 in _candidate_conditions(seed):
        condition_index = accepted_count
        feed = [feed_z0, round(1.0 - feed_z0, 6)]
        repeat_results: list[RepeatResult] = []
        first_repeat = _run_native_repeat(
            condition_index=condition_index,
            repeat_index=0,
            temperature=temperature,
            pressure=pressure,
            feed_composition=feed,
            random_seed=seed,
        )
        if not first_repeat.accepted:
            results.append(
                ConditionResult(
                    condition_index=len(results),
                    accepted=False,
                    temperature=temperature,
                    pressure=pressure,
                    feed_composition=feed,
                    rejection_reason=first_repeat.rejection_reason,
                )
            )
            continue

        repeat_results.append(first_repeat)
        condition = ConditionResult(
            condition_index=condition_index,
            accepted=True,
            repeats=repeat_results,
            temperature=temperature,
            pressure=pressure,
            feed_composition=feed,
        )
        results.append(condition)
        accepted_by_index[condition_index] = condition
        accepted_count += 1
        _log_progress(f"accepted_conditions={accepted_count}/{conditions}")
        if accepted_count == conditions:
            break

    _run_remaining_repeats(
        accepted_conditions=accepted_by_index,
        repeats=repeats,
        seed=seed,
        jobs=jobs,
    )

    summary = summarize_campaign(
        conditions=results,
        required_conditions=conditions,
        required_repeats=repeats,
        seed=seed,
        native_receipt=native_freshness.receipt_to_jsonable(receipt),
    )
    _write_outputs(output_dir=output_dir, summary=summary, conditions=results)
    return summary


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the HELD neutral LLE reliability campaign.")
    parser.add_argument("--family", choices=["neutral-lle"], default="neutral-lle")
    parser.add_argument("--conditions", type=int, default=DEFAULT_CONDITIONS)
    parser.add_argument("--repeats", type=int, default=DEFAULT_REPEATS)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--jobs", type=int, default=DEFAULT_JOBS)
    parser.add_argument("--require-complete", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    return parser


def repeat_rows_for_output(conditions: list[ConditionResult]) -> list[dict[str, Any]]:
    return [
        _repeat_row(repeat)
        for condition in conditions
        for repeat in condition.repeats
    ]


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    checker_command = sys.argv[:] if argv is None else [
        "uv",
        "run",
        "--no-sync",
        "python",
        "scripts/validation/check_held_reliability.py",
        *argv,
    ]
    summary = run_campaign(
        conditions=args.conditions,
        repeats=args.repeats,
        seed=args.seed,
        checker_command=checker_command,
        output_dir=args.output_dir,
        jobs=args.jobs,
    )
    if args.json:
        print(json.dumps(summary, indent=2, sort_keys=True))
    else:
        _print_human(summary)
    if args.require_complete and not summary["complete"]:
        print("HELD neutral LLE reliability campaign is incomplete.", file=sys.stderr)
        return 2
    return 0


def _candidate_conditions(seed: int) -> list[tuple[float, float, float]]:
    candidates = [
        (temperature, pressure, feed_z0)
        for feed_z0 in FEED_GRID
        for temperature in TEMPERATURE_GRID
        for pressure in PRESSURE_GRID
    ]
    rng = np.random.default_rng(seed)
    order = rng.permutation(len(candidates))
    return [candidates[int(index)] for index in order]


def _run_remaining_repeats(
    *,
    accepted_conditions: dict[int, ConditionResult],
    repeats: int,
    seed: int,
    jobs: int,
) -> None:
    tasks: list[dict[str, Any]] = []
    for condition_index, condition in accepted_conditions.items():
        for repeat_index in range(1, repeats):
            tasks.append(
                {
                    "condition_index": condition_index,
                    "repeat_index": repeat_index,
                    "temperature": condition.temperature,
                    "pressure": condition.pressure,
                    "feed_composition": condition.feed_composition,
                    "random_seed": seed + condition_index * repeats + repeat_index,
                }
            )
    if not tasks:
        return
    if jobs <= 1:
        for completed, task in enumerate(tasks, start=1):
            accepted_conditions[int(task["condition_index"])].repeats.append(_run_native_repeat(**task))
            _log_repeat_progress(completed, len(tasks))
    else:
        with ProcessPoolExecutor(max_workers=jobs) as executor:
            futures = {executor.submit(_run_native_repeat, **task): task for task in tasks}
            for completed, future in enumerate(as_completed(futures), start=1):
                task = futures[future]
                accepted_conditions[int(task["condition_index"])].repeats.append(future.result())
                _log_repeat_progress(completed, len(tasks))
    for condition in accepted_conditions.values():
        condition.repeats.sort(key=lambda repeat: repeat.repeat_index)


def _run_native_repeat(
    *,
    condition_index: int,
    repeat_index: int,
    temperature: float,
    pressure: float,
    feed_composition: list[float],
    random_seed: int,
) -> RepeatResult:
    run_id = f"condition-{condition_index:03d}-repeat-{repeat_index:03d}"
    native_module_path = native_freshness.native_module_path(_core)
    stage_statuses: dict[str, Any] = {}
    try:
        mix = runtime.neutral_lle_synthetic_mixture()
        with runtime.suppress_native_stdout():
            route = dict(
                _core._native_equilibrium_selector_route_result(
                    mix._native,
                    {
                        "route": "neutral_lle",
                        "temperature": temperature,
                        "pressure": pressure,
                        "composition": feed_composition,
                        "composition_role": "feed",
                    },
                    260,
                    1.0e-6,
                    0.0,
                    "auto",
                    8,
                    1.0e-8,
                    1.0e-3,
                    1.0e-6,
                    1.0e-6,
                    {},
                    linear_solver="auto",
                    option_profile="held_refinement",
                    print_level=0,
                    acceptable_tolerance=1.0e-7,
                    constraint_violation_tolerance=1.0e-7,
                    dual_infeasibility_tolerance=1.0e-8,
                    complementarity_tolerance=1.0e-8,
                )
            )
    except Exception as exc:
        return RepeatResult(
            condition_index=condition_index,
            repeat_index=repeat_index,
            accepted=False,
            temperature=temperature,
            pressure=pressure,
            feed_composition=feed_composition,
            random_seed=random_seed,
            native_module_path=native_module_path,
            stage_statuses=stage_statuses,
            rejection_reason=f"{type(exc).__name__}: {exc}",
            run_id=run_id,
            process_id=os.getpid(),
        )

    discovery: dict[str, Any] = {}
    postsolve = dict(route.get("postsolve") or {})
    seed_attempts = list(route.get("seed_attempts") or ())
    first_seed_attempt = dict(seed_attempts[0]) if seed_attempts else {}
    stage_statuses = {
        "continuous_tpd_status": postsolve.get("continuous_tpd_status", discovery.get("continuous_tpd_status")),
        "held_stage_ii_status": postsolve.get("held_stage_ii_status", discovery.get("held_stage_ii_status")),
        "held_stage_iii_status": postsolve.get("held_stage_iii_status"),
    }
    repeat = RepeatResult(
        condition_index=condition_index,
        repeat_index=repeat_index,
        accepted=True,
        temperature=temperature,
        pressure=pressure,
        feed_composition=feed_composition,
        random_seed=random_seed,
        native_module_path=native_module_path,
        stage_statuses=stage_statuses,
        pressure_transformed_objective=float(first_seed_attempt.get("objective", route.get("objective", 0.0))),
        phase_count=len(route.get("phase_roles") or postsolve.get("phase_roles") or []),
        selected_phase_roles=[str(item) for item in route.get("phase_roles", [])],
        continuous_tpd_status=str(stage_statuses["continuous_tpd_status"]),
        held_stage_ii_status=str(stage_statuses["held_stage_ii_status"]),
        held_stage_ii_dual_loop_status=str(
            postsolve.get("held_stage_ii_dual_loop_status", discovery.get("held_stage_ii_dual_loop_status", ""))
        ),
        held_stage_ii_bound_gap=float(
            postsolve.get("held_stage_ii_bound_gap", discovery.get("held_stage_ii_bound_gap", float("inf")))
        ),
        held_stage_ii_bound_tolerance=float(
            postsolve.get(
                "held_stage_ii_bound_tolerance",
                discovery.get("held_stage_ii_bound_tolerance", 0.0),
            )
        ),
        held_stage_iii_status=str(stage_statuses["held_stage_iii_status"]),
        held_stage_iii_consumed_stage_ii_replay_metadata=bool(
            postsolve.get("held_stage_iii_consumed_stage_ii_replay_metadata")
        ),
        solver_status=str(route.get("solver_status", "")),
        application_status=str(route.get("application_status", "")),
        material_balance_norm=float(postsolve.get("material_balance_norm", first_seed_attempt.get("material_balance_norm", float("inf")))),
        pressure_consistency_norm=float(
            postsolve.get("pressure_consistency_norm", first_seed_attempt.get("pressure_consistency_norm", float("inf")))
        ),
        ln_fugacity_consistency_norm=float(
            postsolve.get(
                "ln_fugacity_consistency_norm",
                first_seed_attempt.get("phase_equilibrium_norm", float("inf")),
            )
        ),
        phase_distance=float(postsolve.get("phase_distance", first_seed_attempt.get("phase_distance", 0.0))),
        selected_candidate_count=int(postsolve.get("selected_candidate_count", discovery.get("selected_candidate_count", 0))),
        run_id=run_id,
        process_id=os.getpid(),
        native_start_policy="deterministic_multistart",
        stage_i_start_count=int(postsolve.get("held_stage_i_start_count", discovery.get("held_stage_i_start_count", 0))),
        candidate_start_sources=[
            str(item)
            for item in postsolve.get("tpd_candidate_sources", discovery.get("tpd_candidate_sources", []))
        ],
        stage_ii_stopping_reason=str(
            postsolve.get("held_stage_ii_stopping_reason", discovery.get("held_stage_ii_stopping_reason", ""))
        ),
        hidden_state_carryover_allowed=False,
    )
    blockers = _accepted_repeat_blockers(repeat, DEFAULT_THRESHOLDS)
    if blockers:
        repeat.accepted = False
        repeat.rejection_reason = blockers[0]
    return repeat


def _accepted_repeat_blockers(repeat: RepeatResult, thresholds: ReliabilityThresholds) -> list[str]:
    blockers: list[str] = []
    if repeat.continuous_tpd_status != "converged":
        blockers.append("continuous_tpd_status_mismatch")
    if repeat.held_stage_ii_status != "dual_loop_verified":
        blockers.append("held_stage_ii_status_mismatch")
    if repeat.held_stage_ii_dual_loop_status != "verified":
        blockers.append("held_stage_ii_dual_loop_status_mismatch")
    if repeat.held_stage_ii_bound_gap > repeat.held_stage_ii_bound_tolerance:
        blockers.append("held_stage_ii_bound_gap_above_tolerance")
    if repeat.held_stage_iii_status != "ipopt_refinement_completed_current_route":
        blockers.append("held_stage_iii_status_mismatch")
    if repeat.held_stage_iii_consumed_stage_ii_replay_metadata is not True:
        blockers.append("held_stage_iii_missing_stage_ii_replay_metadata")
    if repeat.solver_status != "success":
        blockers.append("solver_status_mismatch")
    if repeat.application_status != "solve_succeeded":
        blockers.append("application_status_mismatch")
    if repeat.material_balance_norm > thresholds.material_balance_norm:
        blockers.append("material_balance_norm_above_tolerance")
    if repeat.pressure_consistency_norm > thresholds.pressure_consistency_norm:
        blockers.append("pressure_consistency_norm_above_tolerance")
    if repeat.ln_fugacity_consistency_norm > thresholds.ln_fugacity_consistency_norm:
        blockers.append("ln_fugacity_consistency_norm_above_tolerance")
    if repeat.phase_distance < thresholds.phase_distance_min:
        blockers.append("phase_distance_below_minimum")
    if repeat.selected_candidate_count != 2:
        blockers.append("selected_candidate_count_mismatch")
    if (
        repeat.native_start_policy not in {"deterministic_multistart", "seeded_multistart"}
        or repeat.stage_i_start_count <= 0
        or not repeat.candidate_start_sources
    ):
        blockers.append("missing_start_policy_receipt")
    if repeat.stage_ii_stopping_reason != "bound_gap_closed":
        blockers.append("stage_ii_stopping_reason_mismatch")
    if repeat.hidden_state_carryover_allowed is not False:
        blockers.append("hidden_state_carryover_allowed")
    return blockers


def _first_failure_reproduction(repeat: RepeatResult) -> dict[str, Any]:
    return {
        "condition_index": repeat.condition_index,
        "repeat_index": repeat.repeat_index,
        "temperature": repeat.temperature,
        "pressure": repeat.pressure,
        "feed_composition": repeat.feed_composition,
        "random_seed": repeat.random_seed,
        "native_module_path": repeat.native_module_path,
        "stage_statuses": repeat.stage_statuses,
        "rejection_reason": repeat.rejection_reason,
    }


def _write_outputs(
    *,
    output_dir: Path,
    summary: dict[str, Any],
    conditions: list[ConditionResult],
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "held_lle_reliability_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    condition_rows = [_condition_row(condition) for condition in conditions]
    repeat_rows = repeat_rows_for_output(conditions)
    _write_csv(output_dir / "held_lle_reliability_conditions.csv", condition_rows)
    _write_csv(output_dir / "held_lle_reliability_repeats.csv", repeat_rows)


def _condition_row(condition: ConditionResult) -> dict[str, Any]:
    return {
        "condition_index": condition.condition_index,
        "accepted": condition.accepted,
        "temperature": condition.temperature,
        "pressure": condition.pressure,
        "feed_composition": json.dumps(condition.feed_composition),
        "repeat_count": len(condition.repeats),
        "rejection_reason": condition.rejection_reason,
    }


def _repeat_row(repeat: RepeatResult) -> dict[str, Any]:
    row = asdict(repeat)
    row["feed_composition"] = json.dumps(row["feed_composition"])
    row["stage_statuses"] = json.dumps(row["stage_statuses"], sort_keys=True)
    row["selected_phase_roles"] = json.dumps(row["selected_phase_roles"])
    row["candidate_start_sources"] = json.dumps(row["candidate_start_sources"])
    return row


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def _print_human(summary: dict[str, Any]) -> None:
    status = "complete" if summary["complete"] else "incomplete"
    print(f"HELD neutral LLE reliability campaign: {status}")
    print(f"  accepted_conditions: {summary['accepted_conditions']}")
    print(f"  attempted_repeats: {summary['attempted_repeats']}")
    print(f"  failed_repeats: {summary['failed_repeats']}")
    for blocker in summary["blockers"]:
        print(f"  blocker: {blocker}")


def _log_progress(message: str) -> None:
    print(f"[held-reliability] {message}", file=sys.stderr, flush=True)


def _log_repeat_progress(completed: int, total: int) -> None:
    stride = max(1, min(250, total // 20 if total >= 20 else 1))
    if completed == total or completed % stride == 0:
        _log_progress(f"completed_repeats_after_prefilter={completed}/{total}")


def _dedupe(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        result.append(value)
    return result


if __name__ == "__main__":
    raise SystemExit(main())
