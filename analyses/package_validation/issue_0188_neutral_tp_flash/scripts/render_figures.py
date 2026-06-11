from __future__ import annotations

import csv
import json
import math
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

ANALYSIS_ROOT = Path(__file__).resolve().parents[1]
SHARED_RESULTS = ANALYSIS_ROOT / "shared" / "results"
FIGURES_ROOT = ANALYSIS_ROOT / "figures"


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _as_float(row: dict[str, str], key: str) -> float:
    return float(row[key])


def _ternary_xy(row: dict[str, str]) -> tuple[float, float]:
    methane = _as_float(row, "Methane")
    ethane = _as_float(row, "Ethane")
    propane = _as_float(row, "Propane")
    total = methane + ethane + propane
    if total <= 0.0:
        raise ValueError("composition must have positive total")
    methane /= total
    ethane /= total
    propane /= total
    x = propane + 0.5 * ethane
    y = (math.sqrt(3.0) / 2.0) * ethane
    return x, y


def _write_sidecar(path: Path, *, plot_id: str, title: str, png_name: str, svg_name: str, csv_files: list[str]) -> None:
    csv_block = "\n".join(f"    - {name}" for name in csv_files)
    path.write_text(
        f"""kind: matplotlib-figure
version: 1
plot_id: {plot_id}
title: {title}
files:
  figures:
    - {png_name}
    - {svg_name}
  data:
{csv_block}
matplotlib:
  title: {title}
  style: scientific-validation
""",
        encoding="utf-8",
    )


def _save(fig: plt.Figure, output_dir: Path, stem: str, *, plot_id: str, title: str, csv_files: list[str]) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    png_name = f"{stem}.png"
    svg_name = f"{stem}.svg"
    fig.savefig(output_dir / png_name, dpi=180, bbox_inches="tight")
    fig.savefig(output_dir / svg_name, bbox_inches="tight")
    _write_sidecar(
        output_dir / f"{stem}.mpl.yaml",
        plot_id=plot_id,
        title=title,
        png_name=png_name,
        svg_name=svg_name,
        csv_files=csv_files,
    )
    plt.close(fig)


def render_tieline() -> None:
    rows = _read_csv(SHARED_RESULTS / "neutral_tp_flash_phase_points.csv")
    by_role = {row["role"]: row for row in rows}
    fig, ax = plt.subplots(figsize=(7.2, 6.2))

    triangle = [(0.0, 0.0), (1.0, 0.0), (0.5, math.sqrt(3.0) / 2.0), (0.0, 0.0)]
    ax.plot([p[0] for p in triangle], [p[1] for p in triangle], color="black", linewidth=1.6)
    for fraction in (0.2, 0.4, 0.6, 0.8):
        ax.plot([fraction, 0.5 + 0.5 * fraction], [0.0, (math.sqrt(3.0) / 2.0) * (1.0 - fraction)], color="#d4d4d4", linewidth=0.8)
        ax.plot([1.0 - fraction, 0.5 * (1.0 - fraction)], [0.0, (math.sqrt(3.0) / 2.0) * fraction], color="#d4d4d4", linewidth=0.8)
        ax.plot([0.5 * fraction, 1.0 - 0.5 * fraction], [(math.sqrt(3.0) / 2.0) * fraction] * 2, color="#d4d4d4", linewidth=0.8)

    source_liq = _ternary_xy(by_role["source_liquid"])
    source_vap = _ternary_xy(by_role["source_vapor"])
    solved_liq = _ternary_xy(by_role["solved_liquid"])
    solved_vap = _ternary_xy(by_role["solved_vapor"])
    feed = _ternary_xy(by_role["feed"])

    ax.plot([source_liq[0], source_vap[0]], [source_liq[1], source_vap[1]], color="#737373", linestyle="--", linewidth=2.0)
    ax.plot([solved_liq[0], solved_vap[0]], [solved_liq[1], solved_vap[1]], color="#0f766e", linewidth=2.4)
    ax.scatter(*source_liq, s=92, marker="o", facecolor="white", edgecolor="#525252", linewidth=1.8, zorder=3)
    ax.scatter(*source_vap, s=92, marker="s", facecolor="white", edgecolor="#525252", linewidth=1.8, zorder=3)
    ax.scatter(*solved_liq, s=56, marker="o", color="#0f766e", zorder=4)
    ax.scatter(*solved_vap, s=56, marker="s", color="#0f766e", zorder=4)
    ax.scatter(*feed, s=88, marker="D", color="#b45309", zorder=5)

    ax.text(-0.055, -0.055, "Methane", ha="center", va="top", fontsize=12)
    ax.text(1.055, -0.055, "Propane", ha="center", va="top", fontsize=12)
    ax.text(0.5, math.sqrt(3.0) / 2.0 + 0.025, "Ethane", ha="center", va="bottom", fontsize=12)
    ax.set_title("Neutral TP-flash VLE tie-line", fontsize=14, pad=22)
    ax.text(
        0.5,
        -0.12,
        "T = 233.15 K, P = 1.276369 MPa; feed is an equal-phase blend of workbook liquid and vapor states",
        ha="center",
        va="top",
        fontsize=9,
    )
    handles = [
        Line2D([0], [0], color="#737373", linestyle="--", linewidth=2, label="workbook source tie-line"),
        Line2D([0], [0], color="#0f766e", linewidth=2.4, label="current main solved tie-line"),
        Line2D([0], [0], marker="D", color="none", markerfacecolor="#b45309", markeredgecolor="#b45309", linestyle="None", label="constructed feed"),
    ]
    ax.legend(handles=handles, loc="upper right", frameon=False)
    ax.set_aspect("equal")
    ax.set_xlim(-0.12, 1.12)
    ax.set_ylim(-0.16, math.sqrt(3.0) / 2.0 + 0.16)
    ax.axis("off")
    _save(
        fig,
        FIGURES_ROOT / "neutral_tp_flash_vle_tieline" / "results",
        "neutral_tp_flash_vle_tieline",
        plot_id="issue_0188_neutral_tp_flash_vle_tieline",
        title="Issue 188 neutral TP-flash VLE tie-line",
        csv_files=["../../../shared/results/neutral_tp_flash_phase_points.csv"],
    )


