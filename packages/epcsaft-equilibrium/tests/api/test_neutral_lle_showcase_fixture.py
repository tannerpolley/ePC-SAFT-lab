from __future__ import annotations

import csv
import itertools
import json
from pathlib import Path
from typing import Any

import numpy as np
import pytest

import epcsaft
import epcsaft_equilibrium as equilibrium_module
from epcsaft_equilibrium._native import extension_native_core

_core = extension_native_core()

REPO_ROOT = Path(__file__).resolve().parents[4]
CASE_DIR = (
    REPO_ROOT
    / "data"
    / "reference"
    / "equilibrium_benchmarks"
    / "neutral_lle"
    / "matsuda_2011_pfhexane_hexane"
)


def test_equilibrium_lle_solves_source_backed_neutral_showcase_fixture() -> None:
    _skip_without_ipopt()
    metadata = _read_json(CASE_DIR / "metadata.json")
    thresholds = _read_json(CASE_DIR / "thresholds.json")
    feed = _single_row(CASE_DIR / "feed_compositions.csv")
    source = _single_row(CASE_DIR / "experimental_tielines.csv")

    mixture = epcsaft.Mixture(_parameter_set(metadata["species"]))
    result = equilibrium_module.Equilibrium(
        mixture,
        route="lle",
        T=float(feed["temperature_K"]),
        P=float(feed["pressure_Pa"]),
        z=[float(feed["z1"]), float(feed["z2"])],
    ).solve(
        solver_options={
            "max_iterations": int(thresholds["solver_max_iterations"]),
            "tolerance": float(thresholds["solver_tolerance"]),
            "ipopt_iteration_history_limit": 8,
            "ipopt_acceptable_tolerance": float(thresholds["acceptable_tolerance"]),
            "ipopt_constraint_violation_tolerance": float(thresholds["constraint_violation_tolerance"]),
            "ipopt_dual_infeasibility_tolerance": float(thresholds["dual_infeasibility_tolerance"]),
            "ipopt_complementarity_tolerance": float(thresholds["complementarity_tolerance"]),
        }
    )

    assert result.problem_kind == "neutral_lle"
    assert result.route == "lle"
    assert result.selector_route == "neutral_lle"
    assert result.phase_labels == ["liquid1", "liquid2"]
    assert result.diagnostics["route_status"] == "production_accepted"
    assert result.diagnostics["solver_status"] == "success"
    assert result.diagnostics["application_status"] == "solve_succeeded"
    assert result.diagnostics["hessian_approximation"] == "exact"
    assert result.diagnostics["exact_hessian_available"] is True
    assert result.diagnostics["eval_h_calls"] > 0

    evidence = result.diagnostics["physical_evidence"]
    assert evidence["phase_discovery_backend"] == "continuous_tpd_held_dual_phase_discovery"
    assert evidence["held_stage_ii_status"] == "dual_loop_verified"
    assert evidence["held_stage_ii_dual_loop_status"] == "verified"
    assert evidence["held_stage_ii_replay_ready"] is True
    assert evidence["held_stage_iii_status"] == "ipopt_refinement_completed_current_route"
    assert evidence["held_stage_iii_consumed_stage_ii_replay_metadata"] is True

    actual_compositions = [result.phase_compositions[label].tolist() for label in result.phase_labels]
    actual_fractions = [result.phase_fractions[label] for label in result.phase_labels]
    expected_compositions = {
        "liquid1": [float(source["liquid1_x1"]), float(source["liquid1_x2"])],
        "liquid2": [float(source["liquid2_x1"]), float(source["liquid2_x2"])],
    }
    expected_fractions = {
        "liquid1": float(feed["liquid1_phase_fraction"]),
        "liquid2": float(feed["liquid2_phase_fraction"]),
    }
    comparison = _best_phase_match(
        actual_compositions,
        actual_fractions,
        expected_compositions,
        expected_fractions,
    )
    assert comparison["max_composition_abs_error"] <= thresholds["composition_abs"]
    assert comparison["max_phase_fraction_abs_error"] <= thresholds["phase_fraction_abs"]


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _read_csv(path: Path) -> list[dict[str, str]]:
    return list(csv.DictReader(path.read_text(encoding="utf-8").splitlines()))


def _single_row(path: Path) -> dict[str, str]:
    rows = _read_csv(path)
    assert len(rows) == 1
    return rows[0]


def _parameter_set(species: list[str]) -> epcsaft.ParameterSet:
    pure_by_species = {row["species"]: row for row in _read_csv(CASE_DIR / "pure_component_parameters.csv")}
    index = {name: position for position, name in enumerate(species)}
    k_ij = np.zeros((len(species), len(species)), dtype=float)
    for row in _read_csv(CASE_DIR / "binary_interactions.csv"):
        i = index[row["component_i"]]
        j = index[row["component_j"]]
        value = float(row["k_ij"])
        k_ij[i, j] = value
        k_ij[j, i] = value
    return epcsaft.ParameterSet.from_dict(
        {
            "m": np.asarray([float(pure_by_species[name]["m"]) for name in species], dtype=float),
            "s": np.asarray([float(pure_by_species[name]["s_A"]) for name in species], dtype=float),
            "e": np.asarray([float(pure_by_species[name]["e_over_k_K"]) for name in species], dtype=float),
            "MW": np.asarray(
                [float(pure_by_species[name]["molecular_weight_g_per_mol"]) / 1000.0 for name in species],
                dtype=float,
            ),
            "k_ij": k_ij,
        },
        species=species,
    )


def _best_phase_match(
    actual_compositions: list[list[float]],
    actual_fractions: list[float],
    expected_compositions: dict[str, list[float]],
    expected_fractions: dict[str, float],
) -> dict[str, float]:
    labels = list(expected_compositions)
    best: dict[str, float] | None = None
    for permutation in itertools.permutations(range(len(actual_compositions)), len(labels)):
        composition_errors = []
        fraction_errors = []
        for label, actual_index in zip(labels, permutation, strict=True):
            expected = expected_compositions[label]
            actual = actual_compositions[actual_index]
            composition_errors.append(max(abs(left - right) for left, right in zip(expected, actual, strict=True)))
            fraction_errors.append(abs(expected_fractions[label] - actual_fractions[actual_index]))
        candidate = {
            "max_composition_abs_error": max(composition_errors),
            "max_phase_fraction_abs_error": max(fraction_errors),
        }
        if best is None or (
            candidate["max_composition_abs_error"] + candidate["max_phase_fraction_abs_error"]
            < best["max_composition_abs_error"] + best["max_phase_fraction_abs_error"]
        ):
            best = candidate
    assert best is not None
    return best


def _skip_without_ipopt() -> None:
    if not _core._native_ipopt_smoke()["compiled"]:
        pytest.skip("native Ipopt is not compiled")
