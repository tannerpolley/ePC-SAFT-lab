---
issue: 292
title: "M4: open associating GFPE VLE admission for Gross 2002 binaries"
url: https://github.com/ePC-SAFT/ePC-SAFT/issues/292
state: open
milestone: "M4 - Equilibrium"
project: "ePC-SAFT Roadmap"
package: equilibrium
capability: association
backend: Ipopt
readiness: ready
release_target: equilibrium-0.x
source_spec: docs/superpowers/specs/2026-06-19-m4-equilibrium-gross-2002-full-figure-replication.md
source_plan: docs/superpowers/plans/2026-06-20-m4-equilibrium-associating-vle-gfpe-admission-prerequisite-plan.md
afk_hitl: AFK
branch: codex/issue-0292-open-associating-gfpe-vle-admission-for-gross-2002-binaries
last_synced: "2026-06-20"
---

# M4: open associating GFPE VLE admission for Gross 2002 binaries

**GitHub Issue:** https://github.com/ePC-SAFT/ePC-SAFT/issues/292
**GitHub Milestone:** M4 - Equilibrium
**Issue Type:** Task
**Source Spec:** docs/superpowers/specs/2026-06-19-m4-equilibrium-gross-2002-full-figure-replication.md
**Source Plan:** docs/superpowers/plans/2026-06-20-m4-equilibrium-associating-vle-gfpe-admission-prerequisite-plan.md
**AFK/HITL:** AFK
**Classification:** AFK
**Labels:** agent-ready, status:ready, type:task, validation, equilibrium, area:equilibrium, backend:ipopt, native
**Goal Command:** /goal Resolve this issue using docs/superpowers/plans/2026-06-20-m4-equilibrium-associating-vle-gfpe-admission-prerequisite-plan.md. Complete proof oracle: public Gross 2002 Figures 2-9 associating binary VLE bubble/dew routes accepted with exact association-Hessian evidence, existing associating LLE proof preserved, broader unproven families still rejected, docs validation, cleanup hook.
**Execution Mode:** Ask at runtime
**Worktree Policy:** Native Codex worktree thread first
**Integration Policy:** Worker PR reviewed by main thread
**TDD Policy:** Required
**Parallelization Plan:** None
**Reviewer Role:** Main thread orchestrator
**Script Gate Mode:** Safety only

## Outcome Summary

**Outcome Source:** docs/superpowers/plans/2026-06-20-m4-equilibrium-associating-vle-gfpe-admission-prerequisite-plan.md#outcome-contract
**Intent:** Permit source-backed neutral associating binary VLE route solves needed by Gross/Sadowski 2002 Figures 2-9.
**Target Output:** The Figure 2-9 replication workers can generate model CSVs through public equilibrium routes.
**Owner:** `packages/epcsaft-equilibrium` selector/admission and native GFPE route metadata.
**Interface:** Public `epcsaft_equilibrium.Equilibrium(...).solve()` bubble/dew workflows with exact association-Hessian receipts.
**Cutover:** Replace the current VLE admission rejection for source-backed Gross 2002 associating binaries with explicit admissible route cases.
**Replaced Path:** The #281, #282, #283, and #284 blocker paths where public VLE routes reject source-backed Gross/Sadowski 2002 associating VLE before model generation.
**Acceptance Proof:** Focused tests and validation probes show accepted Gross 2002 associating binary VLE solves expose exact derivative evidence and unproven broader families still reject.
**Stop Criteria:** Stop if implementation cannot be narrowed to source-backed neutral associating binary VLE without broader generalized family exposure.
**Avoid:** Do not add Gross 2002 figure artifacts, electrolyte/reactive admission, generalized phase-count claims, approximate derivative acceptance, or weakened diagnostics.

## Project Merge

**Merge Owner:** Main thread orchestrator
**Merge Gate:** Native UI approval required
**Merge Policy:** Repo default
**Worktree Cleanup Policy:** Remove owned worktree after merge
**Orchestrator Wakeup Policy:** Worker handoff or bounded heartbeat

## What To Build

Open the narrow production admission path that lets source-backed neutral associating binary VLE cases from Gross/Sadowski 2002 Figures 2-9 enter public `bubble_pressure` and `dew_pressure` workflows with exact association-Hessian evidence.

## Acceptance Criteria

- [ ] Add a failing public-route test that reproduces the current VLE rejection for representative Gross/Sadowski 2002 Figure 2 methanol/isobutane, Figure 6 1-butanol/n-butane, Figure 8 methanol/cyclohexane, and Figure 9 methanol/1-octanol associating binaries.
- [ ] Admit only source-backed neutral associating binary VLE cases needed by Gross/Sadowski 2002 Figures 2-9.
- [ ] Preserve explicit rejection for unproven broader associating, electrolyte, reactive, CE, CPE, and generalized phase-count cases.
- [ ] Assert exact association-Hessian receipt metadata on accepted associating VLE route results.
- [ ] Preserve the existing Gross/Sadowski 2002 associating LLE proof.
- [ ] Leave Gross 2002 Figure 2-9 source, plot, score, and model-artifact generation to #281, #282, #283, and #284.

## Blocked by

- None

## Blocks

- https://github.com/ePC-SAFT/ePC-SAFT/issues/281
- https://github.com/ePC-SAFT/ePC-SAFT/issues/282
- https://github.com/ePC-SAFT/ePC-SAFT/issues/283
- https://github.com/ePC-SAFT/ePC-SAFT/issues/284

## Non-goals

- No Gross 2002 figure digitization, plotting, or score artifacts.
- No electrolyte, reactive, CE, CPE, or generalized phase-count admission.
- No broad associating-family capability claim.
- No lowering of exact-derivative or source-provenance gates.

## Proof Oracle

```powershell
uv run --no-sync python scripts/dev/build_epcsaft.py --profile equilibrium --build-only --parallel 4
uv run --no-sync python run_pytest.py <focused-associating-vle-route-test> -q
uv run --no-sync python scripts/validation/check_gross_2002_association_acceptance.py --json --require-exact-association-hessian --require-fresh-native
uv run --no-sync python scripts/dev/validate_project.py docs
pwsh.exe -NoProfile -ExecutionPolicy Bypass -File "$env:USERPROFILE\.codex\hooks\codex-cleanup.ps1" -RepoRoot .
```

## GitHub Body

The GitHub issue body mirrors this file and is authoritative for live comments, labels, milestone, dependency edges, issue type, and project fields.
