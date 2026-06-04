from __future__ import annotations

import csv
from pathlib import Path

import matplotlib.pyplot as plt

ANALYSIS_ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ANALYSIS_ROOT / "figures" / "amortized_timing" / "output"
SOURCE = OUTPUT / "amortized_timing.csv"
PLOTTED = OUTPUT / "amortized_timing_plotted_data.csv"
FIGURE = OUTPUT / "amortized_timing.png"
SIDECAR = OUTPUT / "amortized_timing.mpl.yaml"


def main() -> None:
    with SOURCE.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    plotted = [
        {
            "case_id": row["case_id"],
            "topology_id": row["topology_id"],
            "site_count": row["site_count"],
            "closure_name": row["closure_name"],
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
    labels = [f"{row['topology_id']} {row['closure_name']}" for row in plotted]
    exact = [float(row["exact_implicit_elapsed_median_seconds"]) for row in plotted]
    closure = [float(row["closure_elapsed_median_seconds"]) for row in plotted]
    x = range(len(plotted))
    fig, ax = plt.subplots(figsize=(10.5, 5.4))
    ax.bar([value - 0.2 for value in x], exact, width=0.4, label="exact implicit", color="#3d6f8e")
    ax.bar([value + 0.2 for value in x], closure, width=0.4, label="closure", color="#b35c1e")
    ax.set_yscale("log")
    ax.set_xticks(list(x))
    ax.set_xticklabels(labels, rotation=70, ha="right", fontsize=7)
    ax.set_ylabel("Median elapsed seconds")
    ax.set_title("Amortized exact implicit and explicit closure timing")
    ax.grid(axis="y", color="#d9d9d9", linewidth=0.6)
    ax.legend()
    fig.tight_layout()
    fig.savefig(FIGURE, dpi=160)
    plt.close(fig)
    _write_sidecar("amortized_timing", "Amortized exact implicit and explicit closure timing", "Median elapsed seconds")
    print(FIGURE)


def _write_sidecar(plot_id: str, title: str, y_label: str) -> None:
    SIDECAR.write_text(
        "\n".join(
            (
                "kind: matplotlib-figure",
                "version: 1",
                f"plot_id: {plot_id}",
                f"title: {title}",
                "matplotlib:",
                f"  title: {title}",
                "  x_label: Case and closure",
                f"  y_label: {y_label}",
                "files:",
                f"  figure: {FIGURE.name}",
                f"  source_data: {PLOTTED.name}",
                "",
            )
        ),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
