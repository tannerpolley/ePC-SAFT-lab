# M3 Versioned State-Resolved Model Input Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace permissive model-option/default insertion and parallel native serializers with one versioned, state-resolved provider input graph and deterministic receipts.

**Architecture:** `ModelOptions` parses schema version 1 as either a complete explicit formulation or an immutable admitted preset; the initial preset catalog is empty. `ParameterSet` owns only source-bearing scientific definitions, `ResolvedModelInput` is the sole Python-to-native compiler, and `State` evaluates its native input at the actual temperature and composition. The provider prepares a version-1 resolved-input SDK seam; separate stacked M4 and M5 leaves consume it before one coordinated integration cutover deletes the displaced serializers. M6 independently owns paper-bundle repair.

**Tech Stack:** Python 3.13, frozen dataclasses, canonical JSON and SHA-256 receipts, NumPy, pybind11, C++17 native provider records, CppAD provider derivatives, pytest, Ruff, Sphinx, CMake/Ninja, uv.

## Global Constraints

- Milestone ownership is M3 (`packages/epcsaft/**`) plus provider-owned repository tests, SDK manifests, contracts, and user documentation.
- Do not edit `packages/epcsaft-equilibrium/**` or `packages/epcsaft-regression/**` in this plan; create separate stacked M4 and M5 consumer leaves blocked by the prepared M3 SDK seam.
- Do not merge the provider hard cutover/deletions to `main` before both consumer leaves are integration-ready. Land the provider cutover and the two consumer commits as one verified integration sequence so `main` never retains a broken or parallel compatibility path.
- Do not repair Khudaida, Gross 2002, Held, or another paper-validation program in this plan. M6 owns source completion and bundle execution evidence.
- Model-configuration schema version is exactly `1`; missing, unversioned, partial, conflicting, or unknown input fails.
- The initial preset catalog is empty. A preset enters only in a separate source-evidence change with immutable source identity and provider contract tests.
- A complete explicit neutral formulation is valid only when electrostatics and
  every dependent formulation choice carry an explicit disabled sentinel. No
  inactive choice is omitted, represented by `None`, or supplied by a
  constructor default.
- Do not preserve `user_options.json`, `model_options.json`, loose runtime mappings, `ParameterSet.runtime_options`, `ParameterSet.to_runtime_dict()`, `Mixture._runtime_payload`, or payload-side option insertion.
- No compatibility wrapper, duplicate serializer, inferred scientific value, or silent formulation default survives the cutover.
- Temperature and composition correlations carry units, provenance, valid domains, and composition basis; out-of-domain evaluation fails.
- Tests that calculate model predictions must use traceable retained observations and an existing retained literature-versus-model plot. Contract-only parser, receipt, and native-record tests do not require a plot.
- Public equilibrium and regression capability claims do not change.
- Use test-driven development for every behavior change, systematic debugging for every unexpected failure, and fresh verification before each checkpoint claim.

---

## Source Evidence

- Approved design: `docs/superpowers/specs/2026-07-10-m3-eos-versioned-state-resolved-model-input.md`.
- Public ownership decisions: `docs/adr/0002-hard-public-api-reset-cppad-only-frontend.md` and `docs/adr/0005-package-extension-split.md`.
- Current duplicate owners: `packages/epcsaft/src/epcsaft/model/options.py`, `packages/epcsaft/src/epcsaft/model/parameters.py`, `packages/epcsaft/src/epcsaft/model/datasets.py`, `packages/epcsaft/src/epcsaft/frontend/mixture.py`, `packages/epcsaft/src/epcsaft/state/native_payload.py`, and `packages/epcsaft/src/epcsaft/state/native_adapter.py`.
- Typed interaction starting point: `ConstantInteractionRecord`, `LinearTemperatureInteractionRecord`, and `StructuralZeroPolicy` in `packages/epcsaft/src/epcsaft/model/parameters.py`.
- Water-diameter correlation source: `analyses/paper_validation/2026_khudaida/docs/md/source_01_khudaida_2026_main.md` at the retained Table 5 correlation.
- Alcohol-permittivity and salt-free solvent basis sources: `analyses/paper_validation/2012_held/docs/md/source_01_held_2012.md` at Table 4 and Eq. 22.
- Reference-temperature interaction source: `docs/papers/md/Equilibrium/Ascani - 2023 - Simultaneous Predictions of Chemical and Phase Equilibria in Systems with an Esterif.md` at Table 2.
- Read-only retained numerical evidence available to provider characterization:
  - neutral: `analyses/package_validation/equilibrium_single_component_vle/figures/hydrocarbon_saturation_pressure/results/hydrocarbon_saturation_pressure.png` and its plotted-data CSV;
  - associating: `analyses/paper_validation/2002_gross/figures/figure_01/results/figure_01.png`, `plotted_data.csv`, and `model_curve.csv`;
  - electrolyte: `analyses/paper_validation/2012_held/figures/figure_03/results/figure_3.png` and `figure_3.csv`.
- Paused experimental branch `codex/task9-paused` is implementation evidence only. Reuse its proven seams selectively; do not merge its nonempty preset catalog or paper migrations.

## Test Complete And Metrics

Test complete means all of the following are true on one coordinated committed integration revision containing the M3 provider stack and both M4/M5 consumer commits:

1. Parser mutation tests reject missing configuration, schema/version type errors, duplicate JSON keys, unknown keys, loose booleans, partial enabled electrolyte formulations, disabled-formulation extra fields, retired filenames, and preset selection against the empty catalog.
2. Parameter schema tests prove scientific records contain source identity, units, domains, structural-zero evidence, and typed correlations while containing no runtime formulation or state conditions.
3. Correlation tests reproduce the retained source equations at their retained source anchors and reject nonfinite values, unsupported expressions, invalid units/bases, and out-of-domain T/x. No new scientific acceptance tolerance is introduced by this plan.
4. Definition and state receipts are canonical, byte-stable for equivalent inputs, detached from returned mappings, and change fingerprint when a source definition, formulation, temperature, or composition changes.
5. Native contract tests prove `_core.NativeMixture` and `_core.NativeState` consume only the immutable version-1 `EvaluatedModelInput` native handle; raw mappings and `ParameterSet` cannot bypass `ResolvedModelInput`.
6. Focused provider property and derivative tests pass for one traceable neutral, associating, and electrolyte case, with the retained evidence paths above recorded in the tests or support fixture. These tests characterize provider continuity; they do not admit an equilibrium or regression family.
7. Repository structure tests prove the retired serializers, filenames, fallback loaders, and duplicate mapping code are absent.
8. `epcsaft.capabilities()` advertises model-configuration schema version `1` and an empty preset list; active policy appears only in instance receipts.
9. Provider API, native contract, derivative, provenance, templates, and source-bundle suites pass; both consumer SDK integration contracts pass; changed Python passes Ruff; strict docs, `git diff --check`, and cleanup pass.

## Outcome Proof

