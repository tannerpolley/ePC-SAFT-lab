---
issue: 290
title: "M4: admit pure 2B associating single-component VLE prerequisite"
url: "https://github.com/ePC-SAFT/ePC-SAFT/issues/290"
state: "open"
milestone: "M4 - Equilibrium"
project: "ePC-SAFT Roadmap"
package: "equilibrium"
capability: "association"
backend: "Ipopt"
readiness: "ready"
release_target: "equilibrium-0.x"
source_spec: "docs/superpowers/specs/2026-06-19-m4-equilibrium-gross-2002-full-figure-replication.md"
source_plan: "docs/superpowers/plans/2026-06-19-m4-equilibrium-pure-2b-associating-single-component-vle-prerequisite-plan.md"
afk_hitl: "AFK"
branch: codex/issue-0290-pure-2b-associating-single-component-vle
last_synced: "2026-06-19"
---
# M4: admit pure 2B associating single-component VLE prerequisite

**GitHub Issue:** https://github.com/ePC-SAFT/ePC-SAFT/issues/290
**GitHub Milestone:** M4 - Equilibrium
**Issue Type:** Task
**Source Spec:** docs/superpowers/specs/2026-06-19-m4-equilibrium-gross-2002-full-figure-replication.md
**Source Plan:** docs/superpowers/plans/2026-06-19-m4-equilibrium-pure-2b-associating-single-component-vle-prerequisite-plan.md
**Classification:** AFK
**Labels:** status:ready, type:task, validation, equilibrium, area:equilibrium, backend:ipopt, native, docs
**Goal Command:** /goal Resolve this issue using docs/superpowers/plans/2026-06-19-m4-equilibrium-pure-2b-associating-single-component-vle-prerequisite-plan.md. Complete proof oracle: pure 2B associating single-component VLE public-route admission, exact association derivative metadata, focused route tests, native equilibrium build, cleanup hook.
**Execution Mode:** Ask at runtime
**Worktree Policy:** Native Codex worktree thread first
**Integration Policy:** Worker PR reviewed by main thread
**TDD Policy:** Required
**Parallelization Plan:** None
**Reviewer Role:** Main thread orchestrator
**Script Gate Mode:** Safety only

## Outcome Summary

**Outcome Source:** docs/superpowers/plans/2026-06-19-m4-equilibrium-pure-2b-associating-single-component-vle-prerequisite-plan.md#outcome-contract
**Intent:** Make the native package route capable of solving pure 2B associating saturated vapor/liquid states before Figure 1 replication consumes it.
**Target Output:** A reviewer can run the focused route tests and see native Ipopt vapor/liquid densities plus exact association derivative diagnostics for a Gross 2002 pure alcohol case.
**Owner:** `packages/epcsaft-equilibrium` public `single_component_vle` route, selector, activation metadata, and native route derivative diagnostics.
**Interface:** `epcsaft_equilibrium.Equilibrium(..., route="single_component_vle", T=...).solve()`.
**Cutover:** #280 remains blocked until this prerequisite merges; after merge, #280 should contain figure-replication artifacts rather than native admission code.
**Replaced Path:** The blanket associating-component rejection for one-component neutral 2B `single_component_vle` input.
**Acceptance Proof:** Focused API/native route tests, activation capability tests, native equilibrium build, and cleanup hook.
**Stop Criteria:** Stop and create a deeper derivative/route issue if this requires binary associating VLE, electrolyte, reactive, or generalized phase-set admission.
**Avoid:** Do not create Gross 2002 Figure 1 artifacts, lower checker thresholds, claim binary associating VLE, or use a Python-owned production solver.

## Project Merge

**Merge Owner:** Main thread orchestrator
**Merge Gate:** Native UI approval required
**Merge Policy:** Repo default
**Worktree Cleanup Policy:** Remove owned worktree after merge
**Orchestrator Wakeup Policy:** Worker handoff or bounded heartbeat

## What To Build

Admit only pure neutral 2B associating components through `single_component_vle` with exact association derivative evidence, preserving every broader associating/electrolyte/reactive/generalized guard.

## Acceptance Criteria

- [ ] Public `single_component_vle` accepts exactly one neutral 2B associating component.
- [ ] Public `single_component_vle` still rejects binary associating mixtures and out-of-scope ionic/reactive inputs.
- [ ] Native route diagnostics report exact association derivative/Hessian evidence for the accepted pure associating case.
- [ ] Existing nonassociating single-component VLE tests remain green.
- [ ] Capability and activation metadata describe the narrow pure 2B associating admission without broad association overclaiming.

## Blocked by

- None

## Non-goals

- No Gross 2002 Figure 1 source CSV, PNG, SVG, plot score, manifest acceptance, or campaign summary updates.
- No binary associating VLE admission.
- No electrolyte, reactive, LLLE, CE, CPE, or generalized associating phase-count admission.
- No regression package changes.

## Proof Oracle

- uv run --no-sync python scripts/dev/build_epcsaft.py --profile equilibrium --build-only --parallel 4
- uv run --no-sync python run_pytest.py packages/epcsaft-equilibrium/tests/api/test_single_component_vle.py packages/epcsaft-equilibrium/tests/contracts/test_activation_capabilities.py -q
- uv run --no-sync python run_pytest.py packages/epcsaft-equilibrium/tests/native/blocks/test_single_component_vle_block.py packages/epcsaft-equilibrium/tests/native/blocks/test_eos_phase_block.py -q
- pwsh.exe -NoProfile -ExecutionPolicy Bypass -File "$env:USERPROFILE\.codex\hooks\codex-cleanup.ps1" -RepoRoot .

## GitHub Body

The GitHub issue body mirrors this file and is authoritative for live comments, labels, milestone, dependency edges, issue type, and project fields.
