# Repository Truth And Scientific Integrity Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: use
> `superpowers:subagent-driven-development` in the current session or
> `superpowers:executing-plans` in a later session. Every implementation task
> uses red-green TDD and receives a review before its commit.

**Goal:** Make public thermodynamic capabilities mechanically truthful, remove
silent scientific input invention, make regression controls effective, admit
equilibrium routes only through strict real-data proof, harden Linux artifacts,
and decompose the largest ownership tangles without changing proven behavior.

**Architecture:** Execute truth-first. Repair the repository measurement system
and claim/evidence contract before scientific or structural changes. Then
harden provider inputs, regression semantics, equilibrium admission,
distribution proof, and finally large-module ownership. Each task has one
milestone/package owner even though this user-approved program spans M3/M4/M5.

**Tech Stack:** Python 3.9-3.13, pytest, Ruff, Sphinx, C++17, CMake/Ninja,
pybind11, CppAD, Ipopt, Ceres, scikit-build-core, auditwheel, Bash, GitHub
Actions, retained CSV/JSON/SVG/PDF scientific artifacts.

---

## Source And Scope

- Source spec:
  `docs/superpowers/specs/2026-07-09-m3-core-repository-truth-and-scientific-integrity-program.md`
- Approved approach: truth-first sequence
- Program sponsor: `M3 - Core EOS`
- Workstream owners: M3 provider/repo, M4 equilibrium, M5 regression, M6
  retained literature artifacts
- User authorization: audit and implement the complete repository program
- TDD policy: required
- Debug policy: systematic diagnosis before scientific solver changes
- Integration policy: direct local `main` commits were explicitly authorized;
  no push or publication is authorized

## Clean Baseline

The inherited 366-entry worktree was reviewed and reduced to four baseline
commits before this plan:

- `91af1167 docs: canonicalize issue mirrors and validators`
- `6d425693 fix(equilibrium): support system Ipopt interfaces`
- `d8013d59 chore: align standalone CE analysis layout`
- `fdd7a0e2 build: complete Linux workflow migration`

Baseline verification:

- 206 focused workflow/build tests passed.
- 18 Ipopt adapter and equilibrium confidence tests passed.
- A fresh provider wheel built and imported in an isolated CPython 3.13
  environment; methane `z` was finite.
- Strict Sphinx, Ruff, Bash syntax, ShellCheck, YAML/TOML parsing and cleanup
  passed.

Known scientific/architecture failures are inputs to this plan, not baseline
migration regressions.

## Outcome Proof

**Intent:** A public production claim must name the exact route, native owner,
collected proof, real data and thermodynamic acceptance metrics that justify
the claim.

**Current behavior:** Full collection fails on duplicate test module names;
bare and wrapped collection disagree; the default gate has seven architecture
failures; reactive speciation misses balance/stationarity limits by orders of
magnitude while still appearing complete; electrolyte LLE and neutral
multiphase bypass the native selector; provider lookup can invent parameters;
regression controls can be annotations rather than solver inputs; broad wheel
compatibility is unproven; several core files combine thousands of lines of
unrelated responsibility.

**Expected outcome:** Collection and default tests are green; exposed families
equal native-selector-owned families equal complete-evidence families; missing
scientific inputs fail at a typed boundary; regression receipts describe the
actual native problem; every admitted equilibrium route passes strict
thermodynamic checks; artifacts install without checkout state; and giant
modules are split along tested ownership boundaries.

**Target output:** Updated package/runtime contracts, native owners, tests,
literature evidence, build workflows, documentation, and program verification
receipts.

**Owner:** M3 owns repository/provider integration; M4 and M5 own their package
changes; the main thread owns cross-package verification.

**Interface:** `epcsaft`, `epcsaft_equilibrium`, `epcsaft_regression`, their
native extension modules, canonical capability evidence and official validation
commands.

**Cutover:** Production claims and official test entry points move atomically to
the canonical evidence/collection contracts before old lists or bypasses are
deleted.

**Replaced Path:** Independent capability lists, silent scientific defaults,
post-hoc regression annotations, direct route bindings and host-only artifact
proof are displaced by package-owned typed contracts and executable evidence.

**Evidence:** Collected pytest node sets, strict-checker JSON, native problem
receipts, retained literature data/plots, wheel ELF audits and isolated install
smokes.

**Acceptance Proof:** The program criteria and full proof oracle pass, every
admitted family names its thermodynamic evidence, and the obsolete paths named
above are absent.

**Stop Criteria:** Stop a task when the required scientific source, ownership
decision, or diagnostic evidence is absent. Do not invent parameters, weaken
acceptance thresholds, add hidden solver seeds, preserve an obsolete path, or
expand a sibling milestone without recording the owner.

**Avoid:** Do not trade a loud scientific failure for a green status flag,
exception list, synthetic-only proof or compatibility wrapper.

**Risk:** Tightening truth and input contracts will expose unsupported callers
and incomplete datasets; each cutover therefore requires characterization and
an explicit package owner before deletion.

## Implementation Boundaries

**Files To Create:** Focused contract tests, typed provider/regression modules,
diagnostic receipts and package-owned evidence artifacts named by the tasks.

