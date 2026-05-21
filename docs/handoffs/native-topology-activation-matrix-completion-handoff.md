# Native Topology Activation-Matrix Completion Handoff

Created: 2026-05-21

This handoff is for a brand-new Codex thread. Its first job is to create a GoalBuddy board that forces full completion of the native C++ topology and activation-matrix refactor. The previous commit is useful, but it is not satisfactory against the full plan.

## Implementation Update

Updated: 2026-05-21

This handoff has now been executed on branch `ipopt` through the
`docs/goals/native-topology-activation-matrix-completion/state.yaml` board.
The implementation adds the native selector core, routes public
`Equilibrium(mixture).bubble_pressure(T=..., x=...)` through the selector,
generates the Python capability mirror from native activation metadata, deletes
non-production route source/tests/docs instead of preserving stubs, and records
the decision in ADR 0003. Treat the remaining sections as historical acceptance
context; the current source of truth is the code, ADR, updated roadmaps,
algorithm registry, and GoalBuddy receipts from this implementation run.

## Copy-Paste Prompt For The New Thread

Paste the following into a fresh Codex thread from `C:\Users\Tanner\Documents\git\ePC-SAFT`:

```text
Use GoalBuddy goal prep and create a local live board for this exact follow-up. Do not start implementation until the board exists, passes the GoalBuddy checker, and contains the acceptance gates below as explicit tasks.

Goal title: Finish Native Topology And Activation-Matrix Refactor
Goal slug: native-topology-activation-matrix-completion

Context:
- Current branch: ipopt.
- Baseline commit to audit from: 3889de77 Refactor native topology around activation matrix.
- That commit successfully moved native C++ files into domain folders and passed focused tests, but it did not fully satisfy the architecture plan.
- It also did not complete the unified equilibrium-core roadmap: the current code has shared `NlpProblem`/Ipopt plumbing and native activation metadata, but route construction remains mostly route-specific instead of being driven by a canonical residual/constraint selector core.
- The work must finish the actual plan, not merely make tests pass.

Required skills/policies:
- Read and apply C:\Users\Tanner\Documents\git\ePC-SAFT\docs\.codex-journal\user_preferences.md.
- Read and apply C:\Users\Tanner\Documents\git\ePC-SAFT\docs\roadmaps\FULL_ROADMAP.md.
- Read and apply C:\Users\Tanner\Documents\git\ePC-SAFT\docs\roadmaps\unified_equilibrium_core_algorithm.md.
- Use the GoalBuddy policy at C:\Users\Tanner\.codex\GOALBUDDY.md.
- Use the chemical-engineer skill for ePC-SAFT/native equilibrium claims.
- Use requesting-code-review before final commit.

Hard rule:
The goal is not complete until every acceptance gate in docs/handoffs/native-topology-activation-matrix-completion-handoff.md is implemented, tested, documented, and recorded on the GoalBuddy board. If a gate cannot be implemented, stop and mark the exact task blocked with evidence. Do not silently downgrade the requirement.

Create the GoalBuddy board first:
1. Resolve the installed GoalBuddy checker with:
   $goalBuddyChecker = & C:\Users\Tanner\Documents\git\codex-maintenance\scripts\resolve-goalbuddy-skill-path.ps1 -RelativePath "scripts\check-goal-state.mjs"
2. Create docs/goals/native-topology-activation-matrix-completion/goal.md.
3. Create docs/goals/native-topology-activation-matrix-completion/state.yaml using the bundled v2 template shape.
4. Use a local live visual board by default:
   & C:\Users\Tanner\Documents\git\codex-maintenance\scripts\start-goalbuddy-board.ps1 -Goal docs/goals/native-topology-activation-matrix-completion
5. Run:
   node $goalBuddyChecker docs/goals/native-topology-activation-matrix-completion/state.yaml
6. Only after that, begin implementation.

The first active task must be a read-only gap audit against this handoff and commit 3889de77. The second task must be a Judge/PM acceptance-gate decision that confirms the planned implementation slices and guard tests before edits.

Before adding new route families, new route tests, or broad validation, the board must resolve Gate 4A: whether this follow-up implements the full selector-driven residual core or a guarded intermediate where existing route-specific `NlpProblem` classes remain constrained by activation metadata.

Do not commit until all required validation commands in this handoff have passed and repo cleanup has passed.
```

