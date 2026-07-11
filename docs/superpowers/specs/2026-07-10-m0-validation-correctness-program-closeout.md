# Validation Correctness And Reproducibility Program Closeout

Milestone: `M0 - Governance`
Issue: `https://github.com/ePC-SAFT/ePC-SAFT/issues/434`
Status: `approved; tracker published`
Last reviewed: `2026-07-10`

## Context

This specification defines the final governance and evidence boundary for the
repository-wide program originally recorded in
docs/superpowers/specs/2026-07-09-m3-core-repository-truth-and-scientific-integrity-program.md
and its matching implementation plan.

The source program spans provider inputs, regression correctness, equilibrium
admission, validation evidence, local Linux packaging, maintainability, and
final proof. Those domains do not share one implementation owner. M0 therefore
closes the program by consuming milestone-owned receipts rather than rerunning
or re-owning every domain inside one giant issue.

The source specification and plan are user-requested historical and operational
records. They are retained and marked complete after closeout; they are never
deleted as a completion shortcut.

## Current Evidence

- ADR 0005 assigns the M3 provider, M4 equilibrium, and M5 regression
  boundaries.
- scripts/dev/validation_registry.py defines named repository and equilibrium
  validation lanes, including activation generation and strict Gross and NIST
  production checkers.
- The public associating `bubble_pressure` and `dew_pressure` rows currently
  cite the Gross/Sadowski 2002 Figures 2-9 retained bundle. The focused M6
  refresh of that exact public-route evidence is therefore an active closeout
  prerequisite; it is not part of the deferred-paper list while those routes
  remain exposed.
- M6 owns executable literature, plot, capability, and checker evidence.
- M1 owns monorepo package layout, extension boundaries, and local Linux
  build/install proof. Existing M1 work proves useful foundations but does not
  substitute for the final receipts required by the current program.
- M0 already owns tracker hygiene, dependency readiness, completion rules, and
  repository-wide process gates.
- Some valid final states keep a capability closed. An evidence-aligned closed status is
  complete when activation, public API, docs, tests, and evidence agree; it is
  not a failure that must be hidden or forced open.

## Goals

1. Produce one reproducible, machine-checkable closeout receipt graph.
2. Prove every public claim through current package behavior, collected tests,
   source-backed evidence, and fresh owning artifacts.
3. Consume M6 scientific/capability receipts and M1 local Linux
   build/install receipts without duplicating their ownership in M0.
4. Require M3, M4, and M5 receipts while preserving explicit closed-family
   capability state where admission proof did not pass.
5. Reconcile user docs, ADRs, capability reports, issue dependencies, and
   milestone pages with the same final state.
6. Retain the source program documents, mark them complete, and link their
   durable replacement rules and receipts.
7. Finish with a clean Git worktree, an independently reviewed handoff, and a
   closeout commit identity recorded outside that commit without
   self-reference.

## Non-Goals

- No model, solver, regression, packaging, or paper-specific implementation in
  the M0 closeout issue.
- No capability admission based only on a successful solver exit or sampled
  finite candidate set.
- No invention of scientific inputs, thresholds, provenance, or release
  support.
- No external package publication, PyPI release, or downstream repository
  mutation as part of this closeout.
- No deletion of the source specification or plan.
- No narrative-only declaration that substitutes for missing executable
  receipts.

## Alternatives

### One giant final command

Rejected. It obscures domain ownership, is difficult to resume, and cannot show
which scientific, package, or governance proof is missing.

### A prose completion checklist

Rejected. It can drift from current commands and cannot validate source
identity, artifacts, or dependency closure.

### A milestone-owned receipt graph with M0 reconciliation

Selected. Each domain proves what it owns. M0 validates references, requires
all blockers to be resolved, and records the exact final repository state.

## Selected Design

### Receipt hierarchy

The final machine-readable closeout receipt contains:

- schema version and stable program ID;
- source specification, plan, tested `proof_input_commit`, and branch;
- canonical closeout issue identity used for the later external commit record;
- M3 provider/model-input completion receipt;
- M4 equilibrium correctness, admission, and decomposition receipts;
- M5 regression correctness, evidence, and decomposition receipt;
- M6 scientific and capability validation receipt;
- M1 local Linux build, artifact, and isolated-install receipt;
- M0 maintainability/tracker receipt plus documentation, review, Git, and
  cleanup results;
- an empty blocker list and final status.

Each child receipt records its milestone, package, issue, commit, commands,
environment, result, and retained artifact paths. M0 references those facts; it
does not copy scientific tables or reclassify package capability records.

The `proof_input_commit` is the clean integrated commit whose package code,
child receipts, and selected proof commands are accepted before the final
status-only documentation change. The tracked receipt does not contain a
`closeout_commit` field: a commit cannot contain its own SHA without changing
that SHA.

