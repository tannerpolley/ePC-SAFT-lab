# M4 Equilibrium Canonical-Owner Decomposition Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> `superpowers:subagent-driven-development` (recommended) or
> `superpowers:executing-plans` task-by-task. Use
> `superpowers:test-driven-development` for each extraction,
> `superpowers:systematic-debugging` for any characterization mismatch, and
> `superpowers:verification-before-completion` before every checkpoint.

**Goal:** Decompose the largest equilibrium owners into enforceable canonical
boundaries while preserving public behavior, numerical receipts, closed-family
state, and one selector/certification policy.

**Architecture:** Extend the existing M4 capability evidence into an
executable ownership map against the inactive M0 schema. M0 then activates the
shared gate from those records before any extraction begins. Public-green
owners move first; route-gated internal owners remain separate leaves until
their correctness and external caller-cutover receipts pass. Native flow
remains activation -> selector -> formulation/NLP -> Ipopt ->
result/certification -> binding; Python remains constructor normalization ->
one selector solve -> one result adapter.

**Tech Stack:** C++17, pybind11, CMake source manifest, Python 3.13 local
development baseline, pytest, `uv`, Ruff, Sphinx, native activation generation,
M0 structural ratchets, and existing strict M4 checkers.

## Global Constraints

- Milestone and package ownership are `M4 - Equilibrium` and
  `packages/epcsaft-equilibrium/**`.
- This is behavior-preserving structural work: no equation, parameter,
  tolerance, solver option, phase-discovery claim, route admission, or public
  result-schema change.
- Preserve public routes exactly: `bubble_pressure`, `dew_pressure`, and scoped
  nonassociating hydrocarbon `single_component_vle`.
- Keep neutral LLE, electrolyte LLE, TP flash, multiphase, standalone CE, and
  reactive/coupled families closed unless a separate admission issue passes.
- Do not create compatibility forwarders, parallel dispatchers, duplicate
  result builders, backup files, or route-specific acceptance branches.
- A decomposition leaf depends on the accepted M0 ratchet, closed #362, and
  only the still-open correctness/admission issue for the exact path it
  touches. It is not blanket-blocked by #361.
- Required cross-plan order is M0 schema/validator -> M4 characterization -> M0
  activation/cutover -> M4 extraction.
- Characterize corrected behavior. Do not freeze a known-defective CE,
  electrolyte, or paper-specific output before its owning issue establishes
  the accepted state.
- Deferred paper-validation scripts, data, figures, and results are outside
  this plan. Their owning issues must migrate external callers before a
  route-gated M4 owner can be deleted.
- Candidate discovery and Stage III refinement do not own final acceptance;
  electrolyte postsolve certification stays under result/certification.
- Every moved declaration gets one canonical header; every caller includes
  that header directly; the old declaration and definition are deleted.
- Ratchet each affected baseline downward in the same accepted slice.

---

## Source Evidence

- Approved spec:
  `docs/superpowers/specs/2026-07-10-m4-equilibrium-canonical-owner-decomposition.md`.
- Shared certification foundation: closed issue #362 and
  `phase_equilibrium_certification.py`.
- M0 source:
  `docs/superpowers/specs/2026-07-10-m0-characterized-ownership-and-maintainability-ratchets.md`.
- Current measured hotspots at plan time:
  `two_phase_eos_route.cpp` 6,596 lines, `bubble_dew.cpp` 4,984 lines,
  `register_bindings.cpp` 4,506 lines, and `workflows.py` 1,656 lines.
- Existing canonical owners to deepen, not replace:
  `activation_matrix.h`, `selector_core.*`, `ipopt_adapter.*`,
  `results/result_builder.*`, `results/route_result_bridge.h`, and
  `capability_evidence.py`.
- Native source ownership manifest:
  `packages/epcsaft-equilibrium/cmake/equilibrium_native_sources.json`.

## Test Complete And Metrics

- Every public route and every touched internal path has one ownership record
  for request, activation, formulation, NLP, solver, discovery, certification,
  result, binding, proof nodes, checker, and retained artifact.
- Characterization captures normalized request, activation row, selector
  dispatch, native evidence, certification, public result, rejection class,
  and native source identity before and after each extraction.
