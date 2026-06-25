from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

DEFAULT_REPO = "ePC-SAFT/ePC-SAFT"
READY_LABEL = "status:ready"
BLOCKED_LABEL = "status:blocked"


def _label_names(issue: dict[str, Any]) -> list[str]:
    labels = issue.get("labels", [])
    if not isinstance(labels, list):
        raise ValueError("issue labels must be a list.")
    names: list[str] = []
    for label in labels:
        if isinstance(label, str):
            names.append(label)
        elif isinstance(label, dict) and isinstance(label.get("name"), str):
            names.append(str(label["name"]))
        else:
            raise ValueError("issue label entries must be strings or objects with name.")
    return names


def _issue_number(issue: dict[str, Any]) -> int:
    number = issue.get("number")
    if not isinstance(number, int):
        raise ValueError("issue payload missing integer number.")
    return number


def _issue_state(issue: dict[str, Any]) -> str:
    state = issue.get("state")
    if not isinstance(state, str):
        raise ValueError("issue payload missing string state.")
    return state.lower()


def _payload_items(payload: Any, *, key: str | None = None) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        items = payload
    elif isinstance(payload, dict) and key and isinstance(payload.get(key), list):
        items = payload[key]
    elif isinstance(payload, dict) and isinstance(payload.get("items"), list):
        items = payload["items"]
    elif payload in (None, ""):
        items = []
    else:
        raise ValueError("GitHub dependency payload must be a list or object containing a list.")
    if not all(isinstance(item, dict) for item in items):
        raise ValueError("GitHub dependency payload entries must be objects.")
    return list(items)


def classify_dependency_readiness(
    *,
    resolved_issue: int,
    dependents_payload: Any,
    blocked_by_payloads: dict[int, Any],
    agent_ready_eligible: dict[int, bool] | None = None,
) -> list[dict[str, Any]]:
    dependents = _payload_items(dependents_payload, key="blocking")
    agent_ready_eligible = agent_ready_eligible or {}
    results: list[dict[str, Any]] = []
    for dependent in dependents:
        dependent_number = _issue_number(dependent)
        labels = _label_names(dependent)
        blockers = _payload_items(blocked_by_payloads.get(dependent_number, []), key="blocked_by")
        remaining_open = sorted(_issue_number(blocker) for blocker in blockers if _issue_state(blocker) != "closed")
        proposed_add: list[str] = []
        proposed_remove: list[str] = []
        if remaining_open:
            classification = "still_blocked"
        elif BLOCKED_LABEL in labels:
            classification = "ready_to_unblock"
            proposed_remove.append(BLOCKED_LABEL)
            if READY_LABEL not in labels:
                proposed_add.append(READY_LABEL)
            if agent_ready_eligible.get(dependent_number, False) and "agent-ready" not in labels:
                proposed_add.append("agent-ready")
        else:
            classification = "no_op"
        results.append(
            {
                "resolved_issue": resolved_issue,
                "dependent_issue": dependent_number,
                "classification": classification,
                "current_labels": labels,
                "remaining_open_blockers": remaining_open,
                "all_blockers": sorted(_issue_number(blocker) for blocker in blockers),
                "proposed_label_changes": {"add": proposed_add, "remove": proposed_remove},
            }
        )
    return results


def _frontmatter_value(text: str, key: str) -> str | None:
    match = re.search(rf"(?m)^{re.escape(key)}:\s*['\"]?([^'\"\n]+)['\"]?\s*$", text)
    return match.group(1).strip() if match else None


