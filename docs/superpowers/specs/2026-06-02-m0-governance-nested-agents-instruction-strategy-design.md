# Nested AGENTS.md Instruction Strategy Design

## Project Context Evidence

- Root `AGENTS.md` owns repo-wide routing, IntelliJ/MCP policy, tracker rules, package-boundary invariants, and cleanup expectations.
- `docs/superpowers/PROJECT_CONTEXT.md` defines the package identity, milestone ownership, CppAD-only public derivative policy, and provider/equilibrium/regression split.
- ADR 0005 assigns long-term package ownership: `epcsaft` is the provider, `epcsaft-equilibrium` owns Ipopt-backed equilibrium, and `epcsaft-regression` owns Ceres-backed regression.
- `docs/pages/project_structure.rst` defines analysis layout, including figure-owned `source/`, `scripts/`, and `results/` folders plus the paper-validation parameter snapshot rules.
- User-level architecture policy prefers a small number of high-value nested instruction files over blanketing every folder.

## User Decisions

- Use the Superpowers Project docs model under `docs/superpowers`.
- Save one design spec for nested repo instructions.
- Lock the nested instruction strategy to five targeted files:
  - `packages/epcsaft/AGENTS.md`
  - `packages/epcsaft-equilibrium/AGENTS.md`
  - `packages/epcsaft-regression/AGENTS.md`
  - `analyses/AGENTS.md`
  - `analyses/paper_validation/AGENTS.md`

## Recommended Approach

Create five concise nested `AGENTS.md` files. Each file should only add subtree-specific behavior that changes how agents work in that subtree. Do not duplicate root rules, Git policy, global cleanup policy, or the full package-context document.

This keeps instruction discovery predictable: root rules remain the common contract, and nested files sharpen package or analysis behavior when the working directory enters that subtree.

## Draft File Contents

### `packages/epcsaft/AGENTS.md`

```markdown
# Provider Package Instructions

This subtree owns the core `epcsaft` provider package: `Mixture`, `State`,
`ParameterSet`, `ModelOptions`, EOS/property evaluation, provider-native `_core`,
CppAD derivative substrate, provider capability evidence, and the provider SDK.

Do not add equilibrium route assembly, Ipopt ownership, Ceres optimizer logic,
or regression workflow behavior here. If provider work appears to require those,
split the issue by package/milestone.

Provider public derivatives must remain CppAD-backed where public payloads claim
derivative support. Missing derivative coverage is an implementation gap, not a
runtime mode.

Keep native SDK manifests, CMake source lists, pybind bindings, `.pyi` surfaces,
and provider tests aligned when moving native or public-provider code.

Focused validation:
- `uv run python run_pytest.py --provider-api -q`
- `uv run python run_pytest.py --native -q`
- Provider-only native boundary: `uv run python scripts/dev/build_epcsaft.py --clean --profile provider`
```

### `packages/epcsaft-equilibrium/AGENTS.md`

```markdown
# Equilibrium Package Instructions

This subtree owns `epcsaft-equilibrium`: `Equilibrium`, route specs, selector
admission, native activation matrix consumption, GFPE assembly, Ipopt NLPs,
route scaling, postsolve certification, equilibrium diagnostics, and equilibrium
capability evidence.

Provider EOS supplies thermodynamic state/property and local derivative data.
Equilibrium owns pressure-transformed objective assembly, route residuals,
Jacobians, Hessians, tensors, NLP contracts, and solver-status acceptance.

Do not expose declared-not-exposed route families as callable production routes.
Do not treat acceptable Ipopt statuses, iteration-limit seeds, or diagnostic
staged workflows as completion evidence.

Any broadened route claim must update activation/capability evidence and run a
route-appropriate focused proof.

Focused validation:
- `uv run python run_pytest.py --equilibrium-api -q`
- `uv run python run_pytest.py --native-contracts -q`
- Debug one route only: `uv run python run_pytest.py --equilibrium-debug -q -s packages/epcsaft-equilibrium/tests/api/test_equilibrium.py::test_equilibrium_bubble_pressure_uses_trusted_cppad_ipopt_route`
```

