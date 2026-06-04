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

OUTPUT = ANALYSIS_ROOT / "figures" / "pure_saturation_validation" / "output"
SOURCE = OUTPUT / "pure_saturation_validation.csv"
PLOTTED = OUTPUT / "pure_saturation_validation_plotted_data.csv"
FIGURE = OUTPUT / "pure_saturation_validation.png"
SIDECAR = OUTPUT / "pure_saturation_validation.mpl.yaml"
MODEL_DOTTED = (0, (1.2, 1.8))
MODEL_COLORS = {
    "Exact implicit": BLUE,
    "Picard": ORANGE,
    "Picard JAX": GREEN,
}
MODEL_WIDTHS = {
    "Exact implicit": 2.3,
    "Picard": 1.25,
    "Picard JAX": 1.6,
}
MODEL_LABEL_ORDER = ("Exact implicit", "Picard", "Picard JAX")
COMPONENT_LABELS = {
    "methanol": "Methanol",
    "water": "Water",
}


def build_plotted_rows(rows: Sequence[Mapping[str, object]]) -> list[dict[str, object]]:
    plotted: list[dict[str, object]] = []
    for row in rows:
        pressure = _optional_float(row["model_p_sat_Pa"])
        rho_liq = _optional_float(row["model_rho_liq_mol_m3"])
        rho_vap = _optional_float(row["model_rho_vap_mol_m3"])
        plot_role = "reference_marker" if row["row_role"] == "reference_data" else "model_curve"
        p_kpa = None if pressure is None else pressure / 1000.0
        plotted.append(
            {
                "component": str(row["component"]),
                "T_K": float(row["T_K"]),
                "inverse_temperature_1000_per_K": 1000.0 / float(row["T_K"]),
                "plot_role": plot_role,
                "closure_name": str(row["closure_name"]),
                "series_label": str(row["model_label"]),
                "p_sat_kPa": "" if p_kpa is None else p_kpa,
                "log10_p_sat_kPa": _positive_log10_or_blank(p_kpa),
                "rho_vap_mol_m3": "" if rho_vap is None else rho_vap,
                "rho_liq_mol_cm3": "" if rho_liq is None else rho_liq / 1.0e6,
                "solver_status": str(row["solver_status"]),
                "optimizer_backend": str(row.get("optimizer_backend", "")),
                "autodiff_backend": str(row.get("autodiff_backend", "")),
                "source_url": str(row["source_url"]),
                "parameter_source": str(row["parameter_source"]),
            }
        )
    if not plotted:
        raise ValueError("pure saturation plotting received no retained rows.")
    return plotted


def main() -> None:
    apply_plot_style()
    rows = _read_rows(SOURCE)
    plotted = build_plotted_rows(rows)
    _write_plotted_data(plotted)
    _render(plotted)
    write_sidecar(
        SIDECAR,
        plot_id="explicit_association_pure_saturation_validation",
        title="Pure-component saturation validation",
        figure=FIGURE,
        source_data=PLOTTED,
        x_label="10^3/T / K^-1 and rho_l / mol cm^-3",
        y_label="log10 pressure / kPa and temperature / K",
        y_scale="linear transformed pressure",
        command=(
            "uv run python "
            "analyses/package_validation/explicit_association_toybox/figures/"
            "pure_saturation_validation/scripts/render_figure.py"
        ),
    )
    print(FIGURE)


def _read_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise FileNotFoundError(
            "pure_saturation_validation.csv is required before rendering; run generate_data.py first."
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
    fig, axes = plt.subplots(
        2,
        len(components),
        figsize=(4.2 * len(components), 6.7),
        constrained_layout=True,
    )
    if len(components) == 1:
        axes = axes.reshape(2, 1)
    for column, component in enumerate(components):
        component_rows = [row for row in rows if row["component"] == component]
        reference_rows = sorted(
            [row for row in component_rows if row["plot_role"] == "reference_marker"],
            key=lambda row: float(row["T_K"]),
        )
        pressure_axis = axes[0, column]
        density_axis = axes[1, column]
        pressure_axis.scatter(
            [float(row["inverse_temperature_1000_per_K"]) for row in reference_rows],
            [float(row["log10_p_sat_kPa"]) for row in reference_rows],
            marker="o",
            s=14,
            facecolors="black",
            edgecolors="black",
            linewidths=0.4,
            label="Data",
            zorder=3,
        )
        density_axis.scatter(
            [float(row["rho_liq_mol_cm3"]) for row in reference_rows],
            [float(row["T_K"]) for row in reference_rows],
            marker="o",
            s=14,
            facecolors="black",
            edgecolors="black",
            linewidths=0.4,
            zorder=3,
        )
        for model_label in MODEL_LABEL_ORDER:
            model_rows = sorted(
                [row for row in component_rows if row["series_label"] == model_label],
                key=lambda row: float(row["T_K"]),
            )
            _plot_optional_line(
                pressure_axis,
                [row["inverse_temperature_1000_per_K"] for row in model_rows],
                [row["log10_p_sat_kPa"] for row in model_rows],
                color=MODEL_COLORS[model_label],
                linestyle=MODEL_DOTTED,
                linewidth=MODEL_WIDTHS[model_label],
                label=model_label,
            )
            _plot_optional_line(
                density_axis,
                [row["rho_liq_mol_cm3"] for row in model_rows],
                [row["T_K"] for row in model_rows],
                color=MODEL_COLORS[model_label],
                linestyle=MODEL_DOTTED,
                linewidth=MODEL_WIDTHS[model_label],
            )
        label = COMPONENT_LABELS.get(component, component.replace("_", " ").title())
        pressure_axis.set_title(label)
        pressure_axis.set_xlabel(r"$10^3/T\ \left[\mathrm{K}^{-1}\right]$")
        pressure_axis.set_ylabel(r"$\log_{10}\!\left(P_{\mathrm{sat}}/\mathrm{kPa}\right)$")
        density_axis.set_xlabel(r"$\rho_\ell\ \left[\mathrm{mol}\,\mathrm{cm}^{-3}\right]$")
        density_axis.set_ylabel(r"$T\ \left[\mathrm{K}\right]$")
        density_axis.xaxis.set_major_locator(MaxNLocator(nbins=5))
        density_axis.xaxis.set_major_formatter(FormatStrFormatter("%.3f"))
        _style_chapman_axis(pressure_axis)
        _style_chapman_axis(density_axis)
    axes[0, 0].legend(frameon=False, loc="best", fontsize=8)
    save_png_svg(fig, FIGURE)
    plt.close(fig)


def _plot_optional_line(axis, x_values, y_values, **kwargs) -> None:
    pairs = [
        (float(x), float(y))
        for x, y in zip(x_values, y_values, strict=True)
        if _is_finite_value(x) and _is_finite_value(y)
    ]
    if not pairs:
        return
    pairs.sort(key=lambda item: item[0])
    axis.plot([x for x, _ in pairs], [y for _, y in pairs], **kwargs)


def _positive_log10_or_blank(value: float | None) -> float | str:
    if value is None or not math.isfinite(value) or value <= 0.0:
        return ""
    return math.log10(value)


def _optional_float(value: object) -> float | None:
    if value in {"", None}:
        return None
    parsed = float(value)
    return parsed if math.isfinite(parsed) else None


def _is_finite_value(value: object) -> bool:
    if value in {"", None}:
        return False
    try:
        return math.isfinite(float(value))
    except (TypeError, ValueError):
        return False


def _style_chapman_axis(axis) -> None:
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