**Files To Modify:** Root validation configuration, canonical evidence records,
the three package implementations, owned native code, build workflows and
user-facing docs explicitly listed per task.

**Files To Avoid:** Downstream repositories, unrelated milestone code,
untraceable parameter snapshots, published release state and private developer
paths.

**Source Of Truth:** Foundational PC-SAFT/ePC-SAFT literature, retained
repository source data, canonical package contracts and strict executable
thermodynamic proof.

**Read Path:** Follow public entry point to typed Python contract, native owner,
result receipt, evidence registry, exact proof node and retained data before
changing behavior.

**Write Path:** Add the failing owner-specific test, implement the smallest
canonical change, delete the displaced path, then update evidence and docs.

**Integration Points:** Test collection, capability reporting, provider SDK,
selector dispatch, native result building, regression payloads, artifact build
backends and literature-validation lanes.

**Migration Or Cutover:** Each task moves all obvious callers and proof records
to the new owner in the same commit series; obsolete wrappers and parallel
lists are removed.

**Replaced Path Handling:** Characterize old behavior first, preserve only
scientifically proven outputs, and delete old branches, helper bindings and
metadata after the new path passes.

**Acceptance Proof Gate:** A task cannot complete until its red-green tests,
package proof, relevant docs/static checks, diff review and cleanup pass.

## Program Acceptance Criteria

- [ ] Bare and wrapped collection produce the same node set and exit zero.
- [ ] `uv run --no-sync python run_pytest.py -q` exits zero.
- [ ] Production capability, selector and complete-evidence family sets are
      identical.
- [ ] Every production capability names collected, passing proofs.
- [ ] No provider runtime path infers scientific parameters from species names
      or blank cells.
- [ ] Every accepted regression control changes the native solve or is rejected
      before solve construction.
- [ ] Every production regression family retains source data, plotted data and
      a literature-versus-model plot.
- [ ] Reactive speciation is either absent from production/public claims or
      passes final `lambda=1`, balance `<=1e-8`, stationarity `<=1e-6` and
      native acceptance.
- [ ] Declared Python/platform artifacts pass isolated downstream installs and
      native dependency audits.
- [ ] Identified giant modules have smaller, tested single-owner units and no
      duplicated acceptance policy.

## Phase 1: Truth And Green Gate

### Task 1: Make Test Collection Deterministic

**Owner:** M3 repo validation

**Use Cases:**

- A developer runs bare pytest or the official wrapper and sees the same
  package/repo suite.
- Duplicate package-local test basenames do not collide.
- Analysis-local tests run only from explicit analysis validation commands.

**Files:**

- Modify: `pyproject.toml`
- Modify: `run_pytest.py`
- Modify: `tests/workflows/repo/test_run_pytest.py`
- Modify: `tests/workflows/repo/test_workflow_entrypoints.py`

- [ ] **Step 1: Add failing collection-contract tests**

  Add tests that run bare and wrapped `--collect-only`, parse node IDs, assert
  both return zero, and compare exact sets. Assert the intended test roots are
  `tests`, all three package test roots, and no `analyses/**/tests` root.

- [ ] **Step 2: Prove the current red state**

  ```bash
  uv run --no-sync python -m pytest tests/workflows/repo/test_run_pytest.py -q
  ```

  Expected red reason: duplicate module collection and bare/wrapper scope
  mismatch.

- [ ] **Step 3: Configure canonical collection**

  Set pytest `--import-mode=importlib` and explicit root `testpaths`. Make the
  wrapper inherit the same config rather than maintaining a divergent module
  import mode.

- [ ] **Step 4: Verify collection equivalence**

  ```bash
  uv run --no-sync python -m pytest --collect-only -q
  uv run --no-sync python run_pytest.py --all --collect-only -q
  uv run --no-sync python -m pytest tests/workflows/repo/test_run_pytest.py -q
  ```

- [ ] **Step 5: Commit**

  Commit message: `test: make repository collection deterministic`

### Task 2: Replace Substring Policing With Semantic Text Gates

**Owner:** M3 repo validation

**Use Cases:**

- Identifiers such as `native_status` and `derivative_status` are accepted.
- Exact forbidden placeholder/control phrases are still rejected.
- The gate reports file, line and matched semantic token.

**Files:**

- Modify: `tests/workflows/repo/test_project_structure.py`
- Create or modify: `tests/workflows/repo/test_text_gates.py`
- Modify only if canonical helper already exists: `scripts/dev/check_text_gates.py`

- [ ] **Step 1: Add boundary-aware red tests**

  Add temporary-file unit cases for neutral identifiers and exact blocked
  tokens. Require token-boundary matching and an actionable error payload.

- [ ] **Step 2: Run and record the seven false-positive failures**

  ```bash
  uv run --no-sync python -m pytest tests/workflows/repo/test_project_structure.py::test_strict_solver_derivative_text_gate_passes tests/workflows/repo/test_text_gates.py -q
  ```

- [ ] **Step 3: Centralize semantic matching**

  Use one compiled boundary-aware policy in the canonical text-gate helper.
  Delete duplicated substring checks.

