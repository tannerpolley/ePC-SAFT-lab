from __future__ import annotations

import csv
import math
import sys
from collections.abc import Mapping, Sequence
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter, MaxNLocator

ANALYSIS_ROOT = Path(__file__).resolve().parents[3]
REPO_ROOT = ANALYSIS_ROOT.parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from analyses.package_validation.explicit_association_toybox.scripts.plot_style import (
    BLUE,
    GREEN,
    ORANGE,
    apply_plot_style,
    save_png_svg,
    write_sidecar,
)

OUTPUT = ANALYSIS_ROOT / "figures" / "final_picard_admission_report" / "output"
SOURCE = OUTPUT / "final_picard_admission_report.csv"
PLOTTED = OUTPUT / "final_picard_admission_report_plotted_data.csv"
FIGURE = OUTPUT / "final_picard_admission_report.png"
SIDECAR = OUTPUT / "final_picard_admission_report.mpl.yaml"
MODEL_DOTTED = (0, (1.2, 1.8))
MODEL_COLORS = {
    "Exact implicit": BLUE,
    "Picard high accuracy": ORANGE,
    "Picard fast": GREEN,
}
MODEL_WIDTHS = {
    "Exact implicit": 2.2,
    "Picard high accuracy": 1.45,
    "Picard fast": 1.25,
}


def build_plotted_rows(rows: Sequence[Mapping[str, object]]) -> list[dict[str, object]]:
    plotted: list[dict[str, object]] = []
    exact_rows = [row for row in rows if row["policy_name"] == "implicit_exact_mass_action"]
    selected_policy_names = _selected_picard_policy_names(rows)
    for row in exact_rows:
        plotted.extend(_reference_rows(row))
        plotted.extend(_model_rows(row, label="Exact implicit", pressure_key="model_p_sat_exact_Pa", density_key="model_rho_liq_exact_mol_m3"))
    for row in rows:
        if row["policy_name"] not in selected_policy_names:
            continue
        label = selected_policy_names[str(row["policy_name"])]
        plotted.extend(_model_rows(row, label=label, pressure_key="model_p_sat_picard_Pa", density_key="model_rho_liq_picard_mol_m3"))
    if not plotted:
        raise ValueError("final Picard admission plotting received no retained rows.")
    return plotted


def main() -> None:
    apply_plot_style()
    rows = _read_rows(SOURCE)
    plotted = build_plotted_rows(rows)
    _write_plotted_data(plotted)
    _render(plotted)
    write_sidecar(
        SIDECAR,
        plot_id="final_picard_admission_report",
        title="Final Picard admission evidence",
        figure=FIGURE,
        source_data=PLOTTED,
        x_label="10^3/T / K^-1 and rho_l / mol cm^-3",
        y_label="log10 pressure / kPa and temperature / K",
        y_scale="linear transformed pressure",
        command=(
            "uv run python "
            "analyses/package_validation/explicit_association_toybox/figures/"
            "final_picard_admission_report/scripts/render_figure.py"
        ),
    )
    print(FIGURE)


def _reference_rows(row: Mapping[str, object]) -> list[dict[str, object]]:
    return [
        _plot_row(
            row,
            plot_role="reference_marker",
            plot_kind="saturation_pressure",
            series_label="Data",
            x_value=1000.0 / float(row["simulation_id"].split("_")[-1].removesuffix("K")),
            y_value=_positive_log10_or_blank(float(row["reference_p_sat_Pa"]) / 1000.0),
        ),
        _plot_row(
            row,
            plot_role="reference_marker",
            plot_kind="liquid_density",
            series_label="Data",
            x_value=float(row["reference_rho_liq_mol_m3"]) / 1.0e6,
            y_value=float(row["simulation_id"].split("_")[-1].removesuffix("K")),
        ),
    ]


def _model_rows(row: Mapping[str, object], *, label: str, pressure_key: str, density_key: str) -> list[dict[str, object]]:
    temperature = float(row["simulation_id"].split("_")[-1].removesuffix("K"))
    pressure = _optional_float(row.get(pressure_key, ""))
    density = _optional_float(row.get(density_key, ""))
    return [
        _plot_row(
            row,
            plot_role="model_curve",
            plot_kind="saturation_pressure",
            series_label=label,
            x_value=1000.0 / temperature,
            y_value=_positive_log10_or_blank(None if pressure is None else pressure / 1000.0),
        ),
        _plot_row(
            row,
            plot_role="model_curve",
            plot_kind="liquid_density",
            series_label=label,
            x_value="" if density is None else density / 1.0e6,
            y_value=temperature,
        ),
    ]


def _plot_row(
    row: Mapping[str, object],
    *,
    plot_role: str,
    plot_kind: str,
    series_label: str,
    x_value: object,
    y_value: object,
) -> dict[str, object]:
    return {
        "component": str(row["component_family"]),
        "simulation_id": str(row["simulation_id"]),
        "plot_role": plot_role,
        "plot_kind": plot_kind,
        "series_label": series_label,
        "policy_name": str(row["policy_name"]),
        "x_value": x_value,
        "y_value": y_value,
        "admission_band": str(row["admission_band"]),
        "issue_161_recommendation": str(row["issue_161_recommendation"]),
        "source_url": str(row.get("source_url", "")),
        "parameter_source": str(row.get("parameter_source", "")),
    }


