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
    import_path = str(import_root)
    if import_path not in sys.path:
        sys.path.insert(0, import_path)

DEFAULT_CASE_DIR = (
    REPO_ROOT
    / "data"
    / "reference"
    / "equilibrium_benchmarks"
    / "electrolyte_lle"
    / "water_ethanol_isobutanol_nacl"
)
REQUIRED_FILES = (
    "metadata.json",
    "thresholds.json",
    "feed_compositions.csv",
    "experimental_tielines.csv",
    "source_notes.md",
)
FORMULA_SPECIES = ["H2O", "Ethanol", "Isobutanol", "NaCl"]
NATIVE_SPECIES = ["H2O", "Ethanol", "Butanol", "Na+", "Cl-"]
CHARGES = np.asarray([0.0, 0.0, 0.0, 1.0, -1.0], dtype=float)


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _read_csv(path: Path) -> list[dict[str, str]]:
    return list(csv.DictReader(path.read_text(encoding="utf-8").splitlines()))


def _jsonable(value: Any) -> Any:
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    return value


def _finite_nonnegative(values: np.ndarray) -> bool:
    return bool(np.all(np.isfinite(values)) and np.all(values >= 0.0))


def _formula_values(row: dict[str, str], *, source: str) -> np.ndarray:
    if source == "feed":
        keys = ("x_water_total", "x_ethanol_total", "x_isobutanol_total", "x_nacl_total")
    elif source == "tieline":
        keys = ("x_water", "x_ethanol", "x_isobutanol", "x_nacl")
    else:
        raise ValueError(f"unsupported source row type: {source}")
    return np.asarray([float(row[key]) for key in keys], dtype=float)


def expand_formula_to_explicit_ions(values: np.ndarray) -> np.ndarray:
    if values.shape != (4,):
        raise ValueError("formula composition must contain H2O, ethanol, isobutanol, and NaCl entries")
    salt = float(values[3])
    denominator = 1.0 + salt
    if denominator <= 0.0:
        raise ValueError("explicit-ion expansion denominator must be positive")
    return np.asarray(
        [
            float(values[0]) / denominator,
            float(values[1]) / denominator,
            float(values[2]) / denominator,
            salt / denominator,
            salt / denominator,
        ],
        dtype=float,
    )


