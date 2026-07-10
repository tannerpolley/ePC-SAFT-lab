from __future__ import annotations

import sys as _bootstrap_sys
from functools import lru_cache
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

OUTPUT = Path(__file__).with_name("figure_9.png")
PANELS = figure_data.FIG9_PANELS
DEFAULT_TARGETS = [
    (
        0.8,
        common.ORGANIC_COLOR,
        "^",
        common.ORGANIC_COLOR,
        "-",
        r"Model, $w_{org}^{salt-free}=0.8$",
        r"$w_{org}^{salt-free}=0.8$",
    ),
    (
        0.4,
        common.GREEN_COLOR,
        "s",
        common.GREEN_COLOR,
        "-",
        r"Model, $w_{org}^{salt-free}=0.4$",
        r"$w_{org}^{salt-free}=0.4$",
    ),
]


@lru_cache(maxsize=1)
def _payload():
    return tuple(figure_data.read_payload("figure_9"))


def _series_xy(series_id: str, panel_id: str):
    return figure_data.xy(figure_data.select_rows(list(_payload()), panel_id=panel_id, series_id=series_id))


def _plot_panel(ax, label: str, salt: str, solvent_system: str, m_max: float) -> None:
    for target_w, marker_color, marker, line_color, line_style, line_label, data_label_text in DEFAULT_TARGETS:
        target_token = f"{target_w:.1f}"
        m_grid, y_model = _series_xy(f"model_{salt}_{solvent_system}_w{target_token}", label)
        ax.plot(
            m_grid,
            y_model,
            color=line_color,
            linestyle=line_style,
            linewidth=2.2,
            zorder=5,
            label=line_label,
        )

        data_m, data_y = _series_xy(f"data_{salt}_{solvent_system}_w{target_token}", label)
        if data_m:
            ax.scatter(
                data_m,
                data_y,
                s=24,
                marker=marker,
                facecolor="none",
                edgecolor=marker_color,
                linewidth=1.0,
                zorder=6,
                label=data_label_text,
            )

    organic = next(s for s in solvent_system.split("-") if s != "water")
    organic_label = "methanol" if organic == "methanol" else "ethanol"
    ax.set_xlim(0.0, m_max)
    ax.set_ylim(0.0, 1.125)
    ax.set_title(f"{salt} in aqueous {organic_label}", fontsize=10, pad=8)
    ax.set_xlabel(r"$\bar{m}_{salt}$ / mol kg$^{-1}$", labelpad=4)
    ax.set_ylabel(r"$\gamma_{\pm}^{m,*}$ of salt / -", labelpad=4)


def main() -> None:
    common.configure_style()
    fig, axes = plt.subplots(2, 2, figsize=(9.3, 8.1))
    for ax, cfg in zip(axes.flat, PANELS):
        _plot_panel(ax, *cfg)
    handles = [
        plt.Line2D([0], [0], color=common.ORGANIC_COLOR, linewidth=2.2, label=r"Model, $w_{org}^{salt-free}=0.8$"),
        plt.Line2D(
            [0],
            [0],
            marker="^",
            linestyle="None",
            markerfacecolor="none",
            markeredgecolor=common.ORGANIC_COLOR,
            color=common.ORGANIC_COLOR,
            label=r"$w_{org}^{salt-free}=0.8$",
        ),
        plt.Line2D([0], [0], color=common.GREEN_COLOR, linewidth=2.2, label=r"Model, $w_{org}^{salt-free}=0.4$"),
        plt.Line2D(
            [0],
            [0],
            marker="s",
            linestyle="None",
            markerfacecolor="none",
            markeredgecolor=common.GREEN_COLOR,
            color=common.GREEN_COLOR,
            label=r"$w_{org}^{salt-free}=0.4$",
        ),
    ]
    fig.legend(handles=handles, loc="upper center", ncol=2, bbox_to_anchor=(0.5, 0.965), fontsize=9)
    fig.suptitle(
        "Molality-based salt mean ionic activity coefficients $\\gamma_{\\pm}^{m,*}$ in aqueous-organic solvent mixtures",
        fontsize=12,
        y=0.995,
    )
    fig.subplots_adjust(left=0.08, right=0.98, bottom=0.08, top=0.86, wspace=0.20, hspace=0.28)
    common.save_figure(fig, OUTPUT)
    plt.close(fig)


if __name__ == "__main__":
    main()
