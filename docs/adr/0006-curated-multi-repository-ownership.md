# ADR 0006: Curated Multi-Repository Ownership

## Status

Accepted.

## Context

ADR 0005 established the provider/equilibrium/regression package split inside
one transition monorepo. That layout enabled coordinated recovery, but it is
not the final repository topology. The provider, equilibrium, and regression
owners need independent dependency, build, validation, release, and tracker
boundaries. Organization-wide profile and reusable policy also need an owner
that is not any one package repository.

The transition checkout already uses `ePC-SAFT/ePC-SAFT` as `origin`.
Therefore that identity is an existing remote, not an unallocated destination.
Clean local skeleton creation cannot decide whether the existing remote is
retained, renamed, or repurposed, and must not imply destructive history
replacement.

## Decision

- Final ownership is split across intended GitHub homes
  `ePC-SAFT/ePC-SAFT` for the provider, `ePC-SAFT/ePC-SAFT-equilibrium` for
  equilibrium, `ePC-SAFT/ePC-SAFT-regression` for regression, and
  `ePC-SAFT/.github` for organization profile and shared policy.
- The optional validation repository remains deferred until M6 and
  cross-package evidence ownership receive a separate decision.
- Dependencies are one-way from the equilibrium and regression extensions to
  a compatible installed provider. The provider depends on neither extension,
  and the extensions do not depend on each other. CppAD remains provider-owned,
  Ipopt equilibrium-owned, and Ceres regression-owned.
- Stage 11 may create governance-only local repository homes before scientific
  transfer. Those deliberately non-buildable skeletons are not packages,
  runtime owners, capability evidence, remotes, or development sources of
  truth.
- Stage 13 alone owns accepted core owner transfer, installed-provider
  compatibility, cross-repository parity and provenance, and any separately
  approved development-source-of-truth cutover. Optional Stage 7-10 branches
  require their own transfer leaves.
- Stage 12 alone owns transition-repository retirement and archive mutation.
- The existing `ePC-SAFT/ePC-SAFT` remote requires a separately approved
  retain/rename/repurpose strategy. Force-push and history replacement are not
  authorized by this ADR.
- Remote creation, initial push, publication, release, organization-policy
  mutation, issue or milestone movement, and source-of-truth changes remain
  separate user approval gates.

## Consequences

The transition monorepo remains the executable source and reference evidence
until accepted transfer receipts say otherwise. Early repository homes can
stabilize ownership and routing without copying unresolved runtime structure.
No skeleton may acquire package metadata, workflows, executable tests, or
capability claims merely to look complete.

Each later transfer must be selective, provenance-backed, independently
buildable against installed artifacts, and delete any displaced active owner
in the same accepted checkpoint. Historical records and failed scientific
evidence remain preserved according to their owning stage.

## Migration Gate

Before Stage 13 changes a development source of truth:

- Stages 4-6 have accepted scientific and architecture receipts;
- the M5 regression admission blocker is resolved before regression transfer;
- destination ownership, dependency, package, compatibility, and provenance
  contracts are approved;
- independent builds and installed-artifact parity pass without sibling-source
  leakage;
- the existing provider-remote identity has a non-destructive approved
  strategy; and
- every external write has separate user authorization.

Before Stage 12 archives or retires the transition repository, the Stage 13
core transfer/parity receipt and an exact keep/archive/delete manifest must be
accepted.
