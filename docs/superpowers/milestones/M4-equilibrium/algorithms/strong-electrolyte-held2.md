---
doctrine_schema_version: 1
algorithm_ids:
  - perdomo-held2
source_local_path: docs/papers/md/Equilibrium/Perdomo et al. - 2025 - Phase stability criteria and fluid-phase equilibria in strong-electrolyte systems.md
source_anchors:
  - section-2.2-electroneutrality-and-eliminated-species
  - section-3.2-modified-mole-coordinates
  - section-4-algorithm-1-three-stage-scheme
  - section-4.4-stage-iii-free-energy-minimization
stage_iii_primary_problem: direct-total-free-energy-minimization
residual_solve_role: optional-corrector-or-diagnostic
interphase_stationarity: independent-modified-potential-equality
individual_ionic_potential_comparison_requires: explicit-galvani-convention
runtime_status: closed
algorithm_parity_status: incomplete
stage_ii_status: not-executed
stage_iii_status: not-executed
---

# Perdomo HELD2 For Strong Electrolytes

## Identity And Scope

Perdomo and coauthors extend the Pereira three-stage construction to fluid
mixtures containing strong, fully dissociated electrolytes. Their scope is
nonreactive phase equilibrium. It excludes weak-electrolyte speciation,
chemical reactions, and solid or hydrate phases.

The paper demonstrates HELD2 with electrolyte SAFT-gamma Mie. Those results do
not establish ePC-SAFT model parity. Its multistart and tunnelling searches also
do not provide a deterministic finite-time global guarantee.

Local source: Perdomo et al. 2025, Sections 2.2, 3.2, 4, and 4.4 in the paper
named by `source_local_path` above.

## Modified-Mole Formulation

The formulation enforces phase electroneutrality by eliminating one charged
species. It then defines modified mole numbers and modified mole fractions for
the remaining independent species. The reduced composition has `C - 2`
independent coordinates after electroneutrality and normalization.

The reduced thermodynamics uses formulation-specific modified
electrochemical-potential combinations. It does not compare unconstrained
single-ion chemical potentials as though they were independently measurable
transfer quantities.

## Three Coordinated Stages

Stage I transforms the feed into the modified coordinates and performs the
electrolyte tangent-plane stability search.

Stage II alternates a linear upper problem with nonconvex lower problems in
modified composition and volume. It adds cutting planes, updates bounds, and
collects candidate phases. Charge-neutral TPD screening, a finite candidate
list, or an open bound audit is component evidence, not a completed HELD2
Stage II loop.

Stage III directly minimizes total free energy over candidate phase
fractions, phase volumes, and modified phase compositions. It enforces the
modified material balances and formulation bounds. The controller returns to
Stage II when the candidate set or convergence checks fail, and it refines
trace modified mole fractions after convergence.

## Stationarity And Certification

The Stage III stationarity conditions produce common pressure and equality of
the independent modified potentials across retained phases. Postsolve must
check those conditions together with modified and explicit material balance,
per-phase charge, phase amounts, phase separation, and domain validity.

Comparing individual ionic electrochemical potentials requires an explicit
phase-electric or Galvani-potential convention. A generic individual-ion
equality check is not a substitute for the independent modified-potential
conditions.

An exact residual solve may correct or diagnose a Stage III result. It does not
define the HELD2 Stage III objective.

## Separation From The Ascani Formulation

Perdomo explicitly distinguishes this individual-species modified-mole
transformation from the independent counterion-pair construction published by
Ascani and coauthors. The package must keep them as separate algorithm
families unless a future derivation proves equation-level equivalence.

## Package Status

The package retains useful electroneutral coordinates, continuous TPD,
counterion-pair, projected-residual, local-NLP, derivative, and postsolve
components. Those components do not implement the published Perdomo controller
as a whole. Public electrolyte phase-equilibrium routes remain closed.
