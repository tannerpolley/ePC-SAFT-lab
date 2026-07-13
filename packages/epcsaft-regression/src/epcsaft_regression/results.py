"""Frozen public views of authoritative native regression receipts."""

from __future__ import annotations

import json
import math
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from numbers import Real
from typing import Any, Literal

from epcsaft import InputError

from .problem import CompiledRegressionProblem

_RECEIPT_SCHEMA_VERSION = 1
_COMMON_NATIVE_FIELDS = frozenset(
    {
        "receipt_schema_version",
        "problem_receipt",
        "problem_fingerprint",
        "termination_type",
        "solution_usable",
        "effective_ceres_options",
        "parameter_values",
        "row_diagnostics",
        "objective",
        "jacobian_row_major",
        "jacobian_shape",
        "derivative_metadata",
        "success",
    }
)
_SOLVE_NATIVE_FIELDS = frozenset(
    {"iterations", "initial_cost", "final_cost", "message"}
)
_PROBLEM_RECEIPT_FIELDS = frozenset(
    {
        "contract_id",
        "schema_version",
        "dataset_id",
        "provider_definition_fingerprint",
        "snapshot_fingerprints",
        "provider_handles",
        "row_ids",
        "source_ids",
        "parameter_keys",
        "rows",
        "parameters",
        "fixed_parameter_fingerprints",
        "controls",
        "problem_fingerprint",
    }
)
_PROVIDER_HANDLE_FIELDS = frozenset(
    {
        "definition_fingerprint_sha256",
        "snapshot_fingerprint_sha256",
        "component_order",
        "temperature_K",
        "composition_basis",
        "canonical_composition",
    }
)
_ROW_RECEIPT_FIELDS = frozenset(
    {
        "row_id",
        "source_id",
        "source_kind",
        "target_family",
        "provider_handle_indices",
        "pressure_Pa",
        "weight",
        "residual_scale",
        "target_value",
        "model_intercept",
        "parameter_coefficients",
        "derivative_owner",
    }
)
_PARAMETER_RECEIPT_FIELDS = frozenset(
    {"key", "target_kind", "first_index", "second_index", "start", "lower", "upper"}
)
_CONTROL_RECEIPT_FIELDS = frozenset(
    {
        "loss",
        "max_num_iterations",
        "function_tolerance",
        "gradient_tolerance",
        "parameter_tolerance",
    }
)


@dataclass(frozen=True, slots=True, init=False)
class FitProblem:
    """One compiled configured problem paired with its native identity."""

    _compiled: CompiledRegressionProblem = field(repr=False)
    _problem_fingerprint: str
    _receipt_json: bytes = field(repr=False)

    def __init__(self) -> None:
        raise TypeError("FitProblem is created only by Regression.fit.")

    @classmethod
    def _from_receipt(
        cls,
        compiled: CompiledRegressionProblem,
        receipt: RegressionReceipt,
    ) -> FitProblem:
        if not isinstance(compiled, CompiledRegressionProblem):
            raise InputError("FitProblem requires a CompiledRegressionProblem.")
        from .native_adapter import _native_problem_from_compiled

        problem_receipt = receipt.problem_receipt
        expected_receipt = _native_problem_from_compiled(compiled).problem_receipt
        if _canonical_json(problem_receipt, "native problem receipt") != _canonical_json(
            expected_receipt, "compiled native problem receipt"
        ):
            raise InputError(
                "native problem receipt does not exactly match the compiled problem."
            )
        instance = object.__new__(cls)
        object.__setattr__(instance, "_compiled", compiled)
        object.__setattr__(
            instance, "_problem_fingerprint", receipt.problem_fingerprint
        )
        object.__setattr__(
            instance,
            "_receipt_json",
            _canonical_json(problem_receipt, "native problem receipt"),
        )
        return instance

    @property
    def problem_fingerprint(self) -> str:
        return self._problem_fingerprint

    @property
    def dataset_id(self) -> str:
        return self._compiled.dataset_id

    @property
    def provider_definition_fingerprint(self) -> str:
        return self._compiled.provider_definition_fingerprint

    @property
    def row_ids(self) -> tuple[str, ...]:
        return self._compiled.row_ids

    @property
    def source_ids(self) -> tuple[str, ...]:
        return self._compiled.source_ids

    @property
    def parameter_keys(self) -> tuple[str, ...]:
        return self._compiled.parameter_keys

    @property
    def controls(self) -> dict[str, object]:
        return self._compiled.controls.to_dict()

    def to_dict(self) -> dict[str, Any]:
        """Return a deep detached native problem receipt."""

        return json.loads(self._receipt_json)


