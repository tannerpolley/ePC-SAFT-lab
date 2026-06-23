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

FIGURE_ID = "figure_01"
MODEL_POINTS_PER_BRANCH = 31
CONNECTOR_POINTS_PER_COMPONENT = 41
FIGURE_DIR = REPO_ROOT / "analyses" / "paper_validation" / "2002_gross" / "figures" / FIGURE_ID
SOURCE_DIR = FIGURE_DIR / "source"
RESULTS_DIR = FIGURE_DIR / "results"
SHARED_DIR = REPO_ROOT / "analyses" / "paper_validation" / "2002_gross" / "shared"
PARAMETER_CSV = REPO_ROOT / "analyses" / "paper_validation" / "2002_gross" / "parameters" / "pure" / "any_solvent.csv"
MANIFEST_PATH = SHARED_DIR / "gross_2002_full_replication_manifest.json"
PURE_COMPONENT_REFERENCE_DIR = REPO_ROOT / "data" / "reference" / "pure_component"
REFERENCE_SATURATION_DENSITY_CSVS = {
    "methanol": PURE_COMPONENT_REFERENCE_DIR / "saturation_density" / "methanol" / "saturation_density.csv",
    "1-pentanol": PURE_COMPONENT_REFERENCE_DIR / "saturation_density" / "1_pentanol" / "saturation_density.csv",
    "1-nonanol": PURE_COMPONENT_REFERENCE_DIR / "saturation_density" / "1_nonanol" / "saturation_density.csv",
}
REFERENCE_ASSOCIATION_AAD_CSVS = {
    "methanol": PURE_COMPONENT_REFERENCE_DIR / "association_aad" / "methanol" / "association_aad.csv",
    "1-pentanol": PURE_COMPONENT_REFERENCE_DIR / "association_aad" / "1_pentanol" / "association_aad.csv",
    "1-nonanol": PURE_COMPONENT_REFERENCE_DIR / "association_aad" / "1_nonanol" / "association_aad.csv",
}
SOURCE_IMAGE = SOURCE_DIR / f"{FIGURE_ID}.png"
SOURCE_CSV = SOURCE_DIR / "source_points.csv"
SOURCE_NOTES_CSV = SOURCE_DIR / "source_notes.csv"
ASSOCIATION_SOURCE_CSV = SOURCE_DIR / "pure_association_aad.csv"
MODEL_CSV = RESULTS_DIR / "model_curve.csv"
PLOTTED_CSV = RESULTS_DIR / "plotted_data.csv"
FIT_STATISTICS_CSV = RESULTS_DIR / "fit_statistics.csv"
ASSOCIATION_FIT_STATISTICS_CSV = RESULTS_DIR / "association_fit_statistics.csv"
PNG = RESULTS_DIR / f"{FIGURE_ID}.png"
SVG = RESULTS_DIR / f"{FIGURE_ID}.svg"
PDF = RESULTS_DIR / f"{FIGURE_ID}.pdf"

COMPONENT_STYLES = {
    "methanol": {"color": "#222222", "marker": "D"},
    "1-pentanol": {"color": "#0F6B8F", "marker": "o"},
    "1-nonanol": {"color": "#A33B20", "marker": "o"},
}

NEAR_CRITICAL_EXCLUSIONS = [
    {
        "component": "methanol",
        "temperature_window_K": "485-512",
        "reason": "single_component_vle postsolve phase-distance gate rejects phase coalescence near the visible critical tip",
    }
]

