# Regression Capability Reset And Scoped Readmission Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> `superpowers:subagent-driven-development` (recommended) or
> `superpowers:executing-plans` to implement this plan task-by-task. Steps use
> checkbox (`- [ ]`) syntax for tracking. Use
> `superpowers:test-driven-development` for each change,
> `superpowers:systematic-debugging` for unexpected failures, and
> `superpowers:verification-before-completion` before accepting either the
> reset checkpoint or final readmission checkpoint.

**Goal:** Separate registered/derivative/optimizer facts from locally
validated regression workflows, reset the admitted set to empty, and later
re-admit only the exact methane/NIST and ethanol-water/Susial scopes backed by
accepted M6 records.

**Architecture:** A strict package-owned evidence schema validates immutable
workflow records and a bundled registry is the sole input to admitted
capability rows. The first executable checkpoint lands an empty registry while
preserving backend and component-test facts. A deterministic importer may add
the two exact M6 records only after their strict checkers pass; capability
reporting derives narrow scope/exclusion data from those records rather than
from native-library availability.

**Tech Stack:** Python 3.9-3.13, frozen dataclasses, `StrEnum`, JSON schema-like
validation in package code, `importlib.resources`, SHA-256, pytest, Ruff,
Sphinx, `uv`, and Git.

## Global Constraints

- Milestone/package ownership is M5 and `packages/epcsaft-regression`; reuse
  GitHub issue #193 as the parent.
- The evidence-schema/reset slice is blocked by the traceable native-problem
  contract only where it names receipt fields. Final readmission is blocked by
  both accepted M6 evidence gates.
- The dependency order is: M5 native contract -> M5 evidence schema and empty
  admitted set -> M6 NIST and Susial gates -> final M5 scoped readmission.
  Do not add a reverse dependency from M6 to final M5 admission.
- Ceres availability, registered targets, exact derivative support, optimizer
  support, and synthetic recovery tests are component facts; none activates an
  admitted workflow.
- Admission is local reproducible workflow evidence for this private project,
  not a release, universal accuracy, or paper-reproduction claim.
- No scientific accuracy threshold is introduced. Store metrics and structural
  acceptance facts; do not convert an uncited numerical cutoff into a gate.
- Keep pure-ion, liquid-electrolyte, association-parameter, reactive,
  Khudaida, and all other regression scopes closed.
- Do not edit M6 source/model tables or plots in this plan. The importer reads
  accepted M6 checker receipts and their linked evidence receipts but does not
  generate or repair them.
- Do not preserve backend-derived admitted rows through aliases or legacy
  capability keys that still report them as active.

---

## Source Evidence

- Approved source spec:
  `docs/superpowers/specs/2026-07-10-m5-m6-regression-real-data-admission.md`.
- Blocking plan:
  `docs/superpowers/plans/2026-07-10-m5-regression-traceable-native-problem-contract-plan.md`.
- Dependent evidence plan:
  `docs/superpowers/plans/2026-07-10-m6-regression-real-data-evidence-gates-plan.md`.
- `verified`: current `capabilities.py` makes pure-neutral, constant binary
  `k_ij`, and liquid-electrolyte Born rows production-supported whenever Ceres
  and provider derivative availability are true.
- `verified`: current target-kind rows mix registry, derivative, optimizer, and
  public-support dimensions; the public-support dimension is prefilled without
  independent retained evidence.
- `verified`: pure-ion and liquid-electrolyte native tests are synthetic or
  recovery/component evidence and cannot independently validate a real-data
  workflow.
- `verified`: the approved M6 design fixes methane training rows at 110, 130,
  150, and 170 K and evaluation at all nine retained 100-180 K rows.
- `verified`: the approved binary design uses all 26 Susial 2021 Table 6 rows
  at 100 kPa and plots observed-state target-zero log-fugacity imbalance, not a
  predicted `x-y` curve.
