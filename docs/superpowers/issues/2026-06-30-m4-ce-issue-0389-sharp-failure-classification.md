# M4 CE: classify convergence failures sharply

**GitHub Issue:** https://github.com/ePC-SAFT/ePC-SAFT/issues/389
**GitHub Milestone:** M4 - Equilibrium
**Issue Type:** task
**Source Spec:** docs/superpowers/specs/2026-06-30-m4-ce-convergence-robustness-hardening.md
**Source Plan:** docs/superpowers/plans/2026-06-30-m4-ce-convergence-robustness-hardening-plan.md
**Classification:** AFK
**Labels:** agent-ready,status:ready,type:task,area:equilibrium,equilibrium,solver,native,backend:ipopt,validation
**Goal Command:** /goal Classify CE convergence failures by exact failing proof gate and preserve original diagnostics.
**Execution Mode:** Ask at runtime
**Worktree Policy:** Native Codex worktree thread first
**Integration Policy:** Current thread owns PR
**TDD Policy:** Required
**Parallelization Plan:** None
**Reviewer Role:** Main thread orchestrator
**Script Gate Mode:** Safety only

## Outcome Summary

**Outcome Source:** docs/superpowers/plans/2026-06-30-m4-ce-convergence-robustness-hardening-plan.md#outcome-proof
**Intent:** Replace ambiguous CE convergence failures with stable classes tied to the exact failing proof gate.
**Target Output:** Result diagnostics and retained robustness rows classify infeasible conservation, initialization failure, Ipopt failure, proof-correction failure, stationarity failure, balance failure, EOS activity failure, and unsupported standard-state request.
**Owner:** M4 equilibrium package owner for packages/epcsaft-equilibrium.
**Interface:** Native CE status payloads, Python result diagnostics, retained diagnostics, and standalone CE checker output.
**Cutover:** Stable failure classes become the loop-routing evidence for future CE repair work.
**Replaced Path:** Generic convergence status text is displaced by proof-gate classification plus original diagnostic detail.
**Acceptance Proof:** Focused tests assert every required failure class and the checker rejects unclassified retained failures.
**Stop Criteria:** Stop if classification loses original Ipopt/proof details or hides the failing physical gate.
**Avoid:** Do not convert failures to success states, suppress diagnostics, or add broad catch-all proof claims.

## Project Merge

**Merge Owner:** Main thread orchestrator
**Merge Gate:** Native UI approval required
**Merge Policy:** Repo default
**Worktree Cleanup Policy:** Remove owned worktree after merge
**Orchestrator Wakeup Policy:** Inline run

## What To Build

Implement Task 7 from the source plan: sharp CE failure classification across native, Python, retained diagnostics, and checker output.

## Acceptance Criteria

- [ ] Tests cover infeasible conservation, initialization failure, Ipopt failure, proof-correction failure, stationarity failure, balance failure, EOS activity failure, and unsupported standard-state request.
- [ ] Result diagnostics preserve original Ipopt and proof details.
- [ ] Retained robustness rows include the same stable failure class field.
- [ ] Standalone CE checker rejects unclassified failures.

## Blocked by

- None

## Non-goals

- Treating classified failure as completion.
- Broad catch-all statuses that hide proof gates.
- Public route or capability broadening.

## Proof Oracle

- pwsh.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\validate-plan-task-use-cases.ps1 -PlanPath docs/superpowers/plans/2026-06-30-m4-ce-convergence-robustness-hardening-plan.md
- pwsh.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\validate-plan-outcome-proof.ps1 -PlanPath docs/superpowers/plans/2026-06-30-m4-ce-convergence-robustness-hardening-plan.md
- Focused taxonomy/checker commands from Task 7 of the source plan.
