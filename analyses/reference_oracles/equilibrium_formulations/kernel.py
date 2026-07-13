"""Analysis-private execution kernel for manufactured equilibrium formulations.

The kernel shares numerical plumbing and receipts.  Thermodynamic coordinates,
topology, independent evidence, and acceptance certificates remain family-owned.
"""

from __future__ import annotations

import math
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from enum import Enum

import numpy as np
from numpy.typing import NDArray

FloatArray = NDArray[np.float64]
ScalarFunction = Callable[[FloatArray], float]
VectorFunction = Callable[[FloatArray], FloatArray]
MatrixFunction = Callable[[FloatArray], FloatArray]


class NumericalKind(str, Enum):
    """Nominal numerical path; it is part of the formulation identity."""

    DIRECT_MINIMIZATION = "direct_minimization"
    RESIDUAL_SOLVE = "residual_solve"


@dataclass(frozen=True)
class FormulationDescriptor:
    formulation_id: str
    family: str
    numerical_kind: NumericalKind

    def __post_init__(self) -> None:
        if not self.formulation_id.strip() or not self.family.strip():
            raise ValueError("formulation_id and family must be nonempty")


@dataclass(frozen=True)
class BoxDomain:
    lower: tuple[float, ...]
    upper: tuple[float, ...]
    scale: tuple[float, ...]

    @classmethod
    def from_sequences(
        cls,
        lower: object,
        upper: object,
        scale: object,
    ) -> BoxDomain:
        lower_array = np.asarray(lower, dtype=float)
        upper_array = np.asarray(upper, dtype=float)
        scale_array = np.asarray(scale, dtype=float)
        if lower_array.ndim != 1 or upper_array.ndim != 1 or scale_array.ndim != 1:
            raise ValueError("domain entries must be one-dimensional")
        if not (lower_array.size == upper_array.size == scale_array.size):
            raise ValueError("domain dimensions must match")
        if lower_array.size == 0:
            raise ValueError("domain dimensions must be nonzero")
        if not np.all(np.isfinite(lower_array)) or not np.all(np.isfinite(upper_array)):
            raise ValueError("domain bounds must be finite")
        if not np.all(np.isfinite(scale_array)) or np.any(scale_array <= 0.0):
            raise ValueError("domain scale must be finite and positive")
        if np.any(lower_array >= upper_array):
            raise ValueError("domain bounds must be strictly increasing")
        return cls(tuple(lower_array), tuple(upper_array), tuple(scale_array))

    @property
    def dimension(self) -> int:
        return len(self.lower)

    @property
    def lower_array(self) -> FloatArray:
        return np.asarray(self.lower, dtype=float)

    @property
    def upper_array(self) -> FloatArray:
        return np.asarray(self.upper, dtype=float)

    def validate_vector(self, vector: object, *, label: str) -> FloatArray:
        array = np.asarray(vector, dtype=float)
        if array.shape != (self.dimension,):
            raise ValueError(f"{label} dimension must equal {self.dimension}")
        if not np.all(np.isfinite(array)):
            raise ValueError(f"{label} must be finite")
        if np.any(array < self.lower_array) or np.any(array > self.upper_array):
            raise ValueError(f"{label} must lie inside the box domain")
        return array


@dataclass(frozen=True)
class DirectProblem:
    descriptor: FormulationDescriptor
    domain: BoxDomain
    objective: ScalarFunction
    gradient: VectorFunction
    objective_scale: float = 1.0

    def __post_init__(self) -> None:
        if self.descriptor.numerical_kind is not NumericalKind.DIRECT_MINIMIZATION:
            raise ValueError("direct problem requires a direct-minimization descriptor")
        if not math.isfinite(self.objective_scale) or self.objective_scale <= 0.0:
            raise ValueError("objective_scale must be finite and positive")