**Intent:** Make each local provider calculation reproducible from explicit scientific definitions, formulation choices, temperature, and composition without inferred model policy.
**Current Behavior:** `ModelOptions` has zero-argument defaults, folder loading accepts two retired filenames or no file, `ParameterSet` carries runtime options and serializes, `Mixture` serializes again, native payload code inserts electrolyte choices, and typed temperature interactions cannot reach runtime without being prematurely resolved.
**Expected Outcome:** Every `Mixture` owns one validated model definition, every `State` evaluates it at its exact T/x, native code consumes one immutable version-1 record, and results retain deterministic definition/state receipts.
**Target Output:** Strict schema parser, typed scientific records, decomposed source-bundle loading, `ResolvedModelInput`, version-1 native records/evaluator, provider SDK metadata, integration-ready M4/M5 consumer commits, one coordinated hard cutover, updated docs, and focused provider/consumer proof.
**Owner:** M3 EOS/provider owns implementation; M4 and M5 own their adapters; M6 owns paper-specific source completion and regenerated plots.
**Interface:** `ModelOptions.from_user_options(...)`, `ParameterSet.from_dict/from_json/from_dataset/from_folder(...)`, `ResolvedModelInput.resolve(parameters, model_options, components=...)`, `ResolvedModelInput.configuration_receipt`, `ResolvedModelInput.evaluate(temperature=..., composition=...) -> EvaluatedModelInput`, `EvaluatedModelInput.native_handle`, `EvaluatedModelInput.receipt`, `Mixture`, `State`, `epcsaft.capabilities()`, and `epcsaft.provider_native_sdk()`.
**Cutover:** Prepare and contract-test the version-1 SDK seam, stack the separate M4 and M5 consumer leaves on that seam, then integrate the provider frontend/native cutover, both consumer commits, and deletion of all displaced serializers as one verified sequence.
**Replaced Path:** `ModelOptions()` defaults, `coerce_model_options(None)`, `user_options.json`/`model_options.json`, `runtime_options`, `to_runtime_dict()`, `Mixture._runtime_payload`, `state/native_payload.py`, and raw-mapping native construction.
**Evidence:** RED/GREEN mutation receipts, provider-only native build, focused API/native/derivative suites, source-backed characterization tests, absence scans, strict docs, Ruff, diff check, and cleanup output.
**Acceptance Proof:** On the combined provider/M4/M5 revision, a clean provider-only build passes the provider suite and both consumer SDK contracts; equivalent explicit inputs produce identical canonical receipts/fingerprints; distinct T/x produce distinct state receipts; every native state reports exact evaluated records/structural zeros/native mappings; and no supported provider or consumer call reaches a displaced serializer.
**Stop Criteria:** Stop the affected slice if an active native choice cannot be traced to an equation owner or source record, if a correlation lacks source/domain/basis evidence, if the native record cannot express the active formulation exactly, or if a required numerical test lacks retained observation/model evidence.
**Avoid:** Do not add defaults, provisional presets, expression evaluation, guessed domains, inferred structural zeros, paper-specific repair, consumer-package edits, capability expansion, redirectors, or a second payload compiler.
**Risk:** The hard cutover will expose callers that relied on inferred configuration and can reveal incomplete paper inputs; resolving those failures in the provider slice would recreate the scope problem this plan is designed to remove.

## Implementation Boundaries

**Files To Create:** `packages/epcsaft/src/epcsaft/model/configuration_catalog.py`, `packages/epcsaft/src/epcsaft/model/correlations.py`, `packages/epcsaft/src/epcsaft/model/resolved_input.py`, `packages/epcsaft/src/epcsaft/model/source_bundles.py`, `packages/epcsaft/src/epcsaft/state/input_validation.py`, version-1 native resolved-input model/binding files under `packages/epcsaft/src/epcsaft/native/model` and `native/bindings`, focused provider tests, and provider-owned fixture configuration files.
**Files To Modify:** Provider model/frontend/state/runtime/native sources; provider CMake and SDK source manifest; provider package exports/type stubs/tests/support; `CONTEXT.md`, `docs/superpowers/PROJECT_CONTEXT.md`, ADR 0001/0002 clarifications, provider API/SDK contracts, user/model-input docs, templates, and provider-owned repository structure tests.
**Files To Avoid:** `packages/epcsaft-equilibrium/**`, `packages/epcsaft-regression/**`, `analyses/paper_validation/**`, downstream repositories, M4/M5 capability registries, release metadata, and the paused branch itself.
**Source Of Truth:** The approved M3 spec, ADR 0002/0005, typed source records, `docs/latex/equations.tex` plus native equation owners for mapping semantics, and the version-1 provider SDK contract.
**Read Path:** Parse `model_configuration.json`; parse scientific definitions into `ParameterSet`; resolve ordered definitions once; evaluate T/x in `State`; read immutable native snapshot and detached receipts from the provider object.
**Write Path:** Write only canonical in-memory records and detached receipt mappings. Templates write unresolved schema files; implementation does not rewrite paper bundles.
**Integration Points:** Provider package root exports, `Mixture`/`State`, native model setup, CppAD property/derivative calls, provider capabilities, provider native SDK CMake/source manifest, and source-checkout validation registry.
**Migration Or Cutover:** Increment the incompatible parameter-set envelope to schema version 3 on the provider stack, prepare M4/M5 consumer commits against SDK v1, then integrate provider cutover plus both consumers before rejecting version 2 and deleting old serializers on `main`; leave paper migrations to explicit M6 issues.
**Replaced Path Handling:** Delete displaced serializers and source files; update all provider-owned references; add structural guards preventing retired filenames/functions from returning.
**Acceptance Proof Gate:** Do not mark the M3 tracking parent complete until provider-only build/tests/docs pass, both M4/M5 consumer integration leaves pass against SDK v1 and are integrated with the hard cutover, the absence scan is clean on the combined revision, and remaining paper failures are classified under M6 rather than hidden.

## Decision Ledger

| Decision | Evidence | Selected answer | Consequence | Deferred? | Owner |
| --- | --- | --- | --- | --- | --- |
| Primary purpose | User clarification and approved spec | Optimize local reproducibility and validation correctness, not release messaging. | Receipts and strict inputs are proof/debug tools. | No | M3 |
| Configuration schema | Approved spec | `epcsaft.model-configuration`, version `1`. | Unversioned mappings fail. | No | M3 |
| Preset catalog | Approved execution selection | Start empty. | Every initial executable fixture uses a complete explicit formulation. | No | M3 |
| Parameter schema | Removal of `runtime_options` and addition of typed scientific records changes the canonical shape | Increment `epcsaft.parameter-set` to version `3`; reject version `2`. | No compatibility parser remains. | No | M3 |
| Correlation scope | Retained local inputs | Admit only constant, reference-temperature linear, logarithmic-temperature, sourced exponential, sourced piecewise, and exact sourced composition forms needed by retained evidence. | Free-form expressions stay rejected. | No | M3 |
| State conditions | ADR 0002 | `State` owns T/x and triggers evaluation. | No mixture-time collapse of dynamic values. | No | M3 |
| Native owner | Duplicate serializer audit | `ResolvedModelInput` is the sole compiler to `ResolvedNativeInput` version `1`. | Raw maps and `ParameterSet` cannot construct native state. | No | M3 |
| Receipt identity | Reproducibility requirement | Canonical sorted JSON plus SHA-256 definition fingerprint; state receipt includes T/x and evaluated records. | Equivalent inputs are byte-stable and returned mappings are detached. | No | M3 |
| Scientific test data | Repo validation policy | Reuse only traceable retained cases with existing observation/model plots. | Missing evidence blocks the numerical test and routes to M6. | No | M3/M6 |
| Consumer migration | ADR 0005 and repo milestone invariant | Prepare SDK v1 in the M3 stack, build separate M4/M5 consumer commits on it, then integrate all three in dependency order. | This plan does not edit sibling packages, and `main` never retains the provider hard cutover without both consumers. | Yes | M4/M5 |
| Paper migration | Paused Task 9 failure surface | Separate nonblocking M6 leaves migrate/repair individual bundles. | Incomplete bundles remain non-executable with exact blockers and do not gate M3 closure. | Yes | M6 |

## Tasks

### Task 1: Establish The Strict Version-1 Model Configuration Boundary

**Use Cases:**

- A neutral provider caller supplies an explicit disabled-electrostatics formulation and gets one deterministic `ModelOptions` record.
- An electrolyte caller must supply every active choice with strict booleans and supported tokens.
- Missing files, retired filenames, duplicate JSON keys, partial mappings, and preset requests against the empty catalog fail before parameter resolution.
- The cutover replaces zero-argument/default construction rather than preserving it.

**Files:**

