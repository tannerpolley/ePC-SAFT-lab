# Associating GFPE VLE Admission Prerequisite Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:test-driven-development and superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Open production admission for source-backed neutral associating binary VLE route solves needed by Gross/Sadowski 2002 Figures 2-9, while preserving exact association-Hessian evidence and current GFPE admission discipline.

**Architecture:** The public VLE workflows currently reject source-backed Gross/Sadowski 2002 associating binary VLE cases, including the Figure 2 methanol/isobutane case and the Figure 6 1-butanol/n-butane case. Figure 8 and Figure 9 also require public isobaric associating VLE branches for full envelope replication. Associating GFPE admission is still limited to the retained Gross/Sadowski 2002 neutral two-phase LLE proof. This plan adds a narrow source-backed VLE admission slice in `packages/epcsaft-equilibrium` so figure-replication issues can generate real model curves through public routes instead of adding route implementation work to validation PRs.

**Tech Stack:** Python public equilibrium API, `packages/epcsaft-equilibrium`, native Ipopt GFPE route, CppAD exact association derivatives, pytest through `run_pytest.py`, Gross/Sadowski 2002 paper-validation artifacts, docs validation, cleanup hook.

---

## Intake

- Source spec: `docs/superpowers/specs/2026-06-19-m4-equilibrium-gross-2002-full-figure-replication.md`
- Dependent issues:
  - https://github.com/ePC-SAFT/ePC-SAFT/issues/281
  - https://github.com/ePC-SAFT/ePC-SAFT/issues/282
  - https://github.com/ePC-SAFT/ePC-SAFT/issues/283
  - https://github.com/ePC-SAFT/ePC-SAFT/issues/284
- Milestone: `M4 - Equilibrium`
- Package owner: `packages/epcsaft-equilibrium`
- Capability: `association`
- Backend: `Ipopt`
- Triggering evidence: #281 worker probe found public `bubble_pressure` and `dew_pressure` reject the Figure 2 methanol/isobutane associating binary with `InputError` because associating GFPE admission is limited to the source-backed LLE proof. #282 then hit the same public-route admission block for Figure 6 1-butanol/n-butane during model generation. #283 and #284 require the same VLE route family for Figure 8 methanol/cyclohexane and Figure 9 methanol/1-octanol envelope replication.

## Outcome Contract

**Intent:** Permit source-backed neutral associating binary VLE route solves needed by Gross/Sadowski 2002 Figures 2-9.
**Current Behavior:** Associating GFPE admission accepts the retained Gross/Sadowski 2002 neutral LLE proof but rejects source-backed associating binary VLE solves through the public workflow.
**Expected Outcome:** Source-backed Gross/Sadowski 2002 associating binary VLE cases can be solved through public `Equilibrium(...).solve()` bubble/dew routes with exact association-Hessian receipts.
**Target-Perspective Output:** The Figure 2-9 replication workers can generate model CSVs from production public routes and the checker can verify exact derivative evidence.
**Truth Owner:** `packages/epcsaft-equilibrium` selector/admission, native GFPE route metadata, Gross/Sadowski 2002 source-backed validation records, and full-replication checker contracts.
**Contract Interface:** Public `epcsaft_equilibrium.Equilibrium(...).solve()` bubble/dew workflows and retained result metadata consumed by Gross 2002 validation scripts.
**Cutover Decision:** Replace the VLE rejection for source-backed associating binary Gross 2002 cases with explicit admissible route cases backed by tests and retained derivative receipts.
**Displaced Path:** The Figure 2-9 worker routes must stop using admission rejection as a validation blocker once this issue lands.
**Evidence Lane:** Failing admission tests, production route tests, exact association-Hessian receipts, validation probes for representative Gross 2002 Figure 2, Figure 6, Figure 8, and Figure 9 inputs, docs validation, cleanup hook.
**Acceptance Evidence:** Focused tests prove public bubble/dew routes accept the source-backed associating binary cases and report exact association derivative metadata; #281, #282, #283, and #284 can resume model generation without touching native implementation files.
**Stop Criteria:** Stop if the required VLE admission cannot be narrowed to source-backed neutral associating binary cases without broader generalized phase-family exposure.
**Avoid:** Do not add electrolyte, reactive, CE, CPE, generalized phase-count, or broad associating-family claims. Do not weaken selector diagnostics, derivative receipt checks, source-backed parameter provenance, or #279 score/checker thresholds.

## Architecture Slice

**Files To Modify:** Candidate files are under `packages/epcsaft-equilibrium/**`, focused native GFPE admission/selector tests, public route tests, and Gross 2002 validation probe files when needed.
**Files To Avoid:** Gross 2002 figure source/plot artifacts owned by #281, #282, #283, and #284; regression package files; downstream repositories; electrolyte/reactive route files; and unrelated provider EOS logic.
**Source Of Truth:** GFPE admission policy, existing associating LLE proof, Gross/Sadowski 2002 Figure 2 source identity artifact, Figure 6/7 source metadata, Figure 8/9 source metadata, Table 1 pure parameters, Table 2 binary parameters, and public route contracts.
**Read Path:** Public route request -> selector/admission -> native GFPE solve -> result metadata -> validation checker.
**Write Path:** Production route code changes stay in `packages/epcsaft-equilibrium`; validation evidence stays in focused tests and retained Gross 2002 proof artifacts.
**Integration Points:** `epcsaft_equilibrium.Equilibrium`, selector admission, Ipopt route dispatch, exact association derivative diagnostics, Gross 2002 full-replication checker.
**Acceptance Evidence Gate:** The issue cannot close until source-backed Figure 2 methanol/isobutane, Figure 6 1-butanol/n-butane, Figure 8 methanol/cyclohexane, and Figure 9 methanol/1-octanol VLE probes succeed through public routes and expose exact association-Hessian evidence.

