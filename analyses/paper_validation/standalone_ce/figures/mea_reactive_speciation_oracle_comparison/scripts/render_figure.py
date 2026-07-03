from __future__ import annotations

import math
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.animation import FuncAnimation, PillowWriter
from matplotlib.lines import Line2D

FIGURE_DIR = Path(__file__).resolve().parents[1]
RESULTS_DIR = FIGURE_DIR / "results"
PLOT_DATA_PATH = RESULTS_DIR / "mea_ce_oracle_speciation_plot_data.csv"
ERRORS_PATH = RESULTS_DIR / "mea_ce_oracle_speciation_errors.csv"
SUMMARY_PATH = RESULTS_DIR / "mea_ce_oracle_speciation_error_summary.csv"
TRACE_SUMMARY_PATH = RESULTS_DIR / "mea_ce_continuation_trace_summary.csv"
NONIDEAL_PLOT_DATA_PATH = RESULTS_DIR / "mea_ce_eos_x_gamma_speciation_plot_data.csv"
NONIDEAL_ANIMATION_DATA_PATH = RESULTS_DIR / "mea_ce_eos_x_gamma_speciation_temperature_sweep_animation_data.csv"
DPI = 300
FIGURE_CREATOR = "ePC-SAFT standalone CE validation"
ANIMATION_STEM = "mea_ce_eos_x_gamma_speciation_temperature_sweep_model_only"
ANIMATION_FPS = 8

PLOT_SPECIES = (
    "CO2",
    "MEA",
    "MEAH+",
    "MEACOO-",
    "HCO3-",
    "CO3^2-",
    "H3O+",
    "OH-",
    "MEA + MEAH+",
)
NONIDEAL_SPECIES_GROUPS = {
    "concentrated": {
        "species": ("MEA", "MEAH+", "MEACOO-", "HCO3-", "MEA + MEAH+"),
        "ylim": (1.0e-6, 3.0e-1),
        "title_fragment": "concentrated species",
    },
    "trace": {
        "species": ("CO2", "CO3^2-", "H3O+", "OH-"),
        "ylim": (1.0e-14, 5.0e-2),
        "title_fragment": "trace and minor species",
    },
}
SPECIES_LABELS = {
    "CO2": r"$CO_2$",
    "MEA": r"$MEA$",
    "MEAH+": r"$MEAH^+$",
    "MEACOO-": r"$MEACOO^-$",
    "HCO3-": r"$HCO_3^-$",
    "CO3^2-": r"$CO_3^{2-}$",
    "H3O+": r"$H_3O^+$",
    "OH-": r"$OH^-$",
    "MEA + MEAH+": r"$MEA + MEAH^+$",
    "H2O": r"$H_2O$",
}
SPECIES_COLORS = {
    "CO2": "#1b8a5a",
    "MEA": "#245db5",
    "MEAH+": "#b7bf10",
    "MEACOO-": "#d9232e",
    "HCO3-": "#20bac5",
    "CO3^2-": "#8e62c7",
    "H3O+": "#99584a",
    "OH-": "#7f7f7f",
    "MEA + MEAH+": "#df6bc4",
}
DATA_SOURCE_MARKERS = {
    "Bottinger": "o",
    "Jakobsen": "s",
    "Matin": "^",
}


def _require_csv(path: Path) -> pd.DataFrame:
    if not path.is_file():
        raise FileNotFoundError(f"required plotted data file is missing: {path}")
    return pd.read_csv(path)


def _save_bundle(fig: plt.Figure, stem: str) -> None:
    for suffix in ("svg", "png", "pdf"):
        path = RESULTS_DIR / f"{stem}.{suffix}"
        fig.savefig(path, dpi=DPI, bbox_inches="tight", metadata=_save_metadata(suffix))
        if suffix == "svg":
            _strip_svg_trailing_whitespace(path)
    sidecar = "\n".join(
        [
            "figure:",
            f"  title: {stem}",
            f"  png: {stem}.png",
            f"  svg: {stem}.svg",
            f"  pdf: {stem}.pdf",
            f"  dpi: {DPI}",
            "style:",
            "  source: analyses/paper_validation/standalone_ce/figures/mea_reactive_speciation_oracle_comparison/scripts/render_figure.py",
            "",
        ]
    )
    (RESULTS_DIR / f"{stem}.mpl.yaml").write_text(sidecar, encoding="utf-8")


