---
issue: 330
title: "M4 CE: activate standalone CE only after gates pass"
url: https://github.com/ePC-SAFT/ePC-SAFT/issues/330
state: open
milestone: "M4 - Equilibrium"
project: "ePC-SAFT Roadmap"
package: equilibrium
capability: null
backend: Ipopt
readiness: blocked
release_target: equilibrium-0.x
source_spec: docs/superpowers/specs/2026-06-25-m4-equilibrium-standalone-chemical-equilibrium-before-cpe.md
source_plan: docs/superpowers/plans/2026-06-26-m4-equilibrium-standalone-chemical-equilibrium-before-cpe-plan.md
afk_hitl: HITL
branch: codex/issue-0330-m4-ce-activate-standalone-ce-only-after-gates-pass
last_synced: "2026-06-26"
---

# M4 CE: activate standalone CE only after gates pass

**GitHub Issue:** https://github.com/ePC-SAFT/ePC-SAFT/issues/330
**GitHub Milestone:** M4 - Equilibrium
**Issue Type:** feature
**Source Spec:** docs/superpowers/specs/2026-06-25-m4-equilibrium-standalone-chemical-equilibrium-before-cpe.md
**Source Plan:** docs/superpowers/plans/2026-06-26-m4-equilibrium-standalone-chemical-equilibrium-before-cpe-plan.md
**AFK/HITL:** HITL
**Classification:** HITL
**Labels:** enhancement,docs,validation,equilibrium,area:equilibrium,backend:ipopt,type:feature,status:blocked
**Goal Command:** /goal Activate only standalone CE after strict checker proof and preserve CPE closure.
**Execution Mode:** Ask at runtime
**Worktree Policy:** Native Codex worktree thread first
**Integration Policy:** Worker PR reviewed by main thread
**TDD Policy:** Required
**Parallelization Plan:** None
**Reviewer Role:** Main thread orchestrator
**Script Gate Mode:** Safety only

## Outcome Summary

**Outcome Source:** docs/superpowers/plans/2026-06-26-m4-equilibrium-standalone-chemical-equilibrium-before-cpe-plan.md#outcome-proof
**Intent:** Open only standalone reactive_speciation after all strict CE gates pass.
**Target Output:** Activation/capability tests and checker proof open CE only and keep reactive LLE/CPE routes closed.
**Owner:** M4 equilibrium package owner for packages/epcsaft-equilibrium.
**Interface:** Source plan, issue mirror, route-specific tests, validation checker evidence, registry/capability payloads, and GitHub issue state.
**Cutover:** Replace placeholder or broad closed-ticket state only for this issue's accepted slice; keep unsupported CE/CPE surfaces closed.
**Replaced Path:** Prior prototype evidence, broad closed tickets, or placeholder-only docs cannot stand in for this issue's proof.
**Acceptance Proof:** Activation/capability tests and checker proof open CE only and keep reactive LLE/CPE routes closed.
**Stop Criteria:** Stop if the slice requires implicit standard-state conventions, unproven derivative evidence, unsupported phase coupling, or capability claims beyond this issue.
**Avoid:** Do not add downstream application metrics, regression work, release claims, or reactive phase route admission outside this issue scope.

## Project Merge

**Merge Owner:** Main thread orchestrator
**Merge Gate:** Native UI approval required
**Merge Policy:** Repo default
**Worktree Cleanup Policy:** Remove owned worktree after merge
**Orchestrator Wakeup Policy:** Worker handoff or bounded heartbeat

## What To Build

Open only standalone reactive_speciation after all strict CE gates pass.

## One-NLP Invariant

Activation may open only when the #326 standalone CE route remains the sole
public executable CE path: activation matrix, selector contract, native
`NlpProblem`, Ipopt adapter, and the #325 homogeneous CE block. Internal
continuation may support that route, but activation must keep reactive LLE,
reactive electrolyte LLE, and CPE routes closed and must not expose another CE
route, algorithm selector, or solver bypass.

## Acceptance Criteria

- [ ] Implement the issue slice described in the source plan.
- [ ] Add or update focused tests named in the source plan for this slice.
- [ ] Update docs, registry, capability payloads, and retained validation artifacts when this slice owns them.
- [ ] Run the slice proof oracle plus the plan validators before handoff.
- [ ] Prove activation opens only the single native NLP/Ipopt-backed `reactive_speciation` route after strict checker evidence passes.
- [ ] Preserve CE, PE, and CPE capability boundaries in user-facing text and capability payloads.

## Blocked by

- https://github.com/ePC-SAFT/ePC-SAFT/issues/329

## Non-goals

- Reactive LLE production support outside the standalone CE activation slice.
- Reactive electrolyte LLE production support outside later CPE issue sets.
- Downstream application metrics, parameter regression, or release publication.

## Proof Oracle

- uv run --no-sync python scripts/validate_plan_task_use_cases.py --plan-path docs/superpowers/plans/2026-06-26-m4-equilibrium-standalone-chemical-equilibrium-before-cpe-plan.md
- uv run --no-sync python scripts/validate_plan_outcome_proof.py --plan-path docs/superpowers/plans/2026-06-26-m4-equilibrium-standalone-chemical-equilibrium-before-cpe-plan.md
- Slice-specific commands from docs/superpowers/plans/2026-06-26-m4-equilibrium-standalone-chemical-equilibrium-before-cpe-plan.md Task section for this issue.
