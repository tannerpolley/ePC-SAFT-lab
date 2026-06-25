from __future__ import annotations

import argparse
import json
import math
import os
import sys
from pathlib import Path
from typing import Any

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = REPO_ROOT / "packages" / "epcsaft" / "src"
EQUILIBRIUM_SRC_ROOT = REPO_ROOT / "packages" / "epcsaft-equilibrium" / "src"
for import_root in (REPO_ROOT, SRC_ROOT, EQUILIBRIUM_SRC_ROOT):
    import_path = str(import_root)
    if import_path not in sys.path:
        sys.path.insert(0, import_path)

from scripts.validation import check_electrolyte_gfpe_gate
from scripts.validation import check_electrolyte_tpd_gate

ALGORITHM_SCOPE = "held2_counterion_pair_phase_discovery_only"
CHARGE_TOLERANCE = check_electrolyte_tpd_gate.CHARGE_TOLERANCE
TPD_TOLERANCE = check_electrolyte_tpd_gate.TPD_TOLERANCE
CANDIDATE_MASS_BALANCE_TOLERANCE = check_electrolyte_tpd_gate.CANDIDATE_MASS_BALANCE_TOLERANCE
NATIVE_SPECIES = check_electrolyte_tpd_gate.NATIVE_SPECIES
CHARGE_VECTOR = check_electrolyte_tpd_gate.CHARGE_VECTOR.astype(float)
RANK_TOLERANCE = 1.0e-10
ROUND_TRIP_TOLERANCE = 1.0e-8
ASCANI_PAPER_PATH = (
    REPO_ROOT
    / "docs"
    / "papers"
    / "md"
    / "Equilibrium"
    / "Ascani, Sadowski, Held - 2022 - Calculation of Multiphase Equilibria Containing Mixed Solvents and M.md"
)
ASCANI_TABLE5_PATH = REPO_ROOT / "analyses" / "paper_validation" / "2022_ascani" / "tables" / "table_005" / "table_005.md"


def _jsonable(value: Any) -> Any:
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    return value


def _matrix_rank(matrix: list[list[float]], tolerance: float = RANK_TOLERANCE) -> int:
    if not matrix:
        return 0
    return int(np.linalg.matrix_rank(np.asarray(matrix, dtype=float), tol=tolerance))


def _ordered_by_feed(indices: list[int], feed: list[float]) -> list[int]:
    return sorted(indices, key=lambda index: (-float(feed[index]), index))


def _active_position(charged_indices: list[int], species_index: int) -> int:
    try:
        return charged_indices.index(species_index)
    except ValueError as exc:
        raise ValueError("counterion pair references a species outside the charged set") from exc


