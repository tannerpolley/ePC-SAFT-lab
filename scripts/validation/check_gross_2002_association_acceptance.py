from __future__ import annotations

import argparse
import csv
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
    if str(import_root) not in sys.path:
        sys.path.insert(0, str(import_root))

MANIFEST_PATH = REPO_ROOT / "analyses" / "paper_validation" / "2002_gross" / "shared" / "gross_2002_association_acceptance_manifest.json"
SUMMARY_DIR = REPO_ROOT / "analyses" / "paper_validation" / "2002_gross" / "shared" / "results"
REQUIRED_ACCEPTED_FIGURES = ("figure_01", "figure_08", "figure_10")
SOURCE_REQUIREMENT_FIGURES = ("figure_02", "figure_03", "figure_04", "figure_05", "figure_06", "figure_07", "figure_09")
VISUAL_ARTIFACT_KEYS = ("source_csv", "model_csv", "plotted_csv", "summary_json", "png", "svg", "pdf")
FIGURE01_ARTIFACT_KEYS = ("source_csv", "fit_statistics_csv")
FIGURE_MISSING_BLOCKERS = {
    "figure_01": "gross_2002_figure_01_pure_association_statistics_missing",
    "figure_08": "gross_2002_figure_08_campaign_evidence_missing",
    "figure_10": "gross_2002_figure_10_source_data_missing",
}


def _jsonable(value: Any) -> Any:
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, Path):
        return value.as_posix()
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    return value


def _repo_path(path: str | Path) -> Path:
    path = Path(path)
    if path.is_absolute():
        return path
    return REPO_ROOT / path


def _relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError:
        return path.resolve().as_posix()


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _read_csv(path: Path) -> list[dict[str, str]]:
    return list(csv.DictReader(path.read_text(encoding="utf-8").splitlines()))


