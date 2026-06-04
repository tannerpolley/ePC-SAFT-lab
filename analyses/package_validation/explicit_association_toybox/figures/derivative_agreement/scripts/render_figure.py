from __future__ import annotations

import csv
from pathlib import Path

import matplotlib.pyplot as plt

ANALYSIS_ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ANALYSIS_ROOT / "figures" / "derivative_agreement" / "output"
SOURCE = OUTPUT / "derivative_agreement.csv"
PLOTTED = OUTPUT / "derivative_agreement_plotted_data.csv"
FIGURE = OUTPUT / "derivative_agreement.png"
SIDECAR = OUTPUT / "derivative_agreement.mpl.yaml"


def main() -> None:
    with SOURCE.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    plotted = [
        {
            "case_id": row["case_id"],
            "closure_name": row["closure_name"],
            "target": row["target"],
            "derivative_abs_error": row["derivative_abs_error"],
            "derivative_rel_error": row["derivative_rel_error"],
            "speedup_vs_exact_implicit": row["speedup_vs_exact_implicit"],
        }
        for row in rows
    ]
    OUTPUT.mkdir(parents=True, exist_ok=True)
    with PLOTTED.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(plotted[0]))
        writer.writeheader()
        writer.writerows(plotted)
    labels = [f"{row['target']}\n{row['closure_name']}" for row in plotted]
    y = [max(float(row["derivative_rel_error"]), 1.0e-14) for row in plotted]
    fig, ax = plt.subplots(figsize=(11.0, 5.5))
    ax.bar(range(len(plotted)), y, color="#3d6f8e")
    ax.set_yscale("log")
    ax.set_xticks(list(range(len(plotted))))
    ax.set_xticklabels(labels, rotation=75, ha="right", fontsize=7)
    ax.set_ylabel("Derivative relative error")
    ax.set_title("Derivative agreement against exact implicit association")
    ax.grid(axis="y", color="#d9d9d9", linewidth=0.6)
    fig.tight_layout()
    fig.savefig(FIGURE, dpi=160)
    plt.close(fig)
    SIDECAR.write_text(
        "\n".join(
            (
                "kind: matplotlib-figure",
                "version: 1",
                "plot_id: derivative_agreement",
                "title: Derivative agreement against exact implicit association",
                "files:",
                "  figure: derivative_agreement.png",
                "  source_data: derivative_agreement_plotted_data.csv",
                "",
            )
        ),
        encoding="utf-8",
    )
    print(FIGURE)


if __name__ == "__main__":
    main()
