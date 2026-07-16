# Prove Electrolyte GFPE And HELD2.0 Validation Gates Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> `superpowers:subagent-driven-development` or `superpowers:executing-plans` to
> implement child issues task-by-task. This parent plan is an umbrella plan; do
> not open public electrolyte routes directly from #191.

**Goal:** Resolve GitHub issue #191 by closing the electrolyte HELD2 child gates
in order: counterion-pair phase discovery (#306), Stage III reduced-variable
refinement (#312), postsolve certification (#313), representative public route
admission (#314), and full Khudaida figure-level model reproduction plus
broader HELD2 flash scenario validation (#320), followed by full HELD2-style
public-route phase discovery and final registry/capability admission
(#343 through #350).

**Architecture:** #191 is the electrolyte GFPE umbrella for
`packages/epcsaft-equilibrium`. Existing children prove source data, reduced
electroneutral variables, Born SSM/DS derivative receipts, charge-neutral TPD
screening, HELD2 counterion-pair phase discovery, Stage III refinement,
postsolve certification, and representative public route admission. #320 proved
Perdomo/Figiel HELD2 flash behavior through the public package route. #343
then closed the full HELD2-style public-route phase-discovery tracker after
#344 through #350 retained doctrine, continuous reduced-electroneutral TPD,
Stage I stability, Stage II dual discovery, public-route orchestration,
scenario validation, and registry/capability admission evidence. Final #191
closeout re-runs the retained public-route oracle and closes the parent only if
the evidence remains executable.

**Tech Stack:** C++ equilibrium native core, `NlpProblem`, Ipopt,
`VariableTransform`, pybind11 bindings, Python validation checkers, pytest
contracts through `run_pytest.py`, M4 issue mirrors, M4 registry evidence,
GitHub dependency readiness.

---

## Intake

- Source Spec: `docs/superpowers/specs/2026-05-30-m4-equilibrium-issue-0191-prove-electrolyte-gfpe-and-held2-0-validation-gates.md`
- Source Issue: `docs/superpowers/issues/2026-05-30-m4-equilibrium-issue-0191-prove-electrolyte-gfpe-and-held2-0-validation-gates.md`
- Source Plan: `docs/superpowers/plans/2026-05-30-m4-equilibrium-issue-0191-prove-electrolyte-gfpe-and-held2-0-validation-gates-plan.md`
- Closed Validation Child: `https://github.com/ePC-SAFT/ePC-SAFT/issues/320`
- Closed Full-Discovery Tracker: `https://github.com/ePC-SAFT/ePC-SAFT/issues/343`
- Final Closeout Issue: `https://github.com/ePC-SAFT/ePC-SAFT/issues/191`
- Milestone: `M4 - Equilibrium`
- AFK/HITL: `HITL`

## Outcome Proof

**Intent:** Keep #191 as the parent acceptance gate for electrolyte GFPE while
forcing implementation through PR-sized child gates.
**Current Behavior:** #269, #300, #302, #306, #312, #313, #314, #320, #343, and
#344 through #350 are closed. The remaining #191 work is proof/sync closeout:
the full Figiel validator command must run as written on Windows and parent
docs must no longer describe closed children as active blockers.
**Expected Outcome:** #191 closes after the final proof/sync PR proves the
Figiel validation command, the public electrolyte admission checker, the HELD2
public-route scenario checker, focused package tests, and docs validation all
pass from the public package route.
**Target Output:** `electrolyte_lle` remains scoped to the exact behavior proven
by retained checkers; final closeout requires Perdomo/Figiel validation,
full-discovery Stage I/II/III evidence, exact-Hessian route diagnostics, and
closed #320/#343/#344-#350 provenance.
**Owner:** M4 equilibrium package owner.
**Interface:** GitHub issue dependencies, local issue mirrors, M4 README,
benchmark registry rows, validation checkers, and native diagnostics.
**Cutover:** Direct #191 implementation is displaced by the completed child
sequence; this plan now owns only final closeout proof and tracker sync.
**Replaced Path:** The stale parent plan text that named #320 or #343 as active
blockers is replaced with closed-provenance closeout evidence so workers do not
treat readiness, TPD screening, or representative admission alone as production
electrolyte support.
**Evidence:** Closed child issue mirrors, checker JSON, targeted contract tests,
`NlpProblem` sparse derivative receipts, Ipopt option/profile diagnostics, Born
SSM+DS active-block exact-Hessian receipts, reduced-coordinate lift/back-lift
diagnostics, registry evidence, dependency-readiness receipts, and PR merge
records.
**Acceptance Proof:** #191 acceptance is proven when all electrolyte child gates
are closed, the final public-route proof oracle passes, the Figiel validator
does not self-lock the editable native extension on Windows, and parent
docs/GitHub text show #320 and #343 as closed provenance.
**Stop Criteria:** Stop if the final oracle fails, if a child admits public
electrolyte routes before Stage III and postsolve evidence, compares charged
species by raw single-ion chemical potentials, bypasses `NlpProblem`/Ipopt,
lacks Born SSM+DS active-block exact-Hessian evidence, or uses downstream
case-study metrics as upstream package validation.
**Avoid:** Do not add reactive electrolyte routes, parameter-regression work,
release claims, or public admission before the required proof gates.
**Risk:** The existing #302 negative TPD candidate can be mistaken for full
HELD2; every child and tracker update must keep screening, phase discovery,
refinement, certification, and admission separate.

## Implementation Boundaries

**Files To Create:** Focused regression tests for the final closeout blocker, if needed.
**Files To Modify:** `analyses/paper_validation/2025_figiel/scripts/validate_figure_data.py`, focused regression tests, `docs/superpowers/issues/2026-05-30-m4-equilibrium-issue-0191-prove-electrolyte-gfpe-and-held2-0-validation-gates.md`, `docs/superpowers/plans/2026-05-30-m4-equilibrium-issue-0191-prove-electrolyte-gfpe-and-held2-0-validation-gates-plan.md`, and `docs/superpowers/milestones/M4-equilibrium/README.md`.
**Files To Avoid:** Regression package files, downstream repositories, public
electrolyte route maps before the admission child, and provider EOS internals
unless a child issue explicitly scopes provider receipt consumption.
**Source Of Truth:** #191 source spec, M4 GFPE doctrine, Stage 14/15 electrolyte
plan, Perdomo 2025 HELD2 paper markdown, Ascani 2022 electrolyte methodology,
Khudaida 2026 retained source data, and closed child issue mirrors
#269/#300/#302.
**Read Path:** Read source fixture readiness through
`check_electrolyte_gfpe_gate.py`, readiness through
`check_electrolyte_held2_readiness.py`, TPD screening through
`check_electrolyte_tpd_gate.py`, and GitHub dependency state through native
issue dependencies.
**Write Path:** Update parent issue mirrors and M4 docs after each child issue
is created or closed; write implementation code only inside the active child
scope.
**Integration Points:** Native phase-discovery diagnostics, `NlpProblem` sparse
derivative metadata, `VariableTransform` reduced-coordinate lift/back-lift,
Ipopt exact-Hessian profile diagnostics, checker CLIs, activation capability
rows, benchmark registry rows, and GitHub dependency readiness automation.
**Migration Or Cutover:** #191 is ready after dependency readiness confirms all
native blockers are closed.
**Replaced Path Handling:** Remove active-child wording and keep closed child
proof as parent provenance.
**Acceptance Proof Gate:** Run the final #191 proof oracle and docs validation
before merging the closeout PR.

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
- #314 public admission checkpoint: consume all prior checkers and expose only
  the certified representative electrolyte route surface.
- #320 Perdomo/Figiel checkpoint: closed by PR #341 with retained HELD2 flash
  validation through the public package route.
- #343 full-discovery checkpoint: closed by PR #359 after #344 through #350
  retained doctrine, continuous reduced-electroneutral TPD, Stage I stability,
  Stage II dual discovery, public-route orchestration, scenario validation, and
  registry/capability proof.

## Acceptance Criteria

- [x] #320 closed after Perdomo/Figiel HELD2 flash scenario validation passed.
- [x] #320 accepted rows prove the shared native `NlpProblem`/Ipopt
  exact-Hessian route path, fixed sparse derivative receipts, route-owned
  transforms/scaling, and Ipopt postsolve diagnostics.
- [x] #320 retains Born SSM+DS active-block exact-Hessian evidence, reduced
  electroneutral lift/back-lift, and projected electrochemical or modified
  mean-ionic residuals.
- [x] #343 closed after #344 through #350 retained the full HELD2-style
  public-route discovery chain and capability evidence.
- [x] Parent #191 docs list closed children #269, #300, #302, #306, #312, #313,
  and #314 as
  historical provenance only.
- [x] Parent #191 docs list closed #320 and #343 provenance instead of active
  blockers.
- [x] The parent tracker keeps the HELD2 adoption checkpoint sequence current
  as each child opens or closes.
- [x] Public electrolyte route claims stay narrowed until #320 proves the full
  retained source-backed model-reproduction gate.

## Non-Goals

- No direct implementation under #191.
- No final `electrolyte_lle` production closeout from representative route
  admission alone.
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

### Task 2: Confirm The Closed Child Chain

**Use Cases:**
- A resolver needs #320, #343, and #344 through #350 shown as closed provenance
  before #191 can close.
- The final closeout must replace unresolved parent phrases with native checker
  evidence.
- The parent must state the old path it displaces and the route surfaces it
  keeps closed.

**Files:**
- #191 source plan.
- #191 issue mirror.
- M4 README.

- [x] Confirm #320, #343, and #344 through #350 are closed.
- [ ] Run the #191 final proof oracle before PR creation.
- [ ] Merge only after the final acceptance criteria pass.

## Proof Oracle

```powershell
uv run --no-sync python scripts/validate_plan_task_use_cases.py --plan-path docs/superpowers/plans/2026-05-30-m4-equilibrium-issue-0191-prove-electrolyte-gfpe-and-held2-0-validation-gates-plan.md
uv run --no-sync python scripts/validate_plan_outcome_proof.py --plan-path docs/superpowers/plans/2026-05-30-m4-equilibrium-issue-0191-prove-electrolyte-gfpe-and-held2-0-validation-gates-plan.md
uv run --no-sync python analyses\paper_validation\2025_figiel\scripts\validate_figure_data.py
uv run --no-sync python scripts\validation\check_electrolyte_public_admission.py --json --require-held2-stage-ii --require-stage-iii --require-postsolve-certification --require-public-admission --require-complete
uv run --no-sync python scripts\validation\check_electrolyte_held2_public_route_scenarios.py --json --require-complete
uv run --no-sync python -m pytest packages\epcsaft-equilibrium\tests -k "electrolyte and held2 and flash"
uv run --no-sync python scripts/dev/validate_project.py docs
pwsh.exe -NoProfile -ExecutionPolicy Bypass -File "$env:USERPROFILE\.codex\hooks\codex-cleanup.ps1" -RepoRoot .
```
