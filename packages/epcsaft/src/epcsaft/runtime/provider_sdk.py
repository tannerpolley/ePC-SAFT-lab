"""Provider-native SDK discovery for extension package builds."""

from __future__ import annotations

import copy
import importlib
from importlib import resources
from pathlib import Path
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


def _provider_source_sdk_paths() -> dict[str, Any]:
    package_root = resources.files("epcsaft")
    sdk_root = package_root.joinpath("native_sdk", "provider_native_sdk_v1")
    cmake_config = sdk_root.joinpath("epcsaft_provider_sdk.cmake")
    source_manifest = sdk_root.joinpath("provider_sources.json")
    include_root = package_root.joinpath("native")
    required_paths = {
        "native_sdk_cmake_config": cmake_config,
        "native_sdk_source_manifest": source_manifest,
        "native_sdk_include_root": include_root,
    }
    absent = [name for name, path in required_paths.items() if not Path(path).exists()]
    if absent:
        joined = ", ".join(absent)
        raise RuntimeError(f"epcsaft provider native SDK package data is incomplete: {joined}.")
    paths = {
        "native_sdk_kind": "source_cmake_sdk",
        "native_sdk_version": "provider_native_sdk_v1",
        "native_sdk_cmake_config": str(cmake_config),
        "native_sdk_source_manifest": str(source_manifest),
        "native_sdk_include_root": str(include_root),
        "supported_extension_native_modules": [
            "epcsaft_equilibrium._native_core",
            "epcsaft_regression._native_core",
        ],
    }
    paths.update(
        {
            "source_sdk_kind": paths["native_sdk_kind"],
            "source_sdk_version": paths["native_sdk_version"],
            "cmake_config_path": paths["native_sdk_cmake_config"],
            "source_manifest_path": paths["native_sdk_source_manifest"],
            "include_root": paths["native_sdk_include_root"],
        }
    )
    return paths


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
    payload.update(_provider_source_sdk_paths())
    native_payload = _native_provider_sdk_metadata()
    payload["native_contract_exported"] = native_payload is not None
    payload["native_metadata"] = native_payload or {}
    payload["provider_only_core"] = bool(payload["native_metadata"].get("provider_only_core", False))
    payload["equilibrium_native_enabled"] = bool(payload["native_metadata"].get("equilibrium_native_enabled", False))
    payload["regression_native_enabled"] = bool(payload["native_metadata"].get("regression_native_enabled", False))
    return payload
