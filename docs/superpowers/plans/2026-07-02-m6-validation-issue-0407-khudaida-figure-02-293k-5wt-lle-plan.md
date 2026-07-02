# Khudaida Figure 2 Public Route Evidence Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reproduce Khudaida 2026 Figure 2 at 293.15 K and 5 wt% NaCl through the public electrolyte LLE route using the fixed Figiel 2025 parameter snapshot.

**Architecture:** Keep the figure-specific scripts as the public artifact entrypoints and make the shared Khudaida model-generation helper produce complete Figure 2 package-route evidence. Add a narrow package test that proves the retained Figure 2 CSVs, diagnostics, statistics, and checker output are consistent with the M6 paper-validation contract.

**Tech Stack:** Python via `uv`, `packages/epcsaft-equilibrium`, public `Equilibrium(..., route="electrolyte_lle")`, Ipopt route diagnostics, retained CSV/Matplotlib artifacts, and PowerShell Superpowers validators.

---

## Source Evidence

- Issue mirror: `docs/superpowers/issues/2026-07-02-m6-validation-issue-0407-khudaida-figure-02-293k-5wt-lle.md`.
- Source spec: `docs/superpowers/specs/2026-07-02-m6-khudaida-paper-validation-with-figiel-parameters.md`.
- Figure folder: `analyses/paper_validation/2026_khudaida/figures/figure_02`.
- Shared model owner: `analyses/paper_validation/2026_khudaida/scripts/_common.py`.
- Current measured state: Figure 2 retains 16 experimental tie-line phase rows, 8 paper ePC-SAFT rows, and 8 feed rows; the retained package model CSV has 16 rows but only 2 accepted model rows and `fit_statistics.csv` has `pass=False`.

## Test Complete And Metrics

Figure 2 is complete only when the retained artifacts prove these values:

- `source/source_points.csv` has 16 `experimental_tieline` rows, 8 `paper_epcsaft` rows, and 8 `feed` rows at 293.15 K and `salt_wtfrac=0.05`.
- `results/data/model_tielines.csv` has 16 rows, two phases for each of the 8 tie lines, `source=epcsaft_public_electrolyte_lle`, finite phase compositions, and public-route diagnostics for every accepted row.
- `results/fit_statistics.csv` has `series=package_electrolyte_lle_vs_experimental`, `model_point_count=16`, `accepted_model_count=16`, `pass=True`, and records AAD/RMSE/max-error style statistics or exact failed rows if the fixed Figiel path cannot pass.
- `scripts/validation/check_khudaida_2026_figure_validation.py --require-complete --require-model-pass` has no Figure 2 artifact blockers or Figure 2 model blockers.
- The branch reports any unresolved fixed-parameter miss as an explicit M4 solver/API blocker or M5 parameter-regression blocker before #407 can close.

## Outcome Proof

**Intent:** Turn #407 from a hierarchy-ready leaf into retained Figure 2 validation evidence that a maintainer can inspect and rerun through the public electrolyte LLE route.
**Current Behavior:** The Figure 2 artifact folder exists and the checker can read it, but retained package-route statistics accept only 2 of 16 model rows and the #407 mirror previously pointed at the hierarchy cutover plan instead of an executable Figure 2 implementation plan.
**Expected Outcome:** Figure 2 regenerates retained source/model CSVs, plots, fit statistics, and diagnostics through the public package route, or stops with exact row-level evidence and a routed M4/M5 blocker.
**Target Output:** A #407 PR with Figure 2 retained artifacts, a Figure 2 package test, checker evidence, and issue mirror proof that closes only the Figure 2 leaf.
**Owner:** M6 validation owns the retained paper-validation artifacts; M4 owns solver/API defects discovered by the validation; M5 owns parameter-regression defects discovered by fixed Figiel evidence.
**Interface:** `analyses/paper_validation/2026_khudaida/figures/figure_02`, `analyses/paper_validation/2026_khudaida/scripts/_common.py`, `scripts/validation/check_khudaida_2026_figure_validation.py`, and `packages/epcsaft-equilibrium/tests/api/test_khudaida_figure02_public_route_reproduction.py`.
**Cutover:** Replace the previous #407 execution contract that reused the M6 hierarchy cutover plan with this Figure 2 implementation plan and a structured #407 Outcome Summary.
**Replaced Path:** Treating #407 as ready for direct execution while its mirror pointed at tracker-hierarchy work instead of Figure 2 artifact reproduction.
**Evidence:** Retained Figure 2 CSVs, regenerated plot files, package-route diagnostics, fit statistics, focused pytest output, Khudaida checker output, issue mirror validation, plan validators, and docs validation.
**Acceptance Proof:** A reviewer can rerun the proof oracle and see complete Figure 2 source/model rows, public-route diagnostics, passing Figure 2 statistics or exact routed blockers, and no Figure 2 checker blockers.
**Stop Criteria:** Stop before closing #407 if source rows are not traceable, the public route is not used, diagnostics are missing, accepted rows remain incomplete without an M4/M5 blocker, or validator output cannot prove the retained artifacts.
**Avoid:** Do not fit hidden parameters in M6, use private-native-only evidence, count diagnostic-only success, broaden electrolyte capability claims, or edit unrelated Khudaida figures.
**Risk:** A fixed Figiel parameter miss can look like a solver problem unless inputs, units, species ordering, phase labels, diagnostics, and parameter provenance are verified before changing code.

