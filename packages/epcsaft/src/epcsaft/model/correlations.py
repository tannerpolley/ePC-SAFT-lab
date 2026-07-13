"""Typed, source-bearing scientific definitions for parameter schema 3."""

from __future__ import annotations

import math
from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum
from numbers import Real
from typing import Any

from .._types import InputError


class IndependentVariable(StrEnum):
    """Closed independent-variable vocabulary for scientific definitions."""

    TEMPERATURE_K = "temperature_K"
    MOLE_FRACTION = "mole_fraction"
    MOLAR_DENSITY = "molar_density"
    PRESSURE_PA = "pressure_Pa"


@dataclass(frozen=True, slots=True)
class DependencySignature:
    """Explicit state variables on which a definition depends."""

    variables: tuple[IndependentVariable, ...]
    composition_components: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        variables = tuple(self.variables)
        if any(not isinstance(variable, IndependentVariable) for variable in variables):
            raise InputError("dependency variables must use the closed IndependentVariable vocabulary.")
        if len(set(variables)) != len(variables):
            raise InputError("dependency variables must be unique.")
        components = tuple(_nonblank(item, "composition component identity") for item in self.composition_components)
        if len(set(components)) != len(components):
            raise InputError("composition component identities must be unique.")
        if IndependentVariable.MOLE_FRACTION in variables and not components:
            raise InputError("composition dependency requires explicit component identities.")
        if IndependentVariable.MOLE_FRACTION not in variables and components:
            raise InputError("composition component identities require a mole-fraction dependency.")
        object.__setattr__(self, "variables", variables)
        object.__setattr__(self, "composition_components", components)


@dataclass(frozen=True, slots=True)
class DomainEvidence:
    """Evidence supporting an admitted scientific-definition domain."""

    kind: str
    source: str

    def __post_init__(self) -> None:
        kind = _nonblank(self.kind, "domain evidence kind")
        if kind not in {"source_validity", "source_application"}:
            raise InputError("domain evidence kind must be 'source_validity' or 'source_application'.")
        object.__setattr__(self, "kind", kind)
        object.__setattr__(self, "source", _nonblank(self.source, "domain evidence source"))


@dataclass(frozen=True, slots=True)
class TemperatureDomain:
    """Inclusive temperature interval supported by explicit evidence."""

    minimum_K: float
    maximum_K: float
    evidence: DomainEvidence

    def __post_init__(self) -> None:
        minimum = _finite_number(self.minimum_K, "temperature-domain minimum")
        maximum = _finite_number(self.maximum_K, "temperature-domain maximum")
        if minimum > maximum:
            raise InputError("temperature-domain minimum must not exceed its maximum.")
        if not isinstance(self.evidence, DomainEvidence):
            raise InputError("temperature domain requires DomainEvidence.")
        object.__setattr__(self, "minimum_K", minimum)
        object.__setattr__(self, "maximum_K", maximum)

    def validate(self, temperature_K: Real) -> float:
        value = _finite_number(temperature_K, "temperature")
        if not self.minimum_K <= value <= self.maximum_K:
            raise InputError("temperature is outside the sourced record domain.")
        return value


@dataclass(frozen=True, slots=True)
class ScientificSource:
    """Stable locator and provenance class for one scientific definition."""

    kind: str
    locator: str

    def __post_init__(self) -> None:
        kind = _nonblank(self.kind, "scientific source kind")
        if kind not in {"literature", "fitted", "model_structural_zero"}:
            raise InputError("scientific source kind must be literature, fitted, or model_structural_zero.")
        object.__setattr__(self, "kind", kind)
        object.__setattr__(self, "locator", _nonblank(self.locator, "scientific source locator"))


@dataclass(frozen=True, slots=True)
class ConstantCorrelation:
    value: float

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _finite_number(self.value, "constant correlation value"))

    def evaluate(self, **_: Any) -> float:
        return self.value

    def temperature_derivatives(self, temperature_K: Real) -> tuple[float, float, float]:
        _finite_number(temperature_K, "temperature")
        return self.value, 0.0, 0.0


