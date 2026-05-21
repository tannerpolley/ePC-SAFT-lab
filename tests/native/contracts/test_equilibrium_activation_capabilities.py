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
    assert activation["production_families"] == ["neutral_tp_flash", "bubble_dew_derived_routes"]
    assert activation["declared_not_exposed_families"] == [
        "neutral_lle",
        "electrolyte_lle",
        "reactive_speciation",
        "reactive_lle",
        "reactive_electrolyte_lle",
    ]
    assert capabilities["production_families"] == ["neutral_tp_flash", "bubble_dew_derived_routes"]
    assert capabilities["public_routes"] == [
        "Equilibrium.solve(route='bubble_pressure')",
        "Equilibrium.solve(route='bubble_temperature')",
        "Equilibrium.solve(route='dew_pressure')",
        "Equilibrium.solve(route='dew_temperature')",
        "Equilibrium.solve(route='flash')",
    ]
    assert capabilities["bubble_dew_derived_routes"]["entrypoint"] == (
        "Equilibrium(mixture).solve(route='bubble_pressure'|'bubble_temperature'|'dew_pressure'|'dew_temperature')"
    )
    assert capabilities["bubble_dew_derived_routes"]["available"] is capabilities["activation_matrix"][
        "ipopt_available"
    ]
    assert capabilities["neutral_tp_flash"]["entrypoint"] == "Equilibrium(mixture).solve(route='flash')"
    assert capabilities["neutral_tp_flash"]["available"] is capabilities["activation_matrix"]["ipopt_available"]

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
