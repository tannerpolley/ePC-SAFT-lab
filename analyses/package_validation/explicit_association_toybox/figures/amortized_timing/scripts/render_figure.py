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
    save_plot_artifacts,
    style_axis,
)

OUTPUT = ANALYSIS_ROOT / "figures" / "amortized_timing" / "output"
SOURCE = OUTPUT / "amortized_timing.csv"
PLOTTED = OUTPUT / "amortized_timing_plotted_data.csv"
FIGURE = OUTPUT / "amortized_timing.png"


def main() -> None:
    apply_plot_style()
    with SOURCE.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    plotted = [
        {
            "case_id": row["case_id"],
            "topology_id": row["topology_id"],
            "site_count": row["site_count"],
            "closure_name": row["closure_name"],
            "closure_label": closure_label(row["closure_name"]),
            "exact_implicit_elapsed_median_seconds": row["exact_implicit_elapsed_median_seconds"],
            "closure_elapsed_median_seconds": row["closure_elapsed_median_seconds"],
            "speedup_vs_exact_implicit": row["speedup_vs_exact_implicit"],
            "exact_iteration_count_median": row["exact_iteration_count_median"],
        }
        for row in rows
    ]
    OUTPUT.mkdir(parents=True, exist_ok=True)
    with PLOTTED.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(plotted[0]))
        writer.writeheader()
        writer.writerows(plotted)

    labels = [f"{row['topology_id']} ({row['site_count']} sites)" for row in plotted]
    x = list(range(len(plotted)))
    exact = [float(row["exact_implicit_elapsed_median_seconds"]) for row in plotted]
    picard = [float(row["closure_elapsed_median_seconds"]) for row in plotted]
    fig, ax = plt.subplots(figsize=(8.8, 4.8))
    ax.plot(x, exact, marker="o", linewidth=1.9, color=BLUE, label="Exact implicit")
    ax.plot(x, picard, marker="s", linewidth=1.9, color=ORANGE, label="Picard")
    for xi, row in zip(x, plotted, strict=True):
        ax.annotate(
            f"{float(row['speedup_vs_exact_implicit']):.1f}x",
            (xi, picard[xi]),
            textcoords="offset points",
            xytext=(0, -14),
            ha="center",
            fontsize=8,
        )
    ax.set_yscale("log")
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylabel("median elapsed time / s")
    ax.set_title("Exact implicit vs Picard timing by topology")
    style_axis(ax, minor=True)
    ax.legend()
    fig.tight_layout()
    save_plot_artifacts(fig, FIGURE)
    plt.close(fig)
    print(FIGURE)


if __name__ == "__main__":
    main()