@dataclass(frozen=True, slots=True, init=False)
class RegressionReceipt:
    """Immutable owner of one validated native receipt envelope."""

    _receipt_json: bytes = field(repr=False)
    _problem_fingerprint: str
    _row_ids: tuple[str, ...]
    _source_ids: tuple[str, ...]
    _parameter_keys: tuple[str, ...]
    _parameter_values: tuple[float, ...]
    _termination_type: str
    _solution_usable: bool
    _success: bool
    _objective: float

    def __init__(self) -> None:
        raise TypeError(
            "RegressionReceipt is created only from an authoritative native receipt."
        )

    @classmethod
    def from_native(
        cls,
        payload: Mapping[str, Any],
        *,
        operation: Literal["fit", "evaluate"],
    ) -> RegressionReceipt:
        if operation not in {"fit", "evaluate"}:
            raise InputError(f"unsupported regression receipt operation: {operation!r}.")
        values = _string_mapping(payload, "native regression receipt")
        required = set(_COMMON_NATIVE_FIELDS)
        if operation == "fit":
            required.update(_SOLVE_NATIVE_FIELDS)
        missing = sorted(required - set(values))
        if missing:
            raise InputError(
                "missing native receipt field(s): " + ", ".join(missing) + "."
            )
        version = values["receipt_schema_version"]
        if type(version) is not int or version != _RECEIPT_SCHEMA_VERSION:
            raise InputError(
                f"unsupported native regression receipt schema version: {version!r}."
            )

        problem_receipt = _string_mapping(
            values["problem_receipt"], "native problem receipt"
        )
        missing_problem_fields = sorted(
            _PROBLEM_RECEIPT_FIELDS - set(problem_receipt)
        )
        if missing_problem_fields:
            raise InputError(
                "missing native problem receipt field(s): "
                + ", ".join(missing_problem_fields)
                + "."
            )
        if problem_receipt["contract_id"] != "epcsaft.regression.native-problem":
            raise InputError("native problem receipt contract_id is unsupported.")
        if (
            type(problem_receipt["schema_version"]) is not int
            or problem_receipt["schema_version"] != 1
        ):
            raise InputError("native problem receipt schema_version is unsupported.")

        problem_fingerprint = _sha256(
            values["problem_fingerprint"], "problem_fingerprint"
        )
        if problem_receipt["problem_fingerprint"] != problem_fingerprint:
            raise InputError("native problem fingerprints do not match.")

        row_ids = _string_tuple(problem_receipt["row_ids"], "row_ids")
        source_ids = _string_tuple(problem_receipt["source_ids"], "source_ids")
        parameter_keys = _string_tuple(
            problem_receipt["parameter_keys"], "parameter_keys"
        )
        if not row_ids:
            raise InputError("native problem receipt requires at least one row_id.")
        if not parameter_keys:
            raise InputError("native problem receipt requires at least one parameter_key.")
        if len(row_ids) != len(source_ids):
            raise InputError("native problem row_ids and source_ids have different sizes.")
        _validate_problem_receipt_details(
            problem_receipt,
            row_ids=row_ids,
            source_ids=source_ids,
            parameter_keys=parameter_keys,
        )

        parameter_values = _finite_tuple(
            values["parameter_values"], "parameter_values"
        )
        if len(parameter_values) != len(parameter_keys):
            raise InputError(
                "native receipt parameter_values do not match parameter_keys."
            )
        row_diagnostics = _diagnostics(
            values["row_diagnostics"], row_ids=row_ids, source_ids=source_ids
        )
        objective = _finite_float(values["objective"], "objective")
        _validate_jacobian(
            values,
            row_count=len(row_ids),
            parameter_count=len(parameter_keys),
        )
        derivative_complete = _validate_derivative_metadata(
            values["derivative_metadata"], parameter_keys
        )
        _validate_effective_options(
            values["effective_ceres_options"], operation=operation
        )

        termination_type = _nonblank(values["termination_type"], "termination_type")
        solution_usable = _strict_bool(values["solution_usable"], "solution_usable")
        success = _strict_bool(values["success"], "success")
        if operation == "fit":
            _validate_fit_fields(values)
            allowed_terminations = {
                "CONVERGENCE",
                "FAILURE",
                "NO_CONVERGENCE",
                "USER_FAILURE",
                "USER_SUCCESS",
            }
            if termination_type not in allowed_terminations:
                raise InputError("native fit termination_type is unsupported.")
            expected_success = (
                termination_type in {"CONVERGENCE", "USER_SUCCESS"}
                and solution_usable
                and derivative_complete
            )
        else:
            if termination_type != "EVALUATION_ONLY":
                raise InputError(
                    "native regression evaluation must report EVALUATION_ONLY termination."
                )
            expected_success = solution_usable and derivative_complete
        if success is not expected_success:
            raise InputError(
                "native regression success is inconsistent with termination, "
                "solution usability, or derivative completeness."
            )

        canonical = _canonical_json(values, "native regression receipt")
        # The canonicalization above is also the final recursive finite/JSON-shape check.
        instance = object.__new__(cls)
        for name, value in (
            ("_receipt_json", canonical),
            ("_problem_fingerprint", problem_fingerprint),
            ("_row_ids", row_ids),
            ("_source_ids", source_ids),
            ("_parameter_keys", parameter_keys),
            ("_parameter_values", parameter_values),
            ("_termination_type", termination_type),
            ("_solution_usable", solution_usable),
            ("_success", success),
            ("_objective", objective),
        ):
            object.__setattr__(instance, name, value)
        return instance

    @property
    def receipt_schema_version(self) -> int:
        return _RECEIPT_SCHEMA_VERSION

    @property
    def problem_fingerprint(self) -> str:
        return self._problem_fingerprint

    @property
    def problem_receipt(self) -> dict[str, Any]:
        return self.to_dict()["problem_receipt"]

    @property
    def row_ids(self) -> tuple[str, ...]:
        return self._row_ids

    @property
    def source_ids(self) -> tuple[str, ...]:
        return self._source_ids

    @property
    def parameter_keys(self) -> tuple[str, ...]:
        return self._parameter_keys

    @property
    def parameter_values(self) -> tuple[float, ...]:
        return self._parameter_values

    @property
    def termination_type(self) -> str:
        return self._termination_type

    @property
    def solution_usable(self) -> bool:
        return self._solution_usable

    @property
    def success(self) -> bool:
        return self._success

    @property
    def objective(self) -> float:
        return self._objective

    @property
    def row_diagnostics(self) -> tuple[dict[str, Any], ...]:
        return tuple(self.to_dict()["row_diagnostics"])

    @property
    def effective_ceres_options(self) -> dict[str, Any]:
        return self.to_dict()["effective_ceres_options"]

    @property
    def derivative_metadata(self) -> dict[str, Any]:
        return self.to_dict()["derivative_metadata"]

    @property
    def canonical_json(self) -> bytes:
        """Return the immutable canonical receipt bytes."""

        return self._receipt_json

    def to_dict(self) -> dict[str, Any]:
        """Return a deep detached representation of the validated receipt."""

        return json.loads(self._receipt_json)


