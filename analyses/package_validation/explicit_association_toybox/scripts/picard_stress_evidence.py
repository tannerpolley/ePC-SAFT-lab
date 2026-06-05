from __future__ import annotations

import argparse
import csv
import statistics
from collections.abc import Callable, Iterable, Mapping, Sequence
from pathlib import Path
import sys

import numpy as np

if __package__ in {None, ""}:
    REPO_ROOT = Path(__file__).resolve().parents[4]
    if str(REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))
    from analyses.package_validation.explicit_association_toybox.scripts.association_models import (
        association_helmholtz,
        mass_action_residual,
    )
    from analyses.package_validation.explicit_association_toybox.scripts.closure_models import (
        EXACT_MASS_ACTION_BASELINE,
        PICARD_POLICY_GRID,
        PicardPolicy,
        evaluate_picard_policy,
    )
    from analyses.package_validation.explicit_association_toybox.scripts.exact_baseline import solve_exact_site_fractions
    from analyses.package_validation.explicit_association_toybox.scripts.metrics import timed_closure
    from analyses.package_validation.explicit_association_toybox.scripts.picard_stress_cases import (
        PicardStressCase,
        materialize_picard_stress_cases,
    )
    from analyses.package_validation.explicit_association_toybox.scripts.propagation_evidence import relative_error
else:
    from .association_models import association_helmholtz, mass_action_residual
    from .closure_models import EXACT_MASS_ACTION_BASELINE, PICARD_POLICY_GRID, PicardPolicy, evaluate_picard_policy
    from .exact_baseline import solve_exact_site_fractions
    from .metrics import timed_closure
    from .picard_stress_cases import PicardStressCase, materialize_picard_stress_cases
    from .propagation_evidence import relative_error

ANALYSIS_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ANALYSIS_ROOT / "figures" / "picard_stress_evidence" / "output" / "picard_stress_evidence.csv"
DEFAULT_MEMO = ANALYSIS_ROOT / "docs" / "picard_stress_rescue_or_retire_decision.md"
TOTAL_ARES_CONTEXT = 0.2

PICARD_STRESS_COLUMNS = (
    "row_kind",
    "stress_decision",
    "case_id",
    "source_case_id",
    "case_family",
    "topology_id",
    "axis_id",
    "decision_role",
    "simulation_scope",
    "closure_name",
    "step_count",
    "damping",
    "density",
    "temperature",
    "strength_scale",
    "composition",
    "site_count",
    "component_count",
    "exact_iteration_count",
    "baseline_status",
    "evaluation_status",
    "site_fraction_max_abs_error",
    "mass_action_residual_inf",
    "association_helmholtz_exact",
    "association_helmholtz_picard",
    "association_helmholtz_relative_error",
    "total_ares_proxy_exact",
    "total_ares_proxy_picard",
    "total_ares_proxy_relative_error",
    "pressure_proxy_exact",
    "pressure_proxy_picard",
    "pressure_proxy_relative_error",
    "density_derivative_relative_error",
    "strength_derivative_relative_error",
    "derivative_max_relative_error",
    "density_hessian_relative_error",
    "strength_hessian_relative_error",
    "hessian_max_relative_error",
    "objective_exact",
    "objective_picard",
    "objective_relative_error",
    "gradient_direction_agreement",
    "hessian_conditioning_indicator",
    "closure_elapsed_median_seconds_exact",
    "closure_elapsed_median_seconds_picard",
    "simulation_elapsed_median_seconds_exact",
    "simulation_elapsed_median_seconds_picard",
    "simulation_speedup_vs_exact",
)


def run_picard_stress_evidence(
    *,
    repeat_count: int = 3,
    max_cases: int | None = None,
    max_policies: int | None = None,
    policies: Iterable[PicardPolicy] = PICARD_POLICY_GRID,
) -> list[dict[str, object]]:
    if repeat_count <= 0:
        raise ValueError("repeat_count must be positive.")
    selected_cases = materialize_picard_stress_cases(max_cases=max_cases)
    selected_policies = tuple(policies)
    if max_policies is not None:
        selected_policies = selected_policies[:max_policies]
    rows: list[dict[str, object]] = []
    for case in selected_cases:
        exact_bundle = _exact_bundle(case, repeat_count=repeat_count)
        rows.append(_exact_row(case, exact_bundle))
        for policy in selected_policies:
            rows.append(_picard_row(case, policy, exact_bundle, repeat_count=repeat_count))
    decision = _stress_decision(rows)
    for row in rows:
        row["stress_decision"] = decision
    return rows


