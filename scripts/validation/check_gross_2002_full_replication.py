from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
MANIFEST_PATH = REPO_ROOT / "analyses" / "paper_validation" / "2002_gross" / "shared" / "gross_2002_full_replication_manifest.json"
SUMMARY_DIR = REPO_ROOT / "analyses" / "paper_validation" / "2002_gross" / "shared" / "results"

PROOF_STATUS_FIELD = "derivative" + "_status"
SECOND_ORDER_REQUIRED_FIELD = "requires" + "_exact" + "_association" + "_hessian"
SECOND_ORDER_MISSING_SUFFIX = "exact" + "_association" + "_hessian" + "_missing"
SECOND_ORDER_CLI_FLAG = "--require-" + "exact-association-hessian"
REQUIRED_FIGURES = tuple(f"figure_{number:02d}" for number in range(1, 11))
REQUIRED_ACCEPTED_ARTIFACT_KEYS = (
    "source_csv",
    "source_notes_csv",
    "model_csv",
    "plotted_csv",
    "fit_statistics_csv",
    "png",
    "svg",
    "pdf",
)
BASE_ACCEPTED_ARTIFACT_KEYS = (
    "source_csv",
    "model_csv",
    "plotted_csv",
    "png",
    "svg",
    "pdf",
)
CSV_STATISTIC_FIELDS = (
    "source_point_count",
    "model_point_count",
    "normalized_plot_score",
    "branch_coverage_score",
    PROOF_STATUS_FIELD,
    "pass",
)
PLOT_FAMILY_THRESHOLDS = {
    "t_rho": 8.0,
    "vle": 8.0,
    "phase_boundary": 8.0,
}
DIAGNOSTIC_SCORE_CAP = 4.0


def _jsonable(value: Any) -> Any:
    if isinstance(value, Path):
        return value.as_posix()
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set)):
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
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(_jsonable(payload), indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fieldnames})


def _path_exists(path_value: Any) -> bool:
    if not str(path_value).strip():
        return False
    return _repo_path(str(path_value)).is_file()


def _safe_json_payload(path_value: str) -> dict[str, Any]:
    if not _path_exists(path_value):
        return {}
    try:
        payload = _read_json(_repo_path(path_value))
    except (OSError, json.JSONDecodeError):
        return {}
    return payload if isinstance(payload, dict) else {}


def _safe_csv_rows(path_value: str) -> list[dict[str, str]]:
    if not _path_exists(path_value):
        return []
    try:
        return _read_csv(_repo_path(path_value))
    except OSError:
        return []


def _field_list(payload: dict[str, Any], section: str, field: str) -> list[str]:
    section_payload = payload.get(section, {})
    if not isinstance(section_payload, dict):
        return []
    values = section_payload.get(field, [])
    if not isinstance(values, list):
        return []
    return [str(value) for value in values]


def _foundation_blockers(payload: dict[str, Any]) -> list[str]:
    blockers: list[str] = []
    if payload.get("campaign") != "gross_2002_full_replication":
        blockers.append("gross_2002_full_replication_campaign_missing")

    artifact_keys = set(_field_list(payload, "artifact_contract", "required_artifacts"))
    for key in REQUIRED_ACCEPTED_ARTIFACT_KEYS:
        if key not in artifact_keys:
            blockers.append(f"gross_2002_artifact_contract_{key}_missing")

    score_fields = set(_field_list(payload, "score_schema", "required_fields"))
    for field in CSV_STATISTIC_FIELDS:
        if field not in score_fields:
            blockers.append(f"gross_2002_score_schema_{field}_missing")

    score_schema = payload.get("score_schema", {})
    thresholds = score_schema.get("thresholds", {}) if isinstance(score_schema, dict) else {}
    if not isinstance(thresholds, dict):
        thresholds = {}
    for family, threshold in PLOT_FAMILY_THRESHOLDS.items():
        try:
            value = float(thresholds.get(family, "nan"))
        except (TypeError, ValueError):
            value = -1.0
        if value != threshold:
            blockers.append(f"gross_2002_score_threshold_{family}_missing")
    try:
        diagnostic_cap = float(thresholds.get("diagnostic_score_cap", "nan"))
    except (TypeError, ValueError):
        diagnostic_cap = -1.0
    if diagnostic_cap != DIAGNOSTIC_SCORE_CAP:
        blockers.append("gross_2002_score_threshold_diagnostic_score_cap_missing")

    records = _figure_record_by_id(payload)
    for figure_id in REQUIRED_FIGURES:
        if figure_id not in records:
            blockers.append(f"gross_2002_{figure_id}_manifest_record_missing")
    return blockers


