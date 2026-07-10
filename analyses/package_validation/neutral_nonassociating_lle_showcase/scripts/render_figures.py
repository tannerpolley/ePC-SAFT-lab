from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

ANALYSIS_ROOT = Path(__file__).resolve().parents[1]
SHARED_RESULTS = ANALYSIS_ROOT / "shared" / "results"
FIGURES_ROOT = ANALYSIS_ROOT / "figures"

plt.rcParams["svg.hashsalt"] = "neutral_nonassociating_lle_showcase"
plt.rcParams["font.family"] = "serif"


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _as_float(row: dict[str, str], key: str) -> float:
    return float(row[key])


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


def _snapshot(output_dir: Path, source_name: str, target_name: str) -> str:
    rows = _read_csv(SHARED_RESULTS / source_name)
    _write_csv(output_dir / target_name, list(rows[0]) if rows else [], rows)
    return target_name


def render_binodal_showcase() -> None:
    output_dir = FIGURES_ROOT / "neutral_lle_binodal_showcase" / "results"
    phase_points_name = _snapshot(output_dir, "neutral_lle_phase_points.csv", "neutral_lle_phase_points_plotted.csv")
    binodal_name = _snapshot(output_dir, "neutral_lle_source_binodal_points.csv", "neutral_lle_source_binodal_points_plotted.csv")
    phase_rows = _read_csv(output_dir / phase_points_name)
    binodal_rows = _read_csv(output_dir / binodal_name)
    by_role = {row["role"]: row for row in phase_rows}

    fig, ax = plt.subplots(figsize=(7.2, 5.0))
    ax.plot(
        [_as_float(row, "x_perfluorohexane") for row in binodal_rows],
        [_as_float(row, "temperature_K") for row in binodal_rows],
        color="#525252",
        linewidth=1.4,
        alpha=0.72,
    )
    ax.scatter(
        [_as_float(row, "x_perfluorohexane") for row in binodal_rows],
        [_as_float(row, "temperature_K") for row in binodal_rows],
        s=34,
        marker="o",
        facecolor="white",
        edgecolor="#525252",
        linewidth=1.1,
        label="NIST cloud-point rows",
    )

    source_roles = ["source_liquid1", "source_liquid2"]
    sampled_roles = ["sampled_liquid1", "sampled_liquid2"]
    source_x = [_as_float(by_role[role], "x_perfluorohexane") for role in source_roles]
    source_t = [_as_float(by_role[role], "temperature_K") for role in source_roles]
    sampled_x = [_as_float(by_role[role], "x_perfluorohexane") for role in sampled_roles]
    sampled_t = [_as_float(by_role[role], "temperature_K") for role in sampled_roles]
    feed = by_role["feed"]
    ax.plot(source_x, source_t, color="#2563eb", linestyle="--", linewidth=2.0)
    ax.plot(sampled_x, sampled_t, color="#0f766e", linewidth=2.2)
    ax.scatter(source_x, source_t, s=88, marker="s", facecolor="white", edgecolor="#2563eb", linewidth=1.8)
    ax.scatter(sampled_x, sampled_t, s=62, marker="o", color="#0f766e")
    ax.scatter(
        [_as_float(feed, "x_perfluorohexane")],
        [_as_float(feed, "temperature_K")],
        s=82,
        marker="D",
        color="#b45309",
    )

    ax.set_title("Neutral LLE sampled-candidate comparison")
    ax.set_xlabel(r"$x_{\mathrm{perfluorohexane}}$ in liquid phase")
    ax.set_ylabel("Temperature / K")
    ax.grid(True, which="major", alpha=0.25)
    ax.set_xlim(0.12, 0.73)
    ax.set_ylim(284.0, 297.2)
    ax.legend(
        handles=[
            Line2D([0], [0], marker="o", color="#525252", markerfacecolor="white", linestyle="-", label="NIST cloud-point rows"),
            Line2D([0], [0], marker="s", color="#2563eb", markerfacecolor="white", linestyle="--", label="paired source branches"),
            Line2D([0], [0], marker="o", color="#0f766e", linestyle="-", label="sampled TPD candidates"),
            Line2D([0], [0], marker="D", color="#b45309", linestyle="None", label="constructed feed"),
        ],
        frameon=False,
        loc="lower left",
    )
    fig.tight_layout()
    _save(
        fig,
        output_dir,
        "neutral_lle_binodal_showcase",
    )