## Why This Follow-Up Exists

Commit `3889de77` completed a valuable topology tranche:

- moved native implementation files into `native/model`, `native/eos`, `native/autodiff`, `native/equilibrium`, `native/regression`, and `native/bindings`;
- moved `src/epcsaft/bindings.cpp` to `src/epcsaft/native/bindings/module.cpp`;
- replaced broad native CMake globs with explicit source groups;
- added `src/epcsaft/native/equilibrium/core/activation_matrix.h`;
- updated traceability docs and passed focused validation.

It did not fully satisfy the plan because:

- `src/epcsaft/native/bindings/module.cpp` still directly includes equilibrium route blocks, solver internals, route builders, and second-order assembly headers;
- runtime capability reporting still uses the Python registry in `src/epcsaft/runtime/capability_evidence.py` as the production source instead of native activation metadata;
- `src/epcsaft/native/equilibrium/facade.h` still leaks route-builder/internal `equilibrium_nlp` result types across the facade boundary;
- the new guard tests catch stale paths and CMake globs, but do not catch the binding seam leak or activation-matrix/capability divergence.

## Critical Equilibrium-Core Gap Against The Roadmap

This follow-up must not treat the native topology move as equivalent to the unified equilibrium-core architecture.

Verified roadmap contract from `docs/roadmaps/unified_equilibrium_core_algorithm.md`:

- The final equilibrium core is one residual-based constrained NLP, not a family of disconnected route solvers.
- Route differences are represented by route-owned variableizations plus selectors/masks over a master residual stack and a master hard-constraint stack:
  - `r_p(u) = S_p r_bar(u)`
  - `c_p(u) = H_p c_bar(u)`
- The activation matrix is supposed to define which problem-family features are active: direct transfer, reaction equilibrium, conservation basis, phase charge, split variables, stability prelayer, postsolve certification, residual families, constraint families, and derivative requirements.
- Gibbs-style minimization may be used as a soft-start, feasibility, pretreatment, or globalization layer, but it is not the final simultaneous residual-core truth condition.
- Final certification must be tied to active residuals, active hard constraints, exact derivative coverage, density/closure diagnostics, and stability/certification checks.

Current implementation status that the next agent must treat as a gap, not as completion:

- `src/epcsaft/native/equilibrium/core/nlp_problem.h` provides a shared `NlpProblem` ABI for Ipopt callbacks.
- `src/epcsaft/native/equilibrium/core/second_order.h` provides shared second-order carriers, including `ResidualSecondOrderData`, `residual_quadratic_objective_second_order`, and `LagrangianHessianAssembler`.
- `src/epcsaft/native/equilibrium/core/activation_matrix.h` declares the problem-family activation metadata and currently marks only `bubble_dew_derived_routes` as production-exposed.
- The activation matrix is exposed through `_core._native_equilibrium_activation_matrix()` and tested as metadata.
- However, the activation matrix does not currently drive route construction, variable-model selection, residual-family activation, hard-constraint activation, seed recipes, or production capability truth end-to-end.
- Current route assembly still lives in separate concrete `NlpProblem` classes, including but not limited to:
  - `LiquidRootElectrolyteLleProblem` in `src/epcsaft/native/equilibrium/workflows.cpp`;
  - `NeutralTwoPhaseEosProblem` and `ReactiveTwoPhaseEosProblem` in `src/epcsaft/native/equilibrium/routes/route_builders.cpp`;
  - `NeutralFixedTemperaturePressureProblem` and `NeutralFixedPressureTemperatureProblem` in `src/epcsaft/native/equilibrium/routes/derived/bubble_dew.cpp`;
  - `NonidealSpeciationResidualProblem` and `IdealSpeciationProblem` in `src/epcsaft/native/equilibrium/routes/reactive/`;
  - `ReactiveLiquidRootTwoPhaseProblem` in `src/epcsaft/native/equilibrium/routes/reactive/phase_equilibrium_problem.cpp`;
  - `StabilityTpdProblem` in `src/epcsaft/native/equilibrium/routes/stability/stability_route_builders.cpp`.
