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
    GRAY,
    ORANGE,
    apply_plot_style,
    closure_label,
    role_label,
    save_png_svg,
    style_axis,
    write_sidecar,
)

OUTPUT = ANALYSIS_ROOT / "figures" / "timing_pareto" / "output"
PARETO = OUTPUT / "timing_pareto.csv"
FIGURE = OUTPUT / "timing_pareto.png"
PLOTTED = OUTPUT / "timing_pareto_plotted_data.csv"
SIDECAR = OUTPUT / "timing_pareto.mpl.yaml"


def main() -> None:
    apply_plot_style()
    with PARETO.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    plotted = [
        {
            **row,
            "closure_label": closure_label(row["closure"]),
            "comparison_label": role_label(row["comparison_role"]),
        }
        for row in rows
    ]
    with PLOTTED.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(plotted[0]))
        writer.writeheader()
        writer.writerows(plotted)

    fig, ax = plt.subplots(figsize=(7.6, 4.8))
    colors = {"exact_topology_reduction": GRAY, "explicit_approximation": ORANGE}
    markers = {"exact_topology_reduction": "o", "explicit_approximation": "s"}
    seen: set[str] = set()
    for row in plotted:
        role = row["comparison_role"]
        label = role_label(role) if role not in seen else None
        seen.add(role)
        x = max(float(row["median_elapsed_seconds"]), 1.0e-12)
        y = max(float(row["max_abs_assoc_helmholtz_rel_error"]), 1.0e-14)
        ax.scatter(x, y, s=60, color=colors.get(role, BLUE), marker=markers.get(role, "o"), label=label)
        if role == "explicit_approximation":
            ax.annotate("Picard", (x, y), textcoords="offset points", xytext=(6, 5), fontsize=8)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_title("Association solve timing and error")
    ax.set_xlabel("median elapsed time / s")
    ax.set_ylabel(r"max relative error in $a_{\mathrm{assoc}}$")
    style_axis(ax, grid_axis="both", minor=True)
    ax.legend()
    fig.tight_layout()
    save_png_svg(fig, FIGURE)
    plt.close(fig)
    write_sidecar(
        SIDECAR,
        plot_id="explicit_association_timing_pareto",
        title="Association solve timing and error",
        figure=FIGURE,
        source_data=PLOTTED,
        x_label="median elapsed time / s",
        y_label="max relative error in a_assoc",
        y_scale="log",
        command="uv run python analyses/package_validation/explicit_association_toybox/figures/timing_pareto/scripts/render_figure.py",
    )
    print(FIGURE)


if __name__ == "__main__":
    main()
