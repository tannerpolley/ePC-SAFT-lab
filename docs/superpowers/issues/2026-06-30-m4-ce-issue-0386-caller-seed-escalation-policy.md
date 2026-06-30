# M4 CE: harden caller seed escalation policy

**GitHub Issue:** https://github.com/ePC-SAFT/ePC-SAFT/issues/386
**GitHub Milestone:** M4 - Equilibrium
**Issue Type:** task
**Source Spec:** docs/superpowers/specs/2026-06-30-m4-ce-convergence-robustness-hardening.md
**Source Plan:** docs/superpowers/plans/2026-06-30-m4-ce-convergence-robustness-hardening-plan.md
**Classification:** AFK
**Labels:** agent-ready,status:ready,type:task,area:equilibrium,equilibrium,solver,native,backend:ipopt,validation
**Goal Command:** /goal Treat caller-provided CE seeds as proof-required hints and escalate failed seeds through CE-owned initialization.
**Branch:** codex/m4-ce-generic-pope-homotopy-continuation
**Execution Mode:** Ask at runtime
**Worktree Policy:** Native Codex worktree thread first
**Integration Policy:** Current thread owns PR
**TDD Policy:** Required
**Parallelization Plan:** None
**Reviewer Role:** Main thread orchestrator
**Script Gate Mode:** Safety only

## Outcome Summary

**Outcome Source:** docs/superpowers/plans/2026-06-30-m4-ce-convergence-robustness-hardening-plan.md#outcome-proof
**Intent:** Make caller seed handling explicit, proof-driven, and recoverable when a positive but poor seed fails strict final proof.
**Target Output:** Public API diagnostics report seed attempt order, caller seed proof status, escalation path, and final accepted seed source.
**Owner:** M4 equilibrium package owner for packages/epcsaft-equilibrium.
**Interface:** `reactive_speciation` seed arguments, Python validation, native seed provenance, and result diagnostics.
**Cutover:** Caller seeds become hints that require proof; CE-owned initialization becomes the authoritative recovery path.
**Replaced Path:** Treating a caller seed as trusted proof input is displaced by independent final proof and escalation diagnostics.
**Acceptance Proof:** Focused API tests cover good seeds, bad positive seeds, invalid nonpositive seeds, and escalation to CE-owned initialization.
**Stop Criteria:** Stop if seed escalation hides invalid inputs or accepts caller-seeded results without final proof.
**Avoid:** Do not add silent seed repair, fake default amounts, or source-oracle proof seeding.

## Project Merge

**Merge Owner:** Main thread orchestrator
**Merge Gate:** Native UI approval required
**Merge Policy:** Repo default
**Worktree Cleanup Policy:** Remove owned worktree after merge
**Orchestrator Wakeup Policy:** Inline run

## What To Build

Implement Task 4 from the source plan: caller seed validation, proof-first escalation, and seed provenance diagnostics.

## Acceptance Criteria

- [ ] Good caller seeds still solve when they pass final proof.
- [ ] Bad positive caller seeds escalate through CE-owned initialization and record that escalation.
- [ ] Nonpositive or shape-invalid caller seeds fail before native solving.
- [ ] Diagnostics identify attempted and accepted seed sources.

## Blocked by

- None

## Non-goals

- Using source-oracle seeds as proof.
- Hidden seed repair.
- Public initializer route exposure.

## Proof Oracle

- pwsh.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\validate-plan-task-use-cases.ps1 -PlanPath docs/superpowers/plans/2026-06-30-m4-ce-convergence-robustness-hardening-plan.md
- pwsh.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\validate-plan-outcome-proof.ps1 -PlanPath docs/superpowers/plans/2026-06-30-m4-ce-convergence-robustness-hardening-plan.md
- Focused API commands from Task 4 of the source plan.
