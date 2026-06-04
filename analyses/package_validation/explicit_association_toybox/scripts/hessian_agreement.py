from __future__ import annotations

import argparse
from collections.abc import Iterable, Mapping
from pathlib import Path

import numpy as np

from .association_models import AssociationSystem
from .closure_models import CANDIDATE_CLOSURES
from .derivative_agreement import centered_slope
from .implicit_sensitivity import (
    exact_binary_composition_sensitivity,
    exact_density_sensitivity,
    exact_strength_sensitivity,
)
from .propagation_evidence import closure_association_value, relative_error, write_rows_csv

ANALYSIS_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ANALYSIS_ROOT / "figures" / "hessian_agreement" / "output" / "hessian_agreement.csv"
DEFAULT_CLOSURES = CANDIDATE_CLOSURES
HESSIAN_TARGETS = ("density_density", "density_strength", "strength_strength", "composition_composition")


def run_hessian_agreement_cases(*, closure_names: Iterable[str] = DEFAULT_CLOSURES) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for case in _hessian_cases():
        for closure_name in closure_names:
            rows.extend(_case_rows(case, closure_name))
    return rows


def generate_hessian_agreement(output_path: Path = DEFAULT_OUTPUT) -> Path:
    return write_rows_csv(run_hessian_agreement_cases(), output_path)


def _case_rows(case: Mapping[str, object], closure_name: str) -> list[dict[str, object]]:
    case_id = str(case["case_id"])
    system = case["system"]
    if not isinstance(system, AssociationSystem):
        raise ValueError("hessian case system must be an AssociationSystem.")
    density = float(case["density"])
    strength = float(case["strength"])
    composition = np.asarray(case["composition"], dtype=float)
    rows: list[dict[str, object]] = []
    targets = ("density_density", "density_strength", "strength_strength")
    if system.component_count == 2:
        targets = targets + ("composition_composition",)
    for target in targets:
        exact_value = exact_hessian_target(
            target,
            system=system,
            density=density,
            strength=strength,
            composition=composition,
        )
        closure_value = _closure_hessian_target(
            target,
            closure_name=closure_name,
            system=system,
            density=density,
            strength=strength,
            composition=composition,
        )
        diagnostics = _exact_diagnostics(
            target,
            system=system,
            density=density,
            strength=strength,
            composition=composition,
        )
        rows.append(
            {
                "case_id": case_id,
                "closure_name": closure_name,
                "target": target,
                "exact_hessian": exact_value,
                "closure_hessian": closure_value,
                "hessian_abs_error": abs(closure_value - exact_value),
                "hessian_rel_error": relative_error(closure_value, exact_value),
                "exact_hessian_method": "centered_difference_of_implicit_first_derivative",
                "closure_hessian_method": "centered_difference_of_closure_first_derivative",
                "implicit_jacobian_condition_number": diagnostics["implicit_jacobian_condition_number"],
                "mass_action_residual_inf": diagnostics["mass_action_residual_inf"],
            }
        )
    return rows


def exact_hessian_target(
    target: str,
    *,
    system: AssociationSystem,
    density: float,
    strength: float,
    composition: np.ndarray,
) -> float:
    if target == "density_density":
        step = max(1.0e-5, density * 1.0e-4)
        return centered_slope(
            lambda value: exact_density_sensitivity(
                system=system,
                density=value,
                composition=composition,
                delta=system.delta_matrix(strength),
            ).da_dtheta,
            base_value=density,
            step_size=step,
        )
    if target == "density_strength":
        step = max(1.0e-4, strength * 1.0e-4)
        return centered_slope(
            lambda value: exact_density_sensitivity(
                system=system,
                density=density,
                composition=composition,
                delta=system.delta_matrix(value),
            ).da_dtheta,
            base_value=strength,
            step_size=step,
        )
    if target == "strength_strength":
        step = max(1.0e-4, strength * 1.0e-4)
        return centered_slope(
            lambda value: exact_strength_sensitivity(
                system=system,
                density=density,
                composition=composition,
                delta=system.delta_matrix(value),
                strength=value,
            ).da_dtheta,
            base_value=strength,
            step_size=step,
        )
    if target == "composition_composition":
        step = 1.0e-5
        return centered_slope(
            lambda x0: exact_binary_composition_sensitivity(
                system=system,
                density=density,
                composition=np.array([x0, 1.0 - x0], dtype=float),
                delta=system.delta_matrix(strength),
            ).da_dtheta,
            base_value=float(composition[0]),
            step_size=step,
        )
    raise ValueError(f"Unknown hessian target: {target}")


