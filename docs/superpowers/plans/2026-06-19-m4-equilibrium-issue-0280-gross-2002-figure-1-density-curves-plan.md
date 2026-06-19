# Gross 2002 Figure 1 Density Curves Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fully replicate Gross/Sadowski 2002 Figure 1 as paper-scale saturated vapor/liquid density curves for methanol, 1-pentanol, and 1-nonanol with retained source data, native model data, plot-match scoring, and checker evidence.

**Architecture:** Promote Figure 1 from the #275 association-AAD sanity mirror to the #279 full-replication contract. The native pure 2B associating `single_component_vle` admission is split into prerequisite issue #290; this issue consumes that merged route to retain calibrated Figure 1 source points, generate PC-SAFT vapor/liquid density curves, render the `T-rho` paper plot, update the manifest to accepted, and keep the campaign checker strict.

**Tech Stack:** Python stdlib CSV/JSON/pathlib, pandas, matplotlib, yaml, existing `epcsaft` and `epcsaft_equilibrium` public APIs, native equilibrium Ipopt route code, C++ exact derivative blocks, pytest through `run_pytest.py`, Sphinx docs validation, and the repo cleanup hook.

---

## Intake

- Source spec: `docs/superpowers/specs/2026-06-19-m4-equilibrium-gross-2002-full-figure-replication.md`
- Issue mirror: `docs/superpowers/issues/2026-06-19-m4-equilibrium-issue-0280-fully-replicate-gross-2002-figure-1-pure-component-density-curves.md`
- GitHub issue: `https://github.com/ePC-SAFT/ePC-SAFT/issues/280`
- Milestone: `M4 - Equilibrium`
- Package owner: `packages/epcsaft-equilibrium`
- Capability: `association`
- Backend: `Ipopt`
- Validation root: `analyses/paper_validation/2002_gross/figures/figure_01`
- Foundation issue: #279, merged through PR #288

## Planning Grill Resolution

Material planning questions were answered from repo evidence:

- Scope: #280 owns Figure 1 only. #281-#285 own the other figure families, and #286 owns final campaign closure.
- Source policy: use the retained Gross/Sadowski Figure 1 image as the coordinate truth for this issue unless a traceable cited source table is found quickly during source acquisition. Either path must produce the same retained source CSV, metadata JSON, and QA overlay.
- Route policy: #280 is blocked by #290. #280 must not implement native route admission; it must consume the merged #290 public `single_component_vle` route and keep the Figure 1 PR focused on source/model/plot/score artifacts.
- Metrics: inherit the #279 `t_rho` normalized score gate of `>= 7.0`, plus per-component vapor/liquid branch coverage.
- Branch strategy: use the issue branch from the mirror, `codex/issue-0280-gross-2002-figure-1-density-curves`.
- Execution route: worker-thread orchestration after #290 is merged and this plan is linked to the issue mirror.

## Test Complete And Metrics

Test complete for #280 means:

- The merged #290 route receipt proves `Equilibrium(mixture, route="single_component_vle", T=...).solve()` returns native Ipopt results for pure methanol, 1-pentanol, and 1-nonanol parameter sets from Gross/Sadowski Table 1.
- Figure 1 source data is retained with at least six source points per component per branch for `vapor` and `liquid`, unless the retained paper image visibly contains fewer; any lower count must be recorded in the metadata and score caveats.
- Figure 1 model data is retained with at least thirty model points per component per branch across the paper temperature span.
- The Figure 1 score JSON records per-component and per-branch `source_point_count`, `model_point_count`, `rmse_axis`, `max_axis_error`, `normalized_plot_score`, `branch_coverage_score`, `derivative_status`, and `pass`.
- Every component and branch has `normalized_plot_score >= 7.0`, `branch_coverage_score == 1.0`, and `pass: true`.
- The rendered PNG/SVG plot uses the paper plot type and scale: temperature on the vertical axis and density on the horizontal axis, with source markers and PC-SAFT model curves for all three alcohols.
- `scripts/validation/check_gross_2002_full_replication.py --json --require-complete --require-exact-association-hessian --require-fresh-native` no longer reports a Figure 1 blocker. Other figures may still block until #281-#285 land.

