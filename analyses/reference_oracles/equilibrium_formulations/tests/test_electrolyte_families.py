from __future__ import annotations

import numpy as np
import pytest

from analyses.reference_oracles.equilibrium_formulations.families.ascani_pairs import AscaniPairAdapter
from analyses.reference_oracles.equilibrium_formulations.families.perdomo_held2 import PerdomoHeld2Adapter
from analyses.reference_oracles.equilibrium_formulations.kernel import (
    check_direct_derivatives,
    check_residual_derivatives,
    run_direct,
    run_residual,
)


def test_perdomo_modified_mole_direct_problem_recovers_balances_charge_and_modified_potentials() -> None:
    adapter = PerdomoHeld2Adapter()
    result = run_direct(adapter, seed=1729)
    state = adapter.decode(np.asarray(result.selected.vector))

    assert result.selected.vector == pytest.approx([0.2, 0.8, 1.0, 1.0], abs=1.0e-10)
    assert state.phase_fraction == pytest.approx(0.5, abs=1.0e-10)
    assert result.certificate.accepted
    assert result.certificate.metrics["modified_balance_abs"] < 1.0e-12
    assert result.certificate.metrics["ordinary_balance_inf_norm"] < 1.0e-12
    assert result.certificate.metrics["phase_charge_inf_norm"] < 1.0e-12
    assert result.certificate.metrics["modified_potential_gap"] < 1.0e-9
    assert result.certificate.metrics["pressure_stationarity_inf_norm"] < 1.0e-10
    assert result.certificate.metrics["reduced_kkt_inf_norm"] < 1.0e-9
    assert result.certificate.metrics["independent_modified_composition_count"] == 1.0


def test_perdomo_reduced_gradient_matches_central_differences() -> None:
    adapter = PerdomoHeld2Adapter()

    assert check_direct_derivatives(adapter.build(), np.asarray([0.27, 0.73, 0.92, 1.08])).max_abs_error < 5.0e-7


def test_perdomo_galvani_shift_cancels_from_modified_potentials() -> None:
    adapter = PerdomoHeld2Adapter()
    chemical_potentials = np.asarray([3.0, -2.0, 4.0])

    baseline = adapter.modified_potentials(chemical_potentials, faraday_galvani_energy=0.0)
    shifted = adapter.modified_potentials(chemical_potentials, faraday_galvani_energy=17.0)

    assert shifted == pytest.approx(baseline, abs=1.0e-12)


def test_perdomo_recovery_rejects_negative_eliminated_ion_amount() -> None:
    with pytest.raises(ValueError, match="eliminated ion"):
        PerdomoHeld2Adapter().recover_physical_composition(-0.1)


def test_perdomo_modified_potentials_are_derivatives_of_the_extensive_modified_phase_gibbs() -> None:
    adapter = PerdomoHeld2Adapter()
    amounts = np.asarray([0.7, 0.3])
    volume = 0.93
    step = 1.0e-6
    u = float(amounts[1] / np.sum(amounts))
    analytic = adapter.phase_modified_potentials(u, volume / np.sum(amounts))
    numerical = np.empty(2)
    for index in range(2):
        delta = np.zeros(2)
        delta[index] = step
        numerical[index] = (
            adapter.extensive_phase_gibbs(amounts + delta, volume)
            - adapter.extensive_phase_gibbs(amounts - delta, volume)
        ) / (2.0 * step)

    assert analytic == pytest.approx(numerical, abs=2.0e-8)


def test_ascani_pair_residual_recovers_pair_transfers_balances_and_local_charge() -> None:
    adapter = AscaniPairAdapter()
    result = run_residual(adapter, seed=1729)

    assert result.selected.vector == pytest.approx([0.8, 0.3, 0.2], abs=1.0e-10)
    assert result.certificate.accepted
    assert result.certificate.metrics["pair_basis_rank"] == 2.0
    assert result.certificate.metrics["pair_basis_charge_null_inf_norm"] < 1.0e-12
    assert result.certificate.metrics["material_balance_inf_norm"] < 1.0e-12
    assert result.certificate.metrics["phase_charge_inf_norm"] < 1.0e-12
    assert result.certificate.metrics["pair_potential_gap"] < 1.0e-10


