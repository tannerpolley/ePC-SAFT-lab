# Deletion-First Provider And Equilibrium Simplification

Milestones: `M3 - EOS` and `M4 - Equilibrium`, with structural enforcement owned by `M0 - Governance`
Packages: `packages/epcsaft` and `packages/epcsaft-equilibrium`
Status: `approved design basis; specification recorded from the 2026-07-11 thermo-nuclear code-quality assessment`
Last reviewed: `2026-07-11`

## Context

The provider and equilibrium packages contain valuable ePC-SAFT equations,
exact-derivative machinery, density closure, phase blocks, a reusable Ipopt
adapter, and several real validation campaigns. Their main structural problem
is not lack of sophistication. It is successive accumulation: new serializers,
adapters, route-specific NLPs, validation gates, result dictionaries, and
closed research workflows were added without deleting the paths they displaced.

The result is a public API that appears narrow while traversing several layers
of duplicated policy and numerical orchestration. Provider input can be
normalized by several owners. Equilibrium activation metadata, route selection,
NLP construction, solver attempts, postsolve acceptance, capability evidence,
and Python result conversion each have overlapping representations.

This specification makes deletion—not mechanical file splitting—the governing
architecture rule. It reconciles and tightens:

- `2026-07-10-m0-characterized-ownership-and-maintainability-ratchets.md`;
- `2026-07-10-m3-eos-versioned-state-resolved-model-input.md`;
- `2026-07-10-m4-equilibrium-canonical-owner-decomposition.md`;
- ADR 0002, ADR 0003, ADR 0004, and ADR 0005.

Where an earlier decomposition document permits moving the same behavior into
new owners, this specification adds a stronger requirement: the cutover must
delete a duplicated decision, serialization path, solver path, binding, or
runtime validation campaign. Smaller files without fewer concepts are not a
successful outcome.

## Verified Baseline

Measurements on `main` at `c00ee92a` found:

| Area | Files | Source lines | Main concentration |
| --- | ---: | ---: | --- |
| Provider | 77 | 18,669 | model and state Python boundary |
| Equilibrium | 75 | 36,452 | native core, derived routes, bindings, workflows |
| Combined | 152 | 55,121 | overlapping input, route, solver, and result owners |

The provider had three source files above 1,000 lines and eleven above 500
lines. The principal owners were `model/datasets.py`,
`state/native_adapter.py`, and `model/parameters.py`.

Equilibrium had six source files above 1,000 lines and eighteen above 500
lines. Its three largest C++ files contained 16,086 lines, approximately 44%
of all equilibrium source:

- `native/equilibrium/core/two_phase_eos_route.cpp`: 6,596 lines;
- `native/equilibrium/routes/derived/bubble_dew.cpp`: 4,984 lines;
- `native/equilibrium/register_bindings.cpp`: 4,506 lines.

Equilibrium source grew from 18,339 lines on 2026-06-01 to 36,452 lines at the
design snapshot. That growth was concentrated in electrolyte, phase-discovery,
chemical-equilibrium, paper-validation, binding, and diagnostic additions.

The paused Task 9 core commits changed provider source by 9,711 insertions and
4,787 deletions, a net increase of 4,924 lines. They created several new files
near or above 1,000 lines. Those measurements do not invalidate the scientific
records or tests on the branch; they invalidate wholesale adoption of its
architecture.

## Problem Statement

### Provider

At least four owners serialize or normalize overlapping parts of the model:

- `ParameterSet.to_runtime_dict()`;
- `Mixture._runtime_payload`;
- dataset runtime option and condition resolution;
- `state/native_payload.create_struct()`.

The internal `ePCSAFTMixture` and `ePCSAFTState` adapters then form a parallel
API underneath the public `Mixture` and `State` objects. Writable `NativeArgs`
fields expose the entire loose native payload, and derivative calls can rebuild
native arguments from Python dictionaries.

Scientific correlations may also be evaluated while loading a dataset, before
the actual state temperature and composition exist. This confuses parameter
records, formulation choices, and state conditions.

### Equilibrium

The public route appears to be activation-matrix driven, but exposed saturation
routes use route-specific contract and solver switches rather than the generic
activation compiler. The production extension contains multiple NLP classes,
many direct Ipopt call sites, repeated seed-attempt loops, and callable bindings
for closed or diagnostic workflows.

Paper fixtures and source paths are embedded in Python workflows, the native
selector, derived route code, and binding validation. Native acceptance is
converted into dictionaries and then partially reconstructed by Python as a
second policy engine.

