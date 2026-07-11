# M4 Equilibrium Canonical-Owner Decomposition

Milestone: `M4 - Equilibrium`
Issue: planned M4 tracking issue
Status: `draft for review`
Last reviewed: `2026-07-10`

## Context

This specification replaces Task 20's greenfield cleanup wording with an
incremental M4 design grounded in the current equilibrium package. The package
already has an activation matrix, selector core, Ipopt adapter, result builder,
route-result bridge, capability evidence, and shared certification work from
closed issue #362. The remaining problem is that route formulation,
orchestration, result conversion, diagnostics, and binding registration still
share several very large owners.

This is a behavior-preserving decomposition program. It starts only after the
relevant M4 correctness and admission decisions are stable and the accepted
behavior is characterized.

## Current Evidence

- ADR 0003 makes the native activation matrix and selector core authoritative
  for public route admission.
- The public surface is bubble_pressure, dew_pressure, and scoped
  single_component_vle. Neutral LLE, TP flash, multiphase, electrolyte,
  reactive, and chemical/coupled phase families remain closed unless their own
  proof later admits them.
- Closed issue #362 and capability_evidence.py provide the first executable map
  from public route families to native owners and retained proof.
- Existing result-builder/bridge modules own important certification work, but
  current route, boundary, binding, and workflow files remain concentrated at
  approximately 6,596, 4,984, 4,506, and 1,656 lines respectively.
- register_bindings.cpp still combines route-result conversion and diagnostic
  assembly with pybind registration.
- The prior
  docs/superpowers/specs/2026-05-27-m4-equilibrium-gfpe-package-cleanup-plan.md
  describes obsolete production routes and is not executable guidance.

## Goals

1. Establish an executable M4 ownership map covering public and retained
   internal equilibrium paths.
2. Separate formulation, selector, NLP, Ipopt, result/certification, and
   binding ownership while retaining one admission and acceptance policy.
3. Make pybind registration a thin translation layer without solver or
   acceptance decisions.
4. Delete superseded pass-throughs and route-specific acceptance branches in
   the same slice that removes their last caller.
5. Preserve accepted numerical behavior, public API shape, closed-family capability state,
   and retained scientific evidence.
6. Reduce accountable structural baselines under the M0 maintainability
   ratchet.

## Non-Goals

- No new equilibrium route or capability admission.
- No change to thermodynamic equations, parameter values, phase-discovery
  claims, residual tolerances, or solver acceptance thresholds.
- No solver-option tuning to make a characterization test pass.
- No repair of individual Gross, Khudaida, MEA, or other paper programs.
- No simultaneous rewrite of the equilibrium package.
- No compatibility wrappers, parallel result builders, or old-file backups.
- No split performed solely to meet a line-count target.

## Alternatives

### Rewrite the equilibrium core around a new abstraction

Rejected. It would combine architecture change with numerical reimplementation
and make scientific drift difficult to localize.

### Split files mechanically by route name

Rejected. Moving the same condition tree into smaller files would reduce line
counts without clarifying ownership.

### Extract one characterized canonical owner at a time

Selected. Each slice begins with an accepted receipt, moves one responsibility,
deletes the superseded path, and reruns the same package and scientific proof.

## Selected Design

### Characterized ownership map

The existing M4 capability records are extended into an ownership map with:

- public route and visibility;
- Python request-normalization owner;
- activation and selector owner;
- thermodynamic formulation owner;
- variable-layout, residual, derivative, and NLP owner;
- Ipopt profile and solve owner;
- phase-discovery owner when applicable;
- certification and result owner;
- pybind registration unit;
- proof nodes, strict checkers, and retained artifacts.

Closed and internal families are mapped as internal evidence only. Their
presence in the map does not make them callable.

### Canonical owner boundaries

- activation_matrix owns declared and admitted route metadata.
- selector_core owns eligibility, dispatch, and the single production solve
  entrance.
- Route formulation modules own physical residual construction and route seeds,
  not admission or final acceptance.
- Shared NLP modules own variable layout, transforms, constraints, derivative
  callbacks, and sparse structure.
- ipopt_adapter owns named numerical profiles and normalized solver results.
- Existing result_builder and certification modules own physical postsolve
  acceptance.
- route_result_bridge and package result adapters own serialization of accepted
  native evidence.
- Domain registration units expose bindings; one module entry calls them.

### Extraction slices

1. Characterize all admitted routes and every internal path that later slices
   touch.
2. Move remaining result conversion and acceptance assembly out of
   register_bindings.cpp into the existing result/certification owners.
3. Split binding registration into domain-owned public, phase-discovery,
   electrolyte, chemical-equilibrium, and result-support units.
4. Split two_phase_eos_route.cpp by actual owner boundaries, including shared
   neutral route mechanics, phase-discovery/refinement, and electrolyte
   refinement, while retaining shared types only where they are genuinely
   shared.
5. Split bubble_dew.cpp by characterized physical formulation and shared
   boundary-tracing mechanics.
6. Reduce workflows.py to request normalization and one selector solve lane;
   delete internal bypasses made obsolete by the extracted native owners.
7. Ratchet structural baselines after every accepted reduction.

The implementation plan may divide these into smaller non-overlapping issues.
It may not combine them into one unreviewable rewrite.

## Ownership

