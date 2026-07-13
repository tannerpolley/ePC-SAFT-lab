# Gross 2002 Associating LLE Tolerance Evidence Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Resolve GitHub issue #369 by connecting accepted Gross/Sadowski 2002 associating LLE evidence to the shared phase-equilibrium certification contract and retained source-data tolerance margins.

**Architecture:** Keep the existing public `lle` route and Gross 2002 retained artifacts. Extend the Gross association acceptance checker so accepted Figure 8 and Figure 10 rows report the shared PE contract receipt, request-specific associating proof quantities, exact association derivative receipts, source-score margins, and literature-overlay gaps as non-M4 regression follow-up data. Do not change route equations, parameters, source artifacts, or M5 regression scope.

**Tech Stack:** Python validation checker, package-level pytest, native checker tests, M4 registry, Superpowers issue mirror workflow, GitHub issue #369.

---

## Intake

- GitHub Issue: `https://github.com/ePC-SAFT/ePC-SAFT/issues/369`
- Source Spec: `docs/superpowers/specs/2026-06-29-m4-phase-equilibrium-unified-certification-contract.md`
- Source Issue: `docs/superpowers/issues/2026-06-30-m4-equilibrium-issue-0369-integrate-gross-2002-associating-lle-tolerance-evidence.md`
- Source Plan: `docs/superpowers/plans/2026-06-30-m4-equilibrium-issue-0369-gross-2002-associating-lle-tolerance-evidence-plan.md`
- Parent Issue: `https://github.com/ePC-SAFT/ePC-SAFT/issues/367`
- Milestone: `M4 - Equilibrium`
- Package owner: `packages/epcsaft-equilibrium`

## Outcome Proof

**Intent:** Connect Gross 2002 associating LLE/VLLE validation evidence to the shared phase-equilibrium certification contract.
**Current Behavior:** The Gross association acceptance checker proves campaign completion and exact association Hessians, but the package selector for #369 collects zero tests and the checker does not retain shared-contract fields or explicit source-margin rows.
**Expected Outcome:** The checker returns `shared_certification.status == "accepted"`, empty shared-contract blockers, accepted source margins for Figure 8 and Figure 10, retained exact association derivative receipts, and visible literature-overlay gaps marked outside M4 route acceptance.
**Target Output:** Package selector `-k "associating and lle and certification"` collects real tests and passes with shared certification, source-margin, and overlay-separation assertions.
**Owner:** M4 equilibrium package owner.
**Interface:** `scripts/validation/check_gross_2002_association_acceptance.py`, package API tests, native checker contract tests, M4 benchmark registry, #369 issue mirror, and GitHub issue #369.
**Cutover:** Add shared-contract and source-margin fields to the checker output and enforce them in tests.
**Replaced Path:** Gross associating paper-validation evidence that proves campaign completion but does not prove the shared PE contract or source tolerance margins.
**Evidence:** Red/green focused tests, checker JSON completion, registry contract test, plan validators, docs validation, cleanup hook, GitHub issue update, and PR merge.
**Acceptance Proof:** Acceptance is proven when Gross Figure 8 and Figure 10 rows retain source-point, plot-score, branch-coverage, mass-action residual, exact-derivative, shared `neutral_lle` certification, and regression-follow-up overlay diagnostics.
**Stop Criteria:** Stop if source-backed tolerance cannot pass without M5 parameter regression.
**Avoid:** Do not tune parameters inside M4 validation, hide out-of-tolerance overlay gaps, broaden associating surfaces beyond the retained Gross proof rows, or count diagnostic-only success as production support.
**Risk:** The main risk is treating campaign completion as shared-contract evidence without retaining the actual PE contract and source margin fields. The fix must make both visible in the accepted checker payload.

## Implementation Boundaries

