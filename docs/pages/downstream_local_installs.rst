Local Source Installs
=====================

This page is for projects that use a local ePC-SAFT checkout before or instead
of installing a published wheel.

Editable install
----------------

Use an editable install when you are changing Python files in the ePC-SAFT
checkout:

.. code-block:: bash

   cd /path/to/ePC-SAFT
   python -m pip install -e packages/epcsaft

With ``uv``:

.. code-block:: bash

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
       "epcsaft @ file:///home/user/workspaces/ePC-SAFT/packages/epcsaft",
   ]

Recommended local dependency loop
---------------------------------

Install or refresh the local package once, then prove the installed package and
the downstream repo-local integration wrapper without implicit sync:

.. code-block:: bash

   export UV_CACHE_DIR="$PWD/.uv-cache"
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

PEP 517 wheel builds use an isolated temporary native build directory by default. This avoids repeated downstream path installs writing into the shared source checkout ``build/`` tree, which can cause stale ``_core*.so`` artifacts during parallel work.

If you intentionally want a persistent build directory for a downstream reinstall, set:

.. code-block:: bash

   export EPCSAFT_PEP517_BUILD_DIR="$PWD/.uv-cache/epcsaft-build"
   uv sync --reinstall-package epcsaft

This keeps the package-install build tree around so repeated provider installs
can reuse CMake/Ninja provider build state.

Reusable Ceres package
----------------------

Provider package installs are provider-only and do not compile Ceres or Ipopt.
When repeated source-checkout development builds need Ceres for the regression
extension, build Ceres once in the ePC-SAFT checkout and pass the result to the
dev build:

.. code-block:: bash

   cd /path/to/ePC-SAFT
   uv run python scripts/dev/build_system_ceres.py --parallel 4
   uv run python scripts/dev/build_epcsaft.py --use-system-ceres --ceres-dir /path/to/lib/cmake/Ceres

For normal ePC-SAFT source development, keep using the explicit in-place dev build:

.. code-block:: bash

   uv run python scripts/dev/build_epcsaft.py
   uv run python scripts/dev/build_epcsaft.py --build-only --parallel 10

The default dev-script build is the required source-checkout native dependency
profile: Ceres ON, CppAD ON, and Ipopt ON when ``EPCSAFT_IPOPT_ROOT``,
``EPCSAFT_PEP517_IPOPT_ROOT``, ``--ipopt-dir``, or Linux default Ipopt
discovery provides a native Ipopt install.
Editable, wheel, and downstream path installs of ``epcsaft`` remain
provider-only; Ipopt-enabled native equilibrium routes require an explicit
source-checkout build with Ipopt enabled. New dev build configurations prefer
Ninja when available. Existing ``build/dev`` trees keep their configured
generator until you run the coordinated repair command
``uv run python scripts/dev/build_epcsaft.py --clean --generator ninja``.

Linux ``_core`` lock failures
-----------------------------

If a build reports ``Permission denied`` while writing ``_core*.so``, inspect
the target directory ownership and permissions and stop any concurrent build
that is writing the same output. A Linux process may keep the previous inode
mapped after replacement, but it does not lock the ``.so`` path like a Windows
``.pyd``. Run exactly one reinstall/build command before starting checks again.

Runtime metadata
----------------

Downstream projects can confirm which package source they are using:

.. code-block:: python

   import epcsaft

   print(epcsaft.__version__)
   print(epcsaft.runtime_build_info()["source_git_commit"])
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
   exported_families = set(equilibrium_caps["production_families"])
   exported_routes = set(equilibrium_caps["public_routes"])
   assert exported_families == {
       "bubble_dew_derived_routes",
       "single_component_vle",
   }
   assert exported_routes == {
       "bubble_pressure",
       "dew_pressure",
       "single_component_vle",
   }

Native EOS/property calls and native regression helpers are available. The
``production_families`` and ``public_routes`` fields are evidence-derived from
the current activation surface. The exported route surface is limited to
pressure-boundary bubble/dew and scoped nonassociating hydrocarbon
single-component VLE.

Standalone CE remains an internal validation workflow. Its re-admission gate
must pass before any public route or capability claim is restored:

.. code-block:: bash

   uv run --no-sync python scripts/validation/check_standalone_ce_gate.py --json --require-single-nlp-path --require-oracles --require-complete

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
     - Internal validation only
     - The retained workbook is not a literature benchmark, so ``flash`` is not a public route.
   * - Neutral LLE
     - Internal validation only
     - Retained Matsuda/NIST and Gross/Sadowski artifacts do not replace a global HELD Stage II proof.
   * - Neutral bubble/dew pressure
     - Production selector-backed native Ipopt routes when compiled
     - Temperature-boundary routes remain internal component diagnostics.
   * - Single-component VLE
     - Production selector-backed native Ipopt route when compiled
     - Nonassociating methane, ethane, and propane within the retained NIST ranges.
   * - Multiphase, electrolyte LLE, and reactive speciation
     - Internal validation only
     - These activation families publish no public or proof routes.
   * - IPOPT
     - Optional native NLP backend
     - Owns production equilibrium solves as route builders land; Python does not provide an alternate optimizer path.

Closed-family validation evidence
---------------------------------

Source-backed electrolyte and reactive calculations are retained only as
internal repair diagnostics. They are not package API smoke tests and do not
admit an equilibrium route.

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

The smoke tests also assert that the public derivative contract exposes only
exact derivative routes. Use ``analytic``, ``cppad``,
``analytic_implicit``, or ``cppad_implicit`` derivative routes where
derivatives are required.
