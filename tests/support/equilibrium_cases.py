from __future__ import annotations

import numpy as np

from epcsaft.state.native_adapter import ePCSAFTMixture
from tests.support.runtime_cases import _ionic_params


def _neutral_binary_mixture() -> ePCSAFTMixture:
    params = {
        "m": np.asarray([1.0, 1.6069]),
        "s": np.asarray([3.7039, 3.5206]),
        "e": np.asarray([150.03, 191.42]),
        "k_ij": np.asarray([[0.0, 3.0e-4], [3.0e-4, 0.0]]),
    }
    return ePCSAFTMixture.from_params(params, species=["Methane", "Ethane"])


def _nonideal_lle_binary_mixture() -> ePCSAFTMixture:
    params = {
        "m": np.asarray([1.0, 2.0]),
        "s": np.asarray([3.5, 4.0]),
        "e": np.asarray([150.0, 250.0]),
        "k_ij": np.asarray([[0.0, 0.5], [0.5, 0.0]]),
    }
    return ePCSAFTMixture.from_params(params, species=["A", "B"])


def _methanol_cyclohexane_mixture() -> ePCSAFTMixture:
    params = {
        "MW": np.asarray([32.042e-3, 84.147e-3]),
        "m": np.asarray([1.5255, 2.5303]),
        "s": np.asarray([3.2300, 3.8499]),
        "e": np.asarray([188.90, 278.11]),
        "e_assoc": np.asarray([2899.5, 0.0]),
        "vol_a": np.asarray([0.035176, 0.0]),
        "assoc_scheme": ["2B", None],
        "k_ij": np.asarray([[0.0, 0.051], [0.051, 0.0]]),
        "z": np.asarray([0.0, 0.0]),
        "dielc": np.asarray([33.05, 2.02]),
    }
    return ePCSAFTMixture.from_params(params, species=["Methanol", "Cyclohexane"])


def _methanol_cyclohexane_lle_feed() -> list[float]:
    methanol_poor = np.asarray([0.05, 0.95], dtype=float)
    methanol_rich = np.asarray([0.85, 0.15], dtype=float)
    return (0.5 * methanol_poor + 0.5 * methanol_rich).tolist()


def _hydrocarbon_workbook_params() -> dict[str, np.ndarray]:
    return {
        "m": np.asarray([1.0, 1.6069, 2.0020]),
        "s": np.asarray([3.7039, 3.5206, 3.6184]),
        "e": np.asarray([150.03, 191.42, 208.11]),
        "k_ij": np.asarray(
            [
                [0.0, 3.0e-4, 1.15e-2],
                [3.0e-4, 0.0, 5.10e-3],
                [1.15e-2, 5.10e-3, 0.0],
            ],
            dtype=float,
        ),
    }


# The workbook's "PC-SAFT VLE" sheet is a bubble-pressure solve: fixed T and
# liquid x, liquid/vapor eta roots adjusted to P, and y_i = x_i phi_i^L/phi_i^V.
WORKBOOK_TEMPERATURE = 233.15
WORKBOOK_BUBBLE_PRESSURE = 1_276_369.4735856401
WORKBOOK_LIQUID_COMPOSITION = [0.1, 0.3, 0.6]
WORKBOOK_VAPOR_COMPOSITION = [0.7246628928343289, 0.20293191372324873, 0.0724051934424223]
WORKBOOK_LIQUID_DENSITY = 14_330.417109760687
WORKBOOK_VAPOR_DENSITY = 728.5617203262267


def _hydrocarbon_workbook_mixture() -> ePCSAFTMixture:
    params = _hydrocarbon_workbook_params()
    return ePCSAFTMixture.from_params(params, species=["Methane", "Ethane", "Propane"])


def _ionic_mixture() -> ePCSAFTMixture:
    params = _ionic_params()
    params["assoc_scheme"] = [None, None, None]
    params["e_assoc"] = np.zeros(3)
    params["vol_a"] = np.zeros(3)
    return ePCSAFTMixture.from_params(params, species=["water", "Na+", "Cl-"])


def _reactive_stability_inputs() -> dict[str, object]:
    return {
        "feed_composition": [0.3, 0.7],
        "balance_rows": 1,
        "balance_matrix_row_major": [1.0, 1.0],
        "total_vector": [1.0],
        "reaction_rows": 1,
        "reaction_stoichiometry_row_major": [-1.0, 1.0],
        "log_equilibrium_constants": [0.0],
    }


def _ascani_electrolyte_mixture() -> tuple[ePCSAFTMixture, list[float]]:
    aq = np.asarray([0.798324680201737, 0.016320352824141723, 0.09267748348706063, 0.09267748348706063])
    org = np.asarray([0.37006036048879404, 0.6214918588210971, 0.004223890345054407, 0.004223890345054407])
    beta_org = 0.613766575013417
    feed = ((1.0 - beta_org) * aq + beta_org * org).tolist()
    params = {
        "MW": np.asarray([18.01528e-3, 74.12e-3, 22.98e-3, 35.45e-3]),
        "m": np.asarray([1.2047, 3.626, 1.0, 1.0]),
        "s": np.asarray([2.7927, 3.784, 2.8232, 2.7560]),
        "e": np.asarray([353.95, 250.0, 230.0, 170.0]),
        "e_assoc": np.asarray([2425.7, 0.0, 0.0, 0.0]),
        "vol_a": np.asarray([0.04509, 0.0, 0.0, 0.0]),
        "assoc_scheme": ["2B", None, None, None],
        "z": np.asarray([0.0, 0.0, 1.0, -1.0]),
        "dielc": np.asarray([78.09, 20.0, 8.0, 8.0]),
        "d_born": np.asarray([0.0, 0.0, 3.445, 4.1]),
        "f_solv": np.asarray([1.5, 1.0, 1.0, 1.0]),
        "k_ij": np.zeros((4, 4)),
        "l_ij": np.zeros((4, 4)),
        "k_hb": np.zeros((4, 4)),
    }
    mix = ePCSAFTMixture.from_params(params, species=["H2O", "Butanol", "Na+", "Cl-"])
    return mix, feed


def _dense_jacobian_from_sparse_contract(payload: dict) -> np.ndarray:
    dense = np.zeros((payload["constraint_count"], payload["variable_count"]), dtype=float)
    rows = np.asarray(payload["jacobian_rows"], dtype=int)
    cols = np.asarray(payload["jacobian_cols"], dtype=int)
    values = np.asarray(payload["jacobian_values_at_initial"], dtype=float)
    assert rows.shape == cols.shape == values.shape == (payload["jacobian_nonzero_count"],)
    for row, col, value in zip(rows, cols, values, strict=True):
        dense[row, col] += value
    return dense


