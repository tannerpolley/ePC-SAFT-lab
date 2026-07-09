#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

OUTCOME_PROOF_FIELDS = (
    "Intent",
    "Current Behavior",
    "Expected Outcome",
    "Target Output",
    "Owner",
    "Interface",
    "Cutover",
    "Replaced Path",
    "Evidence",
    "Acceptance Proof",
    "Stop Criteria",
    "Avoid",
    "Risk",
)
IMPLEMENTATION_BOUNDARY_FIELDS = (
    "Files To Create",
    "Files To Modify",
    "Files To Avoid",
    "Source Of Truth",
    "Read Path",
    "Write Path",
    "Integration Points",
    "Migration Or Cutover",
    "Replaced Path Handling",
    "Acceptance Proof Gate",
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate outcome-proof structure in a plan.")
    parser.add_argument("--repo-root", default=Path(__file__).resolve().parents[1])
    parser.add_argument("--plan-path", required=True)
    return parser


def _repo_path(repo_root: Path, raw_path: str) -> Path:
    root = repo_root.expanduser().resolve()
    candidate = Path(raw_path).expanduser()
    if not candidate.is_absolute():
        candidate = root / candidate
    resolved = candidate.resolve()
    if resolved != root and root not in resolved.parents:
        raise ValueError(f"plan path is outside repo root: {resolved}")
    return resolved


def _markdown_section(text: str, name: str) -> str | None:
    match = re.search(rf"(?ims)^\s{{0,3}}##\s+{re.escape(name)}\s*$\r?\n(?P<body>.*?)(?=^\s{{0,3}}##\s+|\Z)", text)
    return match.group("body") if match else None


def _field_value(text: str, name: str) -> str | None:
    escaped = re.escape(name)
    patterns = (
        rf"(?im)^\s*\*\*{escaped}\s*:\s*\*\*\s*(.+?)\s*$",
        rf"(?im)^\s*\*\*{escaped}\*\*\s*:\s*(.+?)\s*$",
        rf"(?im)^\s*{escaped}\s*:\s*(.+?)\s*$",
    )
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(1).strip()
    return None


def _concrete_value(field: str, value: str | None) -> tuple[bool, str]:
    if value is None or not value.strip():
        return False, f"{field} is empty"
    trimmed = value.strip().lower()
    if re.fullmatch(r"(tbd|none|n/a|na|not applicable|same as above|-)", trimmed):
        return False, f"{field} uses a generic value"
    if field == "Acceptance Proof" and re.fullmatch(
        r"(tests?\s+pass(?:ed)?|unit tests?\s+pass(?:ed)?|lint\s+pass(?:ed)?|diff\s+reviewed)", trimmed
    ):
        return False, "Acceptance Proof must name target behavior, not only test status"
    return True, "passed"


def _check_fields(section_text: str, fields: tuple[str, ...], section_name: str) -> tuple[bool, str, dict[str, str]]:
    values: dict[str, str] = {}
    for field in fields:
        value = _field_value(section_text, field)
        ok, reason = _concrete_value(field, value)
        if not ok:
            return False, f"{section_name} {reason}", values
        values[field] = str(value)
    return True, "passed", values


def _task_use_cases(lines: list[str]) -> list[str]:
    tasks: list[tuple[int, int, str]] = []
    for index, line in enumerate(lines):
        match = re.match(r"^\s{0,3}#{2,4}\s+Task\s+(?P<number>\d+)\s*[:.-]\s*(?P<title>.+?)\s*$", line)
        if match:
            tasks.append((int(match.group("number")), index, match.group("title")))

    use_cases: list[str] = []
    for task_index, (_, start, _) in enumerate(tasks):
        end = tasks[task_index + 1][1] if task_index + 1 < len(tasks) else len(lines)
        block = lines[start:end]
        use_case_index = next((idx for idx, line in enumerate(block) if re.match(r"^\s*\*\*Use Cases:\*\*\s*$", line)), -1)
        if use_case_index < 0:
            continue
        for line in block[use_case_index + 1 :]:
            if re.match(r"^\s{0,3}#{1,6}\s+", line) or re.match(r"^\s*\*\*[^*]+:\*\*\s*$", line):
                break
            if re.match(r"^\s*[-*]\s+\S", line) or re.match(r"^\s*\d+\.\s+\S", line):
                use_cases.append(line.strip())
    return use_cases


def _task_use_case_outcome_coverage(text: str) -> tuple[bool, str, int]:
    use_cases = _task_use_cases(text.splitlines())
    if not use_cases:
        return False, "Task # Use Cases are required to cover outcome evidence and cutover", 0
    combined = "\n".join(use_cases).lower()
    has_evidence = re.search(r"acceptance|evidence|proof|validator|visible|diagnostic|checker", combined) is not None
    has_cutover = re.search(r"cutover|displaced|migration|old path|duplicate|retire|replace|replaced|shared tracer", combined) is not None
    if not has_evidence or not has_cutover:
        return False, "Task # Use Cases must cover acceptance evidence and cutover or replaced path handling", len(use_cases)
    return True, "passed", len(use_cases)


def validate(repo_root: Path, raw_plan_path: str) -> dict[str, object]:
    root = repo_root.expanduser().resolve()
    plan_path = _repo_path(root, raw_plan_path)
    if not plan_path.is_file():
        raise ValueError(f"plan does not exist: {raw_plan_path}")
    relative_plan = plan_path.relative_to(root).as_posix()
    if not relative_plan.lower().startswith("docs/superpowers/plans/"):
        raise ValueError(f"plan must be under docs/superpowers/plans: {relative_plan}")

    text = plan_path.read_text(encoding="utf-8")
    outcome_section = _markdown_section(text, "Outcome Proof")
    if outcome_section is None:
        raise ValueError("missing ## Outcome Proof")
    outcome_ok, outcome_reason, outcome_fields = _check_fields(outcome_section, OUTCOME_PROOF_FIELDS, "Outcome Proof")
    if not outcome_ok:
        raise ValueError(outcome_reason)

    boundary_section = _markdown_section(text, "Implementation Boundaries")
    if boundary_section is None:
        raise ValueError("missing ## Implementation Boundaries")
    boundary_ok, boundary_reason, boundary_fields = _check_fields(
        boundary_section,
        IMPLEMENTATION_BOUNDARY_FIELDS,
        "Implementation Boundaries",
    )
    if not boundary_ok:
        raise ValueError(boundary_reason)

    coverage_ok, coverage_reason, use_case_count = _task_use_case_outcome_coverage(text)
    if not coverage_ok:
        raise ValueError(coverage_reason)

    return {
        "ok": True,
        "phase": "plan-outcome-proof",
        "plan_path": relative_plan,
        "reason": "outcome proof passed",
        "use_case_count": use_case_count,
        "fields": {
            "outcome_proof": outcome_fields,
            "implementation_boundaries": boundary_fields,
        },
    }


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        result = validate(Path(args.repo_root), args.plan_path)
    except Exception as exc:
        result = {
            "ok": False,
            "phase": "plan-outcome-proof",
            "reason": str(exc),
        }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
