# M4 Equilibrium Gross 2002 Association Acceptance Pass

Milestone: `M4 - Equilibrium`
Affected package: `packages/epcsaft-equilibrium`
Related provider package: `packages/epcsaft` for association derivative evidence
Affected validation milestone: `M6 - Validation`
Status: `draft`
Created: `2026-06-18`

## Summary

This spec defines an improved association acceptance pass for the M4
equilibrium milestone using the Gross and Sadowski 2002 paper-validation
bundle. The acceptance evidence must live under the existing literature source
tree:

```text
analyses/paper_validation/2002_gross
```

The pass covers every relevant Gross 2002 figure, not only Figure 8. Figures 8
and 10 are the hard phase-split confidence gates because they contain
liquid-liquid or vapor-liquid-liquid behavior. Figure 1 is the pure
associating-component sanity gate. Figures 2-7 and 9 provide VLE mirror and
stress coverage for systems with at least one associating component.

The goal is to raise confidence that the association implementation landed as
the actual implicit association algorithm used by equilibrium routes: source
data, paper parameters, model predictions, exact derivative receipts, retained
plots, and campaign-level summaries must all agree. A merged PR or closed
issue is provenance only; this acceptance pass is the executable local evidence
that the implementation still works on the current checkout and native build.

## Scope Rule

All Gross 2002 association evidence stays attached to the paper-validation
source. Do not create a detached package-validation mirror for this campaign.

Per-figure source data, scripts, and results must stay inside the existing
figure lanes:

```text
analyses/paper_validation/2002_gross/figures/figure_01
analyses/paper_validation/2002_gross/figures/figure_02
...
analyses/paper_validation/2002_gross/figures/figure_10
```

Campaign-level summaries may live under:

```text
analyses/paper_validation/2002_gross/shared/results
```

The validation checker may live under `scripts/validation` because it is an
executable repo gate, but it must read and write retained evidence in the
paper-validation tree above.

## Project Context Evidence Used

- Verified: `docs/superpowers/PROJECT_CONTEXT.md` makes
  `docs/superpowers/milestones/M4-equilibrium/generalized-fluid-phase-equilibrium.md`
  the M4 GFPE doctrine and keeps capability claims tied to executable evidence.
- Verified:
  `docs/superpowers/milestones/M4-equilibrium/generalized-fluid-phase-equilibrium.md`
  lists Gross/Sadowski 2002 methanol/cyclohexane as the first associating
  validation target and names water/1-pentanol as the follow-on stress target.
- Verified:
  `analyses/paper_validation/2002_gross/shared/source/figures_manifest.csv`
  already records local source images for Figures 1-10.
- Verified:
  `analyses/paper_validation/2002_gross/tables/table_001/table_001.csv`
  records Gross 2002 pure-component association parameters for alkanols, water,
  amines, and acetic acid.
- Verified:
  `analyses/paper_validation/2002_gross/tables/table_002/table_002.csv`
  records Gross 2002 PC-SAFT binary interaction parameters, including
  methanol/cyclohexane, methanol/1-octanol, 1-pentanol/benzene, and
  water/1-pentanol.
- Verified:
  `data/reference/equilibrium_benchmarks/associating_lle/methanol_cyclohexane`
  already contains a source-backed Figure 8 methanol/cyclohexane fixture with
  digitized liquid-liquid points, Gross 2002 Table 1/2 parameters, and
  metadata linking to the retained Figure 8 image.
- Verified: the retained Figure 8 fixture uses methanol `assoc_scheme=2B`,
  `k_ij=0.051`, 1.013 bar, 16 source rows, source composition uncertainty
  0.02, source temperature uncertainty 2 K, and exact association-Hessian
  checks in the current validation gate.
- Verified: Gross 2002 states that all associating components in the paper use
  a two-site association model in this study.
- Inference: every Gross 2002 figure is relevant to association confidence
  because every figure contains at least one associating component or pure
  associating fluid.
- Inference: Figures 8 and 10 should be hard M4 associating phase-split gates
  because they exercise association inside liquid-liquid or
  vapor-liquid-liquid equilibrium, not only single-phase EOS properties or VLE.

## Figure Acceptance Matrix