- Exact JSON/numeric comparisons are unchanged except for explicitly excluded
  nonsemantic source-location metadata; exclusions are named in the test.
- Negative tests reject a second dispatcher, a public diagnostic binding, a
  duplicate acceptance decision, a second native solve, or a binding that
  supplies scientific values.
- No moved symbol remains declared or defined in its old file, and the native
  source manifest names every new source/header once.
- Source-owner tests reject electrolyte postsolve certification in a discovery
  module and reject any deferred paper path in this plan's changed-file set.
- Public activation/capability maps, strict checker outcomes, and retained
  scientific artifacts remain byte-identical unless a separately approved
  correctness issue owns the change.
- M0 line-count baselines never grow and ratchet to each newly measured lower
  count.

## Outcome Proof

**Intent:** Make equilibrium ownership small enough to review and enforce
without changing the thermodynamics or using file size alone as a success
proxy.

**Current Behavior:** Canonical selector, Ipopt, result, and capability owners
exist, but route mechanics, phase discovery, conversion, registration, and
Python orchestration remain concentrated in four very large files.

**Expected Outcome:** Domain modules expose typed internal interfaces, pybind
registration contains translation only, `workflows.py` owns one public selector
lane, superseded branches are deleted, and every extraction reproduces the
same accepted receipts.

**Target Output:** Extended M4 ownership records, route characterization tests,
public-green result/binding/neutral-discovery/route/Python modules, separately
gated internal owner modules, a thin registration entry, updated native source
manifest, and lower M0 ratchet baselines.

**Owner:** M4 owns the package changes and route-specific characterization;
M0 owns the shared ratchet schema/validator; M6 owns retained literature
artifacts consumed as proof.

**Interface:** `epcsaft_equilibrium.capabilities()` ownership records,
`register_equilibrium_bindings(py::module_&)`, domain registration functions,
existing native route/discovery function signatures,
`Equilibrium(...).solve()`, and package/native checker receipts.

**Cutover:** Each caller moves directly to the new canonical header/module and
the old function/branch is deleted in the same checkpoint. No compatibility
import or C++ forwarding function survives.

**Replaced Path:** Conversion and acceptance logic in `register_bindings.cpp`,
mixed neutral/electrolyte discovery in `two_phase_eos_route.cpp`, seed/postsolve
logic in `bubble_dew.cpp`, and internal validation/result ownership mixed into
`workflows.py` are displaced owner-by-owner. Deferred paper callers are changed
only by their own issues before a corresponding internal owner is removed.

**Evidence:** Before/after characterization receipts, focused native unit
tests, API/capability tests, strict route checkers, activation generation,
source-manifest checks, line-count ratchets, docs, Ruff, diff, cleanup, and
independent code/scientific review.

**Acceptance Proof:** Every accepted slice yields the same public requests,
native dispatch count, solver/certification evidence, results, failures,
activation/capability set, and strict checker outcomes while deleting one
duplicated decision owner and lowering its structural baseline.

**Stop Criteria:** Stop a slice on any numerical, status, schema, activation,
capability, checker, or retained-artifact mismatch; a required sibling-package
change; an unresolved touched-route correctness issue; or a design that needs
two live owners.

**Avoid:** Do not mechanically split by route name, normalize mismatches away,
move logic behind wrappers, combine unrelated extractions, or count smaller
files without clearer single ownership as completion.

**Risk:** Moving coupled C++ code can change initialization order, floating
evaluation order, or binding semantics. Small slices, fresh native builds, and
exact before/after receipts constrain that risk.

## Implementation Boundaries

**Files To Create:** M4 characterization tests; result bridge `.cpp` owners;
domain binding registration headers/sources; neutral/electrolyte
phase-discovery headers/sources; a result-owned electrolyte postsolve
certification module; focused neutral/electrolyte route owners; boundary
seed/postsolve owners; and focused Python public/internal modules named in the
tasks below.

**Files To Modify:** `capability_evidence.py`, the four hotspot files, existing
canonical owner headers/sources, package tests, native source manifest, M0
ratchet index, and ownership documentation.

**Files To Avoid:** Provider and regression implementations, scientific input
bundles, paper scripts/results, activation state, release metadata, and
downstream repositories.

