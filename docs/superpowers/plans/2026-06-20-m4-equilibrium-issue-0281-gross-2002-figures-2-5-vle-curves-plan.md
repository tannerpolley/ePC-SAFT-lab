# Gross 2002 Figures 2-5 VLE Curves Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fully replicate Gross/Sadowski 2002 Figures 2-5 as source-backed, paper-scale self-associating VLE plots with retained source data, native model curves, scorecards, and checker evidence.

**Architecture:** Consume the merged #279 full-replication checker contract and the merged #280 Figure 1 campaign state, then move Figures 2-5 from planned records to accepted records. Figure-specific scripts retain or digitize source points, generate PC-SAFT VLE model data through the public equilibrium workflow, render paper-scale plots, and write score summaries. Any missing native equilibrium capability discovered during generation must be split into a separate prerequisite issue; this issue owns figure replication artifacts and checker integration.

**Tech Stack:** Python stdlib CSV/JSON/pathlib, pandas, matplotlib, yaml, existing `epcsaft` and `epcsaft_equilibrium` public APIs, native equilibrium Ipopt routes, C++ exact derivative receipts consumed through public result metadata, pytest through `run_pytest.py`, Sphinx docs validation, GitHub issue mirrors, and the repo cleanup hook.

---

## Intake

- Source spec: `docs/superpowers/specs/2026-06-19-m4-equilibrium-gross-2002-full-figure-replication.md`
- Issue mirror: `docs/superpowers/issues/2026-06-19-m4-equilibrium-issue-0281-fully-replicate-gross-2002-figures-2-5-self-associating-vle-curves.md`
- GitHub issue: `https://github.com/ePC-SAFT/ePC-SAFT/issues/281`
- Milestone: `M4 - Equilibrium`
- Package owner: `packages/epcsaft-equilibrium`
- Capability: `association`
- Backend: `Ipopt`
- Validation root: `analyses/paper_validation/2002_gross/figures`
- Foundation issue: #279, merged through PR #288
- Prior campaign issue: #280, merged through PR #289

## Planning Grill Resolution

Material planning questions were answered from repo evidence:

- Scope: #281 owns only Figures 2-5. #282-#285 own the later Gross 2002 figure families, and #286 owns final campaign closure.
- Figure 2 identity: the retained caption says `methanol-isobutane`, Table 2 says `methanol-isobutanol`, and the local parameter snapshot maps the `k_ij = 0.05` row to `methanol` with `2-methyl-2-butanol`. Figure 2 cannot be accepted until a retained identity-resolution artifact names the accepted system and explains the source evidence.
- Source policy: use cited experimental data when it can be extracted in bounded time; otherwise use calibrated digitization from the retained Gross 2002 paper image. Either route must write the required source CSV, metadata JSON, and QA overlay.
- Route policy: #281 must not hide native route admission or solver implementation work inside a figure-replication PR. If a production binary self-associating VLE route is missing for any required figure, create a separate prerequisite issue and keep #281 open until that prerequisite lands.
- Metrics: inherit the #279 `vle` normalized plot score gate of `>= 7.0`, exact association derivative status `verified_exact`, native freshness evidence, and complete required-series coverage.
- Branch strategy: use the issue branch from the mirror, `codex/issue-0281-gross-2002-figures-2-5-vle-curves`.
- Execution route: worker-thread orchestration after this plan is committed and linked to the issue mirror.

## Test Complete And Metrics

Test complete for #281 means:

- Figures 2, 3, 4, and 5 are `accepted` in `analyses/paper_validation/2002_gross/shared/gross_2002_full_replication_manifest.json`.
- Every accepted figure has `counts_toward_completion: true`, empty `remaining_work`, and retained artifact paths for `source_csv`, `source_metadata_json`, `digitization_qa_overlay`, `model_csv`, `plotted_csv`, `score_json`, `summary_json`, `png`, `svg`, and `PDF artifact and provenance file`.
- Figure 2 has `source_identity_status: resolved` and a retained identity artifact under `analyses/paper_validation/2002_gross/figures/figure_02/source/`.
- Every figure-level score JSON records `source_point_count`, `model_point_count`, `rmse_axis`, `max_axis_error`, `normalized_plot_score`, `branch_coverage_score`, `derivative_status`, and `pass`.
- Every required Figure 2-5 series has `normalized_plot_score >= 7.0`, `branch_coverage_score == 1.0`, `derivative_status: "verified_exact"`, and `pass: true`.
- Source metadata records provenance, axis calibration, units, series labels, digitization uncertainty, QA overlay path, and component/order basis.
- Model summaries retain native freshness and exact association derivative receipts for accepted route solves.
- The rendered PNG/SVG plots match the paper plot type and scale for each figure.
- `scripts/validation/check_gross_2002_full_replication.py --json --require-exact-association-hessian --require-fresh-native` exits `0` with Figures 1-5 accepted and no blockers for Figures 2-5. A separate full-campaign readout with `--require-complete` is expected to exit `2` until Figures 6-10 land.

## Outcome Contract

