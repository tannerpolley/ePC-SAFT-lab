# Stage 4 Provider Resolved-Input Boundary Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace every live provider model-input default, serializer, mutable native argument record, equilibrium reconstruction path, and regression serializer dependency with one source-bearing, state-evaluated, immutable provider input and a cross-extension const handle, without changing equations, derivatives, public equilibrium routes, regression capability, or numerical policy.

**Architecture:** M3 parses one strict version-1 model configuration and schema-3 scientific definition graph, evaluates that graph at exact canonical T/composition conditions, and owns `ResolvedNativeInput`, `NativeEvaluatedInputSnapshot`, `ProviderResolvedInputHandleV1`, deterministic receipts, and the only Python compiler. M4 retains one evaluated provider object through configure/structure/solve and migrates all 25 characterized native intakes to its const handle. A bounded M5 gate must first prove that the existing approved typed fitted-parameter overlay can consume an immutable provider baseline without mapping reconstruction; otherwise the stage stops before the incompatible cutover. All runtime commits remain on one local integration stack until the combined M3+M4+M5 revision is green and can fast-forward `main` atomically.

**Tech Stack:** Python 3.13, frozen dataclasses, canonical JSON and SHA-256, NumPy, C++17, pybind11, CppAD, Ceres 2.2, Ipopt, CMake/Ninja, pytest through `run_pytest.py`, Ruff, Sphinx, `uv`, YAML receipts, and Git.

## Global Constraints

- Governing design: `docs/superpowers/specs/2026-07-13-m3-m4-stage-4-provider-resolved-input-boundary-design.md`.
- M3 owns `packages/epcsaft/**`, provider SDK files, provider tests, and provider docs. M4 owns `packages/epcsaft-equilibrium/**` and its preservation manifest. The only M5 authority is the explicitly approved contract-only consumer/feasibility leaf in `packages/epcsaft-regression/**`.
- Start from committed `main` and create local branch `codex/stage4-resolved-input-stack`. Do not merge or fast-forward this branch to `main` until Tasks 1-10 are green on one revision. Do not push.
- Keep M3, M4, and M5 changes in separate owner commits even though they share the integration stack.
- The primary worker owns every Git write, CMake/native build, clean/reconfigure action, integration decision, cleanup, and final receipt. Subagents may implement non-overlapping source slices or perform read-only review, but they do not run coordinated native rebuilds.
- Model configuration schema is exactly `epcsaft.model-configuration` version `1`; the only filename is `model_configuration.json`; the initial preset catalog is empty; zero-argument construction, missing configuration, implicit booleans, partial formulations, and retired filenames fail.
- `ParameterSet` is exactly `epcsaft.parameter-set` version `3` and owns scientific definitions only. It does not own runtime policy, formulation selection, T, composition, topology inference, or serialization.
- Dependency signatures and validity domains are distinct. Every active record names every independent variable it uses. Unknown dependency identity is invalid and makes trial-phase invariance false.
- The exact native names are `ResolvedNativeInput`, `NativeEvaluatedInputSnapshot`, and `ProviderResolvedInputHandleV1`. Do not substitute `ResolvedNativeInputSnapshot` or another carrier name.
- `ProviderResolvedInputHandleV1` owns `std::shared_ptr<const NativeEvaluatedInputSnapshot>`. M3, M4, and M5 take its const snapshot view. No consumer reconstructs `add_args`, calls a Python mapping serializer, recursively unwraps `_native`, or copies fields into another model structure.
- Temperature, composition, density, and other EOS state variables remain live equation/CppAD variables. A state-dependent scientific record in an already admitted provider/route combination must use definition-backed AD or complete chain-rule derivatives through the route's required order; missing derivative coverage stops Stage 4. Early rejection is permitted only for a combination already classified closed or unsupported by the committed capability/preservation evidence.
- State composition uses one provider canonicalizer. It validates the existing normalized vector and preserves it byte-for-byte; it does not renormalize, floor, clip, reorder, or insert a component.
- M4 alone normalizes route composition, once, in the existing order: shape/finiteness/nonnegativity, division by positive sum, existing minimum-composition check. M3 only validates the resulting vector.
- Bubble pressure evaluates the provider at specified liquid `x`; dew pressure at specified vapor `y`; scoped pure VLE at `[1.0]`. Each M4 disposition row declares every solve-varying independent variable; route-polymorphic selector rows declare the exact set per route. M4 rejects before NLP construction when the selected set intersects provider `affected_record_ids`; `trial_phase_composition_invariant` remains the public composition-specific summary, not a substitute for temperature or other dependency checks.
- M4 public routes remain exactly `bubble_pressure`, `dew_pressure`, and scoped methane/ethane/propane `single_component_vle`. No activation, solver, derivative, proof, or development-family state changes.
- The M5 leaf preserves capability rows, public target kinds, bounds, residual definitions, optimizer, derivative policy, and acceptance. If immutable-baseline adaptation needs a new compiler, new public workflow, target reinterpretation, or mutable snapshot, stop Stage 4 before Task 6 and request separate M5 design approval.
- Existing scientific prediction, equation, derivative, implicit-association, Ipopt, activation, local-NLP, electroneutrality, CE-schema, and postsolve tests remain. Only tests tied solely to the retired input/default contract may be replaced or deleted.
- New Stage 4 tests are contract, identity, derivative-continuity, or mutation tests. They do not create new literature predictions or plots. Reuse retained source-backed cases and their existing plots whenever a model prediction is evaluated.
- Do not repair Khudaida, Gross 2002, MEA, HELD, HELD2, CE, CPE, or another paper program. Task 8 may make only the explicitly listed input-construction migration needed to keep already-required proof callers executable; it must not change their data, equations, tolerances, expected outputs, or evidence classification. Record existing blockers under their current M6/M4 owner.
- Do not add defaults, aliases, public compatibility wrappers, duplicate owners, fake parameters, inferred source records, a writable evaluated handle, or capability expansion. The only temporary exception on the unmerged integration stack is the exact private, tagged, caller-allowlisted legacy parity path specified in Tasks 1-2; it preserves the pre-edit implementation without new behavior, rejects strict v1/v3 objects, and is deleted in Task 6 immediately after the Task 5 gate.
- Use `uv run --no-sync python run_pytest.py ...`, not direct `pytest`.
- After every file-changing checkpoint run `git diff --check` and `bash "$HOME/.codex/hooks/codex-cleanup.sh" --repo-root .`. Remove only task-owned ignored paths.

---

## Source Evidence

- Approved Stage 4 design: `docs/superpowers/specs/2026-07-13-m3-m4-stage-4-provider-resolved-input-boundary-design.md`.
- Parent program: `docs/superpowers/specs/2026-07-12-m4-equilibrium-source-faithful-recovery-and-curated-migration.md` and its 12-stage implementation plan.
- Existing M3 design/plan: `docs/superpowers/specs/2026-07-10-m3-eos-versioned-state-resolved-model-input.md` and `docs/superpowers/plans/2026-07-10-m3-eos-versioned-state-resolved-model-input-plan.md`.
- Existing M4 consumer plan: `docs/superpowers/plans/2026-07-10-m4-equilibrium-provider-resolved-input-sdk-v1-consumer-plan.md`.
- Approved M5 typed compiler/parameter records: `docs/superpowers/specs/2026-07-10-m5-regression-traceable-native-problem-contract.md` and Task 2/3 of `docs/superpowers/plans/2026-07-10-m5-regression-traceable-native-problem-contract-plan.md`.
- Current provider duplicate owners are `model/options.py`, `model/parameters.py`, `model/datasets.py`, `frontend/mixture.py`, `state/native_payload.py`, `state/native_adapter.py`, `native/model/native_types.h`, and `native/model/parameter_setup.cpp`.
- Current provider schema is version 2 and `ParameterSet.to_runtime_dict()` plus `ParameterSource.to_runtime_dict()` emit mutable runtime mappings.
- Current provider binding exposes writable `_core.NativeArgs`, constructs `_core.NativeMixture(add_args)`, exposes `_native_args_payload()`, and constructs `_core.NativeState` from a condition-free mixture.
- Current M4 `register_bindings.cpp` uses `native_args_from_mixture_object()` to copy 47 provider fields and accepts `_native_args_payload`, recursive `_native`, or a native-mixture cast. It has 25 affected intakes recorded in the Stage 4 design.
- Current public `Equilibrium` passes `mixture.native` separately into configure, structure, and solve.
- Current M5 `native_adapter.py` imports `check_association` and `create_struct`; `core.py` calls `ParameterSource.to_runtime_dict()`; native Ceres copies and mutates pure, association, electrolyte, and interaction fields at every fitted iteration.
- Current M5 public free functions do not all own a configured `Mixture`. The feasibility gate must prove that the already approved typed compiler supplies the required immutable baseline without inventing a strict model configuration.
- Current source does not yet contain the approved M5 `targets.py`, `controls.py`, `parameters.py`, `problem.py`, `CompiledRegressionProblem`, or `NativeRegressionProblem` prerequisites. Therefore execution from this revision is expected to stop at Task 5 Step 3 unless those already designed M5 Tasks 1-3 receive separate execution approval and land first.
- Stage 3 preservation evidence is `docs/superpowers/milestones/M4-equilibrium/equilibrium-preservation-manifest.yaml`, `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/capability_evidence.py`, and `packages/epcsaft-equilibrium/tests/contracts/test_equilibrium_ownership_map.py`.
- Retained numerical evidence is already owned by provider/equilibrium tests for neutral, associating, and electrolyte cases; this stage does not regenerate paper evidence.

## Test Complete And Metrics

Stage 4 is test-complete only when one committed integration revision proves all of these outcomes:

1. Strict configuration mutation tests reject missing/unversioned/partial/conflicting/unknown input, retired filenames, duplicate JSON keys, non-boolean booleans, inactive extra fields, direct construction, and every preset request against the empty catalog.
2. Schema-3 record tests prove source identity, units, separate domains, fail-closed dependency signatures, structural-zero evidence, typed correlations, no loader-time evaluation, and no runtime policy/T/x/serializer fields.
3. Native tests account for every former `add_args` model field, expose only read-only snapshot/handle identity, reject raw maps, and prove identical canonical inputs have identical receipt bytes/fingerprints while one mutation per scientific family changes the snapshot fingerprint.
4. Cross-extension tests pass one provider-created `ProviderResolvedInputHandleV1` into separately built M4 and M5 modules, retain it after Python receipt objects are deleted, and echo schema/version/component/T/composition/fingerprint identity without mapping conversion.
5. `Mixture` requires explicit `ModelOptions`; `State` evaluates once at exact canonical T/x; native state reports the same snapshot fingerprint; no condition-free public native escape or serializer remains.
6. Correlation-sensitive derivative oracles prove value and complete chain-rule parity through every derivative order used by current provider/M4 APIs; density and trial composition remain live variables. Missing coverage for an admitted combination stops the stage rather than withdrawing it.
7. The refreshed M4 manifest assigns all 25 intakes their approved disposition, complete solve-varying independent-variable set or selector route map, and proof owner. Every retained intake accepts the provider handle or fails closed only for combinations already classified unsupported; no preserved component silently disappears.
8. Public M4 configure/structure/solve reuse one object/fingerprint, expose the full detached receipt only as `Equilibrium.provider_input_receipt`, attach exact native `provider_input_identity` to diagnostics, reject mismatch before dispatch, preserve receipt-backed active-family/ionic/association/source admission including the exact Gross-2002 exception, and retain current route/numerical/activation behavior.
9. The M5 gate and leaf, if feasible, prove immutable-baseline fitted iteration for every currently supported target kind and preserve capability/target/bound/residual/optimizer/derivative/acceptance bytes. If infeasible, Task 6 never starts and Stage 4 remains incomplete.
10. Live-source absence scans find no retired filenames/default tables, runtime dictionaries, `to_runtime_dict`, `_runtime_payload`, `create_struct`, writable `NativeArgs`, `_native_args_payload`, M4 field reconstruction/fallbacks, or M5 serializer import.
11. Provider, M4, and M5 focused builds/tests pass on one revision; provider/equilibrium/regression capabilities differ only by the approved nested provider schema discovery.
12. The final receipt records source/native identity, exact commits, proof commands, review outcomes, deferred paper blockers, cleanup result, and `push_performed: false`.

## Outcome Proof

**Intent:** Make every provider, equilibrium, and bounded regression calculation consume one explicit, source-traceable model definition evaluated at its exact conditions, with no hidden default or reconstructed payload.
**Current Behavior:** Provider policy and scientific records are mixed across default-bearing Python objects and runtime mappings; native arguments are writable; M4 reconstructs 47 fields through fallbacks; M5 serializes and mutates those fields during Ceres iteration.
**Expected Outcome:** M3 alone resolves and evaluates model input, M4 and M5 retain a provider-owned const handle, unsupported dynamic-input routes fail before solver construction, and equations/capabilities/numerical policy remain unchanged.
**Target Output:** Strict schema parser, schema-3 scientific records and dependency metadata, immutable native definition/snapshot/handle, deterministic Python receipts, provider frontend/native hard cutover, 25-intake M4 migration, bounded M5 consumer proof, displaced-path deletion, SDK/docs updates, and a Stage 4 receipt.
**Owner:** M3 owns provider records and native SDK; M4 owns every equilibrium intake and result receipt; M5 owns only the approved feasibility/consumer leaf; M6 retains paper-evidence blockers.
**Interface:** `ModelOptions.from_user_options`, `ParameterSet`, `ResolvedModelInput.resolve`, `ResolvedModelInput.evaluate`, `EvaluatedModelInput.native_handle/receipt/snapshot_fingerprint_sha256`, `ProviderResolvedInputHandleV1`, `Mixture`, `State`, `Equilibrium.provider_input_receipt`, M4 `provider_input_identity`, and the approved typed M5 fitted-parameter overlay.
**Cutover:** Build all commits on `codex/stage4-resolved-input-stack`, pass the M5 gate before deletion, then verify provider hard cutover plus separate M4/M5 commits together and fast-forward `main` only from the combined green revision.
**Replaced Path:** Default/unversioned model options, `ParameterSet.runtime_options`, runtime-dictionary emission, loader-time T/x evaluation, association topology inference for native construction, `state/native_payload.py`, writable `NativeArgs`, condition-free `Mixture.native`, M4 field copies/fallbacks/classification, and M5 serializer imports.
**Evidence:** RED/GREEN mutation tests, field-accounting tables, canonical receipt hashes, cross-extension lifetime probes, M4 25-row disposition proof, M5 immutable-baseline parity, existing property/derivative and public-route suites, capability byte comparisons, SDK/source identity, absence scans, Ruff, strict docs, diff checks, cleanup, and independent code/scientific reviews.
**Acceptance Proof:** One combined revision builds all three packages; public bubble/dew/scoped pure VLE and existing regression lanes pass with exact provider fingerprints; correlation derivatives retain chain-rule parity; all displaced paths are absent; capabilities are unchanged except nested provider discovery; and the committed receipt identifies every proof and owner commit.
**Stop Criteria:** Stop before Task 6 if M5 cannot obtain explicit configuration plus an immutable baseline through its already approved typed compiler, or if adaptation changes targets/residuals/optimizer/derivatives/acceptance. Stop any later slice on unknown dependency identity, missing source/domain data, unaccounted native fields, lost chain-rule terms, numerical drift, a second serializer, or a writable handle.
**Avoid:** Do not add presets, new defaults, inferred values, mutable snapshots, mapping fallbacks, public/final compatibility wrappers, duplicate compilers, solver tuning, paper repair, route activation, capability admission, or a broad M5 workflow redesign. Do not extend the exact temporary tagged parity path beyond its Tasks 1-2 caller allowlists or retain it after Task 6.
**Risk:** The hard reset deliberately exposes incomplete paper bundles and the current mismatch between strict provider configuration and legacy M5 free functions; hiding either defect would make receipts reproducible-looking while preserving scientifically ambiguous input.

## Implementation Boundaries

