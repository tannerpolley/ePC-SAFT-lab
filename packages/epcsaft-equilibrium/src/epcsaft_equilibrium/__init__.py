"""Public interface for the ePC-SAFT equilibrium extension."""

from __future__ import annotations

from ._native import provider_contract
from .capabilities import capabilities
from .chemical_equilibrium import (
    ChemicalReaction,
    ChemicalSpecies,
    CompiledChemicalEquilibrium,
    EquilibriumConstantRecord,
    StandardStateRecord,
    StandardStateRegistry,
    build_standard_state_registry,
    compile_reaction_set,
)
from .equilibrium import Equilibrium
from .workflows import (
    EquilibriumPhase,
    EquilibriumResult,
    EquilibriumSolverOptions,
    ReactiveSpeciationResult,
    chemical_equilibrium_native_payload,
    compile_chemical_equilibrium_schema,
    reactive_speciation,
)

__version__ = "0.1.0"

__all__ = [
    "ChemicalReaction",
    "ChemicalSpecies",
    "CompiledChemicalEquilibrium",
    "Equilibrium",
    "EquilibriumConstantRecord",
    "EquilibriumPhase",
    "EquilibriumResult",
    "EquilibriumSolverOptions",
    "ReactiveSpeciationResult",
    "StandardStateRecord",
    "StandardStateRegistry",
    "__version__",
    "build_standard_state_registry",
    "capabilities",
    "chemical_equilibrium_native_payload",
    "compile_chemical_equilibrium_schema",
    "compile_reaction_set",
    "provider_contract",
    "reactive_speciation",
]
