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
    save_png_svg,
    style_axis,
    write_sidecar,
)

OUTPUT = ANALYSIS_ROOT / "figures" / "hessian_agreement" / "output"
SOURCE = OUTPUT / "hessian_agreement.csv"
PLOTTED = OUTPUT / "hessian_agreement_plotted_data.csv"
FIGURE = OUTPUT / "hessian_agreement.png"
SIDECAR = OUTPUT / "hessian_agreement.mpl.yaml"


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
            "target": row["target_pair"],
            "target_label": _hessian_target_label(row["target_pair"]),
            "hessian_abs_error": row["absolute_error"],
            "hessian_rel_error": row["relative_error"],
            "finite_difference_step": row["finite_difference_step"],
            "baseline_status": row["baseline_status"],
            "autodiff_backend": row["autodiff_backend"],
            "implicit_jacobian_condition_number": row["implicit_jacobian_condition_number"],
            "mass_action_residual_inf": row["mass_action_residual_inf"],
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
    remaining_cases = sorted({row["case_id"] for row in plotted} - set(cases))
    cases.extend(remaining_cases)
    fig, axes = plt.subplots(len(cases), 1, figsize=(9.8, 6.2), sharey=True, constrained_layout=True)
    if len(cases) == 1:
        axes = [axes]
    colors = [BLUE, ORANGE]
    for axis, color, case in zip(axes, colors, cases, strict=False):
        case_rows = [row for row in plotted if row["case_id"] == case]
        x = list(range(len(case_rows)))
        y = [max(float(row["hessian_rel_error"]), 1.0e-14) for row in case_rows]
        axis.plot(
            x,
            y,
            marker="o",
            linestyle=":",
            linewidth=1.6,
            markersize=4.5,
            color=color,
            label=closure_label(case_rows[0]["closure_name"]),
        )
        axis.set_xticks(x)
        axis.set_xticklabels([row["target_label"] for row in case_rows], rotation=20, ha="right")
        axis.set_yscale("log")
        axis.set_title(case_label(case), loc="left")
        axis.set_ylabel("relative error")
        style_axis(axis, minor=True)
        axis.legend(loc="upper right", frameon=False)
    axes[-1].set_xlabel("Hessian target")
    fig.suptitle(r"Picard Hessian agreement against exact implicit sensitivities")
    save_png_svg(fig, FIGURE)
    plt.close(fig)
    write_sidecar(
        SIDECAR,
        plot_id="hessian_agreement",
        title="Picard Hessian agreement against exact implicit sensitivities",
        figure=FIGURE,
        source_data=PLOTTED,
        x_label="Hessian target",
        y_label="relative Hessian error",
        y_scale="log",
        command="uv run python analyses/package_validation/explicit_association_toybox/figures/hessian_agreement/scripts/render_figure.py",
    )
    print(FIGURE)


def _hessian_target_label(name: str) -> str:
    labels = {
        "density_density": r"$\partial^2 a_{\mathrm{assoc}}/\partial \rho^2$",
        "density_strength": r"$\partial^2 a_{\mathrm{assoc}}/\partial \rho\,\partial\Delta$",
        "strength_strength": r"$\partial^2 a_{\mathrm{assoc}}/\partial \Delta^2$",
        "composition_composition": r"$\partial^2 a_{\mathrm{assoc}}/\partial x_1^2$",
    }
    return labels.get(name, name.replace("_", " "))


if __name__ == "__main__":
    main()
