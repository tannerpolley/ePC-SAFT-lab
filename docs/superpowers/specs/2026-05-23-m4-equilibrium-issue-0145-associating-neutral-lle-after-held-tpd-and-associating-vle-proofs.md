# Associating neutral LLE after HELD/TPD and associating VLE proofs

Milestone: `M4 - Equilibrium`
Issue: `https://github.com/ePC-SAFT/ePC-SAFT/issues/145`
Status: `open`
Last synced: `2026-06-18`

## Summary

#148 is closed, so the native GitHub dependency blocker is satisfied and #145 is
ready. This issue owns the first source-backed neutral associating LLE proof
before public associating GFPE admission. It must prove the implicit association
state, Jacobian, and Hessian path using real Gross and Sadowski 2002 evidence,
then keep public associating GFPE admission closed for #190.

The first validation target is methanol/cyclohexane at 1.013 bar from Gross and
Sadowski 2002, Figure 8, with pure-component and binary-interaction parameters
from the retained 2002 Gross paper-validation bundle. The follow-on stress case
for broader confidence is water/1-pentanol from the same paper, Figure 10, but
that stress case must not broaden the #145 completion claim by itself.

## Acceptance Gates

- [ ] Gross and Sadowski 2002 methanol/cyclohexane source data, parameters, and
  thresholds are retained in the repo and are checked by a replayable validation
  command.
- [ ] Active association reports bounded site fractions, low mass-action
  residuals, exact first sensitivities, and exact second sensitivities for every
  solved liquid phase in the proof fixture.
- [ ] The native equilibrium block and phase-system diagnostics report exact
  association Hessian coverage, including objective, pressure, mass-action, and
  Lagrangian-Hessian evidence.
- [ ] The associating LLE proof route solves or certifies the source-backed
  methanol/cyclohexane split without weakening neutral HELD/TPD postsolve
  checks.
- [ ] Public `Equilibrium(..., route="lle")` associating admission remains
  closed until #190; #145 records internal proof evidence only.
- [ ] GitHub issue #145 outcome is satisfied without broadening unrelated
  package capability claims.

## Source Context

- `docs/superpowers/milestones/M4-equilibrium/generalized-fluid-phase-equilibrium.md`
- `docs/superpowers/specs/2026-05-26-m4-equilibrium-stage-by-stage-implementation-plan.md`
- `docs/superpowers/specs/2026-05-23-m3-eos-explicit-association-closure-for-pcsaft.md`
- `docs/superpowers/specs/2026-06-11-m4-equilibrium-held-1-0-full-adoption.md`
- `analyses/paper_validation/2002_gross/docs/md/source_01_gross_2002.md`
- `analyses/paper_validation/2002_gross/tables/table_001/table_001.csv`
- `analyses/paper_validation/2002_gross/tables/table_002/table_002.csv`
- `analyses/paper_validation/2002_gross/parameters/`
- `analyses/paper_validation/2002_gross/figures/figure_08/source/paper_source_01_gross_2002_figure_008.png`

## Implementation Notes

- Keep this issue in `equilibrium` scope unless the
  GitHub issue explicitly approves cross-milestone work.
- Preserve capability claims and backend labels unless the proof oracle records
  matching implementation evidence.
- Use the linked issue mirror and plan as the execution entry points for
  `project-resolve`.
- HELD is the Pereira algorithm acronym in this repo context; do not use Held
  electrolyte papers as HELD 1.0 algorithm evidence.
- #190 stays blocked by #145. #191 electrolyte work must wait until the
  associating proof and associating GFPE admission gates are resolved or
  explicitly left closed.

## Non-Goals

- No unrelated package, milestone, or public API scope should be added.
- No electrolyte, reactive, CE, CPE, LLLE, or generalized associating phase-set
  admission.
- No approximate explicit association closure as exact production evidence.

## Validation

- `uv run python scripts/validation/check_associating_lle_gross_2002.py --json --require-source-data --require-exact-association-hessian --require-route-closed --require-complete`
- `uv run python run_pytest.py packages/epcsaft/tests/native/contracts/test_association_implicit_derivative_contract.py packages/epcsaft/tests/native/state/test_phase_state_sensitivities.py packages/epcsaft-equilibrium/tests/native/blocks/test_association_block.py packages/epcsaft-equilibrium/tests/native/blocks/test_eos_phase_block.py -q`
- `uv run python run_pytest.py packages/epcsaft-equilibrium/tests/native/results/test_associating_lle_reference_values.py tests/native/contracts/test_associating_lle_gross_2002_checker.py -q`
- `uv run python scripts/dev/validate_project.py quick`
