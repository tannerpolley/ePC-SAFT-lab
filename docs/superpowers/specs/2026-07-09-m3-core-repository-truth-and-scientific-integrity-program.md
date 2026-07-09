# ePC-SAFT Repository Truth And Scientific Integrity Program

## Approval And Ownership

- Approved design: truth-first execution sequence
- Approval date: 2026-07-09
- Program sponsor: `M3 - Core EOS`
- Primary repo owner: `packages/epcsaft`
- Workstream owners:
  - M3: provider inputs, EOS state/derivatives, repo validation, SDK and build metadata
  - M4: `packages/epcsaft-equilibrium`, selector architecture, Ipopt routes, phase and chemical equilibrium evidence
  - M5: `packages/epcsaft-regression`, Ceres routes, target contracts and retained-fit evidence
  - M6: retained literature-validation artifacts only; package behavior remains owned by M3/M4/M5
- Cross-milestone scope: explicitly approved by the user for this repository-wide audit and remediation program

This document is the durable design for the full program. Every implementation
task must still stay inside its named milestone and package boundary. A search
hit in a sibling package is evidence of a possible dependency, not permission
to move ownership.

## Purpose

Make the repository mechanically truthful, scientifically traceable, and
maintainable enough that a passing capability claim means all of the following:

1. the public route exists through the canonical package boundary;
2. its complete test node is collected by the official test runner;
3. the test executes the production native path;
4. numerical acceptance checks thermodynamic residuals, not only solver exit;
5. input parameters and target data have explicit units and provenance;
6. required wheels contain their audited native dependency closure; and
7. the implementation has one clear owner rather than duplicated route logic.

The project must fail loudly when any of those statements is false. Missing
scientific data may not be replaced with invented numerical values, omitted
user controls may not be silently ignored, and an unfinished validation ladder
may not appear as production evidence.

## Scientific Scope And Literature Basis

The package family is intended to provide a native Python implementation of
PC-SAFT and electrolyte PC-SAFT with separate equilibrium and regression
extensions.

- The original PC-SAFT model covers a hard-chain reference plus dispersion and
  was demonstrated for pure vapor pressure/liquid volume, mixture VLE, and
  high-pressure polymer LLE. Nonassociating compounds use three fitted pure
  parameters. See Gross and Sadowski (2001),
  <https://doi.org/10.1021/ie0003887>.
- The associating extension adds two pure association parameters and was
  demonstrated for pure associating fluids plus binary VLE and LLE. See Gross
  and Sadowski (2002), <https://doi.org/10.1021/ie010954d>.
- The electrolyte extension was demonstrated against density, vapor-pressure,
  and mean-ionic-activity data for aqueous salts. Ion parameters are empirical
  scientific inputs, not values that software may infer from species spelling.
  See Held, Cameretti, and Sadowski (2008),
  <https://doi.org/10.1016/j.fluid.2008.06.010>.
- Weak-electrolyte use requires explicit association/dissociation chemistry and
  equilibrium constants. See Held and Sadowski (2009),
  <https://doi.org/10.1016/j.fluid.2009.02.015>.
- Revised ePC-SAFT work extends the intended application surface to
  multicomponent electrolyte VLE, LLE, and SLE, but that literature scope does
  not make every software route production-ready without repository-owned
  executable proof.

These references define model intent. Repository capabilities remain narrower
than the literature until exact package evidence admits each route.

## Audited System

### Package roles

| Package | Intended role | Current native backend |
| --- | --- | --- |
| `packages/epcsaft` | parameters, model options, EOS state, properties, exact derivatives, provider SDK | C++/pybind11/CppAD |
| `packages/epcsaft-equilibrium` | selector-owned bubble, dew, flash, LLE, multiphase and reaction-equilibrium workflows | C++/pybind11/Ipopt |
| `packages/epcsaft-regression` | pure, binary and electrolyte parameter fitting | C++/pybind11/Ceres/CppAD |

### Scale and maintainability pressure

The audit measured approximately 22,280 lines in the provider package, 45,916
in equilibrium, and 7,128 in regression. The most important structural
hotspots are:

| File | Approximate lines | Structural concern |
| --- | ---: | --- |
| `two_phase_eos_route.cpp` | 7,225 | route dispatch, solve orchestration, acceptance and payload construction mixed together |
| `bubble_dew.cpp` | 4,960 | multiple thermodynamic formulations and branch behavior in one unit |
| `register_bindings.cpp` | 4,118 | broad public/native surface assembled in one binding unit |
| `epcsaft_regression/core.py` | 3,322 | contracts, payload construction, orchestration and result annotation combined |
| `workflows.py` | 1,930 | public workflow and route-specific bypass behavior mixed together |
| `datasets.py` | 1,755 | data lookup, embedded defaults, normalization and policy combined |

