from __future__ import annotations

import argparse
import csv
import statistics
import sys
from collections.abc import Callable, Mapping, Sequence
from pathlib import Path
from typing import TypeVar

import numpy as np

if __package__ in {None, ""}:
    REPO_ROOT = Path(__file__).resolve().parents[4]
    if str(REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))
    from analyses.package_validation.explicit_association_toybox.scripts.closure_models import (
        EXACT_MASS_ACTION_BASELINE,
        PICARD_POLICY_GRID,
        PicardPolicy,
    )
    from analyses.package_validation.explicit_association_toybox.scripts.fixed_state_property_residuals import (
        DEFAULT_CASES,
        DEFAULT_SOURCE,
        load_provider_cases,
        load_public_saturation_rows,
    )
    from analyses.package_validation.explicit_association_toybox.scripts.picard_policy_grid import (
        run_picard_policy_grid,
    )
    from analyses.package_validation.explicit_association_toybox.scripts.propagation_evidence import (
        relative_error,
        write_rows_csv,
    )
    from analyses.package_validation.explicit_association_toybox.scripts.pure_saturation import (
        PureSaturationResult,
        solve_pure_saturation,
    )
    from analyses.package_validation.explicit_association_toybox.scripts.metrics import timed_closure
else:
    from .closure_models import EXACT_MASS_ACTION_BASELINE, PICARD_POLICY_GRID, PicardPolicy
    from .fixed_state_property_residuals import (
        DEFAULT_CASES,
        DEFAULT_SOURCE,
        load_provider_cases,
        load_public_saturation_rows,
    )
    from .metrics import timed_closure
    from .picard_policy_grid import run_picard_policy_grid
    from .propagation_evidence import relative_error, write_rows_csv
    from .pure_saturation import PureSaturationResult, solve_pure_saturation

ANALYSIS_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = (
    ANALYSIS_ROOT
    / "figures"
    / "final_picard_admission_report"
    / "output"
    / "final_picard_admission_report.csv"
)
DEFAULT_MEMO = ANALYSIS_ROOT / "docs" / "issue_161_picard_admission_decision.md"
DEFAULT_MAX_SOURCE_ROWS = 4

FINAL_REPORT_COLUMNS = (
    "case_id",
    "topology_id",
    "simulation_id",
    "simulation_type",
    "component_family",
    "mixture_family",
    "step_count",
    "damping",
    "policy_name",
    "exact_iteration_count",
    "solver_status_exact",
    "solver_status_picard",
    "density_root_status_exact",
    "density_root_status_picard",
    "association_helmholtz_relative_error",
    "total_ares_proxy_relative_error",
    "pressure_proxy_relative_error",
    "saturation_pressure_relative_error",
    "liquid_density_relative_error",
    "vapor_density_relative_error",
    "derivative_max_relative_error",
    "hessian_max_relative_error",
    "closure_elapsed_median_seconds_exact",
    "closure_elapsed_median_seconds_picard",
    "simulation_elapsed_median_seconds_exact",
    "simulation_elapsed_median_seconds_picard",
    "closure_speedup_vs_exact",
    "simulation_speedup_vs_exact",
    "pareto_band",
    "admission_band",
    "issue_161_recommendation",
    "reference_p_sat_Pa",
    "reference_rho_liq_mol_m3",
    "model_p_sat_exact_Pa",
    "model_p_sat_picard_Pa",
    "model_rho_vap_exact_mol_m3",
    "model_rho_vap_picard_mol_m3",
    "model_rho_liq_exact_mol_m3",
    "model_rho_liq_picard_mol_m3",
    "source_url",
    "parameter_source",
    "message",
)

T = TypeVar("T")


