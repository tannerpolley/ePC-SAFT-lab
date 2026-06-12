# Fresh-Native HELD/GFPE Validation Receipts Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Resolve #246 by adding fresh-native receipts to HELD and GFPE validation artifacts so stale native extensions cannot produce false Stage II/III evidence.

**Architecture:** Add a shared Python receipt helper for validation scripts, carry the receipt through the phase-discovery and neutral TP-flash fixture checkers, and retain the same receipt in issue 188 analysis outputs before plots can render Stage II/III claims. The implementation is a validation-evidence guard only; it does not change HELD algorithms, public routes, or family capability exposure.

**Tech Stack:** Python validation scripts, native extension import metadata, Git commit metadata, retained JSON/CSV analysis artifacts, Matplotlib figure rendering, pytest, Sphinx docs validation.

---

## Source Links

- Source Spec: `docs/superpowers/specs/2026-06-11-m4-equilibrium-held-1-0-fresh-native-proof-gate.md`
- Source Issue: `docs/superpowers/issues/2026-06-12-m4-equilibrium-issue-0246-add-fresh-native-receipts-to-held-and-gfpe-validation-artifacts.md`
- GitHub Issue: `https://github.com/ePC-SAFT/ePC-SAFT/issues/246`
- Milestone: `M4 - Equilibrium`
- Package: `packages/epcsaft-equilibrium`

## Scope

This is a validation-evidence guard. It makes existing HELD/GFPE proof scripts
and retained analysis artifacts record or reject native freshness before they
claim Stage II/III completion.

## What Counts As Test Complete

- `check_phase_discovery.py --json --include-route-refinement --require-complete` emits a `native_freshness_receipt` object with commit, native module path, checker command, and build-refresh command or freshness proof.
- `check_neutral_tp_flash_fixture.py --generate-phase-discovery --json --require-complete` emits the same receipt shape.
- Issue 188 retained analysis JSON/CSV rows include the receipt fields used to render the HELD stage plot.
- Plot rendering refuses Stage II/III verified text when retained status rows or native freshness receipts are missing.
- Docs explain that closed PRs are evidence only after the local native extension has been rebuilt or proven current.

## Non-Goals

- No new HELD algorithm work.
- No associating, electrolyte, reactive, CE, or CPE admission.
- No source-backed neutral LLE benchmark.
- No public capability promotion beyond the receipt-backed evidence already proven by #241 and #188.

### Task 1: Add A Reusable Native Freshness Receipt

**Use Cases:**
- A developer runs the phase-discovery checker after merging native C++ changes and needs the retained JSON to show which commit and native extension were used.
- A stale local `.pyd` is accidentally imported after a merge; the validation path must avoid silently producing milestone evidence that looks current.
- A checker run without `--require-complete` should still work as a diagnostic, while a milestone proof run must include the receipt.

**Files:**
- Create: `scripts/validation/native_freshness.py`
- Modify: `scripts/validation/check_phase_discovery.py`
- Modify: `scripts/validation/check_neutral_tp_flash_fixture.py`
- Test: `tests/native/contracts/test_native_freshness_receipt.py`

- [ ] **Step 1: Write failing receipt helper tests**

  Create `tests/native/contracts/test_native_freshness_receipt.py` with tests that import `scripts.validation.native_freshness` and require:

  - `build_receipt(checker_command=[...])` returns `git_commit`, `native_module_path`, `checker_command`, and `build_refresh_command`.
  - `require_receipt(receipt)` raises `ValueError` when `git_commit` or `native_module_path` is empty.
  - `receipt_to_jsonable(receipt)` returns only strings, booleans, numbers, lists, dictionaries, or null values.

- [ ] **Step 2: Run tests and verify expected failure**

  ```powershell
  uv run --no-sync python run_pytest.py tests/native/contracts/test_native_freshness_receipt.py -q
  ```

  Expected result before implementation: import failure for `scripts.validation.native_freshness`.

- [ ] **Step 3: Implement the receipt helper**

  Add `scripts/validation/native_freshness.py` with:

  - `git_commit()` using `git rev-parse HEAD`
  - `native_module_path(native_module)` using `Path(native_module.__file__).resolve()`
  - `build_receipt(native_module, checker_command)`
  - `require_receipt(receipt)`
  - `receipt_to_jsonable(receipt)`

  The default `build_refresh_command` must be:

  ```text
  uv run --no-sync python scripts/dev/build_epcsaft.py --profile equilibrium --build-only --parallel 4
  ```

- [ ] **Step 4: Attach receipts to checker payloads**

  In both validation checkers, add a top-level `native_freshness_receipt` field when JSON is emitted. When `--require-complete` is set, fail with exit code `2` if the receipt lacks commit or native module path.

- [ ] **Step 5: Run focused tests**

  ```powershell
  uv run --no-sync python run_pytest.py tests/native/contracts/test_native_freshness_receipt.py -q
  uv run --no-sync python scripts/validation/check_phase_discovery.py --json --include-route-refinement --require-complete
  uv run --no-sync python scripts/validation/check_neutral_tp_flash_fixture.py --generate-phase-discovery --json --require-complete
  ```

- [ ] **Step 6: Commit**

  ```powershell
  git add scripts/validation/native_freshness.py scripts/validation/check_phase_discovery.py scripts/validation/check_neutral_tp_flash_fixture.py tests/native/contracts/test_native_freshness_receipt.py
  git commit -m "Add native freshness receipts"
  ```

### Task 2: Carry Receipts Into Retained HELD/GFPE Analysis Evidence

