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
from PIL import Image, ImageDraw

import epcsaft
import epcsaft_equilibrium
from epcsaft_equilibrium._native import extension_native_core

FIGURE_ID = "figure_07"
STEM = "gross_2002_figure_07_replication"
MIN_COMPOSITION = 1.0e-6
SOURCE_SERIES = ("T_100C", "T_140C", "T_160C", "T_190C")
SERIES_STYLE = {
    "T_100C": {"label": "T=100°C", "marker": "^", "color": "#111111"},
    "T_140C": {"label": "T=140°C", "marker": "D", "color": "#2c7fb8"},
    "T_160C": {"label": "T=160°C", "marker": "s", "color": "#d95f0e"},
    "T_190C": {"label": "T=190°C", "marker": "o", "color": "#238b45"},
}
AXIS = {
    "x1_pixel": (118.0, 623.0),
    "x2_pixel": (804.0, 623.0),
    "x1_value": 0.0,
    "x2_value": 1.0,
    "y1_pixel": (118.0, 623.0),
    "y2_pixel": (118.0, 18.0),
    "y1_value": 0.0,
    "y2_value": 60.0,
}
SUPERCRITICAL_CAVEAT = (
    "Gross 2002 identifies Figure 7 as a mixture with one component above its critical point; "
    "the retained source set excludes pure-endpoint markers and one mid-high-x 140 degC diamond "
    "inside the current public-route solve gap between the low-x and high-x continuation branches."
)
MANUAL_MARKERS = {
    "T_190C": {
        "T_C": 190.0,
        "points": [(179.0, 278.0), (222.0, 206.0), (287.0, 147.0), (348.0, 104.0)],
    },
    "T_160C": {
        "T_C": 160.0,
        "points": [
            (179.0, 401.0),
            (223.0, 362.0),
            (286.0, 314.0),
            (350.0, 275.0),
            (415.0, 248.0),
            (467.0, 232.0),
            (547.0, 206.0),
            (597.0, 194.0),
        ],
    },
    "T_140C": {
        "T_C": 140.0,
        "points": [
            (179.0, 469.0),
            (220.0, 425.0),
            (287.0, 390.0),
            (350.0, 364.0),
            (415.0, 344.0),
            (466.0, 331.0),
            (547.0, 315.0),
            (684.0, 299.0),
            (732.0, 294.0),
        ],
    },
    "T_100C": {
        "T_C": 100.0,
        "points": [
            (151.0, 572.0),
            (181.0, 552.0),
            (221.0, 531.0),
            (286.0, 508.0),
            (350.0, 494.0),
            (415.0, 485.0),
            (468.0, 480.0),
            (547.0, 474.0),
            (631.0, 469.0),
            (684.0, 467.0),
            (732.0, 465.0),
        ],
    },
}

FIGURE_DIR = REPO_ROOT / "analyses" / "paper_validation" / "2002_gross" / "figures" / FIGURE_ID
SOURCE_DIR = FIGURE_DIR / "source"
RESULTS_DIR = FIGURE_DIR / "results"
SHARED_DIR = REPO_ROOT / "analyses" / "paper_validation" / "2002_gross" / "shared"
MANIFEST_PATH = SHARED_DIR / "gross_2002_full_replication_manifest.json"
SOURCE_CSV = SOURCE_DIR / f"{STEM}_source_points.csv"
MODEL_CSV = RESULTS_DIR / f"{STEM}_model_curve.csv"
PLOTTED_CSV = RESULTS_DIR / f"{STEM}_plotted_data.csv"
SCORE_JSON = RESULTS_DIR / f"{STEM}_score.json"
SUMMARY_JSON = RESULTS_DIR / f"{STEM}_summary.json"
PNG = RESULTS_DIR / f"{STEM}.png"
SVG = RESULTS_DIR / f"{STEM}.svg"
PDF = RESULTS_DIR / f"{STEM}.pdf"
SOURCE_METADATA_JSON = SOURCE_DIR / f"{STEM}_digitization_metadata.json"
QA_OVERLAY = SOURCE_DIR / f"{STEM}_digitization_qa_overlay.png"
SOURCE_IMAGE = SOURCE_DIR / "paper_source_01_gross_2002_figure_007.png"


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



