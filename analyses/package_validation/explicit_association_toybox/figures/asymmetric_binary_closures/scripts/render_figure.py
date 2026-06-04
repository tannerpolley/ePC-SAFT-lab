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

OUTPUT = ANALYSIS_ROOT / "figures" / "asymmetric_binary_closures" / "output"
SOURCE = OUTPUT / "asymmetric_binary_closures.csv"
PLOTTED = OUTPUT / "asymmetric_binary_closures_plotted_data.csv"
FIGURE = OUTPUT / "asymmetric_binary_closures.png"
SIDECAR = OUTPUT / "asymmetric_binary_closures.mpl.yaml"


def main() -> None:
    apply_plot_style()
    with SOURCE.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    plotted = [
        {
            "case_id": row["case_id"],
            "case_role": row["case_role"],
            "case_label": case_label(row["case_id"]),
            "closure_name": row["closure_name"],
            "closure_label": closure_label(row["closure_name"]),
            "ares_assoc_rel_error": row["ares_assoc_rel_error"],
            "mass_action_residual_inf": row["mass_action_residual_inf"],
            "speedup_vs_exact_implicit": row["speedup_vs_exact_implicit"],
            "evidence_band": row["evidence_band"],
        }
        for row in rows
    ]
    plotted.sort(key=lambda row: float(row["ares_assoc_rel_error"]))
    OUTPUT.mkdir(parents=True, exist_ok=True)
    with PLOTTED.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(plotted[0]))
        writer.writeheader()
        writer.writerows(plotted)

    y = list(range(len(plotted)))
    labels = [row["case_label"] for row in plotted]
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.8), sharey=True, constrained_layout=True)
    axes[0].scatter(
        [max(float(row["ares_assoc_rel_error"]), 1.0e-14) for row in plotted],
        y,
        color=BLUE,
        s=52,
        label=closure_label(plotted[0]["closure_name"]),
    )
    axes[0].set_xscale("log")
    axes[0].set_xlabel(r"relative error in $a_{\mathrm{assoc}}$")
    axes[0].set_yticks(y)
    axes[0].set_yticklabels(labels)
    axes[0].set_title("Association error")
    style_axis(axes[0], grid_axis="x", minor=True)

    axes[1].scatter(
        [float(row["speedup_vs_exact_implicit"]) for row in plotted],
        y,
        color=ORANGE,
        s=52,
    )
    axes[1].set_xlabel("speedup vs exact implicit")
    axes[1].set_title("Timing")
    style_axis(axes[1], grid_axis="x")

    fig.suptitle("Asymmetric mixture diagnostics for Picard closure")
    save_png_svg(fig, FIGURE)
    plt.close(fig)
    write_sidecar(
        SIDECAR,
        plot_id="asymmetric_binary_closures",
        title="Asymmetric mixture diagnostics for Picard closure",
        figure=FIGURE,
        source_data=PLOTTED,
        x_label="association error and speedup",
        y_label="case",
        y_scale="linear",
        command="uv run python analyses/package_validation/explicit_association_toybox/figures/asymmetric_binary_closures/scripts/render_figure.py",
    )
    print(FIGURE)


if __name__ == "__main__":
    main()
