---
issue: 194
title: "M6: re-open executable literature benchmark and capability evidence backlog"
url: https://github.com/ePC-SAFT/ePC-SAFT/issues/194
state: open
milestone: "M6 - Validation"
project: "ePC-SAFT Roadmap"
package: benchmark
capability: Null
backend: Null
readiness: "needs design"
release_target: future
source_spec: docs/superpowers/specs/2026-05-29-m6-validation-validation-benchmark-backlog.md
source_plan: docs/superpowers/plans/2026-05-30-m6-validation-issue-0194-re-open-executable-literature-benchmark-and-capability-evidence-backlog-plan.md
afk_hitl: HITL
branch: codex/issue-0194-re-open-executable-literature-benchmark-and-capability-evidence-backlog
last_synced: "2026-06-02"
---

# Re-open executable literature benchmark and capability evidence backlog

GitHub Issue: https://github.com/ePC-SAFT/ePC-SAFT/issues/194
Source Spec: docs/superpowers/specs/2026-05-29-m6-validation-validation-benchmark-backlog.md
Source Plan: docs/superpowers/plans/2026-05-30-m6-validation-issue-0194-re-open-executable-literature-benchmark-and-capability-evidence-backlog-plan.md
Branch: codex/issue-0194-re-open-executable-literature-benchmark-and-capability-evidence-backlog
AFK/HITL: HITL

GitHub remains authoritative for state, labels, Project fields, comments,
dependency edges, and PR linkage. This mirror exists so `project-resolve` can
start from a durable local source plan.

## Summary

Re-open the executable literature benchmark and capability evidence backlog so validation work is tracked as command-backed evidence instead of broad roadmap prose.

## Supplemental Context

- `docs/superpowers/milestones/M4-equilibrium/generalized-fluid-phase-equilibrium.md`

## Acceptance Criteria

- [ ] Benchmark families are inventoried with source, fixture, expected behavior, tolerance, and command requirements.
- [ ] Capability evidence rules define when docs may claim support.
- [ ] Registry/docs/test ownership is clear across provider, equilibrium, regression, and cross-package lanes.
- [ ] Release-quality validation gates are separated from ordinary PR local-proof gates.

## Proof Oracle

- Run docs validation after the local plan and mirror are added.
- Confirm project fields and milestone assignment.

## Non-Goals And Boundaries

- No implementation of all benchmarks in this publication pass.
- No publication or release.
- No unsupported capability claim broadening.

## Tracker Metadata

- Milestone: `M6 - Validation`
- Package: `benchmark`
- Capability: `-`
- Backend: `-`
- Readiness: `needs design`
- AFK/HITL: `HITL`
- Release target: `future`
- Labels: `docs, validation, area:benchmark, status:needs-design, type:task`
