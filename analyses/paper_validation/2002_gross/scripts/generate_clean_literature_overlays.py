from __future__ import annotations

import csv
import math
from collections import defaultdict
from pathlib import Path
from typing import Any, Callable

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[4]
ANALYSIS_ROOT = REPO_ROOT / "analyses" / "paper_validation" / "2002_gross"
FIGURES_ROOT = ANALYSIS_ROOT / "figures"
SHARED_RESULTS = ANALYSIS_ROOT / "shared" / "results"

MODEL_COLORS = [
    "#0b4f6c",
    "#b23a48",
    "#2f7d32",
    "#7b2cbf",
    "#d97706",
    "#0077b6",
    "#6a994e",
    "#9d4edd",
]
LITERATURE_COLORS = [
    "#111111",
    "#d00000",
    "#006d77",
    "#5a189a",
    "#9a031e",
    "#0a9396",
    "#ee9b00",
    "#3a0ca3",
]
SMOOTH_POINTS_PER_BRANCH = 320


CSV_FIELDS = [
    "figure_id",
    "dataset",
    "series",
    "source_role",
    "system",
    "source_reference",
    "source_detail",
    "T_K",
    "T_C",
    "P_bar",
    "P_kPa",
    "P_MPa",
    "x_axis",
    "y_axis",
    "x_axis_label",
    "y_axis_label",
    "x_liquid",
    "y_vapor",
    "x_component_1",
    "y_component_1",
    "x_benzene",
    "x_alcohol",
    "x_butane",
    "x_methanol",
    "y_methanol",
    "x_water",
    "x_1_pentanol",
    "point_index",
    "note",
]

def _figure_dirs(figure_id: str) -> tuple[Path, Path, Path]:
    figure_dir = FIGURES_ROOT / figure_id
    return figure_dir, figure_dir / "source", figure_dir / "results"


def _relative(path: Path) -> str:
    return path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()


def _write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str] = CSV_FIELDS) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fieldnames})


def _read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise FileNotFoundError(path)
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _float(row: dict[str, Any], key: str) -> float | None:
    value = row.get(key)
    if value in (None, ""):
        return None
    try:
        return float(value)
    except ValueError:
        return None


def _row(
    *,
    figure_id: str,
    dataset: str,
    series: str,
    source_role: str,
    system: str,
    source_reference: str,
    source_detail: str,
    x_axis: float,
    y_axis: float,
    x_axis_label: str,
    y_axis_label: str,
    point_index: int,
    note: str = "",
    **values: Any,
) -> dict[str, Any]:
    row = {
        "figure_id": figure_id,
        "dataset": dataset,
        "series": series,
        "source_role": source_role,
        "system": system,
        "source_reference": source_reference,
        "source_detail": source_detail,
        "x_axis": x_axis,
        "y_axis": y_axis,
        "x_axis_label": x_axis_label,
        "y_axis_label": y_axis_label,
        "point_index": point_index,
        "note": note,
    }
    row.update(values)
    return row


def _plot_series(
    ax: plt.Axes,
    rows: list[dict[str, Any]],
    *,
    dataset: str,
    linestyle: str,
    marker: str | None,
    linewidth: float,
    alpha: float,
    colors: list[str],
    marker_face: str | None = None,
    zorder: int = 2,
    include_legend: bool = True,
) -> None:
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[(str(row["series"]), str(row["source_role"]))].append(row)
    for index, ((series, source_role), group) in enumerate(sorted(grouped.items())):
        points = sorted(group, key=lambda item: float(item["x_axis"]))
        x_values = [float(item["x_axis"]) for item in points]
        y_values = [float(item["y_axis"]) for item in points]
        color = colors[index % len(colors)]
        label = _short_label(dataset, series, source_role) if include_legend else "_nolegend_"
        if marker_face is None:
            ax.plot(
                x_values,
                y_values,
                linestyle=linestyle,
                marker=marker,
                linewidth=linewidth,
                color=color,
                alpha=alpha,
                label=label,
                zorder=zorder,
            )
        else:
            ax.plot(
                x_values,
                y_values,
                linestyle=linestyle,
                marker=marker,
                linewidth=linewidth,
                color=color,
                markerfacecolor=marker_face,
                markeredgewidth=1.0,
                alpha=alpha,
                label=label,
                zorder=zorder,
            )


def _unique_xy(rows: list[dict[str, Any]]) -> tuple[np.ndarray, np.ndarray]:
    grouped: dict[float, list[float]] = defaultdict(list)
    for row in rows:
        grouped[float(row["x_axis"])].append(float(row["y_axis"]))
    x_values = np.asarray(sorted(grouped), dtype=float)
    y_values = np.asarray([float(np.mean(grouped[x])) for x in x_values], dtype=float)
    return x_values, y_values


def _pchip_values(x_values: np.ndarray, y_values: np.ndarray, dense_x: np.ndarray) -> np.ndarray:
    if x_values.size < 3:
        return np.interp(dense_x, x_values, y_values)

    h = np.diff(x_values)
    if np.any(h <= 0.0):
        return np.interp(dense_x, x_values, y_values)
    delta = np.diff(y_values) / h
    derivatives = np.zeros_like(y_values)

    for index in range(1, x_values.size - 1):
        left = delta[index - 1]
        right = delta[index]
        if left == 0.0 or right == 0.0 or np.sign(left) != np.sign(right):
            derivatives[index] = 0.0
            continue
        w1 = (2.0 * h[index]) + h[index - 1]
        w2 = h[index] + (2.0 * h[index - 1])
        derivatives[index] = (w1 + w2) / ((w1 / left) + (w2 / right))

    derivatives[0] = _pchip_endpoint_derivative(h[0], h[1], delta[0], delta[1])
    derivatives[-1] = _pchip_endpoint_derivative(h[-1], h[-2], delta[-1], delta[-2])

    segment_index = np.searchsorted(x_values, dense_x, side="right") - 1
    segment_index = np.clip(segment_index, 0, x_values.size - 2)
    x0 = x_values[segment_index]
    x1 = x_values[segment_index + 1]
    y0 = y_values[segment_index]
    y1 = y_values[segment_index + 1]
    d0 = derivatives[segment_index]
    d1 = derivatives[segment_index + 1]
    segment_h = x1 - x0
    t = (dense_x - x0) / segment_h

    h00 = (2.0 * t**3) - (3.0 * t**2) + 1.0
    h10 = t**3 - (2.0 * t**2) + t
    h01 = (-2.0 * t**3) + (3.0 * t**2)
    h11 = t**3 - t**2
    return h00 * y0 + h10 * segment_h * d0 + h01 * y1 + h11 * segment_h * d1


def _pchip_endpoint_derivative(h0: float, h1: float, delta0: float, delta1: float) -> float:
    derivative = (((2.0 * h0) + h1) * delta0 - h0 * delta1) / (h0 + h1)
    if derivative == 0.0 or delta0 == 0.0 or np.sign(derivative) != np.sign(delta0):
        return 0.0
    if np.sign(delta0) != np.sign(delta1) and abs(derivative) > abs(3.0 * delta0):
        return 3.0 * delta0
    return derivative


def _smooth_model_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[(str(row["series"]), str(row["source_role"]))].append(row)

    smooth_rows: list[dict[str, Any]] = []
    for (series, source_role), group in sorted(grouped.items()):
        if len(group) < 2:
            smooth_rows.extend(group)
            continue
        x_values, y_values = _unique_xy(group)
        if x_values.size < 2:
            smooth_rows.extend(group)
            continue
        dense_x = np.linspace(float(x_values.min()), float(x_values.max()), SMOOTH_POINTS_PER_BRANCH)
        dense_y = _pchip_values(x_values, y_values, dense_x)
        template = dict(group[0])
        for point_index, (x_axis, y_axis) in enumerate(zip(dense_x, dense_y), start=1):
            row = dict(template)
            row["dataset"] = "smooth_model_curve"
            row["series"] = series
            row["source_role"] = source_role
            row["source_detail"] = "shape-preserving cubic interpolation through current model points"
            row["x_axis"] = float(x_axis)
            row["y_axis"] = float(y_axis)
            row["point_index"] = point_index
            row["note"] = f"PCHIP-style smooth curve with {SMOOTH_POINTS_PER_BRANCH} points per branch"
            _sync_axis_columns(row)
            smooth_rows.append(row)
    return smooth_rows


