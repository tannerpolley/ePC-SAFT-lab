from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from epcsaft.state.native_adapter import ePCSAFTMixture
from scripts.data.paper_validation_parameters import paper_validation_parameter_path

REPO_ROOT = Path(__file__).resolve().parents[3]
CASE_DIR = (
    REPO_ROOT
    / "data"
    / "reference"
    / "equilibrium_benchmarks"
    / "electrolyte_lle"
    / "water_ethanol_isobutanol_nacl"
)
SPECIES = ["H2O", "Ethanol", "Butanol", "Na+", "Cl-"]
TEMPERATURE = 293.15


def _expanded_first_feed() -> np.ndarray:
    formula = np.asarray(
        [
            0.7490917605469083,
            0.013693284488625435,
            0.21044057604658695,
            0.026774378917879427,
        ],
        dtype=float,
    )
    salt = float(formula[3])
    denominator = 1.0 + salt
    return np.asarray(
        [
            formula[0] / denominator,
            formula[1] / denominator,
            formula[2] / denominator,
            salt / denominator,
            salt / denominator,
        ],
        dtype=float,
    )


def test_khudaida_parameter_bundle_constructs_through_path_without_public_dataset_registration() -> None:
    composition = _expanded_first_feed()

    with pytest.raises(Exception):
        ePCSAFTMixture.from_dataset("2026_Khudaida", SPECIES, composition, TEMPERATURE)

    mixture = ePCSAFTMixture.from_dataset(
        paper_validation_parameter_path("2026_Khudaida"),
        SPECIES,
        composition,
        TEMPERATURE,
    )

    assert mixture.species == SPECIES
    assert mixture.ncomp == 5


def test_electrolyte_gfpe_gate_reports_source_backed_prerequisite_complete() -> None:
    from scripts.validation import check_electrolyte_gfpe_gate as checker

    payload = checker.evaluate_case_dir(
        CASE_DIR,
        require_parameter_bundle=True,
        require_native_diagnostics=True,
    )

    assert payload["complete"] is True
    assert payload["blockers"] == []
    assert payload["fixture"]["feed_row_count"] > 0
    assert payload["fixture"]["tieline_phase_count"] > 0
    assert payload["explicit_ion_expansion"]["formula_species"] == ["H2O", "Ethanol", "Isobutanol", "NaCl"]
    assert payload["explicit_ion_expansion"]["native_species"] == SPECIES
    assert payload["explicit_ion_expansion"]["max_formula_row_sum_error"] <= 1.0e-10
    assert payload["explicit_ion_expansion"]["max_charge_balance_error"] <= 1.0e-8
    assert payload["parameter_bundle"]["status"] == "constructs_native_mixture"
    assert payload["native_diagnostics"]["electrolyte_contribution"]["active"] is True
    assert payload["native_diagnostics"]["phase_system"]["max_phase_charge_residual"] <= 1.0e-8
    assert payload["public_route_state"]["electrolyte_lle"]["production_exposed"] is True
    assert payload["public_route_state"]["electrolyte_lle"]["public_routes"] == ["electrolyte_lle"]
    assert payload["public_route_state"]["electrolyte_lle"]["proof_routes"] == [
        "electrolyte_held2_public_route_admission"
    ]


def test_legacy_closed_route_requirement_rejects_current_public_admission() -> None:
    from scripts.validation import check_electrolyte_gfpe_gate as checker

    payload = checker.evaluate_case_dir(
        CASE_DIR,
        require_parameter_bundle=True,
        require_native_diagnostics=True,
    )

    result = checker.evaluate_payload(payload, require_public_routes_closed=True)

    assert result["complete"] is False
    assert "electrolyte_lle_public_route_exposed" in result["blockers"]
