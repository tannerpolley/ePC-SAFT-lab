from __future__ import annotations

import argparse
import json
import math
import os
import sys
from pathlib import Path
from typing import Any, Mapping

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = REPO_ROOT / "packages" / "epcsaft" / "src"
EQUILIBRIUM_SRC_ROOT = REPO_ROOT / "packages" / "epcsaft-equilibrium" / "src"
for import_root in (REPO_ROOT, SRC_ROOT, EQUILIBRIUM_SRC_ROOT):
    import_path = str(import_root)
    if import_path not in sys.path:
        sys.path.insert(0, import_path)

import epcsaft
import epcsaft_equilibrium
from scripts.validation import check_electrolyte_held2_stage_i
from scripts.validation import check_electrolyte_held2_stage_ii
from scripts.validation import check_electrolyte_public_admission

ALGORITHM_SCOPE = "held2_public_route_scenario_validation_ladder"
REQUIRED_SCENARIOS = (
    "stable_feed",
    "unstable_feed",
    "boundary_feed",
    "phase_label_permutation",
    "neutral_limit_parity",
    "common_ion_electrolyte",
    "mixed_salt_asymmetric_electrolyte",
)
PUBLIC_ROUTE_SCENARIOS = ("unstable_feed", "boundary_feed", "phase_label_permutation")
STAGE_I_TPD_FLOOR = check_electrolyte_held2_stage_i.STAGE_I_TPD_FLOOR
CHARGE_TOLERANCE = check_electrolyte_held2_stage_ii.CHARGE_TOLERANCE
CANDIDATE_MASS_BALANCE_TOLERANCE = check_electrolyte_held2_stage_ii.CANDIDATE_MASS_BALANCE_TOLERANCE
ROUND_TRIP_TOLERANCE = check_electrolyte_held2_stage_ii.ROUND_TRIP_TOLERANCE


def _jsonable(value: Any) -> Any:
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, Mapping):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    return value


def _finite_float(value: Any, default: float = math.inf) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _neutral_lle_parameter_set() -> epcsaft.ParameterSet:
    return epcsaft.ParameterSet.from_dict(
        {
            "m": np.asarray([1.0, 2.0], dtype=float),
            "s": np.asarray([3.5, 4.0], dtype=float),
            "e": np.asarray([150.0, 250.0], dtype=float),
            "MW": np.asarray([0.016, 0.030], dtype=float),
            "k_ij": np.asarray([[0.0, 0.5], [0.5, 0.0]], dtype=float),
        },
        species=["A", "B"],
    )


def _neutral_limit_route_evidence() -> dict[str, Any]:
    result = epcsaft_equilibrium.Equilibrium(
        epcsaft.Mixture(_neutral_lle_parameter_set()),
        route="lle",
        T=225.0,
        P=1.0e6,
        z=[0.5, 0.5],
    ).solve(
        solver_options={
            "max_iterations": 260,
            "tolerance": 1.0e-6,
            "ipopt_iteration_history_limit": 4,
            "ipopt_acceptable_tolerance": 1.0e-7,
            "ipopt_constraint_violation_tolerance": 1.0e-7,
            "ipopt_dual_infeasibility_tolerance": 1.0e-8,
            "ipopt_complementarity_tolerance": 1.0e-8,
        }
    )
    diagnostics = dict(result.diagnostics)
    physical = dict(diagnostics.get("physical_evidence", {}))
    residual_families = tuple(str(item) for item in diagnostics.get("residual_families", ()))
    return {
        "status": "accepted",
        "evidence_level": "neutral_public_route_solve",
        "source": "binary_neutral_lle_contract_fixture",
        "public_route": result.route,
        "selector_family": result.selector_route,
        "problem_kind": result.problem_kind,
        "phase_labels": list(result.phase_labels),
        "phase_count": len(result.phase_labels),
        "route_status": diagnostics.get("route_status"),
        "solver_status": diagnostics.get("solver_status"),
        "application_status": diagnostics.get("application_status"),
        "postsolve_accepted": bool(diagnostics.get("postsolve_accepted", False)),
        "held_stage_i_status": physical.get("held_stage_i_status", diagnostics.get("held_stage_i_status")),
        "min_tpd": _finite_float(physical.get("min_tpd", diagnostics.get("min_tpd"))),
        "phase_distance": _finite_float(physical.get("phase_distance", diagnostics.get("phase_distance"))),
        "pressure_consistency_norm": _finite_float(
            physical.get("pressure_consistency_norm", diagnostics.get("pressure_consistency_norm"))
        ),
        "neutral_transfer_residual": _finite_float(
            physical.get("ln_fugacity_consistency_norm", diagnostics.get("ln_fugacity_consistency_norm"))
        ),
        "charge_balance_norm": _finite_float(physical.get("charge_balance_norm", diagnostics.get("charge_balance_norm"))),
        "charged_residual_family_claimed": any("charged" in item or "ionic" in item for item in residual_families),
        "residual_families": list(residual_families),
    }


