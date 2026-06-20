# Gross 2002 Figures 6-7 Supercritical VLE Curves Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fully replicate Gross/Sadowski 2002 Figures 6 and 7 as source-backed, paper-scale supercritical-partner VLE plots with retained source data, model curves generated only through existing public routes, scorecards, and checker evidence.

**Architecture:** Keep #282 in the figure-replication lane: figure-owned source files, generation scripts, rendered plots, score JSON, shared manifest updates, issue mirror/docs updates, and validation checks. Generation scripts may call existing public `epcsaft_equilibrium.Equilibrium(...).solve()` routes, but route admission or native solver gaps are blockers that must be split out of this PR. The worker must not edit package implementation, native C++, headers, CMake, or package tests.

**Tech Stack:** Python stdlib CSV/JSON/pathlib, pandas, matplotlib, yaml, existing `epcsaft` and `epcsaft_equilibrium` public APIs, retained Gross 2002 paper images and tables, `scripts/validation/check_gross_2002_full_replication.py`, pytest through `run_pytest.py`, Sphinx docs validation, GitHub issue mirrors, and the repo cleanup hook.

---

## Intake

- Source spec: `docs/superpowers/specs/2026-06-19-m4-equilibrium-gross-2002-full-figure-replication.md`
- Issue mirror: `docs/superpowers/issues/2026-06-19-m4-equilibrium-issue-0282-fully-replicate-gross-2002-figures-6-7-supercritical-partner-vle-curves.md`
- GitHub issue: `https://github.com/ePC-SAFT/ePC-SAFT/issues/282`
- Milestone: `M4 - Equilibrium`
- Package owner: `packages/epcsaft-equilibrium`
- Capability: `association`
- Backend: `Ipopt`
- Validation root: `analyses/paper_validation/2002_gross/figures`
- Foundation issue: #279, merged through PR #288
- Prior figure issue: #280, merged through PR #289
- Parallel queue note: #281 is blocked by #292 for model-curve generation. #282 may proceed only as figure-replication work and must stop if it hits the same route gap.

## Planning Resolution

- Figure 6 source identity: Gross 2002 Figure 6 is `1-butanol-n-butane` at four visible temperature series: `T=60 degC`, `T=100 degC`, `T=160 degC`, and `T=200 degC`; PC-SAFT `k_ij = 0.015`, SAFT `k_ij = 0.025`; experimental source reference 26.
- Figure 7 source identity: Gross 2002 Figure 7 is `ethanol-n-butane` at four visible temperature series: `T=100 degC`, `T=140 degC`, `T=160 degC`, and `T=190 degC`; PC-SAFT `k_ij = 0.028`, SAFT `k_ij = 0.021`; experimental source reference 26.
- Supercritical caveat: Gross 2002 text says mixtures with one compound above its critical point are shown in Figures 6 and 7, notes SAFT vapor-pressure deficiencies for butane at higher temperatures, and records that a subcritical system is predicted at `160 degC` although the butane critical point is about 8 K lower. Figure 7 must retain this caveat in metadata and summary evidence.
- Source policy: try to extract cited reference-26 data when it is available in bounded local evidence; otherwise use calibrated digitization from the retained Gross 2002 paper images with QA overlays and recorded uncertainty.
- Route policy: model generation must use existing public equilibrium routes only. If the route rejects associating alcohol plus n-butane VLE, or lacks exact association-Hessian/fresh-native receipts, stop the model-generation task and report the blocker; do not implement admission, derivatives, selectors, native code, or package tests here.
- Metrics: inherit the #279 VLE normalized plot score gate of `>= 7.0`, exact association derivative status `verified_exact`, native freshness evidence, and complete required-series coverage.
- Branch strategy: use the issue mirror branch `codex/issue-0282-gross-2002-figures-6-7-vle-curves`.
- Execution route: worker-thread orchestration after this plan is committed and the issue mirror points to it.

## Test Complete And Metrics

Test complete for #282 means:

- Figures 6 and 7 are `accepted` in `analyses/paper_validation/2002_gross/shared/gross_2002_full_replication_manifest.json`.
- Every accepted Figure 6/7 record has `counts_toward_completion: true`, empty `remaining_work`, and retained artifact paths for `source_csv`, `source_metadata_json`, `digitization_qa_overlay`, `model_csv`, `plotted_csv`, `score_json`, `summary_json`, `png`, `svg`, and `sidecar`.
- Figure 6 has required series `T_60C`, `T_100C`, `T_160C`, and `T_200C`.
- Figure 7 has required series `T_100C`, `T_140C`, `T_160C`, and `T_190C`.
- Every figure-level score JSON records `source_point_count`, `model_point_count`, `rmse_axis`, `max_axis_error`, `normalized_plot_score`, `branch_coverage_score`, `derivative_status`, `native_freshness`, and `pass`.
- Every required temperature series has `normalized_plot_score >= 7.0`, `branch_coverage_score == 1.0`, `derivative_status: "verified_exact"`, `native_freshness: "fresh_native"`, and `pass: true`.
- Source metadata records provenance, axis calibration, units, temperature labels, symbol mapping, digitization uncertainty, QA overlay path, component/order basis, and the reference-26 source citation.
- Figure 7 summary records the supercritical-partner caveat from the Gross 2002 text.
- The rendered PNG/SVG plots match the paper `P-x_Butane` axis family and pressure scale for each figure.
- `scripts/validation/check_gross_2002_full_replication.py --json --require-exact-association-hessian --require-fresh-native` exits `0` with Figures 6 and 7 accepted and no blockers for Figures 6/7. A separate full-campaign readout with `--require-complete` is expected to exit `2` until every child issue in #286 closes.

## Outcome Proof

**Intent:** Convert Figures 6 and 7 from source-requirement records into curve-level Gross 2002 supercritical-partner VLE replications.
**Current Behavior:** Figures 6 and 7 are planned records with source images, captions, and Table 2 `k_ij` rows, but no retained source CSVs, model curves, paper-scale plots, score JSON, or accepted checker evidence.
**Expected Outcome:** Figures 6 and 7 are accepted with retained source, model, plotted, score, summary, PNG, SVG, sidecar, native receipt, exact association-Hessian, and supercritical-caveat artifacts.
**Target Output:** A reviewer can open the two generated plots, compare PC-SAFT curves against retained source markers in paper coordinates, and inspect score JSON plus source/model CSVs behind each temperature series.
**Owner:** Figure-replication artifacts under `analyses/paper_validation/2002_gross`, shared validation manifests under the same analysis root, and M4 issue/docs metadata.
**Interface:** `scripts/validation/check_gross_2002_full_replication.py`, the #279 score/source metadata schemas, and public `epcsaft_equilibrium.Equilibrium(...).solve()` workflows used by the generation scripts.
**Cutover:** Move a figure from `planned` to `accepted` only after its source/model/score/plot artifacts pass the checker and its temperature-series/caveat evidence is retained.
**Replaced Path:** Replace source-image-only Figure 6/7 records with retained curve-level replication artifacts; do not treat source images, captions, or diagnostic plots as completion evidence.
**Evidence:** Figure-owned source/model/plot artifacts, shared manifest/summary updates, full-replication checker output, association acceptance checker output, docs validation, `git diff --check`, cleanup hook, and final rendered plot handoff.
**Acceptance Proof:** Passing proof oracle commands plus final handoff rendering Figures 6 and 7 inline with a compact table of source row counts, model row counts, scores, derivative status, native freshness, and pass state for each temperature series.
**Stop Criteria:** Stop the worker route and report a prerequisite issue if existing public routes cannot generate any required Figure 6/7 model curve with exact association-Hessian and fresh-native receipts.
**Avoid:** Do not edit `packages/**`, C++ sources, headers, CMake, package tests, native route selectors, provider EOS code, electrolyte/reactive routes, or broad capability claims. Do not lower score thresholds or accept unscored plots.
**Risk:** If route gaps are hidden inside this figure PR, the project loses the separation between validation evidence and package implementation; if digitization is weak, the plot-match scores may overstate model agreement.

## Implementation Boundaries

