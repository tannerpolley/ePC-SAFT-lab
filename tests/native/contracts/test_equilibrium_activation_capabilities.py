from __future__ import annotations

import epcsaft
import pytest
from epcsaft import _core


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
    assert activation["production_families"] == ["bubble_dew_derived_routes"]
    assert activation["declared_not_exposed_families"] == [
        "neutral_tp_flash",
        "neutral_lle",
        "electrolyte_lle",
        "reactive_speciation",
        "reactive_lle",
        "reactive_electrolyte_lle",
    ]
    assert capabilities["production_families"] == ["bubble_dew_derived_routes"]
    assert capabilities["public_routes"] == ["Equilibrium.bubble_pressure"]
    assert capabilities["bubble_dew_derived_routes"]["entrypoint"] == "Equilibrium(mixture).bubble_pressure"
    assert capabilities["bubble_dew_derived_routes"]["available"] is capabilities["activation_matrix"][
        "ipopt_available"
    ]

    deleted_route_keys = {
        "neutral_tp_flash",
        "neutral_lle_flash",
        "neutral_stability",
        "electrolyte_lle",
        "electrolyte_bubble_pressure",
        "electrolyte_stability",
        "reactive_speciation",
        "reactive_stability",
    }
    assert deleted_route_keys.isdisjoint(capabilities)
