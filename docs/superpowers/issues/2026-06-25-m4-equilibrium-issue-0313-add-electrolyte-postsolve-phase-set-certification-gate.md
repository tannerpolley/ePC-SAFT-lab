---
issue: 313
title: "M4: add electrolyte postsolve phase-set certification gate"
url: "https://github.com/ePC-SAFT/ePC-SAFT/issues/313"
state: "open"
milestone: "M4 - Equilibrium"
project: "ePC-SAFT Roadmap"
package: "equilibrium"
capability: "electrolyte"
backend: "Ipopt"
readiness: "blocked"
release_target: "equilibrium-0.x"
source_spec: "docs/superpowers/specs/2026-05-30-m4-equilibrium-issue-0191-prove-electrolyte-gfpe-and-held2-0-validation-gates.md"
source_plan: "docs/superpowers/plans/2026-06-25-m4-equilibrium-issue-0313-electrolyte-postsolve-phase-set-certification-gate-plan.md"
afk_hitl: "AFK"
branch: codex/issue-0313-electrolyte-postsolve-certification
last_synced: "2026-06-25"
---

# M4: add electrolyte postsolve phase-set certification gate

**GitHub Issue:** https://github.com/ePC-SAFT/ePC-SAFT/issues/313
**GitHub Milestone:** M4 - Equilibrium
**Issue Type:** Feature
**Source Spec:** docs/superpowers/specs/2026-05-30-m4-equilibrium-issue-0191-prove-electrolyte-gfpe-and-held2-0-validation-gates.md
**Source Plan:** docs/superpowers/plans/2026-06-25-m4-equilibrium-issue-0313-electrolyte-postsolve-phase-set-certification-gate-plan.md
**Classification:** AFK
**Labels:** enhancement, native, solver, docs, validation, equilibrium, area:equilibrium, backend:ipopt, status:blocked, type:feature
**Goal Command:** /goal Resolve https://github.com/ePC-SAFT/ePC-SAFT/issues/313 using docs/superpowers/issues/2026-06-25-m4-equilibrium-issue-0313-add-electrolyte-postsolve-phase-set-certification-gate.md and docs/superpowers/plans/2026-06-25-m4-equilibrium-issue-0313-electrolyte-postsolve-phase-set-certification-gate-plan.md after #312 closes. Complete proof oracle: issue acceptance criteria checked and PR merged.
**Execution Mode:** Ask at runtime
**Worktree Policy:** Native Codex worktree thread first
**Integration Policy:** Worker PR reviewed by main thread
**TDD Policy:** Required
**Parallelization Plan:** None
**Reviewer Role:** Main thread orchestrator
**Script Gate Mode:** Safety only

## Outcome Summary

**Outcome Source:** docs/superpowers/plans/2026-06-25-m4-equilibrium-issue-0313-electrolyte-postsolve-phase-set-certification-gate-plan.md#outcome-proof
**Intent:** Certify the refined electrolyte phase set after Stage III solves, separating mathematical convergence from physical electrolyte acceptance.
**Target Output:** `scripts/validation/check_electrolyte_postsolve_certification.py --json --require-stage-iii --require-postsolve-certification --require-public-routes-closed --require-complete` returns `complete: true`.
**Owner:** M4 equilibrium package owner.
**Interface:** Electrolyte postsolve payload, retained checker JSON, pytest contracts, M4 issue mirror, registry row, and M4 README.
**Cutover:** This checker becomes the #313 proof oracle; #191 remains blocked by #313/#314 until the child sequence closes.
**Replaced Path:** Stage III convergence-only evidence remains prerequisite evidence and no longer stands in for physical electrolyte acceptance.
**Acceptance Proof:** Acceptance is proven when postsolve certification consumes #312, reports explicit-ion reconstruction, charge balance, neutral and mean-ionic transfer residuals, pressure consistency, phase amounts, and domain margins with closed public route state.
**Stop Criteria:** Stop if any physical certification family is absent or if a public electrolyte route must be opened to satisfy this gate.
**Avoid:** Do not admit public electrolyte routes, add reactive routes, regression work, downstream study logic, or release claims.

## Project Merge

**Merge Owner:** Main thread orchestrator
**Merge Gate:** Native UI approval required
**Merge Policy:** Repo default
**Worktree Cleanup Policy:** Remove owned worktree after merge
**Orchestrator Wakeup Policy:** Worker handoff or bounded heartbeat

## What To Build

Add the postsolve certification gate for electrolyte GFPE. It must consume the
Stage III reduced-variable refinement result and certify the explicit-ion
reconstructed state, per-phase charge balance, phase amounts, pressure
consistency, neutral transfer, mean-ionic transfer bookkeeping,
composition/domain margins, and capability boundary state.

## Parent And Dependencies

- Parent issue: https://github.com/ePC-SAFT/ePC-SAFT/issues/191
- Blocks: https://github.com/ePC-SAFT/ePC-SAFT/issues/191 and https://github.com/ePC-SAFT/ePC-SAFT/issues/314
- Blocked by: https://github.com/ePC-SAFT/ePC-SAFT/issues/312

## Acceptance Criteria

- [ ] The checker consumes the closed #312 Stage III refinement gate.
- [ ] Explicit-ion material reconstruction closes to a retained tolerance from the reduced electroneutral solution.
- [ ] Per-phase and total charge residuals are retained and accepted.
- [ ] Neutral transfer and mean-ionic transfer residuals are reported separately with documented conventions.
- [ ] Pressure consistency, phase amounts, phase composition normalization, nonnegativity margins, and domain margins are retained.
- [ ] Negative tests reject Stage III-only results, phase-collapsed results, charge-imbalanced phases, missing transfer diagnostics, and premature public-admission status.
- [ ] Capabilities and registry evidence keep public electrolyte routes closed.
- [ ] #191 and the M4 README name #314 as the only remaining M4 electrolyte gate after this issue closes.

## Blocked by

- https://github.com/ePC-SAFT/ePC-SAFT/issues/312

## Non-Goals

- No public electrolyte route admission.
- No reactive, CE, CPE, regression, downstream, release, or publication claim.

## Proof Oracle

```powershell
pwsh.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\validate-plan-task-use-cases.ps1 -PlanPath docs\superpowers\plans\2026-06-25-m4-equilibrium-issue-0313-electrolyte-postsolve-phase-set-certification-gate-plan.md
pwsh.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\validate-plan-outcome-proof.ps1 -PlanPath docs\superpowers\plans\2026-06-25-m4-equilibrium-issue-0313-electrolyte-postsolve-phase-set-certification-gate-plan.md
uv run --no-sync python scripts/validation/check_electrolyte_postsolve_certification.py --json --require-stage-iii --require-postsolve-certification --require-public-routes-closed --require-complete
uv run --no-sync python run_pytest.py tests/native/contracts/test_electrolyte_postsolve_certification.py tests/native/contracts/test_electrolyte_stage_iii_refinement.py packages/epcsaft-equilibrium/tests/contracts/test_activation_capabilities.py tests/native/contracts/test_generalized_equilibrium_registry.py -q
uv run --no-sync python scripts/dev/validate_project.py docs
pwsh.exe -NoProfile -ExecutionPolicy Bypass -File "$env:USERPROFILE\.codex\hooks\codex-cleanup.ps1" -RepoRoot .
```