- `inference`: exact artifact hashes and native fingerprints are execution
  products; the importer must copy them from the acyclic M6 chain
  `artifacts -> evidence receipt -> checker receipt` and may not contain
  authored stand-in values.

## Test Complete And Metrics

- Mutation tests remove or corrupt every required evidence field and require a
  specific validation failure.
- The initial bundled evidence registry has schema version 1 and exactly zero
  records.
- `capabilities()` reports registered targets, derivative support, optimizer
  support, and `admitted_workflows` as separate structures.
- No backend or component-test mutation can change the empty admitted set.
- The importer rejects a failed checker, stale artifact hash, missing source
  row, mismatched model/problem fingerprint, unsupported workflow ID, synthetic
  admission source, or unrecognized evidence schema.
- After both M6 gates pass, the bundled registry contains exactly two records:
  `pure_neutral_methane_nist_saturation_v1` and
  `binary_constant_kij_ethanol_water_susial_100kpa_v1`.
- Final capabilities reproduce the exact scopes/exclusions in those records
  and keep pure-ion, liquid-electrolyte, association, reactive, Khudaida, and
  broader pure/binary families absent.
- Focused capability tests, package data build/install tests, strict docs,
  Ruff, diff checks, and cleanup pass at both checkpoints.

## Outcome Proof

**Intent:** Prevent native availability or synthetic self-recovery from being
mistaken for a locally validated scientific regression workflow.

**Current Behavior:** Capability rows become active from compiled Ceres and
provider derivative availability even when no strict record joins the configured
API, native receipt, retained independent observations, model table, metrics,
and plot.

**Expected Outcome:** The admitted set is empty until complete M6 records pass;
afterward exactly two narrowly described workflows are admitted from immutable
evidence records, while component facts and all unproven families remain
separate and visible.

**Target Output:** A strict evidence record module, bundled schema-v1 registry,
mutation tests, reset capability payload and docs, deterministic evidence
importer, two final generated admission records after M6 acceptance, and final
scope/exclusion contract tests.

**Owner:** M5 owns evidence schema, bundled records, capability derivation, and
final admission; M6 owns source/model artifacts and strict checker receipts;
M3 owns model-input fingerprints.

**Interface:** `RegressionEvidenceRecord.from_dict`,
`load_regression_evidence() -> tuple[RegressionEvidenceRecord, ...]`,
`epcsaft_regression.capabilities()["regression"]["admitted_workflows"]`, and
`scripts/dev/import_regression_evidence.py --nist-checker-receipt ...
--susial-checker-receipt ... --output ... [--check]`.

**Cutover:** The empty schema-v1 registry replaces backend-derived admission;
the final generated two-record registry replaces the empty registry only after
both M6 checkers return accepted receipts.

**Replaced Path:** Remove `public_production_supported_target_kind` as an
availability-derived fact, route-wide production booleans inferred solely from
Ceres/CppAD, and any test that treats synthetic recovery as admission.

**Evidence:** Field-mutation tests, empty-set tests, backend-independence tests,
M6 checker receipts, exact source/model/plot hashes, native receipt and model
fingerprints, package resource tests, capability snapshots, docs, Ruff, diff
review, and cleanup output.

**Acceptance Proof:** Before M6, a compiled native backend still yields zero
admitted workflows. After both accepted M6 checker receipts and their linked
evidence receipts are imported, a fresh process reports exactly the two
selected IDs with exact fingerprints and exclusions; a fresh importer
`--check` and both fresh M6 checker commands pass, while deleting or changing
any referenced artifact makes one of those checks fail.

**Stop Criteria:** Stop on an incomplete native receipt, failed or stale M6
checker, model/problem fingerprint mismatch, artifact hash mismatch, missing
row coverage, unexpected third workflow, or any attempt to admit an
electrolyte/reactive/synthetic scope.

