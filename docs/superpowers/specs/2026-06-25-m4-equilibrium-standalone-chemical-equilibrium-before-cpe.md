# M4 Standalone Chemical Equilibrium Before CPE

Milestone: `M4 - Equilibrium`
Issue: `https://github.com/ePC-SAFT/ePC-SAFT/issues/321`
Status: `draft`
Last synced: `2026-06-26`

## Remaining-Work Supersession

This document remains the historical foundation for the CE/CPE boundary,
reaction and standard-state contracts, one-NLP architecture, oracle harness,
and original issue tree under #321. Its remaining diagnostic, formulation
repair, and standalone `reactive_speciation` admission work is superseded by
`docs/superpowers/specs/2026-07-10-m4-standalone-ce-diagnostic-repair-and-admission.md`.

Where the historical text below describes `reactive_speciation` as a public or
activated surface, the current native activation matrix and the 2026-07-10 spec
govern: standalone CE remains internal validation, issue #330 remains blocked,
and reactive LLE, reactive electrolyte LLE, and CPE remain closed.

## Summary

Create a standalone chemical-equilibrium and speciation tranche for
`packages/epcsaft-equilibrium` before combining reactions with phase splitting.
This tranche should turn the existing CE placeholder into a scoped issue set,
while leaving CPE as a downstream simultaneous phase-plus-chemistry method.

The first production target is homogeneous CE/speciation: true species,
element/moiety conservation, reaction stoichiometry, reaction affinity or
equivalent constrained-Gibbs stationarity, explicit standard-state convention,
exact derivatives, diagnostics, and validation. Reactive LLE, reactive
electrolyte LLE, phase discovery, and HELD coupling depend on that CE proof.

## Source Map

- Verified repo doctrine: `docs/superpowers/milestones/M4-equilibrium/generalized-fluid-phase-equilibrium.md`
  keeps `CE Standalone Reactive Speciation` separate from `CPE Simultaneous
  Phase-Chemistry Contract`.
- Verified registry contract: `docs/superpowers/milestones/M4-equilibrium/registries/equilibrium-benchmark-registry.yaml`
  defines CE as homogeneous chemical/speciation equilibrium and requires
  reaction-constant, standard-state, and reaction-affinity gates before exposure.
- Verified stage plan: `docs/superpowers/specs/2026-05-26-m4-equilibrium-stage-by-stage-implementation-plan.md`
  says CE and CPE must not be used as capability claims, standard states must be
  explicit, homogeneous CE proof is separate from CPE proof, and staged PE plus
  staged CE is not a final CPE proof.
- Verified code state: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/core/activation_matrix.h`
  and `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/equilibrium_activation.py`
  already declare `reactive_speciation`, `reactive_lle`, and
  `reactive_electrolyte_lle`; `reactive_speciation` is the standalone CE
  public surface, while reactive phase routes stay closed to production exposure.
- Verified native seed: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/blocks/reaction_block.cpp`
  contains an ideal reaction quotient, standard chemical-potential, and reaction
  extent block. This is a useful kernel, not the standalone CE family contract.
- Verified retained evidence: `analyses/paper_validation/2023_ascani/analysis.yaml`
  and `analyses/paper_validation/2023_ascani/shared/results/reactive_phase_equilibrium/summary.json`
  preserve Ascani 2023 route-gate evidence for homogeneous CE and reactive LLE,
  but paper-match validation is still blocked by missing source target rows.
- Verified issue tracker check: `gh issue list --state open --search "chemical equilibrium speciation reactive CPE CE in:title,body"`
  returned no matching open issues on 2026-06-25.

## Literature Fit

- Verified from Ascani, Sadowski, and Held 2022: electrolyte phase-equilibrium
  algorithms may include coupled reaction or dissociation equilibria, and the
  paper cites RAND, Tsanas, and related geochemical work. Its own core value for
  this repo remains distributed-ion PE/LLE with stability analysis.
- Verified from Ascani 2023: combined chemical and LLE equilibrium is a
  simultaneous reactive-flash problem. The paper uses staged homogeneous CE and
  phase-stability steps as initialization, then solves a final reactive flash.
  That matches the repo rule that staged CE plus PE cannot be accepted as final
  CPE proof.
