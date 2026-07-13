"""Provider-owned discovery for the versioned model-configuration schema."""

from __future__ import annotations

MODEL_CONFIGURATION_SCHEMA = "epcsaft.model-configuration"
MODEL_CONFIGURATION_SCHEMA_VERSION = 1
MODEL_CONFIGURATION_FILENAME = "model_configuration.json"
MODEL_CONFIGURATION_PRESETS: tuple[str, ...] = ()


def model_configuration_capabilities() -> dict[str, object]:
    """Return detached global schema discovery without instance policy."""

    return {
        "schema": MODEL_CONFIGURATION_SCHEMA,
        "supported_schema_versions": [MODEL_CONFIGURATION_SCHEMA_VERSION],
        "filename": MODEL_CONFIGURATION_FILENAME,
        "admitted_presets": list(MODEL_CONFIGURATION_PRESETS),
    }