## Outcome Contract

**Intent:** Convert Figure 1 from a diagnostic association-AAD mirror into source-backed curve-level paper replication.
**Current Behavior:** Figure 1 is `planned` in `gross_2002_full_replication_manifest.json`; existing artifacts only show Table 1 AAD sanity evidence. #290 owns the native pure associating `single_component_vle` admission required before this figure can generate model curves.
**Expected Outcome:** Figure 1 is `accepted`, counts toward full campaign completion, and has retained source, model, plotted, score, summary, PNG, SVG, sidecar, and native route evidence artifacts.
**Target-Perspective Output:** A reviewer can open the Figure 1 PNG/SVG and see a paper-scale `T-rho` reproduction for methanol, 1-pentanol, and 1-nonanol, then inspect score JSON and retained CSVs behind the plot.
**Truth Owner:** Gross/Sadowski 2002 Figure 1 source image and the #279 full-replication checker contract.
**Contract Interface:** `scripts/validation/check_gross_2002_full_replication.py` and the #290 public `epcsaft_equilibrium.Equilibrium(..., route="single_component_vle", T=...).solve()` workflow.
**Cutover Decision:** Replace the current Figure 1 `planned` manifest record with an `accepted` record only after the source/model/score/plot artifacts pass the checker.
**Displaced Path:** Keep the older `gross_2002_figure_01_association_mirror_*` artifacts as #275 acceptance evidence, but do not use them as full-replication proof.
**Evidence Lane:** #290 route receipt, Figure 1 retained source/model/plot artifacts, full-replication checker output, association acceptance checker output, docs validation, and cleanup hook.
**Acceptance Evidence:** Passing proof oracle commands plus rendered Figure 1 PNG/SVG and a score table showing all six component/branch series pass.
**Kill Criteria:** Stop the worker route if #290 is not merged or if the merged pure-associating saturation route cannot produce stable, certified vapor/liquid densities for all three alcohols with exact derivative metadata.
**Forbidden Moves:** Do not relabel the #275 AAD mirror as full replication; do not use synthetic source points; do not lower #279 thresholds; do not add electrolyte/reactive/generalized phase-count claims; do not bypass native route evidence with a Python-owned production solver.
**Risk If Wrong:** The project would claim association confidence before the package can reproduce the simplest pure associating saturation curves from the Gross paper, weakening the blocker chain before electrolyte work.

## Architecture Slice

