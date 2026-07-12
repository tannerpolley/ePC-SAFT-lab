# Source-Faithful Equilibrium Recovery And Curated Migration

Milestones: `M1 - Packages`, `M3 - EOS`, `M4 - Equilibrium`, and
`M6 - Validation`, with program sequencing under `M0 - Governance`
Packages: `packages/epcsaft` and `packages/epcsaft-equilibrium`
Status: `approved program basis; implementation requires stage-owned plans`
Last reviewed: `2026-07-12`

## Context

The ePC-SAFT provider is substantially more mature than the equilibrium
extension. The provider has a bounded thermodynamic responsibility and has
source-backed equation, derivative, and property-validation evidence. The
equilibrium extension contains valuable exact-derivative, association, Ipopt,
electroneutral-coordinate, local-NLP, and postsolve work, but accumulated
several generations of route, diagnostic, paper-specific, and certification
logic in one installed package.

The existing generalized-fluid-phase-equilibrium doctrine contains strong
package-boundary and numerical-engineering rules, but it is not a sufficiently
tight implementation authority. It combines package architecture, algorithm
doctrine, activation policy, validation evidence, historical issue state, and
debugging instructions. Its description of HELD Stage III is not source
faithful, and its electrolyte roadmap combines Perdomo HELD2 modified-mole
coordinates with Ascani counterion-pair methodology without an equivalence
derivation.

This specification preserves the proven work while correcting those
scientific and architectural boundaries. It extends, rather than replaces:

- `2026-07-11-m0-repository-health-stabilization-and-execution-readiness-design.md`;
- `2026-07-11-m3-m4-deletion-first-provider-equilibrium-simplification-design.md`;
- `2026-07-10-m3-eos-versioned-state-resolved-model-input.md`;
- `2026-07-10-m4-equilibrium-canonical-owner-decomposition.md`.

Where an earlier document calls sampled-candidate bookkeeping, a residual
refinement, or a counterion-pair path HELD or HELD2 completion, this
specification governs the meaning of those terms for future work.

## Verified Baseline

At the 2026-07-12 review checkpoint:

- public equilibrium routes were limited to `bubble_pressure`,
  `dew_pressure`, and scoped methane/ethane/propane
  `single_component_vle`;
- bubble/dew pressure used direct local boundary NLPs and did not execute a
  complete HELD phase-discovery algorithm;
- neutral TP flash and neutral LLE had useful exact local NLP and postsolve
  component evidence but remained closed;
- neutral Stage II reported `held_stage_ii_dual_loop_status = not_performed`
  in retained tests;
- electrolyte Stage II retained an open bound gap and explicitly reported an
  incomplete dual loop;
- associating phase-block and implicit-association derivative machinery was
  valuable and reached scoped Gross pressure-route evidence;
- electrolyte code retained useful charge-neutral lifting, continuous TPD,
  counterion-pair, projected-residual, and postsolve components, but did not
  implement Perdomo HELD2 as published;
- standalone CE had a real homogeneous Gibbs/Ipopt foundation but its retained
  nonideal MEA balance and stationarity proof failed;
- reactive LLE, reactive electrolyte LLE, and simultaneous CPE were not
  implemented production solvers;
- the worktree was clean on `main` at `8e334c85`, four commits ahead of
  `origin/main`.

These are checkpoint facts, not permanent capability declarations. Every
stage refreshes the relevant state before acting.

## Scientific Classification

Material claims use these meanings:

- `verified`: checked against a local source document, implementation owner,
  test, or retained run receipt;
- `inference`: a design conclusion drawn from verified facts;
- `unknown`: not established and therefore not usable for admission.

### Pereira HELD

Verified: Pereira 2012 describes a nonreactive molecular-fluid fixed-`T,P,z`
algorithm with three coordinated stages:

1. multistart/tunnelling stability search;
2. an upper linear dual problem alternating with nonconvex Helmholtz lower
   problems, cutting planes, bound updates, and candidate-phase discovery;
3. direct total free-energy minimization over the candidate phase set,
   convergence checks, trace-component refinement, and return to Stage II when
   incomplete.

HELD is not one monolithic NLP. Ipopt may be the common local-NLP backend, but
the Stage II upper problem remains a distinct linear optimization problem.

### Perdomo HELD2

Verified: Perdomo 2025 extends HELD to nonreactive strong, fully dissociated
electrolyte fluid phases. It eliminates one charged species through
electroneutrality and uses modified mole numbers and modified mole fractions.
It does not cover weak-electrolyte speciation, reactions, or solids.

