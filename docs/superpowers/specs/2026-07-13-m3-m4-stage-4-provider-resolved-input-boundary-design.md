# Stage 4 Provider Resolved-Input Boundary

Milestones: `M3 - EOS` and `M4 - Equilibrium`, with one contract-only
`M5 - Regression` integration leaf
Packages: `packages/epcsaft`, `packages/epcsaft-equilibrium`, and the bounded
consumer seam in `packages/epcsaft-regression`
Status: `approved child design; implementation plan not yet approved`
Date: `2026-07-13`
Parent program:
`2026-07-12-m4-equilibrium-source-faithful-recovery-and-curated-migration.md`

## Context

Stage 3 recorded the current provider-model intake as an equilibrium-owned
47-field reconstruction path. Current `main` still has four overlapping
model-input compilers:

1. provider parameter runtime-dictionary generation;
2. provider `Mixture` payload generation;
3. provider Python-to-native argument construction; and
4. equilibrium reconstruction of those native arguments from Python objects or
   mappings.

The provider also permits missing model configuration, supplies scientific
formulation defaults, can evaluate state-dependent records before the actual
state exists, and exposes mutable native arguments. The equilibrium public
path reaches the static mixture-native object independently during configure,
structure, and solve. Regression imports the same provider serializer that
this stage must delete.

The paused Task 9 implementation contains useful typed records, correlation
forms, native resolved-input concepts, and contract tests. It is not an
integration candidate: it mixes provider, equilibrium, regression, paper, and
validation changes across 288 files; admits a nonempty initial preset catalog;
retains condition-free native mixture access; and does not return the accepted
immutable evaluated-input object.

This child design tightens the approved July 10 M3 resolved-input design and
M4 consumer plan using the Stage 3 inventory. It does not replace either
document. Where the older M4 plan assumes one known request composition is
sufficient for any future multiphase model, this design adds a narrow
scientific rejection gate.

## Authority And Integration Exception

The user selected Stage 4, approved replacement or removal of tests that encode
the retired input contract, and approved this design. Existing scientific
prediction and derivative tests remain preservation evidence.

During child-spec self-review, current source inspection verified that
`epcsaft-regression` imports and invokes the exact provider serializer that
Stage 4 deletes. The user therefore authorized one bounded M5 consumer leaf so
the deletion-first cutover can remain green on `main`. That leaf may change
only input-contract adaptation and its tests. It may not change regression
capability, target semantics, fitting algorithms, parameter bounds, numerical
policy, public admission, or retained evidence.

This exception does not authorize other cross-milestone work.

## Scientific Confidence

- **Verified:** the currently admitted equilibrium routes are
  `bubble_pressure`, `dew_pressure`, and scoped nonassociating
  methane/ethane/propane `single_component_vle`.
- **Verified:** bubble uses the normalized specified liquid composition, dew
  uses the normalized specified vapor composition, and scoped pure VLE uses
  the single-component composition.
- **Verified:** bubble and dew solve an unknown second-phase composition after
  request intake.
- **Verified:** the current admitted routes are neutral and do not require the
  composition-dependent electrolyte records retained in closed workflows.
- **Verified:** current provider EOS, CppAD, implicit-association, pressure,
  fugacity, density, and state-sensitivity tests provide continuity evidence.
- **Inference to prove:** a single evaluated snapshot is sufficient for the
  admitted public routes when every active scientific input is independent of
  the changing trial-phase composition.
- **Inference to prove:** current exact derivative APIs remain exact when a
  state-dependent scientific record is represented in an evaluated snapshot
  together with its required derivative evidence or a definition-backed
  automatic-differentiation evaluator.
- **Unknown and deferred:** the correct provider contract for a multiphase
  solve whose active scientific records must be re-evaluated at every trial
  phase composition.

No governing EOS equation, derivative backend, phase-equilibrium equation,
normalization convention, unit convention, or numerical tolerance changes in
this stage.

## Goals

1. Make model configuration required, complete, immutable, and versioned.
2. Keep scientific values, correlations, domains, provenance, and structural
   zeros in typed `ParameterSet` records without runtime policy.
3. Make `ResolvedModelInput` the only Python-to-native model compiler.
4. Evaluate supported state-dependent records at the actual state temperature
   and normalized ordered composition.
