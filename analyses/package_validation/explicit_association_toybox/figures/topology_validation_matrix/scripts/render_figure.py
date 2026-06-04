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
    role_label,
    save_png_svg,
    style_axis,
    write_sidecar,
)

OUTPUT = ANALYSIS_ROOT / "figures" / "topology_validation_matrix" / "output"
MATRIX = OUTPUT / "topology_matrix.csv"
FIGURE = OUTPUT / "topology_validation_matrix.png"
PLOTTED = OUTPUT / "topology_validation_matrix_plotted_data.csv"
SIDECAR = OUTPUT / "topology_validation_matrix.mpl.yaml"


def main() -> None:
    apply_plot_style()
    rows = _load_rows()
    grouped: dict[tuple[str, str], float] = {}
    for row in rows:
        key = (row["paper_topology_type"], row["comparison_role"])
        value = abs(float(row["assoc_helmholtz_rel_error"]))
        grouped[key] = max(grouped.get(key, 0.0), value)

    plotted_rows = [
        {
            "paper_topology_type": topology,
            "comparison_role": role,
            "comparison_label": role_label(role),
            "max_abs_assoc_helmholtz_rel_error": value,
        }
        for (topology, role), value in sorted(grouped.items())
    ]
    OUTPUT.mkdir(parents=True, exist_ok=True)
    with PLOTTED.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(plotted_rows[0]))
        writer.writeheader()
        writer.writerows(plotted_rows)

    topologies = sorted({row["paper_topology_type"] for row in plotted_rows})
    roles = ["exact_topology_reduction", "explicit_approximation"]
    colors = {"exact_topology_reduction": BLUE, "explicit_approximation": ORANGE}

    fig, ax = plt.subplots(figsize=(8.2, 4.8))
    for role in roles:
        values = []
        for topology in topologies:
            match = next(
                (
                    row
                    for row in plotted_rows
                    if row["paper_topology_type"] == topology and row["comparison_role"] == role
                ),
                None,
            )
            values.append(max(float(match["max_abs_assoc_helmholtz_rel_error"]), 1.0e-14) if match else 1.0e-14)
        ax.plot(
            range(len(topologies)),
            values,
            marker="o",
            linewidth=1.8,
            color=colors[role],
            label=role_label(role),
        )
    ax.set_xticks(range(len(topologies)))
    ax.set_xticklabels(topologies)
    ax.set_yscale("log")
    ax.set_title("Huang/Radosz topology validation")
    ax.set_xlabel("Table VII topology")
    ax.set_ylabel(r"max relative error in $a_{\mathrm{assoc}}$")
    style_axis(ax, minor=True)
    ax.legend()
    fig.tight_layout()
    save_png_svg(fig, FIGURE)
    plt.close(fig)
    write_sidecar(
        SIDECAR,
        plot_id="explicit_association_topology_validation_matrix",
        title="Huang/Radosz topology validation",
        figure=FIGURE,
        source_data=PLOTTED,
        x_label="Table VII topology",
        y_label="max relative error in a_assoc",
        y_scale="log",
        command="uv run python analyses/package_validation/explicit_association_toybox/figures/topology_validation_matrix/scripts/render_figure.py",
    )
    print(FIGURE)


def _load_rows() -> list[dict[str, str]]:
    with MATRIX.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


if __name__ == "__main__":
    main()