- Create: `packages/epcsaft/src/epcsaft/model/configuration_catalog.py`
- Create: `packages/epcsaft/tests/api/frontend/test_model_configuration_receipt.py`
- Create: `packages/epcsaft/tests/api/package/test_model_configuration_capabilities.py`
- Modify: `packages/epcsaft/src/epcsaft/model/options.py`
- Modify: `packages/epcsaft/src/epcsaft/model/__init__.py`
- Modify: `packages/epcsaft/src/epcsaft/__init__.py`
- Modify: `packages/epcsaft/src/epcsaft/runtime/core.py`
- Modify: `packages/epcsaft/src/epcsaft/_core.pyi`

**Interfaces:**

- Consumes: `InputError` and current public `ModelOptions` name.
- Produces: `MODEL_CONFIGURATION_SCHEMA = "epcsaft.model-configuration"`, `MODEL_CONFIGURATION_SCHEMA_VERSION = 1`, `MODEL_CONFIGURATION_FILENAME = "model_configuration.json"`, `MODEL_CONFIGURATION_PRESETS = ()`, `ModelOptions.from_user_options(value) -> ModelOptions`, and detached capability payload `{"supported_schemas": [...], "admitted_presets": []}`.

- [ ] **Step 1: Write parser RED tests before production edits.**

  Use this complete explicit-neutral fixture in the tests. Each disabled
  dependent term is an explicit schema value; none is inferred from the parent
  switch:

  ```python
  EXPLICIT_NEUTRAL_CONFIGURATION = {
      "schema": "epcsaft.model-configuration",
      "schema_version": 1,
      "selection_origin": "explicit_configuration",
      "formulation": {
          "electrostatics": {"enabled": False},
          "relative_permittivity": {"enabled": False},
          "debye_huckel": {"enabled": False},
          "born": {"enabled": False},
          "solvated_ion_diameter": {"enabled": False},
          "ion_dispersion": {"enabled": False},
      },
  }
  ```

  Add named tests for absent configuration, direct construction, retired filenames, schema/version types, duplicate keys, unknown keys, conflicting preset/formulation, strict booleans, incomplete electrolyte choices, inactive fields on disabled formulations, and empty-catalog preset rejection.

- [ ] **Step 2: Run the RED slice and confirm feature-specific failures.**

  Run:

  ```bash
  uv run --no-sync pytest -q \
    packages/epcsaft/tests/api/frontend/test_model_configuration_receipt.py \
    packages/epcsaft/tests/api/package/test_model_configuration_capabilities.py
  ```

  Expected: tests fail because the current parser accepts missing/default input, retired filenames, and zero-argument construction; collection errors or unrelated import failures do not count as RED evidence.

- [ ] **Step 3: Implement the empty catalog and strict parser.**

  The public construction contract is:

  ```python
  @dataclass(frozen=True, slots=True, init=False)
  class ModelOptions:
      schema: str
      schema_version: int
      selection: Literal["preset", "explicit"]
      selection_origin: Literal["explicit_configuration"] | None
      preset_id: str | None
      preset_version: int | None
      electrostatics: DisabledFormulation | ElectrostaticsOptions
      relative_permittivity_rule: DisabledFormulation | RelativePermittivityRule
      debye_huckel: DisabledFormulation | DebyeHuckelOptions
      born_model: DisabledFormulation | BornModelOptions
      solvated_ion_diameter_rule: DisabledFormulation | SolvatedIonDiameterRule
      ion_dispersion_rule: DisabledFormulation | IonDispersionRule

      @classmethod
      def from_user_options(
          cls,
          value: str | Path | Mapping[str, Any] | "ModelOptions",
      ) -> "ModelOptions": ...
  ```

  `DisabledFormulation` is a frozen sentinel with the sole field
  `enabled: Literal[False]`; each enabled record requires every field for its
  selected formulation and none of these records has a dataclass default. Keep
  CppAD fixed provider behavior out of the user schema. Parse JSON with
  duplicate-key rejection. A directory accepts only
  `model_configuration.json`; presence of either retired filename is an error
  even if the new file also exists.

- [ ] **Step 4: Expose global schema discovery without active instance policy.**

  Add `model_configuration_capabilities()` to the catalog and merge only its schema/preset discovery into `epcsaft.capabilities()`. Return fresh nested containers on every call.

- [ ] **Step 5: Run GREEN and refactor.**

  Run the Task 1 command again. Expected: all collected tests pass, `admitted_presets == []`, and no active formulation appears in global capabilities. Refactor key parsing into small exact-key/strict-scalar helpers while the slice stays green.

- [ ] **Step 6: Checkpoint commit.**

  ```bash
  git add \
    packages/epcsaft/src/epcsaft/model/configuration_catalog.py \
    packages/epcsaft/src/epcsaft/model/options.py \
    packages/epcsaft/src/epcsaft/model/__init__.py \
    packages/epcsaft/src/epcsaft/runtime/core.py \
    packages/epcsaft/src/epcsaft/__init__.py \
    packages/epcsaft/src/epcsaft/_core.pyi \
    packages/epcsaft/tests/api/frontend/test_model_configuration_receipt.py \
    packages/epcsaft/tests/api/package/test_model_configuration_capabilities.py
  git commit -m "feat(provider): require versioned model configuration"
  ```

### Task 2: Make Parameter Data Typed, Source-Bearing, And Policy-Free

**Use Cases:**

- A source record preserves parameter units, provenance, domain, and typed correlation structure through JSON round-trip.
- A temperature or composition correlation evaluates only inside its retained domain/basis.
- `ParameterSet` cannot carry formulation choices, state T/x, or a native runtime payload.
- Schema version 3 replaces the version-2 runtime-options shape and prevents duplicate serializers from returning.

**Files:**

- Create: `packages/epcsaft/src/epcsaft/model/correlations.py`
- Create: `packages/epcsaft/tests/api/frontend/test_parameter_correlations.py`
- Create: `packages/epcsaft/tests/api/frontend/test_formulation_records.py`
- Create: `packages/epcsaft/tests/api/frontend/test_parameter_set_ownership.py`
- Modify: `packages/epcsaft/src/epcsaft/model/parameters.py`
- Modify: `packages/epcsaft/src/epcsaft/model/__init__.py`
- Modify: `packages/epcsaft/src/epcsaft/__init__.py`
- Modify: `packages/epcsaft/tests/api/frontend/test_interaction_provenance.py`
- Modify: `packages/epcsaft/tests/api/frontend/test_parameter_input_integrity.py`

**Interfaces:**

- Consumes: version-2 `PureRecord`, interaction records, `StructuralZeroPolicy`, and the source correlations named in Source Evidence.
- Produces: `PARAMETER_SET_SCHEMA_VERSION = 3`; `TemperatureDomainEvidence`, `TemperatureDomain`, `CorrelationProvenance`, typed `ParameterCorrelation` variants, `PureParameterProvenance`, formulation records, `ReferenceTemperatureLinearInteractionRecord`, and a `ParameterSet` with no runtime serializer.

- [ ] **Step 1: Write RED round-trip and ownership tests.**

  Assert the canonical top-level shape is exactly:

  ```python
  {
      "schema",
      "schema_version",
      "components",
      "pure_records",
      "formulation_records",
      "interactions",
      "interaction_policies",
      "metadata",
  }
  ```

  Add tests that version 2, `runtime_options`, `T`, `x`, model-choice keys, expression strings, invalid units/domains, duplicate records, missing provenance, and unsourced zero cells are rejected.

- [ ] **Step 2: Verify RED.**

  Run:

  ```bash
  uv run --no-sync pytest -q \
    packages/epcsaft/tests/api/frontend/test_parameter_correlations.py \
    packages/epcsaft/tests/api/frontend/test_formulation_records.py \
    packages/epcsaft/tests/api/frontend/test_parameter_set_ownership.py \
    packages/epcsaft/tests/api/frontend/test_interaction_provenance.py \
    packages/epcsaft/tests/api/frontend/test_parameter_input_integrity.py
  ```

  Expected: feature-specific failures because schema 2 still permits `runtime_options`, current pure values lack typed source/domain records, and temperature interactions have no state evaluator.

