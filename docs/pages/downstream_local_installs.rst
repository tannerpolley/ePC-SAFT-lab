Local Source Installs
=====================

This page is for projects that use a local ePC-SAFT checkout before or instead
of installing a published wheel.

Editable install
----------------

Use an editable install when you are changing Python files in the ePC-SAFT
checkout:

.. code-block:: powershell

   cd C:\path\to\ePC-SAFT
   python -m pip install -e packages/epcsaft

With ``uv``:

.. code-block:: powershell

   uv pip install -e packages/epcsaft

Editable installs use the same native build backend as wheel installs. Python
source changes are picked up from the checkout. If you change C++ sources,
pybind bindings, CMake files, or build metadata, rerun the editable install
command so the native extension is rebuilt.

Local path dependency
---------------------

Use a path dependency when another project should install a local ePC-SAFT
checkout:

.. code-block:: toml

   dependencies = [
       "epcsaft @ file:///C:/Users/Tanner/Documents/git/ePC-SAFT/packages/epcsaft",
   ]

Recommended local dependency loop
---------------------------------

Install or refresh the local package once, then prove the installed package and
the downstream repo-local integration wrapper without implicit sync:

.. code-block:: powershell

   $env:UV_CACHE_DIR = "$PWD\.uv-cache"
   uv sync --reinstall-package epcsaft
   uv run --no-sync python -m epcsaft
   uv run --no-sync python scripts/check_epcsaft_integration.py --mode dev

The repo's current CI path-install smoke uses Python 3.13. The package
metadata remains broader, but Python 3.13 is the baseline to match when
checking current local-install behavior.

Use ``uv run --no-sync`` after a known-good install because ordinary ``uv run`` is allowed to sync the environment. For a local native path dependency, that sync can rebuild ePC-SAFT when the downstream goal is only to run a smoke test.

Do not start multiple downstream ``uv run`` commands in parallel until the reinstall has completed. If parallel checks are needed, run the reinstall once first, then use ``uv run --no-sync`` for every parallel check.

The current downstream repos ``MEA-Thermodynamics``, ``Lithium_Extraction``,
and ``MEA-Absorption-Column`` all expose the repo-local install check
``scripts/check_epcsaft_integration.py --mode dev``. Run that first in the
downstream repo after reinstalling the local package, then run one real
workflow command from that repo separately. The real workflow runs are not
replaced by package-side smokes; issue #119 tracks them as a later release-gate
phase.

Build directory behavior
------------------------

PEP 517 wheel builds use an isolated temporary native build directory by default. This avoids repeated downstream path installs writing into the shared source checkout ``build/`` tree, which is the common source of Windows ``_core*.pyd`` lock races.

If you intentionally want a persistent build directory for a downstream reinstall, set:

.. code-block:: powershell

   $env:EPCSAFT_PEP517_BUILD_DIR = "$PWD\.uv-cache\epcsaft-build"
   uv sync --reinstall-package epcsaft

This keeps the package-install build tree around so repeated provider installs
can reuse CMake/Ninja provider build state.

Reusable Ceres package
----------------------

Provider package installs are provider-only and do not compile Ceres or Ipopt.
When repeated source-checkout development builds need Ceres for the regression
extension, build Ceres once in the ePC-SAFT checkout and pass the result to the
dev build:

.. code-block:: powershell

   cd C:\path\to\ePC-SAFT
   uv run python scripts\dev\build_system_ceres.py --parallel 4
   uv run python scripts\dev\build_epcsaft.py --use-system-ceres --ceres-dir C:\path\to\lib\cmake\Ceres

For normal ePC-SAFT source development, keep using the explicit in-place dev build:

.. code-block:: powershell

   uv run python scripts\dev\build_epcsaft.py
   uv run python scripts\dev\build_epcsaft.py --build-only --parallel 10

The default dev-script build is the required source-checkout native dependency
profile: Ceres ON, CppAD ON, and Ipopt ON when ``EPCSAFT_IPOPT_ROOT``,
``EPCSAFT_PEP517_IPOPT_ROOT``, ``--ipopt-dir``, or the Windows local SDK default
``%USERPROFILE%\Documents\deps\ipopt-msvc`` provides a native Ipopt install.
Editable, wheel, and downstream path installs of ``epcsaft`` remain
provider-only; Ipopt-enabled native equilibrium routes require an explicit
source-checkout build with Ipopt enabled. New dev build configurations prefer
Ninja when available. Existing ``build/dev`` trees keep their configured
generator until you run the coordinated repair command
``uv run python scripts\dev\build_epcsaft.py --clean --generator ninja``.

Windows ``_core`` lock failures
-------------------------------

If a build reports ``Permission denied`` while writing ``_core*.pyd``, a Python process is usually still importing the extension. Stop downstream tests, Python REPLs, IDE runs, and parallel workers that imported ``epcsaft._core``. Then run exactly one reinstall/build command before starting checks again.