@dataclass(frozen=True)
class ResidualProblem:
    descriptor: FormulationDescriptor
    domain: BoxDomain
    residual: VectorFunction
    jacobian: MatrixFunction
    residual_scale: tuple[float, ...] | None = None

    def __post_init__(self) -> None:
        if self.descriptor.numerical_kind is not NumericalKind.RESIDUAL_SOLVE:
            raise ValueError("residual problem requires a residual-solve descriptor")
        if self.residual_scale is not None:
            scale = np.asarray(self.residual_scale, dtype=float)
            if scale.ndim != 1 or scale.size == 0:
                raise ValueError("residual_scale must be a nonempty one-dimensional sequence")
            if not np.all(np.isfinite(scale)) or np.any(scale <= 0.0):
                raise ValueError("residual_scale must be finite and positive")

    def scale_array(self, residual_count: int) -> FloatArray:
        if self.residual_scale is None:
            return np.ones(residual_count, dtype=float)
        scale = np.asarray(self.residual_scale, dtype=float)
        if scale.shape != (residual_count,):
            raise ValueError("residual_scale length must match the residual dimension")
        return scale


@dataclass(frozen=True)
class DerivativeReceipt:
    max_abs_error: float
    step: float


@dataclass(frozen=True)
class Candidate:
    vector: tuple[float, ...]
    merit: float
    converged: bool
    iterations: int
    projected_gradient_inf_norm: float


@dataclass(frozen=True)
class Certificate:
    formulation_id: str
    accepted: bool
    metrics: Mapping[str, float]
    independent_evidence: bool


@dataclass(frozen=True)
class BackendIdentity:
    name: str = "numpy_projected_gradient"
    ipopt_available: bool = False
    ipopt_used: bool = False
    fallback_used: bool = False
    availability_note: str = "IPOPT is excluded by this EOS-free manufactured analysis contract"


@dataclass(frozen=True)
class RunReceipt:
    formulation_id: str
    numerical_kind: NumericalKind
    backend: BackendIdentity
    seed: int
    candidates: tuple[Candidate, ...]
    candidate_certificates: tuple[Certificate | None, ...]
    selected: Candidate
    certificate: Certificate


class CandidateOutcome(str, Enum):
    """Family-certificate-aware result for one deterministic local start."""

    ACCEPTED = "accepted"
    REJECTED = "converged_but_rejected"
    NOT_CONVERGED = "not_converged"


@dataclass(frozen=True)
class CandidateClassification:
    formulation_id: str
    seed: int
    start_index: int
    outcome: CandidateOutcome
    candidate: Candidate


@dataclass(frozen=True)
class ConvergenceSummary:
    classifications: tuple[CandidateClassification, ...]
    accepted_count: int
    rejected_count: int
    not_converged_count: int


def summarize_convergence(receipts: tuple[RunReceipt, ...]) -> ConvergenceSummary:
    """Classify every local start without weakening family-owned certificates."""

    classifications: list[CandidateClassification] = []
    for receipt in receipts:
        if len(receipt.candidates) != len(receipt.candidate_certificates):
            raise ValueError("candidate and certificate counts must match")
        for index, (candidate, certificate) in enumerate(
            zip(receipt.candidates, receipt.candidate_certificates, strict=True)
        ):
            if not candidate.converged:
                if certificate is not None:
                    raise ValueError("a nonconverged candidate cannot carry a certificate")
                outcome = CandidateOutcome.NOT_CONVERGED
            elif certificate is None:
                raise ValueError("a converged candidate must carry a certificate")
            elif certificate.accepted:
                outcome = CandidateOutcome.ACCEPTED
            else:
                outcome = CandidateOutcome.REJECTED
            classifications.append(
                CandidateClassification(
                    receipt.formulation_id,
                    receipt.seed,
                    index,
                    outcome,
                    candidate,
                )
            )
    accepted = sum(item.outcome is CandidateOutcome.ACCEPTED for item in classifications)
    rejected = sum(item.outcome is CandidateOutcome.REJECTED for item in classifications)
    not_converged = sum(item.outcome is CandidateOutcome.NOT_CONVERGED for item in classifications)
    return ConvergenceSummary(tuple(classifications), accepted, rejected, not_converged)


