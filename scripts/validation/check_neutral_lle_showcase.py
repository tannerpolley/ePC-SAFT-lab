from __future__ import annotations

import argparse
import csv
import itertools
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

from scripts.dev.native_runtime_env import apply_native_runtime_env

apply_native_runtime_env(os.environ)

from epcsaft.state.native_adapter import ePCSAFTMixture
from epcsaft_equilibrium._native import extension_native_core
from scripts.validation import equilibrium_validation_runtime as runtime
from scripts.validation import native_freshness

_core = extension_native_core()

DEFAULT_CASE_DIR = (
    REPO_ROOT
    / "data"
    / "reference"
    / "equilibrium_benchmarks"
    / "neutral_lle"
    / "perfluorohexane_hexane"
)

REQUIRED_FILES = (
    "metadata.json",
    "source_notes.md",
    "pure_component_parameters.csv",
    "binary_interactions.csv",
    "experimental_tielines.csv",
    "feed_compositions.csv",
    "thresholds.json",
    "source_binodal_points.csv",
)
REQUIRED_METADATA_FIELDS = (
    "case_label",
    "family_label",
    "route",
    "selector_route",
    "species",
    "expected_phase_count",
    "source_status",
    "source_model_family",
    "runtime_model_family",
    "source_paths",
    "parameter_basis",
    "binary_interaction_basis",
    "association_active",
    "electrolyte_active",
    "reaction_active",
    "scope_statement",
)
REQUIRED_THRESHOLDS = (
    "solver_max_iterations",
    "solver_tolerance",
    "acceptable_tolerance",
    "constraint_violation_tolerance",
    "dual_infeasibility_tolerance",
    "complementarity_tolerance",
    "composition_abs",
    "phase_fraction_abs",
    "material_balance_abs",
    "pressure_abs_Pa",
    "ln_fugacity_abs",
    "phase_distance_min",
    "source_temperature_pair_abs_K",
)
ACCEPTED_MODEL_FAMILIES = {"PC-SAFT", "ePC-SAFT", "PC-SAFT-compatible sPC-SAFT"}


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _read_csv(path: Path) -> list[dict[str, str]]:
    return list(csv.DictReader(path.read_text(encoding="utf-8").splitlines()))


def _finite_float(value: Any) -> bool:
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return False
    return math.isfinite(numeric)


def _positive_finite_float(value: Any) -> bool:
    return _finite_float(value) and float(value) > 0.0


def _composition_from_prefix(row: dict[str, str], prefix: str, count: int) -> list[float]:
    values = [float(row[f"{prefix}{index}"]) for index in range(1, count + 1)]
    if not math.isclose(sum(values), 1.0, rel_tol=0.0, abs_tol=1.0e-10):
        raise ValueError(f"{prefix} composition does not sum to 1")
    if any(value < 0.0 or value > 1.0 for value in values):
        raise ValueError(f"{prefix} composition contains value outside [0, 1]")
    return values


def _load_fixture(case_dir: Path) -> dict[str, Any]:
    metadata = _read_json(case_dir / "metadata.json")
    thresholds = _read_json(case_dir / "thresholds.json")
    pure_rows = _read_csv(case_dir / "pure_component_parameters.csv")
    binary_rows = _read_csv(case_dir / "binary_interactions.csv")
    tie_rows = _read_csv(case_dir / "experimental_tielines.csv")
    feed_rows = _read_csv(case_dir / "feed_compositions.csv")
    binodal_rows = _read_csv(case_dir / "source_binodal_points.csv")
    source_notes = (case_dir / "source_notes.md").read_text(encoding="utf-8")
    return {
        "metadata": metadata,
        "thresholds": thresholds,
        "pure_rows": pure_rows,
        "binary_rows": binary_rows,
        "tie_rows": tie_rows,
        "feed_rows": feed_rows,
        "binodal_rows": binodal_rows,
        "source_notes": source_notes,
    }


