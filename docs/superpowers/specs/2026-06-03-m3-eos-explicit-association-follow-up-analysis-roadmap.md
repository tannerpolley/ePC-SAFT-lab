# Explicit Association Follow-Up Analysis Roadmap

## Purpose

This loose spec captures the follow-up analysis that should come after the
current explicit association toybox results. The existing toybox now proves the
basic mechanics: exact Huang/Radosz topology reductions can be compared against
the generic mass-action baseline, explicit approximations can be ranked, public
saturation rows can feed fixed-state diagnostics, and plots/tables can be
retained under the analysis folder.

The next question is sharper:

```text
Which explicit association closures remain plausible after topology-resolved
error maps, real-system topology mapping, derivative smoothness checks,
pressure residual reframing, repeated timing, water-specific parameter lanes,
and total residual Helmholtz context are added?
```

This remains analysis work. It should improve evidence quality before any
provider EOS implementation, equilibrium admission, or public API change is
proposed.

## Project Context Evidence Used

- `docs/superpowers/PROJECT_CONTEXT.md` identifies the explicit association
  closure derivation as M3 EOS evidence and warns agents not to treat synthetic
  toybox grids as real closure proof.
- `docs/superpowers/specs/2026-05-23-m3-eos-explicit-association-closure-for-pcsaft.md`
  separates exact implicit association from explicit approximations and keeps
  CppAD derivative claims scoped to the model being differentiated.
- `docs/superpowers/specs/2026-06-03-m3-eos-paper-backed-association-closure-validation-matrix-design.md`
  defines the validation matrix shape and the Huang/Radosz topology crosswalk.
- `docs/superpowers/plans/2026-06-03-m3-eos-paper-backed-association-closure-validation-matrix-plan.md`
  already implemented the first matrix slice under
  `analyses/package_validation/explicit_association_toybox`.
- `docs/superpowers/issues/2026-06-03-m3-eos-issue-0216-add-hc-and-dispersion-context-to-the-explicit-association-toybox.md`
  is the open narrow slice for hard-chain, dispersion, total `ares`, and timing
  context.
- `C:\Users\Tanner\.codex\instructions\PYTHON_ANALYSIS_AND_PLOTTING.md`
  requires figure-owned `figures/<figure_id>/input|output|scripts` workflows,
  retained plotted data, and rendered plot artifacts.
- Root `AGENTS.md` now requires any new or updated plots to be shown in chat
  with compact real data tables when analysis work completes.

## Current Findings To Preserve

The first results are useful, but they are still diagnostic evidence.

| Finding | Current evidence | Interpretation |
| --- | ---: | --- |
| Huang/Radosz exact topology reductions | Topology reductions satisfy mass-action residuals around `1e-13` to `1e-12`. | The source formulas are a strong validation baseline when their topology assumptions are met. |
| 2B exact reduction | Max topology `ares_assoc` relative error about `5.996e-11`; mass-action residual about `2.220e-16`. | This lane can be treated as exact for the one-associating-component 2B topology gate. |
| Active Picard approximation | `damped_picard_7_05` is the only retained explicit approximation candidate. | Follow-up work should test property and derivative propagation for this candidate against exact implicit mass-action. |
| Fixed-state density residuals | Methanol median absolute density residual about `6.233e-03`; water about `2.342e-02`. | Density residuals are informative but must stay tied to the fixed-state diagnostic label. |
| Fixed-state pressure residuals | Methanol median absolute pressure residual about `1.521e+02`; water about `1.554e+03`. | Relative pressure residual alone is too harsh and too hard to interpret; absolute MPa and `Z` residuals are needed. |
| Public source coverage | Methanol and water saturation rows were fetched from public source ranges. | The data path works, but it needs source-status and range filters before claims broaden. |

## Recommended Direction

Keep the follow-up inside the existing analysis root:

```text
analyses/package_validation/explicit_association_toybox/
```

Do not create a second package-like playground. The value comes from one
toybox that can accumulate comparable rows, figures, source metadata, and
tests.

The next analysis should add eight lanes:

1. **Topology heatmaps**: show closure error by `rho * Delta`, topology, and
   closure family instead of only aggregate bars.
2. **Real-system topology mapping**: map acids, alkanols, water, amines, and
   Gross/Sadowski associating binaries to source-backed topology rows.
3. **Closure sensitivity ranking**: sweep Picard step count, damping, and
   diagonal-polish settings to see whether the current candidates are near a
   useful Pareto frontier.
4. **Derivative smoothness checks**: evaluate first-order numerical smoothness
   of `ares_assoc` with respect to density, association strength, and
   composition so approximate closures do not look accurate but differentiate
   poorly.
5. **Pressure residual reframing**: report pressure residuals in MPa and
   compressibility-factor residuals alongside relative residuals.
6. **Water parameter lane**: isolate water-specific assumptions, including the
   parameter source and any temperature-dependent effective diameter handling.
7. **Repeated timing harness**: run repeated exact implicit and closure
   evaluations so timing evidence reports medians and spread, not one-off
   elapsed values.
8. **Total residual Helmholtz context**: fold in hard-chain and dispersion
   scalar context from issue #216 so association approximation error can be
   compared against total neutral `ares`.

## Tradeoffs

| Approach | Benefit | Cost | Recommendation |
| --- | --- | --- | --- |
| Keep adding lanes in the existing toybox | One evidence root, comparable outputs, simple validation. | More files under one analysis folder. | Recommended. |
| Create separate analysis roots per lane | Smaller folders and isolated figures. | Harder to compare closures across rows and easy to duplicate loaders. | Avoid for now. |
| Move logic into package tests | Strong routine enforcement. | Turns exploratory scientific sweeps into default package burden. | Keep routine tests small and analysis-local. |
| Add provider EOS implementation now | Speeds production experimentation. | Current evidence does not justify production behavior. | Defer until analysis gates are stronger. |

## Boundaries

- No provider C++ implementation of explicit closures.
- No public `epcsaft` API changes.
- No equilibrium route, bubble, dew, flash, LLE, HELD, or objective assembly
  work.
- No regression package work.
- No broad dependency changes.
- No paper AAD values used as raw validation data.
- No plot updates without rendered in-chat plots and compact data summaries
  when the implementation is reported complete.

## Success Signals

The follow-up is useful when it can answer these questions with retained CSVs,
figures, and compact summaries:

- Which topology and `rho * Delta` ranges stress the active Picard candidate?
- Does the active Picard candidate remain accurate enough to justify its timing
  benefit?
- Does the active Picard candidate remain smooth enough for later CppAD or equilibrium
  derivative discussions?
- Are pressure residuals still alarming when reframed as MPa and `Z` errors?
- Does water need a separate parameter-source lane before comparing 3B and 4C
  assumptions?
- Does total neutral `ares` context change which errors matter physically?

## Proof Oracle Candidates For Later Planning

- `uv run python run_pytest.py analyses/package_validation/explicit_association_toybox/tests -q`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/topology_error_heatmaps/scripts/generate_data.py`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/topology_error_heatmaps/scripts/render_figure.py`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/closure_sensitivity/scripts/generate_data.py`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/closure_sensitivity/scripts/render_figure.py`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/derivative_smoothness/scripts/generate_data.py`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/derivative_smoothness/scripts/render_figure.py`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/property_residuals/scripts/generate_data.py`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/property_residuals/scripts/render_figure.py`
- `uv run python run_pytest.py tests/workflows/repo/test_project_structure.py -q`
- `uv run python scripts/dev/validate_project.py quick`

## Planning Assumptions

- The implementation plan should be one cohesive M3 analysis plan, not a
  GitHub issue yet.
- Issue #216 stays the source for hard-chain and dispersion context. The
  follow-up plan should depend on or reuse it rather than overwrite it.
- Real-system rows should start from source-backed topology labels and retained
  parameter/source metadata before attempting broad property claims.
- Derivative smoothness checks can use small centered perturbation diagnostics
  inside the analysis, but they are not a substitute for production exact
  derivative evidence.