**Files To Create:** Figure-owned source, script, and result files under `analyses/paper_validation/2002_gross/figures/figure_06` and `analyses/paper_validation/2002_gross/figures/figure_07`, including source CSV, metadata JSON, QA overlay PNG, generator script, model CSV, plotted CSV, score JSON, summary JSON, PNG, SVG, and MPL sidecar artifacts.
**Files To Modify:** `scripts/validation/check_gross_2002_full_replication.py`, `tests/native/contracts/test_gross_2002_full_replication_checker.py`, `analyses/paper_validation/2002_gross/shared/gross_2002_full_replication_manifest.json`, `analyses/paper_validation/2002_gross/shared/results/gross_2002_full_replication_summary.json`, `analyses/paper_validation/2002_gross/shared/results/gross_2002_full_replication_summary.csv`, the #282 issue mirror, and `docs/superpowers/milestones/M4-equilibrium/README.md`.
**Files To Avoid:** `packages/**`, `**/*.cpp`, `**/*.hpp`, `CMakeLists.txt`, package-local tests, provider EOS code, regression code, electrolyte/reactive route files, downstream repositories, and Gross 2002 figure folders outside Figures 6 and 7 except shared summary files.
**Source Of Truth:** Gross/Sadowski 2002 Figures 6 and 7 images/captions, Gross 2002 Table 1, Gross 2002 Table 2, source reference 26, analysis-local parameter snapshots, and the #279 full-replication checker schema.
**Read Path:** Source CSV and metadata feed generation; model CSV and source CSV feed rendering; score/summary JSON feed manifest and checker aggregation.
**Write Path:** Figure-specific artifacts stay under each `figure_NN` folder; shared status artifacts stay under `analyses/paper_validation/2002_gross/shared`.
**Integration Points:** Public equilibrium route calls in figure-local scripts, exact association derivative diagnostics in public result metadata, full-replication checker, M4 milestone evidence table, and GitHub issue mirror.
**Migration Or Cutover:** Remove owned `_placeholder.md` files from a figure's `scripts` or `results` folder only after real files occupy that folder.
**Replaced Path Handling:** Preserve source images as provenance inputs while replacing source-image-only completion state with scored, retained curve-level artifacts.
**Acceptance Proof Gate:** The worker cannot mark #282 PR-ready until Figures 6 and 7 are accepted by the full-replication checker and the final handoff renders both new plots inline.

## Acceptance Coverage

- Retain source data, metadata, and QA overlays for every Figure 6/7 temperature series: Tasks 2 and 4.
- Generate matching PC-SAFT model curves for every temperature series through existing public routes only: Tasks 3 and 5.
- Render paper-scale mirror plots with labels matching the paper: Tasks 3 and 5.
- Write score JSON per temperature series and figure: Tasks 1, 3, and 5.
- Record the supercritical-partner caveat and evidence-scoped capability text: Tasks 4 and 6.
- Keep package/native implementation out of the figure PR: Tasks 3, 5, and 7.

## Non-Goals

- No `packages/**` changes.
- No C++/header/CMake/native route implementation.
- No package-local test changes.
- No electrolyte, reactive, CE, CPE, or generalized phase-count admission.
- No broad associating-family capability claim beyond the Figure 6/7 evidence proven here.
- No changes to Figures 2-5 or Figures 8-10 beyond shared campaign summary state.

### Task 1: Add Figure 6/7 Series And Caveat Checker Gates

**Use Cases:**
- An accepted Figure 6 record fails if any required temperature series score is absent.
- An accepted Figure 7 record fails if the supercritical-partner caveat is absent from the figure summary.
- The checker can report Figure 6/7 blockers without marking the full Gross 2002 campaign complete.
- Planned Figure 6/7 records remain allowed while source acquisition is still in progress.

**Files:**
- Modify: `scripts/validation/check_gross_2002_full_replication.py`
- Modify: `tests/native/contracts/test_gross_2002_full_replication_checker.py`
- Modify: `analyses/paper_validation/2002_gross/shared/gross_2002_full_replication_manifest.json`
- Test: `tests/native/contracts/test_gross_2002_full_replication_checker.py`

- [ ] **Step 1: Add failing tests for required temperature series and caveat**

  Add tests that accepted Figure 6 fails without one of `T_60C`, `T_100C`, `T_160C`, `T_200C`, and accepted Figure 7 fails without one of `T_100C`, `T_140C`, `T_160C`, `T_190C` or without a retained supercritical caveat field in the summary JSON.

