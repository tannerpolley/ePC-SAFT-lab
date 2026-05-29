Parameter Regression
====================

Public regression now runs through ``Regression(mixture, ...)`` in the
``epcsaft-regression`` extension package. The reset frontend does not expose
free ``fit_*`` functions or backend-selection flags.

Current Public Proof
--------------------

The current trusted public regression path is pure-neutral hydrocarbon fitting
through the native Ceres route with CppAD-backed Jacobians. Ceres is the
regression optimizer dependency; CppAD-backed provider derivatives remain
core-owned:

.. code-block:: python

   from epcsaft import Mixture
   from epcsaft_regression import Regression

   result = Regression(Mixture(parameters)).fit_pure_neutral(
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
