---
issue: 413
title: "M4 Khudaida Fig. 8: reproduce separation-factor metric with Figiel parameters"
url: "https://github.com/ePC-SAFT/ePC-SAFT/issues/413"
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
branch: codex/issue-0413-khudaida-fig08
last_synced: "2026-07-02"
---

# M4 Khudaida Fig. 8: reproduce separation-factor metric with Figiel parameters

**GitHub Issue:** https://github.com/ePC-SAFT/ePC-SAFT/issues/413
**GitHub Milestone:** M4 - Equilibrium
**Issue Type:** Task
**Source Spec:** docs/superpowers/specs/2026-07-02-m4-khudaida-figure-replication-with-figiel-parameters.md
**Source Plan:** docs/superpowers/plans/2026-07-02-m4-khudaida-figure-replication-with-figiel-parameters-plan.md
**Classification:** AFK
**Labels:** enhancement, docs, validation, equilibrium, area:equilibrium, backend:ipopt, status:blocked, type:task
**Goal Command:** /goal Resolve issue #413 and reproduce Khudaida Figure 8 with Figiel 2025 parameters.
**Execution Mode:** Auto after #412 closes
**Worktree Policy:** Native Codex worktree thread first
**Integration Policy:** Worker PR reviewed by main thread
**TDD Policy:** Required
**Parallelization Plan:** None
**Reviewer Role:** Main thread orchestrator
**Script Gate Mode:** Safety plus proof oracle

## Outcome Summary

Reproduce `figure_08`, the separation factor of water over ethanol for
293.15-313.15 K and 0, 5, and 10 wt% NaCl. Current retained evidence has 47
source points and zero model rows.

## Project Merge

**Merge Owner:** Main thread orchestrator
**Merge Gate:** Native UI approval required
**Merge Policy:** Repo default
**Worktree Cleanup Policy:** Remove owned worktree after merge
**Orchestrator Wakeup Policy:** Worker handoff or bounded heartbeat

## What To Build

Regenerate Figure 8 metric artifacts from reproduced phase compositions with
Figiel 2025 parameter provenance.

## Acceptance Criteria

- [ ] Figure 8 source/model CSVs and plot artifacts regenerate.
- [ ] Separation factors are computed from reproduced phase compositions.
- [ ] Metric statistics include row counts, tolerance basis, AAD/RMSE/max
  error, Figiel provenance, and exact failed rows if any.

## Blocked By

- #412

## Blocking

- #405
- #414

## Non-goals

- No source-only metric success.
- No fitted parameters in M4.
- No broad electrolyte capability claim beyond Figure 8 evidence.

## Proof Oracle

```powershell
uv run --no-sync python analyses\paper_validation\2026_khudaida\figures\figure_08\scripts\generate_data.py
uv run --no-sync python analyses\paper_validation\2026_khudaida\figures\figure_08\scripts\render_figure.py
uv run --no-sync python scripts\validation\check_khudaida_2026_figure_validation.py
uv run --no-sync python -m pytest packages\epcsaft-equilibrium\tests -k "khudaida and figure_08 and electrolyte" -q
pwsh.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\validate-plan-task-use-cases.ps1 -PlanPath docs/superpowers/plans/2026-07-02-m4-khudaida-figure-replication-with-figiel-parameters-plan.md
pwsh.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\validate-plan-outcome-proof.ps1 -PlanPath docs/superpowers/plans/2026-07-02-m4-khudaida-figure-replication-with-figiel-parameters-plan.md
```