- [ ] **Step 2: Run targeted tests and verify expected failure**

  Run:

  ```powershell
  uv run --no-sync python run_pytest.py tests/native/contracts/test_gross_2002_full_replication_checker.py::test_accepted_vle_figures_require_all_series_scores -q
  ```

  Expected before implementation: failure because Figure 6/7 required-series and caveat validation is not yet enforced.

- [ ] **Step 3: Implement strict validation**

  Require every accepted Figure 6/7 record to include `required_series`, require every listed token to exist in `score_json["series_scores"]`, and require Figure 7 summary JSON to retain `supercritical_partner_caveat`.

- [ ] **Step 4: Update planned manifest records**

  Add Figure 6 required series `["T_60C", "T_100C", "T_160C", "T_200C"]`, Figure 7 required series `["T_100C", "T_140C", "T_160C", "T_190C"]`, source captions, PC-SAFT `k_ij` values, and reference-26 provenance to the manifest records while keeping both figures `planned`.

- [ ] **Step 5: Run checker tests**

  Run:

  ```powershell
  uv run --no-sync python run_pytest.py tests/native/contracts/test_gross_2002_full_replication_checker.py -q
  ```

  Expected: checker tests pass.

- [ ] **Step 6: Commit**

  Commit:

  ```powershell
  git add scripts/validation/check_gross_2002_full_replication.py tests/native/contracts/test_gross_2002_full_replication_checker.py analyses/paper_validation/2002_gross/shared/gross_2002_full_replication_manifest.json
  git commit -m "Require Gross 2002 Figure 6 and 7 series scores"
  ```

### Task 2: Retain Figure 6 Source Data And Metadata

**Use Cases:**
- Figure 6 source points are traceable to reference 26 or calibrated image digitization.
- The retained source data preserves all four temperature series.
- Axis calibration, pressure units, composition basis, and symbol mapping are reviewable.
- The QA overlay makes point extraction visible.

**Files:**
- Create: `analyses/paper_validation/2002_gross/figures/figure_06/source/gross_2002_figure_06_replication_source_points.csv`
- Create: `analyses/paper_validation/2002_gross/figures/figure_06/source/gross_2002_figure_06_replication_digitization_metadata.json`
- Create: `analyses/paper_validation/2002_gross/figures/figure_06/source/gross_2002_figure_06_replication_digitization_qa_overlay.png`

- [ ] **Step 1: Extract or digitize Figure 6 points**

  Produce a source CSV with columns:

  ```text
  figure_id,series,system,T_C,T_K,P_bar,x_butane,source_kind,source_reference,digitized_x_px,digitized_y_px,uncertainty_P_bar,uncertainty_composition
  ```

- [ ] **Step 2: Write metadata**

  Record the Gross 2002 caption, reference 26 citation, `k_ij = 0.015`, component order, axis calibration, units, series labels, symbol mapping, digitization uncertainty, and QA overlay path.

- [ ] **Step 3: Save the QA overlay**

  Save the overlay showing the Figure 6 image, calibration anchors, series markers, and extracted points.

- [ ] **Step 4: Verify row coverage**

  Run:

  ```powershell
  uv run --no-sync python -c "import pandas as pd; f=pd.read_csv('analyses/paper_validation/2002_gross/figures/figure_06/source/gross_2002_figure_06_replication_source_points.csv'); print(f.groupby('series').size().to_string())"
  ```

  Expected: all four Figure 6 required source series are present.

- [ ] **Step 5: Commit**

  Commit:

  ```powershell
  git add analyses/paper_validation/2002_gross/figures/figure_06/source
  git commit -m "Retain Gross 2002 Figure 6 VLE source points"
  ```

### Task 3: Generate And Render Figure 6 Model Curves

**Use Cases:**
- Figure 6 model data covers all four temperature series.
- The plotted figure uses paper `P-x_Butane` axes and not a diagnostic substitute.
- Score JSON proves per-series agreement against source points.
- The generation output records native freshness and exact association derivative status.
- A public-route gap stops the task without package/native edits.