def render_tolerance_margins() -> None:
    output_dir = FIGURES_ROOT / "neutral_lle_tolerance_margins" / "results"
    tolerance_name = _snapshot(output_dir, "neutral_lle_tolerance_summary.csv", "neutral_lle_tolerance_summary_plotted.csv")
    component_name = _snapshot(output_dir, "neutral_lle_component_errors.csv", "neutral_lle_component_errors_plotted.csv")
    rows = _read_csv(output_dir / tolerance_name)
    metrics = [row["metric"] for row in rows]
    ratios = [max(float(row["margin_ratio"]), 1.0e-8) for row in rows]
    colors = ["#15803d" if row["accepted"] == "True" else "#b91c1c" for row in rows]

    fig, ax = plt.subplots(figsize=(8.0, 4.8))
    ax.bar(range(len(metrics)), ratios, color=colors, width=0.64)
    ax.axhline(1.0, color="black", linewidth=1.1, linestyle="--", label="reference threshold")
    ax.set_yscale("log")
    ax.set_ylabel("margin ratio")
    ax.set_title("Internal sampled-candidate diagnostics vs reference thresholds")
    ax.set_xticks(range(len(metrics)))
    ax.set_xticklabels(metrics, rotation=24, ha="right")
    ax.grid(axis="y", which="major", alpha=0.25)
    for index, row in enumerate(rows):
        ax.text(
            index,
            max(float(row["margin_ratio"]) * 1.15, 1.4e-8),
            f"{float(row['observed_abs']):.2e}",
            ha="center",
            va="bottom",
            fontsize=8,
        )
    ax.legend(frameon=False)
    ax.set_ylim(1.0e-8, 2.0)
    fig.tight_layout()
    _save(
        fig,
        output_dir,
        "neutral_lle_tolerance_margins",
    )


def render_held_stage_status() -> None:
    output_dir = FIGURES_ROOT / "neutral_lle_held_stage_status" / "results"
    stage_name = _snapshot(output_dir, "held_stage_status.csv", "held_stage_status_plotted.csv")
    rows = sorted(_read_csv(output_dir / stage_name), key=lambda row: int(row["order"]))
    fig, ax = plt.subplots(figsize=(8.0, 4.4))
    y_positions = list(range(len(rows)))
    colors = ["#15803d" if row["accepted"] == "True" else "#b91c1c" for row in rows]
    ax.barh(y_positions, [1] * len(rows), color=colors, height=0.62)
    ax.set_yticks(y_positions)
    ax.set_yticklabels([row["label"] for row in rows])
    ax.invert_yaxis()
    ax.set_xlim(0.0, 1.0)
    ax.set_xticks([])
    ax.set_title("Internal neutral LLE sampled-candidate diagnostics")
    for y, row in zip(y_positions, rows, strict=True):
        ax.text(0.02, y, row["status"], va="center", ha="left", color="white", fontsize=9)
    for spine in ax.spines.values():
        spine.set_visible(False)
    fig.tight_layout()
    _save(
        fig,
        output_dir,
        "neutral_lle_held_stage_status",
    )


def main() -> int:
    summary = json.loads((SHARED_RESULTS / "run_summary.json").read_text(encoding="utf-8"))
    if (
        summary["diagnostic_status"] != "internal_diagnostic_complete"
        or summary["production_route_admitted"] is not False
        or summary["global_phase_set_certified"] is not False
        or not summary["complete"]
    ):
        raise RuntimeError("neutral LLE internal diagnostic retained data are not complete")
    render_binodal_showcase()
    render_tolerance_margins()
    render_held_stage_status()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
