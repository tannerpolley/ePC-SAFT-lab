# HELD2 Public Route Phase Discovery Full Adoption Plan

## Outcome Proof

**Intent:** Convert the remaining long-term HELD2 electrolyte phase-discovery
plan into concrete M4 issue slices that can be implemented one PR at a time.

**Current Behavior:** M4 has closed prerequisite gates for electrolyte
readiness, deterministic TPD screening, HELD2 diagnostics, Stage III local
refinement, postsolve certification, and representative public admission, but
there is no tracking issue or implementation sequence for full HELD2-style
continuous phase discovery in the public package route.

**Expected Outcome:** The missing full HELD2 public-route adoption work is
represented by a source-backed spec, a validated plan, GitHub issues with
native dependency links, and local issue mirrors that preserve the exact
implementation and validation boundaries.

**Target Output:** A tracking issue plus implementation issues that cover the
full path from HELD2 reduced TPD minimization through public route admission.

**Owner:** `packages/epcsaft-equilibrium`.

**Interface:** Native HELD2 discovery diagnostics, `NlpProblem`/Ipopt Stage III
refinement, public `Equilibrium(..., route="electrolyte_lle")` orchestration,
validation scripts, registry rows, and capability docs.

**Cutover:** Keep #314 and #320 as retained partial evidence. Add the new
tracking issue as the explicit full-implementation blocker for #191.

**Replaced Path:** Representative public admission, retained diagnostics, or
boundary-only residual solves treated as full HELD2 production discovery.

**Evidence:** The plan names each missing algorithm stage, its files, its
public-route cutover point, and proof commands, and the GitHub dependency graph
keeps #191 blocked until the final capability-admission slice closes.

**Acceptance Proof:** Each slice has a proof oracle. The final slice admits
only the public route behavior proven by the full validation ladder.

**Stop Criteria:** Stop if a slice requires M5 parameter regression, reactive
chemistry, unavailable literature data, raw single-ion equality, hidden charge
clipping, or public capability claims broader than retained evidence.

**Avoid:** Do not close #191 from issue metadata alone; do not claim full
Khudaida model reproduction without M5 parameter evidence; do not replace
HELD2 discovery with a residual-only local solve.

**Risk:** Splitting too coarsely would hide algorithm coverage gaps; splitting
too finely would produce tracker-only issues without an executable public-route
cutover.

## Implementation Boundaries

**Files To Create:** This spec, this plan, and local mirrors for the new
tracking issue and issue slices under `docs/superpowers/issues/` after GitHub
numbers are assigned.
**Files To Modify:** `docs/superpowers/milestones/M4-equilibrium/README.md`,
the #191 local mirror, and this plan's issue-number references after issue
creation.
**Files To Avoid:** Native solver implementation files, package runtime files,
registry rows that imply completed HELD2 public-route capability, M5 regression
files, downstream project files, and generated validation artifacts.
**Source Of Truth:** `docs/superpowers/PROJECT_CONTEXT.md`, the M4 GFPE
milestone doctrine, Stage 15 in the M4 stage-by-stage plan, the Perdomo 2025
HELD2 paper markdown, #191, #300, #302, #306, #312, #313, #314, #320, and #338.
**Read Path:** Read the current issue mirrors, M4 milestone docs, relevant
GitHub issue states, and validation scripts before publishing issue bodies.
**Write Path:** Write only source-backed docs, plans, issue mirrors, issue
bodies, and dependency metadata needed to make the implementation path
actionable.
**Integration Points:** GitHub issue dependencies, local issue mirrors, the M4
README dependency summary, and #191's blocker list.
**Migration Or Cutover:** Keep #314 and #320 as partial evidence, add a new
full-implementation tracking issue as the public-route HELD2 blocker, and do
not move #191 to ready until the final capability-admission issue closes.
**Replaced Path Handling:** Explicitly mark deterministic screening,
diagnostic-only discovery, representative route admission, and boundary
residual solves as evidence prerequisites rather than full HELD2 production
discovery.
**Acceptance Proof Gate:** The plan validators pass, GitHub issues exist with
native dependencies, local mirrors name issue numbers and proof oracles, and
docs validation passes without broadening capability claims.

## Coverage Audit

Existing gates cover prerequisites but not full production discovery:

- #300: readiness and Born exactness.
- #302: charge-neutral TPD screening, not full HELD2 discovery.
- #306: reduced-coordinate phase-discovery diagnostics, not public-route
  candidate generation.
- #312: Stage III local refinement proof.
- #313: postsolve certification proof.
- #314: representative public route admission.
- #320: Perdomo/Figiel boundary validation and retained scenario evidence.

Missing implementation coverage is the production discovery orchestrator and
its validation matrix.

## Issue Slices

### Slice 0: Tracking Issue (#343)

Title: `M4: implement full HELD2-style electrolyte phase discovery in the public route`

GitHub: https://github.com/ePC-SAFT/ePC-SAFT/issues/343

Purpose: parent the new implementation sequence and block #191 until all child
slices pass.

Proof: all child issues closed, public route validation ladder passes, #191
mirror updated with closed provenance.

### Slice 1: Doctrine And Validation Matrix (#344)

Title: `M4: define HELD2 public-route doctrine and validation matrix`

GitHub: https://github.com/ePC-SAFT/ePC-SAFT/issues/344

Build:

- Convert the spec into route-level equations, candidate lifecycle states, and
  validation cases.
- Define stable/unstable/boundary/phase-label/common-ion/mixed-salt fixtures.
- Record exact residual families, scaling, and acceptance tolerances.

Proof:

```powershell
uv run --no-sync python scripts\dev\validate_project.py docs
```

### Slice 2: Continuous Reduced-Electroneutral TPD Minimizer (#345)

Title: `M4: implement electrolyte continuous TPD minimizer in reduced coordinates`

GitHub: https://github.com/ePC-SAFT/ePC-SAFT/issues/345

Build:

- Add native reduced electroneutral volume-composition trial phase variables.
- Use exact phase-block derivatives where available.
- Return start-by-start convergence, residual, bound, and charge diagnostics.
- Keep public route admission closed.

Proof:

```powershell
uv run --no-sync python -m pytest packages\epcsaft-equilibrium\tests -k "electrolyte and held2 and continuous and tpd" -q
uv run --no-sync python scripts\validation\check_electrolyte_held2_continuous_tpd.py --json --require-complete
```

### Slice 3: Stage I Stability Certificate (#346)

Title: `M4: add HELD2 Stage I electrolyte stability certificate`

GitHub: https://github.com/ePC-SAFT/ePC-SAFT/issues/346

Build:

- Consume Slice 2 minimizer output.
- Distinguish stable feed, unstable feed, incomplete minimization, and
  numerically suspect starts.
- Retain negative TPD and no-negative-TPD certificates.
- Reject single-start or deterministic-screen-only claims.

Proof:

```powershell
uv run --no-sync python scripts\validation\check_electrolyte_held2_stage_i.py --json --require-continuous-tpd --require-complete
uv run --no-sync python -m pytest packages\epcsaft-equilibrium\tests -k "electrolyte and held2 and stage_i" -q
```

### Slice 4: Stage II Dual/Cutting-Plane Discovery (#347)

Title: `M4: implement HELD2 Stage II electrolyte dual phase discovery`

GitHub: https://github.com/ePC-SAFT/ePC-SAFT/issues/347

Build:

- Add dual/cutting-plane candidate discovery with lower and upper bounds.
- Store candidate phase sets, bound gaps, replay payloads, and rejected
  candidate reasons.
- Support neutral-only, single-salt, common-ion, and mixed-salt reduced bases.
- Keep Stage III and public route cutover separate.

Proof:

```powershell
uv run --no-sync python scripts\validation\check_electrolyte_held2_stage_ii.py --json --require-stage-i --require-bound-gap --require-replay --require-complete
uv run --no-sync python -m pytest packages\epcsaft-equilibrium\tests -k "electrolyte and held2 and stage_ii" -q
```

### Slice 5: Public Route Orchestration Through Stage III (#348)

Title: `M4: integrate HELD2 discovery into electrolyte public route orchestration`

GitHub: https://github.com/ePC-SAFT/ePC-SAFT/issues/348

Build:

- Route `Equilibrium(..., route="electrolyte_lle")` through Stage I/II
  discovery before Stage III refinement when the electrolyte family requires
  discovery.
- Ensure Stage III consumes the Stage II replay payload.
- Preserve exact-Hessian receipts and postsolve certification.
- Expose result diagnostics without broadening unsupported routes.