def _save_metadata(suffix: str) -> dict[str, object]:
    if suffix == "pdf":
        return {"Creator": FIGURE_CREATOR, "CreationDate": None, "ModDate": None}
    if suffix == "svg":
        return {"Creator": FIGURE_CREATOR, "Date": None}
    if suffix == "png":
        return {"Software": FIGURE_CREATOR}
    raise ValueError(f"unexpected figure suffix: {suffix}")


def _strip_svg_trailing_whitespace(path: Path) -> None:
    lines = path.read_text(encoding="utf-8").splitlines()
    path.write_text("\n".join(line.rstrip() for line in lines) + "\n", encoding="utf-8")


def _apply_axes_style(ax: plt.Axes) -> None:
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(True, which="major", axis="y", color="#d8d8d8", linewidth=0.6)
    ax.tick_params(axis="both", labelsize=10)


def _plot_temperature_overlay(
    plot_data: pd.DataFrame,
    temperature_C: float,
    *,
    title: str,
    ce_label: str,
    stem: str,
) -> None:
    frame = plot_data[plot_data["temperature_C"] == temperature_C]
    if frame.empty:
        raise ValueError(f"no plot data rows found for {temperature_C:g} C")

    plt.rcParams.update(
        {
            "font.family": "serif",
            "mathtext.fontset": "dejavuserif",
            "svg.hashsalt": "epcsaft-standalone-ce-mea-oracle-comparison",
            "axes.labelsize": 11,
            "axes.titlesize": 13,
            "legend.fontsize": 9,
        }
    )
    fig, ax = plt.subplots(figsize=(10.0, 6.2))
    for species in PLOT_SPECIES:
        color = SPECIES_COLORS[species]
        source = frame[(frame["role"] == "source_oracle") & (frame["species"] == species)].sort_values("CO2_loading")
        ce = frame[(frame["role"] == "ce_unassisted_pointwise") & (frame["species"] == species)].sort_values("CO2_loading")
        if source.empty or ce.empty:
            raise ValueError(f"missing source or CE rows for {species} at {temperature_C:g} C")
        ax.plot(
            source["CO2_loading"],
            source["mole_fraction"].clip(lower=1.0e-30),
            color=color,
            linestyle=(0, (4, 2)),
            linewidth=1.8,
            alpha=0.75,
        )
        ax.plot(
            ce["CO2_loading"],
            ce["mole_fraction"].clip(lower=1.0e-30),
            color=color,
            linestyle="-",
            linewidth=1.2,
            marker="o",
            markersize=2.2,
            markevery=16,
        )
    ax.set_title(title)
    ax.set_xlabel(r"$CO_2$ loading, mol $CO_2$/mol MEA")
    ax.set_ylabel("True-species mole fraction")
    ax.set_yscale("log")
    ax.set_xlim(0.0, 0.8)
    ax.set_ylim(1.0e-14, 1.0)
    _apply_axes_style(ax)
    species_handles = [
        Line2D([0], [0], color=SPECIES_COLORS[species], linewidth=2.0, label=SPECIES_LABELS[species])
        for species in PLOT_SPECIES
    ]
    role_handles = [
        Line2D([0], [0], color="#333333", linestyle=(0, (4, 2)), linewidth=1.8, label="Smith-Missen oracle"),
        Line2D(
            [0],
            [0],
            color="#333333",
            linestyle="-",
            marker="o",
            linewidth=1.2,
            markersize=3.0,
            label=ce_label,
        ),
    ]
    role_legend = ax.legend(handles=role_handles, loc="lower left", frameon=True)
    ax.add_artist(role_legend)
    ax.legend(
        handles=species_handles,
        title="Species",
        loc="center left",
        bbox_to_anchor=(1.01, 0.5),
        frameon=True,
    )
    fig.subplots_adjust(right=0.78)
    _save_bundle(fig, stem)
    plt.close(fig)


