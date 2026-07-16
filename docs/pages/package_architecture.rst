Archived Monorepo Architecture
==============================

This page describes the runnable personal-lab checkout. It is not the target
topology or authority for clean production repositories.

The lab contains three workspace distributions:

.. code-block:: text

   packages/epcsaft              # provider EOS/state/property package
   packages/epcsaft-equilibrium  # equilibrium extension
   packages/epcsaft-regression   # regression extension

The Python layers own public objects, validation, request/result shaping, and
diagnostics. Native C++ exposed through ``pybind11`` owns the retained
thermodynamic and solver kernels. The monorepo remains the sole transitional
runtime authority until each named slice is accepted in its clean owner.

Archive Boundary
----------------

The lab preserves source, tests, papers, equation catalogues, validation data,
and rejected or deferred work. It does not own clean-package publication,
live roadmap state, or future production authority.

Clean repositories must not depend on this checkout, the migration repository,
or sibling source paths. Their only intended production dependency directions
are:

.. code-block:: text

   epcsaft-equilibrium  --> installed epcsaft provider artifact
   epcsaft-regression   --> installed epcsaft provider artifact
   validation           --> installed admitted artifacts

No directory, old test suite, compatibility layer, or native kernel moves as a
unit. A promotion manifest selects the minimum call graph and independent
evidence for one capability.

Retained Package Boundaries
---------------------------

Provider
   ``packages/epcsaft`` contains input resolution, model/state objects,
   EOS/property evaluation, native bindings, capability reporting, and
   provider-owned tests.

Equilibrium
   ``packages/epcsaft-equilibrium`` contains pressure-boundary and saturation
   routes plus broader internal/experimental equilibrium work. Public exposure
   is narrower than the source tree; consult executable capability metadata and
   accepted evidence.

Regression
   ``packages/epcsaft-regression`` contains fitting contracts, native Ceres
   paths, diagnostics, and characterization tests. Presence in the lab is not
   production admission.

Evidence
   ``analyses``, ``data/reference``, ``docs/latex``, and ``docs/papers`` retain
   broad scientific and validation evidence. Production packages do not import
   these trees at runtime.

Local Archive Imports
---------------------

These imports describe the retained monorepo surface only:

.. code-block:: python

   import epcsaft
   from epcsaft import Mixture, ModelOptions, ParameterSet, State
   from epcsaft_equilibrium import Equilibrium
   from epcsaft_regression import Regression

Use ``capabilities()`` and ``runtime_build_info()`` to inspect the compiled lab
artifact. Do not infer a clean-package capability from an import succeeding.

Native Provider Transport
-------------------------

The retained ``provider_native_sdk_v1`` source/CMake material is
pre-extraction experimental evidence needed by this monorepo's extension build
tests. It is not the approved transport for clean repositories and must not be
copied or compiled into another owner without a dedicated transport decision
and isolated proof against duplicate EOS ownership. The private
``epcsaft._core`` module is not a stable public ABI.

Compatibility And Optional Dependencies
---------------------------------------

Do not add compatibility shims, mutable legacy payloads, alternate public
derivative backends, or fake scientific defaults to keep old call sites alive.
Heavy dependencies remain capability-scoped: Ipopt belongs with equilibrium
and Ceres with regression. The provider package must not import extension
packages by default.

Repository Layout
-----------------

Provider tests live under ``packages/epcsaft/tests``. Equilibrium and
regression tests live under their package directories. Root ``tests`` retains
monorepo build, workflow, documentation, integration, and cross-package
contracts. Generated builds, caches, run payloads, and temporary output are not
source artifacts.

Migration Rule
--------------

A clean slice freezes its equations, source records, units, domain, inputs,
outputs, derivative orders, failure boundaries, and independent oracles before
implementation. It is built in isolation, proves excluded legacy seams are
absent, and moves runtime authority only through an accepted promotion receipt.