def _build_counterion_pairs(
    *,
    species_labels: list[str],
    feed_composition: list[float],
    charges: list[float],
    rank_tolerance: float = RANK_TOLERANCE,
) -> dict[str, Any]:
    if not (len(species_labels) == len(feed_composition) == len(charges)):
        raise ValueError("species labels, feed composition, and charge vector must have the same length")
    charged_indices = [
        index
        for index, (feed, charge) in enumerate(zip(feed_composition, charges, strict=True))
        if abs(float(charge)) > rank_tolerance and float(feed) > 1.0e-12
    ]
    cation_indices = [index for index in charged_indices if charges[index] > 0.0]
    anion_indices = [index for index in charged_indices if charges[index] < 0.0]
    if not cation_indices or not anion_indices:
        raise ValueError("active cation and anion species are required")

    ordered_cations = _ordered_by_feed(cation_indices, feed_composition)
    ordered_anions = _ordered_by_feed(anion_indices, feed_composition)
    matrix: list[list[float]] = []
    pair_labels: list[str] = []

    def append_pair(cation: int, anion: int) -> None:
        row = [0.0 for _ in charged_indices]
        row[_active_position(charged_indices, cation)] = 1.0 / abs(float(charges[cation]))
        row[_active_position(charged_indices, anion)] = 1.0 / abs(float(charges[anion]))
        matrix.append(row)
        pair_labels.append(f"{species_labels[cation]}/{species_labels[anion]}")

    if len(ordered_cations) <= len(ordered_anions):
        pivot_cation = ordered_cations[0]
        for anion in ordered_anions:
            append_pair(pivot_cation, anion)
        for ordinal, cation in enumerate(ordered_cations[1:]):
            append_pair(cation, ordered_anions[ordinal])
    else:
        pivot_anion = ordered_anions[0]
        for cation in ordered_cations:
            append_pair(cation, pivot_anion)
        for ordinal, anion in enumerate(ordered_anions[1:]):
            append_pair(ordered_cations[ordinal], anion)

    expected_rank = len(charged_indices) - 1
    lift_matrix: list[list[float]] = []
    for charged_row in matrix:
        full_row = [0.0 for _ in species_labels]
        for local_index, global_index in enumerate(charged_indices):
            full_row[global_index] = charged_row[local_index]
        lift_matrix.append(full_row)
    return {
        "charged_species_labels": [species_labels[index] for index in charged_indices],
        "active_charged_species_indices": charged_indices,
        "cation_indices": cation_indices,
        "anion_indices": anion_indices,
        "charged_feed_ordering": sorted(charged_indices, key=lambda index: (-float(feed_composition[index]), index)),
        "pair_labels": pair_labels,
        "matrix": matrix,
        "row_sums": [float(sum(row)) for row in matrix],
        "rank": _matrix_rank(matrix, rank_tolerance),
        "expected_rank": expected_rank,
        "rank_tolerance": rank_tolerance,
        "transformed_variable_count": len(matrix),
        "lift_matrix": lift_matrix,
    }


def build_counterion_pair_fixture(
    *,
    fixture_id: str,
    species_labels: list[str],
    feed_composition: list[float],
    charges: list[float],
    source_path: str | Path,
    source_notes: str = "",
) -> dict[str, Any]:
    pairs = _build_counterion_pairs(
        species_labels=species_labels,
        feed_composition=feed_composition,
        charges=charges,
    )
    return _jsonable(
        {
            "algorithm_scope": ALGORITHM_SCOPE,
            "feed_composition": feed_composition,
            "charge_vector": charges,
            "charged_species": {
                "species_labels": species_labels,
                "charged_species_labels": pairs["charged_species_labels"],
                "charge_vector": charges,
                "active_charged_species_indices": pairs["active_charged_species_indices"],
                "cation_indices": pairs["cation_indices"],
                "anion_indices": pairs["anion_indices"],
                "charged_feed_ordering": pairs["charged_feed_ordering"],
            },
            "counterion_pairs": {
                "pair_labels": pairs["pair_labels"],
                "charged_species_labels": pairs["charged_species_labels"],
                "matrix": pairs["matrix"],
                "row_sums": pairs["row_sums"],
                "rank": pairs["rank"],
                "expected_rank": pairs["expected_rank"],
                "rank_tolerance": pairs["rank_tolerance"],
                "transformed_variable_count": pairs["transformed_variable_count"],
            },
            "electroneutral_lift": {
                "basis_label": "counterion_pair_transformed_variables",
                "lift_matrix": pairs["lift_matrix"],
                "round_trip_tolerance": ROUND_TRIP_TOLERANCE,
            },
            "source_fixtures": {
                "fixture_id": fixture_id,
                "source_path": str(source_path),
                "source_notes": source_notes,
            },
        }
    )


def ascani_table5_common_anion_fixture() -> dict[str, Any]:
    return build_counterion_pair_fixture(
        fixture_id="ascani_2022_table5_water_butanol_nacl_kcl",
        species_labels=["water", "1-butanol", "Na+", "K+", "Cl-"],
        feed_composition=[0.8094, 0.1728, 0.0054, 0.0124, 0.0178],
        charges=[0.0, 0.0, 1.0, 1.0, -1.0],
        source_path=ASCANI_TABLE5_PATH,
        source_notes="Table 5 source context: water + 1-butanol + NaCl + KCl at 298.15 K and 1 bar.",
    ) | {
        "source_fixtures": {
            "fixture_id": "ascani_2022_table5_water_butanol_nacl_kcl",
            "source_path": str(ASCANI_TABLE5_PATH),
            "component_set": ["water", "1-butanol", "NaCl", "KCl"],
            "temperature_K": 298.15,
            "pressure_bar": 1.0,
            "feed_basis": "mass_fraction_salt_basis_source_context",
            "feed": {"water": 0.8094, "1-butanol": 0.1728, "NaCl": 0.0054, "KCl": 0.0124},
            "mean_ionic_pair_labels": ["Na+/Cl-", "K+/Cl-"],
        }
    }