- [ ] **Step 3: Add the typed correlation API.**

  Define frozen records with these evaluation interfaces:

  ```python
  class TemperatureDomain:
      def validate_temperature(self, temperature: Real) -> float: ...

  class ConstantTemperatureCorrelation:
      def evaluate(self, temperature: Real) -> float: ...

  class ReferenceTemperatureLinearCorrelation:
      def evaluate(self, temperature: Real) -> float: ...

  class LogTemperatureCorrelation:
      def evaluate(self, temperature: Real) -> float: ...

  class ConstantPlusExponentialTermsCorrelation:
      def evaluate(self, temperature: Real) -> float: ...

  class PiecewiseQuadraticTemperatureCorrelation:
      def evaluate(self, temperature: Real) -> float: ...

  class SaltFreeWaterMoleFractionCubicPermittivityCorrelation:
      def evaluate(self, temperature: Real, composition: Sequence[Real], components: Sequence[str]) -> float: ...
  ```

  Canonical parsers accept numeric coefficients only, exact units/bases, explicit domain evidence, and exact keys. Use the retained equations only in tests that cite their local source files.

- [ ] **Step 4: Cut `ParameterSet` to scientific definitions only.**

  Remove `runtime_options`, `to_runtime_dict()`, `ParameterSource.to_runtime_dict()`, runtime-option normalization, and interaction-matrix emission. Store immutable tuples of pure, formulation, interaction, and structural-zero records; preserve canonical JSON ordering and duplicate-key rejection.

- [ ] **Step 5: Run GREEN, then refactor record families.**

  Run the Task 2 command again. Expected: all tests pass; source anchors reproduce their retained equations; arbitrary strings and out-of-domain evaluation fail. Split parsing/serialization helpers by record family only where it reduces `parameters.py` ownership without adding alternate public paths.

- [ ] **Step 6: Checkpoint commit.**

  ```bash
  git add \
    packages/epcsaft/src/epcsaft/model/correlations.py \
    packages/epcsaft/src/epcsaft/model/parameters.py \
    packages/epcsaft/src/epcsaft/model/__init__.py \
    packages/epcsaft/src/epcsaft/__init__.py \
    packages/epcsaft/tests/api/frontend/test_parameter_correlations.py \
    packages/epcsaft/tests/api/frontend/test_formulation_records.py \
    packages/epcsaft/tests/api/frontend/test_parameter_set_ownership.py \
    packages/epcsaft/tests/api/frontend/test_interaction_provenance.py \
    packages/epcsaft/tests/api/frontend/test_parameter_input_integrity.py
  git commit -m "refactor(provider): separate scientific records from runtime policy"
  ```

### Task 3: Separate Source-Bundle Storage, Validation, And Selection

**Use Cases:**

- A provider-owned bundle loader reads scientific files and one explicit configuration without evaluating at guessed state conditions.
- Typed source correlations are selected by component/field identity, never by evaluating a text expression.
- An incomplete bundle returns a precise input error and remains non-executable.
- The decomposition replaces `datasets.py` as a model-policy and native-payload owner.

**Files:**

- Create: `packages/epcsaft/src/epcsaft/model/source_bundles.py`
- Create: `packages/epcsaft/tests/api/frontend/test_source_bundle_loading.py`
- Create: `packages/epcsaft/tests/fixtures/model_input/explicit_neutral/model_configuration.json`
- Create: `packages/epcsaft/tests/fixtures/model_input/explicit_neutral/parameter_set.json`
- Modify: `packages/epcsaft/src/epcsaft/model/datasets.py`
- Modify: `packages/epcsaft/src/epcsaft/model/sources.py`
- Modify: `packages/epcsaft/src/epcsaft/model/validation.py`
- Modify: `packages/epcsaft/src/epcsaft/model/templates.py`
- Modify: `packages/epcsaft/tests/api/frontend/test_templates.py`
- Modify: `packages/epcsaft/tests/api/frontend/test_parameter_input_integrity.py`

**Interfaces:**

- Consumes: schema-3 `ParameterSet`, strict `ModelOptions`, current CSV/source-manifest validation, and provider input templates.
- Produces: `SourceBundleSelection`, `load_source_bundle_selection(path, *, components) -> SourceBundleSelection`, typed lookup methods, and templates that write unresolved `model_configuration.json` plus scientific schema files.

- [ ] **Step 1: Add RED ownership and bundle-selection tests.**

  Require that `datasets.py` contains no default option tables, model normalization, native mapping, composition precomputation, or serializer; require `source_bundles.py` to reject raw expressions that do not have an exact typed record, missing configuration, duplicate records, and incomplete pair evidence.

- [ ] **Step 2: Verify RED.**

  Run:

  ```bash
  uv run --no-sync pytest -q \
    packages/epcsaft/tests/api/frontend/test_source_bundle_loading.py \
    packages/epcsaft/tests/api/frontend/test_templates.py \
    packages/epcsaft/tests/api/frontend/test_parameter_input_integrity.py \
    packages/epcsaft/tests/api/frontend/test_parameter_set_ownership.py
  ```

  Expected: failures identify current default tables, expression parsing, state-time evaluation, and `user_options.json` template output.

- [ ] **Step 3: Implement the source-bundle selection boundary.**

  Use immutable selection records:

  ```python
  @dataclass(frozen=True, slots=True)
  class SourceBundleSelection:
      parameter_set: ParameterSet
      model_options: ModelOptions
      source_files: tuple[Path, ...]

      def pure_correlation(self, component: str, field: str) -> ParameterCorrelation: ...
      def interaction_correlation(self, family: str, left: str, right: str) -> InteractionRecord: ...
  ```

  Keep file IO and manifest identity in `source_bundles.py`; keep record validation in `parameters.py`; keep `datasets.py` limited to dataset discovery/storage reads that return source records.

- [ ] **Step 4: Replace template output.**

  `create_input_template()` writes `model_configuration.json` with schema/version and unresolved explicit choices that fail until the user supplies a complete formulation/source identity. It does not write a populated default model.

- [ ] **Step 5: Run GREEN and refactor.**

  Run the Task 3 command again. Expected: all provider bundle/template/ownership tests pass, and the provider fixture loads without evaluating temperature or composition.

- [ ] **Step 6: Checkpoint commit.**

  ```bash
  git add \
    packages/epcsaft/src/epcsaft/model/source_bundles.py \
    packages/epcsaft/src/epcsaft/model/datasets.py \
    packages/epcsaft/src/epcsaft/model/sources.py \
    packages/epcsaft/src/epcsaft/model/validation.py \
    packages/epcsaft/src/epcsaft/model/templates.py \
    packages/epcsaft/tests/api/frontend/test_source_bundle_loading.py \
    packages/epcsaft/tests/api/frontend/test_templates.py \
    packages/epcsaft/tests/api/frontend/test_parameter_input_integrity.py \
    packages/epcsaft/tests/api/frontend/test_parameter_set_ownership.py \
    packages/epcsaft/tests/fixtures/model_input/explicit_neutral/model_configuration.json \
    packages/epcsaft/tests/fixtures/model_input/explicit_neutral/parameter_set.json
  git commit -m "refactor(provider): separate source bundle selection"
  ```

### Task 4: Add The Version-1 Resolved Native Record And State Evaluator

**Use Cases:**

- Native code receives one immutable identity, formulation, and parameter graph instead of a mutable argument dictionary.
- The evaluator resolves temperature/composition records, exact interactions, structural zeros, association topology, and formulation mappings at state conditions.
- Native construction rejects missing pair evidence, inactive choices, invalid component order, and out-of-domain records.
- The record schema replaces payload-side defaults and raw mapping conversion.

**Files:**