def build_final_picard_admission_rows(
    *,
    repeat_count: int = 3,
    max_source_rows: int | None = DEFAULT_MAX_SOURCE_ROWS,
) -> list[dict[str, object]]:
    if repeat_count <= 0:
        raise ValueError("repeat_count must be positive.")
    source_rows = _selected_source_rows(load_public_saturation_rows(DEFAULT_SOURCE), max_source_rows=max_source_rows)
    provider_cases = load_provider_cases(DEFAULT_CASES)
    grid_rows = run_picard_policy_grid(repeat_count=repeat_count)
    policy_summaries = _policy_metric_summaries(grid_rows)

    rows: list[dict[str, object]] = []
    for source_row in source_rows:
        component = str(source_row["component"]).lower()
        case = provider_cases.get(component)
        if case is None:
            continue
        simulation_id = _simulation_id(source_row)
        exact_attempt = _timed_repeat(
            lambda: solve_pure_saturation(
                case,
                temperature=float(source_row["T_K"]),
                closure_name=EXACT_MASS_ACTION_BASELINE,
                pressure_seed_Pa=float(source_row["p_sat_Pa"]),
                liquid_density_seed_mol_m3=float(source_row["rho_sat_liq_mol_m3"]),
            ),
            repeat_count=repeat_count,
        )
        exact_result = exact_attempt.result
        rows.append(_exact_row(source_row, case, simulation_id, exact_attempt, policy_summaries))
        for policy in PICARD_POLICY_GRID:
            summary = policy_summaries[policy.closure_name]
            policy_attempt = _timed_repeat(
                lambda policy=policy: solve_pure_saturation(
                    case,
                    temperature=float(source_row["T_K"]),
                    closure_name=policy.closure_name,
                    pressure_seed_Pa=float(source_row["p_sat_Pa"]),
                    liquid_density_seed_mol_m3=float(source_row["rho_sat_liq_mol_m3"]),
                ),
                repeat_count=repeat_count,
            )
            rows.append(
                _policy_row(
                    source_row,
                    case,
                    simulation_id,
                    policy,
                    summary,
                    exact_attempt,
                    policy_attempt,
                    exact_result,
                )
            )
    if not rows:
        raise ValueError("final Picard admission report produced no rows.")
    recommendation = _issue_161_recommendation(rows)
    for row in rows:
        row["issue_161_recommendation"] = recommendation
    return rows


def classify_admission_band(row: Mapping[str, object]) -> str:
    if row["solver_status_exact"] != "computed_toy_pure_saturation":
        return "m8_continue_only"
    if row["policy_name"] == EXACT_MASS_ACTION_BASELINE:
        return "exact_reference"
    if row["solver_status_picard"] != "computed_toy_pure_saturation":
        return "provider_blocked"
    errors = [
        _float_or_nan(row["association_helmholtz_relative_error"]),
        _float_or_nan(row["total_ares_proxy_relative_error"]),
        _float_or_nan(row["pressure_proxy_relative_error"]),
        _float_or_nan(row["saturation_pressure_relative_error"]),
        _float_or_nan(row["liquid_density_relative_error"]),
        _float_or_nan(row["vapor_density_relative_error"]),
        _float_or_nan(row["derivative_max_relative_error"]),
        _float_or_nan(row["hessian_max_relative_error"]),
    ]
    if not np.all(np.isfinite(errors)):
        return "provider_blocked"
    if max(errors) > 1.0e-2:
        return "provider_blocked"
    if max(errors) <= 1.0e-4 and _float_or_nan(row["simulation_speedup_vs_exact"]) >= 1.0:
        return "m8_continue_only"
    return "m8_continue_only"


def generate_final_picard_admission_report(
    output_path: Path = DEFAULT_OUTPUT,
    memo_path: Path = DEFAULT_MEMO,
    *,
    repeat_count: int = 3,
    max_source_rows: int | None = DEFAULT_MAX_SOURCE_ROWS,
) -> Path:
    rows = build_final_picard_admission_rows(repeat_count=repeat_count, max_source_rows=max_source_rows)
    write_rows_csv(_ordered_rows(rows), output_path)
    _write_memo(rows, memo_path)
    return output_path


