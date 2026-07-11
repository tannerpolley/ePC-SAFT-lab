# M3 Versioned State-Resolved Model Input

Milestone: `M3 - EOS`
Package: `packages/epcsaft`
Issue: `https://github.com/ePC-SAFT/ePC-SAFT/issues/439` (`M3: establish versioned state-resolved model input`)
Status: `approved; tracker published`
Last reviewed: `2026-07-10`

## Context

This spec replaces Task 9 of the repository-wide program defined by:

- [2026-07-09 program spec](2026-07-09-m3-core-repository-truth-and-scientific-integrity-program.md)
- [2026-07-09 implementation plan](../plans/2026-07-09-m3-core-repository-truth-and-scientific-integrity-program-plan.md)

The repository is a private, single-user scientific workspace. The purpose of
this change is therefore reproducible local calculation and debugging: the
same parameter records, model choices, temperature, and composition must
produce the same native input and an inspectable receipt. This spec does not
create a release or marketing claim.

ADR 0002 assigns formulation choices to public `ModelOptions`, parameter data
to `ParameterSet`, and thermodynamic conditions to `State`. ADR 0005 assigns
the resolved provider contract to `epcsaft` and makes the equilibrium and
regression packages consumers of that contract.

## Verified Current Behavior

The following observations were checked on `main` at `1fc4c819`:

- `ModelOptions` and `BornModelOptions` have generic zero-argument defaults,
  and `coerce_model_options(None)` constructs them.
- folder loading accepts `model_options.json`, falls back to
  `user_options.json`, and treats a folder containing neither as an empty
  configuration;
- `ParameterSet.runtime_options`, `ParameterSet.to_runtime_dict()`,
  `Mixture._runtime_payload`, and `state/native_payload.py` independently
  serialize overlapping parts of the model;
- `state/native_payload.py` inserts a complete electrolyte formulation when
  ionic parameters are present and fills nested option fields from defaults;
- temperature- or composition-dependent scientific values can be resolved
  before the state that supplies their actual conditions exists;
- the local `codex/task9-paused` experiment demonstrated useful design seams,
  but its 304-file change and downstream paper failures show that provider
  architecture, package-consumer migration, and paper-specific repair cannot
  be treated as one implementation slice.

