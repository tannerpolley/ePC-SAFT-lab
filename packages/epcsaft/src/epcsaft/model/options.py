"""Public model configuration for the reset frontend."""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Literal

import numpy as np

from .._types import InputError
from .configuration_catalog import (
    MODEL_CONFIGURATION_FILENAME,
    MODEL_CONFIGURATION_PRESETS,
    MODEL_CONFIGURATION_SCHEMA,
    MODEL_CONFIGURATION_SCHEMA_VERSION,
)


class MissingModelParameterError(InputError):
    """Raised when an enabled model formulation lacks required parameters."""


RelativePermittivityRule = Literal[
    "component_linear",
    "linear",
    "constant",
    "linear_massfraction",
    "linear_saltfraction",
    "salt_free_massfraction",
    "combined",
    "empirical",
    "aqueous_organic",
]
BornDiameterRule = Literal["sigma", "sigma_reduced", "temperature_dependent", "fitted"]
IonDiameterRule = Literal["sigma", "sigma_reduced", "temperature_dependent"]

_RELATIVE_PERMITTIVITY_RULES = {
    "component_linear": "linear",
    "linear": "linear",
    "constant": "constant",
    "linear_massfraction": "linear-massfraction",
    "linear_saltfraction": "linear-saltfraction",
    "salt_free_massfraction": "salt-free-massfraction",
    "combined": "combined",
    "empirical": "empirical",
    "aqueous_organic": "aqueous-organic",
}
_BORN_DIAMETER_MODES = {
    "sigma": "t_indep",
    "sigma_reduced": "t_dep_1",
    "temperature_dependent": "t_dep_2",
    "fitted": "fitted_param",
}
_BORN_BULK_MODES = {"mix", "solvent"}
@dataclass(frozen=True, slots=True)
class DisabledFormulation:
    """Explicit inactive formulation record."""

    enabled: Literal[False]

    def __post_init__(self) -> None:
        if self.enabled is not False:
            raise InputError("disabled formulation enabled must be false.")


@dataclass(frozen=True, slots=True)
class ElectrostaticsOptions:
    """Explicit electrostatics activation record."""

    enabled: Literal[True]

    def __post_init__(self) -> None:
        if self.enabled is not True:
            raise InputError("enabled electrostatics must set enabled to true.")


@dataclass(frozen=True, slots=True)
class RelativePermittivityOptions:
    """Explicit relative-permittivity formulation."""

    enabled: Literal[True]
    rule: RelativePermittivityRule

    def __post_init__(self) -> None:
        if self.enabled is not True:
            raise InputError("enabled relative_permittivity must set enabled to true.")
        if self.rule not in _RELATIVE_PERMITTIVITY_RULES:
            raise InputError("relative_permittivity.rule is unsupported.")


@dataclass(frozen=True, slots=True)
class DebyeHuckelOptions:
    """Explicit Debye-Huckel formulation."""

    enabled: Literal[True]
    ion_diameter_rule: IonDiameterRule
    bjerrum_pairing: bool

    def __post_init__(self) -> None:
        if self.enabled is not True:
            raise InputError("enabled debye_huckel must set enabled to true.")
        if self.ion_diameter_rule not in {"sigma", "sigma_reduced", "temperature_dependent"}:
            raise InputError("debye_huckel.ion_diameter_rule is unsupported.")
        _require_strict_bool(self.bjerrum_pairing, "debye_huckel.bjerrum_pairing")


@dataclass(frozen=True, slots=True)
class BornModelOptions:
    """Complete explicit Born formulation without defaults."""

    enabled: Literal[True]
    born_diameter_rule: BornDiameterRule
    solvation_shell_model: bool
    dielectric_saturation: bool
    bulk_mode: Literal["mix", "solvent"]

    def __post_init__(self) -> None:
        if self.enabled is not True:
            raise InputError("enabled born formulation must set enabled to true.")
        if self.born_diameter_rule not in _BORN_DIAMETER_MODES:
            raise InputError("born.born_diameter_rule is unsupported.")
        _require_strict_bool(self.solvation_shell_model, "born.solvation_shell_model")
        _require_strict_bool(self.dielectric_saturation, "born.dielectric_saturation")
        if self.bulk_mode not in _BORN_BULK_MODES:
            raise InputError("born.bulk_mode must be 'mix' or 'solvent'.")


