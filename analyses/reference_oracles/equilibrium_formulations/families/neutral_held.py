"""Neutral and association-aware HELD manufactured conformance adapters."""

from __future__ import annotations

import math
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
from analyses.reference_oracles.neutral_held.oracle import (
    ManufacturedTripleWellEvaluator,
    NeutralHeldProblem,
    PhaseEvaluator,
    PhaseSplit,
    diagnose_candidate,
    enumerate_global,
)


@dataclass(frozen=True)
class NeutralHeldAdapter(DirectAdapter):
    evaluator: PhaseEvaluator = field(default_factory=ManufacturedTripleWellEvaluator)
    formulation_id: str = "neutral-held.stage-iii.manufactured.v1"
    family_name: str = "neutral HELD Stage III"

    @property
    def descriptor(self) -> FormulationDescriptor:
        return FormulationDescriptor(
            formulation_id=self.formulation_id,
            family=self.family_name,
            numerical_kind=NumericalKind.DIRECT_MINIMIZATION,
        )

    @property
    def problem(self) -> NeutralHeldProblem:
        return NeutralHeldProblem(
            evaluator=self.evaluator,
            feed_composition=0.5,
            pressure=1.0,
            volume_bounds=(0.5, 1.5),
        )

    def decode(self, vector: np.ndarray) -> PhaseSplit:
        if vector.shape != (4,) or not np.all(np.isfinite(vector)):
            raise ValueError("neutral HELD reduced vector must contain four finite entries")
        x_alpha, x_beta, v_alpha, v_beta = (float(value) for value in vector)
        if not x_alpha < self.problem.feed_composition < x_beta:
            raise ValueError("reduced phase compositions must straddle the feed")
        phase_fraction = (x_beta - self.problem.feed_composition) / (x_beta - x_alpha)
        return PhaseSplit(phase_fraction, x_alpha, v_alpha, x_beta, v_beta)

    def _objective(self, vector: np.ndarray) -> float:
        return self.problem.objective_value(self.decode(vector))

    def _gradient(self, vector: np.ndarray) -> np.ndarray:
        state = self.decode(vector)
        separation = state.x_beta - state.x_alpha
        beta = state.phase_fraction
        complement = 1.0 - beta
        gibbs_alpha = self.problem.phase_gibbs(state.x_alpha, state.v_alpha)
        gibbs_beta = self.problem.phase_gibbs(state.x_beta, state.v_beta)
        gradient_alpha = self.problem.phase_gibbs_gradient(state.x_alpha, state.v_alpha)
        gradient_beta = self.problem.phase_gibbs_gradient(state.x_beta, state.v_beta)
        beta_x_alpha = beta / separation
        beta_x_beta = complement / separation
        return np.asarray(
            [
                beta_x_alpha * (gibbs_alpha - gibbs_beta) + beta * gradient_alpha[0],
                beta_x_beta * (gibbs_alpha - gibbs_beta) + complement * gradient_beta[0],
                beta * gradient_alpha[1],
                complement * gradient_beta[1],
            ]
        )

    def build(self) -> DirectProblem:
        return DirectProblem(
            descriptor=self.descriptor,
            domain=BoxDomain.from_sequences(
                [0.05, 0.51, 0.5, 0.5],
                [0.49, 0.95, 1.5, 1.5],
                [0.3, 0.7, 1.0, 1.0],
            ),
            objective=self._objective,
            gradient=self._gradient,
        )

    def starts(self, seed: int) -> tuple[np.ndarray, ...]:
        generator = np.random.default_rng(seed)
        domain = self.build().domain
        return (
            np.asarray([0.21, 0.79, 1.02, 0.98]),
            np.asarray([0.35, 0.65, 0.9, 1.1]),
            generator.uniform(domain.lower_array, domain.upper_array),
        )

    def certify(self, vector: np.ndarray) -> Certificate:
        try:
            state = self.problem.with_objective(self.decode(vector))
            global_reference = enumerate_global(self.problem)
            evidence = diagnose_candidate(self.problem, state, global_reference)
        except ValueError:
            return Certificate(self.descriptor.formulation_id, False, {"invalid_state": 1.0}, True)
        metrics = {
            "material_balance_abs": evidence.material_balance_abs,
            "pressure_stationarity_inf_norm": evidence.pressure_stationarity_inf_norm,
            "kkt_stationarity_inf_norm": evidence.kkt_stationarity_inf_norm,
            "potential_gap": evidence.potential_gap,
            "common_tangent_gap": evidence.common_tangent_gap,
            "minimum_tangent_plane_distance": evidence.minimum_tangent_plane_distance,
            "enumeration_objective_gap": evidence.enumeration_objective_gap,
        }
        accepted = evidence.global_evidence and evidence.material_balance_abs < 1.0e-10
        return Certificate(self.descriptor.formulation_id, accepted, metrics, evidence.global_evidence)