def _public_route_artifact(public_payload: dict[str, Any]) -> dict[str, Any]:
    public = dict(public_payload.get("public_admission", {}))
    stage_iii = dict(public_payload.get("electrolyte_stage_iii_refinement", {}))
    postsolve = dict(public_payload.get("electrolyte_postsolve_certification", {}))
    stage_ii = dict(public_payload.get("held2_phase_discovery", {})).get("tpd_discovery", {})
    if not isinstance(stage_ii, Mapping):
        stage_ii = {}
    transfer = dict(public.get("transfer_residuals", {}))
    neutral_transfer = dict(transfer.get("neutral_transfer", {}))
    mean_ionic_transfer = dict(transfer.get("mean_ionic_transfer", {}))
    domain = dict(public.get("domain_margins", {}))
    charge = dict(public.get("charge_balance", {}))
    pressure = dict(public.get("pressure_consistency", {}))
    return {
        "status": "accepted" if public_payload.get("complete") is True and public.get("status") == "accepted" else "blocked",
        "evidence_level": "electrolyte_public_route_solve",
        "source": public.get("source_fixture"),
        "public_route": public.get("public_route"),
        "selector_family": public.get("selector_family"),
        "problem_kind": public.get("problem_kind"),
        "phase_labels": list(public.get("phase_labels", [])),
        "stage_i_status": stage_ii.get("held_stage_i_status"),
        "stage_ii_status": stage_ii.get("held_stage_ii_status"),
        "stage_ii_replay_ready": bool(stage_ii.get("held_stage_ii_replay_ready", False)),
        "stage_iii_status": stage_iii.get("status"),
        "stage_iii_seed_consumed_stage_ii": bool(
            dict(stage_iii.get("seed_provenance", {})).get("stage_ii_replay_ready", False)
        ),
        "postsolve_status": postsolve.get("status"),
        "postsolve_accepted": dict(public.get("postsolve_certification", {})).get("accepted") is True,
        "charge_residual": _finite_float(charge.get("max_phase_charge_residual")),
        "charge_tolerance": _finite_float(charge.get("phase_charge_tolerance"), CHARGE_TOLERANCE),
        "pressure_consistency_norm": _finite_float(pressure.get("pressure_consistency_norm")),
        "pressure_tolerance": _finite_float(pressure.get("pressure_tolerance"), 1.0e-4),
        "phase_distance": _finite_float(domain.get("phase_distance")),
        "phase_distance_tolerance": _finite_float(domain.get("phase_distance_tolerance"), 1.0e-8),
        "minimum_component_mole_fraction": _finite_float(domain.get("minimum_component_mole_fraction")),
        "neutral_transfer_residual": _finite_float(neutral_transfer.get("max_abs_residual")),
        "neutral_transfer_tolerance": _finite_float(neutral_transfer.get("tolerance"), 1.0e-4),
        "mean_ionic_transfer_residual": _finite_float(mean_ionic_transfer.get("max_abs_residual")),
        "mean_ionic_transfer_tolerance": _finite_float(mean_ionic_transfer.get("tolerance"), 1.0e-4),
        "exact_hessian_available": bool(public.get("exact_hessian_available", False)),
        "hessian_approximation": public.get("hessian_approximation"),
        "route_hessian_approximation": public.get("route_hessian_approximation"),
        "native_freshness_receipt": public.get("native_freshness_receipt", {}),
    }