**Files To Create:** Provider configuration/correlation/source-bundle/resolved-input modules; native resolved-input definition/evaluator/bindings; provider input-validation/support fixtures/tests; M4/M5 provider-handle integration tests; a bounded M5 resolved-input adapter only if the feasibility gate proves it mechanical; and `docs/superpowers/milestones/M4-equilibrium/stage-4-provider-resolved-input-boundary-receipt.yaml`.
**Files To Modify:** Provider model/frontend/state/native/runtime/SDK/CMake/tests/docs; M4 public workflow, binding intake, native owners, result bridge, tests, SDK metadata, and preservation manifest; M5 native adapter/Ceres binding/tests only within the approved consumer leaf; repository structure/package-boundary tests and live provider docs.
**Files To Avoid:** Paper-validation analyses except the exact Task 8 input-construction-only Gross generator list; retained plot/data artifacts, M6 evidence mathematics/results, regression targets/bounds/loss/solver policy, M4 activation tables except byte-equivalence assertions, release metadata, remotes, branches/stashes not created by this stage, and the paused experimental branch.
**Source Of Truth:** The approved Stage 4 design, M3/M5 approved contracts, ADR 0002/0005, schema-3 typed source records, provider native equation owners, Stage 3 preservation manifest, and current executable capability/derivative tests.
**Read Path:** Parse `model_configuration.json`; parse source definitions without evaluating them; resolve one ordered definition graph; evaluate exact T/canonical composition; read the immutable provider snapshot through its owned handle; consume its detached receipt for identity only.
**Write Path:** Construct immutable in-memory records and canonical receipt JSON; pass const handles into native algorithms; write only source-controlled tests/docs/manifests and the final YAML receipt. Do not rewrite paper bundles or fitted datasets.
**Integration Points:** Provider root exports/type stubs/capabilities, provider native SDK manifest/CMake target, `Mixture`/`State`, EOS/CppAD/implicit derivatives, M4 selector and 25 binding intakes, M4 results, M5 Ceres problem intake, package extension builds, docs, and repository structural tests.
**Migration Or Cutover:** Complete additive schema/native/receipt work and both cross-extension probes on the local stack; run the M4/M5 pre-cutover gates; then make the incompatible provider deletion, M4 migration, and M5 leaf separate commits; verify the full stack; fast-forward `main` once.
**Replaced Path Handling:** Delete the final caller and displaced owner in the same integration stack; remove empty folders and live references; add structural guards; retain no alias, redirect, warning-only compatibility period, or test-only production fallback.
**Acceptance Proof Gate:** Do not fast-forward `main` or mark Stage 4 complete until M5 feasibility is green, all three owner commits coexist on one passing source revision, all 25 M4 rows are accounted for, capability bytes meet the allowed delta, live absence scans are empty, independent reviews approve, cleanup passes, and the final receipt is committed.

## Decision Ledger

| Decision | Evidence | Selected answer | Consequence | Deferred? | Owner |
| --- | --- | --- | --- | --- | --- |
| Runtime branch | Approved design requires a green integration stack | `codex/stage4-resolved-input-stack`, then one fast-forward | `main` never carries a provider-only break | No | Integration |
| Configuration | Current defaults/retired filenames | Strict schema v1, explicit formulation, empty presets | Missing policy fails | No | M3 |
| Parameters | Current schema 2 carries runtime options | Schema 3 scientific definitions and fail-closed dependencies | No serializer on `ParameterSet` | No | M3 |
| Native boundary | Four compilers and writable `add_args` | Definition, immutable evaluated snapshot, owned const handle | One compiler/identity | No | M3 |
| Dynamic derivatives | Pre-evaluation can drop chain-rule terms | Definition-backed AD, complete carried derivatives, or reject | Point parity alone cannot pass | No | M3 |
| M4 unknown phase | Partner composition varies during solve | Admit only provider-classified invariant inputs | Reject before NLP otherwise | No | M3/M4 |
| M4 closed components | Stage 3 preservation manifest | Migrate all 25 intakes by disposition | No implicit retirement | No | M4 |
| M5 mutation | Ceres mutates model fields | Prove approved typed overlay on const baseline first | New compiler/workflow needs separate approval | Conditional | M5 |
| Capability | Representation-only stage | Only nested provider contract/schema discovery may differ | Activation/targets/solvers stay byte-equal | No | M3/M4/M5 |
| Paper failures | Missing or failed source programs | Record existing M6/M4 blockers | No core repair | Yes | M6/M4 |
| Tests | User approved retired-contract replacement | Preserve scientific tests; replace only displaced-contract assertions | No tolerance tuning | No | All |

## Execution Dependency Graph

```text
Task 1 strict configuration
          |
Task 2 schema-3 definitions/dependencies
          |
Task 3 native definition/snapshot/handle + M4/M5 ABI probes
          |
Task 4 Python resolver/receipts
          |
Task 5 M4 inventory + M5 immutable-baseline feasibility
          |
          +-- BLOCKED -> stop before incompatible cutover; request separate execution approval for the already designed M5 Tasks 1-3 prerequisites
          |
          v
Task 6 provider frontend/native hard cutover
          |
Task 7 provider derivative/SDK/docs proof
          |
Task 8 M4 25-intake/public-route cutover
          |
Task 9 bounded M5 consumer cutover
          |
Task 10 combined proof, review, receipt, fast-forward main
```

## Execution Stack Protocol

- [ ] Confirm the approved plan commit is on clean `main`, then create the local stack:

  ```bash
  git status --short --branch
  git switch -c codex/stage4-resolved-input-stack
  ```

  Expected: clean status before the switch; the new branch points at the approved plan commit.

- [ ] Before each task, invoke `chemical-engineer`, `code-intelligence-ladder`, and `superpowers:test-driven-development`. For unexpected failures invoke `superpowers:systematic-debugging`. Before every completion claim invoke `superpowers:verification-before-completion`.

- [ ] Keep commits in task order. Do not rebase, squash, push, or fast-forward `main` during Tasks 1-9.

- [ ] Before every command containing `build_epcsaft.py --clean`, run this non-mutating coordination check and proceed only when it reports no live repo build and no active Ninja lock:

  ```bash
  uv run --no-sync python scripts/dev/build_epcsaft.py --status
  ```

  If another owned build is active, wait for that exact process. Do not delete `.ninja_lock`, kill broad process names, or start a concurrent clean build.

### Task 1: Add The Strict Version-1 Model Configuration Boundary Without Breaking The Parity Oracle

**Use Cases:**

- A neutral caller supplies an explicit disabled-electrostatics formulation and receives one deterministic configuration receipt.
- An electrolyte caller supplies every enabled/disabled formulation field explicitly with strict JSON types.
- Missing configuration, direct construction, retired filenames, duplicate keys, unknown keys, partial choices, conflicting preset/formulation input, and preset selection are rejected before parameter resolution.
- Strict public parsing and discovery are additive on the local stack. Existing provider/M5 execution remains temporarily isolated behind one private tagged legacy-options path so Task 5 can characterize it; the public hard cutover and deletion occur in Task 6.

**Files:**

- Create: `packages/epcsaft/src/epcsaft/model/configuration_catalog.py`
- Create: `packages/epcsaft/tests/api/frontend/test_model_configuration_receipt.py`
- Create: `packages/epcsaft/tests/api/package/test_model_configuration_capabilities.py`
- Modify: `packages/epcsaft/src/epcsaft/model/options.py`
- Modify: `packages/epcsaft/src/epcsaft/model/datasets.py`
- Modify: `packages/epcsaft/src/epcsaft/frontend/mixture.py`
- Modify: `packages/epcsaft/src/epcsaft/model/__init__.py`
- Modify: `packages/epcsaft/src/epcsaft/__init__.py`
- Modify: `packages/epcsaft/src/epcsaft/__init__.pyi`
- Modify: `packages/epcsaft/src/epcsaft/runtime/core.py`

**Interfaces:**

- Produces `MODEL_CONFIGURATION_SCHEMA = "epcsaft.model-configuration"`, `MODEL_CONFIGURATION_SCHEMA_VERSION = 1`, `MODEL_CONFIGURATION_FILENAME = "model_configuration.json"`, `MODEL_CONFIGURATION_PRESETS: tuple[str, ...] = ()`, strict `ModelOptions.from_user_options(value)`, detached `ModelOptions.receipt`, and global schema discovery with `admitted_presets == []`.
- Direct dataclass construction of `ModelOptions` is closed with `@dataclass(frozen=True, slots=True, init=False)`.
- Temporarily retains the exact current option conversion as private tagged variant `LegacyRuntimeOptionsState` plus `ModelOptions._from_stage4_legacy_runtime_options(...)` and `ModelOptions._to_stage4_legacy_runtime_options(...)`. Only `frontend/mixture.py` and `model/datasets.py` may call them; strict v1 instances raise if passed to either method, and no root export, stub, capability, or documentation exposes them.

- [ ] **Step 1: Write RED parser and discovery tests.**

  Use this complete explicit neutral fixture; it contains no omitted dependent policy:

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

  Parameterize one mutation per missing key, wrong schema/version type, duplicate JSON key, non-boolean `enabled`, unknown top/nested key, inactive extra field, incomplete enabled field set, `preset_id`, and retired `user_options.json`/`model_options.json`. Assert `ModelOptions()` raises `TypeError` and two receipt accesses are detached. Add a structural caller test proving the two private legacy methods are called only from `frontend/mixture.py` and `model/datasets.py`, reject a strict v1 instance, and reproduce the pre-edit canonical runtime-options bytes for the retained neutral/electrolyte characterization fixtures.

- [ ] **Step 2: Run RED.**

  ```bash
  uv run --no-sync python run_pytest.py \
    packages/epcsaft/tests/api/frontend/test_model_configuration_receipt.py \
    packages/epcsaft/tests/api/package/test_model_configuration_capabilities.py -q
  ```

  Expected: feature-specific failures show the current default constructor, permissive parser, retired filenames, and missing discovery contract. Import/build failures do not count as RED.

- [ ] **Step 3: Implement the strict records and parser.**

  The public owner has this shape; each enabled formulation record has exact required keys and no dataclass defaults:

  ```python
  @dataclass(frozen=True, slots=True, init=False)
  class ModelOptions:
      schema: str
      schema_version: int
      selection_origin: Literal["explicit_configuration", "admitted_preset"]
      preset_id: str | None
      electrostatics: DisabledFormulation | ElectrostaticsOptions
      relative_permittivity: DisabledFormulation | RelativePermittivityOptions
      debye_huckel: DisabledFormulation | DebyeHuckelOptions
      born: DisabledFormulation | BornModelOptions
      solvated_ion_diameter: DisabledFormulation | SolvatedIonDiameterOptions
      ion_dispersion: DisabledFormulation | IonDispersionOptions

      @classmethod
      def from_user_options(
          cls,
          value: str | Path | Mapping[str, Any] | "ModelOptions",
      ) -> "ModelOptions":
          return _parse_model_configuration(value)

      @property
      def receipt(self) -> dict[str, Any]:
          return json.loads(_canonical_model_options_json(self))
  ```

  Parse JSON with an `object_pairs_hook` that rejects duplicate keys. A directory must contain exactly `model_configuration.json`; either retired filename is a loud error even when the canonical file also exists. Keep fixed CppAD implementation policy out of the user schema.

  Move the exact pre-edit permissive/default conversion body, without edits, into the private `LegacyRuntimeOptionsState` factory/accessor and update only the two allowlisted existing callers. This is a transient parity oracle on the local stack, not a public compatibility API. It accepts only its private legacy tag; `ModelOptions.from_user_options` and every strict v1 object can never reach it.

- [ ] **Step 4: Add global discovery without instance policy.**

  `model_configuration_capabilities()` returns fresh containers with schema/version/filename and an empty preset list. `epcsaft.capabilities()` may nest this discovery but must not report an instance's active formulation.

- [ ] **Step 5: Run GREEN, Ruff, diff, and cleanup.**

  ```bash
  uv run --no-sync python run_pytest.py \
    packages/epcsaft/tests/api/frontend/test_model_configuration_receipt.py \
    packages/epcsaft/tests/api/package/test_model_configuration_capabilities.py -q
  uv run --no-sync ruff check \
    packages/epcsaft/src/epcsaft/model/configuration_catalog.py \
    packages/epcsaft/src/epcsaft/model/options.py \
    packages/epcsaft/tests/api/frontend/test_model_configuration_receipt.py \
    packages/epcsaft/tests/api/package/test_model_configuration_capabilities.py
  git diff --check
  bash "$HOME/.codex/hooks/codex-cleanup.sh" --repo-root .
  ```

  Expected: all selected tests and checks exit zero; discovery reports no preset and no active instance policy; the private allowlist is exact; strict instances cannot serialize; and legacy characterization bytes are unchanged.

- [ ] **Step 6: Commit the M3 checkpoint on the stack.**

  ```bash
  git add packages/epcsaft/src/epcsaft packages/epcsaft/tests/api/frontend/test_model_configuration_receipt.py packages/epcsaft/tests/api/package/test_model_configuration_capabilities.py
  git commit -m "feat(provider): require strict model configuration"
  ```

### Task 2: Add Schema-3 Scientific Records As Source-Bearing, Dependency-Explicit, And Policy-Free

**Use Cases:**

- A scientific record round-trips source identity, units, structural-zero evidence, validity domain, and a separate exact dependency signature.
- Constant, temperature-dependent, and admitted composition-dependent correlations evaluate only inside their sourced domains and expose derivatives through the order required by their consumers.
- Source-bundle loading selects records without nominal T, equal composition, expression evaluation, or runtime policy insertion.
- Schema 3 itself has no runtime-options serializer and its strict loader rejects version-2 input. The existing version-2 runtime serializer/parser remains isolated as the sole tagged legacy execution/parity path on the local integration stack through Task 5; it is not callable from schema 3 and is deleted only in the coordinated Task 6/9 cutover after the M5 gate passes.

**Files:**

- Create: `packages/epcsaft/src/epcsaft/model/correlations.py`
- Create: `packages/epcsaft/src/epcsaft/model/source_bundles.py`
- Create: `packages/epcsaft/tests/api/frontend/test_parameter_correlations.py`
- Create: `packages/epcsaft/tests/api/frontend/test_formulation_records.py`
- Create: `packages/epcsaft/tests/api/frontend/test_parameter_set_ownership.py`
- Create: `packages/epcsaft/tests/api/frontend/test_source_bundle_loading.py`
- Modify: `packages/epcsaft/src/epcsaft/model/parameters.py`
- Modify: `packages/epcsaft/src/epcsaft/model/datasets.py`
- Modify: `packages/epcsaft/src/epcsaft/model/sources.py`
- Modify: `packages/epcsaft/src/epcsaft/model/validation.py`
- Modify: `packages/epcsaft/src/epcsaft/model/templates.py`
- Modify: `packages/epcsaft/src/epcsaft/frontend/mixture.py`
- Modify: `packages/epcsaft/src/epcsaft/state/native_payload.py`
- Modify: `packages/epcsaft/src/epcsaft/model/__init__.py`
- Modify: `packages/epcsaft/src/epcsaft/__init__.py`
- Modify: `packages/epcsaft/tests/api/frontend/test_interaction_provenance.py`
- Modify: `packages/epcsaft/tests/api/frontend/test_parameter_input_integrity.py`
- Modify: `packages/epcsaft/tests/api/frontend/test_templates.py`

**Interfaces:**

- Produces `PARAMETER_SET_SCHEMA_VERSION = 3`, `IndependentVariable`, `DependencySignature`, `TemperatureDomain`, optional composition-domain records, typed correlation variants, source-bearing pure/formulation/interaction records, and `SourceBundleSelection`.
- Canonical `ParameterSet` keys are exactly `schema`, `schema_version`, `components`, `pure_records`, `formulation_records`, `interactions`, `interaction_policies`, and `metadata`.
- During the additive gate phase, `ParameterSet` has a private immutable schema-origin tag. `ParameterSet.from_schema3(...)` and `SourceBundleSelection` create only `scientific_v3`; the unchanged legacy `ParameterSource.to_parameter_set(...)`/`load_parameter_set(...)` create only `legacy_v2_gate`. `_to_stage4_legacy_runtime_dict(...)` accepts only the latter and is called only by `ParameterSource.to_runtime_dict`, `model/datasets.py`, `model/validation.py`, and `state/native_payload.py`. A schema-3 object raises before serialization.

- [ ] **Step 1: Write RED ownership, dependency, correlation, and bundle tests.**

  The strict schema-3 loader rejects version 2, `runtime_options`, `T`, `x`, model-choice keys, unknown dependencies, domain-as-dependency inference, free-form expressions, invalid units/bases/domains, duplicate records, missing provenance, unsourced zeros, missing strict configuration, loader-time evaluation, and retired template filenames. Assert loaders preserve correlation definitions at two distinct requested conditions without evaluating either. Add a structural test for the exact four legacy serializer callers, byte parity on all retained Task 5 fixtures, and rejection when any schema-3 object reaches the legacy method.

- [ ] **Step 2: Run RED.**

  ```bash
  uv run --no-sync python run_pytest.py \
    packages/epcsaft/tests/api/frontend/test_parameter_correlations.py \
    packages/epcsaft/tests/api/frontend/test_formulation_records.py \
    packages/epcsaft/tests/api/frontend/test_parameter_set_ownership.py \
    packages/epcsaft/tests/api/frontend/test_source_bundle_loading.py \
    packages/epcsaft/tests/api/frontend/test_interaction_provenance.py \
    packages/epcsaft/tests/api/frontend/test_parameter_input_integrity.py \
    packages/epcsaft/tests/api/frontend/test_templates.py -q
  ```

  Expected: failures identify schema 2, runtime policy storage, missing dependency identity, early evaluation, and retired template output.