@dataclass(frozen=True, slots=True)
class SolvatedIonDiameterOptions:
    """Explicit activation of solvated-ion-diameter mixing."""

    enabled: Literal[True]

    def __post_init__(self) -> None:
        if self.enabled is not True:
            raise InputError("enabled solvated_ion_diameter must set enabled to true.")


@dataclass(frozen=True, slots=True)
class IonDispersionOptions:
    """Explicit activation of ion-dispersion mixing."""

    enabled: Literal[True]

    def __post_init__(self) -> None:
        if self.enabled is not True:
            raise InputError("enabled ion_dispersion must set enabled to true.")


@dataclass(frozen=True, slots=True, init=False)
class ModelOptions:
    """Strict version-1 provider formulation configuration."""

    schema: str
    schema_version: int
    selection_origin: Literal["explicit_configuration", "admitted_preset"]
    preset_id: str | None
    electrostatics: DisabledFormulation | ElectrostaticsOptions
    relative_permittivity: DisabledFormulation | RelativePermittivityOptions
    debye_huckel: DisabledFormulation | DebyeHuckelOptions
    born: DisabledFormulation | BornModelOptions
    solvated_ion_diameter: DisabledFormulation | SolvatedIonDiameterOptions
    ion_dispersion: DisabledFormulation | IonDispersionOptions
    _receipt_json: str

    def __init__(self) -> None:
        raise TypeError("ModelOptions must be created with ModelOptions.from_user_options().")

    @classmethod
    def from_user_options(
        cls,
        value: str | Path | Mapping[str, Any] | ModelOptions,
    ) -> ModelOptions:
        """Parse one strict version-1 configuration mapping, file, or folder."""

        return _parse_model_configuration(value)

    @property
    def receipt(self) -> dict[str, Any]:
        """Return a detached canonical configuration receipt."""

        return json.loads(self._receipt_json)


_FORMULATION_KEYS = {
    "electrostatics",
    "relative_permittivity",
    "debye_huckel",
    "born",
    "solvated_ion_diameter",
    "ion_dispersion",
}


