# Gross 2002 Association Acceptance Campaign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [x]`) syntax for tracking.

**Goal:** Resolve GitHub issue #275 by turning the Gross/Sadowski 2002 paper-validation tree into an executable association acceptance campaign with retained source data, plots, exact association-Hessian evidence, and native freshness receipts.

**Architecture:** Keep the campaign attached to `analyses/paper_validation/2002_gross` and aggregate figure-local evidence through one validation checker. Figure 8 remains the public associating LLE proof, Figure 10 becomes the cross-associating VLLE/LLE stress gate, Figure 1 provides pure-association sanity evidence, and Figures 2-7 plus 9 are represented in the manifest with concrete source-readiness requirements instead of counted as accepted evidence before their source points are retained.

**Tech Stack:** Python validation scripts, Matplotlib retained figure artifacts, JSON/CSV manifests and summaries, existing Gross 2002 Figure 8 checker, CppAD implicit association diagnostics, `scripts.validation.native_freshness`, pytest through `run_pytest.py`, GitHub issue mirrors.

---

## Intake

- Source Spec: `docs/superpowers/specs/2026-06-18-m4-equilibrium-gross-2002-association-acceptance-pass.md`
- Source Issue: `docs/superpowers/issues/2026-06-18-m4-equilibrium-issue-0275-add-gross-2002-paper-validation-association-acceptance-campaign.md`
- GitHub Issue: `https://github.com/ePC-SAFT/ePC-SAFT/issues/275`
- Milestone: `M4 - Equilibrium`
- Package Owner: `packages/epcsaft-equilibrium`
- Validation Owner: `analyses/paper_validation/2002_gross`
- Existing proof dependency: `scripts/validation/check_associating_lle_gross_2002.py`
- Existing public admission gate: `scripts/validation/check_associating_gfpe_gate.py`

## Verified Planning Facts

- Verified: `analyses/paper_validation/2002_gross/shared/source/figures_manifest.csv` lists local source images for Figures 1-10.
- Verified: `analyses/paper_validation/2002_gross/tables/table_001/table_001.csv` stores Gross 2002 pure associating parameters and the source note that all associating components use two association sites in this paper.
- Verified: `analyses/paper_validation/2002_gross/tables/table_002/table_002.csv` stores Gross 2002 `k_ij` rows, including methanol/cyclohexane, methanol/1-octanol, and water/1-pentanol.
- Verified: Figure 2 has an unresolved source-text discrepancy: the retained caption says methanol-isobutane while Table 2 says methanol-isobutanol.
- Verified: `data/reference/equilibrium_benchmarks/associating_lle/methanol_cyclohexane` already contains source-backed Figure 8 source rows, parameters, thresholds, and exact association-Hessian checker coverage.
- Verified: no current Figure 1 or Figure 10 figure lane contains retained plotted data, model data, summary statistics, PDF artifacts, or provenance files.
- Inference: issue #275 can be closed only if the new checker fails loudly when the campaign manifest tries to count source-incomplete figures as accepted evidence.

## Test-Complete Definition And Metrics

Test complete means all issue #275 acceptance criteria are covered by retained artifacts and the commands below pass from the repo root:

- `uv run --no-sync python scripts/validation/check_gross_2002_association_acceptance.py --json --require-complete --require-exact-association-hessian --require-fresh-native`
- `uv run --no-sync python scripts/validation/check_associating_lle_gross_2002.py --json --require-source-data --require-exact-association-hessian --require-complete`
- `uv run --no-sync python run_pytest.py tests/native/contracts/test_gross_2002_association_acceptance_checker.py tests/native/contracts/test_associating_lle_gross_2002_checker.py -q`
- `uv run --no-sync python scripts/dev/validate_project.py docs`
- `pwsh.exe -NoProfile -ExecutionPolicy Bypass -File "$env:USERPROFILE\.codex\hooks\codex-cleanup.ps1" -RepoRoot .`

Numerical and structural pass metrics:

- Figure 8 source rows are at least the existing 16 retained Gross 2002 methanol/cyclohexane rows, pressure is `1.013 bar`, `k_ij` is `0.051`, methanol uses `assoc_scheme=2B`, cyclohexane has zero association sites, and exact association-Hessian status is `verified_exact`.
- Figure 10 source rows include both water-rich and 1-pentanol-rich liquid branches at `1.013 bar`, use Table 1 water and 1-pentanol pure parameters, use Table 2 `k_ij=0.016`, carry digitization uncertainty, and record the Gross 2002 water two-site caveat.
- Figure 1 accepted evidence records the Table 1 pure-association AAD values for methanol, 1-pentanol, and 1-nonanol and retains a plotted sanity mirror of those source AAD values with exact plotted CSV and PDF artifact and provenance file.
- Accepted visual figures have nonempty source CSV, model/evidence CSV, plotted-data CSV, summary JSON, PNG, SVG, and PDF artifacts under `figure_NN/results`; Figure 1 pure-association sanity evidence is retained as `association_fit_statistics.csv` rather than a bar-plot artifact.
- `--require-exact-association-hessian` requires exact implicit association evidence for Figure 8 and Figure 10; no approximate association closure evidence may satisfy that flag.
- `--require-fresh-native` requires a `native_freshness_receipt` with current git commit, native module path, checker command, and equilibrium build-refresh command.
- Figures 2-7 and 9 may remain outside accepted evidence only if the manifest records their concrete source-data requirements and the checker does not count them toward completion.

## Acceptance Criteria Mapping

- Manifest for participating figures, hard gates, routes, sources, parameters, and thresholds: Tasks 2 and 3.
- Existing Figure 8 fixture connected to campaign summary: Tasks 2, 4, and 5.
- Figure 10 hard cross-association stress gate: Tasks 2, 3, 4, and 5.
- Figure 1 pure-association sanity mirror: Tasks 2, 3, 4, and 5.
- Figures 2-7 and 9 campaign-ready source requirements and Figure 2 discrepancy: Tasks 2 and 3.
- Checker with `--json`, `--require-complete`, `--require-exact-association-hessian`, and `--require-fresh-native`: Tasks 2 and 4.
- Retained campaign summary JSON/CSV and plots: Tasks 4 and 5.
- Evidence-scoped capability text and tracker state: Tasks 1 and 6.

## Tasks

### Task 1: Link The Source Plan To Issue #275

**Use Cases:**
- The resolve-issue workflow needs #275 to have a concrete source plan before implementation begins.
- A reviewer needs the GitHub issue body and local mirror to name the exact implementation plan used for this PR.
- The issue mirror must remain AFK-ready after the plan gate passes.

**Files:**
- Create: `docs/superpowers/plans/2026-06-19-m4-equilibrium-issue-0275-gross-2002-association-acceptance-campaign-plan.md`
- Modify: `docs/superpowers/issues/2026-06-18-m4-equilibrium-issue-0275-add-gross-2002-paper-validation-association-acceptance-campaign.md`

- [x] **Step 1: Save this implementation plan.**

  Use the path above and keep the `Task N` sections with nonempty `**Use Cases:**` blocks.

- [x] **Step 2: Validate the plan.**

  Run:

  ```powershell
  uv run --no-sync python scripts/validate_plan_task_use_cases.py --plan-path docs/superpowers/plans/2026-06-19-m4-equilibrium-issue-0275-gross-2002-association-acceptance-campaign-plan.md
  ```

  Expected: exit code `0`, with every numbered task passing the use-case gate.

- [x] **Step 3: Update the local mirror.**

  Set `source_plan` in the YAML frontmatter and `**Source Plan:**` in the body to this plan path.

- [x] **Step 4: Update the GitHub issue body.**

  Use `gh issue edit 275 --body-file <updated-body-file>` or an equivalent body update so the live issue names this source plan.

- [x] **Step 5: Commit the plan link.**

  Run:

  ```powershell
  git add docs/superpowers/plans/2026-06-19-m4-equilibrium-issue-0275-gross-2002-association-acceptance-campaign-plan.md docs/superpowers/issues/2026-06-18-m4-equilibrium-issue-0275-add-gross-2002-paper-validation-association-acceptance-campaign.md
  git commit -m "Plan Gross 2002 association acceptance campaign"
  ```

### Task 2: Add The Red Campaign Checker Contract

**Use Cases:**
- `--require-complete` must fail when no Gross 2002 association campaign manifest exists.
- `--require-exact-association-hessian` must fail when hard-gate figures lack exact implicit association evidence.
- `--require-fresh-native` must fail when the checker output lacks a native freshness receipt.
- Figure 2 must not count as evidence while the methanol-isobutane versus methanol-isobutanol discrepancy is unresolved.

