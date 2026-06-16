from __future__ import annotations

import numpy as np
import pytest

from epcsaft_equilibrium._native import extension_native_core
from epcsaft.state.native_adapter import ePCSAFTMixture

_core = extension_native_core()
from equilibrium_support.equilibrium_cases import (
    WORKBOOK_BUBBLE_PRESSURE,
    WORKBOOK_TEMPERATURE,
    _hydrocarbon_workbook_mixture,
)


def _skip_without_ipopt() -> None:
    if not _core._native_ipopt_smoke()["compiled"]:
        pytest.skip("Ipopt native adapter is not compiled.")


def _three_phase_hydrocarbon_case() -> tuple[object, float, float, list[list[float]], list[float], list[float]]:
    mix = _hydrocarbon_workbook_mixture()
    composition = np.asarray([0.2, 0.3, 0.5], dtype=float)
    density = 14_000.0
    target_pressure = mix.state(
        T=WORKBOOK_TEMPERATURE,
        rho=density,
        x=composition,
        phase="liquid",
    ).pressure()
    phase_totals = np.asarray([0.6, 0.3, 0.1], dtype=float)
    phase_amounts = [(total * composition).tolist() for total in phase_totals]
    volumes = [float(total / density) for total in phase_totals]
    feed_amounts = np.sum(np.asarray(phase_amounts, dtype=float), axis=0).tolist()
    return mix, WORKBOOK_TEMPERATURE, float(target_pressure), phase_amounts, volumes, feed_amounts


def _symmetric_ternary_nonassociating_mixture() -> ePCSAFTMixture:
    params = {
        "m": np.asarray([1.5, 1.5, 1.5], dtype=float),
        "s": np.asarray([3.7, 3.7, 3.7], dtype=float),
        "e": np.asarray([220.0, 220.0, 220.0], dtype=float),
        "k_ij": np.asarray(
            [
                [0.0, 0.8, 0.8],
                [0.8, 0.0, 0.8],
                [0.8, 0.8, 0.0],
            ],
            dtype=float,
        ),
    }
    return ePCSAFTMixture.from_params(params, species=["A", "B", "C"])


def test_internal_multiphase_activation_plan_contract_builds_three_phase_layout() -> None:
    mix = _hydrocarbon_workbook_mixture()

    payload = _core._native_equilibrium_activation_plan_contract(
        mix._native,
        {
            "route": "neutral_multiphase_nonassoc",
            "temperature": WORKBOOK_TEMPERATURE,
            "pressure": WORKBOOK_BUBBLE_PRESSURE,
            "composition": [0.2, 0.3, 0.5],
            "composition_role": "feed",
            "phase_kinds": ["liquid", "liquid", "vapor"],
        },
    )

    plan = payload["activation_plan"]
    layout = payload["variable_layout"]

    assert plan["family_key"] == "neutral_multiphase_nonassoc"
    assert plan["route"] == "neutral_multiphase_nonassoc"
    assert plan["phase_keys"] == ["liquid1", "liquid2", "vapor"]
    assert plan["phase_kinds"] == ["liquid", "liquid", "vapor"]
    assert plan["variable_blocks"] == ["phase_species_amounts", "phase_volumes"]
    assert plan["constraint_blocks"] == ["material_balance", "phase_pressure_consistency"]
    assert plan["residual_blocks"] == [
        "material_balance",
        "phase_pressure_consistency",
        "phase_equilibrium",
        "phase_distance",
    ]
    assert plan["variable_model"] == "phase_species_amounts_plus_phase_volume"
    assert plan["density_backend"] == "explicit_phase_volume_pressure_constraint"
    assert plan["feed_composition"] == pytest.approx([0.2, 0.3, 0.5])

    assert layout["family_key"] == "neutral_multiphase_nonassoc"
    assert layout["route"] == "neutral_multiphase_nonassoc"
    assert layout["phase_count"] == 3
    assert layout["species_count"] == 3
    assert layout["variable_count"] == 12
    assert layout["phase_amount_indices"] == [[0, 1, 2], [4, 5, 6], [8, 9, 10]]
    assert layout["phase_volume_indices"] == [3, 7, 11]


def test_internal_multiphase_eos_nlp_contract_reports_exact_hessian_for_three_phase_state() -> None:
    mix, temperature, target_pressure, phase_amounts, volumes, feed_amounts = _three_phase_hydrocarbon_case()

    payload = _core._native_neutral_multiphase_eos_nlp_contract(
        mix._native,
        temperature,
        target_pressure,
        phase_amounts,
        volumes,
        feed_amounts,
    )

    assert payload["problem_name"] == "neutral_multiphase_eos"
    assert payload["phase_count"] == 3
    assert payload["species_count"] == 3
    assert payload["variable_count"] == 12
    assert payload["constraint_count"] == 6
    assert payload["jacobian_nonzero_count"] == 21
    assert payload["exact_hessian_available"] is True
    assert payload["hessian_backend"] == "cppad_phase_system"
    assert payload["variable_model"] == "phase_species_amounts_plus_phase_volume"
    assert payload["density_backend"] == "explicit_phase_volume_pressure_constraint"
    assert payload["residual_families"] == [
        "material_balance",
        "phase_pressure_consistency",
        "phase_equilibrium",
        "phase_distance",
    ]
    assert payload["constraint_families"] == ["material_balance", "phase_pressure_consistency"]


