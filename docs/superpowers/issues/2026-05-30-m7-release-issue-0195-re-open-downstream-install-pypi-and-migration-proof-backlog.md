---
issue: 195
title: "M7: re-open downstream install, PyPI, and migration proof backlog"
url: https://github.com/ePC-SAFT/ePC-SAFT/issues/195
state: open
milestone: "M7 - Release"
project: "ePC-SAFT Roadmap"
package: downstream
capability: Null
backend: Null
readiness: "needs design"
release_target: future
source_spec: docs/superpowers/specs/2026-05-29-m7-release-release-downstream-backlog.md
source_plan: docs/superpowers/plans/2026-05-30-m7-release-issue-0195-re-open-downstream-install-pypi-and-migration-proof-backlog-plan.md
afk_hitl: HITL
branch: codex/issue-0195-re-open-downstream-install-pypi-and-migration-proof-backlog
last_synced: "2026-06-02"
---

# Re-open downstream install, PyPI, and migration proof backlog

GitHub Issue: https://github.com/ePC-SAFT/ePC-SAFT/issues/195
Source Spec: docs/superpowers/specs/2026-05-29-m7-release-release-downstream-backlog.md
Source Plan: docs/superpowers/plans/2026-05-30-m7-release-issue-0195-re-open-downstream-install-pypi-and-migration-proof-backlog-plan.md
Branch: codex/issue-0195-re-open-downstream-install-pypi-and-migration-proof-backlog
AFK/HITL: HITL

GitHub remains authoritative for state, labels, Project fields, comments,
dependency edges, and PR linkage. This mirror exists so `project-resolve` can
start from a durable local source plan.

## Summary

Re-open the downstream install, PyPI, and migration proof backlog so release readiness is tracked separately from package-layout completion.

## Supplemental Context

- none

## Acceptance Criteria

- [ ] Install proof scope covers epcsaft, epcsaft-equilibrium, epcsaft-regression, and all-three combinations.
- [ ] Downstream migration proof requires real downstream workflows without private upstream workarounds.
- [ ] PyPI/trusted-publisher release choreography is documented as release work, not ordinary PR proof.
- [ ] Docs explain monorepo source-of-truth behavior for release consumers.

## Proof Oracle

- Run docs validation after the local plan and mirror are added.
- Confirm project fields and milestone assignment.

## Non-Goals And Boundaries

- No PyPI publication in this issue-publication pass.
- No downstream repo edits in this issue-publication pass.
- No public import/distribution rename.

## Tracker Metadata

- Milestone: `M7 - Release`
- Package: `downstream`
- Capability: `-`
- Backend: `-`
- Readiness: `needs design`
- AFK/HITL: `HITL`
- Release target: `future`
- Labels: `packaging, docs, validation, status:needs-design, type:task`
