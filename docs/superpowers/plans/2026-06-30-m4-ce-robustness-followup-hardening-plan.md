# M4 CE Robustness Follow-Up Hardening Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:executing-plans`, `superpowers:test-driven-development`, `superpowers:systematic-debugging` for failing numerical gates, and `superpowers:verification-before-completion`. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Convert the seven CE robustness review findings into issue-backed hardening changes so EOS activity, seed escalation, continuation, assistance level, retained artifacts, and follow-up confidence gates are sharply inspectable without regenerating plots already produced elsewhere.

**Architecture:** Standalone CE remains one M4-owned `reactive_speciation` path. Robustness work lives in diagnostics, continuation control, native CE payloads, retained checker summaries, and focused validation gates. Accepted results must continue to prove unscaled balance and reaction stationarity; assisted paths may help find the state but may not replace final proof.

**Tech Stack:** Python 3.13 source checkout, C++17 equilibrium native core, Ipopt, CppAD-backed EOS derivative path, pybind diagnostics, pytest, PowerShell Superpowers validators, JSON checker evidence.

---

Source spec: `docs/superpowers/specs/2026-06-30-m4-ce-robustness-followup-audit-findings.md`
Prior plan: `docs/superpowers/plans/2026-06-30-m4-ce-convergence-robustness-hardening-plan.md`
Milestone: `M4 - Equilibrium`
Package owner: `packages/epcsaft-equilibrium`
IntelliJ receipt: CE-scoped IntelliJ MCP was available through `mcp__intellij_index_ePC_SAFT_CE`; `ide_index_status` reported `isDumbMode=false` and `isIndexing=false`.

## Outcome Proof

**Intent:** Harden the post-loop CE robustness surface so every difficult solve exposes the exact failing or assisting mechanism instead of requiring manual reconstruction from plots, native exceptions, or scattered diagnostics.
**Current Behavior:** The branch has strict final-proof gates and strong retained ideal MEA evidence, but EOS failures can hide exact proof gates, caller-seed exceptions can be dropped, EOS activity continuation is fixed-grid, assistance level is inferred manually, retained artifact diffs are noisy, there is no single follow-up checker, and EOS nonideality evidence is thinner than ideal MEA evidence.
**Expected Outcome:** CE diagnostics classify EOS-context failures by exact proof gate, preserve caller-seed exception evidence, adapt EOS activity continuation when needed, summarize assistance as a first-class diagnostic, emit retained artifact review digests, expose a follow-up confidence checker, and report an EOS nonideality diagnostic matrix without claiming literature MEA nonideality.
**Target Output:** Focused tests, issue mirrors, checker JSON, and result diagnostics show exact gate classes, seed rejection provenance, activity continuation accepted/rejected traces, assistance summaries, artifact digest hashes/extrema, follow-up gate status, and EOS `eos_x_phi`/`eos_x_gamma` evidence.
**Owner:** M4 equilibrium package owner for `packages/epcsaft-equilibrium`.
**Interface:** `ReactiveSpeciationResult.diagnostics`, native CE diagnostic payloads, `scripts/validation/check_standalone_ce_gate.py`, the new follow-up checker, retained JSON/CSV artifact summaries, and CE API/native tests.
**Cutover:** Review and loop-routing decisions move from plot inspection and ad hoc traceback reading to structured diagnostics and checker receipts.
**Replaced Path:** Generic EOS failure labels, silent caller-seed exception loss, fixed activity ladders without rejection trace, manually inferred assistance level, raw CSV diff review, hand-assembled command lists, and ambiguous EOS capability evidence are displaced by durable proof surfaces.
**Evidence:** Red-green focused tests for each slice, Superpowers plan and issue validators, direct checker JSON output, focused API/native test output, and cleanup hook output.
**Acceptance Proof:** The seven issue proof oracles pass and the follow-up checker reports complete evidence while preserving strict unscaled final balance and reaction-stationarity acceptance gates.
**Stop Criteria:** Stop if strict final-proof tolerances must be relaxed, if a change requires CPE or phase-equilibrium admission, if EOS evidence would require source-backed MEA nonideality data beyond this tranche, or if native exception capture requires provider-package scope outside an approved split.
**Avoid:** Do not add public solver routes, duplicate MEA plots, downstream application metrics, CPE behavior, reactive LLE admission, or broad provider refactors.
**Risk:** Added assistance and continuation diagnostics can look like solver success if not tied back to final unscaled proof; every accepted result must still expose the final physical proof norms.

## Implementation Boundaries

