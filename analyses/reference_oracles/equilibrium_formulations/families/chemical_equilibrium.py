"""Extensive manufactured standalone chemical-equilibrium formulations."""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

from analyses.reference_oracles.equilibrium_formulations.kernel import (
    BoxDomain,
    Certificate,
    DirectAdapter,
    DirectProblem,
    FormulationDescriptor,
    NumericalKind,
)


@dataclass(frozen=True)
class ChemicalEquilibriumAdapter(DirectAdapter):
    target_extent: float = 0.75
    reaction_vector: tuple[float, float] = (-1.0, 1.0)
    inventory_scale: float = 1.0
    boundary_target: float | None = None

    def __post_init__(self) -> None:
        if not np.isfinite(self.target_extent) or not 0.0 < self.target_extent < 1.0:
            raise ValueError("target_extent must lie strictly inside (0, 1)")
        if not np.isfinite(self.inventory_scale) or self.inventory_scale <= 0.0:
            raise ValueError("inventory_scale must be finite and positive")
        reaction = np.asarray(self.reaction_vector, dtype=float)
        if reaction.shape != (2,) or not np.all(np.isfinite(reaction)):
            raise ValueError("reaction_vector must contain two finite entries")
        if abs(float(np.sum(reaction))) > 1.0e-12:
            raise ValueError("reaction vector must conserve the declared element")
        if np.linalg.matrix_rank(reaction.reshape(2, 1)) != 1:
            raise ValueError("reaction basis must be complete for the elemental null space")
        if self.boundary_target is not None:
            if not np.isfinite(self.boundary_target) or 0.0 <= self.boundary_target <= 1.0:
                raise ValueError("boundary_target must be finite and outside [0, 1]")

    @property
    def descriptor(self) -> FormulationDescriptor:
        suffix = "boundary" if self.boundary_target is not None else "ideal-interior"
        return FormulationDescriptor(
            f"standalone-ce.{suffix}.manufactured.v1",
            "standalone chemical equilibrium",
            NumericalKind.DIRECT_MINIMIZATION,
        )

    @property
    def element_matrix(self) -> np.ndarray:
        return np.asarray([[1.0, 1.0]])

    @property
    def stoichiometric_matrix(self) -> np.ndarray:
        return np.asarray(self.reaction_vector, dtype=float).reshape(2, 1)

    @property
    def reference_composition(self) -> float:
        if self.boundary_target is None:
            return self.target_extent
        return float(np.clip(self.boundary_target, 0.0, 1.0))

    @property
    def extent_upper_bound(self) -> float:
        return self.inventory_scale / abs(float(self.stoichiometric_matrix[1, 0]))

    @property
    def initial_amounts(self) -> np.ndarray:
        if self.stoichiometric_matrix[1, 0] > 0.0:
            return np.asarray([self.inventory_scale, 0.0])
        return np.asarray([0.0, self.inventory_scale])

    @property
    def reference_extent(self) -> float:
        if self.stoichiometric_matrix[1, 0] > 0.0:
            reacted_fraction = self.reference_composition
        else:
            reacted_fraction = 1.0 - self.reference_composition
        return reacted_fraction * self.extent_upper_bound

    def amounts(self, vector: np.ndarray) -> np.ndarray:
        if vector.shape != (1,) or not np.all(np.isfinite(vector)):
            raise ValueError("CE extent vector must contain one finite entry")
        extent = float(vector[0])
        amounts = self.initial_amounts + self.stoichiometric_matrix[:, 0] * extent
        if np.any(amounts < -1.0e-12 * self.inventory_scale):
            raise ValueError("CE extent produces a negative species amount")
        return np.maximum(amounts, 0.0)

    @staticmethod
    def _xlog_ratio(fraction: float, reference: float) -> float:
        if fraction == 0.0:
            return 0.0
        return fraction * math.log(fraction / reference)

    def gibbs(self, amounts: np.ndarray) -> float:
        values = np.asarray(amounts, dtype=float)
        if values.shape != (2,) or np.any(values < 0.0) or not np.all(np.isfinite(values)):
            raise ValueError("CE amounts must be two finite nonnegative entries")
        total = float(np.sum(values))
        if total <= 0.0:
            raise ValueError("CE total amount must be positive")
        fractions = values / total
        if self.boundary_target is None:
            reference = np.asarray([1.0 - self.target_extent, self.target_extent])
            molar = self._xlog_ratio(float(fractions[0]), float(reference[0])) - fractions[0] + reference[0]
            molar += self._xlog_ratio(float(fractions[1]), float(reference[1])) - fractions[1] + reference[1]
        else:
            molar = (float(fractions[1]) - self.boundary_target) ** 2
        return total * molar

    def chemical_potentials(self, amounts: np.ndarray) -> np.ndarray:
        values = np.asarray(amounts, dtype=float)
        total = float(np.sum(values))
        fractions = values / total
        if self.boundary_target is None:
            if np.any(fractions <= 0.0):
                raise ValueError("ideal manufactured chemical potentials require positive fractions")
            reference = np.asarray([1.0 - self.target_extent, self.target_extent])
            return np.log(fractions / reference)
        x_b = float(fractions[1])
        molar = (x_b - self.boundary_target) ** 2
        derivative = 2.0 * (x_b - self.boundary_target)
        return np.asarray([molar - x_b * derivative, molar + (1.0 - x_b) * derivative])

    def _objective(self, vector: np.ndarray) -> float:
        return self.gibbs(self.amounts(vector))

    def _gradient(self, vector: np.ndarray) -> np.ndarray:
        potentials = self.chemical_potentials(self.amounts(vector))
        return np.asarray([float(self.stoichiometric_matrix[:, 0] @ potentials)])

    def build(self) -> DirectProblem:
        if self.boundary_target is None:
            lower, upper = 1.0e-8 * self.extent_upper_bound, (1.0 - 1.0e-8) * self.extent_upper_bound
        else:
            lower, upper = 0.0, self.extent_upper_bound
        return DirectProblem(
            self.descriptor,
            BoxDomain.from_sequences([lower], [upper], [self.extent_upper_bound]),
            self._objective,
            self._gradient,
            objective_scale=self.inventory_scale,
        )

    def starts(self, seed: int) -> tuple[np.ndarray, ...]:
        generator = np.random.default_rng(seed)
        near = float(
            np.clip(
                self.reference_extent - 0.02 * self.extent_upper_bound,
                0.05 * self.extent_upper_bound,
                0.95 * self.extent_upper_bound,
            )
        )
        return (
            np.asarray([near]),
            np.asarray([0.2 * self.extent_upper_bound]),
            generator.uniform(0.05 * self.extent_upper_bound, 0.95 * self.extent_upper_bound, size=1),
        )

    def affinity(self, vector: np.ndarray, *, reaction_orientation: float = 1.0) -> float:
        potentials = self.chemical_potentials(self.amounts(vector))
        return float(reaction_orientation * self.stoichiometric_matrix[:, 0] @ potentials)

    def certify(self, vector: np.ndarray) -> Certificate:
        try:
            amounts = self.amounts(vector)
            potentials = self.chemical_potentials(amounts)
        except ValueError:
            return Certificate(self.descriptor.formulation_id, False, {"invalid_state": 1.0}, True)
        element_residual = self.element_matrix @ amounts - np.asarray([self.inventory_scale])
        affinity = float(self.stoichiometric_matrix[:, 0] @ potentials)
        boundary = amounts <= 1.0e-12 * self.inventory_scale
        if boundary[0]:
            element_multiplier = float(potentials[1])
        elif boundary[1]:
            element_multiplier = float(potentials[0])
        else:
            element_multiplier = float(np.mean(potentials))
        lower_multipliers = potentials - element_multiplier
        lower_multipliers = np.where(boundary, lower_multipliers, 0.0)
        stationarity = potentials - element_multiplier - lower_multipliers
        complementarity = amounts * lower_multipliers
        reference_vector = np.asarray([self.reference_extent])
        objective_gap = self._objective(vector) - self._objective(reference_vector)
        reaction_scale = float(self.stoichiometric_matrix[1, 0] ** 2 / self.inventory_scale)
        if self.boundary_target is None:
            reference = self.reference_composition
            convexity = reaction_scale * (1.0 / reference + 1.0 / (1.0 - reference))
        else:
            convexity = 2.0 * reaction_scale
        dual_minimum = float(np.min(lower_multipliers[boundary])) if np.any(boundary) else 0.0
        metrics = {
            "element_balance_inf_norm": float(np.max(np.abs(element_residual))),
            "affinity_inf_norm": abs(affinity),
            "reaction_basis_rank": float(np.linalg.matrix_rank(self.stoichiometric_matrix)),
            "reaction_space_complete": 1.0,
            "objective_gap": float(objective_gap),
            "boundary_species_count": float(np.count_nonzero(boundary)),
            "stationarity_inf_norm": float(np.max(np.abs(stationarity))),
            "complementarity_inf_norm": float(np.max(np.abs(complementarity))),
            "active_multiplier_min": dual_minimum,
            "feasible_curvature": convexity,
            "minimum_amount": float(np.min(amounts)),
        }
        accepted = metrics["element_balance_inf_norm"] < 1.0e-12
        accepted = accepted and abs(metrics["objective_gap"]) < 1.0e-12
        accepted = accepted and metrics["minimum_amount"] >= -1.0e-12
        accepted = accepted and metrics["stationarity_inf_norm"] < 1.0e-10
        accepted = accepted and metrics["complementarity_inf_norm"] < 1.0e-10
        accepted = accepted and metrics["active_multiplier_min"] >= -1.0e-12
        if not np.any(boundary):
            accepted = accepted and metrics["affinity_inf_norm"] < 1.0e-10
        independent = abs(objective_gap) < 1.0e-12 and convexity > 0.0
        return Certificate(self.descriptor.formulation_id, accepted, metrics, independent)
