---
issue: 415
title: "M6 Khudaida Fig. 10: reproduce sigma-profile source figure with parameter provenance"
url: https://github.com/ePC-SAFT/ePC-SAFT/issues/415
state: open
milestone: "M6 - Validation"
project: "ePC-SAFT Roadmap"
package: benchmark
capability: electrolyte
backend: Ipopt
readiness: blocked
release_target: validation
source_spec: docs/superpowers/specs/2026-07-02-m6-khudaida-paper-validation-with-figiel-parameters.md
source_plan: docs/superpowers/plans/2026-07-02-m6-khudaida-paper-validation-with-figiel-parameters-plan.md
afk_hitl: AFK
branch: codex/issue-0415-khudaida-fig10
last_synced: "2026-07-02"
---

# M6 Khudaida Fig. 10: reproduce sigma-profile source figure with parameter provenance

**GitHub Issue:** https://github.com/ePC-SAFT/ePC-SAFT/issues/415
**GitHub Milestone:** M6 - Validation
**Issue Type:** Task
**Sub-Issue Role:** leaf
**Parent Issue:** https://github.com/ePC-SAFT/ePC-SAFT/issues/421
**Parent Mirror:** docs/superpowers/issues/2026-07-02-m6-validation-issue-0421-khudaida-2026-paper-validation-parent.md
**Source Spec:** docs/superpowers/specs/2026-07-02-m6-khudaida-paper-validation-with-figiel-parameters.md
**Source Plan:** docs/superpowers/plans/2026-07-02-m6-khudaida-paper-validation-with-figiel-parameters-plan.md
**AFK/HITL:** AFK
**Classification:** AFK
**Labels:** enhancement, docs, validation, equilibrium, area:equilibrium, area:benchmark, backend:ipopt, status:blocked, type:task
**Goal Command:** /goal Resolve issue #415 and reproduce Khudaida Figure 10 provenance artifacts.
**Execution Mode:** Auto, one child figure at a time under #421
**Worktree Policy:** Native Codex worktree thread first
**Integration Policy:** Worker PR reviewed by main thread
**TDD Policy:** Required
**Parallelization Plan:** None
**Reviewer Role:** Main thread orchestrator
**Script Gate Mode:** Safety plus proof oracle

## Outcome Summary

This issue is a child of #421, the M6 Khudaida 2026 paper-validation parent. It owns retained figure evidence and opens or blocks on M4/M5 follow-up issues only when validation proves solver or parameter defects.

Reproduce `figure_10` as a sigma-profile source/provenance figure. This is not
an HELD2 flash residual gate and must not be counted as LLE model evidence.

## Project Merge

**Merge Owner:** Main thread orchestrator
**Merge Gate:** Native UI approval required
**Merge Policy:** Repo default
**Worktree Cleanup Policy:** Remove owned worktree after merge
**Orchestrator Wakeup Policy:** Worker handoff or bounded heartbeat

## What To Build

Regenerate Figure 10 source/provenance artifacts and classify the figure
honestly in the checker.

## Acceptance Criteria

- [ ] Figure 10 source data and plot artifacts regenerate.
- [ ] The checker records Figure 10 as a source/sigma-profile provenance figure.
- [ ] Figure metadata explains why HELD2 residual diagnostics do not apply.
- [ ] Capability/docs wording is narrowed to the evidence retained.

## Blocked By

- #414

## Blocking

- #421
- #416

## Non-goals

- No HELD2 residual proof claim from Figure 10.
- No hidden parameter fitting inside M6 validation.
- No broad electrolyte capability claim beyond retained Figure 10 provenance evidence.

## Proof Oracle

```powershell
uv run --no-sync python analyses\paper_validation\2026_khudaida\figures\figure_10\scripts\generate_data.py
uv run --no-sync python analyses\paper_validation\2026_khudaida\figures\figure_10\scripts\render_figure.py
uv run --no-sync python scripts\validation\check_khudaida_2026_figure_validation.py
uv run --no-sync python -m pytest packages\epcsaft-equilibrium\tests -k "khudaida and figure_10" -q
uv run --no-sync python scripts/validate_plan_task_use_cases.py --plan-path docs/superpowers/plans/2026-07-02-m6-khudaida-paper-validation-with-figiel-parameters-plan.md
uv run --no-sync python scripts/validate_plan_outcome_proof.py --plan-path docs/superpowers/plans/2026-07-02-m6-khudaida-paper-validation-with-figiel-parameters-plan.md
```
