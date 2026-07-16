# Khudaida Collapsed Electrolyte LLE Rejection Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make Khudaida public `electrolyte_lle` validation reject collapsed false-positive splits and retain a root-cause diagnosis for why the route converges to the trivial branch.

**Architecture:** Repair the evidence chain before changing solver behavior: first make the Khudaida checker and artifact tests classify collapsed rows as model-row failures, then use that failing loop to inspect route/postsolve diagnostics and branch selection. If M4 owns the defect, repair the public route or postsolve acceptance path; if current parameters cannot support noncollapsed residual-feasible Khudaida rows, keep the route truthful and hand fitted-parameter work to #338.

**Tech Stack:** Python, pytest, `epcsaft-equilibrium`, native C++ equilibrium route diagnostics, Ipopt, retained Khudaida 2026 paper-validation artifacts.

---

## Source And Scope

- Source Spec: `docs/superpowers/specs/2026-07-03-m4-khudaida-collapsed-electrolyte-lle-rejection.md`
- Related closed validation issue: #407
- Related M5 parameter-regression issue: #338
- Owning milestone: `M4 - Equilibrium`
- Owning package: `packages/epcsaft-equilibrium`
- Execution classification: AFK
- Issue type: Bug
- TDD policy: Required
- Debug policy: Required; use systematic route/input diagnosis before solver changes

## Outcome Proof

**Intent:** Replace false-positive Khudaida LLE acceptance with a truthful public-route evidence path that rejects collapsed duplicate-feed phases and records why the noncollapsed branch is absent.

**Current Behavior:** Figure 2 source tie-lines and feed rows are traceable, but current package model rows accept six public-route solves whose phase distances are only about `1.7e-8` to `1.17e-7` and whose phase fractions are effectively `0.99999 / 1e-5`. Tie-lines 6 and 7 fail postsolve certification. A direct midpoint feed probe for Table 3 tie-line 1 also converges to a collapsed split. The checker reports model fit failure, but row-level failure classification does not yet say that accepted finite rows are physically collapsed.

**Expected Outcome:** Collapsed rows are classified as failed Khudaida model rows with explicit phase-distance, beta, and route diagnostics. The public route either produces noncollapsed Figure 2 rows, or retains a source-backed diagnosis that the current parameter bundle cannot satisfy noncollapsed residual feasibility and keeps #338 as the parameter owner.

**Target Output:** Updated checker, tests, retained Figure 2 artifacts, and route diagnostics that make the collapsed split visible as a failure instead of accepted model evidence.

**Owner:** `packages/epcsaft-equilibrium` owns public `electrolyte_lle` route acceptance and postsolve truthfulness; `analyses/paper_validation/2026_khudaida` owns retained source/model artifact evidence; #338 owns fitted-parameter work if needed.

**Interface:** `Equilibrium(..., route="electrolyte_lle")`, `scripts/validation/check_khudaida_2026_figure_validation.py`, `analyses/paper_validation/2026_khudaida/figures/figure_02/results/data/model_tielines.csv`, and focused package tests.

**Cutover:** Current rows with collapsed phase distance and trace minor beta stop counting as accepted model rows. New artifacts must show either noncollapsed model rows or explicit collapsed/root-cause failures.

**Replaced Path:** Treating `converged=True`, `postsolve_accepted=True`, and finite compositions as enough to accept a Khudaida LLE model row.

**Evidence:** Failing and passing pytest output, checker JSON with `model_row_failures`, regenerated Figure 2 model CSVs, root-cause diagnostic payload, and retained comparison against Table 3/feed provenance.

**Acceptance Proof:** The proof oracle passes, and the checker can no longer return model-row success for the current collapsed Figure 2 rows. If noncollapsed model rows remain absent, the issue closes only with retained route diagnostics proving the failure is assigned to #338 rather than hidden in M4.

**Stop Criteria:** Stop before changing parameters, adding hidden row-specific seeds, weakening phase-distance thresholds, bypassing public route execution, or claiming Khudaida reproduction while any model row is collapsed.

