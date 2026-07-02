# M4 CE: add retained artifact review digest

**Mirror Retention:** retain
**GitHub Issue:** https://github.com/ePC-SAFT/ePC-SAFT/issues/400
**GitHub Milestone:** M4 - Equilibrium
**Issue Type:** task
**Source Spec:** docs/superpowers/specs/2026-06-30-m4-ce-robustness-followup-audit-findings.md
**Source Plan:** docs/superpowers/plans/2026-06-30-m4-ce-robustness-followup-hardening-plan.md
**Classification:** AFK
**Labels:** agent-ready,status:ready,type:task,area:equilibrium,equilibrium,solver,native,backend:ipopt,validation
**Goal Command:** /goal Make retained CE artifact diffs reviewable through semantic digest evidence.
**Branch:** codex/m4-ce-generic-pope-homotopy-continuation
**Execution Mode:** Looping Mode
**Worktree Policy:** Current CE worktree
**Integration Policy:** Current thread owns PR
**TDD Policy:** Required
**Parallelization Plan:** None
**Reviewer Role:** Main thread orchestrator
**Script Gate Mode:** Safety and proof

## Outcome Summary

**Outcome Source:** docs/superpowers/plans/2026-06-30-m4-ce-robustness-followup-hardening-plan.md#outcome-proof
**Intent:** Retained CE artifact changes should be reviewable from semantic digest evidence before raw CSV diffs.
**Target Output:** Checker JSON reports row counts, column sets, numeric extrema, and stable hashes for retained CE CSV/JSON artifacts.
**Owner:** M4 equilibrium package owner for packages/epcsaft-equilibrium.
**Interface:** `scripts/validation/check_standalone_ce_gate.py`, retained summary JSON if needed, and checker contract tests.
**Cutover:** Semantic digest evidence becomes the first retained artifact review surface.
**Replaced Path:** Raw-diff-first artifact review is displaced by digest-first evidence.
**Acceptance Proof:** Checker contract tests and direct standalone checker execution require retained artifact digest evidence.
**Stop Criteria:** Stop if digest generation requires duplicate plot artifacts.
**Avoid:** Do not regenerate or show MEA plots for this issue.

## Project Merge

**Merge Owner:** Main thread orchestrator
**Merge Gate:** Native UI approval required
**Merge Policy:** Repo default
**Worktree Cleanup Policy:** Keep current CE worktree until all loop issues finish
**Orchestrator Wakeup Policy:** Inline run

## What To Build

Implement Task 5 from the source plan: add retained artifact review digest evidence and checker enforcement.

## Acceptance Criteria

- [ ] Standalone checker emits retained artifact digest evidence.
- [ ] Checker contract tests reject missing digest fields under require-complete.
- [ ] No duplicate plot artifacts are generated for this tranche.

## Resolution Evidence

- `scripts/validation/check_standalone_ce_gate.py` now emits `artifact_review_digest` with SHA-256 hashes, row counts, column sets, and numeric extrema for retained CE JSON/CSV artifacts.
- No plot artifacts were regenerated or added for this tranche.
- Fresh proof: `tests/native/contracts/test_standalone_ce_gate.py` passed inside the 44-test combined focused run.
- Fresh proof: `uv run --no-sync python scripts/validation/check_standalone_ce_gate.py --json --require-single-nlp-path --require-oracles --require-complete` returned `status=complete`, `blocker_count=0`, `artifact_digest_status=complete`, `artifact_digest_count=5`.

## Blocked by

- None

## Non-goals

- Duplicate MEA plot output.
- CPE, reactive LLE, or phase-equilibrium admission.
- Downstream application metrics.

## Proof Oracle

- pwsh.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\validate-plan-task-use-cases.ps1 -PlanPath docs/superpowers/plans/2026-06-30-m4-ce-robustness-followup-hardening-plan.md
- pwsh.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\validate-plan-outcome-proof.ps1 -PlanPath docs/superpowers/plans/2026-06-30-m4-ce-robustness-followup-hardening-plan.md
- pwsh.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\validate-issue-mirror.ps1 -IssueFile docs/superpowers/issues/2026-06-30-m4-ce-issue-0400-retained-artifact-review-digest.md
- uv run --no-sync python run_pytest.py tests/native/contracts/test_standalone_ce_gate.py -q
- uv run --no-sync python scripts/validation/check_standalone_ce_gate.py --json --require-single-nlp-path --require-oracles --require-complete
