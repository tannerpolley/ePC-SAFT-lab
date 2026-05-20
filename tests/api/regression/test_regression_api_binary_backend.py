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


def test_fit_binary_pair_vle_kij_default_and_rejects_temperature_models(monkeypatch):
    calls = _patch_native_generic_ceres_runner(monkeypatch)
    records = [
        {"T": 330.0, "P": 101325.0, "x_H2O": 0.7, "x_Ethanol": 0.3, "y_H2O": 0.5, "y_Ethanol": 0.5},
        {"T": 340.0, "P": 101325.0, "x_H2O": 0.6, "x_Ethanol": 0.4, "y_H2O": 0.4, "y_Ethanol": 0.6},
    ]
    result = epcsaft.fit_binary_pair(
        records,
        ("H2O", "Ethanol"),
        dataset="2026_Khudaida",
        initial_guess={"k_ij": -0.02},
        bounds={"k_ij": (-0.2, 0.2)},
    )

    assert result.success, result.message
    assert result.backend == "ceres"
    assert result.jacobian_available is True
    assert result.jacobian_backend == "cppad_implicit"
    assert result.problem.mode == "binary_pair"
    assert result.problem.fit_targets == ("k_ij",)
    assert set(result.fitted_values) == {"k_ij"}
    assert result.parameter_map == result.fitted_values
    assert result.initial_parameters == {"k_ij": -0.02}
    assert result.final_parameters == result.fitted_values
    assert result.parameter_movement == {"k_ij": 0.0}
    assert result.row_diagnostics == [{"row_family": "binary_vle_fugacity_balance", "metric": 0.0}]
    assert result.active_bounds == []
    assert result.residual_block_norms == {"binary_vle_fugacity_balance": 0.0}
    assert result.source_summaries["records"]["record_count"] == 2
    assert result.target_family_summaries["binary_vle_fugacity_balance"] == {
        "record_count": 2,
        "residual_block_norm": 0.0,
    }
    assert result.metrics_by_term == {"binary_vle_fugacity_balance": 0.0}
    assert result.provenance_report["parameter_movement"] == {"k_ij": 0.0}
    assert result.provenance_report["source_summary"]["record_count"] == 2
    assert len(calls) == 1
    assert calls[0]["optimization_names"] == ("k_ij",)
    assert calls[0]["pair"] == ("H2O", "Ethanol")

    with pytest.raises(InputError, match="temperature_model"):
        epcsaft.fit_binary_pair(
            records,
            ("H2O", "Ethanol"),
            dataset="2026_Khudaida",
            temperature_model="linear",
        )

def test_fit_binary_pair_rejects_unsupported_generic_binary_optimizer_targets(monkeypatch):
    calls = _patch_native_generic_ceres_runner(monkeypatch)
    records = [
        {"T": 330.0, "P": 101325.0, "x_H2O": 0.7, "x_Ethanol": 0.3, "y_H2O": 0.5, "y_Ethanol": 0.5},
        {"T": 340.0, "P": 101325.0, "x_H2O": 0.6, "x_Ethanol": 0.4, "y_H2O": 0.4, "y_Ethanol": 0.6},
    ]

    with pytest.raises(InputError, match="supports only constant k_ij"):
        epcsaft.fit_binary_pair(
            records,
            ("H2O", "Ethanol"),
            dataset="2026_Khudaida",
            fit_targets=("k_ij", "l_ij", "k_hb_ij"),
            initial_guess={"k_ij": -0.02, "l_ij": 0.01, "k_hb_ij": 0.02},
            bounds={"k_ij": (-0.2, 0.2), "l_ij": (-0.2, 0.2), "k_hb_ij": (-0.2, 0.2)},
        )

    assert calls == []

def test_fit_binary_pair_rejects_non_ceres_backend():
    records = [
        {"T": 330.0, "P": 101325.0, "x_H2O": 0.7, "x_Ethanol": 0.3, "y_H2O": 0.5, "y_Ethanol": 0.5},
        {"T": 340.0, "P": 101325.0, "x_H2O": 0.6, "x_Ethanol": 0.4, "y_H2O": 0.4, "y_Ethanol": 0.6},
    ]

    with pytest.raises(InputError, match="Unsupported optimizer_backend"):
        epcsaft.fit_binary_pair(
            records,
            ("H2O", "Ethanol"),
            dataset="2026_Khudaida",
            initial_guess={"k_ij": -0.02},
            optimizer_backend="native_optimizer",
        )

def test_fit_binary_pair_rejects_nonpositive_vle_fractions_before_native_solve():
    records = [
        {"T": 330.0, "P": 101325.0, "x_H2O": 0.7, "x_Ethanol": 0.3, "y_H2O": 0.0, "y_Ethanol": 1.0},
    ]
    with pytest.raises(InputError, match="strictly positive"):
        epcsaft.fit_binary_pair(
            records,
            ("H2O", "Ethanol"),
            dataset="2026_Khudaida",
            initial_guess={"k_ij": -0.02},
        )

def test_fit_binary_pair_rejects_ion_involving_kij_without_direct_electrolyte_provenance():
    records = [
        {
            "T": 298.15,
            "P": 101325.0,
            "x_H2O": 0.998,
            "x_Na+": 0.001,
            "x_Cl-": 0.001,
            "y_H2O": 0.998,
            "y_Na+": 0.001,
            "y_Cl-": 0.001,
        }
    ]

    with pytest.raises(InputError, match=r"opposite-sign ionic pair.*direct electrolyte"):
        epcsaft.fit_binary_pair(
            records,
            ("Na+", "Cl-"),
            dataset="2026_Khudaida",
            species=["H2O", "Na+", "Cl-"],
            initial_guess={"k_ij": 0.0},
        )