**Avoid:** Do not fit parameters in M4, do not count duplicate-feed phases as LLE, do not demote solver failure to a plotting tolerance, do not route around public `electrolyte_lle`, and do not broaden capability language.

**Risk:** A route-level fix may still leave model reproduction blocked by #338. That is acceptable only if M4 first rejects collapsed acceptance and retains proof that the route diagnosis is complete.

## Implementation Boundaries

**Files To Create:**
- `packages/epcsaft-equilibrium/tests/api/test_khudaida_collapsed_electrolyte_lle_rejection.py`

**Files To Modify:**
- `scripts/validation/check_khudaida_2026_figure_validation.py`
- `analyses/paper_validation/2026_khudaida/scripts/_common.py`
- `packages/epcsaft-equilibrium/tests/api/test_khudaida_figure02_public_route_reproduction.py`
- `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/workflows.py`
- `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/core/native_results.py`
- `packages/epcsaft-equilibrium/native/equilibrium/core/two_phase_eos_route.cpp`
- `analyses/paper_validation/2026_khudaida/figures/figure_02/results/data/model_tielines.csv`
- `analyses/paper_validation/2026_khudaida/figures/figure_02/results/fit_statistics.csv`
- `analyses/paper_validation/2026_khudaida/figures/figure_02/results/model_curve.csv`
- `analyses/paper_validation/2026_khudaida/figures/figure_02/results/plotted_data.csv`
- `analyses/paper_validation/2026_khudaida/figures/figure_02/source/source_notes.csv`

**Files To Avoid:**
- `packages/epcsaft-regression/**`
- `analyses/paper_validation/2026_khudaida/parameters/**` unless only provenance text is corrected
- Downstream repositories
- Release documentation
- Unrelated provider/EOS refactors

**Source Of Truth:** Khudaida Table 3 source rows, Figure 2 feed provenance, retained public-route diagnostics, and M4 route/postsolve acceptance contracts.

**Read Path:** Read Table 3 rows, Figure 2 feed rows, retained model rows, `_common.py` generation logic, checker failure logic, public route result conversion, native postsolve acceptance, and #338 residual-feasibility evidence before changing behavior.

**Write Path:** Change the smallest owner that can make collapsed rows fail loudly. Checker/artifact changes happen before route changes; route changes happen only after the failing tests prove the defect boundary.

**Integration Points:** Khudaida artifact generation, checker CLI, package API tests, public `Equilibrium` route, native route diagnostics, and issue #338 dependency evidence.

**Migration Or Cutover:** Regenerate Figure 2 artifacts after the classification and route changes so retained CSVs no longer present collapsed rows as accepted model evidence.

**Replaced Path Handling:** Replace finite-composition acceptance with noncollapsed phase certification for Khudaida rows. Keep #338 as the owner for fitted parameters if noncollapsed feasibility remains impossible with the retained bundle.

**Acceptance Proof Gate:** No implementation branch is complete until the checker, focused tests, regenerated Figure 2 artifacts, docs validation, `git diff --check`, and cleanup hook all pass or the checker fails only with retained #338-owned root-cause evidence.

## Test Complete And Metrics

- Minimum Khudaida noncollapsed phase distance: `1.0e-3` formula-basis infinity norm.
- Minor phase beta review threshold: `1.0e-4`.
- Current bad-row target: ties 1-5 and 8 in Figure 2 must no longer be counted as accepted model rows when their phase distance is `O(1e-8)` and minor beta is `O(1e-5)`.
- Source-data preservation target: Figure 2 keeps 16 experimental phase rows, 8 feed rows, and 8 paper ePC-SAFT comparison rows.
- Feed contract target: regenerated feed rows remain about 5 wt% NaCl and 1:1 aqueous feed to isobutanol mass ratio.
- Route diagnosis target: each rejected row records `phase_distance`, `phase_distance_threshold`, `beta_organic`, `beta_aqueous`, `route_status`, `solver_status`, `application_status`, `postsolve_accepted`, and `root_cause`.

