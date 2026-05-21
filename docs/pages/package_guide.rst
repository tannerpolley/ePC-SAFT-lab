Package Guide
=============

This guide groups the reset public package surface by task. The package root
exports ``Mixture``, ``State``, ``Equilibrium``, ``Regression``,
``ParameterSet``, ``ModelOptions``, and ``create_input_template``.

Constructing A Model
--------------------

Build a ``ParameterSet`` from ePC-SAFT parameter data, then attach
``ModelOptions`` when constructing ``Mixture``:

.. code-block:: python

   import numpy as np
   from epcsaft import Mixture, ModelOptions, ParameterSet, State

   parameters = ParameterSet.from_dict(
       {
           "MW": np.asarray([16.043e-3]),
           "m": np.asarray([1.0]),
           "s": np.asarray([3.7039]),
           "e": np.asarray([150.03]),
       },
       species=["Methane"],
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

   from epcsaft import Equilibrium

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

   from epcsaft import Regression

   result = Regression(mixture).fit_pure_neutral(
       records,
       component="Methane",
       assoc_scheme="",
       fixed_parameters=fixed_parameters,
       initial_guess={"m": 1.1, "s": 3.6, "e": 145.0},
   )

Input Templates
---------------

``create_input_template(...)`` creates CSV parameter tables plus JSON option
files for model, state, equilibrium, and regression workflow defaults:

.. code-block:: python

   from epcsaft import create_input_template

   create_input_template(
       r"C:\Users\Tanner\Documents\my_epcsaft_data\methane_case",
       components=["Methane"],
       workflows=("state", "equilibrium", "regression"),
   )
