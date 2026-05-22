from __future__ import annotations

from pathlib import Path

import pytest

import epcsaft
from epcsaft._types import InputError
from tests.support.native_cases import _neutral_state


def _state():
    mix, _species, _pressure, density, temperature, composition = _neutral_state()
    return mix.state(T=temperature, x=composition, rho=density)


def test_capabilities_expose_property_derivative_result_apis() -> None:
    capabilities = epcsaft.capabilities()

    payload = capabilities["derivatives"]["property_derivative_result_apis"]

    assert payload["available"] is True
    assert "outputs" in payload["result_shape"]
    assert "variables" in payload["result_shape"]
    assert "derivative_backend" in payload["result_shape"]
    assert "pressure_density_derivative_result" in payload["state_methods"]
    assert "relative_permittivity_parameter_derivative_result" in payload["state_methods"]
    assert "numerical" + "_derivative" not in str(payload["backend_labels"])
    assert "unsupported" not in str(payload["backend_labels"])
    parameter_families = payload["parameter_families"]
    assert "state_property_derivative_supported" in parameter_families
    assert "regression_public_production_supported" in parameter_families
    assert "production_supported" not in parameter_families
    assert {"e_assoc", "vol_a", "l_ij", "k_hb_ij"}.issubset(
        set(parameter_families["state_property_derivative_supported"])
    )
    assert {"e_assoc", "vol_a", "l_ij", "k_hb_ij"}.isdisjoint(
        set(parameter_families["regression_public_production_supported"])
    )


def test_core_type_stub_declares_association_component_parameter_binding() -> None:
    stub = Path(epcsaft.__file__).with_name("_core.pyi").read_text(encoding="utf-8")

    assert "def _native_cppad_association_component_parameters" in stub


def test_public_derivative_result_methods_share_required_shape() -> None:
    state = _state()

    for method_name in (
        "pressure_density_derivative_result",
        "ares_composition_derivative_result",
    ):
        result = getattr(state, method_name)()
        assert set(
            ("supported", "backend", "derivative_backend", "message", "value", "jacobian", "outputs", "variables", "shape")
        ).issubset(result)
        assert isinstance(result["shape"], list)
        assert len(result["shape"]) == 2
        assert isinstance(result["outputs"], list)
        assert isinstance(result["variables"], list)
        assert "numerical" + "_derivative" not in str(result).lower()


def test_unsupported_property_derivative_methods_raise() -> None:
    state = _state()

    for method_name in (
        "pressure_composition_derivative_result",
        "pressure_parameter_derivative_result",
        "density_pressure_derivative_result",
        "chemical_potential_composition_derivative_result",
        "chemical_potential_parameter_derivative_result",
        "ln_fugacity_composition_derivative_result",
        "ln_fugacity_parameter_derivative_result",
    ):
        with pytest.raises(InputError, match="unsupported"):
            getattr(state, method_name)()