| Figure | System | Association role | Acceptance role |
| --- | --- | --- | --- |
| Figure 1 | Methanol, 1-pentanol, 1-nonanol saturated liquid/vapor densities | Pure associating components | Required pure-association sanity mirror before broad phase-split claims |
| Figure 2 | Methanol with isobutane/isobutanol source-text discrepancy | One associating component VLE | Required source-resolution item before using this panel as evidence |
| Figure 3 | 1-propanol/ethylbenzene VLE | One associating component VLE | Supporting VLE mirror and derivative activation check |
| Figure 4 | 1-pentanol/benzene VLE | One associating component VLE | Supporting VLE mirror and binary-parameter check |
| Figure 5 | 1-propanol/benzene and 2-propanol/benzene VLE | One associating component VLE | Supporting isomer stress mirror |
| Figure 6 | 1-butanol/n-butane VLE | One associating component VLE | Supporting pressure/temperature stress mirror |
| Figure 7 | Ethanol/n-butane VLE | One associating component VLE | Supporting pressure/temperature stress mirror |
| Figure 8 | Methanol/cyclohexane isobaric VLE and LLE | One associating component plus nonassociating component | Hard primary associating LLE/VLE gate |
| Figure 9 | Methanol/1-octanol isobaric VLE | Two associating components | Supporting cross-association VLE mirror |
| Figure 10 | Water/1-pentanol isobaric heteroazeotropic VLE and LLE | Two associating components with water caveat | Hard cross-association VLLE/LLE stress gate |

Figure 2 has a source-resolution requirement because the local extracted table
row says `methanol-isobutanol`, while the figure caption says
`methanol-isobutane`. The implementation plan must resolve the PDF/source text
before any Figure 2 result is counted as campaign evidence.

## Architecture

### Per-Figure Layout

Each figure lane that participates in the campaign should use the same retained
artifact shape:

```text
analyses/paper_validation/2002_gross/figures/figure_NN/source/
  paper_source_01_gross_2002_figure_NNN.png
  gross_2002_figure_NN_digitized_points.csv
  gross_2002_figure_NN_digitization_metadata.json

analyses/paper_validation/2002_gross/figures/figure_NN/scripts/
  generate_gross_2002_figure_NN_association_data.py
  render_gross_2002_figure_NN_association_mirror.py

analyses/paper_validation/2002_gross/figures/figure_NN/results/
  gross_2002_figure_NN_model_curve.csv
  gross_2002_figure_NN_plotted_data.csv
  gross_2002_figure_NN_association_summary.json
  gross_2002_figure_NN_association_mirror.png
  gross_2002_figure_NN_association_mirror.svg
  gross_2002_figure_NN_association_mirror.pdf
```

The script names may be shortened during implementation, but the ownership and
artifact roles should remain stable: source data in `source`, generated model
and plot artifacts in `results`, reproducible scripts in `scripts`.

### Campaign Summary

The campaign checker should aggregate per-figure evidence into:

```text
analyses/paper_validation/2002_gross/shared/results/
  gross_2002_association_acceptance_summary.json
  gross_2002_association_acceptance_summary.csv
```

The summary must identify:

- figure id;
- source image path;
- digitized source table path;
- paper parameter rows used;
- binary parameter rows used;
- EOS/provider backend used;
- equilibrium route used;
- exact association derivative receipt;
- fresh native receipt for equilibrium-native checks;
- source-point count;
- model-point count;
- maximum source-to-model deviations in the figure's physical coordinates;
- pass/fail status;
- reason for any failed figure.

### Validation Checker

Add a single executable gate:

```text
scripts/validation/check_gross_2002_association_acceptance.py
```

The checker should support:

```powershell
uv run --no-sync python scripts/validation/check_gross_2002_association_acceptance.py --json --require-complete
```

Recommended optional flags:

```text
--figures figure_08 figure_10
--regenerate
--render
--require-exact-association-hessian
--require-fresh-native
--output-dir analyses/paper_validation/2002_gross/shared/results
```

The default complete run should require the hard gate figures and any
supporting figures marked campaign-ready in a local manifest. The checker must
not count a figure as skipped evidence. A figure is either outside the current
manifest scope or it has a concrete pass/fail result.

## Data Flow

1. Start from the paper-validation source image and paper tables already under
   `analyses/paper_validation/2002_gross`.
2. Digitize or reuse source points for each relevant figure. Every source CSV
   must carry physical units and digitization uncertainty.
3. Read pure parameters from `tables/table_001/table_001.csv` and binary
   parameters from `tables/table_002/table_002.csv`, with any nonassociating
   pure-component parameters linked to their retained source.
4. Generate model predictions using the current provider and equilibrium route
   intended for the figure family.
5. Record exact association derivative and mass-action receipts for every
   figure that exercises association in an equilibrium solve.
6. Render a retained mirror plot showing source data and model predictions
   together.
7. Aggregate per-figure summaries into the campaign summary.
8. The validation checker reads the retained artifacts and fails loudly when
   source data, model data, derivative receipts, fresh-native receipts, or plot
   PDF artifacts and provenance files are missing.

## Acceptance Criteria

- The campaign lives under `analyses/paper_validation/2002_gross`; no detached
  package-validation mirror is created for Gross 2002.
- Figure 8 remains the primary methanol/cyclohexane associating LLE/VLE gate
  and retains the existing source-backed fixture evidence.
- Figure 10 becomes the hard cross-association VLLE/LLE stress gate before
  electrolyte work uses associating GFPE confidence as a premise.
