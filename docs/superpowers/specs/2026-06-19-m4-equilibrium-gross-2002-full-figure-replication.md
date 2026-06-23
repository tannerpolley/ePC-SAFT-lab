# M4 Equilibrium Gross 2002 Full Figure Replication

Milestone: `M4 - Equilibrium`
Affected package: `packages/epcsaft-equilibrium`
Related provider package: `packages/epcsaft`
Validation root: `analyses/paper_validation/2002_gross`
Status: `draft`
Created: `2026-06-19`

## Summary

This spec defines the next Gross and Sadowski 2002 validation campaign: full
curve-level replication of every retained paper figure, using either cited
source data or calibrated digitization from the retained paper images. The goal
is to move beyond the #275 association acceptance campaign, which proved the
campaign infrastructure and exact association derivative evidence for Figures
1, 8, and 10, but did not reproduce every plotted PC-SAFT curve or every paper
figure.

Completion requires retained source data, model predictions, paper-scale plots,
digitization QA overlays, numerical plot-match scores, derivative receipts, and
checker gates for Figures 1-10. Plots created by this campaign must match the
type, axes, scale, and plotted physical coordinates of the Gross 2002 paper
figures. A figure cannot count as fully replicated unless the checker can score
the model output against retained source data in the same coordinate system as
the paper plot.

## User Decisions

- Replication standard: curve-level proof.
- Source acquisition policy: hybrid source-first. Try to locate or extract the
  cited experimental source data first; when that is impractical for a figure,
  use calibrated digitization of the retained Gross 2002 paper image with a QA
  overlay and recorded uncertainty.
- Execution shape: one full-replication spec with family-sliced plans and
  issues. Do not attempt all ten figures in one implementation PR.
- Visual companion: text-only brainstorming for this spec.

## Project Context Evidence Used

- Verified: `docs/superpowers/PROJECT_CONTEXT.md` makes the M4 GFPE doctrine
  evidence-gated. Capability claims must match executable local evidence.
- Verified: `docs/superpowers/milestones/M4-equilibrium/generalized-fluid-phase-equilibrium.md`
  currently records the #275 Gross 2002 acceptance proof as evidence-scoped to
  Figures 1, 8, and 10, and says Figures 2-7 and 9 remain source-requirement
  records until source points and provenance are retained.
- Verified: `analyses/paper_validation/2002_gross/shared/source/figures_manifest.csv`
  records source images and captions for Figures 1-10.
- Verified: `analyses/paper_validation/2002_gross/docs/md/source_01_gross_2002.md`
  records the local paper text, figure captions, the two-site association
  statement for all associating substances in this work, and the Figure 10
  water caveat.
- Verified: `analyses/paper_validation/2002_gross/tables/table_001/table_001.csv`
  records pure associating parameters and AAD values for the Gross 2002
  associating substances.
- Verified: `analyses/paper_validation/2002_gross/tables/table_002/table_002.csv`
  records the Gross 2002 binary `k_ij` rows for Figures 2-10.
- Verified: #275 added retained result artifacts for Figures 1, 8, and 10 only.
  Figures 2-7 and 9 still have source images but no retained source CSV,
  digitization metadata, model data, mirror plot, score summary, or derivative
  evidence.
- Verified: the current Gross 2002 campaign checker reports accepted evidence
  for `figure_01`, `figure_08`, and `figure_10`, while `figure_02`,
  `figure_03`, `figure_04`, `figure_05`, `figure_06`, `figure_07`, and
  `figure_09` remain source-requirement records with no completion credit.
- Verified: the only open M4 GitHub issue matching this area during intake was
  #191. There is no separate open issue set for full Gross 2002 figure
  replication.
- Inference: full Gross 2002 reproduction should remain a prerequisite-quality
  confidence campaign for association work before broader electrolyte or
  reactive equilibrium work relies on associating GFPE behavior.

## Non-Goals

- No electrolyte admission.
- No reactive, CE, CPE, or generalized phase-count admission.
- No claim that the Gross 2002 campaign proves all associating families.
- No broad package API change.
- No detached validation mirror outside `analyses/paper_validation/2002_gross`.
- No acceptance credit for a figure that only has a source image, table AAD
  values, a representative diagnostic point, or an unscored plot.

