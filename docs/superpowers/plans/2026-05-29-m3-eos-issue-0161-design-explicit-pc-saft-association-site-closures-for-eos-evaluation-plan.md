# Design explicit PC-SAFT association-site closures for EOS evaluation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> `superpowers:subagent-driven-development` or `superpowers:executing-plans` to
> implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for
> tracking.

**Goal:** Resolve GitHub issue #161: Design explicit PC-SAFT association-site closures for EOS evaluation.

**Architecture:** Keep the work inside the owning milestone/package boundary and
use the source spec plus GitHub issue as the behavior contract. Public capability
claims should move only when the proof oracle records matching evidence.

**Tech Stack:** Python, C++/pybind11 where the issue touches native code, CMake,
CppAD/Ceres/Ipopt only when required by the issue labels, pytest, GitHub Issues.

---

## Intake

- Source Spec: `docs/superpowers/specs/2026-05-23-m3-eos-explicit-association-closure-for-pcsaft.md`
- Source Issue: `docs/superpowers/issues/2026-05-29-m3-eos-issue-0161-design-explicit-pc-saft-association-site-closures-for-eos-evaluation.md`
- Source Plan: `docs/superpowers/plans/2026-05-29-m3-eos-issue-0161-design-explicit-pc-saft-association-site-closures-for-eos-evaluation-plan.md`
- GitHub Issue: `https://github.com/ePC-SAFT/ePC-SAFT/issues/161`
- Milestone: `M3 - EOS`
- AFK/HITL: `HITL`
- Related validation design:
  `docs/superpowers/specs/2026-06-03-m3-eos-paper-backed-association-closure-validation-matrix-design.md`
- Huang/Radosz topology source:
  `docs/papers/md/ePC-SAFT-Literature/Huang and Radosz - 1990 - Equation of State for Small, Large, Polydisperse, and Associating Molecules.md`

## Acceptance Criteria

- [ ] Trace the current association implementation owner, site flattening/grouping convention, site multiplicities, active site-pair topology, association-strength matrix construction, and parameter units.
- [ ] Prove Tier 0 is inactive and bitwise or tolerance-equivalent to current EOS outputs.
- [ ] For Tier 1, test the 2B exact reduction against the exact mass-action solve on controlled pure and inert-partner EOS state grids and prove site fractions, `a_assoc`, pressure, residual chemical potentials, and fugacity coefficients match within stated tolerances.
- [ ] For Tier 2, separately test unequal multiplicities and density/composition-dependent strength terms before making any exactness claim.
- [ ] For Tier 3, evaluate only `damped_picard_7_05` as an approximate explicit EOS model and report residual/error curves versus density, composition, and association strength.
- [ ] For Tier 4, fail loudly or keep the explicit closure path unavailable until a separate derivation supports that configuration.
- [ ] For Tier 5, keep only the active Picard candidate in the analysis lane unless a separate issue approves another explicit approximation.
- [ ] Add derivative tests that compare closed-form and CppAD sensitivities of the explicit closure with independent implicit-sensitivity references where available.
- [ ] Document derivative semantics in code/docs: Explicit-closure derivatives are derivatives of the approximate explicit EOS, not automatically the exact implicit PC-SAFT association derivatives.
- [ ] Add topology-gating tests that prevent unsupported association configurations from silently using a closure outside its proven assumptions.
- [ ] Do not add fake fallbacks, hidden compatibility wrappers, broad capability claims, or silent clamps that hide invalid site fractions.

## Tasks

### Task 1: Preflight And Boundary Check

**Files:**
- `packages/epcsaft/**`
- `packages/epcsaft/tests/**`
- `tests/native/contracts/**`
- `docs/superpowers/**`

- [ ] Confirm GitHub issue #161 is still `needs design` and verify blocker/design state before code changes.
- [ ] Read the source spec, issue mirror, GitHub issue, and milestone README.
- [ ] Read the related paper-backed validation matrix spec before claiming
      topology coverage or real 2B/3B/4C evidence.
- [ ] Confirm candidate file ownership and reject unrelated package or milestone scope.
- [ ] Select the smallest validation slice that proves the issue behavior.

### Task 2: Implement The Issue Slice

**Files:**
- `packages/epcsaft/**`
- `packages/epcsaft/tests/**`
- `tests/native/contracts/**`
- `docs/superpowers/**`

- [ ] Write or identify the failing contract/test that expresses the acceptance criteria.
- [ ] Implement the smallest behavior change that satisfies the issue without fallback paths.
- [ ] Update docs, registries, source manifests, or capability evidence only when behavior changed.

### Task 3: Validate And Handoff

**Files:**
- `packages/epcsaft/**`
- `packages/epcsaft/tests/**`
- `tests/native/contracts/**`
- `docs/superpowers/**`

- [ ] Run the proof oracle commands that apply to the changed files.
- [ ] Run `uv run python scripts/dev/validate_project.py quick` unless a narrower documented validation is sufficient and recorded.
- [ ] Prepare PR-ready evidence that closes GitHub issue #161.

## Proof Oracle

- uv run python scripts/dev/validate_project.py quick
