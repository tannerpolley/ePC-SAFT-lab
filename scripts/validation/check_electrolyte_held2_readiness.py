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

from scripts.validation import check_electrolyte_gfpe_gate

BASIS_SPECIES = ["H2O", "Ethanol", "Butanol", "NaCl"]
NATIVE_SPECIES = ["H2O", "Ethanol", "Butanol", "Na+", "Cl-"]
CHARGE_VECTOR = np.asarray([0.0, 0.0, 0.0, 1.0, -1.0], dtype=float)
LIFT_MATRIX = np.asarray(
    [
        [1.0, 0.0, 0.0, 0.0],
        [0.0, 1.0, 0.0, 0.0],
        [0.0, 0.0, 1.0, 0.0],
        [0.0, 0.0, 0.0, 1.0],
        [0.0, 0.0, 0.0, 1.0],
    ],
    dtype=float,
)
CHARGE_BALANCE_THRESHOLD = 1.0e-10
PENDING_HELD2_GATES = [
    "electrolyte_tpd",
    "held2_dual_phase_discovery",
    "electrolyte_stage_iii_refinement",
    "postsolve_electrolyte_phase_set_certification",
    "public_electrolyte_route_admission",
]


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


def _array_is_finite(value: Any) -> bool:
    values = np.asarray(value, dtype=float)
    return bool(values.size and np.all(np.isfinite(values)))


def _read_csv(path: Path) -> list[dict[str, str]]:
    return list(csv.DictReader(path.read_text(encoding="utf-8").splitlines()))


def _representative_reduced_amounts(case_dir: Path) -> np.ndarray:
    feed_rows = _read_csv(case_dir / "feed_compositions.csv")
    if not feed_rows:
        raise ValueError("source fixture has no feed composition rows")
    row = feed_rows[0]
    values = np.asarray(
        [
            float(row["x_water_total"]),
            float(row["x_ethanol_total"]),
            float(row["x_isobutanol_total"]),
            float(row["x_nacl_total"]),
        ],
        dtype=float,
    )
    if not np.all(np.isfinite(values)) or np.any(values < 0.0):
        raise ValueError("source fixture representative reduced amounts must be finite and nonnegative")
    total = float(values.sum())
    if total <= 0.0:
        raise ValueError("source fixture representative reduced amount total must be positive")
    return values / total


def _source_gate_payload(case_dir: Path, checker_command: list[str] | None) -> dict[str, Any]:
    command = checker_command or [
        "uv",
        "run",
        "--no-sync",
        "python",
        "scripts/validation/check_electrolyte_held2_readiness.py",
    ]
    return check_electrolyte_gfpe_gate.evaluate_case_dir(
        case_dir,
        require_source_data=True,
        require_parameter_bundle=True,
        require_native_diagnostics=True,
        require_public_routes_closed=True,
        checker_command=command,
    )


def _reduced_basis_payload(case_dir: Path, source_gate: dict[str, Any]) -> dict[str, Any]:
    blockers: list[str] = []
    try:
        reduced = _representative_reduced_amounts(case_dir)
        native_amounts = LIFT_MATRIX @ reduced
        charge_balance = float(CHARGE_VECTOR @ native_amounts)
        na_cl_amount_gap = abs(float(native_amounts[3] - native_amounts[4]))
    except (KeyError, TypeError, ValueError) as exc:
        return {
            "status": "invalid_source_basis",
            "blockers": [f"electrolyte_reduced_basis_source_invalid:{exc}"],
            "basis_species": BASIS_SPECIES,
            "native_species": NATIVE_SPECIES,
            "charge_vector": CHARGE_VECTOR,
            "lift_matrix_row_major": LIFT_MATRIX,
            "max_abs_charge_balance": math.inf,
            "charge_balance_threshold": CHARGE_BALANCE_THRESHOLD,
        }

    max_abs_charge_balance = abs(charge_balance)
    if max_abs_charge_balance > CHARGE_BALANCE_THRESHOLD:
        blockers.append("electrolyte_reduced_basis_charge_balance_exceeds_threshold")
    if na_cl_amount_gap > CHARGE_BALANCE_THRESHOLD:
        blockers.append("electrolyte_reduced_basis_salt_lift_not_pairwise_neutral")

    source_expansion = source_gate.get("explicit_ion_expansion", {})
    return {
        "status": "verified_exact_charge_neutral_lift" if not blockers else "incomplete",
        "blockers": blockers,
        "basis_species": BASIS_SPECIES,
        "native_species": NATIVE_SPECIES,
        "charge_vector": CHARGE_VECTOR,
        "lift_matrix_row_major": LIFT_MATRIX,
        "representative_basis_amounts": reduced,
        "representative_native_amounts": native_amounts,
        "representative_native_amount_sum": float(native_amounts.sum()),
        "max_abs_charge_balance": max_abs_charge_balance,
        "charge_balance_threshold": CHARGE_BALANCE_THRESHOLD,
        "source_gate_max_explicit_ion_charge_balance": float(
            source_expansion.get("max_charge_balance_error", math.inf)
        ),
        "basis_semantics": "charge_neutral_reduced_amount_lift_for_strong_NaCl_electrolyte",
    }


