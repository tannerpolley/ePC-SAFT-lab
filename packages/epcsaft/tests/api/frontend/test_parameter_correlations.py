from __future__ import annotations

import math

import epcsaft.model as model
import pytest
from epcsaft._types import InputError


def _api(name: str):
    value = getattr(model, name, None)
    assert value is not None, f"epcsaft.model.{name} is required"
    return value


def _evidence():
    return _api("DomainEvidence")(
        kind="source_validity",
        source="test_parameter_correlations.py contract interval",
    )


def _domain():
    return _api("TemperatureDomain")(minimum_K=250.0, maximum_K=400.0, evidence=_evidence())


def _temperature_dependency():
    variable = _api("IndependentVariable")
    return _api("DependencySignature")(variables=(variable.TEMPERATURE_K,))


def test_dependency_signature_is_fail_closed_and_separate_from_domains() -> None:
    variable = _api("IndependentVariable")
    dependency = _api("DependencySignature")

    assert dependency(variables=()).variables == ()
    assert _domain().minimum_K == 250.0
    with pytest.raises(InputError, match="unique"):
        dependency(variables=(variable.TEMPERATURE_K, variable.TEMPERATURE_K))
    with pytest.raises(InputError, match="component identities"):
        dependency(variables=(variable.MOLE_FRACTION,))
    with pytest.raises(InputError, match="mole-fraction dependency"):
        dependency(variables=(), composition_components=("Water",))
    with pytest.raises((InputError, ValueError)):
        dependency(variables=("unknown_state",))


def test_temperature_domain_is_inclusive_source_bearing_and_strict() -> None:
    domain = _domain()

    assert domain.validate(250.0) == 250.0
    assert domain.validate(400.0) == 400.0
    with pytest.raises(InputError, match="outside"):
        domain.validate(249.999)
    with pytest.raises(InputError, match="finite"):
        domain.validate(float("nan"))
    with pytest.raises(InputError, match="minimum"):
        _api("TemperatureDomain")(minimum_K=400.0, maximum_K=250.0, evidence=_evidence())


@pytest.mark.parametrize(
    ("factory", "temperature", "expected"),
    (
        (lambda: _api("ConstantCorrelation")(value=7.0), 300.0, (7.0, 0.0, 0.0)),
        (
            lambda: _api("ReferenceTemperatureLinearCorrelation")(
                reference_temperature_K=300.0,
                reference_value=10.0,
                slope_per_K=0.25,
            ),
            304.0,
            (11.0, 0.25, 0.0),
        ),
        (
            lambda: _api("LogTemperatureCorrelation")(
                coefficient=2.0,
                intercept=1.0,
                reference_temperature_K=1.0,
                logarithm_base="natural",
            ),
            math.e,
            (3.0, 2.0 / math.e, -2.0 / math.e**2),
        ),
        (
            lambda: _api("ConstantPlusExponentialTermsCorrelation")(
                constant=1.0,
                terms=(_api("ExponentialTerm")(coefficient=2.0, temperature_coefficient_per_K=0.01),),
            ),
            300.0,
            (1.0 + 2.0 * math.exp(3.0), 0.02 * math.exp(3.0), 0.0002 * math.exp(3.0)),
        ),
        (
            lambda: _api("PiecewiseQuadraticTemperatureCorrelation")(
                transition_temperature_K=300.0,
                lower=_api("QuadraticCoefficients")(quadratic=0.0, linear=2.0, constant=1.0),
                upper=_api("QuadraticCoefficients")(quadratic=1.0, linear=0.0, constant=0.0),
            ),
            320.0,
            (102400.0, 640.0, 2.0),
        ),
    ),
)
def test_typed_temperature_correlations_carry_first_and_second_derivatives(factory, temperature, expected) -> None:
    actual = factory().temperature_derivatives(temperature)

    assert actual == pytest.approx(expected)


