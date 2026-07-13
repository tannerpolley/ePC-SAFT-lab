"""Nominal registry of EOS-free manufactured formulation adapters."""

from __future__ import annotations

from analyses.reference_oracles.equilibrium_formulations.families.ascani_pairs import AscaniPairAdapter
from analyses.reference_oracles.equilibrium_formulations.families.chemical_equilibrium import (
    ChemicalEquilibriumAdapter,
)
from analyses.reference_oracles.equilibrium_formulations.families.coupled_phase_chemical import (
    CoupledPhaseChemicalAdapter,
)
from analyses.reference_oracles.equilibrium_formulations.families.neutral_held import (
    AssociationHeldAdapter,
    NeutralHeldAdapter,
    NeutralHeldSinglePhaseAdapter,
)
from analyses.reference_oracles.equilibrium_formulations.families.perdomo_held2 import PerdomoHeld2Adapter
from analyses.reference_oracles.equilibrium_formulations.families.public_boundaries import (
    BoundaryKind,
    ManufacturedBoundaryAdapter,
)
from analyses.reference_oracles.equilibrium_formulations.kernel import DirectAdapter, ResidualAdapter


def manufactured_adapters() -> tuple[DirectAdapter | ResidualAdapter, ...]:
    """Return every canonical family variant exercised by this analysis."""

    return (
        ManufacturedBoundaryAdapter(BoundaryKind.BUBBLE_PRESSURE),
        ManufacturedBoundaryAdapter(BoundaryKind.DEW_PRESSURE),
        ManufacturedBoundaryAdapter(BoundaryKind.PURE_SATURATION),
        NeutralHeldAdapter(),
        NeutralHeldSinglePhaseAdapter(),
        AssociationHeldAdapter(),
        PerdomoHeld2Adapter(),
        AscaniPairAdapter(),
        ChemicalEquilibriumAdapter(),
        CoupledPhaseChemicalAdapter(),
    )
