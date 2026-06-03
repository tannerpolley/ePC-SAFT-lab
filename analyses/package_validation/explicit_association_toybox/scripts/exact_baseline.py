from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .association_models import mass_action_residual


@dataclass(frozen=True)
class ExactAssociationResult:
    xa: np.ndarray
    converged: bool
    iteration_count: int
    update_norm: float
    residual_norm: float


def stable_two_class_2b_solution(*, density: float, x_assoc: float, delta_da: float) -> np.ndarray:
    c = density * x_assoc * delta_da
    if c < 0.0 or not np.isfinite(c):
        raise ValueError("2B strength must be finite and nonnegative.")
    value = 2.0 / (1.0 + np.sqrt(1.0 + 4.0 * c))
    return np.array([value, value], dtype=float)


def solve_exact_site_fractions(
    *,
    density: float,
    x_assoc: np.ndarray,
    delta: np.ndarray,
    max_iterations: int = 500,
    update_tolerance: float = 1.0e-14,
    residual_tolerance: float = 1.0e-10,
    relaxation_factor: float = 0.5,
) -> ExactAssociationResult:
    if density <= 0.0 or not np.isfinite(density):
        raise ValueError("density must be positive and finite.")
    if not 0.0 < relaxation_factor <= 1.0:
        raise ValueError("relaxation_factor must be in (0, 1].")
    x_assoc = np.asarray(x_assoc, dtype=float)
    delta = np.asarray(delta, dtype=float)
    if x_assoc.ndim != 1:
        raise ValueError("x_assoc must be one-dimensional.")
    if np.any(x_assoc < 0.0):
        raise ValueError("x_assoc must be nonnegative.")
    if delta.shape != (x_assoc.size, x_assoc.size):
        raise ValueError("delta must be square and match x_assoc.")

    xa_old = np.ones_like(x_assoc, dtype=float)
    update_norm = float("inf")
    residual_norm = float("inf")
    for iteration in range(1, max_iterations + 1):
        proposal = 1.0 / (1.0 + density * (delta @ (x_assoc * xa_old)))
        xa_new = (1.0 - relaxation_factor) * xa_old + relaxation_factor * proposal
        update_norm = float(np.max(np.abs(xa_new - xa_old)))
        residual = mass_action_residual(xa_new, density=density, x_assoc=x_assoc, delta=delta)
        residual_norm = float(np.linalg.norm(residual, ord=np.inf))
        if (
            update_norm <= update_tolerance
            and residual_norm <= residual_tolerance
            and np.all(xa_new > 0.0)
            and np.all(xa_new <= 1.0)
        ):
            return ExactAssociationResult(
                xa=xa_new,
                converged=True,
                iteration_count=iteration,
                update_norm=update_norm,
                residual_norm=residual_norm,
            )
        xa_old = xa_new

    raise RuntimeError(
        "association exact baseline solve did not converge; "
        f"iteration_count={max_iterations}; update_norm={update_norm}; residual_norm={residual_norm}"
    )