def _write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fieldnames})


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(_jsonable(payload), indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _artifact_paths(figure_id: str, stem: str, source_csv: str | None = None) -> dict[str, str]:
    result_dir = REPO_ROOT / "analyses" / "paper_validation" / "2002_gross" / "figures" / figure_id / "results"
    if figure_id == "figure_01":
        return {
            "source_csv": _relative(_repo_path(source_csv)) if source_csv else "",
            "fit_statistics_csv": _relative(result_dir / "association_fit_statistics.csv"),
        }
    return {
        "source_csv": _relative(_repo_path(source_csv)) if source_csv else "",
        "model_csv": _relative(result_dir / f"{stem}_model_curve.csv"),
        "plotted_csv": _relative(result_dir / f"{stem}_plotted_data.csv"),
        "summary_json": _relative(result_dir / f"{stem}_association_summary.json"),
        "png": _relative(result_dir / f"{stem}_association_mirror.png"),
        "svg": _relative(result_dir / f"{stem}_association_mirror.svg"),
        "pdf": _relative(result_dir / f"{stem}_association_mirror.pdf"),
    }


def _path_exists(path_value: Any) -> bool:
    if not str(path_value).strip():
        return False
    return _repo_path(str(path_value)).is_file()


def _figure_artifact_blockers(record: dict[str, Any]) -> list[str]:
    figure_id = str(record.get("figure_id", "unknown"))
    artifacts = record.get("artifacts", {})
    blockers: list[str] = []
    if not isinstance(artifacts, dict):
        return [f"gross_2002_{figure_id}_artifacts_missing"]
    artifact_keys = FIGURE01_ARTIFACT_KEYS if figure_id == "figure_01" else VISUAL_ARTIFACT_KEYS
    for key in artifact_keys:
        if not _path_exists(artifacts.get(key, "")):
            blockers.append(f"gross_2002_{figure_id}_{key}_missing")
    return blockers


def _figure_record_by_id(payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    records = payload.get("figure_records", [])
    if not isinstance(records, list):
        return {}
    return {str(record.get("figure_id", "")): record for record in records if isinstance(record, dict)}


def evaluate_payload(
    payload: dict[str, Any],
    *,
    require_complete: bool = False,
    require_exact_association_hessian: bool = False,
    require_fresh_native: bool = False,
) -> dict[str, Any]:
    blockers = [str(item) for item in payload.get("blockers", [])]
    by_figure = _figure_record_by_id(payload)
    accepted_figures: list[str] = []
    source_requirement_figures: list[str] = []

    for figure_id, record in sorted(by_figure.items()):
        role = str(record.get("role", ""))
        status = str(record.get("status", ""))
        counts = bool(record.get("counts_toward_completion"))
        if figure_id == "figure_02" and (counts or role != "source_requirement"):
            blockers.append("gross_2002_figure_02_source_identity_unresolved")
        if role == "source_requirement":
            source_requirement_figures.append(figure_id)
            if counts:
                blockers.append(f"gross_2002_{figure_id}_source_requirement_counted_as_evidence")
            requirements = record.get("source_requirements", [])
            if not isinstance(requirements, list) or not requirements:
                blockers.append(f"gross_2002_{figure_id}_source_requirements_missing")
            continue
        if counts:
            accepted_figures.append(figure_id)
            if status != "accepted":
                blockers.append(f"gross_2002_{figure_id}_not_accepted")
            source_count = int(record.get("source_point_count", 0) or 0)
            if source_count <= 0:
                blockers.append(f"gross_2002_{figure_id}_source_data_missing")
            if require_complete:
                blockers.extend(_figure_artifact_blockers(record))
            if figure_id == "figure_01" and record.get("pure_association_sanity", {}).get("status") != "verified":
                blockers.append("gross_2002_figure_01_pure_association_statistics_missing")
            if figure_id == "figure_10" and record.get("cross_association_stress", {}).get("status") != "verified":
                blockers.append("gross_2002_figure_10_cross_association_stress_missing")

    if require_complete:
        for figure_id in REQUIRED_ACCEPTED_FIGURES:
            record = by_figure.get(figure_id)
            if not record or not bool(record.get("counts_toward_completion")) or record.get("status") != "accepted":
                blockers.append(FIGURE_MISSING_BLOCKERS[figure_id])
        for figure_id in SOURCE_REQUIREMENT_FIGURES:
            record = by_figure.get(figure_id)
            if not record or record.get("role") != "source_requirement":
                blockers.append(f"gross_2002_{figure_id}_source_requirement_missing")
        summary_artifacts = payload.get("summary_artifacts", {})
        if not isinstance(summary_artifacts, dict):
            blockers.append("gross_2002_campaign_summary_missing")
        else:
            for key in ("json", "csv"):
                if not _path_exists(summary_artifacts.get(key, "")):
                    blockers.append(f"gross_2002_campaign_summary_{key}_missing")

    if require_exact_association_hessian:
        for figure_id in ("figure_08", "figure_10"):
            record = by_figure.get(figure_id, {})
            hessian = record.get("exact_association_hessian", {})
            if hessian.get("status") != "verified_exact":
                blockers.append(f"gross_2002_{figure_id}_exact_association_hessian_missing")
            blockers.extend(str(item) for item in hessian.get("blockers", []))

    if require_fresh_native:
        receipt = payload.get("native_freshness_receipt", {})
        try:
            from scripts.validation import native_freshness

            native_freshness.require_receipt(dict(receipt))
        except Exception:
            blockers.append("gross_2002_native_freshness_receipt_missing")

    unique_blockers = sorted(set(blockers))
    result = dict(payload)
    result["accepted_figures"] = sorted(set(accepted_figures))
    result["source_requirement_figures"] = sorted(set(source_requirement_figures))
    result["blockers"] = unique_blockers
    result["complete"] = not unique_blockers
    result["status"] = "complete" if result["complete"] else "blocked"
    return _jsonable(result)


def _load_manifest(manifest_path: Path) -> dict[str, Any]:
    return _read_json(manifest_path)


def _manifest_figure(manifest: dict[str, Any], figure_id: str) -> dict[str, Any]:
    figures = manifest.get("figures", [])
    for row in figures:
        if row.get("figure_id") == figure_id:
            return dict(row)
    raise KeyError(figure_id)


def _row_count(csv_path: str | None) -> int:
    if not csv_path or not _repo_path(csv_path).is_file():
        return 0
    return len(_read_csv(_repo_path(csv_path)))


def _source_requirement_record(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "figure_id": row["figure_id"],
        "role": "source_requirement",
        "status": "source_requirement_recorded",
        "counts_toward_completion": False,
        "source_image": row.get("source_image", ""),
        "source_data_home": row.get("source_data_home", []),
        "route_family": row.get("route_family", ""),
        "source_requirements": list(row.get("source_requirements", [])),
    }


def _figure01_record(row: dict[str, Any]) -> dict[str, Any]:
    source_csv = row.get("source_csv", "")
    stem = row.get("result_stem", "association")
    source_rows = _read_csv(_repo_path(source_csv)) if _repo_path(source_csv).is_file() else []
    components = {source_row.get("component", "") for source_row in source_rows}
    status = "accepted" if {"methanol", "1-pentanol", "1-nonanol"} <= components else "blocked"
    return {
        "figure_id": "figure_01",
        "role": "accepted_sanity_gate",
        "status": status,
        "counts_toward_completion": True,
        "source_point_count": len(source_rows),
        "source_image": row.get("source_image", ""),
        "source_data_home": row.get("source_data_home", []),
        "route_family": row.get("route_family", ""),
        "artifacts": _artifact_paths("figure_01", stem, source_csv),
        "pure_association_sanity": {
            "status": "verified" if status == "accepted" else "blocked",
            "components": sorted(components),
            "source": row.get("parameter_sources", []),
        },
    }


def _figure08_record(row: dict[str, Any], *, require_exact: bool) -> dict[str, Any]:
    from scripts.validation import check_associating_lle_gross_2002 as gross_2002

    stem = row.get("result_stem", "gross_2002_figure_08_association_mirror")
    source_csv = row.get("source_csv", "")
    proof = gross_2002.evaluate_case_dir(
        gross_2002.DEFAULT_CASE_DIR,
        require_source_data=True,
        require_exact_association_hessian=require_exact,
        require_internal_route=require_exact,
        require_route_closed=False,
    )
    hessian = proof.get("association_hessian", {})
    status = "accepted" if proof.get("fixture", {}).get("status") == "source_backed" else "blocked"
    if require_exact and hessian.get("status") != "verified_exact":
        status = "blocked"
    return {
        "figure_id": "figure_08",
        "role": "accepted_hard_gate",
        "status": status,
        "counts_toward_completion": True,
        "source_point_count": int(proof.get("fixture", {}).get("source_data", {}).get("paper_data_rows", 0) or 0),
        "source_image": row.get("source_image", ""),
        "route_family": row.get("route_family", ""),
        "artifacts": _artifact_paths("figure_08", stem, source_csv),
        "exact_association_hessian": hessian,
        "existing_checker": "scripts/validation/check_associating_lle_gross_2002.py",
    }


def _parse_table1_components(names: tuple[str, ...]) -> dict[str, dict[str, float]]:
    rows = list(csv.reader((REPO_ROOT / "analyses" / "paper_validation" / "2002_gross" / "tables" / "table_001" / "table_001.csv").read_text(encoding="utf-8").splitlines()))
    wanted: dict[str, dict[str, float]] = {}
    for row in rows:
        if row and row[0] in names and len(row) > 6 and str(row[1]).strip():
            wanted[row[0]] = {
                "molecular_weight_g_per_mol": float(row[1]),
                "m": float(row[2]),
                "sigma_A": float(row[3]),
                "epsilon_over_k_K": float(row[4]),
                "association_volume": float(row[5]),
                "association_energy_over_k_K": float(row[6]),
            }
    missing = sorted(set(names) - set(wanted))
    if missing:
        raise ValueError("Gross 2002 Table 1 rows missing: " + ", ".join(missing))
    return wanted


def _parse_table2_kij(binary_system: str) -> float:
    rows = list(csv.reader((REPO_ROOT / "analyses" / "paper_validation" / "2002_gross" / "tables" / "table_002" / "table_002.csv").read_text(encoding="utf-8").splitlines()))
    for row in rows:
        if row and row[0] == binary_system:
            return float(row[1])
    raise ValueError(f"Gross 2002 Table 2 row missing: {binary_system}")


def _matrix_symmetric(row_major: list[float], shape: tuple[int, int], *, tolerance: float) -> tuple[bool, float]:
    matrix = np.asarray(row_major, dtype=float).reshape(shape)
    if not np.all(np.isfinite(matrix)):
        return False, math.inf
    error = float(np.max(np.abs(matrix - matrix.T))) if matrix.size else 0.0
    return error <= tolerance, error


def _figure10_mixture():
    from epcsaft.state.native_adapter import ePCSAFTMixture

    names = ("water", "1-pentanol")
    pure = _parse_table1_components(names)
    kij = _parse_table2_kij("water-1-pentanol")
    params = {
        "MW": np.asarray([pure[name]["molecular_weight_g_per_mol"] / 1000.0 for name in names], dtype=float),
        "m": np.asarray([pure[name]["m"] for name in names], dtype=float),
        "s": np.asarray([pure[name]["sigma_A"] for name in names], dtype=float),
        "e": np.asarray([pure[name]["epsilon_over_k_K"] for name in names], dtype=float),
        "e_assoc": np.asarray([pure[name]["association_energy_over_k_K"] for name in names], dtype=float),
        "vol_a": np.asarray([pure[name]["association_volume"] for name in names], dtype=float),
        "assoc_scheme": ["2B", "2B"],
        "k_ij": np.asarray([[0.0, kij], [kij, 0.0]], dtype=float),
        "z": np.asarray([0.0, 0.0], dtype=float),
        "dielc": np.asarray([78.4, 15.1], dtype=float),
    }
    return ePCSAFTMixture.from_params(params, species=["Water", "1-Pentanol"])


def _figure10_association_hessian_payload(source_rows: list[dict[str, str]]) -> dict[str, Any]:
    try:
        from scripts.dev.native_runtime_env import apply_native_runtime_env

        apply_native_runtime_env(os.environ)

        import epcsaft._core as provider_core
        from epcsaft.state.native_adapter import create_struct
        from epcsaft_equilibrium._native import extension_native_core

        if not provider_core._native_cppad_smoke()["cppad_compiled"]:
            return {"status": "blocked", "blockers": ["gross_2002_figure_10_cppad_required"]}

        mixture = _figure10_mixture()
        selected = next(row for row in source_rows if row.get("phase_branch") == "LLE_1_pentanol_rich_liquid")
        temperature = float(selected["temperature_K"])
        composition = np.asarray([float(selected["x_water"]), float(selected["x_1_pentanol"])], dtype=float)
        density = 500.0
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
        tolerance = 1.0e-8
        second_symmetric = all(
            float(np.max(np.abs(second_response[:, :, site] - second_response[:, :, site].T))) <= tolerance
            for site in range(second_shape[2])
        )

        equilibrium_core = extension_native_core()
        amounts = composition.copy()
        volume = float(amounts.sum() / density)
        phase_block = equilibrium_core._native_eos_phase_block(
            mixture._native,
            temperature,
            pressure,
            amounts.tolist(),
            volume,
        )
        pressure_shape = tuple(phase_block["pressure_hessian_shape"])
        pressure_symmetric, pressure_symmetry_error = _matrix_symmetric(
            phase_block["pressure_hessian_row_major"],
            pressure_shape,
            tolerance=tolerance,
        )
        objective_shape = tuple(phase_block["objective_curvature_shape"])
        objective_symmetric, objective_symmetry_error = _matrix_symmetric(
            phase_block["objective_curvature_row_major"],
            objective_shape,
            tolerance=tolerance,
        )

        delta = [0.0, 1.0e-3, 1.0e-3, 0.0]
        solve = provider_core._native_association_site_fraction_solve(delta, density, composition.tolist())
        site_fractions = np.asarray(solve["site_fractions"], dtype=float)
        mass_action = equilibrium_core._native_association_mass_action_block(
            density,
            site_fractions.tolist(),
            composition.tolist(),
            delta,
        )
        max_mass_action_residual = max(abs(float(value)) for value in mass_action["residuals"])
        mass_action_shape = tuple(mass_action["site_fraction_hessian_shape"])
        mass_action_hessian = np.asarray(mass_action["site_fraction_hessian_tensor_row_major"], dtype=float).reshape(mass_action_shape)
        mass_action_hessians_symmetric = all(
            float(np.max(np.abs(mass_action_hessian[site, :, :] - mass_action_hessian[site, :, :].T))) <= tolerance
            for site in range(mass_action_shape[0])
        )

        blockers: list[str] = []
        if raw.get("association_sensitivity_backend") != "cppad_implicit_association":
            blockers.append("gross_2002_figure_10_exact_association_hessian_missing")
        if not np.any(np.abs(first_response) > 1.0e-12):
            blockers.append("gross_2002_figure_10_first_sensitivity_missing")
        if not np.any(np.abs(second_response) > 1.0e-12) or not second_symmetric:
            blockers.append("gross_2002_figure_10_second_sensitivity_missing")
        if not pressure_symmetric or not objective_symmetric or not mass_action_hessians_symmetric:
            blockers.append("gross_2002_figure_10_hessian_symmetry_failed")
        if max_mass_action_residual > 1.0e-8:
            blockers.append("gross_2002_figure_10_mass_action_residual_too_large")

        return {
            "status": "verified_exact" if not blockers else "blocked",
            "blockers": blockers,
            "backend": raw.get("association_sensitivity_backend"),
            "temperature_K": temperature,
            "composition": composition.tolist(),
            "pressure_Pa": pressure,
            "site_fraction_min": float(np.min(site_fractions)),
            "site_fraction_max": float(np.max(site_fractions)),
            "max_mass_action_residual": float(max_mass_action_residual),
            "site_first_sensitivity_shape": list(first_shape),
            "site_second_sensitivity_shape": list(second_shape),
            "site_first_sensitivity_nonzero": bool(np.any(np.abs(first_response) > 1.0e-12)),
            "site_second_sensitivity_nonzero": bool(np.any(np.abs(second_response) > 1.0e-12)),
            "site_second_sensitivities_symmetric": bool(second_symmetric),
            "phase_block_pressure_hessian_symmetric": bool(pressure_symmetric),
            "phase_block_objective_hessian_symmetric": bool(objective_symmetric),
            "association_mass_action_hessians_symmetric": bool(mass_action_hessians_symmetric),
            "phase_block_pressure_symmetry_error": pressure_symmetry_error,
            "phase_block_objective_symmetry_error": objective_symmetry_error,
        }
    except Exception as exc:
        return {
            "status": "blocked",
            "blockers": ["gross_2002_figure_10_exact_association_diagnostics_failed"],
            "message": str(exc),
        }


def _figure10_record(row: dict[str, Any], *, require_exact: bool) -> dict[str, Any]:
    source_csv = row.get("source_csv", "")
    stem = row.get("result_stem", "gross_2002_figure_10_association_mirror")
    source_rows = _read_csv(_repo_path(source_csv)) if _repo_path(source_csv).is_file() else []
    branches = {source_row.get("phase_branch", "") for source_row in source_rows}
    status = (
        "accepted"
        if len(source_rows) >= int(row.get("thresholds", {}).get("min_source_points", 8))
        and {"LLE_1_pentanol_rich_liquid", "LLE_water_rich_liquid"} <= branches
        else "blocked"
    )
    hessian = _figure10_association_hessian_payload(source_rows) if require_exact and source_rows else {"status": "not_requested", "blockers": []}
    if require_exact and hessian.get("status") != "verified_exact":
        status = "blocked"
    return {
        "figure_id": "figure_10",
        "role": "accepted_hard_gate",
        "status": status,
        "counts_toward_completion": True,
        "source_point_count": len(source_rows),
        "source_image": row.get("source_image", ""),
        "route_family": row.get("route_family", ""),
        "artifacts": _artifact_paths("figure_10", stem, source_csv),
        "exact_association_hessian": hessian,
        "cross_association_stress": {
            "status": "verified" if status == "accepted" else "blocked",
            "branches": sorted(branches),
            "k_ij": _parse_table2_kij("water-1-pentanol"),
            "gross_2002_water_caveat": "two-site water association model used by Gross 2002",
        },
    }


def _build_payload(
    manifest_path: Path,
    *,
    require_exact_association_hessian: bool = False,
    require_fresh_native: bool = False,
    checker_command: list[str] | None = None,
) -> dict[str, Any]:
    if not manifest_path.is_file():
        return {
            "checker": "gross_2002_association_acceptance_campaign",
            "manifest": _relative(manifest_path),
            "figure_records": [],
            "summary_artifacts": {
                "json": _relative(SUMMARY_DIR / "gross_2002_association_acceptance_summary.json"),
                "csv": _relative(SUMMARY_DIR / "gross_2002_association_acceptance_summary.csv"),
            },
            "native_freshness_receipt": {},
            "blockers": ["gross_2002_campaign_manifest_missing"],
        }

    manifest = _load_manifest(manifest_path)
    figure_records: list[dict[str, Any]] = []
    for row in manifest.get("figures", []):
        figure_id = row.get("figure_id")
        role = row.get("role")
        if role == "source_requirement":
            figure_records.append(_source_requirement_record(row))
        elif figure_id == "figure_01":
            figure_records.append(_figure01_record(row))
        elif figure_id == "figure_08":
            figure_records.append(_figure08_record(row, require_exact=require_exact_association_hessian))
        elif figure_id == "figure_10":
            figure_records.append(_figure10_record(row, require_exact=require_exact_association_hessian))
        else:
            figure_records.append({"figure_id": figure_id, "role": role, "status": "blocked", "counts_toward_completion": False})

    receipt: dict[str, Any] = {}
    if require_fresh_native:
        try:
            from scripts.dev.native_runtime_env import apply_native_runtime_env

            apply_native_runtime_env(os.environ)
            from epcsaft_equilibrium._native import extension_native_core
            from scripts.validation import native_freshness

            receipt = native_freshness.receipt_to_jsonable(
                native_freshness.build_receipt(
                    native_module=extension_native_core(),
                    checker_command=checker_command
                    or [
                        "python",
                        "scripts/validation/check_gross_2002_association_acceptance.py",
                    ],
                )
            )
        except Exception:
            receipt = {}

    return {
        "checker": "gross_2002_association_acceptance_campaign",
        "manifest": _relative(manifest_path),
        "campaign": manifest.get("campaign", ""),
        "figure_records": figure_records,
        "summary_artifacts": {
            "json": _relative(SUMMARY_DIR / "gross_2002_association_acceptance_summary.json"),
            "csv": _relative(SUMMARY_DIR / "gross_2002_association_acceptance_summary.csv"),
        },
        "native_freshness_receipt": receipt,
        "blockers": [],
    }


def _write_campaign_summary(payload: dict[str, Any]) -> None:
    SUMMARY_DIR.mkdir(parents=True, exist_ok=True)
    retained_payload = dict(payload)
    retained_payload.pop("native_freshness_receipt", None)
    rows: list[dict[str, Any]] = []
    for record in payload.get("figure_records", []):
        rows.append(
            {
                "figure_id": record.get("figure_id", ""),
                "role": record.get("role", ""),
                "status": record.get("status", ""),
                "counts_toward_completion": bool(record.get("counts_toward_completion")),
                "source_point_count": record.get("source_point_count", ""),
                "route_family": record.get("route_family", ""),
                "exact_association_hessian_status": record.get("exact_association_hessian", {}).get("status", ""),
            }
        )
    _write_json(SUMMARY_DIR / "gross_2002_association_acceptance_summary.json", retained_payload)
    _write_csv(
        SUMMARY_DIR / "gross_2002_association_acceptance_summary.csv",
        rows,
        [
            "figure_id",
            "role",
            "status",
            "counts_toward_completion",
            "source_point_count",
            "route_family",
            "exact_association_hessian_status",
        ],
    )


def evaluate_campaign(
    *,
    manifest_path: Path = MANIFEST_PATH,
    require_complete: bool = False,
    require_exact_association_hessian: bool = False,
    require_fresh_native: bool = False,
    checker_command: list[str] | None = None,
    write_summary: bool = False,
) -> dict[str, Any]:
    payload = _build_payload(
        Path(manifest_path),
        require_exact_association_hessian=require_exact_association_hessian,
        require_fresh_native=require_fresh_native,
        checker_command=checker_command,
    )
    result = evaluate_payload(
        payload,
        require_complete=require_complete,
        require_exact_association_hessian=require_exact_association_hessian,
        require_fresh_native=require_fresh_native,
    )
    if write_summary and Path(manifest_path).is_file():
        _write_campaign_summary(result)
        refreshed_payload = _build_payload(
            Path(manifest_path),
            require_exact_association_hessian=require_exact_association_hessian,
            require_fresh_native=require_fresh_native,
            checker_command=checker_command,
        )
        result = evaluate_payload(
            refreshed_payload,
            require_complete=require_complete,
            require_exact_association_hessian=require_exact_association_hessian,
            require_fresh_native=require_fresh_native,
        )
    return result


def _save_plot(fig: Any, png: Path, svg: Path, pdf: Path) -> None:
    png.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(png, dpi=180, bbox_inches="tight")
    fig.savefig(svg, bbox_inches="tight")
    text = svg.read_text(encoding="utf-8")
    svg.write_text("\n".join(line.rstrip() for line in text.splitlines()) + "\n", encoding="utf-8")
    fig.savefig(pdf, bbox_inches="tight")


def _render_figure01(row: dict[str, Any]) -> dict[str, Any]:
    source_csv = _repo_path(row["source_csv"])
    source_rows = _read_csv(source_csv)
    stem = row.get("result_stem", "association")
    artifacts = _artifact_paths("figure_01", stem, row["source_csv"])
    statistics_rows: list[dict[str, Any]] = []
    for source_row in source_rows:
        component = source_row["component"]
        statistics_rows.extend(
            [
                {
                    "component": component,
                    "metric": "vapor_pressure_aad",
                    "value_percent": source_row["psat_aad_percent"],
                    "source_table": source_row["source_table"],
                    "source_status": source_row["source_status"],
                    "source_method": source_row.get("source_method", ""),
                    "source_reference": source_row.get("source_reference", ""),
                    "evidence_role": "gross_2002_table_1_pc_saft_aad",
                },
                {
                    "component": component,
                    "metric": "liquid_density_aad",
                    "value_percent": source_row["liquid_density_aad_percent"],
                    "source_table": source_row["source_table"],
                    "source_status": source_row["source_status"],
                    "source_method": source_row.get("source_method", ""),
                    "source_reference": source_row.get("source_reference", ""),
                    "evidence_role": "gross_2002_table_1_pc_saft_aad",
                },
            ]
        )
    _write_csv(
        _repo_path(artifacts["fit_statistics_csv"]),
        statistics_rows,
        [
            "component",
            "metric",
            "value_percent",
            "source_table",
            "source_status",
            "source_method",
            "source_reference",
            "evidence_role",
        ],
    )

    components = [source_row["component"] for source_row in source_rows]
    summary = {
        "figure_id": "figure_01",
        "status": "accepted",
        "source_point_count": len(source_rows),
        "artifacts": artifacts,
        "source_data_home": row.get("source_data_home", []),
        "pure_association_sanity": {"status": "verified", "components": components},
    }
    return summary


def _render_figure08(row: dict[str, Any]) -> dict[str, Any]:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from scripts.validation import check_associating_gfpe_gate

    source_rows = _read_csv(_repo_path(row["source_csv"]))
    proof = check_associating_gfpe_gate.evaluate_case_dir(
        require_source_data=True,
        require_public_admission=True,
        require_exact_association_hessian=True,
        require_capability_evidence=True,
        require_electrolyte_closed=True,
    )
    public = proof["public_admission"]
    stem = row["result_stem"]
    artifacts = _artifact_paths("figure_08", stem, row["source_csv"])
    retained_summary_path = _repo_path(artifacts["summary_json"])
    retained_summary = _read_json(retained_summary_path) if retained_summary_path.is_file() else {}
    plotted_rows = [
        {
            "series": source_row["phase_branch"],
            "temperature_C": source_row["temperature_C"],
            "temperature_K": source_row["temperature_K"],
            "x_methanol": source_row["x_methanol"],
            "source_status": source_row["source_status"],
        }
        for source_row in source_rows
    ]
    if "methanol_branch_values" in public and "temperature_K" in proof["prerequisite_proof"].get("internal_route", {}):
        route_temperature_k = float(proof["prerequisite_proof"]["internal_route"]["temperature_K"])
        model_rows = [
            {
                "series": "public_associating_lle_route",
                "phase_index": index,
                "temperature_K": route_temperature_k,
                "x_methanol": x_value,
                "route_status": public["status"],
            }
            for index, x_value in enumerate(public["methanol_branch_values"])
        ]
        public_admission = public
        exact_hessian = proof["prerequisite_proof"]["association_hessian"]
    else:
        model_rows = _read_csv(_repo_path(artifacts["model_csv"]))
        if not model_rows:
            raise RuntimeError(f"retained Figure 8 association model CSV is empty: {artifacts['model_csv']}")
        route_temperature_k = float(model_rows[0]["temperature_K"])
        public_admission = retained_summary.get("public_admission", public)
        exact_hessian = retained_summary.get("exact_association_hessian", proof["prerequisite_proof"].get("association_hessian", {}))
    _write_csv(_repo_path(artifacts["plotted_csv"]), plotted_rows, ["series", "temperature_C", "temperature_K", "x_methanol", "source_status"])
    _write_csv(_repo_path(artifacts["model_csv"]), model_rows, ["series", "phase_index", "temperature_K", "x_methanol", "route_status"])

    fig, ax = plt.subplots(figsize=(7.0, 4.8))
    for branch, marker in (("methanol_lean_liquid", "o"), ("methanol_rich_liquid", "s")):
        branch_rows = [source_row for source_row in source_rows if source_row["phase_branch"] == branch]
        ax.scatter(
            [float(source_row["x_methanol"]) for source_row in branch_rows],
            [float(source_row["temperature_K"]) - 273.15 for source_row in branch_rows],
            marker=marker,
            label=f"source {branch.replace('_', ' ')}",
            s=38,
        )
    route_temperature_c = route_temperature_k - 273.15
    route_x = [float(model_row["x_methanol"]) for model_row in model_rows]
    ax.scatter(route_x, [route_temperature_c] * len(route_x), color="#E45756", marker="D", label="public route proof")
    ax.set_xlabel("methanol mole fraction")
    ax.set_ylabel("T / degC")
    ax.set_title("Gross 2002 Figure 8 associating LLE mirror")
    ax.grid(alpha=0.25)
    ax.legend(frameon=False)
    _save_plot(fig, _repo_path(artifacts["png"]), _repo_path(artifacts["svg"]), _repo_path(artifacts["pdf"]))
    plt.close(fig)
    summary = {
        "figure_id": "figure_08",
        "status": "accepted",
        "source_point_count": len(source_rows),
        "artifacts": artifacts,
        "exact_association_hessian": exact_hessian,
        "public_admission": public_admission,
    }
    _write_json(_repo_path(artifacts["summary_json"]), summary)
    return summary


def _render_figure10(row: dict[str, Any]) -> dict[str, Any]:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    source_rows = _read_csv(_repo_path(row["source_csv"]))
    hessian = _figure10_association_hessian_payload(source_rows)
    stem = row["result_stem"]
    artifacts = _artifact_paths("figure_10", stem, row["source_csv"])
    plotted_rows = [
        {
            "source_series": source_row["source_series"],
            "phase_branch": source_row["phase_branch"],
            "temperature_C": source_row["temperature_C"],
            "temperature_K": source_row["temperature_K"],
            "x_water": source_row["x_water"],
            "source_status": source_row["source_status"],
        }
        for source_row in source_rows
    ]
    model_rows = [
        {
            "series": "exact_association_diagnostic_sample",
            "temperature_K": hessian.get("temperature_K", ""),
            "x_water": hessian.get("composition", ["", ""])[0],
            "x_1_pentanol": hessian.get("composition", ["", ""])[1],
            "backend": hessian.get("backend", ""),
            "max_mass_action_residual": hessian.get("max_mass_action_residual", ""),
            "status": hessian.get("status", ""),
        }
    ]
    _write_csv(_repo_path(artifacts["plotted_csv"]), plotted_rows, ["source_series", "phase_branch", "temperature_C", "temperature_K", "x_water", "source_status"])
    _write_csv(_repo_path(artifacts["model_csv"]), model_rows, ["series", "temperature_K", "x_water", "x_1_pentanol", "backend", "max_mass_action_residual", "status"])

    fig, ax = plt.subplots(figsize=(7.0, 4.8))
    styles = {
        "LLE_1_pentanol_rich_liquid": ("o", "#4C78A8"),
        "LLE_water_rich_liquid": ("s", "#F58518"),
        "VLE_or_VLLE_source_points": ("^", "#54A24B"),
    }
    for branch, (marker, color) in styles.items():
        branch_rows = [source_row for source_row in source_rows if source_row["phase_branch"] == branch]
        ax.scatter(
            [float(source_row["x_water"]) for source_row in branch_rows],
            [float(source_row["temperature_C"]) for source_row in branch_rows],
            marker=marker,
            color=color,
            s=38,
            label=branch.replace("_", " "),
        )
    if hessian.get("status") == "verified_exact":
        ax.scatter(
            [float(hessian["composition"][0])],
            [float(hessian["temperature_K"]) - 273.15],
            color="#E45756",
            marker="D",
            s=64,
            label="exact association diagnostic sample",
        )
    ax.set_xlabel("water mole fraction")
    ax.set_ylabel("T / degC")
    ax.set_title("Gross 2002 Figure 10 cross-association stress mirror")
    ax.grid(alpha=0.25)
    ax.legend(frameon=False)
    _save_plot(fig, _repo_path(artifacts["png"]), _repo_path(artifacts["svg"]), _repo_path(artifacts["pdf"]))
    plt.close(fig)
    summary = {
        "figure_id": "figure_10",
        "status": "accepted" if hessian.get("status") == "verified_exact" else "blocked",
        "source_point_count": len(source_rows),
        "artifacts": artifacts,
        "exact_association_hessian": hessian,
        "cross_association_stress": {"status": "verified" if hessian.get("status") == "verified_exact" else "blocked"},
    }
    _write_json(_repo_path(artifacts["summary_json"]), summary)
    return summary


def render_figure(figure_id: str, *, manifest_path: Path = MANIFEST_PATH) -> dict[str, Any]:
    manifest = _load_manifest(manifest_path)
    row = _manifest_figure(manifest, figure_id)
    if figure_id == "figure_01":
        return _render_figure01(row)
    if figure_id == "figure_08":
        return _render_figure08(row)
    if figure_id == "figure_10":
        return _render_figure10(row)
    raise ValueError(f"Gross 2002 render only owns accepted figures, got {figure_id}")


def render_accepted_figures(*, manifest_path: Path = MANIFEST_PATH) -> list[dict[str, Any]]:
    return [render_figure(figure_id, manifest_path=manifest_path) for figure_id in REQUIRED_ACCEPTED_FIGURES]


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--manifest", type=Path, default=MANIFEST_PATH)
    parser.add_argument("--require-complete", action="store_true")
    parser.add_argument("--require-exact-association-hessian", action="store_true")
    parser.add_argument("--require-fresh-native", action="store_true")
    parser.add_argument("--render", action="store_true")
    parser.add_argument("--regenerate", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_arg_parser().parse_args(argv)
    cli_args = sys.argv[1:] if argv is None else argv
    checker_command = [
        "uv",
        "run",
        "--no-sync",
        "python",
        "scripts/validation/check_gross_2002_association_acceptance.py",
        *cli_args,
    ]
    if args.render or args.regenerate:
        render_accepted_figures(manifest_path=args.manifest)
    output = evaluate_campaign(
        manifest_path=args.manifest,
        require_complete=args.require_complete,
        require_exact_association_hessian=args.require_exact_association_hessian or args.require_complete,
        require_fresh_native=args.require_fresh_native or args.require_complete,
        checker_command=checker_command,
        write_summary=args.render or args.regenerate,
    )
    if args.json:
        print(json.dumps(output, indent=2, sort_keys=True))
    else:
        print(f"Gross 2002 association acceptance: {output['status']}")
        if output["blockers"]:
            print("  blockers: " + ", ".join(str(item) for item in output["blockers"]))
    if args.require_complete and not output["complete"]:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
