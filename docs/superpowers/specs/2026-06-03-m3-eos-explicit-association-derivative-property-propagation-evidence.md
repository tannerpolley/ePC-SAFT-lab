# Explicit Association Derivative And Property Propagation Evidence

## Purpose

This loose M3 EOS spec captures the next analysis step after the explicit
association toybox follow-up results from issue #218 / PR #219.

The current toybox now has a retained exact implicit association timing
baseline, topology error heatmaps, closure sensitivity rankings, derivative
smoothness diagnostics, fixed-state property residual reframing, water
parameter rows, real-system topology metadata, and total neutral `ares`
context.

The next question is sharper:

```text
Do explicit association closure errors remain acceptable after propagation into
local derivatives, pressure-like properties, chemical-potential-like
composition sensitivities, fugacity-like proxies, and an equilibrium-style
objective sensitivity diagnostic?
```

This remains analysis-only. It should strengthen or reject explicit closure
candidates before any provider EOS implementation, equilibrium admission, or
public API change is proposed.

## Project Context Evidence Used

- Verified: `docs/superpowers/PROJECT_CONTEXT.md` treats explicit association
  closure work as M3 provider EOS evidence and warns that synthetic toybox grids
  are not sufficient production proof.
- Verified: `docs/superpowers/specs/2026-05-23-m3-eos-explicit-association-closure-for-pcsaft.md`
  separates `implicit_exact` mass-action association from `explicit_approx`
  closures and states that CppAD derivatives of explicit closures are exact
  derivatives of the approximate model only.
- Verified: `docs/superpowers/specs/2026-06-03-m3-eos-paper-backed-association-closure-validation-matrix-design.md`
  defines the paper-backed topology matrix and requires the exact implicit
  baseline as the common arbiter for source formulas and closure comparisons.
- Verified: `docs/superpowers/specs/2026-06-03-m3-eos-explicit-association-follow-up-analysis-roadmap.md`
  defined the #218 follow-up lanes that have now landed: topology heatmaps,
  real-system mapping, closure sensitivity, smoothness diagnostics, property
  residual reframing, water rows, timing repeatability, and total `ares`
  context.
- Verified: `analyses/package_validation/explicit_association_toybox/**` is the
  current analysis root for explicit association closure evidence. The merged
  #218 artifacts retain exact implicit timing and closure timing in CSV form.
- Verified: `docs/superpowers/milestones/M3-eos/README.md` currently keeps
  explicit association closure design in M3 EOS and lists #214, #216, and #218
  as closed toybox evidence work.
- Inference: the next useful analysis should compare propagated derivative and
  property effects, because association `ares` error by itself does not decide
  whether an approximation is viable for EOS or later equilibrium use.

## User Decisions

- Spec shape: one cohesive M3 spec.
- Scope: analysis-only.
- Canonical artifact root:

```text
analyses/package_validation/explicit_association_toybox/
```

- Do not split into seven specs.
- Do not create an M4 equilibrium implementation spec yet.
- Do not create GitHub issues or implementation plans from this brainstorm.

## Retained Findings To Preserve

| Result area | Retained finding | Interpretation |
| --- | --- | --- |
| Timing | Explicit closures are roughly `7x-11x` faster than exact implicit mass-action in retained toybox timing lanes. | Speedup is real in the analysis harness, but the exact solve is only about `1-2 ms`, so equilibrium-scale value still needs proof. |
| Accuracy | More damped Picard steps reduce association Helmholtz error; `damped_picard_7_05` was best among tested sensitivity variants at about `1.86e-2` max relative association `ares` error. | Accuracy improves with unroll count, but not yet enough for production admission. |
| Tradeoff | `damped_picard_3_05` was fastest in sensitivity, but had the worst tested sensitivity error, about `7.47e-2`. | A speed candidate and an accuracy candidate may be different closures. |
| Diagonal polish | `picard3_diag_newton1` did not beat `damped_picard_5_05` or `damped_picard_7_05` on error. | The polish step is not obviously worth its complexity yet. |
| Collapsed mean field | The collapsed donor/acceptor closure hits `1.0` relative error in topology maps. | Keep it diagnostic-only; do not consider it a provider candidate. |
| Smoothness | Density and strength local slope jumps are about `4.23e-4`; symmetric composition perturbation is smooth. | Smoothness alone is not discriminating enough; derivative agreement against exact implicit is needed. |
| Property residuals | Fixed-state pressure residuals are very large for high-temperature water. | Water needs isolated source/parameter/topology analysis, and fixed-state residuals must not be presented as VLE validation. |

