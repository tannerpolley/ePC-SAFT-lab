# M4 Neutral Nonassociating LLE Source-Backed Showcase

Milestone: `M4 - Equilibrium`
Affected package: `packages/epcsaft-equilibrium`
Validation scope: `M6 - Validation` fixture and plot evidence only where
needed
Status: `implemented-by-issue-250`
Created: `2026-06-11`
Updated: `2026-06-13`

## Summary

Current `main` has a production-exposed neutral nonassociating `lle` utility
route and focused synthetic binary proof. Issue #250 adds the first
source-backed neutral nonassociating LLE benchmark fixture and retained LLE
showcase figure.

This spec defines that source-backed showcase: a neutral, nonelectrolyte,
nonreactive, nonassociating binary LLE fixture; the existing `route="lle"` path
through fresh native HELD 1.0 diagnostics; and retained LLE figures that clearly
do not borrow associating, electrolyte, or reactive claims.

## Implementation Result

Issue #250 implements this showcase with the Matsuda/NIST perfluorohexane +
hexane source case:

- Fixture:
  `data/reference/equilibrium_benchmarks/neutral_lle/matsuda_2011_pfhexane_hexane`
- Checker: `scripts/validation/check_neutral_lle_showcase.py`
- Public API regression:
  `packages/epcsaft-equilibrium/tests/api/test_neutral_lle_showcase_fixture.py`
- Retained analysis:
  `analyses/package_validation/neutral_nonassociating_lle_showcase`

The retained source rows are paired NIST ThermoML binodal/cloud-point branch
rows at 293.89 K and 293.90 K, inside the reported 0.2 K temperature
uncertainty. The pure parameters are Tihic PC-SAFT-compatible sPC-SAFT rows and
family correlations. The binary interaction is explicitly source-fitted for
the current route (`kij = 0.0662`); it is not imported as the Tihic literature
`kij = 0.073` value because that value over-splits this route. This distinction
is retained in `source_notes.md`, `binary_interactions.csv`, and the checker
payload.

## Project Context Evidence Used

- Verified: `docs/superpowers/PROJECT_CONTEXT.md` lists neutral
  nonassociating `lle` as a current public utility route while keeping
  associating, electrolyte, and reactive LLE separate.
- Verified:
  `docs/superpowers/milestones/M4-equilibrium/generalized-fluid-phase-equilibrium.md`
  treats `PE-Neutral TP Flash` as the neutral TP flash plus neutral VLE/LLE
  validation ladder.
- Verified:
  `docs/superpowers/milestones/M4-equilibrium/registries/equilibrium-benchmark-registry.yaml`
  has a source-backed neutral TP-flash fixture and electrolyte LLE fixtures,
  but no `neutral_lle` fixture directory or neutral nonassociating LLE benchmark
  case.
- Verified: #144 implemented the activation-driven neutral nonassociating LLE
  route using a synthetic nonassociating A/B binary split.
- Verified: #241 and a fresh native rebuild now provide HELD Stage II replay
  and Stage III replay-consumption evidence for the neutral proof lane.
- Verified:
  `packages/epcsaft-equilibrium/tests/native/results/test_neutral_lle_reference_values.py`
  proves the synthetic LLE route with exact Hessian support, HELD stage
  diagnostics, material balance, pressure consistency, fugacity consistency,
  candidate completeness, and phase distance.
- Verified:
  `packages/epcsaft-equilibrium/tests/equilibrium_support/equilibrium_cases.py`
  defines the current synthetic LLE example as species `A` and `B` with
  `m = [1.0, 2.0]`, `sigma = [3.5, 4.0]`, `epsilon = [150.0, 250.0]`, and
  `k_ij = 0.5`.

## Source Candidate

The first source-backed neutral nonassociating LLE candidate should be a
perfluoroalkane + n-alkane binary system.

Recommended first data source:

- NIST ThermoML page for Matsuda et al., Fluid Phase Equilibria 297(2),
  187-191, DOI `10.1016/j.fluid.2010.05.018`.