def _source_fixture_payload(case_dir: Path) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]]]:
    blockers = [f"missing_required_file:{name}" for name in REQUIRED_FILES if not (case_dir / name).is_file()]
    if blockers:
        return {"status": "missing_files", "blockers": blockers}, [], []

    metadata = _read_json(case_dir / "metadata.json")
    thresholds = _read_json(case_dir / "thresholds.json")
    feed_rows = _read_csv(case_dir / "feed_compositions.csv")
    tieline_rows = _read_csv(case_dir / "experimental_tielines.csv")
    source_notes = (case_dir / "source_notes.md").read_text(encoding="utf-8")

    row_blockers: list[str] = []
    expanded_feed_rows: list[dict[str, Any]] = []
    expanded_tieline_rows: list[dict[str, Any]] = []
    max_raw_formula_row_sum_error = 0.0
    max_formula_row_sum_error = 0.0
    max_expanded_row_sum_error = 0.0
    max_charge_balance_error = 0.0

    if metadata.get("parameter_dataset") != "2026_Khudaida":
        row_blockers.append("khudaida_parameter_dataset_mismatch")
    if metadata.get("species") != NATIVE_SPECIES:
        row_blockers.append("khudaida_native_species_order_mismatch")
    if metadata.get("formula_species") != FORMULA_SPECIES:
        row_blockers.append("khudaida_formula_species_order_mismatch")
    if not feed_rows:
        row_blockers.append("khudaida_feed_rows_missing")
    if not tieline_rows:
        row_blockers.append("khudaida_tieline_rows_missing")

    def append_row(row: dict[str, str], *, source: str, target: list[dict[str, Any]]) -> None:
        nonlocal max_raw_formula_row_sum_error, max_formula_row_sum_error, max_expanded_row_sum_error
        nonlocal max_charge_balance_error
        try:
            raw_formula = _formula_values(row, source=source)
            raw_sum = float(raw_formula.sum())
            if raw_sum <= 0.0 or not math.isfinite(raw_sum):
                raise ValueError("formula row sum must be finite and positive")
            formula = raw_formula / raw_sum
            expanded = expand_formula_to_explicit_ions(formula)
        except (KeyError, TypeError, ValueError) as exc:
            row_blockers.append(f"khudaida_{source}_row_invalid:{exc}")
            return
        if not _finite_nonnegative(raw_formula):
            row_blockers.append(f"khudaida_{source}_formula_row_not_finite_nonnegative")
        if not _finite_nonnegative(expanded):
            row_blockers.append(f"khudaida_{source}_expanded_row_not_finite_nonnegative")
        raw_formula_sum_error = abs(raw_sum - 1.0)
        formula_sum_error = abs(float(formula.sum()) - 1.0)
        expanded_sum_error = abs(float(expanded.sum()) - 1.0)
        charge_error = abs(float(expanded @ CHARGES))
        max_raw_formula_row_sum_error = max(max_raw_formula_row_sum_error, raw_formula_sum_error)
        max_formula_row_sum_error = max(max_formula_row_sum_error, formula_sum_error)
        max_expanded_row_sum_error = max(max_expanded_row_sum_error, expanded_sum_error)
        max_charge_balance_error = max(max_charge_balance_error, charge_error)
        target.append(
            {
                "case_key": row.get("case_key", ""),
                "tie_line": int(row.get("tie_line", 0)),
                "phase": row.get("phase", source),
                "temperature_K": float(row["temperature_K"]),
                "raw_formula": raw_formula.tolist(),
                "formula": formula.tolist(),
                "expanded": expanded.tolist(),
                "raw_formula_row_sum_error": raw_formula_sum_error,
                "formula_row_sum_error": formula_sum_error,
                "expanded_row_sum_error": expanded_sum_error,
                "charge_balance_error": charge_error,
            }
        )

    for row in feed_rows:
        append_row(row, source="feed", target=expanded_feed_rows)
    for row in tieline_rows:
        append_row(row, source="tieline", target=expanded_tieline_rows)

    formula_tolerance = float(thresholds.get("material_balance_error", 1.0e-10))
    charge_tolerance = float(thresholds.get("charge_balance_error", 1.0e-8))
    if max_formula_row_sum_error > formula_tolerance:
        row_blockers.append("khudaida_formula_rows_not_normalized")
    if max_expanded_row_sum_error > formula_tolerance:
        row_blockers.append("khudaida_explicit_ion_rows_not_normalized")
    if max_charge_balance_error > charge_tolerance:
        row_blockers.append("khudaida_explicit_ion_charge_balance_exceeds_threshold")
    if "Khudaida" not in source_notes:
        row_blockers.append("khudaida_source_notes_missing_source_name")

    status = "source_backed" if not row_blockers else "incomplete"
    return (
        {
            "status": status,
            "blockers": row_blockers,
            "case_dir": case_dir.relative_to(REPO_ROOT).as_posix(),
            "metadata": metadata,
            "thresholds": thresholds,
            "feed_row_count": len(feed_rows),
            "tieline_phase_count": len(tieline_rows),
            "source_notes_status": "retained",
            "max_raw_formula_row_sum_error": max_raw_formula_row_sum_error,
            "formula_closure_correction": "normalized_finite_source_rows_for_explicit_ion_native_gate",
        },
        expanded_feed_rows,
        expanded_tieline_rows,
    )


def _representative_tieline_pair(expanded_tieline_rows: list[dict[str, Any]]) -> list[np.ndarray]:
    by_case: dict[str, list[dict[str, Any]]] = {}
    for row in expanded_tieline_rows:
        by_case.setdefault(str(row["case_key"]), []).append(row)
    for rows in by_case.values():
        if len(rows) >= 2:
            rows = sorted(rows[:2], key=lambda item: str(item["phase"]))
            return [np.asarray(row["expanded"], dtype=float) for row in rows]
    raise ValueError("no complete Khudaida tie-line pair found")


