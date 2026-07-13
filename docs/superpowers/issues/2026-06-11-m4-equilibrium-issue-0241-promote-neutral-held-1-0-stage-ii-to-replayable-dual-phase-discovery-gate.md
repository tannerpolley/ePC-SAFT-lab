---
issue: 241
title: "M4: promote neutral HELD 1.0 Stage II to replayable dual phase-discovery gate"
url: https://github.com/ePC-SAFT/ePC-SAFT/issues/241
state: closed
milestone: "M4 - Equilibrium"
project: "ePC-SAFT Roadmap"
package: equilibrium
capability: lle
backend: Ipopt
readiness: closed
release_target: equilibrium-0.x
source_spec: null
source_plan: null
afk_hitl: AFK
branch: null
last_synced: "2026-07-12"
---

**Source-faithful historical classification (2026-07-12):** Preserve this closed issue as component history only. Stage 1 doctrine supersedes any classification of sampled-candidate replay as a completed Pereira Stage II upper/lower loop or of current-route/local residual refinement as canonical Stage III. The retained work does not establish Pereira HELD parity, global phase-set completeness, or public route admission.

# M4: promote neutral HELD 1.0 Stage II to replayable dual phase-discovery gate

**Mirror Retention:** Keep

**GitHub Issue:** https://github.com/ePC-SAFT/ePC-SAFT/issues/241
**GitHub Milestone:** M4 - Equilibrium
**Issue Type:** feature
**Source Spec:** docs/superpowers/specs/2026-06-11-m4-equilibrium-held-1-0-full-adoption.md
**Source Plan:** docs/superpowers/plans/2026-06-11-m4-equilibrium-held-1-0-adoption-and-issue-0187-start-plan.md
Branch: codex/issue-0241-promote-neutral-held-stage-ii-dual-discovery
AFK/HITL: AFK
**Classification:** Closed
**Labels:** enhancement, native, solver, docs, validation, equilibrium, area:equilibrium, backend:ipopt, status:ready, type:feature
**Goal Command:** Create a native execution goal for #241 from this mirror.
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

Implement the missing HELD 1.0 adoption gate between #187 and #188: promote
neutral Stage II from the current finite candidate bound audit to a replayable
dual phase-discovery loop with explicit lower and upper bound history,
candidate storage, stopping criteria, and Stage III replay metadata.

## Acceptance Criteria

- [x] Stage II reports lower bound, upper bound, bound gap, stopping reason,
  candidate list, rejected candidates, and replay metadata.
- [x] Stage III route refinement consumes Stage II candidate metadata.
- [x] Incomplete continuous TPD starts, open Stage II gaps, tiny-step paths,
  acceptable-level points, feasible-only points, and iteration-limit routes do
  not satisfy the adoption gate.
- [x] Registry and diagnostics distinguish deterministic screening, continuous
  TPD, Stage I, Stage II audit, Stage II dual-loop verification, and Stage III
  refinement.
- [x] No associating, electrolyte, reactive, CE, CPE, public route, benchmark,
  or capability broadening occurs in this issue.

## Resolution Notes

- Closed by https://github.com/ePC-SAFT/ePC-SAFT/pull/244 on 2026-06-11.
- Neutral Stage II now exposes candidate-bound audit status separately from
  replayable dual-loop verification.
- Stage III neutral LLE route refinement starts from the Stage II replay seed
  and records replay consumption in postsolve, physical evidence, stability
  certificates, and validation diagnostics.
- The Stage 9 proof oracle now requires replay metadata and Stage III replay
  consumption before reporting completion.

## Blocked By

- https://github.com/ePC-SAFT/ePC-SAFT/issues/187

## Blocking

- https://github.com/ePC-SAFT/ePC-SAFT/issues/188
- https://github.com/ePC-SAFT/ePC-SAFT/issues/189

## Non-Goals

- No source-backed neutral TP flash fixture admission.
- No boundary workflow or generalized phase-set PE admission.
- No associating, electrolyte, reactive, CE, or CPE admission.
- No public route exposure.

## Proof Oracle

```powershell
uv run python run_pytest.py packages/epcsaft-equilibrium/tests/native/diagnostics/test_selector_core_contracts.py -q
```

```powershell
uv run python run_pytest.py tests/native/contracts/test_generalized_equilibrium_registry.py tests/native/contracts/test_equilibrium_benchmark_registry.py -q
```

```powershell
uv run python scripts/validation/check_phase_discovery.py --json --include-route-refinement --require-complete
```

```powershell
uv run python scripts/dev/validate_project.py docs
```

## GitHub Body Text

Implement the missing HELD 1.0 adoption gate between #187 and #188: promote
neutral Stage II from the current finite candidate bound audit to a replayable
dual phase-discovery loop with explicit lower/upper bound history, candidate
storage, stopping criteria, and Stage III replay metadata.

Source spec:
docs/superpowers/specs/2026-06-11-m4-equilibrium-held-1-0-full-adoption.md

Source plan:
docs/superpowers/plans/2026-06-11-m4-equilibrium-held-1-0-adoption-and-issue-0187-start-plan.md

Classification:
Ready after #187 closed by #242. This can run AFK while the proof oracle remains
sufficient.

Outcome:
Neutral HELD Stage II can be used as a full adoption gate only when a replayable
dual phase-discovery loop records bound history, candidate creation and
rejection, stopping criteria, and route-refinement metadata.