def _plot_nonideal_temperature_group(
    plot_data: pd.DataFrame,
    temperature_C: float,
    *,
    group_key: str,
) -> None:
    frame = plot_data[plot_data["temperature_C"] == temperature_C]
    if frame.empty:
        raise ValueError(f"no nonideal plot data rows found for {temperature_C:g} C")
    group = NONIDEAL_SPECIES_GROUPS[group_key]
    species_group = tuple(group["species"])

    plt.rcParams.update(
        {
            "font.family": "serif",
            "mathtext.fontset": "dejavuserif",
            "svg.hashsalt": "epcsaft-standalone-ce-mea-eos-x-gamma-speciation",
            "axes.labelsize": 11,
            "axes.titlesize": 13,
            "legend.fontsize": 9,
        }
    )
    fig, ax = plt.subplots(figsize=(10.0, 6.2))
    for species in species_group:
        color = SPECIES_COLORS[species]
        activity = frame[
            (frame["role"] == "eos_x_gamma_activity")
            & (frame["species"] == species)
        ].sort_values("CO2_loading")
        data = frame[
            (frame["role"] == "real_speciation_data")
            & (frame["species"] == species)
        ].sort_values("CO2_loading")
        if activity.empty:
            raise ValueError(f"missing eos_x_gamma rows for {species} at {temperature_C:g} C")
        ax.plot(
            activity["CO2_loading"],
            activity["mole_fraction"].clip(lower=1.0e-30),
            color=color,
            linestyle="--",
            linewidth=1.8,
            alpha=0.9,
        )
        for source, source_rows in data.groupby("data_source", sort=True):
            marker = DATA_SOURCE_MARKERS.get(str(source), "D")
            ax.scatter(
                source_rows["CO2_loading"],
                source_rows["mole_fraction"].clip(lower=1.0e-30),
                marker=marker,
                s=38.0,
                facecolors="white",
                edgecolors=color,
                linewidths=1.2,
                zorder=4,
            )
    ax.set_title(f"Nonideal ePC-SAFT activity speciation, {group['title_fragment']}, {temperature_C:g} C")
    ax.set_xlabel(r"$CO_2$ loading, mol $CO_2$/mol MEA")
    ax.set_ylabel("True-species mole fraction")
    ax.set_yscale("log")
    max_loading = float(frame["CO2_loading"].max())
    ax.set_xlim(0.0, min(1.0, math.ceil(max_loading * 20.0) / 20.0))
    ax.set_ylim(*group["ylim"])
    _apply_axes_style(ax)
    species_handles = [
        Line2D(
            [0],
            [0],
            color=SPECIES_COLORS[species],
            linestyle="--",
            linewidth=2.0,
            label=SPECIES_LABELS[species],
        )
        for species in species_group
    ]
    role_handles = [
        Line2D(
            [0],
            [0],
            color="#333333",
            linestyle="--",
            linewidth=1.8,
            label=r"ePC-SAFT $a_i=\gamma_i x_i$ fit",
        ),
    ]
    plotted_data = frame[
        (frame["role"] == "real_speciation_data")
        & frame["species"].isin(species_group)
    ]
    data_sources = sorted(str(item) for item in plotted_data["data_source"].dropna().unique())
    for source in data_sources:
        role_handles.append(
            Line2D(
                [0],
                [0],
                color="#333333",
                marker=DATA_SOURCE_MARKERS.get(source, "D"),
                linestyle="",
                markerfacecolor="white",
                markeredgewidth=1.2,
                markersize=6.0,
                label=source,
            )
        )
    role_legend = ax.legend(handles=role_handles, loc="lower left", frameon=True)
    ax.add_artist(role_legend)
    ax.legend(
        handles=species_handles,
        title="Species",
        loc="center left",
        bbox_to_anchor=(1.01, 0.5),
        frameon=True,
    )
    fig.subplots_adjust(right=0.78)
    _save_bundle(fig, f"mea_ce_eos_x_gamma_speciation_{group_key}_{int(temperature_C)}C")
    plt.close(fig)


