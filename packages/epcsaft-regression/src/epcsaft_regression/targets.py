"""Strict source-backed target records for native regression compilation."""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from enum import Enum
from numbers import Real
from types import MappingProxyType
from typing import Any

from epcsaft import InputError


class SourceKind(str, Enum):
    """Evidence classification for one target row's source."""

    LITERATURE = "literature"
    USER_MEASUREMENT = "user_measurement"
    COMPONENT_TEST = "component_test"


class CompositionBasis(str, Enum):
    """Closed composition bases admitted by the first regression contract."""

    MOLE_FRACTION = "mole_fraction"


class TargetFamily(str, Enum):
    """Initially admitted strict target meanings."""

    BINARY_VLE = "binary_vle"
    PURE_SATURATION_FUGACITY_BALANCE = "pure_saturation_fugacity_balance"
    PURE_LIQUID_DENSITY_AT_PRESSURE = "pure_liquid_density_at_pressure"


@dataclass(frozen=True, slots=True)
class SourceIdentity:
    """Stable source identity without fabricated publication metadata."""

    source_id: str
    source_kind: SourceKind
    citation: str
    locator: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "source_id", _nonblank(self.source_id, "source_id"))
        if not isinstance(self.source_kind, SourceKind):
            raise InputError("source_kind must be a SourceKind.")
        citation = str(self.citation).strip()
        locator = str(self.locator).strip()
        if self.source_kind is SourceKind.LITERATURE and not citation:
            raise InputError("literature source identity requires a nonblank citation.")
        if not locator:
            raise InputError("source identity requires a nonblank locator.")
        object.__setattr__(self, "citation", citation)
        object.__setattr__(self, "locator", locator)

    def to_dict(self) -> dict[str, str]:
        return {
            "source_id": self.source_id,
            "source_kind": self.source_kind.value,
            "citation": self.citation,
            "locator": self.locator,
        }

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> SourceIdentity:
        values = _exact_mapping(
            payload,
            {"source_id", "source_kind", "citation", "locator"},
            "source identity",
        )
        return cls(
            source_id=values["source_id"],
            source_kind=_enum_value(SourceKind, values["source_kind"], "source_kind"),
            citation=values["citation"],
            locator=values["locator"],
        )


@dataclass(frozen=True, slots=True)
class CompositionRecord:
    """One exact ordered composition vector; values are never normalized."""

    phase: str
    basis: CompositionBasis
    species: tuple[str, ...]
    fractions: tuple[float, ...]

    def __post_init__(self) -> None:
        object.__setattr__(self, "phase", _nonblank(self.phase, "composition phase"))
        if not isinstance(self.basis, CompositionBasis):
            raise InputError("composition basis must be a CompositionBasis.")
        species = tuple(_nonblank(item, "composition species") for item in self.species)
        if not species:
            raise InputError("composition requires at least one species.")
        if len(set(species)) != len(species):
            raise InputError("composition species identities must be unique.")
        fractions = tuple(_finite_float(item, "composition fraction") for item in self.fractions)
        if len(species) != len(fractions):
            raise InputError("composition species and fractions must have the same length.")
        if any(value < 0.0 for value in fractions):
            raise InputError("composition fractions must be non-negative.")
        if abs(math.fsum(fractions) - 1.0) > 1.0e-7:
            raise InputError("composition fractions must sum to one without normalization.")
        object.__setattr__(self, "species", species)
        object.__setattr__(self, "fractions", fractions)

    def to_dict(self) -> dict[str, Any]:
        return {
            "phase": self.phase,
            "basis": self.basis.value,
            "species": list(self.species),
            "fractions": list(self.fractions),
        }

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> CompositionRecord:
        values = _exact_mapping(
            payload,
            {"phase", "basis", "species", "fractions"},
            "composition record",
        )
        return cls(
            phase=values["phase"],
            basis=_enum_value(CompositionBasis, values["basis"], "composition basis"),
            species=_strict_array(values["species"], "composition species"),
            fractions=_strict_array(values["fractions"], "composition fractions"),
        )


