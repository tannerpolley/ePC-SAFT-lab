"""Public interface for the ePC-SAFT equilibrium extension."""

from __future__ import annotations

from ._native import provider_contract
from .capabilities import capabilities
from .equilibrium import Equilibrium
from .workflows import EquilibriumPhase, EquilibriumResult, EquilibriumSolverOptions

__version__ = "0.1.0"

__all__ = [
    "Equilibrium",
    "EquilibriumPhase",
    "EquilibriumResult",
    "EquilibriumSolverOptions",
    "__version__",
    "capabilities",
    "provider_contract",
]
