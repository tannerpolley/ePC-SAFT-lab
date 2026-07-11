# M0 Characterized Ownership And Maintainability Ratchets Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> `superpowers:subagent-driven-development` (recommended) or
> `superpowers:executing-plans` to implement this plan task-by-task. Steps use
> checkbox (`- [ ]`) syntax for tracking. Use
> `superpowers:test-driven-development` for every change,
> `superpowers:systematic-debugging` for unexpected failures, and
> `superpowers:verification-before-completion` before closing a task.

**Goal:** Add one repository-owned, package-aware ownership and structural
ratchet gate that prevents oversized production owners from growing while
preserving package ownership of scientific and capability evidence.

**Architecture:** M0 stores a versioned index of package-owned ownership sources
and measured file baselines plus a versioned local accountability snapshot. A
pure-Python validator checks source uniqueness, tracked-path existence,
locally resolvable issue-or-ADR evidence, no-growth, and ratchet-on-shrink
behavior without importing native extensions or using the network. A separate
explicit command reconciles issue snapshot/mirror records with live GitHub
state.

**Tech Stack:** Python 3.13 repository runtime, YAML, pytest, Ruff, Sphinx, Git,
and the existing `scripts/dev/validate_project.py` orchestration.

## Global Constraints

- M0 changes governance schemas, validation, and documentation only; it does
  not decompose production code or change numerical behavior.
- Package-owned M3, M4, and M5 records remain authoritative for runtime and
  scientific ownership.
- Required order is M0 schema/validator -> package characterization, including
  M4 -> M0 activation/cutover -> M4 extraction.
- A new production file above 1,000 lines requires an accepted ADR; an indexed
  oversized file may not exceed its measured maximum.
- A file that shrinks must ratchet its maximum downward in the same change.
- Do not snapshot known-defective Task 9-15 behavior as a compatibility target.
- Do not add wrappers, automatic baseline rewrites, capability admissions,
  parameter values, or paper-specific repairs.

---

## Source Evidence

- Approved source:
  `docs/superpowers/specs/2026-07-10-m0-characterized-ownership-and-maintainability-ratchets.md`.
- Existing provider structural gate:
  `tests/workflows/repo/test_project_structure.py::test_m3_provider_source_files_stay_below_large_file_limit`.
- Existing M4 capability owner:
  `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/capability_evidence.py`.
- Existing shared M4 contract foundation: closed issue #362.
- Provider decomposition foundation: merged PR #203.
- Deferred owner inputs: the accepted M3 model-input, M5 regression-contract,
  and M4 characterization plans produce their package records before
  activation. M4 extraction begins only after the activated shared gate.

## Test Complete And Metrics

- Schema mutations reject unknown versions, duplicate IDs, missing source
  paths, conflicting public owners, and invalid visibility values.
- Structural mutations reject growth above the recorded maximum, stale maxima
  after shrink, missing owner evidence, new unapproved files above 1,000 lines,
  and stale paths after rename/removal.
- Accountability mutations reject missing stable IDs, unresolved issue
  mirrors/ADRs, duplicate canonical identifiers, and mirror/snapshot mismatch.
- The pure validator never accesses the network; a separately tested live
  reconciliation command reports tracker drift and never rewrites local files.
- `--report-candidates` is read-only and deterministically reports tracked line
  counts; no command edits the index automatically.
- Repository structure tests, the M0 validator, strict docs, Ruff, diff checks,
  and cleanup all pass.
- Numerical package confidence/checker results remain unchanged because this
  plan moves no production behavior.

## Outcome Proof

**Intent:** Make large-owner debt and public-to-native ownership mechanically
reviewable without treating line count as a scientific quality metric.

**Current Behavior:** The provider has a fixed source-size assertion, M4 has a
capability evidence map, and other oversized owners have no shared baseline,
owner record, or ratchet rule.