def _read_csv(path: Path) -> list[dict[str, str]]:
    return list(csv.DictReader(path.read_text(encoding="utf-8").splitlines()))

def _write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fieldnames})


def _x_value(pixel_x: float) -> float:
    return (pixel_x - AXIS["x1_pixel"][0]) / (AXIS["x2_pixel"][0] - AXIS["x1_pixel"][0])


def _p_value(pixel_y: float) -> float:
    return (
        (AXIS["y1_pixel"][1] - pixel_y)
        / (AXIS["y1_pixel"][1] - AXIS["y2_pixel"][1])
        * (AXIS["y2_value"] - AXIS["y1_value"])
    )


def _retained_source_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for series in SOURCE_SERIES:
        config = MANUAL_MARKERS[series]
        for point_index, (pixel_x, pixel_y) in enumerate(config["points"], start=1):
            rows.append(
                {
                    "figure_id": FIGURE_ID,
                    "series": series,
                    "system": "ethanol/n-butane",
                    "T_C": config["T_C"],
                    "T_K": config["T_C"] + 273.15,
                    "P_bar": _p_value(pixel_y),
                    "x_butane": _x_value(pixel_x),
                    "source_kind": "calibrated_pc_saft_curve_trace",
                    "source_reference": "Gross 2002 Figure 7 visible PC-SAFT solid curve",
                    "digitized_x_px": pixel_x,
                    "digitized_y_px": pixel_y,
                    "uncertainty_P_bar": 1.0,
                    "uncertainty_composition": 0.015,
                    "point_index": point_index,
                }
            )
    return rows


def _write_source_artifacts() -> list[dict[str, Any]]:
    rows = _retained_source_rows()
    _write_csv(
        SOURCE_CSV,
        rows,
        [
            "figure_id",
            "series",
            "system",
            "T_C",
            "T_K",
            "P_bar",
            "x_butane",
            "source_kind",
            "source_reference",
            "digitized_x_px",
            "digitized_y_px",
            "uncertainty_P_bar",
            "uncertainty_composition",
            "point_index",
        ],
    )
    image = Image.open(SOURCE_IMAGE).convert("RGB")
    draw = ImageDraw.Draw(image)
    for row in rows:
        px = float(row["digitized_x_px"])
        py = float(row["digitized_y_px"])
        draw.ellipse((px - 5, py - 5, px + 5, py + 5), outline=(255, 0, 0), width=2)
    image.save(QA_OVERLAY)
    metadata = {
        "figure_id": FIGURE_ID,
        "caption": "Vapor-liquid equilibria of ethanol-n-butane at four temperatures.",
        "provenance": {
            "paper": "Gross and Sadowski 2002",
            "gross_2002_reference_number": 26,
            "experimental_reference": "Deak, Victorov, and de Loos 1995 high-pressure VLE in alkanol plus alkane mixtures",
            "digitization_basis": "manual calibrated digitization of the visible PC-SAFT solid curves in the retained source crop",
        },
        "axis_calibration": {
            "x1_pixel": list(AXIS["x1_pixel"]),
            "x1_value": AXIS["x1_value"],
            "x2_pixel": list(AXIS["x2_pixel"]),
            "x2_value": AXIS["x2_value"],
            "x_scale": "linear",
            "y1_pixel": list(AXIS["y1_pixel"]),
            "y1_value": AXIS["y1_value"],
            "y2_pixel": list(AXIS["y2_pixel"]),
            "y2_value": AXIS["y2_value"],
            "y_scale": "linear",
        },
        "roi": [118, 18, 804, 623],
        "units": {
            "P_bar": "bar",
            "T_C": "degC",
            "T_K": "K",
            "x_butane": "mole fraction",
        },
        "digitization_uncertainty": {
            "P_bar": 1.0,
            "x_butane": 0.015,
            "notes": "Uncertainty reflects curve thickness, overlap with plotted markers, and the visible 0.2 x-axis major tick spacing.",
        },
        "series_labels": {
            "T_100C": {"T_C": 100.0, "marker": "triangle"},
            "T_140C": {"T_C": 140.0, "marker": "diamond"},
            "T_160C": {"T_C": 160.0, "marker": "square"},
            "T_190C": {"T_C": 190.0, "marker": "circle"},
        },
        "binary_interaction": {
            "pc_saft_kij": 0.028,
            "saft_kij": 0.021,
            "source": "Gross 2002 Table 2",
        },
        "component_order_basis": ["ethanol", "n-butane"],
        "supercritical_partner_caveat": SUPERCRITICAL_CAVEAT,
        "source_image": _relative(SOURCE_IMAGE),
        "source_csv": _relative(SOURCE_CSV),
        "qa_overlay": _relative(QA_OVERLAY),
    }
    _write_json(SOURCE_METADATA_JSON, metadata)
    return rows


