"""Thermodynamically consistent manufactured pressure-boundary formulations."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

import numpy as np

from analyses.reference_oracles.equilibrium_formulations.kernel import (
    BoxDomain,
    Certificate,
    FormulationDescriptor,
    NumericalKind,
    ResidualAdapter,
    ResidualProblem,
)


class BoundaryKind(str, Enum):
    BUBBLE_PRESSURE = "bubble_pressure"
    DEW_PRESSURE = "dew_pressure"
    PURE_SATURATION = "pure_saturation"


@dataclass(frozen=True)
class BinaryBoundaryEvaluator:
    """One extensive Helmholtz function with two prescribed stable wells."""

    potential_shift: tuple[float, float] = (0.0, 0.0)
    imposed_pressure: float = 2.0

    @staticmethod
    def _liquid_well() -> np.ndarray:
        return np.asarray([0.25, 1.0])

    @staticmethod
    def _vapour_well() -> np.ndarray:
        return np.asarray([0.75, 3.0])

    def _gibbs_well(self, composition: float, volume: float) -> tuple[float, np.ndarray, np.ndarray]:
        point = np.asarray([composition, volume], dtype=float)
        liquid_displacement = point - self._liquid_well()
        vapour_displacement = point - self._vapour_well()
        liquid_distance = float(np.dot(liquid_displacement, liquid_displacement))
        vapour_distance = float(np.dot(vapour_displacement, vapour_displacement))
        value = liquid_distance * vapour_distance
        gradient = 2.0 * liquid_displacement * vapour_distance + 2.0 * vapour_displacement * liquid_distance
        hessian = (
            2.0 * np.eye(2) * (liquid_distance + vapour_distance)
            + 4.0 * np.outer(liquid_displacement, vapour_displacement)
            + 4.0 * np.outer(vapour_displacement, liquid_displacement)
        )
        return value, gradient, hessian

    def molar_helmholtz(self, composition: float, volume: float) -> float:
        value, _, _ = self._gibbs_well(composition, volume)
        first, second = self.potential_shift
        affine_species_energy = second + (first - second) * composition
        return value - self.imposed_pressure * volume + affine_species_energy

    def properties(self, composition: float, volume: float) -> tuple[float, np.ndarray]:
        _, gradient, _ = self._gibbs_well(composition, volume)
        first, second = self.potential_shift
        helmholtz = self.molar_helmholtz(composition, volume)
        helmholtz_x = gradient[0] + first - second
        helmholtz_v = gradient[1] - self.imposed_pressure
        pressure = -helmholtz_v
        mu_first = helmholtz + (1.0 - composition) * helmholtz_x - volume * helmholtz_v
        mu_second = helmholtz - composition * helmholtz_x - volume * helmholtz_v
        return pressure, np.asarray([mu_first, mu_second])

    def property_derivatives(self, composition: float, volume: float) -> tuple[np.ndarray, np.ndarray]:
        _, _, hessian = self._gibbs_well(composition, volume)
        g_xx, g_xv, g_vv = hessian[0, 0], hessian[0, 1], hessian[1, 1]
        pressure_derivative = np.asarray([-g_xv, -g_vv])
        potential_derivative = np.asarray(
            [
                [(1.0 - composition) * g_xx - volume * g_xv, (1.0 - composition) * g_xv - volume * g_vv],
                [-composition * g_xx - volume * g_xv, -composition * g_xv - volume * g_vv],
            ]
        )
        return pressure_derivative, potential_derivative

    def extensive_helmholtz(self, volume: float, amounts: np.ndarray) -> float:
        values = np.asarray(amounts, dtype=float)
        total = float(np.sum(values))
        if values.shape != (2,) or total <= 0.0 or np.any(values <= 0.0) or volume <= 0.0:
            raise ValueError("binary extensive state must contain positive volume and amounts")
        return total * self.molar_helmholtz(float(values[0] / total), volume / total)

    def euler_error(self, composition: float, volume: float) -> float:
        pressure, potentials = self.properties(composition, volume)
        lhs = self.molar_helmholtz(composition, volume) + pressure * volume
        rhs = composition * potentials[0] + (1.0 - composition) * potentials[1]
        return abs(lhs - rhs)


@dataclass(frozen=True)
class PureBoundaryEvaluator:
    potential_shift: float = 0.0
    imposed_pressure: float = 2.0

    @staticmethod
    def _well(volume: float) -> tuple[float, float, float]:
        left = volume - 1.0
        right = volume - 3.0
        value = left**2 * right**2
        first = 2.0 * left * right * (left + right)
        second = 2.0 * (left + right) ** 2 + 4.0 * left * right
        return value, first, second

    def molar_helmholtz(self, volume: float) -> float:
        value, _, _ = self._well(volume)
        return value - self.imposed_pressure * volume + self.potential_shift

    def properties(self, volume: float) -> tuple[float, float]:
        value, first, _ = self._well(volume)
        pressure = self.imposed_pressure - first
        potential = value - volume * first + self.potential_shift
        return pressure, potential

    def property_derivatives(self, volume: float) -> tuple[float, float]:
        _, _, second = self._well(volume)
        return -second, -volume * second

    def extensive_helmholtz(self, volume: float, amount: float) -> float:
        if volume <= 0.0 or amount <= 0.0:
            raise ValueError("pure extensive state must contain positive volume and amount")
        return amount * self.molar_helmholtz(volume / amount)

    def euler_error(self, volume: float) -> float:
        pressure, potential = self.properties(volume)
        return abs(self.molar_helmholtz(volume) + pressure * volume - potential)


@dataclass(frozen=True)
class ManufacturedBoundaryAdapter(ResidualAdapter):
    kind: BoundaryKind
    potential_shift: tuple[float, float] = (0.0, 0.0)

    @property
    def descriptor(self) -> FormulationDescriptor:
        return FormulationDescriptor(
            formulation_id=f"public.{self.kind.value}.manufactured.v1",
            family=f"public {self.kind.value}",
            numerical_kind=NumericalKind.RESIDUAL_SOLVE,
        )

    @property
    def evaluator(self) -> BinaryBoundaryEvaluator | PureBoundaryEvaluator:
        if self.kind is BoundaryKind.PURE_SATURATION:
            return PureBoundaryEvaluator(self.potential_shift[0])
        return BinaryBoundaryEvaluator(self.potential_shift)

    @property
    def target(self) -> np.ndarray:
        if self.kind is BoundaryKind.BUBBLE_PRESSURE:
            return np.asarray([2.0, 1.0, 3.0, 0.75, 0.25])
        if self.kind is BoundaryKind.DEW_PRESSURE:
            return np.asarray([2.0, 1.0, 3.0, 0.25, 0.75])
        return np.asarray([2.0, 1.0, 3.0])

    def _residual(self, vector: np.ndarray) -> np.ndarray:
        pressure, liquid_volume, vapour_volume = vector[:3]
        if self.kind is BoundaryKind.PURE_SATURATION:
            evaluator = self.evaluator
            assert isinstance(evaluator, PureBoundaryEvaluator)
            liquid_pressure, liquid_potential = evaluator.properties(liquid_volume)
            vapour_pressure, vapour_potential = evaluator.properties(vapour_volume)
            return np.asarray(
                [liquid_pressure - pressure, vapour_pressure - pressure, liquid_potential - vapour_potential]
            )

        evaluator = self.evaluator
        assert isinstance(evaluator, BinaryBoundaryEvaluator)
        trial = vector[3:5]
        trial_composition = float(trial[0])
        if self.kind is BoundaryKind.BUBBLE_PRESSURE:
            liquid_composition, vapour_composition = 0.25, trial_composition
        else:
            liquid_composition, vapour_composition = trial_composition, 0.75
        liquid_pressure, liquid_potentials = evaluator.properties(liquid_composition, liquid_volume)
        vapour_pressure, vapour_potentials = evaluator.properties(vapour_composition, vapour_volume)
        return np.asarray(
            [
                liquid_pressure - pressure,
                vapour_pressure - pressure,
                *(liquid_potentials - vapour_potentials),
                float(np.sum(trial) - 1.0),
            ]
        )

    def _jacobian(self, vector: np.ndarray) -> np.ndarray:
        _, liquid_volume, vapour_volume = vector[:3]
        if self.kind is BoundaryKind.PURE_SATURATION:
            evaluator = self.evaluator
            assert isinstance(evaluator, PureBoundaryEvaluator)
            liquid_pressure_v, liquid_potential_v = evaluator.property_derivatives(liquid_volume)
            vapour_pressure_v, vapour_potential_v = evaluator.property_derivatives(vapour_volume)
            return np.asarray(
                [
                    [-1.0, liquid_pressure_v, 0.0],
                    [-1.0, 0.0, vapour_pressure_v],
                    [0.0, liquid_potential_v, -vapour_potential_v],
                ]
            )

        evaluator = self.evaluator
        assert isinstance(evaluator, BinaryBoundaryEvaluator)
        trial_composition = float(vector[3])
        if self.kind is BoundaryKind.BUBBLE_PRESSURE:
            liquid_composition, vapour_composition = 0.25, trial_composition
        else:
            liquid_composition, vapour_composition = trial_composition, 0.75
        liquid_pressure_derivative, liquid_potential_derivative = evaluator.property_derivatives(
            liquid_composition, liquid_volume
        )
        vapour_pressure_derivative, vapour_potential_derivative = evaluator.property_derivatives(
            vapour_composition, vapour_volume
        )
        trial_pressure_liquid = liquid_pressure_derivative[0] if self.kind is BoundaryKind.DEW_PRESSURE else 0.0
        trial_pressure_vapour = vapour_pressure_derivative[0] if self.kind is BoundaryKind.BUBBLE_PRESSURE else 0.0
        trial_potential = (
            liquid_potential_derivative[:, 0]
            if self.kind is BoundaryKind.DEW_PRESSURE
            else -vapour_potential_derivative[:, 0]
        )
        return np.asarray(
            [
                [-1.0, liquid_pressure_derivative[1], 0.0, trial_pressure_liquid, 0.0],
                [-1.0, 0.0, vapour_pressure_derivative[1], trial_pressure_vapour, 0.0],
                [
                    0.0,
                    liquid_potential_derivative[0, 1],
                    -vapour_potential_derivative[0, 1],
                    trial_potential[0],
                    0.0,
                ],
                [
                    0.0,
                    liquid_potential_derivative[1, 1],
                    -vapour_potential_derivative[1, 1],
                    trial_potential[1],
                    0.0,
                ],
                [0.0, 0.0, 0.0, 1.0, 1.0],
            ]
        )

    def build(self) -> ResidualProblem:
        if self.kind is BoundaryKind.PURE_SATURATION:
            domain = BoxDomain.from_sequences([0.1, 0.5, 2.0], [5.0, 2.0, 4.5], [2.0, 1.0, 3.0])
        else:
            domain = BoxDomain.from_sequences(
                [0.1, 0.5, 2.0, 0.0, 0.0],
                [5.0, 2.0, 4.5, 1.0, 1.0],
                [2.0, 1.0, 3.0, 1.0, 1.0],
            )
        return ResidualProblem(self.descriptor, domain, self._residual, self._jacobian)

    def starts(self, seed: int) -> tuple[np.ndarray, ...]:
        generator = np.random.default_rng(seed)
        domain = self.build().domain
        random_start = generator.uniform(domain.lower_array, domain.upper_array)
        if self.kind is BoundaryKind.PURE_SATURATION:
            fixed_start = np.asarray([1.5, 0.8, 3.5])
        else:
            fixed_start = np.asarray([1.5, 0.8, 3.5, 0.5, 0.5])
        near_start = self.target.copy()
        near_start[:3] += np.asarray([-0.1, 0.03, -0.03])
        if self.kind is not BoundaryKind.PURE_SATURATION:
            near_start[3:] += np.asarray([-0.02, 0.02])
        return near_start, fixed_start, random_start

    def certify(self, vector: np.ndarray) -> Certificate:
        expected_dimension = 3 if self.kind is BoundaryKind.PURE_SATURATION else 5
        if vector.shape != (expected_dimension,) or not np.all(np.isfinite(vector)):
            return Certificate(self.descriptor.formulation_id, False, {"invalid_state": 1.0}, True)
        residual_norm = float(np.max(np.abs(self._residual(vector))))
        volume_gap = float(vector[2] - vector[1])
        rank = int(np.linalg.matrix_rank(self._jacobian(vector)))
        domain = self.build().domain
        in_domain = bool(
            np.all(vector >= domain.lower_array - 1.0e-12) and np.all(vector <= domain.upper_array + 1.0e-12)
        )
        root_gap = float(np.max(np.abs(vector - self.target)))
        if self.kind is BoundaryKind.PURE_SATURATION:
            evaluator = self.evaluator
            assert isinstance(evaluator, PureBoundaryEvaluator)
            curvature = min(evaluator._well(1.0)[2], evaluator._well(3.0)[2])
            euler_error = max(evaluator.euler_error(vector[1]), evaluator.euler_error(vector[2]))
        else:
            evaluator = self.evaluator
            assert isinstance(evaluator, BinaryBoundaryEvaluator)
            curvature = min(
                float(np.min(np.linalg.eigvalsh(evaluator._gibbs_well(0.25, 1.0)[2]))),
                float(np.min(np.linalg.eigvalsh(evaluator._gibbs_well(0.75, 3.0)[2]))),
            )
            euler_error = max(evaluator.euler_error(0.25, vector[1]), evaluator.euler_error(0.75, vector[2]))
        independent = root_gap < 1.0e-8 and curvature > 0.0 and euler_error < 1.0e-10
        accepted = residual_norm < 1.0e-8 and volume_gap > 1.0e-8 and vector[0] > 0.0
        accepted = accepted and rank == expected_dimension and in_domain and independent
        return Certificate(
            formulation_id=self.descriptor.formulation_id,
            accepted=accepted,
            metrics={
                "residual_inf_norm": residual_norm,
                "volume_gap": volume_gap,
                "jacobian_rank": float(rank),
                "analytic_root_gap": root_gap,
                "minimum_well_curvature": curvature,
                "euler_identity_abs": euler_error,
                "global_stability_claim": 0.0,
            },
            independent_evidence=independent,
        )