**Source Of Truth:** Native activation matrix, selector core, closed #362
certification contract, route-specific strict checkers, package capability
evidence, and accepted M0 ratchet index.

**Read Path:** Public/internal request -> ownership record -> characterized
request/activation/native/result receipt -> existing implementation owner ->
new owner -> same receipt and checker outcome.

**Write Path:** Add one RED ownership/characterization assertion, capture the
accepted baseline, move one responsibility, update all callers/manifests,
delete the old owner, rerun proof, and ratchet the baseline.

**Integration Points:** Native build/source identity, activation generator,
selector core, `NlpProblem`, Ipopt adapter, result builder/bridge, pybind module,
Python workflow/result adapters, capabilities, M0 validator, and strict M4
checkers.

**Migration Or Cutover:** Task 1 lands M4 characterization after M0 Task 1's
schema. M0 Tasks 2-3 then activate and cut over the shared gate. Only then do
public-green extraction Tasks 2-6 run. Route-gated internal Tasks 7-8 remain
separate issue/PR leaves until their exact correctness and external
caller-cutover dependencies pass.

**Replaced Path Handling:** Delete old symbols, includes, imports, branches,
tests, and manifest rows after the last caller moves. Retain no redirect module
or header alias.

**Acceptance Proof Gate:** Characterization requires the accepted M0 schema and
closed #362. Every extraction leaf requires the later activated M0 gate,
touched-route correctness, a fresh equilibrium-native build, exact before/after
characterization, focused/confidence checks, strict checkers, docs, Ruff, diff,
cleanup, and independent review.

## Decision Ledger

| Decision | Evidence | Resolution | Owner |
| --- | --- | --- | --- |
| Extend existing certification map | Closed #362 already maps production routes to proof | Add ownership fields there; no parallel registry | M4 |
| Move conversion into existing result owners | `result_builder` and `route_result_bridge` already own acceptance/serialization | Deepen them before splitting registration | M4 |
| Split registration by domain | Current registration mixes CE, phase, electrolyte, result, and smoke bindings | One module entry calls typed domain registrars | M4 |
| Split discovery by algorithm domain | Neutral and electrolyte discovery share one giant source but different constraints | Separate neutral and reduced-electroneutral owners | M4 |
| Certification ownership | Electrolyte postsolve certification consumes discovery and solver evidence to decide acceptance | Move it only to result/certification, never discovery | M4 |
| Preserve signatures while moving | Callers already depend on stable typed C++ functions | Move definitions/declarations; do not wrap | M4 |
| Gate by touched route | #361 includes unrelated future admissions | Depend only on correctness for the moved path | M4 |
| Cross-plan order | M4 characterization needs the schema; M0 activation needs M4 records | Schema -> characterization -> activation -> extraction | M0/M4 |
| Deferred callers | Paper programs have separate milestone owners and unresolved validation work | Keep their paths out; block internal M4 deletion until caller-cutover receipts land | M4/M6 |
| Ratchet on every shrink | M0 contract forbids regained structural debt | Update accepted lower counts with each slice | M0/M4 |

### Task 1: Characterize M4 Ownership Against The Inactive M0 Schema

**Use Cases:**

- A reviewer can trace every admitted route and touched internal path from
  request to evidence before an extraction begins.
- M0 receives complete M4 owner records before it activates any M4 baseline,
  avoiding a circular dependency.
- Before/after characterization is the acceptance evidence for each cutover;
  a mismatch stops the extraction instead of being normalized.

**Files:**

- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/capability_evidence.py`
- Create: `packages/epcsaft-equilibrium/tests/contracts/test_equilibrium_ownership_map.py`
- Modify: `packages/epcsaft-equilibrium/tests/contracts/test_activation_capabilities.py`

**Interfaces:**

- Produces ownership fields `request_owner`, `activation_owner`,
  `formulation_owner`, `nlp_owner`, `solver_owner`, `discovery_owner`,
  `certification_owner`, `result_owner`, `binding_owner`, `proof_nodes`,
  `strict_checkers`, and `retained_artifacts` on existing evidence records.
- Consumes the M0 ratchet schema; does not create a second capability source.
- Produces a characterization receipt consumed by M0 activation; it neither
  measures nor activates structural baselines.

- [ ] **Step 1: Write RED ownership/characterization tests.** Require one owner
  per concern for each public route and each package-internal path selected by
  Tasks 2-8; reject duplicate owners, missing paths, a public diagnostic
  binding, discovery-owned postsolve certification, and any paper-program path
  in an M4 ownership record.

- [ ] **Step 2: Verify RED.** Run
  `uv run --no-sync python run_pytest.py packages/epcsaft-equilibrium/tests/contracts/test_equilibrium_ownership_map.py packages/epcsaft-equilibrium/tests/contracts/test_activation_capabilities.py tests/workflows/repo/test_project_structure.py -q`.
  Expected: the new ownership fields and characterization receipt are missing.

- [ ] **Step 3: Add characterized ownership records.** Extend the existing
  capability evidence with exact owners and proof identities for the public and
  selected package-internal paths. Leave the M0 index unchanged; its activation
  task later measures the four hotspots and references this accepted record.

- [ ] **Step 4: Refactor and verify GREEN.** Reuse one schema validator for
  existing capability and ownership fields. Rerun Task 1; expected: all tests
  pass without a compiled native extension.

- [ ] **Step 5: Checkpoint commit.** Commit
  `test(equilibrium): characterize canonical route ownership`.

After this checkpoint, execute M0 ratchet-plan Tasks 2-3. Tasks 2-8 below are
blocked until that shared gate is active.

### Task 2: Move Public-Route Result Conversion Out Of Registration

**Use Cases:**

- Binding code registers functions but cannot certify a result or assemble
  route acceptance.
- Before/after payloads prove the moved result bridge displaced the old
  conversion code without changing numerical evidence.

**Files:**

- Create: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/results/route_result_bridge.cpp`
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/results/route_result_bridge.h`
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/register_bindings.cpp`
- Modify: `packages/epcsaft-equilibrium/cmake/equilibrium_native_sources.json`
- Modify: `packages/epcsaft-equilibrium/tests/native/results/test_result_builder.py`
- Modify: `packages/epcsaft-equilibrium/tests/contracts/test_equilibrium_native_contracts.py`
- Modify: `docs/superpowers/milestones/M0-governance/ownership-ratchets.yaml`

**Interfaces:**

- Produces `route_result_to_python(const NeutralTwoPhaseEosRouteResult&) ->
  pybind11::dict` for characterized public-route results.
- Consumes `result_builder` certification output; makes no acceptance decision.

- [ ] **Step 1: Add RED source-ownership and payload tests.** Require
  conversion/acceptance key assembly to be absent from
  `register_bindings.cpp`, present once in result owners, and produce an exact
  payload for representative accepted and rejected results.

- [ ] **Step 2: Verify RED.** Run the native-contract/result tests; expected:
  source-owner assertions fail while current payload characterization passes.

- [ ] **Step 3: Move implementations and all callers.** Turn the current inline
  route bridge into declarations plus `.cpp`, update the source manifest, and
  delete the moved public-route function from registration. Leave CE/internal
  result conversion untouched for Task 8.

- [ ] **Step 4: Rebuild, refactor, and verify GREEN.** Rebuild incrementally,
  run the Task 2 tests and public route characterization, then lower the
  registration baseline. Expected: byte-equivalent JSON-like payloads.

- [ ] **Step 5: Checkpoint commit.** Commit
  `refactor(equilibrium): centralize native result conversion`.

### Task 3: Split Public-Green Pybind Registration Into Domain Units

**Use Cases:**

- Each binding domain has one registrar and no solver/certification decision.
- The module entry calls every registrar exactly once, replacing the monolithic
  registration body without exposing private diagnostics publicly.

**Files:**

- Create: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/bindings/registration.h`
- Create: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/bindings/metadata.cpp`
- Create: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/bindings/solver_contracts.cpp`
- Create: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/bindings/phase_routes.cpp`
- Create: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/bindings/result_support.cpp`
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/register_bindings.cpp`
- Modify: `packages/epcsaft-equilibrium/cmake/equilibrium_native_sources.json`
- Modify: `packages/epcsaft-equilibrium/tests/contracts/test_equilibrium_native_contracts.py`
- Modify: `packages/epcsaft-equilibrium/tests/native/diagnostics/test_selector_core_contracts.py`
- Modify: `docs/superpowers/milestones/M0-governance/ownership-ratchets.yaml`

