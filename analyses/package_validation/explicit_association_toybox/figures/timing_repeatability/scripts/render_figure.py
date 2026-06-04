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
    write_sidecar,
)

OUTPUT = ANALYSIS_ROOT / "figures" / "timing_repeatability" / "output"
TIMING = OUTPUT / "timing_repeatability.csv"
FIGURE = OUTPUT / "timing_repeatability.png"
PLOTTED = OUTPUT / "timing_repeatability_plotted_data.csv"
SIDECAR = OUTPUT / "timing_repeatability.mpl.yaml"


def main() -> None:
    apply_plot_style()
    with TIMING.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    rows_by_name = {row["closure_name"]: row for row in rows}
    ordered_rows = [
        rows_by_name[name]
        for name in ("implicit_exact_mass_action", "damped_picard_7_05")
        if name in rows_by_name
    ]
    plotted = [
        {
            "closure_name": row["closure_name"],
            "closure_label": closure_label(row["closure_name"]),
            "repeat_count": row["repeat_count"],
            "elapsed_median_seconds": row["elapsed_median_seconds"],
            "elapsed_iqr_seconds": row["elapsed_iqr_seconds"],
            "elapsed_min_seconds": row["elapsed_min_seconds"],
            "elapsed_max_seconds": row["elapsed_max_seconds"],
            "speedup_median": row["speedup_median"],
        }
        for row in ordered_rows
    ]
    OUTPUT.mkdir(parents=True, exist_ok=True)
    with PLOTTED.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(plotted[0]))
        writer.writeheader()
        writer.writerows(plotted)

    labels = [row["closure_label"] for row in plotted]
    x = list(range(len(labels)))
    medians = [float(row["elapsed_median_seconds"]) for row in plotted]
    minimums = [float(row["elapsed_min_seconds"]) for row in plotted]
    maximums = [float(row["elapsed_max_seconds"]) for row in plotted]
    half_iqr = [float(row["elapsed_iqr_seconds"]) / 2.0 for row in plotted]
    fig, ax = plt.subplots(figsize=(7.2, 4.4))
    colors = [ORANGE if row["closure_name"] == "damped_picard_7_05" else BLUE for row in plotted]
    for xi, median, minimum, maximum, spread, color in zip(x, medians, minimums, maximums, half_iqr, colors, strict=True):
        ax.vlines(xi, minimum, maximum, color=color, linewidth=1.2, alpha=0.7)
        ax.vlines(xi, max(median - spread, minimum), min(median + spread, maximum), color=color, linewidth=4.0)
        ax.scatter([xi], [minimum], marker="_", s=90, color=color)
        ax.scatter([xi], [median], marker="o", s=44, color=color, zorder=3)
        ax.scatter([xi], [maximum], marker="_", s=90, color=color)
    ax.set_yscale("log")
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_title("Repeated association solve timing range")
    ax.set_ylabel("elapsed time / s")
    style_axis(ax, minor=True)
    for xi, row in zip(x, plotted, strict=True):
        speed = float(row["speedup_median"])
        if speed > 1.0:
            ax.annotate(f"{speed:.1f}x", (xi, medians[xi]), textcoords="offset points", xytext=(0, 6), ha="center")
    fig.tight_layout()
    save_png_svg(fig, FIGURE)
    plt.close(fig)
    write_sidecar(
        SIDECAR,
        plot_id="explicit_association_timing_repeatability",
        title="Repeated association solve timing range",
        figure=FIGURE,
        source_data=PLOTTED,
        x_label="method",
        y_label="elapsed time / s",
        y_scale="log",
        command="uv run python analyses/package_validation/explicit_association_toybox/figures/timing_repeatability/scripts/render_figure.py",
    )
    print(FIGURE)


if __name__ == "__main__":
    main()