## Goals

1. Establish exactly one provider model-definition and native-serialization
   owner.
2. Resolve temperature- and composition-dependent scientific records exactly
   once at state conditions.
3. Make the provider/equilibrium boundary an immutable typed native handle plus
   detached receipt, never a loose dictionary or private adapter.
4. Make native activation metadata the sole route and topology authority.
5. Compile each admitted equilibrium request into one typed production NLP
   specification.
6. Route all admitted solves through one common attempt policy, exact Ipopt
   adapter, postsolve owner, and typed result.
7. Remove paper-specific numerical tables, source paths, and validation programs
   from installed runtime code.
8. Remove closed research and diagnostic bindings from the normal production
   extension.
9. Unify duplicated EOS value/derivative and density-solve orchestration.
10. Achieve material net source deletion without weakening currently proven
    numerical behavior or broadening capability claims.

## Non-Goals

- No new public equilibrium route.
- No repair of a specific Gross, Khudaida, Held, Ascani, Figiel, or other paper
  reproduction as part of the architecture cutover.
- No new regression capability.
- No replacement EOS or change to the governing ePC-SAFT equations.
- No conversion of finite sampled candidates into global phase-set proof.
- No compatibility wrapper around removed serializers, adapters, route methods,
  option files, or native bindings.
- No mechanical decomposition whose main result is more files with the same
  total decisions and call graph.
- No promise that every closed experimental implementation remains compiled or
  present in the working tree.

## Alternatives

### Split giant files while preserving every path

Rejected. This would improve navigation while retaining duplicate NLPs,
serializers, bindings, result policies, and validation programs. It treats file
size rather than ownership as the defect.

### Add a new clean layer and migrate callers gradually

Rejected as a general strategy. The repository already contains several
partially superseding layers. A new facade with long-lived fallback to the old
path would deepen the problem. Short red/green cutover work may temporarily
touch both representations in one branch, but no accepted commit retains two
production owners.

### Preserve all closed research in the production extension

Rejected. A declared-not-exposed route must not remain a permanent production
binding or hidden alternate solver path. Active research may use a separately
declared experimental target; inactive work remains recoverable from Git and
its specifications.

### Deletion-first canonical cutover

Selected. Characterize the accepted public behavior, introduce the smallest
typed owner that can replace the overlap, cut every caller over, and delete the
superseded path in the same accepted slice.

## Architectural Invariants

### Provider invariants

- `ParameterSet` owns scientific parameter and correlation records only.
- `ModelConfiguration` owns all active formulation choices and is required,
  complete, and versioned.
- `State` supplies temperature, composition, closure, and phase conditions.
- One native `NativeModelDefinition` is constructed from `ParameterSet` and
  `ModelConfiguration`.
- One resolver evaluates the definition at `T` and `x` and produces an
  immutable `ResolvedNativeInput` plus detached receipt.
- Python never constructs, mutates, or recopies raw native parameter fields.
- No payload-side formulation defaults exist.
- Unknown, missing, conflicting, or out-of-domain model input fails before EOS
  evaluation.

### Equilibrium invariants

- The native activation descriptor is the only production route/topology
  authority.
- Python owns ergonomic request construction, not activation, admission, or
  solver acceptance.
- The production API exposes no derivative-backend selection and no raw solver
  continuation state.
- All admitted routes compile into a typed `CompiledRoute`.
- All admitted solves pass through one exact-derivative Ipopt execution owner.
- Native code owns the accepted/rejected decision and required postsolve
  evidence.
- Python receives a typed result and performs no fallback certification.
- Closed families are not callable through production bindings.

### Validation invariants

- Paper fixtures, literature arrays, analysis paths, and checker commands live
  in validation data, scripts, or evidence manifests—not installed runtime
  modules.
- A validation campaign exercises the public generic API or an explicitly
  experimental target; it does not add paper identity branches to the solver.
- Scientific constants are supplied through traceable parameter records and
  receipts, never duplicated as floating-point whitelists across layers.

## Selected Provider Design

### Model-definition flow

```text
source bundle
  -> strict ParameterSet records
  + required versioned ModelConfiguration
  -> one pybind construction
  -> immutable NativeModelDefinition
  -> resolve(T, x)
  -> ResolvedNativeInput + receipt
  -> NativeState
  -> thin public State result conversion
```

`Mixture` owns the immutable model definition and component ordering. It does
not own state temperature, composition, pressure, density, or phase defaults.
It may expose a typed instance receipt, but it does not expose writable native
arguments or a loose runtime dictionary.