def _sync_axis_columns(row: dict[str, Any]) -> None:
    x_axis = float(row["x_axis"])
    y_axis = float(row["y_axis"])
    if row.get("y_axis_label") == "P_bar":
        row["P_bar"] = y_axis
    elif row.get("y_axis_label") == "T_C":
        row["T_C"] = y_axis
        row["T_K"] = y_axis + 273.15

    x_label = str(row.get("x_axis_label", ""))
    if "benzene" in x_label:
        row["x_benzene"] = x_axis
    elif "butane" in x_label:
        row["x_butane"] = x_axis
    elif "methanol" in x_label and "vapor" in x_label and row.get("source_role") in {"dew_curve", "vle_dew_right"}:
        row["y_methanol"] = x_axis
    elif "methanol" in x_label:
        row["x_methanol"] = x_axis
    elif "water" in x_label:
        row["x_water"] = x_axis
        row["x_1_pentanol"] = 1.0 - x_axis


def _short_label(dataset: str, series: str, source_role: str) -> str:
    prefix = {
        "Current PC-SAFT": "model",
        "Literature table": "table",
        "Gross figure trace": "Gross trace",
    }.get(dataset, dataset)
    series_text = (
        series.replace("pressure_series_high", "101.3 kPa")
        .replace("pressure_series_low", "low P")
        .replace("bubble_line", "bubble")
        .replace("dew_line", "dew")
        .replace("bubble_curve", "bubble")
        .replace("dew_curve", "dew")
        .replace("lle_1_pentanol_rich", "pentanol-rich LLE")
        .replace("lle_water_rich", "water-rich LLE")
        .replace("upper_vle_curve", "upper VLE")
        .replace("vlle_tie_line", "VLLE tie")
        .replace("vle_bubble_left", "VLE bubble")
        .replace("vle_dew_right", "VLE dew")
        .replace("_", " ")
    )
    role_text = (
        source_role.replace("bubble_curve", "bubble")
        .replace("dew_curve", "dew")
        .replace("bubble_line", "bubble")
        .replace("dew_line", "dew")
        .replace("lle_1_pentanol_rich", "pentanol-rich LLE")
        .replace("lle_water_rich", "water-rich LLE")
        .replace("upper_vle_curve", "upper VLE")
        .replace("vlle_tie_line", "VLLE tie")
        .replace("_", " ")
    )
    if role_text and role_text != series_text:
        return f"{prefix} {series_text} {role_text}"
    return f"{prefix} {series_text}"


def _render_figure(
    *,
    figure_id: str,
    title: str,
    xlabel: str,
    ylabel: str,
    model_rows: list[dict[str, Any]],
    literature_rows: list[dict[str, Any]],
    xlim: tuple[float, float] = (0.0, 1.0),
    ylim: tuple[float, float] | None = None,
) -> None:
    _, _, results_dir = _figure_dirs(figure_id)
    png = results_dir / f"{figure_id}.png"
    svg = results_dir / f"{figure_id}.svg"
    pdf = results_dir / f"{figure_id}.pdf"

    fig, ax = plt.subplots(figsize=(8.8, 5.2), constrained_layout=True)
    ax.set_title(title, fontsize=12, pad=8)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_xlim(*xlim)
    if ylim is not None:
        ax.set_ylim(*ylim)
    ax.grid(True, color="#e5e7eb", linewidth=0.7)
    ax.set_axisbelow(True)

    if model_rows:
        _plot_series(
            ax,
            model_rows,
            dataset="Current PC-SAFT",
            linestyle="-",
            marker=None,
            linewidth=1.8,
            alpha=0.92,
            colors=MODEL_COLORS,
            zorder=2,
        )
    if literature_rows:
        _plot_series(
            ax,
            literature_rows,
            dataset="Literature table",
            linestyle="",
            marker="o",
            linewidth=0.0,
            alpha=0.96,
            colors=LITERATURE_COLORS,
            marker_face="white",
            zorder=3,
        )

    handles, labels = ax.get_legend_handles_labels()
    if handles:
        ax.legend(
            handles,
            labels,
            loc="upper left",
            bbox_to_anchor=(1.01, 1.0),
            fontsize=7,
            frameon=True,
            framealpha=0.92,
            borderpad=0.45,
            handlelength=2.2,
        )
    png.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(png, dpi=220)
    fig.savefig(svg)
    fig.savefig(pdf)
    plt.close(fig)



def _interp_pressure(points: list[tuple[float, float]], target_t_k: float) -> float | None:
    ordered = sorted(points)
    temps = np.asarray([item[0] for item in ordered], dtype=float)
    pressures = np.asarray([item[1] for item in ordered], dtype=float)
    if target_t_k < float(temps.min()) or target_t_k > float(temps.max()):
        return None
    return float(np.interp(target_t_k, temps, pressures))


def _nearest_branch_stats(
    figure_id: str,
    model_rows: list[dict[str, Any]],
    literature_rows: list[dict[str, Any]],
    *,
    y_unit: str,
) -> dict[str, Any]:
    grouped_model: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in model_rows:
        grouped_model[(str(row["series"]), str(row["source_role"]))].append(row)

    residuals: list[float] = []
    matched = 0
    skipped = 0
    for lit in literature_rows:
        key = (str(lit["series"]), str(lit["source_role"]))
        branch = grouped_model.get(key)
        if not branch:
            skipped += 1
            continue
        points = sorted((float(item["x_axis"]), float(item["y_axis"])) for item in branch)
        x_values = np.asarray([point[0] for point in points], dtype=float)
        y_values = np.asarray([point[1] for point in points], dtype=float)
        x = float(lit["x_axis"])
        if x < float(x_values.min()) or x > float(x_values.max()):
            skipped += 1
            continue
        predicted = float(np.interp(x, x_values, y_values))
        residuals.append(float(lit["y_axis"]) - predicted)
        matched += 1

    abs_residuals = [abs(value) for value in residuals]
    if abs_residuals:
        mae = float(np.mean(abs_residuals))
        max_abs = float(np.max(abs_residuals))
        signed_bias = float(np.mean(residuals))
    else:
        mae = math.nan
        max_abs = math.nan
        signed_bias = math.nan
    y_values = [float(row["y_axis"]) for row in literature_rows]
    y_range = max(y_values) - min(y_values) if len(y_values) >= 2 else math.nan
    normalized_mae = mae / y_range if y_range and not math.isnan(mae) else math.nan
    return {
        "figure_id": figure_id,
        "matched_literature_points": matched,
        "skipped_literature_points": skipped,
        "mae": mae,
        "max_abs": max_abs,
        "signed_bias": signed_bias,
        "normalized_mae": normalized_mae,
        "y_unit": y_unit,
    }