@dataclass(frozen=True, slots=True)
class ReferenceTemperatureLinearCorrelation:
    reference_temperature_K: float
    reference_value: float
    slope_per_K: float

    def __post_init__(self) -> None:
        reference_temperature = _finite_number(self.reference_temperature_K, "reference_temperature_K")
        if reference_temperature <= 0.0:
            raise InputError("reference_temperature_K must be positive.")
        object.__setattr__(self, "reference_temperature_K", reference_temperature)
        object.__setattr__(self, "reference_value", _finite_number(self.reference_value, "reference_value"))
        object.__setattr__(self, "slope_per_K", _finite_number(self.slope_per_K, "slope_per_K"))

    def evaluate(self, *, temperature_K: Real) -> float:
        return self.temperature_derivatives(temperature_K)[0]

    def temperature_derivatives(self, temperature_K: Real) -> tuple[float, float, float]:
        temperature = _finite_number(temperature_K, "temperature")
        return (
            self.reference_value + self.slope_per_K * (temperature - self.reference_temperature_K),
            self.slope_per_K,
            0.0,
        )


@dataclass(frozen=True, slots=True)
class LogTemperatureCorrelation:
    coefficient: float
    intercept: float
    reference_temperature_K: float
    logarithm_base: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "coefficient", _finite_number(self.coefficient, "coefficient"))
        object.__setattr__(self, "intercept", _finite_number(self.intercept, "intercept"))
        reference_temperature = _finite_number(self.reference_temperature_K, "reference_temperature_K")
        if reference_temperature <= 0.0:
            raise InputError("reference_temperature_K must be positive.")
        object.__setattr__(self, "reference_temperature_K", reference_temperature)
        if self.logarithm_base != "natural":
            raise InputError("logarithm_base must be 'natural'.")

    def evaluate(self, *, temperature_K: Real) -> float:
        return self.temperature_derivatives(temperature_K)[0]

    def temperature_derivatives(self, temperature_K: Real) -> tuple[float, float, float]:
        temperature = _finite_number(temperature_K, "temperature")
        if temperature <= 0.0:
            raise InputError("temperature must be positive for a logarithmic correlation.")
        return (
            self.intercept + self.coefficient * math.log(temperature / self.reference_temperature_K),
            self.coefficient / temperature,
            -self.coefficient / temperature**2,
        )


@dataclass(frozen=True, slots=True)
class ExponentialTerm:
    coefficient: float
    temperature_coefficient_per_K: float

    def __post_init__(self) -> None:
        object.__setattr__(self, "coefficient", _finite_number(self.coefficient, "exponential coefficient"))
        object.__setattr__(
            self,
            "temperature_coefficient_per_K",
            _finite_number(self.temperature_coefficient_per_K, "exponential temperature coefficient"),
        )


@dataclass(frozen=True, slots=True)
class ConstantPlusExponentialTermsCorrelation:
    constant: float
    terms: tuple[ExponentialTerm, ...]

    def __post_init__(self) -> None:
        object.__setattr__(self, "constant", _finite_number(self.constant, "exponential correlation constant"))
        terms = tuple(self.terms)
        if not terms or any(not isinstance(term, ExponentialTerm) for term in terms):
            raise InputError("constant-plus-exponential correlation requires typed ExponentialTerm records.")
        object.__setattr__(self, "terms", terms)

    def evaluate(self, *, temperature_K: Real) -> float:
        return self.temperature_derivatives(temperature_K)[0]

    def temperature_derivatives(self, temperature_K: Real) -> tuple[float, float, float]:
        temperature = _finite_number(temperature_K, "temperature")
        value = self.constant
        first = 0.0
        second = 0.0
        for term in self.terms:
            exponential = math.exp(term.temperature_coefficient_per_K * temperature)
            contribution = term.coefficient * exponential
            value += contribution
            first += contribution * term.temperature_coefficient_per_K
            second += contribution * term.temperature_coefficient_per_K**2
        if not all(math.isfinite(item) for item in (value, first, second)):
            raise InputError("exponential correlation produced a nonfinite result.")
        return value, first, second


@dataclass(frozen=True, slots=True)
class QuadraticCoefficients:
    quadratic: float
    linear: float
    constant: float

    def __post_init__(self) -> None:
        for name in ("quadratic", "linear", "constant"):
            object.__setattr__(self, name, _finite_number(getattr(self, name), f"quadratic {name}"))

    def derivatives(self, value: Real) -> tuple[float, float, float]:
        argument = _finite_number(value, "quadratic argument")
        return (
            self.quadratic * argument**2 + self.linear * argument + self.constant,
            2.0 * self.quadratic * argument + self.linear,
            2.0 * self.quadratic,
        )


