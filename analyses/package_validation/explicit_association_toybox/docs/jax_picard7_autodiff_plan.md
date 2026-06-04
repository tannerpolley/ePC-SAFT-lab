# JAX Picard7 Autodiff Derivative Comparison Plan

## Purpose

Use this toybox to compare automatic derivatives of the explicit
`damped_picard_7_05` association closure against the implicit sensitivities
required by the exact PC-SAFT association mass-action solve.

This is analysis-only work. It must not add provider runtime behavior, public
API claims, equilibrium route behavior, or package dependency requirements until
the retained evidence justifies a follow-up implementation issue.

## Scope

- Keep `damped_picard_7_05` as the only explicit approximation candidate.
- Keep exact implicit mass-action as the derivative baseline.
- Keep Huang/Radosz topology reductions only as exact special-topology
  references, not explicit approximation candidates.
- Compare derivatives for pure self-association, associating plus inert
  mixtures, cross-associating binaries, unequal association strengths, and
  water-like topology cases.

## JAX Implementation Sketch

1. Add a toybox-local JAX script only after confirming the analysis environment
   has `jax` available or after an explicit dependency decision.
2. Enable double precision with `jax_enable_x64=True`.
3. Implement a pure JAX function for fixed-step Picard7:
   - inputs: density, composition, association-strength matrix, site ownership,
     and active-pair topology
   - loop: exactly seven damped Picard updates with damping `0.5`
   - output: bounded site fractions and association Helmholtz contribution
4. Use JAX transforms on the explicit closure:
   - `jacfwd` or `jacrev` for first derivatives
   - `hessian` or nested Jacobians for second derivatives
   - optional third-order tensors only if an equilibrium plan needs them
5. Implement the exact implicit baseline with the implicit function theorem:
   - mass-action residual: `F(X, y) = 0`
   - first sensitivity: `dX/dy = -F_X^{-1} F_y`
   - second sensitivity: differentiate the first sensitivity expression or
     start with high-accuracy central differences before adding tensor code

## Retained Outputs

Add one figure/data lane when implemented:

- `figures/jax_picard7_derivatives/output/jax_picard7_derivatives.csv`
- `figures/jax_picard7_derivatives/output/jax_picard7_derivatives_plotted_data.csv`
- `figures/jax_picard7_derivatives/output/jax_picard7_derivatives.png`
- `figures/jax_picard7_derivatives/output/jax_picard7_derivatives.mpl.yaml`

Required columns:

- `case_id`
- `topology_id`
- `derivative_target`
- `derivative_order`
- `exact_implicit_value`
- `picard7_jax_value`
- `abs_error`
- `rel_error`
- `implicit_jacobian_condition_number`
- `mass_action_residual_inf`
- `exact_implicit_elapsed_seconds`
- `picard7_jax_elapsed_seconds`
- `speedup_vs_exact_implicit`

## Acceptance Signals

- JAX explicit derivatives are compared against exact implicit sensitivities,
  not against finite differences of the same Picard7 approximation.
- The exact implicit timing baseline is retained in every timing row.
- Results report Jacobian and Hessian agreement separately.
- Cases cover single self-associated molecules, binary mixtures, cross
  association, unequal `Delta_ij`, and water-like topology assumptions.
- The final chat/handoff renders any new plots inline and includes a real data
  summary table.