def _write_figure_outputs(
    *,
    figure_id: str,
    title: str,
    xlabel: str,
    ylabel: str,
    literature_rows: list[dict[str, Any]],
    model_rows: list[dict[str, Any]],
    sources: list[str],
    pending: list[str],
    y_unit: str,
    xlim: tuple[float, float] = (-0.02, 1.02),
    ylim: tuple[float, float] | None = None,
) -> dict[str, Any]:
    _, source_dir, results_dir = _figure_dirs(figure_id)
    source_csv = source_dir / "literature_points.csv"
    plotted_csv = results_dir / "plotted_data.csv"
    smooth_model_rows = _smooth_model_rows(model_rows)

    _write_csv(source_csv, literature_rows)
    _write_csv(plotted_csv, [*smooth_model_rows, *literature_rows])
    _render_figure(
        figure_id=figure_id,
        title=title,
        xlabel=xlabel,
        ylabel=ylabel,
        model_rows=smooth_model_rows,
        literature_rows=literature_rows,
        xlim=xlim,
        ylim=ylim,
    )

    stats = _nearest_branch_stats(figure_id, smooth_model_rows, literature_rows, y_unit=y_unit)
    summary = {
        "figure_id": figure_id,
        "title": title,
        "artifact_png": _relative(results_dir / f"{figure_id}.png"),
        "artifact_svg": _relative(results_dir / f"{figure_id}.svg"),
        "artifact_pdf": _relative(results_dir / f"{figure_id}.pdf"),
        "literature_points_csv": _relative(source_csv),
        "plotted_data_csv": _relative(plotted_csv),
        "model_seed_rows": len(model_rows),
        "smooth_model_rows": len(smooth_model_rows),
        "source_trace_rows_plotted": 0,
        "literature_rows": len(literature_rows),
        "sources": sources,
        "pending_source_data": pending,
        "fit_statistics": stats,
    }
    return summary


def _figure_paths(figure_id: str) -> tuple[Path, Path]:
    _, _, results_dir = _figure_dirs(figure_id)
    return results_dir / "model_curve.csv", results_dir / "plotted_data.csv"


def _model_rows_from_csv(
    figure_id: str,
    converter: Callable[[dict[str, str]], dict[str, Any] | None],
) -> list[dict[str, Any]]:
    model_path, _ = _figure_paths(figure_id)
    rows: list[dict[str, Any]] = []
    for index, source_row in enumerate(_read_csv(model_path), start=1):
        converted = converter(source_row)
        if converted is not None:
            converted["point_index"] = index
            rows.append(converted)
    return rows


def _fig2_model(row: dict[str, str]) -> dict[str, Any] | None:
    figure_id = "figure_02"
    series = row["series"]
    if series == "bubble_line":
        x_axis = _float(row, "x_component_1")
    elif series == "dew_line":
        x_axis = _float(row, "y_component_1")
    else:
        return None
    y_axis = _float(row, "P_bar")
    if x_axis is None or y_axis is None:
        return None
    return _row(
        figure_id=figure_id,
        dataset="current_model",
        series=series,
        source_role=series,
        system="methanol/isobutane",
        source_reference="Current ePC-SAFT Figure 2 replication model curve",
        source_detail="regenerated model curve",
        x_axis=x_axis,
        y_axis=y_axis,
        x_axis_label="x or y isobutane",
        y_axis_label="P_bar",
        point_index=0,
        T_K=_float(row, "T_K"),
        P_bar=y_axis,
        x_component_1=x_axis if series == "bubble_line" else "",
        y_component_1=x_axis if series == "dew_line" else "",
    )


def _fig2_literature() -> list[dict[str, Any]]:
    data = [
        (0.3470, 0.0000, 0.0000),
        (0.5965, 0.0143, 0.4329),
        (1.3380, 0.0914, 0.7349),
        (1.8430, 0.2542, 0.8021),
        (2.0410, 0.4290, 0.8397),
        (2.1190, 0.6730, 0.8537),
        (2.1800, 0.8595, 0.8794),
    ]
    rows: list[dict[str, Any]] = []
    for index, (p_mpa, x_isobutane, y_isobutane) in enumerate(data, start=1):
        p_bar = p_mpa * 10.0
        rows.append(
            _row(
                figure_id="figure_02",
                dataset="literature_table",
                series="bubble_line",
                source_role="bubble_line",
                system="methanol/isobutane",
                source_reference="Leu and Robinson 1992 Table I",
                source_detail="methanol(1)-isobutane(2), T=100 C, columns p/MPa and x2",
                x_axis=x_isobutane,
                y_axis=p_bar,
                x_axis_label="x isobutane",
                y_axis_label="P_bar",
                point_index=index,
                T_K=373.15,
                T_C=100.0,
                P_bar=p_bar,
                P_MPa=p_mpa,
                x_component_1=x_isobutane,
            )
        )
        rows.append(
            _row(
                figure_id="figure_02",
                dataset="literature_table",
                series="dew_line",
                source_role="dew_line",
                system="methanol/isobutane",
                source_reference="Leu and Robinson 1992 Table I",
                source_detail="methanol(1)-isobutane(2), T=100 C, columns p/MPa and y2",
                x_axis=y_isobutane,
                y_axis=p_bar,
                x_axis_label="y isobutane",
                y_axis_label="P_bar",
                point_index=index,
                T_K=373.15,
                T_C=100.0,
                P_bar=p_bar,
                P_MPa=p_mpa,
                y_component_1=y_isobutane,
            )
        )
    return rows


def _fig3_model(row: dict[str, str]) -> dict[str, Any] | None:
    figure_id = "figure_03"
    role = row["source_role"]
    x_axis = _float(row, "x_1_propanol" if role == "bubble_curve" else "y_1_propanol")
    y_axis = _float(row, "T_C")
    if x_axis is None or y_axis is None:
        return None
    return _row(
        figure_id=figure_id,
        dataset="current_model",
        series=row["series"],
        source_role=role,
        system="1-propanol/ethylbenzene",
        source_reference="Current ePC-SAFT Figure 3 replication model curve",
        source_detail="regenerated model curve",
        x_axis=x_axis,
        y_axis=y_axis,
        x_axis_label="x or y 1-propanol",
        y_axis_label="T_C",
        point_index=0,
        T_C=y_axis,
        T_K=_float(row, "T_K"),
        P_bar=_float(row, "P_bar"),
        x_alcohol=x_axis if role == "bubble_curve" else "",
        y_vapor=x_axis if role == "dew_curve" else "",
    )


def _fig3_literature() -> list[dict[str, Any]]:
    data = [
        (392.05, 0.067, 0.413),
        (389.45, 0.087, 0.466),
        (386.45, 0.116, 0.527),
        (383.35, 0.144, 0.584),
        (381.55, 0.176, 0.609),
        (378.95, 0.224, 0.655),
        (377.15, 0.277, 0.683),
        (375.95, 0.320, 0.701),
        (374.95, 0.372, 0.720),
        (374.05, 0.425, 0.735),
        (373.15, 0.495, 0.755),
        (372.55, 0.544, 0.768),
        (371.95, 0.599, 0.783),
        (371.45, 0.664, 0.802),
        (371.15, 0.714, 0.819),
        (370.75, 0.759, 0.835),
        (370.75, 0.771, 0.841),
        (370.35, 0.867, 0.889),
        (370.25, 0.912, 0.920),
        (370.15, 0.942, 0.944),
    ]
    rows: list[dict[str, Any]] = []
    for index, (t_k, x_1_propanol, y_1_propanol) in enumerate(data, start=1):
        t_c = t_k - 273.15
        for series, role, composition in [
            ("pressure_series_high", "bubble_curve", x_1_propanol),
            ("pressure_series_high", "dew_curve", y_1_propanol),
        ]:
            rows.append(
                _row(
                    figure_id="figure_03",
                    dataset="literature_table",
                    series=series,
                    source_role=role,
                    system="1-propanol/ethylbenzene",
                    source_reference="Goral et al. 2004 Table 3.9",
                    source_detail="recommended VLE data, P=101.32 kPa, Ref. Ellis and Froome 1954",
                    x_axis=composition,
                    y_axis=t_c,
                    x_axis_label="x or y 1-propanol",
                    y_axis_label="T_C",
                    point_index=index,
                    T_K=t_k,
                    T_C=t_c,
                    P_bar=1.0132,
                    P_kPa=101.32,
                    x_alcohol=composition if role == "bubble_curve" else "",
                    y_vapor=composition if role == "dew_curve" else "",
                )
            )
    return rows


