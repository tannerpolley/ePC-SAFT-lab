from __future__ import annotations

import csv
from pathlib import Path

import matplotlib.pyplot as plt

ANALYSIS_ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ANALYSIS_ROOT / "figures" / "derivative_smoothness" / "output"
SMOOTHNESS = OUTPUT / "derivative_smoothness.csv"
FIGURE = OUTPUT / "derivative_smoothness.png"
PLOTTED = OUTPUT / "derivative_smoothness_plotted_data.csv"
SIDECAR = OUTPUT / "derivative_smoothness.mpl.yaml"


def main() -> None:
    with SMOOTHNESS.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    plotted = [
        {
            "closure_name": row["closure_name"],
            "perturbation_axis": row["perturbation_axis"],
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

    closures = sorted({row["closure_name"] for row in plotted})
    axes_names = sorted({row["perturbation_axis"] for row in plotted})
    offsets = {closure: idx - (len(closures) - 1) / 2.0 for idx, closure in enumerate(closures)}
    colors = {
        "implicit_exact_mass_action": "#2f6f9f",
        "explicit_damped_picard_unroll_3": "#b35c1e",
        "explicit_picard3_diag_newton1": "#6f8f3a",
    }
    fig, ax = plt.subplots(figsize=(8.6, 4.8))
    for closure in closures:
        xs: list[float] = []
        ys: list[float] = []
        for idx, axis_name in enumerate(axes_names):
            match = next(
                row for row in plotted if row["closure_name"] == closure and row["perturbation_axis"] == axis_name
            )
            xs.append(idx + 0.22 * offsets[closure])
            ys.append(max(float(match["relative_jump"]), 1.0e-14))
        ax.bar(xs, ys, width=0.2, label=closure, color=colors.get(closure, "#404040"))
    ax.set_xticks(range(len(axes_names)))
    ax.set_xticklabels(axes_names, rotation=25, ha="right")
    ax.set_yscale("log")
    ax.set_title("Association closure local derivative smoothness")
    ax.set_ylabel("Relative slope jump")
    ax.grid(axis="y", color="#d9d9d9", linewidth=0.6)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(FIGURE, dpi=160)
    plt.close(fig)
    SIDECAR.write_text(
        "\n".join(
            (
                "kind: matplotlib-figure",
                "version: 1",
                "plot_id: explicit_association_derivative_smoothness",
                "title: Association closure local derivative smoothness",
                "matplotlib:",
                "  title: Association closure local derivative smoothness",
                "  x_label: Perturbation axis",
                "  y_label: Relative slope jump",
                "  y_scale: log",
                "files:",
                "  figure: derivative_smoothness.png",
                "  source_data: derivative_smoothness_plotted_data.csv",
                "render:",
                "  command: uv run python analyses/package_validation/explicit_association_toybox/figures/derivative_smoothness/scripts/render_figure.py",
                "",
            )
        ),
        encoding="utf-8",
    )
    print(FIGURE)


if __name__ == "__main__":
    main()
