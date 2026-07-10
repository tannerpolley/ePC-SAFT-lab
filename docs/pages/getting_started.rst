Getting Started
===============

Install
-------

For the current release, install the Windows CPython 3.13 wheel from GitHub:

.. code-block:: powershell

   python -m pip install C:\path\to\epcsaft-0.2.0-*.whl

The GitHub URLs below point at the current organization-owned source location.

The ``v0.2.0`` tag also supports source installs that build the native
extension locally:

.. code-block:: bash

   python -m pip install "epcsaft @ git+https://github.com/ePC-SAFT/ePC-SAFT.git@v0.2.0#subdirectory=packages/epcsaft"

After the package is published on PyPI, use the standard package-manager
command:

.. code-block:: bash

   python -m pip install epcsaft

For a local editable checkout:

.. code-block:: bash

   git clone https://github.com/ePC-SAFT/ePC-SAFT.git
   cd ePC-SAFT
   python -m pip install -e packages/epcsaft

Source and editable installs build a native C++ extension. They require Python
``>=3.9``, a C++ compiler, CMake, and Ninja or another CMake generator. See
:doc:`release_installation` for the full install matrix.

Verify the install
------------------

.. code-block:: python

   import epcsaft

   print(epcsaft.__version__)
   print(epcsaft.runtime_build_info())

Create a mixture
----------------

For a one-component example, create a ``ParameterSet`` and pass it to
``Mixture``:

.. code-block:: python

   import numpy as np
   from epcsaft import Mixture, ParameterSet, State

   parameters = ParameterSet.from_dict(
       {
           "schema": "epcsaft.parameter-set",
           "schema_version": 1,
           "components": ["Toluene"],
           "pure_records": [{
               "component": "Toluene",
               "molar_mass": 92.1405e-3,
               "molar_mass_units": "kg/mol",
               "m": 2.8149,
               "sigma": 3.7169,
               "epsilon_k": 285.69,
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
   mixture = Mixture(parameters)

   state = State(mixture, T=320.0, x=np.asarray([1.0]), P=101325.0)
   print(state.density())
   print(state.z())
   print(state.fugacity_coefficients())

Use pressure or density closure
-------------------------------

Every state uses exactly one closure variable:

- ``P`` asks the EOS to solve for density.
- ``rho`` evaluates the model directly at a supplied molar density.
- ``rho_guess`` is allowed only with ``P`` and seeds the pressure-density solve.

.. code-block:: python

   base = State(mixture, T=320.0, x=np.asarray([1.0]), P=101325.0)
   nearby = State(
       mixture,
       T=321.0,
       x=np.asarray([1.0]),
       P=101325.0,
       rho_guess=base.density(),
   )

   density_state = State(mixture, T=320.0, x=np.asarray([1.0]), rho=base.density())
   print(density_state.pressure())

Create a parameter folder
-------------------------

For real systems, keep your parameter data in a folder you control:

.. code-block:: python

   from epcsaft import create_input_template

   template_root = create_input_template(
       "/path/to/my_epcsaft_data/water_salt_case",
       components=["H2O", "Na+", "Cl-"],
   )

Fill every null scientific field in ``parameter_set.json`` with a traceable
value, then load the ``ParameterSet`` for the case you want to run. Missing
values fail with the component and field name.

Next steps
----------

- :doc:`user_parameter_templates` explains the parameter-folder layout.
- :doc:`user_options` lists supported model options.
- :doc:`package_guide` gives task-based examples.
- :doc:`equilibrium_cookbook` shows public equilibrium workflow examples.
- :doc:`api_reference` lists the public API.