### Correlations

Pure-property and binary interaction correlations remain typed records until
resolution. Each record carries units, domain, source identity, functional
form, and required independent variables. The state resolver evaluates them at
the actual state conditions and records both the expression identity and
evaluated value.

Unsupported correlation forms fail at input parsing. A missing state variable
fails at resolution. No loader substitutes a nominal temperature.

### Native model policy

Flat magic integers are replaced by typed enums and cohesive formulation
records. Overlapping flags for Born, diameter, dielectric, derivative, and
bulk-mode concepts are collapsed so only the selected formulation is stored.
Derived native choices are computed once during definition validation rather
than persisted as parallel flags.

### Public state surface

Public `Mixture` owns the native definition directly. Public `State` owns or
wraps the native state directly. The internal `ePCSAFTMixture` and
`ePCSAFTState` facade pair is removed after callers migrate. Small typed result
converters may remain; method-by-method facade forwarding does not.

## Selected Equilibrium Design

### Production request flow

```text
Equilibrium constructor
  -> typed ConfiguredRoute
  -> native compile(resolved model handle, route request)
  -> CompiledRoute
  -> SaturationPressureNlp
  -> common attempt/Ipopt runner
  -> native postsolve and acceptance
  -> typed EquilibriumResult
```

The currently admitted `bubble_pressure`, `dew_pressure`, and scoped
`single_component_vle` routes share a saturation-pressure formulation. Their
differences are expressed through typed route data such as fixed phase role,
composition role, pure-component topology, and specified scalar—not separate
solver architectures or diagnostic-name branches.

### Activation descriptor

One compile-time native descriptor contains:

- route enum and public label;
- exposure status;
- fixed and solved quantities;
- composition role;
- variable topology;
- residual and constraint families;
- exact-derivative requirement;
- NLP builder;
- postsolve policy;
- compact proof-receipt identifiers.

Python may query this descriptor for capability display. It must not maintain a
handwritten route table containing the same activation, family, phase, or proof
facts.

### NLP ownership

One saturation-pressure NLP serves the exposed pressure routes. The common NLP
interface owns variables, bounds, constraints, exact Jacobian, exact Lagrangian
Hessian, scaling, and initial-point contract. Route-specific equations are
expressed as typed blocks or data, not subclasses that repeat the full solver
contract.

Closed TP flash, LLE, multiphase, electrolyte, and reactive NLPs are not part of
the normal production target until their own admission programs become active.
An actively developed formulation may live in a separately named experimental
target with no production binding or capability consequence. Inactive closed
implementations should be deleted and recovered from Git when work resumes.

### Attempt and continuation policy

One runner owns seed construction, rejected-seed evidence, continuation,
Ipopt invocation, attempt ranking, timeout, and normalized solver status. The
first cut preserves characterized seed behavior while deleting repeated route
loops. Numerical reduction of the broad pressure sweep is a later evidence-
driven change, not an assumption in this structural cutover.

### Result ownership

Native results are composed from four typed records:

1. solver diagnostics;
2. thermodynamic postsolve evidence;
3. optional discovery/certification receipt;
4. route result and phase records.

Each record is serialized once. Required fields have no fallback default.
Python converts arrays and exposes stable result properties but does not infer
acceptance, exactness, stability, or certification from optional dictionary
keys.

### Production binding surface

The production extension should expose only:

- provider SDK/ABI compatibility intake;
- activation and capability descriptor query;
- optional route contract query when required by the public API;
- one production solve entry point;
- typed result and receipt classes.

Smoke probes, paper validators, direct closed-route solvers, phase-discovery
experiments, and component diagnostics belong in native unit tests or a
separate experimental test extension.

## EOS Kernel Consolidation

### Residual and derivative assembly

The canonical scalar-templated residual implementation is recorded with CppAD
for derivative evaluation. Bespoke equation copies used only to construct a
composition-derivative route are deleted after parity tests pass. Value and
derivative paths therefore share one equation owner.

Association solved-state implicit differentiation remains explicit and exact;
the simplification does not differentiate through iterative solves or weaken
ADR 0004.

### Density closure

One density solver returns a typed report containing root, validity, phase
selection, candidates, and failure diagnostics. Scalar convenience functions
delegate to that report. A second scan/bracket/refine/selection implementation
is not retained.

## Capability And Evidence Separation

Runtime capability output reports compiled features, exposed routes,
configuration schema identities, and compact accepted proof identifiers.

