from __future__ import annotations

import csv
import json
import math
import os
import platform
import subprocess
import sys


from collections.abc import Mapping
from pathlib import Path
import sys as _bootstrap_sys
from pathlib import Path as _BootstrapPath

for _candidate in _BootstrapPath(__file__).resolve().parents:
    if (_candidate / "scripts" / "plot_outputs.py").is_file():
        if str(_candidate) not in _bootstrap_sys.path:
            _bootstrap_sys.path.insert(0, str(_candidate))
        break
else:
    raise ModuleNotFoundError("Could not locate repo root containing scripts/plot_outputs.py")
from scripts.plot_outputs import REPO_ROOT
from typing import Iterable

import matplotlib
import numpy as np
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

ROOT = Path(__file__).resolve().parent
ANALYSIS_ROOT = ROOT.parent
SOURCE_INPUT_ROOT = ANALYSIS_ROOT / "shared" / "source"
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts._env import require_epcsaft_install
from scripts.dev.native_runtime_env import apply_native_runtime_env
from scripts.plot_outputs import analysis_data_path, analysis_plot_set_dir, paper_validation_output_path, save_plot_figure

require_epcsaft_install()
apply_native_runtime_env(os.environ)


def _fast_machine() -> str:
    return os.environ.get("PROCESSOR_ARCHITECTURE", "AMD64")


platform.machine = _fast_machine

import epcsaft
import epcsaft_equilibrium
from scripts.data.paper_validation_parameters import paper_validation_parameter_path

P_REF = 1.0e5
MODEL_SOLVE_MAX_ITERATIONS = 180
KHUDAIDA_MIN_PHASE_DISTANCE = 1.0e-3
KHUDAIDA_MINOR_BETA_REVIEW = 1.0e-4
PARAMETER_DATASET = paper_validation_parameter_path("2026_Khudaida")
SPECIES = ["H2O", "Ethanol", "Butanol", "Na+", "Cl-"]
FORMULA_SPECIES = ["H2O", "Ethanol", "Isobutanol", "NaCl"]
IDX5 = {name: i for i, name in enumerate(SPECIES)}
IDX4 = {name: i for i, name in enumerate(FORMULA_SPECIES)}
SQRT3_OVER_2 = math.sqrt(3.0) / 2.0

MW_ION = np.asarray([18.01528e-3, 46.068e-3, 74.1216e-3, 22.98e-3, 35.45e-3], dtype=float)
MW_FORMULA = np.asarray([18.01528e-3, 46.068e-3, 74.1216e-3, 58.43e-3], dtype=float)

BLACK = "#000000"
RED = "#d62728"
BLUE = "#1f4ed8"
LIGHT_GREEN = "#63c46b"
WATER_COLOR = "#2f6fb3"
ETHANOL_COLOR = "#c25a14"
ISOBUTANOL_COLOR = "#5f8f1f"

def explicit_to_formula(x_ion: np.ndarray) -> np.ndarray:
    return ion_to_formula_basis(x_ion)


def formula_to_explicit(x_formula: np.ndarray) -> np.ndarray:
    return formula_to_ion_basis(x_formula)


def configure_style() -> None:
    plt.rcParams.update(
        {
            "font.family": "DejaVu Serif",
            "font.size": 10,
            "axes.linewidth": 1.0,
            "axes.grid": False,
            "xtick.direction": "in",
            "ytick.direction": "in",
            "xtick.top": False,
            "ytick.right": False,
            "legend.frameon": False,
            "mathtext.default": "regular",
        }
    )


def save_figure(fig: plt.Figure, path: Path) -> None:
    path = paper_validation_output_path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    save_plot_figure(fig, path, dpi=300)
    if path.parent.name == "results" and path.stem.startswith("figure_") and len(path.stem) == len("figure_00"):
        artist_csv = path.with_suffix(".csv")
        if artist_csv.exists():
            artist_csv.unlink()


def add_figure_caption(
    fig: plt.Figure, caption: str, *, left: float = 0.09, y: float = 0.02, fontsize: float = 9.0
) -> None:
    fig.text(left, y, caption, ha="left", va="bottom", fontsize=fontsize, wrap=True)


