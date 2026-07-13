from __future__ import annotations

import numpy as np
import pytest

from analyses.reference_oracles.equilibrium_formulations.families.chemical_equilibrium import (
    ChemicalEquilibriumAdapter,
)
from analyses.reference_oracles.equilibrium_formulations.families.coupled_phase_chemical import (
    CoupledPhaseChemicalAdapter,
    CoupledState,
)
from analyses.reference_oracles.equilibrium_formulations.kernel import check_direct_derivatives, run_direct


def test_standalone_ce_recovers_complete_reaction_equilibrium_and_element_balance() -> None:
    adapter = ChemicalEquilibriumAdapter()
    result = run_direct(adapter, seed=1729)

    assert result.selected.vector == pytest.approx([0.75], abs=1.0e-10)
    assert result.certificate.accepted
    assert result.certificate.metrics["element_balance_inf_norm"] < 1.0e-12
    assert result.certificate.metrics["affinity_inf_norm"] < 1.0e-10
    assert result.certificate.metrics["reaction_basis_rank"] == 1.0
    assert result.certificate.metrics["reaction_space_complete"] == 1.0
    assert result.certificate.metrics["objective_gap"] < 1.0e-12


def test_standalone_ce_derivative_and_reaction_basis_orientation_are_consistent() -> None:
    adapter = ChemicalEquilibriumAdapter()
    point = np.asarray([0.43])

    assert check_direct_derivatives(adapter.build(), point).max_abs_error < 1.0e-9
    assert adapter.build().gradient(point)[0] == pytest.approx(adapter.affinity(point), abs=1.0e-14)
    assert adapter.affinity(point, reaction_orientation=1.0) == pytest.approx(
        -adapter.affinity(point, reaction_orientation=-1.0)
    )


def test_standalone_ce_reversed_and_scaled_reaction_basis_preserves_physical_solution() -> None:
    forward = ChemicalEquilibriumAdapter(reaction_vector=(-1.0, 1.0))
    reversed_scaled = ChemicalEquilibriumAdapter(reaction_vector=(2.0, -2.0))
    forward_result = run_direct(forward, seed=1729)
    reversed_result = run_direct(reversed_scaled, seed=1729)
    forward_amounts = forward.amounts(np.asarray(forward_result.selected.vector))
    reversed_amounts = reversed_scaled.amounts(np.asarray(reversed_result.selected.vector))

    assert forward_result.selected.vector == pytest.approx([0.75], abs=1.0e-9)
    assert reversed_result.selected.vector == pytest.approx([0.125], abs=1.0e-9)
    assert reversed_amounts == pytest.approx(forward_amounts, abs=1.0e-9)
    assert reversed_amounts == pytest.approx(
        reversed_scaled.initial_amounts
        + reversed_scaled.stoichiometric_matrix[:, 0] * reversed_result.selected.vector[0],
        abs=1.0e-12,
    )
    reversed_point = np.asarray([0.2])
    assert reversed_scaled.build().gradient(reversed_point)[0] == pytest.approx(
        reversed_scaled.affinity(reversed_point),
        abs=1.0e-14,
    )
    assert forward_result.certificate.accepted
    assert reversed_result.certificate.accepted
    assert reversed_scaled.affinity(np.asarray(reversed_result.selected.vector)) == pytest.approx(0.0, abs=1.0e-9)


def test_standalone_ce_boundary_species_uses_complementarity_not_log_equality() -> None:
    result = run_direct(ChemicalEquilibriumAdapter(boundary_target=1.2), seed=1729)

    assert result.selected.vector == pytest.approx([1.0], abs=1.0e-10)
    assert result.certificate.accepted
    assert result.certificate.metrics["boundary_species_count"] == 1.0
    assert result.certificate.metrics["complementarity_inf_norm"] < 1.0e-12
    assert result.certificate.metrics["active_multiplier_min"] > 0.0
    assert result.certificate.metrics["affinity_inf_norm"] > 0.0


def test_incomplete_or_nonconserving_ce_reaction_basis_is_rejected() -> None:
    with pytest.raises(ValueError, match="conserve"):
        ChemicalEquilibriumAdapter(reaction_vector=(-1.0, 0.5))
    with pytest.raises(ValueError, match="complete"):
        ChemicalEquilibriumAdapter(reaction_vector=(0.0, 0.0))


def test_ce_chemical_potentials_are_extensive_gibbs_derivatives_and_satisfy_euler_identity() -> None:
    adapter = ChemicalEquilibriumAdapter(inventory_scale=2.3)
    amounts = np.asarray([0.7, 1.6])
    step = 1.0e-6
    potentials = adapter.chemical_potentials(amounts)
    numerical = np.empty(2)
    for index in range(2):
        delta = np.zeros(2)
        delta[index] = step
        numerical[index] = (adapter.gibbs(amounts + delta) - adapter.gibbs(amounts - delta)) / (2.0 * step)

    assert potentials == pytest.approx(numerical, abs=2.0e-9)
    assert adapter.gibbs(amounts) == pytest.approx(float(amounts @ potentials), abs=1.0e-12)