@dataclass(frozen=True)
class NeutralHeldSinglePhaseAdapter(DirectAdapter):
    """Family-owned active-set variant for a retained single phase."""

    evaluator: PhaseEvaluator = field(default_factory=ManufacturedTripleWellEvaluator)
    feed_composition: float = 0.1
    pressure: float = 1.03

    @property
    def descriptor(self) -> FormulationDescriptor:
        return FormulationDescriptor(
            "neutral-held.stage-iii.single-phase.manufactured.v1",
            "neutral HELD Stage III single-phase active set",
            NumericalKind.DIRECT_MINIMIZATION,
        )

    @property
    def problem(self) -> NeutralHeldProblem:
        return NeutralHeldProblem(self.evaluator, self.feed_composition, self.pressure, (0.5, 1.5))

    def _objective(self, vector: np.ndarray) -> float:
        return self.problem.phase_gibbs(self.feed_composition, float(vector[0]))

    def _gradient(self, vector: np.ndarray) -> np.ndarray:
        return np.asarray([self.problem.phase_gibbs_gradient(self.feed_composition, float(vector[0]))[1]])

    def build(self) -> DirectProblem:
        return DirectProblem(
            self.descriptor,
            BoxDomain.from_sequences([0.5], [1.5], [1.0]),
            self._objective,
            self._gradient,
        )

    def starts(self, seed: int) -> tuple[np.ndarray, ...]:
        generator = np.random.default_rng(seed)
        return np.asarray([1.05]), generator.uniform(0.5, 1.5, size=1)

    def certify(self, vector: np.ndarray) -> Certificate:
        if vector.shape != (1,) or not np.all(np.isfinite(vector)):
            return Certificate(self.descriptor.formulation_id, False, {"invalid_state": 1.0}, True)
        state = PhaseSplit(
            1.0,
            self.feed_composition,
            float(vector[0]),
            self.feed_composition,
            float(vector[0]),
        )
        try:
            candidate = self.problem.with_objective(state)
            global_reference = enumerate_global(self.problem)
            evidence = diagnose_candidate(self.problem, candidate, global_reference)
        except ValueError:
            return Certificate(self.descriptor.formulation_id, False, {"invalid_state": 1.0}, True)
        metrics = {
            "material_balance_abs": evidence.material_balance_abs,
            "pressure_stationarity_inf_norm": evidence.pressure_stationarity_inf_norm,
            "minimum_tangent_plane_distance": evidence.minimum_tangent_plane_distance,
            "enumeration_objective_gap": evidence.enumeration_objective_gap,
            "single_phase_active_set": 1.0,
        }
        accepted = (
            evidence.global_evidence
            and max(
                metrics["material_balance_abs"],
                metrics["pressure_stationarity_inf_norm"],
                abs(metrics["enumeration_objective_gap"]),
            )
            < 1.0e-8
        )
        return Certificate(self.descriptor.formulation_id, accepted, metrics, evidence.global_evidence)


