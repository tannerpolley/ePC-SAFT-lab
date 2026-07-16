# ePC-SAFT Personal Lab Context

## Authority boundary

This repository is the preserved personal lab for the original ePC-SAFT
monorepo. The permanent ecosystem policy is organization doctrine revision 2;
the approved local source is
`/home/tnnrpolley21/Workspaces/Engineering/ePC-SAFT-project/ePC-SAFT-organization/GOVERNANCE.md`.
The temporary migration sequence is owned by
`/home/tnnrpolley21/Workspaces/Engineering/ePC-SAFT-project/ePC-SAFT-migration/MIGRATION.md`.

The personal lab is the sole transitional runtime authority for every
unpromoted slice. It does not own live issue intake, roadmap state, clean
package releases, PyPI publication, or permanent production authority. After
an accepted promotion receipt, the clean destination owns that slice and the
lab copy remains non-authoritative provenance or research.

Historical issue mirrors, plans, specs, milestone pages, release notes, and
old repository URLs describe the state at their recorded date. They are not
instructions for new work. Git history preserves superseded detail.

## Why the lab exists

The lab keeps three things recoverable:

1. the working monorepo implementation and its Git history;
2. primary-source, equation, algorithm, parameter, and validation evidence;
3. rejected, deferred, experimental, and not-yet-promoted work.

Keeping evidence here does not approve copying it into a clean repository.
Each migration slice must select exact source and evidence files deliberately.

## Current code layout

- `packages/epcsaft` contains the provider EOS, inputs, state/property runtime,
  native implementation, and provider-owned tests.
- `packages/epcsaft-equilibrium` contains the monorepo equilibrium extension.
- `packages/epcsaft-regression` contains the monorepo regression extension.
- `analyses`, `data/reference`, `docs/latex`, and `docs/papers` contain broad
  scientific and validation evidence.

The monorepo package split is historical/transitional architecture. The clean
ecosystem uses separate `epcsaft`, `epcsaft-equilibrium`,
`epcsaft-regression`, and installed-artifact validation repositories. No clean
repository may depend on this lab, the migration repository, or sibling source
paths.

## Scientific and capability boundaries

The provider implements PC-SAFT/ePC-SAFT residual Helmholtz and state/property
paths. Equations and broad source traceability remain indexed in
`docs/latex/equations.tex`; that catalogue is evidence, not a promotable
slice specification.

The public equilibrium scope preserved in this lab is limited to
`bubble_pressure`, `dew_pressure`, and scoped nonassociating hydrocarbon
`single_component_vle`. These are local pressure-boundary/saturation routes;
they do not prove global phase discovery. Neutral LLE, general flash,
multiphase, electrolyte, and reactive families remain closed unless their own
formulation, derivative, stability, source, and validation gates pass.

The lab contains regression implementation and characterization evidence, but
production regression admission remains closed until a strict source-backed
target family, exact consumed derivatives, diagnostics, identifiability, and
held-out validation are accepted.

Scientific work must preserve these invariants:

- parameter values, units, bases, component order, model options, and source
  transformations are explicit;
- nonlinear production derivatives use the approved CppAD path; exact linear
  transformations and implicit solves may assemble CppAD partials;
- iterative solver history is not taped as the governing function;
- solver termination, numerical convergence, and physical validity are
  separate acceptance layers;
- density and phase results require branch/topology and stability diagnostics,
  not only a small scalar residual; and
- no fake defaults, hidden scientific constants, mutable compatibility
  payloads, or alternate derivative backends enter clean slices.

Active association parameters remain outside the strict resolved-input
provider baseline until a typed association-topology owner is admitted.
Specified-pressure density closure is not part of the first clean slice.

## Development and validation

For setup and commands, use:

- `docs/agents/new-agent-start-here.md`;
- `docs/pages/development_workflows.rst`;
- `docs/protocols/build_package_dependency_protocol.rst`; and
- root `CMAKE.md` for direct preset operations.

The provider-only native build/import is the preserved archive smoke proof.
Focused tests and documentation checks should be selected in proportion to the
change. The full repository confidence suite is not currently green: retained
regression code still uses removed mutable inputs, older numerical tests still
import retired construction seams, and several project-structure assertions
represent unresolved Stage 4 cutover debt. Do not hide that debt with shims or
claim full validation green.

Tests that claim model agreement must use traceable literature data and retain
the data/model comparison artifact required by repository policy. A successful
nonlinear solve alone is not scientific acceptance.

## Clean-slice migration rule

Every promoted capability follows the same small path:

1. name one capability, destination, source commit, domain, and exclusions;
2. freeze equations, conventions, units, inputs, outputs, errors, derivatives,
   and independent oracles;
3. trace the minimum source call graph;
4. implement cleanly without bulk history, directory, or old-test copying;
5. build and test in isolation from the lab and sibling checkouts;
6. prove required behavior and the absence of excluded seams/defaults; and
7. accept a promotion receipt before runtime authority moves.

The first provider design direction is a neutral, nonassociating, nonionic
binary at explicit molar density using the minimum hard-chain and dispersion
path. Exact components, source records, state domain, outputs, derivative
orders, tolerances, and independent oracle require a separate bounded design
approval before implementation.

## Completion standard for lab changes

A lab change is complete only when it preserves recoverability, removes or
recasts any displaced active authority, updates affected references and tests,
runs proportionate validation, passes the repository cleanup audit, and leaves
the intended Git state explicit. Lab cleanup never changes clean-package
runtime authority by implication.