@dataclass(frozen=True, slots=True)
class FitResult:
    """Receipt-backed result of one configured native fit."""

    problem: FitProblem
    receipt: RegressionReceipt

    def __post_init__(self) -> None:
        _require_matching_problem(self.problem, self.receipt)

    @property
    def success(self) -> bool:
        return self.receipt.success

    @property
    def objective(self) -> float:
        return self.receipt.objective

    @property
    def final_parameters(self) -> dict[str, float]:
        return dict(zip(self.problem.parameter_keys, self.receipt.parameter_values, strict=True))

    @property
    def row_diagnostics(self) -> tuple[dict[str, Any], ...]:
        return self.receipt.row_diagnostics

    def to_dict(self) -> dict[str, Any]:
        return {
            "problem": self.problem.to_dict(),
            "receipt": self.receipt.to_dict(),
            "final_parameters": self.final_parameters,
        }


@dataclass(frozen=True, slots=True)
class RegressionEvaluation:
    """Receipt-backed evaluation of an existing fitted problem."""

    problem: FitProblem
    receipt: RegressionReceipt

    def __post_init__(self) -> None:
        _require_matching_problem(self.problem, self.receipt)

    @property
    def success(self) -> bool:
        return self.receipt.success

    @property
    def objective(self) -> float:
        return self.receipt.objective

    @property
    def parameter_values(self) -> dict[str, float]:
        return dict(zip(self.problem.parameter_keys, self.receipt.parameter_values, strict=True))

    @property
    def row_diagnostics(self) -> tuple[dict[str, Any], ...]:
        return self.receipt.row_diagnostics

    def to_dict(self) -> dict[str, Any]:
        return {
            "problem": self.problem.to_dict(),
            "receipt": self.receipt.to_dict(),
            "parameter_values": self.parameter_values,
        }


