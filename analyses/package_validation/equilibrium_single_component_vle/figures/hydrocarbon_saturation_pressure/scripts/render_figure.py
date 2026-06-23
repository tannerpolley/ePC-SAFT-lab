from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def _repo_root() -> Path:
    for parent in Path(__file__).resolve().parents:
        if (parent / "pyproject.toml").is_file() and (parent / "data" / "reference").is_dir():
            return parent
    raise RuntimeError("Could not locate repository root from the figure script path.")


REPO_ROOT = _repo_root()
FIGURE_ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = FIGURE_ROOT / "results"
PLOT_ID = "hydrocarbon_saturation_pressure"
SOURCE_CSV = RESULTS_DIR / f"{PLOT_ID}.csv"
PLOTTED_CSV = RESULTS_DIR / f"{PLOT_ID}_plotted_data.csv"
PNG = RESULTS_DIR / f"{PLOT_ID}.png"
SVG = RESULTS_DIR / f"{PLOT_ID}.svg"
PDF = RESULTS_DIR / f"{PLOT_ID}.pdf"
PLOT_METADATA = {
    "title": "Single-component VLE route vs NIST saturation pressure",
    "xlabel": "temperature, $T$ / K",
    "ylabel": "saturation pressure, $p_{sat}$ / kPa",
    "error_ylabel": "relative error / %",
    "density_error_ylabel": "liquid-density error / %",
    "figsize": (11.0, 7.8),
}


def _strip_svg_trailing_whitespace(path: Path) -> None:
    lines = path.read_text(encoding="utf-8").splitlines()
    path.write_text("\n".join(line.rstrip() for line in lines) + "\n", encoding="utf-8")


def _plot_rows(frame: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for row in frame.to_dict("records"):
        rows.append(
            {
                "species": row["species"],
                "T_K": row["T_K"],
                "quantity": "pressure",
                "series_role": "NIST reference",
                "value": row["p_sat_nist_Pa"],
            }
        )
        rows.append(
            {
                "species": row["species"],
                "T_K": row["T_K"],
                "quantity": "pressure",
                "series_role": "single_component_vle route",
                "value": row["p_sat_route_Pa"],
            }
        )
        rows.append(
            {
                "species": row["species"],
                "T_K": row["T_K"],
                "quantity": "absolute relative error",
                "series_role": "absolute relative error",
                "value": row["absolute_relative_error_percent"],
            }
        )
        rows.append(
            {
                "species": row["species"],
                "T_K": row["T_K"],
                "quantity": "liquid density",
                "series_role": "NIST reference",
                "value": row["rho_sat_liq_nist_kg_m3"],
            }
        )
        rows.append(
            {
                "species": row["species"],
                "T_K": row["T_K"],
                "quantity": "liquid density",
                "series_role": "single_component_vle route",
                "value": row["rho_liquid_route_kg_m3"],
            }
        )
        rows.append(
            {
                "species": row["species"],
                "T_K": row["T_K"],
                "quantity": "liquid density absolute relative error",
                "series_role": "liquid density absolute relative error",
                "value": row["rho_sat_liq_absolute_relative_error_percent"],
            }
        )
    return pd.DataFrame(rows)


def main() -> int:
    frame = pd.read_csv(SOURCE_CSV)
    plotted = _plot_rows(frame)
    plotted.to_csv(PLOTTED_CSV, index=False)
    plt.rcParams["svg.hashsalt"] = PLOT_ID

    species_order = ["Methane", "Ethane", "Propane"]
    colors = {"Methane": "#1b4f9c", "Ethane": "#c44e24", "Propane": "#2f7d50"}
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
        3,
        3,
        figsize=PLOT_METADATA["figsize"],
        sharex="col",
        constrained_layout=True,
        gridspec_kw={"height_ratios": [2.2, 1.0, 1.0]},
    )
    for col, species in enumerate(species_order):
        subset = frame[frame["species"] == species].sort_values("T_K")
        color = colors[species]
        pressure_ax = axes[0, col]
        error_ax = axes[1, col]
        density_ax = axes[2, col]
        pressure_ax.plot(
            subset["T_K"],
            subset["p_sat_route_Pa"] / 1000.0,
            color=color,
            linewidth=2.0,
            label="Route",
        )
        pressure_ax.scatter(
            subset["T_K"],
            subset["p_sat_nist_Pa"] / 1000.0,
            facecolors="white",
            edgecolors=color,
            linewidths=1.4,
            s=34,
            label="NIST",
            zorder=3,
        )
        pressure_ax.set_yscale("log")
        pressure_ax.set_title(species)
        pressure_ax.grid(True, which="major", color="#d7dce2", linewidth=0.7, alpha=0.85)
        pressure_ax.grid(True, which="minor", color="#edf0f3", linewidth=0.45, alpha=0.65)
        error_ax.axhline(0.0, color="#53565a", linewidth=0.8)
        error_ax.plot(
            subset["T_K"],
            subset["relative_error_percent"],
            color=color,
            marker="o",
            markersize=3.5,
            linewidth=1.4,
        )
        error_ax.grid(True, which="major", color="#d7dce2", linewidth=0.7, alpha=0.85)
        density_ax.axhline(0.0, color="#53565a", linewidth=0.8)
        density_ax.plot(
            subset["T_K"],
            subset["rho_sat_liq_relative_error_percent"],
            color=color,
            marker="s",
            markersize=3.2,
            linewidth=1.25,
        )
        density_ax.grid(True, which="major", color="#d7dce2", linewidth=0.7, alpha=0.85)
        density_ax.set_xlabel(PLOT_METADATA["xlabel"])
        if col == 0:
            pressure_ax.set_ylabel(PLOT_METADATA["ylabel"])
            error_ax.set_ylabel(PLOT_METADATA["error_ylabel"])
            density_ax.set_ylabel(PLOT_METADATA["density_error_ylabel"])
        if col == 2:
            pressure_ax.legend(frameon=False, loc="best")

    fig.suptitle(PLOT_METADATA["title"], fontsize=13)
    fig.savefig(PNG, bbox_inches="tight")
    fig.savefig(SVG, bbox_inches="tight", metadata={"Date": None})
    fig.savefig(PDF, bbox_inches="tight")
    _strip_svg_trailing_whitespace(SVG)
    print(f"wrote {PNG}")
    print(f"wrote {SVG}")
    print(f"wrote {PDF}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