## Decision Ledger

| Decision | Source | Answer | Impact | Deferred? | Risk owner |
| --- | --- | --- | --- | --- | --- |
| Workflow mode | User correction in this thread | Auto Mode for one issue-creation workflow; stop before implementation | Allows issue/spec/plan/mirror creation without more route prompts | No | Main thread |
| Milestone owner | Historical #407 M6 routing | M4 owns this issue because #407 routes solver/API defects to M4 | Prevents M6 validation issue from absorbing route behavior | No | Main thread |
| Parameter ownership | #338 body and project context | M5 #338 owns fitted Khudaida parameter work | Keeps this issue focused on truthful route acceptance and diagnosis | No | Main thread |
| Bug metric | Current retained Figure 2 rows | `phase_distance < 1.0e-3` is collapsed for Khudaida reproduction | Gives checker a concrete failure threshold | No | Implementing agent |
| Completion target | User request and project context | Reject collapsed splits and debug branch convergence; do not require hidden parameter fitting | Lets issue complete with honest M4 diagnosis when #338 remains required | No | Implementing agent |
| TDD policy | Project plan rules | Required | Forces red-green proof for checker and route behavior | No | Implementing agent |

## Acceptance Criteria

- [ ] The checker classifies collapsed finite public-route rows as `model_row_failures` with tie-line id, phase distance, beta values, objective, statuses, and root cause.
- [ ] Figure 2 ties 1-5 and 8 are no longer counted as accepted model rows while their phase distance remains `O(1e-8)` and minor beta remains `O(1e-5)`.
- [ ] The public `electrolyte_lle` route diagnostics explain why the current row converges to the trivial branch: branch-selection defect, route/postsolve acceptance defect, or current-parameter noncollapsed infeasibility.
- [ ] If the route can produce a noncollapsed split with the retained parameter bundle, regenerated Figure 2 model rows retain noncollapsed phase distances and pass focused route tests.
- [ ] If retained parameters cannot produce a noncollapsed residual-feasible split, the checker fails loudly with a #338-owned root-cause payload and no M4 hidden parameter edits.
- [ ] Regenerated Figure 2 artifacts retain source data, feed provenance, route diagnostics, and fit statistics consistent with the new row classification.
- [ ] No public capability text claims full Khudaida reproduction while any model row is collapsed or #338-owned.

## Non-goals

- No M5 regression implementation.
- No changes to Khudaida source Table 3 or Table 4 data.
- No changes to issue #407's retained source provenance except clarifying the collapsed-model diagnosis.
- No downstream metrics or release readiness claims.

## Proof Oracle

```bash
KHUDAIDA_FORCE_RECOMPUTE=1 uv run --no-sync python analyses/paper_validation/2026_khudaida/figures/figure_02/scripts/generate_data.py
uv run --no-sync python analyses/paper_validation/2026_khudaida/figures/figure_02/scripts/render_figure.py
uv run --no-sync python scripts/validation/check_khudaida_2026_figure_validation.py --figure figure_02 --require-complete --json
uv run --no-sync python scripts/validation/check_khudaida_2026_figure_validation.py --figure figure_02 --require-complete --require-model-pass --json
uv run --no-sync python -m pytest packages/epcsaft-equilibrium/tests/api/test_khudaida_collapsed_electrolyte_lle_rejection.py -q
uv run --no-sync python -m pytest packages/epcsaft-equilibrium/tests/api/test_khudaida_figure02_public_route_reproduction.py -q
uv run --no-sync python scripts/validate_plan_task_use_cases.py --plan-path docs/superpowers/plans/2026-07-03-m4-equilibrium-khudaida-collapsed-electrolyte-lle-rejection-plan.md
uv run --no-sync python scripts/validate_plan_outcome_proof.py --plan-path docs/superpowers/plans/2026-07-03-m4-equilibrium-khudaida-collapsed-electrolyte-lle-rejection-plan.md
uv run --no-sync python scripts/dev/validate_project.py docs
git diff --check
bash "$HOME/.codex/hooks/codex-cleanup.sh" --repo-root .
```