def _require_matching_problem(
    problem: FitProblem,
    receipt: RegressionReceipt,
) -> None:
    if not isinstance(problem, FitProblem) or not isinstance(receipt, RegressionReceipt):
        raise InputError("receipt-backed results require FitProblem and RegressionReceipt.")
    if problem.problem_fingerprint != receipt.problem_fingerprint:
        raise InputError("result receipt does not match its FitProblem.")
    if _canonical_json(problem.to_dict(), "FitProblem receipt") != _canonical_json(
        receipt.problem_receipt, "result problem receipt"
    ):
        raise InputError("result problem receipt does not exactly match its FitProblem.")


def _string_mapping(payload: Any, context: str) -> dict[str, Any]:
    if not isinstance(payload, Mapping) or any(type(key) is not str for key in payload):
        raise InputError(f"{context} must be a string-keyed mapping.")
    return dict(payload)


def _sequence(payload: Any, context: str) -> tuple[Any, ...]:
    if isinstance(payload, (str, bytes)) or not isinstance(payload, Sequence):
        raise InputError(f"{context} must be an ordered sequence.")
    return tuple(payload)


def _string_tuple(payload: Any, context: str) -> tuple[str, ...]:
    values = _sequence(payload, context)
    return tuple(_nonblank(value, context) for value in values)


def _finite_tuple(payload: Any, context: str) -> tuple[float, ...]:
    return tuple(_finite_float(value, context) for value in _sequence(payload, context))


def _nonblank(value: Any, context: str) -> str:
    if type(value) is not str or not value.strip():
        raise InputError(f"{context} must be nonblank.")
    return value.strip()


def _sha256(value: Any, context: str) -> str:
    result = _nonblank(value, context)
    if len(result) != 64 or any(
        character not in "0123456789abcdef" for character in result
    ):
        raise InputError(f"{context} must be a lowercase SHA-256 value.")
    return result


def _finite_float(value: Any, context: str) -> float:
    if isinstance(value, bool) or not isinstance(value, Real):
        raise InputError(f"{context} must be finite.")
    result = float(value)
    if not math.isfinite(result):
        raise InputError(f"{context} must be finite.")
    return result


def _require_fields(
    values: Mapping[str, Any],
    required: frozenset[str],
    context: str,
) -> None:
    missing = sorted(required - set(values))
    if missing:
        raise InputError(
            f"missing native {context} field(s): " + ", ".join(missing) + "."
        )


