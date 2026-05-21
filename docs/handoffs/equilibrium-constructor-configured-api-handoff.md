# Constructor-Configured Equilibrium API Handoff

Created: 2026-05-21

This handoff is for a fresh Codex implementation thread working from
`C:\Users\Tanner\Documents\git\ePC-SAFT` on branch `ipopt`.

The task is a breaking frontend equilibrium API reset. The implementation must
make `Equilibrium` behave like `State`: construct the configured thermodynamic
problem first, then call methods on that configured object.

This document is intentionally strict. The goal is not just to describe the API
shape; it is to add enough friction that the next agent cannot silently take a
plausible but wrong shortcut.

## Core Friction Rule

The model problem is not intelligence; it is insufficient friction before action.
The way to "fix" me is to force those friction points into the repo
instructions, tests, and GoalBuddy gates so I cannot silently take the
plausible-but-wrong shortcut.

Implementation implication:

- If a decision or action seems unclear, stop and ask for clarification.
- Do not implement a compatibility bridge, wrapper, hidden alias, broad
  fallback, fake placeholder, or route-specific patch just to make a test pass.
- If a required gate cannot be satisfied cleanly, mark the GoalBuddy task
  blocked with evidence and ask before proceeding.

## Copy-Paste Prompt For The New Thread

Paste this into a new Codex thread from `C:\Users\Tanner\Documents\git\ePC-SAFT`:

```text
Implement docs/handoffs/equilibrium-constructor-configured-api-handoff.md exactly.

Start by reading:
- docs/.codex-journal/user_preferences.md
- docs/roadmaps/FULL_ROADMAP.md
- docs/roadmaps/unified_equilibrium_core_algorithm.md
- C:\Users\Tanner\.codex\GOALBUDDY.md

Use skills:
- goalbuddy:goal-prep
- chemical-engineer
- tdd
- jetbrains if semantic tracing helps

Use owner agents where useful:
- python_api_test_owner
- native_solver_backend_owner
- build_packaging_owner
- command_runner

First implementation action:
Create and validate the GoalBuddy board at
docs/goals/equilibrium-setup-workflow/state.yaml.

Do not edit implementation files until the GoalBuddy board exists, passes the
GoalBuddy checker, and contains explicit tasks for every gate in this handoff.

This is a hard breaking API change. Do not add wrappers, aliases, deprecated
bridges, compatibility forwarding, direct route-specific public methods, broad
kwargs, fake initialize(), or Python-owned solver/route shortcuts.

If any required action is ambiguous, stop and ask for clarification instead of
guessing.
```

## Final Locked Public API

The target user workflow is:

```python
import numpy as np
from epcsaft import Equilibrium, Mixture

mixture = Mixture(parameters)

equilibrium = Equilibrium(
    mixture,
    route="bubble_pressure",
    T=233.15,
    x=np.asarray([0.1, 0.3, 0.6]),
)

structure = equilibrium.structure()

result = equilibrium.solve(
    solver_options={
        "max_iterations": 200,
        "tolerance": 1.0e-8,
    }
)

liquid = result.phases["liquid"]
vapor = result.phases["vapor"]

P = result.pressure
y = result.y
rho_liq = liquid.density
rho_vap = vapor.density
diagnostics = result.diagnostics
```

Required public behavior:

- `Equilibrium(...)` requires `mixture` plus a route and that route's fixed
  thermodynamic specification.
- `Equilibrium(...)` constructor owns problem specification only.
- `Equilibrium.solve(...)` executes the already configured problem.
- Solver controls live on `solve(solver_options=...)`, not in the constructor.
- `solver_options` accepts a dict or a public `EquilibriumSolverOptions`
  dataclass.
- Normal user examples should still require only
  `from epcsaft import Equilibrium, Mixture`; helper types such as
  `EquilibriumSolverOptions` are advanced/discoverability surfaces, not objects
  a new user must import to solve a route.
- `equilibrium.problem` exposes read-only advanced metadata.
- `equilibrium.structure()` returns a programmatic immutable object with
  `.to_dict()`.
- `result.phases` is an immutable mapping keyed by `"liquid"` and `"vapor"`.
- Public phase labels are `"liquid"` and `"vapor"`.
- Result helpers include:
  - `result.pressure`
  - `result.temperature`
  - `result.x`
  - `result.y`
  - `result.z` only for feed routes such as `flash`
  - `result.liquid_fraction`
  - `result.vapor_fraction`
- Capabilities list public route names only, not method-call strings.

Current production routes remain:

| Constructor route | Required inputs | Forbidden inputs | Composition role | Selector route | Activation key |
| --- | --- | --- | --- | --- | --- |
| `bubble_pressure` | `T`, `x` | `P`, `y`, `z` | liquid | `bubble_pressure` | `bubble_dew_derived_routes` |
| `bubble_temperature` | `P`, `x` | `T`, `y`, `z` | liquid | `bubble_temperature` | `bubble_dew_derived_routes` |
| `dew_pressure` | `T`, `y` | `P`, `x`, `z` | vapor | `dew_pressure` | `bubble_dew_derived_routes` |
| `dew_temperature` | `P`, `y` | `T`, `x`, `z` | vapor | `dew_temperature` | `bubble_dew_derived_routes` |
| `flash` | `T`, `P`, `z` | `x`, `y` | feed | `neutral_tp_flash` | `neutral_tp_flash` |

## Explicitly Rejected Designs

Do not implement any of these:

- Builder DSL:
  `eq.problem("bubble_pressure").at_temperature(...).with_liquid_composition(...)`
- `equilibrium.setup(...)`
- Empty `Equilibrium(mixture)` object.
- Old direct public solve:
  `Equilibrium(mixture).solve(route="bubble_pressure", T=..., x=...)`
- Compatibility wrapper that forwards the old direct solve into the new
  constructor-configured path.
- Route-specific public wrappers such as `bubble_pressure()`, `flash()`,
  `bubble_temperature()`, or `dew_pressure()`.
- Fake `initialize()`.
- Broad `**kwargs`, `route_options`, `problem_options`, or future placeholder
  fields to avoid future API work.
- Python-owned backend selection or Python-owned alternate solve loops.
- Direct native route entrypoints or pybind route-specific public methods.

## Current Owner Files To Prove Before Editing

The first GoalBuddy implementation task after board creation must be read-only
owner-file proof. The next agent must inspect these actual files and record a
receipt before implementation edits:

- Public equilibrium frontend owner:
  `src/epcsaft/frontend/equilibrium.py`
- Python selector dispatch and route-spec owner:
  `src/epcsaft/equilibrium/workflows.py`
- Public result shape owner:
  `src/epcsaft/equilibrium/workflows.py`
- Native selector owner:
  `src/epcsaft/native/equilibrium/core/selector_core.cpp`
- Capability evidence owner:
  `src/epcsaft/runtime/capability_evidence.py`
- Capability payload owner:
  `src/epcsaft/runtime/core.py`
- Public frontend tests:
  `tests/api/frontend/test_equilibrium.py`
- Activation/capability tests:
  `tests/native/contracts/test_equilibrium_activation_capabilities.py`
- Project structure guard tests:
  `tests/workflows/repo/test_project_structure.py`
- Reference result proof:
  `tests/native/equilibrium/results/test_neutral_vle_reference_values.py`
- Active roadmaps/docs:
  `docs/roadmaps/FULL_ROADMAP.md`,
  `docs/roadmaps/unified_equilibrium_core_algorithm.md`,
  `docs/pages/api_reference.rst`,
  `docs/pages/equilibrium_cookbook.rst`,
  `docs/pages/equilibrium_architecture.rst`,
  `docs/pages/diagnostics.rst`,
  `docs/pages/downstream_local_installs.rst`

Known stale fact at handoff creation:

- `FULL_ROADMAP.md` and `unified_equilibrium_core_algorithm.md` still describe
  direct `Equilibrium(mixture).solve(route=..., ...)` as current public API.
  The implementation must update them.

## GoalBuddy Gate

The next implementation thread must create the GoalBuddy board first.

Goal title:

`Constructor-Configured Equilibrium API`

Goal slug:

`equilibrium-setup-workflow`

Required files:

- `docs/goals/equilibrium-setup-workflow/goal.md`
- `docs/goals/equilibrium-setup-workflow/state.yaml`
- `docs/goals/equilibrium-setup-workflow/notes/`

Required commands:

```powershell
$goalBuddyChecker = & C:\Users\Tanner\Documents\git\codex-maintenance\scripts\resolve-goalbuddy-skill-path.ps1 -RelativePath "scripts\check-goal-state.mjs"
node $goalBuddyChecker docs/goals/equilibrium-setup-workflow/state.yaml
```

Local visual board should be attempted by default:

```powershell
& C:\Users\Tanner\Documents\git\codex-maintenance\scripts\start-goalbuddy-board.ps1 -Goal docs/goals/equilibrium-setup-workflow
```

Failure condition:

- If implementation files are edited before the board exists and passes the
  checker, the run has violated this handoff.

The board must contain explicit tasks for:

1. GoalBuddy board creation, checker proof, and local live-board attempt.
2. Owner-file proof before edits.
3. Route/spec matrix for all five VLE routes under the new constructor API.
4. Frontend contract tests before implementation.
5. Result-shape tests before implementation.
6. Structure/capability/docs tests before cleanup.
7. Implementation without wrappers or fake fallbacks.
8. Stale temporary docs/handoffs/goals removal or roadmap/doc update.
9. Owner-agent review.
10. Full confidence validation.
11. Logical local commits.
12. Push branch `ipopt`.

