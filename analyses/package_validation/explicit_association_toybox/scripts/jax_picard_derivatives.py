from __future__ import annotations

import argparse
import csv
import time
from pathlib import Path
from typing import Iterable

import numpy as np

from .association_models import AssociationSystem
from .closure_models import PICARD7_CLOSURE
from .hessian_agreement import exact_hessian_target
from .implicit_sensitivity import (
    ImplicitSensitivityResult,
    exact_binary_composition_sensitivity,
    exact_density_sensitivity,
    exact_strength_sensitivity,
)
from .propagation_evidence import relative_error

try:
    import jax
    import jax.numpy as jnp
except ModuleNotFoundError as exc:
    raise ModuleNotFoundError(
        "JAX is required for the autodiff lane. Run with `uv run --group autodiff ...`."
    ) from exc

jax.config.update("jax_enable_x64", True)

ANALYSIS_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ANALYSIS_ROOT / "figures" / "jax_picard_derivatives" / "output" / "jax_picard_derivatives.csv"


def run_jax_picard_derivative_cases() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for case in _jax_cases():
        rows.extend(_case_rows(case))
    return rows


def generate_jax_picard_derivatives(output_path: Path = DEFAULT_OUTPUT) -> Path:
    rows = run_jax_picard_derivative_cases()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    return output_path


def _case_rows(case: dict[str, object]) -> list[dict[str, object]]:
    case_id = str(case["case_id"])
    system = case["system"]
    if not isinstance(system, AssociationSystem):
        raise ValueError("JAX derivative case system must be an AssociationSystem.")
    density = float(case["density"])
    strength = float(case["strength"])
    composition = np.asarray(case["composition"], dtype=float)
    rows: list[dict[str, object]] = []
    targets = ["density", "strength", "density_density", "density_strength", "strength_strength"]
    if system.component_count == 2:
        targets.extend(["composition", "composition_composition"])
    for target in targets:
        exact_start = time.perf_counter()
        exact_value = _exact_value(
            target,
            system=system,
            density=density,
            strength=strength,
            composition=composition,
        )
        exact_elapsed = time.perf_counter() - exact_start
        exact_diagnostics = _exact_diagnostics(
            target,
            system=system,
            density=density,
            strength=strength,
            composition=composition,
        )
        autodiff_value, autodiff_elapsed = _jax_value_with_elapsed(
            target,
            system=system,
            density=density,
            strength=strength,
            composition=composition,
        )
        rows.append(
            {
                "case_id": case_id,
                "closure_name": PICARD7_CLOSURE,
                "target": target,
                "derivative_order": 2
                if target in {
                    "density_density",
                    "density_strength",
                    "strength_strength",
                    "composition_composition",
                }
                else 1,
                "exact_implicit_value": exact_value,
                "picard_jax_value": autodiff_value,
                "abs_error": abs(autodiff_value - exact_value),
                "rel_error": relative_error(autodiff_value, exact_value),
                "implicit_jacobian_condition_number": exact_diagnostics.jacobian_condition_number,
                "mass_action_residual_inf": exact_diagnostics.mass_action_residual_inf,
                "exact_implicit_elapsed_seconds": exact_elapsed,
                "picard_jax_elapsed_seconds": autodiff_elapsed,
                "speedup_vs_exact_implicit": exact_elapsed / autodiff_elapsed if autodiff_elapsed > 0.0 else np.nan,
                "autodiff_backend": "jax",
                "exact_baseline": "implicit_function_theorem_first_derivative_or_centered_hessian",
            }
        )
    return rows


def jax_picard_association_value(
    *,
    density: float,
    strength: float,
    composition: np.ndarray,
    site_component_index: Iterable[int],
    active_pairs: Iterable[tuple[int, int]],
    site_count: int,
) -> float:
    value = jax_picard_association_scalar(
        density=density,
        strength=strength,
        composition=composition,
        site_component_index=site_component_index,
        active_pairs=active_pairs,
        site_count=site_count,
    )
    return float(value)


def jax_picard_association_scalar(
    *,
    density,
    strength,
    composition,
    site_component_index: Iterable[int],
    active_pairs: Iterable[tuple[int, int]],
    site_count: int,
):
    return _jax_picard_association_value(
        jnp.asarray(density, dtype=jnp.float64),
        jnp.asarray(strength, dtype=jnp.float64),
        jnp.asarray(composition, dtype=jnp.float64),
        jnp.asarray(tuple(site_component_index), dtype=jnp.int32),
        tuple(active_pairs),
        int(site_count),
    )


def _jax_value(
    target: str,
    *,
    system: AssociationSystem,
    density: float,
    strength: float,
    composition: np.ndarray,
) -> float:
    value, _ = _jax_value_with_elapsed(
        target,
        system=system,
        density=density,
        strength=strength,
        composition=composition,
    )
    return value


