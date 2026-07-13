"""Small strict model configurations for provider boundary tests."""

from __future__ import annotations

from dataclasses import replace

import epcsaft

NEUTRAL_MODEL_CONFIGURATION = {
    "schema": "epcsaft.model-configuration",
    "schema_version": 1,
    "selection_origin": "explicit_configuration",
    "formulation": {
        "electrostatics": {"enabled": False},
        "relative_permittivity": {"enabled": False},
        "debye_huckel": {"enabled": False},
        "born": {"enabled": False},
        "solvated_ion_diameter": {"enabled": False},
        "ion_dispersion": {"enabled": False},
    },
}


def neutral_model_options() -> epcsaft.ModelOptions:
    """Return one explicit all-neutral formulation selection."""

    return epcsaft.ModelOptions.from_user_options(NEUTRAL_MODEL_CONFIGURATION)


def neutral_scientific_parameter_set(
    *,
    reverse_records: bool = False,
    source_locator: str = "Stage 4 resolved-input contract source",
) -> epcsaft.ParameterSet:
    """Return a two-component definitions-only provider fixture."""

    components = ("Methane", "Ethane")
    values = {
        "Methane": {
            "molar_mass_kg_per_mol": (0.016043, "kg/mol"),
            "segment_count": (1.0, "dimensionless"),
            "sigma_angstrom": (3.7039, "angstrom"),
            "epsilon_k_K": (150.03, "K"),
            "charge_number": (0.0, "dimensionless"),
            "association_energy_K": (0.0, "K"),
            "association_volume": (0.0, "dimensionless"),
        },
        "Ethane": {
            "molar_mass_kg_per_mol": (0.03007, "kg/mol"),
            "segment_count": (1.6069, "dimensionless"),
            "sigma_angstrom": (3.5206, "angstrom"),
            "epsilon_k_K": (191.42, "K"),
            "charge_number": (0.0, "dimensionless"),
            "association_energy_K": (0.0, "K"),
            "association_volume": (0.0, "dimensionless"),
        },
    }
    formulation_values = {
        "relative_permittivity": (1.0, "dimensionless"),
        "born_diameter_angstrom": (3.0, "angstrom"),
        "solvation_factor": (1.0, "dimensionless"),
    }
    source = epcsaft.ScientificSource(kind="literature", locator=source_locator)
    domain = epcsaft.TemperatureDomain(
        minimum_K=100.0,
        maximum_K=500.0,
        evidence=epcsaft.DomainEvidence(
            kind="source_validity",
            source="Stage 4 resolved-input contract interval",
        ),
    )

    def record(component: str, field: str, value: float, units: str) -> epcsaft.ScientificRecord:
        return epcsaft.ScientificRecord(
            record_id=f"{component}-{field}",
            component=component,
            field=field,
            units=units,
            source=source,
            dependency_signature=epcsaft.DependencySignature(variables=()),
            temperature_domain=domain,
            definition=epcsaft.ConstantCorrelation(value=value),
        )

    pure_records = tuple(
        record(component, field, value, units)
        for component in components
        for field, (value, units) in values[component].items()
    )
    formulation_records = tuple(
        record(component, field, value, units)
        for component in components
        for field, (value, units) in formulation_values.items()
    )
    policies = tuple(
        epcsaft.ScientificStructuralZero(
            record_id=f"methane-ethane-{family}-zero",
            family=family,
            components=components,
            reason="The cited combining rule supplies no correction.",
            source=epcsaft.ScientificSource(
                kind="model_structural_zero",
                locator="Stage 4 resolved-input contract combining rule",
            ),
        )
        for family in ("k_ij", "l_ij", "k_hb_ij")
    )
    if reverse_records:
        pure_records = tuple(reversed(pure_records))
        formulation_records = tuple(reversed(formulation_records))
        policies = tuple(reversed(policies))
    return epcsaft.ParameterSet.from_schema3_records(
        components=components,
        pure_records=pure_records,
        formulation_records=formulation_records,
        interaction_policies=policies,
        metadata={"source": "Stage 4 resolved-input contract fixture", "source_backed": True},
    )