def _selected_picard_policy_names(rows: Sequence[Mapping[str, object]]) -> dict[str, str]:
    picard_rows = [row for row in rows if row["policy_name"] != "implicit_exact_mass_action"]
    selected: dict[str, str] = {}
    finite_speed_rows = [
        row for row in picard_rows if _is_finite_value(row.get("simulation_elapsed_median_seconds_picard", ""))
    ]
    if finite_speed_rows:
        fast = min(finite_speed_rows, key=lambda row: float(row["simulation_elapsed_median_seconds_picard"]))
        selected[str(fast["policy_name"])] = "Picard fast"
    finite_error_rows = [row for row in picard_rows if math.isfinite(_max_relative_error(row))]
    if finite_error_rows:
        accurate = min(finite_error_rows, key=_max_relative_error)
        selected[str(accurate["policy_name"])] = "Picard high accuracy"
    return selected


def _read_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise FileNotFoundError(
            "final_picard_admission_report.csv is required before rendering; run generate_data.py first."
        )
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _write_plotted_data(rows: list[dict[str, object]]) -> None:
    PLOTTED.parent.mkdir(parents=True, exist_ok=True)
    with PLOTTED.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def _render(rows: list[dict[str, object]]) -> None:
    components = sorted({str(row["component"]) for row in rows})
    fig, axes = plt.subplots(2, len(components), figsize=(4.2 * len(components), 6.7), constrained_layout=True)
    if len(components) == 1:
        axes = axes.reshape(2, 1)
    for column, component in enumerate(components):
        component_rows = [row for row in rows if row["component"] == component]
        pressure_axis = axes[0, column]
        density_axis = axes[1, column]
        _scatter_reference(pressure_axis, component_rows, "saturation_pressure")
        _scatter_reference(density_axis, component_rows, "liquid_density")
        for label in ("Exact implicit", "Picard high accuracy", "Picard fast"):
            _plot_model_line(pressure_axis, component_rows, label, "saturation_pressure")
            _plot_model_line(density_axis, component_rows, label, "liquid_density")
        pressure_axis.set_title(component.replace("_", " ").title())
        pressure_axis.set_xlabel(r"$10^3/T\ \left[\mathrm{K}^{-1}\right]$")
        pressure_axis.set_ylabel(r"$\log_{10}\!\left(P_{\mathrm{sat}}/\mathrm{kPa}\right)$")
        density_axis.set_xlabel(r"$\rho_\ell\ \left[\mathrm{mol}\,\mathrm{cm}^{-3}\right]$")
        density_axis.set_ylabel(r"$T\ \left[\mathrm{K}\right]$")
        density_axis.xaxis.set_major_locator(MaxNLocator(nbins=5))
        density_axis.xaxis.set_major_formatter(FormatStrFormatter("%.3f"))
        _style_axis(pressure_axis)
        _style_axis(density_axis)
    axes[0, 0].legend(frameon=False, loc="best", fontsize=8)
    save_png_svg(fig, FIGURE)
    plt.close(fig)


def _scatter_reference(axis, rows: Sequence[Mapping[str, object]], plot_kind: str) -> None:
    values = _finite_pairs([row for row in rows if row["plot_role"] == "reference_marker" and row["plot_kind"] == plot_kind])
    if not values:
        return
    axis.scatter(
        [x for x, _ in values],
        [y for _, y in values],
        marker="o",
        s=16,
        facecolors="black",
        edgecolors="black",
        linewidths=0.4,
        label="Data" if plot_kind == "saturation_pressure" else None,
        zorder=3,
    )


def _plot_model_line(axis, rows: Sequence[Mapping[str, object]], label: str, plot_kind: str) -> None:
    values = _finite_pairs([row for row in rows if row["series_label"] == label and row["plot_kind"] == plot_kind])
    if not values:
        return
    axis.plot(
        [x for x, _ in values],
        [y for _, y in values],
        color=MODEL_COLORS[label],
        linestyle=MODEL_DOTTED,
        linewidth=MODEL_WIDTHS[label],
        label=label if plot_kind == "saturation_pressure" else None,
    )


def _finite_pairs(rows: Sequence[Mapping[str, object]]) -> list[tuple[float, float]]:
    pairs = [
        (float(row["x_value"]), float(row["y_value"]))
        for row in rows
        if _is_finite_value(row["x_value"]) and _is_finite_value(row["y_value"])
    ]
    pairs.sort(key=lambda item: item[0])
    return pairs


def _max_relative_error(row: Mapping[str, object]) -> float:
    keys = (
        "association_helmholtz_relative_error",
        "total_ares_proxy_relative_error",
        "pressure_proxy_relative_error",
        "saturation_pressure_relative_error",
        "liquid_density_relative_error",
        "vapor_density_relative_error",
        "derivative_max_relative_error",
        "hessian_max_relative_error",
    )
    values = [_optional_float(row.get(key, "")) for key in keys]
    finite = [value for value in values if value is not None]
    return max(finite) if finite else float("nan")


def _positive_log10_or_blank(value: float | None) -> float | str:
    if value is None or not math.isfinite(value) or value <= 0.0:
        return ""
    return math.log10(value)


def _optional_float(value: object) -> float | None:
    if value in {"", None}:
        return None
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return None
    return parsed if math.isfinite(parsed) else None


def _is_finite_value(value: object) -> bool:
    parsed = _optional_float(value)
    return parsed is not None


def _style_axis(axis) -> None:
    axis.grid(False)
    axis.minorticks_on()
    for spine in axis.spines.values():
        spine.set_visible(True)
        spine.set_linewidth(1.1)
        spine.set_color("black")
    axis.tick_params(axis="both", which="major", direction="in", top=True, right=True, length=5.0, width=1.0)
    axis.tick_params(axis="both", which="minor", direction="in", top=True, right=True, length=2.5, width=0.8)


if __name__ == "__main__":
    main()
