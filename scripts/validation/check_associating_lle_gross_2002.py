from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
EQUILIBRIUM_SRC_ROOT = REPO_ROOT / "packages" / "epcsaft-equilibrium" / "src"
if str(EQUILIBRIUM_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(EQUILIBRIUM_SRC_ROOT))

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
    require_route_closed: bool = False,
) -> dict[str, Any]:
    fixture = _fixture_payload(Path(case_dir))
    payload = {
        "checker": "gross_2002_associating_lle_closed_admission_gate",
        "case_label": "Gross/Sadowski 2002 methanol/cyclohexane associating LLE",
        "fixture": fixture,
        "association_hessian": {"status": "pending_internal_proof_for_issue_145"},
        "public_route_state": _public_route_state_payload(),
        "blockers": list(fixture["blockers"]),
    }
    return _jsonable(
        evaluate_payload(
            payload,
            require_source_data=require_source_data,
            require_exact_association_hessian=require_exact_association_hessian,
            require_route_closed=require_route_closed,
        )
    )


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--case-dir", type=Path, default=DEFAULT_CASE_DIR)
    parser.add_argument("--require-source-data", action="store_true")
    parser.add_argument("--require-exact-association-hessian", action="store_true")
    parser.add_argument("--require-route-closed", action="store_true")
    parser.add_argument("--require-complete", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_arg_parser().parse_args(argv)
    output = evaluate_case_dir(
        args.case_dir,
        require_source_data=args.require_source_data or args.require_complete,
        require_exact_association_hessian=args.require_exact_association_hessian or args.require_complete,
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
        or args.require_route_closed
    ) and not output["complete"]:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
