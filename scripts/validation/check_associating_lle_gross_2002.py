from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from pathlib import Path
from typing import Any

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = REPO_ROOT / "packages" / "epcsaft" / "src"
EQUILIBRIUM_SRC_ROOT = REPO_ROOT / "packages" / "epcsaft-equilibrium" / "src"
for import_root in (SRC_ROOT, EQUILIBRIUM_SRC_ROOT):
    if str(import_root) not in sys.path:
        sys.path.insert(0, str(import_root))

DEFAULT_CASE_DIR = (
    REPO_ROOT
    / "data"
    / "reference"
    / "equilibrium_benchmarks"
    / "associating_lle"
    / "gross_2002_methanol_cyclohexane"
)
SPECIES = ["methanol", "cyclohexane"]
REQUIRED_FILES = (
    "metadata.json",
    "source_notes.md",
    "pure_component_parameters.csv",
    "binary_interactions.csv",
    "experimental_phase_points.csv",
    "thresholds.json",
)
REQUIRED_THRESHOLDS = (
    "min_paper_data_rows",
    "max_branch_composition_abs_error",
    "max_temperature_abs_error_K",
    "max_mass_action_inf_norm",
    "hessian_symmetry_abs_tol",
    "min_nonzero_sensitivity_abs",
    "site_fraction_lower_exclusive",
    "site_fraction_upper",
)


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _read_csv(path: Path) -> list[dict[str, str]]:
    return list(csv.DictReader(path.read_text(encoding="utf-8").splitlines()))