## Recommended Approach

Use family-sliced curve replication.

One spec owns the full Gross 2002 replication doctrine. Later plans and issues
should split the work into reviewable implementation slices:

1. Full-replication checker and scoring foundation.
2. Figure 1 pure-component saturated density curve replication.
3. Figures 2-5 subcritical self-associating VLE replication.
4. Figures 6-7 supercritical-partner self-associating VLE replication.
5. Figure 8 methanol/cyclohexane LLE+VLE envelope upgrade.
6. Figure 9 methanol/1-octanol cross-associating VLE replication.
7. Figure 10 water/1-pentanol VLLE/LLE envelope upgrade.

This approach keeps each PR small enough to review, lets failed figures report
independent blockers, and prevents one hard phase-split figure from blocking
source-data progress for simpler VLE figures.

## Figure Replication Matrix

| Figure | Paper plot type | System | Current evidence | Required full-replication work |
| --- | --- | --- | --- | --- |
| 1 | `T-rho` saturated vapor/liquid densities | methanol, 1-pentanol, 1-nonanol | Table AAD sanity mirror only | Extract or digitize coexisting density data, generate PC-SAFT density curves, render paper-scale `T-rho` plot, score vapor and liquid branches |
| 2 | isothermal VLE `P-x/y` | methanol-isobutane caption versus methanol-isobutanol table row | source image only | Resolve identity, retain source data, prove pure-parameter provenance, generate PC-SAFT VLE curve at 100 degC, score pressure and composition |
| 3 | VLE at two pressures | 1-propanol/ethylbenzene | source image only | Retain both pressure panels/series, generate matching VLE curves, score each pressure series |
| 4 | isothermal VLE `P-x/y` | 1-pentanol/benzene | source image only | Retain source points, generate 40 degC VLE curve, score pressure/composition |
| 5 | isothermal VLE `P-x/y` with two isomer systems | 1-propanol/benzene and 2-propanol/benzene | source image only | Retain both systems with series identity, generate both curves, score each isomer system separately |
| 6 | VLE at four temperatures | 1-butanol/n-butane | source image only | Retain all four temperature series, generate matching curves, score each temperature |
| 7 | VLE at four temperatures | ethanol/n-butane | source image only | Retain all four temperature series, generate matching curves, score each temperature and record the supercritical-partner caveat |
| 8 | isobaric VLE and LLE `T-x` | methanol/cyclohexane | selected LLE branch evidence and exact association-Hessian receipt | Upgrade to full LLE+VLE envelope reproduction at 1.013 bar, score branches and azeotrope/plait-region behavior |
| 9 | isobaric VLE `T-x` | methanol/1-octanol | source image only | Retain source data, generate cross-associating VLE curve at 1.013 bar, score temperature/composition |
| 10 | isobaric VLLE/LLE `T-x` | water/1-pentanol | digitized source rows plus one exact diagnostic sample | Upgrade to full water-rich, alcohol-rich, and vapor/VLLE envelope reproduction at 1.013 bar, score each branch and keep water two-site caveat |

## Architecture

The campaign is layered on top of the merged #275 acceptance campaign. It
keeps the same source ownership and adds a stricter full-replication gate.

Canonical artifact layout:

```text
analyses/paper_validation/2002_gross/figures/figure_NN/source/
  paper_source_01_gross_2002_figure_NNN.png
  gross_2002_figure_NN_digitized_points.csv
  gross_2002_figure_NN_digitization_metadata.json
  gross_2002_figure_NN_digitization_qa_overlay.png

analyses/paper_validation/2002_gross/figures/figure_NN/scripts/
  generate_gross_2002_figure_NN_replication_data.py
  render_gross_2002_figure_NN_replication.py

analyses/paper_validation/2002_gross/figures/figure_NN/results/
  gross_2002_figure_NN_replication_model_curve.csv
  gross_2002_figure_NN_replication_plotted_data.csv
  gross_2002_figure_NN_replication_score.json
  gross_2002_figure_NN_replication_summary.json
  gross_2002_figure_NN_replication.png
  gross_2002_figure_NN_replication.svg
  gross_2002_figure_NN_replication.pdf
```

