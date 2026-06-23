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

from analyses.package_validation.explicit_association_toybox.scripts.plot_style import (
    BLUE,
    ORANGE,
    apply_plot_style,
    save_plot_artifacts,
)

OUTPUT = ANALYSIS_ROOT / "figures" / "pressure_density_validation" / "output"
SOURCE = OUTPUT / "pressure_density_validation.csv"
PLOTTED = OUTPUT / "pressure_density_validation_plotted_data.csv"
FIGURE = OUTPUT / "pressure_density_validation.png"
MODEL_DOTTED = (0, (1.2, 1.8))
MODEL_COLORS = {
    "exact_implicit": BLUE,
    "picard": ORANGE,
}
MODEL_LINEWIDTHS = {
    "exact_implicit": 2.4,
    "picard": 1.2,
}
COMPONENT_LABELS = {
    "acetic_acid": "Acetic acid",
    "methanol": "Methanol",
    "water": "Water",
}


def main() -> None:
    apply_plot_style()
    rows = _read_rows(SOURCE)
    plotted = [_plotted_row(row) for row in rows]
    _write_plotted_data(plotted)
    _render(plotted)
    print(FIGURE)


def _read_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise FileNotFoundError(
            "pressure_density_validation.csv is required before rendering; run generate_data.py first."
        )
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _plotted_row(row: dict[str, str]) -> dict[str, object]:
    pressure = _optional_float(row["model_pressure_Pa"])
    density = _optional_float(row["model_liquid_density_mol_m3"])
    return {
        "component": row["component"],
        "T_K": float(row["T_K"]),
        "inverse_temperature_1000_per_K": 1000.0 / float(row["T_K"]),
        "row_role": row["row_role"],
        "model_name": row["model_name"],
        "model_label": row["model_label"],
        "pressure_kPa": "" if pressure is None else pressure / 1000.0,
        "log10_pressure_kPa": _positive_log10_or_blank(None if pressure is None else pressure / 1000.0),
        "liquid_density_mol_cm3": "" if density is None else density / 1.0e6,
        "density_root_status": row["density_root_status"],
        "root_branch": row["root_branch"],
        "density_root_residual_Pa": row["density_root_residual_Pa"],
        "bracket_policy": row["bracket_policy"],
        "pressure_evaluation_count": row["pressure_evaluation_count"],
        "source_url": row["source_url"],
        "parameter_source": row["parameter_source"],
    }


def _write_plotted_data(rows: list[dict[str, object]]) -> None:
    PLOTTED.parent.mkdir(parents=True, exist_ok=True)
    with PLOTTED.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def _render(rows: list[dict[str, object]]) -> None:
    components = sorted({str(row["component"]) for row in rows})
    fig, axes = plt.subplots(2, len(components), figsize=(4.1 * len(components), 6.7), constrained_layout=True)
    if len(components) == 1:
        axes = axes.reshape(2, 1)
    for column, component in enumerate(components):
        component_rows = [row for row in rows if row["component"] == component]
        reference_rows = sorted(
            [row for row in component_rows if row["row_role"] == "reference_data"],
            key=lambda row: float(row["T_K"]),
        )
        pressure_axis = axes[0, column]
        density_axis = axes[1, column]
        label = COMPONENT_LABELS.get(component, component.replace("_", " ").title())

        pressure_axis.scatter(
            [float(row["inverse_temperature_1000_per_K"]) for row in reference_rows],
            [float(row["log10_pressure_kPa"]) for row in reference_rows],
            marker="o",
            s=14,
            facecolors="black",
            edgecolors="black",
            linewidths=0.4,
            label="Data",
            zorder=3,
        )
        density_axis.scatter(
            [float(row["liquid_density_mol_cm3"]) for row in reference_rows],
            [float(row["T_K"]) for row in reference_rows],
            marker="o",
            s=14,
            facecolors="black",
            edgecolors="black",
            linewidths=0.4,
            zorder=3,
        )

        for model_name in ("exact_implicit", "picard"):
            model_rows = sorted(
                [row for row in component_rows if row["model_name"] == model_name],
                key=lambda row: float(row["T_K"]),
            )
            _plot_optional_line(
                pressure_axis,
                [row["inverse_temperature_1000_per_K"] for row in model_rows],
                [row["log10_pressure_kPa"] for row in model_rows],
                color=MODEL_COLORS[model_name],
                linestyle=MODEL_DOTTED,
                linewidth=MODEL_LINEWIDTHS[model_name],
                label=str(model_rows[0]["model_label"]) if model_rows else model_name,
            )
            _plot_optional_line(
                density_axis,
                [row["liquid_density_mol_cm3"] for row in model_rows],
                [row["T_K"] for row in model_rows],
                color=MODEL_COLORS[model_name],
                linestyle=MODEL_DOTTED,
                linewidth=MODEL_LINEWIDTHS[model_name],
                label=str(model_rows[0]["model_label"]) if model_rows else model_name,
            )

        pressure_axis.set_title(label)
        pressure_axis.set_xlabel(r"$10^3/T\ \left[\mathrm{K}^{-1}\right]$")
        pressure_axis.set_ylabel(r"$\log_{10}\!\left(P/\mathrm{kPa}\right)$")
        density_axis.set_xlabel(r"$\rho_\ell\ \left[\mathrm{mol}\,\mathrm{cm}^{-3}\right]$")
        density_axis.set_ylabel(r"$T\ \left[\mathrm{K}\right]$")
        _style_chapman_axis(pressure_axis)
        _style_chapman_axis(density_axis)

    axes[0, 0].legend(frameon=False, loc="best", fontsize=8)
    save_plot_artifacts(fig, FIGURE)
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
