"""Public model configuration for the reset frontend."""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Literal

import numpy as np

from .._types import InputError
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
class BornModelOptions:
    """Grouped public controls for the Born contribution."""

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
    def from_user_options(cls, value: Mapping[str, Any] | BornModelOptions | None) -> BornModelOptions:
        if value is None:
            return cls()
        if isinstance(value, BornModelOptions):
            return value
        if not isinstance(value, Mapping):
            raise InputError("born_model must be a mapping or BornModelOptions instance.")
        _reject_legacy_public_keys(value, context="born_model")
        _require_mapping_keys(value, _BORN_MODEL_KEYS, "born_model")
        return cls(**dict(value))

    def to_json_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class ModelOptions:
    """Formulation choices owned by :class:`epcsaft.Mixture`.

    The public API has one derivative mode: ``"autodiff"``. It maps to the
    package's CppAD runtime and applies to all residual-Helmholtz
    contributions that expose derivative routes.
    """

    differential_mode: DifferentialMode = _DIFFERENTIAL_MODE
    relative_permittivity_rule: RelativePermittivityRule = "component_linear"
    born_model: BornModelOptions | Mapping[str, Any] = field(default_factory=BornModelOptions)

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
        born = BornModelOptions.from_user_options(self.born_model)
        object.__setattr__(self, "differential_mode", differential_mode)
        object.__setattr__(self, "relative_permittivity_rule", rel_perm)
        object.__setattr__(self, "born_model", born)

    @classmethod
    def from_user_options(cls, value: str | Path | Mapping[str, Any] | ModelOptions | None) -> ModelOptions:
        """Load the public option schema from a mapping, JSON file, or folder.

        A folder may contain either ``model_options.json`` or ``user_options.json``.
        ``elec_model`` is accepted as a lightweight envelope for analysis bundles.
        """

        if value is None:
            return cls()
        if isinstance(value, ModelOptions):
            return value
        if isinstance(value, (str, Path)):
            return cls.from_user_options(_read_model_options_payload(Path(value).expanduser()))
        if not isinstance(value, Mapping):
            raise InputError("model_options must be a ModelOptions instance, mapping, JSON file, or folder.")

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


def coerce_model_options(value: ModelOptions | Mapping[str, object] | str | Path | None) -> ModelOptions:
    if value is None:
        return ModelOptions()
    if isinstance(value, ModelOptions):
        return value
    if isinstance(value, (Mapping, str, Path)):
        return ModelOptions.from_user_options(value)
    raise InputError("model_options must be a ModelOptions instance, mapping, JSON file, or folder.")


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
