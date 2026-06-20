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

REQUIRED_FIGURES = tuple(f"figure_{number:02d}" for number in range(1, 11))
REQUIRED_ACCEPTED_ARTIFACT_KEYS = (
    "source_csv",
    "source_metadata_json",
    "digitization_qa_overlay",
    "model_csv",
    "plotted_csv",
    "score_json",
    "summary_json",
    "png",
    "svg",
    "sidecar",
)
REQUIRED_SOURCE_METADATA_FIELDS = (
    "provenance",
    "axis_calibration",
    "units",
    "series_labels",
    "digitization_uncertainty",
    "qa_overlay",
)
REQUIRED_SCORE_FIELDS = (
    "source_point_count",
    "model_point_count",
    "rmse_axis",
    "max_axis_error",
    "normalized_plot_score",
    "branch_coverage_score",
    "derivative_status",
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

    metadata_fields = set(_field_list(payload, "source_metadata_schema", "required_fields"))
    for field in REQUIRED_SOURCE_METADATA_FIELDS:
        if field not in metadata_fields:
            blockers.append(f"gross_2002_source_metadata_schema_{field}_missing")

    score_fields = set(_field_list(payload, "score_schema", "required_fields"))
    for field in REQUIRED_SCORE_FIELDS:
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
    require_exact_association_hessian: bool,
) -> list[str]:
    figure_id = str(record.get("figure_id", "unknown"))
    blockers: list[str] = []
    artifacts = record.get("artifacts", {})
    if not isinstance(artifacts, dict):
        return [f"gross_2002_{figure_id}_artifacts_missing"]

    for key in REQUIRED_ACCEPTED_ARTIFACT_KEYS:
        if not _path_exists(artifacts.get(key, "")):
            blockers.append(f"gross_2002_{figure_id}_{key}_missing")

    metadata_path = str(artifacts.get("source_metadata_json", ""))
    metadata = _safe_json_payload(metadata_path)
    if metadata:
        for field in REQUIRED_SOURCE_METADATA_FIELDS:
            if field not in metadata:
                blockers.append(f"gross_2002_{figure_id}_source_metadata_{field}_missing")

    score_path = str(artifacts.get("score_json", ""))
    score = _safe_json_payload(score_path)
    if score:
        for field in REQUIRED_SCORE_FIELDS:
            if field not in score:
                blockers.append(f"gross_2002_{figure_id}_score_{field}_missing")
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
            if normalized_series_score < threshold or series_score.get("pass") is not True:
                blockers.append(f"gross_2002_{figure_id}_required_series_{_blocker_token(series_token)}_score_below_threshold")
            if _as_float(series_score.get("branch_coverage_score"), default=-1.0) != 1.0:
                blockers.append(f"gross_2002_{figure_id}_required_series_{_blocker_token(series_token)}_coverage_incomplete")
            requires_exact = bool(record.get("requires_exact_association_hessian")) or require_exact_association_hessian
            if requires_exact and series_score.get("derivative_status") != "verified_exact":
                blockers.append(f"gross_2002_{figure_id}_required_series_{_blocker_token(series_token)}_exact_association_hessian_missing")
        threshold = _record_threshold(record)
        normalized_score = _as_float(score.get("normalized_plot_score"), default=-1.0)
        if normalized_score < threshold or score.get("pass") is not True:
            blockers.append(f"gross_2002_{figure_id}_score_below_threshold")
        requires_exact = bool(record.get("requires_exact_association_hessian")) or require_exact_association_hessian
        if requires_exact and score.get("derivative_status") != "verified_exact":
            blockers.append(f"gross_2002_{figure_id}_exact_association_hessian_missing")
    if figure_id == "figure_02" and record.get("source_identity_status") != "resolved":
        blockers.append("gross_2002_figure_02_source_identity_unresolved")
    if figure_id == "figure_02" and not _path_exists(artifacts.get("source_identity_json", "")):
        blockers.append("gross_2002_figure_02_source_identity_json_missing")

    return blockers


def _blocker_token(value: str) -> str:
    return "".join(character if character.isalnum() else "_" for character in value).strip("_")


def _as_float(value: Any, *, default: float) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


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
    require_exact_association_hessian: bool = False,
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
                    require_exact_association_hessian=require_exact_association_hessian,
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
                "requires_exact_association_hessian": bool(record.get("requires_exact_association_hessian")),
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
            "requires_exact_association_hessian",
            "blockers",
        ],
    )


def evaluate_campaign(
    *,
    manifest_path: Path = MANIFEST_PATH,
    require_foundation: bool = False,
    require_complete: bool = False,
    require_exact_association_hessian: bool = False,
    require_fresh_native: bool = False,
    write_summary: bool = False,
) -> dict[str, Any]:
    result = evaluate_payload(
        _build_payload(Path(manifest_path)),
        require_foundation=require_foundation,
        require_complete=require_complete,
        require_exact_association_hessian=require_exact_association_hessian,
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
    parser.add_argument("--require-exact-association-hessian", action="store_true")
    parser.add_argument("--require-fresh-native", action="store_true")
    parser.add_argument("--write-summary", action="store_true")
    args = parser.parse_args(argv)

    result = evaluate_campaign(
        manifest_path=args.manifest,
        require_foundation=args.require_foundation,
        require_complete=args.require_complete,
        require_exact_association_hessian=args.require_exact_association_hessian,
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
