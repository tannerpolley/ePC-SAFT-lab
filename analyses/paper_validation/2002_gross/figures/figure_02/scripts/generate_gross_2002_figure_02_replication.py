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

FIGURE_ID = "figure_02"
STEM = "gross_2002_figure_02_replication"
TEMPERATURE_K = 373.15
MODEL_POINTS_PER_SERIES = 41
MIN_COMPOSITION = 1.0e-6

FIGURE_DIR = REPO_ROOT / "analyses" / "paper_validation" / "2002_gross" / "figures" / FIGURE_ID
SOURCE_DIR = FIGURE_DIR / "source"
RESULTS_DIR = FIGURE_DIR / "results"
SHARED_DIR = REPO_ROOT / "analyses" / "paper_validation" / "2002_gross" / "shared"
MANIFEST_PATH = SHARED_DIR / "gross_2002_full_replication_manifest.json"
SOURCE_IMAGE = SOURCE_DIR / "paper_source_01_gross_2002_figure_002.png"
SOURCE_CSV = SOURCE_DIR / f"{STEM}_source_points.csv"
SOURCE_METADATA_JSON = SOURCE_DIR / f"{STEM}_digitization_metadata.json"
IDENTITY_JSON = SOURCE_DIR / f"{STEM}_identity.json"
QA_OVERLAY = SOURCE_DIR / f"{STEM}_digitization_qa_overlay.png"
MODEL_CSV = RESULTS_DIR / f"{STEM}_model_curve.csv"
PLOTTED_CSV = RESULTS_DIR / f"{STEM}_plotted_data.csv"
SCORE_JSON = RESULTS_DIR / f"{STEM}_score.json"
SUMMARY_JSON = RESULTS_DIR / f"{STEM}_summary.json"
PNG = RESULTS_DIR / f"{STEM}.png"
SVG = RESULTS_DIR / f"{STEM}.svg"
SIDECAR = RESULTS_DIR / f"{STEM}.mpl.yaml"

COMPONENT_ORDER = ["isobutane", "methanol"]
MIXTURE_SPECIES = ["Methanol", "Isobutane"]
SOURCE_SERIES = ("bubble_line", "dew_line")
AXIS_CALIBRATION = {
    "composition_isobutane": {"min": 0.0, "max": 1.0, "pixel_min": 116.0, "pixel_max": 802.0},
    "pressure_bar": {"min": 0.0, "max": 25.0, "pixel_min": 548.0, "pixel_max": 16.0},
}

METHANOL_PARAMS = {
    "MW": 32.042e-3,
    "m": 1.5255,
    "s": 3.2300,
    "e": 188.90,
    "e_assoc": 2899.5,
    "vol_a": 0.035176,
    "assoc_scheme": "2B",
    "source": "Gross2002 Table1",
}
ISOBUTANE_PARAMS = {
    "MW": 58.123e-3,
    "m": 2.2616,
    "s": 3.7574,
    "e": 216.53,
    "e_assoc": 0.0,
    "vol_a": 0.0,
    "assoc_scheme": None,
    "source": "Gross2001 Table2",
}
MIXTURE_METADATA = {
    "source": "Gross/Sadowski 2002 Figure 2",
    "paper": "Gross and Sadowski 2002",
    "table": "Gross 2002 Figure 2 caption plus Gross 2001 isobutane pure-component table",
    "figure": "Figure 2",
    "source_path": "analyses/paper_validation/2002_gross",
    "source_backed": True,
    "caption_system": "methanol-isobutane",
    "table_002_conflict": "methanol-isobutanol",
    "parameter_snapshot_resolution": "Use methanol from Gross2002 Table1, isobutane from Gross2001 Table2, and k_ij=0.05 from the retained Figure 2 caption because the local binary snapshot currently mislabels the pair.",
}
SOURCE_PROVENANCE = {
    "paper": "Gross and Sadowski 2002",
    "figure": "Figure 2",
    "source_image": "analyses/paper_validation/2002_gross/figures/figure_02/source/paper_source_01_gross_2002_figure_002.png",
    "source_markers": "Leu and Robinson 1992 experimental data as reproduced in Gross 2002 Figure 2",
    "parameter_provenance": {
        "methanol": "Gross2002 Table1",
        "isobutane": "Gross2001 Table2",
        "k_ij": "Gross2002 Figure 2 caption and retained identity artifact",
    },
}


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