Files above 1,000 lines are presumed decomposition candidates. Refactoring is
accepted only when it deletes concepts or enforces a clearer owner; moving the
same branching into more files is not sufficient.

## Verified Audit Findings

### P0: official repository truth is red

1. `run_pytest.py --all --collect-only -q` collects 828 tests and exits with
   three import-file-mismatch errors caused by duplicate package-local test
   basenames. Diagnostic importlib mode collects 831 and exits successfully.
2. Bare repository collection reaches 935 tests and nine errors because it also
   collects analysis-local suites with missing optional dependencies and stale
   `tests.helpers` imports. The bare runner and official wrapper therefore do
   not describe the same repository contract.
3. The default generic gate reports 180 passing and seven failing architecture
   tests. Failures cover derivative-text policing, activation/route mismatch,
   duplicated result acceptance, chemical-equilibrium ownership, a public
   reaction helper and direct electrolyte native dispatch.
4. Runtime equilibrium capabilities claim seven production families while the
   confidence registry contains three. Six nonreactive families have Python
   route specs, but `electrolyte_lle` and `neutral_multiphase_nonassoc` branch
   around the native selector solve and build acceptance through route-specific
   paths. A declared route spec therefore does not prove selector ownership.
5. The required standalone chemical-equilibrium proof reports balance infinity
   norm about `2.6` and stationarity about `73.79`, against required limits of
   `1e-8` and `1e-6`. The final continuation point is rejected, yet the route is
   public/production and its analysis metadata says `complete`.

### P0: scientific inputs can be invented silently

`packages/epcsaft/src/epcsaft/model/datasets.py` contains embedded component
defaults and a deterministic ion policy that can invent segment count,
association values, Born diameter, relative permittivity and solvation values.
Missing optional fields and absent binary matrices can become numerical zero
without recording whether zero is physically intended. `ParameterSet` legacy
conversion also supplies model values and can accept payloads without a
complete, traceable schema.

The software must distinguish three states: explicit measured/fitted value,
explicit model-defined structural zero, and missing value. Only the first two
may reach a native calculation.

Further trace found that the defect spans `parameters.py`, `datasets.py`,
`frontend/mixture.py` and `state/native_payload.py`, not one loader:

- named dataset discovery points at a nonexistent package path and returns an
  empty catalog;
- unknown legacy keys can become runtime options, and Held 2012 currently
  parses successfully before crashing when derived receipt fields are treated
  as user options;
- `get_prop_dict()` preserves directed interaction cells while
  `ParameterSet.from_dataset()` reads one triangle and symmetrizes it; the 2019
  Bülow matrix therefore produces loader-dependent values;
- temperature-dependent water diameter, dielectric and `k_ij` correlations,
  plus composition-dependent mixed-solvent rules, are resolved once during
  mixture construction even though later states may use different conditions;
- the documentation assigns the Held-2012 hydrogen-bond correction to
  association energy while the source-consistent native equation applies it to
  association volume.

The target architecture must carry typed constants/correlations to state
construction and create one condition-resolved native payload and receipt.

### P0: regression accepts controls that do not control the solve

The public regression surface accepts weights, loss selection, fixed
parameters and solver options that are partly written into returned metadata
after the native solve rather than passed into it. This is an API correctness
defect: returned annotations imply a problem different from the one solved.
Target rows also lack a complete finite-value, units and source contract.

Runtime probes confirmed that extreme changes to public pure and binary
weights, loss and iteration controls leave fitted parameters, objective and
evaluation count identical while the returned receipt changes. Pure target
subsets raise mapping errors and reordered targets can return a successful but
misassigned parameter map. The native layer always uses a quadratic loss,
hard-codes several pure controls and permits a non-improving termination to be
reported as success. The target dataset type is disconnected from the public
fit path and accepts non-finite observations, missing provenance, invalid
composition totals and duplicates.

### P1: evidence breadth is narrower than capability breadth

- Pure-neutral has traceable data elsewhere in the repository but no retained
  public-fit proof joining observations, predictions and the native receipt.
- Binary `k_ij` has independent Susial 2021 VLE rows available, but current
  native admission tests are synthetic and the retained plot shows parameters
  rather than literature observations against predictions.
- Pure-ion and liquid-electrolyte regressions are synthetic or self-recovery
  tests and cannot independently admit a production claim.
- Reactive speciation has component tests but fails its required end-to-end
  thermodynamic proof.
- Provider derivative and representative equilibrium proofs pass, but route
  families and proof registries are not one-to-one.
- A strict derivative text gate produces seven false positives from substrings
  inside neutral diagnostic names. It is not a reliable numerical-method gate.

### P1: distribution proof is host-dependent

