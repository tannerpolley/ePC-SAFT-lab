# M0 Validation Correctness Program Closeout Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> `superpowers:subagent-driven-development` (recommended) or
> `superpowers:executing-plans` to implement this plan task-by-task. Steps use
> checkbox (`- [ ]`) syntax for tracking. Use
> `superpowers:test-driven-development`,
> `superpowers:systematic-debugging` for any failed receipt or proof command,
> and `superpowers:verification-before-completion` before the final status
> transition.

**Goal:** Close the Tasks 9-22 validation-correctness program from exact
milestone-owned receipts without absorbing release work, unrelated deferred
paper work, or package implementation into M0.

**Architecture:** A versioned M0 receipt graph references accepted M1, M3, M4,
M5, M6, and M0 evidence by immutable commit, issue, command, and artifact path.
A pure checker rejects stale, missing, conflicting, or blocked children and
binds proof to one clean `proof_input_commit`. The later closeout-only commit
is recorded in the canonical GitHub issue after it exists and verified by a
separate reconciler, so no tracked receipt tries to contain its own SHA.

**Tech Stack:** Python 3.13 repository runtime, YAML/JSON, pytest, repository
validation registry, Ruff, Sphinx, Git, and GitHub issue dependency evidence.

## Global Constraints

- This M0 plan implements no EOS, equilibrium, regression, packaging, or
  paper-specific numerical change.
- Deferred Khudaida, electrolyte, and Gross work unrelated to an exposed
  capability is recorded as deferred. The focused M6 Gross/Sadowski Figures
  2-9 evidence refresh remains active because current public associating
  bubble/dew capability rows cite it.
- Future equilibrium admission leaves are not closeout blockers when runtime,
  API, docs, and evidence consistently keep those families closed.
- M1 proves only the current local Linux/Python 3.13 workflow; it does not add
  manylinux, PyPI, multi-Python, or downstream release claims.
- A finite sampled candidate set never establishes phase-set completeness.
- Missing receipts, source data, plots, issue edges, or review findings fail
  loudly; no fallback values or relaxed checkers are allowed.
- The tracked receipt records `proof_input_commit` and the canonical closeout
  issue, never a self-referential `closeout_commit`; the actual closeout SHA is
  recorded and reconciled externally after commit.
- The July 9 source spec and plan are retained and marked Complete, never
  deleted or rewritten out of history.

---

## Source Evidence

- Approved source:
  `docs/superpowers/specs/2026-07-10-m0-validation-correctness-program-closeout.md`.
- Roadmap reconciliation:
  `docs/superpowers/specs/2026-07-10-m0-validation-correctness-tasks-9-22-roadmap-reconciliation.md`.
- Historical source program:
  `docs/superpowers/specs/2026-07-09-m3-core-repository-truth-and-scientific-integrity-program.md`
  and its matching plan.
- Canonical validation command registry:
  `scripts/dev/validation_registry.py`.
- Historical milestone and dependency policy recorded by the retained issue
  graph.
- Required child evidence comes only from the terminal leaves selected in the
  published Tasks 9-22 issue graph.
- The focused Gross public-route prerequisite is defined by
  `docs/superpowers/specs/2026-07-10-m6-gross-2002-public-bubble-dew-evidence-refresh.md`
  and its matching M6 plan.

## Test Complete And Metrics

- Receipt-schema mutations reject absent child receipts, wrong commits,
  duplicate milestone ownership, stale artifact hashes, unknown statuses,
  unresolved blockers, a missing proof-input identity, a forbidden tracked
  closeout-commit field, and a Complete state with any failed command.
- External-record mutations reject a nonexistent closeout SHA, wrong ancestry,
  changes outside the declared closeout files, or a SHA different from local
  `HEAD`.
- Closed-capability tests accept only exact agreement among activation,
  capabilities, docs, tests, and retained evidence.
- The checker validates only the active M6 evidence lanes, including the
  focused Gross/Sadowski Figures 2-9 receipt backing current bubble/dew
  capability rows, and reports unrelated deferred paper bundles separately.
- M1 receipt covers four local install combinations on the active Python 3.13
  runtime without interpreting package metadata as tested breadth.
- Independent code and thermodynamic reviews have no unresolved blocking P0/P1
  finding.
- Selected provider, equilibrium, regression, M6, local-Linux, docs, Ruff,
  diff, cleanup, and Git-state proof all pass for the declared
  `proof_input_commit` and closeout-only working tree as specified below.

