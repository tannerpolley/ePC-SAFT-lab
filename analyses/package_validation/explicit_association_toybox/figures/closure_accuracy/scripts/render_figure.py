from __future__ import annotations

import csv
from pathlib import Path

import matplotlib.pyplot as plt

ANALYSIS_ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ANALYSIS_ROOT / "figures" / "closure_accuracy" / "output"
METRICS = OUTPUT / "closure_metrics.csv"
FIGURE = OUTPUT / "closure_accuracy_summary.png"
PLOTTED = OUTPUT / "closure_accuracy_summary_plotted_data.csv"
SIDECAR = OUTPUT / "closure_accuracy_summary.mpl.yaml"


def _load_rows() -> list[dict[str, str]]:
    with METRICS.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def main() -> None:
    rows = _load_rows()
    grouped: dict[str, list[float]] = {}
    for row in rows:
        grouped.setdefault(row["closure"], []).append(float(row["assoc_helmholtz_rel_error"]))
    names = sorted(grouped)
    values = [max(grouped[name]) for name in names]
    OUTPUT.mkdir(parents=True, exist_ok=True)
    with PLOTTED.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["closure", "max_assoc_helmholtz_rel_error"])
        writer.writerows(zip(names, values))

    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.bar(names, values, color="#2f6f9f")
    ax.axhline(0.03, color="black", linestyle="--", linewidth=1.0, label="3 percent reference")
    ax.set_yscale("symlog", linthresh=0.03, linscale=0.8)
    ax.set_title("Explicit association closure accuracy")
    ax.set_ylabel("Max relative association Helmholtz error")
    ax.set_xlabel("Closure")
    ax.tick_params(axis="x", rotation=30)
    ax.grid(axis="y", color="#d9d9d9", linewidth=0.6)
    ax.legend()
    fig.tight_layout()
    fig.savefig(FIGURE, dpi=160)
    plt.close(fig)
    SIDECAR.write_text(
        "\n".join(
            (
                "kind: matplotlib-figure",
                "version: 1",
                "plot_id: explicit_association_closure_accuracy_summary",
                "title: Explicit association closure accuracy",
                "matplotlib:",
                "  title: Explicit association closure accuracy",
                "  x_label: Closure",
                "  y_label: Max relative association Helmholtz error",
                "  y_scale: symlog",
                "  reference_line: 0.03",
                "files:",
                "  figure: closure_accuracy_summary.png",
                "  source_data: closure_accuracy_summary_plotted_data.csv",
                "render:",
                "  command: uv run python analyses/package_validation/explicit_association_toybox/figures/closure_accuracy/scripts/render_figure.py",
                "",
            )
        ),
        encoding="utf-8",
    )
    print(FIGURE)


if __name__ == "__main__":
    main()
