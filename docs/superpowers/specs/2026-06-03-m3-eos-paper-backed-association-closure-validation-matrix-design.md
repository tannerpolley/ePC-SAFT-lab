# Paper-Backed Association Closure Validation Matrix

## Purpose

Design a Python-only analysis workflow that can answer a broader question than
the first explicit association toybox:

```text
Across real association topologies, mixture families, and fixed EOS states,
which explicit association closures are accurate enough to remain candidates,
and what speedup do they offer against the exact implicit association solve?
```

The current toybox proves that the mechanics can exist. This spec resets the
next design target around a validation matrix: rows are paper-backed systems
and association topologies, columns are exact and approximate association
models, and cells report site-fraction error, association residual Helmholtz
error, total neutral residual Helmholtz error, timing, and evidence-band
classification.

This is still analysis-only. It does not admit an explicit closure into the
provider, does not change public package behavior, and does not make an
equilibrium-route claim.

## Project Context Evidence Used

- `docs/superpowers/PROJECT_CONTEXT.md` names the explicit association closure
  spec as the policy reference before adding approximate `X_A` closures or
  claiming exact derivatives of an approximate association model.
- `docs/superpowers/specs/2026-05-23-m3-eos-explicit-association-closure-for-pcsaft.md`
  separates `implicit_exact` from `explicit_approx` and warns that CppAD
  derivatives of explicit closures are exact derivatives of the approximate
  model, not automatically exact PC-SAFT association derivatives.
- `docs/superpowers/specs/2026-06-03-m3-eos-explicit-association-toybox-design.md`
  deliberately starts with fixed `T`, fixed density, and synthetic/simple
  state grids. That is useful as a first slice but insufficient for real
  topology coverage.
- `docs/pages/project_structure.rst` puts source-owned package validation under
  `analyses/package_validation/<short_id>/` and archival paper markdown under
  `docs/papers/md/`.
- `docs/papers/md/ePC-SAFT-Literature/Huang and Radosz - 1990 - Equation of State for Small, Large, Polydisperse, and Associating Molecules.md`
  provides the SAFT association topology source now needed for this design:
  Table VII gives explicit monomer-fraction formulas for 1, 2A, 2B, 3A, 3B,
  4A, 4B, and 4C bonding types; Table VIII maps real fluid classes to rigorous
  and assigned bonding types; Table IX lists self-associating parameter rows
  and reported vapor-pressure/liquid-density AAD metadata.
- Gross/Sadowski 2002 remains the PC-SAFT associating-system staging source for
  one-associating-component mixtures and binary systems with dispersion `k_ij`
  corrections.
- MEA literature already in `docs/papers/md/MEA/` records later multi-scheme
  2B/3B/4C comparisons for MEA/water. That should inform future validation,
  but this spec stays provider-analysis-only and does not become an MEA
  application workflow.

## User Decisions

- Create a new drawing-board spec rather than only patching the current toybox
  design.
- Add Huang/Radosz as literature markdown only for now, not as a full
  `analyses/paper_validation/1990_huang_radosz` scaffold.
- Optimize the next direction for a validation matrix with real topologies,
  timing comparisons, and optional property-data metadata, rather than a
  production provider path.
- Update related explicit-association Superpowers docs and issue mirrors so
  later agents do not treat the synthetic toybox as the whole validation story.

## Huang/Radosz And Derivation Crosswalk

Huang/Radosz Table VII should not be treated as a disconnected closure catalog.
It is a set of source-backed closed-form topology reductions that must be
organized against the repo derivation families:

| Huang/Radosz item | Role in this repo | Derivation relationship |
| --- | --- | --- |
| `1` | One-site scalar exact reduction under the Table VII assumptions. | New topology reduction used to validate the exact baseline; not Closure A. |
| `2A` | Two equivalent sites with all pair interactions active and equal. | New scalar/equivalent-site reduction; compare against the generic mass-action baseline, then against Closure B/C as approximations. |
| `2B` | Donor-acceptor two-site reduction with only unlike association active. | Matches Closure A when one associating component, donor/acceptor grouping, and multiplicities match. |
| `3A` | Three equivalent sites with all pair interactions active and equal. | New equivalent-site reduction; not Closure A because it is not donor/acceptor 2B. |
| `3B` | Two equivalent donor/acceptor-like sites coupled to a third site under the source assumptions. | New constrained topology reduction; compare to Closure B/C full-matrix approximations and Closure D only as diagnostic. |
| `4A` | Four equivalent sites with all pair interactions active and equal. | New equivalent-site reduction; validates topology handling, not a production closure by itself. |
| `4B` | Three equivalent sites coupled to a fourth site under the source assumptions. | New constrained topology reduction; compare to full-matrix approximations. |
| `4C` | Two-by-two donor/acceptor-like topology with specific unlike interactions. | New constrained topology reduction; relevant to water/MEA scheme studies, but only exact under its stated assumptions. |

The required comparison order is:

1. Construct a generic exact mass-action case whose `K_ab` matrix matches the
   Huang/Radosz Table VII assumptions.
