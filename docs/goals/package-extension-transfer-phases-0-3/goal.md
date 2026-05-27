# Package Extension Transfer Phases 0-3

## Objective

Turn `docs/roadmaps/package_extension_transfer_roadmap.md` into an executable
pre-extraction GoalBuddy board and then complete the roadmap work that must
precede any `epcsaft-equilibrium` package extraction: organization readiness
inventory, split contract decision, provider contract freeze, native/build
boundary decision, GFPE cleanup evidence audit, and internal package-boundary
proof inside this repo.

## Original Request

Read `docs/roadmaps/package_extension_transfer_roadmap.md`, review the overall
phase plan, and create a plan to implement Phases 0-3 with a GoalBuddy board
using subagents, the GitHub plugin, and grill-me style skepticism. Later update:
revise the board so it includes every local pre-extraction step needed before
equilibrium can safely become its own package extension.

## Intake Summary

- Input shape: `existing_plan`
- Audience: repo maintainers and downstream package consumers
- Authority: `requested`
- Proof type: `artifact`
- Completion proof: Phase 0 prerequisites are either completed or explicitly
  blocked with evidence; Phase 1 ADR and source-of-truth docs agree on split
  ownership; Phase 2 provider, extension compatibility, and native/build
  boundary docs/tests pass; Phase 3 internal boundary proof passes
  provider-only, equilibrium, regression, and explicit integration validation;
  a final pre-extraction audit proves equilibrium can be extracted without
  hidden core internals, route-local acceptance assembly, or compatibility
  wrappers.
- Likely misfire: stop after ADR/docs, start moving code before ownership,
  contract, and validation gates are explicit, or confuse GFPE cleanup
  completion with extraction readiness.
- Blind spots considered: Phase 0 is mostly external GitHub organization/admin
  work; current docs still describe regression and equilibrium as core package
  capabilities; current publishing and metadata still point at
  `tannerpolley/ePC-SAFT`; Phase 2 and Phase 3 depend on explicit Judge gates;
  the GFPE cleanup work already completed some selector/result/Ipopt gates but
  not the full provider/native package boundary; the worktree already contains
  a user-owned modification to `docs/roadmaps/FULL_ROADMAP.md`.
- Existing plan facts: the roadmap defines the dependency order
  `ADR -> source-of-truth docs -> provider API -> internal boundaries ->
  transfer -> extraction -> coordinated releases`; the first implementation PR
  should not move production code; long-lived compatibility wrappers are out of
  policy; extraction readiness is a narrower gate than full GFPE completion.

## Goal Kind

`existing_plan`

## Current Tranche

Complete the pre-extraction execution tranche defined by roadmap Phases 0-3:

1. Phase 0: confirm or stage the external organization, project, labels, and transfer prerequisites.
2. Phase 1: land the split contract in ADRs, source-of-truth docs, publishing docs, metadata, and issue-tracker guidance.
3. Phase 2: freeze the provider API contract, extension compatibility
   contract, native/build linkage contract, and contract tests.
4. Phase 3: prove internal package boundaries inside this repo before any repo
   extraction or transfer work starts.
5. Extraction-readiness audit: prove the current equilibrium implementation can
   move to `epcsaft-equilibrium` through documented seams, with remaining GFPE
   cleanup explicitly marked post-extraction.

The first active work is validation of the plan itself, not blind execution. The board should use read-only Scouts and Judge gates to freeze sequencing and ownership before any write-capable Worker starts.

## Non-Negotiable Constraints

- Respect the roadmap dependency order. Do not start Phase 2 before a Judge receipt proves Phase 1 is complete enough to freeze the provider contract.
- Do not start Phase 3 before a Judge receipt proves the Phase 2 provider contract, future-owner map, and validation expectations are fixed.
- Do not transfer repos, extract repos, or leave long-lived compatibility wrappers during this goal. This goal ends at extraction readiness, not extraction.
- Do not require full GFPE completion before extraction readiness. Require only the selector, result, Ipopt, provider, native/build, and boundary contracts that make extraction safe.
- Keep APIs generic and capability claims evidence-backed.
- Keep the change scoped to the smallest maintainable slice that still clears the current phase gate.
- One write-capable Worker at a time unless a Judge-approved board update proves disjoint write scopes.
- Do not touch the existing user-owned modification in `docs/roadmaps/FULL_ROADMAP.md` except where a later approved Worker task explicitly needs to integrate with it.
- Use the GitHub plugin for GitHub-surface inspection or later approved issue/project work; do not create external GitHub artifacts without an explicit board task and approval when required.

## Stop Rule

Stop only when a final audit proves the full original outcome is complete.

Do not stop after planning, discovery, or Judge selection if a safe phase-specific Worker can run.

Do not stop after a single docs PR if the provider-contract, native/build
boundary, GFPE cleanup audit, and internal-boundary phases are still required
for the user outcome.

## Slice Sizing

Safe means bounded, explicit, verified, and reversible. It does not mean tiny.

A good task is the largest safe useful slice.

For this goal, the preferred slices are:

- one read-only evidence package per unresolved phase gate;
- one coherent Worker per major phase after the gate is cleared;
- a Judge review at each phase boundary and before any write-heavy migration.
- one final Judge audit that distinguishes pre-extraction blockers from
  post-extraction cleanup.

Avoid helper-only micro-Workers for Phase 3. If the smaller-step fallback is chosen, it should still be one coherent Phase 3 start slice, not a chain of compatibility wrappers.

## Canonical Board

Machine truth lives at:

`docs/goals/package-extension-transfer-phases-0-3/state.yaml`

If this charter and `state.yaml` disagree, `state.yaml` wins for task status, active task, receipts, verification freshness, and completion truth.

## Run Command

```text
/goal Follow docs/goals/package-extension-transfer-phases-0-3/goal.md.
```

## PM Loop

On every `/goal` continuation:

1. Read this charter.
2. Read `state.yaml`.
3. Re-check the roadmap dependency order and current phase gate.
4. Work only on the active board task.
5. Keep external GitHub org/admin work separate from repo-writing Worker tasks.
6. Write a compact receipt.
7. Update the board.
8. Move to the next largest reversible slice only after the current gate is satisfied.
9. Finish only with a Judge/PM audit that maps receipts and verification back to the original request and records `full_outcome_complete: true`.
