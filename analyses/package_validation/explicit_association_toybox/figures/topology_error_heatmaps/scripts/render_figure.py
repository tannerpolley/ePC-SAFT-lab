from __future__ import annotations

import csv
import math
import statistics
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm

ANALYSIS_ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ANALYSIS_ROOT / "figures" / "topology_error_heatmaps" / "output"
HEATMAP = OUTPUT / "topology_error_heatmap.csv"
FIGURE = OUTPUT / "topology_error_heatmap.png"
PLOTTED = OUTPUT / "topology_error_heatmap_plotted_data.csv"
SIDECAR = OUTPUT / "topology_error_heatmap.mpl.yaml"


def main() -> None:
    rows = _load_rows()
    plotted = _plotted_rows(rows)
    OUTPUT.mkdir(parents=True, exist_ok=True)
    with PLOTTED.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(plotted[0]))
        writer.writeheader()
        writer.writerows(plotted)

    closures = sorted({row["closure_name"] for row in plotted})
    topologies = sorted({row["topology_id"] for row in plotted})
    rho_values = sorted({float(row["rho_delta"]) for row in plotted})
    columns = min(3, len(closures))
    rows_count = math.ceil(len(closures) / columns)
    fig, axes = plt.subplots(
        rows_count,
        columns,
        figsize=(4.1 * columns, 3.2 * rows_count),
        squeeze=False,
        constrained_layout=True,
    )
    values = [max(float(row["max_abs_ares_assoc_rel_error"]), 1.0e-14) for row in plotted]
    norm = LogNorm(vmin=min(values), vmax=max(values))
    image = None
    for ax, closure in zip(axes.ravel(), closures, strict=False):
        matrix = []
        for rho in rho_values:
            matrix_row = []
            for topology in topologies:
                match = next(
                    (
                        row
                        for row in plotted
                        if row["closure_name"] == closure
                        and row["topology_id"] == topology
                        and float(row["rho_delta"]) == rho
                    ),
                    None,
                )
                matrix_row.append(max(float(match["max_abs_ares_assoc_rel_error"]), 1.0e-14) if match else 1.0e-14)
            matrix.append(matrix_row)
        image = ax.imshow(matrix, aspect="auto", norm=norm, cmap="viridis")
        ax.set_title(closure, fontsize=9)
        ax.set_xticks(range(len(topologies)))
        ax.set_xticklabels(topologies, rotation=35, ha="right")
        ax.set_yticks(range(len(rho_values)))
        ax.set_yticklabels([f"{value:.3g}" for value in rho_values])
        ax.set_xlabel("Topology")
        ax.set_ylabel("rho * Delta")
    for ax in axes.ravel()[len(closures) :]:
        ax.axis("off")
    if image is not None:
        fig.colorbar(image, ax=axes.ravel().tolist(), shrink=0.82, label="Max |association ares relative error|")
    fig.suptitle("Topology-resolved explicit association closure error")
    fig.savefig(FIGURE, dpi=160)
    plt.close(fig)
    SIDECAR.write_text(
        "\n".join(
            (
                "kind: matplotlib-figure",
                "version: 1",
                "plot_id: explicit_association_topology_error_heatmap",
                "title: Topology-resolved explicit association closure error",
                "matplotlib:",
                "  title: Topology-resolved explicit association closure error",
                "  x_label: Huang/Radosz topology",
                "  y_label: rho * Delta",
                "  color_scale: log",
                "files:",
                "  figure: topology_error_heatmap.png",
                "  source_data: topology_error_heatmap_plotted_data.csv",
                "render:",
                "  command: uv run python analyses/package_validation/explicit_association_toybox/figures/topology_error_heatmaps/scripts/render_figure.py",
                "",
            )
        ),
        encoding="utf-8",
    )
    print(FIGURE)


def _load_rows() -> list[dict[str, str]]:
    with HEATMAP.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _plotted_rows(rows: list[dict[str, str]]) -> list[dict[str, object]]:
    grouped: dict[tuple[str, str, str], list[dict[str, str]]] = {}
    for row in rows:
        key = (row["topology_id"], row["closure_name"], row["rho_delta"])
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
