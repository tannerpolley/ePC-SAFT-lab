---
issue: 314
title: "M4: admit source-backed public electrolyte GFPE route"
url: "https://github.com/ePC-SAFT/ePC-SAFT/issues/314"
state: "open"
milestone: "M4 - Equilibrium"
project: "ePC-SAFT Roadmap"
package: "equilibrium"
capability: "electrolyte"
backend: "Ipopt"
readiness: "in_progress"
release_target: "equilibrium-0.x"
source_spec: "docs/superpowers/specs/2026-05-30-m4-equilibrium-issue-0191-prove-electrolyte-gfpe-and-held2-0-validation-gates.md"
source_plan: "docs/superpowers/plans/2026-06-25-m4-equilibrium-issue-0314-electrolyte-public-route-admission-gate-plan.md"
afk_hitl: "AFK"
branch: codex/issue-0314-electrolyte-public-admission
last_synced: "2026-06-25"
---

# M4: admit source-backed public electrolyte GFPE route

**GitHub Issue:** https://github.com/ePC-SAFT/ePC-SAFT/issues/314
**GitHub Milestone:** M4 - Equilibrium
**Issue Type:** Feature
**Source Spec:** docs/superpowers/specs/2026-05-30-m4-equilibrium-issue-0191-prove-electrolyte-gfpe-and-held2-0-validation-gates.md
**Source Plan:** docs/superpowers/plans/2026-06-25-m4-equilibrium-issue-0314-electrolyte-public-route-admission-gate-plan.md
**Classification:** AFK
**Labels:** enhancement, native, solver, docs, validation, equilibrium, area:equilibrium, backend:ipopt, status:ready, type:feature
**Goal Command:** /goal Resolve https://github.com/ePC-SAFT/ePC-SAFT/issues/314 using docs/superpowers/issues/2026-06-25-m4-equilibrium-issue-0314-admit-source-backed-public-electrolyte-gfpe-route.md and docs/superpowers/plans/2026-06-25-m4-equilibrium-issue-0314-electrolyte-public-route-admission-gate-plan.md after #313 closes. Complete proof oracle: issue acceptance criteria checked, PR merged, and #191 closeout evidence prepared.
**Execution Mode:** Ask at runtime
**Worktree Policy:** Native Codex worktree thread first
**Integration Policy:** Worker PR reviewed by main thread
**TDD Policy:** Required
**Parallelization Plan:** None
**Reviewer Role:** Main thread orchestrator
**Script Gate Mode:** Safety only

## Outcome Summary

**Outcome Source:** docs/superpowers/plans/2026-06-25-m4-equilibrium-issue-0314-electrolyte-public-route-admission-gate-plan.md#outcome-proof
**Intent:** Admit only the certified, source-backed public electrolyte GFPE route surface after every prior #191 gate is closed.
**Target Output:** `scripts/validation/check_electrolyte_public_admission.py --json --require-source-gate --require-readiness-gate --require-tpd-gate --require-held2-discovery --require-stage-iii --require-postsolve-certification --require-public-admission --require-complete` returns `complete: true`.
**Owner:** M4 equilibrium package owner.
**Interface:** Public `Equilibrium` route contract, activation matrix, capability payload, retained checker JSON, docs, M4 registry, and #191 closeout evidence.
**Cutover:** Open the certified electrolyte route surface and remove closed-route assertions that are no longer true for that exact scope.
**Replaced Path:** Permanent closed electrolyte route state after executable source-backed certification exists.
**Acceptance Proof:** Acceptance is proven when the public admission checker consumes all prerequisite gates, proves the route returns certified electrolyte phase-set results, and keeps unsupported reactive/generalized/regression claims closed.
**Stop Criteria:** Stop if prerequisite evidence is missing, if capability claims outrun executable evidence, or if admission requires reactive/CE/CPE support.
**Avoid:** Do not add reactive equilibrium, parameter regression, downstream application metrics, release claims, or broad electrolyte families beyond the retained source-backed evidence.

## Project Merge

