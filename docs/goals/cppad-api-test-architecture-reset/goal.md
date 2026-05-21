# CppAD-Only API And Test Architecture Reset

## Objective

Implement the hard public API and test architecture reset around a CppAD-only production evaluation path. The package should expose clean frontend objects only: `Mixture`, `State`, `Equilibrium`, `Regression`, `ParameterSet`, and `ModelOptions`.

## Outcome

- `ParameterSet` stores ePC-SAFT parameters only.
- `ModelOptions` belongs to `Mixture` and owns model-formulation choices.
- `Mixture.state(...)`, `Mixture.equilibrium(...)`, and `Mixture.regression(...)` create configured workflow objects.
- Public `State`, `Equilibrium`, and `Regression` paths use CppAD-backed evaluation. No public backend-mode options remain.
- The final public API has no `ePCSAFTMixture`, `ePCSAFTState`, free `fit_*`, free `bubble_p`, free `dew_p`, typed problem root exports, or legacy lazy export layer.
- Test roots separate public Interface checks, native Implementation contracts, workflow guards, and support fixtures.

## Completion Proof

The reset is complete when focused tests prove:

- CppAD-only `State` computes hydrocarbon property values and required derivatives.
- `Regression` passes the existing hydrocarbon Gross/Sadowski anchor through the new object API.
- `Equilibrium` passes the trusted hydrocarbon VLE bubble/IPOPT exact-Hessian route through the new object API.
- Old public API exports and mixed Interface/Implementation pytest roots are removed.
- `uv run python scripts/dev/validate_project.py quick` and the repo cleanup hook pass.

## Hard Constraints

- Do not add compatibility aliases or deprecated wrappers in the final state.
- Do not expose analytic/auto/cppad backend selection to users.
- Do not silently fall back from exact derivatives, Jacobians, or Hessians.
- Keep electrolyte/reactive/SSM+DS production validation out of this goal unless needed to keep the CppAD-only infrastructure honest.
- Do not run broad full pytest during the reset; use focused targets until the final quick validation.
- If this charter and `state.yaml` disagree, `state.yaml` is the board truth.

## Starter Command

```text
/goal Follow docs/goals/cppad-api-test-architecture-reset/goal.md.
```
