# M1 Local Linux Package Reproducibility Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build all three distributions on the current Zorin/Python 3.13 host and prove four isolated installed-package combinations with native smokes, ELF inspection, and one machine-readable receipt.

**Architecture:** Replace the release-named install helper with a current-host gate composed of a small reusable receipt/inspection module and one CLI orchestrator. The orchestrator refuses dirty tracked state, builds provider plus installed-provider extension artifacts into an empty task-owned artifact root, creates four virtual environments under a recorded temporary root outside the checkout from locked third-party dependencies and exact local wheels, runs native smokes from an external working directory, inspects module/linker origins, then validates and writes one schema-versioned receipt.

**Tech Stack:** CPython 3.13, uv, Python standard library, PEP 517, scikit-build-core, CMake 3.28, Ninja 1.11, GCC 13, CppAD, Ceres, Ipopt, pytest, `readelf`, `ldd`, SHA-256, JSON, Sphinx, Ruff.

## Global Constraints

- Milestone ownership is M1 Packages. This is local Linux reproducibility, not M7 release readiness.
- Prove only the Python minor in `.python-version` (`3.13`) on the host executing the command. Do not change any package `requires-python` field.
- Record the host exactly; do not claim manylinux, older glibc, another distribution, Windows, macOS, ARM, musl, or another Python version.
- Build provider, equilibrium, and regression from one clean commit and one recorded dependency environment.
- The clean commit must already contain the coordinated M3 resolved-model-input
  provider cutover and its M4/M5 consumer integrations. This plan is blocked by
  those three integration leaves and must not certify artifacts built from the
  displaced model-input SDK.
- Extension artifacts must consume the installed provider SDK. Monorepo-provider mode cannot satisfy the final receipt.
- A real Ipopt SDK and a real Ceres configuration are required. There is no no-Ipopt or import-only success path.
- Prove exactly four combinations: provider; provider plus equilibrium; provider plus regression; all three.
- Project packages install from exact wheels in the new artifact directory. Third-party dependencies come from the frozen lock export, never editable/workspace paths.
- Installed-runtime commands run from outside the checkout with checkout paths removed from `PYTHONPATH` and `LD_LIBRARY_PATH` unset.
- Native smokes prove component/runtime operation only. They do not admit a regression or equilibrium family or change scientific capabilities.
- Do not add PyPI upload, tag, GitHub release, signing, manylinux, auditwheel breadth, or public-install workflow.
- Replace `scripts/dev/check_release_installs.py`; do not leave a redirector.
- Use test-driven development for behavior changes, systematic debugging for build/runtime failures, and fresh verification before completion.

---

## Source Evidence

- Approved design: `docs/superpowers/specs/2026-07-10-m1-local-linux-package-reproducibility.md`.
- Blocking provider/consumer cutover:
  `docs/superpowers/plans/2026-07-10-m3-eos-versioned-state-resolved-model-input-plan.md`
  Task 8 plus its separately owned M4 and M5 resolved-input consumer leaves.
- Build policy: `docs/protocols/build_package_dependency_protocol.rst` and `CMAKE.md`.
- Package ownership: `docs/adr/0005-package-extension-split.md`.
- Verified planning host on 2026-07-10:
  - `.python-version`: `3.13`;
  - `uv run --no-sync python`: CPython `3.13.14`;
  - OS: Zorin OS `18.1`, Ubuntu/Debian family;
  - architecture: `x86_64`;
  - CMake `3.28.3`, Ninja `1.11.1`, GCC `13.3.0`, uv `0.11.28`.
