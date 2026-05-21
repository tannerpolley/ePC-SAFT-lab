Reactive Electrolyte Workflow
=============================

Reactive electrolyte equilibrium is not part of the reset public proof. Native
route builders, residual surfaces, and benchmark scripts may remain as internal
implementation evidence, but the public API should not claim production support
until it is ported behind ``Equilibrium(mixture, ...)`` with CppAD-backed
focused tests.

For the current reset, use the hydrocarbon ``bubble_pressure`` route as the
trusted equilibrium workflow. Treat reactive electrolyte LLE, electrolyte LLE,
and broader paper reproduction as later goals.
