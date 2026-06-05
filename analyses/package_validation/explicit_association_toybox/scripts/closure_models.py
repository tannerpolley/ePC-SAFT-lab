from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .association_models import AssociationSystem
from .exact_baseline import stable_two_class_2b_solution

EXACT_MASS_ACTION_BASELINE = "implicit_exact_mass_action"
EXACT_2B_REDUCTION = "exact_2b_reduction"
PICARD7_CLOSURE = "damped_picard_7_05"
CANDIDATE_CLOSURES = (PICARD7_CLOSURE,)
PICARD_STEP_COUNTS = (3, 5, 7, 9, 11)
PICARD_DAMPING_VALUES = (0.35, 0.5, 0.65, 0.8, 1.0)


@dataclass(frozen=True)
class ClosureResult:
    name: str
    xa: np.ndarray
    association_model: str
    association_closure: str
    exact_derivative_of: str
    information_loss: str


@dataclass(frozen=True)
class PicardPolicy:
    step_count: int
    damping: float

    def __post_init__(self) -> None:
        if self.step_count <= 0:
            raise ValueError("Picard step_count must be positive.")
        if self.damping <= 0.0 or self.damping > 1.0:
            raise ValueError("Picard damping must be in (0, 1].")

    @property
    def closure_name(self) -> str:
        if self.step_count == 7 and self.damping == 0.5:
            return PICARD7_CLOSURE
        damping_text = f"{self.damping:.2f}".rstrip("0").rstrip(".").replace(".", "p")
        return f"picard_n{self.step_count}_lambda{damping_text}"


PICARD_DEFAULT_POLICY = PicardPolicy(step_count=7, damping=0.5)
PICARD_POLICY_GRID = tuple(
    PicardPolicy(step_count=step_count, damping=damping)
    for step_count in PICARD_STEP_COUNTS
    for damping in PICARD_DAMPING_VALUES
)


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
    if name == EXACT_2B_REDUCTION:
        if system.site_count != 2 or tuple(system.site_kind) != ("D", "A"):
            raise ValueError("exact_2b_reduction requires a two-site D/A topology.")
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
    return evaluate_picard_policy(
        PICARD_DEFAULT_POLICY,
        system=system,
        density=density,
        composition=composition,
        delta=delta,
    )


def evaluate_picard_policy(
    policy: PicardPolicy,
    *,
    system: AssociationSystem,
    density: float,
    composition: np.ndarray,
    delta: np.ndarray,
) -> ClosureResult:
    x_assoc = system.x_assoc(composition)
    xa = _picard(density, x_assoc, delta, steps=policy.step_count, damping=policy.damping)
    return ClosureResult(
        name=policy.closure_name,
        xa=xa,
        association_model="explicit_approx",
        association_closure=policy.closure_name,
        exact_derivative_of="approximate_association_closure",
        information_loss="none",
    )
