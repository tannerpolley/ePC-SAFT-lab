"""Manufactured simultaneous coupled phase-and-chemical equilibrium."""

from __future__ import annotations

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
class CoupledState:
    phase_fraction: float
    alpha: tuple[float, float, float]
    beta: tuple[float, float, float]

    def swapped(self) -> CoupledState:
        return CoupledState(1.0 - self.phase_fraction, self.beta, self.alpha)


@dataclass(frozen=True)
class CoupledPhaseChemicalAdapter(DirectAdapter):
    element_reference_shift: tuple[float, float] = (0.0, 0.0)

    @property
    def descriptor(self) -> FormulationDescriptor:
        return FormulationDescriptor(
            "cpe.manufactured.v1",
            "coupled phase-and-chemical equilibrium",
            NumericalKind.DIRECT_MINIMIZATION,
        )

    @property
    def element_matrix(self) -> np.ndarray:
        return np.asarray([[1.0, 1.0, 0.0], [0.0, 0.0, 1.0]])

    @property
    def reaction_vector(self) -> np.ndarray:
        return np.asarray([-1.0, 1.0, 0.0])

    @property
    def global_lower_bound(self) -> float:
        first, second = self.element_reference_shift
        return 0.6 * first + 0.4 * second

    @staticmethod
    def _well_alpha() -> np.ndarray:
        return np.asarray([0.2, 0.2, 1.0])

    @staticmethod
    def _well_beta() -> np.ndarray:
        return np.asarray([0.3, 0.6, 3.0])

    def _phase_energy(self, phase: np.ndarray) -> float:
        first_distance = float(np.dot(phase - self._well_alpha(), phase - self._well_alpha()))
        second_distance = float(np.dot(phase - self._well_beta(), phase - self._well_beta()))
        first, second = self.element_reference_shift
        reference = first * (1.0 - phase[1]) + second * phase[1]
        return first_distance * second_distance + reference

    def _phase_gradient(self, phase: np.ndarray) -> np.ndarray:
        first_displacement = phase - self._well_alpha()
        second_displacement = phase - self._well_beta()
        first_distance = float(np.dot(first_displacement, first_displacement))
        second_distance = float(np.dot(second_displacement, second_displacement))
        gradient = 2.0 * first_displacement * second_distance + 2.0 * second_displacement * first_distance
        first, second = self.element_reference_shift
        gradient[1] += second - first
        return gradient

    def decode(self, vector: np.ndarray) -> CoupledState:
        if vector.shape != (6,) or not np.all(np.isfinite(vector)):
            raise ValueError("CPE reduced vector must contain six finite entries")
        alpha = tuple(float(item) for item in vector[:3])
        beta = tuple(float(item) for item in vector[3:])
        if not alpha[1] < 0.4 < beta[1]:
            raise ValueError("phase C compositions must straddle the elemental feed")
        if alpha[0] + alpha[1] > 1.0 or beta[0] + beta[1] > 1.0:
            raise ValueError("phase compositions must lie in the ternary simplex")
        fraction = (beta[1] - 0.4) / (beta[1] - alpha[1])
        return CoupledState(fraction, alpha, beta)

    def objective_state(self, state: CoupledState) -> float:
        alpha = np.asarray(state.alpha)
        beta = np.asarray(state.beta)
        return float(
            state.phase_fraction * self._phase_energy(alpha) + (1.0 - state.phase_fraction) * self._phase_energy(beta)
        )

    def _objective(self, vector: np.ndarray) -> float:
        return self.objective_state(self.decode(vector))

    def _gradient(self, vector: np.ndarray) -> np.ndarray:
        state = self.decode(vector)
        alpha = np.asarray(state.alpha)
        beta = np.asarray(state.beta)
        fraction = state.phase_fraction
        complement = 1.0 - fraction
        separation = beta[1] - alpha[1]
        energy_alpha = self._phase_energy(alpha)
        energy_beta = self._phase_energy(beta)
        gradient_alpha = self._phase_gradient(alpha)
        gradient_beta = self._phase_gradient(beta)
        return np.asarray(
            [
                fraction * gradient_alpha[0],
                fraction / separation * (energy_alpha - energy_beta) + fraction * gradient_alpha[1],
                fraction * gradient_alpha[2],
                complement * gradient_beta[0],
                complement / separation * (energy_alpha - energy_beta) + complement * gradient_beta[1],
                complement * gradient_beta[2],
            ]
        )

    def build(self) -> DirectProblem:
        return DirectProblem(
            self.descriptor,
            BoxDomain.from_sequences(
                [0.05, 0.1, 0.5, 0.2, 0.5, 2.5],
                [0.35, 0.3, 1.5, 0.35, 0.65, 3.5],
                [0.2, 0.2, 1.0, 0.3, 0.6, 3.0],
            ),
            self._objective,
            self._gradient,
        )

    def starts(self, seed: int) -> tuple[np.ndarray, ...]:
        generator = np.random.default_rng(seed)
        domain = self.build().domain
        return (
            np.asarray([0.205, 0.205, 1.02, 0.295, 0.595, 2.98]),
            np.asarray([0.25, 0.25, 1.2, 0.25, 0.55, 2.8]),
            generator.uniform(domain.lower_array, domain.upper_array),
        )

    def topology(self, state: CoupledState, *, tolerance: float = 1.0e-10) -> str:
        """Classify a CPE active set without claiming a topology search."""

        if state.phase_fraction <= tolerance or state.phase_fraction >= 1.0 - tolerance:
            return "single_phase_boundary"
        alpha = self._phase_composition(np.asarray(state.alpha))
        beta = self._phase_composition(np.asarray(state.beta))
        if np.max(np.abs(alpha - beta)) <= tolerance and abs(state.alpha[2] - state.beta[2]) <= tolerance:
            return "duplicate_single_phase"
        if min(float(np.min(alpha)), float(np.min(beta))) <= tolerance:
            return "boundary_species_two_phase"
        return "interior_two_phase"

    def _phase_composition(self, phase: np.ndarray) -> np.ndarray:
        return np.asarray([phase[0], 1.0 - phase[0] - phase[1], phase[1]])

    def chemical_potentials(self, phase: np.ndarray) -> np.ndarray:
        energy = self._phase_energy(phase)
        gradient = self._phase_gradient(phase)
        x_a, x_c = phase[:2]
        mu_b = energy - x_a * gradient[0] - x_c * gradient[1] - phase[2] * gradient[2]
        return np.asarray([mu_b + gradient[0], mu_b, mu_b + gradient[1]])

    def extensive_phase_gibbs(self, amounts: np.ndarray, volume: float) -> float:
        values = np.asarray(amounts, dtype=float)
        total = float(np.sum(values))
        if values.shape != (3,) or np.any(values <= 0.0) or total <= 0.0 or volume <= 0.0:
            raise ValueError("CPE phase amounts and volume must be positive")
        phase = np.asarray([values[0] / total, values[2] / total, volume / total])
        return total * self._phase_energy(phase)

    def staged_candidates(self) -> tuple[np.ndarray, np.ndarray]:
        ce_only = np.asarray([0.25, 0.2, 1.0, 0.25, 0.6, 3.0])
        phase_only = np.asarray([0.2, 0.2, 1.0, 0.2, 0.6, 3.0])
        return ce_only, phase_only

    def certify(self, vector: np.ndarray) -> Certificate:
        try:
            state = self.decode(vector)
        except ValueError:
            return Certificate(self.descriptor.formulation_id, False, {"invalid_state": 1.0}, True)
        alpha = np.asarray(state.alpha)
        beta = np.asarray(state.beta)
        alpha_composition = self._phase_composition(alpha)
        beta_composition = self._phase_composition(beta)
        total = state.phase_fraction * alpha_composition + (1.0 - state.phase_fraction) * beta_composition
        element_residual = self.element_matrix @ total - np.asarray([0.6, 0.4])
        mu_alpha = self.chemical_potentials(alpha)
        mu_beta = self.chemical_potentials(beta)
        affinities = np.asarray([self.reaction_vector @ mu_alpha, self.reaction_vector @ mu_beta])
        pressure_residuals = np.asarray([self._phase_gradient(alpha)[2], self._phase_gradient(beta)[2]])
        objective_gap = self.objective_state(state) - self.global_lower_bound
        metrics = {
            "element_balance_inf_norm": float(np.max(np.abs(element_residual))),
            "interphase_potential_gap": float(np.max(np.abs(mu_alpha - mu_beta))),
            "reaction_affinity_inf_norm": float(np.max(np.abs(affinities))),
            "pressure_stationarity_inf_norm": float(np.max(np.abs(pressure_residuals))),
            "global_lower_bound_gap": float(objective_gap),
            "reactive_tpd_complete": 0.0,
            "minimum_species_fraction": float(min(np.min(alpha_composition), np.min(beta_composition))),
            "reaction_space_complete": 1.0,
        }
        accepted = metrics["element_balance_inf_norm"] < 1.0e-10
        accepted = accepted and metrics["interphase_potential_gap"] < 1.0e-9
        accepted = accepted and metrics["reaction_affinity_inf_norm"] < 1.0e-9
        accepted = accepted and metrics["pressure_stationarity_inf_norm"] < 1.0e-9
        accepted = accepted and abs(metrics["global_lower_bound_gap"]) < 1.0e-10
        accepted = accepted and metrics["minimum_species_fraction"] >= -1.0e-12
        return Certificate(self.descriptor.formulation_id, accepted, metrics, abs(objective_gap) < 1.0e-10)