**Files:**
- Create: `tests/native/contracts/test_gross_2002_association_acceptance_checker.py`
- Create: `scripts/validation/check_gross_2002_association_acceptance.py`

- [x] **Step 1: Add failing schema and missing-manifest tests.**

  Create tests that import `scripts.validation.check_gross_2002_association_acceptance as checker`, call `checker.evaluate_campaign(require_complete=True)`, and assert missing artifacts produce named blockers:

  ```python
  assert "gross_2002_campaign_manifest_missing" in payload["blockers"]
  assert "gross_2002_figure_10_source_data_missing" in payload["blockers"]
  assert "gross_2002_figure_01_pure_association_mirror_missing" in payload["blockers"]
  ```

- [x] **Step 2: Add complete-payload tests for `evaluate_payload`.**

  Build an in-memory payload with accepted `figure_01`, `figure_08`, and `figure_10` records, source-requirement records for Figures 2-7 and 9, a `native_freshness_receipt`, and assert `complete is True` when all require flags are set.

- [x] **Step 3: Add CLI tests.**

  Call `checker.main(["--json", "--manifest", str(tmp_path / "missing.json"), "--require-complete"])` and assert exit code `2` plus JSON blockers.

- [x] **Step 4: Run red tests.**

  Run:

  ```powershell
  uv run --no-sync python run_pytest.py tests/native/contracts/test_gross_2002_association_acceptance_checker.py -q
  ```

  Expected before implementation: import failure or missing-manifest failure from the new tests.

### Task 3: Add The Campaign Manifest And Source Evidence

**Use Cases:**
- The campaign checker needs one manifest that names every relevant Gross 2002 figure and defines which figures are accepted hard gates versus source-requirement records.
- Figure 10 needs retained source rows, source uncertainties, water caveat, and paper parameter provenance before it can be a hard stress gate.
- Figure 1 needs retained pure-association source evidence before broad association-confidence text can point at pure-component sanity evidence.
- Figures 2-7 and 9 must be visible in the campaign without being counted as accepted evidence until their source points are retained.

**Files:**
- Create: `analyses/paper_validation/2002_gross/shared/gross_2002_association_acceptance_manifest.json`
- Create: `analyses/paper_validation/2002_gross/figures/figure_01/source/pure_association_aad.csv`
- Create: `analyses/paper_validation/2002_gross/figures/figure_01/source/digitization_notes.csv`
- Create: `analyses/paper_validation/2002_gross/figures/figure_10/source/gross_2002_figure_10_digitized_points.csv`
- Create: `analyses/paper_validation/2002_gross/figures/figure_10/source/gross_2002_figure_10_digitization_metadata.json`

- [x] **Step 1: Create the manifest with all ten figures.**

  Define `accepted_hard_gate` records for `figure_08` and `figure_10`, an `accepted_sanity_gate` record for `figure_01`, and `source_requirement` records for `figure_02` through `figure_07` plus `figure_09`.

- [x] **Step 2: Record Figure 1 source evidence.**

  Create a CSV containing methanol, 1-pentanol, and 1-nonanol with Table 1 `psat_aad_percent`, `liquid_density_aad_percent`, `temperature_range_K`, association scheme `2B`, and source table `table_001`.

- [x] **Step 3: Record Figure 10 source evidence.**

  Create a digitized source CSV with water-rich and 1-pentanol-rich liquid branch points at `1.013 bar`, columns for `temperature_K`, `x_water`, `x_1_pentanol`, `phase_branch`, `source_status`, `x_uncertainty`, and `temperature_uncertainty_K`.

- [x] **Step 4: Record metadata.**

  Add metadata JSON files naming source image paths, Gross 2002 Table 1/2 parameter rows, the water two-site caveat, and digitization uncertainties.

- [x] **Step 5: Re-run red tests.**

  Run:

  ```powershell
  uv run --no-sync python run_pytest.py tests/native/contracts/test_gross_2002_association_acceptance_checker.py -q
  ```

  Expected: failures move from missing manifest/source artifacts to missing checker behavior and retained result artifacts.

### Task 4: Implement The Campaign Checker

**Use Cases:**
- Local validation needs one command that reads retained Gross 2002 evidence and produces a campaign-level pass/fail payload.
- Accepted figures must fail loudly when source CSVs, model/evidence CSVs, plotted-data CSVs, summaries, PDF artifacts and provenance files, exact Hessian receipts, or native freshness receipts are absent.
- Figure 8 must reuse the existing source-backed checker instead of duplicating its scientific contract.
- Figure 10 must exercise exact implicit association diagnostics for the water/1-pentanol cross-association parameter bundle without expanding public route admission.