def _file_blockers(case_dir: Path) -> list[str]:
    return [f"missing_required_file:{name}" for name in REQUIRED_FILES if not (case_dir / name).exists()]


def _metadata_blockers(metadata: dict[str, Any], species: list[str]) -> list[str]:
    blockers = [f"missing_metadata_field:{field}" for field in REQUIRED_METADATA_FIELDS if field not in metadata]
    if metadata.get("route") != "lle":
        blockers.append("neutral_lle_public_route_mismatch")
    if metadata.get("selector_route") != "neutral_lle":
        blockers.append("neutral_lle_selector_route_mismatch")
    if metadata.get("species") != species:
        blockers.append("neutral_lle_species_order_mismatch")
    if metadata.get("expected_phase_count") != 2:
        blockers.append("neutral_lle_expected_phase_count_mismatch")
    if metadata.get("source_status") != "source_backed":
        blockers.append("neutral_lle_source_status_not_source_backed")
    if str(metadata.get("source_model_family", "")) not in ACCEPTED_MODEL_FAMILIES:
        blockers.append("neutral_lle_source_model_family_rejected")
    if metadata.get("association_active") is not False:
        blockers.append("neutral_lle_association_terms_active")
    if metadata.get("electrolyte_active") is not False:
        blockers.append("neutral_lle_electrolyte_terms_active")
    if metadata.get("reaction_active") is not False:
        blockers.append("neutral_lle_reaction_terms_active")
    source_paths = metadata.get("source_paths")
    if not isinstance(source_paths, dict) or not all(str(value).strip() for value in source_paths.values()):
        blockers.append("neutral_lle_source_paths_incomplete")
    return blockers


def _threshold_blockers(thresholds: dict[str, Any]) -> list[str]:
    blockers = [f"missing_threshold:{field}" for field in REQUIRED_THRESHOLDS if field not in thresholds]
    for field in REQUIRED_THRESHOLDS:
        if field not in thresholds:
            continue
        value = thresholds[field]
        if field == "solver_max_iterations":
            if not isinstance(value, int) or value <= 0:
                blockers.append("neutral_lle_solver_max_iterations_invalid")
        elif not _positive_finite_float(value):
            blockers.append(f"neutral_lle_threshold_invalid:{field}")
    return blockers


def _source_data_blockers(
    tie_rows: list[dict[str, str]],
    feed_rows: list[dict[str, str]],
    binodal_rows: list[dict[str, str]],
    species: list[str],
    thresholds: dict[str, Any],
) -> list[str]:
    blockers: list[str] = []
    if len(tie_rows) != 1:
        blockers.append("neutral_lle_expected_one_source_tieline")
    if len(feed_rows) != 1:
        blockers.append("neutral_lle_expected_one_feed_row")
    if len(binodal_rows) < 2:
        blockers.append("neutral_lle_source_binodal_rows_insufficient")
    if blockers:
        return blockers

    tie = tie_rows[0]
    feed = feed_rows[0]
    if tie["component_1"] != species[0] or tie["component_2"] != species[1]:
        blockers.append("neutral_lle_tieline_species_order_mismatch")
    if feed["component_1"] != species[0] or feed["component_2"] != species[1]:
        blockers.append("neutral_lle_feed_species_order_mismatch")
    if tie.get("source_status") != "source_backed":
        blockers.append("neutral_lle_tieline_source_status_rejected")
    if tie.get("source_basis") != "paired_binodal_branch_rows":
        blockers.append("neutral_lle_tieline_source_basis_rejected")
    if feed.get("source_status") != "source_derived":
        blockers.append("neutral_lle_feed_source_status_rejected")
    for field in ("temperature_K", "pressure_Pa", "pressure_kPa", "liquid1_source_temperature_K", "liquid2_source_temperature_K"):
        if not _positive_finite_float(tie.get(field)):
            blockers.append(f"neutral_lle_tieline_field_invalid:{field}")
    for field in ("temperature_K", "pressure_Pa", "z1", "z2", "liquid1_phase_fraction", "liquid2_phase_fraction"):
        if not _finite_float(feed.get(field)):
            blockers.append(f"neutral_lle_feed_field_invalid:{field}")
    try:
        _composition_from_prefix(tie, "liquid1_x", len(species))
        _composition_from_prefix(tie, "liquid2_x", len(species))
        _composition_from_prefix(feed, "z", len(species))
    except (KeyError, ValueError) as exc:
        blockers.append(f"neutral_lle_source_composition_invalid:{exc}")
    if not math.isclose(float(feed["liquid1_phase_fraction"]) + float(feed["liquid2_phase_fraction"]), 1.0, abs_tol=1.0e-12):
        blockers.append("neutral_lle_feed_phase_fractions_do_not_sum_to_one")
    if abs(float(tie["temperature_difference_K"])) > float(thresholds["source_temperature_pair_abs_K"]):
        blockers.append("neutral_lle_source_branch_temperature_gap_exceeds_threshold")
    for row in binodal_rows:
        if row.get("component_1") != species[0] or row.get("component_2") != species[1]:
            blockers.append("neutral_lle_binodal_species_order_mismatch")
            break
        if row.get("method") != "cloud_point":
            blockers.append("neutral_lle_binodal_method_rejected")
            break
    return blockers


