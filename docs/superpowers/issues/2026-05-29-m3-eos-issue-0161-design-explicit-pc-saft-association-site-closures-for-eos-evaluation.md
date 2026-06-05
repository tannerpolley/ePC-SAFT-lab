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
last_synced: "2026-06-05"
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

Capture the explicit PC-SAFT association-site Picard derivation as later EOS-provider work. Source note: `docs/latex/explicit_assocation.tex`.

## Supplemental Context

- Related paper-backed validation design:
  `docs/superpowers/specs/2026-06-03-m3-eos-paper-backed-association-closure-validation-matrix-design.md`.
- Huang/Radosz topology source markdown:
  `docs/papers/md/ePC-SAFT-Literature/Huang and Radosz - 1990 - Equation of State for Small, Large, Polydisperse, and Associating Molecules.md`.
- Any provider closure admission path should use the validation matrix to avoid
  treating the first synthetic toybox grids as sufficient real 2B/3B/4C
  evidence.
- Final M8 toybox admission evidence was closed by
  [issue #223](https://github.com/ePC-SAFT/ePC-SAFT/issues/223) and
  [PR #233](https://github.com/ePC-SAFT/ePC-SAFT/pull/233).
- Final Picard decision memo:
  `analyses/package_validation/explicit_association_toybox/docs/issue_161_picard_admission_decision.md`.
- Final retained evidence:
  `analyses/package_validation/explicit_association_toybox/figures/final_picard_admission_report/output/final_picard_admission_report.csv`.
- Post-#223 Picard stress evidence:
  `analyses/package_validation/explicit_association_toybox/figures/picard_stress_evidence/output/picard_stress_evidence.csv`.
- Post-#223 stress decision memo:
  `analyses/package_validation/explicit_association_toybox/docs/picard_stress_rescue_or_retire_decision.md`.
- The stress memo selects `retire_picard`, so #161 should close without a
  provider implementation unless a future spec introduces a different explicit
  closure candidate with stronger property and derivative evidence.
- Until the M8 decision memo explicitly recommends a narrow M3 provider
  admission issue, this issue remains design/admission evidence and is not
  provider implementation-ready.

## Acceptance Criteria

- [ ] Trace the current association implementation owner, site flattening/grouping convention, site multiplicities, active site-pair topology, association-strength matrix construction, and parameter units.
- [ ] Prove Tier 0 is inactive and bitwise or tolerance-equivalent to current EOS outputs.
- [ ] For Tier 1, test the 2B exact reduction against the exact mass-action solve on controlled pure and inert-partner EOS state grids and prove site fractions, `a_assoc`, pressure, residual chemical potentials, and fugacity coefficients match within stated tolerances.
- [ ] For Tier 2, separately test unequal multiplicities and density/composition-dependent strength terms before making any exactness claim.
- [ ] For Tier 3, evaluate fixed Picard policy settings as approximate explicit EOS models and report residual/error curves versus density, composition, association strength, and end-to-end simulation timing.
- [ ] For Tier 4, fail loudly or keep the explicit closure path unavailable until a separate derivation supports that configuration.
- [ ] For Tier 5, keep only the active Picard candidate in the analysis lane unless a separate issue approves another explicit approximation.
- [ ] Add derivative tests that compare closed-form and CppAD sensitivities of the explicit closure with independent implicit-sensitivity references where available.
- [ ] Document derivative semantics in code/docs: Explicit-closure derivatives are derivatives of the approximate explicit EOS, not automatically the exact implicit PC-SAFT association derivatives.
- [ ] Add topology-gating tests that prevent unsupported association configurations from silently using a closure outside its proven assumptions.
- [ ] Do not add fake fallbacks, hidden compatibility wrappers, broad capability claims, or silent clamps that hide invalid site fractions.

## Proof Oracle

- uv run python scripts/dev/validate_project.py quick
- uv run python run_pytest.py analyses/package_validation/explicit_association_toybox/tests/test_picard_policy_grid.py analyses/package_validation/explicit_association_toybox/tests/test_pure_saturation.py analyses/package_validation/explicit_association_toybox/tests/test_final_picard_admission_report.py -q
- uv run python analyses/package_validation/explicit_association_toybox/figures/final_picard_admission_report/scripts/generate_data.py
- uv run python analyses/package_validation/explicit_association_toybox/figures/final_picard_admission_report/scripts/render_figure.py
- uv run python run_pytest.py analyses/package_validation/explicit_association_toybox/tests/test_picard_stress_cases.py analyses/package_validation/explicit_association_toybox/tests/test_picard_stress_evidence.py analyses/package_validation/explicit_association_toybox/tests/test_picard_stress_derivatives.py analyses/package_validation/explicit_association_toybox/tests/test_picard_stress_objective_probe.py analyses/package_validation/explicit_association_toybox/tests/test_picard_stress_report.py -q
- uv run python analyses/package_validation/explicit_association_toybox/figures/picard_stress_evidence/scripts/generate_data.py
- uv run python analyses/package_validation/explicit_association_toybox/figures/picard_stress_evidence/scripts/render_figure.py

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
