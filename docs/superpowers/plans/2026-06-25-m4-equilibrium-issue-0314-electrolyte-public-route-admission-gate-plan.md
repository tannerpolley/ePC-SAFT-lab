# Electrolyte Public GFPE Route Admission Gate Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> `superpowers:subagent-driven-development` or `superpowers:executing-plans` to
> implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for
> tracking.

**Goal:** Resolve GitHub issue #314 by admitting only the certified,
source-backed public electrolyte GFPE route surface and then closing parent
issue #191.

**Architecture:** This is the final M4 electrolyte admission gate. It consumes
#269 source evidence, #300 reduced-basis/Born exactness, #302 charge-neutral
TPD screening, #306 HELD2 phase discovery, #312 Stage III refinement, and #313
postsolve certification. It updates selector/admission behavior, capability
evidence, registry evidence, docs, tests, and #191 closeout state. Reactive,
CE, CPE, regression, downstream, and release claims remain outside this gate.

**Tech Stack:** C++ equilibrium native core, pybind11 bindings, Python
activation/capability layer, validation checker, pytest contracts through
`run_pytest.py`, M4 issue mirrors, M4 benchmark registry, GitHub dependencies.

---

## Intake

- GitHub Issue: `https://github.com/ePC-SAFT/ePC-SAFT/issues/314`
- Parent Issue: `https://github.com/ePC-SAFT/ePC-SAFT/issues/191`
- Source Spec: `docs/superpowers/specs/2026-05-30-m4-equilibrium-issue-0191-prove-electrolyte-gfpe-and-held2-0-validation-gates.md`
- Source Issue: `docs/superpowers/issues/2026-06-25-m4-equilibrium-issue-0314-admit-source-backed-public-electrolyte-gfpe-route.md`
- Source Plan: `docs/superpowers/plans/2026-06-25-m4-equilibrium-issue-0314-electrolyte-public-route-admission-gate-plan.md`
- Prior Child Gate: `docs/superpowers/issues/2026-06-25-m4-equilibrium-issue-0313-add-electrolyte-postsolve-phase-set-certification-gate.md`
- Milestone: `M4 - Equilibrium`
- Package owner: `packages/epcsaft-equilibrium`

## Outcome Proof

**Intent:** Open only the certified, source-backed public electrolyte GFPE route
surface after every prior #191 gate is closed.
**Current Behavior:** Electrolyte route evidence is planned to be certified by
#313, but public route admission remains closed until a separate route/capability
cutover proves the user-facing boundary.
**Expected Outcome:** A retained public-admission checker exits successfully
only when all prerequisite electrolyte checkers pass and the exposed route
returns certified electrolyte phase-set results with honest capability scope.
**Target Output:** `scripts/validation/check_electrolyte_public_admission.py --json --require-source-gate --require-readiness-gate --require-tpd-gate --require-held2-discovery --require-stage-iii --require-postsolve-certification --require-public-admission --require-complete` returns `complete: true`.
**Owner:** M4 equilibrium package owner.
**Interface:** Public `Equilibrium` route contract, activation matrix,
capability payload, retained checker JSON, docs, M4 registry, and #191 closeout
evidence.
**Cutover:** Open the certified electrolyte route surface and remove closed-route
assertions that are no longer true for that exact scope.
**Replaced Path:** Permanent closed electrolyte route state after executable
source-backed certification exists.
**Evidence:** Public admission checker JSON, activation/capability tests,
registry evidence tests, docs validation, and GitHub issue/PR closure evidence.
**Acceptance Proof:** Acceptance is proven when the public admission checker
consumes all prerequisite gates, proves the route returns certified electrolyte
phase-set results, and keeps unsupported reactive/generalized/regression claims
closed.
**Stop Criteria:** Stop if prerequisite evidence is missing, if capability
claims outrun executable evidence, or if admission requires reactive/CE/CPE
support.
**Avoid:** Do not add reactive equilibrium, parameter regression, downstream
application metrics, release claims, or broad electrolyte families beyond the
retained source-backed evidence.
**Risk:** Public admission can easily overstate capability; this gate must make
the admitted scope narrow and executable.

## Implementation Boundaries

**Files To Create:** `scripts/validation/check_electrolyte_public_admission.py`, `tests/native/contracts/test_electrolyte_public_admission.py`.
**Files To Modify:** Public route activation and capability files under
`packages/epcsaft-equilibrium/**`, registry evidence, user-facing docs, #191/#314
issue mirrors, and the M4 README.
**Files To Avoid:** Regression package files, downstream repositories, provider
EOS internals unless consuming a public provider receipt, release metadata, and
reactive route code.
**Source Of Truth:** #191 source spec, M4 GFPE doctrine, #313 postsolve proof,
and the retained source-backed electrolyte evidence chain.
**Read Path:** Consume #269, #300, #302, #306, #312, and #313 checkers.
**Write Path:** Write one admission checker, one public-admission contract test
module, activation/capability updates, registry evidence rows, docs, and
tracker updates.
**Integration Points:** Public `Equilibrium` route selector, capability evidence,
activation capability tests, registry evidence, docs, and GitHub dependencies.
**Migration Or Cutover:** #191 remains blocked by #314 until this PR merges;
after merge, #191 can close and M6 #192 can become the next GFPE evidence gate.
**Replaced Path Handling:** Remove or rewrite closed-route assertions only for
the admitted electrolyte scope; keep unsupported surfaces explicitly closed.
**Acceptance Proof Gate:** The proof oracle commands below must pass before
push, PR creation, merge, #314 close, and #191 close.

