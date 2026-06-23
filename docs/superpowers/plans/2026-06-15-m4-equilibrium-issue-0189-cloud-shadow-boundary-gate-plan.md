# Cloud/Shadow Boundary Gate Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add the next #189 AFK child gate that proves cloud/shadow boundary data readiness from the retained neutral nonassociating LLE fixture while keeping native cloud/shadow route admission closed until real solver evidence exists.

**Architecture:** Extend the existing derived-boundary checker instead of adding a second boundary doctrine. The gate reads the Matsuda/NIST perfluorohexane + hexane LLE fixture, verifies cloud-point/binodal rows and one paired cloud-shadow source pair, emits machine-readable route-admission blockers, and keeps cloud/shadow as derived subworkflows with no runtime routes.

**Tech Stack:** Python, pytest through `run_pytest.py`, `scripts/validation/check_boundary_workflows.py`, `scripts/validation/check_neutral_lle_showcase.py`, CSV/JSON fixture validation, M4 Superpowers Project docs, GitHub issue mirrors.

---

## Intake

- Direct planning approval: user selected the #189 child planning path and chose `Cloud/Shadow Gate` with `Retained Gate` as test-complete.
- Source spec: `docs/superpowers/specs/2026-05-30-m4-equilibrium-issue-0189-derive-boundary-workflows-and-generalized-phase-set-pe-from-neutral-gfpe.md`
- Source issue mirror: `docs/superpowers/issues/2026-05-30-m4-equilibrium-issue-0189-derive-boundary-workflows-and-generalized-phase-set-pe-from-neutral-gfpe.md`
- Parent GitHub issue: `https://github.com/ePC-SAFT/ePC-SAFT/issues/189`
- Prior child results: #252 closed internal neutral generalized phase-set diagnostics; #256 closed retained bubble/dew boundary traces.
- Milestone: `M4 - Equilibrium`
- Package owner: `packages/epcsaft-equilibrium`
- Capability: `lle`
- Backend: `Ipopt`
- Candidate child title: `M4: add retained cloud/shadow boundary data gate`

## Verified Planning Facts

- Verified: `scripts/validation/check_boundary_workflows.py` already reports bubble, dew, cloud, and shadow as derived boundary workflows.
- Verified: current bubble/dew routes have retained `boundary_trace` evidence after #256; cloud/shadow rows still have `current_runtime_routes: []` and `current_convergence_status: planned_not_executable`.
- Verified: `data/reference/equilibrium_benchmarks/neutral_lle/perfluorohexane_hexane/source_binodal_points.csv` contains 14 source-backed `cloud_point` rows for perfluorohexane + hexane at 101.3 kPa, with temperatures from 285.09 K to 296.26 K and perfluorohexane mole fractions from 0.1498 to 0.7000.
- Verified: `experimental_tielines.csv` records one paired source branch at 293.895 K and 101.3 kPa with liquid compositions `[0.2000, 0.8000]` and `[0.5497, 0.4503]`; the branch temperature gap is 0.01 K against a 0.2 K source threshold.
- Verified: `metadata.json` marks the fixture neutral, nonelectrolyte, nonreactive, nonassociating, source-backed, and scoped to the current public `lle` utility route only.
- Verified: `docs/superpowers/milestones/M4-equilibrium/generalized-fluid-phase-equilibrium.md` says cloud/shadow are derived boundary workflows after the neutral TP-flash proof and must not invent synthetic VLLE validation fixtures.
- Inference: the closest #189 child is a retained source-data gate for cloud/shadow readiness, not native cloud/shadow route solving.

## Acceptance Criteria

