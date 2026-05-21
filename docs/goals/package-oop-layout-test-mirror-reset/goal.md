# Package OOP Layout And Test Mirror Reset

## Objective

Implement the direct-constructor public API and package/test layout reset. The package should expose clean public objects: `Mixture`, `State`, `Equilibrium`, `Regression`, `ParameterSet`, and `ModelOptions`.

## Outcome

- `Mixture` owns components, parameters, and model options only.
- `State` is initialized from a `Mixture` plus thermodynamic conditions.
- `Equilibrium` and `Regression` are constructed directly from a `Mixture`.
- Public `State` exposes residual property methods and residual Helmholtz contribution access.
- Source modules are organized by package concepts instead of a broad flat root.
- Tests mirror the package structure and share hydrocarbon/regression/equilibrium cases through `tests/support`.

## Completion Proof

The reset is complete when focused tests prove:

- Direct public constructors work and `Mixture` no longer exposes workflow factories.
- Hydrocarbon `State` computes `Z`, residual Helmholtz/Gibbs/enthalpy/entropy values, fugacity quantities, and residual Helmholtz contributions.
- The trusted hydrocarbon bubble-pressure route and hydrocarbon regression anchor still work through direct workflow objects.
- Package and test skeletons are present, with future equilibrium route modules private until implemented.
- Focused pytest targets, quick validation, GoalBuddy checker, and repo cleanup pass.

## Hard Constraints

- Do not add compatibility aliases or deprecated wrappers in the final public API.
- Do not expose backend-selection flags to users.
- Do not add paper-validation tests to default pytest.
- Do not hard-code parameter tables in individual tests when a shared support case is appropriate.
- Keep user-facing docstrings scientific and user-oriented.
