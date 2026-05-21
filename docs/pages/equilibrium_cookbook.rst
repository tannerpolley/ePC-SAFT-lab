Equilibrium Cookbook
====================

Public equilibrium runs through ``Equilibrium(mixture, ...)``. The reset
frontend does not expose free bubble/dew functions, typed problem root exports,
or backend-selection flags.

Trusted Bubble-Pressure Route
-----------------------------

The current public equilibrium proof is the hydrocarbon VLE bubble-pressure
route through native Ipopt with an exact Hessian:

.. code-block:: python

   import numpy as np
   from epcsaft import Equilibrium, Mixture

   result = Equilibrium(
       Mixture(parameters),
       max_iterations=200,
       tolerance=1.0e-8,
   ).bubble_pressure(
       T=233.15,
       x=np.asarray([0.1, 0.3, 0.6]),
   )

   print(result.problem_kind)
   print(result.diagnostics["hessian_approximation"])

Derivative Contract
-------------------

Public equilibrium routes require CppAD-backed derivatives and exact
Jacobians/Hessians for supported native solves. Unsupported coverage should
raise a clear package error instead of selecting a fallback derivative mode.