**Files To Create:** This plan and `packages/epcsaft-equilibrium/tests/api/test_associating_lle_gross_2002_certification.py`.
**Files To Modify:** `scripts/validation/check_gross_2002_association_acceptance.py`, `tests/native/contracts/test_gross_2002_association_acceptance_checker.py`, `docs/superpowers/milestones/M6-validation/registries/equilibrium-evidence-registry.yaml`, `tests/native/contracts/test_equilibrium_benchmark_registry.py`, and `docs/superpowers/issues/2026-06-30-m4-equilibrium-issue-0369-integrate-gross-2002-associating-lle-tolerance-evidence.md`.
**Files To Avoid:** EOS equation files, native solver code, Gross source artifacts, retained parameter rows, M5 regression assets, electrolyte LLE, reactive routes, and release metadata.
**Source Of Truth:** Gross 2002 retained campaign artifacts under `analyses/paper_validation/2002_gross`, the methanol/cyclohexane fixture under `data/reference/equilibrium_benchmarks/associating_lle/methanol_cyclohexane`, and shared PE certification capabilities.
**Read Path:** Read retained fit-stat CSV rows, association Hessian diagnostics, package `phase_equilibrium_certification`, and validator blockers from `validate_phase_equilibrium_certification_contracts`.
**Write Path:** Add checker fields, package tests, native checker tests, registry acceptance checks, issue mirror plan/evidence, and GitHub issue body sync.
**Integration Points:** `evaluate_payload`, `evaluate_campaign`, package selector tests, native checker contract tests, and `equilibrium-evidence-registry.yaml`.
**Migration Or Cutover:** Additive checker payload fields only. Existing keys remain present.
**Replaced Path Handling:** Replace implicit Gross campaign completion with explicit `shared_certification`, `source_tolerance_margins`, and non-acceptance `literature_overlay` diagnostics.
**Acceptance Proof Gate:** Do not push or open a PR until the focused #369 selector, checker tests, registry test, docs validation, and cleanup hook pass.

## Decision Ledger

| Decision | Source | Answer | Impact | Deferred? | Risk owner |
| --- | --- | --- | --- | --- | --- |
| Scope owner | #369 mirror and M4 policy | Work is limited to associating LLE validation evidence in M4. | Avoids changing solver math or fitted parameters. | No | M4 owner |
| Shared contract source | #362 contract | Use `phase_equilibrium_certification` and require the Gross associating production evidence quantities. | Proves Gross rows connect to the same shared contract as other PE routes. | No | M4 owner |
| Source margins | Gross retained fit statistics | Retain actual, threshold, margin, and status for source points, plot score, branch coverage, and mass-action residual. | Makes pass/fail margins auditable instead of prose-only. | No | M4 owner |
| Overlay gaps | Gross retained fit statistics | Mark literature-overlay rows as `regression_followup_not_m4_acceptance`. | Keeps M4 route proof honest without hiding M5-style regression gaps. | No | M4 owner |
| Test complete | #369 proof oracle | Package selector must collect real tests; checker and registry tests guard the same fields. | Prevents a zero-test selector from satisfying the issue. | No | M4 owner |

## Test Complete Definition

Test complete for #369 means:

- `uv run --no-sync python -m pytest packages\epcsaft-equilibrium\tests -k "associating and lle and certification" -q` passes with real tests collected.
- `uv run --no-sync python -m pytest tests\native\contracts\test_gross_2002_association_acceptance_checker.py tests\native\contracts\test_equilibrium_benchmark_registry.py -q` passes.
- `uv run --no-sync python scripts\validation\check_gross_2002_association_acceptance.py --json --require-complete --require-exact-association-hessian --require-fresh-native` reports `complete: true`, `shared_certification.status: accepted`, no blockers, and accepted Figure 8/Figure 10 source margins.
- `uv run --no-sync python scripts\dev\validate_project.py docs` passes.

## Acceptance Criteria Mapping

- Accepted Gross associating LLE rows include shared PE contract fields: Tasks 1 and 2.
- Active association derivative receipts remain retained: Tasks 1 and 2.
- Out-of-tolerance model gaps are split to M5 instead of hidden: Tasks 2 and 3.

## Non-Goals