The `--require-model-pass` command may fail after this issue only when its JSON
failure payload proves noncollapsed rows are blocked by #338-owned parameter
regression. It must not pass with collapsed rows.

### Task 1: Add Collapsed-Row Failure Tests

**Use Cases:**
- A developer reruns the current retained Figure 2 artifacts and sees ties 1-5 and 8 rejected because their public-route rows are collapsed.
- A future route change cannot mark duplicate-feed phases as successful by only setting `converged=True`.
- The test complete metric is executable: `phase_distance < 1.0e-3` and minor beta near `1e-5` classify the current rows as failures.

**Files:**
- Create: `packages/epcsaft-equilibrium/tests/api/test_khudaida_collapsed_electrolyte_lle_rejection.py`
- Modify: `packages/epcsaft-equilibrium/tests/api/test_khudaida_figure02_public_route_reproduction.py`
- Test: `packages/epcsaft-equilibrium/tests/api/test_khudaida_collapsed_electrolyte_lle_rejection.py`

- [ ] **Step 1: Write the failing collapsed-row test**

  Add a test that loads `figure_02/results/data/model_tielines.csv`, groups rows by `tie_line`, and asserts no row group with `status=accepted` has `phase_distance < 1.0e-3` or both phase compositions within `1.0e-3` infinity norm.

- [ ] **Step 2: Run the focused test and verify it fails on current artifacts**

  Run:

  ```bash
  uv run --no-sync python -m pytest packages/epcsaft-equilibrium/tests/api/test_khudaida_collapsed_electrolyte_lle_rejection.py -q
  ```

  Expected failure: the assertion names Figure 2 tie-lines 1-5 and 8 as collapsed accepted rows.

- [ ] **Step 3: Tighten the existing Figure 2 artifact test**

  Update the existing artifact test so `converged=True` rows must satisfy the Khudaida noncollapsed threshold before they can count toward accepted model rows. Keep the source row, feed row, status, exact-Hessian, and fit-statistics checks.

- [ ] **Step 4: Run both focused tests and keep the expected red state**

  Run:

  ```bash
  uv run --no-sync python -m pytest packages/epcsaft-equilibrium/tests/api/test_khudaida_collapsed_electrolyte_lle_rejection.py packages/epcsaft-equilibrium/tests/api/test_khudaida_figure02_public_route_reproduction.py -q
  ```

  Expected: both tests expose the current collapsed-row acceptance defect before implementation.

- [ ] **Step 5: Commit the red tests**

  Commit after confirming the tests fail for the intended reason.

### Task 2: Make The Khudaida Checker Reject Collapsed Rows

**Use Cases:**
- `check_khudaida_2026_figure_validation.py --figure figure_02 --json` reports collapsed row details in `model_row_failures`.
- `--require-model-pass` cannot pass when rows are collapsed, even if fit-statistics already report high AAD.
- Fit-statistics `failure_reasons` identify collapse separately from non-convergence.

**Files:**
- Modify: `scripts/validation/check_khudaida_2026_figure_validation.py`
- Modify: `analyses/paper_validation/2026_khudaida/scripts/_common.py`
- Test: `packages/epcsaft-equilibrium/tests/api/test_khudaida_collapsed_electrolyte_lle_rejection.py`

- [ ] **Step 1: Add checker constants**

  Add named constants for `KHUDAIDA_MIN_PHASE_DISTANCE = 1.0e-3` and `KHUDAIDA_MINOR_BETA_REVIEW = 1.0e-4` in the checker or shared Khudaida helper.

