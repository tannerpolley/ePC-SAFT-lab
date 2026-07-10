from __future__ import annotations

import argparse
import json
import math
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

from scripts.validation import (
    check_electrolyte_held2_phase_discovery,
    check_electrolyte_held2_stage_i,
    check_electrolyte_tpd_gate,
)

ALGORITHM_SCOPE = "held2_stage_ii_electrolyte_dual_phase_discovery_only"
CHARGE_TOLERANCE = check_electrolyte_tpd_gate.CHARGE_TOLERANCE
CANDIDATE_MASS_BALANCE_TOLERANCE = check_electrolyte_tpd_gate.CANDIDATE_MASS_BALANCE_TOLERANCE
ROUND_TRIP_TOLERANCE = check_electrolyte_held2_phase_discovery.ROUND_TRIP_TOLERANCE
STAGE_II_BOUND_TOLERANCE = check_electrolyte_tpd_gate.TPD_TOLERANCE


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


def _finite_float(value: Any, default: float = math.inf) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _charge_vector(held2: dict[str, Any]) -> list[float]:
    charged_species = held2.get("charged_species", {})
    return [float(value) for value in charged_species.get("charge_vector", [])]


def _charge_residual(composition: list[float], charges: list[float]) -> float:
    if len(composition) != len(charges):
        return math.inf
    return abs(float(np.asarray(composition, dtype=float) @ np.asarray(charges, dtype=float)))


def _composition_sum_residual(composition: list[float]) -> float:
    return abs(float(sum(composition) - 1.0))


def _domain_margin(composition: list[float]) -> float:
    return min((float(value) for value in composition), default=-math.inf)


def _stage_i_evidence(stage_i_payload: dict[str, Any]) -> dict[str, Any]:
    return dict(stage_i_payload.get("electrolyte_held2_stage_i", {}))


def _candidate_bounds(tpd_discovery: dict[str, Any]) -> dict[str, Any]:
    return {
        "major_iterations": int(tpd_discovery.get("held_stage_ii_major_iterations", 0)),
        "candidate_count": int(tpd_discovery.get("held_stage_ii_candidate_count", 0)),
        "selected_candidate_count": int(tpd_discovery.get("selected_candidate_count", 0)),
        "lower_bound": _finite_float(tpd_discovery.get("held_stage_ii_lower_bound")),
        "upper_bound": _finite_float(tpd_discovery.get("held_stage_ii_upper_bound")),
        "bound_gap": _finite_float(tpd_discovery.get("held_stage_ii_bound_gap")),
        "bound_tolerance": _finite_float(tpd_discovery.get("held_stage_ii_bound_tolerance")),
        "lower_bound_history": [
            _finite_float(value) for value in tpd_discovery.get("held_stage_ii_lower_bound_history", [])
        ],
        "upper_bound_history": [
            _finite_float(value) for value in tpd_discovery.get("held_stage_ii_upper_bound_history", [])
        ],
        "bound_gap_history": [
            _finite_float(value) for value in tpd_discovery.get("held_stage_ii_bound_gap_history", [])
        ],
    }


def _replay_payload(tpd_discovery: dict[str, Any], charges: list[float]) -> dict[str, Any]:
    phase_compositions = [
        [float(value) for value in composition]
        for composition in tpd_discovery.get("held_stage_ii_replay_phase_compositions", [])
    ]
    charge_residuals = [_charge_residual(composition, charges) for composition in phase_compositions]
    composition_residuals = [_composition_sum_residual(composition) for composition in phase_compositions]
    return {
        "status": "replayable" if tpd_discovery.get("held_stage_ii_replay_ready") is True else "incomplete",
        "replay_ready": tpd_discovery.get("held_stage_ii_replay_ready") is True,
        "source": str(tpd_discovery.get("held_stage_ii_replay_source", "")),
        "seed_name": str(tpd_discovery.get("held_stage_ii_replay_seed_name", "")),
        "native_candidate_count": int(tpd_discovery.get("held_stage_ii_replay_candidate_count", 0)),
        "candidate_count": len(phase_compositions),
        "candidate_ranks": [
            int(value) for value in tpd_discovery.get("held_stage_ii_replay_candidate_ranks", [])
        ],
        "phase_fractions": [
            float(value) for value in tpd_discovery.get("held_stage_ii_replay_phase_fractions", [])
        ],
        "phase_kinds": [
            int(value) for value in tpd_discovery.get("held_stage_ii_replay_phase_kinds", [])
        ],
        "phase_compositions": phase_compositions,
        "max_charge_residual": max(charge_residuals, default=math.inf),
        "max_composition_sum_residual": max(composition_residuals, default=math.inf),
        "stage_iii_status": str(tpd_discovery.get("held_stage_iii_status", "")),
    }