## Outcome Proof

**Intent:** Provide one reproducible answer to whether every active Tasks 9-22
contract is complete or explicitly closed at the integrated local commit.

**Current Behavior:** Requirements and evidence are distributed across package
tests, M6 artifacts, local package scripts, issue relationships, and historical
program documents; there is no single validated receipt graph.

**Expected Outcome:** M0 validates immutable child receipts, an empty active
blocker set, exact selected commands, aligned capability states, one tested
`proof_input_commit`, and an externally recorded closeout-only commit before
the historical program is reported finally closed.

**Target Output:** A version-1 closeout YAML, strict checker, external-record
reconciler, mutation tests, registered local closeout command, updated M0
documentation, and linked Complete status blocks on the historical spec and
plan.

**Owner:** M0 Governance owns the graph, checker, final documentation state, and
tracker reconciliation; each milestone retains ownership of its child receipt.

**Interface:** `uv run --no-sync python scripts/validation/check_validation_correctness_closeout.py --json --require-complete`,
`evaluate_closeout(repo_root: Path, payload: Mapping[str, object]) ->
CloseoutResult`, and the post-commit
`uv run --no-sync python scripts/validation/reconcile_validation_closeout_record.py --json --check`.

**Cutover:** The historical July 9 task list stops being an active queue only
after the checker passes, its documents link the accepted milestone plans,
issues, and receipt, and the external closeout record is reconciled.

**Replaced Path:** Narrative completion claims, giant unstructured final command
lists, and deleted-plan retirement are displaced by the validated receipt graph.

**Evidence:** Child receipt hashes and commits, `proof_input_commit`, GitHub
issue/dependency snapshot, selected command results, capability/activation
comparisons, retained M6 tables/plots, M1 ELF/install proof, independent
reviews, externally recorded closeout SHA, cleanup, and clean Git status.

**Acceptance Proof:** The checker returns `complete: true`, `blockers: []`, and
the tested `proof_input_commit`; every selected issue and child receipt matches
that commit or an explicitly accepted immutable prerequisite; all selected
commands pass; deferred work is named but not classified complete. After the
closeout-only commit, the separate reconciler verifies the external
`closeout_commit` record against local `HEAD`, ancestry, and changed paths.

**Stop Criteria:** Stop on any missing/stale receipt, active issue blocker,
P0/P1 review finding, capability mismatch, failed selected command, dirty
tracked worktree, unauthorized/unavailable external closeout recording, or
attempt to make deferred paper/release work appear done.

**Avoid:** Do not edit numerical child results, reroute ownership into M0,
weaken a checker, require every historical paper bundle, push, publish, or
delete the source program documents.

**Risk:** A closeout graph can drift into paperwork; immutable identities,
artifact existence/hash checks, executable commands, and package-owned results
make each record falsifiable.

## Implementation Boundaries

**Files To Create:** `docs/superpowers/milestones/M0-governance/validation-correctness-closeout.yaml`,
`scripts/validation/check_validation_correctness_closeout.py`,
`scripts/validation/reconcile_validation_closeout_record.py`, and
`tests/workflows/repo/test_validation_correctness_closeout.py`.

**Files To Modify:** `scripts/dev/validation_registry.py`,
`docs/superpowers/milestones/M0-governance/README.md`, the July 9 source spec
and plan status blocks, and the Tasks 9-22 reconciliation final-status section.

**Files To Avoid:** Package production code, native build sources, scientific
parameter/data files, retained prediction artifacts owned by M6, release
workflows, and downstream repositories.

**Source Of Truth:** Terminal milestone issues and their validated receipts;
package capability/activation sources remain authoritative for runtime state.

**Read Path:** Checker reads the M0 YAML, resolves child receipt paths and
hashes, verifies issue/dependency evidence, checks selected artifacts, and
compares all command/commit identities at `proof_input_commit`. After the
closeout commit exists, the separate reconciler reads the canonical issue's
versioned external record and verifies it against local Git history.

**Write Path:** Milestone owners write child receipts; the final M0 task writes
only the graph, status links, and human-readable closeout summary. After that
tracked change is committed, one explicit authorized tracker write records the
actual closeout SHA without modifying repository files.

**Integration Points:** Validation registry, M0 ownership ratchets, M1 local
Linux checker, M3/M4/M5 package receipts, M6 evidence checkers, GitHub issue
dependencies, docs, and cleanup hook.

