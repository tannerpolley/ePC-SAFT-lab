---
issue: 362
title: "M4 PE: implement shared production-route certification contract"
url: https://github.com/ePC-SAFT/ePC-SAFT/issues/362
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
last_synced: "2026-06-29"
---

# M4 PE: implement shared production-route certification contract

**Mirror Retention:** Keep
**GitHub Issue:** https://github.com/ePC-SAFT/ePC-SAFT/issues/362
**GitHub Milestone:** M4 - Equilibrium
**Issue Type:** Feature
**Source Spec:** docs/superpowers/specs/2026-06-29-m4-phase-equilibrium-unified-certification-contract.md
**Source Plan:** docs/superpowers/plans/2026-06-29-m4-equilibrium-issue-0362-shared-production-route-certification-contract-plan.md
**AFK/HITL:** AFK
**Branch:** codex/issue-0362-shared-production-route-certification
**Classification:** AFK
**Labels:** enhancement, agent-ready, native, solver, docs, validation, equilibrium, area:equilibrium, backend:ipopt, status:ready, type:feature
**Goal Command:** /goal Resolve https://github.com/ePC-SAFT/ePC-SAFT/issues/362 using the local mirror and docs/superpowers/plans/2026-06-29-m4-equilibrium-issue-0362-shared-production-route-certification-contract-plan.md. Complete proof oracle: issue acceptance criteria checked and PR merged.
**Execution Mode:** Ask at runtime
**Worktree Policy:** Native Codex worktree thread first
**Integration Policy:** Worker PR reviewed by main thread
**TDD Policy:** Required
**Parallelization Plan:** None
**Reviewer Role:** Main thread orchestrator
**Script Gate Mode:** Safety only

## Outcome Summary
**Outcome Source:** docs/superpowers/plans/2026-06-29-m4-equilibrium-issue-0362-shared-production-route-certification-contract-plan.md#outcome-proof
**Intent:** Implement the first executable shared contract that every production-exposed phase-equilibrium route must satisfy.
**Target Output:** A package-level validator/test fails when a production-exposed PE route lacks shared certification fields or overclaims capability evidence.
**Owner:** M4 equilibrium package owner.
**Interface:** GitHub native sub-issues, local issue mirrors, M4 spec/plan docs, validation checkers, and package-level route contracts.
**Cutover:** Move production-exposed PE route acceptance to the shared contract while planned/private routes remain declared planned.
**Replaced Path:** Route-specific tests that can pass while omitting discovery, postsolve, residual, or capability evidence.
**Acceptance Proof:** Focused package tests and registry/capability checks prove the shared contract over all production-exposed routes.
**Stop Criteria:** Stop if the route inventory cannot distinguish production-exposed, private, diagnostic, and planned routes.
**Avoid:** Do not force planned routes to pass production gates or add solver dodge flags.

## Project Merge

**Merge Owner:** Main thread orchestrator
**Merge Gate:** Native UI approval required
**Merge Policy:** Repo default
**Worktree Cleanup Policy:** Remove owned worktree after merge
**Orchestrator Wakeup Policy:** Worker handoff or bounded heartbeat

## What To Build

Add the shared certification schema, route inventory assertions, and package-level tests for production-exposed phase-equilibrium routes.

## Acceptance Criteria

- [ ] Production-exposed routes emit or map to one shared certification shape.
- [ ] Planned/private routes remain declared without fake production support.
- [ ] Registry/capability tests fail if support claims outpace evidence.

## Blocked by

- None.

## Non-goals

- No M5 parameter regression in this M4 tracker issue.
- No release claim.
- No downstream application metrics.
- No diagnostic-only success counted as production route support.

## Proof Oracle

- uv run --no-sync python -m pytest packages\epcsaft-equilibrium\tests -k "certification and phase and equilibrium" -q
- uv run --no-sync python -m pytest tests\native\contracts\test_equilibrium_benchmark_registry.py tests\native\contracts\test_generalized_equilibrium_registry.py -q
