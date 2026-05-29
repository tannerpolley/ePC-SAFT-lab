Installation
============

Current package version: ``0.2.0``

Install from a wheel
--------------------

The ``v0.2.0`` GitHub release provides a Windows CPython 3.13 wheel and source
archive:

``https://github.com/ePC-SAFT/ePC-SAFT/releases/tag/v0.2.0``

That URL is the current organization-owned release location.

Windows users on Python 3.13 can download the wheel and install it directly:

.. code-block:: powershell

   python -m pip install C:\path\to\epcsaft-0.2.0-*.whl

This is the simplest install path because the native extension is already
built for your platform. The GitHub release wheel is built without a local
Ipopt runtime dependency; build from source when you need optional
Ipopt-backed equilibrium routes.

Install from PyPI
-----------------

PyPI publishing is configured through GitHub Actions, but the first upload
requires the PyPI pending publisher for this repository. When the project page
is live at ``https://pypi.org/project/epcsaft/``, install with:

.. code-block:: powershell

   python -m pip install epcsaft

With ``uv``:

.. code-block:: powershell

   uv add epcsaft

If PyPI returns 404 for ``epcsaft``, use the GitHub release wheel instead.

Install from tagged source
--------------------------

The ``v0.2.0`` tag supports source installs that build the native extension
locally:

.. code-block:: powershell

   python -m pip install "epcsaft @ git+https://github.com/ePC-SAFT/ePC-SAFT.git@v0.2.0#subdirectory=packages/epcsaft"

With ``uv``:

.. code-block:: powershell

   uv add "epcsaft @ git+https://github.com/ePC-SAFT/ePC-SAFT.git@v0.2.0#subdirectory=packages/epcsaft"

Source builds require:

- Python ``>=3.9``.
- A C++ compiler for your platform.
- CMake.
- Ninja or another working CMake generator.
- Network access to download build requirements declared in ``pyproject.toml``.

Python 3.13 is the current project smoke-test baseline.

Install from a local source archive
-----------------------------------

Download the release source archive, extract it, then run:

.. code-block:: powershell

   cd C:\path\to\ePC-SAFT-0.2.0
   python -m pip install packages/epcsaft

Editable source install
-----------------------

Use an editable install when you are changing Python files and want imports to
come directly from the checkout:

.. code-block:: powershell

   git clone https://github.com/ePC-SAFT/ePC-SAFT.git
   cd ePC-SAFT
   python -m pip install -e packages/epcsaft

With ``uv``:

.. code-block:: powershell

   uv pip install -e packages/epcsaft

Editable installs use the same native build backend as wheel installs. Python
source changes are picked up from the checkout. If you change C++ sources,
pybind bindings, CMake files, or build metadata, rerun the editable install
command so the native extension is rebuilt.

Equilibrium and regression workflows live in monorepo workspace packages under
``packages/``. Their local distribution artifacts can be built and installed
from ``dist/`` alongside the provider artifact before PyPI publication:

.. code-block:: powershell

   uv run python scripts/dev/build_dist.py --parallel 1
   uv run python scripts/dev/build_extension_dists.py --mode monorepo --parallel 1 --ipopt-root "$env:USERPROFILE\Documents\deps\ipopt-msvc"
   uv run python scripts/dev/build_extension_dists.py --mode installed-provider --parallel 1 --ipopt-root "$env:USERPROFILE\Documents\deps\ipopt-msvc"
   uv run python scripts/dev/check_release_installs.py --dist-dir dist

The release install proof covers these package combinations from local
artifacts:

.. code-block:: powershell

   python -m pip install epcsaft
   python -m pip install epcsaft epcsaft-equilibrium
   python -m pip install epcsaft epcsaft-regression
   python -m pip install epcsaft epcsaft-equilibrium epcsaft-regression

The commands above describe the release target. Until the extension packages
are published, use the local ``dist/`` proof or the monorepo uv workspace.
Production equilibrium extension artifacts require a real Ipopt SDK; no-Ipopt
builds are not production equilibrium package evidence.

Local path dependency
---------------------

For a project that depends on a local checkout, use a path dependency:

.. code-block:: toml

   dependencies = [
       "epcsaft @ file:///C:/path/to/ePC-SAFT",
   ]

After package changes, refresh the installed dependency:

.. code-block:: powershell

   uv sync --reinstall-package epcsaft

Use ``uv run --no-sync ...`` for follow-up downstream commands when you do not
want an implicit sync to rebuild the package again.

Native IPOPT SDK support
------------------------

IPOPT support is a native build dependency for constrained-NLP equilibrium
routes in the current transition build, not a Python extra. Long term, Ipopt
belongs to the ``epcsaft-equilibrium`` extension package. On Windows, the
supported default SDK probes are
``%LOCALAPPDATA%\ePC-SAFT\deps\ipopt-msvc``,
``%USERPROFILE%\.epcsaft\deps\ipopt-msvc``, and the legacy
``%USERPROFILE%\Documents\deps\ipopt-msvc`` path. Explicit
``EPCSAFT_IPOPT_ROOT`` / ``EPCSAFT_PEP517_IPOPT_ROOT`` values take precedence
and are preferred for reproducible release proof. Source and editable installs
use a discovered SDK automatically when the directory exists; otherwise point
the build backend at an Ipopt install root explicitly:

.. code-block:: powershell

   $env:EPCSAFT_PEP517_IPOPT_ROOT = "$env:USERPROFILE\Documents\deps\ipopt-msvc"
   python -m pip install "epcsaft @ git+https://github.com/ePC-SAFT/ePC-SAFT.git@v0.2.0"

Use ``EPCSAFT_PEP517_IPOPT_DIR`` instead when the install provides an
``IpoptConfig.cmake`` directory.
Runtime processes that execute Ipopt on Windows must expose the SDK ``bin``
directory through both ``PATH`` and ``EPCSAFT_RUNTIME_DLL_DIRS``; repo build
scripts do this automatically for the local SDK.

``epcsaft-equilibrium`` wheels must package only the audited runtime dependency
closure for ``epcsaft_equilibrium._native_core`` and Ipopt. The package CMake
install step uses runtime dependency inspection and does not blindly copy every
DLL in the SDK ``bin`` directory. Large build-time source trees such as Ceres
``FetchContent`` checkouts are not release payload; use
``scripts/dev/build_system_ceres.py`` or ``EPCSAFT_PEP517_CERES_DIR`` to reuse
the local Ceres package for repeated regression extension builds.

When Ipopt is compiled, import ``Equilibrium`` from ``epcsaft_equilibrium`` and
use the certified route specs and ordinary solver tolerances for native
constrained-NLP behavior. The public equilibrium API does not expose a
solver-backend selector or claim unvalidated Ipopt coverage.

Verify the install
------------------

.. code-block:: python

   import epcsaft
   import epcsaft_equilibrium

   print(epcsaft.__version__)
   print(epcsaft.runtime_build_info())
   print(epcsaft.capabilities())
   print(epcsaft_equilibrium.capabilities())

If import fails after a source build on Windows, make sure no Python process is
holding an old ``epcsaft._core`` extension open and reinstall from a clean
environment.