- [ ] **Step 3: Implement dependency and correlation records.**

  Use closed independent-variable tokens and keep domains separate:

  ```python
  class IndependentVariable(StrEnum):
      TEMPERATURE_K = "temperature_K"
      MOLE_FRACTION = "mole_fraction"
      MOLAR_DENSITY = "molar_density"
      PRESSURE_PA = "pressure_Pa"

  @dataclass(frozen=True, slots=True)
  class DependencySignature:
      variables: tuple[IndependentVariable, ...]
      composition_components: tuple[str, ...] = ()

      def __post_init__(self) -> None:
          if len(set(self.variables)) != len(self.variables):
              raise InputError("dependency variables must be unique")
          if IndependentVariable.MOLE_FRACTION in self.variables and not self.composition_components:
              raise InputError("composition dependency requires explicit component identities")
          if IndependentVariable.MOLE_FRACTION not in self.variables and self.composition_components:
              raise InputError("composition component identities require a mole-fraction dependency")

  @dataclass(frozen=True, slots=True)
  class TemperatureDomain:
      minimum_K: float
      maximum_K: float
      evidence: DomainEvidence

      def validate(self, temperature_K: Real) -> float:
          value = float(temperature_K)
          if not np.isfinite(value) or not self.minimum_K <= value <= self.maximum_K:
              raise InputError("temperature is outside the sourced record domain")
          return value
  ```

  Admit only the locally sourced typed families already named by the M3 plan: constant, reference-temperature linear, logarithmic-temperature, constant-plus-exponential, piecewise quadratic, and exact sourced composition forms. Every record has stable `record_id`, source locator, units, domain, and dependency signature. Each nonconstant record implements value plus the exact derivative order used by current APIs.

- [ ] **Step 4: Make schema-3 `ParameterSet` and bundle loading definitions-only while quarantining the legacy parity path.**

  Schema-3 objects reject `runtime_options`, expose no `to_runtime_dict()`, perform no runtime option normalization or native matrix emission, contain no default option table, and perform no loader-time T/x evaluation. Keep `ParameterSource.to_runtime_dict()` as the sole public legacy gate used by current provider/M5 execution, delete `frontend/mixture.py::_runtime_payload`, and route that legacy mixture construction through `ParameterSource` without changing canonical bytes. Move all direct provider serialization behind `_to_stage4_legacy_runtime_dict(...)`. Preserve the exact pre-edit version-2 parser, runtime-option normalization, native matrix emission, and default tables under the private `legacy_v2_gate` tag; do not change their bytes or admit a new direct caller. `scientific_v3` rejects before `ParameterSource` or the private method. Implement:

  ```python
  @dataclass(frozen=True, slots=True)
  class SourceBundleSelection:
      parameter_set: ParameterSet
      model_options: ModelOptions
      source_files: tuple[Path, ...]

      def pure_record(self, component: str, field: str) -> ScientificRecord:
          return _require_unique_pure_record(self.parameter_set, component, field)

      def interaction_record(self, family: str, left: str, right: str) -> InteractionRecord:
          return _require_unique_interaction_record(self.parameter_set, family, left, right)
  ```

  Templates write unresolved `parameter_set.json` plus `model_configuration.json`; they do not populate a runnable default.

- [ ] **Step 5: Run GREEN, Ruff, diff, and cleanup.**

  ```bash
  uv run --no-sync python run_pytest.py \
    packages/epcsaft/tests/api/frontend/test_parameter_correlations.py \
    packages/epcsaft/tests/api/frontend/test_formulation_records.py \
    packages/epcsaft/tests/api/frontend/test_parameter_set_ownership.py \
    packages/epcsaft/tests/api/frontend/test_source_bundle_loading.py \
    packages/epcsaft/tests/api/frontend/test_interaction_provenance.py \
    packages/epcsaft/tests/api/frontend/test_parameter_input_integrity.py \
    packages/epcsaft/tests/api/frontend/test_templates.py -q
  uv run --no-sync ruff check packages/epcsaft/src/epcsaft/model packages/epcsaft/tests/api/frontend
  git diff --check
  bash "$HOME/.codex/hooks/codex-cleanup.sh" --repo-root .
  ```

  Expected: all selected tests/checks pass; no schema-3 source loader evaluates T/composition or emits runtime policy; strict objects cannot reach the legacy gate; the caller allowlist is exact; and characterized legacy provider/M5 tests still produce byte-identical serializer output needed by Task 5.

- [ ] **Step 6: Commit the M3 checkpoint.**

  ```bash
  git add packages/epcsaft/src/epcsaft/model packages/epcsaft/src/epcsaft/frontend/mixture.py packages/epcsaft/src/epcsaft/state/native_payload.py packages/epcsaft/src/epcsaft/__init__.py packages/epcsaft/tests/api/frontend
  git commit -m "refactor(provider): separate scientific definitions from runtime input"
  git status --short --branch
  ```

  Expected: the Task 2 checkpoint is clean; `frontend/mixture.py` has no second serializer; schema-3 input is rejected by every legacy provider/M5 path.

### Task 3: Add The Immutable Native Definition, Evaluated Snapshot, Const Handle, And Cross-Extension ABI

**Use Cases:**

- Native provider code evaluates one typed definition graph into one immutable snapshot containing every former model field and its source/dependency/native-consumer evidence.
- Provider EOS kernels gain one provider-owned, read-only parameter-access seam that can read either the immutable snapshot or the still-active legacy `add_args` object without copying; both paths execute the same kernels and are parity-tested before the legacy intake is removed.
- A provider-created `ProviderResolvedInputHandleV1` survives detached-receipt deletion and is consumed by separately built M4 and M5 extensions through one shared C++ type.
- Raw mappings, writable bindings, consumer-side copies, schema mismatch, missing fields, unknown dependencies, and unaccounted old fields fail.
- This additive checkpoint proves the replacement ABI before the incompatible provider constructor and serializer are removed.

**Files:**

- Create: `packages/epcsaft/src/epcsaft/native/model/resolved_input.h`
- Create: `packages/epcsaft/src/epcsaft/native/model/resolved_input.cpp`
- Create: `packages/epcsaft/src/epcsaft/native/model/resolved_input_evaluator.h`
- Create: `packages/epcsaft/src/epcsaft/native/model/provider_parameter_access.h`
- Create: `packages/epcsaft/src/epcsaft/model/_resolved_input_native.py`
- Create: `packages/epcsaft/src/epcsaft/native/bindings/resolved_input_binding_internal.h`
- Create: `packages/epcsaft/src/epcsaft/native/bindings/resolved_input_bindings.h`
- Create: `packages/epcsaft/src/epcsaft/native/bindings/resolved_input_bindings.cpp`
- Create: `packages/epcsaft/src/epcsaft/native/bindings/resolved_input_record_bindings.cpp`
- Create: `packages/epcsaft/tests/native/contracts/test_resolved_native_input_contract.py`
- Create: `packages/epcsaft-equilibrium/tests/contracts/test_provider_resolved_input_handle_abi.py`
- Create: `packages/epcsaft-regression/tests/contracts/test_provider_resolved_input_handle_abi.py`
- Modify: `packages/epcsaft/src/epcsaft/native/model/native_types.h`
- Modify: `packages/epcsaft/src/epcsaft/native/model/parameter_setup.cpp`
- Modify: `packages/epcsaft/src/epcsaft/native/eos/core_internal.h`
- Modify: `packages/epcsaft/src/epcsaft/native/eos/contributions/association.cpp`
- Modify: `packages/epcsaft/src/epcsaft/native/eos/contributions/born.cpp`
- Modify: `packages/epcsaft/src/epcsaft/native/eos/contributions/contribution_internal.h`
- Modify: `packages/epcsaft/src/epcsaft/native/eos/contributions/dispersion.cpp`
- Modify: `packages/epcsaft/src/epcsaft/native/eos/contributions/hard_chain.cpp`
- Modify: `packages/epcsaft/src/epcsaft/native/eos/contributions/ion.cpp`
- Modify: `packages/epcsaft/src/epcsaft/native/eos/derivatives/parameters/phase_parameters.cpp`
- Modify: `packages/epcsaft/src/epcsaft/native/eos/derivatives/parameters/pure_neutral.cpp`
- Modify: `packages/epcsaft/src/epcsaft/native/eos/derivatives/backend_labels.h`
- Modify: `packages/epcsaft/src/epcsaft/native/eos/derivatives/phase/association_corrections.cpp`
- Modify: `packages/epcsaft/src/epcsaft/native/eos/derivatives/phase/local_helmholtz_derivatives.cpp`
- Modify: `packages/epcsaft/src/epcsaft/native/eos/derivatives/phase/pressure_derivatives.cpp`
- Modify: `packages/epcsaft/src/epcsaft/native/eos/derivatives/phase/state_sensitivities.cpp`
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
- Modify: `packages/epcsaft/src/epcsaft/native/eos/state.cpp`
- Modify: `packages/epcsaft/src/epcsaft/native/bindings/module.cpp`
- Modify: `packages/epcsaft/src/epcsaft/native/bindings/payload_converters.cpp`
- Modify: `packages/epcsaft/src/epcsaft/native/bindings/payload_converters.h`
- Modify: `packages/epcsaft/src/epcsaft/_core.pyi`
- Modify: `packages/epcsaft/CMakeLists.txt`
- Modify: `packages/epcsaft/src/epcsaft/native_sdk/provider_native_sdk_v1/provider_sources.json`
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/module.cpp`
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/_native_core.pyi`
- Modify: `packages/epcsaft-equilibrium/cmake/equilibrium_native_sources.json`
- Modify: `packages/epcsaft-regression/src/epcsaft_regression/native/regression/module.cpp`
- Modify: `packages/epcsaft-regression/src/epcsaft_regression/_native_core.pyi`

**Interfaces:**

- Produces provider-owned `ResolvedNativeInput`, `NativeEvaluatedInputSnapshot`, and `ProviderResolvedInputHandleV1` with schema ID `epcsaft.resolved-model-input`, schema version `1`, and read-only pybind identity properties.
- Produces internal `ProviderParameterAccessV1<Scalar>` kernels plus non-copying legacy/snapshot adapters. Existing `add_args` signatures remain the sole active provider/M5 path only through Task 5, call the shared kernels through the legacy adapter, and expose no new public compatibility API.
- M4 and M5 expose contract-only `_native_provider_resolved_input_handle_probe(handle)` during this additive checkpoint; each returns identity read from the same const snapshot and never accepts a dict.

- [ ] **Step 1: Write provider field-accounting and cross-extension RED tests first.**

  Provider tests cover immutable construction, explicit disabled formulations, exact components/T/composition, dependency grouping, `trial_phase_composition_invariant`, record/source/structural-zero evidence, association topology fingerprint, active residual/ionic classifications, raw-map rejection, read-only properties, one mutation per pure/association/interaction/dielectric/ion/Born/solvation family, and a table accounting for every current `add_args` member by snapshot field or same-checkpoint consumer deletion. Add a legacy-adapter versus snapshot-adapter matrix covering residual Helmholtz contributions, pressure/density, fugacity, pure/association/binary/electrolyte parameter derivatives, and every target kind listed by Task 5 at the existing tolerances.

  M4/M5 ABI tests create one provider handle, delete all Python receipt dictionaries, call both extension probes repeatedly, and assert exact schema/version/component/T/composition/definition/snapshot fingerprint identity. Passing the detached receipt dict must raise `TypeError`.

- [ ] **Step 2: Build all three extensions and confirm RED.**

  ```bash
  uv run --no-sync python scripts/dev/build_epcsaft.py --clean --profile full --parallel 1
  uv run --no-sync python scripts/dev/build_extension_dists.py --mode monorepo --parallel 1
  uv run --no-sync python run_pytest.py \
    packages/epcsaft/tests/native/contracts/test_resolved_native_input_contract.py \
    packages/epcsaft-equilibrium/tests/contracts/test_provider_resolved_input_handle_abi.py \
    packages/epcsaft-regression/tests/contracts/test_provider_resolved_input_handle_abi.py -q
  ```

  Expected: feature-specific build/test failures show the native records, carrier, and extension probes are absent. Dependency/toolchain failures are diagnosed separately.

- [ ] **Step 3: Implement the exact native records and carrier.**

  Use value records and const ownership; this is the complete public identity skeleton and contains no writable member binding:

  ```cpp
  struct EvaluatedRecordEvidence {
      std::string record_id;
      std::string scientific_source_id;
      std::vector<std::string> dependency_signature;
      std::vector<double> evaluated_value;
      std::vector<std::string> derivative_variable_order;
      int carried_derivative_order{0};
      bool definition_backed_ad{false};
      std::vector<double> first_derivatives;
      std::vector<double> second_derivatives_row_major;
      std::string native_field;
      std::string native_consumer;
  };

  using NativeCorrelationDefinitionV1 = std::variant<
      NativeConstantCorrelationV1,
      NativeReferenceTemperatureLinearCorrelationV1,
      NativeLogTemperatureCorrelationV1,
      NativeConstantPlusExponentialTermsCorrelationV1,
      NativePiecewiseQuadraticTemperatureCorrelationV1,
      NativeSaltFreeWaterMoleFractionCubicPermittivityCorrelationV1
  >;

  struct NativeStateDependentDefinitionV1 {
      std::string record_id;
      NativeDependencySignatureV1 dependency_signature;
      NativeCorrelationDefinitionV1 correlation;
  };

  struct NativeStateDependentDefinitionGraphV1 {
      std::vector<NativeStateDependentDefinitionV1> records;
  };

  struct NativeEvaluatedInputSnapshot {
      std::string contract_id{"provider_resolved_input_handle_v1"};
      std::string schema{"epcsaft.resolved-model-input"};
      int schema_version{1};
      std::string definition_fingerprint_sha256;
      std::string snapshot_fingerprint_sha256;
      std::vector<std::string> component_order;
      double temperature_K{0.0};
      std::string composition_basis{"mole_fraction"};
      std::vector<double> canonical_composition;
      std::vector<EvaluatedRecordEvidence> evaluated_records;
      NativeStateDependentDefinitionGraphV1 state_dependent_definitions;
      std::map<std::string, std::vector<std::string>> affected_record_ids;
      bool trial_phase_composition_invariant{false};
      std::vector<std::string> active_residual_families;
      std::vector<int> ionic_component_indices;
      std::string association_topology_fingerprint_sha256;
      std::vector<StructuralZeroEvidence> structural_zeros;
      std::vector<std::string> scientific_source_classifications;
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
      NativeFormulation formulation;
      std::map<std::string, NativeFieldReference> native_mapping;
  };

  struct ResolvedNativeInput {
      NativeInputIdentity identity;
      NativeFormulation formulation;
      NativeParameterGraph parameter_graph;
  };

  class ProviderResolvedInputHandleV1 final {
  public:
      explicit ProviderResolvedInputHandleV1(
          std::shared_ptr<const NativeEvaluatedInputSnapshot> snapshot
      );
      const NativeEvaluatedInputSnapshot& snapshot() const;
      std::shared_ptr<const NativeEvaluatedInputSnapshot> shared_snapshot() const;
  private:
      std::shared_ptr<const NativeEvaluatedInputSnapshot> snapshot_;
  };
  ```

  `ResolvedNativeInput` retains typed correlation definitions and source/dependency evidence. `evaluate_resolved_native_input(...)` validates exact T/canonical composition, evaluates records, copies the closed typed state-dependent definition graph into the immutable snapshot, computes dependency groups/invariance, and constructs a `shared_ptr<const NativeEvaluatedInputSnapshot>`. Native algorithms may therefore evaluate an admitted definition inside an existing AD graph; alternatively they consume complete carried derivative jets. Unknown dependency identity sets no optimistic flag; construction rejects it.

- [ ] **Step 4: Add the non-copying provider parameter-access seam before the M5 gate.**

  Refactor the listed provider EOS kernels so their canonical implementation is parameterized by `ProviderParameterAccessV1<Scalar>`. `LegacyAddArgsParameterAccessV1` returns const reads from the existing `add_args`; `SnapshotParameterAccessV1` returns const reads or typed definition evaluation from `NativeEvaluatedInputSnapshot`; neither constructs or mutates an `add_args`, snapshot, mapping, or second field store. Existing provider functions keep their current signatures on the local stack only by constructing the legacy view and invoking the same kernel. Add a private snapshot-path native probe used by the parity matrix. Task 5's overlay implements this same access contract, so feasibility does not depend on the Task 6 deletion.

