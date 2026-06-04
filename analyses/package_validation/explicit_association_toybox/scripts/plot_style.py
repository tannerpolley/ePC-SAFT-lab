from __future__ import annotations

import math
from pathlib import Path

import matplotlib.pyplot as plt

PICARD_LABEL = "Picard"
EXACT_LABEL = "Exact implicit"

BLUE = "#2b6f9f"
ORANGE = "#b65f22"
GREEN = "#2f7d5c"
PURPLE = "#6d5aa8"
GRAY = "#6b7280"
RED = "#9b3f2f"


def apply_plot_style() -> None:
    plt.rcParams.update(
        {
            "figure.dpi": 160,
            "savefig.dpi": 180,
            "font.family": "serif",
            "mathtext.fontset": "stix",
            "figure.titlesize": 15,
            "axes.titlesize": 14,
            "axes.labelsize": 11,
            "xtick.labelsize": 9,
            "ytick.labelsize": 9,
            "legend.fontsize": 9,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.grid": False,
        }
    )


def style_axis(ax, *, grid_axis: str = "y", minor: bool = False) -> None:
    ax.grid(axis=grid_axis, which="major", color="#d9dde3", linewidth=0.7)
    if minor:
        ax.grid(axis=grid_axis, which="minor", color="#eceff3", linewidth=0.45, alpha=0.8)


def log_fit_line(x_values: list[float], y_values: list[float], *, points: int = 120) -> tuple[list[float], list[float]]:
    pairs = [(x, y) for x, y in zip(x_values, y_values, strict=False) if x > 0.0 and y > 0.0]
    if len(pairs) < 2:
        return [], []
    xs = [math.log10(x) for x, _ in pairs]
    ys = [math.log10(y) for _, y in pairs]
    count = float(len(pairs))
    sum_x = sum(xs)
    sum_y = sum(ys)
    sum_xx = sum(x * x for x in xs)
    sum_xy = sum(x * y for x, y in zip(xs, ys, strict=True))
    denominator = count * sum_xx - sum_x * sum_x
    if abs(denominator) < 1.0e-30:
        return [], []
    slope = (count * sum_xy - sum_x * sum_y) / denominator
    intercept = (sum_y - slope * sum_x) / count
    lo = min(xs)
    hi = max(xs)
    if lo == hi:
        return [], []
    fit_x = [10.0 ** (lo + (hi - lo) * index / float(points - 1)) for index in range(points)]
    fit_y = [10.0 ** (intercept + slope * math.log10(value)) for value in fit_x]
    return fit_x, fit_y


def closure_label(name: str) -> str:
    labels = {
        "damped_picard_7_05": PICARD_LABEL,
        "implicit_exact_mass_action": EXACT_LABEL,
    }
    if name.startswith("topology_reduction_huang_radosz_"):
        return "Huang/Radosz exact"
    return labels.get(name, name.replace("_", " "))


def role_label(name: str) -> str:
    labels = {
        "explicit_approximation": PICARD_LABEL,
        "exact_topology_reduction": "Huang/Radosz exact",
        "candidate_accuracy": "candidate",
        "reject_for_provider_path": "reject",
    }
    return labels.get(name, name.replace("_", " "))


def target_label(name: str) -> str:
    labels = {
        "a_assoc_density": r"$\partial a_{\mathrm{assoc}}/\partial \rho$",
        "a_assoc_strength": r"$\partial a_{\mathrm{assoc}}/\partial \Delta$",
        "a_assoc_composition_0": r"$\partial a_{\mathrm{assoc}}/\partial x_1$",
        "pressure_proxy_density": r"$\partial P_{\mathrm{proxy}}/\partial \rho$",
        "mu_proxy_composition_0": r"$\partial \mu_{\mathrm{proxy}}/\partial x_1$",
        "fugacity_proxy_composition_0": r"$\partial f_{\mathrm{proxy}}/\partial x_1$",
        "density": r"$\rho$",
        "association_strength_scale": r"$\Delta$",
        "composition_component_0": r"$x_1$",
    }
    return labels.get(name, name.replace("_", " "))


def case_label(name: str) -> str:
    labels = {
        "pure_2b_moderate": "pure 2B",
        "cross_binary_asymmetric": "cross binary",
        "pure_2b_low_total_context": "2B low",
        "pure_3b_moderate_total_context": "3B moderate",
        "pure_4c_moderate_total_context": "4C moderate",
        "local_objective_cross_binary_proxy": "cross-binary objective",
        "assoc_plus_inert_2b_x20": "associating + inert",
        "cross_assoc_binary_x30": "cross association",
        "unequal_delta_binary_x70": r"unequal $\Delta_{ij}$",
        "non_equimolar_3b_like_binary": "non-equimolar",
        "water_3b_4c_contrast_binary": "water-like topology",
    }
    return labels.get(name, name.replace("_", " "))


def save_png_svg(fig, png_path: Path) -> Path:
    svg_path = png_path.with_suffix(".svg")
    fig.savefig(png_path, dpi=180)
    fig.savefig(svg_path)
    return svg_path


def write_sidecar(
    path: Path,
    *,
    plot_id: str,
    title: str,
    figure: Path,
    source_data: Path,
    x_label: str,
    y_label: str,
    y_scale: str | None = None,
    extra_files: dict[str, Path] | None = None,
    command: str | None = None,
) -> None:
    files = {
        "figure": figure.name,
        "svg": figure.with_suffix(".svg").name,
        "source_data": source_data.name,
    }
    if extra_files:
        files.update({key: value.name for key, value in extra_files.items()})
    lines = [
        "kind: matplotlib-figure",
        "version: 1",
        f"plot_id: {plot_id}",
        f"title: {title}",
        "matplotlib:",
        f"  title: {title}",
        f"  x_label: {x_label}",
        f"  y_label: {y_label}",
    ]
    if y_scale is not None:
        lines.append(f"  y_scale: {y_scale}")
    lines.append("files:")
    lines.extend(f"  {key}: {value}" for key, value in files.items())
    if command:
        lines.extend(("render:", f"  command: {command}"))
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")
