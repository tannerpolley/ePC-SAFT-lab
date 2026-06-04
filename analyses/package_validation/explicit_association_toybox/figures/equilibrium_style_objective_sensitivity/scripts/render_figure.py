from __future__ import annotations

import csv
from pathlib import Path

import matplotlib.pyplot as plt

ANALYSIS_ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ANALYSIS_ROOT / "figures" / "equilibrium_style_objective_sensitivity" / "output"
SOURCE = OUTPUT / "equilibrium_style_objective_sensitivity.csv"
PLOTTED = OUTPUT / "equilibrium_style_objective_sensitivity_plotted_data.csv"
FIGURE = OUTPUT / "equilibrium_style_objective_sensitivity.png"
SIDECAR = OUTPUT / "equilibrium_style_objective_sensitivity.mpl.yaml"


def main() -> None:
    with SOURCE.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    plotted = [
        {
            "case_id": row["case_id"],
            "closure_name": row["closure_name"],
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
    labels = [row["closure_name"] for row in plotted]
    gradient = [max(float(row["gradient_max_abs_error"]), 1.0e-14) for row in plotted]
    hessian = [max(float(row["hessian_proxy_max_abs_error"]), 1.0e-14) for row in plotted]
    x = range(len(plotted))
    fig, ax = plt.subplots(figsize=(8.6, 5.0))
    ax.bar([value - 0.18 for value in x], gradient, width=0.36, label="gradient", color="#3d6f8e")
    ax.bar([value + 0.18 for value in x], hessian, width=0.36, label="hessian proxy", color="#b35c1e")
    ax.set_yscale("log")
    ax.set_xticks(list(x))
    ax.set_xticklabels(labels, rotation=45, ha="right")
    ax.set_ylabel("Max absolute error")
    ax.set_title("Local objective derivative sensitivity")
    ax.grid(axis="y", color="#d9d9d9", linewidth=0.6)
    ax.legend()
    fig.tight_layout()
    fig.savefig(FIGURE, dpi=160)
    plt.close(fig)
    SIDECAR.write_text(
        "kind: matplotlib-figure\nversion: 1\nplot_id: equilibrium_style_objective_sensitivity\ntitle: Local objective derivative sensitivity\nfiles:\n  figure: equilibrium_style_objective_sensitivity.png\n  source_data: equilibrium_style_objective_sensitivity_plotted_data.csv\n",
        encoding="utf-8",
    )
    print(FIGURE)


if __name__ == "__main__":
    main()
