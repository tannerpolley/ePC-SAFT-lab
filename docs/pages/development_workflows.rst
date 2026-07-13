Development Workflow Guide
==========================

This is the operational guide for maintainers working from this source tree. Use these commands before inventing new build, test, or package workflows.

The build/package dependency authority is :doc:`../protocols/build_package_dependency_protocol`. Update that protocol in the same change as any build, package, dependency, CMake, C++ package-management, or CI-lane behavior change.

Default source-checkout sequence
--------------------------------

Start every fresh source checkout with this sequence:

.. code-block:: bash

   scripts/dev/check_linux_prereqs.sh --check
   uv sync --no-install-workspace
   uv run --no-sync python scripts/dev/bootstrap.py

The bootstrap entrypoint runs the current setup sequence and prints the next
exact validation command:

.. code-block:: bash

   uv sync --no-install-workspace
   uv run --no-sync python scripts/dev/build_epcsaft.py
   uv run --no-sync python scripts/dev/doctor.py --require-provider-sdk --require-extension-native
   uv run --no-sync python scripts/dev/validate_project.py quick

This is the expected healthy full-native baseline. It creates the uv
environment, builds the in-place pybind11 ``epcsaft._core`` extension plus the
extension-owned native modules, verifies imports/tool paths and generated-output
state through doctor, then runs the fast contract suite. The default test route
intentionally samples representative API, native, regression, equilibrium
metadata, and workflow contracts instead of running full equilibrium route
sweeps, regression reproductions, or generated plot production. Use ``uv run
python scripts/dev/validate_project.py confidence`` before release or broad
runtime claims when extra native runtime contracts should be included.
The current development and CI smoke baseline is Python 3.13, while ``pyproject.toml`` still declares package compatibility with Python ``>=3.9``.

Use ``uv run python run_pytest.py ...`` for repo validation. Direct ``uv run python -m pytest ...`` also works, but the wrapper uses a per-run pytest temp directory that is safer for parallel local runs. Bare root collection and ``run_pytest.py --all`` collect the same ordered test nodes from ``tests`` and the three package-owned test roots. Pytest uses importlib import mode so repeated test-module basenames remain package-local. Analysis tests under ``analyses/`` are deliberately outside that default collection universe and run only when explicitly targeted by their owning workflow.

For a checkout copied from Windows, inspect ignored native/cache artifacts with
``scripts/dev/clean_transferred_artifacts.sh --dry-run`` before deleting them
with ``--apply``. The cleanup helper removes only Git-ignored paths.

PR gate policy
--------------

Ordinary early package-development PRs use local proof first. The default merge
policy is risk-based focused validation in the PR body, not waiting for every
Ceres, Ipopt, package, wheel, release, or installed-provider lane to run in
GitHub Actions. As of 2026-05-29, branch protection has no required status
checks or required reviews.

Only the lightweight local-development smoke workflow runs automatically on
``pull_request``. Heavy native/profile builds, package build lanes, full wheel
matrices, publish workflows, and installed-provider extension proofs are
manual-only workflows. They remain required before a PR claims release
readiness, capability support, or production native behavior. Ordinary PRs do
not need boilerplate notes for skipped heavy lanes.

Command matrix
--------------

