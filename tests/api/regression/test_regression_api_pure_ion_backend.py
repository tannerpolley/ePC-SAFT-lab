from __future__ import annotations

import numpy as np
import pytest

import epcsaft
from epcsaft import fit_pure_neutral
from epcsaft._types import InputError
from epcsaft.regression import _debug_native_pure_neutral_objective
from tests.api.regression.native_backend_cases import (
    _minimal_nacl_records,
    _patch_native_generic_ceres_runner,
)
from tests.helpers.regression_cases import _methane_like_records, _minimal_neutral_metadata


def test_fit_pure_ion_requires_composition_and_supported_records():
    with pytest.raises(InputError, match="composition"):
        epcsaft.fit_pure_ion(
            [{"T": 298.15, "P": 101325.0, "osmotic_coefficient": 0.93}],
            "Na+",
            dataset="2026_Khudaida",
        )

    with pytest.raises(InputError, match=r"density|osmotic|mean-ionic|mean ionic"):
        epcsaft.fit_pure_ion(
            [{"T": 298.15, "P": 101325.0, "molality": 0.1}],
            "Na+",
            dataset="2026_Khudaida",
            species=["H2O", "Na+", "Cl-"],
            solvent="H2O",
        )

def test_fit_pure_ion_default_s_e_bounds_contract(monkeypatch):
    calls = _patch_native_generic_ceres_runner(monkeypatch)
    result = epcsaft.fit_pure_ion(
        _minimal_nacl_records(),
        "Na+",
        dataset="2026_Khudaida",
        species=["H2O", "Na+", "Cl-"],
        solvent="H2O",
        initial_guess={"s": 2.6, "e": 210.0},
        bounds={"s": (2.4, 3.2), "e": (150.0, 300.0)},
    )

    assert result.success, result.message
    assert result.backend == "ceres"
    assert result.jacobian_available is True
    assert result.jacobian_backend == "cppad_implicit"
    assert result.problem.mode == "pure_ion"
    assert result.problem.fit_targets == ("s", "e")
    assert set(result.metrics_by_term) == {"osmotic_coefficient", "mean_ionic_activity"}
    assert result.fitted_values == {"s": 2.6, "e": 210.0}
    assert result.parameter_map == {"s": 2.6, "e": 210.0}
    assert result.active_bounds == []
    assert {row["row_family"] for row in result.row_diagnostics} == {"osmotic_coefficient", "mean_ionic_activity"}
    assert result.provenance_report["parameter_movement"] == {"s": 0.0, "e": 0.0}
    assert len(calls) == 1
    assert calls[0]["optimization_names"] == ("s", "e")
    assert calls[0]["component"] == "Na+"
    assert calls[0]["species"] == ("H2O", "Na+", "Cl-")
    assert {record["term_name"] for record in calls[0]["native_records"]} == {
        "osmotic_coefficient",
        "mean_ionic_activity",
    }

@pytest.mark.parametrize("missing_key", ["optimizer_backend", "derivative_backend"])
def test_fit_pure_ion_requires_native_ceres_backend_metadata(monkeypatch, missing_key):
    _patch_native_generic_ceres_runner(monkeypatch, omit_result_keys=(missing_key,))

    with pytest.raises(RuntimeError, match=rf"missing required '{missing_key}' metadata"):
        epcsaft.fit_pure_ion(
            _minimal_nacl_records(),
            "Na+",
            dataset="2026_Khudaida",
            species=["H2O", "Na+", "Cl-"],
            solvent="H2O",
            initial_guess={"s": 2.6, "e": 210.0},
            bounds={"s": (2.4, 3.2), "e": (150.0, 300.0)},
        )

def test_fit_pure_ion_accepts_d_born_and_born_user_options(monkeypatch):
    calls = _patch_native_generic_ceres_runner(monkeypatch)
    user_options = {
        "elec_model": {
            "rel_perm": {"rule": "empirical", "differential_mode": "cppad"},
            "born_model": {
                "d_Born_mode": 3,
                "solvation_shell_model": True,
                "dielectric_saturation": True,
                "mu_born_model": {"differential_mode": "cppad", "comp_dep_delta_d": True},
            },
        }
    }
    result = epcsaft.fit_pure_ion(
        _minimal_nacl_records(),
        "Na+",
        dataset="2026_Khudaida",
        species=["H2O", "Na+", "Cl-"],
        solvent="H2O",
        fit_targets=("d_born",),
        initial_guess={"d_born": 3.2},
        bounds={"d_born": (2.0, 5.0)},
        user_options=user_options,
    )

    assert result.success, result.message
    assert result.backend == "ceres"
    assert result.jacobian_backend == "cppad_implicit"
    assert result.problem.fit_targets == ("d_born",)
    assert "osmotic_coefficient" in result.metrics_by_term
    assert len(calls) == 1
    assert calls[0]["optimization_names"] == ("d_born",)
    assert result.provenance_report["parameter_sources"]["Na+.d_born"] == "ion_activity"

def test_fit_pure_ion_passes_explicit_mean_ionic_pair_label_to_native_backend(monkeypatch):
    calls = _patch_native_generic_ceres_runner(monkeypatch)
    records = [dict(record, pair_label="Na+Cl-") for record in _minimal_nacl_records()]
    result = epcsaft.fit_pure_ion(
        records,
        "Na+",
        dataset="2026_Khudaida",
        species=["H2O", "Na+", "Cl-"],
        solvent="H2O",
        initial_guess={"s": 2.6, "e": 210.0},
        bounds={"s": (2.4, 3.2), "e": (150.0, 300.0)},
    )

    assert result.success, result.message
    assert result.backend == "ceres"
    assert "mean_ionic_activity" in result.metrics_by_term
    assert len(calls) == 1
    mean_ionic_record = next(
        record for record in calls[0]["native_records"] if record["term_name"] == "mean_ionic_activity"
    )
    assert mean_ionic_record["target_index"] == 1
    assert mean_ionic_record["target_index_2"] == 2