Runtime metadata
----------------

Downstream projects can confirm which package source they are using:

.. code-block:: python

   import epcsaft

   print(epcsaft.__version__)
   print(epcsaft.__git_commit__)
   print(epcsaft.runtime_build_info())

``runtime_build_info()`` reports package version, source path/commit when discoverable, native extension path, Python version, and platform information.

Capability discovery
--------------------

Use provider and extension capabilities before wiring high-level downstream
workflows:

.. code-block:: python

   import epcsaft
   import epcsaft_equilibrium

   provider_caps = epcsaft.capabilities()
   equilibrium_caps = epcsaft_equilibrium.capabilities()
   assert provider_caps["package"] == "epcsaft"
   assert provider_caps["owner"] == "core_provider"
   assert equilibrium_caps["production_families"] == [
       "neutral_tp_flash",
       "neutral_lle",
       "bubble_dew_derived_routes",
   ]
   assert "bubble_pressure" in equilibrium_caps["public_routes"]
   assert "flash" in equilibrium_caps["public_routes"]

Native EOS/property calls and native regression helpers are available. The
production equilibrium public route list contains route names for
constructor-configured ``Equilibrium(mixture, route=..., ...).solve()``
workflows: selector-backed neutral VLE bubble/dew pressure and temperature
specs, certified two-phase flash, and neutral nonassociating LLE. Electrolyte,
reactive, and speciation families are declared in the native activation matrix
without being advertised as callable routes.

For routing examples and the production/opt-in solver table, see
:doc:`equilibrium_cookbook`.

Capability status summary
~~~~~~~~~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1

   * - Area
     - Status
     - Notes
   * - Neutral TP flash
     - Production selector-backed native Ipopt route when compiled
     - Certified two-phase flash only; Python does not provide an alternate solve loop.
   * - Neutral LLE
     - Production selector-backed native Ipopt route when compiled
     - Neutral nonassociating LLE only.
   * - Neutral bubble/dew pressure and temperature
     - Native Ipopt route when compiled
     - Requires an Ipopt-enabled build; Python does not provide an alternate solve loop.
   * - Neutral stability
     - Native Ipopt route when compiled
     - Uses native TPD route builders; Python does not provide an alternate solve loop.
   * - Electrolyte stability
     - Native Ipopt route when compiled
     - Uses native charge-constrained TPD route builders; Python does not provide an alternate solve loop.
   * - Electrolyte LLE
     - Native Ipopt route when compiled
     - Public package route is limited to the retained source-backed
       H2O/Ethanol/Butanol/Na+/Cl- NaCl mixed-solvent fixture through
       ``route="electrolyte_lle"``; generic salt/solvent, reactive, CE/CPE,
       and regression claims remain downstream or future-gate work.
   * - Reactive speciation
     - Explicit Ipopt ideal route
     - Native Ipopt support covers homogeneous ``ideal_mole_fraction`` when compiled; activity and concentration residual diagnostics use exact CppAD-implicit phase-state derivatives, while production nonideal solves require the native Gibbs/activity NLP route builder.
   * - Electrolyte bubble pressure
     - Native Ipopt route when compiled
     - Fixed liquid composition with neutral vapor species; ions remain liquid-only.
   * - Reactive electrolyte bubble
     - Staged native route when compiled
     - Requires native speciation followed by the native Ipopt fixed-liquid electrolyte bubble route.
   * - IPOPT
     - Optional native NLP backend
     - Owns production equilibrium solves as route builders land; Python does not provide an alternate optimizer path.

Package-side generic contract smoke coverage
--------------------------------------------

The upstream package tests cover three downstream-shaped generic API contracts
without adding downstream-specific public APIs:

* Reactive speciation with generic target rows for speciation, volatile partial
  pressure, and activity observations.
* Electrolyte LLE with generic solvent-feed, salt-molality, phase-composition,
  mean-ionic-activity, and regularization row shapes. This smoke coverage does
  not broaden the admitted ``electrolyte_lle`` route beyond the retained
  source-backed package fixture.
* Reactive electrolyte bubble pressure with generic speciation, fugacity, and
  partial-pressure rows.

Downstream projects should build their own project-specific metrics outside
``epcsaft``. The package boundary is the generic problem, result, capability,
and regression-target schema. Public API names are intentionally not tied to
MEA, lithium extraction, absorption columns, distribution coefficients,
selectivity, or other application labels.

These package-side tests do not count as the real downstream workflow proof
required by issue #119. They verify that a local install exposes the generic
package contracts that downstream repos consume. The required downstream proof
is still one real recorded workflow run each in ``MEA-Thermodynamics``,
``Lithium_Extraction``, and ``MEA-Absorption-Column`` after the local install
check has passed.

The smoke tests also assert that the public derivative contract keeps finite
difference route. Use ``analytic``, ``cppad``, ``analytic_implicit``, or
``cppad_implicit`` derivative routes where derivatives are required.