.. list-table::
   :header-rows: 1
   :widths: 28 42 30

   * - Situation
     - Command
     - Use when
   * - First setup or uncertain state
     - ``uv sync --no-install-workspace`` then ``uv run --no-sync python scripts/dev/bootstrap.py``
     - Starting a fresh thread, after dependency changes, or after a failed import. The command runs sync, native build, doctor, and prints the next exact command.
   * - Handoff validation
     - ``uv run python scripts/dev/validate_project.py confidence``
     - Before claiming repo runtime confidence. This includes doctor and the confidence slice.
   * - Fast generic validation
     - ``uv run python scripts/dev/validate_project.py quick``
     - Quick checks across provider API, transition regression API, equilibrium capability metadata, cheap native metadata, and package-boundary contracts.
   * - Provider API work
     - ``uv run python run_pytest.py --provider-api -q`` or ``uv run python scripts/dev/validate_project.py provider``
     - Core provider package imports, state, mixture, parameter-template, and root export checks. This slice must not import ``epcsaft_equilibrium``.
   * - Provider-only boundary proof
     - ``uv run python scripts/dev/build_epcsaft.py --clean --profile provider`` then ``uv run python run_pytest.py packages/epcsaft/tests/native/contracts/test_provider_only_core_symbols.py -q``
     - Prove provider ``_core`` builds without Ceres and Ipopt and does not export equilibrium/regression native symbols.
   * - Provider Codex worktree lane
     - ``uv sync --no-install-workspace`` then ``uv run --no-sync python scripts/dev/bootstrap.py --step provider-native`` or Codex action ``Provider Native``
     - Build the provider-only native profile and require provider SDK plus provider ``_core``.
   * - Equilibrium Codex worktree lane
     - ``uv sync --no-install-workspace`` then ``uv run --no-sync python scripts/dev/bootstrap.py --step equilibrium-native`` or Codex action ``Equilibrium Native``
     - Build the equilibrium native profile and require ``epcsaft_equilibrium._native_core`` without building regression native code.
   * - Regression Codex worktree lane
     - ``uv sync --no-install-workspace`` then ``uv run --no-sync python scripts/dev/bootstrap.py --step regression-native`` or Codex action ``Regression Native``
     - Build the regression native profile with the reusable Ceres package and require ``epcsaft_regression._native_core`` without building equilibrium native code.
   * - Full native Codex worktree lane
     - ``uv sync --no-install-workspace`` then ``uv run --no-sync python scripts/dev/bootstrap.py --step full-native`` or Codex action ``Full Native``
     - Build the transition source-checkout native profile and require both extension-owned native modules.
   * - Equilibrium extension contracts
     - ``uv run python run_pytest.py --equilibrium-api -q``
     - Package-owned metadata/API check under ``packages/epcsaft-equilibrium/tests`` for neutral equilibrium route construction, solver-option validation, derivative-backend contracts, and capability reporting. This slice does not run the full route-solve file.
   * - Standalone CE internal validation gate
     - ``uv run --no-sync python scripts/validation/check_standalone_ce_gate.py --json --require-single-nlp-path --require-oracles --require-complete`` then ``uv run --no-sync python run_pytest.py packages/epcsaft-equilibrium/tests/contracts/test_activation_capabilities.py tests/native/contracts/test_standalone_ce_gate.py -q``
     - Active repair gate for the closed reactive-speciation family. It must pass before a separate re-admission change can add any public route; it does not admit reactive LLE, reactive electrolyte LLE, or CPE.
   * - Regression extension tests
     - ``uv run python run_pytest.py --regression -q`` or ``uv run python scripts/dev/validate_project.py regression``
     - Regression-extension Ceres tests routed through ``epcsaft_regression``.
   * - Package integration checks
     - ``uv run python run_pytest.py --integration -q`` or ``uv run python scripts/dev/validate_project.py integration``
     - Cross-package workspace, provider/extension capability, and ownership-boundary checks.
   * - Native or density/equation work
     - ``uv run python scripts/dev/build_epcsaft.py --build-only --parallel 10`` then ``uv run python run_pytest.py --runtime -q``
     - C++ iteration after ``build/dev`` is already configured.
   * - Native contract only
     - ``uv run python run_pytest.py --native -q``
     - Fast check for pressure-vs-density and contribution-map contracts.
   * - Native route metadata/result contracts
     - ``uv run python run_pytest.py --native-contracts -q``
     - Fast check for native route ``variable_model``, ``density_backend``, residual-family payloads, and Python route diagnostics. Equilibrium native contract tests now live under ``packages/epcsaft-equilibrium/tests/native``; use this instead of the full route-builder suite for architecture or metadata edits.
   * - Equilibrium route confidence
     - ``uv run python run_pytest.py --equilibrium-confidence -q -s`` or ``uv run python scripts/dev/validate_project.py equilibrium-confidence``
     - One focused convergence target per selector-admitted equilibrium family. Full route sweeps, bubble/dew ladders, paper validation, and feed-line validation remain explicit benchmark or analysis workflows, not default pytest validation.
   * - Equilibrium debug trace
     - ``uv run python run_pytest.py --equilibrium-debug -q -s <one equilibrium test node>``
     - Opt-in verbose Ipopt print level, continuous-TPD trace output, and expanded iteration-history capture for diagnosing iteration-limit, TPD candidate, or seed-attempt behavior. Debug mode requires one explicit equilibrium test node; it cannot run a slice.
   * - Phase-discovery check
     - ``uv run python scripts/validation/check_phase_discovery.py --json``
     - Cheap phase-discovery snapshot for deterministic screening, continuous TPD, HELD Stage I, and Stage II candidate bound-gap diagnostics. Add ``--include-route-refinement`` only when current-route Ipopt refinement is needed; add ``--debug --include-route-refinement --require-complete`` to print continuous-TPD rows, route seed-attempt markers, Ipopt ``print_level=5`` output, and bounded Ipopt iteration history for this one route while failing on incomplete convergence.
   * - Receipt-backed HELD/GFPE proof
     - ``uv run --no-sync python scripts/dev/build_epcsaft.py --profile equilibrium --build-only --parallel 4`` then ``uv run --no-sync python scripts/validation/check_phase_discovery.py --json --include-route-refinement --require-complete`` and ``uv run --no-sync python scripts/validation/check_neutral_tp_flash_fixture.py --generate-phase-discovery --json --require-complete``
     - Use before treating HELD Stage II/III rows, neutral TP-flash fixture status, or M4 milestone figures as completion evidence. Both checker payloads must include ``native_freshness_receipt`` with the git commit, imported native module path, checker command, and equilibrium native build-refresh command. Closed PRs or issues do not replace this local receipt.
   * - Docs check
     - ``uv run python scripts/dev/validate_project.py docs``
     - Build Sphinx HTML under ``build/docs-html``.
   * - Retired local benchmark scripts
     - No retained command.
     - The previous local benchmark scripts were removed as obsolete; current performance or literature-coverage claims need a newly owned benchmark or analysis workflow before being cited.
   * - Package boundary
     - ``uv run python scripts/dev/build_dist.py``
     - Wheel/sdist and smoke-import validation. The default release baseline disables local Ipopt so wheels do not require user-local Ipopt shared libraries. Isolated package builds default to serial native compilation for reproducible package proofs; use ``--parallel N`` only when the machine has enough headroom.
   * - Release install proof
     - ``uv run python scripts/dev/check_release_installs.py --dist-dir dist``
     - Local built-artifact install proof for ``epcsaft``, ``epcsaft-equilibrium``, ``epcsaft-regression``, and the combined install set. Run after provider and extension dist builds.
   * - Installed/source diagnostic
     - ``uv run python -m epcsaft``
     - Confirm package and ``epcsaft._core`` paths.