**Expected Outcome:** One M0 validator reads package-owned sources, rejects
ambiguous ownership and structural growth, and requires every indexed exception
to name a locally resolvable active decomposition issue or accepted ADR while
the separate reconciler detects live issue drift.

**Target Output:** A version-1 ownership/ratchet index, version-1 local
accountability snapshot, pure-Python validator, separate live reconciler,
mutation tests, repository-validation integration, and documented update
workflow.

**Owner:** M0 Governance owns the index, validator, and policy; M3, M4, and M5
own the referenced package records.

**Interface:** `uv run --no-sync python scripts/dev/validate_ownership_ratchets.py --json`
and `validate_index(repo_root: Path, payload: Mapping[str, object],
accountability: Mapping[str, object]) -> ValidationResult`. Live tracker drift
is checked separately with
`uv run --no-sync python scripts/dev/reconcile_ownership_accountability.py --json --check`.

**Cutover:** The shared validator replaces the provider-only hard-coded size
check only after its initial index enforces equal or stricter provider limits.

**Replaced Path:** Hard-coded, package-specific size thresholds without an
owner, issue/ADR record, or ratchet-on-shrink rule are removed after parity.

**Evidence:** Mutation-test JSON, deterministic candidate reports, exact index
entries, versioned local accountability records and mirrors, separate live
reconciliation output, package-owner source paths, repository structure tests,
and strict documentation proof.

**Acceptance Proof:** Every indexed file is at or below its current maximum,
every oversized entry has one accountable owner and issue/ADR, all declared
ownership sources exist and validate, and mutations of each rule fail with the
expected path-specific diagnostic.

**Stop Criteria:** Stop activation when a package owner source is absent,
known-defective behavior would be frozen, a local accountability record cannot
be resolved, live tracker reconciliation reports drift, or the shared gate
would weaken an existing package check.

**Avoid:** Do not auto-edit baselines, duplicate capability facts in M0, use
branch-relative merge-base logic, or split files mechanically to satisfy a
number.

**Risk:** A structural index can become paperwork or encourage shallow file
splits; package characterization, issue/ADR accountability, and ratchet-only
updates keep the gate tied to real ownership improvements.

## Implementation Boundaries

**Files To Create:** `docs/superpowers/milestones/M0-governance/ownership-ratchets.yaml`,
`docs/superpowers/milestones/M0-governance/ownership-accountability.yaml`,
`scripts/dev/validate_ownership_ratchets.py`,
`scripts/dev/reconcile_ownership_accountability.py`, and
`tests/workflows/repo/test_ownership_ratchets.py`.

**Files To Modify:** `scripts/dev/validate_project.py`,
`tests/workflows/repo/test_project_structure.py`,
`docs/pages/development_workflows.rst`, and
`docs/superpowers/milestones/M0-governance/README.md`.

**Files To Avoid:** Production files under `packages/**`, scientific data,
capability activation tables, retained plots, and paper-validation inputs.

**Source Of Truth:** Package-owned ownership/capability records plus the
versioned M0 index for structural baselines only. GitHub remains authoritative
for live issue state; the versioned local snapshot is deterministic gate input,
not a competing tracker.

**Read Path:** Validator loads the M0 index and accountability snapshot,
resolves tracked paths and issue mirrors/ADRs, loads each declared package
source as pure data, measures line counts, and emits ordered diagnostics. The
separate reconciler queries GitHub only when explicitly invoked.

**Write Path:** Humans update package records, the M0 index, and the local
accountability snapshot/mirrors in reviewed changes; validation and live
reconciliation never write the repository.

**Integration Points:** `scripts/dev/validate_project.py`, repository structure
tests, package capability evidence, issue/ADR links, and milestone docs.

**Migration Or Cutover:** Land schema/validator first, wait for corrected
package owner sources and M4 characterization, reconcile the local snapshot,
activate measured baselines, retire the displaced provider-only literal
threshold, then unblock M4 extraction.

**Replaced Path Handling:** Delete the old hard-coded provider check only in
the activation commit that demonstrates parity through mutation tests.

