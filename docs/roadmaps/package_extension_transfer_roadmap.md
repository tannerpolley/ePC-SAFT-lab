# ePC-SAFT Organization Transfer Roadmap

Date: 2026-05-27

Purpose: summarize the package-split advice in
`docs/ChatGPT_Gemini_Responses/ePC-SAFT_Organization.md`, give a direct
technical opinion, and define the staged roadmap for moving the project into the
`ePC-SAFT` GitHub organization and eventually into core, equilibrium, and
regression repositories.

This document is a planning roadmap. It does not by itself change the current
package contract. Contract changes must land through an ADR, roadmap updates,
build-protocol updates, tests, and release documentation.

## Current Public Organization State

The public `ePC-SAFT` GitHub organization currently exists at
<https://github.com/ePC-SAFT>. On 2026-05-27, the public organization page
reported no public repositories and no public members. That empty public state
is useful: configure governance before transferring the current repository or
creating extension repositories.

GitHub's transfer documentation matters for this migration:

- A repository transfer preserves repository contents, issues, pull requests,
  releases, projects, settings, stars, watchers, wiki, webhooks, secrets, deploy
  keys, and commit history.
- Existing web and Git URLs redirect after transfer, but local clones should
  still update `origin` to the new URL.
- GitHub Pages URLs are not redirected by repository transfer.
- Creating a new repository or fork at the previous location permanently
  removes the redirect.
- Transferring into an organization requires permission to create repositories
  in the target organization.
- Organization default repository permissions apply after transfer.

## Conversation Summary

The ChatGPT/Gemini conversation makes one strong recommendation:

`epcsaft` should become the core thermodynamic provider, while Ceres-backed
regression and Ipopt-backed equilibrium should become extension packages and,
eventually, separate repositories.

Suggested end-state:

```text
ePC-SAFT/ePC-SAFT              # current repo, core EoS/provider package
ePC-SAFT/epcsaft-equilibrium   # Ipopt-backed equilibrium extension
ePC-SAFT/epcsaft-regression    # Ceres-backed regression extension
```

The conversation also correctly identifies that the split should not start as a
repo extraction. It should start with internal package boundaries, dependency
boundaries, tests, and a provider contract. The current public equilibrium and
regression APIs are still moving, so extracting first would create cross-repo
churn before the interfaces are stable.

Important details from the conversation:

- Keep CppAD/exact derivative support close to the core EoS provider because
  both regression and equilibrium need derivative-capable thermodynamic
  functions.
- Make `epcsaft-equilibrium` own phase discovery, GFPE route assembly,
  stability checks, Ipopt options, postsolve certification, and equilibrium
  result schemas.
- Make `epcsaft-regression` own target datasets, parameter maps, Ceres residual
  blocks, optimizer diagnostics, and regression result schemas.
- Allow `epcsaft-regression` to optionally integrate with
  `epcsaft-equilibrium` for target rows that require phase or reactive
  equilibrium solves.
- Use one organization-level GitHub Project for coordination, but keep source of
  truth in docs, ADRs, issues, PRs, CI, and releases.
- Use CODEOWNERS, protected `main`, consistent labels, shared issue templates,
  deliberate releases, and Dependabot/dependency graph settings across repos.

## Opinion

I agree with the split target. It is the right long-term architecture.

The scientific boundary is real: the EoS provides thermodynamic functions;
regression and equilibrium are algorithms that consume those functions. Ceres
and Ipopt should not burden users who only need property evaluation, fugacity
coefficients, activity coefficients, chemical potentials, or density/pressure
closure.

I do not think the code should be split into separate repos immediately. The
current roadmap and build protocol still define native regression and production
equilibrium as core package capabilities. The current repo has public docs,
release docs, build workflows, issue-tracker docs, PyPI trusted-publisher text,
and package metadata that still point at `tannerpolley/ePC-SAFT`. Moving folders
before changing those contracts would produce a partially split project with
contradictory instructions.

The right sequence is:

```text
1. Decide the contract in an ADR.
2. Update source-of-truth docs so future agents stop treating Ceres and Ipopt
   as core-package dependencies.
3. Freeze a provider API and derivative/result contract.
4. Enforce import and dependency boundaries inside this repo.
5. Move code into internal package roots.
6. Transfer the current repository to the organization once org governance and
   publishing checks are ready.
7. Extract extension repositories only after internal boundaries pass tests.
8. Cut coordinated releases.
```

