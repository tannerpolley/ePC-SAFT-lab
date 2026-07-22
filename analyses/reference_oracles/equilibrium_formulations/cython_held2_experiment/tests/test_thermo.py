from __future__ import annotations

import csv
import math
from pathlib import Path

import numpy as np
import pytest

EXPERIMENT_ROOT = Path(__file__).resolve().parents[1]


def test_evaluate_state_reports_complete_helmholtz_partition() -> None:
    from cython_held2_experiment import evaluate_state

    state = evaluate_state(
        298.15,
        (0.964, 0.018, 0.018),
        1.8e-5,
    )

    contributions = state["contributions"]
    assert set(contributions) == {
        "ideal",
        "hard_chain",
        "dispersion",
        "association",
        "debye_huckel",
        "born_ssm_ds",
    }
    assert math.isclose(
        state["helmholtz_over_rt"],
        sum(contributions.values()),
        rel_tol=2.0e-15,
        abs_tol=2.0e-14,
    )
    assert math.isfinite(state["pressure_pa"])
    assert len(state["chemical_potential_inputs_over_rt"]) == 3
    assert state["solver_convergence"] == "passed"
    assert state["numerical_convergence"] == "passed"
    assert state["physical_validity"] == "passed"
    assert state["globality_certificate"] == "not_applicable"


def test_reduced_derivatives_match_fresh_association_resolves() -> None:
    from cython_held2_experiment import derivative_bundle, evaluate_state

    temperature = 298.15
    amounts = np.array((0.964, 0.018, 0.018), dtype=float)
    volume = 1.8e-5
    derivatives = derivative_bundle(temperature, amounts, volume)
    gradient = np.asarray(derivatives["gradient"])
    hessian = np.asarray(derivatives["hessian"])
    state = evaluate_state(temperature, amounts, volume)

    assert gradient.shape == (5,)
    assert hessian.shape == (5, 5)
    assert np.allclose(hessian, hessian.T, rtol=2.0e-13, atol=2.0e-8)
    assert state["pressure_pa"] == pytest.approx(-8.31446261815324 * temperature * gradient[4], rel=3.0e-13)
    assert derivatives["association"]["residual_inf_norm"] <= 2.0e-13
    assert math.isfinite(derivatives["association"]["jacobian_condition"])

    # This salt direction preserves electroneutrality. Every outer value call
    # independently resolves both water site fractions before evaluating A/RT.
    direction = np.array((0.0, 0.0, 1.0, 1.0, 0.0), dtype=float)
    step = 2.0e-6

    def resolved_value(offset: float) -> float:
        shifted = amounts + offset * direction[1:4]
        return evaluate_state(temperature, shifted, volume)["helmholtz_over_rt"]

    center = resolved_value(0.0)
    lower = resolved_value(-step)
    upper = resolved_value(step)
    finite_gradient = (upper - lower) / (2.0 * step)
    finite_curvature = (upper - 2.0 * center + lower) / (step * step)

    assert math.isclose(float(gradient @ direction), finite_gradient, rel_tol=3.0e-7, abs_tol=3.0e-7)
    assert math.isclose(
        float(direction @ hessian @ direction),
        finite_curvature,
        rel_tol=2.0e-4,
        abs_tol=2.0e-2,
    )


def test_source_identity_and_physical_domain_fail_closed() -> None:
    from cython_held2_experiment import evaluate_state, source_identity

    identity = source_identity()
    assert identity["provider_commit"] == "97d7b37db601a147a316f3f2e63293d5ea3a95f6"
    assert identity["selected_model_fingerprint"] == (
        "sha256:7c637771bc9f717b8f47b44bb2a61044c3fe83084dca7c3c16102fba0989912d"
    )
    assert identity["species_order"] == (
        "water",
        "sodium-cation",
        "chloride-anion",
    )
    assert identity["diameter_mixing_rule"] == "lorentz-fixed-no-lij"

    with pytest.raises(ValueError, match="electroneutral"):
        evaluate_state(298.15, (0.97, 0.02, 0.01), 1.8e-5)
    with pytest.raises(ValueError, match="source domain"):
        evaluate_state(300.0, (0.964, 0.018, 0.018), 1.8e-5)
    with pytest.raises(ValueError, match="ion mole fraction"):
        evaluate_state(298.15, (0.4, 0.3, 0.3), 1.8e-5)


def test_retained_provider_matrix_has_no_unexplained_discrepancy() -> None:
    with (EXPERIMENT_ROOT / "evidence" / "provider_comparison.csv").open(newline="") as stream:
        rows = list(csv.DictReader(stream))

    assert len(rows) == 6
    assert {(row["composition"], row["regime"]) for row in rows} == {
        (composition, regime) for composition in ("dilute", "feed") for regime in ("dense", "intermediate", "gas_safe")
    }
    for row in rows:
        assert row["provider_status"] == "0"
        assert row["fingerprint_match"] == "true"
        assert row["result"] == "pass"
        for observed, allowance in (
            ("contribution_max_abs_error", "contribution_allowance"),
            ("value_abs_error", "value_allowance"),
            ("temperature_gradient_abs_error", "temperature_gradient_allowance"),
            ("temperature_hessian_abs_error", "temperature_hessian_allowance"),
            ("pressure_abs_error_pa", "pressure_allowance_pa"),
            ("gradient_max_abs_error", "gradient_allowance"),
            ("hessian_max_abs_error", "hessian_allowance"),
        ):
            assert float(row[observed]) <= float(row[allowance])
        assert float(row["association_residual_inf"]) <= 2.0e-13