- Existing provider build owner: `scripts/dev/build_dist.py`.
- Existing extension build owner: `scripts/dev/build_extension_dists.py`; its installed-provider mode already discovers the SDK from an installed provider wheel.
- Replaced helper: `scripts/dev/check_release_installs.py`; it installs four combinations but performs import/SDK checks only and inserts a target directory into `sys.path`.
- Current manual callers: `.github/workflows/package-build-lanes.yml`, `docs/pages/development_workflows.rst`, `docs/pages/release_installation.rst`, `docs/pages/publishing.rst`, and `docs/protocols/build_package_dependency_protocol.rst`.
- Admitted equilibrium smoke evidence remains read-only: `analyses/package_validation/equilibrium_single_component_vle/figures/hydrocarbon_saturation_pressure/results/hydrocarbon_saturation_pressure_plotted_data.csv` and `hydrocarbon_saturation_pressure.png`.

## Test Complete And Metrics

Test complete means one clean committed run produces `build/local-linux-package-proof/local-linux-package-proof.json` with:

1. receipt schema `epcsaft.local-linux-package-proof`, schema version `1`, clean commit SHA, Python `3.13`, exact host/tool/dependency identities, and exact command/environment records;
2. one wheel and one sdist for each of `epcsaft`, `epcsaft-equilibrium`, and `epcsaft-regression`, with filename, normalized version, wheel tag where applicable, byte size, and SHA-256;
3. proof that both extension builds used the SDK exposed by the newly built and installed provider wheel;
4. four fresh virtual environments outside the checkout, exact local project-wheel origins, compatible installed dependency sets, and no checkout import origin;
5. provider native state smoke, one currently admitted `single_component_vle` smoke backed by the retained input/plot identity, a Ceres native component smoke, and all three smokes in one process for the combined environment;
6. `readelf -d` and `ldd` records for every installed native module, no missing library, and no checkout/build/cache RPATH, RUNPATH, or resolved dependency;
7. mutation tests rejecting dirty tracked state, wrong Python minor, stale/mixed/duplicate artifacts, version mismatch, malformed receipt, checkout import, missing shared library, and unexpected runtime path;
8. focused workflow tests, Ruff, strict docs, `git diff --check`, and cleanup passing.

The gate uses exact identity/equality checks and process exit status. It introduces no scientific numerical acceptance threshold.

## Outcome Proof

**Intent:** Prove that the current private Linux checkout can produce and run its three package artifacts outside the source tree without confusing that local result with public portability.
**Current Behavior:** Provider and extension build helpers exist, while `check_release_installs.py` installs into target directories under the checkout, mutates `sys.path`, checks imports/SDK metadata, and labels the result as release proof without native operation, ELF, or one-run receipt evidence.
**Expected Outcome:** One current-host command builds all artifacts through the installed-provider SDK boundary, proves four isolated environments and native operations, rejects source/runtime leakage, and writes a validated local receipt.
**Target Output:** `scripts/dev/check_local_linux_packages.py`, reusable receipt/inspection helpers, focused mutation tests, build-helper output-directory support, renamed callers/docs, and one ignored task-owned proof root.
**Owner:** M1 Packages owns the cross-package gate; provider/equilibrium/regression retain ownership of their own build metadata and native modules.
**Interface:** `check_local_linux_packages.py --output-root ... [--environment-root ...] [--ipopt-root ...] [--ceres-dir ...]`, `validate_local_linux_receipt(path)`, `build_dist.py --dist-dir`, and `build_extension_dists.py --dist-dir --mode installed-provider`.
**Cutover:** Update every live caller to the local-Linux command and delete `check_release_installs.py` in the same series.
**Replaced Path:** Target-directory import smoke under `build/release-install-proof`, release-oriented command/status text, and independent green jobs that can be combined across commits.
**Evidence:** Unit/mutation tests, six artifact hashes, four external environment receipts, native smoke outputs, native module origins, `readelf`/`ldd` records, receipt validation, docs/Ruff/diff/cleanup results.
**Acceptance Proof:** Starting from a clean commit and empty output root, one command exits zero only after all artifacts and all four combinations pass in that same run; the receipt revalidates independently and shows no source-path or unresolved-library leakage.
**Stop Criteria:** Stop before execution if the coordinated M3/M4/M5
resolved-input cutover is not integrated; otherwise stop on dirty tracked
state, wrong Python minor, missing build tool/native SDK, mixed artifact
commit/version, unavailable installed-provider SDK, closed equilibrium route
substitution, missing Ceres/Ipopt operation, source-path leakage, unresolved
library, or incomplete receipt.
**Avoid:** Do not weaken native smokes to imports, synthesize dependency identities, write user paths into package defaults, change scientific capability metadata, alter `requires-python`, publish artifacts, or describe the receipt as cross-host support.
**Risk:** Local native dependency drift and implicit checkout imports can make a package appear healthy when only the development tree works; strict origin/linkage capture may expose existing local-path coupling that must be diagnosed before the gate can pass.

