from __future__ import annotations

import csv
import math
import sys
from pathlib import Path

import matplotlib.pyplot as plt

ANALYSIS_ROOT = Path(__file__).resolve().parents[3]
REPO_ROOT = ANALYSIS_ROOT.parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from analyses.package_validation.explicit_association_toybox.scripts.plot_style import save_png_svg, write_sidecar

OUTPUT = ANALYSIS_ROOT / "figures" / "property_residuals" / "output"
RESIDUALS = OUTPUT / "property_residuals.csv"
FIGURE = OUTPUT / "property_residuals.png"
PLOTTED = OUTPUT / "property_residuals_plotted_data.csv"
SIDECAR = OUTPUT / "property_residuals.mpl.yaml"
EXACT_COLOR = "#1f77b4"
PICARD_COLOR = "#d55e00"
MODEL_DOTTED = (0, (1.2, 1.8))
COMPONENT_LABELS = {
    "acetic_acid": "Acetic acid",
    "methanol": "Methanol",
    "water": "Water",
}


def main() -> None:
    _apply_chapman_style()
    with RESIDUALS.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    plotted = [
        {
            "component": row["component"],
            "T_K": row["T_K"],
            "inverse_temperature_1000_per_K": 1000.0 / float(row["T_K"]),
            "source_p_sat_mpa": float(row["source_p_sat_Pa"]) / 1.0e6,
            "source_log10_p_kpa": _safe_log10(float(row["source_p_sat_Pa"]) / 1000.0),
            "provider_pressure_at_exp_density_mpa": float(row["provider_pressure_at_exp_density_Pa"]) / 1.0e6,
            "exact_implicit_log10_pressure_kpa": _positive_log10_or_blank(
                float(row["toy_exact_pressure_at_exp_density_Pa"]) / 1000.0
            ),
            "source_rho_sat_liq_mol_m3": row["source_rho_sat_liq_mol_m3"],
            "source_density_mol_cc": float(row["source_rho_sat_liq_mol_m3"]) / 1.0e6,
            "provider_density_at_exp_pressure_mol_m3": row["provider_density_at_exp_pressure_mol_m3"],
            "exact_implicit_density_mol_cc": _optional_float(
                row["toy_exact_density_at_exp_pressure_mol_m3"], scale=1.0 / 1.0e6
            ),
            "picard_log10_pressure_kpa": _positive_log10_or_blank(
                _optional_float(row["picard_pressure_at_exp_density_Pa"], scale=1.0 / 1000.0)
            ),
            "picard_density_mol_cc": _optional_float(
                row["picard_density_at_exp_pressure_mol_m3"], scale=1.0 / 1.0e6
            ),
            "picard_output_status": row["picard_output_status"],
            "picard_model_role": row["picard_model_role"],
            "toy_exact_density_root_status": row["toy_exact_density_root_status"],
            "picard_density_root_status": row["picard_density_root_status"],
            "pressure_residual_mpa": row["pressure_residual_mpa"],
            "density_residual_rel": row["density_residual_rel"],
            "z_provider": row["z_provider"],
            "z_experimental": row["z_experimental"],
        }
        for row in rows
    ]
    with PLOTTED.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(plotted[0]))
        writer.writeheader()
        writer.writerows(plotted)

    components = sorted({row["component"] for row in plotted})
    fig, axes = plt.subplots(2, len(components), figsize=(4.2 * len(components), 6.8), constrained_layout=True)
    if len(components) == 1:
        axes = axes.reshape(2, 1)
    for column, component in enumerate(components):
        component_rows = sorted(
            (row for row in plotted if row["component"] == component),
            key=lambda row: float(row["T_K"]),
        )
        inverse_temperature = [float(row["inverse_temperature_1000_per_K"]) for row in component_rows]
        exp_log_p = [float(row["source_log10_p_kpa"]) for row in component_rows]
        temperature = [float(row["T_K"]) for row in component_rows]
        exp_density = [float(row["source_density_mol_cc"]) for row in component_rows]
        label = COMPONENT_LABELS.get(component, component.replace("_", " ").title())

        pressure_axis = axes[0, column]
        density_axis = axes[1, column]
        pressure_axis.scatter(
            inverse_temperature,
            exp_log_p,
            marker="o",
            s=10,
            facecolors="black",
            edgecolors="black",
            linewidths=0.4,
            label="Data",
        )
        _plot_optional_line(
            pressure_axis,
            inverse_temperature,
            [row["exact_implicit_log10_pressure_kpa"] for row in component_rows],
            color=EXACT_COLOR,
            linewidth=1.4,
            linestyle=MODEL_DOTTED,
            label="Exact implicit",
        )
        _plot_optional_line(
            pressure_axis,
            inverse_temperature,
            [row["picard_log10_pressure_kpa"] for row in component_rows],
            color=PICARD_COLOR,
            linewidth=1.4,
            linestyle=MODEL_DOTTED,
            label="Picard",
        )
        pressure_axis.set_title(label)
        pressure_axis.set_xlabel(r"$10^3/T\ [\mathrm{K}^{-1}]$")
        pressure_axis.set_ylabel(r"$\log_{10}(P/\mathrm{kPa})$")
        _style_chapman_axis(pressure_axis)

        density_axis.scatter(
            exp_density,
            temperature,
            marker="o",
            s=10,
            facecolors="black",
            edgecolors="black",
            linewidths=0.4,
        )
        _plot_optional_line(
            density_axis,
            [row["exact_implicit_density_mol_cc"] for row in component_rows],
            temperature,
            color=EXACT_COLOR,
            linewidth=1.4,
            linestyle=MODEL_DOTTED,
            label="Exact implicit",
        )
        _plot_optional_line(
            density_axis,
            [row["picard_density_mol_cc"] for row in component_rows],
            temperature,
            color=PICARD_COLOR,
            linewidth=1.4,
            linestyle=MODEL_DOTTED,
            label="Picard",
        )
        density_axis.set_xlabel(r"$\rho_\ell\ [\mathrm{mol}\,\mathrm{cm}^{-3}]$")
        density_axis.set_ylabel(r"$T\ [\mathrm{K}]$")
        _style_chapman_axis(density_axis)

    axes[0, 0].legend(frameon=False, loc="best", fontsize=7)

    save_png_svg(fig, FIGURE)
    plt.close(fig)
    write_sidecar(
        SIDECAR,
        plot_id="explicit_association_fixed_state_property_residuals",
        title="Chapman-style associating-fluid fixed-state check",
        figure=FIGURE,
        source_data=PLOTTED,
        x_label="10^3/T / K^-1 and rho_l / mol cm^-3",
        y_label="log10 pressure / kPa and temperature / K",
        y_scale="linear transformed pressure",
        command="uv run python analyses/package_validation/explicit_association_toybox/figures/property_residuals/scripts/render_figure.py",
    )
    print(FIGURE)


