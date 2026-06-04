from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .association_models import AssociationSystem
from .exact_baseline import stable_two_class_2b_solution

EXACT_MASS_ACTION_BASELINE = "implicit_exact_mass_action"
PICARD7_CLOSURE = "damped_picard_7_05"
CANDIDATE_CLOSURES = (PICARD7_CLOSURE,)


@dataclass(frozen=True)
class ClosureResult:
    name: str
    xa: np.ndarray
    association_model: str
    association_closure: str
    exact_derivative_of: str
    information_loss: str


def _bounded_site_fractions(xa: np.ndarray) -> np.ndarray:
    return np.clip(np.asarray(xa, dtype=float), 1.0e-14, 1.0)


def _row_sum_initializer(density: float, x_assoc: np.ndarray, delta: np.ndarray) -> np.ndarray:
    strengths = density * np.sum(delta * x_assoc[np.newaxis, :], axis=1)
    return _bounded_site_fractions(2.0 / (1.0 + np.sqrt(1.0 + 4.0 * strengths)))


def _picard(
    density: float,
    x_assoc: np.ndarray,
    delta: np.ndarray,
    *,
    steps: int,
    damping: float,
) -> np.ndarray:
    xa = _row_sum_initializer(density, x_assoc, delta)
    for _ in range(steps):
        proposal = 1.0 / (1.0 + density * (delta @ (x_assoc * xa)))
        xa = (1.0 - damping) * xa + damping * proposal
    return _bounded_site_fractions(xa)


def evaluate_closure(
    name: str,
    *,
    system: AssociationSystem,
    density: float,
    composition: np.ndarray,
    delta: np.ndarray,
) -> ClosureResult:
    x_assoc = system.x_assoc(composition)
    if name == "closure_2b_exact_reduction":
        if system.site_count != 2 or tuple(system.site_kind) != ("D", "A"):
            raise ValueError("closure_2b_exact_reduction requires a two-site D/A topology.")
        xa = stable_two_class_2b_solution(density=density, x_assoc=x_assoc[0], delta_da=delta[0, 1])
        return ClosureResult(
            name=name,
            xa=xa,
            association_model="implicit_exact",
            association_closure=name,
            exact_derivative_of="exact_mass_action",
            information_loss="none",
        )
    if name != PICARD7_CLOSURE:
        raise ValueError(f"Unknown association closure: {name}")
    xa = _picard(density, x_assoc, delta, steps=7, damping=0.5)
    return ClosureResult(
        name=name,
        xa=xa,
        association_model="explicit_approx",
        association_closure=name,
        exact_derivative_of="approximate_association_closure",
        information_loss="none",
    )
