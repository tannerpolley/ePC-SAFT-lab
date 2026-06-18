---
issue: 260
title: "M4: admit checker-gated native cloud/shadow isobaric route evidence"
url: "https://github.com/ePC-SAFT/ePC-SAFT/issues/260"
state: "closed"
milestone: "M4 - Equilibrium"
project: "ePC-SAFT Roadmap"
package: "equilibrium"
capability: "lle"
backend: "Ipopt"
readiness: "closed"
release_target: "equilibrium-0.x"
source_spec: null
source_plan: null
afk_hitl: "AFK"
branch: null
last_synced: "2026-06-16"
---

# M4: admit checker-gated native cloud/shadow isobaric route evidence

**Mirror Retention:** Keep

**GitHub Issue:** https://github.com/ePC-SAFT/ePC-SAFT/issues/260
**GitHub Milestone:** M4 - Equilibrium
**Issue Type:** feature
**Source Spec:** docs/superpowers/specs/2026-05-30-m4-equilibrium-issue-0189-derive-boundary-workflows-and-generalized-phase-set-pe-from-neutral-gfpe.md
**Source Plan:** docs/superpowers/plans/2026-06-15-m4-equilibrium-issue-0189-native-cloud-shadow-isobaric-route-admission-plan.md
Parent Issue: https://github.com/ePC-SAFT/ePC-SAFT/issues/189
Branch: codex/issue-0260-checker-gated-native-cloud-shadow-isobaric-route-evidence
AFK/HITL: AFK
**Classification:** Closed
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
- [ ] The checker derives the current model-refined Matsuda parent branch from the certified `neutral_lle` source showcase, reports its source-parent error against `[0.2000, 0.8000]`, and uses that model-refined parent as the private cloud-temperature route input.
- [ ] The route solves the boundary temperature and reports matched shadow composition against the raw source shadow branch `[0.5497, 0.4503]`.
- [ ] The checker reports solved/source temperature, temperature error, source/model parent composition error, solved/source shadow composition, composition error, route residuals, seed attempts, solver status, application status, native receipt, and route trace metadata.
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
uv run --no-sync python run_pytest.py --allow-long-equilibrium-tests packages/epcsaft-equilibrium/tests/api/test_equilibrium.py packages/epcsaft-equilibrium/tests/contracts/test_activation_capabilities.py -q
uv run --no-sync python scripts/validation/check_boundary_workflows.py --json --contracts-only
uv run --no-sync python scripts/validation/check_boundary_workflows.py --json --cloud-shadow-gate --require-cloud-shadow-gate
uv run --no-sync python scripts/validation/check_boundary_workflows.py --json --run-cloud-shadow-route --require-cloud-shadow-route
uv run --no-sync python scripts/validation/check_neutral_lle_showcase.py --case-dir data/reference/equilibrium_benchmarks/neutral_lle/matsuda_2011_pfhexane_hexane --json --require-complete
uv run --no-sync python scripts/dev/validate_project.py docs
pwsh.exe -NoProfile -ExecutionPolicy Bypass -File "$env:USERPROFILE\.codex\hooks\codex-cleanup.ps1" -RepoRoot .
```

## Route Evidence Receipt

Fresh checker command:

```powershell
uv run --no-sync python scripts/validation/check_boundary_workflows.py --json --run-cloud-shadow-route --require-cloud-shadow-route
```

Measured result:

- Status: `native_route_complete`
- Public route admission: `closed`
- Solver status: `success`
- Application status: `solve_succeeded`
- Source temperature: `293.895 K`
- Solved cloud temperature: `293.8950027132599 K`
- Temperature absolute error: `2.713259902975551e-06 K`
- Raw source parent branch: `[0.2, 0.8]`
- Model-refined parent branch used by the private route: `[0.192531986929226, 0.807468013070774]`
- Source/model parent absolute error: `[0.00746801307077383, 0.00746801307077372]`
- Raw source shadow branch: `[0.5497, 0.4503]`
- Solved shadow branch: `[0.539765955844712, 0.460234044155288]`
- Max shadow-composition absolute error: `0.009934044155287869`
- Pressure consistency norm: `4.676236130762845e-05 Pa`
- Ln-fugacity consistency norm: `4.637046302491399e-10`
- Material-balance norm: `1.1102230246251565e-16`
- Phase distance: `0.347233968915486`

Fresh validation receipts:

- `uv run --no-sync python scripts/dev/build_epcsaft.py --profile equilibrium --build-only --parallel 4`
- `uv run --no-sync python run_pytest.py tests/native/contracts/test_cloud_shadow_route_admission_checker.py tests/native/contracts/test_cloud_shadow_boundary_gate_checker.py tests/native/contracts/test_boundary_workflow_checker.py tests/native/contracts/test_generalized_equilibrium_registry.py -q`
- `uv run --no-sync python run_pytest.py --allow-long-equilibrium-tests packages/epcsaft-equilibrium/tests/api/test_equilibrium.py packages/epcsaft-equilibrium/tests/contracts/test_activation_capabilities.py -q`
- `uv run --no-sync python scripts/validation/check_boundary_workflows.py --json --contracts-only`
- `uv run --no-sync python scripts/validation/check_boundary_workflows.py --json --cloud-shadow-gate --require-cloud-shadow-gate`
- `uv run --no-sync python scripts/validation/check_boundary_workflows.py --json --run-cloud-shadow-route --require-cloud-shadow-route`
- `uv run --no-sync python scripts/validation/check_neutral_lle_showcase.py --case-dir data/reference/equilibrium_benchmarks/neutral_lle/matsuda_2011_pfhexane_hexane --json --require-complete`
- `uv run --no-sync python scripts/dev/validate_project.py docs`
- `git diff --check`

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
- Readiness: `closed`
- AFK/HITL: `AFK`
- Release target: `equilibrium-0.x`
- Labels: `enhancement, agent-ready, native, solver, docs, validation, equilibrium, area:equilibrium, backend:ipopt, status:ready, type:feature`
