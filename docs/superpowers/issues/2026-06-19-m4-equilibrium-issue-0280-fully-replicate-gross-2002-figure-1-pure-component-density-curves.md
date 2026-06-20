---
issue: 280
title: "M4: fully replicate Gross 2002 Figure 1 pure-component density curves"
url: "https://github.com/ePC-SAFT/ePC-SAFT/issues/280"
state: "open"
milestone: "M4 - Equilibrium"
project: "ePC-SAFT Roadmap"
package: "equilibrium"
capability: "association"
backend: "Ipopt"
readiness: "ready"
release_target: "equilibrium-0.x"
source_spec: "docs/superpowers/specs/2026-06-19-m4-equilibrium-gross-2002-full-figure-replication.md"
source_plan: "docs/superpowers/plans/2026-06-19-m4-equilibrium-issue-0280-gross-2002-figure-1-density-curves-plan.md"
afk_hitl: "AFK"
branch: codex/issue-0280-gross-2002-figure-1-density-curves
last_synced: "2026-06-19"
---
# M4: fully replicate Gross 2002 Figure 1 pure-component density curves

**GitHub Issue:** https://github.com/ePC-SAFT/ePC-SAFT/issues/280
**GitHub Milestone:** M4 - Equilibrium
**Issue Type:** Task
**Source Spec:** docs/superpowers/specs/2026-06-19-m4-equilibrium-gross-2002-full-figure-replication.md
**Source Plan:** docs/superpowers/plans/2026-06-19-m4-equilibrium-issue-0280-gross-2002-figure-1-density-curves-plan.md
**Classification:** AFK
**Labels:** status:ready, type:task, validation, equilibrium, area:equilibrium, backend:ipopt, native, docs
**Goal Command:** /goal Resolve this issue using docs/superpowers/plans/2026-06-19-m4-equilibrium-issue-0280-gross-2002-figure-1-density-curves-plan.md after https://github.com/ePC-SAFT/ePC-SAFT/issues/279 and https://github.com/ePC-SAFT/ePC-SAFT/issues/290 are closed. Complete proof oracle: Figure 1 pure-component saturated vapor/liquid density curves retained source data, native model curve from the #290 public route, paper-scale plot, score JSON, validation checker, docs validation, cleanup hook.
**Execution Mode:** Ask at runtime
**Worktree Policy:** Native Codex worktree thread first
**Integration Policy:** Worker PR reviewed by main thread
**TDD Policy:** Required
**Parallelization Plan:** None
**Reviewer Role:** Main thread orchestrator
**Script Gate Mode:** Safety only

## Project Merge

**Merge Owner:** Main thread orchestrator
**Merge Gate:** Native UI approval required
**Merge Policy:** Repo default
**Worktree Cleanup Policy:** Remove owned worktree after merge
**Orchestrator Wakeup Policy:** Worker handoff or bounded heartbeat

## What To Build

Upgrade Figure 1 from table-AAD sanity evidence to a paper-scale T-rho reproduction for methanol, 1-pentanol, and 1-nonanol.

## Outcome Summary

**Outcome Source:** docs/superpowers/plans/2026-06-19-m4-equilibrium-issue-0280-gross-2002-figure-1-density-curves-plan.md#outcome-contract
**Intent:** Convert Figure 1 from a diagnostic association-AAD mirror into source-backed curve-level paper replication.
**Target Output:** A reviewer can open the retained Figure 1 PNG/SVG and inspect source/model/score artifacts showing paper-scale T-rho vapor/liquid density replication for methanol, 1-pentanol, and 1-nonanol.
**Owner:** Gross/Sadowski 2002 Figure 1 source image, the #279 full-replication checker contract, and the #290 public route receipt.
**Interface:** `scripts/validation/check_gross_2002_full_replication.py` plus the #290 `epcsaft_equilibrium.Equilibrium(..., route="single_component_vle", T=...).solve()` prerequisite route.
**Cutover:** Figure 1 changes from `planned` to `accepted` only after all required source, model, score, plot, summary, and route-receipt artifacts pass the checker.
**Replaced Path:** Existing `gross_2002_figure_01_association_mirror_*` artifacts remain #275 evidence and cannot count as #280 full-replication artifacts.
**Acceptance Proof:** Passing proof oracle commands, rendered Figure 1 plot, branch score table, #290 route receipt, and no Figure 1 blockers in the full-replication checker readout.
**Stop Criteria:** Stop if #290 is not merged or if the merged route cannot produce certified native vapor/liquid density curves for all three alcohols.
**Avoid:** Do not relabel the #275 AAD mirror as full replication, use synthetic source points, lower #279 thresholds, claim electrolyte/reactive/generalized admission, or use a Python-owned production solver.

## Acceptance Criteria

- [ ] Retain or digitize coexisting vapor/liquid density source data with temperature and density units.
- [ ] Generate PC-SAFT saturated vapor and liquid density model curves for all three alcohols.
- [ ] Render a paper-scale T-rho mirror plot with source data and model curves.
- [ ] Write score JSON for vapor and liquid branches and require the Figure 1 score gate.
- [ ] Keep Figure 1 artifacts inside analyses/paper_validation/2002_gross/figures/figure_01.

## Blocked by

- None

## Non-goals

- No electrolyte, reactive, CE, CPE, or generalized phase-count admission.
- No detached validation mirror outside analyses/paper_validation/2002_gross.
- No completion credit for diagnostic-only or unscored plot evidence.

## Proof Oracle

- uv run --no-sync python scripts/dev/build_epcsaft.py --profile equilibrium --build-only --parallel 4
- uv run --no-sync python scripts/validation/check_gross_2002_full_replication.py --json --require-exact-association-hessian --require-fresh-native
- uv run --no-sync python scripts/validation/check_gross_2002_association_acceptance.py --json --require-complete --require-exact-association-hessian --require-fresh-native
- uv run --no-sync python run_pytest.py tests/native/contracts/test_gross_2002_full_replication_checker.py -q
- uv run --no-sync python scripts/dev/validate_project.py docs
- cleanup hook


## GitHub Body

The GitHub issue body mirrors this file and is authoritative for live comments, labels, milestone, dependency edges, issue type, and project fields.