def _parameter_blockers(
    pure_rows: list[dict[str, str]],
    binary_rows: list[dict[str, str]],
    species: list[str],
) -> list[str]:
    blockers: list[str] = []
    pure_by_species = {row.get("species", ""): row for row in pure_rows}
    if set(pure_by_species) != set(species):
        blockers.append("neutral_lle_pure_parameter_species_mismatch")
        return blockers
    for name in species:
        row = pure_by_species[name]
        for field in ("m", "s_A", "e_over_k_K", "molecular_weight_g_per_mol"):
            if not _positive_finite_float(row.get(field)):
                blockers.append(f"neutral_lle_pure_parameter_invalid:{name}:{field}")
        if row.get("source_status") not in {"source_backed", "source_derived"}:
            blockers.append(f"neutral_lle_pure_parameter_source_rejected:{name}")
    if len(binary_rows) != 1:
        blockers.append("neutral_lle_expected_one_binary_interaction")
        return blockers
    binary = binary_rows[0]
    if {binary.get("component_i"), binary.get("component_j")} != set(species):
        blockers.append("neutral_lle_binary_interaction_species_mismatch")
    if binary.get("source_status") != "source_fitted":
        blockers.append("neutral_lle_binary_interaction_source_not_fitted")
    if not _positive_finite_float(binary.get("k_ij")):
        blockers.append("neutral_lle_binary_interaction_invalid")
    return blockers


def _fixture_payload(case_dir: Path) -> dict[str, Any]:
    blockers = _file_blockers(case_dir)
    if blockers:
        return {
            "executable": False,
            "source_data": {"status": "blocked"},
            "binary_interaction": {"status": "blocked"},
            "blockers": blockers,
        }

    payload = _load_fixture(case_dir)
    metadata = payload["metadata"]
    thresholds = payload["thresholds"]
    species = [str(item) for item in metadata.get("species", [])]
    blockers.extend(_metadata_blockers(metadata, species))
    blockers.extend(_threshold_blockers(thresholds))
    if not blockers:
        blockers.extend(
            _source_data_blockers(
                payload["tie_rows"],
                payload["feed_rows"],
                payload["binodal_rows"],
                species,
                thresholds,
            )
        )
        blockers.extend(_parameter_blockers(payload["pure_rows"], payload["binary_rows"], species))
    if not payload["source_notes"].strip():
        blockers.append("neutral_lle_source_notes_empty")
    binary_status = payload["binary_rows"][0].get("source_status", "blocked") if payload["binary_rows"] else "blocked"
    return {
        "executable": not blockers,
        "source_data": {
            "status": "source_backed" if not blockers else "blocked",
            "tieline_count": len(payload["tie_rows"]),
            "binodal_point_count": len(payload["binodal_rows"]),
        },
        "binary_interaction": {
            "status": binary_status if not blockers else "blocked",
            "k_ij": float(payload["binary_rows"][0]["k_ij"]) if payload["binary_rows"] and _finite_float(payload["binary_rows"][0].get("k_ij")) else None,
        },
        "blockers": blockers,
    }


