"""Public interface for the ePC-SAFT equilibrium extension."""

from __future__ import annotations

from ._native import provider_contract
from .capabilities import capabilities
from .chemical_equilibrium import ChemicalReaction, ChemicalSpecies, CompiledChemicalEquilibrium, compile_reaction_set
from .equilibrium import Equilibrium
from .workflows import (
    EquilibriumPhase,
    EquilibriumResult,
    EquilibriumSolverOptions,
    chemical_equilibrium_native_payload,
    compile_chemical_equilibrium_schema,
)

__version__ = "0.1.0"

__all__ = [
    "Equilibrium",
    "EquilibriumPhase",
    "EquilibriumResult",
    "EquilibriumSolverOptions",
    "ChemicalReaction",
    "ChemicalSpecies",
    "CompiledChemicalEquilibrium",
    "__version__",
    "chemical_equilibrium_native_payload",
    "compile_chemical_equilibrium_schema",
    "compile_reaction_set",
    "capabilities",
    "provider_contract",
]
