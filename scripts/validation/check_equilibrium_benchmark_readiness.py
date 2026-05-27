from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CASE_DIR = (
    REPO_ROOT / "data" / "reference" / "equilibrium_benchmarks" / "neutral_tp_flash" / "pereira_2012"
)
ACCEPTED_STAGE10_MODEL_FAMILIES = {"PC-SAFT", "ePC-SAFT"}
STAGE9_EVIDENCE_REQUIREMENTS = (
    "deterministic_screening",
    "continuous_tpd_minimization",
    "held_stage_i_stability",
    "held_stage_ii_dual_phase_discovery",
    "held_stage_iii_ipopt_refinement",
)


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _read_csv(path: Path) -> list[dict[str, str]]:
    return list(csv.DictReader(path.read_text(encoding="utf-8").splitlines()))


def _float_or_none(value: str | None) -> float | None:
    if value is None:
        return None
    stripped = value.strip()
    if not stripped or stripped == "not_evaluated":
        return None
    return float(stripped)


def _phase_rows_by_case(phase_rows: list[dict[str, str]]) -> dict[str, dict[str, dict[str, str]]]:
    by_case: dict[str, dict[str, dict[str, str]]] = {}
    for row in phase_rows:
        by_case.setdefault(row["case_key"], {})[row["phase"]] = row
    return by_case


def _composition(row: dict[str, str]) -> tuple[float, float]:
    return float(row["x1"]), float(row["x2"])


def _composition_sum(row: dict[str, str]) -> float:
    return float(row["composition_sum"])


def _lever_fraction(feed: tuple[float, float], vapor: tuple[float, float], liquid: tuple[float, float]) -> float:
    denominator = vapor[0] - liquid[0]
    if abs(denominator) <= 1.0e-15:
        raise ValueError("phase split cannot determine a lever-rule vapor fraction")
    return (feed[0] - liquid[0]) / denominator


def _material_balance_residual(
    feed: tuple[float, float],
    vapor: tuple[float, float],
    liquid: tuple[float, float],
    vapor_fraction: float,
) -> float:
    liquid_fraction = 1.0 - vapor_fraction
    return max(
        abs(feed[index] - (vapor_fraction * vapor[index] + liquid_fraction * liquid[index]))
        for index in range(2)
    )


def _case_blockers(metadata: dict[str, Any], row: dict[str, Any]) -> list[str]:
    blockers = []
    source_model_family = str(metadata.get("source_model_family", ""))
    if source_model_family not in ACCEPTED_STAGE10_MODEL_FAMILIES:
        blockers.append("model_family_mismatch")
    if str(metadata.get("runtime_model_support", "")) == "absent_from_epcsaft":
        blockers.append("saft_vr_runtime_absent")
    if row["reported_feed_status"] != "normalized":
        blockers.append("published_second_feed_composition_not_normalized")
    return list(dict.fromkeys(blockers))


def _computed_material_balance_rows(metadata: dict[str, Any], case_dir: Path) -> list[dict[str, Any]]:
    by_case = _phase_rows_by_case(_read_csv(case_dir / "phase_splits.csv"))
    rows: list[dict[str, Any]] = []
    for case_key in sorted(by_case):
        phases = by_case[case_key]
        feed_row = phases["feed"]
        vapor = _composition(phases["vapor"])
        liquid = _composition(phases["liquid"])
        feed = _composition(feed_row)
        feed_sum = _composition_sum(feed_row)
        normalized = math.isclose(feed_sum, 1.0, rel_tol=0.0, abs_tol=1.0e-12)
        row: dict[str, Any] = {
            "case_key": case_key,
            "reported_feed_status": "normalized" if normalized else "not_normalized",
            "material_balance_status": "blocked_by_published_feed",
            "vapor_fraction": None,
            "liquid_fraction": None,
            "max_abs_material_balance_residual": None,
            "material_balance_eligible": False,
            "proof_eligible": False,
            "blockers": [],
        }
        if normalized:
            vapor_fraction = _lever_fraction(feed, vapor, liquid)
            residual = _material_balance_residual(feed, vapor, liquid, vapor_fraction)
            row.update(
                {
                    "material_balance_status": "feasible_from_reported_feed",
                    "vapor_fraction": vapor_fraction,
                    "liquid_fraction": 1.0 - vapor_fraction,
                    "max_abs_material_balance_residual": residual,
                    "material_balance_eligible": residual <= 1.0e-10 and 0.0 < vapor_fraction < 1.0,
                }
            )
        row["blockers"] = _case_blockers(metadata, row)
        row["proof_eligible"] = row["material_balance_eligible"] and not row["blockers"]
        rows.append(row)
    return rows