def _build_mixture(case_dir: Path, species: list[str]) -> ePCSAFTMixture:
    pure_by_species = {row["species"]: row for row in _read_csv(case_dir / "pure_component_parameters.csv")}
    binary_rows = _read_csv(case_dir / "binary_interactions.csv")
    index = {name: position for position, name in enumerate(species)}
    k_ij = np.zeros((len(species), len(species)), dtype=float)
    for row in binary_rows:
        i = index[row["component_i"]]
        j = index[row["component_j"]]
        value = float(row["k_ij"])
        k_ij[i, j] = value
        k_ij[j, i] = value
    if not np.any(k_ij):
        raise ValueError("neutral_lle_binary_interaction_requires_explicit_nonzero_value")
    return ePCSAFTMixture.from_params(
        {
            "m": np.asarray([float(pure_by_species[name]["m"]) for name in species], dtype=float),
            "s": np.asarray([float(pure_by_species[name]["s_A"]) for name in species], dtype=float),
            "e": np.asarray([float(pure_by_species[name]["e_over_k_K"]) for name in species], dtype=float),
            "k_ij": k_ij,
        },
        species=species,
    )


def _feed_row(case_dir: Path) -> dict[str, str]:
    rows = _read_csv(case_dir / "feed_compositions.csv")
    if len(rows) != 1:
        raise ValueError("neutral_lle_expected_one_feed_row")
    return rows[0]


def _tieline_row(case_dir: Path) -> dict[str, str]:
    rows = _read_csv(case_dir / "experimental_tielines.csv")
    if len(rows) != 1:
        raise ValueError("neutral_lle_expected_one_source_tieline")
    return rows[0]


def _run_route_payload(case_dir: Path, metadata: dict[str, Any], thresholds: dict[str, Any], *, debug: bool) -> dict[str, Any]:
    species = [str(item) for item in metadata["species"]]
    mix = _build_mixture(case_dir, species)
    feed = _feed_row(case_dir)
    request = {
        "route": "neutral_lle",
        "temperature": float(feed["temperature_K"]),
        "pressure": float(feed["pressure_Pa"]),
        "composition": _composition_from_prefix(feed, "z", len(species)),
        "composition_role": "feed",
    }
    return dict(
        _core._native_equilibrium_selector_route_result(
            mix._native,
            request,
            int(thresholds["solver_max_iterations"]),
            float(thresholds["solver_tolerance"]),
            0.0,
            "auto",
            50 if debug else 8,
            1.0e-8,
            float(thresholds["pressure_abs_Pa"]),
            float(thresholds["solver_tolerance"]),
            float(thresholds["solver_tolerance"]),
            {},
            linear_solver="auto",
            print_level=5 if debug else 0,
            acceptable_tolerance=float(thresholds["acceptable_tolerance"]),
            constraint_violation_tolerance=float(thresholds["constraint_violation_tolerance"]),
            dual_infeasibility_tolerance=float(thresholds["dual_infeasibility_tolerance"]),
            complementarity_tolerance=float(thresholds["complementarity_tolerance"]),
        )
    )


def _run_route(
    case_dir: Path,
    metadata: dict[str, Any],
    thresholds: dict[str, Any],
    *,
    debug: bool,
    show_native_output: bool,
    redirect_native_output_to_stderr: bool,
) -> dict[str, Any]:
    if show_native_output:
        return _run_route_payload(case_dir, metadata, thresholds, debug=debug)
    if redirect_native_output_to_stderr:
        with runtime.redirect_native_stdout_to_stderr():
            return _run_route_payload(case_dir, metadata, thresholds, debug=debug)
    with runtime.suppress_native_stdout():
        return _run_route_payload(case_dir, metadata, thresholds, debug=debug)


