from __future__ import annotations

import numpy as np
import pytest


def _contains_key(value: object, forbidden: str) -> bool:
    if isinstance(value, dict):
        return forbidden in value or any(_contains_key(item, forbidden) for item in value.values())
    if isinstance(value, (list, tuple)):
        return any(_contains_key(item, forbidden) for item in value)
    return False


def test_stage3_callback_has_exact_sparse_derivatives() -> None:
    from cython_held2_experiment._stage3 import manufactured_stage3_evaluation

    point = np.asarray((0.45, 0.55, 0.20, 0.80, 0.0, 0.0))
    lagrange = np.asarray((0.7, -0.4))
    observed = manufactured_stage3_evaluation(point, lagrange, 1.0)
    gradient = np.asarray(observed["gradient"])
    constraints = np.asarray(observed["constraints"])
    jacobian = np.asarray(observed["jacobian"])
    hessian = np.asarray(observed["hessian"])

    assert observed["jacobian_nonzeros"] == 6
    assert observed["hessian_lower_nonzeros"] == 10
    assert jacobian.shape == (2, 6)
    assert hessian.shape == (6, 6)
    assert np.allclose(hessian, hessian.T, rtol=0.0, atol=1.0e-13)

    step = 2.0e-6
    for coordinate in range(point.size):
        lower = point.copy()
        upper = point.copy()
        lower[coordinate] -= step
        upper[coordinate] += step
        lower_result = manufactured_stage3_evaluation(lower, lagrange, 1.0)
        upper_result = manufactured_stage3_evaluation(upper, lagrange, 1.0)
        finite_gradient = (upper_result["objective"] - lower_result["objective"]) / (2.0 * step)
        finite_jacobian = (np.asarray(upper_result["constraints"]) - np.asarray(lower_result["constraints"])) / (
            2.0 * step
        )
        finite_lagrangian_column = (
            np.asarray(upper_result["lagrangian_gradient"]) - np.asarray(lower_result["lagrangian_gradient"])
        ) / (2.0 * step)
        assert gradient[coordinate] == pytest.approx(finite_gradient, rel=2.0e-7, abs=2.0e-7)
        assert jacobian[:, coordinate] == pytest.approx(finite_jacobian, rel=2.0e-7, abs=2.0e-7)
        assert hessian[:, coordinate] == pytest.approx(finite_lagrangian_column, rel=2.0e-6, abs=2.0e-5)
    assert constraints == pytest.approx((0.0, 0.03), abs=1.0e-14)


def test_kkt_inactive_phase_is_retired_only_after_dual_pullback_and_resolve() -> None:
    from cython_held2_experiment import manufactured_stage3_demo

    result = manufactured_stage3_demo("inactive")

    assert result["outcome"] == "accepted"
    assert result["solver_status"] == "passed"
    assert result["numerical_status"] == "passed"
    assert result["physical_status"] == "passed"
    assert result["initial_solve"]["dual_pullback"]["status"] == "passed"
    assert result["retirement"]["retired_ids"] == ["inactive"]
    assert result["retirement"]["basis"] == "kkt_certified_lower_bound_inactivity"
    assert result["active_set_confirmation"]["performed"] is True
    assert result["active_set_confirmation"]["settings_unchanged"] is True
    assert result["active_set_confirmation"]["numerical_status"] == "passed"
    assert result["active_set_confirmation"]["physical_status"] == "passed"
    assert [phase["id"] for phase in result["phases"]] == ["alpha", "beta"]


def test_step9_physical_rejection_returns_named_stage2_feedback() -> None:
    from cython_held2_experiment import manufactured_stage3_demo

    result = manufactured_stage3_demo("feedback")

    assert result["outcome"] == "return_to_stage2"
    assert result["feedback"] == "step9_physical_rejection"
    assert result["solver_status"] == "passed"
    assert result["numerical_status"] == "passed"
    assert result["physical_status"] == "failed"
    assert result["step9"]["modified_potential_equality"] == "failed"
    assert result["step9"]["material_balance"] == "passed"
    assert result["step9"]["pressure_equality"] == "passed"


def test_step9_recomputes_kkt_from_retained_raw_residuals() -> None:
    from cython_held2_experiment._stage3 import _step9, manufactured_stage3_demo

    solved = manufactured_stage3_demo("split")
    forged = dict(solved["initial_solve"])
    forged["numerical_status"] = "passed"
    forged["stationarity_inf_norm"] = 1.0

    result = _step9(forged, 0.5)

    assert result["kkt_and_feasibility"] == "failed"
    assert result["status"] == "failed"
    assert result["metrics"]["stationarity_inf_norm"] == 1.0


def test_kkt_retirement_with_fewer_than_two_phases_fails_closed() -> None:
    from cython_held2_experiment._stage3 import _retirement_decision

    result = _retirement_decision(
        ("active", "inactive-a", "inactive-b"),
        ("inactive-a", "inactive-b"),
    )

    assert result["proceed"] is False
    assert result["feedback"] == "insufficient_active_phases_after_kkt_retirement"
    assert result["retirement"] == {
        "retired_ids": ["inactive-a", "inactive-b"],
        "basis": "kkt_certified_lower_bound_inactivity",
    }
    assert result["active_set_confirmation"] == {
        "performed": False,
        "reason": "fewer_than_two_active_phases",
    }


@pytest.mark.parametrize(
    ("case", "outcome", "physical"),
    (
        ("stable", "one_phase", "passed"),
        ("unstable", "two_phase", "passed"),
        ("feedback", "return_to_stage2", "failed"),
        ("trace", "two_phase", "passed"),
    ),
)
def test_full_manufactured_route_has_ten_step_ledger_and_only_three_status_axes(
    case: str, outcome: str, physical: str
) -> None:
    from cython_held2_experiment import manufactured_full_demo

    result = manufactured_full_demo(case)
    assert result["outcome"] == outcome
    assert result["physical_status"] == physical
    assert {entry["step"] for entry in result["step_ledger"]} == set(range(1, 11))
    assert {"solver_status", "numerical_status", "physical_status"} <= set(result)
    assert not _contains_key(result, "globality_certificate")
    if case == "trace":
        trace = result["trace"]
        assert trace["status"] == "passed"
        assert trace["iterations"] >= 2
        assert trace["final_fraction"] < trace["initial_fraction"]
        assert result["step_ledger"][-1]["status"] == "completed"


def test_displaced_python_controller_surfaces_remain_absent() -> None:
    from pathlib import Path

    root = Path(__file__).resolve().parents[5]
    family = root / "analyses/reference_oracles/equilibrium_formulations/families"
    forbidden = (
        "perdomo_held2_controller.py",
        "perdomo_held2_legacy_eos.py",
        "perdomo_held2_physical_probe.py",
    )
    assert all(not (family / name).exists() for name in forbidden)

    production_files = (
        *family.glob("*.py"),
        root / "analyses/reference_oracles/equilibrium_formulations/registry.py",
    )
    text = "\n".join(path.read_text(encoding="utf-8") for path in production_files)
    assert "perdomo_held2_controller" not in text
    assert "perdomo_held2_legacy_eos" not in text
    assert "perdomo_held2_physical_probe" not in text
    assert "backend_selector" not in text
