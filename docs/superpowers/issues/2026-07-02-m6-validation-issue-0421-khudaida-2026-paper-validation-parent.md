---
issue: 421
title: "M6 Khudaida 2026 paper validation with Figiel parameter provenance"
url: https://github.com/ePC-SAFT/ePC-SAFT/issues/421
state: open
milestone: "M6 - Validation"
project: "ePC-SAFT Roadmap"
package: benchmark
capability: electrolyte
backend: Ipopt
readiness: ready
release_target: validation
source_spec: docs/superpowers/specs/2026-07-02-m6-khudaida-paper-validation-with-figiel-parameters.md
source_plan: docs/superpowers/plans/2026-07-02-m6-khudaida-paper-validation-with-figiel-parameters-plan.md
afk_hitl: AFK
branch: codex/issue-0421-khudaida-2026-paper-validation-parent
last_synced: "2026-07-10"
---

# M6 Khudaida 2026 paper validation with Figiel parameter provenance

**GitHub Issue:** https://github.com/ePC-SAFT/ePC-SAFT/issues/421
**GitHub Milestone:** M6 - Validation
**Issue Type:** Task
**Sub-Issue Role:** plan-wrapper
**Parent Issue:** https://github.com/ePC-SAFT/ePC-SAFT/issues/420
**Parent Mirror:** docs/superpowers/issues/2026-07-02-m6-validation-issue-0420-m6-paper-validation-campaign-parent.md
**Child Issues:** https://github.com/ePC-SAFT/ePC-SAFT/issues/406, https://github.com/ePC-SAFT/ePC-SAFT/issues/407, https://github.com/ePC-SAFT/ePC-SAFT/issues/408, https://github.com/ePC-SAFT/ePC-SAFT/issues/409, https://github.com/ePC-SAFT/ePC-SAFT/issues/410, https://github.com/ePC-SAFT/ePC-SAFT/issues/411, https://github.com/ePC-SAFT/ePC-SAFT/issues/412, https://github.com/ePC-SAFT/ePC-SAFT/issues/413, https://github.com/ePC-SAFT/ePC-SAFT/issues/414, https://github.com/ePC-SAFT/ePC-SAFT/issues/415, https://github.com/ePC-SAFT/ePC-SAFT/issues/416, https://github.com/ePC-SAFT/ePC-SAFT/issues/417
**Source Spec:** docs/superpowers/specs/2026-07-02-m6-khudaida-paper-validation-with-figiel-parameters.md
**Source Plan:** docs/superpowers/plans/2026-07-02-m6-khudaida-paper-validation-with-figiel-parameters-plan.md
**AFK/HITL:** AFK
**Classification:** AFK
**Labels:** validation, equilibrium, area:benchmark, area:equilibrium, status:ready, type:task
**Goal Command:** /goal Resolve the next ready Khudaida 2026 paper-validation figure issue.
**Execution Mode:** Auto, one child figure at a time
**Worktree Policy:** Native Codex worktree thread first
**Integration Policy:** Worker PR reviewed by main thread
**TDD Policy:** Required

## Outcome Summary

Track Khudaida 2026 figure reproduction as M6 paper-validation evidence with
Figiel 2025 parameter provenance and explicit M4/M5 blocker split rules.

## Project Merge

**Merge Owner:** Main thread orchestrator
**Merge Gate:** Native UI approval required
**Merge Policy:** Repo default
**Worktree Cleanup Policy:** Remove owned worktree after merge
**Orchestrator Wakeup Policy:** Worker handoff or bounded heartbeat

## What To Build

Resolve #406-#417 as retained Khudaida figure artifacts and validation
statistics. Model-comparable figures use fixed Figiel 2025 parameters through
the public package route; misses open or block on M4/M5 follow-up issues.

## Acceptance Criteria

- [ ] #406-#417 are native sub-issues of this parent.
- [ ] Figure issues retain source/model CSVs, plots, statistics, provenance,
  and exact failed rows where relevant.
- [ ] Solver defects route to M4 and parameter-regression defects route to M5.
- [ ] The final campaign checker reports complete accepted evidence or exact
  source-backed blockers.

## Blocked by

- https://github.com/ePC-SAFT/ePC-SAFT/issues/428

## Blocking

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

- No hidden parameter fitting inside M6 validation.
- No broad electrolyte capability claim beyond retained evidence.
- No private-native-only proof.
- No diagnostic-only success.

## Proof Oracle

```bash
gh issue view 421 --json number,title,milestone,parent,subIssues
uv run --no-sync python scripts/validation/check_khudaida_2026_figure_validation.py
uv run --no-sync python scripts/validate_plan_task_use_cases.py --plan-path docs/superpowers/plans/2026-07-02-m6-khudaida-paper-validation-with-figiel-parameters-plan.md
uv run --no-sync python scripts/validate_plan_outcome_proof.py --plan-path docs/superpowers/plans/2026-07-02-m6-khudaida-paper-validation-with-figiel-parameters-plan.md
```
