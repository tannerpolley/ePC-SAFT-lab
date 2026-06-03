from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class AssociationSystem:
    component_count: int
    site_component_index: np.ndarray
    site_kind: tuple[str, ...]
    active_pairs: tuple[tuple[int, int], ...]

    def __post_init__(self) -> None:
        if self.site_component_index.ndim != 1:
            raise ValueError("site_component_index must be one-dimensional.")
        if self.component_count <= 0:
            raise ValueError("component_count must be positive.")
        if len(self.site_kind) != self.site_component_index.size:
            raise ValueError("site_kind length must match site count.")
        if np.any(self.site_component_index < 0) or np.any(self.site_component_index >= self.component_count):
            raise ValueError("site_component_index contains an invalid component index.")
        for i, j in self.active_pairs:
            if i < 0 or j < 0 or i >= self.site_count or j >= self.site_count:
                raise ValueError("active_pairs contains an invalid site index.")

    @property
    def site_count(self) -> int:
        return int(self.site_component_index.size)

    def x_assoc(self, composition: np.ndarray) -> np.ndarray:
        composition = np.asarray(composition, dtype=float)
        if composition.shape != (self.component_count,):
            raise ValueError("composition length must match component_count.")
        if not np.isclose(float(np.sum(composition)), 1.0):
            raise ValueError("composition must sum to one.")
        if np.any(composition < 0.0):
            raise ValueError("composition must be nonnegative.")
        return composition[self.site_component_index]

    def delta_matrix(self, strength: float) -> np.ndarray:
        if not np.isfinite(strength) or strength < 0.0:
            raise ValueError("strength must be finite and nonnegative.")
        delta = np.zeros((self.site_count, self.site_count), dtype=float)
        for i, j in self.active_pairs:
            delta[i, j] = float(strength)
        return delta


def mass_action_residual(
    xa: np.ndarray,
    *,
    density: float,
    x_assoc: np.ndarray,
    delta: np.ndarray,
) -> np.ndarray:
    xa = np.asarray(xa, dtype=float)
    x_assoc = np.asarray(x_assoc, dtype=float)
    delta = np.asarray(delta, dtype=float)
    if xa.ndim != 1:
        raise ValueError("xa must be one-dimensional.")
    if x_assoc.shape != xa.shape:
        raise ValueError("x_assoc must match xa.")
    if delta.shape != (xa.size, xa.size):
        raise ValueError("delta must be a square matrix matching xa.")
    if not np.isfinite(density) or density < 0.0:
        raise ValueError("density must be finite and nonnegative.")
    return xa * (1.0 + density * (delta @ (x_assoc * xa))) - 1.0


def association_helmholtz(
    xa: np.ndarray,
    composition: np.ndarray,
    site_component_index: np.ndarray,
) -> float:
    xa = np.asarray(xa, dtype=float)
    composition = np.asarray(composition, dtype=float)
    site_component_index = np.asarray(site_component_index, dtype=int)
    if xa.ndim != 1:
        raise ValueError("xa must be one-dimensional.")
    if site_component_index.shape != xa.shape:
        raise ValueError("site_component_index must match xa.")
    if np.any(xa <= 0.0):
        raise ValueError("site fractions must be positive for association Helmholtz evaluation.")
    terms = np.log(xa) - 0.5 * xa + 0.5
    weights = composition[site_component_index]
    return float(np.sum(weights * terms))