## Decision Ledger

| Decision | Source | Answer | Impact | Deferred? | Risk owner |
| --- | --- | --- | --- | --- | --- |
| Final child | #191 checkpoint sequence | #314 owns public electrolyte route admission. | Prevents premature closure of #191. | No | M4 owner |
| Admission breadth | M4 GFPE doctrine | Admit only source-backed certified electrolyte scope. | Avoids broad unsupported claims. | No | M4 owner |
| Downstream linkage | Project roadmap | M6 #192 follows after #191. | Keeps benchmark/capability closure outside M4 implementation. | No | M4 owner |

## Required Contract Tests

- `test_public_admission_requires_all_electrolyte_gates`: the checker rejects
  missing #269/#300/#302/#306/#312/#313 evidence.
- `test_public_route_returns_certified_electrolyte_result`: the route payload
  includes postsolve certification receipts.
- `test_capabilities_distinguish_scope`: neutral, associating, electrolyte, and
  reactive support remain distinct.
- `test_registry_records_source_and_checker_chain`: source fixture, parameter
  bundle, checkers, tolerances, and route status are retained.
- `test_unsupported_surfaces_remain_closed`: reactive, CE, CPE, regression,
  release, and unsupported generalized electrolyte claims stay closed.
- `test_parent_issue_closeout_evidence_is_current`: #191 mirror and M4 README
  no longer list open M4 blockers after #314 closes.

## Acceptance Criteria

- [ ] The public admission checker consumes #269, #300, #302, #306, #312, and
  #313 evidence.
- [ ] The public route surface exposes only the certified electrolyte GFPE scope.
- [ ] Capability evidence distinguishes neutral, associating, electrolyte, and
  reactive support.
- [ ] Registry evidence names the source fixture, parameter bundle, validation
  checkers, tolerances, and public route status.
- [ ] User-facing docs state the admitted electrolyte scope and explicit
  non-goals.
- [ ] Negative tests reject missing prerequisite evidence, uncertified phase
  sets, unsupported species bases, and premature reactive admission.
- [ ] #191 is updated and closed only after this issue merges and the retained
  public-admission checker passes.
- [ ] M4 README shows no remaining open M4 issues after #191 closes.

## Non-Goals

- No reactive route admission.
- No CE/CPE support claim.
- No parameter regression or downstream application metrics.
- No release publication claim.

## Tasks

### Task 1: Define The Public Admission Contract

**Use Cases:**

- A user needs to know exactly which electrolyte route surface is supported.
- A reviewer needs proof that all prerequisite gates are consumed.

**Files:**

- `scripts/validation/check_electrolyte_public_admission.py`
- `tests/native/contracts/test_electrolyte_public_admission.py`

- [ ] Add missing-prerequisite tests for #269/#300/#302/#306/#312/#313.
- [ ] Add capability-scope tests for admitted and still-closed surfaces.
- [ ] Add registry evidence tests for source and checker chain metadata.

### Task 2: Admit The Certified Route

**Use Cases:**

- The certified electrolyte route must become a public package capability after
  evidence exists.
- Unsupported electrolyte/reactive surfaces must stay closed.

**Files:**

- `packages/epcsaft-equilibrium/**`
- `docs/pages/**`
- `docs/superpowers/milestones/M4-equilibrium/registries/equilibrium-benchmark-registry.yaml`

- [ ] Update selector/admission behavior for the certified scope.
- [ ] Update capabilities and registry evidence.
- [ ] Update user-facing docs and negative tests.

### Task 3: Close The M4 Parent

**Use Cases:**

- M4 should hand off to M6 only after all #191 children close.
- The local and GitHub trackers must show no remaining M4 blockers.
- The acceptance evidence must show the cutover from closed public electrolyte
  route state to the certified #314 admission path while keeping unsupported
  surfaces out of the replacement.

**Files:**

- `docs/superpowers/issues/**`
- `docs/superpowers/milestones/M4-equilibrium/README.md`

- [ ] Update #314 mirror after merge.
- [ ] Update and close #191 after public admission passes.
- [ ] Confirm M6 #192 remains the next GFPE evidence gate.

## Proof Oracle

```powershell
uv run --no-sync python scripts/validate_plan_task_use_cases.py --plan-path docs/superpowers/plans/2026-06-25-m4-equilibrium-issue-0314-electrolyte-public-route-admission-gate-plan.md
uv run --no-sync python scripts/validate_plan_outcome_proof.py --plan-path docs/superpowers/plans/2026-06-25-m4-equilibrium-issue-0314-electrolyte-public-route-admission-gate-plan.md
uv run --no-sync python scripts/validation/check_electrolyte_public_admission.py --json --require-source-gate --require-readiness-gate --require-tpd-gate --require-held2-discovery --require-stage-iii --require-postsolve-certification --require-public-admission --require-complete
uv run --no-sync python run_pytest.py tests/native/contracts/test_electrolyte_public_admission.py tests/native/contracts/test_electrolyte_postsolve_certification.py packages/epcsaft-equilibrium/tests/contracts/test_activation_capabilities.py tests/native/contracts/test_generalized_equilibrium_registry.py -q
uv run --no-sync python scripts/dev/validate_project.py docs
pwsh.exe -NoProfile -ExecutionPolicy Bypass -File "$env:USERPROFILE\.codex\hooks\codex-cleanup.ps1" -RepoRoot .
```
