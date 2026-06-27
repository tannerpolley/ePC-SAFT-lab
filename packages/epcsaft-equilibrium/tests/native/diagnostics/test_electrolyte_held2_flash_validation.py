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
