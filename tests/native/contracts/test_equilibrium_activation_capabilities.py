from __future__ import annotations

import epcsaft
import pytest
import epcsaft._core as _core


def test_generated_activation_mirror_matches_native_source_of_truth() -> None:
    try:
        from epcsaft.runtime.equilibrium_activation import EQUILIBRIUM_ACTIVATION_MATRIX
    except ModuleNotFoundError as exc:
        pytest.fail(f"missing generated activation mirror: {exc}")

    native_rows = list(_core._native_equilibrium_activation_matrix())

    assert EQUILIBRIUM_ACTIVATION_MATRIX == native_rows


def test_runtime_equilibrium_capabilities_are_activation_matrix_driven() -> None:
    native_rows = list(_core._native_equilibrium_activation_matrix())
    capabilities = epcsaft.capabilities()["equilibrium"]
    activation = capabilities["activation_matrix"]

    assert activation["source"] == "native_cpp"
    assert activation["rows"] == native_rows
    assert activation["production_families"] == [
        "neutral_tp_flash",
        "neutral_lle",
        "bubble_dew_derived_routes",
    ]
    assert activation["declared_not_exposed_families"] == [
        "electrolyte_lle",
        "reactive_speciation",
        "reactive_lle",
        "reactive_electrolyte_lle",
    ]
    assert capabilities["production_families"] == [
        "neutral_tp_flash",
        "neutral_lle",
        "bubble_dew_derived_routes",
    ]
    assert capabilities["public_routes"] == [
        "bubble_pressure",
        "bubble_temperature",
        "dew_pressure",
        "dew_temperature",
        "flash",
        "lle",
    ]
    assert capabilities["bubble_dew_derived_routes"]["entrypoint"] == ("Equilibrium(mixture, route=..., ...).solve()")
    assert (
        capabilities["bubble_dew_derived_routes"]["available"] is capabilities["activation_matrix"]["ipopt_available"]
    )
    assert (
        capabilities["neutral_tp_flash"]["entrypoint"]
        == "Equilibrium(mixture, route='flash', T=..., P=..., z=...).solve()"
    )
    assert capabilities["neutral_tp_flash"]["available"] is capabilities["activation_matrix"]["ipopt_available"]
    assert capabilities["neutral_lle"]["entrypoint"] == "Equilibrium(mixture, route='lle', T=..., P=..., z=...).solve()"
    assert capabilities["neutral_lle"]["available"] is capabilities["activation_matrix"]["ipopt_available"]
    assert capabilities["problem_objects"]["available"] is True
    assert capabilities["problem_objects"]["entrypoint"] == "Equilibrium(mixture, route=..., ...)"

    deleted_route_keys = {
        "neutral_lle_flash",
        "neutral_stability",
        "electrolyte_lle",
        "electrolyte_bubble_pressure",
        "electrolyte_stability",
        "reactive_speciation",
        "reactive_stability",
    }
    assert deleted_route_keys.isdisjoint(capabilities)
