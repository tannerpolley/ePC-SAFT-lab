Equilibrium Architecture
========================

This page describes the equilibrium surface now owned by the
``epcsaft-equilibrium`` extension package.

The current reset public API is workflow-object based:

* ``Equilibrium(mixture, route=..., ...).solve()`` for certified neutral
  nonassociating VLE, flash, and LLE route specs.
* ``reactive_speciation(...)`` for standalone homogeneous chemical/speciation
  equilibrium over true species, explicit reactions, feed amounts, and explicit
  standard-state metadata.
* Additional associating, electrolyte, reactive, and speciation families are
  declared in the native activation matrix as not exposed until they have
  production selector support, focused public tests, and capability evidence.

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

   flash = Equilibrium(
       mixture,
       route="flash",
       T=233.15,
       P=result.pressure,
       z=[0.4, 0.25, 0.35],
   ).solve()

   lle = Equilibrium(
       neutral_nonassociating_binary,
       route="lle",
       T=225.0,
       P=1.0e6,
       z=[0.5, 0.5],
   ).solve()

Request Normalization
---------------------

Public request normalization lives at ``Equilibrium(mixture, route=..., ...)``.
The workflow object owns route/spec validation and delegates only to the
selector core for production neutral two-phase routes. Solver controls are passed to
``solve(solver_options=...)``. Selector-ineligible inputs fail before solver
dispatch; solver or certification failures after dispatch raise with
diagnostics. Flash is a selector-owned route spec over the same native VLE
residual/constraint core as bubble and dew routes, not a direct pybind route or
Python-owned optimizer loop. Neutral LLE is also selector-owned: the activation
matrix row builds a ``liquid1``/``liquid2`` activation plan and reuses the same
generic two-phase EOS NLP core with a phase-distance anti-collapse constraint
instead of a VLE ``phase_volume_gap``. The phase-distance constraint proves
candidate distinctness, not thermodynamic equilibrium; accepted neutral TP
flash and neutral nonassociating LLE results also require
``held_tpd_volume_composition`` discovery and ``tpd_postsolve`` phase-set
certification. Route-specific public methods are intentionally absent;
``solve`` is the only public execution lane.

Solver Selection
----------------

The reset public frontend does not expose a solver-backend selector. Public
equilibrium workflows choose the required native route directly and raise at the
route boundary when the compiled dependency or CppAD coverage is missing. The
trusted public proof set is the hydrocarbon neutral VLE/flash route family,
neutral LLE, the source-backed methanol/cyclohexane associating LLE fixture,
and the source-backed Khudaida explicit-ion NaCl mixed-solvent electrolyte LLE
fixture through the native selector core, Ipopt, and exact Hessian or exact
reduced-derivative callbacks. Broader associating, generic electrolyte,
reactive phase, CPE, and coupled speciation route families remain
declared-not-exposed activation rows until they are ported behind the selector
and reset ``Equilibrium(mixture, route=..., ...)`` workflow. The standalone
``reactive_speciation(...)`` API is homogeneous CE only; it is not a reactive
LLE, electrolyte LLE, or simultaneous phase-plus-chemistry route.

The convex Gibbs formulation is limited to homogeneous ideal reaction or
speciation subkernels and validation tests. Full ePC-SAFT multiphase,
electrolyte, density-coupled, or association-coupled equilibrium should be
treated as a thermodynamic constrained NLP, not as a globally convex problem.
Production equilibrium routes require exact analytic or CppAD Jacobians. Native
Ceres owns the current monorepo regression solves and the future
``epcsaft-regression`` capability. Ipopt owns the current monorepo equilibrium
solves and the future ``epcsaft-equilibrium`` capability. CppAD and implicit
sensitivities remain provider-owned where the EoS route is validated.

Ipopt diagnostics are route-owned and available through
``result.diagnostics``. Use ``ipopt_iteration_history_limit`` to retain recent
iteration records and ``ipopt_print_level`` only for local debugging output;
normal tests should assert the diagnostic payload instead of enabling noisy
solver logs.

Associating Equilibrium Boundary
--------------------------------

Associating mixtures remain selector-ineligible for generalized production
equilibrium routes under the ADR 0004 boundary. The prior narrow associating
``bubble_pressure`` admission path has been retired in favor of the shared GFPE
TP-flash plan. Gross/Sadowski 2002 remains the first associating proof
target, but it must enter through exact association derivatives, phase NLP
certification, and the collapsed GFPE registry gates. Association site
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
