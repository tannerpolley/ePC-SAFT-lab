"""Provider-native SDK discovery for extension package builds."""

from __future__ import annotations

import copy
import importlib
from typing import Any

_PROVIDER_NATIVE_SDK: dict[str, Any] = {
    "contract_id": "provider_native_sdk_v1",
    "provider_api_contract_id": "provider_api_v1",
    "owner_package": "epcsaft",
    "native_target": "epcsaft_provider_native",
    "required_native_dependencies": ["cppad", "eigen"],
    "forbidden_native_dependencies": ["ceres", "ipopt"],
    "extension_consumers": ["epcsaft-equilibrium", "epcsaft-regression"],
    "stable_python_surface": (
        "epcsaft.ParameterSet, epcsaft.ModelOptions, epcsaft.Mixture, "
        "epcsaft.State, epcsaft.runtime_build_info, epcsaft.provider_native_sdk"
    ),
    "transition_workspace_target": True,
}


def _native_provider_sdk_metadata() -> dict[str, Any] | None:
    try:
        core = importlib.import_module("epcsaft._core")
    except (ImportError, OSError):
        return None
    try:
        payload = core._native_provider_sdk_contract()
    except AttributeError:
        return None
    return dict(payload)


def provider_native_sdk() -> dict[str, Any]:
    """Return the provider-native SDK contract used by extension packages."""

    payload = copy.deepcopy(_PROVIDER_NATIVE_SDK)
    native_payload = _native_provider_sdk_metadata()
    payload["native_contract_exported"] = native_payload is not None
    payload["native_metadata"] = native_payload or {}
    return payload