- [ ] `check_boundary_workflows.py` exposes a retained cloud/shadow gate that can run without native cloud/shadow route solves.
- [ ] The gate verifies the Matsuda/NIST cloud-point data contract: exactly 14 current retained binodal rows, `method == "cloud_point"`, species order `perfluorohexane, hexane`, pressure 101.3 kPa, finite temperatures in 285.09-296.26 K, and perfluorohexane mole fractions in 0.1498-0.7000.
- [ ] The gate verifies one paired cloud-shadow source pair from `experimental_tielines.csv`: two liquid branch compositions on the simplex, pressure 101300 Pa, temperature 293.895 K, source row pair, branch temperature gap no larger than 0.2 K, and phase distance greater than the fixture threshold.
- [ ] The gate emits explicit native route-admission blockers for missing cloud and shadow executable routes while still allowing the retained source-data gate to complete.
- [ ] Cloud/shadow registry rows keep `current_runtime_routes: []` and `current_convergence_status: planned_not_executable`; no public route or capability text claims native cloud/shadow support.
- [ ] Existing bubble/dew boundary trace checks and neutral LLE showcase checks remain green.
- [ ] #189 remains open after this child unless generalized phase-set completion and final public capability admission are separately proven.

## Non-Goals

- No native cloud-point or shadow-point route implementation.
- No public `cloud_point`, `shadow_point`, `neutral_multiphase_nonassoc`, LLLE, VLLE, associating, electrolyte, reactive, CE, or CPE route admission.
- No Pereira 2012 System III ePC-SAFT validation promotion; that paper remains HELD/SAFT-VR context until model parity or a source-backed ePC-SAFT reparameterization exists.
- No synthetic LLE or VLLE fixture creation.
- No closure of #189 from this gate alone.
- No compatibility wrapper, legacy route alias, or silent default for missing source rows.

## Test-Complete Definition And Metrics

This child is test-complete only when the retained gate proves source-data readiness and still blocks native route admission.

- `uv run --no-sync python scripts/validation/check_boundary_workflows.py --json --cloud-shadow-gate --require-cloud-shadow-gate` exits zero and returns `complete: true` for the cloud/shadow source-data gate.
- The checker output includes `binodal_point_count == 14`, `paired_cloud_shadow_count == 1`, pressure 101.3 kPa or 101300 Pa as appropriate, `temperature_range_K == [285.09, 296.26]`, and `composition_range_x1 == [0.1498, 0.7000]`.
- The checker output includes route-admission blockers for native cloud and shadow route absence, but those blockers are separated from source-data gate blockers so reviewers cannot confuse source-data readiness with route completion.
- Any missing fixture file, malformed composition, wrong method, wrong species order, wrong pressure unit, invalid source status, forbidden association/electrolyte/reaction activation, or missing paired branch row makes the gate fail with a named blocker.
- `scripts/validation/check_neutral_lle_showcase.py --case-dir data/reference/equilibrium_benchmarks/neutral_lle/perfluorohexane_hexane --json --require-complete` remains green.
- Existing `tests/native/contracts/test_boundary_workflow_checker.py` remains green; cloud/shadow gate tests prove no regression in the #256 boundary trace evaluator.

## File Map

- Modify: `scripts/validation/check_boundary_workflows.py`
- Create: `tests/native/contracts/test_cloud_shadow_boundary_gate_checker.py`
- Modify: `tests/native/contracts/test_boundary_workflow_checker.py` if shared fixture helpers are needed.
- Modify: `tests/native/contracts/test_generalized_equilibrium_registry.py`
- Modify: `docs/superpowers/milestones/M4-equilibrium/registries/equilibrium-benchmark-registry.yaml`
- Modify: `docs/superpowers/milestones/M4-equilibrium/generalized-fluid-phase-equilibrium.md`
- Modify: `docs/superpowers/milestones/M4-equilibrium/README.md`
- Modify: `docs/superpowers/issues/2026-05-30-m4-equilibrium-issue-0189-derive-boundary-workflows-and-generalized-phase-set-pe-from-neutral-gfpe.md`
- Create after issue creation: `docs/superpowers/issues/<yyyy-mm-dd>-m4-equilibrium-issue-<number>-retained-cloud-shadow-boundary-data-gate.md`

