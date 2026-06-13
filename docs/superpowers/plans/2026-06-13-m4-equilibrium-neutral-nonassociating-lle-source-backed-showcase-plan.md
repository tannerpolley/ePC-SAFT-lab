# M4 Neutral Nonassociating LLE Source-Backed Showcase Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add the first source-backed neutral nonassociating LLE fixture, checker, retained analysis, and M4 registry evidence for the current neutral `route="lle"` utility without broadening associating, electrolyte, reactive, CE, CPE, or generalized phase-set claims.

**Architecture:** Create a source-audited fixture under `data/reference/equilibrium_benchmarks/neutral_lle`, a fail-loud checker that proves fixture completeness and current-route acceptance, a retained two-step analysis under `analyses/package_validation/neutral_nonassociating_lle_showcase`, and milestone registry/docs updates that distinguish this showcase from synthetic HELD reliability and generalized GFPE admission.

**Tech Stack:** Python 3.13, `packages/epcsaft-equilibrium`, `epcsaft_equilibrium._native`, Ipopt, exact Hessian route diagnostics, pytest, CSV/JSON reference fixtures, Matplotlib retained-plot workflow, Superpowers Project issue mirrors.

---

## Source Evidence And Decisions

- Source spec: `docs/superpowers/specs/2026-06-11-m4-equilibrium-neutral-nonassociating-lle-source-backed-showcase.md`
- HELD adoption context: `docs/superpowers/specs/2026-06-11-m4-equilibrium-held-1-0-full-adoption.md`
- Current M4 index: `docs/superpowers/milestones/M4-equilibrium/README.md`
- Current benchmark registry: `docs/superpowers/milestones/M4-equilibrium/registries/equilibrium-benchmark-registry.yaml`
- Verified: current `main` exposes and tests a neutral nonassociating `lle` utility route with synthetic LLE proof and HELD Stage II/III diagnostics.
- Verified: current M4 registry has source-backed neutral TP flash and electrolyte LLE entries, but no source-backed neutral nonassociating LLE fixture entry.
- Verified: #247 retained synthetic neutral LLE reliability evidence; that evidence is algorithm reliability, not source-backed public LLE benchmark evidence.
- Inference: the next closest ready M4 issue should be one source-backed neutral nonassociating LLE showcase because it closes the public-evidence gap without touching association, electrolyte, reactive, or generalized phase-count behavior.
- Verified source decision: Matsuda et al. ThermoML perfluorohexane + hexane rows provide the source LLE branch pair, and Tihic PC-SAFT-compatible sPC-SAFT rows/correlations provide the pure-parameter basis. The current-route binary interaction is source-fitted and retained as such.
- Unknown until Task 1: exact binary, PC-SAFT parameter rows, binary interaction values, source uncertainties, and final source-derived composition tolerance.

## What Counts As Test Complete

The issue is complete only when all of these are true:

- The fixture source audit records DOI or URL, source data rows, source model family, species order, pure parameters, binary interactions, phase labels, and why the selected binary is neutral, nonelectrolyte, nonreactive, and nonassociating.
- The checker rejects the fixture when source rows, source notes, parameters, binary interactions, feed rows, tolerances, HELD evidence, exact Hessian evidence, or route diagnostics are missing.
- The checker rejects any fixture that activates association, electrolyte, reactive, salting-out, SLE, CE, or CPE fields.
- The current `route="lle"` path accepts the source-backed fixture with exact Hessian support and fresh native receipt fields.
- Route diagnostics satisfy material balance, pressure consistency, fugacity or chemical-potential consistency, phase distance, candidate completeness, and two-liquid phase selection.
- HELD Stage II reports replayable dual-loop evidence and Stage III reports Ipopt refinement that consumed the Stage II replay seed.
- Retained CSV/JSON data under the analysis folder exactly drive the rendered PNG/SVG figures.
- The M4 registry and docs state this is neutral nonassociating LLE showcase evidence only.

## Non-Goals

- No associating LLE admission.
- No electrolyte LLE admission.
- No reactive LLE admission.
- No salting-out, SLE, precipitation, CE, or CPE claims.
- No generalized arbitrary phase-count or LLLE production claim.
- No public route broadening beyond the current neutral `route="lle"` utility.
- No use of methanol/cyclohexane, water/alcohol, electrolyte LLE, or Pereira 2012 SAFT-VR systems as the source-backed neutral nonassociating fixture.

## File Map

