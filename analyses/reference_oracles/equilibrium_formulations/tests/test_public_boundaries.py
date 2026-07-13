from __future__ import annotations

import numpy as np
import pytest

from analyses.reference_oracles.equilibrium_formulations.families.public_boundaries import (
    BinaryBoundaryEvaluator,
    BoundaryKind,
    ManufacturedBoundaryAdapter,
    PureBoundaryEvaluator,
)
from analyses.reference_oracles.equilibrium_formulations.kernel import check_residual_derivatives, run_residual


@pytest.mark.parametrize(
    ("kind", "expected"),
    [
        (BoundaryKind.BUBBLE_PRESSURE, [2.0, 1.0, 3.0, 0.75, 0.25]),
        (BoundaryKind.DEW_PRESSURE, [2.0, 1.0, 3.0, 0.25, 0.75]),
        (BoundaryKind.PURE_SATURATION, [2.0, 1.0, 3.0]),
    ],
)
def test_manufactured_boundary_root_has_full_rank_and_family_certificate(
    kind: BoundaryKind,
    expected: list[float],
) -> None:
    adapter = ManufacturedBoundaryAdapter(kind)
    problem = adapter.build()
    result = run_residual(adapter, seed=1729)

    assert result.selected.vector == pytest.approx(expected, abs=2.0e-8)
    assert np.linalg.matrix_rank(problem.jacobian(np.asarray(expected))) == len(expected)
    assert np.max(np.abs(problem.residual(np.asarray(result.selected.vector)))) < 1.0e-8
    assert result.certificate.accepted
    assert result.certificate.metrics["volume_gap"] == pytest.approx(2.0)
    assert result.certificate.metrics["global_stability_claim"] == 0.0


@pytest.mark.parametrize("kind", list(BoundaryKind))
def test_boundary_jacobian_matches_central_differences(kind: BoundaryKind) -> None:
    adapter = ManufacturedBoundaryAdapter(kind)
    problem = adapter.build()
    point = np.asarray(adapter.starts(23)[0])

    receipt = check_residual_derivatives(problem, point)

    assert receipt.max_abs_error < 5.0e-9


def test_common_affine_species_reference_shift_does_not_change_boundary_root() -> None:
    baseline = run_residual(ManufacturedBoundaryAdapter(BoundaryKind.BUBBLE_PRESSURE), seed=9)
    shifted = run_residual(
        ManufacturedBoundaryAdapter(BoundaryKind.BUBBLE_PRESSURE, potential_shift=(17.0, -8.0)),
        seed=9,
    )

    assert shifted.selected.vector == pytest.approx(baseline.selected.vector, abs=1.0e-10)


def test_collapsed_boundary_volumes_fail_the_independent_topology_certificate() -> None:
    adapter = ManufacturedBoundaryAdapter(BoundaryKind.PURE_SATURATION)
    collapsed = np.asarray([2.0, 1.5, 1.5])

    certificate = adapter.certify(collapsed)

    assert not certificate.accepted
    assert certificate.metrics["volume_gap"] == 0.0


def test_boundary_adapter_rejects_nonpositive_pressure_and_reversed_volumes() -> None:
    adapter = ManufacturedBoundaryAdapter(BoundaryKind.PURE_SATURATION)

    assert not adapter.certify(np.asarray([0.0, 1.0, 3.0])).accepted
    assert not adapter.certify(np.asarray([2.0, 3.0, 1.0])).accepted


def test_binary_pressure_and_potentials_are_derivatives_of_one_extensive_helmholtz_function() -> None:
    evaluator = BinaryBoundaryEvaluator(potential_shift=(3.0, -2.0))
    amounts = np.asarray([0.4, 0.6])
    volume = 1.7
    step = 1.0e-6
    pressure, potentials = evaluator.properties(amounts[0] / np.sum(amounts), volume / np.sum(amounts))
    numerical_pressure = -(
        evaluator.extensive_helmholtz(volume + step, amounts) - evaluator.extensive_helmholtz(volume - step, amounts)
    ) / (2.0 * step)
    numerical_potentials = np.empty(2)
    for index in range(2):
        delta = np.zeros(2)
        delta[index] = step
        numerical_potentials[index] = (
            evaluator.extensive_helmholtz(volume, amounts + delta)
            - evaluator.extensive_helmholtz(volume, amounts - delta)
        ) / (2.0 * step)

    assert pressure == pytest.approx(numerical_pressure, abs=2.0e-8)
    assert potentials == pytest.approx(numerical_potentials, abs=2.0e-8)


def test_pure_pressure_and_potential_are_derivatives_of_one_extensive_helmholtz_function() -> None:
    evaluator = PureBoundaryEvaluator(potential_shift=4.0)
    amount = 1.3
    volume = 2.2 * amount
    step = 1.0e-6
    pressure, potential = evaluator.properties(volume / amount)
    numerical_pressure = -(
        evaluator.extensive_helmholtz(volume + step, amount) - evaluator.extensive_helmholtz(volume - step, amount)
    ) / (2.0 * step)
    numerical_potential = (
        evaluator.extensive_helmholtz(volume, amount + step) - evaluator.extensive_helmholtz(volume, amount - step)
    ) / (2.0 * step)

    assert pressure == pytest.approx(numerical_pressure, abs=2.0e-8)
    assert potential == pytest.approx(numerical_potential, abs=2.0e-8)