**Acceptance Proof Gate:** The focused validator/test suite, all repository
structure tests, strict Sphinx, Ruff, `git diff --check`, cleanup, and an
independent review must pass before each checkpoint closes.

## Decision Ledger

| Decision | Evidence | Selected action | Consequence | Owner |
| --- | --- | --- | --- | --- |
| Shared gate owner | M0 issue policy | M0 owns schema/index/validator | Package implementation stays milestone-owned | M0 |
| Capability facts | ADR 0005 and package reports | Store pointers, not copied claims | No second capability registry | M0/M3/M4/M5 |
| File threshold | Approved spec | 1,000 lines is a new-file review gate | Existing owners use measured maxima | M0 |
| Existing debt | Current hotspots | Baseline then no-growth/ratchet | No forced mechanical rewrite | Package owners |
| Activation order | Tasks 9-15 change behavior | Characterize corrected contracts first | Known defects are not frozen | M3/M4/M5 |
| Accountability evidence | Pure validation cannot prove live issue state | Validate versioned local records; reconcile GitHub separately | Routine validation stays deterministic | M0 |
| Cross-plan dependency | M4 characterization consumes the schema while activation consumes its records | Schema -> characterization -> activation -> extraction | No circular prerequisite | M0/M4 |
| Baseline updates | Reproducibility requirement | Manual reviewed edits only | Validator has no write mode | M0 |

### Task 1: Define The Versioned Schemas And Pure Validator

**Use Cases:**

- A reviewer receives path-specific schema evidence before any baseline is
  activated.
- An invalid or duplicate owner record is rejected without importing a native
  module.
- An accountability ID resolves through a tracked issue mirror or ADR without
  contacting GitHub.
- The new validator can later replace package-specific structural checks
  without keeping a duplicate decision path.

**Files:**

- Create: `docs/superpowers/milestones/M0-governance/ownership-ratchets.yaml`
- Create: `docs/superpowers/milestones/M0-governance/ownership-accountability.yaml`
- Create: `scripts/dev/validate_ownership_ratchets.py`
- Create: `scripts/dev/reconcile_ownership_accountability.py`
- Create: `tests/workflows/repo/test_ownership_ratchets.py`

**Interfaces:**

- Consumes: repository root, a version-1 index with `ownership_sources` and
  `oversized_files` arrays, and a version-1 accountability snapshot with
  `records` containing stable GitHub-issue or ADR identifiers.
- Produces: `validate_index(repo_root, payload, accountability) ->
  ValidationResult`, CLI `--json`, read-only `--report-candidates` output, and a separate
  `reconcile_ownership_accountability.py --json --check` command.

- [ ] **Step 1: Write RED schema and determinism tests**

  Add tests that load a minimal valid temporary index and accountability
  snapshot, then mutate schema version, IDs, paths, owners, visibility,
  accountability references, mirror/ADR fields, and record order. Assert
  ordered diagnostics such as `duplicate_record_id:<id>`,
  `unknown_accountability_id:<id>`, and
  `missing_referenced_path:<path>`.

- [ ] **Step 2: Run the RED tests**

  Run:

  ```bash
  uv run --no-sync pytest -q tests/workflows/repo/test_ownership_ratchets.py
  ```

  Expected: collection or import fails because
  `scripts.dev.validate_ownership_ratchets`, the version-1 files, and the
  reconciliation command do not yet exist.

- [ ] **Step 3: Implement the smallest pure-data contract**

  Define frozen result/diagnostic records, strict top-level and nested key
  sets, stable path normalization relative to the repository root, duplicate
  detection, local mirror/ADR resolution, and JSON rendering. Start with no
  newly activated cross-package baselines, so existing package checks remain
  authoritative during characterization. `--report-candidates` reads only
  tracked production paths and returns sorted path/count rows; it has no update
  flag. The live reconciler accepts injected tracker JSON in tests, compares it
  with the local snapshot/mirror, and has no apply mode.

