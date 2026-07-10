from __future__ import annotations

import sys as _bootstrap_sys
from pathlib import Path
from pathlib import Path as _BootstrapPath

for _candidate in _BootstrapPath(__file__).resolve().parents:
    if (_candidate / "scripts" / "plot_outputs.py").is_file():
        if str(_candidate) not in _bootstrap_sys.path:
            _bootstrap_sys.path.insert(0, str(_candidate))
        break
else:
    raise ModuleNotFoundError("Could not locate repo root containing scripts/plot_outputs.py")
import sys

import matplotlib.pyplot as plt

from scripts.plot_outputs import analysis_root

ANALYSIS_ROOT = analysis_root(__file__)
if str(ANALYSIS_ROOT) not in sys.path:
    sys.path.insert(0, str(ANALYSIS_ROOT))

from shared import _common as common
from shared import figure_data

OUTPUT = Path(__file__).with_name("figure_3.png")
SERIES_STYLE = {
    "data_water": {"color": common.GRAY_COLOR, "marker": "o", "facecolor": common.LIGHT_GRAY, "size": 28},
    "data_methanol": {"color": common.BLUE_COLOR, "marker": "^", "facecolor": common.BLUE_COLOR, "size": 34},
    "data_ethanol": {"color": common.GREEN_COLOR, "marker": "s", "facecolor": common.GREEN_COLOR, "size": 30},
}


def main() -> None:
    common.configure_style()
    rows = figure_data.read_payload("figure_3")
    fig, ax = plt.subplots(figsize=(4.2, 3.2))

    for series_id, style in SERIES_STYLE.items():
        x_data, y_data = figure_data.xy(figure_data.select_rows(rows, series_id=series_id))
        ax.scatter(
            x_data,
            y_data,
            s=style["size"],
            marker=style["marker"],
            facecolor=style["facecolor"],
            edgecolor=style["color"],
            linewidth=0.8,
        )

    x_grid, y_model = figure_data.xy(figure_data.select_rows(rows, series_id="model_empirical_ratio"))
    ax.plot(x_grid, y_model, color="black", linewidth=1.5)
    ax.set_xlim(0.0, 0.20)
    ax.set_ylim(0.0, 1.0)
    ax.set_xlabel(r"$x_{\mathrm{ion}}$ / mol mol$^{-1}$")
    ax.set_ylabel(r"$\epsilon_r / \epsilon_{r,\mathrm{solvent}}$ / -")
    common.save_figure(fig, OUTPUT)
    plt.close(fig)


if __name__ == "__main__":
    main()