Build rules
-----------

The canonical local native build command is:

.. code-block:: bash

   uv run --no-sync python scripts/dev/build_epcsaft.py

That command uses ``--profile fast`` by default: Ceres and CppAD are enabled,
and Ipopt is enabled when a native install is available. On Linux, the script
first honors explicit ``EPCSAFT_IPOPT_ROOT`` /
``EPCSAFT_PEP517_IPOPT_ROOT`` values and otherwise probes default install roots
such as ``~/.local/opt/ipopt``, ``/usr/local``, ``/usr``, and
``/opt/ipopt``. ``bootstrap.py`` and ``doctor.py`` report the active Ipopt root,
its source, all default probe paths, and the exact ``export`` assignment to
change it. In this transition
checkout, Ceres is enabled by default for native regression builds, CppAD is
required for derivative-capable provider builds, and Ipopt-enabled equilibrium
routes require an Ipopt-enabled native build. ADR 0005 assigns final Ceres
ownership to ``epcsaft-regression`` and final Ipopt ownership to
``epcsaft-equilibrium``. Explicit package-boundary proof lanes may disable
Ceres or Ipopt to prove the future provider and extension dependency split.

The provider-only boundary proof uses:

.. code-block:: bash

   uv run --no-sync python scripts/dev/build_epcsaft.py --clean --profile provider