5. Return one immutable `EvaluatedModelInput` containing the exact read-only
   native snapshot handle and a detached deterministic receipt.
6. Make provider `State`, admitted equilibrium routes, and the bounded
   regression consumer use that provider-owned contract.
7. Delete displaced serializers, native mapping constructors, formulation
   defaults, and equilibrium reconstruction in the same cutover series.
8. Preserve public capability state and existing scientific/numerical behavior.

## Non-Goals

- No public equilibrium or regression capability expansion.
- No HELD, HELD2, chemical-equilibrium, electrolyte, association, paper, or
  validation-campaign repair.
- No per-trial-phase composition evaluator for closed multiphase models.
- No governing EOS, density, fugacity, association, Born, ion, or derivative
  equation change.
- No solver-option, attempt-policy, tolerance, target, bound, or fitting-policy
  change.
- No compatibility wrapper, deprecated alias, fallback mapping, guessed
  parameter, provisional preset, or default configuration.
- No wholesale merge or cherry-pick of the paused Task 9 implementation.
- No requirement to keep a paper caller executable when its scientific inputs
  do not satisfy the new contract; Stage 3 preservation decisions still govern
  the underlying native mathematics and component proof.

## Alternatives

### Add an equilibrium adapter before the provider contract exists

Rejected. It would create a fifth serializer and allow equilibrium to retain
provider configuration policy.

### Merge the paused Task 9 branch

Rejected. Its useful records and tests are selected individually under this
design; its cross-milestone scope, nonempty preset catalog, retained native
escape path, and incomplete evaluated-input contract are not accepted.

### Cut provider and equilibrium while leaving regression on the old serializer

Rejected. The provider serializer is shared production code. Keeping it for
regression would fail the one-owner and absence gates; deleting it without a
consumer leaf would break the repository.

### Build a dynamic per-trial-phase evaluator now

Deferred. It could support future composition-dependent multiphase models, but
it would broaden the native contract and proof surface beyond the admitted
neutral routes. Its thermodynamic semantics belong to the stage that owns that
capability.

### Coordinated deletion-first cutover

Selected. Prepare bounded M3 provider checkpoints, then separate M4 and minimal
M5 consumer checkpoints, delete every displaced input owner on the integration
stack, integrate only the verified combined revision, and stop before Stage 5.

## Selected Provider Contract

### Required configuration

`ModelOptions` remains the public domain name. Direct construction is closed;
`ModelOptions.from_user_options(...)` is the sole public parser for
`epcsaft.model-configuration` schema version `1`.

The parser accepts exactly one of:

1. an immutable admitted preset identifier and version; or
2. a complete explicit formulation with
   `selection_origin="explicit_configuration"`.

The initial preset catalog is empty. An explicit neutral configuration states
that electrostatics, relative permittivity, Debye-Huckel, Born, solvated-ion
diameter, and ion-dispersion formulations are disabled. An enabled formulation
requires every selected field. Disabled formulations reject active-only
fields.

The canonical folder file is `model_configuration.json`. Missing
configuration, retired option filenames, duplicate JSON keys, unknown keys,
loose booleans, partial formulations, conflicting preset/explicit selection,
unsupported schema versions, and preset selection against the empty catalog
raise `InputError` before parameter resolution.

Global capabilities report supported configuration schema versions and the
empty preset list. They never report an instance's active formulation.

### Scientific records

`ParameterSet` schema version `3` owns only immutable, source-bearing
scientific definitions. Records include units, component identities, source
identity, structural-zero evidence, and required temperature/composition
domains. Every record also has a fail-closed dependency signature naming each
independent variable used by its value or derivative evaluation. Unknown
dependency identity is invalid. Only typed, locally sourced correlation
families are admitted. Free-form expression evaluation is not.

`ParameterSet` does not own formulation selection, runtime options, state
temperature, state composition, association-topology inference, or native
serialization. Dataset and source-bundle loading preserves correlation
definitions until state evaluation. A loader cannot substitute a nominal
temperature or equal composition.

Validity domains and dependency signatures are separate. A domain states where
a record is supported; it does not prove which state variables affect the
record. Provider receipts identify the dependency signature and record IDs for
every active definition. M4 and M5 consume that provider classification and do
not reproduce it from arrays, correlation type names, or values.