Proof:

```powershell
uv run --no-sync python scripts\validation\check_electrolyte_public_admission.py --json --require-held2-stage-ii --require-stage-iii --require-postsolve-certification --require-public-admission --require-complete
uv run --no-sync python -m pytest packages\epcsaft-equilibrium\tests -k "electrolyte and held2 and public and route" -q
```

### Slice 6: Multi-Scenario Validation Ladder (#349)

Title: `M4: add HELD2 public-route scenario validation ladder`

GitHub: https://github.com/ePC-SAFT/ePC-SAFT/issues/349

Build:

- Add retained package tests for stable feeds, unstable feeds, boundary feeds,
  phase-label permutations, neutral-limit parity, common-ion systems, and
  mixed-salt systems.
- Keep Khudaida model reproduction separated from M4 algorithm proof when it
  requires M5 parameter regression.
- Retain plots or data snapshots only when model predictions are compared to
  literature data.

Proof:

```powershell
uv run --no-sync python scripts\validation\check_electrolyte_held2_public_route_scenarios.py --json --require-complete
uv run --no-sync python -m pytest packages\epcsaft-equilibrium\tests -k "electrolyte and held2 and scenario" -q
```

### Slice 7: Registry, Docs, And Capability Admission (#350)

Title: `M4: admit HELD2 public-route capability evidence after full validation`

GitHub: https://github.com/ePC-SAFT/ePC-SAFT/issues/350

Build:

- Update registry rows and capability docs only after Slice 6 passes.
- Mark which electrolyte route families are production exposed.
- Keep reactive, CE/CPE, regression, and unfitted Khudaida claims closed.
- Update #191 with closed child provenance.

Proof:

```powershell
uv run --no-sync python -m pytest tests\native\contracts\test_equilibrium_benchmark_registry.py tests\native\contracts\test_generalized_equilibrium_registry.py -q
uv run --no-sync python scripts\dev\validate_project.py docs
```

## Dependency Order

Tracking issue is blocked by Slices 1 through 7. Slice order is linear:

```text
#344 -> #345 -> #346 -> #347 -> #348 -> #349 -> #350
```

The tracking issue #343 blocks #191. M5 issue #338 remains separate and blocks only
claims that require Khudaida parameter regression.

## Publication Plan

- Publish the tracking issue first.
- Publish slices in dependency order.
- Add native GitHub `blocked_by` relationships.
- Add local issue mirrors after issue numbers are assigned.
- Update the M4 README and #191 mirror with the new blocker topology.

## Tasks

### Task 1: Validate Existing Coverage And Gap

**Use Cases:**
- A milestone reviewer needs source-backed evidence that the current long-term
  plan does not yet fully cover HELD2 public-route phase discovery.
- The new issue set must preserve the existing #314/#320 evidence while making
  clear that representative admission and boundary residual checks are not the
  final production discovery cutover.
- The acceptance evidence must identify the old partial proof paths that the
  new full-discovery plan replaces as the #191 blocker.

**Files:**
- `docs/superpowers/specs/2026-06-27-m4-equilibrium-held2-public-route-phase-discovery-full-adoption.md`
- `docs/superpowers/plans/2026-06-27-m4-equilibrium-held2-public-route-phase-discovery-full-adoption-plan.md`

- [x] Audit the M4 milestone, #191, #300, #302, #306, #312, #313, #314, #320,
  and #338 for current coverage.
- [x] Record the missing full HELD2 public-route discovery stages.
- [x] Define the replaced partial evidence paths and the acceptance proof gate.

### Task 2: Publish The Tracking Issue And Slice Issues

**Use Cases:**
- The GitHub tracker must contain real implementation issues, not only a local
  prose plan.
- Each issue must have an owner, public-route boundary, proof oracle, and stop
  criteria so future work can be implemented independently.
- Dependency readiness must be visible through native GitHub blockers rather
  than only in Markdown.

**Files:**
- GitHub Issues for `ePC-SAFT/ePC-SAFT`.
- `docs/superpowers/plans/2026-06-27-m4-equilibrium-held2-public-route-phase-discovery-full-adoption-plan.md`

- [x] Create the parent tracking issue.
- [x] Create Slice 1 through Slice 7 issues in dependency order.
- [x] Add GitHub `blocked_by` relationships so Slice 2 waits for Slice 1,
  continuing through Slice 7, and the parent tracking issue waits for the final
  validated capability-admission slice.