## Implementation Boundaries

**Files To Create:** `packages/epcsaft-equilibrium/tests/api/test_khudaida_figure02_public_route_reproduction.py`.
**Files To Modify:** `analyses/paper_validation/2026_khudaida/scripts/_common.py`, `analyses/paper_validation/2026_khudaida/figures/figure_02/scripts/generate_data.py`, `analyses/paper_validation/2026_khudaida/figures/figure_02/scripts/render_figure.py`, `scripts/validation/check_khudaida_2026_figure_validation.py`, Figure 2 retained artifacts under `analyses/paper_validation/2026_khudaida/figures/figure_02/results`, and the #407 issue mirror when status evidence changes.
**Files To Avoid:** `packages/epcsaft-regression/**`, unrelated provider/EOS code, unrelated Khudaida figure folders, downstream projects, release docs, and broad roadmap files.
**Source Of Truth:** Khudaida 2026 Figure 2 retained source CSVs, `analyses/paper_validation/2025_figiel/parameters`, and the public `electrolyte_lle` route diagnostics.
**Read Path:** Trace source rows, feed rows, Figiel parameter loading, explicit-ion/formula-basis conversion, public route solve inputs, phase labels, diagnostics, model CSV rows, fit statistics, and checker payload before changing solver behavior.
**Write Path:** Add the failing Figure 2 acceptance test first, then change the smallest owner needed to regenerate the public-route Figure 2 artifacts and diagnostics.
**Integration Points:** `Equilibrium(..., route="electrolyte_lle")`, Ipopt diagnostics, `solve_model_rows`, `get_or_build_model_rows`, `_fit_statistics_row`, `write_case_data`, `plot_lle_figure`, the Khudaida checker, and the retained plot artifact contract.
**Migration Or Cutover:** Keep #406 closed and #408 blocked while #407 runs; move only #407's source plan and outcome proof to this executable plan.
**Replaced Path Handling:** Preserve the M6 hierarchy plan for tracker organization, but stop using it as #407's direct implementation contract.
**Acceptance Proof Gate:** The PR must show Figure 2 numeric statistics, exact artifact paths, checker output, focused pytest output, plan and mirror validators, docs validation, and cleanup output before push approval.

## Decision Ledger

| Decision | Source | Answer | Impact | Deferred? | Risk owner |
| --- | --- | --- | --- | --- | --- |
| Execution scope | User Looping Mode revisit and issue #407 | Repair #407's execution contract and then resolve Figure 2 only. | Prevents the parent #421 and blocked #408 from entering implementation. | No | Main thread |
| Milestone ownership | M6 Khudaida spec | Figure 2 artifact evidence stays in M6; M4/M5 receive blockers only when evidence proves their ownership. | Keeps validation work separate from solver/API and parameter-regression work. | No | M6 validation owner |
| Parameter policy | #407 issue body and M6 spec | Use fixed Figiel 2025 parameters from `analyses/paper_validation/2025_figiel/parameters`. | Blocks hidden fitting inside the validation branch. | No | M6 validation owner |
| Test-complete metrics | Current Figure 2 artifacts and #407 acceptance criteria | Require 16 source tie-line phase rows, 8 paper points, 8 feed rows, 16 public-route model rows, complete diagnostics, and passing Figure 2 checker evidence. | Gives reviewers numeric proof instead of a visual-only plot comparison. | No | Main thread |
| Branch strategy | #407 mirror | Use `codex/issue-0407-khudaida-fig02`. | Keeps plan repair and Figure 2 implementation on the issue branch. | No | Main thread |
| Stop rule | Chemical-engineering input gate | Verify inputs and provenance before changing solver or parameter logic. | Prevents treating bad inputs as equation or optimizer defects. | No | Main thread |

## Acceptance Criteria