**Merge Owner:** Main thread orchestrator
**Merge Gate:** Native UI approval required
**Merge Policy:** Repo default
**Worktree Cleanup Policy:** No worktree created
**Orchestrator Wakeup Policy:** Worker handoff or bounded heartbeat

## What To Build

Admit the certified electrolyte GFPE route only after the postsolve
certification child closes. This issue updates the selector/admission path,
public capability evidence, benchmark registry, docs, and tests so user-facing
electrolyte support matches the exact source-backed validation scope. It is
retained as representative public-route admission evidence only; #191 remains
blocked by #320 until full Khudaida figure-level model reproduction and HELD2
flash scenario gates pass.

## Parent And Dependencies

- Parent issue: https://github.com/ePC-SAFT/ePC-SAFT/issues/191
- Blocks: https://github.com/ePC-SAFT/ePC-SAFT/issues/191
- Prerequisite satisfied by this sequence: https://github.com/ePC-SAFT/ePC-SAFT/issues/313

## Implementation Results

The #314 branch adds the retained public admission checker and admits only the
source-backed Khudaida explicit-ion H2O/Ethanol/Butanol/Na+/Cl- NaCl
mixed-solvent LLE route through
`Equilibrium(..., route="electrolyte_lle")`. The retained checker consumes
#269/#300/#302/#306/#312/#313 and reports `complete: true`, `blockers: []`,
phase labels `liquid1` and `liquid2`, per-phase charge residuals `[0.0, 0.0]`,
total charge residual `0.0`, pressure consistency norm
`6.984919309616089e-10`, phase distance `2.7722252287643023e-06`, neutral
transfer residual max `1.1078450725898747e-05`, mean-ionic transfer residual
max `3.3871562834519864e-05`, and exact reduced Hessian availability while
keeping reactive, CE/CPE, regression, and release claims closed.

## Acceptance Criteria

- [x] The public admission checker consumes #269, #300, #302, #306, #312, and #313 evidence.
- [x] The public route surface exposes only the certified electrolyte GFPE scope.
- [x] Capability evidence distinguishes neutral, associating, electrolyte, and reactive support.
- [x] Registry evidence names the source fixture, parameter bundle, validation checkers, tolerances, and public route status.
- [x] User-facing docs state the admitted electrolyte scope and explicit non-goals.
- [x] Negative tests reject missing prerequisite evidence, uncertified phase sets, unsupported species bases, and premature reactive admission.
- [x] #191 closeout evidence is prepared; the umbrella should close only after this issue merges and the retained public-admission checker passes on main.
- [x] M4 README identifies #191 as ready to close after #314 merges.

## Prerequisite

- https://github.com/ePC-SAFT/ePC-SAFT/issues/313

## Non-Goals

- No reactive route admission.
- No CE/CPE support claim.
- No parameter regression or downstream application metrics.
- No release publication claim.

## Proof Oracle

```powershell
pwsh.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\validate-plan-task-use-cases.ps1 -PlanPath docs\superpowers\plans\2026-06-25-m4-equilibrium-issue-0314-electrolyte-public-route-admission-gate-plan.md
pwsh.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\validate-plan-outcome-proof.ps1 -PlanPath docs\superpowers\plans\2026-06-25-m4-equilibrium-issue-0314-electrolyte-public-route-admission-gate-plan.md
uv run --no-sync python scripts/validation/check_electrolyte_public_admission.py --json --require-source-gate --require-readiness-gate --require-tpd-gate --require-held2-discovery --require-stage-iii --require-postsolve-certification --require-public-admission --require-complete
uv run --no-sync python run_pytest.py tests/native/contracts/test_electrolyte_public_admission.py tests/native/contracts/test_electrolyte_postsolve_certification.py packages/epcsaft-equilibrium/tests/contracts/test_activation_capabilities.py tests/native/contracts/test_generalized_equilibrium_registry.py -q
uv run --no-sync python scripts/dev/validate_project.py docs
pwsh.exe -NoProfile -ExecutionPolicy Bypass -File "$env:USERPROFILE\.codex\hooks\codex-cleanup.ps1" -RepoRoot .
```