**Files To Create:** `analyses/paper_validation/2002_gross/figures/figure_01/source/gross_2002_figure_01_replication_source.csv`, `analyses/paper_validation/2002_gross/figures/figure_01/source/gross_2002_figure_01_replication_metadata.json`, `analyses/paper_validation/2002_gross/figures/figure_01/source/gross_2002_figure_01_replication_qa_overlay.png`, `analyses/paper_validation/2002_gross/figures/figure_01/scripts/generate_gross_2002_figure_01_replication_data.py`, `analyses/paper_validation/2002_gross/figures/figure_01/scripts/render_gross_2002_figure_01_replication.py`, `analyses/paper_validation/2002_gross/figures/figure_01/results/gross_2002_figure_01_replication_model_curve.csv`, `analyses/paper_validation/2002_gross/figures/figure_01/results/gross_2002_figure_01_replication_plotted_data.csv`, `analyses/paper_validation/2002_gross/figures/figure_01/results/gross_2002_figure_01_replication_score.json`, `analyses/paper_validation/2002_gross/figures/figure_01/results/gross_2002_figure_01_replication_summary.json`, `analyses/paper_validation/2002_gross/figures/figure_01/results/gross_2002_figure_01_replication.png`, `analyses/paper_validation/2002_gross/figures/figure_01/results/gross_2002_figure_01_replication.svg`, `analyses/paper_validation/2002_gross/figures/figure_01/results/gross_2002_figure_01_replication.mpl.yaml`.
**Files To Modify:** `scripts/validation/check_gross_2002_full_replication.py`, `tests/native/contracts/test_gross_2002_full_replication_checker.py`, `analyses/paper_validation/2002_gross/shared/gross_2002_full_replication_manifest.json`, `analyses/paper_validation/2002_gross/shared/results/gross_2002_full_replication_summary.json`, `analyses/paper_validation/2002_gross/shared/results/gross_2002_full_replication_summary.csv`, `docs/superpowers/milestones/M4-equilibrium/README.md`.
**Files To Avoid:** Other Gross 2002 figure folders except shared campaign summary files, electrolyte/reactive code paths, regression package code, and downstream repositories.
**Source Of Truth:** Gross/Sadowski 2002 Figure 1 image, Table 1 alcohol parameter rows, and #279 checker schema.
**Read Path:** Source CSV and metadata feed the generation script; model CSV and source CSV feed the render script; score and summary JSON feed the manifest and checker.
**Write Path:** Figure-specific artifacts stay under `analyses/paper_validation/2002_gross/figures/figure_01`; shared status artifacts stay under `analyses/paper_validation/2002_gross/shared`.
**Integration Points:** Public `Equilibrium` route, native selector route, exact derivative/Ipopt diagnostics, full-replication checker, M4 milestone evidence table.
**Migration Or Cutover:** Keep #275 association mirror files intact, remove only owned `_placeholder.md` files from `figure_01/scripts` or `figure_01/results` when real files occupy those folders.
**Displaced Path Handling:** The old association mirror remains referenced only by the #275 acceptance checker and must not be listed as Figure 1 full-replication artifacts.
**Acceptance Evidence Gate:** The worker cannot mark #280 ready until the Figure 1 record is accepted by the full-replication checker and the final handoff renders the new plot inline.

## Acceptance Coverage

- Retain or digitize coexisting vapor/liquid density source data: Tasks 3 and 5.
- Generate PC-SAFT saturated vapor/liquid density model curves: Tasks 2 and 4.
- Render paper-scale `T-rho` mirror plot: Task 5.
- Write and enforce Figure 1 score JSON: Tasks 1, 4, and 6.
- Keep artifacts under `analyses/paper_validation/2002_gross/figures/figure_01`: Tasks 3-6.
- Preserve #275 association acceptance evidence: Tasks 5-7.

## Non-Goals

- No electrolyte, reactive, CE, CPE, or generalized phase-count admission.
- No changes to Figures 2-10 beyond shared summary readout.
- No broad associating-family capability claim beyond the pure 2B alcohol saturation evidence proven here.
- No package regression workflow changes.

### Task 1: Strengthen The Full-Replication Checker For Figure 1 Branch Coverage

**Use Cases:**
- A future Figure 1 record cannot pass with only liquid-density evidence.
- A score JSON missing methanol vapor, 1-pentanol liquid, or 1-nonanol vapor branch data produces a named blocker.
- Figure 1 acceptance requires `t_rho` threshold `>= 7.0` plus complete vapor/liquid branch coverage.
- The #279 foundation mode still passes with planned Figure 1 data.

**Files:**
- Modify: `scripts/validation/check_gross_2002_full_replication.py`
- Modify: `tests/native/contracts/test_gross_2002_full_replication_checker.py`
- Test: `tests/native/contracts/test_gross_2002_full_replication_checker.py`

- [ ] **Step 1: Add a failing branch-coverage test**

  Add a test that builds an accepted Figure 1 record with score JSON lacking a `vapor` branch and expects `gross_2002_figure_01_required_branch_vapor_missing`.

- [ ] **Step 2: Run the targeted test and verify failure**

  Run:

  ```powershell
  uv run --no-sync python run_pytest.py tests/native/contracts/test_gross_2002_full_replication_checker.py::test_figure_one_requires_vapor_and_liquid_branch_scores -q
  ```

  Expected before implementation: failure because the checker does not inspect Figure 1 branch detail.

