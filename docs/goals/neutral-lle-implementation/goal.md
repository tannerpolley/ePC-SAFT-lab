# Neutral LLE Implementation

## Objective

Implement GitHub issue #144 as a production neutral, nonreactive, nonelectrolyte, nonassociating LLE route, then prepare the next associating neutral LLE tranche without exposing associating LLE in this tranche.

## Original Request

Use Agentify to read the final ChatGPT response about implementing LLE, create the issue, and begin a goal board to accomplish the full issue and plan to prep for associating neutral LLE.

## Intake Summary

- Input shape: `existing_plan`
- Audience: ePC-SAFT maintainers, Codex implementation agents, and downstream package consumers
- Authority: `requested`
- Proof type: `test`
- Completion proof: Issue #144 is implemented through the public `Equilibrium(..., route="lle", T=..., P=..., z=...).solve()` route, native Ipopt proof tests pass for the synthetic nonassociating binary split, docs/capabilities are updated without overclaiming, and an associating-neutral-LLE follow-up plan or issue is prepared from the verified baseline.
- Likely misfire: Declaring LLE complete after selector metadata, synthetic structure tests, or documentation only; admitting methanol/cyclohexane, water/alcohol, electrolyte LLE, salting-out, or reactive LLE before the nonassociating native route is production-proven.
- Blind spots considered: Ipopt availability must be verified before production exposure; LLE needs composition-distance separation rather than `phase_volume_gap`; public result helpers must not force VLE `x`/`y`; associating neutral LLE depends on association solved-state and derivative readiness.
- Existing plan facts: GitHub issue #144 is the controlling tracker artifact; the Agentify source response requires a synthetic nonassociating binary proof first and treats associating neutral LLE as the next planning tranche.

## Goal Kind

`existing_plan`

## Current Tranche

Complete issue #144 end to end: validate the live repo against the issue body, implement the neutral nonassociating LLE native route and Python API, prove it with focused native/API/docs validation, then prepare the next associating neutral LLE plan only after the nonassociating route is verified.

## Non-Negotiable Constraints

- Keep the first production LLE route neutral, nonreactive, nonelectrolyte, and nonassociating.
- Do not expose methanol/cyclohexane, water/alcohol, electrolyte LLE, salting-out LLE, reactive LLE, reactive electrolyte LLE, SLE, precipitation, Ksp, or solid saturation in this tranche.
- Use the activation-plan / block-assembled native NLP path; do not add a route-specific C++ problem class when the generic two-phase route machinery can own it.
- Do not mark `neutral_lle` production-exposed until an Ipopt-enabled accepted solve proof passes.
- Preserve `liquid1` and `liquid2` phase labels for LLE and keep VLE convenience helpers VLE-only.
- Keep public APIs generic and capability claims honest.
- Use `run_pytest.py` for pytest validation and the repo native build workflow for `_core`.

## Stop Rule

Stop only when a final audit proves the full original outcome is complete.

Do not stop after planning, discovery, or Judge selection if a safe Worker task can be activated.

Do not stop after a single verified Worker package when the broader owner outcome still has safe local follow-up work. Advance the board to the next highest-leverage safe Worker package and continue unless a phase, risk, rejected-verification, ambiguity, or final-completion review is due.

Do not create one Worker/Judge pair per repeated file, table, route, or helper. Put repeated same-shape work into one Worker package and review the package as a whole.

Do not stop because a slice needs owner input, credentials, production access, destructive operations, or policy decisions. Mark that exact slice blocked with a receipt, create the smallest safe follow-up or workaround task, and continue all local, non-destructive work that can still move the goal toward the full outcome.

## Slice Sizing

Safe means bounded, explicit, verified, and reversible. It does not mean tiny.

A good task is the largest safe useful slice.

Small is not the goal. Useful is the goal.

A Worker should finish the whole assigned slice. A Judge should judge the whole assigned slice. A PM should reorient the board when tasks are safe but not moving the outcome.

Tiny tasks are allowed when the failure is isolated, the risk is high, the scope is unknown, or the tiny task unlocks a larger slice. Tiny tasks are bad when they keep happening, do not change behavior, only add wrappers/contracts/proof files, or avoid the real milestone.

## Canonical Board

Machine truth lives at:

`docs/goals/neutral-lle-implementation/state.yaml`

If this charter and `state.yaml` disagree, `state.yaml` wins for task status, active task, receipts, verification freshness, and completion truth.

## Run Command

```text
/goal Follow docs/goals/neutral-lle-implementation/goal.md.
```

## PM Loop

On every `/goal` continuation:

1. Read this charter.
2. Read `state.yaml`.
3. Run the bundled GoalBuddy update checker when available and mention a newer version without blocking.
4. Re-check the intake: original request, input shape, authority, proof, blind spots, existing plan facts, and likely misfire.
5. Work only on the active board task.
6. Assign Scout, Judge, Worker, or PM according to the task.
7. Write a compact task receipt.
8. Update the board.
9. If safe local work remains, choose the next largest reversible Worker package and continue unless blocked.
10. If a problem, suggestion, or follow-up should become a repo artifact, create an approved issue/PR or ask the operator whether to create one.
11. Review at phase, risk, rejected-verification, ambiguity, or final-completion boundaries; do not review every small Worker by habit.
12. Finish only with a Judge/PM audit receipt that maps receipts and verification back to the original user outcome and records `full_outcome_complete: true`.

Issue and PR handoffs are supporting artifacts. `state.yaml` remains authoritative, and every external artifact decision must be recorded in a task receipt.