- Verified from Perdomo 2025: satisfying PE optimality equations is not enough;
  metastable or unstable phase combinations can satisfy necessary conditions, so
  phase stability must be certified. This is a phase-discovery requirement, not
  a standalone CE requirement.
- Verified from Pope 2004: Gibbs function continuation solves ideal-gas
  constrained chemical equilibrium by tracking constraint potentials from a
  max-min feasible composition to the true Gibbs functions. Its direct value is
  CE robustness for small species and constrained bases, not LLE phase discovery.
- Verified from Cantera docs checked on 2026-06-25:
  `ThermoPhase.equilibrate` exposes `element_potential`, `gibbs`, and `vcs`
  solver choices; `Mixture.equilibrate` uses VCS/Gibbs variants to minimize
  mixture Gibbs energy subject to element conservation. Cantera is therefore a
  CE/speciation reference and diagnostic oracle for compatible thermodynamic
  models, not a replacement for ePC-SAFT HELD/TPD LLE solving.

## Boundary Decision

Standalone CE/speciation owns:

- true species amounts for one homogeneous phase;
- element, charge, or moiety conservation basis;
- stoichiometric reaction sets and rank checks;
- reaction affinity residuals or equivalent constrained-Gibbs stationarity;
- standard-state and equilibrium-constant conversion rules;
- exact derivative contracts for exposed Ipopt routes;
- diagnostics for species amounts, activities, chemical potentials, extents,
  conservation residuals, affinities, active bounds, and standard-state metadata.

CPE/reactive phase equilibrium owns later:

- phase species amounts and phase volumes;
- phase pressure consistency;
- transferable-potential equality or projected electrochemical-potential
  equality across phases;
- reaction stationarity in each reacting phase or across the declared reaction
  domain;
- per-phase electroneutrality for electrolyte routes;
- phase stability and phase-set completeness certification.

## Cantera And Pope Adoption Points

Use Cantera for CE reference behavior, not as the production PE engine:

- compare element-potential, Gibbs, and VCS results on ideal-gas and simple
  ideal-solution CE cases;
- compare element balances, reaction affinities, species activation, and
  diagnostic residuals;
- preserve cases where Cantera succeeds or fails as regression fixtures for
  ePC-SAFT solver diagnostics;
- avoid using Cantera multiphase CE as proof of LLE phase discovery, because the
  ePC-SAFT problem needs EOS fugacity/activity models, charge-neutral reduced
  variables, and HELD/TPD phase-set certification.

Use Pope as a robustness pattern for the standalone CE solver layer:

- implement a max-min feasible composition or equivalent interior seed;
- track a pseudo-Gibbs path for ideal or activity-model CE cases where Newton or
  Ipopt starts near tiny species are fragile;
- expose continuation diagnostics separately from final thermodynamic residuals;
- treat continuation as a CE algorithm option or initializer, not as CPE proof.

## Candidate Issue Set

Tracking issue:

- Title: `M4 CE: standalone chemical/speciation equilibrium foundation before CPE`
- Type: `Feature`
- Package: `epcsaft-equilibrium`
- Milestone: `M4 - Equilibrium`
- Acceptance: all CE gates below close; CPE remains downstream.

Child issues:

1. `M4 CE: write CE/CPE boundary doctrine and registry update`
   - Type: `Task`
   - Scope: docs and registry only.
   - Acceptance: CE, CPE, and PE boundaries are explicit; staged CE+PE is
     documented as initialization only.

2. `M4 CE: define reaction-set schema and conservation-basis compiler`
   - Type: `Feature`
   - Scope: true species labels, element/moiety matrix, charge vector,
     stoichiometric matrix, rank diagnostics, independent reaction detection,
     feed feasibility, and impossible-basis errors.
   - Acceptance: unit tests cover neutral, charged, rank-deficient, and
     impossible feed cases.