### Ascani Electrolyte Equilibrium

Verified: Ascani 2022 uses independent counterion-pair coordinates,
mean-ionic equilibrium conditions, stability testing, successive phase
addition, and an equilibrium-equation solve. Perdomo explicitly distinguishes
its modified-mole transformation from this counterion-pair construction.

Both formulations may be retained. They are separate algorithm families until
an equation-level equivalence proof says otherwise.

### Stage III

Verified source doctrine: canonical HELD Stage III directly minimizes total
free energy under material balance, bounds, and formulation-specific feasible
coordinates. Equal pressure and the applicable independent potential
conditions arise from stationarity and are checked in postsolve. Molecular
species use chemical-potential equality. Perdomo HELD2 uses its independent
modified-potential conditions, while the Ascani counterion-pair formulation
uses independent mean-ionic or pair conditions. Individual ionic
electrochemical potentials may be compared only when the phase electric or
Galvani-potential convention is explicit.

A strict residual equation solve may remain an optional corrector or
diagnostic. It is not the defining HELD Stage III objective.

## Goals

1. Preserve the provider, derivative, association, Ipopt, local-NLP,
   electroneutral, CE-schema, and postsolve work that has independent value.
2. Correct HELD, HELD2, Stage II, Stage III, boundary-route, CE, and CPE
   terminology before further implementation.
3. Separate algorithm parity, local equilibrium validity, phase-discovery
   completeness, and literature/model reproduction.
4. Establish one provider-to-equilibrium resolved-input boundary.
5. Establish one local-NLP interface and one Ipopt adapter without forcing
   distinct mathematical problems into one NLP.
6. Consolidate currently public-green routes before attempting broader
   equilibrium admission.
7. Implement neutral HELD and strong-electrolyte HELD2 only through
   source-faithful, independently testable controllers.
8. Keep Ascani electrolyte equilibrium, standalone CE, and simultaneous CPE
   as explicitly distinct formulation families.
9. Prepare a curated repository migration that transfers proven owners and
   evidence rather than accumulated compatibility structure.
10. Keep verification proportional: focused characterization per slice,
    package confidence at stage boundaries, full proof only at admission or
    closeout.

## Non-Goals

- No implementation is authorized by this specification alone.
- No public capability expansion.
- No immediate repair of Khudaida, Gross, Held, Ascani, Figiel, or other
  paper-specific validation programs.
- No requirement to make every retained paper bundle executable before core
  architecture work.
- No wholesale merge of paused Task 9 work.
- No deletion of valuable internal code before characterization and caller
  inventory.
- No claim of deterministic global optimization unless a separately selected
  deterministic global method and proof contract are implemented.
- No compatibility wrappers, duplicate serializers, backup modules, or fake
  scientific defaults.
- No requirement that every stage run the full repository suite.
- No push, publication, PR, or release without separate user authorization.

## Selected Architecture

```text
Provider-owned resolved model
  -> immutable native model definition
  -> resolve(T, x, state conditions)
  -> PhaseEvaluator

PhaseEvaluator
  -> boundary saturation problem
  -> TPD problem
  -> HELD lower problem
  -> phase-set free-energy refinement problem
  -> homogeneous CE problem

LocalNlpProblem
  -> one exact-derivative Ipopt adapter

HeldController
  -> Stage I
  -> Stage II upper LP / lower NLP loop
  -> Stage III free-energy refinement
  -> trace refinement and postsolve

EquilibriumCertificate
  -> material balance
  -> pressure consistency
  -> molecular chemical-potential consistency
  -> formulation-specific modified-potential or mean-ionic consistency
  -> explicit Galvani-potential handling when individually required
  -> phase distance and duplicate/collapse checks
  -> charge and formula feasibility when applicable
```

The activation descriptor remains the sole runtime exposure authority. Python
constructs typed requests and presents typed results; it does not decide route
admission, solver acceptance, or scientific fallback policy.

## Evidence Separation

Five gates remain independent:

| Gate | Owning question | Primary owner |
| --- | --- | --- |
| EOS validity | Does ePC-SAFT evaluate the intended thermodynamics and derivatives? | M3 |
| Local equilibrium validity | Does a supplied phase-set NLP solve its stated problem? | M4 |
| Phase-discovery validity | Were the relevant stable phases found for the claimed scope? | M4 |
| Algorithm parity | Does the controller implement the named Pereira, Perdomo, or Ascani algorithm? | M4 |
| Literature reproduction | Does the full stack reproduce the selected real system? | M6 |

