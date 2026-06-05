from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .association_models import AssociationSystem, association_helmholtz, mass_action_residual
from .exact_baseline import solve_exact_site_fractions


@dataclass(frozen=True)
class ImplicitSensitivityResult:
    xa: np.ndarray
    a_assoc: float
    dxa_dtheta: np.ndarray
    da_dtheta: float
    jacobian: np.ndarray
    jacobian_condition_number: float
    mass_action_residual_inf: float


def mass_action_jacobian(*, xa: np.ndarray, density: float, x_assoc: np.ndarray, delta: np.ndarray) -> np.ndarray:
    xa = _as_vector("xa", xa)
    x_assoc = _as_vector("x_assoc", x_assoc)
    delta = np.asarray(delta, dtype=float)
    if delta.shape != (xa.size, xa.size):
        raise ValueError("delta must be square and match xa.")
    if x_assoc.shape != xa.shape:
        raise ValueError("x_assoc must match xa.")
    if density <= 0.0 or not np.isfinite(density):
        raise ValueError("density must be positive and finite.")

    coupling = delta @ (x_assoc * xa)
    main_entries = 1.0 + density * coupling
    jacobian = np.diag(main_entries)
    jacobian += density * xa[:, np.newaxis] * delta * x_assoc[np.newaxis, :]
    return jacobian


def exact_density_sensitivity(
    *,
    system: AssociationSystem,
    density: float,
    composition: np.ndarray,
    delta: np.ndarray,
) -> ImplicitSensitivityResult:
    return exact_parameter_sensitivity(
        system=system,
        density=density,
        composition=composition,
        delta=delta,
        parameter_rhs=_density_rhs,
        association_weight_derivative=np.zeros(system.site_count, dtype=float),
    )


def exact_strength_sensitivity(
    *,
    system: AssociationSystem,
    density: float,
    composition: np.ndarray,
    delta: np.ndarray,
    strength: float,
) -> ImplicitSensitivityResult:
    if strength <= 0.0 or not np.isfinite(strength):
        raise ValueError("strength must be positive and finite.")
    delta_derivative = np.asarray(delta, dtype=float) / strength
    return exact_parameter_sensitivity(
        system=system,
        density=density,
        composition=composition,
        delta=delta,
        parameter_rhs=lambda *, xa, density, x_assoc, delta: _delta_rhs(
            xa=xa,
            density=density,
            x_assoc=x_assoc,
            delta_derivative=delta_derivative,
        ),
        association_weight_derivative=np.zeros(system.site_count, dtype=float),
    )


def exact_binary_composition_sensitivity(
    *,
    system: AssociationSystem,
    density: float,
    composition: np.ndarray,
    delta: np.ndarray,
) -> ImplicitSensitivityResult:
    composition = _as_vector("composition", composition)
    if system.component_count != 2 or composition.shape != (2,):
        raise ValueError("composition sensitivity currently requires a binary AssociationSystem.")
    dx_assoc = np.where(system.site_component_index == 0, 1.0, -1.0)
    return exact_parameter_sensitivity(
        system=system,
        density=density,
        composition=composition,
        delta=delta,
        parameter_rhs=lambda *, xa, density, x_assoc, delta: _x_assoc_rhs(
            xa=xa,
            density=density,
            delta=delta,
            dx_assoc=dx_assoc,
        ),
        association_weight_derivative=dx_assoc,
    )


def exact_parameter_sensitivity(
    *,
    system: AssociationSystem,
    density: float,
    composition: np.ndarray,
    delta: np.ndarray,
    parameter_rhs,
    association_weight_derivative: np.ndarray,
) -> ImplicitSensitivityResult:
    composition = _as_vector("composition", composition)
    x_assoc = system.x_assoc(composition)
    exact = solve_exact_site_fractions(density=density, x_assoc=x_assoc, delta=delta)
    xa = exact.xa
    jacobian = mass_action_jacobian(xa=xa, density=density, x_assoc=x_assoc, delta=delta)
    rhs = parameter_rhs(xa=xa, density=density, x_assoc=x_assoc, delta=delta)
    dxa = -np.linalg.solve(jacobian, rhs)
    weight_derivative = _as_vector("association_weight_derivative", association_weight_derivative)
    if weight_derivative.shape != xa.shape:
        raise ValueError("association_weight_derivative must match xa.")
    weights = composition[system.site_component_index]
    site_terms = np.log(xa) - 0.5 * xa + 0.5
    da = float(np.dot(weight_derivative, site_terms) + np.dot(weights * (1.0 / xa - 0.5), dxa))
    residual = mass_action_residual(xa, density=density, x_assoc=x_assoc, delta=delta)
    return ImplicitSensitivityResult(
        xa=xa,
        a_assoc=association_helmholtz(xa, composition, system.site_component_index),
        dxa_dtheta=dxa,
        da_dtheta=da,
        jacobian=jacobian,
        jacobian_condition_number=float(np.linalg.cond(jacobian)),
        mass_action_residual_inf=float(np.linalg.norm(residual, ord=np.inf)),
    )


def _density_rhs(*, xa: np.ndarray, density: float, x_assoc: np.ndarray, delta: np.ndarray) -> np.ndarray:
    return xa * (delta @ (x_assoc * xa))


def _delta_rhs(
    *,
    xa: np.ndarray,
    density: float,
    x_assoc: np.ndarray,
    delta_derivative: np.ndarray,
) -> np.ndarray:
    return density * xa * (delta_derivative @ (x_assoc * xa))


def _x_assoc_rhs(*, xa: np.ndarray, density: float, delta: np.ndarray, dx_assoc: np.ndarray) -> np.ndarray:
    return density * xa * (delta @ (dx_assoc * xa))


def _as_vector(name: str, value: object) -> np.ndarray:
    array = np.asarray(value, dtype=float)
    if array.ndim != 1:
        raise ValueError(f"{name} must be one-dimensional.")
    if not np.all(np.isfinite(array)):
        raise ValueError(f"{name} must contain finite values.")
    return array
