# Move equilibrium objective assembly onto provider derivative bundles Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> `superpowers:subagent-driven-development` or `superpowers:executing-plans` to
> implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for
> tracking.

**Goal:** Resolve GitHub issue #208: Move equilibrium objective assembly onto provider derivative bundles.

**Architecture:** Keep the work inside the owning milestone/package boundary and
use the source spec plus GitHub issue as the behavior contract. Public capability
claims should move only when the proof oracle records matching evidence.

**Tech Stack:** Python, C++/pybind11 where the issue touches native code, CMake,
CppAD/Ceres/Ipopt only when required by the issue labels, pytest, GitHub Issues.

---

## Intake

- Source Spec: `docs/superpowers/specs/2026-06-01-m4-equilibrium-move-equilibrium-objective-assembly-to-extension.md`
- Source Issue: `docs/superpowers/issues/2026-06-01-m4-equilibrium-issue-0208-move-equilibrium-objective-assembly-onto-provider-derivative-bundles.md`
- Source Plan: `docs/superpowers/plans/2026-06-01-m4-equilibrium-issue-0208-move-equilibrium-objective-assembly-onto-provider-derivative-bundles-plan.md`
- GitHub Issue: `https://github.com/ePC-SAFT/ePC-SAFT/issues/208`
- Milestone: `M4 - Equilibrium`
- AFK/HITL: `HITL`

## Acceptance Criteria

- [ ] Equilibrium constructs pressure-transformed Helmholtz objective terms, gradients, Hessians, third-derivative tensors, and pressure-work derivatives from the provider derivative bundle.
- [ ] No provider API called by equilibrium requires `target_pressure` or returns a solver objective value as a provider-owned concept.
- [ ] `EosPhaseBlockResult` and NLP contract evidence keep existing public/test payload shapes and exact derivative backend labels.
- [ ] M4 native CMake/source lists and focused equilibrium tests use the new assembly path.
- [ ] This issue is blocked by the M3 provider derivative bundle issue until that provider contract is merged.

## Tasks

### Task 1: Preflight And Boundary Check

**Files:**
- `packages/epcsaft-equilibrium/**`
- `packages/epcsaft/tests/**`
- `tests/native/contracts/**`
- `tests/workflows/repo/**`
- `docs/superpowers/**`

- [ ] Confirm GitHub issue #208 is still `blocked` and verify blocker/design state before code changes.
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
- [ ] Prepare PR-ready evidence that closes GitHub issue #208.

## Proof Oracle

- `pwsh.exe -NoProfile -ExecutionPolicy Bypass -File scripts/dev/cmake_preset.ps1 -Action Build -Target epcsaft_equilibrium_native_core -Parallel 10`
- `uv run python run_pytest.py packages/epcsaft-equilibrium/tests/native/blocks/test_eos_phase_block.py packages/epcsaft-equilibrium/tests/native/diagnostics/test_selector_core_contracts.py packages/epcsaft-equilibrium/tests/api/test_bubble_derivatives.py -q`
- `uv run python scripts/dev/validate_project.py quick`
