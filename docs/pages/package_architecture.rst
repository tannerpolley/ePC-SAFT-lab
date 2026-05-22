Package Architecture
====================

``epcsaft`` is a package repo. The Python layer owns input validation,
user-facing objects, diagnostics, documentation examples, and workflow
orchestration. The equation-of-state runtime and package-owned phase,
chemical-equilibrium, and regression kernels are native C++ exposed through
``pybind11``.

Organization Boundary
---------------------

``epcsaft`` remains one installable distribution package. The project uses
clean internal subsystem boundaries instead of splitting EOS, equilibrium,
regression, native, data, or benchmark code into separate packages.

The target internal shape is:

.. code-block:: text

   src/epcsaft/
     frontend/
     model/
     state/
     equilibrium/
     regression/
     runtime/
     native/

Subsystem Boundaries
--------------------

EOS harness
   Owns the reset ``Mixture`` and ``State`` frontend. ``Mixture`` establishes
   components, parameters, and model options; ``State`` owns temperature,
   pressure or density closure, composition, and phase. It validates user inputs
   and delegates thermodynamic calculations to the native runtime.

Equilibrium
   Owns phase-equilibrium, stability, bubble/dew, electrolyte LLE, and
   chemical-equilibrium orchestration. It may use Python for problem objects,
   request normalization, result shaping, and diagnostics, but production
   thermodynamic evaluations should route through the EOS/native boundary.
   The public reset frontend is reached through direct
   ``Equilibrium(mixture, ...)`` workflow objects. Legacy string facades and
   typed problem objects are internal transition surfaces until they are ported
   behind reset methods.

Regression
   Owns fitting problem definitions, records, provenance validation, objective
   assembly, derivative diagnostics, and fit-result serialization. Public
   regression workflows are reached through ``Regression(mixture, ...)``,
   while expensive objective and derivative work uses native kernels.

Native
   Owns C++ kernels, pybind11 bindings, native capability reporting, and
   internal C++ helpers. Python code should call native functionality through
   the public runtime surfaces or thin package-owned adapters, not by reaching
   into build artifacts directly.

Data
   Owns packaged parameter datasets, dataset validation, reference-data loading
   contracts, and reusable package data. Analysis-local inputs belong under the
   relevant ``analyses/<category>/<id>/figures/<figure_id>/input`` tree instead of becoming hidden package
   dependencies.

Benchmarks
   Owns package-maintained timing, smoke, and regression benchmarks that protect
   runtime expectations. The previous local benchmark entrypoints were removed
   as obsolete, so new performance or literature-coverage claims must add a
   current owned benchmark or analysis workflow before being cited. Benchmark
   execution may consume the public package API and packaged/reference data, but
   should not become a runtime package import dependency for normal users.

Core Surfaces
-------------

Use these imports for new code:

* ``from epcsaft import Mixture, State, Equilibrium, Regression`` for workflow
  construction.
* ``from epcsaft import ParameterSet, ModelOptions`` for parameter data and
  model formulation choices.
* ``from epcsaft import create_input_template`` for reset input scaffolds.
* current explicit benchmark or analysis workflows for package-owned timing and smoke claims.
* ``epcsaft.capabilities()`` and ``epcsaft.runtime_build_info()`` for runtime
  capability metadata.

Benchmark execution helpers are validation assets, not runtime thermodynamic
APIs; keep them outside the runtime package.

Import Policy
-------------

Public user code should import from the top-level package or from documented
subsystem modules:

* ``import epcsaft``
* ``from epcsaft import Mixture, ParameterSet, ModelOptions``
* ``from epcsaft import Equilibrium, Regression``

Internal modules may share package-owned helpers when that keeps behavior
centralized, but subsystem code should avoid circular ownership. In particular,
benchmarks and docs may depend on public APIs, while core runtime modules must
not depend on benchmark entrypoints or generated analysis artifacts.

Compatibility Policy
--------------------

The hard reset intentionally cuts off legacy root imports:

.. code-block:: python

   import epcsaft

   epcsaft.Mixture
   epcsaft.ParameterSet
   epcsaft.ModelOptions

Legacy runtime classes may remain in internal bridge modules while the native
routes are ported, but they are not top-level public imports.

Optional Dependency Policy
--------------------------

The default install should keep the lightweight runtime usable. Heavy or
platform-sensitive dependencies belong behind optional dependency groups,
feature flags, or runtime capability checks. For example, Ipopt-dependent
workflows must fail with actionable diagnostics when native Ipopt is not
compiled or a route is outside the compiled native adapter surface, instead of
making the base package import fail.

Native build capabilities should be reported through ``capabilities()`` and
``runtime_build_info()`` so downstream projects can select supported workflows
without probing private modules.

Repository Layout
-----------------

``src/epcsaft`` contains the package. ``tests`` contains package/API/native
contracts. ``data/reference`` is the canonical source-checkout reference-data
library. ``analyses`` contains paper-validation and analysis workflows, each
with local ``data`` and ``results`` folders.

Generated benchmark output, run payloads, build trees, and local graph or temp
outputs are not source artifacts.

Native-First Policy
-------------------

Package-owned regression, equilibrium, and speciation workflows must use native
runtime kernels for thermodynamic calculations. Python may batch rows, validate
inputs, and report diagnostics, but it should not
silently become the production thermodynamic solver.