def _fig4_model(row: dict[str, str]) -> dict[str, Any] | None:
    figure_id = "figure_04"
    series = row["series"]
    if series == "bubble_line":
        x_alcohol = _float(row, "x_1_pentanol")
    elif series == "dew_line":
        x_alcohol = _float(row, "y_1_pentanol")
    else:
        return None
    y_axis = _float(row, "P_bar")
    if x_alcohol is None or y_axis is None:
        return None
    x_axis = 1.0 - x_alcohol
    return _row(
        figure_id=figure_id,
        dataset="current_model",
        series=series,
        source_role=series,
        system="1-pentanol/benzene",
        source_reference="Current ePC-SAFT Figure 4 replication model curve",
        source_detail="regenerated model curve",
        x_axis=x_axis,
        y_axis=y_axis,
        x_axis_label="x or y benzene",
        y_axis_label="P_bar",
        point_index=0,
        T_K=_float(row, "T_K"),
        P_bar=y_axis,
        x_benzene=x_axis,
        x_alcohol=x_alcohol,
    )


def _fig4_literature() -> list[dict[str, Any]]:
    data = [
        (0.0000, 0.899),
        (0.0266, 2.520),
        (0.0576, 4.294),
        (0.0975, 6.395),
        (0.1482, 8.797),
        (0.1977, 10.868),
        (0.2479, 12.692),
        (0.2977, 14.267),
        (0.3480, 15.648),
        (0.3981, 16.834),
        (0.4486, 17.862),
        (0.4988, 18.755),
        (0.5488, 19.530),
        (0.5493, 19.516),
        (0.5990, 20.182),
        (0.6492, 20.779),
        (0.6984, 21.301),
        (0.7492, 21.826),
        (0.7993, 22.311),
        (0.8497, 22.770),
        (0.8990, 23.200),
        (0.9394, 23.589),
        (0.9695, 23.980),
        (1.0000, 24.509),
    ]
    return [
        _row(
            figure_id="figure_04",
            dataset="literature_table",
            series="bubble_line",
            source_role="bubble_line",
            system="1-pentanol/benzene",
            source_reference="Rhodes et al. 2001 Table 2",
            source_detail="total pressure data at T=313.15 K; x is benzene mole fraction",
            x_axis=x_benzene,
            y_axis=p_kpa / 100.0,
            x_axis_label="x benzene",
            y_axis_label="P_bar",
            point_index=index,
            T_K=313.15,
            T_C=40.0,
            P_bar=p_kpa / 100.0,
            P_kPa=p_kpa,
            x_benzene=x_benzene,
            x_alcohol=1.0 - x_benzene,
        )
        for index, (x_benzene, p_kpa) in enumerate(data, start=1)
    ]


def _fig5_model(row: dict[str, str]) -> dict[str, Any] | None:
    figure_id = "figure_05"
    role = row["source_role"]
    x_alcohol = _float(row, "x_alcohol" if role == "bubble_curve" else "y_alcohol")
    y_axis = _float(row, "P_bar")
    if x_alcohol is None or y_axis is None:
        return None
    x_axis = 1.0 - x_alcohol
    return _row(
        figure_id=figure_id,
        dataset="current_model",
        series=row["series"],
        source_role=role,
        system=row["system"],
        source_reference="Current ePC-SAFT Figure 5 replication model curve",
        source_detail="regenerated model curve",
        x_axis=x_axis,
        y_axis=y_axis,
        x_axis_label="x or y benzene",
        y_axis_label="P_bar",
        point_index=0,
        T_K=_float(row, "T_K"),
        P_bar=y_axis,
        x_benzene=x_axis,
        x_alcohol=x_alcohol,
    )


def _fig5_literature() -> list[dict[str, Any]]:
    one_propanol = [
        (0.0000, 7.047),
        (0.0295, 9.358),
        (0.0593, 11.418),
        (0.0993, 13.828),
        (0.1492, 16.300),
        (0.1992, 18.308),
        (0.2491, 19.913),
        (0.2993, 21.206),
        (0.3494, 22.214),
        (0.3995, 23.030),
        (0.4496, 23.686),
        (0.4997, 24.219),
        (0.4996, 24.273),
        (0.5496, 24.697),
        (0.5997, 25.049),
        (0.6495, 25.334),
        (0.6999, 25.583),
        (0.7498, 25.778),
        (0.8001, 25.942),
        (0.8500, 26.043),
        (0.9003, 26.069),
        (0.9402, 25.931),
        (0.9705, 25.554),
        (1.0000, 24.541),
    ]
    two_propanol = [
        (0.0000, 14.161),
        (0.0293, 16.356),
        (0.0602, 18.292),
        (0.1000, 20.400),
        (0.1495, 22.549),
        (0.1995, 24.262),
        (0.2494, 25.665),
        (0.2993, 26.722),
        (0.3496, 27.555),
        (0.3995, 28.230),
        (0.4496, 28.768),
        (0.4498, 28.712),
        (0.4997, 29.338),
        (0.5496, 29.574),
        (0.5998, 29.794),
        (0.6499, 29.946),
        (0.7001, 30.079),
        (0.7501, 30.175),
        (0.8002, 30.172),
        (0.8463, 30.020),
        (0.8982, 29.587),
        (0.9403, 28.799),
        (0.9704, 27.455),
        (1.0000, 24.341),
    ]
    rows: list[dict[str, Any]] = []
    for series, system, data in [
        ("1-propanol-benzene", "1-propanol/benzene", one_propanol),
        ("2-propanol-benzene", "2-propanol/benzene", two_propanol),
    ]:
        for index, (x_benzene, p_kpa) in enumerate(data, start=1):
            rows.append(
                _row(
                    figure_id="figure_05",
                    dataset="literature_table",
                    series=series,
                    source_role="bubble_curve",
                    system=system,
                    source_reference="Rhodes et al. 2001 Table 2",
                    source_detail="total pressure data at T=313.15 K; x is benzene mole fraction",
                    x_axis=x_benzene,
                    y_axis=p_kpa / 100.0,
                    x_axis_label="x benzene",
                    y_axis_label="P_bar",
                    point_index=index,
                    T_K=313.15,
                    T_C=40.0,
                    P_bar=p_kpa / 100.0,
                    P_kPa=p_kpa,
                    x_benzene=x_benzene,
                    x_alcohol=1.0 - x_benzene,
                )
            )
    return rows


def _isotherm_model_row(figure_id: str, system: str, row: dict[str, str]) -> dict[str, Any] | None:
    x_axis = _float(row, "x_butane")
    y_axis = _float(row, "P_bar")
    if x_axis is None or y_axis is None:
        return None
    return _row(
        figure_id=figure_id,
        dataset="current_model",
        series=row["series"],
        source_role=row["series"],
        system=system,
        source_reference=f"Current ePC-SAFT {figure_id} replication model curve",
        source_detail="regenerated model curve",
        x_axis=x_axis,
        y_axis=y_axis,
        x_axis_label="x n-butane",
        y_axis_label="P_bar",
        point_index=0,
        T_K=_float(row, "T_K"),
        P_bar=y_axis,
        x_butane=x_axis,
    )