**Files To Create:** Local issue mirrors under `docs/superpowers/issues/`, focused follow-up checker tests if needed, and `scripts/validation/check_ce_robustness_followup.py` if an existing checker mode would blur ownership.
**Files To Modify:** `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/core/native_results.py`, CE native NLP/objective/bindings under `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/`, focused CE API/native tests, and CE validation scripts.
**Files To Avoid:** Bubble/dew routes, HELD route code, CPE route admission, regression package code, provider public APIs except existing EOS derivative/diagnostic contracts, and downstream project artifacts.
**Source Of Truth:** This plan, the audit spec, current retained CE diagnostics schema, native CE final-proof payloads, and existing M4 issue tracker conventions.
**Read Path:** Before each issue, read the touched diagnostics adapter, native payload fields, relevant focused tests, checker schema, and the issue mirror acceptance criteria.
**Write Path:** Add or tighten failing tests first, make the smallest CE-owned implementation change, run focused proof, then update checker evidence or retained digest schema only when the test requires it.
**Integration Points:** Native CE solve result, pybind diagnostic exposure, Python result classification, EOS activity objective, Ipopt continuation trace, retained artifact checker, and Superpowers issue mirrors.
**Migration Or Cutover:** Keep existing accepted CE API behavior stable while adding diagnostic fields and stricter checker gates; old ambiguous fields may remain as detailed context but cannot be the primary proof surface.
**Replaced Path Handling:** Remove obsolete diagnostic shortcuts that hide exact proof gates and retire any checker assumptions that force reviewers to inspect raw plot or CSV diffs first.
**Acceptance Proof Gate:** Each issue is complete only after its focused tests, plan validators, issue mirror validator, follow-up checker where relevant, standalone CE checker where relevant, ruff for changed Python files, and cleanup hook pass or a blocker is recorded.

## Decision Ledger

| Decision | Source | Answer | Deferred |
| --- | --- | --- | --- |
| Scope source | Audit spec | Convert all seven findings into repair slices. | No |
| Issue count | User request and planning gate default | Seven issues, one per finding. | No |
| Issue publication | Issue tracker policy | Create GitHub issues and local mirrors. | No |
| Validation depth | Planning gate default | Focused tests plus standalone and follow-up checkers. | No |
| TDD policy | User and repo policy | Required for every issue slice. | No |
| Execution route | Workflow ledger | Looping Mode with current-thread resolve-issue execution. | No |
| Milestone and package | Repo invariant | `M4 - Equilibrium`, `packages/epcsaft-equilibrium`. | No |
| Plot policy | User request | Do not show or regenerate plots already made elsewhere. | No |

## Task Plan

### Task 1: Classify EOS-Context Failures By Exact Proof Gate

**Use Cases:**
- A maintainer sees an EOS-context failure as stationarity, balance, proof-corrector, initialization, or Ipopt failure evidence instead of a generic EOS label.
- The EOS context remains visible as diagnostic evidence while the exact proof gate drives issue routing and acceptance review.
- The old early EOS catch-all classification is replaced by proof-gate-first classification.

**Files:**
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/core/native_results.py`
- Modify: `packages/epcsaft-equilibrium/tests/api/test_reactive_speciation_api.py`
- Modify: `scripts/validation/check_ce_robustness_followup.py` if Task 6 creates it first

- [ ] **Step 1: Add failing API classification cases.** Cover EOS-context stationarity, balance, proof-corrector, initialization, and Ipopt-shaped payloads.
- [ ] **Step 2: Verify the red failure.** Run the focused API test and confirm the current `eos_activity_failure` catch-all masks exact gates.
- [ ] **Step 3: Reorder classification.** Preserve activity context but classify exact gates before the EOS-context fallback.
- [ ] **Step 4: Expose context evidence.** Add or preserve diagnostic fields that say the failure occurred under EOS activity evaluation.
- [ ] **Step 5: Run proof.** Re-run focused API tests and the follow-up checker gate that consumes failure classes.

### Task 2: Preserve Caller-Seed Rejection And Exception Evidence

**Use Cases:**
- A bad caller seed escalates to CE-owned initialization while retaining the original rejection reason, exception message, and escalation source.
- Accepted fallback results still show that the caller seed did not pass independent final proof.
- The old silent catch-and-continue path is replaced by traceable seed provenance.

**Files:**
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/core/chemical_equilibrium_nlp.cpp`
- Modify: native CE result/binding files under `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/`
- Modify: `packages/epcsaft-equilibrium/tests/api/test_reactive_speciation_api.py`

- [ ] **Step 1: Add a failing seed-exception diagnostic test.** Use a pathological positive caller seed that triggers escalation and assert original rejection evidence.
- [ ] **Step 2: Verify the red failure.** Run the focused API/native test and capture the missing diagnostic field.
- [ ] **Step 3: Capture native exception evidence.** Record rejection source, reason, exception message, and whether fallback continued.
- [ ] **Step 4: Expose through bindings and diagnostics.** Keep accepted fallback behavior stable while adding fields.
- [ ] **Step 5: Run proof.** Re-run focused seed tests and API diagnostics tests.