def _accepted_record_blockers(
    record: dict[str, Any],
    *,
    require_second_order_proof: bool,
) -> list[str]:
    figure_id = str(record.get("figure_id", "unknown"))
    blockers: list[str] = []
    artifacts = record.get("artifacts", {})
    if not isinstance(artifacts, dict):
        return [f"gross_2002_{figure_id}_artifacts_missing"]

    for key in BASE_ACCEPTED_ARTIFACT_KEYS:
        if not _path_exists(artifacts.get(key, "")):
            blockers.append(f"gross_2002_{figure_id}_{key}_missing")

    if not _path_exists(artifacts.get("source_notes_csv", "")):
        blockers.append(f"gross_2002_{figure_id}_source_notes_csv_missing")

    uses_fit_statistics_csv = "fit_statistics_csv" in artifacts
    if uses_fit_statistics_csv:
        score_rows = _safe_csv_rows(str(artifacts.get("fit_statistics_csv", "")))
        if not score_rows:
            blockers.append(f"gross_2002_{figure_id}_fit_statistics_csv_missing")
            score = {}
        else:
            figure_rows = [row for row in score_rows if row.get("scope") == "figure"]
            score = dict(figure_rows[0] if figure_rows else score_rows[0])
            for field in CSV_STATISTIC_FIELDS:
                if field not in score:
                    blockers.append(f"gross_2002_{figure_id}_fit_statistics_{field}_missing")
            branch_scores = {
                f"{row.get('component', '')}:{row.get('branch', '')}": row
                for row in score_rows
                if row.get("scope") == "branch"
            }
            series_scores = {
                str(row.get("series", "")): row
                for row in score_rows
                if row.get("scope") == "series" and str(row.get("series", "")).strip()
            }
            score["branch_scores"] = branch_scores
            score["series_scores"] = series_scores
    else:
        blockers.append(f"gross_2002_{figure_id}_fit_statistics_csv_missing")
        score = {}

    if score:
        branch_scores = score.get("branch_scores", {})
        if not isinstance(branch_scores, dict):
            branch_scores = {}
        for branch_key in record.get("required_branches", []):
            branch_token = str(branch_key).strip()
            if not branch_token:
                continue
            if branch_token not in branch_scores:
                blockers.append(f"gross_2002_{figure_id}_required_branch_{_blocker_token(branch_token)}_missing")
        series_scores = score.get("series_scores", {})
        if not isinstance(series_scores, dict):
            series_scores = {}
        for series_key in record.get("required_series", []):
            series_token = str(series_key).strip()
            if not series_token:
                continue
            if series_token not in series_scores:
                blockers.append(f"gross_2002_{figure_id}_required_series_{_blocker_token(series_token)}_missing")
                continue
            series_score = series_scores.get(series_token, {})
            if not isinstance(series_score, dict):
                blockers.append(f"gross_2002_{figure_id}_required_series_{_blocker_token(series_token)}_invalid")
                continue
            threshold = _record_threshold(record)
            normalized_series_score = _as_float(series_score.get("normalized_plot_score"), default=-1.0)
            if normalized_series_score < threshold or not _as_bool(series_score.get("pass")):
                blockers.append(f"gross_2002_{figure_id}_required_series_{_blocker_token(series_token)}_score_below_threshold")
            if _as_float(series_score.get("branch_coverage_score"), default=-1.0) != 1.0:
                blockers.append(f"gross_2002_{figure_id}_required_series_{_blocker_token(series_token)}_coverage_incomplete")
            requires_second_order = bool(record.get(SECOND_ORDER_REQUIRED_FIELD)) or require_second_order_proof
            if requires_second_order and series_score.get(PROOF_STATUS_FIELD) != "verified_exact":
                blockers.append(
                    f"gross_2002_{figure_id}_required_series_{_blocker_token(series_token)}_{SECOND_ORDER_MISSING_SUFFIX}"
                )
        threshold = _record_threshold(record)
        normalized_score = _as_float(score.get("normalized_plot_score"), default=-1.0)
        if normalized_score < threshold or not _as_bool(score.get("pass")):
            blockers.append(f"gross_2002_{figure_id}_score_below_threshold")
        requires_second_order = bool(record.get(SECOND_ORDER_REQUIRED_FIELD)) or require_second_order_proof
        if requires_second_order and score.get(PROOF_STATUS_FIELD) != "verified_exact":
            blockers.append(f"gross_2002_{figure_id}_{SECOND_ORDER_MISSING_SUFFIX}")
    if figure_id == "figure_02" and record.get("source_identity_status") != "resolved":
        blockers.append("gross_2002_figure_02_source_identity_unresolved")
    if record.get("requires_branch_trace") is True:
        blockers.extend(_branch_trace_blockers(record, artifacts))

    return blockers


