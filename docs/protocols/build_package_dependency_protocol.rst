Build/Package Dependency Protocol
=================================

This protocol is the source of truth for source-checkout builds, native
dependency policy, CMake package management, GitHub Actions native lanes, and
package-boundary validation. Update it in the same change as any build,
packaging, dependency, or CI behavior change that would otherwise change the
meaning of the commands in the development workflow guide.

Root ``CMAKE.md`` is the direct CMake execution protocol. Keep it aligned when
direct preset, Services, wrapper, generator, or local toolchain behavior
changes.

Current transition dependency contract
--------------------------------------

This source checkout is still a monorepo transition build. It builds the
provider ``epcsaft._core`` module from provider-owned native code and builds
package-owned native modules for ``epcsaft-equilibrium`` and
``epcsaft-regression`` when those extension lanes are enabled. ADR 0005 assigns
final Ceres-backed regression ownership to ``epcsaft-regression`` and
Ipopt-backed equilibrium ownership to ``epcsaft-equilibrium``; provider
``_core`` must not carry extension-native symbols.

Ceres is currently required for native regression builds in this checkout.
CppAD is required for derivative-capable provider builds and remains core-owned
after the split. Ipopt is required for production equilibrium validation because
production native equilibrium routes are Ipopt-backed NLP routes.

The default source-checkout build command remains:

.. code-block:: powershell

   uv run python scripts/dev/build_epcsaft.py

That command uses the fast profile: package-owned equilibrium and regression
native modules enabled, Ceres ON, CppAD ON, and Ipopt ON when a native Ipopt
install is discoverable. ``--disable-ipopt`` is allowed only for a diagnostic
or smoke lane that intentionally excludes Ipopt. A no-Ipopt smoke lane must not
be described as production equilibrium validation.

The provider-only boundary proof now has an explicit direct-build profile:

.. code-block:: powershell

   uv run python scripts/dev/build_epcsaft.py --clean --profile provider

That profile keeps CppAD ON while setting
``EPCSAFT_ENABLE_CERES=OFF``, ``EPCSAFT_ENABLE_IPOPT=OFF``,
``EPCSAFT_BUILD_EQUILIBRIUM_NATIVE_MODULE=OFF``, and
``EPCSAFT_BUILD_REGRESSION_NATIVE_MODULE=OFF`` so provider ``epcsaft._core``
exports provider-owned symbols only. The repo build helper also writes
``EPCSAFT_BUILD_PROFILE=provider`` into CMake cache so Ninja regeneration keeps
the provider-only flags pinned instead of falling back to transition defaults.

Package-specific source-checkout lanes have explicit direct-build profiles:

.. code-block:: powershell

   uv run python scripts/dev/build_epcsaft.py --profile equilibrium
   uv run python scripts/dev/build_epcsaft.py --profile regression

The ``equilibrium`` profile builds provider ``_core`` plus the
``epcsaft-equilibrium`` package-owned native module with Ipopt enabled and
Ceres/regression disabled. The ``regression`` profile builds provider ``_core``
plus the ``epcsaft-regression`` package-owned native module with Ceres enabled
and Ipopt/equilibrium disabled. These profiles are the Codex worktree setup
lanes for package-scoped threads; the full source-checkout profile remains the
cross-package native lane.

Extension package build proof now has package-local entry points:

.. code-block:: powershell

   uv run python scripts/dev/build_extension_dists.py --mode monorepo --parallel 1 --ipopt-root "$env:USERPROFILE\Documents\deps\ipopt-msvc"
   uv run python scripts/dev/build_extension_dists.py --mode installed-provider --parallel 1 --ipopt-root "$env:USERPROFILE\Documents\deps\ipopt-msvc"

The monorepo mode consumes the sibling ``packages/epcsaft`` provider SDK
source/CMake metadata. The installed-provider mode consumes the same SDK from
an installed provider wheel. The equilibrium extension proof requires a real
Ipopt SDK; disabling Ipopt is not production equilibrium package evidence.

Release/install proof from local artifacts is executable through:

.. code-block:: powershell

   uv run python scripts/dev/check_release_installs.py --dist-dir dist

The helper installs from the local ``dist/`` directory with
``--no-index --find-links`` and proves the supported provider and extension
combinations. It is not a PyPI publish step.

Regression and equilibrium are transition capabilities
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Native regression and production native equilibrium are current monorepo
capabilities, not optional examples. That does not make them final core package
capabilities. ADR 0005 assigns final ownership of Ceres-backed regression to
``epcsaft-regression`` and Ipopt-backed equilibrium to
``epcsaft-equilibrium``.

Ceres, CppAD, and Ipopt should therefore be enabled by default in this checkout
where the relevant native dependency can be provided with controlled,
reproducible friction. The provider-only package proof separates that
source-checkout convenience from final core dependency ownership by explicitly
building without Ceres and Ipopt while retaining CppAD.

