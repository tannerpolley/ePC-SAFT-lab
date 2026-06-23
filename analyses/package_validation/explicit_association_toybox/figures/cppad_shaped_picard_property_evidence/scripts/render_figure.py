from __future__ import annotations

import csv
import sys
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
    apply_plot_style,
    case_label,
    save_plot_artifacts,
    style_axis,
)

OUTPUT = ANALYSIS_ROOT / "figures" / "cppad_shaped_picard_property_evidence" / "output"
SOURCE = OUTPUT / "cppad_shaped_picard_property_evidence.csv"
PLOTTED = OUTPUT / "cppad_shaped_picard_property_evidence_plotted_data.csv"
FIGURE = OUTPUT / "cppad_shaped_picard_property_evidence.png"
SELECTED_CASES = (
    "pure_2b_self",
    "cross_associating_binary",
    "mixed_2b_3b_binary",
    "mixed_2b_4c_binary",
    "mixed_4c_4c_binary",
)
BACKEND_LABELS = {
    "exact": "Exact implicit",
    "numpy": "Picard NumPy",
    "jax": "Picard JAX",
}
BACKEND_COLORS = {
    "exact": BLUE,
    "numpy": ORANGE,
    "jax": GREEN,
}
PICARD_LINE = (0, (1.2, 1.8))


def main() -> None:
    apply_plot_style()
    with SOURCE.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    plotted = _plotted_rows(rows)
    OUTPUT.mkdir(parents=True, exist_ok=True)
    with PLOTTED.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(plotted[0]))
        writer.writeheader()
        writer.writerows(plotted)
    _render(plotted)
    print(FIGURE)


def _plotted_rows(rows: list[dict[str, str]]) -> list[dict[str, object]]:
    plotted: list[dict[str, object]] = []
    for row in rows:
        if row["case_id"] not in SELECTED_CASES:
            continue
        if row["picard_backend"] == "numpy":
            plotted.append(
                {
                    "case_id": row["case_id"],
                    "case_label": case_label(row["case_id"]),
                    "backend": "exact",
                    "backend_label": BACKEND_LABELS["exact"],
                    "density": float(row["density"]),
                    "association_helmholtz": float(row["association_helmholtz_exact"]),
                    "pressure_proxy": float(row["pressure_exact"]),
                    "relative_error": 0.0,
                }
            )
        plotted.append(
            {
                "case_id": row["case_id"],
                "case_label": case_label(row["case_id"]),
                "backend": row["picard_backend"],
                "backend_label": BACKEND_LABELS[row["picard_backend"]],
                "density": float(row["density"]),
                "association_helmholtz": float(row["association_helmholtz_picard"]),
                "pressure_proxy": float(row["pressure_picard"]),
                "relative_error": float(row["relative_error"]),
            }
        )
    if not plotted:
        raise ValueError("CppAD-shaped property plotting received no retained rows.")
    return plotted


def _render(rows: list[dict[str, object]]) -> None:
    fig, axes = plt.subplots(
        len(SELECTED_CASES),
        2,
        figsize=(9.6, 12.0),
        constrained_layout=True,
    )
    for row_index, case_id in enumerate(SELECTED_CASES):
        case_rows = [row for row in rows if row["case_id"] == case_id]
        for backend in ("exact", "numpy", "jax"):
            backend_rows = sorted(
                [row for row in case_rows if row["backend"] == backend],
                key=lambda item: float(item["density"]),
            )
            if not backend_rows:
                continue
            linestyle = "-" if backend == "exact" else PICARD_LINE
            marker = "o" if backend == "exact" else "s"
            color = BACKEND_COLORS[backend]
            label = BACKEND_LABELS[backend]
            axes[row_index, 0].plot(
                [float(row["density"]) for row in backend_rows],
                [float(row["association_helmholtz"]) for row in backend_rows],
                marker=marker,
                linestyle=linestyle,
                color=color,
                linewidth=1.8,
                markersize=4.2,
                label=label,
            )
            axes[row_index, 1].plot(
                [float(row["density"]) for row in backend_rows],
                [float(row["pressure_proxy"]) for row in backend_rows],
                marker=marker,
                linestyle=linestyle,
                color=color,
                linewidth=1.8,
                markersize=4.2,
                label=label,
            )
        axes[row_index, 0].set_ylabel(r"$a^{\mathrm{assoc}}$")
        axes[row_index, 1].set_ylabel(r"$P_{\mathrm{proxy}}$")
        for axis in axes[row_index]:
            axis.set_title(case_label(case_id), loc="left")
            axis.set_xlabel(r"$\rho$")
            style_axis(axis)
    axes[0, 0].legend(frameon=False, loc="best")
    fig.suptitle("Picard property evidence across pure and mixture association cases")
    save_plot_artifacts(fig, FIGURE)
    plt.close(fig)


if __name__ == "__main__":
    main()
