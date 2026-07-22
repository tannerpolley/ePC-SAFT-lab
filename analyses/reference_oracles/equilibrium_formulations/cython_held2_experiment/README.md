# Cython HELD2 experiment

This isolated lab analysis tests a Cython, `cppad_py`, and `cyipopt` route for a
future manufactured HELD2 controller experiment. It is non-production evidence.
The clean Provider remains the sole production EOS owner, and nothing here is a
runtime dependency or migration candidate.

## Current thermodynamic slice

`_thermo.pyx` implements only the source-bound H2O/Na+/Cl- Figiel 2025 model at
298.15 K. The hash-bound packet records the selected Provider subject and model
fingerprint. The extensive dimensionless phase Helmholtz scalar contains:

- ideal mixing;
- PC-SAFT hard-chain and dispersion terms;
- water 2B association;
- finite-size Debye-Huckel electrostatics with composition-dependent dielectric
  suppression; and
- the combined Born SSM+DS radial contribution.

The fixed Lorentz diameter mixing equation has no adjustable `l_ij`. The packet
therefore records `lorentz-fixed-no-lij` instead of inventing zero-valued
parameters. Only water has association sites, so there is no cross-association
`k_ij_hb` parameter in this bounded model.

The defining `cppad_py` tape has joint coordinates
`(T, n_water, n_sodium, n_chloride, V, X_A, X_B)`. The site-fraction iteration
runs before recording. First and second derivatives with respect to
`(T, n_water, n_sodium, n_chloride, V)` are reduced through the mass-action
Jacobian, including the second implicit derivative. A singular, poorly
conditioned, nonconverged, nonfinite, non-electroneutral, or out-of-source-domain
state fails closed.

The APIs are deliberately narrow:

- `evaluate_state(T, amounts, V)` returns the contribution partition, total
  `A/(RT)`, pressure, amount-derivative chemical-potential inputs, source
  identity, association diagnostics, and separate solver/numerical/physical
  statuses.
- `derivative_bundle(T, amounts, V)` returns the reduced five-coordinate
  gradient and symmetric Hessian from the same tape definition.

## Bounded comparison evidence

[`evidence/provider_comparison.csv`](evidence/provider_comparison.csv) compares
the wheel with the immutable Provider artifact built from commit `97d7b37` and
selected fingerprint `sha256:7c6377...9912d`. The six cases cross dilute and
5.6-molal feed compositions with dense (`eta=0.35`), intermediate (`eta=0.1`),
and gas-safe (`eta=1e-4`) volumes. All contribution, total-value, pressure,
four-coordinate gradient, and 4x4 Hessian comparisons pass the retained
Provider test allowances. The temperature gradient and temperature-temperature
curvature independently agree with the Provider residual-energy and isochoric
heat-capacity identities. No discrepancy is deferred to the next issue.

The comparison does not make this implementation authoritative, validate a
phase-equilibrium prediction, or establish behavior outside the exact species,
temperature, composition, and packing domain.

## Rebuild and test

Create the dependency environment exactly as described by the predecessor
[`evidence/build_receipt.json`](evidence/build_receipt.json), then run:

```bash
.venv/bin/python -m build --wheel
.venv/bin/python -m pip install --force-reinstall --no-deps \
  dist/cython_held2_experiment-0.0.1-cp313-cp313-linux_x86_64.whl
.venv/bin/python -m pytest -q
```

The retained thermodynamic receipt binds the source, parameter packet,
comparison CSV, wheel, and exact Provider artifact. Tests run only against the
installed experiment wheel; the Provider is an evidence-generation subject and
is not imported by the experiment package.