- Create: `data/reference/equilibrium_benchmarks/neutral_lle/matsuda_2011_pfhexane_hexane/source_notes.md`
- Create: `data/reference/equilibrium_benchmarks/neutral_lle/matsuda_2011_pfhexane_hexane/metadata.json`
- Create: `data/reference/equilibrium_benchmarks/neutral_lle/matsuda_2011_pfhexane_hexane/pure_component_parameters.csv`
- Create: `data/reference/equilibrium_benchmarks/neutral_lle/matsuda_2011_pfhexane_hexane/binary_interactions.csv`
- Create: `data/reference/equilibrium_benchmarks/neutral_lle/matsuda_2011_pfhexane_hexane/experimental_tielines.csv`
- Create: `data/reference/equilibrium_benchmarks/neutral_lle/matsuda_2011_pfhexane_hexane/feed_compositions.csv`
- Create: `data/reference/equilibrium_benchmarks/neutral_lle/matsuda_2011_pfhexane_hexane/thresholds.json`
- Create: `scripts/validation/check_neutral_lle_showcase.py`
- Create: `tests/native/contracts/test_neutral_lle_showcase_checker.py`
- Create: `packages/epcsaft-equilibrium/tests/api/test_neutral_lle_showcase_fixture.py`
- Create: `analyses/package_validation/neutral_nonassociating_lle_showcase/README.md`
- Create: `analyses/package_validation/neutral_nonassociating_lle_showcase/analysis.yaml`
- Create: `analyses/package_validation/neutral_nonassociating_lle_showcase/scripts/generate_data.py`
- Create: `analyses/package_validation/neutral_nonassociating_lle_showcase/scripts/render_figures.py`
- Generate: `analyses/package_validation/neutral_nonassociating_lle_showcase/shared/results/neutral_lle_showcase_check.json`
- Generate: `analyses/package_validation/neutral_nonassociating_lle_showcase/shared/results/run_summary.json`
- Generate: `analyses/package_validation/neutral_nonassociating_lle_showcase/shared/results/neutral_lle_phase_points.csv`
- Generate: `analyses/package_validation/neutral_nonassociating_lle_showcase/shared/results/neutral_lle_tolerance_summary.csv`
- Generate: `analyses/package_validation/neutral_nonassociating_lle_showcase/figures/neutral_lle_binodal_showcase/results/neutral_lle_binodal_showcase.png`
- Generate: `analyses/package_validation/neutral_nonassociating_lle_showcase/figures/neutral_lle_binodal_showcase/results/neutral_lle_binodal_showcase.svg`
- Generate: `analyses/package_validation/neutral_nonassociating_lle_showcase/figures/neutral_lle_binodal_showcase/results/neutral_lle_binodal_showcase.mpl.yaml`
- Generate: `analyses/package_validation/neutral_nonassociating_lle_showcase/figures/neutral_lle_tolerance_margins/results/neutral_lle_tolerance_margins.png`
- Generate: `analyses/package_validation/neutral_nonassociating_lle_showcase/figures/neutral_lle_tolerance_margins/results/neutral_lle_tolerance_margins.svg`
- Generate: `analyses/package_validation/neutral_nonassociating_lle_showcase/figures/neutral_lle_tolerance_margins/results/neutral_lle_tolerance_margins.mpl.yaml`
- Generate: `analyses/package_validation/neutral_nonassociating_lle_showcase/figures/neutral_lle_held_stage_status/results/neutral_lle_held_stage_status.png`
- Modify: `docs/superpowers/milestones/M4-equilibrium/registries/equilibrium-benchmark-registry.yaml`
- Modify: `docs/superpowers/milestones/M4-equilibrium/README.md`
- Modify: `docs/superpowers/specs/2026-06-11-m4-equilibrium-held-1-0-full-adoption.md`

### Task 1: Audit Source And Select One Neutral Nonassociating LLE Tie-Line

**Use Cases:**
- A worker must prove the selected fixture is source-backed neutral nonassociating LLE, not an associating, electrolyte, reactive, or synthetic substitute.
- If the selected Matsuda/Tihic source chain cannot supply compatible data and PC-SAFT-compatible parameters, the issue must stop with a retained rejection note instead of manufacturing a benchmark.
- Future workers need to see the exact source row, species order, parameter provenance, binary interaction provenance, and tolerance decision.