- M4 Equilibrium owns every production and internal file changed by this work.
- M0 Governance owns the shared ownership schema and structural ratchet.
- M3 Provider is an external dependency through its stable public/native SDK;
  provider internals are outside scope.
- M6 Validation owns retained literature artifacts and checkers; M4 consumes
  them as proof.

The M4 tracking issue is separate from open issue #361. Issue #361 governs
phase-equilibrium certification; this specification governs implementation
ownership. The decomposition tracker is not blocked by the whole #361 future
admission tree. Each extraction leaf depends only on the accepted M0 ratchet,
closed shared-contract leaf #362, and any still-open correctness/admission issue
for the exact route path it touches.

## Interfaces

Public Python signatures and result schemas remain unchanged. Native
characterization receipts define the before-and-after compatibility boundary.

New internal modules expose typed C++ interfaces, not pybind dictionaries.
Dictionary conversion occurs at the binding/result boundary only. Registration
functions accept the extension module and register one owned domain; they do
not solve or certify a route.

No extraction introduces a second dispatcher, option profile, certification
policy, or capability table.

## Data Flow

1. Equilibrium validates a constructor-configured request.
2. The public workflow sends one normalized request to the selector binding.
3. Selector admission reads the activation row and rejects ineligible scope.
4. Selector dispatches to one formulation/NLP owner and the Ipopt adapter.
5. The formulation returns native solver and physical evidence.
6. The canonical result builder applies postsolve certification.
7. The result bridge serializes the certified evidence once.
8. Python constructs the public result without a second native solve or a
   second acceptance decision.

Internal validation paths enter only through explicitly mapped private
diagnostic bindings and remain labeled internal.

## Error Handling

- Closed or unsupported routes fail before solver dispatch.
- Solver failure and postsolve rejection remain distinct and retain their
  current diagnostics.
- Bindings validate types and required fields but never supply scientific
  defaults or reinterpret acceptance.
- A characterization mismatch stops the current extraction slice. It is not
  normalized away or hidden behind a wrapper.
- An internal diagnostic cannot set public admission or certification fields.

## Stop Gates

- The M0 ownership/ratchet schema is accepted.
- Closed shared-contract issue #362 and any active correctness/admission issue
  for the touched route establish the route and certification state for that
  slice; unrelated future family admission does not block decomposition.
- Each touched path has a before-change characterization receipt.
- The native build used for comparison is fresh for the owning sources.
- Stop if one slice changes numerical results, public capability sets,
  activation rows, strict-checker outcomes, or literature artifacts without a
  separately approved correctness specification.
- Stop if an extraction requires simultaneous provider or regression changes.

## Testing

- Ownership-map schema and uniqueness tests.
- Negative tests for selector bypass, direct public diagnostic bindings,
  duplicate acceptance, and a second native solve.
- Before-and-after characterization of requests, activation, native evidence,
  certification, public results, and failures.
- Focused native unit tests for every extracted module.
- M4 API, contract, native-confidence, and equilibrium-confidence lanes.
- Activation generation and all strict checkers backing admitted routes.
- Ruff, strict documentation build, diff check, and repository cleanup.

No new model prediction is accepted without the repository-required traceable
source and retained comparison plot. A behavior-preserving slice normally
reuses existing retained evidence rather than regenerating unrelated figures.

## Cutover

Each slice lands only after all callers use the new canonical owner. The same
slice deletes the superseded internal function, branch, registration block, or
wrapper. Includes, build manifests, SDK manifests, tests, docs, and ownership
records change together.

The obsolete May 27 cleanup document remains only as a historical record with a
prominent superseded notice. It is never used as a route or capability source.

## Risks

- Refactoring may change numerics accidentally. Control: fresh-native receipts
  and strict before/after characterization per slice.
- Splitting bindings may create circular includes. Control: typed core
  interfaces flow toward registration units, never back into them.
- Closed diagnostic paths may appear public. Control: activation/selector and
  negative export tests remain authoritative.
- Files may shrink without coupling improving. Control: each slice must delete
  duplicated decisions or establish one enforceable owner.
- Concurrent M4 science work may invalidate snapshots. Control: dependency
  gates and post-correctness characterization.

## Execution-Time Mapping

No material architecture decision remains. Exact function moves and initial
ratchet measurements are derived from the accepted ownership map at execution
time and recorded in the implementation plan.

## Decision Ledger

| Decision | Evidence | Resolution | Owner |
| --- | --- | --- | --- |
| Preserve selector admission | ADR 0003 and current public route map | selector_core remains the sole production dispatcher | M4 |
| Extend the existing result owner | result_builder and route_result_bridge already exist | Move remaining conversion to them; do not invent a replacement | M4 |
| Separate from #361 | #361 governs certification contracts, not source decomposition | Create a distinct M4 tracker with leaf-level route dependencies | M4 |
| Characterize after correctness | Earlier M4 tasks intentionally repair or admit behavior | Preserve the accepted post-correction contract | M4 |
| Keep closed families closed | Finite internal evidence does not establish public admission | Structural work cannot change activation | M4/M6 |
| Use incremental extraction | Current concentration spans several physical domains | Move and delete one canonical owner per reviewed slice | M4 |
| Supersede old cleanup guidance | The May 27 route table contradicts ADR 0003 | Retain it as non-executable history with a new-spec pointer | M4 |
