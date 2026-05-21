Equilibrium Architecture
========================

The reset public API is workflow-object based:

* ``Equilibrium(mixture, ...).solve(route=..., ...)`` for all certified neutral
  VLE route specs.
* Additional equilibrium families are declared in the native activation matrix
  as not exposed until they have production selector support, focused public
  tests, and capability evidence.

Old public mixture route methods such as ``mixture.bubble_p(...)`` and
``mixture.equilibrium(kind=...)`` are no longer part of the reset public
frontend. Deleted route families are not retained as compatibility stubs,
hidden route modules, or typed problem-object shells.

Example
-------

.. code-block:: python

   import epcsaft

   workflow = epcsaft.Equilibrium(mixture, max_iterations=200)
   result = workflow.solve(route="bubble_pressure", T=233.15, x=[0.1, 0.3, 0.6])
   flash = workflow.solve(route="flash", T=233.15, P=result.pressure, z=[0.4, 0.25, 0.35])

Request Normalization
---------------------

Public request normalization lives at ``Equilibrium(mixture, ...)``. The
workflow object owns user-facing defaults and delegates only to the selector
core for production neutral VLE routes. Selector-ineligible inputs fail before
solver dispatch; solver or certification failures after dispatch raise with
diagnostics. Flash is a selector-owned route spec over the same native VLE
residual/constraint core as bubble and dew routes, not a direct pybind route or
Python-owned optimizer loop. Route-specific public methods are intentionally
absent; ``solve`` is the only public execution lane.

Solver Selection
----------------

The reset public frontend does not expose a solver-backend selector. Public
equilibrium workflows choose the required native route directly and raise at the
route boundary when the compiled dependency or CppAD coverage is missing. The
trusted public proof set is the hydrocarbon neutral VLE route family through
the native selector core, Ipopt, and exact Hessian callbacks. LLE, electrolyte,
reactive, and speciation route families are declared-not-exposed activation rows
until they are ported behind the selector and reset
``Equilibrium(mixture, ...)`` methods.

The convex Gibbs formulation is limited to homogeneous ideal reaction or
speciation subkernels and validation tests. Full ePC-SAFT multiphase,
electrolyte, density-coupled, or association-coupled equilibrium should be
treated as a thermodynamic constrained NLP, not as a globally convex problem.
Production equilibrium routes require exact analytic or CppAD Jacobians. Native
Ceres owns package regression solves, while CppAD and implicit sensitivities
provide derivative payloads where the route is validated.

Repeated State Work
-------------------

For many property calls, keep the loop downstream-owned. Feed each successful
state density into the next pressure-closed state as ``rho_guess``. Use direct ``rho=...`` only when density is the closure variable,
not when exact pressure closure is required.