A paper-specific reproduction cannot substitute for algorithm parity. An
algorithm-stage receipt cannot substitute for ePC-SAFT parameter and data
validity.

## Twelve-Stage Program

### Stage 1: Correct doctrine and terminology

Entry: this specification is accepted and the local paper markdown remains
available.

Deliverables:

- a short package architecture authority;
- separate Pereira HELD, Perdomo HELD2, Ascani electrolyte, standalone CE,
  and reactive CPE doctrine;
- corrected Stage III and boundary-route terminology;
- explicit supersession notes on historical overclaims.

Guard: documentation changes may add a new repository doctrine-contract test,
but may not alter activation, source code, existing tests, or retained results.

Proof: source-anchor contract tests, docs validation, strict Sphinx, and a
search proving no active doctrine calls sampled-candidate bookkeeping a
verified dual loop.

Exit: one unambiguous algorithm vocabulary governs later plans.

### Stage 2: Repair milestone and tracker modeling

Entry: Stage 1 doctrine is accepted.

Deliverables:

- M4 owns algorithm architecture, runtime implementation, and local proof;
- M6 owns benchmark datasets, retained figures, model reproduction, and
  evidence maturity;
- runtime exposure comes only from the native activation descriptor;
- M4 dashboard contains current work, with historical narratives archived;
- issue titles or bodies visibly classify superseded completion claims.

Guard: tracker cleanup does not reopen, close, delete, or reparent live issues
without an exact proposed change set and user approval.

Proof: local mirror validators, dependency dry run, registry contract tests,
and docs validation.

Exit: roadmap state, runtime state, and validation state are separately
discoverable.

### Stage 3: Characterize and classify the current implementation

Entry: doctrine and ownership taxonomy are stable.

Deliverables:

- caller and owner maps for public and retained internal equilibrium paths;
- a preservation manifest classifying each owner as preserve directly,
  preserve concept/rewrite owner, validation-only, or retire;
- fresh source/native identity for runtime characterization;
- focused behavior receipts for valuable current paths.

Guard: characterize only behavior worth preserving; do not freeze a known
incorrect paper result or failed scientific conclusion as the desired output.
The durable manifest records stable responsibility and evidence invariants;
exact filenames and transient caller locations are checkpoint evidence, not a
permanent production-coupling contract.

Proof: ownership-map tests, source-manifest checks, fresh equilibrium build,
focused API/native contracts, and exact before/after receipt schema.

Exit: no substantial owner can be moved or deleted without a recorded caller,
role, evidence level, and migration decision.

### Stage 4: Stabilize the provider-to-equilibrium input contract

Entry: Stage 3 identifies every equilibrium-side model serializer and default.

Deliverables:

- required versioned model configuration;
- provider-owned immutable native model definition;
- state-time resolution of temperature/composition correlations;
- one resolved input handle and detached receipt consumed by equilibrium;
- removal of displaced equilibrium-side serialization and defaults.

Guard: missing scientific parameters remain errors. Task 9 concepts are
selected by contract and tests, not merged wholesale.

Proof: provider configuration receipt, derivative/package tests, equilibrium
consumer tests, unknown/conflicting-key rejection, and absence tests for old
serializers.

Exit: equilibrium cannot reinterpret provider model configuration.

### Stage 5: Extract the minimal equilibrium kernel

Entry: provider input contract is stable and Stage 3 characterization is
accepted.

Deliverables:

- canonical `PhaseEvaluator`;
- one `LocalNlpProblem` contract and Ipopt adapter;
- typed transforms and problem specifications;
- native-owned certification and typed results;
- removal of duplicated policy, solver, and conversion owners.

Guard: each extraction deletes an old owner in the same checkpoint. File
splitting without concept deletion does not count.

Proof: exact schema, activation, ownership, attempt-count, and status parity;
predeclared tolerance-based numerical parity for state variables, objectives,
and residuals; phase-permutation-aware topology equivalence; duplicate-owner
rejection; focused native tests; and lowered structural ratchets.

Exit: all admitted local solves use one kernel and one attempt/Ipopt policy
owner and schema. Typed route-specific values remain allowed when justified by
the route contract; duplicate policy owners and ad hoc route branches do not.

### Stage 6: Consolidate public-green equilibrium routes

Entry: Stage 5 kernel is active.

Deliverables:

- bubble pressure, dew pressure, and scoped pure saturation use one typed
  saturation route owner;
- paper identity is removed from the numerical kernel;
- activation and evidence scopes remain unchanged;
- duplicate Python/native dispatch is deleted.

Guard: no route or component-domain expansion.

