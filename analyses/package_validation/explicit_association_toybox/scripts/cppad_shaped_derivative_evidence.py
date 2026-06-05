from __future__ import annotations

import argparse
import json
import subprocess
from functools import lru_cache
from pathlib import Path
from typing import Callable, Mapping

import numpy as np

from .association_case_matrix import AssociationEvidenceCase, association_case_by_id
from .association_models import association_helmholtz, mass_action_residual
from .closure_models import PICARD7_CLOSURE, evaluate_closure
from .derivative_agreement import centered_slope
from .exact_baseline import solve_exact_site_fractions
from .propagation_evidence import relative_error, write_rows_csv

ANALYSIS_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = ANALYSIS_ROOT.parents[2]
DEFAULT_OUTPUT = (
    ANALYSIS_ROOT
    / "figures"
    / "cppad_shaped_picard_derivative_evidence"
    / "output"
    / "cppad_shaped_picard_derivative_evidence.csv"
)
BACKEND_MODULE = "analyses.package_validation.explicit_association_toybox.scripts.cppad_shaped_jax_backend"


def run_cppad_shaped_derivative_evidence() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for jax_row in _jax_derivative_rows():
        case = association_case_by_id(str(jax_row["case_id"]))
        rows.append(_comparison_row(case, jax_row))
    return rows


def generate_cppad_shaped_derivative_evidence(output_path: Path = DEFAULT_OUTPUT) -> Path:
    return write_rows_csv(run_cppad_shaped_derivative_evidence(), output_path)