@dataclass(frozen=True, slots=True)
class PiecewiseQuadraticTemperatureCorrelation:
    transition_temperature_K: float
    lower: QuadraticCoefficients
    upper: QuadraticCoefficients

    def __post_init__(self) -> None:
        transition = _finite_number(self.transition_temperature_K, "transition_temperature_K")
        if transition <= 0.0:
            raise InputError("transition_temperature_K must be positive.")
        if not isinstance(self.lower, QuadraticCoefficients) or not isinstance(self.upper, QuadraticCoefficients):
            raise InputError("piecewise quadratic branches must be QuadraticCoefficients records.")
        object.__setattr__(self, "transition_temperature_K", transition)

    def evaluate(self, *, temperature_K: Real) -> float:
        return self.temperature_derivatives(temperature_K)[0]

    def temperature_derivatives(self, temperature_K: Real) -> tuple[float, float, float]:
        temperature = _finite_number(temperature_K, "temperature")
        branch = self.lower if temperature <= self.transition_temperature_K else self.upper
        return branch.derivatives(temperature)


@dataclass(frozen=True, slots=True)
class SaltFreeWaterMoleFractionCubicPermittivityCorrelation:
    water_component: str
    organic_component: str
    composition_basis: str
    coefficient_a: float
    coefficient_b: float
    coefficient_c: float

    def __post_init__(self) -> None:
        water = _nonblank(self.water_component, "water_component")
        organic = _nonblank(self.organic_component, "organic_component")
        if water == organic:
            raise InputError("water_component and organic_component must be distinct.")
        if self.composition_basis != "salt_free_solvent_mole_fraction":
            raise InputError("composition_basis must be 'salt_free_solvent_mole_fraction'.")
        object.__setattr__(self, "water_component", water)
        object.__setattr__(self, "organic_component", organic)
        for name in ("coefficient_a", "coefficient_b", "coefficient_c"):
            object.__setattr__(self, name, _finite_number(getattr(self, name), name))

    def evaluate(
        self,
        *,
        water_fraction: Real,
        organic_relative_permittivity: Real,
    ) -> float:
        return self.composition_derivatives(water_fraction, organic_relative_permittivity)[0]

    def composition_derivatives(
        self,
        water_fraction: Real,
        organic_relative_permittivity: Real,
    ) -> tuple[float, float, float]:
        fraction = _finite_number(water_fraction, "salt-free water mole fraction")
        if not 0.0 <= fraction <= 1.0:
            raise InputError("salt-free water mole fraction must lie in [0, 1].")
        organic = _finite_number(organic_relative_permittivity, "organic relative permittivity")
        value = organic + self.coefficient_a * fraction**3 + self.coefficient_b * fraction**2 + self.coefficient_c * fraction
        first = 3.0 * self.coefficient_a * fraction**2 + 2.0 * self.coefficient_b * fraction + self.coefficient_c
        second = 6.0 * self.coefficient_a * fraction + 2.0 * self.coefficient_b
        return value, first, second


CorrelationDefinition = (
    ConstantCorrelation
    | ReferenceTemperatureLinearCorrelation
    | LogTemperatureCorrelation
    | ConstantPlusExponentialTermsCorrelation
    | PiecewiseQuadraticTemperatureCorrelation
    | SaltFreeWaterMoleFractionCubicPermittivityCorrelation
)


_ALLOWED_UNITS = {"dimensionless", "kg/mol", "angstrom", "K"}
_EXPECTED_FIELD_UNITS = {
    "molar_mass_kg_per_mol": "kg/mol",
    "segment_count": "dimensionless",
    "sigma_angstrom": "angstrom",
    "epsilon_k_K": "K",
    "charge_number": "dimensionless",
    "association_energy_K": "K",
    "association_volume": "dimensionless",
    "association_scheme": "dimensionless",
    "association_sites": "dimensionless",
    "relative_permittivity": "dimensionless",
    "born_diameter_angstrom": "angstrom",
    "solvation_factor": "dimensionless",
}
_SCIENTIFIC_FIELDS = {
    "molar_mass_kg_per_mol",
    "segment_count",
    "sigma_angstrom",
    "epsilon_k_K",
    "charge_number",
    "association_energy_K",
    "association_volume",
    "association_scheme",
    "association_sites",
    "relative_permittivity",
    "born_diameter_angstrom",
    "solvation_factor",
}


