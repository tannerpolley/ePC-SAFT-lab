# M1 Local Linux Package Reproducibility

Milestone: `M1 - Packages`
Issue: `https://github.com/ePC-SAFT/ePC-SAFT/issues/435`
Status: `approved; tracker published`
Last synced: `2026-07-10`

## Summary

Replace the original Tasks 16-18 release-hardening program with one bounded
local Linux proof: on the repository's current Python minor, build the provider
and both extension packages, install the supported local artifact combinations
outside the source tree, execute representative native smokes, and retain one
machine-readable environment/artifact receipt.

This is private-project reproducibility work. It makes no manylinux breadth,
PyPI, multi-Python, cross-distribution, or public release promise.

## Context And Verified Current Behavior

- `.python-version` pins Python `3.13`; `uv run --no-sync python` resolves to
  CPython `3.13.14` (the unscoped host `python` is 3.12.3 and is not the
  repository proof runtime).
- The current host is Zorin OS 18.1 (`ubuntu`/`debian` family), `x86_64`, with
  CMake 3.28.3, Ninja 1.11.1, and GCC 13.3.0. These values describe the current
  receipt; they are not a portability claim.
- Provider, equilibrium, and regression package metadata currently declare
  Python `>=3.9`, while active build workflows use Python 3.13.
- `scripts/dev/build_dist.py` builds provider artifacts.
- `scripts/dev/build_extension_dists.py` builds extension artifacts from the
  monorepo or installed provider SDK and requires a real Ipopt root for the
  equilibrium package.
- `scripts/dev/check_release_installs.py` enumerates provider-only,
  provider-plus-equilibrium, provider-plus-regression, and all-package installs,
  but currently proves imports and provider-SDK metadata rather than complete
  isolated native smokes.
- The build protocol correctly assigns CppAD to the provider, Ipopt to
  `epcsaft-equilibrium`, and Ceres to `epcsaft-regression`.

## Goals

1. Define one canonical local Linux package gate for Python 3.13.
2. Build provider, equilibrium, and regression artifacts from one commit and
   one recorded native dependency environment.
3. Prove all four supported installation combinations outside the checkout.
4. Run native provider, current-public equilibrium, and regression-component
   smokes without source-path leakage.
5. Record artifact hashes, installed origins, native dependency resolution,
   commands, and environment identity.
6. Replace release-oriented local naming where it would overstate this proof.

## Non-Goals

- No manylinux tag selection, container baseline, auditwheel policy breadth, or
  compatibility claim for older Linux/glibc systems.
- No PyPI publisher, upload, release tag, GitHub release, or downstream public
  installation campaign.
- No Python 3.9-3.12, Python 3.14, PyPy, Windows, macOS, ARM, or musl matrix.
- No claim that a regression or equilibrium family is scientifically admitted
  merely because its native module imports or a component smoke runs.
- No scientific solver repair, capability change, or paper-validation work.
- No hidden dependency download, fallback build, or environment-specific path
  committed as a default.

## Alternatives

### Preserve The Original Manylinux And Multi-Python Program

Rejected. It solves a public distribution problem the private project does not
currently need and multiplies native dependency work without improving the
current local development loop.

### Prove Only A Source-Checkout Build

Rejected. A source build can pass while wheel contents, provider-SDK transfer,
installed imports, or native runtime dependency resolution are broken.

### Prove Current-Python Local Artifacts End To End

Selected. It is the smallest gate that verifies the actual local Linux package
workflow without implying portability or public release readiness.

## Selected Design

### Canonical Environment Contract

The gate reads the Python minor from `.python-version` and proves only the
current `3.13` line. It does not narrow the three packages' published
`requires-python` metadata or claim that older declared versions were tested by
this local gate. Metadata support is a separate release-policy decision.

The run receipt records, without converting them into compatibility promises:

- OS release, architecture, kernel, Python implementation/version;
- compiler, CMake, Ninja, uv, build-backend, and package versions;
- CppAD source/version, Ceres config path/version, Ipopt root/version, and
  BLAS/LAPACK/MUMPS linkage visible to the built artifacts;
- repository commit, dirty-state refusal, exact command arguments, and relevant
  environment variables.

The gate accepts an explicitly supplied or protocol-discovered local Ipopt root
and Ceres config. It records the resolved paths but never writes a user-specific
path into package defaults.

### Artifact Build

From a clean tracked worktree and an empty task-owned output directory:

1. build the provider wheel and sdist;
2. install that provider wheel into the SDK staging environment;
3. build `epcsaft-equilibrium` from the installed provider SDK with real Ipopt;
4. build `epcsaft-regression` from the installed provider SDK with real Ceres;
5. retain artifact filenames, versions, wheel tags, sizes, and SHA-256 hashes;
6. reject mixed commits, stale artifacts, duplicate versions, or missing
   extension-native modules.

The installed-provider route is the final package-boundary proof. Monorepo mode
may remain a development test but cannot substitute for it.

### Isolated Install Matrix

Create a new environment per combination, with working directory outside the
checkout, no checkout entries on `PYTHONPATH`, and `LD_LIBRARY_PATH` unset for
the installed-runtime step:

