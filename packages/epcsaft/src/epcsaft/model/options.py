"""Public model configuration for the reset frontend."""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import asdict, dataclass, field
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
from .parameters import ParameterSet


class MissingModelParameterError(InputError):
    """Raised when an enabled model formulation lacks required parameters."""


DifferentialMode = Literal["autodiff"]
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

_DIFFERENTIAL_MODE = "autodiff"
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
_LEGACY_PUBLIC_KEYS = {
    "born_formulation",
    "include_born_model",
    "rel_perm",
    "hc_model",
    "disp_model",
    "assoc_model",
    "DH_model",
    "d_Born_mode",
    "mu_born_model",
    "dadx_differential_mode",
}
_MODEL_OPTIONS_KEYS = {"differential_mode", "relative_permittivity_rule", "born_model"}
_BORN_MODEL_KEYS = {
    "enabled",
    "born_diameter_rule",
    "solvation_shell_model",
    "dielectric_saturation",
    "bulk_mode",
}


@dataclass(frozen=True, slots=True)
class _LegacyBornModelOptions:
    """Pre-Stage-4 Born controls retained only for the parity gate."""

    enabled: bool = True
    born_diameter_rule: BornDiameterRule = "sigma"
    solvation_shell_model: bool = True
    dielectric_saturation: bool = True
    bulk_mode: Literal["mix", "solvent"] = "mix"

    def __post_init__(self) -> None:
        diameter_rule = _normalize_token(self.born_diameter_rule, "born_model.born_diameter_rule")
        if diameter_rule not in _BORN_DIAMETER_MODES:
            raise InputError(
                "born_model.born_diameter_rule must be 'sigma', 'sigma_reduced', "
                "'temperature_dependent', or 'fitted'."
            )
        bulk_mode = _normalize_token(self.bulk_mode, "born_model.bulk_mode")
        if bulk_mode not in _BORN_BULK_MODES:
            raise InputError("born_model.bulk_mode must be 'mix' or 'solvent'.")
        object.__setattr__(self, "enabled", _coerce_bool(self.enabled, "born_model.enabled"))
        object.__setattr__(self, "born_diameter_rule", diameter_rule)
        object.__setattr__(
            self,
            "solvation_shell_model",
            _coerce_bool(self.solvation_shell_model, "born_model.solvation_shell_model"),
        )
        object.__setattr__(
            self,
            "dielectric_saturation",
            _coerce_bool(self.dielectric_saturation, "born_model.dielectric_saturation"),
        )
        object.__setattr__(self, "bulk_mode", bulk_mode)

    @classmethod
    def from_user_options(
        cls,
        value: Mapping[str, Any] | _LegacyBornModelOptions | None,
    ) -> _LegacyBornModelOptions:
        if value is None:
            return cls()
        if isinstance(value, _LegacyBornModelOptions):
            return value
        if not isinstance(value, Mapping):
            raise InputError("born_model must be a mapping or legacy Born options instance.")
        _reject_legacy_public_keys(value, context="born_model")
        _require_mapping_keys(value, _BORN_MODEL_KEYS, "born_model")
        return cls(**dict(value))

    def to_json_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class LegacyRuntimeOptionsState:
    """Exact pre-Stage-4 option state retained for the additive parity gate.

    The public API has one derivative mode: ``"autodiff"``. It maps to the
    package's CppAD runtime and applies to all residual-Helmholtz
    contributions that expose derivative routes.
    """

    differential_mode: DifferentialMode = _DIFFERENTIAL_MODE
    relative_permittivity_rule: RelativePermittivityRule = "component_linear"
    born_model: _LegacyBornModelOptions | Mapping[str, Any] = field(default_factory=_LegacyBornModelOptions)
    _stage4_origin: Literal["legacy_runtime_options"] = field(
        default="legacy_runtime_options",
        init=False,
        repr=False,
    )

    def __post_init__(self) -> None:
        differential_mode = _normalize_token(self.differential_mode, "differential_mode")
        if differential_mode != _DIFFERENTIAL_MODE:
            raise InputError('ModelOptions.differential_mode must be "autodiff".')
        rel_perm = _normalize_token(self.relative_permittivity_rule, "relative_permittivity_rule")
        if rel_perm not in _RELATIVE_PERMITTIVITY_RULES:
            raise InputError(
                "ModelOptions.relative_permittivity_rule must be one of: "
                + ", ".join(sorted(_RELATIVE_PERMITTIVITY_RULES))
            )
        born = _LegacyBornModelOptions.from_user_options(self.born_model)
        object.__setattr__(self, "differential_mode", differential_mode)
        object.__setattr__(self, "relative_permittivity_rule", rel_perm)
        object.__setattr__(self, "born_model", born)

    @classmethod
    def from_user_options(
        cls,
        value: str | Path | Mapping[str, Any] | LegacyRuntimeOptionsState | None,
    ) -> LegacyRuntimeOptionsState:
        """Load the public option schema from a mapping, JSON file, or folder.

        A folder may contain either ``model_options.json`` or ``user_options.json``.
        ``elec_model`` is accepted as a lightweight envelope for analysis bundles.
        """

        if value is None:
            return cls()
        if isinstance(value, LegacyRuntimeOptionsState):
            return value
        if isinstance(value, (str, Path)):
            return cls.from_user_options(_read_model_options_payload(Path(value).expanduser()))
        if not isinstance(value, Mapping):
            raise InputError("legacy model options must be a mapping, JSON file, folder, or tagged legacy state.")

        payload = dict(value)
        if "elec_model" in payload:
            _require_mapping_keys(
                payload,
                {"elec_model", "solvated_ion_diameter_mixing_rule", "ion_dispersion_mixing_rule"},
                "model options",
            )
            elec_model = payload["elec_model"]
            if not isinstance(elec_model, Mapping):
                raise InputError("model_options['elec_model'] must be a mapping.")
            payload = dict(elec_model)
        else:
            payload = {
                key: item
                for key, item in payload.items()
                if key not in {"solvated_ion_diameter_mixing_rule", "ion_dispersion_mixing_rule"}
            }
        _reject_legacy_public_keys(payload, context="model options")
        _require_mapping_keys(payload, _MODEL_OPTIONS_KEYS, "model options")
        return cls(**payload)

    @classmethod
    def help(cls, topic: str | None = None) -> str:
        """Return a short description of the supported public option schema."""

        topic_name = None if topic is None else _normalize_token(topic, "topic")
        if topic_name in (None, "all", "overview"):
            return (
                "ModelOptions controls public ePC-SAFT formulation choices. "
                'differential_mode is always "autodiff" and maps to CppAD. '
                "born_model.enabled toggles the Born contribution. "
                "solvation_shell_model and dielectric_saturation default to true; "
                "setting both false reduces the canonical Born path to the direct Born case. "
                "born_diameter_rule is 'sigma' by default and 'fitted' requires positive ionic born_diameter values."
            )
        if topic_name in {"born", "born_model"}:
            return (
                "born_model fields: enabled, born_diameter_rule, solvation_shell_model, "
                "dielectric_saturation, and bulk_mode. The canonical enabled case is SSM+DS."
            )
        if topic_name in {"differential", "autodiff", "derivatives"}:
            return 'The only public differential_mode is "autodiff"; it selects the CppAD derivative backend.'
        if topic_name in {"permittivity", "relative_permittivity"}:
            return (
                "relative_permittivity_rule chooses the dielectric mixing rule used by electrolyte terms; "
                "component_linear is the default."
            )
        raise InputError("Unknown ModelOptions.help topic.")

    def explain(self, parameters: ParameterSet | None = None) -> str:
        """Explain the resolved options and any parameter requirements."""

        lines = [
            f"differential_mode={self.differential_mode}: public autodiff maps to the CppAD runtime.",
            (
                f"relative_permittivity_rule={self.relative_permittivity_rule}: "
                f"runtime rule {_RELATIVE_PERMITTIVITY_RULES[self.relative_permittivity_rule]!r}."
            ),
        ]
        born = self.born_model
        if not born.enabled:
            lines.append("born_model.enabled=False: the Born residual Helmholtz contribution is disabled.")
        else:
            lines.append(
                "born_model: enabled canonical Born path with "
                f"SSM={born.solvation_shell_model}, DS={born.dielectric_saturation}, "
                f"diameter_rule={born.born_diameter_rule}."
            )
            if born.born_diameter_rule == "fitted":
                lines.append("fitted Born diameters require positive born_diameter values for charged species.")
        if parameters is not None:
            self.validate_parameters(parameters)
            lines.append("parameter check: passed.")
        return "\n".join(lines)

    def validate_parameters(self, parameters: ParameterSet) -> None:
        """Validate that enabled formulations have required parameter data."""

        if not isinstance(parameters, ParameterSet):
            raise InputError("ModelOptions validation requires a ParameterSet.")
        if not self.born_model.enabled or self.born_model.born_diameter_rule != "fitted":
            return
        charged = [record for record in parameters.pure_records if abs(float(record.charge)) > 0.0]
        missing = [record.component for record in charged if float(record.born_diameter) <= 0.0]
        if missing:
            joined = ", ".join(missing)
            raise MissingModelParameterError(
                f"born_model.born_diameter_rule='fitted' requires positive born_diameter for: {joined}."
            )

    def to_runtime_options(self, parameters: ParameterSet | None = None) -> dict[str, object]:
        """Return the existing native runtime option payload for this model."""

        if parameters is not None:
            self.validate_parameters(parameters)
        rel_rule = _RELATIVE_PERMITTIVITY_RULES[self.relative_permittivity_rule]
        born = self.born_model
        assoc_dadx_mode = "auto" if _has_active_association(parameters) else "cppad"
        return {
            "elec_model": {
                "rel_perm": {
                    "rule": rel_rule,
                    "differential_mode": "cppad",
                },
                "hc_model": {"dadx_differential_mode": "cppad"},
                "disp_model": {"dadx_differential_mode": "cppad"},
                "assoc_model": {"dadx_differential_mode": assoc_dadx_mode},
                "DH_model": {
                    "d_ion_mode": "t_dep_1",
                    "bjeruum_treatment": False,
                    "mu_DH_model": {
                        "differential_mode": "cppad",
                        "comp_dep_rel_perm": True,
                        "include_sum_term": True,
                    },
                },
                "include_born_model": bool(born.enabled),
                "born_model": {
                    "d_Born_mode": _BORN_DIAMETER_MODES[born.born_diameter_rule],
                    "solvation_shell_model": bool(born.solvation_shell_model),
                    "dielectric_saturation": bool(born.dielectric_saturation),
                    "bulk_mode": born.bulk_mode,
                    "mu_born_model": {
                        "differential_mode": "cppad",
                        "comp_dep_rel_perm": True,
                        "include_sum_term": True,
                        "comp_dep_delta_d": bool(born.solvation_shell_model),
                    },
                },
            },
            "solvated_ion_diameter_mixing_rule": False,
            "ion_dispersion_mixing_rule": True,
        }

    def to_json_dict(self) -> dict[str, object]:
        return {
            "differential_mode": self.differential_mode,
            "relative_permittivity_rule": self.relative_permittivity_rule,
            "born_model": self.born_model.to_json_dict(),
        }


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

    @classmethod
    def _from_stage4_legacy_runtime_options(
        cls,
        value: object,
    ) -> LegacyRuntimeOptionsState:
        if isinstance(value, cls):
            raise InputError("strict version-1 ModelOptions cannot enter the Stage 4 legacy runtime path.")
        if value is not None and not isinstance(value, (LegacyRuntimeOptionsState, Mapping, str, Path)):
            raise InputError("legacy model options must be a mapping, JSON file, folder, or tagged legacy state.")
        return LegacyRuntimeOptionsState.from_user_options(value)

    @classmethod
    def _to_stage4_legacy_runtime_options(
        cls,
        value: object,
        parameters: ParameterSet | None = None,
    ) -> dict[str, object]:
        if isinstance(value, cls):
            raise InputError("strict version-1 ModelOptions cannot enter the Stage 4 legacy runtime path.")
        if not isinstance(value, LegacyRuntimeOptionsState) or value._stage4_origin != "legacy_runtime_options":
            raise InputError("Stage 4 legacy runtime options require the private tagged state.")
        return value.to_runtime_options(parameters)

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
    retired_names = ("user_options.json", "model_options.json")
    if path.is_dir():
        retired = [name for name in retired_names if (path / name).exists()]
        if retired:
            raise InputError(f"model configuration folder contains retired filename(s): {', '.join(retired)}.")
        path = path / MODEL_CONFIGURATION_FILENAME
        if not path.is_file():
            raise InputError(f"model configuration folder must contain {MODEL_CONFIGURATION_FILENAME}.")
    elif path.name in retired_names:
        raise InputError(f"{path.name} is a retired model configuration filename.")
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


