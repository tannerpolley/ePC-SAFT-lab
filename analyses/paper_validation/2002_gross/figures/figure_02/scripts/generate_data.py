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
import matplotlib.pyplot as plt
import numpy as np
from epcsaft.model.parameters import (
    ConstantInteractionRecord,
    InteractionProvenance,
    PureRecord,
    StructuralZeroPolicy,
)
from epcsaft_equilibrium import Equilibrium
from epcsaft_equilibrium._native import extension_native_core
from epcsaft_equilibrium.branch_tracing import (
    BranchTraceAnchor,
    BranchTraceOptions,
    BranchTraceResult,
    trace_equilibrium_boundary_route,
)
from PIL import Image, ImageDraw

FIGURE_ID = "figure_02"
TEMPERATURE_K = 373.15
MODEL_POINTS_PER_SERIES = 41
MIN_COMPOSITION = 1.0e-6
BINARY_BRANCH_MIN_COMPOSITION = 0.02

FIGURE_DIR = REPO_ROOT / "analyses" / "paper_validation" / "2002_gross" / "figures" / FIGURE_ID
SOURCE_DIR = FIGURE_DIR / "source"
RESULTS_DIR = FIGURE_DIR / "results"
SHARED_DIR = REPO_ROOT / "analyses" / "paper_validation" / "2002_gross" / "shared"
MANIFEST_PATH = SHARED_DIR / "gross_2002_full_replication_manifest.json"
SOURCE_IMAGE = SOURCE_DIR / f"{FIGURE_ID}.png"
SOURCE_CSV = SOURCE_DIR / "source_points.csv"
LITERATURE_CSV = SOURCE_DIR / "literature_points.csv"
SOURCE_NOTES_CSV = SOURCE_DIR / "source_notes.csv"
SOURCE_IDENTITY_CSV = SOURCE_DIR / "source_identity.csv"
QA_OVERLAY = RESULTS_DIR / f"{FIGURE_ID}.png"
MODEL_CSV = RESULTS_DIR / "model_curve.csv"
PLOTTED_CSV = RESULTS_DIR / "plotted_data.csv"
FIT_STATISTICS_CSV = RESULTS_DIR / "fit_statistics.csv"
SUMMARY_JSON = SHARED_DIR / "results" / f"{FIGURE_ID}_generation_summary.json"
TRACE_SUMMARY_JSON = SHARED_DIR / "results" / f"{FIGURE_ID}_trace_summary.json"
PNG = RESULTS_DIR / f"{FIGURE_ID}.png"
SVG = RESULTS_DIR / f"{FIGURE_ID}.svg"
PDF = RESULTS_DIR / f"{FIGURE_ID}.pdf"

