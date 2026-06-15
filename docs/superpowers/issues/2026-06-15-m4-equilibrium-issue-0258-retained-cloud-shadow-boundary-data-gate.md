---
issue: 258
title: "M4: add retained cloud/shadow boundary data gate"
url: "https://github.com/ePC-SAFT/ePC-SAFT/issues/258"
state: "open"
milestone: "M4 - Equilibrium"
project: "ePC-SAFT Roadmap"
package: "equilibrium"
capability: "lle"
backend: "Ipopt"
readiness: "ready"
release_target: "equilibrium-0.x"
source_spec: "docs/superpowers/specs/2026-05-30-m4-equilibrium-issue-0189-derive-boundary-workflows-and-generalized-phase-set-pe-from-neutral-gfpe.md"
source_plan: "docs/superpowers/plans/2026-06-15-m4-equilibrium-issue-0189-cloud-shadow-boundary-gate-plan.md"
afk_hitl: "AFK"
branch: codex/issue-0258-retained-cloud-shadow-boundary-data-gate
parent_issue: 189
last_synced: "2026-06-15"
---

# M4: add retained cloud/shadow boundary data gate

**GitHub Issue:** https://github.com/ePC-SAFT/ePC-SAFT/issues/258
**GitHub Milestone:** M4 - Equilibrium
**Issue Type:** feature
**Source Spec:** docs/superpowers/specs/2026-05-30-m4-equilibrium-issue-0189-derive-boundary-workflows-and-generalized-phase-set-pe-from-neutral-gfpe.md
**Source Plan:** docs/superpowers/plans/2026-06-15-m4-equilibrium-issue-0189-cloud-shadow-boundary-gate-plan.md
Parent Issue: https://github.com/ePC-SAFT/ePC-SAFT/issues/189
Branch: codex/issue-0258-retained-cloud-shadow-boundary-data-gate
AFK/HITL: AFK
**Classification:** AFK
**Labels:** enhancement, native, solver, docs, validation, equilibrium, area:equilibrium, backend:ipopt, status:ready, agent-ready, type:feature
**Goal Command:** /goal Resolve issue 258: implement the retained cloud/shadow boundary data gate from docs/superpowers/plans/2026-06-15-m4-equilibrium-issue-0189-cloud-shadow-boundary-gate-plan.md, preserve planned-only native route admission, and open a PR.
**Execution Mode:** Ask at runtime
**Worktree Policy:** Native Codex worktree thread first
**Integration Policy:** Worker PR reviewed by main thread
**TDD Policy:** Required
**Parallelization Plan:** None
**Reviewer Role:** Main thread orchestrator
**Script Gate Mode:** Safety only

## Project Merge

**Merge Owner:** Main thread orchestrator
**Merge Gate:** Native UI approval required
**Merge Policy:** Repo default
**Worktree Cleanup Policy:** Remove owned worktree after merge
**Orchestrator Wakeup Policy:** Worker handoff or bounded heartbeat

## What To Build

Add the next #189 child gate for cloud/shadow derived-boundary readiness. This
issue proves retained source-data readiness from the Matsuda/NIST
perfluorohexane + hexane neutral LLE fixture and keeps native cloud/shadow
route admission closed until a separate solver route gate exists.

## Parent

- Parent issue: #189
- Source plan: docs/superpowers/plans/2026-06-15-m4-equilibrium-issue-0189-cloud-shadow-boundary-gate-plan.md
- Prior children: #252 internal generalized phase-set diagnostics; #256 bubble/dew boundary traces.

## Acceptance Criteria

- [x] `check_boundary_workflows.py --json --cloud-shadow-gate --require-cloud-shadow-gate` completes the retained source-data gate.
- [x] The gate verifies 14 Matsuda/NIST cloud-point rows and one paired cloud-shadow source branch for perfluorohexane + hexane.
- [x] The gate emits separate route-admission blockers for native cloud and shadow route absence.
- [x] Cloud/shadow registry rows keep no runtime routes and do not claim native route support.
- [x] Existing bubble/dew boundary trace and neutral LLE showcase checks remain green.
- [x] #189 remains open after this child unless every umbrella gate is separately complete.

