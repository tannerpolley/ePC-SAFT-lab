from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .association_models import AssociationSystem, mass_action_residual
from .exact_baseline import stable_two_class_2b_solution


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


def _diagonal_polish(
    xa: np.ndarray,
    density: float,
    x_assoc: np.ndarray,
    delta: np.ndarray,
    *,
    damping: float,
) -> np.ndarray:
    residual = mass_action_residual(xa, density=density, x_assoc=x_assoc, delta=delta)
    interaction = density * (delta @ (x_assoc * xa))
    diagonal = 1.0 + interaction + xa * density * np.diag(delta) * x_assoc
    return _bounded_site_fractions(xa - damping * residual / diagonal)


def _collapsed_mean_field(
    system: AssociationSystem,
    density: float,
    composition: np.ndarray,
    delta: np.ndarray,
) -> np.ndarray:
    donor_mask = np.array([kind == "D" for kind in system.site_kind], dtype=bool)
    acceptor_mask = np.array([kind == "A" for kind in system.site_kind], dtype=bool)
    x_assoc = system.x_assoc(composition)
    donor_total = float(np.sum(x_assoc[donor_mask]))
    acceptor_total = float(np.sum(x_assoc[acceptor_mask]))
    if donor_total <= 0.0 or acceptor_total <= 0.0:
        return np.ones(system.site_count, dtype=float)
    weighted = (
        delta[np.ix_(donor_mask, acceptor_mask)]
        * x_assoc[donor_mask][:, np.newaxis]
        * x_assoc[acceptor_mask][np.newaxis, :]
    )
    delta_eff = float(np.sum(weighted) / (donor_total * acceptor_total))
    donor_acceptor = stable_two_class_2b_solution(density=density, x_assoc=1.0, delta_da=delta_eff)
    xa = np.ones(system.site_count, dtype=float)
    xa[donor_mask] = donor_acceptor[0]
    xa[acceptor_mask] = donor_acceptor[1]
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
    if name == "explicit_picard_unroll_1":
        xa = _picard(density, x_assoc, delta, steps=1, damping=1.0)
    elif name == "explicit_damped_picard_unroll_3":
        xa = _picard(density, x_assoc, delta, steps=3, damping=0.5)
    elif name == "explicit_damped_picard_unroll_5":
        xa = _picard(density, x_assoc, delta, steps=5, damping=0.5)
    elif name == "explicit_picard3_diag_newton1":
        xa = _picard(density, x_assoc, delta, steps=3, damping=0.5)
        xa = _diagonal_polish(xa, density, x_assoc, delta, damping=0.5)
    elif name == "collapsed_donor_acceptor_mean_field":
        xa = _collapsed_mean_field(system, density, composition, delta)
    else:
        raise ValueError(f"Unknown association closure: {name}")
    return ClosureResult(
        name=name,
        xa=xa,
        association_model="explicit_approx",
        association_closure=name,
        exact_derivative_of="approximate_association_closure",
        information_loss="closure_specific" if name == "collapsed_donor_acceptor_mean_field" else "none",
    )