## Implementation Boundaries

**Files To Create:** `scripts/dev/local_linux_package_proof.py`, `scripts/dev/check_local_linux_packages.py`, and `tests/workflows/repo/test_local_linux_package_reproducibility.py`.
**Files To Modify:** `scripts/dev/build_dist.py`, `scripts/dev/build_extension_dists.py`, `.github/workflows/package-build-lanes.yml`, `tests/workflows/repo/test_workflow_entrypoints.py`, `docs/protocols/build_package_dependency_protocol.rst`, `docs/pages/development_workflows.rst`, `docs/pages/release_installation.rst`, and `docs/pages/publishing.rst`.
**Files To Avoid:** `packages/*/pyproject.toml` Python support metadata, `.python-version`, `.github/workflows/publish-pypi.yml`, `.github/workflows/wheels.yml`, solver/EOS sources, capability registries, paper-validation programs, and M7 release backlog issue #195.
**Source Of Truth:** `.python-version`, the current clean Git commit, package metadata, provider SDK discovery, explicit/discovered Ceres and Ipopt configs, frozen `uv.lock`, installed module metadata, and system linker output.
**Read Path:** Capture host/tools/dependencies; build into the task-owned artifact directory; export locked third-party requirements; install exact local wheels into four external environments; run smokes; inspect module/linker origins; validate the receipt.
**Write Path:** Write artifacts/receipt only under the caller-selected output root (default `build/local-linux-package-proof`); write install environments and runtime working files under a recorded task-owned root outside the checkout; use build helpers' task-owned native directories. No installed proof artifact is tracked.
**Integration Points:** PEP 517 build helpers, provider native SDK, equilibrium/regression native modules, uv lock export, `readelf`, `ldd`, manual package-build workflow, development/build docs, and cleanup audit.
**Migration Or Cutover:** After the coordinated M3 provider plus M4/M5 consumer
cutover is integrated, add output-directory support, build the new
command/tests, update all callers, delete the retired helper, then execute the
complete gate from a clean commit.
**Replaced Path Handling:** Structural tests require `scripts/dev/check_release_installs.py` and its live references to be absent; historical specs/issues may retain dated references.
**Acceptance Proof Gate:** Do not mark M1 complete until the receipt's commit
contains the M3 resolved-input cutover and both M4/M5 consumer integrations and
the full one-run receipt independently validates on the current host; focused
unit tests alone are insufficient.

## Decision Ledger

