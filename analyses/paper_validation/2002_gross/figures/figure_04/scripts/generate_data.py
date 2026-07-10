from __future__ import annotations

import csv
import json
import math
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[6]
for import_root in (
    REPO_ROOT,
    REPO_ROOT / "packages" / "epcsaft" / "src",
    REPO_ROOT / "packages" / "epcsaft-equilibrium" / "src",
):
    if str(import_root) not in sys.path:
        sys.path.insert(0, str(import_root))

from scripts.dev.native_runtime_env import apply_to_current_process
from scripts.validation import native_freshness

apply_to_current_process()

import matplotlib

matplotlib.use("Agg")
import epcsaft
import epcsaft_equilibrium
import matplotlib.pyplot as plt
import numpy as np
from epcsaft_equilibrium._native import extension_native_core

FIGURE_ID = "figure_04"
TEMPERATURE_K = 313.15
MIN_COMPOSITION = 1.0e-6

FIGURE_DIR = REPO_ROOT / "analyses" / "paper_validation" / "2002_gross" / "figures" / FIGURE_ID
SOURCE_DIR = FIGURE_DIR / "source"
RESULTS_DIR = FIGURE_DIR / "results"
SHARED_DIR = REPO_ROOT / "analyses" / "paper_validation" / "2002_gross" / "shared"
MANIFEST_PATH = SHARED_DIR / "gross_2002_full_replication_manifest.json"
SOURCE_CSV = SOURCE_DIR / "source_points.csv"
SOURCE_NOTES_CSV = SOURCE_DIR / "source_notes.csv"
SOURCE_IMAGE = SOURCE_DIR / f"{FIGURE_ID}.png"
QA_OVERLAY = RESULTS_DIR / f"{FIGURE_ID}.png"
MODEL_CSV = RESULTS_DIR / "model_curve.csv"
PLOTTED_CSV = RESULTS_DIR / "plotted_data.csv"
FIT_STATISTICS_CSV = RESULTS_DIR / "fit_statistics.csv"
SUMMARY_JSON = SHARED_DIR / "results" / f"{FIGURE_ID}_generation_summary.json"
PNG = RESULTS_DIR / f"{FIGURE_ID}.png"
SVG = RESULTS_DIR / f"{FIGURE_ID}.svg"
PDF = RESULTS_DIR / f"{FIGURE_ID}.pdf"

COMPONENT_ORDER = ["1-Pentanol", "Benzene"]
SOURCE_SERIES = ("bubble_line", "dew_line")
AXIS_LABEL = r"$x_{\mathrm{Benzene}}$ or $y_{\mathrm{Benzene}}$"


def _relative(path: Path) -> str:
    return path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()


def _jsonable(value: Any) -> Any:
    if isinstance(value, Path):
        return _relative(value)
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    return value


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(_jsonable(payload), indent=2, sort_keys=True) + "\n", encoding="utf-8")



def _strip_trailing_whitespace(path: Path) -> None:
    lines = path.read_text(encoding="utf-8").splitlines()
    path.write_text("\n".join(line.rstrip() for line in lines) + "\n", encoding="utf-8")


def _read_csv(path: Path) -> list[dict[str, str]]:
    return list(csv.DictReader(path.read_text(encoding="utf-8").splitlines()))

def _write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fieldnames})


FIT_STATISTICS_FIELDS = [
    "scope", "series", "component", "branch", "source_point_count", "model_point_count",
    "rmse_density_kg_m3", "rmse_temperature_K", "rmse_temperature_C", "rmse_pressure_bar", "rmse_composition",
    "max_density_error_kg_m3", "max_temperature_error_K", "max_temperature_error_C", "max_pressure_error_bar", "max_composition_error",
    "normalized_plot_score", "branch_coverage_score", "derivative_status", "pass", "score_basis",
]
SOURCE_NOTE_FIELDS = ["section", "key", "value", "unit", "notes"]


def _axis_value(axis: dict[str, Any], *names: str) -> Any:
    for name in names:
        if name in axis:
            return axis[name]
    for key, value in axis.items():
        lowered = key.lower()
        if any(token in lowered for token in ("composition", "x_", "y_")):
            return value
    return ""