def _require_nonideal_animation_frame_data() -> pd.DataFrame:
    frame_data = _require_csv(NONIDEAL_ANIMATION_DATA_PATH)
    required_columns = {
        "role",
        "activity_mode",
        "temperature_C",
        "CO2_loading",
        "species",
        "mole_fraction",
        "solve_accepted",
    }
    missing_columns = sorted(required_columns - set(frame_data.columns))
    if missing_columns:
        raise ValueError(f"animation solve data is missing required columns: {missing_columns}")
    if set(frame_data["role"]) != {"eos_x_gamma_activity_temperature_sweep"}:
        raise ValueError(f"unexpected animation roles: {sorted(frame_data['role'].unique())}")
    if not frame_data["solve_accepted"].astype(bool).all():
        raise ValueError("animation solve data contains rejected CE solve rows")
    expected_species = set(PLOT_SPECIES)
    for temperature_C, rows in frame_data.groupby("temperature_C", sort=True):
        missing_species = sorted(expected_species - set(rows["species"]))
        if missing_species:
            raise ValueError(f"animation data for {temperature_C:g} C is missing species: {missing_species}")
    return frame_data


def _plot_nonideal_temperature_sweep_animation() -> None:
    frame_data = _require_nonideal_animation_frame_data()
    frame_temperatures = sorted(float(value) for value in frame_data["temperature_C"].dropna().unique())
    if not frame_temperatures:
        raise ValueError("animation solve data contains no temperatures")
    plt.rcParams.update(
        {
            "font.family": "serif",
            "mathtext.fontset": "dejavuserif",
            "axes.labelsize": 11,
            "axes.titlesize": 13,
            "legend.fontsize": 9,
        }
    )
    fig, ax = plt.subplots(figsize=(10.0, 6.2))
    line_by_species: dict[str, Line2D] = {}
    for species in PLOT_SPECIES:
        (line,) = ax.plot(
            [],
            [],
            color=SPECIES_COLORS[species],
            linestyle="--",
            linewidth=1.8,
            label=SPECIES_LABELS[species],
        )
        line_by_species[species] = line
    ax.set_xlabel(r"$CO_2$ loading, mol $CO_2$/mol MEA")
    ax.set_ylabel("True-species mole fraction")
    ax.set_yscale("log")
    ax.set_xlim(0.0, min(1.0, math.ceil(float(frame_data["CO2_loading"].max()) * 20.0) / 20.0))
    ax.set_ylim(1.0e-14, 3.0e-1)
    _apply_axes_style(ax)
    ax.legend(
        title="Species",
        loc="center left",
        bbox_to_anchor=(1.01, 0.5),
        frameon=True,
    )
    title = fig.suptitle("")
    fig.subplots_adjust(right=0.78, top=0.88)

    def update(frame_index: int) -> list[object]:
        temperature_C = frame_temperatures[frame_index]
        frame = frame_data[frame_data["temperature_C"] == temperature_C]
        title.set_text(
            rf"Model-only nonideal ePC-SAFT activity speciation, $T={temperature_C:g}\ ^\circ C$"
        )
        artists: list[object] = [title]
        for species, line in line_by_species.items():
            source_rows = frame[frame["species"] == species].sort_values("CO2_loading")
            if source_rows.empty:
                raise ValueError(f"missing animation rows for {species} at {temperature_C:g} C")
            line.set_data(
                source_rows["CO2_loading"].to_numpy(dtype=float),
                source_rows["mole_fraction"].clip(lower=1.0e-30).to_numpy(dtype=float),
            )
            artists.append(line)
        return artists

    animation = FuncAnimation(fig, update, frames=len(frame_temperatures), interval=1000 / ANIMATION_FPS)
    gif_path = RESULTS_DIR / f"{ANIMATION_STEM}.gif"
    animation.save(gif_path, writer=PillowWriter(fps=ANIMATION_FPS), dpi=180)
    update(0)
    fig.savefig(RESULTS_DIR / f"{ANIMATION_STEM}_preview.png", dpi=DPI, bbox_inches="tight")
    sidecar = "\n".join(
        [
            "animation:",
            f"  title: {ANIMATION_STEM}",
            f"  gif: {ANIMATION_STEM}.gif",
            f"  preview_png: {ANIMATION_STEM}_preview.png",
            f"  plotted_data: {NONIDEAL_ANIMATION_DATA_PATH.name}",
            f"  frame_count: {len(frame_temperatures)}",
            f"  fps: {ANIMATION_FPS}",
            f"  temperature_range_C: [{frame_temperatures[0]:g}, {frame_temperatures[-1]:g}]",
            "  data_policy: model_only_actual_ce_solves_no_literature_markers",
            "  temperature_policy: sparse_direct_reactive_speciation_solves_no_temperature_interpolation",
            "style:",
            "  source: analyses/paper_validation/standalone_ce/figures/mea_reactive_speciation_oracle_comparison/scripts/render_figure.py",
            "",
        ]
    )
    (RESULTS_DIR / f"{ANIMATION_STEM}.mpl.yaml").write_text(sidecar, encoding="utf-8")
    plt.close(fig)