class DirectAdapter:
    descriptor: FormulationDescriptor

    def build(self) -> DirectProblem:
        raise NotImplementedError

    def starts(self, seed: int) -> tuple[FloatArray, ...]:
        raise NotImplementedError

    def certify(self, vector: FloatArray) -> Certificate:
        raise NotImplementedError

    def candidate_order(self, candidate: Candidate, certificate: Certificate) -> tuple[object, ...]:
        return candidate.merit, candidate.vector


class ResidualAdapter:
    descriptor: FormulationDescriptor

    def build(self) -> ResidualProblem:
        raise NotImplementedError

    def starts(self, seed: int) -> tuple[FloatArray, ...]:
        raise NotImplementedError

    def certify(self, vector: FloatArray) -> Certificate:
        raise NotImplementedError

    def candidate_order(self, candidate: Candidate, certificate: Certificate) -> tuple[object, ...]:
        return candidate.merit, candidate.vector


def _central_gradient(function: ScalarFunction, point: FloatArray, step: float) -> FloatArray:
    values = np.empty(point.size, dtype=float)
    for index in range(point.size):
        delta = np.zeros_like(point)
        delta[index] = step
        values[index] = (function(point + delta) - function(point - delta)) / (2.0 * step)
    return values


def check_direct_derivatives(
    problem: DirectProblem,
    point: object,
    *,
    step: float = 1.0e-6,
) -> DerivativeReceipt:
    if not math.isfinite(step) or step <= 0.0:
        raise ValueError("step must be finite and positive")
    vector = problem.domain.validate_vector(point, label="derivative point")
    analytic = np.asarray(problem.gradient(vector), dtype=float)
    if analytic.shape != vector.shape or not np.all(np.isfinite(analytic)):
        raise ValueError("direct gradient must be finite and match the problem dimension")
    numerical = _central_gradient(problem.objective, vector, step)
    return DerivativeReceipt(float(np.max(np.abs(analytic - numerical))), step)


def check_residual_derivatives(
    problem: ResidualProblem,
    point: object,
    *,
    step: float = 1.0e-6,
) -> DerivativeReceipt:
    if not math.isfinite(step) or step <= 0.0:
        raise ValueError("step must be finite and positive")
    vector = problem.domain.validate_vector(point, label="derivative point")
    residual = np.asarray(problem.residual(vector), dtype=float)
    analytic = np.asarray(problem.jacobian(vector), dtype=float)
    if residual.ndim != 1 or not np.all(np.isfinite(residual)):
        raise ValueError("residual must be a finite vector")
    if analytic.shape != (residual.size, vector.size) or not np.all(np.isfinite(analytic)):
        raise ValueError("residual Jacobian must be finite and have shape (residuals, variables)")
    numerical = np.column_stack(
        [
            (
                np.asarray(problem.residual(vector + step * np.eye(vector.size)[index]), dtype=float)
                - np.asarray(problem.residual(vector - step * np.eye(vector.size)[index]), dtype=float)
            )
            / (2.0 * step)
            for index in range(vector.size)
        ]
    )
    return DerivativeReceipt(float(np.max(np.abs(analytic - numerical))), step)