def _validate_problem_receipt_details(
    receipt: Mapping[str, Any],
    *,
    row_ids: tuple[str, ...],
    source_ids: tuple[str, ...],
    parameter_keys: tuple[str, ...],
) -> None:
    _nonblank(receipt["dataset_id"], "native problem dataset_id")
    definition_fingerprint = _sha256(
        receipt["provider_definition_fingerprint"],
        "native provider definition fingerprint",
    )
    snapshot_fingerprints = _string_tuple(
        receipt["snapshot_fingerprints"], "snapshot_fingerprints"
    )
    for fingerprint in snapshot_fingerprints:
        _sha256(fingerprint, "native snapshot fingerprint")

    provider_handles = _sequence(receipt["provider_handles"], "provider_handles")
    if not provider_handles or len(provider_handles) != len(snapshot_fingerprints):
        raise InputError(
            "native provider_handles must match the ordered snapshot_fingerprints."
        )
    for index, record in enumerate(provider_handles):
        values = _string_mapping(record, "native provider handle receipt")
        _require_fields(values, _PROVIDER_HANDLE_FIELDS, "provider handle receipt")
        if (
            _sha256(
                values["definition_fingerprint_sha256"],
                "provider handle definition fingerprint",
            )
            != definition_fingerprint
        ):
            raise InputError("native provider handle definition fingerprint is inconsistent.")
        if (
            _sha256(
                values["snapshot_fingerprint_sha256"],
                "provider handle snapshot fingerprint",
            )
            != snapshot_fingerprints[index]
        ):
            raise InputError("native provider handle snapshot order is inconsistent.")
        components = _string_tuple(values["component_order"], "component_order")
        composition = _finite_tuple(
            values["canonical_composition"], "canonical_composition"
        )
        if not components or len(components) != len(composition):
            raise InputError(
                "native provider handle component_order and composition do not match."
            )
        if any(value < 0.0 for value in composition) or not math.isclose(
            math.fsum(composition), 1.0, rel_tol=0.0, abs_tol=1.0e-12
        ):
            raise InputError("native provider handle composition is not canonical.")
        if _finite_float(values["temperature_K"], "provider handle temperature_K") <= 0.0:
            raise InputError("native provider handle temperature_K must be positive.")
        _nonblank(values["composition_basis"], "provider handle composition_basis")

    row_records = _sequence(receipt["rows"], "native problem rows")
    if len(row_records) != len(row_ids):
        raise InputError("native problem rows do not match row_ids.")
    for index, record in enumerate(row_records):
        values = _string_mapping(record, "native problem row")
        _require_fields(values, _ROW_RECEIPT_FIELDS, "problem row")
        if values["row_id"] != row_ids[index] or values["source_id"] != source_ids[index]:
            raise InputError("native problem rows are not in declared row/source order.")
        _nonblank(values["source_kind"], "native row source_kind")
        _nonblank(values["target_family"], "native row target_family")
        _nonblank(values["derivative_owner"], "native row derivative_owner")
        handle_indices = _sequence(
            values["provider_handle_indices"], "provider_handle_indices"
        )
        if not handle_indices or any(
            type(value) is not int
            or value < 0
            or value >= len(provider_handles)
            for value in handle_indices
        ):
            raise InputError("native row provider_handle_indices are invalid.")
        if len(set(handle_indices)) != len(handle_indices):
            raise InputError("native row provider_handle_indices must be unique.")
        for key in ("pressure_Pa", "weight", "residual_scale"):
            if _finite_float(values[key], f"native row {key}") <= 0.0:
                raise InputError(f"native row {key} must be positive.")
        _finite_float(values["target_value"], "native row target_value")
        _finite_float(values["model_intercept"], "native row model_intercept")
        _finite_tuple(values["parameter_coefficients"], "parameter_coefficients")

    parameter_records = _sequence(
        receipt["parameters"], "native problem parameters"
    )
    if len(parameter_records) != len(parameter_keys):
        raise InputError("native problem parameters do not match parameter_keys.")
    for index, record in enumerate(parameter_records):
        values = _string_mapping(record, "native fitted parameter")
        _require_fields(values, _PARAMETER_RECEIPT_FIELDS, "fitted parameter")
        if values["key"] != parameter_keys[index]:
            raise InputError("native fitted parameters are not in declared key order.")
        _nonblank(values["target_kind"], "native fitted target_kind")
        if type(values["first_index"]) is not int or type(values["second_index"]) is not int:
            raise InputError("native fitted parameter indices must be integers.")
        start = _finite_float(values["start"], "native fitted start")
        lower = _finite_float(values["lower"], "native fitted lower")
        upper = _finite_float(values["upper"], "native fitted upper")
        if lower >= upper or not lower <= start <= upper:
            raise InputError("native fitted parameter bounds are invalid.")

    fixed_records = _sequence(
        receipt["fixed_parameter_fingerprints"],
        "fixed_parameter_fingerprints",
    )
    for record in fixed_records:
        values = _string_mapping(record, "fixed parameter fingerprint")
        _require_fields(
            values,
            frozenset({"record_id", "sha256"}),
            "fixed parameter fingerprint",
        )
        _nonblank(values["record_id"], "fixed parameter record_id")
        _sha256(values["sha256"], "fixed parameter fingerprint")

    controls = _string_mapping(receipt["controls"], "native problem controls")
    _require_fields(controls, _CONTROL_RECEIPT_FIELDS, "problem controls")
    _nonblank(controls["loss"], "native problem loss")
    iterations = controls["max_num_iterations"]
    if type(iterations) is not int or iterations <= 0:
        raise InputError("native problem max_num_iterations must be positive.")
    for key in (
        "function_tolerance",
        "gradient_tolerance",
        "parameter_tolerance",
    ):
        if _finite_float(controls[key], f"native problem {key}") <= 0.0:
            raise InputError(f"native problem {key} must be positive.")


def _strict_bool(value: Any, context: str) -> bool:
    if type(value) is not bool:
        raise InputError(f"{context} must be a boolean.")
    return value


