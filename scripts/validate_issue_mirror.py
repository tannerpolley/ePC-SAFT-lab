#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate a local GitHub issue mirror.")
    parser.add_argument("--issue-file", required=True)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--milestone-required", action="store_true")
    return parser


def _metadata_value(text: str, name: str) -> str | None:
    match = re.search(rf"(?m)^\*\*{re.escape(name)}:\*\*\s*(.+?)\s*$", text)
    return match.group(1).strip() if match else None


def _section_body(text: str, name: str) -> str | None:
    match = re.search(
        rf"(?ms)^##\s+{re.escape(name)}\s*\r?\n(?P<body>.*?)(?=^##\s+|\Z)",
        text,
    )
    return match.group("body") if match else None


def _resolve_inside_repo(repo_root: Path, raw_path: str) -> Path:
    root = repo_root.resolve()
    candidate = Path(raw_path).expanduser()
    if not candidate.is_absolute():
        candidate = root / candidate
    resolved = candidate.resolve()
    if resolved != root and root not in resolved.parents:
        raise ValueError(f"Issue mirror must be inside repo root: {raw_path}")
    return resolved


def validate(issue_file: Path, repo_root: Path, *, milestone_required: bool) -> dict[str, object]:
    root = repo_root.resolve()
    relative_path = issue_file.relative_to(root).as_posix()
    text = issue_file.read_text(encoding="utf-8")
    errors: list[str] = []

    def add_error(message: str) -> None:
        errors.append(message)

    if not re.fullmatch(r"docs/superpowers/issues/.+[.]md", relative_path):
        add_error("mirror must live under docs/superpowers/issues")

    issue_number: int | None = None
    file_issue_number: int | None = None
    filename_match = re.search(r"issue-(\d{4})-", issue_file.name)
    if filename_match:
        file_issue_number = int(filename_match.group(1))
    else:
        add_error("filename must include issue-####")

    title_match = re.search(r"(?m)^#\s+(.+?)\s*$", text)
    title = title_match.group(1).strip() if title_match else None
    if title is None:
        add_error("mirror must start with an H1 title")

    required_metadata = (
        "GitHub Issue",
        "GitHub Milestone",
        "Issue Type",
        "Source Spec",
        "Source Plan",
        "Classification",
        "Labels",
        "Goal Command",
        "Execution Mode",
        "Worktree Policy",
        "Integration Policy",
        "TDD Policy",
    )
    metadata = {name: _metadata_value(text, name) for name in required_metadata}
    for name, value in metadata.items():
        if not value:
            add_error(f"missing metadata: {name}")

    issue_url = metadata["GitHub Issue"]
    if issue_url:
        issue_match = re.fullmatch(r"https://github[.]com/ePC-SAFT/ePC-SAFT/issues/(\d+)", issue_url)
        if issue_match:
            issue_number = int(issue_match.group(1))
            if file_issue_number is not None and issue_number != file_issue_number:
                add_error("filename issue number does not match GitHub issue URL")
        else:
            add_error("GitHub Issue metadata must use the canonical ePC-SAFT issue URL")

    if milestone_required and not metadata["GitHub Milestone"]:
        add_error("GitHub Milestone metadata is required")

    labels = metadata["Labels"] or ""
    for required_prefix in ("type:", "status:"):
        if labels and re.search(rf"(^|,)\s*{re.escape(required_prefix)}", labels) is None:
            add_error(f"Labels metadata must include {required_prefix}")

    for section in (
        "Outcome Summary",
        "Project Merge",
        "What To Build",
        "Acceptance Criteria",
        "Blocked by",
        "Non-goals",
        "Proof Oracle",
    ):
        if re.search(rf"(?m)^##\s+{re.escape(section)}\s*$", text) is None:
            add_error(f"missing section: {section}")

    if re.search(r"(?m)^-\s+\[\s\]\s+\S", text) is None:
        add_error("Acceptance Criteria must include unchecked checklist items")

    proof_oracle = _section_body(text, "Proof Oracle") or ""
    if re.search(r"validate_plan_task_use_cases[.]py", proof_oracle) is None:
        add_error("Proof Oracle must include validate_plan_task_use_cases.py")
    if re.search(r"validate_plan_outcome_proof[.]py", proof_oracle) is None:
        add_error("Proof Oracle must include validate_plan_outcome_proof.py")

    return {
        "ok": not errors,
        "issue_file": relative_path,
        "issue_number": issue_number,
        "title": title,
        "error_count": len(errors),
        "errors": errors,
    }


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    repo_root = Path(args.repo_root).expanduser().resolve()
    try:
        issue_file = _resolve_inside_repo(repo_root, args.issue_file)
        result = validate(issue_file, repo_root, milestone_required=args.milestone_required)
    except Exception as exc:
        result = {
            "ok": False,
            "issue_file": args.issue_file,
            "issue_number": None,
            "title": None,
            "error_count": 1,
            "errors": [str(exc)],
        }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