The intended transition low-friction path is:

- reuse or auto-detect a local/system Ceres package when repeated builds would
  otherwise rebuild Ceres;
- use FetchContent for Ceres/CppAD where that is the simplest reproducible
  source-checkout route;
- use a native system Ipopt install or pinned non-Conda Ipopt SDK artifact;
- keep normal wheels/sdists free from user-local Ipopt runtime coupling unless
  an explicit Ipopt package artifact is being validated;
- reserve no-Ipopt and no-Ceres builds for smoke, diagnostic, or
  package-boundary lanes.

A build or CI lane that disables Ipopt must be named and documented as a
no-Ipopt lane. It must not be used as evidence for production equilibrium
validation.

CMake and C++ dependency rules
------------------------------

Keep the CMake dependency contract explicit and loud:

- ``EPCSAFT_ENABLE_CERES`` stays ON by default for the transition checkout, but
  OFF is supported for provider-only and equilibrium-extension package-boundary
  proof lanes.
- ``EPCSAFT_BUILD_EQUILIBRIUM_NATIVE_MODULE`` stays ON by default for the
  source checkout, but OFF is required for provider-only build/install proof.
- ``EPCSAFT_BUILD_REGRESSION_NATIVE_MODULE`` stays ON by default for the source
  checkout, but OFF is required for provider-only build/install proof.
- ``EPCSAFT_ENABLE_CPPAD`` stays ON and unsupported when OFF.
- ``EPCSAFT_ENABLE_IPOPT`` stays ON for Ipopt-capable source validation.
- ``build_epcsaft.py --profile equilibrium`` is the equilibrium-native lane:
  Ipopt ON, Ceres OFF, equilibrium native module ON, regression native module
  OFF.
- ``build_epcsaft.py --profile regression`` is the regression-native lane:
  Ceres ON, Ipopt OFF, regression native module ON, equilibrium native module
  OFF.
- Vendored Ipopt builds are not supported by the package CMake project.
- System Ipopt is supplied through ``EPCSAFT_IPOPT_ROOT`` or ``Ipopt_DIR``.
  On Windows, default discovery probes
  ``%LOCALAPPDATA%\ePC-SAFT\deps\ipopt-msvc``,
  ``%USERPROFILE%\.epcsaft\deps\ipopt-msvc``, and the legacy
  ``%USERPROFILE%\Documents\deps\ipopt-msvc`` path, in that order.
- Reusable local Ceres packages are preferred over repeated clean FetchContent
  Ceres builds when a workflow repeatedly rebuilds native code.
- CppAD may use FetchContent or an installed include tree, but the package
  remains derivative-capable by default.

Do not hide missing required dependency coverage behind silent defaults. A lane
that needs production equilibrium proof must configure Ipopt and fail loudly if
the requested Ipopt root or config package cannot be used.

Do not reframe Ceres, CppAD, or Ipopt as greenfield optional dependencies in
repo protocol documents. In the transition checkout, Ceres and Ipopt are enabled
for the native capabilities named above, with explicitly scoped smoke or
package-boundary exceptions. In the final split, Ceres belongs to the regression
package, Ipopt belongs to the equilibrium package, and CppAD remains part of the
core derivative provider substrate.

CI lane policy
--------------

The current early package-development merge policy is local proof first. As of
2026-05-29, GitHub branch protection has no required status checks or required
reviews. Ordinary PRs should carry risk-based focused local proof in the PR
body, and only lightweight smoke checks run automatically on ``pull_request``.
Heavy native, package, release, and installed-provider lanes are manual-only
unless a PR explicitly claims release readiness, capability support, or
production native behavior.

CI lane names still separate different claims:

``native production Ipopt``
   The production equilibrium lane. It should download a
   pinned non-Conda Ipopt SDK artifact, verify checksum and provenance, set
   ``EPCSAFT_IPOPT_ROOT`` or ``Ipopt_DIR``, run
   ``uv run python scripts/dev/build_epcsaft.py --clean --profile ipopt``, and
   run native contracts plus focused selector/equilibrium tests. It is
   manual-only during early package development and required before production
   Ipopt capability or release claims.

``native no-Ipopt smoke``
   A cheap smoke lane that intentionally runs with ``--disable-ipopt``. It
   may prove package import, Ceres, CppAD, and non-Ipopt contracts, but it does
   not prove production Ipopt equilibrium behavior.

``provider-only boundary``
   A focused lane that runs ``uv run python scripts/dev/build_epcsaft.py
   --clean --profile provider`` and then checks that provider ``_core`` omits
   equilibrium and regression native symbols.

