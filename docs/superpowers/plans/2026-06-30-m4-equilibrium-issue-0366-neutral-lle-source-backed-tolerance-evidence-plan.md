# Neutral Nonassociating LLE Source-Backed Tolerance Evidence Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Resolve GitHub issue #366 by connecting the Matsuda/NIST neutral nonassociating LLE showcase to the shared phase-equilibrium certification contract and retained source-data tolerance margins.

**Architecture:** Keep the existing public `lle` route and Matsuda fixture. Extend the neutral LLE checker payload so accepted source-backed rows report the shared PE contract receipt and explicit pass/fail margins for source composition, phase fraction, residual, and phase-distance tolerances. The route equations, source parameters, and fitted binary interaction remain unchanged and provenance-tagged.

**Tech Stack:** Python validation checker, package-level pytest, native checker tests, M4 registry, Superpowers issue mirror workflow, GitHub issue #366.

---

## Intake

- GitHub Issue: `https://github.com/ePC-SAFT/ePC-SAFT/issues/366`
- Source Spec: `docs/superpowers/specs/2026-06-29-m4-phase-equilibrium-unified-certification-contract.md`
- Source Issue: `docs/superpowers/issues/366-m4-lle-integrate-neutral-nonassociating-source-backed-tolerance-evidence.md`
- Source Plan: `docs/superpowers/plans/2026-06-30-m4-equilibrium-issue-0366-neutral-lle-source-backed-tolerance-evidence-plan.md`
- Parent Issue: `https://github.com/ePC-SAFT/ePC-SAFT/issues/364`
- Milestone: `M4 - Equilibrium`
- Package owner: `packages/epcsaft-equilibrium`

## Outcome Proof

**Intent:** Connect source-backed neutral nonassociating LLE validation evidence to the shared phase-equilibrium certification contract.
**Current Behavior:** The Matsuda checker proves fixture completeness and source-row tolerances, but the accepted payload does not retain the shared `neutral_lle` certification contract fields or explicit tolerance-margin rows.
**Expected Outcome:** The checker returns `shared_certification.status == "accepted"`, empty shared-contract blockers, and accepted tolerance margins for source composition, phase fraction, material balance, pressure consistency, fugacity consistency, and phase distance.
**Target Output:** Package selector `-k "neutral and lle and source"` collects real tests and passes with shared certification and tolerance-margin assertions.
**Owner:** M4 equilibrium package owner.
**Interface:** `scripts/validation/check_neutral_lle_showcase.py`, package API showcase tests, native checker contract tests, M4 benchmark registry, #366 issue mirror, and GitHub issue #366.
**Cutover:** Add shared-contract and tolerance-margin fields to the checker output and enforce them in tests.
**Replaced Path:** Source-backed neutral LLE artifacts that prove route acceptance but do not prove the shared PE contract.
**Evidence:** Red/green focused tests, checker JSON completion, registry contract test, plan validators, docs validation, cleanup hook, GitHub issue update, and PR merge.
**Acceptance Proof:** Acceptance is proven when source-backed Matsuda rows retain provenance, fitted binary interaction status, shared `neutral_lle` certification fields, and declared tolerance margins with nonnegative margins.
**Stop Criteria:** Stop if retained source data or fitted-parameter provenance is missing.
**Avoid:** Do not change source parameters, refit inside the route-validation path, alter thermodynamic equations, add solver flags, broaden LLE claims, or count diagnostic-only success as production support.
**Risk:** The main risk is treating a complete showcase as shared-contract evidence without retaining the actual contract fields and tolerance margins. The fix must make both visible in the accepted checker payload.

## Implementation Boundaries

**Files To Create:** This plan only.
**Files To Modify:** `scripts/validation/check_neutral_lle_showcase.py`, `packages/epcsaft-equilibrium/tests/api/test_neutral_lle_showcase_fixture.py`, `tests/native/contracts/test_neutral_lle_showcase_checker.py`, `docs/superpowers/milestones/M4-equilibrium/registries/equilibrium-benchmark-registry.yaml`, `tests/native/contracts/test_equilibrium_benchmark_registry.py`, and `docs/superpowers/issues/366-m4-lle-integrate-neutral-nonassociating-source-backed-tolerance-evidence.md`.
**Files To Avoid:** EOS equation files, native solver code, source fixture parameter rows, M5 regression assets, associating LLE, electrolyte LLE, reactive routes, and release metadata.
**Source Of Truth:** Matsuda/NIST fixture under `data/reference/equilibrium_benchmarks/neutral_lle/perfluorohexane_hexane`, shared PE certification contract, and current public `Equilibrium(..., route="lle")` behavior.
**Read Path:** Read fixture metadata/thresholds, route postsolve diagnostics, `epcsaft_equilibrium.capabilities()["phase_equilibrium_certification"]`, and validator blockers from `validate_phase_equilibrium_certification_contracts`.
**Write Path:** Add checker fields, tests, registry acceptance checks, issue mirror plan/evidence, and GitHub issue body sync.
**Integration Points:** `evaluate_case_dir`, `_route_certification_blockers`, package API showcase test, native checker contract test, and `equilibrium-benchmark-registry.yaml`.
**Migration Or Cutover:** Additive checker payload fields only. Existing keys remain present.
**Replaced Path Handling:** Replace implicit source-backed completion with explicit `shared_certification` and `tolerance_margins` payloads.
**Acceptance Proof Gate:** Do not push or open a PR until the focused #366 selector, checker tests, registry test, docs validation, and cleanup hook pass.

## Decision Ledger

