from __future__ import annotations

import csv
from pathlib import Path

import matplotlib.pyplot as plt

ANALYSIS_ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ANALYSIS_ROOT / "figures" / "closure_sensitivity" / "output"
SENSITIVITY = OUTPUT / "closure_sensitivity.csv"
FIGURE = OUTPUT / "closure_sensitivity.png"
PLOTTED = OUTPUT / "closure_sensitivity_plotted_data.csv"
SIDECAR = OUTPUT / "closure_sensitivity.mpl.yaml"


def main() -> None:
    with SENSITIVITY.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    plotted = [
        {
            "closure_variant": row["closure_variant"],
            "picard_steps": row["picard_steps"],
            "damping": row["damping"],
            "diagonal_polish": row["diagonal_polish"],
            "max_ares_assoc_rel_error": row["max_ares_assoc_rel_error"],
            "max_mass_action_residual_inf": row["max_mass_action_residual_inf"],
            "median_elapsed_seconds": row["median_elapsed_seconds"],
            "median_exact_implicit_elapsed_seconds": row["median_exact_implicit_elapsed_seconds"],
            "speedup_vs_exact_implicit": row["speedup_vs_exact_implicit"],
            "evidence_band": row["evidence_band"],
        }
        for row in rows
    ]
    OUTPUT.mkdir(parents=True, exist_ok=True)
    with PLOTTED.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(plotted[0]))
        writer.writeheader()
        writer.writerows(plotted)

    fig, ax = plt.subplots(figsize=(8.5, 4.8))
    x = [max(float(row["median_elapsed_seconds"]), 1.0e-12) for row in plotted]
    y = [max(float(row["max_ares_assoc_rel_error"]), 1.0e-14) for row in plotted]
    colors = ["#2f6f9f" if row["diagonal_polish"] == "False" else "#b35c1e" for row in plotted]
    ax.scatter(x, y, c=colors, s=60)
    max_x = max(x)
    for xi, yi, row in zip(x, y, plotted, strict=True):
        if xi == max_x:
            ax.annotate(row["closure_variant"], (xi, yi), textcoords="offset points", xytext=(-5, 5), ha="right", fontsize=8)
        else:
            ax.annotate(row["closure_variant"], (xi, yi), textcoords="offset points", xytext=(5, 5), fontsize=8)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_title("Explicit association closure sensitivity ranking")
    ax.set_xlabel("Median elapsed seconds")
    ax.set_ylabel("Max association ares relative error")
    ax.grid(color="#d9d9d9", linewidth=0.6)
    ax.margins(x=0.12, y=0.16)
    fig.tight_layout()
    fig.savefig(FIGURE, dpi=160)
    plt.close(fig)
    SIDECAR.write_text(
        "\n".join(
            (
                "kind: matplotlib-figure",
                "version: 1",
                "plot_id: explicit_association_closure_sensitivity",
                "title: Explicit association closure sensitivity ranking",
                "matplotlib:",
                "  title: Explicit association closure sensitivity ranking",
                "  x_label: Median elapsed seconds",
                "  y_label: Max association ares relative error",
                "  x_scale: log",
                "  y_scale: log",
                "files:",
                "  figure: closure_sensitivity.png",
                "  source_data: closure_sensitivity_plotted_data.csv",
                "render:",
                "  command: uv run python analyses/package_validation/explicit_association_toybox/figures/closure_sensitivity/scripts/render_figure.py",
                "",
            )
        ),
        encoding="utf-8",
    )
    print(FIGURE)


if __name__ == "__main__":
    main()