def _compact_ionic_params() -> dict[str, Any]:
    temperature = 298.15
    sigma_water = (
        2.7927
        + 10.11 * np.exp(-0.01775 * temperature)
        - 1.417 * np.exp(-0.01146 * temperature)
    )
    return {
        "MW": np.asarray([18.01528e-3, 22.98e-3, 35.45e-3]),
        "m": np.asarray([1.2047, 1.0, 1.0]),
        "s": np.asarray([sigma_water, 2.8232, 2.7560]),
        "e": np.asarray([353.95, 230.0, 170.0]),
        "e_assoc": np.asarray([2425.7, 0.0, 0.0]),
        "vol_a": np.asarray([0.04509, 0.0, 0.0]),
        "assoc_scheme": ["2B", None, None],
        "z": np.asarray([0.0, 1.0, -1.0]),
        "dielc": np.asarray([78.09, 8.0, 8.0]),
        "d_born": np.asarray([0.0, 3.445, 4.1]),
        "f_solv": np.asarray([1.5, 1.0, 1.0]),
        "k_ij": np.asarray(
            [
                [0.0, 0.0045, -0.25],
                [0.0045, 0.0, 0.317],
                [-0.25, 0.317, 0.0],
            ]
        ),
        "l_ij": np.zeros((3, 3)),
        "k_hb": np.zeros((3, 3)),
        "elec_model": {
            "rel_perm": {"rule": "empirical", "differential_mode": "cppad"},
            "born_model": {
                "d_Born_mode": "fitted_param",
                "solvation_shell_model": True,
                "dielectric_saturation": True,
                "mu_born_model": {"differential_mode": "cppad", "comp_dep_delta_d": True},
            },
        },
    }


