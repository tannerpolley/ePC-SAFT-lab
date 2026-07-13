from __future__ import annotations

import numpy as np
import pytest

from analyses.reference_oracles.equilibrium_formulations.families.neutral_held import (
    AssociationHeldAdapter,
    ManufacturedAssociationEvaluator,
    NeutralHeldAdapter,
    NeutralHeldSinglePhaseAdapter,
)
from analyses.reference_oracles.equilibrium_formulations.kernel import check_direct_derivatives, run_direct
from analyses.reference_oracles.neutral_held.oracle import PhaseSplit


def test_neutral_held_adapter_runs_direct_stage_three_and_matches_independent_global_evidence() -> None:
    adapter = NeutralHeldAdapter()
    result = run_direct(adapter, seed=1729)
    state = adapter.decode(np.asarray(result.selected.vector))

    assert state.phase_fraction == pytest.approx(0.5, abs=1.0e-10)
    assert (state.x_alpha, state.x_beta) == pytest.approx((0.2, 0.8), abs=1.0e-10)
    assert (state.v_alpha, state.v_beta) == pytest.approx((1.0, 1.0), abs=1.0e-10)
    assert abs(adapter.problem.material_residual(state)) < 1.0e-12
    assert result.certificate.accepted
    assert result.certificate.metrics["minimum_tangent_plane_distance"] > -1.0e-9
    assert result.certificate.metrics["enumeration_objective_gap"] < 1.0e-9


def test_neutral_held_single_phase_active_set_runs_through_the_same_kernel_facade() -> None:
    adapter = NeutralHeldSinglePhaseAdapter()
    result = run_direct(adapter, seed=1729)

    assert result.selected.vector == pytest.approx([0.994], abs=1.0e-9)
    assert result.selected.iterations > 0
    assert result.certificate.accepted
    assert result.certificate.metrics["single_phase_active_set"] == 1.0
    assert result.certificate.metrics["minimum_tangent_plane_distance"] > -1.0e-9
    assert result.certificate.metrics["enumeration_objective_gap"] < 1.0e-9


def test_neutral_held_metastable_converged_basin_is_rejected_by_global_certificate() -> None:
    result = run_direct(NeutralHeldAdapter(), seed=11)
    rejected = [
        (candidate, certificate)
        for candidate, certificate in zip(result.candidates, result.candidate_certificates, strict=True)
        if certificate is not None and not certificate.accepted
    ]

    assert rejected
    assert any(candidate.converged for candidate, _certificate in rejected)
    assert any(
        certificate.metrics["minimum_tangent_plane_distance"] < -0.1
        and certificate.metrics["enumeration_objective_gap"] > 0.1
        for _candidate, certificate in rejected
    )


def test_neutral_held_reduced_gradient_matches_central_differences() -> None:
    adapter = NeutralHeldAdapter()
    receipt = check_direct_derivatives(adapter.build(), np.asarray([0.27, 0.73, 0.92, 1.08]))

    assert receipt.max_abs_error < 5.0e-7


def test_neutral_held_objective_is_invariant_to_phase_relabeling() -> None:
    adapter = NeutralHeldAdapter()
    state = adapter.decode(np.asarray([0.27, 0.73, 0.92, 1.08]))
    swapped = PhaseSplit(
        phase_fraction=1.0 - state.phase_fraction,
        x_alpha=state.x_beta,
        v_alpha=state.v_beta,
        x_beta=state.x_alpha,
        v_beta=state.v_alpha,
    )

    assert adapter.problem.objective_value(state) == pytest.approx(adapter.problem.objective_value(swapped))
    assert adapter.problem.material_residual(swapped) == pytest.approx(0.0, abs=1.0e-14)


def test_association_inner_state_and_implicit_derivative_are_independently_checkable() -> None:
    evaluator = ManufacturedAssociationEvaluator()
    composition = 0.31
    volume = 1.07
    state = evaluator.solve_association(composition, volume)
    sensitivity = evaluator.association_sensitivity(composition, volume)
    step = 1.0e-6
    numerical = np.asarray(
        [
            (
                evaluator.solve_association(composition + step, volume)
                - evaluator.solve_association(composition - step, volume)
            )
            / (2.0 * step),
            (
                evaluator.solve_association(composition, volume + step)
                - evaluator.solve_association(composition, volume - step)
            )
            / (2.0 * step),
        ]
    )

    assert evaluator.association_residual(composition, volume, state) == pytest.approx(0.0, abs=1.0e-14)
    assert sensitivity == pytest.approx(numerical, abs=1.0e-10)
    assert evaluator.gradient(composition, volume) == pytest.approx(
        evaluator.base.gradient(composition, volume),
        abs=1.0e-12,
    )
    assert (
        np.max(np.abs(evaluator.frozen_state_gradient(composition, volume) - evaluator.gradient(composition, volume)))
        > 1.0e-3
    )


def test_association_held_uses_the_same_outer_solution_with_an_augmented_inner_certificate() -> None:
    result = run_direct(AssociationHeldAdapter(), seed=1729)

    assert result.selected.vector == pytest.approx([0.2, 0.8, 1.0, 1.0], abs=1.0e-10)
    assert result.certificate.accepted
    assert result.certificate.metrics["association_residual_inf_norm"] < 1.0e-12
    assert result.certificate.metrics["implicit_derivative_max_abs_error"] < 1.0e-9
    assert result.certificate.metrics["reduced_energy_derivative_max_abs_error"] < 1.0e-7


def test_stale_association_state_and_singular_inner_jacobian_fail_explicitly() -> None:
    evaluator = ManufacturedAssociationEvaluator()
    state = evaluator.solve_association(0.3, 1.0)

    assert not evaluator.association_state_is_accepted(0.4, 1.0, state)
    with pytest.raises(ValueError, match="singular"):
        ManufacturedAssociationEvaluator(residual_scale=0.0).solve_association(0.3, 1.0)