## Tasks

### Task 1: Preflight And Child Issue Setup

**Use Cases:**
- A worker needs a narrow AFK issue because #189 is a HITL umbrella with completed #252 and #256 children.
- A reviewer needs the child to state that it creates a retained data gate, not native cloud/shadow route support.
- The local mirror and M4 index need to preserve parent-child context before implementation starts.

**Files:**
- Modify: `docs/superpowers/milestones/M4-equilibrium/README.md`
- Modify: `docs/superpowers/issues/2026-05-30-m4-equilibrium-issue-0189-derive-boundary-workflows-and-generalized-phase-set-pe-from-neutral-gfpe.md`
- Create: `docs/superpowers/issues/<yyyy-mm-dd>-m4-equilibrium-issue-<number>-retained-cloud-shadow-boundary-data-gate.md`

- [ ] Confirm `git status --short --branch` is clean and on a `codex/` branch or a Codex app worktree branch before implementation.
- [ ] Create one GitHub child issue from the Issue Creation Packet below.
- [ ] Assign milestone `M4 - Equilibrium`, labels from the packet, and a native dependency or comment link tying it to #189.
- [ ] Create the local issue mirror using the actual issue number and exact GitHub URL.
- [ ] Update the #189 mirror to say this child owns cloud/shadow source-data gating only.
- [ ] Commit the issue mirror and M4 index changes before code changes.

### Task 2: Add Failing Cloud/Shadow Gate Contract Tests

**Use Cases:**
- A retained gate should pass when the Matsuda/NIST fixture has the expected cloud/binodal rows and paired branch evidence.
- A retained gate should fail when source rows are missing, species order changes, the method is not `cloud_point`, pressure units are malformed, or branch compositions do not sum to one.
- A retained gate should fail if native cloud/shadow routes are accidentally marked executable without route evidence.

**Files:**
- Create: `tests/native/contracts/test_cloud_shadow_boundary_gate_checker.py`
- Modify: `tests/native/contracts/test_boundary_workflow_checker.py` if reusable boundary payload helpers should be shared.
- Test: `scripts/validation/check_boundary_workflows.py`

- [ ] Add a test importing `scripts.validation.check_boundary_workflows as checker`.
- [ ] Add a passing synthetic fixture test for `evaluate_cloud_shadow_gate(case_dir=CASE_DIR)` using the current Matsuda fixture.
- [ ] Add tests that copy fixture rows into temporary directories and assert named blockers for missing `source_binodal_points.csv`, fewer than 14 rows, wrong species order, wrong `method`, nonfinite temperature, nonpositive pressure, invalid mole fraction, and missing paired branch row.
- [ ] Add a test that rejects a cloud/shadow workflow contract if `routes` is nonempty while the checker cannot cite native route evidence.
- [ ] Run:

  ```powershell
  uv run --no-sync python run_pytest.py tests/native/contracts/test_cloud_shadow_boundary_gate_checker.py -q
  ```

- [ ] Confirm the new tests fail before implementing the checker gate.
- [ ] Commit the red tests.

### Task 3: Implement The Retained Cloud/Shadow Source-Data Gate

**Use Cases:**
- A reviewer needs one JSON command that proves cloud/shadow source-data readiness without executing an unavailable native route.
- A future native route worker needs explicit route-admission blockers and source-data metrics to know what remains before route support can be claimed.
- A docs worker needs the checker output to distinguish completed retained evidence from remaining native solver work.

**Files:**
- Modify: `scripts/validation/check_boundary_workflows.py`
- Test: `tests/native/contracts/test_cloud_shadow_boundary_gate_checker.py`

