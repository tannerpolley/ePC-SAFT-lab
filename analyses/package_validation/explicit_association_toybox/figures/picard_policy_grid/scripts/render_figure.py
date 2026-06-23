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
    PURPLE,
    RED,
    apply_plot_style,
    case_label,
    save_plot_artifacts,
    style_axis,
)

OUTPUT = ANALYSIS_ROOT / "figures" / "picard_policy_grid" / "output"
SOURCE = OUTPUT / "picard_policy_grid.csv"
PLOTTED = OUTPUT / "picard_policy_grid_plotted_data.csv"
FIGURE = OUTPUT / "picard_policy_grid.png"
SELECTED_CASES = (
    "pure_2b_self",
    "water_like_3b_topology",
    "asymmetric_donor_acceptor_binary",
    "mixed_2b_4c_binary",
)
TARGETS = (
    ("association_helmholtz_relative_error", r"$a^{\mathrm{assoc}}$ rel. error"),
    ("derivative_max_relative_error", "max deriv. rel. error"),
)
LAMBDA_COLORS = {
    0.35: BLUE,
    0.5: ORANGE,
    0.65: GREEN,
    0.8: PURPLE,
    1.0: RED,
}


def main() -> None:
    apply_plot_style()
    with SOURCE.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    plotted = _plotted_rows(rows)
    OUTPUT.mkdir(parents=True, exist_ok=True)
    with PLOTTED.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(plotted[0]))
        writer.writeheader()
        writer.writerows(plotted)
    _render(plotted)
    print(FIGURE)


def _plotted_rows(rows: list[dict[str, str]]) -> list[dict[str, object]]:
    plotted: list[dict[str, object]] = []
    for row in rows:
        if row["case_id"] not in SELECTED_CASES:
            continue
        for target, label in TARGETS:
            plotted.append(
                {
                    "case_id": row["case_id"],
                    "case_label": case_label(row["case_id"]),
                    "target": target,
                    "target_label": label,
                    "step_count": int(row["step_count"]),
                    "damping": float(row["damping"]),
                    "relative_error": max(float(row[target]), 1.0e-14),
                    "pareto_band": row["pareto_band"],
                    "candidate_policy_label": row["candidate_policy_label"],
                }
            )
    if not plotted:
        raise ValueError("Picard policy-grid plotting received no retained rows.")
    return plotted


def _render(rows: list[dict[str, object]]) -> None:
    fig, axes = plt.subplots(
        len(SELECTED_CASES),
        len(TARGETS),
        figsize=(10.8, 11.6),
        sharex=True,
        constrained_layout=True,
    )
    for row_index, case_id in enumerate(SELECTED_CASES):
        for col_index, (target, target_label) in enumerate(TARGETS):
            axis = axes[row_index, col_index]
            target_rows = [
                row
                for row in rows
                if row["case_id"] == case_id and row["target"] == target
            ]
            for damping in sorted({float(row["damping"]) for row in target_rows}):
                damping_rows = sorted(
                    [row for row in target_rows if float(row["damping"]) == damping],
                    key=lambda item: int(item["step_count"]),
                )
                axis.plot(
                    [int(row["step_count"]) for row in damping_rows],
                    [float(row["relative_error"]) for row in damping_rows],
                    marker="o",
                    linestyle=(0, (1.2, 1.8)),
                    color=LAMBDA_COLORS[damping],
                    linewidth=1.5,
                    markersize=4.0,
                    label=fr"$\lambda={damping:g}$",
                )
            axis.set_yscale("log")
            axis.set_title(f"{case_label(case_id)} - {target_label}", loc="left")
            axis.set_ylabel("relative error")
            axis.set_xticks([3, 5, 7, 9, 11])
            style_axis(axis, minor=True)
    for axis in axes[-1, :]:
        axis.set_xlabel("Picard steps")
    axes[0, 0].legend(frameon=False, loc="best", ncol=2)
    fig.suptitle("Fixed-depth Picard policy grid against exact implicit association")
    save_plot_artifacts(fig, FIGURE)
    plt.close(fig)


if __name__ == "__main__":
    main()