3. `M4 CE: define standard-state and equilibrium-constant registry`
   - Type: `Feature`
   - Scope: `log K`, `delta G standard`, mole-fraction activity, molality,
     fugacity, EOS `x phi`, temperature dependence, units, and conversion
     diagnostics.
   - Acceptance: no reaction residual can be evaluated without an explicit
     standard-state record.

4. `M4 CE: build homogeneous CE residual and constrained objective core`
   - Type: `Feature`
   - Scope: species amounts or extents, Gibbs/Helmholtz chemical objective,
     conservation constraints, reaction stationarity, exact Jacobian and
     Hessian hooks, and scaling.
   - Acceptance: native tests prove balances, stationarity, curvature, and
     finite-domain handling.

5. `M4 CE: add single CE NLP activation path`
   - Type: `Feature`
   - Scope: one standalone CE route through the activation matrix, selector
     contract, native `NlpProblem`, and Ipopt adapter using the homogeneous CE
     residual/objective block.
   - Acceptance: tests and checker evidence prove CE cannot bypass the
     activation-matrix NLP/Ipopt path through direct extent,
     element-potential/VCS-style, Pope-style continuation, checker-only, native
     binding, or public API side routes.

6. `M4 CE: create Cantera and Pope reference-oracle harness`
   - Type: `Task`
   - Scope: local scripts/fixtures that compare ePC-SAFT CE outputs against
     Cantera-compatible ideal cases and Pope-paper constrained ideal-gas
     reference cases.
   - Acceptance: retained JSON summaries include element residuals, affinity
     residuals, species mole fractions, solver metadata, and known limitation
     notes; the harness is reference-only and creates no alternate CE solver
     route.

7. `M4 CE: design standalone speciation public API and result schema`
   - Type: `Feature`
   - Scope: user-facing request object, route metadata, result fields,
     diagnostics, errors, and activation reporting for CE only.
   - Acceptance: public API does not claim reactive LLE or electrolyte CPE.

8. `M4 CE: complete primitive receipts and independent component checker`
   - Type: `Task`
   - Scope: analytic ideal reactions, multi-reaction rank tests, charged
     speciation/electroneutrality tests, Ascani 2023 homogeneous CE, MEA
     speciation cases, and Cantera/Pope comparisons.
   - Acceptance: every capability claim has retained source-backed evidence.

9. `M4 CE: activate standalone CE only after gates pass`
   - Type: `Milestone gate`
   - Scope: activation matrix, capability reporting, docs, examples, and
     validation records.
   - Acceptance: `reactive_speciation` can be exposed only if the CE gate is
     satisfied; `reactive_lle` and `reactive_electrolyte_lle` stay closed.

10. `M4 CPE: define simultaneous phase-plus-chemistry interface contract`
    - Type: `Task`
    - Scope: future-only interface contract connecting CE variables to GFPE
      variables, phase stability, per-phase charge, and postsolve
      certification.
    - Acceptance: no production CPE route is exposed; the issue only defines
      the coupling contract and blockers.

## Dependency Order

1. Boundary doctrine and registry update.
2. Reaction-set schema plus standard-state registry.
3. Homogeneous CE residual/objective core.
4. Robust algorithm lanes and reference-oracle harness.
5. API/result schema and validation ladder.
6. CE activation gate.
7. CPE interface contract.
8. Reactive LLE and reactive electrolyte LLE implementation issues after CE and
   PE gates are both proven.

## Acceptance Gates

- [x] A GitHub tracking issue exists for standalone CE under `M4 - Equilibrium`.
- [x] Child issues are created with one milestone and package scope each.
- [ ] CE registry and docs say homogeneous CE is separate from CPE.
- [ ] Standard-state conventions are explicit before any CE public route.
- [ ] Cantera/Pope comparison harness scope is CE-only.
- [ ] CPE issues depend on both CE and PE validation gates.

## Validation

Planning validation before creating issues:

```bash
gh issue list --state open --search "chemical equilibrium speciation reactive CPE CE in:title,body" --json number,title,labels,milestone,url
```

Implementation validation will be issue-specific, but the minimum CE proof
ladder must include native unit tests, reference-oracle summaries, and retained
literature validation artifacts before activation.