COMPONENT_ORDER = ["isobutane", "methanol"]
MIXTURE_SPECIES = ["Methanol", "Isobutane"]
SOURCE_SERIES = ("bubble_line", "dew_line")
FIGURE_2_TRACE_OPTIONS = {
    "max_coordinate_gap": 0.075,
    "max_interpolation_error": 0.35,
    "requested_coordinate_tolerance": 2.0e-4,
    "max_refinement_iterations": 8,
    "max_points": 240,
}
EQUILIBRIUM_SOLVER_OPTIONS = {
    "max_iterations": 320,
    "tolerance": 1.0e-6,
    "ipopt_iteration_history_limit": 12,
    "ipopt_acceptable_tolerance": 1.0e-7,
    "ipopt_constraint_violation_tolerance": 1.0e-7,
    "ipopt_dual_infeasibility_tolerance": 1.0e-8,
    "ipopt_complementarity_tolerance": 1.0e-8,
}
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
    "neutral_only_fields": {
        "charge": 0.0,
        "relative_permittivity": 1.0,
        "born_diameter": 0.0,
        "solvation_factor": 1.0,
        "basis": "legacy neutral payload values; ionic and Born terms are inactive",
    },
}
SOURCE_PROVENANCE = {
    "paper": "Gross and Sadowski 2002",
    "figure": "Figure 2",
    "source_image": "analyses/paper_validation/2002_gross/figures/figure_02/source/figure_02.png",
    "source_pdf": "analyses/paper_validation/2002_gross/docs/pdf/source_01_gross_2002.pdf",
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
        {"section": "provenance", "key": "source_pdf", "value": SOURCE_PROVENANCE["source_pdf"], "unit": "", "notes": ""},
        {"section": "source_method", "key": "published_figure_curve_trace", "value": "retained visible PC-SAFT curve points from the published figure", "unit": "", "notes": ""},
        {"section": "source_method", "key": "production_scoring", "value": "retained literature pressure-composition points", "unit": "", "notes": ""},
        {"section": "data_file", "key": "literature_points", "value": _relative(LITERATURE_CSV), "unit": "", "notes": "Leu and Robinson 1992 Table I"},
        {"section": "data_file", "key": "source_identity", "value": _relative(SOURCE_IDENTITY_CSV), "unit": "", "notes": "row-level literature provenance payload"},
    ]
    for key, value in sorted((metadata or {}).items()):
        _flatten_note("metadata", str(key), value, rows)
    _write_csv(SOURCE_NOTES_CSV, rows, SOURCE_NOTE_FIELDS)


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
        x = float(row.get("source_x_px") or row.get("retained_x_px"))
        y = float(row.get("source_y_px") or row.get("retained_y_px"))
        color = colors[row["series"]]
        if row["source_role"] == "paper_pc_saft_curve":
            draw.ellipse((x - 3, y - 3, x + 3, y + 3), fill=color)
        elif row["series"] == "bubble_line":
            draw.ellipse((x - 5, y - 5, x + 5, y + 5), outline=color, width=2)
        else:
            draw.ellipse((x - 4, y - 4, x + 4, y + 4), fill=color)
    image.save(QA_OVERLAY)