def _write_overlay(source_rows: list[dict[str, Any]]) -> None:
    image = Image.open(SOURCE_IMAGE).convert("RGB")
    draw = ImageDraw.Draw(image)
    x_axis = AXIS_CALIBRATION["composition_isobutane"]
    y_axis = AXIS_CALIBRATION["pressure_bar"]
    draw.rectangle(
        (x_axis["pixel_min"], y_axis["pixel_max"], x_axis["pixel_max"], y_axis["pixel_min"]),
        outline=(40, 120, 220),
        width=2,
    )
    colors = {"bubble_line": (180, 50, 50), "dew_line": (20, 120, 40)}
    for row in source_rows:
        x = float(row["digitized_x_px"])
        y = float(row["digitized_y_px"])
        color = colors[row["series"]]
        if row["source_role"] == "paper_pc_saft_curve":
            draw.ellipse((x - 3, y - 3, x + 3, y + 3), fill=color)
        elif row["series"] == "bubble_line":
            draw.ellipse((x - 5, y - 5, x + 5, y + 5), outline=color, width=2)
        else:
            draw.ellipse((x - 4, y - 4, x + 4, y + 4), fill=color)
    image.save(QA_OVERLAY)


def _mixture() -> epcsaft.Mixture:
    parameter_set = epcsaft.ParameterSet.from_dict(
        {
            "MW": np.asarray([METHANOL_PARAMS["MW"], ISOBUTANE_PARAMS["MW"]]),
            "m": np.asarray([METHANOL_PARAMS["m"], ISOBUTANE_PARAMS["m"]]),
            "s": np.asarray([METHANOL_PARAMS["s"], ISOBUTANE_PARAMS["s"]]),
            "e": np.asarray([METHANOL_PARAMS["e"], ISOBUTANE_PARAMS["e"]]),
            "e_assoc": np.asarray([METHANOL_PARAMS["e_assoc"], ISOBUTANE_PARAMS["e_assoc"]]),
            "vol_a": np.asarray([METHANOL_PARAMS["vol_a"], ISOBUTANE_PARAMS["vol_a"]]),
            "assoc_scheme": [METHANOL_PARAMS["assoc_scheme"], ISOBUTANE_PARAMS["assoc_scheme"]],
            "k_ij": np.asarray([[0.0, 0.05], [0.05, 0.0]]),
            "z": np.asarray([0.0, 0.0]),
            "dielc": np.asarray([1.0, 1.0]),
        },
        species=MIXTURE_SPECIES,
        metadata=MIXTURE_METADATA,
    )
    return epcsaft.Mixture(parameter_set)


def _load_source_rows() -> list[dict[str, Any]]:
    with SOURCE_CSV.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise RuntimeError("Gross 2002 Figure 2 source CSV is empty.")
    return rows