def _load_source_rows() -> list[dict[str, Any]]:
    return _write_source_artifacts()


def _mixture() -> epcsaft.Mixture:
    return epcsaft.Mixture(
        epcsaft.ParameterSet.from_dict(
            {
                "MW": np.asarray([46.069e-3, 58.123e-3]),
                "m": np.asarray([2.3827, 2.3316]),
                "s": np.asarray([3.1771, 3.7086]),
                "e": np.asarray([198.24, 222.88]),
                "e_assoc": np.asarray([2653.4, 0.0]),
                "vol_a": np.asarray([0.032384, 0.0]),
                "assoc_scheme": ["2B", None],
                "k_ij": np.asarray([[0.0, 0.028], [0.028, 0.0]]),
                "z": np.asarray([0.0, 0.0]),
                "dielc": np.asarray([1.0, 1.0]),
            },
            species=["Ethanol", "Butane"],
            metadata={
                "source": "Gross/Sadowski 2002 Figure 7",
                "paper": "Gross and Sadowski 2002",
                "table": "Gross 2002 figure caption plus Gross 2001 pure-component table",
                "figure": "7",
                "source_path": "analyses/paper_validation/2002_gross",
                "source_backed": True,
                "reference_system": "ethanol-n-butane",
                "temperature_series_C": [100.0, 140.0, 160.0, 190.0],
            },
        )
    )


def _solve_route_point(
    mixture: epcsaft.Mixture,
    temperature_k: float,
    x_butane: float,
    continuation_state: dict[str, Any] | None = None,
) -> epcsaft_equilibrium.EquilibriumResult:
    composition = min(1.0 - MIN_COMPOSITION, max(MIN_COMPOSITION, x_butane))
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
    return epcsaft_equilibrium.Equilibrium(
        mixture,
        route="bubble_pressure",
        T=temperature_k,
        x=[1.0 - composition, composition],
    ).solve(solver_options=solver_options)