def _stored_bool(value: str) -> bool:
    return value.strip().lower() == "true"


def _stored_blockers(value: str) -> list[str]:
    return [] if not value.strip() else value.split(";")


def _compare_stored_readiness(
    computed_rows: list[dict[str, Any]],
    stored_rows: list[dict[str, str]],
) -> list[dict[str, Any]]:
    stored_by_case = {row["case_key"]: row for row in stored_rows}
    mismatches: list[dict[str, Any]] = []
    for computed in computed_rows:
        case_key = str(computed["case_key"])
        stored = stored_by_case.get(case_key)
        if stored is None:
            mismatches.append({"case_key": case_key, "field": "case_key", "stored": None, "computed": case_key})
            continue
        checks: tuple[tuple[str, Any, Any], ...] = (
            ("reported_feed_status", stored["reported_feed_status"], computed["reported_feed_status"]),
            ("material_balance_status", stored["material_balance_status"], computed["material_balance_status"]),
            ("vapor_fraction", _float_or_none(stored["vapor_fraction"]), computed["vapor_fraction"]),
            ("liquid_fraction", _float_or_none(stored["liquid_fraction"]), computed["liquid_fraction"]),
            (
                "max_abs_material_balance_residual",
                _float_or_none(stored["max_abs_material_balance_residual"]),
                computed["max_abs_material_balance_residual"],
            ),
            ("material_balance_eligible", _stored_bool(stored["material_balance_eligible"]), computed["material_balance_eligible"]),
            ("proof_eligible", _stored_bool(stored["proof_eligible"]), computed["proof_eligible"]),
            ("blockers", _stored_blockers(stored["blockers"]), computed["blockers"]),
        )
        for field, stored_value, computed_value in checks:
            if _values_match(stored_value, computed_value):
                continue
            mismatches.append(
                {
                    "case_key": case_key,
                    "field": field,
                    "stored": stored_value,
                    "computed": computed_value,
                }
            )
    return mismatches


def _values_match(left: Any, right: Any) -> bool:
    if left is None or right is None:
        return left is None and right is None
    if isinstance(left, float) or isinstance(right, float):
        return math.isclose(float(left), float(right), rel_tol=1.0e-10, abs_tol=1.0e-12)
    return left == right


def _computed_feed_correction_rows(case_dir: Path) -> list[dict[str, Any]]:
    by_case = _phase_rows_by_case(_read_csv(case_dir / "phase_splits.csv"))
    rows: list[dict[str, Any]] = []
    for case_key, phases in sorted(by_case.items()):
        feed = phases["feed"]
        if math.isclose(_composition_sum(feed), 1.0, rel_tol=0.0, abs_tol=1.0e-12):
            continue
        vapor = _composition(phases["vapor"])
        liquid = _composition(phases["liquid"])
        candidate_feed = (float(feed["x1"]), 1.0 - float(feed["x1"]))
        vapor_fraction = _lever_fraction(candidate_feed, vapor, liquid)
        rows.append(
            {
                "case_key": case_key,
                "candidate_x1": candidate_feed[0],
                "candidate_x2": candidate_feed[1],
                "candidate_source": "material_balance_from_reported_phase_splits",
                "correction_status": "inferred_not_source_confirmed",
                "candidate_vapor_fraction": vapor_fraction,
                "candidate_liquid_fraction": 1.0 - vapor_fraction,
                "max_abs_material_balance_residual": _material_balance_residual(
                    candidate_feed,
                    vapor,
                    liquid,
                    vapor_fraction,
                ),
            }
        )
    return rows