Do not keep long-lived compatibility wrappers in the core package. If
`Equilibrium`, `TargetDataset`, and `fit_*` ownership moves to extension
packages, make that a documented breaking change at a coordinated release
boundary and remove the old core-owned path in the same migration.

## End-State Ownership

### Core Repository: `ePC-SAFT/ePC-SAFT`

Public package/distribution: `epcsaft`

Owns:

- residual Helmholtz energy and contribution maps
- hard-chain, dispersion, association, Debye-Huckel, Born, and related EoS terms
- `ParameterSet`
- mixture and state construction
- property evaluation
- fugacity coefficients
- activity coefficients
- chemical potentials
- density and pressure closure
- derivative-capable provider functions
- contribution-level traces
- core `capabilities()` for provider-level behavior
- provider API contract consumed by extensions

Does not own after the split:

- Ceres optimizer loops
- Ipopt equilibrium routes
- GFPE route solvers
- parameter-regression target packing
- application-specific MEA, lithium, or absorption-column workflows

### Equilibrium Repository: `ePC-SAFT/epcsaft-equilibrium`

Public package/distribution: `epcsaft-equilibrium`

Import package: `epcsaft_equilibrium`

Owns:

- `Equilibrium(...)`
- route specs for bubble, dew, flash, LLE, electrolyte LLE, speciation,
  reactive equilibrium, reactive LLE, and reactive electrolyte LLE
- GFPE route assembly
- phase eligibility masks
- phase discovery and stability checks
- Ipopt NLP assembly and option profiles
- postsolve certification
- route diagnostics
- equilibrium result and capability schemas

Depends on:

- `epcsaft`
- Ipopt

Does not depend on:

- Ceres
- downstream MEA or lithium repositories

### Regression Repository: `ePC-SAFT/epcsaft-regression`

Public package/distribution: `epcsaft-regression`

Import package: `epcsaft_regression`

Owns:

- `TargetDataset`
- `TargetRow`
- `RegressionProblem`
- parameter maps and bounds
- Ceres residual blocks
- optimizer diagnostics
- parameter movement reports
- regression result and capability schemas
- pure, binary, ion, Born, association, and other generic parameter-fit workflows

Depends on:

- `epcsaft`
- Ceres

Optional integration:

- `epcsaft-equilibrium` for VLE, LLE, electrolyte LLE, speciation, reactive
  pressure, and reactive phase-equilibrium target rows.

The default regression install must not require Ipopt. The
equilibrium-target regression lane may require both extension packages.

## Roadmap

### Phase 0: Organization Preparation

Goal: make the empty organization ready before any repository moves.

Actions:

- Set organization display name, description, avatar, contact email, and profile
  README if desired.
- Create teams:
  - `maintainers`
  - `core`
  - `equilibrium`
  - `regression`
  - `build-release`
- Set organization base repository permission to no broad write access.
- Restrict repository creation to maintainers until the split is complete.
- Create one organization Project named `ePC-SAFT Roadmap`.
- Add Project fields:
  - `Package`: core, equilibrium, regression, benchmark, downstream
  - `Capability`: eos, derivatives, vle, lle, electrolyte, reactive, regression
  - `Backend`: analytic, CppAD, implicit, Ceres, Ipopt
  - `Status`: blocked, ready, in progress, review, merged
  - `Release target`: core-0.x, equilibrium-0.x, regression-0.x, future
- Prepare shared labels:
  - `area:core`
  - `area:equilibrium`
  - `area:regression`
  - `area:derivatives`
  - `area:build`
  - `area:docs`
  - `area:benchmark`
  - `backend:cppad`
  - `backend:ceres`
  - `backend:ipopt`
  - `status:blocked`
  - `status:needs-design`
  - `status:ready`
  - `status:breaking-change`
  - `release:blocker`
- Decide the transferred core repo name:
  - Recommended immediate transfer name: `ePC-SAFT/ePC-SAFT`, preserving the
    current repository name and minimizing release-history confusion.
  - Optional later rename: `ePC-SAFT/epcsaft`, only in a release window.
- Do not create a placeholder repository at `tannerpolley/ePC-SAFT` after
  transfer, because that would destroy GitHub's redirect.

Exit criteria:

