---
issue: 298
title: "M4: add internal adaptive branch tracing for boundary-route validation"
url: "https://github.com/ePC-SAFT/ePC-SAFT/issues/298"
state: "open"
milestone: "M4 - Equilibrium"
project: "ePC-SAFT Roadmap"
package: "equilibrium"
capability: "association"
backend: "Ipopt"
readiness: "ready"
release_target: "equilibrium-0.x"
source_spec: "docs/superpowers/specs/2026-06-24-m4-equilibrium-adaptive-branch-tracing-and-validation.md"
source_plan: "docs/superpowers/plans/2026-06-24-m4-equilibrium-adaptive-branch-tracing-validation-plan.md"
afk_hitl: "AFK"
branch: codex/fix-gross-2002-figure-02-bubble-line
last_synced: "2026-06-24"
---

# M4: add internal adaptive branch tracing for boundary-route validation

**GitHub Issue:** https://github.com/ePC-SAFT/ePC-SAFT/issues/298
**GitHub Milestone:** M4 - Equilibrium
**Issue Type:** Task
**Source Spec:** docs/superpowers/specs/2026-06-24-m4-equilibrium-adaptive-branch-tracing-and-validation.md
**Source Plan:** docs/superpowers/plans/2026-06-24-m4-equilibrium-adaptive-branch-tracing-validation-plan.md
**AFK/HITL:** AFK
**Classification:** AFK
**Labels:** agent-ready, status:ready, type:task, validation, equilibrium, area:equilibrium, backend:ipopt, solver
**Goal Command:** /goal Resolve this issue using docs/superpowers/plans/2026-06-24-m4-equilibrium-adaptive-branch-tracing-validation-plan.md. Complete proof oracle: internal adaptive branch tracer, Figure 2 trace cutover, checker trace gate, regenerated Figure 2 artifacts, full Gross 2002 checker, docs validation, cleanup hook.
**Execution Mode:** Direct current-thread Auto Mode
**Worktree Policy:** Current Codex branch because user explicitly requested this branch be merged
**Integration Policy:** Current thread owns PR and merge
**TDD Policy:** Required
**Parallelization Plan:** None
**Reviewer Role:** Main thread orchestrator
**Script Gate Mode:** Safety only

## Outcome Summary

**Outcome Source:** docs/superpowers/plans/2026-06-24-m4-equilibrium-adaptive-branch-tracing-validation-plan.md#outcome-proof
**Intent:** Add reusable internal branch tracing so boundary-route validation proves solved branch density, required source-anchor solves, exact-Hessian receipts, and postsolve receipts before a paper-validation curve can count as accepted.
**Target Output:** `scripts/validation/check_gross_2002_full_replication.py --json --require-complete --require-exact-association-hessian --require-fresh-native` exits `0` only when Figure 2 has accepted branch trace summaries for `bubble_line` and `dew_line` plus solved model rows behind the rendered `figure_02.png`, `figure_02.svg`, and `figure_02.pdf`.
**Owner:** `packages/epcsaft-equilibrium` owns the reusable branch tracer; `analyses/paper_validation/2002_gross/figures/figure_02` owns Figure 2 source/model/plot artifacts; `scripts/validation/check_gross_2002_full_replication.py` owns campaign admission.
**Interface:** Internal module `epcsaft_equilibrium.branch_tracing` with explicit trace data objects and `trace_boundary_route(...)`; Figure 2 consumes that module and writes `trace_summary.json`; the checker reads manifest fields `requires_branch_trace`, `trace_requirements`, and artifact `trace_summary_json`.
**Cutover:** Replace Figure 2's figure-local `_solve_route_point(...)` and `_solve_series(...)` route loop with the shared tracer while keeping Figure 2 source acquisition, scoring, rendering, and manifest update ownership in the figure script.
**Replaced Path:** The old path where a figure-local loop could produce sparse model rows and rely on renderer smoothing is displaced by trace completeness gates and shared package branch tracing.
**Acceptance Proof:** A reviewer can inspect the Figure 2 trace summary and see both required series complete, every required anchor solved, maximum coordinate gap `<= 0.075`, maximum pressure interpolation error `<= 0.35 bar`, exact-Hessian and postsolve status true for every accepted trace point, and no checker blockers.
**Stop Criteria:** Stop if the native point route cannot solve a required Figure 2 anchor exactly, if accepted points do not expose exact-Hessian or postsolve receipts, if trace completeness requires broad native continuation work, or if branch tracing cannot remain internal without public API claims.
**Avoid:** Do not add electrolyte, reactive, CE, CPE, generalized phase-count, HELD Stage I/II, public branch-tracing API, Gross-specific native C++ code, hidden coordinate substitution, or acceptance credit based only on interpolation.

