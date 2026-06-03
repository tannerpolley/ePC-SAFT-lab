# Nested AGENTS Instruction Strategy Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add five approved nested `AGENTS.md` files and a repo-structure guard so package and analysis subtrees get precise Codex instructions without duplicating root policy.

**Architecture:** Root `AGENTS.md` remains the short repo-wide router. Nested files only add subtree-specific package or analysis behavior, and `tests/workflows/repo/test_project_structure.py` records the expected nested instruction set so drift is visible in routine validation.

**Tech Stack:** Markdown repo instructions, pytest project-structure tests, Superpowers Project docs under `docs/superpowers`.

---

## Intake

- Source Spec: `docs/superpowers/specs/2026-06-02-m0-governance-nested-agents-instruction-strategy-design.md`
- Source Issue: none yet
- Milestone: `M0 - Governance`
- TDD Policy: Required for the structure guard.
- Completion Sub-Skill: Use `superpowers:verification-before-completion` before claiming the issue complete.

## Acceptance Criteria

- [ ] `packages/epcsaft/AGENTS.md` exists and contains provider-only instructions for EOS/state/parameter/native SDK work.
- [ ] `packages/epcsaft-equilibrium/AGENTS.md` exists and contains equilibrium route, Ipopt, GFPE, solver-status, and derivative-assembly instructions.
- [ ] `packages/epcsaft-regression/AGENTS.md` exists and contains regression/Ceres/target-dataset instructions.
- [ ] `analyses/AGENTS.md` exists and contains reproducible analysis artifact-layout instructions.
- [ ] `analyses/paper_validation/AGENTS.md` exists and contains the paper-validation exception layout from `docs/pages/project_structure.rst`.
- [ ] `tests/workflows/repo/test_project_structure.py` fails if any expected nested instruction file is missing, if extra nested `AGENTS.md` files appear outside the approved set, or if nested instructions contain machine-local user paths.
- [ ] `tests/workflows/repo/test_project_structure.py` tracks the source spec under `docs/superpowers/specs`.
- [ ] Public package APIs, native code, capability claims, and runtime behavior are unchanged.

## Non-Goals

- Do not change provider, equilibrium, regression, or native implementation behavior.
- Do not add nested instruction files below package internals such as `native/`, `tests/`, or `src/`.
- Do not duplicate root Git, cleanup, IntelliJ, tracker, or global milestone policy inside nested files.
- Do not edit user-level Codex instructions.

## File Map

- Create: `packages/epcsaft/AGENTS.md`
- Create: `packages/epcsaft-equilibrium/AGENTS.md`
- Create: `packages/epcsaft-regression/AGENTS.md`
- Create: `analyses/AGENTS.md`
- Create: `analyses/paper_validation/AGENTS.md`
- Modify: `tests/workflows/repo/test_project_structure.py`
- Validate: `docs/superpowers/specs/2026-06-02-m0-governance-nested-agents-instruction-strategy-design.md`

## Tasks

### Task 1: Add The Structure Guard First

**Files:**
- Modify: `tests/workflows/repo/test_project_structure.py`
- Test: `tests/workflows/repo/test_project_structure.py`