def _parameter_bundle_payload(
    metadata: dict[str, Any],
    feed_row: dict[str, Any] | None,
) -> tuple[dict[str, Any], Any | None]:
    from scripts.data.paper_validation_parameters import paper_validation_parameter_path

    dataset_name = str(metadata.get("parameter_dataset", "2026_Khudaida"))
    species = [str(item) for item in metadata.get("species", NATIVE_SPECIES)]
    temperature = float(feed_row["temperature_K"]) if feed_row is not None else 293.15
    composition = np.asarray(feed_row["expanded"], dtype=float) if feed_row is not None else np.full(len(species), 1.0 / len(species))
    bundle_path = paper_validation_parameter_path(dataset_name)
    blockers: list[str] = []

    from epcsaft.state.native_adapter import ePCSAFTMixture

    public_dataset_status = "closed"
    try:
        ePCSAFTMixture.from_dataset(dataset_name, species, composition, temperature)
    except Exception as exc:
        public_dataset_error = str(exc)
    else:
        public_dataset_error = ""
        public_dataset_status = "unexpectedly_open"
        blockers.append("khudaida_public_dataset_registered")

    try:
        mixture = ePCSAFTMixture.from_dataset(bundle_path, species, composition, temperature)
    except Exception as exc:
        return (
            {
                "status": "failed",
                "blockers": [*blockers, "khudaida_parameter_bundle_does_not_construct"],
                "dataset": dataset_name,
                "path": bundle_path.relative_to(REPO_ROOT).as_posix(),
                "public_dataset_status": public_dataset_status,
                "public_dataset_error": public_dataset_error,
                "error": str(exc),
            },
            None,
        )

    return (
        {
            "status": "constructs_native_mixture" if not blockers else "incomplete",
            "blockers": blockers,
            "dataset": dataset_name,
            "path": bundle_path.relative_to(REPO_ROOT).as_posix(),
            "public_dataset_status": public_dataset_status,
            "public_dataset_error": public_dataset_error,
            "species": mixture.species,
            "component_count": mixture.ncomp,
        },
        mixture,
    )


def _native_diagnostics_payload(
    mixture: Any,
    metadata: dict[str, Any],
    feed_row: dict[str, Any] | None,
    expanded_tieline_rows: list[dict[str, Any]],
    checker_command: list[str] | None,
) -> dict[str, Any]:
    from scripts.dev.native_runtime_env import apply_native_runtime_env

    apply_native_runtime_env(os.environ)

    from epcsaft_equilibrium._native import extension_native_core
    from scripts.validation import native_freshness

    if mixture is None:
        return {"status": "skipped", "blockers": ["khudaida_native_mixture_missing"]}
    if feed_row is None:
        return {"status": "skipped", "blockers": ["khudaida_feed_row_missing"]}

    core = extension_native_core()
    temperature = float(feed_row["temperature_K"])
    density = 55344.274540081075
    phase_system_density = 20000.0
    feed = np.asarray(feed_row["expanded"], dtype=float)
    electrolyte = core._native_electrolyte_contribution_block(
        mixture._native,
        temperature,
        density,
        feed.tolist(),
        feed.tolist(),
    )
    phase_system_mixture = _nonassociating_diagnostic_mixture(mixture)
    phase_amounts = _representative_tieline_pair(expanded_tieline_rows)
    volumes = [float(phase.sum() / phase_system_density) for phase in phase_amounts]
    phase_system = core._native_eos_phase_system(
        phase_system_mixture._native,
        temperature,
        float(metadata.get("pressure_Pa", 100000.0)),
        [phase.tolist() for phase in phase_amounts],
        volumes,
        np.sum(phase_amounts, axis=0).tolist(),
        CHARGES.tolist(),
    )
    phase_charge_residuals = [abs(float(value)) for value in phase_system.get("phase_charge_residuals", [])]
    receipt = native_freshness.build_receipt(
        native_module=core,
        checker_command=checker_command or ["python", "scripts/validation/check_electrolyte_gfpe_gate.py"],
    )
    blockers: list[str] = []
    if electrolyte.get("active") is not True:
        blockers.append("khudaida_electrolyte_contribution_inactive")
    if not phase_charge_residuals:
        blockers.append("khudaida_phase_charge_residuals_missing")
    elif max(phase_charge_residuals) > 1.0e-8:
        blockers.append("khudaida_phase_charge_residual_exceeds_threshold")
    return {
        "status": "native_diagnostics_complete" if not blockers else "incomplete",
        "blockers": blockers,
        "electrolyte_contribution": {
            "active": bool(electrolyte.get("active")),
            "block": electrolyte.get("block"),
            "value_backend": electrolyte.get("value_backend"),
            "term_basis": electrolyte.get("term_basis"),
            "phase_charge_residual": float(electrolyte.get("phase_charge_residual", math.nan)),
            "electrolyte_residual_helmholtz": float(electrolyte.get("electrolyte_residual_helmholtz", math.nan)),
        },
        "phase_system": {
            "association_state": "disabled_for_pre_association_electrolyte_gate",
            "diagnostic_density_mol_m3": phase_system_density,
            "constraint_names": list(phase_system.get("constraint_names", [])),
            "phase_charge_residuals": phase_system.get("phase_charge_residuals", []),
            "max_phase_charge_residual": max(phase_charge_residuals) if phase_charge_residuals else math.inf,
        },
        "native_freshness_receipt": native_freshness.receipt_to_jsonable(receipt),
    }