Closed issues [#156](https://github.com/ePC-SAFT/ePC-SAFT/issues/156),
[#157](https://github.com/ePC-SAFT/ePC-SAFT/issues/157),
[#159](https://github.com/ePC-SAFT/ePC-SAFT/issues/159), and
[#160](https://github.com/ePC-SAFT/ePC-SAFT/issues/160) document the permissive
folder-loading/default behavior displaced by this design. Issue
[#158](https://github.com/ePC-SAFT/ePC-SAFT/issues/158) remains useful native
Born implementation history; it is not a duplicate of this work.

## Goals

- Require one versioned model configuration for every `Mixture`.
- Allow either an immutable, source-specific preset or a complete explicit
  formulation; do not merge partial configuration with hidden defaults.
- Keep scientific constants and correlations in `ParameterSet`, formulation
  choices in `ModelOptions`, and resolution conditions in `State`.
- Represent supported temperature- and composition-dependent inputs as typed,
  provenance-bearing records with explicit domains and units.
- Establish one frozen `ResolvedModelInput` graph as the only owner that maps
  provider inputs to native records.
- Evaluate that graph at each state temperature and composition and retain an
  exact detached receipt.
- Keep package capability output limited to supported configuration schema and
  preset identities; report the active selection only on an instance receipt.
- Split provider dataset storage/provenance, validation, and lookup policy as
  part of this owner cutover, absorbing the provider half of old Task 21.

## Non-Goals

- No repair of Khudaida, Gross 2002, or another paper's numerical results.
- No invention of missing pure, interaction, dielectric, Born, or solvation
  values so a bundle can execute.
- No public equilibrium-family expansion.
- No regression capability admission.
- No compatibility loader for `user_options.json`, loose runtime mappings, or
  `ParameterSet.to_runtime_dict()`.
- No promise that every historical parameter bundle qualifies for a preset.
- No requirement to preserve a public `Mixture.native` escape hatch; extension
  packages consume the provider-owned resolved-input contract instead.

## Alternatives Considered

### Keep defaults and add receipts afterward

This is the smallest code change, but the receipt would document values the
software inferred rather than choices the scientist supplied. It would not fix
condition-early correlation evaluation or duplicate serialization.

### Version only the JSON envelope

Adding a schema version while retaining runtime dictionaries would improve
file validation but leave multiple owners and payload-side defaults. Different
call paths could still produce different native inputs.

### Versioned definition plus one state-resolved native graph

This is the selected design. It is a larger provider change, but it aligns the
existing public ownership rules with the conditions required to evaluate
scientific correlations and gives extensions one exact provider seam.

## Selected Design

### Versioned `ModelOptions`

`ModelOptions` remains the public domain term required by ADR 0002. Public
construction crosses one strict parser and accepts exactly one of:

1. a preset identity and preset version from the provider-owned catalog; or
2. an explicit formulation containing every active and inactive formulation
   choice plus a stable selection origin such as `explicit_configuration`.

An explicit selection origin is not a literature citation. Scientific values,
correlations, and source-claimed presets still require scientific provenance.
Preset entries are immutable and do not accept overrides. Explicit neutral
configuration is allowed, but electrostatics and its dependent terms must be
explicitly inactive. Unknown keys, conflicting selections, loose booleans,
unsupported enum values, missing fields, and unsupported schema versions fail
before parameter resolution.

The canonical folder filename is `model_configuration.json`. A missing file or
the presence of a retired option filename is an error. The direct
zero-argument constructor is closed; strict factory or parser construction is
the public path.

### Typed scientific records

`ParameterSet` stores values, units, provenance, structural-zero policy, and
correlation definitions. It does not select a formulation and does not emit a
native payload. Initial correlation families include only locally sourced
forms needed by retained inputs, such as constant, reference-temperature
linear, logarithmic-temperature, and explicitly sourced exponential or
piecewise correlations.

Every nonconstant correlation records its valid temperature and, when
applicable, composition domain. A composition-dependent rule records its
composition basis and species identities. Evaluation outside a retained domain
fails. Unsupported free-form expressions remain rejected.

### `ResolvedModelInput`

`ResolvedModelInput` is a frozen provider object created from an ordered
`ParameterSet` and a validated `ModelOptions`. It owns:

- the exact component order;
- typed pure, association, interaction, dielectric, ion, Born, and solvation
  definitions;
- structural-zero evidence;
- the exact mapping from public formulation names to native enum/record fields;
- a stable definition fingerprint; and
- definition- and state-level receipt generation.

The object may compile a condition-independent native graph once. It must not
collapse condition-dependent values at mixture construction. Its state
evaluation consumes temperature in kelvin and normalized mole fractions and
returns the exact evaluated native snapshot used by that state.

No other public or internal owner serializes a `ParameterSet`, `ModelOptions`,
or raw mapping into native model arguments. Association topology construction
also moves behind this owner instead of being inferred in the adapter.

### Receipts and capabilities

The definition receipt contains schema versions, component order, source IDs,
parameter/formulation fingerprints, structural-zero records, and exact native
mapping metadata. The state receipt additionally contains temperature,
composition and basis, every evaluated correlation, domain evidence, and the
native snapshot fingerprint.

Receipts are detached immutable data: mutating a returned dictionary cannot
alter the calculation. Equivalent canonical inputs produce byte-stable
canonical receipt JSON and the same fingerprint.

`epcsaft.capabilities()` lists only configuration schema versions and preset
identities that pass provider contract tests. It does not report a process-wide
active preset.

## Package And Milestone Ownership

- M3 / `packages/epcsaft` owns schema parsing, correlation records, resolution,
  native provider records, receipts, capability metadata, and provider SDK.
- M4 and M5 own separate milestone issues for their adapters to the resolved
  provider contract. Those issues are blocked by the M3 SDK seam; their tests
  are consumer proofs, not a transfer of provider ownership into M3.
- M6 owns migration and retained evidence for paper bundles. An incomplete
  bundle may remain non-executable with a precise source blocker.
- User-facing provider docs and templates are M3-owned supporting files.

## Interfaces And Data Flow

1. A folder or mapping is parsed as a versioned `ModelOptions` selection.
2. Parameter files are parsed into a source-bearing `ParameterSet` without
   evaluating state-dependent definitions.
3. `Mixture(parameters, model_options=...)` validates component order and
   creates the frozen resolved definition graph.
4. `State(mixture, T=..., x=..., P=... or rho=...)` validates conditions and
   asks that graph for one exact native snapshot.
5. Native state construction accepts only the resolved provider record.
6. Provider, equilibrium, and regression results retain the state receipt or
   its fingerprint so the numerical result is reproducible.

## Loud Errors And Stop Gates

- Reject missing configuration, retired filenames, unknown schema keys,
  partial formulations, and conflicting preset/explicit selections.
- Reject a preset whose source record, native mapping, or required parameter
  family is incomplete.
- Reject missing interactions separately from sourced structural zeros.
- Reject nonfinite values, invalid units or bases, duplicate records,
  inconsistent component order, and correlation-domain violations.
- Stop the implementation slice if a native mapping cannot be traced to the
  active equation owner or source record.
- Stop a bundle migration when its literature source does not establish a
  value, zero policy, correlation domain, or formulation choice.
- Do not make a failed bundle executable by adding another default.

## Testing And Proof

Required proof families are:

- parser mutation tests for schema, selection, key, boolean, enum, source, and
  retired-file failures;
- correlation value, units, boundary, domain, and composition-basis tests;
- deterministic definition/state receipt and detached-copy tests;
- native contract tests proving raw mappings and `ParameterSet` cannot bypass
  `ResolvedModelInput`;
- provider property and derivative tests for one fully sourced neutral case,
  one associating case, and one fully sourced electrolyte case;
- M3 contract tests proving the SDK seam is consumable; separately owned M4 and
  M5 integration leaves prove each extension consumes it;
- repository structure tests proving retired serializers and filenames are
  absent; and
- strict docs, Ruff, diff, and cleanup checks.

Any test that computes model predictions must use traceable retained source
data and retain the required observation/model plot. Contract-only mutation
tests do not need a scientific plot.

## Migration And Cutover

1. Characterize each current serializer and its callers without preserving it
   as a compatibility route.
2. Add strict schema and typed records behind failing contract tests.
3. Establish the resolved graph, state evaluation, native record, and receipts.
4. Move provider state/property callers to that owner and delete displaced
   serializers in the same cutover series.
5. Publish the stable provider SDK seam, then unblock separate M4 and M5
   consumer-integration leaves; the M3 implementation issue does not edit
   sibling packages.
6. Migrate only source-complete provider-owned bundles mechanically. Record canonical
   loud blockers for incomplete bundles; paper-specific scientific repair is a
   separate M6/M4/M5 issue.
7. Update CONTEXT.md, PROJECT_CONTEXT.md, ADR 0001-era serialization language,
   templates, and user docs so `ParameterSet.to_runtime_dict()` is no longer
   described as canonical.

The M3 issue must not close while a supported provider call can still reach a
parallel serializer. It need not make an incomplete paper bundle executable.

## Risks

- Tight cutover will reveal many callers that relied on configuration defaults.
- A preset catalog can become an unreviewed default table if entries are not
  source-gated and immutable.
- Native graph caching can accidentally freeze state-dependent values.
- Receipt breadth can become unstable if canonical ordering is unspecified.
- Removing `ParameterSet.to_runtime_dict()` intentionally supersedes current
  context language and therefore requires coordinated ADR/context updates.

## Execution-Time Selections

- The initial preset catalog is empty unless planning identifies a fully
  source-proven entry. An unproven bundle is excluded, not made provisional.
- The first provider SDK binary-record schema is version `1`. M4/M5 consumer
  mapping may refine its fields before the RED test, but no old record remains
  as a fallback.

## Decision Ledger

| Decision | Evidence | Selected answer | Consequence | Deferred? | Owner |
| --- | --- | --- | --- | --- | --- |
| Primary purpose | User clarification, 2026-07-10 | Optimize for exact local reproducibility and validation correctness. | No release or marketing claim is required. | No | M3 |
| Public terminology | ADR 0002 and `CONTEXT.md` | Keep `ModelOptions`; use `model_configuration.json` as the file schema. | No unreviewed API rename. | No | M3 |
| Configuration choice | July 9 Task 9 audit | Require an immutable preset or a complete explicit formulation. | Partial mappings and hidden defaults disappear. | No | M3 |
| Scientific ownership | ADR 0002 plus code trace | `ParameterSet` owns data/correlations; `ModelOptions` owns formulation; `State` owns T/x. | Correlations resolve at actual conditions. | No | M3 |
| Native ownership | Duplicate serializer audit | One `ResolvedModelInput` graph owns native mapping and receipts. | Delete `to_runtime_dict`, mixture payload, and payload-side defaults. | No | M3 |
| Downstream failures | Paused Task 9 evidence | Separate consumer migration and paper repair from provider architecture. | Incomplete bundles fail at a canonical boundary without blocking source-independent provider design. | No | M3/M4/M5/M6 |
| Dataset decomposition | Tasks 9/21 reconciliation | Fold provider data/provenance/lookup separation into this owner cutover. | Avoid a later duplicate refactor of `datasets.py`. | No | M3 |
| Preset membership | Source audit not yet complete | Start empty; admit only fully proven entries named by later evidence. | Missing evidence causes exclusion. | No | M3/M6 |
