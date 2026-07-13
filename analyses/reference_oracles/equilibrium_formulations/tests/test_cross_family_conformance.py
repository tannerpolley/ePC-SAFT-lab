from __future__ import annotations

from collections import Counter, defaultdict

import numpy as np
import pytest

from analyses.reference_oracles.equilibrium_formulations.families.chemical_equilibrium import (
    ChemicalEquilibriumAdapter,
)
from analyses.reference_oracles.equilibrium_formulations.families.coupled_phase_chemical import (
    CoupledPhaseChemicalAdapter,
)
from analyses.reference_oracles.equilibrium_formulations.families.neutral_held import (
    ManufacturedAssociationEvaluator,
    NeutralHeldAdapter,
)
from analyses.reference_oracles.equilibrium_formulations.families.perdomo_held2 import PerdomoHeld2Adapter
from analyses.reference_oracles.equilibrium_formulations.families.public_boundaries import (
    BoundaryKind,
    ManufacturedBoundaryAdapter,
)
from analyses.reference_oracles.equilibrium_formulations.kernel import (
    CandidateOutcome,
    NumericalKind,
    run_formulation,
    summarize_convergence,
)
from analyses.reference_oracles.equilibrium_formulations.registry import manufactured_adapters


def test_one_kernel_facade_executes_every_registered_family_with_unique_nominal_identity() -> None:
    adapters = manufactured_adapters()
    receipts = tuple(run_formulation(adapter, seed=1729) for adapter in adapters)
    formulation_ids = tuple(receipt.formulation_id for receipt in receipts)

    assert len(adapters) == 10
    assert len(set(formulation_ids)) == len(formulation_ids)
    assert all(receipt.certificate.accepted for receipt in receipts)
    assert all(receipt.certificate.formulation_id == receipt.formulation_id for receipt in receipts)
    assert {receipt.numerical_kind for receipt in receipts} == {
        NumericalKind.DIRECT_MINIMIZATION,
        NumericalKind.RESIDUAL_SOLVE,
    }


@pytest.mark.parametrize("seed", [3, 11, 29])
def test_registered_family_selection_and_acceptance_are_seed_deterministic(seed: int) -> None:
    first = tuple(run_formulation(adapter, seed=seed) for adapter in manufactured_adapters())
    second = tuple(run_formulation(adapter, seed=seed) for adapter in manufactured_adapters())

    assert first == second
    assert all(sum(candidate.converged for candidate in receipt.candidates) >= 1 for receipt in first)


def test_anchor_free_multistart_basin_map_classifies_every_local_attempt() -> None:
    seeds = (3, 11, 29)
    adapters = manufactured_adapters()
    receipts = tuple(run_formulation(adapter, seed=seed) for seed in seeds for adapter in adapters)
    repeated = tuple(run_formulation(adapter, seed=seed) for seed in seeds for adapter in adapters)
    summary = summarize_convergence(receipts)

    assert receipts == repeated
    assert len(summary.classifications) == sum(len(receipt.candidates) for receipt in receipts)
    assert summary.accepted_count + summary.rejected_count + summary.not_converged_count == len(summary.classifications)
    assert summary.accepted_count >= len(adapters) * len(seeds)
    assert summary.rejected_count > 0
    assert summary.not_converged_count > 0
    assert {item.outcome for item in summary.classifications} == {
        CandidateOutcome.ACCEPTED,
        CandidateOutcome.REJECTED,
        CandidateOutcome.NOT_CONVERGED,
    }
    counts_by_family: dict[str, Counter[CandidateOutcome]] = defaultdict(Counter)
    for item in summary.classifications:
        counts_by_family[item.formulation_id][item.outcome] += 1
    assert {formulation_id: dict(counts) for formulation_id, counts in sorted(counts_by_family.items())} == {
        "ascani.counterion-pair.manufactured.v1": {
            CandidateOutcome.ACCEPTED: 5,
            CandidateOutcome.NOT_CONVERGED: 1,
        },
        "association-neutral-held.stage-iii.manufactured.v1": {
            CandidateOutcome.ACCEPTED: 3,
            CandidateOutcome.REJECTED: 6,
        },
        "cpe.manufactured.v1": {CandidateOutcome.ACCEPTED: 9},
        "neutral-held.stage-iii.manufactured.v1": {
            CandidateOutcome.ACCEPTED: 3,
            CandidateOutcome.REJECTED: 6,
        },
        "neutral-held.stage-iii.single-phase.manufactured.v1": {CandidateOutcome.ACCEPTED: 6},
        "perdomo-held2.modified-mole.manufactured.v1": {
            CandidateOutcome.ACCEPTED: 3,
            CandidateOutcome.REJECTED: 6,
        },
        "public.bubble_pressure.manufactured.v1": {CandidateOutcome.ACCEPTED: 9},
        "public.dew_pressure.manufactured.v1": {CandidateOutcome.ACCEPTED: 9},
        "public.pure_saturation.manufactured.v1": {CandidateOutcome.ACCEPTED: 9},
        "standalone-ce.ideal-interior.manufactured.v1": {CandidateOutcome.ACCEPTED: 9},
    }
    assert (summary.accepted_count, summary.rejected_count, summary.not_converged_count) == (65, 18, 1)
    for seed in seeds:
        for adapter in adapters:
            receipt = next(
                item
                for item in receipts
                if item.seed == seed and item.formulation_id == adapter.descriptor.formulation_id
            )
            selected = np.asarray(receipt.selected.vector)
            assert all(not np.allclose(start, selected, atol=1.0e-14, rtol=0.0) for start in adapter.starts(seed))

    neutral_receipts = [
        item for item in receipts if item.formulation_id == NeutralHeldAdapter().descriptor.formulation_id
    ]
    rejected_neutral = [
        certificate
        for receipt in neutral_receipts
        for certificate in receipt.candidate_certificates
        if certificate is not None and not certificate.accepted
    ]
    assert rejected_neutral
    assert any(certificate.metrics["minimum_tangent_plane_distance"] < 0.0 for certificate in rejected_neutral)


