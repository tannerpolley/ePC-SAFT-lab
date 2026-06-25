---
issue: 312
title: "M4: add electrolyte HELD2 Stage III reduced-variable refinement gate"
url: "https://github.com/ePC-SAFT/ePC-SAFT/issues/312"
state: "open"
milestone: "M4 - Equilibrium"
project: "ePC-SAFT Roadmap"
package: "equilibrium"
capability: "electrolyte"
backend: "Ipopt"
readiness: "ready"
release_target: "equilibrium-0.x"
source_spec: "docs/superpowers/specs/2026-05-30-m4-equilibrium-issue-0191-prove-electrolyte-gfpe-and-held2-0-validation-gates.md"
source_plan: "docs/superpowers/plans/2026-06-25-m4-equilibrium-issue-0312-electrolyte-held2-stage-iii-refinement-gate-plan.md"
afk_hitl: "AFK"
branch: codex/issue-0312-electrolyte-stage-iii-refinement
last_synced: "2026-06-25"
---

# M4: add electrolyte HELD2 Stage III reduced-variable refinement gate

**GitHub Issue:** https://github.com/ePC-SAFT/ePC-SAFT/issues/312
**GitHub Milestone:** M4 - Equilibrium
**Issue Type:** Feature
**Source Spec:** docs/superpowers/specs/2026-05-30-m4-equilibrium-issue-0191-prove-electrolyte-gfpe-and-held2-0-validation-gates.md
**Source Plan:** docs/superpowers/plans/2026-06-25-m4-equilibrium-issue-0312-electrolyte-held2-stage-iii-refinement-gate-plan.md
**Classification:** AFK
**Labels:** enhancement, agent-ready, native, solver, docs, validation, equilibrium, area:equilibrium, backend:ipopt, status:ready, type:feature
**Goal Command:** /goal Resolve https://github.com/ePC-SAFT/ePC-SAFT/issues/312 using docs/superpowers/issues/2026-06-25-m4-equilibrium-issue-0312-add-electrolyte-held2-stage-iii-reduced-variable-refinement-gate.md and docs/superpowers/plans/2026-06-25-m4-equilibrium-issue-0312-electrolyte-held2-stage-iii-refinement-gate-plan.md. Complete proof oracle: issue acceptance criteria checked and PR merged.
**Execution Mode:** Ask at runtime
**Worktree Policy:** Native Codex worktree thread first
**Integration Policy:** Worker PR reviewed by main thread
**TDD Policy:** Required
**Parallelization Plan:** None
**Reviewer Role:** Main thread orchestrator
**Script Gate Mode:** Safety only

## Outcome Summary

**Outcome Source:** docs/superpowers/plans/2026-06-25-m4-equilibrium-issue-0312-electrolyte-held2-stage-iii-refinement-gate-plan.md#outcome-proof
**Intent:** Convert the #306 HELD2 counterion-pair candidate handoff into a strict Stage III electrolyte reduced-variable refinement proof.
**Target Output:** `scripts/validation/check_electrolyte_stage_iii_refinement.py --json --require-source-gate --require-readiness-gate --require-tpd-gate --require-held2-discovery --require-native-stage-iii --require-public-routes-closed --require-complete` returns `complete: true`.
**Owner:** M4 equilibrium package owner.
**Interface:** Native reduced-variable Stage III diagnostic, retained checker JSON, pytest contracts, M4 issue mirror, registry row, and M4 README.
**Cutover:** This checker becomes the #312 proof oracle; #191 remains blocked by #312/#313/#314 until the child sequence closes.
**Replaced Path:** HELD2 phase-discovery candidate evidence remains prerequisite evidence and no longer stands in for a refined electrolyte phase-set solve.
**Acceptance Proof:** Acceptance is proven when the retained checker consumes #269/#300/#302/#306, reports exact reduced residual Jacobian/Hessian evidence, strict solver success, bounded finite phase compositions, no phase collapse, and explicit pending postsolve/admission gates.
**Stop Criteria:** Stop if the reduced residual equations cannot be stated, if raw single-ion equality appears as acceptance evidence, if Ipopt success is used without physical diagnostics, or if public route admission is needed to satisfy this gate.
**Avoid:** Do not add postsolve certification, public electrolyte routes, reactive routes, regression work, downstream study logic, or release claims.

## Project Merge

**Merge Owner:** Main thread orchestrator
**Merge Gate:** Native UI approval required
**Merge Policy:** Repo default
**Worktree Cleanup Policy:** Remove owned worktree after merge
**Orchestrator Wakeup Policy:** Worker handoff or bounded heartbeat

## What To Build

Add the next #191 child gate: consume the #306 reduced-coordinate candidate set
and solve the electrolyte phase-set equations in reduced electroneutral
variables. The proof must retain exact Jacobian/Hessian evidence for the
reduced residual system, solver diagnostics, selected candidate provenance, and
explicit blockers showing that postsolve certification and public route
admission are still separate.

## Parent And Dependencies

- Parent issue: https://github.com/ePC-SAFT/ePC-SAFT/issues/191
- Blocks: https://github.com/ePC-SAFT/ePC-SAFT/issues/191 and https://github.com/ePC-SAFT/ePC-SAFT/issues/313
- Blocked by: None.
- Prerequisite evidence consumed: #269, #300, #302, and #306.

## Acceptance Criteria

- [ ] The checker consumes #269, #300, #302, and #306 evidence.
- [ ] Stage III refinement consumes the #306 candidate set without regenerating unproven candidates.
- [ ] The reduced electroneutral residual system reports variables, equations, scaling, bounds, seed provenance, and selected phase labels.
- [ ] Exact reduced residual Jacobian and Hessian receipts are retained.
- [ ] Solver diagnostics report Ipopt status, application status, residual norms, active-bound diagnostics, and finite phase compositions.
- [ ] Negative tests reject missing prerequisites, raw single-ion equality, phase-collapsed solutions, and premature postsolve/public-admission status.
- [ ] Capabilities and registry evidence keep public electrolyte routes closed.
- [ ] #191 and the M4 README name #313 and #314 as the remaining gates after this issue closes.

## Blocked by

- None. Prerequisite evidence #269, #300, #302, and #306 is closed.

## Non-Goals

- No public electrolyte route admission.
- No postsolve certification cutover.
- No reactive, CE, CPE, regression, downstream, release, or publication claim.

## Proof Oracle

```powershell
pwsh.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\validate-plan-task-use-cases.ps1 -PlanPath docs\superpowers\plans\2026-06-25-m4-equilibrium-issue-0312-electrolyte-held2-stage-iii-refinement-gate-plan.md
pwsh.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\validate-plan-outcome-proof.ps1 -PlanPath docs\superpowers\plans\2026-06-25-m4-equilibrium-issue-0312-electrolyte-held2-stage-iii-refinement-gate-plan.md
uv run --no-sync python scripts/validation/check_electrolyte_stage_iii_refinement.py --json --require-source-gate --require-readiness-gate --require-tpd-gate --require-held2-discovery --require-native-stage-iii --require-public-routes-closed --require-complete
uv run --no-sync python run_pytest.py tests/native/contracts/test_electrolyte_stage_iii_refinement.py tests/native/contracts/test_electrolyte_held2_phase_discovery.py packages/epcsaft-equilibrium/tests/contracts/test_activation_capabilities.py tests/native/contracts/test_generalized_equilibrium_registry.py -q
uv run --no-sync python scripts/dev/validate_project.py docs
pwsh.exe -NoProfile -ExecutionPolicy Bypass -File "$env:USERPROFILE\.codex\hooks\codex-cleanup.ps1" -RepoRoot .
```
