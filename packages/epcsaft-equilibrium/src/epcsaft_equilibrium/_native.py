"""Package-owned native bridge for the equilibrium extension."""

from __future__ import annotations

from importlib import import_module
from typing import Any

from epcsaft import provider_native_sdk

_REQUIRED_EQUILIBRIUM_SYMBOLS = (
    "_native_equilibrium_selector_contract",
    "_native_equilibrium_selector_route_result",
    "_native_neutral_two_phase_eos_result",
)


def provider_contract() -> dict[str, object]:
    sdk = provider_native_sdk()
    return {
        "provider_package": "epcsaft",
        "provider_api_contract_id": str(sdk.get("provider_api_contract_id", "")),
        "provider_native_sdk_contract_id": str(sdk.get("contract_id", "")),
        "provider_only_core": bool(sdk.get("provider_only_core", False)),
    }


def extension_native_core() -> Any:
    sdk = provider_native_sdk()
    if sdk.get("contract_id") != "provider_native_sdk_v1":
        raise RuntimeError("epcsaft-equilibrium requires provider_native_sdk_v1.")
    if sdk.get("native_contract_exported") is not True:
        raise RuntimeError("epcsaft provider native SDK contract is not exported.")
    native = import_module("epcsaft_equilibrium._native_core")
    missing = [name for name in _REQUIRED_EQUILIBRIUM_SYMBOLS if not hasattr(native, name)]
    if missing:
        raise RuntimeError(
            "epcsaft-equilibrium requires package-owned native symbols: "
            + ", ".join(_REQUIRED_EQUILIBRIUM_SYMBOLS)
            + ". Missing from epcsaft_equilibrium._native_core: "
            + ", ".join(missing)
        )
    return native


def native_ipopt_backend_info() -> dict[str, object]:
    try:
        smoke = extension_native_core()._native_ipopt_smoke()
    except (AttributeError, ImportError, OSError, RuntimeError):
        return {
            "backend": "ipopt",
            "status": "equilibrium_native_module_missing",
            "required": True,
            "compiled": False,
            "available": False,
            "adapter_available": False,
            "adapter_kind": "native_tnlp_adapter",
            "adapter_source_available": False,
            "requires_exact_gradient": True,
            "requires_exact_jacobian": True,
        }
    status = str(smoke.get("status", "ipopt_probe_missing"))
    compiled = bool(smoke.get("compiled", False))
    return {
        "backend": "ipopt",
        "status": status,
        "required": True,
        "compiled": compiled,
        "available": status == "enabled_available" and compiled,
        "adapter_available": bool(smoke.get("adapter_available", False)),
        "adapter_kind": str(smoke.get("adapter_kind", "native_tnlp_adapter")),
        "adapter_source_available": bool(smoke.get("adapter_source_available", False)),
        "requires_exact_gradient": bool(smoke.get("requires_exact_gradient", True)),
        "requires_exact_jacobian": bool(smoke.get("requires_exact_jacobian", True)),
    }
