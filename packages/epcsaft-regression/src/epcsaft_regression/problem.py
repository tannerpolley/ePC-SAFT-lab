"""Single M3-aware compiler for immutable regression problems."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any

from epcsaft import InputError, Mixture
from epcsaft.model.resolved_input import EvaluatedModelInput

from .controls import RegressionControls
from .parameters import FittedParameter, ParsedParameterKey, parse_parameter_key
from .targets import TargetDataset, TargetFamily, TargetRow

_CONTRACT_ID = "epcsaft.regression.compiled-problem"
_SCHEMA_VERSION = 1
_PURE_PARAMETER_COMPATIBILITY = {
    TargetFamily.PURE_SATURATION_FUGACITY_BALANCE: {"m", "sigma", "epsilon_k"},
    TargetFamily.PURE_LIQUID_DENSITY_AT_PRESSURE: {"m", "sigma", "epsilon_k"},
}
_BINARY_PARAMETER_COMPATIBILITY = {"m", "sigma", "epsilon_k", "k_ij"}


@dataclass(frozen=True, slots=True)
class CompiledRegressionProblem:
    """Frozen typed inputs submitted by later tasks to the native solver."""

    contract_id: str
    schema_version: int
    dataset_id: str
    row_ids: tuple[str, ...]
    source_ids: tuple[str, ...]
    state_keys: tuple[str, ...]
    provider_definition_fingerprint: str
    evaluated_inputs: tuple[EvaluatedModelInput, ...]
    parameters: tuple[FittedParameter, ...]
    controls: RegressionControls
    fixed_parameter_fingerprints: tuple[tuple[str, str], ...]
    _definition_receipt_json: bytes = field(repr=False)
    _state_receipt_json: tuple[bytes, ...] = field(repr=False)

    @property
    def parameter_keys(self) -> tuple[str, ...]:
        return tuple(parameter.key for parameter in self.parameters)

    @property
    def native_handles(self) -> tuple[Any, ...]:
        return tuple(evaluated.native_handle for evaluated in self.evaluated_inputs)

    @property
    def snapshot_fingerprints(self) -> tuple[str, ...]:
        return tuple(
            evaluated.snapshot_fingerprint_sha256 for evaluated in self.evaluated_inputs
        )

    @property
    def definition_receipt(self) -> dict[str, Any]:
        return json.loads(self._definition_receipt_json)

    @property
    def state_receipts(self) -> tuple[dict[str, Any], ...]:
        return tuple(json.loads(receipt) for receipt in self._state_receipt_json)


def compile_regression_problem(
    *,
    mixture: Mixture,
    dataset: TargetDataset,
    parameters: tuple[FittedParameter, ...],
    controls: RegressionControls,
) -> CompiledRegressionProblem:
    """Compile targets, provider states, parameters, and controls exactly once."""

    if not isinstance(mixture, Mixture):
        raise InputError("compile_regression_problem requires a configured Mixture.")
    if not isinstance(dataset, TargetDataset):
        raise InputError("compile_regression_problem requires a TargetDataset.")
    if not isinstance(controls, RegressionControls):
        raise InputError("compile_regression_problem requires RegressionControls.")
    if not isinstance(parameters, tuple) or any(
        not isinstance(parameter, FittedParameter) for parameter in parameters
    ):
        raise InputError("compile_regression_problem parameters must be a tuple of FittedParameter values.")
    if not parameters:
        raise InputError("compile_regression_problem requires at least one FittedParameter.")

    ordered_parameters = tuple(sorted(parameters, key=lambda parameter: parameter.key))
    keys = tuple(parameter.key for parameter in ordered_parameters)
    duplicates = sorted({key for key in keys if keys.count(key) > 1})
    if duplicates:
        raise InputError(f"duplicate fitted parameter key(s): {', '.join(duplicates)}.")
    parsed_parameters = tuple(parse_parameter_key(parameter.key) for parameter in ordered_parameters)
    _validate_target_parameter_compatibility(mixture, dataset, parsed_parameters)

    definition_receipt = mixture.configuration_receipt
    fitted_record_ids = _fitted_record_ids(definition_receipt, parsed_parameters)
    fixed_fingerprints = _fixed_parameter_fingerprints(
        definition_receipt,
        fitted_record_ids,
    )

    evaluated_inputs: list[EvaluatedModelInput] = []
    state_keys: list[str] = []
    for row in dataset.rows:
        for state_key, composition in _row_states(mixture, row):
            evaluated = mixture.resolved_model_input.evaluate(
                temperature=row.conditions["temperature"],
                composition=composition,
            )
            if (
                evaluated.definition_fingerprint_sha256
                != mixture.resolved_model_input.fingerprint_sha256
            ):
                raise InputError("compiled provider state does not descend from the configured definition.")
            evaluated_inputs.append(evaluated)
            state_keys.append(f"{row.row_id}:{state_key}")

    definition_json = _canonical_json(definition_receipt)
    state_json = tuple(_canonical_json(item.receipt) for item in evaluated_inputs)
    return CompiledRegressionProblem(
        contract_id=_CONTRACT_ID,
        schema_version=_SCHEMA_VERSION,
        dataset_id=dataset.dataset_id,
        row_ids=dataset.row_ids,
        source_ids=tuple(row.source.source_id for row in dataset.rows),
        state_keys=tuple(state_keys),
        provider_definition_fingerprint=mixture.resolved_model_input.fingerprint_sha256,
        evaluated_inputs=tuple(evaluated_inputs),
        parameters=ordered_parameters,
        controls=controls,
        fixed_parameter_fingerprints=fixed_fingerprints,
        _definition_receipt_json=definition_json,
        _state_receipt_json=state_json,
    )


def _validate_target_parameter_compatibility(
    mixture: Mixture,
    dataset: TargetDataset,
    parameters: tuple[ParsedParameterKey, ...],
) -> None:
    for row in dataset.rows:
        if row.target_family is TargetFamily.BINARY_VLE:
            species = row.compositions[0].species
            if species != mixture.components:
                raise InputError("binary target species order must match the configured mixture.")
            admitted = _BINARY_PARAMETER_COMPATIBILITY
        else:
            if len(mixture.components) != 1:
                raise InputError("pure target families require a single-component configured mixture.")
            species = mixture.components
            admitted = _PURE_PARAMETER_COMPATIBILITY.get(row.target_family, set())
        for parameter in parameters:
            if parameter.parameter not in admitted:
                raise InputError(
                    f"fitted parameter {parameter.key!r} is not compatible with target family "
                    f"{row.target_family.value!r}."
                )
            if parameter.is_interaction:
                if set(parameter.owners) != set(species):
                    raise InputError(
                        f"fitted interaction {parameter.key!r} does not match the target species."
                    )
            elif parameter.owners[0] not in species:
                raise InputError(
                    f"fitted parameter {parameter.key!r} does not match the target species."
                )


def _row_states(mixture: Mixture, row: TargetRow) -> tuple[tuple[str, tuple[float, ...]], ...]:
    if row.target_family is TargetFamily.BINARY_VLE:
        return tuple(
            (composition.phase, composition.fractions) for composition in row.compositions
        )
    if len(mixture.components) != 1:
        raise InputError("pure target families require a single-component configured mixture.")
    return (("pure", (1.0,)),)


def _fitted_record_ids(
    definition_receipt: dict[str, Any],
    parameters: tuple[ParsedParameterKey, ...],
) -> set[str]:
    definitions = definition_receipt["definitions"]
    fitted: set[str] = set()
    for parameter in parameters:
        if parameter.is_interaction:
            candidates = [
                record
                for owner in ("interactions", "interaction_policies")
                for record in definitions[owner]
                if record["family"] == parameter.provider_field
                and set(record["components"]) == set(parameter.owners)
            ]
        else:
            candidates = [
                record
                for owner in ("pure_records", "formulation_records")
                for record in definitions[owner]
                if record["component"] == parameter.owners[0]
                and record["field"] == parameter.provider_field
            ]
        if len(candidates) != 1:
            raise InputError(
                f"fitted parameter {parameter.key!r} must resolve to exactly one provider definition."
            )
        record_id = candidates[0]["record_id"]
        if record_id in fitted:
            raise InputError(f"conflicting fitted parameter key for provider record {record_id!r}.")
        fitted.add(record_id)
    return fitted


def _fixed_parameter_fingerprints(
    definition_receipt: dict[str, Any],
    fitted_record_ids: set[str],
) -> tuple[tuple[str, str], ...]:
    definitions = definition_receipt["definitions"]
    records = tuple(
        record
        for owner in (
            "pure_records",
            "formulation_records",
            "interactions",
            "interaction_policies",
        )
        for record in definitions[owner]
        if record["record_id"] not in fitted_record_ids
    )
    return tuple(
        sorted(
            (
                record["record_id"],
                hashlib.sha256(_canonical_json(record)).hexdigest(),
            )
            for record in records
        )
    )


def _canonical_problem_json(problem: CompiledRegressionProblem) -> bytes:
    """Serialize the typed problem deterministically without native handles."""

    if not isinstance(problem, CompiledRegressionProblem):
        raise InputError("canonical problem serialization requires CompiledRegressionProblem.")
    payload = {
        "contract_id": problem.contract_id,
        "schema_version": problem.schema_version,
        "dataset_id": problem.dataset_id,
        "row_ids": list(problem.row_ids),
        "source_ids": list(problem.source_ids),
        "state_keys": list(problem.state_keys),
        "provider_definition_fingerprint": problem.provider_definition_fingerprint,
        "snapshot_fingerprints": list(problem.snapshot_fingerprints),
        "definition_receipt": problem.definition_receipt,
        "state_receipts": list(problem.state_receipts),
        "parameters": [parameter.to_dict() for parameter in problem.parameters],
        "controls": problem.controls.to_dict(),
        "fixed_parameter_fingerprints": [
            {"record_id": record_id, "sha256": fingerprint}
            for record_id, fingerprint in problem.fixed_parameter_fingerprints
        ],
    }
    return _canonical_json(payload)


def _canonical_json(payload: Any) -> bytes:
    return json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