**Files:**
- Create: `data/reference/equilibrium_benchmarks/neutral_lle/matsuda_2011_pfhexane_hexane/source_notes.md`
- Create: `data/reference/equilibrium_benchmarks/neutral_lle/matsuda_2011_pfhexane_hexane/metadata.json`
- Create: `data/reference/equilibrium_benchmarks/neutral_lle/matsuda_2011_pfhexane_hexane/pure_component_parameters.csv`
- Create: `data/reference/equilibrium_benchmarks/neutral_lle/matsuda_2011_pfhexane_hexane/binary_interactions.csv`
- Create: `data/reference/equilibrium_benchmarks/neutral_lle/matsuda_2011_pfhexane_hexane/experimental_tielines.csv`
- Create: `data/reference/equilibrium_benchmarks/neutral_lle/matsuda_2011_pfhexane_hexane/feed_compositions.csv`
- Create: `data/reference/equilibrium_benchmarks/neutral_lle/matsuda_2011_pfhexane_hexane/thresholds.json`
- Test: `tests/native/contracts/test_neutral_lle_showcase_checker.py`

- [x] Write a failing fixture-completeness test that imports `scripts.validation.check_neutral_lle_showcase` and asserts the candidate fixture is complete.
- [x] Audit Matsuda ThermoML rows for one binary branch-pair with temperature, pressure, and both liquid compositions.
- [x] Audit Tihic PC-SAFT-compatible parameter rows/correlations and record the source-fitted binary interaction decision.
- [x] Select the simplest source-compatible binary: perfluorohexane + n-hexane.
- [x] Record explicit rejection rules for methanol/cyclohexane, water/alcohol, electrolyte LLE, Pereira 2012 SAFT-VR, and synthetic A/B evidence.
- [x] Set `thresholds.json` using source uncertainty where available and documented route-fit residual limits where source composition uncertainty is absent.
- [x] Run the focused test and verify it fails before the checker exists:

  ```powershell
  uv run --no-sync python run_pytest.py tests/native/contracts/test_neutral_lle_showcase_checker.py -q
  ```

### Task 2: Implement The Neutral LLE Fixture Checker

**Use Cases:**
- A ready issue needs one command that proves fixture completeness and route acceptance.
- Missing source evidence, missing parameters, or forbidden physics terms must produce named blockers.
- The checker must report enough diagnostics for M4 to distinguish source-backed LLE from synthetic HELD reliability.

**Files:**
- Create: `scripts/validation/check_neutral_lle_showcase.py`
- Modify: `tests/native/contracts/test_neutral_lle_showcase_checker.py`
- Test: `tests/native/contracts/test_neutral_lle_showcase_checker.py`

- [x] Implement `evaluate_case_dir(case_dir: Path) -> dict[str, object]`.
- [x] Require `source_notes.md`, `metadata.json`, `pure_component_parameters.csv`, `binary_interactions.csv`, `experimental_tielines.csv`, `feed_compositions.csv`, and `thresholds.json`.
- [x] Require metadata fields for `case_label`, `family_label`, `route`, `species`, `source_paths`, `source_model_family`, source status, expected phase count, and route scope.
- [x] Reject association, electrolyte, and reactive activation fields with named blockers.
- [x] Build a native neutral LLE mixture from the fixture parameters and binary interactions.
- [x] Run the current native selector route for `neutral_lle` and capture diagnostics.
- [x] Require exact Hessian support, Ipopt success, `solve_succeeded`, selected candidate count `2`, phase distance at least `1.0e-6`, material balance at most `1.0e-8`, pressure consistency at most `1.0e-3`, and fugacity consistency at most `1.0e-6` unless `thresholds.json` tightens those limits.
- [x] Require HELD Stage II replayable dual-loop evidence and Stage III replay-consumption evidence.
- [x] Return JSON with `complete`, `status`, `blockers`, `fixture`, `route`, `comparison`, and `native_freshness_receipt`.
- [x] Run:

  ```powershell
  uv run --no-sync python run_pytest.py tests/native/contracts/test_neutral_lle_showcase_checker.py -q
  uv run --no-sync python scripts/validation/check_neutral_lle_showcase.py --case-dir data/reference/equilibrium_benchmarks/neutral_lle/matsuda_2011_pfhexane_hexane --json --require-complete
  ```

### Task 3: Add Package-Level Source-Backed LLE Route Test

**Use Cases:**
- Package tests must prove the current `lle` utility can solve the source-backed case, not just synthetic A/B mechanics.
- The test must keep exact Hessian, HELD Stage II, Stage III, and postsolve certification tied to the source fixture.
- A regression in public route wiring must fail before the retained analysis scripts produce misleading figures.

**Files:**
- Create: `packages/epcsaft-equilibrium/tests/api/test_neutral_lle_showcase_fixture.py`
- Modify: `scripts/validation/check_neutral_lle_showcase.py`
- Test: `packages/epcsaft-equilibrium/tests/api/test_neutral_lle_showcase_fixture.py`

