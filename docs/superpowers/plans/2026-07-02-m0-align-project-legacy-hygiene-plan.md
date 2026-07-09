# M0 Align-Project Legacy Hygiene Plan

## Outcome Proof

**Intent:** Turn the remaining align-project findings after the Khudaida M6
hierarchy repair into one AFK governance issue.
**Current Behavior:** `align-project -Mode GitHubAware` reports no blocking
findings and no Khudaida repairables, but still reports 52 legacy
closed-mirror lifecycle findings and 9 milestone-page findings.
**Expected Outcome:** The project has a focused repair issue that can normalize
closed mirror retention evidence and reconcile milestone page discovery with
the repo's `docs/superpowers/milestones/M*/README.md` layout.
**Target Output:** One M0 issue and mirror with exact acceptance criteria,
proof commands, and stop criteria for the remaining align-project hygiene.
**Owner:** M0 governance owns project workflow metadata, tracker hygiene,
issue mirrors, and align-project audit compatibility.
**Interface:** `docs/superpowers/issues`, `docs/superpowers/milestones`,
`docs/agents/triage-labels.md`, the GitHub issue tracker, and the
`align-project` audit output.
**Cutover:** Keep the merged Khudaida M6 hierarchy as-is; route only the
remaining legacy cleanup through the new M0 issue.
**Replaced Path:** Opportunistic broad edits during unrelated issue work.
**Evidence:** Final audit summary from PR #422 closeout: `ok=True`,
`blocking=0`, `closed-mirror-lifecycle: 52`, `milestone-membership: 9`,
Khudaida repairables `0`.
**Acceptance Proof:** The future issue closes only when the GitHub-aware align
audit has no blocking findings and no repairables for closed mirror lifecycle
or milestone page discovery, with a clean worktree and docs validation.
**Risk:** A broad cleanup could hide policy decisions inside mechanical edits;
the issue must require classification evidence and stop on ambiguous retention
or script-ownership questions.
**Stop Criteria:** Stop and revise if retention vocabulary is ambiguous, if
closed mirrors should be deleted instead of retained, or if the milestone page
finding requires a plugin/script contract change outside repo-owned docs.
**Avoid:** Do not alter product code, solver behavior, validation artifacts,
issue close state, or milestone assignment while repairing workflow metadata.
Do not mask a script-layout mismatch by duplicating canonical milestone truth.

## Implementation Boundaries

**Files To Create:** One M0 issue mirror under `docs/superpowers/issues` after
GitHub publication.
**Files To Modify:** Legacy closed issue mirrors that should be retained;
milestone index or documentation files only if they are the correct repo-owned
surface for milestone page discovery.
**Files To Avoid:** `packages/**`, validation datasets, figure artifacts,
native build files, and plugin cache files.
**Source Of Truth:** GitHub Issues, `docs/superpowers/PROJECT_CONTEXT.md`,
`docs/superpowers/milestones/M*/README.md`, and the align-project audit.
**Read Path:** Run `align-project -Mode GitHubAware`, inspect repairables by
dimension, inspect representative closed mirrors, and inspect milestone layout.
**Write Path:** Apply the smallest docs/tracker-mirror repair that makes the
audit evidence match actual repo policy.
**Integration Points:** `scripts/validate_issue_mirror.py`,
`scripts/dev/validate_project.py docs`, `git diff --check`, and the cleanup
hook.
**Migration Or Cutover:** Keep existing valid milestone README pages; prefer a
single compatibility/index correction over duplicate milestone sources.
**Replaced Path Handling:** Replace parser-invisible closed mirror retention
and milestone page assumptions with machine-checkable evidence.
**Acceptance Proof Gate:** Report exact before/after audit counts, changed
files, and retained closed mirror policy in the closing PR.

## Tasks

### Task 1: Normalize Closed Mirror Lifecycle Evidence

**Use Cases:**

- Closed issue mirrors that remain useful historical records should be
  machine-readable as retained.
- Closed mirrors that are stale noise should be removed only when references
  and ownership allow it.

**Files:** `docs/superpowers/issues/*.md`

1. Run the GitHub-aware align audit and export the closed-mirror findings.
2. Classify each closed mirror as retain or remove.
3. Add parser-compatible retention evidence to retained mirrors.
4. Remove only mirrors proven obsolete and unreferenced.
5. Validate the repair with a second align audit.

### Task 2: Reconcile Milestone Page Discovery

**Use Cases:**

- GitHub milestones M0-M8 should map to the existing local milestone pages.
- The repair should avoid inventing duplicate canonical milestone documents.

**Files:** `docs/superpowers/milestones/**`

1. Inspect how align-project discovers milestone pages.
2. Verify the repo's current `M*/README.md` milestone layout.
3. Choose the smallest repo-owned compatibility repair, or stop with a precise
   script-contract blocker if repo docs cannot own the fix.
4. Validate that M0-M8 no longer report missing local milestone pages.

### Task 3: Prove Project Alignment Health For This Repair Surface

**Use Cases:**

- The governance repair must close with executable evidence.
- Manual claims that the tracker is cleaner should not close the issue.

**Files:** `docs/superpowers/issues/*.md`, `docs/superpowers/milestones/**`,
`docs/agents/triage-labels.md`

1. Rerun `align-project -Mode GitHubAware`.
2. Rerun changed issue mirror validation where mirrors were edited.
3. Run `uv run --no-sync python scripts\dev\validate_project.py docs`.
4. Run `git diff --check` and the repo cleanup hook.
5. Report residual findings explicitly; do not close if the two target
   repairable dimensions remain.