def _closure_hessian_target(
    target: str,
    *,
    closure_name: str,
    system: AssociationSystem,
    density: float,
    strength: float,
    composition: np.ndarray,
) -> float:
    if target == "density_density":
        step = max(1.0e-5, density * 1.0e-4)
        return centered_slope(
            lambda value: _closure_density_slope(
                closure_name,
                system=system,
                density=value,
                strength=strength,
                composition=composition,
            ),
            base_value=density,
            step_size=step,
        )
    if target == "density_strength":
        step = max(1.0e-4, strength * 1.0e-4)
        return centered_slope(
            lambda value: _closure_density_slope(
                closure_name,
                system=system,
                density=density,
                strength=value,
                composition=composition,
            ),
            base_value=strength,
            step_size=step,
        )
    if target == "strength_strength":
        step = max(1.0e-4, strength * 1.0e-4)
        return centered_slope(
            lambda value: _closure_strength_slope(
                closure_name,
                system=system,
                density=density,
                strength=value,
                composition=composition,
            ),
            base_value=strength,
            step_size=step,
        )
    if target == "composition_composition":
        step = 1.0e-5
        return centered_slope(
            lambda x0: _closure_composition_slope(
                closure_name,
                system=system,
                density=density,
                strength=strength,
                composition=np.array([x0, 1.0 - x0], dtype=float),
            ),
            base_value=float(composition[0]),
            step_size=step,
        )
    raise ValueError(f"Unknown hessian target: {target}")


def _closure_density_slope(
    closure_name: str,
    *,
    system: AssociationSystem,
    density: float,
    strength: float,
    composition: np.ndarray,
) -> float:
    step = max(1.0e-5, density * 1.0e-4)
    return centered_slope(
        lambda value: _closure_value(
            closure_name,
            system=system,
            density=value,
            strength=strength,
            composition=composition,
        ),
        base_value=density,
        step_size=step,
    )


def _closure_strength_slope(
    closure_name: str,
    *,
    system: AssociationSystem,
    density: float,
    strength: float,
    composition: np.ndarray,
) -> float:
    step = max(1.0e-4, strength * 1.0e-4)
    return centered_slope(
        lambda value: _closure_value(
            closure_name,
            system=system,
            density=density,
            strength=value,
            composition=composition,
        ),
        base_value=strength,
        step_size=step,
    )


def _closure_composition_slope(
    closure_name: str,
    *,
    system: AssociationSystem,
    density: float,
    strength: float,
    composition: np.ndarray,
) -> float:
    step = 1.0e-5
    return centered_slope(
        lambda x0: _closure_value(
            closure_name,
            system=system,
            density=density,
            strength=strength,
            composition=np.array([x0, 1.0 - x0], dtype=float),
        ),
        base_value=float(composition[0]),
        step_size=step,
    )


def _closure_value(
    closure_name: str,
    *,
    system: AssociationSystem,
    density: float,
    strength: float,
    composition: np.ndarray,
) -> float:
    _, value, _ = closure_association_value(
        closure_name,
        system=system,
        density=density,
        composition=composition,
        delta=system.delta_matrix(strength),
    )
    return value


def _exact_diagnostics(
    target: str,
    *,
    system: AssociationSystem,
    density: float,
    strength: float,
    composition: np.ndarray,
) -> dict[str, float]:
    if target in {"strength_strength"}:
        sensitivity = exact_strength_sensitivity(
            system=system,
            density=density,
            composition=composition,
            delta=system.delta_matrix(strength),
            strength=strength,
        )
    elif target == "composition_composition":
        sensitivity = exact_binary_composition_sensitivity(
            system=system,
            density=density,
            composition=composition,
            delta=system.delta_matrix(strength),
        )
    else:
        sensitivity = exact_density_sensitivity(
            system=system,
            density=density,
            composition=composition,
            delta=system.delta_matrix(strength),
        )
    return {
        "implicit_jacobian_condition_number": sensitivity.jacobian_condition_number,
        "mass_action_residual_inf": sensitivity.mass_action_residual_inf,
    }


def _hessian_cases() -> tuple[dict[str, object], ...]:
    return (
        {
            "case_id": "pure_2b_moderate",
            "system": AssociationSystem(
                component_count=1,
                site_component_index=np.array([0, 0], dtype=int),
                site_kind=("D", "A"),
                active_pairs=((0, 1), (1, 0)),
            ),
            "density": 0.05,
            "strength": 10.0,
            "composition": np.array([1.0], dtype=float),
        },
        {
            "case_id": "cross_binary_asymmetric",
            "system": AssociationSystem(
                component_count=2,
                site_component_index=np.array([0, 1], dtype=int),
                site_kind=("D", "A"),
                active_pairs=((0, 1), (1, 0)),
            ),
            "density": 0.05,
            "strength": 10.0,
            "composition": np.array([0.35, 0.65], dtype=float),
        },
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate Picard Hessian agreement diagnostics.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    print(generate_hessian_agreement(args.output))


if __name__ == "__main__":
    main()
