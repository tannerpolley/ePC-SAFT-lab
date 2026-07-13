"""Private typed compiler for the provider-owned resolved-input ABI."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Sequence
from typing import Any

from .. import _core
from .._types import InputError
from .correlations import (
    ConstantCorrelation,
    ConstantPlusExponentialTermsCorrelation,
    LogTemperatureCorrelation,
    PiecewiseQuadraticTemperatureCorrelation,
    ReferenceTemperatureLinearCorrelation,
    SaltFreeWaterMoleFractionCubicPermittivityCorrelation,
    ScientificInteractionRecord,
    ScientificRecord,
    ScientificStructuralZero,
)
from .options import DisabledFormulation
from .source_bundles import SourceBundleSelection

_RELATIVE_PERMITTIVITY_RULES = {
    "constant": 0,
    "component_linear": 1,
    "linear": 1,
    "linear_massfraction": 2,
    "combined": 3,
    "empirical": 4,
    "linear_saltfraction": 7,
    "aqueous_organic": 8,
    "salt_free_massfraction": 9,
}
_DIAMETER_MODES = {
    "sigma": 0,
    "sigma_reduced": 1,
    "temperature_dependent": 2,
    "fitted": 3,
}


def _canonical_definition_payload(
    selection: SourceBundleSelection,
    components: tuple[str, ...],
) -> dict[str, Any]:
    parameters = json.loads(selection.parameter_set.to_json())
    for key in ("pure_records", "formulation_records", "interactions", "interaction_policies"):
        parameters[key] = sorted(parameters[key], key=lambda item: item["record_id"])
    return {
        "schema": "epcsaft.resolved-model-input",
        "schema_version": 1,
        "components": list(components),
        "parameters": parameters,
        "model_configuration": selection.model_options.receipt,
        "source_files": sorted(path.as_posix() for path in selection.source_files),
    }


def _definition_fingerprint(selection: SourceBundleSelection, components: tuple[str, ...]) -> str:
    encoded = json.dumps(
        _canonical_definition_payload(selection, components),
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _native_dependency(record: ScientificRecord | ScientificInteractionRecord):
    signature = record.dependency_signature
    return _core._NativeDependencySignatureV1(
        [str(variable) for variable in signature.variables],
        list(signature.composition_components),
    )


def _native_domain(record: ScientificRecord | ScientificInteractionRecord):
    domain = record.temperature_domain
    return _core._NativeTemperatureDomainV1(
        domain.minimum_K,
        domain.maximum_K,
        domain.evidence.kind,
        domain.evidence.source,
    )


def _native_correlation(definition: object):
    if isinstance(definition, ConstantCorrelation):
        return _core._NativeConstantCorrelationV1(definition.value)
    if isinstance(definition, ReferenceTemperatureLinearCorrelation):
        return _core._NativeReferenceTemperatureLinearCorrelationV1(
            definition.reference_temperature_K,
            definition.reference_value,
            definition.slope_per_K,
        )
    if isinstance(definition, LogTemperatureCorrelation):
        return _core._NativeLogTemperatureCorrelationV1(
            definition.coefficient,
            definition.intercept,
            definition.reference_temperature_K,
        )
    if isinstance(definition, ConstantPlusExponentialTermsCorrelation):
        return _core._NativeConstantPlusExponentialTermsCorrelationV1(
            definition.constant,
            [
                _core._NativeExponentialTermV1(
                    term.coefficient,
                    term.temperature_coefficient_per_K,
                )
                for term in definition.terms
            ],
        )
    if isinstance(definition, PiecewiseQuadraticTemperatureCorrelation):
        return _core._NativePiecewiseQuadraticTemperatureCorrelationV1(
            definition.transition_temperature_K,
            _core._NativeQuadraticCoefficientsV1(
                definition.lower.quadratic,
                definition.lower.linear,
                definition.lower.constant,
            ),
            _core._NativeQuadraticCoefficientsV1(
                definition.upper.quadratic,
                definition.upper.linear,
                definition.upper.constant,
            ),
        )
    if isinstance(definition, SaltFreeWaterMoleFractionCubicPermittivityCorrelation):
        return _core._NativeSaltFreeWaterMoleFractionCubicPermittivityCorrelationV1(
            definition.water_component,
            definition.organic_component,
            definition.coefficient_a,
            definition.coefficient_b,
            definition.coefficient_c,
        )
    raise InputError(f"unsupported typed scientific correlation: {type(definition).__name__}.")


def _native_record(record: ScientificRecord, component_index: dict[str, int]):
    return _core._NativeScientificRecordV1(
        record.record_id,
        component_index[record.component],
        record.component,
        record.field,
        record.units,
        record.source.kind,
        record.source.locator,
        _native_dependency(record),
        _native_domain(record),
        _native_correlation(record.definition),
    )


def _native_interaction(record: ScientificInteractionRecord, component_index: dict[str, int]):
    left, right = sorted(component_index[component] for component in record.components)
    return _core._NativeScientificInteractionRecordV1(
        record.record_id,
        record.family,
        left,
        right,
        record.units,
        record.source.kind,
        record.source.locator,
        _native_dependency(record),
        _native_domain(record),
        _native_correlation(record.definition),
    )


def _native_structural_zero(record: ScientificStructuralZero, component_index: dict[str, int]):
    left, right = sorted(component_index[component] for component in record.components)
    return _core._NativeStructuralZeroEvidenceV1(
        record.record_id,
        record.family,
        left,
        right,
        record.reason,
        f"{record.source.kind}:{record.source.locator}",
    )


def _enabled(value: object) -> bool:
    return not isinstance(value, DisabledFormulation)


def _native_formulation(selection: SourceBundleSelection):
    options = selection.model_options
    relative_permittivity_enabled = _enabled(options.relative_permittivity)
    debye_huckel_enabled = _enabled(options.debye_huckel)
    born_enabled = _enabled(options.born)
    return _core._NativeFormulationV1(
        _enabled(options.electrostatics),
        relative_permittivity_enabled,
        _RELATIVE_PERMITTIVITY_RULES[options.relative_permittivity.rule]
        if relative_permittivity_enabled
        else 0,
        debye_huckel_enabled,
        _DIAMETER_MODES[options.debye_huckel.ion_diameter_rule] if debye_huckel_enabled else 0,
        options.debye_huckel.bjerrum_pairing if debye_huckel_enabled else False,
        born_enabled,
        _DIAMETER_MODES[options.born.born_diameter_rule] if born_enabled else 0,
        options.born.solvation_shell_model if born_enabled else False,
        options.born.dielectric_saturation if born_enabled else False,
        1 if born_enabled and options.born.bulk_mode == "solvent" else 0,
        _enabled(options.solvated_ion_diameter),
        _enabled(options.ion_dispersion),
    )


def _build_native_resolved_input(
    selection: SourceBundleSelection,
    *,
    components: Sequence[str],
):
    """Compile typed source definitions without evaluating a state condition."""

    if not isinstance(selection, SourceBundleSelection):
        raise InputError("native resolved input requires a SourceBundleSelection.")
    component_order = tuple(str(component) for component in components)
    if component_order != selection.parameter_set.components:
        raise InputError("native resolved-input component order must exactly match the source bundle.")
    selection.parameter_set.validate()
    index = {component: position for position, component in enumerate(component_order)}
    records = [
        _native_record(record, index)
        for record in (*selection.parameter_set.pure_records, *selection.parameter_set.formulation_records)
    ]
    interactions = [
        _native_interaction(record, index)
        for record in selection.parameter_set.interactions
    ]
    structural_zeros = [
        _native_structural_zero(record, index)
        for record in selection.parameter_set.interaction_policies
    ]
    try:
        return _core.ResolvedNativeInput(
            _definition_fingerprint(selection, component_order),
            list(component_order),
            _native_formulation(selection),
            records,
            interactions,
            structural_zeros,
        )
    except (_core.NativeValueError, TypeError, ValueError) as exc:
        raise InputError(f"invalid typed native resolved input: {exc}") from exc


def _evaluate_native_resolved_input(
    resolved_input: object,
    *,
    temperature_K: float,
    canonical_composition: Sequence[float],
):
    """Evaluate one typed native graph into a provider-owned immutable handle."""

    if not isinstance(resolved_input, _core.ResolvedNativeInput):
        raise InputError("native evaluation requires a ResolvedNativeInput.")
    composition = tuple(float(value) for value in canonical_composition)
    return _core._native_evaluate_resolved_input_v1(
        resolved_input,
        float(temperature_K),
        composition,
    )
