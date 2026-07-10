from __future__ import annotations

import argparse
import csv
import sys
from collections.abc import Iterable, Mapping
from pathlib import Path

import numpy as np

if __package__ in {None, ""}:
    REPO_ROOT = Path(__file__).resolve().parents[4]
    if str(REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))
    from analyses.package_validation.explicit_association_toybox.scripts.association_models import AssociationSystem
    from analyses.package_validation.explicit_association_toybox.scripts.closure_models import CANDIDATE_CLOSURES
    from analyses.package_validation.explicit_association_toybox.scripts.derivative_agreement import centered_slope
    from analyses.package_validation.explicit_association_toybox.scripts.implicit_sensitivity import (
        exact_binary_composition_sensitivity,
        exact_density_sensitivity,
        exact_strength_sensitivity,
    )
    from analyses.package_validation.explicit_association_toybox.scripts.jax_picard_derivatives import (
        DEFAULT_OUTPUT as JAX_SOURCE_OUTPUT,
    )
    from analyses.package_validation.explicit_association_toybox.scripts.jax_picard_derivatives import (
        run_jax_picard_derivative_cases,
    )
    from analyses.package_validation.explicit_association_toybox.scripts.propagation_evidence import (
        closure_association_value,
        relative_error,
        write_rows_csv,
    )
else:
    from .association_models import AssociationSystem
    from .closure_models import CANDIDATE_CLOSURES
    from .derivative_agreement import centered_slope
    from .implicit_sensitivity import (
        exact_binary_composition_sensitivity,
        exact_density_sensitivity,
        exact_strength_sensitivity,
    )
    from .jax_picard_derivatives import DEFAULT_OUTPUT as JAX_SOURCE_OUTPUT
    from .jax_picard_derivatives import run_jax_picard_derivative_cases
    from .propagation_evidence import closure_association_value, relative_error, write_rows_csv

ANALYSIS_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ANALYSIS_ROOT / "figures" / "hessian_agreement" / "output" / "hessian_agreement.csv"
DEFAULT_CLOSURES = CANDIDATE_CLOSURES
HESSIAN_TARGETS = ("density_density", "density_strength", "strength_strength", "composition_composition")


def run_hessian_agreement_cases(
    *,
    closure_names: Iterable[str] = DEFAULT_CLOSURES,
    jax_rows: Iterable[Mapping[str, object]] | None = None,
) -> list[dict[str, object]]:
    jax_index = _index_jax_rows(jax_rows if jax_rows is not None else run_jax_picard_derivative_cases())
    rows: list[dict[str, object]] = []
    for case in _hessian_cases():
        for closure_name in closure_names:
            rows.extend(_case_rows(case, closure_name, jax_index))
    return rows


def generate_hessian_agreement(
    output_path: Path = DEFAULT_OUTPUT,
    *,
    jax_rows: Iterable[Mapping[str, object]] | None = None,
) -> Path:
    return write_rows_csv(run_hessian_agreement_cases(jax_rows=jax_rows), output_path)


def _case_rows(
    case: Mapping[str, object],
    closure_name: str,
    jax_index: Mapping[tuple[str, str], Mapping[str, object]],
) -> list[dict[str, object]]:
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
        targets = (*targets, "composition_composition")
    for target in targets:
        exact_value = exact_hessian_target(
            target,
            system=system,
            density=density,
            strength=strength,
            composition=composition,
        )
        jax_row = jax_index[(case_id, target)]
        closure_value = float(jax_row["picard_jax_value"])
        diagnostics = _exact_diagnostics(
            target,
            system=system,
            density=density,
            strength=strength,
            composition=composition,
        )
        step = hessian_finite_difference_step(target, density=density, strength=strength)
        rows.append(
            {
                "case_id": case_id,
                "closure_name": closure_name,
                "target": target,
                "target_pair": target,
                "derivative_order": 2,
                "exact_hessian_value": exact_value,
                "picard_jax_hessian_value": closure_value,
                "absolute_error": abs(closure_value - exact_value),
                "relative_error": relative_error(closure_value, exact_value),
                "finite_difference_step": step,
                "baseline_status": hessian_baseline_status(),
                "autodiff_backend": "jax",
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
        step = hessian_finite_difference_step(target, density=density, strength=strength)
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
        step = hessian_finite_difference_step(target, density=density, strength=strength)
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
        step = hessian_finite_difference_step(target, density=density, strength=strength)
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
        step = hessian_finite_difference_step(target, density=density, strength=strength)
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


def hessian_finite_difference_step(target: str, *, density: float, strength: float) -> float:
    if target == "density_density":
        return max(1.0e-5, density * 1.0e-4)
    if target in {"density_strength", "strength_strength"}:
        return max(1.0e-4, strength * 1.0e-4)
    if target == "composition_composition":
        return 1.0e-5
    raise ValueError(f"Unknown hessian target: {target}")


def hessian_baseline_status() -> str:
    return "centered_finite_difference_exact_implicit"


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


def load_committed_jax_rows(source: Path = JAX_SOURCE_OUTPUT) -> list[dict[str, object]]:
    with source.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _index_jax_rows(rows: Iterable[Mapping[str, object]]) -> dict[tuple[str, str], Mapping[str, object]]:
    indexed = {
        (str(row["case_id"]), str(row["target"])): row
        for row in rows
        if int(row["derivative_order"]) == 2
    }
    if not indexed:
        raise ValueError("No second-derivative JAX rows were provided for Hessian agreement.")
    return indexed


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate Picard Hessian agreement diagnostics.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    print(generate_hessian_agreement(args.output))


if __name__ == "__main__":
    main()
