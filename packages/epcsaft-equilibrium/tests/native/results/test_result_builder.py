from __future__ import annotations

import epcsaft_equilibrium.workflows as workflows_module
import numpy as np
import pytest
from epcsaft.state.native_adapter import ePCSAFTMixture
from epcsaft_equilibrium._native import extension_native_core

_core = extension_native_core()


class _NoSecondAcceptanceBinding:
    def __getattr__(self, name: str) -> object:
        raise AssertionError(f"public selector result attempted a second native call: {name}")


def _neutral_binary_mixture() -> ePCSAFTMixture:
    params = {
        "m": np.asarray([1.0, 1.6069]),
        "s": np.asarray([3.7039, 3.5206]),
        "e": np.asarray([150.03, 191.42]),
        "k_ij": np.asarray([[0.0, 3.0e-4], [3.0e-4, 0.0]]),
    }
    return ePCSAFTMixture.from_params(params, species=["Methane", "Ethane"])


def _sampled_candidate_raw_evidence(**overrides: object) -> dict[str, object]:
    evidence: dict[str, object] = {
        "continuous_tpd_required": True,
        "continuous_tpd_status": "converged",
        "candidate_count": 2,
        "major_iterations": 1,
        "lower_bound": 0.0,
        "phase_set_mass_balance_feasible": True,
        "selected_candidate_count": 2,
        "bound_gap": 0.0,
        "bound_tolerance": 1.0e-8,
    }
    evidence.update(overrides)
    return evidence


def _electrolyte_stage_iii_raw_evidence(**overrides: object) -> dict[str, object]:
    evidence: dict[str, object] = {
        "solver_accepted": True,
        "route_accepted": True,
        "solver_status": "success",
        "application_status": "solve_succeeded",
        "phase_compositions": [[0.9, 0.1], [0.1, 0.9]],
        "residual_values": [0.0, 0.0],
        "equation_labels": ["pair_mean_ionic_equality:Na+/Cl-", "phase_fraction_closure"],
        "residual_inf_norm": 0.0,
        "residual_tolerance": 1.0e-8,
        "phase_distance": 0.8,
        "phase_distance_tolerance": 1.0e-8,
        "active_bound_violation": 0.0,
        "active_bound_tolerance": 1.0e-8,
        "exact_reduced_jacobian_available": True,
        "exact_reduced_hessian_available": True,
    }
    evidence.update(overrides)
    return evidence


def test_sampled_candidate_result_builder_rejects_count_only_evidence_without_replay_payload() -> None:
    payload = _core._native_result_builder_complete_sampled_candidate_bound_audit(
        _sampled_candidate_raw_evidence()
    )

    assert payload == {
        "status": "sampled_candidate_audit_incomplete",
        "candidate_bound_audit_status": "candidate_bound_gap_closed",
        "dual_loop_status": "not_performed",
        "stopping_reason": "sampled_candidate_replay_metadata_incomplete",
        "replay_ready": False,
        "replay_source": "",
        "replay_seed_name": "",
    }


@pytest.mark.parametrize(
    ("mutation", "expected_status"),
    [
        ({"bound_gap": float("nan")}, "sampled_candidate_audit_incomplete"),
        ({"bound_tolerance": float("nan")}, "sampled_candidate_audit_incomplete"),
        ({"lower_bound": float("nan")}, "inconclusive_no_finite_candidate_bound"),
    ],
)
def test_sampled_candidate_result_builder_rejects_nan_evidence(
    mutation: dict[str, object],
    expected_status: str,
) -> None:
    payload = _core._native_result_builder_complete_sampled_candidate_bound_audit(
        _sampled_candidate_raw_evidence(**mutation)
    )

    assert payload["status"] == expected_status
    assert payload["replay_ready"] is False
    assert payload["replay_source"] == ""
    assert payload["replay_seed_name"] == ""


@pytest.mark.parametrize(
    ("mutation", "expected_status"),
    [
        ({"continuous_tpd_required": False}, "not_requested"),
        ({"continuous_tpd_status": "incomplete_iteration_limit"}, "incomplete_stage_i_evidence"),
        ({"candidate_count": 0}, "inconclusive_no_candidates"),
        ({"major_iterations": 0}, "inconclusive_no_finite_candidate_bound"),
        ({"major_iterations": -1}, "inconclusive_no_finite_candidate_bound"),
        ({"phase_set_mass_balance_feasible": False}, "candidate_simplex_mass_balance_incomplete"),
        ({"selected_candidate_count": 1}, "candidate_simplex_mass_balance_incomplete"),
        ({"bound_gap": 2.0e-8}, "sampled_candidate_audit_incomplete"),
        ({"bound_gap": -1.0e-8}, "sampled_candidate_audit_incomplete"),
        ({"bound_tolerance": -1.0e-8}, "sampled_candidate_audit_incomplete"),
        ({"selected_candidate_count": 3}, "sampled_candidate_audit_incomplete"),
    ],
)
def test_sampled_candidate_result_builder_rejects_incomplete_evidence(
    mutation: dict[str, object],
    expected_status: str,
) -> None:
    payload = _core._native_result_builder_complete_sampled_candidate_bound_audit(
        _sampled_candidate_raw_evidence(**mutation)
    )

    assert payload["status"] == expected_status
    assert payload["replay_ready"] is False