def _safe_log10(value: float) -> float:
    if value <= 0.0:
        raise ValueError("log10 pressure plots require positive pressure values.")

    return math.log10(value)


def _positive_log10_or_blank(value: float | None) -> float | str:
    if value is None or not math.isfinite(value) or value <= 0.0:
        return ""
    return math.log10(value)


def _optional_float(value: object, *, scale: float = 1.0) -> float | None:
    if value in {"", None}:
        return None
    parsed = float(value)
    return parsed * scale if math.isfinite(parsed) else None


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


def _is_finite_value(value: object) -> bool:
    if value in {"", None}:
        return False
    try:
        return math.isfinite(float(value))
    except (TypeError, ValueError):
        return False


def _apply_chapman_style() -> None:
    plt.rcParams.update(
        {
            "figure.dpi": 160,
            "savefig.dpi": 180,
            "font.family": "DejaVu Sans",
            "font.weight": "bold",
            "axes.labelweight": "bold",
            "axes.titleweight": "bold",
            "figure.titlesize": 12,
            "axes.titlesize": 11,
            "axes.labelsize": 10,
            "xtick.labelsize": 8,
            "ytick.labelsize": 8,
            "axes.grid": False,
        }
    )


def _style_chapman_axis(axis) -> None:
    axis.grid(False)
    axis.minorticks_on()
    for spine in axis.spines.values():
        spine.set_visible(True)
        spine.set_linewidth(1.2)
        spine.set_color("black")
    axis.tick_params(axis="both", which="major", direction="in", top=True, right=True, length=5.0, width=1.0)
    axis.tick_params(axis="both", which="minor", direction="in", top=True, right=True, length=2.5, width=0.8)


if __name__ == "__main__":
    main()