**Interfaces:**

- Produces four functions named `register_<domain>_bindings(pybind11::module_&)`
  for metadata, solver contracts, public phase routes, and result support.
- Preserves provider SDK entry
  `register_equilibrium_bindings(pybind11::module_&)`, now a thin ordered call
  list.

- [ ] **Step 1: Write RED registration topology tests.** Require each binding
  name to occur in exactly one domain source, all registrar functions to be
  called once, no domain source to call a solve during module initialization,
  and private binding names to remain private.

- [ ] **Step 2: Verify RED.** Run native contract and selector metadata tests;
  expected: topology assertions fail on the monolith.

- [ ] **Step 3: Move registrations by domain.** Move binding lambdas plus only
  their translation helpers, include typed owners directly, update the source
  manifest, and delete each moved block from `register_bindings.cpp`. Leave
  gated CE, electrolyte, and private-discovery registrations for Tasks 7-8.

- [ ] **Step 4: Rebuild, refactor, and verify GREEN.** Run native contracts,
  binding import smoke, activation metadata, and exact public/private export
  snapshots; ratchet the old file count.

- [ ] **Step 5: Checkpoint commit.** Commit
  `refactor(equilibrium): split native binding registration`.

### Task 4: Extract Public-Route Neutral Phase Discovery

**Use Cases:**

- Neutral TPD support executed by admitted boundary routes has one typed owner.
- A moved discovery path retains the same scoped completeness status and never
  converts finite candidates into global phase-set proof.

**Files:**

