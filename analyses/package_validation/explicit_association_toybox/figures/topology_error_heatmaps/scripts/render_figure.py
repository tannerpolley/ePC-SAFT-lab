from __future__ import annotations

import csv
import statistics
import sys
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm

ANALYSIS_ROOT = Path(__file__).resolve().parents[3]
REPO_ROOT = ANALYSIS_ROOT.parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from analyses.package_validation.explicit_association_toybox.scripts.plot_style import (
    apply_plot_style,
    save_plot_artifacts,
)

OUTPUT = ANALYSIS_ROOT / "figures" / "topology_error_heatmaps" / "output"
HEATMAP = OUTPUT / "topology_error_heatmap.csv"
FIGURE = OUTPUT / "topology_error_heatmap.png"
PLOTTED = OUTPUT / "topology_error_heatmap_plotted_data.csv"


def main() -> None:
    apply_plot_style()
    rows = _load_rows()
    plotted = _plotted_rows(rows)
    OUTPUT.mkdir(parents=True, exist_ok=True)
    with PLOTTED.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(plotted[0]))
        writer.writeheader()
        writer.writerows(plotted)

    topologies = sorted({row["paper_topology_type"] for row in plotted})
    rho_values = sorted({float(row["rho_delta"]) for row in plotted})
    matrix = []
    for rho in rho_values:
        matrix_row = []
        for topology in topologies:
            match = next(
                (
                    row
                    for row in plotted
                    if row["paper_topology_type"] == topology and float(row["rho_delta"]) == rho
                ),
                None,
            )
            matrix_row.append(max(float(match["max_abs_ares_assoc_rel_error"]), 1.0e-14) if match else 1.0e-14)
        matrix.append(matrix_row)
    values = [value for row in matrix for value in row]
    norm = LogNorm(vmin=max(min(values), 1.0e-14), vmax=max(values))
    fig, ax = plt.subplots(figsize=(8.4, 5.6), constrained_layout=True)
    image = ax.imshow(matrix, aspect="auto", norm=norm, cmap="viridis")
    ax.set_title(r"Picard association error across topology and $\rho\Delta$")
    ax.set_xticks(range(len(topologies)))
    ax.set_xticklabels(topologies)
    ax.set_yticks(range(len(rho_values)))
    ax.set_yticklabels([f"{value:.3g}" for value in rho_values])
    ax.set_xlabel("Huang/Radosz topology")
    ax.set_ylabel(r"$\rho\Delta$")
    fig.colorbar(image, ax=ax, shrink=0.84, label=r"max relative error in $a_{\mathrm{assoc}}$")
    save_plot_artifacts(fig, FIGURE)
    plt.close(fig)
    print(FIGURE)


def _load_rows() -> list[dict[str, str]]:
    with HEATMAP.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _plotted_rows(rows: list[dict[str, str]]) -> list[dict[str, object]]:
    grouped: dict[tuple[str, str], list[dict[str, str]]] = {}
    for row in rows:
        if row["closure_name"] != "damped_picard_7_05":
            continue
        key = (row["paper_topology_type"], row["rho_delta"])
        grouped.setdefault(key, []).append(row)
    plotted: list[dict[str, object]] = []
    for key in sorted(grouped):
        group = grouped[key]
        representative = group[0]
        plotted.append(
            {
                "topology_id": representative["topology_id"],
                "paper_topology_type": representative["paper_topology_type"],
                "closure_name": representative["closure_name"],
                "closure_label": "Picard",
                "rho_delta": float(representative["rho_delta"]),
                "max_abs_ares_assoc_rel_error": max(abs(float(row["ares_assoc_rel_error"])) for row in group),
                "max_mass_action_residual_inf": max(float(row["mass_action_residual_inf"]) for row in group),
                "median_exact_implicit_elapsed_seconds": statistics.median(
                    float(row["exact_implicit_elapsed_seconds"]) for row in group
                ),
                "median_closure_elapsed_seconds": statistics.median(
                    float(row["closure_elapsed_seconds"]) for row in group
                ),
                "evidence_band": representative["evidence_band"],
            }
        )
    return plotted


if __name__ == "__main__":
    main()
