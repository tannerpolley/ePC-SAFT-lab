# Issue #189 Current Plan: Generalized Phase-Set Diagnostics And Boundary Queue

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> `superpowers:executing-plans` for a single-thread implementation or
> `superpowers:subagent-driven-development` only when the task is split into
> independent file-owned slices. Steps use checkbox (`- [ ]`) syntax for
> tracking.

**Goal:** Unblock GitHub issue #189 after #188 and #241 closed, keep #189 as the
M4 umbrella for boundary workflows plus generalized phase-set PE, and create the
first AFK implementation slice for neutral generalized phase-set diagnostics.

**Architecture:** #189 must not close from two-phase HELD reliability, source
backed LLE showcase evidence, or repeated two-phase route calls. It closes only
after boundary workflows are expressed as degree-of-freedom swaps over the
certified neutral GFPE path and generalized phase-set PE records selected and
rejected candidate phase sets for arbitrary neutral phase counts. The next
ready slice is diagnostic-first: make the internal neutral multiphase path emit
and validate complete phase-set records without making `neutral_multiphase_nonassoc`
a public route.

**Tech Stack:** Python, C++/pybind11, Ipopt-backed native equilibrium contracts,
pytest through `run_pytest.py`, GitHub Issues native dependency API, and local
Superpowers Project mirrors under `docs/superpowers`.

---

## Intake

- Source Spec: `docs/superpowers/specs/2026-05-30-m4-equilibrium-issue-0189-derive-boundary-workflows-and-generalized-phase-set-pe-from-neutral-gfpe.md`
- Source Issue: `docs/superpowers/issues/2026-05-30-m4-equilibrium-issue-0189-derive-boundary-workflows-and-generalized-phase-set-pe-from-neutral-gfpe.md`
- GitHub Issue: `https://github.com/ePC-SAFT/ePC-SAFT/issues/189`
- Milestone: `M4 - Equilibrium`
- Package: `packages/epcsaft-equilibrium`
- Backend: `Ipopt`
- Capability: `lle`
- Current dependency result: #188 and #241 are closed, so #189 has no open native blockers and should move from `status:blocked` to `status:ready`.
- Queue policy: #189 remains HITL umbrella/tracking scope; the first child issue is AFK.

## Current Completion State

- Done before this plan:
  - #148 added neutral phase discovery and postsolve certification foundations.
  - #187 hardened the shared NLP/Ipopt gate.
  - #241 promoted neutral HELD Stage II to replayable dual phase-discovery evidence.
  - #188 added source-backed neutral TP-flash GFPE evidence.
  - #247/#250 added neutral HELD reliability and the first source-backed neutral nonassociating LLE showcase.
- Still missing for #189:
  - Phase-set records are not yet a first-class generalized diagnostic schema for selected and rejected phase sets.
  - The internal neutral multiphase route is not yet checked by a retained generalized phase-set validation script.
  - Duplicate, collapsed, infeasible, uncertified, and lower-free-energy omitted phase sets are not yet all separated by a deterministic checker.
  - Boundary workflows are not yet derived as degree-of-freedom swaps over the same certified neutral GFPE path.
  - `PE-Generalized Multiphase` must remain `planned_not_public`.

## Acceptance Gates For The First Child Issue

- [ ] `neutral_multiphase_nonassoc` remains internal-only and absent from public route/capability surfaces.
- [ ] Internal neutral multiphase postsolve diagnostics expose complete phase-set records for at least one three-phase neutral state.
- [ ] Each selected or rejected phase-set record carries phase count, phase kinds or roles, source, phase amounts or fractions, volume or density evidence, composition, objective or TPD evidence, feasibility status, selected/rejected status, and rejection reason when rejected.
- [ ] A retained checker fails loudly when phase-set records are missing, malformed, infeasible, collapsed, duplicated, uncertified, or incomplete.
- [ ] Registry and milestone docs state that this is internal neutral multiphase diagnostic progress, not public generalized multiphase admission, associating LLLE admission, electrolyte admission, or reactive admission.

## Tasks

### Task 1: Refresh #189 Readiness And Split The Queue

**Use Cases:**

- When GitHub native dependencies show #188 and #241 closed, #189 is no longer dependency-blocked and should not keep `status:blocked`.
- When #189 still spans boundary workflows and generalized multiphase PE, it should remain the umbrella instead of becoming one oversized implementation PR.
- When an AFK worker starts from the new child issue, the worker should have a narrow proof oracle and no permission to broaden public route claims.

**Files:**

- `docs/superpowers/issues/2026-05-30-m4-equilibrium-issue-0189-derive-boundary-workflows-and-generalized-phase-set-pe-from-neutral-gfpe.md`
- `docs/superpowers/milestones/M4-equilibrium/README.md`
- `docs/superpowers/specs/2026-05-30-m4-equilibrium-issue-0189-derive-boundary-workflows-and-generalized-phase-set-pe-from-neutral-gfpe.md`

