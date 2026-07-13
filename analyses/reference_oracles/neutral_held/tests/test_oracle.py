from __future__ import annotations

import numpy as np
import pytest

from analyses.reference_oracles.neutral_held.oracle import (
    ManufacturedTripleWellEvaluator,
    NeutralHeldProblem,
    PhaseSplit,
    check_derivatives,
    diagnose_candidate,
    enumerate_global,
    local_minimize,
    solve_reference,
)


def _problem(
    feed: float,
    *,
    evaluator: ManufacturedTripleWellEvaluator | None = None,
    pressure: float = 1.0,
) -> NeutralHeldProblem:
    return NeutralHeldProblem(
        evaluator=evaluator or ManufacturedTripleWellEvaluator(),
        feed_composition=feed,
        pressure=pressure,
        volume_bounds=(0.5, 1.5),
    )


def test_analytic_derivatives_and_constraint_jacobian_match_finite_differences() -> None:
    problem = _problem(0.47)
    state = PhaseSplit(
        phase_fraction=0.55,
        x_alpha=0.31,
        v_alpha=0.91,
        x_beta=(0.47 - 0.55 * 0.31) / 0.45,
        v_beta=1.08,
    )

    receipt = check_derivatives(problem, state, step=1.0e-6)

    assert receipt.evaluator_gradient_max_abs < 2.0e-7
    assert receipt.evaluator_hessian_max_abs < 2.0e-5
    assert receipt.objective_gradient_max_abs < 2.0e-7
    assert receipt.constraint_jacobian_max_abs < 2.0e-10
    assert receipt.reduced_objective_gradient_max_abs < 2.0e-7


def test_two_phase_case_matches_independent_enumeration_and_certificates() -> None:
    result = solve_reference(_problem(0.5), seed=1729)
    selected = result.selected

    assert selected.topology == "two_phase"
    assert selected.phase_fraction == pytest.approx(0.5, abs=2.0e-8)
    assert sorted((selected.x_alpha, selected.x_beta)) == pytest.approx([0.2, 0.8], abs=2.0e-8)
    assert selected.v_alpha == pytest.approx(1.0, abs=2.0e-8)
    assert selected.v_beta == pytest.approx(1.0, abs=2.0e-8)
    assert result.certificate.material_balance_abs < 1.0e-12
    assert result.certificate.pressure_stationarity_inf_norm < 1.0e-10
    assert result.certificate.kkt_stationarity_inf_norm < 1.0e-9
    assert result.certificate.potential_gap < 1.0e-9
    assert result.certificate.common_tangent_gap < 1.0e-9
    assert result.certificate.minimum_tangent_plane_distance > -1.0e-9
    assert result.certificate.enumeration_objective_gap < 1.0e-10
    assert result.certificate.global_evidence
    assert selected.total_volume == pytest.approx(
        selected.phase_fraction * selected.v_alpha + (1.0 - selected.phase_fraction) * selected.v_beta
    )


def test_single_phase_global_boundary_case_is_retained() -> None:
    result = solve_reference(_problem(0.1, pressure=1.03), seed=1729)

    assert result.selected.topology == "single_phase"
    assert result.selected.x_alpha == pytest.approx(0.1, abs=1.0e-12)
    assert result.selected.v_alpha == pytest.approx(0.994, abs=2.0e-8)
    assert result.certificate.material_balance_abs < 1.0e-12
    assert result.certificate.minimum_tangent_plane_distance > -1.0e-9
    assert result.certificate.enumeration_objective_gap < 1.0e-10
    assert result.certificate.global_evidence


def test_off_grid_two_phase_and_volume_optima_are_refined_without_derivatives() -> None:
    evaluator = ManufacturedTripleWellEvaluator(outer_well_offset=0.293)
    result = solve_reference(_problem(0.5, evaluator=evaluator, pressure=1.03), seed=1729)

    assert result.selected.topology == "two_phase"
    assert result.selected.phase_fraction == pytest.approx(0.5, abs=2.0e-7)
    assert sorted((result.selected.x_alpha, result.selected.x_beta)) == pytest.approx(
        [0.207, 0.793],
        abs=2.0e-7,
    )
    assert result.selected.v_alpha == pytest.approx(0.994, abs=2.0e-7)
    assert result.selected.v_beta == pytest.approx(0.994, abs=2.0e-7)
    assert result.certificate.enumeration_objective_gap < 1.0e-8
    assert result.certificate.global_evidence


def test_metastable_duplicate_phase_local_minimum_fails_global_certificate() -> None:
    problem = _problem(0.5)
    metastable = PhaseSplit(
        phase_fraction=0.5,
        x_alpha=0.5,
        v_alpha=1.0,
        x_beta=0.5,
        v_beta=1.0,
    )

    local = local_minimize(problem, metastable)
    enumeration = enumerate_global(problem)
    certificate = diagnose_candidate(problem, local.state, enumeration)

    assert local.converged
    assert local.state.topology == "duplicate_single_phase"
    assert certificate.kkt_stationarity_inf_norm < 1.0e-10
    assert certificate.minimum_tangent_plane_distance < -0.1
    assert certificate.enumeration_objective_gap > 0.1
    assert not certificate.global_evidence


def test_invalid_inputs_and_infeasible_local_start_are_rejected() -> None:
    with pytest.raises(ValueError, match="feed_composition"):
        _problem(-0.01)
    with pytest.raises(ValueError, match="positive"):
        NeutralHeldProblem(
            evaluator=ManufacturedTripleWellEvaluator(),
            feed_composition=0.5,
            pressure=0.0,
            volume_bounds=(0.5, 1.5),
        )

    problem = _problem(0.5)
    infeasible = PhaseSplit(
        phase_fraction=0.5,
        x_alpha=0.2,
        v_alpha=1.0,
        x_beta=0.7,
        v_beta=1.0,
    )
    with pytest.raises(ValueError, match="material balance"):
        local_minimize(problem, infeasible)


def test_seeded_multistart_is_deterministic_and_solver_identity_is_explicit() -> None:
    first = solve_reference(_problem(0.5), seed=20260713)
    second = solve_reference(_problem(0.5), seed=20260713)

    assert first.selected == second.selected
    assert first.local_candidates == second.local_candidates
    assert first.solver.name == "numpy_feasible_gradient"
    assert first.solver.ipopt_available is False
    assert first.solver.used_fallback is False
    assert "repository policy" in first.solver.availability_note
    assert np.isfinite(first.selected.objective)