**Avoid:** Do not invent hashes, numerical thresholds, citation locators,
capability aliases, or admission records; do not infer admission from an
installed native library; and do not make a broad pure/binary claim from one
species/system proof.

**Risk:** Capability consumers may currently expect broad booleans, and final
evidence paths can become stale after regeneration; exact schema versions,
scope IDs, hashes, and freshness tests make the intentional narrower behavior
explicit.

## Implementation Boundaries

**Files To Create:** `evidence.py`, `evidence/validated_workflows.json`,
`tests/contracts/test_regression_evidence.py`,
`tests/api/test_capabilities.py`, and
`scripts/dev/import_regression_evidence.py`.

**Files To Modify:** `capabilities.py`, `__init__.py`, package `pyproject.toml`
resource/sdist inclusion, package/root regression docs,
`test_ceres_cppad_build_contract.py`, package extension boundary tests,
validation registry, and repo structure tests.

**Files To Avoid:** M6 analysis artifacts except read-only importer inputs,
provider/equilibrium implementation, native regression numerics, paper
validation folders, release metadata, stashes, and remote refs.

**Source Of Truth:** Accepted M5 receipt schema, schema-v1 bundled evidence
registry, exact accepted M6 checker receipts and artifact hashes, and the
capability renderer that consumes only validated records.

**Read Path:** Load the bundled JSON resource, validate every field and hash
shape into frozen evidence records, join those records to separately reported
component facts, and render exact admitted scope/exclusion dictionaries.

**Write Path:** Only the deterministic importer writes the bundled registry; it
reads both accepted M6 checker receipts, follows each one-way link to its
evidence receipt, rehashes every referenced file, validates IDs and
fingerprints, sorts records by evidence ID, and writes canonical JSON. In
`--check` mode it performs the same derivation and compares canonical bytes
without writing.

**Integration Points:** M5 native receipt fields, M6 checkers/artifacts,
`importlib.resources`, package wheel/sdist inclusion, capability API, docs,
validation registry, and GitHub issue #193 children.

**Migration Or Cutover:** Land schema and empty registry first, update consumers
to the separated capability dimensions, wait for both M6 gates, run the
deterministic importer, then land the two-record final admission checkpoint.

**Replaced Path Handling:** Delete availability-derived admission code and
assert its field name is absent from the runtime payload. Do not leave a second
registry, fallback record set, or legacy capability renderer.

**Acceptance Proof Gate:** The reset checkpoint requires zero admitted records
with native dependencies available; final completion additionally requires
both current M6 checker commands, importer `--check`, exact artifact hashes,
exactly two admitted IDs, package resource proof, and all excluded families
still absent.

## Decision Ledger

| Decision | Evidence | Selected answer | Consequence | Deferred? | Owner |
| --- | --- | --- | --- | --- | --- |
| Parent tracker | Existing roadmap | Reuse #193 | No duplicate M5 capability tracker. | No | M5 |
| Admission trigger | Current backend-derived rows | Complete evidence record only | Native availability remains a component fact. | No | M5 |
| Initial state | No complete independent evidence records | Empty admitted set | Existing broad rows are reset before evidence work. | No | M5 |
| Evidence storage | Capability must work from an installed package | Bundled canonical JSON validated into frozen records | Runtime does not inspect a source checkout analysis directory. | No | M5 |
| Hash values | Generated artifacts do not exist at planning time | Deterministic importer copies/rechecks execution outputs | No authored stand-in hashes. | No | M5/M6 |
| Pure scope | Fixed M6 design | Methane/NIST saturation fit only | No Gross/Sadowski reproduction claim. | No | M5/M6 |
| Binary scope | Fixed M6 design and current M4 boundary | Ethanol/water Susial observed-state residual fit only | No associating `x-y` prediction claim. | No | M5/M6 |
| Numerical quality | No source-backed threshold selected | Retain metrics without a numerical admission cutoff | Structural workflow validation and accuracy remain distinct. | No | M5/M6 |
| Electrolytes | Synthetic evidence and separate Khudaida work | Keep closed | No inherited admission from optimizer tests. | No | M5 |
| DAG | Single-milestone issue policy | M5 reset/schema precedes M6; final M5 follows both M6 gates | No dependency cycle. | No | M5/M6 |

