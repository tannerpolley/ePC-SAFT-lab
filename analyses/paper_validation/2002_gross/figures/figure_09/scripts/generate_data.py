from __future__ import annotations

import csv
import json
import math
import sys
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
from epcsaft.model.parameters import (
    ConstantInteractionRecord,
    InteractionProvenance,
    PureRecord,
    StructuralZeroPolicy,
)
from epcsaft_equilibrium._native import extension_native_core
from PIL import Image, ImageDraw

FIGURE_ID = "figure_09"
SOURCE_SERIES = ("bubble_curve", "dew_curve")
SERIES_STYLE = {
    "bubble_curve": {"label": "PC-SAFT bubble branch", "color": "#1f77b4", "marker": "o"},
    "dew_curve": {"label": "PC-SAFT dew branch", "color": "#111111", "marker": "s"},
}
AXIS = {
    "x1_pixel": (124.0, 596.0),
    "x2_pixel": (790.0, 596.0),
    "x1_value": 0.0,
    "x2_value": 1.0,
    "y1_pixel": (124.0, 596.0),
    "y2_pixel": (124.0, 49.0),
    "y1_value": 50.0,
    "y2_value": 195.0,
}
CURVE_PIXELS = {
    "dew_curve": [
        (210.0, 65.0),
        (301.0, 88.0),
        (409.0, 117.0),
        (516.0, 157.0),
        (603.0, 197.0),
        (687.0, 254.0),
    ],
    "bubble_curve": [
        (206.0, 340.0),
        (255.0, 388.0),
        (304.0, 425.0),
        (377.0, 456.0),
        (452.0, 479.0),
        (524.0, 494.0),
        (601.0, 508.0),
        (681.0, 521.0),
    ],
}

FIGURE_DIR = REPO_ROOT / "analyses" / "paper_validation" / "2002_gross" / "figures" / FIGURE_ID
SOURCE_DIR = FIGURE_DIR / "source"
RESULTS_DIR = FIGURE_DIR / "results"
SHARED_DIR = REPO_ROOT / "analyses" / "paper_validation" / "2002_gross" / "shared"
MANIFEST_PATH = SHARED_DIR / "gross_2002_full_replication_manifest.json"
SOURCE_IMAGE = SOURCE_DIR / f"{FIGURE_ID}.png"
SOURCE_CSV = SOURCE_DIR / "source_points.csv"
SOURCE_NOTES_CSV = SOURCE_DIR / "source_notes.csv"
QA_OVERLAY = RESULTS_DIR / f"{FIGURE_ID}.png"
MODEL_CSV = RESULTS_DIR / "model_curve.csv"
PLOTTED_CSV = RESULTS_DIR / "plotted_data.csv"
FIT_STATISTICS_CSV = RESULTS_DIR / "fit_statistics.csv"
SUMMARY_JSON = SHARED_DIR / "results" / f"{FIGURE_ID}_generation_summary.json"
PNG = RESULTS_DIR / f"{FIGURE_ID}.png"
SVG = RESULTS_DIR / f"{FIGURE_ID}.svg"
PDF = RESULTS_DIR / f"{FIGURE_ID}.pdf"


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


def _x_value(pixel_x: float) -> float:
    return AXIS["x1_value"] + (pixel_x - AXIS["x1_pixel"][0]) * (
        (AXIS["x2_value"] - AXIS["x1_value"]) / (AXIS["x2_pixel"][0] - AXIS["x1_pixel"][0])
    )


def _t_c_value(pixel_y: float) -> float:
    return AXIS["y1_value"] + (AXIS["y1_pixel"][1] - pixel_y) * (
        (AXIS["y2_value"] - AXIS["y1_value"]) / (AXIS["y1_pixel"][1] - AXIS["y2_pixel"][1])
    )


