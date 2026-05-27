# GFPE Package Cleanup Plan

This plan translates the generalized fluid-phase equilibrium doctrine into a
package cleanup sequence. The goal is a small set of deep modules: one selector
admission layer, one shared equilibrium NLP, one Ipopt adapter, one certified
result shape, and one capability source of truth.

This document is implementation guidance. Runtime route labels and family keys
remain owned by the selector activation metadata, not by roadmap prose.

## Source Order

1. `docs/roadmaps/generalized_fluid_phase_equilibrium.md` defines the GFPE
   architecture, equations, gates, and staged production policy.
2. `docs/adr/0003-selector-core-activation-capabilities.md` makes selector
   admission and the native activation matrix the capability authority.
3. `docs/adr/0004-associating-equilibrium-architecture.md` keeps associating
   equilibrium declared-not-exposed until exact derivative support exists.
4. `docs/adr/0005-package-extension-split.md` assigns final equilibrium
   ownership to `epcsaft-equilibrium`; this cleanup plan prepares that module
   boundary before extraction.
5. `src/epcsaft/native/equilibrium/core/activation_matrix.h` is the executable
   selector-admission inventory.
6. During the monorepo transition, `epcsaft.capabilities()` mirrors that
   inventory upward for users and downstream projects. After extraction, the
   equilibrium extension owns its capability report and any aggregate view must
   be explicit and test-backed.

## Design Rules

- Public equilibrium calls enter through `Equilibrium(mixture, route=..., ...)`.
- Selector Core is the only module that decides whether a route is callable.
- Route adapters may choose a named request, but they do not own variable
  packing, scaling, transforms, derivative policy, or acceptance.
- Production equilibrium requires exact gradient, Jacobian, and Lagrangian
  Hessian support.
- Ipopt convergence is the only solve success condition. Iteration limits,
  acceptable points, tiny steps, and feasible-but-uncertified exits are failures.
- Benchmark data stores source facts and tolerances only. It must not encode
  solver decisions.
- Validation lanes are named, narrow, and registry-backed. A broad sweep is an
  opt-in diagnostic or benchmark workflow, not routine package confidence.
- Compatibility forwarders are temporary only when a public deprecation window
  exists. Internal cleanup should remove migrated wrappers.

## Module Cleanup Sequence

### 1. Selector Admission

Make `selector_core.*`, `activation_matrix.*`, and the generated Python mirror
the only callable-route inventory.

Required shape:

- each production activation row declares its admitted public routes;
- declared-not-exposed rows have no public routes;
- Python route specs map back to one admitted activation family;
- `capabilities()` reports public routes from activation metadata;
- tests fail if any public route is callable without selector admission.

Current admitted route map:

| Public route | Selector route | Activation family | Status |
| --- | --- | --- | --- |
| `bubble_pressure` | `bubble_pressure` | `bubble_dew_derived_routes` | production |
| `bubble_temperature` | `bubble_temperature` | `bubble_dew_derived_routes` | production |
| `dew_pressure` | `dew_pressure` | `bubble_dew_derived_routes` | production |
| `dew_temperature` | `dew_temperature` | `bubble_dew_derived_routes` | production |
| `flash` | `neutral_tp_flash` | `neutral_tp_flash` | production |
| `lle` | `neutral_lle` | `neutral_lle` | production |

Declared-not-exposed families stay route-ineligible until their GFPE derivative,
phase-discovery, and certification gates pass.

### 2. Shared NLP Core

Deepen the shared NLP module so route code cannot depend on internal packing.

Target interface:

- route request in physical terms;
- activation plan from selector metadata;
- `NlpProblem` with objective, constraints, sparse Jacobian, and sparse Hessian;
- `VariableLayout` for block ownership;
- `VariableTransform` for coordinate maps and chain-rule derivatives;
- residual and constraint blocks registered by contribution family.

Route code should not assemble variable vectors, scaling vectors, sparsity
patterns, or derivative callbacks directly.

### 3. Ipopt Adapter

Move scattered Ipopt behavior into `ipopt_adapter.*`.

The adapter owns:

- named option profiles;
- exact Hessian policy;
- user scaling;
- NLP-declared bounds enforced through Ipopt barrier constraints;
- acceptable-status rejection;
- iteration history capture;
- active-bound and barrier diagnostics;
- convergence and postsolve acceptance handoff.