The repaired equilibrium wheel now bundles its audited Ipopt/BLAS/LAPACK/MUMPS
runtime closure and passes an isolated import/native smoke. A wheel built on
the current Ubuntu host is tagged `manylinux_2_39_x86_64`, however, which is not
evidence of broad older-Linux compatibility. Release CI exercises CPython 3.13
while package metadata permits Python 3.9 and newer.

### P1: ownership duplication creates inconsistent acceptance

`two_phase_eos_route.cpp` constructs result/acceptance payloads outside the
canonical result builder. Public reaction and electrolyte helpers can bypass
the intended selector lane. Chemical-equilibrium solve/contract logic lives in
a route-specific owner while architecture policy requires shared selector/core
ownership. These are correctness risks, not cosmetic organization concerns.

## Chosen Strategy

The approved order is truth-first.

Two alternatives were rejected:

- Science-first would attempt the MEA chemical-equilibrium repair while false
  production claims and broken collection remain visible.
- Architecture-first would split giant files before the repository can prove
  which behavior is correct and which behavior should be deleted.

Truth-first establishes a trustworthy measurement system, then makes the
scientific and structural changes against that system.

## Program Architecture

### Phase 1: Truth And Green Gate

Owner: M3 for repository validation; M4 for equilibrium evidence, claims and
selector corrections.

Required outcomes:

1. Root pytest configuration defines the intended package/repo suite and uses
   importlib collection. Analysis-local tests execute only through named,
   dependency-complete lanes.
2. Bare collection and `run_pytest.py --all --collect-only -q` collect the same
   node set and both exit zero.
3. Exposed capability families, native-selector-owned solve families and
   executable confidence evidence are checked for exact set equality. A Python
   route-spec row alone cannot satisfy selector ownership.
4. Every production evidence entry names exact collected node IDs or a strict
   checker command and records the owning package.
5. Reactive speciation is removed from public production claims and the
   standalone-CE analysis records the live failure until the complete proof
   passes. Component tests remain available as development evidence.
6. `electrolyte_lle` and `neutral_multiphase_nonassoc` are also removed from
   public production exposure until their solves and results enter through the
   native selector. The immediate truthful surface is the four selector-backed
   families: bubble/dew, neutral TP flash, neutral LLE and single-component VLE.
7. Public equilibrium solve behavior enters through one selector-owned lane.
8. Result construction and acceptance delegate to the canonical result
   builder. Route-specific code supplies thermodynamic quantities, not an
   independent acceptance policy.
9. Text gates match forbidden semantic tokens at boundaries and do not reject
   legitimate diagnostic identifiers.
10. `run_pytest.py -q` exits zero without allowlists that hide architecture or
   scientific failures.

Phase 1 is complete only when the repository can tell the truth about later
phases.

### Phase 2: Provider Input Integrity

Owner: M3, `packages/epcsaft`.

Required outcomes:

1. Remove deterministic scientific parameter generation and undocumented
   component value tables from runtime lookup code.
2. Define typed pure-component, binary-interaction and model-option input
   records with required units, finite-value checks and source identifiers.
3. Reject unknown keys and missing required model terms.
4. Treat structural zeros as explicit schema values with a named model reason;
   do not conflate blank cells with zero.
5. Keep model policy defaults only when the equation definition itself supplies
   them; expose their chosen preset in runtime metadata.
6. Move literature parameter snapshots into the existing source-owned data and
   provenance layout.
7. Add characterization tests for every currently supported neutral,
   associating, ionic and mixed input path before removing old behavior.

### Phase 3: Regression Contract Correctness

Owner: M5, `packages/epcsaft-regression`.

Required outcomes:

1. Every accepted public control changes the native optimization problem or is
   rejected before solving.
2. Weights, robust loss, fixed parameters, bounds, tolerances and evaluation
   limits survive Python-to-native payload conversion and appear in the native
   problem receipt.
3. Returned problem metadata is generated from the actual submitted native
   payload, not added afterward.
4. Target data require finite values, named units, source citation, observable
   definition and composition-basis validation.
5. Each production regression family has independent, traceable literature
   rows plus a retained plot containing both literature data and predictions.
6. Synthetic recovery tests remain unit tests and cannot admit capabilities.

### Phase 4: Equilibrium Scientific Admission

Owner: M4, `packages/epcsaft-equilibrium`.

Required outcomes:

1. Reproduce the failing MEA continuation point with retained primal,
   constraint, activity, Jacobian, gradient and multiplier diagnostics.
2. Establish whether the root cause is standard-state convention, reaction
   stoichiometry/rank, initialization, derivative implementation, scaling or
   convergence acceptance before changing solver tuning.
3. Repair the smallest canonical owner and retain real literature inputs.
4. Require final `lambda=1`, balance infinity norm at most `1e-8`, stationarity
   at most `1e-6`, accepted native status and consistent species constraints.