def test_electrolyte_stage_iii_result_builder_rejects_evidence_without_stage_ii_replay_or_solver_vectors() -> None:
    payload = _core._native_result_builder_certify_electrolyte_stage_iii_refinement(
        _electrolyte_stage_iii_raw_evidence()
    )

    assert payload == {
        "status": "incomplete",
        "stage_iii_refinement_status": "incomplete",
    }


@pytest.mark.parametrize(
    "mutation",
    [
        {"residual_inf_norm": float("nan")},
        {"residual_tolerance": float("nan")},
        {"phase_distance": float("nan")},
        {"phase_distance_tolerance": float("nan")},
        {"active_bound_violation": float("nan")},
        {"active_bound_tolerance": float("nan")},
        {"phase_compositions": [[0.9, 0.1], [float("nan"), 0.9]]},
        {"residual_values": [float("nan"), 0.0]},
        {"residual_values": [float("inf"), 0.0]},
    ],
)
def test_electrolyte_stage_iii_result_builder_rejects_nan_evidence(
    mutation: dict[str, object],
) -> None:
    payload = _core._native_result_builder_certify_electrolyte_stage_iii_refinement(
        _electrolyte_stage_iii_raw_evidence(**mutation)
    )

    assert payload == {
        "status": "incomplete",
        "stage_iii_refinement_status": "incomplete",
    }


@pytest.mark.parametrize(
    "mutation",
    [
        {"solver_accepted": False},
        {"route_accepted": False},
        {"solver_status": "acceptable_point"},
        {"application_status": "solved_to_acceptable_level"},
        {"phase_compositions": []},
        {"phase_compositions": [[], []]},
        {"phase_compositions": [[0.9, 0.1], [-0.1, 1.1]]},
        {"residual_values": [], "equation_labels": []},
        {"residual_inf_norm": 2.0e-8},
        {"residual_inf_norm": -1.0},
        {"residual_tolerance": -1.0},
        {"residual_values": [0.0]},
        {"phase_distance": 1.0e-8},
        {"phase_distance": -1.0},
        {"phase_distance_tolerance": -1.0},
        {"active_bound_violation": 2.0e-8},
        {"active_bound_violation": -1.0},
        {"active_bound_tolerance": -1.0},
        {"exact_reduced_jacobian_available": False},
        {"exact_reduced_hessian_available": False},
    ],
)
def test_electrolyte_stage_iii_result_builder_rejects_each_incomplete_gate(
    mutation: dict[str, object],
) -> None:
    payload = _core._native_result_builder_certify_electrolyte_stage_iii_refinement(
        _electrolyte_stage_iii_raw_evidence(**mutation)
    )

    assert payload == {
        "status": "incomplete",
        "stage_iii_refinement_status": "incomplete",
    }