def evaluate_case_dir(case_dir: Path) -> dict[str, Any]:
    metadata = _read_json(case_dir / "metadata.json")
    computed_rows = _computed_material_balance_rows(metadata, case_dir)
    stored_readiness = _read_csv(case_dir / "material_balance_readiness.csv")
    mismatches = _compare_stored_readiness(computed_rows, stored_readiness)
    blockers = list(dict.fromkeys(reason for row in computed_rows for reason in row["blockers"]))
    proof_readiness = metadata.get("proof_readiness", {})
    stage9_evidence_required = bool(proof_readiness.get("stage9_evidence_path_required", False))
    stage9_evidence_verified = bool(proof_readiness.get("stage9_evidence_path_verified", False))
    if stage9_evidence_required and not stage9_evidence_verified:
        blockers.append("stage9_evidence_path_not_verified")
    if bool(proof_readiness.get("source_confirmed_feed_correction_required", False)):
        blockers.append("source_confirmed_feed_correction_required")
    if mismatches:
        blockers.append("stored_material_balance_readiness_mismatch")
    executable = (
        str(metadata.get("source_model_family", "")) in ACCEPTED_STAGE10_MODEL_FAMILIES
        and all(bool(row["proof_eligible"]) for row in computed_rows)
        and not mismatches
        and (not stage9_evidence_required or stage9_evidence_verified)
        and not bool(proof_readiness.get("source_confirmed_feed_correction_required", False))
    )
    return {
        "name": metadata.get("name", ""),
        "case_label": metadata.get("case_label", ""),
        "family_label": metadata.get("family_label", ""),
        "source_model_family": metadata.get("source_model_family", ""),
        "proof_status": "executable" if executable else "blocked",
        "executable": executable,
        "stage9_evidence_path_required": stage9_evidence_required,
        "stage9_evidence_path_verified": stage9_evidence_verified,
        "stage9_evidence": {key: "required_not_verified" for key in STAGE9_EVIDENCE_REQUIREMENTS},
        "blockers": list(dict.fromkeys(blockers)),
        "cases": computed_rows,
        "feed_correction_candidates": _computed_feed_correction_rows(case_dir),
        "stored_readiness_consistent": not mismatches,
        "stored_readiness_mismatches": mismatches,
    }


def _print_human(payload: dict[str, Any]) -> None:
    print(f"{payload['case_label']}: {payload['proof_status']}")
    print(f"  executable: {str(payload['executable']).lower()}")
    print(f"  source model: {payload['source_model_family']}")
    if payload["blockers"]:
        print("  blockers: " + ", ".join(str(item) for item in payload["blockers"]))
    for case in payload["cases"]:
        print(
            "  "
            + str(case["case_key"])
            + f": {case['material_balance_status']}, proof_eligible={str(case['proof_eligible']).lower()}"
        )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Check equilibrium benchmark readiness for Stage 10 proof use.")
    parser.add_argument("--case-dir", type=Path, default=DEFAULT_CASE_DIR)
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    parser.add_argument(
        "--require-executable",
        action="store_true",
        help="Return a failing exit code when the fixture is not executable proof evidence.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    payload = evaluate_case_dir(args.case_dir)
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        _print_human(payload)
    if not payload["stored_readiness_consistent"]:
        return 1
    if args.require_executable and not payload["executable"]:
        print(
            f"{payload['case_label']} is not an executable Stage 10 proof fixture.",
            file=sys.stderr,
        )
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