- [ ] **Step 3: Add optional accepted-record branch validation**

  In `check_gross_2002_full_replication.py`, support an optional manifest field named `required_branches`. When present on an accepted record, require `score_json["branch_scores"]` to contain every branch token.

- [ ] **Step 4: Add the Figure 1 required branches to the manifest record**

  Update the Figure 1 manifest record with:

  ```json
  "required_branches": ["methanol:vapor", "methanol:liquid", "1-pentanol:vapor", "1-pentanol:liquid", "1-nonanol:vapor", "1-nonanol:liquid"]
  ```

- [ ] **Step 5: Run the full checker contract tests**

  Run:

  ```powershell
  uv run --no-sync python run_pytest.py tests/native/contracts/test_gross_2002_full_replication_checker.py -q
  ```

  Expected: all checker contract tests pass.

- [ ] **Step 6: Commit**

  Commit:

  ```powershell
  git add scripts/validation/check_gross_2002_full_replication.py tests/native/contracts/test_gross_2002_full_replication_checker.py analyses/paper_validation/2002_gross/shared/gross_2002_full_replication_manifest.json
  git commit -m "Require Gross 2002 Figure 1 branch coverage"
  ```

### Task 2: Verify The #290 Native Route Prerequisite

**Use Cases:**
- Methanol, 1-pentanol, and 1-nonanol model-curve generation consumes the merged #290 public route.
- #280 does not edit native route admission, selector guards, or capability metadata.
- The final Figure 1 handoff names the #290 route receipt and derivative metadata it consumed.

**Files:**
- Read: `docs/superpowers/issues/2026-06-19-m4-equilibrium-issue-0290-admit-pure-2b-associating-single-component-vle-prerequisite.md`
- Read: `docs/superpowers/plans/2026-06-19-m4-equilibrium-pure-2b-associating-single-component-vle-prerequisite-plan.md`
- Test: `packages/epcsaft-equilibrium/tests/api/test_single_component_vle.py`

- [ ] **Step 1: Confirm #290 is merged**

  Confirm GitHub issue #290 is closed by a merged PR before starting Figure 1 artifact work.

- [ ] **Step 2: Run the #290 route receipt test**

  Run:

  ```powershell
  uv run --no-sync python run_pytest.py packages/epcsaft-equilibrium/tests/api/test_single_component_vle.py packages/epcsaft-equilibrium/tests/contracts/test_activation_capabilities.py -q
  ```

  Expected: the pure 2B associating route test passes and reports exact derivative metadata.

- [ ] **Step 3: Keep Figure 1 branch scoped to artifacts**

  Do not modify `packages/epcsaft-equilibrium/src/epcsaft_equilibrium`, native C++ route files, activation metadata, or route capability tests in the Figure 1 PR. If the generator exposes a route defect, reopen or amend #290 instead of hiding the fix in #280.

### Task 3: Retain Figure 1 Source Data And Metadata

**Use Cases:**
- Reviewers can trace every plotted source point to either the retained Gross image digitization or a cited experimental source.
- The Figure 1 source CSV separates component and vapor/liquid branch identity.
- Axis calibration, units, uncertainty, and QA overlay are retained beside the source CSV.
- The old AAD source CSV remains available only for #275.

**Files:**
- Create: `analyses/paper_validation/2002_gross/figures/figure_01/source/gross_2002_figure_01_replication_source.csv`
- Create: `analyses/paper_validation/2002_gross/figures/figure_01/source/gross_2002_figure_01_replication_metadata.json`
- Create: `analyses/paper_validation/2002_gross/figures/figure_01/source/gross_2002_figure_01_replication_qa_overlay.png`
- Modify: `analyses/paper_validation/2002_gross/figures/figure_01/source/gross_2002_figure_01_digitization_metadata.json` only if it is superseded by the new replication metadata.