**Files:**
- Modify: `scripts/validation/check_gross_2002_association_acceptance.py`
- Modify: `tests/native/contracts/test_gross_2002_association_acceptance_checker.py`
- Modify: `analyses/paper_validation/2002_gross/shared/results/gross_2002_association_acceptance_summary.json`
- Modify: `analyses/paper_validation/2002_gross/shared/results/gross_2002_association_acceptance_summary.csv`

- [x] **Step 1: Implement manifest loading and payload evaluation.**

  Add pure functions that read the manifest, validate figure roles, collect blockers, and expose `evaluate_payload` for testable in-memory payloads.

- [x] **Step 2: Connect Figure 8.**

  Call `check_associating_lle_gross_2002.evaluate_case_dir(..., require_source_data=True, require_exact_association_hessian=True, require_internal_route=True)` and copy its exact-Hessian and source-row metrics into the campaign figure record.

- [x] **Step 3: Add Figure 10 exact association diagnostics.**

  Build a water/1-pentanol native mixture from Gross 2002 Tables 1/2, sample representative liquid compositions from the retained Figure 10 source CSV, call the provider and equilibrium native association diagnostic hooks, and record site-fraction bounds, mass-action residual, and Hessian symmetry metrics.

- [x] **Step 4: Add native freshness receipt support.**

  When `--require-fresh-native` or `--require-complete` is set, call `scripts.validation.native_freshness.build_receipt` with `epcsaft_equilibrium._native` and the checker command.

- [x] **Step 5: Write campaign summaries.**

  Write JSON and CSV summaries under `analyses/paper_validation/2002_gross/shared/results`, including one row per figure and explicit `counts_toward_completion` fields.

- [x] **Step 6: Run focused checker tests.**

  Run:

  ```powershell
  uv run --no-sync python run_pytest.py tests/native/contracts/test_gross_2002_association_acceptance_checker.py -q
  ```

  Expected: all new checker contract tests pass.

### Task 5: Generate And Retain Figure Artifacts

**Use Cases:**
- Reviewers need visible source-versus-model/evidence plots for the accepted Gross 2002 figures.
- MPLGallery and local artifact review need PNG/SVG outputs, plotted-data CSV snapshots, and PDF artifacts in each figure results folder.
- The final handoff must render every new or updated plot inline and include a compact table of retained source data.

**Files:**
- Create: `analyses/paper_validation/2002_gross/figures/figure_01/results/association_fit_statistics.csv`
- Create: `analyses/paper_validation/2002_gross/figures/figure_08/scripts/render_gross_2002_figure_08_association_mirror.py`
- Create: `analyses/paper_validation/2002_gross/figures/figure_10/scripts/render_gross_2002_figure_10_association_mirror.py`
- Create: retained result files in `analyses/paper_validation/2002_gross/figures/figure_01/results/`
- Create: retained result files in `analyses/paper_validation/2002_gross/figures/figure_08/results/`
- Create: retained result files in `analyses/paper_validation/2002_gross/figures/figure_10/results/`

- [x] **Step 1: Add Figure 1 render script.**

  Read the Figure 1 pure-association AAD CSV, write model/evidence CSV and plotted-data CSV, then render a bar/point mirror showing vapor-pressure and liquid-density AAD values for methanol, 1-pentanol, and 1-nonanol.

- [x] **Step 2: Add Figure 8 render script.**

  Read the existing Gross 2002 methanol/cyclohexane source fixture and checker output, write plotted-data/model CSVs, then render a source branch mirror with the public associating route point.

- [x] **Step 3: Add Figure 10 render script.**

  Read the retained Figure 10 source CSV and checker diagnostics, write plotted-data/model CSVs, then render a water-rich and 1-pentanol-rich source/evidence mirror with explicit text that this is a cross-association stress gate, not public electrolyte admission.

- [x] **Step 4: Run the render scripts.**

  Run:

  ```powershell
  uv run --no-sync python -c "from scripts.validation import check_gross_2002_association_acceptance as c; c.render_figure('figure_01')"
  uv run --no-sync python analyses/paper_validation/2002_gross/figures/figure_08/scripts/render_gross_2002_figure_08_association_mirror.py
  uv run --no-sync python analyses/paper_validation/2002_gross/figures/figure_10/scripts/render_gross_2002_figure_10_association_mirror.py
  ```

  Expected: each script writes `.csv`, `.json`, `.png`, `.svg`, and `.pdf` artifacts to its figure `results` folder.

