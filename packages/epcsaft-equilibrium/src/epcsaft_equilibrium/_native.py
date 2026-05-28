"""Provider-native bridge for the equilibrium extension."""

from __future__ import annotations

from importlib import import_module
from typing import Any

from epcsaft import provider_native_sdk


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
    return import_module("epcsaft._core")