## Execution Dependency Graph

```text
M5 traceable native-problem contract
                  |
                  v
Task 1 evidence schema ---> Task 2 empty admitted set
                                  |
                     +------------+------------+
                     |                         |
                     v                         v
             M6 methane/NIST           M6 Susial residual
                     |                         |
                     +------------+------------+
                                  |
                                  v
                     Task 3 import/readmit exactly two
                                  |
                                  v
                     Task 4 final capability proof
```

### Task 1: Add the complete evidence record schema and canonical resource

**Use Cases:**

- A capability record joins one configured workflow, native receipt, source
  table, model table, metrics, checker, plot, and exact scope/exclusions.
- Removing any required field produces a specific schema failure before
  capability rendering.
- An installed wheel loads the same canonical evidence resource as the source
  checkout.
- The schema replaces ad hoc evidence dictionaries without yet admitting a
  workflow.

**Files:**

- Create: `packages/epcsaft-regression/src/epcsaft_regression/evidence.py`
- Create: `packages/epcsaft-regression/src/epcsaft_regression/evidence/validated_workflows.json`
- Create: `packages/epcsaft-regression/tests/contracts/test_regression_evidence.py`
- Modify: `packages/epcsaft-regression/pyproject.toml`
- Modify: `packages/epcsaft-regression/src/epcsaft_regression/__init__.py`

**Interfaces:**

- Consumes: canonical JSON resource with `schema_version == 1` and `records`.
- Produces frozen `RegressionEvidenceRecord` and
  `load_regression_evidence() -> tuple[RegressionEvidenceRecord, ...]`.
- Required record fields are exactly `evidence_id`, `workflow_id`,
  `target_families`, `parameter_families`, `model_input_fingerprint`,
  `native_problem_fingerprint`, `native_receipt_path`, `native_receipt_sha256`,
  `source_table_path`, `source_table_sha256`, `model_table_path`,
  `model_table_sha256`, `metrics_path`, `metrics_sha256`, `plot_path`,
  `plot_sha256`, `plot_data_path`, `plot_data_sha256`,
  `evidence_receipt_path`, `evidence_receipt_sha256`, `checker_command`,
  `checker_receipt_path`, `checker_receipt_sha256`, `optimizer_backend`,
  `derivative_backend`, `scope`, and `exclusions`. The evidence receipt hashes
  only upstream artifacts; the checker receipt hashes that evidence receipt and
  its checked inputs. Neither may contain a back-reference that creates a hash
  cycle.

- [ ] **Step 1: Write RED field, type, duplicate-ID, and resource tests.**

  Start with an empty canonical resource:

  ```json
  {
    "schema_version": 1,
    "records": []
  }
  ```

  Build one complete in-memory record fixture, delete each required key in a
  parameterized test, corrupt each SHA-256 shape, duplicate `evidence_id`, use
  an unknown schema version, and assert a specific `InputError`. Assert the
  package resource can be read through `importlib.resources.files`.

- [ ] **Step 2: Run the RED evidence-schema tests.**

  Run:

  ```bash
  uv run --no-sync python run_pytest.py packages/epcsaft-regression/tests/contracts/test_regression_evidence.py -q
  ```

  Expected: tests fail because the frozen schema and package resource are
  absent.

- [ ] **Step 3: Implement strict parsing and package the empty resource.**

  Reject unknown keys as well as missing keys, require nonblank tuples and
  mappings where the record is nonempty, require lowercase 64-character hex
  hashes, preserve exact scope/exclusion strings, and sort loaded records by
  `evidence_id`. Add JSON files to both wheel package data and sdist inclusion.