- [ ] **Step 1: Digitize or extract Figure 1 source points**

  Produce `gross_2002_figure_01_replication_source.csv` with columns:

  ```text
  figure_id,component,branch,T_K,density_kg_m3,density_mol_m3,source_kind,source_reference,digitized_x_px,digitized_y_px,uncertainty_T_K,uncertainty_density_kg_m3
  ```

- [ ] **Step 2: Write metadata**

  Write `gross_2002_figure_01_replication_metadata.json` with the #279 required fields plus:

  ```json
  {
    "figure_id": "figure_01",
    "plot_type": "T-rho",
    "source_image": "analyses/paper_validation/2002_gross/figures/figure_01/source/paper_source_01_gross_2002_figure_001.png",
    "series_labels": ["methanol:vapor", "methanol:liquid", "1-pentanol:vapor", "1-pentanol:liquid", "1-nonanol:vapor", "1-nonanol:liquid"]
  }
  ```

- [ ] **Step 3: Save the QA overlay**

  Save `gross_2002_figure_01_replication_qa_overlay.png` showing the retained paper image with calibration anchors and extracted points overlaid.

- [ ] **Step 4: Check source row coverage**

  Run a one-shot CSV check:

  ```powershell
  uv run --no-sync python -c "import pandas as pd; f=pd.read_csv('analyses/paper_validation/2002_gross/figures/figure_01/source/gross_2002_figure_01_replication_source.csv'); print(f.groupby(['component','branch']).size().to_string())"
  ```

  Expected: all six component/branch groups are present.

- [ ] **Step 5: Commit**

  Commit:

  ```powershell
  git add analyses/paper_validation/2002_gross/figures/figure_01/source/gross_2002_figure_01_replication_source.csv analyses/paper_validation/2002_gross/figures/figure_01/source/gross_2002_figure_01_replication_metadata.json analyses/paper_validation/2002_gross/figures/figure_01/source/gross_2002_figure_01_replication_qa_overlay.png
  git commit -m "Retain Gross 2002 Figure 1 source density points"
  ```

### Task 4: Generate Native Model Curves And Scores

**Use Cases:**
- The model CSV contains vapor and liquid density curves for all three Figure 1 alcohols.
- The score JSON proves branch-level agreement against retained source points.
- Solver diagnostics and native freshness evidence are retained in the summary JSON.
- The generation path is separate from rendering, so the plot can be reproduced without rerunning solves.

**Files:**
- Create: `analyses/paper_validation/2002_gross/figures/figure_01/scripts/generate_gross_2002_figure_01_replication_data.py`
- Create: `analyses/paper_validation/2002_gross/figures/figure_01/results/gross_2002_figure_01_replication_model_curve.csv`
- Create: `analyses/paper_validation/2002_gross/figures/figure_01/results/gross_2002_figure_01_replication_score.json`
- Create: `analyses/paper_validation/2002_gross/figures/figure_01/results/gross_2002_figure_01_replication_summary.json`

- [ ] **Step 1: Write the generation script**

  Create the script using the same repo-root and native-runtime setup pattern as `analyses/package_validation/equilibrium_single_component_vle/figures/hydrocarbon_saturation_pressure/scripts/generate_data.py`.

- [ ] **Step 2: Load Gross Table 1 alcohol parameters**

  Read `analyses/paper_validation/2002_gross/tables/table_001/table_001.csv` and construct one-component `ParameterSet` objects for methanol, 1-pentanol, and 1-nonanol with `MW`, `m`, `s`, `e`, `e_assoc`, `vol_a`, and 2B association topology.

- [ ] **Step 3: Solve native curves**

  For each component and source temperature span, call:

  ```python
  epcsaft_equilibrium.Equilibrium(mixture, route="single_component_vle", T=temperature).solve(
      solver_options={"max_iterations": 500, "tolerance": 1.0e-8}
  )
  ```

  Retain `rho_vapor_mol_m3`, `rho_liquid_mol_m3`, `rho_vapor_kg_m3`, `rho_liquid_kg_m3`, `P_sat_Pa`, solver status, route status, phase distance, pressure consistency norm, chemical potential consistency norm, and derivative metadata.