def _local_minimize(
    domain: BoxDomain,
    objective: ScalarFunction,
    gradient: VectorFunction,
    start: object,
    *,
    objective_scale: float,
    tolerance: float,
    max_iterations: int,
) -> Candidate:
    vector = domain.validate_vector(start, label="start")
    lower = domain.lower_array
    upper = domain.upper_array
    scale = np.asarray(domain.scale, dtype=float)
    scaled_lower = lower / scale
    scaled_upper = upper / scale
    physical_value = float(objective(vector))
    if not math.isfinite(physical_value):
        raise ValueError("objective callback must return a finite value")
    value = physical_value / objective_scale

    converged = False
    projected_norm = math.inf
    iterations = 0
    for iterations in range(max_iterations + 1):
        derivative = np.asarray(gradient(vector), dtype=float)
        if derivative.shape != vector.shape or not np.all(np.isfinite(derivative)):
            raise ValueError("gradient callback must be finite and match the problem dimension")
        scaled_vector = vector / scale
        scaled_derivative = derivative * scale / objective_scale
        projected = scaled_vector - np.clip(scaled_vector - scaled_derivative, scaled_lower, scaled_upper)
        projected_norm = float(np.max(np.abs(projected)))
        if projected_norm <= tolerance:
            converged = True
            break
        if iterations == max_iterations:
            break

        direction = -scaled_derivative
        directional_derivative = float(np.dot(scaled_derivative, direction))
        step = 1.0
        accepted = False
        for _ in range(80):
            trial_scaled = np.clip(scaled_vector + step * direction, scaled_lower, scaled_upper)
            trial = trial_scaled * scale
            if np.array_equal(trial, vector):
                step *= 0.5
                continue
            trial_physical_value = float(objective(trial))
            if not math.isfinite(trial_physical_value):
                step *= 0.5
                continue
            trial_value = trial_physical_value / objective_scale
            displacement = trial_scaled - scaled_vector
            armijo_slope = float(np.dot(scaled_derivative, displacement))
            trial_derivative = np.asarray(gradient(trial), dtype=float)
            if trial_derivative.shape != vector.shape or not np.all(np.isfinite(trial_derivative)):
                step *= 0.5
                continue
            trial_scaled_derivative = trial_derivative * scale / objective_scale
            trial_projected = trial_scaled - np.clip(
                trial_scaled - trial_scaled_derivative,
                scaled_lower,
                scaled_upper,
            )
            trial_projected_norm = float(np.max(np.abs(trial_projected)))
            objective_resolution = 32.0 * np.finfo(float).eps * max(1.0, abs(value), abs(trial_value))
            sufficient_decrease = (
                trial_value <= value + 1.0e-4 * armijo_slope
                and trial_value < value - objective_resolution
                and armijo_slope < 0.0
            )
            resolved_stationarity = (
                trial_value <= value + objective_resolution and trial_projected_norm <= 0.9 * projected_norm
            )
            if sufficient_decrease or resolved_stationarity:
                vector = trial
                value = trial_value
                physical_value = trial_physical_value
                accepted = True
                break
            step *= 0.5
        if not accepted and projected_norm <= 1.0e-5:
            hessian = np.empty((vector.size, vector.size), dtype=float)
            finite_hessian = True
            for index in range(vector.size):
                difference_step = 1.0e-5 * max(1.0, abs(float(scaled_vector[index])))
                if not (
                    scaled_lower[index] < scaled_vector[index] - difference_step
                    and scaled_vector[index] + difference_step < scaled_upper[index]
                ):
                    finite_hessian = False
                    break
                plus_scaled = scaled_vector.copy()
                minus_scaled = scaled_vector.copy()
                plus_scaled[index] += difference_step
                minus_scaled[index] -= difference_step
                plus_gradient = np.asarray(gradient(plus_scaled * scale), dtype=float) * scale / objective_scale
                minus_gradient = np.asarray(gradient(minus_scaled * scale), dtype=float) * scale / objective_scale
                if not np.all(np.isfinite(plus_gradient)) or not np.all(np.isfinite(minus_gradient)):
                    finite_hessian = False
                    break
                hessian[:, index] = (plus_gradient - minus_gradient) / (2.0 * difference_step)
            if finite_hessian:
                hessian = 0.5 * (hessian + hessian.T)
                newton_direction = np.linalg.lstsq(hessian, -scaled_derivative, rcond=None)[0]
                if float(np.dot(scaled_derivative, newton_direction)) < 0.0:
                    for refinement_step in (1.0, 0.5, 0.25, 0.125):
                        trial_scaled = np.clip(
                            scaled_vector + refinement_step * newton_direction,
                            scaled_lower,
                            scaled_upper,
                        )
                        trial = trial_scaled * scale
                        trial_physical_value = float(objective(trial))
                        trial_value = trial_physical_value / objective_scale
                        trial_derivative = np.asarray(gradient(trial), dtype=float)
                        if not math.isfinite(trial_value) or not np.all(np.isfinite(trial_derivative)):
                            continue
                        trial_scaled_derivative = trial_derivative * scale / objective_scale
                        trial_projected = trial_scaled - np.clip(
                            trial_scaled - trial_scaled_derivative,
                            scaled_lower,
                            scaled_upper,
                        )
                        trial_projected_norm = float(np.max(np.abs(trial_projected)))
                        objective_resolution = (
                            32.0
                            * np.finfo(float).eps
                            * max(
                                1.0,
                                abs(value),
                                abs(trial_value),
                            )
                        )
                        if trial_value <= value + objective_resolution and trial_projected_norm < projected_norm:
                            vector = trial
                            value = trial_value
                            physical_value = trial_physical_value
                            accepted = True
                            break
        if not accepted or directional_derivative >= 0.0:
            break

    return Candidate(tuple(float(item) for item in vector), physical_value, converged, iterations, projected_norm)