2. Verify the Huang/Radosz closed form against that exact baseline.
3. Map the verified formula to a `topology_reduction` label.
4. Run the repo derivation closures against the same case:
   - Closure A only where the topology is one-associating-component 2B.
   - Closure B and Closure C as general full-matrix explicit approximations.
   - Closure D only as a collapsed donor/acceptor diagnostic.
5. Only after the source topology check passes, add real component rows that
   use Huang/Radosz assigned or rigorous bonding types.

Each output row should carry enough metadata to make this explicit:

```text
source_formula_family
source_formula_id
derivation_family
comparison_role
topology_gate
exactness_claim
```

Recommended values:

```text
source_formula_family = huang_radosz_table_vii | repo_derivation
derivation_family = closure_a_2b | closure_b_picard | closure_c_picard_diagonal_newton | closure_d_collapsed_mean_field | topology_reduction
comparison_role = exact_baseline | exact_topology_reduction | explicit_approximation | diagnostic_collapse
topology_gate = matched | mismatched_unavailable | diagnostic_only
exactness_claim = exact_mass_action | exact_for_table_vii_topology | exact_for_approximate_model | none
```

Do not compare a Huang/Radosz formula directly to a derivation closure without
also comparing both to `implicit_exact`. The exact baseline is the common
arbiter.

## Recommended Approach

Grow the existing analysis root rather than creating a second package-like
playground:

```text
analyses/package_validation/explicit_association_toybox/
  config/
    closure_sweep.yaml
    systems.yaml
    paper_topologies.yaml
    paper_systems.yaml
  scripts/
    association_models.py
    exact_baseline.py
    closure_models.py
    topology_registry.py
    topology_reductions.py
    paper_systems.py
    metrics.py
    run_grid.py
    summarize_results.py
  figures/
    closure_accuracy/
    residual_ares_error/
    topology_validation_matrix/
    timing_pareto/
```

The existing toybox remains the low-friction calculation sandbox. The new
matrix layer makes it paper-backed and reviewer-readable without turning it
into a public package.

## Validation Matrix Shape

Rows should be explicit validation cases, not ad hoc examples:

```text
source_family
source_paper
system_id
component_names
association_topology
rigorous_topology
assigned_topology
parameter_source
temperature
density
composition
association_strength_scale
property_data_status
```

Initial rows should include:

- synthetic controls retained from the first toybox;
- Huang/Radosz pure self-associating topologies: 1, 2A, 2B, 3A, 3B, 4A, 4B,
  and 4C where the source formula assumptions are clear;
- Huang/Radosz real assigned-type families: acids as 1, alkanols as 2B, water
  as 3B assigned from a 4C rigorous type, primary amines as 3B, secondary amines
  as 2B;
- Gross/Sadowski one-associating-component binary cases such as
  methanol/isobutane, methanol/cyclohexane, ethanol/n-butane,
  1-butanol/n-butane, and 1-pentanol/benzene;
- optional later MEA/water scheme-comparison rows only after the analysis is
  ready to handle multiple published parameter sets without becoming a
  downstream application study.

Columns should be association model choices:

```text
implicit_exact
topology_reduction_huang_radosz_1
topology_reduction_huang_radosz_2a
topology_reduction_huang_radosz_2b
topology_reduction_huang_radosz_3a
topology_reduction_huang_radosz_3b
topology_reduction_huang_radosz_4a
topology_reduction_huang_radosz_4b
topology_reduction_huang_radosz_4c
closure_a_2b_exact_reduction
explicit_picard_unroll_1
explicit_picard_unroll_3
explicit_damped_picard_unroll_3
explicit_damped_picard_unroll_5
explicit_picard3_diag_newton1
collapsed_donor_acceptor_mean_field
```

The Huang/Radosz formulas should be treated as exact reductions only for the
stated topology and simplifying assumptions. Outside those assumptions they
must either be unavailable or clearly marked diagnostic-only.

## Metrics

Each matrix cell should report:

- site-fraction minimum, maximum, and boundedness status;
- maximum absolute and relative site-fraction error versus `implicit_exact`;
- mass-action residual infinity norm;
- `ares_assoc_exact`;
- `ares_assoc_model`;
- `ares_assoc_abs_error`;
- `ares_assoc_rel_error`;
- `ares_hc` and `ares_disp` when the neutral scalar context is available;
- `ares_total_exact`;
- `ares_total_model`;
- `ares_total_abs_error`;
- `ares_total_rel_error`;
- exact implicit solve elapsed time;
- model elapsed time;
- speedup ratio;
- evidence band.

Timing must remain analysis evidence only. Python timing from this toybox is not
provider performance proof.

## Property Data Lane

Real vapor-pressure and liquid-density comparison is valuable, but it should be
handled as a staged lane rather than silently implied by the fixed-state matrix.

Stage the property-data lane this way:

1. Record paper metadata first: reported AAD percent, temperature ranges, and
   data-source notes from Huang/Radosz Table IX and Gross/Sadowski tables.