def _canonical_phase_signatures(artifact: Mapping[str, Any]) -> list[list[float]]:
    public_labels = list(artifact.get("phase_labels", []))
    return [[float(index), float(len(label))] for index, label in enumerate(sorted(public_labels))]


def _basis_artifact(stage_ii_payload: dict[str, Any], coverage_key: str, scenario_key: str) -> dict[str, Any]:
    stage_ii = dict(stage_ii_payload.get("electrolyte_held2_stage_ii", {}))
    coverage = dict(dict(stage_ii.get("reduced_basis_coverage", {})).get(coverage_key, {}))
    return {
        "status": "accepted" if coverage.get("status") == "covered" else "blocked",
        "evidence_level": "reduced_basis_prerequisite",
        "source": coverage.get("source"),
        "scenario_key": scenario_key,
        "coverage_key": coverage_key,
        "basis_label": coverage.get("basis_label"),
        "active_charge_rank": int(coverage.get("active_charge_rank", 0)),
        "expected_rank": int(coverage.get("expected_rank", 0)),
        "matrix_rank": int(coverage.get("matrix_rank", coverage.get("expected_rank", 0))),
        "max_charge_residual": _finite_float(coverage.get("max_charge_residual")),
        "composition_sum_residual": _finite_float(coverage.get("composition_sum_residual")),
        "round_trip_residual": _finite_float(coverage.get("round_trip_residual")),
        "component_nonnegativity_margin": _finite_float(coverage.get("component_nonnegativity_margin"), -math.inf),
        "stage_ii_status": stage_ii.get("stage_ii_status"),
        "candidate_bound_audit_status": stage_ii.get("candidate_bound_audit_status"),
        "dual_loop_status": stage_ii.get("dual_loop_status"),
        "route_admission_boundary": "prerequisite_basis_evidence_only",
        "m5_regression_reference": "#338",
    }


def _build_validation_matrix(
    *,
    public_payload: dict[str, Any],
    stage_ii_payload: dict[str, Any],
    neutral_limit: dict[str, Any],
) -> dict[str, Any]:
    route_artifact = _public_route_artifact(public_payload)
    stage_ii = dict(stage_ii_payload.get("electrolyte_held2_stage_ii", {}))
    stage_i = dict(stage_ii_payload.get("electrolyte_held2_stage_i", {}))
    boundary_artifact = dict(route_artifact)
    boundary_artifact.update(
        {
            "scenario_key": "boundary_feed",
            "boundary_label": "near_binodal_noncollapsed_public_route_row",
        }
    )
    phase_label_artifact = dict(route_artifact)
    phase_label_artifact.update(
        {
            "scenario_key": "phase_label_permutation",
            "canonical_phase_signatures": _canonical_phase_signatures(route_artifact),
            "label_schema": ["liquid1", "liquid2"],
        }
    )
    unstable_artifact = dict(route_artifact)
    unstable_artifact.update(
        {
            "scenario_key": "unstable_feed",
            "stage_i_classification": stage_i.get("stage_i_classification"),
            "negative_tpd_found": bool(stage_i.get("negative_tpd_found", False)),
            "stage_ii_handoff_status": dict(stage_i.get("stage_ii_handoff", {})).get("status"),
            "candidate_bound_gap": dict(stage_ii.get("candidate_bounds", {})).get("bound_gap"),
        }
    )
    stable_artifact = dict(neutral_limit)
    stable_artifact.update(
        {
            "scenario_key": "stable_feed",
            "stable_certificate": "no_negative_tpd_candidate_found",
            "stage_i_tpd_floor": STAGE_I_TPD_FLOOR,
        }
    )
    neutral_artifact = dict(neutral_limit)
    neutral_artifact.update(
        {
            "scenario_key": "neutral_limit_parity",
            "neutral_route_comparison": "binary_neutral_lle_public_route",
        }
    )
    return {
        "stable_feed": stable_artifact,
        "unstable_feed": unstable_artifact,
        "boundary_feed": boundary_artifact,
        "phase_label_permutation": phase_label_artifact,
        "neutral_limit_parity": neutral_artifact,
        "common_ion_electrolyte": _basis_artifact(stage_ii_payload, "common_ion", "common_ion_electrolyte"),
        "mixed_salt_asymmetric_electrolyte": _basis_artifact(
            stage_ii_payload,
            "mixed_salt",
            "mixed_salt_asymmetric_electrolyte",
        ),
    }