That profile keeps CppAD ON while disabling Ceres, Ipopt, and the transition
equilibrium/regression native registration surfaces.

The package-specific source-checkout profiles are:

.. code-block:: bash

   uv run python scripts/dev/build_epcsaft.py --profile equilibrium
   uv run python scripts/dev/build_epcsaft.py --profile regression

The ``equilibrium`` profile builds provider ``_core`` plus
``epcsaft_equilibrium._native_core`` with Ipopt enabled and Ceres/regression
disabled. The ``regression`` profile builds provider ``_core`` plus
``epcsaft_regression._native_core`` with Ceres enabled and Ipopt/equilibrium
disabled. The Codex app setup actions route through ``scripts/dev/bootstrap.py``
so each package lane also runs the matching Doctor requirement.

Root ``CMAKE.md`` is the source of truth for direct CMake preset operations. Direct CMake preset operations must use ``scripts/dev/cmake_preset.sh``. Do not call raw ``cmake --preset`` or ``cmake --build`` from ad hoc shells for this repo. The wrapper uses ``.venv/bin/python -m cmake``, ``.venv/bin/ninja``, pins ``CMAKE_MAKE_PROGRAM`` for ``dev-native``, and refuses to run while ``build/dev/.ninja_lock`` exists.

Provider wheel/editable/path installs go through the package-local
PEP 517/scikit-build backend in ``packages/epcsaft``. That backend builds the
provider-only distribution: CppAD ON, Ceres OFF, Ipopt OFF, and extension-owned
native modules OFF. Source-checkout native builds still use
``scripts/dev/build_epcsaft.py`` when equilibrium/regression extension modules,
Ceres, or Ipopt are needed.

Extension package wheel/sdist proof goes through package-local scikit-build
metadata in ``packages/epcsaft-equilibrium`` and
``packages/epcsaft-regression``. Use the repository helper so both the monorepo
provider SDK and installed-provider SDK paths are exercised:

.. code-block:: bash

   uv run python scripts/dev/build_dist.py --parallel 1
   uv run python scripts/dev/build_extension_dists.py --mode monorepo --parallel 1
   uv run python scripts/dev/build_extension_dists.py --mode installed-provider --parallel 1

The extension helper fails if the provider SDK CMake metadata is missing.
Equilibrium package builds require a real Ipopt SDK; regression package builds
require Ceres through the package-local CMake configuration. The helper uses
the shared Linux Ipopt discovery policy by default; set
``EPCSAFT_IPOPT_ROOT=/path/to/ipopt`` to pin a specific audited install. The
helper accepts ``--ceres-dir`` or ``EPCSAFT_PEP517_CERES_DIR`` and otherwise auto-detects the
repo-local reusable Ceres package built by
``uv run python scripts/dev/build_system_ceres.py``. If that cache is missing,
only the regression package build uses Ceres ``FetchContent``; this is
build-time dependency work, not runtime wheel payload.

After building provider and extension distributions, prove the install matrix
from local artifacts without PyPI:

.. code-block:: bash

   uv run python scripts/dev/check_release_installs.py --dist-dir dist

That helper installs from ``dist/`` with ``--no-index --find-links`` and smoke
imports the requested provider and extension native modules. It does not publish
to PyPI.