- Some route code uses the shared residual-quadratic second-order helper, but the package does not yet have one canonical `r_bar/c_bar` residual/constraint representation selected by the activation matrix.
- Gibbs behavior is fragmented:
  - ideal speciation uses a reduced Gibbs objective as its route objective;
  - electrolyte LLE records a Gibbs proxy/diagnostic;
  - many routes use deterministic seed sweeps and continuation warm starts;
  - the Ipopt adapter supports warm-start inputs;
  - there is not yet a shared roadmap-style pretreatment ladder that runs homogeneous chemistry/Gibbs-style seeds, stability/split detection, relaxed polish, lift into true-species state, continuation residual solve, and final exact-route solve with seed penalty removed.

Implementation implication:

- Before adding new route families, new route tests, or broader paper-validation tests, the next agent must first decide and implement how the activation matrix becomes the native source of truth for route assembly and capability exposure.
- If a full selector-driven master residual stack is too large for this follow-up, the GoalBuddy board must record the explicit blocker and still add guard tests that prevent new route families from being exposed as production through route-local ad hoc logic.
- The trusted hydrocarbon bubble/IPOPT exact-Hessian route remains the tracer bullet; it should be routed through the cleaned facade/activation/capability path without changing its numerical behavior.

## Non-Negotiable Completion Gates

Every gate below must be represented as a GoalBuddy task or subtask. A green test suite alone is not completion.

### Gate 1: GoalBuddy Board Exists Before Implementation

Required outcome:

- `docs/goals/native-topology-activation-matrix-completion/goal.md` exists.
- `docs/goals/native-topology-activation-matrix-completion/state.yaml` exists and is v2 shape.
- Local live board is selected unless board launch fails.
- GoalBuddy checker passes.
- Board contains tasks for every gate in this document.

Required checker:

```powershell
$goalBuddyChecker = & C:\Users\Tanner\Documents\git\codex-maintenance\scripts\resolve-goalbuddy-skill-path.ps1 -RelativePath "scripts\check-goal-state.mjs"
node $goalBuddyChecker docs/goals/native-topology-activation-matrix-completion/state.yaml
```

Failure condition:

- If implementation files are edited before the board exists and passes the checker, the run has already violated this handoff.

### Gate 2: Binding Seam Is Actually Shrunk

Current bad state:

- `src/epcsaft/native/bindings/module.cpp` includes headers like:
  - `equilibrium/blocks/association_block.h`
  - `equilibrium/blocks/electrolyte_block.h`
  - `equilibrium/blocks/eos_phase_block.h`
  - `equilibrium/blocks/gibbs_blocks.h`
  - `equilibrium/blocks/reaction_block.h`
  - `equilibrium/solvers/ipopt_adapter.h`
  - `equilibrium/core/second_order.h`
  - `equilibrium/routes/route_builders.h`
  - `equilibrium/routes/stability/stability_route_builders.h`
  - `equilibrium/routes/reactive/chemical_equilibrium.h`

Required outcome:

- `src/epcsaft/native/bindings/module.cpp` becomes a thin module entrypoint.
- Files under `src/epcsaft/native/bindings/` may include pybind11, standard headers, `model/native_types.h`, and narrow domain facade registration headers.
- Files under `src/epcsaft/native/bindings/` must not directly include route blocks, route builders, Ipopt adapter, second-order assembly, NLP problem internals, or route-family internals.
- Any private diagnostic bindings that need route internals must call narrow domain-owned facade functions. Those facade functions should live under the owning domain, for example `native/equilibrium/diagnostics_facade.*` or a similarly named domain facade, not as direct route/block includes in `native/bindings`.
- The trusted neutral bubble-pressure route must still bind and solve through `_core`.