def _candidate_by_rank(tpd_discovery: dict[str, Any]) -> dict[int, dict[str, Any]]:
    out: dict[int, dict[str, Any]] = {}
    for candidate in tpd_discovery.get("candidates", []):
        record = dict(candidate)
        out[int(record.get("candidate_rank", -1))] = record
    return out


def _rejected_candidate_records(tpd_discovery: dict[str, Any], charges: list[float]) -> list[dict[str, Any]]:
    by_rank = _candidate_by_rank(tpd_discovery)
    ranks = [int(value) for value in tpd_discovery.get("held_stage_ii_rejected_candidate_ranks", [])]
    reasons = [str(value) for value in tpd_discovery.get("held_stage_ii_rejected_candidate_reasons", [])]
    records: list[dict[str, Any]] = []
    for index, rank in enumerate(ranks):
        candidate = by_rank.get(rank, {})
        composition = [float(value) for value in candidate.get("composition", [])]
        records.append(
            {
                "candidate_rank": rank,
                "source": str(candidate.get("source", "")),
                "phase_kind": int(candidate.get("phase_kind", -1)),
                "selected": bool(candidate.get("selected", False)),
                "reason": reasons[index] if index < len(reasons) else "stage_ii_rejected_candidate",
                "feasibility_status": str(candidate.get("feasibility_status", "")),
                "tpd": _finite_float(candidate.get("tpd")),
                "tpd_status": str(candidate.get("tpd_status", "")),
                "composition": composition,
                "charge_residual": _charge_residual(composition, charges),
                "composition_sum_residual": _composition_sum_residual(composition),
                "domain_margin": _domain_margin(composition),
            }
        )
    return records


def _neutral_only_coverage() -> dict[str, Any]:
    composition = [0.55, 0.45]
    return {
        "status": "covered",
        "basis_label": "neutral_mole_fraction_simplex",
        "source": "neutral-only Stage II selector contracts",
        "active_charge_rank": 0,
        "expected_rank": 0,
        "max_charge_residual": 0.0,
        "composition_sum_residual": _composition_sum_residual(composition),
        "round_trip_residual": 0.0,
        "component_nonnegativity_margin": _domain_margin(composition),
    }


def _single_salt_coverage(held2: dict[str, Any], charges: list[float]) -> dict[str, Any]:
    lift = dict(held2.get("electroneutral_lift", {}))
    pairs = dict(held2.get("counterion_pairs", {}))
    charged_species = dict(held2.get("charged_species", {}))
    active_count = len(charged_species.get("active_charged_species_indices", []))
    return {
        "status": "covered",
        "basis_label": lift.get("basis_label", "counterion_pair_transformed_variables"),
        "source": "khudaida_2026_single_salt_nacl_native_route",
        "active_charge_rank": active_count - 1 if active_count else 0,
        "expected_rank": int(pairs.get("expected_rank", 0)),
        "matrix_rank": int(pairs.get("rank", 0)),
        "max_charge_residual": _finite_float(lift.get("max_charge_residual")),
        "composition_sum_residual": _finite_float(lift.get("composition_sum_residual")),
        "round_trip_residual": _finite_float(lift.get("round_trip_residual")),
        "component_nonnegativity_margin": _finite_float(lift.get("component_nonnegativity_margin"), -math.inf),
        "charge_vector": charges,
    }