- [ ] Confirm `gh api /repos/ePC-SAFT/ePC-SAFT/issues/189/dependencies/blocked_by` returns only closed blockers.
- [ ] Edit GitHub #189 labels from `status:blocked` to `status:ready`.
- [ ] Refresh the local #189 mirror readiness to `ready`, keep `afk_hitl: "HITL"`, and record that #189 is an umbrella.
- [ ] Add the child issue to the M4 current-open issue table after creation.
- [ ] Add a GitHub #189 comment with the blocker evidence and the child issue link.

### Task 2: Add The Failing Generalized Phase-Set Diagnostic Contract

**Use Cases:**

- When the internal native neutral multiphase postsolve returns a three-phase result, tests should be able to inspect phase-set records without reconstructing them from parallel arrays.
- When a candidate is rejected because it is infeasible, duplicate, collapsed, or uncertified, the diagnostic contract should retain that reason.
- When a worker accidentally exposes `neutral_multiphase_nonassoc` publicly, the existing public capability test should fail.

**Files:**

- `packages/epcsaft-equilibrium/tests/native/diagnostics/test_internal_multiphase_activation_contracts.py`
- `packages/epcsaft-equilibrium/tests/contracts/test_activation_capabilities.py`
- `tests/native/contracts/test_generalized_phase_set_checker.py`
- `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/_native_core.pyi`

- [ ] Extend `test_internal_multiphase_activation_contracts.py` with assertions for a `phase_set_records` or equivalent first-class record list on the internal multiphase postsolve payload.
- [ ] Assert at least one three-phase accepted row includes selected phase count, selected phase kinds, phase amounts/fractions, volumes/densities, compositions, objective or TPD evidence, and source metadata.
- [ ] Assert rejected rows use explicit rejection statuses rather than missing values or generic failure text.
- [ ] Add a checker contract test that fails when a synthetic payload lacks any required field or reports public route exposure.
- [ ] Keep the public activation capability test requiring `neutral_multiphase_nonassoc` to stay absent from `public_routes`.

### Task 3: Implement Native And Python Diagnostic Payloads

**Use Cases:**

- When C++ postsolve copies discovery metadata, selected and rejected candidates should arrive in Python as coherent row records.
- When current code already has parallel arrays for candidates, the public Python layer should not force downstream checks to zip partially aligned arrays.
- When the generalized phase-set route has not met production evidence, route diagnostics should remain internal/provisional.

**Files:**

- `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/core/two_phase_eos_route.h`
- `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/core/two_phase_eos_route.cpp`
- `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/register_bindings.cpp`
- `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/results/route_result_bridge.h`
- `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/core/native_results.py`
- `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/equilibrium_activation.py`

- [ ] Add a native row structure or binding helper for generalized phase-set records using existing discovery/postsolve metadata.
- [ ] Populate selected rows from phase amounts, phase kinds, phase compositions, phase volumes/densities, and candidate source/rank data.
- [ ] Populate rejected rows from TPD candidate metadata with distinct statuses for infeasible, duplicate/collapsed, uncertified, and omitted-lower-objective cases when that evidence is available.
- [ ] Export the record list through pybind without weakening existing parallel-array diagnostics.
- [ ] Preserve current hard failures for size mismatches and invalid phase counts.
- [ ] Keep `neutral_multiphase_nonassoc` internal by avoiding capability or public workflow admission changes.

### Task 4: Add The Retained Checker And Registry Evidence

**Use Cases:**

- When a future PR claims #189 progress, there should be a single retained command that proves the generalized phase-set diagnostic record contract.
- When the checker sees only two-phase HELD reliability evidence, it should report that generalized phase-set evidence is still incomplete.
- When docs or registries mention `PE-Generalized Multiphase`, they should clearly distinguish internal diagnostics from public support.

**Files:**

- `scripts/validation/check_generalized_phase_set.py`
- `tests/native/contracts/test_generalized_phase_set_checker.py`
- `docs/superpowers/milestones/M4-equilibrium/registries/equilibrium-benchmark-registry.yaml`
- `docs/superpowers/milestones/M4-equilibrium/generalized-fluid-phase-equilibrium.md`
- `docs/superpowers/milestones/M4-equilibrium/README.md`

- [ ] Add `scripts/validation/check_generalized_phase_set.py` with `--json` and `--require-complete`.
- [ ] Make the checker report named blockers for missing records, missing selected rows, missing rejected rows, non-three-phase evidence, mass-balance infeasibility, collapsed/duplicate phase sets, uncertified phase sets, or public route exposure.
- [ ] Add contract tests for passing and failing checker payloads.
- [ ] Update the M4 registry row for `PE-Generalized Multiphase` only with internal diagnostic evidence and keep its status `planned_not_public`.
- [ ] Update the GFPE milestone doc to point at the checker and state what remains for boundary workflows and final generalized phase-set admission.

