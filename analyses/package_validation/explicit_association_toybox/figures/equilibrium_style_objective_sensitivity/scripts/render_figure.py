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
    GREEN,
    ORANGE,
    apply_plot_style,
    closure_label,
    save_plot_artifacts,
    style_axis,
)

OUTPUT = ANALYSIS_ROOT / "figures" / "equilibrium_style_objective_sensitivity" / "output"
SOURCE = OUTPUT / "equilibrium_style_objective_sensitivity.csv"
PLOTTED = OUTPUT / "equilibrium_style_objective_sensitivity_plotted_data.csv"
FIGURE = OUTPUT / "equilibrium_style_objective_sensitivity.png"


def main() -> None:
    apply_plot_style()
    with SOURCE.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    plotted = [
        {
            "case_id": row["case_id"],
            "closure_name": row["closure_name"],
            "closure_label": closure_label(row["closure_name"]),
            "objective_abs_error": row["objective_abs_error"],
            "gradient_max_abs_error": row["gradient_max_abs_error"],
            "hessian_proxy_max_abs_error": row["hessian_proxy_max_abs_error"],
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

    row = plotted[0]
    labels = [r"$\Phi$", r"$\nabla\Phi$", r"$\nabla^2\Phi$ proxy"]
    values = [
        max(float(row["objective_abs_error"]), 1.0e-14),
        max(float(row["gradient_max_abs_error"]), 1.0e-14),
        max(float(row["hessian_proxy_max_abs_error"]), 1.0e-14),
    ]
    fig, ax = plt.subplots(figsize=(7.4, 4.4))
    ax.plot(range(len(values)), values, marker="o", linewidth=1.9, color=BLUE)
    ax.scatter(range(len(values)), values, s=70, color=[GREEN, BLUE, ORANGE])
    ax.set_yscale("log")
    ax.set_xticks(range(len(values)))
    ax.set_xticklabels(labels)
    ax.set_ylabel("absolute error vs exact implicit")
    ax.set_title(f"Local objective derivative sensitivity: {row['closure_label']}")
    style_axis(ax, minor=True)
    ax.annotate(
        f"{float(row['speedup_vs_exact_implicit']):.1f}x speedup",
        (1, values[1]),
        textcoords="offset points",
        xytext=(10, 8),
        fontsize=9,
    )
    fig.tight_layout()
    save_plot_artifacts(fig, FIGURE)
    plt.close(fig)
    print(FIGURE)


if __name__ == "__main__":
    main()