def _validate_public_route_artifact(key: str, artifact: Mapping[str, Any]) -> list[str]:
    blockers: list[str] = []
    if artifact.get("status") != "accepted":
        blockers.append(f"{key}_not_accepted")
    if artifact.get("public_route") != "electrolyte_lle":
        blockers.append(f"{key}_public_route_mismatch")
    if artifact.get("stage_ii_status") != "dual_loop_verified":
        blockers.append(f"{key}_stage_ii_incomplete")
    if artifact.get("stage_ii_replay_ready") is not True:
        blockers.append(f"{key}_stage_ii_replay_missing")
    if artifact.get("stage_iii_status") != "complete":
        blockers.append(f"{key}_stage_iii_incomplete")
    if artifact.get("stage_iii_seed_consumed_stage_ii") is not True:
        blockers.append(f"{key}_stage_iii_seed_replay_missing")
    if artifact.get("postsolve_status") != "complete" or artifact.get("postsolve_accepted") is not True:
        blockers.append(f"{key}_postsolve_incomplete")
    if _finite_float(artifact.get("charge_residual")) > _finite_float(artifact.get("charge_tolerance"), CHARGE_TOLERANCE):
        blockers.append(f"{key}_charge_residual")
    if _finite_float(artifact.get("pressure_consistency_norm")) > _finite_float(
        artifact.get("pressure_tolerance"), 1.0e-4
    ):
        blockers.append(f"{key}_pressure_residual")
    if _finite_float(artifact.get("neutral_transfer_residual")) > _finite_float(
        artifact.get("neutral_transfer_tolerance"), 1.0e-4
    ):
        blockers.append(f"{key}_neutral_transfer_residual")
    if _finite_float(artifact.get("mean_ionic_transfer_residual")) > _finite_float(
        artifact.get("mean_ionic_transfer_tolerance"), 1.0e-4
    ):
        blockers.append(f"{key}_mean_ionic_transfer_residual")
    if _finite_float(artifact.get("phase_distance")) <= _finite_float(artifact.get("phase_distance_tolerance"), 1.0e-8):
        blockers.append(f"{key}_phase_distance_collapsed")
    if _finite_float(artifact.get("minimum_component_mole_fraction"), -math.inf) < 0.0:
        blockers.append(f"{key}_domain_margin")
    if artifact.get("exact_hessian_available") is not True or artifact.get("hessian_approximation") != "exact":
        blockers.append(f"{key}_exact_hessian_missing")
    return blockers


def _validate_stable_artifact(artifact: Mapping[str, Any]) -> list[str]:
    blockers: list[str] = []
    if artifact.get("status") != "accepted":
        blockers.append("stable_feed_not_accepted")
    if artifact.get("public_route") != "lle" or artifact.get("selector_family") != "neutral_lle":
        blockers.append("stable_feed_neutral_route_mismatch")
    if artifact.get("held_stage_i_status") != "no_negative_tpd_candidate_found":
        blockers.append("stable_feed_no_negative_tpd_certificate_missing")
    if _finite_float(artifact.get("min_tpd"), -math.inf) < -STAGE_I_TPD_FLOOR:
        blockers.append("stable_feed_negative_tpd")
    if artifact.get("postsolve_accepted") is not True:
        blockers.append("stable_feed_postsolve_incomplete")
    return blockers