- [ ] **Step 4: Run GREEN schema and build-resource tests.**

  Run:

  ```bash
  uv run --no-sync python run_pytest.py packages/epcsaft-regression/tests/contracts/test_regression_evidence.py packages/epcsaft-regression/tests/test_imports.py -q
  uv build --package epcsaft-regression --wheel --sdist
  ```

  Expected: tests pass; wheel and sdist each contain
  `epcsaft_regression/evidence/validated_workflows.json` with zero records.

- [ ] **Step 5: Refactor canonical field validation without changing resource
  bytes.**

  Centralize path/hash pairs in one private tuple, rerun Step 4, and compare
  the resource SHA-256 before/after. Expected: identical bytes and tests.

- [ ] **Step 6: Commit the checkpoint.**

  ```bash
  git add packages/epcsaft-regression/src/epcsaft_regression/evidence.py packages/epcsaft-regression/src/epcsaft_regression/evidence/validated_workflows.json packages/epcsaft-regression/src/epcsaft_regression/__init__.py packages/epcsaft-regression/tests/contracts/test_regression_evidence.py packages/epcsaft-regression/pyproject.toml
  git commit -m "feat(regression): define capability evidence records"
  ```

### Task 2: Reset admission and separate component facts from validated workflows

**Use Cases:**

- A compiled Ceres/CppAD installation reports its component support while the
  admitted workflow list remains empty.
- Synthetic pure-ion/electrolyte recovery tests cannot activate a workflow.
- Existing consumers receive explicit registered, derivative, optimizer, and
  admitted structures instead of one conflated production flag.
- The reset visibly replaces backend-derived admission before M6 evidence is
  generated.

**Files:**

- Create: `packages/epcsaft-regression/tests/api/test_capabilities.py`
- Modify: `packages/epcsaft-regression/src/epcsaft_regression/capabilities.py`
- Modify: `packages/epcsaft-regression/tests/contracts/test_ceres_cppad_build_contract.py`
- Modify: `tests/workflows/repo/test_package_extension_boundary.py`
- Modify: `tests/workflows/repo/test_run_pytest.py`
- Modify: `docs/pages/parameter_regression.rst`
- Modify: `packages/epcsaft-regression/README.md`

**Interfaces:**

- Consumes: `load_regression_evidence()` from Task 1 plus existing native
  Ceres/provider derivative probes.
- Produces capability keys `registered_target_kinds`,
  `derivative_supported_target_kinds`, `optimizer_supported_target_kinds`, and
  `admitted_workflows`.
- `admitted_workflows` is a list of dictionaries rendered only from validated
  evidence records; it is empty at this checkpoint.

- [ ] **Step 1: Write RED empty-admission and independence tests.**

  Assert:

  ```python
  regression = epcsaft_regression.capabilities()["regression"]
  assert regression["admitted_workflows"] == []
  assert "m" in regression["registered_target_kinds"]
  assert "m" in regression["derivative_supported_target_kinds"]
  assert "m" in regression["optimizer_supported_target_kinds"]
  assert "public_production_supported_target_kind" not in repr(regression)
  ```

  Monkeypatch component availability true/false and synthetic test metadata;
  assert `admitted_workflows` stays empty in every case.

- [ ] **Step 2: Run the RED capability tests.**

  Run:

  ```bash
  uv run --no-sync python run_pytest.py packages/epcsaft-regression/tests/api/test_capabilities.py packages/epcsaft-regression/tests/contracts/test_ceres_cppad_build_contract.py tests/workflows/repo/test_package_extension_boundary.py -q
  ```

  Expected: current broad availability-derived admission assertions fail.

- [ ] **Step 3: Implement separated capability rendering and remove the old
  admission dimension.**

  Retain registered/derivative/optimizer facts from their exact owners. Render
  admitted rows only from Task 1 records. Remove route booleans whose truth is
  computed solely from dependency availability and update docs to say no local
  real-data workflow is admitted at this checkpoint.