def _fixture_coverage(label: str, fixture: dict[str, Any], samples: list[list[float]]) -> dict[str, Any]:
    lift = check_electrolyte_held2_phase_discovery.evaluate_reduced_lift_samples(
        fixture,
        samples=samples,
    )
    pairs = fixture["counterion_pairs"]
    return {
        "status": "covered",
        "basis_label": lift["basis_label"],
        "source": fixture["source_fixtures"]["fixture_id"],
        "coverage_label": label,
        "active_charge_rank": int(pairs["expected_rank"]),
        "expected_rank": int(pairs["expected_rank"]),
        "matrix_rank": int(pairs["rank"]),
        "max_charge_residual": _finite_float(lift["max_charge_residual"]),
        "composition_sum_residual": _finite_float(lift["composition_sum_residual"]),
        "round_trip_residual": _finite_float(lift["round_trip_residual"]),
        "component_nonnegativity_margin": _finite_float(lift["component_nonnegativity_margin"], -math.inf),
    }


def _basis_coverage(held2: dict[str, Any], charges: list[float]) -> dict[str, Any]:
    common_ion = check_electrolyte_held2_phase_discovery.ascani_table5_common_anion_fixture()
    mixed_salt = check_electrolyte_held2_phase_discovery.ascani_multivalent_preprocessor_fixture()
    return {
        "neutral_only": _neutral_only_coverage(),
        "single_salt": _single_salt_coverage(held2, charges),
        "common_ion": _fixture_coverage(
            "common_ion",
            common_ion,
            samples=[[1.0e-4, -5.0e-5], [-1.0e-4, 5.0e-5]],
        ),
        "mixed_salt": _fixture_coverage(
            "mixed_salt",
            mixed_salt,
            samples=[[1.0e-4, -5.0e-5, 2.5e-5], [-1.0e-4, 5.0e-5, -2.5e-5]],
        ),
    }


def _coverage_blockers(coverage: dict[str, Any]) -> list[str]:
    blockers: list[str] = []
    for key, evidence in coverage.items():
        if evidence.get("status") != "covered":
            blockers.append(f"stage_ii_basis_{key}_missing")
        if int(evidence.get("matrix_rank", evidence.get("active_charge_rank", 0))) != int(
            evidence.get("expected_rank", evidence.get("active_charge_rank", 0))
        ):
            blockers.append(f"stage_ii_basis_{key}_rank_incomplete")
        if _finite_float(evidence.get("max_charge_residual")) > CHARGE_TOLERANCE:
            blockers.append(f"stage_ii_basis_{key}_charge_residual")
        if _finite_float(evidence.get("composition_sum_residual")) > CANDIDATE_MASS_BALANCE_TOLERANCE:
            blockers.append(f"stage_ii_basis_{key}_composition_residual")
        if _finite_float(evidence.get("round_trip_residual")) > ROUND_TRIP_TOLERANCE:
            blockers.append(f"stage_ii_basis_{key}_round_trip_residual")
        if _finite_float(evidence.get("component_nonnegativity_margin"), -math.inf) < -1.0e-12:
            blockers.append(f"stage_ii_basis_{key}_domain_margin")
    return blockers


