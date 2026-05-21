Installation
============

Current package version: ``0.2.0``

Install from a wheel
--------------------

The ``v0.2.0`` GitHub release provides a Windows CPython 3.13 wheel and source
archive:

``https://github.com/tannerpolley/ePC-SAFT/releases/tag/v0.2.0``

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

   python -m pip install "epcsaft @ git+https://github.com/tannerpolley/ePC-SAFT.git@v0.2.0"

With ``uv``:

.. code-block:: powershell

   uv add "epcsaft @ git+https://github.com/tannerpolley/ePC-SAFT.git@v0.2.0"

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
   python -m pip install .

Editable source install
-----------------------

Use an editable install when you are changing Python files and want imports to
come directly from the checkout:

.. code-block:: powershell

   git clone https://github.com/tannerpolley/ePC-SAFT.git
   cd ePC-SAFT
   python -m pip install -e .

With ``uv``:

.. code-block:: powershell

   uv pip install -e .

Editable installs use the same native build backend as wheel installs. Python
source changes are picked up from the checkout. If you change C++ sources,
pybind bindings, CMake files, or build metadata, rerun the editable install
command so the native extension is rebuilt.

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

IPOPT support is a native build dependency, not a Python extra. On Windows, the
preferred local dependency is the SDK root at
``%USERPROFILE%\Documents\deps\ipopt-msvc``. Source and editable installs use
that SDK automatically when the directory exists; otherwise point the build
backend at an Ipopt install root explicitly:

.. code-block:: powershell

   $env:EPCSAFT_PEP517_IPOPT_ROOT = "$env:USERPROFILE\Documents\deps\ipopt-msvc"
   python -m pip install "epcsaft @ git+https://github.com/tannerpolley/ePC-SAFT.git@v0.2.0"

Use ``EPCSAFT_PEP517_IPOPT_DIR`` instead when the install provides an
``IpoptConfig.cmake`` directory.
Runtime processes that execute Ipopt on Windows must expose the SDK ``bin``
directory through both ``PATH`` and ``EPCSAFT_RUNTIME_DLL_DIRS``; repo build
scripts do this automatically for the local SDK.

When Ipopt is compiled, use explicit Ipopt-backed routes or solver options for
native constrained-NLP behavior. The automatic backend selector does not claim
unvalidated Ipopt coverage.

Verify the install
------------------

.. code-block:: python

   import epcsaft

   print(epcsaft.__version__)
   print(epcsaft.runtime_build_info())
   print(epcsaft.capabilities())

If import fails after a source build on Windows, make sure no Python process is
holding an old ``epcsaft._core`` extension open and reinstall from a clean
environment.
