from __future__ import annotations

import csv
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
    style_axis,
)

OUTPUT = ANALYSIS_ROOT / "figures" / "quick_phase_equilibrium" / "output"
SOURCE = OUTPUT / "quick_phase_equilibrium.csv"
PLOTTED = OUTPUT / "quick_phase_equilibrium_plotted_data.csv"
FIGURE = OUTPUT / "quick_phase_equilibrium.png"
COLORS = {"Exact implicit": BLUE, "Picard": ORANGE}


def main() -> None:
    apply_plot_style()
    with SOURCE.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    plotted = [
        {
            "component": row["component"],
            "T_K": row["T_K"],
            "model_label": row["model_label"],
            "status": row["status"],
            "scaled_residual_norm": row["scaled_residual_norm"],
            "initial_scaled_residual_norm": row["initial_scaled_residual_norm"],
            "residual_reduction_factor": row["residual_reduction_factor"],
            "iteration_count": row["iteration_count"],
            "pressure_residual_MPa": float(row["pressure_residual_Pa"]) / 1.0e6,
            "reduced_mu_residual": row["reduced_mu_residual"],
            "vapor_density_mol_m3": row["vapor_density_mol_m3"],
            "liquid_density_mol_m3": row["liquid_density_mol_m3"],
        }
        for row in rows
    ]
    OUTPUT.mkdir(parents=True, exist_ok=True)
    with PLOTTED.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(plotted[0]))
        writer.writeheader()
        writer.writerows(plotted)

    components = sorted({row["component"] for row in plotted})
    fig, axes = plt.subplots(1, len(components), figsize=(5.2 * len(components), 3.9), constrained_layout=True)
    if len(components) == 1:
        axes = [axes]
    for axis, component in zip(axes, components, strict=True):
        component_rows = sorted(
            (row for row in plotted if row["component"] == component),
            key=lambda item: (str(item["model_label"]), float(item["T_K"])),
        )
        for label in ("Exact implicit", "Picard"):
            series = [row for row in component_rows if row["model_label"] == label]
            if not series:
                continue
            axis.plot(
                [float(row["T_K"]) for row in series],
                [max(float(row["scaled_residual_norm"]), 1.0e-16) for row in series],
                marker="o",
                linestyle=":",
                linewidth=1.7,
                markersize=4.2,
                color=COLORS[label],
                label=label,
            )
        axis.set_title(component.replace("_", " ").title(), loc="left")
        axis.set_xlabel(r"$T\ [\mathrm{K}]$")
        axis.set_yscale("log")
        axis.set_ylabel(r"$\Vert r_{P,\mu}\Vert_2$")
        style_axis(axis, minor=True)
        axis.legend(frameon=False)

    fig.suptitle("Quick toy phase-pair residuals")
    save_plot_artifacts(fig, FIGURE)
    plt.close(fig)
    print(FIGURE)


if __name__ == "__main__":
    main()
