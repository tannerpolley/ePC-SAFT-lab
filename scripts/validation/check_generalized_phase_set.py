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
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
NEUTRAL_MULTIPHASE_ROUTE = "neutral_multiphase_nonassoc"
REQUIRED_RECORD_FIELDS = {
    "record_id",
    "phase_count",
    "phase_index",
    "phase_kind",
    "phase_role",
    "source",
    "phase_amount_total",
    "phase_fraction",
    "volume",
    "density",
    "composition",
    "objective",
    "tpd",
    "feasibility_status",
    "selection_status",
    "rejection_reason",
    "phase_set_status",
    "mass_balance_feasible",
    "stability_accepted",
    "candidate_completeness_accepted",
}


def _record_composition_key(record: dict[str, Any], *, tolerance: float = 1.0e-8) -> tuple[float, ...]:
    composition = record.get("composition")
    if not isinstance(composition, list) or not composition:
        return ()
    return tuple(round(float(value) / tolerance) * tolerance for value in composition)


def evaluate_payload(payload: dict[str, Any]) -> dict[str, Any]:
    blockers: list[str] = []
    public_routes = payload.get("public_routes", [])
    if NEUTRAL_MULTIPHASE_ROUTE in public_routes:
        blockers.append("neutral_multiphase_public_route_exposed")

    postsolve = payload.get("postsolve")
    if not isinstance(postsolve, dict):
        blockers.append("missing_postsolve")
        postsolve = {}
    records = postsolve.get("phase_set_records")
    if not isinstance(records, list) or not records:
        blockers.append("missing_phase_set_records")
        records = []

    selected_records: list[dict[str, Any]] = []
    rejected_records: list[dict[str, Any]] = []
    selected_keys: set[tuple[float, ...]] = set()
    for record in records:
        if not isinstance(record, dict):
            blockers.append("malformed_phase_set_record:row")
            continue
        for field in sorted(REQUIRED_RECORD_FIELDS):
            if field not in record:
                blockers.append(f"malformed_phase_set_record:{field}")
                break
        if record.get("phase_count") != 3:
            blockers.append("non_three_phase_record")
        composition = record.get("composition")
        if isinstance(composition, list):
            total = sum(float(value) for value in composition)
            if not math.isfinite(total) or abs(total - 1.0) > 1.0e-6:
                blockers.append("composition_not_normalized")
        status = record.get("selection_status")
        if status == "selected":
            selected_records.append(record)
            key = _record_composition_key(record)
            if key in selected_keys:
                blockers.append("duplicate_selected_phase_compositions")
            selected_keys.add(key)
        elif status == "rejected":
            rejected_records.append(record)
            if record.get("rejection_reason") in ("", None, "accepted"):
                blockers.append("missing_rejection_reason")
        else:
            blockers.append("unknown_phase_set_selection_status")

    if len(selected_records) < 3:
        blockers.append("missing_selected_three_phase_rows")
    if not rejected_records:
        blockers.append("missing_rejected_candidate_rows")
    if postsolve.get("phase_set_mass_balance_feasible") is not True:
        blockers.append("mass_balance_infeasible")
    if postsolve.get("candidate_completeness_accepted") is not True:
        blockers.append("candidate_completeness_not_accepted")
    if postsolve.get("stability_accepted") is not True:
        blockers.append("stability_not_accepted")
    if postsolve.get("phase_set_status") != "phase_set_certified":
        blockers.append("phase_set_not_certified")
    if float(postsolve.get("phase_distance", 0.0) or 0.0) <= 0.0:
        blockers.append("collapsed_phase_distance")

    blockers = sorted(set(blockers))
    return {
        "complete": not blockers,
        "blockers": blockers,
        "record_summary": {
            "total": len(records),
            "selected": len(selected_records),
            "rejected": len(rejected_records),
        },
        "public_route_exposure": NEUTRAL_MULTIPHASE_ROUTE in public_routes,
    }


def _symmetric_ternary_nonassociating_mixture() -> Any:
    from epcsaft.state.native_adapter import ePCSAFTMixture

    params = {
        "m": np.asarray([1.5, 1.5, 1.5], dtype=float),
        "s": np.asarray([3.7, 3.7, 3.7], dtype=float),
        "e": np.asarray([220.0, 220.0, 220.0], dtype=float),
        "k_ij": np.asarray(
            [
                [0.0, 0.8, 0.8],
                [0.8, 0.0, 0.8],
                [0.8, 0.8, 0.0],
            ],
            dtype=float,
        ),
    }
    return ePCSAFTMixture.from_params(params, species=["A", "B", "C"])


def _run_internal_multiphase_postsolve() -> dict[str, Any]:
    from scripts.dev.native_runtime_env import apply_native_runtime_env

    apply_native_runtime_env(os.environ)

    import epcsaft_equilibrium
    from epcsaft_equilibrium._native import extension_native_core

    core = extension_native_core()
    mix = _symmetric_ternary_nonassociating_mixture()
    postsolve = core._native_neutral_tpd_phase_discovery(
        mix._native,
        200.0,
        1.0e6,
        [1.0 / 3.0, 1.0 / 3.0, 1.0 / 3.0],
        [0, 0, 0],
        1.0e-6,
        1.0e-6,
    )
    return {
        "public_routes": epcsaft_equilibrium.capabilities()["public_routes"],
        "postsolve": postsolve,
    }


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--require-complete", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_arg_parser().parse_args(argv)
    payload = _run_internal_multiphase_postsolve()
    result = evaluate_payload(payload)
    output = {
        **result,
        "route": NEUTRAL_MULTIPHASE_ROUTE,
        "checker": "generalized_phase_set",
        "scope": "internal_neutral_multiphase_diagnostics",
    }
    if args.json:
        print(json.dumps(output, indent=2, sort_keys=True))
    else:
        print(f"complete={output['complete']} blockers={','.join(output['blockers'])}")
    if args.require_complete and not output["complete"]:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