## Contract-Test-First Gates

### Gate 1: Constructor API Contracts Fail First

Before editing implementation code, add tests that fail until the API is
changed:

- `Equilibrium(mixture, route="bubble_pressure", T=..., x=...).solve(...)`
  solves the hydrocarbon reference point.
- Same constructor-configured pattern works for:
  - `bubble_pressure`
  - `bubble_temperature`
  - `dew_pressure`
  - `dew_temperature`
  - `flash`
- `Equilibrium(mixture)` without a route fails.
- Route-specific required/forbidden inputs are enforced at construction.
- Solver options passed to the constructor fail.
- Solver options passed to `solve(solver_options=...)` are accepted.

### Gate 2: Old Direct Solve Dies

Add negative tests proving:

- `Equilibrium(mixture).solve(route="bubble_pressure", T=..., x=...)` is not a
  supported public workflow.
- `solve()` does not accept `route`, `T`, `P`, `x`, `y`, or `z`.
- No compatibility wrapper forwards old direct-solve kwargs into the new path.
- Docs and capability strings no longer advertise direct `solve(route=...)`.

The old call shape may fail by normal Python signature/type validation. Do not
add a compatibility wrapper merely to raise a custom migration message.

### Gate 3: Result Shape Contracts Fail First

Add tests proving:

- `result.phases["liquid"]` works.
- `result.phases["vapor"]` works.
- `result.phases[0]` and `result.phases[1]` are not the public API.
- `result.phase_labels` returns `["liquid", "vapor"]`.
- `result.pressure` and `result.temperature` report common phase values.
- `result.x` is the liquid composition.
- `result.y` is the vapor composition.
- `result.z` exists only for feed routes such as `flash`.
- `result.liquid_fraction` and `result.vapor_fraction` match phase fractions.

### Gate 4: Structure Contracts Fail First

Add tests proving:

- `equilibrium.problem` is read-only public metadata.
- `equilibrium.structure()` returns a programmatic immutable object.
- `structure().to_dict()` includes:
  - route
  - selector route
  - knowns
  - unknowns
  - composition role
  - activation key
  - residual families
  - hard-constraint families
  - expected phase keys
  - DOF only if generally owned and available
- If DOF is not generally owned, the structure result reports unavailable DOF
  explicitly instead of inventing a route-local count.

### Gate 5: Initialization Is Real Or Absent

Do not add `initialize()` unless native selector initialization evidence is
cleanly available without a one-off wrapper.

Allowed only if real:

- `equilibrium.initialize(...)` prepares/reports native-owned seed,
  scaling, and warm-start evidence for the configured problem.
- It may accept validated guesses, scaling, and warm-start controls.
- It must reject raw native variable vectors unless the native selector owns a
  public-safe shape for them.
- Repeated `solve()` calls use the latest validated initialization state.

If any of this is not cleanly supportable, omit `initialize()` in this
implementation and record the blocker on the GoalBuddy board.

### Gate 6: Capability Strings Become Route Names

Capabilities must list public route names, not method-call strings.

Target shape:

- `capabilities()["equilibrium"]["public_routes"]` contains route names like
  `bubble_pressure`, `bubble_temperature`, `dew_pressure`, `dew_temperature`,
  `flash`.
- `capabilities()["optimizers"]["ipopt"]["public_routes"]` uses the same
  route-name convention.
- Route-family sections must not advertise old direct call strings.
- Capability evidence remains activation-matrix driven and does not overclaim
  future LLE/electrolyte/reactive/speciation routes.

### Gate 7: No Wrappers, Aliases, Or Route-Specific Public Methods

Guard tests must fail if any of these appear:

- `Equilibrium.setup`
- `Equilibrium.bubble_pressure`
- `Equilibrium.bubble_temperature`
- `Equilibrium.dew_pressure`
- `Equilibrium.dew_temperature`
- `Equilibrium.flash`
- old direct `solve(route=...)` support
- root free functions for VLE routes
- Python direct route-specific pybind calls
- public classes representing route-specific problem objects

### Gate 8: Future Extensibility Without Public Ad Hoc Fields

The implementation must leave future LLE/electrolyte/speciation routes possible
through internal route-spec metadata, not broad public escape hatches.

Required rule:

- Add current explicit constructor fields only:
  `route`, `T`, `P`, `x`, `y`, `z`, and `phase_count` if the implementation
  proves it is needed and route-safe.
- Do not add `**kwargs`, `route_options`, `problem_options`, or future
  placeholder fields.
- Do not add `phase_count` just because it appeared in planning sketches. Add
  it only if the current selector contract actually consumes it generally for
  production routes.
- If a future route would need new public fields, leave that for the route's
  implementation PR/goal and update the route-spec table then.

### Gate 9: Stale Docs And Temporary Receipts