- [ ] **Step 4: Run GREEN and static checks**

  ```bash
  uv run --no-sync pytest -q tests/workflows/repo/test_ownership_ratchets.py
  uv run --no-sync ruff check scripts/dev/validate_ownership_ratchets.py scripts/dev/reconcile_ownership_accountability.py tests/workflows/repo/test_ownership_ratchets.py
  ```

  Expected: all focused tests pass, candidate order is stable, and Ruff exits
  zero.

- [ ] **Step 5: Refactor and checkpoint**

  Extract parsing from validation only if tests show a distinct owner; rerun
  Step 4 and commit:

  ```bash
  git add docs/superpowers/milestones/M0-governance/ownership-ratchets.yaml docs/superpowers/milestones/M0-governance/ownership-accountability.yaml scripts/dev/validate_ownership_ratchets.py scripts/dev/reconcile_ownership_accountability.py tests/workflows/repo/test_ownership_ratchets.py
  git commit -m "test(governance): define ownership ratchet contract"
  ```

### Task 2: Activate Measured Ownership Sources And Structural Ratchets

**Use Cases:**

- A package owner can see the accepted maximum, current count, issue/ADR, and
  characterization evidence for every oversized production file.
- A one-line growth or stale post-shrink maximum produces executable rejection
  evidence.
- Corrected M3/M4/M5 ownership sources displace informal prose without copying
  their scientific claims into M0.
- The M4 characterization task has completed against Task 1's schema, so
  activation consumes records that already exist instead of creating a cycle.

**Files:**

- Modify: `docs/superpowers/milestones/M0-governance/ownership-ratchets.yaml`
- Modify: `docs/superpowers/milestones/M0-governance/ownership-accountability.yaml`
- Modify: `tests/workflows/repo/test_ownership_ratchets.py`
- Read only: package-owned M3, M4, and M5 ownership/capability sources delivered
  by their prerequisite issues

**Interfaces:**

- Consumes: `--report-candidates` output, accepted package owner records at the
  integrated commit, including the M4 characterization receipt, and a local
  accountability snapshot whose issue entries pass live reconciliation.
- Produces: a complete version-1 index with exact measured maxima and validated
  package source pointers.

- [ ] **Step 1: Add RED mutation tests for every ratchet rule**

  In temporary repositories, grow an indexed file by one line, shrink without
  lowering its maximum, add an unindexed production file above 1,000 lines,
  replace its accountability ID with an unknown record, mismatch an issue
  mirror, remove an ADR path, rename a tracked path, and declare conflicting
  public owners. Assert the exact current/permitted counts, owner, and local
  accountability identifier in each diagnostic.

- [ ] **Step 2: Confirm the mutations fail**

  ```bash
  uv run --no-sync pytest -q tests/workflows/repo/test_ownership_ratchets.py -k "growth or shrink or oversized or owner"
  ```

  Expected: new mutation tests fail because measurement and active-index rules
  are not yet enforced.

- [ ] **Step 3: Measure and commit the accepted index**

  Run the separate live reconciliation command and require zero drift. Then run
  the read-only report on the exact integrated commit, copy its counts into the
  YAML, add the characterized package source paths and stable local
  accountability IDs, and implement no-growth, ratchet-on-shrink, new-file,
  rename/removal, and local-accountability checks. Do not use historical counts
  or rounded values.

- [ ] **Step 4: Verify the activated index**

  ```bash
  uv run --no-sync python scripts/dev/reconcile_ownership_accountability.py --json --check
  uv run --no-sync python scripts/dev/validate_ownership_ratchets.py --json
  uv run --no-sync pytest -q tests/workflows/repo/test_ownership_ratchets.py
  ```

  Expected: validator reports `ok: true`; every mutation test passes by
  rejecting its bad fixture.