- Create: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/phase_discovery/phase_discovery_types.h`
- Create: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/phase_discovery/neutral_phase_discovery.h`
- Create: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/phase_discovery/neutral_phase_discovery.cpp`
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/core/two_phase_eos_route.h`
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/core/two_phase_eos_route.cpp`
- Modify: `packages/epcsaft-equilibrium/cmake/equilibrium_native_sources.json`
- Modify: `packages/epcsaft-equilibrium/tests/native/diagnostics/test_internal_multiphase_activation_contracts.py`
- Modify: `docs/superpowers/milestones/M0-governance/ownership-ratchets.yaml`

**Interfaces:**

- Moves existing signature `evaluate_neutral_tpd_phase_discovery` without a
  wrapper.
- Produces shared candidate/result types only in
  `phase_discovery_types.h`.

- [ ] **Step 1: Add RED owner and receipt characterization.** Require the
  symbol to be declared/defined once in its target domain and snapshot all
  candidate, bound, replay, and scoped-completeness fields for the public
  boundary route.

- [ ] **Step 2: Verify RED.** Run focused phase-discovery tests/checkers;
  expected: owner assertions fail while current public-route receipts establish
  the baseline.

- [ ] **Step 3: Move the neutral slice.** Move shared candidate types needed by
  the public path, then the neutral algorithm. Update direct includes/callers
  and delete moved code from the old source. Leave every electrolyte symbol,
  including postsolve certification, for Task 7.

- [ ] **Step 4: Rebuild, refactor, and verify GREEN.** Run the exact checker for
  each moved path, confirm unchanged completeness/closed status, and ratchet
  `two_phase_eos_route.cpp` after the slice.

- [ ] **Step 5: Checkpoint commit.** Use
  `refactor(equilibrium): isolate neutral phase discovery`.

### Task 5: Extract Public Neutral Route And Boundary Owners

**Use Cases:**

- Public neutral route solve mechanics and bubble/dew seed/postsolve mechanics
  have one physical owner each, while selector and final acceptance remain
  centralized.
- Public bubble/dew characterization proves the extraction replaces old
  branches without numerical drift.

**Files:**

- Create: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/routes/neutral/two_phase_route.h`
- Create: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/routes/neutral/two_phase_route.cpp`
- Create: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/routes/derived/boundary_seed_factory.h`
- Create: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/routes/derived/boundary_seed_factory.cpp`
- Create: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/routes/derived/boundary_postsolve.h`
- Create: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/routes/derived/boundary_postsolve.cpp`
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/core/two_phase_eos_route.h`
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/core/two_phase_eos_route.cpp`
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/routes/derived/bubble_dew.cpp`
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/core/selector_core.cpp`
- Modify: `packages/epcsaft-equilibrium/cmake/equilibrium_native_sources.json`
- Modify: `packages/epcsaft-equilibrium/tests/api/test_equilibrium.py`
- Modify: `packages/epcsaft-equilibrium/tests/native/diagnostics/test_route_metadata_contracts.py`
- Modify: `packages/epcsaft-equilibrium/tests/native/results/test_result_builder.py`
- Modify: `docs/superpowers/milestones/M0-governance/ownership-ratchets.yaml`

**Interfaces:**

- Preserves existing public internal C++ solve signatures from
  `two_phase_eos_route.h` and `bubble_dew.cpp` by moving them to domain headers.
- Produces `boundary_seed_candidates(const BoundaryRouteInput&)` and
  `build_boundary_postsolve(const BoundaryRouteInput&, const
  IpoptSolveResult&)`; selector remains the only dispatcher and result builder
  remains the only certification owner.

- [ ] **Step 1: Add RED characterization and owner tests.** Snapshot public
  bubble/dew requests, seed attempts, solver evidence, postsolve metrics,
  failures, and result JSON. Require each moved symbol to have one target
  owner and no route-local activation/acceptance branch.

- [ ] **Step 2: Verify RED.** Run one public bubble/dew node plus native
  contract/result tests; expected: owner assertions fail and characterization
  is green.

- [ ] **Step 3: Move one route responsibility per commit.** Extract shared
  neutral mechanics, then boundary seeds, then boundary postsolve; update
  callers and delete old branches each time. Leave electrolyte mechanics for
  Task 7.

- [ ] **Step 4: Rebuild, refactor, and verify GREEN.** Re-run exact public and
  boundary-route receipts/checkers after each move; ratchet both giant source
  files to their measured lower counts.

- [ ] **Step 5: Checkpoint commits.** Use focused messages such as
  `refactor(equilibrium): isolate boundary seed ownership`; never combine all
  route extractions in one commit.

### Task 6: Reduce Python Workflows To One Public Selector Lane

**Use Cases:**

- `Equilibrium` normalization, native solve, and result adaptation each have
  one owner and no second solve or acceptance decision.
- Public-green owners move without waiting for or editing deferred internal and
  paper callers.

**Files:**

- Create: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/core/configured_problem.py`
- Create: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/core/result_adapter.py`
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/core/native_results.py`
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/workflows.py`
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/equilibrium.py`
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/__init__.py`
- Modify: `packages/epcsaft-equilibrium/tests/api/test_equilibrium.py`
- Modify: `packages/epcsaft-equilibrium/tests/contracts/test_activation_capabilities.py`
- Modify: `packages/epcsaft-equilibrium/tests/native/results/test_result_builder.py`
- Modify: `tests/workflows/repo/test_project_structure.py`
- Modify: `docs/superpowers/milestones/M0-governance/ownership-ratchets.yaml`

**Interfaces:**

- `configured_problem.py` owns `EquilibriumProblem`, `EquilibriumStructure`,
  and `configure_equilibrium_problem(...)`.
- `result_adapter.py` owns `native_selector_route_to_result(...)` adaptation.
  `EquilibriumPhase` and `EquilibriumResult` remain in `workflows.py` during
  this public-green slice because a deferred Gross contract still imports the
  private owner; their move is explicitly assigned to route-gated Task 8 after
  its M6 caller-cutover receipt.
- `workflows.py` retains `EquilibriumSolverOptions`, option normalization,
  `_solve_selector_route(...)`, and selector request construction.

- [ ] **Step 1: Write RED module-boundary tests.** Require one public selector
  solve, one result adaptation, no internal validator in public exports, no
  compatibility reexports, and direct imports from the new canonical owner.

- [ ] **Step 2: Verify RED.** Run API, import, structure, capability, and repo
  structure tests; expected: owner assertions fail while current public route
  behavior is characterized.

- [ ] **Step 3: Move only public-green owners.** Move immutable problem types
  and the selector-result adapter, updating `core/native_results.py`,
  `Equilibrium`, and package tests directly. Do not move or reexport
  `EquilibriumPhase`/`EquilibriumResult` while the deferred Gross caller still
  imports their current owner. Leave those types and other route-gated internal
  helpers in place for Task 8; do not edit deferred caller paths.

- [ ] **Step 4: Refactor and verify GREEN.** Remove duplicate freezes,
  serializers, and old imports; run package API/confidence and touched strict
  checkers; ratchet `workflows.py` to the new lower count.

- [ ] **Step 5: Checkpoint commit.** Commit
  `refactor(equilibrium): isolate configured workflow owners`.

### Task 7: Extract Route-Gated Electrolyte Native Owners

**Use Cases:**

- Electrolyte discovery/refinement and route mechanics move only after their
  exact correctness gate passes.
- Postsolve certification consumes discovery evidence from a result-owned
  module and can never be mistaken for candidate discovery.

**Files:**

- Create: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/phase_discovery/electrolyte_phase_discovery.h`
- Create: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/phase_discovery/electrolyte_phase_discovery.cpp`
- Create: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/results/electrolyte_postsolve_certification.h`
- Create: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/results/electrolyte_postsolve_certification.cpp`
- Create: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/routes/electrolyte/two_phase_route.h`
- Create: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/routes/electrolyte/two_phase_route.cpp`
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/core/two_phase_eos_route.h`
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/core/two_phase_eos_route.cpp`
- Modify: `packages/epcsaft-equilibrium/cmake/equilibrium_native_sources.json`
- Modify: `tests/native/contracts/test_electrolyte_held2_phase_discovery.py`
- Modify: `tests/native/contracts/test_electrolyte_postsolve_certification.py`
- Modify: `docs/superpowers/milestones/M0-governance/ownership-ratchets.yaml`

**Interfaces:**

- Discovery owns `evaluate_electrolyte_tpd_phase_discovery`,
  `evaluate_electrolyte_continuous_tpd_minimizer`,
  `evaluate_electrolyte_held2_phase_discovery`, and
  `evaluate_electrolyte_stage_iii_refinement`.
- Result/certification alone owns
  `evaluate_electrolyte_postsolve_certification`; electrolyte route mechanics
  consume both typed boundaries without a forwarding wrapper.

- [ ] **Step 1: Write RED gated-owner tests.** Require exact one-definition
  ownership, unchanged discovery/Stage III/postsolve receipts, and a source
  rule that rejects postsolve certification under `phase_discovery/`.

- [ ] **Step 2: Verify the gate and RED state.** Require the exact electrolyte
  correctness issue and external caller-cutover receipts to be accepted, then
  run both focused native contract files. Expected: scientific baselines pass
  and owner assertions fail.

- [ ] **Step 3: Move discovery, route, and certification separately.** Move the
  four discovery/refinement functions, then eligible electrolyte route
  mechanics, then postsolve certification into `results/`. Update every direct
  package caller and delete old declarations/definitions; add no aliases.

- [ ] **Step 4: Rebuild and verify GREEN.** Run the two exact checkers and
  ownership tests after each move, confirm unchanged closed/completeness state,
  and ratchet the old source after each accepted reduction.

- [ ] **Step 5: Checkpoint commits.** Use separate commits for discovery,
  route mechanics, and postsolve certification; do not combine their gates.

### Task 8: Retire Route-Gated Internal Binding And Python Owners

**Use Cases:**

- CE, electrolyte diagnostics, and private validation bindings move only after
  their package correctness gates and all external caller migrations pass.
- M4 deletes old internal owners without taking ownership of deferred paper
  scripts or preserving compatibility reexports.

**Files:**

- Create: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/results/chemical_equilibrium_result_bridge.h`
- Create: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/results/chemical_equilibrium_result_bridge.cpp`
- Create: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/bindings/chemical_equilibrium.cpp`
- Create: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/bindings/phase_discovery.cpp`
- Create: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/internal_validation.py`
- Create: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/core/result_types.py`
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/register_bindings.cpp`
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/workflows.py`
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/core/native_results.py`
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/core/result_adapter.py`
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/__init__.py`
- Modify: `packages/epcsaft-equilibrium/cmake/equilibrium_native_sources.json`
- Modify: `packages/epcsaft-equilibrium/tests/contracts/test_chemical_equilibrium_standard_state.py`
- Modify: `packages/epcsaft-equilibrium/tests/contracts/test_equilibrium_native_contracts.py`
- Modify: `packages/epcsaft-equilibrium/tests/contracts/test_activation_capabilities.py`
- Modify: `tests/workflows/repo/test_project_structure.py`
- Modify: `docs/superpowers/milestones/M0-governance/ownership-ratchets.yaml`