- [ ] **Step 4: Verify true positives and true negatives**

  Run the focused tests and `uv run --no-sync python scripts/dev/check_text_gates.py`.

- [ ] **Step 5: Commit**

  Commit message: `test: make strict solver text gates semantic`

### Task 3: Make Production Capabilities Evidence-Derived

**Owner:** M4 equilibrium activation/evidence; repository validation orchestration

**Use Cases:**

- A production family cannot exist without exact proof nodes/checkers.
- A proof node typo fails collection validation.
- Development/component tests remain visible without becoming production
  admission.

**Files:**

- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/capabilities.py`
- Create: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/capability_evidence.py`
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/core/activation_matrix.h`
- Create: `scripts/dev/validation_registry.py`
- Modify: `run_pytest.py`
- Modify: `scripts/dev/validate_project.py`
- Modify: `packages/epcsaft-equilibrium/tests/contracts/test_activation_capabilities.py`
- Modify: `tests/native/contracts/test_equilibrium_benchmark_registry.py`
- Modify: `tests/native/contracts/test_generalized_equilibrium_registry.py`
- Modify: `tests/workflows/repo/test_run_pytest.py`

- [ ] **Step 1: Add failing set-equality and proof-collection tests**

  Assert:

  ```python
  exposed_families == native_selector_solve_families == complete_evidence_families
  ```

  Validate every proof node through pytest collection.

- [ ] **Step 2: Prove the current mismatch**

  Run the capability/registry tests and retain the seven/three/six family-set
  diagnostic.

- [ ] **Step 3: Define the canonical evidence record**

  Keep exposure, public routes and proof IDs in the generated native activation
  contract. Add an equilibrium-owned pure-data mapping from proof IDs to exact
  node IDs/checkers, sources, artifacts and acceptance metrics. Derive public
  reporting by joining those sources.

- [ ] **Step 4: Remove parallel hand-maintained production lists**

  Move repository test-slice orchestration out of provider runtime metadata and
  into `scripts/dev/validation_registry.py`. The provider must not declare M4
  or M5 production surfaces. Do not add exception lists.

- [ ] **Step 5: Verify exact alignment**

  ```bash
  uv run --no-sync python -m pytest packages/epcsaft-equilibrium/tests/contracts/test_activation_capabilities.py tests/native/contracts/test_equilibrium_benchmark_registry.py tests/native/contracts/test_generalized_equilibrium_registry.py tests/workflows/repo/test_run_pytest.py -q
  ```

- [ ] **Step 6: Commit**

  Commit message: `refactor: derive production capabilities from evidence`

### Task 4: Close Unproven And Noncanonical Equilibrium Claims

**Owner:** M4 equilibrium; M6 retained analysis status

**Use Cases:**

- Users cannot mistake the failing MEA continuation for production behavior.
- Route specs cannot mask direct electrolyte-LLE or neutral-multiphase selector
  bypasses.
- Developers retain internal component diagnostics and exact re-admission proof
  targets without a compatibility surface.

**Files:**

- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/__init__.py`
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/workflows.py`
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/core/native_requests.py`
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/chemical_equilibrium.py`
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/capabilities.py`
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/core/activation_matrix.h`
- Modify: `analyses/package_validation/standalone_ce/analysis.yaml`
- Modify: `analyses/package_validation/standalone_ce/README.md`
- Modify: `tests/native/contracts/test_standalone_ce_gate.py`
- Modify: `packages/epcsaft-equilibrium/tests/contracts/test_activation_capabilities.py`
- Modify: M4 benchmark registries, public docs and route-specific API tests for
  `electrolyte_lle` and `neutral_multiphase_nonassoc`.

- [ ] **Step 1: Add red truthfulness tests**

  Assert reactive speciation, electrolyte LLE and neutral multiphase are absent
  from public production exports. Assert the immediate exposed set is exactly
  bubble/dew, neutral TP flash, neutral LLE and single-component VLE, each
  native-selector-owned and evidence-complete. Require CE analysis metadata to
  record the live validation failure with exact target metrics.

- [ ] **Step 2: Run the existing strict proof**

  ```bash
  uv run --no-sync python -m pytest tests/native/contracts/test_standalone_ce_gate.py -q
  ```

  Retain the failing `balance_inf_norm` and `stationarity_inf_norm` evidence as
  a repair receipt. Do not turn the scientific failure into an expected-success
  production test.

- [ ] **Step 3: Remove public/production admission**

  Close the three activation rows, clear their public routes and proof IDs, and
  remove their public route specs/exports. Keep internal formulation/component
  diagnostics required by Phase 4; remove API tests and examples that assert
  the closed surfaces.

- [ ] **Step 4: Correct analysis and capability metadata**

  Record active CE validation work, the exact checker command and re-admission
  limits. Remove production/admission booleans from retained scientific
  artifacts; live activation plus green proof authorizes admission.

- [ ] **Step 5: Verify truthful green tests**

  ```bash
  uv run --no-sync python -m pytest packages/epcsaft-equilibrium/tests/contracts/test_activation_capabilities.py packages/epcsaft-equilibrium/tests/api/test_imports.py tests/native/contracts/test_equilibrium_benchmark_registry.py tests/native/contracts/test_generalized_equilibrium_registry.py -q
  ```

- [ ] **Step 6: Commit**

  Commit message: `fix(equilibrium): close noncanonical production routes`

### Task 5: Restore Selector-Only Dispatch And Canonical Acceptance

**Owner:** M4 equilibrium

**Use Cases:**

- Every public solve enters through one typed selector route spec.
- Closed electrolyte-LLE and multiphase paths cannot masquerade as selector
  routes; their later re-admission requires native-selector integration.
- Route code cannot create an independently accepted result.

**Files:**

- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/workflows.py`
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/core/native_results.py`
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/core/two_phase_eos_route.cpp`
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/results/result_builder.cpp`
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/results/result_builder.h`
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/register_bindings.cpp`
- Modify: `packages/epcsaft-equilibrium/tests/native/results/test_result_builder.py`
- Modify: `packages/epcsaft-equilibrium/tests/native/diagnostics/test_selector_core_contracts.py`
- Modify: `tests/workflows/repo/test_project_structure.py`

- [ ] **Step 1: Add characterization and bypass-failure tests**

  Capture current accepted bubble/dew/flash/LLE payloads. Add tests that fail if
  public Python dispatch names a route-specific native binding or if route code
  constructs acceptance outside `result_builder`.

- [ ] **Step 2: Prove the current architecture failures**

  Run the six relevant project-structure nodes plus result-builder and selector
  contract tests.

- [ ] **Step 3: Move result construction into the canonical builder**

  Define the smallest typed input needed by the builder. Route code calculates
  thermodynamic fields and passes them to the builder; delete duplicate
  acceptance/payload construction.

- [ ] **Step 4: Route public workflows through selector specs**

  For the four exposed families, require selector route construction and native
  selector solve. Delete public bindings and Python helpers that only served
  the three closed bypasses; retain only explicitly internal diagnostics needed
  by later scientific admission tasks.

- [ ] **Step 5: Resolve chemical-equilibrium contract ownership**

  Move shared solve/contract responsibilities to the selector/core owner while
  retaining reaction-specific equations in reaction blocks. If full movement
  depends on Phase 4 science, remove the production route now and keep the
  internal diagnostic owner explicit.

- [ ] **Step 6: Verify characterization and structure**

  ```bash
  uv run --no-sync python -m pytest packages/epcsaft-equilibrium/tests/native/results/test_result_builder.py packages/epcsaft-equilibrium/tests/native/diagnostics/test_selector_core_contracts.py tests/workflows/repo/test_project_structure.py -q
  uv run --no-sync python run_pytest.py --equilibrium-confidence -q
  ```

- [ ] **Step 7: Commit**

  Commit message: `refactor(equilibrium): centralize selector acceptance`

### Task 6: Prove The Phase 1 Green Gate

**Owner:** M3/M4 integration; main thread only

**Use Cases:**

- An integrator sees one acceptance proof for collection, capabilities,
  selector cutover and the retired duplicate paths.
- Documentation makes the truthful gate visible to future developers.

**Files:**

- Modify: `docs/pages/development_workflows.rst`
- Modify: `docs/pages/package_guide.rst`
- Modify: `docs/pages/equilibrium_architecture.rst`
- Modify: `docs/superpowers/PROJECT_CONTEXT.md` only for durable completion rules

- [ ] **Step 1: Run collection proofs**

  ```bash
  uv run --no-sync python -m pytest --collect-only -q
  uv run --no-sync python run_pytest.py --all --collect-only -q
  ```

- [ ] **Step 2: Run default and confidence proofs**

  ```bash
  uv run --no-sync python run_pytest.py -q
  uv run --no-sync python run_pytest.py --confidence -q
  uv run --no-sync python run_pytest.py --equilibrium-confidence -q
  ```

- [ ] **Step 3: Validate documentation and static checks**

  ```bash
  uv run --no-sync python scripts/dev/validate_project.py docs
  uv run --no-sync ruff check .
  git diff --check
  bash "$HOME/.codex/hooks/codex-cleanup.sh" --repo-root .
  ```

- [ ] **Step 4: Request code review and commit**

  Commit message: `docs: define the truthful repository green gate`

## Phase 2: Provider Input Integrity

### Task 7: Characterize And Remove Invented Component Defaults

**Owner:** M3 provider

**Use Cases:**

- A missing ion or association parameter produces a visible field-specific
  error instead of a fabricated value.
- Source-backed parameter records preserve their acceptance evidence during
  the default-removal cutover.

**Files:**

- Modify: `packages/epcsaft/src/epcsaft/model/datasets.py`
- Modify: `packages/epcsaft/src/epcsaft/model/parameters.py`
- Modify: `packages/epcsaft/src/epcsaft/model/validation.py`
- Modify: `packages/epcsaft/src/epcsaft/model/templates.py`
- Modify: `packages/epcsaft/src/epcsaft/model/sources.py`
- Modify: `packages/epcsaft/src/epcsaft/frontend/mixture.py`
- Create: `packages/epcsaft/tests/api/frontend/test_parameter_input_integrity.py`
- Modify provider input/API docs that currently teach legacy arrays or inferred
  dataset behavior.

- [ ] Add tests proving missing charge/topology/required association,
      dielectric, Born and solvation inputs fail with component and field names.
- [ ] Reject unknown keys, every non-finite scalar, suffix-based charge
      inference and loose expression parsing.
- [ ] Characterize source-backed Gross 2001, Gross 2002, Held 2008 and Held
      2012 records before cutover.
- [ ] Make `ParameterSet.from_dict()` accept only the versioned canonical
      schema; migrate callers and hard-reject parallel-array payloads.
- [ ] Remove embedded component defaults, name-based scientific inference,
      blank-to-number handling and the dead named-dataset catalog.
- [ ] Prove Held 2012 parsing no longer leaks derived receipt keys into user
      options.
- [ ] Run provider API/native state tests.
- [ ] Commit: `fix(provider): reject missing scientific parameters`

### Task 8: Distinguish Explicit Zero From Missing Interaction Data

**Owner:** M3 provider

**Use Cases:**

- A scientist can prove why an interaction is exactly zero and distinguish it
  from absent data.
- Old blank-to-zero behavior is replaced without losing supported parameter
  evidence.

**Files:**

- Modify: `packages/epcsaft/src/epcsaft/model/datasets.py`
- Modify: `packages/epcsaft/src/epcsaft/model/parameters.py`
- Modify: `packages/epcsaft/src/epcsaft/model/templates.py`
- Create: `packages/epcsaft/tests/api/frontend/test_interaction_provenance.py`
- Modify source-owned parameter manifests under the existing
  `analyses/**/parameters` and package-data layout only when traceable.
- Correct: `docs/latex/equations.tex`, generated equation views and equation
  registry evidence for the source-consistent association-volume correction.

- [ ] Add red tests for absent/blank/non-finite interaction families, zero
      without provenance, duplicate/reversed pairs, invalid dimensions and
      asymmetric matrices.
- [ ] Replace scalar-defaulted binary records with family-specific value or
      correlation records whose provenance distinguishes literature, fitted and
      equation/model structural zero.
- [ ] Generate diagonal identity and named topology zeros from equation policy;
      never serialize missing interactions as zero.
- [ ] Make catalog loading and canonical serialization use the same typed owner.
- [ ] Reject the asymmetric 2019 Bülow matrix until an authoritative cell choice
      is approved; do not average or choose a triangle silently.
- [ ] Migrate supported data; leave unresolved wildcard-zero records as loud
      boundary errors pending an approved versioned combining-rule policy.
- [ ] Verify existing neutral/associating/electrolyte characterization cases.
- [ ] Commit: `refactor(provider): make interaction provenance explicit`

### Task 9: Make Model Configuration Typed And Reproducible

**Owner:** M3 provider

**Use Cases:**

- A result receipt makes the exact model preset and user choices visible.
- Conflicting or unknown configuration is rejected while the loosely shaped
  old path is retired.

**Files:**

- Modify: `packages/epcsaft/src/epcsaft/model/options.py`
- Modify: `packages/epcsaft/src/epcsaft/model/parameters.py`
- Modify: `packages/epcsaft/src/epcsaft/frontend/mixture.py`
- Modify: `packages/epcsaft/src/epcsaft/frontend/state.py`
- Modify: `packages/epcsaft/src/epcsaft/state/native_payload.py`
- Modify: `packages/epcsaft/src/epcsaft/state/native_adapter.py`
- Modify: `packages/epcsaft/src/epcsaft/runtime/core.py`
- Create: `packages/epcsaft/tests/api/frontend/test_model_configuration_receipt.py`

- [ ] Reject unknown/conflicting option keys.
- [ ] Require a versioned source-specific preset or every active formulation
      choice; remove the generic modern-electrolyte defaults.
- [ ] Carry supported water-diameter, dielectric and interaction correlations as
      typed expressions and resolve them for each state temperature and relevant
      solvent composition.
- [ ] Introduce one resolved model-input object as the sole native serializer;
      delete payload-side default insertion and duplicate serialization.
- [ ] Record schema/preset version, sources, resolution conditions, evaluated
      correlations, structural zeros and native mappings in a reproducible
      mixture/state configuration receipt.
- [ ] Ensure global capabilities list supported schemas/presets while the
      instance receipt alone reports the active policy.
- [ ] Run provider derivative and package tests.
- [ ] Commit: `feat(provider): expose exact model configuration receipts`

## Phase 3: Regression Contract Correctness

### Task 10: Bind Every Public Regression Control To Native Payloads

**Owner:** M5 regression

**Use Cases:**

- Changing weights, loss or fixed parameters produces visible native problem
  differences and corresponding acceptance evidence.
- Post-hoc metadata that described an unsolved problem is replaced by the
  submitted native receipt.

**Files:**

- Modify: `packages/epcsaft-regression/src/epcsaft_regression/core.py`
- Modify: `packages/epcsaft-regression/src/epcsaft_regression/options.py`
- Modify: `packages/epcsaft-regression/src/epcsaft_regression/native_adapter.py`
- Modify: `packages/epcsaft-regression/src/epcsaft_regression/_native_core.pyi`
- Modify: `packages/epcsaft-regression/src/epcsaft_regression/workflow.py`
- Modify: `packages/epcsaft-regression/src/epcsaft_regression/native/regression/module.cpp`
- Modify: `packages/epcsaft-regression/src/epcsaft_regression/native/regression/ceres_regression.cpp`
- Create: `packages/epcsaft-regression/tests/api/test_optimization_contract.py`
- Modify: `packages/epcsaft-regression/tests/native/test_pure.py`
- Modify: `packages/epcsaft-regression/tests/native/test_binary.py`
- Modify: `packages/epcsaft-regression/tests/native/test_liquid_electrolyte.py`

- [ ] Prove pure/binary controls currently leave native outputs byte-identical
      while post-hoc receipts differ; prove target subset/order corruption and
      permissive success classification.
- [ ] Define strict typed iteration/tolerance/loss options; reject unknown keys
      and unsupported fixed/target combinations before native dispatch.
- [ ] Pass every accepted start, bound, weight, row-level robust loss, fixed
      payload, tolerance, iteration limit, target ordering and source-row ID to
      Ceres.
- [ ] Return a native-authored resolved problem receipt and build `FitProblem`
      only from it; delete `_annotate_contract_problem`.
- [ ] Replace cost-nondegradation success shortcuts with explicit Ceres
      termination and solution-usability semantics.
- [ ] Make `Regression(mixture)` consume its configured mixture and remove
      contradictory root free-function exports per ADR 0002.
- [ ] Commit: `fix(regression): honor public optimization controls`

### Task 11: Add Strict Target Data Contracts

**Owner:** M5 regression

**Use Cases:**

- Invalid units, composition basis, source or finite values fail before a
  regression solve and name the bad row.
- Target parsing is cut out of the oversized orchestration module into one
  tested owner.

**Files:**

- Extract from `packages/epcsaft-regression/src/epcsaft_regression/core.py` to
  `packages/epcsaft-regression/src/epcsaft_regression/targets.py`
- Create: `packages/epcsaft-regression/tests/api/test_target_dataset_contract.py`
- Modify: `docs/pages/parameter_regression.rst`

- [ ] Make every public fit accept `TargetDataset`; raw mappings/CSV must cross
      an explicit strict constructor and cannot bypass it.
- [ ] Require unique row IDs, canonical units, observable schema, finite target
      and conditions, explicit species fractions/composition basis, source ID,
      citation metadata, residual scale and positive row weight.
- [ ] Reject inferred missing fractions, implicit normalization, duplicates and
      conflicting observations.
- [ ] Carry row/source IDs into native records, diagnostics and receipts.
- [ ] Commit: `feat(regression): require traceable target contracts`

### Task 12: Rebuild Regression Admission Around Real Data

**Owner:** M5 regression; M6 retained artifacts where applicable

**Use Cases:**

- Users can inspect the exact literature rows, plotted data and acceptance plot
  behind each production regression family.
- Synthetic-only capability claims are retired while their component tests are
  preserved.

**Files:**

- Modify: `packages/epcsaft-regression/src/epcsaft_regression/capabilities.py`
- Modify: `packages/epcsaft/src/epcsaft/runtime/capability_evidence.py`
- Modify relevant `analyses/package_validation/**` regression lanes.
- Create focused capability-evidence tests.

- [ ] Begin with no production regression family; classify all synthetic and
      self-recovery tests as component evidence only.
- [ ] Add complete evidence records with owner, public/native entry points,
      proof nodes/checker, independent source, retained artifact and acceptance
      metrics; reject incomplete production rows in contract tests.
- [ ] Re-admit pure-neutral through the public `Regression` API using traceable
      NIST observations and Gross-Sadowski reference context.
- [ ] Re-admit binary `k_ij` using the Susial 2021 VLE dataset and a package-owned
      prediction oracle; an M4 full-equilibrium plot requires explicit
      cross-milestone ownership.
- [ ] Retain exact source/model tables, native receipt, metrics and plots that
      show observations and predictions, not parameter bars.
- [ ] Keep pure-ion and liquid-electrolyte regression closed until independent
      cited data and public-fit proof exist.
- [ ] Commit: `fix(regression): align capabilities with real-data evidence`

## Phase 4: Equilibrium Scientific Admission

### Task 13: Retain A Complete MEA Chemical-Equilibrium Diagnostic Receipt

**Owner:** M4 equilibrium

**Use Cases:**

- A thermodynamic debugger can inspect every continuation state needed to
  distinguish formulation, derivative, scaling and solver failures.
- Opaque solver rejection is replaced by a retained, independently checkable
  diagnostic receipt without changing production equations.

**Files:**

- Modify: `analyses/package_validation/standalone_ce/scripts/check_standalone_ce.py`
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/core/chemical_equilibrium_nlp.cpp`
- Modify: `packages/epcsaft-equilibrium/tests/native/diagnostics/test_chemical_equilibrium_homotopy.py`
- Modify: `packages/epcsaft-equilibrium/tests/native/diagnostics/test_chemical_equilibrium_eos_activity.py`

- [ ] Reproduce the final continuation failure deterministically.
- [ ] Retain primal, constraints, balance, activity, Jacobian, gradient,
      stationarity, scaling and multiplier data at every continuation step.
- [ ] Add independent numerical-perturbation and analytic-derivative
      consistency tests around the failing point without replacing CppAD
      production derivatives.
- [ ] Commit: `test(equilibrium): retain CE failure diagnostics`

### Task 14: Repair The Canonical Chemical-Equilibrium Formulation

**Owner:** M4 equilibrium

**Use Cases:**

- A traceable MEA state satisfies independent balance and stationarity limits
  at the final physical continuation point.
- The diagnosed defective equation, derivative, convention or scaling owner is
  replaced in its canonical implementation rather than masked by solver tuning.

**Files:**

- Select only after Task 13 identifies the owner; candidates include
  `chemical_equilibrium_block.cpp`, `chemical_equilibrium_objective.cpp`,
  `chemical_equilibrium_nlp.cpp`, and standard-state Python contracts.

- [ ] Form and rank hypotheses from retained evidence.
- [ ] Add one failing test for the selected root cause.
- [ ] Repair the smallest canonical formulation/derivative/scaling owner.
- [ ] Verify balance `<=1e-8`, stationarity `<=1e-6`, final `lambda=1`, and
      accepted native status using traceable MEA inputs.
- [ ] Commit: `fix(equilibrium): satisfy standalone CE thermodynamic proof`

### Task 15: Re-Admit Closed Equilibrium Families Through The Selector

**Owner:** M4 equilibrium

**Use Cases:**

- Users regain reactive speciation, electrolyte LLE or neutral multiphase only
  after that family's public route, native selector, strict checker and retained
  evidence agree.
- Former direct helpers and production declarations remain removed until each
  family independently passes the complete re-admission proof.

**Files:**

- Modify the M4 native selector, route specs, activation/evidence records and
  public workflow surface selected by Tasks 3, 4 and 5.
- Modify each family's retained M4 analysis and focused contract tests with
  source-backed proof artifacts.

- [ ] Add native-selector solve ownership and canonical result-builder input for
      one family at a time.
- [ ] Restore that public API only through `Equilibrium` construction/solve.
- [ ] Register its strict checker and retained literature artifacts in canonical
      evidence.
- [ ] Require full collection/default/confidence gates before opening its
      activation row; do not batch-admit families.
- [ ] Commit one family-specific admission slice after its proof passes.

## Phase 5: Distribution And Downstream Proof

### Task 16: Define And Build The Manylinux Compatibility Target

**Owner:** M3/M4/M5 build metadata by package

**Use Cases:**

- A Linux wheel consumer receives an artifact whose tag matches its actual ELF
  and glibc compatibility proof.
- Host-built `manylinux_2_39` evidence is replaced by a controlled declared
  build baseline rather than relabeled as broader portability.

**Files:**

- Modify: `.github/workflows/wheels.yml`
- Modify: `.github/workflows/package-build-lanes.yml`
- Modify: `.github/workflows/publish-pypi.yml`
- Modify package build backends and pyprojects only as required by proof.

- [ ] Choose a declared manylinux baseline supported by all native dependencies.
- [ ] Build inside that controlled image, not the Ubuntu host.
- [ ] Assert wheel tags and auditwheel policy.
- [ ] Retain ELF dependency receipts.
- [ ] Commit: `build: prove declared manylinux compatibility`

### Task 17: Prove Every Artifact Combination Downstream

**Owner:** package owning each artifact; M3 integration script

**Use Cases:**

- Provider-only and extension consumers can install and run without a source
  checkout or task-local environment variables.
- Missing shared libraries, host RPATH leakage and invalid package combinations
  fail before release publication.

**Files:**

- Modify: `scripts/dev/build_extension_dists.py`
- Modify: `scripts/dev/check_release_installs.py`
- Modify: `tests/workflows/build/test_build_extension_dists.py`
- Modify: `tests/workflows/build/test_build_backend.py`

- [ ] Build provider-only, provider/equilibrium, provider/regression and all
      combinations.
- [ ] Install from artifacts with no checkout paths.
- [ ] Clear `LD_LIBRARY_PATH`; run representative native state, equilibrium and
      regression smokes.
- [ ] Assert RPATH/NEEDED and reject host paths.
- [ ] Commit: `test: prove isolated package combinations`

### Task 18: Align Declared And Tested Python Versions

**Owner:** M3 package metadata, M4/M5 extension metadata

**Use Cases:**

- Each advertised Python minor has wheel, import and native-runtime evidence.
- Unsupported declarations are narrowed instead of leaving users with an
  untested compatibility promise.

**Files:**

- Modify root and package `pyproject.toml` metadata, CI matrices and release
  documentation selected from the declared-version audit.
- Modify focused workflow tests that validate version and artifact matrices.

- [ ] Add CI lanes for every declared Python minor or narrow metadata.
- [ ] Assert wheel/import/native smoke for each supported minor.
- [ ] Update user/release docs with proven support only.
- [ ] Commit: `build: align Python support with release proof`

## Phase 6: Maintainability Cut Lines

### Task 19: Add Characterization Maps And File-Size Gates

**Owner:** each package

**Use Cases:**

- A maintainer can trace each public call to its native owner, result builder
  and admission evidence before changing a large module.
- New growth in already oversized production files requires an explicit owner
  boundary or ADR rather than silently deepening the monolith.

**Files:**

- Create package-owned characterization maps in the existing architecture
  documentation category.
- Modify repository structure validators and focused characterization tests.

- [ ] Map public entry points to native owner, result builder and proof nodes.
- [ ] Add characterization tests around route payloads and regression receipts.
- [ ] Add a changed-production-file review gate for files above 1,000 lines,
      with ADR-based exceptions only.
- [ ] Commit: `test: characterize large-module ownership boundaries`

### Task 20: Decompose Equilibrium Along Canonical Owners

**Owner:** M4 equilibrium

**Use Cases:**

- Route formulation, selector orchestration, result acceptance and bindings can
  evolve independently behind characterized contracts.
- Superseded per-route acceptance branches and pass-through bindings are
  deleted after their callers use the canonical owners.

**Files:**

- Modify the characterized M4 native route, selector, result and binding files
  identified by Task 19 in small non-overlapping slices.
- Modify focused M4 characterization and confidence tests with each extraction.

- [ ] Extract thermodynamic route formulations from orchestration.
- [ ] Keep one selector dispatcher and one result/acceptance builder.
- [ ] Split binding registration by public domain surface.
- [ ] Delete superseded condition branches and pass-through wrappers.
- [ ] Prove identical characterization outputs and confidence results.
- [ ] Commit in small owner-specific slices.

### Task 21: Decompose Regression And Dataset Responsibilities

**Owner:** M5 regression for `core.py`; M3 provider for `datasets.py`

**Use Cases:**

- Regression contracts, payload construction, native execution and results
  have separately testable owners.
- Provider data provenance, validation and lookup policy no longer share one
  module or preserve wrappers from invented-default behavior.

**Files:**

- Modify `packages/epcsaft-regression/src/epcsaft_regression/core.py` and create
  package-local modules selected by the Task 19 characterization map.
- Modify `packages/epcsaft/src/epcsaft/model/datasets.py` and create
  package-local data-contract modules selected by the same map.

- [ ] Extract typed contracts, native payloads, results and route adapters from
      regression `core.py`.
- [ ] Separate provider data storage/provenance, validation and lookup policy.
- [ ] Delete wrappers that no longer own behavior.
- [ ] Prove reduced branching/coupling and unchanged characterized numerics.
- [ ] Commit in package-owned slices.

### Task 22: Run The Full Program Proof And Retire This Plan

**Owner:** main thread integration

**Use Cases:**

- Maintainers receive one reproducible proof that public claims, scientific
  evidence, artifacts, docs and package tests agree.
- Temporary execution documents are removed only after their durable rules and
  evidence live in canonical project documentation and tests.

**Files:**

- Modify canonical project context, ADR, capability, release and development
  documentation with the durable outcomes of completed tasks.
- Delete this plan and its implementation-specific spec only after all program
  acceptance gates pass and no unique requirement remains in them.

- [ ] Run all package/repo tests and explicit analysis lanes.
- [ ] Build/install all release artifacts in declared environments.
- [ ] Render every changed scientific plot and summarize retained source data.
- [ ] Run Ruff, Sphinx, ShellCheck, YAML/TOML, `git diff --check`, status and
      cleanup.
- [ ] Request independent code and thermodynamic review.
- [ ] Move durable rules into project context/ADR/docs.
- [ ] Remove this completed plan and the implementation-specific spec after all
      behavior is durably represented elsewhere.

## Phase 1 Proof Oracle

```bash
uv run --no-sync python -m pytest --collect-only -q
uv run --no-sync python run_pytest.py --all --collect-only -q
uv run --no-sync python run_pytest.py -q
uv run --no-sync python run_pytest.py --confidence -q
uv run --no-sync python run_pytest.py --equilibrium-confidence -q
uv run --no-sync python -m pytest packages/epcsaft-equilibrium/tests/contracts/test_activation_capabilities.py tests/native/contracts/test_standalone_ce_gate.py tests/workflows/repo/test_project_structure.py tests/workflows/repo/test_run_pytest.py -q
uv run --no-sync python scripts/dev/validate_project.py docs
uv run --no-sync ruff check .
git diff --check
bash "$HOME/.codex/hooks/codex-cleanup.sh" --repo-root .
```

## Full Program Proof Oracle

```bash
uv run --no-sync python run_pytest.py --all -q
uv run --no-sync python scripts/dev/validate_project.py confidence
uv run --no-sync python scripts/dev/validate_project.py docs
uv run --no-sync python scripts/dev/build_dist.py
uv run --no-sync python scripts/dev/build_extension_dists.py --mode monorepo --parallel 1
uv run --no-sync python scripts/dev/build_extension_dists.py --mode installed-provider --parallel 1
uv run --no-sync python scripts/dev/check_release_installs.py --dist-dir dist --combination all
uv run --no-sync ruff format --check .
uv run --no-sync ruff check .
git diff --check
bash "$HOME/.codex/hooks/codex-cleanup.sh" --repo-root .
git status --short
```