- [ ] **Step 4: Score model against source**

  Interpolate model curves onto source temperatures for each component/branch. Write branch score entries keyed by `component:branch`, then compute the top-level score JSON fields required by #279.

- [ ] **Step 5: Run generation**

  Run:

  ```powershell
  uv run --no-sync python analyses/paper_validation/2002_gross/figures/figure_01/scripts/generate_gross_2002_figure_01_replication_data.py
  ```

  Expected: model curve, score JSON, and summary JSON are written.

- [ ] **Step 6: Commit**

  Commit:

  ```powershell
  git add analyses/paper_validation/2002_gross/figures/figure_01/scripts/generate_gross_2002_figure_01_replication_data.py analyses/paper_validation/2002_gross/figures/figure_01/results/gross_2002_figure_01_replication_model_curve.csv analyses/paper_validation/2002_gross/figures/figure_01/results/gross_2002_figure_01_replication_score.json analyses/paper_validation/2002_gross/figures/figure_01/results/gross_2002_figure_01_replication_summary.json
  git commit -m "Generate Gross 2002 Figure 1 model density curves"
  ```

### Task 5: Render The Paper-Scale Figure 1 Replication

**Use Cases:**
- A reviewer can visually compare source points and PC-SAFT curves in the same coordinate orientation as Gross Figure 1.
- Rendering consumes retained CSVs and score metadata; it does not run native solves.
- The plotted-data CSV preserves exactly what was drawn.
- The old association mirror remains separate.

**Files:**
- Create: `analyses/paper_validation/2002_gross/figures/figure_01/scripts/render_gross_2002_figure_01_replication.py`
- Create: `analyses/paper_validation/2002_gross/figures/figure_01/results/gross_2002_figure_01_replication_plotted_data.csv`
- Create: `analyses/paper_validation/2002_gross/figures/figure_01/results/gross_2002_figure_01_replication.png`
- Create: `analyses/paper_validation/2002_gross/figures/figure_01/results/gross_2002_figure_01_replication.svg`
- Create: `analyses/paper_validation/2002_gross/figures/figure_01/results/gross_2002_figure_01_replication.mpl.yaml`
- Delete: `analyses/paper_validation/2002_gross/figures/figure_01/scripts/_placeholder.md` if the folder now has real scripts.
- Delete: `analyses/paper_validation/2002_gross/figures/figure_01/results/_placeholder.md` if the folder now has real full-replication results.

- [ ] **Step 1: Create the MPL sidecar**

  Write sidecar metadata with plot id, source CSV, model CSV, score JSON, axis labels, figure size, and command.

- [ ] **Step 2: Write the render script**

  Plot density on the x-axis and temperature on the y-axis. Use source markers and solid PC-SAFT curves for methanol, 1-pentanol, and 1-nonanol. Use separate visual encodings for vapor and liquid branches.

- [ ] **Step 3: Run rendering**

  Run:

  ```powershell
  uv run --no-sync python analyses/paper_validation/2002_gross/figures/figure_01/scripts/render_gross_2002_figure_01_replication.py
  ```

  Expected: PNG, SVG, sidecar, and plotted-data CSV are written.

- [ ] **Step 4: Inspect the plot**

  Verify visually that the axes, branch identities, source markers, and model curves match the paper plot type and scale.

- [ ] **Step 5: Remove owned placeholders**

  Remove `_placeholder.md` only from Figure 1 folders that now contain real full-replication scripts or results.

- [ ] **Step 6: Commit**

  Commit:

  ```powershell
  git add analyses/paper_validation/2002_gross/figures/figure_01
  git commit -m "Render Gross 2002 Figure 1 density replication"
  ```

### Task 6: Accept Figure 1 In The Full-Replication Manifest