def _born_ssm_ds_payload() -> dict[str, Any]:
    from scripts.dev.native_runtime_env import apply_native_runtime_env

    apply_native_runtime_env(os.environ)

    from epcsaft.state.native_adapter import ePCSAFTMixture

    species = ["water", "Na+", "Cl-"]
    mixture = ePCSAFTMixture.from_params(_compact_ionic_params(), species=species)
    state = mixture.state(
        T=298.15,
        x=np.asarray([0.9998, 1.0e-4, 1.0e-4], dtype=float),
        P=1.0e5,
        phase="liq",
    )

    blockers: list[str] = []
    try:
        composition = state.composition_derivative_residual_helmholtz()
        lnfug_composition = state.ln_fugacity_composition_derivative_result()
        lnfug_parameter = state.ln_fugacity_parameter_derivative_result()
        activity_parameter = state.activity_parameter_derivative_result(species=species)
        born = state.born_parameter_derivatives()
    except Exception as exc:
        return {
            "status": "failed",
            "blockers": [f"born_ssm_ds_receipt_failed:{exc}"],
            "backend": "",
            "solvation_shell_model": True,
            "dielectric_saturation": True,
            "composition_derivative_backend": "",
            "finite_composition_derivatives": False,
            "finite_fugacity_derivatives": False,
            "finite_activity_derivatives": False,
            "finite_parameter_derivatives": False,
            "parameter_families": [],
        }

    finite_composition = (
        composition.get("derivative_backend", {}).get("born") == "cppad"
        and _array_is_finite(composition.get("terms", {}).get("born", []))
    )
    finite_fugacity = (
        str(lnfug_composition.get("backend", "")).startswith("cppad")
        and _array_is_finite(lnfug_composition.get("jacobian", []))
        and _array_is_finite(lnfug_parameter.get("jacobian", []))
    )
    finite_activity = (
        activity_parameter.get("backend") == "cppad"
        and _array_is_finite(activity_parameter.get("value", []))
        and _array_is_finite(activity_parameter.get("jacobian", []))
    )
    finite_parameter = (
        born.get("backend") == "cppad"
        and all(
            _array_is_finite(born.get(key, []))
            for key in (
                "a_born_d_d_born",
                "a_born_d_f_solv",
                "mu_res_d_d_born",
                "mu_res_d_f_solv",
                "lnfug_d_d_born",
                "lnfug_d_f_solv",
                "lngamma_d_d_born",
                "lngamma_d_f_solv",
            )
        )
    )
    if not finite_composition:
        blockers.append("born_ssm_ds_composition_derivatives_missing")
    if not finite_fugacity:
        blockers.append("born_ssm_ds_fugacity_derivatives_missing")
    if not finite_activity:
        blockers.append("born_ssm_ds_activity_derivatives_missing")
    if not finite_parameter:
        blockers.append("born_ssm_ds_parameter_derivatives_missing")

    return {
        "status": "verified_cppad_born_ssm_ds_receipts" if not blockers else "incomplete",
        "blockers": blockers,
        "species": species,
        "backend": str(born.get("backend", "")),
        "solvation_shell_model": True,
        "dielectric_saturation": True,
        "composition_derivative_backend": str(composition.get("derivative_backend", {}).get("born", "")),
        "ln_fugacity_composition_backend": str(lnfug_composition.get("backend", "")),
        "ln_fugacity_parameter_backend": str(lnfug_parameter.get("backend", "")),
        "activity_parameter_backend": str(activity_parameter.get("backend", "")),
        "finite_composition_derivatives": finite_composition,
        "finite_fugacity_derivatives": finite_fugacity,
        "finite_activity_derivatives": finite_activity,
        "finite_parameter_derivatives": finite_parameter,
        "composition_jacobian_shape": lnfug_composition.get("shape"),
        "ln_fugacity_parameter_shape": lnfug_parameter.get("shape"),
        "activity_parameter_shape": activity_parameter.get("shape"),
        "born_parameter_order": born.get("parameters"),
        "parameter_families": ["d_born", "f_solv"],
        "source_equation_ids": {
            "composition": composition.get("source_equation_ids", []),
            "ln_fugacity_composition": lnfug_composition.get("source_equation_ids", []),
            "activity_parameter": activity_parameter.get("source_equation_ids", []),
        },
    }


def _held2_readiness_payload() -> dict[str, Any]:
    return {
        "status": "readiness_prerequisites_verified",
        "readiness_only": True,
        "full_held2_claimed": False,
        "pending_gates": PENDING_HELD2_GATES,
        "ready_prerequisites": [
            "khudaida_source_gate",
            "reduced_charge_neutral_NaCl_amount_lift",
            "cppad_born_ssm_ds_derivative_receipts",
            "closed_public_electrolyte_route_state",
        ],
    }


