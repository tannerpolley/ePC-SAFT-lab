Native And Equation Debugging
=============================

Use this page when a change crosses the Python wrapper, pybind11 seam, or native ePC-SAFT equations.

Runtime flow
------------

The public API starts in ``src/epcsaft/frontend/``. ``Mixture`` normalizes
``ParameterSet`` and ``ModelOptions`` inputs and owns the internal native
runtime bridge. ``State`` validates ``T/x/P`` or ``T/x/rho`` inputs and exposes
pressure, density, fugacity, and derivative payloads.

The pybind11 boundary starts in ``src/epcsaft/native/bindings/module.cpp``. It
exposes ``NativeArgs``, ``NativeMixture``, ``NativeState``, and contribution
result structs through the private ``epcsaft._core`` module. Equilibrium
bindings are registered by the domain-owned
``src/epcsaft/native/equilibrium/register_bindings.cpp`` unit so the generic
binding file does not include route, block, solver, or result internals.

The native implementation lives under domain folders in ``src/epcsaft/native``. High-traffic files are:

- ``eos/density.cpp`` for pressure-to-density closure.
- ``eos/residual_helmholtz.cpp`` for residual Helmholtz contribution totals.
- ``eos/compressibility.cpp`` for compressibility factor and pressure from density.
- ``eos/chemical_potential.cpp`` and ``eos/fugacity.cpp`` for residual chemical potential and fugacity.
- ``eos/activity.cpp`` for activity, osmotic, and solvation outputs.
- ``equilibrium/core/activation_matrix.h`` for native route family activation metadata.
- ``equilibrium/routes/derived/bubble_dew.cpp`` and ``equilibrium/solvers/ipopt_adapter.cpp`` for the trusted bubble/dew Ipopt route.

Validation commands
-------------------

Use the normal build path first:

.. code-block:: powershell

   uv run python scripts/dev/build_epcsaft.py
   uv run python scripts/dev/doctor.py
   uv run python run_pytest.py --confidence -q

The normal local dev build is the fast profile: Ceres ON, CppAD ON, and Ipopt ON when ``EPCSAFT_IPOPT_ROOT``, ``EPCSAFT_PEP517_IPOPT_ROOT``, ``--ipopt-dir``, or the Windows local SDK default ``%USERPROFILE%\Documents\deps\ipopt-msvc`` provides a native Ipopt install. Ceres is required for native regression builds, CppAD is required for derivative-capable builds, and Ipopt-enabled builds own the production native equilibrium routes. Use ``uv run python scripts/dev/build_epcsaft.py --disable-ipopt`` only when the debug task intentionally excludes native Ipopt coverage.

For C++ iteration after the build tree is configured:

.. code-block:: powershell

   uv run python scripts/dev/build_epcsaft.py --build-only --parallel 10
   uv run python run_pytest.py --runtime -q

For method-speed checks, add or restore an explicit benchmark or analysis
workflow before making speed claims. The previous local benchmark scripts were
removed as obsolete; pytest remains for contracts and diagnostics, not
performance evidence.

Equation traceability
---------------------

``docs/latex/equations.tex`` is the source of truth for equation text. ``docs/equations.md`` and ``docs/equations_registry.yaml`` are generated navigation views.

Native owner comments use ``// EqID: <id>`` near the implementing C++ function. When touching equation code, keep the EqID comment close to the function that owns the expression and run:

.. code-block:: powershell

   uv run python scripts/docs/sync_equation_registry.py --check --strict-traceability
   uv run python run_pytest.py tests/native/contracts/test_equation_registry.py -q

See :doc:`equation_traceability` for the EqID classification and owner-comment checklist.

Debugging checklist
-------------------

- Reproduce the behavior through a public ``Mixture`` / ``State`` call before debugging private native functions.
- Compare pressure-created and density-created states when investigating density closure. Start with the same ``T`` and ``x`` and compare density, pressure, ``z()``, and ``ares()``. Use ``State(mixture, ..., P=..., rho_guess=...)`` to test seeded pressure closure and ``State(mixture, ..., rho=...)`` to audit an externally supplied density against a target pressure.
- Inspect ``src/epcsaft/native/eos/density.cpp`` and ``src/epcsaft/native/eos/state.cpp`` for pressure-to-density root selection, warm-start behavior, and phase-branch policy before changing contribution code.
- Request contribution terms with ``return_contribution_terms=True`` when debugging residual Helmholtz, compressibility factor, chemical potential, or fugacity totals.
- Request contribution terms and compare ``hc``, ``disp``, ``assoc``, ``ion``, and ``born`` totals before adding temporary native instrumentation.
- Run ``uv run python scripts/docs/sync_equation_registry.py --check --strict-traceability`` before making equation ownership claims. If that check passes but registry entries still show ``cpp_refs: []``, treat those EqIDs as documentation or supplemental equations unless the task proves they should map to implementation code.
- Use ``tests/native/state/`` for fast neutral closure, contribution-map, derivative, and runtime-cache regression coverage.