@dataclass(frozen=True, slots=True)
class TargetRow:
    """One source-qualified regression target with an exact residual meaning."""

    row_id: str
    target_family: TargetFamily
    conditions: Mapping[str, float]
    observations: Mapping[str, float]
    units: Mapping[str, str]
    weight: float
    residual_scale: float
    source: SourceIdentity
    phase: str
    compositions: tuple[CompositionRecord, ...]

    def __post_init__(self) -> None:
        object.__setattr__(self, "row_id", _nonblank(self.row_id, "row_id"))
        if not isinstance(self.target_family, TargetFamily):
            raise InputError("target_family must be a TargetFamily.")
        conditions = _finite_mapping(self.conditions, "conditions")
        observations = _finite_mapping(self.observations, "observations")
        units = _units_mapping(self.units)
        weight = _positive_float(self.weight, "weight")
        residual_scale = _positive_float(self.residual_scale, "residual_scale")
        if not isinstance(self.source, SourceIdentity):
            raise InputError("target row source must be a SourceIdentity.")
        phase = _nonblank(self.phase, "target row phase")
        compositions = tuple(self.compositions)
        if any(not isinstance(item, CompositionRecord) for item in compositions):
            raise InputError("target row compositions must contain CompositionRecord values.")
        _validate_family(
            self.target_family,
            conditions,
            observations,
            units,
            residual_scale,
            phase,
            compositions,
        )
        object.__setattr__(self, "conditions", MappingProxyType(conditions))
        object.__setattr__(self, "observations", MappingProxyType(observations))
        object.__setattr__(self, "units", MappingProxyType(units))
        object.__setattr__(self, "weight", weight)
        object.__setattr__(self, "residual_scale", residual_scale)
        object.__setattr__(self, "phase", phase)
        object.__setattr__(self, "compositions", compositions)

    def to_dict(self) -> dict[str, Any]:
        return {
            "row_id": self.row_id,
            "target_family": self.target_family.value,
            "conditions": dict(self.conditions),
            "observations": dict(self.observations),
            "units": dict(self.units),
            "weight": self.weight,
            "residual_scale": self.residual_scale,
            "source": self.source.to_dict(),
            "phase": self.phase,
            "compositions": [item.to_dict() for item in self.compositions],
        }

    @classmethod
    def from_dict(
        cls,
        payload: Mapping[str, Any],
        *,
        default_family: TargetFamily | str | None = None,
    ) -> TargetRow:
        if not isinstance(payload, Mapping):
            raise InputError("target row must be a mapping.")
        values = dict(payload)
        if "target_family" not in values and default_family is not None:
            values["target_family"] = (
                default_family.value
                if isinstance(default_family, TargetFamily)
                else default_family
            )
        values = _exact_mapping(
            values,
            {
                "row_id",
                "target_family",
                "conditions",
                "observations",
                "units",
                "weight",
                "residual_scale",
                "source",
                "phase",
                "compositions",
            },
            "target row",
        )
        source = values["source"]
        compositions = _strict_array(values["compositions"], "target row compositions")
        return cls(
            row_id=values["row_id"],
            target_family=_enum_value(TargetFamily, values["target_family"], "target_family"),
            conditions=values["conditions"],
            observations=values["observations"],
            units=values["units"],
            weight=values["weight"],
            residual_scale=values["residual_scale"],
            source=(
                source
                if isinstance(source, SourceIdentity)
                else SourceIdentity.from_dict(source)
            ),
            phase=values["phase"],
            compositions=tuple(
                item
                if isinstance(item, CompositionRecord)
                else CompositionRecord.from_dict(item)
                for item in compositions
            ),
        )


@dataclass(frozen=True, slots=True)
class TargetDataset:
    """Ordered strict target rows with stable dataset and row identities."""

    rows: tuple[TargetRow, ...]
    dataset_id: str

    def __post_init__(self) -> None:
        dataset_id = _nonblank(self.dataset_id, "dataset_id")
        rows = tuple(self.rows)
        if not rows:
            raise InputError("TargetDataset requires at least one TargetRow.")
        if any(not isinstance(row, TargetRow) for row in rows):
            raise InputError("TargetDataset rows must contain only TargetRow values.")
        row_ids = tuple(row.row_id for row in rows)
        duplicates = sorted({row_id for row_id in row_ids if row_ids.count(row_id) > 1})
        if duplicates:
            raise InputError(f"TargetDataset contains duplicate row_id values: {', '.join(duplicates)}.")
        object.__setattr__(self, "dataset_id", dataset_id)
        object.__setattr__(self, "rows", rows)

    @property
    def row_ids(self) -> tuple[str, ...]:
        return tuple(row.row_id for row in self.rows)

    @classmethod
    def from_records(
        cls,
        records: Sequence[Mapping[str, Any]],
        *,
        dataset_id: str,
        default_family: TargetFamily | str | None = None,
    ) -> TargetDataset:
        if isinstance(records, (str, bytes)):
            raise InputError("TargetDataset.from_records requires a sequence of mappings.")
        try:
            items = tuple(records)
        except TypeError as exc:
            raise InputError("TargetDataset.from_records requires a sequence of mappings.") from exc
        if any(not isinstance(item, Mapping) for item in items):
            raise InputError("TargetDataset.from_records accepts only mapping records.")
        return cls(
            rows=tuple(
                TargetRow.from_dict(item, default_family=default_family)
                for item in items
            ),
            dataset_id=dataset_id,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "dataset_id": self.dataset_id,
            "rows": [row.to_dict() for row in self.rows],
        }