- [ ] **Step 4: Run GREEN capability, boundary, docs, and registry tests.**

  Run:

  ```bash
  uv run --no-sync python run_pytest.py packages/epcsaft-regression/tests/api/test_capabilities.py packages/epcsaft-regression/tests/contracts/test_ceres_cppad_build_contract.py tests/workflows/repo/test_package_extension_boundary.py tests/workflows/repo/test_run_pytest.py -q
  uv run --no-sync sphinx-build -W --keep-going -b html docs docs/_build/html
  ```

  Expected: all selected tests and strict docs pass; fresh-process capability
  output contains zero admitted workflows regardless of installed backend
  state.

- [ ] **Step 5: Commit the reset checkpoint and stop before readmission.**

  ```bash
  git add packages/epcsaft-regression/src/epcsaft_regression/capabilities.py packages/epcsaft-regression/tests/api/test_capabilities.py packages/epcsaft-regression/tests/contracts/test_ceres_cppad_build_contract.py packages/epcsaft-regression/README.md docs/pages/parameter_regression.rst tests/workflows/repo/test_package_extension_boundary.py tests/workflows/repo/test_run_pytest.py
  git commit -m "fix(regression): reset evidence-backed capabilities"
  ```

  Expected: the reset is a usable, reviewable checkpoint. Pause this plan until
  both M6 checker receipts are accepted; do not execute Task 3 from incomplete
  evidence.

### Task 3: Import the accepted M6 records and re-admit exactly two scopes

**Use Cases:**

- A deterministic importer starts from both accepted M6 checker receipts,
  follows their immutable links to evidence receipts, and copies exact
  hashes/fingerprints into the package registry.
- A stale plot, missing source row, failed checker, or mismatched native
  fingerprint blocks readmission.
- The capability payload names only methane/NIST and ethanol-water/Susial
  configured workflows with exact exclusions.
- This cutover replaces the empty registry only after both independent M6
  evidence gates pass.

**Files:**

- Create: `scripts/dev/import_regression_evidence.py`
- Create: `tests/workflows/repo/test_import_regression_evidence.py`
- Modify: `packages/epcsaft-regression/src/epcsaft_regression/evidence/validated_workflows.json`
- Modify: `packages/epcsaft-regression/tests/api/test_capabilities.py`
- Modify: `packages/epcsaft-regression/tests/contracts/test_regression_evidence.py`

**Interfaces:**

- Consumes:
  `analyses/package_validation/regression_real_data/figures/methane_nist_fit/results/checker_receipt.json`
  and
  `analyses/package_validation/regression_real_data/figures/ethanol_water_susial_residual/results/checker_receipt.json`;
  each checker receipt names and hashes its upstream `evidence_receipt.json`.
- Produces canonical `validated_workflows.json` with exactly the two fixed
  evidence IDs and exact current hashes.
- CLI exit code is zero only when both strict checker receipts say accepted,
  each one-way evidence-receipt join is exact, and every referenced artifact
  rehashes to the recorded value. `--check` additionally requires the existing
  output bytes to equal the freshly derived canonical registry and never writes.

- [ ] **Step 1: Write RED importer freshness and exact-scope tests.**

  Use temporary complete receipt bundles. Mutate each referenced byte file,
  checker status, evidence-receipt link/hash, attempted circular back-reference,
  row count, workflow ID, model/problem fingerprint, source kind, optimizer
  backend, derivative backend, and exclusion set. Assert a nonzero importer
  result with the exact failing field/path. Assert one checker receipt alone
  cannot produce a registry, and assert `--check` detects stale canonical output
  without modifying it.

- [ ] **Step 2: Run RED importer tests.**

  Run:

  ```bash
  uv run --no-sync python run_pytest.py tests/workflows/repo/test_import_regression_evidence.py packages/epcsaft-regression/tests/api/test_capabilities.py -q
  ```

  Expected: failures show the deterministic importer and two-scope assertions
  are absent.

