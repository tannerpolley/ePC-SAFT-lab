from __future__ import annotations

import epcsaft
import epcsaft.model as model

EXPECTED_DISCOVERY = {
    "schema": "epcsaft.model-configuration",
    "supported_schema_versions": [1],
    "filename": "model_configuration.json",
    "admitted_presets": [],
}


def test_model_configuration_discovery_is_global_and_default_free() -> None:
    model_configuration_capabilities = getattr(model, "model_configuration_capabilities", None)
    assert callable(model_configuration_capabilities)
    discovery = model_configuration_capabilities()

    assert discovery == EXPECTED_DISCOVERY
    assert discovery["admitted_presets"] == []
    assert "formulation" not in discovery
    assert "active" not in discovery


def test_model_configuration_discovery_returns_fresh_nested_containers() -> None:
    model_configuration_capabilities = getattr(model, "model_configuration_capabilities", None)
    assert callable(model_configuration_capabilities)
    first = model_configuration_capabilities()
    first["supported_schema_versions"].append(99)
    first["admitted_presets"].append("invented")

    assert model_configuration_capabilities() == EXPECTED_DISCOVERY


def test_provider_capabilities_nest_only_schema_discovery() -> None:
    capabilities = epcsaft.capabilities()

    assert capabilities["model_configuration"] == EXPECTED_DISCOVERY
    assert "formulation" not in capabilities["model_configuration"]
    assert "active_formulation" not in capabilities
