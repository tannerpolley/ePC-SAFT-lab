# Matsuda 2011 Perfluorohexane + Hexane Neutral LLE Fixture

## Source Data

The experimental rows come from the NIST ThermoML record for Matsuda et al.,
Fluid Phase Equilibria 297(2), 187-191, DOI
`10.1016/j.fluid.2010.05.018`.

NIST dataset 2 reports cloud-point liquid-liquid equilibrium temperatures for
hexane + perfluorohexane at 101.3 kPa. The retained source rows are:

- x(perfluorohexane) = 0.2000 at 293.89 K.
- x(perfluorohexane) = 0.5497 at 293.90 K.

These are paired binodal branch rows, not a separate tabulated tie-line. For a
binary LLE system at fixed pressure, the paired branch compositions at the same
temperature define the two coexisting liquid compositions used by this fixture.
The 0.01 K branch-temperature difference is inside the 0.2 K combined
temperature uncertainty reported by the NIST record.

## Parameters

The pure-component rows use Tihic thesis PC-SAFT-compatible sPC-SAFT parameters:

- Perfluorohexane is derived from the fluorinated-family molecular-weight
  correlations: `m = 0.0121 MW + 1.634`, `m*sigma^3 = 0.6888 MW + 22.895`, and
  `m*epsilon/k = 2.9412 MW + 230.1`.
- Hexane uses the n-hexane Approach I row: `m = 2.8141`, `sigma = 3.8766 A`,
  and `epsilon/k = 233.90 K`.

Tihic reports `kij = 0.073` for the sPC-SAFT perfluorohexane + n-alkane LLE
context. With the internal ePC-SAFT neutral PC-SAFT diagnostic, that value
over-splits the retained source pair by about 0.13 mole fraction. This fixture
therefore stores `kij = 0.0662`, fitted against the retained source pair using
the current route. The binary interaction is source-fitted, not imported as a
literature value.

## Scope

This fixture is neutral, nonelectrolyte, nonreactive, and nonassociating. It is
one source-backed internal sampled-candidate LLE diagnostic. It does not prove
global HELD phase-set completeness, admit a public `lle` route, or cover
associating, electrolyte, reactive, CE, or CPE behavior.