def _build_stage_ii_evidence(
    held2: dict[str, Any],
    stage_i_payload: dict[str, Any],
) -> dict[str, Any]:
    stage_i = _stage_i_evidence(stage_i_payload)
    tpd_discovery = dict(held2.get("tpd_discovery", {}))
    charges = _charge_vector(held2)
    bounds = _candidate_bounds(tpd_discovery)
    replay = _replay_payload(tpd_discovery, charges)
    rejected = _rejected_candidate_records(tpd_discovery, charges)
    coverage = _basis_coverage(held2, charges)
    stage_i_status = "consumed" if str(tpd_discovery.get("held_stage_i_status", "")).endswith("_consumed") else "pending"
    return {
        "algorithm_scope": ALGORITHM_SCOPE,
        "native_binding": held2.get("native_binding", "_native_electrolyte_held2_phase_discovery"),
        "phase_discovery_backend": tpd_discovery.get("phase_discovery_backend"),
        "stability_certificate": tpd_discovery.get("stability_certificate"),
        "stage_i_certificate": {
            "status": stage_i_status,
            "native_status": tpd_discovery.get("held_stage_i_status"),
            "stage_i_classification": stage_i.get("stage_i_classification"),
            "minimum_tpd": stage_i.get("continuous_tpd_min"),
            "negative_tpd_found": stage_i.get("negative_tpd_found"),
            "handoff_status": stage_i.get("stage_ii_handoff", {}).get("status"),
        },
        "stage_ii_status": tpd_discovery.get("held_stage_ii_status"),
        "candidate_bound_audit_status": tpd_discovery.get("held_stage_ii_candidate_bound_audit_status"),
        "dual_loop_status": tpd_discovery.get("held_stage_ii_dual_loop_status"),
        "stopping_reason": tpd_discovery.get("held_stage_ii_stopping_reason"),
        "candidate_bounds": bounds,
        "replay_payload": replay,
        "rejected_candidate_count": len(rejected),
        "native_rejected_candidate_count": int(tpd_discovery.get("held_stage_ii_rejected_candidate_count", 0)),
        "rejected_candidates": rejected,
        "reduced_basis_coverage": coverage,
        "stage_iii_refinement_status": tpd_discovery.get("held_stage_iii_status"),
        "public_route_admission_status": "separate_public_admission_gate",
        "native_freshness_receipt": held2.get("native_freshness_receipt", {}),
    }


