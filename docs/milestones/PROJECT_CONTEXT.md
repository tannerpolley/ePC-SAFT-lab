# ePC-SAFT Project Context And Milestone Plan

## Purpose of this document

Every Codex agent working on this ePC-SAFT repository must read this document before planning, coding, reviewing, or merging.

This document explains:

1. What the package is supposed to be.
2. Why the package needs the current backend, derivative, equilibrium, regression, and benchmark work.
3. What downstream projects require.
4. What prior agents got wrong.
5. What “complete” means now.

This document is authoritative over older planning language that allowed audit-only closure, inventory-only closure, staged-only closure, diagnostic-only closure, or documented limitations as completion.

`docs/milestones/M4-equilibrium/plans/generalized-fluid-phase-equilibrium.md` is the canonical architecture contract, mathematical doctrine, activation policy, and staged implementation plan for generalized fluid-phase equilibrium. It defines the shared equilibrium-core structure, thermodynamic constrained NLP form, Ipopt/numerics layer, staged HELD requirements, postsolve certification, and collapsed family labels. Those labels are planning labels only, not runtime route keys.

`docs/milestones/M4-equilibrium/registries/equilibrium-benchmark-registry.yaml` is the executable registry for the collapsed generalized equilibrium plan. It uses descriptive `family_label` values, derived subworkflows, and PE-focused benchmark cases. Current deterministic TPD/candidate screening is not full HELD, so generalized family rows stay `planned_not_public` until full HELD-stage phase discovery, exact derivatives, and postsolve certification gates pass. Bubble/dew/cloud/shadow are derived boundary workflows planned after the neutral TP flash fixture for `T-x` and `P-x` diagrams; do not delete existing bubble/dew code or tests.

`docs/milestones/M4-equilibrium/plans/stage-by-stage-implementation-plan.md` is the GFPE-first execution overlay for generalized fluid-phase equilibrium. It uses this master context as package context and completion standard, but GFPE doctrine is the organizing spine for its stages.
Its Stage 8 gate must complete route-owned user scaling, Ipopt option profiles,
scaled numerical acceptance diagnostics, barrier/active-bound diagnostics, and
exact-Hessian profile gating before Stage 9 real-mixture HELD validation work starts.
Stage 9 and Stage 10 convergence diagnosis must stay narrow: use the phase-discovery
checker or one explicit `--equilibrium-debug` test node, not broad
equilibrium route/result sweeps. Stage 10 currently uses the
hydrocarbon-workbook-derived PC-SAFT TP flash fixture as the executable neutral
validation target; Pereira 2012 System III remains SAFT-VR/HELD context until model
parity or a source-backed ePC-SAFT reparameterization exists.
Stage 11 boundary diagnostics follow the same rule: routine checks are
contract-only, one named route point is the debug unit, and any Ipopt
acceptable-point, tiny-step, feasible-point, or iteration-limit seed path is
not completion evidence. Current bubble/dew `P-x` and `T-x` route-point validation is
available only through the explicit Stage 11 checker sweep opt-in, not through
routine validation.

`docs/milestones/M4-equilibrium/plans/gfpe-package-cleanup-plan.md` is the module cleanup overlay for
that same GFPE doctrine. It keeps selector admission, shared NLP ownership,
Ipopt numerics, result certification, capability reporting, and validation
lanes aligned around one modular equilibrium core.

`docs/adr/0005-package-extension-split.md` is the source-of-truth decision for
the package-extension split. The current monorepo still exposes provider,
equilibrium, and regression workflows, but final ownership is `epcsaft` for the
core provider, `epcsaft-equilibrium` for Ipopt-backed equilibrium, and
`epcsaft-regression` for Ceres-backed regression. CppAD/exact derivative
provider support stays core-owned.

`docs/milestones/M3-eos/plans/explicit-association-closure-for-pcsaft.md` is the current derivation and policy reference for reduced explicit association closures. Read it before adding approximate `X_A` closures or claiming exact CppAD derivatives of an approximate association model. It is separate from the generalized phase-equilibrium plan.

`docs/protocols/build_package_dependency_protocol.rst` is the canonical build, package, dependency, CMake, C++ package-management, and CI-lane protocol. Read it before changing native dependency defaults, GitHub Actions build lanes, package build behavior, or source-checkout build scripts.

---

# 1. Package identity

`epcsaft` is a general-purpose thermodynamic package. In the long-term package
split, `epcsaft` is the core thermodynamic provider. The current repository is
still a monorepo transition build that exposes equilibrium and regression
workflows until the provider and native extension boundaries are proven.

It must provide generic, reusable ePC-SAFT functionality for:

- EOS/state/property evaluation
- fugacity coefficients
- activity coefficients
- chemical potentials
- density and pressure closures
- pure-component and binary parameter regression
- electrolyte parameter regression
- phase equilibrium
- chemical/speciation equilibrium
- reactive phase equilibrium
- electrolyte LLE
- reactive electrolyte LLE
- literature benchmark validation
- downstream integration through generic APIs

It must not become application-specific.

Forbidden public package API shapes:

```python
fit_mea_absorption(...)
fit_lithium_extraction_parameters(...)
screen_lithium_extractants(...)
fit_absorption_column(...)
calculate_extraction_efficiency(...)
calculate_distribution_coefficient(...)
calculate_selectivity(...)
```

Allowed package API concepts:

```python
ParameterSet.from_records(...)
ParameterSet.from_dataset(...)
ParameterSet.to_runtime_dict()
State(...)
TargetRow(...)
TargetDataset(...)
TargetDataset.target_family_summaries()
Equilibrium(mixture, route=..., ...)
Equilibrium(mixture, route="bubble_pressure", T=..., x=...).solve()
Equilibrium(mixture, route="bubble_temperature", P=..., x=...).solve()
Equilibrium(mixture, route="dew_pressure", T=..., y=...).solve()
Equilibrium(mixture, route="dew_temperature", P=..., y=...).solve()
Equilibrium(mixture, route="flash", T=..., P=..., z=...).solve()
Equilibrium(mixture, route="lle", T=..., P=..., z=...).solve()
fit_pure_parameters(...)
fit_binary_parameters(...)
fit_liquid_electrolyte_parameters(...)
epcsaft.capabilities()
epcsaft.provider_native_sdk()
```

Downstream projects compute application metrics from generic outputs.

The list above describes accepted generic API concepts across the current
monorepo and the future package ecosystem. ADR 0005 decides which package owns
each concept after the split: provider objects stay in `epcsaft`; equilibrium
objects move to `epcsaft-equilibrium`; regression objects move to
`epcsaft-regression`.

Current API orientation for agents:

- Prefer the constructor-configured `Equilibrium(mixture, route=..., ...)` workflow object for public equilibrium calls.
- The current production neutral equilibrium surface is one
  `Equilibrium(mixture, route=..., ...).solve()` workflow with route specs
  `bubble_pressure`, `bubble_temperature`, `dew_pressure`, `dew_temperature`,
  `flash`, and neutral nonassociating `lle`; route-specific public methods,
  route-family dataclasses, and private native request payloads are not
  exported compatibility surfaces.
- Treat the native activation matrix and selector core as the source of truth for which route families are production exposed versus declared-not-exposed.
- Treat current neutral deterministic TPD/candidate screening and postsolve
  certification as useful existing route support, not as full HELD. Any
  generalized neutral, associating, electrolyte, or reactive production claim
  still needs the GFPE infrastructure gate, staged HELD proof, exact
  derivatives, and registry evidence update.
- Treat `ParameterSet` as the canonical parameter-family boundary; runtime payload emission belongs to `ParameterSet.to_runtime_dict()`.
- Treat `TargetDataset.target_family_summaries()` as the shared target-family summary shape across retained regression evidence.
- During the monorepo transition, treat `epcsaft.capabilities()` as the
  provider capability contract and `epcsaft_equilibrium.capabilities()` as the
  equilibrium capability contract. The retained `capability_evidence` registry
  still owns test-slice routing for source-checkout validation.
- Treat `epcsaft.provider_native_sdk()` as the provider-owned native SDK
  discovery surface for future extension builds. It does not make
  `epcsaft._core` a stable extension ABI.

---

# 2. Downstream projects and why this package matters

## MEA-Thermodynamics

Needs a publishable true-species reactive electrolyte ePC-SAFT workflow for MEA/CO2/H2O.

The downstream project needs:

- pure MEA, CO2, H2O parameter handling
- MEA association scheme support
- MEA-water and CO2-related binary parameters
- true-species speciation
- activity-based reaction equilibrium
- vapor/liquid fugacity equality for CO2 and other neutral volatile species
- pressure/speciation validation
- ionic parameter regression for MEAH+ and MEACOO-
- Born/SSM/DS parameter regression where justified
- reproducible manuscript figures and parameter tables

The package must provide generic equilibrium and regression capabilities. The MEA repo owns manuscript data, plots, interpretation, and application-specific wrappers.

## Lithium_Extraction

Needs electrolyte LLE and reactive electrolyte LLE support for brine/organic solvent systems.

The downstream project needs:

