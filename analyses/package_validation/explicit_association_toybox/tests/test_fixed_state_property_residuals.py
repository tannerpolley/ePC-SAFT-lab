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
        provider_cases={"methanol": {"species": ["Methanol"], "parameter_source": "packaged_default"}},
        evaluator=evaluator,
    )

    assert len(rows) == 1
    row = rows[0]
    assert row["property_workflow"] == "fixed_state_saturation_property_residual"
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


def test_load_public_saturation_rows_fails_loudly_when_source_csv_is_missing(tmp_path: Path) -> None:
    source = tmp_path / "public_saturation_properties.csv"

    with pytest.raises(FileNotFoundError, match="shared/source/public_saturation_properties.csv"):
        load_public_saturation_rows(source)
