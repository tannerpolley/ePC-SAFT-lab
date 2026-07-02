---
issue: 417
title: "M4 Khudaida Fig. S3: reproduce 10 wt% NaCl supporting LLE panels with Figiel parameters"
url: "https://github.com/ePC-SAFT/ePC-SAFT/issues/417"
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
branch: codex/issue-0417-khudaida-figs3
last_synced: "2026-07-02"
---

# M4 Khudaida Fig. S3: reproduce 10 wt% NaCl supporting LLE panels with Figiel parameters

**GitHub Issue:** https://github.com/ePC-SAFT/ePC-SAFT/issues/417
**GitHub Milestone:** M4 - Equilibrium
**Issue Type:** Task
**Source Spec:** docs/superpowers/specs/2026-07-02-m4-khudaida-figure-replication-with-figiel-parameters.md
**Source Plan:** docs/superpowers/plans/2026-07-02-m4-khudaida-figure-replication-with-figiel-parameters-plan.md
**Classification:** AFK
**Labels:** enhancement, docs, validation, equilibrium, area:equilibrium, backend:ipopt, status:blocked, type:task
**Goal Command:** /goal Resolve issue #417 and reproduce Khudaida Figure S3 with Figiel 2025 parameters.
**Execution Mode:** Auto after #416 closes
**Worktree Policy:** Native Codex worktree thread first
**Integration Policy:** Worker PR reviewed by main thread
**TDD Policy:** Required
**Parallelization Plan:** None
**Reviewer Role:** Main thread orchestrator
**Script Gate Mode:** Safety plus proof oracle

## Outcome Summary

Reproduce `figure_12`, supporting Figure S3, for 10 wt% NaCl panels at 293.15,
303.15, and 313.15 K from 64 source points.

## Project Merge

**Merge Owner:** Main thread orchestrator
**Merge Gate:** Native UI approval required
**Merge Policy:** Repo default
**Worktree Cleanup Policy:** Remove owned worktree after merge
**Orchestrator Wakeup Policy:** Worker handoff or bounded heartbeat

## What To Build

Regenerate Figure S3 panel artifacts and public-route electrolyte LLE
diagnostics with Figiel 2025 parameter provenance.

## Acceptance Criteria

- [ ] Figure S3 source/model CSVs and plot artifacts regenerate for all panels.
- [ ] Accepted rows use the public electrolyte LLE route with Figiel 2025
  parameter provenance.
- [ ] Per-panel residual and exact-Hessian diagnostics are retained.
- [ ] Fit statistics include panel row counts, tolerance basis, AAD/RMSE/max
  error, and exact failed rows if any.

## Blocked By

- #416

## Blocking

- #405

## Non-goals

- No fitted parameters in M4.
- No private-native-only proof.
- No broad electrolyte capability claim beyond Figure S3 evidence.

## Proof Oracle

```powershell
uv run --no-sync python analyses\paper_validation\2026_khudaida\figures\figure_12\scripts\generate_data.py
uv run --no-sync python analyses\paper_validation\2026_khudaida\figures\figure_12\scripts\render_figure.py
uv run --no-sync python scripts\validation\check_khudaida_2026_figure_validation.py
uv run --no-sync python -m pytest packages\epcsaft-equilibrium\tests -k "khudaida and figure_12 and electrolyte" -q
pwsh.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\validate-plan-task-use-cases.ps1 -PlanPath docs/superpowers/plans/2026-07-02-m4-khudaida-figure-replication-with-figiel-parameters-plan.md
pwsh.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\validate-plan-outcome-proof.ps1 -PlanPath docs/superpowers/plans/2026-07-02-m4-khudaida-figure-replication-with-figiel-parameters-plan.md
```