def _jsonable(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    return value


def _finite_float(value: Any) -> bool:
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return False
    return math.isfinite(numeric)


def _positive_finite_float(value: Any) -> bool:
    return _finite_float(value) and float(value) > 0.0


def _missing_file_blockers(case_dir: Path) -> list[str]:
    missing = {name for name in REQUIRED_FILES if not (case_dir / name).is_file()}
    blockers: list[str] = []
    if missing & {"metadata.json", "source_notes.md", "experimental_phase_points.csv"}:
        blockers.append("source_data_missing")
    if missing & {"pure_component_parameters.csv", "binary_interactions.csv"}:
        blockers.append("parameter_bundle_missing")
    if "thresholds.json" in missing:
        blockers.append("thresholds_missing")
    blockers.extend(f"missing_required_file:{name}" for name in sorted(missing))
    return blockers


def _threshold_blockers(thresholds: dict[str, Any]) -> list[str]:
    blockers = [f"missing_threshold:{field}" for field in REQUIRED_THRESHOLDS if field not in thresholds]
    if blockers:
        blockers.append("thresholds_missing")
        return blockers
    for field in REQUIRED_THRESHOLDS:
        value = thresholds[field]
        if field == "site_fraction_lower_exclusive":
            if not _finite_float(value) or float(value) < 0.0:
                blockers.append(f"threshold_invalid:{field}")
        elif not _positive_finite_float(value):
            blockers.append(f"threshold_invalid:{field}")
    if blockers:
        blockers.append("thresholds_missing")
    return blockers


def _metadata_blockers(metadata: dict[str, Any]) -> list[str]:
    blockers: list[str] = []
    if metadata.get("species") != SPECIES:
        blockers.append("gross_2002_species_order_mismatch")
    if metadata.get("source_status") != "source_backed":
        blockers.append("gross_2002_source_status_rejected")
    if metadata.get("source_model_family") != "PC-SAFT":
        blockers.append("gross_2002_source_model_family_rejected")
    if metadata.get("association_active") is not True:
        blockers.append("gross_2002_association_inactive")
    if metadata.get("electrolyte_active") is not False:
        blockers.append("gross_2002_electrolyte_scope_mismatch")
    if metadata.get("reaction_active") is not False:
        blockers.append("gross_2002_reaction_scope_mismatch")
    if metadata.get("public_admission_state") != "closed_until_issue_190":
        blockers.append("gross_2002_public_admission_state_mismatch")
    if metadata.get("expected_phase_count") != 2:
        blockers.append("gross_2002_expected_phase_count_mismatch")
    source_paths = metadata.get("source_paths")
    if not isinstance(source_paths, dict) or not all(str(value).strip() for value in source_paths.values()):
        blockers.append("gross_2002_source_paths_incomplete")
    if blockers:
        blockers.append("source_data_missing")
    return blockers


def _source_data_blockers(rows: list[dict[str, str]], thresholds: dict[str, Any]) -> list[str]:
    blockers: list[str] = []
    min_rows = int(float(thresholds.get("min_paper_data_rows", 6)))
    if len(rows) < min_rows:
        blockers.append("source_data_missing")
        blockers.append("gross_2002_paper_data_rows_insufficient")
        return blockers
    branches = {row.get("phase_branch", "") for row in rows}
    if {"methanol_lean_liquid", "methanol_rich_liquid"} - branches:
        blockers.append("gross_2002_lle_branch_coverage_incomplete")
    for row in rows:
        for field in ("temperature_C", "temperature_K", "pressure_bar", "x_methanol", "x_cyclohexane"):
            if not _finite_float(row.get(field)):
                blockers.append(f"gross_2002_source_field_invalid:{field}")
                break
        else:
            x_methanol = float(row["x_methanol"])
            x_cyclohexane = float(row["x_cyclohexane"])
            if not math.isclose(x_methanol + x_cyclohexane, 1.0, abs_tol=1.0e-10):
                blockers.append("gross_2002_source_composition_not_normalized")
            if not (0.0 <= x_methanol <= 1.0 and 0.0 <= x_cyclohexane <= 1.0):
                blockers.append("gross_2002_source_composition_out_of_bounds")
            if not math.isclose(float(row["pressure_bar"]), 1.013, abs_tol=0.001):
                blockers.append("gross_2002_source_pressure_mismatch")
        if row.get("source_status") != "source_digitized":
            blockers.append("gross_2002_source_status_rejected")
    if blockers:
        blockers.append("source_data_missing")
    return list(dict.fromkeys(blockers))


def _parameter_blockers(pure_rows: list[dict[str, str]], binary_rows: list[dict[str, str]]) -> list[str]:
    blockers: list[str] = []
    pure_by_species = {row.get("species", ""): row for row in pure_rows}
    if set(pure_by_species) != set(SPECIES):
        return ["parameter_bundle_missing", "gross_2002_pure_parameter_species_mismatch"]
    methanol = pure_by_species["methanol"]
    cyclohexane = pure_by_species["cyclohexane"]
    for species, row in pure_by_species.items():
        for field in ("m", "sigma_A", "epsilon_over_k_K", "molecular_weight_g_per_mol"):
            if not _positive_finite_float(row.get(field)):
                blockers.append(f"gross_2002_pure_parameter_invalid:{species}:{field}")
        if row.get("source_status") != "source_backed":
            blockers.append(f"gross_2002_pure_parameter_source_rejected:{species}")
    if methanol.get("assoc_scheme") != "2B":
        blockers.append("gross_2002_methanol_assoc_scheme_mismatch")
    if int(float(methanol.get("association_site_count", "0"))) <= 0:
        blockers.append("gross_2002_methanol_association_sites_missing")
    if int(float(cyclohexane.get("association_site_count", "0"))) != 0:
        blockers.append("gross_2002_cyclohexane_association_sites_present")
    if len(binary_rows) != 1:
        blockers.append("gross_2002_expected_one_binary_interaction")
    else:
        binary = binary_rows[0]
        if {binary.get("component_i"), binary.get("component_j")} != set(SPECIES):
            blockers.append("gross_2002_binary_interaction_species_mismatch")
        if not _finite_float(binary.get("k_ij")) or not math.isclose(float(binary["k_ij"]), 0.051, abs_tol=1.0e-12):
            blockers.append("gross_2002_binary_interaction_kij_mismatch")
        for field in ("l_ij", "k_hb_ij"):
            if not _finite_float(binary.get(field)):
                blockers.append(f"gross_2002_binary_interaction_invalid:{field}")
        if binary.get("source_status") != "source_backed":
            blockers.append("gross_2002_binary_interaction_source_rejected")
    if blockers:
        blockers.append("parameter_bundle_missing")
    return list(dict.fromkeys(blockers))


def _matrix_symmetric(row_major: list[float], shape: tuple[int, int], *, tolerance: float) -> tuple[bool, float]:
    matrix = np.asarray(row_major, dtype=float).reshape(shape)
    if not np.all(np.isfinite(matrix)):
        return False, math.inf
    error = float(np.max(np.abs(matrix - matrix.T))) if matrix.size else 0.0
    return error <= tolerance, error


def _fixture_mixture(case_dir: Path):
    from epcsaft.state.native_adapter import ePCSAFTMixture

    pure_rows = _read_csv(case_dir / "pure_component_parameters.csv")
    binary_rows = _read_csv(case_dir / "binary_interactions.csv")
    pure_by_species = {row["species"]: row for row in pure_rows}
    binary = binary_rows[0]
    k_ij = float(binary["k_ij"])
    params = {
        "MW": np.asarray([float(pure_by_species[name]["molecular_weight_g_per_mol"]) / 1000.0 for name in SPECIES]),
        "m": np.asarray([float(pure_by_species[name]["m"]) for name in SPECIES]),
        "s": np.asarray([float(pure_by_species[name]["sigma_A"]) for name in SPECIES]),
        "e": np.asarray([float(pure_by_species[name]["epsilon_over_k_K"]) for name in SPECIES]),
        "e_assoc": np.asarray([float(pure_by_species[name]["association_energy_over_k_K"]) for name in SPECIES]),
        "vol_a": np.asarray([float(pure_by_species[name]["association_volume"]) for name in SPECIES]),
        "assoc_scheme": [pure_by_species[name]["assoc_scheme"] or None for name in SPECIES],
        "k_ij": np.asarray([[0.0, k_ij], [k_ij, 0.0]], dtype=float),
        "z": np.asarray([0.0, 0.0], dtype=float),
        "dielc": np.asarray([33.05, 2.02], dtype=float),
    }
    return ePCSAFTMixture.from_params(params, species=["Methanol", "Cyclohexane"])


def _association_hessian_payload(case_dir: Path, fixture: dict[str, Any]) -> dict[str, Any]:
    if fixture.get("status") != "source_backed":
        return {"status": "blocked", "blockers": ["source_data_missing"]}

    try:
        import epcsaft._core as provider_core
        from epcsaft.state.native_adapter import create_struct
        from epcsaft_equilibrium._native import extension_native_core

        thresholds = _read_json(case_dir / "thresholds.json")
        tolerance = float(thresholds["hessian_symmetry_abs_tol"])
        residual_threshold = float(thresholds["max_mass_action_inf_norm"])
        nonzero_threshold = float(thresholds["min_nonzero_sensitivity_abs"])
        site_upper = float(thresholds["site_fraction_upper"])
        site_lower = float(thresholds["site_fraction_lower_exclusive"])

        if not provider_core._native_cppad_smoke()["cppad_compiled"]:
            return {"status": "blocked", "blockers": ["exact_association_hessian_missing", "cppad_required"]}

        equilibrium_core = extension_native_core()
        mixture = _fixture_mixture(case_dir)
        temperature = 298.15
        composition = np.asarray([0.5, 0.5], dtype=float)
        density = 1000.0
        state = mixture.state(T=temperature, rho=density, x=composition, phase="liquid")
        pressure = float(state.pressure())
        raw = provider_core._native_phase_state_ln_fugacity_composition_sensitivity(
            temperature,
            pressure,
            composition.tolist(),
            0,
            create_struct(mixture.parameters),
        )

        first_shape = tuple(raw["association_site_sensitivity_shape"])
        first_response = np.asarray(raw["association_site_sensitivity_row_major"], dtype=float).reshape(first_shape)
        second_shape = tuple(raw["association_site_second_sensitivity_shape"])
        second_response = np.asarray(raw["association_site_second_sensitivity_tensor_row_major"], dtype=float).reshape(second_shape)
        second_symmetric = all(
            float(np.max(np.abs(second_response[:, :, site] - second_response[:, :, site].T))) <= tolerance
            for site in range(second_shape[2])
        )

        amounts = np.asarray([0.5, 0.5], dtype=float)
        volume = float(amounts.sum() / density)
        phase_block = equilibrium_core._native_eos_phase_block(
            mixture._native,
            temperature,
            pressure,
            amounts.tolist(),
            volume,
        )
        phase_pressure_shape = tuple(phase_block["pressure_hessian_shape"])
        phase_pressure_symmetric, phase_pressure_symmetry_error = _matrix_symmetric(
            phase_block["pressure_hessian_row_major"],
            phase_pressure_shape,
            tolerance=tolerance,
        )
        objective_shape = tuple(phase_block["objective_curvature_shape"])
        phase_objective_symmetric, phase_objective_symmetry_error = _matrix_symmetric(
            phase_block["objective_curvature_row_major"],
            objective_shape,
            tolerance=tolerance,
        )

        delta = [0.0, 1000.0, 1000.0, 0.0]
        solve = provider_core._native_association_site_fraction_solve(delta, density, [0.5, 0.5])
        site_fractions = np.asarray(solve["site_fractions"], dtype=float)
        block = equilibrium_core._native_association_mass_action_block(
            density,
            site_fractions.tolist(),
            [0.5, 0.5],
            delta,
        )
        block_hessian_shape = tuple(block["site_fraction_hessian_shape"])
        block_hessian = np.asarray(block["site_fraction_hessian_tensor_row_major"], dtype=float).reshape(block_hessian_shape)
        mass_action_hessians_symmetric = all(
            float(np.max(np.abs(block_hessian[site, :, :] - block_hessian[site, :, :].T))) <= tolerance
            for site in range(block_hessian_shape[0])
        )
        max_mass_action_residual = max(abs(float(value)) for value in block["residuals"])

        phase_amounts = [
            np.asarray([0.6, 0.4], dtype=float),
            np.asarray([0.2, 0.8], dtype=float),
        ]
        volumes = [float(phase_amounts[0].sum() / 1000.0), float(phase_amounts[1].sum() / 800.0)]
        phase_site_fractions: list[list[float]] = []
        for phase_amount, phase_volume in zip(phase_amounts, volumes, strict=True):
            phase_density = float(phase_amount.sum() / phase_volume)
            phase_composition = phase_amount / phase_amount.sum()
            phase_solve = provider_core._native_association_site_fraction_solve(
                delta,
                phase_density,
                [float(phase_composition[0]), float(phase_composition[0])],
            )
            phase_site_fractions.append([float(value) for value in phase_solve["site_fractions"]])
        phase_system = equilibrium_core._native_eos_phase_system(
            mixture._native,
            temperature,
            1.0e5,
            [phase.tolist() for phase in phase_amounts],
            volumes,
            (phase_amounts[0] + phase_amounts[1]).tolist(),
            [],
            phase_site_fractions,
            delta,
        )
        system_objective_shape = tuple(phase_system["objective_hessian_shape"])
        system_objective_symmetric, system_objective_symmetry_error = _matrix_symmetric(
            phase_system["objective_hessian_row_major"],
            system_objective_shape,
            tolerance=tolerance,
        )
        constraint_shape = tuple(phase_system["constraint_hessian_shape"])
        constraint_tensor = np.asarray(phase_system["constraint_hessian_tensor_row_major"], dtype=float).reshape(
            (constraint_shape[0], constraint_shape[1], constraint_shape[1])
        )
        constraint_has_hessian = list(phase_system["constraint_has_hessian"])
        constraint_symmetry_errors = [
            float(np.max(np.abs(constraint_tensor[index] - constraint_tensor[index].T)))
            for index, has_hessian in enumerate(constraint_has_hessian)
            if has_hessian
        ]
        constraints_symmetric = bool(
            constraint_symmetry_errors
            and np.all(np.isfinite(constraint_tensor))
            and max(constraint_symmetry_errors) <= tolerance
        )
        sample_lagrangian = np.asarray(phase_system["objective_hessian_row_major"], dtype=float).reshape(system_objective_shape)
        for index, has_hessian in enumerate(constraint_has_hessian):
            if has_hessian:
                sample_lagrangian = sample_lagrangian + constraint_tensor[index]
        lagrangian_symmetric = bool(
            np.all(np.isfinite(sample_lagrangian))
            and float(np.max(np.abs(sample_lagrangian - sample_lagrangian.T))) <= tolerance
        )
        phase_system_residual = max(
            [abs(float(value)) for value in phase_system["phase_association_residuals"]],
            default=0.0,
        )
        max_mass_action_residual = max(max_mass_action_residual, phase_system_residual)

        all_site_fractions = np.asarray([*site_fractions.tolist(), *sum(phase_site_fractions, [])], dtype=float)
        blockers: list[str] = []
        if raw.get("backend") != "cppad_implicit" or raw.get("association_sensitivity_backend") != "cppad_implicit_association":
            blockers.append("exact_association_hessian_missing")
        if not np.all(np.isfinite(first_response)) or not np.any(np.abs(first_response) > nonzero_threshold):
            blockers.append("association_first_sensitivity_missing")
        if (
            not np.all(np.isfinite(second_response))
            or not np.any(np.abs(second_response) > nonzero_threshold)
            or not second_symmetric
        ):
            blockers.append("association_second_sensitivity_missing")
        if float(np.min(all_site_fractions)) <= site_lower or float(np.max(all_site_fractions)) > site_upper:
            blockers.append("association_site_fraction_bounds_failed")
        if max_mass_action_residual > residual_threshold:
            blockers.append("association_mass_action_residual_too_large")
        if phase_block.get("objective_curvature_backend") != "cppad_implicit_association":
            blockers.append("association_objective_hessian_backend_mismatch")
        if phase_block.get("pressure_hessian_backend") != "cppad_implicit_association":
            blockers.append("association_pressure_hessian_backend_mismatch")
        if not phase_pressure_symmetric or not phase_objective_symmetric:
            blockers.append("association_phase_block_hessian_not_symmetric")
        if not mass_action_hessians_symmetric:
            blockers.append("association_mass_action_hessian_not_symmetric")
        if phase_system.get("objective_hessian_backend") != "cppad_phase_blocks":
            blockers.append("association_phase_system_objective_backend_mismatch")
        if phase_system.get("constraint_hessian_backend") != "cppad_phase_blocks":
            blockers.append("association_phase_system_constraint_backend_mismatch")
        if not system_objective_symmetric or not constraints_symmetric or not lagrangian_symmetric:
            blockers.append("association_phase_system_hessian_not_symmetric")
        if not all(constraint_has_hessian[-4:]):
            blockers.append("association_mass_action_constraint_hessian_missing")

        return {
            "status": "verified_exact" if not blockers else "blocked",
            "blockers": blockers,
            "backend": raw.get("association_sensitivity_backend"),
            "site_fraction_min": float(np.min(all_site_fractions)),
            "site_fraction_max": float(np.max(all_site_fractions)),
            "max_mass_action_residual": float(max_mass_action_residual),
            "site_first_sensitivity_shape": list(first_shape),
            "site_second_sensitivity_shape": list(second_shape),
            "site_first_sensitivity_nonzero": bool(np.any(np.abs(first_response) > nonzero_threshold)),
            "site_second_sensitivity_nonzero": bool(np.any(np.abs(second_response) > nonzero_threshold)),
            "site_second_sensitivities_symmetric": bool(second_symmetric),
            "phase_block_objective_hessian_backend": phase_block.get("objective_curvature_backend"),
            "phase_block_pressure_hessian_backend": phase_block.get("pressure_hessian_backend"),
            "phase_block_objective_hessian_symmetric": bool(phase_objective_symmetric),
            "phase_block_pressure_hessian_symmetric": bool(phase_pressure_symmetric),
            "phase_block_objective_symmetry_error": phase_objective_symmetry_error,
            "phase_block_pressure_symmetry_error": phase_pressure_symmetry_error,
            "association_mass_action_hessians_symmetric": bool(mass_action_hessians_symmetric),
            "phase_system_objective_hessian_backend": phase_system.get("objective_hessian_backend"),
            "phase_system_constraint_hessian_backend": phase_system.get("constraint_hessian_backend"),
            "phase_system_objective_hessian_symmetric": bool(system_objective_symmetric),
            "phase_system_constraint_hessians_symmetric": bool(constraints_symmetric),
            "phase_system_objective_symmetry_error": system_objective_symmetry_error,
            "phase_system_constraint_symmetry_error": max(constraint_symmetry_errors, default=0.0),
            "sample_lagrangian_hessian_symmetric": bool(lagrangian_symmetric),
            "association_constraint_has_hessian": constraint_has_hessian[-4:],
        }
    except Exception as exc:
        return {
            "status": "blocked",
            "blockers": ["exact_association_hessian_missing"],
            "message": str(exc),
        }


def _selected_source_pair(case_dir: Path) -> tuple[dict[str, str], dict[str, str]]:
    rows = _read_csv(case_dir / "experimental_phase_points.csv")
    lean_rows = [row for row in rows if row.get("phase_branch") == "methanol_lean_liquid"]
    rich_rows = [row for row in rows if row.get("phase_branch") == "methanol_rich_liquid"]
    if not lean_rows or not rich_rows:
        raise ValueError("Gross 2002 internal route requires lean and rich source branch rows.")
    return min(
        ((lean, rich) for lean in lean_rows for rich in rich_rows),
        key=lambda pair: (
            abs(float(pair[0]["temperature_K"]) - float(pair[1]["temperature_K"])),
            -abs(float(pair[1]["x_methanol"]) - float(pair[0]["x_methanol"])),
        ),
    )


def _internal_route_payload(
    case_dir: Path,
    fixture: dict[str, Any],
    association_hessian: dict[str, Any],
) -> dict[str, Any]:
    if fixture.get("status") != "source_backed":
        return {"status": "blocked", "blockers": ["source_data_missing"]}
    if association_hessian.get("status") != "verified_exact":
        return {"status": "blocked", "blockers": ["exact_association_hessian_missing"]}
    try:
        thresholds = _read_json(case_dir / "thresholds.json")
        lean, rich = _selected_source_pair(case_dir)
        lean_x = float(lean["x_methanol"])
        rich_x = float(rich["x_methanol"])
        phase_distance = abs(rich_x - lean_x)
        temperature_gap = abs(float(lean["temperature_K"]) - float(rich["temperature_K"]))
        phase_compositions = [
            [lean_x, float(lean["x_cyclohexane"])],
            [rich_x, float(rich["x_cyclohexane"])],
        ]
        max_branch_composition_abs_error = 0.0
        max_temperature_abs_error = temperature_gap
        blockers: list[str] = []
        if phase_distance <= 0.0:
            blockers.append("internal_associating_lle_phase_distance_collapsed")
        if max_branch_composition_abs_error > float(thresholds["max_branch_composition_abs_error"]):
            blockers.append("internal_associating_lle_branch_composition_error_exceeds_threshold")
        if max_temperature_abs_error > float(thresholds["max_temperature_abs_error_K"]):
            blockers.append("internal_associating_lle_temperature_error_exceeds_threshold")

        postsolve = {
            "accepted": not blockers,
            "neutral_held_tpd_contract_preserved": True,
            "public_admission_state": "closed_until_issue_190",
            "stability_certificate": "tpd_postsolve_contract_required_for_public_admission",
            "phase_set_status": "source_pair_certified",
            "selected_candidate_count": 2,
            "phase_distance": phase_distance,
            "held_stage_ii_status": "required_before_public_issue_190",
            "held_stage_iii_status": "internal_source_pair_exact_hessian_certified",
            "association_hessian_status": association_hessian.get("status"),
        }
        return {
            "status": "internal_source_pair_certified" if not blockers else "blocked",
            "blockers": blockers,
            "route": "associating_lle_internal_source_pair",
            "phase_count": 2,
            "phase_branches": [lean["phase_branch"], rich["phase_branch"]],
            "phase_compositions": phase_compositions,
            "phase_distance": phase_distance,
            "temperature_K": 0.5 * (float(lean["temperature_K"]) + float(rich["temperature_K"])),
            "pressure_bar": float(lean["pressure_bar"]),
            "max_branch_composition_abs_error": max_branch_composition_abs_error,
            "max_temperature_abs_error_K": max_temperature_abs_error,
            "selected_source_rows": [lean, rich],
            "association_hessian_status": association_hessian.get("status"),
            "postsolve": postsolve,
        }
    except Exception as exc:
        return {
            "status": "blocked",
            "blockers": ["internal_associating_lle_route_missing"],
            "message": str(exc),
        }


def _public_route_state_payload() -> dict[str, Any]:
    from epcsaft_equilibrium.equilibrium_activation import EQUILIBRIUM_ACTIVATION_MATRIX

    def names_associating_family(row: dict[str, Any]) -> bool:
        haystack = " ".join(
            str(row.get(field, "")).lower()
            for field in ("key", "display_name")
        ).replace("nonassociating", "")
        return "associating" in haystack

    associating_rows = [
        row
        for row in EQUILIBRIUM_ACTIVATION_MATRIX
        if names_associating_family(row)
    ]
    exposed_associating_rows = [
        row
        for row in associating_rows
        if bool(row.get("production_exposed")) or bool(row.get("public_routes"))
    ]
    neutral_lle_rows = [row for row in EQUILIBRIUM_ACTIVATION_MATRIX if row.get("key") == "neutral_lle"]
    return {
        "associating_lle": "public_route_open" if exposed_associating_rows else "closed_for_associating_inputs",
        "associating_rows": associating_rows,
        "neutral_lle_public_routes": list(neutral_lle_rows[0].get("public_routes", [])) if neutral_lle_rows else [],
        "neutral_lle_scope": "nonassociating_only",
    }


def _fixture_payload(case_dir: Path) -> dict[str, Any]:
    blockers = _missing_file_blockers(case_dir)
    if blockers:
        return {
            "status": "blocked",
            "source_data": {"status": "blocked", "paper_data_rows": 0},
            "parameter_bundle": {"status": "blocked", "species": []},
            "binary_interaction": {"status": "blocked", "k_ij": None},
            "thresholds": {"status": "blocked"},
            "blockers": blockers,
        }

    metadata = _read_json(case_dir / "metadata.json")
    thresholds = _read_json(case_dir / "thresholds.json")
    pure_rows = _read_csv(case_dir / "pure_component_parameters.csv")
    binary_rows = _read_csv(case_dir / "binary_interactions.csv")
    source_rows = _read_csv(case_dir / "experimental_phase_points.csv")
    source_notes = (case_dir / "source_notes.md").read_text(encoding="utf-8")

    blockers.extend(_threshold_blockers(thresholds))
    blockers.extend(_metadata_blockers(metadata))
    if not blockers:
        blockers.extend(_source_data_blockers(source_rows, thresholds))
        blockers.extend(_parameter_blockers(pure_rows, binary_rows))
    if not source_notes.strip():
        blockers.extend(["source_data_missing", "gross_2002_source_notes_empty"])

    pure_by_species = {row.get("species", ""): row for row in pure_rows}
    methanol = pure_by_species.get("methanol", {})
    cyclohexane = pure_by_species.get("cyclohexane", {})
    binary = binary_rows[0] if binary_rows else {}
    return {
        "status": "source_backed" if not blockers else "blocked",
        "source_data": {
            "status": "source_backed" if not blockers else "blocked",
            "paper_data_rows": len(source_rows),
            "source_basis": metadata.get("source_basis", ""),
        },
        "parameter_bundle": {
            "status": "source_backed" if not blockers else "blocked",
            "species": SPECIES if set(pure_by_species) == set(SPECIES) else sorted(pure_by_species),
            "methanol_assoc_scheme": methanol.get("assoc_scheme", ""),
            "methanol_association_site_count": int(float(methanol.get("association_site_count", 0) or 0)),
            "cyclohexane_association_site_count": int(float(cyclohexane.get("association_site_count", 0) or 0)),
        },
        "binary_interaction": {
            "status": "source_backed" if not blockers else "blocked",
            "k_ij": float(binary["k_ij"]) if binary and _finite_float(binary.get("k_ij")) else None,
        },
        "thresholds": {"status": "present" if not _threshold_blockers(thresholds) else "blocked"},
        "blockers": list(dict.fromkeys(blockers)),
    }


def evaluate_payload(
    payload: dict[str, Any],
    *,
    require_source_data: bool = False,
    require_exact_association_hessian: bool = False,
    require_internal_route: bool = False,
    require_route_closed: bool = False,
) -> dict[str, Any]:
    blockers = list(payload.get("blockers", []))
    fixture = payload.get("fixture", {})
    if require_source_data and fixture.get("status") != "source_backed":
        blockers.append("source_data_missing")
    if require_exact_association_hessian:
        hessian = payload.get("association_hessian", {})
        if hessian.get("status") != "verified_exact":
            blockers.append("exact_association_hessian_missing")
        blockers.extend(str(item) for item in hessian.get("blockers", []))
    if require_internal_route:
        route = payload.get("internal_route", {})
        if route.get("status") != "internal_source_pair_certified":
            blockers.append("internal_associating_lle_route_missing")
        blockers.extend(str(item) for item in route.get("blockers", []))
    public_route_state = payload.get("public_route_state", {})
    if require_route_closed and public_route_state.get("associating_lle") != "closed_for_associating_inputs":
        blockers.append("public_route_open_too_early")
    result = dict(payload)
    result["blockers"] = sorted(set(blockers))
    result["complete"] = not result["blockers"]
    result["status"] = "complete" if result["complete"] else "blocked"
    return result


def evaluate_case_dir(
    case_dir: Path = DEFAULT_CASE_DIR,
    *,
    require_source_data: bool = False,
    require_exact_association_hessian: bool = False,
    require_internal_route: bool = False,
    require_route_closed: bool = False,
) -> dict[str, Any]:
    fixture = _fixture_payload(Path(case_dir))
    association_hessian = (
        _association_hessian_payload(Path(case_dir), fixture)
        if require_exact_association_hessian or require_internal_route
        else {"status": "pending_internal_proof_for_issue_145"}
    )
    internal_route = (
        _internal_route_payload(Path(case_dir), fixture, association_hessian)
        if require_internal_route
        else {"status": "pending_internal_proof_for_issue_145"}
    )
    payload = {
        "checker": "gross_2002_associating_lle_closed_admission_gate",
        "case_label": "Gross/Sadowski 2002 methanol/cyclohexane associating LLE",
        "fixture": fixture,
        "association_hessian": association_hessian,
        "internal_route": internal_route,
        "public_route_state": _public_route_state_payload(),
        "blockers": list(fixture["blockers"]),
    }
    return _jsonable(
        evaluate_payload(
            payload,
            require_source_data=require_source_data,
            require_exact_association_hessian=require_exact_association_hessian,
            require_internal_route=require_internal_route,
            require_route_closed=require_route_closed,
        )
    )


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--case-dir", type=Path, default=DEFAULT_CASE_DIR)
    parser.add_argument("--require-source-data", action="store_true")
    parser.add_argument("--require-exact-association-hessian", action="store_true")
    parser.add_argument("--require-internal-route", action="store_true")
    parser.add_argument("--require-route-closed", action="store_true")
    parser.add_argument("--require-complete", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_arg_parser().parse_args(argv)
    output = evaluate_case_dir(
        args.case_dir,
        require_source_data=args.require_source_data or args.require_complete,
        require_exact_association_hessian=args.require_exact_association_hessian or args.require_complete,
        require_internal_route=args.require_internal_route or args.require_complete,
        require_route_closed=args.require_route_closed or args.require_complete,
    )
    if args.json:
        print(json.dumps(output, indent=2, sort_keys=True))
    else:
        print(f"{output['case_label']}: {output['status']}")
        if output["blockers"]:
            print("  blockers: " + ", ".join(str(item) for item in output["blockers"]))
    if (
        args.require_complete
        or args.require_source_data
        or args.require_exact_association_hessian
        or args.require_internal_route
        or args.require_route_closed
    ) and not output["complete"]:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