**Files:**
- Create: `analyses/paper_validation/2002_gross/figures/figure_06/scripts/generate_gross_2002_figure_06_replication.py`
- Create: `analyses/paper_validation/2002_gross/figures/figure_06/results/gross_2002_figure_06_replication_model_curve.csv`
- Create: `analyses/paper_validation/2002_gross/figures/figure_06/results/gross_2002_figure_06_replication_plotted_data.csv`
- Create: `analyses/paper_validation/2002_gross/figures/figure_06/results/gross_2002_figure_06_replication_score.json`
- Create: `analyses/paper_validation/2002_gross/figures/figure_06/results/gross_2002_figure_06_replication_summary.json`
- Create: `analyses/paper_validation/2002_gross/figures/figure_06/results/gross_2002_figure_06_replication.png`
- Create: `analyses/paper_validation/2002_gross/figures/figure_06/results/gross_2002_figure_06_replication.svg`
- Create: `analyses/paper_validation/2002_gross/figures/figure_06/results/gross_2002_figure_06_replication.mpl.yaml`
- Delete: `analyses/paper_validation/2002_gross/figures/figure_06/scripts/_placeholder.md` if real scripts occupy the folder.
- Delete: `analyses/paper_validation/2002_gross/figures/figure_06/results/_placeholder.md` if real results occupy the folder.

- [ ] **Step 1: Write the generator**

  The script must read Figure 6 source points, metadata, Gross Table 1, Table 2, `k_ij = 0.015`, analysis-local pure/mixed parameter snapshots, and public equilibrium routes only.

- [ ] **Step 2: Stop cleanly on route gaps**

  Before writing result artifacts, probe each required public model route. If any route rejects the system, lacks fresh-native evidence, or lacks exact association-Hessian metadata, stop with a clear blocker message naming the missing route evidence and do not edit `packages/**`.

- [ ] **Step 3: Generate four temperature-series curves**

  Generate PC-SAFT VLE data for `T_60C`, `T_100C`, `T_160C`, and `T_200C` with coordinates matching the retained source CSV.

- [ ] **Step 4: Score all series**

  Write `series_scores` for every temperature series plus top-level #279 score fields.

- [ ] **Step 5: Render the plot**

  Render source markers and PC-SAFT curves on a paper-scale `P-x_Butane` plot.

- [ ] **Step 6: Run generation**

  Run:

  ```powershell
  uv run --no-sync python analyses/paper_validation/2002_gross/figures/figure_06/scripts/generate_gross_2002_figure_06_replication.py
  ```

  Expected: all Figure 6 result artifacts are written and each required series passes, or the script stops before artifacts with a route-gap blocker that must become a separate prerequisite issue.

- [ ] **Step 7: Commit**

  Commit only if model generation succeeds:

  ```powershell
  git add analyses/paper_validation/2002_gross/figures/figure_06
  git commit -m "Replicate Gross 2002 Figure 6 VLE curves"
  ```

### Task 4: Retain Figure 7 Source Data, Metadata, And Caveat

**Use Cases:**
- Figure 7 source points are traceable to reference 26 or calibrated image digitization.
- The retained source data preserves all four temperature series.
- Metadata records the butane critical behavior caveat from the paper text.
- Axis calibration, pressure units, composition basis, and symbol mapping are reviewable.

**Files:**
- Create: `analyses/paper_validation/2002_gross/figures/figure_07/source/gross_2002_figure_07_replication_source_points.csv`
- Create: `analyses/paper_validation/2002_gross/figures/figure_07/source/gross_2002_figure_07_replication_digitization_metadata.json`
- Create: `analyses/paper_validation/2002_gross/figures/figure_07/source/gross_2002_figure_07_replication_digitization_qa_overlay.png`

- [ ] **Step 1: Extract or digitize Figure 7 points**

  Produce a source CSV with columns:

  ```text
  figure_id,series,system,T_C,T_K,P_bar,x_butane,source_kind,source_reference,digitized_x_px,digitized_y_px,uncertainty_P_bar,uncertainty_composition
  ```

- [ ] **Step 2: Write metadata**

  Record the Gross 2002 caption, reference 26 citation, `k_ij = 0.028`, component order, axis calibration, units, series labels, symbol mapping, digitization uncertainty, QA overlay path, and `supercritical_partner_caveat`.

