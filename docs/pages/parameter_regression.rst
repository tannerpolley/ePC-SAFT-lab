Parameter Regression
====================

Public regression runs through ``Mixture.regression(...)``. The reset frontend
does not expose free ``fit_*`` functions or backend-selection flags.

Current Public Proof
--------------------

The current trusted public regression path is pure-neutral hydrocarbon fitting
through the native Ceres route with CppAD-backed Jacobians:

.. code-block:: python

   from epcsaft import Mixture

   result = Mixture(parameters).regression().fit_pure_neutral(
       records,
       component="Methane",
       assoc_scheme="",
       fixed_parameters=fixed_parameters,
       initial_guess={"m": 1.1, "s": 3.6, "e": 145.0},
   )

Completion Contract
-------------------

Regression workflows must report exact CppAD derivative coverage. Missing
coverage is a blocker, not a fallback to a Python optimizer loop or a
user-selectable derivative mode.