def test_ascani_residual_jacobian_matches_central_differences() -> None:
    adapter = AscaniPairAdapter()

    assert check_residual_derivatives(adapter.build(), np.asarray([0.9, 0.4, 0.3])).max_abs_error < 1.0e-9


def test_ascani_pair_potentials_are_galvani_gauge_invariant() -> None:
    adapter = AscaniPairAdapter()
    charged_chemical_potentials = np.asarray([2.0, -1.0, 4.0])

    baseline = adapter.pair_potentials(charged_chemical_potentials, faraday_galvani_energy=0.0)
    shifted = adapter.pair_potentials(charged_chemical_potentials, faraday_galvani_energy=-13.0)

    assert shifted == pytest.approx(baseline, abs=1.0e-12)


@pytest.mark.parametrize(
    ("phase", "amounts"),
    [("alpha", np.asarray([0.9, 0.35, 0.25])), ("beta", np.asarray([1.1, 0.65, 0.75]))],
)
def test_ascani_neutral_and_pair_potentials_derive_from_one_extensive_reduced_gibbs(
    phase: str,
    amounts: np.ndarray,
) -> None:
    adapter = AscaniPairAdapter()
    analytic = adapter.reduced_phase_potentials(amounts, phase=phase)
    numerical = np.empty(3)
    step = 1.0e-6
    for index in range(3):
        delta = np.zeros(3)
        delta[index] = step
        numerical[index] = (
            adapter.reduced_phase_gibbs(amounts + delta, phase=phase)
            - adapter.reduced_phase_gibbs(amounts - delta, phase=phase)
        ) / (2.0 * step)

    hessian = adapter.reduced_phase_hessian(amounts)
    numerical_hessian = np.column_stack(
        [
            (
                adapter.reduced_phase_potentials(amounts + step * np.eye(3)[index], phase=phase)
                - adapter.reduced_phase_potentials(amounts - step * np.eye(3)[index], phase=phase)
            )
            / (2.0 * step)
            for index in range(3)
        ]
    )
    assert analytic == pytest.approx(numerical, abs=1.0e-9)
    assert adapter.reduced_phase_gibbs(amounts, phase=phase) == pytest.approx(float(amounts @ analytic), abs=1.0e-12)
    assert hessian == pytest.approx(numerical_hessian, abs=1.0e-9)
    assert hessian == pytest.approx(hessian.T, abs=1.0e-14)


def test_ascani_pair_basis_change_preserves_zero_equilibrium_residual() -> None:
    adapter = AscaniPairAdapter()
    basis_change = np.asarray([[2.0, 1.0], [-1.0, 1.0]])
    transformed_basis = basis_change @ adapter.pair_matrix
    pair_amounts = np.asarray([0.3, 0.2])
    transformed_pair_amounts = np.linalg.solve(basis_change.T, pair_amounts)
    potential_difference = np.asarray([2.0, -1.0, 4.0])

    baseline = adapter.pair_matrix @ potential_difference
    transformed = transformed_basis @ potential_difference
    physical_amounts = adapter.pair_matrix.T @ pair_amounts
    transformed_physical_amounts = transformed_basis.T @ transformed_pair_amounts

    assert transformed == pytest.approx(basis_change @ baseline)
    assert transformed_physical_amounts == pytest.approx(physical_amounts)
    assert np.linalg.matrix_rank(transformed_basis) == 2


def test_rank_deficient_pair_basis_is_rejected_and_family_certificates_are_not_exchangeable() -> None:
    with pytest.raises(ValueError, match="rank"):
        AscaniPairAdapter(pair_rows=((1.0, 1.0, 0.0), (2.0, 2.0, 0.0)))

    held2 = run_direct(PerdomoHeld2Adapter(), seed=1)
    ascani = run_residual(AscaniPairAdapter(), seed=1)

    assert held2.certificate.formulation_id != ascani.certificate.formulation_id
