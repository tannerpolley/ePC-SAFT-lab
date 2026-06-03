# Re-open executable literature benchmark and capability evidence backlog Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> `superpowers:subagent-driven-development` or `superpowers:executing-plans` to
> implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for
> tracking.

**Goal:** Resolve GitHub issue #194: Re-open executable literature benchmark and capability evidence backlog.

**Architecture:** Keep the work inside the owning milestone/package boundary and
use the source spec plus GitHub issue as the behavior contract. Public capability
claims should move only when the proof oracle records matching evidence.

**Tech Stack:** Python, C++/pybind11 where the issue touches native code, CMake,
CppAD/Ceres/Ipopt only when required by the issue labels, pytest, GitHub Issues.

---

## Intake

- Source Spec: `docs/superpowers/specs/2026-05-29-m6-validation-validation-benchmark-backlog.md`
- Source Issue: `docs/superpowers/issues/2026-05-30-m6-validation-issue-0194-re-open-executable-literature-benchmark-and-capability-evidence-backlog.md`
- Source Plan: `docs/superpowers/plans/2026-05-30-m6-validation-issue-0194-re-open-executable-literature-benchmark-and-capability-evidence-backlog-plan.md`
- GitHub Issue: `https://github.com/ePC-SAFT/ePC-SAFT/issues/194`
- Milestone: `M6 - Validation`
- AFK/HITL: `HITL`

## Acceptance Criteria

- [ ] Benchmark families are inventoried with source, fixture, expected behavior, tolerance, and command requirements.
- [ ] Capability evidence rules define when docs may claim support.
- [ ] Registry/docs/test ownership is clear across provider, equilibrium, regression, and cross-package lanes.
- [ ] Release-quality validation gates are separated from ordinary PR local-proof gates.

## Tasks

### Task 1: Preflight And Boundary Check

**Files:**
- `analyses/**`
- `tests/native/contracts/**`
- `tests/workflows/repo/**`
- `docs/superpowers/**`
- `docs/pages/**`

- [ ] Confirm GitHub issue #194 is still `needs design` and verify blocker/design state before code changes.
- [ ] Read the source spec, issue mirror, GitHub issue, and milestone README.
- [ ] Confirm candidate file ownership and reject unrelated package or milestone scope.
- [ ] Select the smallest validation slice that proves the issue behavior.

### Task 2: Implement The Issue Slice

**Files:**
- `analyses/**`
- `tests/native/contracts/**`
- `tests/workflows/repo/**`
- `docs/superpowers/**`
- `docs/pages/**`

- [ ] Write or identify the failing contract/test that expresses the acceptance criteria.
- [ ] Implement the smallest behavior change that satisfies the issue without fallback paths.
- [ ] Update docs, registries, source manifests, or capability evidence only when behavior changed.

### Task 3: Validate And Handoff

**Files:**
- `analyses/**`
- `tests/native/contracts/**`
- `tests/workflows/repo/**`
- `docs/superpowers/**`
- `docs/pages/**`

- [ ] Run the proof oracle commands that apply to the changed files.
- [ ] Run `uv run python scripts/dev/validate_project.py quick` unless a narrower documented validation is sufficient and recorded.
- [ ] Prepare PR-ready evidence that closes GitHub issue #194.

## Proof Oracle

- Run docs validation after the local plan and mirror are added.
- Confirm project fields and milestone assignment.