| Decision | Source | Answer | Impact | Deferred? | Risk owner |
| --- | --- | --- | --- | --- | --- |
| Scope owner | #366 mirror and M4 policy | Work is limited to neutral nonassociating LLE validation evidence in M4. | Avoids changing solver math or fitted parameters. | No | M4 owner |
| Shared contract source | #362 contract | Use `phase_equilibrium_certification` from package capabilities and validate it with the shared validator. | Proves the accepted Matsuda route connects to the same contract shape as other production routes. | No | M4 owner |
| Tolerance evidence | Matsuda fixture thresholds | Retain actual, threshold, margin, and status for each accepted tolerance. | Makes pass/fail margins auditable instead of prose-only. | No | M4 owner |
| Parameter provenance | Existing fixture | Keep `source_fitted` binary interaction visible; do not refit or hide parameters. | Satisfies #366 provenance requirement without M5 work. | No | M4 owner |
| Test complete | #366 proof oracle | Package selector must collect real tests; checker and registry tests guard the same fields. | Prevents a zero-test selector from satisfying the issue. | No | M4 owner |

## Test Complete Definition

Test complete for #366 means:

- `uv run --no-sync python -m pytest packages\epcsaft-equilibrium\tests -k "neutral and lle and source" -q` passes with real tests collected.
- `uv run --no-sync python -m pytest tests\native\contracts\test_neutral_lle_showcase_checker.py tests\native\contracts\test_equilibrium_benchmark_registry.py -q` passes.
- `uv run --no-sync python scripts\validation\check_neutral_lle_showcase.py --json --require-complete` reports `complete: true`, `shared_certification.status: accepted`, no shared blockers, and accepted tolerance margins.
- `uv run --no-sync python scripts\dev\validate_project.py docs` passes.

## Acceptance Criteria Mapping

- Source-backed neutral LLE rows retain data provenance and tolerance margins: Tasks 1, 2, and 3.
- Shared certification fields are present for accepted rows: Tasks 1 and 2.
- Fitted parameters remain explicitly provenance-tagged: Tasks 2 and 3.

## Non-Goals

- No M5 parameter regression.
- No source parameter refit.
- No EOS equation changes.
- No new LLE family admission.
- No associating, electrolyte, VLE, flash, boundary, or reactive route changes.
- No release claim.
- No downstream application metrics.

## Tasks

### Task 1: Add Red Contract Assertions

**Use Cases:**
- A maintainer needs the package selector to fail if the Matsuda checker omits shared PE certification fields.
- A validation reviewer needs explicit source tolerance margins, not only a boolean complete flag.
- A future route update must preserve source-fitted binary interaction provenance.
- The cutover must replace route-only completion evidence with shared-contract and tolerance-margin assertions.

**Files:**
- Modify: `packages/epcsaft-equilibrium/tests/api/test_neutral_lle_showcase_fixture.py`
- Modify: `tests/native/contracts/test_neutral_lle_showcase_checker.py`

- [x] **Step 1: Add package-level assertions for `shared_certification` and `tolerance_margins`.**
- [x] **Step 2: Add checker-contract assertions for the same payload fields.**
- [x] **Step 3: Run focused tests and confirm the missing-field failure.**

### Task 2: Emit Shared Certification And Tolerance Margins

**Use Cases:**
- Accepted source-backed rows should show the shared `neutral_lle` certification contract.
- Accepted tolerance rows should retain actual values, thresholds, margins, and statuses.
- Shared certification drift should block completion with named blockers.
- The replaced path where a complete showcase lacks shared certification fields must be impossible to accept.

**Files:**
- Modify: `scripts/validation/check_neutral_lle_showcase.py`

- [x] **Step 1: Build `shared_certification` from package capabilities.**
- [x] **Step 2: Add `tolerance_margins` from comparison and postsolve diagnostics.**
- [x] **Step 3: Treat shared-contract blockers as checker blockers.**
- [x] **Step 4: Re-run focused tests and checker JSON.**

### Task 3: Sync Registry, Mirror, And Proof

**Use Cases:**
- Registry readers need to see that Matsuda evidence includes shared certification and tolerance margins.
- The local and GitHub issue text must point at this executable implementation plan.
- Future maintainers need exact rerunnable commands.
- Acceptance evidence must show the cutover from isolated showcase proof to shared PE contract proof.

**Files:**
- Modify: `docs/superpowers/milestones/M4-equilibrium/registries/equilibrium-benchmark-registry.yaml`
- Modify: `tests/native/contracts/test_equilibrium_benchmark_registry.py`
- Modify: `docs/superpowers/issues/366-m4-lle-integrate-neutral-nonassociating-source-backed-tolerance-evidence.md`

- [x] **Step 1: Add registry acceptance checks for shared certification and tolerance margins.**
- [x] **Step 2: Validate the plan and docs.**
- [x] **Step 3: Sync local mirror and GitHub body with retained evidence.**

## Proof Oracle

```powershell
pwsh.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\validate-plan-task-use-cases.ps1 -PlanPath docs\superpowers\plans\2026-06-30-m4-equilibrium-issue-0366-neutral-lle-source-backed-tolerance-evidence-plan.md
pwsh.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\validate-plan-outcome-proof.ps1 -PlanPath docs\superpowers\plans\2026-06-30-m4-equilibrium-issue-0366-neutral-lle-source-backed-tolerance-evidence-plan.md
uv run --no-sync python -m pytest packages\epcsaft-equilibrium\tests -k "neutral and lle and source" -q
uv run --no-sync python -m pytest tests\native\contracts\test_neutral_lle_showcase_checker.py tests\native\contracts\test_equilibrium_benchmark_registry.py -q
uv run --no-sync python scripts\validation\check_neutral_lle_showcase.py --json --require-complete
uv run --no-sync python scripts\dev\validate_project.py docs
pwsh.exe -NoProfile -ExecutionPolicy Bypass -File "$env:USERPROFILE\.codex\hooks\codex-cleanup.ps1" -RepoRoot .
```