- [ ] **Step 5: Add the exact private typed factory and bind the provider carrier read-only.**

  Implement `_resolved_input_native.py::_build_native_resolved_input(selection: SourceBundleSelection, components: tuple[str, ...])` and `_evaluate_native_resolved_input(...)`. They accept only Task 2 typed records, never mappings, and are not exported from the `epcsaft` root. The ABI tests call this exact factory; Task 4 imports it rather than replacing it. Provider pybind exposes only properties returning copied scalars/containers. M4 and M5 include the SDK header and accept `std::shared_ptr<ProviderResolvedInputHandleV1>`:

  ```cpp
  py::dict provider_handle_identity(
      const std::shared_ptr<ProviderResolvedInputHandleV1>& handle
  ) {
      if (!handle) {
          throw ValueError("provider resolved-input handle is required");
      }
      const auto& snapshot = handle->snapshot();
      py::dict out;
      out["contract_id"] = snapshot.contract_id;
      out["schema"] = snapshot.schema;
      out["schema_version"] = snapshot.schema_version;
      out["definition_fingerprint_sha256"] = snapshot.definition_fingerprint_sha256;
      out["snapshot_fingerprint_sha256"] = snapshot.snapshot_fingerprint_sha256;
      out["component_order"] = snapshot.component_order;
      out["temperature_K"] = snapshot.temperature_K;
      out["composition_basis"] = snapshot.composition_basis;
      out["canonical_composition"] = snapshot.canonical_composition;
      return out;
  }
  ```

  Register every new provider source in the canonical SDK manifest and have both consumer build graphs include the same exported header/source identity.

- [ ] **Step 6: Build and run GREEN ABI/field/access proof.**

  Repeat Step 2 and the provider legacy/snapshot parity matrix. Expected: all builds and selected tests pass; both modules echo the same identity after receipt deletion; dict inputs fail; field accounting has no unowned old field; the two non-copying adapters execute the same kernels with parity at every existing tolerance.

- [ ] **Step 7: Commit separate owner checkpoints.**

  ```bash
  git add packages/epcsaft
  git commit -m "feat(provider): add immutable resolved input handle"
  git add packages/epcsaft-equilibrium
  git commit -m "test(equilibrium): prove provider input handle ABI"
  git add packages/epcsaft-regression
  git commit -m "test(regression): prove provider input handle ABI"
  ```

### Task 4: Make `ResolvedModelInput` The Sole Python Compiler And Receipt Owner

**Use Cases:**

- Equivalent canonical definitions produce byte-identical configuration receipts and definition fingerprints.
- Exact T/canonical composition evaluation produces one frozen `EvaluatedModelInput` whose native handle and detached receipt identify the same snapshot.
- Dependency groups, invariance, active families, ionic state, topology, structural zeros, and source classifications survive receipt detachment.
- Raw mappings, `ParameterSet` native construction, second normalization, receipt mutation, missing source data, and out-of-domain conditions fail without changing later evaluation.

**Files:**

- Create: `packages/epcsaft/src/epcsaft/model/resolved_input.py`
- Create: `packages/epcsaft/src/epcsaft/state/input_validation.py`
- Create: `packages/epcsaft/tests/support/model_configurations.py`
- Modify: `packages/epcsaft/src/epcsaft/model/__init__.py`
- Modify: `packages/epcsaft/src/epcsaft/__init__.py`
- Modify: `packages/epcsaft/src/epcsaft/__init__.pyi`
- Modify: `packages/epcsaft/src/epcsaft/_core.pyi`
- Modify: `packages/epcsaft/tests/api/frontend/test_model_configuration_receipt.py`
- Modify: `packages/epcsaft/tests/api/frontend/test_parameter_correlations.py`
- Modify: `packages/epcsaft/tests/api/frontend/test_interaction_provenance.py`
- Modify: `packages/epcsaft/tests/native/contracts/test_resolved_native_input_contract.py`

**Interfaces:**

- Produces `ResolvedModelInput.resolve(parameters, model_options, components=...)`, `configuration_receipt`, `fingerprint_sha256`, `evaluate(temperature=..., composition=...)`, and frozen `EvaluatedModelInput.native_handle/receipt/snapshot_fingerprint_sha256`.
- Consumes the exact private `_build_native_resolved_input` and `_evaluate_native_resolved_input` factory from Task 3; no second Python-to-native compiler is introduced.
- `ResolvedModelInput.evaluate` calls `validate_canonical_composition` and never normalizes.

- [ ] **Step 1: Write RED deterministic identity and copy-safety tests.**

  Cover definition construction order, mapping key order, receipt detachment, source mutation, formulation mutation, T change, composition change, record dependency grouping, unknown dependency failure, structural zeros, active classifications, native mapping, exact canonical vector retention, non-normalized input rejection, and handle/receipt fingerprint mismatch rejection.

- [ ] **Step 2: Run RED.**

  ```bash
  uv run --no-sync python run_pytest.py \
    packages/epcsaft/tests/api/frontend/test_model_configuration_receipt.py \
    packages/epcsaft/tests/api/frontend/test_parameter_correlations.py \
    packages/epcsaft/tests/api/frontend/test_interaction_provenance.py \
    packages/epcsaft/tests/native/contracts/test_resolved_native_input_contract.py -q
  ```

  Expected: failures identify the absent Python resolver/evaluated owner and deterministic receipt APIs.

- [ ] **Step 3: Implement the frozen compiler and evaluated object.**

  ```python
  @dataclass(frozen=True, slots=True, init=False)
  class EvaluatedModelInput:
      definition_fingerprint_sha256: str
      snapshot_fingerprint_sha256: str
      _native_handle: Any
      _receipt_json: str

      @property
      def native_handle(self) -> Any:
          return self._native_handle

      @property
      def receipt(self) -> dict[str, Any]:
          return json.loads(self._receipt_json)

  @dataclass(frozen=True, slots=True, init=False)
  class ResolvedModelInput:
      components: tuple[str, ...]
      fingerprint_sha256: str
      _native_input: Any
      _configuration_receipt_json: str

      @classmethod
      def resolve(
          cls,
          parameters: ParameterSet,
          model_options: ModelOptions,
          *,
          components: Sequence[str] | None = None,
      ) -> "ResolvedModelInput":
          return _compile_resolved_model_input(parameters, model_options, components)

      @property
      def configuration_receipt(self) -> dict[str, Any]:
          return json.loads(self._configuration_receipt_json)

      def evaluate(
          self,
          *,
          temperature: float,
          composition: Sequence[float],
      ) -> EvaluatedModelInput:
          canonical = validate_canonical_composition(composition, len(self.components))
          return _evaluate_resolved_model_input(self, float(temperature), canonical)
  ```

  Canonical JSON uses sorted object keys, stable record order, exact schema/version, component order, configuration, definitions, dependencies, domains, evaluated records, structural zeros, classifications, and native mappings. Snapshot fingerprint input includes exact T and vector bytes represented by the canonical JSON number policy.

- [ ] **Step 4: Implement validation without normalization.**

  `validate_canonical_composition` requires one-dimensional exact length, finite nonnegative values, and `abs(sum(x)-1.0) <= 1e-7`, preserving the current provider tolerance. It returns a copied read-only NumPy array with exactly the submitted values; it does not divide, clip, floor, or reorder.

- [ ] **Step 5: Run GREEN, Ruff, diff, cleanup, and commit.**

  ```bash
  uv run --no-sync python run_pytest.py \
    packages/epcsaft/tests/api/frontend/test_model_configuration_receipt.py \
    packages/epcsaft/tests/api/frontend/test_parameter_correlations.py \
    packages/epcsaft/tests/api/frontend/test_interaction_provenance.py \
    packages/epcsaft/tests/native/contracts/test_resolved_native_input_contract.py -q
  uv run --no-sync ruff check packages/epcsaft/src/epcsaft/model/resolved_input.py packages/epcsaft/src/epcsaft/state/input_validation.py packages/epcsaft/tests/support/model_configurations.py
  git diff --check
  bash "$HOME/.codex/hooks/codex-cleanup.sh" --repo-root .
  git add packages/epcsaft
  git commit -m "feat(provider): resolve state input with deterministic receipts"
  ```

  Expected: all checks pass; receipt mutation does not affect native handle identity or later receipt access.

### Task 5: Pass The M4 Disposition Gate And The M5 Immutable-Baseline Feasibility Gate

**Use Cases:**

- The Stage 3 preservation manifest names every one of the 25 affected M4 bindings, its exact Stage 4 disposition, complete static `solve_varying_independent_variables` or selector `solve_varying_independent_variables_by_route`, retained proof owner, and migration test.
- A native regression probe evaluates every currently production-supported fitted target from one immutable provider baseline plus the already approved typed fitted-parameter overlay, without a Python mapping or snapshot mutation.
- The gate first proves the separately approved M5 Tasks 1-3 prerequisites actually exist: strict `TargetDataset`, `FittedParameter`, `RegressionControls`, `CompiledRegressionProblem`, `compile_regression_problem(...)`, `NativeRegressionProblem`, and ordered evaluated provider handles. Their absence is a deterministic Stage 4 stop, not authority to implement them here.
- Existing and proposed regression paths produce the same target order, residual formulas, bounds, optimizer identity, derivative labels/Jacobian coverage, acceptance fields, and numerical values at existing tolerances.
- If a legacy free function cannot obtain explicit model configuration and a resolved baseline through the approved M5 compiler, the gate records the exact missing authority and stops before the incompatible cutover; the blocker is visible but is not Stage 4 success.

**Files:**

- Modify: `docs/superpowers/milestones/M4-equilibrium/equilibrium-preservation-manifest.yaml`
- Modify: `packages/epcsaft-equilibrium/tests/contracts/test_equilibrium_ownership_map.py`
- Create: `packages/epcsaft-regression/src/epcsaft_regression/native/regression/resolved_input_adapter.h`
- Create: `packages/epcsaft-regression/src/epcsaft_regression/native/regression/resolved_input_adapter.cpp`
- Create: `packages/epcsaft-regression/tests/contracts/test_provider_resolved_input_feasibility.py`
- Create on FAIL only: `docs/superpowers/milestones/M5-regression/stage-4-provider-input-prerequisite-blocker.yaml`
- Create: `packages/epcsaft-equilibrium/tests/contracts/fixtures/stage4_activation_capability_baseline.json`
- Create: `packages/epcsaft-regression/tests/contracts/fixtures/stage4_capability_baseline.json`
- Modify: `packages/epcsaft-regression/src/epcsaft_regression/native/regression/ceres_regression.cpp`
- Modify: `packages/epcsaft-regression/src/epcsaft_regression/native/regression/module.cpp`
- Modify: `packages/epcsaft-regression/src/epcsaft_regression/_native_core.pyi`
- Modify: `packages/epcsaft-regression/CMakeLists.txt`
- Modify: `packages/epcsaft-regression/tests/api/test_regression.py`
- Modify: `packages/epcsaft-regression/tests/native/test_pure.py`
- Modify: `packages/epcsaft-regression/tests/native/test_binary.py`
- Modify: `packages/epcsaft-regression/tests/native/test_liquid_electrolyte.py`

**Interfaces:**

- Adds `checkpoint.stage_4_provider_input_binding_dispositions` to the M4 preservation manifest with exactly 25 rows. Each non-selector row has `solve_varying_independent_variables`; the two route-polymorphic selector rows have `solve_varying_independent_variables_by_route`. No union approximation is allowed.
- Adds contract-only M5 `_native_provider_resolved_input_overlay_feasibility(handle, fitted_parameters, theta, records)` returning baseline/overlay identity, residual/Jacobian parity, target order, and a boolean `mechanical_adaptation_proven`.
- Uses the approved `NativeFittedParameter` meaning from the M5 plan: stable key, target kind, component/pair indices, start, lower, and upper. It does not implement the full future M5 workflow/receipt redesign.
- Reads, but does not create or modify, the prerequisite M5 contract files `targets.py`, `controls.py`, `parameters.py`, `problem.py`, and `native/regression/regression_problem.h`. Implementing those approved M5 Tasks 1-3 requires separate M5 execution approval.

- [ ] **Step 0: Characterize the M5 prerequisite state before any M4 gate edit.**

  Create only `test_provider_resolved_input_feasibility.py` first. Its prerequisite classification checks exact file/type/function ownership and returns either `ready_for_stage4_overlay_gate` or `requires_approved_m5_tasks_1_to_3`; it never treats absence as readiness. On the current source, the test passes only by asserting the exact absent-contract inventory and blocked classification. Run:

  ```bash
  uv run --no-sync python run_pytest.py packages/epcsaft-regression/tests/contracts/test_provider_resolved_input_feasibility.py -q
  git diff --check
  bash "$HOME/.codex/hooks/codex-cleanup.sh" --repo-root .
  ```

  If classified blocked, do not edit the M4 manifest or create native adapter code. Write the conditional M5 blocker YAML with source commit, exact absent files/symbols, test command/result, required separately approved M5 tasks, `stage_4_status: blocked_before_incompatible_cutover`, cleanup result, and `push_performed: false`. Commit the passing characterization test and blocker receipt, verify a clean stack, return to the user, and stop:

  ```bash
  git add packages/epcsaft-regression/tests/contracts/test_provider_resolved_input_feasibility.py docs/superpowers/milestones/M5-regression/stage-4-provider-input-prerequisite-blocker.yaml
  git commit -m "docs(regression): record stage 4 provider input blocker"
  git status --short --branch
  ```

  Continue to Step 1 only when the exact approved prerequisite contracts are present and the classification is `ready_for_stage4_overlay_gate`.