def generate_picard_stress_report(
    output_path: Path = DEFAULT_OUTPUT,
    memo_path: Path = DEFAULT_MEMO,
    *,
    repeat_count: int = 3,
    max_cases: int | None = None,
    max_policies: int | None = None,
) -> Path:
    rows = run_picard_stress_evidence(repeat_count=repeat_count, max_cases=max_cases, max_policies=max_policies)
    _write_rows(rows, output_path)
    _write_memo(rows, memo_path)
    return output_path


def _exact_bundle(case: PicardStressCase, *, repeat_count: int) -> dict[str, object]:
    if case.source_case.system is None:
        raise ValueError(f"{case.source_case_id} has no association system.")
    delta = case.scaled_delta()
    x_assoc = case.source_case.system.x_assoc(case.composition)
    exact, exact_timings = _timed_repeat(
        lambda: solve_exact_site_fractions(density=case.density, x_assoc=x_assoc, delta=delta),
        repeat_count=repeat_count,
    )
    exact_a = association_helmholtz(exact.xa, case.composition, case.source_case.system.site_component_index)
    pressure = _pressure_proxy(case, exact=True, policy=None)
    objective = _local_objective(total_ares=TOTAL_ARES_CONTEXT + exact_a, pressure_proxy=pressure)
    return {
        "exact": exact,
        "timings": exact_timings,
        "association_helmholtz": exact_a,
        "total_ares_proxy": TOTAL_ARES_CONTEXT + exact_a,
        "pressure_proxy": pressure,
        "objective": objective,
    }


def _picard_row(
    case: PicardStressCase,
    policy: PicardPolicy,
    exact_bundle: Mapping[str, object],
    *,
    repeat_count: int,
) -> dict[str, object]:
    exact = exact_bundle["exact"]
    delta = case.scaled_delta()
    closure, closure_timings = _timed_repeat(
        lambda: evaluate_picard_policy(
            policy,
            system=case.source_case.system,
            density=case.density,
            composition=case.composition,
            delta=delta,
        ),
        repeat_count=repeat_count,
    )
    policy_a = association_helmholtz(closure.xa, case.composition, case.source_case.system.site_component_index)
    total_policy = TOTAL_ARES_CONTEXT + policy_a
    pressure_policy = _pressure_proxy(case, exact=False, policy=policy)
    objective_policy = _local_objective(total_ares=total_policy, pressure_proxy=pressure_policy)
    density_derivative_error = _derivative_error(case, policy, variable="density")
    strength_derivative_error = _derivative_error(case, policy, variable="strength")
    density_hessian_error = _hessian_error(case, policy, variable="density")
    strength_hessian_error = _hessian_error(case, policy, variable="strength")
    exact_timings = [float(value) for value in exact_bundle["timings"]]
    exact_median = statistics.median(exact_timings)
    policy_median = statistics.median(closure_timings)
    exact_simulation = exact_median + _property_proxy_elapsed(case, exact=True, policy=None)
    policy_simulation = policy_median + _property_proxy_elapsed(case, exact=False, policy=policy)
    residual = mass_action_residual(
        closure.xa,
        density=case.density,
        x_assoc=case.source_case.system.x_assoc(case.composition),
        delta=delta,
    )
    objective_error = relative_error(objective_policy, float(exact_bundle["objective"]))
    max_hessian = max(density_hessian_error, strength_hessian_error)
    return _base_row(case) | {
        "row_kind": "picard_policy",
        "stress_decision": "pending",
        "closure_name": policy.closure_name,
        "step_count": policy.step_count,
        "damping": policy.damping,
        "exact_iteration_count": exact.iteration_count,
        "baseline_status": "exact_implicit_mass_action_solved",
        "evaluation_status": _evaluation_status(objective_error, density_derivative_error, max_hessian),
        "site_fraction_max_abs_error": float(np.max(np.abs(closure.xa - exact.xa))),
        "mass_action_residual_inf": float(np.linalg.norm(residual, ord=np.inf)),
        "association_helmholtz_exact": exact_bundle["association_helmholtz"],
        "association_helmholtz_picard": policy_a,
        "association_helmholtz_relative_error": relative_error(policy_a, float(exact_bundle["association_helmholtz"])),
        "total_ares_proxy_exact": exact_bundle["total_ares_proxy"],
        "total_ares_proxy_picard": total_policy,
        "total_ares_proxy_relative_error": relative_error(total_policy, float(exact_bundle["total_ares_proxy"])),
        "pressure_proxy_exact": exact_bundle["pressure_proxy"],
        "pressure_proxy_picard": pressure_policy,
        "pressure_proxy_relative_error": relative_error(pressure_policy, float(exact_bundle["pressure_proxy"])),
        "density_derivative_relative_error": density_derivative_error,
        "strength_derivative_relative_error": strength_derivative_error,
        "derivative_max_relative_error": max(density_derivative_error, strength_derivative_error),
        "density_hessian_relative_error": density_hessian_error,
        "strength_hessian_relative_error": strength_hessian_error,
        "hessian_max_relative_error": max_hessian,
        "objective_exact": exact_bundle["objective"],
        "objective_picard": objective_policy,
        "objective_relative_error": objective_error,
        "gradient_direction_agreement": "aligned" if density_derivative_error <= 0.25 else "changed",
        "hessian_conditioning_indicator": 1.0 + max_hessian,
        "closure_elapsed_median_seconds_exact": exact_median,
        "closure_elapsed_median_seconds_picard": policy_median,
        "simulation_elapsed_median_seconds_exact": exact_simulation,
        "simulation_elapsed_median_seconds_picard": policy_simulation,
        "simulation_speedup_vs_exact": exact_simulation / policy_simulation if policy_simulation > 0.0 else np.nan,
    }