- [x] Add a focused pytest file that loads the fixture through the public API.
- [x] Assert the public route solves the selected source-backed case.
- [x] Assert route status, solver status, application status, exact Hessian support, Stage II replay evidence, Stage III replay consumption, selected candidate count, phase distance, material balance, pressure consistency, and fugacity consistency.
- [x] Assert the matched solved liquid compositions are within the final recorded source-derived tolerance.
- [x] Run:

  ```powershell
  uv run --no-sync python run_pytest.py packages/epcsaft-equilibrium/tests/api/test_neutral_lle_showcase_fixture.py -q
  ```

### Task 4: Build Retained Data And Figures

**Use Cases:**
- Reviewers need retained CSV/JSON data that exactly matches the source-backed showcase figures.
- The figure must make the source tie-line, solved liquid phases, feed, and diagnostic margins inspectable.
- The visual evidence must not imply associating, electrolyte, reactive, CE, CPE, or generalized production admission.

**Files:**
- Create: `analyses/package_validation/neutral_nonassociating_lle_showcase/README.md`
- Create: `analyses/package_validation/neutral_nonassociating_lle_showcase/analysis.yaml`
- Create: `analyses/package_validation/neutral_nonassociating_lle_showcase/scripts/generate_data.py`
- Create: `analyses/package_validation/neutral_nonassociating_lle_showcase/scripts/render_figures.py`
- Generate: `analyses/package_validation/neutral_nonassociating_lle_showcase/shared/results/neutral_lle_showcase_check.json`
- Generate: `analyses/package_validation/neutral_nonassociating_lle_showcase/shared/results/run_summary.json`
- Generate: `analyses/package_validation/neutral_nonassociating_lle_showcase/shared/results/neutral_lle_phase_points.csv`
- Generate: `analyses/package_validation/neutral_nonassociating_lle_showcase/shared/results/neutral_lle_tolerance_summary.csv`
- Generate: figure PNG/SVG/CSV/`.mpl.yaml` outputs under `analyses/package_validation/neutral_nonassociating_lle_showcase/figures/*/results/`
- Test: `analyses/package_validation/neutral_nonassociating_lle_showcase/scripts/generate_data.py`
- Test: `analyses/package_validation/neutral_nonassociating_lle_showcase/scripts/render_figures.py`

- [x] Implement `generate_data.py` so it calls the checker, writes the summary JSON, writes phase-point rows, and writes diagnostic margin rows.
- [x] Implement `render_figures.py` so it reads retained data only and writes PNG, SVG, plot-input CSV, and `.mpl.yaml` sidecars.
- [x] Include a binodal-style composition figure with source liquid phases, solved liquid phases, and feed.
- [x] Include a diagnostic-margin figure for composition, material balance, pressure, fugacity, and phase distance, plus a HELD-stage status figure for Stage II and Stage III evidence.
- [x] Add README text stating the analysis is neutral nonassociating LLE showcase evidence only.
- [x] Run:

  ```powershell
  uv run --no-sync python analyses/package_validation/neutral_nonassociating_lle_showcase/scripts/generate_data.py
  uv run --no-sync python analyses/package_validation/neutral_nonassociating_lle_showcase/scripts/render_figures.py
  ```

### Task 5: Update M4 Registry And Adoption Docs

**Use Cases:**
- M4 needs a registry row that separates source-backed neutral LLE from source-backed neutral TP flash and electrolyte LLE.
- HELD 1.0 adoption status must show that this is public source-backed neutral LLE evidence, while #189 still owns generalized phase-set completion.
- Future issue routing must see the new issue as ready and the blocked generalized/associating/electrolyte issues as still blocked by their distinct gates.

**Files:**
- Modify: `docs/superpowers/milestones/M4-equilibrium/registries/equilibrium-benchmark-registry.yaml`
- Modify: `docs/superpowers/milestones/M4-equilibrium/README.md`
- Modify: `docs/superpowers/specs/2026-06-11-m4-equilibrium-held-1-0-full-adoption.md`
- Test: `scripts/dev/validate_project.py`

- [x] Add a registry reference case for source-backed neutral nonassociating LLE.
- [x] Add a reference entry for the selected Matsuda/Tihic-backed fixture with evidence tier, source path, status, route, retained evidence, and acceptance checks.
- [x] Update M4 README with retained evidence and queue guard context.
- [x] Update the HELD 1.0 full-adoption spec to state that source-backed neutral nonassociating LLE showcase evidence is present after #250.
- [x] Preserve the Queue Guard statement that #189, #190, and #191 remain blocked by their own proof gates.
- [x] Run:

  ```powershell
  uv run --no-sync python scripts/dev/validate_project.py docs
  ```