- Create: `packages/epcsaft/src/epcsaft/native/model/resolved_input.h`
- Create: `packages/epcsaft/src/epcsaft/native/model/resolved_input.cpp`
- Create: `packages/epcsaft/src/epcsaft/native/model/resolved_input_evaluator.h`
- Create: `packages/epcsaft/src/epcsaft/native/bindings/resolved_input_binding_internal.h`
- Create: `packages/epcsaft/src/epcsaft/native/bindings/resolved_input_bindings.h`
- Create: `packages/epcsaft/src/epcsaft/native/bindings/resolved_input_bindings.cpp`
- Create: `packages/epcsaft/src/epcsaft/native/bindings/resolved_input_record_bindings.cpp`
- Create: `packages/epcsaft/tests/native/contracts/test_resolved_native_input_contract.py`
- Modify: `packages/epcsaft/src/epcsaft/native/model/native_types.h`
- Modify: `packages/epcsaft/src/epcsaft/native/model/parameter_setup.cpp`
- Modify: `packages/epcsaft/src/epcsaft/native/bindings/module.cpp`
- Modify: `packages/epcsaft/src/epcsaft/native/bindings/payload_converters.cpp`
- Modify: `packages/epcsaft/src/epcsaft/native/bindings/payload_converters.h`
- Modify: `packages/epcsaft/CMakeLists.txt`
- Modify: `packages/epcsaft/src/epcsaft/native_sdk/provider_native_sdk_v1/provider_sources.json`
- Modify: `packages/epcsaft/src/epcsaft/_core.pyi`

**Interfaces:**

- Consumes: typed Python record semantics, native parameter setup, and provider component ordering.
- Produces: C++ `ResolvedNativeInput`, `ResolvedNativeInputSnapshot`, `NativeInputIdentity`, `NativeFormulation`, `NativeParameterGraph`, typed temperature/composition values, and `ResolvedNativeInput::evaluate(double temperature_K, const std::vector<double>& composition)`.

- [ ] **Step 1: Write RED native-record tests.**

  Add pybind contract tests for immutable construction, exact schema/version,
  empty preset semantics, complete explicit formulation, domain evaluation,
  reference-temperature interaction, structural-zero retention, exact component
  order, every pair/family evidence, and rejection of raw mappings. Add a
  field-coverage table keyed to every model-input member of `add_args`; for each
  member, prove the snapshot carries the evaluated value plus its source/native
  mapping reference, or prove the member's native consumer was deleted in this
  cutover. Mutate one field in each pure, association, interaction, dielectric,
  ion, Born, and solvation group and require the snapshot fingerprint to change.

- [ ] **Step 2: Build and confirm RED.**

  Run:

  ```bash
  uv run --no-sync python scripts/dev/build_epcsaft.py --clean --profile provider --parallel 1
  uv run --no-sync pytest -q packages/epcsaft/tests/native/contracts/test_resolved_native_input_contract.py
  ```

  Expected: the build or tests fail because resolved native record types and evaluator bindings do not exist. A dependency/build-environment failure must be diagnosed separately and is not RED behavior evidence.

- [ ] **Step 3: Implement the native schema without a legacy constructor.**

  The stable native boundary is:

  ```cpp
  struct NativeEvaluatedInputSnapshot {
      std::string schema{"epcsaft.resolved-model-input"};
      int schema_version{1};
      std::string definition_fingerprint_sha256;
      std::string snapshot_fingerprint_sha256;
      std::vector<std::string> component_order;
      double temperature_K;
      std::vector<double> mole_fraction;
      std::string composition_basis{"mole_fraction"};

      // Exact evaluated record evidence.
      std::vector<EvaluatedRecordEvidence> evaluated_records;
      std::vector<StructuralZeroEvidence> structural_zeros;

      // Every numeric input consumed by the current add_args/EOS graph.
      std::vector<double> segment_count;
      std::vector<double> sigma_angstrom;
      std::vector<double> epsilon_k_K;
      std::vector<double> molecular_weight_kg_per_mol;
      std::vector<double> charge_number;
      std::vector<double> association_energy_K;
      std::vector<double> association_volume;
      std::vector<int> association_site_count;
      std::vector<int> association_site_matrix;
      std::vector<double> k_ij_row_major;
      std::vector<double> l_ij_row_major;
      std::vector<double> k_hb_ij_row_major;
      std::vector<double> pure_relative_permittivity;
      MixedRelativePermittivityInputs mixed_relative_permittivity;
      std::vector<double> born_diameter_angstrom;
      std::vector<double> solvation_factor;

      // Every selected native enum/switch, including explicit disabled values.
      NativeFormulation formulation;
      std::map<std::string, NativeFieldReference> native_mapping;
  };

  struct ResolvedNativeInput {
      NativeInputIdentity identity;
      NativeFormulation formulation;
      NativeParameterGraph parameter_graph;
  };

  NativeEvaluatedInputSnapshot evaluate_resolved_native_input(
      const ResolvedNativeInput& input,
      double temperature_K,
      const std::vector<double>& composition
  );
  ```

  `NativeFormulation` must carry the exact dielectric rule and derivative mode,
  hard-chain/dispersion/association derivative modes, ion-diameter rule,
  Debye-Huckel model and derivative switches, Born model/radius/diameter/
  dielectric/solvation switches, and their explicit disabled sentinels. The
  mixed-relative-permittivity record carries coefficient arrays, mask, and
  water index. `NativeFieldReference` identifies the public record ID, native
  destination field, owning equation/native consumer, and selected enum token.
  Audit this list field-for-field against `add_args` in
  `native/model/native_types.h`, its construction in
  `native/model/parameter_setup.cpp`, and all contribution/property/derivative
  consumers named in Task 6; a field may disappear only when its old native
  consumer is deleted in the same cutover. Store typed variants, not expression
  strings. Validate all invariants in construction/evaluation and expose
  read-only pybind properties.

- [ ] **Step 4: Register sources and remove duplicate conversion responsibility.**

  Add the new native sources to the canonical provider SDK manifest and provider CMake graph. Restrict `payload_converters` to detached result conversion; it must not build model arguments from a Python mapping.

- [ ] **Step 5: Build and run GREEN.**

  Run the Task 4 build and test commands again. Expected: provider-only build succeeds and all native resolved-input contract tests pass.

- [ ] **Step 6: Refactor and checkpoint.**

  Keep record validation in `resolved_input.cpp`, templated evaluation in `resolved_input_evaluator.h`, and binding-only code under `native/bindings`. Then commit:

  ```bash
  git add \
    packages/epcsaft/CMakeLists.txt \
    packages/epcsaft/src/epcsaft/native/model \
    packages/epcsaft/src/epcsaft/native/bindings \
    packages/epcsaft/src/epcsaft/native_sdk/provider_native_sdk_v1/provider_sources.json \
    packages/epcsaft/src/epcsaft/_core.pyi \
    packages/epcsaft/tests/native/contracts/test_resolved_native_input_contract.py
  git commit -m "feat(provider): add resolved native input schema"
  ```

### Task 5: Make `ResolvedModelInput` The Sole Compiler And Receipt Owner

**Use Cases:**

- Equivalent parameter/configuration definitions produce identical definition receipts and fingerprints.
- A state evaluates nonconstant records at exact T/x and receives one immutable
  `EvaluatedModelInput` containing the exact native snapshot handle plus a
  detached receipt for every evaluated record, structural zero, and native
  mapping.
- Mutating a returned receipt cannot mutate later calculations or receipts.
- Source incompatibility or missing active formulation data fails before native state construction.

**Files:**

- Create: `packages/epcsaft/src/epcsaft/model/resolved_input.py`
- Modify: `packages/epcsaft/src/epcsaft/model/__init__.py`
- Modify: `packages/epcsaft/src/epcsaft/__init__.py`
- Modify: `packages/epcsaft/tests/api/frontend/test_model_configuration_receipt.py`
- Modify: `packages/epcsaft/tests/api/frontend/test_parameter_correlations.py`
- Modify: `packages/epcsaft/tests/api/frontend/test_interaction_provenance.py`

**Interfaces:**

- Consumes: schema-3 `ParameterSet`, strict `ModelOptions`, and `_core.ResolvedNativeInput` version 1.
- Produces: `ResolvedModelInput.resolve(...)`, `configuration_receipt`,
  `evaluate(temperature=..., composition=...) -> EvaluatedModelInput`,
  `EvaluatedModelInput.native_handle`, `EvaluatedModelInput.receipt`,
  `EvaluatedModelInput.snapshot_fingerprint_sha256`,
  `ResolvedModelInput.fingerprint_sha256`, and exact native graph ownership.