### Definition and evaluation objects

The Python boundary is:

```python
ResolvedModelInput.resolve(
    parameters,
    model_options,
    components=component_order,
) -> ResolvedModelInput

ResolvedModelInput.configuration_receipt -> detached mapping

ResolvedModelInput.evaluate(
    temperature=temperature_K,
    composition=ordered_mole_fraction,
) -> EvaluatedModelInput

EvaluatedModelInput.native_handle
EvaluatedModelInput.receipt
EvaluatedModelInput.snapshot_fingerprint_sha256
```

`ResolvedModelInput` is frozen and owns component order, the typed native
definition graph, structural-zero evidence, the public-to-native mapping, and
the definition fingerprint. It cannot be constructed from a raw mapping.

`EvaluatedModelInput` is frozen and is not a mapping. Its `native_handle` is the
exact version-1 `NativeEvaluatedInputSnapshot` consumed by native code. Its
receipt access returns a detached copy, and its fingerprint is derived from
canonical schema/version, definition identity, component order, temperature,
composition basis, normalized composition, evaluated records, structural
zeros, formulation, and native-field mapping.

The snapshot and receipt expose provider-owned, read-only identity fields for
schema ID/version, component order, temperature, canonical composition,
definition fingerprint, and snapshot fingerprint. They also expose:

- each evaluated record's dependency signature;
- affected record IDs grouped by independent variable;
- `trial_phase_composition_invariant`, which is true only when no input record
  depends on a route-varying partner-phase composition or other solve-varying
  state input; and
- active residual-family, ionic-component, association-topology, structural-
  zero, and scientific-source classifications.

Unknown dependency classification makes
`trial_phase_composition_invariant` false. This flag concerns scientific input
records, not the ordinary dependence of the EOS, mixing rules, association
equations, or their derivatives on the live trial-phase composition.

Equivalent canonical inputs produce byte-stable canonical receipt JSON and the
same SHA-256 fingerprint. Mutating a returned receipt cannot change the handle,
later calculations, or later receipt access.

### Native ownership

The provider native graph contains a condition-independent
`ResolvedNativeInput` definition and an immutable version-1
`NativeEvaluatedInputSnapshot`. Every current model field must be accounted for
by one of:

- an evaluated snapshot field with record and native-consumer evidence; or
- deletion of the displaced native consumer in the same checkpoint.

The snapshot carries exact typed formulation values and explicit disabled
sentinels. Native bindings expose read-only properties only. Raw mappings,
`ParameterSet`, mutable native-argument records, and payload constructors cannot
construct provider state.

The cross-extension carrier is one provider-owned
`ProviderResolvedInputHandleV1`. It owns a
`std::shared_ptr<const NativeEvaluatedInputSnapshot>`. Python sees only
read-only identity properties. Provider, M4, and M5 native algorithms accept
the provider handle and take its canonical const snapshot view; none converts
the snapshot into the retired argument record or another fieldwise model
structure. The handle owns snapshot lifetime independently of transient
receipt dictionaries. The implementation plan's cross-extension RED probe
must prove this exact carrier works across the separately built modules before
native implementation proceeds.

Trial temperature, phase composition, density, and other EOS state variables
remain live native equation and CppAD variables. Snapshot evaluation cannot
silently turn a live equation variable into a constant. For every
state-dependent record used by an existing derivative API, the provider must
do one of the following:

1. retain definition-backed typed evaluation inside the exact scalar/AD graph;
2. carry the evaluated derivatives through the highest order required by the
   existing API and assemble every chain-rule term; or
3. reject that record/route combination before native evaluation.

This rule applies to temperature and composition derivatives, implicit
association sensitivities, and any second-order callback that consumes the
record. Provider EOS and derivative code reads only the canonical snapshot
view plus live equation variables. This is a representation cutover, not
permission to rewrite equations or drop correlation derivative terms.

## State Flow

`Mixture` requires explicit `ModelOptions`, creates one
`ResolvedModelInput`, and exposes its detached configuration receipt. It has no
condition-free public native escape path.