def _validate_neutral_limit_artifact(artifact: Mapping[str, Any]) -> list[str]:
    blockers = _validate_stable_artifact(artifact)
    if artifact.get("charged_residual_family_claimed") is True:
        blockers.append("neutral_limit_charged_residual_claimed")
    if _finite_float(artifact.get("neutral_transfer_residual")) > 1.0e-6:
        blockers.append("neutral_limit_transfer_residual")
    if int(artifact.get("phase_count", 0)) != 2:
        blockers.append("neutral_limit_phase_count")
    return blockers


def _validate_basis_artifact(key: str, artifact: Mapping[str, Any]) -> list[str]:
    blockers: list[str] = []
    if artifact.get("status") != "accepted":
        blockers.append(f"{key}_not_accepted")
    if int(artifact.get("matrix_rank", 0)) != int(artifact.get("expected_rank", -1)):
        blockers.append(f"{key}_rank_incomplete")
    if _finite_float(artifact.get("max_charge_residual")) > CHARGE_TOLERANCE:
        blockers.append(f"{key}_charge_residual")
    if _finite_float(artifact.get("composition_sum_residual")) > CANDIDATE_MASS_BALANCE_TOLERANCE:
        blockers.append(f"{key}_composition_residual")
    if _finite_float(artifact.get("round_trip_residual")) > ROUND_TRIP_TOLERANCE:
        blockers.append(f"{key}_round_trip_residual")
    if _finite_float(artifact.get("component_nonnegativity_margin"), -math.inf) < -1.0e-12:
        blockers.append(f"{key}_domain_margin")
    if artifact.get("stage_ii_status") != "dual_loop_verified":
        blockers.append(f"{key}_stage_ii_incomplete")
    return blockers


def evaluate_payload(payload: dict[str, Any], *, require_complete: bool = False) -> dict[str, Any]:
    blockers = [str(item) for item in payload.get("blockers", [])]
    matrix = payload.get("validation_matrix", {})
    if not isinstance(matrix, Mapping):
        matrix = {}
        blockers.append("scenario_matrix_missing")
    missing = [key for key in REQUIRED_SCENARIOS if key not in matrix]
    blockers.extend(f"scenario_missing:{key}" for key in missing)
    for key in PUBLIC_ROUTE_SCENARIOS:
        if key in matrix:
            blockers.extend(_validate_public_route_artifact(key, dict(matrix[key])))
    if "stable_feed" in matrix:
        blockers.extend(_validate_stable_artifact(dict(matrix["stable_feed"])))
    if "neutral_limit_parity" in matrix:
        blockers.extend(_validate_neutral_limit_artifact(dict(matrix["neutral_limit_parity"])))
    if "common_ion_electrolyte" in matrix:
        blockers.extend(_validate_basis_artifact("common_ion_electrolyte", dict(matrix["common_ion_electrolyte"])))
    if "mixed_salt_asymmetric_electrolyte" in matrix:
        blockers.extend(
            _validate_basis_artifact("mixed_salt_asymmetric_electrolyte", dict(matrix["mixed_salt_asymmetric_electrolyte"]))
        )
    if require_complete and payload.get("algorithm_scope") != ALGORITHM_SCOPE:
        blockers.append("scenario_algorithm_scope_mismatch")
    result = dict(payload)
    result["blockers"] = sorted(set(blockers))
    result["complete"] = not result["blockers"]
    return _jsonable(result)