def _comparison_row(case: AssociationEvidenceCase, jax_row: Mapping[str, object]) -> dict[str, object]:
    target = str(jax_row["target"])
    density = float(case.density_grid[len(case.density_grid) // 2])
    strength = float(case.strength_scale)
    exact_value = _target_value(case, target=target, density=density, strength_scale=strength, exact=True)
    picard_numpy = _target_value(case, target=target, density=density, strength_scale=strength, exact=False)
    picard_jax = float(jax_row["picard_jax_value"])
    rel = relative_error(picard_jax, exact_value)
    return {
        "case_id": case.case_id,
        "topology_id": case.topology_id,
        "target": target,
        "variable_block": str(jax_row["variable_block"]),
        "derivative_order": int(jax_row["derivative_order"]),
        "backend": "jax_proxy_for_cppad_shape",
        "exact_implicit_value": exact_value,
        "picard_numpy_value": picard_numpy,
        "picard_jax_value": picard_jax,
        "absolute_error": abs(picard_jax - exact_value),
        "relative_error": rel,
        "finite_difference_step": _step_for_target(target, density=density, strength_scale=strength),
        "autodiff_status": str(jax_row["autodiff_status"]),
        "cppad_relevance_note": str(jax_row["cppad_relevance_note"]),
        "admission_band": _admission_band(rel),
        "baseline_status": _baseline_status(target),
        "mass_action_residual_norm": _exact_residual(case, density=density, strength_scale=strength),
        "diagnostic_scope": "python_toybox_cppad_shaped_derivative_evidence",
    }


def _target_value(
    case: AssociationEvidenceCase,
    *,
    target: str,
    density: float,
    strength_scale: float,
    exact: bool,
) -> float:
    if target == "a_assoc_density":
        return centered_slope(
            lambda rho: _association_value(case, density=rho, strength_scale=strength_scale, exact=exact),
            base_value=density,
            step_size=_density_step(density),
        )
    if target == "a_assoc_strength":
        return centered_slope(
            lambda scale: _association_value(case, density=density, strength_scale=max(scale, 1.0e-12), exact=exact),
            base_value=strength_scale,
            step_size=_strength_step(strength_scale),
        )
    if target == "pressure_proxy_density":
        return centered_slope(
            lambda rho: _pressure_proxy(case, density=rho, strength_scale=strength_scale, exact=exact),
            base_value=density,
            step_size=_density_step(density),
        )
    if target == "a_assoc_density_density":
        return _second_derivative(
            lambda rho: _association_value(case, density=rho, strength_scale=strength_scale, exact=exact),
            base_value=density,
            step_size=_density_step(density),
        )
    if target == "a_assoc_density_strength":
        return _mixed_derivative(
            lambda rho, scale: _association_value(case, density=rho, strength_scale=max(scale, 1.0e-12), exact=exact),
            density=density,
            strength_scale=strength_scale,
        )
    if target == "a_assoc_strength_strength":
        return _second_derivative(
            lambda scale: _association_value(case, density=density, strength_scale=max(scale, 1.0e-12), exact=exact),
            base_value=strength_scale,
            step_size=_strength_step(strength_scale),
        )
    if target == "a_assoc_composition_0":
        return centered_slope(
            lambda x0: _association_value(
                case,
                density=density,
                strength_scale=strength_scale,
                exact=exact,
                composition=np.array([x0, 1.0 - x0], dtype=float),
            ),
            base_value=float(case.composition[0]),
            step_size=_composition_step(),
        )
    if target == "fugacity_proxy_composition_0":
        return centered_slope(
            lambda x0: _fugacity_proxy(
                _association_value(
                    case,
                    density=density,
                    strength_scale=strength_scale,
                    exact=exact,
                    composition=np.array([x0, 1.0 - x0], dtype=float),
                )
            ),
            base_value=float(case.composition[0]),
            step_size=_composition_step(),
        )
    if target == "a_assoc_composition_0_0":
        return _second_derivative(
            lambda x0: _association_value(
                case,
                density=density,
                strength_scale=strength_scale,
                exact=exact,
                composition=np.array([x0, 1.0 - x0], dtype=float),
            ),
            base_value=float(case.composition[0]),
            step_size=_composition_step(),
        )
    if target == "local_quadratic_prediction":
        return _local_quadratic_prediction(case, density=density, strength_scale=strength_scale, exact=exact)
    raise ValueError(f"Unknown CppAD-shaped derivative target: {target}")


def _association_value(
    case: AssociationEvidenceCase,
    *,
    density: float,
    strength_scale: float,
    exact: bool,
    composition: np.ndarray | None = None,
) -> float:
    if case.system is None:
        return 0.0
    composition = np.asarray(composition if composition is not None else case.composition, dtype=float)
    delta = case.scaled_delta(strength_scale)
    if exact:
        solved = solve_exact_site_fractions(
            density=density,
            x_assoc=case.system.x_assoc(composition),
            delta=delta,
        )
        xa = solved.xa
    else:
        xa = evaluate_closure(
            PICARD7_CLOSURE,
            system=case.system,
            density=density,
            composition=composition,
            delta=delta,
        ).xa
    return association_helmholtz(xa, composition, case.system.site_component_index)


def _pressure_proxy(
    case: AssociationEvidenceCase,
    *,
    density: float,
    strength_scale: float,
    exact: bool,
) -> float:
    ares = _association_value(case, density=density, strength_scale=strength_scale, exact=exact)
    slope = centered_slope(
        lambda rho: _association_value(case, density=rho, strength_scale=strength_scale, exact=exact),
        base_value=density,
        step_size=_density_step(density),
    )
    return float(density * (1.0 + ares) + density * density * slope)


def _local_quadratic_prediction(
    case: AssociationEvidenceCase,
    *,
    density: float,
    strength_scale: float,
    exact: bool,
) -> float:
    def f(rho: float, scale: float) -> float:
        return _association_value(case, density=rho, strength_scale=max(scale, 1.0e-12), exact=exact)

    base = f(density, strength_scale)
    grad = np.array(
        [
            centered_slope(lambda rho: f(rho, strength_scale), base_value=density, step_size=_density_step(density)),
            centered_slope(
                lambda scale: f(density, scale),
                base_value=strength_scale,
                step_size=_strength_step(strength_scale),
            ),
        ],
        dtype=float,
    )
    hessian = np.array(
        [
            [
                _second_derivative(lambda rho: f(rho, strength_scale), base_value=density, step_size=_density_step(density)),
                _mixed_derivative(f, density=density, strength_scale=strength_scale),
            ],
            [
                _mixed_derivative(f, density=density, strength_scale=strength_scale),
                _second_derivative(
                    lambda scale: f(density, scale),
                    base_value=strength_scale,
                    step_size=_strength_step(strength_scale),
                ),
            ],
        ],
        dtype=float,
    )
    step = np.array([0.05 * density, 0.03 * strength_scale], dtype=float)
    return float(base + np.dot(grad, step) + 0.5 * step @ hessian @ step)


def _second_derivative(function: Callable[[float], float], *, base_value: float, step_size: float) -> float:
    high = function(base_value + step_size)
    mid = function(base_value)
    low = function(base_value - step_size)
    return float((high - 2.0 * mid + low) / (step_size * step_size))


def _mixed_derivative(function: Callable[[float, float], float], *, density: float, strength_scale: float) -> float:
    h = _density_step(density)
    k = _strength_step(strength_scale)
    return float(
        (
            function(density + h, strength_scale + k)
            - function(density + h, strength_scale - k)
            - function(density - h, strength_scale + k)
            + function(density - h, strength_scale - k)
        )
        / (4.0 * h * k)
    )


def _exact_residual(case: AssociationEvidenceCase, *, density: float, strength_scale: float) -> float:
    if case.system is None:
        return 0.0
    delta = case.scaled_delta(strength_scale)
    exact = solve_exact_site_fractions(
        density=density,
        x_assoc=case.system.x_assoc(case.composition),
        delta=delta,
    )
    residual = mass_action_residual(
        exact.xa,
        density=density,
        x_assoc=case.system.x_assoc(case.composition),
        delta=delta,
    )
    return float(np.linalg.norm(residual, ord=np.inf))


def _fugacity_proxy(value: float) -> float:
    return float(np.exp(np.clip(value, -50.0, 50.0)))


def _density_step(density: float) -> float:
    return max(1.0e-5, abs(density) * 1.0e-4)


def _strength_step(strength_scale: float) -> float:
    return max(1.0e-4, abs(strength_scale) * 1.0e-4)


def _composition_step() -> float:
    return 1.0e-5


def _step_for_target(target: str, *, density: float, strength_scale: float) -> str:
    if "density_strength" in target or target == "local_quadratic_prediction":
        return f"{_density_step(density):.12g};{_strength_step(strength_scale):.12g}"
    if "density" in target or "pressure" in target:
        return f"{_density_step(density):.12g}"
    if "strength" in target:
        return f"{_strength_step(strength_scale):.12g}"
    if "composition" in target or "fugacity" in target:
        return f"{_composition_step():.12g}"
    return ""


def _baseline_status(target: str) -> str:
    if target == "local_quadratic_prediction":
        return "centered_finite_difference_exact_implicit_local_quadratic"
    if target.endswith("_density") or target.endswith("_strength") or target.endswith("_composition_0"):
        return "centered_finite_difference_exact_implicit_first_derivative"
    return "centered_finite_difference_exact_implicit_second_derivative"


def _admission_band(relative: float) -> str:
    if relative <= 1.0e-4:
        return "candidate_accuracy"
    if relative <= 1.0e-2:
        return "needs_more_evidence"
    return "fails_derivative_gate"


@lru_cache(maxsize=1)
def _jax_derivative_rows() -> tuple[dict[str, object], ...]:
    completed = subprocess.run(
        ["uv", "run", "--group", "autodiff", "python", "-m", BACKEND_MODULE, "--mode", "derivative"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    stdout = completed.stdout.strip()
    if not stdout:
        raise RuntimeError("JAX derivative backend emitted no rows.")
    return tuple(json.loads(stdout))


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate CppAD-shaped Picard derivative evidence.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    print(generate_cppad_shaped_derivative_evidence(args.output))


if __name__ == "__main__":
    main()