**Migration Or Cutover:** Land the checker in incomplete mode, attach exact
terminal receipts after prerequisite issues close, create and test one clean
`proof_input_commit`, then atomically mark the historical documents Complete.
Commit those declared files once, record the resulting SHA externally, and
reconcile it without another tracked commit.

**Replaced Path Handling:** Retain historical content beneath a prominent
Complete/reconciliation block; remove no history and leave no alternate
closeout checklist active.

**Acceptance Proof Gate:** Checker, mutation tests, selected domain lanes,
strict docs, Ruff, diff, cleanup, independent review, and clean Git status must
all pass before the final checkpoint commit.

## Decision Ledger

| Decision | Evidence | Selected action | Consequence | Owner |
| --- | --- | --- | --- | --- |
| Closeout owner | Cross-milestone issue policy | M0 references milestone receipts | No package scope moves to M0 | M0 |
| Scientific scope | User private-workflow clarification plus current capability evidence | Use only the active M6 graph, including Gross Figures 2-9 while they back exposed bubble/dew routes | Unrelated deferred paper repairs do not re-enter | M0/M6 |
| Closed capabilities | Activation/evidence contract | Accept exact aligned closed state | Feature breadth is not forced | M4/M6 |
| Linux proof | Approved M1 spec | Current host/Python only | M7 release remains deferred | M1 |
| Review gate | Independent review policy | No unresolved blocking P0/P1 | Nonblocking notes remain recorded | M0 |
| Historical docs | Explicit user direction | Retain and mark Complete | Traceability is preserved | M0 |
| Git identity | A tracked file cannot contain the SHA of its own commit | Store `proof_input_commit`; record the closeout SHA externally after commit | No self-reference loop | M0 |
| Remote state | Git identity must be recorded after commit | One explicit authorized issue record; no branch push or publication | Tracker state records the commit without rewriting it | M0 |

### Task 1: Define The Closeout Receipt And Strict Checker

**Use Cases:**

- An incomplete child graph produces exact blocker evidence instead of a prose
  completion claim.
- A closed capability can complete only when every runtime and documentation
  surface agrees on the closed state.
- The new graph displaces giant narrative checklists while preserving each
  milestone's ownership.

**Files:**

- Create: `docs/superpowers/milestones/M0-governance/validation-correctness-closeout.yaml`
- Create: `scripts/validation/check_validation_correctness_closeout.py`
- Create: `scripts/validation/reconcile_validation_closeout_record.py`
- Create: `tests/workflows/repo/test_validation_correctness_closeout.py`

**Interfaces:**

- Consumes: a version-1 payload with `program`, `proof_input_commit`,
  `closeout_issue`, `child_receipts`, `selected_validation`, `deferred_work`,
  `reviews`, and `blockers`.
- Produces: `CloseoutResult` with `complete`, ordered `blockers`, child status,
  artifact checks, command evidence, and JSON rendering.

- [ ] **Step 1: Write RED schema and false-completion tests**

  Add a complete temporary payload fixture, then mutate each required field,
  `proof_input_commit`, hash, artifact, issue, command result, review verdict,
  closed-state agreement, and blocker. Require a Complete payload with a
  blocker or failed child to be rejected, and reject any tracked
  `closeout_commit` field.

- [ ] **Step 2: Run RED**

  ```bash
  uv run --no-sync pytest -q tests/workflows/repo/test_validation_correctness_closeout.py
  ```

  Expected: collection/import fails because the closeout checker and version-1
  receipt do not exist.

- [ ] **Step 3: Implement strict pure-data evaluation**

  Parse an exact key set, normalize repository-relative artifact paths, verify
  SHA-256 hashes and immutable commits, require one child per selected
  milestone/terminal issue, require `proof_input_commit`, reject a tracked
  closeout SHA, compare closed-capability fields, and keep `deferred_work`
  distinct from `blockers`. The checker never runs repair code or edits a child
  receipt. Add the separate external reconciler with injected GitHub responses
  in tests; its `--check` mode performs no writes.

- [ ] **Step 4: Run GREEN and static checks**

  ```bash
  uv run --no-sync pytest -q tests/workflows/repo/test_validation_correctness_closeout.py
  uv run --no-sync ruff check scripts/validation/check_validation_correctness_closeout.py scripts/validation/reconcile_validation_closeout_record.py tests/workflows/repo/test_validation_correctness_closeout.py
  ```

  Expected: every positive fixture passes, every mutation is rejected with an
  exact blocker, and Ruff exits zero.

