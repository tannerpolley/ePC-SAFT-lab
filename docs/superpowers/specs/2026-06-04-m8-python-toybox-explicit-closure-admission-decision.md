# Explicit Closure Admission Decision

Milestone: `M8 - Python Toybox`
Issue: `none`
Status: `draft`
Last synced: `2026-06-05`

## Summary

Create a toybox evidence decision spec that decides whether the retained Picard
closure remains the only explicit association candidate worth testing and what
must be true before any provider EOS admission work is allowed.

The likely current answer is conservative: Picard remains the only candidate
worth continuing, and no provider implementation should be attempted until
property, derivative, simulation, and timing gates pass.

This spec is the final M8 evidence request needed before issue #161 can be
resolved or rewritten. The remaining gap is not another closure family. The
remaining gap is a single decision packet that evaluates the same fixed Picard
policy grid with relative-error evidence and end-to-end simulation timing, then
states whether #161 should close, stay blocked, or become a narrow M3 provider
admission issue.

## Project Context Evidence Used

- `docs/superpowers/milestones/M8-python-toybox/README.md` defines toybox
  evidence as pre-admission work.
- `docs/superpowers/milestones/M3-eos/README.md` still lists #161 as the
  provider-facing explicit association closure design issue.
- `docs/superpowers/specs/2026-05-23-m3-eos-explicit-association-closure-for-pcsaft.md`
  says explicit closure derivatives are exact only for the approximate model.
- `docs/superpowers/specs/2026-06-03-m3-eos-explicit-association-derivative-property-propagation-evidence.md`
  preserves the finding that Picard is the retained active approximation
  candidate.
- `docs/latex/explicit_assocation.tex` now derives only the full-matrix
  fixed-depth Picard closure and removes unrelated closure clutter.
- `docs/superpowers/specs/2026-06-04-m8-python-toybox-cppad-shaped-picard-property-derivative-evidence.md`
  defines the broad pure/mixture property and C++/CppAD-shaped derivative
  evidence lane that must be read before any provider admission claim.
- `docs/superpowers/specs/2026-06-04-m8-python-toybox-picard-step-damping-policy-grid.md`
  defines the retained policy grid: fixed step counts `3`, `5`, `7`, `9`, and
  `11` with damping values `0.35`, `0.5`, `0.65`, `0.8`, and `1.0`.
- `analyses/package_validation/explicit_association_toybox/figures/picard_policy_grid/output/picard_policy_grid.csv`
  currently retains 275 policy-grid rows over 11 cases and 25 policies per
  case, including association, total-EOS proxy, derivative, Hessian, timing,
  and Pareto-band columns.
- `analyses/package_validation/explicit_association_toybox/figures/pure_saturation_validation/output/pure_saturation_validation.csv`
  currently retains 288 saturation-simulation rows with pressure, density,
  solver, residual, JAX, Hessian, and Python Ipopt status columns.

## User Decisions

- Remove or ignore old diagonal-polish, collapsed-mean-field, and other
  non-retained closure lanes.
- Treat Picard as the only explicit association approximation candidate worth
  continuing for now.
- Treat Picard step count and damping as fixed policy settings, not as separate
  closure families and not as adaptive convergence controls.
- Do not promote Picard into provider EOS until property and derivative gates
  pass.
- Use M8 for toybox decision evidence; use M3 only when the decision becomes a
  provider implementation or provider-admission issue.
- The final issue #161 decision must compare both relative error and
  end-to-end simulation time against the exact implicit mass-action baseline.

## Admission Decision Shape

The decision artifact should classify each closure family as:

```text
continue
historical_only
delete_from_toybox
provider_blocked
provider_candidate
```

Current expected classification:

| Closure family | Expected status | Reason |
| --- | --- | --- |
| Fixed-policy Picard | `continue` | Only retained approximation candidate with useful speed/accuracy tradeoff so far; final policy choice must come from the retained grid. |
| Exact implicit mass-action | `continue` | Reference baseline, not an approximation. |
| Huang/Radosz topology reductions | `continue` as validation baselines only | Exact only under source topology assumptions. |
| Diagonal polish variants | `historical_only` or `delete_from_toybox` | Did not clearly beat Picard accuracy/cost tradeoff. |
| Collapsed mean field | `delete_from_toybox` | Diagnostic-only and not provider plausible. |
| Other ad hoc closures | `delete_from_toybox` | Clutter unless a source-backed reason exists. |

## Final Evidence Package For #161

The last M8 pass should produce one decision packet, not another open-ended
exploration. It should use the existing Picard policy grid and add the missing
simulation-level comparison so #161 has enough evidence to be resolved.

Required retained evidence:

- exact implicit mass-action baseline rows for every retained case;
- Picard policy rows for the same grid: step counts `3`, `5`, `7`, `9`, `11`
  and damping values `0.35`, `0.5`, `0.65`, `0.8`, `1.0`;
- relative errors for site fractions, mass-action residuals, association
  Helmholtz energy, total residual Helmholtz proxy, pressure proxy, selected
  first derivatives, and selected Hessian/Jacobian diagnostics;