def _diagnostics(
    payload: Any,
    *,
    row_ids: tuple[str, ...],
    source_ids: tuple[str, ...],
) -> tuple[dict[str, Any], ...]:
    records = _sequence(payload, "row_diagnostics")
    if len(records) != len(row_ids):
        raise InputError("native row_diagnostics do not match row_ids.")
    diagnostics: list[dict[str, Any]] = []
    required = {"row_id", "source_id", "raw_residual", "weighted_residual"}
    for index, record in enumerate(records):
        values = _string_mapping(record, "row diagnostic")
        missing = sorted(required - set(values))
        if missing:
            raise InputError(
                "missing native row diagnostic field(s): " + ", ".join(missing) + "."
            )
        if values["row_id"] != row_ids[index] or values["source_id"] != source_ids[index]:
            raise InputError("native row diagnostics are not in compiled row order.")
        _finite_float(values["raw_residual"], "raw_residual")
        _finite_float(values["weighted_residual"], "weighted_residual")
        diagnostics.append(values)
    return tuple(diagnostics)


def _validate_jacobian(
    values: Mapping[str, Any],
    *,
    row_count: int,
    parameter_count: int,
) -> None:
    shape = _sequence(values["jacobian_shape"], "jacobian_shape")
    if len(shape) != 2 or any(type(value) is not int for value in shape):
        raise InputError("native jacobian_shape must contain two integers.")
    if shape != (row_count, parameter_count):
        raise InputError("native jacobian_shape does not match the compiled problem.")
    jacobian = _finite_tuple(values["jacobian_row_major"], "jacobian_row_major")
    if len(jacobian) != row_count * parameter_count:
        raise InputError("native jacobian size does not match jacobian_shape.")


def _validate_derivative_metadata(
    payload: Any,
    parameter_keys: tuple[str, ...],
) -> bool:
    values = _string_mapping(payload, "derivative_metadata")
    required = {"complete", "parameter_keys", "column_owners"}
    missing = sorted(required - set(values))
    if missing:
        raise InputError(
            "missing native derivative metadata field(s): " + ", ".join(missing) + "."
        )
    complete = _strict_bool(values["complete"], "derivative_metadata.complete")
    if _string_tuple(values["parameter_keys"], "derivative parameter_keys") != parameter_keys:
        raise InputError("native derivative parameter_keys do not match the problem.")
    if len(_string_tuple(values["column_owners"], "derivative column_owners")) != len(
        parameter_keys
    ):
        raise InputError("native derivative column_owners do not match parameter_keys.")
    return complete


def _validate_fit_fields(values: Mapping[str, Any]) -> None:
    iterations = values["iterations"]
    if type(iterations) is not int or iterations < 0:
        raise InputError("native fit iterations must be a non-negative integer.")
    _finite_float(values["initial_cost"], "initial_cost")
    _finite_float(values["final_cost"], "final_cost")
    _nonblank(values["message"], "message")


def _validate_effective_options(
    payload: Any,
    *,
    operation: Literal["fit", "evaluate"],
) -> None:
    values = _string_mapping(payload, "effective_ceres_options")
    if operation == "evaluate":
        if values:
            raise InputError(
                "native regression evaluation cannot report effective Ceres options."
            )
        return
    expected = {
        "max_num_iterations",
        "function_tolerance",
        "gradient_tolerance",
        "parameter_tolerance",
    }
    missing = sorted(expected - set(values))
    unknown = sorted(set(values) - expected)
    if missing or unknown:
        details = []
        if missing:
            details.append("missing: " + ", ".join(missing))
        if unknown:
            details.append("unknown: " + ", ".join(unknown))
        raise InputError("invalid effective Ceres options (" + "; ".join(details) + ").")
    iterations = values["max_num_iterations"]
    if type(iterations) is not int or iterations <= 0:
        raise InputError("effective max_num_iterations must be a positive integer.")
    for key in (
        "function_tolerance",
        "gradient_tolerance",
        "parameter_tolerance",
    ):
        value = _finite_float(values[key], f"effective {key}")
        if value <= 0.0:
            raise InputError(f"effective {key} must be positive.")


def _canonical_json(payload: Any, context: str) -> bytes:
    try:
        return json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise InputError(f"{context} is not canonical JSON data.") from exc


__all__ = [
    "FitProblem",
    "FitResult",
    "RegressionEvaluation",
    "RegressionReceipt",
]
