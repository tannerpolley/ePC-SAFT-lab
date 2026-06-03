# Derive boundary workflows and generalized phase-set PE from neutral GFPE Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> `superpowers:subagent-driven-development` or `superpowers:executing-plans` to
> implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for
> tracking.

**Goal:** Resolve GitHub issue #189: Derive boundary workflows and generalized phase-set PE from neutral GFPE.

**Architecture:** Keep the work inside the owning milestone/package boundary and
use the source spec plus GitHub issue as the behavior contract. Public capability
claims should move only when the proof oracle records matching evidence.

**Tech Stack:** Python, C++/pybind11 where the issue touches native code, CMake,
CppAD/Ceres/Ipopt only when required by the issue labels, pytest, GitHub Issues.

---

## Intake

- Source Spec: `docs/superpowers/specs/2026-05-30-m4-equilibrium-issue-0189-derive-boundary-workflows-and-generalized-phase-set-pe-from-neutral-gfpe.md`
- Source Issue: `docs/superpowers/issues/2026-05-30-m4-equilibrium-issue-0189-derive-boundary-workflows-and-generalized-phase-set-pe-from-neutral-gfpe.md`
- Source Plan: `docs/superpowers/plans/2026-05-30-m4-equilibrium-issue-0189-derive-boundary-workflows-and-generalized-phase-set-pe-from-neutral-gfpe-plan.md`
- GitHub Issue: `https://github.com/ePC-SAFT/ePC-SAFT/issues/189`
- Milestone: `M4 - Equilibrium`
- AFK/HITL: `HITL`

## Acceptance Criteria

- [ ] Boundary workflows are derived from the certified neutral GFPE path, not special-cased route copies.
- [ ] Generalized phase-set PE exposes deterministic diagnostics for selected and rejected phase sets.
- [ ] Tests cover phase-set selection, conservation, residuals, and rejection of uncertified solutions.
- [ ] Docs explain what generalized phase-set behavior is supported and what remains blocked.

## Tasks

### Task 1: Preflight And Boundary Check

**Files:**
- `packages/epcsaft-equilibrium/**`
- `packages/epcsaft/tests/**`
- `tests/native/contracts/**`
- `tests/workflows/repo/**`
- `docs/superpowers/**`

- [ ] Confirm GitHub issue #189 is still `blocked` and verify blocker/design state before code changes.
- [ ] Read the source spec, issue mirror, GitHub issue, and milestone README.
- [ ] Confirm candidate file ownership and reject unrelated package or milestone scope.
- [ ] Select the smallest validation slice that proves the issue behavior.

### Task 2: Implement The Issue Slice

**Files:**
- `packages/epcsaft-equilibrium/**`
- `packages/epcsaft/tests/**`
- `tests/native/contracts/**`
- `tests/workflows/repo/**`
- `docs/superpowers/**`

- [ ] Write or identify the failing contract/test that expresses the acceptance criteria.
- [ ] Implement the smallest behavior change that satisfies the issue without fallback paths.
- [ ] Update docs, registries, source manifests, or capability evidence only when behavior changed.

### Task 3: Validate And Handoff

**Files:**
- `packages/epcsaft-equilibrium/**`
- `packages/epcsaft/tests/**`
- `tests/native/contracts/**`
- `tests/workflows/repo/**`
- `docs/superpowers/**`

- [ ] Run the proof oracle commands that apply to the changed files.
- [ ] Run `uv run python scripts/dev/validate_project.py quick` unless a narrower documented validation is sufficient and recorded.
- [ ] Prepare PR-ready evidence that closes GitHub issue #189.

## Proof Oracle

- Run focused equilibrium phase-set workflow tests.
- Run native contracts.
- Run docs validation.
