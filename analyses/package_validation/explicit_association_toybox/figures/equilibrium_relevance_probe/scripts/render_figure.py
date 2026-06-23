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
    save_plot_artifacts,
    style_axis,
)

OUTPUT = ANALYSIS_ROOT / "figures" / "equilibrium_relevance_probe" / "output"
SOURCE = OUTPUT / "equilibrium_relevance_probe.csv"
PLOTTED = OUTPUT / "equilibrium_relevance_probe_plotted_data.csv"
FIGURE = OUTPUT / "equilibrium_relevance_probe.png"

ERROR_METRICS = (
    ("objective_abs_error", r"$|\Delta \Phi|$"),
    ("gradient_absolute_error_norm", r"$\|\Delta \nabla \Phi\|_2$"),
    ("hessian_absolute_error_norm", r"$\|\Delta H_\Phi\|_F$"),
    ("picard_mass_action_residual_norm", r"$\|r_{\mathrm{MA}}\|_\infty$"),
)


def build_plotted_rows(rows: list[dict[str, str]]) -> list[dict[str, object]]:
    plotted: list[dict[str, object]] = []
    for row in rows:
        for metric_name, metric_label in ERROR_METRICS:
            plotted.append(
                {
                    "case_id": row["case_id"],
                    "case_label": case_label(row["case_id"]),
                    "metric": metric_name,
                    "metric_label": metric_label,
                    "metric_value": float(row[metric_name]),
                    "admission_status": row["admission_status"],
                    "evidence_band": row["evidence_band"],
                    "closure_name": row["closure_name"],
                }
            )
    if not plotted:
        raise ValueError("equilibrium relevance plotting received no retained rows.")
    return plotted


def main() -> None:
    apply_plot_style()
    rows = _read_rows(SOURCE)
    plotted = build_plotted_rows(rows)
    _write_plotted_data(plotted)
    _render(plotted)
    print(FIGURE)


def _read_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise FileNotFoundError(
            "equilibrium_relevance_probe.csv is required before rendering; run generate_data.py first."
        )
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _write_plotted_data(rows: list[dict[str, object]]) -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    with PLOTTED.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def _render(rows: list[dict[str, object]]) -> None:
    fig, axis = plt.subplots(figsize=(7.0, 4.6), constrained_layout=True)
    x_values = list(range(len(ERROR_METRICS)))
    y_values = []
    labels = []
    for metric_name, metric_label in ERROR_METRICS:
        matches = [row for row in rows if row["metric"] == metric_name]
        value = max(float(matches[0]["metric_value"]), 1.0e-14)
        y_values.append(value)
        labels.append(metric_label)
    axis.plot(
        x_values,
        y_values,
        marker="o",
        linestyle=":",
        linewidth=1.8,
        markersize=5.5,
        color=ORANGE,
        label="Picard vs exact implicit",
    )
    axis.axhline(1.0e-2, color=BLUE, linestyle=(0, (1.2, 1.8)), linewidth=1.2, label=r"$10^{-2}$ guide")
    axis.set_yscale("log")
    axis.set_xticks(x_values)
    axis.set_xticklabels(labels)
    axis.set_ylabel("absolute error or residual norm")
    axis.set_xlabel("local objective diagnostic")
    axis.set_title(str(rows[0]["case_label"]), loc="left")
    style_axis(axis, minor=True)
    axis.legend(frameon=False, loc="best")
    save_plot_artifacts(fig, FIGURE)
    plt.close(fig)


if __name__ == "__main__":
    main()