def test_internal_multiphase_phase_set_diagnostics_certify_three_phase_shape_without_public_exposure() -> None:
    mix = _symmetric_ternary_nonassociating_mixture()

    payload = _core._native_neutral_tpd_phase_discovery(
        mix._native,
        200.0,
        1.0e6,
        [1.0 / 3.0, 1.0 / 3.0, 1.0 / 3.0],
        [0, 0, 0],
        1.0e-6,
        1.0e-6,
    )

    assert payload["phase_set_status"] == "phase_set_certified"
    assert payload["phase_set_mass_balance_feasible"] is True
    assert payload["stability_accepted"] is True
    assert payload["candidate_completeness_accepted"] is True
    assert payload["held_stage_ii_replay_seed_name"] == "held_stage_ii_dual_loop_candidate_set"
    assert payload["phase_distance"] > 0.0
    assert payload["selected_candidate_count"] == 3
    assert payload["selected_phase_kinds"] == [0, 0, 0]
    assert len(payload["selected_phase_compositions"]) == 3
    assert len(payload["phase_set_records"]) >= 3
    selected_records = [row for row in payload["phase_set_records"] if row["selection_status"] == "selected"]
    rejected_records = [row for row in payload["phase_set_records"] if row["selection_status"] == "rejected"]
    assert len(selected_records) == 3
    assert rejected_records
    required_fields = {
        "record_id",
        "phase_count",
        "phase_index",
        "phase_kind",
        "phase_role",
        "source",
        "phase_amount_total",
        "phase_fraction",
        "volume",
        "density",
        "composition",
        "objective",
        "tpd",
        "feasibility_status",
        "selection_status",
        "rejection_reason",
        "phase_set_status",
        "mass_balance_feasible",
        "stability_accepted",
        "candidate_completeness_accepted",
    }
    for row in payload["phase_set_records"]:
        assert required_fields.issubset(row)
        assert row["phase_count"] == 3
        assert len(row["composition"]) == 3
        assert row["selection_status"] in {"selected", "rejected"}
        if row["selection_status"] == "rejected":
            assert row["rejection_reason"] not in {"", "accepted"}
    first_selected = selected_records[0]
    assert first_selected["phase_amount_total"] == pytest.approx(payload["selected_phase_fractions"][0])
    assert first_selected["phase_fraction"] == pytest.approx(payload["selected_phase_fractions"][0])
    assert first_selected["volume"] > 0.0
    assert first_selected["density"] > 0.0
    assert first_selected["composition"] == pytest.approx(payload["selected_phase_compositions"][0])
    assert payload["phase_discovery_backend"] == "continuous_tpd_held_dual_phase_discovery"
    assert payload["stability_certificate"] == "tpd_postsolve"
    assert payload["candidate_mass_balance_norm"] >= 0.0


def test_internal_multiphase_strict_fugacity_residual_route_consumes_stage_ii_candidate_set() -> None:
    _skip_without_ipopt()
    mix = _symmetric_ternary_nonassociating_mixture()

    payload = _core._native_neutral_multiphase_fugacity_residual_route_result(
        mix._native,
        200.0,
        1.0e6,
        [1.0 / 3.0, 1.0 / 3.0, 1.0 / 3.0],
        [0, 0, 0],
        320,
        1.0e-8,
        0.0,
        "auto",
        50,
        1.0e-8,
        1.0e-3,
        1.0e-6,
        1.0e-6,
        {},
        linear_solver="auto",
        option_profile="held_refinement",
        print_level=0,
        acceptable_tolerance=1.0e-8,
        constraint_violation_tolerance=1.0e-8,
        dual_infeasibility_tolerance=1.0e-8,
        complementarity_tolerance=1.0e-8,
    )

    postsolve = payload["postsolve"]
    assert payload["route"] == "neutral_multiphase_nonassoc"
    assert payload["route_refinement_kind"] == "strict_fugacity_residual"
    assert payload["problem_name"] == "neutral_multiphase_fugacity_residual"
    assert payload["solver_status"] == "success"
    assert payload["application_status"] == "solve_succeeded"
    assert payload["accepted"] is True
    assert payload["exact_hessian_available"] is True
    assert payload["hessian_backend"] == "cppad_phase_system_plus_reduced_fugacity_residual"
    assert payload["residual_exact_jacobian_available"] is True
    assert payload["residual_exact_hessian_available"] is True
    assert payload["public_route_admission"] == "closed"
    assert payload["requested_phase_kinds"] == [0, 0, 0]
    assert payload["requested_phase_count"] == 3
    assert payload["seed_name"] == "held_stage_ii_dual_loop_candidate_set"
    assert payload["seed_attempts"]
    assert all(attempt["status"] != "max_iterations_exceeded" for attempt in payload["seed_attempts"])
    assert postsolve["accepted"] is True
    assert postsolve["ln_fugacity_consistency_norm"] <= 1.0e-6
    assert postsolve["held_stage_ii_replay_seed_name"] == "held_stage_ii_dual_loop_candidate_set"
    assert postsolve["held_stage_iii_status"] == "ipopt_refinement_completed_current_route"
    assert postsolve["held_stage_iii_consumed_stage_ii_replay_metadata"] is True
    assert postsolve["held_stage_iii_replay_seed_name"] == "held_stage_ii_dual_loop_candidate_set"
    assert postsolve["held_stage_iii_replay_candidate_count"] == postsolve["held_stage_ii_replay_candidate_count"]
    assert postsolve["selected_candidate_count"] == 3
    assert postsolve["phase_distance"] > 0.0