### Task 5: Validate, Comment, And Prepare The Next Slice

**Use Cases:**

- When the child issue PR closes, the result should advance #189 but not close #189 unless all umbrella gates are met.
- When the diagnostic slice passes, the next #189 slice should be obvious: boundary workflow degree-of-freedom swaps or stronger lower-free-energy omission tests.
- When dependent issues are blocked only by stale labels, the closeout should record whether they can be unblocked.

**Files:**

- `docs/superpowers/issues/*.md`
- `docs/superpowers/milestones/M4-equilibrium/README.md`
- `docs/agents/issue-tracker.md`

- [ ] Run the proof oracle below.
- [ ] Update the child issue with validation evidence and scope boundaries.
- [ ] Add a #189 progress comment that names the remaining umbrella gates.
- [ ] Do not close #189 unless boundary workflows, generalized phase-set records, rejection diagnostics, docs, and registry gates are all complete.
- [ ] Hand off the next issue recommendation: boundary workflow derived traces or complete rejected/lower-free-energy phase-set proof, depending on the child issue result.

## Proof Oracle

Run these commands from the repo root for the first child issue:

```powershell
uv run --no-sync python scripts/dev/build_epcsaft.py --profile equilibrium --build-only --parallel 4
uv run --no-sync python run_pytest.py packages/epcsaft-equilibrium/tests/native/diagnostics/test_internal_multiphase_activation_contracts.py -q
uv run --no-sync python run_pytest.py packages/epcsaft-equilibrium/tests/contracts/test_activation_capabilities.py tests/native/contracts/test_generalized_phase_set_checker.py -q
uv run --no-sync python scripts/validation/check_generalized_phase_set.py --json --require-complete
uv run --no-sync python scripts/dev/validate_project.py docs
pwsh.exe -NoProfile -ExecutionPolicy Bypass -File "$env:USERPROFILE\.codex\hooks\codex-cleanup.ps1" -RepoRoot .
```

## Issue Creation Packet

Create one AFK child issue from this plan.

**Title:** `M4: add neutral generalized phase-set diagnostics contract`

**Type:** `Feature`

**Milestone:** `M4 - Equilibrium`

**Labels:** `enhancement`, `native`, `solver`, `docs`, `validation`, `equilibrium`, `area:equilibrium`, `backend:ipopt`, `status:ready`, `agent-ready`, `type:feature`

**Body:**

```markdown
Implement the first AFK slice under #189: make the internal neutral generalized phase-set path expose and validate deterministic phase-set diagnostic records without public route admission.

Source plan:
docs/superpowers/plans/2026-05-30-m4-equilibrium-issue-0189-derive-boundary-workflows-and-generalized-phase-set-pe-from-neutral-gfpe-plan.md

Parent:
#189

Goal:
Add a retained diagnostic contract and checker for internal neutral multiphase phase-set records so #189 can advance from two-phase HELD/LLE evidence toward true generalized phase-set PE.

Acceptance:
- `neutral_multiphase_nonassoc` remains internal-only and absent from public route/capability surfaces.
- Internal neutral multiphase postsolve diagnostics expose complete phase-set records for at least one three-phase neutral state.
- Each selected or rejected record carries phase count, phase kind/role, source, phase amount or fraction, volume or density evidence, composition, objective or TPD evidence, feasibility status, selected/rejected status, and rejection reason when rejected.
- A retained checker fails on missing records, malformed rows, mass-balance infeasibility, collapsed or duplicate phases, uncertified phase sets, or accidental public route exposure.
- `PE-Generalized Multiphase` remains `planned_not_public`; docs and registry text must not claim public generalized multiphase, associating LLLE, electrolyte, or reactive support.

Non-goals:
- No public `neutral_multiphase_nonassoc` route exposure.
- No associating, electrolyte, reactive, CE, or CPE admission.
- No boundary workflow admission in this issue.
- No closure of #189 unless all umbrella gates are separately proven.

Proof oracle:
uv run --no-sync python scripts/dev/build_epcsaft.py --profile equilibrium --build-only --parallel 4
uv run --no-sync python run_pytest.py packages/epcsaft-equilibrium/tests/native/diagnostics/test_internal_multiphase_activation_contracts.py -q
uv run --no-sync python run_pytest.py packages/epcsaft-equilibrium/tests/contracts/test_activation_capabilities.py tests/native/contracts/test_generalized_phase_set_checker.py -q
uv run --no-sync python scripts/validation/check_generalized_phase_set.py --json --require-complete
uv run --no-sync python scripts/dev/validate_project.py docs
```
