---
issue: 428
title: "M4: reject collapsed Khudaida electrolyte LLE splits"
url: https://github.com/ePC-SAFT/ePC-SAFT/issues/428
state: open
milestone: "M4 - Equilibrium"
project: "ePC-SAFT Roadmap"
package: equilibrium
capability: electrolyte_lle
backend: Ipopt
readiness: ready
release_target: equilibrium-0.x
source_spec: docs/superpowers/specs/2026-07-03-m4-khudaida-collapsed-electrolyte-lle-rejection.md
source_plan: docs/superpowers/plans/2026-07-03-m4-equilibrium-khudaida-collapsed-electrolyte-lle-rejection-plan.md
afk_hitl: AFK
branch: codex/issue-0428-khudaida-collapsed-lle-rejection
last_synced: "2026-07-03"
---

# M4: reject collapsed Khudaida electrolyte LLE splits

**GitHub Issue:** https://github.com/ePC-SAFT/ePC-SAFT/issues/428
**GitHub Milestone:** M4 - Equilibrium
**Issue Type:** Bug
**Source Spec:** docs/superpowers/specs/2026-07-03-m4-khudaida-collapsed-electrolyte-lle-rejection.md
**Source Plan:** docs/superpowers/plans/2026-07-03-m4-equilibrium-khudaida-collapsed-electrolyte-lle-rejection-plan.md
**AFK/HITL:** AFK
**Classification:** AFK
**Labels:** agent-ready, bug, native, solver, validation, equilibrium, area:equilibrium, backend:ipopt, status:ready, type:bug
**Goal Command:** /goal Resolve issue 428 by making Khudaida public electrolyte_lle validation reject collapsed false-positive splits and retain a root-cause diagnosis for the trivial-branch convergence.
**Execution Mode:** Ask at runtime
**Worktree Policy:** Native Codex worktree thread first
**Integration Policy:** Worker PR reviewed by main thread
**TDD Policy:** Required
**Parallelization Plan:** None
**Reviewer Role:** Main thread orchestrator
**Script Gate Mode:** Safety plus proof oracle

## Outcome Summary

**Outcome Source:** docs/superpowers/plans/2026-07-03-m4-equilibrium-khudaida-collapsed-electrolyte-lle-rejection-plan.md#outcome-proof
**Intent:** Replace false-positive Khudaida LLE acceptance with a truthful public-route evidence path that rejects collapsed duplicate-feed phases and records why the noncollapsed branch is absent.
**Target Output:** Updated checker, tests, retained Figure 2 artifacts, and route diagnostics that make the collapsed split visible as a failure instead of accepted model evidence.
**Owner:** `packages/epcsaft-equilibrium` owns public `electrolyte_lle` route acceptance and postsolve truthfulness; `analyses/paper_validation/2026_khudaida` owns retained source/model artifact evidence; #338 owns fitted-parameter work if needed.
**Interface:** `Equilibrium(..., route="electrolyte_lle")`, `scripts/validation/check_khudaida_2026_figure_validation.py`, `analyses/paper_validation/2026_khudaida/figures/figure_02/results/data/model_tielines.csv`, and focused package tests.
**Cutover:** Current rows with collapsed phase distance and trace minor beta stop counting as accepted model rows.
**Replaced Path:** Treating `converged=True`, `postsolve_accepted=True`, and finite compositions as enough to accept a Khudaida LLE model row.
**Acceptance Proof:** The proof oracle passes, and the checker can no longer return model-row success for current collapsed Figure 2 rows. If noncollapsed model rows remain absent, close only with retained route diagnostics assigning remaining fitted-parameter work to #338.
**Stop Criteria:** Stop before changing parameters, adding hidden row-specific seeds, weakening phase-distance thresholds, bypassing public route execution, or claiming Khudaida reproduction while any model row is collapsed.
**Avoid:** Do not fit parameters in M4, count duplicate-feed phases as LLE, demote solver failure to plotting tolerance, route around public `electrolyte_lle`, or broaden capability language.

## Project Merge

**Merge Owner:** Main thread orchestrator
**Merge Gate:** Native UI approval required
**Merge Policy:** Repo default
**Worktree Cleanup Policy:** Remove owned worktree after merge
**Orchestrator Wakeup Policy:** Worker handoff or bounded heartbeat

## Reproduction

Verified local evidence from Figure 2:

- Source tie-lines come from Khudaida Table 3: 293.15 K and 5 wt% NaCl.
- Feed rows invert to about 5.00 wt% NaCl, near 1:1 aqueous feed to isobutanol mass ratio, and ethanol mass fractions spanning about 2.0 to 11.6 wt%.
- Current public-route model rows accept six tie-lines with phase distances about `1.7e-8` to `1.17e-7` and phase fractions near `0.99999 / 1e-5`.
- Tie-lines 6 and 7 fail postsolve certification.
- A direct midpoint feed probe for Table 3 tie-line 1 also converges to a collapsed split.

## What To Build

Make collapsed public `electrolyte_lle` rows fail loudly in Khudaida model
validation, then diagnose why the route is converging to the trivial branch
instead of a noncollapsed LLE split. Repair the M4-owned route or postsolve
acceptance path when that is the defect. If the retained parameter bundle
cannot support noncollapsed residual-feasible Khudaida rows, retain the
evidence and keep #338 as the M5 owner.

## Acceptance Criteria

- [ ] The checker classifies collapsed finite public-route rows as `model_row_failures` with tie-line id, phase distance, beta values, objective, statuses, and root cause.
- [ ] Figure 2 ties 1-5 and 8 are no longer counted as accepted model rows while their phase distance remains `O(1e-8)` and minor beta remains `O(1e-5)`.
- [ ] Public `electrolyte_lle` diagnostics explain why the current row converges to the trivial branch: branch-selection defect, route/postsolve acceptance defect, or current-parameter noncollapsed infeasibility.
- [ ] If the route can produce a noncollapsed split with the retained parameter bundle, regenerated Figure 2 model rows retain noncollapsed phase distances and pass focused route tests.
- [ ] If retained parameters cannot produce a noncollapsed residual-feasible split, the checker fails loudly with a #338-owned root-cause payload and no M4 hidden parameter edits.
- [ ] Regenerated Figure 2 artifacts retain source data, feed provenance, route diagnostics, and fit statistics consistent with the new row classification.
- [ ] No public capability text claims full Khudaida reproduction while any model row is collapsed or #338-owned.

## Blocked by

- None. Related M5 parameter-regression follow-up: #338.

## Non-goals

- No M5 regression implementation.
- No changes to Khudaida source Table 3 or Table 4 data.
- No changes to issue #407's retained source provenance except clarifying the collapsed-model diagnosis.
- No downstream metrics or release readiness claims.

## Proof Oracle

```powershell
$env:KHUDAIDA_FORCE_RECOMPUTE='1'; uv run --no-sync python analyses\paper_validation\2026_khudaida\figures\figure_02\scripts\generate_data.py
uv run --no-sync python analyses\paper_validation\2026_khudaida\figures\figure_02\scripts\render_figure.py
uv run --no-sync python scripts\validation\check_khudaida_2026_figure_validation.py --figure figure_02 --require-complete --json
uv run --no-sync python scripts\validation\check_khudaida_2026_figure_validation.py --figure figure_02 --require-complete --require-model-pass --json
uv run --no-sync python -m pytest packages\epcsaft-equilibrium\tests\api\test_khudaida_collapsed_electrolyte_lle_rejection.py -q
uv run --no-sync python -m pytest packages\epcsaft-equilibrium\tests\api\test_khudaida_figure02_public_route_reproduction.py -q
uv run --no-sync python scripts/validate_plan_task_use_cases.py --plan-path docs/superpowers/plans/2026-07-03-m4-equilibrium-khudaida-collapsed-electrolyte-lle-rejection-plan.md
uv run --no-sync python scripts/validate_plan_outcome_proof.py --plan-path docs/superpowers/plans/2026-07-03-m4-equilibrium-khudaida-collapsed-electrolyte-lle-rejection-plan.md
uv run --no-sync python scripts\dev\validate_project.py docs
git diff --check
pwsh.exe -NoProfile -ExecutionPolicy Bypass -File "$env:USERPROFILE\.codex\hooks\codex-cleanup.ps1" -RepoRoot .
```

The `--require-model-pass` command may fail after this issue only when its JSON
failure payload proves noncollapsed rows are blocked by #338-owned parameter
regression. It must not pass with collapsed rows.

## GitHub Body Text

This issue makes the Khudaida public `electrolyte_lle` validation path reject
collapsed false-positive splits before claiming model evidence. It owns the M4
route/postsolve truthfulness and diagnosis work exposed by closed M6 issue #407.
M5 issue #338 remains the owner of fitted-parameter work if the M4 diagnosis
proves the retained parameter bundle cannot support noncollapsed residual-feasible
Khudaida rows.