def _validate_family(
    family: TargetFamily,
    conditions: dict[str, float],
    observations: dict[str, float],
    units: dict[str, str],
    residual_scale: float,
    phase: str,
    compositions: tuple[CompositionRecord, ...],
) -> None:
    _require_exact_keys(conditions, {"temperature", "pressure"}, "target conditions")
    if conditions["temperature"] <= 0.0 or conditions["pressure"] <= 0.0:
        raise InputError("target temperature and pressure must be positive.")
    if family is TargetFamily.BINARY_VLE:
        _require_exact_keys(observations, set(), "binary VLE observations")
        _require_exact_units(units, {"temperature": "K", "pressure": "Pa"})
        if phase != "vle":
            raise InputError("binary VLE target phase must be 'vle'.")
        if residual_scale != 1.0:
            raise InputError("binary VLE residual_scale must be 1.0.")
        _validate_binary_compositions(compositions)
        return
    _require_exact_keys(observations, {"target"}, "pure target observations")
    if compositions:
        raise InputError("pure observed-pressure targets cannot carry compositions.")
    if phase != "liquid_vapor":
        raise InputError("pure observed-pressure target phase must be 'liquid_vapor'.")
    if family is TargetFamily.PURE_SATURATION_FUGACITY_BALANCE:
        if observations["target"] != 0.0 or residual_scale != 1.0:
            raise InputError(
                "pure saturation fugacity balance requires a zero dimensionless target and scale 1.0."
            )
        _require_exact_units(
            units,
            {"temperature": "K", "pressure": "Pa", "target": "dimensionless"},
        )
        return
    if family is TargetFamily.PURE_LIQUID_DENSITY_AT_PRESSURE:
        _require_exact_units(
            units,
            {"temperature": "K", "pressure": "Pa", "target": "kg/m3"},
        )
        target = observations["target"]
        if target <= 0.0:
            raise InputError("pure liquid density target must be positive.")
        if residual_scale != target:
            raise InputError(
                "pure liquid density residual_scale must equal the retained density observation."
            )
        return
    raise InputError(f"unsupported target family: {family.value}.")


def _validate_binary_compositions(compositions: tuple[CompositionRecord, ...]) -> None:
    if len(compositions) != 2:
        raise InputError("binary VLE requires exactly liquid and vapor compositions.")
    phases = tuple(item.phase for item in compositions)
    if phases != ("liquid", "vapor"):
        raise InputError("binary VLE compositions must be ordered liquid then vapor.")
    liquid, vapor = compositions
    if liquid.basis is not CompositionBasis.MOLE_FRACTION or vapor.basis is not CompositionBasis.MOLE_FRACTION:
        raise InputError("binary VLE requires mole-fraction composition basis.")
    if liquid.species != vapor.species or len(liquid.species) != 2:
        raise InputError("binary VLE liquid and vapor compositions require the same two-species order.")
    if any(value <= 0.0 for value in (*liquid.fractions, *vapor.fractions)):
        raise InputError("binary VLE observed fractions must be positive for logarithmic residuals.")