- The ThermoML page reports experimental LLE data for perfluorohexane +
  n-hexane, perfluorohexane + n-octane, and perfluorooctane + n-octane.
- These systems are neutral, nonelectrolyte, nonreactive, and nonassociating
  under the current route boundary.
- The page exposes machine-readable JSON/ThermoML links, which makes it a
  better first fixture source than a figure-only paper.

Recommended model/parameter source to audit:

- Aparicio, The Journal of Supercritical Fluids 46(1), 10-20, DOI
  `10.1016/j.supflu.2008.02.017`, which studies perfluoroalkane + alkane phase
  behavior with PC-SAFT.

Reason to avoid other nearby examples:

- Methanol/cyclohexane and water/alcohol LLE are associating systems and belong
  to #145/#190, not this source-backed nonassociating showcase.
- Khudaida, Ascani, and Held electrolyte LLE data belong to #191 and HELD2.0,
  not this neutral nonassociating route.
- The synthetic A/B case should remain a route mechanics fixture, not the
  source-backed public evidence figure.

## Required Artifact Shape

Add a new source fixture under:

```text
data/reference/equilibrium_benchmarks/neutral_lle/<source_slug>/
```

Minimum retained files:

- `source_notes.md`
- `metadata.json`
- `pure_component_parameters.csv`
- `binary_interactions.csv`
- `experimental_tielines.csv`
- `feed_compositions.csv`

The fixture must record:

- source citation and URL or DOI;
- species and exact species order;
- source model family or parameter source;
- pure PC-SAFT/ePC-SAFT parameters used by the package;
- binary interaction parameters and provenance;
- temperature, pressure, feed composition, and phase compositions;
- phase labels `liquid1` and `liquid2`;
- tolerances for composition, material balance, pressure, fugacity, and phase
  distance;
- explicit statement that association, electrolyte, and reaction terms are not
  active.

## Showcase Figure Requirements

Add an analysis folder under:

```text
analyses/package_validation/neutral_nonassociating_lle_showcase/
```

Use the two-step plotting workflow:

1. `scripts/generate_data.py` loads the fixture, runs the current `lle` route,
   and writes retained CSV/JSON outputs.
2. `scripts/render_figures.py` reads those retained outputs and writes PNG/SVG
   plus `.mpl.yaml` sidecars.

Minimum figures:

- binary LLE tie-line or binodal-style composition figure showing source
  liquid phases, solved liquid phases, and feed;
- diagnostic margin figure showing observed/tolerance ratios for composition,
  material balance, pressure, fugacity, phase distance, and HELD stage
  admission;
- optional HELD stage-status figure if it adds clarity without duplicating the
  TP-flash evidence plot.

The figure text must state neutral nonassociating LLE only. It must not mention
associating, electrolyte, salting-out, reactive, CE, CPE, or generalized
production admission as solved by this showcase.

## Implementation Boundaries

Allowed:

- neutral LLE fixture ingestion;
- source-backed fixture checker for one or more neutral nonassociating LLE
  tie-lines;
- current `Equilibrium(mixture, route="lle", T=..., P=..., z=...).solve()`
  route;
- exact-Hessian, HELD Stage II replay, Stage III replay-consumption, and
  postsolve certification receipts;
- registry update adding the neutral LLE benchmark case under the neutral
  PE/VLE/LLE ladder.

Forbidden:

- associating LLE admission;
- electrolyte LLE admission;
- reactive LLE admission;
- salting-out, SLE, precipitation, or Ksp claims;
- using methanol/cyclohexane or water/alcohol as this nonassociating proof;
- claiming a generalized family production row solely because the current
  public `lle` utility route solves one fixture.

## Acceptance Criteria

- A source-backed neutral nonassociating LLE fixture exists under
  `data/reference/equilibrium_benchmarks/neutral_lle/`.
- The fixture uses neutral, nonelectrolyte, nonreactive, nonassociating species.
- The fixture records source data, package parameters, binary interactions,
  feed construction, phase compositions, pressure, temperature, and tolerances.
