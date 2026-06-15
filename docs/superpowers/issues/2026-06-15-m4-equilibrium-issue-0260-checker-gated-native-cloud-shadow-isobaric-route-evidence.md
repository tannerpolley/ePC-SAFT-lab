---
issue: 260
title: "M4: admit checker-gated native cloud/shadow isobaric route evidence"
url: "https://github.com/ePC-SAFT/ePC-SAFT/issues/260"
state: "open"
milestone: "M4 - Equilibrium"
project: "ePC-SAFT Roadmap"
package: "equilibrium"
capability: "lle"
backend: "Ipopt"
readiness: "ready"
release_target: "equilibrium-0.x"
source_spec: "docs/superpowers/specs/2026-05-30-m4-equilibrium-issue-0189-derive-boundary-workflows-and-generalized-phase-set-pe-from-neutral-gfpe.md"
source_plan: "docs/superpowers/plans/2026-06-15-m4-equilibrium-issue-0189-native-cloud-shadow-isobaric-route-admission-plan.md"
afk_hitl: "AFK"
branch: codex/issue-0260-checker-gated-native-cloud-shadow-isobaric-route-evidence
parent_issue: 189
last_synced: "2026-06-15"
---

# M4: admit checker-gated native cloud/shadow isobaric route evidence

**GitHub Issue:** https://github.com/ePC-SAFT/ePC-SAFT/issues/260
**GitHub Milestone:** M4 - Equilibrium
**Issue Type:** feature
**Source Spec:** docs/superpowers/specs/2026-05-30-m4-equilibrium-issue-0189-derive-boundary-workflows-and-generalized-phase-set-pe-from-neutral-gfpe.md
**Source Plan:** docs/superpowers/plans/2026-06-15-m4-equilibrium-issue-0189-native-cloud-shadow-isobaric-route-admission-plan.md
Parent Issue: https://github.com/ePC-SAFT/ePC-SAFT/issues/189
Branch: codex/issue-0260-checker-gated-native-cloud-shadow-isobaric-route-evidence
AFK/HITL: AFK
**Classification:** AFK
**Labels:** enhancement, agent-ready, native, solver, docs, validation, equilibrium, area:equilibrium, backend:ipopt, status:ready, type:feature
**Goal Command:** /goal Resolve issue 260: implement checker-gated native cloud/shadow isobaric route evidence from docs/superpowers/plans/2026-06-15-m4-equilibrium-issue-0189-native-cloud-shadow-isobaric-route-admission-plan.md while keeping public cloud/shadow route keys closed.
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

Add the next #189 child after #258: prove one checker-gated native isobaric
cloud/shadow route point from the retained Matsuda/NIST perfluorohexane +
hexane neutral LLE fixture. This issue converts the existing cloud/shadow
source-data gate into native route evidence while keeping public cloud/shadow
route keys closed.

## Parent

- Parent issue: #189
- Source plan: docs/superpowers/plans/2026-06-15-m4-equilibrium-issue-0189-native-cloud-shadow-isobaric-route-admission-plan.md
- Prior children: #252 internal generalized phase-set diagnostics; #256 bubble/dew boundary traces; #258 retained cloud/shadow source-data gate.

## Acceptance Criteria

- [ ] A private native cloud-temperature proof route solves the retained Matsuda paired branch at 101300 Pa with strict Ipopt convergence and exact-Hessian diagnostics.
- [ ] The route fixes parent-liquid composition `[0.2000, 0.8000]`, solves the boundary temperature, and reports matched shadow composition against `[0.5497, 0.4503]`.
- [ ] The checker reports solved/source temperature, temperature error, solved/source shadow composition, composition error, route residuals, seed attempts, solver status, application status, native receipt, and route trace metadata.
- [ ] The route proof satisfies source fixture metrics: temperature error <= 0.2 K, max shadow-composition error <= 0.02, material-balance residual <= 1.0e-8, pressure residual <= 0.001 Pa, ln-fugacity residual <= 1.0e-6, and phase distance >= 1.0e-6.
- [ ] The retained source-data gate from #258 remains green.
- [ ] Public cloud/shadow route strings remain closed in `Equilibrium` and activation/capability mirrors.
- [ ] Existing bubble/dew boundary trace validation, neutral LLE showcase validation, and registry tests remain green.
- [ ] #189 remains open after this child unless generalized phase-set completion and final public capability admission are separately proven.

## Blocked By

- None

## Non-Goals

- No public cloud/shadow route key exposure.
- No cloud-pressure route in this issue.
- No associating, electrolyte, reactive, CE, CPE, LLLE, or VLLE admission.
- No closure of #189 from this child alone.

## Proof Oracle

```powershell
uv run --no-sync python run_pytest.py tests/native/contracts/test_cloud_shadow_route_admission_checker.py tests/native/contracts/test_cloud_shadow_boundary_gate_checker.py tests/native/contracts/test_boundary_workflow_checker.py tests/native/contracts/test_generalized_equilibrium_registry.py -q
uv run --no-sync python run_pytest.py packages/epcsaft-equilibrium/tests/api/test_equilibrium.py packages/epcsaft-equilibrium/tests/contracts/test_activation_capabilities.py -q
uv run --no-sync python scripts/validation/check_boundary_workflows.py --json --contracts-only
uv run --no-sync python scripts/validation/check_boundary_workflows.py --json --cloud-shadow-gate --require-cloud-shadow-gate
uv run --no-sync python scripts/validation/check_boundary_workflows.py --json --run-cloud-shadow-route --require-cloud-shadow-route
uv run --no-sync python scripts/validation/check_neutral_lle_showcase.py --case-dir data/reference/equilibrium_benchmarks/neutral_lle/matsuda_2011_pfhexane_hexane --json --require-complete
uv run --no-sync python scripts/dev/validate_project.py docs
pwsh.exe -NoProfile -ExecutionPolicy Bypass -File "$env:USERPROFILE\.codex\hooks\codex-cleanup.ps1" -RepoRoot .
```

## GitHub Body Text

Add the next #189 child after #258: prove one checker-gated native isobaric
cloud/shadow route point from the retained Matsuda/NIST perfluorohexane +
hexane neutral LLE fixture. This issue converts the existing cloud/shadow
source-data gate into native route evidence while keeping public cloud/shadow
route keys closed.

Source plan:
docs/superpowers/plans/2026-06-15-m4-equilibrium-issue-0189-native-cloud-shadow-isobaric-route-admission-plan.md

Classification:
AFK and ready. Scope, acceptance criteria, proof oracle, non-goals, route
metrics, public-exposure boundary, and native freshness requirement are explicit
in the source plan and this mirror.

Outcome:
One checker-gated native isobaric cloud/shadow route point becomes evidence for
#189. Public cloud/shadow route-key exposure, generalized phase-set completion,
and final public capability admission remain separate gates.

## Tracker Metadata

- Milestone: `M4 - Equilibrium`
- Package: `equilibrium`
- Capability: `lle`
- Backend: `Ipopt`
- Readiness: `ready`
- AFK/HITL: `AFK`
- Release target: `equilibrium-0.x`
- Labels: `enhancement, agent-ready, native, solver, docs, validation, equilibrium, area:equilibrium, backend:ipopt, status:ready, type:feature`
