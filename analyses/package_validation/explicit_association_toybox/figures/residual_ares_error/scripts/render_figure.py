from __future__ import annotations

import csv
from pathlib import Path

import matplotlib.pyplot as plt

ANALYSIS_ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ANALYSIS_ROOT / "figures" / "residual_ares_error" / "output"
METRICS = OUTPUT / "residual_ares_metrics.csv"
FIGURE = OUTPUT / "residual_ares_error_summary.png"
PLOTTED = OUTPUT / "residual_ares_error_summary_plotted_data.csv"
SIDECAR = OUTPUT / "residual_ares_error_summary.mpl.yaml"


def _load_rows() -> list[dict[str, str]]:
    with METRICS.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def main() -> None:
    rows = _load_rows()
    grouped: dict[str, list[float]] = {}
    timings: dict[str, list[float]] = {}
    for row in rows:
        grouped.setdefault(row["closure"], []).append(float(row["ares_total_rel_error"]))
        timings.setdefault(row["closure"], []).append(float(row["speedup_ratio"]))
    names = sorted(grouped)
    errors = [max(grouped[name]) for name in names]
    speedups = [max(timings[name]) for name in names]

    OUTPUT.mkdir(parents=True, exist_ok=True)
    with PLOTTED.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["closure", "max_ares_total_rel_error", "max_speedup_ratio"])
        writer.writerows(zip(names, errors, speedups))

    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.bar(names, errors, color="#6f8f3a")
    ax.set_yscale("symlog", linthresh=0.03, linscale=0.8)
    ax.set_title("Explicit association total residual Helmholtz error")
    ax.set_ylabel("Max relative total ares error")
    ax.set_xlabel("Closure")
    ax.tick_params(axis="x", rotation=30)
    ax.grid(axis="y", color="#d9d9d9", linewidth=0.6)
    fig.tight_layout()
    fig.savefig(FIGURE, dpi=160)
    plt.close(fig)
    SIDECAR.write_text(
        "\n".join(
            (
                "kind: matplotlib-figure",
                "version: 1",
                "plot_id: explicit_association_total_residual_ares_error",
                "title: Explicit association total residual Helmholtz error",
                "matplotlib:",
                "  title: Explicit association total residual Helmholtz error",
                "  x_label: Closure",
                "  y_label: Max relative total ares error",
                "  y_scale: symlog",
                "files:",
                "  figure: residual_ares_error_summary.png",
                "  source_data: residual_ares_error_summary_plotted_data.csv",
                "render:",
                "  command: uv run python analyses/package_validation/explicit_association_toybox/figures/residual_ares_error/scripts/render_figure.py",
                "",
            )
        ),
        encoding="utf-8",
    )
    print(FIGURE)


if __name__ == "__main__":
    main()