**Intent:** Convert Figures 2-5 from source-requirement records into curve-level Gross 2002 VLE replications.
**Current Behavior:** Figure 1 is accepted; Figures 2-5 remain planned with source images only and named blockers in the shared summary.
**Expected Outcome:** Figures 2-5 are accepted with retained source, model, plotted, score, summary, PNG, SVG, PDF artifact and provenance file, identity, and native receipt artifacts.
**Target-Perspective Output:** A reviewer can open the four generated plots, compare PC-SAFT curves against retained source markers in paper coordinates, and inspect score JSON plus source/model CSVs behind each plot.
**Truth Owner:** Gross/Sadowski 2002 Figures 2-5 source images, local Gross 2002 paper text, Table 1 pure parameters, Table 2 binary `k_ij` rows, analysis-local parameter snapshots, and the #279 full-replication checker contract.
**Contract Interface:** `scripts/validation/check_gross_2002_full_replication.py`, the #279 score/source metadata schemas, and public `epcsaft_equilibrium.Equilibrium(...).solve()` workflows used by the generation scripts.
**Cutover Decision:** Move a figure from `planned` to `accepted` only after its source/model/score/plot artifacts pass the checker and its source identity/provenance is retained.
**Displaced Path:** Keep the existing source images and #275/#279 campaign summary as historical context; do not use source images alone as completion evidence.
**Evidence Lane:** Figure-owned source/model/plot artifacts, shared manifest/summary updates, full-replication checker output, association acceptance checker output, docs validation, and cleanup hook.
**Acceptance Evidence:** Passing proof oracle commands plus final handoff rendering Figures 2-5 inline with a compact table of source row counts, model row counts, scores, derivative status, and pass state.
**Kill Criteria:** Stop the worker route and create a prerequisite issue if any Figure 2-5 system cannot be generated through a production native equilibrium route with exact association derivative metadata.
**Forbidden Moves:** Do not implement unrelated C++ route work inside #281; do not use synthetic source points; do not lower #279 score thresholds; do not accept Figure 2 while the identity conflict is unresolved; do not add electrolyte, reactive, or generalized associating phase-set claims.
**Risk If Wrong:** The project would claim association confidence before the package reproduces the binary associating VLE curves used by the paper to validate PC-SAFT mixtures.

## Architecture Slice

**Files To Create:** Figure-owned source, script, and result files under `analyses/paper_validation/2002_gross/figures/figure_02`, `figure_03`, `figure_04`, and `figure_05`, including identity, source CSV, metadata JSON, QA overlay, model CSV, plotted CSV, score JSON, summary JSON, PNG, SVG, and PDF LaTeX artifacts.
**Files To Modify:** `scripts/validation/check_gross_2002_full_replication.py`, `tests/native/contracts/test_gross_2002_full_replication_checker.py`, `analyses/paper_validation/2002_gross/shared/gross_2002_full_replication_manifest.json`, `analyses/paper_validation/2002_gross/shared/results/gross_2002_full_replication_summary.json`, `analyses/paper_validation/2002_gross/shared/results/gross_2002_full_replication_summary.csv`, this issue mirror, and `docs/superpowers/milestones/M4-equilibrium/README.md`.
**Files To Avoid:** Native C++ route implementation files, provider EOS code, regression package code, electrolyte/reactive route files, downstream repositories, and Gross 2002 figure folders outside Figures 2-5 except shared summary files.
**Source Of Truth:** Gross/Sadowski 2002 Figures 2-5 images and captions, Table 1, Table 2, `analyses/paper_validation/2002_gross/parameters`, and #279 checker schema.
**Read Path:** Source CSV and metadata feed generation; model CSV and source CSV feed rendering; score/summary JSON feed manifest and checker aggregation.
**Write Path:** Figure-specific artifacts stay under each `figure_NN` folder; shared status artifacts stay under `analyses/paper_validation/2002_gross/shared`.
**Integration Points:** Public equilibrium route, native selector route, exact association derivative diagnostics, full-replication checker, M4 milestone evidence table, GitHub issue mirror.
**Migration Or Cutover:** Remove owned `_placeholder.md` files from a figure's `scripts` or `results` folder only after real files occupy that folder.
**Acceptance Evidence Gate:** The worker cannot mark #281 ready until Figures 2-5 are accepted by the full-replication checker and the final handoff renders all four new plots inline.

## Acceptance Coverage

- Resolve Figure 2 identity before acceptance: Task 1.
- Retain source data, metadata, and QA overlays for Figures 2-5: Tasks 1, 3, 5, 7, and 9.
- Generate paper-axis VLE model curves for all required systems and series: Tasks 4, 6, 8, and 10.
- Render paper-scale mirror plots for Figures 2-5: Tasks 4, 6, 8, and 10.
- Write score JSON per figure and per series: Tasks 2, 4, 6, 8, and 10.
- Keep the full-replication checker strict and partial-campaign proof honest: Tasks 2 and 11.

## Non-Goals

- No electrolyte, reactive, CE, CPE, or generalized phase-count admission.
- No changes to Figures 6-10 beyond shared summary readout.
- No broad associating-family capability claim beyond the Figure 2-5 evidence proven here.
- No package regression workflow changes.
- No native route implementation bundled inside the figure-replication PR.

