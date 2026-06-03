from __future__ import annotations

import csv
from pathlib import Path

import matplotlib.pyplot as plt

ANALYSIS_ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ANALYSIS_ROOT / "figures" / "timing_pareto" / "output"
PARETO = OUTPUT / "timing_pareto.csv"
FIGURE = OUTPUT / "timing_pareto.png"
PLOTTED = OUTPUT / "timing_pareto_plotted_data.csv"
SIDECAR = OUTPUT / "timing_pareto.mpl.yaml"


def main() -> None:
    with PARETO.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    with PLOTTED.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    fig, ax = plt.subplots(figsize=(8, 4.8))
    for row in rows:
        ax.scatter(
            max(float(row["median_elapsed_seconds"]), 1.0e-12),
            max(float(row["max_abs_assoc_helmholtz_rel_error"]), 1.0e-14),
            s=44,
            label=row["closure"],
        )
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_title("Association closure timing and error")
    ax.set_xlabel("Median closure elapsed seconds")
    ax.set_ylabel("Max absolute relative association Helmholtz error")
    ax.grid(color="#d9d9d9", linewidth=0.6)
    ax.legend(fontsize=7, loc="center left", bbox_to_anchor=(1.0, 0.5))
    fig.tight_layout()
    fig.savefig(FIGURE, dpi=160)
    plt.close(fig)
    SIDECAR.write_text(
        "\n".join(
            (
                "kind: matplotlib-figure",
                "version: 1",
                "plot_id: explicit_association_timing_pareto",
                "title: Association closure timing and error",
                "matplotlib:",
                "  title: Association closure timing and error",
                "  x_label: Median closure elapsed seconds",
                "  y_label: Max absolute relative association Helmholtz error",
                "  x_scale: log",
                "  y_scale: log",
                "files:",
                "  figure: timing_pareto.png",
                "  source_data: timing_pareto_plotted_data.csv",
                "render:",
                "  command: uv run python analyses/package_validation/explicit_association_toybox/figures/timing_pareto/scripts/render_figure.py",
                "",
            )
        ),
        encoding="utf-8",
    )
    print(FIGURE)


if __name__ == "__main__":
    main()
