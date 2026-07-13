"""Manufactured Perdomo modified-mole HELD2 direct formulation."""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from analyses.reference_oracles.equilibrium_formulations.kernel import (
    BoxDomain,
    Certificate,
    DirectAdapter,
    DirectProblem,
    FormulationDescriptor,
    NumericalKind,
)
from analyses.reference_oracles.neutral_held.oracle import ManufacturedTripleWellEvaluator


@dataclass(frozen=True)
class ModifiedMoleSplit:
    phase_fraction: float
    u_alpha: float
    u_beta: float
    v_alpha: float
    v_beta: float


@dataclass(frozen=True)
class PerdomoHeld2Adapter(DirectAdapter):
    evaluator: ManufacturedTripleWellEvaluator = field(default_factory=ManufacturedTripleWellEvaluator)

    @property
    def descriptor(self) -> FormulationDescriptor:
        return FormulationDescriptor(
            "perdomo-held2.modified-mole.manufactured.v1",
            "Perdomo modified-mole HELD2",
            NumericalKind.DIRECT_MINIMIZATION,
        )

    @staticmethod
    def recover_physical_composition(modified_cation_fraction: float) -> np.ndarray:
        u = float(modified_cation_fraction)
        eliminated_ion = 0.5 * u
        if not np.isfinite(u) or eliminated_ion < 0.0 or u > 1.0:
            raise ValueError("eliminated ion amount must be nonnegative and physical")
        return np.asarray([1.0 - u, 0.5 * u, eliminated_ion])

    @staticmethod
    def modified_potentials(
        chemical_potentials: np.ndarray,
        *,
        faraday_galvani_energy: float,
    ) -> np.ndarray:
        """Return modified potentials with an explicit electrostatic-energy basis.

        ``faraday_galvani_energy`` denotes ``F*Phi`` in the energy units of
        ``chemical_potentials``, or ``F*Phi/(R*T)`` if they are reduced by
        ``R*T``.
        """

        values = np.asarray(chemical_potentials, dtype=float)
        if values.shape != (3,):
            raise ValueError("chemical_potentials must contain solvent, cation, and eliminated anion")
        if not np.isfinite(faraday_galvani_energy):
            raise ValueError("faraday_galvani_energy must be finite")
        charge = np.asarray([0.0, 1.0, -1.0])
        electrochemical = values + charge * faraday_galvani_energy
        return np.asarray([electrochemical[0], 0.5 * (electrochemical[1] + electrochemical[2])])

    def decode(self, vector: np.ndarray) -> ModifiedMoleSplit:
        if vector.shape != (4,) or not np.all(np.isfinite(vector)):
            raise ValueError("HELD2 reduced vector must contain four finite entries")
        u_alpha, u_beta, v_alpha, v_beta = (float(value) for value in vector)
        if not u_alpha < 0.5 < u_beta:
            raise ValueError("modified compositions must straddle the modified feed")
        fraction = (u_beta - 0.5) / (u_beta - u_alpha)
        return ModifiedMoleSplit(fraction, u_alpha, u_beta, v_alpha, v_beta)

    def _phase_gibbs(self, u: float, volume: float) -> float:
        return self.evaluator.molar_helmholtz(u, volume) + volume

    def _phase_gradient(self, u: float, volume: float) -> np.ndarray:
        gradient = self.evaluator.gradient(u, volume).copy()
        gradient[1] += 1.0
        return gradient

    def _objective(self, vector: np.ndarray) -> float:
        state = self.decode(vector)
        return float(
            state.phase_fraction * self._phase_gibbs(state.u_alpha, state.v_alpha)
            + (1.0 - state.phase_fraction) * self._phase_gibbs(state.u_beta, state.v_beta)
        )

    def _gradient(self, vector: np.ndarray) -> np.ndarray:
        state = self.decode(vector)
        separation = state.u_beta - state.u_alpha
        fraction = state.phase_fraction
        complement = 1.0 - fraction
        gibbs_alpha = self._phase_gibbs(state.u_alpha, state.v_alpha)
        gibbs_beta = self._phase_gibbs(state.u_beta, state.v_beta)
        gradient_alpha = self._phase_gradient(state.u_alpha, state.v_alpha)
        gradient_beta = self._phase_gradient(state.u_beta, state.v_beta)
        return np.asarray(
            [
                fraction / separation * (gibbs_alpha - gibbs_beta) + fraction * gradient_alpha[0],
                complement / separation * (gibbs_alpha - gibbs_beta) + complement * gradient_beta[0],
                fraction * gradient_alpha[1],
                complement * gradient_beta[1],
            ]
        )

    def build(self) -> DirectProblem:
        return DirectProblem(
            self.descriptor,
            BoxDomain.from_sequences(
                [0.05, 0.51, 0.5, 0.5],
                [0.49, 0.95, 1.5, 1.5],
                [0.3, 0.7, 1.0, 1.0],
            ),
            self._objective,
            self._gradient,
        )

    def starts(self, seed: int) -> tuple[np.ndarray, ...]:
        generator = np.random.default_rng(seed)
        domain = self.build().domain
        return (
            np.asarray([0.21, 0.79, 1.02, 0.98]),
            np.asarray([0.35, 0.65, 0.9, 1.1]),
            generator.uniform(domain.lower_array, domain.upper_array),
        )

    def phase_modified_potentials(self, u: float, volume: float) -> np.ndarray:
        gibbs = self._phase_gibbs(u, volume)
        gradient = self._phase_gradient(u, volume)
        common_volume_term = -volume * gradient[1]
        return np.asarray(
            [
                gibbs - u * gradient[0] + common_volume_term,
                gibbs + (1.0 - u) * gradient[0] + common_volume_term,
            ]
        )

    def extensive_phase_gibbs(self, modified_amounts: np.ndarray, volume: float) -> float:
        amounts = np.asarray(modified_amounts, dtype=float)
        total = float(np.sum(amounts))
        if amounts.shape != (2,) or np.any(amounts <= 0.0) or total <= 0.0 or volume <= 0.0:
            raise ValueError("modified amounts and volume must be positive")
        return total * self._phase_gibbs(float(amounts[1] / total), volume / total)

    def _enumerated_objective(self) -> float:
        compositions = np.unique(np.concatenate((np.linspace(0.0, 1.0, 101), np.asarray([0.2, 0.5, 0.8]))))
        volumes = np.unique(np.concatenate((np.linspace(0.5, 1.5, 101), np.asarray([1.0]))))
        phase_minima = np.asarray(
            [min(self._phase_gibbs(float(u), float(volume)) for volume in volumes) for u in compositions]
        )
        best = float(phase_minima[int(np.argmin(np.abs(compositions - 0.5)))])
        left_indices = np.flatnonzero(compositions <= 0.5)
        right_indices = np.flatnonzero(compositions >= 0.5)
        for left in left_indices:
            for right in right_indices:
                if compositions[right] <= compositions[left]:
                    continue
                fraction = (compositions[right] - 0.5) / (compositions[right] - compositions[left])
                value = fraction * phase_minima[left] + (1.0 - fraction) * phase_minima[right]
                best = min(best, float(value))
        return best

    def certify(self, vector: np.ndarray) -> Certificate:
        try:
            state = self.decode(vector)
        except ValueError:
            return Certificate(self.descriptor.formulation_id, False, {"invalid_state": 1.0}, True)
        modified_balance = state.phase_fraction * state.u_alpha + (1.0 - state.phase_fraction) * state.u_beta
        alpha = self.recover_physical_composition(state.u_alpha)
        beta = self.recover_physical_composition(state.u_beta)
        ordinary_balance = state.phase_fraction * alpha + (1.0 - state.phase_fraction) * beta
        expected_balance = self.recover_physical_composition(0.5)
        charges = np.asarray([0.0, 1.0, -1.0])
        charge_residual = max(abs(float(charges @ alpha)), abs(float(charges @ beta)))
        potential_gap = float(
            np.max(
                np.abs(
                    self.phase_modified_potentials(state.u_alpha, state.v_alpha)
                    - self.phase_modified_potentials(state.u_beta, state.v_beta)
                )
            )
        )
        pressure_stationarity = max(
            abs(float(self._phase_gradient(state.u_alpha, state.v_alpha)[1])),
            abs(float(self._phase_gradient(state.u_beta, state.v_beta)[1])),
        )
        reduced_kkt = float(np.max(np.abs(self._gradient(vector))))
        objective_gap = self._objective(vector) - self._enumerated_objective()
        metrics = {
            "modified_balance_abs": abs(modified_balance - 0.5),
            "ordinary_balance_inf_norm": float(np.max(np.abs(ordinary_balance - expected_balance))),
            "phase_charge_inf_norm": charge_residual,
            "modified_potential_gap": potential_gap,
            "pressure_stationarity_inf_norm": pressure_stationarity,
            "reduced_kkt_inf_norm": reduced_kkt,
            "enumeration_objective_gap": float(objective_gap),
            "independent_modified_composition_count": 1.0,
        }
        accepted = (
            max(
                metrics["modified_balance_abs"],
                metrics["ordinary_balance_inf_norm"],
                metrics["phase_charge_inf_norm"],
                metrics["modified_potential_gap"],
                metrics["pressure_stationarity_inf_norm"],
                metrics["reduced_kkt_inf_norm"],
                abs(metrics["enumeration_objective_gap"]),
            )
            < 1.0e-8
        )
        return Certificate(self.descriptor.formulation_id, accepted, metrics, abs(objective_gap) < 1.0e-8)