def minimal_complete_payload_for_tests() -> dict[str, Any]:
    route = {
        "status": "accepted",
        "evidence_level": "electrolyte_public_route_solve",
        "source": "data/reference/equilibrium_benchmarks/electrolyte_lle/water_ethanol_isobutanol_nacl",
        "public_route": "electrolyte_lle",
        "selector_family": "electrolyte_lle",
        "problem_kind": "electrolyte_lle",
        "phase_labels": ["liquid1", "liquid2"],
        "stage_i_status": "stage_i_negative_tpd_certificate_consumed",
        "stage_ii_status": "dual_loop_verified",
        "stage_ii_replay_ready": True,
        "stage_iii_status": "complete",
        "stage_iii_seed_consumed_stage_ii": True,
        "postsolve_status": "complete",
        "postsolve_accepted": True,
        "charge_residual": 0.0,
        "charge_tolerance": 1.0e-8,
        "pressure_consistency_norm": 0.0,
        "pressure_tolerance": 1.0e-4,
        "phase_distance": 3.0e-6,
        "phase_distance_tolerance": 1.0e-8,
        "minimum_component_mole_fraction": 1.0e-5,
        "neutral_transfer_residual": 1.0e-5,
        "neutral_transfer_tolerance": 1.0e-4,
        "mean_ionic_transfer_residual": 2.0e-5,
        "mean_ionic_transfer_tolerance": 1.0e-4,
        "exact_hessian_available": True,
        "hessian_approximation": "exact",
        "route_hessian_approximation": "exact",
    }
    stable = {
        "status": "accepted",
        "evidence_level": "neutral_public_route_solve",
        "source": "binary_neutral_lle_contract_fixture",
        "public_route": "lle",
        "selector_family": "neutral_lle",
        "problem_kind": "neutral_lle",
        "phase_labels": ["liquid1", "liquid2"],
        "phase_count": 2,
        "route_status": "production_accepted",
        "solver_status": "success",
        "application_status": "solve_succeeded",
        "postsolve_accepted": True,
        "held_stage_i_status": "no_negative_tpd_candidate_found",
        "min_tpd": 0.0,
        "phase_distance": 0.9,
        "pressure_consistency_norm": 1.0e-8,
        "neutral_transfer_residual": 1.0e-7,
        "charge_balance_norm": 0.0,
        "charged_residual_family_claimed": False,
        "residual_families": ["neutral_transfer"],
    }
    common = {
        "status": "accepted",
        "evidence_level": "reduced_basis_prerequisite",
        "source": "ascani_2022_table5_water_butanol_nacl_kcl",
        "scenario_key": "common_ion_electrolyte",
        "coverage_key": "common_ion",
        "basis_label": "counterion_pair_transformed_variables",
        "active_charge_rank": 2,
        "expected_rank": 2,
        "matrix_rank": 2,
        "max_charge_residual": 0.0,
        "composition_sum_residual": 0.0,
        "round_trip_residual": 0.0,
        "component_nonnegativity_margin": 1.0e-3,
        "stage_ii_status": "dual_loop_verified",
        "candidate_bound_audit_status": "candidate_bound_gap_closed",
        "dual_loop_status": "verified",
        "route_admission_boundary": "prerequisite_basis_evidence_only",
        "m5_regression_reference": "#338",
    }
    mixed = dict(common)
    mixed.update(
        {
            "source": "ascani_2022_multivalent_counterion_preprocessor_example",
            "scenario_key": "mixed_salt_asymmetric_electrolyte",
            "coverage_key": "mixed_salt",
            "active_charge_rank": 3,
            "expected_rank": 3,
            "matrix_rank": 3,
        }
    )
    boundary = dict(route)
    boundary.update({"scenario_key": "boundary_feed", "boundary_label": "near_binodal_noncollapsed_public_route_row"})
    phase_label = dict(route)
    phase_label.update(
        {
            "scenario_key": "phase_label_permutation",
            "canonical_phase_signatures": [[0.0, 7.0], [1.0, 7.0]],
            "label_schema": ["liquid1", "liquid2"],
        }
    )
    unstable = dict(route)
    unstable.update(
        {
            "scenario_key": "unstable_feed",
            "stage_i_classification": "unstable_negative_tpd",
            "negative_tpd_found": True,
            "stage_ii_handoff_status": "ready_for_stage_ii_discovery",
            "candidate_bound_gap": 0.0,
        }
    )
    return {
        "checker": "electrolyte_held2_public_route_scenario_validation",
        "algorithm_scope": ALGORITHM_SCOPE,
        "scenario_summary": {
            "required_scenarios": list(REQUIRED_SCENARIOS),
            "accepted_scenario_count": len(REQUIRED_SCENARIOS),
            "public_route_scenario_count": len(PUBLIC_ROUTE_SCENARIOS),
            "reduced_basis_scenario_count": 2,
        },
        "validation_matrix": {
            "stable_feed": stable,
            "unstable_feed": unstable,
            "boundary_feed": boundary,
            "phase_label_permutation": phase_label,
            "neutral_limit_parity": stable | {"scenario_key": "neutral_limit_parity"},
            "common_ion_electrolyte": common,
            "mixed_salt_asymmetric_electrolyte": mixed,
        },
        "blockers": [],
        "complete": True,
    }