.. list-table::
   :header-rows: 1
   :widths: 16 22 22 40

   * - Profile
     - Native options
     - Default Linux parallelism
     - Use when
   * - ``fast``
     - Ceres ON, CppAD ON, Ipopt ON when available, extension-owned native modules ON
     - ``4``
     - Normal source-checkout setup, C++ iteration, and most validation.
   * - ``full``
     - Ceres ON, CppAD ON, Ipopt ON when available, extension-owned native modules ON
     - ``4``
     - Alias for the required Ceres + CppAD dependency profile.
   * - ``ipopt``
     - Ceres ON, CppAD ON, Ipopt ON, extension-owned native modules ON
     - ``4``
     - Native Ipopt adapter development or validation with the local SDK or another native Ipopt package.
   * - ``equilibrium``
     - Ceres OFF, CppAD ON, Ipopt ON, equilibrium native module ON, regression native module OFF
     - ``1``
     - Equilibrium package-native worktree lane.
   * - ``regression``
     - Ceres ON, CppAD ON, Ipopt OFF, regression native module ON, equilibrium native module OFF
     - ``1``
     - Regression package-native worktree lane.
   * - ``provider``
     - Ceres OFF, CppAD ON, Ipopt OFF, extension-owned native modules OFF
     - ``1``
     - Provider-only boundary proof for the future core package.

Use ``--build-only --parallel 10`` only after the CMake tree already exists. ``--build-only`` does not reconfigure profile flags; it builds whatever ``build/dev/CMakeCache.txt`` already says. Use ``--configure-only`` when you need to refresh CMake configuration without compiling. For a new ``build/dev`` tree, ``scripts/dev/build_epcsaft.py`` inherits the current Linux shell compiler environment and requires the uv-managed ``.venv/bin/cmake`` and ``.venv/bin/ninja`` tools. Existing non-Ninja CMake trees must be migrated once with ``uv run python scripts/dev/build_epcsaft.py --clean --generator ninja``; missing repo-local tools fail loudly instead of falling back to host executables.

Every native build writes ``build/dev/build_epcsaft.log`` and finishes with an ``epcsaft._core`` import check when compilation runs. Source-checkout profiles also copy extension-owned ``_native_core`` modules into the package source trees when those modules are enabled. Use ``uv run python scripts/dev/build_epcsaft.py --status`` when you need a non-mutating check of the configured generator, named build profile, Ceres/CppAD flags, system-Ceres/Ceres_DIR state, importable ``_core`` artifacts, stale ``.ninja_lock`` state, last Ninja target, and live repo-owned build processes. This is the safest first check when an IDE run or interrupted terminal build appears hung. The provider profile persists ``EPCSAFT_BUILD_PROFILE=provider`` so CMake/Ninja regeneration keeps Ceres, Ipopt, and extension-native modules disabled.

For IDE run configurations, keep commands explicit instead of relying on one overloaded target:

- Native build status: ``uv run python scripts/dev/build_epcsaft.py --status``
- Native incremental build: ``uv run python scripts/dev/build_epcsaft.py --build-only --parallel 10``
- Native configure/build: ``uv run python scripts/dev/build_epcsaft.py --profile fast``
- Clean Ceres + CppAD proof: ``uv run python scripts/dev/build_epcsaft.py --clean --profile full --parallel 4``
- Equilibrium package-native lane: ``uv run python scripts/dev/build_epcsaft.py --profile equilibrium``
- Regression package-native lane: ``uv run python scripts/dev/build_epcsaft.py --profile regression``
- Native Ipopt proof with the local install root: ``uv run python scripts/dev/build_epcsaft.py --clean --profile ipopt --ipopt-root "$HOME/.local/opt/ipopt"``
- Native Ipopt proof with another install root: ``uv run python scripts/dev/build_epcsaft.py --clean --profile ipopt --ipopt-root /path/to/Ipopt``
- Native Ipopt proof with an ``IpoptConfig.cmake`` directory: ``uv run python scripts/dev/build_epcsaft.py --clean --profile ipopt --ipopt-dir /path/to/lib/cmake/Ipopt``

