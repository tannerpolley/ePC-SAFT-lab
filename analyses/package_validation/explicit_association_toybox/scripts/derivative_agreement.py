from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping
from pathlib import Path

import numpy as np

from .association_models import AssociationSystem
from .propagation_evidence import (
    closure_association_value,
    exact_association_value,
    evaluate_named_closure,
    relative_error,
    write_rows_csv,
)

ANALYSIS_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ANALYSIS_ROOT / "figures" / "derivative_agreement" / "output" / "derivative_agreement.csv"
DERIVATIVE_TARGETS = (
    "a_assoc_density",
    "a_assoc_strength",
    "a_assoc_composition_0",
    "pressure_proxy_density",
    "mu_proxy_composition_0",
    "fugacity_proxy_composition_0",
)
DEFAULT_CLOSURES = ("damped_picard_3_05", "damped_picard_5_05", "damped_picard_7_05", "picard3_diag_newton1")


def centered_slope(function: Callable[[float], float], *, base_value: float, step_size: float) -> float:
    if step_size <= 0.0:
        raise ValueError("step_size must be positive.")
    return float((function(base_value + step_size) - function(base_value - step_size)) / (2.0 * step_size))


def pressure_proxy_from_ares(*, density: float, ares_value: float, density_slope: float) -> float:
    return float(density * ares_value + density * density * density_slope)


def mu_proxy_from_composition_slope(composition_slope: float) -> float:
    return float(composition_slope)


def fugacity_proxy_from_mu(mu_proxy: float) -> float:
    return float(np.exp(np.clip(mu_proxy, -50.0, 50.0)))