def _phase_totals(route_payload: dict[str, Any]) -> list[float]:
    postsolve = route_payload.get("postsolve")
    if isinstance(postsolve, dict) and isinstance(postsolve.get("phase_amount_totals"), list):
        return [float(value) for value in postsolve["phase_amount_totals"]]
    return [float(sum(phase_amounts)) for phase_amounts in route_payload.get("phase_amounts", [])]


def _expected(case_dir: Path, species_count: int) -> tuple[dict[str, list[float]], dict[str, float]]:
    tie = _tieline_row(case_dir)
    feed = _feed_row(case_dir)
    return (
        {
            "liquid1": _composition_from_prefix(tie, "liquid1_x", species_count),
            "liquid2": _composition_from_prefix(tie, "liquid2_x", species_count),
        },
        {
            "liquid1": float(feed["liquid1_phase_fraction"]),
            "liquid2": float(feed["liquid2_phase_fraction"]),
        },
    )


def _best_phase_match(
    actual_compositions: list[list[float]],
    actual_fractions: list[float],
    expected_compositions: dict[str, list[float]],
    expected_fractions: dict[str, float],
) -> dict[str, Any]:
    labels = list(expected_compositions)
    best: dict[str, Any] | None = None
    for permutation in itertools.permutations(range(len(actual_compositions)), len(labels)):
        composition_errors = []
        fraction_errors = []
        mapping: dict[str, int] = {}
        for label, actual_index in zip(labels, permutation, strict=True):
            mapping[label] = actual_index
            expected = expected_compositions[label]
            actual = actual_compositions[actual_index]
            composition_errors.append(max(abs(left - right) for left, right in zip(expected, actual, strict=True)))
            fraction_errors.append(abs(expected_fractions[label] - actual_fractions[actual_index]))
        candidate = {
            "phase_index_by_expected_label": mapping,
            "max_composition_abs_error": max(composition_errors),
            "max_phase_fraction_abs_error": max(fraction_errors),
        }
        if best is None or (
            candidate["max_composition_abs_error"] + candidate["max_phase_fraction_abs_error"]
            < best["max_composition_abs_error"] + best["max_phase_fraction_abs_error"]
        ):
            best = candidate
    if best is None:
        raise ValueError("neutral_lle_no_phase_match_constructed")
    return best


def _route_certification_blockers(postsolve: dict[str, Any], *, expected_phase_count: int, thresholds: dict[str, Any]) -> list[str]:
    blockers: list[str] = []
    if postsolve.get("phase_discovery_backend") != "continuous_tpd_held_dual_phase_discovery":
        blockers.append("neutral_lle_phase_discovery_backend_rejected")
    if postsolve.get("stability_certificate") != "tpd_postsolve":
        blockers.append("neutral_lle_tpd_postsolve_not_certified")
    if postsolve.get("stability_checked") is not True:
        blockers.append("neutral_lle_stability_not_checked")
    if postsolve.get("stability_accepted") is not True:
        blockers.append("neutral_lle_stability_not_accepted")
    if postsolve.get("candidate_completeness_accepted") is not True:
        blockers.append("neutral_lle_candidate_completeness_not_accepted")
    if postsolve.get("phase_set_status") != "phase_set_certified":
        blockers.append("neutral_lle_phase_set_not_certified")
    if int(postsolve.get("selected_candidate_count", 0)) != expected_phase_count:
        blockers.append("neutral_lle_selected_candidate_count_mismatch")
    if not _positive_finite_float(postsolve.get("phase_distance")) or float(postsolve.get("phase_distance", 0.0)) < float(thresholds["phase_distance_min"]):
        blockers.append("neutral_lle_phase_distance_not_distinct")
    if postsolve.get("held_stage_ii_candidate_bound_audit_status") != "candidate_bound_gap_closed":
        blockers.append("neutral_lle_held_stage_ii_bound_gap_open")
    if postsolve.get("held_stage_ii_status") != "dual_loop_verified":
        blockers.append("neutral_lle_held_stage_ii_not_verified")
    if postsolve.get("held_stage_ii_dual_loop_status") != "verified":
        blockers.append("neutral_lle_held_stage_ii_dual_loop_not_verified")
    if postsolve.get("held_stage_ii_replay_ready") is not True:
        blockers.append("neutral_lle_held_stage_ii_not_replay_ready")
    if postsolve.get("held_stage_iii_status") != "ipopt_refinement_completed_current_route":
        blockers.append("neutral_lle_held_stage_iii_not_completed")
    if postsolve.get("held_stage_iii_consumed_stage_ii_replay_metadata") is not True:
        blockers.append("neutral_lle_held_stage_iii_did_not_consume_stage_ii_replay")
    return blockers