- [ ] Add `DEFAULT_CLOUD_SHADOW_CASE_DIR = REPO_ROOT / "data" / "reference" / "equilibrium_benchmarks" / "neutral_lle" / "perfluorohexane_hexane"`.
- [ ] Add CSV/JSON readers local to the checker or reuse existing simple reader patterns from `check_neutral_lle_showcase.py`.
- [ ] Add `evaluate_cloud_shadow_gate(case_dir: Path = DEFAULT_CLOUD_SHADOW_CASE_DIR) -> dict[str, Any]`.
- [ ] Validate fixture metadata fields: source-backed status, species list, route `lle`, selector route `neutral_lle`, expected two liquid phases, and all forbidden physics flags false.
- [ ] Validate `source_binodal_points.csv` rows and report `binodal_point_count`, pressure in kPa, temperature range in K, composition range for component 1, method set, and source dataset names.
- [ ] Validate `experimental_tielines.csv` and report `paired_cloud_shadow_count`, paired branch compositions, phase distance, pressure in Pa, branch temperature gap, source row pair, and threshold used.
- [ ] Return separated lists named `source_data_blockers` and `route_admission_blockers`; source-data blockers control `complete`, route-admission blockers document why public/native cloud/shadow remains closed.
- [ ] Add CLI flags `--cloud-shadow-gate` and `--require-cloud-shadow-gate`; when requested, include `cloud_shadow_gate` in the JSON payload and fail nonzero only for source-data blockers.
- [ ] Keep `--contracts-only` cheap and non-executable; it may list cloud/shadow planned contracts but must not run the source-data gate unless `--cloud-shadow-gate` is supplied.
- [ ] Run:

  ```powershell
  uv run --no-sync python run_pytest.py tests/native/contracts/test_cloud_shadow_boundary_gate_checker.py -q
  uv run --no-sync python scripts/validation/check_boundary_workflows.py --json --cloud-shadow-gate --require-cloud-shadow-gate
  ```

- [ ] Commit the checker implementation.

### Task 4: Preserve Boundary And LLE Regression Evidence

**Use Cases:**
- Existing #256 bubble/dew boundary traces should stay valid after the checker gains cloud/shadow source-data logic.
- Existing neutral LLE showcase evidence should stay valid because the cloud/shadow gate consumes that fixture instead of redefining it.
- If native cloud/shadow solving is attempted during this child, validation should stop and require a separate route-admission issue.

**Files:**
- Modify: `tests/native/contracts/test_boundary_workflow_checker.py` only if needed for shared assertions.
- Modify: `scripts/validation/check_boundary_workflows.py`
- Test: `tests/native/contracts/test_boundary_workflow_checker.py`
- Test: `scripts/validation/check_neutral_lle_showcase.py`

- [ ] Run the existing boundary trace contract tests:

  ```powershell
  uv run --no-sync python run_pytest.py tests/native/contracts/test_boundary_workflow_checker.py -q
  ```

- [ ] Run the cheap boundary contract checker:

  ```powershell
  uv run --no-sync python scripts/validation/check_boundary_workflows.py --json --contracts-only
  ```

- [ ] Run the source-backed neutral LLE showcase checker:

  ```powershell
  uv run --no-sync python scripts/validation/check_neutral_lle_showcase.py --case-dir data/reference/equilibrium_benchmarks/neutral_lle/perfluorohexane_hexane --json --require-complete
  ```

- [ ] If implementation changes native files or public route names, stop this child and split a new native route-admission issue before continuing.
- [ ] Commit any regression-test or checker repair needed to keep these commands green.

### Task 5: Update Registry, GFPE Doctrine, And Milestone Evidence

**Use Cases:**
- The M4 registry should show cloud/shadow have source-data gate evidence but no executable native routes.
- The GFPE doctrine should tell future workers that cloud/shadow data readiness is retained and route solving remains a separate gate.
- The milestone README should make the next #189 progress visible without implying #189 is closed.

