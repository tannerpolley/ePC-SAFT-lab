from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import math
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
FIGURE_ROOT = REPO_ROOT / "analyses" / "paper_validation" / "2026_khudaida" / "figures"
MANIFEST_PATH = REPO_ROOT / ".mplgallery" / "manifest.yaml"
EXPECTED_FIGURES = tuple(f"figure_{idx:02d}" for idx in range(1, 13))
FORMULA_COMPONENTS = ("x_water", "x_ethanol", "x_isobutanol", "x_nacl")
KHUDAIDA_MIN_PHASE_DISTANCE = 1.0e-3
KHUDAIDA_MINOR_BETA_REVIEW = 1.0e-4


def _load_contract_checker():
    path = REPO_ROOT / "analyses" / "paper_validation" / "scripts" / "check_figure_contract.py"
    spec = importlib.util.spec_from_file_location("paper_validation_figure_contract", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load figure contract checker from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError:
        return path.resolve().as_posix()


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def _truthy(value: str | bool | None) -> bool:
    if isinstance(value, bool):
        return value
    return str(value or "").strip().lower() in {"1", "true", "yes", "pass", "passed"}


def _finite_float(value: str | None) -> float:
    try:
        parsed = float(str(value or "").strip())
    except ValueError:
        return math.nan
    return parsed if math.isfinite(parsed) else math.nan


def _short_float(value: float) -> str:
    return f"{value:.6g}" if math.isfinite(value) else ""


def _phase_rows(tie_rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    return {row.get("phase", ""): row for row in tie_rows}


def _components_finite(tie_rows: list[dict[str, str]]) -> bool:
    return all(
        math.isfinite(_finite_float(row.get(component)))
        for row in tie_rows
        for component in FORMULA_COMPONENTS
    )


def _component_distance(tie_rows: list[dict[str, str]]) -> float:
    phases = _phase_rows(tie_rows)
    organic = phases.get("organic")
    aqueous = phases.get("aqueous")
    if organic is None or aqueous is None:
        return math.nan
    deltas = [
        abs(_finite_float(organic.get(component)) - _finite_float(aqueous.get(component)))
        for component in FORMULA_COMPONENTS
    ]
    return max(deltas) if all(math.isfinite(delta) for delta in deltas) else math.nan


def _phase_distance(tie_rows: list[dict[str, str]]) -> float:
    distances = [_finite_float(row.get("phase_distance")) for row in tie_rows]
    finite = [distance for distance in distances if math.isfinite(distance)]
    return min(finite) if finite else _component_distance(tie_rows)


def _minor_beta(tie_rows: list[dict[str, str]]) -> float:
    beta_values = [_finite_float(row.get("beta")) for row in tie_rows]
    finite = [value for value in beta_values if math.isfinite(value)]
    return min(finite) if finite else math.nan


def _collapsed_split_failure(tie_rows: list[dict[str, str]]) -> dict[str, str] | None:
    if not _components_finite(tie_rows):
        return None
    status_collapsed = any(str(row.get("status", "")).strip().lower() == "collapsed_split" for row in tie_rows)
    converged = all(_truthy(row.get("converged")) for row in tie_rows)
    phase_distance = _phase_distance(tie_rows)
    component_distance = _component_distance(tie_rows)
    minor_beta = _minor_beta(tie_rows)
    collapsed = math.isfinite(phase_distance) and phase_distance < KHUDAIDA_MIN_PHASE_DISTANCE
    duplicate_formula = math.isfinite(component_distance) and component_distance < KHUDAIDA_MIN_PHASE_DISTANCE
    trace_minor_phase = math.isfinite(minor_beta) and minor_beta < KHUDAIDA_MINOR_BETA_REVIEW
    if not status_collapsed and not (converged and (collapsed or duplicate_formula or trace_minor_phase)):
        return None
    return {
        "failure_kind": "collapsed_split",
        "root_cause": "postsolve_acceptance",
        "phase_distance": _short_float(phase_distance),
        "component_distance": _short_float(component_distance),
        "phase_distance_threshold": f"{KHUDAIDA_MIN_PHASE_DISTANCE:.6g}",
        "minor_beta": _short_float(minor_beta),
        "minor_beta_review_threshold": f"{KHUDAIDA_MINOR_BETA_REVIEW:.6g}",
        "follow_up_issue": "#338",
    }


def _model_row_failures(root: Path) -> list[dict[str, str]]:
    model_path = root / "results" / "data" / "model_tielines.csv"
    if not model_path.is_file():
        return []
    rows = _read_csv(model_path)
    grouped: dict[str, list[dict[str, str]]] = {}
    for row in rows:
        grouped.setdefault(row.get("tie_line", ""), []).append(row)

    failures = []
    for tie_line, tie_rows in sorted(grouped.items(), key=lambda item: int(item[0] or 0)):
        phases = sorted(row.get("phase", "") for row in tie_rows)
        converged = all(_truthy(row.get("converged")) for row in tie_rows)
        finite_components = _components_finite(tie_rows)
        collapsed = _collapsed_split_failure(tie_rows)
        if converged and finite_components and collapsed is None:
            continue
        first = tie_rows[0]
        failure_kind = "collapsed_split" if collapsed is not None else "solver_failure"
        failures.append(
            {
                "tie_line": tie_line,
                "phases": ",".join(phases),
                "converged": str(converged),
                "failure_kind": failure_kind,
                "root_cause": collapsed.get("root_cause", "") if collapsed is not None else "",
                "message": first.get("message", ""),
                "route_status": first.get("route_status", ""),
                "solver_status": first.get("solver_status", ""),
                "application_status": first.get("application_status", ""),
                "objective": first.get("objective", ""),
                "phase_distance": collapsed.get("phase_distance", first.get("phase_distance", ""))
                if collapsed is not None
                else first.get("phase_distance", ""),
                "component_distance": collapsed.get("component_distance", "") if collapsed is not None else "",
                "phase_distance_threshold": collapsed.get("phase_distance_threshold", "") if collapsed is not None else "",
                "minor_beta": collapsed.get("minor_beta", "") if collapsed is not None else "",
                "minor_beta_review_threshold": collapsed.get("minor_beta_review_threshold", "")
                if collapsed is not None
                else "",
                "follow_up_issue": collapsed.get("follow_up_issue", "") if collapsed is not None else "",
                "postsolve_accepted": first.get("postsolve_accepted", ""),
            }
        )
    return failures


def _manifest_paths() -> set[str]:
    if not MANIFEST_PATH.is_file():
        return set()
    paths = set()
    for line in MANIFEST_PATH.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped.startswith("svg_path:"):
            paths.add(stripped.split(":", 1)[1].strip().strip("'\""))
    return paths


def _figure_payload(figure_id: str, manifest_paths: set[str], contract_checker: Any) -> dict[str, Any]:
    root = FIGURE_ROOT / figure_id
    blockers = list(contract_checker.check_figure_root(root))
    svg_rel = f"analyses/paper_validation/2026_khudaida/figures/{figure_id}/results/{figure_id}.svg"
    if svg_rel not in manifest_paths:
        blockers.append(f"{svg_rel}:missing_mplgallery_manifest_entry")

    result_files = {}
    for suffix in (".svg", ".png", ".pdf"):
        path = root / "results" / f"{figure_id}{suffix}"
        result_files[suffix[1:]] = _relative(path)
        if path.is_file() and path.stat().st_size <= 0:
            blockers.append(f"{_relative(path)}:empty_result_artifact")

    fit_path = root / "results" / "fit_statistics.csv"
    fit_rows = _read_csv(fit_path) if fit_path.is_file() else []
    model_row_failures = _model_row_failures(root)
    model_fit_failures = []
    for row in fit_rows:
        series = row.get("series", "")
        if "package_electrolyte_lle_vs_experimental" not in series:
            continue
        if not _truthy(row.get("pass")):
            model_fit_failures.append(
                {
                    "figure": figure_id,
                    "series": series,
                    "temperature_K": row.get("temperature_K", ""),
                    "salt_wtfrac": row.get("salt_wtfrac", ""),
                    "source_point_count": row.get("source_point_count", ""),
                    "model_point_count": row.get("model_point_count", ""),
                    "accepted_model_count": row.get("accepted_model_count", ""),
                    "grand_aad": row.get("grand_aad", ""),
                    "rmse": row.get("rmse", ""),
                    "max_abs_error": row.get("max_abs_error", ""),
                    "normalized_plot_score": row.get("normalized_plot_score", ""),
                    "failed_tie_lines": row.get("failed_tie_lines", ""),
                    "failure_reasons": row.get("failure_reasons", ""),
                    "model_row_failures": model_row_failures,
                }
            )

    return {
        "figure": figure_id,
        "artifact_complete": not blockers,
        "blockers": sorted(set(blockers)),
        "result_files": result_files,
        "fit_statistics": fit_rows,
        "model_fit_failures": model_fit_failures,
        "model_row_failures": model_row_failures,
    }


def evaluate(selected_figures: tuple[str, ...] = EXPECTED_FIGURES) -> dict[str, Any]:
    contract_checker = _load_contract_checker()
    manifest_paths = _manifest_paths()
    figures = [_figure_payload(figure_id, manifest_paths, contract_checker) for figure_id in selected_figures]
    blockers = [blocker for figure in figures for blocker in figure["blockers"]]
    model_fit_failures = [failure for figure in figures for failure in figure["model_fit_failures"]]
    return {
        "checker": "khudaida_2026_figure_validation",
        "figure_count": len(figures),
        "artifact_complete": not blockers,
        "model_reproduction_complete": not model_fit_failures,
        "complete": not blockers,
        "blockers": blockers,
        "model_blockers": model_fit_failures,
        "figures": figures,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate Khudaida 2026 paper-validation figure artifacts.")
    parser.add_argument(
        "--figure",
        action="append",
        choices=EXPECTED_FIGURES,
        help="limit validation to one figure id; repeat to validate multiple figures",
    )
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--require-complete", action="store_true", help="fail on missing or malformed artifacts")
    parser.add_argument("--require-model-pass", action="store_true", help="fail when package model fits do not pass")
    args = parser.parse_args(argv)

    payload = evaluate(tuple(args.figure) if args.figure else EXPECTED_FIGURES)
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(
            "artifact_complete={artifact_complete} model_reproduction_complete={model_reproduction_complete} "
            "blockers={blockers} model_blockers={model_blockers}".format(
                artifact_complete=payload["artifact_complete"],
                model_reproduction_complete=payload["model_reproduction_complete"],
                blockers=len(payload["blockers"]),
                model_blockers=len(payload["model_blockers"]),
            )
        )
    if args.require_complete and payload["blockers"]:
        return 2
    if args.require_model_pass and payload["model_blockers"]:
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