def _nonassociating_diagnostic_mixture(mixture: Any) -> Any:
    from epcsaft.state.native_adapter import ePCSAFTMixture

    params = mixture.parameters
    ncomp = len(mixture.species)
    params["assoc_scheme"] = [None] * ncomp
    params["e_assoc"] = np.zeros(ncomp, dtype=float)
    params["vol_a"] = np.zeros(ncomp, dtype=float)
    params.pop("assoc_num", None)
    params.pop("assoc_matrix", None)
    return ePCSAFTMixture.from_params(params, species=mixture.species)


def _public_route_state_payload() -> dict[str, Any]:
    import epcsaft_equilibrium

    capabilities = epcsaft_equilibrium.capabilities()
    rows = capabilities["activation_matrix"]["rows"]
    activation = {str(row["key"]): row for row in rows}
    electrolyte = activation.get("electrolyte_lle", {})
    derivative_quantities = [
        str(row.get("quantity", ""))
        for row in capabilities.get("route_derivative_evidence", {}).get("rows", [])
        if isinstance(row, dict)
    ]
    return {
        "electrolyte_lle": {
            "present": bool(electrolyte),
            "production_exposed": bool(electrolyte.get("production_exposed", False)),
            "exposure_status": electrolyte.get("exposure_status"),
            "public_routes": list(electrolyte.get("public_routes", [])),
            "proof_routes": list(electrolyte.get("proof_routes", [])),
        },
        "capabilities_public_routes": list(capabilities.get("public_routes", [])),
        "production_families": list(capabilities.get("production_families", [])),
        "route_derivative_evidence_quantities": derivative_quantities,
    }


def evaluate_payload(
    payload: dict[str, Any],
    *,
    require_source_data: bool = True,
    require_parameter_bundle: bool = False,
    require_native_diagnostics: bool = False,
    require_public_routes_closed: bool = False,
) -> dict[str, Any]:
    blockers = list(payload.get("blockers", []))
    fixture = payload.get("fixture", {})
    if require_source_data:
        if fixture.get("status") != "source_backed":
            blockers.append("khudaida_source_fixture_not_source_backed")
        blockers.extend(str(item) for item in fixture.get("blockers", []))

    expansion = payload.get("explicit_ion_expansion", {})
    if expansion.get("max_formula_row_sum_error", math.inf) > 1.0e-10:
        blockers.append("khudaida_formula_row_sum_error_exceeds_threshold")
    if expansion.get("max_charge_balance_error", math.inf) > 1.0e-8:
        blockers.append("khudaida_explicit_ion_charge_balance_exceeds_threshold")

    parameter_bundle = payload.get("parameter_bundle", {})
    if require_parameter_bundle:
        if parameter_bundle.get("status") != "constructs_native_mixture":
            blockers.append("khudaida_parameter_bundle_does_not_construct")
        blockers.extend(str(item) for item in parameter_bundle.get("blockers", []))

    native_diagnostics = payload.get("native_diagnostics", {})
    if require_native_diagnostics:
        if native_diagnostics.get("status") != "native_diagnostics_complete":
            blockers.append("khudaida_native_diagnostics_incomplete")
        blockers.extend(str(item) for item in native_diagnostics.get("blockers", []))

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
        if "electrolyte_lle" in public_state.get("route_derivative_evidence_quantities", []):
            blockers.append("electrolyte_lle_derivative_evidence_exposed")

    unique_blockers = sorted(set(blockers))
    result = dict(payload)
    result["blockers"] = unique_blockers
    result["complete"] = not unique_blockers
    return result


