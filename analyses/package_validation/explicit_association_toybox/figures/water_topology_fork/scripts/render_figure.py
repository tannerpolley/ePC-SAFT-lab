from __future__ import annotations

import csv
from pathlib import Path

import matplotlib.pyplot as plt

ANALYSIS_ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ANALYSIS_ROOT / "figures" / "water_topology_fork" / "output"
SOURCE = OUTPUT / "water_topology_fork.csv"
PLOTTED = OUTPUT / "water_topology_fork_plotted_data.csv"
FIGURE = OUTPUT / "water_topology_fork.png"
SIDECAR = OUTPUT / "water_topology_fork.mpl.yaml"


def main() -> None:
    with SOURCE.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    plotted = [
        {
            "case_id": row["case_id"],
            "assigned_topology": row["assigned_topology"],
            "rigorous_topology": row["rigorous_topology"],
            "temperature_k": row["temperature_k"],
            "pressure_residual_mpa": row["pressure_residual_mpa"],
            "z_residual_abs": row["z_residual_abs"],
            "water_diagnostic_role": row["water_diagnostic_role"],
        }
        for row in rows
    ]
    OUTPUT.mkdir(parents=True, exist_ok=True)
    with PLOTTED.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(plotted[0]))
        writer.writeheader()
        writer.writerows(plotted)
    fig, ax = plt.subplots(figsize=(8.6, 5.0))
    x = [float(row["temperature_k"]) for row in plotted]
    y = [abs(float(row["pressure_residual_mpa"])) for row in plotted]
    ax.scatter(x, y, c=["#b35c1e" if row["water_diagnostic_role"] == "fixed_state_warning" else "#3d6f8e" for row in plotted], s=58)
    ax.set_yscale("log")
    ax.set_xlabel("Temperature K")
    ax.set_ylabel("Absolute pressure residual MPa")
    ax.set_title("Water topology fork fixed-state warnings")
    ax.grid(color="#d9d9d9", linewidth=0.6)
    fig.tight_layout()
    fig.savefig(FIGURE, dpi=160)
    plt.close(fig)
    SIDECAR.write_text(
        "kind: matplotlib-figure\nversion: 1\nplot_id: water_topology_fork\ntitle: Water topology fork fixed-state warnings\nfiles:\n  figure: water_topology_fork.png\n  source_data: water_topology_fork_plotted_data.csv\n",
        encoding="utf-8",
    )
    print(FIGURE)


if __name__ == "__main__":
    main()