### Task 1: Resolve Figure 2 Source Identity And Parameter Provenance

**Use Cases:**
- Figure 2 cannot pass while the caption, Table 2 row, and parameter snapshot disagree.
- A reviewer can see the accepted Figure 2 component pair, the rejected alternatives, and the evidence path.
- The generator uses the same component names, order, and `k_ij` value retained in the identity artifact.
- The checker names a blocker if Figure 2 is accepted without resolved identity evidence.

**Files:**
- Create: `analyses/paper_validation/2002_gross/figures/figure_02/source/gross_2002_figure_02_replication_identity.json`
- Modify: `analyses/paper_validation/2002_gross/shared/gross_2002_full_replication_manifest.json`
- Modify: `scripts/validation/check_gross_2002_full_replication.py`
- Modify: `tests/native/contracts/test_gross_2002_full_replication_checker.py`
- Test: `tests/native/contracts/test_gross_2002_full_replication_checker.py`

- [ ] **Step 1: Add a failing checker test for unresolved Figure 2 identity**

  Add a test that marks Figure 2 accepted while `source_identity_status` is not `resolved` and expects a blocker named `gross_2002_figure_02_source_identity_unresolved`.

- [ ] **Step 2: Run the targeted test and verify failure**

  Run:

  ```powershell
  uv run --no-sync python run_pytest.py tests/native/contracts/test_gross_2002_full_replication_checker.py::test_figure_two_requires_resolved_source_identity -q
  ```

  Expected before implementation: the test fails because the checker does not yet enforce the Figure 2 identity artifact.

- [ ] **Step 3: Implement Figure 2 identity validation**

  Require accepted Figure 2 records to include `source_identity_status: "resolved"` and an artifact key named `source_identity_json` that points to an existing JSON file.

- [ ] **Step 4: Write the identity artifact**

  Create `gross_2002_figure_02_replication_identity.json` only after the accepted system is verified from retained evidence. The committed JSON must include the verified `figure_id`, `caption_system`, `table_002_system`, `parameter_snapshot_system`, `pc_saft_k_ij`, `saft_k_ij`, `accepted_system`, `accepted_component_order`, `evidence`, and `resolution_reason` fields. The `evidence` array must name the exact retained files used to reach the conclusion.

- [ ] **Step 5: Run checker tests**

  Run:

  ```powershell
  uv run --no-sync python run_pytest.py tests/native/contracts/test_gross_2002_full_replication_checker.py -q
  ```

  Expected: checker tests pass, and planned Figure 2 records remain allowed until the identity is resolved.

- [ ] **Step 6: Commit**

  Commit:

  ```powershell
  git add scripts/validation/check_gross_2002_full_replication.py tests/native/contracts/test_gross_2002_full_replication_checker.py analyses/paper_validation/2002_gross/figures/figure_02/source/gross_2002_figure_02_replication_identity.json analyses/paper_validation/2002_gross/shared/gross_2002_full_replication_manifest.json
  git commit -m "Require resolved Gross 2002 Figure 2 identity"
  ```

### Task 2: Add Shared VLE Series Validation For Figures 2-5

**Use Cases:**
- An accepted VLE figure cannot pass with only a top-level score.
- Each required liquid and vapor/composition series is scored separately.
- Figures with multiple panels or systems report a distinct score for each required series.
- The #279 foundation mode still passes while later figures remain planned.

**Files:**
- Modify: `scripts/validation/check_gross_2002_full_replication.py`
- Modify: `tests/native/contracts/test_gross_2002_full_replication_checker.py`
- Modify: `analyses/paper_validation/2002_gross/shared/gross_2002_full_replication_manifest.json`
- Test: `tests/native/contracts/test_gross_2002_full_replication_checker.py`

- [ ] **Step 1: Add failing tests for VLE required series**

  Add checker tests that accepted Figure 3 fails when one pressure series score is absent and accepted Figure 5 fails when one isomer system score is absent.

- [ ] **Step 2: Run targeted tests and verify failure**

  Run:

  ```powershell
  uv run --no-sync python run_pytest.py tests/native/contracts/test_gross_2002_full_replication_checker.py::test_accepted_vle_figures_require_all_series_scores -q
  ```

  Expected before implementation: failure because the checker does not enforce every Figure 2-5 required series.

- [ ] **Step 3: Add `required_series` support**

  In the checker, require `score_json["series_scores"]` to contain every token listed in an accepted figure record's `required_series` field.

