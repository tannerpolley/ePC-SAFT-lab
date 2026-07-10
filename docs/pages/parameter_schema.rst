Parameter Schema
================

``ParameterSet`` is the public parameter boundary. It stores ePC-SAFT parameter
data and can still emit the native runtime payload needed by the internal C++
bridge, but model and workflow options are not owned by ``ParameterSet``.

Constructing A ParameterSet
---------------------------

.. code-block:: python

   from epcsaft import ParameterSet

   parameters = ParameterSet.from_dict(
       {
           "schema": "epcsaft.parameter-set",
           "schema_version": 1,
           "components": ["Methane"],
           "pure_records": [{
               "component": "Methane",
               "molar_mass": 16.043e-3,
               "molar_mass_units": "kg/mol",
               "m": 1.0,
               "sigma": 3.7039,
               "epsilon_k": 150.03,
               "charge": 0.0,
               "epsilon_k_ab": 0.0,
               "kappa_ab": 0.0,
               "association_scheme": None,
               "association_sites": [],
               "relative_permittivity": 1.0,
               "born_diameter": 0.0,
               "solvation_factor": 1.0,
           }],
           "binary_records": [],
           "metadata": {
               "source": "Gross and Sadowski (2001), Table 2",
               "source_backed": True,
               "auxiliary_neutral_fields": "equation_structural_neutral_inactive",
           },
       }
   )

The schema, schema version, every scientific pure-component field, and source
metadata are explicit. Unversioned arrays, missing fields, non-finite values,
unknown keys, and inferred component properties are rejected.

Using ModelOptions
------------------

``ModelOptions`` belongs to ``Mixture``:

.. code-block:: python

   from epcsaft import Mixture, ModelOptions

   mixture = Mixture(
       parameters,
       model_options=ModelOptions(relative_permittivity_rule="component_linear"),
   )

The reset API has no public backend-mode flag. Public provider ``State``,
extension ``Equilibrium``, and transition ``Regression`` workflows require
CppAD-backed derivative coverage and raise when coverage is missing.