def test_selector_result_adapter_uses_canonical_physical_evidence_without_second_native_call(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(workflows_module, "extension_native_core", lambda: _NoSecondAcceptanceBinding())
    phase_evidence = [
        {
            "label": "phase_0",
            "role": "liquid",
            "phase_kind": 0,
            "amount_total": 0.8,
            "volume": 1.0e-4,
            "density": 8000.0,
            "phase_fraction": 0.4,
            "composition": [0.75, 0.25],
            "ln_fugacity_coefficients": [-0.2, -0.1],
        },
        {
            "label": "phase_1",
            "role": "vapor",
            "phase_kind": 1,
            "amount_total": 1.2,
            "volume": 2.0e-2,
            "density": 60.0,
            "phase_fraction": 0.6,
            "composition": [0.2, 0.8],
            "ln_fugacity_coefficients": [0.05, 0.02],
        },
    ]
    route = {
        "accepted": True,
        "status": "accepted",
        "backend": "ipopt",
        "solver_accepted": True,
        "postsolve_accepted": True,
        "rejection_reason": "accepted",
        "selector_family": "bubble_dew_derived_routes",
        "route": "bubble_pressure",
        "postsolve": {
            "accepted": True,
            "rejection_reason": "accepted",
            "stability_checked": False,
            "stability_accepted": True,
            "candidate_completeness_accepted": True,
            "stability_certificate": "postsolve_local_only",
            "phase_set_status": "not_required",
            "material_balance_norm": 0.0,
            "pressure_consistency_norm": 1.0e-7,
            "chemical_potential_consistency_norm": 1.0e-8,
            "ln_fugacity_consistency_norm": 1.0e-8,
            "phase_distance": 0.55,
        },
        "physical_evidence": {
            "phase_labels": ["liquid", "vapor"],
            "phase_roles": ["liquid", "vapor"],
            "phases": phase_evidence,
        },
    }

    result = workflows_module._accepted_native_selector_two_phase_result(
        T=300.0,
        P=2.5e6,
        route=route,
        public_route="bubble_pressure",
        problem_kind="neutral_bubble_p",
        route_label="bubble_pressure",
        selector_family="bubble_dew_derived_routes",
        composition_role="liquid",
    )

    assert result.problem_kind == "neutral_bubble_p"
    assert result.backend == "native_equilibrium_nlp"
    assert result.route == "bubble_pressure"
    assert result.selector_route == "bubble_pressure"
    assert result.split_detected is True
    assert result.phase_labels == ["liquid", "vapor"]
    assert result.phases["liquid"].temperature == pytest.approx(300.0)
    assert result.phases["liquid"].pressure == pytest.approx(2.5e6)
    assert result.phases["liquid"].fugacity_coefficient == pytest.approx(np.exp([-0.2, -0.1]))
    assert result.diagnostics["route_status"] == "accepted"
    assert result.diagnostics["postsolve_certification"]["accepted"] is True


def test_neutral_two_phase_postsolve_certifier_accepts_metrics_and_retains_evidence() -> None:
    mix = _neutral_binary_mixture()
    temperature = 300.0
    phase_amounts = [
        np.asarray([0.7, 0.3], dtype=float),
        np.asarray([0.1, 0.9], dtype=float),
    ]
    density = 120.0
    volumes = [float(phase.sum() / density) for phase in phase_amounts]
    feed_amounts = phase_amounts[0] + phase_amounts[1]
    target_pressure = mix.state(
        T=temperature,
        rho=density,
        x=phase_amounts[0] / phase_amounts[0].sum(),
        phase="liquid",
    ).pressure()

    payload = _core._native_neutral_two_phase_eos_postsolve(
        mix._native,
        temperature,
        target_pressure,
        [phase.tolist() for phase in phase_amounts],
        volumes,
        feed_amounts.tolist(),
        1.0e-8,
        1.0e12,
        1.0e12,
        1.0e-3,
    )

    assert payload["accepted"] is True
    assert payload["derivative_backend"] == "analytic_cppad"
    assert payload["rejection_reason"] == "accepted"
    assert payload["phase_distance"] > 1.0e-3
    assert payload["material_balance_norm"] <= 1.0e-12
    assert payload["ln_fugacity_consistency_norm"] <= 1.0e12
    assert payload["phase_count"] == 2
    assert payload["phase_amount_totals"] == pytest.approx([1.0, 1.0])
    assert payload["phase_volumes"] == pytest.approx(volumes)
    assert payload["phase_densities"] == pytest.approx([density, density])
    np.testing.assert_allclose(
        payload["phase_compositions"],
        [(phase / phase.sum()).tolist() for phase in phase_amounts],
    )

    reduced_ln_fugacity = []
    for composition_raw, ln_phi_raw in zip(
        payload["phase_compositions"],
        payload["phase_ln_fugacity_coefficients"],
        strict=True,
    ):
        composition = np.asarray(composition_raw, dtype=float)
        ln_phi = np.asarray(ln_phi_raw, dtype=float)
        reduced_ln_fugacity.append(np.log(composition) + ln_phi)
    expected_ln_fugacity_norm = float(np.max(np.abs(reduced_ln_fugacity[0] - reduced_ln_fugacity[1])))
    assert payload["ln_fugacity_consistency_norm"] == pytest.approx(expected_ln_fugacity_norm)


def test_neutral_two_phase_postsolve_certifier_authors_rejection_reason() -> None:
    mix = _neutral_binary_mixture()
    temperature = 300.0
    phase_amounts = [
        np.asarray([0.4, 0.6], dtype=float),
        np.asarray([0.4, 0.6], dtype=float),
    ]
    density = 120.0
    volumes = [float(phase.sum() / density) for phase in phase_amounts]
    feed_amounts = phase_amounts[0] + phase_amounts[1]
    target_pressure = mix.state(
        T=temperature,
        rho=density,
        x=phase_amounts[0] / phase_amounts[0].sum(),
        phase="liquid",
    ).pressure()
    target_pressure *= 1.1

    payload = _core._native_neutral_two_phase_eos_postsolve(
        mix._native,
        temperature,
        target_pressure,
        [phase.tolist() for phase in phase_amounts],
        volumes,
        feed_amounts.tolist(),
        1.0e-8,
        1.0e-12,
        1.0e12,
        1.0e-3,
    )

    assert payload["accepted"] is False
    assert payload["rejection_reason"] == "pressure_consistency"
    assert payload["phase_count"] == 2
    assert payload["phase_distance"] == pytest.approx(0.0, abs=1.0e-14)
    assert payload["ln_fugacity_consistency_norm"] == pytest.approx(0.0, abs=1.0e-14)
