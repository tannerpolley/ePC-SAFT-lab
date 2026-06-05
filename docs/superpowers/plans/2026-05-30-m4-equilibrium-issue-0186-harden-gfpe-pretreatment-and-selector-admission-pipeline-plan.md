# Harden GFPE pretreatment and selector admission pipeline Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> `superpowers:subagent-driven-development` or `superpowers:executing-plans` to
> implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for
> tracking.

**Goal:** Resolve GitHub issue #186: Harden GFPE pretreatment and selector admission pipeline.

**Architecture:** Keep the work inside the owning milestone/package boundary and
use the source spec plus GitHub issue as the behavior contract. Public capability
claims should move only when the proof oracle records matching evidence.

**Tech Stack:** Python, C++/pybind11 where the issue touches native code, CMake,
CppAD/Ceres/Ipopt only when required by the issue labels, pytest, GitHub Issues.

---

## Intake

- Source Spec: `docs/superpowers/specs/2026-05-30-m4-equilibrium-issue-0186-harden-gfpe-pretreatment-and-selector-admission-pipeline.md`
- Source Issue: `docs/superpowers/issues/2026-05-30-m4-equilibrium-issue-0186-harden-gfpe-pretreatment-and-selector-admission-pipeline.md`
- Source Plan: `docs/superpowers/plans/2026-05-30-m4-equilibrium-issue-0186-harden-gfpe-pretreatment-and-selector-admission-pipeline-plan.md`
- GitHub Issue: `https://github.com/ePC-SAFT/ePC-SAFT/issues/186`
- Milestone: `M4 - Equilibrium`
- AFK/HITL: `AFK`

## Acceptance Criteria

- [ ] GFPE input and runtime state contracts are package-owned and deterministic.
- [ ] Pretreatment and selector/admission logic has focused tests for admissible and rejected route states.
- [ ] Legacy route-specific assumptions are either removed or isolated behind explicit tests.
- [ ] Capability evidence remains conservative and does not broaden production routes.
- [ ] Docs and local mirrors identify this as a ready M4 selector/admission verification issue.

## Current Scope Note

This plan is now a verification and closure slice for the existing
selector/admission path, not a broad new GFPE implementation. Current code
already exposes selector request pretreatment, route-shape validation,
thermodynamic input classification, parameter readiness checks, activation-plan
validation, and activation-matrix production-certification enforcement. Keep the
native activation matrix as the admission source of truth; do not admit
associating, electrolyte, or reactive routes, bypass `NlpProblem`, or expand
public capability claims without matching executable evidence.

## Tasks

### Task 1: Preflight And Boundary Check

**Files:**
- `packages/epcsaft-equilibrium/**`
- `packages/epcsaft-equilibrium/tests/**`
- `tests/native/contracts/test_generalized_equilibrium_registry.py`
- `docs/superpowers/**`

- [ ] Read the source spec, issue mirror, GitHub issue, and milestone README.
- [ ] Confirm candidate file ownership and reject unrelated package or milestone scope.
- [ ] Confirm current selector/admission evidence before adding code.
- [ ] Select the smallest validation slice that proves the issue behavior.

### Task 2: Verify Or Implement The Narrow Admission Slice

**Files:**
- `packages/epcsaft-equilibrium/**`
- `packages/epcsaft-equilibrium/tests/**`
- `tests/native/contracts/test_generalized_equilibrium_registry.py`
- `docs/superpowers/**`

- [ ] Identify whether existing selector tests cover route-shape rejection, neutral/ionic/associating classification, binary-interaction readiness, and activation certification.
- [ ] Write a failing package-local selector/admission contract only for a real uncovered gap.
- [ ] Implement the smallest behavior change that satisfies the issue without fallback paths.
- [ ] Preserve `activation_matrix.h` as the production-admission source of truth.
- [ ] Update docs, registries, source manifests, or capability evidence only when behavior changed.

### Task 3: Validate And Handoff

**Files:**
- `packages/epcsaft-equilibrium/**`
- `packages/epcsaft-equilibrium/tests/**`
- `tests/native/contracts/test_generalized_equilibrium_registry.py`
- `docs/superpowers/**`

- [ ] Run the proof oracle commands that apply to the changed files.
- [ ] Run `uv run python scripts/dev/validate_project.py quick` unless a narrower documented validation is sufficient and recorded.
- [ ] Prepare PR-ready evidence that closes GitHub issue #186.

## Proof Oracle

- `uv run python run_pytest.py packages/epcsaft-equilibrium/tests/native/diagnostics/test_selector_core_contracts.py packages/epcsaft-equilibrium/tests/contracts/test_activation_capabilities.py -q`
- `uv run python run_pytest.py --native-contracts -q`
- `uv run python scripts/dev/validate_project.py docs`
- `uv run python scripts/dev/validate_project.py quick`