@dataclass(frozen=True, slots=True)
class ScientificRecord:
    """One pure-component or formulation scientific definition."""

    record_id: str
    component: str
    field: str
    units: str
    source: ScientificSource
    dependency_signature: DependencySignature
    temperature_domain: TemperatureDomain
    definition: CorrelationDefinition

    def __post_init__(self) -> None:
        object.__setattr__(self, "record_id", _nonblank(self.record_id, "record_id"))
        object.__setattr__(self, "component", _nonblank(self.component, "component"))
        field = _nonblank(self.field, "scientific field")
        if field not in _SCIENTIFIC_FIELDS:
            raise InputError(f"{field!r} is not an admitted scientific field.")
        object.__setattr__(self, "field", field)
        units = _nonblank(self.units, "units")
        if units not in _ALLOWED_UNITS:
            raise InputError(f"scientific record units must be one of {sorted(_ALLOWED_UNITS)}.")
        expected_units = _EXPECTED_FIELD_UNITS[field]
        if units != expected_units:
            raise InputError(f"scientific record {field} units must be {expected_units!r}.")
        object.__setattr__(self, "units", units)
        if not isinstance(self.source, ScientificSource):
            raise InputError("scientific record source must be a ScientificSource.")
        if self.source.kind == "model_structural_zero":
            raise InputError("scientific records cannot use model_structural_zero sources.")
        if not isinstance(self.dependency_signature, DependencySignature):
            raise InputError("scientific record requires a DependencySignature.")
        if not isinstance(self.temperature_domain, TemperatureDomain):
            raise InputError("scientific record requires a TemperatureDomain.")
        if not isinstance(self.definition, _CORRELATION_TYPES):
            raise InputError("scientific record definition must be a typed correlation.")
        if self.dependency_signature != _definition_dependency_signature(self.definition):
            raise InputError("scientific record dependency signature must match its typed correlation.")

    def evaluate(self, **state: Any) -> float:
        if IndependentVariable.TEMPERATURE_K in self.dependency_signature.variables:
            if "temperature_K" not in state:
                raise InputError("temperature-dependent scientific record requires temperature_K.")
            self.temperature_domain.validate(state["temperature_K"])
        if isinstance(self.definition, ConstantCorrelation):
            return self.definition.evaluate()
        return self.definition.evaluate(**state)


@dataclass(frozen=True, slots=True)
class ScientificInteractionRecord:
    """One source-bearing binary scientific definition."""

    record_id: str
    family: str
    components: tuple[str, str]
    units: str
    source: ScientificSource
    dependency_signature: DependencySignature
    temperature_domain: TemperatureDomain
    definition: CorrelationDefinition

    def __post_init__(self) -> None:
        object.__setattr__(self, "record_id", _nonblank(self.record_id, "record_id"))
        family = _nonblank(self.family, "interaction family")
        if family not in {"k_ij", "l_ij", "k_hb_ij"}:
            raise InputError("interaction family is not admitted.")
        object.__setattr__(self, "family", family)
        components = _component_pair(self.components, "scientific interaction")
        object.__setattr__(self, "components", components)
        if self.units != "dimensionless":
            raise InputError("scientific interaction units must be 'dimensionless'.")
        if not isinstance(self.source, ScientificSource) or self.source.kind == "model_structural_zero":
            raise InputError("scientific interaction requires a non-structural-zero source.")
        if not isinstance(self.dependency_signature, DependencySignature):
            raise InputError("scientific interaction requires a DependencySignature.")
        if not isinstance(self.temperature_domain, TemperatureDomain):
            raise InputError("scientific interaction requires a TemperatureDomain.")
        if not isinstance(self.definition, _CORRELATION_TYPES):
            raise InputError("scientific interaction definition must be a typed correlation.")
        if self.dependency_signature != _definition_dependency_signature(self.definition):
            raise InputError("scientific interaction dependency signature must match its typed correlation.")


@dataclass(frozen=True, slots=True)
class ScientificStructuralZero:
    """Explicit source-backed structural zero for one interaction pair."""

    record_id: str
    family: str
    components: tuple[str, str]
    reason: str
    source: ScientificSource

    def __post_init__(self) -> None:
        object.__setattr__(self, "record_id", _nonblank(self.record_id, "record_id"))
        family = _nonblank(self.family, "interaction family")
        if family not in {"k_ij", "l_ij", "k_hb_ij"}:
            raise InputError("interaction family is not admitted.")
        object.__setattr__(self, "family", family)
        object.__setattr__(self, "components", _component_pair(self.components, "scientific structural zero"))
        object.__setattr__(self, "reason", _nonblank(self.reason, "structural-zero reason"))
        if not isinstance(self.source, ScientificSource) or self.source.kind != "model_structural_zero":
            raise InputError("scientific structural zero source kind must be model_structural_zero.")