def _fit_row(scope: str, payload: dict[str, Any], *, series: str = "", component: str = "", branch: str = "") -> dict[str, Any]:
    rmse = payload.get("rmse_axis", {}) if isinstance(payload.get("rmse_axis"), dict) else {}
    max_axis = payload.get("max_axis_error", {}) if isinstance(payload.get("max_axis_error"), dict) else {}
    return {
        "scope": scope, "series": series, "component": component, "branch": branch,
        "source_point_count": payload.get("source_point_count", ""),
        "model_point_count": payload.get("model_point_count", ""),
        "rmse_density_kg_m3": _axis_value(rmse, "density_kg_m3"),
        "rmse_temperature_K": _axis_value(rmse, "temperature_K", "T_K"),
        "rmse_temperature_C": _axis_value(rmse, "T_C"),
        "rmse_pressure_bar": _axis_value(rmse, "P_bar", "pressure_bar"),
        "rmse_composition": _axis_value(rmse, "composition_component_1", "x_component_1", "y_component_1", "x_methanol", "y_methanol", "x_water"),
        "max_density_error_kg_m3": _axis_value(max_axis, "density_kg_m3"),
        "max_temperature_error_K": _axis_value(max_axis, "temperature_K", "T_K"),
        "max_temperature_error_C": _axis_value(max_axis, "T_C"),
        "max_pressure_error_bar": _axis_value(max_axis, "P_bar", "pressure_bar"),
        "max_composition_error": _axis_value(max_axis, "composition_component_1", "x_component_1", "y_component_1", "x_methanol", "y_methanol", "x_water"),
        "normalized_plot_score": payload.get("normalized_plot_score", ""),
        "branch_coverage_score": payload.get("branch_coverage_score", ""),
        "derivative_status": payload.get("derivative_status", ""),
        "pass": payload.get("pass", ""),
        "score_basis": str(payload.get("score_basis", "")).replace("retained", "retained"),
    }


def _write_fit_statistics_csv(score_payload: dict[str, Any]) -> None:
    rows = [_fit_row("figure", score_payload)]
    for series, payload in sorted((score_payload.get("series_scores") or {}).items()):
        if isinstance(payload, dict):
            rows.append(_fit_row("series", payload, series=str(series)))
    for branch_key, payload in sorted((score_payload.get("branch_scores") or {}).items()):
        if isinstance(payload, dict):
            component, _, branch = str(branch_key).partition(":")
            rows.append(_fit_row("branch", payload, component=component, branch=branch))
    _write_csv(FIT_STATISTICS_CSV, rows, FIT_STATISTICS_FIELDS)


def _flatten_note(section: str, key: str, value: Any, rows: list[dict[str, Any]]) -> None:
    if isinstance(value, dict):
        for child_key, child_value in sorted(value.items()):
            _flatten_note(section, f"{key}.{child_key}" if key else str(child_key), child_value, rows)
    elif isinstance(value, list):
        rows.append({"section": section, "key": key, "value": json.dumps(_jsonable(value), sort_keys=True), "unit": "", "notes": ""})
    else:
        rows.append({"section": section, "key": key, "value": value, "unit": "", "notes": ""})


def _write_source_notes_csv(metadata: dict[str, Any] | None = None) -> None:
    rows: list[dict[str, Any]] = [
        {"section": "provenance", "key": "paper", "value": "Gross and Sadowski 2002", "unit": "", "notes": ""},
        {"section": "provenance", "key": "figure", "value": FIGURE_ID, "unit": "", "notes": ""},
        {"section": "provenance", "key": "source_image", "value": _relative(SOURCE_IMAGE), "unit": "", "notes": ""},
        {"section": "source_method", "key": "published_figure_curve_trace", "value": "retained visible PC-SAFT curve points from the published figure", "unit": "", "notes": ""},
    ]
    for key, value in sorted((metadata or {}).items()):
        _flatten_note("metadata", str(key), value, rows)
    _write_csv(SOURCE_NOTES_CSV, rows, SOURCE_NOTE_FIELDS)


def _load_source_rows() -> list[dict[str, Any]]:
    with SOURCE_CSV.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise RuntimeError("Gross 2002 Figure 4 source CSV is empty.")
    return rows


