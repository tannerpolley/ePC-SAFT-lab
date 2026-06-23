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
    apply_plot_style,
    case_label,
    closure_label,
    log_fit_line,
    save_plot_artifacts,
    style_axis,
)

OUTPUT = ANALYSIS_ROOT / "figures" / "closure_accuracy" / "output"
METRICS = OUTPUT / "closure_metrics.csv"
FIGURE = OUTPUT / "closure_accuracy_summary.png"
PLOTTED = OUTPUT / "closure_accuracy_summary_plotted_data.csv"


def _load_rows() -> list[dict[str, str]]:
    with METRICS.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def main() -> None:
    apply_plot_style()
    rows = _load_rows()
    plotted = [
        {
            "system": row["system"],
            "closure": row["closure"],
            "closure_label": closure_label(row["closure"]),
            "density": row["density"],
            "strength": row["strength"],
            "rho_delta": float(row["density"]) * float(row["strength"]),
            "assoc_helmholtz_rel_error": row["assoc_helmholtz_rel_error"],
            "ares_total_rel_error": row["ares_total_rel_error"],
            "speedup_ratio": row["speedup_ratio"],
        }
        for row in rows
    ]
    OUTPUT.mkdir(parents=True, exist_ok=True)
    with PLOTTED.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(plotted[0]))
        writer.writeheader()
        writer.writerows(plotted)

    systems = sorted({row["system"] for row in plotted})
    colors = [BLUE, ORANGE, GREEN]
    fig, axes = plt.subplots(1, 2, figsize=(10.8, 4.4), sharex=True, constrained_layout=True)
    for color, system in zip(colors, systems, strict=False):
        system_rows = sorted((row for row in plotted if row["system"] == system), key=lambda row: row["rho_delta"])
        x = [row["rho_delta"] for row in system_rows]
        assoc = [max(float(row["assoc_helmholtz_rel_error"]), 1.0e-14) for row in system_rows]
        total = [max(float(row["ares_total_rel_error"]), 1.0e-14) for row in system_rows]
        label = case_label(system)
        axes[0].scatter(x, assoc, s=34, color=color, label=label)
        axes[1].scatter(x, total, s=34, color=color, label=label)
        assoc_fit_x, assoc_fit_y = log_fit_line(x, assoc)
        total_fit_x, total_fit_y = log_fit_line(x, total)
        if assoc_fit_x:
            axes[0].plot(assoc_fit_x, assoc_fit_y, linewidth=1.2, color=color, alpha=0.72)
        if total_fit_x:
            axes[1].plot(total_fit_x, total_fit_y, linewidth=1.2, color=color, alpha=0.72)

    for ax in axes:
        ax.set_xscale("log")
        ax.set_yscale("log")
        ax.axhline(3.0e-2, color="#111827", linewidth=0.9, linestyle="--", label="3% reference")
        ax.set_xlabel(r"$\rho\Delta$")
        style_axis(ax, minor=True)
    axes[0].set_title(r"Association Helmholtz error")
    axes[0].set_ylabel(r"relative error in $a_{\mathrm{assoc}}$")
    axes[1].set_title(r"Total residual Helmholtz error")
    axes[1].set_ylabel(r"relative error in $a_{\mathrm{res}}$")
    axes[1].legend(fontsize=8, loc="lower left")
    fig.suptitle(f"{closure_label(plotted[0]['closure'])} closure accuracy")

    save_plot_artifacts(fig, FIGURE)
    plt.close(fig)
    print(FIGURE)


if __name__ == "__main__":
    main()
