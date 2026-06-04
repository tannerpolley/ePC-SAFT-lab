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
    GREEN,
    RED,
    apply_plot_style,
    case_label,
    closure_label,
    save_png_svg,
    style_axis,
    write_sidecar,
)

OUTPUT = ANALYSIS_ROOT / "figures" / "total_eos_impact" / "output"
SOURCE = OUTPUT / "total_eos_impact.csv"
PLOTTED = OUTPUT / "total_eos_impact_plotted_data.csv"
FIGURE = OUTPUT / "total_eos_impact.png"
SIDECAR = OUTPUT / "total_eos_impact.mpl.yaml"


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

    fig, ax = plt.subplots(figsize=(8.0, 4.8))
    colors = {"candidate_accuracy": GREEN, "reject_for_provider_path": RED}
    for row in plotted:
        x = float(row["speedup_vs_exact_implicit"])
        y = max(float(row["pressure_proxy_rel_error"]), 1.0e-14)
        ax.scatter(x, y, color=colors.get(row["evidence_band"], "#684f9e"), s=70)
        ax.annotate(row["case_label"], (x, y), textcoords="offset points", xytext=(6, 5), fontsize=8)
    ax.set_yscale("log")
    ax.set_xlabel("speedup vs exact implicit")
    ax.set_ylabel(r"relative error in $P_{\mathrm{proxy}}$")
    ax.set_title(f"Total EOS propagation: {closure_label(plotted[0]['closure_name'])}")
    style_axis(ax, minor=True)
    fig.tight_layout()
    save_png_svg(fig, FIGURE)
    plt.close(fig)
    write_sidecar(
        SIDECAR,
        plot_id="total_eos_impact",
        title="Total EOS propagation for Picard closure",
        figure=FIGURE,
        source_data=PLOTTED,
        x_label="speedup vs exact implicit",
        y_label="relative error in P_proxy",
        y_scale="log",
        command="uv run python analyses/package_validation/explicit_association_toybox/figures/total_eos_impact/scripts/render_figure.py",
    )
    print(FIGURE)


if __name__ == "__main__":
    main()