The existing #275 result files may remain as association-acceptance artifacts.
Full-replication artifacts should use the `replication` stem so reviewers can
distinguish diagnostic acceptance mirrors from curve-level paper reproduction.
Existing `_placeholder.md` files in figure lanes should be removed once real
source, script, or result files occupy the folder.

## Components

### Source Acquisition

For each figure, source acquisition must:

- read the local Gross 2002 caption and figure image;
- identify cited experimental references when the paper names them;
- attempt source-data extraction from cited data when practical;
- otherwise use calibrated digitization from the retained paper image;
- write source CSV, metadata JSON, and QA overlay PNG;
- record axis calibration, units, series names, source provenance, and
  digitization uncertainty.

The spec does not require cited-source extraction when it would block progress
indefinitely. It requires honest provenance and quantified uncertainty.

### Model Generation

Model generation must produce CSV data in the same coordinate family as the
paper figure:

- Figure 1: saturated vapor and liquid density versus temperature.
- Figures 2, 4, and 5: isothermal VLE pressure/composition curves.
- Figures 3, 6, and 7: VLE curves for the pressure or temperature series shown.
- Figures 8, 9, and 10: isobaric `T-x` phase boundary curves and phase-split
  branches.

Native-backed equilibrium routes must emit fresh-native receipts, exact
association derivative receipts, mass-action residuals, site-fraction bounds,
and solver status summaries.

### Rendering

Render scripts must read retained source and model CSVs. They should not perform
long model solves inside the plotting path. Each rendered plot must match the
paper's plot type and scale, including axis direction, units, legend semantics,
and branch styling where practical. Every plot must have a PNG, SVG, plotted
data CSV, and MPLGallery-registered SVG.

### Scoring

Each figure must have a retained score JSON with:

- source point count by series;
- model point count by series;
- axis-coordinate RMSE after interpolation onto source coordinates;
- maximum axis error;
- normalized plot-coordinate score from 0 to 10;
- branch coverage score;
- pass/fail status;
- score caveats.

Score thresholds should be figure-family specific. Initial planning should use
these default gates unless source inspection justifies tighter or looser limits:

- `T-rho` pure component curves: score >= 7.0 and both vapor and liquid branch
  coverage present.
- VLE curves: score >= 7.0 per required series.
- LLE/VLLE phase boundaries: score >= 6.5 per required branch plus exact
  association derivative status `verified_exact`.
- Diagnostic-only evidence: score cannot exceed 4.0 and cannot satisfy full
  replication.

### Campaign Validation

Add a strict full-replication checker, either as a new sibling checker:

```text
scripts/validation/check_gross_2002_full_replication.py
```

or as a strict mode in the existing checker:

```text
scripts/validation/check_gross_2002_association_acceptance.py --require-full-replication
```

The recommended path is a sibling checker so #275 acceptance and full
reproduction stay distinct.

## Data Flow

1. Read Gross 2002 figure metadata from the retained paper source and manifest.
2. Resolve Table 1 pure parameters and Table 2 binary `k_ij` rows.
3. For nonassociating partner components, retain or link pure-parameter
   provenance before model generation can count.
4. Acquire source data through cited data extraction or calibrated paper-image
   digitization.
5. Generate model curve or envelope data with the current provider and
   equilibrium route.
6. Write exact derivative and solver receipts for associating equilibrium
   solves.
7. Render paper-scale mirror plots from retained source and model data.
8. Score model-vs-source agreement in paper-figure coordinates.
9. Aggregate all figure records into a shared full-replication summary.
10. The checker fails when any figure marked accepted lacks required artifacts
    or misses its score gate.

## Error Handling

The full-replication checker must fail loudly for:

- missing source CSVs;
- missing calibration metadata;
- missing digitization QA overlays;
- ambiguous axis units or basis;
- unresolved Figure 2 source identity;
- missing pure or binary parameter provenance;
- model domain that does not cover the paper plot;
- missing exact association derivative receipts for associating equilibrium
  routes;
- missing native freshness receipts for native-backed model generation;
- missing mirror plot, SVG, PNG, plotted-data CSV, or PDF artifact and provenance file;
- score below the figure-family threshold.

Figure 2 remains blocked from acceptance until the methanol-isobutane caption
versus methanol-isobutanol Table 2 discrepancy is resolved from the paper text,
source reference, or another retained provenance artifact.

