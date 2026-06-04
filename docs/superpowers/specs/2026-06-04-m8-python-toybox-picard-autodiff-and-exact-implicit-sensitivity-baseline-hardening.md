# Picard Autodiff And Exact Implicit Sensitivity Baseline Hardening

Milestone: `M8 - Python Toybox`
Issue: `none`
Status: `draft`
Last synced: `2026-06-04`

## Summary

Create a Python-only toybox spec for comparing the active Picard association
closure against exact implicit association sensitivities. The work should make
the derivative story explicit: JAX can give clean first and second derivatives
of the reduced Picard model, but those derivatives must be compared against
implicit exact mass-action sensitivities before any provider or equilibrium
admission claim is made.

This spec is analysis-only. It does not add provider C++ behavior, public
package APIs, equilibrium routes, or production capability claims.

## Project Context Evidence Used

- `docs/superpowers/PROJECT_CONTEXT.md` treats explicit association closure
  work as pre-admission evidence and separates it from generalized equilibrium
  implementation.
- `docs/superpowers/milestones/M8-python-toybox/README.md` defines the new
  Python toybox milestone as the right lane for cross-EOS/equilibrium analysis
  that is not production package work.
- `docs/latex/explicit_assocation.tex` explains the exact implicit association
  solve, the implicit derivative burden, and the explicit seven-step Picard
  reduced model.
- `docs/superpowers/specs/2026-06-03-m3-eos-explicit-association-derivative-property-propagation-evidence.md`
  already identifies derivative agreement as the missing evidence after
  smoothness-only diagnostics.
- `C:\Users\Tanner\.codex\PROJECT_ARCHITECTURE.md` and
  `C:\Users\Tanner\.codex\instructions\PYTHON_ANALYSIS_AND_PLOTTING.md`
  require analysis work to stay self-contained, reproducible, and separated
  from package code.

## User Decisions

- Use the new `M8 - Python Toybox` milestone.
- Keep this Python-only and analysis-only.
- Focus on the retained Picard closure, not old closure families.
- Include exact implicit baseline timing and sensitivities, not just explicit
  closure timings.
- Plan JAX as an analysis dependency candidate for autodiff comparison, not as
  a provider runtime dependency.

## Recommended Approach

Extend the existing analysis root:

```text
analyses/package_validation/explicit_association_toybox/
```

Add derivative-focused figure/data lanes that compare:

- exact implicit first derivatives from implicit sensitivity formulas or a
  verified finite-difference baseline;
- exact implicit second derivatives or tensor slices where feasible;
- JAX `jacfwd`, `jacrev`, `hessian`, and mixed-mode derivatives of the Picard
  reduced model;
- sensitivity to density, temperature, composition, association strength, and
  source-labeled hydrogen-bond parameters such as `k_hb` and `l_ij` when those
  names are present in the toybox input metadata.

The goal is not to prove JAX is production-ready. The goal is to build an
honest derivative error budget between:

```text
exact implicit association model
explicit Picard reduced association model
JAX derivatives of the reduced model
implicit or finite-difference baseline derivatives of the exact model
```

## Required Analysis Outputs

Retain CSV or Parquet rows with:

```text
case_id
topology_id
component_family
state_temperature
state_density
composition
parameter_name
derivative_target
derivative_order
exact_implicit_value
picard_jax_value
absolute_error
relative_error
finite_difference_step
implicit_baseline_status
jax_backend_status
```

Required target families:

- `a_assoc`;
- site fractions `X_A`;
- density derivatives;
- association-strength scale derivatives;
- composition derivatives for asymmetric mixtures;
- parameter derivatives for `epsilon_hb`, `kappa_hb`, `k_hb`, `l_ij`, or their
  source-backed toybox equivalents.

## Non-Goals

- No provider C++ implementation.
- No public `epcsaft` derivative API changes.
- No equilibrium package implementation.
- No benchmark admission.
- No old closure-family resurrection.
- No claim that Picard derivatives are exact PC-SAFT association derivatives.

## Open Questions

- Which exact implicit second-derivative path is cheapest enough for toybox
  use: analytic implicit formulas, nested finite differences, or a small
  implicit-function autodiff prototype?
- Should JAX be an optional analysis-only dependency, or should the first pass
  use a local environment file to avoid changing repo dependency policy?
- Which parameter names should be canonical in retained outputs when source
  papers use different association-strength notation?

## Proof Oracle Candidates For Later Planning

- `uv run python run_pytest.py analyses/package_validation/explicit_association_toybox/tests -q`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/derivative_agreement/scripts/generate_data.py`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/derivative_agreement/scripts/render_figure.py`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/autodiff_hessian_error/scripts/generate_data.py`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/autodiff_hessian_error/scripts/render_figure.py`
