# Prove Electrolyte GFPE And HELD2.0 Validation Gates Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> `superpowers:subagent-driven-development` or `superpowers:executing-plans` to
> implement child issues task-by-task. This parent plan is an umbrella plan; do
> not open public electrolyte routes directly from #191.

**Goal:** Resolve GitHub issue #191 by closing the electrolyte HELD2 child gates
in order: counterion-pair phase discovery (#306), Stage III reduced-variable
refinement (#312), postsolve certification (#313), and public route admission
(#314).

**Architecture:** #191 is the electrolyte GFPE umbrella for
`packages/epcsaft-equilibrium`. Existing children prove source data, reduced
electroneutral variables, Born SSM/DS derivative receipts, charge-neutral TPD
screening, and HELD2 counterion-pair phase discovery. The next child, #312,
must consume the #306 candidate handoff and prove Stage III reduced-variable
refinement. Public electrolyte admission stays closed until #313 proves
postsolve certification and #314 proves public route admission.

**Tech Stack:** C++ equilibrium native core, pybind11 bindings, Python
validation checkers, pytest contracts through `run_pytest.py`, M4 issue
mirrors, M4 registry evidence, GitHub dependency readiness.

---

## Intake

- Source Spec: `docs/superpowers/specs/2026-05-30-m4-equilibrium-issue-0191-prove-electrolyte-gfpe-and-held2-0-validation-gates.md`
- Source Issue: `docs/superpowers/issues/2026-05-30-m4-equilibrium-issue-0191-prove-electrolyte-gfpe-and-held2-0-validation-gates.md`
- Source Plan: `docs/superpowers/plans/2026-05-30-m4-equilibrium-issue-0191-prove-electrolyte-gfpe-and-held2-0-validation-gates-plan.md`
- Active Child: `https://github.com/ePC-SAFT/ePC-SAFT/issues/312`
- Active Child Plan: `docs/superpowers/plans/2026-06-25-m4-equilibrium-issue-0312-electrolyte-held2-stage-iii-refinement-gate-plan.md`
- Milestone: `M4 - Equilibrium`
- AFK/HITL: `HITL`

## Outcome Proof

**Intent:** Keep #191 as the parent acceptance gate for electrolyte GFPE while
forcing implementation through PR-sized child gates.
**Current Behavior:** #269, #300, #302, and #306 are closed, but the current
code only has source readiness, reduced-basis/Born exactness evidence,
deterministic charge-neutral TPD screening, and HELD2 phase-discovery handoff
evidence.
**Expected Outcome:** #191 closes only after HELD2 counterion-pair phase
discovery, Stage III electrolyte refinement, postsolve certification, and
public route admission children all close with retained executable evidence.
**Target Output:** `electrolyte_lle` remains closed until the final admission
child; each intermediate child produces a retained checker with `complete: true`
for its own gate and names the remaining electrolyte gates.
**Owner:** M4 equilibrium package owner.
**Interface:** GitHub issue dependencies, local issue mirrors, M4 README,
benchmark registry rows, validation checkers, and native diagnostics.
**Cutover:** Direct #191 implementation is displaced by the child sequence
continuing with #312, #313, and #314.
**Replaced Path:** The stale generic parent plan is replaced with explicit
child-gate orchestration so workers do not treat readiness or TPD screening as
production electrolyte support.
**Evidence:** Closed child issue mirrors, checker JSON, targeted contract tests,
registry evidence, dependency-readiness receipts, and PR merge records.
**Acceptance Proof:** #191 acceptance is proven only when all electrolyte child
gates are closed and the public electrolyte route admission checker passes with
source-backed validation and postsolve certification.
**Stop Criteria:** Stop if a child attempts to admit public electrolyte routes
before Stage III and postsolve evidence, compares charged species by raw
single-ion chemical potentials, or uses downstream case-study metrics as
upstream package validation.
**Avoid:** Do not add reactive electrolyte routes, parameter-regression work,
release claims, or public admission before the required proof gates.
**Risk:** The existing #302 negative TPD candidate can be mistaken for full
HELD2; every child and tracker update must keep screening, phase discovery,
refinement, certification, and admission separate.

## Implementation Boundaries

**Files To Create:** Child plans and issue mirrors for unresolved #191 gates.
**Files To Modify:** `docs/superpowers/issues/2026-05-30-m4-equilibrium-issue-0191-prove-electrolyte-gfpe-and-held2-0-validation-gates.md`, `docs/superpowers/milestones/M4-equilibrium/README.md`, `docs/superpowers/milestones/M4-equilibrium/registries/equilibrium-benchmark-registry.yaml`, and child-owned native/checker/test files.
**Files To Avoid:** Regression package files, downstream repositories, public
electrolyte route maps before the admission child, and provider EOS internals
unless a child issue explicitly scopes provider receipt consumption.
**Source Of Truth:** #191 source spec, M4 GFPE doctrine, Stage 14/15 electrolyte
plan, local HELD2 paper markdown, and closed child issue mirrors #269/#300/#302.
**Read Path:** Read source fixture readiness through
`check_electrolyte_gfpe_gate.py`, readiness through
`check_electrolyte_held2_readiness.py`, TPD screening through
`check_electrolyte_tpd_gate.py`, and GitHub dependency state through native
issue dependencies.
**Write Path:** Update parent issue mirrors and M4 docs after each child issue
is created or closed; write implementation code only inside the active child
scope.
**Integration Points:** Native phase-discovery diagnostics, checker CLIs,
activation capability rows, benchmark registry rows, and GitHub dependency
readiness automation.
**Migration Or Cutover:** As each child opens, #191 carries `status:blocked`;
after a child closes, dependency readiness either exposes the next child or
returns #191 to ready for planning.
**Replaced Path Handling:** Remove direct #191 execution language and keep the
active child plan as the executable entry point.
**Acceptance Proof Gate:** Run the active child proof oracle and docs validation
before merging any tracker or implementation PR.

## HELD2 Adoption Checkpoint Sequence

The #191 parent closes only when each checkpoint has its own retained checker,
focused tests, and tracker evidence:

- Source and readiness checkpoints: #269, #300, and #302 remain prerequisite
  evidence for source fixtures, reduced electroneutral variables, Born SSM/DS
  derivatives, and charge-neutral TPD screening.
- #306 phase-discovery checkpoint: retained diagnostics are counterion-pair
  matrix rank, reduced-coordinate lift/back-lift residuals, finite TPD
  candidate metrics, pair-based mean-ionic residual bookkeeping, closed public
  routes, and a Stage III handoff record.
- #312 Stage III refinement checkpoint: consume the #306 candidate set and solve the
  electrolyte reduced-variable phase-set equations with exact residual
  derivative receipts.
- #313 postsolve checkpoint: certify explicit-ion material reconstruction,
  per-phase charge balance, neutral transfer, mean-ionic transfer, pressure
  consistency, phase amounts, and domain margins.
- #314 public admission checkpoint: consume all prior checkers and expose only the
  certified electrolyte route surface.

## Acceptance Criteria

- [ ] #312 or its successor child blocks #191 until the current electrolyte
  gate is closed.
- [ ] Parent #191 docs list closed children #269, #300, #302, and #306 as
  historical provenance only.
- [ ] Parent #191 docs list open child #312 as the current Stage III
  reduced-variable refinement gate.
- [ ] #313 postsolve and #314 admission gates remain separate and blocked in
  order.
- [ ] The parent tracker keeps the HELD2 adoption checkpoint sequence current
  as each child opens or closes.
- [ ] Public electrolyte route claims stay closed until the final admission
  child closes.

## Non-Goals

- No direct implementation under #191.
- No public `electrolyte_lle` admission from readiness, Born, TPD, or phase
  discovery gates.
- No reactive, CE, CPE, regression, downstream, release, or publication claim.

## Tasks

### Task 1: Keep The Parent Tracker Correct

**Use Cases:**
- A resolver needs #191 to show the active child blocker rather than stale
  generic acceptance text.
- A reviewer needs acceptance evidence and cutover language that separates
  screening, phase discovery, refinement, certification, and route admission.
- Dependency readiness needs a concrete GitHub blocker before it can move #191
  between blocked and ready states.

**Files:**
- `docs/superpowers/issues/2026-05-30-m4-equilibrium-issue-0191-prove-electrolyte-gfpe-and-held2-0-validation-gates.md`
- `docs/superpowers/milestones/M4-equilibrium/README.md`

- [ ] Update #191 when each child opens or closes.
- [ ] Keep labels/readiness mirrored from GitHub.
- [ ] Keep closed child evidence in provenance sections, not active blockers.

### Task 2: Resolve The Active Child Gate

**Use Cases:**
- A worker needs one executable child plan with concrete files, proof oracle,
  and acceptance evidence.
- The child must replace an unresolved parent phrase with native checker
  evidence before #191 can progress.
- The child must state the old path it displaces and the route surfaces it keeps
  closed.

**Files:**
- Active child source plan.
- Active child issue mirror.
- Child-owned implementation files.

- [ ] Start from the active child plan.
- [ ] Run its proof oracle before PR creation.
- [ ] Merge only after the child acceptance criteria pass.

### Task 3: Reconcile Dependency Readiness After Each Merge

**Use Cases:**
- GitHub dependencies must reflect whether #191 is still blocked by an open
  child.
- Local M4 docs need visible acceptance evidence after merge, not only GitHub
  state.
- The next child should be created only after the previous proof has closed its
  gate.

**Files:**
- `docs/superpowers/issues/**`
- `docs/superpowers/milestones/M4-equilibrium/README.md`
- `scripts/dev/update_issue_dependency_readiness.py`

- [ ] Run dependency readiness sync after a child closes.
- [ ] If another child is needed, create it and block #191 with it.
- [ ] If no child remains, prepare final #191 closure evidence.

## Proof Oracle

```powershell
pwsh.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\validate-plan-task-use-cases.ps1 -PlanPath docs\superpowers\plans\2026-05-30-m4-equilibrium-issue-0191-prove-electrolyte-gfpe-and-held2-0-validation-gates-plan.md
pwsh.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\validate-plan-outcome-proof.ps1 -PlanPath docs\superpowers\plans\2026-05-30-m4-equilibrium-issue-0191-prove-electrolyte-gfpe-and-held2-0-validation-gates-plan.md
uv run --no-sync python scripts/dev/update_issue_dependency_readiness.py --reconcile --dry-run --json
uv run --no-sync python scripts/dev/validate_project.py docs
pwsh.exe -NoProfile -ExecutionPolicy Bypass -File "$env:USERPROFILE\.codex\hooks\codex-cleanup.ps1" -RepoRoot .
```
