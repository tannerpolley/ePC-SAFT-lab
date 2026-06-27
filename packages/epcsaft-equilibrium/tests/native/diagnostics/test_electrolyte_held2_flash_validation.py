from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

import epcsaft
from epcsaft_equilibrium import _native_core as core

REPO_ROOT = Path(__file__).resolve().parents[5]
FIGIEL_PARAMETERS = REPO_ROOT / "analyses" / "paper_validation" / "2025_figiel" / "parameters"
SPECIES = ["Methanol", "H2O", "Li+", "Cl-"]
CHARGES = [0.0, 0.0, 1.0, -1.0]
TEMPERATURE_K = 351.25
PRESSURE_PA = 101_325.0


def _perdomo_table4_liquid_feed() -> list[float]:
    # Perdomo et al. 2025 Table 4 reports compositions as Li+, Cl-, methanol, water.
    liquid = np.array([0.29880, 0.61277, 0.044213, 0.044213], dtype=float)
    return (liquid / liquid.sum()).tolist()


def _assert_figiel_parameter_snapshot() -> None:
    options = json.loads((FIGIEL_PARAMETERS / "user_options.json").read_text(encoding="utf-8"))
    elec_model = options["elec_model"]
    born_model = elec_model["born_model"]

    assert (FIGIEL_PARAMETERS / "pure" / "any_solvent.csv").is_file()
    assert (FIGIEL_PARAMETERS / "mixed" / "binary_interaction" / "k_ij.csv").is_file()
    assert (FIGIEL_PARAMETERS / "mixed" / "rel_perm" / "parameters.csv").is_file()
    assert elec_model["differential_mode"] == "autodiff"
    assert elec_model["relative_permittivity_rule"] == "empirical"
    assert born_model["enabled"] is True
    assert born_model["solvation_shell_model"] is True
    assert born_model["dielectric_saturation"] is True


def test_electrolyte_held2_flash_uses_figiel_parameters_and_records_single_phase_blocker() -> None:
    _assert_figiel_parameter_snapshot()
    feed = _perdomo_table4_liquid_feed()
    mixture = epcsaft.Mixture.from_folder(
        FIGIEL_PARAMETERS,
        components=SPECIES,
        reference_temperature=TEMPERATURE_K,
        reference_composition=feed,
    )

    result = core._native_electrolyte_stage_iii_refinement(
        mixture.native._native,
        TEMPERATURE_K,
        PRESSURE_PA,
        feed,
        CHARGES,
        SPECIES,
        [0, 1],
        1.0e-10,
        1.0e-8,
        1.0e-8,
        1.0e-4,
        1.0e-8,
        1.0e-8,
    )

    route = result["native_stage_iii_route_result"]
    solver = result["solver_diagnostics"]
    residual_system = result["reduced_residual_system"]
    derivatives = result["derivative_receipts"]
    discovery = result["held2_phase_discovery"]["tpd_discovery"]
    candidates = discovery["candidates"]
    trace_ion_candidates = [
        candidate
        for candidate in candidates
        if candidate["composition"][2] <= 1.0e-9 and candidate["composition"][3] <= 1.0e-9
    ]

    assert result["status"] == "incomplete"
    assert route["status"] == "postsolve_rejected"
    assert route["rejection_reason"] == "phase_distance"
    assert solver["solver_status"] == "success"
    assert solver["application_status"] == "solve_succeeded"
    assert solver["solver_accepted"] is True
    assert solver["route_accepted"] is False
    assert discovery["tpd_candidate_count"] >= 30
    assert any(candidate["phase_kind"] == 1 for candidate in trace_ion_candidates)
    assert all(candidate["tpd"] > 0.0 for candidate in trace_ion_candidates)

    assert route["initial_point_strategy"] == "electrolyte_held2_candidate_set_replay"
    assert route["problem_name"] == "electrolyte_stage_iii_projected_residual_refinement"
    assert route["hessian_approximation"] == "exact"
    assert str(route["hessian_backend"]).startswith("cppad_phase_system_projected_electrolyte")
    assert derivatives["route_hessian_approximation"] == "exact"
    assert derivatives["exact_reduced_hessian_available"] is True
    assert derivatives["born_ssm_ds_active_block_exact_hessian"] is True

    assert residual_system["equation_labels"] == [
        "pair_mean_ionic_equality:Li+/Cl-",
        "phase_fraction_closure",
        "phase_charge_balance:phase_0",
        "phase_charge_balance:phase_1",
    ]
    assert max(abs(value) for value in residual_system["residual_values"]) <= 1.0e-4
    assert solver["charge_balance_norm"] <= 1.0e-10
    assert solver["pressure_consistency_norm"] <= 1.0e-2
    assert solver["phase_distance"] < solver["phase_distance_tolerance"]

    first, second = solver["phase_compositions"]
    assert np.max(np.abs(np.array(first) - np.array(second))) == pytest.approx(
        solver["phase_distance"],
        rel=0.0,
        abs=1.0e-12,
    )