DEAK_1_BUTANOL: dict[float, list[tuple[float, float]]] = {
    0.1019: [
        (333.01, 0.196),
        (342.92, 0.243),
        (352.96, 0.294),
        (362.99, 0.354),
        (373.02, 0.420),
        (383.21, 0.497),
        (393.17, 0.582),
        (403.10, 0.676),
        (413.27, 0.788),
        (423.18, 0.910),
        (433.12, 1.049),
        (443.09, 1.207),
        (453.07, 1.388),
        (463.06, 1.592),
        (473.02, 1.822),
        (482.97, 2.078),
        (493.06, 2.374),
        (503.03, 2.699),
        (513.12, 3.065),
    ],
    0.2007: [
        (333.11, 0.322),
        (343.12, 0.399),
        (353.14, 0.485),
        (363.20, 0.581),
        (373.14, 0.686),
        (383.19, 0.803),
        (393.17, 0.931),
        (403.20, 1.072),
        (413.23, 1.226),
        (423.28, 1.397),
        (433.26, 1.584),
        (443.19, 1.788),
        (453.15, 2.016),
        (462.41, 2.246),
        (472.37, 2.519),
        (482.31, 2.819),
        (492.29, 3.150),
        (502.29, 3.510),
        (512.49, 3.898),
    ],
    0.3354: [
        (333.24, 0.440),
        (343.30, 0.545),
        (353.30, 0.665),
        (363.26, 0.797),
        (373.28, 0.945),
        (383.30, 1.108),
        (393.27, 1.285),
        (403.37, 1.479),
        (413.37, 1.689),
        (423.37, 1.918),
        (433.36, 2.165),
        (443.36, 2.430),
        (453.33, 2.720),
        (463.35, 3.034),
        (473.27, 3.369),
        (483.23, 3.730),
        (493.23, 4.114),
        (503.23, 4.509),
        (508.24, 4.701),
    ],
    0.4174: [
        (333.22, 0.491),
        (343.28, 0.610),
        (353.25, 0.745),
        (363.26, 0.897),
        (373.27, 1.066),
        (383.26, 1.252),
        (393.29, 1.459),
        (403.35, 1.689),
        (413.38, 1.928),
        (423.36, 2.190),
        (433.35, 2.474),
        (443.36, 2.782),
        (453.36, 3.112),
        (463.33, 3.463),
        (473.30, 3.840),
        (483.25, 4.229),
        (493.25, 4.624),
        (498.22, 4.808),
        (503.23, 4.958),
        (508.21, 5.019),
        (508.93, 5.020),
    ],
    0.5018: [
        (333.26, 0.522),
        (343.24, 0.650),
        (353.24, 0.795),
        (363.31, 0.962),
        (373.28, 1.148),
        (383.25, 1.353),
        (393.31, 1.581),
        (403.36, 1.832),
        (413.34, 2.102),
        (423.34, 2.394),
        (433.33, 2.711),
        (443.37, 3.055),
        (453.30, 3.419),
        (463.31, 3.807),
        (473.28, 4.215),
        (483.26, 4.619),
        (488.24, 4.800),
        (493.28, 4.937),
        (496.24, 4.975),
        (497.24, 4.981),
    ],
    0.6072: [
        (333.48, 0.559),
        (342.84, 0.692),
        (353.18, 0.852),
        (363.23, 1.034),
        (373.17, 1.237),
        (383.23, 1.466),
        (393.16, 1.740),
        (403.19, 1.997),
        (413.16, 2.303),
        (423.23, 2.637),
        (433.21, 2.999),
        (443.19, 3.404),
        (453.22, 3.805),
        (463.09, 4.228),
        (468.19, 4.443),
        (473.21, 4.640),
        (477.58, 4.774),
        (481.22, 4.837),
    ],
    0.7065: [
        (333.65, 0.590),
        (343.08, 0.728),
        (353.10, 0.897),
        (363.26, 1.095),
        (373.21, 1.310),
        (383.15, 1.562),
        (393.20, 1.842),
        (403.15, 2.150),
        (413.27, 2.497),
        (423.25, 2.870),
        (433.51, 3.292),
        (442.46, 3.683),
        (452.45, 4.145),
        (457.42, 4.365),
        (462.41, 4.536),
        (464.78, 4.586),
    ],
    0.8114: [
        (333.25, 0.598),
        (343.20, 0.750),
        (353.26, 0.930),
        (363.26, 1.136),
        (373.28, 1.374),
        (383.27, 1.640),
        (393.27, 1.945),
        (403.36, 2.288),
        (413.37, 2.671),
        (423.36, 3.097),
        (433.33, 3.561),
        (443.40, 4.053),
        (448.33, 4.246),
        (449.06, 4.261),
    ],
    0.9031: [
        (333.24, 0.617),
        (343.26, 0.779),
        (353.26, 0.968),
        (363.27, 1.190),
        (373.30, 1.446),
        (383.29, 1.739),
        (393.33, 2.077),
        (403.36, 2.458),
        (413.39, 2.902),
        (423.37, 3.371),
        (428.35, 3.634),
        (433.35, 3.900),
        (435.20, 3.972),
    ],
}

DEAK_ETHANOL: dict[float, list[tuple[float, float]]] = {
    0.0905: [
        (323.21, 0.240),
        (328.23, 0.270),
        (338.22, 0.340),
        (348.23, 0.430),
        (358.26, 0.540),
        (368.24, 0.660),
        (378.36, 0.810),
        (388.06, 0.975),
        (398.01, 1.170),
        (408.08, 1.405),
        (417.91, 1.670),
        (427.81, 1.980),
        (437.70, 2.335),
        (447.43, 2.740),
        (457.23, 3.210),
        (465.81, 3.680),
        (477.22, 4.390),
        (486.60, 5.065),
        (500.32, 6.080),
    ],
    0.1510: [
        (343.21, 0.532),
        (353.25, 0.657),
        (363.21, 0.802),
        (373.25, 0.972),
        (383.21, 1.167),
        (393.22, 1.387),
        (403.29, 1.642),
        (413.28, 1.937),
        (423.29, 2.267),
        (433.25, 2.642),
        (443.23, 3.067),
        (453.26, 3.552),
        (463.24, 4.070),
        (473.20, 4.700),
        (483.24, 5.372),
        (491.22, 5.902),
        (492.23, 5.952),
        (493.23, 5.986),
        (494.12, 6.000),
    ],
    0.2436: [
        (323.24, 0.394),
        (333.24, 0.504),
        (343.20, 0.634),
        (345.63, 0.669),
        (353.24, 0.787),
        (363.26, 0.964),
        (373.25, 1.168),
        (383.22, 1.402),
        (393.21, 1.665),
        (403.29, 1.966),
        (413.29, 2.304),
        (423.26, 2.684),
        (433.25, 3.112),
        (443.25, 3.590),
        (453.25, 4.123),
        (463.23, 4.711),
        (473.22, 5.340),
        (478.25, 5.647),
        (482.18, 5.805),
        (482.79, 5.820),
    ],
    0.3316: [
        (323.27, 0.438),
        (333.25, 0.558),
        (343.23, 0.703),
        (345.64, 0.738),
        (353.26, 0.869),
        (363.25, 1.069),
        (373.28, 1.294),
        (383.23, 1.549),
        (393.26, 1.844),
        (403.28, 2.174),
        (413.34, 2.550),
        (423.30, 2.965),
        (433.31, 3.435),
        (443.28, 3.950),
        (453.28, 4.530),
        (458.26, 4.830),
        (463.28, 5.140),
        (468.27, 5.430),
        (470.25, 5.530),
        (473.06, 5.620),
    ],
    0.4381: [
        (323.23, 0.464),
        (333.21, 0.593),
        (343.23, 0.748),
        (345.60, 0.788),
        (353.19, 0.929),
        (363.22, 1.142),
        (373.23, 1.388),
        (383.19, 1.668),
        (393.24, 1.992),
        (403.30, 2.357),
        (413.15, 2.767),
        (423.26, 3.228),
        (433.30, 3.745),
        (443.28, 4.312),
        (448.27, 4.615),
        (453.23, 4.918),
        (458.23, 5.184),
        (460.21, 5.254),
    ],
    0.5118: [
        (323.23, 0.473),
        (333.23, 0.606),
        (343.24, 0.766),
        (345.62, 0.809),
        (353.24, 0.955),
        (363.28, 1.176),
        (373.28, 1.432),
        (383.26, 1.724),
        (393.21, 2.059),
        (403.27, 2.445),
        (413.30, 2.879),
        (423.27, 3.367),
        (433.28, 3.914),
        (448.23, 4.813),
        (452.26, 4.998),
        (452.43, 5.003),
    ],
    0.5842: [
        (323.26, 0.487),
        (333.25, 0.622),
        (343.25, 0.787),
        (345.64, 0.832),
        (353.26, 0.982),
        (363.28, 1.212),
        (373.28, 1.477),
        (383.23, 1.778),
        (393.22, 2.128),
        (403.32, 2.533),
        (413.33, 2.988),
        (423.29, 3.503),
        (438.31, 4.393),
        (443.27, 4.688),
        (445.28, 4.778),
        (445.50, 4.783),
    ],
    0.6698: [
        (323.22, 0.492),
        (333.23, 0.633),
        (343.23, 0.803),
        (345.63, 0.847),
        (353.25, 1.003),
        (363.28, 1.235),
        (373.24, 1.509),
        (383.23, 1.827),
        (393.23, 2.191),
        (403.30, 2.614),
        (413.34, 3.090),
        (423.29, 3.629),
        (428.32, 3.925),
        (433.28, 4.233),
        (435.30, 4.359),
        (437.29, 4.477),
        (438.40, 4.523),
    ],
    0.7735: [
        (323.23, 0.505),
        (333.23, 0.646),
        (343.23, 0.816),
        (345.62, 0.860),
        (353.26, 1.018),
        (363.28, 1.260),
        (373.24, 1.541),
        (383.22, 1.868),
        (393.27, 2.249),
        (403.27, 2.688),
        (413.29, 3.190),
        (423.26, 3.765),
        (428.27, 4.081),
        (430.19, 4.196),
    ],
    0.8451: [
        (323.24, 0.498),
        (333.25, 0.643),
        (343.24, 0.817),
        (345.66, 0.865),
        (353.31, 1.026),
        (363.30, 1.274),
        (373.29, 1.563),
        (383.28, 1.897),
        (393.30, 2.285),
        (403.37, 2.733),
        (413.35, 3.244),
        (418.36, 3.528),
        (423.36, 3.830),
        (426.26, 4.015),
    ],
    0.8974: [
        (323.26, 0.505),
        (323.72, 0.515),
        (333.25, 0.650),
        (343.26, 0.830),
        (345.64, 0.875),
        (353.24, 1.035),
        (363.22, 1.286),
        (373.24, 1.576),
        (383.21, 1.911),
        (393.23, 2.296),
        (403.31, 2.746),
        (413.33, 3.256),
        (418.28, 3.531),
        (420.31, 3.651),
        (423.32, 3.836),
        (424.85, 3.931),
        (425.22, 3.956),
    ],
    1.0: [
        (323.06, 0.510),
        (332.90, 0.640),
        (343.43, 0.820),
        (353.43, 1.025),
        (363.42, 1.260),
        (373.51, 1.540),
        (383.37, 1.860),
        (393.37, 2.230),
        (403.21, 2.640),
        (413.04, 3.115),
        (425.03, 3.782),
    ],
}


