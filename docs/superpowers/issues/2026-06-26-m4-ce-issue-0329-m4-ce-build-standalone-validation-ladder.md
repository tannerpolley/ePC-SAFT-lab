# M4 CE: build standalone validation ladder

**GitHub Issue:** https://github.com/ePC-SAFT/ePC-SAFT/issues/329
**GitHub Milestone:** M4 - Equilibrium
**Issue Type:** task
**Source Spec:** docs/superpowers/specs/2026-06-25-m4-equilibrium-standalone-chemical-equilibrium-before-cpe.md
**Source Plan:** docs/superpowers/plans/2026-06-26-m4-equilibrium-standalone-chemical-equilibrium-before-cpe-plan.md
**Classification:** AFK
**Labels:** enhancement,docs,validation,equilibrium,area:equilibrium,backend:ipopt,type:task,status:ready
**Goal Command:** /goal Build retained standalone CE validation ladder and checker evidence.
**Execution Mode:** Ask at runtime
**Worktree Policy:** Native Codex worktree thread first
**Integration Policy:** Worker PR reviewed by main thread
**TDD Policy:** Required
**Parallelization Plan:** None
**Reviewer Role:** Main thread orchestrator
**Script Gate Mode:** Safety only

## Outcome Summary

**Outcome Source:** docs/superpowers/plans/2026-06-26-m4-equilibrium-standalone-chemical-equilibrium-before-cpe-plan.md#outcome-proof
**Intent:** Build retained analytic, charged, Ascani, MEA, Cantera, and Pope validation ladder.
**Target Output:** Standalone CE checker complete mode consumes every validation family and rejects missing evidence.
**Owner:** M4 equilibrium package owner for packages/epcsaft-equilibrium.
**Interface:** Source plan, issue mirror, route-specific tests, validation checker evidence, registry/capability payloads, and GitHub issue state.
**Cutover:** Replace placeholder or broad closed-ticket state only for this issue's accepted slice; keep unsupported CE/CPE surfaces closed.
**Replaced Path:** Prior prototype evidence, broad closed tickets, or placeholder-only docs cannot stand in for this issue's proof.
**Acceptance Proof:** Standalone CE checker complete mode consumes every validation family and rejects missing evidence.
**Stop Criteria:** Stop if the slice requires implicit standard-state conventions, unproven derivative evidence, unsupported phase coupling, or capability claims beyond this issue.
**Avoid:** Do not add downstream application metrics, regression work, release claims, or reactive phase route admission outside this issue scope.

## Continuation Evidence Update

The MEA validation-ladder proof is superseded by the no-oracle continuation evidence in `docs/superpowers/plans/2026-06-29-m4-ce-generic-pope-homotopy-continuation-plan.md`. The retained MEA record must point to the generated no-oracle summary artifact, report `uses_source_oracle_initial_amounts=false`, use the max-min feasible seed policy, and include continuation-trace and shuffled-subset proof gates. Three-point source-seeded MEA sweeps may remain diagnostic only; they do not prove unassisted standalone CE.

## Project Merge

**Merge Owner:** Main thread orchestrator
**Merge Gate:** Native UI approval required
**Merge Policy:** Repo default
**Worktree Cleanup Policy:** Remove owned worktree after merge
**Orchestrator Wakeup Policy:** Worker handoff or bounded heartbeat

## What To Build

Build retained analytic, charged, Ascani, MEA, Cantera, and Pope validation ladder.

## One-NLP Invariant

The validation ladder must prove the #326 standalone CE route remains the only
executable CE solve path: activation matrix, selector contract, native
`NlpProblem`, Ipopt adapter, and the #325 homogeneous CE block. Complete mode
must reject missing single-path evidence and must not accept checker-only,
oracle-only, direct, VCS, element-potential, or Pope-continuation evidence as a
replacement for the native NLP/Ipopt path.

## Acceptance Criteria

- [ ] Implement the issue slice described in the source plan.
- [ ] Add or update focused tests named in the source plan for this slice.
- [ ] Update docs, registry, capability payloads, and retained validation artifacts when this slice owns them.
- [ ] Run the slice proof oracle plus the plan validators before handoff.
- [ ] Prove complete-mode validation fails when #326 single NLP/Ipopt evidence is missing or bypassed.
- [ ] Preserve CE, PE, and CPE capability boundaries in user-facing text and capability payloads.

## Blocked by

- https://github.com/ePC-SAFT/ePC-SAFT/issues/327
- https://github.com/ePC-SAFT/ePC-SAFT/issues/328

## Non-goals

- Reactive LLE production support outside the standalone CE activation slice.
- Reactive electrolyte LLE production support outside later CPE issue sets.
- Downstream application metrics, parameter regression, or release publication.

## Proof Oracle

- pwsh.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\validate-plan-task-use-cases.ps1 -PlanPath docs/superpowers/plans/2026-06-26-m4-equilibrium-standalone-chemical-equilibrium-before-cpe-plan.md
- pwsh.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\validate-plan-outcome-proof.ps1 -PlanPath docs/superpowers/plans/2026-06-26-m4-equilibrium-standalone-chemical-equilibrium-before-cpe-plan.md
- Slice-specific commands from docs/superpowers/plans/2026-06-26-m4-equilibrium-standalone-chemical-equilibrium-before-cpe-plan.md Task section for this issue.