**Use Cases:**
- The campaign checker recognizes Figure 1 as accepted and counted.
- The shared summary shows Figure 1 complete while Figure 2-10 blockers remain.
- M4 README distinguishes #280 evidence from #275 and #279 evidence.
- The live issue body and mirror point to this plan.
- Cutover evidence shows the Figure 1 manifest record moves from `planned` to `accepted` only after the new replication artifacts pass.
- Displaced path handling keeps `gross_2002_figure_01_association_mirror_*` as #275 evidence rather than #280 full-replication evidence.

**Files:**
- Modify: `analyses/paper_validation/2002_gross/shared/gross_2002_full_replication_manifest.json`
- Modify: `analyses/paper_validation/2002_gross/shared/results/gross_2002_full_replication_summary.json`
- Modify: `analyses/paper_validation/2002_gross/shared/results/gross_2002_full_replication_summary.csv`
- Modify: `docs/superpowers/issues/2026-06-19-m4-equilibrium-issue-0280-fully-replicate-gross-2002-figure-1-pure-component-density-curves.md`
- Modify: `docs/superpowers/milestones/M4-equilibrium/README.md`

- [ ] **Step 1: Update the Figure 1 manifest record**

  Set Figure 1 to:

  ```json
  "replication_status": "accepted",
  "counts_toward_completion": true,
  "artifacts": {
    "source_csv": "analyses/paper_validation/2002_gross/figures/figure_01/source/gross_2002_figure_01_replication_source.csv",
    "source_metadata_json": "analyses/paper_validation/2002_gross/figures/figure_01/source/gross_2002_figure_01_replication_metadata.json",
    "digitization_qa_overlay": "analyses/paper_validation/2002_gross/figures/figure_01/source/gross_2002_figure_01_replication_qa_overlay.png",
    "model_csv": "analyses/paper_validation/2002_gross/figures/figure_01/results/gross_2002_figure_01_replication_model_curve.csv",
    "plotted_csv": "analyses/paper_validation/2002_gross/figures/figure_01/results/gross_2002_figure_01_replication_plotted_data.csv",
    "score_json": "analyses/paper_validation/2002_gross/figures/figure_01/results/gross_2002_figure_01_replication_score.json",
    "summary_json": "analyses/paper_validation/2002_gross/figures/figure_01/results/gross_2002_figure_01_replication_summary.json",
    "png": "analyses/paper_validation/2002_gross/figures/figure_01/results/gross_2002_figure_01_replication.png",
    "svg": "analyses/paper_validation/2002_gross/figures/figure_01/results/gross_2002_figure_01_replication.svg",
    "sidecar": "analyses/paper_validation/2002_gross/figures/figure_01/results/gross_2002_figure_01_replication.mpl.yaml"
  }
  ```

- [ ] **Step 2: Refresh the shared summary**

  Run:

  ```powershell
  uv run --no-sync python scripts/validation/check_gross_2002_full_replication.py --json --require-foundation --write-summary
  ```

  Expected: shared summary records Figure 1 as accepted.

- [ ] **Step 3: Run the partial complete gate**

  Run:

  ```powershell
  uv run --no-sync python scripts/validation/check_gross_2002_full_replication.py --json --require-complete --require-exact-association-hessian --require-fresh-native
  ```

  Expected for #280 closeout: exit `2`, no `gross_2002_figure_01_*` blockers, and named blockers remain for Figure 2-10.

- [ ] **Step 4: Update docs and issue mirror**

  Link this plan in the #280 issue mirror and update M4 README retained evidence or queue notes with the Figure 1 replication result and plot path.

- [ ] **Step 5: Sync the live GitHub issue body**

  After local validation, update issue #280 from the corrected local mirror body.

- [ ] **Step 6: Commit**

  Commit:

  ```powershell
  git add analyses/paper_validation/2002_gross/shared/gross_2002_full_replication_manifest.json analyses/paper_validation/2002_gross/shared/results/gross_2002_full_replication_summary.json analyses/paper_validation/2002_gross/shared/results/gross_2002_full_replication_summary.csv docs/superpowers/issues/2026-06-19-m4-equilibrium-issue-0280-fully-replicate-gross-2002-figure-1-pure-component-density-curves.md docs/superpowers/milestones/M4-equilibrium/README.md
  git commit -m "Accept Gross 2002 Figure 1 replication evidence"
  ```