**Files:**
- Modify: `docs/superpowers/milestones/M4-equilibrium/registries/equilibrium-benchmark-registry.yaml`
- Modify: `docs/superpowers/milestones/M4-equilibrium/generalized-fluid-phase-equilibrium.md`
- Modify: `docs/superpowers/milestones/M4-equilibrium/README.md`
- Modify: `docs/superpowers/issues/2026-05-30-m4-equilibrium-issue-0189-derive-boundary-workflows-and-generalized-phase-set-pe-from-neutral-gfpe.md`
- Modify: `docs/superpowers/issues/<yyyy-mm-dd>-m4-equilibrium-issue-<number>-retained-cloud-shadow-boundary-data-gate.md`
- Test: `tests/native/contracts/test_generalized_equilibrium_registry.py`

- [ ] Add registry acceptance checks such as `source_backed_cloud_binodal_rows`, `source_backed_cloud_shadow_pair`, and `native_route_admission_blockers_declared`.
- [ ] Keep cloud/shadow `current_runtime_routes: []` and `current_convergence_status: planned_not_executable`.
- [ ] Add or update registry tests to require those source-data checks while forbidding runtime route claims.
- [ ] Update GFPE derived-boundary text with the exact cloud/shadow gate command and what it proves.
- [ ] Update the M4 README retained evidence section with the gate command after implementation.
- [ ] Update #189 mirror progress notes: #252 internal phase-set diagnostics closed, #256 bubble/dew trace closed, this child cloud/shadow data gate closed if validation passes, generalized phase-set completion and public admission remain open.
- [ ] Run:

  ```powershell
  uv run --no-sync python run_pytest.py tests/native/contracts/test_generalized_equilibrium_registry.py -q
  uv run --no-sync python scripts/dev/validate_project.py docs
  ```

- [ ] Commit docs, registry, and mirror updates.

### Task 6: Closeout, Proof Oracle, And Parent Issue Progress

**Use Cases:**
- A PR reviewer needs one proof oracle covering source-data gate completion, no public route broadening, and retained prior evidence.
- A tracker reviewer needs the child issue closed only when the retained gate passes, while #189 remains open for remaining umbrella gates.
- If a validation command fails because source data or native receipts are stale, closeout should preserve the named blocker instead of weakening acceptance.

**Files:**
- Modify: `docs/superpowers/issues/<yyyy-mm-dd>-m4-equilibrium-issue-<number>-retained-cloud-shadow-boundary-data-gate.md`
- Modify: `docs/superpowers/issues/2026-05-30-m4-equilibrium-issue-0189-derive-boundary-workflows-and-generalized-phase-set-pe-from-neutral-gfpe.md`
- Modify: `docs/superpowers/milestones/M4-equilibrium/README.md`

- [ ] Run the Proof Oracle below from the repo root.
- [ ] Capture the cloud/shadow gate JSON summary in the PR or issue comment: source fixture path, 14 binodal rows, one paired branch row, source-data blockers empty, route-admission blockers present.
- [ ] Verify no public route list, docs claim, or registry row exposes native cloud/shadow route support.
- [ ] Close only the new child issue when every acceptance criterion passes.
- [ ] Add a #189 progress comment naming remaining work: generalized phase-set completion, native cloud/shadow route admission if desired, and final public capability admission.
- [ ] Run the repo cleanup hook.
- [ ] Commit post-merge mirror cleanup if the merge workflow updates local tracker files.

## Proof Oracle

Run these commands from the repo root:

```powershell
uv run --no-sync python run_pytest.py tests/native/contracts/test_cloud_shadow_boundary_gate_checker.py tests/native/contracts/test_boundary_workflow_checker.py tests/native/contracts/test_generalized_equilibrium_registry.py -q
uv run --no-sync python scripts/validation/check_boundary_workflows.py --json --contracts-only
uv run --no-sync python scripts/validation/check_boundary_workflows.py --json --cloud-shadow-gate --require-cloud-shadow-gate
uv run --no-sync python scripts/validation/check_neutral_lle_showcase.py --case-dir data/reference/equilibrium_benchmarks/neutral_lle/perfluorohexane_hexane --json --require-complete
uv run --no-sync python scripts/dev/validate_project.py docs
pwsh.exe -NoProfile -ExecutionPolicy Bypass -File "$env:USERPROFILE\.codex\hooks\codex-cleanup.ps1" -RepoRoot .
```