### Task 1: Capture The Current VLE Admission Rejection

**Use Cases:**
- The existing public route rejection is preserved as a failing test before implementation.
- The failure names representative Figure 2, Figure 6, Figure 8, and Figure 9 systems and the route family involved.
- The test goes through public `Equilibrium(...).solve()`, not private helpers.

**Files:**
- Modify or create focused tests under `tests/native/contracts` or the existing equilibrium route contract test lane.
- Avoid figure replication artifact files owned by #281.

- [ ] **Step 1: Add a failing public-route test**

  Add a test that constructs the source-backed Gross/Sadowski 2002 Figure 2 methanol/isobutane, Figure 6 1-butanol/n-butane, Figure 8 methanol/cyclohexane, and Figure 9 methanol/1-octanol associating binary inputs and calls the public VLE routes through `Equilibrium(...).solve()`.

- [ ] **Step 2: Verify the current failure**

  Run the focused test and confirm it fails from the current admission rejection rather than parameter loading, import setup, or unrelated solver configuration.

### Task 2: Open Narrow Source-Backed Associating VLE Admission

**Use Cases:**
- Source-backed neutral associating VLE bubble/dew cases can enter GFPE.
- Admission remains closed for unproven broad associating, electrolyte, reactive, CE, CPE, or generalized phase-count cases.
- Diagnostics stay explicit when an unproven associating case is rejected.

**Files:**
- Modify `packages/epcsaft-equilibrium/**` selector/admission and route metadata files identified by IntelliJ definition/reference lookup.
- Modify focused tests only.

- [ ] **Step 1: Locate the admission guard**

  Use IntelliJ definition/reference navigation first to find the admission guard that emits the current associating GFPE VLE rejection.

- [ ] **Step 2: Implement the narrow admission change**

  Admit only the source-backed neutral associating binary VLE route cases required for Gross/Sadowski 2002 Figures 2-9. Keep all broader unproven route families rejected with clear diagnostics.

- [ ] **Step 3: Preserve exact derivative gating**

  Require exact association derivative evidence for accepted associating VLE solves. Do not route accepted associating VLE through approximate derivative evidence.

### Task 3: Prove Public Route Metadata And Regression Safety

**Use Cases:**
- The accepted solve returns retained metadata consumed by the Gross 2002 figure scripts.
- Rejected unproven families still fail loudly.
- The proof command is narrow enough for M4 implementation work.

**Files:**
- Modify route contract tests and validation probes as needed.
- Avoid broad docs or capability claims unless a user-facing admission matrix changes.

- [ ] **Step 1: Assert derivative receipt metadata**

  Extend the focused test to assert `derivative_status` or the existing exact association-Hessian receipt field used by Gross 2002 acceptance checkers.

- [ ] **Step 2: Assert no broad exposure**

  Add or update a negative test showing at least one unproven associating route family still rejects with an explicit diagnostic.

- [ ] **Step 3: Run focused validation**

  Run the route tests and the Gross 2002 acceptance checker mode needed to prove Figures 2, 6, 8, and 9 can resume model generation.

## Test Complete And Metrics

Test complete for this prerequisite means:

- Public VLE routes accept the source-backed Gross/Sadowski 2002 Figure 2, Figure 6, Figure 8, and Figure 9 associating binary inputs.
- Accepted route results expose exact association-Hessian evidence consumed by Gross 2002 validation scripts.
- Existing associating LLE proof remains accepted.
- At least one unproven broader associating/electrolyte/reactive route remains explicitly rejected.
- #281, #282, #283, and #284 can resume model curve generation without adding native implementation files to the figure-replication PRs.

## Proof Oracle

```bash
uv run --no-sync python scripts/dev/build_epcsaft.py --profile equilibrium --build-only --parallel 4
uv run --no-sync python run_pytest.py <focused-associating-vle-route-test> -q
uv run --no-sync python scripts/validation/check_gross_2002_association_acceptance.py --json --require-exact-association-hessian --require-fresh-native
uv run --no-sync python scripts/dev/validate_project.py docs
bash "$HOME/.codex/hooks/codex-cleanup.sh" --repo-root .
```

## Non-Goals

- No Gross 2002 figure digitization, plot rendering, or scoring artifacts; those remain in #281, #282, #283, and #284.
- No electrolyte, reactive, CE, CPE, or generalized phase-count admission.
- No broad associating-family capability claim beyond source-backed neutral binary VLE route admission.
- No lowering of existing exact-derivative or source-provenance gates.