- [ ] **Step 5: Review and checkpoint**

  Independently compare each measured count with `wc -l` on the indexed path,
  rerun Task 2 proof, and commit:

  ```bash
  git add docs/superpowers/milestones/M0-governance/ownership-ratchets.yaml docs/superpowers/milestones/M0-governance/ownership-accountability.yaml scripts/dev/validate_ownership_ratchets.py scripts/dev/reconcile_ownership_accountability.py tests/workflows/repo/test_ownership_ratchets.py
  git commit -m "build(governance): activate maintainability ratchets"
  ```

### Task 3: Cut Repository Validation Over To The Shared Gate

**Use Cases:**

- Developers run one documented validator and receive the same ownership and
  structural proof locally and in repository validation.
- The provider-only threshold is retired only after parity evidence exists.
- Milestone documentation makes the replacement path and baseline-update rule
  visible without implying a numerical capability change.

**Files:**

- Modify: `scripts/dev/validate_project.py`
- Modify: `tests/workflows/repo/test_project_structure.py`
- Modify: `tests/workflows/repo/test_ownership_ratchets.py`
- Modify: `docs/pages/development_workflows.rst`
- Modify: `docs/superpowers/milestones/M0-governance/README.md`

**Interfaces:**

- Consumes: the passing M0 validator and active index from Task 2.
- Produces: one `validate_project.py` governance invocation and documented
  update/cutover workflow. This checkpoint completes M0 activation and unblocks
  M4 extraction tasks; it does not rerun M4 characterization.

- [ ] **Step 1: Add RED orchestration and parity tests**

  Require repository validation to invoke the M0 command, require the shared
  index to include the exact provider files/limits formerly hard-coded, and
  reject any surviving second literal threshold owner after cutover.

- [ ] **Step 2: Prove the old orchestration fails the new contract**

  ```bash
  uv run --no-sync pytest -q tests/workflows/repo/test_project_structure.py tests/workflows/repo/test_ownership_ratchets.py
  ```

  Expected: the new orchestration/parity assertions fail while the focused
  validator remains green.

- [ ] **Step 3: Integrate and delete the displaced check**

  Add the governance command to `validate_project.py`, document the read-only
  report/manual update workflow, and remove
  `test_m3_provider_source_files_stay_below_large_file_limit` only after its
  paths and maxima are enforced by the shared mutation-tested index.

- [ ] **Step 4: Run the complete M0 proof**

  ```bash
  uv run --no-sync python scripts/dev/reconcile_ownership_accountability.py --json --check
  uv run --no-sync python scripts/dev/validate_ownership_ratchets.py --json
  uv run --no-sync pytest -q tests/workflows/repo/test_ownership_ratchets.py tests/workflows/repo/test_project_structure.py
  uv run --no-sync python scripts/dev/validate_project.py docs
  uv run --no-sync ruff check scripts/dev/validate_ownership_ratchets.py scripts/dev/reconcile_ownership_accountability.py tests/workflows/repo/test_ownership_ratchets.py
  git diff --check
  bash "$HOME/.codex/hooks/codex-cleanup.sh" --repo-root .
  ```

  Expected: validator `ok: true`, focused tests and docs pass, Ruff/diff pass,
  and cleanup reports no unowned task artifact requiring removal.

- [ ] **Step 5: Independent review and checkpoint**

  Review that no production source, activation, or scientific artifact changed;
  then commit:

  ```bash
  git add scripts/dev/validate_project.py tests/workflows/repo/test_project_structure.py tests/workflows/repo/test_ownership_ratchets.py docs/pages/development_workflows.rst docs/superpowers/milestones/M0-governance/README.md
  git commit -m "chore(governance): enforce shared ownership ratchets"
  ```

## Proof Oracle

The plan is complete only when the version-1 index validates at the integrated
commit, every negative mutation is rejected, local accountability records are
resolvable, live reconciliation reports no drift, package-owned sources remain
the only capability owners, the provider-specific duplicate check is absent
after parity, M4 extraction is unblocked only after activation, repository/docs/static/cleanup
proof passes, and Git status is clean.