- [ ] **Step 1: Refresh and test the exact M4 binding set.**

  Add a test constant with all affected names and assert it equals both the manifest rows and the live calls to `native_args_from_mixture_object`:

  ```python
  EXPECTED_STAGE_4_BINDINGS = {
      "_native_equilibrium_activation_plan_contract",
      "_native_equilibrium_selector_contract",
      "_native_equilibrium_selector_route_result",
      "_native_activated_neutral_tp_flash_nlp_contract",
      "_native_equilibrium_cloud_shadow_route_result",
      "_native_eos_phase_system",
      "_native_phase_equilibrium_residual_block_contract",
      "_native_neutral_two_phase_eos_nlp_contract",
      "_native_neutral_multiphase_eos_nlp_contract",
      "_native_neutral_two_phase_eos_postsolve",
      "_native_neutral_multiphase_eos_postsolve",
      "_native_neutral_multiphase_fugacity_residual_route_result",
      "_native_neutral_tpd_phase_discovery",
      "_native_associating_single_component_vle_validation_result",
      "_native_eos_phase_block",
      "_native_saturation_block",
      "_native_electrolyte_contribution_block",
      "_native_chemical_equilibrium_nlp_activation:eos_activity",
      "_native_electrolyte_bubble_t_reduced_nlp_probe",
      "_native_electrolyte_bubble_t_route_result",
      "_native_electrolyte_tpd_phase_discovery",
      "_native_electrolyte_held2_continuous_tpd_minimizer",
      "_native_electrolyte_held2_phase_discovery",
      "_native_electrolyte_stage_iii_refinement",
      "_native_electrolyte_postsolve_certification",
  }
  ```

  The following matrix is authoritative; implementation does not derive or widen it. `T`, `x`, `rho`, and `P` below serialize as `temperature_K`, `mole_fraction`, `molar_density`, and `pressure_Pa`.

  | Binding | Disposition | Solve-varying set | Stage 3 owner/item | Focused proof |
  | --- | --- | --- | --- | --- |
  | `_native_equilibrium_activation_plan_contract` | `migrate_public_handle` | `x, rho` | `activation_selector_core`; `local_nlp_ipopt_adapter` | `test_internal_multiphase_activation_contracts.py` |
  | `_native_equilibrium_selector_contract` | `migrate_public_handle` | route-keyed table below | `activation_selector_core` | `test_selector_core_contracts.py` |
  | `_native_equilibrium_selector_route_result` | `migrate_public_handle` | route-keyed table below | `activation_selector_core`; `public_pressure_boundary_routes`; `public_single_component_saturation` | `test_equilibrium.py`; `test_single_component_vle.py` |
  | `_native_activated_neutral_tp_flash_nlp_contract` | `migrate_const_handle_preserve_concept` | `x, rho` | `local_nlp_ipopt_adapter`; `exact_phase_derivative_assembly` | `test_selector_core_contracts.py` |
  | `_native_equilibrium_cloud_shadow_route_result` | `migrate_const_handle_preserve_concept` | `T, x, rho` | `local_nlp_ipopt_adapter`; `neutral_phase_discovery` | `test_cloud_shadow_route_admission_checker.py` |
  | `_native_eos_phase_system` | `migrate_const_handle_preserve_concept` | `x, rho` | `exact_phase_derivative_assembly` | `test_eos_phase_block.py` |
  | `_native_phase_equilibrium_residual_block_contract` | `migrate_const_handle_preserve_concept` | `x, rho` | `exact_phase_derivative_assembly` | `test_phase_equilibrium_residual_block_contract.py` |
  | `_native_neutral_two_phase_eos_nlp_contract` | `migrate_const_handle_preserve_concept` | `x, rho` | `local_nlp_ipopt_adapter`; `exact_phase_derivative_assembly` | new direct case in `test_provider_resolved_input_integration.py` plus both owner proofs |
  | `_native_neutral_multiphase_eos_nlp_contract` | `migrate_const_handle_preserve_concept` | `x, rho` | `local_nlp_ipopt_adapter`; `exact_phase_derivative_assembly` | `test_internal_multiphase_activation_contracts.py` |
  | `_native_neutral_two_phase_eos_postsolve` | `migrate_const_handle_preserve_concept` | `x, rho` | `native_postsolve_certification` | `test_result_builder.py` |
  | `_native_neutral_multiphase_eos_postsolve` | `migrate_const_handle_preserve_concept` | `x, rho` | `native_postsolve_certification` | new direct case in `test_provider_resolved_input_integration.py` |
  | `_native_neutral_multiphase_fugacity_residual_route_result` | `migrate_const_handle_preserve_concept` | `x, rho` | `neutral_phase_discovery`; `local_nlp_ipopt_adapter` | `test_internal_multiphase_activation_contracts.py`; `check_generalized_phase_set.py` |
  | `_native_neutral_tpd_phase_discovery` | `migrate_const_handle_preserve_concept` | `x, rho` | `neutral_phase_discovery` | `test_neutral_lle_reference_values.py`; `check_generalized_phase_set.py` |
  | `_native_associating_single_component_vle_validation_result` | `migrate_const_handle_preserve_concept` | `rho, P` | `association_components`; `local_nlp_ipopt_adapter` | `test_gross_2002_figure01_internal_saturation.py` |
  | `_native_eos_phase_block` | `migrate_const_handle_preserve_concept` | `x, rho` | `exact_phase_derivative_assembly` | `test_eos_phase_block.py` |
  | `_native_saturation_block` | `migrate_const_handle_preserve_concept` | `rho, P` | `public_single_component_saturation`; `exact_phase_derivative_assembly` | `test_single_component_vle_block.py` |
  | `_native_electrolyte_contribution_block` | `migrate_const_handle_preserve_concept` | none; value-only call at explicit state | `electrolyte_counterion_pair_components` | `test_eos_phase_block.py` |
  | `_native_chemical_equilibrium_nlp_activation:eos_activity` | `optional_eos_activity_handle_or_reject` | `x, rho` | `standalone_chemical_equilibrium_components`; retain `failed_nonideal_mea_ce_output` | `test_chemical_equilibrium_eos_activity.py`; `test_standalone_ce_gate.py` |
  | `_native_electrolyte_bubble_t_reduced_nlp_probe` | `migrate_const_handle_preserve_concept` | `T, x, rho` | `electrolyte_counterion_pair_components`; `exact_phase_derivative_assembly` | `test_electrolyte_held2_flash_validation.py` |
  | `_native_electrolyte_bubble_t_route_result` | `migrate_const_handle_preserve_concept` | `T, x, rho` | `electrolyte_counterion_pair_components`; `local_nlp_ipopt_adapter` | `test_electrolyte_held2_flash_validation.py` |
  | `_native_electrolyte_tpd_phase_discovery` | `migrate_const_handle_preserve_concept` | `x, rho` | `electrolyte_counterion_pair_components` | `test_electrolyte_tpd_gate.py` |
  | `_native_electrolyte_held2_continuous_tpd_minimizer` | `migrate_const_handle_preserve_concept` | `x, rho` | `electrolyte_counterion_pair_components` | `test_electrolyte_held2_continuous_tpd.py` |
  | `_native_electrolyte_held2_phase_discovery` | `migrate_const_handle_preserve_concept` | `x, rho` | `electrolyte_counterion_pair_components` | `test_electrolyte_held2_phase_discovery.py` |
  | `_native_electrolyte_stage_iii_refinement` | `migrate_const_handle_preserve_concept` | `x, rho` | `electrolyte_counterion_pair_components`; `local_nlp_ipopt_adapter` | `test_electrolyte_stage_iii_refinement.py` |
  | `_native_electrolyte_postsolve_certification` | `migrate_const_handle_preserve_concept` | `x, rho` | `native_postsolve_certification`; `electrolyte_counterion_pair_components` | `test_electrolyte_postsolve_certification.py` |

  The two selector rows use exactly this route-owned map:

  | Selector route | Solve-varying set |
  | --- | --- |
  | `bubble_pressure` | `x, rho, P` |
  | `dew_pressure` | `x, rho, P` |
  | `bubble_temperature` | `T, x, rho` |
  | `dew_temperature` | `T, x, rho` |
  | `neutral_tp_flash` | `x, rho` |
  | `neutral_lle` | `x, rho` |
  | `single_component_vle` | `rho, P` |

  This route-keyed manifest field is the bounded design choice for selector rows. A static union would wrongly reject temperature-dependent input on fixed-temperature pressure routes; a smaller static set would freeze input on another route.

  Each row must match this disposition, owner, and proof path exactly and must declare the complete state set using the closed provider tokens. The ownership test asserts exact matrix equality, including the two route maps and the two newly direct-tested rows. Composition-varying rows also retain the public `trial_phase_composition_invariant` requirement, but all rows are guarded by exact set intersection with provider `affected_record_ids`.

  Before editing M4 production code, serialize canonical activation plus capabilities into `stage4_activation_capability_baseline.json`. Before editing M5 production code, serialize canonical M5 capabilities into `stage4_capability_baseline.json`. The comparison helper removes only the new nested provider contract/schema discovery fields; every route, activation, target, optimizer, derivative, status, and proof field remains in the byte comparison.

- [ ] **Step 2: Run the M4 disposition RED/GREEN loop.**

  ```bash
  uv run --no-sync python run_pytest.py packages/epcsaft-equilibrium/tests/contracts/test_equilibrium_ownership_map.py -q
  ```

  Expected RED: the new 25-row field is absent. Expected GREEN after the manifest edit: all preservation tests pass, every solve-varying set is explicit, no `preserve_directly` component is retired, and no affected live binding is unlisted.

- [ ] **Step 3: Reconfirm compiled public-entrypoint ownership before adapter code.**

  Extend the Step 0 test to compile every still-public production entrypoint from an explicitly configured `Mixture` and assert the result owns ordered `EvaluatedModelInput.native_handle` objects without a mapping round-trip. Continue only when every public production entrypoint compiles through those exact typed contracts; record the prerequisite commit in the Stage 4 gate evidence. Do not create private substitutes, infer `ModelOptions`, or reinterpret a legacy free-function dataset.

- [ ] **Step 4: On prerequisite PASS only, write the M5 feasibility RED tests before adapter code.**

  Cover the production-supported target set exactly:

  ```python
  PRODUCTION_TARGET_KINDS = (
      "m",
      "s",
      "e",
      "e_assoc",
      "vol_a",
      "d_born",
      "k_ij",
      "l_ij",
      "k_hb_ij",
      "f_solv",
      "dielc",
  )
  ```

  Use existing source-backed pure-neutral, associating pure-neutral, pure-ion, constant-binary interaction, and liquid-electrolyte fixtures. For every fitted iterate used by the tests, compare the current immutable copy-and-mutate path to the handle-plus-overlay probe for ordered raw/scaled residuals, cost, Jacobian shape/values, target indices, bounds, backend labels, and success predicate at the tests' existing tolerances. Every still-public target/entrypoint combination must appear; an omitted combination must cite an already approved closure/removal and prove it is no longer reachable before deletion. Also assert baseline snapshot fingerprint is unchanged before/after every iterate and that no dict or `add_args` is accepted by the new probe.

  Add API tests that trace how `Regression(mixture).fit_pure_neutral`, `fit_binary_parameters`, and `fit_liquid_electrolyte_parameters` obtain an explicit `ModelOptions` plus one `ResolvedModelInput`. A public free function that has no configured mixture/configuration must be classified `requires_approved_m5_tasks_1_to_3`, not supplied a default.

- [ ] **Step 5: Run the M5 feasibility RED slice.**

  ```bash
  uv run --no-sync python scripts/dev/build_epcsaft.py --profile regression --parallel 1
  uv run --no-sync python run_pytest.py \
    packages/epcsaft-regression/tests/contracts/test_provider_resolved_input_feasibility.py \
    packages/epcsaft-regression/tests/api/test_regression.py \
    packages/epcsaft-regression/tests/native/test_pure.py \
    packages/epcsaft-regression/tests/native/test_binary.py \
    packages/epcsaft-regression/tests/native/test_liquid_electrolyte.py -q
  ```

  Expected: the feasibility test fails because the const-baseline adapter is absent and current free paths build provider mappings. Existing scientific regressions must remain green in the RED run.

- [ ] **Step 6: Implement only the already approved typed overlay adapter.**

  The adapter references, but never mutates or copies, the provider snapshot:

  ```cpp
  enum class FittedProviderFieldV1 {
      segment_count,
      sigma_angstrom,
      epsilon_k_K,
      association_energy_K,
      association_volume,
      born_diameter_angstrom,
      k_ij,
      l_ij,
      k_hb_ij,
      solvation_factor,
      pure_relative_permittivity,
  };

  struct NativeFittedParameterOverlayV1 {
      std::string key;
      FittedProviderFieldV1 field;
      int first_index{-1};
      int second_index{-1};
      double start{0.0};
      double lower{0.0};
      double upper{0.0};
  };

  class ResolvedInputOverlayViewV1 final {
  public:
      ResolvedInputOverlayViewV1(
          std::shared_ptr<ProviderResolvedInputHandleV1> baseline,
          std::vector<NativeFittedParameterOverlayV1> parameters,
          const std::vector<double>& theta
      );
      const NativeEvaluatedInputSnapshot& baseline() const;
      double scalar(FittedProviderFieldV1 field, int first, int second) const;
      const std::string& snapshot_fingerprint_sha256() const;
  private:
      std::shared_ptr<ProviderResolvedInputHandleV1> baseline_;
      std::vector<NativeFittedParameterOverlayV1> parameters_;
      const std::vector<double>& theta_;
  };
  ```

  The view implements Task 3's `ProviderParameterAccessV1<Scalar>` contract and supplies fitted scalar access to those shared provider kernels while every fixed field and all source/formulation/dependency identity comes directly from `baseline().snapshot()`. It must not construct `add_args`, a new snapshot, or a map. Reuse existing residual packing and CppAD/implicit derivative owners unchanged.

- [ ] **Step 7: Apply the decisive gate.**

  Run Step 5 again and inspect the API ownership classifications.

  - PASS only if every production-supported target and public production entrypoint reaches an explicit resolved baseline through the already approved typed compiler semantics, all parity assertions pass, and `mechanical_adaptation_proven` is true.
  - FAIL if any entrypoint lacks explicit configuration/baseline, any target needs a new overlay meaning, or any target/residual/bound/optimizer/derivative/acceptance behavior changes.

  On FAIL: do not run Tasks 6-10, do not delete provider serializers, do not fast-forward `main`, and do not claim Stage 4 complete. Remove any uncommitted unsuccessful native adapter implementation with targeted patches, retaining only passing characterization evidence. Commit the valid M4 disposition/baseline checkpoint separately, update or create the M5 blocker YAML with the exact failed target/entrypoint/parity authority, commit the passing blocker characterization plus receipt, run cleanup, and verify a clean stack. Report that the separately approved M5 compiler/workflow work is required; `main` remains at the pre-runtime revision.

- [ ] **Step 8: On PASS only, commit separate M4 and M5 gate checkpoints.**

  ```bash
  git add docs/superpowers/milestones/M4-equilibrium/equilibrium-preservation-manifest.yaml packages/epcsaft-equilibrium/tests/contracts/test_equilibrium_ownership_map.py packages/epcsaft-equilibrium/tests/contracts/fixtures/stage4_activation_capability_baseline.json
  git commit -m "test(equilibrium): map provider input binding dispositions"
  git add packages/epcsaft-regression
  git commit -m "test(regression): prove immutable provider baseline fitting"
  ```

### Task 6: Cut `Mixture`, `State`, And Provider Native Equations To The Resolved Graph

**Use Cases:**

- `Mixture` requires `ParameterSet` plus explicit `ModelOptions`, owns one `ResolvedModelInput`, and exposes a detached definition receipt but no condition-free native model.
- `State` validates one exact canonical T/composition, evaluates once, retains the `EvaluatedModelInput`, constructs native state from its handle, and verifies the native snapshot fingerprint.
- Every provider EOS/property/derivative owner switches from Task 3's parity-tested legacy parameter adapter to its parity-tested immutable snapshot adapter plus live equation variables; no equation, backend selection, or numerical tolerance changes.
- Writable `NativeArgs`, raw-map/native-mixture construction, association topology inference, payload snapshots, runtime dictionaries, and the displaced serializer are deleted on the integration stack.
- The private Task 1 `LegacyRuntimeOptionsState` methods/tag and Task 2 `legacy_v2_gate` parser/serializer/tag are deleted in the same checkpoint; the final source contains only strict v1/v3 ownership.

**Files:**

- Modify: `packages/epcsaft/src/epcsaft/model/options.py`
- Modify: `packages/epcsaft/src/epcsaft/model/parameters.py`
- Modify: `packages/epcsaft/src/epcsaft/model/datasets.py`
- Modify: `packages/epcsaft/src/epcsaft/model/sources.py`
- Modify: `packages/epcsaft/src/epcsaft/model/validation.py`
- Modify: `packages/epcsaft/src/epcsaft/frontend/mixture.py`
- Modify: `packages/epcsaft/src/epcsaft/frontend/state.py`
- Modify: `packages/epcsaft/src/epcsaft/state/native_adapter.py`
- Delete: `packages/epcsaft/src/epcsaft/state/native_payload.py`
- Modify: `packages/epcsaft/src/epcsaft/runtime/core.py`
- Modify: `packages/epcsaft/src/epcsaft/native/bindings/module.cpp`
- Modify: `packages/epcsaft/src/epcsaft/native/model/native_types.h`
- Modify: `packages/epcsaft/src/epcsaft/native/model/parameter_setup.cpp`
- Modify: `packages/epcsaft/src/epcsaft/native/eos/contributions/association.cpp`
- Modify: `packages/epcsaft/src/epcsaft/native/eos/contributions/born.cpp`
- Modify: `packages/epcsaft/src/epcsaft/native/eos/contributions/contribution_internal.h`
- Modify: `packages/epcsaft/src/epcsaft/native/eos/contributions/dispersion.cpp`
- Modify: `packages/epcsaft/src/epcsaft/native/eos/contributions/hard_chain.cpp`
- Modify: `packages/epcsaft/src/epcsaft/native/eos/contributions/ion.cpp`
- Modify: `packages/epcsaft/src/epcsaft/native/eos/core_internal.h`
- Modify: `packages/epcsaft/src/epcsaft/native/eos/derivatives/backend_labels.h`
- Modify: `packages/epcsaft/src/epcsaft/native/eos/derivatives/parameters/phase_parameters.cpp`
- Modify: `packages/epcsaft/src/epcsaft/native/eos/derivatives/parameters/pure_neutral.cpp`
- Modify: `packages/epcsaft/src/epcsaft/native/eos/derivatives/phase/association_corrections.cpp`
- Modify: `packages/epcsaft/src/epcsaft/native/eos/derivatives/phase/local_helmholtz_derivatives.cpp`
- Modify: `packages/epcsaft/src/epcsaft/native/eos/derivatives/phase/pressure_derivatives.cpp`
- Modify: `packages/epcsaft/src/epcsaft/native/eos/derivatives/phase/state_sensitivities.cpp`
- Modify: `packages/epcsaft/src/epcsaft/native/eos/properties/activity.cpp`
- Modify: `packages/epcsaft/src/epcsaft/native/eos/properties/chemical_potential.cpp`
- Modify: `packages/epcsaft/src/epcsaft/native/eos/properties/compressibility.cpp`
- Modify: `packages/epcsaft/src/epcsaft/native/eos/properties/density.cpp`
- Modify: `packages/epcsaft/src/epcsaft/native/eos/properties/fugacity.cpp`
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
- Modify: `packages/epcsaft/src/epcsaft/native/eos/state.cpp`
- Modify: `packages/epcsaft/src/epcsaft/_core.pyi`
- Modify: `packages/epcsaft/src/epcsaft/__init__.pyi`
- Modify: `packages/epcsaft/tests/api/frontend/test_mixture.py`
- Modify: `packages/epcsaft/tests/api/frontend/test_state_properties.py`
- Modify: `packages/epcsaft/tests/native/contracts/test_provider_api_contract.py`
- Modify: `packages/epcsaft/tests/native/contracts/test_resolved_native_input_contract.py`