- [ ] **Step 3: Save the QA overlay**

  Save the overlay showing the Figure 7 image, calibration anchors, series markers, and extracted points.

- [ ] **Step 4: Verify row coverage**

  Run:

  ```powershell
  uv run --no-sync python -c "import pandas as pd; f=pd.read_csv('analyses/paper_validation/2002_gross/figures/figure_07/source/gross_2002_figure_07_replication_source_points.csv'); print(f.groupby('series').size().to_string())"
  ```

  Expected: all four Figure 7 required source series are present.

- [ ] **Step 5: Commit**

  Commit:

  ```powershell
  git add analyses/paper_validation/2002_gross/figures/figure_07/source
  git commit -m "Retain Gross 2002 Figure 7 VLE source points"
  ```

### Task 5: Generate And Render Figure 7 Model Curves

**Use Cases:**
- Figure 7 model data covers all four temperature series.
- Score JSON reports a pass/fail result per temperature series.
- The rendered plot preserves the paper axis family, labels, and supercritical-partner context.
- Native and exact derivative receipts are retained.
- A public-route gap stops the task without package/native edits.

**Files:**
- Create: `analyses/paper_validation/2002_gross/figures/figure_07/scripts/generate_gross_2002_figure_07_replication.py`
- Create: `analyses/paper_validation/2002_gross/figures/figure_07/results/gross_2002_figure_07_replication_model_curve.csv`
- Create: `analyses/paper_validation/2002_gross/figures/figure_07/results/gross_2002_figure_07_replication_plotted_data.csv`
- Create: `analyses/paper_validation/2002_gross/figures/figure_07/results/gross_2002_figure_07_replication_score.json`
- Create: `analyses/paper_validation/2002_gross/figures/figure_07/results/gross_2002_figure_07_replication_summary.json`
- Create: `analyses/paper_validation/2002_gross/figures/figure_07/results/gross_2002_figure_07_replication.png`
- Create: `analyses/paper_validation/2002_gross/figures/figure_07/results/gross_2002_figure_07_replication.svg`
- Create: `analyses/paper_validation/2002_gross/figures/figure_07/results/gross_2002_figure_07_replication.mpl.yaml`
- Delete: `analyses/paper_validation/2002_gross/figures/figure_07/scripts/_placeholder.md` if real scripts occupy the folder.
- Delete: `analyses/paper_validation/2002_gross/figures/figure_07/results/_placeholder.md` if real results occupy the folder.

- [ ] **Step 1: Write the generator**

  The script must read Figure 7 source points, metadata, Gross Table 1, Table 2, `k_ij = 0.028`, analysis-local pure/mixed parameter snapshots, and public equilibrium routes only.

- [ ] **Step 2: Stop cleanly on route gaps**

  Before writing result artifacts, probe each required public model route. If any route rejects the system, lacks fresh-native evidence, or lacks exact association-Hessian metadata, stop with a clear blocker message naming the missing route evidence and do not edit `packages/**`.

- [ ] **Step 3: Generate four temperature-series curves**

  Generate PC-SAFT VLE data for `T_100C`, `T_140C`, `T_160C`, and `T_190C` with coordinates matching the retained source CSV.

- [ ] **Step 4: Score all series**

  Write `series_scores` for every temperature series plus top-level #279 score fields and the retained `supercritical_partner_caveat`.

- [ ] **Step 5: Render the plot**

  Render source markers and PC-SAFT curves on a paper-scale `P-x_Butane` plot.

- [ ] **Step 6: Run generation**

  Run:

  ```powershell
  uv run --no-sync python analyses/paper_validation/2002_gross/figures/figure_07/scripts/generate_gross_2002_figure_07_replication.py
  ```

  Expected: all Figure 7 result artifacts are written and each required series passes, or the script stops before artifacts with a route-gap blocker that must become a separate prerequisite issue.

- [ ] **Step 7: Commit**

  Commit only if model generation succeeds:

  ```powershell
  git add analyses/paper_validation/2002_gross/figures/figure_07
  git commit -m "Replicate Gross 2002 Figure 7 VLE curves"
  ```

