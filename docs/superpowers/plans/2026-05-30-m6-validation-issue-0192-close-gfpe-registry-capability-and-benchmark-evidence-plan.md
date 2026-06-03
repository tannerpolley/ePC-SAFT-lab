# Close GFPE registry, capability, and benchmark evidence Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> `superpowers:subagent-driven-development` or `superpowers:executing-plans` to
> implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for
> tracking.

**Goal:** Resolve GitHub issue #192: Close GFPE registry, capability, and benchmark evidence.

**Architecture:** Keep the work inside the owning milestone/package boundary and
use the source spec plus GitHub issue as the behavior contract. Public capability
claims should move only when the proof oracle records matching evidence.

**Tech Stack:** Python, C++/pybind11 where the issue touches native code, CMake,
CppAD/Ceres/Ipopt only when required by the issue labels, pytest, GitHub Issues.

---

## Intake

- Source Spec: `docs/superpowers/specs/2026-05-30-m6-validation-issue-0192-close-gfpe-registry-capability-and-benchmark-evidence.md`
- Source Issue: `docs/superpowers/issues/2026-05-30-m6-validation-issue-0192-close-gfpe-registry-capability-and-benchmark-evidence.md`
- Source Plan: `docs/superpowers/plans/2026-05-30-m6-validation-issue-0192-close-gfpe-registry-capability-and-benchmark-evidence-plan.md`
- GitHub Issue: `https://github.com/ePC-SAFT/ePC-SAFT/issues/192`
- Milestone: `M6 - Validation`
- AFK/HITL: `HITL`

## Acceptance Criteria

- [ ] Algorithm registry entries point to executable GFPE evidence rather than planned-only claims.
- [ ] Capability evidence identifies proven neutral, associating, electrolyte, and reactive route scope separately.
- [ ] Benchmark or literature fixture metadata includes source, expected behavior, tolerances, and command receipts.
- [ ] Docs and tests fail if registry support claims outpace executable evidence.

## Tasks

### Task 1: Preflight And Boundary Check

**Files:**
- `analyses/**`
- `tests/native/contracts/**`
- `tests/workflows/repo/**`
- `docs/superpowers/**`
- `docs/pages/**`

- [ ] Confirm GitHub issue #192 is still `blocked` and verify blocker/design state before code changes.
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
- [ ] Prepare PR-ready evidence that closes GitHub issue #192.

## Proof Oracle

- Run capability evidence tests.
- Run benchmark/registry structural tests.
- Run docs validation.