`State` validates positive finite temperature, exact component count, finite
nonnegative mole fractions, and normalization. It evaluates the mixture graph
once at those conditions, retains the `EvaluatedModelInput`, and constructs
native state from its handle. The native state fingerprint must match the
evaluated snapshot fingerprint. `State.configuration_receipt` returns the
detached state receipt.

Public `State` uses one provider-owned canonicalizer before evaluation.
`ResolvedModelInput.evaluate(...)` validates the already canonical vector but
does not renormalize, floor, clip, or reorder it. The exact vector passed to the
evaluator is the vector recorded in the receipt and fingerprint.

## Equilibrium Consumer Contract

The public flow is:

```text
route request
  -> validate route, temperature, and specified composition
  -> normalize and validate the route-owned composition once
  -> evaluate the provider definition once
  -> retain one EvaluatedModelInput
  -> configure, structure, and solve with the same native handle
  -> attach detached provider receipt identity to result evidence
```

Bubble pressure evaluates at its specified liquid composition, dew pressure at
its specified vapor composition, and scoped pure VLE at the single-component
composition. Configure, structure, repeated structure queries, solve, and
repeated solve calls must retain the same object and fingerprint identity.

M4 remains the sole canonicalizer for an equilibrium route composition. It
preserves the existing order: validate shape/finiteness/nonnegativity, divide
once by the positive sum, then enforce the existing minimum-composition check.
M3 validates this canonical vector without a second normalization. Condition
mismatch uses the existing input-validation tolerance; Stage 4 does not add or
change a tolerance.

Before native dispatch, M4 rejects a missing handle, unsupported schema or
version, component-order mismatch, temperature mismatch, specified-composition
mismatch, receipt/handle fingerprint mismatch, or an active record whose value
would need re-evaluation at the unknown trial-phase composition. M4 never
freezes such a value at the feed or known-phase composition.

The composition-dependency gate reads only the provider-owned
`trial_phase_composition_invariant` field and its affected record IDs. It fails
closed on missing or unknown classification. It does not reject ordinary EOS
or association dependence on the live phase composition, which remains inside
the native exact equation graph.

All retained equilibrium native entrypoints that currently use the shared
model converter must accept the typed provider handle. No mapping, `_native`
recursion, native-mixture cast, 47-field copy, or default remains. Closed
capability status does not change merely because an internal intake signature
changes.

Equilibrium may consume the stable provider fields for active residual
families, ionic-component status, association activity/topology fingerprint,
scientific source IDs, structural-zero IDs, and input dependency identity. It
may not infer those facts from provider arrays or insert fallback values.
Paper-proof identity remains M6/M4 evidence and is not invented as a provider
classification; a paper-specific binding that cannot use generic source IDs is
left closed and its failure evidence remains durable.

The selector request schema, standalone chemical-equilibrium schema, numerical
solver controls, certification tolerances, activation descriptor, and result
acceptance remain M4-owned and separate from provider model input.

### Binding disposition gate

Before changing the shared converter, the implementation plan refreshes the
Stage 3 binding inventory and assigns every affected intake one of the
following exact dispositions:

| Converter caller | Stage 4 disposition |
| --- | --- |
| `_native_equilibrium_activation_plan_contract`, `_native_equilibrium_selector_contract`, `_native_equilibrium_selector_route_result` | Migrate to the retained public request's one handle; enforce dependency invariance before selector/NLP dispatch. |
| `_native_activated_neutral_tp_flash_nlp_contract`, `_native_equilibrium_cloud_shadow_route_result`, `_native_eos_phase_system`, `_native_phase_equilibrium_residual_block_contract`, `_native_neutral_two_phase_eos_nlp_contract`, `_native_neutral_multiphase_eos_nlp_contract`, `_native_neutral_two_phase_eos_postsolve`, `_native_neutral_multiphase_eos_postsolve`, `_native_neutral_multiphase_fugacity_residual_route_result`, `_native_neutral_tpd_phase_discovery` | Preserve the characterized neutral components and migrate to the const handle; reject a handle whose provider dependency classification is not invariant for every route-varying phase input. |
| `_native_associating_single_component_vle_validation_result`, `_native_eos_phase_block`, `_native_saturation_block`, `_native_electrolyte_contribution_block` | Preserve component mathematics and migrate to a handle evaluated at the exact explicit block temperature/composition; keep public exposure unchanged. |
| Optional EOS activity inside `_native_chemical_equilibrium_nlp_activation` | Accept a handle only when the standard-state record supplies the exact T/composition required for evaluation; otherwise reject before NLP while preserving generic CE component proof. |
| `_native_electrolyte_bubble_t_reduced_nlp_probe`, `_native_electrolyte_bubble_t_route_result`, `_native_electrolyte_tpd_phase_discovery`, `_native_electrolyte_held2_continuous_tpd_minimizer`, `_native_electrolyte_held2_phase_discovery`, `_native_electrolyte_stage_iii_refinement`, `_native_electrolyte_postsolve_certification` | Preserve separately classified electrolyte coordinates, local NLPs, derivatives, and postsolve mathematics; migrate the intake to the const handle and fail closed unless dependency metadata proves all route-varying input use is valid. This signature migration does not validate HELD/HELD2 identity or repair failed paper evidence. |