def _complete_receipt(
    descriptor: FormulationDescriptor,
    seed: int,
    candidates: tuple[Candidate, ...],
    certificate_function: Callable[[FloatArray], Certificate],
    candidate_order: Callable[[Candidate, Certificate], tuple[object, ...]],
    backend: BackendIdentity,
) -> RunReceipt:
    converged_indices = tuple(index for index, candidate in enumerate(candidates) if candidate.converged)
    if not converged_indices:
        raise RuntimeError("no manufactured local start converged")
    certificate_slots: list[Certificate | None] = [None] * len(candidates)
    certified: list[tuple[Candidate, Certificate]] = []
    for index in converged_indices:
        candidate = candidates[index]
        certificate = certificate_function(np.asarray(candidate.vector, dtype=float))
        if certificate.formulation_id != descriptor.formulation_id:
            raise ValueError("certificate formulation_id does not match the executed formulation")
        if certificate.accepted and not certificate.independent_evidence:
            raise ValueError("an accepted certificate requires independent evidence")
        certificate_slots[index] = certificate
        certified.append((candidate, certificate))
    accepted = tuple(item for item in certified if item[1].accepted)
    selection_pool = accepted or tuple(certified)
    selected, certificate = min(selection_pool, key=lambda item: candidate_order(item[0], item[1]))
    return RunReceipt(
        formulation_id=descriptor.formulation_id,
        numerical_kind=descriptor.numerical_kind,
        backend=backend,
        seed=seed,
        candidates=candidates,
        candidate_certificates=tuple(certificate_slots),
        selected=selected,
        certificate=certificate,
    )


def run_direct(
    adapter: DirectAdapter,
    *,
    seed: int,
    tolerance: float = 1.0e-10,
    max_iterations: int = 2000,
) -> RunReceipt:
    if not isinstance(adapter, DirectAdapter):
        raise TypeError("run_direct requires a direct formulation adapter")
    if adapter.descriptor.numerical_kind is not NumericalKind.DIRECT_MINIMIZATION:
        raise TypeError("run_direct requires a direct formulation descriptor")
    problem = adapter.build()
    if problem.descriptor.formulation_id != adapter.descriptor.formulation_id:
        raise ValueError("problem formulation_id does not match the adapter")
    starts = adapter.starts(seed)
    if not starts:
        raise ValueError("at least one start is required")
    candidates = tuple(
        _local_minimize(
            problem.domain,
            problem.objective,
            problem.gradient,
            start,
            objective_scale=problem.objective_scale,
            tolerance=tolerance,
            max_iterations=max_iterations,
        )
        for start in starts
    )
    return _complete_receipt(
        adapter.descriptor,
        seed,
        candidates,
        adapter.certify,
        adapter.candidate_order,
        BackendIdentity(name="numpy_projected_gradient"),
    )


