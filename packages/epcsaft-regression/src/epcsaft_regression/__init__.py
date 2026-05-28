"""Ceres-backed regression extension for ePC-SAFT."""

from __future__ import annotations

from .capabilities import capabilities, provider_contract
from .workflow import Regression

__version__ = "0.1.0"

_CORE_EXPORTS = {
    "FitResult",
    "TargetDataset",
    "TargetRow",
    "evaluate_pure_neutral_derivatives",
    "fit_binary_pair",
    "fit_binary_parameters",
    "fit_liquid_electrolyte_parameters",
    "fit_pure_ion",
    "fit_pure_neutral",
    "fit_pure_parameters",
    "write_fit_result",
}

__all__ = [
    "Regression",
    "__version__",
    "capabilities",
    "provider_contract",
    *_CORE_EXPORTS,
]


def __getattr__(name: str):
    if name in _CORE_EXPORTS:
        from . import core

        value = getattr(core, name)
        globals()[name] = value
        return value
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