### Task 6: Run Full Proof And Close The Issue Cleanly

**Use Cases:**
- The final PR must be mergeable without depending on unstated local files.
- Reviewers need one ordered proof oracle that starts from a fresh native build and ends with docs validation.
- The issue mirror, GitHub issue, and milestone index must agree before resolution starts.

**Files:**
- Modify: `docs/superpowers/issues/<issue-number>-add-source-backed-neutral-nonassociating-lle-showcase-fixture.md`
- Modify: `docs/superpowers/milestones/M4-equilibrium/README.md`
- Test: full proof oracle below

- [x] Run the full proof oracle in order.
- [x] Review `git status --short` and ensure generated retained artifacts are intentionally tracked or intentionally excluded by existing policy.
- [x] Run the repo cleanup hook.
- [x] Commit the issue implementation on its feature branch and open a PR.
- [x] Do not close the GitHub issue until the PR is merged.

## Proof Oracle

Run the proof in this order:

```powershell
uv run --no-sync python scripts/dev/build_epcsaft.py --profile equilibrium --build-only --parallel 4
uv run --no-sync python run_pytest.py tests/native/contracts/test_neutral_lle_showcase_checker.py -q
uv run --no-sync python run_pytest.py packages/epcsaft-equilibrium/tests/api/test_neutral_lle_showcase_fixture.py -q
uv run --no-sync python scripts/validation/check_neutral_lle_showcase.py --case-dir data/reference/equilibrium_benchmarks/neutral_lle/matsuda_2011_pfhexane_hexane --json --require-complete
uv run --no-sync python analyses/package_validation/neutral_nonassociating_lle_showcase/scripts/generate_data.py
uv run --no-sync python analyses/package_validation/neutral_nonassociating_lle_showcase/scripts/render_figures.py
uv run --no-sync python scripts/dev/validate_project.py docs
pwsh.exe -NoProfile -ExecutionPolicy Bypass -File "$env:USERPROFILE\.codex\hooks\codex-cleanup.ps1" -RepoRoot .
```

## Issue Creation Packet

Published M4 issue from this plan:

- https://github.com/ePC-SAFT/ePC-SAFT/issues/250
- Local mirror: deleted during post-merge closeout after PR #251 closed issue #250.

```text
Title: M4: add source-backed neutral nonassociating LLE showcase fixture
Milestone: M4 - Equilibrium
Type: Feature
Package: equilibrium
Backend: Ipopt
Readiness: ready
Classification: AFK
Blocked by: None
```

Suggested labels:

```text
enhancement, native, solver, docs, validation, equilibrium, area:equilibrium, backend:ipopt, status:ready, agent-ready, type:feature
```

Goal command:

```text
/goal Resolve M4 issue: add the first source-backed neutral nonassociating LLE fixture, checker, retained analysis, and registry evidence for the current neutral route="lle" utility, without broadening associating, electrolyte, reactive, CE, CPE, or generalized phase-set claims.
```

Acceptance:

- `data/reference/equilibrium_benchmarks/neutral_lle/<source_slug>/` contains source notes, metadata, pure parameters, binary interactions, feed rows, experimental tie-lines, and thresholds.
- `scripts/validation/check_neutral_lle_showcase.py --json --require-complete` proves fixture completeness, route acceptance, exact Hessian support, HELD Stage II replay, HELD Stage III replay consumption, material balance, pressure consistency, fugacity consistency, phase distance, and candidate completeness.
- Package-level tests prove the source-backed fixture through the current `route="lle"` utility.
- `analyses/package_validation/neutral_nonassociating_lle_showcase/` writes retained JSON/CSV data and renders PNG/SVG figures from retained data only.
- M4 registry and docs state this is neutral nonassociating LLE showcase evidence only.

## Risk Notes

- The largest uncertainty was source/parameter parity. The selected Matsuda/Tihic case is retained with an explicit source-fitted binary interaction rather than claiming imported literature `kij` parity.
- A single source-backed tie-line is public showcase evidence, not a broad LLE validation campaign.
- Exact Hessian and HELD Stage II/III diagnostics must come from fresh native code; stale native artifacts cannot support this issue.
- Tolerances must be source-justified. Do not loosen composition tolerances to hide a route or parameter mismatch.