def _selected_source_rows(
    rows: Sequence[Mapping[str, object]],
    *,
    max_source_rows: int | None,
) -> list[dict[str, object]]:
    matched = [dict(row) for row in rows if str(row.get("component", "")).lower() in {"methanol", "water"}]
    matched.sort(key=lambda row: (str(row["component"]).lower(), float(row["T_K"])))
    if max_source_rows is None:
        return matched
    if max_source_rows <= 0:
        raise ValueError("max_source_rows must be positive when provided.")
    selected: list[dict[str, object]] = []
    by_component = sorted({str(row["component"]).lower() for row in matched})
    per_component = max(1, int(np.ceil(max_source_rows / max(len(by_component), 1))))
    for component in by_component:
        component_rows = [row for row in matched if str(row["component"]).lower() == component]
        selected.extend(_spread_rows(component_rows, per_component))
    return selected[:max_source_rows]


def _spread_rows(rows: Sequence[dict[str, object]], count: int) -> list[dict[str, object]]:
    if len(rows) <= count:
        return list(rows)
    indices = np.linspace(0, len(rows) - 1, count, dtype=int)
    return [rows[int(index)] for index in indices]


def _policy_metric_summaries(rows: Sequence[Mapping[str, object]]) -> dict[str, dict[str, object]]:
    summaries: dict[str, dict[str, object]] = {}
    exact_times = [float(row["exact_implicit_elapsed_median_seconds"]) for row in rows]
    exact_time = statistics.median(exact_times)
    for policy in PICARD_POLICY_GRID:
        policy_rows = [row for row in rows if str(row["policy_name"]) == policy.closure_name]
        if not policy_rows:
            raise ValueError(f"policy grid missing rows for {policy.closure_name}.")
        summaries[policy.closure_name] = {
            "exact_iteration_count": int(max(int(row["exact_iteration_count"]) for row in policy_rows)),
            "association_helmholtz_relative_error": max(
                float(row["association_helmholtz_relative_error"]) for row in policy_rows
            ),
            "total_ares_proxy_relative_error": max(float(row["total_ares_proxy_relative_error"]) for row in policy_rows),
            "pressure_proxy_relative_error": max(float(row["pressure_proxy_relative_error"]) for row in policy_rows),
            "derivative_max_relative_error": max(float(row["derivative_max_relative_error"]) for row in policy_rows),
            "hessian_max_relative_error": max(float(row["hessian_max_relative_error"]) for row in policy_rows),
            "closure_elapsed_median_seconds_exact": exact_time,
            "closure_elapsed_median_seconds_picard": statistics.median(
                float(row["policy_elapsed_median_seconds"]) for row in policy_rows
            ),
            "closure_speedup_vs_exact": statistics.median(
                float(row["speedup_vs_exact_implicit"]) for row in policy_rows
            ),
            "pareto_band": _best_label(row["pareto_band"] for row in policy_rows),
            "candidate_policy_label": _best_label(row["candidate_policy_label"] for row in policy_rows),
        }
    return summaries


def _exact_row(
    source_row: Mapping[str, object],
    case: Mapping[str, object],
    simulation_id: str,
    exact_attempt: "_TimedAttempt[PureSaturationResult]",
    policy_summaries: Mapping[str, Mapping[str, object]],
) -> dict[str, object]:
    exact_result = exact_attempt.result
    exact_time = _median_or_blank(exact_attempt.timings)
    first_summary = next(iter(policy_summaries.values()))
    row = _base_report_row(source_row, case, simulation_id)
    row.update(
        {
            "step_count": "",
            "damping": "",
            "policy_name": EXACT_MASS_ACTION_BASELINE,
            "exact_iteration_count": first_summary["exact_iteration_count"],
            "solver_status_exact": _result_status(exact_attempt),
            "solver_status_picard": "",
            "density_root_status_exact": _result_status(exact_attempt),
            "density_root_status_picard": "",
            "association_helmholtz_relative_error": 0.0,
            "total_ares_proxy_relative_error": 0.0,
            "pressure_proxy_relative_error": 0.0,
            "saturation_pressure_relative_error": 0.0,
            "liquid_density_relative_error": 0.0,
            "vapor_density_relative_error": 0.0,
            "derivative_max_relative_error": 0.0,
            "hessian_max_relative_error": 0.0,
            "closure_elapsed_median_seconds_exact": first_summary["closure_elapsed_median_seconds_exact"],
            "closure_elapsed_median_seconds_picard": "",
            "simulation_elapsed_median_seconds_exact": exact_time,
            "simulation_elapsed_median_seconds_picard": "",
            "closure_speedup_vs_exact": "",
            "simulation_speedup_vs_exact": "",
            "pareto_band": "exact_reference",
            "model_p_sat_exact_Pa": _result_value(exact_result, "p_sat_Pa"),
            "model_p_sat_picard_Pa": "",
            "model_rho_vap_exact_mol_m3": _result_value(exact_result, "rho_vap_mol_m3"),
            "model_rho_vap_picard_mol_m3": "",
            "model_rho_liq_exact_mol_m3": _result_value(exact_result, "rho_liq_mol_m3"),
            "model_rho_liq_picard_mol_m3": "",
            "message": exact_attempt.message,
        }
    )
    row["admission_band"] = classify_admission_band(row)
    row["issue_161_recommendation"] = ""
    return row