def test_electrolyte_held2_flash_bubble_temperature_route_accepts_figiel_boundary() -> None:
    _assert_figiel_parameter_snapshot()
    feed = _perdomo_table4_liquid_feed()
    mixture = epcsaft.Mixture.from_folder(
        FIGIEL_PARAMETERS,
        components=SPECIES,
        reference_temperature=TEMPERATURE_K,
        reference_composition=feed,
    )

    route = core._native_electrolyte_bubble_t_route_result(
        mixture.native._native,
        PRESSURE_PA,
        feed,
        CHARGES,
        80,
        1.0e-8,
        30.0,
        "exact",
        3,
        1.0e-8,
        1.0e-2,
        1.0e-10,
        1.0e-6,
        1.0e-8,
        None,
        bound_push=1.0e-10,
        bound_frac=1.0e-10,
    )

    assert route["route"] == "electrolyte_bubble_temperature"
    assert route["route_refinement_kind"] == "charge_constrained_projected_residual_temperature_boundary"
    assert route["problem_name"] == "electrolyte_bubble_t_eos"
    assert route["hessian_approximation"] == "exact"
    assert route["hessian_backend"] == "cppad_phase_temperature_reduced_residual_constraints"
    assert route["variable_model"] == "reduced_electroneutral_logit_amount_volume_temperature"
    assert route["exact_hessian_available"] is True
    assert route["residual_derivative_backend"] == "cppad_phase_temperature_reduced_residual_constraints"
    assert route["residual_exact_jacobian_available"] is True
    assert route["residual_exact_hessian_available"] is True
    assert route["public_route_admission"] == "focused_validation_binding"
    assert route["production_exposed"] is False
    assert route["last_callback_exception"] == ""

    assert route["status"] == "accepted"
    assert route["solver_status"] == "success"
    assert route["application_status"] == "solve_succeeded"
    assert route["accepted"] is True
    assert route["solver_accepted"] is True
    assert route["seed_name"] == "canonical_phase_density_root"
    assert route["iteration_count"] <= 12

    variables = np.asarray(route["variables"], dtype=float)
    species_count = len(SPECIES)
    liquid = variables[:species_count]
    liquid_volume = float(variables[species_count])
    vapor = variables[species_count + 1 : 2 * species_count + 1]
    vapor_volume = float(variables[2 * species_count + 1])
    temperature = float(variables[-1])

    liquid_block = core._native_eos_phase_block(
        mixture.native._native,
        temperature,
        PRESSURE_PA,
        liquid.tolist(),
        liquid_volume,
    )
    vapor_block = core._native_eos_phase_block(
        mixture.native._native,
        temperature,
        PRESSURE_PA,
        vapor.tolist(),
        vapor_volume,
    )
    pressure_scale = 1.0 / max(1.0, 1.0e-3 * PRESSURE_PA)
    projected_residuals = np.array(
        [
            pressure_scale * liquid_block["pressure_consistency_residual"],
            pressure_scale * vapor_block["pressure_consistency_residual"],
            liquid_block["gradient"][0] - vapor_block["gradient"][0],
            liquid_block["gradient"][1] - vapor_block["gradient"][1],
            liquid_block["gradient"][2]
            + liquid_block["gradient"][3]
            - vapor_block["gradient"][2]
            - vapor_block["gradient"][3],
        ],
        dtype=float,
    )

    assert liquid.tolist() == pytest.approx(feed, rel=0.0, abs=1.0e-12)
    assert np.sum(vapor) == pytest.approx(1.0, rel=0.0, abs=1.0e-7)
    assert float(np.dot(vapor, CHARGES)) == pytest.approx(0.0, rel=0.0, abs=1.0e-12)
    assert route["objective"] == pytest.approx(0.0, rel=0.0, abs=0.0)
    assert np.max(np.abs(projected_residuals)) <= 1.0e-6
    assert temperature == pytest.approx(351.90223321057, rel=0.0, abs=1.0e-7)
    assert vapor.tolist() == pytest.approx(
        [0.59580640799008, 0.32808099776732, 0.03805629712130, 0.03805629712130],
        rel=0.0,
        abs=1.0e-10,
    )

    probe = core._native_electrolyte_bubble_t_reduced_nlp_probe(
        mixture.native._native,
        PRESSURE_PA,
        feed,
        CHARGES,
        variables.tolist(),
        1.0e-10,
    )
    assert probe["problem_name"] == "electrolyte_bubble_t_eos"
    assert probe["hessian_backend"] == "cppad_phase_temperature_reduced_residual_constraints"
    assert probe["variable_model"] == "reduced_electroneutral_logit_amount_volume_temperature"
    assert probe["variable_count"] == 5
    assert probe["constraints"] == pytest.approx(projected_residuals.tolist(), rel=0.0, abs=1.0e-9)
    assert np.all(np.isfinite(np.asarray(probe["jacobian_values"], dtype=float)))
    assert np.all(np.isfinite(np.asarray(probe["hessian_values"], dtype=float)))