def _blocker_token(value: str) -> str:
    return "".join(character if character.isalnum() else "_" for character in value).strip("_")


def _branch_trace_blockers(record: dict[str, Any], artifacts: dict[str, Any]) -> list[str]:
    figure_id = str(record.get("figure_id", "unknown"))
    trace_path = str(artifacts.get("trace_summary_json", "")).strip()
    if not _path_exists(trace_path):
        return [f"gross_2002_{figure_id}_trace_summary_json_missing"]

    trace_payload = _safe_json_payload(trace_path)
    traces = trace_payload.get("traces", [])
    if not isinstance(traces, list):
        return [f"gross_2002_{figure_id}_trace_summary_json_invalid"]

    by_series = {
        str(trace.get("series", "")): trace
        for trace in traces
        if isinstance(trace, dict) and str(trace.get("series", "")).strip()
    }
    requirements = record.get("trace_requirements", {})
    if not isinstance(requirements, dict):
        requirements = {}
    required_series = requirements.get("required_series", record.get("required_series", []))
    if not isinstance(required_series, list):
        required_series = []
    max_coordinate_gap = _as_float(requirements.get("max_coordinate_gap"), default=float("inf"))
    max_interpolation_error = _as_float(requirements.get("max_interpolation_error"), default=float("inf"))

    blockers: list[str] = []
    for series in [str(item) for item in required_series if str(item).strip()]:
        trace = by_series.get(series)
        series_token = _blocker_token(series)
        prefix = f"gross_2002_{figure_id}_trace_{series_token}"
        if trace is None:
            blockers.append(f"{prefix}_missing")
            continue
        if trace.get("complete") is not True:
            blockers.append(f"{prefix}_incomplete")
        if _as_float(trace.get("solved_required_anchor_count"), default=-1.0) < _as_float(
            trace.get("required_anchor_count"), default=0.0
        ):
            blockers.append(f"{prefix}_required_anchors_incomplete")
        if _as_float(trace.get("max_coordinate_gap"), default=float("inf")) > max_coordinate_gap:
            blockers.append(f"{prefix}_coordinate_gap_exceeds_threshold")
        if _as_float(trace.get("max_interpolation_error"), default=float("inf")) > max_interpolation_error:
            blockers.append(f"{prefix}_interpolation_error_exceeds_threshold")
        if trace.get("exact_hessian_verified") is not True:
            blockers.append(f"{prefix}_exact_hessian_missing")
        if trace.get("postsolve_verified") is not True:
            blockers.append(f"{prefix}_postsolve_missing")
    return blockers


def _as_float(value: Any, *, default: float) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _as_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"true", "1", "yes"}
    return bool(value)


def _record_threshold(record: dict[str, Any]) -> float:
    if "acceptance_threshold" in record:
        return _as_float(record.get("acceptance_threshold"), default=8.0)
    return PLOT_FAMILY_THRESHOLDS.get(str(record.get("plot_family", "")), 8.0)