- Figure 2 source/model CSVs and plot artifacts regenerate from the issue proof oracle.
- Accepted rows use the public `electrolyte_lle` package route and retain material balance, pressure, phase charge, lift/back-lift, neutral transfer, mean-ionic transfer, phase distance, exact-Hessian, and Ipopt route receipts where the public route exposes them.
- Fit statistics report row counts, tolerance basis, AAD/RMSE/max error, and exact failed rows when any row cannot pass with fixed Figiel parameters.
- `packages/epcsaft-equilibrium` has a focused Figure 2 test that fails on the current retained `accepted_model_count=2` state and passes only after retained evidence is complete.
- The PR either closes #407 with retained Figure 2 evidence or links a new/existing M4/M5 blocker with exact failed-row evidence.

## Non-Goals

- No hidden parameter fitting inside M6 validation.
- No private-native-only proof.
- No broad electrolyte capability claim.
- No edits to unrelated Khudaida figures.

## Tasks

### Task 1: Add The Figure 2 Acceptance Test

**Use Cases:**
- Acceptance proof shows Figure 2 has complete retained source rows, model rows, fit statistics, and public-route provenance before #407 can close.
- Cutover proof shows #407 now executes this Figure 2 evidence plan instead of the older hierarchy-only plan.
- Failure evidence shows the current retained state fails because `accepted_model_count` is 2 rather than the required 16.

**Files:**
- Create: `packages/epcsaft-equilibrium/tests/api/test_khudaida_figure02_public_route_reproduction.py`
- Read: `packages/epcsaft-equilibrium/tests/api/test_khudaida_figure01_source_reproduction.py`
- Test: `packages/epcsaft-equilibrium/tests/api/test_khudaida_figure02_public_route_reproduction.py`

- [ ] **Step 1: Write the failing Figure 2 artifact test.** Read `source/source_points.csv`, `source/feed_compositions.csv`, `results/data/model_tielines.csv`, and `results/fit_statistics.csv`; assert the source row counts, 16 model rows, `source=epcsaft_public_electrolyte_lle`, no blank model compositions for accepted rows, `accepted_model_count == "16"`, and `pass == "True"`.
- [ ] **Step 2: Run the focused test and verify the expected failure.** Run `uv run --no-sync python -m pytest packages\epcsaft-equilibrium\tests\api\test_khudaida_figure02_public_route_reproduction.py -q`; expected failure is the current retained `accepted_model_count` or `pass` assertion.
- [ ] **Step 3: Keep the test focused on retained artifacts.** Do not call the solver directly from the test; generation scripts and the checker own solver execution so the test stays deterministic.
- [ ] **Step 4: Commit after the failing test is proven.** Commit only the test when the expected failure is captured.

### Task 2: Verify Inputs, Parameters, And Diagnostics Before Solver Changes

**Use Cases:**
- Acceptance evidence proves Figure 2 inputs use 293.15 K, 5 wt% NaCl, 8 feed rows, 16 experimental phase rows, and fixed Figiel 2025 parameters.
- Failure evidence separates bad input/provenance from M4 solver/API behavior or M5 parameter adequacy.
- Cutover evidence keeps #407 within M6 validation until a source-backed M4/M5 blocker is required.

**Files:**
- Read: `analyses/paper_validation/2026_khudaida/figures/figure_02/source/source_points.csv`
- Read: `analyses/paper_validation/2026_khudaida/figures/figure_02/source/feed_compositions.csv`
- Read: `analyses/paper_validation/2025_figiel/parameters/**`
- Modify: `analyses/paper_validation/2026_khudaida/scripts/_common.py`
- Modify: `analyses/paper_validation/2026_khudaida/figures/figure_02/source/source_notes.csv`

- [ ] **Step 1: Trace the run contract.** Verify species order, formula-basis versus explicit-ion conversion, salt mass fraction, temperature, pressure, feed normalization, and parameter path before changing code.
- [ ] **Step 2: Snapshot provenance in source notes or retained diagnostics.** Ensure the Figure 2 artifact set names the Figiel parameter path and public `electrolyte_lle` route.
- [ ] **Step 3: Preserve failed-row evidence.** If any row remains incomplete after verified inputs, retain tie-line id, feed composition, route status, solver status, residual norm, phase distance, and objective.
- [ ] **Step 4: Re-run the focused test.** Confirm it still fails until the public-route artifacts and diagnostics are complete.

### Task 3: Regenerate Figure 2 Public-Route Artifacts

**Use Cases:**
- Acceptance proof shows `generate_data.py`, `render_figure.py`, and the retained checker agree on the same Figure 2 data.
- Validation evidence shows public-route rows are regenerated rather than manually patched.
- Recovery evidence records exact failed rows and blocker ownership if fixed Figiel parameters cannot reproduce every row.

**Files:**
- Modify: `analyses/paper_validation/2026_khudaida/scripts/_common.py`
- Modify: `analyses/paper_validation/2026_khudaida/figures/figure_02/scripts/generate_data.py`
- Modify: `analyses/paper_validation/2026_khudaida/figures/figure_02/scripts/render_figure.py`
- Modify: `analyses/paper_validation/2026_khudaida/figures/figure_02/results/**`
- Modify: `scripts/validation/check_khudaida_2026_figure_validation.py`

