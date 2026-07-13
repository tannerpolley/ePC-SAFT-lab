"""Non-production neutral HELD direct-minimization reference oracle.

The local solver minimizes the prescribed two-phase total free energy on an
exact material-balance manifold.  A separate low-dimensional enumeration uses
only objective values and provides independent evidence about globality.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, replace
from typing import Protocol

import numpy as np
from numpy.typing import NDArray

FloatArray = NDArray[np.float64]


class PhaseEvaluator(Protocol):
    """Small evaluator seam for a future EOS adapter."""

    def molar_helmholtz(self, composition: float, molar_volume: float) -> float:
        """Return a manufactured molar Helmholtz free energy."""

    def gradient(self, composition: float, molar_volume: float) -> FloatArray:
        """Return derivatives with respect to composition and molar volume."""

    def hessian(self, composition: float, molar_volume: float) -> FloatArray:
        """Return the corresponding two-by-two Hessian."""


@dataclass(frozen=True)
class ManufacturedTripleWellEvaluator:
    """Symmetric triple-well composition energy plus a quadratic volume term."""

    scale: float = 1.0e4
    inner_stationary_offset: float = 0.15
    outer_well_offset: float = 0.30
    volume_curvature: float = 5.0
    reference_volume: float = 1.20

    def _validate(self, composition: float, molar_volume: float) -> None:
        if not math.isfinite(composition) or not 0.0 <= composition <= 1.0:
            raise ValueError("composition must be finite and in [0, 1]")
        if not math.isfinite(molar_volume) or molar_volume <= 0.0:
            raise ValueError("molar_volume must be finite and positive")

    def molar_helmholtz(self, composition: float, molar_volume: float) -> float:
        self._validate(composition, molar_volume)
        t = composition - 0.5
        a2 = self.inner_stationary_offset**2
        b2 = self.outer_well_offset**2
        composition_energy = self.scale * (t**6 / 6.0 - (a2 + b2) * t**4 / 4.0 + a2 * b2 * t**2 / 2.0)
        volume_energy = 0.5 * self.volume_curvature * (molar_volume - self.reference_volume) ** 2
        return float(composition_energy + volume_energy)

    def gradient(self, composition: float, molar_volume: float) -> FloatArray:
        self._validate(composition, molar_volume)
        t = composition - 0.5
        a2 = self.inner_stationary_offset**2
        b2 = self.outer_well_offset**2
        derivative_x = self.scale * (t**5 - (a2 + b2) * t**3 + a2 * b2 * t)
        derivative_v = self.volume_curvature * (molar_volume - self.reference_volume)
        return np.asarray([derivative_x, derivative_v], dtype=float)

    def hessian(self, composition: float, molar_volume: float) -> FloatArray:
        self._validate(composition, molar_volume)
        t = composition - 0.5
        a2 = self.inner_stationary_offset**2
        b2 = self.outer_well_offset**2
        curvature_x = self.scale * (5.0 * t**4 - 3.0 * (a2 + b2) * t**2 + a2 * b2)
        return np.asarray(
            [[curvature_x, 0.0], [0.0, self.volume_curvature]],
            dtype=float,
        )


@dataclass(frozen=True)
class PhaseSplit:
    """Two candidate phases on a one-mole binary basis."""

    phase_fraction: float
    x_alpha: float
    v_alpha: float
    x_beta: float
    v_beta: float
    objective: float = math.nan

    @property
    def vector(self) -> FloatArray:
        return np.asarray(
            [
                self.phase_fraction,
                self.x_alpha,
                self.v_alpha,
                self.x_beta,
                self.v_beta,
            ],
            dtype=float,
        )

    @property
    def topology(self) -> str:
        if self.phase_fraction <= 1.0e-10 or self.phase_fraction >= 1.0 - 1.0e-10:
            return "single_phase"
        if abs(self.x_alpha - self.x_beta) <= 1.0e-10 and abs(self.v_alpha - self.v_beta) <= 1.0e-10:
            return "duplicate_single_phase"
        return "two_phase"

    @property
    def total_volume(self) -> float:
        return self.phase_fraction * self.v_alpha + (1.0 - self.phase_fraction) * self.v_beta


@dataclass(frozen=True)
class NeutralHeldProblem:
    """Fixed-temperature, fixed-pressure binary direct-minimization problem."""

    evaluator: PhaseEvaluator
    feed_composition: float
    pressure: float
    volume_bounds: tuple[float, float]

    def __post_init__(self) -> None:
        if not math.isfinite(self.feed_composition) or not 0.0 <= self.feed_composition <= 1.0:
            raise ValueError("feed_composition must be finite and in [0, 1]")
        if not math.isfinite(self.pressure) or self.pressure <= 0.0:
            raise ValueError("pressure must be finite and positive")
        lower, upper = self.volume_bounds
        if not (math.isfinite(lower) and math.isfinite(upper) and 0.0 < lower < upper):
            raise ValueError("volume_bounds must be finite, positive, and increasing")

    def validate_state(self, state: PhaseSplit) -> None:
        vector = state.vector
        if not np.all(np.isfinite(vector)):
            raise ValueError("phase state must contain only finite values")
        if not 0.0 <= state.phase_fraction <= 1.0:
            raise ValueError("phase_fraction must be in [0, 1]")
        if not 0.0 <= state.x_alpha <= 1.0 or not 0.0 <= state.x_beta <= 1.0:
            raise ValueError("phase compositions must be in [0, 1]")
        lower, upper = self.volume_bounds
        if not lower <= state.v_alpha <= upper or not lower <= state.v_beta <= upper:
            raise ValueError("phase molar volumes must lie within volume_bounds")

    def phase_gibbs(self, composition: float, molar_volume: float) -> float:
        return self.evaluator.molar_helmholtz(composition, molar_volume) + self.pressure * molar_volume

    def phase_gibbs_gradient(self, composition: float, molar_volume: float) -> FloatArray:
        gradient = self.evaluator.gradient(composition, molar_volume).copy()
        gradient[1] += self.pressure
        return gradient

    def objective_value(self, state: PhaseSplit) -> float:
        self.validate_state(state)
        beta = state.phase_fraction
        return float(
            beta * self.phase_gibbs(state.x_alpha, state.v_alpha)
            + (1.0 - beta) * self.phase_gibbs(state.x_beta, state.v_beta)
        )

    def with_objective(self, state: PhaseSplit) -> PhaseSplit:
        return replace(state, objective=self.objective_value(state))

    def material_residual(self, state: PhaseSplit) -> float:
        beta = state.phase_fraction
        return float(beta * state.x_alpha + (1.0 - beta) * state.x_beta - self.feed_composition)

    def constraint_jacobian(self, state: PhaseSplit) -> FloatArray:
        beta = state.phase_fraction
        return np.asarray(
            [state.x_alpha - state.x_beta, beta, 0.0, 1.0 - beta, 0.0],
            dtype=float,
        )

    def objective_gradient(self, state: PhaseSplit) -> FloatArray:
        self.validate_state(state)
        beta = state.phase_fraction
        g_alpha = self.phase_gibbs(state.x_alpha, state.v_alpha)
        g_beta = self.phase_gibbs(state.x_beta, state.v_beta)
        grad_alpha = self.phase_gibbs_gradient(state.x_alpha, state.v_alpha)
        grad_beta = self.phase_gibbs_gradient(state.x_beta, state.v_beta)
        return np.asarray(
            [
                g_alpha - g_beta,
                beta * grad_alpha[0],
                beta * grad_alpha[1],
                (1.0 - beta) * grad_beta[0],
                (1.0 - beta) * grad_beta[1],
            ],
            dtype=float,
        )

    def pressure_residuals(self, state: PhaseSplit) -> FloatArray:
        residuals = [-self.evaluator.gradient(state.x_alpha, state.v_alpha)[1] - self.pressure]
        if state.topology != "single_phase":
            residuals.append(-self.evaluator.gradient(state.x_beta, state.v_beta)[1] - self.pressure)
        return np.asarray(residuals, dtype=float)


@dataclass(frozen=True)
class DerivativeReceipt:
    evaluator_gradient_max_abs: float
    evaluator_hessian_max_abs: float
    objective_gradient_max_abs: float
    constraint_jacobian_max_abs: float
    reduced_objective_gradient_max_abs: float


@dataclass(frozen=True)
class LocalResult:
    state: PhaseSplit
    converged: bool
    iterations: int
    reduced_gradient_inf_norm: float


@dataclass(frozen=True)
class EquilibriumCertificate:
    material_balance_abs: float
    pressure_stationarity_inf_norm: float
    kkt_stationarity_inf_norm: float
    potential_gap: float
    common_tangent_gap: float
    minimum_tangent_plane_distance: float
    enumeration_objective_gap: float
    global_evidence: bool


@dataclass(frozen=True)
class SolverIdentity:
    name: str
    ipopt_available: bool
    used_fallback: bool
    availability_note: str


@dataclass(frozen=True)
class OracleResult:
    selected: PhaseSplit
    local_candidates: tuple[PhaseSplit, ...]
    enumerated_global: PhaseSplit
    certificate: EquilibriumCertificate
    solver: SolverIdentity
    seed: int


class GlobalEvidenceError(RuntimeError):
    """Raised when no direct-minimization candidate agrees with enumeration."""


def _state_from_vector(vector: FloatArray) -> PhaseSplit:
    return PhaseSplit(
        phase_fraction=float(vector[0]),
        x_alpha=float(vector[1]),
        v_alpha=float(vector[2]),
        x_beta=float(vector[3]),
        v_beta=float(vector[4]),
    )


def _central_difference_scalar(function: object, point: FloatArray, step: float) -> FloatArray:
    values = np.empty(point.size, dtype=float)
    for index in range(point.size):
        delta = np.zeros_like(point)
        delta[index] = step
        values[index] = (function(point + delta) - function(point - delta)) / (2.0 * step)  # type: ignore[operator]
    return values


def check_derivatives(
    problem: NeutralHeldProblem,
    state: PhaseSplit,
    *,
    step: float = 1.0e-6,
) -> DerivativeReceipt:
    """Compare analytic evaluator/problem derivatives with central differences."""

    if step <= 0.0:
        raise ValueError("step must be positive")
    problem.validate_state(state)

    evaluator_gradient_errors: list[float] = []
    evaluator_hessian_errors: list[float] = []
    for composition, volume in (
        (state.x_alpha, state.v_alpha),
        (state.x_beta, state.v_beta),
    ):
        point = np.asarray([composition, volume], dtype=float)

        def energy(candidate: FloatArray) -> float:
            return problem.evaluator.molar_helmholtz(float(candidate[0]), float(candidate[1]))

        finite_gradient = _central_difference_scalar(energy, point, step)
        analytic_gradient = problem.evaluator.gradient(composition, volume)
        evaluator_gradient_errors.append(float(np.max(np.abs(finite_gradient - analytic_gradient))))

        finite_hessian = np.column_stack(
            [
                (
                    problem.evaluator.gradient(*(point + step * np.eye(2)[axis]))
                    - problem.evaluator.gradient(*(point - step * np.eye(2)[axis]))
                )
                / (2.0 * step)
                for axis in range(2)
            ]
        )
        analytic_hessian = problem.evaluator.hessian(composition, volume)
        evaluator_hessian_errors.append(float(np.max(np.abs(finite_hessian - analytic_hessian))))

    vector = state.vector

    def objective(candidate: FloatArray) -> float:
        return problem.objective_value(_state_from_vector(candidate))

    def constraint(candidate: FloatArray) -> float:
        return problem.material_residual(_state_from_vector(candidate))

    objective_error = np.max(
        np.abs(_central_difference_scalar(objective, vector, step) - problem.objective_gradient(state))
    )
    constraint_error = np.max(
        np.abs(_central_difference_scalar(constraint, vector, step) - problem.constraint_jacobian(state))
    )

    reduced = _reduced_vector(problem, state)

    def reduced_objective(candidate: FloatArray) -> float:
        expanded = _expand_reduced(problem, candidate)
        if expanded is None:
            raise ValueError("perturbed point left the feasible reduced domain")
        return problem.objective_value(expanded)

    reduced_error = np.max(
        np.abs(_central_difference_scalar(reduced_objective, reduced, step) - _reduced_gradient(problem, state))
    )
    return DerivativeReceipt(
        evaluator_gradient_max_abs=max(evaluator_gradient_errors),
        evaluator_hessian_max_abs=max(evaluator_hessian_errors),
        objective_gradient_max_abs=float(objective_error),
        constraint_jacobian_max_abs=float(constraint_error),
        reduced_objective_gradient_max_abs=float(reduced_error),
    )


def _reduced_vector(problem: NeutralHeldProblem, state: PhaseSplit) -> FloatArray:
    if not 0.0 < state.phase_fraction < 1.0:
        raise ValueError("local two-phase minimization requires an interior phase_fraction")
    if abs(problem.material_residual(state)) > 1.0e-10:
        raise ValueError("local start must satisfy the material balance exactly")
    return np.asarray(
        [state.phase_fraction, state.x_alpha, state.v_alpha, state.v_beta],
        dtype=float,
    )


def _expand_reduced(problem: NeutralHeldProblem, reduced: FloatArray) -> PhaseSplit | None:
    beta, x_alpha, v_alpha, v_beta = (float(value) for value in reduced)
    lower, upper = problem.volume_bounds
    if not 1.0e-8 < beta < 1.0 - 1.0e-8:
        return None
    if not -1.0e-12 <= x_alpha <= 1.0 + 1.0e-12:
        return None
    if not lower <= v_alpha <= upper or not lower <= v_beta <= upper:
        return None
    x_beta = (problem.feed_composition - beta * x_alpha) / (1.0 - beta)
    if not -1.0e-12 <= x_beta <= 1.0 + 1.0e-12:
        return None
    return PhaseSplit(
        beta,
        min(1.0, max(0.0, x_alpha)),
        v_alpha,
        min(1.0, max(0.0, x_beta)),
        v_beta,
    )


def _reduced_gradient(problem: NeutralHeldProblem, state: PhaseSplit) -> FloatArray:
    beta = state.phase_fraction
    complement = 1.0 - beta
    g_alpha = problem.phase_gibbs(state.x_alpha, state.v_alpha)
    g_beta = problem.phase_gibbs(state.x_beta, state.v_beta)
    grad_alpha = problem.phase_gibbs_gradient(state.x_alpha, state.v_alpha)
    grad_beta = problem.phase_gibbs_gradient(state.x_beta, state.v_beta)
    return np.asarray(
        [
            g_alpha - g_beta + grad_beta[0] * (problem.feed_composition - state.x_alpha) / complement,
            beta * (grad_alpha[0] - grad_beta[0]),
            beta * grad_alpha[1],
            complement * grad_beta[1],
        ],
        dtype=float,
    )


def local_minimize(
    problem: NeutralHeldProblem,
    initial: PhaseSplit,
    *,
    gradient_tolerance: float = 5.0e-8,
    max_iterations: int = 500,
) -> LocalResult:
    """Locally minimize the direct objective on the exact balance manifold."""

    problem.validate_state(initial)
    reduced = _reduced_vector(problem, initial)
    state = _expand_reduced(problem, reduced)
    assert state is not None
    iterations = 0
    converged = False

    for iterations in range(max_iterations + 1):
        gradient = _reduced_gradient(problem, state)
        gradient_norm = float(np.max(np.abs(gradient)))
        if gradient_norm <= gradient_tolerance:
            converged = True
            break
        if iterations == max_iterations:
            break

        objective = problem.objective_value(state)
        direction = -gradient
        directional_norm = float(np.dot(gradient, gradient))
        step = 1.0
        accepted = False
        for _ in range(80):
            candidate_reduced = reduced + step * direction
            candidate = _expand_reduced(problem, candidate_reduced)
            if candidate is not None:
                candidate_objective = problem.objective_value(candidate)
                if candidate_objective <= objective - 1.0e-4 * step * directional_norm:
                    reduced = candidate_reduced
                    state = candidate
                    accepted = True
                    break
            step *= 0.5
        if not accepted:
            break

    final_gradient_norm = float(np.max(np.abs(_reduced_gradient(problem, state))))
    return LocalResult(
        state=problem.with_objective(state),
        converged=converged,
        iterations=iterations,
        reduced_gradient_inf_norm=final_gradient_norm,
    )


def _enumerated_phase_curve(
    problem: NeutralHeldProblem,
    compositions: FloatArray,
    volumes: FloatArray,
) -> tuple[FloatArray, FloatArray]:
    energies = np.empty(compositions.size, dtype=float)
    minimizing_volumes = np.empty(compositions.size, dtype=float)
    for index, composition in enumerate(compositions):
        values = np.fromiter(
            (problem.phase_gibbs(float(composition), float(volume)) for volume in volumes),
            dtype=float,
            count=volumes.size,
        )
        minimum_index = int(np.argmin(values))
        energies[index] = values[minimum_index]
        minimizing_volumes[index] = volumes[minimum_index]
    return energies, minimizing_volumes


def _pair_state_from_coordinates(
    problem: NeutralHeldProblem,
    coordinates: FloatArray,
) -> PhaseSplit | None:
    x_alpha, v_alpha, x_beta, v_beta = (float(value) for value in coordinates)
    feed = problem.feed_composition
    lower, upper = problem.volume_bounds
    if not 0.0 <= x_alpha < feed < x_beta <= 1.0:
        return None
    if not lower <= v_alpha <= upper or not lower <= v_beta <= upper:
        return None
    phase_fraction = (x_beta - feed) / (x_beta - x_alpha)
    state = PhaseSplit(phase_fraction, x_alpha, v_alpha, x_beta, v_beta)
    return problem.with_objective(state)


def _refine_enumerated_candidate(
    problem: NeutralHeldProblem,
    candidate: PhaseSplit,
    *,
    composition_step: float,
    volume_step: float,
) -> PhaseSplit:
    """Refine a coarse enumeration result using objective values only."""

    improvement_tolerance = 1.0e-14
    coordinate_tolerance = 1.0e-11
    if candidate.topology == "single_phase":
        volume = candidate.v_alpha
        step = volume_step
        best = candidate
        while step > coordinate_tolerance:
            improved = False
            for direction in (-1.0, 1.0):
                trial_volume = volume + direction * step
                if not problem.volume_bounds[0] <= trial_volume <= problem.volume_bounds[1]:
                    continue
                trial = problem.with_objective(
                    PhaseSplit(
                        1.0,
                        problem.feed_composition,
                        trial_volume,
                        problem.feed_composition,
                        trial_volume,
                    )
                )
                if trial.objective < best.objective - improvement_tolerance:
                    volume = trial_volume
                    best = trial
                    improved = True
                    break
            if not improved:
                step *= 0.5
        return best

    coordinates = np.asarray(
        [candidate.x_alpha, candidate.v_alpha, candidate.x_beta, candidate.v_beta],
        dtype=float,
    )
    steps = np.asarray(
        [composition_step, volume_step, composition_step, volume_step],
        dtype=float,
    )
    best = candidate
    for _ in range(20_000):
        if float(np.max(steps)) <= coordinate_tolerance:
            break
        improved = False
        for index in range(coordinates.size):
            for direction in (-1.0, 1.0):
                trial_coordinates = coordinates.copy()
                trial_coordinates[index] += direction * steps[index]
                trial = _pair_state_from_coordinates(problem, trial_coordinates)
                if trial is not None and trial.objective < best.objective - improvement_tolerance:
                    coordinates = trial_coordinates
                    best = trial
                    improved = True
                    break
            if improved:
                break
        if not improved:
            steps *= 0.5
    return best


def enumerate_global(
    problem: NeutralHeldProblem,
    *,
    composition_points: int = 301,
    volume_points: int = 51,
) -> PhaseSplit:
    """Enumerate the one- and two-phase objective without using derivatives."""

    if composition_points < 101 or composition_points % 2 == 0:
        raise ValueError("composition_points must be an odd integer of at least 101")
    if volume_points < 21 or volume_points % 2 == 0:
        raise ValueError("volume_points must be an odd integer of at least 21")

    compositions = np.linspace(0.0, 1.0, composition_points)
    volumes = np.linspace(*problem.volume_bounds, volume_points)
    curve, minimizing_volumes = _enumerated_phase_curve(problem, compositions, volumes)

    feed_values = np.fromiter(
        (problem.phase_gibbs(problem.feed_composition, float(volume)) for volume in volumes),
        dtype=float,
        count=volumes.size,
    )
    feed_volume_index = int(np.argmin(feed_values))
    best = PhaseSplit(
        phase_fraction=1.0,
        x_alpha=problem.feed_composition,
        v_alpha=float(volumes[feed_volume_index]),
        x_beta=problem.feed_composition,
        v_beta=float(volumes[feed_volume_index]),
        objective=float(feed_values[feed_volume_index]),
    )

    feed = problem.feed_composition
    for left_index in np.flatnonzero(compositions < feed):
        right_indices = np.flatnonzero(compositions > feed)
        if right_indices.size == 0:
            continue
        x_left = compositions[left_index]
        x_right = compositions[right_indices]
        fractions = (x_right - feed) / (x_right - x_left)
        objectives = fractions * curve[left_index] + (1.0 - fractions) * curve[right_indices]
        local_index = int(np.argmin(objectives))
        objective = float(objectives[local_index])
        if objective < best.objective:
            right_index = int(right_indices[local_index])
            best = PhaseSplit(
                phase_fraction=float(fractions[local_index]),
                x_alpha=float(x_left),
                v_alpha=float(minimizing_volumes[left_index]),
                x_beta=float(compositions[right_index]),
                v_beta=float(minimizing_volumes[right_index]),
                objective=objective,
            )
    return _refine_enumerated_candidate(
        problem,
        best,
        composition_step=1.0 / (composition_points - 1),
        volume_step=(problem.volume_bounds[1] - problem.volume_bounds[0]) / (volume_points - 1),
    )


def _minimum_tangent_plane_distance(
    problem: NeutralHeldProblem,
    state: PhaseSplit,
    *,
    composition_points: int = 301,
    volume_points: int = 51,
) -> float:
    compositions = np.linspace(0.0, 1.0, composition_points)
    volumes = np.linspace(*problem.volume_bounds, volume_points)
    curve, minimizing_volumes = _enumerated_phase_curve(problem, compositions, volumes)
    reference_x = state.x_alpha
    reference_g = problem.phase_gibbs(state.x_alpha, state.v_alpha)
    reference_slope = problem.phase_gibbs_gradient(state.x_alpha, state.v_alpha)[0]
    tangent = reference_g + reference_slope * (compositions - reference_x)
    coarse_values = curve - tangent
    coarse_index = int(np.argmin(coarse_values))
    coordinates = np.asarray(
        [compositions[coarse_index], minimizing_volumes[coarse_index]],
        dtype=float,
    )
    steps = np.asarray(
        [
            1.0 / (composition_points - 1),
            (problem.volume_bounds[1] - problem.volume_bounds[0]) / (volume_points - 1),
        ],
        dtype=float,
    )

    def tangent_plane_distance(point: FloatArray) -> float:
        composition, volume = (float(value) for value in point)
        return float(
            problem.phase_gibbs(composition, volume) - reference_g - reference_slope * (composition - reference_x)
        )

    best = tangent_plane_distance(coordinates)
    for _ in range(10_000):
        if float(np.max(steps)) <= 1.0e-11:
            break
        improved = False
        for index in range(coordinates.size):
            for direction in (-1.0, 1.0):
                trial = coordinates.copy()
                trial[index] += direction * steps[index]
                if not 0.0 <= trial[0] <= 1.0:
                    continue
                if not problem.volume_bounds[0] <= trial[1] <= problem.volume_bounds[1]:
                    continue
                value = tangent_plane_distance(trial)
                if value < best - 1.0e-14:
                    coordinates = trial
                    best = value
                    improved = True
                    break
            if improved:
                break
        if not improved:
            steps *= 0.5
    return best


def diagnose_candidate(
    problem: NeutralHeldProblem,
    candidate: PhaseSplit,
    enumerated_global: PhaseSplit,
    *,
    tolerance: float = 1.0e-8,
) -> EquilibriumCertificate:
    """Build KKT, pressure, tangent-plane, and enumeration diagnostics."""

    candidate = problem.with_objective(candidate)
    material = abs(problem.material_residual(candidate))
    pressure_norm = float(np.max(np.abs(problem.pressure_residuals(candidate))))

    if candidate.topology == "single_phase":
        active_gradient = problem.phase_gibbs_gradient(candidate.x_alpha, candidate.v_alpha)
        kkt_norm = abs(float(active_gradient[1]))
        potential_gap = 0.0
        common_tangent_gap = 0.0
    else:
        objective_gradient = problem.objective_gradient(candidate)
        constraint_jacobian = problem.constraint_jacobian(candidate)
        multiplier = -float(np.dot(constraint_jacobian, objective_gradient)) / float(
            np.dot(constraint_jacobian, constraint_jacobian)
        )
        kkt_norm = float(np.max(np.abs(objective_gradient + multiplier * constraint_jacobian)))
        grad_alpha = problem.phase_gibbs_gradient(candidate.x_alpha, candidate.v_alpha)
        grad_beta = problem.phase_gibbs_gradient(candidate.x_beta, candidate.v_beta)
        potential_gap = abs(float(grad_alpha[0] - grad_beta[0]))
        if abs(candidate.x_beta - candidate.x_alpha) <= 1.0e-12:
            common_tangent_gap = 0.0
        else:
            secant = (
                problem.phase_gibbs(candidate.x_beta, candidate.v_beta)
                - problem.phase_gibbs(candidate.x_alpha, candidate.v_alpha)
            ) / (candidate.x_beta - candidate.x_alpha)
            common_tangent_gap = abs(float(secant - grad_alpha[0]))

    minimum_tpd = _minimum_tangent_plane_distance(problem, candidate)
    enumeration_gap = float(candidate.objective - enumerated_global.objective)
    global_evidence = (
        material <= tolerance
        and pressure_norm <= tolerance
        and kkt_norm <= tolerance
        and potential_gap <= tolerance
        and common_tangent_gap <= tolerance
        and minimum_tpd >= -tolerance
        and abs(enumeration_gap) <= tolerance
    )
    return EquilibriumCertificate(
        material_balance_abs=material,
        pressure_stationarity_inf_norm=pressure_norm,
        kkt_stationarity_inf_norm=kkt_norm,
        potential_gap=potential_gap,
        common_tangent_gap=common_tangent_gap,
        minimum_tangent_plane_distance=minimum_tpd,
        enumeration_objective_gap=enumeration_gap,
        global_evidence=global_evidence,
    )


def _single_phase_candidate(problem: NeutralHeldProblem) -> PhaseSplit:
    volume = 0.5 * (problem.volume_bounds[0] + problem.volume_bounds[1])
    state = PhaseSplit(1.0, problem.feed_composition, volume, problem.feed_composition, volume)
    for _ in range(500):
        gradient = float(problem.phase_gibbs_gradient(problem.feed_composition, volume)[1])
        if abs(gradient) <= 1.0e-10:
            return problem.with_objective(state)
        objective = problem.phase_gibbs(problem.feed_composition, volume)
        step = 1.0
        accepted = False
        for _ in range(80):
            trial_volume = volume - step * gradient
            if problem.volume_bounds[0] <= trial_volume <= problem.volume_bounds[1]:
                trial_objective = problem.phase_gibbs(problem.feed_composition, trial_volume)
                if trial_objective <= objective - 1.0e-4 * step * gradient**2:
                    volume = trial_volume
                    state = PhaseSplit(
                        1.0,
                        problem.feed_composition,
                        volume,
                        problem.feed_composition,
                        volume,
                    )
                    accepted = True
                    break
            step *= 0.5
        if not accepted:
            break
    return problem.with_objective(state)


def _deterministic_starts(problem: NeutralHeldProblem, seed: int) -> tuple[PhaseSplit, ...]:
    feed = problem.feed_composition
    midpoint_volume = 0.5 * (problem.volume_bounds[0] + problem.volume_bounds[1])
    starts = [PhaseSplit(0.5, feed, midpoint_volume, feed, midpoint_volume)]

    anchors = np.linspace(0.0, 1.0, 6)
    for left in anchors:
        for right in anchors:
            if left < feed < right:
                fraction = (right - feed) / (right - left)
                if 1.0e-8 < fraction < 1.0 - 1.0e-8:
                    starts.append(
                        PhaseSplit(
                            float(fraction),
                            float(left),
                            midpoint_volume,
                            float(right),
                            midpoint_volume,
                        )
                    )

    rng = np.random.default_rng(seed)
    for _ in range(4):
        left = float(rng.uniform(0.0, feed)) if feed > 0.0 else 0.0
        right = float(rng.uniform(feed, 1.0)) if feed < 1.0 else 1.0
        if right - left <= 1.0e-12:
            continue
        fraction = (right - feed) / (right - left)
        if 1.0e-8 < fraction < 1.0 - 1.0e-8:
            starts.append(
                PhaseSplit(
                    float(fraction),
                    left,
                    midpoint_volume,
                    right,
                    midpoint_volume,
                )
            )
    return tuple(starts)


def solve_reference(
    problem: NeutralHeldProblem,
    *,
    seed: int = 1729,
    agreement_tolerance: float = 2.0e-7,
) -> OracleResult:
    """Run deterministic multistart and accept only enumeration-backed results."""

    candidates = [_single_phase_candidate(problem)]
    for start in _deterministic_starts(problem, seed):
        result = local_minimize(problem, start)
        if result.converged:
            candidates.append(result.state)

    unique: dict[tuple[float, ...], PhaseSplit] = {}
    for candidate in candidates:
        key = tuple(float(value) for value in np.round(candidate.vector, decimals=11))
        previous = unique.get(key)
        if previous is None or candidate.objective < previous.objective:
            unique[key] = candidate
    local_candidates = tuple(
        sorted(
            unique.values(),
            key=lambda candidate: (
                candidate.objective,
                *candidate.vector.tolist(),
            ),
        )
    )

    enumerated = enumerate_global(problem)
    matching = [
        candidate
        for candidate in local_candidates
        if abs(candidate.objective - enumerated.objective) <= agreement_tolerance
    ]
    if not matching:
        raise GlobalEvidenceError("no direct-minimization candidate agrees with the independent enumeration")
    certified = [
        (
            candidate,
            diagnose_candidate(
                problem,
                candidate,
                enumerated,
                tolerance=agreement_tolerance,
            ),
        )
        for candidate in matching
    ]
    certified = [(candidate, certificate) for candidate, certificate in certified if certificate.global_evidence]
    if not certified:
        raise GlobalEvidenceError("the selected local result failed its independent certificate")
    selected, certificate = min(
        certified,
        key=lambda item: (
            item[0].topology != "single_phase",
            abs(item[1].enumeration_objective_gap),
            item[1].kkt_stationarity_inf_norm,
        ),
    )

    solver = SolverIdentity(
        name="numpy_feasible_gradient",
        ipopt_available=False,
        used_fallback=False,
        availability_note=(
            "Ipopt is unavailable in this analysis area by repository policy; "
            "the declared NumPy solver is the only backend and no fallback was used."
        ),
    )
    return OracleResult(
        selected=selected,
        local_candidates=local_candidates,
        enumerated_global=enumerated,
        certificate=certificate,
        solver=solver,
        seed=seed,
    )