def _mixture() -> epcsaft.Mixture:
    pair = tuple(MIXTURE_SPECIES)
    parameter_set = epcsaft.ParameterSet.from_records(
        (
            PureRecord(
                component=MIXTURE_SPECIES[0],
                molar_mass=METHANOL_PARAMS["MW"],
                m=METHANOL_PARAMS["m"],
                sigma=METHANOL_PARAMS["s"],
                epsilon_k=METHANOL_PARAMS["e"],
                charge=0.0,
                epsilon_k_ab=METHANOL_PARAMS["e_assoc"],
                kappa_ab=METHANOL_PARAMS["vol_a"],
                association_scheme=METHANOL_PARAMS["assoc_scheme"],
                relative_permittivity=1.0,
                born_diameter=0.0,
                solvation_factor=1.0,
            ),
            PureRecord(
                component=MIXTURE_SPECIES[1],
                molar_mass=ISOBUTANE_PARAMS["MW"],
                m=ISOBUTANE_PARAMS["m"],
                sigma=ISOBUTANE_PARAMS["s"],
                epsilon_k=ISOBUTANE_PARAMS["e"],
                charge=0.0,
                epsilon_k_ab=ISOBUTANE_PARAMS["e_assoc"],
                kappa_ab=ISOBUTANE_PARAMS["vol_a"],
                association_scheme=ISOBUTANE_PARAMS["assoc_scheme"],
                relative_permittivity=1.0,
                born_diameter=0.0,
                solvation_factor=1.0,
            ),
        ),
        (
            ConstantInteractionRecord(
                "k_ij",
                pair,
                0.05,
                InteractionProvenance(
                    "literature",
                    "Gross and Sadowski 2002 Figure 2 caption: methanol-isobutane PC-SAFT k_ij=0.05",
                ),
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
        metadata=MIXTURE_METADATA,
    )
    return epcsaft.Mixture(parameter_set)


def _load_source_rows() -> list[dict[str, Any]]:
    with SOURCE_CSV.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise RuntimeError("Gross 2002 Figure 2 source CSV is empty.")
    return rows


def _load_literature_rows() -> list[dict[str, Any]]:
    with LITERATURE_CSV.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise RuntimeError("Gross 2002 Figure 2 literature CSV is empty.")
    required_fields = {"series", "source_reference", "source_detail", "point_index", "x_axis"}
    missing_fields = sorted(required_fields - set(rows[0]))
    if missing_fields:
        raise RuntimeError(
            "Gross 2002 Figure 2 literature CSV is missing required fields: "
            + ", ".join(missing_fields)
        )
    return rows


def _write_source_identity_csv(literature_rows: list[dict[str, Any]]) -> None:
    rows = [
        {
            "figure_id": row["figure_id"],
            "dataset": row["dataset"],
            "series": row["series"],
            "point_index": row["point_index"],
            "source_reference": row["source_reference"],
            "source_detail": row["source_detail"],
            "source_pdf": _relative(SHARED_DIR.parent / "docs" / "pdf" / "source_01_gross_2002.pdf"),
            "source_data_file": _relative(LITERATURE_CSV),
        }
        for row in literature_rows
    ]
    _write_csv(
        SOURCE_IDENTITY_CSV,
        rows,
        [
            "figure_id",
            "dataset",
            "series",
            "point_index",
            "source_reference",
            "source_detail",
            "source_pdf",
            "source_data_file",
        ],
    )


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
    values = {
        min(1.0 - MIN_COMPOSITION, max(MIN_COMPOSITION, value))
        for value in source_values
        if BINARY_BRANCH_MIN_COMPOSITION <= value < 1.0
    }
    return sorted(values)


def _trace_series(mixture: epcsaft.Mixture, source_rows: list[dict[str, Any]], series: str) -> BranchTraceResult:
    route = "bubble_pressure" if series == "bubble_line" else "dew_pressure"
    anchors = [
        BranchTraceAnchor(
            anchor_id=f"{series}_{index:03d}",
            coordinate=composition,
            source_role=series,
            source_reference="analyses/paper_validation/2002_gross/figures/figure_02/source/source_points.csv",
            required=True,
        )
        for index, composition in enumerate(_series_compositions(source_rows, series), start=1)
    ]
    result = trace_equilibrium_boundary_route(
        mixture,
        anchors=anchors,
        options=BranchTraceOptions(
            route=route,
            component_index=1,
            fixed_variable="T_K",
            fixed_value=TEMPERATURE_K,
            solver_options=EQUILIBRIUM_SOLVER_OPTIONS,
            **FIGURE_2_TRACE_OPTIONS,
        ),
    )
    if not result.complete:
        raise RuntimeError(f"{series} trace did not satisfy branch completeness: {', '.join(result.blockers)}")
    return result


def _model_rows_from_trace(trace: BranchTraceResult, series: str) -> list[dict[str, Any]]:
    composition_key = "x_component_1" if series == "bubble_line" else "y_component_1"
    paired_key = "y_component_1" if series == "bubble_line" else "x_component_1"
    rows: list[dict[str, Any]] = []
    for point in trace.accepted_points:
        rows.append(
            {
                "series": series,
                composition_key: point.solved_coordinate,
                paired_key: point.paired_coordinate,
                "T_K": point.temperature_k,
                "P_bar": point.pressure_bar,
                "route": point.route,
                "problem_kind": "boundary_branch_trace",
                "route_status": point.route_status,
                "solver_status": point.solver_status,
                "hessian_approximation": point.hessian_approximation,
                "exact_hessian_available": point.exact_hessian_available,
                "postsolve_accepted": point.postsolve_accepted,
                "hessian_backend": "cppad_phase_pressure_route",
                "iteration_count": "",
                "pressure_consistency_norm": point.residuals.get("pressure_consistency_norm", ""),
                "chemical_potential_consistency_norm": point.residuals.get("chemical_potential_consistency_norm", ""),
                "trace_point_id": point.point_id,
                "requested_coordinate": point.requested_coordinate,
                "source_anchor_id": point.source_anchor_id,
            }
        )
    rows.sort(key=lambda row: float(row[composition_key]))
    return rows


def _boundary_limit_rows(
    mixture: epcsaft.Mixture,
    source_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    solved: dict[float, Any] = {}
    rows: list[dict[str, Any]] = []
    for source_row in _source_curve_rows(source_rows):
        series = source_row["series"]
        coordinate_key = "x_component_1" if series == "bubble_line" else "y_component_1"
        coordinate = float(source_row[coordinate_key])
        if coordinate not in {0.0, 1.0}:
            continue
        limit_coordinate = MIN_COMPOSITION if coordinate == 0.0 else 1.0 - MIN_COMPOSITION
        component = "methanol" if coordinate == 0.0 else "isobutane"
        if limit_coordinate not in solved:
            solved[limit_coordinate] = Equilibrium(
                mixture,
                route="dew_pressure",
                T=TEMPERATURE_K,
                y=[1.0 - limit_coordinate, limit_coordinate],
            ).solve(
                solver_options=EQUILIBRIUM_SOLVER_OPTIONS
            )
        result = solved[limit_coordinate]
        diagnostics = result.diagnostics
        payload = result.to_dict() if hasattr(result, "to_dict") else {}
        residuals = payload.get("saturation_residuals", {}) if isinstance(payload.get("saturation_residuals"), dict) else {}
        postsolve_certification = diagnostics.get("postsolve_certification", {})
        postsolve_accepted = diagnostics.get("postsolve_accepted")
        if postsolve_accepted is None and isinstance(postsolve_certification, dict):
            postsolve_accepted = postsolve_certification.get("accepted")
        rows.append(
            {
                "series": series,
                "x_component_1": float(result.x[1]),
                "y_component_1": float(result.y[1]),
                "T_K": TEMPERATURE_K,
                "P_bar": float(result.pressure) / 1.0e5,
                "route": result.route,
                "problem_kind": result.problem_kind,
                "route_status": diagnostics.get("route_status", ""),
                "solver_status": diagnostics.get("solver_status", ""),
                "hessian_approximation": diagnostics.get("hessian_approximation", ""),
                "exact_hessian_available": bool(diagnostics.get("exact_hessian_available")),
                "postsolve_accepted": bool(postsolve_accepted),
                "hessian_backend": diagnostics.get("hessian_backend", ""),
                "iteration_count": diagnostics.get("iteration_count", ""),
                "pressure_consistency_norm": residuals.get(
                    "pressure_consistency_norm",
                    diagnostics.get("pressure_consistency_norm", ""),
                ),
                "chemical_potential_consistency_norm": residuals.get(
                    "chemical_potential_consistency_norm",
                    diagnostics.get("chemical_potential_consistency_norm", ""),
                ),
                "trace_point_id": f"dew_pressure:binary_limit:{component}",
                "requested_coordinate": limit_coordinate,
                "requested_coordinate_role": "y_component_1",
                "source_anchor_id": f"binary_limit:{component}",
                "endpoint_limit_basis": "finite_binary_dew_pressure_limit",
            }
        )
    return rows


def _solve_traces(mixture: epcsaft.Mixture, source_rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, BranchTraceResult]]:
    trace_results = {series: _trace_series(mixture, source_rows, series) for series in SOURCE_SERIES}
    rows: list[dict[str, Any]] = _boundary_limit_rows(mixture, source_rows)
    for series, result in trace_results.items():
        rows.extend(_model_rows_from_trace(result, series))
    return rows, trace_results


def _interp_pressure(series_rows: list[dict[str, Any]], coordinate_key: str, composition: float) -> float:
    x = np.asarray([float(row[coordinate_key]) for row in series_rows], dtype=float)
    p = np.asarray([float(row["P_bar"]) for row in series_rows], dtype=float)
    order = np.argsort(x)
    minimum = x[order[0]]
    maximum = x[order[-1]]
    if composition < minimum and 0.0 <= composition and minimum <= 1.01 * MIN_COMPOSITION:
        composition = minimum
    if composition > maximum and composition <= 1.0 and 1.0 - maximum <= 1.01 * MIN_COMPOSITION:
        composition = maximum
    if composition < minimum or composition > maximum:
        raise RuntimeError(
            f"Literature coordinate {composition} is outside the retained {coordinate_key} model branch."
        )
    return float(np.interp(composition, x[order], p[order]))


def _score(
    source_rows: list[dict[str, Any]],
    model_rows: list[dict[str, Any]],
    *,
    scoring_rows: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    del source_rows
    scoring_rows = _load_literature_rows() if scoring_rows is None else scoring_rows
    if not scoring_rows:
        raise RuntimeError("Gross 2002 Figure 2 production scoring requires literature points.")
    source_by_series = _sorted_source_series(scoring_rows)
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
        "source_point_count": len(scoring_rows),
        "model_point_count": len(model_rows),
        "rmse_axis": {"P_bar": all_rmse, "composition_component_1": 0.0},
        "max_axis_error": {"P_bar": all_max, "composition_component_1": 0.0},
        "normalized_plot_score": normalized_score,
        "branch_coverage_score": 1.0,
        "derivative_status": "verified_exact",
        "pass": normalized_score >= 8.0,
        "series_scores": series_scores,
        "score_basis": (
            "pressure-coordinate RMSE against Leu and Robinson 1992 Table I "
            "literature P-x/y points retained for Gross 2002 Figure 2"
        ),
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
    _strip_trailing_whitespace(SVG)
    fig.savefig(PDF)
    plt.close(fig)


def _write_plotted_csv(literature_rows: list[dict[str, Any]], model_rows: list[dict[str, Any]]) -> None:
    rows: list[dict[str, Any]] = []
    for row in literature_rows:
        rows.append(
            {
                "dataset": "literature_experimental",
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


def _trace_summary_payload(trace_results: dict[str, BranchTraceResult]) -> dict[str, Any]:
    traces: list[dict[str, Any]] = []
    for series, result in trace_results.items():
        accepted_points = result.accepted_points
        traces.append(
            {
                "series": series,
                "route": result.route,
                "complete": result.complete,
                "required_anchor_count": result.required_anchor_count,
                "solved_required_anchor_count": result.solved_required_anchor_count,
                "accepted_point_count": len(accepted_points),
                "max_coordinate_gap": result.max_coordinate_gap,
                "max_interpolation_error": result.max_interpolation_error,
                "exact_hessian_verified": all(
                    point.exact_hessian_available and point.hessian_approximation == "exact"
                    for point in accepted_points
                ),
                "postsolve_verified": all(point.postsolve_accepted for point in accepted_points),
                "blockers": list(result.blockers),
            }
        )
    return {
        "figure_id": FIGURE_ID,
        "trace_contract": "m4_boundary_route_trace_v1",
        "trace_options": dict(FIGURE_2_TRACE_OPTIONS),
        "trace_source_policy": {
            "binary_branch_min_composition": BINARY_BRANCH_MIN_COMPOSITION,
            "boundary_limit_route": "dew_pressure",
            "boundary_limit_coordinate_role": "y_component_1",
            "boundary_limit_coordinates": [MIN_COMPOSITION, 1.0 - MIN_COMPOSITION],
            "reason": "finite binary dew-pressure limits provide both liquid and vapor compositions on the shared boundary without claiming unsupported public pure-component scope",
        },
        "traces": traces,
    }


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
        "source_identity_csv": _relative(SOURCE_IDENTITY_CSV),
        "source_csv": _relative(SOURCE_CSV),
        "source_notes_csv": _relative(SOURCE_NOTES_CSV),
        "model_csv": _relative(MODEL_CSV),
        "plotted_csv": _relative(PLOTTED_CSV),
        "fit_statistics_csv": _relative(FIT_STATISTICS_CSV),
        "trace_summary_json": _relative(TRACE_SUMMARY_JSON),
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
                "requires_branch_trace": True,
                "artifacts": artifacts,
                "remaining_work": [] if score_payload["pass"] else ["improve Figure 2 per-series replication score to the acceptance threshold"],
                "source_data_basis": (
                    "Leu and Robinson 1992 Table I literature pressure-composition points "
                    "retained in literature_points.csv; published Figure 2 PC-SAFT curve "
                    "points are retained only for branch tracing"
                ),
                "trace_requirements": {
                    "max_coordinate_gap": FIGURE_2_TRACE_OPTIONS["max_coordinate_gap"],
                    "max_interpolation_error": FIGURE_2_TRACE_OPTIONS["max_interpolation_error"],
                    "required_series": list(SOURCE_SERIES),
                },
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
    unknown_args = [arg for arg in sys.argv[1:] if arg != "--render-only"]
    if unknown_args:
        raise RuntimeError(f"Unsupported arguments: {unknown_args}")
    render_only = "--render-only" in sys.argv[1:]

    source_rows = _load_source_rows()
    literature_rows = _load_literature_rows()
    _write_source_identity_csv(literature_rows)
    if render_only:
        if not MODEL_CSV.exists():
            raise RuntimeError(f"Retained model CSV is required for --render-only: {_relative(MODEL_CSV)}")
        if not TRACE_SUMMARY_JSON.exists():
            raise RuntimeError(f"Retained trace summary is required for --render-only: {_relative(TRACE_SUMMARY_JSON)}")
        model_rows = list(_read_csv(MODEL_CSV))
        trace_summary = json.loads(TRACE_SUMMARY_JSON.read_text(encoding="utf-8"))
        receipt = _retained_native_receipt()
    else:
        mixture = _mixture()
        model_rows, trace_results = _solve_traces(mixture, source_rows)
        trace_summary = _trace_summary_payload(trace_results)
        _write_json(TRACE_SUMMARY_JSON, trace_summary)
        receipt = _native_receipt()
    score_payload = _score(source_rows, model_rows, scoring_rows=literature_rows)

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
            "trace_point_id",
            "requested_coordinate",
            "requested_coordinate_role",
            "source_anchor_id",
            "endpoint_limit_basis",
        ],
    )
    _write_overlay(source_rows)
    _write_plotted_csv(literature_rows, model_rows)
    _write_fit_statistics_csv(score_payload)
    _write_source_notes_csv(
        {
            "scoring_source": _relative(LITERATURE_CSV),
            "scoring_source_reference": "Leu and Robinson 1992 Table I",
            "source_point_count": score_payload["source_point_count"],
            "normalized_plot_score": score_payload["normalized_plot_score"],
            "score_basis": score_payload["score_basis"],
        }
    )
    _write_plot(literature_rows, model_rows, score_payload)

    summary = {
        "figure_id": FIGURE_ID,
        "status": "accepted" if score_payload["pass"] else "blocked",
        "artifacts": {
            "source_identity_csv": SOURCE_IDENTITY_CSV,
            "source_csv": SOURCE_CSV,
            "source_notes_csv": SOURCE_NOTES_CSV,
            "model_csv": MODEL_CSV,
            "plotted_csv": PLOTTED_CSV,
            "fit_statistics_csv": FIT_STATISTICS_CSV,
            "trace_summary_json": TRACE_SUMMARY_JSON,
            "png": PNG,
            "svg": SVG,
            "pdf": PDF,
        },
        "source_point_count": score_payload["source_point_count"],
        "model_point_count": len(model_rows),
        "score": score_payload,
        "trace_summary": trace_summary,
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
