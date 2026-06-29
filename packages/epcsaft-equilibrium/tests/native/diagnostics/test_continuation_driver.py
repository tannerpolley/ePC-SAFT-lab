from __future__ import annotations

import pytest
from epcsaft_equilibrium._native import extension_native_core

_core = extension_native_core()

pytestmark = pytest.mark.native_contract


def _require_ipopt() -> None:
    if not _core._native_ipopt_smoke()["compiled"]:
        pytest.skip("native Ipopt is not compiled")


def test_native_continuation_driver_runs_parameterized_quadratic_path() -> None:
    _require_ipopt()

    smoke = _core._native_continuation_driver_smoke()

    assert smoke["driver"] == "generic_ipopt_continuation_driver"
    assert smoke["accepted"] is True
    assert smoke["final_proof_status"] == "accepted"
    assert smoke["final_stage_id"] == "lambda_1"
    assert [stage["parameter_value"] for stage in smoke["trace"]] == [0.0, 0.5, 1.0]
    assert [stage["stage_id"] for stage in smoke["trace"]] == ["lambda_0", "lambda_half", "lambda_1"]
    assert [stage["final_proof"] for stage in smoke["trace"]] == [False, False, True]

    trace = smoke["trace"]
    assert all(stage["accepted"] is True for stage in trace)
    assert trace[0]["warm_start_requested"] is False
    assert trace[1]["warm_start_requested"] is True
    assert trace[1]["warm_start_used"] is True
    assert trace[2]["warm_start_requested"] is True
    assert trace[2]["warm_start_used"] is True
    assert trace[1]["seeded_from_stage"] == trace[0]["stage_id"]
    assert trace[2]["seeded_from_stage"] == trace[1]["stage_id"]
    assert trace[1]["initial_state"]["variables"] == pytest.approx(trace[0]["continuation_state"]["variables"])
    assert trace[2]["initial_state"]["variables"] == pytest.approx(trace[1]["continuation_state"]["variables"])
    assert smoke["continuation_state"]["variables"] == pytest.approx(trace[-1]["variables"])
    assert len(smoke["continuation_state"]["bound_lower_multipliers"]) == 2
    assert len(smoke["continuation_state"]["bound_upper_multipliers"]) == 2
    assert len(smoke["continuation_state"]["constraint_multipliers"]) == 1
    assert trace[-1]["scaled_constraint_violation_inf_norm"] <= 1.0e-8
    assert trace[-1]["scaled_stationarity_inf_norm"] <= 1.0e-8


def test_native_continuation_driver_final_proof_rejects_trace() -> None:
    _require_ipopt()

    smoke = _core._native_continuation_driver_smoke(final_proof_max_iterations=0)

    assert smoke["accepted"] is False
    assert smoke["final_proof_status"] == "rejected"
    assert smoke["trace"][0]["accepted"] is True
    assert smoke["trace"][1]["accepted"] is True
    assert smoke["trace"][-1]["final_proof"] is True
    assert smoke["trace"][-1]["accepted"] is False
    assert smoke["rejection_stage_id"] == "lambda_1"


def test_native_continuation_driver_rejects_incompatible_initial_state() -> None:
    _require_ipopt()

    bad_state = {
        "variables": [1.0],
        "bound_lower_multipliers": [0.0],
        "bound_upper_multipliers": [0.0],
        "constraint_multipliers": [0.0],
    }

    with pytest.raises(Exception, match="continuation_state.variables"):
        _core._native_continuation_driver_smoke(continuation_state=bad_state)
