---
issue: 407
title: "M6 Khudaida Fig. 2: reproduce 293.15 K 5 wt% NaCl LLE with Figiel parameters"
url: "https://github.com/ePC-SAFT/ePC-SAFT/issues/407"
state: "open"
milestone: "M6 - Validation"
project: "ePC-SAFT Roadmap"
package: "benchmark"
capability: "electrolyte"
backend: "Ipopt"
readiness: "ready"
release_target: "validation"
source_spec: "docs/superpowers/specs/2026-07-02-m6-khudaida-paper-validation-with-figiel-parameters.md"
source_plan: "docs/superpowers/plans/2026-07-02-m6-validation-issue-0407-khudaida-figure-02-293k-5wt-lle-plan.md"
afk_hitl: "AFK"
branch: codex/issue-0407-khudaida-fig02
last_synced: "2026-07-02"
---

# M6 Khudaida Fig. 2: reproduce 293.15 K 5 wt% NaCl LLE with Figiel parameters

**GitHub Issue:** https://github.com/ePC-SAFT/ePC-SAFT/issues/407
**GitHub Milestone:** M6 - Validation
**Issue Type:** Task
**Sub-Issue Role:** leaf
**Executable:** true
**Parent Issue:** https://github.com/ePC-SAFT/ePC-SAFT/issues/421
**Parent Mirror:** docs/superpowers/issues/2026-07-02-m6-validation-issue-0421-khudaida-2026-paper-validation-parent.md
**Source Spec:** docs/superpowers/specs/2026-07-02-m6-khudaida-paper-validation-with-figiel-parameters.md
**Source Plan:** docs/superpowers/plans/2026-07-02-m6-validation-issue-0407-khudaida-figure-02-293k-5wt-lle-plan.md
**Classification:** AFK
**Labels:** enhancement, agent-ready, docs, validation, equilibrium, area:equilibrium, area:benchmark, backend:ipopt, status:ready, type:task
**Goal Command:** /goal Resolve issue #407 using docs/superpowers/plans/2026-07-02-m6-validation-issue-0407-khudaida-figure-02-293k-5wt-lle-plan.md and reproduce Khudaida Figure 2 with the retained 2026_Khudaida parameter bundle and Figiel 2025 SSM+DS/Born option provenance.
**Execution Mode:** Auto, one child figure at a time under #421
**Worktree Policy:** Native Codex worktree thread first
**Integration Policy:** Worker PR reviewed by main thread
**TDD Policy:** Required
**Parallelization Plan:** None
**Reviewer Role:** Main thread orchestrator
**Script Gate Mode:** Safety plus proof oracle

## Outcome Summary