Run this current-route regression check before merging if `scripts/validation/check_boundary_workflows.py` route-point evaluation changes beyond the cloud/shadow source-data gate:

```powershell
uv run --no-sync python scripts/validation/check_boundary_workflows.py --json --run-current-boundary-route --allow-route-sweep --route-point-count 1 --require-complete
```

## Issue Creation Packet

Create one AFK child issue from this plan.

Title:

`M4: add retained cloud/shadow boundary data gate`

Body:

```markdown
## Summary

Add the next #189 child gate for cloud/shadow derived-boundary readiness. This issue proves retained source-data readiness from the Matsuda/NIST perfluorohexane + hexane neutral LLE fixture and keeps native cloud/shadow route admission closed until a separate solver route gate exists.

## Parent

- Parent issue: #189
- Source plan: `docs/superpowers/plans/2026-06-15-m4-equilibrium-issue-0189-cloud-shadow-boundary-gate-plan.md`
- Prior children: #252 internal generalized phase-set diagnostics; #256 bubble/dew boundary traces.

## Acceptance Criteria

- [ ] `check_boundary_workflows.py --json --cloud-shadow-gate --require-cloud-shadow-gate` completes the retained source-data gate.
- [ ] The gate verifies 14 Matsuda/NIST cloud-point rows and one paired cloud-shadow source branch for perfluorohexane + hexane.
- [ ] The gate emits separate route-admission blockers for native cloud and shadow route absence.
- [ ] Cloud/shadow registry rows keep no runtime routes and do not claim native route support.
- [ ] Existing bubble/dew boundary trace and neutral LLE showcase checks remain green.
- [ ] #189 remains open after this child unless every umbrella gate is separately complete.

## Proof Oracle

```powershell
uv run --no-sync python run_pytest.py tests/native/contracts/test_cloud_shadow_boundary_gate_checker.py tests/native/contracts/test_boundary_workflow_checker.py tests/native/contracts/test_generalized_equilibrium_registry.py -q
uv run --no-sync python scripts/validation/check_boundary_workflows.py --json --contracts-only
uv run --no-sync python scripts/validation/check_boundary_workflows.py --json --cloud-shadow-gate --require-cloud-shadow-gate
uv run --no-sync python scripts/validation/check_neutral_lle_showcase.py --case-dir data/reference/equilibrium_benchmarks/neutral_lle/perfluorohexane_hexane --json --require-complete
uv run --no-sync python scripts/dev/validate_project.py docs
pwsh.exe -NoProfile -ExecutionPolicy Bypass -File "$env:USERPROFILE\.codex\hooks\codex-cleanup.ps1" -RepoRoot .
```

## Non-Goals

- No native cloud or shadow route implementation.
- No public route admission.
- No associating, electrolyte, reactive, CE, CPE, LLLE, or VLLE admission.
- No closure of #189 from this child alone.
```

Labels:

`enhancement`, `native`, `solver`, `docs`, `validation`, `equilibrium`, `area:equilibrium`, `backend:ipopt`, `status:ready`, `agent-ready`, `type:feature`

Milestone:

`M4 - Equilibrium`

## Risk Notes

- Risk: the name "cloud/shadow gate" can be misread as native route completion. Mitigation: every artifact must separate `source_data_blockers` from `route_admission_blockers`, and docs must keep runtime routes empty.
- Risk: the current Matsuda/NIST fixture has source-backed cloud rows and one paired branch, not a broad cloud/shadow validation campaign. Mitigation: metrics explicitly say 14 retained rows and one paired source branch.
- Risk: future workers may try to close #189 after this child. Mitigation: #189 mirror and M4 README must continue naming generalized phase-set completion and public capability admission as remaining gates.
