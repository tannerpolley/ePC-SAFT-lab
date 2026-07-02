---
issue: 405
title: "M4 Khudaida: reproduce all figures one by one with Figiel 2025 parameters"
url: "https://github.com/ePC-SAFT/ePC-SAFT/issues/405"
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
afk_hitl: "HITL"
branch: codex/issue-0405-khudaida-figure-replication
last_synced: "2026-07-02"
---

# M4 Khudaida: reproduce all figures one by one with Figiel 2025 parameters

**GitHub Issue:** https://github.com/ePC-SAFT/ePC-SAFT/issues/405
**GitHub Milestone:** M4 - Equilibrium
**Issue Type:** Task
**Source Spec:** docs/superpowers/specs/2026-07-02-m4-khudaida-figure-replication-with-figiel-parameters.md
**Source Plan:** docs/superpowers/plans/2026-07-02-m4-khudaida-figure-replication-with-figiel-parameters-plan.md
**Classification:** HITL
**Labels:** enhancement, docs, validation, equilibrium, area:equilibrium, backend:ipopt, status:blocked, type:task
**Goal Command:** None; tracking parent issue.
**Execution Mode:** Ask at runtime
**Worktree Policy:** Native Codex worktree thread first
**Integration Policy:** Worker PR reviewed by main thread
**TDD Policy:** Required
**Parallelization Plan:** None; child issues are intentionally chained one by one.
**Reviewer Role:** Main thread orchestrator
**Script Gate Mode:** Safety plus proof oracle

## Outcome Summary

Track the Khudaida 2026 figure-by-figure reproduction campaign as an M4
equilibrium validation tranche. This tranche first proves the retained Figiel
2025 ePC-SAFT parameters through the public route before treating M5 regression
as a blocker.

## Project Merge

**Merge Owner:** Main thread orchestrator
**Merge Gate:** Native UI approval required
**Merge Policy:** Repo default
**Worktree Cleanup Policy:** Remove owned worktree after merge
**Orchestrator Wakeup Policy:** Worker handoff or bounded heartbeat

## What To Build

Maintain the parent tracker for the Khudaida figure-by-figure reproduction
campaign and close it only after child issues #406 through #417 close with
retained evidence.

## Acceptance Criteria

- [ ] Figures 1-10 and supporting Figures S2/S3 close or stop with exact
  source-backed blockers in child issues #406-#417.
- [ ] Model-comparable figures use
  `analyses/paper_validation/2025_figiel/parameters` or retain row-equivalence
  evidence for any local copy.
- [ ] The Khudaida checker reports complete artifacts and complete model
  reproduction for the accepted figure set.
- [ ] Any figure that cannot pass retains exact failed rows, residuals,
  parameter provenance, and source comparison before any M5 follow-up.

## Blocked By

- #406
- #407
- #408
- #409
- #410
- #411
- #412
- #413
- #414
- #415
- #416
- #417

## Non-goals

- No M5 parameter fitting inside this M4 tracker.
- No private-native-only proof.
- No diagnostic-only success.
- No release or broad electrolyte capability claim from issue creation alone.

## Proof Oracle

```powershell
uv run --no-sync python analyses\paper_validation\2026_khudaida\scripts\run_all.py
uv run --no-sync python scripts\validation\check_khudaida_2026_figure_validation.py
uv run --no-sync python -m pytest packages\epcsaft-equilibrium\tests -k "khudaida and electrolyte and lle" -q
pwsh.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\validate-plan-task-use-cases.ps1 -PlanPath docs/superpowers/plans/2026-07-02-m4-khudaida-figure-replication-with-figiel-parameters-plan.md
pwsh.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\validate-plan-outcome-proof.ps1 -PlanPath docs/superpowers/plans/2026-07-02-m4-khudaida-figure-replication-with-figiel-parameters-plan.md
uv run --no-sync python scripts\dev\validate_project.py docs
```
