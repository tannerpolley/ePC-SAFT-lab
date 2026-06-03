# Re-open downstream install, PyPI, and migration proof backlog Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> `superpowers:subagent-driven-development` or `superpowers:executing-plans` to
> implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for
> tracking.

**Goal:** Resolve GitHub issue #195: Re-open downstream install, PyPI, and migration proof backlog.

**Architecture:** Keep the work inside the owning milestone/package boundary and
use the source spec plus GitHub issue as the behavior contract. Public capability
claims should move only when the proof oracle records matching evidence.

**Tech Stack:** Python, C++/pybind11 where the issue touches native code, CMake,
CppAD/Ceres/Ipopt only when required by the issue labels, pytest, GitHub Issues.

---

## Intake

- Source Spec: `docs/superpowers/specs/2026-05-29-m7-release-release-downstream-backlog.md`
- Source Issue: `docs/superpowers/issues/2026-05-30-m7-release-issue-0195-re-open-downstream-install-pypi-and-migration-proof-backlog.md`
- Source Plan: `docs/superpowers/plans/2026-05-30-m7-release-issue-0195-re-open-downstream-install-pypi-and-migration-proof-backlog-plan.md`
- GitHub Issue: `https://github.com/ePC-SAFT/ePC-SAFT/issues/195`
- Milestone: `M7 - Release`
- AFK/HITL: `HITL`

## Acceptance Criteria

- [ ] Install proof scope covers epcsaft, epcsaft-equilibrium, epcsaft-regression, and all-three combinations.
- [ ] Downstream migration proof requires real downstream workflows without private upstream workarounds.
- [ ] PyPI/trusted-publisher release choreography is documented as release work, not ordinary PR proof.
- [ ] Docs explain monorepo source-of-truth behavior for release consumers.

## Tasks

### Task 1: Preflight And Boundary Check

**Files:**
- `pyproject.toml`
- `packages/**`
- `scripts/dev/**`
- `docs/pages/**`
- `docs/superpowers/**`

- [ ] Confirm GitHub issue #195 is still `needs design` and verify blocker/design state before code changes.
- [ ] Read the source spec, issue mirror, GitHub issue, and milestone README.
- [ ] Confirm candidate file ownership and reject unrelated package or milestone scope.
- [ ] Select the smallest validation slice that proves the issue behavior.

### Task 2: Implement The Issue Slice

**Files:**
- `pyproject.toml`
- `packages/**`
- `scripts/dev/**`
- `docs/pages/**`
- `docs/superpowers/**`

- [ ] Write or identify the failing contract/test that expresses the acceptance criteria.
- [ ] Implement the smallest behavior change that satisfies the issue without fallback paths.
- [ ] Update docs, registries, source manifests, or capability evidence only when behavior changed.

### Task 3: Validate And Handoff

**Files:**
- `pyproject.toml`
- `packages/**`
- `scripts/dev/**`
- `docs/pages/**`
- `docs/superpowers/**`

- [ ] Run the proof oracle commands that apply to the changed files.
- [ ] Run `uv run python scripts/dev/validate_project.py quick` unless a narrower documented validation is sufficient and recorded.
- [ ] Prepare PR-ready evidence that closes GitHub issue #195.

## Proof Oracle

- Run docs validation after the local plan and mirror are added.
- Confirm project fields and milestone assignment.