def _find_issue_mirror(repo_root: Path, issue_number: int) -> Path | None:
    issue_dir = repo_root / "docs" / "superpowers" / "issues"
    if not issue_dir.exists():
        return None
    for path in sorted(issue_dir.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        if _frontmatter_value(text, "issue") == str(issue_number):
            return path
    return None


def mirror_is_afk_ready(repo_root: Path, issue_number: int) -> bool:
    mirror = _find_issue_mirror(repo_root, issue_number)
    if mirror is None:
        return False
    text = mirror.read_text(encoding="utf-8")
    source_plan = _frontmatter_value(text, "source_plan")
    return (
        _frontmatter_value(text, "afk_hitl") == "AFK"
        and bool(source_plan)
        and (repo_root / str(source_plan)).exists()
        and "## Acceptance Criteria" in text
        and "## Proof Oracle" in text
    )


def _replace_status_label_text(text: str, readiness: str) -> str:
    target_label = READY_LABEL if readiness == "ready" else BLOCKED_LABEL
    opposite_label = BLOCKED_LABEL if readiness == "ready" else READY_LABEL
    text = text.replace(opposite_label, target_label)
    if target_label not in text and "- Labels:" in text:
        text = re.sub(r"(?m)^(- Labels: `)([^`]*)(`)$", rf"\1\2, {target_label}\3", text)
    return text


def sync_local_issue_readiness(repo_root: Path, issue_number: int, *, readiness: str, today: str) -> dict[str, Any]:
    mirror = _find_issue_mirror(repo_root, issue_number)
    warnings: list[str] = []
    changed = False
    mirror_rel: str | None = None
    if mirror is None:
        warnings.append("missing_local_mirror")
    else:
        mirror_rel = mirror.relative_to(repo_root).as_posix()
        original = mirror.read_text(encoding="utf-8")
        updated = original
        updated = re.sub(r'(?m)^readiness:\s*["\']?[^"\'\n]+["\']?\s*$', f'readiness: "{readiness}"', updated)
        updated = re.sub(r'(?m)^last_synced:\s*["\']?[^"\'\n]+["\']?\s*$', f'last_synced: "{today}"', updated)
        updated = re.sub(r"(?m)^- Readiness: `[^`]+`$", f"- Readiness: `{readiness}`", updated)
        updated = _replace_status_label_text(updated, readiness)
        if updated != original:
            mirror.write_text(updated, encoding="utf-8")
            changed = True

    milestone_paths: list[str] = []
    milestone_root = repo_root / "docs" / "superpowers" / "milestones"
    if milestone_root.exists():
        issue_pattern = re.compile(
            rf"(?m)^(\| \[#\s*{issue_number}\]|\| \[#{issue_number}\])(?P<tail>.+?)\| `[^`]+` \|(?P<rest>.+)$"
        )
        for readme in sorted(milestone_root.glob("*/README.md")):
            original = readme.read_text(encoding="utf-8")

            def replace_row(match: re.Match[str]) -> str:
                return f"{match.group(1)}{match.group('tail')}| `{readiness}` |{match.group('rest')}"

            updated = issue_pattern.sub(replace_row, original)
            if updated != original:
                readme.write_text(updated, encoding="utf-8")
                changed = True
                milestone_paths.append(readme.relative_to(repo_root).as_posix())
    if mirror is not None and not milestone_paths:
        warnings.append("missing_milestone_row")
    return {
        "issue": issue_number,
        "readiness": readiness,
        "changed": changed,
        "mirror_path": mirror_rel,
        "milestone_paths": milestone_paths,
        "warnings": warnings,
    }


def closed_issues_from_event(path: Path, *, event_name: str) -> list[int]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if event_name == "issues" and payload.get("action") == "closed":
        issue = payload.get("issue", {})
        number = issue.get("number") if isinstance(issue, dict) else None
        return [number] if isinstance(number, int) else []
    return []


def local_commit_decision(*, local_updates: list[dict[str, Any]], apply: bool) -> dict[str, Any]:
    commit_required = apply and any(bool(update.get("changed")) for update in local_updates)
    return {
        "commit_required": commit_required,
        "reason": "local_mirror_changes" if commit_required else "no_local_mirror_changes",
        "commit_message": "Sync issue readiness mirrors",
    }


class GitHubClient:
    def __init__(self, repo: str) -> None:
        self.repo = repo

    def _run_json(self, command: list[str]) -> Any:
        completed = subprocess.run(command, check=True, capture_output=True, text=True)
        return json.loads(completed.stdout or "null")

    def api(self, endpoint: str) -> Any:
        return self._run_json(["gh", "api", endpoint])

    def blocked_by(self, issue_number: int) -> Any:
        return self.api(f"/repos/{self.repo}/issues/{issue_number}/dependencies/blocked_by")

    def blocking(self, issue_number: int) -> Any:
        return self.api(f"/repos/{self.repo}/issues/{issue_number}/dependencies/blocking")

    def blocked_issues(self) -> list[dict[str, Any]]:
        return self._run_json(
            [
                "gh",
                "issue",
                "list",
                "--repo",
                self.repo,
                "--state",
                "open",
                "--label",
                BLOCKED_LABEL,
                "--json",
                "number,state,labels,title",
                "--limit",
                "200",
            ]
        )

    def apply_labels(self, issue_number: int, *, add: list[str], remove: list[str]) -> None:
        command = ["gh", "issue", "edit", str(issue_number), "--repo", self.repo]
        for label in add:
            command.extend(["--add-label", label])
        for label in remove:
            command.extend(["--remove-label", label])
        subprocess.run(command, check=True)


def _plan_for_issue(
    client: GitHubClient,
    repo_root: Path,
    issue_number: int,
) -> tuple[list[dict[str, Any]], dict[int, bool]]:
    dependents = client.blocking(issue_number)
    dependents_list = _payload_items(dependents, key="blocking")
    blocked_by_payloads = {_issue_number(dependent): client.blocked_by(_issue_number(dependent)) for dependent in dependents_list}
    eligible = {_issue_number(dependent): mirror_is_afk_ready(repo_root, _issue_number(dependent)) for dependent in dependents_list}
    return (
        classify_dependency_readiness(
            resolved_issue=issue_number,
            dependents_payload=dependents,
            blocked_by_payloads=blocked_by_payloads,
            agent_ready_eligible=eligible,
        ),
        eligible,
    )


def _plan_reconcile(client: GitHubClient, repo_root: Path) -> tuple[list[dict[str, Any]], dict[int, bool]]:
    results: list[dict[str, Any]] = []
    eligible: dict[int, bool] = {}
    for issue in client.blocked_issues():
        number = _issue_number(issue)
        blocked_by = client.blocked_by(number)
        synthetic_blocking_payload = [issue]
        eligible[number] = mirror_is_afk_ready(repo_root, number)
        results.extend(
            classify_dependency_readiness(
                resolved_issue=0,
                dependents_payload=synthetic_blocking_payload,
                blocked_by_payloads={number: blocked_by},
                agent_ready_eligible=eligible,
            )
        )
    return results, eligible


def _apply_ready_result(
    client: GitHubClient,
    repo_root: Path,
    result: dict[str, Any],
    *,
    today: str,
    strict_local: bool,
) -> dict[str, Any]:
    issue_number = int(result["dependent_issue"])
    changes = result["proposed_label_changes"]
    client.apply_labels(issue_number, add=list(changes["add"]), remove=list(changes["remove"]))
    local_update = sync_local_issue_readiness(repo_root, issue_number, readiness="ready", today=today)
    if strict_local and local_update["warnings"]:
        raise RuntimeError(f"local mirror sync incomplete for #{issue_number}: {', '.join(local_update['warnings'])}")
    return local_update


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=DEFAULT_REPO)
    parser.add_argument("--issue", type=int, action="append", default=[])
    parser.add_argument("--reconcile", action="store_true")
    parser.add_argument("--event-path", type=Path)
    parser.add_argument("--event-name")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--strict-local", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_arg_parser().parse_args(argv)
    repo_root = Path.cwd()
    issue_numbers = list(args.issue)
    event_mode = bool(args.event_path or args.event_name)
    if event_mode and not (args.event_path and args.event_name):
        raise SystemExit("--event-path and --event-name must be supplied together.")
    if args.event_path and args.event_name:
        issue_numbers.extend(closed_issues_from_event(args.event_path, event_name=args.event_name))
    if not issue_numbers and not args.reconcile:
        if event_mode:
            payload = {
                "repo": args.repo,
                "mode": "apply" if args.apply else "dry_run",
                "dry_run": not args.apply,
                "dependent_results": [],
                "agent_ready_eligible": {},
                "local_updates": [],
                "commit_decision": local_commit_decision(local_updates=[], apply=args.apply),
                "summary": {
                    "ready_to_unblock": 0,
                    "still_blocked": 0,
                    "no_op": 1,
                },
                "no_op_reason": "event_has_no_closed_issue_references",
            }
            if args.json:
                print(json.dumps(payload, indent=2, sort_keys=True))
            else:
                print("Dependency readiness sync: event has no closed issue references.")
            return 0
        raise SystemExit("--issue, --event-path/--event-name, or --reconcile is required.")
    client = GitHubClient(args.repo)
    today = dt.date.today().isoformat()
    results: list[dict[str, Any]] = []
    agent_ready_eligible: dict[int, bool] = {}
    for issue_number in sorted(set(issue_numbers)):
        issue_results, issue_eligible = _plan_for_issue(client, repo_root, issue_number)
        results.extend(issue_results)
        agent_ready_eligible.update(issue_eligible)
    if args.reconcile:
        reconcile_results, reconcile_eligible = _plan_reconcile(client, repo_root)
        results.extend(reconcile_results)
        agent_ready_eligible.update(reconcile_eligible)

    local_updates: list[dict[str, Any]] = []
    if args.apply:
        for result in results:
            if result["classification"] == "ready_to_unblock":
                local_updates.append(
                    _apply_ready_result(client, repo_root, result, today=today, strict_local=args.strict_local)
                )
    commit_decision = local_commit_decision(local_updates=local_updates, apply=args.apply)
    payload = {
        "repo": args.repo,
        "mode": "apply" if args.apply else "dry_run",
        "dry_run": not args.apply,
        "dependent_results": results,
        "agent_ready_eligible": agent_ready_eligible,
        "local_updates": local_updates,
        "commit_decision": commit_decision,
        "summary": {
            "ready_to_unblock": sum(1 for result in results if result["classification"] == "ready_to_unblock"),
            "still_blocked": sum(1 for result in results if result["classification"] == "still_blocked"),
            "no_op": sum(1 for result in results if result["classification"] == "no_op"),
        },
    }
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(
            f"ready_to_unblock={payload['summary']['ready_to_unblock']} "
            f"still_blocked={payload['summary']['still_blocked']} no_op={payload['summary']['no_op']}"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