def _has_active_association(parameters: ParameterSet | None) -> bool:
    if parameters is None:
        return False
    for record in parameters.pure_records:
        has_site_schema = record.association_scheme not in (None, "") or bool(record.association_sites)
        has_association_parameters = float(record.epsilon_k_ab) != 0.0 and float(record.kappa_ab) != 0.0
        if has_site_schema or has_association_parameters:
            return True
    return False


def require_cppad_backend(result: Mapping[str, object], *, label: str) -> None:
    backend = str(result.get("derivative_backend", result.get("jacobian_backend", result.get("backend", ""))))
    if not backend.startswith("cppad"):
        raise InputError(f"{label} requires CppAD derivative coverage; got backend {backend!r}.")


def as_float_array(value: object) -> np.ndarray:
    return np.asarray(value, dtype=float)


def _read_model_options_payload(path: Path) -> Mapping[str, Any]:
    if path.is_dir():
        candidates = (path / "model_options.json", path / "user_options.json")
        for candidate in candidates:
            if candidate.exists():
                path = candidate
                break
        else:
            return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, Mapping):
        raise InputError(f"Model options file '{path}' must contain a JSON object.")
    return payload


def _normalize_token(value: object, field_name: str) -> str:
    text = str(value).strip().lower().replace("-", "_")
    if not text:
        raise InputError(f"{field_name} must not be empty.")
    return text


def _coerce_bool(value: object, field_name: str) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, np.integer)):
        return bool(value)
    if isinstance(value, str):
        text = value.strip().lower()
        if text in {"1", "true", "yes", "y", "on"}:
            return True
        if text in {"0", "false", "no", "n", "off"}:
            return False
    raise InputError(f"{field_name} must be boolean.")


def _require_mapping_keys(value: Mapping[str, Any], allowed: set[str], context: str) -> None:
    unknown = sorted(set(value) - allowed)
    if unknown:
        raise InputError(f"Unknown {context} key(s): {', '.join(unknown)}.")


def _reject_legacy_public_keys(value: Mapping[str, Any], *, context: str) -> None:
    found = sorted(set(value) & _LEGACY_PUBLIC_KEYS)
    if found:
        joined = ", ".join(found)
        raise InputError(f"{context} uses retired public option key(s): {joined}. Use ModelOptions.help().")
    for key, item in value.items():
        if key == "differential_mode":
            mode = _normalize_token(item, "differential_mode")
            if mode != _DIFFERENTIAL_MODE:
                raise InputError('differential_mode must be "autodiff".')
            continue
        if isinstance(item, Mapping):
            _reject_legacy_public_keys(item, context=f"{context}.{key}")