Recommended implementation shape:

- Keep `native/bindings/module.cpp` as the `PYBIND11_MODULE` owner.
- Add binding registration units only if needed, such as:
  - `src/epcsaft/native/bindings/runtime_bindings.cpp/.h`
  - `src/epcsaft/native/bindings/state_bindings.cpp/.h`
  - `src/epcsaft/native/bindings/equilibrium_bindings.cpp/.h`
  - `src/epcsaft/native/bindings/regression_bindings.cpp/.h`
- If `equilibrium_bindings.cpp` would need route internals, introduce an equilibrium-owned facade first. Binding code should include the facade header, not the route internals.

Required guard test:

- Add or strengthen a test in `tests/workflows/repo/test_project_structure.py` that fails if any file under `src/epcsaft/native/bindings/` contains these include tokens:
  - `equilibrium/blocks/`
  - `equilibrium/solvers/`
  - `equilibrium/core/second_order`
  - `equilibrium/core/nlp_problem`
  - `equilibrium/core/route_campaign`
  - `equilibrium/routes/route_builders`
  - `equilibrium/routes/stability/`
  - `equilibrium/routes/reactive/`

Required proof:

```powershell
uv run python run_pytest.py tests/workflows/repo/test_project_structure.py -q
uv run python run_pytest.py tests/native/equilibrium/routes/neutral/test_bubble_dew.py --allow-long-native-tests -q
```

Failure condition:

- If `native/bindings` still directly includes any forbidden route/block/solver header, this gate is not complete.

### Gate 3: Equilibrium Facade Does Not Leak Route Internals

Current bad state:

- `src/epcsaft/native/equilibrium/facade.h` includes `equilibrium/routes/route_builders.h`.
- `facade.h` exposes many `epcsaft::native::equilibrium_nlp::*` result types directly.

Required outcome:

- `facade.h` exposes only stable facade-level types or intentionally narrow domain facade declarations.
- If internal result types cannot be removed in one slice, add a transitional facade header with a TODO is not enough. The board must record exactly which exposed type remains, why it remains, and what guard prevents further leakage. The preferred finish is no route-builder include from `facade.h`.
- Route builders, route metadata, NLP problem types, and Ipopt adapter types stay inside `native/equilibrium/core`, `routes`, `solvers`, `blocks`, or domain implementation files.

Required guard test:

- Add a test that fails if `src/epcsaft/native/equilibrium/facade.h` includes:
  - `equilibrium/routes/route_builders.h`
  - `equilibrium/blocks/`
  - `equilibrium/solvers/`
  - `equilibrium/core/second_order`
  - `equilibrium/core/nlp_problem`
  - `equilibrium/core/route_campaign`

Required proof:

```powershell
uv run python run_pytest.py tests/workflows/repo/test_project_structure.py -q
uv run python scripts/dev/build_epcsaft.py --build-only --parallel 10
```

Failure condition:

- If `facade.h` still includes route builders or solver/block internals without an explicit accepted blocker on the board, this gate is not complete.

### Gate 4: Native Activation Matrix Drives Runtime Capability Truth

Current bad state:

- `src/epcsaft/native/equilibrium/core/activation_matrix.h` says only `bubble_dew_derived_routes` is `production_exposed`.
- `src/epcsaft/runtime/capability_evidence.py` still independently registers route evidence for reactive speciation, electrolyte LLE, neutral bubble/dew, and other route families.
- `src/epcsaft/runtime/core.py` builds runtime capability output from the Python registry, not from native activation metadata.

Required outcome:

- Native activation metadata is the source of truth for production exposure.
- Python runtime capabilities either:
  - read `_core._native_equilibrium_activation_matrix()` when `_core` is available; or
  - use a generated/static mirror that is tested byte-for-byte/key-for-key against native metadata when `_core` is available.