def _stage_ii_blockers(
    evidence: dict[str, Any],
    stage_i_payload: dict[str, Any],
    upstream_blockers: list[str],
    *,
    require_stage_i: bool,
    require_bound_gap: bool,
    require_replay: bool,
    require_complete: bool,
) -> list[str]:
    blockers = list(upstream_blockers)
    stage_i = evidence["stage_i_certificate"]
    bounds = evidence["candidate_bounds"]
    replay = evidence["replay_payload"]
    if require_stage_i or require_complete:
        if stage_i_payload.get("complete") is not True:
            blockers.append("stage_i_certificate_incomplete")
        blockers.extend(str(item) for item in stage_i_payload.get("blockers", []))
        if stage_i.get("stage_i_classification") != "unstable_negative_tpd":
            blockers.append("stage_i_negative_tpd_certificate_missing")
        if stage_i.get("status") != "consumed":
            blockers.append("stage_i_certificate_not_consumed")
    if evidence.get("stage_ii_status") != "dual_loop_verified":
        blockers.append("stage_ii_dual_loop_incomplete")
    if evidence.get("candidate_bound_audit_status") != "candidate_bound_gap_closed":
        blockers.append("stage_ii_bound_gap_open")
    if evidence.get("dual_loop_status") != "verified":
        blockers.append("stage_ii_dual_loop_unverified")
    if require_bound_gap or require_complete:
        if not math.isfinite(bounds["bound_gap"]):
            blockers.append("stage_ii_bound_gap_nonfinite")
        if bounds["bound_gap"] > bounds["bound_tolerance"]:
            blockers.append("stage_ii_bound_gap_open")
        if bounds["bound_tolerance"] > STAGE_II_BOUND_TOLERANCE:
            blockers.append("stage_ii_bound_tolerance_too_loose")
        if bounds["major_iterations"] <= 0:
            blockers.append("stage_ii_bound_history_missing")
        if len(bounds["lower_bound_history"]) != bounds["major_iterations"]:
            blockers.append("stage_ii_lower_bound_history_mismatch")
        if len(bounds["upper_bound_history"]) != bounds["major_iterations"]:
            blockers.append("stage_ii_upper_bound_history_mismatch")
        if len(bounds["bound_gap_history"]) != bounds["major_iterations"]:
            blockers.append("stage_ii_gap_history_mismatch")
    if require_replay or require_complete:
        if replay["status"] != "replayable" or replay["replay_ready"] is not True:
            blockers.append("stage_ii_replay_payload_missing")
        if replay["candidate_count"] <= 0:
            blockers.append("stage_ii_replay_payload_missing")
        if replay["candidate_count"] != len(replay["phase_fractions"]):
            blockers.append("stage_ii_replay_fraction_count_mismatch")
        if replay["candidate_count"] != len(replay["phase_kinds"]):
            blockers.append("stage_ii_replay_phase_kind_count_mismatch")
        if replay["max_charge_residual"] > CHARGE_TOLERANCE:
            blockers.append("stage_ii_replay_charge_residual")
        if replay["max_composition_sum_residual"] > CANDIDATE_MASS_BALANCE_TOLERANCE:
            blockers.append("stage_ii_replay_composition_residual")
    if evidence.get("rejected_candidate_count", 0) <= 0:
        blockers.append("stage_ii_rejected_candidate_records_missing")
    for record in evidence.get("rejected_candidates", []):
        if not record.get("reason"):
            blockers.append("stage_ii_rejected_candidate_reason_missing")
        if _finite_float(record.get("charge_residual")) > CHARGE_TOLERANCE:
            blockers.append("stage_ii_rejected_candidate_charge_residual")
        if _finite_float(record.get("composition_sum_residual")) > CANDIDATE_MASS_BALANCE_TOLERANCE:
            blockers.append("stage_ii_rejected_candidate_composition_residual")
        if _finite_float(record.get("domain_margin"), -math.inf) <= 0.0:
            blockers.append("stage_ii_rejected_candidate_domain_margin")
    blockers.extend(_coverage_blockers(evidence["reduced_basis_coverage"]))
    if evidence.get("stage_iii_refinement_status") == "complete":
        blockers.append("stage_iii_claimed_complete_by_stage_ii_gate")
    if evidence.get("public_route_admission_status") != "separate_public_admission_gate":
        blockers.append("public_route_opened_by_stage_ii_gate")
    return sorted(set(blockers))


def evaluate_stage_ii_payload(
    phase_payload: dict[str, Any],
    *,
    stage_i_payload: dict[str, Any],
    require_stage_i: bool = False,
    require_bound_gap: bool = False,
    require_replay: bool = False,
    require_complete: bool = False,
) -> dict[str, Any]:
    held2 = dict(phase_payload.get("held2_phase_discovery", {}))
    evidence = _build_stage_ii_evidence(held2, stage_i_payload)
    upstream_blockers = [str(item) for item in phase_payload.get("blockers", [])]
    upstream_blockers.extend(str(item) for item in held2.get("blockers", []))
    blockers = _stage_ii_blockers(
        evidence,
        stage_i_payload,
        upstream_blockers,
        require_stage_i=require_stage_i,
        require_bound_gap=require_bound_gap,
        require_replay=require_replay,
        require_complete=require_complete,
    )
    return _jsonable(
        {
            "checker": "electrolyte_held2_stage_ii_dual_phase_discovery",
            "complete": not blockers,
            "blockers": blockers,
            "source_gate": phase_payload.get("source_gate", {}),
            "held2_readiness_gate": phase_payload.get("held2_readiness_gate", {}),
            "electrolyte_tpd_gate": phase_payload.get("electrolyte_tpd_gate", {}),
            "held2_phase_discovery": held2,
            "electrolyte_held2_stage_i": _stage_i_evidence(stage_i_payload),
            "electrolyte_held2_stage_ii": evidence,
        }
    )


