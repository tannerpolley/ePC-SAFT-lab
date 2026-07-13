"""Immutable public owner of compiled provider definitions and state receipts."""

from __future__ import annotations

import json
import math
import re
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any

from .. import _core
from .._types import InputError
from ..state.input_validation import validate_canonical_composition
from ._resolved_input_native import (
    _build_native_resolved_input,
    _evaluate_native_resolved_input,
)
from .options import ModelOptions
from .parameters import ParameterSet
from .source_bundles import SourceBundleSelection

_RESOLVED_INPUT_SCHEMA = "epcsaft.resolved-model-input"
_RESOLVED_INPUT_SCHEMA_VERSION = 1
_SHA256_PATTERN = re.compile(r"[0-9a-f]{64}")


@dataclass(frozen=True, slots=True, init=False)
class EvaluatedModelInput:
    """One immutable provider snapshot plus its detached scientific receipt."""

    definition_fingerprint_sha256: str
    snapshot_fingerprint_sha256: str
    _native_handle: Any
    _receipt_json: str

    @property
    def native_handle(self) -> Any:
        """Return the provider-owned immutable native carrier."""

        return self._native_handle

    @property
    def receipt(self) -> dict[str, Any]:
        """Return a detached copy of the evaluated scientific receipt."""

        return json.loads(self._receipt_json)


@dataclass(frozen=True, slots=True, init=False)
class ResolvedModelInput:
    """A frozen typed provider definition graph compiled exactly once."""

    components: tuple[str, ...]
    fingerprint_sha256: str
    _native_input: Any
    _configuration_receipt_json: str

    @classmethod
    def resolve(
        cls,
        parameters: ParameterSet,
        model_options: ModelOptions,
        *,
        components: Sequence[str] | None = None,
    ) -> ResolvedModelInput:
        """Compile typed definitions and one explicit formulation selection."""

        return _compile_resolved_model_input(parameters, model_options, components)

    @property
    def configuration_receipt(self) -> dict[str, Any]:
        """Return a detached copy of the deterministic definition receipt."""

        return json.loads(self._configuration_receipt_json)

    def evaluate(
        self,
        *,
        temperature: float,
        composition: Sequence[float],
    ) -> EvaluatedModelInput:
        """Evaluate one exact state without normalizing its composition."""

        canonical = validate_canonical_composition(composition, len(self.components))
        try:
            temperature_K = float(temperature)
        except (TypeError, ValueError) as exc:
            raise InputError("temperature must be a finite number in kelvin.") from exc
        if not math.isfinite(temperature_K):
            raise InputError("temperature must be a finite number in kelvin.")
        return _evaluate_resolved_model_input(self, temperature_K, canonical)


def _canonical_json(payload: dict[str, Any]) -> str:
    return json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


def _canonical_definitions(parameters: ParameterSet) -> dict[str, Any]:
    payload = json.loads(parameters.to_json())
    for key in ("pure_records", "formulation_records", "interactions", "interaction_policies"):
        payload[key] = sorted(payload[key], key=lambda item: item["record_id"])
    return payload


def _compile_resolved_model_input(
    parameters: ParameterSet,
    model_options: ModelOptions,
    components: Sequence[str] | None,
) -> ResolvedModelInput:
    if not isinstance(parameters, ParameterSet):
        raise InputError("ResolvedModelInput.resolve requires a ParameterSet.")
    if not isinstance(model_options, ModelOptions):
        raise InputError("ResolvedModelInput.resolve requires a ModelOptions selection.")
    if parameters.schema_origin != "scientific_v3":
        raise InputError("ResolvedModelInput requires a definitions-only schema-3 ParameterSet.")
    component_order = (
        parameters.components
        if components is None
        else tuple(str(component) for component in components)
    )
    if component_order != parameters.components:
        raise InputError("resolved-input component order must exactly match the ParameterSet.")
    parameters.validate()
    selection = SourceBundleSelection(
        parameter_set=parameters,
        model_options=model_options,
        source_files=(),
    )
    native_input = _build_native_resolved_input(selection, components=component_order)
    _validate_definition_identity(native_input, component_order)
    fingerprint = native_input.definition_fingerprint_sha256
    receipt = {
        "contract_id": native_input.contract_id,
        "schema": native_input.schema,
        "schema_version": native_input.schema_version,
        "components": list(component_order),
        "definition_fingerprint_sha256": fingerprint,
        "configuration": model_options.receipt,
        "definitions": _canonical_definitions(parameters),
    }
    result = object.__new__(ResolvedModelInput)
    object.__setattr__(result, "components", component_order)
    object.__setattr__(result, "fingerprint_sha256", fingerprint)
    object.__setattr__(result, "_native_input", native_input)
    object.__setattr__(result, "_configuration_receipt_json", _canonical_json(receipt))
    return result


