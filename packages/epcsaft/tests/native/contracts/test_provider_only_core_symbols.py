from __future__ import annotations

import epcsaft
import epcsaft._core as _core

BLOCKED_EXTENSION_SYMBOLS = (
    "_native_equilibrium_selector_contract",
    "_native_equilibrium_selector_route_result",
    "_native_ipopt_quadratic_smoke",
    "_native_ipopt_smoke",
    "_native_nlp_shape_validation_smoke",
    "_native_second_order_assembly_smoke",
    "_native_variable_transform_smoke",
    "_native_ceres_smoke",
    "_fit_pure_neutral_native_ceres",
    "_fit_pure_neutral_native_debug",
    "_fit_generic_native_ceres",
    "_evaluate_generic_native_debug",
)


def test_provider_native_sdk_reports_provider_only_surface_flags() -> None:
    sdk = epcsaft.provider_native_sdk()

    assert "provider_only_core" in sdk
    assert "equilibrium_native_enabled" in sdk
    assert "regression_native_enabled" in sdk


def test_provider_only_core_does_not_export_extension_native_symbols() -> None:
    sdk = epcsaft.provider_native_sdk()

    assert sdk["provider_only_core"] is True
    assert sdk["equilibrium_native_enabled"] is False
    assert sdk["regression_native_enabled"] is False

    leaked = [name for name in BLOCKED_EXTENSION_SYMBOLS if hasattr(_core, name)]
    assert leaked == []
