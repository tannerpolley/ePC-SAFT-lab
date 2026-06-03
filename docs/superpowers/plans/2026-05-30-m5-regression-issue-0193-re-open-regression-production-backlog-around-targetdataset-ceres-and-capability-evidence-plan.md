# Re-open regression production backlog around TargetDataset, Ceres, and capability evidence Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> `superpowers:subagent-driven-development` or `superpowers:executing-plans` to
> implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for
> tracking.

**Goal:** Resolve GitHub issue #193: Re-open regression production backlog around TargetDataset, Ceres, and capability evidence.

**Architecture:** Keep the work inside the owning milestone/package boundary and
use the source spec plus GitHub issue as the behavior contract. Public capability
claims should move only when the proof oracle records matching evidence.

**Tech Stack:** Python, C++/pybind11 where the issue touches native code, CMake,
CppAD/Ceres/Ipopt only when required by the issue labels, pytest, GitHub Issues.

---

## Intake

- Source Spec: `docs/superpowers/specs/2026-05-29-m5-regression-regression-production-backlog.md`
- Source Issue: `docs/superpowers/issues/2026-05-30-m5-regression-issue-0193-re-open-regression-production-backlog-around-targetdataset-ceres-and-capability-evidence.md`
- Source Plan: `docs/superpowers/plans/2026-05-30-m5-regression-issue-0193-re-open-regression-production-backlog-around-targetdataset-ceres-and-capability-evidence-plan.md`
- GitHub Issue: `https://github.com/ePC-SAFT/ePC-SAFT/issues/193`
- Milestone: `M5 - Regression`
- AFK/HITL: `HITL`

## Acceptance Criteria

- [ ] TargetDataset, TargetRow, result schema, bounds/maps, and diagnostics have current production gaps inventoried.
- [ ] Ceres residual blocks and optimizer loops have a proof plan tied to package-local regression tests.
- [ ] Parameter movement/sensitivity tests are identified for pure, binary, electrolyte, and optional equilibrium-target lanes.
- [ ] Capability evidence requirements distinguish implemented support from planned regression routes.

## Tasks

### Task 1: Preflight And Boundary Check

**Files:**
- `packages/epcsaft-regression/**`
- `packages/epcsaft-regression/tests/**`
- `tests/workflows/repo/**`
- `docs/superpowers/**`

- [ ] Confirm GitHub issue #193 is still `needs design` and verify blocker/design state before code changes.
- [ ] Read the source spec, issue mirror, GitHub issue, and milestone README.
- [ ] Confirm candidate file ownership and reject unrelated package or milestone scope.
- [ ] Select the smallest validation slice that proves the issue behavior.

### Task 2: Implement The Issue Slice

**Files:**
- `packages/epcsaft-regression/**`
- `packages/epcsaft-regression/tests/**`
- `tests/workflows/repo/**`
- `docs/superpowers/**`

- [ ] Write or identify the failing contract/test that expresses the acceptance criteria.
- [ ] Implement the smallest behavior change that satisfies the issue without fallback paths.
- [ ] Update docs, registries, source manifests, or capability evidence only when behavior changed.

### Task 3: Validate And Handoff

**Files:**
- `packages/epcsaft-regression/**`
- `packages/epcsaft-regression/tests/**`
- `tests/workflows/repo/**`
- `docs/superpowers/**`

- [ ] Run the proof oracle commands that apply to the changed files.
- [ ] Run `uv run python scripts/dev/validate_project.py quick` unless a narrower documented validation is sufficient and recorded.
- [ ] Prepare PR-ready evidence that closes GitHub issue #193.

## Proof Oracle

- Run docs validation after the local plan and mirror are added.
- Confirm project fields and milestone assignment.
