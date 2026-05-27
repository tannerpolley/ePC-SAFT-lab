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

This source checkout is still a monorepo transition build. It compiles the
current provider, regression, and equilibrium native capability set into one
``_core`` module, with logical native object targets separating provider/CppAD,
equilibrium/Ipopt, and regression/Ceres ownership while ADR 0005 moves final
package ownership to separate packages.

Ceres is currently required for native regression builds in this checkout.
CppAD is required for derivative-capable provider builds and remains core-owned
after the split. Ipopt is required for production equilibrium validation because
production native equilibrium routes are Ipopt-backed NLP routes.

The default source-checkout build command remains:

.. code-block:: powershell

   uv run python scripts/dev/build_epcsaft.py

That command uses the fast profile: Ceres ON, CppAD ON, and Ipopt ON when a
native Ipopt install is discoverable. ``--disable-ipopt`` is allowed only for a
diagnostic or smoke lane that intentionally excludes Ipopt. A no-Ipopt smoke
lane must not be described as production equilibrium validation.

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
- ``EPCSAFT_ENABLE_CPPAD`` stays ON and unsupported when OFF.
- ``EPCSAFT_ENABLE_IPOPT`` stays ON for Ipopt-capable source validation.
- Vendored Ipopt builds are not supported by the package CMake project.
- System Ipopt is supplied through ``EPCSAFT_IPOPT_ROOT`` or ``Ipopt_DIR``.
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

Normal PR CI should have separate lane names for separate claims:

``native production Ipopt``
   The future merge-relevant production equilibrium lane. It should download a
   pinned non-Conda Ipopt SDK artifact, verify checksum and provenance, set
   ``EPCSAFT_IPOPT_ROOT`` or ``Ipopt_DIR``, run
   ``uv run python scripts/dev/build_epcsaft.py --clean --profile ipopt``, and
   run native contracts plus focused selector/equilibrium tests.

``native no-Ipopt smoke``
   A cheap PR smoke lane that intentionally runs with ``--disable-ipopt``. It
   may prove package import, Ceres, CppAD, and non-Ipopt contracts, but it does
   not prove production Ipopt equilibrium behavior.

``native CppAD derivative contract``
   A focused CppAD derivative lane for CppAD/autodiff derivative coverage. It should use
   current build flags, not the removed ``--enable-cppad`` flag, and should run
   focused derivative and association-sensitivity contracts.

``release package boundary``
   Wheel and sdist validation. The normal release baseline may avoid local
   Ipopt runtime coupling so installable artifacts do not require user-local
   Ipopt DLLs. This does not reduce the source/native requirement that
   production equilibrium validation prove Ipopt.

No-Conda Ipopt policy
---------------------

Conda or mamba must not be the normal Ipopt CI provisioning path. The accepted
direction is a controlled non-Conda SDK artifact path based on the official
COIN-OR build route. The Ipopt installation documentation describes Windows
MSYS2/MinGW setup, BLAS/LAPACK, sparse symmetric indefinite linear solver
requirements, and source builds. The coinbrew documentation describes a helper
that fetches, builds, and installs COIN-OR projects and dependencies.

Option B is the accepted normal PR CI direction: normal PR CI should fetch a
pinned prebuilt non-Conda Ipopt SDK artifact, verify checksum and provenance,
set ``EPCSAFT_IPOPT_ROOT`` or ``Ipopt_DIR``, and run the production Ipopt native
lane. The source build belongs in a separate manual/scheduled builder workflow
that publishes the pinned SDK artifact and provenance manifest.

Decision ledger
---------------

2026-05-22 - Native PR CI dependency direction
   Status: Pending workflow.

   Decision: use Option B for normal PR CI. Build Ipopt from source in a
   separate manual/scheduled no-Conda SDK artifact-builder workflow, then let
   normal PR CI consume that pinned artifact with checksum/provenance
   verification.

2026-05-22 - ``--disable-ipopt`` CI meaning
   Status: Implemented as policy; pending full production Ipopt PR lane.

   Decision: ``--disable-ipopt`` is acceptable only for a no-Ipopt smoke lane.
   It must not be the only source/native PR signal once production equilibrium
   behavior is being validated.

2026-05-22 - CppAD PR lane
   Status: Implemented for stale command and PR scheduling; expandable test
   coverage remains lane-specific maintenance.

   Decision: the focused CppAD lane runs on PRs, uses current build flags, and
   protects derivative/autodiff contracts rather than duplicating the future
   production Ipopt lane.

2026-05-22 - Release package boundary
   Status: Accepted.

   Decision: wheel/sdist release checks may keep local Ipopt runtime coupling
   out of normal install artifacts, while source/native production equilibrium
   validation remains responsible for Ipopt proof.

References
----------

- `Ipopt installing documentation <https://coin-or.github.io/Ipopt/INSTALL.html>`_
- `coinbrew documentation <https://coin-or.github.io/coinbrew/>`_
