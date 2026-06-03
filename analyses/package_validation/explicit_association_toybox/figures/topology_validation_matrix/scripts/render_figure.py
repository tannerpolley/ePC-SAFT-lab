from __future__ import annotations

import csv
from pathlib import Path

import matplotlib.pyplot as plt

ANALYSIS_ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ANALYSIS_ROOT / "figures" / "topology_validation_matrix" / "output"
MATRIX = OUTPUT / "topology_matrix.csv"
FIGURE = OUTPUT / "topology_validation_matrix.png"
PLOTTED = OUTPUT / "topology_validation_matrix_plotted_data.csv"
SIDECAR = OUTPUT / "topology_validation_matrix.mpl.yaml"


def main() -> None:
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
            "max_abs_assoc_helmholtz_rel_error": value,
        }
        for (topology, role), value in sorted(grouped.items())
    ]
    OUTPUT.mkdir(parents=True, exist_ok=True)
    with PLOTTED.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(plotted_rows[0]))
        writer.writeheader()
        writer.writerows(plotted_rows)

    roles = sorted({row["comparison_role"] for row in plotted_rows})
    topologies = sorted({row["paper_topology_type"] for row in plotted_rows})
    offsets = {role: idx - (len(roles) - 1) / 2.0 for idx, role in enumerate(roles)}
    colors = {
        "exact_topology_reduction": "#2f6f9f",
        "explicit_approximation": "#b35c1e",
        "diagnostic_collapse": "#7a5aa6",
    }

    fig, ax = plt.subplots(figsize=(9, 4.8))
    for role in roles:
        xs: list[float] = []
        ys: list[float] = []
        for idx, topology in enumerate(topologies):
            match = next(
                (
                    row
                    for row in plotted_rows
                    if row["paper_topology_type"] == topology and row["comparison_role"] == role
                ),
                None,
            )
            if match is None:
                continue
            xs.append(idx + 0.18 * offsets[role])
            ys.append(float(match["max_abs_assoc_helmholtz_rel_error"]))
        ax.scatter(xs, ys, label=role, color=colors.get(role, "#404040"), s=42)
    ax.set_xticks(range(len(topologies)))
    ax.set_xticklabels(topologies)
    ax.set_yscale("symlog", linthresh=1.0e-8)
    ax.set_title("Huang/Radosz topology validation matrix")
    ax.set_xlabel("Table VII topology")
    ax.set_ylabel("Max absolute relative association Helmholtz error")
    ax.grid(axis="y", color="#d9d9d9", linewidth=0.6)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(FIGURE, dpi=160)
    plt.close(fig)
    SIDECAR.write_text(
        "\n".join(
            (
                "kind: matplotlib-figure",
                "version: 1",
                "plot_id: explicit_association_topology_validation_matrix",
                "title: Huang/Radosz topology validation matrix",
                "matplotlib:",
                "  title: Huang/Radosz topology validation matrix",
                "  x_label: Table VII topology",
                "  y_label: Max absolute relative association Helmholtz error",
                "  y_scale: symlog",
                "files:",
                "  figure: topology_validation_matrix.png",
                "  source_data: topology_validation_matrix_plotted_data.csv",
                "render:",
                "  command: uv run python analyses/package_validation/explicit_association_toybox/figures/topology_validation_matrix/scripts/render_figure.py",
                "",
            )
        ),
        encoding="utf-8",
    )
    print(FIGURE)


def _load_rows() -> list[dict[str, str]]:
    with MATRIX.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


if __name__ == "__main__":
    main()