def ascani_multivalent_preprocessor_fixture() -> dict[str, Any]:
    return build_counterion_pair_fixture(
        fixture_id="ascani_2022_multivalent_counterion_preprocessor_example",
        species_labels=["water", "1-butanol", "K+", "Cl-", "Na+", "SO4--"],
        feed_composition=[0.310, 0.310, 0.085, 0.085, 0.140, 0.070],
        charges=[0.0, 0.0, 1.0, -1.0, 1.0, -2.0],
        source_path=ASCANI_PAPER_PATH,
        source_notes="Section 3.1 counterion-pair preprocessing example.",
    ) | {
        "source_fixtures": {
            "fixture_id": "ascani_2022_multivalent_counterion_preprocessor_example",
            "source_path": str(ASCANI_PAPER_PATH),
            "component_set": ["water", "1-butanol", "KCl", "Na2SO4"],
            "feed_basis": "single_ion_mole_fraction",
            "charged_species_order": ["K+", "Cl-", "Na+", "SO4--"],
            "methodology_pair_labels": ["Na+/Cl-", "Na+/SO4--", "K+/Cl-"],
        }
    }


def evaluate_reduced_lift_samples(
    fixture: dict[str, Any],
    *,
    samples: list[list[float]],
) -> dict[str, Any]:
    feed = np.asarray(fixture["feed_composition"], dtype=float)
    charges = np.asarray(fixture["charge_vector"], dtype=float)
    lift_matrix = np.asarray(fixture["electroneutral_lift"]["lift_matrix"], dtype=float)
    charged_indices = [int(index) for index in fixture["charged_species"]["active_charged_species_indices"]]
    counterion_matrix = np.asarray(fixture["counterion_pairs"]["matrix"], dtype=float)
    neutral_indices = [index for index, charge in enumerate(charges) if abs(charge) <= RANK_TOLERANCE]
    lifted: list[list[float]] = []
    reduced_coordinates: list[list[float]] = []
    round_trip_residual = 0.0
    max_charge = 0.0
    max_sum = 0.0
    min_component = math.inf
    normal = counterion_matrix @ counterion_matrix.T
    for sample in samples:
        xi = np.asarray(sample, dtype=float)
        if xi.shape[0] != lift_matrix.shape[0]:
            raise ValueError("sample coordinate dimension does not match the counterion-pair matrix")
        composition = feed + xi @ lift_matrix
        sum_offset = float(composition.sum() - 1.0)
        if abs(sum_offset) > 0.0:
            if not neutral_indices:
                raise ValueError("reduced lift sample requires at least one neutral component to keep composition closed")
            composition[neutral_indices[0]] -= sum_offset
        delta_charged = composition[charged_indices] - feed[charged_indices]
        recovered = np.linalg.solve(normal, counterion_matrix @ delta_charged)
        round_trip_residual = max(round_trip_residual, float(np.max(np.abs(recovered - xi))))
        max_charge = max(max_charge, abs(float(composition @ charges)))
        max_sum = max(max_sum, abs(float(composition.sum() - 1.0)))
        min_component = min(min_component, float(np.min(composition)))
        lifted.append(composition.tolist())
        reduced_coordinates.append(recovered.tolist())
    return _jsonable(
        {
            "basis_label": "counterion_pair_transformed_variables",
            "lifted_candidate_compositions": lifted,
            "reduced_candidate_coordinates": reduced_coordinates,
            "max_charge_residual": max_charge,
            "component_nonnegativity_margin": min_component if math.isfinite(min_component) else 0.0,
            "composition_sum_residual": max_sum,
            "round_trip_residual": round_trip_residual,
            "round_trip_tolerance": ROUND_TRIP_TOLERANCE,
        }
    )


