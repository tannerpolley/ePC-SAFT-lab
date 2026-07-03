# M4 Khudaida Collapsed Electrolyte LLE Rejection

## Purpose

Create a solver-truthfulness issue for the Khudaida electrolyte LLE validation
path exposed by #407. The package public `electrolyte_lle` route currently
returns rows that are marked accepted even though the two phases are nearly
identical duplicated-feed states. The next repair must make those collapsed
rows fail loudly, then diagnose why the route converges to the trivial
stationary point instead of a noncollapsed LLE branch.

## Owning Milestone And Package

- GitHub milestone: `M4 - Equilibrium`
- Owning package: `packages/epcsaft-equilibrium`
- Proof fixture: `analyses/paper_validation/2026_khudaida/figures/figure_02`
- Related validation issue: #407
- Related parameter-regression issue: #338

This is M4 work because #407 explicitly routes solver/API defects to M4. M6
owns retained Khudaida figure evidence, while M5 #338 owns fitted-parameter
work if the M4 diagnosis proves the current route is correctly rejecting all
noncollapsed candidates for the retained parameter bundle.

## Verified Input Evidence

- Figure 2 uses Table 3, not Table 4: 293.15 K and 5 wt% NaCl source tie-line
  rows from `shared/source/table_3_4_experimental_tielines.csv`.
- Table 4 is the 10 wt% NaCl source table for later Khudaida figures.
- Retained Figure 2 feed rows invert to approximately 5.00 wt% NaCl, aqueous
  feed to isobutanol mass ratio near 1:1, and ethanol mass fractions spanning
  about 2.0 to 11.6 wt%, matching the paper's feed-preparation method.
- The current retained Figure 2 model rows report six accepted tie-lines with
  phase distances from about `1.7e-8` to `1.17e-7` and phase fractions near
  `0.99999 / 1e-5`.
- Tie-lines 6 and 7 currently fail postsolve certification.
- A direct midpoint feed probe for Table 3 tie-line 1 also converges to a
  collapsed split with phase distance about `1.0e-7` and phase fractions near
  `0.99999 / 7e-6`.

## Required Behavior

- Khudaida model-row generation must not classify a collapsed duplicate-feed
  state as a successful LLE split.
- The Khudaida checker must report collapsed rows as model-row solver failures,
  not only as high fit error.
- Public route diagnostics must retain enough evidence to distinguish:
  route branch-selection failure, route formulation/postsolve acceptance
  failure, and current-parameter noncollapsed infeasibility.
- If the diagnosis proves parameter regression is required, the M4 issue must
  keep #338 as the owner of fitted-parameter work and must not add hidden
  Khudaida parameters in the equilibrium route.

## Acceptance Metrics

- A Khudaida model row is noncollapsed only when the formula-basis
  phase-distance infinity norm is at least `1.0e-3`.
- A row with finite phase compositions but phase distance below `1.0e-3` is a
  solver failure for Khudaida reproduction, even if Ipopt and postsolve report
  residual feasibility.
- A row with minor phase fraction below `1.0e-4` must be retained with beta
  diagnostics and reviewed as collapsed or boundary-adjacent evidence; for
  Figure 2 current rows this is a failure because the phase compositions are
  also duplicate-feed states.
- The checker JSON must expose collapsed row identifiers, phase distance,
  phase-distance threshold, phase fractions, objective, route status, solver
  status, and root-cause bucket.

## Non-goals

- No parameter fitting in M4.
- No release claim.
- No broad electrolyte production claim.
- No private-only proof that bypasses the public
  `Equilibrium(..., route="electrolyte_lle")` path.
- No weakening of #407 retained source-data provenance.
