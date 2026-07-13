"""Ceres-backed regression extension for ePC-SAFT."""

from __future__ import annotations

from importlib import import_module

from .controls import LossKind, RegressionControls
from .parameters import FittedParameter
from .problem import CompiledRegressionProblem, compile_regression_problem
from .results import FitProblem, FitResult, RegressionEvaluation, RegressionReceipt
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

__all__ = [
    "CompiledRegressionProblem",
    "CompositionBasis",
    "CompositionRecord",
    "FitProblem",
    "FitResult",
    "FittedParameter",
    "LossKind",
    "Regression",
    "RegressionControls",
    "RegressionEvaluation",
    "RegressionReceipt",
    "SourceIdentity",
    "SourceKind",
    "TargetDataset",
    "TargetFamily",
    "TargetRow",
    "__version__",
    "capabilities",
    "compile_regression_problem",
    "provider_contract",
]


def __getattr__(name: str):
    if name in {"capabilities", "provider_contract"}:
        capability_module = import_module(".capabilities", __name__)
        value = getattr(capability_module, name)
        globals()[name] = value
        return value
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
