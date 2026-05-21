Equilibrium Architecture
========================

The reset public API is workflow-object based:

* ``Equilibrium(mixture, ...).bubble_pressure(...)`` for the trusted neutral
  bubble-pressure proof.
* Additional equilibrium families remain private route modules until they have
  focused public tests and capability evidence.

Old public mixture route methods such as ``mixture.bubble_p(...)`` and
``mixture.equilibrium(kind=...)`` are no longer part of the reset public
frontend. Internal native adapters may still use typed problem objects and
route builders while those routes are ported behind the direct workflow object.

For internal route builders that need a serializable problem object, use the
private equilibrium problem objects with one of:

* ``TPFlash``
* ``StabilityAnalysis``
* ``BubblePoint``
* ``DewPoint``
* ``LLEProblem``
* ``ElectrolyteLLEProblem``
* ``ElectrolyteBubblePoint``
* ``ReactiveSpeciationProblem``
* ``ReactivePhaseEquilibriumProblem``
* ``ReactiveElectrolyteBubbleProblem``

Example
-------

.. code-block:: python

   import epcsaft

   workflow = epcsaft.Equilibrium(mixture, max_iterations=200)
   result = workflow.bubble_pressure(T=233.15, x=[0.1, 0.3, 0.6])

Request Normalization
---------------------

Public request normalization lives at ``Equilibrium(mixture, ...)``. The
workflow object owns user-facing defaults and delegates to private route
adapters that stamp diagnostics and results consistently.

Reactive convenience routes remain explicit. ``chemical_equilibrium``,
``reactive_staged_equilibrium``, ``reactive_lle``,
``reactive_electrolyte_lle``, ``reactive_stability``, and
``reactive_electrolyte_bubble_pressure`` are selected before non-reactive
normalization so their specialized option checks and native route boundaries do
not become implicit fallback behavior.

Solver Selection
----------------

The reset public frontend does not expose a solver-backend selector. Public
equilibrium workflows choose the required native route directly and raise at the
route boundary when the compiled dependency or CppAD coverage is missing. The
trusted public proof is the hydrocarbon bubble-pressure route through native
Ipopt with an exact Hessian. Other native route builders remain implementation
evidence until they are ported behind reset ``Equilibrium(mixture, ...)``
methods and focused API tests.

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