Proof: public API tests, equilibrium confidence, exact route/status schemas,
tolerance-based numerical route parity, retained NIST/Gross evidence checks
selected by current capability dependencies, and rejection of unsupported
inputs.

Exit: the current public equilibrium surface is small, coherent, and suitable
for curated migration.

### Stage 7: Rebuild neutral fixed-state equilibrium and Pereira HELD

Entry: the public-green kernel is stable and neutral admission remains closed.

Deliverables:

- canonical fixed-phase-set free-energy NLP;
- independent TPD problem;
- Stage I multistart stability contract;
- Stage II upper LP and nonconvex lower problem with cuts and bound history;
- Stage III free-energy refinement, feedback, trace handling, and postsolve;
- removal or renaming of misleading sampled-dual status fields.

Guard: deterministic screening remains seed evidence. No global guarantee is
claimed from finite starts or sampled candidates.

Proof: analytic toy free-energy surfaces with known minima, independent LP
oracle tests, two- and three-phase material-balance fixtures, adversarial
metastable seeds, Stage II/III feedback tests, and source-backed scoped cases.

Exit: the controller demonstrably executes the Pereira stage structure. Route
admission remains a separate decision.

### Stage 8: Extend the neutral controller to association

Entry: neutral HELD parity and exact implicit-association derivatives pass.

Deliverables:

- one neutral controller operating on associating and nonassociating phase
  evaluators;
- retained association derivative and mass-action certification;
- paper parameters remain data, not dispatch branches;
- associating LLE/VLLE admission remains separately scoped.

Guard: Gross reproduction does not establish generalized associating phase
discovery by itself.

Proof: association derivative tests, nonassociating parity, Gross source joins,
mass-action/postsolve checks, and phase-discovery tests independent of paper
fingerprints.

Exit: association is a thermodynamic formulation extension, not a second
solver architecture.

### Stage 9: Resolve and implement electrolyte architecture

Entry: provider electrolyte state resolution is stable and neutral HELD
controller boundaries are proven.

Deliverables:

- equation-level decision between Perdomo modified-mole HELD2 and any retained
  Ascani counterion-pair path;
- source-faithful HELD2 coordinates and controller when selected;
- explicit separate naming for an Ascani equation-solving alternative;
- trace-ion and phase-electroneutral postsolve handling;
- no public admission until independent algorithm and model gates pass.

Guard: do not claim coordinate equivalence without a derivation. Do not make
incomplete Khudaida bundles executable with invented values or disabled
physics.

Proof: coordinate round trips, charge conservation, exact derivatives,
trace-ion asymptotic tests within the electrolyte topology, separately owned
neutral-controller parity, Stage I/II/III tests, trace-ion cases, Perdomo
algorithm benchmarks, and separate M6 ePC-SAFT reproductions. An exact
zero-electrolyte topology-transition test is required only if the child design
derives and implements that transition.

Exit: algorithm identity, coordinate identity, and model validity are
independently established.

### Stage 10: Complete standalone CE before simultaneous CPE

Entry: provider resolved inputs and homogeneous CE source conventions are
stable.

Deliverables:

- conservation, standard-state, equilibrium-constant, and reaction-affinity
  contracts;
- repaired or explicitly rejected nonideal CE evidence;
- public CE only after its own gate;
- separate source-faithful simultaneous CPE design;
- reactive electrolyte work remains later unless independently specified.

Guard: sequential speciation plus flash is not simultaneous CPE.

Proof: independent ideal/convex oracles, conservation rank and feasibility,
reaction stationarity, nonideal source-qualified cases, and coupled
phase/reaction residual tests when CPE is implemented.

Exit: CE is independently trustworthy before CPE consumes it.

### Stage 11: Transfer the proven skeleton into a curated repository

Entry: Stages 1-6 are stable; later algorithm stages may migrate only after
their own exit gates.

Deliverables:

- new repository bootstrap and ownership policy;
- provider core and resolved-input SDK;
- minimal equilibrium kernel and public-green routes;
- required literature inputs and validation harnesses;
- provenance map from every transferred owner to its source commit and proof;
- no historical compatibility layer copied solely to preserve old structure.

Guard: the old repository remains the reference archive until parity is
accepted. Copying a large owner requires a preservation decision and a lower
complexity target.

Proof: clean builds, package isolation, provider/equilibrium API parity,
source/native identity, artifact install tests, focused literature checks, and
line/owner metrics.

Exit: the curated repository provides the same admitted capability with fewer
owners and a reproducible Linux build.

### Stage 12: Retire superseded paths and close the program

