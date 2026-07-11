# Pure-Component Saturation Pressure Solver For The Python Toybox

Milestone: `M8 - Python Toybox`
Issue: `none`
Status: `draft`
Last synced: `2026-06-04`

## Summary

Add a Python-only pure-component saturation-pressure solver to the explicit
association toybox. The goal is to replace fixed-state pressure residual plots
with honest vapor-pressure predictions for associating compounds: at a fixed
temperature, solve the vapor and liquid density roots plus common saturation
pressure using equality of pressure and chemical potential or fugacity.

This is exploratory analysis. It should use SciPy and stay inside the toybox;
it must not claim production provider, equilibrium, or benchmark capability.

## Project Context Evidence Used

- `docs/superpowers/milestones/M8-python-toybox/README.md` assigns
  Python-only EOS/equilibrium-style analysis to M8 before provider,
  equilibrium, or benchmark admission.
- `docs/superpowers/specs/2026-06-04-m8-python-toybox-associating-compound-pressure-density-validation-lane.md`
  created source-backed pressure-density plots but still treated pressure residuals as
  fixed-state diagnostics, not saturation predictions.
- `analyses/package_validation/explicit_association_toybox/references/legacy_pcsaft_electrolyte.py`
  contains legacy `pcsaft_vaporP`/`vaporPfit` style workflows that can inform a
  quick toybox solver without becoming package API.
- The current `epcsaft` provider exposes state pressure/density evaluation, not
  a public pure-component vapor-pressure route.

## User Decisions

- Production single-component VLE belongs in `epcsaft-equilibrium`, not the
  provider package.
- The toybox should still get a lightweight SciPy `pcsaft_vaporP`-style
  capability so explicit association can be tested against true saturation
  pressure data.
- Keep the first toybox scope to pure compounds, especially associating
  compounds such as water and methanol.
- Keep exact implicit association and Picard on the same solver path so
  differences come from the association closure, not from route logic.

## Recommended Approach

Create a toybox module such as:

```text
analyses/package_validation/explicit_association_toybox/scripts/pure_saturation.py
```

with a small public analysis function:

```text
solve_pure_saturation(case, temperature, closure_name, initial_guess=None)
```

The solver should solve local variables such as:

```text
log_rho_v
log_rho_l
log_p_sat
```

or an equivalent reduced variable set. The residual equations should represent:

```text
P(T, rho_v) - P_sat = 0
P(T, rho_l) - P_sat = 0
mu(T, rho_v) - mu(T, rho_l) = 0
```

An equivalent fugacity equality residual is acceptable if it is clearer in the
toybox implementation.

## Figure And Data Lane

Add a figure-owned lane:

```text
analyses/package_validation/explicit_association_toybox/figures/pure_saturation_validation/
  output/
  scripts/
    generate_data.py
    render_figure.py
```

The rendered figure should compare:

- NIST/reference vapor-pressure data points;
- exact implicit association saturation curves;
- Picard saturation curves;
- saturated liquid density data points and model curves when the solver returns
  a liquid density root.

Use data markers for reference rows and dotted lines for model curves. Do not
use bar plots as primary evidence.

## Required Retained Columns

```text
component
T_K
reference_p_sat_Pa
reference_rho_liq_mol_m3
closure_name
model_p_sat_Pa
model_rho_vap_mol_m3
model_rho_liq_mol_m3
pressure_relative_error
liquid_density_relative_error
residual_pressure_vap_Pa
residual_pressure_liq_Pa
residual_mu
solver_status
solver_iteration_count
initial_guess_policy
parameter_source
source_url
```

## Non-Goals

- No provider package saturation API.
- No `epcsaft-equilibrium` route implementation.
- No binary bubble-pressure prototype in this first toybox spec.
- No benchmark registry promotion.
- No fitted parameter claims from this analysis lane.

## Open Questions

- Should the first solver use pressure as an explicit optimization variable or
  eliminate it through `P(T, rho_v) = P(T, rho_l)`?
- Which chemical-potential expression should be the first toybox baseline:
  reduced residual chemical potential plus ideal terms, or fugacity
  coefficient equality?
- What strict failure labels should be used for missing vapor roots, missing
  liquid roots, and near-critical cases?

## Proof Oracle Candidates For Later Planning

- `uv run python run_pytest.py analyses/package_validation/explicit_association_toybox/tests/test_pure_saturation.py -q`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/pure_saturation_validation/scripts/generate_data.py`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/pure_saturation_validation/scripts/render_figure.py`
- `rg -n "bubble|dew|flash|GFPE|HELD" analyses/package_validation/explicit_association_toybox/scripts/pure_saturation.py analyses/package_validation/explicit_association_toybox/figures/pure_saturation_validation`