- [ ] **Step 1: Register the nested instruction set and source spec**

  Add the spec to `SUPERPOWERS_SPEC_FILES`, and add exact nested instruction expectations near `AGENTS_BANNED_PHRASES`:

  ```python
  SUPERPOWERS_SPEC_FILES = {
      "PROJECT_CONTEXT.md",
      "specs/2026-05-23-m3-eos-explicit-association-closure-for-pcsaft.md",
      "specs/2026-05-26-m4-equilibrium-generalized-fluid-phase-equilibrium.md",
      "specs/2026-05-26-m4-equilibrium-stage-by-stage-implementation-plan.md",
      "specs/2026-05-27-m4-equilibrium-gfpe-package-cleanup-plan.md",
      "specs/2026-05-28-m1-packages-monorepo-package-migration.md",
      "specs/2026-05-29-m5-regression-regression-production-backlog.md",
      "specs/2026-05-29-m6-validation-validation-benchmark-backlog.md",
      "specs/2026-05-29-m7-release-release-downstream-backlog.md",
      "specs/2026-06-01-m4-equilibrium-move-equilibrium-objective-assembly-to-extension.md",
      "specs/2026-06-02-m0-governance-nested-agents-instruction-strategy-design.md",
  }
  EXPECTED_NESTED_AGENT_FILES = {
      "packages/epcsaft/AGENTS.md",
      "packages/epcsaft-equilibrium/AGENTS.md",
      "packages/epcsaft-regression/AGENTS.md",
      "analyses/AGENTS.md",
      "analyses/paper_validation/AGENTS.md",
  }
  EXPECTED_NESTED_AGENT_TOKENS = {
      "packages/epcsaft/AGENTS.md": (
          "core `epcsaft` provider package",
          "Do not add equilibrium route assembly",
          "Provider public derivatives must remain CppAD-backed",
          "provider SDK",
      ),
      "packages/epcsaft-equilibrium/AGENTS.md": (
          "`epcsaft-equilibrium`",
          "Ipopt NLPs",
          "pressure-transformed objective assembly",
          "Do not expose declared-not-exposed route families",
      ),
      "packages/epcsaft-regression/AGENTS.md": (
          "`epcsaft-regression`",
          "Ceres residual blocks",
          "Regression claims require native optimizer evidence",
      ),
      "analyses/AGENTS.md": (
          "source-controlled scientific analyses",
          "Separate data generation from rendering",
          "Do not place analysis scripts in root `scripts/`",
      ),
      "analyses/paper_validation/AGENTS.md": (
          "Paper-validation analyses",
          "figures/figure_NN/source/",
          "parameters/mixed/",
          "Do not add nested dataset-name folders",
      ),
  }
  ```

- [ ] **Step 2: Add the failing nested-AGENTS test**

  Add this test after `test_agents_md_stays_a_short_tracked_repo_router`:

  ```python
  def test_expected_nested_agents_files_are_present_and_scoped() -> None:
      missing = sorted(
          relpath for relpath in EXPECTED_NESTED_AGENT_FILES if not (REPO_ROOT / relpath).is_file()
      )
      assert missing == []

      allowed = {"AGENTS.md", *EXPECTED_NESTED_AGENT_FILES}
      actual = {
          path.relative_to(REPO_ROOT).as_posix()
          for path in REPO_ROOT.rglob("AGENTS.md")
          if ".git" not in path.parts
      }
      unexpected = sorted(actual - allowed)
      assert unexpected == []

      for relpath, tokens in EXPECTED_NESTED_AGENT_TOKENS.items():
          text = (REPO_ROOT / relpath).read_text(encoding="utf-8")
          missing_tokens = sorted(token for token in tokens if token not in text)
          assert missing_tokens == [], relpath
          assert not re.search(r"[A-Za-z]:\\Users\\Tanner", text)
          assert "docs/superpowers/PROJECT_CONTEXT.md" not in text
          assert "docs/agents/issue-tracker.md" not in text
  ```

- [ ] **Step 3: Run the structure test and verify the expected failure**

  Run:

  ```powershell
  uv run python run_pytest.py tests/workflows/repo/test_project_structure.py::test_expected_nested_agents_files_are_present_and_scoped -q
  ```

  Expected: FAIL with the five missing nested `AGENTS.md` files.

- [ ] **Step 4: Commit the red test**

  ```powershell
  git add tests/workflows/repo/test_project_structure.py
  git commit -m "test: guard nested agent instruction layout"
  ```

### Task 2: Add Package-Level Nested Instructions

**Files:**
- Create: `packages/epcsaft/AGENTS.md`
- Create: `packages/epcsaft-equilibrium/AGENTS.md`
- Create: `packages/epcsaft-regression/AGENTS.md`
- Test: `tests/workflows/repo/test_project_structure.py`

- [ ] **Step 1: Create the provider package instruction file**

  Write `packages/epcsaft/AGENTS.md`:

  ```markdown
  # Provider Package Instructions

  This subtree owns the core `epcsaft` provider package: `Mixture`, `State`,
  `ParameterSet`, `ModelOptions`, EOS/property evaluation, provider-native
  `_core`, CppAD derivative substrate, provider capability evidence, and the
  provider SDK.

  Do not add equilibrium route assembly, Ipopt ownership, Ceres optimizer logic,
  or regression workflow behavior here. If provider work appears to require
  those, split the issue by package and milestone.

  Provider public derivatives must remain CppAD-backed where public payloads
  claim derivative support. Missing derivative coverage is an implementation
  gap, not a runtime mode.

  Keep native SDK manifests, CMake source lists, pybind bindings, `.pyi`
  surfaces, and provider tests aligned when moving native or public-provider
  code.

  Focused validation:
  - `uv run python run_pytest.py --provider-api -q`
  - `uv run python run_pytest.py --native -q`
  - `uv run python scripts/dev/build_epcsaft.py --clean --profile provider`
  ```