- [ ] **Step 2: Add collapsed-row classification**

  Extend `_model_row_failures` so finite, converged rows fail when paired phase compositions are closer than `1.0e-3`. Include `failure_kind="collapsed_split"`, `phase_distance_threshold`, `beta_organic`, `beta_aqueous`, `postsolve_accepted`, and route statuses.

- [ ] **Step 3: Preserve failed-row information in fit statistics**

  Update `_common.py` so regenerated `fit_statistics.csv` includes `collapsed_split` entries in `failed_tie_lines` and `failure_reasons` instead of only `objective=...;phase_distance=...`.

- [ ] **Step 4: Run checker JSON and inspect the payload**

  Run:

  ```bash
  uv run --no-sync python scripts/validation/check_khudaida_2026_figure_validation.py --figure figure_02 --require-complete --json
  ```

  Expected: `artifact_complete=true`, `model_reproduction_complete=false`, and `model_row_failures` names collapsed ties.

- [ ] **Step 5: Run model-pass gate and verify it fails loudly**

  Run:

  ```bash
  uv run --no-sync python scripts/validation/check_khudaida_2026_figure_validation.py --figure figure_02 --require-complete --require-model-pass --json
  ```

  Expected: exit code `2` while collapsed rows remain.

- [ ] **Step 6: Commit the checker repair**

  Commit after the checker fails for collapsed rows instead of silently accepting them.

### Task 3: Diagnose Public Route Branch Selection

**Use Cases:**
- A maintainer can tell whether the current failure is branch discovery, postsolve acceptance, or parameter infeasibility.
- The midpoint-feed probe is retained as evidence that collapse is not only caused by the traced figure feed points.
- Route diagnostics include enough data for #338 if fitted parameters are the remaining blocker.

**Files:**
- Modify: `analyses/paper_validation/2026_khudaida/scripts/_common.py`
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/workflows.py`
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/core/native_results.py`
- Modify: `packages/epcsaft-equilibrium/native/equilibrium/core/two_phase_eos_route.cpp`
- Test: `packages/epcsaft-equilibrium/tests/api/test_khudaida_collapsed_electrolyte_lle_rejection.py`

- [ ] **Step 1: Add a retained diagnosis payload**

  Add per-row diagnostic fields for selected seed, candidate feed source, minimum requested phase distance, measured phase distance, beta values, pressure residual, neutral transfer residual, mean ionic transfer residual, and rejection reason.

- [ ] **Step 2: Reproduce traced-feed and midpoint-feed collapse**

  Run a focused diagnostic script or test path that solves Figure 2 tie-line 1 with the traced feed and the Table 3 endpoint midpoint. Retain the output in the test log or generated CSV diagnostics.

- [ ] **Step 3: Inspect route/postsolve acceptance ownership**

  Trace whether the public route is accepting the row in Python result conversion, native result building, or native two-phase route postsolve. Record the exact owner before editing.

- [ ] **Step 4: Classify the root cause**

  Use these concrete buckets:
  - `branch_selection`: noncollapsed candidate exists but the route selects the collapsed point.
  - `postsolve_acceptance`: postsolve accepts a collapsed point under a Khudaida model-row contract.
  - `parameter_regression`: noncollapsed candidates are residual-infeasible with the retained parameter bundle and #338 owns the next fit.

- [ ] **Step 5: Commit the diagnostic evidence**

  Commit only diagnostics needed by the acceptance proof and route repair.

### Task 4: Repair The M4-Owned Route Or Assign The M5 Blocker

**Use Cases:**
- If branch selection is defective, the public route returns a noncollapsed split or rejects collapsed candidates before result conversion.
- If postsolve acceptance is too weak for Khudaida rows, public result diagnostics still expose solver success but model rows are rejected for reproduction.
- If parameter regression is the root cause, M4 closes with a truthful failing checker and #338 remains the next owner.

**Files:**
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/workflows.py`
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/core/native_results.py`
- Modify: `packages/epcsaft-equilibrium/native/equilibrium/core/two_phase_eos_route.cpp`
- Modify: `analyses/paper_validation/2026_khudaida/scripts/_common.py`
- Test: focused tests from Tasks 1-3