- [ ] **Step 4: Add required series to Figures 2-5**

  Add manifest fields with final tokens aligned to the rendered plot legends. Use these initial tokens unless source acquisition proves a better series naming:

  ```json
  {
    "figure_02": ["bubble_line", "dew_line"],
    "figure_03": ["pressure_series_low", "pressure_series_high"],
    "figure_04": ["bubble_line", "dew_line"],
    "figure_05": ["1-propanol-benzene", "2-propanol-benzene"]
  }
  ```

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
  git commit -m "Require Gross 2002 VLE series scores"
  ```

### Task 3: Retain Figure 2 Source Data And Metadata

**Use Cases:**
- Figure 2 source points are traceable to cited data or calibrated image digitization.
- The retained source data uses the same accepted system and component order as the identity artifact.
- Axis calibration, pressure units, composition basis, and digitization uncertainty are reviewable.
- The QA overlay makes calibration and point extraction visible.

**Files:**
- Create: `analyses/paper_validation/2002_gross/figures/figure_02/source/gross_2002_figure_02_replication_source_points.csv`
- Create: `analyses/paper_validation/2002_gross/figures/figure_02/source/gross_2002_figure_02_replication_digitization_metadata.json`
- Create: `analyses/paper_validation/2002_gross/figures/figure_02/source/gross_2002_figure_02_replication_digitization_qa_overlay.png`
- Modify: `analyses/paper_validation/2002_gross/figures/figure_02/source/gross_2002_figure_02_replication_identity.json`

- [ ] **Step 1: Extract or digitize Figure 2 points**

  Produce a source CSV with columns:

  ```text
  figure_id,series,accepted_system,component_order,T_K,P_bar,x_component_1,y_component_1,source_kind,source_reference,digitized_x_px,digitized_y_px,uncertainty_P_bar,uncertainty_composition
  ```

- [ ] **Step 2: Write metadata**

  Write metadata with `provenance`, `axis_calibration`, `units`, `series_labels`, `digitization_uncertainty`, `qa_overlay`, `accepted_system`, `component_order`, and `identity_json`.

- [ ] **Step 3: Save the QA overlay**

  Save the overlay showing the Figure 2 image, calibration anchors, and extracted points.

- [ ] **Step 4: Verify row coverage**

  Run:

  ```powershell
  uv run --no-sync python -c "import pandas as pd; f=pd.read_csv('analyses/paper_validation/2002_gross/figures/figure_02/source/gross_2002_figure_02_replication_source_points.csv'); print(f.groupby('series').size().to_string())"
  ```

  Expected: every Figure 2 required source series is present with at least six total source rows unless the retained image visibly contains fewer.

- [ ] **Step 5: Commit**

  Commit:

  ```powershell
  git add analyses/paper_validation/2002_gross/figures/figure_02/source
  git commit -m "Retain Gross 2002 Figure 2 VLE source points"
  ```

### Task 4: Generate And Render Figure 2 Model Curves

**Use Cases:**
- Figure 2 model data is generated from the resolved identity and retained parameter provenance.
- The plotted figure uses paper `P-x/y` axes and not a diagnostic substitute.
- Score JSON proves per-series agreement against source points.
- The generation output records native freshness and exact association derivative status.

**Files:**
- Create: `analyses/paper_validation/2002_gross/figures/figure_02/scripts/generate_gross_2002_figure_02_replication.py`
- Create: `analyses/paper_validation/2002_gross/figures/figure_02/results/gross_2002_figure_02_replication_model_curve.csv`
- Create: `analyses/paper_validation/2002_gross/figures/figure_02/results/gross_2002_figure_02_replication_plotted_data.csv`
- Create: `analyses/paper_validation/2002_gross/figures/figure_02/results/gross_2002_figure_02_replication_score.json`
- Create: `analyses/paper_validation/2002_gross/figures/figure_02/results/gross_2002_figure_02_replication_summary.json`
- Create: `analyses/paper_validation/2002_gross/figures/figure_02/results/gross_2002_figure_02_replication.png`
- Create: `analyses/paper_validation/2002_gross/figures/figure_02/results/gross_2002_figure_02_replication.svg`
- Create: `analyses/paper_validation/2002_gross/figures/figure_02/results/gross_2002_figure_02_replication.pdf`
- Delete: `analyses/paper_validation/2002_gross/figures/figure_02/scripts/_placeholder.md` if real scripts occupy the folder.
- Delete: `analyses/paper_validation/2002_gross/figures/figure_02/results/_placeholder.md` if real results occupy the folder.

- [ ] **Step 1: Write the generator**

  The script must read the identity JSON, source CSV, metadata JSON, Table 1, Table 2, and analysis-local parameter snapshots before model generation.

- [ ] **Step 2: Generate the model curve**

  Generate PC-SAFT Figure 2 VLE data at `T_K = 373.15` with model columns:

  ```text
  figure_id,series,accepted_system,component_order,T_K,P_bar,x_component_1,y_component_1,phase_label,solver_status,route_status,derivative_status,native_freshness_receipt
  ```

- [ ] **Step 3: Score the model**

  Interpolate model curves in paper coordinates and write per-series scores plus the #279 top-level score fields.

- [ ] **Step 4: Render the plot**

  Render a paper-scale `P-x/y` plot with source markers and PC-SAFT curves. The render path must read retained CSVs and score JSON rather than running native solves.

- [ ] **Step 5: Run generation**

  Run:

  ```powershell
  uv run --no-sync python analyses/paper_validation/2002_gross/figures/figure_02/scripts/generate_gross_2002_figure_02_replication.py
  ```

  Expected: all Figure 2 result artifacts are written and the score JSON has `pass: true`.

- [ ] **Step 6: Commit**

  Commit:

  ```powershell
  git add analyses/paper_validation/2002_gross/figures/figure_02
  git commit -m "Replicate Gross 2002 Figure 2 VLE curve"
  ```

### Task 5: Retain Figure 3 Source Data And Metadata

**Use Cases:**
- Both Figure 3 pressure series are retained with series identity.
- Ethylbenzene pure-parameter provenance is recorded before model generation counts.
- Axis calibration, units, pressure labels, and uncertainty are reviewable.
- The QA overlay shows both source series.

**Files:**
- Create: `analyses/paper_validation/2002_gross/figures/figure_03/source/gross_2002_figure_03_replication_source_points.csv`
- Create: `analyses/paper_validation/2002_gross/figures/figure_03/source/gross_2002_figure_03_replication_digitization_metadata.json`
- Create: `analyses/paper_validation/2002_gross/figures/figure_03/source/gross_2002_figure_03_replication_digitization_qa_overlay.png`

- [ ] **Step 1: Extract or digitize Figure 3 points**

  Produce a source CSV with columns:

  ```text
  figure_id,series,system,pressure_label,P_bar_or_MPa,T_K,x_1_propanol,y_1_propanol,source_kind,source_reference,digitized_x_px,digitized_y_px,uncertainty_temperature_K,uncertainty_composition
  ```

- [ ] **Step 2: Write metadata**

  Record the Gross 2002 caption, reference 24 provenance, `k_ij = 0.023`, component order, axis calibration, units, and series labels.

- [ ] **Step 3: Save the QA overlay**

  Save the overlay with calibration anchors and both pressure series visibly marked.

- [ ] **Step 4: Verify row coverage**

  Run:

  ```powershell
  uv run --no-sync python -c "import pandas as pd; f=pd.read_csv('analyses/paper_validation/2002_gross/figures/figure_03/source/gross_2002_figure_03_replication_source_points.csv'); print(f.groupby('series').size().to_string())"
  ```

  Expected: both Figure 3 pressure series are present.

- [ ] **Step 5: Commit**

  Commit:

  ```powershell
  git add analyses/paper_validation/2002_gross/figures/figure_03/source
  git commit -m "Retain Gross 2002 Figure 3 VLE source points"
  ```

### Task 6: Generate And Render Figure 3 Model Curves

**Use Cases:**
- Figure 3 model data covers both pressure series shown in the paper.
- Score JSON reports a pass/fail result per pressure series.
- The rendered figure preserves the paper axis family and series labels.
- Native and exact derivative receipts are retained.

**Files:**
- Create: `analyses/paper_validation/2002_gross/figures/figure_03/scripts/generate_gross_2002_figure_03_replication.py`
- Create: `analyses/paper_validation/2002_gross/figures/figure_03/results/gross_2002_figure_03_replication_model_curve.csv`
- Create: `analyses/paper_validation/2002_gross/figures/figure_03/results/gross_2002_figure_03_replication_plotted_data.csv`
- Create: `analyses/paper_validation/2002_gross/figures/figure_03/results/gross_2002_figure_03_replication_score.json`
- Create: `analyses/paper_validation/2002_gross/figures/figure_03/results/gross_2002_figure_03_replication_summary.json`
- Create: `analyses/paper_validation/2002_gross/figures/figure_03/results/gross_2002_figure_03_replication.png`
- Create: `analyses/paper_validation/2002_gross/figures/figure_03/results/gross_2002_figure_03_replication.svg`
- Create: `analyses/paper_validation/2002_gross/figures/figure_03/results/gross_2002_figure_03_replication.pdf`
- Delete: `analyses/paper_validation/2002_gross/figures/figure_03/scripts/_placeholder.md` if real scripts occupy the folder.
- Delete: `analyses/paper_validation/2002_gross/figures/figure_03/results/_placeholder.md` if real results occupy the folder.

- [ ] **Step 1: Write the generator**

  The script must read source points, metadata, Gross Table 1, Table 2, `k_ij = 0.023`, and analysis-local pure/mixed parameter snapshots.

- [ ] **Step 2: Generate both pressure-series curves**

  Generate model data in the same coordinate family as the paper, preserving series labels and component order.

- [ ] **Step 3: Score both series**

  Write `series_scores` with one entry per pressure series and top-level score fields required by #279.

- [ ] **Step 4: Render the plot**

  Render a paper-scale Figure 3 mirror plot from retained source/model CSVs.

- [ ] **Step 5: Run generation**

  Run:

  ```powershell
  uv run --no-sync python analyses/paper_validation/2002_gross/figures/figure_03/scripts/generate_gross_2002_figure_03_replication.py
  ```

  Expected: all Figure 3 result artifacts are written and each required series passes.

- [ ] **Step 6: Commit**

  Commit:

  ```powershell
  git add analyses/paper_validation/2002_gross/figures/figure_03
  git commit -m "Replicate Gross 2002 Figure 3 VLE curves"
  ```

### Task 7: Retain Figure 4 Source Data And Metadata

**Use Cases:**
- Figure 4 source points are retained for 1-pentanol/benzene at 40 degC.
- Benzene pure-parameter provenance is recorded.
- Axis calibration, pressure units, and composition basis are reviewable.
- The QA overlay makes extracted points auditable.

**Files:**
- Create: `analyses/paper_validation/2002_gross/figures/figure_04/source/gross_2002_figure_04_replication_source_points.csv`
- Create: `analyses/paper_validation/2002_gross/figures/figure_04/source/gross_2002_figure_04_replication_digitization_metadata.json`
- Create: `analyses/paper_validation/2002_gross/figures/figure_04/source/gross_2002_figure_04_replication_digitization_qa_overlay.png`

- [ ] **Step 1: Extract or digitize Figure 4 points**

  Produce a source CSV with columns:

  ```text
  figure_id,series,system,T_K,P_bar,x_1_pentanol,y_1_pentanol,source_kind,source_reference,digitized_x_px,digitized_y_px,uncertainty_P_bar,uncertainty_composition
  ```

- [ ] **Step 2: Write metadata**

  Record the Gross 2002 caption, reference 25 provenance, `k_ij = 0.0135`, component order, axis calibration, units, and series labels.

- [ ] **Step 3: Save the QA overlay**

  Save the overlay with calibration anchors and source points.

- [ ] **Step 4: Verify row coverage**

  Run:

  ```powershell
  uv run --no-sync python -c "import pandas as pd; f=pd.read_csv('analyses/paper_validation/2002_gross/figures/figure_04/source/gross_2002_figure_04_replication_source_points.csv'); print(len(f)); print(f.groupby('series').size().to_string())"
  ```

  Expected: Figure 4 source rows are present for the required source series.

- [ ] **Step 5: Commit**

  Commit:

  ```powershell
  git add analyses/paper_validation/2002_gross/figures/figure_04/source
  git commit -m "Retain Gross 2002 Figure 4 VLE source points"
  ```

### Task 8: Generate And Render Figure 4 Model Curves

**Use Cases:**
- Figure 4 model data reproduces the 40 degC 1-pentanol/benzene `P-x/y` curve.
- Score JSON records bubble/dew or equivalent required-series scores.
- The rendered figure matches the paper plot family and scale.
- Native and exact derivative receipts are retained.

**Files:**
- Create: `analyses/paper_validation/2002_gross/figures/figure_04/scripts/generate_gross_2002_figure_04_replication.py`
- Create: `analyses/paper_validation/2002_gross/figures/figure_04/results/gross_2002_figure_04_replication_model_curve.csv`
- Create: `analyses/paper_validation/2002_gross/figures/figure_04/results/gross_2002_figure_04_replication_plotted_data.csv`
- Create: `analyses/paper_validation/2002_gross/figures/figure_04/results/gross_2002_figure_04_replication_score.json`
- Create: `analyses/paper_validation/2002_gross/figures/figure_04/results/gross_2002_figure_04_replication_summary.json`
- Create: `analyses/paper_validation/2002_gross/figures/figure_04/results/gross_2002_figure_04_replication.png`
- Create: `analyses/paper_validation/2002_gross/figures/figure_04/results/gross_2002_figure_04_replication.svg`
- Create: `analyses/paper_validation/2002_gross/figures/figure_04/results/gross_2002_figure_04_replication.pdf`
- Delete: `analyses/paper_validation/2002_gross/figures/figure_04/scripts/_placeholder.md` if real scripts occupy the folder.
- Delete: `analyses/paper_validation/2002_gross/figures/figure_04/results/_placeholder.md` if real results occupy the folder.

- [ ] **Step 1: Write the generator**

  The script must read source points, metadata, Gross Table 1, Table 2, `k_ij = 0.0135`, and analysis-local pure/mixed parameter snapshots.

- [ ] **Step 2: Generate the model curve**

  Generate PC-SAFT VLE data at `T_K = 313.15` with columns matching the retained source coordinate family.

- [ ] **Step 3: Score required series**

  Write per-series scores and top-level #279 score fields.

- [ ] **Step 4: Render the plot**

  Render source markers and PC-SAFT curves on a paper-scale `P-x/y` plot.

- [ ] **Step 5: Run generation**

  Run:

  ```powershell
  uv run --no-sync python analyses/paper_validation/2002_gross/figures/figure_04/scripts/generate_gross_2002_figure_04_replication.py
  ```

  Expected: all Figure 4 result artifacts are written and each required series passes.

- [ ] **Step 6: Commit**

  Commit:

  ```powershell
  git add analyses/paper_validation/2002_gross/figures/figure_04
  git commit -m "Replicate Gross 2002 Figure 4 VLE curve"
  ```

### Task 9: Retain Figure 5 Source Data And Metadata

**Use Cases:**
- Figure 5 source points preserve both isomer systems.
- The metadata records distinct `k_ij` values for 1-propanol/benzene and 2-propanol/benzene.
- Axis calibration, units, symbol mapping, and uncertainty are reviewable.
- The QA overlay shows both isomer systems.

**Files:**
- Create: `analyses/paper_validation/2002_gross/figures/figure_05/source/gross_2002_figure_05_replication_source_points.csv`
- Create: `analyses/paper_validation/2002_gross/figures/figure_05/source/gross_2002_figure_05_replication_digitization_metadata.json`
- Create: `analyses/paper_validation/2002_gross/figures/figure_05/source/gross_2002_figure_05_replication_digitization_qa_overlay.png`

- [ ] **Step 1: Extract or digitize Figure 5 points**

  Produce a source CSV with columns:

  ```text
  figure_id,series,system,T_K,P_bar,x_alcohol,y_alcohol,source_kind,source_reference,digitized_x_px,digitized_y_px,uncertainty_P_bar,uncertainty_composition
  ```

- [ ] **Step 2: Write metadata**

  Record the Gross 2002 caption, reference 25 provenance, `k_ij = 0.020` for 1-propanol/benzene, `k_ij = 0.021` for 2-propanol/benzene, component order, axis calibration, units, and series labels.

- [ ] **Step 3: Save the QA overlay**

  Save the overlay with calibration anchors, source points, and visible symbol mapping.

- [ ] **Step 4: Verify row coverage**

  Run:

  ```powershell
  uv run --no-sync python -c "import pandas as pd; f=pd.read_csv('analyses/paper_validation/2002_gross/figures/figure_05/source/gross_2002_figure_05_replication_source_points.csv'); print(f.groupby('system').size().to_string())"
  ```

  Expected: both isomer systems have retained source rows.

- [ ] **Step 5: Commit**

  Commit:

  ```powershell
  git add analyses/paper_validation/2002_gross/figures/figure_05/source
  git commit -m "Retain Gross 2002 Figure 5 VLE source points"
  ```

### Task 10: Generate And Render Figure 5 Model Curves

**Use Cases:**
- Figure 5 model data contains separate curves for 1-propanol/benzene and 2-propanol/benzene.
- Score JSON reports separate pass/fail results for both isomer systems.
- The rendered plot preserves the paper's two-system comparison.
- Native and exact derivative receipts are retained.

**Files:**
- Create: `analyses/paper_validation/2002_gross/figures/figure_05/scripts/generate_gross_2002_figure_05_replication.py`
- Create: `analyses/paper_validation/2002_gross/figures/figure_05/results/gross_2002_figure_05_replication_model_curve.csv`
- Create: `analyses/paper_validation/2002_gross/figures/figure_05/results/gross_2002_figure_05_replication_plotted_data.csv`
- Create: `analyses/paper_validation/2002_gross/figures/figure_05/results/gross_2002_figure_05_replication_score.json`
- Create: `analyses/paper_validation/2002_gross/figures/figure_05/results/gross_2002_figure_05_replication_summary.json`
- Create: `analyses/paper_validation/2002_gross/figures/figure_05/results/gross_2002_figure_05_replication.png`
- Create: `analyses/paper_validation/2002_gross/figures/figure_05/results/gross_2002_figure_05_replication.svg`
- Create: `analyses/paper_validation/2002_gross/figures/figure_05/results/gross_2002_figure_05_replication.pdf`
- Delete: `analyses/paper_validation/2002_gross/figures/figure_05/scripts/_placeholder.md` if real scripts occupy the folder.
- Delete: `analyses/paper_validation/2002_gross/figures/figure_05/results/_placeholder.md` if real results occupy the folder.

- [ ] **Step 1: Write the generator**

  The script must read source points, metadata, Gross Table 1, Table 2, isomer-specific `k_ij` values, and analysis-local pure/mixed parameter snapshots.

- [ ] **Step 2: Generate both isomer curves**

  Generate PC-SAFT VLE data at `T_K = 313.15` for both systems with retained component order and series labels.

- [ ] **Step 3: Score both systems**

  Write `series_scores` for `1-propanol-benzene` and `2-propanol-benzene` plus top-level #279 score fields.

- [ ] **Step 4: Render the plot**

  Render source markers and PC-SAFT curves for both isomer systems on one paper-scale plot.

- [ ] **Step 5: Run generation**

  Run:

  ```powershell
  uv run --no-sync python analyses/paper_validation/2002_gross/figures/figure_05/scripts/generate_gross_2002_figure_05_replication.py
  ```

  Expected: all Figure 5 result artifacts are written and both required systems pass.

- [ ] **Step 6: Commit**

  Commit:

  ```powershell
  git add analyses/paper_validation/2002_gross/figures/figure_05
  git commit -m "Replicate Gross 2002 Figure 5 VLE curves"
  ```

### Task 11: Accept Figures 2-5 And Verify Partial Campaign State

**Use Cases:**
- The checker recognizes Figures 2-5 as accepted without pretending Figures 6-10 are complete.
- Shared summaries show Figures 1-5 accepted and later figure blockers still visible.
- M4 README records the new evidence and keeps electrolyte #191 blocked until #286 closes.
- The live issue body and mirror point to this plan.

**Files:**
- Modify: `analyses/paper_validation/2002_gross/shared/gross_2002_full_replication_manifest.json`
- Modify: `analyses/paper_validation/2002_gross/shared/results/gross_2002_full_replication_summary.json`
- Modify: `analyses/paper_validation/2002_gross/shared/results/gross_2002_full_replication_summary.csv`
- Modify: `docs/superpowers/issues/2026-06-19-m4-equilibrium-issue-0281-fully-replicate-gross-2002-figures-2-5-self-associating-vle-curves.md`
- Modify: `docs/superpowers/milestones/M4-equilibrium/README.md`
- Test: `scripts/validation/check_gross_2002_full_replication.py`
- Test: `scripts/validation/check_gross_2002_association_acceptance.py`

- [ ] **Step 1: Update Figure 2-5 manifest records**

  Set Figures 2-5 to accepted with artifact paths, score summaries, required series, exact derivative requirement, `counts_toward_completion: true`, and empty `remaining_work`.

- [ ] **Step 2: Refresh the shared summary**

  Run:

  ```powershell
  uv run --no-sync python scripts/validation/check_gross_2002_full_replication.py --json --require-foundation --write-summary
  ```

  Expected: shared summary records Figures 1-5 accepted and Figures 6-10 still planned.

- [ ] **Step 3: Run the Figure 2-5 acceptance gate**

  Run:

  ```powershell
  uv run --no-sync python scripts/validation/check_gross_2002_full_replication.py --json --require-exact-association-hessian --require-fresh-native
  ```

  Expected for #281 closeout: exit `0`, Figures 2-5 accepted, and no blockers for Figures 2-5.

- [ ] **Step 4: Run the expected partial-campaign readout**

  Run:

  ```powershell
  uv run --no-sync python scripts/validation/check_gross_2002_full_replication.py --json --require-complete --require-exact-association-hessian --require-fresh-native
  ```

  Expected for #281 closeout: exit `2`; Figures 1-5 have no blockers, and Figures 6-10 still report blockers until #282-#285 close.

- [ ] **Step 5: Run association acceptance regression**

  Run:

  ```powershell
  uv run --no-sync python scripts/validation/check_gross_2002_association_acceptance.py --json --require-complete --require-exact-association-hessian --require-fresh-native
  ```

  Expected: exit `0`, preserving the #275 association acceptance evidence.

- [ ] **Step 6: Update docs and issue mirror**

  Link this plan in the #281 issue mirror and update M4 README retained evidence or queue notes with the Figures 2-5 replication result and plot paths.

- [ ] **Step 7: Sync the live GitHub issue body**

  After local validation, update issue #281 from the corrected local mirror body.

- [ ] **Step 8: Commit**

  Commit:

  ```powershell
  git add analyses/paper_validation/2002_gross/shared/gross_2002_full_replication_manifest.json analyses/paper_validation/2002_gross/shared/results/gross_2002_full_replication_summary.json analyses/paper_validation/2002_gross/shared/results/gross_2002_full_replication_summary.csv docs/superpowers/issues/2026-06-19-m4-equilibrium-issue-0281-fully-replicate-gross-2002-figures-2-5-self-associating-vle-curves.md docs/superpowers/milestones/M4-equilibrium/README.md
  git commit -m "Accept Gross 2002 Figures 2-5 replication evidence"
  ```

### Task 12: Final Verification And PR Handoff

**Use Cases:**
- The PR proves #281 without claiming the full Gross 2002 campaign is complete.
- The final handoff renders Figures 2-5 inline and includes source/model/score numerics.
- The repo is clean after validation.
- #282 remains the next ready figure-family issue after #281 merges.

**Files:**
- Test: `scripts/validation/check_gross_2002_full_replication.py`
- Test: `scripts/validation/check_gross_2002_association_acceptance.py`
- Test: `tests/native/contracts/test_gross_2002_full_replication_checker.py`

- [ ] **Step 1: Build native equilibrium**

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

  Expected: full-replication partial acceptance exits `0`, with Figures 1-5 accepted and no Figure 2-5 blockers. Association acceptance exits `0`.

- [ ] **Step 4: Run docs validation and diff hygiene**

  Run:

  ```powershell
  uv run --no-sync python scripts/dev/validate_project.py docs
  git diff --check
  ```

- [ ] **Step 5: Run cleanup**

  Run:

  ```powershell
  pwsh.exe -NoProfile -ExecutionPolicy Bypass -File "$env:USERPROFILE\.codex\hooks\codex-cleanup.ps1" -RepoRoot .
  ```

- [ ] **Step 6: Prepare PR handoff**

  The handoff must include absolute PNG/SVG paths for Figures 2-5, source row counts by figure and series, model row counts by figure and series, score table, derivative/native receipt status, the Figure 2 identity conclusion, and the remaining Figure 6-10 blockers.

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

Expected for #281: exit `2`; Figures 1-5 have no blockers, and Figures 6-10 blockers remain until #282-#285 close.

## Risk Notes

- Figure 2 identity has conflicting local evidence and must be resolved before any Figure 2 acceptance claim.
- Binary self-associating VLE model generation may expose native route limitations. Those must be split into prerequisite issues rather than merged into #281.
- Source digitization quality directly controls scores. The metadata and QA overlays must make calibration reviewable.
- Figure 3 pressure labels and Figure 5 isomer symbols must stay tied to source metadata so the scorer does not compare the wrong series.
- This issue only moves the Gross 2002 full-replication campaign from Figure 1 accepted to Figures 1-5 accepted. Full campaign completion remains #286.

## Recommended Implementation Route

Use `$superpowers-project:orchestrate-issues` for issue #281 after this plan is committed and the issue mirror points to it. Start #282 only after #281 is merged because the shared full-replication manifest and summary files are sequential campaign state.
