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
    GREEN,
    ORANGE,
    apply_plot_style,
    case_label,
    save_png_svg,
    style_axis,
    write_sidecar,
)

OUTPUT = ANALYSIS_ROOT / "figures" / "cppad_shaped_picard_derivative_evidence" / "output"
SOURCE = OUTPUT / "cppad_shaped_picard_derivative_evidence.csv"
PLOTTED = OUTPUT / "cppad_shaped_picard_derivative_evidence_plotted_data.csv"
FIGURE = OUTPUT / "cppad_shaped_picard_derivative_evidence.png"
SIDECAR = OUTPUT / "cppad_shaped_picard_derivative_evidence.mpl.yaml"
SELECTED_CASES = (
    "pure_2b_self",
    "cross_associating_binary",
    "mixed_2b_3b_binary",
    "mixed_2b_4c_binary",
    "mixed_4c_4c_binary",
)
ORDER_COLORS = {1: BLUE, 2: ORANGE}


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
    write_sidecar(
        SIDECAR,
        plot_id="cppad_shaped_picard_derivative_evidence",
        title="CppAD-shaped Picard derivative evidence",
        figure=FIGURE,
        source_data=PLOTTED,
        x_label="derivative target and local quadratic target",
        y_label="relative error",
        y_scale="log",
        command=(
            "uv run python analyses/package_validation/explicit_association_toybox/figures/"
            "cppad_shaped_picard_derivative_evidence/scripts/render_figure.py"
        ),
    )
    print(FIGURE)


def _plotted_rows(rows: list[dict[str, str]]) -> list[dict[str, object]]:
    plotted = [
        {
            "case_id": row["case_id"],
            "case_label": case_label(row["case_id"]),
            "target": row["target"],
            "target_label": _target_label(row["target"]),
            "derivative_order": int(row["derivative_order"]),
            "relative_error": max(float(row["relative_error"]), 1.0e-14),
            "absolute_error": float(row["absolute_error"]),
            "admission_band": row["admission_band"],
            "baseline_status": row["baseline_status"],
            "cppad_relevance_note": row["cppad_relevance_note"],
        }
        for row in rows
        if row["case_id"] in SELECTED_CASES
    ]
    if not plotted:
        raise ValueError("CppAD-shaped derivative plotting received no retained rows.")
    return plotted


def _render(rows: list[dict[str, object]]) -> None:
    cases = [case for case in SELECTED_CASES if any(row["case_id"] == case for row in rows)]
    fig, axes = plt.subplots(len(cases), 1, figsize=(10.8, 12.0), sharey=True, constrained_layout=True)
    if len(cases) == 1:
        axes = [axes]
    for axis, case in zip(axes, cases, strict=True):
        case_rows = [row for row in rows if row["case_id"] == case]
        x = list(range(len(case_rows)))
        y = [float(row["relative_error"]) for row in case_rows]
        colors = [GREEN if row["target"] == "local_quadratic_prediction" else ORDER_COLORS[int(row["derivative_order"])] for row in case_rows]
        axis.plot(x, y, color="#6b7280", linestyle=":", linewidth=1.3)
        axis.scatter(x, y, color=colors, marker="o", s=34, zorder=3)
        axis.set_yscale("log")
        axis.set_title(case_label(case), loc="left")
        axis.set_ylabel("relative error")
        axis.set_xticks(x)
        axis.set_xticklabels([str(row["target_label"]) for row in case_rows], rotation=22, ha="right")
        style_axis(axis, minor=True)
    axes[0].legend(
        handles=[
            Line2D([0], [0], marker="o", color="none", markerfacecolor=BLUE, label="first derivative"),
            Line2D([0], [0], marker="o", color="none", markerfacecolor=ORANGE, label="second derivative"),
            Line2D([0], [0], marker="o", color="none", markerfacecolor=GREEN, label="local quadratic"),
        ],
        frameon=False,
        loc="upper right",
    )
    axes[-1].set_xlabel("Derivative target")
    fig.suptitle("JAX Picard derivatives against exact implicit baselines")
    save_png_svg(fig, FIGURE)
    plt.close(fig)


def _target_label(name: str) -> str:
    labels = {
        "a_assoc_density": r"$\partial a^{\mathrm{assoc}}/\partial\rho$",
        "a_assoc_strength": r"$\partial a^{\mathrm{assoc}}/\partial\Delta$",
        "pressure_proxy_density": r"$\partial P_{\mathrm{proxy}}/\partial\rho$",
        "a_assoc_density_density": r"$\partial^2 a^{\mathrm{assoc}}/\partial\rho^2$",
        "a_assoc_density_strength": r"$\partial^2 a^{\mathrm{assoc}}/\partial\rho\,\partial\Delta$",
        "a_assoc_strength_strength": r"$\partial^2 a^{\mathrm{assoc}}/\partial\Delta^2$",
        "a_assoc_composition_0": r"$\partial a^{\mathrm{assoc}}/\partial x_1$",
        "fugacity_proxy_composition_0": r"$\partial f_{\mathrm{proxy}}/\partial x_1$",
        "a_assoc_composition_0_0": r"$\partial^2 a^{\mathrm{assoc}}/\partial x_1^2$",
        "local_quadratic_prediction": r"$m(p)$ local quadratic",
    }
    return labels.get(name, name.replace("_", " "))


if __name__ == "__main__":
    main()