- The organization has maintainers and team permissions configured.
- The org Project and shared labels exist.
- No repo with a conflicting target name exists in the organization.
- The transfer owner has permission to create repositories in `ePC-SAFT`.

### Phase 1: Contract Decision PR

Goal: make the repo's source-of-truth docs agree on the package split before
moving code.

Create:

- `docs/adr/0005-package-extension-split.md`

Modify:

- `docs/roadmaps/FULL_ROADMAP.md`
- `docs/protocols/build_package_dependency_protocol.rst`
- `docs/pages/project_structure.rst`
- `docs/pages/development_workflows.rst`
- `docs/pages/publishing.rst`
- `README.md`
- `pyproject.toml`
- `.github/workflows/publish-pypi.yml`
- `docs/agents/issue-tracker.md`

Decision to record:

```text
epcsaft core owns the EoS/provider contract.
epcsaft-equilibrium owns Ipopt-backed equilibrium.
epcsaft-regression owns Ceres-backed regression.
CppAD/exact derivative provider support remains in core where the EoS algebra
and implicit EoS states live.
```

Documentation changes:

- Replace language that says Ceres and Ipopt are core package dependencies with
  language that assigns them to the regression and equilibrium packages.
- Keep the current completion standard, but scope it to the package that owns
  the capability.
- Keep downstream-facing generic API requirements, and continue forbidding
  application-specific MEA, lithium, and absorption-column public APIs.
- Define how `capabilities()` works after split:
  - core `epcsaft.capabilities()` reports provider capability only.
  - extension packages expose their own capability reports.
  - any aggregate capability view must be explicit and test-backed.

Exit criteria:

- No source-of-truth doc contradicts the ADR.
- Build documentation clearly separates provider, regression, and equilibrium
  dependency ownership.
- Publishing docs identify the future organization repository and PyPI trusted
  publisher changes.
- A search for old repository URLs identifies only intentional release history
  references or entries scheduled for the transfer PR.

Suggested validation:

```powershell
rg -n "tannerpolley/ePC-SAFT|github.com/tannerpolley" README.md pyproject.toml docs .github
rg -n "Ceres|Ipopt|core package capabilities|core capabilities" docs README.md
```

### Phase 2: Provider API Contract

Goal: define the smallest stable contract extensions need from core.

Create:

- `docs/contracts/provider_api_v1.md`
- `docs/contracts/extension_compatibility.md`
- `tests/native/contracts/test_provider_api_contract.py`
- `tests/workflows/build/test_extension_boundary_contract.py`

Contract must cover:

- package version and provider contract version
- `ParameterSet` schema
- mixture/state input schema
- core property result schema
- derivative result schema
- contribution trace schema
- error and diagnostic schema
- capability evidence schema
- native ABI expectations for extension builds

Testing must prove:

- core imports without Ceres or Ipopt loaded as runtime requirements
- core provider functions expose the derivative information required by both
  extension packages
- provider schemas are serializable and versioned
- capability claims cannot silently broaden without evidence updates

Exit criteria:

- Provider contract tests pass.
- Core public API is narrow enough for extension consumption.
- Every existing equilibrium/regression call that will move has a mapped future
  owner.

### Phase 3: Internal Package Boundary Split

Goal: prove package boundaries inside this repo before repo extraction.

Recommended intermediate layout:

```text
packages/
  epcsaft/
    pyproject.toml
    src/epcsaft/
  epcsaft-equilibrium/
    pyproject.toml
    src/epcsaft_equilibrium/
  epcsaft-regression/
    pyproject.toml
    src/epcsaft_regression/
```

This is a large change. If the first implementation needs a smaller step, start
with import-boundary tests against the current `src/epcsaft/` layout, then move
to `packages/` once the tests define the boundary.

Boundary rules:

- `epcsaft` must not import `epcsaft_equilibrium`.
- `epcsaft` must not import `epcsaft_regression`.
- `epcsaft` must not reference Ceres or Ipopt in public provider runtime paths.
- `epcsaft_equilibrium` may depend on `epcsaft` and Ipopt.
- `epcsaft_equilibrium` must not depend on Ceres.
- `epcsaft_regression` may depend on `epcsaft` and Ceres.
- `epcsaft_regression` must not require Ipopt unless the equilibrium-target
  integration lane is explicitly selected.

Implementation order:

1. Add import-boundary tests.
2. Move core-only Python provider code into the core package root.
3. Move equilibrium Python frontends into `epcsaft_equilibrium`.
4. Move equilibrium native code under an extension-owned native tree.
5. Move regression Python frontends into `epcsaft_regression`.
6. Move regression native code under an extension-owned native tree.
7. Update CMake targets so Ceres and Ipopt belong to the extension builds.
8. Update validation orchestration to run provider, equilibrium, regression, and
   integration lanes separately.

Exit criteria:

- `uv run python scripts/dev/validate_project.py quick` passes for the adjusted
  current repo.
- Provider-only install proof passes without Ceres and Ipopt.
- Equilibrium extension install proof passes with Ipopt.
- Regression extension install proof passes with Ceres.
- Regression-with-equilibrium integration proof passes with both extensions.
- No moved public API remains in core as a hidden compatibility path.

### Phase 4: Capability Migration

Goal: move functionality ownership without lowering scientific completion
standards.

Equilibrium migration:

- Move `Equilibrium(...)` ownership to `epcsaft_equilibrium`.
- Move Ipopt route assembly, option profiles, route diagnostics, phase
  discovery, postsolve certification, and GFPE-specific capability reporting.
- Keep provider derivative calls in core.
- Keep tests that prove every exposed route uses production native code,
  exact/implicit derivative support, and literature-backed or contract-backed
  evidence.

Regression migration:

- Move `TargetDataset`, `TargetRow`, fit entrypoints, Ceres residual blocks,
  parameter maps, bounds, optimizer diagnostics, and regression capability
  reporting.
- Add a separate integration module for equilibrium-backed target rows.
- Keep core-only regression rows independent from Ipopt.

Exit criteria:

- Extension packages can be installed from sibling checkouts.
- Downstream projects can call the new extension APIs with no private package
  workaround.
- `capabilities()` and extension capability reports do not claim unsupported
  routes.
- Documentation examples import from the package that owns the workflow.

### Phase 5: Transfer Current Repository To The Organization

Goal: move the current upstream source of truth from
`tannerpolley/ePC-SAFT` to `ePC-SAFT/ePC-SAFT`.

Preflight:

- Confirm target org permissions.
- Confirm no target repo name conflict.
- Audit GitHub Actions environments, especially `pypi`.
- Update or prepare PyPI trusted-publisher records for the new org/repo.
- Audit workflow text that expects `tannerpolley/ePC-SAFT`.
- Audit `pyproject.toml` project URLs.
- Audit README, Sphinx docs, release docs, downstream protocol docs, and issue
  tracker docs.
- Check whether GitHub Pages is enabled; if so, plan a separate Pages URL
  migration because GitHub transfer redirects do not cover Pages URLs.

Transfer:

1. Transfer `tannerpolley/ePC-SAFT` to the `ePC-SAFT` organization.
2. Keep the repo name `ePC-SAFT` for the first transfer.
3. Update local clones:

   ```powershell
   git remote set-url origin https://github.com/ePC-SAFT/ePC-SAFT.git
   ```

4. Update docs and metadata from old URLs to the new canonical URL.
5. Update GitHub Actions and PyPI trusted-publisher configuration.
6. Run quick validation and release/publishing preflight.

Exit criteria:

- GitHub repository URL is `https://github.com/ePC-SAFT/ePC-SAFT`.
- Local `origin` points at the organization URL.
- CI runs in the organization repository.
- PyPI trusted-publisher preflight references the organization repository.
- User-facing docs point at the organization repository.
- Old URL redirects work and no replacement repo exists at the old location.

### Phase 6: Extract Extension Repositories

Goal: create true separate repositories after internal package boundaries pass.

Create:

```text
ePC-SAFT/epcsaft-equilibrium
ePC-SAFT/epcsaft-regression
```

Extraction policy:

- Prefer history-preserving extraction for extension-owned code when practical.
- Use a clean import only if history preservation would create a misleading or
  oversized repository.
- Remove moved extension code from core in the same coordinated migration.
- Do not leave redirect modules, duplicated native code, or dead CMake branches
  in core.

Each new repo must have:

- `pyproject.toml`
- README
- license file
- package docs
- CMake/native build docs if native code exists
- GitHub Actions CI
- publish workflow
- issue templates
- CODEOWNERS
- protected `main`
- Dependabot/dependency graph settings
- compatibility docs naming required `epcsaft` versions
- contract tests against the core provider API

