---
issue: 344
title: "M4: define HELD2 public-route doctrine and validation matrix"
url: "https://github.com/ePC-SAFT/ePC-SAFT/issues/344"
state: "open"
milestone: "M4 - Equilibrium"
project: "ePC-SAFT Roadmap"
package: "equilibrium"
capability: "electrolyte"
backend: "Ipopt"
readiness: "ready"
release_target: "equilibrium-0.x"
source_spec: "docs/superpowers/specs/2026-06-27-m4-equilibrium-held2-public-route-phase-discovery-full-adoption.md"
source_plan: "docs/superpowers/plans/2026-06-27-m4-equilibrium-held2-public-route-phase-discovery-full-adoption-plan.md"
afk_hitl: "AFK"
branch: codex/issue-0344-held2-public-route-doctrine-validation-matrix
last_synced: "2026-06-27"
---

# M4: define HELD2 public-route doctrine and validation matrix

**GitHub Issue:** https://github.com/ePC-SAFT/ePC-SAFT/issues/344
**GitHub Milestone:** M4 - Equilibrium
**Issue Type:** task
**Source Spec:** docs/superpowers/specs/2026-06-27-m4-equilibrium-held2-public-route-phase-discovery-full-adoption.md
**Source Plan:** docs/superpowers/plans/2026-06-27-m4-equilibrium-held2-public-route-phase-discovery-full-adoption-plan.md
**Classification:** AFK
**Labels:** enhancement, native, solver, docs, validation, equilibrium, area:equilibrium, backend:ipopt, status:ready, agent-ready, type:task
**Goal Command:** /goal Resolve issue 344 by writing the HELD2 public-route doctrine and validation matrix.
**Execution Mode:** Ask at runtime
**Worktree Policy:** Native Codex worktree thread first
**Integration Policy:** Worker PR reviewed by main thread
**TDD Policy:** Required
**Parallelization Plan:** None
**Reviewer Role:** Main thread orchestrator
**Script Gate Mode:** Safety plus docs proof

## Outcome Summary

**Intent:** Convert the full HELD2 adoption spec into executable route doctrine.
**Target Output:** Source-backed equations, state transitions, validation cases, tolerances, and proof boundaries for future implementation slices.
**Owner:** `packages/epcsaft-equilibrium`.
**Interface:** M4 milestone docs, source spec, issue mirrors, validation scripts, and future native route contracts.
**Cutover:** Replace ambiguous long-term wording with a numbered validation matrix before any runtime public-route cutover.
**Replaced Path:** Treating #302, #306, #314, or #320 as complete HELD2 public-route discovery.
**Acceptance Proof:** Docs validation and plan validators pass.
**Stop Criteria:** Stop if source equations, residual families, fixture scope, or acceptance tolerances cannot be stated without inventing unsupported physics.
**Avoid:** Do not modify runtime solver code in this doctrine slice.

## What To Build

Define route-level equations, reduced-electroneutral variables, candidate
lifecycle states, residual families, validation cases, and acceptance
tolerances for full HELD2 public-route adoption.

## Acceptance Criteria

- [ ] Doctrine names Stage I, Stage II, Stage III, postsolve, and public-route cutover responsibilities.
- [ ] Validation matrix covers stable, unstable, boundary, phase-label, neutral-limit, common-ion, and mixed-salt scenarios.
- [ ] Projected electrochemical and mean-ionic residuals are required for charged transfer evidence.
- [ ] Raw single-ion equality, hidden charge clipping, residual-only success, and fallback solver flags are rejected as acceptance evidence.
- [ ] Public-route capability remains closed until implementation slices pass.

## Blocked by

- None

## Non-goals

- No runtime implementation.
- No registry capability admission.
- No M5 regression work.

## Proof Oracle

```powershell
pwsh.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\validate-plan-task-use-cases.ps1 -PlanPath docs\superpowers\plans\2026-06-27-m4-equilibrium-held2-public-route-phase-discovery-full-adoption-plan.md
pwsh.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\validate-plan-outcome-proof.ps1 -PlanPath docs\superpowers\plans\2026-06-27-m4-equilibrium-held2-public-route-phase-discovery-full-adoption-plan.md
uv run --no-sync python scripts\dev\validate_project.py docs
```
