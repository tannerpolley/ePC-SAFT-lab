"""Internal adapters for native regression routes."""

from __future__ import annotations

from importlib import import_module
from typing import Any, Mapping, Sequence

import numpy as np

from epcsaft import provider_native_sdk
from epcsaft._types import InputError, vector_to_array
from epcsaft.state.native_adapter import check_association, create_struct

__all__ = [
    "_evaluate_generic_native_debug",
    "_fit_generic_native_ceres",
    "_fit_pure_neutral_native_debug",
    "check_association",
    "create_struct",
    "native_ceres_backend_info",
]

_REQUIRED_REGRESSION_SYMBOLS = (
    "_evaluate_generic_native_debug",
    "_fit_generic_native_ceres",
    "_fit_pure_neutral_native_ceres",
    "_fit_pure_neutral_native_debug",
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
            "epcsaft-regression requires package-owned native symbols: "
            + ", ".join(_REQUIRED_REGRESSION_SYMBOLS)
            + ". Missing from epcsaft_regression._native_core: "
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


def _fit_pure_neutral_native_debug(
    fixed_payload: Mapping[str, Any],
    density_T: Sequence[float],
    density_P: Sequence[float],
    density_rho_exp: Sequence[float],
    density_phase: Sequence[int],
    density_scale: float,
    vle_T: Sequence[float],
    vle_P: Sequence[float],
    pure_vle_scale: float,
    x: Sequence[float],
) -> dict[str, Any]:
    params = check_association(dict(fixed_payload))
    cppargs = create_struct(params)
    core = _regression_native_core()
    result = core._fit_pure_neutral_native_debug(
        cppargs,
        np.asarray(density_T, dtype=float),
        np.asarray(density_P, dtype=float),
        np.asarray(density_rho_exp, dtype=float),
        np.asarray(density_phase, dtype=int),
        float(density_scale),
        np.asarray(vle_T, dtype=float),
        np.asarray(vle_P, dtype=float),
        float(pure_vle_scale),
        np.asarray(x, dtype=float),
    )
    return {
        "objective": float(result["objective"]),
        "gradient": vector_to_array(result["gradient"]),
        "residuals": vector_to_array(result["residuals"]),
        "jacobian_row_major": vector_to_array(result["jacobian_row_major"]),
        "jacobian_shape": (result["jacobian_shape"]),
        "jacobian_available": bool(result.get("jacobian_available", True)),
        "jacobian_backend": str(result.get("jacobian_backend", "unspecified")),
        "density_raw_residuals": vector_to_array(result["density_raw_residuals"]),
        "pure_vle_raw_residuals": vector_to_array(result["pure_vle_raw_residuals"]),
        "residual_evaluations": int(result["residual_evaluations"]),
        "density_solves": int(result["density_solves"]),
        "fused_state_evaluations": int(result["fused_state_evaluations"]),
        "callback_wall_time_s": float(result["callback_wall_time_s"]),
    }


def _native_args_sequence(payloads: Sequence[Mapping[str, Any]]):
    return [create_struct(check_association(dict(payload))) for payload in payloads]


def _fit_generic_native_ceres(
    fixed_payloads: Sequence[Mapping[str, Any]],
    records: Sequence[Mapping[str, Any]],
    target_kinds: Sequence[int],
    target_indices: Sequence[int],
    target_indices_2: Sequence[int],
    x0: Sequence[float],
    lower: Sequence[float],
    upper: Sequence[float],
    max_nfev: int = 200,
) -> dict[str, Any]:
    max_nfev = int(max_nfev)
    if max_nfev < 1:
        raise InputError("Native Ceres generic regression requires max_nfev >= 1.")
    core = _regression_native_core()
    result = core._fit_generic_native_ceres(
        _native_args_sequence(fixed_payloads),
        list(records),
        np.asarray(target_kinds, dtype=int),
        np.asarray(target_indices, dtype=int),
        np.asarray(target_indices_2, dtype=int),
        np.asarray(x0, dtype=float),
        np.asarray(lower, dtype=float),
        np.asarray(upper, dtype=float),
        max_nfev,
    )
    return {
        "x": vector_to_array(result["x"]),
        "cost": float(result["cost"]),
        "residual_norm": float(result["residual_norm"]),
        "initial_cost": float(result["initial_cost"]),
        "initial_residual_norm": float(result["initial_residual_norm"]),
        "metrics_by_term": {str(k): float(v) for k, v in dict(result["metrics_by_term"]).items()},
        "success": bool(result["success"]),
        "status": int(result["status"]),
        "nfev": int(result["nfev"]),
        "iterations": int(result["iterations"]),
        "starts_tried": int(result["starts_tried"]),
        "message": str(result["message"]),
        "backend": str(result["backend"]),
        "optimizer_backend": str(result["optimizer_backend"]),
        "derivative_backend": str(result["derivative_backend"]),
        "jacobian_available": bool(result.get("jacobian_available", True)),
        "jacobian_backend": str(result.get("jacobian_backend", "unspecified")),
    }


def _evaluate_generic_native_debug(
    fixed_payloads: Sequence[Mapping[str, Any]],
    records: Sequence[Mapping[str, Any]],
    target_kinds: Sequence[int],
    target_indices: Sequence[int],
    target_indices_2: Sequence[int],
    x: Sequence[float],
) -> dict[str, Any]:
    core = _regression_native_core()
    result = core._evaluate_generic_native_debug(
        _native_args_sequence(fixed_payloads),
        list(records),
        np.asarray(target_kinds, dtype=int),
        np.asarray(target_indices, dtype=int),
        np.asarray(target_indices_2, dtype=int),
        np.asarray(x, dtype=float),
    )
    return {
        "cost": float(result["cost"]),
        "residual_norm": float(result["residual_norm"]),
        "residuals": vector_to_array(result["residuals"]),
        "metrics_by_term": {str(k): float(v) for k, v in dict(result["metrics_by_term"]).items()},
        "jacobian_row_major": vector_to_array(result.get("jacobian_row_major", [])),
        "jacobian_shape": tuple(result.get("jacobian_shape", (len(result["residuals"]), 0))),
        "jacobian_available": bool(result.get("jacobian_available", True)),
        "jacobian_backend": str(result.get("jacobian_backend", "unspecified")),
    }