Exit criteria:

- `epcsaft-equilibrium` installs against released or sibling-checkout
  `epcsaft`.
- `epcsaft-regression` installs against released or sibling-checkout `epcsaft`.
- `epcsaft-regression` equilibrium-target lane installs only when
  `epcsaft-equilibrium` is present.
- Core package install and tests pass without extension packages.
- Downstream smoke checks pass with explicit extension dependencies.

### Phase 7: Coordinated Releases

Goal: publish usable packages with narrow compatibility windows.

Release set:

```text
epcsaft             0.x    # provider API v1
epcsaft-equilibrium 0.1.x  # requires epcsaft >=0.x,<0.y
epcsaft-regression  0.1.x  # requires epcsaft >=0.x,<0.y
```

Release requirements:

- Core release notes explain that core no longer owns Ceres regression or Ipopt
  equilibrium routes.
- Extension release notes identify supported core versions.
- PyPI projects and trusted publishers exist for each package.
- GitHub Releases include wheels/sdists or document source build requirements.
- Docs show install choices:

  ```text
  pip install epcsaft
  pip install epcsaft epcsaft-equilibrium
  pip install epcsaft epcsaft-regression
  pip install epcsaft epcsaft-equilibrium epcsaft-regression
  ```

- Downstream repos pin explicit package dependencies.

Exit criteria:

- A clean environment can install each package combination.
- Downstream MEA, lithium, and column smoke workflows use generic extension
  APIs.
- No downstream repo copies EoS, equilibrium, or regression implementation code.

## First Implementation PR

The first PR should be docs and tests only. Do not move production code in the
first PR.

Scope:

- Add `docs/adr/0005-package-extension-split.md`.
- Update `docs/roadmaps/FULL_ROADMAP.md` to state that the completion standard
  follows the owning package after the split.
- Update `docs/protocols/build_package_dependency_protocol.rst` so Ceres belongs
  to regression and Ipopt belongs to equilibrium.
- Add import/dependency boundary tests that initially document the current
  failing state.
- Update publishing docs with the organization-transfer implications.

The second PR should make the boundary tests pass without moving files between
repos. Only after those tests pass should code move into internal package roots.

## Risk Register

Interface instability:

- Risk: equilibrium and regression APIs are still evolving.
- Control: freeze provider/result/derivative contracts before repo extraction.

Native build duplication:

- Risk: each repo grows its own inconsistent CMake and dependency logic.
- Control: extract shared build conventions only after the core provider target
  and extension targets are clear.

Regression-equilibrium dependency cycle:

- Risk: regression imports equilibrium by default and pulls Ipopt into all
  regression installs.
- Control: make equilibrium-target regression an explicit integration lane.

Stale docs and old URLs:

- Risk: install docs, PyPI workflow text, release docs, and issue tracker docs
  continue pointing at `tannerpolley/ePC-SAFT`.
- Control: transfer PR includes a narrow URL search and updates user-facing docs.

PyPI trusted publishing:

- Risk: OIDC publisher claims no longer match after transfer.
- Control: update PyPI trusted publisher settings before the first org-owned
  publish run.

GitHub Pages:

- Risk: repository transfer does not redirect Pages URLs.
- Control: audit Pages separately and document the new URL if Pages is enabled.

Capability overclaims:

- Risk: core or extensions report routes that moved or are not implemented.
- Control: capability reports stay package-owned and evidence-backed.

Old location reuse:

- Risk: creating a placeholder repo at `tannerpolley/ePC-SAFT` destroys the
  transfer redirect.
- Control: do not create a replacement repo or fork at the old location.

## Completion Definition For The Full Transfer

The full transfer is complete only when all of these are true:

- The current upstream repo lives under `ePC-SAFT`.
- Core provider docs, metadata, workflows, and PyPI publisher settings reference
  the organization-owned repository.
- The extension split has an accepted ADR and matching source-of-truth docs.
- Core can install and validate without Ceres and Ipopt.
- Equilibrium can install and validate with Ipopt.
- Regression can install and validate with Ceres.
- Regression/equilibrium integration is explicit and separately tested.
- Extension repositories exist only after internal boundaries pass.
- Downstream smoke workflows use generic APIs from the correct package.
- No stale core-owned Ceres/Ipopt workflow, dead code, or hidden compatibility
  path remains in `epcsaft`.