## Project Merge

**Merge Owner:** Main thread orchestrator
**Merge Gate:** Auto Mode preauthorized after clean premerge
**Merge Policy:** Repo default
**Worktree Cleanup Policy:** Remove owned worktree after merge; current checkout has no linked worktree
**Orchestrator Wakeup Policy:** Bounded current-thread execution

## What To Build

Add the internal adaptive branch-tracing primitive, require retained branch
trace evidence in the Gross 2002 full-replication checker, and cut Figure 2
generation over to the shared tracer.

## Acceptance Criteria

- [ ] Add `epcsaft_equilibrium.branch_tracing` with explicit branch trace data objects and input validation.
- [ ] Implement adaptive branch refinement that solves required anchors first, carries continuation state, rejects coordinate drift, and reports incomplete traces loudly.
- [ ] Add an internal equilibrium point-solve adapter for bubble/dew boundary routes without exporting a public API.
- [ ] Require retained trace completeness for accepted Figure 2 records in the full-replication checker.
- [ ] Replace Figure 2's figure-local route loop with the shared tracer and write `trace_summary.json`.
- [ ] Regenerate Figure 2 artifacts and preserve exact-Hessian, postsolve, score, and full-campaign checker evidence.
- [ ] Update M4 evidence docs and pass the plan proof oracle.

## Blocked by

- None

## Non-goals

- No public `EquilibriumTrace` or `Equilibrium(...).trace()` API.
- No native continuation, tangent, arclength, HELD Stage I/II, or phase-discovery implementation.
- No electrolyte, reactive, CE, CPE, generalized phase-count, or broad capability claims.
- No plot score threshold reduction.

## Proof Oracle

```powershell
pwsh.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\validate-plan-outcome-proof.ps1 -PlanPath docs/superpowers/plans/2026-06-24-m4-equilibrium-adaptive-branch-tracing-validation-plan.md
pwsh.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\validate-plan-task-use-cases.ps1 -PlanPath docs/superpowers/plans/2026-06-24-m4-equilibrium-adaptive-branch-tracing-validation-plan.md
uv run --no-sync python scripts/dev/build_epcsaft.py --profile equilibrium --build-only --parallel 4
uv run --no-sync python run_pytest.py packages/epcsaft-equilibrium/tests/api/test_branch_tracing.py tests/native/contracts/test_gross_2002_full_replication_checker.py -q
uv run --no-sync python analyses/paper_validation/2002_gross/figures/figure_02/scripts/generate_data.py
uv run --no-sync python analyses/paper_validation/scripts/check_figure_contract.py analyses/paper_validation/2002_gross/figures/figure_02
uv run --no-sync python scripts/validation/check_gross_2002_full_replication.py --json --require-complete --require-exact-association-hessian --require-fresh-native --write-summary
uv run --no-sync python scripts/dev/validate_project.py docs
git diff --check
pwsh.exe -NoProfile -ExecutionPolicy Bypass -File "$env:USERPROFILE\.codex\hooks\codex-cleanup.ps1" -RepoRoot .
```

## GitHub Body

The GitHub issue body mirrors this file and is authoritative for live comments,
labels, milestone, dependency edges, issue type, and project fields.