def _parse_model_configuration(
    value: str | Path | Mapping[str, Any] | ModelOptions,
) -> ModelOptions:
    if isinstance(value, ModelOptions):
        return value
    if isinstance(value, (str, Path)):
        payload = _read_model_configuration_payload(Path(value).expanduser())
    elif isinstance(value, Mapping):
        payload = dict(value)
    else:
        raise InputError("model configuration must be a mapping, JSON file, folder, or ModelOptions instance.")

    _require_exact_keys(
        payload,
        required={"schema", "schema_version", "selection_origin"},
        allowed={"schema", "schema_version", "selection_origin", "formulation", "preset_id"},
        context="model configuration",
    )
    schema = payload["schema"]
    if type(schema) is not str or schema != MODEL_CONFIGURATION_SCHEMA:
        raise InputError(f"model configuration schema must be {MODEL_CONFIGURATION_SCHEMA!r}.")
    schema_version = payload["schema_version"]
    if type(schema_version) is not int or schema_version != MODEL_CONFIGURATION_SCHEMA_VERSION:
        raise InputError(f"model configuration schema_version must be {MODEL_CONFIGURATION_SCHEMA_VERSION}.")
    selection_origin = payload["selection_origin"]
    if type(selection_origin) is not str:
        raise InputError("model configuration selection_origin must be a string.")
    if selection_origin == "admitted_preset":
        if "formulation" in payload:
            raise InputError("admitted preset selection cannot include an explicit formulation.")
        if "preset_id" not in payload:
            raise InputError("model configuration is missing required key: preset_id.")
        if not MODEL_CONFIGURATION_PRESETS:
            raise InputError("the provider has no admitted presets.")
        raise InputError(f"model configuration preset_id {payload['preset_id']!r} is not admitted.")
    if selection_origin != "explicit_configuration":
        raise InputError("selection_origin must be 'explicit_configuration' or 'admitted_preset'.")
    if "preset_id" in payload:
        raise InputError("explicit configuration cannot include preset_id.")
    if "formulation" not in payload:
        raise InputError("model configuration is missing required key: formulation.")

    formulation = _require_mapping(payload["formulation"], "model configuration.formulation")
    _require_exact_keys(
        formulation,
        required=_FORMULATION_KEYS,
        allowed=_FORMULATION_KEYS,
        context="model configuration.formulation",
    )
    parsed = {
        "electrostatics": _parse_formulation_record("electrostatics", formulation["electrostatics"]),
        "relative_permittivity": _parse_formulation_record(
            "relative_permittivity", formulation["relative_permittivity"]
        ),
        "debye_huckel": _parse_formulation_record("debye_huckel", formulation["debye_huckel"]),
        "born": _parse_formulation_record("born", formulation["born"]),
        "solvated_ion_diameter": _parse_formulation_record(
            "solvated_ion_diameter", formulation["solvated_ion_diameter"]
        ),
        "ion_dispersion": _parse_formulation_record("ion_dispersion", formulation["ion_dispersion"]),
    }
    if isinstance(parsed["electrostatics"], DisabledFormulation):
        active = [name for name in _FORMULATION_KEYS - {"electrostatics"} if not isinstance(parsed[name], DisabledFormulation)]
        if active:
            raise InputError("dependent formulations cannot be enabled when electrostatics is disabled.")
    if isinstance(parsed["relative_permittivity"], DisabledFormulation) and any(
        not isinstance(parsed[name], DisabledFormulation) for name in ("debye_huckel", "born")
    ):
        raise InputError("Debye-Huckel and Born require enabled relative permittivity.")

    receipt = {
        "schema": MODEL_CONFIGURATION_SCHEMA,
        "schema_version": MODEL_CONFIGURATION_SCHEMA_VERSION,
        "selection_origin": "explicit_configuration",
        "formulation": {name: asdict(parsed[name]) for name in _FORMULATION_KEYS},
    }
    receipt_json = json.dumps(receipt, sort_keys=True, separators=(",", ":"), allow_nan=False)
    instance = object.__new__(ModelOptions)
    object.__setattr__(instance, "schema", MODEL_CONFIGURATION_SCHEMA)
    object.__setattr__(instance, "schema_version", MODEL_CONFIGURATION_SCHEMA_VERSION)
    object.__setattr__(instance, "selection_origin", "explicit_configuration")
    object.__setattr__(instance, "preset_id", None)
    for name in _FORMULATION_KEYS:
        object.__setattr__(instance, name, parsed[name])
    object.__setattr__(instance, "_receipt_json", receipt_json)
    return instance


