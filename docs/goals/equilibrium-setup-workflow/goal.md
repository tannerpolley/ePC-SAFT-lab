# Constructor-Configured Equilibrium API

## Objective

Implement `docs/handoffs/equilibrium-constructor-configured-api-handoff.md` exactly: reset the public `Equilibrium` frontend so the thermodynamic problem is configured in the constructor, `solve()` executes only that configured problem, capabilities and active docs describe public route names only, and the branch is validated, committed, and pushed.

## Original Request

Use `docs/handoffs/equilibrium-constructor-configured-api-handoff.md` to accomplish the full goal. No assumptions allowed; unclear decisions or unsure actions must stop and ask for clarification.

## Intake Summary

- Input shape: `existing_plan`
- Audience: ePC-SAFT maintainers and downstream package consumers
- Authority: `requested`
- Proof type: `test`
- Completion proof: GoalBuddy checker passes, every handoff gate has a receipt, constructor-configured `Equilibrium` is the only public equilibrium workflow, five production VLE routes still solve the hydrocarbon reference point, active docs and capabilities are current, full confidence validation passes, local commits exist, branch `ipopt` is pushed, and `git status --short` is clean.
- Likely misfire: Treating this as a small frontend rename while preserving legacy direct-solve compatibility, route-specific public methods, broad keyword escape hatches, Python-owned solver shortcuts, or stale capability/docs claims.
- Blind spots considered: owner-file proof before edits; route/spec matrix for all five current routes; real versus absent initialization; read-only `problem` metadata; immutable `structure()` and result phases; capability route-name claims; stale temporary receipt cleanup; native selector ownership; full validation and push.
- Existing plan facts: the handoff fixes the goal title and slug, requires this board before implementation edits, requires contract-test-first gates, forbids wrappers/aliases/fake initialization, requires owner-agent review, requires full confidence validation, requires logical local commits, and requires pushing branch `ipopt`.

## Goal Kind

`existing_plan`

## Current Tranche

Complete the full constructor-configured equilibrium API reset described by the handoff in one continuous execution tranche. Do not stop after board creation, discovery, red tests, or a single passing implementation slice while safe local work remains.

## Non-Negotiable Constraints

- Do not edit implementation files until this board exists, passes the GoalBuddy checker, and records the required gate tasks.
- Do not implement compatibility bridges, hidden aliases, broad keyword escape hatches, route-specific public methods, direct native route public methods, Python-owned solver loops, or fake initialization.
- If `initialize()` is not cleanly backed by native selector-owned initialization evidence, omit it and record the blocker.
- If `structure()` or DOF metadata is not generally owned by route/native metadata, report unavailable metadata explicitly instead of inventing a route-local count.
- If deleting old docs/goals/handoffs could remove a durable source of truth, stop and ask before deleting.
- If any required action is ambiguous, stop and ask before guessing.

## Stop Rule

Stop only when a final audit proves the full original outcome is complete, or when the same unresolved clarification blocker prevents meaningful progress.

Do not stop after planning, discovery, red tests, implementation of one route, or partial validation if the broader owner outcome still has safe local follow-up work.

## Slice Sizing

Safe means bounded, explicit, verified, and reversible. It does not mean tiny.

Use the largest safe useful slice for each Worker package, but preserve the handoff's gates: board first, owner-file proof before edits, tests before implementation, implementation, docs/capability cleanup, owner-agent review, full validation, commits, and push.

## Canonical Board

Machine truth lives at:

`docs/goals/equilibrium-setup-workflow/state.yaml`

If this charter and `state.yaml` disagree, `state.yaml` wins for task status, active task, receipts, verification freshness, and completion truth.

## Run Command

```text
/goal Follow docs/goals/equilibrium-setup-workflow/goal.md.
```

## PM Loop

On every `/goal` continuation:

1. Read this charter.
2. Read `state.yaml`.
3. Re-check the handoff gates and the no-assumptions stop rule.
4. Work only on the active board task.
5. Write a compact task receipt.
6. Update the board.
7. If safe local work remains, choose the next largest reversible task and continue unless blocked by a required clarification.
8. Finish only with a Judge/PM audit receipt that maps receipts and verification back to the handoff completion definition.
