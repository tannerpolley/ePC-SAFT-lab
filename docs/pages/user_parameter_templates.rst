User Input Templates
====================

Use ``create_input_template(...)`` to create a reset input scaffold. The
scaffold separates ePC-SAFT parameter tables from workflow/model options:

- ``pure_parameters.csv``
- ``binary_parameters.csv``
- ``permittivity_parameters.csv``
- ``model_options.json``
- ``state_options.json``
- ``equilibrium_options.json``
- ``regression_options.json``

Example:

.. code-block:: python

   from epcsaft import create_input_template

   root = create_input_template(
       "/path/to/case",
       components=["Methane", "Ethane"],
       workflows=("state", "equilibrium", "regression"),
   )

``ParameterSet`` owns the values from the parameter tables. ``ModelOptions``
owns formulation choices such as the relative-permittivity mixture rule and
Born-family variant selection. State, equilibrium, and regression workflow
defaults stay in their own JSON files and are passed to the matching
``Mixture`` workflow factory.
