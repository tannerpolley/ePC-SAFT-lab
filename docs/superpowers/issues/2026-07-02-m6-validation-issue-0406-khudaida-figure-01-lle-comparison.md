---
issue: 406
title: "M6 Khudaida Fig. 1: reproduce salt-free and salted LLE comparison with Figiel parameters"
url: https://github.com/ePC-SAFT/ePC-SAFT/issues/406
state: closed
milestone: "M6 - Validation"
project: "ePC-SAFT Roadmap"
package: benchmark
capability: electrolyte
backend: Ipopt
readiness: closed
release_target: validation
source_spec: null
source_plan: null
afk_hitl: AFK
branch: null
last_synced: "2026-07-02"
---

# M6 Khudaida Fig. 1: reproduce salt-free and salted LLE comparison with Figiel parameters

**GitHub Issue:** https://github.com/ePC-SAFT/ePC-SAFT/issues/406
**GitHub Milestone:** M6 - Validation
**Issue Type:** Task
**Sub-Issue Role:** leaf
**Parent Issue:** https://github.com/ePC-SAFT/ePC-SAFT/issues/421
**Parent Mirror:** docs/superpowers/issues/2026-07-02-m6-validation-issue-0421-khudaida-2026-paper-validation-parent.md
**Source Spec:** docs/superpowers/specs/2026-07-02-m6-khudaida-paper-validation-with-figiel-parameters.md
**Source Plan:** docs/superpowers/plans/2026-07-02-m6-khudaida-paper-validation-with-figiel-parameters-plan.md
**AFK/HITL:** AFK
**Classification:** AFK
**Mirror Retention:** Keep
**Labels:** enhancement, agent-ready, docs, validation, equilibrium, area:equilibrium, area:benchmark, backend:ipopt, status:ready, type:task
**Goal Command:** /goal Resolve issue #406 and reproduce Khudaida Figure 1 with Figiel 2025 parameters.
**Execution Mode:** Auto, one child figure at a time under #421
**Worktree Policy:** Native Codex worktree thread first
**Integration Policy:** Worker PR reviewed by main thread
**TDD Policy:** Required
**Parallelization Plan:** None
**Reviewer Role:** Main thread orchestrator
**Script Gate Mode:** Safety plus proof oracle

## Outcome Summary

This issue is a child of #421, the M6 Khudaida 2026 paper-validation parent. It owns retained figure evidence and opens or blocks on M4/M5 follow-up issues only when validation proves solver or parameter defects.

Reproduce `figure_01` at 293.15 K for salt-free, 5 wt% NaCl, and 10 wt% NaCl
LLE comparison as a source-only salt-effect figure. The source text/caption has
no ePC-SAFT model curve for Figure 1; public electrolyte LLE route evidence
starts with model-comparable Figures 2-7 and S2-S3.

## Project Merge

**Merge Owner:** Main thread orchestrator
**Merge Gate:** Native UI approval required
**Merge Policy:** Repo default
**Worktree Cleanup Policy:** Remove owned worktree after merge
**Orchestrator Wakeup Policy:** Worker handoff or bounded heartbeat

## What To Build

Regenerate Figure 1 source/recreation artifacts and retained statistics while
recording the Figiel 2025 parameter boundary honestly for this source-only
figure.

## Acceptance Criteria

- [ ] `analyses/paper_validation/2026_khudaida/figures/figure_01` regenerates
  retained source/model CSVs and plot artifacts.
- [ ] Source rows and retained recreation rows are nonzero.
- [ ] Figure 1 records that Figiel 2025 fitted-parameter use is outside this
  source-only figure and starts with model-comparable figures.
- [ ] Fit statistics include row counts, tolerance basis, errors, and exact
  failed rows if any.

## Blocked By

- None.

## Blocking

- #421
- #407

## Non-goals

- No hidden parameter fitting inside M6 validation.
- No private-native-only proof.
- No broad electrolyte capability claim beyond retained Figure 1 evidence.
- No public-route model-fit claim for Figure 1, because the paper caption does
  not contain an ePC-SAFT curve for that figure.

## Proof Oracle

```powershell
uv run --no-sync python analyses\paper_validation\2026_khudaida\figures\figure_01\scripts\generate_data.py
uv run --no-sync python analyses\paper_validation\2026_khudaida\figures\figure_01\scripts\render_figure.py
uv run --no-sync python scripts\validation\check_khudaida_2026_figure_validation.py
uv run --no-sync python -m pytest packages\epcsaft-equilibrium\tests -k "khudaida and figure_01 and electrolyte" -q
uv run --no-sync python scripts/validate_plan_task_use_cases.py --plan-path docs/superpowers/plans/2026-07-02-m6-khudaida-paper-validation-with-figiel-parameters-plan.md
uv run --no-sync python scripts/validate_plan_outcome_proof.py --plan-path docs/superpowers/plans/2026-07-02-m6-khudaida-paper-validation-with-figiel-parameters-plan.md
```
