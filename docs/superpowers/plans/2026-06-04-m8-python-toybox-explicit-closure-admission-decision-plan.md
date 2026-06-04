# Explicit Closure Admission Decision Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn the toybox evidence into a clear admission decision that keeps Picard as the only retained approximation candidate and blocks provider implementation until property and derivative gates pass.

**Architecture:** Remove active code paths for obsolete closure candidates from the toybox while preserving source-backed exact baselines. Add a generated admission summary that maps retained evidence to `continue`, `historical_only`, `delete_from_toybox`, `provider_blocked`, or `provider_candidate`.

**Tech Stack:** Python, YAML/CSV, Markdown, pytest, ripgrep.

---

## Intake

- Source Spec: `docs/superpowers/specs/2026-06-04-m8-python-toybox-explicit-closure-admission-decision.md`
- Source Issue: `none`
- Source Plan: `docs/superpowers/plans/2026-06-04-m8-python-toybox-explicit-closure-admission-decision-plan.md`
- GitHub Issue: `none`
- Milestone: `M8 - Python Toybox`
- AFK/HITL: `HITL` because provider admission thresholds need human review.

## Dependencies

This plan should run after:

- `docs/superpowers/plans/2026-06-04-m8-python-toybox-picard-autodiff-and-exact-implicit-sensitivity-baseline-hardening-plan.md`
- `docs/superpowers/plans/2026-06-04-m8-python-toybox-associating-compound-pressure-density-validation-lane-plan.md`

It may also consume the equilibrium relevance probe if that probe exists
before the admission decision is finalized. It must not mark provider work as
implementation-ready unless derivative, property, and residual gates have
evidence.

## Acceptance Criteria

- [ ] The toybox active closure registry retains exact implicit baselines, source topology reductions, exact 2B reduction, and seven-step Picard only.
- [ ] Obsolete diagonal-polish, collapsed-mean-field, and unrelated approximation families do not appear as runnable active closure lanes.
- [ ] A retained admission summary records each closure family, status, evidence basis, and provider-admission decision.
- [ ] Issue #161 docs are not marked implementation-ready unless the evidence gates pass.
- [ ] No provider, equilibrium, benchmark, or public API files are changed.

## Tasks

### Task 1: Closure Registry Cleanup

**Files:**
- Modify: `analyses/package_validation/explicit_association_toybox/scripts/closure_models.py`
- Modify: `analyses/package_validation/explicit_association_toybox/scripts/run_grid.py`
- Modify: `analyses/package_validation/explicit_association_toybox/tests/test_topology_reductions.py`
- Modify: `analyses/package_validation/explicit_association_toybox/tests/test_propagation_evidence.py`

- [ ] **Step 1: Write failing closure-registry tests**

Add tests that assert the active closure names are exactly:
`implicit_exact`, `exact_2b_reduction`, source topology reductions, and the
Picard closure constant.

- [ ] **Step 2: Run tests and verify failure**

Run: `uv run python run_pytest.py analyses/package_validation/explicit_association_toybox/tests/test_topology_reductions.py analyses/package_validation/explicit_association_toybox/tests/test_propagation_evidence.py -q`

Expected before cleanup: obsolete closure names are still reachable or tests
are missing.

- [ ] **Step 3: Remove active obsolete closure paths**

Delete runnable registry entries and generation loops for diagonal-polish,
collapsed-mean-field, and other non-retained approximation families. Keep
source topology reductions because they are exact validation baselines under
matched topology assumptions.

- [ ] **Step 4: Run closure tests**

Run: `uv run python run_pytest.py analyses/package_validation/explicit_association_toybox/tests/test_topology_reductions.py analyses/package_validation/explicit_association_toybox/tests/test_propagation_evidence.py -q`

Expected: active closure registry tests pass.

- [ ] **Step 5: Commit**

Stage only closure cleanup files and commit with:
`analysis: retain only Picard association closure candidate`

### Task 2: Admission Summary Artifact

**Files:**
- Create: `analyses/package_validation/explicit_association_toybox/scripts/admission_decision.py`
- Create: `analyses/package_validation/explicit_association_toybox/docs/explicit_closure_admission_decision.md`
- Test: `analyses/package_validation/explicit_association_toybox/tests/test_admission_decision.py`

- [ ] **Step 1: Write failing summary tests**

Add a test that calls `build_admission_decision_rows()` and asserts every row
has `closure_family`, `status`, `evidence_basis`, `provider_admission`, and
`blocking_gate`.

- [ ] **Step 2: Run tests and verify failure**

Run: `uv run python run_pytest.py analyses/package_validation/explicit_association_toybox/tests/test_admission_decision.py -q`

Expected before implementation: admission decision module missing.

- [ ] **Step 3: Implement summary generation**

Generate rows that classify Picard as `continue` and `provider_blocked`,
exact implicit as `continue` reference baseline, Huang/Radosz reductions as
validation baselines, and obsolete closure families as `delete_from_toybox` or
`historical_only`.

- [ ] **Step 4: Render Markdown summary**

Run: `uv run python analyses/package_validation/explicit_association_toybox/scripts/admission_decision.py`

Expected: `docs/explicit_closure_admission_decision.md` contains a table with
provider gates and a clear statement that no provider implementation is
admitted yet.

- [ ] **Step 5: Commit**

Stage only admission summary files and commit with:
`analysis: document explicit closure admission decision`

### Task 3: M3 Issue 161 Alignment

**Files:**
- Modify: `docs/superpowers/issues/2026-05-29-m3-eos-issue-0161-design-explicit-pc-saft-association-site-closures-for-eos-evaluation.md`
- Modify: `docs/superpowers/plans/2026-05-29-m3-eos-issue-0161-design-explicit-pc-saft-association-site-closures-for-eos-evaluation-plan.md`

- [ ] **Step 1: Update local issue mirror wording**

State that M8 toybox evidence is required before #161 can become provider
implementation-ready. Link the M8 admission decision spec and plan.

- [ ] **Step 2: Update local issue plan wording**

Replace any implementation-ready language with provider-admission gate
language unless all M8 gates have passed.

- [ ] **Step 3: Verify references**

Run: `rg -n "M8|provider_admission|Picard|implementation-ready" docs/superpowers/issues/2026-05-29-m3-eos-issue-0161-design-explicit-pc-saft-association-site-closures-for-eos-evaluation.md docs/superpowers/plans/2026-05-29-m3-eos-issue-0161-design-explicit-pc-saft-association-site-closures-for-eos-evaluation-plan.md`

Expected: M8 gate references appear and implementation-ready wording is not
unconditional.

- [ ] **Step 4: Commit**

Stage only #161 local docs and commit with:
`docs: align explicit closure provider admission gate`

## Proof Oracle

- `uv run python run_pytest.py analyses/package_validation/explicit_association_toybox/tests/test_topology_reductions.py analyses/package_validation/explicit_association_toybox/tests/test_propagation_evidence.py analyses/package_validation/explicit_association_toybox/tests/test_admission_decision.py -q`
- `uv run python analyses/package_validation/explicit_association_toybox/scripts/admission_decision.py`
- `rg -n "collapsed|diagonal|mean_field|polish" analyses/package_validation/explicit_association_toybox/scripts analyses/package_validation/explicit_association_toybox/config`
