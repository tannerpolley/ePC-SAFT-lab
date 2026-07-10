---
issue: 328
title: "M4 CE: design standalone speciation public API and result schema"
url: https://github.com/ePC-SAFT/ePC-SAFT/issues/328
state: open
milestone: "M4 - Equilibrium"
project: "ePC-SAFT Roadmap"
package: equilibrium
capability: null
backend: Ipopt
readiness: ready
release_target: equilibrium-0.x
source_spec: docs/superpowers/specs/2026-06-25-m4-equilibrium-standalone-chemical-equilibrium-before-cpe.md
source_plan: docs/superpowers/plans/2026-06-26-m4-equilibrium-standalone-chemical-equilibrium-before-cpe-plan.md
afk_hitl: AFK
branch: codex/issue-0328-m4-ce-design-standalone-speciation-public-api-and-result-schema
last_synced: "2026-06-26"
---

# M4 CE: design standalone speciation public API and result schema

**GitHub Issue:** https://github.com/ePC-SAFT/ePC-SAFT/issues/328
**GitHub Milestone:** M4 - Equilibrium
**Issue Type:** feature
**Source Spec:** docs/superpowers/specs/2026-06-25-m4-equilibrium-standalone-chemical-equilibrium-before-cpe.md
**Source Plan:** docs/superpowers/plans/2026-06-26-m4-equilibrium-standalone-chemical-equilibrium-before-cpe-plan.md
**AFK/HITL:** AFK
**Classification:** AFK
**Labels:** enhancement,docs,validation,equilibrium,area:equilibrium,backend:ipopt,type:feature,status:ready
**Goal Command:** /goal Add standalone reactive_speciation API/result schema without CPE claims.
**Execution Mode:** Ask at runtime
**Worktree Policy:** Native Codex worktree thread first
**Integration Policy:** Worker PR reviewed by main thread
**TDD Policy:** Required
**Parallelization Plan:** None
**Reviewer Role:** Main thread orchestrator
**Script Gate Mode:** Safety only

## Outcome Summary

**Outcome Source:** docs/superpowers/plans/2026-06-26-m4-equilibrium-standalone-chemical-equilibrium-before-cpe-plan.md#outcome-proof
**Intent:** Expose standalone CE/speciation API and result schema without reactive phase claims.
**Target Output:** API and capability tests prove standalone CE fields and closed reactive LLE/CPE surfaces.
**Owner:** M4 equilibrium package owner for packages/epcsaft-equilibrium.
**Interface:** Source plan, issue mirror, route-specific tests, validation checker evidence, registry/capability payloads, and GitHub issue state.
**Cutover:** Replace placeholder or broad closed-ticket state only for this issue's accepted slice; keep unsupported CE/CPE surfaces closed.
**Replaced Path:** Prior prototype evidence, broad closed tickets, or placeholder-only docs cannot stand in for this issue's proof.
**Acceptance Proof:** API and capability tests prove standalone CE fields and closed reactive LLE/CPE surfaces.
**Stop Criteria:** Stop if the slice requires implicit standard-state conventions, unproven derivative evidence, unsupported phase coupling, or capability claims beyond this issue.
**Avoid:** Do not add downstream application metrics, regression work, release claims, or reactive phase route admission outside this issue scope.

## Project Merge

**Merge Owner:** Main thread orchestrator
**Merge Gate:** Native UI approval required
**Merge Policy:** Repo default
**Worktree Cleanup Policy:** Remove owned worktree after merge
**Orchestrator Wakeup Policy:** Worker handoff or bounded heartbeat

## What To Build

Expose standalone CE/speciation API and result schema without reactive phase claims.

## One-NLP Invariant

The public `reactive_speciation` API and result schema must expose the #326
standalone CE route only: activation matrix, selector contract, native
`NlpProblem`, Ipopt adapter, and the #325 homogeneous CE block. Internal
continuation and diagnostic strategies may support that route, but they must
not create a second public route, solver bypass, checker-only execution path,
or alternate algorithm selector.

## Acceptance Criteria

- [ ] Implement the issue slice described in the source plan.
- [ ] Add or update focused tests named in the source plan for this slice.
- [ ] Update docs, registry, capability payloads, and retained validation artifacts when this slice owns them.
- [ ] Run the slice proof oracle plus the plan validators before handoff.
- [ ] Prove the public API and result schema report the single native NLP/Ipopt path without exposing a second CE route or solver bypass.
- [ ] Preserve CE, PE, and CPE capability boundaries in user-facing text and capability payloads.

## Blocked by

- https://github.com/ePC-SAFT/ePC-SAFT/issues/325

## Non-goals

- Reactive LLE production support outside the standalone CE activation slice.
- Reactive electrolyte LLE production support outside later CPE issue sets.
- Downstream application metrics, parameter regression, or release publication.

## Proof Oracle

- uv run --no-sync python scripts/validate_plan_task_use_cases.py --plan-path docs/superpowers/plans/2026-06-26-m4-equilibrium-standalone-chemical-equilibrium-before-cpe-plan.md
- uv run --no-sync python scripts/validate_plan_outcome_proof.py --plan-path docs/superpowers/plans/2026-06-26-m4-equilibrium-standalone-chemical-equilibrium-before-cpe-plan.md
- Slice-specific commands from docs/superpowers/plans/2026-06-26-m4-equilibrium-standalone-chemical-equilibrium-before-cpe-plan.md Task section for this issue.
