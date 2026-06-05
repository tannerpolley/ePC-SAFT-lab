# Picard Stress Evidence To Rescue Or Retire

## Summary

Use the Python-only M8 toybox to run the harsh evidence that would be needed to
either rescue the retained Picard explicit association approximation or retire it
cleanly after the issue 223 admission packet.

The current issue 223 result is conservative: the retained final report recommends
`close_without_provider_implementation` for issue 161. That should remain the
default interpretation unless this follow-up evidence shows that Picard can hold
derivative, Hessian, pressure-density, and equilibrium-style objective quality
under harder cases.

This is not a provider implementation spec. It is a research and validation spec
for deciding whether further Picard work is still worth planning.

## Project Context Evidence

- `docs/superpowers/PROJECT_CONTEXT.md` assigns exploratory EOS/property and
  equilibrium-style analysis that is not provider-ready to M8.
- `docs/superpowers/milestones/M8-python-toybox/README.md` says M8 is the
  Python-only toybox milestone for EOS, derivative, property, and
  equilibrium-style analysis.
- Issue 223 and PR 233 generated the final Picard admission packet for issue 161:
  `analyses/package_validation/explicit_association_toybox/figures/final_picard_admission_report/output/final_picard_admission_report.csv`.
- The issue 223 retained data showed useful but insufficient evidence:
  association Helmholtz error reached about `1.60e-2`, pressure proxy error
  reached about `2.95e-2`, first-derivative error reached about `3.60e-2`,
  Hessian error reached about `8.22e-2`, and end-to-end speedup ranged from
  about `0.61x` to `2.56x`.
- Existing M8 specs already cover several sublanes: Picard autodiff, pure
  saturation solving, pressure-density validation, equilibrium relevance, and
  CppAD-shaped derivative/property evidence. This spec should consolidate the
  post-223 burden of proof rather than duplicate those plans.

## User Decisions

- Create a new M8 loose spec rather than revise an existing M8 spec.
- Optimize the next testing lane for evidence that can rescue Picard or rule it
  out, not for immediate provider implementation.
- Keep Picard as the only explicit association approximation under test. Do not
  reintroduce retired alternate approximation families.

## Hypothesis

The retained Picard approximation may still be useful if its errors stay bounded
when association strength, topology, density, temperature, composition, and
mixture asymmetry are pushed harder than the current methanol/water saturation
packet.

The rescue condition is not that Picard gives pretty saturation plots. The rescue
condition is that it preserves the derivative information needed by EOS and later
equilibrium objectives while providing a meaningful runtime advantage over exact
implicit association.

## Recommended Evidence Lanes

### 1. Association-Strength Stress Grid

Run the same fixed Picard policy grid against controlled sweeps in:

- association energy and volume through the toybox equivalents of `epsilon_hb`
  and `k_hb`;
- binary association modifiers such as `l_ij` and `k_ij` where the toybox model
  supports them;
- density from dilute vapor-like states to dense liquid-like states;
- temperature across weak, moderate, and strong association regimes.

Report exact implicit iteration count, site-fraction error, mass-action residual,
`a^assoc` error, total residual Helmholtz proxy error, pressure proxy error,
first-derivative error, Hessian error, closure-only timing, and end-to-end
simulation timing.

### 2. Asymmetric Mixture And Cross-Association Cases

Move beyond pure methanol/water and symmetric toy grids.

The stress set should include:

- one self-associating compound diluted in a nonassociating solvent;
- two self-associating compounds with unequal site topology;
- cross-association with unequal association strengths;
- composition sweeps away from `x = 0.5`;
- water-like `4C` behavior separately from alcohol-like `2B` behavior.

The question is whether Picard stays usable when the association matrix is
unbalanced, not only when topology is clean and symmetric.

### 3. JAX Versus Exact Implicit Sensitivity Comparison

Use JAX in the toybox to differentiate the explicit Picard expression and compare
against exact implicit sensitivity baselines.

Retain rows for:

- gradients with respect to density, composition, temperature, and association
  strength;
- Hessians over the variables that later feed equilibrium objectives;
- failure or conditioning diagnostics when the implicit baseline is ill
  conditioned;
- graph-depth or evaluation-cost proxies that make fixed Picard depth visible.

This lane should make clear that Picard derivatives are derivatives of the
approximate explicit EOS, not exact PC-SAFT association derivatives.

### 4. Equilibrium-Style Objective Probe

Do not implement equilibrium package behavior. Instead, add a tiny M8 objective
probe that consumes provider-like EOS values and derivatives.

The probe should compare exact implicit association versus Picard for:

- objective value residuals;
- objective gradient differences;
- Hessian differences and conditioning;
- Newton-step direction or trust-region-style step quality;
- whether Picard changes the sign, rank, or conditioning of the local problem.

The purpose is to test whether derivative error is dangerous for Ipopt-like
workflows before any M4 issue is opened.

### 5. Honest Plotting And Retained Tables

Plots should use readable scientific-figure conventions:

- data markers for retained reference data;
- dotted model curves for exact implicit and Picard;
- density, pressure, residual, derivative, and hessian plots with physical axes;
- no bar plots unless a later plan explicitly justifies them;
- every rendered figure accompanied by retained plotted-data CSV and a compact
  Markdown table summarizing the underlying values.

## Decision Outcomes

The follow-up evidence should force one of three outcomes:

1. **Retire Picard**: errors or Hessian/objective behavior are too risky, or
   end-to-end speedup is not meaningful.
2. **Keep M8-only**: Picard is scientifically interesting but needs more toybox
   work and must not become provider scope.
3. **Open narrow M3 admission issue**: only if harsh-grid property and derivative
   evidence pass explicit thresholds and the runtime win remains meaningful.

The default after issue 223 is outcome 1 or 2. Outcome 3 has the burden of proof.

## Proposed Admission Gates For Later Planning

These are candidate gates, not final thresholds:

- no failed exact implicit baseline rows in the retained stress set;
- no Picard density-root failures in cases where exact implicit succeeds;
- bounded `a^assoc`, total residual proxy, and pressure proxy relative errors
  across strong-association cases;
- bounded first-derivative and Hessian relative errors across the JAX versus
  implicit-sensitivity comparison;
- no equilibrium-style objective conditioning regressions that would plausibly
  damage Ipopt;
- median end-to-end speedup above exact implicit for each retained case family;
- no case family where Picard is routinely slower than exact implicit.

## Non-Goals

- No provider EOS implementation.
- No M4 equilibrium package implementation.
- No M5 regression or M6 benchmark promotion.
- No new approximation families.
- No compatibility surfaces or old-route redirects.
- No conclusion based only on scalar `a^assoc` plots.

## Open Questions

- What hard numeric thresholds should define rescue versus retirement?
- Which real associating compounds should be the minimum stress set after
  methanol and water?
- Should cross-association parameters be synthetic first, paper-backed first, or
  both?
- Should the equilibrium-style probe optimize a tiny objective, or only evaluate
  objective derivative quality at fixed states?

## Recommended Next Route

Turn this spec into one M8 plan only if issue 223 is merged and the project still
wants to continue Picard research. The plan should be explicit that it may end in
retiring Picard rather than implementing it.