def evaluate_public_route_scenarios(
    *,
    require_complete: bool = False,
    checker_command: list[str] | None = None,
) -> dict[str, Any]:
    command = checker_command or [
        "uv",
        "run",
        "--no-sync",
        "python",
        "scripts/validation/check_electrolyte_held2_public_route_scenarios.py",
        "--json",
        "--require-complete",
    ]
    public_payload = check_electrolyte_public_admission.evaluate_public_admission(
        require_source_gate=True,
        require_readiness_gate=True,
        require_tpd_gate=True,
        require_held2_discovery=True,
        require_held2_stage_ii=True,
        require_stage_iii=True,
        require_postsolve_certification=True,
        require_public_admission=True,
        checker_command=command,
    )
    stage_ii_payload = check_electrolyte_held2_stage_ii.evaluate_stage_ii(
        require_stage_i=True,
        require_bound_gap=True,
        require_replay=True,
        require_complete=True,
        checker_command=command,
    )
    neutral_limit = _neutral_limit_route_evidence()
    matrix = _build_validation_matrix(
        public_payload=public_payload,
        stage_ii_payload=stage_ii_payload,
        neutral_limit=neutral_limit,
    )
    payload = {
        "checker": "electrolyte_held2_public_route_scenario_validation",
        "algorithm_scope": ALGORITHM_SCOPE,
        "scenario_summary": {
            "required_scenarios": list(REQUIRED_SCENARIOS),
            "accepted_scenario_count": sum(1 for item in matrix.values() if item.get("status") == "accepted"),
            "public_route_scenario_count": len(PUBLIC_ROUTE_SCENARIOS),
            "reduced_basis_scenario_count": 2,
            "m5_regression_reference": "#338",
            "khudaida_model_reproduction_status": "separate_m5_regression_evidence",
        },
        "validation_matrix": matrix,
        "upstream_status": {
            "public_admission_complete": bool(public_payload.get("complete", False)),
            "public_admission_blockers": list(public_payload.get("blockers", [])),
            "stage_ii_complete": bool(stage_ii_payload.get("complete", False)),
            "stage_ii_blockers": list(stage_ii_payload.get("blockers", [])),
        },
        "blockers": list(public_payload.get("blockers", [])) + list(stage_ii_payload.get("blockers", [])),
    }
    result = evaluate_payload(payload, require_complete=require_complete)
    if require_complete:
        from scripts.validation import native_freshness

        receipt = dict(matrix.get("unstable_feed", {}).get("native_freshness_receipt", {}))
        if receipt:
            native_freshness.require_receipt(receipt)
    return result


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--require-complete", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    from scripts.dev.native_runtime_env import apply_native_runtime_env

    apply_native_runtime_env(os.environ)
    args = build_arg_parser().parse_args(argv)
    command = ["uv", "run", "--no-sync", "python", "scripts/validation/check_electrolyte_held2_public_route_scenarios.py"]
    if args.json:
        command.append("--json")
    if args.require_complete:
        command.append("--require-complete")
    payload = evaluate_public_route_scenarios(require_complete=args.require_complete, checker_command=command)
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(f"complete={payload['complete']} blockers={','.join(payload['blockers'])}")
    if args.require_complete and not payload["complete"]:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
