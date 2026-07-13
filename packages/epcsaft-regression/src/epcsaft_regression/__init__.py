"""Ceres-backed regression extension for ePC-SAFT."""

from __future__ import annotations

from importlib import import_module

from .controls import LossKind, RegressionControls
from .parameters import FittedParameter
from .problem import CompiledRegressionProblem, compile_regression_problem
from .targets import (
    CompositionBasis,
    CompositionRecord,
    SourceIdentity,
    SourceKind,
    TargetDataset,
    TargetFamily,
    TargetRow,
)
from .workflow import Regression

__version__ = "0.1.0"

_CORE_EXPORTS = {
    "FitResult",
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
    "CompositionBasis",
    "CompositionRecord",
    "CompiledRegressionProblem",
    "FittedParameter",
    "LossKind",
    "Regression",
    "RegressionControls",
    "SourceIdentity",
    "SourceKind",
    "TargetDataset",
    "TargetFamily",
    "TargetRow",
    "__version__",
    "capabilities",
    "compile_regression_problem",
    "provider_contract",
    *_CORE_EXPORTS,
]


def __getattr__(name: str):
    if name in {"capabilities", "provider_contract"}:
        capability_module = import_module(".capabilities", __name__)
        value = getattr(capability_module, name)
        globals()[name] = value
        return value
    if name in _CORE_EXPORTS:
        from . import core

        value = getattr(core, name)
        globals()[name] = value
        return value
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