def write_csv_rows(path: Path, fieldnames: Iterable[str], rows: Iterable[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(list(rows), columns=list(fieldnames)).to_csv(path, index=False)


def out_path(fig_dir: Path, filename: str) -> Path:
    plot_set_dir = analysis_plot_set_dir(fig_dir)
    return plot_set_dir / "data" / filename


def figure_root(figure_number: int) -> Path:
    return ANALYSIS_ROOT / "figures" / figure_id_for_number(figure_number)


NO_SALT_293_TRACE = [
    {"x_ethanol_aq": 0.0046, "distribution": 4.8, "separation": 9.2, "x_isobutanol_aq": 0.0020},
    {"x_ethanol_aq": 0.0069, "distribution": 4.4, "separation": 8.3, "x_isobutanol_aq": 0.0022},
    {"x_ethanol_aq": 0.0096, "distribution": 4.2, "separation": 7.7, "x_isobutanol_aq": 0.0025},
    {"x_ethanol_aq": 0.0148, "distribution": 4.1, "separation": 7.0, "x_isobutanol_aq": 0.0030},
    {"x_ethanol_aq": 0.0205, "distribution": 3.7, "separation": 5.6, "x_isobutanol_aq": 0.0036},
    {"x_ethanol_aq": 0.0243, "distribution": 3.6, "separation": 4.8, "x_isobutanol_aq": 0.0040},
    {"x_ethanol_aq": 0.0265, "distribution": 3.4, "separation": 4.5, "x_isobutanol_aq": 0.0044},
    {"x_ethanol_aq": 0.0320, "distribution": 3.0, "separation": 4.2, "x_isobutanol_aq": 0.0050},
]

NOMINAL_ETHANOL_FEED_WT = {
    0.05: (0.12, 0.10, 0.08, 0.06, 0.05, 0.04, 0.03, 0.02),
    0.10: (0.06, 0.05, 0.04, 0.03, 0.02, 0.01),
}

EePCSAFT_AAD_REFERENCE = {
    0.05: {
        293.15: {
            "grand": 0.0161,
            "organic": (0.0287, 0.0031, 0.0313, 0.0009),
            "aqueous": (0.0482, 0.0064, 0.0021, 0.0083),
        },
        303.15: {
            "grand": 0.0168,
            "organic": (0.0305, 0.0027, 0.0336, 0.0005),
            "aqueous": (0.0495, 0.0061, 0.0026, 0.0088),
        },
        313.15: {
            "grand": 0.0203,
            "organic": (0.0245, 0.0033, 0.0276, 0.0006),
            "aqueous": (0.0487, 0.0052, 0.0025, 0.0081),
        },
    },
    0.10: {
        293.15: {
            "grand": 0.0342,
            "organic": (0.0729, 0.0096, 0.0739, 0.0005),
            "aqueous": (0.0975, 0.0020, 0.0007, 0.0161),
        },
        303.15: {
            "grand": 0.0341,
            "organic": (0.0760, 0.0021, 0.0774, 0.0005),
            "aqueous": (0.0973, 0.0023, 0.0008, 0.0165),
        },
        313.15: {
            "grand": 0.0357,
            "organic": (0.0801, 0.0039, 0.0783, 0.0002),
            "aqueous": (0.1021, 0.0025, 0.0003, 0.0179),
        },
    },
}

ENRTL_AAD_REFERENCE = {
    0.05: {
        293.15: {
            "grand": 0.0046,
            "organic": (0.0059, 0.0048, 0.0010, 0.0011),
            "aqueous": (0.0102, 0.0025, 0.0080, 0.0029),
        },
        303.15: {
            "grand": 0.0047,
            "organic": (0.0053, 0.0040, 0.0015, 0.0007),
            "aqueous": (0.0120, 0.0029, 0.0097, 0.0012),
        },
        313.15: {
            "grand": 0.0078,
            "organic": (0.0147, 0.0117, 0.0041, 0.0011),
            "aqueous": (0.0128, 0.0030, 0.0126, 0.0027),
        },
    },
    0.10: {
        293.15: {
            "grand": 0.0086,
            "organic": (0.0010, 0.0026, 0.0022, 0.0007),
            "aqueous": (0.0312, 0.0008, 0.0062, 0.0241),
        },
        303.15: {
            "grand": 0.0083,
            "organic": (0.0011, 0.0022, 0.0033, 0.0022),
            "aqueous": (0.0289, 0.0006, 0.0079, 0.0204),
        },
        313.15: {
            "grand": 0.0091,
            "organic": (0.0011, 0.0035, 0.0028, 0.0004),
            "aqueous": (0.0323, 0.0020, 0.0098, 0.0205),
        },
    },
}

SUPPORTING_FIGURE_PANELS = {
    2: [
        ("a", 2, 293.15, 0.05),
        ("b", 3, 303.15, 0.05),
        ("c", 4, 313.15, 0.05),
    ],
    3: [
        ("a", 5, 293.15, 0.10),
        ("b", 6, 303.15, 0.10),
        ("c", 7, 313.15, 0.10),
    ],
}
PHASE_COLUMNS = [
    "tie_line",
    "phase",
    "temperature_K",
    "salt_wtfrac",
    "x_water",
    "x_ethanol",
    "x_isobutanol",
    "x_nacl",
    "source",
]
MODEL_DIAGNOSTIC_COLUMNS = [
    "feed_x_water",
    "feed_x_ethanol",
    "feed_x_isobutanol",
    "feed_x_nacl",
    "status",
    "message",
    "route_status",
    "solver_status",
    "application_status",
    "postsolve_accepted",
    "phase_distance",
    "phase_distance_tolerance",
    "pressure_consistency_norm",
    "charge_balance_norm",
    "neutral_transfer_residual",
    "mean_ionic_transfer_residual",
    "exact_hessian_available",
    "hessian_approximation",
    "route_hessian_approximation",
]
MODEL_COLUMNS = (
    PHASE_COLUMNS[:-1]
    + ["beta", "residual_norm", "objective", "converged"]
    + MODEL_DIAGNOSTIC_COLUMNS
    + ["source"]
)
FEED_COLUMNS = [
    "tie_line",
    "temperature_K",
    "salt_wtfrac",
    "x_water_total",
    "x_ethanol_total",
    "x_isobutanol_total",
    "x_nacl_total",
    "x_water_salt_free",
    "x_ethanol_salt_free",
    "x_isobutanol_salt_free",
    "ethanol_total_feed_wtfrac",
    "source",
]
PLOT_POINT_COLUMNS = [
    "dataset",
    "series",
    "tie_line",
    "phase",
    "temperature_K",
    "salt_wtfrac",
    "x_water",
    "x_ethanol",
    "x_isobutanol",
    "x_nacl",
    "x_ternary",
    "y_ternary",
    "source",
]
FIT_STATISTICS_COLUMNS = [
    "scope",
    "series",
    "temperature_K",
    "salt_wtfrac",
    "source_point_count",
    "model_point_count",
    "accepted_model_count",
    "grand_aad",
    "organic_aad_water",
    "organic_aad_ethanol",
    "organic_aad_isobutanol",
    "organic_aad_nacl",
    "aqueous_aad_water",
    "aqueous_aad_ethanol",
    "aqueous_aad_isobutanol",
    "aqueous_aad_nacl",
    "max_objective",
    "rmse",
    "max_abs_error",
    "failed_tie_lines",
    "failure_reasons",
    "normalized_plot_score",
    "pass",
    "score_basis",
]


def source_input_path(filename: str) -> Path:
    return SOURCE_INPUT_ROOT / filename


def figure_id_for_number(figure_number: int) -> str:
    return f"figure_{figure_number:02d}"


def _figure_number_from_dir(fig_dir: Path) -> int:
    figure_root = analysis_plot_set_dir(fig_dir).parent
    return int(figure_root.name.split("_", maxsplit=1)[1])


def result_path(fig_dir: Path, filename: str) -> Path:
    return analysis_plot_set_dir(fig_dir) / filename


def source_path(fig_dir: Path, filename: str) -> Path:
    return analysis_data_path(fig_dir, filename, kind="source")


def _source_label(value: str | None, fallback: str = "published_figure_trace") -> str:
    return (value or fallback).strip()


def _write_source_notes(fig_dir: Path, rows: list[dict]) -> None:
    fields = ["section", "key", "value", "unit", "notes"]
    write_csv_rows(source_path(fig_dir, "source_notes.csv"), fields, rows)


def _write_source_points(fig_dir: Path, rows: list[dict]) -> None:
    fields = [
        "dataset",
        "series",
        "point_id",
        "tie_line",
        "phase",
        "temperature_K",
        "salt_wtfrac",
        "x_water",
        "x_ethanol",
        "x_isobutanol",
        "x_nacl",
        "x_water_salt_free",
        "x_ethanol_salt_free",
        "x_isobutanol_salt_free",
        "source_method",
        "source_reference",
    ]
    write_csv_rows(source_path(fig_dir, "source_points.csv"), fields, rows)


def source_experimental_cases() -> dict[tuple[float, float], list[tuple[int, tuple[float, ...], tuple[float, ...]]]]:
    path = source_input_path("table_3_4_experimental_tielines.csv")
    cases: dict[tuple[float, float], list[tuple[int, tuple[float, ...], tuple[float, ...]]]] = {}
    with path.open("r", newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        for raw in reader:
            salt_wt = float(raw["salt_wtfrac"])
            temperature_k = float(raw["temperature_K"])
            key = (salt_wt, temperature_k)
            organic = tuple(
                float(raw[name]) for name in ("x_water_org", "x_ethanol_org", "x_isobutanol_org", "x_nacl_org")
            )
            aqueous = tuple(
                float(raw[name]) for name in ("x_water_aq", "x_ethanol_aq", "x_isobutanol_aq", "x_nacl_aq")
            )
            cases.setdefault(key, []).append((int(raw["tie_line"]), organic, aqueous))
    return cases


def _experimental_rows(salt_wt: float, temperature_k: float) -> list[dict]:
    rows = []
    for tie_line, organic, aqueous in source_experimental_cases()[(salt_wt, temperature_k)]:
        rows.append(
            {
                "tie_line": tie_line,
                "temperature_K": float(temperature_k),
                "salt_wtfrac": float(salt_wt),
                "organic_formula": np.asarray(organic, dtype=float),
                "aqueous_formula": np.asarray(aqueous, dtype=float),
            }
        )
    return rows


def _source_feed_rows_for_figure(figure_number: int, temperature_k: float, salt_wt: float) -> list[dict] | None:
    path = analysis_data_path(figure_root(figure_number), "feed_compositions.csv", kind="source")
    if not path.exists():
        return None
    rows = []
    with path.open("r", newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        for idx, raw in enumerate(reader, start=1):
            ethanol = float(raw["x_ethanol_salt_free"])
            isobutanol = float(raw["x_isobutanol_salt_free"])
            water = float(raw["x_water_salt_free"])
            feed_formula = build_feed_formula_from_salt_free_molefractions(
                np.asarray([water, ethanol, isobutanol], dtype=float), salt_wt
            )
            rows.append(
                {
                    "tie_line": idx,
                    "temperature_K": float(temperature_k),
                    "salt_wtfrac": float(salt_wt),
                    "feed_formula": feed_formula,
                    "ethanol_total_feed_wtfrac": "",
                    "source": _source_label(raw.get("source"), "user_supplied_figure_trace"),
                }
            )
    return rows


def formula_to_ion_basis(x_formula: np.ndarray) -> np.ndarray:
    x_formula = np.asarray(x_formula, dtype=float)
    denom = 1.0 + float(x_formula[3])
    return np.asarray(
        [
            x_formula[0] / denom,
            x_formula[1] / denom,
            x_formula[2] / denom,
            x_formula[3] / denom,
            x_formula[3] / denom,
        ],
        dtype=float,
    )


def ion_to_formula_basis(x_ion: np.ndarray) -> np.ndarray:
    x_ion = np.asarray(x_ion, dtype=float)
    salt_formula = 0.5 * float(x_ion[IDX5["Na+"]] + x_ion[IDX5["Cl-"]])
    denom = float(x_ion[IDX5["H2O"]] + x_ion[IDX5["Ethanol"]] + x_ion[IDX5["Butanol"]] + salt_formula)
    return np.asarray(
        [
            x_ion[IDX5["H2O"]] / denom,
            x_ion[IDX5["Ethanol"]] / denom,
            x_ion[IDX5["Butanol"]] / denom,
            salt_formula / denom,
        ],
        dtype=float,
    )


def salt_free_from_formula(x_formula: np.ndarray) -> np.ndarray:
    x_formula = np.asarray(x_formula, dtype=float)
    total = float(np.sum(x_formula[:3]))
    return np.asarray(x_formula[:3], dtype=float) / total


def ternary_xy_from_formula(x_formula: np.ndarray) -> tuple[float, float]:
    salt_free = salt_free_from_formula(x_formula)
    x = float(salt_free[2] + 0.5 * salt_free[1])
    y = float(SQRT3_OVER_2 * salt_free[1])
    return x, y


def _draw_ternary_axes(ax: plt.Axes) -> None:
    triangle = np.asarray([[0.0, 0.0], [1.0, 0.0], [0.5, SQRT3_OVER_2], [0.0, 0.0]], dtype=float)
    ax.plot(triangle[:, 0], triangle[:, 1], color="black", linewidth=1.2, zorder=2)
    left_normal = np.asarray([-SQRT3_OVER_2, 0.5], dtype=float)
    right_normal = np.asarray([SQRT3_OVER_2, 0.5], dtype=float)
    for frac in np.linspace(0.05, 0.95, 19):
        is_major = abs(frac * 10.0 - round(frac * 10.0)) < 1.0e-9
        grid_linewidth = 0.6 if is_major else 0.35
        grid_alpha = 0.55 if is_major else 0.28
        # Constant ethanol: horizontal lines between left and right edges.
        ax.plot(
            [0.5 * frac, 1.0 - 0.5 * frac],
            [SQRT3_OVER_2 * frac, SQRT3_OVER_2 * frac],
            color=ETHANOL_COLOR,
            linewidth=grid_linewidth,
            alpha=grid_alpha,
            linestyle="--",
            zorder=0,
        )
        # Constant isobutanol: lines parallel to the left edge.
        ax.plot(
            [frac, 0.5 + 0.5 * frac],
            [0.0, SQRT3_OVER_2 * (1.0 - frac)],
            color=ISOBUTANOL_COLOR,
            linewidth=grid_linewidth,
            alpha=grid_alpha,
            linestyle="--",
            zorder=0,
        )
        # Constant water: lines parallel to the right edge.
        ax.plot(
            [1.0 - frac, 0.5 * (1.0 - frac)],
            [0.0, SQRT3_OVER_2 * (1.0 - frac)],
            color=WATER_COLOR,
            linewidth=grid_linewidth,
            alpha=grid_alpha,
            linestyle="--",
            zorder=0,
        )
    ax.text(0.50, -0.10, r"$x$ Isobutanol", color=ISOBUTANOL_COLOR, ha="center", va="top", fontsize=11)
    ax.text(0.15, 0.52, r"$x$ Water", color=WATER_COLOR, rotation=60, ha="center", va="center", fontsize=11)
    ax.text(0.85, 0.50, r"$x$ Ethanol", color=ETHANOL_COLOR, rotation=-60, ha="center", va="center", fontsize=11)
    left_tick_offset = 0.035
    right_tick_offset = 0.035
    for frac in np.arange(0.0, 1.01, 0.1):
        if frac < 1.0:
            ax.text(frac, -0.03, f"{frac:.1f}", color=ISOBUTANOL_COLOR, ha="center", va="top", fontsize=8)
        if 0.0 < frac < 1.0:
            # Left edge shows water decreasing from 1 at the lower-left corner to 0 at the apex.
            left_point = np.asarray([0.5 * frac, SQRT3_OVER_2 * frac], dtype=float) + left_tick_offset * left_normal
            ax.text(
                left_point[0],
                left_point[1],
                f"{1.0 - frac:.1f}",
                color=WATER_COLOR,
                ha="right",
                va="center",
                fontsize=8,
            )
            # Right edge shows ethanol increasing from 0 at the lower-right corner to 1 at the apex.
            right_point = (
                np.asarray([1.0 - 0.5 * frac, SQRT3_OVER_2 * frac], dtype=float) + right_tick_offset * right_normal
            )
            ax.text(
                right_point[0], right_point[1], f"{frac:.1f}", color=ETHANOL_COLOR, ha="left", va="center", fontsize=8
            )
    left_bottom = np.asarray([0.0, 0.0], dtype=float) + left_tick_offset * left_normal
    left_top = np.asarray([0.5, SQRT3_OVER_2], dtype=float) + left_tick_offset * left_normal
    right_bottom = np.asarray([1.0, 0.0], dtype=float) + right_tick_offset * right_normal
    right_top = np.asarray([0.5, SQRT3_OVER_2], dtype=float) + right_tick_offset * right_normal
    ax.text(left_bottom[0], left_bottom[1], "1.0", color=WATER_COLOR, ha="right", va="center", fontsize=8)
    ax.text(left_top[0], left_top[1], "0.0", color=WATER_COLOR, ha="right", va="center", fontsize=8)
    ax.text(right_bottom[0], right_bottom[1], "0.0", color=ETHANOL_COLOR, ha="left", va="center", fontsize=8)
    ax.text(right_top[0], right_top[1], "1.0", color=ETHANOL_COLOR, ha="left", va="center", fontsize=8)
    ax.set_xlim(-0.08, 1.08)
    ax.set_ylim(-0.08, SQRT3_OVER_2 + 0.06)
    ax.set_aspect("equal")
    ax.axis("off")


def _plot_tie_lines(
    ax: plt.Axes,
    rows: list[dict],
    color: str,
    marker: str,
    label: str,
    *,
    linewidth: float = 1.0,
    markersize: float = 18.0,
    linestyle: str = "-",
    xy_transform=ternary_xy_from_formula,
) -> None:
    if not rows:
        return
    for idx, row in enumerate(rows):
        aq_xy = xy_transform(row["aqueous_formula"])
        org_xy = xy_transform(row["organic_formula"])
        ax.plot(
            [aq_xy[0], org_xy[0]],
            [aq_xy[1], org_xy[1]],
            color=color,
            linewidth=linewidth,
            linestyle=linestyle,
            zorder=3,
            label=label if idx == 0 else None,
        )
        ax.scatter(
            [aq_xy[0], org_xy[0]],
            [aq_xy[1], org_xy[1]],
            s=markersize,
            marker=marker,
            facecolors=color,
            edgecolors=color,
            linewidths=0.5,
            zorder=4,
        )


def _model_objective(exp_row: dict, pred_org: np.ndarray, pred_aq: np.ndarray) -> float:
    return float(
        np.sum(np.abs(pred_org - exp_row["organic_formula"])) + np.sum(np.abs(pred_aq - exp_row["aqueous_formula"]))
    )


def build_feed_formula_from_total_feed_weights(ethanol_wt: float, salt_wt: float) -> np.ndarray:
    water_wt = 1.0 - 0.50 - salt_wt - ethanol_wt
    weights = np.asarray([water_wt, ethanol_wt, 0.50, salt_wt], dtype=float)
    moles = weights / MW_FORMULA
    return moles / np.sum(moles)


def build_feed_formula_from_salt_free_molefractions(salt_free_xyz: np.ndarray, salt_wt: float) -> np.ndarray:
    salt_free_xyz = np.asarray(salt_free_xyz, dtype=float)
    salt_free_xyz = salt_free_xyz / np.sum(salt_free_xyz)
    neutral_average_mw = float(np.dot(salt_free_xyz, MW_FORMULA[:3]))
    salt_moles_per_neutral_mole = salt_wt * neutral_average_mw / ((1.0 - salt_wt) * MW_FORMULA[3])
    total_moles = 1.0 + salt_moles_per_neutral_mole
    return np.asarray(
        [
            salt_free_xyz[0] / total_moles,
            salt_free_xyz[1] / total_moles,
            salt_free_xyz[2] / total_moles,
            salt_moles_per_neutral_mole / total_moles,
        ],
        dtype=float,
    )


def _derived_feed_rows(salt_wt: float, temperature_k: float) -> list[dict]:
    nominal_ethanol = NOMINAL_ETHANOL_FEED_WT[salt_wt]
    return [
        {
            "tie_line": idx,
            "temperature_K": float(temperature_k),
            "salt_wtfrac": float(salt_wt),
            "feed_formula": build_feed_formula_from_total_feed_weights(ethanol_wt, salt_wt),
            "ethanol_total_feed_wtfrac": float(ethanol_wt),
            "source": "derived_from_methods_1to1_feed_rule",
        }
        for idx, ethanol_wt in enumerate(nominal_ethanol, start=1)
    ]


def _plot_feed_points(
    ax: plt.Axes,
    rows: list[dict],
    color: str = LIGHT_GREEN,
    marker: str = "^",
    markersize: float = 24.0,
    label: str | None = None,
    xy_transform=ternary_xy_from_formula,
) -> None:
    if not rows:
        return
    xs = []
    ys = []
    for row in rows:
        x_coord, y_coord = xy_transform(row["feed_formula"])
        xs.append(x_coord)
        ys.append(y_coord)
    if xs:
        ax.scatter(
            xs,
            ys,
            s=markersize,
            marker=marker,
            facecolors=color,
            edgecolors=color,
            linewidths=0.5,
            zorder=5,
            label=label,
        )


def _paper_epcsaft_source_rows(fig_dir: Path, temperature_k: float, salt_wt: float) -> list[dict]:
    path = analysis_data_path(fig_dir, "paper_epcsaft_points.csv", kind="source")
    if not path.exists():
        return []
    rows = []
    with path.open("r", newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        for raw in reader:
            salt_free = np.asarray(
                [
                    float(raw["x_water_salt_free"]),
                    float(raw["x_ethanol_salt_free"]),
                    float(raw["x_isobutanol_salt_free"]),
                ],
                dtype=float,
            )
            salt_free = salt_free / float(np.sum(salt_free))
            formula = np.asarray([salt_free[0], salt_free[1], salt_free[2], 0.0], dtype=float)
            rows.append(
                {
                    "tie_line": int(raw["point_id"]),
                    "temperature_K": float(temperature_k),
                    "salt_wtfrac": float(salt_wt),
                    "organic_formula": formula,
                    "source": _source_label(raw.get("source"), "published_figure_trace"),
                }
            )
    return rows


def _plot_formula_series(
    ax: plt.Axes,
    rows: list[dict],
    key: str,
    color: str,
    marker: str,
    label: str,
    *,
    linewidth: float = 1.0,
    markersize: float = 18.0,
    linestyle: str = "-",
    xy_transform=ternary_xy_from_formula,
) -> None:
    xs = []
    ys = []
    for row in rows:
        x_formula = row[key]
        if not np.all(np.isfinite(x_formula)):
            continue
        x_coord, y_coord = xy_transform(x_formula)
        xs.append(x_coord)
        ys.append(y_coord)
    if not xs:
        return
    if len(xs) > 1 and linestyle:
        ax.plot(xs, ys, color=color, linewidth=linewidth, linestyle=linestyle, zorder=3, label=label)
        scatter_label = None
    else:
        scatter_label = label
    ax.scatter(
        xs,
        ys,
        s=markersize,
        marker=marker,
        facecolors=color,
        edgecolors=color,
        linewidths=0.5,
        zorder=4,
        label=scatter_label,
    )

def _candidate_formula_feeds(exp_row: dict, target_feed_formula: np.ndarray | None = None) -> list[np.ndarray]:
    feeds = []
    if target_feed_formula is not None and np.all(np.isfinite(target_feed_formula)):
        feeds.append(np.asarray(target_feed_formula, dtype=float) / np.sum(target_feed_formula))
    midpoint = 0.5 * (exp_row["organic_formula"] + exp_row["aqueous_formula"])
    feeds.append(midpoint / np.sum(midpoint))
    unique = []
    for feed in feeds:
        if not any(np.allclose(feed, prior, atol=1e-10) for prior in unique):
            unique.append(feed)
    return unique


def _finite_float_or_nan(value) -> float:
    if value in (None, ""):
        return np.nan
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return np.nan
    return parsed if math.isfinite(parsed) else np.nan


def _diagnostic_mapping(value) -> dict:
    return dict(value) if isinstance(value, Mapping) else {}


def _route_diagnostic_summary(diagnostics: dict | None) -> dict:
    diagnostics = _diagnostic_mapping(diagnostics)
    domain = _diagnostic_mapping(diagnostics.get("domain_margins"))
    pressure = _diagnostic_mapping(diagnostics.get("pressure_consistency"))
    charge = _diagnostic_mapping(diagnostics.get("charge_balance"))
    transfer = _diagnostic_mapping(diagnostics.get("transfer_residuals"))
    neutral_transfer = _diagnostic_mapping(transfer.get("neutral_transfer"))
    mean_ionic_transfer = _diagnostic_mapping(transfer.get("mean_ionic_transfer"))
    return {
        "postsolve_accepted": bool(diagnostics.get("postsolve_accepted", False)),
        "phase_distance": _finite_float_or_nan(domain.get("phase_distance", diagnostics.get("phase_distance"))),
        "phase_distance_tolerance": _finite_float_or_nan(domain.get("phase_distance_tolerance")),
        "pressure_consistency_norm": _finite_float_or_nan(pressure.get("pressure_consistency_norm")),
        "charge_balance_norm": _finite_float_or_nan(charge.get("max_phase_charge_residual")),
        "neutral_transfer_residual": _finite_float_or_nan(neutral_transfer.get("max_abs_residual")),
        "mean_ionic_transfer_residual": _finite_float_or_nan(mean_ionic_transfer.get("max_abs_residual")),
        "exact_hessian_available": bool(diagnostics.get("exact_hessian_available", False)),
        "hessian_approximation": str(diagnostics.get("hessian_approximation", "")),
        "route_hessian_approximation": str(diagnostics.get("route_hessian_approximation", "")),
    }


def _failed_solve_result(
    z_feed: np.ndarray,
    *,
    message: str,
    residual_norm: float = np.nan,
    route_status: str | None = None,
    solver_status: str | None = None,
    application_status: str | None = None,
) -> dict:
    return {
        "converged": False,
        "status": None,
        "message": message,
        "residual_norm": residual_norm,
        "route_status": route_status,
        "solver_status": solver_status,
        "application_status": application_status,
        "feed_formula": ion_to_formula_basis(z_feed),
        "organic_formula": np.full(4, np.nan),
        "aqueous_formula": np.full(4, np.nan),
        "beta_organic": np.nan,
        "beta_aqueous": np.nan,
        "split_norm": np.nan,
        "objective": np.nan,
        "source": "epcsaft_public_electrolyte_lle",
        **_route_diagnostic_summary(
            {
                "route_status": route_status,
                "solver_status": solver_status,
                "application_status": application_status,
                "postsolve_accepted": False,
            }
        ),
    }


def _solve_formula_feed_direct(temperature_k: float, feed_formula: np.ndarray) -> dict | None:
    z_feed = formula_to_ion_basis(feed_formula)
    if not np.all(np.isfinite(z_feed)):
        return None

    try:
        mixture = epcsaft.Mixture.from_folder(
            PARAMETER_DATASET,
            components=SPECIES,
            reference_temperature=float(temperature_k),
            reference_composition=z_feed,
        )
        result = epcsaft_equilibrium.Equilibrium(
            mixture,
            route="electrolyte_lle",
            T=float(temperature_k),
            P=P_REF,
            z=z_feed,
        ).solve(
            solver_options={
                "max_iterations": MODEL_SOLVE_MAX_ITERATIONS,
                "tolerance": 1.0e-6,
                "hessian_mode": "auto",
                "ipopt_iteration_history_limit": 8,
                "ipopt_acceptable_tolerance": 1.0e-7,
                "ipopt_constraint_violation_tolerance": 1.0e-8,
                "ipopt_dual_infeasibility_tolerance": 1.0e-8,
                "ipopt_complementarity_tolerance": 1.0e-8,
            }
        )
    except (epcsaft.InputError, epcsaft.SolutionError, RuntimeError, ValueError) as exc:
        diagnostics = getattr(exc, "diagnostics", None) or (
            exc.args[1] if len(exc.args) > 1 and isinstance(exc.args[1], dict) else {}
        )
        failed = _failed_solve_result(
            z_feed,
            message=str(exc.args[0] if exc.args else exc),
            residual_norm=float(diagnostics.get("solver_residual_norm", np.nan)),
            route_status=diagnostics.get("route_status"),
            solver_status=diagnostics.get("solver_status"),
            application_status=diagnostics.get("application_status"),
        )
        failed["split_norm"] = float(diagnostics.get("phase_distance", np.nan))
        return failed

    phase_compositions = dict(result.phase_compositions)
    if len(phase_compositions) != 2:
        return None
    formula_phases = {
        label: explicit_to_formula(np.asarray(composition, dtype=float))
        for label, composition in phase_compositions.items()
    }
    organic_label = max(formula_phases, key=lambda label: float(formula_phases[label][IDX4["Isobutanol"]]))
    aqueous_label = max(
        (label for label in formula_phases if label != organic_label),
        key=lambda label: float(formula_phases[label][IDX4["H2O"]] + formula_phases[label][IDX4["NaCl"]]),
    )
    org_formula = formula_phases[organic_label]
    aq_formula = formula_phases[aqueous_label]
    diagnostics = result.diagnostics
    diagnostic_summary = _route_diagnostic_summary(diagnostics)
    if not np.isfinite(diagnostic_summary["phase_distance"]):
        diagnostic_summary["phase_distance"] = float(np.max(np.abs(org_formula - aq_formula)))
    residual_norm = float(diagnostics.get("solver_residual_norm", np.nan))
    return {
        "converged": True,
        "status": "accepted",
        "message": None,
        "residual_norm": residual_norm,
        "route_status": diagnostics.get("route_status"),
        "solver_status": diagnostics.get("solver_status"),
        "application_status": diagnostics.get("application_status"),
        "feed_formula": ion_to_formula_basis(z_feed),
        "organic_formula": org_formula,
        "aqueous_formula": aq_formula,
        "beta_organic": float(result.phase_fractions[organic_label]),
        "beta_aqueous": float(result.phase_fractions[aqueous_label]),
        "split_norm": float(diagnostic_summary["phase_distance"]),
        "objective": np.nan,
        "source": "epcsaft_public_electrolyte_lle",
        **diagnostic_summary,
    }


def _json_ready_solve_result(row: dict | None) -> dict | None:
    if row is None:
        return None
    out: dict = {}
    for key, value in row.items():
        if isinstance(value, np.ndarray):
            out[key] = value.tolist()
        elif isinstance(value, np.generic):
            out[key] = value.item()
        elif isinstance(value, float) and not math.isfinite(value):
            out[key] = None
        else:
            out[key] = value
    return out


def _solve_result_from_json(row: dict | None) -> dict | None:
    if row is None:
        return None
    out = dict(row)
    for key in ("feed_formula", "organic_formula", "aqueous_formula"):
        out[key] = np.asarray(out[key], dtype=float)
    for key in (
        "residual_norm",
        "beta_organic",
        "beta_aqueous",
        "split_norm",
        "objective",
        "phase_distance",
        "phase_distance_tolerance",
        "pressure_consistency_norm",
        "charge_balance_norm",
        "neutral_transfer_residual",
        "mean_ionic_transfer_residual",
    ):
        if out.get(key) is None:
            out[key] = np.nan
    return out


def _solve_formula_feed(temperature_k: float, feed_formula: np.ndarray) -> dict | None:
    if os.environ.get("KHUDAIDA_SOLVE_IN_PROCESS", "").strip().lower() in {"1", "true", "yes", "on"}:
        return _solve_formula_feed_direct(temperature_k, feed_formula)

    z_feed = formula_to_ion_basis(feed_formula)
    if not np.all(np.isfinite(z_feed)):
        return None
    helper = ROOT / "solve_electrolyte_feed.py"
    payload = {
        "temperature_K": float(temperature_k),
        "feed_formula": [float(value) for value in np.asarray(feed_formula, dtype=float)],
    }
    env = os.environ.copy()
    env["KHUDAIDA_SOLVE_IN_PROCESS"] = "1"
    try:
        completed = subprocess.run(
            [sys.executable, str(helper)],
            input=json.dumps(payload),
            capture_output=True,
            check=False,
            encoding="utf-8",
            env=env,
            timeout=120,
        )
    except subprocess.TimeoutExpired:
        return _failed_solve_result(z_feed, message="public electrolyte_lle solve timed out in isolated subprocess")

    stdout_lines = [line for line in completed.stdout.splitlines() if line.strip()]
    if completed.returncode != 0:
        stderr_lines = [line for line in completed.stderr.splitlines() if line.strip()]
        detail = stderr_lines[0] if stderr_lines else f"returncode={completed.returncode}"
        return _failed_solve_result(
            z_feed,
            message=f"public electrolyte_lle isolated solve failed: {detail}",
        )
    if not stdout_lines:
        return _failed_solve_result(z_feed, message="public electrolyte_lle isolated solve returned no JSON")
    return _solve_result_from_json(json.loads(stdout_lines[-1]))


def solve_model_rows(exp_rows: list[dict], feed_rows: list[dict] | None = None) -> list[dict]:
    feed_map = {int(row["tie_line"]): np.asarray(row["feed_formula"], dtype=float) for row in (feed_rows or [])}
    solved = []
    for exp_row in exp_rows:
        best = None
        target_feed_formula = feed_map.get(int(exp_row["tie_line"]))
        for feed_idx, feed_formula in enumerate(_candidate_formula_feeds(exp_row, target_feed_formula)):
            candidate = _solve_formula_feed(exp_row["temperature_K"], feed_formula)
            if candidate is None:
                continue
            score = _model_objective(exp_row, candidate["organic_formula"], candidate["aqueous_formula"])
            if best is None or score < best["objective"]:
                best = {**candidate, "objective": score}
            if best is not None and target_feed_formula is not None and feed_idx == 0 and best["converged"]:
                break
        if best is None:
            best = {
                "converged": False,
                "status": None,
                "message": "No converged model candidate.",
                "residual_norm": np.nan,
                "route_status": None,
                "solver_status": None,
                "application_status": None,
                "feed_formula": np.full(4, np.nan),
                "organic_formula": np.full(4, np.nan),
                "aqueous_formula": np.full(4, np.nan),
                "beta_organic": np.nan,
                "beta_aqueous": np.nan,
                "split_norm": np.nan,
                "objective": np.nan,
            }
        solved.append(
            {
                "tie_line": exp_row["tie_line"],
                "temperature_K": exp_row["temperature_K"],
                "salt_wtfrac": exp_row["salt_wtfrac"],
                **best,
            }
        )
    return solved


def _parse_float(value: str | float | int | None) -> float:
    if value in (None, ""):
        return np.nan
    return float(value)


def _csv_float(value) -> float | str:
    parsed = _finite_float_or_nan(value)
    return float(parsed) if np.isfinite(parsed) else ""


def _parse_bool(value) -> bool:
    return str(value or "").strip().lower() in {"true", "1", "yes"}


def _finite_model_phases(row: dict) -> bool:
    return np.all(np.isfinite(row["organic_formula"])) and np.all(np.isfinite(row["aqueous_formula"]))


def _formula_phase_distance(row: dict) -> float:
    if not _finite_model_phases(row):
        return np.nan
    return float(np.max(np.abs(np.asarray(row["organic_formula"]) - np.asarray(row["aqueous_formula"]))))


def _model_phase_distance(row: dict) -> float:
    phase_distance = _finite_float_or_nan(row.get("phase_distance", row.get("split_norm")))
    if np.isfinite(phase_distance):
        return phase_distance
    return _formula_phase_distance(row)


def _minor_beta(row: dict) -> float:
    beta_values = (_finite_float_or_nan(row.get("beta_organic")), _finite_float_or_nan(row.get("beta_aqueous")))
    finite = [value for value in beta_values if np.isfinite(value)]
    return min(finite) if finite else np.nan


def _collapsed_split_failure(row: dict) -> dict[str, str | float] | None:
    status = str(row.get("status") or "").strip().lower()
    if status != "collapsed_split" and not bool(row.get("converged")):
        return None
    if not _finite_model_phases(row):
        return None
    phase_distance = _model_phase_distance(row)
    formula_distance = _formula_phase_distance(row)
    minor_beta = _minor_beta(row)
    collapsed = np.isfinite(phase_distance) and phase_distance < KHUDAIDA_MIN_PHASE_DISTANCE
    duplicate_formula = np.isfinite(formula_distance) and formula_distance < KHUDAIDA_MIN_PHASE_DISTANCE
    trace_minor_phase = np.isfinite(minor_beta) and minor_beta < KHUDAIDA_MINOR_BETA_REVIEW
    if status != "collapsed_split" and not (collapsed or duplicate_formula or trace_minor_phase):
        return None
    return {
        "failure_kind": "collapsed_split",
        "root_cause": "postsolve_acceptance",
        "message": "Public electrolyte_lle returned a collapsed split under the Khudaida model-row contract.",
        "phase_distance": phase_distance,
        "formula_phase_distance": formula_distance,
        "phase_distance_threshold": KHUDAIDA_MIN_PHASE_DISTANCE,
        "minor_beta": minor_beta,
        "minor_beta_review_threshold": KHUDAIDA_MINOR_BETA_REVIEW,
        "follow_up_issue": "#338",
    }


def _accepted_model_rows(rows: list[dict]) -> list[dict]:
    return [
        row
        for row in rows
        if bool(row.get("converged")) and _finite_model_phases(row) and _collapsed_split_failure(row) is None
    ]


def _load_model_rows_from_csv(path: Path) -> list[dict]:
    grouped: dict[int, dict] = {}
    with path.open("r", newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        for raw in reader:
            tie_line = int(raw["tie_line"])
            entry = grouped.setdefault(
                tie_line,
                {
                    "tie_line": tie_line,
                    "temperature_K": _parse_float(raw.get("temperature_K")),
                    "salt_wtfrac": _parse_float(raw.get("salt_wtfrac")),
                    "organic_formula": np.full(4, np.nan),
                    "aqueous_formula": np.full(4, np.nan),
                    "feed_formula": np.full(4, np.nan),
                    "beta_organic": np.nan,
                    "beta_aqueous": np.nan,
                    "residual_norm": np.nan,
                    "objective": np.nan,
                    "converged": False,
                    "status": None,
                    "message": None,
                    "split_norm": np.nan,
                    "source": raw.get("source", "epcsaft_public_electrolyte_lle"),
                    "route_status": raw.get("route_status", ""),
                    "solver_status": raw.get("solver_status", ""),
                    "application_status": raw.get("application_status", ""),
                    "postsolve_accepted": _parse_bool(raw.get("postsolve_accepted")),
                    "phase_distance": _parse_float(raw.get("phase_distance")),
                    "phase_distance_tolerance": _parse_float(raw.get("phase_distance_tolerance")),
                    "pressure_consistency_norm": _parse_float(raw.get("pressure_consistency_norm")),
                    "charge_balance_norm": _parse_float(raw.get("charge_balance_norm")),
                    "neutral_transfer_residual": _parse_float(raw.get("neutral_transfer_residual")),
                    "mean_ionic_transfer_residual": _parse_float(raw.get("mean_ionic_transfer_residual")),
                    "exact_hessian_available": _parse_bool(raw.get("exact_hessian_available")),
                    "hessian_approximation": raw.get("hessian_approximation", ""),
                    "route_hessian_approximation": raw.get("route_hessian_approximation", ""),
                },
            )
            feed_vec = np.asarray(
                [
                    _parse_float(raw.get("feed_x_water")),
                    _parse_float(raw.get("feed_x_ethanol")),
                    _parse_float(raw.get("feed_x_isobutanol")),
                    _parse_float(raw.get("feed_x_nacl")),
                ],
                dtype=float,
            )
            if np.all(np.isfinite(feed_vec)):
                entry["feed_formula"] = feed_vec
            phase_vec = np.asarray(
                [
                    _parse_float(raw.get("x_water")),
                    _parse_float(raw.get("x_ethanol")),
                    _parse_float(raw.get("x_isobutanol")),
                    _parse_float(raw.get("x_nacl")),
                ],
                dtype=float,
            )
            phase_name = str(raw.get("phase", "")).strip().lower()
            if phase_name == "organic":
                entry["organic_formula"] = phase_vec
                entry["beta_organic"] = _parse_float(raw.get("beta"))
            elif phase_name == "aqueous":
                entry["aqueous_formula"] = phase_vec
                entry["beta_aqueous"] = _parse_float(raw.get("beta"))
            entry["residual_norm"] = _parse_float(raw.get("residual_norm"))
            entry["objective"] = _parse_float(raw.get("objective"))
            entry["converged"] = _parse_bool(raw.get("converged"))
            entry["status"] = raw.get("status") or entry["status"]
            entry["message"] = raw.get("message") or entry["message"]
            entry["source"] = raw.get("source") or entry["source"]
    return [grouped[key] for key in sorted(grouped)]


def _model_cache_path(fig_dir: Path) -> Path:
    return out_path(fig_dir, "model_tielines.csv")


def get_or_build_model_rows(
    fig_dir: Path, exp_rows: list[dict], feed_rows: list[dict] | None = None, force_recompute: bool = False
) -> list[dict]:
    cache_path = _model_cache_path(fig_dir)
    if not force_recompute and cache_path.exists():
        cached = _load_model_rows_from_csv(cache_path)
        cached_ties = {row["tie_line"] for row in cached}
        expected_ties = {row["tie_line"] for row in exp_rows}
        if cached_ties == expected_ties:
            return cached
    model_rows = solve_model_rows(exp_rows, feed_rows=feed_rows)
    write_case_data(fig_dir, exp_rows, model_rows)
    return model_rows


def _phase_rows_for_csv(rows: list[dict], source: str) -> list[dict]:
    out = []
    for row in rows:
        for phase_name, x in (("organic", row["organic_formula"]), ("aqueous", row["aqueous_formula"])):
            out.append(
                {
                    "tie_line": row["tie_line"],
                    "phase": phase_name,
                    "temperature_K": row["temperature_K"],
                    "salt_wtfrac": row["salt_wtfrac"],
                    "x_water": float(x[0]),
                    "x_ethanol": float(x[1]),
                    "x_isobutanol": float(x[2]),
                    "x_nacl": float(x[3]),
                    "source": source,
                }
            )
    return out


def _model_rows_for_csv(rows: list[dict]) -> list[dict]:
    out = []
    for row in rows:
        feed = np.asarray(row.get("feed_formula", np.full(4, np.nan)), dtype=float)
        collapse = _collapsed_split_failure(row)
        model_accepted = bool(row["converged"]) and collapse is None
        status = "collapsed_split" if collapse is not None else row.get("status", "")
        message = str(collapse["message"]) if collapse is not None else row.get("message", "")
        for phase_name, x, beta in (
            ("organic", row["organic_formula"], row["beta_organic"]),
            ("aqueous", row["aqueous_formula"], row["beta_aqueous"]),
        ):
            out.append(
                {
                    "tie_line": row["tie_line"],
                    "phase": phase_name,
                    "temperature_K": row["temperature_K"],
                    "salt_wtfrac": row["salt_wtfrac"],
                    "x_water": float(x[0]),
                    "x_ethanol": float(x[1]),
                    "x_isobutanol": float(x[2]),
                    "x_nacl": float(x[3]),
                    "beta": float(beta),
                    "residual_norm": _csv_float(row["residual_norm"]),
                    "objective": _csv_float(row["objective"]),
                    "converged": model_accepted,
                    "feed_x_water": _csv_float(feed[0]),
                    "feed_x_ethanol": _csv_float(feed[1]),
                    "feed_x_isobutanol": _csv_float(feed[2]),
                    "feed_x_nacl": _csv_float(feed[3]),
                    "status": status,
                    "message": message,
                    "route_status": row.get("route_status", ""),
                    "solver_status": row.get("solver_status", ""),
                    "application_status": row.get("application_status", ""),
                    "postsolve_accepted": bool(row.get("postsolve_accepted", False)),
                    "phase_distance": _csv_float(row.get("phase_distance", row.get("split_norm"))),
                    "phase_distance_tolerance": _csv_float(row.get("phase_distance_tolerance")),
                    "pressure_consistency_norm": _csv_float(row.get("pressure_consistency_norm")),
                    "charge_balance_norm": _csv_float(row.get("charge_balance_norm")),
                    "neutral_transfer_residual": _csv_float(row.get("neutral_transfer_residual")),
                    "mean_ionic_transfer_residual": _csv_float(row.get("mean_ionic_transfer_residual")),
                    "exact_hessian_available": bool(row.get("exact_hessian_available", False)),
                    "hessian_approximation": row.get("hessian_approximation", ""),
                    "route_hessian_approximation": row.get("route_hessian_approximation", ""),
                    "source": str(row.get("source", "epcsaft_public_electrolyte_lle")),
                }
            )
    return out


def _feed_rows_for_csv(rows: list[dict]) -> list[dict]:
    out = []
    ordered_rows = sorted(rows, key=lambda row: float(salt_free_from_formula(row["feed_formula"])[1]))
    for row in ordered_rows:
        x = row["feed_formula"]
        x_salt_free = salt_free_from_formula(x)
        out.append(
            {
                "tie_line": row["tie_line"],
                "temperature_K": row["temperature_K"],
                "salt_wtfrac": row["salt_wtfrac"],
                "x_water_total": float(x[0]),
                "x_ethanol_total": float(x[1]),
                "x_isobutanol_total": float(x[2]),
                "x_nacl_total": float(x[3]),
                "x_water_salt_free": float(x_salt_free[0]),
                "x_ethanol_salt_free": float(x_salt_free[1]),
                "x_isobutanol_salt_free": float(x_salt_free[2]),
                "ethanol_total_feed_wtfrac": (
                    float(row["ethanol_total_feed_wtfrac"])
                    if row["ethanol_total_feed_wtfrac"] not in ("", None)
                    else ""
                ),
                "source": row["source"],
            }
        )
    return out


def _plot_point_row(
    dataset: str,
    series: str,
    tie_line: int | str,
    phase: str,
    temperature_k: float,
    salt_wt: float,
    x_formula: np.ndarray,
    source: str,
) -> dict:
    x_coord, y_coord = ternary_xy_from_formula(x_formula)
    return {
        "dataset": dataset,
        "series": series,
        "tie_line": tie_line,
        "phase": phase,
        "temperature_K": float(temperature_k),
        "salt_wtfrac": float(salt_wt),
        "x_water": float(x_formula[0]),
        "x_ethanol": float(x_formula[1]),
        "x_isobutanol": float(x_formula[2]),
        "x_nacl": float(x_formula[3]),
        "x_ternary": x_coord,
        "y_ternary": y_coord,
        "source": source,
    }


def _phase_plot_rows(dataset: str, series: str, rows: list[dict], source: str) -> list[dict]:
    out: list[dict] = []
    for row in rows:
        for phase, key in (("organic", "organic_formula"), ("aqueous", "aqueous_formula")):
            x_formula = row[key]
            if np.all(np.isfinite(x_formula)):
                out.append(
                    _plot_point_row(
                        dataset,
                        series,
                        row["tie_line"],
                        phase,
                        row["temperature_K"],
                        row["salt_wtfrac"],
                        x_formula,
                        source,
                    )
                )
    return out


def _organic_series_plot_rows(dataset: str, series: str, rows: list[dict], source: str) -> list[dict]:
    out: list[dict] = []
    for row in rows:
        x_formula = row["organic_formula"]
        if np.all(np.isfinite(x_formula)):
            out.append(
                _plot_point_row(
                    dataset,
                    series,
                    row["tie_line"],
                    "organic",
                    row["temperature_K"],
                    row["salt_wtfrac"],
                    x_formula,
                    source,
                )
            )
    return out


def _feed_plot_rows(rows: list[dict]) -> list[dict]:
    out: list[dict] = []
    for row in rows:
        out.append(
            _plot_point_row(
                "source",
                "feed",
                row["tie_line"],
                "feed",
                row["temperature_K"],
                row["salt_wtfrac"],
                row["feed_formula"],
                row["source"],
            )
        )
    return out


def _score_from_aad(value: float) -> float | str:
    if not np.isfinite(value):
        return ""
    return max(0.0, min(10.0, 10.0 - 50.0 * float(value)))


def _summary_passes(summary: dict) -> bool:
    grand = summary.get("grand", "")
    if grand == "" or not np.isfinite(float(grand)):
        return False
    score = _score_from_aad(float(grand))
    return bool(score != "" and float(score) >= 8.0)


def _fit_error_metrics(exp_rows: list[dict], model_rows: list[dict]) -> dict[str, float | str]:
    valid = _accepted_model_rows(model_rows)
    if not valid:
        return {"rmse": "", "max_abs_error": ""}
    exp_map = {row["tie_line"]: row for row in exp_rows}
    deltas = []
    for row in valid:
        exp_row = exp_map[row["tie_line"]]
        deltas.extend((row["organic_formula"] - exp_row["organic_formula"]).tolist())
        deltas.extend((row["aqueous_formula"] - exp_row["aqueous_formula"]).tolist())
    arr = np.asarray(deltas, dtype=float)
    return {"rmse": float(np.sqrt(np.mean(arr * arr))), "max_abs_error": float(np.max(np.abs(arr)))}


def _short_float(value) -> str:
    parsed = _finite_float_or_nan(value)
    return f"{parsed:.6g}" if np.isfinite(parsed) else ""


def _model_failure_summary(model_rows: list[dict], *, include_objectives: bool) -> dict[str, str]:
    failed_ties: list[str] = []
    reasons: list[str] = []
    for row in model_rows:
        tie_line = str(row["tie_line"])
        finite_phases = _finite_model_phases(row)
        collapse = _collapsed_split_failure(row)
        reason = ""
        if collapse is not None:
            reason = (
                "collapsed_split;"
                f"phase_distance={_short_float(collapse['phase_distance'])};"
                f"phase_distance_threshold={KHUDAIDA_MIN_PHASE_DISTANCE:.6g};"
                f"minor_beta={_short_float(collapse['minor_beta'])};"
                f"minor_beta_review_threshold={KHUDAIDA_MINOR_BETA_REVIEW:.6g};"
                f"objective={_short_float(row.get('objective'))};"
                f"route_status={row.get('route_status', '')};"
                f"solver_status={row.get('solver_status', '')};"
                f"application_status={row.get('application_status', '')};"
                f"postsolve_accepted={bool(row.get('postsolve_accepted', False))};"
                f"root_cause={collapse['root_cause']};"
                f"follow_up_issue={collapse['follow_up_issue']}"
            )
        elif not bool(row.get("converged")):
            reason = row.get("message") or "public electrolyte_lle route did not converge"
        elif not finite_phases:
            reason = row.get("message") or "public electrolyte_lle route produced no finite model phases"
        elif include_objectives:
            objective = _short_float(row.get("objective"))
            phase_distance = _short_float(row.get("phase_distance", row.get("split_norm")))
            reason = f"objective={objective};phase_distance={phase_distance}"
        if reason:
            failed_ties.append(tie_line)
            reasons.append(f"{tie_line}:{reason}")
    return {"failed_tie_lines": ",".join(failed_ties), "failure_reasons": " | ".join(reasons)}


def _fit_statistics_row(
    scope: str,
    series: str,
    temperature_k: float | str,
    salt_wt: float | str,
    source_point_count: int,
    model_point_count: int,
    accepted_model_count: int,
    summary: dict,
    max_objective: float | str,
    score_basis: str,
    rmse: float | str = "",
    max_abs_error: float | str = "",
    failed_tie_lines: str = "",
    failure_reasons: str = "",
) -> dict:
    organic = summary.get("organic", ("", "", "", ""))
    aqueous = summary.get("aqueous", ("", "", "", ""))
    grand = summary.get("grand", "")
    score = _score_from_aad(float(grand)) if grand != "" and np.isfinite(float(grand)) else ""
    return {
        "scope": scope,
        "series": series,
        "temperature_K": temperature_k,
        "salt_wtfrac": salt_wt,
        "source_point_count": source_point_count,
        "model_point_count": model_point_count,
        "accepted_model_count": accepted_model_count,
        "grand_aad": grand,
        "organic_aad_water": organic[0],
        "organic_aad_ethanol": organic[1],
        "organic_aad_isobutanol": organic[2],
        "organic_aad_nacl": organic[3],
        "aqueous_aad_water": aqueous[0],
        "aqueous_aad_ethanol": aqueous[1],
        "aqueous_aad_isobutanol": aqueous[2],
        "aqueous_aad_nacl": aqueous[3],
        "max_objective": max_objective,
        "rmse": rmse,
        "max_abs_error": max_abs_error,
        "failed_tie_lines": failed_tie_lines,
        "failure_reasons": failure_reasons,
        "normalized_plot_score": score,
        "pass": bool(score != "" and float(score) >= 8.0),
        "score_basis": score_basis,
    }


def _source_rows_for_lle_figure(
    exp_rows: list[dict], feed_rows: list[dict], paper_rows: list[dict], source_reference: str
) -> list[dict]:
    rows: list[dict] = []
    for row in exp_rows:
        for phase, x in (("organic", row["organic_formula"]), ("aqueous", row["aqueous_formula"])):
            rows.append(
                {
                    "dataset": "experimental_tieline",
                    "series": "experimental",
                    "point_id": "",
                    "tie_line": row["tie_line"],
                    "phase": phase,
                    "temperature_K": row["temperature_K"],
                    "salt_wtfrac": row["salt_wtfrac"],
                    "x_water": float(x[0]),
                    "x_ethanol": float(x[1]),
                    "x_isobutanol": float(x[2]),
                    "x_nacl": float(x[3]),
                    "x_water_salt_free": "",
                    "x_ethanol_salt_free": "",
                    "x_isobutanol_salt_free": "",
                    "source_method": "source_table",
                    "source_reference": "shared/source/table_3_4_experimental_tielines.csv",
                }
            )
    for row in feed_rows:
        x = row["feed_formula"]
        salt_free = salt_free_from_formula(x)
        rows.append(
            {
                "dataset": "feed",
                "series": "feed",
                "point_id": row["tie_line"],
                "tie_line": row["tie_line"],
                "phase": "feed",
                "temperature_K": row["temperature_K"],
                "salt_wtfrac": row["salt_wtfrac"],
                "x_water": float(x[0]),
                "x_ethanol": float(x[1]),
                "x_isobutanol": float(x[2]),
                "x_nacl": float(x[3]),
                "x_water_salt_free": float(salt_free[0]),
                "x_ethanol_salt_free": float(salt_free[1]),
                "x_isobutanol_salt_free": float(salt_free[2]),
                "source_method": row["source"],
                "source_reference": source_reference,
            }
        )
    for row in paper_rows:
        x = row["organic_formula"]
        salt_free = salt_free_from_formula(x)
        rows.append(
            {
                "dataset": "paper_epcsaft",
                "series": "paper_epcsaft_organic",
                "point_id": row["tie_line"],
                "tie_line": row["tie_line"],
                "phase": "organic",
                "temperature_K": row["temperature_K"],
                "salt_wtfrac": row["salt_wtfrac"],
                "x_water": float(x[0]),
                "x_ethanol": float(x[1]),
                "x_isobutanol": float(x[2]),
                "x_nacl": float(x[3]),
                "x_water_salt_free": float(salt_free[0]),
                "x_ethanol_salt_free": float(salt_free[1]),
                "x_isobutanol_salt_free": float(salt_free[2]),
                "source_method": row["source"],
                "source_reference": source_reference,
            }
        )
    return rows


def _write_lle_contract_outputs(
    fig_dir: Path,
    figure_number: int,
    exp_rows: list[dict],
    feed_rows: list[dict],
    model_rows: list[dict],
    paper_rows: list[dict],
) -> None:
    figure_id = figure_id_for_number(figure_number)
    write_csv_rows(result_path(fig_dir, "model_curve.csv"), MODEL_COLUMNS, _model_rows_for_csv(model_rows))
    plotted_rows = [
        *_phase_plot_rows("source", "experimental_tielines", exp_rows, "paper_table"),
        *_phase_plot_rows("model", "package_electrolyte_lle", model_rows, "epcsaft_public_electrolyte_lle"),
        *_organic_series_plot_rows("source", "paper_epcsaft_organic", paper_rows, "published_figure_trace"),
        *_feed_plot_rows(feed_rows),
    ]
    write_csv_rows(result_path(fig_dir, "plotted_data.csv"), PLOT_POINT_COLUMNS, plotted_rows)
    source_reference = f"analyses/paper_validation/2026_khudaida/figures/{figure_id}/source/source_points.csv"
    _write_source_points(fig_dir, _source_rows_for_lle_figure(exp_rows, feed_rows, paper_rows, source_reference))
    _write_source_notes(
        fig_dir,
        [
            {"section": "provenance", "key": "paper", "value": "Khudaida 2026", "unit": "", "notes": ""},
            {"section": "provenance", "key": "figure", "value": figure_id, "unit": "", "notes": ""},
            {"section": "provenance", "key": "source_image", "value": f"source/{figure_id}.png", "unit": "", "notes": ""},
            {"section": "basis", "key": "composition", "value": "salt-free ternary projection with NaCl retained in source/model CSV rows", "unit": "", "notes": ""},
            {"section": "model", "key": "route", "value": "public electrolyte_lle", "unit": "", "notes": "package rows are retained from the latest public electrolyte_lle regeneration; set KHUDAIDA_FORCE_RECOMPUTE=1 to refresh"},
            {
                "section": "model",
                "key": "collapsed_split_contract",
                "value": "failed_model_row",
                "unit": "",
                "notes": "Rows below phase_distance 0.001 or minor beta 0.0001 are retained as diagnostics but excluded from accepted model counts; solver success with postsolve_accepted=True is classified as root_cause=postsolve_acceptance, with #338 retaining fitted-parameter/noncollapsed-branch follow-up ownership.",
            },
            {
                "section": "parameters",
                "key": "parameter_dataset",
                "value": PARAMETER_DATASET.relative_to(REPO_ROOT).as_posix(),
                "unit": "",
                "notes": "retained 2026_Khudaida Tables 5-7 parameter bundle for public-route validation",
            },
            {
                "section": "parameters",
                "key": "figiel_2025_ssm_ds_born_options",
                "value": "retained_in_2026_Khudaida",
                "unit": "",
                "notes": "Figiel 2025 SSM+DS/Born option family is carried by the Khudaida parameter bundle",
            },
        ],
    )
    valid = _accepted_model_rows(model_rows)
    summary = _aad_summary(exp_rows, model_rows)
    metrics = _fit_error_metrics(exp_rows, model_rows)
    failures = _model_failure_summary(model_rows, include_objectives=not _summary_passes(summary))
    max_objective = max((float(row["objective"]) for row in valid if np.isfinite(row["objective"])), default="")
    write_csv_rows(
        result_path(fig_dir, "fit_statistics.csv"),
        FIT_STATISTICS_COLUMNS,
        [
            _fit_statistics_row(
                "figure",
                "package_electrolyte_lle_vs_experimental",
                exp_rows[0]["temperature_K"],
                exp_rows[0]["salt_wtfrac"],
                len(exp_rows) * 2,
                len(model_rows) * 2,
                len(valid) * 2,
                summary,
                max_objective,
                "formula-basis mean absolute phase-composition deviation against source tie-lines",
                metrics["rmse"],
                metrics["max_abs_error"],
                failures["failed_tie_lines"],
                failures["failure_reasons"],
            )
        ],
    )


def write_case_data(fig_dir: Path, exp_rows: list[dict], model_rows: list[dict]) -> None:
    write_csv_rows(
        out_path(fig_dir, "experimental_tielines.csv"), PHASE_COLUMNS, _phase_rows_for_csv(exp_rows, "paper_table")
    )
    write_csv_rows(out_path(fig_dir, "model_tielines.csv"), MODEL_COLUMNS, _model_rows_for_csv(model_rows))


def write_lle_figure_data(
    fig_dir: Path,
    figure_number: int,
    temperature_k: float,
    salt_wt: float,
    *,
    force_recompute: bool | None = None,
) -> dict[str, list[dict]]:
    exp_rows = _experimental_rows(salt_wt, temperature_k)
    feed_rows = _source_feed_rows_for_figure(figure_number, temperature_k, salt_wt) or _derived_feed_rows(
        salt_wt, temperature_k
    )
    if force_recompute is None:
        force_recompute = os.environ.get("KHUDAIDA_FORCE_RECOMPUTE", "").strip().lower() in {"1", "true", "yes", "on"}
    model_rows = get_or_build_model_rows(fig_dir, exp_rows, feed_rows=feed_rows, force_recompute=force_recompute)
    paper_rows = _paper_epcsaft_source_rows(fig_dir, temperature_k, salt_wt)
    write_csv_rows(out_path(fig_dir, "feed_compositions.csv"), FEED_COLUMNS, _feed_rows_for_csv(feed_rows))
    _write_lle_contract_outputs(fig_dir, figure_number, exp_rows, feed_rows, model_rows, paper_rows)
    return {"experimental": exp_rows, "feed": feed_rows, "model": model_rows, "paper": paper_rows}


def plot_lle_figure(fig_dir: Path, figure_number: int, temperature_k: float, salt_wt: float) -> None:
    configure_style()
    data = write_lle_figure_data(fig_dir, figure_number, temperature_k, salt_wt)
    exp_rows = data["experimental"]
    feed_rows = data["feed"]
    model_rows = data["model"]
    paper_rows = data["paper"]

    fig, ax = plt.subplots(figsize=(6.1, 5.9))
    fig.subplots_adjust(left=0.08, right=0.98, top=0.98, bottom=0.18)
    _draw_ternary_axes(ax)
    _plot_tie_lines(ax, exp_rows, BLACK, "o", "Exp.", linestyle="-")
    valid_model_rows = _accepted_model_rows(model_rows)
    _plot_tie_lines(ax, valid_model_rows, RED, "o", "model ePC-SAFT", linestyle="--")
    _plot_formula_series(ax, paper_rows, "organic_formula", BLUE, "s", "paper ePC-SAFT", linestyle="-")
    _plot_feed_points(ax, feed_rows, label="Feed")
    ax.legend(loc="upper right", fontsize=8)
    if valid_model_rows:
        model_caption = f"red dashed (package public ePC-SAFT, {len(valid_model_rows)}/{len(model_rows)} tie-lines)"
    else:
        model_caption = "package public ePC-SAFT rejected all model tie-lines; no red model tie-lines are drawn"
    paper_caption = f"blue squares (paper ePC-SAFT organic branch, {len(paper_rows)} points)"
    add_figure_caption(
        fig,
        f"Figure {figure_number}. LLE for the system water + ethanol + isobutanol + {int(round(salt_wt * 100))} wt % NaCl at {temperature_k:.2f} K and atmospheric pressure expressed as salt-free composition: black (exp), {model_caption}, {paper_caption}, and green (feed compositions).",
    )
    save_figure(fig, fig_dir / f"{figure_id_for_number(figure_number)}.png")
    plt.close(fig)


def _no_salt_source_rows() -> list[dict]:
    rows = []
    for idx, item in enumerate(NO_SALT_293_TRACE, start=1):
        x2_aq = float(item["x_ethanol_aq"])
        x3_aq = float(item["x_isobutanol_aq"])
        x1_aq = 1.0 - x2_aq - x3_aq
        D = float(item["distribution"])
        S = float(item["separation"])
        x2_org = D * x2_aq
        x1_org = x1_aq * D / S
        x3_org = max(1.0 - x1_org - x2_org, 1.0e-6)
        org = np.asarray([x1_org, x2_org, x3_org, 0.0], dtype=float)
        org = org / np.sum(org)
        aq = np.asarray([x1_aq, x2_aq, x3_aq, 0.0], dtype=float)
        aq = aq / np.sum(aq)
        rows.append(
            {
                "tie_line": idx,
                "temperature_K": 293.15,
                "salt_wtfrac": 0.0,
                "organic_formula": org,
                "aqueous_formula": aq,
            }
        )
    return rows


def _write_figure_1_contract_outputs(
    fig_dir: Path, no_salt_rows: list[dict], five_rows: list[dict], ten_rows: list[dict]
) -> None:
    all_rows = [
        ("without_nacl", no_salt_rows, "published_figure_trace"),
        ("with_5wt_nacl", five_rows, "paper_table"),
        ("with_10wt_nacl", ten_rows, "paper_table"),
    ]
    plotted_rows: list[dict] = []
    source_rows: list[dict] = []
    model_rows: list[dict] = []
    for series, rows, source in all_rows:
        plotted_rows.extend(_phase_plot_rows("source", series, rows, source))
        model_rows.extend(_phase_rows_for_csv(rows, source))
        for row in rows:
            for phase, x in (("organic", row["organic_formula"]), ("aqueous", row["aqueous_formula"])):
                source_rows.append(
                    {
                        "dataset": series,
                        "series": series,
                        "point_id": "",
                        "tie_line": row["tie_line"],
                        "phase": phase,
                        "temperature_K": row["temperature_K"],
                        "salt_wtfrac": row["salt_wtfrac"],
                        "x_water": float(x[0]),
                        "x_ethanol": float(x[1]),
                        "x_isobutanol": float(x[2]),
                        "x_nacl": float(x[3]),
                        "x_water_salt_free": "",
                        "x_ethanol_salt_free": "",
                        "x_isobutanol_salt_free": "",
                        "source_method": source,
                        "source_reference": "shared/source/table_3_4_experimental_tielines.csv"
                        if source == "paper_table"
                        else "published Figure 1 trace retained in source_points.csv",
                    }
                )
    write_csv_rows(result_path(fig_dir, "model_curve.csv"), PHASE_COLUMNS, model_rows)
    write_csv_rows(result_path(fig_dir, "plotted_data.csv"), PLOT_POINT_COLUMNS, plotted_rows)
    _write_source_points(fig_dir, source_rows)
    _write_source_notes(
        fig_dir,
        [
            {"section": "provenance", "key": "paper", "value": "Khudaida 2026", "unit": "", "notes": ""},
            {"section": "provenance", "key": "figure", "value": "figure_01", "unit": "", "notes": ""},
            {"section": "provenance", "key": "source_image", "value": "source/figure_01.png", "unit": "", "notes": ""},
            {"section": "basis", "key": "composition", "value": "salt-free ternary projection", "unit": "", "notes": ""},
            {
                "section": "model",
                "key": "route",
                "value": "source-data recreation",
                "unit": "",
                "notes": "Figure 1 is a source comparison of salt effects; the paper caption has no ePC-SAFT model curve.",
            },
            {
                "section": "model",
                "key": "package_route_scope",
                "value": "figures_02_07_and_s2_s3",
                "unit": "",
                "notes": "Public electrolyte_lle package-route evidence starts with the model-comparable Khudaida figures.",
            },
            {
                "section": "parameters",
                "key": "figiel_2025_snapshot",
                "value": "out_of_scope_for_figure_01_source_recreation",
                "unit": "",
                "notes": "Figure 1 does not consume fitted ePC-SAFT parameters because it reproduces the experimental salt-effect comparison only.",
            },
        ],
    )
    write_csv_rows(
        result_path(fig_dir, "fit_statistics.csv"),
        FIT_STATISTICS_COLUMNS,
        [
            {
                "scope": "figure",
                "series": "source_recreation",
                "temperature_K": 293.15,
                "salt_wtfrac": "0,0.05,0.10",
                "source_point_count": len(plotted_rows),
                "model_point_count": 0,
                "accepted_model_count": 0,
                "grand_aad": "",
                "organic_aad_water": "",
                "organic_aad_ethanol": "",
                "organic_aad_isobutanol": "",
                "organic_aad_nacl": "",
                "aqueous_aad_water": "",
                "aqueous_aad_ethanol": "",
                "aqueous_aad_isobutanol": "",
                "aqueous_aad_nacl": "",
                "max_objective": "",
                "normalized_plot_score": "",
                "pass": True,
                "score_basis": "source-data figure recreation; the paper caption has no ePC-SAFT model curve",
            }
        ],
    )


def plot_figure_1(fig_dir: Path) -> None:
    configure_style()
    no_salt_rows = _no_salt_source_rows()
    five_rows = _experimental_rows(0.05, 293.15)
    ten_rows = _experimental_rows(0.10, 293.15)
    fieldnames = [
        "tie_line",
        "phase",
        "temperature_K",
        "salt_wtfrac",
        "x_water",
        "x_ethanol",
        "x_isobutanol",
        "x_nacl",
        "source",
    ]
    write_csv_rows(
        out_path(fig_dir, "without_nacl_29315.csv"),
        fieldnames,
        _phase_rows_for_csv(no_salt_rows, "published_figure_trace"),
    )
    write_csv_rows(
        out_path(fig_dir, "with_5wt_nacl_29315.csv"), fieldnames, _phase_rows_for_csv(five_rows, "paper_table")
    )
    write_csv_rows(
        out_path(fig_dir, "with_10wt_nacl_29315.csv"), fieldnames, _phase_rows_for_csv(ten_rows, "paper_table")
    )
    _write_figure_1_contract_outputs(fig_dir, no_salt_rows, five_rows, ten_rows)

    fig, ax = plt.subplots(figsize=(6.1, 5.9))
    fig.subplots_adjust(left=0.08, right=0.98, top=0.98, bottom=0.18)
    _draw_ternary_axes(ax)
    _plot_tie_lines(ax, no_salt_rows, BLACK, "o", "without NaCl", linestyle="-")
    _plot_tie_lines(ax, five_rows, RED, "o", "5 wt% NaCl", linestyle="-")
    _plot_tie_lines(ax, ten_rows, BLUE, "o", "10 wt% NaCl", linestyle="-")
    add_figure_caption(
        fig,
        "Figure 1. LLE for the system water + ethanol + isobutanol without and with NaCl at 293.15 K and atmospheric pressure expressed as salt-free composition: black (without NaCl), red (5 wt % NaCl), and blue (10 wt % NaCl).",
    )
    save_figure(fig, fig_dir / "figure_01.png")
    plt.close(fig)


def _metric_from_row(row: dict) -> dict:
    org = row["organic_formula"]
    aq = row["aqueous_formula"]
    distribution = float(org[1] / aq[1]) if aq[1] > 0.0 else np.nan
    separation = float((org[1] / aq[1]) / (org[0] / aq[0])) if aq[1] > 0.0 and org[0] > 0.0 else np.nan
    return {
        "temperature_K": row["temperature_K"],
        "salt_wtfrac": row["salt_wtfrac"],
        "x_ethanol_aq": float(aq[1]),
        "distribution": distribution,
        "separation": separation,
    }


def _metric_dataset() -> list[dict]:
    rows = []
    for salt_wt, temperature_k in sorted(source_experimental_cases()):
        for exp_row in _experimental_rows(salt_wt, temperature_k):
            rows.append({**_metric_from_row(exp_row), "source": "paper_table"})
    for item in NO_SALT_293_TRACE:
        rows.append(
            {
                "temperature_K": 293.15,
                "salt_wtfrac": 0.0,
                "x_ethanol_aq": float(item["x_ethanol_aq"]),
                "distribution": float(item["distribution"]),
                "separation": float(item["separation"]),
                "source": "published_figure_trace",
            }
        )
    rows.sort(key=lambda item: (item["temperature_K"], item["salt_wtfrac"], item["x_ethanol_aq"]))
    return rows


def _metric_color(temperature_k: float) -> str:
    if abs(temperature_k - 293.15) < 1e-6:
        return BLACK
    if abs(temperature_k - 303.15) < 1e-6:
        return RED
    return BLUE


def _metric_marker(salt_wt: float) -> str:
    if salt_wt <= 1e-12:
        return "s"
    if abs(salt_wt - 0.05) < 1e-9:
        return "o"
    return "^"


def _write_metric_contract_outputs(fig_dir: Path, figure_number: int, rows: list[dict], y_key: str) -> None:
    figure_id = figure_id_for_number(figure_number)
    fields = ["temperature_K", "salt_wtfrac", "x_ethanol_aq", "distribution", "separation", "source"]
    source_rows = [
        {
            "dataset": "source_metric",
            "series": y_key,
            "point_id": idx,
            "tie_line": "",
            "phase": "aqueous",
            "temperature_K": row["temperature_K"],
            "salt_wtfrac": row["salt_wtfrac"],
            "x_water": "",
            "x_ethanol": "",
            "x_isobutanol": "",
            "x_nacl": "",
            "x_water_salt_free": "",
            "x_ethanol_salt_free": row["x_ethanol_aq"],
            "x_isobutanol_salt_free": "",
            "source_method": row["source"],
            "source_reference": "shared/source/table_s1_s2_distribution_separation.csv"
            if float(row["salt_wtfrac"]) > 0.0
            else "published Figure 8/9 trace retained in source_points.csv",
        }
        for idx, row in enumerate(rows, start=1)
    ]
    write_csv_rows(result_path(fig_dir, "model_curve.csv"), fields, rows)
    write_csv_rows(result_path(fig_dir, "plotted_data.csv"), fields, rows)
    _write_source_points(fig_dir, source_rows)
    _write_source_notes(
        fig_dir,
        [
            {"section": "provenance", "key": "paper", "value": "Khudaida 2026", "unit": "", "notes": ""},
            {"section": "provenance", "key": "figure", "value": figure_id, "unit": "", "notes": ""},
            {"section": "provenance", "key": "source_image", "value": f"source/{figure_id}.png", "unit": "", "notes": ""},
            {"section": "basis", "key": "x_axis", "value": "ethanol mole fraction in aqueous phase", "unit": "mole fraction", "notes": ""},
            {"section": "basis", "key": "y_axis", "value": y_key, "unit": "", "notes": "source metric from table rows and retained no-salt trace"},
        ],
    )
    write_csv_rows(
        result_path(fig_dir, "fit_statistics.csv"),
        FIT_STATISTICS_COLUMNS,
        [
            {
                "scope": "figure",
                "series": y_key,
                "temperature_K": "293.15-313.15",
                "salt_wtfrac": "0,0.05,0.10",
                "source_point_count": len(rows),
                "model_point_count": 0,
                "accepted_model_count": 0,
                "grand_aad": "",
                "organic_aad_water": "",
                "organic_aad_ethanol": "",
                "organic_aad_isobutanol": "",
                "organic_aad_nacl": "",
                "aqueous_aad_water": "",
                "aqueous_aad_ethanol": "",
                "aqueous_aad_isobutanol": "",
                "aqueous_aad_nacl": "",
                "max_objective": "",
                "normalized_plot_score": "",
                "pass": True,
                "score_basis": "source metric recreation; package equilibrium model curve is not drawn in this figure",
            }
        ],
    )


def _plot_metric_figure(fig_dir: Path, figure_number: int, y_key: str, y_label: str, y_max: float) -> None:
    configure_style()
    rows = _metric_dataset()
    write_csv_rows(
        out_path(fig_dir, "metric_points.csv"),
        ["temperature_K", "salt_wtfrac", "x_ethanol_aq", "distribution", "separation", "source"],
        rows,
    )
    _write_metric_contract_outputs(fig_dir, figure_number, rows, y_key)

    fig, ax = plt.subplots(figsize=(6.0, 4.4))
    fig.subplots_adjust(left=0.13, right=0.98, top=0.97, bottom=0.24)
    for row in rows:
        ax.scatter(
            row["x_ethanol_aq"],
            row[y_key],
            color=_metric_color(row["temperature_K"]),
            marker=_metric_marker(row["salt_wtfrac"]),
            s=22,
            linewidths=0.6,
        )
    ax.set_xlim(0.0, 0.042)
    ax.set_ylim(0.0, y_max)
    ax.set_xlabel(r"$x$ ethanol in aqueous phase")
    ax.set_ylabel(y_label)
    if figure_number == 8:
        caption = "Figure 8. Separation factor of water over ethanol for the mixture water + ethanol + isobutanol + NaCl; black (293.15 K), red (303.15 K), blue (313.15 K), squares (without NaCl), circles (5 wt % NaCl), and triangles (10 wt % NaCl)."
    else:
        caption = "Figure 9. Distribution coefficient of ethanol over water of the mixture water + ethanol + isobutanol + NaCl; black (293.15 K), red (303.15 K), blue (313.15 K), squares (without NaCl), circles (5 wt % NaCl), and triangles (10 wt % NaCl)."
    add_figure_caption(fig, caption, left=0.13, y=0.02)
    save_figure(fig, fig_dir / f"{figure_id_for_number(figure_number)}.png")
    plt.close(fig)


def plot_figure_8(fig_dir: Path) -> None:
    _plot_metric_figure(fig_dir, 8, "separation", "Separation Factor", 260.0)


def plot_figure_9(fig_dir: Path) -> None:
    _plot_metric_figure(fig_dir, 9, "distribution", "Distribution Coefficient of Ethanol", 70.0)


def plot_figure_10(fig_dir: Path) -> None:
    configure_style()
    figure_id = "figure_10"
    source_image = source_path(fig_dir, f"{figure_id}.png")
    if not source_image.is_file():
        raise FileNotFoundError(source_image)
    source_rows = [
        {
            "dataset": "source_image",
            "series": "sigma_profile",
            "point_id": 1,
            "tie_line": "",
            "phase": "",
            "temperature_K": "",
            "salt_wtfrac": "",
            "x_water": "",
            "x_ethanol": "",
            "x_isobutanol": "",
            "x_nacl": "",
            "x_water_salt_free": "",
            "x_ethanol_salt_free": "",
            "x_isobutanol_salt_free": "",
            "source_method": "published_figure_image",
            "source_reference": "Khudaida 2026 main Figure 10",
        }
    ]
    _write_source_points(fig_dir, source_rows)
    _write_source_notes(
        fig_dir,
        [
            {"section": "provenance", "key": "paper", "value": "Khudaida 2026", "unit": "", "notes": ""},
            {"section": "provenance", "key": "figure", "value": figure_id, "unit": "", "notes": ""},
            {"section": "provenance", "key": "source_image", "value": f"source/{figure_id}.png", "unit": "", "notes": ""},
            {"section": "basis", "key": "figure_role", "value": "sigma profile source retention", "unit": "", "notes": "not an electrolyte LLE solve"},
        ],
    )
    write_csv_rows(result_path(fig_dir, "model_curve.csv"), list(source_rows[0].keys()), source_rows)
    write_csv_rows(result_path(fig_dir, "plotted_data.csv"), list(source_rows[0].keys()), source_rows)
    write_csv_rows(
        result_path(fig_dir, "fit_statistics.csv"),
        FIT_STATISTICS_COLUMNS,
        [
            {
                "scope": "figure",
                "series": "sigma_profile_source_image",
                "temperature_K": "",
                "salt_wtfrac": "",
                "source_point_count": 1,
                "model_point_count": 0,
                "accepted_model_count": 0,
                "grand_aad": "",
                "organic_aad_water": "",
                "organic_aad_ethanol": "",
                "organic_aad_isobutanol": "",
                "organic_aad_nacl": "",
                "aqueous_aad_water": "",
                "aqueous_aad_ethanol": "",
                "aqueous_aad_isobutanol": "",
                "aqueous_aad_nacl": "",
                "max_objective": "",
                "normalized_plot_score": "",
                "pass": True,
                "score_basis": "source-image retention for the paper sigma-profile figure; package electrolyte LLE validation is owned by Figures 2-7 and S2-S3",
            }
        ],
    )
    image = plt.imread(source_image)
    fig, ax = plt.subplots(figsize=(6.0, 4.8))
    ax.imshow(image)
    ax.axis("off")
    ax.set_title("Khudaida 2026 Figure 10 sigma profile", fontsize=11)
    save_figure(fig, fig_dir / f"{figure_id}.png")
    plt.close(fig)


def _supporting_panel_rows(figure_number: int) -> list[dict]:
    rows = []
    for panel, main_figure, temperature_k, salt_wt in SUPPORTING_FIGURE_PANELS[figure_number]:
        exp_rows = _experimental_rows(salt_wt, temperature_k)
        feed_rows = _source_feed_rows_for_figure(main_figure, temperature_k, salt_wt) or _derived_feed_rows(
            salt_wt, temperature_k
        )
        main_fig_dir = figure_root(main_figure)
        model_rows = get_or_build_model_rows(main_fig_dir, exp_rows, feed_rows)
        paper_rows = _paper_epcsaft_source_rows(
            main_fig_dir, temperature_k, salt_wt
        )
        rows.append(
            {
                "panel": panel,
                "main_figure": main_figure,
                "temperature_K": temperature_k,
                "salt_wtfrac": salt_wt,
                "experimental": exp_rows,
                "feed": feed_rows,
                "model": model_rows,
                "paper": paper_rows,
            }
        )
    return rows


def write_supporting_figure_data(fig_dir: Path, figure_number: int) -> None:
    if figure_number not in SUPPORTING_FIGURE_PANELS:
        raise ValueError(f"Unsupported Khudaida supporting figure: S{figure_number}")
    phase_rows: list[dict] = []
    feed_rows_out: list[dict] = []
    for panel in _supporting_panel_rows(figure_number):
        for source, rows, phase_key in (
            ("experimental_table_3_4", panel["experimental"], None),
            ("package_public_native_electrolyte_lle", panel["model"], None),
            ("paper_epcsaft_source_curve", panel["paper"], "organic_formula"),
        ):
            for row in rows:
                if phase_key is not None:
                    phases = (("organic", row[phase_key]),)
                else:
                    phases = (("organic", row["organic_formula"]), ("aqueous", row["aqueous_formula"]))
                for phase, x in phases:
                    phase_rows.append(
                        {
                            "panel": panel["panel"],
                            "main_figure": panel["main_figure"],
                            "tie_line": row["tie_line"],
                            "phase": phase,
                            "temperature_K": panel["temperature_K"],
                            "salt_wtfrac": panel["salt_wtfrac"],
                            "x_water": float(x[0]),
                            "x_ethanol": float(x[1]),
                            "x_isobutanol": float(x[2]),
                            "x_nacl": float(x[3]),
                            "source": source,
                        }
                    )
        for row in panel["feed"]:
            x = row["feed_formula"]
            salt_free = salt_free_from_formula(x)
            feed_rows_out.append(
                {
                    "panel": panel["panel"],
                    "main_figure": panel["main_figure"],
                    "tie_line": row["tie_line"],
                    "temperature_K": panel["temperature_K"],
                    "salt_wtfrac": panel["salt_wtfrac"],
                    "x_water_total": float(x[0]),
                    "x_ethanol_total": float(x[1]),
                    "x_isobutanol_total": float(x[2]),
                    "x_nacl_total": float(x[3]),
                    "x_water_salt_free": float(salt_free[0]),
                    "x_ethanol_salt_free": float(salt_free[1]),
                    "x_isobutanol_salt_free": float(salt_free[2]),
                    "source": row["source"],
                }
            )
    write_csv_rows(
        out_path(fig_dir, f"{figure_id_for_number(_figure_number_from_dir(fig_dir))}_phase_points.csv"),
        [
            "panel",
            "main_figure",
            "tie_line",
            "phase",
            "temperature_K",
            "salt_wtfrac",
            "x_water",
            "x_ethanol",
            "x_isobutanol",
            "x_nacl",
            "source",
        ],
        phase_rows,
    )
    write_csv_rows(
        out_path(fig_dir, f"{figure_id_for_number(_figure_number_from_dir(fig_dir))}_feed_points.csv"),
        [
            "panel",
            "main_figure",
            "tie_line",
            "temperature_K",
            "salt_wtfrac",
            "x_water_total",
            "x_ethanol_total",
            "x_isobutanol_total",
            "x_nacl_total",
            "x_water_salt_free",
            "x_ethanol_salt_free",
            "x_isobutanol_salt_free",
            "source",
        ],
        feed_rows_out,
    )


def _write_supporting_contract_outputs(fig_dir: Path, supporting_number: int, panel_rows: list[dict]) -> None:
    figure_number = _figure_number_from_dir(fig_dir)
    figure_id = figure_id_for_number(figure_number)
    model_rows_out: list[dict] = []
    plotted_rows: list[dict] = []
    source_rows: list[dict] = []
    fit_rows: list[dict] = []
    for panel in panel_rows:
        panel_id = panel["panel"]
        exp_rows = panel["experimental"]
        model_rows = panel["model"]
        paper_rows = panel["paper"]
        feed_rows = panel["feed"]
        model_rows_out.extend(
            {
                **row,
                "source": csv_row["source"],
            }
            for csv_row in _model_rows_for_csv(model_rows)
            for row in [csv_row]
        )
        plotted_rows.extend(
            [
                *_phase_plot_rows("source", f"panel_{panel_id}_experimental", exp_rows, "paper_table"),
                *_phase_plot_rows(
                    "model",
                    f"panel_{panel_id}_package_electrolyte_lle",
                    model_rows,
                    "epcsaft_public_electrolyte_lle",
                ),
                *_organic_series_plot_rows("source", f"panel_{panel_id}_paper_epcsaft_organic", paper_rows, "published_figure_trace"),
                *_feed_plot_rows(feed_rows),
            ]
        )
        for row in _source_rows_for_lle_figure(
            exp_rows,
            feed_rows,
            paper_rows,
            f"analyses/paper_validation/2026_khudaida/figures/{figure_id}/source/source_points.csv",
        ):
            source_rows.append({**row, "series": f"panel_{panel_id}_{row['series']}"})
        valid = _accepted_model_rows(model_rows)
        summary = _aad_summary(exp_rows, model_rows)
        metrics = _fit_error_metrics(exp_rows, model_rows)
        failures = _model_failure_summary(model_rows, include_objectives=not _summary_passes(summary))
        max_objective = max((float(row["objective"]) for row in valid if np.isfinite(row["objective"])), default="")
        fit_rows.append(
            _fit_statistics_row(
                "panel",
                f"panel_{panel_id}_package_electrolyte_lle_vs_experimental",
                panel["temperature_K"],
                panel["salt_wtfrac"],
                len(exp_rows) * 2,
                len(model_rows) * 2,
                len(valid) * 2,
                summary,
                max_objective,
                "formula-basis mean absolute phase-composition deviation against source tie-lines",
                metrics["rmse"],
                metrics["max_abs_error"],
                failures["failed_tie_lines"],
                failures["failure_reasons"],
            )
        )
    write_csv_rows(result_path(fig_dir, "model_curve.csv"), MODEL_COLUMNS, model_rows_out)
    write_csv_rows(result_path(fig_dir, "plotted_data.csv"), PLOT_POINT_COLUMNS, plotted_rows)
    write_csv_rows(result_path(fig_dir, "fit_statistics.csv"), FIT_STATISTICS_COLUMNS, fit_rows)
    _write_source_points(fig_dir, source_rows)
    _write_source_notes(
        fig_dir,
        [
            {"section": "provenance", "key": "paper", "value": "Khudaida 2026 Supporting Information", "unit": "", "notes": ""},
            {"section": "provenance", "key": "figure", "value": f"Figure S{supporting_number}", "unit": "", "notes": figure_id},
            {"section": "provenance", "key": "source_image", "value": f"source/{figure_id}.png", "unit": "", "notes": ""},
            {"section": "basis", "key": "composition", "value": "salt-free ternary projection with NaCl retained in source/model CSV rows", "unit": "", "notes": ""},
            {"section": "model", "key": "route", "value": "public electrolyte_lle", "unit": "", "notes": "three-panel retained package/source comparison"},
            {
                "section": "parameters",
                "key": "parameter_dataset",
                "value": PARAMETER_DATASET.relative_to(REPO_ROOT).as_posix(),
                "unit": "",
                "notes": "retained 2026_Khudaida Tables 5-7 parameter bundle for public-route validation",
            },
            {
                "section": "parameters",
                "key": "figiel_2025_ssm_ds_born_options",
                "value": "retained_in_2026_Khudaida",
                "unit": "",
                "notes": "Figiel 2025 SSM+DS/Born option family is carried by the Khudaida parameter bundle",
            },
        ],
    )


def plot_supporting_figure_grid(fig_dir: Path, figure_number: int) -> None:
    configure_style()
    panel_rows = _supporting_panel_rows(figure_number)
    write_supporting_figure_data(fig_dir, figure_number)
    _write_supporting_contract_outputs(fig_dir, figure_number, panel_rows)
    fig, axes = plt.subplots(1, 3, figsize=(14.0, 4.9))
    fig.subplots_adjust(left=0.04, right=0.99, top=0.88, bottom=0.18, wspace=0.18)
    for ax, panel in zip(axes, panel_rows, strict=True):
        _draw_ternary_axes(ax)
        model_rows = [
            row
            for row in panel["model"]
            if np.all(np.isfinite(row["organic_formula"])) and np.all(np.isfinite(row["aqueous_formula"]))
        ]
        _plot_tie_lines(ax, panel["experimental"], BLACK, "o", "Exp.", linestyle="-")
        _plot_tie_lines(ax, _accepted_model_rows(model_rows), RED, "o", "package ePC-SAFT", linestyle="--")
        _plot_formula_series(ax, panel["paper"], "organic_formula", BLUE, "s", "paper ePC-SAFT", linestyle="-")
        _plot_feed_points(ax, panel["feed"], label="Feed", marker="^")
        ax.set_title(f"({panel['panel']}) {panel['temperature_K']:.2f} K", fontsize=10)
    axes[0].legend(loc="upper right", fontsize=7)
    salt_label = "5 wt % NaCl" if figure_number == 2 else "10 wt % NaCl"
    add_figure_caption(
        fig,
        f"Figure S{figure_number}. LLE for water + ethanol + isobutanol + {salt_label} at 293.15, 303.15, and 313.15 K: black (experimental), red dashed (package public electrolyte_lle solve), blue (paper ePC-SAFT), and green triangles (feed compositions).",
        left=0.04,
        y=0.02,
    )
    save_figure(fig, fig_dir / f"{figure_id_for_number(_figure_number_from_dir(fig_dir))}.png")
    plt.close(fig)


def _aad_summary(exp_rows: list[dict], model_rows: list[dict]) -> dict:
    valid = _accepted_model_rows(model_rows)
    if not valid:
        nan4 = (np.nan, np.nan, np.nan, np.nan)
        return {"organic": nan4, "aqueous": nan4, "grand": np.nan}
    exp_map = {row["tie_line"]: row for row in exp_rows}
    organic_delta = []
    aqueous_delta = []
    for row in valid:
        exp_row = exp_map[row["tie_line"]]
        organic_delta.append(np.abs(row["organic_formula"] - exp_row["organic_formula"]))
        aqueous_delta.append(np.abs(row["aqueous_formula"] - exp_row["aqueous_formula"]))
    organic_arr = np.vstack(organic_delta)
    aqueous_arr = np.vstack(aqueous_delta)
    grand = float((organic_arr.sum() + aqueous_arr.sum()) / (8.0 * organic_arr.shape[0]))
    return {
        "organic": tuple(np.mean(organic_arr, axis=0).tolist()),
        "aqueous": tuple(np.mean(aqueous_arr, axis=0).tolist()),
        "grand": grand,
    }


def _table_rows_for_png(salt_wt: float) -> list[list[str]]:
    rows = []
    temps = sorted({key[1] for key in source_experimental_cases() if abs(key[0] - salt_wt) < 1e-9})
    figure_number_map = {
        (0.05, 293.15): 2,
        (0.05, 303.15): 3,
        (0.05, 313.15): 4,
        (0.10, 293.15): 5,
        (0.10, 303.15): 6,
        (0.10, 313.15): 7,
    }
    force_recompute = os.environ.get("KHUDAIDA_FORCE_RECOMPUTE", "").strip().lower() in {"1", "true", "yes", "on"}
    for temperature_k in temps:
        exp_rows = _experimental_rows(salt_wt, temperature_k)
        feed_rows = _source_feed_rows_for_figure(
            figure_number_map[(salt_wt, temperature_k)], temperature_k, salt_wt
        ) or _derived_feed_rows(salt_wt, temperature_k)
        fig_dir = figure_root(figure_number_map[(salt_wt, temperature_k)])
        model_rows = get_or_build_model_rows(fig_dir, exp_rows, feed_rows=feed_rows, force_recompute=force_recompute)
        ours = _aad_summary(exp_rows, model_rows)
        paper_epc = EePCSAFT_AAD_REFERENCE[salt_wt][temperature_k]
        paper_enrtl = ENRTL_AAD_REFERENCE[salt_wt][temperature_k]
        for model_name, summary in (
            ("ePC-SAFT (package)", ours),
            ("ePC-SAFT (paper)", paper_epc),
            ("eNRTL (paper)", paper_enrtl),
        ):
            rows.append(
                [
                    f"{temperature_k:.2f}",
                    model_name,
                    f"{summary['organic'][0]:.4f}",
                    f"{summary['organic'][1]:.4f}",
                    f"{summary['organic'][2]:.4f}",
                    f"{summary['organic'][3]:.4f}",
                    f"{summary['aqueous'][0]:.4f}",
                    f"{summary['aqueous'][1]:.4f}",
                    f"{summary['aqueous'][2]:.4f}",
                    f"{summary['aqueous'][3]:.4f}",
                    f"{summary['grand']:.4f}",
                ]
            )
    return rows


def plot_tables_9_10(tables_root: Path) -> None:
    configure_style()
    columns = [
        "T / K",
        "Model",
        "Org x1",
        "Org x2",
        "Org x3",
        "Org x4",
        "Aq x1",
        "Aq x2",
        "Aq x3",
        "Aq x4",
        "Grand AAD",
    ]
    for table_number, salt_wt in ((9, 0.05), (10, 0.10)):
        table_dir = tables_root / f"table_{table_number:03d}" / "results"
        table_dir.mkdir(parents=True, exist_ok=True)
        rows = _table_rows_for_png(salt_wt)
        csv_rows = [dict(zip(columns, row)) for row in rows]
        write_csv_rows(out_path(table_dir, f"table_{table_number}.csv"), columns, csv_rows)
        fig, ax = plt.subplots(figsize=(13.0, 3.0 + 0.28 * len(rows)))
        ax.axis("off")
        table = ax.table(cellText=rows, colLabels=columns, loc="center", cellLoc="center")
        table.auto_set_font_size(False)
        table.set_fontsize(8)
        table.scale(1.0, 1.2)
        ax.set_title(
            f"Table {table_number}: AAD comparison for {int(round(salt_wt * 100))} wt% NaCl", fontsize=11, pad=12
        )
        save_figure(fig, table_dir / f"table_{table_number}.png")
        plt.close(fig)


def write_provenance_notes() -> None:
    notes = """# 2026 Khudaida analysis provenance

- Tables 3 and 4 in the local Khudaida markdown/PDF are treated as the canonical experimental tie-line source for Figures 2-7 and for the salted points in Figures 8-9.
- Analysis-owned source CSVs in `shared/source/` retain paper Tables 3-7 and Supporting Information Tables S1-S4. The runtime dataset `2026_Khudaida` uses the paper's Table 5 pure-component parameters, Table 6 dielectric constants, Table 7 binary interaction parameters, and the Figiel 2025 SSM+DS Born option family.
- Figures S2 and S3 are represented as three-panel figure-owned workflows that reuse the public non-reactive `electrolyte_lle` route and snapshot the exact plotted phase/feed points.
- Figure 1 salt-free data and the no-salt points in Figures 8-9 were reconstructed from the local paper figures because the Zotero baseline source remained inaccessible in this session.
- The no-salt baseline is therefore marked as `published_figure_trace` in the emitted CSV files.
- Tables 9 and 10 include package-generated ePC-SAFT AAD values and paper-copied eNRTL/ePC-SAFT reference values for comparison.
- The package model evidence is non-reactive electrolyte LLE through the public `electrolyte_lle` route with the `2026_Khudaida` Born SSM+DS dataset options.
- The current public-route regeneration is retained in `figures/figure_02` through `figure_07` under `results/data/model_tielines.csv`. The artifacts are complete, but the model-fit statistics do not pass the Khudaida source-data reproduction criteria.
"""
    path = ANALYSIS_ROOT / "docs" / "md" / "provenance_notes.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(notes, encoding="utf-8")
