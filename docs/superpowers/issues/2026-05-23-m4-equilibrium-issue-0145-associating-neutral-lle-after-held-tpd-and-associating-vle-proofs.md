---
issue: 145
title: "Associating neutral LLE after HELD/TPD and associating VLE proofs"
url: https://github.com/ePC-SAFT/ePC-SAFT/issues/145
state: closed
milestone: "M4 - Equilibrium"
project: "ePC-SAFT Roadmap"
package: equilibrium
capability: lle
backend: Ipopt
readiness: closed
release_target: equilibrium-0.x
source_spec: null
source_plan: null
afk_hitl: HITL
branch: null
last_synced: "2026-07-12"
---

**Source-faithful historical classification (2026-07-12):** Preserve the exact association, local-equilibrium, or source-fixture evidence as internal component evidence only. It does not establish Pereira HELD parity, globally complete neutral or associating phase discovery, or public LLE admission. Literature and model reproduction belong to M6; runtime exposure remains governed by the native activation descriptor.

# Associating neutral LLE after HELD/TPD and associating VLE proofs

**Mirror Retention:** Keep

GitHub Issue: https://github.com/ePC-SAFT/ePC-SAFT/issues/145
Source Spec: docs/superpowers/specs/2026-05-23-m4-equilibrium-issue-0145-associating-neutral-lle-after-held-tpd-and-associating-vle-proofs.md
Source Plan: docs/superpowers/plans/2026-05-23-m4-equilibrium-issue-0145-associating-neutral-lle-after-held-tpd-and-associating-vle-proofs-plan.md
Branch: closed by PR #273
AFK/HITL: HITL

GitHub remains authoritative for state, labels, Project fields, comments,
dependency edges, and PR linkage. This mirror exists so `project-resolve` can
start from a durable local source plan.

## Summary

#145 closed through PR #273 with its source-backed neutral associating LLE proof
scope satisfied. The proof exercises the implicit association state, Jacobian,
and Hessian path using real Gross and Sadowski 2002 evidence while keeping
public associating GFPE admission closed for #190.

The first validation target is methanol/cyclohexane at 1.013 bar from Gross and
Sadowski 2002, Figure 8, with pure-component and binary-interaction parameters
from the retained 2002 Gross paper-validation bundle. The water/1-pentanol
Figure 10 case is follow-on stress evidence only and must not broaden the #145
completion claim.

## Supplemental Context

- `docs/superpowers/milestones/M4-equilibrium/generalized-fluid-phase-equilibrium.md`
- `docs/superpowers/specs/2026-05-26-m4-equilibrium-stage-by-stage-implementation-plan.md`
- `docs/superpowers/specs/2026-05-23-m3-eos-explicit-association-closure-for-pcsaft.md`
- `docs/superpowers/specs/2026-06-11-m4-equilibrium-held-1-0-full-adoption.md`
- `analyses/paper_validation/2002_gross/docs/md/source_01_gross_2002.md`
- `analyses/paper_validation/2002_gross/tables/table_001/table_001.csv`
- `analyses/paper_validation/2002_gross/tables/table_002/table_002.csv`
- `analyses/paper_validation/2002_gross/parameters/`
- `analyses/paper_validation/2002_gross/figures/figure_08/source/paper_source_01_gross_2002_figure_008.png`

## Acceptance Criteria

- [x] Gross and Sadowski 2002 methanol/cyclohexane source data, parameters, and
  thresholds are retained in the repo and checked by a replayable validation
  command.
- [x] Active association reports bounded site fractions, low mass-action
  residuals, exact first sensitivities, and exact second sensitivities for every
  solved liquid phase in the proof fixture.
- [x] The native equilibrium block and phase-system diagnostics report exact
  association Hessian coverage, including objective, pressure, mass-action, and
  Lagrangian-Hessian evidence.
- [x] The associating LLE proof route solves or certifies the source-backed
  methanol/cyclohexane split without weakening neutral HELD/TPD postsolve
  checks.
- [x] Public `Equilibrium(..., route="lle")` associating admission remains
  closed until #190; #145 records internal proof evidence only.
- [x] GitHub issue #145 outcome is satisfied without broadening unrelated
  package capability claims.

## Implementation Evidence

The branch-local #145 proof is complete when the proof oracle below passes. The
proof remains internal: `epcsaft_equilibrium.capabilities()` records
`associating_neutral_lle_gross_2002_internal_exact_hessian` as
`internal_proof_closed_until_issue_190`, and the public `lle` route remains
mapped to `neutral_lle` for nonassociating inputs only.

The retained checker reports Gross/Sadowski 2002 Figure 8 source rows, Table 1
methanol 2B parameters, the retained cyclohexane PC-SAFT row, Table 2
`k_ij = 0.051`, bounded site fractions, mass-action residuals below `1.0e-8`,
exact association first and second site sensitivities, symmetric
objective/pressure/mass-action/Lagrangian Hessian evidence, an internal
source-pair certification, and `closed_for_associating_inputs` public route
state.

## Proof Oracle

- `uv run python scripts/validation/check_associating_lle_gross_2002.py --json --require-source-data --require-exact-association-hessian --require-route-closed --require-complete`
- `uv run python run_pytest.py packages/epcsaft/tests/native/contracts/test_association_implicit_derivative_contract.py packages/epcsaft/tests/native/state/test_phase_state_sensitivities.py packages/epcsaft/tests/native/state/test_fugacity_derivatives.py packages/epcsaft-equilibrium/tests/native/blocks/test_association_block.py packages/epcsaft-equilibrium/tests/native/blocks/test_eos_phase_block.py -q`
- `uv run python run_pytest.py packages/epcsaft-equilibrium/tests/native/results/test_associating_lle_reference_values.py tests/native/contracts/test_associating_lle_gross_2002_checker.py packages/epcsaft-equilibrium/tests/contracts/test_activation_capabilities.py -q`
- `uv run python scripts/dev/validate_project.py quick`

## Non-Goals And Boundaries

- No public associating GFPE admission in #145.
- No electrolyte route behavior or electrolyte capability claim.
- No reactive, CE, CPE, LLLE, or generalized associating phase-set admission.
- No approximate explicit association closure accepted as exact evidence.
- No broad associating phase-count claim from the methanol/cyclohexane proof.
- No unrelated package, milestone, or public API scope should be added.

## Tracker Metadata

- Milestone: `M4 - Equilibrium`
- Package: `equilibrium`
- Capability: `lle`
- Backend: `Ipopt`
- Readiness: `closed`
- AFK/HITL: `HITL`
- Release target: `equilibrium-0.x`
- Labels: `python-api, native, solver, docs, validation, equilibrium, area:equilibrium, backend:ipopt, status:ready, type:feature`