Repository-only evidence—paper names, retained paths, checker commands, issue
history, and artifact freshness—is validated by M6 tooling against those
identifiers. The installed package does not contain a parallel executable
governance application for repository paths and paper campaigns.

## Deletion And Size Contract

The combined provider and equilibrium source baseline is 55,121 lines. A
credible architecture target is a net reduction of approximately 13,000 to
17,000 lines without deleting the governing EOS equations. This is a design
target, not permission to remove tests or evidence indiscriminately.

Package-specific targets are:

| Area | Expected net reduction | Primary deletion source |
| --- | ---: | --- |
| Provider | 1,600-2,500 lines | serializers, adapters, defaults, duplicate EOS/density paths, dead skeletons |
| Equilibrium Python | 2,500-3,000 lines | validation programs, duplicate policy, capability governance, mapping adapters |
| Equilibrium native | 9,000-12,000 lines | closed production scaffolding, duplicate NLP/attempt/result/binding paths |

The estimates overlap within each package and are not per-commit quotas. The
following rules are mandatory:

- every accepted structural slice has net-negative production source unless a
  reviewed scientific correctness change requires otherwise;
- no new production file may exceed 1,000 lines without an accepted ADR;
- new cohesive owners should normally remain below 700-800 lines;
- existing oversized owners may not grow and must ratchet downward when a
  slice shrinks them;
- tests, source data, and required receipts are measured separately from
  production source so deletion pressure cannot be satisfied by removing proof;
- moving code without deleting an owner overlap does not count toward the
  architecture target.

## Characterization And Testing

### Before each cutover

- build fresh native artifacts from the exact source commit;
- characterize the affected public provider or equilibrium path;
- record inputs, resolved receipt, outputs, derivatives, diagnostics, and
  expected failures;
- retain real source data and plots for any test computing literature/model
  predictions;
- confirm current activation and capability state.

### During each cutover

- begin with a failing ownership, schema, or parity test;
- introduce one canonical owner;
- cut all in-scope callers over;
- delete the displaced owner in the same accepted change;
- compare numerical results and exact derivatives against the characterized
  baseline;
- reject two-owner compatibility periods from committed production code.

### After each cutover

- run focused provider/equilibrium API and native tests;
- run derivative and receipt parity tests;
- run activation/capability equality and negative-export tests;
- run repository ownership and size ratchets;
- run documentation, lint, diff, cleanup, and Git-status checks;
- record deferred paper failures separately when they are outside the slice.

## Cutover Sequence

1. Activate the M0 ownership schema and characterize accepted public owners.
2. Salvage Task 9 tests, record types, and literature-backed correlations
   without merging its full architecture.
3. Establish `NativeModelDefinition`, state-time resolution, and the detached
   receipt.
4. Migrate public provider `Mixture` and `State`, then delete loose serializers,
   private facade ownership, payload defaults, and writable native construction.
5. Publish the provider resolved-input SDK contract and migrate equilibrium to
   the typed handle.
6. Remove paper-validation logic and closed diagnostic bindings from installed
   equilibrium runtime code.
7. Compile exposed routes through one typed saturation specification and one
   common exact Ipopt runner.
8. Replace native/Python dictionary policy reconstruction with typed results.
9. Unify provider residual derivative recording and density closure.
10. Delete obsolete skeletons, stale exports, and structure tests that protect
    empty or displaced paths.
11. Ratchet line and ownership baselines after every accepted reduction.

## Error Handling

- Missing model configuration, formulation field, source value, or state
  variable raises a typed input error before native evaluation.
- Unknown model keys and route enums are rejected; they are not ignored or
  normalized to a default.
- A provider/equilibrium SDK mismatch fails at extension intake with both
  contract identities.
- A closed route fails before NLP construction and is not reachable through a
  direct binding.
- Failed seed construction is retained in attempt evidence rather than silently
  discarded.
- Native rejection returns one typed diagnostic record; Python does not retry or
  reinterpret it.
- A numerical mismatch during structural cutover stops deletion until its cause
  is understood or separately approved as a correctness change.

## Stop Gates

- Stop if a slice creates a new facade while retaining the old production path.
- Stop if Task 9 integration increases production source without deleting the
  serializers or adapters it replaces.
- Stop if paper identity is proposed as a production solver branch.
- Stop if a closed route must remain directly Python-callable for its tests;
  move the test to a native or experimental boundary instead.
- Stop if activation, admission, exactness, or acceptance is decided in both
  C++ and Python.