- generic electrolyte LLE with distributed ions
- phase electroneutrality
- mixed salts / common ions
- organic and aqueous phase support
- lithium and sodium species in aqueous and possibly organic phases
- reaction-coupled phase transfer when a chemistry model requires it
- generic parameter regression where literature parameters are missing
- output phase compositions, activities, fugacities, and reaction extents

The package must not compute lithium extraction efficiency, selectivity, or distribution coefficient. The downstream repo computes those from generic equilibrium outputs.

## MEA-Absorption-Column

Needs generic reactive vapor/liquid equilibrium and speciation outputs that can be used inside column calculations.

The package provides thermodynamic state/equilibrium results. The column project owns column discretization, transport, kinetics, and absorber metrics.

---

# 3. Scientific model foundation

The core ePC-SAFT model is based on residual Helmholtz energy:

```text
a_res = a_hard_chain + a_dispersion + a_association + a_Debye_Huckel + a_Born
```

The package must therefore treat the EOS as a coupled thermodynamic model, not as isolated property helpers.

Required contribution families:

- hard-chain
- dispersion
- association
- Debye-Hückel / ionic
- Born
- modified Born / SSM / DS liquid-electrolyte terms
- relative-permittivity and concentration-dependent dielectric behavior

The literature basis requires:

- pure neutral parameters: `m`, `sigma`, `epsilon`
- associating parameters: association energy and association volume
- ion parameters: ionic diameter / solvated diameter and ion-solvent dispersion energy
- modified Born parameters: `d_born`, `f_solv`, and related solvent/ion terms
- binary parameters: `k_ij`, `l_ij`, `k_hb_ij`

The package must treat `k_ij`, `l_ij`, and `k_hb_ij` as real required parameter families. They are not optional vocabulary.

---

# 4. Non-negotiable backend policy

Two literal tokens are banned from committed repository text.

Define them only as fragments in scripts/tests to avoid writing the exact strings:

```python
BANNED_MISSING_BACKEND_TOKEN = "backend" + "_" + "unavailable"
BANNED_NONEXACT_DERIVATIVE_TOKEN = "finite" + "_" + "difference"
```

The exact assembled strings must not appear anywhere in committed repository text, including:

- source
- tests
- docs
- prompts
- GoalBuddy files
- issue-scope notes
- capability strings
- diagnostics
- comments
- generated committed artifacts

The package must not use missing-backend status strings as normal runtime output for required workflows.

The package must not use non-exact derivative substitutes.

Allowed derivative mechanisms:

- exact analytic derivatives
- CppAD for explicit algebraic derivatives
- analytic implicit sensitivities
- CppAD implicit sensitivities

Production solvers and regression loops must be native C++ where the package owns the algorithm.

Python may:

- validate inputs
- construct problem objects
- serialize data
- call native code
- format outputs

Python may not own production optimizer loops, residual packing, or solver iterations for required workflows.

---

# 5. What prior agents got wrong

Prior agents often completed a narrow safe slice and marked the issue done.

That is no longer allowed.

Common failure modes:

- inventory treated as benchmark implementation
- diagnostic route treated as solver implementation
- staged workflow treated as coupled equilibrium
- synthetic payload treated as downstream integration
- missing paths recorded as limitations
- unsupported parameter families called out of scope
- Ceres dependency presence treated as native Ceres production regression
- CppAD availability treated as complete derivative coverage
- association sensitivity deferred without implementing the actual required path
- GoalBuddy final audit marked `full_outcome_complete: true` despite known missing required workflows

A PR may not close an issue by being honest about incompleteness. Honesty is required, but incompleteness means the issue remains open.

---

# 6. Completion standard

An issue is complete only when every in-scope workflow is:

1. Implemented in production code.
2. Exercised through public generic APIs.
3. Backed by native C++ implementation where the package owns the algorithm.
4. Using analytic, CppAD, analytic-implicit, or CppAD-implicit derivatives.
5. Tested with executable tests.
6. Validated with real or literature-backed data when relevant.
7. Free of banned literal tokens in committed text.
8. Free of synthetic-only or monkeypatched proof.
9. Reflected in capabilities without overclaiming.
10. Usable by downstream projects without private package workarounds.

The final audit question is:

```text
Can a downstream project use this generic package workflow now without adding missing package code?
```

If the answer is no, the issue is not complete.

---

# 7. Required architecture

## EOS harness

Must support:

- residual Helmholtz energy and contribution maps
- property evaluation
- fugacity coefficients
- activity coefficients
- chemical potentials
- relative permittivity
- density and pressure closure
- parameter derivatives
- composition derivatives
- temperature/density derivatives where required
- contribution-level traceability