No `preserve_directly` item in the Stage 3 manifest may become unavailable in
Stage 4. A `preserve_concept_rewrite_owner` item retains its native mathematics
and focused proof; Stage 4 changes only model intake. Only an item already
classified `retire` may be removed, and only under its recorded migration
guard. The implementation plan records the refreshed caller and proof path for
every row before the provider hard cutover.

### Receipt and capability delta

`Equilibrium.provider_input_receipt` returns the full detached provider receipt.
The native result diagnostics add exactly one immutable
`provider_input_identity` record containing contract ID, schema/version,
definition fingerprint, snapshot fingerprint, component order, temperature,
canonical composition basis/vector, and
`trial_phase_composition_invariant`. Structure and solve must echo the same
identity. Python does not rebuild this record from optional fields.

The allowed capability delta is limited to nested provider contract/schema
discovery required by the new SDK. Equilibrium activation rows, public route
names/count, development-family status, solver/optimizer claims, derivative
claims, and proof/admission state remain byte-equivalent. Regression capability
rows remain byte-equivalent.

## Bounded Regression Consumer Leaf

The M5 leaf replaces imports and calls to provider runtime dictionaries,
association mutation, and native argument construction with the accepted
provider resolved-input contract. It may add a contract test proving the
provider handle is consumed with matching schema/version, component order,
conditions, and fingerprint.

Regression-specific fitted-parameter mutation cannot be hidden inside an
immutable state snapshot. If the current regression architecture requires a
new fitted-input compiler or target semantics, the leaf stops and reports that
M5 design blocker. It does not add a mutable snapshot, restore the serializer,
or redesign regression under Stage 4 authority.

The leaf must prove unchanged capability rows, public targets, bounds,
residual definitions, optimizer selection, derivative policy, and numerical
acceptance. Any change beyond mechanical intake adaptation requires a
separately approved M5 design.

Before any incompatible provider cutover or serializer deletion, a RED/GREEN
M5 feasibility gate proves that every currently supported fitted-parameter
iteration can use an immutable provider baseline plus an already approved
typed fitted-parameter overlay without rebuilding a provider mapping. Current
source mutates pure, association, electrolyte, and interaction fields during
native Ceres evaluation, so this is not presumed mechanical. If the proof
requires a new overlay/compiler design, Stage 4 stops incomplete and requests
that separate M5 approval before deletion. A recorded blocker is not a Stage 4
success path.

## Displaced Paths

After their final callers move, the cutover deletes or removes the production
responsibility of:

- `ParameterSet.runtime_options` and runtime-dictionary emission;
- dataset option defaults and early state-condition evaluation;
- provider mixture payload generation;
- Python association-topology inference used for native construction;
- provider Python-to-mutable-native argument construction;
- the condition-free `Mixture.native` escape path;
- writable native model-argument bindings and payload snapshots;
- equilibrium field-by-field provider reconstruction and object fallbacks;
- equilibrium raw-array/default-based provider classification; and
- regression imports and calls to the deleted provider serializer.

No forwarding function, deprecated alias, test-only production fallback, or
compatibility module replaces these paths.

## Error Handling And Stop Gates

- Missing scientific parameters, correlation domains, provenance, structural
  zero evidence, or active formulation fields remain errors.