- No M5 parameter regression.
- No source parameter refit.
- No EOS equation changes.
- No new associating family admission.
- No electrolyte, reactive, CE, CPE, boundary, or generalized phase-set route changes.
- No release claim.
- No downstream application metrics.

## Tasks

### Task 1: Add Red Package And Checker Assertions

**Use Cases:**
- A maintainer needs the package selector to fail if Gross accepted rows omit shared PE certification fields.
- A validation reviewer needs exact association derivative receipts and source tolerance margins, not only a campaign completion flag.
- A future route update must preserve request-specific Gross associating proof quantities.
- The cutover must replace campaign-only evidence with shared-contract and source-margin assertions.

**Files:**
- Create: `packages/epcsaft-equilibrium/tests/api/test_associating_lle_gross_2002_certification.py`
- Modify: `tests/native/contracts/test_gross_2002_association_acceptance_checker.py`

- [x] **Step 1: Add package-level assertions for `shared_certification`, source margins, and overlay separation.**
- [x] **Step 2: Add checker-contract assertions and a negative failed-margin assertion.**
- [x] **Step 3: Run focused tests and confirm the zero-test selector is replaced by real package tests.**

### Task 2: Emit Shared Certification And Source Margins

**Use Cases:**
- Accepted Gross Figure 8 and Figure 10 rows should show the shared `neutral_lle` certification contract.
- Accepted source-score rows should retain actual values, thresholds, margins, and statuses.
- Association derivative receipts should remain attached to accepted rows.
- Literature-overlay gaps should be visible without counting as M4 route acceptance.

**Files:**
- Modify: `scripts/validation/check_gross_2002_association_acceptance.py`

- [x] **Step 1: Build `shared_certification` from package capabilities and associating proof quantities.**
- [x] **Step 2: Add `source_tolerance_margins` from retained fit-stat and Hessian diagnostics.**
- [x] **Step 3: Treat shared-contract and source-margin blockers as checker blockers.**
- [x] **Step 4: Re-run focused tests and checker JSON.**

### Task 3: Sync Registry, Mirror, And Proof

**Use Cases:**
- Registry readers need to see that Gross associating evidence includes shared certification and source margins.
- The local and GitHub issue text must point at this executable implementation plan.
- Future maintainers need exact rerunnable commands.
- Acceptance evidence must show overlay gaps are not hidden inside M4 acceptance.

**Files:**
- Modify: `docs/superpowers/milestones/M6-validation/registries/equilibrium-evidence-registry.yaml`
- Modify: `tests/native/contracts/test_equilibrium_benchmark_registry.py`
- Modify: `docs/superpowers/issues/2026-06-30-m4-equilibrium-issue-0369-integrate-gross-2002-associating-lle-tolerance-evidence.md`

- [x] **Step 1: Add registry acceptance checks for shared certification and source margins.**
- [x] **Step 2: Validate the plan and docs.**
- [x] **Step 3: Sync local mirror and GitHub body with retained evidence.**

## Proof Oracle

```powershell
uv run --no-sync python scripts/validate_plan_task_use_cases.py --plan-path docs/superpowers/plans/2026-06-30-m4-equilibrium-issue-0369-gross-2002-associating-lle-tolerance-evidence-plan.md
uv run --no-sync python scripts/validate_plan_outcome_proof.py --plan-path docs/superpowers/plans/2026-06-30-m4-equilibrium-issue-0369-gross-2002-associating-lle-tolerance-evidence-plan.md
uv run --no-sync python -m pytest packages\epcsaft-equilibrium\tests -k "associating and lle and certification" -q
uv run --no-sync python -m pytest tests\native\contracts\test_gross_2002_association_acceptance_checker.py tests\native\contracts\test_equilibrium_benchmark_registry.py -q
uv run --no-sync python scripts\validation\check_gross_2002_association_acceptance.py --json --require-complete --require-exact-association-hessian --require-fresh-native
uv run --no-sync python scripts\dev\validate_project.py docs
pwsh.exe -NoProfile -ExecutionPolicy Bypass -File "$env:USERPROFILE\.codex\hooks\codex-cleanup.ps1" -RepoRoot .
```