_CORRELATION_TYPES = (
    ConstantCorrelation,
    ReferenceTemperatureLinearCorrelation,
    LogTemperatureCorrelation,
    ConstantPlusExponentialTermsCorrelation,
    PiecewiseQuadraticTemperatureCorrelation,
    SaltFreeWaterMoleFractionCubicPermittivityCorrelation,
)


def _definition_dependency_signature(definition: CorrelationDefinition) -> DependencySignature:
    if isinstance(definition, ConstantCorrelation):
        return DependencySignature(variables=())
    if isinstance(definition, SaltFreeWaterMoleFractionCubicPermittivityCorrelation):
        return DependencySignature(
            variables=(IndependentVariable.MOLE_FRACTION,),
            composition_components=(definition.water_component, definition.organic_component),
        )
    return DependencySignature(variables=(IndependentVariable.TEMPERATURE_K,))


def scientific_record_to_json(record: ScientificRecord) -> dict[str, Any]:
    return {
        "record_id": record.record_id,
        "component": record.component,
        "field": record.field,
        "units": record.units,
        "source": scientific_source_to_json(record.source),
        "dependency_signature": dependency_signature_to_json(record.dependency_signature),
        "temperature_domain": temperature_domain_to_json(record.temperature_domain),
        "definition": correlation_to_json(record.definition),
    }


def scientific_interaction_to_json(record: ScientificInteractionRecord) -> dict[str, Any]:
    return {
        "record_id": record.record_id,
        "family": record.family,
        "components": list(record.components),
        "units": record.units,
        "source": scientific_source_to_json(record.source),
        "dependency_signature": dependency_signature_to_json(record.dependency_signature),
        "temperature_domain": temperature_domain_to_json(record.temperature_domain),
        "definition": correlation_to_json(record.definition),
    }


def scientific_structural_zero_to_json(record: ScientificStructuralZero) -> dict[str, Any]:
    return {
        "record_id": record.record_id,
        "family": record.family,
        "components": list(record.components),
        "reason": record.reason,
        "source": scientific_source_to_json(record.source),
    }


def scientific_record_from_json(payload: Any) -> ScientificRecord:
    data = _exact_mapping(
        payload,
        {"record_id", "component", "field", "units", "source", "dependency_signature", "temperature_domain", "definition"},
        "scientific record",
    )
    return ScientificRecord(
        record_id=data["record_id"],
        component=data["component"],
        field=data["field"],
        units=data["units"],
        source=scientific_source_from_json(data["source"]),
        dependency_signature=dependency_signature_from_json(data["dependency_signature"]),
        temperature_domain=temperature_domain_from_json(data["temperature_domain"]),
        definition=correlation_from_json(data["definition"]),
    )


def scientific_interaction_from_json(payload: Any) -> ScientificInteractionRecord:
    data = _exact_mapping(
        payload,
        {"record_id", "family", "components", "units", "source", "dependency_signature", "temperature_domain", "definition"},
        "scientific interaction",
    )
    return ScientificInteractionRecord(
        record_id=data["record_id"],
        family=data["family"],
        components=tuple(data["components"]),
        units=data["units"],
        source=scientific_source_from_json(data["source"]),
        dependency_signature=dependency_signature_from_json(data["dependency_signature"]),
        temperature_domain=temperature_domain_from_json(data["temperature_domain"]),
        definition=correlation_from_json(data["definition"]),
    )


def scientific_structural_zero_from_json(payload: Any) -> ScientificStructuralZero:
    data = _exact_mapping(payload, {"record_id", "family", "components", "reason", "source"}, "scientific structural zero")
    return ScientificStructuralZero(
        record_id=data["record_id"],
        family=data["family"],
        components=tuple(data["components"]),
        reason=data["reason"],
        source=scientific_source_from_json(data["source"]),
    )


def scientific_source_to_json(source: ScientificSource) -> dict[str, str]:
    return {"kind": source.kind, "locator": source.locator}