def _deak_isotherm_rows(
    *,
    figure_id: str,
    system: str,
    data: dict[float, list[tuple[float, float]]],
    targets: dict[str, float],
    source_reference: str,
    source_detail: str,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    point_index = 1
    for series, target_t_k in targets.items():
        for x_butane, table_points in sorted(data.items()):
            p_mpa = _interp_pressure(table_points, target_t_k)
            if p_mpa is None:
                continue
            p_bar = p_mpa * 10.0
            rows.append(
                _row(
                    figure_id=figure_id,
                    dataset="literature_table",
                    series=series,
                    source_role=series,
                    system=system,
                    source_reference=source_reference,
                    source_detail=source_detail,
                    x_axis=x_butane,
                    y_axis=p_bar,
                    x_axis_label="x n-butane",
                    y_axis_label="P_bar",
                    point_index=point_index,
                    T_K=target_t_k,
                    T_C=target_t_k - 273.15,
                    P_bar=p_bar,
                    P_MPa=p_mpa,
                    x_butane=x_butane,
                    note="linear interpolation of constant-composition Deak table values to the Gross 2002 isotherm",
                )
            )
            point_index += 1
    return rows


def _fig8_model(row: dict[str, str]) -> dict[str, Any] | None:
    figure_id = "figure_08"
    series = row["series"]
    if series == "vle_dew_right":
        x_axis = _float(row, "y_methanol")
    else:
        x_axis = _float(row, "x_methanol")
    y_axis = _float(row, "T_C")
    if x_axis is None or y_axis is None:
        return None
    return _row(
        figure_id=figure_id,
        dataset="current_model",
        series=series,
        source_role=series,
        system="methanol/cyclohexane",
        source_reference="Current ePC-SAFT Figure 8 replication model curve",
        source_detail="regenerated model curve",
        x_axis=x_axis,
        y_axis=y_axis,
        x_axis_label="x or y methanol",
        y_axis_label="T_C",
        point_index=0,
        T_C=y_axis,
        T_K=_float(row, "T_K"),
        P_bar=_float(row, "pressure_bar"),
        x_methanol=x_axis if series != "vle_dew_right" else "",
        y_methanol=x_axis if series == "vle_dew_right" else "",
    )


def _fig8_literature() -> list[dict[str, Any]]:
    data = [
        (0.0497, 0.5318, 58.30),
        (0.0715, 0.5746, 55.91),
        (0.0980, 0.6012, 55.00),
        (0.1641, 0.6036, 54.32),
        (0.2639, 0.6070, 54.05),
        (0.3451, 0.6049, 53.93),
        (0.4503, 0.6005, 53.88),
        (0.5509, 0.6007, 53.87),
        (0.6486, 0.6018, 53.92),
        (0.7465, 0.6026, 54.03),
        (0.8515, 0.6154, 54.40),
        (0.8922, 0.6355, 54.94),
        (0.9144, 0.6569, 55.52),
        (0.9291, 0.6775, 56.10),
        (0.9426, 0.7031, 56.94),
        (0.9601, 0.7514, 58.50),
        (0.9731, 0.8030, 59.50),
    ]
    rows: list[dict[str, Any]] = []
    for index, (x_methanol, y_methanol, t_c) in enumerate(data, start=1):
        for series, composition in [("vle_bubble_left", x_methanol), ("vle_dew_right", y_methanol)]:
            rows.append(
                _row(
                    figure_id="figure_08",
                    dataset="literature_table",
                    series=series,
                    source_role=series,
                    system="methanol/cyclohexane",
                    source_reference="Madhavan and Murti 1966 Table 3c",
                    source_detail="760 mm Hg isobaric methanol/cyclohexane VLE",
                    x_axis=composition,
                    y_axis=t_c,
                    x_axis_label="x or y methanol",
                    y_axis_label="T_C",
                    point_index=index,
                    T_C=t_c,
                    T_K=t_c + 273.15,
                    P_bar=1.01325,
                    x_methanol=composition if series == "vle_bubble_left" else "",
                    y_methanol=composition if series == "vle_dew_right" else "",
                )
            )
    return rows


def _fig9_model(row: dict[str, str]) -> dict[str, Any] | None:
    figure_id = "figure_09"
    role = row["source_role"]
    x_axis = _float(row, "x_methanol" if role == "bubble_curve" else "y_methanol")
    y_axis = _float(row, "T_C")
    if x_axis is None or y_axis is None:
        return None
    return _row(
        figure_id=figure_id,
        dataset="current_model",
        series=row["series"],
        source_role=role,
        system="methanol/1-octanol",
        source_reference="Current ePC-SAFT Figure 9 replication model curve",
        source_detail="regenerated model curve",
        x_axis=x_axis,
        y_axis=y_axis,
        x_axis_label="x or y methanol",
        y_axis_label="T_C",
        point_index=0,
        T_C=y_axis,
        T_K=_float(row, "T_K"),
        P_bar=_float(row, "pressure_bar"),
        x_methanol=x_axis if role == "bubble_curve" else "",
        y_methanol=x_axis if role == "dew_curve" else "",
    )


def _fig9_literature() -> list[dict[str, Any]]:
    data = [
        (0.0000, 0.0000, 467.85),
        (0.0032, 0.1564, 461.88),
        (0.0079, 0.3085, 455.06),
        (0.0127, 0.4072, 449.29),
        (0.0169, 0.5053, 444.51),
        (0.0242, 0.6062, 437.95),
        (0.0278, 0.6674, 433.78),
        (0.0419, 0.7691, 424.43),
        (0.0592, 0.8432, 414.68),
        (0.1002, 0.9109, 401.33),
        (0.1477, 0.9512, 388.40),
        (0.1635, 0.9632, 383.64),
        (0.2064, 0.9756, 377.25),
        (0.2646, 0.9848, 368.40),
        (0.3662, 0.9917, 360.18),
        (0.4390, 0.9937, 355.64),
        (0.5053, 0.9957, 352.24),
        (0.5823, 0.9968, 349.62),
        (0.6433, 0.9973, 347.13),
        (0.7358, 0.9979, 344.03),
        (0.8143, 0.9987, 341.99),
        (0.8978, 0.9990, 340.06),
        (0.9522, 0.9992, 338.87),
        (0.9819, 0.9995, 338.15),
        (1.0000, 1.0000, 337.75),
    ]
    rows: list[dict[str, Any]] = []
    for index, (x_methanol, y_methanol, t_k) in enumerate(data, start=1):
        t_c = t_k - 273.15
        for series, role, composition in [
            ("bubble_curve", "bubble_curve", x_methanol),
            ("dew_curve", "dew_curve", y_methanol),
        ]:
            rows.append(
                _row(
                    figure_id="figure_09",
                    dataset="literature_table",
                    series=series,
                    source_role=role,
                    system="methanol/1-octanol",
                    source_reference="Arce et al. 1995 Table 3",
                    source_detail="isobaric VLE at 101.32 kPa for methanol(1)/1-octanol(2)",
                    x_axis=composition,
                    y_axis=t_c,
                    x_axis_label="x or y methanol",
                    y_axis_label="T_C",
                    point_index=index,
                    T_K=t_k,
                    T_C=t_c,
                    P_bar=1.0132,
                    P_kPa=101.32,
                    x_methanol=composition if role == "bubble_curve" else "",
                    y_methanol=composition if role == "dew_curve" else "",
                )
            )
    return rows


def _fig10_model(row: dict[str, str]) -> dict[str, Any] | None:
    figure_id = "figure_10"
    x_axis = _float(row, "x_water")
    y_axis = _float(row, "T_C")
    if x_axis is None or y_axis is None:
        return None
    return _row(
        figure_id=figure_id,
        dataset="current_model",
        series=row["series"],
        source_role=row["series"],
        system="water/1-pentanol",
        source_reference="Current ePC-SAFT Figure 10 replication model curve",
        source_detail="retained Gross Figure 10 PC-SAFT trace",
        x_axis=x_axis,
        y_axis=y_axis,
        x_axis_label="x water",
        y_axis_label="T_C",
        point_index=0,
        T_K=_float(row, "T_K"),
        T_C=y_axis,
        P_bar=_float(row, "pressure_bar"),
        x_water=x_axis,
        x_1_pentanol=_float(row, "x_1_pentanol"),
    )


def _fig10_literature() -> list[dict[str, Any]]:
    water_rich = [
        (273.15, 7.00e-3),
        (283.15, 5.50e-3),
        (283.35, 5.40e-3),
        (288.20, 4.80e-3),
        (293.15, 4.60e-3),
        (293.35, 4.70e-3),
        (298.15, 4.50e-3),
        (303.15, 4.21e-3),
        (303.75, 4.20e-3),
        (310.20, 3.90e-3),
        (313.15, 3.90e-3),
        (313.35, 3.90e-3),
        (323.15, 3.80e-3),
        (333.15, 3.60e-3),
        (333.45, 3.80e-3),
        (343.15, 4.00e-3),
        (353.15, 4.10e-3),
        (358.15, 4.20e-3),
        (363.15, 4.10e-3),
        (363.85, 4.60e-3),
        (367.15, 4.20e-3),
        (368.15, 4.20e-3),
        (373.15, 4.70e-3),
        (383.15, 5.40e-3),
        (393.15, 6.30e-3),
        (403.15, 7.50e-3),
        (413.15, 9.20e-3),
        (423.15, 1.14e-2),
        (433.15, 1.49e-2),
        (443.15, 2.11e-2),
    ]
    alcohol_rich = [
        (273.15, 0.340),
        (283.15, 0.339),
        (283.35, 0.346),
        (285.15, 0.357),
        (288.15, 0.362),
        (292.10, 0.348),
        (293.15, 0.347),
        (293.35, 0.358),
        (298.15, 0.357),
        (298.70, 0.355),
        (302.15, 0.352),
        (303.15, 0.369),
        (303.75, 0.366),
        (305.15, 0.352),
        (308.15, 0.377),
        (309.15, 0.357),
        (313.15, 0.365),
        (313.35, 0.379),
        (314.65, 0.370),
        (323.15, 0.384),
        (323.20, 0.384),
        (329.15, 0.389),
        (333.15, 0.391),
        (339.15, 0.409),
        (343.15, 0.404),
        (346.65, 0.422),
        (353.15, 0.422),
        (358.15, 0.400),
        (359.65, 0.452),
        (363.15, 0.450),
        (363.85, 0.463),
        (368.15, 0.435),
        (368.45, 0.519),
        (368.95, 0.421),
        (373.15, 0.480),
        (383.15, 0.511),
        (393.15, 0.544),
        (403.15, 0.578),
        (413.15, 0.615),
        (423.15, 0.655),
        (433.15, 0.697),
        (443.15, 0.745),
    ]
    rows: list[dict[str, Any]] = []
    for index, (t_k, x_pentanol) in enumerate(water_rich, start=1):
        x_water = 1.0 - x_pentanol
        rows.append(
            _row(
                figure_id="figure_10",
                dataset="literature_table",
                series="lle_water_rich",
                source_role="lle_water_rich",
                system="water/1-pentanol",
                source_reference="Goral et al. 2006 Table 8",
                source_detail="recommended 1-pentanol(1)/water(2) LLE, water-rich phase x1 converted to x_water",
                x_axis=x_water,
                y_axis=t_k - 273.15,
                x_axis_label="x water",
                y_axis_label="T_C",
                point_index=index,
                T_K=t_k,
                T_C=t_k - 273.15,
                x_water=x_water,
                x_1_pentanol=x_pentanol,
                P_bar=1.013,
            )
        )
    for index, (t_k, x_water) in enumerate(alcohol_rich, start=1):
        rows.append(
            _row(
                figure_id="figure_10",
                dataset="literature_table",
                series="lle_1_pentanol_rich",
                source_role="lle_1_pentanol_rich",
                system="water/1-pentanol",
                source_reference="Goral et al. 2006 Table 8",
                source_detail="recommended 1-pentanol(1)/water(2) LLE, alcohol-rich phase x2 is x_water",
                x_axis=x_water,
                y_axis=t_k - 273.15,
                x_axis_label="x water",
                y_axis_label="T_C",
                point_index=index,
                T_K=t_k,
                T_C=t_k - 273.15,
                x_water=x_water,
                x_1_pentanol=1.0 - x_water,
                P_bar=1.013,
            )
        )
    return rows


def _build_all() -> list[dict[str, Any]]:
    summaries: list[dict[str, Any]] = []

    summaries.append(
        _write_figure_outputs(
            figure_id="figure_02",
            title="Gross 2002 Fig. 2: methanol/isobutane at 100 C",
            xlabel="isobutane mole fraction in liquid/vapor",
            ylabel="pressure / bar",
            literature_rows=_fig2_literature(),
            model_rows=_model_rows_from_csv("figure_02", _fig2_model),
            sources=["Leu and Robinson 1992 Table I"],
            pending=[],
            y_unit="bar",
            ylim=(0.0, 24.0),
        )
    )
    summaries.append(
        _write_figure_outputs(
            figure_id="figure_03",
            title="Gross 2002 Fig. 3: 1-propanol/ethylbenzene",
            xlabel="1-propanol mole fraction in liquid/vapor",
            ylabel="temperature / C",
            literature_rows=_fig3_literature(),
            model_rows=_model_rows_from_csv("figure_03", _fig3_model),
            sources=["Goral et al. 2004 Table 3.9, 101.32 kPa branch"],
            pending=["second pressure branch source table still needs the original Ellis/Froome data if a table-backed overlay is required"],
            y_unit="degC",
            ylim=(80.0, 142.0),
        )
    )
    summaries.append(
        _write_figure_outputs(
            figure_id="figure_04",
            title="Gross 2002 Fig. 4: 1-pentanol/benzene at 40 C",
            xlabel="benzene mole fraction",
            ylabel="pressure / bar",
            literature_rows=_fig4_literature(),
            model_rows=_model_rows_from_csv("figure_04", _fig4_model),
            sources=["Rhodes et al. 2001 Table 2"],
            pending=[],
            y_unit="bar",
            ylim=(0.0, 0.30),
        )
    )
    summaries.append(
        _write_figure_outputs(
            figure_id="figure_05",
            title="Gross 2002 Fig. 5: propanol/benzene at 40 C",
            xlabel="benzene mole fraction",
            ylabel="pressure / bar",
            literature_rows=_fig5_literature(),
            model_rows=_model_rows_from_csv("figure_05", _fig5_model),
            sources=["Rhodes et al. 2001 Table 2"],
            pending=[],
            y_unit="bar",
            ylim=(0.0, 0.36),
        )
    )
    summaries.append(
        _write_figure_outputs(
            figure_id="figure_06",
            title="Gross 2002 Fig. 6: 1-butanol/n-butane isotherms",
            xlabel="n-butane mole fraction",
            ylabel="pressure / bar",
            literature_rows=_deak_isotherm_rows(
                figure_id="figure_06",
                system="1-butanol/n-butane",
                data=DEAK_1_BUTANOL,
                targets={"T_60C": 333.15, "T_100C": 373.15, "T_160C": 433.15, "T_200C": 473.15},
                source_reference="Deak et al. 1995 Table 3",
                source_detail="n-butane + 1-butanol bubble point pressure p/MPa as a function of T for fixed x",
            ),
            model_rows=_model_rows_from_csv(
                "figure_06", lambda row: _isotherm_model_row("figure_06", "1-butanol/n-butane", row)
            ),
            sources=["Deak et al. 1995 Table 3"],
            pending=[],
            y_unit="bar",
            ylim=(0.0, 55.0),
        )
    )
    summaries.append(
        _write_figure_outputs(
            figure_id="figure_07",
            title="Gross 2002 Fig. 7: ethanol/n-butane isotherms",
            xlabel="n-butane mole fraction",
            ylabel="pressure / bar",
            literature_rows=_deak_isotherm_rows(
                figure_id="figure_07",
                system="ethanol/n-butane",
                data=DEAK_ETHANOL,
                targets={"T_100C": 373.15, "T_140C": 413.15, "T_160C": 433.15, "T_190C": 463.15},
                source_reference="Deak et al. 1995 Table 1",
                source_detail="n-butane + ethanol bubble point pressure p/MPa as a function of T for fixed x",
            ),
            model_rows=_model_rows_from_csv(
                "figure_07", lambda row: _isotherm_model_row("figure_07", "ethanol/n-butane", row)
            ),
            sources=["Deak et al. 1995 Table 1"],
            pending=[],
            y_unit="bar",
            ylim=(0.0, 60.0),
        )
    )
    summaries.append(
        _write_figure_outputs(
            figure_id="figure_08",
            title="Gross 2002 Fig. 8: methanol/cyclohexane at 1.013 bar",
            xlabel="methanol mole fraction in liquid/vapor",
            ylabel="temperature / C",
            literature_rows=_fig8_literature(),
            model_rows=_model_rows_from_csv("figure_08", _fig8_model),
            sources=["Madhavan and Murti 1966 Table 3c"],
            pending=["Kato et al. 1992 methanol/cyclohexane LLE table needs OCR or manual source_capture because the Zotero PDF table does not extract as text"],
            y_unit="degC",
            ylim=(0.0, 70.0),
        )
    )
    summaries.append(
        _write_figure_outputs(
            figure_id="figure_09",
            title="Gross 2002 Fig. 9: methanol/1-octanol at 1.013 bar",
            xlabel="methanol mole fraction in liquid/vapor",
            ylabel="temperature / C",
            literature_rows=_fig9_literature(),
            model_rows=_model_rows_from_csv("figure_09", _fig9_model),
            sources=["Arce et al. 1995 Table 3"],
            pending=[],
            y_unit="degC",
            ylim=(55.0, 200.0),
        )
    )
    summaries.append(
        _write_figure_outputs(
            figure_id="figure_10",
            title="Gross 2002 Fig. 10: water/1-pentanol LLE",
            xlabel="water mole fraction",
            ylabel="temperature / C",
            literature_rows=_fig10_literature(),
            model_rows=_model_rows_from_csv("figure_10", _fig10_model),
            sources=["Goral et al. 2006 Table 8"],
            pending=["Cho, Ochi, and Kojima 1984 water/1-pentanol VLE table for the heteroazeotropic upper branch"],
            y_unit="degC",
            ylim=(-5.0, 175.0),
        )
    )
    return summaries


def main() -> None:
    summaries = _build_all()
    SHARED_RESULTS.mkdir(parents=True, exist_ok=True)
    summary_csv = SHARED_RESULTS / "gross_2002_literature_overlay_summary.csv"
    rows = [
        {
            "figure_id": item["figure_id"],
            "artifact_png": item["artifact_png"],
            "literature_rows": item["literature_rows"],
            "model_seed_rows": item["model_seed_rows"],
            "smooth_model_rows": item["smooth_model_rows"],
            "source_trace_rows_plotted": item["source_trace_rows_plotted"],
            "matched_literature_points": item["fit_statistics"]["matched_literature_points"],
            "skipped_literature_points": item["fit_statistics"]["skipped_literature_points"],
            "mae": item["fit_statistics"]["mae"],
            "max_abs": item["fit_statistics"]["max_abs"],
            "signed_bias": item["fit_statistics"]["signed_bias"],
            "normalized_mae": item["fit_statistics"]["normalized_mae"],
            "y_unit": item["fit_statistics"]["y_unit"],
            "sources": "; ".join(item["sources"]),
            "pending_source_data": "; ".join(item["pending_source_data"]),
        }
        for item in summaries
    ]
    _write_csv(
        summary_csv,
        rows,
        [
            "figure_id",
            "artifact_png",
            "literature_rows",
            "model_seed_rows",
            "smooth_model_rows",
            "source_trace_rows_plotted",
            "matched_literature_points",
            "skipped_literature_points",
            "mae",
            "max_abs",
            "signed_bias",
            "normalized_mae",
            "y_unit",
            "sources",
            "pending_source_data",
        ],
    )
    print(f"Wrote {len(summaries)} clean Gross 2002 literature overlays.")
    print(_relative(summary_csv))


if __name__ == "__main__":
    main()