def _policy_row(
    source_row: Mapping[str, object],
    case: Mapping[str, object],
    simulation_id: str,
    policy: PicardPolicy,
    summary: Mapping[str, object],
    exact_attempt: "_TimedAttempt[PureSaturationResult]",
    policy_attempt: "_TimedAttempt[PureSaturationResult]",
    exact_result: PureSaturationResult | None,
) -> dict[str, object]:
    policy_result = policy_attempt.result
    exact_time = _median_or_blank(exact_attempt.timings)
    policy_time = _median_or_blank(policy_attempt.timings)
    row = _base_report_row(source_row, case, simulation_id)
    row.update(
        {
            "step_count": policy.step_count,
            "damping": policy.damping,
            "policy_name": policy.closure_name,
            "exact_iteration_count": summary["exact_iteration_count"],
            "solver_status_exact": _result_status(exact_attempt),
            "solver_status_picard": _result_status(policy_attempt),
            "density_root_status_exact": _result_status(exact_attempt),
            "density_root_status_picard": _result_status(policy_attempt),
            "association_helmholtz_relative_error": summary["association_helmholtz_relative_error"],
            "total_ares_proxy_relative_error": summary["total_ares_proxy_relative_error"],
            "pressure_proxy_relative_error": summary["pressure_proxy_relative_error"],
            "saturation_pressure_relative_error": _relative_result_value(policy_result, exact_result, "p_sat_Pa"),
            "liquid_density_relative_error": _relative_result_value(policy_result, exact_result, "rho_liq_mol_m3"),
            "vapor_density_relative_error": _relative_result_value(policy_result, exact_result, "rho_vap_mol_m3"),
            "derivative_max_relative_error": summary["derivative_max_relative_error"],
            "hessian_max_relative_error": summary["hessian_max_relative_error"],
            "closure_elapsed_median_seconds_exact": summary["closure_elapsed_median_seconds_exact"],
            "closure_elapsed_median_seconds_picard": summary["closure_elapsed_median_seconds_picard"],
            "simulation_elapsed_median_seconds_exact": exact_time,
            "simulation_elapsed_median_seconds_picard": policy_time,
            "closure_speedup_vs_exact": summary["closure_speedup_vs_exact"],
            "simulation_speedup_vs_exact": _speedup(exact_time, policy_time),
            "pareto_band": summary["pareto_band"],
            "model_p_sat_exact_Pa": _result_value(exact_result, "p_sat_Pa"),
            "model_p_sat_picard_Pa": _result_value(policy_result, "p_sat_Pa"),
            "model_rho_vap_exact_mol_m3": _result_value(exact_result, "rho_vap_mol_m3"),
            "model_rho_vap_picard_mol_m3": _result_value(policy_result, "rho_vap_mol_m3"),
            "model_rho_liq_exact_mol_m3": _result_value(exact_result, "rho_liq_mol_m3"),
            "model_rho_liq_picard_mol_m3": _result_value(policy_result, "rho_liq_mol_m3"),
            "message": policy_attempt.message,
        }
    )
    row["admission_band"] = classify_admission_band(row)
    row["issue_161_recommendation"] = ""
    return row