- [ ] **Step 1: Add RED deterministic-receipt tests.**

  Exercise construction order, mapping key order, detached copies, missing/blank parameter provenance, missing active records, domain failure, state T/x changes, structural zeros, and exact native mapping metadata. Explicit configuration origin identifies the user selection; it is not required to duplicate every scientific record's source identity.

- [ ] **Step 2: Verify RED.**

  Run:

  ```bash
  uv run --no-sync pytest -q \
    packages/epcsaft/tests/api/frontend/test_model_configuration_receipt.py \
    packages/epcsaft/tests/api/frontend/test_parameter_correlations.py \
    packages/epcsaft/tests/api/frontend/test_interaction_provenance.py
  ```

  Expected: failures because no Python resolved owner/fingerprint/state receipt exists.

- [ ] **Step 3: Implement the sole compiler.**

  Use this public boundary:

  ```python
  @dataclass(frozen=True, slots=True, init=False)
  class EvaluatedModelInput:
      definition_fingerprint_sha256: str
      snapshot_fingerprint_sha256: str
      _native_handle: Any
      _receipt_json: str

      @property
      def native_handle(self) -> Any: ...

      @property
      def receipt(self) -> dict[str, Any]: ...

  @dataclass(frozen=True, slots=True, init=False)
  class ResolvedModelInput:
      components: tuple[str, ...]
      fingerprint_sha256: str
      _native_input: Any

      @classmethod
      def resolve(
          cls,
          parameters: ParameterSet,
          model_options: ModelOptions,
          *,
          components: Sequence[str] | None = None,
      ) -> "ResolvedModelInput": ...

      @property
      def configuration_receipt(self) -> dict[str, Any]: ...

      def evaluate(
          self,
          *,
          temperature: float,
          composition: Sequence[float],
      ) -> EvaluatedModelInput: ...
  ```

  The frozen `EvaluatedModelInput` is the provider SDK object used by `State`
  and M5: its read-only pybind `native_handle` is the exact snapshot passed to
  native code, while every `receipt` access reparses `_receipt_json` (or uses an
  equivalent deep detachment). It is not a mapping and exposes no serializer.
  Fingerprint canonical sorted JSON containing schema/version, exact component
  order, configuration, parameter definitions, structural zeros, and native
  mapping contract.

- [ ] **Step 4: Run GREEN and refactor.**

  Run the Task 5 command again. Expected: deterministic/copy-safety/source/domain tests pass. Keep native-record construction private to this module.

- [ ] **Step 5: Checkpoint commit.**

  ```bash
  git add \
    packages/epcsaft/src/epcsaft/model/resolved_input.py \
    packages/epcsaft/src/epcsaft/model/__init__.py \
    packages/epcsaft/src/epcsaft/__init__.py \
    packages/epcsaft/tests/api/frontend/test_model_configuration_receipt.py \
    packages/epcsaft/tests/api/frontend/test_parameter_correlations.py \
    packages/epcsaft/tests/api/frontend/test_interaction_provenance.py
  git commit -m "feat(provider): resolve model input with deterministic receipts"
  ```

### Task 6: Cut `Mixture`, `State`, And Native Provider Calls To The Resolved Graph

**Use Cases:**

- `Mixture` requires explicit model configuration and stores one frozen definition graph.
- `State` validates T/x, evaluates the graph at those conditions, constructs native state from the resolved record, and exposes a detached receipt.
- Condition-dependent inputs cannot be accessed through a condition-free `Mixture.native` path.
- Raw mappings, `ParameterSet`, and deleted payload helpers cannot bypass the sole compiler.

**Files:**

- Create: `packages/epcsaft/src/epcsaft/state/input_validation.py`
- Create: `packages/epcsaft/tests/support/model_configurations.py`
- Modify: `packages/epcsaft/src/epcsaft/frontend/mixture.py`
- Modify: `packages/epcsaft/src/epcsaft/frontend/state.py`
- Modify: `packages/epcsaft/src/epcsaft/state/native_adapter.py`
- Delete: `packages/epcsaft/src/epcsaft/state/native_payload.py`
- Modify: `packages/epcsaft/src/epcsaft/runtime/core.py`
- Modify: `packages/epcsaft/src/epcsaft/native/eos/state.cpp`
- Modify: `packages/epcsaft/src/epcsaft/native/eos/core_internal.h`
- Modify: `packages/epcsaft/src/epcsaft/native/eos/contributions/contribution_internal.h`
- Modify: `packages/epcsaft/src/epcsaft/native/eos/contributions/association.cpp`
- Modify: `packages/epcsaft/src/epcsaft/native/eos/contributions/born.cpp`
- Modify: `packages/epcsaft/src/epcsaft/native/eos/contributions/dispersion.cpp`
- Modify: `packages/epcsaft/src/epcsaft/native/eos/contributions/hard_chain.cpp`
- Modify: `packages/epcsaft/src/epcsaft/native/eos/contributions/ion.cpp`
- Modify: `packages/epcsaft/src/epcsaft/native/eos/residual/cppad/association.h`
- Modify: `packages/epcsaft/src/epcsaft/native/eos/residual/cppad/born.h`
- Modify: `packages/epcsaft/src/epcsaft/native/eos/residual/cppad/contributions.h`
- Modify: `packages/epcsaft/src/epcsaft/native/eos/residual/cppad/hard_chain_dispersion.h`
- Modify: `packages/epcsaft/src/epcsaft/native/eos/residual/cppad/ionic.h`
- Modify: `packages/epcsaft/src/epcsaft/native/eos/residual/cppad/state.h`
- Modify: `packages/epcsaft/src/epcsaft/native/eos/residual/helmholtz.cpp`
- Modify: `packages/epcsaft/src/epcsaft/native/eos/residual/implicit_association/sensitivities.cpp`
- Modify: `packages/epcsaft/src/epcsaft/native/eos/residual/implicit_association/sensitivities.h`
- Modify: `packages/epcsaft/src/epcsaft/native/eos/residual/property_derivatives.cpp`
- Modify: `packages/epcsaft/src/epcsaft/native/eos/residual/thermodynamic_properties.cpp`
- Modify: `packages/epcsaft/src/epcsaft/native/eos/properties/activity.cpp`
- Modify: `packages/epcsaft/src/epcsaft/native/eos/properties/chemical_potential.cpp`
- Modify: `packages/epcsaft/src/epcsaft/native/eos/properties/compressibility.cpp`
- Modify: `packages/epcsaft/src/epcsaft/native/eos/properties/density.cpp`
- Modify: `packages/epcsaft/src/epcsaft/native/eos/properties/fugacity.cpp`
- Modify: `packages/epcsaft/src/epcsaft/native/eos/derivatives/backend_labels.h`
- Modify: `packages/epcsaft/src/epcsaft/native/eos/derivatives/parameters/phase_parameters.cpp`
- Modify: `packages/epcsaft/src/epcsaft/native/eos/derivatives/parameters/pure_neutral.cpp`
- Modify: `packages/epcsaft/src/epcsaft/native/eos/derivatives/phase/association_corrections.cpp`
- Modify: `packages/epcsaft/src/epcsaft/native/eos/derivatives/phase/local_helmholtz_derivatives.cpp`
- Modify: `packages/epcsaft/src/epcsaft/native/eos/derivatives/phase/pressure_derivatives.cpp`
- Modify: `packages/epcsaft/src/epcsaft/native/eos/derivatives/phase/state_sensitivities.cpp`
- Modify: `packages/epcsaft/tests/api/frontend/test_mixture.py`
- Modify: `packages/epcsaft/tests/api/frontend/test_state_properties.py`
- Modify: `packages/epcsaft/tests/native/contracts/test_provider_api_contract.py`

**Interfaces:**