- [ ] **Step 5: Checkpoint the incomplete gate**

  Commit the checker with the live receipt explicitly incomplete until child
  issues close:

  ```bash
  git add docs/superpowers/milestones/M0-governance/validation-correctness-closeout.yaml scripts/validation/check_validation_correctness_closeout.py scripts/validation/reconcile_validation_closeout_record.py tests/workflows/repo/test_validation_correctness_closeout.py
  git commit -m "test(governance): define program closeout receipt"
  ```

### Task 2: Attach Exact Milestone Receipts And Register The Gate

**Use Cases:**

- The closeout graph names only terminal active issues and accepted local proof,
  including the Gross Figures 2-9 public-route evidence leaf, while unrelated
  deferred paper and release issues remain visible but nonblocking.
- A stale native or artifact receipt is rejected before the final integrated
  validation run.
- One registered command replaces ad hoc closeout invocation paths.

**Files:**

- Modify: `docs/superpowers/milestones/M0-governance/validation-correctness-closeout.yaml`
- Modify: `scripts/dev/validation_registry.py`
- Modify: `tests/workflows/repo/test_validation_correctness_closeout.py`
- Modify: `docs/superpowers/milestones/M0-governance/README.md`

**Interfaces:**

- Consumes: accepted terminal M1/M3/M4/M5/M6/M0 receipts and native issue
  dependency evidence from the published hierarchy.
- Produces: a registered `program-closeout` validation lane whose checker reads
  the exact graph at the declared `proof_input_commit`.

- [ ] **Step 1: Add RED live-graph and registry tests**

  Require one exact terminal leaf per selected owner, reject broad backlog
  parents as substitutes, require the focused Gross public-route evidence leaf
  as active, require unrelated deferred paper issue IDs under `deferred_work`,
  and assert the validation registry exposes only the strict checker command.

- [ ] **Step 2: Confirm RED at incomplete program state**

  ```bash
  uv run --no-sync pytest -q tests/workflows/repo/test_validation_correctness_closeout.py -k "live_graph or registry"
  uv run --no-sync python scripts/validation/check_validation_correctness_closeout.py --json --require-complete
  ```

  Expected: tests identify missing integration; the live checker exits nonzero
  with exact not-yet-accepted child receipts, not paper-specific repair noise.

- [ ] **Step 3: Populate exact accepted references**

  After prerequisite issues close, record their issue numbers, milestones,
  commits, receipt paths, hashes, and selected commands. Add the registry lane
  and M0 documentation. Do not point at #195 or at broad #194 as a completion
  substitute; use accepted terminal evidence leaves.

- [ ] **Step 4: Verify the assembled graph**

  ```bash
  uv run --no-sync pytest -q tests/workflows/repo/test_validation_correctness_closeout.py
  uv run --no-sync python scripts/validation/check_validation_correctness_closeout.py --json
  ```

  Expected: tests pass; the checker reports only
  `proof_input_commit_missing` because every selected child and graph edge is
  accepted but the clean Task 2 checkpoint does not exist until Step 5 commits
  it.

- [ ] **Step 5: Review and checkpoint**

  Independently compare YAML references with issue relationships and child
  receipt hashes, then commit:

  ```bash
  git add docs/superpowers/milestones/M0-governance/validation-correctness-closeout.yaml scripts/dev/validation_registry.py tests/workflows/repo/test_validation_correctness_closeout.py docs/superpowers/milestones/M0-governance/README.md
  git commit -m "docs(governance): assemble validation closeout graph"
  ```

### Task 3: Run Integrated Proof And Retire The Historical Queue

**Use Cases:**

- The user receives one accepted local proof tied to a clean
  `proof_input_commit`, an externally recorded closeout commit, and exact
  milestone evidence.
- Historical Tasks 9-22 are retired as a queue without deleting their design or
  hiding deferred follow-ups.
- Final documentation and tracker state visibly replace the old program status
  only after executable acceptance evidence passes.

**Files:**

- Modify: `docs/superpowers/milestones/M0-governance/validation-correctness-closeout.yaml`
- Modify: `docs/superpowers/specs/2026-07-09-m3-core-repository-truth-and-scientific-integrity-program.md`
- Modify: `docs/superpowers/plans/2026-07-09-m3-core-repository-truth-and-scientific-integrity-program-plan.md`
- Modify: `docs/superpowers/specs/2026-07-10-m0-validation-correctness-tasks-9-22-roadmap-reconciliation.md`
- Modify: `docs/superpowers/milestones/M0-governance/README.md`

