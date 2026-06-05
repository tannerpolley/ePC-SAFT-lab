from __future__ import annotations

import argparse
import json

import jax
import jax.numpy as jnp
import numpy as np

from .association_case_matrix import AssociationEvidenceCase, jax_supported_cases

jax.config.update("jax_enable_x64", True)


def jax_property_rows() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for case in jax_supported_cases():
        for density in case.density_grid:
            rows.append(
                {
                    "case_id": case.case_id,
                    "density": float(density),
                    "picard_jax_value": _jax_value(case, density=float(density), strength_scale=case.strength_scale),
                    "autodiff_status": "jax_x64",
                    "cppad_relevance_note": "fixed_graph_differentiability_proxy",
                }
            )
    return rows


def jax_derivative_rows() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for case in jax_supported_cases():
        density = float(case.density_grid[len(case.density_grid) // 2])
        strength = float(case.strength_scale)
        rows.extend(_case_derivative_rows(case, density=density, strength_scale=strength))
    return rows


def _case_derivative_rows(
    case: AssociationEvidenceCase,
    *,
    density: float,
    strength_scale: float,
) -> list[dict[str, object]]:
    composition = jnp.asarray(case.composition, dtype=jnp.float64)
    base_pair = jnp.asarray([density, strength_scale], dtype=jnp.float64)

    def value_pair(pair):
        return _picard_association_scalar(case, pair[0], pair[1], composition)

    gradient_pair = jax.grad(value_pair)(base_pair)
    hessian_pair = jax.hessian(value_pair)(base_pair)
    rows = [
        _row(case, "a_assoc_density", "density", 1, float(gradient_pair[0])),
        _row(case, "a_assoc_strength", "association_strength_scale", 1, float(gradient_pair[1])),
        _row(
            case,
            "pressure_proxy_density",
            "density",
            1,
            _pressure_proxy_density_derivative(case, density=density, strength_scale=strength_scale, composition=composition),
        ),
        _row(case, "a_assoc_density_density", "density", 2, float(hessian_pair[0, 0])),
        _row(case, "a_assoc_density_strength", "density,association_strength_scale", 2, float(hessian_pair[0, 1])),
        _row(case, "a_assoc_strength_strength", "association_strength_scale", 2, float(hessian_pair[1, 1])),
    ]
    rows.append(
        _row(
            case,
            "local_quadratic_prediction",
            "density,association_strength_scale",
            2,
            _quadratic_prediction(value_pair, base_pair, gradient_pair, hessian_pair),
        )
    )
    if case.component_count == 2:
        x0 = jnp.asarray(float(case.composition[0]), dtype=jnp.float64)

        def value_composition(x_value):
            comp = jnp.asarray([x_value, 1.0 - x_value], dtype=jnp.float64)
            return _picard_association_scalar(case, density, strength_scale, comp)

        rows.append(
            _row(
                case,
                "a_assoc_composition_0",
                "composition_component_0",
                1,
                float(jax.grad(value_composition)(x0)),
            )
        )
        rows.append(
            _row(
                case,
                "fugacity_proxy_composition_0",
                "composition_component_0",
                1,
                float(jax.grad(lambda value: jnp.exp(jnp.clip(value_composition(value), -50.0, 50.0)))(x0)),
            )
        )
        rows.append(
            _row(
                case,
                "a_assoc_composition_0_0",
                "composition_component_0",
                2,
                float(jax.hessian(value_composition)(x0)),
            )
        )
    return rows


def _row(
    case: AssociationEvidenceCase,
    target: str,
    variable_block: str,
    derivative_order: int,
    value: float,
) -> dict[str, object]:
    return {
        "case_id": case.case_id,
        "topology_id": case.topology_id,
        "target": target,
        "variable_block": variable_block,
        "derivative_order": derivative_order,
        "picard_jax_value": float(value),
        "autodiff_status": "jax_x64",
        "cppad_relevance_note": "fixed_graph_differentiability_proxy",
    }


def _quadratic_prediction(value_pair, base_pair, gradient_pair, hessian_pair) -> float:
    step = jnp.asarray([0.05 * base_pair[0], 0.03 * base_pair[1]], dtype=jnp.float64)
    return float(value_pair(base_pair) + jnp.dot(gradient_pair, step) + 0.5 * step @ hessian_pair @ step)


def _pressure_proxy_density_derivative(
    case: AssociationEvidenceCase,
    *,
    density: float,
    strength_scale: float,
    composition,
) -> float:
    def assoc(rho):
        return _picard_association_scalar(case, rho, strength_scale, composition)

    def pressure_proxy(rho):
        ares = assoc(rho)
        da_drho = jax.grad(assoc)(rho)
        return rho * (1.0 + ares) + rho * rho * da_drho

    return float(jax.grad(pressure_proxy)(jnp.asarray(density, dtype=jnp.float64)))


def _jax_value(case: AssociationEvidenceCase, *, density: float, strength_scale: float) -> float:
    return float(
        _picard_association_scalar(
            case,
            jnp.asarray(density, dtype=jnp.float64),
            jnp.asarray(strength_scale, dtype=jnp.float64),
            jnp.asarray(case.composition, dtype=jnp.float64),
        )
    )


def _picard_association_scalar(
    case: AssociationEvidenceCase,
    density,
    strength_scale,
    composition,
):
    if case.system is None:
        return jnp.asarray(0.0, dtype=jnp.float64)
    site_component_index = jnp.asarray(tuple(int(value) for value in case.system.site_component_index), dtype=jnp.int32)
    delta = jnp.asarray(case.delta_matrix, dtype=jnp.float64)
    if case.strength_scale > 0.0:
        delta = delta * strength_scale / float(case.strength_scale)
    x_assoc = composition[site_component_index]
    strengths = density * jnp.sum(delta * x_assoc[jnp.newaxis, :], axis=1)
    xa = 2.0 / (1.0 + jnp.sqrt(1.0 + 4.0 * strengths))
    for _ in range(7):
        proposal = 1.0 / (1.0 + density * (delta @ (x_assoc * xa)))
        xa = 0.5 * xa + 0.5 * proposal
    xa = jnp.clip(xa, 1.0e-14, 1.0)
    terms = jnp.log(xa) - 0.5 * xa + 0.5
    return jnp.sum(composition[site_component_index] * terms)


def main() -> None:
    parser = argparse.ArgumentParser(description="Emit JAX rows for CppAD-shaped Picard toybox evidence.")
    parser.add_argument("--mode", choices=("property", "derivative"), required=True)
    args = parser.parse_args()
    rows = jax_property_rows() if args.mode == "property" else jax_derivative_rows()
    print(json.dumps(rows))


if __name__ == "__main__":
    main()