### `packages/epcsaft-regression/AGENTS.md`

```markdown
# Regression Package Instructions

This subtree owns `epcsaft-regression`: `Regression`, target datasets, target
family summaries, Ceres residual blocks, parameter maps and bounds, optimizer
diagnostics, regression result schemas, and regression capability evidence.

Do not move regression optimizer loops, Ceres ownership, or regression result
contracts into the provider package. Provider code may supply parameter payloads
and CppAD derivative inputs only through provider-owned public contracts.

Regression claims require native optimizer evidence, derivative evidence, and
package-local tests. Dependency presence alone is not capability evidence.

Focused validation:
- `uv run python run_pytest.py --regression -q`
- `uv run python scripts/dev/validate_project.py regression`
```

### `analyses/AGENTS.md`

```markdown
# Analysis Workflow Instructions

This subtree owns source-controlled scientific analyses, validation studies,
and figure workflows. It is not package runtime code.

Keep each analysis self-contained under `analyses/{category}/{short_id}/`.
Use root `data/reference/` only for reusable stable inputs shared across
analyses or package tests.

Figure-owned layout is:
`figures/{figure_id}/source/`, `figures/{figure_id}/scripts/`, and
`figures/{figure_id}/results/`. Disposable run payloads go under
`figures/{figure_id}/results/runs/`.

Separate data generation from rendering. Retain exact plotted data snapshots
beside rendered figures and `.mpl.yaml` sidecars.

Do not place analysis scripts in root `scripts/`, package `src/`, or package
tests. Do not turn downstream metrics into package APIs.
```

### `analyses/paper_validation/AGENTS.md`

```markdown
# Paper Validation Instructions

Paper-validation analyses are retained literature reproduction workflows and
use the repo-specific exception layout from `docs/pages/project_structure.rst`.

Use `figures/figure_NN/source/` for source assets and
`figures/figure_NN/results/` for retained generated outputs. Use
`tables/table_###/source/` for extracted paper tables and conversions.

Parameter snapshots used to execute the analysis belong directly under
`parameters/mixed/`, `parameters/pure/`, and `parameters/user_options.json`.
Do not add nested dataset-name folders under `parameters/`.

Keep paper source manifests, copied paper notes, plotted data snapshots, and
rendered outputs traceable to the cited source. Application-specific conclusions
remain analysis output, not package capability claims.
```

## Alternatives Considered

### Package-Only Nested Instructions

This would add only the three package files. It reduces instruction count, but leaves analysis workflows relying on scattered docs and user-level policy. That misses the recurring analysis artifact risks around figure outputs, paper-validation exceptions, and generated results.

### Broad Tree Instructions

This would add files under native, tests, package submodules, and analysis categories. It is stricter but likely too noisy for Codex instruction discovery. The root and package docs already cover most of those paths, so broad nesting would duplicate policy rather than sharpen behavior.

## Non-Goals

- Do not create the nested `AGENTS.md` files in this spec step.
- Do not change public package APIs, runtime behavior, tests, native code, or capability claims.
- Do not add package-specific implementation plans until this spec is reviewed.
- Do not add nested files to every package subfolder or every analysis category.

## Milestone Linkage

- M1 - Packages: package ownership, workspace layout, and extension-native boundaries.
- M3 - EOS: provider EOS, state, parameters, native SDK, and derivative policy.
- M4 - Equilibrium: `epcsaft-equilibrium`, Ipopt, selector admission, GFPE, route derivatives, and certification.
- M5 - Regression: `epcsaft-regression`, Ceres optimizer, target datasets, and regression evidence.
- M6 - Validation: literature validation and analysis workflow evidence.

## Proof Oracle Candidates

- `rg --files -g AGENTS.md`
- `uv run python run_pytest.py tests/workflows/repo/test_project_structure.py -q`
- `uv run python scripts/dev/validate_project.py quick`

## Follow-Up Implementation Shape

A later `project-plan` run should create a short implementation plan that:

1. Adds the five nested `AGENTS.md` files exactly under the approved paths.
2. Adds or updates a structure guard so the expected nested instruction files remain discoverable.
3. Runs the focused project-structure test and quick validation.
