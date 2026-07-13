# Equilibrium formulation conformance kernel

This analysis exercises every family in the
[canonical equilibrium-formulations document](../../../docs/latex/equilibrium_formulations.tex)
with deterministic manufactured functions. It is a reference/toy workflow,
not installed package code, an ePC-SAFT evaluator, or evidence of physical
mixture predictions.

## Evidence status

- **verified:** each adapter preserves the ensemble, coordinate, balance,
  derivative, and certificate structure assigned to its exercised active set
  by the canonical document. Neutral HELD has separate two-phase and
  single-phase active-set adapters. Perdomo, Ascani, and CPE currently exercise
  fixed active-phase topologies only. The focused tests execute with NumPy and
  do not import the native provider or equilibrium extension.
- **inference:** a common orchestration envelope can execute every family when
  direct-minimization and residual-solving paths remain nominally distinct and
  certificates carry matching formulation identifiers.
- **assumption:** all polynomial wells, linear residual maps, target states,
  scales, and reference-energy shifts are manufactured mathematical fixtures.
  They are not EOS parameterizations.
- **unknown:** these tests do not establish phase-appearance searches for all
  families, ePC-SAFT domain behavior,
  association conditioning for a physical site model, production derivative
  sparsity, large-problem scaling, physical phase stability, or convergence of
  any native optimizer.

## Kernel boundary

`kernel.py` provides one public analysis facade, `run_formulation`, with two
explicit internal numerical paths:

- direct minimization for neutral HELD fixed active sets, association-aware neutral HELD,
  Perdomo HELD2, standalone CE, and CPE;
- residual solving for bubble/dew/pure boundaries and Ascani counterion-pair
  equilibrium.

The kernel shares box-domain validation, variable/objective/residual scaling,
deterministic starts, derivative receipts, backend identity, candidate receipts,
basin classifications, and certificate-identity enforcement. Family modules
retain their own coordinates, constraints, active-set topology, independent
evidence, and acceptance certificate. A result cannot borrow a certificate
from another formulation identifier. “One kernel” therefore means one
orchestration and receipt contract, not one equation system or one silently
interchangeable solver.

## Covered checks

- full residual, balance, element, reaction, modified-mole, and pair-basis
  ranks;
- analytic gradients and Jacobians against central differences;
- known manufactured roots and global lower bounds or objective-only
  enumeration where available;
- material/element balances, local electroneutrality, positivity, pressure or
  volume stationarity, complementarity, and exercised active-set topology;
- neutral/common-tangent, association-inner-state, modified-potential,
  counterion-pair, reaction-affinity, and simultaneous CPE certificates;
- phase/species reference shifts, explicitly energy-based Galvani-gauge
  cancellation, reaction-basis scaling/orientation, phase permutation, and
  extensive inventory scaling;
- analytic-anchor-free deterministic multistart receipts, complete per-start
  outcome classification, tolerance and unit-scale sensitivity,
  metastable/local rejection, and invalid inputs.

For the retained seeds `3`, `11`, and `29`, the basin contract locks all 84
local attempts to 65 accepted solutions, 18 converged-but-rejected local
states, and one explicit nonconvergence. These are manufactured numerical
regression counts, not physical convergence probabilities.

The public pressure-boundary fixtures explicitly report that they do not carry
a global stability claim. CPE uses a nonnegative manufactured energy lower
bound and explicitly reports reactive-TPD completeness as unavailable; the
lower bound is independent mathematical evidence only for that fixture.
Standalone CE uses an extensive relative-entropy fixture for its interior
solution and a separate extensive convex polynomial fixture for active-bound
KKT/complementarity testing.

## Run

```bash
uv run --no-sync python run_pytest.py analyses/reference_oracles/equilibrium_formulations/tests -q
```

The original, more detailed neutral HELD nonconvex oracle remains in
`analyses/reference_oracles/neutral_held/`. This conformance analysis reuses its
family-owned enumeration and certificates without moving those concepts into
the shared kernel.
