Package Guide
=============

This guide groups the reset public package surface by task. The current
provider release exports ``Mixture``, ``State``, ``ParameterSet``,
``ModelOptions``, and ``create_input_template`` from the provider package root.

``Equilibrium`` is imported from ``epcsaft_equilibrium`` and ``Regression`` is
imported from ``epcsaft_regression``.

Constructing A Model
--------------------

Build a ``ParameterSet`` from ePC-SAFT parameter data, then attach
``ModelOptions`` when constructing ``Mixture``:

.. code-block:: python

   import numpy as np
   from epcsaft import Mixture, ModelOptions, ParameterSet, State

   parameters = ParameterSet.from_dict(
       {
           "schema": "epcsaft.parameter-set",
           "schema_version": 2,
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
           "interactions": [],
           "interaction_policies": [],
           "metadata": {
               "source": "Gross and Sadowski (2001), Table 2",
               "source_backed": True,
               "auxiliary_neutral_fields": "equation_structural_neutral_inactive",
           },
       }
   )
   mixture = Mixture(
       parameters,
       model_options=ModelOptions(relative_permittivity_rule="component_linear"),
   )

Evaluating State Properties
---------------------------

Create states from a mixture and thermodynamic conditions:

.. code-block:: python

   state = State(mixture, T=300.0, x=np.asarray([1.0]), P=101325.0, phase="liq")
   print(state.density())
   print(state.z())
   print(state.ares())
   print(state.fugacity_coefficients())
   print(state.pressure_density_derivative()["derivative_backend"])

Equilibrium
-----------

Construct ``Equilibrium`` directly from a ``Mixture``. The trusted equilibrium
proof is the hydrocarbon bubble-pressure route with native Ipopt and an exact
Hessian:

.. code-block:: python

   from epcsaft_equilibrium import Equilibrium

   result = Equilibrium(
       mixture,
       route="bubble_pressure",
       T=233.15,
       x=np.asarray([1.0]),
   ).solve(solver_options={"max_iterations": 200})

Regression
----------

Construct ``Regression`` directly from a ``Mixture``. The current public proof
is pure-neutral hydrocarbon regression through the CppAD/Ceres route:

.. code-block:: python

   from epcsaft_regression import Regression

   result = Regression(mixture).fit_pure_neutral(
       records,
       component="Methane",
       assoc_scheme="",
       fixed_parameters=fixed_parameters,
       initial_guess={"m": 1.1, "s": 3.6, "e": 145.0},
   )

Input Templates
---------------

``create_input_template(...)`` creates one versioned ``parameter_set.json``
plus JSON option files for model, state, equilibrium, and regression. Every
scientific parameter in the generated parameter set is null and must be
replaced with a traceable value before the file can load:

.. code-block:: python

   from epcsaft import create_input_template

   create_input_template(
       "/path/to/my_epcsaft_data/methane_case",
       components=["Methane"],
       workflows=("state", "equilibrium", "regression"),
   )