- [ ] **Step 1: Implement the smallest M4-owned repair**

  If root cause is branch selection or postsolve acceptance, update the route owner so collapsed candidates cannot be exposed as accepted LLE model rows under the Khudaida public-route contract.

- [ ] **Step 2: Preserve exact diagnostics**

  Keep solver status, application status, postsolve status, phase distance, beta values, and residual norms visible in returned diagnostics and retained CSVs.

- [ ] **Step 3: Route parameter failure to #338 when proven**

  If retained parameters are the blocker, write the generated diagnosis so #338 receives noncollapsed infeasibility evidence and this issue does not modify parameter files.

- [ ] **Step 4: Run focused tests**

  Run:

  ```bash
  uv run --no-sync python -m pytest packages/epcsaft-equilibrium/tests/api/test_khudaida_collapsed_electrolyte_lle_rejection.py packages/epcsaft-equilibrium/tests/api/test_khudaida_figure02_public_route_reproduction.py -q
  ```

  Expected: collapsed rows are rejected, or noncollapsed rows pass with retained diagnostics.

- [ ] **Step 5: Commit the route repair or blocker assignment**

  Commit the minimal M4-owned change and retained evidence.

### Task 5: Regenerate Figure 2 Artifacts And Validate

**Use Cases:**
- Retained Figure 2 artifacts no longer imply that collapsed rows are successful model evidence.
- Source data and feed ratios remain unchanged.
- The issue closeout can explain exactly whether the next work is route repair complete or #338 parameter regression.

**Files:**
- Modify: `analyses/paper_validation/2026_khudaida/figures/figure_02/results/data/model_tielines.csv`
- Modify: `analyses/paper_validation/2026_khudaida/figures/figure_02/results/data/feed_compositions.csv`
- Modify: `analyses/paper_validation/2026_khudaida/figures/figure_02/results/data/experimental_tielines.csv`
- Modify: `analyses/paper_validation/2026_khudaida/figures/figure_02/results/fit_statistics.csv`
- Modify: `analyses/paper_validation/2026_khudaida/figures/figure_02/results/model_curve.csv`
- Modify: `analyses/paper_validation/2026_khudaida/figures/figure_02/results/plotted_data.csv`
- Modify: `analyses/paper_validation/2026_khudaida/figures/figure_02/results/figure_02.svg`
- Modify: `analyses/paper_validation/2026_khudaida/figures/figure_02/results/figure_02.png`
- Modify: `analyses/paper_validation/2026_khudaida/figures/figure_02/results/figure_02.pdf`
- Modify: `analyses/paper_validation/2026_khudaida/figures/figure_02/source/source_notes.csv`

- [ ] **Step 1: Regenerate Figure 2 data**

  Run:

  ```bash
  KHUDAIDA_FORCE_RECOMPUTE=1 uv run --no-sync python analyses/paper_validation/2026_khudaida/figures/figure_02/scripts/generate_data.py
  ```

- [ ] **Step 2: Render Figure 2**

  Run:

  ```bash
  uv run --no-sync python analyses/paper_validation/2026_khudaida/figures/figure_02/scripts/render_figure.py
  ```

- [ ] **Step 3: Run checker gates**

  Run the checker commands from the proof oracle and confirm the JSON matches the accepted outcome: noncollapsed pass or #338-owned loud failure.

- [ ] **Step 4: Run docs and diff checks**

  Run:

  ```bash
  uv run --no-sync python scripts/dev/validate_project.py docs
  git diff --check
  ```

- [ ] **Step 5: Run cleanup hook**

  Run:

  ```bash
  bash "$HOME/.codex/hooks/codex-cleanup.sh" --repo-root .
  ```

- [ ] **Step 6: Commit final artifacts**

  Commit regenerated artifacts, tests, checker changes, and diagnostic docs with a message that names the collapsed-row rejection.
