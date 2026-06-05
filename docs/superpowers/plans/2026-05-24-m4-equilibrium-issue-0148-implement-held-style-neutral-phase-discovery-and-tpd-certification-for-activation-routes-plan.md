# Implement HELD-style neutral phase discovery and TPD certification for activation routes Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> `superpowers:subagent-driven-development` or `superpowers:executing-plans` to
> implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for
> tracking.

**Goal:** Resolve GitHub issue #148: Implement HELD-style neutral phase discovery and TPD certification for activation routes.

**Architecture:** Keep the work inside the owning milestone/package boundary and
use the source spec plus GitHub issue as the behavior contract. Public capability
claims should move only when the proof oracle records matching evidence.

**Tech Stack:** Python, C++/pybind11 where the issue touches native code, CMake,
CppAD/Ceres/Ipopt only when required by the issue labels, pytest, GitHub Issues.

---

## Intake

- Source Spec: `docs/superpowers/specs/2026-05-24-m4-equilibrium-issue-0148-implement-held-style-neutral-phase-discovery-and-tpd-certification-for-activation-routes.md`
- Source Issue: `docs/superpowers/issues/2026-05-24-m4-equilibrium-issue-0148-implement-held-style-neutral-phase-discovery-and-tpd-certification-for-activation-routes.md`
- Source Plan: `docs/superpowers/plans/2026-05-24-m4-equilibrium-issue-0148-implement-held-style-neutral-phase-discovery-and-tpd-certification-for-activation-routes-plan.md`
- GitHub Issue: `https://github.com/ePC-SAFT/ePC-SAFT/issues/148`
- Milestone: `M4 - Equilibrium`
- AFK/HITL: `AFK`

## Acceptance Criteria

- [ ] A neutral TPD evaluator exists with deterministic tests.
- [ ] A volume-composition trial-phase path can use existing EOS phase-state data without hidden pressure-root derivative dependence in production callbacks.
- [ ] Candidate phases can be generated, de-duplicated, and ranked.
- [ ] Candidate phase fractions can be selected or rejected by material-balance feasibility.
- [ ] Neutral flash/LLE seed generation can consume the candidate set.
- [ ] Postsolve certification checks per-phase stability, phase-set candidate completeness, conservation, pressure, fugacity/chemical-potential residuals, phase distinctness, and route diagnostics.
- [ ] Tests prove an optimizer-converged but uncertified or unstable point is not `production_accepted`.
- [ ] Capabilities do not broaden public route support.
- [ ] Algorithm registry and roadmap docs remain synchronized.

## Current Scope Note

This plan should resolve the existing Stage 9 neutral evidence path rather than
inventing a parallel HELD route. Current code already exposes deterministic
screening, continuous TPD, HELD Stage I diagnostics, a finite-candidate Stage II
bound audit, and current-route Stage III Ipopt refinement. Keep the native
activation matrix as admission control and keep generalized HELD claims limited
to the evidence proved by the commands below.

## Tasks

### Task 1: Preflight And Boundary Check

**Files:**
- `packages/epcsaft-equilibrium/**`
- `packages/epcsaft/tests/**`
- `tests/native/contracts/**`
- `tests/workflows/repo/**`
- `docs/superpowers/**`

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
- [ ] Prepare PR-ready evidence that closes GitHub issue #148.

## Proof Oracle

- `uv run python run_pytest.py packages/epcsaft-equilibrium/tests/native/diagnostics/test_selector_core_contracts.py packages/epcsaft-equilibrium/tests/contracts/test_activation_capabilities.py -q`
- `uv run python run_pytest.py --native-contracts -q`
- `uv run python scripts/validation/check_phase_discovery.py --json --include-route-refinement`
- `uv run python scripts/dev/validate_project.py docs`
- `uv run python scripts/dev/validate_project.py quick`