### Task 6: Accept Figures 6-7 And Verify Partial Campaign State

**Use Cases:**
- The checker recognizes Figures 6 and 7 as accepted without pretending the full campaign is complete.
- Shared summaries show the current accepted figure set and later blockers accurately.
- M4 README records the new evidence and keeps broader capability claims evidence-scoped.
- The live issue body and mirror point to this plan.

**Files:**
- Modify: `analyses/paper_validation/2002_gross/shared/gross_2002_full_replication_manifest.json`
- Modify: `analyses/paper_validation/2002_gross/shared/results/gross_2002_full_replication_summary.json`
- Modify: `analyses/paper_validation/2002_gross/shared/results/gross_2002_full_replication_summary.csv`
- Modify: `docs/superpowers/issues/2026-06-19-m4-equilibrium-issue-0282-fully-replicate-gross-2002-figures-6-7-supercritical-partner-vle-curves.md`
- Modify: `docs/superpowers/milestones/M4-equilibrium/README.md`
- Test: `scripts/validation/check_gross_2002_full_replication.py`
- Test: `scripts/validation/check_gross_2002_association_acceptance.py`

- [ ] **Step 1: Update Figure 6/7 manifest records**

  Set Figures 6 and 7 to accepted with artifact paths, score summaries, required series, exact derivative requirement, native freshness requirement, `counts_toward_completion: true`, and empty `remaining_work`.

- [ ] **Step 2: Refresh the shared summary**

  Run:

  ```powershell
  uv run --no-sync python scripts/validation/check_gross_2002_full_replication.py --json --require-foundation --write-summary
  ```

  Expected: shared summary records Figures 6 and 7 accepted while unfinished figure families still report blockers.

- [ ] **Step 3: Run the Figure 6/7 acceptance gate**

  Run:

  ```powershell
  uv run --no-sync python scripts/validation/check_gross_2002_full_replication.py --json --require-exact-association-hessian --require-fresh-native
  ```

  Expected for #282 closeout: exit `0`, Figures 6 and 7 accepted, and no blockers for Figures 6/7.

- [ ] **Step 4: Run the expected partial-campaign readout**

  Run:

  ```powershell
  uv run --no-sync python scripts/validation/check_gross_2002_full_replication.py --json --require-complete --require-exact-association-hessian --require-fresh-native
  ```

  Expected for #282 closeout: exit `2` until every child issue in #286 closes.

- [ ] **Step 5: Run association acceptance regression**

  Run:

  ```powershell
  uv run --no-sync python scripts/validation/check_gross_2002_association_acceptance.py --json --require-complete --require-exact-association-hessian --require-fresh-native
  ```

  Expected: exit `0`, preserving the #275 association acceptance evidence.

- [ ] **Step 6: Update docs and issue mirror**

  Link this plan in the #282 issue mirror and update M4 README retained evidence or queue notes with the Figures 6/7 replication result and plot paths.

- [ ] **Step 7: Sync the live GitHub issue body**

  After local validation, update issue #282 from the corrected local mirror body.

- [ ] **Step 8: Commit**

  Commit:

  ```powershell
  git add analyses/paper_validation/2002_gross/shared/gross_2002_full_replication_manifest.json analyses/paper_validation/2002_gross/shared/results/gross_2002_full_replication_summary.json analyses/paper_validation/2002_gross/shared/results/gross_2002_full_replication_summary.csv docs/superpowers/issues/2026-06-19-m4-equilibrium-issue-0282-fully-replicate-gross-2002-figures-6-7-supercritical-partner-vle-curves.md docs/superpowers/milestones/M4-equilibrium/README.md
  git commit -m "Accept Gross 2002 Figures 6 and 7 replication evidence"
  ```

### Task 7: Final Verification And PR Handoff

**Use Cases:**
- The PR proves #282 without claiming the full Gross 2002 campaign is complete.
- The final handoff renders Figures 6 and 7 inline and includes source/model/score numerics.
- The repo is clean after validation.
- The changed-file inventory proves no package/native implementation files were touched.

**Files:**
- Test: `scripts/validation/check_gross_2002_full_replication.py`
- Test: `scripts/validation/check_gross_2002_association_acceptance.py`
- Test: `tests/native/contracts/test_gross_2002_full_replication_checker.py`