- [ ] **Step 3: Implement the importer with closed workflow descriptors.**

  Hard-code only the two allowed IDs, their required row counts (nine methane
  evaluation temperatures and 26 Susial source rows), their required target
  and parameter families, and their exclusions. Read all fingerprints and
  hashes from accepted checker/evidence receipts, independently rehash files,
  reject any checker/evidence back-reference cycle, canonical-sort records, and
  write UTF-8 JSON with sorted keys and a terminal newline. Implement `--check`
  by deriving the same bytes in memory and comparing them with `--output`.

- [ ] **Step 4: Run both strict M6 checkers, then import current evidence.**

  Run:

  ```bash
  uv run --no-sync python scripts/validation/check_regression_real_data_evidence.py --lane methane_nist --json --require-complete
  uv run --no-sync python scripts/validation/check_regression_real_data_evidence.py --lane ethanol_water_susial --json --require-complete
  uv run --no-sync python scripts/dev/import_regression_evidence.py --nist-checker-receipt analyses/package_validation/regression_real_data/figures/methane_nist_fit/results/checker_receipt.json --susial-checker-receipt analyses/package_validation/regression_real_data/figures/ethanol_water_susial_residual/results/checker_receipt.json --output packages/epcsaft-regression/src/epcsaft_regression/evidence/validated_workflows.json
  uv run --no-sync python scripts/dev/import_regression_evidence.py --nist-checker-receipt analyses/package_validation/regression_real_data/figures/methane_nist_fit/results/checker_receipt.json --susial-checker-receipt analyses/package_validation/regression_real_data/figures/ethanol_water_susial_residual/results/checker_receipt.json --output packages/epcsaft-regression/src/epcsaft_regression/evidence/validated_workflows.json --check
  ```

  Expected: both checker commands report accepted; importer reports exactly two
  records and lists their revalidated hashes; `--check` confirms byte-identical
  canonical output without writing.

- [ ] **Step 5: Run GREEN importer, evidence, and capability tests in a fresh
  process.**

  Run:

  ```bash
  uv run --no-sync python run_pytest.py tests/workflows/repo/test_import_regression_evidence.py packages/epcsaft-regression/tests/contracts/test_regression_evidence.py packages/epcsaft-regression/tests/api/test_capabilities.py -q
  uv run --no-sync python -c 'import epcsaft_regression, json; print(json.dumps(epcsaft_regression.capabilities()["regression"]["admitted_workflows"], sort_keys=True))'
  ```

  Expected: all tests pass; the fresh process prints exactly the two fixed IDs,
  their source/model/problem fingerprints, scopes, and exclusions.

- [ ] **Step 6: Commit the readmission checkpoint.**

  ```bash
  git add scripts/dev/import_regression_evidence.py tests/workflows/repo/test_import_regression_evidence.py packages/epcsaft-regression/src/epcsaft_regression/evidence/validated_workflows.json packages/epcsaft-regression/tests/api/test_capabilities.py packages/epcsaft-regression/tests/contracts/test_regression_evidence.py
  git commit -m "feat(regression): admit two real-data workflows"
  ```

### Task 4: Close the M5 capability documentation and verification gate

**Use Cases:**

- User docs distinguish local workflow validation from model accuracy and
  release claims.
- Package archives contain the exact accepted registry and capability output
  remains stable outside the source checkout.
- A final repository proof demonstrates all excluded families remain closed.
- Independent review verifies the evidence import and replaced-path cutover.

**Files:**

- Modify: `docs/pages/parameter_regression.rst`
- Modify: `docs/pages/api_reference.rst`
- Modify: `packages/epcsaft-regression/README.md`
- Modify: `packages/epcsaft-regression/docs/README.md`
- Modify: `scripts/dev/validation_registry.py`
- Modify: `tests/workflows/repo/test_project_structure.py`