- A checker fails when association, electrolyte, reactive terms, missing
  binary interactions, missing source rows, or missing HELD stage evidence are
  present.
- The current `lle` route accepts the fixture with exact Hessian support.
- Postsolve certification passes material balance, pressure consistency,
  chemical-potential or fugacity consistency, phase distance, candidate
  completeness, and stability.
- HELD Stage II reports replayable dual-loop evidence.
- HELD Stage III consumes the Stage II replay seed and reports Ipopt success
  plus `solve_succeeded`.
- Retained plotted CSV/JSON data exactly match the rendered figures.
- The M4 registry distinguishes this source-backed LLE showcase from the
  existing source-backed TP-flash fixture and from electrolyte LLE.

## Recommended Implementation Issue

Create this M4 issue after this spec is accepted:

```text
Title: M4: add source-backed neutral nonassociating LLE showcase fixture
Milestone: M4 - Equilibrium
Type: Feature
Package: equilibrium
Backend: Ipopt
Readiness: ready
```

Issue body:

```text
Add the first source-backed neutral nonassociating LLE fixture and showcase
figure for the current production `route="lle"` utility. Use a perfluoroalkane
+ n-alkane binary source if the source audit confirms usable package
parameters and tie-line data.

Acceptance:
- `data/reference/equilibrium_benchmarks/neutral_lle/<source_slug>/` contains
  source notes, metadata, parameters, binary interactions, feed rows, and
  experimental tie-lines.
- A neutral LLE fixture checker verifies source fields, route acceptance,
  HELD Stage II replay, Stage III replay consumption, exact Hessian support,
  material balance, pressure consistency, fugacity consistency, phase distance,
  and candidate completeness.
- `analyses/package_validation/neutral_nonassociating_lle_showcase/` renders
  retained-data PNG/SVG figures for the LLE tie-line/binodal and diagnostic
  margins.
- Registry and docs state this is neutral nonassociating LLE only.
- Associating, electrolyte, reactive, salting-out, CE, and CPE routes remain
  outside this issue.

Proof:
- uv run --no-sync python scripts/dev/build_epcsaft.py --profile equilibrium
  --build-only --parallel 4
- uv run --no-sync python run_pytest.py
  packages/epcsaft-equilibrium/tests/native/results/test_neutral_lle_reference_values.py
  -q
- uv run --no-sync python <new neutral_lle_fixture_checker> --json
  --require-complete
- uv run --no-sync python
  analyses/package_validation/neutral_nonassociating_lle_showcase/scripts/generate_data.py
- uv run --no-sync python
  analyses/package_validation/neutral_nonassociating_lle_showcase/scripts/render_figures.py
- uv run --no-sync python scripts/dev/validate_project.py docs
```

## Open Questions For Planning

- Should the first source-backed neutral LLE fixture use Matsuda 2010
  ThermoML data directly, or should it first audit Aparicio 2008 PC-SAFT
  parameter rows for model parity?
- Should the first showcased binary be perfluorohexane + n-hexane because it is
  simplest, or perfluorohexane + n-octane because it may produce stronger phase
  separation?
- Should the registry add a dedicated `neutral_lle_fixture_gate`, or keep the
  case under the existing `PE-Neutral TP Flash` neutral VLE/LLE ladder until
  #189 generalizes the phase-set row?

## Non-Goals

- No source implementation is included in this spec.
- No new public route is added.
- No associating, electrolyte, reactive, CE, or CPE admission is created.
- No downstream application metric is computed.
- No broad generalized production claim is created from a single LLE showcase.

## Self-Review

- Placeholder scan: no unresolved placeholders remain.
- Scope check: this is one source-backed neutral nonassociating LLE showcase,
  not a generalized LLE validation campaign.
- Ambiguity check: the first candidate source and rejected nearby examples are
  explicit.
- Capability check: the current public `lle` utility remains narrower than a
  generalized family admission claim.
