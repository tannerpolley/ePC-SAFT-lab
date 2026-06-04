from __future__ import annotations

import csv
from pathlib import Path

import matplotlib.pyplot as plt

ANALYSIS_ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ANALYSIS_ROOT / "figures" / "total_eos_impact" / "output"
SOURCE = OUTPUT / "total_eos_impact.csv"
PLOTTED = OUTPUT / "total_eos_impact_plotted_data.csv"
FIGURE = OUTPUT / "total_eos_impact.png"
SIDECAR = OUTPUT / "total_eos_impact.mpl.yaml"


def main() -> None:
    with SOURCE.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    plotted = [
        {
            "case_id": row["case_id"],
            "closure_name": row["closure_name"],
            "ares_total_rel_error": row["ares_total_rel_error"],
            "pressure_proxy_rel_error": row["pressure_proxy_rel_error"],
            "mu_proxy_max_abs_error": row["mu_proxy_max_abs_error"],
            "fugacity_proxy_max_abs_error": row["fugacity_proxy_max_abs_error"],
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
    x = [float(row["speedup_vs_exact_implicit"]) for row in plotted]
    y = [max(float(row["pressure_proxy_rel_error"]), 1.0e-14) for row in plotted]
    fig, ax = plt.subplots(figsize=(8.6, 5.2))
    ax.scatter(x, y, color="#684f9e", s=55)
    for xi, yi, row in zip(x, y, plotted, strict=True):
        ax.annotate(row["closure_name"], (xi, yi), textcoords="offset points", xytext=(5, 5), fontsize=7)
    ax.set_yscale("log")
    ax.set_xlabel("Speedup vs exact implicit")
    ax.set_ylabel("Pressure proxy relative error")
    ax.set_title("Total EOS impact ranking")
    ax.grid(color="#d9d9d9", linewidth=0.6)
    fig.tight_layout()
    fig.savefig(FIGURE, dpi=160)
    plt.close(fig)
    SIDECAR.write_text(
        "kind: matplotlib-figure\nversion: 1\nplot_id: total_eos_impact\ntitle: Total EOS impact ranking\nfiles:\n  figure: total_eos_impact.png\n  source_data: total_eos_impact_plotted_data.csv\n",
        encoding="utf-8",
    )
    print(FIGURE)


if __name__ == "__main__":
    main()
