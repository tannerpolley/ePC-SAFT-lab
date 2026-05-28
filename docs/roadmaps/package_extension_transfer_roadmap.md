# ePC-SAFT Package Extension Transfer Roadmap

Date: 2026-05-28

This document is the authoritative roadmap for the true ePC-SAFT package-extension
transfer. Treat this as the original plan for the split, not as a correction to
an older plan.

This roadmap controls extraction sequencing. Do not proceed with real extraction
work until the target state and phase gates defined here are satisfied.

## Non-Negotiable Target State

### Final GitHub Organization Layout

```text
ePC-SAFT/ePC-SAFT
  Core provider repo and PyPI package: epcsaft

ePC-SAFT/epcsaft-equilibrium
  Equilibrium extension repo and PyPI package: epcsaft-equilibrium

ePC-SAFT/epcsaft-regression
  Regression extension repo and PyPI package: epcsaft-regression
```

### Final Local Sibling-Repo Layout

```text
C:\Users\Tanner\Documents\Workspaces\Engineering\ePC-SAFT
C:\Users\Tanner\Documents\Workspaces\Engineering\epcsaft-equilibrium
C:\Users\Tanner\Documents\Workspaces\Engineering\epcsaft-regression
```

### Hard Rules

- No Git submodules. Use normal Python dependencies, editable installs, `uv`
  path sources, and CI checkout/install steps.
- `packages/epcsaft-equilibrium` and `packages/epcsaft-regression` are
  temporary monorepo staging folders only. They are not the final package
  layout, they are not the final local development layout, and they are not the
  final GitHub repository layout.
- The provider package is a provider-only core after extraction. It must not
  permanently keep extension-owned code, symbols, wrappers, or hidden import
  paths.
- The split is not complete until local sibling repos, remote GitHub repos,
  native ownership, tests, CI, docs, package metadata, release choreography,
  and install proofs all agree.
- Prefer loud failure over fake defaults. Do not leave hidden compatibility
  wrappers, duplicated native code, dead CMake branches, or stale capability
  claims behind the migration.

## Current Verified State In This Repo

The current checkout is still a transition monorepo, not real extraction:

- equilibrium C++ still lives under `src/epcsaft/native/equilibrium`;
- regression C++ still lives under `src/epcsaft/native/regression`;
- `CMakeLists.txt` defines object targets
  `epcsaft_provider_native`, `epcsaft_equilibrium_native`, and
  `epcsaft_regression_native`, but still links them into one provider-owned
  `epcsaft._core` module;
- `packages/epcsaft-equilibrium` is currently a Python extension-package shell
  around provider-owned native bindings exposed through `epcsaft._core`;
- `packages/epcsaft-regression` is currently a thin shell and does not own the
  native regression implementation;
- root `epcsaft` still exports `Regression`;
- provider runtime metadata still reports regression transition capability data;
- this is not yet true provider/extension extraction.

These facts are the starting point for the roadmap. They are not acceptable as
the final state.

## End-State Ownership

### Core Provider Repo: `ePC-SAFT/ePC-SAFT`

Public package/distribution: `epcsaft`

Owns:

- EOS, model, state, parameters, density/pressure closure;
- fugacity, activity, and chemical-potential evaluation;
- contribution traces and derivative-capable provider functions;
- CppAD and exact provider derivative support;
- provider diagnostics, provider capabilities, and provider result schemas;
- `provider_native_sdk` and the versioned provider contract consumed by
  extensions.

Must build and install without:

- Ceres;
- Ipopt;
- extension-package imports;
- extension-owned native symbols.

Must not own after extraction:

- equilibrium result schemas, route assembly, or solver acceptance logic;
- regression datasets, target rows, residual blocks, or optimizer logic;
- permanent extension code under `src/epcsaft/native/equilibrium`;
- permanent extension code under `src/epcsaft/native/regression`;
- permanent `packages/epcsaft-equilibrium` or `packages/epcsaft-regression`
  staging folders.