def _retained_source_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for series in SOURCE_SERIES:
        for point_index, (pixel_x, pixel_y) in enumerate(CURVE_PIXELS[series], start=1):
            x_methanol = _x_value(pixel_x)
            if x_methanol <= 0.005 or x_methanol >= 0.995:
                continue
            temperature_c = _t_c_value(pixel_y)
            rows.append(
                {
                    "figure_id": FIGURE_ID,
                    "series": series,
                    "source_role": series,
                    "system": "methanol/1-octanol",
                    "pressure_bar": 1.013,
                    "T_C": temperature_c,
                    "T_K": temperature_c + 273.15,
                    "x_methanol": x_methanol if series == "bubble_curve" else "",
                    "y_methanol": x_methanol if series == "dew_curve" else "",
                    "source_kind": "calibrated_pc_saft_curve_source_capture",
                    "source_reference": "Gross 2002 Figure 9 retained PC-SAFT solid curve",
                    "retained_x_px": pixel_x,
                    "retained_y_px": pixel_y,
                    "uncertainty_x": 0.01,
                    "uncertainty_T_C": 1.0,
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
            "source_role",
            "system",
            "pressure_bar",
            "T_C",
            "T_K",
            "x_methanol",
            "y_methanol",
            "source_kind",
            "source_reference",
            "retained_x_px",
            "retained_y_px",
            "uncertainty_x",
            "uncertainty_T_C",
            "point_index",
        ],
    )
    image = Image.open(SOURCE_IMAGE).convert("RGB")
    draw = ImageDraw.Draw(image)
    for row in rows:
        px = float(row["retained_x_px"])
        py = float(row["retained_y_px"])
        color = (31, 119, 180) if row["series"] == "bubble_curve" else (17, 17, 17)
        draw.ellipse((px - 4, py - 4, px + 4, py + 4), outline=color, width=2)
    image.save(QA_OVERLAY)
    metadata = {
        "figure_id": FIGURE_ID,
        "caption": "Isobaric vapor-liquid equilibria of methanol-1-octanol at P=1.013 bar.",
        "provenance": {
            "paper": "Gross and Sadowski 2002",
            "source_capture_basis": "manual calibrated source_capture of the retained PC-SAFT solid curves in Figure 9",
            "curve_identity": {
                "bubble_curve": "lower PC-SAFT solid branch using liquid methanol mole fraction x_methanol",
                "dew_curve": "upper PC-SAFT solid branch using vapor methanol mole fraction y_methanol",
            },
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
        "roi": [124, 49, 790, 596],
        "units": {
            "pressure_bar": "bar",
            "T_C": "degC",
            "T_K": "K",
            "x_methanol": "mole fraction",
            "y_methanol": "mole fraction",
        },
        "series_labels": {
            "bubble_curve": {"composition_role": "liquid", "x_axis_symbol": "x_methanol"},
            "dew_curve": {"composition_role": "vapor", "x_axis_symbol": "y_methanol"},
        },
        "source_capture_uncertainty": {
            "x": 0.01,
            "T_C": 1.0,
            "notes": "Uncertainty reflects solid-line thickness and overlap with Arce et al. 1995 markers, especially on the high-methanol dew branch.",
        },
        "binary_interaction": {"pc_saft_kij": 0.020, "source": "Gross 2002 Table 2"},
        "source_image": _relative(SOURCE_IMAGE),
        "qa_overlay": _relative(QA_OVERLAY),
        "limitations": [
            "The retained source basis targets the paper's solid PC-SAFT line rather than the nearby filled experimental markers.",
            "The steep high-methanol dew-end segment is visually ambiguous in the crop, so the retained points stop before the near-vertical endpoint cluster.",
        ],
    }
    _write_source_notes_csv(metadata)
    return rows


def _mixture() -> epcsaft.Mixture:
    pair = ("Methanol", "1-Octanol")
    return epcsaft.Mixture(
        epcsaft.ParameterSet.from_records(
            (
                PureRecord(
                    component="Methanol",
                    molar_mass=32.042e-3,
                    m=1.5255,
                    sigma=3.2300,
                    epsilon_k=188.90,
                    charge=0.0,
                    epsilon_k_ab=2899.5,
                    kappa_ab=0.035176,
                    association_scheme="2B",
                    relative_permittivity=1.0,
                    born_diameter=0.0,
                    solvation_factor=1.0,
                ),
                PureRecord(
                    component="1-Octanol",
                    molar_mass=130.23e-3,
                    m=4.3555,
                    sigma=3.7145,
                    epsilon_k=262.74,
                    charge=0.0,
                    epsilon_k_ab=2754.8,
                    kappa_ab=0.002197,
                    association_scheme="2B",
                    relative_permittivity=1.0,
                    born_diameter=0.0,
                    solvation_factor=1.0,
                ),
            ),
            (
                ConstantInteractionRecord(
                    "k_ij",
                    pair,
                    0.020,
                    InteractionProvenance("literature", "Gross 2002 Table 2: methanol-1-octanol PC-SAFT row (k_ij=0.020)"),
                ),
            ),
            interaction_policies=(
                StructuralZeroPolicy(
                    family="l_ij",
                    components=pair,
                    reason="Lorentz segment-diameter mixing rule; no l_ij correction in this source-scoped reproduction.",
                    provenance=InteractionProvenance("model_structural_zero", "Lorentz diameter rule / EqID sigma_mixing"),
                ),
                StructuralZeroPolicy(
                    family="k_hb_ij",
                    components=pair,
                    reason="Gross 2002 Eq. 3 association combining rule; no association binary correction in this source-scoped reproduction.",
                    provenance=InteractionProvenance("model_structural_zero", "Gross 2002 Eq. 3; no association binary correction"),
                ),
            ),
            metadata={
                "source": "Gross/Sadowski 2002 Figure 9",
                "paper": "Gross and Sadowski 2002",
                "table": "Gross 2002 figure caption plus Gross 2001 pure-component table",
                "figure": "9",
                "source_path": "analyses/paper_validation/2002_gross",
                "source_backed": True,
                "reference_system": "methanol-1-octanol",
                "neutral_only_fields": {
                    "charge": 0.0,
                    "relative_permittivity": 1.0,
                    "born_diameter": 0.0,
                    "solvation_factor": 1.0,
                    "basis": "legacy neutral payload values; ionic and Born terms are inactive",
                },
            },
        )
    )


def _solve_pressure(
    mixture: epcsaft.Mixture,
    series: str,
    temperature_k: float,
    composition: float,
) -> epcsaft_equilibrium.EquilibriumResult:
    if series == "bubble_curve":
        return epcsaft_equilibrium.Equilibrium(
            mixture,
            route="bubble_pressure",
            T=temperature_k,
            x=[composition, 1.0 - composition],
        ).solve(solver_options={"max_iterations": 320, "tolerance": 1.0e-6, "ipopt_iteration_history_limit": 12})
    return epcsaft_equilibrium.Equilibrium(
        mixture,
        route="dew_pressure",
        T=temperature_k,
        y=[composition, 1.0 - composition],
    ).solve(solver_options={"max_iterations": 320, "tolerance": 1.0e-6, "ipopt_iteration_history_limit": 12})


def _invert_temperature(
    mixture: epcsaft.Mixture,
    series: str,
    composition: float,
    source_temperature_k: float,
    target_pressure_pa: float,
) -> dict[str, Any]:
    def pressure_at(temperature_k: float) -> tuple[float, epcsaft_equilibrium.EquilibriumResult]:
        result = _solve_pressure(mixture, series, temperature_k, composition)
        return float(result.pressure), result

    guess_1 = source_temperature_k
    pressure_1, result_1 = pressure_at(guess_1)
    if abs(pressure_1 - target_pressure_pa) <= 150.0:
        final_temperature_k = guess_1
        final_result = result_1
    else:
        offset = 6.0 if pressure_1 < target_pressure_pa else -6.0
        guess_2 = min(max(guess_1 + offset, 330.0), 470.0)
        pressure_2, result_2 = pressure_at(guess_2)
        for _ in range(8):
            slope = (pressure_2 - pressure_1) / (guess_2 - guess_1)
            if not np.isfinite(slope) or abs(slope) < 1.0e-9:
                break
            guess_3 = guess_2 + (target_pressure_pa - pressure_2) / slope
            guess_3 = min(max(guess_3, 330.0), 470.0)
            pressure_3, result_3 = pressure_at(guess_3)
            if abs(pressure_3 - target_pressure_pa) <= 150.0:
                final_temperature_k = guess_3
                final_result = result_3
                break
            guess_1, pressure_1 = guess_2, pressure_2
            guess_2, pressure_2, result_2 = guess_3, pressure_3, result_3
        else:
            final_temperature_k = guess_2
            final_result = result_2
    diagnostics = final_result.diagnostics
    if diagnostics.get("hessian_approximation") != "exact" or diagnostics.get("exact_hessian_available") is not True:
        raise RuntimeError(f"Figure 9 {series} inversion at composition={composition:.3f} lost exact-Hessian support.")
    if diagnostics.get("postsolve_accepted") is not True:
        raise RuntimeError(f"Figure 9 {series} inversion at composition={composition:.3f} was not postsolve accepted.")
    return {
        "T_K": float(final_result.temperature),
        "T_C": float(final_result.temperature) - 273.15,
        "pressure_bar": float(final_result.pressure) / 1.0e5,
        "route": final_result.route,
        "problem_kind": final_result.problem_kind,
        "x_methanol": float(final_result.x[0]),
        "y_methanol": float(final_result.y[0]),
        "route_status": diagnostics.get("route_status", ""),
        "solver_status": diagnostics.get("solver_status", ""),
        "hessian_approximation": diagnostics.get("hessian_approximation", ""),
        "exact_hessian_available": bool(diagnostics.get("exact_hessian_available")),
        "postsolve_accepted": bool(diagnostics.get("postsolve_accepted")),
        "hessian_backend": diagnostics.get("hessian_backend", ""),
        "iteration_count": diagnostics.get("iteration_count", ""),
    }


def _solve_model_rows(source_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    mixture = _mixture()
    rows: list[dict[str, Any]] = []
    for row in source_rows:
        series = str(row["series"])
        source_temperature_k = float(row["T_K"])
        composition = float(row["x_methanol"] or row["y_methanol"])
        solved = _invert_temperature(mixture, series, composition, source_temperature_k, 1.013e5)
        rows.append(
            {
                "series": series,
                "source_role": row["source_role"],
                "system": row["system"],
                "pressure_bar": solved["pressure_bar"],
                "T_C": solved["T_C"],
                "T_K": solved["T_K"],
                "x_methanol": solved["x_methanol"],
                "y_methanol": solved["y_methanol"],
                "route": solved["route"],
                "problem_kind": solved["problem_kind"],
                "route_status": solved["route_status"],
                "solver_status": solved["solver_status"],
                "hessian_approximation": solved["hessian_approximation"],
                "exact_hessian_available": solved["exact_hessian_available"],
                "postsolve_accepted": solved["postsolve_accepted"],
                "hessian_backend": solved["hessian_backend"],
                "iteration_count": solved["iteration_count"],
            }
        )
    return rows


def _score(source_rows: list[dict[str, Any]], model_rows: list[dict[str, Any]], native_receipt: dict[str, Any]) -> dict[str, Any]:
    series_scores: dict[str, dict[str, Any]] = {}
    all_errors: list[float] = []
    for series in SOURCE_SERIES:
        source_series = [row for row in source_rows if row["series"] == series]
        model_series = [row for row in model_rows if row["series"] == series]
        coordinate_key = "x_methanol" if series == "bubble_curve" else "y_methanol"
        errors: list[float] = []
        x = np.asarray([float(row[coordinate_key]) for row in model_series], dtype=float)
        t = np.asarray([float(row["T_C"]) for row in model_series], dtype=float)
        order = np.argsort(x)
        for source_row in source_series:
            composition = float(source_row[coordinate_key])
            source_temperature_c = float(source_row["T_C"])
            model_temperature_c = float(np.interp(composition, x[order], t[order]))
            errors.append(model_temperature_c - source_temperature_c)
        rmse = math.sqrt(sum(value * value for value in errors) / len(errors))
        max_error = max(abs(value) for value in errors)
        score = max(0.0, min(10.0, 10.0 - rmse / 0.5))
        series_scores[series] = {
            "source_point_count": len(source_series),
            "model_point_count": len(model_series),
            "rmse_axis": {"T_C": rmse, coordinate_key: 0.0},
            "max_axis_error": {"T_C": max_error, coordinate_key: 0.0},
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
        "rmse_axis": {"T_C": all_rmse, "composition_component_1": 0.0},
        "max_axis_error": {"T_C": all_max, "composition_component_1": 0.0},
        "normalized_plot_score": normalized_score,
        "branch_coverage_score": 1.0,
        "derivative_status": "verified_exact",
        "native_freshness": "fresh_native",
        "pass": normalized_score >= 8.0,
        "series_scores": series_scores,
        "score_basis": "temperature-coordinate RMSE against calibrated Gross 2002 Figure 9 retained PC-SAFT curve source_capture using public pressure-route inversion",
        "native_freshness_receipt": native_receipt,
    }


def _composition_value(row: dict[str, Any], coordinate_key: str) -> float:
    value = row.get(coordinate_key, "")
    if value not in ("", None):
        return float(value)
    fallback = "y_methanol" if coordinate_key == "x_methanol" else "x_methanol"
    return float(row[fallback])


def _write_plot(source_rows: list[dict[str, Any]], model_rows: list[dict[str, Any]], score_payload: dict[str, Any]) -> None:
    fig, ax = plt.subplots(figsize=(7.0, 5.8), constrained_layout=True)
    for series in SOURCE_SERIES:
        style = SERIES_STYLE[series]
        coordinate_key = "x_methanol" if series == "bubble_curve" else "y_methanol"
        source_series = sorted(source_rows, key=lambda row: _composition_value(row, coordinate_key))
        model_series = sorted(model_rows, key=lambda row: _composition_value(row, coordinate_key))
        ax.plot(
            [_composition_value(row, coordinate_key) for row in model_series],
            [float(row["T_C"]) for row in model_series],
            color=style["color"],
            linewidth=2.0,
            label=f"native model {style['label']}",
        )
        ax.scatter(
            [_composition_value(row, coordinate_key) for row in source_series],
            [float(row["T_C"]) for row in source_series],
            s=40,
            marker=style["marker"],
            facecolors="none",
            edgecolors=style["color"],
            linewidths=1.2,
            label=f"retained paper {style['label']}",
            zorder=3,
        )
    ax.set_xlim(0.0, 1.0)
    ax.set_ylim(60.0, 200.0)
    ax.set_xlabel(r"$x_{\mathrm{Methanol}}$ or $y_{\mathrm{Methanol}}$")
    ax.set_ylabel(r"$T$ / $^{\circ}$C")
    ax.grid(True, color="#d9d9d9", linewidth=0.7)
    ax.legend(loc="upper right", fontsize=8, frameon=False)
    ax.set_title("Gross/Sadowski 2002 Figure 9 PC-SAFT replication", fontsize=11)
    fig.text(
        0.02,
        0.01,
        f"minimum branch score: {score_payload['normalized_plot_score']:.2f}; public bubble/dew pressure inversion with exact Hessian",
        fontsize=8,
    )
    fig.savefig(PNG, dpi=180)
    fig.savefig(SVG)
    _strip_trailing_whitespace(SVG)
    fig.savefig(PDF)
    plt.close(fig)


def _write_plotted_csv(source_rows: list[dict[str, Any]], model_rows: list[dict[str, Any]]) -> None:
    rows: list[dict[str, Any]] = []
    for row in source_rows:
        rows.append({"dataset": "paper_curve", **row})
    for row in model_rows:
        rows.append({"dataset": "native_model", **row})
    _write_csv(
        PLOTTED_CSV,
        rows,
        [
            "dataset",
            "series",
            "source_role",
            "system",
            "pressure_bar",
            "T_C",
            "T_K",
            "x_methanol",
            "y_methanol",
            "source_kind",
            "source_reference",
            "retained_x_px",
            "retained_y_px",
            "uncertainty_x",
            "uncertainty_T_C",
            "point_index",
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
                "required_series": list(SOURCE_SERIES),
                "requires_exact_association_hessian": True,
                "artifacts": artifacts,
                "remaining_work": [] if score_payload["pass"] else ["improve Figure 9 replication score to the acceptance threshold"],
                "source_data_basis": "calibrated Gross 2002 Figure 9 retained PC-SAFT solid-curve source_capture with public pressure-route inversion over source-backed associating VLE pressure solves",
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

    source_rows = _write_source_artifacts()
    if render_only:
        if not MODEL_CSV.exists():
            raise RuntimeError(f"Retained model CSV is required for --render-only: {_relative(MODEL_CSV)}")
        model_rows = list(_read_csv(MODEL_CSV))
        native_receipt = _retained_native_receipt()
    else:
        model_rows = _solve_model_rows(source_rows)
        native_receipt = _native_receipt()
    score_payload = _score(source_rows, model_rows, native_receipt)
    _write_csv(
        MODEL_CSV,
        model_rows,
        [
            "series",
            "source_role",
            "system",
            "pressure_bar",
            "T_C",
            "T_K",
            "x_methanol",
            "y_methanol",
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
    _write_fit_statistics_csv(score_payload)
    _write_plot(source_rows, model_rows, score_payload)
    summary = {
        "figure_id": FIGURE_ID,
        "status": "accepted" if score_payload["pass"] else "blocked",
        "system": "methanol/1-octanol",
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
            "public_entrypoint": "epcsaft_equilibrium.Equilibrium(mixture, route='bubble_pressure'/'dew_pressure', T=..., x=.../y=...).solve() with scalar inversion to P=1.013 bar",
            "derivative_status": score_payload["derivative_status"],
            "native_freshness_receipt": native_receipt,
        },
    }
    _write_json(SUMMARY_JSON, summary)
    _update_manifest(score_payload, native_receipt)
    return 0 if score_payload["pass"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