**Interfaces:**

- Produces `Mixture.resolved_model_input`, `Mixture.configuration_receipt`, `State.evaluated_model_input`, and `State.configuration_receipt`.
- Native provider constructors accept only `std::shared_ptr<ProviderResolvedInputHandleV1>` plus live state/closure values; the handle exposes no mutator and owns `std::shared_ptr<const NativeEvaluatedInputSnapshot>`.

- [ ] **Step 1: Add RED bypass, single-evaluation, and fingerprint tests.**

  Assert `Mixture(parameters)` fails, `Mixture.from_folder` requires the canonical configuration, `Mixture.native` is absent, `ePCSAFTMixture.from_params` is absent, `_core.NativeArgs` is absent, `_core.NativeMixture(mapping)` fails, `LegacyRuntimeOptionsState`, `legacy_v2_gate`, `_from_stage4_legacy_runtime_options`, `_to_stage4_legacy_runtime_options`, and `_to_stage4_legacy_runtime_dict` are absent, schema-2 loading fails, state evaluation occurs exactly once, submitted composition bytes equal receipt bytes, and native state fingerprint equals `EvaluatedModelInput.snapshot_fingerprint_sha256`.

- [ ] **Step 2: Run RED against the additive stack.**

  ```bash
  uv run --no-sync python run_pytest.py \
    packages/epcsaft/tests/api/frontend/test_mixture.py \
    packages/epcsaft/tests/api/frontend/test_state_properties.py \
    packages/epcsaft/tests/native/contracts/test_provider_api_contract.py \
    packages/epcsaft/tests/native/contracts/test_resolved_native_input_contract.py -q
  ```

  Expected: failures identify the current condition-free mixture, writable arguments, serializer, and missing state receipt identity.

- [ ] **Step 3: Cut the Python frontend and runtime adapter.**

  Implement this flow exactly:

  ```python
  class Mixture:
      def __init__(
          self,
          parameters: ParameterSet,
          *,
          model_options: ModelOptions,
          components: Sequence[str] | None = None,
      ) -> None:
          self.resolved_model_input = ResolvedModelInput.resolve(
              parameters,
              model_options,
              components=components,
          )
          self._runtime_mixture = ePCSAFTMixture(self.resolved_model_input)

      @property
      def configuration_receipt(self) -> dict[str, Any]:
          return self.resolved_model_input.configuration_receipt

  class State:
      def __init__(self, mixture: Mixture, *, T: float, x: Sequence[float], **closure: Any) -> None:
          canonical_x = validate_canonical_composition(x, mixture.ncomp)
          self.evaluated_model_input = mixture.resolved_model_input.evaluate(
              temperature=T,
              composition=canonical_x,
          )
          self._runtime = mixture._runtime_mixture.state(
              evaluated_input=self.evaluated_model_input.native_handle,
              temperature=float(T),
              composition=canonical_x,
              **closure,
          )
          if self._runtime.configuration_fingerprint() != self.evaluated_model_input.snapshot_fingerprint_sha256:
              raise RuntimeError("native state did not consume the evaluated provider input")
  ```

  Preserve the current P/rho closure API and errors. Remove mapping overloads, reverse receipt reconstruction, parameter payload properties, and condition-free native access.

- [ ] **Step 4: Make the snapshot adapter the only provider native owner field-for-field.**

  Switch every provider constructor and EOS/property/derivative callsite from Task 3's non-copying `LegacyAddArgsParameterAccessV1` to `SnapshotParameterAccessV1`; remove direct `add_args`/`ePCSAFTMixtureNative` model-input reads. The shared kernels already proved in Task 3 remain unchanged. Each snapshot access selects the exact `NativeEvaluatedInputSnapshot` field or live typed correlation evaluation. Density, T, and composition remain parameters to EOS/CppAD functions. Delete an old member only after its field-accounting row proves its native consumer migrated or was already dead.

- [ ] **Step 5: Delete displaced owners and bindings.**

  Delete `state/native_payload.py`; remove `check_association`, `create_assoc_matrix`, `create_struct`, `_canonical_runtime_parameter_payload`, `ParameterSet.to_runtime_dict`, `ParameterSource.to_runtime_dict`, `LegacyRuntimeOptionsState`, both private Task 1 legacy-option methods, the Task 2 `legacy_v2_gate` tag/parser/serializer, Task 3's now-displaced legacy parameter adapter, `_core.NativeArgs`, `_native_args_payload`, writable model-field bindings, and raw-map/native-mixture constructors. Make the strict schema-3 loader the sole `ParameterSet` loader and remove every temporary allowlist assertion in favor of final absence assertions. Remove now-empty imports/folders and update type stubs/SDK manifests in the same commit.

- [ ] **Step 6: Fresh-build provider and run GREEN.**

  ```bash
  uv run --no-sync python scripts/dev/build_epcsaft.py --clean --profile provider --parallel 1
  uv run --no-sync python run_pytest.py \
    packages/epcsaft/tests/api/frontend/test_mixture.py \
    packages/epcsaft/tests/api/frontend/test_state_properties.py \
    packages/epcsaft/tests/native/contracts/test_provider_api_contract.py \
    packages/epcsaft/tests/native/contracts/test_resolved_native_input_contract.py -q
  git diff --check
  bash "$HOME/.codex/hooks/codex-cleanup.sh" --repo-root .
  ```

  Expected: provider build and focused tests pass; no mapping bypass exists. M4/M5 may remain red until Tasks 8/9 and therefore this commit stays on the stack.

- [ ] **Step 7: Commit the incompatible M3 checkpoint without integrating it alone.**

  ```bash
  git add -A packages/epcsaft
  git commit -m "refactor(provider): make evaluated input the only native path"
  ```

### Task 7: Prove Provider Equation/Derivative Continuity And Publish The SDK Contract

**Use Cases:**

- Neutral, associating, and electrolyte source-backed fixtures retain existing property, pressure, density, fugacity, Born, implicit-association, and state-sensitivity results at their existing tolerances.
- Every admitted nonconstant record family proves value and full T/composition chain-rule parity through the highest derivative order consumed by current APIs while density/composition remain live variables.
- SDK/source manifests and live docs teach only the strict configuration, schema-3 definitions, evaluated handle, and detached receipts.
- Structural proof makes retired serializers/defaults/bindings absent and prevents their return before consumer integration.

**Files:**

- Modify: `packages/epcsaft/tests/support/hydrocarbon_cases.py`
- Modify: `packages/epcsaft/tests/support/native_cases.py`
- Modify: `packages/epcsaft/tests/support/runtime_cases.py`
- Modify: `packages/epcsaft/tests/support/model_configurations.py`
- Create: `packages/epcsaft/tests/native/contracts/test_state_dependent_record_chain_rule.py`
- Modify: `packages/epcsaft/tests/native/contracts/test_association_implicit_derivative_contract.py`
- Modify: `packages/epcsaft/tests/native/contracts/test_derivative_coverage_matrix.py`
- Modify: `packages/epcsaft/tests/native/contracts/test_property_derivative_backend_contract.py`
- Modify: `packages/epcsaft/tests/native/state/test_association_parameter_derivative_validation.py`
- Modify: `packages/epcsaft/tests/native/state/test_born_parameter_derivatives.py`
- Modify: `packages/epcsaft/tests/native/state/test_contributions.py`
- Modify: `packages/epcsaft/tests/native/state/test_eos_contributions.py`
- Modify: `packages/epcsaft/tests/native/state/test_fugacity_derivatives.py`
- Modify: `packages/epcsaft/tests/native/state/test_phase_state_sensitivities.py`
- Modify: `packages/epcsaft/tests/native/state/test_pressure_density.py`
- Modify: `packages/epcsaft/tests/native/state/test_pressure_derivatives.py`
- Modify: `packages/epcsaft/tests/native/state/test_properties.py`
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

**Interfaces:**

- SDK discovery adds resolved-input contract ID/schema version/handle name and remains provider-only. Global capabilities add only configuration/resolved-input schema discovery.
- `test_state_dependent_record_chain_rule.py` parameterizes every admitted nonconstant family by dependency signature and required derivative order.

- [ ] **Step 1: Add RED receipt identity and correlation-sensitive derivative oracles.**

  Each existing representative fixture asserts definition/snapshot fingerprints, exact T/composition, evaluated record IDs, dependency groups, and CppAD/implicit backend labels. For a scalar state-dependent record `q(T, x)`, compare provider derivatives against an independently assembled chain rule:

  ```python
  expected_first = partial_property_fixed_q + partial_property_wrt_q * dq_dstate
  expected_second = (
      partial2_property_fixed_q
      + 2.0 * partial2_property_state_q * dq_dstate
      + partial2_property_q_q * dq_dstate**2
      + partial_property_wrt_q * d2q_dstate2
  )
  ```

  Use the actual tensor/vector form for composition records and cover all cross terms. Compare with the existing route tolerance; add no new relaxed tolerance. Perturb live density and trial composition independently so a frozen correlation cannot pass.

- [ ] **Step 2: Run RED/continuity characterization on a fresh provider build.**

  ```bash
  uv run --no-sync python scripts/dev/build_epcsaft.py --clean --profile provider --parallel 1
  uv run --no-sync python run_pytest.py \
    packages/epcsaft/tests/native/contracts/test_state_dependent_record_chain_rule.py \
    packages/epcsaft/tests/native/contracts/test_association_implicit_derivative_contract.py \
    packages/epcsaft/tests/native/contracts/test_derivative_coverage_matrix.py \
    packages/epcsaft/tests/native/state/test_born_parameter_derivatives.py \
    packages/epcsaft/tests/native/state/test_phase_state_sensitivities.py \
    packages/epcsaft/tests/native/state/test_pressure_derivatives.py \
    packages/epcsaft/tests/native/state/test_fugacity_derivatives.py -q
  ```

  Expected: new identity/chain-rule assertions expose any missing carried derivative; all unrelated existing scientific assertions remain green. A missing source record stops that case and is assigned to its existing M6 owner.

- [ ] **Step 3: Complete the derivative path without equation or admission changes.**

  For each failing record in an already admitted provider/route combination, evaluate the snapshot's typed definition inside the existing AD graph or carry derivatives through the route's required order and assemble every chain-rule term. If neither is complete, stop Stage 4. Rejection before native evaluation is permitted only when the exact record/route combination is already classified closed or unsupported by the pre-edit capability/preservation evidence; it may not silently withdraw an admitted combination. Record the choice, prior admission classification, and owner in the native mapping/derivative coverage receipt.

- [ ] **Step 4: Update SDK, docs, and absence guards.**

  Publish only `model_configuration.json`, schema-3 definitions, `ResolvedModelInput`, `EvaluatedModelInput`, `ProviderResolvedInputHandleV1`, exact receipt fields, dependency/invariance semantics, and consumer ownership. Remove live documentation for defaults, runtime dictionaries, `NativeArgs`, or condition-free mixture payloads. Project-structure tests scan executable/live docs and exclude dated historical specs/issues only.

- [ ] **Step 5: Run the provider confidence and structural lanes.**

  ```bash
  uv run --no-sync python run_pytest.py --provider-api -q
  uv run --no-sync python run_pytest.py --native -q
  uv run --no-sync python run_pytest.py \
    tests/workflows/repo/test_package_extension_boundary.py \
    tests/workflows/repo/test_project_structure.py -q
  uv run --no-sync ruff check packages/epcsaft/src packages/epcsaft/tests
  uv run --no-sync python scripts/dev/validate_project.py docs
  git diff --check
  bash "$HOME/.codex/hooks/codex-cleanup.sh" --repo-root .
  ```

  Expected: all selected tests/checks pass on the stack. Strict docs emit no warnings.

- [ ] **Step 6: Commit separate provider test and SDK/docs checkpoints.**

  ```bash
  git add packages/epcsaft/tests
  git commit -m "test(provider): prove resolved input derivative continuity"
  git add packages/epcsaft/src/epcsaft/runtime packages/epcsaft/src/epcsaft/native_sdk docs/contracts docs/adr CONTEXT.md docs/superpowers/PROJECT_CONTEXT.md docs/pages tests/workflows/repo
  git commit -m "docs(provider): publish resolved input contract"
  ```

### Task 8: Migrate All 25 M4 Intakes And The Public Configure/Structure/Solve Flow

**Use Cases:**

- Public bubble/dew/scoped pure VLE normalizes route composition once, evaluates the provider once at the specified phase conditions, and reuses one object/handle/fingerprint through configure, repeated structure, solve, and repeated solve.
- Missing/wrong-version/component/T/composition/fingerprint handles and non-invariant dynamic records fail before selector/NLP construction with affected record IDs.
- All 25 preserved/internal intakes use the const handle at exact explicit conditions or retain their proof while failing closed; no field copy, raw-array classifier, object recursion, or default remains.
- Public admission reads provider-owned active-family, ionic-index, association-topology, source-ID, structural-zero, and fingerprint evidence. Ionic public input remains rejected; nonassociating neutral input remains admitted; associating bubble/dew remains limited to the exact retained Gross/Sadowski 2002 Figures 2-9 proof registry; associating pure VLE remains rejected.
- `Equilibrium.provider_input_receipt` exposes the full detached receipt. Native result diagnostics expose only native-authored `provider_input_identity`; public route, activation, solver, derivative, proof, and numerical behavior remain unchanged.

**Files:**