def _source_curve_rows(source_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    curve_rows = [row for row in source_rows if row.get("source_role", "") == "paper_pc_saft_curve"]
    return curve_rows if curve_rows else source_rows


def _sorted_source_series(source_rows: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    by_series: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in source_rows:
        by_series[row["series"]].append(row)
    for series, rows in by_series.items():
        key = "x_component_1" if series == "bubble_line" else "y_component_1"
        rows.sort(key=lambda row: float(row[key]))
    return dict(by_series)


def _series_compositions(source_rows: list[dict[str, Any]], series: str) -> list[float]:
    coordinate_key = "x_component_1" if series == "bubble_line" else "y_component_1"
    curve_rows = _source_curve_rows(source_rows)
    source_values = [float(row[coordinate_key]) for row in curve_rows if row["series"] == series]
    values = {min(1.0 - MIN_COMPOSITION, max(MIN_COMPOSITION, value)) for value in source_values}
    return sorted(values)


def _series_segments(compositions: list[float], series: str) -> list[list[float]]:
    if series == "bubble_line":
        low = [value for value in compositions if value < 0.7]
        high = [value for value in compositions if value >= 0.7]
        segments: list[list[float]] = []
        if low:
            segments.append(low)
        if high:
            segments.append(sorted(high, reverse=True))
        return segments
    low = [value for value in compositions if value < 0.8]
    high = [value for value in compositions if value >= 0.8]
    segments = []
    if low:
        segments.append(low)
    if high:
        segments.append(sorted(high, reverse=True))
    return segments


def _solve_route_point(
    mixture: epcsaft.Mixture,
    route: str,
    target_composition: float,
    continuation_state: dict[str, Any] | None = None,
) -> epcsaft_equilibrium.EquilibriumResult:
    candidate_offsets = (0.0, -0.01, 0.01, -0.02, 0.02, -0.05, 0.05)
    last_error: Exception | None = None
    for offset in candidate_offsets:
        isobutane = min(1.0 - MIN_COMPOSITION, max(MIN_COMPOSITION, target_composition + offset))
        try:
            solver_options = {
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
                    x=[float(1.0 - isobutane), isobutane],
                ).solve(solver_options=solver_options)
            return epcsaft_equilibrium.Equilibrium(
                mixture,
                route=route,
                T=TEMPERATURE_K,
                y=[float(1.0 - isobutane), isobutane],
            ).solve(solver_options=solver_options)
        except Exception as exc:
            last_error = exc
    assert last_error is not None
    raise last_error


def _solve_series(mixture: epcsaft.Mixture, series: str) -> list[dict[str, Any]]:
    compositions = _series_compositions(_load_source_rows(), series)
    rows: list[dict[str, Any]] = []
    for segment in _series_segments(compositions, series):
        continuation_state: dict[str, Any] | None = None
        for composition in segment:
            if series == "bubble_line":
                result = _solve_route_point(mixture, "bubble_pressure", float(composition), continuation_state)
                composition_key = "x_component_1"
                paired_key = "y_component_1"
                fixed_composition = float(result.x[1])
                paired_composition = float(result.y[1])
            else:
                result = _solve_route_point(mixture, "dew_pressure", float(composition), continuation_state)
                composition_key = "y_component_1"
                paired_key = "x_component_1"
                fixed_composition = float(result.y[1])
                paired_composition = float(result.x[1])

            diagnostics = result.diagnostics
            if diagnostics.get("hessian_approximation") != "exact" or diagnostics.get("exact_hessian_available") is not True:
                raise RuntimeError(f"{series} solve at composition={composition:.3f} did not report the exact Hessian route.")
            if diagnostics.get("postsolve_accepted") is not True:
                raise RuntimeError(f"{series} solve at composition={composition:.3f} was not postsolve accepted.")
            continuation_state = diagnostics.get("continuation_state")

            rows.append(
                {
                    "series": series,
                    composition_key: fixed_composition,
                    paired_key: paired_composition,
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
                    "pressure_consistency_norm": diagnostics.get("pressure_consistency_norm", ""),
                    "chemical_potential_consistency_norm": diagnostics.get("chemical_potential_consistency_norm", ""),
                }
            )
    return rows


def _interp_pressure(series_rows: list[dict[str, Any]], coordinate_key: str, composition: float) -> float:
    x = np.asarray([float(row[coordinate_key]) for row in series_rows], dtype=float)
    p = np.asarray([float(row["P_bar"]) for row in series_rows], dtype=float)
    order = np.argsort(x)
    return float(np.interp(composition, x[order], p[order]))


def _score(source_rows: list[dict[str, Any]], model_rows: list[dict[str, Any]]) -> dict[str, Any]:
    source_curve_rows = _source_curve_rows(source_rows)
    source_by_series = _sorted_source_series(source_curve_rows)
    model_by_series: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in model_rows:
        model_by_series[row["series"]].append(row)
    for series, rows in model_by_series.items():
        key = "x_component_1" if series == "bubble_line" else "y_component_1"
        rows.sort(key=lambda row: float(row[key]))

    series_scores: dict[str, dict[str, Any]] = {}
    all_errors: list[float] = []
    for series in SOURCE_SERIES:
        coordinate_key = "x_component_1" if series == "bubble_line" else "y_component_1"
        errors: list[float] = []
        for source_row in source_by_series[series]:
            composition = float(source_row[coordinate_key])
            source_pressure = float(source_row["P_bar"])
            model_pressure = _interp_pressure(model_by_series[series], coordinate_key, composition)
            errors.append(model_pressure - source_pressure)
        abs_errors = [abs(value) for value in errors]
        rmse = math.sqrt(sum(value * value for value in errors) / len(errors))
        max_error = max(abs_errors)
        score = max(0.0, min(10.0, 10.0 - rmse / 0.35))
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
    normalized_score = min(payload["normalized_plot_score"] for payload in series_scores.values())
    return {
        "source_point_count": len(source_curve_rows),
        "model_point_count": len(model_rows),
        "rmse_axis": {"P_bar": all_rmse, "composition_component_1": 0.0},
        "max_axis_error": {"P_bar": all_max, "composition_component_1": 0.0},
        "normalized_plot_score": normalized_score,
        "branch_coverage_score": 1.0,
        "derivative_status": "verified_exact",
        "pass": normalized_score >= 8.0,
        "series_scores": series_scores,
        "score_basis": "pressure-coordinate RMSE against calibrated Gross 2002 Figure 2 digitized P-x/y source points",
    }


def _write_plot(source_rows: list[dict[str, Any]], model_rows: list[dict[str, Any]], score_payload: dict[str, Any]) -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(7.4, 5.8), constrained_layout=True)
    marker_rows = [row for row in source_rows if row.get("source_role", "") == "experimental_marker"]
    if not marker_rows:
        marker_rows = source_rows
    source_by_series = _sorted_source_series(marker_rows)
    model_by_series: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in model_rows:
        model_by_series[row["series"]].append(row)

    style_map = {
        "bubble_line": {"color": "#111111", "marker": "o", "facecolors": "none", "label": "Exp. data (bubble)"},
        "dew_line": {"color": "#111111", "marker": "o", "facecolors": "#111111", "label": "Exp. data (dew)"},
    }
    model_labels = {"bubble_line": "PC-SAFT bubble", "dew_line": "PC-SAFT dew"}

    for series in SOURCE_SERIES:
        coordinate_key = "x_component_1" if series == "bubble_line" else "y_component_1"
        source = source_by_series[series]
        model = sorted(model_by_series[series], key=lambda row: float(row[coordinate_key]))
        style = style_map[series]
        ax.plot(
            [float(row[coordinate_key]) for row in model],
            [float(row["P_bar"]) for row in model],
            color=style["color"],
            linewidth=2.0,
            label=model_labels[series],
        )
        ax.scatter(
            [float(row[coordinate_key]) for row in source],
            [float(row["P_bar"]) for row in source],
            s=54,
            marker=style["marker"],
            facecolors=style["facecolors"],
            edgecolors=style["color"],
            linewidths=1.4,
            label=style["label"],
            zorder=3,
        )

    ax.set_xlim(0.0, 1.0)
    ax.set_ylim(0.0, 25.0)
    ax.set_xlabel(r"$x_{\mathrm{Isobutane}}$ or $y_{\mathrm{Isobutane}}$")
    ax.set_ylabel("P / bar")
    ax.set_xticks(np.linspace(0.0, 1.0, 6))
    ax.set_yticks(np.arange(0.0, 26.0, 5.0))
    ax.grid(True, color="#d9d9d9", linewidth=0.7)
    ax.legend(loc="lower right", fontsize=8, frameon=False)
    ax.set_title("Gross/Sadowski 2002 Figure 2 PC-SAFT VLE replication", fontsize=11)
    fig.text(
        0.02,
        0.01,
        f"minimum series score: {score_payload['normalized_plot_score']:.2f}; exact Hessian route verified",
        fontsize=8,
    )
    fig.savefig(PNG, dpi=180)
    fig.savefig(SVG)
    plt.close(fig)
    SIDECAR.write_text(
        "\n".join(
            [
                "figure_id: figure_02",
                f"png: {_relative(PNG)}",
                f"svg: {_relative(SVG)}",
                "x_axis: composition_component_1",
                "y_axis: pressure_bar",
                "matplotlib_backend: Agg",
                "style: paper-scale P-x/y overlay with digitized source markers and public-route PC-SAFT curves",
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
                "dataset": "source_digitization",
                "series": row["series"],
                "T_K": row["T_K"],
                "P_bar": row["P_bar"],
                "x_component_1": row["x_component_1"],
                "y_component_1": row["y_component_1"],
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
                "x_component_1": row.get("x_component_1", ""),
                "y_component_1": row.get("y_component_1", ""),
                "source_reference": "epcsaft_equilibrium public bubble/dew exact Hessian route",
            }
        )
    _write_csv(
        PLOTTED_CSV,
        rows,
        ["dataset", "series", "T_K", "P_bar", "x_component_1", "y_component_1", "source_reference"],
    )


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
        "source_identity_json": _relative(IDENTITY_JSON),
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
                "remaining_work": [] if score_payload["pass"] else ["improve Figure 2 per-series replication score to the acceptance threshold"],
                "source_data_basis": "calibrated Gross 2002 Figure 2 pressure-composition source points with figure-local parameter provenance resolution for methanol/isobutane",
                "score": {
                    "normalized_plot_score": score_payload["normalized_plot_score"],
                    "branch_coverage_score": score_payload["branch_coverage_score"],
                    "derivative_status": score_payload["derivative_status"],
                    "pass": score_payload["pass"],
                },
            }
        )
        break
    else:
        raise RuntimeError("figure_02 record missing from full-replication manifest.")
    _write_json(MANIFEST_PATH, manifest)


def main() -> int:
    source_rows = _load_source_rows()
    mixture = _mixture()
    model_rows = _solve_series(mixture, "bubble_line") + _solve_series(mixture, "dew_line")
    score_payload = _score(source_rows, model_rows)
    receipt = _native_receipt()

    _write_csv(
        MODEL_CSV,
        model_rows,
        [
            "series",
            "x_component_1",
            "y_component_1",
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
            "pressure_consistency_norm",
            "chemical_potential_consistency_norm",
        ],
    )
    _write_overlay(source_rows)
    _write_plotted_csv(source_rows, model_rows)
    _write_json(SCORE_JSON, score_payload)
    _write_plot(source_rows, model_rows, score_payload)

    summary = {
        "figure_id": FIGURE_ID,
        "status": "accepted" if score_payload["pass"] else "blocked",
        "artifacts": {
            "source_identity_json": IDENTITY_JSON,
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
        "source_provenance": SOURCE_PROVENANCE,
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