``equilibrium-native worktree``
   A package-scoped lane that runs ``uv run python
   scripts/dev/build_epcsaft.py --profile equilibrium`` and then checks
   ``uv run python scripts/dev/doctor.py --require-provider-sdk
   --require-equilibrium-native``.

``regression-native worktree``
   A package-scoped lane that runs ``uv run python
   scripts/dev/build_epcsaft.py --profile regression`` with the reusable Ceres
   package when available and then checks ``uv run python scripts/dev/doctor.py
   --require-provider-sdk --require-regression-native``.

``native CppAD derivative contract``
   A focused CppAD derivative lane for CppAD/autodiff derivative coverage. It should use
   current build flags, not the removed ``--enable-cppad`` flag, and should run
   focused derivative and association-sensitivity contracts.

``release package boundary``
   Wheel and sdist validation. The normal release baseline may avoid local
   Ipopt runtime coupling so installable artifacts do not require user-local
   Ipopt DLLs. This does not reduce the source/native requirement that
   production equilibrium validation prove Ipopt.

``extension package boundary``
   Package-local wheel/sdist validation for ``epcsaft-equilibrium`` and
   ``epcsaft-regression``. It builds extension wheels from their package roots
   in monorepo-provider and installed-provider SDK modes and smoke-imports
   their package-owned ``_native_core`` modules. Regression package builds
   should consume the repo-local reusable Ceres package through
   ``EPCSAFT_PEP517_CERES_DIR`` or helper auto-detection when it exists, rather
   than recompiling Ceres source for every extension proof.

``package build lanes``
   GitHub Actions lanes named provider package build, regression package build,
   equilibrium package build, and installed-provider extension builds. These
   lanes run by ``workflow_dispatch`` during early package development.
   Equilibrium and installed-provider extension lanes require a real Ipopt SDK
   path or artifact and must not substitute a no-Ipopt success path for
   production equilibrium package proof. Equilibrium wheels must install the
   audited runtime dependency closure for ``epcsaft_equilibrium._native_core``
   and Ipopt, not a broad ``bin/*.dll`` payload from the SDK.

No-Conda Ipopt policy
---------------------

Conda or mamba must not be the normal Ipopt CI provisioning path. The accepted
direction is a controlled non-Conda SDK artifact path based on the official
COIN-OR build route. The Ipopt installation documentation describes Windows
MSYS2/MinGW setup, BLAS/LAPACK, sparse symmetric indefinite linear solver
requirements, and source builds. The coinbrew documentation describes a helper
that fetches, builds, and installs COIN-OR projects and dependencies.

Option B is the accepted production Ipopt lane direction: the manual production
Ipopt lane should fetch a pinned prebuilt non-Conda Ipopt SDK artifact, verify
checksum and provenance, set ``EPCSAFT_IPOPT_ROOT`` or ``Ipopt_DIR``, and run
the production Ipopt native lane. The source build belongs in a separate manual
SDK artifact-builder workflow that publishes the pinned SDK artifact and
provenance manifest.

Decision ledger
---------------

2026-05-22 - Native PR CI dependency direction
   Status: Superseded for ordinary PR gating by the 2026-05-29 local-proof-first
   policy; retained as the production Ipopt lane direction.

   Decision: use Option B for production Ipopt proof. Build Ipopt from source
   in a separate manual no-Conda SDK artifact-builder workflow, then let the
   production Ipopt lane consume that pinned artifact with checksum/provenance
   verification.

2026-05-22 - ``--disable-ipopt`` CI meaning
   Status: Implemented as policy; pending full production Ipopt PR lane.

   Decision: ``--disable-ipopt`` is acceptable only for a no-Ipopt smoke lane.
   It must not be the only source/native PR signal once production equilibrium
   behavior is being validated.

2026-05-22 - CppAD PR lane
   Status: Superseded for ordinary PR gating by the 2026-05-29 local-proof-first
   policy; retained as a manual heavy proof lane.

   Decision: the focused CppAD lane uses current build flags and protects
   derivative/autodiff contracts rather than duplicating the production Ipopt
   lane.

2026-05-29 - Early package PR gates
   Status: Implemented as policy.

   Decision: ordinary early package-development PRs use local proof first.
   Heavy native, package, release, and installed-provider GitHub Actions lanes
   run manually and are required before release readiness, capability support,
   or production native behavior claims, not before every ordinary PR.

2026-05-22 - Release package boundary
   Status: Accepted.

   Decision: wheel/sdist release checks may keep local Ipopt runtime coupling
   out of normal install artifacts, while source/native production equilibrium
   validation remains responsible for Ipopt proof.

References
----------

- `Ipopt installing documentation <https://coin-or.github.io/Ipopt/INSTALL.html>`_
- `coinbrew documentation <https://coin-or.github.io/coinbrew/>`_
