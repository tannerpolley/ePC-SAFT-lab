# Characterized Ownership And Maintainability Ratchets

Milestone: `M0 - Governance`
Issue: planned M0 tracking issue
Status: `draft for review`
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
4. Require every oversized-file exception to name its package owner and either
   an active decomposition issue or an accepted ADR.
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
- oversized production file path;
- measured baseline line count;
- package owner;
- active decomposition issue, or accepted ADR and rationale;
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
public owners are validation errors.

## Data Flow

1. A package declares its authoritative ownership source in the M0 index.
2. Repository validation loads each source and checks schema and uniqueness.
3. Characterization tests exercise the public or internal route named by the
   record and compare its resolved payload, native dispatch, result builder,
   and proof identity with the declared owners.
4. The size validator measures tracked production files against the ratchet
   index.
5. A domain decomposition plan consumes the characterized records, updates one
   owner at a time, and ratchets the affected baseline after verification.

## Error Handling

- Missing or conflicting ownership fails with exact record and path details.
- A growth violation reports current count, permitted count, owner, and
  governing issue or ADR.
- The validator never updates baselines automatically.
- A missing scientific proof cannot be replaced by a structural test.
- A known closed capability remains closed; structural cleanup never changes
  activation or capability status implicitly.

## Stop Gates

- Do not snapshot M3 provider-input behavior until Task 9 correctness is
  accepted.
- Do not snapshot M5 regression numerics until Tasks 10 through 12 establish
  the problem actually solved and its admitted evidence.
- Do not decompose M4 equilibrium before its scientific/certification
  prerequisites and package characterization gate pass.
- Stop if an extraction would require two live owners, a compatibility
  forwarder, or a capability change.
- Stop when a numerical mismatch cannot be explained by an intentional,
  separately approved correctness change.

## Testing

- Schema tests reject duplicate IDs, missing owners, stale paths, and unknown
  status values.
- Mutation tests grow an oversized file, omit its issue or ADR, and retain a
  stale higher baseline after shrink; every mutation must fail.
- Package characterization tests prove public entry point to native owner to
  result owner to evidence identity.
- Existing package confidence and strict scientific checkers remain the
  numerical oracle.
- Documentation and repository structure validation must pass.

## Cutover

1. Record PR #203 and closed #362 as foundations, not unfinished greenfield
   work.
2. Introduce the M0 schemas and initial accepted baselines without weakening
   the current provider gate.
3. Fold the M3 ownership slice into the Task 9 typed-model-input spec and plan.
4. Fold the M5 ownership slice into the Tasks 10 through 12 correctness and
   evidence spec and plan, tracked by issue #193.
5. Execute M4 characterization and decomposition through its dedicated M4
   specification.
6. Replace package-specific size checks only after the shared validator proves
   at least the same constraints.

## Risks

- A central map could duplicate package truth. Control: M0 stores source
  pointers and structural baselines, while packages own scientific records.
- Line-count gaming could create shallow modules. Control: decomposition must
  reduce duplicated decisions or coupling and preserve characterized behavior.
- Baselines could become permanent exemptions. Control: every non-ADR
  oversized record names an active decomposition issue and ratchets on shrink.
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
| Split Task 21 ownership | datasets.py is M3 and regression core.py is M5 | Fold each half into its owning program | M3/M5 |
| Keep scientific evidence ownership package-owned | Canonical evidence contract and package-boundary ADRs | M0 references package sources without copying claims | All package owners |