def _parse_formulation_record(name: str, value: object) -> object:
    record = _require_mapping(value, f"formulation.{name}")
    required_by_name = {
        "electrostatics": {"enabled"},
        "relative_permittivity": {"enabled", "rule"},
        "debye_huckel": {"enabled", "ion_diameter_rule", "bjerrum_pairing"},
        "born": {
            "enabled",
            "born_diameter_rule",
            "solvation_shell_model",
            "dielectric_saturation",
            "bulk_mode",
        },
        "solvated_ion_diameter": {"enabled"},
        "ion_dispersion": {"enabled"},
    }
    if "enabled" not in record:
        raise InputError(f"formulation.{name} is missing required key: enabled.")
    unknown = sorted(set(record) - required_by_name[name])
    if unknown:
        raise InputError(f"formulation.{name} contains unknown key(s): {', '.join(unknown)}.")
    enabled = _require_strict_bool(record["enabled"], f"formulation.{name}.enabled")
    if not enabled:
        if set(record) != {"enabled"}:
            raise InputError(f"disabled formulation.{name} cannot contain active-only fields.")
        return DisabledFormulation(enabled=False)

    _require_exact_keys(record, required=required_by_name[name], allowed=required_by_name[name], context=f"formulation.{name}")
    if name == "electrostatics":
        return ElectrostaticsOptions(enabled=True)
    if name == "relative_permittivity":
        return RelativePermittivityOptions(enabled=True, rule=_require_string(record["rule"], f"formulation.{name}.rule"))
    if name == "debye_huckel":
        return DebyeHuckelOptions(
            enabled=True,
            ion_diameter_rule=_require_string(record["ion_diameter_rule"], f"formulation.{name}.ion_diameter_rule"),
            bjerrum_pairing=_require_strict_bool(record["bjerrum_pairing"], f"formulation.{name}.bjerrum_pairing"),
        )
    if name == "born":
        return BornModelOptions(
            enabled=True,
            born_diameter_rule=_require_string(record["born_diameter_rule"], f"formulation.{name}.born_diameter_rule"),
            solvation_shell_model=_require_strict_bool(
                record["solvation_shell_model"], f"formulation.{name}.solvation_shell_model"
            ),
            dielectric_saturation=_require_strict_bool(
                record["dielectric_saturation"], f"formulation.{name}.dielectric_saturation"
            ),
            bulk_mode=_require_string(record["bulk_mode"], f"formulation.{name}.bulk_mode"),
        )
    if name == "solvated_ion_diameter":
        return SolvatedIonDiameterOptions(enabled=True)
    return IonDispersionOptions(enabled=True)


def _read_model_configuration_payload(path: Path) -> Mapping[str, Any]:
    if path.is_dir():
        admitted_json = {MODEL_CONFIGURATION_FILENAME, "parameter_set.json"}
        unsupported = sorted(
            candidate.name
            for candidate in path.glob("*.json")
            if candidate.name not in admitted_json
        )
        if unsupported:
            raise InputError(
                f"model configuration folder contains unsupported JSON file(s): {', '.join(unsupported)}."
            )
        path = path / MODEL_CONFIGURATION_FILENAME
        if not path.is_file():
            raise InputError(f"model configuration folder must contain {MODEL_CONFIGURATION_FILENAME}.")
    elif path.name != MODEL_CONFIGURATION_FILENAME:
        raise InputError(f"model configuration file must be named {MODEL_CONFIGURATION_FILENAME}.")
    if not path.is_file():
        raise InputError(f"model configuration file '{path}' does not exist.")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_reject_duplicate_json_keys)
    except json.JSONDecodeError as exc:
        raise InputError(f"invalid model configuration JSON: {exc.msg}.") from exc
    if not isinstance(payload, Mapping):
        raise InputError(f"model configuration file '{path}' must contain a JSON object.")
    return payload


def _reject_duplicate_json_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise InputError(f"model configuration JSON contains duplicate key: {key}.")
        result[key] = value
    return result


def _require_mapping(value: object, context: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise InputError(f"{context} must be a mapping.")
    return value


def _require_exact_keys(
    value: Mapping[str, Any],
    *,
    required: set[str],
    allowed: set[str],
    context: str,
) -> None:
    missing = sorted(required - set(value))
    if missing:
        raise InputError(f"{context} is missing required key(s): {', '.join(missing)}.")
    unknown = sorted(set(value) - allowed)
    if unknown:
        raise InputError(f"{context} contains unknown key(s): {', '.join(unknown)}.")


def _require_strict_bool(value: object, field_name: str) -> bool:
    if type(value) is not bool:
        raise InputError(f"{field_name} must be a boolean.")
    return value


def _require_string(value: object, field_name: str) -> str:
    if type(value) is not str or not value:
        raise InputError(f"{field_name} must be a nonempty string.")
    return value


def require_cppad_backend(result: Mapping[str, object], *, label: str) -> None:
    backend = str(result.get("derivative_backend", result.get("jacobian_backend", result.get("backend", ""))))
    if not backend.startswith("cppad"):
        raise InputError(f"{label} requires CppAD derivative coverage; got backend {backend!r}.")


def as_float_array(value: object) -> np.ndarray:
    return np.asarray(value, dtype=float)