def _native_held2_payload(case_dir: Path, checker_command: list[str] | None) -> dict[str, Any]:
    from scripts.dev.native_runtime_env import apply_native_runtime_env

    apply_native_runtime_env(os.environ)
    from epcsaft_equilibrium._native import extension_native_core
    from scripts.validation import native_freshness

    mixture, feed, temperature, pressure = check_electrolyte_tpd_gate._khudaida_mixture_and_feed(case_dir)
    core = extension_native_core()
    discovery = core._native_electrolyte_held2_phase_discovery(
        mixture._native,
        temperature,
        pressure,
        feed.tolist(),
        CHARGE_VECTOR.tolist(),
        NATIVE_SPECIES,
        [0, 0],
        CHARGE_TOLERANCE,
        TPD_TOLERANCE,
        CANDIDATE_MASS_BALANCE_TOLERANCE,
    )
    discovery = dict(discovery)
    blockers: list[str] = []
    if discovery.get("algorithm_scope") != ALGORITHM_SCOPE:
        blockers.append("held2_algorithm_scope_mismatch")
    pairs = discovery.get("counterion_pairs", {})
    if int(pairs.get("rank", 0)) != int(pairs.get("expected_rank", -1)):
        blockers.append("held2_counterion_pair_matrix_rank_incomplete")
    if int(pairs.get("transformed_variable_count", 0)) != int(pairs.get("expected_rank", -1)):
        blockers.append("held2_transformed_dimension_mismatch")
    lift = discovery.get("electroneutral_lift", {})
    if float(lift.get("max_charge_residual", math.inf)) > CHARGE_TOLERANCE:
        blockers.append("held2_lift_charge_residual_exceeds_threshold")
    if float(lift.get("composition_sum_residual", math.inf)) > CANDIDATE_MASS_BALANCE_TOLERANCE:
        blockers.append("held2_lift_composition_sum_residual_exceeds_threshold")
    if float(lift.get("round_trip_residual", math.inf)) > ROUND_TRIP_TOLERANCE:
        blockers.append("held2_lift_round_trip_residual_exceeds_threshold")
    reduced_tpd = discovery.get("reduced_tpd", {})
    if reduced_tpd.get("coordinate_basis") != "counterion_pair_transformed_variables":
        blockers.append("held2_reduced_tpd_basis_mismatch")
    if int(reduced_tpd.get("selected_candidate_count", 0)) <= 0:
        blockers.append("held2_selected_candidates_missing")
    if not math.isfinite(float(reduced_tpd.get("minimum_tpd", math.inf))):
        blockers.append("held2_minimum_tpd_not_finite")
    mean_ionic = discovery.get("mean_ionic_residuals", {})
    if mean_ionic.get("status") != "bookkeeping_only_until_stage_iii":
        blockers.append("held2_mean_ionic_status_mismatch")
    if not mean_ionic.get("pair_labels"):
        blockers.append("held2_mean_ionic_pair_labels_missing")
    if "raw_single_ion_residuals" in mean_ionic:
        blockers.append("held2_raw_single_ion_residuals_present")
    if not math.isfinite(float(mean_ionic.get("maximum_absolute_residual", math.inf))):
        blockers.append("held2_mean_ionic_residual_not_finite")
    stages = discovery.get("stage_statuses", {})
    if stages.get("phase_discovery") != "complete":
        blockers.append("held2_phase_discovery_status_incomplete")
    if stages.get("stage_iii_refinement") == "complete":
        blockers.append("stage_iii_claimed_complete_by_phase_discovery_gate")
    if stages.get("postsolve_certification") == "complete":
        blockers.append("postsolve_claimed_complete_by_phase_discovery_gate")
    if stages.get("public_route_admission") != "separate_public_admission_gate":
        blockers.append("public_route_admission_opened_by_phase_discovery_gate")

    receipt = native_freshness.build_receipt(
        native_module=core,
        checker_command=checker_command
        or [
            "uv",
            "run",
            "--no-sync",
            "python",
            "scripts/validation/check_electrolyte_held2_phase_discovery.py",
            "--json",
            "--require-complete",
        ],
    )
    discovery["native_binding"] = "_native_electrolyte_held2_phase_discovery"
    discovery["native_freshness_receipt"] = native_freshness.receipt_to_jsonable(receipt)
    discovery["blockers"] = blockers
    discovery["status"] = "complete" if not blockers else "incomplete"
    return _jsonable(discovery)