def test_cpe_recovers_simultaneous_phase_and_reaction_solution_with_global_lower_bound() -> None:
    adapter = CoupledPhaseChemicalAdapter()
    result = run_direct(adapter, seed=1729)
    state = adapter.decode(np.asarray(result.selected.vector))

    assert result.selected.vector == pytest.approx([0.2, 0.2, 1.0, 0.3, 0.6, 3.0], abs=1.0e-10)
    assert state.phase_fraction == pytest.approx(0.5, abs=1.0e-10)
    assert result.certificate.accepted
    assert result.certificate.metrics["element_balance_inf_norm"] < 1.0e-12
    assert result.certificate.metrics["interphase_potential_gap"] < 1.0e-12
    assert result.certificate.metrics["reaction_affinity_inf_norm"] < 1.0e-12
    assert result.certificate.metrics["pressure_stationarity_inf_norm"] < 1.0e-12
    assert result.certificate.metrics["global_lower_bound_gap"] < 1.0e-12
    assert result.certificate.metrics["reactive_tpd_complete"] == 0.0


def test_cpe_gradient_matches_central_differences() -> None:
    adapter = CoupledPhaseChemicalAdapter()
    point = np.asarray([0.23, 0.24, 1.2, 0.29, 0.57, 2.7])

    assert check_direct_derivatives(adapter.build(), point).max_abs_error < 2.0e-8


def test_cpe_phase_potentials_are_derivatives_of_the_extensive_phase_gibbs() -> None:
    adapter = CoupledPhaseChemicalAdapter(element_reference_shift=(2.0, -1.0))
    amounts = np.asarray([0.24, 0.51, 0.25])
    volume = 1.3
    total = float(np.sum(amounts))
    phase = np.asarray([amounts[0] / total, amounts[2] / total, volume / total])
    analytic = adapter.chemical_potentials(phase)
    numerical = np.empty(3)
    step = 1.0e-6
    for index in range(3):
        delta = np.zeros(3)
        delta[index] = step
        numerical[index] = (
            adapter.extensive_phase_gibbs(amounts + delta, volume)
            - adapter.extensive_phase_gibbs(amounts - delta, volume)
        ) / (2.0 * step)

    assert analytic == pytest.approx(numerical, abs=2.0e-8)


def test_cpe_is_not_ce_only_or_phase_only_and_rejects_staged_candidates() -> None:
    adapter = CoupledPhaseChemicalAdapter()
    ce_only, phase_only = adapter.staged_candidates()

    assert not adapter.certify(ce_only).accepted
    assert not adapter.certify(phase_only).accepted
    assert adapter.build().objective(ce_only) > adapter.global_lower_bound
    assert adapter.build().objective(phase_only) > adapter.global_lower_bound


def test_cpe_objective_is_phase_permutation_invariant() -> None:
    adapter = CoupledPhaseChemicalAdapter()
    state = adapter.decode(np.asarray([0.23, 0.24, 1.2, 0.29, 0.57, 2.7]))

    assert adapter.objective_state(state) == pytest.approx(adapter.objective_state(state.swapped()))


def test_cpe_family_classifies_active_set_boundaries_without_claiming_a_topology_search() -> None:
    adapter = CoupledPhaseChemicalAdapter()
    interior = adapter.decode(np.asarray([0.2, 0.2, 1.0, 0.3, 0.6, 3.0]))
    single_phase = CoupledState(1.0, interior.alpha, interior.beta)
    boundary_species = CoupledState(0.5, interior.alpha, (0.4, 0.6, 3.0))

    assert adapter.topology(interior) == "interior_two_phase"
    assert adapter.topology(single_phase) == "single_phase_boundary"
    assert adapter.topology(boundary_species) == "boundary_species_two_phase"


def test_element_reference_energy_shift_changes_only_the_feasible_objective_origin() -> None:
    baseline_adapter = CoupledPhaseChemicalAdapter()
    shifted_adapter = CoupledPhaseChemicalAdapter(element_reference_shift=(7.0, -3.0))
    baseline = run_direct(baseline_adapter, seed=91)
    shifted = run_direct(shifted_adapter, seed=91)

    expected_shift = 7.0 * 0.6 - 3.0 * 0.4
    assert shifted.selected.vector == pytest.approx(baseline.selected.vector, abs=1.0e-10)
    assert shifted.selected.merit - baseline.selected.merit == pytest.approx(expected_shift, abs=1.0e-10)