Remove or update stale references intentionally:

- Active roadmap and docs must be updated to the constructor-configured API.
- Contradictory old GoalBuddy and handoff documents that are temporary receipts
  may be removed if they conflict with the new API direction.
- Do not delete durable roadmaps, ADRs, or source-of-truth docs merely because
  they contain stale text. Update those instead.
- If unsure whether a document is temporary receipt or durable source of truth,
  stop and ask before deleting it.

Known stale patterns to eliminate from active code/docs/tests:

- `Equilibrium(mixture).solve(route=`
- `Equilibrium.solve(route=`
- `result.phases[0]`
- `result.phases[1]`
- `Equilibrium(mixture, ...).solve(route=...)`

Exclusions must be explicit and justified if any historical archival text is
left unchanged.

## Stop-And-Ask Triggers

The next agent must stop and ask for clarification if:

- Native initialization is not cleanly exposed but an `initialize()` method seems
  desirable.
- Direct-solve compatibility seems tempting.
- A broad `**kwargs` or `route_options` field seems useful for future routes.
- `structure()` or DOF metadata is not generally owned by route-spec/native
  metadata.
- Deleting old docs/goals/handoffs could remove a non-temporary roadmap,
  decision record, or current source of truth.
- Any route would bypass the selector-owned native NLP core.
- Any fix would solve only one route by special-casing that route in the
  frontend.
- Any test can pass only by weakening architecture guards.
- Any owner-agent review says the implementation is mechanical rather than an
  architecture-complete API reset.

## Required Owner Agents

Use repo owner agents during the implementation where they can run in parallel:

- `python_api_test_owner`:
  frontend constructor API, result shape, public tests, stale direct-solve usage.
- `native_solver_backend_owner`:
  selector request shape, initialization feasibility, structure metadata, and
  no bypass of the selector-owned native NLP core.
- `build_packaging_owner`:
  public exports, package docs, capability evidence, build/package impact.
- `command_runner`:
  non-mutating validation such as focused tests, confidence validation, checker,
  cleanup, and status.

Main thread owns integration decisions, `_core` rebuild coordination, commits,
and push.

## Required Validation

At minimum, run:

```powershell
uv run python run_pytest.py tests/api/frontend/test_equilibrium.py -q
uv run python run_pytest.py tests/native/equilibrium/results/test_neutral_vle_reference_values.py -q
uv run python run_pytest.py tests/native/contracts/test_equilibrium_activation_capabilities.py -q
uv run python run_pytest.py tests/native/equilibrium/diagnostics/test_selector_core_contracts.py -q
uv run python run_pytest.py tests/native/equilibrium/blocks/test_ipopt_adapter_contract.py -q
uv run python run_pytest.py tests/workflows/repo/test_project_structure.py -q
uv run python scripts/docs/sync_algorithm_registry.py --check --strict-traceability
uv run python scripts/docs/sync_equation_registry.py --check --strict-traceability
uv run python scripts/dev/validate_project.py confidence
$goalBuddyChecker = & C:\Users\Tanner\Documents\git\codex-maintenance\scripts\resolve-goalbuddy-skill-path.ps1 -RelativePath "scripts\check-goal-state.mjs"
node $goalBuddyChecker docs/goals/equilibrium-setup-workflow/state.yaml
pwsh.exe -NoProfile -ExecutionPolicy Bypass -File "$env:USERPROFILE\.codex\hooks\codex-cleanup.ps1" -RepoRoot .
git diff --check
git status --short
```

If generated registries/docs are changed intentionally, run the generator
without `--check`, review the diff, and then rerun the strict `--check` command.

No validation may be silently skipped. If a command cannot run, record:

- exact command;
- exact failure;
- whether it is an environment blocker or implementation blocker;
- what remains unverified.

## Commit And Push Requirements

Use logical local commits where feasible:

1. GoalBuddy board and handoff/decision setup.
2. Frontend contract tests.
3. Constructor-configured API and result shape.
4. Capability/docs/stale-reference cleanup.
5. Validation or guard-test refinements.

After all gates pass:

- worktree must be clean;
- push branch `ipopt`;
- do not open a PR unless separately requested.

## Final Completion Definition

The goal is complete only when:

- GoalBuddy checker passes.
- The board records receipts for every gate above.
- The constructor-configured API is the only public equilibrium workflow.
- The old direct `solve(route=...)` public workflow is gone.
- No wrappers, aliases, or fake `initialize()` methods exist.
- The five production VLE routes still recover the hydrocarbon reference point.
- Capabilities list route names only.
- Active docs and roadmaps describe the new API.
- Contradictory temporary handoff/GoalBuddy receipts have been removed or
  explicitly superseded.
- Full confidence validation passes.
- Local commits exist.
- Branch `ipopt` is pushed.
- `git status --short` is clean.