- [ ] **Step 2: Create the equilibrium package instruction file**

  Write `packages/epcsaft-equilibrium/AGENTS.md`:

  ```markdown
  # Equilibrium Package Instructions

  This subtree owns `epcsaft-equilibrium`: `Equilibrium`, route specs, selector
  admission, native activation matrix consumption, GFPE assembly, Ipopt NLPs,
  route scaling, postsolve certification, equilibrium diagnostics, and
  equilibrium capability evidence.

  Provider EOS supplies thermodynamic state/property and local derivative data.
  Equilibrium owns pressure-transformed objective assembly, route residuals,
  Jacobians, Hessians, tensors, NLP contracts, and solver-status acceptance.

  Do not expose declared-not-exposed route families as callable production
  routes. Do not treat acceptable Ipopt statuses, iteration-limit seeds, or
  diagnostic staged workflows as completion evidence.

  Any broadened route claim must update activation/capability evidence and run a
  route-appropriate focused proof.

  Focused validation:
  - `uv run python run_pytest.py --equilibrium-api -q`
  - `uv run python run_pytest.py --native-contracts -q`
  - `uv run python run_pytest.py --equilibrium-debug -q -s packages/epcsaft-equilibrium/tests/api/test_equilibrium.py::test_equilibrium_bubble_pressure_uses_trusted_cppad_ipopt_route`
  ```

- [ ] **Step 3: Create the regression package instruction file**

  Write `packages/epcsaft-regression/AGENTS.md`:

  ```markdown
  # Regression Package Instructions

  This subtree owns `epcsaft-regression`: `Regression`, target datasets, target
  family summaries, Ceres residual blocks, parameter maps and bounds, optimizer
  diagnostics, regression result schemas, and regression capability evidence.

  Do not move regression optimizer loops, Ceres ownership, or regression result
  contracts into the provider package. Provider code may supply parameter
  payloads and CppAD derivative inputs only through provider-owned public
  contracts.

  Regression claims require native optimizer evidence, derivative evidence, and
  package-local tests. Dependency presence alone is not capability evidence.

  Focused validation:
  - `uv run python run_pytest.py --regression -q`
  - `uv run python scripts/dev/validate_project.py regression`
  ```

- [ ] **Step 4: Run the nested-AGENTS test**

  Run:

  ```powershell
  uv run python run_pytest.py tests/workflows/repo/test_project_structure.py::test_expected_nested_agents_files_are_present_and_scoped -q
  ```

  Expected: FAIL with only `analyses/AGENTS.md` and `analyses/paper_validation/AGENTS.md` missing.

- [ ] **Step 5: Commit package instructions**

  ```powershell
  git add packages/epcsaft/AGENTS.md packages/epcsaft-equilibrium/AGENTS.md packages/epcsaft-regression/AGENTS.md
  git commit -m "docs: add package agent instructions"
  ```

### Task 3: Add Analysis Nested Instructions

**Files:**
- Create: `analyses/AGENTS.md`
- Create: `analyses/paper_validation/AGENTS.md`
- Test: `tests/workflows/repo/test_project_structure.py`

- [ ] **Step 1: Create the analysis workflow instruction file**

  Write `analyses/AGENTS.md`:

  ```markdown
  # Analysis Workflow Instructions

  This subtree owns source-controlled scientific analyses, validation studies,
  and figure workflows. It is not package runtime code.

  Keep each analysis self-contained under `analyses/{category}/{short_id}/`.
  Use root `data/reference/` only for reusable stable inputs shared across
  analyses or package tests.

  Figure-owned layout is:
  `figures/{figure_id}/source/`, `figures/{figure_id}/scripts/`, and
  `figures/{figure_id}/results/`. Disposable run payloads go under
  `figures/{figure_id}/results/runs/`.

  Separate data generation from rendering. Retain exact plotted data snapshots
  beside rendered figures and `.mpl.yaml` sidecars.

  Do not place analysis scripts in root `scripts/`, package `src/`, or package
  tests. Do not turn downstream metrics into package APIs.
  ```