**Use Cases:**
- The issue 188 analysis regenerates the HELD status plot and the CSV rows must prove they came from the fresh native extension.
- A future plot renderer sees stale or missing Stage II/III receipt data and must refuse stale explanatory text instead of rendering an outdated claim.
- A reviewer can trace the plotted Stage II/III status back to the checker command and native module path used to create it.

**Files:**
- Modify: `analyses/package_validation/issue_0188_neutral_tp_flash/scripts/generate_data.py`
- Modify: `analyses/package_validation/issue_0188_neutral_tp_flash/scripts/render_figures.py`
- Modify: `analyses/package_validation/issue_0188_neutral_tp_flash/shared/results/**`
- Test: `analyses/package_validation/issue_0188_neutral_tp_flash/scripts/generate_data.py`
- Test: `analyses/package_validation/issue_0188_neutral_tp_flash/scripts/render_figures.py`

- [ ] **Step 1: Inspect retained analysis schema**

  Read the issue 188 generate and render scripts and identify the JSON/CSV fields that carry HELD stage status into the figure.

- [ ] **Step 2: Add failing retained-data assertions**

  Add assertions in the data-generation path so retained rows require `native_git_commit`, `native_module_path`, `native_build_refresh_command`, and `native_checker_command` before Stage II or Stage III can be rendered as verified.

- [ ] **Step 3: Generate receipt-backed retained data**

  Extend the issue 188 data generator to copy the checker receipt fields into retained JSON/CSV outputs. Regenerate retained outputs from the current native extension.

- [ ] **Step 4: Refuse stale plot text**

  Update the figure renderer so Stage II/III verified labels require both verified stage rows and non-empty native receipt fields.

- [ ] **Step 5: Run analysis scripts**

  ```powershell
  uv run --no-sync python analyses/package_validation/issue_0188_neutral_tp_flash/scripts/generate_data.py
  uv run --no-sync python analyses/package_validation/issue_0188_neutral_tp_flash/scripts/render_figures.py
  ```

- [ ] **Step 6: Commit**

  ```powershell
  git add analyses/package_validation/issue_0188_neutral_tp_flash
  git commit -m "Carry native receipts into HELD analysis evidence"
  ```

### Task 3: Document The Completion Rule And Validate The Gate

**Use Cases:**
- A future agent asks why closed PRs were not enough; the docs should point to the native freshness receipt as the actual completion evidence.
- The M4 queue needs a focused proof oracle that can be run before merge without broad equilibrium sweeps.
- The #247 reliability issue can depend on #246 without inheriting stale-native ambiguity.

**Files:**
- Modify: `docs/superpowers/specs/2026-06-11-m4-equilibrium-held-1-0-fresh-native-proof-gate.md`
- Modify: `docs/superpowers/milestones/M4-equilibrium/generalized-fluid-phase-equilibrium.md`
- Modify: `docs/superpowers/milestones/M4-equilibrium/README.md`
- Modify: `docs/pages/development_workflows.rst`

- [ ] **Step 1: Update docs**

  Add or update text saying closed PRs are evidence only after the local native extension has been rebuilt or proven current by a retained receipt.

- [ ] **Step 2: Update M4 queue notes**

  Ensure #247 remains blocked until #246's fresh-native receipt work is complete.

- [ ] **Step 3: Run proof oracle**

  ```powershell
  uv run --no-sync python scripts/dev/build_epcsaft.py --profile equilibrium --build-only --parallel 4
  uv run --no-sync python scripts/validation/check_phase_discovery.py --json --include-route-refinement --require-complete
  uv run --no-sync python scripts/validation/check_neutral_tp_flash_fixture.py --generate-phase-discovery --json --require-complete
  uv run --no-sync python run_pytest.py packages/epcsaft-equilibrium/tests/native/results/test_neutral_lle_reference_values.py::test_stage9_phase_discovery_ladder_reports_distinct_layers -q
  uv run --no-sync python scripts/dev/validate_project.py docs
  ```

- [ ] **Step 4: Run cleanup and commit**

  ```powershell
  pwsh.exe -NoProfile -ExecutionPolicy Bypass -File "$env:USERPROFILE\.codex\hooks\codex-cleanup.ps1" -RepoRoot .
  git add docs/superpowers/specs/2026-06-11-m4-equilibrium-held-1-0-fresh-native-proof-gate.md docs/superpowers/milestones/M4-equilibrium/generalized-fluid-phase-equilibrium.md docs/superpowers/milestones/M4-equilibrium/README.md docs/pages/development_workflows.rst
  git commit -m "Document native freshness completion rule"
  ```

## Proof Oracle

```powershell
uv run --no-sync python scripts/dev/build_epcsaft.py --profile equilibrium --build-only --parallel 4
uv run --no-sync python run_pytest.py tests/native/contracts/test_native_freshness_receipt.py -q
uv run --no-sync python scripts/validation/check_phase_discovery.py --json --include-route-refinement --require-complete
uv run --no-sync python scripts/validation/check_neutral_tp_flash_fixture.py --generate-phase-discovery --json --require-complete
uv run --no-sync python run_pytest.py packages/epcsaft-equilibrium/tests/native/results/test_neutral_lle_reference_values.py::test_stage9_phase_discovery_ladder_reports_distinct_layers -q
uv run --no-sync python analyses/package_validation/issue_0188_neutral_tp_flash/scripts/generate_data.py
uv run --no-sync python analyses/package_validation/issue_0188_neutral_tp_flash/scripts/render_figures.py
uv run --no-sync python scripts/dev/validate_project.py docs
```