### M6 scientific receipt

M6 records:

- named test/confidence lanes and activation/capability equality;
- fresh native-source identity for strict native checkers;
- the exact active M6 evidence lanes backing admitted or explicitly in-scope
  capabilities, with source/model tables, plots, and numerical receipts;
- an accepted M6 Gross/Sadowski Figures 2-9 public bubble/dew evidence-refresh
  receipt, or a separately reviewed M4 change that removes/replaces those
  capability evidence rows before closeout;
- explicit closed disposition for any non-admitted family;
- independent thermodynamic and code-review verdicts.

Every new or updated model-prediction plot has traceable real source data. The
final user handoff renders those plots with absolute paths and compact tables of
the retained source data.

### M1 local Linux receipt

M1 records:

- declared Linux environment and compatibility policy;
- provider-only, provider plus equilibrium, provider plus regression, and
  all-package artifacts;
- isolated installs without checkout imports or host library-path assistance;
- representative native smokes, ELF/runtime-path audit, wheel tags, package
  versions, dependency closure, and the active Python 3.13 result;
- explicit local failure for any declared install combination, without changing
  broader package support metadata in this private-workflow gate.

This receipt is local build/install evidence. External publishing and
downstream release choreography remain separate release work.

### M0 closeout record and commit identities

M0 writes a durable receipt under the M0 milestone registry and a human-readable
summary in the M0 milestone documentation. Both identify the tested
`proof_input_commit`, the canonical closeout issue, and every child receipt.

The source specification and plan receive a Complete status block naming the
completion date, tested proof-input identity, M0 receipt, grouped replacement
artifacts, and their historical rather than active-queue role.

After those tracked closeout files are committed, the resulting
`closeout_commit` SHA is recorded in the canonical GitHub closeout issue and in
the final handoff. A separate live reconciliation verifies that the externally
recorded SHA exists, is descended from `proof_input_commit`, changes only the
declared closeout files, and matches the clean local `HEAD`. This post-commit
record does not rewrite the tracked receipt and therefore cannot be
self-referential. If external tracker mutation is not authorized or available,
the process stops at `proof_complete` and does not claim final closeout.

## Ownership

- M0 Governance owns the closeout schema, dependency graph, final receipt,
  document status transition, and tracker reconciliation.
- M1 Packages owns local Linux artifact and isolated-install proof.
- M3 EOS owns provider and resolved model-input correctness.
- M4 Equilibrium owns selector admission, residual proof, and decomposition.
- M5 Regression owns problem correctness, evidence, Ceres results, and
  decomposition.
- M6 Validation owns literature/checker/capability evidence and scientific
  artifact review.

Every issue has one milestone. The M0 closeout issue is blocked by the
milestone-owned issues; it does not absorb their file scope.

## Interfaces

Receipts use versioned structured data with required fields for identity,
commands, environment, outputs, artifacts, result, `proof_input_commit`, and
canonical closeout issue. References use repository-relative paths and
immutable commits. `closeout_commit` is deliberately excluded from tracked
receipt fields and is validated through the separate external record.

The closeout validator rejects unknown schemas or result states, missing
identities or artifacts, duplicate ownership, stale native-source identity,
uncollected proof nodes, missing plotted source data, incomplete capability
evidence, an absent `proof_input_commit`, any tracked self-referential
`closeout_commit` field, and any complete status with a blocker. The separate
live reconciler rejects a missing or mismatched external closeout record.

## Data Flow

1. Each prerequisite milestone issue produces its owned receipt at an accepted
   commit.
2. M0 integrates the accepted children and creates one clean
   `proof_input_commit`.
3. The M0 validator loads the receipt graph and verifies paths, identities,
   issue relationships, results, and selected proof at that commit.
4. M6 inspects scientific artifacts and M1 verifies isolated Linux artifacts.
5. M0 reconciles docs, ADRs, capabilities, milestone pages, and issue
   readiness, then marks the source program documents complete in the working
   tree.
6. Documentation/static/cleanup proof passes and those declared closeout-only
   files are committed once.
7. The resulting `closeout_commit` is recorded in the canonical GitHub issue;
   separate live reconciliation verifies it without editing tracked files.

## Error Handling

- Any missing, failing, stale, or inconsistent receipt leaves the program open
  and emits an exact blocker.
- A deliberately closed capability is accepted only when every public and
  evidence surface agrees that it is closed.
- Failed proof cannot be converted into completion by weakening its checker;
  scope changes require a reviewed decision.
- M0 never edits child numerical results or substitutes a new default.
- Cleanup never removes unowned work, stashes, or retained evidence.
- A missing external `closeout_commit` record leaves the state
  `proof_complete`; it is not represented by guessing a SHA in a tracked file.

