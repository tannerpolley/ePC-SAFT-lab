---
issue: 192
title: "M6: close GFPE registry, capability, and benchmark evidence"
url: https://github.com/ePC-SAFT/ePC-SAFT/issues/192
state: open
milestone: "M6 - Validation"
project: "ePC-SAFT Roadmap"
package: benchmark
capability: lle
backend: Null
readiness: ready
release_target: future
source_spec: docs/superpowers/specs/2026-05-30-m6-validation-issue-0192-close-gfpe-registry-capability-and-benchmark-evidence.md
source_plan: docs/superpowers/plans/2026-05-30-m6-validation-issue-0192-close-gfpe-registry-capability-and-benchmark-evidence-plan.md
afk_hitl: HITL
branch: codex/issue-0192-close-gfpe-registry-capability-and-benchmark-evidence
last_synced: "2026-06-25"
---

# Close GFPE registry, capability, and benchmark evidence

GitHub Issue: https://github.com/ePC-SAFT/ePC-SAFT/issues/192
Source Spec: docs/superpowers/specs/2026-05-30-m6-validation-issue-0192-close-gfpe-registry-capability-and-benchmark-evidence.md
Source Plan: docs/superpowers/plans/2026-05-30-m6-validation-issue-0192-close-gfpe-registry-capability-and-benchmark-evidence-plan.md
Branch: codex/issue-0192-close-gfpe-registry-capability-and-benchmark-evidence
AFK/HITL: HITL

GitHub remains authoritative for state, labels, Project fields, comments,
dependency edges, and PR linkage. This mirror exists so `project-resolve` can
start from a durable local source plan.

## Summary

Close the GFPE registry/capability/benchmark evidence after the relevant M4 proof gates exist, so user-facing capability claims match executable evidence.

## Supplemental Context

- `docs/superpowers/specs/2026-05-29-m6-validation-validation-benchmark-backlog.md`
- `docs/superpowers/milestones/M4-equilibrium/generalized-fluid-phase-equilibrium.md`

## Acceptance Criteria

- [ ] Algorithm registry entries point to executable GFPE evidence rather than planned-only claims.
- [ ] Capability evidence identifies proven neutral, associating, electrolyte, and reactive route scope separately.
- [ ] Benchmark or literature fixture metadata includes source, expected behavior, tolerances, and command receipts.
- [ ] Docs and tests fail if registry support claims outpace executable evidence.

## Proof Oracle

- Run capability evidence tests.
- Run benchmark/registry structural tests.
- Run docs validation.

## Non-Goals And Boundaries

- No new solver algorithm implementation unless required by a validation gap.
- No release publication.
- No broad unsupported capability claims.

## Tracker Metadata

- Milestone: `M6 - Validation`
- Package: `benchmark`
- Capability: `lle`
- Backend: `-`
- Readiness: `ready`
- AFK/HITL: `HITL`
- Release target: `future`
- Labels: `docs, validation, area:benchmark, status:ready, type:task`
