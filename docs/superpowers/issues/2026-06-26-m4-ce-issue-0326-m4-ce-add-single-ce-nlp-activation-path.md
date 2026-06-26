# M4 CE: add single CE NLP activation path

**GitHub Issue:** https://github.com/ePC-SAFT/ePC-SAFT/issues/326
**GitHub Milestone:** M4 - Equilibrium
**Issue Type:** feature
**Source Spec:** docs/superpowers/specs/2026-06-25-m4-equilibrium-standalone-chemical-equilibrium-before-cpe.md
**Source Plan:** docs/superpowers/plans/2026-06-26-m4-equilibrium-standalone-chemical-equilibrium-before-cpe-plan.md
**Classification:** AFK
**Labels:** enhancement,docs,validation,equilibrium,area:equilibrium,backend:ipopt,type:feature,status:ready
**Goal Command:** /goal Add the standalone CE route through the single activation-matrix NLP/Ipopt path, with no side-channel algorithm lanes.
**Execution Mode:** Ask at runtime
**Worktree Policy:** Native Codex worktree thread first
**Integration Policy:** Worker PR reviewed by main thread
**TDD Policy:** Required
**Parallelization Plan:** None
**Reviewer Role:** Main thread orchestrator
**Script Gate Mode:** Safety only

## Outcome Summary

**Outcome Source:** docs/superpowers/plans/2026-06-26-m4-equilibrium-standalone-chemical-equilibrium-before-cpe-plan.md#outcome-proof
**Intent:** Add one standalone CE activation path that enters through the activation matrix, selector contract, native `NlpProblem`, and Ipopt adapter.
**Target Output:** Tests and checker mode prove standalone CE uses the single NLP/Ipopt route and the #325 homogeneous CE residual/objective block, without direct, VCS-style, Pope-style, or checker-only bypass paths.
**Owner:** M4 equilibrium package owner for packages/epcsaft-equilibrium.
**Interface:** Source plan, issue mirror, route-specific tests, validation checker evidence, registry/capability payloads, and GitHub issue state.
**Cutover:** Replace placeholder or broad closed-ticket state only for this issue's accepted slice; keep unsupported CE/CPE surfaces closed.
**Replaced Path:** Prior prototype evidence, broad closed tickets, or placeholder-only docs cannot stand in for this issue's proof.
**Acceptance Proof:** Activation-path tests and checker mode prove the standalone CE request is admitted only through the activation matrix and solved only through the native NLP/Ipopt path using the #325 CE residual contract.
**Stop Criteria:** Stop if the slice creates side-channel direct extent, element-potential/VCS-style, Pope-style continuation, checker-only, or public API routes outside the activation matrix and Ipopt adapter.
**Avoid:** Do not add downstream application metrics, regression work, release claims, side-channel CE solvers, or reactive phase route admission outside this issue scope.

## Project Merge

**Merge Owner:** Main thread orchestrator
**Merge Gate:** Native UI approval required
**Merge Policy:** Repo default
**Worktree Cleanup Policy:** Remove owned worktree after merge
**Orchestrator Wakeup Policy:** Worker handoff or bounded heartbeat

## What To Build

Add the standalone CE route through the single activation-matrix NLP/Ipopt path. Direct extent, element-potential/VCS-style, and Pope-style continuation ideas may appear only as non-executing reference notes; they must not become route diagnostics, metadata choices, execution lanes, selector branches, native bindings, public APIs, or checker bypasses.

## Acceptance Criteria

- [ ] Implement the issue slice described in the source plan.
- [ ] Add or update focused tests named in the source plan for this slice.
- [ ] Update docs, registry, capability payloads, and retained validation artifacts when this slice owns them.
- [ ] Run the slice proof oracle plus the plan validators before handoff.
- [ ] Preserve CE, PE, and CPE capability boundaries in user-facing text and capability payloads.

## Blocked by

- https://github.com/ePC-SAFT/ePC-SAFT/issues/325

## Non-goals

- Reactive LLE production support outside the standalone CE activation slice.
- Reactive electrolyte LLE production support outside later CPE issue sets.
- Downstream application metrics, parameter regression, or release publication.
- Direct extent, element-potential/VCS-style, Pope-style continuation, or Cantera-like element-potential side solvers outside the activation matrix.
- Native bindings such as `_native_chemical_equilibrium_algorithm_lanes` or checker modes that prove CE without exercising the activation-matrix NLP route.

## Proof Oracle

- pwsh.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\validate-plan-task-use-cases.ps1 -PlanPath docs/superpowers/plans/2026-06-26-m4-equilibrium-standalone-chemical-equilibrium-before-cpe-plan.md
- pwsh.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\validate-plan-outcome-proof.ps1 -PlanPath docs/superpowers/plans/2026-06-26-m4-equilibrium-standalone-chemical-equilibrium-before-cpe-plan.md
- Slice-specific commands from docs/superpowers/plans/2026-06-26-m4-equilibrium-standalone-chemical-equilibrium-before-cpe-plan.md Task section for this issue.
