# ADR 0007: Clean Ecosystem Doctrine

## Status

Accepted on 2026-07-14.

## Context

The July 13 bootstrap proved four clean, remote-free repository skeletons but
deferred validation and treated the transition repository as an eventual
retirement candidate. The approved target now includes a first-class
validation repository and a permanent personal lab, together with stricter
derivative, promotion, and maintenance rules.

## Decision

The canonical permanent authority is `ePC-SAFT/.github/GOVERNANCE.md`, doctrine
revision 1. Until that remote is published, its approved local source is
`/home/tnnrpolley21/Workspaces/Engineering/ePC-SAFT-project/ePC-SAFT-organization/GOVERNANCE.md`.
The one-time cutover authority is
`docs/superpowers/specs/2026-07-14-clean-ecosystem-cutover-design.md`.

Those documents supersede conflicting target-state statements in ADR 0006,
the July 13 bootstrap design and plan, and the bootstrap contract. Those older
records remain authoritative evidence of what Stage 11 actually did: create
four clean local skeletons, no remotes, no runtime transfer, and no source-of-
truth change.

## Consequences

The final topology has provider, equilibrium, regression, validation,
organization-policy, and personal-lab homes. Governance authority changes now;
runtime authority does not. Every runtime slice remains owned by the current
repository until its machine-validated promotion receipt and explicit user
approval make a destination the unique production owner.
