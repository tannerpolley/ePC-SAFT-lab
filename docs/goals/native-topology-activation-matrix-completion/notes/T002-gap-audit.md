# T002 Gap Audit

Date: 2026-05-21

Scope: read-only audit against the approved handoff, baseline `3889de77`, current native/Python surfaces, runtime capability reporting, tests, docs, and build source topology.

## Current Violations

### Binding and Facade Seams

- `src/epcsaft/native/bindings/module.cpp` still directly includes equilibrium route, block, solver, and result internals: `equilibrium/routes/route_builders.h`, `equilibrium/routes/stability/stability_route_builders.h`, `equilibrium/blocks/*`, `equilibrium/solvers/ipopt_adapter.h`, and result bridge headers.
- `module.cpp` still exports non-production route bindings for neutral TP flash, neutral LLE, electrolyte LLE, electrolyte bubble pressure, neutral stability, electrolyte stability, reactive stability, reactive LLE, reactive-electrolyte LLE, reactive phase postsolve, and native chemical equilibrium.
- `src/epcsaft/native/equilibrium/facade.h` still includes `equilibrium/routes/route_builders.h` and exposes route-builder aliases/results, including `NativeRouteMetadata`, neutral two-phase route contracts/results, and reactive route contracts/results.

Task mapping: T004 failing seam tests, T005 selector/binding registration core, T006 route deletion and facade contraction.

### Selector Core

- `src/epcsaft/native/equilibrium/core/activation_matrix.h` is present and already marks only `bubble_dew_derived_routes` as `production_exposed`.
- There is no production selector core under `src/epcsaft/native/equilibrium/core/` that owns row ordering, activation checks, exact-derivative requirements, hard constraints, density closure diagnostics, or hard certification gating.
- The trusted bubble/dew code still lives behind route-specific builders in `src/epcsaft/native/equilibrium/routes/derived/bubble_dew.cpp` and is exported directly through binding functions instead of selector dispatch.

Task mapping: T004 selector contract tests, T005 selector core and bubble/dew migration.

### Runtime Capabilities

- `_core._native_equilibrium_activation_matrix()` reports the intended C++ rows, with only `bubble_dew_derived_routes` production-exposed.
- `epcsaft.capabilities()["equilibrium"]` still reports independent route capability keys such as `neutral_tp_flash`, `neutral_lle_flash`, `neutral_stability`, `electrolyte_lle`, `electrolyte_bubble_pressure`, `electrolyte_stability`, `reactive_speciation`, and reactive stability/LLE families.
- `src/epcsaft/runtime/capability_evidence.py` remains an independent source of route availability claims instead of a generated mirror derived from native activation metadata.

Task mapping: T004 capability mirror tests, T007 generated runtime mirror and capability contraction.

### Python API and Adapters

- `src/epcsaft/frontend/equilibrium.py` already keeps the intended production public API shape: `Equilibrium(mixture).bubble_pressure(T=..., x=...)`.
- Lower-level package exports remain broad: `src/epcsaft/equilibrium/__init__.py` wildcard-exports route workflows.
- `src/epcsaft/equilibrium/workflows.py` still defines TP flash, LLE, stability, electrolyte, reactive speciation, reactive-electrolyte bubble, and reactive phase-equilibrium problem/route surfaces.
- `src/epcsaft/state/native_adapter.py` still exposes route-call methods and generic route dispatch for TP flash, bubble/dew variants, LLE, stability, electrolyte LLE/bubble, chemical equilibrium, reactive LLE, reactive stability, and reactive-electrolyte bubble/sweeps.

Task mapping: T004 deleted-route absence tests, T006 Python API and adapter contraction.

### CMake and Native Source Topology

- `CMakeLists.txt` still builds non-production route sources: `equilibrium/workflows.cpp`, `routes/route_builders.cpp`, `routes/reactive/chemical_equilibrium.cpp`, `routes/reactive/ideal_speciation_problem.cpp`, `routes/reactive/phase_equilibrium_problem.cpp`, and `routes/stability/stability_route_builders.cpp`.
- Production bubble/dew currently depends on `routes/derived/bubble_dew.cpp`, which itself includes `equilibrium/routes/route_builders.h`; this must be isolated through the selector core rather than preserving broad route-builder dependencies.
- Low-level blocks need deletion or retention only after verifying surviving selector/bubble/dew dependencies. No compatibility wrappers or hidden callable route shells are allowed.

Task mapping: T005 native selector implementation, T006 route source deletion, T010 build proof.

### Tests and Docs

- Old route tests still exist under `tests/native/equilibrium/routes/{neutral,electrolyte,reactive,reactive_electrolyte,stability}` and diagnostic/contract tests still assert non-production route metadata and native evaluator presence.
- `tests/workflows/repo/test_project_structure.py` still treats reactive/electrolyte route modules and tests as expected structure.
- `tests/workflows/repo/test_run_pytest.py` still references the old neutral bubble/dew route test path.
- `docs/algorithms_registry.yaml`, `docs/algorithms.md`, and `docs/latex/algorithms.tex` still include active AlgIDs for neutral TP flash, neutral LLE, electrolyte LLE, stability TPD, ideal/nonideal speciation, reactive LLE, and reactive-electrolyte LLE.
- `CONTEXT.md` does not yet define Selector Core, Native Activation Matrix, or Declared-Not-Exposed Route Family.
- No ADR yet records the selector-core ownership, production-first route deletion, activation-driven capability mirror, and no-stub policy.

Task mapping: T004 failing structure/doc absence tests, T006 test cleanup, T008 docs/ADR/registry update.

## Implementation Sequence Verdict

The approved task sequence still matches the current gaps:

1. Write failing contract tests for seam contraction, activation/capability mirror, selector certification, and deleted-route absence.
2. Implement selector-core dispatch and migrate neutral hydrocarbon bubble/dew through it.
3. Delete non-production route bindings, native sources, Python route surfaces, docs, and tests.
4. Generate the runtime activation mirror from C++ metadata and contract capabilities to activation rows.
5. Update docs, ADR, glossary, and algorithm registry.
6. Run independent review before final Gate 10 validation, commit, push, and completion audit.

Blockers found: none before T003 judge review. Risk to watch: the largest implementation risk is accidentally leaving callable route shells through `module.cpp`, `facade.h`, `workflows.py`, or `native_adapter.py` while tests only check documentation.

## Owner Receipts

- `build_packaging_owner` confirmed that binding split work needs explicit CMake ownership because `_core` is currently a single `module.cpp` extension target; deletion is not a pure source prune because non-production route sources are explicitly listed in `CMakeLists.txt`; a generated Python mirror under `src/epcsaft/runtime/` is the safest package-inclusion path; strict algorithm registry traceability will fail unless owner comments move with the surviving algorithm or deleted AlgIDs are removed.
- `python_api_test_owner` confirmed public export leakage through `src/epcsaft/equilibrium/__init__.py`, legacy route dispatch through `src/epcsaft/state/native_adapter.py`, handwritten capability drift through `src/epcsaft/runtime/capability_evidence.py`, run-pytest workflow coupling to that registry, and the missing Python mirror/native activation contract test.
- `native_solver_backend_owner` did not return a bounded receipt before shutdown. Main-thread native evidence is recorded above: direct binding includes and exports, facade route-builder leakage, absence of selector-core dispatch, and direct route-builder ownership of bubble/dew.