| Decision | Evidence | Selected answer | Consequence | Deferred? | Owner |
| --- | --- | --- | --- | --- | --- |
| Milestone | Private local package boundary | M1 Packages, not M7 Release. | No public distribution claim. | No | M1 |
| Python | `.python-version` and verified uv runtime | Require current minor `3.13`; record exact patch. | Broader declared metadata remains unchanged. | No | M1 |
| Platform | Verified Zorin host | Record executing host, architecture, kernel, and toolchain. | No cross-Linux promise. | No | M1 |
| Artifact boundary | Source checkout can hide packaging faults | Build all three distributions and extensions from installed provider SDK. | Monorepo mode is not final evidence. | No | M1 |
| Model-input cutover | M3 owns a coordinated incompatible provider/consumer SDK change | Block M1 execution until the M3 provider and M4/M5 consumer leaves are integrated. | The receipt proves the current SDK rather than an already displaced package graph. | No | M1/M3/M4/M5 |
| Dependency install | Isolated environments need runtime dependencies without workspace paths | Export frozen third-party requirements, install them first, then install exact local project wheels with dependency resolution disabled. | Project code cannot come from the index or checkout. | No | M1 |
| Install matrix | Three distributions have four supported combinations | Prove provider, equilibrium, regression, and all. | One failed combination rejects the receipt. | No | M1 |
| Equilibrium smoke | Current public truth | Use one admitted `single_component_vle` retained point. | Closed routes cannot substitute. | No | M1/M4 |
| Regression smoke | M5 admission is separate | Run `_native_ceres_smoke` as a component check only. | No regression-family claim. | No | M1/M5 |
| Receipt | Runs must not compose across commits | One JSON schema version 1 written only after all checks pass. | Partial runs remain diagnostic only. | No | M1 |
| Release breadth | User selected minimal Linux proof | Keep issue #195 deferred. | manylinux/PyPI/multi-Python work remains M7. | Yes | M7 |

## Tasks

### Task 1: Define The Current-Host Receipt And Failure Contract

**Use Cases:**

- A maintainer can validate host/Python/clean-tree prerequisites before spending time on native builds.
- Artifact and receipt mutations fail with exact diagnostics.
- A completed receipt is canonical, detached, and tied to one commit/run.
- These checks replace informal release-proof status text with machine-readable local evidence.

**Files:**

- Create: `scripts/dev/local_linux_package_proof.py`
- Create: `tests/workflows/repo/test_local_linux_package_reproducibility.py`

**Interfaces:**

- Consumes: `.python-version`, `uv.lock`, Git status/commit, `/etc/os-release`, tool version commands, package artifacts, and JSON.
- Produces: `LOCAL_LINUX_RECEIPT_SCHEMA = "epcsaft.local-linux-package-proof"`, version `1`, `capture_environment()`, `assert_clean_tracked_worktree()`, `artifact_record(path)`, `validate_local_linux_receipt(path)`, and canonical receipt writer.

- [ ] **Step 1: Write RED unit/mutation tests.**

  Define the required top-level receipt shape in tests:

  ```python
  REQUIRED_RECEIPT_KEYS = {
      "schema",
      "schema_version",
      "repository",
      "environment",
      "native_dependencies",
      "artifacts",
      "combinations",
      "commands",
      "status",
  }
  ```

  Test wrong Python minor, dirty tracked files, malformed OS data, missing tools, bad SHA-256, duplicate/mixed artifacts, wrong versions, partial combinations, malformed linker records, and non-`passed` status.

- [ ] **Step 2: Verify RED.**

  Run:

  ```bash
  uv run --no-sync pytest -q tests/workflows/repo/test_local_linux_package_reproducibility.py
  ```

  Expected: collection succeeds and tests fail because the receipt module does not exist.

- [ ] **Step 3: Implement pure capture/validation helpers.**

  Use immutable records internally and JSON at the boundary:

  ```python
  @dataclass(frozen=True, slots=True)
  class ArtifactRecord:
      distribution: str
      version: str
      kind: Literal["wheel", "sdist"]
      filename: str
      size_bytes: int
      sha256: str
      wheel_tag: str | None

  def validate_local_linux_receipt(path: Path) -> dict[str, object]: ...
  ```

  Derive the required Python minor from `.python-version`; capture exact patch/host/tool versions without hard-coding the planning host values as compatibility checks.

- [ ] **Step 4: Run GREEN and refactor.**

  Run the Task 1 test command again. Expected: all tests pass using temporary synthetic artifacts/receipts; no native build runs in this unit slice.