def _exact_row(case: PicardStressCase, exact_bundle: Mapping[str, object]) -> dict[str, object]:
    exact = exact_bundle["exact"]
    exact_median = statistics.median([float(value) for value in exact_bundle["timings"]])
    exact_simulation = exact_median + _property_proxy_elapsed(case, exact=True, policy=None)
    return _base_row(case) | {
        "row_kind": "exact_baseline",
        "stress_decision": "pending",
        "closure_name": EXACT_MASS_ACTION_BASELINE,
        "step_count": 0,
        "damping": 0.0,
        "exact_iteration_count": exact.iteration_count,
        "baseline_status": "exact_implicit_mass_action_solved",
        "evaluation_status": "exact_reference",
        "site_fraction_max_abs_error": 0.0,
        "mass_action_residual_inf": exact.residual_norm,
        "association_helmholtz_exact": exact_bundle["association_helmholtz"],
        "association_helmholtz_picard": exact_bundle["association_helmholtz"],
        "association_helmholtz_relative_error": 0.0,
        "total_ares_proxy_exact": exact_bundle["total_ares_proxy"],
        "total_ares_proxy_picard": exact_bundle["total_ares_proxy"],
        "total_ares_proxy_relative_error": 0.0,
        "pressure_proxy_exact": exact_bundle["pressure_proxy"],
        "pressure_proxy_picard": exact_bundle["pressure_proxy"],
        "pressure_proxy_relative_error": 0.0,
        "density_derivative_relative_error": 0.0,
        "strength_derivative_relative_error": 0.0,
        "derivative_max_relative_error": 0.0,
        "density_hessian_relative_error": 0.0,
        "strength_hessian_relative_error": 0.0,
        "hessian_max_relative_error": 0.0,
        "objective_exact": exact_bundle["objective"],
        "objective_picard": exact_bundle["objective"],
        "objective_relative_error": 0.0,
        "gradient_direction_agreement": "aligned",
        "hessian_conditioning_indicator": 1.0,
        "closure_elapsed_median_seconds_exact": exact_median,
        "closure_elapsed_median_seconds_picard": exact_median,
        "simulation_elapsed_median_seconds_exact": exact_simulation,
        "simulation_elapsed_median_seconds_picard": exact_simulation,
        "simulation_speedup_vs_exact": 1.0,
    }


def _base_row(case: PicardStressCase) -> dict[str, object]:
    return {
        "case_id": case.case_id,
        "source_case_id": case.source_case_id,
        "case_family": case.case_family,
        "topology_id": case.topology_id,
        "axis_id": case.axis_id,
        "decision_role": case.decision_role,
        "simulation_scope": case.simulation_scope,
        "density": case.density,
        "temperature": case.temperature,
        "strength_scale": case.strength_scale,
        "composition": case.composition_text,
        "site_count": case.source_case.site_count,
        "component_count": case.source_case.component_count,
    }


