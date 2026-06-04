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
    save_png_svg,
    style_axis,
    write_sidecar,
)

OUTPUT = ANALYSIS_ROOT / "figures" / "water_topology_fork" / "output"
SOURCE = OUTPUT / "water_topology_fork.csv"
PLOTTED = OUTPUT / "water_topology_fork_plotted_data.csv"
FIGURE = OUTPUT / "water_topology_fork.png"
SIDECAR = OUTPUT / "water_topology_fork.mpl.yaml"


def main() -> None:
    apply_plot_style()
    with SOURCE.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    plotted = [
        {
            "case_id": row["case_id"],
            "assigned_topology": row["assigned_topology"],
            "rigorous_topology": row["rigorous_topology"],
            "parameter_source": row["parameter_source"],
            "temperature_k": row["temperature_k"],
            "pressure_residual_mpa": row["pressure_residual_mpa"],
            "z_residual_abs": row["z_residual_abs"],
            "water_diagnostic_role": row["water_diagnostic_role"],
        }
        for row in rows
    ]
    OUTPUT.mkdir(parents=True, exist_ok=True)
    with PLOTTED.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(plotted[0]))
        writer.writeheader()
        writer.writerows(plotted)

    groups = sorted({row["case_id"] for row in plotted})
    colors = [BLUE, ORANGE]
    fig, axes = plt.subplots(2, 1, figsize=(8.0, 6.0), sharex=True, constrained_layout=True)
    for color, group in zip(colors, groups, strict=False):
        group_rows = sorted((row for row in plotted if row["case_id"] == group), key=lambda row: float(row["temperature_k"]))
        x = [float(row["temperature_k"]) for row in group_rows]
        p = [abs(float(row["pressure_residual_mpa"])) for row in group_rows]
        z = [max(float(row["z_residual_abs"]), 1.0e-14) for row in group_rows]
        label = f"{group_rows[0]['assigned_topology']} assigned"
        axes[0].plot(x, p, marker="o", linewidth=1.8, color=color, label=label)
        axes[1].plot(x, z, marker="o", linewidth=1.8, color=color, label=label)
    axes[0].set_yscale("log")
    axes[0].set_ylabel(r"$|P_{\mathrm{res}}|$ / MPa")
    axes[0].set_title("Water fixed-state topology diagnostic")
    axes[0].legend()
    style_axis(axes[0], minor=True)
    axes[1].set_yscale("log")
    axes[1].set_xlabel(r"$T$ / K")
    axes[1].set_ylabel(r"$|Z_{\mathrm{provider}}-Z_{\mathrm{exp}}|$")
    axes[1].legend()
    style_axis(axes[1], minor=True)
    save_png_svg(fig, FIGURE)
    plt.close(fig)
    write_sidecar(
        SIDECAR,
        plot_id="water_topology_fork",
        title="Water fixed-state topology diagnostic",
        figure=FIGURE,
        source_data=PLOTTED,
        x_label="T / K",
        y_label="absolute pressure and Z residuals",
        y_scale="log",
        command="uv run python analyses/package_validation/explicit_association_toybox/figures/water_topology_fork/scripts/render_figure.py",
    )
    print(FIGURE)


if __name__ == "__main__":
    main()