- [ ] **Step 5: Checkpoint commit.**

  ```bash
  git add \
    scripts/dev/local_linux_package_proof.py \
    tests/workflows/repo/test_local_linux_package_reproducibility.py
  git commit -m "test(packaging): define local Linux proof receipt"
  ```

### Task 2: Build Six Artifacts Through The Installed-Provider SDK Boundary

**Use Cases:**

- One empty artifact directory receives a wheel and sdist for each distribution.
- Both extensions build against the SDK from the new provider wheel.
- Stale, mixed-version, duplicate, or source-tree-SDK artifacts fail before installation.
- Output-directory support replaces reliance on shared `dist/` state.

**Files:**

- Modify: `scripts/dev/build_dist.py`
- Modify: `scripts/dev/build_extension_dists.py`
- Modify: `scripts/dev/local_linux_package_proof.py`
- Modify: `tests/workflows/repo/test_local_linux_package_reproducibility.py`

**Interfaces:**

- Consumes: existing provider/extension build flags and installed-provider SDK discovery.
- Produces: `build_dist.py --dist-dir PATH`, `build_extension_dists.py --dist-dir PATH`, and `build_all_artifacts(output_root, ipopt_root, ceres_dir) -> tuple[ArtifactRecord, ...]`.

- [ ] **Step 1: Add RED command-construction and artifact-set tests.**

  Assert the provider command receives the selected artifact directory; extension command is exactly `--mode installed-provider`; Ceres/Ipopt inputs are validated and recorded; the accepted artifact set contains exactly three wheels and three sdists with one shared normalized version.

- [ ] **Step 2: Verify RED.**

  Run:

  ```bash
  uv run --no-sync pytest -q \
    tests/workflows/repo/test_local_linux_package_reproducibility.py \
    tests/workflows/repo/test_workflow_entrypoints.py -k 'package or dist or extension'
  ```

  Expected: failures show build helpers hard-code `dist/` and the orchestrator does not exist.

- [ ] **Step 3: Add explicit output-directory support.**

  Thread `Path(args.dist_dir).resolve()` through cleaning, artifact discovery, staging, restore, and `uv build --out-dir`. Keep default `dist/` for direct developer use, but the canonical M1 command always supplies its task-owned directory.

- [ ] **Step 4: Add the orchestrated build sequence.**

  The command order is:

  ```text
  build_dist.py --dist-dir <output>/artifacts --parallel 1
  install the resulting provider wheel into <output>/provider-sdk-env
  build_extension_dists.py --dist-dir <output>/artifacts --mode installed-provider --parallel 1
  assert one wheel + one sdist per distribution, one version, one commit
  hash every artifact
  ```

  The orchestrator refuses a nonempty output root rather than mixing with old artifacts.

- [ ] **Step 5: Run GREEN and refactor.**

  Re-run the Task 2 focused tests. Expected: command and artifact mutation tests pass without launching full builds; helpers remain importable for tests.

- [ ] **Step 6: Checkpoint commit.**

  ```bash
  git add \
    scripts/dev/build_dist.py \
    scripts/dev/build_extension_dists.py \
    scripts/dev/local_linux_package_proof.py \
    tests/workflows/repo/test_local_linux_package_reproducibility.py \
    tests/workflows/repo/test_workflow_entrypoints.py
  git commit -m "build(packaging): isolate local Linux artifacts"
  ```

### Task 3: Prove Four External Install Combinations With Native Smokes

**Use Cases:**

- Each supported combination installs into a fresh environment outside the checkout.
- Provider state evaluation proves the provider native module runs.
- Equilibrium executes one admitted source-backed route; regression executes Ceres component code without claiming family admission.
- The all-package environment proves the three native modules coexist in one process.

**Files:**

- Create: `scripts/dev/check_local_linux_packages.py`
- Modify: `scripts/dev/local_linux_package_proof.py`
- Modify: `tests/workflows/repo/test_local_linux_package_reproducibility.py`

**Interfaces:**