def _ordered_model_target_pairs(
    row: TargetRow,
    model_values: Mapping[str, Any],
) -> tuple[tuple[str, float, float], ...]:
    """Return a small independent oracle for each admitted target meaning."""

    if not isinstance(row, TargetRow):
        raise InputError("model target oracle requires a TargetRow.")
    if not isinstance(model_values, Mapping):
        raise InputError("model target oracle values must be a mapping.")
    if row.target_family is TargetFamily.BINARY_VLE:
        values = _exact_mapping(
            model_values,
            {"liquid_fugacity_coefficients", "vapor_fugacity_coefficients"},
            "binary VLE model values",
        )
        liquid_phi = _positive_vector(
            values["liquid_fugacity_coefficients"],
            "liquid fugacity coefficients",
        )
        vapor_phi = _positive_vector(
            values["vapor_fugacity_coefficients"],
            "vapor fugacity coefficients",
        )
        liquid, vapor = row.compositions
        if len(liquid_phi) != len(liquid.species) or len(vapor_phi) != len(liquid.species):
            raise InputError("fugacity-coefficient vectors must match the target species order.")
        return tuple(
            (
                species,
                math.log(
                    liquid.fractions[index]
                    * liquid_phi[index]
                    / (vapor.fractions[index] * vapor_phi[index])
                ),
                0.0,
            )
            for index, species in enumerate(liquid.species)
        )
    if row.target_family is TargetFamily.PURE_SATURATION_FUGACITY_BALANCE:
        values = _exact_mapping(
            model_values,
            {"liquid_log_fugacity", "vapor_log_fugacity"},
            "pure fugacity model values",
        )
        liquid = _finite_float(values["liquid_log_fugacity"], "liquid log fugacity")
        vapor = _finite_float(values["vapor_log_fugacity"], "vapor log fugacity")
        return (("fugacity_balance", liquid - vapor, 0.0),)
    if row.target_family is TargetFamily.PURE_LIQUID_DENSITY_AT_PRESSURE:
        values = _exact_mapping(
            model_values,
            {"liquid_density_kg_per_m3"},
            "pure liquid-density model values",
        )
        model = _positive_float(
            values["liquid_density_kg_per_m3"],
            "liquid density",
        )
        return (("liquid_density", model, row.observations["target"]),)
    raise InputError(f"unsupported target family: {row.target_family.value}.")


def _finite_mapping(value: Mapping[str, Any], context: str) -> dict[str, float]:
    if not isinstance(value, Mapping):
        raise InputError(f"target {context} must be a mapping.")
    if any(type(key) is not str for key in value):
        raise InputError(f"target {context} keys must be strings.")
    return {key: _finite_float(item, f"target {context}.{key}") for key, item in value.items()}


def _units_mapping(value: Mapping[str, Any]) -> dict[str, str]:
    if not isinstance(value, Mapping):
        raise InputError("target units must be a mapping.")
    if any(type(key) is not str for key in value):
        raise InputError("target unit keys must be strings.")
    return {key: _nonblank(item, f"target units.{key}") for key, item in value.items()}


def _require_exact_units(actual: dict[str, str], expected: dict[str, str]) -> None:
    if actual != expected:
        raise InputError(f"target canonical units must be exactly {expected}.")


def _positive_vector(value: Any, context: str) -> tuple[float, ...]:
    values = _strict_array(value, context)
    result = tuple(_positive_float(item, context) for item in values)
    if not result:
        raise InputError(f"{context} must not be empty.")
    return result


def _finite_float(value: Any, context: str) -> float:
    if isinstance(value, bool) or not isinstance(value, Real):
        raise InputError(f"{context} must be a finite number.")
    result = float(value)
    if not math.isfinite(result):
        raise InputError(f"{context} must be finite.")
    return result


def _positive_float(value: Any, context: str) -> float:
    result = _finite_float(value, context)
    if result <= 0.0:
        raise InputError(f"{context} must be positive and finite.")
    return result


def _nonblank(value: Any, context: str) -> str:
    if type(value) is not str or not value.strip():
        raise InputError(f"{context} must be nonblank.")
    return value.strip()


def _strict_array(value: Any, context: str) -> tuple[Any, ...]:
    if not isinstance(value, (list, tuple)):
        raise InputError(f"{context} must be an array.")
    return tuple(value)


def _enum_value(enum_type, value: Any, context: str):
    try:
        return enum_type(value)
    except (TypeError, ValueError) as exc:
        raise InputError(f"{context} is not supported by {enum_type.__name__}.") from exc


def _exact_mapping(
    value: Mapping[str, Any],
    expected: set[str],
    context: str,
) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise InputError(f"{context} must be a mapping.")
    if any(type(key) is not str for key in value):
        raise InputError(f"{context} keys must be strings.")
    unknown = sorted(set(value) - expected)
    if unknown:
        raise InputError(f"{context} contains unknown key(s): {', '.join(unknown)}.")
    missing = sorted(expected - set(value))
    if missing:
        raise InputError(f"{context} is missing required key(s): {', '.join(missing)}.")
    return dict(value)


def _require_exact_keys(value: Mapping[str, Any], expected: set[str], context: str) -> None:
    _exact_mapping(value, expected, context)
