from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import yaml


FIGURE_ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = FIGURE_ROOT / "results"
PLOT_ID = "associating_saturation_scope"
SOURCE_CSV = RESULTS_DIR / f"{PLOT_ID}.csv"
PLOTTED_CSV = RESULTS_DIR / f"{PLOT_ID}_plotted_data.csv"
SIDECAR = RESULTS_DIR / f"{PLOT_ID}.mpl.yaml"
PNG = RESULTS_DIR / f"{PLOT_ID}.png"
SVG = RESULTS_DIR / f"{PLOT_ID}.svg"


def _strip_svg_trailing_whitespace(path: Path) -> None:
    lines = path.read_text(encoding="utf-8").splitlines()
    path.write_text("\n".join(line.rstrip() for line in lines) + "\n", encoding="utf-8")


def _plot_rows(frame: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for row in frame.to_dict("records"):
        rows.append(
            {
                "component": row["component"],
                "T_K": row["T_K"],
                "quantity": "saturation pressure",
                "series_role": "NIST reference",
                "value": row["p_sat_nist_Pa"],
                "route_status": row["route_status"],
            }
        )
        rows.append(
            {
                "component": row["component"],
                "T_K": row["T_K"],
                "quantity": "saturated liquid density",
                "series_role": "NIST reference",
                "value": row["rho_sat_liq_nist_mol_m3"],
                "route_status": row["route_status"],
            }
        )
    return pd.DataFrame(rows)


def main() -> int:
    frame = pd.read_csv(SOURCE_CSV)
    metadata = yaml.safe_load(SIDECAR.read_text(encoding="utf-8"))
    plotted = _plot_rows(frame)
    plotted.to_csv(PLOTTED_CSV, index=False)
    plt.rcParams["svg.hashsalt"] = PLOT_ID

    colors = {"methanol": "#8b3f97", "water": "#1f6f78"}
    labels = {"methanol": "Methanol", "water": "Water"}
    markers = {"methanol": "o", "water": "s"}
    plt.rcParams.update(
        {
            "font.family": "serif",
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.titleweight": "semibold",
            "figure.dpi": 150,
        }
    )
    fig, axes = plt.subplots(
        1,
        2,
        figsize=tuple(metadata["matplotlib"]["figsize"]),
        constrained_layout=True,
    )
    pressure_ax, density_ax = axes
    for component in ("methanol", "water"):
        subset = frame[frame["component"] == component].sort_values("T_K")
        color = colors[component]
        label = labels[component]
        pressure_ax.plot(
            subset["T_K"],
            subset["p_sat_nist_Pa"] / 1000.0,
            color=color,
            marker=markers[component],
            markersize=4.0,
            linewidth=1.8,
            label=label,
        )
        density_ax.plot(
            subset["T_K"],
            subset["rho_sat_liq_nist_mol_m3"] / 1000.0,
            color=color,
            marker=markers[component],
            markersize=4.0,
            linewidth=1.8,
            label=label,
        )

    pressure_ax.set_yscale("log")
    pressure_ax.set_xlabel(metadata["matplotlib"]["xlabel"])
    pressure_ax.set_ylabel(metadata["matplotlib"]["pressure_ylabel"])
    pressure_ax.grid(True, which="major", color="#d7dce2", linewidth=0.7, alpha=0.85)
    pressure_ax.grid(True, which="minor", color="#edf0f3", linewidth=0.45, alpha=0.65)
    pressure_ax.legend(frameon=False, loc="best")

    density_ax.set_xlabel(metadata["matplotlib"]["xlabel"])
    density_ax.set_ylabel(metadata["matplotlib"]["density_ylabel"])
    density_ax.grid(True, which="major", color="#d7dce2", linewidth=0.7, alpha=0.85)
    density_ax.legend(frameon=False, loc="best")
    density_ax.text(
        0.02,
        0.03,
        "production route rejects 2B association",
        transform=density_ax.transAxes,
        fontsize=9,
        color="#44484d",
    )

    fig.suptitle(metadata["matplotlib"]["title"], fontsize=13)
    fig.savefig(PNG, bbox_inches="tight")
    fig.savefig(SVG, bbox_inches="tight", metadata={"Date": None})
    _strip_svg_trailing_whitespace(SVG)
    print(f"wrote {PNG}")
    print(f"wrote {SVG}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
