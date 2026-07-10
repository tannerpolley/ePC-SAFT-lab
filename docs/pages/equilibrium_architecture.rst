Equilibrium Architecture
========================

This page describes the equilibrium surface now owned by the
``epcsaft-equilibrium`` extension package.

The current reset public API is workflow-object based:

* ``Equilibrium(mixture, route=..., ...).solve()`` for certified
  ``bubble_pressure``, ``dew_pressure``, and scoped nonassociating hydrocarbon
  ``single_component_vle`` route specs.
* Neutral LLE, multiphase, electrolyte, reactive, and CPE families are declared
  in the native activation matrix as not exposed until they have production
  selector support, focused public tests, and capability evidence.

Old public mixture route methods such as ``mixture.bubble_p(...)`` and
``mixture.equilibrium(kind=...)`` are no longer part of the reset public
frontend. Deleted route families are not retained as compatibility stubs,
hidden route modules, or typed problem-object shells.

Example
-------

.. code-block:: python

   import epcsaft
   from epcsaft_equilibrium import Equilibrium

   bubble = Equilibrium(
       mixture,
       route="bubble_pressure",
       T=233.15,
       x=[0.1, 0.3, 0.6],
   )
   result = bubble.solve(solver_options={"max_iterations": 200})

   saturation = Equilibrium(
       pure_nonassociating_mixture,
       route="single_component_vle",
       T=233.15,
   ).solve()

Request Normalization
---------------------

Public request normalization lives at ``Equilibrium(mixture, route=..., ...)``.
The workflow object owns route/spec validation and delegates only to the
selector core for production neutral two-phase routes. Solver controls are passed to
``solve(solver_options=...)``. Selector-ineligible inputs fail before solver
dispatch; solver or certification failures after dispatch raise with
diagnostics. Neutral LLE, neutral TP flash, and temperature-boundary VLE remain internal
component diagnostics and are rejected by the public constructor before native
selector dispatch. The retained neutral-LLE activation row builds a
``liquid1``/``liquid2`` internal plan and reuses the generic two-phase EOS NLP
core with a phase-distance anti-collapse constraint. Candidate distinctness,
route convergence, and postsolve checks do not turn a finite sampled-candidate
Stage II audit into the global HELD proof required for production admission.
Route-specific public methods are intentionally absent;
``solve`` is the only public execution lane.

Solver Selection
----------------

The reset public frontend does not expose a solver-backend selector. Public
equilibrium workflows choose the required native route directly and raise at the
route boundary when the compiled dependency or CppAD coverage is missing. The
trusted public proof set is limited to neutral bubble/dew pressure and scoped
nonassociating hydrocarbon single-component VLE through the native selector
core, Ipopt, and exact derivative callbacks. Neutral LLE, neutral TP flash,
temperature-boundary VLE, multiphase, electrolyte LLE, reactive
speciation, reactive phase, CPE, and coupled speciation route families remain
declared-not-exposed activation rows until they are ported behind the selector
and reset ``Equilibrium(mixture, route=..., ...)`` workflow.

The convex Gibbs formulation is limited to homogeneous ideal reaction or
speciation subkernels and validation tests. Full ePC-SAFT multiphase,
electrolyte, density-coupled, or association-coupled equilibrium should be
treated as a thermodynamic constrained NLP, not as a globally convex problem.
Production equilibrium routes require exact analytic or CppAD Jacobians. Native
Ceres owns the current ``epcsaft-regression`` solves. Ipopt owns the current
``epcsaft-equilibrium`` production solves. CppAD and implicit
sensitivities remain provider-owned where the EoS route is validated.

Ipopt diagnostics are route-owned and available through
``result.diagnostics``. Use ``ipopt_iteration_history_limit`` to retain recent
iteration records and ``ipopt_print_level`` only for local debugging output;
normal tests should assert the diagnostic payload instead of enabling noisy
solver logs.

Associating Equilibrium Boundary
--------------------------------

Associating admission is narrow and proof-fixture-specific under the ADR 0004
boundary. Gross/Sadowski 2002 Figures 2--9 admit the corresponding associating
``bubble_pressure`` and ``dew_pressure`` fixtures. Figures 8 and 10 retain
internal neutral-LLE evidence but authorize no public LLE route. Other
associating inputs remain selector-ineligible until exact association derivatives, phase NLP
certification, and the collapsed GFPE registry gates are complete. Association site
fractions remain solved internal variables, and direct CppAD recording through
the association fixed-point iteration is forbidden. State and Regression routes
eliminate the site fractions and apply implicit sensitivities.

Broader associating equilibrium still requires one complete architecture before
public exposure: either eliminate site fractions and provide complete implicit
first- and second-order derivatives for all Ipopt objective and constraint
residuals, or lift site fractions as explicit NLP variables with exact
mass-action constraints, true site topology, and exact Lagrangian Hessian rows.
See ``docs/adr/0004-associating-equilibrium-architecture.md`` and
``docs/superpowers/milestones/M4-equilibrium/generalized-fluid-phase-equilibrium.md``.

Repeated State Work
-------------------

For many property calls, keep the loop downstream-owned. Feed each successful
state density into the next pressure-closed state as ``rho_guess``. Use direct ``rho=...`` only when density is the closure variable,
not when exact pressure closure is required.