- simulation outputs for associating pure compounds and representative
  mixtures where the toybox supports them, including saturation pressure,
  vapor density, liquid density, pressure-density roots, solver residuals, and
  root-selection status;
- simulation timing for exact implicit and each retained Picard policy,
  measured end-to-end through the same simulation path rather than closure
  evaluation only;
- closure-evaluation timing retained separately so the report can distinguish
  algebraic speedup from full simulation speedup;
- policy labels such as `fast`, `balanced`, `high_accuracy`, and
  `provider_blocked` assigned from evidence, not from preference;
- a final #161 disposition recommendation.

Minimum final-report columns:

```text
case_id
topology_id
simulation_id
simulation_type
component_family
mixture_family
step_count
damping
policy_name
exact_iteration_count
solver_status_exact
solver_status_picard
density_root_status_exact
density_root_status_picard
association_helmholtz_relative_error
total_ares_proxy_relative_error
pressure_proxy_relative_error
saturation_pressure_relative_error
liquid_density_relative_error
vapor_density_relative_error
derivative_max_relative_error
hessian_max_relative_error
closure_elapsed_median_seconds_exact
closure_elapsed_median_seconds_picard
simulation_elapsed_median_seconds_exact
simulation_elapsed_median_seconds_picard
closure_speedup_vs_exact
simulation_speedup_vs_exact
pareto_band
admission_band
issue_161_recommendation
```

The final plots should be readable pressure-density and saturation-style
comparisons where possible: data points for retained reference data, dotted
exact-implicit model curves, and dotted Picard model curves. No bar plots are
needed for the final decision evidence.

## Decision Gates

The final report should classify every tested Picard policy into one of these
bands:

| Band | Meaning |
| --- | --- |
| `provider_candidate` | Relative-error, simulation, derivative, Hessian, and timing evidence all pass the stated gates over the retained case matrix. |
| `m8_continue_only` | Picard remains scientifically interesting, but one or more provider gates are still missing or inconclusive. |
| `provider_blocked` | Evidence shows unacceptable property, derivative, root-selection, or simulation behavior for provider admission. |
| `historical_only` | Policy or closure family is retained only for traceability and should not be considered for provider admission. |

The report should make the tolerance bands explicit before applying them. If a
tolerance is not yet scientifically defensible, the report should say
`m8_continue_only` rather than silently treating the policy as provider-ready.

## Provider Admission Gates

No M3 provider implementation should start until M8 evidence proves:

- bounded site fractions over source-backed topology rows;
- mass-action residual error stays within an agreed tolerance band;
- association `ares` error is acceptable over real associating systems;
- total neutral `ares` impact is physically small enough where claimed;
- pressure and density residuals do not hide root-selection failures;
- first and second derivative errors are acceptable for local EOS use;
- CppAD-shaped JAX proxy evidence has been compared against exact implicit
  baselines for pure and mixture association schemes, with JAX explicitly
  treated as a proxy rather than provider CppAD proof;
- equilibrium-style objective/Jacobian/Hessian probe does not show unstable
  derivative behavior.
- end-to-end simulation timing shows a meaningful speedup after solver and
  density-root work are included, not just in closure-only microbenchmarks.

## Relationship To Issue #161

This spec should provide the evidence needed to resolve the design stance
behind provider issue #161.

The final #161 recommendation must choose one of these outcomes:

1. Close #161 with no provider implementation because Picard does not clear the
   evidence gates.
2. Close #161 as design-complete and open a narrower M3 provider-admission
   issue only if Picard clears the gates.
3. Keep #161 open as blocked only if the report identifies one specific
   missing evidence item that cannot be answered inside the current M8 toybox.

Issue #161 should not remain open as a broad catch-all after this final
relative-error and simulation evidence pass.

## Non-Goals

- No provider implementation.
- No compatibility API aliases.
- No public package behavior changes.
- No equilibrium implementation.
- No benchmark admission.
- No old closure-family resurrection.
- No new Picard policy grid beyond the existing fixed step-count and damping
  grid unless the report records a source-backed reason.
- No claim that JAX proves provider CppAD behavior; it is proxy evidence only.

## Open Questions

- Which exact tolerance bands decide `provider_candidate` versus
  `m8_continue_only` versus `provider_blocked`?
- Should the toybox retain historical rows in archived output, or delete
  non-retained closure code entirely?
- How much end-to-end simulation speedup is meaningful after density and
  saturation solves dominate the runtime?

## Proof Oracle Candidates For Later Planning

- `uv run python analyses/package_validation/explicit_association_toybox/scripts/final_picard_admission_report.py`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/picard_policy_grid/scripts/generate_data.py`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/pure_saturation_validation/scripts/generate_data.py`
- `uv run python analyses/package_validation/explicit_association_toybox/scripts/summarize_results.py`
- `uv run python run_pytest.py analyses/package_validation/explicit_association_toybox/tests -q`
- `rg -n "collapsed|diagonal|mean_field|polish" analyses/package_validation/explicit_association_toybox`