def _plot_error_summary(errors: pd.DataFrame, summary: pd.DataFrame) -> None:
    errors = errors.copy()
    errors["abs_error_plot"] = errors["abs_error"].clip(lower=1.0e-16)
    max_by_loading = (
        errors.groupby(["temperature_C", "CO2_loading"], sort=True)["abs_error_plot"]
        .max()
        .reset_index()
    )
    summary = summary.copy()
    summary["max_abs_error_plot"] = summary["max_abs_error"].clip(lower=1.0e-16)

    fig, axes = plt.subplots(1, 2, figsize=(11.0, 4.8))
    for temperature_C, color in ((20.0, "#245db5"), (40.0, "#d9232e")):
        subset = max_by_loading[max_by_loading["temperature_C"] == temperature_C]
        axes[0].plot(
            subset["CO2_loading"],
            subset["abs_error_plot"],
            color=color,
            linewidth=1.6,
            marker="o",
            markersize=2.0,
            markevery=16,
            label=f"{temperature_C:g} C",
        )
    axes[0].set_title("Worst species error by loading")
    axes[0].set_xlabel(r"$CO_2$ loading, mol $CO_2$/mol MEA")
    axes[0].set_ylabel("max |CE - oracle| mole fraction")
    axes[0].set_yscale("log")
    axes[0].set_xlim(0.0, 0.8)
    axes[0].set_ylim(1.0e-16, max(1.0e-6, float(max_by_loading["abs_error_plot"].max()) * 10.0))
    axes[0].legend(frameon=True)
    _apply_axes_style(axes[0])

    species_order = [species for species in PLOT_SPECIES if species != "MEA + MEAH+"] + ["H2O"]
    x_positions = range(len(species_order))
    width = 0.38
    for offset, (temperature_C, color) in zip((-width / 2.0, width / 2.0), ((20.0, "#245db5"), (40.0, "#d9232e"))):
        values = []
        for species in species_order:
            row = summary[(summary["temperature_C"] == temperature_C) & (summary["species"] == species)]
            values.append(float(row["max_abs_error_plot"].iloc[0]) if not row.empty else math.nan)
        axes[1].bar([x + offset for x in x_positions], values, width=width, color=color, label=f"{temperature_C:g} C")
    axes[1].set_title("Worst error by species")
    axes[1].set_xticks(list(x_positions))
    axes[1].set_xticklabels([SPECIES_LABELS[species] for species in species_order], rotation=45, ha="right")
    axes[1].set_ylabel("max |CE - oracle| mole fraction")
    axes[1].set_yscale("log")
    axes[1].set_ylim(1.0e-16, max(1.0e-6, float(summary["max_abs_error_plot"].max()) * 10.0))
    axes[1].legend(frameon=True)
    _apply_axes_style(axes[1])

    fig.suptitle("Unassisted CE reactive speciation oracle-match errors")
    fig.tight_layout()
    _save_bundle(fig, "mea_ce_oracle_speciation_error_summary")
    plt.close(fig)


