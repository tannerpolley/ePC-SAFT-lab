from __future__ import annotations

import csv
from pathlib import Path

import matplotlib.pyplot as plt

ANALYSIS_ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ANALYSIS_ROOT / "figures" / "asymmetric_binary_closures" / "output"
SOURCE = OUTPUT / "asymmetric_binary_closures.csv"
PLOTTED = OUTPUT / "asymmetric_binary_closures_plotted_data.csv"
FIGURE = OUTPUT / "asymmetric_binary_closures.png"
SIDECAR = OUTPUT / "asymmetric_binary_closures.mpl.yaml"


def main() -> None:
    with SOURCE.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    plotted = [
        {
            "case_id": row["case_id"],
            "case_role": row["case_role"],
            "closure_name": row["closure_name"],
            "ares_assoc_rel_error": row["ares_assoc_rel_error"],
            "mass_action_residual_inf": row["mass_action_residual_inf"],
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
    labels = [f"{row['case_role']}\n{row['closure_name']}" for row in plotted]
    y = [max(float(row["ares_assoc_rel_error"]), 1.0e-14) for row in plotted]
    fig, ax = plt.subplots(figsize=(11.5, 5.6))
    ax.bar(range(len(plotted)), y, color="#2f7d5c")
    ax.set_yscale("log")
    ax.set_xticks(list(range(len(plotted))))
    ax.set_xticklabels(labels, rotation=75, ha="right", fontsize=7)
    ax.set_ylabel("Association ares relative error")
    ax.set_title("Asymmetric binary closure propagation cases")
    ax.grid(axis="y", color="#d9d9d9", linewidth=0.6)
    fig.tight_layout()
    fig.savefig(FIGURE, dpi=160)
    plt.close(fig)
    SIDECAR.write_text(
        "kind: matplotlib-figure\nversion: 1\nplot_id: asymmetric_binary_closures\ntitle: Asymmetric binary closure propagation cases\nfiles:\n  figure: asymmetric_binary_closures.png\n  source_data: asymmetric_binary_closures_plotted_data.csv\n",
        encoding="utf-8",
    )
    print(FIGURE)


if __name__ == "__main__":
    main()
