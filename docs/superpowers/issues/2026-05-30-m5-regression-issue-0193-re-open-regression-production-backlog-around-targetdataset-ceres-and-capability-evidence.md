---
issue: 193
title: "M5: re-open regression production backlog around TargetDataset, Ceres, and capability evidence"
url: https://github.com/ePC-SAFT/ePC-SAFT/issues/193
state: open
milestone: "M5 - Regression"
project: "ePC-SAFT Roadmap"
package: regression
capability: regression
backend: Ceres
readiness: "needs design"
release_target: regression-0.x
source_spec: docs/superpowers/specs/2026-05-29-m5-regression-regression-production-backlog.md
source_plan: docs/superpowers/plans/2026-05-30-m5-regression-issue-0193-re-open-regression-production-backlog-around-targetdataset-ceres-and-capability-evidence-plan.md
afk_hitl: HITL
branch: codex/issue-0193-re-open-regression-production-backlog-around-targetdataset-ceres-and-cap
last_synced: "2026-06-02"
---

# Re-open regression production backlog around TargetDataset, Ceres, and capability evidence

GitHub Issue: https://github.com/ePC-SAFT/ePC-SAFT/issues/193
Source Spec: docs/superpowers/specs/2026-05-29-m5-regression-regression-production-backlog.md
Source Plan: docs/superpowers/plans/2026-05-30-m5-regression-issue-0193-re-open-regression-production-backlog-around-targetdataset-ceres-and-capability-evidence-plan.md
Branch: codex/issue-0193-re-open-regression-production-backlog-around-targetdataset-ceres-and-cap
AFK/HITL: HITL

GitHub remains authoritative for state, labels, Project fields, comments,
dependency edges, and PR linkage. This mirror exists so `project-resolve` can
start from a durable local source plan.

## Summary

Re-open the regression production backlog as a single M5 tracker around TargetDataset, Ceres optimizer loops, parameter sensitivity evidence, and honest regression capability claims.

## Supplemental Context

- none

## Acceptance Criteria

- [ ] TargetDataset, TargetRow, result schema, bounds/maps, and diagnostics have current production gaps inventoried.
- [ ] Ceres residual blocks and optimizer loops have a proof plan tied to package-local regression tests.
- [ ] Parameter movement/sensitivity tests are identified for pure, binary, electrolyte, and optional equilibrium-target lanes.
- [ ] Capability evidence requirements distinguish implemented support from planned regression routes.

## Proof Oracle

- Run docs validation after the local plan and mirror are added.
- Confirm project fields and milestone assignment.

## Non-Goals And Boundaries

- No regression implementation in this issue-publication pass.
- No public API rename.
- No PyPI publication.
- No child issue splitting without a later approved decomposition.

## Tracker Metadata

- Milestone: `M5 - Regression`
- Package: `regression`
- Capability: `regression`
- Backend: `Ceres`
- Readiness: `needs design`
- AFK/HITL: `HITL`
- Release target: `regression-0.x`
- Labels: `native, validation, regression, area:regression, backend:ceres, status:needs-design, type:task`
