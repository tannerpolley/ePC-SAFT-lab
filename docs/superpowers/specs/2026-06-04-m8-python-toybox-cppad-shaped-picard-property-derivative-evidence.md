# CppAD-Shaped Picard Property And Derivative Evidence

Milestone: `M8 - Python Toybox`
Issue: `none`
Status: `draft`
Last synced: `2026-06-04`

## Summary

Create a Python-only toybox spec for C++/CppAD-shaped evidence around the
retained Picard association approximation. The work should answer two separate
questions before any provider or equilibrium admission claim is made:

1. Does the Picard reduced form behave well for density, pressure, fugacity-like
   property proxies, and association Helmholtz energy across meaningful pure and
   mixture association schemes?
2. Does the same explicit Picard graph behave well when autodiff is applied for
   Jacobians and Hessians needed by later saturation and equilibrium work?

This is not provider implementation. It is a toybox evidence lane that compares
the same retained Picard equation through NumPy/no-JAX and JAX implementations,
while using exact implicit association as the scientific baseline wherever
possible.

## Project Context Evidence Used

- `docs/superpowers/milestones/M8-python-toybox/README.md` defines Python
  toybox work as the right lane for cross-EOS/equilibrium analysis that is not
  production package work.
- `docs/superpowers/specs/2026-06-04-m8-python-toybox-picard-autodiff-and-exact-implicit-sensitivity-baseline-hardening.md`
  already frames exact implicit sensitivities and JAX Picard derivatives as the
  derivative baseline.
- `docs/superpowers/specs/2026-06-04-m8-python-toybox-equilibrium-relevance-probe-for-picard-closure-error.md`
  asks whether Picard derivative error is dangerous for future objective,
  Jacobian, and Hessian work.
- `docs/latex/explicit_assocation.tex` explains why exact association is
  implicit in site fractions and why a closed Picard reduction is attractive
  for ordinary chain-rule autodiff.
- The current PR #229 evidence shows the pure saturation JAX lane can reproduce
  the SciPy Picard saturation rows with tiny residual norms, while the local
  equilibrium-style Hessian proxy still has nontrivial curvature error that
  needs broader evidence.

## User Decisions

- Stay on the current toybox branch and add the missing spec and plan.
- Keep this in `M8 - Python Toybox`.
- Compare the retained Picard equation through no-JAX and JAX paths.
- Test pure-component and mixture association schemes.
- Evaluate both ordinary property behavior and autodiff derivative behavior.
- Acknowledge that JAX is only a Python proxy for differentiability. CppAD may
  behave differently in tape size, sparsity, memory use, branching, and runtime.
- Do not reintroduce retired explicit closure families. Any iteration or damping
  variation is a stress lane for the same Picard fixed-point form, not a new
  provider candidate.

## Evidence Lanes

### Lane 1: Property And Association Coverage

Build a retained case matrix that evaluates exact implicit association, Picard
NumPy, and Picard JAX for:

- pure nonassociating control;
- pure one-site association when supported by the toybox equations;
- pure 2B self association;
- pure 3B and 4C-like topologies when the site graph can be represented without
  pretending the topology is source-validated;
- inert plus associating binary mixtures;
- two self-associating component mixtures;
- cross-associating binary mixtures;
- asymmetric donor/acceptor mixtures;
- unequal association strength matrices;
- non-50/50 compositions;
- water-like topology forks where 3B and 4C assumptions are explicitly labeled.

Required retained quantities:

```text
case_id
topology_id
component_family
mixture_family
temperature
density
pressure
composition
association_strength_matrix
picard_backend
picard_iteration_count
picard_damping
association_helmholtz_exact
association_helmholtz_picard
total_residual_helmholtz_exact
total_residual_helmholtz_picard
pressure_exact
pressure_picard
fugacity_proxy_exact
fugacity_proxy_picard
density_root_status
mass_action_residual_norm
absolute_error
relative_error
```

The density and pressure checks should use meaningful curves and data-like
grids, not bar charts. Point data and dotted model curves should follow the
current Matplotlib artifact rules.

### Lane 2: C++/CppAD-Shaped Autodiff Evidence

Build a derivative harness that treats the Picard reduced form like a future
CppAD-taped EOS kernel, while remaining honest that JAX is not CppAD. The
Python lane should compare:

- NumPy Picard scalar values;
- JAX Picard scalar values;
- JAX residual Jacobians;
- JAX gradients of selected property/objective proxies;
- JAX Hessians or Hessian-vector products for small retained cases;
- exact implicit first sensitivities where available;
- exact implicit finite-difference or analytic second-derivative baselines when
  feasible.

Derivative targets should include:

- `a_assoc`;
- total residual Helmholtz proxy;
- pressure proxy;
- density root residuals;
- saturation residuals over vapor density, liquid density, and pressure;
- fugacity or chemical-potential-like composition proxies;
- association strength parameters, including toybox equivalents of
  `epsilon_hb`, `kappa_hb`, `k_hb`, and `l_ij` where those are present in input
  metadata.

Retained derivative rows should include:

```text
case_id
topology_id
target
variable_block
derivative_order
backend
exact_implicit_value
picard_numpy_value
picard_jax_value
absolute_error
relative_error
finite_difference_step
autodiff_status
cppad_relevance_note
admission_band
```

## CppAD Relevance Rules

The toybox should use C++/CppAD-shaped evidence, not claim CppAD proof:

- use fixed-size variable blocks that resemble future C++ derivative bundles;
- retain sparsity pattern summaries when possible;
- record branch or clipping events that would affect taped code;
- keep temperature, density, composition, and parameter derivatives separated;
- distinguish value agreement from derivative agreement;
- state clearly when a JAX result is only a differentiability proxy and needs
  future provider CppAD confirmation.

## Non-Goals

- No provider C++ implementation.
- No CppAD implementation in M8.
- No M4 equilibrium route behavior.
- No M6 benchmark admission.
- No public API changes.
- No Python Ipopt dependency requirement.
- No resurrection of rejected closure families.

## Open Questions

- Which association topology labels should be canonical for toybox cases that
  are mathematically useful but not source-backed for a specific compound?
- Which derivative blocks should be full Hessians versus Hessian-vector products
  to keep the analysis lightweight?
- What tolerance band should separate `candidate_accuracy`,
  `needs_more_evidence`, and `fails_derivative_gate`?
- Should iteration-count and damping stress lanes be retained in output rows or
  used only during local diagnostic exploration?

## Proof Oracle Candidates For Later Planning

- `uv run python run_pytest.py analyses/package_validation/explicit_association_toybox/tests/test_cppad_shaped_picard_property_evidence.py analyses/package_validation/explicit_association_toybox/tests/test_cppad_shaped_picard_derivative_evidence.py -q`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/cppad_shaped_picard_property_evidence/scripts/generate_data.py`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/cppad_shaped_picard_property_evidence/scripts/render_figure.py`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/cppad_shaped_picard_derivative_evidence/scripts/generate_data.py`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/cppad_shaped_picard_derivative_evidence/scripts/render_figure.py`
- `uv run python scripts/dev/validate_project.py quick`