def evaluate_stage_ii(
    *,
    require_stage_i: bool = False,
    require_bound_gap: bool = False,
    require_replay: bool = False,
    require_complete: bool = False,
    checker_command: list[str] | None = None,
) -> dict[str, Any]:
    command = checker_command or [
        "uv",
        "run",
        "--no-sync",
        "python",
        "scripts/validation/check_electrolyte_held2_stage_ii.py",
        "--json",
    ]
    stage_i_payload = check_electrolyte_held2_stage_i.evaluate_stage_i(
        require_continuous_tpd=require_stage_i or require_complete,
        require_complete=require_stage_i or require_complete,
        checker_command=command,
    )
    phase_payload = check_electrolyte_held2_phase_discovery.evaluate_held2_phase_discovery(
        require_source_gate=True,
        require_readiness_gate=True,
        require_tpd_gate=True,
        require_native_held2_discovery=True,
        require_public_routes_closed=False,
        checker_command=command,
    )
    return evaluate_stage_ii_payload(
        phase_payload,
        stage_i_payload=stage_i_payload,
        require_stage_i=require_stage_i,
        require_bound_gap=require_bound_gap,
        require_replay=require_replay,
        require_complete=require_complete,
    )


def minimal_stage_i_payload_for_tests() -> dict[str, Any]:
    evidence = {
        "stage_i_classification": "unstable_negative_tpd",
        "certificate_status": "complete",
        "negative_tpd_found": True,
        "continuous_tpd_min": -1.0e-3,
        "stage_ii_handoff": {"status": "ready_for_stage_ii_discovery"},
    }
    return {
        "checker": "electrolyte_held2_stage_i",
        "complete": True,
        "blockers": [],
        "electrolyte_held2_stage_i": evidence,
    }


