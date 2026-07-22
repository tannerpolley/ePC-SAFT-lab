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

## Stage-I experiment

`_held2.pyx` adds only the first HELD2 stage. It reuses `_thermo.pyx`; it does
not contain another EOS. `solve_stage1(...)` deterministically scans the
declared log-volume interval, refines detected pressure roots, rejects
boundary/marginal/tied references, and selects the unique lowest-`A+PV`
strict-stable detected root. The selected state supplies the modified-coordinate
tangent for local `cyipopt` TPD searches.

The H2O/Na+/Cl- chart has one independent modified ion fraction. Its inverse is
explicitly electroneutral, and the salt modified potential is invariant to an
equal-and-opposite ionic Galvani shift. The TPD callback provides an empty exact
sparse constraint Jacobian and the three entries of the exact lower-triangular
two-coordinate Hessian derived from the thermodynamic tape.

The controller reports local solver termination, numerical certification, and
physical certification separately. A certified negative witness has precedence
over an incomplete sibling start. Conversely, a completed finite multistart
search with no negative witness reports only `no_negative_witness_detected`.
No globality field or global-stability claim is emitted.

## Stage-II experiment

The same private controller module now exercises Perdomo Stage II without
adding another thermodynamic model. `solve_stage2(...)` alternates a SciPy
HiGHS upper linear program with deterministic and warm-started local `cyipopt`
lower searches over the modified ion fraction and log-volume. Every major
iteration preserves the upper solution before the lower searches, admits only
distinct certified physical improving cuts, and then evaluates Eq. 66 using
that same upper objective and multiplier.

The Step-6 selector uses fixed-volume composition gradients, relative
multiplier scaling, log-volume stationarity, dual tightness, and pairwise
modified-composition-or-packing distinctness. Solver termination, projected
KKT, complementarity, coordinate/domain, charge, pressure, and final tape
evaluation remain separate fields for every lower attempt. Resource exhaustion,
an empty candidate set, or the absence of a certified improving cut leaves
Stage III `not_run` and physical equilibrium `not_adjudicated`.

The enumerable manufactured double-well case produces cuts in the order
`feed`, `witness`, `C1` and recovers the expected two-point candidate set at
modified fractions 0.2 and 0.8. The real tape smoke completes one upper/lower
major at a known pressure root. Both are finite controller-conformance checks;
neither claims that the nonconvex lower problem was solved globally.

## Stage-III, certification, and tracing experiment

`_stage3.pyx` completes the ten-step manufactured controller route. Stage III
minimizes extensive reduced Gibbs energy over phase fractions, modified
fractions, and log-volumes. It enforces phase-fraction normalization and the
modified material balance as explicit constraints; the reduced composition
recovers electroneutral H2O/Na+/Cl- phases and leaves a strictly positive
dependent fraction. The callback supplies the exact sparse constraint Jacobian
and exact sparse Lagrangian Hessian to `cyipopt`.

The optimizer uses affine cube coordinates only as a numerical chart. Bound
multipliers are divided by the affine scales before original-coordinate
stationarity, sign, and complementarity checks. A phase can be retired only
when its phase fraction is at the lower bound with a positive KKT multiplier
and passing complementarity. The retained phases are then solved again with
unchanged settings; filtering alone is never physical acceptance. If certified
retirement would leave fewer than two phases, the controller returns to Stage
II without performing physical adjudication.

Step 9 recomputes KKT and feasibility from the retained stationarity,
constraint, complementarity, and dual-pullback evidence, then independently
checks modified and ordinary
material balances, per-phase charge, pressure equality, independent modified
potential equality, phase distinction, tape/domain validity, and reconstructed
total free energy. Any failure returns `return_to_stage2`. The manufactured
matrix covers one phase, a successful split, KKT-certified inactive retirement,
physical feedback, and a short damped-Newton trace refinement. Only solver,
numerical, and physical status axes are reported, and no globality claim is
emitted.

## Perdomo Table 3 cross-EOS challenge

The retained 298.15 K, 2.508 kPa, 5.6 molal NaCl/water run is deliberately
classified as a cross-EOS controller challenge. Perdomo Table 3 was calculated
with SAFT-gamma-Mie GC, while this wheel uses the bounded Figiel 2025 ePC-SAFT
H2O/Na+/Cl- tape. No parameter was tuned to the table.

The exact installed run selected a homogeneous pressure reference and all four
local Stage-I solvers returned. Two attempts passed numerical certification,
none passed physical certification, and the other two remained numerically
uncertified. The controller therefore stopped fail-closed at
`stage1_indeterminate`; Stage II, Stage III, and any prediction comparison were
not run. This is an honest result for the ePC-SAFT experiment, not a failure to
reproduce Perdomo's different EOS.

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

[`evidence/stage1_receipt.json`](evidence/stage1_receipt.json) binds the Stage-I
source, tests, and installed wheel. Its manufactured three-root topology selects
the lower strict-stable root, the stable TPD case completes all starts, and the
unstable case retains a `-0.015625` negative witness despite one deliberately
failed start. A real-tape smoke selects the known 0.08 m3/mol pressure root and
completes two certified local searches. These are controller-conformance facts,
not electrolyte-LLE prediction evidence.

[`evidence/stage2_receipt.json`](evidence/stage2_receipt.json) binds the
Stage-II source, focused tests, installed wheel, ordered cut ledger,
manufactured `M*` set, incomplete-search cases, and real-tape one-major smoke.

[`evidence/stage3_manufactured.json`](evidence/stage3_manufactured.json) and
[`evidence/perdomo_table3_cross_eos.json`](evidence/perdomo_table3_cross_eos.json)
are generated by the thin installed-wheel `evidence_runner.py`.
[`evidence/stage3_receipt.json`](evidence/stage3_receipt.json) binds those
outputs to the compiled source, tests, runner, and final wheel.

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
