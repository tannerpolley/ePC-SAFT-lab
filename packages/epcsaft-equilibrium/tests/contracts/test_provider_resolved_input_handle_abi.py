from __future__ import annotations

import gc
import importlib
from pathlib import Path

import epcsaft
import epcsaft_equilibrium._native_core as equilibrium_core
import pytest


def _provider_handle():
    domain = epcsaft.TemperatureDomain(
        100.0,
        500.0,
        epcsaft.DomainEvidence("source_validity", "Stage 4 equilibrium ABI fixture"),
    )
    source = epcsaft.ScientificSource("literature", "Stage 4 equilibrium ABI fixture")
    values = {
        "molar_mass_kg_per_mol": (0.016043, "kg/mol"),
        "segment_count": (1.0, "dimensionless"),
        "sigma_angstrom": (3.7039, "angstrom"),
        "epsilon_k_K": (150.03, "K"),
        "charge_number": (0.0, "dimensionless"),
        "association_energy_K": (0.0, "K"),
        "association_volume": (0.0, "dimensionless"),
    }
    records = tuple(
        epcsaft.ScientificRecord(
            f"methane-{field}",
            "Methane",
            field,
            units,
            source,
            epcsaft.DependencySignature(()),
            domain,
            epcsaft.ConstantCorrelation(value),
        )
        for field, (value, units) in values.items()
    )
    parameters = epcsaft.ParameterSet.from_schema3_records(
        components=("Methane",),
        pure_records=records,
    )
    configuration = epcsaft.ModelOptions.from_user_options(
        {
            "schema": "epcsaft.model-configuration",
            "schema_version": 1,
            "selection_origin": "explicit_configuration",
            "formulation": {
                name: {"enabled": False}
                for name in (
                    "electrostatics",
                    "relative_permittivity",
                    "debye_huckel",
                    "born",
                    "solvated_ion_diameter",
                    "ion_dispersion",
                )
            },
        }
    )
    selection = epcsaft.SourceBundleSelection(
        parameters,
        configuration,
        (Path("parameter_set.json"), Path("model_configuration.json")),
    )
    module = importlib.import_module("epcsaft.model._resolved_input_native")
    resolved = module._build_native_resolved_input(selection, components=("Methane",))
    return module._evaluate_native_resolved_input(
        resolved,
        temperature_K=300.0,
        canonical_composition=(1.0,),
    )


def test_equilibrium_retains_and_reads_the_provider_owned_handle() -> None:
    handle = _provider_handle()
    detached = {
        "schema": handle.schema,
        "snapshot_fingerprint_sha256": handle.snapshot_fingerprint_sha256,
    }
    expected = equilibrium_core._native_provider_resolved_input_handle_probe(handle)
    del detached
    gc.collect()

    assert equilibrium_core._native_provider_resolved_input_handle_probe(handle) == expected
    assert expected["contract_id"] == "provider_resolved_input_handle_v1"
    assert expected["component_order"] == ["Methane"]
    with pytest.raises(TypeError):
        equilibrium_core._native_provider_resolved_input_handle_probe(expected)