### Task 3: Make EOS Activity Continuation Adaptive

**Use Cases:**
- Easy EOS activity cases still use the normal `0.0 -> 0.5 -> 1.0` trace when it succeeds.
- Hard EOS activity cases can reject a trial step, shrink the step, and continue with accepted/rejected trace evidence.
- The old fixed-grid interpretation of robustness is replaced by controller evidence with min step and max stage limits.

**Files:**
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/core/chemical_equilibrium_nlp.cpp`
- Modify: native continuation/result payloads under `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/`
- Modify: `packages/epcsaft-equilibrium/tests/native/diagnostics/test_chemical_equilibrium_eos_activity.py`

- [ ] **Step 1: Add failing adaptive-continuation diagnostics tests.** Assert accepted and rejected step traces, min step, max stage, and final full-EOS proof evidence.
- [ ] **Step 2: Verify the red failure.** Run focused EOS activity tests and confirm only the fixed grid is visible.
- [ ] **Step 3: Implement adaptive stepping.** Try the normal midpoint advance first, bisect rejected advances, and stop loudly at min step or max stage.
- [ ] **Step 4: Preserve easy-case trace.** Keep current successful `0.0, 0.5, 1.0` behavior when no rejection occurs.
- [ ] **Step 5: Run proof.** Re-run native EOS activity tests and API diagnostics tests.

### Task 4: Add First-Class Assistance Summary Diagnostics

**Use Cases:**
- A caller can answer whether the solve was direct, initialized, homotopy-assisted, corrected, caller-seed-escalated, or EOS-activity-assisted from one compact diagnostic object.
- Detailed diagnostics remain available for root cause analysis while the summary drives status display and review.
- The old manual inference path is replaced by a stable `assistance_summary` contract.

**Files:**
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/core/native_results.py`
- Modify: `packages/epcsaft-equilibrium/tests/api/test_reactive_speciation_api.py`
- Modify: follow-up checker tests if Task 6 creates them

- [ ] **Step 1: Add failing assistance-summary API tests.** Cover direct ideal, bad caller seed fallback, homotopy/proof-corrected, and EOS activity paths.
- [ ] **Step 2: Verify the red failure.** Run focused API tests and confirm callers must infer assistance manually.
- [ ] **Step 3: Build the summary.** Populate level, mechanisms, seed source, final proof source, stage counts, corrector use, and escalation status from existing diagnostics.
- [ ] **Step 4: Keep detailed diagnostics stable.** Avoid changing existing detailed keys unless a test proves ambiguity.
- [ ] **Step 5: Run proof.** Re-run focused API tests and the follow-up checker.

### Task 5: Add Retained Artifact Review Digest

**Use Cases:**
- A reviewer can inspect retained artifact row counts, column sets, numeric extrema, and stable hashes before scanning raw CSV diffs.
- The standalone checker rejects missing digest evidence for retained CE artifacts.
- The old raw-diff-first review path is replaced by semantic digest evidence.

**Files:**
- Modify: `scripts/validation/check_standalone_ce_gate.py`
- Modify: `tests/native/contracts/test_standalone_ce_gate.py`
- Modify: retained summary JSON only if digest evidence is stored with retained artifacts

- [ ] **Step 1: Add failing checker contract tests.** Require digest fields for retained CE CSV/JSON artifacts.
- [ ] **Step 2: Verify the red failure.** Run checker contract tests and the standalone CE checker.
- [ ] **Step 3: Implement digest generation.** Compute row counts, column lists, numeric extrema, and SHA-256 hashes from retained artifacts.
- [ ] **Step 4: Wire checker output.** Emit digest JSON in checker evidence and require it for `--require-complete`.
- [ ] **Step 5: Run proof.** Re-run checker contract tests and standalone CE checker.

### Task 6: Add A Single CE Robustness Follow-Up Confidence Gate

**Use Cases:**
- A future agent can run one bounded checker command to see whether this follow-up tranche is healthy.
- The checker reports exact completion state for the seven findings without launching an unbounded full suite.
- The old hand-assembled command list is replaced by one durable confidence gate plus focused tests.

**Files:**
- Create: `scripts/validation/check_ce_robustness_followup.py`
- Create or modify: `tests/native/contracts/test_ce_robustness_followup_gate.py`
- Modify: issue mirrors if proof oracle command names change