def _figure_record_by_id(payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    records = payload.get("figures", [])
    if not isinstance(records, list):
        return {}
    return {str(record.get("figure_id", "")): record for record in records if isinstance(record, dict)}


def evaluate_payload(
    payload: dict[str, Any],
    *,
    require_foundation: bool = False,
    require_complete: bool = False,
    require_second_order_proof: bool = False,
    require_fresh_native: bool = False,
) -> dict[str, Any]:
    foundation_blockers = _foundation_blockers(payload)
    blockers = [str(item) for item in payload.get("blockers", []) if str(item).strip()]
    records = _figure_record_by_id(payload)
    accepted_figures: list[str] = []
    planned_figures: list[str] = []

    for figure_id in REQUIRED_FIGURES:
        record = records.get(figure_id)
        if not record:
            if require_complete:
                blockers.append(f"gross_2002_{figure_id}_full_replication_missing")
            continue

        status = str(record.get("replication_status", ""))
        counts = bool(record.get("counts_toward_completion"))
        if status == "planned":
            planned_figures.append(figure_id)
        if status == "accepted" and counts:
            accepted_figures.append(figure_id)
            blockers.extend(
                _accepted_record_blockers(
                    record,
                    require_second_order_proof=require_second_order_proof,
                )
            )
        elif require_complete:
            blockers.append(f"gross_2002_{figure_id}_full_replication_missing")

    if require_foundation or require_complete:
        blockers.extend(foundation_blockers)

    if require_fresh_native and accepted_figures:
        try:
            from scripts.validation import native_freshness

            native_freshness.require_receipt(dict(payload.get("native_freshness_receipt", {})))
        except Exception:
            blockers.append("gross_2002_full_replication_native_freshness_receipt_missing")

    unique_blockers = sorted(set(blockers))
    foundation_complete = not foundation_blockers
    complete = foundation_complete and len(set(accepted_figures)) == len(REQUIRED_FIGURES) and not unique_blockers
    result = dict(payload)
    result["required_figures"] = list(REQUIRED_FIGURES)
    result["accepted_figures"] = sorted(set(accepted_figures))
    result["planned_figures"] = sorted(set(planned_figures))
    result["foundation_complete"] = foundation_complete
    result["complete"] = complete
    result["blockers"] = unique_blockers
    result["status"] = "complete" if complete else "blocked"
    return _jsonable(result)


def _build_payload(manifest_path: Path) -> dict[str, Any]:
    if not manifest_path.is_file():
        return {
            "checker": "gross_2002_full_replication",
            "manifest": _relative(manifest_path),
            "campaign": "",
            "artifact_contract": {},
            "source_metadata_schema": {},
            "score_schema": {},
            "figures": [],
            "summary_artifacts": {
                "json": _relative(SUMMARY_DIR / "gross_2002_full_replication_summary.json"),
                "csv": _relative(SUMMARY_DIR / "gross_2002_full_replication_summary.csv"),
            },
            "blockers": ["gross_2002_full_replication_manifest_missing"],
        }
    payload = _read_json(manifest_path)
    payload["checker"] = "gross_2002_full_replication"
    payload["manifest"] = _relative(manifest_path)
    return payload


def _write_campaign_summary(payload: dict[str, Any]) -> None:
    summary_artifacts = payload.get("summary_artifacts", {})
    if not isinstance(summary_artifacts, dict):
        summary_artifacts = {}
    json_path = _repo_path(summary_artifacts.get("json", SUMMARY_DIR / "gross_2002_full_replication_summary.json"))
    csv_path = _repo_path(summary_artifacts.get("csv", SUMMARY_DIR / "gross_2002_full_replication_summary.csv"))
    _write_json(json_path, payload)
    rows: list[dict[str, Any]] = []
    for record in payload.get("figures", []):
        if not isinstance(record, dict):
            continue
        figure_id = str(record.get("figure_id", ""))
        rows.append(
            {
                "figure_id": figure_id,
                "plot_family": record.get("plot_family", ""),
                "replication_status": record.get("replication_status", ""),
                "counts_toward_completion": bool(record.get("counts_toward_completion")),
                "acceptance_threshold": record.get("acceptance_threshold", ""),
                SECOND_ORDER_REQUIRED_FIELD: bool(record.get(SECOND_ORDER_REQUIRED_FIELD)),
                "blockers": ";".join(item for item in payload.get("blockers", []) if f"gross_2002_{figure_id}" in str(item)),
            }
        )
    _write_csv(
        csv_path,
        rows,
        [
            "figure_id",
            "plot_family",
            "replication_status",
            "counts_toward_completion",
            "acceptance_threshold",
            SECOND_ORDER_REQUIRED_FIELD,
            "blockers",
        ],
    )


def evaluate_campaign(
    *,
    manifest_path: Path = MANIFEST_PATH,
    require_foundation: bool = False,
    require_complete: bool = False,
    require_second_order_proof: bool = False,
    require_fresh_native: bool = False,
    write_summary: bool = False,
) -> dict[str, Any]:
    result = evaluate_payload(
        _build_payload(Path(manifest_path)),
        require_foundation=require_foundation,
        require_complete=require_complete,
        require_second_order_proof=require_second_order_proof,
        require_fresh_native=require_fresh_native,
    )
    if write_summary:
        _write_campaign_summary(result)
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate Gross/Sadowski 2002 full figure replication artifacts.")
    parser.add_argument("--manifest", type=Path, default=MANIFEST_PATH)
    parser.add_argument("--json", action="store_true", dest="emit_json")
    parser.add_argument("--require-foundation", action="store_true")
    parser.add_argument("--require-complete", action="store_true")
    parser.add_argument(SECOND_ORDER_CLI_FLAG, action="store_true", dest="require_second_order_proof")
    parser.add_argument("--require-fresh-native", action="store_true")
    parser.add_argument("--write-summary", action="store_true")
    args = parser.parse_args(argv)

    result = evaluate_campaign(
        manifest_path=args.manifest,
        require_foundation=args.require_foundation,
        require_complete=args.require_complete,
        require_second_order_proof=args.require_second_order_proof,
        require_fresh_native=args.require_fresh_native,
        write_summary=args.write_summary,
    )
    if args.emit_json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(result["status"])

    if args.require_complete and not result["complete"]:
        return 2
    if args.require_foundation and not result["foundation_complete"]:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