**Interfaces:**

- Produces `chemical_equilibrium_result_to_python(...) -> pybind11::dict`,
  typed private-domain registrars, and package-owned private validation
  entrypoints in `internal_validation.py`. After the M6 Gross caller-cutover
  receipt is accepted, `core/result_types.py` becomes the sole owner of
  `EquilibriumPhase` and `EquilibriumResult`; `native_results.py`, the result
  adapter, workflows, and public exports import that owner directly.
- Consumes accepted CE/electrolyte correctness receipts, the focused M6 Gross
  public-route evidence/caller-cutover receipt, and a zero-external-caller
  inventory produced by the owning caller-migration issues.

- [ ] **Step 1: Write RED internal-owner tests.** Require one CE result owner,
  one private registrar per domain, no public diagnostic export, no internal
  helper reexport from `workflows.py`, and zero deferred-paper path in the M4
  change set.

- [ ] **Step 2: Verify dependencies and RED.** Confirm each moved symbol has no
  external caller and its exact route gate is accepted. Run CE/native/import
  contract tests; expected: current behavior is green and owner assertions
  fail. Stop instead of editing a deferred caller when the inventory is not
  empty.

- [ ] **Step 3: Move one internal domain per commit.** After the M6 Gross test
  no longer imports `workflows.EquilibriumResult`, move
  `EquilibriumPhase`/`EquilibriumResult` to `core/result_types.py` and update
  `core/native_results.py` plus every package caller directly. Then move CE
  result conversion, CE/private-discovery registration, and eligible private
  Python helpers. Delete old blocks and imports without aliases.

