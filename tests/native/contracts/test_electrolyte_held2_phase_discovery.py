from __future__ import annotations

import copy
import importlib.util
import json
import math
import subprocess
import sys
from pathlib import Path
from typing import Any

from epcsaft_equilibrium._native import extension_native_core

REPO_ROOT = Path(__file__).resolve().parents[3]
CHECKER_PATH = REPO_ROOT / "scripts" / "validation" / "check_electrolyte_held2_phase_discovery.py"


def _load_checker() -> Any:
    assert CHECKER_PATH.is_file(), f"missing checker: {CHECKER_PATH.relative_to(REPO_ROOT)}"
    spec = importlib.util.spec_from_file_location("check_electrolyte_held2_phase_discovery", CHECKER_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_native_electrolyte_held2_phase_discovery_binding_is_exposed() -> None:
    core = extension_native_core()

    assert hasattr(core, "_native_electrolyte_held2_phase_discovery")


def test_counterion_pair_matrix_rank_single_salt() -> None:
    checker = _load_checker()

    fixture = checker.build_counterion_pair_fixture(
        fixture_id="unit_single_salt_nacl",
        species_labels=["H2O", "Na+", "Cl-"],
        feed_composition=[0.98, 0.01, 0.01],
        charges=[0.0, 1.0, -1.0],
        source_path="unit-test",
    )

    pairs = fixture["counterion_pairs"]
    assert pairs["pair_labels"] == ["Na+/Cl-"]
    assert pairs["matrix"] == [[1.0, 1.0]]
    assert pairs["rank"] == 1
    assert pairs["expected_rank"] == 1
    assert pairs["transformed_variable_count"] == 1


def test_counterion_pair_matrix_rank_common_anion() -> None:
    checker = _load_checker()

    fixture = checker.ascani_table5_common_anion_fixture()

    pairs = fixture["counterion_pairs"]
    assert set(pairs["pair_labels"]) == {"Na+/Cl-", "K+/Cl-"}
    assert pairs["rank"] == 2
    assert pairs["expected_rank"] == 2
    assert pairs["transformed_variable_count"] == 2
    assert fixture["source_fixtures"]["fixture_id"] == "ascani_2022_table5_water_butanol_nacl_kcl"


def test_counterion_pair_matrix_multivalent_source_example() -> None:
    checker = _load_checker()

    fixture = checker.ascani_multivalent_preprocessor_fixture()

    pairs = fixture["counterion_pairs"]
    assert pairs["charged_species_labels"] == ["K+", "Cl-", "Na+", "SO4--"]
    assert pairs["pair_labels"] == ["Na+/Cl-", "Na+/SO4--", "K+/Cl-"]
    assert pairs["matrix"] == [
        [0.0, 1.0, 1.0, 0.0],
        [0.0, 0.0, 1.0, 0.5],
        [1.0, 1.0, 0.0, 0.0],
    ]
    assert pairs["rank"] == 3
    assert pairs["expected_rank"] == 3


def test_reduced_lift_keeps_charge_zero() -> None:
    checker = _load_checker()
    fixture = checker.ascani_multivalent_preprocessor_fixture()

    lift = checker.evaluate_reduced_lift_samples(
        fixture,
        samples=[
            [0.0001, -0.00005, 0.00003],
            [-0.0002, 0.00004, 0.00001],
            [0.0, 0.00003, -0.00003],
        ],
    )

    assert lift["max_charge_residual"] <= 1.0e-10
    assert lift["composition_sum_residual"] <= 1.0e-10
    assert lift["component_nonnegativity_margin"] >= 0.0


def test_reduced_lift_round_trip_is_stable() -> None:
    checker = _load_checker()
    fixture = checker.ascani_multivalent_preprocessor_fixture()

    lift = checker.evaluate_reduced_lift_samples(
        fixture,
        samples=[
            [0.0001, -0.00005, 0.00003],
            [-0.0002, 0.00004, 0.00001],
        ],
    )

    assert lift["round_trip_residual"] <= lift["round_trip_tolerance"]


def test_mean_ionic_rows_are_pair_based() -> None:
    checker = _load_checker()

    payload = checker.evaluate_held2_phase_discovery(
        require_source_gate=True,
        require_readiness_gate=True,
        require_tpd_gate=True,
        require_native_held2_discovery=True,
    )

    residuals = payload["held2_phase_discovery"]["mean_ionic_residuals"]
    assert residuals["status"] == "bookkeeping_only_until_stage_iii"
    assert residuals["pair_labels"]
    assert "raw_single_ion_residuals" not in residuals
    assert all("/" in label for label in residuals["pair_labels"])
    assert math.isfinite(float(residuals["maximum_absolute_residual"]))


def test_phase_discovery_payload_rejects_stage_iii_claims() -> None:
    checker = _load_checker()
    payload = checker.minimal_complete_payload_for_tests()
    mutated = copy.deepcopy(payload)
    mutated["held2_phase_discovery"]["stage_statuses"]["stage_iii_refinement"] = "complete"

    result = checker.evaluate_payload(
        mutated,
        require_source_gate=True,
        require_readiness_gate=True,
        require_tpd_gate=True,
        require_native_held2_discovery=True,
        require_public_routes_closed=True,
    )

    assert result["complete"] is False
    assert "stage_iii_claimed_complete_by_phase_discovery_gate" in result["blockers"]


def test_checker_consumes_prerequisite_gates() -> None:
    checker = _load_checker()
    payload = checker.minimal_complete_payload_for_tests()
    mutated = copy.deepcopy(payload)
    mutated["source_gate"]["complete"] = False
    mutated["held2_readiness_gate"]["complete"] = False
    mutated["electrolyte_tpd_gate"]["complete"] = False

    result = checker.evaluate_payload(
        mutated,
        require_source_gate=True,
        require_readiness_gate=True,
        require_tpd_gate=True,
        require_native_held2_discovery=True,
        require_public_routes_closed=True,
    )

    assert result["complete"] is False
    assert "electrolyte_source_gate_incomplete" in result["blockers"]
    assert "electrolyte_held2_readiness_gate_incomplete" in result["blockers"]
    assert "electrolyte_tpd_gate_incomplete" in result["blockers"]


def test_phase_discovery_defers_public_admission_to_separate_gate() -> None:
    checker = _load_checker()

    payload = checker.evaluate_held2_phase_discovery(
        require_source_gate=True,
        require_readiness_gate=True,
        require_tpd_gate=True,
        require_native_held2_discovery=True,
    )

    assert payload["public_route_state"]["electrolyte_lle"]["production_exposed"] is True
    assert payload["public_route_state"]["electrolyte_lle"]["public_routes"] == ["electrolyte_lle"]
    assert (
        payload["held2_phase_discovery"]["stage_statuses"]["public_route_admission"]
        == "separate_public_admission_gate"
    )


def test_ascani_2022_table5_fixture_loaded() -> None:
    checker = _load_checker()

    fixture = checker.ascani_table5_common_anion_fixture()

    source = fixture["source_fixtures"]
    assert source["component_set"] == ["water", "1-butanol", "NaCl", "KCl"]
    assert source["temperature_K"] == 298.15
    assert source["pressure_bar"] == 1.0
    assert source["mean_ionic_pair_labels"] == ["Na+/Cl-", "K+/Cl-"]
    assert Path(source["source_path"]).is_file()


def test_cli_requires_complete_electrolyte_held2_phase_discovery() -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(CHECKER_PATH),
            "--json",
            "--require-source-gate",
            "--require-readiness-gate",
            "--require-tpd-gate",
            "--require-native-held2-discovery",
            "--require-complete",
        ],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["complete"] is True
    assert payload["blockers"] == []