def test_logarithmic_and_exponential_correlations_reject_ambiguous_input() -> None:
    with pytest.raises(InputError, match="logarithm_base"):
        _api("LogTemperatureCorrelation")(
            coefficient=1.0,
            intercept=0.0,
            reference_temperature_K=1.0,
            logarithm_base="base10",
        )
    with pytest.raises(InputError, match="finite number"):
        _api("ExponentialTerm")(coefficient="2.0", temperature_coefficient_per_K=0.01)


def test_composition_cubic_has_explicit_component_dependencies_basis_and_derivatives() -> None:
    variable = _api("IndependentVariable")
    dependency = _api("DependencySignature")(
        variables=(variable.MOLE_FRACTION,),
        composition_components=("Water", "Methanol"),
    )
    correlation = _api("SaltFreeWaterMoleFractionCubicPermittivityCorrelation")(
        water_component="Water",
        organic_component="Methanol",
        composition_basis="salt_free_solvent_mole_fraction",
        coefficient_a=1.0,
        coefficient_b=2.0,
        coefficient_c=3.0,
    )

    assert dependency.composition_components == ("Water", "Methanol")
    assert correlation.composition_derivatives(0.5, organic_relative_permittivity=10.0) == pytest.approx(
        (12.125, 5.75, 7.0)
    )
    with pytest.raises(InputError, match=r"\[0, 1\]"):
        correlation.composition_derivatives(1.1, organic_relative_permittivity=10.0)
    with pytest.raises(InputError, match="composition_basis"):
        _api("SaltFreeWaterMoleFractionCubicPermittivityCorrelation")(
            water_component="Water",
            organic_component="Methanol",
            composition_basis="mass_fraction",
            coefficient_a=1.0,
            coefficient_b=2.0,
            coefficient_c=3.0,
        )


def test_scientific_record_keeps_dependency_domain_source_and_definition_without_evaluation() -> None:
    source = _api("ScientificSource")(
        kind="literature",
        locator="Gross and Sadowski 2001 Table 2",
    )
    definition = _api("ReferenceTemperatureLinearCorrelation")(
        reference_temperature_K=300.0,
        reference_value=0.1,
        slope_per_K=1.0e-4,
    )
    record = _api("ScientificRecord")(
        record_id="methane-temperature-example",
        component="Methane",
        field="epsilon_k_K",
        units="K",
        source=source,
        dependency_signature=_temperature_dependency(),
        temperature_domain=_domain(),
        definition=definition,
    )

    assert record.definition is definition
    assert record.source is source
    assert record.dependency_signature.variables == (_api("IndependentVariable").TEMPERATURE_K,)
    assert record.evaluate(temperature_K=300.0) == pytest.approx(0.1)
    with pytest.raises(InputError, match="units"):
        _api("ScientificRecord")(
            record_id="bad-units",
            component="Methane",
            field="epsilon_k_K",
            units="calorie-ish",
            source=source,
            dependency_signature=_temperature_dependency(),
            temperature_domain=_domain(),
            definition=definition,
        )


def test_scientific_record_dependency_and_units_must_match_the_typed_definition() -> None:
    source = _api("ScientificSource")(
        kind="literature",
        locator="test_parameter_correlations.py dependency contract",
    )
    with pytest.raises(InputError, match="dependency signature"):
        _api("ScientificRecord")(
            record_id="temperature-definition-without-dependency",
            component="Methane",
            field="epsilon_k_K",
            units="K",
            source=source,
            dependency_signature=_api("DependencySignature")(variables=()),
            temperature_domain=_domain(),
            definition=_api("ReferenceTemperatureLinearCorrelation")(
                reference_temperature_K=300.0,
                reference_value=150.0,
                slope_per_K=0.1,
            ),
        )
    with pytest.raises(InputError, match="units"):
        _api("ScientificRecord")(
            record_id="sigma-with-wrong-units",
            component="Methane",
            field="sigma_angstrom",
            units="K",
            source=source,
            dependency_signature=_api("DependencySignature")(variables=()),
            temperature_domain=_domain(),
            definition=_api("ConstantCorrelation")(value=3.7),
        )