## Recommended Direction

The next analysis should move from closure-local evidence to propagated EOS
evidence:

```text
closure X_A error
  -> a_assoc error
  -> local derivative error
  -> pressure/composition/fugacity proxy error
  -> equilibrium-style objective sensitivity error
```

The goal is not to crown one closure immediately. The goal is to identify the
smallest explicit approximation that provides useful speedup without corrupting
the derivative or property signals that later EOS and equilibrium workflows
need.

## Follow-Up Analysis Lanes

### 1. Amortized Timing Benchmark

Run thousands of repeated exact implicit and explicit closure evaluations per
case so timing evidence is less dominated by Python call overhead and timer
noise.

Required retained columns:

```text
case_id
topology_id
site_count
closure_name
repeat_count
exact_implicit_elapsed_median_seconds
closure_elapsed_median_seconds
exact_implicit_elapsed_iqr_seconds
closure_elapsed_iqr_seconds
speedup_vs_exact_implicit
exact_iteration_count_median
```

Recommended comparison groups:

- one-site, 2B, 3B, 4C, and higher-site topologies;
- low, moderate, and high `rho * Delta`;
- exact topology reductions where relevant;
- `damped_picard_3_05`, `damped_picard_5_05`, `damped_picard_7_05`,
  `picard3_diag_newton1`, and any new compact variant proposed during planning.

### 2. Derivative Agreement, Not Just Smoothness

Compare explicit closure local derivatives against exact implicit association
derivatives or a high-confidence centered perturbation reference inside the
analysis harness.

Required derivative targets:

```text
d a_assoc / d rho
d a_assoc / d Delta_scale
d a_assoc / d x_i
d pressure_proxy / d rho
d chemical_potential_proxy_i / d x_j
```

The important distinction is:

```text
smooth derivative != correct derivative
```

Smoothness diagnostics should remain, but they should become supporting
evidence beside derivative agreement error.

### 3. Asymmetric Binary Mixtures

The current composition smoothness case is too symmetric. Add binary cases that
break donor/acceptor symmetry and cross-association symmetry.

Required case features:

- unequal association strengths;
- non-50/50 compositions;
- one associating plus one inert component;
- two associating components with cross association;
- component-specific site counts;
- at least one water-like 3B/4C contrast case.

The output should show whether closures that look acceptable for pure/equal
topologies fail when mixture asymmetry is introduced.

### 4. Total EOS Impact Ranking

Rank closures by propagated impact on total neutral residual Helmholtz context:

```text
ares_total = ares_hc + ares_disp + ares_assoc
```

Required retained metrics:

```text
ares_assoc_rel_error
ares_total_abs_error
ares_total_rel_error
pressure_proxy_abs_error
pressure_proxy_rel_error
mu_proxy_max_abs_error
fugacity_proxy_max_abs_error
closure_elapsed_median_seconds
speedup_vs_exact_implicit
evidence_band
```

This lane should answer whether association `ares` error materially affects
EOS-level quantities, or whether some errors are small relative to hard-chain
and dispersion context in specific regimes.

### 5. Real-System Topology Cases

Use the real-system topology map from #218 to run representative cases with
source-backed topology labels and parameter metadata, not only normalized
synthetic grids.

Required families:

- acids;
- alkanols;
- water;
- primary amines;
- secondary amines;
- Gross/Sadowski one-associating-component binaries.

Each row should preserve:

```text
source_paper
component_family
assigned_topology
rigorous_topology
parameter_source_status
validation_role
temperature
density
composition
rho_delta
```

The purpose is still evidence triage, not broad property validation.

### 6. Water-Specific Fork

Treat water as its own diagnostic fork because current fixed-state pressure
residuals are large and water has topology/parameter ambiguity.

Required comparisons:

- assigned `3B` topology versus rigorous `4C` topology label;
- provider default parameter row versus source-labeled parameter row;
- fixed effective diameter assumption versus source-recorded diameter policy;
- low-temperature and high-temperature saturation state diagnostics;
- pressure residual in MPa and `Z` residual.

This lane should decide whether water can stay in the generic closure matrix or
needs a separate future water-focused evidence issue.

### 7. Equilibrium-Style Objective Sensitivity Test

Build a tiny analysis-only objective diagnostic that consumes provider-like EOS
quantities and compares exact implicit versus explicit closure behavior.

