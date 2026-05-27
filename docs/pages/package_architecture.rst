Package Architecture
====================

``epcsaft`` is the current source repository and the long-term core
thermodynamic provider package. The Python layer owns input validation,
user-facing provider objects, diagnostics, documentation examples, and workflow
orchestration. The equation-of-state runtime is native C++ exposed through
``pybind11``.

During the monorepo transition, this distribution still exposes equilibrium and
regression workflow objects. ADR 0005 makes those transition surfaces: final
ownership moves Ipopt-backed equilibrium to ``epcsaft-equilibrium`` and
Ceres-backed regression to ``epcsaft-regression`` after the provider and native
extension boundaries are proven.

Organization Boundary
---------------------

``epcsaft`` currently ships as a single distribution package while the
split is prepared. That is a transition-state implementation detail, not the
long-term package ownership model. The target organization layout is:

.. code-block:: text

   ePC-SAFT/ePC-SAFT              # core provider package: epcsaft
   ePC-SAFT/epcsaft-equilibrium   # Ipopt-backed equilibrium extension
   ePC-SAFT/epcsaft-regression    # Ceres-backed regression extension

The current repo must keep clean internal subsystem boundaries so the extension
packages can be extracted without hidden compatibility paths.

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
   In the current monorepo, owns phase-equilibrium, stability, bubble/dew,
   electrolyte LLE, and chemical-equilibrium orchestration. Long term, this
   subsystem belongs to ``epcsaft-equilibrium``. It may use Python for problem
   objects, request normalization, result shaping, and diagnostics, but
   production thermodynamic evaluations should route through the core
   provider/native boundary. The current public reset frontend is reached
   through direct
   ``Equilibrium(mixture, ...)`` workflow objects. Legacy string facades and
   typed problem objects are internal transition surfaces until they are ported
   behind reset methods.

Regression
   In the current monorepo, owns fitting problem definitions, records,
   provenance validation, objective assembly, derivative diagnostics, and
   fit-result serialization. Long term, this subsystem belongs to
   ``epcsaft-regression``. Public regression workflows are currently reached
   through ``Regression(mixture, ...)``, while expensive objective and
   derivative work uses native kernels.

Native
   Owns C++ kernels, pybind11 bindings, native capability reporting, and
   internal C++ helpers. Python code should call native functionality through
   the public runtime surfaces or thin package-owned adapters, not by reaching
   into build artifacts directly.

Data
   Owns packaged parameter datasets, dataset validation, reference-data loading
   contracts, and reusable package data. Analysis-local inputs belong under the
   relevant analysis ``source`` or ``parameters`` tree instead of becoming
   hidden package dependencies.

Benchmarks
   Owns package-maintained timing, smoke, and regression benchmarks that protect
   runtime expectations. The previous local benchmark entrypoints were removed
   as obsolete, so new performance or literature-coverage claims must add a
   current owned benchmark or analysis workflow before being cited. Benchmark
   execution may consume the public package API and packaged/reference data, but
   should not become a runtime package import dependency for normal users.

Core Surfaces
-------------

Use these imports for current monorepo code:

* ``from epcsaft import Mixture, State`` for core provider workflow
  construction.
* ``from epcsaft import Equilibrium, Regression`` for transition equilibrium
  and regression workflow construction until the extension packages own those
  imports.
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

Current public user code should import from the top-level package or from
documented subsystem modules:

* ``import epcsaft``
* ``from epcsaft import Mixture, ParameterSet, ModelOptions``
* ``from epcsaft import Equilibrium, Regression`` during the transition release
  series

Internal modules may share package-owned helpers when that keeps behavior
centralized, but subsystem code should avoid circular ownership. In particular,
benchmarks and docs may depend on public APIs, while core runtime modules must
not depend on benchmark entrypoints or generated analysis artifacts.

After the split, extension packages import the core provider contract instead
of reaching into private core modules. Core must not import extension packages
by default.

Compatibility Policy
--------------------

The hard reset intentionally cuts off legacy root imports:

.. code-block:: python

   import epcsaft

   epcsaft.Mixture
   epcsaft.ParameterSet
   epcsaft.ModelOptions

Internal bridge modules may exist only as actively owned implementation seams
for current transition work. They are not top-level public imports, and they
must be deleted when the old path is migrated.

Optional Dependency Policy
--------------------------

The default provider install should keep the lightweight runtime usable. Heavy
or platform-sensitive dependencies belong to the capability that needs them:
Ceres to regression and Ipopt to equilibrium. During the monorepo transition,
source-checkout builds may still compile all current native capabilities by
default, but that must not be described as final core dependency ownership.

Ipopt-dependent workflows must fail with actionable diagnostics when native
Ipopt is not compiled or a route is outside the compiled native adapter
surface, instead of making the base package import fail.

Native build capabilities should be reported through ``capabilities()`` and
``runtime_build_info()`` so downstream projects can select supported workflows
without probing private modules.

Repository Layout
-----------------

``src/epcsaft`` contains the package. ``tests`` contains package/API/native
contracts. ``data/reference`` is the canonical source-checkout reference-data
library. ``analyses`` contains paper-validation and analysis workflows with
analysis-owned ``parameters``, ``figures/<figure_id>/source``,
``figures/<figure_id>/results``, ``tables``, and ``shared`` artifacts.

Generated benchmark output, run payloads, build trees, and local graph or temp
outputs are not source artifacts.

Native-First Policy
-------------------

Package-owned regression, equilibrium, and speciation workflows must use native
runtime kernels for thermodynamic calculations. Python may batch rows, validate
inputs, and report diagnostics, but it should not
silently become the production thermodynamic solver.