def scientific_hydrocarbon_parameter_set() -> epcsaft.ParameterSet:
    """Return the source-backed three-component continuity fixture."""

    components = ("Methane", "Ethane", "Propane")
    values = {
        "Methane": (0.016043, 1.0, 3.7039, 150.03),
        "Ethane": (0.030070, 1.6069, 3.5206, 191.42),
        "Propane": (0.044097, 2.0020, 3.6184, 208.11),
    }
    source = epcsaft.ScientificSource(
        kind="literature",
        locator="Gross and Sadowski 2001 Tables 2 and 4",
    )
    domain = epcsaft.TemperatureDomain(
        minimum_K=100.0,
        maximum_K=500.0,
        evidence=epcsaft.DomainEvidence(
            kind="source_validity",
            source="Stage 4 hydrocarbon continuity interval",
        ),
    )

    def record(component: str, field: str, value: float, units: str) -> epcsaft.ScientificRecord:
        return epcsaft.ScientificRecord(
            record_id=f"{component}-{field}",
            component=component,
            field=field,
            units=units,
            source=source,
            dependency_signature=epcsaft.DependencySignature(variables=()),
            temperature_domain=domain,
            definition=epcsaft.ConstantCorrelation(value=value),
        )

    pure_records = []
    formulation_records = []
    for component in components:
        molar_mass, segment_count, sigma, epsilon = values[component]
        pure_records.extend(
            (
                record(component, "molar_mass_kg_per_mol", molar_mass, "kg/mol"),
                record(component, "segment_count", segment_count, "dimensionless"),
                record(component, "sigma_angstrom", sigma, "angstrom"),
                record(component, "epsilon_k_K", epsilon, "K"),
                record(component, "charge_number", 0.0, "dimensionless"),
                record(component, "association_energy_K", 0.0, "K"),
                record(component, "association_volume", 0.0, "dimensionless"),
            )
        )
        formulation_records.extend(
            (
                record(component, "relative_permittivity", 1.0, "dimensionless"),
                record(component, "born_diameter_angstrom", 3.0, "angstrom"),
                record(component, "solvation_factor", 1.0, "dimensionless"),
            )
        )
    interactions = tuple(
        epcsaft.ScientificInteractionRecord(
            record_id=f"{left}-{right}-k_ij",
            family="k_ij",
            components=(left, right),
            units="dimensionless",
            source=source,
            dependency_signature=epcsaft.DependencySignature(variables=()),
            temperature_domain=domain,
            definition=epcsaft.ConstantCorrelation(value=value),
        )
        for left, right, value in (
            ("Methane", "Ethane", 3.0e-4),
            ("Methane", "Propane", 1.15e-2),
            ("Ethane", "Propane", 5.10e-3),
        )
    )
    zeros = tuple(
        epcsaft.ScientificStructuralZero(
            record_id=f"{left}-{right}-{family}-zero",
            family=family,
            components=(left, right),
            reason=reason,
            source=epcsaft.ScientificSource(kind="model_structural_zero", locator=locator),
        )
        for left, right in (
            ("Methane", "Ethane"),
            ("Methane", "Propane"),
            ("Ethane", "Propane"),
        )
        for family, reason, locator in (
            ("l_ij", "The cited Lorentz rule supplies no correction.", "EqID sigma_mixing"),
            (
                "k_hb_ij",
                "The hydrocarbon pair has inactive association topology.",
                "EqID kappa_assoc_mixing",
            ),
        )
    )
    return epcsaft.ParameterSet.from_schema3_records(
        components=components,
        pure_records=tuple(pure_records),
        formulation_records=tuple(formulation_records),
        interactions=interactions,
        interaction_policies=zeros,
        metadata={"source": "Gross and Sadowski 2001 Tables 2 and 4", "source_backed": True},
    )


def with_temperature_dependent_sigma(parameters: epcsaft.ParameterSet) -> epcsaft.ParameterSet:
    """Replace one constant record with a source-backed temperature definition."""

    target = next(
        record
        for record in parameters.pure_records
        if record.component == "Methane" and record.field == "sigma_angstrom"
    )
    replacement = replace(
        target,
        dependency_signature=epcsaft.DependencySignature(
            variables=(epcsaft.IndependentVariable.TEMPERATURE_K,)
        ),
        definition=epcsaft.ReferenceTemperatureLinearCorrelation(
            reference_temperature_K=300.0,
            reference_value=3.7039,
            slope_per_K=1.0e-3,
        ),
    )
    return epcsaft.ParameterSet.from_schema3_records(
        components=parameters.components,
        pure_records=tuple(
            replacement if record.record_id == target.record_id else record
            for record in parameters.pure_records
        ),
        formulation_records=parameters.formulation_records,
        interactions=parameters.interactions,
        interaction_policies=parameters.interaction_policies,
        metadata=parameters.metadata,
    )
