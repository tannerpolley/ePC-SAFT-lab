---
doctrine_schema_version: 1
algorithm_ids:
  - ascani-counterion-pair-equilibrium
source_local_path: docs/papers/md/Equilibrium/Ascani, Sadowski, Held - 2022 - Calculation of Multiphase Equilibria Containing Mixed Solvents and M.md
source_anchors:
  - section-2-equations-13-25-equilibrium-conditions
  - section-3.1-equations-26-27-independent-counterion-pairs
  - section-3.2-equations-28-32-electroneutral-variables
  - section-3.3-equations-33-35-tangent-plane-distance
  - figure-1-successive-phase-addition
interphase_stationarity: independent-mean-ionic-or-pair-equality
individual_ionic_potential_comparison_requires: explicit-galvani-convention
runtime_status: closed
algorithm_parity_status: incomplete
---

# Ascani Counterion-Pair Electrolyte Equilibrium

## Identity And Scope

Ascani, Sadowski, and Held derive equilibrium conditions and an algorithm for
multiphase electrolyte systems with ions distributed among liquid phases. The
published implementation demonstrates LLE and LLLE with ePC-SAFT advanced.
The paper says that a vapor extension is straightforward, but it does not
demonstrate that extension.

Local source: Ascani et al. 2022, Sections 2, 3.1 through 3.3, and Figure 1 in
the paper named by `source_local_path` above.

## Independent Counterion Pairs

The formulation selects `N_ch - 1` independent cation-anion pairs. A pair
matrix records the inverse-valence coefficients, and the matrix must have rank
`N_ch - 1`. Each row defines an independent mean-ionic or pair chemical
potential.

The reduced variables move the paired ions in inverse-valence proportions.
This keeps each phase electroneutral while the solver changes phase
composition. Neutral molecular potentials and the independent mean-ionic pair
potentials supply the interphase equilibrium equations.

Individual ionic electrochemical-potential comparisons require an explicit
phase-electric or Galvani-potential convention. Without that convention, the
independent pair conditions govern certification.

## Published Algorithm

The algorithm performs a transformed tangent-plane stability search. When it
finds an unstable phase, it adds a phase candidate, estimates the split, and
solves the material-balance plus neutral and mean-ionic equilibrium equations.
It repeats stability testing and phase addition until the retained phase set
passes its checks.

This is an equilibrium-equation and successive-phase-addition algorithm. It is
not the Perdomo modified-mole HELD2 controller. Its local convergence and
stability receipts must retain their own formulation identity.

## Package Status

The repository contains useful counterion-pair matrix construction,
charge-neutral lifting, mean-ionic residual, TPD, local refinement, and
postsolve work. Historical files sometimes labeled that work as HELD2. Stage 1
reclassifies it as Ascani-family component evidence until a child plan proves a
different source-faithful controller. Public electrolyte phase-equilibrium
routes remain closed.
