---
issue: 161
title: "Design explicit PC-SAFT association-site closures for EOS evaluation"
url: "https://github.com/ePC-SAFT/ePC-SAFT/issues/161"
state: "open"
milestone: "M3 - EOS"
project: "ePC-SAFT Roadmap"
package: "core"
capability: "eos"
backend: "analytic"
readiness: "needs design"
release_target: "future"
source_spec: "docs/superpowers/specs/2026-05-23-m3-eos-explicit-association-closure-for-pcsaft.md"
source_plan: "docs/superpowers/plans/2026-05-29-m3-eos-issue-0161-design-explicit-pc-saft-association-site-closures-for-eos-evaluation-plan.md"
afk_hitl: "HITL"
branch: codex/issue-0161-design-explicit-pc-saft-association-site-closures-for-eos-evaluation
last_synced: "2026-06-02"
---

# Design explicit PC-SAFT association-site closures for EOS evaluation

GitHub Issue: https://github.com/ePC-SAFT/ePC-SAFT/issues/161
Source Spec: docs/superpowers/specs/2026-05-23-m3-eos-explicit-association-closure-for-pcsaft.md
Source Plan: docs/superpowers/plans/2026-05-29-m3-eos-issue-0161-design-explicit-pc-saft-association-site-closures-for-eos-evaluation-plan.md
Branch: codex/issue-0161-design-explicit-pc-saft-association-site-closures-for-eos-evaluation
AFK/HITL: HITL

GitHub remains authoritative for state, labels, Project fields, comments,
dependency edges, and PR linkage. This mirror exists so `project-resolve` can
start from a durable local source plan.

## Summary

Capture the explicit PC-SAFT association-site closure derivation as later EOS-provider work. Source note: `docs/derivation/explicit_association_closure_for_pcsaft.tex`.

## Supplemental Context

- none

## Acceptance Criteria

- [ ] Trace the current association implementation owner, site flattening/grouping convention, site multiplicities, active site-pair topology, association-strength matrix construction, and parameter units.
- [ ] Prove Tier 0 is inactive and bitwise or tolerance-equivalent to current EOS outputs.
- [ ] For Tier 1, test Closure A against the exact mass-action solve on controlled pure and inert-partner EOS state grids and prove site fractions, `a_assoc`, pressure, residual chemical potentials, and fugacity coefficients match within stated tolerances.
- [ ] For Tier 2, separately test unequal multiplicities and density/composition-dependent strength terms before making any exactness claim.
- [ ] For Tier 3, evaluate Closure B/C only as approximate explicit EOS models and report residual/error curves versus fixed depth, damping, density, composition, and association strength.
- [ ] For Tier 4, fail loudly or keep the explicit closure path unavailable until a separate derivation supports that configuration.
- [ ] For Tier 5, keep mean-field behavior diagnostic-only unless a separate issue defines production criteria.
- [ ] Add derivative tests that compare closed-form and CppAD sensitivities of the explicit closure with independent implicit-sensitivity references where available.
- [ ] Document derivative semantics in code/docs: Explicit-closure derivatives are derivatives of the approximate explicit EOS, not automatically the exact implicit PC-SAFT association derivatives.
- [ ] Add topology-gating tests that prevent unsupported association configurations from silently using a closure outside its proven assumptions.
- [ ] Do not add fake fallbacks, hidden compatibility wrappers, broad capability claims, or silent clamps that hide invalid site fractions.

## Proof Oracle

- uv run python scripts/dev/validate_project.py quick

## Non-Goals And Boundaries

- No unrelated package, milestone, or public API scope should be added.

## Tracker Metadata

- Milestone: `M3 - EOS`
- Package: `core`
- Capability: `eos`
- Backend: `analytic`
- Readiness: `needs design`
- AFK/HITL: `HITL`
- Release target: `future`
- Labels: `enhancement, native, validation, area:core, area:derivatives, status:needs-design, type:feature`