@dataclass(frozen=True)
class ManufacturedAssociationEvaluator:
    """Scalar implicit state wrapped around the neutral manufactured energy."""

    base: ManufacturedTripleWellEvaluator = field(default_factory=ManufacturedTripleWellEvaluator)
    residual_scale: float = 1.0
    coupling: float = 0.4

    @staticmethod
    def _sigma(composition: float, molar_volume: float) -> float:
        return 0.2 + 0.1 * composition + 0.05 * molar_volume

    @staticmethod
    def _sigma_gradient() -> np.ndarray:
        return np.asarray([0.1, 0.05])

    def association_residual(self, composition: float, molar_volume: float, state: float) -> float:
        return self.residual_scale * (state - self._sigma(composition, molar_volume))

    def solve_association(self, composition: float, molar_volume: float) -> float:
        if not math.isfinite(self.residual_scale) or abs(self.residual_scale) <= 1.0e-14:
            raise ValueError("association state Jacobian is singular")
        self.base._validate(composition, molar_volume)
        return self._sigma(composition, molar_volume)

    def association_sensitivity(self, composition: float, molar_volume: float) -> np.ndarray:
        self.solve_association(composition, molar_volume)
        residual_state_jacobian = self.residual_scale
        residual_outer_jacobian = -self.residual_scale * self._sigma_gradient()
        return -residual_outer_jacobian / residual_state_jacobian

    def association_state_is_accepted(
        self,
        composition: float,
        molar_volume: float,
        state: float,
        *,
        tolerance: float = 1.0e-12,
    ) -> bool:
        return abs(self.association_residual(composition, molar_volume, state)) <= tolerance

    def molar_helmholtz(self, composition: float, molar_volume: float) -> float:
        state = self.solve_association(composition, molar_volume)
        return self.base.molar_helmholtz(composition, molar_volume) + self.coupling * (
            state - self._sigma(composition, molar_volume)
        )

    def frozen_state_gradient(self, composition: float, molar_volume: float) -> np.ndarray:
        self.solve_association(composition, molar_volume)
        return self.base.gradient(composition, molar_volume) - self.coupling * self._sigma_gradient()

    def gradient(self, composition: float, molar_volume: float) -> np.ndarray:
        fixed_state = self.frozen_state_gradient(composition, molar_volume)
        state_response = self.coupling * self.association_sensitivity(composition, molar_volume)
        return fixed_state + state_response

    def hessian(self, composition: float, molar_volume: float) -> np.ndarray:
        self.solve_association(composition, molar_volume)
        return self.base.hessian(composition, molar_volume)


@dataclass(frozen=True)
class AssociationHeldAdapter(NeutralHeldAdapter):
    evaluator: ManufacturedAssociationEvaluator = field(default_factory=ManufacturedAssociationEvaluator)
    formulation_id: str = "association-neutral-held.stage-iii.manufactured.v1"
    family_name: str = "association-aware neutral HELD Stage III"

    def certify(self, vector: np.ndarray) -> Certificate:
        outer = super().certify(vector)
        if not outer.accepted:
            return outer
        state = self.decode(vector)
        residuals: list[float] = []
        derivative_errors: list[float] = []
        reduced_energy_errors: list[float] = []
        step = 1.0e-6
        for composition, volume in ((state.x_alpha, state.v_alpha), (state.x_beta, state.v_beta)):
            association_state = self.evaluator.solve_association(composition, volume)
            residuals.append(abs(self.evaluator.association_residual(composition, volume, association_state)))
            analytic = self.evaluator.association_sensitivity(composition, volume)
            numerical = np.asarray(
                [
                    (
                        self.evaluator.solve_association(composition + step, volume)
                        - self.evaluator.solve_association(composition - step, volume)
                    )
                    / (2.0 * step),
                    (
                        self.evaluator.solve_association(composition, volume + step)
                        - self.evaluator.solve_association(composition, volume - step)
                    )
                    / (2.0 * step),
                ]
            )
            derivative_errors.append(float(np.max(np.abs(analytic - numerical))))
            numerical_energy_gradient = np.asarray(
                [
                    (
                        self.evaluator.molar_helmholtz(composition + step, volume)
                        - self.evaluator.molar_helmholtz(composition - step, volume)
                    )
                    / (2.0 * step),
                    (
                        self.evaluator.molar_helmholtz(composition, volume + step)
                        - self.evaluator.molar_helmholtz(composition, volume - step)
                    )
                    / (2.0 * step),
                ]
            )
            reduced_energy_errors.append(
                float(np.max(np.abs(self.evaluator.gradient(composition, volume) - numerical_energy_gradient)))
            )
        metrics = dict(outer.metrics)
        metrics["association_residual_inf_norm"] = max(residuals)
        metrics["implicit_derivative_max_abs_error"] = max(derivative_errors)
        metrics["reduced_energy_derivative_max_abs_error"] = max(reduced_energy_errors)
        accepted = outer.accepted and metrics["association_residual_inf_norm"] < 1.0e-12
        accepted = accepted and metrics["implicit_derivative_max_abs_error"] < 1.0e-9
        accepted = accepted and metrics["reduced_energy_derivative_max_abs_error"] < 1.0e-7
        return Certificate(self.descriptor.formulation_id, accepted, metrics, outer.independent_evidence)