def summarize_derivative_agreement(samples: Iterable[Mapping[str, object]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for sample in samples:
        exact = float(sample["exact_derivative"])
        closure = float(sample["closure_derivative"])
        exact_elapsed = float(sample["exact_implicit_elapsed_seconds"])
        closure_elapsed = float(sample["closure_elapsed_seconds"])
        rows.append(
            {
                **dict(sample),
                "derivative_abs_error": abs(closure - exact),
                "derivative_rel_error": relative_error(closure, exact),
                "speedup_vs_exact_implicit": exact_elapsed / closure_elapsed if closure_elapsed > 0.0 else np.nan,
            }
        )
    return rows


def run_derivative_agreement_cases(
    *,
    closure_names: Iterable[str] = DEFAULT_CLOSURES,
) -> list[dict[str, object]]:
    cases = _derivative_cases()
    samples: list[dict[str, object]] = []
    for case in cases:
        for closure_name in closure_names:
            samples.extend(_case_samples(case, closure_name))
    return summarize_derivative_agreement(samples)


def generate_derivative_agreement(output_path: Path = DEFAULT_OUTPUT) -> Path:
    return write_rows_csv(run_derivative_agreement_cases(), output_path)


def _case_samples(case: Mapping[str, object], closure_name: str) -> list[dict[str, object]]:
    case_id = str(case["case_id"])
    system = case["system"]
    if not isinstance(system, AssociationSystem):
        raise ValueError("case system must be an AssociationSystem.")
    density = float(case["density"])
    strength = float(case["strength"])
    composition = np.asarray(case["composition"], dtype=float)
    delta = system.delta_matrix(strength)
    _, _, exact_elapsed = exact_association_value(system=system, density=density, composition=composition, delta=delta)
    _, _, closure_elapsed = closure_association_value(
        closure_name,
        system=system,
        density=density,
        composition=composition,
        delta=delta,
    )
    rows: list[dict[str, object]] = []
    targets = ("a_assoc_density", "a_assoc_strength", "pressure_proxy_density")
    if system.component_count == 2:
        targets = targets + ("a_assoc_composition_0", "mu_proxy_composition_0", "fugacity_proxy_composition_0")
    for target in targets:
        exact_derivative = _target_derivative(
            target,
            exact=True,
            closure_name=closure_name,
            system=system,
            density=density,
            strength=strength,
            composition=composition,
        )
        closure_derivative = _target_derivative(
            target,
            exact=False,
            closure_name=closure_name,
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
                "exact_derivative": exact_derivative,
                "closure_derivative": closure_derivative,
                "exact_implicit_elapsed_seconds": exact_elapsed,
                "closure_elapsed_seconds": closure_elapsed,
            }
        )
    return rows


def _target_derivative(
    target: str,
    *,
    exact: bool,
    closure_name: str,
    system: AssociationSystem,
    density: float,
    strength: float,
    composition: np.ndarray,
) -> float:
    if target == "a_assoc_density":
        return centered_slope(
            lambda value: _association_scalar(
                exact=exact,
                closure_name=closure_name,
                system=system,
                density=value,
                strength=strength,
                composition=composition,
            ),
            base_value=density,
            step_size=max(1.0e-5, density * 1.0e-3),
        )
    if target == "a_assoc_strength":
        return centered_slope(
            lambda value: _association_scalar(
                exact=exact,
                closure_name=closure_name,
                system=system,
                density=density,
                strength=max(value, 1.0e-8),
                composition=composition,
            ),
            base_value=strength,
            step_size=max(1.0e-4, strength * 1.0e-3),
        )
    if target == "a_assoc_composition_0":
        return centered_slope(
            lambda value: _association_scalar(
                exact=exact,
                closure_name=closure_name,
                system=system,
                density=density,
                strength=strength,
                composition=np.array([value, 1.0 - value], dtype=float),
            ),
            base_value=float(composition[0]),
            step_size=1.0e-4,
        )
    if target == "pressure_proxy_density":
        return centered_slope(
            lambda value: _pressure_proxy_scalar(
                exact=exact,
                closure_name=closure_name,
                system=system,
                density=value,
                strength=strength,
                composition=composition,
            ),
            base_value=density,
            step_size=max(1.0e-5, density * 1.0e-3),
        )
    if target == "mu_proxy_composition_0":
        return _target_derivative(
            "a_assoc_composition_0",
            exact=exact,
            closure_name=closure_name,
            system=system,
            density=density,
            strength=strength,
            composition=composition,
        )
    if target == "fugacity_proxy_composition_0":
        return centered_slope(
            lambda value: fugacity_proxy_from_mu(
                mu_proxy_from_composition_slope(
                    _target_derivative(
                        "a_assoc_composition_0",
                        exact=exact,
                        closure_name=closure_name,
                        system=system,
                        density=density,
                        strength=strength,
                        composition=np.array([value, 1.0 - value], dtype=float),
                    )
                )
            ),
            base_value=float(composition[0]),
            step_size=1.0e-4,
        )
    raise ValueError(f"Unknown derivative target: {target}")


def _association_scalar(
    *,
    exact: bool,
    closure_name: str,
    system: AssociationSystem,
    density: float,
    strength: float,
    composition: np.ndarray,
) -> float:
    delta = system.delta_matrix(strength)
    if exact:
        _, value, _ = exact_association_value(system=system, density=density, composition=composition, delta=delta)
        return value
    _, value, _ = closure_association_value(
        closure_name,
        system=system,
        density=density,
        composition=composition,
        delta=delta,
    )
    return value


def _pressure_proxy_scalar(
    *,
    exact: bool,
    closure_name: str,
    system: AssociationSystem,
    density: float,
    strength: float,
    composition: np.ndarray,
) -> float:
    ares_value = _association_scalar(
        exact=exact,
        closure_name=closure_name,
        system=system,
        density=density,
        strength=strength,
        composition=composition,
    )
    slope = centered_slope(
        lambda value: _association_scalar(
            exact=exact,
            closure_name=closure_name,
            system=system,
            density=value,
            strength=strength,
            composition=composition,
        ),
        base_value=density,
        step_size=max(1.0e-5, density * 1.0e-3),
    )
    return pressure_proxy_from_ares(density=density, ares_value=ares_value, density_slope=slope)


def _derivative_cases() -> tuple[dict[str, object], ...]:
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
