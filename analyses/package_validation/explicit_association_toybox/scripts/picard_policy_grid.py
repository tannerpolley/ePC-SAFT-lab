from __future__ import annotations

import argparse
import statistics
import sys
from collections.abc import Callable, Iterable, Mapping
from pathlib import Path
from typing import TypeVar

import numpy as np

T = TypeVar("T")

if __package__ in {None, ""}:
    REPO_ROOT = Path(__file__).resolve().parents[4]
    if str(REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))
    from analyses.package_validation.explicit_association_toybox.scripts.association_case_matrix import (
        AssociationEvidenceCase,
        association_evidence_cases,
    )
    from analyses.package_validation.explicit_association_toybox.scripts.association_models import (
        association_helmholtz,
        mass_action_residual,
    )
    from analyses.package_validation.explicit_association_toybox.scripts.closure_models import (
        PICARD_POLICY_GRID,
        PicardPolicy,
        evaluate_picard_policy,
    )
    from analyses.package_validation.explicit_association_toybox.scripts.exact_baseline import (
        solve_exact_site_fractions,
    )
    from analyses.package_validation.explicit_association_toybox.scripts.propagation_evidence import (
        relative_error,
        timed_closure,
        write_rows_csv,
    )
else:
    from .association_case_matrix import AssociationEvidenceCase, association_evidence_cases
    from .association_models import association_helmholtz, mass_action_residual
    from .closure_models import PICARD_POLICY_GRID, PicardPolicy, evaluate_picard_policy
    from .exact_baseline import solve_exact_site_fractions
    from .propagation_evidence import relative_error, timed_closure, write_rows_csv

ANALYSIS_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ANALYSIS_ROOT / "figures" / "picard_policy_grid" / "output" / "picard_policy_grid.csv"
DEFAULT_HANDOFF = (
    ANALYSIS_ROOT / "figures" / "picard_policy_grid" / "output" / "picard_policy_cppad_handoff_matrix.csv"
)
DEFAULT_CASE_IDS = (
    "pure_one_site_self",
    "pure_2b_self",
    "pure_3b_labeled",
    "pure_4c_labeled",
    "water_like_3b_topology",
    "water_like_4c_topology",
    "cross_associating_binary",
    "asymmetric_donor_acceptor_binary",
    "mixed_2b_3b_binary",
    "mixed_2b_4c_binary",
    "mixed_4c_4c_binary",
)
TOTAL_ARES_CONTEXT = 0.2


def run_picard_policy_grid(
    *,
    repeat_count: int = 3,
    policies: Iterable[PicardPolicy] = PICARD_POLICY_GRID,
    cases: Iterable[AssociationEvidenceCase] | None = None,
) -> list[dict[str, object]]:
    if repeat_count <= 0:
        raise ValueError("repeat_count must be positive.")
    selected_cases = _selected_cases(cases)
    rows = [
        _policy_case_row(case, policy, repeat_count=repeat_count)
        for case in selected_cases
        for policy in policies
        if case.system is not None
    ]
    _apply_pareto_labels(rows)
    return rows


def generate_picard_policy_grid(
    output_path: Path = DEFAULT_OUTPUT,
    *,
    handoff_path: Path = DEFAULT_HANDOFF,
    repeat_count: int = 3,
) -> Path:
    rows = run_picard_policy_grid(repeat_count=repeat_count)
    write_rows_csv(rows, output_path)
    write_rows_csv(_handoff_rows(rows), handoff_path)
    return output_path


def _selected_cases(cases: Iterable[AssociationEvidenceCase] | None) -> tuple[AssociationEvidenceCase, ...]:
    available = tuple(cases if cases is not None else association_evidence_cases())
    by_id = {case.case_id: case for case in available}
    return tuple(by_id[case_id] for case_id in DEFAULT_CASE_IDS if case_id in by_id)