def _base_report_row(source_row: Mapping[str, object], case: Mapping[str, object], simulation_id: str) -> dict[str, object]:
    component = str(source_row["component"]).lower()
    topology = _topology(case)
    return {
        "case_id": component,
        "topology_id": topology,
        "simulation_id": simulation_id,
        "simulation_type": "pure_saturation",
        "component_family": component,
        "mixture_family": "pure_component",
        "reference_p_sat_Pa": float(source_row["p_sat_Pa"]),
        "reference_rho_liq_mol_m3": float(source_row["rho_sat_liq_mol_m3"]),
        "source_url": str(source_row.get("source_url", "")),
        "parameter_source": str(case.get("parameter_source", "inline_provider_case")),
    }


class _TimedAttempt[T]:
    def __init__(self, result: T | None, timings: list[float], message: str) -> None:
        self.result = result
        self.timings = timings
        self.message = message


def _timed_repeat(function: Callable[[], T], *, repeat_count: int) -> _TimedAttempt[T]:
    result: T | None = None
    timings: list[float] = []
    message = "computed"
    for _ in range(repeat_count):
        try:
            value, elapsed = timed_closure(function)
        except Exception as exc:
            message = str(exc)
            return _TimedAttempt(result=None, timings=timings, message=message)
        result = value
        timings.append(elapsed)
    return _TimedAttempt(result=result, timings=timings, message=message)


def _ordered_rows(rows: Sequence[Mapping[str, object]]) -> list[dict[str, object]]:
    return [{column: row.get(column, "") for column in FINAL_REPORT_COLUMNS} for row in rows]


def _write_memo(rows: Sequence[Mapping[str, object]], memo_path: Path) -> Path:
    memo_path.parent.mkdir(parents=True, exist_ok=True)
    recommendation = _issue_161_recommendation(rows)
    high_accuracy = _best_policy(rows, label="high_accuracy")
    fastest = _fastest_policy(rows)
    worst_error = _worst_error_row(rows)
    worst_residual = _worst_simulation_row(rows)
    lines = [
        "# Issue 161 Picard Admission Decision",
        "",
        "This M8 toybox memo summarizes the final fixed-policy Picard evidence packet for issue #161.",
        "",
        "| Field | Value |",
        "| --- | --- |",
        f"| Retained rows | {len(rows)} |",
        f"| Best high-accuracy policy | {high_accuracy} |",
        f"| Fastest simulation policy | {fastest} |",
        f"| Worst relative-error row | {worst_error} |",
        f"| Worst simulation residual row | {worst_residual} |",
        f"| Issue #161 recommendation | `{recommendation}` |",
        "",
        "Provider implementation remains blocked unless the recommendation is "
        "`close_design_complete_open_narrow_provider_admission_issue`.",
        "",
        "JAX and Python toybox evidence remain proxy evidence; provider CppAD behavior still requires separate M3 proof.",
    ]
    memo_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return memo_path


def _issue_161_recommendation(rows: Sequence[Mapping[str, object]]) -> str:
    bands = {str(row.get("admission_band", "")) for row in rows}
    if "provider_blocked" in bands:
        return "close_without_provider_implementation"
    if "provider_candidate" in bands:
        return "close_design_complete_open_narrow_provider_admission_issue"
    return "keep_blocked_for_named_missing_evidence"


def _best_policy(rows: Sequence[Mapping[str, object]], *, label: str) -> str:
    candidates = [
        row
        for row in rows
        if row["policy_name"] != EXACT_MASS_ACTION_BASELINE and row["pareto_band"] in {label, "pareto_frontier"}
    ]
    if not candidates:
        candidates = [row for row in rows if row["policy_name"] != EXACT_MASS_ACTION_BASELINE]
    if not candidates:
        return "none"
    best = min(candidates, key=_max_relative_error)
    return f"{best['policy_name']} at {best['simulation_id']}"