def scientific_source_from_json(payload: Any) -> ScientificSource:
    data = _exact_mapping(payload, {"kind", "locator"}, "scientific source")
    return ScientificSource(kind=data["kind"], locator=data["locator"])


def dependency_signature_to_json(signature: DependencySignature) -> dict[str, Any]:
    return {
        "variables": [variable.value for variable in signature.variables],
        "composition_components": list(signature.composition_components),
    }


def dependency_signature_from_json(payload: Any) -> DependencySignature:
    data = _exact_mapping(payload, {"variables", "composition_components"}, "dependency signature")
    if not isinstance(data["variables"], list) or not isinstance(data["composition_components"], list):
        raise InputError("dependency signature variables and composition_components must be arrays.")
    try:
        variables = tuple(IndependentVariable(item) for item in data["variables"])
    except (TypeError, ValueError) as exc:
        raise InputError("dependency signature contains an unknown independent variable.") from exc
    return DependencySignature(variables=variables, composition_components=tuple(data["composition_components"]))


def temperature_domain_to_json(domain: TemperatureDomain) -> dict[str, Any]:
    return {
        "minimum_K": domain.minimum_K,
        "maximum_K": domain.maximum_K,
        "evidence": {"kind": domain.evidence.kind, "source": domain.evidence.source},
    }


def temperature_domain_from_json(payload: Any) -> TemperatureDomain:
    data = _exact_mapping(payload, {"minimum_K", "maximum_K", "evidence"}, "temperature domain")
    evidence = _exact_mapping(data["evidence"], {"kind", "source"}, "domain evidence")
    return TemperatureDomain(
        minimum_K=data["minimum_K"],
        maximum_K=data["maximum_K"],
        evidence=DomainEvidence(kind=evidence["kind"], source=evidence["source"]),
    )


def correlation_to_json(correlation: CorrelationDefinition) -> dict[str, Any]:
    if isinstance(correlation, ConstantCorrelation):
        return {"kind": "constant", "value": correlation.value}
    if isinstance(correlation, ReferenceTemperatureLinearCorrelation):
        return {
            "kind": "reference_temperature_linear",
            "reference_temperature_K": correlation.reference_temperature_K,
            "reference_value": correlation.reference_value,
            "slope_per_K": correlation.slope_per_K,
        }
    if isinstance(correlation, LogTemperatureCorrelation):
        return {
            "kind": "log_temperature",
            "coefficient": correlation.coefficient,
            "intercept": correlation.intercept,
            "reference_temperature_K": correlation.reference_temperature_K,
            "logarithm_base": correlation.logarithm_base,
        }
    if isinstance(correlation, ConstantPlusExponentialTermsCorrelation):
        return {
            "kind": "constant_plus_exponential_terms",
            "constant": correlation.constant,
            "terms": [
                {
                    "coefficient": term.coefficient,
                    "temperature_coefficient_per_K": term.temperature_coefficient_per_K,
                }
                for term in correlation.terms
            ],
        }
    if isinstance(correlation, PiecewiseQuadraticTemperatureCorrelation):
        return {
            "kind": "piecewise_quadratic_temperature",
            "transition_temperature_K": correlation.transition_temperature_K,
            "lower": _quadratic_to_json(correlation.lower),
            "upper": _quadratic_to_json(correlation.upper),
        }
    if isinstance(correlation, SaltFreeWaterMoleFractionCubicPermittivityCorrelation):
        return {
            "kind": "salt_free_water_mole_fraction_cubic_permittivity",
            "water_component": correlation.water_component,
            "organic_component": correlation.organic_component,
            "composition_basis": correlation.composition_basis,
            "coefficient_a": correlation.coefficient_a,
            "coefficient_b": correlation.coefficient_b,
            "coefficient_c": correlation.coefficient_c,
        }
    raise InputError("scientific definition must be a typed correlation.")


