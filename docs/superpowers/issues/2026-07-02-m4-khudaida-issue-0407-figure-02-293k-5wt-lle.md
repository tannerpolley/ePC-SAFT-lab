---
issue: 407
title: "M4 Khudaida Fig. 2: reproduce 293.15 K 5 wt% NaCl LLE with Figiel parameters"
url: "https://github.com/ePC-SAFT/ePC-SAFT/issues/407"
state: "open"
milestone: "M4 - Equilibrium"
project: "ePC-SAFT Roadmap"
package: "equilibrium"
capability: "electrolyte"
backend: "Ipopt"
readiness: "blocked"
release_target: "equilibrium-0.x"
source_spec: "docs/superpowers/specs/2026-07-02-m4-khudaida-figure-replication-with-figiel-parameters.md"
source_plan: "docs/superpowers/plans/2026-07-02-m4-khudaida-figure-replication-with-figiel-parameters-plan.md"
afk_hitl: "AFK"
branch: codex/issue-0407-khudaida-fig02
last_synced: "2026-07-02"
---

# M4 Khudaida Fig. 2: reproduce 293.15 K 5 wt% NaCl LLE with Figiel parameters

**GitHub Issue:** https://github.com/ePC-SAFT/ePC-SAFT/issues/407
**GitHub Milestone:** M4 - Equilibrium
**Issue Type:** Task
**Source Spec:** docs/superpowers/specs/2026-07-02-m4-khudaida-figure-replication-with-figiel-parameters.md
**Source Plan:** docs/superpowers/plans/2026-07-02-m4-khudaida-figure-replication-with-figiel-parameters-plan.md
**Classification:** AFK
**Labels:** enhancement, docs, validation, equilibrium, area:equilibrium, backend:ipopt, status:blocked, type:task
**Goal Command:** /goal Resolve issue #407 and reproduce Khudaida Figure 2 with Figiel 2025 parameters.
**Execution Mode:** Auto after #406 closes
**Worktree Policy:** Native Codex worktree thread first
**Integration Policy:** Worker PR reviewed by main thread
**TDD Policy:** Required
**Parallelization Plan:** None
**Reviewer Role:** Main thread orchestrator
**Script Gate Mode:** Safety plus proof oracle

## Outcome Summary

Reproduce `figure_02` at 293.15 K and 5 wt% NaCl from 32 source points, 8 paper
ePC-SAFT points, and 8 feed rows. Current retained evidence accepts only 2
model rows, so this issue must close the figure-specific gap with Figiel 2025
parameter provenance.

## Project Merge

**Merge Owner:** Main thread orchestrator
**Merge Gate:** Native UI approval required
**Merge Policy:** Repo default
**Worktree Cleanup Policy:** Remove owned worktree after merge
**Orchestrator Wakeup Policy:** Worker handoff or bounded heartbeat

## What To Build

Regenerate Figure 2 source/model artifacts, retained statistics, and
public-route electrolyte LLE diagnostics through the Figiel 2025 parameter path.

## Acceptance Criteria

- [ ] Figure 2 source/model CSVs and plot artifacts regenerate.
- [ ] Accepted rows use the public electrolyte LLE route.
- [ ] Per-row diagnostics retain material balance, pressure, phase charge,
  lift/back-lift, neutral transfer, mean-ionic transfer, phase distance,
  exact-Hessian, and Ipopt route receipts.
- [ ] Fit statistics include row counts, tolerance basis, AAD/RMSE/max error,
  and exact failed rows if any.

## Blocked By

- #406

## Blocking

- #405
- #408

## Non-goals

- No fitted parameters in M4.
- No private-native-only proof.
- No broad electrolyte capability claim beyond Figure 2 evidence.

## Proof Oracle

```powershell
uv run --no-sync python analyses\paper_validation\2026_khudaida\figures\figure_02\scripts\generate_data.py
uv run --no-sync python analyses\paper_validation\2026_khudaida\figures\figure_02\scripts\render_figure.py
uv run --no-sync python scripts\validation\check_khudaida_2026_figure_validation.py
uv run --no-sync python -m pytest packages\epcsaft-equilibrium\tests -k "khudaida and figure_02 and electrolyte" -q
pwsh.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\validate-plan-task-use-cases.ps1 -PlanPath docs/superpowers/plans/2026-07-02-m4-khudaida-figure-replication-with-figiel-parameters-plan.md
pwsh.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\validate-plan-outcome-proof.ps1 -PlanPath docs/superpowers/plans/2026-07-02-m4-khudaida-figure-replication-with-figiel-parameters-plan.md
```