## Blocked By

- None

## Non-Goals

- No native cloud or shadow route implementation.
- No public route admission.
- No associating, electrolyte, reactive, CE, CPE, LLLE, or VLLE admission.
- No closure of #189 from this child alone.

## Proof Oracle

```powershell
uv run --no-sync python run_pytest.py tests/native/contracts/test_cloud_shadow_boundary_gate_checker.py tests/native/contracts/test_boundary_workflow_checker.py tests/native/contracts/test_generalized_equilibrium_registry.py -q
uv run --no-sync python scripts/validation/check_boundary_workflows.py --json --contracts-only
uv run --no-sync python scripts/validation/check_boundary_workflows.py --json --cloud-shadow-gate --require-cloud-shadow-gate
uv run --no-sync python scripts/validation/check_neutral_lle_showcase.py --case-dir data/reference/equilibrium_benchmarks/neutral_lle/matsuda_2011_pfhexane_hexane --json --require-complete
uv run --no-sync python scripts/dev/validate_project.py docs
pwsh.exe -NoProfile -ExecutionPolicy Bypass -File "$env:USERPROFILE\.codex\hooks\codex-cleanup.ps1" -RepoRoot .
```

## Validation Evidence

Recorded on 2026-06-15 from branch
`codex/issue-0258-retained-cloud-shadow-boundary-data-gate`.

- `uv run --no-sync python run_pytest.py tests/native/contracts/test_cloud_shadow_boundary_gate_checker.py tests/native/contracts/test_boundary_workflow_checker.py tests/native/contracts/test_generalized_equilibrium_registry.py -q` passed: 27 tests.
- `uv run --no-sync python scripts/validation/check_boundary_workflows.py --json --contracts-only` passed with no blockers; cloud and shadow remained `planned_not_executable` with empty runtime routes.
- `uv run --no-sync python scripts/validation/check_boundary_workflows.py --json --cloud-shadow-gate --require-cloud-shadow-gate` passed with `complete: true`, 14 binodal rows, one paired branch row, empty source-data blockers, and route-admission blockers `native_cloud_point_route_absent` and `native_shadow_point_route_absent`.
- `uv run --no-sync python scripts/validation/check_neutral_lle_showcase.py --case-dir data/reference/equilibrium_benchmarks/neutral_lle/matsuda_2011_pfhexane_hexane --json --require-complete` passed with `complete: true`, 14 source binodal rows, one tie-line, and no fixture blockers.
- `uv run --no-sync python scripts/dev/validate_project.py docs` passed.
- `pwsh.exe -NoProfile -ExecutionPolicy Bypass -File "$env:USERPROFILE\.codex\hooks\codex-cleanup.ps1" -RepoRoot .` passed with no matching leftover Codex processes.

## GitHub Body Text

Add the next #189 child gate for cloud/shadow derived-boundary readiness. This
issue proves retained source-data readiness from the Matsuda/NIST
perfluorohexane + hexane neutral LLE fixture and keeps native cloud/shadow
route admission closed until a separate solver route gate exists.

Source plan:
docs/superpowers/plans/2026-06-15-m4-equilibrium-issue-0189-cloud-shadow-boundary-gate-plan.md

Classification:
AFK and ready. Scope, acceptance criteria, proof oracle, non-goals, and route
admission boundaries are explicit in the source plan and this mirror.

Outcome:
Cloud/shadow gets a retained source-data gate with named future route-admission
blockers. This advances #189 but does not close #189 or admit native
cloud/shadow routes.

## Tracker Metadata

- Milestone: `M4 - Equilibrium`
- Package: `equilibrium`
- Capability: `lle`
- Backend: `Ipopt`
- Readiness: `ready`
- AFK/HITL: `AFK`
- Release target: `equilibrium-0.x`
- Labels: `enhancement, agent-ready, native, solver, docs, validation, equilibrium, area:equilibrium, backend:ipopt, status:ready, type:feature`
