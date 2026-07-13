Parameter Regression
====================

Public regression is configured through ``Regression(mixture, controls=...)``
in the ``epcsaft-regression`` extension package. The frontend does not expose
free ``fit_*`` functions, loose-record fit paths, or backend-selection flags.

Current Public Proof
--------------------

The configured workflow compiles one strict ``TargetDataset`` and explicit
``FittedParameter`` tuple into a provider-fingerprinted ``FitProblem``. Native
results and evaluation oracles are returned only through immutable
``RegressionReceipt`` views:

.. code-block:: python

   from epcsaft_regression import Regression

   regression = Regression(mixture, controls=controls)
   result = regression.fit(
       dataset,
       parameters=fitted_parameters,
   )
   evaluation = regression.evaluate(
       result.problem,
       parameter_values=result.final_parameters,
   )

At the current migration checkpoint, production target dispatch remains closed
until the immutable resolved-input overlay passes its Stage 4 parity gate. The
configured compiler and receipt path are public contract evidence, not a claim
that a production fit is already admitted.

Completion Contract
-------------------

Regression workflows must report exact CppAD derivative coverage. Missing
coverage is a blocker, not a fallback to a Python optimizer loop or a
user-selectable derivative mode. Ceres is the regression optimizer dependency;
CppAD-backed provider derivatives remain core-owned.