def _plot_continuation_stage_diagnostics(trace: pd.DataFrame) -> None:
    trace = trace.copy()
    trace["corrector_flag"] = trace["physical_proof_corrector_accepted"].astype(bool)

    fig, axes = plt.subplots(1, 2, figsize=(11.0, 4.8))
    for temperature_C, color in ((20.0, "#245db5"), (40.0, "#d9232e")):
        subset = trace[trace["temperature_C"] == temperature_C].sort_values("CO2_loading")
        axes[0].plot(
            subset["CO2_loading"],
            subset["stage_count"],
            color=color,
            linewidth=1.5,
            marker="o",
            markersize=2.0,
            markevery=16,
            label=f"{temperature_C:g} C",
        )
    axes[0].set_title("Internal continuation stages")
    axes[0].set_xlabel(r"$CO_2$ loading, mol $CO_2$/mol MEA")
    axes[0].set_ylabel("retained stage count")
    axes[0].set_xlim(0.0, 0.8)
    axes[0].set_ylim(0.8, max(3.2, float(trace["stage_count"].max()) + 0.4))
    axes[0].legend(frameon=True)
    _apply_axes_style(axes[0])

    grouped = (
        trace.groupby(["temperature_C", "physical_proof_corrector_status"], sort=True)
        .size()
        .reset_index(name="count")
    )
    statuses = list(grouped["physical_proof_corrector_status"].drop_duplicates())
    x_positions = range(len(statuses))
    width = 0.38
    for offset, (temperature_C, color) in zip((-width / 2.0, width / 2.0), ((20.0, "#245db5"), (40.0, "#d9232e"))):
        values = []
        for status in statuses:
            row = grouped[(grouped["temperature_C"] == temperature_C) & (grouped["physical_proof_corrector_status"] == status)]
            values.append(int(row["count"].iloc[0]) if not row.empty else 0)
        axes[1].bar([x + offset for x in x_positions], values, width=width, color=color, label=f"{temperature_C:g} C")
    axes[1].set_title("Physical proof corrector outcomes")
    axes[1].set_xticks(list(x_positions))
    axes[1].set_xticklabels(statuses, rotation=35, ha="right")
    axes[1].set_ylabel("loading points")
    axes[1].legend(frameon=True)
    _apply_axes_style(axes[1])

    fig.suptitle("CE-owned continuation and strict physical proof diagnostics")
    fig.tight_layout()
    _save_bundle(fig, "mea_ce_continuation_stage_diagnostics")
    plt.close(fig)


def _nonideal_temperatures(plot_data: pd.DataFrame) -> list[float]:
    activity_temperatures = set(
        float(value)
        for value in plot_data.loc[
            plot_data["role"] == "eos_x_gamma_activity",
            "temperature_C",
        ].dropna().unique()
    )
    data_temperatures = set(
        float(value)
        for value in plot_data.loc[
            plot_data["role"] == "real_speciation_data",
            "temperature_C",
        ].dropna().unique()
    )
    return sorted(activity_temperatures & data_temperatures)


def render() -> None:
    plot_data = _require_csv(PLOT_DATA_PATH)
    errors = _require_csv(ERRORS_PATH)
    summary = _require_csv(SUMMARY_PATH)
    trace = _require_csv(TRACE_SUMMARY_PATH)
    nonideal_plot_data = _require_csv(NONIDEAL_PLOT_DATA_PATH)
    for temperature_C in (20.0, 40.0):
        _plot_temperature_overlay(
            plot_data,
            temperature_C,
            title=f"Unassisted CE reactive speciation vs Smith-Missen oracle, {temperature_C:g} C",
            ce_label="CE route (no source seed)",
            stem=f"mea_ce_oracle_speciation_{int(temperature_C)}C",
        )
        _plot_temperature_overlay(
            plot_data,
            temperature_C,
            title=f"CE-owned continuation proof trace vs Smith-Missen oracle, {temperature_C:g} C",
            ce_label="CE route (internal continuation proof)",
            stem=f"mea_ce_owned_continuation_speciation_{int(temperature_C)}C",
        )
    for temperature_C in _nonideal_temperatures(nonideal_plot_data):
        for group_key in NONIDEAL_SPECIES_GROUPS:
            _plot_nonideal_temperature_group(nonideal_plot_data, temperature_C, group_key=group_key)
    _plot_nonideal_temperature_sweep_animation()
    _plot_error_summary(errors, summary)
    _plot_continuation_stage_diagnostics(trace)


def main() -> int:
    render()
    print(f"Rendered MEA CE oracle comparison figures: {RESULTS_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