def _timed_repeat[T](function: Callable[[], T], *, repeat_count: int) -> tuple[T, list[float]]:
    result: T | None = None
    timings: list[float] = []
    for _ in range(repeat_count):
        result, elapsed = timed_closure(function)
        timings.append(elapsed)
    if result is None:
        raise RuntimeError("timed repeat produced no result.")
    return result, timings


def _association_value(case: PicardStressCase, *, exact: bool, policy: PicardPolicy | None, density: float, strength: float) -> float:
    delta = case.source_case.scaled_delta(max(strength, 1.0e-12))
    if exact:
        xa = solve_exact_site_fractions(
            density=density,
            x_assoc=case.source_case.system.x_assoc(case.composition),
            delta=delta,
        ).xa
    else:
        if policy is None:
            raise ValueError("Picard association value requires a policy.")
        xa = evaluate_picard_policy(
            policy,
            system=case.source_case.system,
            density=density,
            composition=case.composition,
            delta=delta,
        ).xa
    return association_helmholtz(xa, case.composition, case.source_case.system.site_component_index)


def _pressure_proxy(case: PicardStressCase, *, exact: bool, policy: PicardPolicy | None) -> float:
    ares = _association_value(case, exact=exact, policy=policy, density=case.density, strength=case.strength_scale)
    slope = _centered_slope(
        lambda rho: _association_value(case, exact=exact, policy=policy, density=rho, strength=case.strength_scale),
        base_value=case.density,
        step_size=_density_step(case.density),
    )
    return float(case.density * (1.0 + ares) + case.density * case.density * slope)


def _derivative_error(case: PicardStressCase, policy: PicardPolicy, *, variable: str) -> float:
    if variable == "density":
        exact = _centered_slope(
            lambda rho: _association_value(case, exact=True, policy=None, density=rho, strength=case.strength_scale),
            base_value=case.density,
            step_size=_density_step(case.density),
        )
        picard = _centered_slope(
            lambda rho: _association_value(case, exact=False, policy=policy, density=rho, strength=case.strength_scale),
            base_value=case.density,
            step_size=_density_step(case.density),
        )
        return relative_error(picard, exact)
    if variable == "strength":
        exact = _centered_slope(
            lambda strength: _association_value(case, exact=True, policy=None, density=case.density, strength=strength),
            base_value=case.strength_scale,
            step_size=_strength_step(case.strength_scale),
        )
        picard = _centered_slope(
            lambda strength: _association_value(case, exact=False, policy=policy, density=case.density, strength=strength),
            base_value=case.strength_scale,
            step_size=_strength_step(case.strength_scale),
        )
        return relative_error(picard, exact)
    raise ValueError(f"unknown derivative variable: {variable}")


def _hessian_error(case: PicardStressCase, policy: PicardPolicy, *, variable: str) -> float:
    if variable == "density":
        exact = _second_derivative(
            lambda rho: _association_value(case, exact=True, policy=None, density=rho, strength=case.strength_scale),
            base_value=case.density,
            step_size=_density_step(case.density),
        )
        picard = _second_derivative(
            lambda rho: _association_value(case, exact=False, policy=policy, density=rho, strength=case.strength_scale),
            base_value=case.density,
            step_size=_density_step(case.density),
        )
        return relative_error(picard, exact)
    if variable == "strength":
        exact = _second_derivative(
            lambda strength: _association_value(case, exact=True, policy=None, density=case.density, strength=strength),
            base_value=case.strength_scale,
            step_size=_strength_step(case.strength_scale),
        )
        picard = _second_derivative(
            lambda strength: _association_value(case, exact=False, policy=policy, density=case.density, strength=strength),
            base_value=case.strength_scale,
            step_size=_strength_step(case.strength_scale),
        )
        return relative_error(picard, exact)
    raise ValueError(f"unknown hessian variable: {variable}")


def _property_proxy_elapsed(case: PicardStressCase, *, exact: bool, policy: PicardPolicy | None) -> float:
    _, elapsed = timed_closure(lambda: _pressure_proxy(case, exact=exact, policy=policy))
    return elapsed