def correlation_from_json(payload: Any) -> CorrelationDefinition:
    if not isinstance(payload, Mapping):
        raise InputError("scientific definition must be a typed correlation mapping.")
    kind = payload.get("kind")
    constructors: dict[str, tuple[set[str], Any]] = {
        "constant": ({"kind", "value"}, lambda p: ConstantCorrelation(value=p["value"])),
        "reference_temperature_linear": (
            {"kind", "reference_temperature_K", "reference_value", "slope_per_K"},
            lambda p: ReferenceTemperatureLinearCorrelation(
                reference_temperature_K=p["reference_temperature_K"],
                reference_value=p["reference_value"],
                slope_per_K=p["slope_per_K"],
            ),
        ),
        "log_temperature": (
            {"kind", "coefficient", "intercept", "reference_temperature_K", "logarithm_base"},
            lambda p: LogTemperatureCorrelation(
                coefficient=p["coefficient"],
                intercept=p["intercept"],
                reference_temperature_K=p["reference_temperature_K"],
                logarithm_base=p["logarithm_base"],
            ),
        ),
        "constant_plus_exponential_terms": (
            {"kind", "constant", "terms"},
            _exponential_from_json,
        ),
        "piecewise_quadratic_temperature": (
            {"kind", "transition_temperature_K", "lower", "upper"},
            lambda p: PiecewiseQuadraticTemperatureCorrelation(
                transition_temperature_K=p["transition_temperature_K"],
                lower=_quadratic_from_json(p["lower"]),
                upper=_quadratic_from_json(p["upper"]),
            ),
        ),
        "salt_free_water_mole_fraction_cubic_permittivity": (
            {"kind", "water_component", "organic_component", "composition_basis", "coefficient_a", "coefficient_b", "coefficient_c"},
            lambda p: SaltFreeWaterMoleFractionCubicPermittivityCorrelation(
                water_component=p["water_component"],
                organic_component=p["organic_component"],
                composition_basis=p["composition_basis"],
                coefficient_a=p["coefficient_a"],
                coefficient_b=p["coefficient_b"],
                coefficient_c=p["coefficient_c"],
            ),
        ),
    }
    if kind not in constructors:
        raise InputError("scientific definition must identify an admitted typed correlation.")
    keys, constructor = constructors[kind]
    data = _exact_mapping(payload, keys, f"{kind} correlation")
    return constructor(data)


def _exponential_from_json(payload: Mapping[str, Any]) -> ConstantPlusExponentialTermsCorrelation:
    terms = payload["terms"]
    if not isinstance(terms, list):
        raise InputError("exponential correlation terms must be an array.")
    parsed = []
    for term in terms:
        data = _exact_mapping(term, {"coefficient", "temperature_coefficient_per_K"}, "exponential term")
        parsed.append(
            ExponentialTerm(
                coefficient=data["coefficient"],
                temperature_coefficient_per_K=data["temperature_coefficient_per_K"],
            )
        )
    return ConstantPlusExponentialTermsCorrelation(constant=payload["constant"], terms=tuple(parsed))


def _quadratic_to_json(value: QuadraticCoefficients) -> dict[str, float]:
    return {"quadratic": value.quadratic, "linear": value.linear, "constant": value.constant}


def _quadratic_from_json(payload: Any) -> QuadraticCoefficients:
    data = _exact_mapping(payload, {"quadratic", "linear", "constant"}, "quadratic coefficients")
    return QuadraticCoefficients(quadratic=data["quadratic"], linear=data["linear"], constant=data["constant"])


def _exact_mapping(payload: Any, expected: set[str], owner: str) -> Mapping[str, Any]:
    if not isinstance(payload, Mapping):
        raise InputError(f"{owner} must be a mapping.")
    if any(type(key) is not str for key in payload):
        raise InputError(f"{owner} keys must be strings.")
    unknown = sorted(set(payload) - expected)
    if unknown:
        raise InputError(f"{owner} contains unsupported key(s): {', '.join(unknown)}.")
    missing = sorted(expected - set(payload))
    if missing:
        raise InputError(f"{owner} requires explicit field(s): {', '.join(missing)}.")
    return payload


def _finite_number(value: Any, field_name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, Real):
        raise InputError(f"{field_name} must be a finite number.")
    result = float(value)
    if not math.isfinite(result):
        raise InputError(f"{field_name} must be a finite number.")
    return result


def _nonblank(value: Any, field_name: str) -> str:
    if type(value) is not str or not value.strip():
        raise InputError(f"{field_name} must be nonblank text.")
    return value.strip()


def _component_pair(value: Any, owner: str) -> tuple[str, str]:
    if not isinstance(value, tuple) or len(value) != 2:
        raise InputError(f"{owner} components must contain exactly two component identities.")
    pair = (_nonblank(value[0], f"{owner} component"), _nonblank(value[1], f"{owner} component"))
    if pair[0] == pair[1]:
        raise InputError(f"{owner} components must be distinct.")
    return pair