## Stop Gates

- All issues selected into the active program graph are complete at the final
  integrated commit. Gross/Sadowski Figures 2-9 evidence backing currently
  exposed bubble/dew routes is active, while Khudaida and paper work unrelated
  to an exposed capability may remain listed as deferred and nonblocking.
- M6 scientific/capability proof has fresh native identity.
- M1 Linux proof covers every declared local combination on the active Python
  runtime.
- M0 ownership ratchets and repository structure validation pass.
- Documentation and capability claims match runtime activation exactly.
- Independent code and thermodynamic reviews report no unresolved blocking
  P0/P1 finding.
- No required plot, source table, checker receipt, or issue dependency is
  missing.
- Git status is clean after repository-scoped cleanup.
- The external tracker records the actual closeout commit and the separate
  reconciliation verifies it against local `HEAD`.

## Testing

- Receipt-schema mutation tests for missing/stale records, artifacts, proof
  nodes, blockers, false complete states, absent proof-input identity, and a
  forbidden tracked closeout-commit field.
- External-record tests reject a nonexistent SHA, wrong ancestry, changes
  outside the declared closeout-only files, and a SHA different from local
  `HEAD`.
- Bare and official full collection parity.
- Full, confidence, equilibrium-confidence, regression, integration, and docs
  validation lanes as registered by the repository.
- Activation generation and every strict checker backing an exposed
  capability.
- Only the paper-analysis lanes selected by the active M6 issue graph. This
  includes the focused Gross/Sadowski Figures 2-9 refresh required by current
  bubble/dew capability evidence; deferred Khudaida, Gross work unrelated to
  exposed routes, and other non-admitted bundles remain explicit follow-ups.
- M1 artifact matrix, isolated installs, ELF/runtime-path checks, and the active
  Python-runtime proof.
- Ruff format/check, strict Sphinx, shell and structured-data validation,
  diff check, cleanup, and final Git status.

The final proof runs from a fresh native build wherever the owning checker
requires native freshness.

## Cutover

1. Create the M0 tracker with dependencies on every grouped milestone issue.
2. Add the receipt schema and fail it against incomplete program state.
3. Accept M6 and M1 child receipts only after their own issue gates pass.
4. Commit the integrated input state, record its SHA as
   `proof_input_commit`, and run the integrated proof and independent reviews.
5. Move durable rules into canonical docs/tests, then mark the source
   specification and plan Complete and link the proof receipt.
6. Commit only the declared closeout files, record that actual SHA in the
   external closeout issue, reconcile it live, and report the clean,
   no-publication handoff.

## Risks

- Receipt paperwork may drift from execution. Control: require commands,
  immutable identities, and validated paths.
- Heavy proof may be inconsistent. Control: M6 and M1 own reproducible
  subreceipts.
- Closed capabilities may be mistaken for failure. Control: completion means
  agreement across declarations, execution, and evidence, not maximum feature
  breadth.
- Old documents may look active. Control: prominent Complete status and links.
- A tracked receipt cannot name its own containing commit. Control: bind proof
  to `proof_input_commit`, record the later closeout commit externally, and
  reconcile ancestry and changed paths after the commit exists.
- Local Linux success may be misrepresented as publication support. Control:
  M1 receipt scope is explicit and external release work stays separate.

## Closeout-Time Facts

No material closeout decision remains. The implementation plan will record the
final issue numbers, exact `proof_input_commit`, canonical external closeout
record, and measured artifact identities produced by the milestone-owned proof
runs.

## Decision Ledger

| Decision | Evidence | Resolution | Owner |
| --- | --- | --- | --- |
| Use M0 as closeout parent | M0 owns completion rules and cross-repository gates | M0 validates, links, and reconciles milestone receipts | M0 |
| Keep domain proof milestone-owned | ADR 0005 and issue-tracker package boundaries | M3/M4/M5/M6/M1 produce their own receipts | All milestones |
| Use M6 for scientific proof | M6 owns executable literature and capability evidence | M0 consumes the accepted M6 receipt | M6 |
| Use M1 for local Linux proof | M1 owns package layout, extension boundaries, and install proof | M0 consumes the accepted local Linux receipt | M1 |
| Accept evidence-backed closed states | Public admission requires complete selector and scientific proof | Closed, aligned capability state can complete | M4/M6 |
| Retain source documents | Explicit user direction supersedes earlier deletion wording | Mark Complete and link receipts; never delete | M0 |
| Avoid commit self-reference | A commit SHA changes when tracked receipt content changes | Store `proof_input_commit`; record `closeout_commit` externally after commit | M0 |
| Keep publication separate | Local correctness proof is not a release event | No PyPI or downstream publication in closeout | M0/M1 |