def test_solution_location_is_stable_but_independent_acceptance_remains_authoritative() -> None:
    for adapter in manufactured_adapters():
        tight = run_formulation(adapter, seed=101, tolerance=1.0e-10)
        relaxed = run_formulation(adapter, seed=101, tolerance=1.0e-8)

        assert relaxed.selected.vector == pytest.approx(tight.selected.vector, abs=1.0e-8)
        assert tight.certificate.accepted
        assert relaxed.certificate.formulation_id == relaxed.formulation_id


def test_family_constraint_and_coordinate_ranks_match_the_canonical_degrees_of_freedom() -> None:
    bubble = ManufacturedBoundaryAdapter(BoundaryKind.BUBBLE_PRESSURE).build()
    ce = ChemicalEquilibriumAdapter()
    cpe = CoupledPhaseChemicalAdapter()
    held2 = PerdomoHeld2Adapter()
    association = ManufacturedAssociationEvaluator()

    assert np.linalg.matrix_rank(bubble.jacobian(np.asarray([2.0, 1.0, 3.0, 0.75, 0.25]))) == 5
    assert np.linalg.matrix_rank(ce.element_matrix) == 1
    assert np.linalg.matrix_rank(ce.stoichiometric_matrix) == 1
    assert np.allclose(ce.element_matrix @ ce.stoichiometric_matrix, np.zeros((1, 1)))
    assert ce.stoichiometric_matrix.shape[1] == 2 - np.linalg.matrix_rank(ce.element_matrix)
    assert np.linalg.matrix_rank(cpe.element_matrix) == 2
    assert cpe.element_matrix @ cpe.reaction_vector == pytest.approx([0.0, 0.0])
    assert 1 == 3 - np.linalg.matrix_rank(cpe.element_matrix)
    assert held2.certify(np.asarray([0.2, 0.8, 1.0, 1.0])).metrics["independent_modified_composition_count"] == 1.0
    assert association.residual_scale != 0.0


def test_standalone_ce_is_invariant_to_extensive_inventory_scaling() -> None:
    unit_adapter = ChemicalEquilibriumAdapter(inventory_scale=1.0)
    scaled_adapter = ChemicalEquilibriumAdapter(inventory_scale=37.0)
    unit = run_formulation(unit_adapter, seed=44)
    scaled = run_formulation(scaled_adapter, seed=44)

    assert scaled.selected.vector[0] / scaled_adapter.extent_upper_bound == pytest.approx(
        unit.selected.vector[0] / unit_adapter.extent_upper_bound,
        abs=1.0e-10,
    )
    assert scaled.certificate.metrics["affinity_inf_norm"] == pytest.approx(
        unit.certificate.metrics["affinity_inf_norm"],
        abs=1.0e-12,
    )


def test_family_specific_invalid_topologies_do_not_reach_generic_acceptance() -> None:
    cpe = CoupledPhaseChemicalAdapter()

    assert not cpe.certify(np.asarray([0.2, 0.45, 1.0, 0.3, 0.6, 3.0])).accepted
    assert not cpe.certify(np.asarray([0.8, 0.3, 1.0, 0.3, 0.6, 3.0])).accepted