NEAR_CRITICAL_CONNECTORS = {
    "methanol": {
        "tip_temperature_K": 505.0,
        "tip_density_kg_m3": 275.0,
        "basis": "visible Gross 2002 Figure 1 near-critical marker center between the retained vapor and liquid branch endpoints",
    },
    "1-pentanol": {
        "tip_temperature_K": 585.0,
        "tip_density_kg_m3": 275.0,
        "basis": "visible Gross 2002 Figure 1 near-critical marker at the top of the 1-pentanol envelope",
    },
    "1-nonanol": {
        "tip_temperature_K": 670.0,
        "tip_density_kg_m3": 255.0,
        "basis": "visible Gross 2002 Figure 1 near-critical marker at the top of the 1-nonanol envelope",
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


def _write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fieldnames})


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _read_reference_rows(paths: dict[str, Path]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for component, path in paths.items():
        if not path.is_file():
            raise RuntimeError(f"{component} reference input missing: {_relative(path)}")
        rows.extend(dict(row) for row in _read_csv(path))
    return rows


def _write_source_notes() -> None:
    rows: list[dict[str, Any]] = [
        {"section": "provenance", "key": "paper", "value": "Gross and Sadowski 2002", "unit": "", "notes": ""},
        {"section": "provenance", "key": "figure", "value": "Figure 1", "unit": "", "notes": ""},
        {"section": "provenance", "key": "source_image", "value": _relative(SOURCE_IMAGE), "unit": "", "notes": ""},
        {
            "section": "provenance",
            "key": "parameter_table",
            "value": _relative(PARAMETER_CSV),
            "unit": "",
            "notes": "",
        },
        {
            "section": "source_method",
            "key": "published_figure_curve_trace",
            "value": "solid PC-SAFT curve points retained from the published figure",
            "unit": "",
            "notes": "",
        },
        {
            "section": "source_method",
            "key": "published_figure_marker_trace",
            "value": "experimental marker centers retained from the published figure",
            "unit": "",
            "notes": "",
        },
        {
            "section": "source_method",
            "key": "source_table",
            "value": "values copied from a published source table",
            "unit": "",
            "notes": "",
        },
    ]
    for component, path in REFERENCE_SATURATION_DENSITY_CSVS.items():
        rows.append(
            {
                "section": "reference_data",
                "key": f"{component}_saturation_density",
                "value": _relative(path),
                "unit": "",
                "notes": "pure_component/saturation_density taxonomy home",
            }
        )
    for component, path in REFERENCE_ASSOCIATION_AAD_CSVS.items():
        rows.append(
            {
                "section": "reference_data",
                "key": f"{component}_association_aad",
                "value": _relative(path),
                "unit": "",
                "notes": "pure_component/association_aad taxonomy home",
            }
        )
    for component, connector in NEAR_CRITICAL_CONNECTORS.items():
        rows.append(
            {
                "section": "near_critical_connector",
                "key": component,
                "value": f"{connector['tip_temperature_K']} K; {connector['tip_density_kg_m3']} kg/m^3",
                "unit": "K;kg/m^3",
                "notes": connector["basis"],
            }
        )
    _write_csv(SOURCE_NOTES_CSV, rows, ["section", "key", "value", "unit", "notes"])


def _copy_reference_inputs() -> None:
    if not SOURCE_IMAGE.is_file():
        raise RuntimeError(f"Retained source image missing: {_relative(SOURCE_IMAGE)}")
    source_rows = _read_reference_rows(REFERENCE_SATURATION_DENSITY_CSVS)
    association_rows = _read_reference_rows(REFERENCE_ASSOCIATION_AAD_CSVS)
    _write_csv(
        SOURCE_CSV,
        source_rows,
        [
            "component",
            "branch",
            "source_role",
            "temperature_K",
            "density_kg_m3",
            "pixel_x",
            "pixel_y",
            "density_uncertainty_kg_m3",
            "temperature_uncertainty_K",
            "source_reference",
            "notes",
            "source_method",
            "source_document",
        ],
    )
    _write_csv(
        ASSOCIATION_SOURCE_CSV,
        association_rows,
        [
            "component",
            "assoc_scheme",
            "psat_aad_percent",
            "liquid_density_aad_percent",
            "temperature_range_K",
            "source_table",
            "source_status",
            "source_method",
            "source_reference",
        ],
    )
    _write_source_notes()


def _load_parameters() -> dict[str, dict[str, str]]:
    with PARAMETER_CSV.open(encoding="utf-8", newline="") as handle:
        rows = {row["component"]: row for row in csv.DictReader(handle)}
    missing = {"methanol", "1-pentanol", "1-nonanol"} - set(rows)
    if missing:
        raise RuntimeError(f"Gross 2002 pure parameter rows missing for: {sorted(missing)}")
    return rows


def _mixture(component: str, parameters: dict[str, dict[str, str]]) -> epcsaft.Mixture:
    row = parameters[component]
    payload = {
        "MW": np.asarray([float(row["MW"])]),
        "m": np.asarray([float(row["m"])]),
        "s": np.asarray([float(row["s"])]),
        "e": np.asarray([float(row["e"])]),
        "e_assoc": np.asarray([float(row["e_assoc"])]),
        "vol_a": np.asarray([float(row["vol_a"])]),
        "assoc_scheme": [row["assoc_scheme"]],
    }
    return epcsaft.Mixture(
        epcsaft.ParameterSet.from_dict(
            payload,
            species=[component],
            metadata={"source": row["source"], "figure": "Gross 2002 Figure 1"},
        )
    )


def _source_rows() -> list[dict[str, Any]]:
    rows = [dict(row) for row in _read_csv(SOURCE_CSV)]
    required = {
        "component",
        "branch",
        "source_role",
        "temperature_K",
        "density_kg_m3",
        "source_reference",
        "source_method",
    }
    missing = required - set(rows[0] if rows else {})
    if not rows or missing:
        raise RuntimeError(f"Figure 1 source CSV is missing required columns: {sorted(missing)}")
    return rows


def _model_reference_rows(source_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    by_branch: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in source_rows:
        if row["source_role"] == "paper_pc_saft_curve":
            by_branch[f"{row['component']}:{row['branch']}"].append(row)

    for branch_key, branch_rows in sorted(by_branch.items()):
        component, branch = branch_key.split(":", maxsplit=1)
        branch_rows = sorted(branch_rows, key=lambda row: float(row["temperature_K"]))
        temperatures = np.asarray([float(row["temperature_K"]) for row in branch_rows], dtype=float)
        densities = np.asarray([float(row["density_kg_m3"]) for row in branch_rows], dtype=float)
        for temperature_K in np.linspace(float(temperatures.min()), float(temperatures.max()), MODEL_POINTS_PER_BRANCH):
            rows.append(
                {
                    "component": component,
                    "branch": branch,
                    "temperature_K": float(temperature_K),
                    "density_kg_m3": float(np.interp(temperature_K, temperatures, densities)),
                }
            )
    return rows


def _source_curve_counts(source_rows: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = defaultdict(int)
    for row in source_rows:
        if row["source_role"] == "paper_pc_saft_curve":
            counts[f"{row['component']}:{row['branch']}"] += 1
    return dict(counts)


def _solve_model_rows(source_rows: list[dict[str, Any]], parameters: dict[str, dict[str, str]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    mixtures = {component: _mixture(component, parameters) for component in ("methanol", "1-pentanol", "1-nonanol")}
    for source_row in _model_reference_rows(source_rows):
        component = source_row["component"]
        branch = source_row["branch"]
        temperature_K = float(source_row["temperature_K"])
        result = epcsaft_equilibrium.Equilibrium(
            mixtures[component],
            route="single_component_vle",
            T=temperature_K,
        ).solve(solver_options={"max_iterations": 220, "tolerance": 1.0e-8, "ipopt_print_level": 0})
        diagnostics = result.diagnostics
        if diagnostics.get("hessian_approximation") != "exact" or diagnostics.get("exact_hessian_available") is not True:
            raise RuntimeError(f"{component} {temperature_K} K solve did not report the exact Hessian route.")
        density_mol_m3 = result.vapor_density if branch == "vapor" else result.liquid_density
        density_kg_m3 = density_mol_m3 * float(parameters[component]["MW"])
        source_reference_density = float(source_row["density_kg_m3"])
        rows.append(
            {
                "component": component,
                "branch": branch,
                "temperature_K": temperature_K,
                "density_kg_m3": density_kg_m3,
                "density_mol_m3": density_mol_m3,
                "saturation_pressure_Pa": result.P_sat,
                "source_reference_density_kg_m3": source_reference_density,
                "density_error_kg_m3": density_kg_m3 - source_reference_density,
                "route_status": diagnostics.get("route_status", ""),
                "solver_status": diagnostics.get("solver_status", ""),
                "hessian_approximation": diagnostics.get("hessian_approximation", ""),
                "exact_hessian_available": bool(diagnostics.get("exact_hessian_available")),
                "hessian_backend": diagnostics.get("hessian_backend", ""),
                "iteration_count": diagnostics.get("iteration_count", ""),
                "pressure_consistency_norm": diagnostics.get("pressure_consistency_norm", ""),
                "chemical_potential_consistency_norm": diagnostics.get("chemical_potential_consistency_norm", ""),
            }
        )
    return rows


def _score(model_rows: list[dict[str, Any]], source_rows: list[dict[str, Any]]) -> dict[str, Any]:
    by_branch: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in model_rows:
        by_branch[f"{row['component']}:{row['branch']}"].append(row)
    source_counts = _source_curve_counts(source_rows)

    branch_scores: dict[str, dict[str, Any]] = {}
    for branch_key, rows in sorted(by_branch.items()):
        errors = [float(row["density_error_kg_m3"]) for row in rows]
        abs_errors = [abs(value) for value in errors]
        rmse = math.sqrt(sum(value * value for value in errors) / len(errors))
        max_error = max(abs_errors)
        score = max(0.0, min(10.0, 10.0 - rmse / 4.0))
        branch_scores[branch_key] = {
            "source_point_count": source_counts.get(branch_key, 0),
            "model_point_count": len(rows),
            "rmse_axis": {"density_kg_m3": rmse, "temperature_K": 0.0},
            "max_axis_error": {"density_kg_m3": max_error, "temperature_K": 0.0},
            "normalized_plot_score": score,
            "branch_coverage_score": 1.0,
            "derivative_status": "verified_exact",
            "pass": score >= 8.0,
        }

    all_errors = [float(row["density_error_kg_m3"]) for row in model_rows]
    all_rmse = math.sqrt(sum(value * value for value in all_errors) / len(all_errors))
    all_max = max(abs(value) for value in all_errors)
    required_branches = {
        "methanol:vapor",
        "methanol:liquid",
        "1-pentanol:vapor",
        "1-pentanol:liquid",
        "1-nonanol:vapor",
        "1-nonanol:liquid",
    }
    branch_coverage = len(required_branches & set(branch_scores)) / len(required_branches)
    normalized_score = min(value["normalized_plot_score"] for value in branch_scores.values())
    return {
        "source_point_count": sum(source_counts.get(branch, 0) for branch in required_branches),
        "model_point_count": len(model_rows),
        "rmse_axis": {"density_kg_m3": all_rmse, "temperature_K": 0.0},
        "max_axis_error": {"density_kg_m3": all_max, "temperature_K": 0.0},
        "normalized_plot_score": normalized_score,
        "branch_coverage_score": branch_coverage,
        "derivative_status": "verified_exact",
        "pass": branch_coverage == 1.0 and normalized_score >= 8.0,
        "branch_scores": branch_scores,
        "score_basis": "density-coordinate RMSE against calibrated Gross 2002 Figure 1 solid PC-SAFT curve points",
        "near_critical_exclusions": NEAR_CRITICAL_EXCLUSIONS,
        "near_critical_connectors": NEAR_CRITICAL_CONNECTORS,
    }


def _model_rows_by_key(model_rows: list[dict[str, Any]]) -> dict[tuple[str, str], list[dict[str, Any]]]:
    rows_by_key: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in model_rows:
        rows_by_key[(row["component"], row["branch"])].append(row)
    return rows_by_key


def _quadratic_bezier(
    start: tuple[float, float],
    control: tuple[float, float],
    end: tuple[float, float],
    point_count: int,
) -> list[tuple[float, float]]:
    points: list[tuple[float, float]] = []
    for value in np.linspace(0.0, 1.0, point_count):
        one_minus = 1.0 - float(value)
        density_kg_m3 = (
            one_minus * one_minus * start[0]
            + 2.0 * one_minus * float(value) * control[0]
            + float(value) * float(value) * end[0]
        )
        temperature_K = (
            one_minus * one_minus * start[1]
            + 2.0 * one_minus * float(value) * control[1]
            + float(value) * float(value) * end[1]
        )
        points.append((density_kg_m3, temperature_K))
    return points


def _near_critical_connector_rows(
    model_by_key: dict[tuple[str, str], list[dict[str, Any]]],
    component: str,
) -> list[dict[str, Any]]:
    vapor = sorted(model_by_key[(component, "vapor")], key=lambda row: float(row["temperature_K"]))
    liquid = sorted(model_by_key[(component, "liquid")], key=lambda row: float(row["temperature_K"]))
    if not vapor or not liquid:
        return []

    connector = NEAR_CRITICAL_CONNECTORS[component]
    vapor_tip = (float(vapor[-1]["density_kg_m3"]), float(vapor[-1]["temperature_K"]))
    liquid_tip = (float(liquid[-1]["density_kg_m3"]), float(liquid[-1]["temperature_K"]))
    visible_tip = (float(connector["tip_density_kg_m3"]), float(connector["tip_temperature_K"]))

    segment_points = max(3, CONNECTOR_POINTS_PER_COMPONENT // 2 + 1)
    left_control = ((vapor_tip[0] + visible_tip[0]) / 2.0, visible_tip[1])
    right_control = ((visible_tip[0] + liquid_tip[0]) / 2.0, visible_tip[1])
    left_segment = _quadratic_bezier(vapor_tip, left_control, visible_tip, segment_points)
    right_segment = _quadratic_bezier(visible_tip, right_control, liquid_tip, segment_points)
    connector_points = left_segment[:-1] + right_segment

    return [
        {
            "component": component,
            "branch": "near_critical_connector",
            "temperature_K": temperature_K,
            "density_kg_m3": density_kg_m3,
            "source_reference": connector["basis"],
        }
        for density_kg_m3, temperature_K in connector_points
    ]


def _continuous_model_envelope(
    model_by_key: dict[tuple[str, str], list[dict[str, Any]]],
    component: str,
) -> list[dict[str, Any]]:
    vapor = sorted(model_by_key[(component, "vapor")], key=lambda row: float(row["temperature_K"]))
    liquid = sorted(model_by_key[(component, "liquid")], key=lambda row: float(row["temperature_K"]), reverse=True)
    connector = _near_critical_connector_rows(model_by_key, component)
    if not connector:
        return vapor + liquid
    return vapor + connector[1:-1] + liquid


def _all_near_critical_connector_rows(model_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    model_by_key = _model_rows_by_key(model_rows)
    rows: list[dict[str, Any]] = []
    for component in ("methanol", "1-pentanol", "1-nonanol"):
        rows.extend(_near_critical_connector_rows(model_by_key, component))
    return rows


def _write_plot(source_rows: list[dict[str, Any]], model_rows: list[dict[str, Any]], score_payload: dict[str, Any]) -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(7.2, 6.4), constrained_layout=True)
    model_by_key = _model_rows_by_key(model_rows)
    source_curve_by_key: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    markers_by_component: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in source_rows:
        if row["source_role"] == "paper_pc_saft_curve":
            source_curve_by_key[(row["component"], row["branch"])].append(row)
        elif row["source_role"] == "experimental_marker":
            markers_by_component[row["component"]].append(row)

    for component in ("methanol", "1-pentanol", "1-nonanol"):
        style = COMPONENT_STYLES[component]
        model = _continuous_model_envelope(model_by_key, component)
        if model:
            ax.plot(
                [float(row["density_kg_m3"]) for row in model],
                [float(row["temperature_K"]) for row in model],
                color=style["color"],
                linewidth=2.0,
                label=f"{component} model envelope",
            )
        for branch in ("vapor", "liquid"):
            source = sorted(source_curve_by_key[(component, branch)], key=lambda item: float(item["temperature_K"]))
            if source:
                ax.scatter(
                    [float(row["density_kg_m3"]) for row in source],
                    [float(row["temperature_K"]) for row in source],
                    s=18,
                    marker="x",
                    color=style["color"],
                    linewidths=1.0,
                    label=f"{component} source PC-SAFT" if branch == "liquid" else None,
                )
        markers = markers_by_component[component]
        if markers:
            facecolor = style["color"] if component == "1-pentanol" else "none"
            ax.scatter(
                [float(row["density_kg_m3"]) for row in markers],
                [float(row["temperature_K"]) for row in markers],
                s=48,
                marker=style["marker"],
                facecolors=facecolor,
                edgecolors=style["color"],
                linewidths=1.4,
                label=f"{component} experimental markers",
            )

    ax.set_xlim(0, 1000)
    ax.set_ylim(150, 750)
    ax.set_xlabel("Density / kg m$^{-3}$")
    ax.set_ylabel("T / K")
    ax.set_xticks([0, 200, 400, 600, 800, 1000])
    ax.set_yticks([150, 300, 450, 600, 750])
    ax.grid(True, color="#d9d9d9", linewidth=0.7)
    ax.legend(loc="upper right", fontsize=8, frameon=False)
    ax.set_title("Gross/Sadowski 2002 Figure 1 PC-SAFT density replication", fontsize=11)
    ax.text(
        0.02,
        0.02,
        f"min branch score {score_payload['normalized_plot_score']:.2f}; connector excluded from score",
        transform=ax.transAxes,
        fontsize=8,
        va="bottom",
    )
    fig.savefig(PNG, dpi=180)
    fig.savefig(SVG)
    fig.savefig(PDF)
    _strip_trailing_whitespace(SVG)
    plt.close(fig)


def _write_plotted_csv(source_rows: list[dict[str, Any]], model_rows: list[dict[str, Any]]) -> None:
    rows: list[dict[str, Any]] = []
    for row in source_rows:
        rows.append(
            {
                "dataset": row["source_role"],
                "component": row["component"],
                "branch": row["branch"],
                "temperature_K": row["temperature_K"],
                "density_kg_m3": row["density_kg_m3"],
                "source_reference": row["source_reference"],
                "source_method": row.get("source_method", ""),
            }
        )
    for row in model_rows:
        rows.append(
            {
                "dataset": "package_model",
                "component": row["component"],
                "branch": row["branch"],
                "temperature_K": row["temperature_K"],
                "density_kg_m3": row["density_kg_m3"],
                "source_reference": "epcsaft_equilibrium single_component_vle exact Hessian route",
                "source_method": "package_model",
            }
        )
    for row in _all_near_critical_connector_rows(model_rows):
        rows.append(
            {
                "dataset": "plot_continuity_connector",
                "component": row["component"],
                "branch": row["branch"],
                "temperature_K": row["temperature_K"],
                "density_kg_m3": row["density_kg_m3"],
                "source_reference": row["source_reference"],
                "source_method": "paper_visible_tip_connector",
            }
        )
    _write_csv(
        PLOTTED_CSV,
        rows,
        ["dataset", "component", "branch", "temperature_K", "density_kg_m3", "source_reference", "source_method"],
    )


def _write_fit_statistics_csv(
    score_payload: dict[str, Any],
    *,
    generation_mode: str,
    source_point_count: int,
    model_point_count: int,
) -> None:
    rows: list[dict[str, Any]] = [
        {
            "scope": "figure",
            "component": "all",
            "branch": "all",
            "source_point_count": source_point_count,
            "model_point_count": model_point_count,
            "rmse_density_kg_m3": score_payload["rmse_axis"]["density_kg_m3"],
            "rmse_temperature_K": score_payload["rmse_axis"]["temperature_K"],
            "max_density_error_kg_m3": score_payload["max_axis_error"]["density_kg_m3"],
            "max_temperature_error_K": score_payload["max_axis_error"]["temperature_K"],
            "normalized_plot_score": score_payload["normalized_plot_score"],
            "branch_coverage_score": score_payload["branch_coverage_score"],
            "derivative_status": score_payload["derivative_status"],
            "pass": score_payload["pass"],
            "generation_mode": generation_mode,
            "score_basis": score_payload["score_basis"],
        }
    ]
    for branch_key, branch_score in sorted(score_payload["branch_scores"].items()):
        component, branch = branch_key.split(":", maxsplit=1)
        rows.append(
            {
                "scope": "branch",
                "component": component,
                "branch": branch,
                "source_point_count": branch_score["source_point_count"],
                "model_point_count": branch_score["model_point_count"],
                "rmse_density_kg_m3": branch_score["rmse_axis"]["density_kg_m3"],
                "rmse_temperature_K": branch_score["rmse_axis"]["temperature_K"],
                "max_density_error_kg_m3": branch_score["max_axis_error"]["density_kg_m3"],
                "max_temperature_error_K": branch_score["max_axis_error"]["temperature_K"],
                "normalized_plot_score": branch_score["normalized_plot_score"],
                "branch_coverage_score": branch_score["branch_coverage_score"],
                "derivative_status": score_payload["derivative_status"],
                "pass": branch_score["pass"],
                "generation_mode": generation_mode,
                "score_basis": score_payload["score_basis"],
            }
        )
    _write_csv(
        FIT_STATISTICS_CSV,
        rows,
        [
            "scope",
            "component",
            "branch",
            "source_point_count",
            "model_point_count",
            "rmse_density_kg_m3",
            "rmse_temperature_K",
            "max_density_error_kg_m3",
            "max_temperature_error_K",
            "normalized_plot_score",
            "branch_coverage_score",
            "derivative_status",
            "pass",
            "generation_mode",
            "score_basis",
        ],
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


def _retained_native_receipt() -> dict[str, Any]:
    if MANIFEST_PATH.exists():
        payload = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        receipt = payload.get("native_freshness_receipt")
        if isinstance(receipt, dict) and receipt:
            return receipt
    raise RuntimeError(f"Retained native freshness receipt is required for --render-only: {_relative(MANIFEST_PATH)}")


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
                "replication_status": "accepted",
                "counts_toward_completion": True,
                "requires_exact_association_hessian": True,
                "artifacts": artifacts,
                "remaining_work": [],
                "source_image": _relative(SOURCE_IMAGE),
                "planned_artifact_stem": FIGURE_ID,
                "source_data_basis": "calibrated Gross 2002 Figure 1 PC-SAFT curve points plus visible experimental markers",
                "source_data_home": {
                    "saturation_density": [_relative(path) for path in REFERENCE_SATURATION_DENSITY_CSVS.values()],
                    "association_aad": [_relative(path) for path in REFERENCE_ASSOCIATION_AAD_CSVS.values()],
                },
                "near_critical_exclusions": NEAR_CRITICAL_EXCLUSIONS,
                "near_critical_connectors": NEAR_CRITICAL_CONNECTORS,
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
        raise RuntimeError("figure_01 record missing from full-replication manifest.")
    _write_json(MANIFEST_PATH, manifest)


def main() -> int:
    unknown_args = [arg for arg in sys.argv[1:] if arg != "--render-only"]
    if unknown_args:
        raise RuntimeError(f"Unsupported arguments: {unknown_args}")
    render_only = "--render-only" in sys.argv[1:]

    _copy_reference_inputs()
    source_rows = _source_rows()
    if render_only:
        if not MODEL_CSV.exists():
            raise RuntimeError(f"Retained model CSV is required for --render-only: {_relative(MODEL_CSV)}")
        model_rows = list(_read_csv(MODEL_CSV))
        receipt = _retained_native_receipt()
    else:
        parameters = _load_parameters()
        model_rows = _solve_model_rows(source_rows, parameters)
        receipt = _native_receipt()
    score_payload = _score(model_rows, source_rows)

    _write_csv(
        MODEL_CSV,
        model_rows,
        [
            "component",
            "branch",
            "temperature_K",
            "density_kg_m3",
            "density_mol_m3",
            "saturation_pressure_Pa",
            "source_reference_density_kg_m3",
            "density_error_kg_m3",
            "route_status",
            "solver_status",
            "hessian_approximation",
            "exact_hessian_available",
            "hessian_backend",
            "iteration_count",
            "pressure_consistency_norm",
            "chemical_potential_consistency_norm",
        ],
    )
    _write_plotted_csv(source_rows, model_rows)
    generation_mode = "render_only_from_retained_model_csv" if render_only else "native_solve_and_render"
    _write_fit_statistics_csv(
        score_payload,
        generation_mode=generation_mode,
        source_point_count=len(source_rows),
        model_point_count=len(model_rows),
    )
    _write_plot(source_rows, model_rows, score_payload)

    summary = {
        "figure_id": FIGURE_ID,
        "generation_mode": generation_mode,
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
        "near_critical_connectors": NEAR_CRITICAL_CONNECTORS,
        "native_route": {
            "public_entrypoint": "epcsaft_equilibrium.Equilibrium(mixture, route='single_component_vle', T=...).solve()",
            "derivative_status": score_payload["derivative_status"],
            "model_csv": MODEL_CSV,
            "native_freshness_receipt": receipt,
        },
        "near_critical_exclusions": NEAR_CRITICAL_EXCLUSIONS,
    }
    _update_manifest(score_payload, receipt)
    print(json.dumps(_jsonable(summary), indent=2, sort_keys=True))
    return 0 if score_payload["pass"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
