---
issue: 401
title: "M4 CE: add CE robustness follow-up gate"
url: https://github.com/ePC-SAFT/ePC-SAFT/issues/401
state: closed
milestone: "M4 - Equilibrium"
project: "ePC-SAFT Roadmap"
package: equilibrium
capability: null
backend: Ipopt
readiness: closed
release_target: equilibrium-0.x
source_spec: null
source_plan: null
afk_hitl: AFK
branch: null
last_synced: "2026-06-30"
---

# M4 CE: add CE robustness follow-up gate

**Mirror Retention:** Keep
**GitHub Issue:** https://github.com/ePC-SAFT/ePC-SAFT/issues/401
**GitHub Milestone:** M4 - Equilibrium
**Issue Type:** task
**Source Spec:** docs/superpowers/specs/2026-06-30-m4-ce-robustness-followup-audit-findings.md
**Source Plan:** docs/superpowers/plans/2026-06-30-m4-ce-robustness-followup-hardening-plan.md
**AFK/HITL:** AFK
**Classification:** AFK
**Labels:** agent-ready,status:ready,type:task,area:equilibrium,equilibrium,solver,native,backend:ipopt,validation
**Goal Command:** /goal Add one bounded JSON checker command for this seven-finding follow-up tranche.
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
**Intent:** Future agents should have one bounded command that proves this follow-up tranche is healthy.
**Target Output:** `scripts/validation/check_ce_robustness_followup.py` emits JSON status for all seven findings and supports `--require-complete`.
**Owner:** M4 equilibrium package owner for packages/epcsaft-equilibrium.
**Interface:** New follow-up checker, checker contract tests, and issue proof oracles.
**Cutover:** One durable checker command replaces hand-assembled follow-up command lists.
**Replaced Path:** Manual reconstruction of tranche health from scattered commands is displaced by a bounded JSON gate.
**Acceptance Proof:** Checker contract tests and direct `--json --require-complete` execution pass after all required evidence exists.
**Stop Criteria:** Stop if the checker would need to run an unbounded full native suite internally.
**Avoid:** Do not hide missing evidence behind optional flags.

## Project Merge

**Merge Owner:** Main thread orchestrator
**Merge Gate:** Native UI approval required
**Merge Policy:** Repo default
**Worktree Cleanup Policy:** Keep current CE worktree until all loop issues finish
**Orchestrator Wakeup Policy:** Inline run

## What To Build

Implement Task 6 from the source plan: add a bounded CE robustness follow-up checker and contract tests.

## Acceptance Criteria

- [ ] Checker emits JSON with all seven finding keys.
- [ ] `--require-complete` fails when required evidence is absent and passes when evidence is complete.
- [ ] The checker does not launch an unbounded full native test suite internally.

## Resolution Evidence

- Added bounded JSON checker `scripts/validation/check_ce_robustness_followup.py`.
- Added checker contract tests in `tests/native/contracts/test_ce_robustness_followup_gate.py`.
- The checker reports all seven finding keys and consumes static/dynamic evidence rather than launching the full native suite internally.
- Fresh proof: `tests/native/contracts/test_ce_robustness_followup_gate.py` passed inside the 44-test combined focused run.
- Fresh proof: `uv run --no-sync python scripts/validation/check_ce_robustness_followup.py --json --require-complete` returned `status=complete`, `blocker_count=0`, `finding_count=7`.

## Blocked by

- None

## Non-goals

- Duplicate MEA plot output.
- CPE, reactive LLE, or phase-equilibrium admission.
- Downstream application metrics.

## Proof Oracle

- uv run --no-sync python scripts/validate_plan_task_use_cases.py --plan-path docs/superpowers/plans/2026-06-30-m4-ce-robustness-followup-hardening-plan.md
- uv run --no-sync python scripts/validate_plan_outcome_proof.py --plan-path docs/superpowers/plans/2026-06-30-m4-ce-robustness-followup-hardening-plan.md
- uv run --no-sync python scripts/validate_issue_mirror.py --issue-file docs/superpowers/issues/2026-06-30-m4-equilibrium-issue-0401-ce-robustness-followup-gate.md
- uv run --no-sync python run_pytest.py tests/native/contracts/test_ce_robustness_followup_gate.py -q
- uv run --no-sync python scripts/validation/check_ce_robustness_followup.py --json --require-complete