def _local_residual_solve(
    problem: ResidualProblem,
    start: object,
    *,
    tolerance: float,
    max_iterations: int,
) -> Candidate:
    vector = problem.domain.validate_vector(start, label="start")
    lower = problem.domain.lower_array
    upper = problem.domain.upper_array
    scale = np.asarray(problem.domain.scale, dtype=float)
    scaled_lower = lower / scale
    scaled_upper = upper / scale
    iterations = 0
    converged = False
    gradient_norm = math.inf
    merit = math.inf

    for iterations in range(max_iterations + 1):
        residual = np.asarray(problem.residual(vector), dtype=float)
        jacobian = np.asarray(problem.jacobian(vector), dtype=float)
        if residual.ndim != 1 or not np.all(np.isfinite(residual)):
            raise ValueError("residual callback must return a finite vector")
        if jacobian.shape != (residual.size, vector.size) or not np.all(np.isfinite(jacobian)):
            raise ValueError("residual Jacobian must be finite and have shape (residuals, variables)")
        merit = float(0.5 * np.dot(residual, residual))
        residual_scale = problem.scale_array(residual.size)
        scaled_residual = residual / residual_scale
        merit = float(0.5 * np.dot(scaled_residual, scaled_residual))
        residual_norm = float(np.max(np.abs(scaled_residual)))
        scaled_vector = vector / scale
        scaled_jacobian = jacobian * scale[np.newaxis, :] / residual_scale[:, np.newaxis]
        gradient = scaled_jacobian.T @ scaled_residual
        gradient_norm = float(np.max(np.abs(gradient)))
        if residual_norm <= tolerance:
            converged = True
            break
        if iterations == max_iterations:
            break

        direction = np.linalg.lstsq(scaled_jacobian, -scaled_residual, rcond=None)[0]
        step = 1.0
        accepted = False
        for _ in range(80):
            trial_scaled = np.clip(scaled_vector + step * direction, scaled_lower, scaled_upper)
            trial = trial_scaled * scale
            trial_residual = np.asarray(problem.residual(trial), dtype=float)
            if trial_residual.ndim != 1 or not np.all(np.isfinite(trial_residual)):
                step *= 0.5
                continue
            if trial_residual.shape != residual.shape:
                raise ValueError("residual dimension must remain constant")
            trial_scaled_residual = trial_residual / residual_scale
            trial_merit = float(0.5 * np.dot(trial_scaled_residual, trial_scaled_residual))
            if trial_merit < merit:
                vector = trial
                merit = trial_merit
                accepted = True
                break
            step *= 0.5
        if not accepted:
            break

    return Candidate(tuple(float(item) for item in vector), merit, converged, iterations, gradient_norm)


def run_residual(
    adapter: ResidualAdapter,
    *,
    seed: int,
    tolerance: float = 1.0e-10,
    max_iterations: int = 2000,
) -> RunReceipt:
    if not isinstance(adapter, ResidualAdapter):
        raise TypeError("run_residual requires a residual formulation adapter")
    if adapter.descriptor.numerical_kind is not NumericalKind.RESIDUAL_SOLVE:
        raise TypeError("run_residual requires a residual formulation descriptor")
    problem = adapter.build()
    if problem.descriptor.formulation_id != adapter.descriptor.formulation_id:
        raise ValueError("problem formulation_id does not match the adapter")

    starts = adapter.starts(seed)
    if not starts:
        raise ValueError("at least one start is required")
    candidates = tuple(
        _local_residual_solve(
            problem,
            start,
            tolerance=tolerance,
            max_iterations=max_iterations,
        )
        for start in starts
    )
    return _complete_receipt(
        adapter.descriptor,
        seed,
        candidates,
        adapter.certify,
        adapter.candidate_order,
        BackendIdentity(name="numpy_damped_gauss_newton"),
    )


def run_formulation(
    adapter: DirectAdapter | ResidualAdapter,
    *,
    seed: int,
    tolerance: float = 1.0e-10,
    max_iterations: int = 2000,
) -> RunReceipt:
    """Execute one nominal family through its declared numerical path."""

    if adapter.descriptor.numerical_kind is NumericalKind.DIRECT_MINIMIZATION:
        if not isinstance(adapter, DirectAdapter):
            raise TypeError("direct descriptor requires a direct formulation adapter")
        return run_direct(adapter, seed=seed, tolerance=tolerance, max_iterations=max_iterations)
    if adapter.descriptor.numerical_kind is NumericalKind.RESIDUAL_SOLVE:
        if not isinstance(adapter, ResidualAdapter):
            raise TypeError("residual descriptor requires a residual formulation adapter")
        return run_residual(adapter, seed=seed, tolerance=tolerance, max_iterations=max_iterations)
    raise ValueError("unsupported numerical kind")