- `epcsaft.capabilities()` exposes an activation-matrix section, for example:
  - `capabilities()["equilibrium"]["activation_matrix"]["source"]`
  - `capabilities()["equilibrium"]["activation_matrix"]["rows"]`
  - `capabilities()["equilibrium"]["production_families"]`
  - `capabilities()["equilibrium"]["declared_not_exposed_families"]`
- Production capability claims must be derived from or checked against `production_exposed` rows.
- Unproven families may be listed as internal, experimental, planned, or declared-not-exposed, but must not be marked production.
- The trusted public proof remains `Equilibrium.bubble_pressure` through the hydrocarbon bubble/IPOPT exact-Hessian route.

Required tests:

- Add or update a native/runtime contract test that imports `epcsaft.capabilities()` and `_core._native_equilibrium_activation_matrix()` and asserts:
  - runtime activation rows match native activation rows for keys and `production_exposed`;
  - `production_families == ["bubble_dew_derived_routes"]`;
  - every non-production native row is absent from production capability claims;
  - `Equilibrium.bubble_pressure` remains associated with the production bubble/dew row;
  - no capability evidence row can say `classification == "production_supported"` for a non-production native activation family unless the board records a deliberate renamed mapping and a test enforces that mapping.

Required proof:

```powershell
uv run python run_pytest.py tests/native/equilibrium/diagnostics tests/native/contracts -q
uv run python run_pytest.py tests/native/equilibrium/blocks/test_ipopt_adapter_contract.py -q
uv run python scripts/dev/validate_project.py quick
```

Failure condition:

- If runtime capabilities can drift from native activation metadata without a failing test, this gate is not complete.

### Gate 4A: Activation Matrix Drives Equilibrium-Core Assembly Decisions

Current bad state:

- The activation matrix is present as native metadata, but route construction still primarily occurs through route-specific `NlpProblem` classes.
- The current code has a shared `NlpProblem` callback ABI and shared second-order helpers, but not a canonical master residual/hard-constraint stack selected by activation-matrix rows.
- Existing route tests can pass while new route families remain ad hoc, disconnected from the roadmap's `S_p r_bar(u)` and `H_p c_bar(u)` selector model.
- Gibbs-style behavior is not a shared pretreatment/globalization ladder; it is split across ideal speciation objectives, Gibbs proxy diagnostics, deterministic seed sweeps, and Ipopt continuation warm starts.

Required outcome:

- Add a read-only gap-audit note before implementation that maps every current equilibrium route to:
  - activation matrix family key;
  - variable model;
  - density backend;
  - active residual families;
  - active hard-constraint families;
  - seed or warm-start strategy;
  - Hessian mode and derivative coverage;
  - production exposure status.
- Implement or explicitly block the first architecture slice that makes activation metadata drive route assembly decisions rather than merely describing them after the fact.
- At minimum, production-exposed route construction must be checked against its activation row before solve dispatch, and the trusted bubble/dew route must fail loudly if its route metadata diverges from the activation matrix.
- New route-family tests must not be added as production proof until the route family is connected to the activation/capability contract and declared production-exposed in native metadata.
- The board must state whether the follow-up implements the full selector-driven `r_bar/c_bar` core or a guarded intermediate where current route-specific `NlpProblem` classes remain but are constrained by activation metadata.
- Gibbs-style warm starts must be documented as one of:
  - not implemented for the route;
  - seed/continuation only;
  - diagnostic proxy only;
  - actual Gibbs objective route;
  - shared pretreatment layer.
  The final accepted production route must still certify the simultaneous residual/hard-constraint truth conditions.

Required guard tests:

- Add or strengthen native equilibrium diagnostics/contract tests that assert production route metadata matches the activation matrix for:
  - `variable_model`;
  - `density_backend`;
  - residual-family names and order;
  - hard-constraint-family names and order;
  - `production_exposed`;
  - proof-route identifier.
- Add a guard that fails if a route capability is marked production without a matching production-exposed activation row.
- Add a guard that fails if a new production route family is introduced without declaring its activation metadata and diagnostics.

Required proof:

```powershell
uv run python run_pytest.py tests/native/equilibrium/diagnostics tests/native/contracts -q
uv run python run_pytest.py tests/native/equilibrium/routes/neutral/test_bubble_dew.py --allow-long-native-tests -q
uv run python scripts/dev/validate_project.py quick
```

Failure condition:

- If route-specific classes can bypass activation metadata and still appear as production-supported, this gate is not complete.
- If the final report implies the package has the unified residual selector core when only metadata checks were added, this gate is not complete.

### Gate 5: CMake And Source Topology Guards Stay Strict

Required outcome:

- Root native implementation files remain absent.
- `src/epcsaft/bindings.cpp` remains absent.
- `src/epcsaft/native/equilibrium_nlp`, `src/epcsaft/native/cppad`, and `src/epcsaft/native/contributions` remain absent.
- CMake continues to use explicit source lists grouped by model/EOS/autodiff/equilibrium/regression/bindings.
- No broad native implementation globs are reintroduced.

Required proof:

```powershell
uv run python run_pytest.py tests/workflows/repo/test_project_structure.py -q
uv run python run_pytest.py tests/workflows/build/test_build_epcsaft.py::test_package_and_dev_defaults_require_ceres_and_cppad -q
```

Failure condition:

- If a new compatibility directory, forwarding C++ file, broad glob, or root native implementation file appears, this gate is not complete.

### Gate 6: Trusted Hydrocarbon Bubble/IPOPT Exact-Hessian Route Is Preserved

Required outcome:

- The trusted route remains behavior-preserving.
- `hessian_mode="auto"` still selects exact Hessian when available.
- `hessian_mode="exact"` still fails loudly if exact Hessian is unavailable.
- Bubble route metadata families stay in the same order:
  - residuals: `fixed_composition`, `phase_amount_total`, `phase_pressure_consistency`, `phase_equilibrium`, `phase_distance`
  - constraints: `fixed_composition`, `phase_amount_total`, `phase_pressure_consistency`, `phase_equilibrium`, `phase_volume_gap`
- `solver_feasible_point` remains in the neutral bubble payload.

Required proof:

```powershell
uv run python run_pytest.py tests/native/equilibrium/routes/neutral/test_bubble_dew.py --allow-long-native-tests -q
uv run python run_pytest.py tests/native/equilibrium/blocks/test_ipopt_adapter_contract.py -q
uv run python run_pytest.py tests/api/frontend/test_equilibrium.py::test_equilibrium_bubble_pressure_uses_trusted_cppad_ipopt_route -q
```

Failure condition:

- If this route regresses numerically or loses exact-Hessian diagnostics, stop. Do not tune scaling, variables, constraints, or convergence behavior unless a separate board task explicitly validates that change.

### Gate 7: State And Regression Moved Internals Still Work

Required outcome:

- Native state/EOS moved files still pass focused state tests.
- Native regression moved files still pass focused regression tests.
- No analytic/user-selectable fallback is introduced.

Required proof:

```powershell
uv run python run_pytest.py tests/native/state tests/native/regression -q
```

Failure condition:

- Any failure here must be diagnosed as a moved-include/link/API issue first, not hidden by broad test deletion or fallback flags.

### Gate 8: Docs And Traceability Are Current

Required outcome:

- `docs/pages/native_debugging.rst` accurately names the current native paths.
- `docs/roadmaps/FULL_ROADMAP.md` does not advertise removed `mixture.solve_equilibrium` or `mixture.equilibrium` public API.
- `docs/roadmaps/unified_equilibrium_core_algorithm.md` records that native activation metadata is the C++ source of truth.
- Algorithm/equation generated outputs are synced.
- Do not edit old goal-board history as if it were current source truth. Old paths in `docs/goals/**` and `docs/superpowers/**` are historical unless the active goal task explicitly updates them.

Required proof:

```powershell
uv run python scripts/docs/sync_algorithm_registry.py --check --strict-traceability
uv run python scripts/docs/sync_equation_registry.py --check --strict-traceability
rg -n "src/epcsaft/bindings\\.cpp|src/epcsaft/native/equilibrium_nlp|src/epcsaft/native/cppad|src/epcsaft/native/contributions|src/epcsaft/native/epcsaft_(ares|density|equilibrium|regression|electrolyte|core_internal|cppad_internal|parameter_setup|chemical_equilibrium|born_derivatives|state|thermo|fugcoef|activity|mu|Z)" CMakeLists.txt src tests scripts docs -g "!docs/goals/**" -g "!docs/superpowers/**" -g "!docs/.codex-journal/**" -g "!build/**"
```

The `rg` command must return no active-code/doc hits.

Failure condition:

- If active docs or scripts still point at moved native files, this gate is not complete.

### Gate 9: Independent Review Happens Before Commit

Required outcome:

- Before committing, run a review step using the requesting-code-review skill or a role-specific subagent.
- The review prompt must include:
  - baseline commit `3889de77`;
  - this handoff path;
  - all gates above;
  - exact tests run;
  - a request to find ways the work could still be only a mechanical move rather than a full architecture completion.
- Critical and important findings must be fixed before commit or explicitly recorded as blocked in GoalBuddy.

Failure condition:

- If the commit is made before this review step, the run failed the process gate.

### Gate 10: Final Validation And Commit

Required final command sequence:

```powershell
uv run python scripts/dev/build_epcsaft.py --build-only --parallel 10
uv run python run_pytest.py tests/workflows/repo/test_project_structure.py -q
uv run python run_pytest.py tests/workflows/build/test_build_epcsaft.py::test_package_and_dev_defaults_require_ceres_and_cppad -q
uv run python run_pytest.py tests/native/equilibrium/routes/neutral/test_bubble_dew.py --allow-long-native-tests -q
uv run python run_pytest.py tests/native/equilibrium/diagnostics tests/native/contracts -q
uv run python run_pytest.py tests/native/equilibrium/blocks/test_ipopt_adapter_contract.py -q
uv run python run_pytest.py tests/native/state tests/native/regression -q
uv run python scripts/docs/sync_algorithm_registry.py --check --strict-traceability
uv run python scripts/docs/sync_equation_registry.py --check --strict-traceability
uv run python scripts/dev/validate_project.py quick
$goalBuddyChecker = & C:\Users\Tanner\Documents\git\codex-maintenance\scripts\resolve-goalbuddy-skill-path.ps1 -RelativePath "scripts\check-goal-state.mjs"
node $goalBuddyChecker docs/goals/native-topology-activation-matrix-completion/state.yaml
pwsh.exe -NoProfile -ExecutionPolicy Bypass -File "$env:USERPROFILE\.codex\hooks\codex-cleanup.ps1" -RepoRoot .
git diff --check
git status --short
```

Required final state:

- Worktree clean after commit.
- Local commit exists.
- Do not push unless the user explicitly asks.

Failure condition:

- If any validation is skipped, the final response must say exactly which validation was skipped and why.

## Required GoalBuddy Task Skeleton

The next agent should create tasks at least this explicit. It may add smaller subtasks, but it must not remove or weaken these gates.

