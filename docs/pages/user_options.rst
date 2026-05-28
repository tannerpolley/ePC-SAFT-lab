Model Options
=============

The reset public API uses ``ModelOptions`` instead of a public backend-mode
``user_options.json`` surface. ``ParameterSet`` stores ePC-SAFT parameter data;
``ModelOptions`` is passed to ``Mixture`` and owns formulation choices.

Example:

.. code-block:: python

   from epcsaft import Mixture, ModelOptions

   mixture = Mixture(
       parameters,
       model_options=ModelOptions(
           relative_permittivity_rule="component_linear",
           born_formulation="disabled",
       ),
   )

Supported public options:

- ``relative_permittivity_rule``: ``"component_linear"``, ``"linear"``, or
  ``"constant"``
- ``born_formulation``: ``"disabled"``, ``"born"``, ``"ssm"``, ``"ds"``, or
  ``"ssm_ds"``

Derivative selection is not a user option. Public provider ``State``,
extension ``Equilibrium``, and transition ``Regression`` workflows require
CppAD-backed coverage and raise when the requested formulation is not covered.