def _jax_value_with_elapsed(
    target: str,
    *,
    system: AssociationSystem,
    density: float,
    strength: float,
    composition: np.ndarray,
) -> tuple[float, float]:
    site_component_index = tuple(int(item) for item in system.site_component_index)
    active_pairs = tuple((int(i), int(j)) for i, j in system.active_pairs)

    def value(density_value, strength_value, composition_value):
        return _jax_picard_association_value(
            density_value,
            strength_value,
            composition_value,
            jnp.asarray(site_component_index, dtype=jnp.int32),
            active_pairs,
            system.site_count,
        )

    if target == "density":
        function = jax.jit(
            jax.grad(lambda rho: value(rho, strength, jnp.asarray(composition, dtype=jnp.float64)))
        )
        return _timed_jax_scalar(function, jnp.asarray(density, dtype=jnp.float64))
    if target == "strength":
        function = jax.jit(
            jax.grad(
                lambda delta_scale: value(
                    density,
                    delta_scale,
                    jnp.asarray(composition, dtype=jnp.float64),
                )
            )
        )
        return _timed_jax_scalar(function, jnp.asarray(strength, dtype=jnp.float64))
    if target == "composition":
        function = jax.jit(
            jax.grad(
                lambda x0: value(
                    density,
                    strength,
                    jnp.asarray([x0, 1.0 - x0], dtype=jnp.float64),
                )
            )
        )
        return _timed_jax_scalar(function, jnp.asarray(float(composition[0]), dtype=jnp.float64))
    if target in {"density_density", "density_strength", "strength_strength"}:
        function = jax.jit(
            jax.hessian(
                lambda pair: value(
                    pair[0],
                    pair[1],
                    jnp.asarray(composition, dtype=jnp.float64),
                )
            )
        )
        hessian, elapsed = _timed_jax_array(function, jnp.asarray([density, strength], dtype=jnp.float64))
        if target == "density_density":
            return float(hessian[0, 0]), elapsed
        if target == "density_strength":
            return float(hessian[0, 1]), elapsed
        return float(hessian[1, 1]), elapsed
    if target == "composition_composition":
        function = jax.jit(
            jax.hessian(
                lambda x0: value(
                    density,
                    strength,
                    jnp.asarray([x0, 1.0 - x0], dtype=jnp.float64),
                )
            )
        )
        return _timed_jax_scalar(function, jnp.asarray(float(composition[0]), dtype=jnp.float64))
    raise ValueError(f"Unknown JAX derivative target: {target}")


def _timed_jax_scalar(function, argument) -> tuple[float, float]:
    _block_until_ready(function(argument))
    start = time.perf_counter()
    result = _block_until_ready(function(argument))
    return float(result), time.perf_counter() - start


def _timed_jax_array(function, argument):
    _block_until_ready(function(argument))
    start = time.perf_counter()
    result = _block_until_ready(function(argument))
    return result, time.perf_counter() - start


def _block_until_ready(value):
    return value.block_until_ready()


def _jax_picard_association_value(
    density,
    strength,
    composition,
    site_component_index,
    active_pairs: tuple[tuple[int, int], ...],
    site_count: int,
):
    x_assoc = composition[site_component_index]
    delta = jnp.zeros((site_count, site_count), dtype=jnp.float64)
    for i, j in active_pairs:
        delta = delta.at[i, j].set(strength)
    strengths = density * jnp.sum(delta * x_assoc[jnp.newaxis, :], axis=1)
    xa = 2.0 / (1.0 + jnp.sqrt(1.0 + 4.0 * strengths))
    for _ in range(7):
        proposal = 1.0 / (1.0 + density * (delta @ (x_assoc * xa)))
        xa = 0.5 * xa + 0.5 * proposal
    xa = jnp.clip(xa, 1.0e-14, 1.0)
    weights = composition[site_component_index]
    terms = jnp.log(xa) - 0.5 * xa + 0.5
    return jnp.sum(weights * terms)


def _exact_value(
    target: str,
    *,
    system: AssociationSystem,
    density: float,
    strength: float,
    composition: np.ndarray,
) -> float:
    delta = system.delta_matrix(strength)
    if target == "density":
        return exact_density_sensitivity(
            system=system,
            density=density,
            composition=composition,
            delta=delta,
        ).da_dtheta
    if target == "strength":
        return exact_strength_sensitivity(
            system=system,
            density=density,
            composition=composition,
            delta=delta,
            strength=strength,
        ).da_dtheta
    if target == "composition":
        return exact_binary_composition_sensitivity(
            system=system,
            density=density,
            composition=composition,
            delta=delta,
        ).da_dtheta
    if target in {"density_density", "density_strength", "strength_strength", "composition_composition"}:
        return exact_hessian_target(
            target,
            system=system,
            density=density,
            strength=strength,
            composition=composition,
        )
    raise ValueError(f"Unknown exact derivative target: {target}")


def _exact_diagnostics(
    target: str,
    *,
    system: AssociationSystem,
    density: float,
    strength: float,
    composition: np.ndarray,
) -> ImplicitSensitivityResult:
    delta = system.delta_matrix(strength)
    if target in {"strength", "strength_strength"}:
        return exact_strength_sensitivity(
            system=system,
            density=density,
            composition=composition,
            delta=delta,
            strength=strength,
        )
    if target in {"composition", "composition_composition"}:
        return exact_binary_composition_sensitivity(
            system=system,
            density=density,
            composition=composition,
            delta=delta,
        )
    return exact_density_sensitivity(
        system=system,
        density=density,
        composition=composition,
        delta=delta,
    )


def _jax_cases() -> tuple[dict[str, object], ...]:
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
    parser = argparse.ArgumentParser(description="Generate JAX Picard derivative comparison diagnostics.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    print(generate_jax_picard_derivatives(args.output))


if __name__ == "__main__":
    main()