- [ ] **Step 4: Rebuild and verify GREEN.** Run only the strict checker for the
  moved internal route plus native/import/capability tests; confirm public
  exports and closed capability state are unchanged and ratchet each old file.

- [ ] **Step 5: Checkpoint commits.** Keep CE, electrolyte diagnostics, and
  Python-private ownership in separate reviewed commits.

## Proof Oracle

```bash
uv run --no-sync python scripts/validate_plan_task_use_cases.py --plan-path docs/superpowers/plans/2026-07-10-m4-equilibrium-canonical-owner-decomposition-plan.md
uv run --no-sync python scripts/validate_plan_outcome_proof.py --plan-path docs/superpowers/plans/2026-07-10-m4-equilibrium-canonical-owner-decomposition-plan.md
uv run --no-sync python scripts/dev/build_epcsaft.py --profile equilibrium
uv run --no-sync python run_pytest.py packages/epcsaft-equilibrium/tests/contracts/test_equilibrium_ownership_map.py packages/epcsaft-equilibrium/tests/contracts/test_equilibrium_native_contracts.py packages/epcsaft-equilibrium/tests/contracts/test_activation_capabilities.py packages/epcsaft-equilibrium/tests/native/diagnostics/test_selector_core_contracts.py packages/epcsaft-equilibrium/tests/native/results/test_result_builder.py -q
uv run --no-sync python run_pytest.py --equilibrium-api -q
uv run --no-sync python run_pytest.py --native-contracts -q
uv run --no-sync python run_pytest.py --confidence -q
uv run --no-sync python scripts/docs/generate_equilibrium_activation.py --check
uv run --no-sync ruff check packages/epcsaft-equilibrium/src/epcsaft_equilibrium packages/epcsaft-equilibrium/tests tests/workflows/repo/test_project_structure.py
uv run --no-sync python scripts/dev/validate_project.py docs
git diff --check
bash "$HOME/.codex/hooks/codex-cleanup.sh" --repo-root .
```

Run only the strict scientific checker for the route moved by the current leaf;
unrelated paper programs are neither regenerated nor repaired by this plan.