def evaluate_case_dir(
    case_dir: Path = DEFAULT_CASE_DIR,
    *,
    debug: bool = False,
    show_native_output: bool = False,
    redirect_native_output_to_stderr: bool = False,
    checker_command: list[str] | None = None,
) -> dict[str, Any]:
    fixture = _fixture_payload(case_dir)
    metadata = _read_json(case_dir / "metadata.json") if (case_dir / "metadata.json").exists() else {}
    thresholds = _read_json(case_dir / "thresholds.json") if (case_dir / "thresholds.json").exists() else {}
    blockers = list(fixture["blockers"])
    route_payload: dict[str, Any] | None = None
    comparison: dict[str, Any] | None = None
    route_accepted = False
    if fixture["executable"]:
        route_payload = _run_route(
            case_dir,
            metadata,
            thresholds,
            debug=debug,
            show_native_output=show_native_output,
            redirect_native_output_to_stderr=redirect_native_output_to_stderr,
        )
        postsolve = route_payload.get("postsolve")
        postsolve = postsolve if isinstance(postsolve, dict) else {}
        actual_compositions = [list(map(float, row)) for row in postsolve.get("phase_compositions", [])]
        phase_totals = _phase_totals(route_payload)
        total_amount = sum(phase_totals)
        actual_fractions = [amount / total_amount for amount in phase_totals] if total_amount > 0.0 else []
        expected_compositions, expected_fractions = _expected(case_dir, len(metadata["species"]))
        if len(actual_compositions) == len(expected_compositions) and len(actual_fractions) == len(expected_fractions):
            comparison = _best_phase_match(
                actual_compositions,
                actual_fractions,
                expected_compositions,
                expected_fractions,
            )
        route_certification_blockers = _route_certification_blockers(
            postsolve,
            expected_phase_count=int(metadata["expected_phase_count"]),
            thresholds=thresholds,
        )
        blockers.extend(route_certification_blockers)
        route_accepted = (
            route_payload.get("status") == "production_accepted"
            and route_payload.get("solver_status") == "success"
            and route_payload.get("application_status") == "solve_succeeded"
            and route_payload.get("accepted") is True
            and route_payload.get("hessian_approximation") == "exact"
            and route_payload.get("exact_hessian_available") is True
            and int(route_payload.get("eval_h_calls", 0)) > 0
            and postsolve.get("accepted") is True
            and postsolve.get("stability_accepted") is True
            and comparison is not None
            and comparison["max_composition_abs_error"] <= float(thresholds["composition_abs"])
            and comparison["max_phase_fraction_abs_error"] <= float(thresholds["phase_fraction_abs"])
            and float(postsolve.get("material_balance_norm", math.inf)) <= float(thresholds["material_balance_abs"])
            and float(postsolve.get("pressure_consistency_norm", math.inf)) <= float(thresholds["pressure_abs_Pa"])
            and float(postsolve.get("ln_fugacity_consistency_norm", math.inf)) <= float(thresholds["ln_fugacity_abs"])
            and not route_certification_blockers
        )
        if not route_accepted:
            if route_payload.get("status") != "production_accepted":
                blockers.append(f"neutral_lle_route_status_rejected:{route_payload.get('status', 'unknown')}")
            if comparison is None:
                blockers.append("neutral_lle_route_phase_comparison_absent")
            else:
                if comparison["max_composition_abs_error"] > float(thresholds["composition_abs"]):
                    blockers.append("neutral_lle_composition_error_exceeds_threshold")
                if comparison["max_phase_fraction_abs_error"] > float(thresholds["phase_fraction_abs"]):
                    blockers.append("neutral_lle_phase_fraction_error_exceeds_threshold")
            blockers.append("neutral_lle_route_validation_failed")

    complete = fixture["executable"] and route_accepted and not blockers
    route_summary = None
    if route_payload is not None:
        seed_attempts = list(route_payload.get("seed_attempts") or ())
        route_summary = {
            "status": route_payload.get("status"),
            "solver_status": route_payload.get("solver_status"),
            "application_status": route_payload.get("application_status"),
            "accepted": route_payload.get("accepted"),
            "hessian_approximation": route_payload.get("hessian_approximation"),
            "hessian_backend": route_payload.get("hessian_backend"),
            "exact_hessian_available": route_payload.get("exact_hessian_available"),
            "eval_h_calls": route_payload.get("eval_h_calls"),
            "iteration_count": route_payload.get("iteration_count"),
            "seed_attempt_count": len(seed_attempts),
            "postsolve": route_payload.get("postsolve"),
        }
    receipt = native_freshness.build_receipt(
        native_module=_core,
        checker_command=checker_command
        or ["uv", "run", "--no-sync", "python", "scripts/validation/check_neutral_lle_showcase.py"],
    )
    return {
        "case_label": metadata.get("case_label", "neutral_lle_showcase"),
        "family_label": metadata.get("family_label", "PE-Neutral TP Flash"),
        "status": "complete" if complete else "blocked",
        "complete": complete,
        "native_freshness_receipt": native_freshness.receipt_to_jsonable(receipt),
        "fixture": fixture,
        "route": route_summary,
        "comparison": comparison,
        "blockers": list(dict.fromkeys(blockers)),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the source-backed neutral LLE showcase fixture check.")
    parser.add_argument("--case-dir", type=Path, default=DEFAULT_CASE_DIR)
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    parser.add_argument("--debug", action="store_true", help="Expose native Ipopt output and keep more iterations.")
    parser.add_argument(
        "--require-complete",
        dest="require_complete",
        action="store_true",
        help="Return a failing exit code unless the source-backed neutral LLE showcase completes.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    checker_command = sys.argv[:] if argv is None else [
        "uv",
        "run",
        "--no-sync",
        "python",
        "scripts/validation/check_neutral_lle_showcase.py",
        *argv,
    ]
    if args.debug:
        os.environ["EPCSAFT_EQUILIBRIUM_DEBUG"] = "1"
    payload = evaluate_case_dir(
        args.case_dir,
        debug=args.debug,
        show_native_output=args.debug and not args.json,
        redirect_native_output_to_stderr=args.debug and args.json,
        checker_command=checker_command,
    )
    if args.require_complete:
        try:
            native_freshness.require_receipt(dict(payload.get("native_freshness_receipt", {})))
        except ValueError as exc:
            print(str(exc), file=sys.stderr)
            return 2
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(f"{payload['case_label']}: {payload['status']}")
        if payload["blockers"]:
            print("  blockers: " + ", ".join(str(item) for item in payload["blockers"]))
        route = payload.get("route") or {}
        if route:
            print(
                "  route: "
                f"solver={route.get('solver_status')} "
                f"application={route.get('application_status')} "
                f"iterations={route.get('iteration_count')}"
            )
        comparison = payload.get("comparison") or {}
        if comparison:
            print(
                "  comparison: "
                f"composition_abs={comparison.get('max_composition_abs_error')} "
                f"phase_fraction_abs={comparison.get('max_phase_fraction_abs_error')}"
            )
    if args.require_complete and not payload["complete"]:
        print(f"{payload['case_label']} did not complete the neutral LLE showcase check.", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