Do not use ``--clean`` for routine validation. ``uv run python scripts/dev/build_epcsaft.py --clean`` is a repair action for stale CMake state or stale ``_core`` artifacts. A clean dev build deletes the reusable CMake tree, so Ceres source/configuration/build work under ``build/dev/_deps`` may run again unless you use a prebuilt system Ceres package. If a build reports ``Permission denied`` while writing ``_core*.so``, inspect the target directory ownership and permissions plus any concurrent process writing the same output. On Linux, a process importing the previous shared object does not lock the output path; it keeps the previous inode mapped. If ``--status`` reports a stale Ninja lock, inspect the listed process ids and stop only repo-owned build processes before retrying.

If Ceres becomes part of a repeated local source-checkout workflow, build Ceres
once outside ``build/dev`` and use the system-Ceres path instead of vendoring it
through ``FetchContent`` on every clean full-profile configure. The default
helper output can be used explicitly by the dev build and is auto-detected by
``scripts/dev/build_extension_dists.py`` for regression extension package
proof:

.. code-block:: bash

   uv run --no-sync python scripts/dev/build_system_ceres.py --parallel 2
   uv run --no-sync python scripts/dev/build_epcsaft.py --profile full --use-system-ceres --ceres-dir /path/to/lib/cmake/Ceres
   uv run --no-sync python scripts/dev/build_extension_dists.py --mode monorepo --ceres-dir /path/to/lib/cmake/Ceres --ipopt-root /path/to/ipopt

``--ceres-dir`` should point at the directory containing ``CeresConfig.cmake``. Ceres' own CMake documentation supports consuming either an installed Ceres package or an exported Ceres build directory through ``find_package(Ceres)`` and ``Ceres::ceres``.

``build_system_ceres.py`` inherits the current Linux shell compiler environment
and requires the uv-managed repo-local CMake and Ninja executables.

``scripts/dev/build_dist.py`` builds the provider package from
``packages/epcsaft`` with the provider-only release baseline. It keeps its
PEP 517 build state under ``build/pep517/provider-only`` for inspection and
does not consume Ceres or Ipopt.

LaTeX source and Linux builds
-----------------------------

``docs/latex`` is normal tracked repo content and is the source of truth for
equation-heavy LaTeX files. It is not a Git submodule. Its tracked
``.latexmkrc`` directs generated build artifacts to ``docs/latex/builds``.

Build the current equation documents from the repository root with a system
TeX installation that provides ``latexmk``:

.. code-block:: bash

   cd docs/latex
   latexmk -pdf equations.tex
   latexmk -pdf explicit_assocation.tex
   latexmk -pdf equilibrium_formulations.tex

Parallel worker safety
----------------------

The dev build tree and generated outputs under ``build/`` are shared disposable state. In parallel sessions, coordinate native rebuild, clean, and repair work so only one process owns the native extension at a time.

- Do not run clean or repair actions while tests, REPLs, IDE run configurations, or other workers may import ``epcsaft._core``.
- Prefer one native builder at a time for ``build/dev`` and the in-place ``_core`` extension.
- Let parallel workers run focused test slices for their lane, and reserve full build, doctor, and ``--confidence`` validation for coordinated handoff checks.
- Do not route performance claims through pytest. Add or restore an explicit benchmark or analysis workflow before making speed claims.

Project-local Git worktrees
---------------------------

Use ``scripts/dev/create_dev_worktree.sh`` from the primary checkout instead of raw ``git worktree add`` when a contributor needs a project-local worktree under ``.worktrees/``. The helper validates the worktree name, branch, and base ref before creating ``.worktrees/<name>``.

.. code-block:: bash

   scripts/dev/create_dev_worktree.sh --name equilibrium-v3 --branch feature/equilibrium-v3

