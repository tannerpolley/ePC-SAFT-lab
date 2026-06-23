from __future__ import annotations

import csv
import sys
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

ANALYSIS_ROOT = Path(__file__).resolve().parents[3]
REPO_ROOT = ANALYSIS_ROOT.parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from analyses.package_validation.explicit_association_toybox.scripts.plot_style import (
    BLUE,
    ORANGE,
    apply_plot_style,
    case_label,
    save_plot_artifacts,
    style_axis,
)

OUTPUT = ANALYSIS_ROOT / "figures" / "jax_picard_derivatives" / "output"
SOURCE = OUTPUT / "jax_picard_derivatives.csv"
PLOTTED = OUTPUT / "jax_picard_derivatives_plotted_data.csv"
FIGURE = OUTPUT / "jax_picard_derivatives.png"


def main() -> None:
    apply_plot_style()
    with SOURCE.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    plotted = [
        {
            "case_id": row["case_id"],
            "case_label": case_label(row["case_id"]),
            "target": row["target"],
            "target_label": _target_label(row["target"]),
            "derivative_order": row["derivative_order"],
            "rel_error": row["rel_error"],
            "abs_error": row["abs_error"],
            "implicit_jacobian_condition_number": row["implicit_jacobian_condition_number"],
            "mass_action_residual_inf": row["mass_action_residual_inf"],
            "exact_implicit_elapsed_seconds": row["exact_implicit_elapsed_seconds"],
            "picard_jax_elapsed_seconds": row["picard_jax_elapsed_seconds"],
            "speedup_vs_exact_implicit": row["speedup_vs_exact_implicit"],
            "autodiff_backend": row["autodiff_backend"],
        }
        for row in rows
    ]
    OUTPUT.mkdir(parents=True, exist_ok=True)
    with PLOTTED.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(plotted[0]))
        writer.writeheader()
        writer.writerows(plotted)

    preferred_cases = ["pure_2b_moderate", "cross_binary_asymmetric"]
    cases = [case for case in preferred_cases if any(row["case_id"] == case for row in plotted)]
    fig, axes = plt.subplots(len(cases), 1, figsize=(9.8, 6.2), sharey=True, constrained_layout=True)
    if len(cases) == 1:
        axes = [axes]
    colors = {1: BLUE, 2: ORANGE}
    for axis, case in zip(axes, cases, strict=True):
        case_rows = [row for row in plotted if row["case_id"] == case]
        x = list(range(len(case_rows)))
        y = [max(float(row["rel_error"]), 1.0e-14) for row in case_rows]
        point_colors = [colors[int(row["derivative_order"])] for row in case_rows]
        axis.plot(x, y, linestyle=":", linewidth=1.4, color="#6b7280")
        axis.scatter(x, y, marker="o", s=34, color=point_colors)
        axis.set_xticks(x)
        axis.set_xticklabels([row["target_label"] for row in case_rows], rotation=20, ha="right")
        axis.set_yscale("log")
        axis.set_title(case_label(case), loc="left")
        axis.set_ylabel("relative error")
        style_axis(axis, minor=True)
    axes[0].legend(
        handles=[
            Line2D([0], [0], marker="o", color="none", markerfacecolor=BLUE, label="first derivative"),
            Line2D([0], [0], marker="o", color="none", markerfacecolor=ORANGE, label="second derivative"),
        ],
        loc="upper right",
        frameon=False,
    )
    axes[-1].set_xlabel("JAX derivative target")
    fig.suptitle("JAX Picard derivatives against exact implicit sensitivities")
    save_plot_artifacts(fig, FIGURE)
    plt.close(fig)
    print(FIGURE)


def _target_label(name: str) -> str:
    labels = {
        "density": r"$\partial a_{\mathrm{assoc}}/\partial \rho$",
        "strength": r"$\partial a_{\mathrm{assoc}}/\partial \Delta$",
        "composition": r"$\partial a_{\mathrm{assoc}}/\partial x_1$",
        "density_density": r"$\partial^2 a_{\mathrm{assoc}}/\partial \rho^2$",
        "density_strength": r"$\partial^2 a_{\mathrm{assoc}}/\partial \rho\,\partial\Delta$",
        "strength_strength": r"$\partial^2 a_{\mathrm{assoc}}/\partial \Delta^2$",
        "composition_composition": r"$\partial^2 a_{\mathrm{assoc}}/\partial x_1^2$",
    }
    return labels.get(name, name.replace("_", " "))


if __name__ == "__main__":
    main()
