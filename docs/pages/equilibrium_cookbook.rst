Equilibrium Cookbook
====================

Public equilibrium runs through ``Equilibrium(mixture, route=..., ...)`` and
executes with ``solve()``. The reset frontend does not expose free bubble/dew
functions, typed problem root exports, or backend-selection flags.

Trusted Neutral VLE Routes
--------------------------

The current public equilibrium proof is the hydrocarbon neutral VLE route set
through the selector core and native Ipopt with exact Hessian callbacks:

.. code-block:: python

   import numpy as np
   from epcsaft import Equilibrium, Mixture

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

   Equilibrium(Mixture(parameters), route="bubble_temperature", P=p, x=[0.1, 0.3, 0.6]).solve()
   Equilibrium(Mixture(parameters), route="dew_pressure", T=233.15, y=y).solve()
   Equilibrium(Mixture(parameters), route="dew_temperature", P=p, y=y).solve()
   Equilibrium(Mixture(parameters), route="flash", T=233.15, P=p, z=0.5 * (np.asarray([0.1, 0.3, 0.6]) + y)).solve()

``flash`` v1 accepts only certified two-phase neutral VLE splits. Single-phase
or degenerate results raise with diagnostics instead of being reported as a
production flash solution.

Derivative Contract
-------------------

Public equilibrium routes require CppAD-backed derivatives and exact
Jacobians/Hessians for supported native solves. Unsupported coverage should
raise a clear package error instead of selecting a fallback derivative mode.
