"""Workspace shell for the future ePC-SAFT regression extension."""

from __future__ import annotations

__version__ = "0.1.0"


def provider_contract() -> dict[str, object]:
    return {
        "provider_package": "epcsaft",
        "provider_api_contract_id": "provider_api_v1",
        "provider_native_sdk_contract_id": "provider_native_sdk_v1",
    }


def capabilities() -> dict[str, object]:
    return {
        "package": "epcsaft-regression",
        "owner": "regression_extension",
        "status": "workspace_shell_pre_migration",
        "provider_contract": provider_contract(),
        "requires": ["epcsaft", "cppad", "ceres"],
        "forbidden_default_dependencies": ["ipopt"],
        "production_routes_available": False,
    }


__all__ = ["__version__", "capabilities", "provider_contract"]
