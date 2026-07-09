---
issue: 397
title: "M4 CE: preserve caller seed rejection evidence"
url: https://github.com/ePC-SAFT/ePC-SAFT/issues/397
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

# M4 CE: preserve caller seed rejection evidence

**Mirror Retention:** Keep
**GitHub Issue:** https://github.com/ePC-SAFT/ePC-SAFT/issues/397
**GitHub Milestone:** M4 - Equilibrium
**Issue Type:** task
**Source Spec:** docs/superpowers/specs/2026-06-30-m4-ce-robustness-followup-audit-findings.md
**Source Plan:** docs/superpowers/plans/2026-06-30-m4-ce-robustness-followup-hardening-plan.md
**AFK/HITL:** AFK
**Classification:** AFK
**Labels:** agent-ready,status:ready,type:task,area:equilibrium,equilibrium,solver,native,backend:ipopt,validation
**Goal Command:** /goal Record caller-seed rejection reason, exception message, and fallback source when CE escalates to owned initialization.
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
**Intent:** Bad caller seeds should remain debuggable after CE escalates to owned initialization.
**Target Output:** Diagnostics preserve caller-seed rejection source, reason, exception message, and fallback status without changing accepted fallback behavior.
**Owner:** M4 equilibrium package owner for packages/epcsaft-equilibrium.
**Interface:** Native CE result payloads, pybind exposure, and public diagnostics.
**Cutover:** Seed provenance becomes traceable from the public result diagnostics.
**Replaced Path:** Silent native catch-and-continue behavior no longer drops the original caller-seed failure evidence.
**Acceptance Proof:** Focused seed diagnostics tests prove rejection and exception evidence survive fallback.
**Stop Criteria:** Stop if native exception capture requires provider-package scope outside the approved M4 boundary.
**Avoid:** Do not accept caller-seeded states without independent final proof.

## Project Merge

**Merge Owner:** Main thread orchestrator
**Merge Gate:** Native UI approval required
**Merge Policy:** Repo default
**Worktree Cleanup Policy:** Keep current CE worktree until all loop issues finish
**Orchestrator Wakeup Policy:** Inline run

## What To Build

Implement Task 2 from the source plan: capture caller-seed rejection and exception evidence in native CE and expose it through diagnostics.

## Acceptance Criteria

- [ ] Bad caller-seed fallback keeps the original rejection source and message.
- [ ] Accepted fallback diagnostics show the caller seed did not pass final proof.
- [ ] Focused seed policy tests cover proof rejection and exception escalation.

## Resolution Evidence

- Native CE results now carry `caller_seed_rejection_source`, `caller_seed_rejection_reason`, `caller_seed_exception_observed`, and `caller_seed_exception_message`.
- Pybind diagnostics expose the caller-seed rejection evidence under `initialization`.
- The bad positive MEA caller-seed API test now proves fallback to CE-owned initialization while preserving the caller-seed exception evidence.
- Fresh proof: `uv run --no-sync python scripts/dev/build_epcsaft.py --build-only --parallel 10` completed and native import passed after the C++ changes.
- Fresh proof: the combined focused pytest command passed with 44 tests.

## Blocked by

- None

## Non-goals

- Duplicate MEA plot output.
- CPE, reactive LLE, or phase-equilibrium admission.
- Downstream application metrics.

## Proof Oracle

- uv run --no-sync python scripts/validate_plan_task_use_cases.py --plan-path docs/superpowers/plans/2026-06-30-m4-ce-robustness-followup-hardening-plan.md
- uv run --no-sync python scripts/validate_plan_outcome_proof.py --plan-path docs/superpowers/plans/2026-06-30-m4-ce-robustness-followup-hardening-plan.md
- uv run --no-sync python scripts/validate_issue_mirror.py --issue-file docs/superpowers/issues/2026-06-30-m4-equilibrium-issue-0397-caller-seed-exception-diagnostics.md
- uv run --no-sync python scripts/dev/build_epcsaft.py --build-only --parallel 10
- uv run --no-sync python run_pytest.py packages/epcsaft-equilibrium/tests/api/test_reactive_speciation_api.py -q
