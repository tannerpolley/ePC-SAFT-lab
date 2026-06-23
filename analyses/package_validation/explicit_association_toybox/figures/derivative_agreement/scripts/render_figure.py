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
    ORANGE,
    apply_plot_style,
    case_label,
    closure_label,
    save_plot_artifacts,
    style_axis,
    target_label,
)

OUTPUT = ANALYSIS_ROOT / "figures" / "derivative_agreement" / "output"
SOURCE = OUTPUT / "derivative_agreement.csv"
PLOTTED = OUTPUT / "derivative_agreement_plotted_data.csv"
FIGURE = OUTPUT / "derivative_agreement.png"


def main() -> None:
    apply_plot_style()
    with SOURCE.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    plotted = [
        {
            "case_id": row["case_id"],
            "case_label": case_label(row["case_id"]),
            "closure_name": row["closure_name"],
            "closure_label": closure_label(row["closure_name"]),
            "target": row["target"],
            "target_label": target_label(row["target"]),
            "derivative_abs_error": row["derivative_abs_error"],
            "derivative_rel_error": row["derivative_rel_error"],
            "exact_derivative_method": row["exact_derivative_method"],
            "closure_derivative_method": row["closure_derivative_method"],
            "implicit_jacobian_condition_number": row["implicit_jacobian_condition_number"],
            "mass_action_residual_inf": row["mass_action_residual_inf"],
            "speedup_vs_exact_implicit": row["speedup_vs_exact_implicit"],
        }
        for row in rows
    ]
    OUTPUT.mkdir(parents=True, exist_ok=True)
    with PLOTTED.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(plotted[0]))
        writer.writeheader()
        writer.writerows(plotted)

    preferred_cases = ["pure_2b_moderate", "cross_binary_asymmetric"]
    remaining_cases = sorted({row["case_id"] for row in plotted} - set(preferred_cases))
    cases = [case for case in preferred_cases if any(row["case_id"] == case for row in plotted)]
    cases.extend(remaining_cases)
    fig, axes = plt.subplots(len(cases), 1, figsize=(9.8, 6.2), sharey=True, constrained_layout=True)
    if len(cases) == 1:
        axes = [axes]
    colors = [BLUE, ORANGE]
    for ax, color, case in zip(axes, colors, cases, strict=False):
        case_rows = [row for row in plotted if row["case_id"] == case]
        x = list(range(len(case_rows)))
        y = [max(float(row["derivative_rel_error"]), 1.0e-14) for row in case_rows]
        ax.scatter(x, y, marker="o", s=34, color=color, label=closure_label(case_rows[0]["closure_name"]))
        ax.set_xticks(x)
        ax.set_xticklabels([row["target_label"] for row in case_rows], rotation=20, ha="right")
        ax.set_yscale("log")
        ax.set_title(case_label(case), loc="left")
        ax.set_ylabel("relative error")
        style_axis(ax, minor=True)
        ax.legend(loc="upper right")
    axes[-1].set_xlabel("Derivative target")
    fig.suptitle(r"Picard derivative agreement against exact implicit sensitivities")
    save_plot_artifacts(fig, FIGURE)
    plt.close(fig)
    print(FIGURE)


if __name__ == "__main__":
    main()