def _centered_slope(function: Callable[[float], float], *, base_value: float, step_size: float) -> float:
    return float((function(base_value + step_size) - function(base_value - step_size)) / (2.0 * step_size))


def _second_derivative(function: Callable[[float], float], *, base_value: float, step_size: float) -> float:
    high = function(base_value + step_size)
    mid = function(base_value)
    low = function(base_value - step_size)
    return float((high - 2.0 * mid + low) / (step_size * step_size))


def _density_step(density: float) -> float:
    return max(1.0e-5, abs(density) * 1.0e-4)


def _strength_step(strength: float) -> float:
    return max(1.0e-4, abs(strength) * 1.0e-4)


def _local_objective(*, total_ares: float, pressure_proxy: float) -> float:
    return float(total_ares + 0.01 * pressure_proxy)


def _evaluation_status(objective_error: float, derivative_error: float, hessian_error: float) -> str:
    worst = max(objective_error, derivative_error, hessian_error)
    if worst <= 1.0e-3:
        return "passes_stress_gate"
    if worst <= 1.0e-2:
        return "research_only_stress_gate"
    return "reject_for_provider_path"


def _stress_decision(rows: Sequence[Mapping[str, object]]) -> str:
    picard_rows = [row for row in rows if row["row_kind"] == "picard_policy"]
    if not picard_rows:
        return "retire_picard"
    worst_hessian = max(float(row["hessian_max_relative_error"]) for row in picard_rows)
    worst_derivative = max(float(row["derivative_max_relative_error"]) for row in picard_rows)
    worst_pressure = max(float(row["pressure_proxy_relative_error"]) for row in picard_rows)
    min_speedup = min(float(row["simulation_speedup_vs_exact"]) for row in picard_rows)
    if worst_hessian <= 1.0e-3 and worst_derivative <= 1.0e-3 and worst_pressure <= 1.0e-3 and min_speedup > 1.0:
        return "recommend_m3_provider_admission_issue"
    if worst_hessian <= 1.0e-1 and worst_derivative <= 1.0e-1 and min_speedup > 1.0:
        return "keep_m8_only"
    return "retire_picard"


def _write_rows(rows: Sequence[Mapping[str, object]], output_path: Path) -> Path:
    if not rows:
        raise ValueError("Picard stress evidence rows are required.")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(PICARD_STRESS_COLUMNS))
        writer.writeheader()
        writer.writerows(rows)
    return output_path


def _write_memo(rows: Sequence[Mapping[str, object]], memo_path: Path) -> None:
    memo_path.parent.mkdir(parents=True, exist_ok=True)
    decision = str(rows[0]["stress_decision"])
    picard_rows = [row for row in rows if row["row_kind"] == "picard_policy"]
    max_assoc = max(float(row["association_helmholtz_relative_error"]) for row in picard_rows)
    max_pressure = max(float(row["pressure_proxy_relative_error"]) for row in picard_rows)
    max_derivative = max(float(row["derivative_max_relative_error"]) for row in picard_rows)
    max_hessian = max(float(row["hessian_max_relative_error"]) for row in picard_rows)
    min_speedup = min(float(row["simulation_speedup_vs_exact"]) for row in picard_rows)
    lines = [
        "# Picard Stress Rescue Or Retire Decision",
        "",
        f"## Decision: `{decision}`",
        "",
        "This M8 stress lane compares the exact implicit association solve against the fixed Picard policy grid across the retained topology, density, temperature, strength, and composition matrix.",
        "",
        "| Metric | Retained stress result |",
        "| --- | ---: |",
        f"| Max association Helmholtz relative error | {max_assoc:.6g} |",
        f"| Max pressure proxy relative error | {max_pressure:.6g} |",
        f"| Max derivative relative error | {max_derivative:.6g} |",
        f"| Max Hessian relative error | {max_hessian:.6g} |",
        f"| Minimum simulation speedup vs exact implicit | {min_speedup:.6g} |",
        "",
        "The decision is analysis-only evidence for issue 161 disposition and does not change provider, equilibrium, regression, benchmark, or public API behavior.",
    ]
    memo_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate Picard stress evidence CSV and decision memo.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--memo", type=Path, default=DEFAULT_MEMO)
    parser.add_argument("--repeat-count", type=int, default=3)
    args = parser.parse_args()
    print(generate_picard_stress_report(args.output, args.memo, repeat_count=args.repeat_count))


if __name__ == "__main__":
    main()