```text
T001 Read-only gap audit
Owner: PM or Scout
Mode: read-only
Scope: Compare commit 3889de77, this handoff, FULL_ROADMAP, unified_equilibrium_core_algorithm.md, current C++ includes, runtime capabilities, and tests.
Done when: a note in docs/goals/native-topology-activation-matrix-completion/notes/T001-gap-audit.md lists every current violation and maps each to a later task.

T002 Judge acceptance plan
Owner: Judge
Mode: read-only
Scope: Validate that planned tasks fully cover binding seam, facade leak, activation matrix/capabilities, tests, docs, validation, review, and commit.
Done when: state.yaml records an approved sequence and no implementation starts before approval.

T003 Binding seam contraction
Owner: Worker or PM
Allowed files: src/epcsaft/native/bindings/**, new domain facade files under src/epcsaft/native/equilibrium/** as needed, CMakeLists.txt, focused tests.
Done when: binding include guard fails before fix and passes after fix; trusted bubble route still passes.

T004 Equilibrium facade cleanup
Owner: Worker or PM
Allowed files: src/epcsaft/native/equilibrium/facade.h, domain facade implementation files, CMakeLists.txt, focused tests.
Done when: facade.h no longer includes route builders or solver/block internals, or an explicit blocker with exact residual exposure is recorded.

T005 Activation matrix capability integration
Owner: Worker or PM
Allowed files: src/epcsaft/runtime/**, src/epcsaft/native/equilibrium/core/activation_matrix.h only if metadata shape needs fields, tests/native/**, tests/api/**.
Done when: epcsaft.capabilities() reports native activation rows and production claims cannot drift from native metadata.

T005A Activation-driven equilibrium-core assembly
Owner: PM, native_solver_backend_owner, or Worker
Allowed files: src/epcsaft/native/equilibrium/**, src/epcsaft/runtime/**, tests/native/equilibrium/**, tests/native/contracts/**, docs/goals/native-topology-activation-matrix-completion/notes/**
Done when: every production route is checked against the activation matrix before solve dispatch, new production exposure cannot bypass activation metadata, and the board records whether the full selector-driven `r_bar/c_bar` core was implemented or which exact blocker keeps the guarded intermediate in place.

T006 Topology and docs guard hardening
Owner: Worker or PM
Allowed files: tests/workflows/**, docs/pages/native_debugging.rst, docs/roadmaps/**, docs/latex/algorithms.tex, generated registry outputs.
Done when: stale active path scan is clean and registry checks pass.

T007 Focused runtime proof
Owner: PM or command_runner
Mode: validation
Done when: all validation commands listed in Gate 10 pass.

T008 Independent review
Owner: reviewer subagent or requesting-code-review skill
Mode: review
Done when: findings are fixed or explicitly blocked with evidence.

T009 Final commit
Owner: PM
Done when: cleanup hook passes, git diff --check passes, commit exists, worktree is clean.
```

## Explicit Non-Goals

- Do not rework solver scaling, route variables, constraints, continuation, or Ipopt convergence behavior unless a mechanical facade split requires it and the trusted bubble route proves no behavior drift.
- Do not broaden production capability claims for electrolyte/reactive routes.
- Do not add compatibility forwarding headers or root C++ files.
- Do not run broad paper-validation suites as completion proof.
- Do not delete tests to make validation pass.
- Do not push unless the user asks.

## Evidence From The Previous Commit

Commands that passed after `3889de77`:

```powershell
uv run python run_pytest.py tests/workflows/repo/test_project_structure.py -q
uv run python run_pytest.py tests/native/equilibrium/routes/neutral/test_bubble_dew.py --allow-long-native-tests -q
uv run python run_pytest.py tests/native/equilibrium/diagnostics tests/native/contracts -q
uv run python run_pytest.py tests/native/state tests/native/regression -q
uv run python scripts/docs/sync_algorithm_registry.py --check --strict-traceability
uv run python scripts/docs/sync_equation_registry.py --check --strict-traceability
uv run python scripts/dev/validate_project.py quick
$goalBuddyChecker = & C:\Users\Tanner\Documents\git\codex-maintenance\scripts\resolve-goalbuddy-skill-path.ps1 -RelativePath "scripts\check-goal-state.mjs"
node $goalBuddyChecker docs/goals/unified-equilibrium-roadmap-implementation/state.yaml
pwsh.exe -NoProfile -ExecutionPolicy Bypass -File "$env:USERPROFILE\.codex\hooks\codex-cleanup.ps1" -RepoRoot .
```

Do not treat this evidence as enough for the follow-up. It proves the move did not break the known focused paths. It does not prove the binding seam, facade boundary, or activation/capability source-of-truth gates.

## Final Response Requirements For The Next Agent

The final response after the follow-up must state:

- GoalBuddy board path and checker result.
- Whether each gate passed.
- Commit hash.
- Exact validation commands run.
- Any skipped validation.
- Whether the worktree is clean.

If any gate is not complete, the final response must say "not fully satisfactory" and list the blocker.