- [ ] **Step 1: Build native equilibrium if model generation reached public route solves**

  Run:

  ```powershell
  uv run --no-sync python scripts/dev/build_epcsaft.py --profile equilibrium --build-only --parallel 4
  ```

- [ ] **Step 2: Run focused checker tests**

  Run:

  ```powershell
  uv run --no-sync python run_pytest.py tests/native/contracts/test_gross_2002_full_replication_checker.py -q
  ```

- [ ] **Step 3: Run campaign checkers**

  Run:

  ```powershell
  uv run --no-sync python scripts/validation/check_gross_2002_full_replication.py --json --require-exact-association-hessian --require-fresh-native
  uv run --no-sync python scripts/validation/check_gross_2002_association_acceptance.py --json --require-complete --require-exact-association-hessian --require-fresh-native
  ```

  Expected: full-replication partial acceptance exits `0`, with Figures 6 and 7 accepted and no Figure 6/7 blockers. Association acceptance exits `0`.

- [ ] **Step 4: Prove no package/native files changed**

  Run:

  ```powershell
  git diff --name-only main...HEAD
  ```

  Expected: no paths under `packages/`, no `*.cpp`, no `*.hpp`, no `CMakeLists.txt`, and no package-local tests.

- [ ] **Step 5: Run docs validation and diff hygiene**

  Run:

  ```powershell
  uv run --no-sync python scripts/dev/validate_project.py docs
  git diff --check
  ```

- [ ] **Step 6: Run cleanup**

  Run:

  ```powershell
  pwsh.exe -NoProfile -ExecutionPolicy Bypass -File "$env:USERPROFILE\.codex\hooks\codex-cleanup.ps1" -RepoRoot .
  ```

- [ ] **Step 7: Prepare PR handoff**

  The handoff must include absolute PNG/SVG paths for Figures 6 and 7, source row counts by figure and series, model row counts by figure and series, score table, derivative/native receipt status, supercritical caveat text, remaining campaign blockers, and the no-package-change proof.

## Proof Oracle

Required pass commands:

```powershell
uv run --no-sync python scripts/dev/build_epcsaft.py --profile equilibrium --build-only --parallel 4
uv run --no-sync python run_pytest.py tests/native/contracts/test_gross_2002_full_replication_checker.py -q
uv run --no-sync python scripts/validation/check_gross_2002_full_replication.py --json --require-exact-association-hessian --require-fresh-native
uv run --no-sync python scripts/validation/check_gross_2002_association_acceptance.py --json --require-complete --require-exact-association-hessian --require-fresh-native
uv run --no-sync python scripts/dev/validate_project.py docs
git diff --check
pwsh.exe -NoProfile -ExecutionPolicy Bypass -File "$env:USERPROFILE\.codex\hooks\codex-cleanup.ps1" -RepoRoot .
```

Required partial-campaign readout:

```powershell
uv run --no-sync python scripts/validation/check_gross_2002_full_replication.py --json --require-complete --require-exact-association-hessian --require-fresh-native
```

Expected for #282: exit `2` until every child issue in #286 closes.

Required scope proof:

```powershell
git diff --name-only main...HEAD
```

Expected for #282: no `packages/**`, no `*.cpp`, no `*.hpp`, no `CMakeLists.txt`, and no package-local test paths.

## Risk Notes

- Figures 6 and 7 use n-butane as a supercritical partner in parts of the plotted range, so route convergence and curve topology may expose production route gaps.
- If the public route gap matches #292, #282 should stop with an explicit blocker and retain only source/digitization artifacts until the prerequisite lands.
- Source digitization quality directly controls scores. Metadata and QA overlays must make calibration reviewable.
- Figure 7 has a paper caveat about butane critical behavior that must be retained rather than smoothed away by the score.
- This issue only moves the Gross 2002 full-replication campaign for Figures 6 and 7. Full campaign completion remains #286.

## Recommended Implementation Route

Use `$superpowers-project:orchestrate-issues` for issue #282 after this plan is committed, the issue mirror points to it, and the worker handoff repeats the no-package/native-edit scope guard.