- [ ] **Step 2: Create the paper-validation instruction file**

  Write `analyses/paper_validation/AGENTS.md`:

  ```markdown
  # Paper Validation Instructions

  Paper-validation analyses are retained literature reproduction workflows and
  use the repo-specific exception layout from `docs/pages/project_structure.rst`.

  Use `figures/figure_NN/source/` for source assets and
  `figures/figure_NN/results/` for retained generated outputs. Use
  `tables/table_###/source/` for extracted paper tables and conversions.

  Parameter snapshots used to execute the analysis belong directly under
  `parameters/mixed/`, `parameters/pure/`, and `parameters/user_options.json`.
  Do not add nested dataset-name folders under `parameters/`.

  Keep paper source manifests, copied paper notes, plotted data snapshots, and
  rendered outputs traceable to the cited source. Application-specific
  conclusions remain analysis output, not package capability claims.
  ```

- [ ] **Step 3: Run the nested-AGENTS test**

  Run:

  ```powershell
  uv run python run_pytest.py tests/workflows/repo/test_project_structure.py::test_expected_nested_agents_files_are_present_and_scoped -q
  ```

  Expected: PASS.

- [ ] **Step 4: Commit analysis instructions**

  ```powershell
  git add analyses/AGENTS.md analyses/paper_validation/AGENTS.md tests/workflows/repo/test_project_structure.py
  git commit -m "docs: add analysis agent instructions"
  ```

### Task 4: Validate The Instruction Strategy

**Files:**
- Modify: none expected beyond files from Tasks 1-3
- Test: `tests/workflows/repo/test_project_structure.py`

- [ ] **Step 1: Confirm the tracked `AGENTS.md` set**

  Run:

  ```powershell
  rg --files -g AGENTS.md
  ```

  Expected output includes exactly:

  ```text
  AGENTS.md
  analyses/AGENTS.md
  analyses/paper_validation/AGENTS.md
  packages/epcsaft/AGENTS.md
  packages/epcsaft-equilibrium/AGENTS.md
  packages/epcsaft-regression/AGENTS.md
  ```

- [ ] **Step 2: Run the focused structure tests**

  Run:

  ```powershell
  uv run python run_pytest.py tests/workflows/repo/test_project_structure.py -q
  ```

  Expected: PASS.

- [ ] **Step 3: Run quick validation**

  Run:

  ```powershell
  uv run python scripts/dev/validate_project.py quick
  ```

  Expected: PASS.

- [ ] **Step 4: Run the cleanup hook**

  Run:

  ```powershell
  pwsh.exe -NoProfile -ExecutionPolicy Bypass -File "$env:USERPROFILE\.codex\hooks\codex-cleanup.ps1" -RepoRoot .
  ```

  Expected: no leftover processes owned by this repo task.

- [ ] **Step 5: Commit any final validation-only documentation adjustments**

  If validation finds wording drift in the nested instructions or structure test, commit only those scoped fixes:

  ```powershell
  git add AGENTS.md analyses packages tests/workflows/repo/test_project_structure.py docs/superpowers/plans/2026-06-02-m0-governance-nested-agents-instruction-strategy-plan.md
  git commit -m "docs: finalize nested agent instruction strategy"
  ```

## Proof Oracle

- `rg --files -g AGENTS.md`
- `uv run python run_pytest.py tests/workflows/repo/test_project_structure.py -q`
- `uv run python scripts/dev/validate_project.py quick`
- `pwsh.exe -NoProfile -ExecutionPolicy Bypass -File "$env:USERPROFILE\.codex\hooks\codex-cleanup.ps1" -RepoRoot .`

## Risk And Dependency Notes

- The main behavioral risk is duplicated or overly broad instructions. The nested file content is intentionally short and does not repeat root Git, issue-tracker, IntelliJ, cleanup, or full roadmap rules.
- The issue is AFK-ready because the spec fixes the file list and the plan gives exact content and validation commands.
- This is a governance and repo-structure task under `M0 - Governance`; it touches package folders only by adding instruction files.
