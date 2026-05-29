Model Options
=============

The reset public API uses ``ModelOptions`` for formulation choices. ``ParameterSet``
stores ePC-SAFT parameter data; ``ModelOptions`` is passed to ``Mixture`` or loaded
from ``model_options.json``/``user_options.json`` by ``Mixture.from_folder``.

Example:

.. code-block:: python

   from epcsaft import BornModelOptions, Mixture, ModelOptions

   mixture = Mixture(
       parameters,
       model_options=ModelOptions(
           differential_mode="autodiff",
           relative_permittivity_rule="component_linear",
           born_model=BornModelOptions(
               enabled=True,
               born_diameter_rule="sigma",
               solvation_shell_model=True,
               dielectric_saturation=True,
           ),
       ),
   )

Supported public options:

- ``differential_mode``: only ``"autodiff"``. This selects the CppAD-backed
  derivative route.
- ``relative_permittivity_rule``: ``"component_linear"``, ``"linear"``,
  ``"constant"``, ``"combined"``, ``"empirical"``, and related catalog rules.
- ``born_model.enabled``: toggles the Born residual Helmholtz contribution.
- ``born_model.born_diameter_rule``: ``"sigma"``, ``"sigma_reduced"``,
  ``"temperature_dependent"``, or ``"fitted"``. ``"fitted"`` requires positive
  ionic ``born_diameter`` values.
- ``born_model.solvation_shell_model`` and ``born_model.dielectric_saturation``:
  both default to ``True`` for canonical Born SSM+DS behavior. Setting both to
  ``False`` reduces the canonical path to direct Born behavior.

``ModelOptions.help()`` summarizes the supported schema, and
``ModelOptions().explain(parameters)`` reports the resolved runtime meaning and
parameter requirements.

Folder loading:

.. code-block:: python

   mixture = Mixture.from_folder(
       "analyses/paper_validation/2025_figiel/parameters",
       components=["H2O", "Na+", "Cl-"],
   )