- Consumes: six artifact records, frozen third-party dependency export, admitted single-component VLE input identity, provider SDK, `_native_ceres_smoke`, and current public equilibrium API.
- Produces: `create_install_environment(name, requirements, wheels, environment_root)`, `run_provider_smoke`, `run_equilibrium_smoke`, `run_regression_smoke`, `run_combined_smoke`, and per-combination receipt records.

- [ ] **Step 1: Add RED environment/origin/smoke-dispatch tests.**

  Use subprocess fakes only at the process boundary. Assert the environment root and runtime cwd are outside the checkout, no checkout `PYTHONPATH`, unset `LD_LIBRARY_PATH`, exact local wheel arguments, frozen non-workspace requirements, four distinct environments, required smoke dispatch, and nonzero-exit rejection.

- [ ] **Step 2: Verify RED.**

  Run:

  ```bash
  uv run --no-sync pytest -q tests/workflows/repo/test_local_linux_package_reproducibility.py
  ```

  Expected: failures identify the missing CLI/environment/smoke functions.

- [ ] **Step 3: Implement locked dependency and exact-wheel installation.**

  Resolve `--environment-root` to an absolute directory outside the repository; when omitted, create one with `tempfile.mkdtemp(prefix="epcsaft-local-linux-")` under the host temporary directory and record it. For each environment:

  ```text
  uv venv <external-env>
  uv export --frozen --no-dev --no-emit-project --no-emit-workspace --no-emit-local
  uv pip sync --python <external-env>/bin/python <output>/runtime-requirements.txt
  uv pip install --python <external-env>/bin/python --no-deps <exact project wheel paths>
  uv pip check --python <external-env>/bin/python
  ```

  Capture `uv pip freeze` and package/module origins. Reject any origin under the checkout.

- [ ] **Step 4: Implement the exact smoke classifications.**

  - Provider: construct explicit methane parameters/model configuration through the installed public API and evaluate a native `State` property.
  - Equilibrium: run one retained methane `single_component_vle` point selected from the tracked plotted-data CSV; copy only that input row and its source/plot hash into the task output before the external run.
  - Regression: call the installed regression module's native Ceres component smoke and require compiled/run success; label it `component_smoke`, not family admission.
  - Combined: run all three in one interpreter and capture all module/native origins.

- [ ] **Step 5: Run GREEN and refactor.**

  Re-run the Task 3 unit tests. Expected: all environment/origin/dispatch mutations pass. Keep scientific fixture extraction separate from smoke execution so the external process never imports checkout code.

- [ ] **Step 6: Checkpoint commit.**

  ```bash
  git add \
    scripts/dev/check_local_linux_packages.py \
    scripts/dev/local_linux_package_proof.py \
    tests/workflows/repo/test_local_linux_package_reproducibility.py
  git commit -m "feat(packaging): prove isolated local Linux installs"
  ```

### Task 4: Inspect ELF Resolution And Finalize One-Run Receipt Validation

**Use Cases:**

- Every installed native module records its origin, dynamic dependencies, RPATH/RUNPATH, and resolved libraries.
- Missing libraries or checkout/build/cache linkage reject the run.
- Only a run with six artifacts and four passing combinations can write `status: passed`.
- The receipt revalidates independently after the orchestration process exits.

**Files:**

- Modify: `scripts/dev/local_linux_package_proof.py`
- Modify: `scripts/dev/check_local_linux_packages.py`
- Modify: `tests/workflows/repo/test_local_linux_package_reproducibility.py`

**Interfaces:**

- Consumes: installed native module paths, `readelf -d`, `ldd`, artifact/combination records.
- Produces: `inspect_elf(module_path) -> ElfRecord`, `assert_runtime_paths(record, allowed_roots)`, atomic receipt write, and independent `--validate-receipt PATH` mode.

- [ ] **Step 1: Add RED linker/receipt mutation tests.**

  Include fixtures for `not found`, checkout RPATH, build-tree RUNPATH, cache resolution, missing module, duplicate module origin, wrong artifact hash, missing combination, and mixed run/commit IDs.

