from __future__ import annotations

import numpy as np
import pytest

import epcsaft._core as _core
from tests.support.equilibrium_cases import _nonideal_lle_binary_mixture


def test_neutral_lle_synthetic_binary_accepts_split_with_exact_hessian() -> None:
    _skip_without_ipopt()
    mix = _nonideal_lle_binary_mixture()

    route = _core._native_equilibrium_selector_route_result(
        mix._native,
        {
            "route": "neutral_lle",
            "temperature": 225.0,
            "pressure": 1.0e6,
            "composition": [0.5, 0.5],
            "composition_role": "feed",
        },
        260,
        1.0e-6,
        0.0,
        "auto",
        8,
        1.0e-8,
        1.0e-3,
        1.0e-6,
        1.0e-6,
        {},
        linear_solver="auto",
        acceptable_tolerance=1.0e-7,
        constraint_violation_tolerance=1.0e-8,
        dual_infeasibility_tolerance=1.0e-8,
        complementarity_tolerance=1.0e-8,
    )

    assert route["accepted"] is True
    assert route["status"] == "accepted"
    assert route["selector_family"] == "neutral_lle"
    assert route["route"] == "neutral_lle"
    assert route["problem_name"] == "neutral_lle_eos"
    assert route["activation"]["production_exposed"] is True
    assert route["activation_compiler"] == "activation_plan"
    assert route["constraint_families"] == [
        "material_balance",
        "phase_pressure_consistency",
        "phase_distance",
    ]
    assert "phase_volume_gap" not in route["constraint_families"]
    assert route["hessian_approximation"] == "exact"
    assert route["exact_hessian_available"] is True
    assert route["eval_h_calls"] > 0

    postsolve = route["postsolve"]
    assert postsolve["accepted"] is True
    assert postsolve["material_balance_norm"] <= 1.0e-8
    assert postsolve["pressure_consistency_norm"] <= 1.0e-3
    assert postsolve["ln_fugacity_consistency_norm"] <= 1.0e-6
    assert postsolve["phase_distance"] >= 1.0e-6

    compositions = np.asarray(postsolve["phase_compositions"], dtype=float)
    amounts = np.asarray(route["phase_amounts"], dtype=float)
    assert compositions.shape == (2, 2)
    assert amounts.shape == (2, 2)
    assert np.all(amounts > 0.0)
    assert np.max(np.abs(compositions[0] - compositions[1])) == pytest.approx(
        postsolve["phase_distance"],
        rel=1.0e-8,
        abs=1.0e-10,
    )


def _skip_without_ipopt() -> None:
    if not _core._native_ipopt_smoke()["compiled"]:
        pytest.skip("native Ipopt is not compiled")