- Create: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/core/provider_input.py`
- Create: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/core/provider_input.h`
- Create: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/core/provider_input.cpp`
- Create: `packages/epcsaft-equilibrium/tests/contracts/test_provider_resolved_input_integration.py`
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/equilibrium.py`
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/workflows.py`
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/_native.py`
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/_native_core.pyi`
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/core/native_results.py`
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/register_bindings.cpp`
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/blocks/electrolyte_block.cpp`
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/blocks/electrolyte_block.h`
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/blocks/eos_phase_block.cpp`
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/blocks/eos_phase_block.h`
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/blocks/phase_equilibrium_residual_block.cpp`
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/blocks/phase_equilibrium_residual_block.h`
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/blocks/saturation_block.cpp`
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/blocks/saturation_block.h`
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/core/activated_equilibrium_nlp.cpp`
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/core/activated_equilibrium_nlp.h`
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/core/activation_plan.cpp`
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/core/activation_plan.h`
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/core/chemical_equilibrium_nlp.h`
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/core/chemical_equilibrium_nlp.cpp`
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/core/chemical_equilibrium_objective.cpp`
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/core/selector_core.cpp`
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/core/selector_core.h`
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/core/two_phase_eos_route.cpp`
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/core/two_phase_eos_route.h`
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/derivatives/phase_block_derivatives.cpp`
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/derivatives/phase_block_derivatives.h`
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/routes/derived/bubble_dew.cpp`
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/results/result_builder.cpp`
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/results/result_builder.h`
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/results/route_result_bridge.h`
- Modify: `packages/epcsaft-equilibrium/cmake/equilibrium_native_sources.json`
- Modify: `packages/epcsaft-equilibrium/tests/contracts/test_equilibrium_native_contracts.py`
- Modify: `packages/epcsaft-equilibrium/tests/equilibrium_support/equilibrium_cases.py`
- Modify: `packages/epcsaft-equilibrium/tests/api/test_equilibrium.py`
- Modify: `packages/epcsaft-equilibrium/tests/api/test_single_component_vle.py`
- Modify: `packages/epcsaft-equilibrium/tests/api/test_bubble_derivatives.py`
- Modify: `packages/epcsaft-equilibrium/tests/native/blocks/test_eos_phase_block.py`
- Modify: `packages/epcsaft-equilibrium/tests/native/blocks/test_single_component_vle_block.py`
- Modify: `packages/epcsaft-equilibrium/tests/native/diagnostics/test_chemical_equilibrium_eos_activity.py`
- Modify: `packages/epcsaft-equilibrium/tests/native/diagnostics/test_chemical_equilibrium_homotopy.py`
- Modify: `packages/epcsaft-equilibrium/tests/native/diagnostics/test_chemical_equilibrium_nlp_activation.py`
- Modify: `packages/epcsaft-equilibrium/tests/native/diagnostics/test_electrolyte_held2_continuous_tpd.py`
- Modify: `packages/epcsaft-equilibrium/tests/native/diagnostics/test_electrolyte_held2_flash_validation.py`
- Modify: `packages/epcsaft-equilibrium/tests/native/diagnostics/test_electrolyte_held2_stage_ii.py`
- Modify: `packages/epcsaft-equilibrium/tests/native/diagnostics/test_internal_multiphase_activation_contracts.py`
- Modify: `packages/epcsaft-equilibrium/tests/native/diagnostics/test_phase_equilibrium_residual_block_contract.py`
- Modify: `packages/epcsaft-equilibrium/tests/native/diagnostics/test_route_metadata_contracts.py`
- Modify: `packages/epcsaft-equilibrium/tests/native/diagnostics/test_selector_core_contracts.py`
- Modify: `packages/epcsaft-equilibrium/tests/native/results/test_associating_lle_reference_values.py`
- Modify: `packages/epcsaft-equilibrium/tests/native/results/test_neutral_lle_reference_values.py`
- Modify: `packages/epcsaft-equilibrium/tests/native/results/test_result_builder.py`
- Modify: `tests/native/contracts/test_electrolyte_held2_phase_discovery.py`
- Modify: `tests/native/contracts/test_electrolyte_postsolve_certification.py`
- Modify: `tests/native/contracts/test_electrolyte_stage_iii_refinement.py`
- Modify: `tests/native/contracts/test_electrolyte_tpd_gate.py`
- Modify: `tests/native/contracts/test_gross_2002_figure01_internal_saturation.py`
- Modify: `scripts/validation/check_electrolyte_held2_phase_discovery.py`
- Modify: `scripts/validation/check_electrolyte_postsolve_certification.py`
- Modify: `scripts/validation/check_electrolyte_stage_iii_refinement.py`
- Modify: `scripts/validation/check_electrolyte_tpd_gate.py`
- Modify: `scripts/validation/check_generalized_phase_set.py`
- Modify: `scripts/validation/check_standalone_ce_gate.py`
- Modify: `scripts/validation/equilibrium_validation_runtime.py`
- Modify: `scripts/validation/check_associating_lle_gross_2002.py`
- Modify: `scripts/validation/check_boundary_workflows.py`
- Modify: `scripts/validation/check_ce_robustness_followup.py`
- Modify: `scripts/validation/check_electrolyte_gfpe_gate.py`
- Modify: `scripts/validation/check_electrolyte_held2_continuous_tpd.py`
- Modify: `scripts/validation/check_electrolyte_held2_readiness.py`
- Modify: `scripts/validation/check_electrolyte_held2_stage_ii.py`
- Modify: `scripts/validation/check_gross_2002_association_acceptance.py`
- Modify: `scripts/validation/check_held_reliability.py`
- Modify: `scripts/validation/check_neutral_lle_showcase.py`
- Modify: `scripts/validation/check_neutral_tp_flash_fixture.py`
- Modify: `scripts/validation/check_phase_discovery.py`
- Modify: `scripts/validation/check_gross_2002_full_replication.py`
- Modify: `scripts/validation/check_single_component_vle_nist_saturation.py`
- Modify: `scripts/validation/check_electrolyte_public_admission.py`
- Modify: `scripts/validation/native_freshness.py`
- Modify: `analyses/paper_validation/2002_gross/figures/figure_01/scripts/generate_data.py`
- Modify: `analyses/paper_validation/2002_gross/figures/figure_02/scripts/generate_data.py`
- Modify: `analyses/paper_validation/2002_gross/figures/figure_03/scripts/generate_data.py`
- Modify: `analyses/paper_validation/2002_gross/figures/figure_04/scripts/generate_data.py`
- Modify: `analyses/paper_validation/2002_gross/figures/figure_05/scripts/generate_data.py`
- Modify: `analyses/paper_validation/2002_gross/figures/figure_06/scripts/generate_data.py`
- Modify: `analyses/paper_validation/2002_gross/figures/figure_07/scripts/generate_data.py`
- Modify: `analyses/paper_validation/2002_gross/figures/figure_08/scripts/generate_data.py`
- Modify: `analyses/paper_validation/2002_gross/figures/figure_09/scripts/generate_data.py`
- Modify: `analyses/paper_validation/2002_gross/figures/figure_10/scripts/generate_data.py`
- Modify: `tests/native/contracts/test_generalized_phase_set_checker.py`
- Modify: `tests/native/contracts/test_generalized_phase_set_completion_checker.py`
- Modify: `tests/native/contracts/test_standalone_ce_gate.py`
- Modify: `tests/native/contracts/test_chemical_equilibrium_reference_oracles.py`
- Modify: `packages/epcsaft-equilibrium/README.md`
- Modify: `packages/epcsaft-equilibrium/docs/README.md`

**Interfaces:**

- `Equilibrium.__slots__` becomes `("_evaluated_model_input", "_problem", "mixture")` and exposes detached `provider_input_receipt`.
- Every affected native binding's first model-input argument is `std::shared_ptr<ProviderResolvedInputHandleV1>`. The handle has no mutator and owns `std::shared_ptr<const NativeEvaluatedInputSnapshot>`; this exact pybind holder/caster type is shared by M3, M4, and M5.
- Native diagnostics contain exact `provider_input_identity` keys: contract ID, schema, schema version, definition fingerprint, snapshot fingerprint, component order, temperature, composition basis/vector, and `trial_phase_composition_invariant`.

- [ ] **Step 1: Write RED public identity, mismatch, invariance, capability, and 25-binding tests.**

  Instrument `ResolvedModelInput.evaluate` to count calls. For bubble, dew, and pure VLE assert one call at exact `(T, x)`, `(T, y)`, and `(T, [1.0])`; repeated structure/solve calls retain object identity and fingerprints. Mutate each handle identity field and assert failure occurs before a monkeypatched native dispatch. Supply a composition-dependent active record to a composition-varying intake and a temperature-dependent active record to a temperature-varying internal bubble-T intake; assert each error names provider affected record IDs. Also prove a fixed-T public bubble/dew route remains eligible when its only active dependency is temperature and its provider input is composition-invariant.

  Preserve the exact public admission matrix with receipt-backed tests: ionic provider indices reject before selector dispatch; an unproved associating provider handle rejects; every retained Gross/Sadowski Figures 2-9 associating bubble/dew case remains admitted; changing any source ID, definition fingerprint, component order, association-topology fingerprint, structural-zero ID, or retained proof key rejects. M4 owns an immutable Gross proof registry keyed by the migrated source-bundle/definition identity and existing retained proof ID; it does not label a paper from provider arrays or ask M3 to invent a paper classification.

  For all 25 manifest rows, call the existing proof path with a handle evaluated at its explicit block/route conditions. Assert no preservation item changes classification. Capture canonical equilibrium activation/capability JSON before the production edit and compare after while allowing only nested provider contract/schema discovery.

  Audit every validation script listed in this task. Any checker that constructs a retired native input or calls an affected binding must build an explicit strict provider input at its existing source-backed conditions and pass its handle instead of `mixture._native`; its root contract retains the existing blocker/success assertions. The Gross full-replication, NIST saturation, electrolyte public-admission, and native-freshness evidence owners must remain executable even when their own intake does not change. Audit standalone CE and its reference-oracle tests: pass the exact standard-state handle only when the optional EOS-activity intake is active, otherwise record and assert `no_provider_input_required` for the ideal standalone path. No checker may reconstruct a map, keep a condition-free mixture escape, or silently drop its proof.

  Update `equilibrium_cases.py`, the three public API/derivative tests, and Gross Figures 1-10 `generate_data.py` files only to construct the explicit disabled/enabled `ModelOptions` already implied by their retained source bundle. Assert the provider definition/source fingerprint and all pre-edit scientific expected values are unchanged. Do not regenerate data/plots, alter paper logic, relax assertions, or classify a failed paper program as passing.

- [ ] **Step 2: Run RED after a fresh equilibrium build.**

  ```bash
  uv run --no-sync python scripts/dev/build_epcsaft.py --clean --profile equilibrium --parallel 1
  uv run --no-sync python run_pytest.py \
    packages/epcsaft-equilibrium/tests/contracts/test_provider_resolved_input_integration.py \
    packages/epcsaft-equilibrium/tests/contracts/test_equilibrium_ownership_map.py \
    packages/epcsaft-equilibrium/tests/contracts/test_activation_capabilities.py \
    packages/epcsaft-equilibrium/tests/api/test_equilibrium.py \
    packages/epcsaft-equilibrium/tests/api/test_single_component_vle.py -q
  ```

  Expected: failures identify `mixture.native`, the field-copy converter, missing result identity, and old binding signatures; preservation/capability assertions outside the new intake contract remain green.

- [ ] **Step 3: Implement the one-evaluation public flow.**

  ```python
  class Equilibrium:
      __slots__ = ("_evaluated_model_input", "_problem", "mixture")

      def __init__(self, mixture: Mixture, *, route: str, T=None, P=None, x=None, y=None, z=None) -> None:
          provider_contract()
          self.mixture = mixture
          request = validate_and_normalize_equilibrium_request(
              mixture,
              route=route,
              T=T,
              P=P,
              x=x,
              y=y,
              z=z,
          )
          temperature, composition = provider_evaluation_conditions(request)
          self._evaluated_model_input = mixture.resolved_model_input.evaluate(
              temperature=temperature,
              composition=composition,
          )
          provider_input = require_equilibrium_provider_input(
              self._evaluated_model_input,
              request,
          )
          self._problem = configure_equilibrium_problem(
              request,
              provider_input=provider_input,
          )

      @property
      def provider_input_receipt(self) -> dict[str, Any]:
          return self._evaluated_model_input.receipt
  ```

  `validate_and_normalize_equilibrium_request` performs only route-shape/scalar/composition validation and the existing normalization; it cannot classify provider fields. `require_equilibrium_provider_input` validates identity, dynamic dependencies, and admission before configure can construct or dispatch a selector/NLP. Configure, structure, and solve all receive the same native handle, while `Equilibrium` retains the Python object. Preserve `_normalize_feed`'s current validation/division/minimum-check sequence and pass its exact output to M3.

- [ ] **Step 4: Implement one M4 native validator and migrate every const intake.**

  `require_provider_input(...)` checks handle presence, contract/schema/version, components, T, canonical composition, receipt/handle fingerprint, selects the intake's manifest-owned static set or exact selector route set, and intersects it with provider `affected_record_ids` using the current condition-comparison tolerance. It returns `const NativeEvaluatedInputSnapshot&`. The public admission helper then uses snapshot active residual families, ionic indices, association topology, scientific source IDs, structural-zero evidence, and M4's exact retained Gross proof registry to preserve the pre-edit admission matrix. Replace `native_args_from_payload` and `native_args_from_mixture_object` with this validator and migrate all listed block/core/route/derivative owners to snapshot reads. Optional CE EOS activity requires an exact standard-state handle or rejects before NLP. Do not change request schemas, activation, solver options, tolerances, coordinates, objective/residual mathematics, or postsolve acceptance.

- [ ] **Step 5: Author result identity natively.**

  Construct `provider_input_identity` once from the handle in the native result bridge and echo it through structure/solve diagnostics. Only `Equilibrium.provider_input_receipt` exposes the full detached receipt; result objects do not gain a second receipt field. Python verifies both fingerprints match and does not reconstruct identity from optional diagnostics.

- [ ] **Step 6: Delete M4 reconstruction/classification fallbacks.**

  Remove the 47-field parser, `_native_args_payload` path, recursive `_native` handling, native-mixture cast, raw-array active-family/ionic/association/source classifiers, and fallback/default values only after the snapshot-backed admission tests are green. Keep the M4 Gross proof registry, selector request, CE schema, solver options, and derived tolerances in their existing M4 owners.

- [ ] **Step 7: Fresh-build and run the M4 GREEN proof.**

  ```bash
  uv run --no-sync python scripts/dev/build_epcsaft.py --clean --profile equilibrium --parallel 1
  uv run --no-sync python run_pytest.py --equilibrium-api -q
  uv run --no-sync python run_pytest.py --native-contracts -q
  uv run --no-sync python run_pytest.py packages/epcsaft-equilibrium/tests/native -q
  uv run --no-sync python run_pytest.py tests/native/contracts -q
  uv run --no-sync python run_pytest.py \
    packages/epcsaft-equilibrium/tests/contracts/test_provider_resolved_input_integration.py \
    packages/epcsaft-equilibrium/tests/contracts/test_equilibrium_ownership_map.py \
    packages/epcsaft-equilibrium/tests/contracts/test_activation_capabilities.py \
    packages/epcsaft-equilibrium/tests/api/test_equilibrium.py \
    packages/epcsaft-equilibrium/tests/api/test_single_component_vle.py \
    packages/epcsaft-equilibrium/tests/api/test_bubble_derivatives.py \
    tests/native/contracts/test_electrolyte_held2_phase_discovery.py \
    tests/native/contracts/test_electrolyte_postsolve_certification.py \
    tests/native/contracts/test_electrolyte_stage_iii_refinement.py \
    tests/native/contracts/test_electrolyte_tpd_gate.py \
    tests/native/contracts/test_gross_2002_figure01_internal_saturation.py \
    tests/native/contracts/test_generalized_phase_set_checker.py \
    tests/native/contracts/test_generalized_phase_set_completion_checker.py \
    tests/native/contracts/test_standalone_ce_gate.py \
    tests/native/contracts/test_chemical_equilibrium_reference_oracles.py -q
  uv run --no-sync ruff check packages/epcsaft-equilibrium/src packages/epcsaft-equilibrium/tests
  git diff --check
  bash "$HOME/.codex/hooks/codex-cleanup.sh" --repo-root .
  ```

  Expected: build/tests/checks pass; all 25 rows have proof; public numerical/attempt/result behavior stays within existing assertions; capabilities meet the exact allowed delta.

- [ ] **Step 8: Commit the M4 consumer cutover separately.**

  ```bash
  git add -A packages/epcsaft-equilibrium scripts/validation tests/native/contracts analyses/paper_validation/2002_gross/figures/figure_01/scripts/generate_data.py analyses/paper_validation/2002_gross/figures/figure_02/scripts/generate_data.py analyses/paper_validation/2002_gross/figures/figure_03/scripts/generate_data.py analyses/paper_validation/2002_gross/figures/figure_04/scripts/generate_data.py analyses/paper_validation/2002_gross/figures/figure_05/scripts/generate_data.py analyses/paper_validation/2002_gross/figures/figure_06/scripts/generate_data.py analyses/paper_validation/2002_gross/figures/figure_07/scripts/generate_data.py analyses/paper_validation/2002_gross/figures/figure_08/scripts/generate_data.py analyses/paper_validation/2002_gross/figures/figure_09/scripts/generate_data.py analyses/paper_validation/2002_gross/figures/figure_10/scripts/generate_data.py docs/superpowers/milestones/M4-equilibrium/equilibrium-preservation-manifest.yaml
  git commit -m "refactor(equilibrium): consume immutable provider input"
  ```

### Task 9: Complete The Bounded M5 Consumer Cutover Without Redesign

**Use Cases:**

- Every currently admitted M5 production path consumes a provider handle whose schema/version/components/T/composition/fingerprint match the compiled regression row.
- Ceres evaluates its unchanged residuals and derivatives through the Task 5 immutable-baseline overlay; the baseline handle/fingerprint never mutates across iterations.
- Public target kinds, bounds, starts, residual packing/formulas, optimizer, derivative/Jacobian policy, success/acceptance, and capability rows remain byte-equivalent.
- Provider serializer imports, association mutation, native argument construction, and mapping payload arrays are displaced without adding the future M5 receipt/workflow redesign.

**Files:**

- Create: `packages/epcsaft-regression/tests/contracts/test_provider_resolved_input_integration.py`
- Modify: `packages/epcsaft-regression/src/epcsaft_regression/native_adapter.py`
- Modify: `packages/epcsaft-regression/src/epcsaft_regression/core.py`
- Modify: `packages/epcsaft-regression/src/epcsaft_regression/workflow.py`
- Modify: `packages/epcsaft-regression/src/epcsaft_regression/native/regression/resolved_input_adapter.h`
- Modify: `packages/epcsaft-regression/src/epcsaft_regression/native/regression/resolved_input_adapter.cpp`
- Modify: `packages/epcsaft-regression/src/epcsaft_regression/native/regression/ceres_regression.cpp`
- Modify: `packages/epcsaft-regression/src/epcsaft_regression/native/regression/module.cpp`
- Modify: `packages/epcsaft-regression/src/epcsaft_regression/_native_core.pyi`
- Modify: `packages/epcsaft-regression/tests/api/test_regression.py`
- Modify: `packages/epcsaft-regression/tests/native/test_pure.py`
- Modify: `packages/epcsaft-regression/tests/native/test_binary.py`
- Modify: `packages/epcsaft-regression/tests/native/test_liquid_electrolyte.py`
- Modify: `packages/epcsaft-regression/tests/test_imports.py`

**Interfaces:**

