from __future__ import annotations

from pathlib import Path

import pytest

from analyses.package_validation.explicit_association_toybox.scripts.fixed_state_property_residuals import (
    fixed_state_property_residual_rows,
    load_public_saturation_rows,
)


def test_fixed_state_property_residual_rows_label_fixed_state_workflow() -> None:
    source_rows = [
        {
            "component": "methanol",
            "T_K": 283.15,
            "p_sat_Pa": 6000.0,
            "rho_sat_liq_mol_m3": 24500.0,
            "phase": "liquid",
            "source_url": "https://webbook.nist.gov/example",
        }
    ]

    def evaluator(_case: dict[str, object], row: dict[str, object]) -> dict[str, float]:
        return {
            "provider_pressure_at_exp_density_Pa": float(row["p_sat_Pa"]) * 1.25,
            "provider_density_at_exp_pressure_mol_m3": float(row["rho_sat_liq_mol_m3"]) * 0.9,
            "provider_ares_at_exp_density": -1.5,
        }

    rows = fixed_state_property_residual_rows(
        source_rows,
        provider_cases={
            "methanol": {
                "species": ["Methanol"],
                "parameter_source": "packaged_default",
                "parameters": {
                    "m": [1.0],
                    "s": [3.0],
                    "e": [150.0],
                    "e_assoc": [0.0],
                    "vol_a": [0.0],
                    "assoc_scheme": [None],
                },
            }
        },
        evaluator=evaluator,
    )

    assert len(rows) == 1
    row = rows[0]
    assert row["property_workflow"] == "fixed_state_provider_property_residual"
    assert row["source_role"] == "experimental_saturation_data"
    assert row["model_role"] == "provider_fixed_state_probe"
    assert row["saturation_validation_status"] == "fixed_state_diagnostic"
    assert row["pressure_probe_input"] == "experimental_saturated_liquid_density"
    assert row["density_inverse_input"] == "experimental_saturation_pressure"
    assert row["pressure_probe_status"] == "computed"
    assert row["density_inverse_status"] == "computed_provider_density_root"
    assert row["picard_output_status"] == "computed_toy_pressure_density_coupling"
    assert row["picard_model_role"] == "toy_pcsaft_picard_association"
    assert "no coexistence solve" in row["message"]
    assert row["component"] == "methanol"
    assert row["pressure_relative_residual"] == pytest.approx(0.25)
    assert row["pressure_residual_pa"] == pytest.approx(1500.0)
    assert row["pressure_residual_mpa"] == pytest.approx(0.0015)
    assert row["pressure_residual_rel"] == pytest.approx(0.25)
    assert row["density_relative_residual"] == pytest.approx(-0.1)
    assert row["density_residual_abs"] == pytest.approx(-2450.0)
    assert row["density_residual_rel"] == pytest.approx(-0.1)
    assert row["z_provider"] > row["z_experimental"]
    assert row["z_residual_abs"] == pytest.approx(abs(row["z_provider"] - row["z_experimental"]))
    assert row["provider_ares_at_exp_density"] == pytest.approx(-1.5)
    assert row["toy_exact_model_role"] == "toy_pcsaft_exact_implicit_association"
    assert row["toy_exact_pressure_at_exp_density_Pa"] == pytest.approx(
        row["picard_pressure_at_exp_density_Pa"]
    )
    assert row["toy_exact_density_root_status"] in {
        "computed_toy_liquid_density_root",
        "no_pressure_root_bracket",
    }
    assert row["toy_exact_density_initial_guess_mol_m3"] > 0.0
    assert row["toy_exact_density_initial_guess_policy"] == "legacy_pcsaft_liquid_eta_0_5"
    assert row["toy_exact_density_bracket_policy"] in {
        "experimental_density_center_exact",
        "experimental_density_center_local",
        "legacy_eta_guess_center_exact",
        "legacy_eta_guess_center_local",
        "coarse_density_scan",
        "local_bracket_failed",
    }
    assert row["toy_exact_density_pressure_evaluation_count"] > 0
    assert row["toy_exact_z_at_exp_density"] == pytest.approx(
        row["toy_exact_z_ideal"]
        + row["toy_exact_z_hard_chain"]
        + row["toy_exact_z_dispersion"]
        + row["toy_exact_z_association"]
    )
    assert row["picard_density_root_status"] in {
        "computed_toy_liquid_density_root",
        "no_pressure_root_bracket",
    }
    assert row["picard_density_initial_guess_policy"] == "legacy_pcsaft_liquid_eta_0_5"
    assert row["picard_density_pressure_evaluation_count"] > 0
    assert row["picard_z_at_exp_density"] == pytest.approx(
        row["picard_z_ideal"]
        + row["picard_z_hard_chain"]
        + row["picard_z_dispersion"]
        + row["picard_z_association"]
    )


def test_associating_picard_property_outputs_use_toy_pressure_density_coupling() -> None:
    source_rows = [
        {
            "component": "methanol",
            "T_K": 283.15,
            "p_sat_Pa": 6000.0,
            "rho_sat_liq_mol_m3": 24500.0,
            "phase": "liquid",
            "source_url": "https://webbook.nist.gov/example",
        }
    ]

    def evaluator(_case: dict[str, object], row: dict[str, object]) -> dict[str, float]:
        return {
            "provider_pressure_at_exp_density_Pa": float(row["p_sat_Pa"]) * 1.25,
            "provider_density_at_exp_pressure_mol_m3": float(row["rho_sat_liq_mol_m3"]) * 0.9,
            "provider_ares_at_exp_density": -1.5,
        }

    rows = fixed_state_property_residual_rows(
        source_rows,
        provider_cases={
            "methanol": {
                "species": ["Methanol"],
                "parameter_source": "packaged_default",
                "parameters": {
                    "m": [1.5255],
                    "s": [3.23],
                    "e": [188.9],
                    "e_assoc": [2899.5],
                    "vol_a": [0.03518],
                    "assoc_scheme": ["2B"],
                },
            }
        },
        evaluator=evaluator,
    )

    row = rows[0]
    assert row["picard_output_status"] == "computed_toy_pressure_density_coupling"
    assert row["picard_model_role"] == "toy_pcsaft_picard_association"
    assert row["picard_pressure_at_exp_density_Pa"] != ""
    assert row["picard_density_root_status"] in {
        "computed_toy_liquid_density_root",
        "no_pressure_root_bracket",
    }
    assert row["picard_density_initial_guess_mol_m3"] > 0.0
    assert row["picard_density_initial_guess_policy"] == "legacy_pcsaft_liquid_eta_0_5"
    assert row["picard_density_bracket_policy"] in {
        "experimental_density_center_exact",
        "experimental_density_center_local",
        "legacy_eta_guess_center_exact",
        "legacy_eta_guess_center_local",
        "coarse_density_scan",
        "local_bracket_failed",
    }
    assert "seven damped Picard" in row["picard_message"]


def test_load_public_saturation_rows_fails_loudly_when_source_csv_is_missing(tmp_path: Path) -> None:
    source_root = tmp_path / "saturation_properties"

    with pytest.raises(FileNotFoundError, match="saturation_properties"):
        load_public_saturation_rows(source_root)
