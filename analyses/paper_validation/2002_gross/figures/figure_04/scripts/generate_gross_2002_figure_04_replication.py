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
import matplotlib.pyplot as plt
import numpy as np

import epcsaft
import epcsaft_equilibrium
from epcsaft_equilibrium._native import extension_native_core

FIGURE_ID = "figure_04"
STEM = "gross_2002_figure_04_replication"
TEMPERATURE_K = 313.15
MIN_COMPOSITION = 1.0e-6

FIGURE_DIR = REPO_ROOT / "analyses" / "paper_validation" / "2002_gross" / "figures" / FIGURE_ID
SOURCE_DIR = FIGURE_DIR / "source"
RESULTS_DIR = FIGURE_DIR / "results"
SHARED_DIR = REPO_ROOT / "analyses" / "paper_validation" / "2002_gross" / "shared"
MANIFEST_PATH = SHARED_DIR / "gross_2002_full_replication_manifest.json"
SOURCE_CSV = SOURCE_DIR / f"{STEM}_source_points.csv"
SOURCE_METADATA_JSON = SOURCE_DIR / f"{STEM}_digitization_metadata.json"
QA_OVERLAY = SOURCE_DIR / f"{STEM}_digitization_qa_overlay.png"
MODEL_CSV = RESULTS_DIR / f"{STEM}_model_curve.csv"
PLOTTED_CSV = RESULTS_DIR / f"{STEM}_plotted_data.csv"
SCORE_JSON = RESULTS_DIR / f"{STEM}_score.json"
SUMMARY_JSON = RESULTS_DIR / f"{STEM}_summary.json"
PNG = RESULTS_DIR / f"{STEM}.png"
SVG = RESULTS_DIR / f"{STEM}.svg"
SIDECAR = RESULTS_DIR / f"{STEM}.mpl.yaml"

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


def _write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fieldnames})


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


def _pure_mixture(component: str) -> epcsaft.Mixture:
    if component == "1-Pentanol":
        payload = {
            "MW": np.asarray([0.08815]),
            "m": np.asarray([3.6260]),
            "s": np.asarray([3.4508]),
            "e": np.asarray([247.28]),
            "e_assoc": np.asarray([2252.1]),
            "vol_a": np.asarray([0.010319]),
            "assoc_scheme": ["2B"],
        }
    elif component == "Benzene":
        payload = {
            "MW": np.asarray([0.078114]),
            "m": np.asarray([2.4653]),
            "s": np.asarray([3.6478]),
            "e": np.asarray([287.35]),
            "e_assoc": np.asarray([0.0]),
            "vol_a": np.asarray([0.0]),
            "assoc_scheme": [None],
        }
    else:
        raise ValueError(component)
    return epcsaft.Mixture(
        epcsaft.ParameterSet.from_dict(
            payload,
            species=[component],
            metadata={"source": f"Gross/Sadowski 2002 Figure 4 pure {component}", "source_backed": True},
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
    curve_rows = [row for row in _source_curve_rows(source_rows) if row["series"] == series]
    for row in sorted(curve_rows, key=lambda item: float(item[_series_coordinate_key(series)])):
        composition = float(row[_series_coordinate_key(series)])
        if composition <= 1.0e-9 or composition >= 1.0 - 1.0e-9:
            pure_component = "1-Pentanol" if composition >= 1.0 - 1.0e-9 else "Benzene"
            pure_result = epcsaft_equilibrium.Equilibrium(
                _pure_mixture(pure_component),
                route="single_component_vle",
                T=TEMPERATURE_K,
            ).solve(
                solver_options={
                    "max_iterations": 220,
                    "tolerance": 1.0e-8,
                    "ipopt_print_level": 0,
                }
            )
            diagnostics = pure_result.diagnostics
            rows.append(
                {
                    "series": series,
                    "x_1_pentanol": composition,
                    "y_1_pentanol": composition,
                    "T_K": TEMPERATURE_K,
                    "P_bar": float(pure_result.P_sat) / 1.0e5,
                    "route": "single_component_vle",
                    "problem_kind": pure_result.problem_kind,
                    "route_status": diagnostics.get("route_status", ""),
                    "solver_status": diagnostics.get("solver_status", ""),
                    "hessian_approximation": diagnostics.get("hessian_approximation", ""),
                    "exact_hessian_available": bool(diagnostics.get("exact_hessian_available")),
                    "postsolve_accepted": bool(diagnostics.get("postsolve_accepted")),
                    "hessian_backend": diagnostics.get("hessian_backend", ""),
                    "iteration_count": diagnostics.get("iteration_count", ""),
                }
            )
            continue
        result = _solve_route_point(mixture, "bubble_pressure" if series == "bubble_line" else "dew_pressure", composition, continuation_state)
        diagnostics = result.diagnostics
        continuation_state = diagnostics.get("continuation_state")
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
            "pass": score >= 7.0,
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
        "pass": normalized_score >= 7.0,
        "series_scores": series_scores,
        "score_basis": "pressure-coordinate RMSE against calibrated Gross 2002 Figure 4 digitized P-x/y source points",
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
    plt.close(fig)
    SIDECAR.write_text(
        "\n".join(
            [
                "figure_id: figure_04",
                f"png: {_relative(PNG)}",
                f"svg: {_relative(SVG)}",
                "x_axis: composition_component_1",
                "y_axis: pressure_bar",
                "matplotlib_backend: Agg",
                "style: paper-scale P-x/y overlay with retained source markers and public-route PC-SAFT curves",
                "",
            ]
        ),
        encoding="utf-8",
    )


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
    receipt = native_freshness.build_receipt(
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


def _update_manifest(score_payload: dict[str, Any], receipt: dict[str, Any]) -> None:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    manifest["native_freshness_receipt"] = receipt
    artifacts = {
        "source_csv": _relative(SOURCE_CSV),
        "source_metadata_json": _relative(SOURCE_METADATA_JSON),
        "digitization_qa_overlay": _relative(QA_OVERLAY),
        "model_csv": _relative(MODEL_CSV),
        "plotted_csv": _relative(PLOTTED_CSV),
        "score_json": _relative(SCORE_JSON),
        "summary_json": _relative(SUMMARY_JSON),
        "png": _relative(PNG),
        "svg": _relative(SVG),
        "sidecar": _relative(SIDECAR),
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
    source_rows = _load_source_rows()
    mixture = _mixture()
    model_rows = _solve_series(mixture, source_rows, "bubble_line") + _solve_series(mixture, source_rows, "dew_line")
    score_payload = _score(source_rows, model_rows)
    receipt = _native_receipt()
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
        ],
    )
    _write_plotted_csv(source_rows, model_rows)
    _write_json(SCORE_JSON, score_payload)
    _write_plot(source_rows, model_rows, score_payload)
    summary = {
        "figure_id": FIGURE_ID,
        "status": "accepted" if score_payload["pass"] else "blocked",
        "artifacts": {
            "source_csv": SOURCE_CSV,
            "source_metadata_json": SOURCE_METADATA_JSON,
            "digitization_qa_overlay": QA_OVERLAY,
            "model_csv": MODEL_CSV,
            "plotted_csv": PLOTTED_CSV,
            "score_json": SCORE_JSON,
            "summary_json": SUMMARY_JSON,
            "png": PNG,
            "svg": SVG,
            "sidecar": SIDECAR,
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