def minimal_complete_payload_for_tests() -> dict[str, Any]:
    payload = check_electrolyte_held2_phase_discovery.minimal_complete_payload_for_tests()
    held2 = dict(payload["held2_phase_discovery"])
    held2["native_binding"] = "_native_electrolyte_held2_phase_discovery"
    held2["charged_species"] = {
        "species_labels": ["H2O", "Na+", "Cl-"],
        "charged_species_labels": ["Na+", "Cl-"],
        "charge_vector": [0.0, 1.0, -1.0],
        "active_charged_species_indices": [1, 2],
        "cation_indices": [1],
        "anion_indices": [2],
    }
    selected_a = [0.98, 0.01, 0.01]
    selected_b = [0.96, 0.02, 0.02]
    rejected = [0.97, 0.015, 0.015]
    tpd_discovery = {
        "phase_discovery_backend": "continuous_reduced_electroneutral_held2_stage_ii_dual_phase_discovery",
        "stability_certificate": "electrolyte_held2_stage_ii_dual_phase_discovery",
        "held_stage_i_status": "stage_i_negative_tpd_certificate_consumed",
        "held_stage_ii_status": "dual_loop_verified",
        "held_stage_ii_candidate_bound_audit_status": "candidate_bound_gap_closed",
        "held_stage_ii_dual_loop_status": "verified",
        "held_stage_ii_major_iterations": 1,
        "held_stage_ii_candidate_count": 3,
        "held_stage_ii_lower_bound": -1.0e-3,
        "held_stage_ii_upper_bound": -1.0e-3,
        "held_stage_ii_bound_gap": 0.0,
        "held_stage_ii_bound_tolerance": STAGE_II_BOUND_TOLERANCE,
        "held_stage_ii_stopping_reason": "bound_gap_closed",
        "held_stage_ii_lower_bound_history": [-1.0e-3],
        "held_stage_ii_upper_bound_history": [-1.0e-3],
        "held_stage_ii_bound_gap_history": [0.0],
        "held_stage_ii_replay_ready": True,
        "held_stage_ii_replay_source": "stage_ii_dual_loop_selected_candidates",
        "held_stage_ii_replay_seed_name": "held_stage_ii_dual_loop_candidate_pair",
        "held_stage_ii_replay_candidate_count": 3,
        "held_stage_ii_replay_candidate_ranks": [0, 1],
        "held_stage_ii_replay_phase_fractions": [0.5, 0.5],
        "held_stage_ii_replay_phase_kinds": [0, 0],
        "held_stage_ii_replay_phase_compositions": [selected_a, selected_b],
        "held_stage_ii_rejected_candidate_count": 1,
        "held_stage_ii_rejected_candidate_ranks": [2],
        "held_stage_ii_rejected_candidate_reasons": ["not_selected_by_dual_loop_mass_balance_gate"],
        "held_stage_iii_status": "pending_ipopt_refinement",
        "selected_candidate_count": 2,
        "candidates": [
            {
                "candidate_rank": 0,
                "selected": True,
                "source": "unit_selected_a",
                "phase_kind": 0,
                "composition": selected_a,
                "tpd": -1.0e-3,
                "tpd_status": "converged",
                "feasibility_status": "selected_mass_balance_feasible",
            },
            {
                "candidate_rank": 1,
                "selected": True,
                "source": "unit_selected_b",
                "phase_kind": 0,
                "composition": selected_b,
                "tpd": 2.0e-4,
                "tpd_status": "charge_neutral_candidate_generated",
                "feasibility_status": "selected_mass_balance_feasible",
            },
            {
                "candidate_rank": 2,
                "selected": False,
                "source": "unit_rejected",
                "phase_kind": 0,
                "composition": rejected,
                "tpd": 5.0e-4,
                "tpd_status": "charge_neutral_candidate_generated",
                "feasibility_status": "mass_balance_pair_unselected",
            },
        ],
    }
    held2["tpd_discovery"] = tpd_discovery
    held2["electroneutral_lift"] = {
        "basis_label": "counterion_pair_transformed_variables",
        "max_charge_residual": 0.0,
        "composition_sum_residual": 0.0,
        "round_trip_residual": 0.0,
        "component_nonnegativity_margin": 0.01,
    }
    held2["counterion_pairs"] = {
        "rank": 1,
        "expected_rank": 1,
        "pair_labels": ["Na+/Cl-"],
        "matrix": [[1.0, 1.0]],
    }
    payload["held2_phase_discovery"] = held2
    return _jsonable(payload)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate electrolyte HELD2 Stage II dual phase discovery.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    parser.add_argument("--require-stage-i", action="store_true")
    parser.add_argument("--require-bound-gap", action="store_true")
    parser.add_argument("--require-replay", action="store_true")
    parser.add_argument("--require-complete", action="store_true")
    args = parser.parse_args(argv)

    command = ["uv", "run", "--no-sync", "python", "scripts/validation/check_electrolyte_held2_stage_ii.py"]
    if args.json:
        command.append("--json")
    if args.require_stage_i:
        command.append("--require-stage-i")
    if args.require_bound_gap:
        command.append("--require-bound-gap")
    if args.require_replay:
        command.append("--require-replay")
    if args.require_complete:
        command.append("--require-complete")
    payload = evaluate_stage_ii(
        require_stage_i=args.require_stage_i,
        require_bound_gap=args.require_bound_gap,
        require_replay=args.require_replay,
        require_complete=args.require_complete,
        checker_command=command,
    )
    if args.require_complete:
        receipt = payload.get("electrolyte_held2_stage_ii", {}).get("native_freshness_receipt", {})
        if receipt:
            from scripts.validation import native_freshness

            try:
                native_freshness.require_equilibrium_native_fresh(dict(receipt))
            except ValueError as exc:
                print(str(exc), file=sys.stderr)
                return 2
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    elif payload["complete"]:
        print("Electrolyte HELD2 Stage II dual phase discovery validation passed.")
    else:
        print("Electrolyte HELD2 Stage II dual phase discovery validation failed:")
        for blocker in payload["blockers"]:
            print(f"- {blocker}")
    return 0 if payload["complete"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
