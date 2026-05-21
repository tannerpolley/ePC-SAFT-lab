# Native Topology Activation Matrix Completion

## Objective

Complete the existing-plan implementation tranche for the native topology activation matrix: make C++ activation metadata the source of truth, route the trusted hydrocarbon bubble-pressure path through a selector core, remove stale non-production equilibrium route surfaces, update capability evidence and docs, validate through the updated Gate 10 sequence, commit locally, and push `ipopt`.

## Original Request

Implement the Native Topology Activation Matrix Completion Plan in full, start the GoalBuddy board first, use strict gates, stay on `ipopt`, commit, and push the branch.

## Intake Summary

- Input shape: `existing_plan`
- Audience: package maintainers and downstream users relying on generic `epcsaft` APIs
- Authority: `requested`
- Proof type: `test`
- Completion proof: updated Gate 10 passes, GoalBuddy checker passes, independent role-owner review is recorded, local commits exist, `ipopt` is pushed, and the worktree is clean
- Likely misfire: treating this as a mechanical file move or documentation cleanup while capabilities, bindings, route deletion, and selector-core certification still drift
- Blind spots considered: route deletion blast radius, C++/Python capability mirror drift, public API compatibility, stale generated algorithm docs, and non-production route tests hiding removed behavior
- Existing plan facts: use contract-test-first sequencing; keep only `Equilibrium.bubble_pressure`; delete electrolyte/reactive bubble routes; support only neutral non-associating production bubble inputs; use selector certification as a hard gate; commit the generated activation mirror; add one ADR and concise glossary terms; run updated Gate 10; push only, no PR

## Goal Kind

`existing_plan`

## Current Tranche

Continuous execution until the full plan outcome is complete. The PM may coordinate role-owner agents for read-only review, bounded implementation, and validation, but board truth remains in `state.yaml`.

## Non-Negotiable Constraints

- Do not implement before the GoalBuddy board exists.
- Do not keep compatibility stubs, forwarding wrappers, hidden callable route shells, or legacy route aliases for deleted non-production equilibrium routes.
- Do not broaden production claims beyond the neutral non-associating bubble/dew family.
- Do not tune solver scaling, route variables, constraints, continuation, or convergence behavior unless a mechanical seam split forces it and the bubble route remains behavior-preserving.
- Do not delete tests merely to make validation pass; replace removed-route tests with current selector-core, capability, and structure contracts.
- Keep generated Graphify artifacts untracked.
- Stay on branch `ipopt`; push the branch after successful validation; do not open a PR.

## Stop Rule

Stop only when a final PM or Judge audit maps current receipts and validation to the original request and records `full_outcome_complete: true`.

## Canonical Board

Machine truth lives at:

`docs/goals/native-topology-activation-matrix-completion/state.yaml`

If this charter and `state.yaml` disagree, `state.yaml` wins for task status, active task, receipts, verification freshness, and completion truth.

## Run Command

```text
/goal Follow docs/goals/native-topology-activation-matrix-completion/goal.md.
```
