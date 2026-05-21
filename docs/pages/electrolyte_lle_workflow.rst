Electrolyte LLE Workflow
========================

Electrolyte LLE remains native-route work during the CppAD-only API reset. The
reset public frontend currently proves the neutral hydrocarbon bubble route;
electrolyte LLE should be treated as an internal native capability until a
public ``Mixture.equilibrium(...)`` method is added with CppAD coverage and
focused API tests.

Current Boundary
----------------

- Native route builders and pybind contracts live under ``tests/native``.
- Public API tests do not reproduce electrolyte paper lines.
- Downstream projects should keep case-study data, feeds, and acceptance
  thresholds outside upstream pytest.
- Missing public frontend coverage is a blocker for broad capability claims.