## Derivatives

Must support:

- CppAD scalar substrate across EOS and residual layers
- association solved-state implicit sensitivities
- density-root implicit sensitivities
- bubble/dew solved-state sensitivities
- LLE residual Jacobians
- electrolyte LLE residual Jacobians
- reactive/speciation residual Jacobians
- reactive LLE coupled residual Jacobians
- regression objective Jacobians

No direct differentiation through iterative loops is accepted as production derivative support.

## Association

Association site fractions are solved internal states.

Required:

- stable association value evaluation
- residual equations for association site fractions
- Jacobian of association residuals with respect to site fractions
- parameter/composition/density sensitivities through implicit differentiation
- support for associating pure components and associating mixtures
- support for `k_hb_ij` when association interactions require it
- support for `k_ij` regression even when one or both components associate

The package must not claim `k_ij` or `k_hb_ij` cannot be supported merely because association is involved. The required solution is association implicit sensitivity plus native regression integration.

## Regression

The package must provide native Ceres or equivalent native optimizer loops for:

- pure neutral regression
- pure ion regression
- binary `k_ij`
- binary `l_ij`
- binary `k_hb_ij`
- association parameters
- `d_born`
- `f_solv`
- relative-permittivity parameters
- density rows
- vapor-pressure rows
- fugacity rows
- activity rows
- MIAC rows
- osmotic rows
- VLE partial-pressure rows
- LLE phase-composition rows
- reactive speciation rows
- reactive pressure/speciation rows

Required regression result fields:

- optimizer backend
- derivative backend
- parameter map
- initial parameters
- final parameters
- parameter movement
- active bounds
- objective initial
- objective final
- row diagnostics
- source summaries
- target-family summaries
- residual block norms
- convergence status

Current claim boundary:

- Reactive regression is not a current public production optimizer or residual-evaluator surface. Reintroduce it only after native optimizer ownership, public API shape, and capability evidence are complete.

## Equilibrium

Required production solvers:

- neutral VLE / bubble / dew
- direct fugacity-based volatile partial pressure where valid
- neutral LLE
- electrolyte LLE with distributed ions
- activity-based speciation
- reactive VLE / bubble
- reactive LLE
- reactive electrolyte LLE

Staged workflows may exist only as initialization or diagnostics. They do not satisfy coupled equilibrium requirements.

## Benchmarks

A literature benchmark is complete only when it is executable and tolerance-checked.

A manifest, inventory, or data list does not count.

Required benchmark families:

- Gross/Sadowski pure PC-SAFT parameters
- Gross/Sadowski associating systems
- Baygi MEA PC-SAFT reproduction
- Held/Cameretti aqueous electrolyte density/MIAC
- Held alcohol/salt MIAC and mixed-solvent prediction
- Held 2014 revised ePC-SAFT electrolyte phase behavior
- Bülow/Ascani/Held advanced Born and dielectric behavior
- Figiel 2025 modified Born / SSM / DS
- Ascani 2022 electrolyte LLE with distributed ions
- Ascani 2023 reactive phase equilibrium
- Khudaida 2026 electrolyte salting-out LLE
- Rezaee lithium extraction thermodynamic modeling
- MEA-CO2 pressure/speciation data validation with copied fitted parameters
- downstream-facing lithium/column contract workflows with in-worktree inputs

---

# 8. Required milestones

GitHub milestones use short dashboard names. This file owns the detailed
meaning behind each name; issues and slice plans must not invent a separate
milestone taxonomy.

Every GitHub issue must belong to exactly one milestone. Larger local plan files
map to one tracking issue inside the matching milestone, and implementation
issues are the micro changes that move that tracking issue forward. The
GitHub Project is the operating dashboard: group and sort by Milestone,
Package, Capability, Backend, Readiness, and Release target. Keep technical
precision in issue bodies and plan checklists, not in milestone titles.
Use the repository issue templates for tracking, micro, and gate issues, and
use the pull request template so PRs carry issue, milestone, Project, plan,
validation, and capability evidence explicitly.

`docs/milestones/` is the local planning root for the GitHub milestone
dashboard. It stores package context, milestone-owned plans, optional issue
handoff files, and milestone-owned registries. GitHub Issues and the
`ePC-SAFT Roadmap` Project remain authoritative for live tracker state.

For generalized fluid-phase equilibrium work, use
`docs/milestones/M4-equilibrium/plans/stage-by-stage-implementation-plan.md` as the GFPE-first
execution plan. The milestones below define the package completion envelope;
the stage plan breaks GFPE into concrete pretreatment, implementation gates,
and exit evidence.

## M0 - Governance

