Equilibrium Cookbook
====================

Public equilibrium runs through ``Equilibrium(mixture, route=..., ...)`` and
executes with ``solve()``. The reset frontend does not expose free bubble/dew
functions, typed problem root exports, or backend-selection flags.

Trusted Neutral VLE Routes
--------------------------

The current public equilibrium proof is the pressure-boundary bubble/dew set
and scoped nonassociating hydrocarbon single-component VLE through the selector
core and native Ipopt with exact Hessian callbacks:

.. code-block:: python

   import numpy as np
   from epcsaft import Mixture
   from epcsaft_equilibrium import Equilibrium

   result = Equilibrium(
       Mixture(parameters),
       route="bubble_pressure",
       T=233.15,
       x=np.asarray([0.1, 0.3, 0.6]),
   ).solve(solver_options={"max_iterations": 200, "tolerance": 1.0e-8})

   print(result.problem_kind)
   print(result.diagnostics["hessian_approximation"])

   y = result.y
   p = result.pressure

   Equilibrium(Mixture(parameters), route="dew_pressure", T=233.15, y=y).solve()
   Equilibrium(Mixture(pure_parameters), route="single_component_vle", T=233.15).solve()

The temperature-boundary and TP-flash implementations remain component-level
diagnostics. They are not public routes until literature-backed live solver
evidence is retained and joined to the activation contract.

Closed Validation Families
--------------------------

Neutral LLE, neutral TP flash, temperature-boundary VLE, neutral multiphase,
electrolyte LLE, and standalone reactive speciation are internal validation targets, not
public cookbook routes. Their activation rows or route contracts publish no
production proof. Source-backed artifacts remain available to diagnose and
repair those families before a separate re-admission change. Neutral LLE's
sampled-candidate Stage II audit is not a global HELD proof.

Derivative Contract
-------------------

Public equilibrium routes require CppAD-backed derivatives and exact
Jacobians/Hessians for supported native solves. Unsupported coverage should
raise a clear package error instead of selecting a fallback derivative mode.