5. Re-admit reactive speciation only through the selector and only when the
   full strict checker, package tests and retained evidence pass together.
6. Apply the same admission model to electrolyte LLE and future multiphase
   families: solver exit alone never proves phase or chemical equilibrium.

### Phase 5: Distribution And Downstream Proof

Owners: M3 provider metadata/SDK, M4 Ipopt extension, M5 Ceres extension.

Required outcomes:

1. Build Linux release wheels in a controlled manylinux environment whose tag
   matches the declared compatibility target.
2. Test every declared Python minor version or narrow package metadata to the
   versions actually supported.
3. Prove provider-only, provider-plus-equilibrium,
   provider-plus-regression and all-package installations from artifacts.
4. Inspect ELF `NEEDED`, RPATH/RUNPATH and wheel contents; reject host-path or
   unowned native dependencies.
5. Run imports and representative native solves with an empty
   `LD_LIBRARY_PATH` and no source checkout on `PYTHONPATH`.
6. Retain machine-readable build receipts with wheel tag, package versions,
   native dependency list and smoke command.

### Phase 6: Maintainability Cut Lines

Owners follow the package that owns each file.

Required outcomes:

1. Add characterization tests before moving behavior.
2. Split orchestration from thermodynamic formulation, acceptance and payload
   conversion.
3. Replace scattered route conditionals with typed route specifications and
   explicit dispatch.
4. Decompose binding registration by owned public surface.
5. Split regression contracts, native payloads, result receipts and route
   adapters out of `core.py`.
6. Split dataset storage/provenance from validation and lookup policy.
7. No new or materially modified production file may remain above 1,000 lines
   without a recorded ADR explaining why one cohesive unit is safer.
8. A decomposition must reduce branching/coupling metrics or delete duplicated
   logic; file movement alone is not completion.

## Canonical Evidence Contract

Every production capability record must provide:

| Field | Meaning |
| --- | --- |
| `family` | stable public route/fitting family |
| `owner` | package and milestone |
| `public_entrypoint` | exact Python entry point |
| `native_owner` | exact native target/module when applicable |
| `proof_nodes` | collected pytest node IDs |
| `strict_checkers` | commands whose nonzero exit blocks admission |
| `data_sources` | retained literature/source identifiers |
| `artifact_paths` | plots, plotted data and numerical receipts |
| `acceptance_metrics` | thermodynamic and numerical limits |

Production-family sets are derived from records satisfying the complete
contract. They are not maintained as an independent hand-written list.

## Cross-Cutting Engineering Rules

- Test-first changes are required for features and defects.
- Scientific model predictions use real, traceable literature data and retain
  a comparison plot.
- A native solver result is accepted only after independent residual and
  physical-domain checks.
- Provider/equilibrium/regression package boundaries remain explicit.
- The provider may expose a stable SDK; extensions may not reach through
  private provider implementation paths.
- No compatibility wrapper survives after a migrated path is complete.
- Unknown inputs, conflicting configuration and missing proof produce a loud
  error.
- Generated evidence must be reproducible from a documented command and must
  not rely on a developer home path.
- Architecture gates may be made more precise, but may not be weakened to make
  an existing violation disappear.

## Non-Goals

- No blanket claim that the software implements every application demonstrated
  in PC-SAFT/ePC-SAFT literature.
- No hidden row-specific solver seeds or parameter edits.
- No application-study metrics owned by downstream repositories.
- No synthetic-only production admission.
- No simultaneous rewrite of all large modules before behavior is
  characterized.
- No release publication or push as part of this local implementation program.

## Risks And Controls

| Risk | Control |
| --- | --- |
| Demoting a route breaks callers | remove the false production/public promise explicitly, document the exact strict proof required for return |
| Strict inputs reveal incomplete data | migrate only source-backed values; fail at the boundary for unresolved records |
| CE repair becomes solver-option tuning | require retained formulation/derivative diagnostics before tuning changes |
| Refactor changes numerics | characterization fixtures and byte/numerical receipts before extraction |
| Wheel passes only on build host | isolated artifact install, ELF audit and older-manylinux build environment |
| Cross-milestone scope blurs ownership | every task, proof and commit names one owning package/milestone |

## Program Completion Criteria

The full program is complete when:

- official and bare test collection agree and are error-free;
- the default gate is green;
- production capabilities, selector routes and complete evidence are exactly
  aligned;
- no runtime scientific parameter is invented from a species name or blank
  field;
- regression controls describe the problem actually solved;
- every admitted equilibrium family passes its strict thermodynamic residual
  proof;
- all declared distribution targets pass isolated artifact tests; and
- the identified giant modules have clear owners and materially smaller,
  characterized responsibilities.