- Consumes: `ResolvedModelInput` and version-1 native record.
- Produces: `Mixture.resolved_model_input`, `Mixture.configuration_receipt`,
  `State.evaluated_model_input`, `State.configuration_receipt`, and native
  provider constructors accepting only `EvaluatedModelInput.native_handle`.

- [ ] **Step 1: Add RED bypass and state-receipt tests.**

  Assert `Mixture(parameters)` fails, `Mixture.from_folder` requires `model_configuration.json`, `Mixture.native` is absent, `ePCSAFTMixture.from_params(mapping)` is absent, state composition must be finite/nonnegative/normalized in exact component order, and two states retain different T/x receipts.

- [ ] **Step 2: Verify RED.**

  Run:

  ```bash
  uv run --no-sync pytest -q \
    packages/epcsaft/tests/api/frontend/test_mixture.py \
    packages/epcsaft/tests/api/frontend/test_state_properties.py \
    packages/epcsaft/tests/api/frontend/test_model_configuration_receipt.py \
    packages/epcsaft/tests/native/contracts/test_provider_api_contract.py \
    packages/epcsaft/tests/native/contracts/test_resolved_native_input_contract.py
  ```

  Expected: current default/bypass paths fail the new assertions.

- [ ] **Step 3: Cut the frontend and native call graph.**

  Perform this step on the M3 provider stack, not directly on `main`. The resulting provider commit is the base for both consumer leaves and must not merge alone.

  The constructor flow becomes:

  ```python
  class Mixture:
      def __init__(self, parameters: ParameterSet, *, model_options: ModelOptions, components=None):
          self.resolved_model_input = ResolvedModelInput.resolve(
              parameters,
              model_options,
              components=components,
          )
          self._runtime_mixture = ePCSAFTMixture(self.resolved_model_input)

  class State:
      def __init__(self, mixture: Mixture, *, T: float, x: Sequence[float], **closure):
          self.evaluated_model_input = mixture.resolved_model_input.evaluate(
              temperature=T,
              composition=x,
          )
          self._runtime = mixture._runtime_mixture.state(
              evaluated_input=self.evaluated_model_input.native_handle,
              **closure,
          )
          if self._runtime.configuration_fingerprint() != self.evaluated_model_input.snapshot_fingerprint_sha256:
              raise RuntimeError("native state did not consume the evaluated provider input")
  ```

  `State.configuration_receipt` returns
  `self.evaluated_model_input.receipt`. Preserve the public thermodynamic
  closure API, but remove condition-free native access, reverse receipt
  reconstruction from runtime dictionaries, and every mapping overload.

- [ ] **Step 4: Replace native argument reads with resolved snapshot reads.**

  Update native contribution/property/derivative owners to consume the evaluated snapshot consistently. Do not change governing EOS equations or derivative backend selection. When a failure appears, trace the old argument field to its exact resolved field before editing.

- [ ] **Step 5: Delete displaced serializers and run GREEN.**

  Delete `state/native_payload.py`, remove serializer imports/helpers from `native_adapter.py`, and run the Task 6 command after a provider-only rebuild. Expected: focused frontend/native contracts pass with no raw-map route.

- [ ] **Step 6: Refactor and checkpoint.**

  Keep state scalar/composition validation in `state/input_validation.py` and native record evaluation in the model owner. Commit all Task 6 provider files on the M3 stack, and mark the commit as integration-blocked by the M4/M5 leaves:

  ```bash
  git add packages/epcsaft/src packages/epcsaft/tests
  git commit -m "refactor(provider): make state resolved input the only native path"
  ```

### Task 7: Migrate Provider Tests And Prove Source-Backed Property/Derivative Continuity

**Use Cases:**

- Provider tests construct explicit configurations through one support helper rather than a production default.
- Neutral, associating, and electrolyte property/derivative checks use traceable retained records and name the retained plot/table evidence.
- Existing equation/CppAD behavior remains characterized after the input cutover without changing scientific thresholds or capability claims.
- A test with incomplete source identity is stopped and routed to M6 instead of receiving invented data.

**Files:**

- Modify: `packages/epcsaft/tests/support/hydrocarbon_cases.py`
- Modify: `packages/epcsaft/tests/support/native_cases.py`
- Modify: `packages/epcsaft/tests/support/runtime_cases.py`
- Modify: `packages/epcsaft/tests/support/model_configurations.py`
- Modify: `packages/epcsaft/tests/native/state/test_association_parameter_derivative_validation.py`
- Modify: `packages/epcsaft/tests/native/state/test_born_parameter_derivatives.py`
- Modify: `packages/epcsaft/tests/native/state/test_contributions.py`
- Modify: `packages/epcsaft/tests/native/state/test_eos_contributions.py`
- Modify: `packages/epcsaft/tests/native/state/test_fugacity_derivatives.py`
- Modify: `packages/epcsaft/tests/native/state/test_phase_state_sensitivities.py`
- Modify: `packages/epcsaft/tests/native/state/test_pressure_density.py`
- Modify: `packages/epcsaft/tests/native/state/test_pressure_derivatives.py`
- Modify: `packages/epcsaft/tests/native/state/test_properties.py`
- Modify: `packages/epcsaft/tests/native/contracts/test_association_implicit_derivative_contract.py`
- Modify: `packages/epcsaft/tests/native/contracts/test_derivative_coverage_matrix.py`
- Modify: `packages/epcsaft/tests/native/contracts/test_property_derivative_backend_contract.py`

**Interfaces:**

- Consumes: explicit configuration/parameter fixtures, existing retained source data and plots, provider state/property/derivative APIs.
- Produces: `explicit_neutral_model_configuration()`, explicit electrolyte configuration fixtures with exact records, and focused proof that provider results retain state receipt fingerprints.

- [ ] **Step 1: Add RED assertions to the three representative cases.**

  For each case, assert the returned state/result carries the expected definition fingerprint, exact T/x receipt, evaluated record IDs, and CppAD backend label. Record the corresponding retained plot/table path in fixture metadata.

- [ ] **Step 2: Verify RED on a fresh provider build.**

  Run:

  ```bash
  uv run --no-sync python scripts/dev/build_epcsaft.py --clean --profile provider --parallel 1
  uv run --no-sync pytest -q \
    packages/epcsaft/tests/api/frontend/test_state_properties.py \
    packages/epcsaft/tests/native/state/test_association_parameter_derivative_validation.py \
    packages/epcsaft/tests/native/state/test_born_parameter_derivatives.py \
    packages/epcsaft/tests/native/contracts/test_derivative_coverage_matrix.py
  ```

  Expected: failures identify provider fixtures still using raw mappings or results missing receipt identity. If a scientific input cannot be traced to the retained source artifacts, stop that case and open the M6 blocker rather than changing a value.

- [ ] **Step 3: Migrate provider fixtures without adding defaults.**

  Convert each provider test to schema-3 records plus an explicit version-1 configuration. Structural-only native tests may use named contract records; any test calculating predictions uses only the three retained evidence families listed above.

- [ ] **Step 4: Run the focused GREEN slice and broader provider native suite.**

  Run:

  ```bash
  uv run --no-sync pytest -q \
    packages/epcsaft/tests/api/frontend/test_state_properties.py \
    packages/epcsaft/tests/native/state \
    packages/epcsaft/tests/native/contracts
  ```

  Expected: all collected provider state/native contracts pass. No M4/M5 route test is part of this command.

- [ ] **Step 5: Refactor duplicated test setup and checkpoint.**

  Keep one explicit fixture builder in `tests/support/model_configurations.py`; do not move it into production code.

  ```bash
  git add packages/epcsaft/tests
  git commit -m "test(provider): prove resolved input across provider cases"
  ```

### Task 8: Publish The SDK Contract And Coordinate The Provider/Consumer Cutover

**Use Cases:**

