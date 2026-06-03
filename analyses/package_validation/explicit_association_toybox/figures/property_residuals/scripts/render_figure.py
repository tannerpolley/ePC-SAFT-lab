from __future__ import annotations

import csv
from pathlib import Path

import matplotlib.pyplot as plt

ANALYSIS_ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ANALYSIS_ROOT / "figures" / "property_residuals" / "output"
RESIDUALS = OUTPUT / "property_residuals.csv"
FIGURE = OUTPUT / "property_residuals.png"
PLOTTED = OUTPUT / "property_residuals_plotted_data.csv"
SIDECAR = OUTPUT / "property_residuals.mpl.yaml"


def main() -> None:
    with RESIDUALS.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    plotted = [
        {
            "component": row["component"],
            "T_K": row["T_K"],
            "abs_pressure_relative_residual": abs(float(row["pressure_relative_residual"])),
            "abs_density_relative_residual": abs(float(row["density_relative_residual"])),
        }
        for row in rows
    ]
    with PLOTTED.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(plotted[0]))
        writer.writeheader()
        writer.writerows(plotted)

    labels = [f"{row['component']} {float(row['T_K']):.0f} K" for row in plotted]
    x = range(len(plotted))
    fig, axes = plt.subplots(2, 1, figsize=(8, 6), sharex=True)
    axes[0].bar(x, [float(row["abs_pressure_relative_residual"]) for row in plotted], color="#2f6f9f")
    axes[0].set_ylabel("|pressure residual|")
    axes[0].set_yscale("log")
    axes[0].grid(axis="y", color="#d9d9d9", linewidth=0.6)
    axes[1].bar(x, [float(row["abs_density_relative_residual"]) for row in plotted], color="#b35c1e")
    axes[1].set_ylabel("|density residual|")
    axes[1].set_yscale("log")
    axes[1].set_xticks(list(x))
    axes[1].set_xticklabels(labels, rotation=25, ha="right")
    axes[1].grid(axis="y", color="#d9d9d9", linewidth=0.6)
    fig.suptitle("Fixed-state saturation property residuals")
    fig.tight_layout()
    fig.savefig(FIGURE, dpi=160)
    plt.close(fig)
    SIDECAR.write_text(
        "\n".join(
            (
                "kind: matplotlib-figure",
                "version: 1",
                "plot_id: explicit_association_fixed_state_property_residuals",
                "title: Fixed-state saturation property residuals",
                "matplotlib:",
                "  title: Fixed-state saturation property residuals",
                "  x_label: Component and temperature",
                "  y_label: Absolute relative residual",
                "  y_scale: log",
                "files:",
                "  figure: property_residuals.png",
                "  source_data: property_residuals_plotted_data.csv",
                "render:",
                "  command: uv run python analyses/package_validation/explicit_association_toybox/figures/property_residuals/scripts/render_figure.py",
                "",
            )
        ),
        encoding="utf-8",
    )
    print(FIGURE)


if __name__ == "__main__":
    main()
