"""Typed fitted-parameter selections for regression compilation."""

from __future__ import annotations

import math
from collections.abc import Mapping
from dataclasses import dataclass
from numbers import Real
from typing import Any

from epcsaft import InputError

PURE_PARAMETER_FIELDS = {
    "m": "segment_count",
    "sigma": "sigma_angstrom",
    "epsilon_k": "epsilon_k_K",
    "epsilon_k_ab": "association_energy_K",
    "kappa_ab": "association_volume",
    "born_diameter": "born_diameter_angstrom",
    "solvation_factor": "solvation_factor",
    "relative_permittivity": "relative_permittivity",
}
INTERACTION_PARAMETER_FIELDS = {"k_ij", "l_ij", "k_hb_ij"}


@dataclass(frozen=True, slots=True)
class FittedParameter:
    """One stable parameter key with an explicit start and finite bounds."""

    key: str
    start: float
    lower: float
    upper: float

    def __post_init__(self) -> None:
        key = _parameter_key(self.key)
        start = _finite_float(self.start, "fitted parameter start")
        lower = _finite_float(self.lower, "fitted parameter lower bound")
        upper = _finite_float(self.upper, "fitted parameter upper bound")
        if lower >= upper:
            raise InputError("fitted parameter lower bound must be less than its upper bound.")
        if not lower <= start <= upper:
            raise InputError("fitted parameter start must lie within its lower and upper bounds.")
        object.__setattr__(self, "key", key)
        object.__setattr__(self, "start", start)
        object.__setattr__(self, "lower", lower)
        object.__setattr__(self, "upper", upper)

    @classmethod
    def from_mapping(cls, payload: Mapping[str, Any]) -> FittedParameter:
        """Parse one complete fitted-parameter record without defaults."""

        expected = {"key", "start", "lower", "upper"}
        if not isinstance(payload, Mapping):
            raise InputError("fitted parameter must be a mapping.")
        if any(type(key) is not str for key in payload):
            raise InputError("fitted parameter mapping keys must be strings.")
        unknown = sorted(set(payload) - expected)
        if unknown:
            raise InputError(f"unknown fitted parameter key(s): {', '.join(unknown)}.")
        missing = sorted(expected - set(payload))
        if missing:
            raise InputError(f"fitted parameter is missing required field(s): {', '.join(missing)}.")
        return cls(**dict(payload))

    def to_dict(self) -> dict[str, object]:
        return {
            "key": self.key,
            "start": self.start,
            "lower": self.lower,
            "upper": self.upper,
        }


@dataclass(frozen=True, slots=True)
class ParsedParameterKey:
    key: str
    owners: tuple[str, ...]
    parameter: str
    provider_field: str

    @property
    def is_interaction(self) -> bool:
        return len(self.owners) == 2


def parse_parameter_key(key: str) -> ParsedParameterKey:
    """Resolve a stable public key into one closed provider field."""

    normalized = _parameter_key(key)
    owner_text, parameter = normalized.rsplit(".", maxsplit=1)
    if parameter in PURE_PARAMETER_FIELDS:
        if ":" in owner_text:
            raise InputError(f"fitted parameter key {normalized!r} has an invalid component owner.")
        owners = (_identity(owner_text, "component"),)
        provider_field = PURE_PARAMETER_FIELDS[parameter]
    elif parameter in INTERACTION_PARAMETER_FIELDS:
        pair = owner_text.split(":")
        if len(pair) != 2 or pair[0] == pair[1]:
            raise InputError(f"fitted interaction key {normalized!r} requires two distinct components.")
        owners = tuple(_identity(item, "interaction component") for item in pair)
        provider_field = parameter
    else:
        raise InputError(f"fitted parameter key {normalized!r} names an unsupported provider field.")
    return ParsedParameterKey(normalized, owners, parameter, provider_field)


def _parameter_key(value: Any) -> str:
    if type(value) is not str or not value.strip():
        raise InputError("fitted parameter key must be nonblank.")
    result = value.strip()
    if result.count(".") != 1:
        raise InputError("fitted parameter key must use '<owner>.<parameter>'.")
    if any(character.isspace() for character in result):
        raise InputError("fitted parameter key cannot contain whitespace.")
    return result


def _identity(value: str, context: str) -> str:
    result = value.strip()
    if not result:
        raise InputError(f"fitted parameter {context} must be nonblank.")
    return result


def _finite_float(value: Any, context: str) -> float:
    if isinstance(value, bool) or not isinstance(value, Real):
        raise InputError(f"{context} must be finite.")
    result = float(value)
    if not math.isfinite(result):
        raise InputError(f"{context} must be finite.")
    return result
