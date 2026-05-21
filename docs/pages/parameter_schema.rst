Parameter Schema
================

``ParameterSet`` is the public parameter boundary. It stores ePC-SAFT parameter
data and can still emit the native runtime payload needed by the internal C++
bridge, but model and workflow options are not owned by ``ParameterSet``.

Constructing A ParameterSet
---------------------------

.. code-block:: python

   import numpy as np
   from epcsaft import ParameterSet

   parameters = ParameterSet.from_dict(
       {
           "m": np.asarray([1.0, 1.6069]),
           "s": np.asarray([3.7039, 3.5206]),
           "e": np.asarray([150.03, 191.42]),
           "k_ij": np.asarray([[0.0, 3.0e-4], [3.0e-4, 0.0]]),
       },
       species=["Methane", "Ethane"],
   )

Using ModelOptions
------------------

``ModelOptions`` belongs to ``Mixture``:

.. code-block:: python

   from epcsaft import Mixture, ModelOptions

   mixture = Mixture(
       parameters,
       model_options=ModelOptions(relative_permittivity_rule="component_linear"),
   )

The reset API has no public backend-mode flag. Public ``State``,
``Equilibrium``, and ``Regression`` workflows require CppAD-backed derivative
coverage and raise when coverage is missing.