def render_tolerance_margins() -> None:
    rows = _read_csv(SHARED_RESULTS / "neutral_tp_flash_tolerance_summary.csv")
    metrics = [row["metric"] for row in rows]
    ratios = [float(row["observed_to_tolerance"]) for row in rows]
    colors = ["#15803d" if row["accepted"] == "True" else "#b91c1c" for row in rows]
    fig, ax = plt.subplots(figsize=(8.2, 4.8))
    ax.bar(range(len(metrics)), ratios, color=colors, width=0.64)
    ax.axhline(1.0, color="black", linewidth=1.2, linestyle="--", label="acceptance limit")
    ax.set_yscale("log")
    ax.set_ylabel("observed / tolerance")
    ax.set_title("Neutral TP-flash route diagnostics vs issue 188 tolerances", fontsize=13)
    ax.set_xticks(range(len(metrics)))
    ax.set_xticklabels(metrics, rotation=25, ha="right")
    ax.grid(axis="y", which="both", alpha=0.25)
    for index, row in enumerate(rows):
        ax.text(
            index,
            max(float(row["observed_to_tolerance"]) * 1.2, 1.0e-8),
            f"{float(row['observed_abs']):.2e}",
            ha="center",
            va="bottom",
            fontsize=8,
        )
    ax.legend(frameon=False)
    fig.tight_layout()
    _save(
        fig,
        FIGURES_ROOT / "neutral_tp_flash_tolerance_margins" / "results",
        "neutral_tp_flash_tolerance_margins",
        plot_id="issue_0188_neutral_tp_flash_tolerance_margins",
        title="Issue 188 neutral TP-flash tolerance margins",
        csv_files=[
            "../../../shared/results/neutral_tp_flash_tolerance_summary.csv",
            "../../../shared/results/neutral_tp_flash_component_errors.csv",
        ],
    )


def render_held_gate_status() -> None:
    rows = _read_csv(SHARED_RESULTS / "held_1_0_gate_status.csv")
    rows.sort(key=lambda row: int(row["order"]))
    colors = {
        "verified": "#15803d",
        "incomplete": "#b91c1c",
        "not_requested": "#a16207",
    }
    labels = [row["label"] for row in rows]
    status_classes = [row["status_class"] for row in rows]
    fig, ax = plt.subplots(figsize=(8.5, 4.8))
    y_positions = list(range(len(rows)))
    ax.barh(y_positions, [1] * len(rows), color=[colors[item] for item in status_classes], height=0.6)
    ax.set_yticks(y_positions)
    ax.set_yticklabels(labels)
    ax.invert_yaxis()
    ax.set_xlim(0, 1)
    ax.set_xticks([])
    ax.set_title("HELD 1.0 gate status from current main rerun", fontsize=13)
    for y, row in zip(y_positions, rows, strict=True):
        ax.text(0.02, y, row["status"], va="center", ha="left", color="white", fontsize=9)
    ax.text(
        0.0,
        len(rows) + 0.08,
        "Stage II and III are shown as incomplete here; this figure intentionally avoids a full-adoption claim.",
        ha="left",
        va="bottom",
        fontsize=9,
        transform=ax.transData,
    )
    for spine in ax.spines.values():
        spine.set_visible(False)
    fig.tight_layout()
    _save(
        fig,
        FIGURES_ROOT / "held_1_0_gate_status" / "results",
        "held_1_0_gate_status",
        plot_id="issue_0188_held_1_0_gate_status",
        title="Issue 188 HELD 1.0 gate status",
        csv_files=["../../../shared/results/held_1_0_gate_status.csv"],
    )


def main() -> int:
    summary = json.loads((SHARED_RESULTS / "run_summary.json").read_text(encoding="utf-8"))
    if summary["neutral_tp_flash"]["route_status"] != "production_accepted":
        raise RuntimeError("neutral TP flash route was not production accepted")
    render_tieline()
    render_tolerance_margins()
    render_held_gate_status()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
