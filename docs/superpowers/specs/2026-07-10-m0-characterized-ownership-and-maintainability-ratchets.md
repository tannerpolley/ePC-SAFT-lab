# Characterized Ownership And Maintainability Ratchets

Milestone: `M0 - Governance`
Issue: planned M0 tracking issue
Status: `approved for planning`
Last reviewed: `2026-07-10`

## Context

This specification replaces the flat, cross-package interpretation of Task 19
from the repository validation-correctness program. It defines an M0 governance
contract that package-owned M3, M4, and M5 work must satisfy before large
production modules are decomposed.

The objective is not to make line count a proxy for quality. The objective is
to make ownership traceable, preserve corrected behavior before structural
change, prevent known monoliths from growing without review, and ratchet
structural debt downward as package work creates real boundaries.

## Current Evidence

- Merged PR #203 already decomposed important provider-native responsibilities
  and added the provider source-size gate at
  tests/workflows/repo/test_project_structure.py.
- The existing provider gate caps native C++ files at 1,000 lines and selected
  state facades at 1,250 lines. It is useful evidence, but it is provider-only
  and has no shared baseline, issue owner, or ADR exception record.
- Closed issue #362 and
  packages/epcsaft-equilibrium/src/epcsaft_equilibrium/capability_evidence.py
  already map production equilibrium families to public entry points, native
  owners, proof nodes, checkers, sources, artifacts, and metrics.
- The present structural hotspots still include equilibrium route,
  binding, and workflow owners, regression core.py, and provider datasets.py.
  Their exact sizes are observations, not completion criteria.
- Tasks 9 through 15 intentionally correct model-input, regression, and
  equilibrium behavior. Characterizing known-defective behavior before those
  corrections would preserve the wrong contract.

## Goals

1. Define one shared ownership-record contract without creating another
   capability source of truth.
2. Require package-owned characterization of public entry points, condition
   resolution, native dispatch, result construction, and evidence.
3. Govern oversized production files through deterministic baselines,
   no-growth checks, and ratchet-on-shrink updates.
4. Require every oversized-file exception to name its package owner and a
   locally resolvable accountability record for either an active decomposition
   issue or an accepted ADR.
5. Fold provider data ownership into the M3 typed-model-input program and
   regression ownership into the M5 correctness and evidence program.
6. Make decomposition preserve post-correction behavior and capability state.

## Non-Goals

- No source decomposition or numerical behavior change in this M0 work.
- No requirement that every production file immediately fall below 1,000
  lines.
- No duplicate hand-maintained list of capabilities or public routes.
- No capability admission, parameter invention, solver tuning, or paper-bundle
  repair.
- No compatibility wrappers or temporary parallel owner paths.
- No claim that fewer lines alone prove lower coupling or better design.

## Alternatives

### Enforce an immediate absolute size cap

Rejected. It would block narrow safety fixes in existing large files, encourage
mechanical splitting, and confuse a review trigger with an architecture proof.

### Keep ownership maps in prose only

Rejected. Prose drifts and cannot fail when a public entry point, native owner,
result builder, or proof node changes.

### Package-owned maps plus an M0 ratchet index

Selected. Each package retains the canonical scientific and capability facts it
owns. M0 records only where those maps live and the structural debt baselines
needed for repository-wide enforcement.

## Selected Design

### Ownership records

Every production public entry point has exactly one package-owned record with:

- stable record ID, package, and milestone;
- public entry point and supported scope;
- visibility: production, internal validation, or declared-not-exposed;
- request and condition-resolution owner;
- native dispatch owner, when native execution applies;
- result construction and acceptance owner;
- proof nodes and strict checker identities;
- source and retained-artifact references when the record computes model
  predictions.

Internal development records may omit public-entry fields but must state why
they cannot admit a public capability.

M4 extends its existing capability-evidence records rather than creating a
parallel registry. M3 adds the provider-input and dataset owner records through
the Task 9 typed-model-input work. M5 creates its authoritative records only
after Tasks 10 through 12 correct public controls, target contracts, and
production evidence.

### M0 ratchet index

A milestone-owned machine-readable index records:

- schema version;
- package and milestone;
- path to each package-owned ownership source;
- path to the versioned local accountability snapshot;
- oversized production file path;
- measured baseline line count;
- package owner;
- stable accountability ID for an active decomposition issue, or an accepted
  ADR and rationale;
- maximum allowed line count, initially equal to the accepted baseline.

Repository validation applies these rules on every run:

1. A new production file above 1,000 lines fails unless an ADR records why one
   cohesive unit is safer.
2. A baseline-listed file may not exceed its recorded maximum.
3. When a listed file shrinks, the index must ratchet to the lower count in the
   same change; later growth back to the old size fails.
4. An oversized record without an owner and active issue or ADR fails.
5. Removing or renaming a listed file requires updating the index and ownership
   map in the same change.

This deterministic baseline check does not depend on local branch names or an
available Git merge base.

### Local accountability snapshot and live reconciliation

The pure repository gate does not query GitHub. A separate versioned M0
snapshot records each stable accountability ID and enough local evidence to
resolve it deterministically:

- `kind`: `github_issue` or `adr`;
- canonical identifier, such as `github:ePC-SAFT/ePC-SAFT#<number>` or
  `adr:<number>`;
- owning milestone and package;
- local issue-mirror path or ADR path;
- recorded issue state or accepted ADR state; and
- last live-reconciliation date for GitHub issue records.

For an issue record, the pure validator resolves the local mirror and verifies
that its issue number, canonical URL, milestone, package, and recorded state
match the snapshot. For an ADR, it resolves the tracked ADR path and accepted
identifier. An oversized-file record references only one of these stable local
IDs; free-form issue text is not accepted.

A separate explicit reconciliation command compares GitHub issue records with
the live tracker and reports snapshot/mirror drift. It is not called by the
pure validator, does not make routine repository validation network-dependent,
and never rewrites the snapshot automatically. A reviewed snapshot/mirror
update is required before activation when live state has changed.

## Ownership

- M0 Governance owns the schema, ratchet index, validator, and tracker policy.
- M3 EOS owns provider input, state, dataset, and native-provider records.
- M4 Equilibrium owns selector, formulation, NLP, Ipopt, certification, result,
  and binding records.
- M5 Regression owns target, payload, Ceres execution, result, and evidence
  records.
- M6 Validation owns literature and capability proof artifacts, not package
  runtime ownership.

Each GitHub issue remains in exactly one milestone. The M0 issue is the
cross-package tracker; package implementation remains in its M3, M4, or M5
issue.

## Interfaces

The M0 validator consumes pure data and must not require a compiled extension.
Package ownership sources therefore expose or generate deterministic data that
can be inspected in repository validation.

The ownership-record and ratchet-index schemas are versioned. Unknown fields,
duplicate record IDs, missing owners, missing referenced paths, and conflicting
public owners are validation errors. The accountability snapshot is versioned
separately, and the pure validator rejects missing snapshot IDs, duplicate
canonical identifiers, mirror/record disagreement, and unresolved ADR paths.

## Data Flow

1. M0 lands the versioned schema, pure validator, and local-accountability
   contract without activating new cross-package baselines.
2. Each package writes and tests its authoritative ownership records against
   that schema; M4 completes its characterization records before M0 activation.
3. M0 records the characterized package sources, measured baselines, and
   locally reconciled accountability IDs, then activates the shared gate.
4. Repository validation loads each source, checks schema and uniqueness, and
   measures tracked production files against the activated index.
5. Only after activation does a domain decomposition plan update one owner at
   a time and ratchet the affected baseline after verification.

This is the required acyclic order: M0 schema/validator -> package
characterization, including M4 -> M0 activation -> M4 extraction.

## Error Handling

- Missing or conflicting ownership fails with exact record and path details.
- A growth violation reports current count, permitted count, owner, and
  governing local accountability ID.
- Snapshot or mirror drift reports the exact canonical issue/ADR identifier
  and differing fields; only the separate live command reports live GitHub
  drift.
- The validator never updates baselines automatically.
- A missing scientific proof cannot be replaced by a structural test.
- A known closed capability remains closed; structural cleanup never changes
  activation or capability status implicitly.

## Stop Gates