Planning hygiene, tracker setup, labels, issue templates, completion rules,
GoalBuddy/project discipline, and repo-wide process gates.

- purge banned literal tokens from the repo
- add lexical guard
- add GoalBuddy lifecycle guard
- remove classification-as-completion language
- update future prompts
- ensure no merged goal remains active
- keep issue, milestone, Project, plan, and capability state aligned

## M1 - Packages

Monorepo package layout, package ownership, test relocation, provider-only
build proof, extension-native boundaries, and package CI/docs/release
structure.

- keep the monorepo package layout aligned with `docs/milestones/M1-packages/plans/monorepo-package-migration.md`
- prove root `epcsaft` can build as a provider-only package
- keep package-local tests under the package that owns the behavior
- split extension-native ownership from provider `_core`
- keep package docs, CI lanes, and release choreography aligned with ownership

## M2 - Python API

Public Python package surface, user-facing workflow ergonomics, result schemas,
diagnostics, examples, import stability, and package-level user experience.

- keep public imports stable and generic
- keep Python wrappers thin, typed, and aligned with native/provider contracts
- standardize result, diagnostic, and capability payloads before public claims
- keep examples, docs, and validation commands aligned with actual package
  behavior
- improve input validation and error messages without hiding missing production
  code behind fake defaults

## M3 - EOS

Provider EOS/state/parameters, native SDK contract, exact derivatives,
CppAD/implicit sensitivities, and provider-only capability claims.

- package-wide CppAD scalar support
- scalar-templated EOS residuals
- association implicit sensitivities
- density-root implicit sensitivities
- bubble/dew sensitivities where provider-owned contracts require them
- property derivative result APIs
- derivative coverage tests
- provider-native SDK contract and capability evidence

## M4 - Equilibrium

epcsaft-equilibrium, GFPE, selector/admission, Ipopt NLP, HELD/TPD, phase
discovery, and VLE/LLE/electrolyte/reactive equilibrium workflows.

- GFPE infrastructure gate: sparse NLP contracts, route scaling, domain bounds, smooth variable maps, Ipopt barrier constraints, diagnostics, and exact derivative policy
- staged HELD phase discovery and postsolve phase-set certification before generalized neutral production admission
- neutral multiphase phase-set discovery extension after the neutral TP flash proof; VLLE-specific tests are not the immediate priority
- native coupled activity speciation
- native derivative-backed neutral LLE
- native electrolyte LLE with distributed ions
- native coupled reactive LLE
- native coupled reactive electrolyte LLE
- real residual/Jacobian diagnostics

## M5 - Regression

epcsaft-regression, TargetDataset/result contracts, Ceres optimizer,
parameter sensitivities, and pure/binary/electrolyte regression workflows.

- Ceres owns production optimizer loops
- CppAD/implicit derivatives feed Jacobians
- Python only validates/serializes
- all required target families supported
- all binary parameter families supported
- real parameter movement tests
- regression result schemas and capability evidence stay honest

## M6 - Validation

Executable literature benchmarks, registry evidence, capability evidence,
docs/test proof, and release-quality validation gates.

- every named benchmark executable
- every benchmark has fixture, command, expected result, tolerance
- benchmark suite proves parameter/equilibrium behavior
- capability registries and generated docs reflect only proven workflows

## M7 - Release

Downstream integration, install proofs, PyPI/release choreography, migration
docs, and no private downstream workarounds.

- install local package into each downstream repository
- run one real workflow per downstream repo
- prove generic APIs are sufficient
- no copied EOS implementation
- no private workaround for required package behavior
- publish and migration docs match the monorepo package release model

---

# 9. Agent working rules

Every agent must:

1. Read this file.
2. Read the replacement master issue.
3. Inspect current `origin/main`.
4. State whether its task is derivative, regression, equilibrium, benchmark, process, or downstream.
5. Identify the exact production workflow it must make work.
6. Identify tests that prove it.
7. Refuse to close by inventory, diagnostics, staging, synthetic fixtures, or limitation text.
8. Avoid banned exact literals in committed text.
9. Keep APIs generic.
10. Open capability, release, benchmark, or production-native PRs only when the
    claimed production workflow works.

PRs that claim release readiness, capability support, benchmark evidence, or
production native behavior must answer:

```text
What downstream workflow can now run that could not run before?
What production native code path now exists?
What derivative path is used?
What real data or benchmark proves it?
What public API exercises it?
What tests would fail if this regressed?
```

If those answers are weak for a PR making one of those claims, do not merge.
Ordinary early package-development PRs use the M0 local-proof-first policy and
do not need boilerplate production-proof answers.
