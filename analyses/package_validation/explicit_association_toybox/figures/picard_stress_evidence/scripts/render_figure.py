from __future__ import annotations

import csv
import math
import statistics
import sys
from collections.abc import Mapping, Sequence
from pathlib import Path

import matplotlib.pyplot as plt

ANALYSIS_ROOT = Path(__file__).resolve().parents[3]
REPO_ROOT = ANALYSIS_ROOT.parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from analyses.package_validation.explicit_association_toybox.scripts.plot_style import (
    BLUE,
    GREEN,
    ORANGE,
    PURPLE,
    RED,
    apply_plot_style,
    save_png_svg,
    style_axis,
    write_sidecar,
)

OUTPUT = ANALYSIS_ROOT / "figures" / "picard_stress_evidence" / "output"
SOURCE = OUTPUT / "picard_stress_evidence.csv"
PLOTTED = OUTPUT / "picard_stress_evidence_plotted_data.csv"
FIGURE = OUTPUT / "picard_stress_evidence.png"
SIDECAR = OUTPUT / "picard_stress_evidence.mpl.yaml"
LAMBDA_COLORS = {
    0.35: BLUE,
    0.5: ORANGE,
    0.65: GREEN,
    0.8: PURPLE,
    1.0: RED,
}
MODEL_DOTTED = (0, (1.2, 1.8))
METRICS = (
    ("association_helmholtz_relative_error", "max", r"$a^{\mathrm{assoc}}$ relative error"),
    ("pressure_proxy_relative_error", "max", r"$P_{\mathrm{proxy}}$ relative error"),
    ("hessian_max_relative_error", "max", "max Hessian relative error"),
    ("simulation_speedup_vs_exact", "median", "median simulation speedup"),
)


def main() -> None:
    apply_plot_style()
    rows = _read_rows(SOURCE)
    plotted = build_plotted_rows(rows)
    _write_plotted_rows(plotted)
    _render(plotted)
    write_sidecar(
        SIDECAR,
        plot_id="picard_stress_evidence",
        title="Picard stress evidence",
        figure=FIGURE,
        source_data=PLOTTED,
        x_label="fixed Picard step count",
        y_label="relative error or speedup",
        y_scale="log for error panels",
        command=(
            "uv run python analyses/package_validation/explicit_association_toybox/figures/"
            "picard_stress_evidence/scripts/render_figure.py"
        ),
    )
    print(FIGURE)


def build_plotted_rows(rows: Sequence[Mapping[str, str]]) -> list[dict[str, object]]:
    picard_rows = [row for row in rows if row["row_kind"] == "picard_policy"]
    if not picard_rows:
        raise ValueError("Picard stress plotting requires retained policy rows.")
    plotted: list[dict[str, object]] = []
    for metric, aggregate, label in METRICS:
        for step_count, damping in _policy_points(picard_rows):
            group = [
                row
                for row in picard_rows
                if int(row["step_count"]) == step_count and math.isclose(float(row["damping"]), damping)
            ]
            value = _aggregate(group, metric, aggregate)
            plotted.append(
                {
                    "metric": metric,
                    "metric_label": label,
                    "aggregate": aggregate,
                    "step_count": step_count,
                    "damping": damping,
                    "value": value,
                    "stress_decision": group[0]["stress_decision"],
                    "case_count": len({row["case_id"] for row in group}),
                    "max_case_family": _worst_family(group, metric),
                }
            )
    return plotted


def _read_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise FileNotFoundError("picard_stress_evidence.csv is required before rendering; run generate_data.py first.")
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _write_plotted_rows(rows: Sequence[Mapping[str, object]]) -> None:
    PLOTTED.parent.mkdir(parents=True, exist_ok=True)
    with PLOTTED.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def _render(rows: Sequence[Mapping[str, object]]) -> None:
    fig, axes = plt.subplots(2, 2, figsize=(10.8, 7.2), constrained_layout=True)
    for axis, (metric, _, label) in zip(axes.ravel(), METRICS, strict=True):
        metric_rows = [row for row in rows if row["metric"] == metric]
        for damping in sorted({float(row["damping"]) for row in metric_rows}):
            damping_rows = sorted(
                [row for row in metric_rows if math.isclose(float(row["damping"]), damping)],
                key=lambda row: int(row["step_count"]),
            )
            axis.plot(
                [int(row["step_count"]) for row in damping_rows],
                [max(float(row["value"]), 1.0e-14) for row in damping_rows],
                marker="o",
                linestyle=MODEL_DOTTED,
                linewidth=1.6,
                markersize=4.0,
                color=LAMBDA_COLORS[damping],
                label=fr"$\lambda={damping:g}$",
            )
        if metric != "simulation_speedup_vs_exact":
            axis.set_yscale("log")
            axis.set_ylabel("relative error")
        else:
            axis.axhline(1.0, color="#6b7280", linestyle=":", linewidth=1.0)
            axis.set_ylabel("speedup")
        axis.set_title(label, loc="left")
        axis.set_xticks([3, 5, 7, 9, 11])
        axis.set_xlabel("Picard steps")
        style_axis(axis, minor=metric != "simulation_speedup_vs_exact")
    axes[0, 0].legend(frameon=False, loc="best", ncol=2)
    fig.suptitle("Picard policy grid under stress-case exact implicit baselines")
    svg = save_png_svg(fig, FIGURE)
    _strip_trailing_svg_whitespace(svg)
    plt.close(fig)


def _policy_points(rows: Sequence[Mapping[str, str]]) -> tuple[tuple[int, float], ...]:
    return tuple(sorted({(int(row["step_count"]), float(row["damping"])) for row in rows}))


def _aggregate(rows: Sequence[Mapping[str, str]], metric: str, aggregate: str) -> float:
    values = [float(row[metric]) for row in rows if math.isfinite(float(row[metric]))]
    if not values:
        return float("nan")
    if aggregate == "max":
        return max(values)
    if aggregate == "median":
        return statistics.median(values)
    raise ValueError(f"unknown aggregate: {aggregate}")


def _worst_family(rows: Sequence[Mapping[str, str]], metric: str) -> str:
    finite_rows = [row for row in rows if math.isfinite(float(row[metric]))]
    if not finite_rows:
        return ""
    return str(max(finite_rows, key=lambda row: float(row[metric]))["case_family"])


def _strip_trailing_svg_whitespace(path: Path) -> None:
    lines = path.read_text(encoding="utf-8").splitlines()
    path.write_text("\n".join(line.rstrip() for line in lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
