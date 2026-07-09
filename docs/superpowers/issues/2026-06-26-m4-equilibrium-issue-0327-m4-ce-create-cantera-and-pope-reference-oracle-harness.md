---
issue: 327
title: "M4 CE: create Cantera and Pope reference-oracle harness"
url: https://github.com/ePC-SAFT/ePC-SAFT/issues/327
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
last_synced: "2026-06-26"
---

# M4 CE: create Cantera and Pope reference-oracle harness

**Mirror Retention:** Keep
**GitHub Issue:** https://github.com/ePC-SAFT/ePC-SAFT/issues/327
**GitHub Milestone:** M4 - Equilibrium
**Issue Type:** task
**Source Spec:** docs/superpowers/specs/2026-06-25-m4-equilibrium-standalone-chemical-equilibrium-before-cpe.md
**Source Plan:** docs/superpowers/plans/2026-06-26-m4-equilibrium-standalone-chemical-equilibrium-before-cpe-plan.md
**AFK/HITL:** AFK
**Classification:** AFK
**Labels:** enhancement,docs,validation,equilibrium,area:equilibrium,backend:ipopt,type:task,status:ready
**Goal Command:** /goal Create retained CE-only Cantera/Pope oracle fixtures and tests.
**Execution Mode:** Ask at runtime
**Worktree Policy:** Native Codex worktree thread first
**Integration Policy:** Worker PR reviewed by main thread
**TDD Policy:** Required
**Parallelization Plan:** None
**Reviewer Role:** Main thread orchestrator
**Script Gate Mode:** Safety only

## Outcome Summary

**Outcome Source:** docs/superpowers/plans/2026-06-26-m4-equilibrium-standalone-chemical-equilibrium-before-cpe-plan.md#outcome-proof
**Intent:** Create retained CE-only Cantera and Pope oracle records.
**Target Output:** Oracle tests prove retained records include source, solver, species order, balances, affinities, and CE-only scope.
**Owner:** M4 equilibrium package owner for packages/epcsaft-equilibrium.
**Interface:** Source plan, issue mirror, route-specific tests, validation checker evidence, registry/capability payloads, and GitHub issue state.
**Cutover:** Replace placeholder or broad closed-ticket state only for this issue's accepted slice; keep unsupported CE/CPE surfaces closed.
**Replaced Path:** Prior prototype evidence, broad closed tickets, or placeholder-only docs cannot stand in for this issue's proof.
**Acceptance Proof:** Oracle tests prove retained records include source, solver, species order, balances, affinities, and CE-only scope.
**Stop Criteria:** Stop if the slice requires implicit standard-state conventions, unproven derivative evidence, unsupported phase coupling, or capability claims beyond this issue.
**Avoid:** Do not add downstream application metrics, regression work, release claims, or reactive phase route admission outside this issue scope.

## Project Merge

**Merge Owner:** Main thread orchestrator
**Merge Gate:** Native UI approval required
**Merge Policy:** Repo default
**Worktree Cleanup Policy:** Remove owned worktree after merge
**Orchestrator Wakeup Policy:** Worker handoff or bounded heartbeat

## What To Build

Create retained CE-only Cantera and Pope oracle records.

## One-NLP Invariant

Cantera and Pope records are reference oracles only. This issue must preserve
the #326 standalone CE solve route as the only executable CE path: activation
matrix, selector contract, native `NlpProblem`, Ipopt adapter, and the #325
homogeneous CE block. Oracle fixtures may compare against that path, but must
not introduce a checker-only binding, direct solver lane, VCS/element-potential
execution path, or public algorithm selector.

## Acceptance Criteria

- [ ] Implement the issue slice described in the source plan.
- [ ] Add or update focused tests named in the source plan for this slice.
- [ ] Update docs, registry, capability payloads, and retained validation artifacts when this slice owns them.
- [ ] Run the slice proof oracle plus the plan validators before handoff.
- [ ] Prove the retained oracle evidence is consumed by the #326 single NLP/Ipopt path, not by an alternate CE solve route.
- [ ] Preserve CE, PE, and CPE capability boundaries in user-facing text and capability payloads.

## Blocked by

- https://github.com/ePC-SAFT/ePC-SAFT/issues/326

## Non-goals

- Reactive LLE production support outside the standalone CE activation slice.
- Reactive electrolyte LLE production support outside later CPE issue sets.
- Downstream application metrics, parameter regression, or release publication.

## Proof Oracle

- uv run --no-sync python scripts/validate_plan_task_use_cases.py --plan-path docs/superpowers/plans/2026-06-26-m4-equilibrium-standalone-chemical-equilibrium-before-cpe-plan.md
- uv run --no-sync python scripts/validate_plan_outcome_proof.py --plan-path docs/superpowers/plans/2026-06-26-m4-equilibrium-standalone-chemical-equilibrium-before-cpe-plan.md
- Slice-specific commands from docs/superpowers/plans/2026-06-26-m4-equilibrium-standalone-chemical-equilibrium-before-cpe-plan.md Task section for this issue.