## Testing And Proof Oracles

The implementation plan should start with red tests for a strict checker. Tests
must show that a figure marked accepted fails if it lacks source data, metadata,
QA overlay, model curve, plot, PDF artifact and provenance file, score summary, or required derivative
receipts.

Candidate proof commands:

```powershell
uv run --no-sync python scripts/dev/build_epcsaft.py --profile equilibrium --build-only --parallel 4
uv run --no-sync python scripts/validation/check_gross_2002_full_replication.py --json --require-complete --require-exact-association-hessian --require-fresh-native
uv run --no-sync python scripts/validation/check_gross_2002_association_acceptance.py --json --require-complete --require-exact-association-hessian --require-fresh-native
uv run --no-sync python scripts/validation/check_associating_lle_gross_2002.py --json --require-source-data --require-exact-association-hessian --require-complete
uv run --no-sync python run_pytest.py tests/native/contracts/test_gross_2002_full_replication_checker.py tests/native/contracts/test_gross_2002_association_acceptance_checker.py tests/native/contracts/test_associating_lle_gross_2002_checker.py -q
uv run --no-sync python scripts/dev/validate_project.py docs
pwsh.exe -NoProfile -ExecutionPolicy Bypass -File "$env:USERPROFILE\.codex\hooks\codex-cleanup.ps1" -RepoRoot .
```

Final handoffs for implementation issues must render every new or updated plot
inline and include a compact table with source row count, model row count,
score, derivative status, and pass/fail state for each touched figure.

## Issue Decomposition Candidates

The next workflow should create issue mirrors under M4 with these likely slices:

1. `M4: add Gross 2002 full-replication checker and scoring schema`
2. `M4: fully replicate Gross 2002 Figure 1 pure-component density curves`
3. `M4: fully replicate Gross 2002 Figures 2-5 self-associating VLE curves`
4. `M4: fully replicate Gross 2002 Figures 6-7 supercritical-partner VLE curves`
5. `M4: upgrade Gross 2002 Figure 8 to full LLE+VLE envelope replication`
6. `M4: fully replicate Gross 2002 Figure 9 cross-associating VLE curve`
7. `M4: upgrade Gross 2002 Figure 10 to full VLLE/LLE envelope replication`

The first issue should create the checker contract, score schema, source-data
metadata schema, and manifest changes. Figure-specific issues should depend on
that foundation.

## Acceptance Criteria

- All ten Gross 2002 figures are represented in the full-replication manifest.
- Every accepted figure has retained source data, metadata, QA overlay, model
  data, mirror plot, PDF artifact and provenance file, score JSON, and summary JSON.
- Generated plots match the paper plot type and scale rather than using
  diagnostic substitutes.
- Figures 2-7 and 9 no longer remain source-requirement records once their
  curve-level evidence lands.
- Figures 1, 8, and 10 are upgraded from #275 acceptance mirrors or diagnostic
  samples to full curve or envelope replication.
- The checker reports per-figure scores and fails when any required score is
  below threshold.
- Exact association derivative evidence is required for accepted associating
  equilibrium route solves.
- Capability text stays scoped to the replicated figure families and does not
  claim electrolyte, reactive, CE, CPE, generalized phase-count, or broad
  associating-family admission.

## Current Risks

- Figure 2 source identity is inconsistent between caption and Table 2.
- Figures 8 and 10 require more than selected diagnostic points; full envelope
  generation may expose route limitations that need separate implementation
  work.
- Cited experimental references may be harder to extract than paper-image
  digitization, so the hybrid source policy must be retained per figure.
- Plot-match scores depend on calibration quality. QA overlays are required to
  keep the scores reviewable.
- The project workflow-mode validator referenced by
  `superpowers-project:initiate-workflow` was absent during this brainstorm.
  The run ledger records this as a routing-tooling gap, not as a validation
  pass.

## Recommended Next Route

Run `$superpowers-project:create-issues` from this spec to create the M4 issue
set above, then use `$superpowers-project:write-plan` for the foundation issue:
the strict checker, scoring schema, source-data metadata schema, and manifest
upgrade. Figure-specific execution should wait until that foundation issue is
ready.