- Unknown, duplicate, conflicting, nonfinite, out-of-domain, unit-inconsistent,
  or component-order-inconsistent input fails before EOS evaluation.
- Provider/consumer SDK mismatch reports both contract identities before
  selector or regression dispatch.
- A composition-dependent multiphase input unsupported by this design fails
  before NLP construction.
- Numerical or derivative drift stops the current representation cutover; it
  is not tuned away.
- A second serializer, compatibility period in accepted production code, or
  writable evaluated handle stops the stage.
- A paper-specific missing input or failed reproduction is recorded for its M6
  owner and is not repaired here.
- A regression change beyond contract adaptation stops the M5 leaf and Stage 4
  integration.
- An M5 feasibility blocker stops Stage 4 before the incompatible provider
  cutover is integrated; recording the blocker does not satisfy acceptance.
- The stage does not complete until all three packages build and their focused
  consumer proofs pass on one source revision.

## Testing And Proof

### RED-first contract slices

1. Configuration parser mutation tests cover missing configuration, direct
   construction, schema/version types, duplicate keys, unknown nested keys,
   strict booleans, conflicting selection, retired files, incomplete enabled
   formulations, inactive extra fields, and empty-catalog preset rejection.
2. Parameter/correlation tests cover units, provenance, domains, boundaries,
   component order, structural zeros, and absence of loader-time evaluation.
3. Native tests cover immutable construction, complete old-field accounting,
   evaluated values, snapshot fingerprints, read-only bindings, and raw-map
   rejection.
4. Receipt tests cover determinism, detached access, definition/state identity,
   and sensitivity to one mutation in each scientific input family.
5. Provider frontend tests cover explicit `Mixture`, exact `State` evaluation,
   fingerprint identity, and absence of bypass paths.
6. Equilibrium integration tests cover one evaluation, exact route conditions,
   shared configure/structure/solve identity, mismatch rejection before
   dispatch, unsupported composition-dependent multiphase rejection, and
   unchanged public activation.
7. Regression integration tests cover typed-handle intake and prove unchanged
   capability, target, bound, optimizer, derivative, and acceptance contracts.
8. Installed and source-CMake integration tests pass the exact provider handle
   into the separately built M4 and M5 extensions, assert contract, component,
   condition, and fingerprint identity, retain the handle across native calls,
   and fail if either consumer converts through a Python mapping.

Tests that encode the displaced serialization/default contract may be updated
or removed. Existing scientific prediction, equation, derivative, and
activation tests remain. New tests in this stage are input-contract mutation
or identity tests and do not compute new literature/model predictions, so they
do not require a new retained plot.

### Scientific and numerical continuity

Before native representation changes, record a fresh provider/equilibrium
source identity and focused baseline receipts for one fully sourced neutral
case, one associating case, and one fully sourced electrolyte case already
owned by provider tests. After each native cutover, compare existing property,
pressure, density, fugacity, CppAD, implicit-association, Born, and state
sensitivity results at their existing declared tolerances. Do not introduce a
new tolerance.

Correlation-sensitive derivative oracles additionally cover every admitted
nonconstant record family through the derivative order consumed by existing
provider and equilibrium APIs. They prove value and chain-rule parity while
trial composition/density remain live variables; point-value parity alone is
insufficient.

Public bubble, dew, and scoped pure VLE characterization must retain route,
request, activation, attempt-count/status, result-schema, and existing
numerical parity. Phase topology comparison permits only already documented
phase permutation equivalence.

### Structural proof

Absence tests prove there is one configuration parser, one resolved compiler,
one evaluated snapshot constructor, and no old serializer, mutable native
argument binding, equilibrium reconstruction, recursive object fallback, or
regression import of the retired serializer.

Provider SDK manifests and both extension build graphs must consume the same
provider source identity. Global capabilities remain schema discovery only;
equilibrium and regression capability snapshots remain unchanged.

### Proportional verification

Each checkpoint runs its focused RED/GREEN tests, relevant Ruff checks, diff
check, and cleanup audit. Native checkpoints use a fresh provider or
equilibrium build as appropriate. Stage closeout additionally runs provider
confidence, focused equilibrium public-route and consumer contracts, the
bounded regression consumer proof, package-boundary/source-manifest tests,
strict docs, and independent code/scientific review.

