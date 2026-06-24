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
plt.rcParams["svg.hashsalt"] = "issue_0188_neutral_tp_flash"
HELD_GATE_NATIVE_RECEIPT_FIELDS = (
    "native_git_commit",
    "native_module_path",
    "native_build_refresh_command",
    "native_checker_command",
)
HELD_GATE_RECEIPT_REQUIRED_GATES = {
    "held_stage_ii_dual_phase_discovery",
    "held_stage_iii_ipopt_refinement",
}


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


def _strip_trailing_whitespace(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    path.write_text("\n".join(line.rstrip() for line in text.splitlines()) + "\n", encoding="utf-8")


def _save(fig: plt.Figure, output_dir: Path, stem: str) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    png_path = output_dir / f"{stem}.png"
    svg_path = output_dir / f"{stem}.svg"
    pdf_path = output_dir / f"{stem}.pdf"
    fig.savefig(png_path, dpi=180, bbox_inches="tight")
    fig.savefig(svg_path, bbox_inches="tight", metadata={"Date": None})
    fig.savefig(pdf_path, bbox_inches="tight")
    _strip_trailing_whitespace(svg_path)
    plt.close(fig)


def _require_verified_held_gate_receipts(rows: list[dict[str, str]]) -> None:
    for row in rows:
        if row.get("gate") not in HELD_GATE_RECEIPT_REQUIRED_GATES:
            continue
        if row.get("status_class") != "verified" and row.get("accepted") != "True":
            continue
        missing = [
            field
            for field in HELD_GATE_NATIVE_RECEIPT_FIELDS
            if not row.get(field, "").strip()
        ]
        if missing:
            raise ValueError(
                f"native freshness receipt missing for verified {row.get('gate', 'HELD gate')}: "
                + ", ".join(missing)
            )


def render_tieline() -> None:
    rows = _read_csv(SHARED_RESULTS / "neutral_tp_flash_phase_points.csv")
    by_role = {row["role"]: row for row in rows}
    fig, ax = plt.subplots(figsize=(7.0, 5.8))

    triangle = [(0.0, 0.0), (1.0, 0.0), (0.5, math.sqrt(3.0) / 2.0), (0.0, 0.0)]
    ax.plot([p[0] for p in triangle], [p[1] for p in triangle], color="black", linewidth=1.8)
    grid_color = "#e5e7eb"
    grid_width = 0.75
    for fraction in (0.25, 0.5, 0.75):
        # Constant propane.
        ax.plot(
            [fraction, 0.5 + 0.5 * fraction],
            [0.0, (math.sqrt(3.0) / 2.0) * (1.0 - fraction)],
            color=grid_color,
            linewidth=grid_width,
            zorder=0,
        )
        # Constant methane.
        ax.plot(
            [1.0 - fraction, 0.5 * (1.0 - fraction)],
            [0.0, (math.sqrt(3.0) / 2.0) * (1.0 - fraction)],
            color=grid_color,
            linewidth=grid_width,
            zorder=0,
        )
        # Constant ethane.
        ax.plot(
            [0.5 * fraction, 1.0 - 0.5 * fraction],
            [(math.sqrt(3.0) / 2.0) * fraction] * 2,
            color=grid_color,
            linewidth=grid_width,
            zorder=0,
        )

    source_liq = _ternary_xy(by_role["source_liquid"])
    source_vap = _ternary_xy(by_role["source_vapor"])
    solved_liq = _ternary_xy(by_role["solved_liquid"])
    solved_vap = _ternary_xy(by_role["solved_vapor"])
    feed = _ternary_xy(by_role["feed"])

    ax.plot(
        [source_vap[0], source_liq[0]],
        [source_vap[1], source_liq[1]],
        color="#6b7280",
        linestyle=(0, (4, 3)),
        linewidth=1.7,
        zorder=1,
    )
    ax.plot(
        [solved_vap[0], solved_liq[0]],
        [solved_vap[1], solved_liq[1]],
        color="#0f766e",
        linewidth=2.8,
        zorder=2,
    )
    ax.scatter(*source_liq, s=130, marker="o", facecolor="white", edgecolor="#6b7280", linewidth=1.8, zorder=3)
    ax.scatter(*source_vap, s=130, marker="s", facecolor="white", edgecolor="#6b7280", linewidth=1.8, zorder=3)
    ax.scatter(*solved_liq, s=72, marker="o", color="#0f766e", edgecolor="#0f4f47", linewidth=0.8, zorder=4)
    ax.scatter(*solved_vap, s=72, marker="s", color="#0f766e", edgecolor="#0f4f47", linewidth=0.8, zorder=4)
    ax.scatter(*feed, s=96, marker="D", color="#b45309", edgecolor="#7c2d12", linewidth=0.8, zorder=5)

    ax.annotate("vapor", xy=solved_vap, xytext=(-12, 11), textcoords="offset points", ha="right", fontsize=10, color="#0f4f47")
    ax.annotate("liquid", xy=solved_liq, xytext=(12, 10), textcoords="offset points", ha="left", fontsize=10, color="#0f4f47")
    ax.annotate("feed", xy=feed, xytext=(0, -18), textcoords="offset points", ha="center", fontsize=10, color="#7c2d12")

    ax.text(-0.04, -0.05, "Methane", ha="center", va="top", fontsize=12)
    ax.text(1.04, -0.05, "Propane", ha="center", va="top", fontsize=12)
    ax.text(0.5, math.sqrt(3.0) / 2.0 + 0.025, "Ethane", ha="center", va="bottom", fontsize=12)
    ax.set_title("Neutral TP flash: ternary composition closure", fontsize=14, pad=18)
    ax.text(
        0.5,
        -0.10,
        "T = 233.15 K, P = 1.276 MPa",
        ha="center",
        va="top",
        fontsize=10,
    )
    handles = [
        Line2D([0], [0], color="#6b7280", linestyle=(0, (4, 3)), linewidth=1.7, label="reference tie-line"),
        Line2D([0], [0], color="#0f766e", linewidth=2.8, label="solved tie-line"),
        Line2D([0], [0], marker="D", color="none", markerfacecolor="#b45309", markeredgecolor="#7c2d12", linestyle="None", label="feed"),
    ]
    ax.legend(handles=handles, loc="upper right", frameon=False, fontsize=10)
    ax.set_aspect("equal")
    ax.set_xlim(-0.09, 1.09)
    ax.set_ylim(-0.13, math.sqrt(3.0) / 2.0 + 0.13)
    ax.axis("off")
    _save(
        fig,
        FIGURES_ROOT / "neutral_tp_flash_vle_tieline" / "results",
        "neutral_tp_flash_vle_tieline",
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
    )


def render_held_gate_status() -> None:
    rows = _read_csv(SHARED_RESULTS / "held_1_0_gate_status.csv")
    rows.sort(key=lambda row: int(row["order"]))
    _require_verified_held_gate_receipts(rows)
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
    if any(row["status_class"] == "incomplete" for row in rows):
        footer = "Incomplete rows block a full HELD 1.0 admission claim for this rerun."
    else:
        footer = "Stage II and III are verified with a retained native freshness receipt."
    ax.text(0.0, len(rows) + 0.08, footer, ha="left", va="bottom", fontsize=9, transform=ax.transData)
    for spine in ax.spines.values():
        spine.set_visible(False)
    fig.tight_layout()
    _save(
        fig,
        FIGURES_ROOT / "held_1_0_gate_status" / "results",
        "held_1_0_gate_status",
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