- [ ] **Step 1: Make `generate_data.py` regenerate Figure 2 data.** Route it through the shared Figure 2 public-route generation path instead of leaving it as a no-op.
- [ ] **Step 2: Update the shared helper only where Figure 2 evidence requires it.** Keep changes around `solve_model_rows`, `get_or_build_model_rows`, `_fit_statistics_row`, `write_case_data`, or `plot_lle_figure`.
- [ ] **Step 3: Regenerate data and plots.** Run `uv run --no-sync python analyses\paper_validation\2026_khudaida\figures\figure_02\scripts\generate_data.py` and `uv run --no-sync python analyses\paper_validation\2026_khudaida\figures\figure_02\scripts\render_figure.py`.
- [ ] **Step 4: Inspect retained statistics.** Confirm `fit_statistics.csv` reports row counts, tolerance basis, AAD/RMSE/max error fields where implemented, pass status, and exact failed rows when present.
- [ ] **Step 5: Re-run the focused test.** Run the Figure 2 pytest command and keep iterating only within the Figure 2/shared-owner boundary until it passes or the stop criteria require an M4/M5 blocker.

### Task 4: Validate, Update The Mirror, And Prepare PR Evidence

**Use Cases:**
- Acceptance evidence covers the proof oracle, issue mirror validator, source plan validators, docs validator, `git diff --check`, and cleanup hook.
- Cutover evidence shows #407's local mirror points at this executable plan and #408 remains blocked until #407 closes.
- Reviewer evidence includes exact artifact paths, numeric statistics, and blocker ownership if closure depends on M4/M5 follow-up.

**Files:**
- Modify: `docs/superpowers/issues/2026-07-02-m6-validation-issue-0407-khudaida-figure-02-293k-5wt-lle.md`
- Test: `scripts/validate-issue-mirror.ps1`
- Test: `scripts/validate-plan-task-use-cases.ps1`
- Test: `scripts/validate-plan-outcome-proof.ps1`
- Test: `scripts/dev/validate_project.py`

- [ ] **Step 1: Update the #407 mirror with final evidence.** Keep `Sub-Issue Role: leaf`, `Executable: true`, this source plan path, acceptance status, and exact artifact paths aligned.
- [ ] **Step 2: Run the issue proof oracle.** Run the two Figure 2 scripts, the Khudaida checker, and the focused pytest command from the #407 mirror.
- [ ] **Step 3: Run Superpowers validators.** Run the plan task-use-case validator, plan outcome-proof validator, issue mirror validator, docs validator, and `git diff --check`.
- [ ] **Step 4: Run cleanup.** Run `pwsh.exe -NoProfile -ExecutionPolicy Bypass -File "$env:USERPROFILE\.codex\hooks\codex-cleanup.ps1" -RepoRoot .`.
- [ ] **Step 5: Prepare PR evidence.** Summarize acceptance coverage, exact numeric statistics, changed artifacts, validation receipts, and the closing reference `Closes #407`.

## Proof Oracle

```powershell
uv run --no-sync python analyses\paper_validation\2026_khudaida\figures\figure_02\scripts\generate_data.py
uv run --no-sync python analyses\paper_validation\2026_khudaida\figures\figure_02\scripts\render_figure.py
uv run --no-sync python scripts\validation\check_khudaida_2026_figure_validation.py --require-complete --require-model-pass
uv run --no-sync python -m pytest packages\epcsaft-equilibrium\tests\api\test_khudaida_figure02_public_route_reproduction.py -q
uv run --no-sync python -m pytest packages\epcsaft-equilibrium\tests -k "khudaida and figure_02 and electrolyte" -q
pwsh.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\validate-issue-mirror.ps1 -IssueFile docs\superpowers\issues\2026-07-02-m6-validation-issue-0407-khudaida-figure-02-293k-5wt-lle.md
pwsh.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\validate-plan-task-use-cases.ps1 -PlanPath docs\superpowers\plans\2026-07-02-m6-validation-issue-0407-khudaida-figure-02-293k-5wt-lle-plan.md
pwsh.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\validate-plan-outcome-proof.ps1 -PlanPath docs\superpowers\plans\2026-07-02-m6-validation-issue-0407-khudaida-figure-02-293k-5wt-lle-plan.md
uv run --no-sync python scripts\dev\validate_project.py docs
git diff --check
```

Decision-ledger validation is represented by the `## Decision Ledger` table in
this plan. This repo currently owns `scripts/validate-plan-task-use-cases.ps1`
and `scripts/validate-plan-outcome-proof.ps1`, but it does not contain a
repo-local `scripts/validate-decision-ledger.ps1` validator.
