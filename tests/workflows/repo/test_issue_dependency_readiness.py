from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.dev import update_issue_dependency_readiness as readiness


def _issue(number: int, *, state: str = "open", labels: list[str] | None = None) -> dict[str, object]:
    return {
        "number": number,
        "title": f"Issue {number}",
        "state": state,
        "labels": [{"name": label} for label in (labels or [])],
    }


def test_classifies_no_dependents_as_noop() -> None:
    result = readiness.classify_dependency_readiness(
        resolved_issue=188,
        dependents_payload=[],
        blocked_by_payloads={},
    )

    assert result == []


def test_classifies_dependent_with_remaining_open_blocker() -> None:
    result = readiness.classify_dependency_readiness(
        resolved_issue=188,
        dependents_payload=[_issue(189, labels=["status:blocked"])],
        blocked_by_payloads={189: [_issue(188, state="closed"), _issue(241, state="open")]},
    )

    assert result[0]["classification"] == "still_blocked"
    assert result[0]["remaining_open_blockers"] == [241]
    assert result[0]["proposed_label_changes"] == {"add": [], "remove": []}


def test_classifies_dependent_with_all_blockers_closed_as_ready_without_agent_ready() -> None:
    result = readiness.classify_dependency_readiness(
        resolved_issue=241,
        dependents_payload=[_issue(189, labels=["status:blocked"])],
        blocked_by_payloads={189: [_issue(188, state="closed"), _issue(241, state="closed")]},
    )

    assert result[0]["classification"] == "ready_to_unblock"
    assert result[0]["remaining_open_blockers"] == []
    assert result[0]["proposed_label_changes"] == {"add": ["status:ready"], "remove": ["status:blocked"]}


def test_malformed_dependency_payload_fails_loudly() -> None:
    with pytest.raises(ValueError, match="number"):
        readiness.classify_dependency_readiness(
            resolved_issue=188,
            dependents_payload=[{"state": "open"}],
            blocked_by_payloads={},
        )


def test_local_mirror_and_milestone_rows_update_when_ready(tmp_path: Path) -> None:
    issue_dir = tmp_path / "docs" / "superpowers" / "issues"
    issue_dir.mkdir(parents=True)
    mirror = issue_dir / "issue-0189.md"
    mirror.write_text(
        "\n".join(
            [
                "---",
                "issue: 189",
                'readiness: "blocked"',
                'last_synced: "2026-06-01"',
                "---",
                "",
                "## Tracker Metadata",
                "",
                "- Readiness: `blocked`",
                "- Labels: `enhancement, status:blocked, type:feature`",
                "",
            ]
        ),
        encoding="utf-8",
    )
    milestone = tmp_path / "docs" / "superpowers" / "milestones" / "M4-equilibrium" / "README.md"
    milestone.parent.mkdir(parents=True)
    milestone.write_text(
        "| Issue | Capability | Backend | Readiness | Summary |\n"
        "| --- | --- | --- | --- | --- |\n"
        "| [#189](../../issues/issue-0189.md) | `lle` | `Ipopt` | `blocked` | Umbrella. |\n",
        encoding="utf-8",
    )

    updates = readiness.sync_local_issue_readiness(tmp_path, 189, readiness="ready", today="2026-06-13")

    assert updates["mirror_path"].endswith("issue-0189.md")
    assert updates["milestone_paths"] == ["docs/superpowers/milestones/M4-equilibrium/README.md"]
    assert 'readiness: "ready"' in mirror.read_text(encoding="utf-8")
    assert 'last_synced: "2026-06-13"' in mirror.read_text(encoding="utf-8")
    assert "status:ready" in mirror.read_text(encoding="utf-8")
    assert "| `ready` |" in milestone.read_text(encoding="utf-8")


def test_missing_local_mirror_is_reported(tmp_path: Path) -> None:
    updates = readiness.sync_local_issue_readiness(tmp_path, 189, readiness="ready", today="2026-06-13")

    assert updates["mirror_path"] is None
    assert updates["warnings"] == ["missing_local_mirror"]


def test_workflow_event_parser_reads_issue_and_pr_close_events(tmp_path: Path) -> None:
    issue_event = tmp_path / "issue.json"
    issue_event.write_text(json.dumps({"issue": {"number": 188}, "action": "closed"}), encoding="utf-8")
    pr_event = tmp_path / "pr.json"
    pr_event.write_text(
        json.dumps(
            {
                "pull_request": {
                    "merged": True,
                    "body": "Closes #188. Closes ePC-SAFT/ePC-SAFT#241.",
                },
                "action": "closed",
            }
        ),
        encoding="utf-8",
    )

    assert readiness.closed_issues_from_event(issue_event, event_name="issues") == [188]
    assert readiness.closed_issues_from_event(pr_event, event_name="pull_request") == [188, 241]


def test_main_treats_merged_pr_without_close_keyword_as_noop(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    pr_event = tmp_path / "pr.json"
    pr_event.write_text(
        json.dumps(
            {
                "pull_request": {
                    "merged": True,
                    "title": "Tighten HELD2 adoption diagnostics plan",
                    "body": "Refs #306.",
                },
                "action": "closed",
            }
        ),
        encoding="utf-8",
    )

    rc = readiness.main(
        [
            "--event-path",
            str(pr_event),
            "--event-name",
            "pull_request",
            "--dry-run",
            "--json",
        ]
    )

    payload = json.loads(capsys.readouterr().out)
    assert rc == 0
    assert payload["no_op_reason"] == "event_has_no_closed_issue_references"
    assert payload["summary"] == {"ready_to_unblock": 0, "still_blocked": 0, "no_op": 1}


def test_workflow_listens_only_to_closeout_events() -> None:
    workflow = (Path(__file__).resolve().parents[3] / ".github" / "workflows" / "sync-issue-readiness.yml").read_text(
        encoding="utf-8"
    )

    assert "issues:\n    types: [closed]" in workflow
    assert "pull_request:\n    types: [closed]" in workflow
    assert "workflow_dispatch:" in workflow
    assert "schedule:" in workflow
    assert "reopened" not in workflow
    assert "unlabeled" not in workflow


def test_apply_plan_records_git_commit_decision() -> None:
    plan = readiness.local_commit_decision(
        local_updates=[
            {"changed": True, "mirror_path": "docs/superpowers/issues/issue-0189.md"},
            {"changed": False, "mirror_path": None},
        ],
        apply=True,
    )

    assert plan == {
        "commit_required": True,
        "reason": "local_mirror_changes",
        "commit_message": "Sync issue readiness mirrors",
    }
