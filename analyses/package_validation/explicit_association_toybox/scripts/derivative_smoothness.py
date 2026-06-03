from __future__ import annotations

import argparse
import csv
from collections.abc import Iterable
from pathlib import Path

import numpy as np

from .association_models import AssociationSystem, association_helmholtz
from .closure_models import evaluate_closure
from .exact_baseline import solve_exact_site_fractions
from .topology_reductions import topology_system

ANALYSIS_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ANALYSIS_ROOT / "figures" / "derivative_smoothness" / "output" / "derivative_smoothness.csv"
DEFAULT_CLOSURES = ("implicit_exact_mass_action", "explicit_damped_picard_unroll_3", "explicit_picard3_diag_newton1")


def derivative_smoothness_rows(
    *,
    closure_names: Iterable[str] = DEFAULT_CLOSURES,
    density: float = 0.05,
    strength: float = 10.0,
    step_fraction: float = 1.0e-3,
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for closure_name in closure_names:
        rows.append(
            evaluate_density_smoothness(
                closure_name=closure_name,
                density=density,
                strength=strength,
                step_fraction=step_fraction,
            )
        )
        rows.append(
            evaluate_strength_smoothness(
                closure_name=closure_name,
                density=density,
                strength=strength,
                step_fraction=step_fraction,
            )
        )
        rows.append(
            evaluate_composition_smoothness(
                closure_name=closure_name,
                density=density,
                strength=strength,
                step_fraction=step_fraction,
            )
        )
    return rows


def evaluate_density_smoothness(
    *,
    closure_name: str,
    density: float,
    strength: float,
    step_fraction: float,
) -> dict[str, object]:
    step = max(abs(density) * step_fraction, 1.0e-6)
    system = topology_system("2B")
    composition = np.array([1.0], dtype=float)

    def evaluator(value: float) -> float:
        return _association_value(
            closure_name,
            system=system,
            density=value,
            strength=strength,
            composition=composition,
        )

    return _slope_row(
        closure_name=closure_name,
        perturbation_axis="density",
        base_value=density,
        step_size=step,
        evaluator=evaluator,
    )


def evaluate_strength_smoothness(
    *,
    closure_name: str,
    density: float,
    strength: float,
    step_fraction: float,
) -> dict[str, object]:
    step = max(abs(strength) * step_fraction, 1.0e-5)
    system = topology_system("2B")
    composition = np.array([1.0], dtype=float)

    def evaluator(value: float) -> float:
        return _association_value(
            closure_name,
            system=system,
            density=density,
            strength=value,
            composition=composition,
        )

    return _slope_row(
        closure_name=closure_name,
        perturbation_axis="association_strength_scale",
        base_value=strength,
        step_size=step,
        evaluator=evaluator,
    )


def evaluate_composition_smoothness(
    *,
    closure_name: str,
    density: float,
    strength: float,
    step_fraction: float,
) -> dict[str, object]:
    step = max(0.5 * step_fraction, 1.0e-5)
    system = _binary_da_system()

    def evaluator(value: float) -> float:
        composition = np.array([value, 1.0 - value], dtype=float)
        return _association_value(
            closure_name,
            system=system,
            density=density,
            strength=strength,
            composition=composition,
        )

    return _slope_row(
        closure_name=closure_name,
        perturbation_axis="composition_component_0",
        base_value=0.5,
        step_size=step,
        evaluator=evaluator,
    )


def write_derivative_smoothness_csv(rows: list[dict[str, object]], output_path: Path = DEFAULT_OUTPUT) -> Path:
    if not rows:
        raise ValueError("derivative smoothness rows are required.")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    return output_path


def generate_derivative_smoothness(output_path: Path = DEFAULT_OUTPUT) -> Path:
    return write_derivative_smoothness_csv(derivative_smoothness_rows(), output_path)


def _association_value(
    closure_name: str,
    *,
    system: AssociationSystem,
    density: float,
    strength: float,
    composition: np.ndarray,
) -> float:
    delta = system.delta_matrix(strength)
    if closure_name == "implicit_exact_mass_action":
        result = solve_exact_site_fractions(
            density=density,
            x_assoc=system.x_assoc(composition),
            delta=delta,
        )
        xa = result.xa
    else:
        result = evaluate_closure(
            closure_name,
            system=system,
            density=density,
            composition=composition,
            delta=delta,
        )
        xa = result.xa
    return float(association_helmholtz(xa, composition, system.site_component_index))


def _slope_row(
    *,
    closure_name: str,
    perturbation_axis: str,
    base_value: float,
    step_size: float,
    evaluator,
) -> dict[str, object]:
    left_value = evaluator(base_value - step_size)
    center_value = evaluator(base_value)
    right_value = evaluator(base_value + step_size)
    left_slope = (center_value - left_value) / step_size
    right_slope = (right_value - center_value) / step_size
    jump = abs(right_slope - left_slope)
    slope_scale = max(abs(left_slope), abs(right_slope))
    relative_jump = 0.0 if slope_scale <= 1.0e-12 and jump <= 1.0e-12 else jump / max(slope_scale, 1.0e-14)
    return {
        "closure_name": closure_name,
        "perturbation_axis": perturbation_axis,
        "base_value": base_value,
        "step_size": step_size,
        "first_derivative_left": left_slope,
        "first_derivative_right": right_slope,
        "derivative_jump_abs": jump,
        "relative_jump": relative_jump,
        "smoothness_band": _smoothness_band(relative_jump),
    }


def _smoothness_band(relative_jump: float) -> str:
    if relative_jump <= 1.0e-4:
        return "smooth"
    if relative_jump <= 1.0e-2:
        return "mild_transition"
    return "diagnostic_transition"


def _binary_da_system() -> AssociationSystem:
    return AssociationSystem(
        component_count=2,
        site_component_index=np.array([0, 0, 1, 1], dtype=int),
        site_kind=("D", "A", "D", "A"),
        active_pairs=((0, 1), (1, 0), (2, 3), (3, 2), (0, 3), (3, 0), (2, 1), (1, 2)),
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Run explicit association closure derivative-smoothness diagnostics.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    print(generate_derivative_smoothness(args.output))


if __name__ == "__main__":
    main()