- [ ] **Step 2: Verify RED.**

  Run:

  ```bash
  uv run --no-sync pytest -q tests/workflows/repo/test_local_linux_package_reproducibility.py
  ```

  Expected: linker/atomic-receipt tests fail because inspection and final validation are absent.

- [ ] **Step 3: Implement ELF inspection and allowed-root policy.**

  Run `readelf -d` and `ldd` on each installed `.so`. Allow the active environment, audited explicit/discovered native dependency roots, and system library roots. Reject checkout/build/cache paths and unresolved entries; record every raw command and parsed entry.

- [ ] **Step 4: Implement atomic final receipt.**

  Build the complete mapping in memory, validate it, write to a sibling temporary file, `fsync`, and atomically replace `local-linux-package-proof.json`. Do not write a passed receipt after a partial failure.

- [ ] **Step 5: Run GREEN and focused Ruff.**

  ```bash
  uv run --no-sync pytest -q tests/workflows/repo/test_local_linux_package_reproducibility.py
  uv run --no-sync ruff check \
    scripts/dev/local_linux_package_proof.py \
    scripts/dev/check_local_linux_packages.py \
    tests/workflows/repo/test_local_linux_package_reproducibility.py
  ```

  Expected: all focused tests and Ruff pass.

- [ ] **Step 6: Checkpoint commit.**

  ```bash
  git add \
    scripts/dev/local_linux_package_proof.py \
    scripts/dev/check_local_linux_packages.py \
    tests/workflows/repo/test_local_linux_package_reproducibility.py
  git commit -m "feat(packaging): retain local Linux native receipt"
  ```

### Task 5: Cut Over Callers, Documentation, And Execute The Clean Host Gate

**Use Cases:**

- Developers and manual CI use the same accurately named local-Linux command.
- Release docs distinguish the current-host receipt from deferred M7 publication work.
- The retired helper and release-proof wording cannot return unnoticed.
- A clean post-commit run supplies the final M1 acceptance evidence.

**Files:**

- Delete: `scripts/dev/check_release_installs.py`
- Modify: `.github/workflows/package-build-lanes.yml`
- Modify: `tests/workflows/repo/test_workflow_entrypoints.py`
- Modify: `docs/protocols/build_package_dependency_protocol.rst`
- Modify: `docs/pages/development_workflows.rst`
- Modify: `docs/pages/release_installation.rst`
- Modify: `docs/pages/publishing.rst`
- Modify: `tests/workflows/repo/test_local_linux_package_reproducibility.py`

**Interfaces:**

- Consumes: completed local-Linux CLI/receipt validator, existing manual package
  lanes/docs, and a clean revision containing the coordinated M3/M4/M5
  resolved-input cutover.
- Produces: one canonical command name, structural absence checks, accurate current-host documentation, and the final receipt path.

- [ ] **Step 1: Add RED cutover tests.**

  Assert all live callers use `scripts/dev/check_local_linux_packages.py`, the retired helper is absent, the manual workflow does not label component smokes as release checks, and docs state current-host/Python 3.13 scope plus deferred M7 breadth.

- [ ] **Step 2: Verify RED.**

  Run:

  ```bash
  uv run --no-sync pytest -q \
    tests/workflows/repo/test_local_linux_package_reproducibility.py \
    tests/workflows/repo/test_workflow_entrypoints.py
  ```

  Expected: stale command and wording assertions fail.

- [ ] **Step 3: Replace callers and delete the retired helper.**

  Update manual workflow steps to use the new name and scoped labels. Update build/development docs with the exact command and receipt path. Keep public publishing/manylinux material explicitly deferred to M7; do not present this gate as its substitute.