**Outcome Source:** docs/superpowers/plans/2026-07-02-m6-validation-issue-0407-khudaida-figure-02-293k-5wt-lle-plan.md#outcome-proof
**Intent:** Reproduce Khudaida 2026 Figure 2 at 293.15 K and 5 wt% NaCl as retained M6 paper-validation evidence using the retained `2026_Khudaida` Tables 5-7 parameter bundle and Figiel 2025 SSM+DS/Born option provenance.
**Target Output:** Figure 2 source/model CSVs, plots, fit statistics, public-route diagnostics, focused package test, and checker evidence that can close only issue #407.
**Owner:** M6 validation owns retained artifact evidence, with M4 solver/API and M5 parameter-regression blockers opened only when row-level evidence proves that ownership.
**Interface:** `analyses/paper_validation/2026_khudaida/figures/figure_02`, `analyses/paper_validation/2026_khudaida/scripts/_common.py`, `scripts/validation/check_khudaida_2026_figure_validation.py`, and `packages/epcsaft-equilibrium/tests/api/test_khudaida_figure02_public_route_reproduction.py`.
**Cutover:** Replace the previous #407 execution contract that pointed to the M6 hierarchy cutover plan with the Figure 2 implementation plan linked above.
**Replaced Path:** Treating #407 as ready for direct execution while its source plan described tracker hierarchy hygiene instead of Figure 2 artifact reproduction.
**Acceptance Proof:** The proof oracle regenerates Figure 2 artifacts, the focused Figure 2 test passes, the Khudaida checker reports no Figure 2 blockers, validators pass, and any remaining fixed-parameter miss links an exact M4/M5 blocker before closeout.
**Evidence Summary:** Figure 2 regenerates complete artifacts with 16 source tie-line phase rows, 8 feed rows, 8 paper ePC-SAFT rows, and 16 public-route model rows. The retained Khudaida/Figiel-option path accepts 12/16 model rows, records `grand_aad=0.15663412623144893`, `rmse=0.20303190485486292`, `max_abs_error=0.3785917605164288`, `pass=False`, and exact failed tie lines `1,2,3,4,5,6,7,8`.
**Routed Blocker:** https://github.com/ePC-SAFT/ePC-SAFT/issues/338 owns the remaining M5 parameter-regression work for noncollapsed Khudaida electrolyte LLE validation.
**Stop Criteria:** Stop before closing #407 if source rows are not traceable, the public route is not used, diagnostics are missing, accepted rows remain incomplete without an M4/M5 blocker, or validators cannot prove the retained artifacts.
**Avoid:** Do not fit hidden parameters in M6, use private-native-only evidence, count diagnostic-only success, broaden electrolyte capability claims, or edit unrelated Khudaida figures.

## Project Merge

**Merge Owner:** Main thread orchestrator
**Merge Gate:** Native UI approval required
**Merge Policy:** Repo default
**Worktree Cleanup Policy:** Remove owned worktree after merge
**Orchestrator Wakeup Policy:** Worker handoff or bounded heartbeat

## What To Build

Regenerate Figure 2 source/model artifacts, retained statistics, and
public-route electrolyte LLE diagnostics through the retained `2026_Khudaida`
parameter path and Figiel 2025 SSM+DS/Born option provenance.

## Acceptance Criteria

- [ ] Figure 2 source/model CSVs and plot artifacts regenerate.
- [ ] Accepted rows use the public electrolyte LLE route.
- [ ] Per-row diagnostics retain material balance, pressure, phase charge,
  lift/back-lift, neutral transfer, mean-ionic transfer, phase distance,
  exact-Hessian, and Ipopt route receipts.
- [ ] Fit statistics include row counts, tolerance basis, AAD/RMSE/max error,
  and exact failed rows routed to #338.

## Blocked By

- #406

## Blocking

- #421
- #408

## Non-goals

- No hidden parameter fitting inside M6 validation.
- No private-native-only proof.
- No broad electrolyte capability claim beyond retained Figure 2 evidence.

## Proof Oracle

```powershell
uv run --no-sync python analyses\paper_validation\2026_khudaida\figures\figure_02\scripts\generate_data.py
uv run --no-sync python analyses\paper_validation\2026_khudaida\figures\figure_02\scripts\render_figure.py
uv run --no-sync python scripts\validation\check_khudaida_2026_figure_validation.py --figure figure_02 --require-complete --json
uv run --no-sync python -m pytest packages\epcsaft-equilibrium\tests\api\test_khudaida_figure02_public_route_reproduction.py -q
pwsh.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\validate-issue-mirror.ps1 -IssueFile docs\superpowers\issues\2026-07-02-m6-validation-issue-0407-khudaida-figure-02-293k-5wt-lle.md
pwsh.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\validate-plan-task-use-cases.ps1 -PlanPath docs\superpowers\plans\2026-07-02-m6-validation-issue-0407-khudaida-figure-02-293k-5wt-lle-plan.md
pwsh.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\validate-plan-outcome-proof.ps1 -PlanPath docs\superpowers\plans\2026-07-02-m6-validation-issue-0407-khudaida-figure-02-293k-5wt-lle-plan.md
uv run --no-sync python scripts\dev\validate_project.py docs
git diff --check
```