def _policy_case_row(case: AssociationEvidenceCase, policy: PicardPolicy, *, repeat_count: int) -> dict[str, object]:
    if case.system is None:
        raise ValueError("Picard policy grid requires associating cases.")
    density = float(case.density_grid[len(case.density_grid) // 2])
    strength = float(case.strength_scale)
    delta = case.scaled_delta(strength)
    x_assoc = case.system.x_assoc(case.composition)
    exact, exact_timings = _timed_repeat(
        lambda: solve_exact_site_fractions(density=density, x_assoc=x_assoc, delta=delta),
        repeat_count=repeat_count,
    )
    closure, closure_timings = _timed_repeat(
        lambda: evaluate_picard_policy(
            policy,
            system=case.system,
            density=density,
            composition=case.composition,
            delta=delta,
        ),
        repeat_count=repeat_count,
    )
    exact_a = association_helmholtz(exact.xa, case.composition, case.system.site_component_index)
    policy_a = association_helmholtz(closure.xa, case.composition, case.system.site_component_index)
    pressure_exact = _pressure_proxy(case, density=density, strength=strength, exact=True, policy=policy)
    pressure_policy = _pressure_proxy(case, density=density, strength=strength, exact=False, policy=policy)
    density_derivative_error = _derivative_error(case, policy, variable="density", density=density, strength=strength)
    strength_derivative_error = _derivative_error(case, policy, variable="strength", density=density, strength=strength)
    density_hessian_error = _hessian_error(case, policy, variable="density", density=density, strength=strength)
    strength_hessian_error = _hessian_error(case, policy, variable="strength", density=density, strength=strength)
    total_exact = TOTAL_ARES_CONTEXT + exact_a
    total_policy = TOTAL_ARES_CONTEXT + policy_a
    residual = mass_action_residual(closure.xa, density=density, x_assoc=x_assoc, delta=delta)
    exact_median = statistics.median(exact_timings)
    policy_median = statistics.median(closure_timings)
    active_pairs = int(np.count_nonzero(delta))
    return {
        "case_id": case.case_id,
        "topology_id": case.topology_id,
        "component_family": case.component_family,
        "mixture_family": case.mixture_family,
        "site_count": case.site_count,
        "component_count": case.component_count,
        "density": density,
        "strength_scale": strength,
        "composition": case.composition_text(),
        "strength_matrix": case.strength_matrix_text(),
        "binary_parameter_proxy": _binary_parameter_proxy(case),
        "step_count": policy.step_count,
        "damping": policy.damping,
        "policy_name": policy.closure_name,
        "exact_iteration_count": exact.iteration_count,
        "site_fraction_max_abs_error": float(np.max(np.abs(closure.xa - exact.xa))),
        "mass_action_residual_inf": float(np.linalg.norm(residual, ord=np.inf)),
        "association_helmholtz_exact": exact_a,
        "association_helmholtz_policy": policy_a,
        "association_helmholtz_absolute_error": abs(policy_a - exact_a),
        "association_helmholtz_relative_error": relative_error(policy_a, exact_a),
        "total_ares_proxy_exact": total_exact,
        "total_ares_proxy_policy": total_policy,
        "total_ares_proxy_relative_error": relative_error(total_policy, total_exact),
        "pressure_proxy_exact": pressure_exact,
        "pressure_proxy_policy": pressure_policy,
        "pressure_proxy_relative_error": relative_error(pressure_policy, pressure_exact),
        "density_derivative_relative_error": density_derivative_error,
        "strength_derivative_relative_error": strength_derivative_error,
        "derivative_max_relative_error": max(density_derivative_error, strength_derivative_error),
        "density_hessian_relative_error": density_hessian_error,
        "strength_hessian_relative_error": strength_hessian_error,
        "hessian_max_relative_error": max(density_hessian_error, strength_hessian_error),
        "exact_implicit_elapsed_median_seconds": exact_median,
        "policy_elapsed_median_seconds": policy_median,
        "speedup_vs_exact_implicit": exact_median / policy_median if policy_median > 0.0 else np.nan,
        "evaluation_count_proxy": policy.step_count * max(active_pairs, case.site_count),
        "graph_depth_proxy": policy.step_count,
        "pareto_band": "pending",
        "candidate_policy_label": "pending",
        "cppad_stress_relevance": _cppad_stress_relevance(case),
        "diagnostic_scope": "python_toybox_picard_policy_grid",
    }


def _timed_repeat(function: Callable[[], T], *, repeat_count: int) -> tuple[T, list[float]]:
    result: T | None = None
    timings: list[float] = []
    for _ in range(repeat_count):
        result, elapsed = timed_closure(function)
        timings.append(elapsed)
    if result is None:
        raise RuntimeError("timed repeat produced no result.")
    return result, timings


def _association_value(
    case: AssociationEvidenceCase,
    policy: PicardPolicy,
    *,
    density: float,
    strength: float,
    exact: bool,
) -> float:
    if case.system is None:
        return 0.0
    delta = case.scaled_delta(max(strength, 1.0e-12))
    if exact:
        xa = solve_exact_site_fractions(
            density=density,
            x_assoc=case.system.x_assoc(case.composition),
            delta=delta,
        ).xa
    else:
        xa = evaluate_picard_policy(
            policy,
            system=case.system,
            density=density,
            composition=case.composition,
            delta=delta,
        ).xa
    return association_helmholtz(xa, case.composition, case.system.site_component_index)


def _pressure_proxy(case: AssociationEvidenceCase, *, density: float, strength: float, exact: bool, policy: PicardPolicy) -> float:
    ares = _association_value(case, policy, density=density, strength=strength, exact=exact)
    slope = _centered_slope(
        lambda rho: _association_value(case, policy, density=rho, strength=strength, exact=exact),
        base_value=density,
        step_size=_density_step(density),
    )
    return float(density * (1.0 + ares) + density * density * slope)


def _derivative_error(
    case: AssociationEvidenceCase,
    policy: PicardPolicy,
    *,
    variable: str,
    density: float,
    strength: float,
) -> float:
    if variable == "density":
        exact = _centered_slope(
            lambda rho: _association_value(case, policy, density=rho, strength=strength, exact=True),
            base_value=density,
            step_size=_density_step(density),
        )
        policy_value = _centered_slope(
            lambda rho: _association_value(case, policy, density=rho, strength=strength, exact=False),
            base_value=density,
            step_size=_density_step(density),
        )
        return relative_error(policy_value, exact)
    if variable == "strength":
        exact = _centered_slope(
            lambda scale: _association_value(case, policy, density=density, strength=scale, exact=True),
            base_value=strength,
            step_size=_strength_step(strength),
        )
        policy_value = _centered_slope(
            lambda scale: _association_value(case, policy, density=density, strength=scale, exact=False),
            base_value=strength,
            step_size=_strength_step(strength),
        )
        return relative_error(policy_value, exact)
    raise ValueError(f"Unknown derivative variable: {variable}")


def _hessian_error(
    case: AssociationEvidenceCase,
    policy: PicardPolicy,
    *,
    variable: str,
    density: float,
    strength: float,
) -> float:
    if variable == "density":
        exact = _second_derivative(
            lambda rho: _association_value(case, policy, density=rho, strength=strength, exact=True),
            base_value=density,
            step_size=_density_step(density),
        )
        policy_value = _second_derivative(
            lambda rho: _association_value(case, policy, density=rho, strength=strength, exact=False),
            base_value=density,
            step_size=_density_step(density),
        )
        return relative_error(policy_value, exact)
    if variable == "strength":
        exact = _second_derivative(
            lambda scale: _association_value(case, policy, density=density, strength=scale, exact=True),
            base_value=strength,
            step_size=_strength_step(strength),
        )
        policy_value = _second_derivative(
            lambda scale: _association_value(case, policy, density=density, strength=scale, exact=False),
            base_value=strength,
            step_size=_strength_step(strength),
        )
        return relative_error(policy_value, exact)
    raise ValueError(f"Unknown hessian variable: {variable}")


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


def _apply_pareto_labels(rows: list[dict[str, object]]) -> None:
    for case_id in sorted({str(row["case_id"]) for row in rows}):
        case_rows = [row for row in rows if row["case_id"] == case_id]
        frontier = _pareto_frontier(case_rows)
        for row in case_rows:
            accuracy = max(
                float(row["association_helmholtz_relative_error"]),
                float(row["pressure_proxy_relative_error"]),
                float(row["derivative_max_relative_error"]),
                float(row["hessian_max_relative_error"]),
            )
            speedup = float(row["speedup_vs_exact_implicit"])
            if row in frontier and int(row["step_count"]) <= 5 and accuracy <= 1.0e-2:
                label = "fast"
            elif row in frontier and accuracy <= 1.0e-4:
                label = "high_accuracy"
            elif row in frontier and accuracy <= 1.0e-3:
                label = "balanced"
            elif accuracy <= 1.0e-2 and speedup > 1.0:
                label = "diagnostic_candidate"
            else:
                label = "diagnostic_only"
            row["candidate_policy_label"] = label
            row["pareto_band"] = "pareto_frontier" if row in frontier else "dominated"


def _pareto_frontier(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    frontier: list[dict[str, object]] = []
    for row in rows:
        dominated = False
        row_metrics = _pareto_metrics(row)
        for other in rows:
            if other is row:
                continue
            other_metrics = _pareto_metrics(other)
            if all(other_value <= row_value for other_value, row_value in zip(other_metrics, row_metrics, strict=True)) and any(
                other_value < row_value for other_value, row_value in zip(other_metrics, row_metrics, strict=True)
            ):
                dominated = True
                break
        if not dominated:
            frontier.append(row)
    return frontier


def _pareto_metrics(row: Mapping[str, object]) -> tuple[float, float, float, float, float]:
    return (
        float(row["association_helmholtz_relative_error"]),
        float(row["pressure_proxy_relative_error"]),
        float(row["derivative_max_relative_error"]),
        float(row["hessian_max_relative_error"]),
        float(row["policy_elapsed_median_seconds"]),
    )


def _handoff_rows(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    handoff: list[dict[str, object]] = []
    for row in rows:
        if row["candidate_policy_label"] not in {"fast", "balanced", "high_accuracy", "diagnostic_candidate"}:
            continue
        handoff.append(
            {
                "case_id": row["case_id"],
                "topology_id": row["topology_id"],
                "policy_name": row["policy_name"],
                "step_count": row["step_count"],
                "damping": row["damping"],
                "variables": "density;association_strength;composition_when_binary",
                "expected_derivative_orders": "0;1;2",
                "suggested_relative_tolerance": _suggested_tolerance(row),
                "failure_modes": _failure_modes(row),
                "cppad_stress_relevance": row["cppad_stress_relevance"],
                "pareto_band": row["pareto_band"],
                "candidate_policy_label": row["candidate_policy_label"],
            }
        )
    if not handoff:
        raise ValueError("Picard policy grid produced no CppAD handoff candidates.")
    return handoff


def _suggested_tolerance(row: Mapping[str, object]) -> str:
    error = max(
        float(row["association_helmholtz_relative_error"]),
        float(row["pressure_proxy_relative_error"]),
        float(row["derivative_max_relative_error"]),
        float(row["hessian_max_relative_error"]),
    )
    return f"{max(1.0e-8, min(1.0e-2, 10.0 * error)):.3e}"


def _failure_modes(row: Mapping[str, object]) -> str:
    modes: list[str] = []
    if float(row["mass_action_residual_inf"]) > 1.0e-4:
        modes.append("mass_action_residual")
    if float(row["hessian_max_relative_error"]) > 1.0e-3:
        modes.append("curvature_error")
    if float(row["derivative_max_relative_error"]) > 1.0e-3:
        modes.append("jacobian_error")
    if float(row["pressure_proxy_relative_error"]) > 1.0e-3:
        modes.append("pressure_density_proxy_error")
    return ";".join(modes) if modes else "none_observed"


def _binary_parameter_proxy(case: AssociationEvidenceCase) -> str:
    if case.component_count == 1:
        return "not_binary"
    return "delta_matrix_strength_proxy_for_k_hb_l_ij"


def _cppad_stress_relevance(case: AssociationEvidenceCase) -> str:
    if case.component_count == 2:
        return "binary_composition_and_parameter_jacobian_hessian"
    return "pure_density_and_parameter_jacobian_hessian"


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate Picard step/damping policy-grid evidence.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--handoff", type=Path, default=DEFAULT_HANDOFF)
    parser.add_argument("--repeat-count", type=int, default=3)
    args = parser.parse_args()
    print(generate_picard_policy_grid(output_path=args.output, handoff_path=args.handoff, repeat_count=args.repeat_count))


if __name__ == "__main__":
    main()
