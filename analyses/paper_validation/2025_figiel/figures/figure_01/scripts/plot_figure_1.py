from __future__ import annotations

from pathlib import Path
import sys as _bootstrap_sys
from pathlib import Path as _BootstrapPath

for _candidate in _BootstrapPath(__file__).resolve().parents:
    if (_candidate / "scripts" / "plot_outputs.py").is_file():
        if str(_candidate) not in _bootstrap_sys.path:
            _bootstrap_sys.path.insert(0, str(_candidate))
        break
else:
    raise ModuleNotFoundError("Could not locate repo root containing scripts/plot_outputs.py")
from scripts.plot_outputs import analysis_root
import sys

import matplotlib.pyplot as plt

ANALYSIS_ROOT = analysis_root(__file__)
if str(ANALYSIS_ROOT) not in sys.path:
    sys.path.insert(0, str(ANALYSIS_ROOT))

from shared import _common as common
from shared import figure_data

OUTPUT = Path(__file__).with_name("figure_1.png")


def main() -> None:
    common.configure_style()
    rows = figure_data.read_payload("figure_1")
    x_values, y_values = figure_data.xy(figure_data.select_rows(rows, series_id="profile"))
    fig, ax = plt.subplots(figsize=(4.2, 3.2))
    ax.plot(x_values, y_values, color="black", linewidth=1.8)
    ax.set_xlim(0.0, 2.0)
    ax.set_ylim(0.0, 100.0)
    ax.set_xticks([0.0, 1.0, 2.0])
    ax.set_xticklabels([r"$r_i$", r"$r_i + \Delta r_i$", ""])
    ax.set_yticks([0.0, 25.0, 50.0, 75.0, 100.0])
    ax.set_ylabel(r"$\epsilon_r$ / -")
    ax.text(0.28, 12.5, r"$\epsilon_{r,\mathrm{ion}}$", fontsize=10)
    ax.text(1.42, 80.5, r"$\epsilon_{r,\mathrm{bulk}}$", fontsize=10)
    common.save_figure(fig, OUTPUT)
    plt.close(fig)


if __name__ == "__main__":
    main()
