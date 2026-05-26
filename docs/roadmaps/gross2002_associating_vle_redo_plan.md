# Gross 2002 Associating VLE Redo Plan

## Goal

Redo the associating equilibrium work from a clean path. Do not continue from
`codex/associating-lle-goal` as an implementation source. Use Gross/Sadowski
2002 to prove the package can evaluate association cleanly at the EOS level,
then admit one narrow associating VLE `bubble_pressure` route, and only then
progress toward harder VLE and LLE systems.

The first route proof is:

```text
paper: Gross/Sadowski 2002
figure: Figure 2
system: methanol/isobutane
route: bubble_pressure
T: 373.15 K
k_ij: 0.05
composition: representative liquid composition, start at x = [0.5, 0.5]
required evidence: exact Hessian accepted with association diagnostics
```

## Current Direction

The failed branch performed useful reconnaissance, but it mixed too many
concerns:

- paper-validation scaffolding;
- generated route outputs;
- broad selector-policy experiments;
- LLE before associating VLE was proven.

Keep only source-backed inventory ideas:

- Gross 2002 Figure 1-10 classification;
- Table 1 associating pure-component parameters;
- Table 2 binary `k_ij` values;
- nonassociating partner parameters from Gross/Sadowski 2001;
- route diagnostics as historical hints only.

Do not keep generated figure outputs or route outputs as proof. Do not claim
visual agreement until source data or digitized figure data exists and is
checked.

## Source Data Contract

Use the existing source-owned Gross 2002 parameter structure:

```text
analyses/paper_validation/2002_gross/parameters/pure/any_solvent.csv
analyses/paper_validation/2002_gross/parameters/mixed/binary_interaction/k_ij.csv
analyses/paper_validation/2002_gross/shared/source/figures_manifest.csv
docs/papers/md/Gross, Sadowski - 2002 - Application of the PC-SAFT equation of state to associating systems.md
```

Runtime payloads and tests must use the package's current parameter names:

```python
{
    "MW": np.asarray([...], dtype=float),
    "m": np.asarray([...], dtype=float),
    "s": np.asarray([...], dtype=float),
    "e": np.asarray([...], dtype=float),
    "e_assoc": np.asarray([...], dtype=float),
    "vol_a": np.asarray([...], dtype=float),
    "assoc_scheme": ["2B", None],
    "z": np.zeros(n),
    "k_ij": np.asarray([[0.0, kij], [kij, 0.0]], dtype=float),
}
```

Do not introduce ad hoc names such as `kappa_assoc`,
`epsilon_assoc`, or paper-specific route payloads unless a converter writes the
canonical package shape above.

## Implementation Sequence

### Stage 0: Clean Start

- Leave `codex/associating-lle-goal` behind as an implementation source.
- If anything is salvaged, copy only parameter/case inventory into clean
  fixtures or docs with source references.
- Keep the first code branch scoped to one vertical proof. Suggested branch:
  `codex/gross2002-associating-bubble-pressure`.

Before any associating LLE task starts, the generalized equilibrium doctrine in
`docs/roadmaps/generalized_fluid_phase_equilibrium.md` must be
preserved at least through the current neutral TP flash and neutral
nonassociating LLE `held_tpd_volume_composition` discovery and `tpd_postsolve`
phase-set certification baseline. Associating LLE must not rely on a local
Ipopt split plus a phase-distance anti-collapse constraint as proof of global
phase stability; it still needs the broader row-level gates in
`docs/roadmaps/generalized_fluid_phase_equilibrium.md`.

### Stage 1: Report-Ready Derivation

- Create and maintain the LaTeX-ready reduced association closure derivation in
  `docs/derivation/explicit_association_closure_for_pcsaft.tex`.
- Keep the roadmap summary synchronized in
  `docs/roadmaps/explicit_association_closure_for_pcsaft.md`.
- The derivation must state:
  - exact mass-action association remains the reference model;
  - explicit closures are approximate Helmholtz models unless proven exact;
  - CppAD derivatives of explicit closures are exact derivatives of the
    approximate model;
  - direct taping of the exact fixed-point association solve is not accepted.

### Stage 2: Clean Gross 2002 Case Fixtures

- Add compact test support for Gross 2002 systems, preferably under
  `tests/support/gross2002_cases.py`.
- Build fixtures from the existing source-owned CSVs or mirror their values in
  one small helper with explicit source comments.
- Include at least:
  - `gross2002_methanol_isobutane()`;
  - `gross2002_pentanol_benzene()`;
  - `gross2002_propanol_benzene()`;
  - `gross2002_butanol_nbutane()`;
  - `gross2002_methanol_cyclohexane()`.
- Each helper should return a package `ParameterSet` or `Mixture`, source
  metadata, and the recommended route probe.

### Stage 3: EOS Association Validation

Before equilibrium, prove the EOS behavior directly:

- pure methanol 2B association evaluates finite `a_assoc`, pressure,
  residual chemical potential, and log fugacity coefficients;
- methanol/isobutane and methanol/cyclohexane use one associating component
  and the paper `k_ij` values;
- exact implicit association diagnostics report finite site fractions and
  implicit sensitivity labels;
- explicit closures compare against `implicit_exact` at the EOS level before
  any route admission.

Suggested tests:

```text
tests/native/contracts/test_association_explicit_closure_contract.py
tests/native/state/test_gross2002_association_eos_validation.py
```

### Stage 4: Explicit Closure Diagnostics

Implement only diagnostic or experimental closure support first:

```text
explicit_single_assoc_2class
explicit_damped_picard_unroll_3
explicit_picard3_diag_newton1
explicit_moment_donor_acceptor
```

Required diagnostic fields:

```text
closure_name
X
a_assoc
mass_action_residual_inf_norm
min_X
max_X
site_count
unroll_steps
damping
diagonal_newton_polish
```

Production default remains `implicit_exact` until a route explicitly opts into
an approximate model and reports it as approximate.

### Stage 5: Narrow Selector Admission

Update selector policy only after Stages 2-4 pass.

Admit only:

```text
route = bubble_pressure
neutral = true
nonelectrolyte = true
nonreactive = true
associating_component_count <= 1
exact_derivatives_required = true
postsolve_certification = on
```

Keep blocked:

```text
bubble_temperature
dew_pressure
dew_temperature
neutral_tp_flash
associating neutral_lle
electrolyte_lle
reactive routes
cross-associating systems with more than one associating component
```

Do not simply remove the active-association selector guard. Replace it with a
route- and topology-specific admission rule.

### Stage 6: First Gross 2002 Equilibrium Proof

Add a focused route-result test for Figure 2:

```text
tests/native/equilibrium/results/test_gross2002_associating_vle_reference_values.py
```

Minimum assertions:

- solver status is accepted;
- route is `bubble_pressure`;
- exact Hessian mode is used;
- `eval_h` is called;
- association diagnostics are present;
- material, fixed-composition, pressure, phase-equilibrium, and phase-distance
  checks pass;
- liquid density is liquid-like;
- vapor density is vapor-like;
- vapor composition is finite and normalized.

The first test should not require reproducing the full Figure 2 curve. It must
prove the generic API-to-native route wiring and exact derivative path on one
trusted representative case.

### Stage 7: Additional Isothermal VLE Proofs

After Figure 2 passes, add at least one more isothermal Gross 2002 proof:

- Figure 4: 1-pentanol/benzene at `T = 313.15 K`, `k_ij = 0.0135`;
- or Figure 5: 1-propanol/benzene at `T = 313.15 K`, `k_ij = 0.020`.

Keep these as route-wiring and certification tests. Full paper reproduction
belongs in analysis or benchmark scripts, not in broad pytest curves.

### Stage 8: Later Work

Only after the narrow `bubble_pressure` proof is stable:

1. add associating `bubble_temperature`;
2. reproduce Gross Figure 8 methanol/cyclohexane isobaric VLE;
3. reproduce Gross Figure 9 methanol/1-octanol isobaric VLE;
4. return to methanol/cyclohexane LLE;
5. then try water/1-pentanol LLE;
6. then revisit electrolyte and salting-out LLE.

Associating LLE remains blocked until neutral HELD/TPD phase discovery,
postsolve TPD certification, exact associating EOS derivatives, the first
Gross 2002 `bubble_pressure` proof, and at least one additional isothermal
associating VLE proof are all complete.

## Acceptance Criteria

The redo is complete only when all of these are true:

1. The explicit association closure derivation exists and is linked from the
   roadmap.
2. Gross 2002 fixtures use the current package parameter structure.
3. EOS-level tests prove active association values and derivative diagnostics
   before equilibrium.
4. Explicit closure diagnostics compare approximate outputs against
   `implicit_exact`.
5. `explicit_single_assoc_2class` and `explicit_picard3_diag_newton1` are
   available as diagnostics or experimental options.
6. Exact implicit association remains the default.
7. The selector admits only the narrow one-associating-component
   `bubble_pressure` topology.
8. Gross 2002 methanol/isobutane `bubble_pressure` accepts with exact Hessian.
9. At least one additional isothermal Gross 2002 associating VLE
   `bubble_pressure` case accepts.
10. Capabilities describe the result as limited associating bubble-pressure
    support, not general associating VLE or LLE.

## Explicit Non-Goals

- Do not merge or continue the failed branch as implementation source.
- Do not start with LLE.
- Do not start with water/1-pentanol.
- Do not broaden active association globally in the selector.
- Do not expose approximate association as the default.
- Do not call approximate `X_A` exact PC-SAFT association.
- Do not claim digitized Gross figure agreement without source-backed data.
- Do not expose electrolyte, reactive, TP flash, dew, or LLE associating routes
  in this tranche.