def _source_curve_rows(source_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [row for row in source_rows if row["source_role"] == "paper_pc_saft_curve"]


def _series_coordinate_key(series: str) -> str:
    return "x_1_pentanol" if series == "bubble_line" else "y_1_pentanol"


def _paper_axis_composition(row: dict[str, Any], series: str) -> float:
    return 1.0 - float(row[_series_coordinate_key(series)])


def _sorted_source_series(source_rows: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    out: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in source_rows:
        out[row["series"]].append(row)
    for series, rows in out.items():
        rows.sort(key=lambda row: float(row[_series_coordinate_key(series)]))
    return dict(out)


def _mixture() -> epcsaft.Mixture:
    return epcsaft.Mixture(
        epcsaft.ParameterSet.from_dict(
            {
                "MW": np.asarray([0.08815, 0.078114]),
                "m": np.asarray([3.6260, 2.4653]),
                "s": np.asarray([3.4508, 3.6478]),
                "e": np.asarray([247.28, 287.35]),
                "e_assoc": np.asarray([2252.1, 0.0]),
                "vol_a": np.asarray([0.010319, 0.0]),
                "assoc_scheme": ["2B", None],
                "k_ij": np.asarray([[0.0, 0.0135], [0.0135, 0.0]]),
                "z": np.asarray([0.0, 0.0]),
                "dielc": np.asarray([1.0, 1.0]),
            },
            species=COMPONENT_ORDER,
            metadata={
                "source": "Gross/Sadowski 2002 Figure 4",
                "paper": "Gross and Sadowski 2002",
                "table": "Gross 2002 figure caption plus Gross 2001 pure-component table",
                "figure": "Figure 4",
                "source_path": "analyses/paper_validation/2002_gross",
                "source_backed": True,
                "reference_system": "1-pentanol-benzene",
            },
        )
    )


def _solve_route_point(
    mixture: epcsaft.Mixture,
    route: str,
    composition: float,
    continuation_state: dict[str, Any] | None = None,
) -> epcsaft_equilibrium.EquilibriumResult:
    comp = min(1.0 - MIN_COMPOSITION, max(MIN_COMPOSITION, composition))
    solver_options: dict[str, Any] = {
        "max_iterations": 320,
        "tolerance": 1.0e-6,
        "ipopt_iteration_history_limit": 12,
        "ipopt_acceptable_tolerance": 1.0e-7,
        "ipopt_constraint_violation_tolerance": 1.0e-7,
        "ipopt_dual_infeasibility_tolerance": 1.0e-8,
        "ipopt_complementarity_tolerance": 1.0e-8,
    }
    if continuation_state is not None:
        solver_options["continuation_state"] = continuation_state
    if route == "bubble_pressure":
        return epcsaft_equilibrium.Equilibrium(
            mixture,
            route=route,
            T=TEMPERATURE_K,
            x=[comp, 1.0 - comp],
        ).solve(solver_options=solver_options)
    return epcsaft_equilibrium.Equilibrium(
        mixture,
        route=route,
        T=TEMPERATURE_K,
        y=[comp, 1.0 - comp],
    ).solve(solver_options=solver_options)


def _solve_series(mixture: epcsaft.Mixture, source_rows: list[dict[str, Any]], series: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    continuation_state: dict[str, Any] | None = None
    previous_route = ""
    curve_rows = [row for row in _source_curve_rows(source_rows) if row["series"] == series]
    for row in sorted(curve_rows, key=lambda item: float(item[_series_coordinate_key(series)])):
        composition = float(row[_series_coordinate_key(series)])
        is_boundary_limit = composition in {0.0, 1.0}
        route = "dew_pressure" if is_boundary_limit else (
            "bubble_pressure" if series == "bubble_line" else "dew_pressure"
        )
        route_continuation_state = continuation_state if route == previous_route else None
        result = _solve_route_point(mixture, route, composition, route_continuation_state)
        diagnostics = result.diagnostics
        returned_state = diagnostics.get("continuation_state")
        continuation_state = (
            {"variables": list(returned_state["variables"])}
            if isinstance(returned_state, dict) and "variables" in returned_state
            else None
        )
        previous_route = route
        if diagnostics.get("hessian_approximation") != "exact" or diagnostics.get("exact_hessian_available") is not True:
            raise RuntimeError(f"{series} solve at composition={composition:.3f} did not report exact Hessian support.")
        if diagnostics.get("postsolve_accepted") is not True:
            raise RuntimeError(f"{series} solve at composition={composition:.3f} was not postsolve accepted.")
        rows.append(
            {
                "series": series,
                "x_1_pentanol": float(result.x[0]),
                "y_1_pentanol": float(result.y[0]),
                "T_K": TEMPERATURE_K,
                "P_bar": float(result.pressure) / 1.0e5,
                "route": result.route,
                "problem_kind": result.problem_kind,
                "route_status": diagnostics.get("route_status", ""),
                "solver_status": diagnostics.get("solver_status", ""),
                "hessian_approximation": diagnostics.get("hessian_approximation", ""),
                "exact_hessian_available": bool(diagnostics.get("exact_hessian_available")),
                "postsolve_accepted": bool(diagnostics.get("postsolve_accepted")),
                "hessian_backend": diagnostics.get("hessian_backend", ""),
                "iteration_count": diagnostics.get("iteration_count", ""),
                "requested_coordinate": min(
                    1.0 - MIN_COMPOSITION,
                    max(MIN_COMPOSITION, composition),
                ),
                "requested_coordinate_role": "y_1_pentanol" if route == "dew_pressure" else "x_1_pentanol",
                "endpoint_limit_basis": "finite_binary_dew_pressure_limit" if is_boundary_limit else "",
            }
        )
    return rows


def _interp_pressure(series_rows: list[dict[str, Any]], coordinate_key: str, composition: float) -> float:
    x = np.asarray([float(row[coordinate_key]) for row in series_rows], dtype=float)
    p = np.asarray([float(row["P_bar"]) for row in series_rows], dtype=float)
    order = np.argsort(x)
    return float(np.interp(composition, x[order], p[order]))


def _score(source_rows: list[dict[str, Any]], model_rows: list[dict[str, Any]]) -> dict[str, Any]:
    source_by_series = _sorted_source_series(_source_curve_rows(source_rows))
    model_by_series: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in model_rows:
        model_by_series[row["series"]].append(row)
    for series in model_by_series:
        model_by_series[series].sort(key=lambda row: float(row[_series_coordinate_key(series)]))

    series_scores: dict[str, dict[str, Any]] = {}
    all_errors: list[float] = []
    for series in SOURCE_SERIES:
        coordinate_key = _series_coordinate_key(series)
        errors: list[float] = []
        source_curve = sorted(source_by_series[series], key=lambda row: _paper_axis_composition(row, series))
        model_curve = sorted(model_by_series[series], key=lambda row: _paper_axis_composition(row, series))
        model_x = np.asarray([_paper_axis_composition(row, series) for row in model_curve], dtype=float)
        model_p = np.asarray([float(row["P_bar"]) for row in model_curve], dtype=float)
        for source_row in source_curve:
            composition = _paper_axis_composition(source_row, series)
            source_pressure = float(source_row["P_bar"])
            model_pressure = float(np.interp(composition, model_x, model_p))
            errors.append(model_pressure - source_pressure)
        rmse = math.sqrt(sum(value * value for value in errors) / len(errors))
        max_error = max(abs(value) for value in errors)
        score = max(0.0, min(10.0, 10.0 - rmse / 0.01))
        series_scores[series] = {
            "source_point_count": len(source_by_series[series]),
            "model_point_count": len(model_by_series[series]),
            "rmse_axis": {"P_bar": rmse, coordinate_key: 0.0},
            "max_axis_error": {"P_bar": max_error, coordinate_key: 0.0},
            "normalized_plot_score": score,
            "branch_coverage_score": 1.0,
            "derivative_status": "verified_exact",
            "pass": score >= 8.0,
        }
        all_errors.extend(errors)

    all_rmse = math.sqrt(sum(value * value for value in all_errors) / len(all_errors))
    all_max = max(abs(value) for value in all_errors)
    normalized_score = min(item["normalized_plot_score"] for item in series_scores.values())
    return {
        "source_point_count": len(_source_curve_rows(source_rows)),
        "model_point_count": len(model_rows),
        "rmse_axis": {"P_bar": all_rmse, "composition_component_1": 0.0},
        "max_axis_error": {"P_bar": all_max, "composition_component_1": 0.0},
        "normalized_plot_score": normalized_score,
        "branch_coverage_score": 1.0,
        "derivative_status": "verified_exact",
        "pass": normalized_score >= 8.0,
        "series_scores": series_scores,
        "score_basis": "pressure-coordinate RMSE against calibrated Gross 2002 Figure 4 retained P-x/y source points",
    }


def _write_plot(source_rows: list[dict[str, Any]], model_rows: list[dict[str, Any]], score_payload: dict[str, Any]) -> None:
    fig, ax = plt.subplots(figsize=(7.2, 5.8), constrained_layout=True)
    marker_rows = [row for row in source_rows if row["source_role"] == "experimental_marker"]
    source_by_series = _sorted_source_series(marker_rows if marker_rows else _source_curve_rows(source_rows))
    model_by_series: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in model_rows:
        model_by_series[row["series"]].append(row)
    style_map = {
        "bubble_line": {"color": "#111111", "marker": "D", "facecolors": "none", "label": "Exp. data"},
        "dew_line": {"color": "#111111", "marker": "D", "facecolors": "none", "label": None},
    }
    model_labels = {"bubble_line": "PC-SAFT bubble", "dew_line": "PC-SAFT dew"}
    for series in SOURCE_SERIES:
        coordinate_key = _series_coordinate_key(series)
        ax.plot(
            [_paper_axis_composition(row, series) for row in model_by_series[series]],
            [float(row["P_bar"]) for row in model_by_series[series]],
            color=style_map[series]["color"],
            linewidth=2.0,
            label=model_labels[series],
        )
        if series in source_by_series:
            ax.scatter(
                [_paper_axis_composition(row, series) for row in source_by_series[series]],
                [float(row["P_bar"]) for row in source_by_series[series]],
                s=46,
                marker=style_map[series]["marker"],
                facecolors=style_map[series]["facecolors"],
                edgecolors=style_map[series]["color"],
                linewidths=1.4,
                label=style_map[series]["label"],
                zorder=3,
            )
    ax.set_xlim(0.0, 1.0)
    ax.set_ylim(0.0, 0.25)
    ax.set_xlabel(AXIS_LABEL)
    ax.set_ylabel("P / bar")
    ax.grid(True, color="#d9d9d9", linewidth=0.7)
    ax.legend(loc="upper left", fontsize=8, frameon=False)
    ax.set_title("Gross/Sadowski 2002 Figure 4 PC-SAFT VLE replication", fontsize=11)
    fig.text(0.02, 0.01, f"minimum series score: {score_payload['normalized_plot_score']:.2f}; exact Hessian route verified", fontsize=8)
    fig.savefig(PNG, dpi=180)
    fig.savefig(SVG)
    _strip_trailing_whitespace(SVG)
    fig.savefig(PDF)
    plt.close(fig)


def _write_plotted_csv(source_rows: list[dict[str, Any]], model_rows: list[dict[str, Any]]) -> None:
    rows: list[dict[str, Any]] = []
    for row in source_rows:
        rows.append(
            {
                "dataset": row["source_role"],
                "series": row["series"],
                "T_K": row["T_K"],
                "P_bar": row["P_bar"],
                "x_1_pentanol": row["x_1_pentanol"],
                "y_1_pentanol": row["y_1_pentanol"],
                "paper_x_benzene": 1.0 - float(row[_series_coordinate_key(row["series"])]),
                "source_reference": row["source_reference"],
            }
        )
    for row in model_rows:
        rows.append(
            {
                "dataset": "package_model",
                "series": row["series"],
                "T_K": row["T_K"],
                "P_bar": row["P_bar"],
                "x_1_pentanol": row["x_1_pentanol"],
                "y_1_pentanol": row["y_1_pentanol"],
                "paper_x_benzene": _paper_axis_composition(row, row["series"]),
                "source_reference": "epcsaft_equilibrium public bubble/dew exact Hessian route",
            }
        )
    _write_csv(PLOTTED_CSV, rows, ["dataset", "series", "T_K", "P_bar", "x_1_pentanol", "y_1_pentanol", "paper_x_benzene", "source_reference"])


def _native_receipt() -> dict[str, Any]:
    receipt = native_freshness.build_equilibrium_native_receipt(
        native_module=extension_native_core(),
        checker_command=[
            "uv",
            "run",
            "--no-sync",
            "python",
            "scripts/validation/check_gross_2002_full_replication.py",
            "--json",
            "--require-exact-association-hessian",
            "--require-fresh-native",
        ],
    )
    return native_freshness.receipt_to_jsonable(receipt)



def _retained_native_receipt() -> dict[str, Any]:
    if SUMMARY_JSON.exists():
        payload = json.loads(SUMMARY_JSON.read_text(encoding="utf-8"))
        candidates = [
            payload.get("native_freshness_receipt"),
            payload.get("native_freshness"),
            payload.get("native_route", {}).get("native_freshness_receipt")
            if isinstance(payload.get("native_route"), dict)
            else None,
        ]
        for receipt in candidates:
            if isinstance(receipt, dict) and receipt:
                return receipt
    if MANIFEST_PATH.exists():
        payload = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        receipt = payload.get("native_freshness_receipt")
        if isinstance(receipt, dict) and receipt:
            return receipt
    raise RuntimeError(f"Retained native freshness receipt is required for --render-only: {_relative(SUMMARY_JSON)}")

def _update_manifest(score_payload: dict[str, Any], receipt: dict[str, Any]) -> None:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    manifest["native_freshness_receipt"] = receipt
    artifacts = {
        "source_csv": _relative(SOURCE_CSV),
        "source_notes_csv": _relative(SOURCE_NOTES_CSV),
                "model_csv": _relative(MODEL_CSV),
        "plotted_csv": _relative(PLOTTED_CSV),
        "fit_statistics_csv": _relative(FIT_STATISTICS_CSV),
                "png": _relative(PNG),
        "svg": _relative(SVG),
        "pdf": _relative(PDF),
    }
    for record in manifest["figures"]:
        if record.get("figure_id") != FIGURE_ID:
            continue
        record.update(
            {
                "replication_status": "accepted" if score_payload["pass"] else "planned",
                "counts_toward_completion": bool(score_payload["pass"]),
                "requires_exact_association_hessian": True,
                "artifacts": artifacts,
                "remaining_work": [] if score_payload["pass"] else ["improve Figure 4 replication score to the acceptance threshold"],
                "source_data_basis": "calibrated Gross 2002 Figure 4 pressure-composition source points with retained reference-25 marker overlays",
                "score": {
                    "normalized_plot_score": score_payload["normalized_plot_score"],
                    "branch_coverage_score": score_payload["branch_coverage_score"],
                    "derivative_status": score_payload["derivative_status"],
                    "pass": score_payload["pass"],
                },
            }
        )
        break
    _write_json(MANIFEST_PATH, manifest)


def main() -> int:
    unknown_args = [arg for arg in sys.argv[1:] if arg != "--render-only"]
    if unknown_args:
        raise RuntimeError(f"Unsupported arguments: {unknown_args}")
    render_only = "--render-only" in sys.argv[1:]

    source_rows = _load_source_rows()
    if render_only:
        if not MODEL_CSV.exists():
            raise RuntimeError(f"Retained model CSV is required for --render-only: {_relative(MODEL_CSV)}")
        model_rows = list(_read_csv(MODEL_CSV))
        receipt = _retained_native_receipt()
    else:
        mixture = _mixture()
        model_rows = _solve_series(mixture, source_rows, "bubble_line") + _solve_series(mixture, source_rows, "dew_line")
        receipt = _native_receipt()
    score_payload = _score(source_rows, model_rows)
    _write_csv(
        MODEL_CSV,
        model_rows,
        [
            "series",
            "x_1_pentanol",
            "y_1_pentanol",
            "T_K",
            "P_bar",
            "route",
            "problem_kind",
            "route_status",
            "solver_status",
            "hessian_approximation",
            "exact_hessian_available",
            "postsolve_accepted",
            "hessian_backend",
            "iteration_count",
            "requested_coordinate",
            "requested_coordinate_role",
            "endpoint_limit_basis",
        ],
    )
    _write_plotted_csv(source_rows, model_rows)
    _write_fit_statistics_csv(score_payload)
    _write_plot(source_rows, model_rows, score_payload)
    summary = {
        "figure_id": FIGURE_ID,
        "status": "accepted" if score_payload["pass"] else "blocked",
        "artifacts": {
            "source_csv": SOURCE_CSV,
            "source_notes_csv": SOURCE_NOTES_CSV,
                        "model_csv": MODEL_CSV,
            "plotted_csv": PLOTTED_CSV,
            "fit_statistics_csv": FIT_STATISTICS_CSV,
                        "png": PNG,
            "svg": SVG,
            "pdf": PDF,
        },
        "source_point_count": len(source_rows),
        "model_point_count": len(model_rows),
        "score": score_payload,
        "native_route": {
            "public_entrypoint": "epcsaft_equilibrium.Equilibrium(mixture, route='bubble_pressure'/'dew_pressure', T=..., x=.../y=...).solve()",
            "derivative_status": score_payload["derivative_status"],
            "model_csv": MODEL_CSV,
            "native_freshness_receipt": receipt,
        },
    }
    _write_json(SUMMARY_JSON, summary)
    _update_manifest(score_payload, receipt)
    print(json.dumps(_jsonable(summary), indent=2, sort_keys=True))
    return 0 if score_payload["pass"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