### Task 7: Final Verification And PR Handoff

**Use Cases:**
- The PR proves #280 without pretending the entire Gross 2002 campaign is complete.
- The final chat/handoff renders the new Figure 1 plot inline and includes source/model/score numerics.
- The repo is clean after validation.
- #281 remains the next ready figure-family issue after #280 merges.

**Files:**
- Test: `scripts/validation/check_gross_2002_full_replication.py`
- Test: `scripts/validation/check_gross_2002_association_acceptance.py`
- Test: `packages/epcsaft-equilibrium/tests/api/test_single_component_vle.py`
- Test: `tests/native/contracts/test_gross_2002_full_replication_checker.py`

- [ ] **Step 1: Build native equilibrium**

  Run:

  ```powershell
  uv run --no-sync python scripts/dev/build_epcsaft.py --profile equilibrium --build-only --parallel 4
  ```

- [ ] **Step 2: Run focused tests**

  Run:

  ```powershell
  uv run --no-sync python run_pytest.py packages/epcsaft-equilibrium/tests/api/test_single_component_vle.py tests/native/contracts/test_gross_2002_full_replication_checker.py -q
  ```

- [ ] **Step 3: Run campaign checkers**

  Run:

  ```powershell
  uv run --no-sync python scripts/validation/check_gross_2002_full_replication.py --json --require-complete --require-exact-association-hessian --require-fresh-native
  uv run --no-sync python scripts/validation/check_gross_2002_association_acceptance.py --json --require-complete --require-exact-association-hessian --require-fresh-native
  ```

  Expected: full-replication complete gate exits `2` because Figure 2-10 remain planned, but it has no Figure 1 blocker. Association acceptance exits `0`.

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

  The handoff must include the absolute Figure 1 PNG path, absolute SVG path, source row counts by component/branch, model row counts by component/branch, score table, derivative/native receipt status, and the remaining Figure 2-10 blockers.

## Proof Oracle

Required pass commands:

```powershell
uv run --no-sync python scripts/dev/build_epcsaft.py --profile equilibrium --build-only --parallel 4
uv run --no-sync python run_pytest.py packages/epcsaft-equilibrium/tests/api/test_single_component_vle.py tests/native/contracts/test_gross_2002_full_replication_checker.py -q
uv run --no-sync python scripts/validation/check_gross_2002_association_acceptance.py --json --require-complete --require-exact-association-hessian --require-fresh-native
uv run --no-sync python scripts/dev/validate_project.py docs
git diff --check
pwsh.exe -NoProfile -ExecutionPolicy Bypass -File "$env:USERPROFILE\.codex\hooks\codex-cleanup.ps1" -RepoRoot .
```

Required partial-campaign readout:

```powershell
uv run --no-sync python scripts/validation/check_gross_2002_full_replication.py --json --require-complete --require-exact-association-hessian --require-fresh-native
```

Expected for #280: exit `2`; Figure 1 has no blockers, and Figure 2-10 blockers remain until #281-#285 close.

## Risk Notes

- This issue is larger than a plot-only PR because native pure associating saturation is currently rejected at the public workflow layer.
- Native route admission must stay narrow: pure associating `single_component_vle` for the Gross Figure 1 alcohol evidence, not binary associating VLE.
- Digitization quality directly affects scores. The QA overlay and metadata must be reviewable.
- The Figure 1 paper plot compares PC-SAFT and SAFT. #280 only needs PC-SAFT model curves; SAFT lines should not be reproduced unless source data and implementation ownership are explicitly added.

## Recommended Implementation Route

Use `$superpowers-project:orchestrate-issues` for issue #280 after this plan is committed and the issue mirror points to it. Start #281 only after #280 is merged because the shared full-replication manifest and summary files are sequential campaign state.
