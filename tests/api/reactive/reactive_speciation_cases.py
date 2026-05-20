from __future__ import annotations

import numpy as np
import pytest

import epcsaft


def _salt_speciation_mixture() -> epcsaft.ePCSAFTMixture:
    params = {
        "m": np.asarray([1.2047, 1.0, 1.0, 1.0]),
        "s": np.asarray([2.7927, 3.0, 2.8232, 2.7560]),
        "e": np.asarray([353.95, 200.0, 230.0, 170.0]),
        "z": np.asarray([0.0, 0.0, 1.0, -1.0]),
        "dielc": np.asarray([78.09, 8.0, 8.0, 8.0]),
        "d_born": np.asarray([0.0, 0.0, 3.445, 4.1]),
        "MW": np.asarray([18.01528e-3, 58.44e-3, 22.989e-3, 35.45e-3]),
    }
    return epcsaft.ePCSAFTMixture.from_params(params, species=["H2O", "NaCl", "Na+", "Cl-"])

def _native_ipopt_compiled() -> bool:
    from epcsaft import _core

    return bool(_core._native_ipopt_smoke()["compiled"])

def _assert_reactive_speciation_native_ipopt_dependency_required(
    excinfo: pytest.ExceptionInfo[epcsaft.SolutionError],
) -> None:
    message = str(excinfo.value)
    assert "EPCSAFT_ENABLE_IPOPT=ON" in message