2. Add raw source data only when the actual vapor-pressure and liquid-density
   points are available from a permissible source or an existing repo dataset.
3. Keep pure-component saturation or liquid-density calculations as optional
   analysis commands with explicit solver status and no production-equilibrium
   claim.
4. Move full VLE, LLE, bubble, dew, flash, or HELD-style route validation to
   M4/M6 planning. This M3 analysis can provide closure evidence, but it should
   not smuggle equilibrium route ownership into the provider package.

The implementation plan should include an explicit data-request step before any
real-property validation claim. The agent should first search the repo for
existing source tables and raw datasets. If the raw vapor-pressure or
liquid-density data are not already present, the agent should either:

- fetch permissible public/open data with source citations and a retained
  source manifest; or
- ask the user for local source files, PDFs, CSV exports, or permission to use
  a specific proprietary source when the cited data source is not publicly
  accessible.

Do not fabricate raw property data from paper AAD values, plotted curves, or
parameter tables. Reported AAD values are metadata until the actual data points
and calculation path are present.

The first plan should create or prepare a data-request manifest with columns
like:

```text
system_id
component
property
temperature_range
pressure_range
source_named_in_paper
repo_source_available
public_source_candidate
user_input_needed
status
```

The first matrix can therefore include `property_data_status` values such as:

```text
metadata_only
needs_user_source
public_source_candidate
raw_data_available
property_solve_available
equilibrium_route_required
```

## Evidence Bands

Use the existing evidence-band style, but make it topology-aware:

```text
exact_reduction_verified:
    The formula is algebraically appropriate for the declared topology and
    matches the exact mass-action baseline within tight tolerance.

promising_eos_approximation:
    The closure has small `ares_assoc` and total neutral `ares` error over a
    named paper-backed state envelope and has useful speedup.

topology_limited:
    The closure works for one topology or simplifying assumption but should not
    be generalized.

diagnostic_only:
    The closure helps screening, seeds, or stress-region discovery, but misses
    thermodynamic-output thresholds.

reject_for_provider_path:
    The closure produces invalid site fractions, high mass-action residuals,
    unstable timing, or unacceptable thermodynamic-output error.
```

## Figures And Tables

Recommended retained outputs:

- a topology validation heatmap with rows as system/topology cases and columns
  as closure models;
- an `ares_assoc` error heatmap;
- a total neutral `ares` error heatmap when HC/dispersion context is present;
- a timing Pareto plot with model error against speedup;
- a table of property-data metadata, separating reported paper AAD values from
  any raw-data parity calculations;
- a failure-region table that names states, topologies, and closure models that
  leave the valid envelope.

## Non-Goals

- No provider C++ implementation change.
- No public `epcsaft` API change.
- No admission of an approximate association closure into production.
- No equilibrium route implementation or validation claim.
- No regression or parameter-fitting workflow.
- No hidden SciPy dependency or broad dependency-policy exception.
- No direct copying of paper-reported AAD values into validation claims without
  recording whether raw data and calculations exist.
- No MEA-specific application workflow inside this provider analysis.

## Tradeoffs

- Reusing the current toybox root keeps the workflow easy to run and avoids a
  second shadow implementation, but the next plan must prevent that root from
  becoming a broad unofficial PC-SAFT package.
- Paper-backed topology rows make the analysis scientifically meaningful, but
  they require clearer source manifests and topology-gating rules than the
  synthetic first slice.
- Adding property metadata is cheap and useful. Recomputing vapor pressure and
  liquid density is more expensive and should only happen when source data and
  solver boundaries are explicit.
- Huang/Radosz exact reductions are powerful for topology validation, but they
  are not universal mixture closures. The output schema must make that boundary
  visible.

## Later Project-Plan Proof Candidates

These commands are candidates for a later `$project-plan`; they are not proof
that exists today:

```powershell
uv run python analyses/package_validation/explicit_association_toybox/figures/topology_validation_matrix/scripts/generate_data.py
uv run python analyses/package_validation/explicit_association_toybox/figures/topology_validation_matrix/scripts/render_figure.py
uv run python analyses/package_validation/explicit_association_toybox/figures/timing_pareto/scripts/generate_data.py
uv run python analyses/package_validation/explicit_association_toybox/figures/timing_pareto/scripts/render_figure.py
uv run python run_pytest.py analyses/package_validation/explicit_association_toybox/tests -q
uv run python run_pytest.py tests/workflows/repo/test_project_structure.py -q
uv run python scripts/dev/validate_project.py quick
```

## Open Questions For Planning

- Should the next implementation plan expand the existing toybox directly, or
  first create only source manifests and config schemas?
- Which Huang/Radosz table rows should be transcribed into a machine-readable
  first source manifest?
- What fixed density and temperature envelopes should represent each paper
  system before any property solver exists?
- Which raw vapor-pressure and liquid-density data can be found from existing
  repo datasets or permissible public sources, and which ones require the user
  to provide local paper/source files?
- Which topology errors are strict failures versus useful diagnostic evidence?
