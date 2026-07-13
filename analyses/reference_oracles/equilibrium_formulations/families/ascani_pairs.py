"""Manufactured Ascani counterion-pair residual formulation."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from analyses.reference_oracles.equilibrium_formulations.kernel import (
    BoxDomain,
    Certificate,
    FormulationDescriptor,
    NumericalKind,
    ResidualAdapter,
    ResidualProblem,
)


@dataclass(frozen=True)
class AscaniPairAdapter(ResidualAdapter):
    """Counterion-pair transfer backed by one extensive reduced Gibbs owner.

    Reduced coordinates contain one neutral amount and two electrically neutral
    pair amounts. Their extensive-Gibbs derivatives are respectively the
    neutral chemical potential and the two independent pair potentials.
    """

    pair_rows: tuple[tuple[float, float, float], ...] = ((1.0, 1.0, 0.0), (1.0, 0.0, 1.0))

    def __post_init__(self) -> None:
        matrix = self.pair_matrix
        if matrix.shape != (2, 3) or np.linalg.matrix_rank(matrix) != 2:
            raise ValueError("counterion-pair basis must have full row rank")
        if np.max(np.abs(matrix @ self.charge_numbers)) > 1.0e-12:
            raise ValueError("counterion-pair basis must lie in the charge-null space")

    @property
    def descriptor(self) -> FormulationDescriptor:
        return FormulationDescriptor(
            "ascani.counterion-pair.manufactured.v1",
            "Ascani counterion-pair equilibrium",
            NumericalKind.RESIDUAL_SOLVE,
        )

    @property
    def pair_matrix(self) -> np.ndarray:
        return np.asarray(self.pair_rows, dtype=float)

    @property
    def charge_numbers(self) -> np.ndarray:
        return np.asarray([1.0, -1.0, -1.0])

    @staticmethod
    def _reduced_total() -> np.ndarray:
        return np.asarray([2.0, 1.0, 1.0])

    @staticmethod
    def _alpha_reference_amounts() -> np.ndarray:
        return np.asarray([0.8, 0.3, 0.2])

    @classmethod
    def _beta_reference_amounts(cls) -> np.ndarray:
        return cls._reduced_total() - cls._alpha_reference_amounts()

    def pair_potentials(
        self,
        chemical_potentials: np.ndarray,
        *,
        faraday_galvani_energy: float,
    ) -> np.ndarray:
        """Return pair potentials on the same energy basis as ``chemical_potentials``.

        ``faraday_galvani_energy`` means ``F*Phi`` for molar-energy
        potentials, or ``F*Phi/(R*T)`` when all potentials are divided by
        ``R*T``. The neutral pair rows cancel this gauge term exactly.
        """

        values = np.asarray(chemical_potentials, dtype=float)
        if values.shape != (3,) or not np.all(np.isfinite(values)):
            raise ValueError("charged chemical-potential vector must have three finite entries")
        if not np.isfinite(faraday_galvani_energy):
            raise ValueError("faraday_galvani_energy must be finite")
        electrochemical = values + self.charge_numbers * faraday_galvani_energy
        return self.pair_matrix @ electrochemical

    @staticmethod
    def _reference_fractions(phase: str) -> np.ndarray:
        if phase == "alpha":
            amounts = AscaniPairAdapter._alpha_reference_amounts()
        elif phase == "beta":
            amounts = AscaniPairAdapter._beta_reference_amounts()
        else:
            raise ValueError("phase must be 'alpha' or 'beta'")
        return amounts / np.sum(amounts)

    def reduced_phase_gibbs(self, reduced_amounts: np.ndarray, *, phase: str) -> float:
        """Return a one-homogeneous relative-entropy Gibbs fixture."""

        amounts = np.asarray(reduced_amounts, dtype=float)
        if amounts.shape != (3,) or np.any(amounts <= 0.0) or not np.all(np.isfinite(amounts)):
            raise ValueError("reduced neutral/pair amounts must contain three positive finite entries")
        total = float(np.sum(amounts))
        fractions = amounts / total
        reference = self._reference_fractions(phase)
        return float(np.sum(amounts * np.log(fractions / reference)))

    def reduced_phase_potentials(self, reduced_amounts: np.ndarray, *, phase: str) -> np.ndarray:
        amounts = np.asarray(reduced_amounts, dtype=float)
        if amounts.shape != (3,) or np.any(amounts <= 0.0) or not np.all(np.isfinite(amounts)):
            raise ValueError("reduced neutral/pair amounts must contain three positive finite entries")
        fractions = amounts / np.sum(amounts)
        return np.log(fractions / self._reference_fractions(phase))

    @staticmethod
    def reduced_phase_hessian(reduced_amounts: np.ndarray) -> np.ndarray:
        amounts = np.asarray(reduced_amounts, dtype=float)
        if amounts.shape != (3,) or np.any(amounts <= 0.0) or not np.all(np.isfinite(amounts)):
            raise ValueError("reduced neutral/pair amounts must contain three positive finite entries")
        total = float(np.sum(amounts))
        return np.diag(1.0 / amounts) - np.ones((3, 3)) / total

    def _charged_potential_representative(self, pair_potentials: np.ndarray) -> np.ndarray:
        return self.pair_matrix.T @ np.linalg.solve(
            self.pair_matrix @ self.pair_matrix.T,
            pair_potentials,
        )

    def _reduced_phase_amounts(self, vector: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        alpha = np.asarray(vector, dtype=float)
        beta = self._reduced_total() - alpha
        return alpha, beta

    def _phase_potentials(self, vector: np.ndarray) -> tuple[float, float, np.ndarray, np.ndarray]:
        alpha, beta = self._reduced_phase_amounts(vector)
        alpha_reduced = self.reduced_phase_potentials(alpha, phase="alpha")
        beta_reduced = self.reduced_phase_potentials(beta, phase="beta")
        return (
            float(alpha_reduced[0]),
            float(beta_reduced[0]),
            self._charged_potential_representative(alpha_reduced[1:]),
            self._charged_potential_representative(beta_reduced[1:]),
        )

    def _residual(self, vector: np.ndarray) -> np.ndarray:
        neutral_alpha, neutral_beta, charged_alpha, charged_beta = self._phase_potentials(vector)
        return np.concatenate(
            (
                np.asarray([neutral_alpha - neutral_beta]),
                self.pair_potentials(charged_alpha, faraday_galvani_energy=0.0)
                - self.pair_potentials(charged_beta, faraday_galvani_energy=0.0),
            )
        )

    def _jacobian(self, vector: np.ndarray) -> np.ndarray:
        alpha, beta = self._reduced_phase_amounts(vector)
        return self.reduced_phase_hessian(alpha) + self.reduced_phase_hessian(beta)

    def build(self) -> ResidualProblem:
        return ResidualProblem(
            self.descriptor,
            BoxDomain.from_sequences([0.05, 0.05, 0.05], [1.95, 0.95, 0.95], [1.0, 0.5, 0.5]),
            self._residual,
            self._jacobian,
            residual_scale=(1.0, 1.0, 1.0),
        )

    def starts(self, seed: int) -> tuple[np.ndarray, ...]:
        generator = np.random.default_rng(seed)
        domain = self.build().domain
        return np.asarray([0.9, 0.35, 0.25]), generator.uniform(domain.lower_array, domain.upper_array)

    def _phase_amounts(self, vector: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        reduced_alpha, reduced_beta = self._reduced_phase_amounts(vector)
        charged_alpha = self.pair_matrix.T @ reduced_alpha[1:]
        charged_beta = self.pair_matrix.T @ reduced_beta[1:]
        alpha = np.concatenate(([reduced_alpha[0]], charged_alpha))
        beta = np.concatenate(([reduced_beta[0]], charged_beta))
        return alpha, beta

    def certify(self, vector: np.ndarray) -> Certificate:
        if vector.shape != (3,) or not np.all(np.isfinite(vector)):
            return Certificate(self.descriptor.formulation_id, False, {"invalid_state": 1.0}, True)
        try:
            reduced_alpha, reduced_beta = self._reduced_phase_amounts(vector)
            alpha, beta = self._phase_amounts(vector)
            neutral_alpha, neutral_beta, charged_mu_alpha, charged_mu_beta = self._phase_potentials(vector)
        except ValueError:
            return Certificate(self.descriptor.formulation_id, False, {"invalid_state": 1.0}, True)
        pair_potential_gap = float(
            np.max(
                np.abs(
                    self.pair_potentials(charged_mu_alpha, faraday_galvani_energy=0.0)
                    - self.pair_potentials(charged_mu_beta, faraday_galvani_energy=0.0)
                )
            )
        )
        total = alpha + beta
        expected = np.concatenate(([self._reduced_total()[0]], self.pair_matrix.T @ self._reduced_total()[1:]))
        phase_charge = max(
            abs(float(self.charge_numbers @ alpha[1:])),
            abs(float(self.charge_numbers @ beta[1:])),
        )
        total_hessian = self.reduced_phase_hessian(reduced_alpha) + self.reduced_phase_hessian(reduced_beta)
        euler_error = max(
            abs(
                self.reduced_phase_gibbs(reduced_alpha, phase="alpha")
                - float(reduced_alpha @ self.reduced_phase_potentials(reduced_alpha, phase="alpha"))
            ),
            abs(
                self.reduced_phase_gibbs(reduced_beta, phase="beta")
                - float(reduced_beta @ self.reduced_phase_potentials(reduced_beta, phase="beta"))
            ),
        )
        root_gap = float(np.max(np.abs(vector - self._alpha_reference_amounts())))
        metrics = {
            "residual_inf_norm": float(np.max(np.abs(self._residual(vector)))),
            "pair_basis_rank": float(np.linalg.matrix_rank(self.pair_matrix)),
            "pair_basis_charge_null_inf_norm": float(np.max(np.abs(self.pair_matrix @ self.charge_numbers))),
            "material_balance_inf_norm": float(np.max(np.abs(total - expected))),
            "phase_charge_inf_norm": phase_charge,
            "neutral_potential_gap": abs(neutral_alpha - neutral_beta),
            "pair_potential_gap": pair_potential_gap,
            "minimum_amount": float(min(np.min(alpha), np.min(beta))),
            "extensive_euler_abs": euler_error,
            "reduced_hessian_symmetry_max_abs": float(np.max(np.abs(total_hessian - total_hessian.T))),
            "minimum_transfer_curvature": float(np.min(np.linalg.eigvalsh(total_hessian))),
            "analytic_root_gap": root_gap,
        }
        accepted = metrics["residual_inf_norm"] < 1.0e-10
        accepted = accepted and metrics["pair_basis_rank"] == 2.0
        accepted = accepted and metrics["pair_basis_charge_null_inf_norm"] < 1.0e-12
        accepted = accepted and metrics["material_balance_inf_norm"] < 1.0e-12
        accepted = accepted and metrics["phase_charge_inf_norm"] < 1.0e-12
        accepted = accepted and metrics["neutral_potential_gap"] < 1.0e-10
        accepted = accepted and metrics["pair_potential_gap"] < 1.0e-10
        accepted = accepted and metrics["minimum_amount"] >= 0.0
        accepted = accepted and metrics["extensive_euler_abs"] < 1.0e-12
        accepted = accepted and metrics["reduced_hessian_symmetry_max_abs"] < 1.0e-12
        accepted = accepted and metrics["minimum_transfer_curvature"] > 0.0
        independent = root_gap < 1.0e-9 and metrics["minimum_transfer_curvature"] > 0.0
        return Certificate(self.descriptor.formulation_id, accepted and independent, metrics, independent)
