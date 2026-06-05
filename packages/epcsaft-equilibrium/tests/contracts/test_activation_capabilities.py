from __future__ import annotations

import pytest

from epcsaft_equilibrium._native import extension_native_core

_core = extension_native_core()
import epcsaft_equilibrium
from epcsaft_equilibrium.workflows import _EQUILIBRIUM_ROUTE_SPECS

EXPECTED_PUBLIC_ROUTE_FAMILIES = {
    "bubble_pressure": "bubble_dew_derived_routes",
    "bubble_temperature": "bubble_dew_derived_routes",
    "dew_pressure": "bubble_dew_derived_routes",
    "dew_temperature": "bubble_dew_derived_routes",
    "flash": "neutral_tp_flash",
    "lle": "neutral_lle",
    "single_component_vle": "single_component_vle",
}


def _admitted_public_route_map(rows: list[dict[str, object]]) -> dict[str, str]:
    route_map: dict[str, str] = {}
    for row in rows:
        family_key = str(row["key"])
        if not bool(row["production_exposed"]):
            assert row["public_routes"] == []
            continue
        for route in row["public_routes"]:
            assert str(route) not in route_map
            route_map[str(route)] = family_key
    return route_map


def test_generated_activation_mirror_matches_native_source_of_truth() -> None:
    try:
        from epcsaft_equilibrium.equilibrium_activation import EQUILIBRIUM_ACTIVATION_MATRIX
    except ModuleNotFoundError as exc:
        pytest.fail(f"missing generated activation mirror: {exc}")

    native_rows = list(_core._native_equilibrium_activation_matrix())

    assert EQUILIBRIUM_ACTIVATION_MATRIX == native_rows


def test_runtime_equilibrium_capabilities_are_activation_matrix_driven() -> None:
    native_rows = list(_core._native_equilibrium_activation_matrix())
    capabilities = epcsaft_equilibrium.capabilities()
    activation = capabilities["activation_matrix"]
    public_route_map = _admitted_public_route_map(native_rows)

    assert activation["source"] == "native_cpp"
    assert activation["rows"] == native_rows
    assert activation["production_families"] == [
        "neutral_tp_flash",
        "neutral_lle",
        "single_component_vle",
        "bubble_dew_derived_routes",
    ]
    assert activation["declared_not_exposed_families"] == [
        "neutral_multiphase_nonassoc",
        "electrolyte_lle",
        "reactive_speciation",
        "reactive_lle",
        "reactive_electrolyte_lle",
    ]
    assert capabilities["production_families"] == [
        "neutral_tp_flash",
        "neutral_lle",
        "single_component_vle",
        "bubble_dew_derived_routes",
    ]
    assert public_route_map == EXPECTED_PUBLIC_ROUTE_FAMILIES
    assert capabilities["public_routes"] == sorted(EXPECTED_PUBLIC_ROUTE_FAMILIES)
    assert activation["public_routes"] == [
        "bubble_pressure",
        "bubble_temperature",
        "dew_pressure",
        "dew_temperature",
        "flash",
        "lle",
        "single_component_vle",
    ]
    assert activation["public_route_family_map"] == EXPECTED_PUBLIC_ROUTE_FAMILIES
    assert activation["public_routes_by_family"] == {
        "neutral_tp_flash": ["flash"],
        "neutral_lle": ["lle"],
        "single_component_vle": ["single_component_vle"],
        "bubble_dew_derived_routes": [
            "bubble_pressure",
            "bubble_temperature",
            "dew_pressure",
            "dew_temperature",
        ],
    }
    assert {
        route: spec.selector_family for route, spec in _EQUILIBRIUM_ROUTE_SPECS.items()
    } == EXPECTED_PUBLIC_ROUTE_FAMILIES
    assert "neutral_multiphase_nonassoc" not in capabilities["public_routes"]
    assert capabilities["bubble_dew_derived_routes"]["entrypoint"] == ("Equilibrium(mixture, route=..., ...).solve()")
    assert capabilities["bubble_dew_derived_routes"]["public_routes"] == [
        "bubble_pressure",
        "bubble_temperature",
        "dew_pressure",
        "dew_temperature",
    ]
    assert (
        capabilities["bubble_dew_derived_routes"]["available"] is capabilities["activation_matrix"]["ipopt_available"]
    )
    assert (
        capabilities["neutral_tp_flash"]["entrypoint"]
        == "Equilibrium(mixture, route='flash', T=..., P=..., z=...).solve()"
    )
    assert capabilities["neutral_tp_flash"]["public_routes"] == ["flash"]
    assert capabilities["neutral_tp_flash"]["available"] is capabilities["activation_matrix"]["ipopt_available"]
    assert capabilities["neutral_lle"]["entrypoint"] == "Equilibrium(mixture, route='lle', T=..., P=..., z=...).solve()"
    assert capabilities["neutral_lle"]["public_routes"] == ["lle"]
    assert capabilities["neutral_lle"]["available"] is capabilities["activation_matrix"]["ipopt_available"]
    assert (
        capabilities["single_component_vle"]["entrypoint"]
        == "Equilibrium(mixture, route='single_component_vle', T=...).solve()"
    )
    assert capabilities["single_component_vle"]["public_routes"] == ["single_component_vle"]
    assert capabilities["single_component_vle"]["input_scope"] == "single neutral non-reactive non-electrolyte component"
    assert capabilities["single_component_vle"]["available"] is capabilities["activation_matrix"]["ipopt_available"]
    assert capabilities["problem_objects"]["available"] is True
    assert capabilities["problem_objects"]["entrypoint"] == "Equilibrium(mixture, route=..., ...)"
    assert {row["quantity"] for row in capabilities["route_derivative_evidence"]["rows"]} == {
        "bubble_dew_derived_routes",
        "neutral_tp_flash",
        "neutral_lle",
        "single_component_vle",
    }

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