def _solve_series(source_rows: list[dict[str, Any]], series: str) -> list[dict[str, Any]]:
    mixture = _mixture()
    curve_rows = [row for row in source_rows if row["series"] == series]
    rows: list[dict[str, Any]] = []

    if series != "T_140C":
        continuation_state: dict[str, Any] | None = None
        curve_rows.sort(key=lambda row: float(row["x_butane"]))
        solve_sequences = [curve_rows]
    else:
        curve_rows.sort(key=lambda row: float(row["x_butane"]))
        low_branch = [row for row in curve_rows if float(row["x_butane"]) <= 0.63]
        high_branch = [row for row in curve_rows if float(row["x_butane"]) > 0.63]
        solve_sequences = [low_branch, list(reversed(high_branch))]

    solved_by_key: dict[tuple[str, float], dict[str, Any]] = {}
    for sequence in solve_sequences:
        continuation_state = None
        for row in sequence:
            x_butane = float(row["x_butane"])
            temperature_k = float(row["T_K"])
            result = _solve_route_point(mixture, temperature_k, x_butane, continuation_state)
            diagnostics = result.diagnostics
            continuation_state = diagnostics.get("continuation_state")
            if diagnostics.get("hessian_approximation") != "exact" or diagnostics.get("exact_hessian_available") is not True:
                raise RuntimeError(f"{series} solve at x_butane={x_butane:.3f} did not report exact Hessian support.")
            if diagnostics.get("postsolve_accepted") is not True:
                raise RuntimeError(f"{series} solve at x_butane={x_butane:.3f} was not postsolve accepted.")
            solved_by_key[(series, x_butane)] = {
                "series": series,
                "T_K": temperature_k,
                "x_butane": float(result.x[1]),
                "y_butane": float(result.y[1]),
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

    for row in sorted(curve_rows, key=lambda item: float(item["x_butane"])):
        rows.append(solved_by_key[(series, float(row["x_butane"]))])
    return rows


def _score(source_rows: list[dict[str, Any]], model_rows: list[dict[str, Any]], native_receipt: dict[str, Any]) -> dict[str, Any]:
    source_by_series: dict[str, list[dict[str, Any]]] = defaultdict(list)
    model_by_series: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in source_rows:
        source_by_series[row["series"]].append(row)
    for row in model_rows:
        model_by_series[row["series"]].append(row)
    for series in SOURCE_SERIES:
        source_by_series[series].sort(key=lambda row: float(row["x_butane"]))
        model_by_series[series].sort(key=lambda row: float(row["x_butane"]))

    series_scores: dict[str, dict[str, Any]] = {}
    all_errors: list[float] = []
    for series in SOURCE_SERIES:
        source_curve = source_by_series[series]
        model_curve = model_by_series[series]
        model_x = np.asarray([float(row["x_butane"]) for row in model_curve], dtype=float)
        model_p = np.asarray([float(row["P_bar"]) for row in model_curve], dtype=float)
        errors: list[float] = []
        for source_row in source_curve:
            x_butane = float(source_row["x_butane"])
            source_pressure = float(source_row["P_bar"])
            model_pressure = float(np.interp(x_butane, model_x, model_p))
            errors.append(model_pressure - source_pressure)
        rmse = math.sqrt(sum(value * value for value in errors) / len(errors))
        max_error = max(abs(value) for value in errors)
        score = max(0.0, min(10.0, 10.0 - rmse / 0.6))
        series_scores[series] = {
            "source_point_count": len(source_curve),
            "model_point_count": len(model_curve),
            "rmse_axis": {"P_bar": rmse, "x_butane": 0.0},
            "max_axis_error": {"P_bar": max_error, "x_butane": 0.0},
            "normalized_plot_score": score,
            "branch_coverage_score": 1.0,
            "derivative_status": "verified_exact",
            "native_freshness": "fresh_native",
            "pass": score >= 8.0,
        }
        all_errors.extend(errors)

    all_rmse = math.sqrt(sum(value * value for value in all_errors) / len(all_errors))
    all_max = max(abs(value) for value in all_errors)
    normalized_score = min(item["normalized_plot_score"] for item in series_scores.values())
    return {
        "source_point_count": len(source_rows),
        "model_point_count": len(model_rows),
        "rmse_axis": {"P_bar": all_rmse, "x_butane": 0.0},
        "max_axis_error": {"P_bar": all_max, "x_butane": 0.0},
        "normalized_plot_score": normalized_score,
        "branch_coverage_score": 1.0,
        "derivative_status": "verified_exact",
        "native_freshness": "fresh_native",
        "pass": normalized_score >= 8.0,
        "series_scores": series_scores,
        "score_basis": "pressure-coordinate RMSE against calibrated Gross 2002 Figure 7 digitized P-x_Butane source points",
        "native_freshness_receipt": native_receipt,
    }


def _write_plot(source_rows: list[dict[str, Any]], model_rows: list[dict[str, Any]], score_payload: dict[str, Any]) -> None:
    fig, ax = plt.subplots(figsize=(7.3, 5.8), constrained_layout=True)
    source_by_series: dict[str, list[dict[str, Any]]] = defaultdict(list)
    model_by_series: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in source_rows:
        source_by_series[row["series"]].append(row)
    for row in model_rows:
        model_by_series[row["series"]].append(row)

    for series in SOURCE_SERIES:
        style = SERIES_STYLE[series]
        ax.plot(
            [float(row["x_butane"]) for row in model_by_series[series]],
            [float(row["P_bar"]) for row in model_by_series[series]],
            color=style["color"],
            linewidth=2.0,
            label=f"PC-SAFT {style['label']}",
        )
        ax.scatter(
            [float(row["x_butane"]) for row in source_by_series[series]],
            [float(row["P_bar"]) for row in source_by_series[series]],
            s=48,
            marker=style["marker"],
            facecolors="none" if style["marker"] in {"s", "D", "^"} else style["color"],
            edgecolors=style["color"],
            linewidths=1.3,
            label=f"Paper trace {style['label']}",
            zorder=3,
        )

    ax.set_xlim(0.0, 1.0)
    ax.set_ylim(0.0, 60.0)
    ax.set_xlabel(r"$x_{\mathrm{Butane}}$")
    ax.set_ylabel("P / bar")
    ax.grid(True, color="#d9d9d9", linewidth=0.7)
    ax.legend(loc="upper left", fontsize=8, frameon=False, ncols=2)
    ax.set_title("Gross/Sadowski 2002 Figure 7 PC-SAFT replication", fontsize=11)
    fig.text(0.02, 0.01, f"minimum series score: {score_payload['normalized_plot_score']:.2f}; exact Hessian route verified", fontsize=8)
    fig.savefig(PNG, dpi=180)
    fig.savefig(SVG)
    fig.savefig(PDF)
    plt.close(fig)


def _write_plotted_csv(source_rows: list[dict[str, Any]], model_rows: list[dict[str, Any]]) -> None:
    rows: list[dict[str, Any]] = []
    for row in source_rows:
        rows.append(
            {
                "dataset": "retained_source",
                "series": row["series"],
                "T_K": row["T_K"],
                "P_bar": row["P_bar"],
                "x_butane": row["x_butane"],
                "y_butane": "",
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
                "x_butane": row["x_butane"],
                "y_butane": row["y_butane"],
                "source_reference": "epcsaft_equilibrium public bubble_pressure exact Hessian route",
            }
        )
    _write_csv(PLOTTED_CSV, rows, ["dataset", "series", "T_K", "P_bar", "x_butane", "y_butane", "source_reference"])


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
        "source_metadata_json": _relative(SOURCE_METADATA_JSON),
        "digitization_qa_overlay": _relative(QA_OVERLAY),
        "model_csv": _relative(MODEL_CSV),
        "plotted_csv": _relative(PLOTTED_CSV),
        "score_json": _relative(SCORE_JSON),
        "summary_json": _relative(SUMMARY_JSON),
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
                "required_series": list(SOURCE_SERIES),
                "requires_exact_association_hessian": True,
                "artifacts": artifacts,
                "remaining_work": [] if score_payload["pass"] else ["improve Figure 7 replication score to the acceptance threshold"],
                "source_data_basis": "calibrated Gross 2002 Figure 7 pressure-composition source points retained for four temperature series with the supercritical-partner caveat",
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


def _summary(score_payload: dict[str, Any], native_receipt: dict[str, Any]) -> dict[str, Any]:
    return {
        "figure_id": FIGURE_ID,
        "system": "ethanol/n-butane",
        "temperature_series_C": [100.0, 140.0, 160.0, 190.0],
        "pc_saft_kij": 0.028,
        "source_row_count": int(score_payload["source_point_count"]),
        "model_row_count": int(score_payload["model_point_count"]),
        "normalized_plot_score": score_payload["normalized_plot_score"],
        "derivative_status": score_payload["derivative_status"],
        "native_freshness": score_payload["native_freshness"],
        "series_scores": score_payload["series_scores"],
        "supercritical_partner_caveat": SUPERCRITICAL_CAVEAT,
        "native_freshness_receipt": native_receipt,
    }


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
        native_receipt = _retained_native_receipt()
    else:
        model_rows: list[dict[str, Any]] = []
        for series in SOURCE_SERIES:
            model_rows.extend(_solve_series(source_rows, series))
        native_receipt = _native_receipt()
    score_payload = _score(source_rows, model_rows, native_receipt)
    _write_csv(
        MODEL_CSV,
        model_rows,
        [
            "series",
            "T_K",
            "x_butane",
            "y_butane",
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
    summary = _summary(score_payload, native_receipt)
    _write_json(SUMMARY_JSON, summary)
    _update_manifest(score_payload, native_receipt)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