Entry: every migrated or simplified slice has an accepted receipt.

Deliverables:

- removal of obsolete bindings, NLPs, serializers, dispatchers, and plans;
- archived rather than silently rewritten historical records;
- final capability and limitation table;
- clean branches, intentional stashes, clean worktrees, and no unowned
  generated artifacts;
- durable handoff and release decision.

Guard: no source or evidence is deleted solely because it failed validation.
Failed evidence remains available when it explains a closed capability.

Proof: fresh builds, confidence suites, isolated installs, selected M6 proof,
docs, Ruff, diff checks, cleanup, independent scientific/code review, and Git
state audit.

Exit: the old implementation is either retained as an explicit archive or
retired by user-approved repository policy; the curated repository is the
development source of truth only after that decision.

## Execution DAG And Optional Advanced Branches

The stage numbers group responsibilities; this dependency graph controls
execution:

```text
1 -> 2 -> 3 -> 4 -> 5 -> 6 -> 11 core migration -> 12 core closeout
                              |
                              +-> 7 neutral HELD
                              |     +-> 8 association
                              |     +-> 9 electrolyte HELD2
                              +-> 10 standalone CE -> later CPE
```

Stage 11 is one bounded core-migration checkpoint after Stage 6. It creates the
curated repository and transfers the provider, resolved-input boundary,
minimal equilibrium kernel, and public-green routes, then closes. Stages 7-10
are advanced capability branches executed as separate work in the curated
repository, using the old repository only as source/reference evidence.

Stage 12 may close the core migration while Stages 7-10 remain intentionally
deferred, provided their routes remain closed and their source documents,
preservation records, and child-plan requirements remain durable. If an
advanced branch has been accepted before Stage 12, its receipt is included in
closeout; incomplete advanced branches do not block retiring duplicated core
paths.

## Proportional Verification Policy

Each stage runs three layers, not every possible test:

1. **Slice proof:** exact tests for the owner or doctrine changed.
2. **Boundary proof:** provider/equilibrium contracts and one representative
   runtime path when native code changes.
3. **Stage proof:** package confidence, docs, diff, cleanup, and independent
   review at the stage checkpoint.

Full paper campaigns, wheel matrices, and full repository collection run only
when the stage changes their owner, makes an admission claim, prepares a
release, or closes the program.

## Stop Rules

Stop the active slice when:

- governing equations or source identity are unresolved;
- the loaded native module does not match current source;
- a change requires a second live owner or compatibility path;
- public activation changes outside a dedicated admission stage;
- model inputs are missing or out of domain;
- exact schema/status or tolerance-based numerical behavior differs without an
  approved correctness change;
- a paper-specific repair expands the core architecture scope;
- a stage would need cross-milestone implementation not named by its plan;
- verification cannot distinguish algorithm behavior from stale artifacts.

## Decision Ledger

| Decision | Resolution | Reason |
| --- | --- | --- |
| Preserve or rewrite equilibrium | Preserve proven components; rewrite owners selectively | Exact derivative and local-NLP work is valuable, while orchestration is overgrown |
| One NLP or one NLP interface | One interface, multiple typed mathematical problems | HELD contains distinct stability, LP, lower-NLP, and refinement problems |
| Canonical Stage III | Direct free-energy minimization | Source-faithful Pereira/Perdomo formulation |
| Residual solve role | Optional corrector/diagnostic | Useful local tool but not HELD Stage III identity |
| HELD2 coordinates | Perdomo modified-mole path for HELD2 | Source-defined transformation |
| Counterion-pair path | Separate Ascani formulation until equivalence is proven | Prevents algorithm-name conflation |
| Bubble/dew relation to HELD | Shared kernels, independent boundary route | Current public routes do not execute HELD discovery |
| Paper evidence ownership | M6 | Separates model reproduction from M4 algorithm parity |
| Provider input prerequisite | Complete before equilibrium cutover | Prevents equilibrium from duplicating state/configuration semantics |
| Curated repository timing | Begin skeleton after public-green kernel is stable | Avoids copying unresolved bloat while retaining proven work |
| Verification breadth | Risk-based and stage-owned | Prevents proof theater and repeated expensive unrelated campaigns |
| Historical plans | Archive/supersede, do not silently rewrite | Preserves traceability without treating outdated claims as current truth |

## Completion Standard

This specification is complete when the twelve stages have durable stage-owned
plans, their dependency order is represented in the tracker, and future agents
can identify the governing source, owner, focused test, stop rule, and exit
receipt for any selected stage without reconstructing this thread.
