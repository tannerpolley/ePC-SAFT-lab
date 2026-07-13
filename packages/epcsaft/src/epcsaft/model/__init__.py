"""Parameter and model-configuration modules."""

from .configuration_catalog import model_configuration_capabilities
from .correlations import (
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
from .options import BornModelOptions, MissingModelParameterError, ModelOptions
from .parameters import ParameterSet
from .source_bundles import SourceBundleSelection, load_source_bundle_selection
from .templates import create_input_template

__all__ = [
    "BornModelOptions",
    "ConstantCorrelation",
    "ConstantPlusExponentialTermsCorrelation",
    "DependencySignature",
    "DomainEvidence",
    "ExponentialTerm",
    "IndependentVariable",
    "LogTemperatureCorrelation",
    "MissingModelParameterError",
    "ModelOptions",
    "ParameterSet",
    "PiecewiseQuadraticTemperatureCorrelation",
    "QuadraticCoefficients",
    "ReferenceTemperatureLinearCorrelation",
    "SaltFreeWaterMoleFractionCubicPermittivityCorrelation",
    "ScientificInteractionRecord",
    "ScientificRecord",
    "ScientificSource",
    "ScientificStructuralZero",
    "SourceBundleSelection",
    "TemperatureDomain",
    "create_input_template",
    "load_source_bundle_selection",
    "model_configuration_capabilities",
]
