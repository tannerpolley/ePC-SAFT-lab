"""Provider-native bridge for the equilibrium extension."""

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
    }


def provider_native_core() -> Any:
    sdk = provider_native_sdk()
    if sdk.get("contract_id") != "provider_native_sdk_v1":
        raise RuntimeError("epcsaft-equilibrium requires provider_native_sdk_v1.")
    if sdk.get("native_contract_exported") is not True:
        raise RuntimeError("epcsaft provider native SDK contract is not exported.")
    if sdk.get("equilibrium_native_enabled") is not True:
        raise RuntimeError(
            "epcsaft-equilibrium is a monorepo transition package and requires "
            "an epcsaft build with equilibrium native symbols "
            "(EPCSAFT_ENABLE_EQUILIBRIUM_NATIVE=ON)."
        )
    core = import_module("epcsaft._core")
    missing = [name for name in _REQUIRED_EQUILIBRIUM_SYMBOLS if not hasattr(core, name)]
    if missing:
        raise RuntimeError(
            "epcsaft-equilibrium requires provider native symbols: "
            + ", ".join(_REQUIRED_EQUILIBRIUM_SYMBOLS)
            + ". Missing from epcsaft._core: "
            + ", ".join(missing)
        )
    return core
