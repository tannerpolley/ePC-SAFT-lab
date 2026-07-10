from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

import numpy as np

N_AV = 6.02214076e23


@dataclass(frozen=True)
class ToyPCSAFTState:
    temperature: float
    density: float
    composition: np.ndarray
    segments: np.ndarray
    sigma: np.ndarray
    epsilon_over_k: np.ndarray
    k_ij: np.ndarray

    def __post_init__(self) -> None:
        object.__setattr__(self, "composition", _as_vector("composition", self.composition))
        object.__setattr__(self, "segments", _as_vector("segments", self.segments))
        object.__setattr__(self, "sigma", _as_vector("sigma", self.sigma))
        object.__setattr__(self, "epsilon_over_k", _as_vector("epsilon_over_k", self.epsilon_over_k))
        object.__setattr__(self, "k_ij", np.asarray(self.k_ij, dtype=float))
        if not np.isfinite(self.temperature) or self.temperature <= 0.0:
            raise ValueError("temperature must be positive and finite.")
        if not np.isfinite(self.density) or self.density <= 0.0:
            raise ValueError("density must be positive and finite.")
        if not np.isclose(float(np.sum(self.composition)), 1.0):
            raise ValueError("composition must sum to one.")
        if np.any(self.composition < 0.0):
            raise ValueError("composition must be nonnegative.")
        if np.any(self.segments <= 0.0):
            raise ValueError("segments must be positive.")
        if np.any(self.sigma <= 0.0):
            raise ValueError("sigma must be positive.")
        if np.any(self.epsilon_over_k <= 0.0):
            raise ValueError("epsilon_over_k must be positive.")
        n = self.component_count
        for name, array in (
            ("segments", self.segments),
            ("sigma", self.sigma),
            ("epsilon_over_k", self.epsilon_over_k),
        ):
            if array.size != n:
                raise ValueError(f"{name} length must match composition length.")
        if self.k_ij.shape != (n, n):
            raise ValueError("k_ij must be square with shape (component_count, component_count).")
        if not np.all(np.isfinite(self.k_ij)):
            raise ValueError("k_ij must contain finite values.")

    @property
    def component_count(self) -> int:
        return int(self.composition.size)

    @property
    def number_density(self) -> float:
        return float(self.density * N_AV / 1.0e30)

    @property
    def m_bar(self) -> float:
        return float(np.dot(self.composition, self.segments))

    @property
    def segment_diameter(self) -> np.ndarray:
        return self.sigma * (1.0 - 0.12 * np.exp(-3.0 * self.epsilon_over_k / self.temperature))


def _as_vector(name: str, value: object) -> np.ndarray:
    array = np.asarray(value, dtype=float)
    if array.ndim != 1:
        raise ValueError(f"{name} must be one-dimensional.")
    if not np.all(np.isfinite(array)):
        raise ValueError(f"{name} must contain finite values.")
    return array


def state_from_config(
    config: Mapping[str, object],
    *,
    component_count: int,
    composition: np.ndarray,
) -> ToyPCSAFTState:
    segments = _as_vector("segments", config["segments"])
    if segments.size != component_count:
        raise ValueError("segments length must match component_count.")
    sigma = _as_vector("sigma", config["sigma"])
    if sigma.size != component_count:
        raise ValueError("sigma length must match component_count.")
    epsilon_over_k = _as_vector("epsilon_over_k", config["epsilon_over_k"])
    if epsilon_over_k.size != component_count:
        raise ValueError("epsilon_over_k length must match component_count.")
    default_kij = np.zeros((component_count, component_count), dtype=float)
    return ToyPCSAFTState(
        temperature=float(config["temperature"]),
        density=float(config["density"]),
        composition=np.asarray(composition, dtype=float),
        segments=segments,
        sigma=sigma,
        epsilon_over_k=epsilon_over_k,
        k_ij=np.asarray(config.get("k_ij", default_kij), dtype=float),
    )
