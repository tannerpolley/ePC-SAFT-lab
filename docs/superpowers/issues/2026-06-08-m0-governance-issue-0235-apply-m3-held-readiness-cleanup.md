---
issue: 235
title: "M0: Apply M3 / HELD 1.0 readiness cleanup"
url: "https://github.com/ePC-SAFT/ePC-SAFT/issues/235"
state: "open"
milestone: "M0 - Governance"
project: "ePC-SAFT Roadmap"
package: "governance"
capability: "docs"
backend: Null
readiness: "ready"
release_target: "future"
source_spec: "docs/superpowers/specs/2026-06-08-m3-held-readiness-cleanup.md"
source_plan: "docs/superpowers/plans/2026-06-08-m0-m3-held-readiness-cleanup-plan.md"
afk_hitl: "AFK"
branch: codex/issue-0235-apply-m3-held-readiness-cleanup
last_synced: "2026-06-08"
---

# M0: Apply M3 / HELD 1.0 readiness cleanup

**GitHub Issue:** https://github.com/ePC-SAFT/ePC-SAFT/issues/235
**GitHub Milestone:** M0 - Governance
**Issue Type:** task
**Source Spec:** docs/superpowers/specs/2026-06-08-m3-held-readiness-cleanup.md
**Source Plan:** docs/superpowers/plans/2026-06-08-m0-m3-held-readiness-cleanup-plan.md
**Classification:** AFK
**Labels:** agent-ready, status:ready, type:task, docs, validation, area:docs
**Goal Command:** /goal Apply docs/superpowers/plans/2026-06-08-m0-m3-held-readiness-cleanup-plan.md task by task, preserving repo issue-tracker policy, validating docs, and stopping before any source implementation.
**Execution Mode:** Ask at runtime
**Worktree Policy:** Native Codex worktree thread first
**Integration Policy:** Worker PR reviewed by main thread
**TDD Policy:** User-approved opt-out
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

Apply the committed M3 / HELD 1.0 readiness cleanup plan. Close #161 as
design-record evidence, create the local #207 mirror, mark #208 ready after
verifying #207's provider contract in the checkout, and create the separate M6
capability evidence follow-up issue for the `single_component_vle` registry
mismatch.

## Acceptance Criteria

- [ ] #161 is closed on GitHub with a design-record comment that preserves the
  M8 evidence and future-M8 route.
- [ ] The #161 local mirror and M3 README no longer imply that the final M8
  decision memo is pending.
- [ ] A local #207 mirror exists and records the closed provider
  derivative-bundle contract.
- [ ] #208 local mirror, #208 plan, M4 README, and live GitHub labels no longer
  treat #208 as blocked by missing M3 provider work after #207 is verified.
- [ ] #148 remains unedited unless new ambiguity is found; the current narrow
  neutral HELD-style evidence boundary is preserved.
- [ ] A separate M6 follow-up issue is created for the `single_component_vle`
  capability evidence mismatch.
- [ ] Docs validation passes.
- [ ] The repo-scoped cleanup hook reports no matching leftover repo-owned
  processes.

## Blocked by

- None

## Non-goals

- No provider EOS implementation.
- No equilibrium route implementation.
- No HELD/GFPE route expansion.
- No public route exposure changes.
- No associating, electrolyte, reactive, or generalized multiphase claims.
- No `epcsaft-regression` work.
- No closure of #208 in this cleanup issue.
- No edits to `.chatgpt` packet files.

## Proof Oracle

- `uv run python scripts/dev/validate_project.py docs`
- `gh issue view 161 --json state --jq .state`
- `gh issue view 207 --json state --jq .state`
- `gh issue view 208 --json state,labels --jq '{state: .state, labels: [.labels[].name]}'`
- `gh api /repos/ePC-SAFT/ePC-SAFT/issues/208/dependencies/blocked_by --jq '.[].number'`
- `rg -n "eos_phase_objective_derivatives_cpp|target_pressure|pressure_work" packages/epcsaft/src/epcsaft/native/eos packages/epcsaft/src/epcsaft/native_sdk/provider_native_sdk_v1`
- `pwsh.exe -NoProfile -ExecutionPolicy Bypass -File "$env:USERPROFILE\.codex\hooks\codex-cleanup.ps1" -RepoRoot .`

## Tracker Metadata

- Milestone: `M0 - Governance`
- Package: `governance`
- Capability: `docs`
- Backend: `-`
- Readiness: `ready`
- AFK/HITL: `AFK`
- Release target: `future`
- Labels: `agent-ready, status:ready, type:task, docs, validation, area:docs`
