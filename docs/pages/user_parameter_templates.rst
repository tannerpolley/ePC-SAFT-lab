User Input Templates
====================

Use ``create_input_template(...)`` to create a strict input scaffold. The
scaffold separates one versioned parameter document from workflow/model
options:

- ``parameter_set.json``
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

Every generated scientific field in ``parameter_set.json`` is null. The file
cannot load until each field is replaced by a finite, traceable value and the
metadata identifies its source. The template does not infer charge from a
component name and does not prefill missing binary interactions with zeros.

``ParameterSet`` owns the parameter values. ``ModelOptions`` owns formulation
choices such as the relative-permittivity mixture rule and Born-family variant
selection. State, equilibrium, and regression options stay in their own JSON
files and are passed to their owning workflow objects.