- Do not snapshot M3 provider-input behavior until Task 9 correctness is
  accepted.
- Do not snapshot M5 regression numerics until Tasks 10 through 12 establish
  the problem actually solved and its admitted evidence.
- Do not activate M4 structural baselines until its ownership characterization
  records pass the M0 schema.
- Do not decompose M4 equilibrium before the shared M0 gate is activated and
  its scientific/certification prerequisites pass.
- Stop if an extraction would require two live owners, a compatibility
  forwarder, or a capability change.
- Stop when a numerical mismatch cannot be explained by an intentional,
  separately approved correctness change.

## Testing

- Schema tests reject duplicate IDs, missing owners, stale paths, and unknown
  status values.
- Mutation tests grow an oversized file, omit its issue or ADR, and retain a
  stale higher baseline after shrink; every mutation must fail.
- Accountability mutations reject an unknown stable ID, mismatched local
  mirror, duplicate canonical identifier, and missing ADR path.
- Live-reconciliation tests use recorded tracker responses and prove that live
  drift is reported separately without changing the snapshot.
- Package characterization tests prove public entry point to native owner to
  result owner to evidence identity.
- Existing package confidence and strict scientific checkers remain the
  numerical oracle.
- Documentation and repository structure validation must pass.

## Cutover

1. Record PR #203 and closed #362 as foundations, not unfinished greenfield
   work.
2. Introduce the M0 schemas, pure validator, and local-accountability contract
   without activating cross-package baselines or weakening the current
   provider gate.
3. Fold the M3 ownership slice into the Task 9 typed-model-input spec and plan,
   the M5 ownership slice into the Tasks 10 through 12 program tracked by
   issue #193, and complete M4 ownership characterization against the schema.
4. Reconcile the local accountability snapshot with live GitHub state, record
   exact measured baselines, and activate the shared M0 gate.
5. Replace package-specific size checks only after the shared validator proves
   at least the same constraints.
6. Execute M4 extraction slices only after that activation; ratchet the index
   after each accepted reduction.

## Risks

- A central map could duplicate package truth. Control: M0 stores source
  pointers and structural baselines, while packages own scientific records.
- Line-count gaming could create shallow modules. Control: decomposition must
  reduce duplicated decisions or coupling and preserve characterized behavior.
- Baselines could become permanent exemptions. Control: every non-ADR
  oversized record names a locally resolvable active decomposition issue,
  live state is reconciled separately, and the baseline ratchets on shrink.
- A pure gate could silently rely on stale tracker state. Control: version the
  snapshot/mirror evidence, expose its reconciliation date, and require the
  separate live reconciliation before activation and closeout.
- Characterization could freeze a defect. Control: characterization follows
  correctness work and records only accepted behavior.

## Execution-Time Measurements

No material design decision remains. Package implementation plans will record
their then-current measured baselines, exact issue numbers, and serialization
details without changing this contract.

## Decision Ledger

| Decision | Evidence | Resolution | Owner |
| --- | --- | --- | --- |
| Use M0 for the shared gate | Issue-tracker policy assigns repo-wide process gates to M0 | M0 owns schema and tracking; package work stays package-owned | M0 |
| Preserve existing foundations | PR #203 provider gate and closed #362 capability contract | Extend them; do not recreate them | M3/M4 |
| Use a ratchet instead of forced immediate splitting | Current accepted files exceed the review threshold | Prevent growth and require accountable reduction | M0 |
| Characterize after correctness | Tasks 9 through 15 intentionally change defective contracts | Snapshot the corrected contract only | M3/M4/M5 |
| Keep the repository gate pure | GitHub availability is not a deterministic repository input | Resolve versioned local accountability records and reconcile live state separately | M0 |
| Keep the dependency graph acyclic | M4 records need the schema, while activation needs characterized M4 records | Schema -> characterization -> activation -> extraction | M0/M4 |
| Split Task 21 ownership | datasets.py is M3 and regression core.py is M5 | Fold each half into its owning program | M3/M5 |
| Keep scientific evidence ownership package-owned | Canonical evidence contract and package-boundary ADRs | M0 references package sources without copying claims | All package owners |
