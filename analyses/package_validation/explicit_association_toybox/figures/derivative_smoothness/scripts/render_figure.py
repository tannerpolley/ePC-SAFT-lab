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
    closure_label,
    save_png_svg,
    style_axis,
    target_label,
    write_sidecar,
)

OUTPUT = ANALYSIS_ROOT / "figures" / "derivative_smoothness" / "output"
SMOOTHNESS = OUTPUT / "derivative_smoothness.csv"
FIGURE = OUTPUT / "derivative_smoothness.png"
PLOTTED = OUTPUT / "derivative_smoothness_plotted_data.csv"
SIDECAR = OUTPUT / "derivative_smoothness.mpl.yaml"


def main() -> None:
    apply_plot_style()
    with SMOOTHNESS.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    plotted = [
        {
            "closure_name": row["closure_name"],
            "closure_label": closure_label(row["closure_name"]),
            "perturbation_axis": row["perturbation_axis"],
            "perturbation_label": target_label(row["perturbation_axis"]),
            "derivative_jump_abs": row["derivative_jump_abs"],
            "relative_jump": row["relative_jump"],
            "smoothness_band": row["smoothness_band"],
        }
        for row in rows
    ]
    OUTPUT.mkdir(parents=True, exist_ok=True)
    with PLOTTED.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(plotted[0]))
        writer.writeheader()
        writer.writerows(plotted)

    axes_order = ["density", "association_strength_scale", "composition_component_0"]
    axis_labels = [target_label(name) for name in axes_order]
    closures = sorted({row["closure_name"] for row in plotted})
    colors = {"implicit_exact_mass_action": BLUE, "damped_picard_7_05": ORANGE}
    fig, ax = plt.subplots(figsize=(7.8, 4.6))
    for closure in closures:
        values = []
        for axis_name in axes_order:
            match = next(
                row for row in plotted if row["closure_name"] == closure and row["perturbation_axis"] == axis_name
            )
            values.append(max(float(match["relative_jump"]), 1.0e-14))
        ax.plot(
            range(len(axes_order)),
            values,
            marker="o",
            linewidth=1.8,
            color=colors.get(closure, "#404040"),
            label=closure_label(closure),
        )
    ax.set_xticks(range(len(axes_order)))
    ax.set_xticklabels(axis_labels)
    ax.set_yscale("log")
    ax.set_title(r"Local derivative smoothness")
    ax.set_ylabel("relative slope jump")
    style_axis(ax, minor=True)
    ax.legend()
    fig.tight_layout()
    save_png_svg(fig, FIGURE)
    plt.close(fig)
    write_sidecar(
        SIDECAR,
        plot_id="explicit_association_derivative_smoothness",
        title="Local derivative smoothness",
        figure=FIGURE,
        source_data=PLOTTED,
        x_label="perturbation variable",
        y_label="relative slope jump",
        y_scale="log",
        command="uv run python analyses/package_validation/explicit_association_toybox/figures/derivative_smoothness/scripts/render_figure.py",
    )
    print(FIGURE)


if __name__ == "__main__":
    main()
