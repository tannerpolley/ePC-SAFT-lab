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
    assert route["status"] == "production_accepted"
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
    assert postsolve["phase_discovery_backend"] == "deterministic_tpd_candidate_screening"
    assert postsolve["stability_certificate"] == "tpd_postsolve"
    assert postsolve["stability_checked"] is True
    assert postsolve["stability_accepted"] is True
    assert postsolve["candidate_completeness_accepted"] is True
    assert postsolve["phase_set_mass_balance_feasible"] is True
    assert postsolve["phase_set_status"] == "phase_set_certified"
    assert postsolve["tpd_candidate_count"] >= postsolve["unique_candidate_count"] >= 1
    assert postsolve["selected_candidate_count"] == 2
    assert len(postsolve["tpd_candidate_ranks"]) == postsolve["unique_candidate_count"]
    assert len(postsolve["tpd_candidate_sources"]) == postsolve["unique_candidate_count"]
    assert len(postsolve["tpd_candidate_pressure_residuals"]) == postsolve["unique_candidate_count"]
    assert len(postsolve["tpd_candidate_feasibility_statuses"]) == postsolve["unique_candidate_count"]
    assert len(postsolve["tpd_candidate_selected"]) == postsolve["unique_candidate_count"]
    assert postsolve["seed_and_stability"]["phase_discovery_backend"] == "deterministic_tpd_candidate_screening"
    assert postsolve["seed_and_stability"]["candidate_source_count"] == postsolve["unique_candidate_count"]
    assert postsolve["seed_and_stability"]["candidate_sources"] == postsolve["tpd_candidate_sources"]
    assert postsolve["seed_and_stability"]["deterministic_screening_is_full_held"] is False
    assert postsolve["candidate_mass_balance_norm"] <= 1.0e-8
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

    certificate = route["stability_certificate"]
    assert certificate["accepted"] is True
    assert certificate["method"] == "tpd_postsolve"
    assert certificate["phase_discovery_backend"] == "deterministic_tpd_candidate_screening"
    assert certificate["stability_checked"] is True
    assert certificate["stability_accepted"] is True
    assert certificate["candidate_set_complete"] is True
    assert certificate["status"] == "phase_set_certified"
    assert certificate["min_tpd"] == pytest.approx(postsolve["min_tpd"])


def test_neutral_tpd_phase_discovery_reports_candidate_set_for_lle_binary() -> None:
    mix = _nonideal_lle_binary_mixture()

    discovery = _core._native_neutral_tpd_phase_discovery(
        mix._native,
        225.0,
        1.0e6,
        [0.5, 0.5],
        [0, 0],
        1.0e-6,
        1.0e-6,
    )

    assert discovery["phase_discovery_backend"] == "deterministic_tpd_candidate_screening"
    assert discovery["stability_certificate"] == "tpd_postsolve"
    assert discovery["stability_checked"] is True
    assert discovery["tpd_candidate_count"] >= discovery["unique_candidate_count"] >= 1
    assert discovery["phase_set_mass_balance_feasible"] is True
    assert discovery["candidate_completeness_accepted"] is True
    assert discovery["candidate_mass_balance_norm"] <= 1.0e-6
    assert discovery["selected_candidate_count"] == 2
    assert len(discovery["selected_phase_compositions"]) == 2
    assert len(discovery["candidates"]) == discovery["unique_candidate_count"]
    assert [candidate["candidate_rank"] for candidate in discovery["candidates"]] == list(
        range(discovery["unique_candidate_count"])
    )
    assert sum(candidate["selected"] for candidate in discovery["candidates"]) == discovery["selected_candidate_count"]
    for candidate in discovery["candidates"]:
        assert candidate["source"].startswith("feed_phase_kind_")
        assert candidate["feasibility_status"] in {
            "selected_mass_balance_feasible",
            "mass_balance_pair_unselected",
            "candidate_mass_balance_incomplete",
        }
        assert np.isfinite(candidate["pressure_residual_estimate"])
        assert abs(candidate["pressure_residual_estimate"]) <= 1.0e-5


def _skip_without_ipopt() -> None:
    if not _core._native_ipopt_smoke()["compiled"]:
        pytest.skip("native Ipopt is not compiled")
