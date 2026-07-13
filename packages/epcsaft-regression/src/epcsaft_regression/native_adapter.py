"""Typed boundary between compiled regression problems and native records."""

from __future__ import annotations

from importlib import import_module
from typing import Any

from epcsaft import InputError, provider_native_sdk

from .parameters import parse_parameter_key
from .problem import CompiledRegressionProblem
from .targets import TargetFamily

__all__ = [
    "_evaluate_regression",
    "_native_problem_from_compiled",
    "_solve_regression",
    "native_ceres_backend_info",
]

_REQUIRED_REGRESSION_SYMBOLS = (
    "NativeFittedParameter",
    "NativeRegressionControls",
    "NativeRegressionProblem",
    "NativeRegressionRow",
    "_evaluate_regression",
    "_solve_regression",
)


def _regression_native_core() -> Any:
    sdk = provider_native_sdk()
    if sdk.get("contract_id") != "provider_native_sdk_v1":
        raise RuntimeError("epcsaft-regression requires provider_native_sdk_v1.")
    if sdk.get("native_contract_exported") is not True:
        raise RuntimeError("epcsaft provider native SDK contract is not exported.")
    core = import_module("epcsaft_regression._native_core")
    missing = [name for name in _REQUIRED_REGRESSION_SYMBOLS if not hasattr(core, name)]
    if missing:
        raise RuntimeError(
            "epcsaft-regression native typed problem contract is incomplete: "
            + ", ".join(missing)
        )
    return core


def native_ceres_backend_info() -> dict[str, object]:
    try:
        smoke = _regression_native_core()._native_ceres_smoke()
    except (AttributeError, ImportError, OSError, RuntimeError):
        return {
            "backend": "ceres",
            "status": "regression_native_module_missing",
            "required": True,
            "required_for": ["epcsaft-regression"],
            "compiled": False,
            "available": False,
        }
    status = str(smoke.get("status", "ceres_probe_missing"))
    compiled = bool(smoke.get("compiled", False))
    return {
        "backend": "ceres",
        "status": status,
        "required": True,
        "required_for": ["epcsaft-regression"],
        "compiled": compiled,
        "available": status == "enabled_available" and compiled,
    }


def _native_problem_from_compiled(problem: CompiledRegressionProblem) -> Any:
    """Build one native value record while retaining the exact provider handles."""

    if not isinstance(problem, CompiledRegressionProblem):
        raise InputError("native regression dispatch requires CompiledRegressionProblem.")
    core = _regression_native_core()
    handles = problem.native_handles
    if not handles:
        raise InputError("compiled regression problem has no evaluated provider handles.")
    components = tuple(handles[0].component_order)

    native_parameters = []
    for parameter in problem.parameters:
        parsed = parse_parameter_key(parameter.key)
        try:
            first_index = components.index(parsed.owners[0])
            second_index = (
                components.index(parsed.owners[1]) if parsed.is_interaction else -1
            )
        except ValueError as exc:
            raise InputError(
                f"fitted parameter {parameter.key!r} does not match the provider component order."
            ) from exc
        native_parameters.append(
            core.NativeFittedParameter(
                parameter.key,
                parsed.provider_field,
                first_index,
                second_index,
                parameter.start,
                parameter.lower,
                parameter.upper,
            )
        )

    native_rows = []
    handle_cursor = 0
    for row in problem.rows:
        handle_count = 2 if row.target_family is TargetFamily.BINARY_VLE else 1
        handle_indices = tuple(range(handle_cursor, handle_cursor + handle_count))
        handle_cursor += handle_count
        native_rows.append(
            core.NativeRegressionRow(
                row.row_id,
                row.source.source_id,
                row.source.source_kind.value,
                row.target_family.value,
                handle_indices,
                row.conditions["pressure"],
                row.weight,
                row.residual_scale,
                float(row.observations.get("target", 0.0)),
                0.0,
                (),
                "pending_resolved_input_overlay",
            )
        )
    if handle_cursor != len(handles):
        raise InputError("compiled row-to-provider-handle ownership is inconsistent.")

    controls = core.NativeRegressionControls(
        problem.controls.loss.value,
        problem.controls.max_num_iterations,
        problem.controls.function_tolerance,
        problem.controls.gradient_tolerance,
        problem.controls.parameter_tolerance,
    )
    return core.NativeRegressionProblem(
        problem.dataset_id,
        problem.provider_definition_fingerprint,
        handles,
        problem.fixed_parameter_fingerprints,
        tuple(native_rows),
        tuple(native_parameters),
        controls,
    )


def _solve_regression(problem: CompiledRegressionProblem) -> dict[str, Any]:
    return _regression_native_core()._solve_regression(
        _native_problem_from_compiled(problem)
    )


def _evaluate_regression(
    problem: CompiledRegressionProblem,
    parameter_values: tuple[float, ...],
) -> dict[str, Any]:
    return _regression_native_core()._evaluate_regression(
        _native_problem_from_compiled(problem),
        parameter_values,
    )