Routes request a profile and receive a certified adapter result. They do not set
Ipopt options piecemeal.

Current ownership inventory:

- Python `EquilibriumSolverOptions` validates public numerical controls and
  passes scalar controls to the native selector binding without resolving
  adapter-owned optional tolerance defaults.
- `register_bindings.cpp` translates those public controls into
  `IpoptSolveOptions`; it does not decide route acceptance or profile defaults.
- `ipopt_adapter.*` owns profile defaults, exact Hessian gating, normalized
  Ipopt status acceptance, optional tolerance defaults, user scaling
  enforcement, scaled-to-unscaled Ipopt constraint tolerance translation,
  Ipopt barrier/bound diagnostics, and iteration-history capture.
- `two_phase_eos_route.*` and `routes/derived/bubble_dew.cpp` may provide
  route seeds and request a named profile, but must use adapter-normalized
  `IpoptSolveResult` acceptance before postsolve.
- Production route code must not accept Ipopt acceptable-point, feasible-point,
  tiny-step, iteration-limit, or finite-variable-only outputs as postsolve
  candidates.

### 4. Result Certification

Collapse route-specific postprocessing behind one certified result shape.

The result builder owns:

- native status normalization;
- solver convergence acceptance;
- postsolve certification;
- phase labels and phase payloads;
- route diagnostics;
- public `EquilibriumResult` construction.

Bubble, dew, flash, and LLE results should differ by populated fields and phase
labels, not by separate acceptance philosophies.

This result shape is an extraction seam. The future equilibrium extension
should consume provider thermodynamic evidence and own equilibrium acceptance,
certification, diagnostics, and result schemas without reaching through
private core internals.

### 5. Contribution Families

Make thermodynamic contribution families explicit modules.

Each contribution family exposes:

- residual terms;
- hard constraints, if any;
- derivative requirements;
- parameter requirements;
- activation conditions;
- production status.

Association, electrolyte, reaction, EOS phase, Born, and ionic pieces should not
activate through loose flags hidden in route code.

### 6. Benchmark And Validation Boundaries

Keep source facts separate from solver behavior.

Allowed benchmark content:

- source citation metadata;
- mixture and parameter facts;
- target values and tolerances;
- fixture identifiers;
- applicability notes.

Disallowed benchmark content:

- seed heuristics;
- Ipopt option changes;
- route fallback decisions;
- acceptance overrides;
- hardcoded solver branches.

Validation lanes should reference tests or checkers by name and explain their
contract. Temporary diagnostic scripts either become formal lanes or are removed.

### 7. Public Frontend Boundary

Keep the user API clean.

Users see:

- `Equilibrium(mixture, route=..., ...).solve()`;
- supported route labels;
- structured result objects;
- diagnostics only when requested or attached to failures.

Users do not see:

- activation-family keys as input;
- derivative backend flags;
- Ipopt internal knobs unless explicitly configuring solver options;
- native request payloads;
- roadmap family labels.

### 8. Deletion Pass

After each module boundary is migrated, delete old paths in the same change when
they are internal.

Delete or demote:

- stale wrappers that only forward to the new path;
- diagnostic entry points that are not validation lanes;
- duplicate capability registries;
- route-specific result branches that duplicate generic result handling;
- tests that encode historical implementation paths instead of current
  contracts.

## Current First Slice

This slice makes selector admission the route and capability source of truth.

Acceptance:

- every callable equilibrium route is listed in activation metadata;
- every callable route maps to exactly one selector activation family;
- declared-not-exposed families publish no route labels;
- Python route specs agree with the selector admission map;
- `capabilities()["equilibrium"]["public_routes"]` and
  `capabilities()["optimizers"]["ipopt"]["public_routes"]` derive from that map;
- the equilibrium confidence lane has one focused convergence target per
  admitted production family.

## Follow-On Slices

1. Move route-owned Ipopt option assembly into named adapter profiles.
2. Make `VariableTransform` the only coordinate-map seam used by production NLPs.
3. Replace route-specific result normalization with one certified result builder.
4. Split residual and constraint contribution families into explicit modules.
5. Formalize or delete remaining validation scripts under `scripts/validation`.
6. Remove internal forwarders after tests and docs call the new interfaces.
