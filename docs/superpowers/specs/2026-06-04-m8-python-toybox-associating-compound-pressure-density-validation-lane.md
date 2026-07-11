# Associating-Compound Pressure Density Validation Lane

Milestone: `M8 - Python Toybox`
Issue: `none`
Status: `draft`
Last synced: `2026-06-04`

## Summary

Create a Python-only toybox validation lane for real associating compounds. The
lane should compare exact implicit association and the retained Picard closure
against source-backed pressure-density, vapor-pressure, and liquid-density reference
data, using readable figures that resemble literature validation plots rather
than abstract closure-ranking bars.

This is exploratory M8 work. If the evidence becomes reusable checker-gated
benchmark material, a later M6 validation plan or issue can promote it.

## Project Context Evidence Used

- `docs/superpowers/milestones/M8-python-toybox/README.md` routes Python-only
  cross-EOS/equilibrium analysis into the toybox milestone.
- `docs/superpowers/specs/2026-06-03-m3-eos-paper-backed-association-closure-validation-matrix-design.md`
  defines paper-backed topology rows and requires traceable source metadata.
- `docs/superpowers/specs/2026-06-03-m3-eos-explicit-association-derivative-property-propagation-evidence.md`
  identifies fixed-state pressure residuals as useful warnings, not VLE
  validation.
- the repository Python analysis and plotting policy
  requires retained plotted data and figure-owned input/output/script layout.
- Root repo instructions require new or updated plots to be rendered in chat
  with compact real-data tables when analysis work completes.

## User Decisions

- Use associating compounds only.
- Do not show nonassociating butane/octane-style plots for association
  validation.
- Use actual data points and model curves, not bar plots.
- Use dotted model fits for exact implicit and Picard curves, with distinct
  colors and clear labels.
- Keep data and model curves honest: do not smooth over missing density roots,
  missing parameter provenance, or source-data gaps.

## Recommended Approach

Add one figure-owned validation lane under:

```text
analyses/package_validation/explicit_association_toybox/figures/pressure_density_validation/
  input/
  output/
  scripts/
    generate_data.py
    render_figure.py
```

The lane should:

- read source-backed associating-compound data points from `input/` or the
  repo's canonical reference data tree;
- solve density roots when plotting pressure as a function of density or when
  comparing saturation-like liquid-density curves;
- retain the exact data used in every plot under `output/`;
- render publication-readable figures with data markers and dotted model
  curves;
- include exact implicit association and Picard association curves on the same
  axes for each compound.

## Required Systems

Start with compounds that have association and source-backed parameter rows:

- methanol;
- water;
- acetic acid;
- representative alkanols;
- representative amines when parameter/source rows are available.

Exclude nonassociating compounds from this lane unless they are clearly labeled
as inert controls in a separate figure.

## Required Figures

Use density and pressure plots that readers can interpret:

- vapor pressure versus temperature;
- saturated liquid density versus temperature;
- pressure versus density at selected temperatures;
- optional residual plots below the main panels when useful.

Do not use bar plots as primary evidence in this lane.

## Required Retained Columns

```text
source_id
compound
topology
parameter_source
temperature
pressure_reference
liquid_density_reference
model_name
model_pressure
model_liquid_density
density_root_status
root_branch
absolute_pressure_error
relative_pressure_error
absolute_density_error
relative_density_error
```

## Non-Goals

- No production provider density solver changes.
- No public package validation claim.
- No benchmark registry admission in this spec.
- No equilibrium route implementation.
- No nonassociating-compound association-validation plots.

## Open Questions

- Which public source datasets are acceptable for the first retained pressure
  and liquid-density rows?
- Should the first lane use only pure compounds, or include one-associating
  component binaries after pure-compound root solving is proven?
- Which pressure-density root selection rule is strict enough for toybox use
  without becoming production solver policy?

## Proof Oracle Candidates For Later Planning

- `uv run python analyses/package_validation/explicit_association_toybox/figures/pressure_density_validation/scripts/generate_data.py`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/pressure_density_validation/scripts/render_figure.py`
- `uv run python run_pytest.py analyses/package_validation/explicit_association_toybox/tests -q`