def _source_fixtures_payload() -> dict[str, Any]:
    khudaida_fixture = {
        "fixture_id": "khudaida_2026_water_ethanol_isobutanol_nacl",
        "source_path": str(check_electrolyte_gfpe_gate.DEFAULT_CASE_DIR),
        "component_set": ["water", "ethanol", "isobutanol", "NaCl"],
        "native_species": NATIVE_SPECIES,
        "mean_ionic_pair_labels": ["Na+/Cl-"],
    }
    return {
        "khudaida_nacl": khudaida_fixture,
        "ascani_2022_table5": ascani_table5_common_anion_fixture()["source_fixtures"],
        "ascani_2022_multivalent_preprocessor": ascani_multivalent_preprocessor_fixture()["source_fixtures"],
    }


def _source_gates_payload(
    source_gate: dict[str, Any],
    readiness_gate: dict[str, Any],
    tpd_gate: dict[str, Any],
) -> dict[str, Any]:
    return {
        "khudaida_2026_source_gate_complete": source_gate.get("complete") is True,
        "held2_readiness_gate_complete": readiness_gate.get("complete") is True,
        "electrolyte_tpd_gate_complete": tpd_gate.get("complete") is True,
    }


def evaluate_payload(
    payload: dict[str, Any],
    *,
    require_source_gate: bool = False,
    require_readiness_gate: bool = False,
    require_tpd_gate: bool = False,
    require_native_held2_discovery: bool = False,
    require_public_routes_closed: bool = False,
) -> dict[str, Any]:
    blockers = list(payload.get("blockers", []))

    source_gate = payload.get("source_gate", {})
    if require_source_gate:
        if source_gate.get("complete") is not True:
            blockers.append("electrolyte_source_gate_incomplete")
        blockers.extend(str(item) for item in source_gate.get("blockers", []))

    readiness = payload.get("held2_readiness_gate", {})
    if require_readiness_gate:
        if readiness.get("complete") is not True:
            blockers.append("electrolyte_held2_readiness_gate_incomplete")
        blockers.extend(str(item) for item in readiness.get("blockers", []))

    tpd_gate = payload.get("electrolyte_tpd_gate", {})
    if require_tpd_gate:
        if tpd_gate.get("complete") is not True:
            blockers.append("electrolyte_tpd_gate_incomplete")
        blockers.extend(str(item) for item in tpd_gate.get("blockers", []))
        tpd = tpd_gate.get("electrolyte_tpd", {})
        if tpd.get("status") != "charge_neutral_tpd_screening_complete":
            blockers.append("electrolyte_tpd_native_gate_incomplete")

    held2 = payload.get("held2_phase_discovery", {})
    if require_native_held2_discovery:
        if held2.get("status") != "complete":
            blockers.append("held2_phase_discovery_incomplete")
        blockers.extend(str(item) for item in held2.get("blockers", []))
        if held2.get("algorithm_scope") != ALGORITHM_SCOPE:
            blockers.append("held2_algorithm_scope_mismatch")
        source_gates = held2.get("source_gates", {})
        for key in (
            "khudaida_2026_source_gate_complete",
            "held2_readiness_gate_complete",
            "electrolyte_tpd_gate_complete",
        ):
            if source_gates.get(key) is not True:
                blockers.append(f"held2_source_gate_missing:{key}")
        charged_species = held2.get("charged_species", {})
        if not charged_species.get("active_charged_species_indices"):
            blockers.append("held2_charged_species_missing")
        pairs = held2.get("counterion_pairs", {})
        if int(pairs.get("rank", 0)) != int(pairs.get("expected_rank", -1)):
            blockers.append("held2_counterion_pair_matrix_rank_incomplete")
        if int(pairs.get("transformed_variable_count", 0)) != int(pairs.get("expected_rank", -1)):
            blockers.append("held2_transformed_dimension_mismatch")
        if len(pairs.get("pair_labels", [])) != int(pairs.get("expected_rank", -1)):
            blockers.append("held2_counterion_pair_label_count_mismatch")
        lift = held2.get("electroneutral_lift", {})
        if float(lift.get("max_charge_residual", math.inf)) > CHARGE_TOLERANCE:
            blockers.append("held2_lift_charge_residual_exceeds_threshold")
        if float(lift.get("component_nonnegativity_margin", -math.inf)) < -1.0e-12:
            blockers.append("held2_lift_component_negative")
        if float(lift.get("composition_sum_residual", math.inf)) > CANDIDATE_MASS_BALANCE_TOLERANCE:
            blockers.append("held2_lift_composition_sum_residual_exceeds_threshold")
        if float(lift.get("round_trip_residual", math.inf)) > ROUND_TRIP_TOLERANCE:
            blockers.append("held2_lift_round_trip_residual_exceeds_threshold")
        reduced = held2.get("reduced_tpd", {})
        if reduced.get("coordinate_basis") != "counterion_pair_transformed_variables":
            blockers.append("held2_reduced_tpd_basis_mismatch")
        if int(reduced.get("selected_candidate_count", 0)) <= 0:
            blockers.append("held2_selected_candidates_missing")
        if not math.isfinite(float(reduced.get("minimum_tpd", math.inf))):
            blockers.append("held2_minimum_tpd_not_finite")
        for metric in ("duplicate_candidate_distance", "candidate_to_feed_distance"):
            if not math.isfinite(float(reduced.get(metric, math.inf))):
                blockers.append(f"held2_{metric}_not_finite")
        mean_ionic = held2.get("mean_ionic_residuals", {})
        if mean_ionic.get("status") != "bookkeeping_only_until_stage_iii":
            blockers.append("held2_mean_ionic_status_mismatch")
        if not mean_ionic.get("pair_labels"):
            blockers.append("held2_mean_ionic_pair_labels_missing")
        if "raw_single_ion_residuals" in mean_ionic:
            blockers.append("held2_raw_single_ion_residuals_present")
        if not math.isfinite(float(mean_ionic.get("maximum_absolute_residual", math.inf))):
            blockers.append("held2_mean_ionic_residual_not_finite")
        stages = held2.get("stage_statuses", {})
        if stages.get("phase_discovery") != "complete":
            blockers.append("held2_phase_discovery_status_incomplete")
        if stages.get("stage_iii_refinement") == "complete":
            blockers.append("stage_iii_claimed_complete_by_phase_discovery_gate")
        if stages.get("postsolve_certification") == "complete":
            blockers.append("postsolve_claimed_complete_by_phase_discovery_gate")
        if stages.get("public_route_admission") != "separate_public_admission_gate":
            blockers.append("public_route_admission_opened_by_phase_discovery_gate")
        handoff = held2.get("stage_iii_handoff", {})
        if handoff.get("status") != "pending_stage_iii_refinement":
            blockers.append("stage_iii_handoff_status_mismatch")
        source_fixtures = held2.get("source_fixtures", {})
        if "khudaida_nacl" not in source_fixtures:
            blockers.append("khudaida_source_fixture_missing")
        if "ascani_2022_table5" not in source_fixtures:
            blockers.append("ascani_table5_source_fixture_missing")
        if "ascani_2022_multivalent_preprocessor" not in source_fixtures:
            blockers.append("ascani_multivalent_source_fixture_missing")

    public_state = payload.get("public_route_state", {})
    electrolyte = public_state.get("electrolyte_lle", {})
    if require_public_routes_closed:
        if electrolyte.get("present") is not True:
            blockers.append("electrolyte_lle_activation_row_missing")
        if electrolyte.get("production_exposed") is True:
            blockers.append("electrolyte_lle_public_route_exposed")
        if electrolyte.get("public_routes"):
            blockers.append("electrolyte_lle_public_route_exposed")
        if electrolyte.get("proof_routes"):
            blockers.append("electrolyte_lle_proof_route_exposed")
        if "electrolyte_lle" in public_state.get("capabilities_public_routes", []):
            blockers.append("electrolyte_lle_capability_public_route_exposed")
        if "electrolyte_lle" in public_state.get("production_families", []):
            blockers.append("electrolyte_lle_production_family_exposed")

    result = dict(payload)
    result["blockers"] = sorted(set(blockers))
    result["complete"] = not result["blockers"]
    return _jsonable(result)