- [x] **Step 5: Run the complete checker.**

  Run:

  ```powershell
  uv run --no-sync python scripts/validation/check_gross_2002_association_acceptance.py --json --require-complete --require-exact-association-hessian --require-fresh-native
  ```

  Expected: exit code `0`, `complete: true`, accepted figures `figure_01`, `figure_08`, and `figure_10`, and no completion credit for source-requirement figures.

### Task 6: Update Docs, Mirror, And Closeout Evidence

**Use Cases:**
- The M4 docs need to explain what the campaign proves without broadening electrolyte, reactive, CE, CPE, LLLE, or generalized phase-count claims.
- The #275 mirror needs acceptance boxes and proof oracle updated to match the retained artifacts.
- The PR body needs exact commands, artifact paths, plots, and issue-closing language.

**Files:**
- Modify: `docs/superpowers/issues/2026-06-18-m4-equilibrium-issue-0275-add-gross-2002-paper-validation-association-acceptance-campaign.md`
- Modify: `docs/superpowers/milestones/M4-equilibrium/README.md`
- Modify: `docs/superpowers/milestones/M4-equilibrium/generalized-fluid-phase-equilibrium.md`

- [x] **Step 1: Update documentation.**

  Add a concise M4 note that Gross 2002 association confidence is now evidence-scoped to accepted campaign figures and does not admit electrolyte or reactive routes.

- [x] **Step 2: Update the issue mirror.**

  Check off completed acceptance criteria, preserve non-goals, and keep the proof oracle commands exact.

- [x] **Step 3: Run proof oracle.**

  Run:

  ```powershell
  uv run --no-sync python scripts/dev/build_epcsaft.py --profile equilibrium --build-only --parallel 4
  uv run --no-sync python scripts/validation/check_gross_2002_association_acceptance.py --json --require-complete --require-exact-association-hessian --require-fresh-native
  uv run --no-sync python scripts/validation/check_associating_lle_gross_2002.py --json --require-source-data --require-exact-association-hessian --require-complete
  uv run --no-sync python run_pytest.py tests/native/contracts/test_gross_2002_association_acceptance_checker.py tests/native/contracts/test_associating_lle_gross_2002_checker.py -q
  uv run --no-sync python scripts/dev/validate_project.py docs
  pwsh.exe -NoProfile -ExecutionPolicy Bypass -File "$env:USERPROFILE\.codex\hooks\codex-cleanup.ps1" -RepoRoot .
  ```

  Expected: every command exits `0`.

- [x] **Step 4: Commit implementation.**

  Run:

  ```powershell
  git add analyses/paper_validation/2002_gross docs/superpowers scripts/validation tests/native/contracts
  git commit -m "Add Gross 2002 association acceptance campaign"
  ```

- [x] **Step 5: Push and open PR.**

  After artifact review and native push permission, push the branch and open a PR whose body includes `Closes #275`.

## Proof Oracle

```powershell
uv run --no-sync python scripts/dev/build_epcsaft.py --profile equilibrium --build-only --parallel 4
uv run --no-sync python scripts/validation/check_gross_2002_association_acceptance.py --json --require-complete --require-exact-association-hessian --require-fresh-native
uv run --no-sync python scripts/validation/check_associating_lle_gross_2002.py --json --require-source-data --require-exact-association-hessian --require-complete
uv run --no-sync python run_pytest.py tests/native/contracts/test_gross_2002_association_acceptance_checker.py tests/native/contracts/test_associating_lle_gross_2002_checker.py -q
uv run --no-sync python scripts/dev/validate_project.py docs
pwsh.exe -NoProfile -ExecutionPolicy Bypass -File "$env:USERPROFILE\.codex\hooks\codex-cleanup.ps1" -RepoRoot .
```

## Non-Goals And Boundaries

- No electrolyte route admission.
- No HELD2 electrolyte validation.
- No reactive, CE, or CPE admission.
- No generalized phase-count or LLLE claim from Gross 2002 evidence.
- No broad public claim for every associating family; accepted evidence is limited to the retained figure rows and diagnostics.
- No approximate association closure can satisfy the exact-Hessian acceptance gate.