def evaluate_case_dir(
    case_dir: Path = DEFAULT_CASE_DIR,
    *,
    require_source_data: bool = True,
    require_parameter_bundle: bool = False,
    require_native_diagnostics: bool = False,
    require_public_routes_closed: bool = False,
    checker_command: list[str] | None = None,
) -> dict[str, Any]:
    case_dir = Path(case_dir)
    fixture, expanded_feed_rows, expanded_tieline_rows = _source_fixture_payload(case_dir)
    thresholds = fixture.get("thresholds", {})
    expansion = {
        "formula_species": FORMULA_SPECIES,
        "native_species": NATIVE_SPECIES,
        "feed_row_count": len(expanded_feed_rows),
        "tieline_phase_count": len(expanded_tieline_rows),
        "max_raw_formula_row_sum_error": max(
            [float(row["raw_formula_row_sum_error"]) for row in [*expanded_feed_rows, *expanded_tieline_rows]],
            default=math.inf,
        ),
        "max_formula_row_sum_error": max(
            [float(row["formula_row_sum_error"]) for row in [*expanded_feed_rows, *expanded_tieline_rows]],
            default=math.inf,
        ),
        "max_expanded_row_sum_error": max(
            [float(row["expanded_row_sum_error"]) for row in [*expanded_feed_rows, *expanded_tieline_rows]],
            default=math.inf,
        ),
        "max_charge_balance_error": max(
            [float(row["charge_balance_error"]) for row in [*expanded_feed_rows, *expanded_tieline_rows]],
            default=math.inf,
        ),
        "formula_row_sum_threshold": float(thresholds.get("material_balance_error", 1.0e-10)),
        "charge_balance_threshold": float(thresholds.get("charge_balance_error", 1.0e-8)),
    }
    representative_feed = expanded_feed_rows[0] if expanded_feed_rows else None
    parameter_bundle: dict[str, Any] = {"status": "not_requested", "blockers": []}
    mixture = None
    if require_parameter_bundle or require_native_diagnostics:
        parameter_bundle, mixture = _parameter_bundle_payload(fixture.get("metadata", {}), representative_feed)
    native_diagnostics: dict[str, Any] = {"status": "not_requested", "blockers": []}
    if require_native_diagnostics:
        native_diagnostics = _native_diagnostics_payload(
            mixture,
            fixture.get("metadata", {}),
            representative_feed,
            expanded_tieline_rows,
            checker_command,
        )
    payload = {
        "checker": "electrolyte_gfpe_closed_admission_gate",
        "case_label": "Khudaida 2026 electrolyte LLE",
        "fixture": fixture,
        "explicit_ion_expansion": expansion,
        "parameter_bundle": parameter_bundle,
        "native_diagnostics": native_diagnostics,
        "public_route_state": _public_route_state_payload(),
    }
    return _jsonable(
        evaluate_payload(
            payload,
            require_source_data=require_source_data,
            require_parameter_bundle=require_parameter_bundle,
            require_native_diagnostics=require_native_diagnostics,
            require_public_routes_closed=require_public_routes_closed,
        )
    )


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--case-dir", type=Path, default=DEFAULT_CASE_DIR)
    parser.add_argument("--require-source-data", action="store_true")
    parser.add_argument("--require-parameter-bundle", action="store_true")
    parser.add_argument("--require-native-diagnostics", action="store_true")
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
        "scripts/validation/check_electrolyte_gfpe_gate.py",
        *argv,
    ]
    output = evaluate_case_dir(
        args.case_dir,
        require_source_data=args.require_source_data or args.require_complete,
        require_parameter_bundle=args.require_parameter_bundle or args.require_complete,
        require_native_diagnostics=args.require_native_diagnostics or args.require_complete,
        require_public_routes_closed=args.require_public_routes_closed or args.require_complete,
        checker_command=checker_command,
    )
    if args.require_complete:
        receipt = output.get("native_diagnostics", {}).get("native_freshness_receipt", {})
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