def evaluate_held2_phase_discovery(
    case_dir: Path = check_electrolyte_gfpe_gate.DEFAULT_CASE_DIR,
    *,
    require_source_gate: bool = False,
    require_readiness_gate: bool = False,
    require_tpd_gate: bool = False,
    require_native_held2_discovery: bool = False,
    require_public_routes_closed: bool = False,
    checker_command: list[str] | None = None,
) -> dict[str, Any]:
    case_dir = Path(case_dir)
    tpd_gate = check_electrolyte_tpd_gate.evaluate_tpd_gate(
        case_dir,
        require_source_gate=True,
        require_held2_readiness=True,
        require_native_tpd=True,
        require_public_routes_closed=require_public_routes_closed,
        checker_command=checker_command,
    )
    source_gate = tpd_gate.get("source_gate", {})
    readiness_gate = tpd_gate.get("held2_readiness_gate", {})
    public_state = tpd_gate.get("public_route_state", {})
    try:
        held2 = _native_held2_payload(case_dir, checker_command)
    except Exception as exc:
        held2 = {
            "status": "failed",
            "blockers": [f"held2_phase_discovery_native_receipt_failed:{exc}"],
            "algorithm_scope": ALGORITHM_SCOPE,
        }
    held2["source_gates"] = _source_gates_payload(source_gate, readiness_gate, tpd_gate)
    held2["source_fixtures"] = _source_fixtures_payload()
    payload = {
        "checker": "electrolyte_held2_counterion_pair_phase_discovery_gate",
        "case_label": "Khudaida 2026 electrolyte LLE plus Ascani 2022 counterion-pair fixtures",
        "source_gate": source_gate,
        "held2_readiness_gate": readiness_gate,
        "electrolyte_tpd_gate": tpd_gate,
        "held2_phase_discovery": held2,
        "public_route_state": public_state,
    }
    return evaluate_payload(
        payload,
        require_source_gate=require_source_gate,
        require_readiness_gate=require_readiness_gate,
        require_tpd_gate=require_tpd_gate,
        require_native_held2_discovery=require_native_held2_discovery,
        require_public_routes_closed=require_public_routes_closed,
    )