### Task 3: Add Local Issue Mirrors

**Use Cases:**
- Offline repo work must have the same issue titles, acceptance criteria, proof
  commands, and blockers as GitHub.
- Future implementers must be able to use the mirrors as the implementation
  source without re-discovering the HELD2 doctrine.
- The mirror files must preserve cutover and replaced-path handling so old
  diagnostic-only or representative-route paths cannot silently satisfy full
  acceptance.

**Files:**
- `docs/superpowers/issues/2026-06-27-m4-equilibrium-issue-0343-implement-full-held2-style-electrolyte-phase-discovery-in-the-public-route.md`
- `docs/superpowers/issues/2026-06-27-m4-equilibrium-issue-0344-define-held2-public-route-doctrine-and-validation-matrix.md`
- `docs/superpowers/issues/2026-06-27-m4-equilibrium-issue-0345-implement-electrolyte-continuous-tpd-minimizer-in-reduced-coordinates.md`
- `docs/superpowers/issues/2026-06-27-m4-equilibrium-issue-0346-add-held2-stage-i-electrolyte-stability-certificate.md`
- `docs/superpowers/issues/2026-06-27-m4-equilibrium-issue-0347-implement-held2-stage-ii-electrolyte-dual-phase-discovery.md`
- `docs/superpowers/issues/2026-06-27-m4-equilibrium-issue-0348-integrate-held2-discovery-into-electrolyte-public-route-orchestration.md`
- `docs/superpowers/issues/2026-06-27-m4-equilibrium-issue-0349-add-held2-public-route-scenario-validation-ladder.md`
- `docs/superpowers/issues/2026-06-27-m4-equilibrium-issue-0350-admit-held2-public-route-capability-evidence-after-full-validation.md`

- [x] Add one mirror per created issue after numbers are assigned.
- [x] Include proof oracle, acceptance criteria, dependency links, and stop
  criteria in every mirror.
- [x] Keep status labels consistent with the GitHub dependency state.

### Task 4: Update M4 Dependency Docs

**Use Cases:**
- #191 must show the new full HELD2 tracking issue as the remaining blocker
  instead of implying #314 or #320 completes full validation.
- The M4 milestone README must show the public-route phase-discovery chain and
  its relationship to #338 M5 regression work.
- Reviewers need evidence that the old partial paths were displaced by the new
  tracking topology without changing package behavior.

**Files:**
- `docs/superpowers/issues/2026-05-30-m4-equilibrium-issue-0191-prove-electrolyte-gfpe-and-held2-0-validation-gates.md`
- `docs/superpowers/milestones/M4-equilibrium/README.md`
- `docs/superpowers/plans/2026-06-27-m4-equilibrium-held2-public-route-phase-discovery-full-adoption-plan.md`

- [x] Update #191's mirror with the new tracking blocker and retain #320/#338
  provenance accurately.
- [x] Add the new HELD2 full-discovery chain to the M4 README.
- [x] Replace placeholder issue numbers in this plan with created numbers.

### Task 5: Verify And Handoff

**Use Cases:**
- The branch must retain machine-checkable acceptance evidence before the issue
  set is considered published.
- Documentation validation must prove the changed tracker files do not break
  repo links or capability claims.
- The cleanup hook must run so local task artifacts do not leak into the repo.

**Files:**
- All files changed by Tasks 1-4.

- [x] Run the plan validators.
- [x] Run docs validation.
- [x] Run `git diff --check`.
- [x] Run the repo cleanup hook and report any skipped validation.

## Proof Oracle

```powershell
pwsh.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\validate-plan-task-use-cases.ps1 -PlanPath docs\superpowers\plans\2026-06-27-m4-equilibrium-held2-public-route-phase-discovery-full-adoption-plan.md
pwsh.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\validate-plan-outcome-proof.ps1 -PlanPath docs\superpowers\plans\2026-06-27-m4-equilibrium-held2-public-route-phase-discovery-full-adoption-plan.md
uv run --no-sync python scripts\dev\validate_project.py docs
git diff --check
pwsh.exe -NoProfile -ExecutionPolicy Bypass -File "$env:USERPROFILE\.codex\hooks\codex-cleanup.ps1" -RepoRoot .
```