### Equilibrium Extension Repo: `ePC-SAFT/epcsaft-equilibrium`

Public package/distribution: `epcsaft-equilibrium`

Import package: `epcsaft_equilibrium`

Owns:

- `Equilibrium`;
- route specs;
- GFPE assembly;
- phase discovery and stability/TPD evidence;
- Ipopt NLP assembly and Ipopt option profiles;
- postsolve certification;
- equilibrium result schemas, diagnostics, and capabilities;
- the equilibrium native C++ that currently lives under
  `src/epcsaft/native/equilibrium`.

Depends on:

- `epcsaft`;
- Ipopt.

Must not depend on:

- Ceres;
- private provider internals;
- downstream repo code.

### Regression Extension Repo: `ePC-SAFT/epcsaft-regression`

Public package/distribution: `epcsaft-regression`

Import package: `epcsaft_regression`

Owns:

- `Regression`;
- `TargetDataset` and `TargetRow`;
- parameter maps and bounds;
- Ceres residual blocks;
- optimizer diagnostics;
- regression result schemas and capabilities;
- the regression native C++ that currently lives under
  `src/epcsaft/native/regression`.

Depends on:

- `epcsaft`;
- Ceres.

Optional integration:

- `epcsaft-equilibrium` only for explicit equilibrium-backed target lanes.

Must not require by default:

- Ipopt;
- equilibrium package imports for non-equilibrium regression workflows.

## Provider Contract And Native Boundary

The provider repo is the source of truth for the extension contract. Extensions
consume the provider contract, not private core internals.

The provider contract must include:

- Python API compatibility surface;
- `provider_native_sdk` metadata;
- native target or CMake metadata needed by extensions;
- supported symbols;
- error and diagnostic schema;
- derivative and result schema;
- compatibility version.

Required boundary rules:

- `epcsaft.capabilities()` is provider-scoped after extraction;
- extension capability reports are package-owned and evidence-backed;
- provider `_core` in a provider-only build must expose provider-only symbols;
- equilibrium and regression native symbols must not leak into provider-only
  `_core`;
- core must not import extension packages;
- extensions may not depend on private provider modules as their contract.

## Native Module Split Target

The current object-target split is only a transition seam. The final native
ownership split is:

- provider native target:
  owns EOS/model/state/autodiff/provider contract exports;
- equilibrium native target or module:
  owns equilibrium/Ipopt/GFPE/result-certification native code;
- regression native target or module:
  owns regression/Ceres/objective/residual native code.

Acceptance requirements for the split:

- provider target does not link Ceres;
- provider target does not link Ipopt;
- equilibrium target owns Ipopt linkage;
- equilibrium target does not link Ceres;
- regression target owns Ceres linkage;
- regression target does not require Ipopt by default;
- extension-owned native code is not compiled into provider-only `_core`;
- `epcsaft._core` is no longer a dumping ground for extension bindings.

## Temporary Monorepo Staging Policy

The workspace may temporarily use `packages/epcsaft-equilibrium` and
`packages/epcsaft-regression` to prove Python packaging, ownership boundaries,
and provider-contract consumption before extraction.

That staging state is temporary only.

Rules for staging folders:

- they exist only to prove the final split before repo extraction;
- they must not be documented as the final layout;
- they must not justify keeping extension native code in the provider forever;
- they must be deleted from the core repo after the true sibling repos exist and
  the migration lands.

## Test Ownership Matrix

Every test must have one owner:

- core provider repo;
- equilibrium repo;
- regression repo;
- explicit cross-repo integration lane.

Rules:

- provider API, provider contract, provider-only build proof, and provider
  symbol-surface checks belong to core;
- equilibrium route/capability/result/Ipopt tests belong to
  `epcsaft-equilibrium`;
- regression dataset/optimizer/Ceres/result tests belong to
  `epcsaft-regression`;
- only explicit cross-package workflows belong to the integration lane.

No test should remain in the provider repo if it primarily proves extension
internals after extraction.