``.worktrees/`` must stay ignored in ``.gitignore`` before using the helper. A same-user worktree does not require a global ``safe.directory`` mutation.

Test selection rules
--------------------

Use the smallest relevant test first, then run ``uv run python scripts/dev/validate_project.py confidence`` before release, merge, or broad runtime claims. Use ``uv run python run_pytest.py --all -q`` only when you explicitly need every retained pytest contract.

Before running ``run_pytest.py``, direct ``pytest``, or any ``validate_project.py``
mode that runs pytest, read this command matrix and the test-selection rules in
this section. Also read the relevant domain documentation for the slice: for
example, read ``docs/superpowers/milestones/M4-equilibrium/generalized-fluid-phase-equilibrium.md`` before
native/equilibrium route tests. If the right target is unclear, run
``uv run python run_pytest.py --list-slices`` before choosing a command.

- Provider wrapper/API changes: ``uv run python run_pytest.py --provider-api -q`` first, then ``uv run python run_pytest.py --confidence -q``.
- Equilibrium extension API or native-contract changes: ``uv run python run_pytest.py --equilibrium-api -q`` first. Package-facing and native-equilibrium tests live under ``packages/epcsaft-equilibrium/tests``; root ``tests/`` retains only provider, repo/workflow, build/package, registry, integration, and boundary-governance tests.
- Regression extension changes: ``uv run python run_pytest.py --regression -q`` first. Regression API, native, and Ceres contract tests live under ``packages/epcsaft-regression/tests`` and exercise the package through the provider contract and current native bridge.
- Cross-package ownership changes: ``uv run python run_pytest.py --integration -q`` first, then the smallest package-specific slice that matches the edit.
- Native/equation changes: ``uv run python scripts/dev/build_epcsaft.py --build-only --parallel 10`` first, then ``uv run python run_pytest.py --runtime -q``, then ``uv run python run_pytest.py --confidence -q``.
- Native route metadata, result-adapter diagnostics, or pybind payload-shape changes: run ``uv run python run_pytest.py --native-contracts -q`` first. Do not run broad route-builder files under ``packages/epcsaft-equilibrium/tests/native`` for these changes; the wrapper rejects those broad targets unless ``--allow-long-native-tests`` or ``EPCSAFT_ALLOW_LONG_NATIVE_TESTS=1`` is set.
- Equilibrium convergence diagnosis: use one explicit equilibrium test node with ``uv run python run_pytest.py --equilibrium-debug -q -s <target>`` or the phase-discovery checker with ``--debug --include-route-refinement --require-complete``. Do not use generic/API slices to investigate equilibrium runtime; they intentionally do not run the full ``packages/epcsaft-equilibrium/tests/api/test_equilibrium.py`` route-solve file or native result-file sweeps under ``packages/epcsaft-equilibrium/tests/native/results``. The wrapper rejects broad targets, slice-backed debug runs, and multi-node debug runs; long-suite opt-in is for deliberate sweep validation, not debug diagnosis. The checker records bounded Ipopt iteration history in its diagnostics payload so convergence can be audited without broad pytest runs. For neutral TP flash fixture diagnosis, run ``uv run python scripts/validation/check_neutral_tp_flash_fixture.py --phase-discovery-json <payload> --json --debug --require-complete``; debug native output is routed to stderr and JSON fixture output stays on stdout.
- HELD/GFPE milestone proof claims require the receipt-backed command row above. If the native extension has not been rebuilt or proven current, rerun the equilibrium native build before citing Stage II/III, neutral TP-flash fixture, or issue 188 HELD gate figures.
- Equation traceability changes: ``uv run python scripts/docs/sync_equation_registry.py --check --strict-traceability`` then ``uv run python run_pytest.py tests/native/contracts/test_equation_registry.py -q``.
- Performance claims: add or restore an explicit benchmark or analysis workflow first. Do not rely on pytest, skipped tests, or code inspection for speed claims.
- Plot asset changes: run the owning ``analyses/<category>/<short_id>/scripts`` coordinator or the figure-local ``analyses/<category>/<short_id>/figures/<figure_id>/scripts`` entrypoint, plus any targeted opt-in test under ``analyses/package_validation/package_plot_smokes/tests``, only when regenerating local plot outputs is explicitly part of the task.