def minimal_complete_payload_for_tests() -> dict[str, Any]:
    source_gate = {"complete": True, "blockers": []}
    readiness_gate = {"complete": True, "blockers": []}
    tpd_gate = {
        "complete": True,
        "blockers": [],
        "electrolyte_tpd": {"status": "charge_neutral_tpd_screening_complete"},
    }
    source_gates = _source_gates_payload(source_gate, readiness_gate, tpd_gate)
    fixture = build_counterion_pair_fixture(
        fixture_id="unit_single_salt_nacl",
        species_labels=["H2O", "Na+", "Cl-"],
        feed_composition=[0.98, 0.01, 0.01],
        charges=[0.0, 1.0, -1.0],
        source_path="unit-test",
    )
    held2 = {
        "status": "complete",
        "blockers": [],
        "algorithm_scope": ALGORITHM_SCOPE,
        "source_gates": source_gates,
        "charged_species": fixture["charged_species"],
        "counterion_pairs": fixture["counterion_pairs"],
        "electroneutral_lift": {
            "basis_label": "counterion_pair_transformed_variables",
            "lift_matrix": fixture["electroneutral_lift"]["lift_matrix"],
            "lifted_candidate_compositions": [[0.98, 0.01, 0.01]],
            "reduced_candidate_coordinates": [[0.0]],
            "max_charge_residual": 0.0,
            "component_nonnegativity_margin": 0.01,
            "composition_sum_residual": 0.0,
            "round_trip_residual": 0.0,
            "round_trip_tolerance": ROUND_TRIP_TOLERANCE,
        },
        "reduced_tpd": {
            "coordinate_basis": "counterion_pair_transformed_variables",
            "reduced_start_count": 1,
            "converged_start_count": 1,
            "selected_candidate_count": 1,
            "minimum_tpd": -1.0e-3,
            "duplicate_candidate_distance": 0.0,
            "candidate_to_feed_distance": 0.0,
        },
        "mean_ionic_residuals": {
            "pair_labels": ["Na+/Cl-"],
            "residual_values": [0.0],
            "residual_scale": 1.0,
            "maximum_absolute_residual": 0.0,
            "status": "bookkeeping_only_until_stage_iii",
        },
        "stage_statuses": {
            "phase_discovery": "complete",
            "stage_iii_refinement": "pending",
            "postsolve_certification": "pending",
            "public_route_admission": "separate_public_admission_gate",
        },
        "stage_iii_handoff": {
            "status": "pending_stage_iii_refinement",
            "phase_fractions": [1.0],
            "phase_kinds": [0],
            "explicit_ion_phase_compositions": [[0.98, 0.01, 0.01]],
            "reduced_candidate_coordinates": [[0.0]],
            "counterion_pair_matrix": [[1.0, 1.0]],
            "mean_ionic_pair_labels": ["Na+/Cl-"],
            "tpd_values": [-1.0e-3],
        },
        "source_fixtures": _source_fixtures_payload(),
    }
    public_state = {
        "electrolyte_lle": {
            "present": True,
            "production_exposed": False,
            "public_routes": [],
            "proof_routes": [],
        },
        "capabilities_public_routes": [],
        "production_families": [],
    }
    return {
        "checker": "electrolyte_held2_counterion_pair_phase_discovery_gate",
        "source_gate": source_gate,
        "held2_readiness_gate": readiness_gate,
        "electrolyte_tpd_gate": tpd_gate,
        "held2_phase_discovery": held2,
        "public_route_state": public_state,
        "blockers": [],
        "complete": True,
    }


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--case-dir", type=Path, default=check_electrolyte_gfpe_gate.DEFAULT_CASE_DIR)
    parser.add_argument("--require-source-gate", action="store_true")
    parser.add_argument("--require-readiness-gate", action="store_true")
    parser.add_argument("--require-tpd-gate", action="store_true")
    parser.add_argument("--require-native-held2-discovery", action="store_true")
    parser.add_argument("--require-public-routes-closed", action="store_true")
    parser.add_argument("--require-complete", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    from scripts.dev.native_runtime_env import apply_native_runtime_env

    apply_native_runtime_env(os.environ)
    args = build_arg_parser().parse_args(argv)
    checker_command = sys.argv[:] if argv is None else [
        "uv",
        "run",
        "--no-sync",
        "python",
        "scripts/validation/check_electrolyte_held2_phase_discovery.py",
        *argv,
    ]
    output = evaluate_held2_phase_discovery(
        args.case_dir,
        require_source_gate=args.require_source_gate or args.require_complete,
        require_readiness_gate=args.require_readiness_gate or args.require_complete,
        require_tpd_gate=args.require_tpd_gate or args.require_complete,
        require_native_held2_discovery=args.require_native_held2_discovery or args.require_complete,
        require_public_routes_closed=args.require_public_routes_closed,
        checker_command=checker_command,
    )
    if args.require_complete:
        receipt = output.get("held2_phase_discovery", {}).get("native_freshness_receipt", {})
        if receipt:
            from scripts.validation import native_freshness

            try:
                native_freshness.require_receipt(dict(receipt))
            except ValueError as exc:
                print(str(exc), file=sys.stderr)
                return 2
    if args.json:
        print(json.dumps(output, indent=2, sort_keys=True))
    else:
        print(f"complete={output['complete']} blockers={','.join(output['blockers'])}")
    if args.require_complete and not output["complete"]:
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