def _fastest_policy(rows: Sequence[Mapping[str, object]]) -> str:
    candidates = [
        row
        for row in rows
        if row["policy_name"] != EXACT_MASS_ACTION_BASELINE
        and _float_or_nan(row["simulation_elapsed_median_seconds_picard"]) > 0.0
    ]
    if not candidates:
        return "none"
    best = min(candidates, key=lambda row: _float_or_nan(row["simulation_elapsed_median_seconds_picard"]))
    return f"{best['policy_name']} at {best['simulation_id']}"


def _worst_error_row(rows: Sequence[Mapping[str, object]]) -> str:
    candidates = [row for row in rows if row["policy_name"] != EXACT_MASS_ACTION_BASELINE]
    if not candidates:
        return "none"
    worst = max(candidates, key=_max_relative_error)
    return f"{worst['policy_name']} at {worst['simulation_id']} max_rel={_max_relative_error(worst):.3e}"


def _worst_simulation_row(rows: Sequence[Mapping[str, object]]) -> str:
    failures = [row for row in rows if row["policy_name"] != EXACT_MASS_ACTION_BASELINE and row["solver_status_picard"] != "computed_toy_pure_saturation"]
    if failures:
        row = failures[0]
        return f"{row['policy_name']} at {row['simulation_id']} status={row['solver_status_picard']}"
    return _worst_error_row(rows)


def _max_relative_error(row: Mapping[str, object]) -> float:
    keys = (
        "association_helmholtz_relative_error",
        "total_ares_proxy_relative_error",
        "pressure_proxy_relative_error",
        "saturation_pressure_relative_error",
        "liquid_density_relative_error",
        "vapor_density_relative_error",
        "derivative_max_relative_error",
        "hessian_max_relative_error",
    )
    return max(_float_or_nan(row[key]) for key in keys)


def _relative_result_value(actual: PureSaturationResult | None, reference: PureSaturationResult | None, attr: str) -> object:
    if actual is None or reference is None:
        return ""
    return relative_error(float(getattr(actual, attr)), float(getattr(reference, attr)))


def _result_value(result: PureSaturationResult | None, attr: str) -> object:
    return "" if result is None else float(getattr(result, attr))


def _result_status(attempt: _TimedAttempt[PureSaturationResult]) -> str:
    return "computed_toy_pure_saturation" if attempt.result is not None else "solve_failed"


def _median_or_blank(values: Sequence[float]) -> object:
    return "" if not values else statistics.median(values)


def _speedup(exact_time: object, policy_time: object) -> object:
    exact = _float_or_nan(exact_time)
    policy = _float_or_nan(policy_time)
    if not np.isfinite(exact) or not np.isfinite(policy) or policy <= 0.0:
        return ""
    return exact / policy


def _float_or_nan(value: object) -> float:
    if value in {"", None}:
        return float("nan")
    return float(value)


def _topology(case: Mapping[str, object]) -> str:
    parameters = case.get("parameters", {})
    if not isinstance(parameters, Mapping):
        return "unknown"
    raw = parameters.get("assoc_scheme", "none")
    values = raw if isinstance(raw, list) else [raw]
    return "_".join(str(value).lower() for value in values)


def _simulation_id(row: Mapping[str, object]) -> str:
    return f"{str(row['component']).lower()}_{float(row['T_K']):.2f}K"


def _best_label(values: Sequence[object]) -> str:
    order = ("high_accuracy", "balanced", "fast", "diagnostic_candidate", "diagnostic_only", "pareto_frontier", "dominated")
    text_values = {str(value) for value in values}
    for label in order:
        if label in text_values:
            return label
    return sorted(text_values)[0]


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate final Picard admission evidence for issue #161.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--memo", type=Path, default=DEFAULT_MEMO)
    parser.add_argument("--repeat-count", type=int, default=3)
    parser.add_argument("--max-source-rows", type=int, default=DEFAULT_MAX_SOURCE_ROWS)
    args = parser.parse_args()
    print(
        generate_final_picard_admission_report(
            output_path=args.output,
            memo_path=args.memo,
            repeat_count=args.repeat_count,
            max_source_rows=args.max_source_rows,
        )
    )


if __name__ == "__main__":
    main()