- [ ] **Step 1: Add failing checker contract tests.** Require JSON status, seven finding keys, proof command names, exact failure taxonomy evidence, and EOS matrix evidence.
- [ ] **Step 2: Verify the red failure.** Run the new checker contract test and confirm the command is missing.
- [ ] **Step 3: Implement the checker.** Emit bounded JSON evidence from diagnostics/checker artifacts without running the full native suite internally.
- [ ] **Step 4: Add `--require-complete`.** Fail when required evidence is absent or incomplete.
- [ ] **Step 5: Run proof.** Run the checker contract test and direct `--json --require-complete` command.

### Task 7: Add EOS Nonideality Diagnostic Matrix Evidence

**Use Cases:**
- EOS `eos_x_phi` and `eos_x_gamma` both report activity mode, derivative backend, continuation trace, and final proof or exact failure class.
- The checker distinguishes synthetic EOS activity evidence from source-backed MEA nonideality validation.
- The old thin EOS evidence path is replaced by explicit diagnostic-matrix evidence and a capability boundary.

**Files:**
- Modify: `packages/epcsaft-equilibrium/tests/native/diagnostics/test_chemical_equilibrium_eos_activity.py`
- Modify: `packages/epcsaft-equilibrium/tests/api/test_reactive_speciation_api.py`
- Modify: `scripts/validation/check_ce_robustness_followup.py`

- [ ] **Step 1: Add failing EOS matrix tests.** Cover `eos_x_phi`, `eos_x_gamma`, accepted path evidence, and classified-failure evidence.
- [ ] **Step 2: Verify the red failure.** Run focused EOS activity and API tests.
- [ ] **Step 3: Populate matrix evidence.** Report activity mode, derivative backend, continuation trace summary, status, exact failure class, and capability boundary.
- [ ] **Step 4: Wire checker evidence.** Require the matrix in the follow-up checker without claiming MEA-level EOS nonideality validation.
- [ ] **Step 5: Run proof.** Re-run focused EOS tests, API tests, and follow-up checker.

## Proof Oracle

Plan and issue gates:

```powershell
pwsh.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\validate-plan-task-use-cases.ps1 -PlanPath docs/superpowers/plans/2026-06-30-m4-ce-robustness-followup-hardening-plan.md
pwsh.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\validate-plan-outcome-proof.ps1 -PlanPath docs/superpowers/plans/2026-06-30-m4-ce-robustness-followup-hardening-plan.md
pwsh.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\validate-issue-mirror.ps1 -IssueFile <issue-mirror>
```

Focused implementation gates:

```powershell
uv run --no-sync python run_pytest.py packages/epcsaft-equilibrium/tests/api/test_reactive_speciation_api.py -q
uv run --no-sync python run_pytest.py packages/epcsaft-equilibrium/tests/native/diagnostics/test_chemical_equilibrium_eos_activity.py -q
uv run --no-sync python run_pytest.py tests/native/contracts/test_standalone_ce_gate.py -q
uv run --no-sync python run_pytest.py tests/native/contracts/test_ce_robustness_followup_gate.py -q
uv run --no-sync python scripts/validation/check_standalone_ce_gate.py --json --require-single-nlp-path --require-oracles --require-complete
uv run --no-sync python scripts/validation/check_ce_robustness_followup.py --json --require-complete
uv run --no-sync python -m ruff check packages/epcsaft-equilibrium/tests/api/test_reactive_speciation_api.py packages/epcsaft-equilibrium/tests/native/diagnostics/test_chemical_equilibrium_eos_activity.py tests/native/contracts/test_standalone_ce_gate.py tests/native/contracts/test_ce_robustness_followup_gate.py scripts/validation/check_standalone_ce_gate.py scripts/validation/check_ce_robustness_followup.py packages/epcsaft-equilibrium/src/epcsaft_equilibrium/core/native_results.py
pwsh.exe -NoProfile -ExecutionPolicy Bypass -File "$env:USERPROFILE\.codex\hooks\codex-cleanup.ps1" -RepoRoot .
```

Native rebuild gate when C++ files change:

```powershell
uv run --no-sync python scripts/dev/build_epcsaft.py --build-only --parallel 10
```

## Issue Creation Packet

Create seven AFK-ready task issues in `M4 - Equilibrium`, all owned by `packages/epcsaft-equilibrium`, with labels `agent-ready`, `status:ready`, `type:task`, `area:equilibrium`, `equilibrium`, `solver`, `native`, `backend:ipopt`, and `validation`. Add `backend:cppad` to EOS activity issues. Each issue mirror must include this plan, the audit spec, and its focused proof oracle.

## Risk Notes

- Do not weaken final proof tolerances to make a robustness path pass.
- Treat EOS activity as diagnostic and synthetic proof evidence unless source-backed MEA EOS nonideality data is added in a later validation issue.
- Keep plot output out of this tranche unless a later user request explicitly changes the artifact policy.