- [ ] **Step 4: Run focused GREEN, docs, diff, and cleanup.**

  ```bash
  uv run --no-sync pytest -q \
    tests/workflows/repo/test_local_linux_package_reproducibility.py \
    tests/workflows/repo/test_workflow_entrypoints.py \
    tests/workflows/repo/test_package_extension_boundary.py
  uv run --no-sync ruff check scripts/dev tests/workflows/repo
  uv run --no-sync python scripts/dev/validate_project.py docs
  git diff --check
  bash "$HOME/.codex/hooks/codex-cleanup.sh" --repo-root .
  ```

  Expected: all named checks exit zero and cleanup reports no task-owned residue outside the ignored proof root.

- [ ] **Step 5: Checkpoint the cutover before the clean-tree proof.**

  ```bash
  git add \
    scripts/dev/check_release_installs.py \
    .github/workflows/package-build-lanes.yml \
    tests/workflows/repo/test_workflow_entrypoints.py \
    tests/workflows/repo/test_local_linux_package_reproducibility.py \
    docs/protocols/build_package_dependency_protocol.rst \
    docs/pages/development_workflows.rst \
    docs/pages/release_installation.rst \
    docs/pages/publishing.rst
  git commit -m "docs(packaging): define current-host Linux proof"
  ```

- [ ] **Step 6: Run the complete gate from the clean committed revision.**

  First verify the checked-out commit satisfies both provider consumer-contract
  tests named by the M3 cutover plan; a missing integration is a dependency
  blocker, not a packaging failure to work around. Then run with protocol
  discovery; the receipt records the selected Ipopt/Ceres source and paths:

  ```bash
  uv run --no-sync pytest -q \
    packages/epcsaft-equilibrium/tests/contracts/test_provider_resolved_input_integration.py \
    packages/epcsaft-regression/tests/contracts/test_provider_resolved_input_integration.py
  uv run --no-sync python scripts/dev/check_local_linux_packages.py \
    --output-root build/local-linux-package-proof
  uv run --no-sync python scripts/dev/check_local_linux_packages.py \
    --validate-receipt build/local-linux-package-proof/local-linux-package-proof.json
  ```

  Expected: six artifacts, four passing combinations, native/linker records, and independently valid status `passed`. If an audited explicit dependency root is required, rerun from a fresh output root with `--ipopt-root` and/or `--ceres-dir`; never reuse the failed output root.

- [ ] **Step 7: Run final cleanup without deleting the retained receipt.**

  ```bash
  bash "$HOME/.codex/hooks/codex-cleanup.sh" --repo-root .
  git status --short
  ```

  Expected: cleanup passes and Git shows no tracked changes. The ignored task-owned receipt remains available for the handoff.

## Proof Oracle

```bash
uv run --no-sync python scripts/validate_plan_task_use_cases.py --plan-path docs/superpowers/plans/2026-07-10-m1-local-linux-package-reproducibility-plan.md
uv run --no-sync python scripts/validate_plan_outcome_proof.py --plan-path docs/superpowers/plans/2026-07-10-m1-local-linux-package-reproducibility-plan.md
uv run --no-sync pytest -q tests/workflows/repo/test_local_linux_package_reproducibility.py tests/workflows/repo/test_workflow_entrypoints.py tests/workflows/repo/test_package_extension_boundary.py
uv run --no-sync ruff check scripts/dev tests/workflows/repo
uv run --no-sync python scripts/dev/validate_project.py docs
uv run --no-sync pytest -q packages/epcsaft-equilibrium/tests/contracts/test_provider_resolved_input_integration.py packages/epcsaft-regression/tests/contracts/test_provider_resolved_input_integration.py
uv run --no-sync python scripts/dev/check_local_linux_packages.py --output-root build/local-linux-package-proof
uv run --no-sync python scripts/dev/check_local_linux_packages.py --validate-receipt build/local-linux-package-proof/local-linux-package-proof.json
git diff --check
bash "$HOME/.codex/hooks/codex-cleanup.sh" --repo-root .
git status --short
```
