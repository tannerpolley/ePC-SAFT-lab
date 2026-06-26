from __future__ import annotations

import importlib.util
import json
import math
from pathlib import Path

import pytest
import yaml
from epcsaft import InputError
from epcsaft_equilibrium.chemical_equilibrium import (
    EquilibriumConstantRecord,
    StandardStateRecord,
    build_standard_state_registry,
)

REPO_ROOT = Path(__file__).resolve().parents[4]
ASCANI_ANALYSIS = REPO_ROOT / "analyses" / "paper_validation" / "2023_ascani" / "analysis.yaml"
ASCANI_RUNNER = REPO_ROOT / "analyses" / "paper_validation" / "2023_ascani" / "scripts" / "run_all.py"


def test_equilibrium_constant_registry_accepts_log_k_and_delta_g() -> None:
    mole_fraction = StandardStateRecord(
        label="aqueous_mole_fraction",
        activity_convention="mole_fraction_activity",
        temperature_K=298.15,
        pressure_Pa=101325.0,
    )
    molality = StandardStateRecord(
        label="aqueous_molality",
        activity_convention="molality",
        temperature_K=298.15,
        pressure_Pa=101325.0,
        standard_molality_mol_kg=1.0,
    )

    log_record = EquilibriumConstantRecord(
        reaction_label="water_autoionization",
        value=-14.0,
        form="log10_K",
        units="dimensionless",
        standard_state=mole_fraction,
        source="contract fixture",
        source_constant_label="pKw",
    )
    delta_g_record = EquilibriumConstantRecord(
        reaction_label="acid_dissociation",
        value=5_708.0,
        form="delta_g_standard",
        units="J/mol",
        standard_state=molality,
        source="contract fixture",
        source_constant_label="delta_g_standard",
    )

    registry = build_standard_state_registry([log_record, delta_g_record])

    assert registry.reaction_labels == ("water_autoionization", "acid_dissociation")
    assert log_record.ln_equilibrium_constant() == pytest.approx(-14.0 * math.log(10.0))
    assert delta_g_record.ln_equilibrium_constant() == pytest.approx(-5_708.0 / (8.31446261815324 * 298.15))
    assert registry.records["water_autoionization"].standard_state.activity_convention == "mole_fraction_activity"
    assert registry.records["acid_dissociation"].standard_state.standard_molality_mol_kg == 1.0


def test_standard_state_records_cover_fugacity_and_eos_x_phi_payloads() -> None:
    fugacity = StandardStateRecord(
        label="pure_vapor_fugacity",
        activity_convention="fugacity",
        temperature_K=353.15,
        pressure_Pa=101325.0,
        standard_fugacity_Pa=100000.0,
    )
    eos_x_phi = StandardStateRecord(
        label="liquid_x_phi",
        activity_convention="eos_x_phi",
        temperature_K=318.15,
        pressure_Pa=101300.0,
        eos_reference_phase="liquid",
    )
    registry = build_standard_state_registry(
        [
            EquilibriumConstantRecord(
                reaction_label="vapor_association",
                value=2.0,
                form="K",
                units="dimensionless",
                standard_state=fugacity,
                source="contract fixture",
                source_constant_label="K_f",
            ),
            EquilibriumConstantRecord(
                reaction_label="liquid_esterification",
                value=43.99,
                form="K",
                units="dimensionless",
                standard_state=eos_x_phi,
                source="Ascani 2023 Table 4",
                source_constant_label="K_a",
            ),
        ]
    )

    payload = registry.to_native_payload()

    assert payload["records"][0]["standard_state"]["activity_convention"] == "fugacity"
    assert payload["records"][0]["standard_state"]["standard_fugacity_Pa"] == 100000.0
    assert payload["records"][1]["standard_state"]["activity_convention"] == "eos_x_phi"
    assert payload["records"][1]["standard_state"]["eos_reference_phase"] == "liquid"
    assert payload["records"][1]["ln_equilibrium_constant"] == pytest.approx(math.log(43.99))
    json.dumps(payload)


def test_registry_rejects_missing_temperature_units_or_convention_metadata() -> None:
    with pytest.raises(InputError, match="temperature"):
        StandardStateRecord(
            label="missing_temperature",
            activity_convention="mole_fraction_activity",
            temperature_K=None,
            pressure_Pa=101325.0,
        )

    with pytest.raises(InputError, match="standard molality"):
        StandardStateRecord(
            label="missing_molality",
            activity_convention="molality",
            temperature_K=298.15,
            pressure_Pa=101325.0,
        )

    state = StandardStateRecord(
        label="valid",
        activity_convention="mole_fraction_activity",
        temperature_K=298.15,
        pressure_Pa=101325.0,
    )
    with pytest.raises(InputError, match="units"):
        EquilibriumConstantRecord(
            reaction_label="bad_units",
            value=1.0,
            form="delta_g_standard",
            units="dimensionless",
            standard_state=state,
            source="contract fixture",
            source_constant_label="bad",
        )


def test_ascani_analysis_retains_source_constants_in_standard_state_registry() -> None:
    data = yaml.safe_load(ASCANI_ANALYSIS.read_text(encoding="utf-8"))
    entries = data["expected"]["standard_state_registry"]

    assert entries["system_1"] == {
        "reaction_label": "ascani_2023_system1_esterification",
        "source_constant_label": "K_a",
        "constant_form": "K",
        "value": 43.99,
        "units": "dimensionless",
        "temperature_K": 318.15,
        "pressure_bar": 1.0,
        "activity_convention": "mole_fraction_activity",
        "standard_state_label": "ascani_mole_fraction_activity",
        "conversion": "retained_source_activity_constant_without_unit_conversion",
    }
    assert entries["system_2"]["reaction_label"] == "ascani_2023_system2_esterification"
    assert entries["system_2"]["value"] == 22.92
    assert entries["system_2"]["temperature_K"] == 353.6


def test_ascani_runner_uses_registry_for_retained_log_constant() -> None:
    spec = importlib.util.spec_from_file_location("ascani_2023_runner", ASCANI_RUNNER)
    assert spec is not None
    assert spec.loader is not None
    runner = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(runner)

    payload = runner._ascani_standard_state_payload()

    assert runner._ascani_ln_equilibrium_constant("ascani_2023_system1_esterification") == pytest.approx(
        math.log(43.99)
    )
    assert payload["records"][0]["metadata"]["retained_source_constant"] == {"label": "K_a", "value": 43.99}
