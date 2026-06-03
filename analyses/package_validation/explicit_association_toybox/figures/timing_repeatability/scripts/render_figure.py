from __future__ import annotations

import csv
from pathlib import Path

import matplotlib.pyplot as plt

ANALYSIS_ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ANALYSIS_ROOT / "figures" / "timing_repeatability" / "output"
TIMING = OUTPUT / "timing_repeatability.csv"
FIGURE = OUTPUT / "timing_repeatability.png"
PLOTTED = OUTPUT / "timing_repeatability_plotted_data.csv"
SIDECAR = OUTPUT / "timing_repeatability.mpl.yaml"


def main() -> None:
    with TIMING.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    plotted = [
        {
            "closure_name": row["closure_name"],
            "repeat_count": row["repeat_count"],
            "elapsed_median_seconds": row["elapsed_median_seconds"],
            "elapsed_iqr_seconds": row["elapsed_iqr_seconds"],
            "elapsed_min_seconds": row["elapsed_min_seconds"],
            "elapsed_max_seconds": row["elapsed_max_seconds"],
            "speedup_median": row["speedup_median"],
        }
        for row in rows
    ]
    OUTPUT.mkdir(parents=True, exist_ok=True)
    with PLOTTED.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(plotted[0]))
        writer.writeheader()
        writer.writerows(plotted)

    labels = [row["closure_name"] for row in plotted]
    x = list(range(len(labels)))
    medians = [float(row["elapsed_median_seconds"]) for row in plotted]
    spreads = [float(row["elapsed_iqr_seconds"]) / 2.0 for row in plotted]
    fig, ax = plt.subplots(figsize=(8.8, 4.8))
    ax.bar(x, medians, yerr=spreads, color="#2f6f9f", capsize=4)
    ax.set_yscale("log")
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=30, ha="right")
    ax.set_title("Association closure repeated timing")
    ax.set_ylabel("Median elapsed seconds")
    ax.grid(axis="y", color="#d9d9d9", linewidth=0.6)
    fig.tight_layout()
    fig.savefig(FIGURE, dpi=160)
    plt.close(fig)
    SIDECAR.write_text(
        "\n".join(
            (
                "kind: matplotlib-figure",
                "version: 1",
                "plot_id: explicit_association_timing_repeatability",
                "title: Association closure repeated timing",
                "matplotlib:",
                "  title: Association closure repeated timing",
                "  x_label: Closure",
                "  y_label: Median elapsed seconds",
                "  y_scale: log",
                "files:",
                "  figure: timing_repeatability.png",
                "  source_data: timing_repeatability_plotted_data.csv",
                "render:",
                "  command: uv run python analyses/package_validation/explicit_association_toybox/figures/timing_repeatability/scripts/render_figure.py",
                "",
            )
        ),
        encoding="utf-8",
    )
    print(FIGURE)


if __name__ == "__main__":
    main()