| Combination | Required smoke |
| --- | --- |
| `epcsaft` | Import provider/native module; construct explicit methane parameters; evaluate a native `State` property |
| provider + equilibrium | Import both native modules; run one currently admitted selector route with its traceable fixture |
| provider + regression | Import both native modules; run a bounded native regression component smoke without claiming family admission |
| all three | Repeat provider state plus equilibrium and regression smokes in one process and verify package/native origins |

Every import path must resolve inside the isolated environment. Installation
uses only the new local artifact directory, not editable installs or checkout
paths.

### Native Runtime Inspection And Receipt

For each native module, retain:

- installed absolute path and artifact hash;
- `NEEDED`, RPATH/RUNPATH, and resolved `ldd` entries;
- rejection of checkout, build-tree, user-cache, or missing-library resolution;
- native SDK contract identity and package version agreement;
- smoke command, exit status, and compact numerical output.

This inspection proves reproducibility on the recorded local host only. Wheel
tags are reported as artifact facts, not portability evidence.

## Ownership And Data Flow

| Concern | Owner |
| --- | --- |
| Cross-package build/install gate and local docs | M1 Packages |
| Provider wheel and SDK contract | `packages/epcsaft` |
| Ipopt extension artifact | `packages/epcsaft-equilibrium` |
| Ceres extension artifact | `packages/epcsaft-regression` |
| Scientific capability evidence | M3/M4/M5/M6, unchanged by this spec |

```text
clean commit + current Python + resolved local native dependencies
-> provider artifacts -> installed provider SDK
-> equilibrium/regression artifacts
-> four isolated install environments
-> native smokes + ELF inspection
-> one local reproducibility receipt
```

## Loud Errors And Stop Gates

Stop before building for a dirty tracked worktree, wrong Python minor, missing
compiler/build tool, unusable Ipopt/Ceres/CppAD input, or unresolved package
version mismatch. Stop before install for stale/mixed artifacts or hash/version
conflict. Stop the gate for source-path leakage, missing libraries, unexpected
RPATH/RUNPATH, module origin outside the environment, disabled required native
backend, nonzero smoke status, or missing receipt fields.

No no-Ipopt success path, Ceres omission, source-tree import, or import-only
smoke may satisfy the complete gate.

## Testing And Outcome Proof

- Unit tests cover environment capture, artifact selection, hash/version
  agreement, clean-environment construction, path-leak rejection, ELF parsing,
  and each smoke dispatch.
- Mutation tests inject stale wheels, checkout paths, missing shared libraries,
  wrong Python, mixed versions, and malformed receipts.
- Build-script tests preserve provider-only dependency boundaries and require
  installed-provider extension builds.
- The complete local run executes the canonical build helper, all four isolated
  combinations, native smokes, and receipt validation from a fresh task-owned
  output directory.
- Focused static proof includes build workflow tests, Ruff for changed Python,
  strict docs, `git diff --check`, and the cleanup audit.

The final receipt is accepted only when every combination passes in the same
run. Individual green jobs do not compose into a receipt across different
commits or environments.

## Cutover

- Replace the local semantics of `check_release_installs.py` with a clearly
  named local-Linux reproducibility command and update all repository callers in
  the same change. Do not leave a redirector.
- Remove local documentation that presents this gate as manylinux, multi-Python,
  PyPI, or public release proof.
- Preserve M7 release backlog documents as deferred public-release work; this
  M1 gate does not close issue #195.
- Keep package names and current public APIs unchanged.

## Risks

| Risk | Control |
| --- | --- |
| Local dependency drift | Record exact tool/dependency identities and artifact hashes |
| Passing through checkout imports | External cwd, isolated environments, origin assertions |
| Import succeeds but native operation fails | Representative native smokes for every installed extension |
| Component smoke overstates scientific support | Explicit component classification and unchanged capability tests |
| Active Python line changes | Update `.python-version` deliberately and rerun this entire local gate |
| Task leaves large build residue | Task-owned output root plus cleanup audit |

## Implementation-Plan Selections

1. The implementation plan selects the final command and receipt paths within
   existing `scripts/dev` and build-test conventions; it must replace, not wrap,
   the release-oriented local helper.
2. The exact admitted equilibrium smoke is selected from the currently exposed
   routes at implementation time and recorded in the receipt; a closed family
   cannot be substituted.
3. The regression component smoke must exercise native Ceres input without
   implying production family admission; Tasks 10-12 own that later claim.

## Decision Ledger

| Decision | Evidence | Outcome | Status |
| --- | --- | --- | --- |
| Milestone | Work proves monorepo package boundaries for one local environment | M1 Packages, not M7 Release | Selected for review |
| Platform breadth | Private project needs current Zorin/Ubuntu-family Linux workflow | Record host; make no cross-Linux promise | Selected for review |
| Python breadth | `.python-version` and active workflows use 3.13 | Prove Python 3.13 locally without changing broader package metadata | Selected for review |
| Artifact boundary | Source checkout can hide packaging faults | Installed-provider artifacts are required | Selected for review |
| Install matrix | Three distributions have four supported combinations | Prove all four in isolated environments | Selected for review |
| Native proof | Import-only checks miss runtime linkage and dispatch faults | Run native smokes and inspect ELF resolution | Selected for review |
| Release scope | No current need for manylinux/PyPI/public hardening | Defer M7 issue #195 | Selected for review |