## CI And Validation Matrix

### Core CI

Must prove:

- provider-only install/build without Ceres and Ipopt;
- provider API tests;
- provider contract tests;
- provider-only `_core` symbol surface;
- package boundary and docs as owned by the core repo.

### Equilibrium CI

Must prove:

- install/build against released or sibling-checkout `epcsaft`;
- Ipopt-backed equilibrium native build;
- equilibrium API/capability/result/contract tests;
- no Ceres dependency.

### Regression CI

Must prove:

- install/build against released or sibling-checkout `epcsaft`;
- Ceres-backed regression native build;
- regression API/result/contract tests;
- no default Ipopt requirement.

### Integration CI

Must prove:

- explicit combined workflows only;
- optional regression-plus-equilibrium lanes when those target families need
  both packages;
- no hidden dependency cycle between the two extension packages.

## Documentation Requirements

Core docs must:

- stop describing extension internals as core-owned;
- explain the provider-only contract and provider-native SDK;
- document sibling local development using editable installs or `uv` path
  sources;
- avoid any submodule language.

Each extension repo must have:

- `README`;
- docs site or docs tree;
- package guide;
- build instructions;
- capability docs;
- compatibility docs naming required `epcsaft` versions.

## PyPI And Release Choreography

Release order:

1. release `epcsaft` first;
2. release `epcsaft-equilibrium` against the supported `epcsaft` range;
3. release `epcsaft-regression` against the supported `epcsaft` range.

Release requirements:

- trusted publishers exist for each package;
- release notes explain ownership and migration;
- compatibility ranges are explicit;
- install examples are user-facing and current:

```text
pip install epcsaft
pip install epcsaft epcsaft-equilibrium
pip install epcsaft epcsaft-regression
pip install epcsaft epcsaft-equilibrium epcsaft-regression
```

The provider release is not allowed to imply that Ceres regression or Ipopt
equilibrium remain core-owned.

## Honest Repository Creation Standard

Create `ePC-SAFT/epcsaft-equilibrium` and `ePC-SAFT/epcsaft-regression` only
when the contents are honest extension repos, not placeholders.

Each new repo must include:

- `pyproject.toml`;
- `README`;
- `LICENSE`;
- docs;
- tests;
- CI workflows;
- publish workflow;
- `CODEOWNERS`;
- issue templates;
- branch protection;
- labels;
- Dependabot and dependency graph settings;
- project-board linkage;
- compatibility docs naming required `epcsaft` versions.

## Downstream Migration Gates

Downstream migration starts only after all of the following are true:

- provider contract is frozen and tested;
- sibling local repos exist and install together without private workarounds;
- core provider build/install proof passes without Ceres and Ipopt;
- equilibrium package install/build proof passes with Ipopt;
- regression package install/build proof passes with Ceres;
- optional combined integration lane passes;
- user-facing docs and examples point to the correct package owners.

Downstream repos must migrate by normal dependency updates, not by copying code
or vendoring private internals.

## Cleanup And Removal Requirements

After extraction, remove from core:

- `packages/epcsaft-equilibrium`;
- `packages/epcsaft-regression`;
- moved equilibrium C++ sources;
- moved regression C++ sources;
- stale CMake targets;
- stale root exports;
- stale tests;
- stale scripts;
- stale capability claims;
- hidden compatibility wrappers.

The cleanup is part of completion, not optional follow-up work.

## Phase Gates

### Phase 0: Roadmap And Governance Freeze

Goal:

- make this roadmap authoritative before more extraction-facing work;
- prepare the GitHub organization, labels, boards, permissions, and publisher
  preflight.

Exit gate:

- the roadmap, ADR, build protocol, and package architecture docs agree on the
  target state;
- organization prerequisites are either completed or explicitly blocked with
  evidence.

### Phase 1: Provider-Only Core Boundary

Goal:

- prove that core can build and install as a provider-only package.

Required implementation:

- direct build path supports Ceres OFF and Ipopt OFF;
- provider-only `_core` exports provider-only symbols;
- provider-only tests fail if equilibrium or regression symbols leak;
- provider docs and validation commands describe the provider-only proof.

Exit gate:

- provider-only build/install proof passes without Ceres and Ipopt;
- provider-only API and symbol-surface tests pass;
- no provider runtime path claims extension ownership.

### Phase 2: Contract Freeze And Internal Native Split

Goal:

- freeze the provider contract and make the transition workspace reflect the
  future split honestly.

Required implementation:

- provider API contract and native SDK contract are versioned and tested;
- current public surfaces have future owners;
- internal staging packages consume the provider contract;
- native target ownership is explicit and enforced by tests.

Exit gate:

- provider contract, native contract, and ownership docs are aligned;
- extension staging packages are honest consumers of the provider contract;
- no hidden provider-to-extension import path is required.

### Phase 3: Honest Extension Package Readiness

Goal:

- make the staging packages honest enough that repo extraction can preserve real
  ownership instead of placeholder shells.

Required implementation:

- equilibrium owns its Python workflow modules and extension-facing tests;
- regression owns its Python workflow modules and extension-facing tests;
- native code is split to extension-owned targets or modules;
- CI lanes are package-specific plus explicit integration.

Exit gate:

- sibling local proof works through explicit dependency wiring;
- extension repos could be created without immediately violating ownership.

### Phase 4: Repository Creation And Transfer

Goal:

- transfer the provider repo into the organization and create honest extension
  repos.

Required implementation:

- transfer current repo to `ePC-SAFT/ePC-SAFT`;
- create extension repos only when contents are real;
- configure branch protection, labels, templates, CODEOWNERS, workflows,
  Dependabot, and publishers.

Exit gate:

- organization repos exist with honest contents and working CI/publish flows.

### Phase 5: Coordinated Release And Cleanup

Goal:

- publish the package set and remove moved code from core.

Required implementation:

- coordinated package releases with compatibility pins;
- downstream migration proof;
- cleanup/removal of moved core code and staging folders.

Exit gate:

- all three repos, PyPI packages, docs, and install proofs agree;
- the core repo no longer contains permanent extension code.

## First Implementation Slice

The first implementation slice starts here:

1. update this roadmap until it fully defines the target state and gates;
2. inspect the current CMake target split and native symbol surface;
3. make the core build support a provider-only profile with Ceres OFF and Ipopt
   OFF;
4. ensure provider-only `epcsaft._core` exposes provider-only symbols only;
5. add tests that fail if equilibrium/regression symbols leak into provider-only
   core;
6. update validation commands and docs to reflect the implemented boundary.

Focused validation for this slice:

```powershell
uv run python run_pytest.py --provider-api -q
uv run python run_pytest.py --integration -q
uv run python run_pytest.py --native-contracts -q
uv run python scripts/dev/validate_project.py quick
uv run python scripts/dev/validate_project.py docs
```

Use the smallest relevant command first. Full docs validation is required when
docs changed. Native-contract validation is required when the provider/native
boundary or `_core` symbol surface changes.

## Completion Definition For The Full Transfer

The transfer is complete only when all of these are true:

- `ePC-SAFT/ePC-SAFT` is the core provider repo;
- `ePC-SAFT/epcsaft-equilibrium` is the equilibrium extension repo;
- `ePC-SAFT/epcsaft-regression` is the regression extension repo;
- the final local sibling-repo layout is the real development layout;
- no Git submodules are used;
- core builds and installs without Ceres and Ipopt;
- equilibrium builds and installs against `epcsaft` with Ipopt;
- regression builds and installs against `epcsaft` with Ceres;
- optional regression/equilibrium integration is explicit and separately tested;
- docs, CI, package metadata, publishers, and releases agree on ownership;
- downstream repos consume the correct packages through generic APIs;
- no stale provider-owned extension code, wrappers, targets, or claims remain.
