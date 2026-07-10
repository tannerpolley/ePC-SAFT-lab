Overview
========

``epcsaft`` is a Linux-first Python package for PC-SAFT and electrolyte
PC-SAFT thermodynamic calculations. The public interface is Python, while the
equation-of-state runtime is implemented in native C++ through ``pybind11``.

This release is still a monorepo transition build. Ipopt-backed equilibrium is
owned by ``epcsaft-equilibrium``, and Ceres-backed regression is owned by
``epcsaft-regression``. Each extension is a separate distribution that can
consume an installed provider wheel and its native SDK. The monorepo checkout
remains the development and release-proof source until those extension
distributions are published.

Current package version: ``0.2.0``

What the package does
---------------------

Use ``epcsaft`` to build PC-SAFT/ePC-SAFT mixtures, evaluate thermodynamic
states, compute fugacity and activity coefficients, fit supported pure-neutral
parameter sets against tabular data through ``epcsaft_regression``, and pair it
with ``epcsaft_equilibrium`` for constructor-configured neutral equilibrium
routes when native Ipopt is available.

The main user objects are:

- ``ParameterSet``: stores ePC-SAFT parameter data.
- ``ModelOptions``: selects model formulation choices for a ``Mixture``.
- ``Mixture``: stores parameters/options and creates workflow objects.
- ``State``: evaluates CppAD-backed density, pressure, fugacity, and derivative
  payloads.
- ``Equilibrium``: configured workflow object imported from
  ``epcsaft_equilibrium``.
- ``Regression``: configured workflow object imported from
  ``epcsaft_regression``.
- ``create_input_template(...)``: creates a versioned parameter document and workflow-option scaffolds.
- ``capabilities()``: reports available runtime and solver paths.

Install
-------

The ``v0.2.0`` GitHub release provides a Windows CPython 3.13 wheel and source
archive:

``https://github.com/ePC-SAFT/ePC-SAFT/releases/tag/v0.2.0``

That URL is the current organization-owned source location for release history.

Windows users on Python 3.13 can download the wheel and install it directly:

.. code-block:: powershell

   python -m pip install C:\path\to\epcsaft-0.2.0-*.whl

PyPI publishing is configured through GitHub Actions, but the first upload
requires the PyPI pending publisher for this repository. When the project page
is live at ``https://pypi.org/project/epcsaft/``, install with:

.. code-block:: bash

   python -m pip install epcsaft

With ``uv``:

.. code-block:: bash

   uv add epcsaft

If PyPI returns 404 for ``epcsaft``, use the GitHub release wheel above.

The ``v0.2.0`` tag supports source installs that build the native extension
locally:

.. code-block:: bash

   python -m pip install "epcsaft @ git+https://github.com/ePC-SAFT/ePC-SAFT.git@v0.2.0#subdirectory=packages/epcsaft"

With ``uv``:

.. code-block:: bash

   uv add "epcsaft @ git+https://github.com/ePC-SAFT/ePC-SAFT.git@v0.2.0#subdirectory=packages/epcsaft"

Source builds require Python ``>=3.9``, a C++ compiler, CMake, and Ninja or
another CMake generator. Python 3.13 is the current project smoke-test
baseline.

For a normal local source install:

.. code-block:: bash

   git clone https://github.com/ePC-SAFT/ePC-SAFT.git
   cd ePC-SAFT
   python -m pip install packages/epcsaft

For an editable install while changing Python files:

.. code-block:: bash

   python -m pip install -e packages/epcsaft

Editable installs use the same native build backend as wheel installs. Python
source changes are picked up from the checkout. If you change C++ sources,
pybind bindings, CMake files, or build metadata, rerun
``python -m pip install -e packages/epcsaft``.

Equilibrium and regression workflows live in monorepo workspace packages under
``packages/``. In a source checkout, use the uv workspace environment before
importing ``epcsaft_equilibrium`` or ``epcsaft_regression``. Do not install
these transition packages against provider-only ``epcsaft`` wheels; they
require the matching workspace provider build with the relevant native symbols
enabled.

Verify the install
------------------

.. code-block:: python

   import epcsaft
   import epcsaft_equilibrium
   import epcsaft_regression

   print(epcsaft.__version__)
   print(epcsaft.runtime_build_info())
   print(epcsaft.capabilities())
   print(epcsaft_equilibrium.capabilities())
   print(epcsaft_regression.capabilities())

Quick example
-------------

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
   print(state.pressure())
   print(state.z())
   print(state.fugacity_coefficients())

Pressure, density, and seeds
----------------------------

State construction uses exactly one closure variable:

- ``State(..., P=...)`` solves the EOS pressure-density closure.
- ``State(..., rho=...)`` evaluates properties at the supplied molar density.
- ``State(..., P=..., rho_guess=...)`` still solves exact pressure closure, but
  seeds the density solve with a previous good density.

.. code-block:: python

   base = State(mixture, T=320.0, x=np.asarray([1.0]), P=101325.0)
   next_state = State(
       mixture,
       T=321.0,
       x=np.asarray([1.0]),
       P=101325.0,
       rho_guess=base.density(),
   )

   density_state = State(mixture, T=320.0, x=np.asarray([1.0]), rho=base.density())
   print(density_state.pressure())

Parameter data
--------------

Most users should create and own their parameter folders:

.. code-block:: python

   from epcsaft import create_input_template

   template_root = create_input_template(
       "/path/to/my_epcsaft_data/water_salt_case",
       components=["H2O", "Na+", "Cl-"],
   )

The generated ``parameter_set.json`` contains null scientific fields rather
than guessed values. Fill each value and source before loading the
``ParameterSet``; then pass thermodynamic conditions to ``State(...)`` or use
``Equilibrium(...)`` from ``epcsaft_equilibrium`` and ``Regression(...)`` from
``epcsaft_regression``.

Equilibrium
-----------

Use ``epcsaft_equilibrium.capabilities()`` and the cookbook before wiring a
high-level equilibrium workflow. The extension includes native-backed paths for
neutral phase equilibrium through constructor-configured ``Equilibrium(...)``
objects. The production-exposed routes are bubble pressure, dew pressure,
and scoped nonassociating hydrocarbon single-component VLE.

Important boundaries:

- Neutral LLE, bubble/dew temperature, neutral TP flash, neutral multiphase,
  electrolyte LLE, standalone reactive speciation, reactive LLE, reactive electrolyte LLE,
  and CPE remain closed validation families. They publish no public or proof
  routes. Neutral LLE's sampled-candidate Stage II audit is not a global HELD
  proof.
- The GitHub release wheel is built without a local Ipopt runtime dependency.
  Ipopt-backed equilibrium routes require an Ipopt-enabled source or editable
  build.
- IPOPT is an optional native dependency; implemented native equilibrium routes
  use exact Hessians by default when it is compiled, with limited-memory
  Hessians available only as an explicit solver opt-out.
- Downstream case-study models should own their own data, balances, run
  matrices, and acceptance criteria.

Where to go next
----------------

- :doc:`release_installation` for release downloads and source-build notes.
- :doc:`getting_started` for the first local calculation.
- :doc:`user_parameter_templates` to build your own parameter folder.
- :doc:`user_options` for supported ``user_options.json`` settings.
- :doc:`equilibrium_cookbook` for equilibrium and speciation examples.
- :doc:`package_guide` for task-based API guidance.
- :doc:`api_reference` for the full API reference.

License
-------

GNU General Public License v3.0.