- Replaces `fixed_payloads: Sequence[Mapping]` with ordered `EvaluatedModelInput.native_handle` objects already produced by the Task 5-approved compiler seam.
- Native `_fit_*` and `_evaluate_*` bindings accept provider handles plus existing regression records/target metadata/starts/bounds/limits. They do not accept `NativeArgs` or dict model input.

- [ ] **Step 1: Write RED integration, lifetime, parity, and absence tests.**

  Assert each compiled row's exact handle identity reaches native Ceres, remains alive after Python receipt deletion, and is unchanged after multiple objective/Jacobian evaluations. Repeat Task 5 parity for production paths and compare canonical `capabilities()` excluding only approved nested provider schema discovery. Assert source contains no `check_association`, `create_struct`, `to_runtime_dict`, provider mapping, or `NativeArgs` model input.

- [ ] **Step 2: Run RED.**

  ```bash
  uv run --no-sync python scripts/dev/build_epcsaft.py --profile regression --parallel 1
  uv run --no-sync python run_pytest.py \
    packages/epcsaft-regression/tests/contracts/test_provider_resolved_input_integration.py \
    packages/epcsaft-regression/tests/contracts/test_provider_resolved_input_feasibility.py \
    packages/epcsaft-regression/tests/api/test_regression.py \
    packages/epcsaft-regression/tests/native/test_pure.py \
    packages/epcsaft-regression/tests/native/test_binary.py \
    packages/epcsaft-regression/tests/native/test_liquid_electrolyte.py \
    packages/epcsaft-regression/tests/test_imports.py -q
  ```

  Expected: new integration/absence assertions fail on the old adapter while existing regression science stays green.

- [ ] **Step 3: Replace only the provider intake.**

  Pass ordered evaluated handles from the gate-proven compiler seam into native bindings. At binding entry validate contract/schema/version, row components, exact row T/composition, and fingerprint. Reuse `ResolvedInputOverlayViewV1` in the existing Ceres residual/Jacobian loop. Do not introduce the future strict target/result/receipt/persistence redesign from the broader M5 plan in this leaf.

- [ ] **Step 4: Delete displaced M5 provider serialization.**

  Remove imports/exports/calls for `check_association`, `create_struct`, `_native_args_sequence`, `ParameterSource.to_runtime_dict`, provider runtime dictionaries, and native `add_args` inputs. Remove no public regression entrypoint unless the Task 5 PASS evidence already proves it delegates through the unchanged configured contract; otherwise this task is unauthorized and the gate should have stopped the stage.

- [ ] **Step 5: Fresh-build and run GREEN.**

  ```bash
  uv run --no-sync python scripts/dev/build_epcsaft.py --profile regression --parallel 1
  uv run --no-sync python run_pytest.py --regression -q
  uv run --no-sync python run_pytest.py \
    packages/epcsaft-regression/tests/contracts/test_provider_resolved_input_integration.py \
    packages/epcsaft-regression/tests/contracts/test_provider_resolved_input_feasibility.py -q
  uv run --no-sync python scripts/dev/validate_project.py regression
  uv run --no-sync ruff check packages/epcsaft-regression/src packages/epcsaft-regression/tests
  git diff --check
  bash "$HOME/.codex/hooks/codex-cleanup.sh" --repo-root .
  ```

  Expected: all M5 tests/checks pass; immutable baseline/fitted overlay proof is green; capability/target/bound/residual/optimizer/derivative/acceptance bytes are unchanged.

- [ ] **Step 6: Commit the M5 consumer cutover separately.**

  ```bash
  git add -A packages/epcsaft-regression
  git commit -m "refactor(regression): consume immutable provider input"
  ```

### Task 10: Verify The Combined Stack, Commit The Stage Receipt, And Fast-Forward `main`

**Use Cases:**

- Provider, M4, and M5 build and pass focused proofs together on one source revision with matching SDK/source/native identities.
- Live absence scans prove one configuration parser, one resolved compiler, one evaluated snapshot constructor, no retired serializer/default/fallback, and no consumer reconstruction.
- Independent code and scientific reviews verify ownership, chain-rule completeness, preservation, capability neutrality, and stop-gate compliance.
- A durable receipt records exact commits/commands/evidence/deferred blockers and no push; only then is the combined ordered stack fast-forwarded to `main` and Stage 4 stops before Stage 5.

**Files:**

- Create: `docs/superpowers/milestones/M4-equilibrium/stage-4-provider-resolved-input-boundary-receipt.yaml`
- Modify: `docs/superpowers/milestones/M4-equilibrium/README.md`
- Modify: `tests/workflows/repo/test_package_extension_boundary.py`
- Modify: `tests/workflows/repo/test_project_structure.py`
- Modify: `tests/workflows/repo/test_run_pytest.py`

**Interfaces:**

- Final receipt schema records `stage`, `status`, `source_commit`, ordered owner commits, provider/equilibrium/regression source identities, native module paths/embedded identities, proof commands/results, capability comparisons, 25-binding count, derivative families/orders, absence scan, independent reviews, deferred paper blockers, cleanup, and `push_performed: false`.
- `test_project_structure.py` adds an AST-based, identifier-independent live-caller guard. Across provider/M4/M5 Python, `scripts/validation`, and the explicitly migrated Gross generators it rejects any `ast.Attribute` access named `_native` or condition-free `native`, chained native access, `ePCSAFTMixture.from_params(...)`, `NativeArgs`, `_native_args_payload`, and retired converter/serializer calls. `ImportFrom epcsaft_equilibrium._native` remains distinguishable as a module import, not an attribute escape.

- [ ] **Step 1: Run the complete combined build and focused proof from the stack tip.**

  ```bash
  uv run --no-sync python scripts/dev/build_epcsaft.py --clean --profile provider --parallel 1
  uv run --no-sync python run_pytest.py packages/epcsaft/tests/native/contracts/test_provider_only_core_symbols.py -q
  uv run --no-sync python scripts/dev/build_epcsaft.py --clean --profile full --parallel 1
  uv run --no-sync python scripts/dev/build_extension_dists.py --mode monorepo --parallel 1
  uv run --no-sync python scripts/dev/build_extension_dists.py --mode installed-provider --parallel 1
  uv run --no-sync python run_pytest.py packages/epcsaft/tests -q
  uv run --no-sync python run_pytest.py \
    packages/epcsaft-equilibrium/tests/contracts/test_provider_resolved_input_integration.py \
    packages/epcsaft-equilibrium/tests/contracts/test_provider_resolved_input_handle_abi.py \
    packages/epcsaft-equilibrium/tests/contracts/test_equilibrium_ownership_map.py \
    packages/epcsaft-equilibrium/tests/contracts/test_activation_capabilities.py \
    packages/epcsaft-equilibrium/tests/api/test_equilibrium.py \
    packages/epcsaft-equilibrium/tests/api/test_single_component_vle.py \
    packages/epcsaft-equilibrium/tests/api/test_bubble_derivatives.py -q
  uv run --no-sync python run_pytest.py packages/epcsaft-equilibrium/tests/native -q
  uv run --no-sync python run_pytest.py tests/native/contracts -q
  uv run --no-sync python run_pytest.py \
    tests/native/contracts/test_electrolyte_held2_phase_discovery.py \
    tests/native/contracts/test_electrolyte_postsolve_certification.py \
    tests/native/contracts/test_electrolyte_stage_iii_refinement.py \
    tests/native/contracts/test_electrolyte_tpd_gate.py \
    tests/native/contracts/test_gross_2002_figure01_internal_saturation.py \
    tests/native/contracts/test_generalized_phase_set_checker.py \
    tests/native/contracts/test_generalized_phase_set_completion_checker.py \
    tests/native/contracts/test_standalone_ce_gate.py \
    tests/native/contracts/test_chemical_equilibrium_reference_oracles.py -q
  uv run --no-sync python run_pytest.py \
    packages/epcsaft-regression/tests/contracts/test_provider_resolved_input_integration.py \
    packages/epcsaft-regression/tests/contracts/test_provider_resolved_input_handle_abi.py \
    packages/epcsaft-regression/tests/contracts/test_provider_resolved_input_feasibility.py \
    packages/epcsaft-regression/tests/api/test_regression.py \
    packages/epcsaft-regression/tests/native -q
  uv run --no-sync python run_pytest.py \
    tests/workflows/repo/test_package_extension_boundary.py \
    tests/workflows/repo/test_project_structure.py \
    tests/workflows/repo/test_run_pytest.py \
    tests/native/contracts/test_native_freshness_receipt.py -q
  ```

  Expected: all builds/tests exit zero on one source revision; provider handle identity matches in both extensions; M4 count is 25; no capability outside the allowed nested discovery changes.

- [ ] **Step 2: Run exact live absence scans.**

  ```bash
  rg -n 'user_options\.json|model_options\.json|runtime_options|to_runtime_dict|LegacyRuntimeOptionsState|legacy_v2_gate|stage4_legacy_runtime|_runtime_payload|create_struct|check_association|NativeArgs|_native_args_payload|native_args_from_payload|native_args_from_mixture_object' \
    packages/epcsaft/src \
    packages/epcsaft-equilibrium/src \
    packages/epcsaft-regression/src \
    CONTEXT.md docs/pages docs/contracts
  rg -n 'ePCSAFTMixture\.from_params|NativeArgs|_native_args_payload|native_args_from_payload|native_args_from_mixture_object|to_runtime_dict' scripts/validation analyses/paper_validation/2002_gross/figures
  uv run --no-sync python run_pytest.py tests/workflows/repo/test_project_structure.py -q -k condition_free_provider_input
  ```

  Expected: each `rg` exits 1 with no matches. Historical specs/plans/issues and the final receipt may name retired paths as dated evidence and are intentionally outside this live-surface scan.

- [ ] **Step 3: Run lint, docs, plan validators, diff, and cleanup.**

  ```bash
  uv run --no-sync ruff check packages/epcsaft/src packages/epcsaft/tests packages/epcsaft-equilibrium/src packages/epcsaft-equilibrium/tests packages/epcsaft-regression/src packages/epcsaft-regression/tests
  uv run --no-sync python scripts/dev/validate_project.py docs
  uv run --no-sync python scripts/validate_plan_task_use_cases.py --plan-path docs/superpowers/plans/2026-07-13-m3-m4-stage-4-provider-resolved-input-boundary-plan.md
  uv run --no-sync python scripts/validate_plan_outcome_proof.py --plan-path docs/superpowers/plans/2026-07-13-m3-m4-stage-4-provider-resolved-input-boundary-plan.md
  git diff --check
  bash "$HOME/.codex/hooks/codex-cleanup.sh" --repo-root .
  git status --short --branch
  ```

  Expected: all validators/checks exit zero; cleanup reports no task-owned residue; status lists only the not-yet-committed receipt/index changes.

- [ ] **Step 4: Obtain independent code and scientific review.**

  Give reviewers the approved spec, this plan, the complete stack diff, field-accounting table, M4 25-row manifest, M5 gate evidence, derivative matrix, capability comparison, and proof outputs. Code review must find no alternate owner/fallback/mutable handle. Scientific review must approve dependency identity, exact state conditions, live-variable/chain-rule behavior, M4 invariance, preservation, and no equation/tolerance/capability drift. Resolve every blocker and rerun affected proof before continuing.

- [ ] **Step 5: Write and validate the durable receipt.**

  Use exact commit hashes and command outcomes; do not write `passed` without evidence fields. Set `status: complete` only after Steps 1-4 pass. List existing paper blockers without repairing them and set `push_performed: false`. Add the receipt link and Stage 4 completion status to the M4 index.

- [ ] **Step 6: Commit the closeout on the stack.**

  ```bash
  git add docs/superpowers/milestones/M4-equilibrium/stage-4-provider-resolved-input-boundary-receipt.yaml docs/superpowers/milestones/M4-equilibrium/README.md tests/workflows/repo/test_package_extension_boundary.py tests/workflows/repo/test_project_structure.py tests/workflows/repo/test_run_pytest.py
  git commit -m "docs(equilibrium): record stage 4 resolved input cutover"
  git status --short --branch
  ```

  Expected: clean stack branch.

- [ ] **Step 7: Fast-forward `main` only after final verification.**

  ```bash
  git switch main
  git merge --ff-only codex/stage4-resolved-input-stack
  git status --short --branch
  git log --oneline --decorate -15
  ```

  Expected: fast-forward succeeds, `main` is clean, all separate M3/M4/M5/closeout commits remain visible in order, and no push occurs. Stop before Stage 5.

## Proof Oracle

```bash
uv run --no-sync python scripts/validate_plan_task_use_cases.py --plan-path docs/superpowers/plans/2026-07-13-m3-m4-stage-4-provider-resolved-input-boundary-plan.md
uv run --no-sync python scripts/validate_plan_outcome_proof.py --plan-path docs/superpowers/plans/2026-07-13-m3-m4-stage-4-provider-resolved-input-boundary-plan.md
uv run --no-sync python scripts/dev/build_epcsaft.py --clean --profile provider --parallel 1
uv run --no-sync python run_pytest.py packages/epcsaft/tests/native/contracts/test_provider_only_core_symbols.py -q
uv run --no-sync python scripts/dev/build_epcsaft.py --clean --profile full --parallel 1
uv run --no-sync python scripts/dev/build_extension_dists.py --mode monorepo --parallel 1
uv run --no-sync python scripts/dev/build_extension_dists.py --mode installed-provider --parallel 1
uv run --no-sync python run_pytest.py packages/epcsaft/tests -q
uv run --no-sync python run_pytest.py packages/epcsaft-equilibrium/tests/contracts/test_provider_resolved_input_integration.py packages/epcsaft-equilibrium/tests/contracts/test_provider_resolved_input_handle_abi.py packages/epcsaft-equilibrium/tests/contracts/test_equilibrium_ownership_map.py packages/epcsaft-equilibrium/tests/contracts/test_activation_capabilities.py packages/epcsaft-equilibrium/tests/api/test_equilibrium.py packages/epcsaft-equilibrium/tests/api/test_single_component_vle.py packages/epcsaft-equilibrium/tests/api/test_bubble_derivatives.py -q
uv run --no-sync python run_pytest.py packages/epcsaft-equilibrium/tests/native -q
uv run --no-sync python run_pytest.py tests/native/contracts -q
uv run --no-sync python run_pytest.py tests/native/contracts/test_electrolyte_held2_phase_discovery.py tests/native/contracts/test_electrolyte_postsolve_certification.py tests/native/contracts/test_electrolyte_stage_iii_refinement.py tests/native/contracts/test_electrolyte_tpd_gate.py tests/native/contracts/test_gross_2002_figure01_internal_saturation.py tests/native/contracts/test_generalized_phase_set_checker.py tests/native/contracts/test_generalized_phase_set_completion_checker.py tests/native/contracts/test_standalone_ce_gate.py tests/native/contracts/test_chemical_equilibrium_reference_oracles.py -q
uv run --no-sync python run_pytest.py packages/epcsaft-regression/tests/contracts/test_provider_resolved_input_integration.py packages/epcsaft-regression/tests/contracts/test_provider_resolved_input_handle_abi.py packages/epcsaft-regression/tests/contracts/test_provider_resolved_input_feasibility.py packages/epcsaft-regression/tests/api/test_regression.py packages/epcsaft-regression/tests/native -q
uv run --no-sync python run_pytest.py tests/workflows/repo/test_package_extension_boundary.py tests/workflows/repo/test_project_structure.py tests/workflows/repo/test_run_pytest.py tests/native/contracts/test_native_freshness_receipt.py -q
! rg -n 'user_options\.json|model_options\.json|runtime_options|to_runtime_dict|LegacyRuntimeOptionsState|legacy_v2_gate|stage4_legacy_runtime|_runtime_payload|create_struct|check_association|NativeArgs|_native_args_payload|native_args_from_payload|native_args_from_mixture_object' packages/epcsaft/src packages/epcsaft-equilibrium/src packages/epcsaft-regression/src CONTEXT.md docs/pages docs/contracts
! rg -n 'ePCSAFTMixture\.from_params|NativeArgs|_native_args_payload|native_args_from_payload|native_args_from_mixture_object|to_runtime_dict' scripts/validation analyses/paper_validation/2002_gross/figures
uv run --no-sync python run_pytest.py tests/workflows/repo/test_project_structure.py -q -k condition_free_provider_input
uv run --no-sync ruff check packages/epcsaft/src packages/epcsaft/tests packages/epcsaft-equilibrium/src packages/epcsaft-equilibrium/tests packages/epcsaft-regression/src packages/epcsaft-regression/tests
uv run --no-sync python scripts/dev/validate_project.py docs
git diff --check
bash "$HOME/.codex/hooks/codex-cleanup.sh" --repo-root .
```