**Interfaces:**

- Consumes: passing Task 2 graph, selected validation commands, independent
  review verdicts, cleanup audit, and a clean Task 2 `HEAD` suitable for
  `proof_input_commit`.
- Produces: final Complete graph/status blocks, one closeout-only local commit,
  its external tracker record, and a clean local handoff; no remote push.

- [ ] **Step 1: Establish and prove the proof-input commit**

  Require a clean Task 2 `HEAD`, record that immutable SHA as
  `proof_input_commit`, and execute the exact commands recorded by accepted
  child receipts from that commit: M3 provider input/derivative gates, M4
  exposed-route and CE closed/admitted-state gates, M5 native-problem and scoped
  admission gates, active M6 evidence checkers including the Gross Figures 2-9
  public bubble/dew refresh, M1 local artifact checker, and M0 ratchets. Any
  failure returns to its owning issue; M0 does not patch it.

- [ ] **Step 2: Obtain independent code and thermodynamic reviews**

  Give reviewers the graph, child receipts, selected commands, capability
  comparison, retained plots/tables, `proof_input_commit`, and deferred list.
  Require no unresolved blocking P0/P1 finding; record nonblocking findings
  with owners.

- [ ] **Step 3: Mark only the declared closeout files Complete**

  Set `proof_input_commit` and Complete status in the M0 receipt. Add the final
  date, proof-input identity, issue, receipt path, replacement plan set,
  explicit closed capability state, and deferred follow-ups to both July 9
  documents and the reconciliation. Retain all historical content below the
  status block. Do not add a `closeout_commit` field or guessed SHA to any
  tracked file.

- [ ] **Step 4: Verify the closeout-only tree and commit it once**

  ```bash
  uv run --no-sync python scripts/validation/check_validation_correctness_closeout.py --json --require-complete
  uv run --no-sync python scripts/dev/validate_project.py docs
  uv run --no-sync pytest -q tests/workflows/repo/test_project_structure.py tests/workflows/repo/test_validation_correctness_closeout.py
  uv run --no-sync ruff check scripts/validation/check_validation_correctness_closeout.py scripts/validation/reconcile_validation_closeout_record.py tests/workflows/repo/test_validation_correctness_closeout.py
  git diff --check
  bash "$HOME/.codex/hooks/codex-cleanup.sh" --repo-root .
  uv run --no-sync python scripts/validation/reconcile_validation_closeout_record.py --json --check-working-tree
  git add docs/superpowers/milestones/M0-governance/validation-correctness-closeout.yaml docs/superpowers/milestones/M0-governance/README.md docs/superpowers/specs/2026-07-09-m3-core-repository-truth-and-scientific-integrity-program.md docs/superpowers/plans/2026-07-09-m3-core-repository-truth-and-scientific-integrity-program-plan.md docs/superpowers/specs/2026-07-10-m0-validation-correctness-tasks-9-22-roadmap-reconciliation.md
  git commit -m "docs(governance): close validation correctness program"
  ```

  Expected: checker/docs/tests/Ruff/diff pass; only the declared closeout files
  differ from `proof_input_commit`; cleanup has no task-owned residue; and the
  commit succeeds without changing the receipt's proof-input identity.

- [ ] **Step 5: Record and reconcile the actual closeout commit externally**

  ```bash
  uv run --no-sync python scripts/validation/check_validation_correctness_closeout.py --json --require-complete
  uv run --no-sync python scripts/validation/reconcile_validation_closeout_record.py --json --record-head
  uv run --no-sync python scripts/validation/reconcile_validation_closeout_record.py --json --check
  git status --short
  ```

  Run `--record-head` only with explicit tracker-write authority. Expected: the
  versioned GitHub issue record names local `HEAD` as `closeout_commit`, the
  reconciler verifies its ancestry from `proof_input_commit` and the exact
  closeout-only path set, and Git status is empty. Do not push as part of this
  plan. If the external record cannot be written or verified, report
  `proof_complete` and stop before claiming final closeout.

## Proof Oracle

Closeout succeeds only when the strict graph reports Complete for
`proof_input_commit`, selected active evidence passes, closed capabilities
agree across all surfaces, deferred work remains explicit and nonblocking,
independent reviews have no blocking P0/P1 finding, source documents are
retained with Complete links, the actual closeout commit is recorded and
reconciled externally without self-reference, cleanup passes, and the worktree
is clean.