**Interfaces:**

- Consumes: Tasks 1-3 and both accepted M6 checker/evidence receipt chains.
- Produces: final scoped capability docs, validation registry commands, package
  resource proof, and closeout receipts for #193's final child.

- [ ] **Step 1: Write RED docs/structure assertions for exact scope language.**

  Require docs to name the two evidence IDs, training/evaluation row scope,
  observed-state Susial residual meaning, lack of an accuracy threshold, and
  explicit excluded families. Require exactly one bundled registry path and no
  availability-derived admission field.

- [ ] **Step 2: Run RED structure/docs assertions.**

  Run:

  ```bash
  uv run --no-sync python run_pytest.py tests/workflows/repo/test_project_structure.py packages/epcsaft-regression/tests/api/test_capabilities.py -q
  ```

  Expected: failures identify missing final docs/registry integration.

- [ ] **Step 3: Update docs and validation registry without broadening scope.**

  Describe methane/NIST as an operational native fit, Susial as a target-zero
  observed-state fugacity-imbalance fit, and every metric as reported rather
  than an uncited accuracy gate. Keep the paper `k_ij` contextual and all
  unproven families explicitly absent.

- [ ] **Step 4: Run final M5 capability verification.**

  Run:

  ```bash
  uv run --no-sync python scripts/validation/check_regression_real_data_evidence.py --lane methane_nist --json --require-complete
  uv run --no-sync python scripts/validation/check_regression_real_data_evidence.py --lane ethanol_water_susial --json --require-complete
  uv run --no-sync python scripts/dev/import_regression_evidence.py --nist-checker-receipt analyses/package_validation/regression_real_data/figures/methane_nist_fit/results/checker_receipt.json --susial-checker-receipt analyses/package_validation/regression_real_data/figures/ethanol_water_susial_residual/results/checker_receipt.json --output packages/epcsaft-regression/src/epcsaft_regression/evidence/validated_workflows.json --check
  uv run --no-sync python run_pytest.py packages/epcsaft-regression/tests/contracts/test_regression_evidence.py packages/epcsaft-regression/tests/api/test_capabilities.py tests/workflows/repo/test_import_regression_evidence.py tests/workflows/repo/test_package_extension_boundary.py tests/workflows/repo/test_project_structure.py -q
  uv run --no-sync python scripts/dev/validate_project.py regression
  uv build --package epcsaft-regression --wheel --sdist
  uv run --no-sync ruff check packages/epcsaft-regression scripts/dev/import_regression_evidence.py tests/workflows/repo/test_import_regression_evidence.py
  uv run --no-sync sphinx-build -W --keep-going -b html docs docs/_build/html
  git diff --check
  bash "$HOME/.codex/hooks/codex-cleanup.sh" --repo-root .
  ```

  Expected: both freshly executed checkers accept, importer `--check` confirms
  the registry is current, tests/validators/docs/build pass, both archives
  contain the exact two-record resource, Ruff and diff are clean, and cleanup
  reports no task-owned debris.

- [ ] **Step 5: Request independent evidence and capability review.**

  One reviewer compares each bundled field/hash with both M6 checker/evidence
  receipt chains; a second
  reviewer checks capability scope/exclusion semantics and confirms the old
  availability-derived path is absent. Address real findings with a RED test
  and rerun Step 4.

- [ ] **Step 6: Commit the final documentation checkpoint.**

  ```bash
  git add docs/pages/parameter_regression.rst docs/pages/api_reference.rst packages/epcsaft-regression/README.md packages/epcsaft-regression/docs/README.md scripts/dev/validation_registry.py tests/workflows/repo/test_project_structure.py
  git commit -m "docs(regression): document scoped evidence admission"
  ```

  Expected: the plan is complete only after Tasks 1-4 and both M6 gates are
  accepted; otherwise the correct completion state is the Task 2 empty-set
  checkpoint.
