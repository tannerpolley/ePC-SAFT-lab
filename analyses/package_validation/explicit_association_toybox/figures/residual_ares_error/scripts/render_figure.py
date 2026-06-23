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

OUTPUT = ANALYSIS_ROOT / "figures" / "residual_ares_error" / "output"
METRICS = OUTPUT / "residual_ares_metrics.csv"
FIGURE = OUTPUT / "residual_ares_error_summary.png"
PLOTTED = OUTPUT / "residual_ares_error_summary_plotted_data.csv"


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
            "rho_delta": float(row["density"]) * float(row["strength"]),
            "ares_total_rel_error": row["ares_total_rel_error"],
            "max_ares_total_rel_error": row["ares_total_rel_error"],
            "assoc_helmholtz_rel_error": row["assoc_helmholtz_rel_error"],
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
    fig, ax = plt.subplots(figsize=(8.6, 4.8))
    for color, system in zip(colors, systems, strict=False):
        system_rows = sorted((row for row in plotted if row["system"] == system), key=lambda row: row["rho_delta"])
        x = [row["rho_delta"] for row in system_rows]
        y = [max(float(row["ares_total_rel_error"]), 1.0e-14) for row in system_rows]
        ax.scatter(x, y, s=34, color=color, label=case_label(system))
        fit_x, fit_y = log_fit_line(x, y)
        if fit_x:
            ax.plot(fit_x, fit_y, linewidth=1.2, color=color, alpha=0.72)
    ax.axhline(3.0e-2, color="#111827", linewidth=0.9, linestyle="--", label="3% reference")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_title(r"Total residual Helmholtz error from association closure")
    ax.set_xlabel(r"$\rho\Delta$")
    ax.set_ylabel(r"relative error in $a_{\mathrm{res}}$")
    style_axis(ax, minor=True)
    ax.legend(fontsize=8)
    fig.tight_layout()
    save_plot_artifacts(fig, FIGURE)
    plt.close(fig)
    print(FIGURE)


if __name__ == "__main__":
    main()