- An M4 or M5 worker can discover the version-1 resolved-input contract without importing provider-private serializers.
- Provider docs teach only `model_configuration.json`, state-time evaluation, and receipts.
- Repository guards prevent retired option filenames and serializers from returning.
- Paper migrations remain separate nonblocking M6 leaves; the M3 tracking
  parent closes from the provider proof plus both consumer integration leaves,
  without waiting for any paper bundle to become executable.

**Files:**

- Modify: `packages/epcsaft/src/epcsaft/runtime/provider_sdk.py`
- Modify: `packages/epcsaft/src/epcsaft/runtime/core.py`
- Modify: `packages/epcsaft/src/epcsaft/native_sdk/provider_native_sdk_v1/__init__.py`
- Modify: `packages/epcsaft/src/epcsaft/native_sdk/provider_native_sdk_v1/epcsaft_provider_sdk.cmake`
- Modify: `packages/epcsaft/src/epcsaft/native_sdk/provider_native_sdk_v1/provider_sources.json`
- Modify: `docs/contracts/provider_api_v1.md`
- Modify: `docs/contracts/provider_native_sdk_v1.md`
- Modify: `docs/adr/0001-architecture-deepening-public-api-boundaries.md`
- Modify: `docs/adr/0002-hard-public-api-reset-cppad-only-frontend.md`
- Modify: `CONTEXT.md`
- Modify: `docs/superpowers/PROJECT_CONTEXT.md`
- Modify: `docs/pages/user_options.rst`
- Modify: `docs/pages/parameter_schema.rst`
- Modify: `docs/pages/user_parameter_templates.rst`
- Modify: `docs/pages/project_structure.rst`
- Modify: `docs/pages/package_guide.rst`
- Modify: `docs/pages/api_reference.rst`
- Modify: `docs/pages/native_debugging.rst`
- Modify: `tests/workflows/repo/test_package_extension_boundary.py`
- Modify: `tests/workflows/repo/test_project_structure.py`
- Modify: `tests/workflows/repo/test_run_pytest.py`

**Interfaces:**

- Consumes: complete M3 provider stack, provider SDK v1 discovery, and integration-ready M4/M5 consumer commits.
- Produces: SDK metadata for resolved-input schema version 1, global
  model-configuration schema discovery with empty presets, user documentation,
  structural absence gates, one verified combined cutover revision, and a list
  of nonblocking M6 paper follow-ups.

- [ ] **Step 1: Write RED SDK/docs/absence tests.**

  Assert SDK discovery names the resolved-input contract/version, capabilities remain global-only, docs contain no canonical `ParameterSet.to_runtime_dict()` language, project structure names only `model_configuration.json`, and source scans find none of the replaced paths.

- [ ] **Step 2: Verify RED.**

  Run:

  ```bash
  uv run --no-sync pytest -q \
    packages/epcsaft/tests/api \
    packages/epcsaft/tests/native/contracts \
    tests/workflows/repo/test_package_extension_boundary.py \
    tests/workflows/repo/test_project_structure.py \
    tests/workflows/repo/test_run_pytest.py
  ```

  Expected: failures identify stale SDK/docs/structure claims or remaining serializer references.

- [ ] **Step 3: Update SDK and user-facing contracts.**

  Add resolved-input schema/version and public discovery names to provider SDK
  metadata, including the frozen `EvaluatedModelInput` result contract with its
  read-only native handle and detached receipt access. Document the explicit
  neutral/electrolyte JSON shapes, T/x evaluation, receipt retrieval, empty
  initial preset catalog, and M4/M5 consumer ownership. Remove all retired path
  guidance rather than adding redirects.

- [ ] **Step 4: Gate the integration on both consumer leaves without editing sibling code here.**

  The M3 tracking parent must remain blocked by:

  ```text
  M4 leaf: consume provider resolved-input SDK v1 in epcsaft-equilibrium
  M5 leaf: consume provider resolved-input SDK v1 in epcsaft-regression
  ```

  The M4 and M5 leaves each produce a reviewed commit based on the M3 provider stack. Build the final integration revision by applying the provider stack and both consumer commits in dependency order. These consumer files are owned by their own plans; this plan only verifies their contract tests and refuses M3 closure until they pass.
  M6 paper leaves may consume the combined cutover afterward, but they are not
  blockers or subissues of the M3 closure gate; record their current failures
  separately without adding defaults here.

- [ ] **Step 5: Run the complete focused proof.**

  Run:

  ```bash
  uv run --no-sync python scripts/dev/build_epcsaft.py --clean --profile provider --parallel 1
  uv run --no-sync pytest -q packages/epcsaft/tests
  uv run --no-sync pytest -q \
    packages/epcsaft-equilibrium/tests/contracts/test_provider_resolved_input_integration.py \
    packages/epcsaft-regression/tests/contracts/test_provider_resolved_input_integration.py
  uv run --no-sync pytest -q \
    tests/workflows/repo/test_package_extension_boundary.py \
    tests/workflows/repo/test_project_structure.py \
    tests/workflows/repo/test_run_pytest.py
  uv run --no-sync ruff check packages/epcsaft/src packages/epcsaft/tests
  uv run --no-sync python scripts/dev/validate_project.py docs
  git diff --check
  bash "$HOME/.codex/hooks/codex-cleanup.sh" --repo-root .
  ```

  Expected: provider build, both consumer contract tests, and all named docs/lint/diff/cleanup checks exit zero on the combined revision. Any paper-specific failure outside these commands is reported under its M6 leaf and does not trigger a provider default.

- [ ] **Step 6: Run replaced-path absence scans.**

  ```bash
  rg -n 'user_options\.json|model_options\.json|runtime_options|to_runtime_dict|_runtime_payload|create_struct' \
    packages/epcsaft/src packages/epcsaft/tests CONTEXT.md docs/pages docs/contracts
  ```

  Expected: no executable/documented retired path remains in the provider. Historical specs/issues/releases may retain dated history outside this live-surface scan. Run the M4/M5 consumer plans' corresponding absence scans before integration.

- [ ] **Step 7: Refactor final docs/test wording and checkpoint.**

  ```bash
  git add \
    packages/epcsaft/src/epcsaft/runtime \
    packages/epcsaft/src/epcsaft/native_sdk \
    packages/epcsaft/src/epcsaft/native_sdk/provider_native_sdk_v1/provider_sources.json \
    docs/contracts/provider_api_v1.md \
    docs/contracts/provider_native_sdk_v1.md \
    docs/adr/0001-architecture-deepening-public-api-boundaries.md \
    docs/adr/0002-hard-public-api-reset-cppad-only-frontend.md \
    CONTEXT.md docs/superpowers/PROJECT_CONTEXT.md docs/pages \
    tests/workflows/repo/test_package_extension_boundary.py \
    tests/workflows/repo/test_project_structure.py \
    tests/workflows/repo/test_run_pytest.py
  git commit -m "docs(provider): publish resolved model input contract"
  ```

## Proof Oracle

```bash
uv run --no-sync python scripts/validate_plan_task_use_cases.py --plan-path docs/superpowers/plans/2026-07-10-m3-eos-versioned-state-resolved-model-input-plan.md
uv run --no-sync python scripts/validate_plan_outcome_proof.py --plan-path docs/superpowers/plans/2026-07-10-m3-eos-versioned-state-resolved-model-input-plan.md
uv run --no-sync python scripts/dev/build_epcsaft.py --clean --profile provider --parallel 1
uv run --no-sync pytest -q packages/epcsaft/tests
uv run --no-sync pytest -q packages/epcsaft-equilibrium/tests/contracts/test_provider_resolved_input_integration.py packages/epcsaft-regression/tests/contracts/test_provider_resolved_input_integration.py
uv run --no-sync pytest -q tests/workflows/repo/test_package_extension_boundary.py tests/workflows/repo/test_project_structure.py tests/workflows/repo/test_run_pytest.py
uv run --no-sync ruff check packages/epcsaft/src packages/epcsaft/tests
uv run --no-sync python scripts/dev/validate_project.py docs
git diff --check
bash "$HOME/.codex/hooks/codex-cleanup.sh" --repo-root .
```