Unrelated paper-validation failures are reported by owner and do not justify a
default or compatibility path.

## Checkpoint Sequence

1. M3 strict configuration records, dependency metadata, empty catalog, and
   additive contract tests.
2. M3 schema-3 scientific records and source loading without state evaluation.
3. M3 immutable native definition, evaluated snapshot, const handle, and
   cross-extension RED probe.
4. M3 Python resolved owner and deterministic receipts.
5. Pre-cutover M4 binding-disposition proof and M5 immutable-baseline/fitted-
   iteration feasibility proof.
6. On an integration stack, prepare the incompatible M3 provider
   frontend/native cutover and displaced-path deletion; do not integrate it to
   `main` alone.
7. On that stack, prepare the M4 admitted-route consumer cutover and
   equilibrium reconstruction deletion.
8. On that stack, prepare the contract-only M5 consumer leaf. If Step 5 proved
   a new M5 design is required, stop Stage 4 incomplete before Steps 6-8.
9. Verify the combined M3+M4+M5 revision, then integrate the incompatible
   cutover and its consumers as one ordered green sequence with separate
   owner commits.
10. Run derivative, package, SDK, documentation, absence, and independent
    reviews; record the Stage 4 receipt and stop before Stage 5.

M3 and M4 changes do not share one cross-owner commit. The M5 leaf is also a
separate checkpoint. Additive preparation may land only while it is green and
does not establish a second production owner. Incompatible configuration,
native-constructor, serializer-deletion, M4, and M5 commits remain on the
integration stack until the combined revision is green. No accepted checkpoint
leaves `main` broken; exact integration order and commit boundaries are fixed
by the implementation plan after this specification is approved.

## Acceptance

Stage 4 is complete only when:

- model configuration is explicit, schema-versioned, and default-free;
- the initial preset catalog is empty;
- `ParameterSet` carries definitions rather than runtime policy;
- state-dependent records resolve at actual admitted state conditions;
- provider State, admitted M4 routes, and the bounded M5 seam consume the
  immutable evaluated-input contract;
- configure, structure, and solve share one provider handle and receipt;
- unsupported composition-dependent multiphase input fails before dispatch;
- every displaced serializer/default/fallback is absent;
- provider equations and exact derivatives retain focused parity;
- public equilibrium and regression capability state is unchanged;
- provider, equilibrium, and regression focused builds/tests pass on one source
  revision; and
- the stage receipt records source/native identity, commits, proof commands,
  review outcome, deferred paper blockers, and no push.

## Decision Ledger

| Decision | Evidence | Resolution | Owner |
| --- | --- | --- | --- |
| Configuration policy | Current defaults and early option normalization | Require schema version 1 with no implicit construction | M3 |
| Initial presets | Approved M3 execution selection | Empty catalog | M3 |
| Scientific records | State-dependent values currently resolve before State | Preserve typed definitions and resolve at actual T/x | M3 |
| Native owner | Four current compilers and mutable native arguments | One definition graph and immutable evaluated snapshot | M3 |
| Equilibrium intake | M4 reconstructs 47 provider fields and follows private fallbacks | Consume one provider handle directly and delete reconstruction | M4 |
| Public multiphase composition | Bubble/dew vary an unknown second phase | Admit only inputs independent of that changing composition; reject others | M3/M4 |
| Dependency identity | Domains do not identify independent variables | Provider records and receipts carry fail-closed dependency signatures | M3 |
| Derivative continuity | Pre-evaluated records can lose chain-rule terms | Keep definition-backed AD, carry required derivatives, or reject | M3 |
| Closed routes | Stage 3 requires valuable component preservation | Migrate intake under a manifest disposition gate; no fallback or implicit retirement | M4 |
| Regression dependency | M5 imports the provider serializer selected for deletion | User-authorized contract-only M5 leaf | M5 |
| Regression fitted iteration | Current Ceres paths mutate model fields | Prove immutable-baseline adaptation before deletion or stop for an M5 design | M5 |
| Test preservation | User authorized displaced-contract test replacement | Preserve scientific tests; replace only retired-contract assertions | M3/M4/M5 |
| Task 9 reuse | Broad branch contains useful records and tests plus unaccepted architecture | Select concepts/tests by contract; do not merge wholesale | M3 |
