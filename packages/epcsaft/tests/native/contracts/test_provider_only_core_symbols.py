from __future__ import annotations

from pathlib import Path

import epcsaft
import epcsaft._core as _core

REPO_ROOT = Path(__file__).resolve().parents[5]
PROVIDER_NATIVE_ROOT = REPO_ROOT / "packages" / "epcsaft" / "src" / "epcsaft" / "native"

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


def test_provider_local_phase_derivative_contract_is_objective_free() -> None:
    provider_eos_text = "\n".join(
        path.read_text(encoding="utf-8")
        for path in sorted((PROVIDER_NATIVE_ROOT / "eos").rglob("*"))
        if path.suffix in {".cpp", ".h"}
    )
    forbidden_provider_tokens = (
        "eos_phase_objective_derivatives_cpp",
        "eos_phase_temperature_variable_derivatives_cpp",
        "objective_hessian_row_major",
        "target_pressure",
        "pressure_work",
    )

    for token in forbidden_provider_tokens:
        assert token not in provider_eos_text

    provider_sdk_manifest = (
        PROVIDER_NATIVE_ROOT.parent / "native_sdk" / "provider_native_sdk_v1" / "provider_sources.json"
    ).read_text(encoding="utf-8")
    provider_sdk_cmake = (
        PROVIDER_NATIVE_ROOT.parent / "native_sdk" / "provider_native_sdk_v1" / "epcsaft_provider_sdk.cmake"
    ).read_text(encoding="utf-8")

    assert "eos/derivatives/phase/local_helmholtz_derivatives.cpp" in provider_sdk_manifest
    assert "eos/derivatives/phase/local_helmholtz_derivatives.cpp" in provider_sdk_cmake
    assert "eos/derivatives/phase/objective_derivatives.cpp" not in provider_sdk_manifest
    assert "eos/derivatives/phase/objective_derivatives.cpp" not in provider_sdk_cmake