- Stop if structural cleanup changes capability status implicitly.
- Stop if fresh native identity or before/after numerical characterization is
  missing.
- Stop if a file split reduces file length but not duplicate decisions,
  dependencies, or total production source.

## Risks

- **Deleting closed code loses future work.** Control: Git history, specs,
  retained tests/data, and optional explicit experimental targets preserve the
  knowledge without burdening production.
- **One generic NLP becomes an oversized framework.** Control: compose typed
  mathematical blocks and data; keep one solver contract without one giant
  implementation file.
- **Line targets encourage gaming.** Control: require owner deletion, call-graph
  simplification, characterization, and separate proof preservation.
- **Typed bindings increase C++ surface.** Control: expose only domain records
  needed across the boundary and delete dictionary converters in the same slice.
- **Seed-policy centralization changes robustness.** Control: preserve current
  characterized seeds first; optimize the policy only in a later numerical
  issue.
- **Provider resolution changes paper results.** Control: treat old early-
  resolved values as defects unless the actual state receipt proves equivalence;
  do not repair every paper in the provider slice.

## Scientific And Numerical Confidence

- **Verified:** the provider contains reusable EOS contribution and CppAD
  machinery.
- **Verified:** equilibrium contains a shared Ipopt adapter with exact-derivative
  policy.
- **Verified:** public equilibrium admission is currently narrow.
- **Verified:** multiple surrounding serialization, NLP, binding, and result
  policy paths remain.
- **Inference to prove by characterization:** the exposed pressure routes can
  share one typed saturation-pressure NLP without changing their thermodynamic
  equations.
- **Unknown until a dedicated numerical study:** how much of the broad
  multistart pressure sweep can be removed safely.

## Relationship To Existing Specifications

- The M0 ratchet specification remains authoritative for schema, baseline, and
  accountability mechanics.
- The M3 model-input specification remains authoritative for configuration,
  scientific record, receipt, and provider SDK semantics; this document adds a
  net-deletion and owner-count constraint to its implementation.
- The M4 canonical-owner specification remains authoritative for milestone
  ownership and dependency ordering; this document rejects extraction that
  merely relocates validation campaigns or parallel solver paths.
- Scientific admission specs remain authoritative for whether a closed route
  can become public. Structural simplification cannot admit it.
- M6 remains authoritative for paper evidence and retained prediction artifacts.

## Unresolved Decisions

No material architecture decision remains. The exact experimental-target
boundary, function-level extraction order, and numerical seed-policy reduction
are execution-time designs that must be decided under their owning issues after
fresh characterization. They cannot weaken the invariants in this spec.

## Decision Ledger

| Decision | Evidence | Resolution | Owner |
| --- | --- | --- | --- |
| Use deletion-first cutovers | Multiple generations of serializers, NLPs, bindings, and result policies coexist | A slice succeeds only when it deletes a displaced owner | M3/M4 |
| Keep state-dependent resolution at State conditions | Dataset-time evaluation can precede the real `T/x` | Preserve correlations to resolution and record evaluated values | M3 |
| Use one immutable native model definition | Python currently rebuilds loose native arguments through several paths | Construct once and consume through a typed handle | M3 |
| Make activation native and singular | Native and Python route/capability tables overlap | One typed native descriptor drives compile, solve, and runtime capability display | M4 |
| Use one saturation-pressure production NLP | Exposed pressure routes already share most thermodynamic structure | Express route differences as typed data rather than solver classes | M4 |
| Remove closed bindings from production | Declared-not-exposed workflows remain directly compiled and callable internally | Use native tests, explicit experimental targets, or Git history | M4 |
| Remove paper programs from runtime | Gross and Khudaida logic is duplicated across production owners | Keep literature data and validation in M6-owned artifacts | M4/M6 |
| Keep one native acceptance decision | Python reconstructs native certification from loose mappings | Return typed required fields and adapt only presentation in Python | M4 |
| Share EOS equations between values and derivatives | Bespoke derivative equations duplicate templated residual implementations | Record the canonical scalar assembler with CppAD | M3 |
| Share one density workflow | Report and scalar density functions duplicate scan/refine/select logic | Make scalar access delegate to the typed report | M3 |
| Reject wholesale Task 9 merge | The branch adds useful concepts alongside major net source growth | Salvage tests and records selectively under this architecture | M3 |
| Set measurable reduction expectations | Combined source is 55,121 lines with concentrated owner overlap | Target 13,000-17,000 net deletion while preserving equations and proof | M0/M3/M4 |