def _validate_definition_identity(native_input: Any, components: tuple[str, ...]) -> None:
    if not isinstance(native_input, _core.ResolvedNativeInput):
        raise InputError("provider compiler did not return a ResolvedNativeInput.")
    if native_input.schema != _RESOLVED_INPUT_SCHEMA:
        raise InputError("provider definition schema does not match the resolved-input contract.")
    if native_input.schema_version != _RESOLVED_INPUT_SCHEMA_VERSION:
        raise InputError("provider definition schema version does not match the resolved-input contract.")
    if tuple(native_input.component_order) != components:
        raise InputError("provider definition component order does not match the resolved input.")
    if _SHA256_PATTERN.fullmatch(native_input.definition_fingerprint_sha256) is None:
        raise InputError("provider definition fingerprint is not a canonical SHA-256 identity.")


def _evaluate_resolved_model_input(
    resolved: ResolvedModelInput,
    temperature_K: float,
    canonical_composition: Any,
) -> EvaluatedModelInput:
    try:
        handle = _evaluate_native_resolved_input(
            resolved._native_input,
            temperature_K=temperature_K,
            canonical_composition=canonical_composition,
        )
    except InputError:
        raise
    except (_core.NativeValueError, TypeError, ValueError) as exc:
        raise InputError(str(exc)) from exc
    _validate_snapshot_identity(resolved, handle, temperature_K, canonical_composition)
    configuration_receipt = json.loads(resolved._configuration_receipt_json)
    receipt = {
        "contract_id": handle.contract_id,
        "schema": handle.schema,
        "schema_version": handle.schema_version,
        "components": list(resolved.components),
        "definition_fingerprint_sha256": handle.definition_fingerprint_sha256,
        "snapshot_fingerprint_sha256": handle.snapshot_fingerprint_sha256,
        "configuration": configuration_receipt["configuration"],
        "definitions": configuration_receipt["definitions"],
        "state": {
            "temperature_K": handle.temperature_K,
            "composition_basis": handle.composition_basis,
            "canonical_composition": list(handle.canonical_composition),
        },
        "dependency_groups": {
            key: sorted(record_ids)
            for key, record_ids in sorted(handle.affected_record_ids.items())
        },
        "trial_phase_composition_invariant": handle.trial_phase_composition_invariant,
        "evaluated_records": sorted(
            handle.evaluated_records,
            key=lambda item: item["record_id"],
        ),
        "structural_zeros": sorted(
            handle.structural_zeros,
            key=lambda item: item["record_id"],
        ),
        "active_residual_families": list(handle.active_residual_families),
        "ionic_component_indices": list(handle.ionic_component_indices),
        "association_topology_fingerprint_sha256": (
            handle.association_topology_fingerprint_sha256
        ),
        "scientific_source_classifications": sorted(
            handle.scientific_source_classifications
        ),
        "native_mapping": handle.native_mapping,
    }
    receipt_json = _canonical_json(receipt)
    detached = json.loads(receipt_json)
    if detached["definition_fingerprint_sha256"] != resolved.fingerprint_sha256:
        raise InputError("evaluated receipt definition fingerprint mismatch.")
    if detached["snapshot_fingerprint_sha256"] != handle.snapshot_fingerprint_sha256:
        raise InputError("evaluated receipt snapshot fingerprint mismatch.")
    result = object.__new__(EvaluatedModelInput)
    object.__setattr__(
        result,
        "definition_fingerprint_sha256",
        handle.definition_fingerprint_sha256,
    )
    object.__setattr__(
        result,
        "snapshot_fingerprint_sha256",
        handle.snapshot_fingerprint_sha256,
    )
    object.__setattr__(result, "_native_handle", handle)
    object.__setattr__(result, "_receipt_json", receipt_json)
    return result


def _validate_snapshot_identity(
    resolved: ResolvedModelInput,
    handle: Any,
    temperature_K: float,
    canonical_composition: Any,
) -> None:
    if not isinstance(handle, _core.ProviderResolvedInputHandleV1):
        raise InputError("provider evaluator did not return a ProviderResolvedInputHandleV1.")
    if handle.schema != _RESOLVED_INPUT_SCHEMA or handle.schema_version != _RESOLVED_INPUT_SCHEMA_VERSION:
        raise InputError("provider snapshot schema does not match the resolved-input contract.")
    if tuple(handle.component_order) != resolved.components:
        raise InputError("provider snapshot component order does not match the resolved input.")
    if handle.definition_fingerprint_sha256 != resolved.fingerprint_sha256:
        raise InputError("provider handle definition fingerprint mismatch.")
    if _SHA256_PATTERN.fullmatch(handle.snapshot_fingerprint_sha256) is None:
        raise InputError("provider snapshot fingerprint is not a canonical SHA-256 identity.")
    if handle.temperature_K != temperature_K:
        raise InputError("provider snapshot temperature does not match the evaluated state.")
    if handle.composition_basis != "mole_fraction":
        raise InputError("provider snapshot composition basis is not mole_fraction.")
    if list(handle.canonical_composition) != canonical_composition.tolist():
        raise InputError("provider snapshot composition does not match the canonical input.")