- Figure 1 is retained as a pure-association sanity mirror before broad claims
  about association implementation quality.
- Figures 2-7 and 9 are added as source-backed VLE mirrors when their source
  points and required nonassociating pure parameters are retained.
- Every accepted figure has a retained plot, retained plotted-data CSV,
  retained model-data CSV, retained summary JSON, and PDF artifact and provenance file.
- Every accepted associating equilibrium solve records exact association
  derivative evidence, mass-action residuals, site-bound checks, and the
  association contribution state.
- Every native-backed equilibrium campaign run records a fresh-native receipt:
  git commit, imported native module path, checker command, and build-refresh
  command or build freshness proof.
- Capability text is evidence-scoped. The pass may claim only the figure
  families and component configurations proven by retained artifacts.
- Unsupported broader families are absent from the acceptance matrix rather
  than represented by sentinel runtime states.
- Plot text is data-driven from retained summaries and cannot claim completion
  if the retained checker status is failed.

## Failure Behavior

The checker must fail loudly for:

- missing digitized source CSVs for figures inside the campaign manifest;
- missing physical units or digitization uncertainty;
- unresolved Figure 2 source identity;
- missing paper parameter provenance for nonassociating partner components;
- missing exact association derivative receipts;
- missing mass-action residual evidence for associating solves;
- stale or absent native freshness evidence when native equilibrium code is
  exercised;
- plot PDF artifacts and provenance files that do not match the plotted CSV data;
- campaign summaries generated from a different commit than the retained plot
  artifacts;
- any runtime path that substitutes an approximate association closure for the
  exact implicit association evidence required by this pass.

## Non-Goals

- No electrolyte admission is created by this spec.
- No HELD2.0 electrolyte validation is created by this spec.
- No reactive, CE, or CPE admission is created by this spec.
- No generalized phase-count or LLLE claim is created from a two-phase Gross
  2002 mirror.
- No public capability should be broadened beyond the exact retained Gross
  2002 figure evidence produced by the checker.
- No approximate association closure can satisfy this acceptance pass.

## Recommended Implementation Issue

Create one M4 child issue before #191 electrolyte execution:

```text
Title: M4: add Gross 2002 paper-validation association acceptance campaign
Milestone: M4 - Equilibrium
Package: packages/epcsaft-equilibrium
Validation owner: analyses/paper_validation/2002_gross
```

Issue acceptance:

- Add a manifest for Gross 2002 association acceptance under
  `analyses/paper_validation/2002_gross/shared`.
- Add per-figure source-data and result artifacts for the campaign-ready
  figures, starting with Figures 8 and 10 and preserving Figure 8's existing
  source fixture.
- Add generate/render scripts in each participating `figures/figure_NN/scripts`
  lane.
- Add `scripts/validation/check_gross_2002_association_acceptance.py`.
- Retain campaign summary JSON/CSV under
  `analyses/paper_validation/2002_gross/shared/results`.
- Render every new or updated mirror plot and include its retained data in the
  final issue handoff.
- Update M4 docs only where capability or validation evidence text changes.

Proof candidates:

```powershell
uv run --no-sync python scripts/dev/build_epcsaft.py --profile equilibrium --build-only --parallel 4
uv run --no-sync python scripts/validation/check_gross_2002_association_acceptance.py --json --require-complete --require-exact-association-hessian --require-fresh-native
uv run --no-sync python scripts/validation/check_associating_lle_gross_2002.py --json --require-source-data --require-exact-association-hessian --require-complete
uv run --no-sync python scripts/dev/validate_project.py docs
```

## Relationship To Existing M4 Work

- #145 provided the internal exact-Hessian associating LLE proof path for the
  Gross 2002 methanol/cyclohexane fixture.
- #190 provided the narrow public associating GFPE admission proof path.
- This spec raises the acceptance bar from "the narrow gate exists" to "the
  implementation reproduces the relevant Gross 2002 paper-validation campaign
  with retained source data, plots, exact derivative receipts, and fresh-native
  evidence."
- #191 electrolyte work should not depend on association confidence unless this
  campaign or a narrower explicitly approved issue records enough evidence for
  the association premise it uses.

## Self-Review

- Scope check: the campaign is tied to Gross/Sadowski 2002 paper validation,
  not a detached package-validation mirror.
- Figure check: the spec covers all relevant paper figures and marks Figures 8
  and 10 as hard phase-split gates.
- Evidence check: retained source data, retained model data, retained plots,
  exact derivative receipts, and fresh-native receipts are all required for
  accepted figures.
- Capability check: no electrolyte, reactive, CE, CPE, generalized phase-count,
  or broad public-family claim is created here.
- Source ambiguity check: Figure 2's caption/table discrepancy is called out as
  a required source-resolution item before evidence can count.