- Packaging changes: ``uv run python scripts/dev/build_dist.py``. The command
  defaults to the provider-only release baseline with Ceres OFF, Ipopt OFF, and
  extension-owned native modules OFF, and it uses ``--parallel 1`` for isolated
  PEP 517 builds.

Keep generated plot assets and generated CSV workflows out of normal validation unless the task explicitly asks for them. There is no named plot validation slice; target the owning script or test file directly when plot output work is in scope.

Use ``uv run python run_pytest.py --list-slices`` when you need to inspect what each named slice runs before choosing a validation command.
The named slices and ``scripts/dev/validate_project.py`` modes are defined in
``scripts.dev.validation_registry``. Scientific capability evidence remains in
the owning package and must not be duplicated in the repository command registry.

For parallel sessions, leave the default repo-local temp behavior alone unless it causes contention. When running concurrent pytest lanes, set ``EPCSAFT_PYTEST_TEMP_ROOT`` to an external temp root for the extra lanes so each run gets an isolated ``pytest-temp`` child.

Runtime speed rule
------------------

For repeated runtime calls, build ``Mixture`` and ``State`` objects once and reuse them inside hot loops. If a runtime-speed claim matters, add or restore an explicit benchmark or analysis workflow for that claim.

Retired local benchmark scripts
-------------------------------

The previous local neutral-equilibrium timing harness, literature inventory, and
regression profile scripts were removed as obsolete. They no longer have
retained workflow entrypoints in this source tree.

Performance, literature-coverage, or paper-wide validation claims still require
explicit benchmark or analysis evidence, but that evidence must come from a
current, owned workflow added for the claim being made. Pytest remains limited
to package contracts, API wiring, native derivative availability, diagnostics,
and representative solver certification.

Troubleshooting
---------------

Run ``uv run python scripts/dev/doctor.py`` whenever imports, tool paths,
provider ``_core`` state, provider SDK metadata, or generated-output tracking
are unclear. It reports the active Python, git ref, uv/cmake/ninja paths,
provider and extension native module paths when available, provider SDK
CMake/source metadata, local Ceres/Ipopt SDK discovery, native artifact
freshness, generated artifact state, and the next recommended command. Use
``uv sync --no-install-workspace`` then
``uv run --no-sync python scripts/dev/doctor.py --require-provider-sdk`` for
fresh worktree provider/core smoke checks. Use the package-specific native
checks after the matching build lane:

.. code-block:: bash

   uv run --no-sync python scripts/dev/doctor.py --require-provider-sdk --require-provider-native
   uv run --no-sync python scripts/dev/doctor.py --require-provider-sdk --require-equilibrium-native
   uv run --no-sync python scripts/dev/doctor.py --require-provider-sdk --require-regression-native
   uv run --no-sync python scripts/dev/doctor.py --require-provider-sdk --require-extension-native

The extension-native shorthand requires both equilibrium and regression native
modules and should be used after full-native setup or when package-boundary
proof needs both extension-owned native modules.

If ``scripts/dev/build_epcsaft.py`` appears slow, run ``uv run python scripts/dev/build_epcsaft.py --status`` first. If the status output shows a stale Ninja lock and live repo-owned build processes, resolve those processes before retrying. If the status output is clean, check whether ``build/dev/CMakeCache.txt`` reports a non-Ninja generator. A clean one-time switch to Ninja can materially reduce rebuild overhead when Ninja is installed. Clean Ceres configure/builds can still take longer than incremental rebuilds; ``--build-only --parallel 10`` is the intended C++ edit loop after the tree is configured.