def evaluate_payload(
    payload: dict[str, Any],
    *,
    require_source_gate: bool = False,
    require_reduced_basis: bool = False,
    require_born_ssm_ds: bool = False,
    require_public_routes_closed: bool = False,
) -> dict[str, Any]:
    blockers = list(payload.get("blockers", []))

    source_gate = payload.get("source_gate", {})
    if require_source_gate:
        if source_gate.get("complete") is not True:
            blockers.append("electrolyte_source_gate_incomplete")
        blockers.extend(str(item) for item in source_gate.get("blockers", []))

    reduced_basis = payload.get("reduced_basis", {})
    if require_reduced_basis:
        if reduced_basis.get("status") != "verified_exact_charge_neutral_lift":
            blockers.append("electrolyte_reduced_basis_missing")
        blockers.extend(str(item) for item in reduced_basis.get("blockers", []))
        threshold = float(reduced_basis.get("charge_balance_threshold", CHARGE_BALANCE_THRESHOLD))
        if float(reduced_basis.get("max_abs_charge_balance", math.inf)) > threshold:
            blockers.append("electrolyte_reduced_basis_charge_balance_exceeds_threshold")
        if reduced_basis.get("basis_species") != BASIS_SPECIES:
            blockers.append("electrolyte_reduced_basis_species_mismatch")
        if reduced_basis.get("native_species") != NATIVE_SPECIES:
            blockers.append("electrolyte_reduced_basis_native_species_mismatch")

    born = payload.get("born_ssm_ds_exactness", {})
    if require_born_ssm_ds:
        if born.get("status") != "verified_cppad_born_ssm_ds_receipts":
            blockers.append("born_ssm_ds_exactness_missing")
        blockers.extend(str(item) for item in born.get("blockers", []))
        if born.get("backend") != "cppad":
            blockers.append("born_ssm_ds_backend_not_cppad")
        if born.get("composition_derivative_backend") != "cppad":
            blockers.append("born_ssm_ds_composition_backend_not_cppad")
        if born.get("solvation_shell_model") is not True:
            blockers.append("born_ssm_ds_solvation_shell_model_inactive")
        if born.get("dielectric_saturation") is not True:
            blockers.append("born_ssm_ds_dielectric_saturation_inactive")
        for field, blocker in (
            ("finite_composition_derivatives", "born_ssm_ds_composition_derivatives_missing"),
            ("finite_fugacity_derivatives", "born_ssm_ds_fugacity_derivatives_missing"),
            ("finite_activity_derivatives", "born_ssm_ds_activity_derivatives_missing"),
            ("finite_parameter_derivatives", "born_ssm_ds_parameter_derivatives_missing"),
        ):
            if born.get(field) is not True:
                blockers.append(blocker)
        if set(born.get("parameter_families", [])) != {"d_born", "f_solv"}:
            blockers.append("born_ssm_ds_parameter_family_mismatch")

    readiness = payload.get("held2_readiness", {})
    if readiness.get("readiness_only") is not True:
        blockers.append("held2_readiness_not_marked_prerequisite_only")
    if readiness.get("full_held2_claimed") is True:
        blockers.append("full_held2_claimed_by_readiness_gate")
    pending = set(str(item) for item in readiness.get("pending_gates", []))
    for gate in PENDING_HELD2_GATES:
        if gate not in pending:
            blockers.append(f"held2_pending_gate_missing:{gate}")

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


def evaluate_readiness(
    case_dir: Path = check_electrolyte_gfpe_gate.DEFAULT_CASE_DIR,
    *,
    require_source_gate: bool = False,
    require_reduced_basis: bool = False,
    require_born_ssm_ds: bool = False,
    require_public_routes_closed: bool = False,
    checker_command: list[str] | None = None,
) -> dict[str, Any]:
    case_dir = Path(case_dir)
    source_gate = _source_gate_payload(case_dir, checker_command)
    payload = {
        "checker": "electrolyte_held2_readiness_gate",
        "case_label": "Khudaida 2026 electrolyte LLE",
        "source_gate": source_gate,
        "reduced_basis": _reduced_basis_payload(case_dir, source_gate),
        "born_ssm_ds_exactness": _born_ssm_ds_payload(),
        "held2_readiness": _held2_readiness_payload(),
        "public_route_state": source_gate.get("public_route_state", {}),
    }
    return evaluate_payload(
        payload,
        require_source_gate=require_source_gate,
        require_reduced_basis=require_reduced_basis,
        require_born_ssm_ds=require_born_ssm_ds,
        require_public_routes_closed=require_public_routes_closed,
    )


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--case-dir", type=Path, default=check_electrolyte_gfpe_gate.DEFAULT_CASE_DIR)
    parser.add_argument("--require-source-gate", action="store_true")
    parser.add_argument("--require-reduced-basis", action="store_true")
    parser.add_argument("--require-born-ssm-ds", action="store_true")
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
        "scripts/validation/check_electrolyte_held2_readiness.py",
        *argv,
    ]
    output = evaluate_readiness(
        args.case_dir,
        require_source_gate=args.require_source_gate or args.require_complete,
        require_reduced_basis=args.require_reduced_basis or args.require_complete,
        require_born_ssm_ds=args.require_born_ssm_ds or args.require_complete,
        require_public_routes_closed=args.require_public_routes_closed or args.require_complete,
        checker_command=checker_command,
    )
    if args.require_complete:
        receipt = output.get("source_gate", {}).get("native_diagnostics", {}).get("native_freshness_receipt", {})
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