This is not an equilibrium package implementation. It should live under the
toybox and avoid route names such as bubble, dew, flash, or LLE.

Recommended objective form:

```text
local_objective = ares_total + pressure_weight * pressure_proxy
```

Required outputs:

```text
case_id
closure_name
objective_value_exact
objective_value_closure
objective_abs_error
gradient_max_abs_error
hessian_proxy_max_abs_error
speedup_vs_exact_implicit
evidence_band
```

This lane should answer whether closure error breaks derivative quality enough
that later M4 equilibrium Jacobian/Hessian work would be at risk.

## Candidate Evidence Bands

Planning should refine thresholds, but the spec recommends starting with:

| Band | Meaning |
| --- | --- |
| `exact_reference` | Exact implicit or source topology reduction under verified assumptions. |
| `candidate_accuracy` | Closure has low propagated property and derivative error with useful speedup. |
| `speed_only_candidate` | Closure is fast but derivative/property error is too high for direct promotion. |
| `diagnostic_only` | Useful for interpreting failure modes, not a provider candidate. |
| `reject_for_provider_path` | Fails boundedness, residual, derivative, or propagated property gates. |

The collapsed donor/acceptor closure should default to `diagnostic_only` unless
new evidence proves a narrower role.

## Tradeoffs

| Approach | Benefit | Cost | Recommendation |
| --- | --- | --- | --- |
| Extend the existing toybox with propagated derivative/property lanes | Keeps evidence comparable and avoids a second playground. | More analysis files under one root. | Recommended. |
| Move directly to provider implementation | Could test production speed sooner. | Current evidence does not prove derivative or property safety. | Avoid. |
| Split equilibrium relevance into M4 now | Clean ownership for future objective assembly. | Premature while the diagnostic remains analysis-only. | Defer until this spec produces stronger evidence. |
| Focus only on timing | Fast to implement and easy to report. | Speedup without propagated error evidence is insufficient. | Avoid. |

## Non-Goals

- No provider runtime implementation of explicit association closures.
- No public `epcsaft` API changes.
- No equilibrium route implementation.
- No M4 objective assembly, Ipopt, HELD, flash, bubble, dew, or LLE work.
- No regression package work.
- No claim that centered perturbation diagnostics are production exact
  derivatives.
- No new dependency added just to support this analysis.
- No source AAD summary values treated as raw validation data.

## Success Signals

This follow-up is useful if retained CSVs and figures can answer:

- Which closures remain viable after derivative agreement checks?
- Does `damped_picard_7_05` remain the accuracy candidate after propagated
  property errors are included?
- Is `damped_picard_3_05` merely fast, or does it preserve enough EOS signal in
  low-to-moderate association regimes?
- Does diagonal polish ever outperform simply adding more damped Picard steps?
- Which topologies and `rho * Delta` ranges make explicit closures fail?
- Does water need a separate closure/parameter evidence path?
- Do local objective gradients and Hessian proxies retain enough quality for
  later equilibrium discussions?

## Proof Oracle Candidates For Later Planning

- `uv run python run_pytest.py analyses/package_validation/explicit_association_toybox/tests -q`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/amortized_timing/scripts/generate_data.py`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/amortized_timing/scripts/render_figure.py`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/derivative_agreement/scripts/generate_data.py`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/derivative_agreement/scripts/render_figure.py`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/asymmetric_binary_closures/scripts/generate_data.py`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/asymmetric_binary_closures/scripts/render_figure.py`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/total_eos_impact/scripts/generate_data.py`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/total_eos_impact/scripts/render_figure.py`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/water_topology_fork/scripts/generate_data.py`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/water_topology_fork/scripts/render_figure.py`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/equilibrium_style_objective_sensitivity/scripts/generate_data.py`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/equilibrium_style_objective_sensitivity/scripts/render_figure.py`
- `uv run python run_pytest.py tests/workflows/repo/test_project_structure.py -q`
- `uv run python scripts/dev/validate_project.py quick`

When implementation reports new or updated plots, the final chat and handoff
must render the plots inline and include compact Markdown tables from retained
data, following root `AGENTS.md`.

## Planning Decisions Still Needed

These should be resolved by `$project-plan`, not by this loose brainstorm spec:

- whether the implementation should be one issue or two smaller analysis
  issues;
- exact thresholds for derivative/property evidence bands;
- whether objective-sensitivity proxies should be scalar-only or include a
  small local Hessian-proxy matrix;
- whether water-specific rows belong in the same implementation slice or a
  follow-up after derivative/property propagation.
