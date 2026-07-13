"""Public package interface for the native ePC-SAFT runtime."""

from __future__ import annotations

from epcsaft._types import InputError, SolutionError
from epcsaft.frontend import Mixture, State
from epcsaft.model.correlations import (
    ConstantCorrelation,
    ConstantPlusExponentialTermsCorrelation,
    DependencySignature,
    DomainEvidence,
    ExponentialTerm,
    IndependentVariable,
    LogTemperatureCorrelation,
    PiecewiseQuadraticTemperatureCorrelation,
    QuadraticCoefficients,
    ReferenceTemperatureLinearCorrelation,
    SaltFreeWaterMoleFractionCubicPermittivityCorrelation,
    ScientificInteractionRecord,
    ScientificRecord,
    ScientificSource,
    ScientificStructuralZero,
    TemperatureDomain,
)
from epcsaft.model.options import BornModelOptions, MissingModelParameterError, ModelOptions
from epcsaft.model.parameters import ParameterSet
from epcsaft.model.resolved_input import EvaluatedModelInput, ResolvedModelInput
from epcsaft.model.source_bundles import SourceBundleSelection, load_source_bundle_selection
from epcsaft.model.templates import create_input_template
from epcsaft.runtime import __version__, capabilities, provider_native_sdk, runtime_build_info

__all__ = [
    "BornModelOptions",
    "ConstantCorrelation",
    "ConstantPlusExponentialTermsCorrelation",
    "DependencySignature",
    "DomainEvidence",
    "ExponentialTerm",
    "EvaluatedModelInput",
    "IndependentVariable",
    "InputError",
    "LogTemperatureCorrelation",
    "MissingModelParameterError",
    "Mixture",
    "ModelOptions",
    "ParameterSet",
    "PiecewiseQuadraticTemperatureCorrelation",
    "QuadraticCoefficients",
    "ReferenceTemperatureLinearCorrelation",
    "ResolvedModelInput",
    "SaltFreeWaterMoleFractionCubicPermittivityCorrelation",
    "ScientificInteractionRecord",
    "ScientificRecord",
    "ScientificSource",
    "ScientificStructuralZero",
    "SolutionError",
    "SourceBundleSelection",
    "State",
    "TemperatureDomain",
    "__version__",
    "capabilities",
    "create_input_template",
    "load_source_bundle_selection",
    "provider_native_sdk",
    "runtime_build_info",
]
