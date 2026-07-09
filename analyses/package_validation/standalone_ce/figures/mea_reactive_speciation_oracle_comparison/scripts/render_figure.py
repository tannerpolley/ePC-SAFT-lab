from __future__ import annotations

import math
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.lines import Line2D

FIGURE_DIR = Path(__file__).resolve().parents[1]
RESULTS_DIR = FIGURE_DIR / "results"
PLOT_DATA_PATH = RESULTS_DIR / "mea_ce_oracle_speciation_plot_data.csv"
ERRORS_PATH = RESULTS_DIR / "mea_ce_oracle_speciation_errors.csv"
SUMMARY_PATH = RESULTS_DIR / "mea_ce_oracle_speciation_error_summary.csv"
TRACE_SUMMARY_PATH = RESULTS_DIR / "mea_ce_continuation_trace_summary.csv"
DPI = 300
FIGURE_CREATOR = "ePC-SAFT standalone CE validation"

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
            "  source: analyses/package_validation/standalone_ce/figures/mea_reactive_speciation_oracle_comparison/scripts/render_figure.py",
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


def render() -> None:
    plot_data = _require_csv(PLOT_DATA_PATH)
    errors = _require_csv(ERRORS_PATH)
    summary = _require_csv(SUMMARY_PATH)
    trace = _require_csv(TRACE_SUMMARY_PATH)
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
    _plot_error_summary(errors, summary)
    _plot_continuation_stage_diagnostics(trace)


def main() -> int:
    render()
    print(f"Rendered MEA CE oracle comparison figures: {RESULTS_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
