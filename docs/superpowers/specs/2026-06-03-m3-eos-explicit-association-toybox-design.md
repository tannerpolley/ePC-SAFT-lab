# Python Toybox For Explicit Association Closure Accuracy

## Purpose

Create a Python-only analysis toybox for explicit PC-SAFT association closures.
The toybox should answer one narrow question:

```text
How accurate are the reduced explicit association equations against the exact
mass-action association model across EOS-relevant states?
```

This is not a production EOS implementation plan. It is a source-controlled
analysis workflow for testing closure accuracy, failure regions, and promotion
evidence before any provider or equilibrium package change is proposed.

## Project Context Evidence Used

- Verified: `docs/superpowers/PROJECT_CONTEXT.md` names the explicit
  association closure spec as the policy reference before adding approximate
  `X_A` closures or claiming exact derivatives of an approximate association
  model.
- Verified: `docs/superpowers/specs/2026-05-23-m3-eos-explicit-association-closure-for-pcsaft.md`
  defines `implicit_exact` as the solved mass-action PC-SAFT association model
  and `explicit_approx` as approximate algebraic closures.
- Verified: `docs/derivation/explicit_association_closure_for_pcsaft.tex`
  derives Closure A, full-matrix Picard unroll closures, diagonal-polish
  closures, and collapsed donor/acceptor mean-field closure candidates.
- Verified: `docs/latex/equations.tex` owns the association site balance,
  association strength, association Helmholtz contribution, and association
  density/composition/temperature differential equations.
- Verified: `packages/epcsaft/src/epcsaft/native/eos/contributions/association.cpp`
  owns the current exact association setup, mass-action site-fraction solve,
  diagnostics, and association contribution derivatives.
- Verified: `packages/epcsaft/src/epcsaft/native/eos/residual/cppad/association.h`
  currently rejects direct CppAD recording of active association and routes
  active association through implicit sensitivity helpers.
- Verified: `analyses/README.md` and `analyses/AGENTS.md` define
  `analyses/package_validation/<short_id>/` as the correct home for
  package-development analysis workflows that are not runtime package code.

## User Decisions

- Location: use `analyses/package_validation/explicit_association_toybox`.
- Baseline: build an independent Python exact mass-action baseline and allow
  optional native output cross-checks.
- First scope: EOS diagnostics only, not equilibrium route prototypes.
- Closure set: evaluate all four closure families from the current derivation:
  one-component 2B, full-matrix Picard unroll, Picard plus diagonal polish, and
  collapsed donor/acceptor mean field.
- Promotion policy: produce an evidence gate and recommendations, but do not
  admit production behavior directly from the toybox.
- Dependency policy: a later policy change may permit SciPy only inside this
  toybox. Until that guard is changed explicitly, the committed first version
  should use Python, NumPy, Matplotlib, existing package APIs, and small local
  linear algebra helpers.

## Recommended Approach

Build a self-contained package-validation analysis:

```text
analyses/package_validation/explicit_association_toybox/
  README.md
  analysis.yaml
  config/
    closure_sweep.yaml
    systems.yaml
  scripts/
    association_models.py
    exact_baseline.py
    closure_models.py
    metrics.py
    run_grid.py
    summarize_results.py
  figures/
    closure_accuracy/
      input/
      output/
      scripts/
        generate_data.py
        render_figure.py
  tests/
    test_closure_a_exact_reduction.py
    test_mass_action_metrics.py
    test_output_schema.py
```

The toybox should be readable as a small scientific analysis package, not as a
new public package module. Keep all generated runs under
`figures/closure_accuracy/output/runs/`; retained CSV summaries, plotted data,
figures, and Matplotlib sidecars belong under the figure-owned `output/`
folder.

## Exact Baseline

The baseline should implement the exact association model in Python:

```text
F_a(X; T, rho, x, p) =
X_a * (1 + rho * sum_b x_assoc_b * X_b * Delta_ab) - 1
```

The first baseline solve should mirror the provider behavior closely enough to
be auditable:

- fixed under-relaxed Picard iteration;
- independent mass-action residual norm;
- site-fraction bounds check;
- iteration count and solve diagnostics;
- explicit failure when the exact solve does not converge.

The baseline should also expose a direct grouped 2B exact formula for Closure A
cases. That formula is the simplest way to prove the toybox equations are wired
correctly before comparing broader closures.

Native provider calls may be used as cross-checks after the independent Python
baseline exists, but they should not be the only exact reference.

## Closure Candidates

Evaluate these closures under one consistent interface:

1. `closure_2b_exact_reduction`
   - one associating component;
   - donor/acceptor 2B topology;
   - inert partner components;
   - expected to match the exact mass-action solution when the topology
     assumptions match the full site matrix.

2. `explicit_picard_unroll_N`
   - full site matrix;
   - row-sum bounded initializer;
   - fixed unroll counts such as `1`, `3`, and `5`.

3. `explicit_damped_picard_unroll_N`
   - full site matrix;
   - fixed damping such as `omega = 0.5`;
   - fixed unroll counts such as `3` and `5`.

4. `explicit_picard3_diag_newton1`
   - three damped Picard steps;
   - one diagonal-polish correction;
   - candidate for the strongest first explicit approximate closure.

5. `collapsed_donor_acceptor_mean_field`
   - diagnostic and screening closure only;
   - records component-specific information loss in the output metadata.

All closure outputs must include labels that separate exact reductions from
approximations:

```text
association_model = implicit_exact | explicit_approx
association_closure = <closure_name>
exact_derivative_of = exact_mass_action | approximate_association_closure
```

## State And System Coverage

Start with controlled synthetic systems before using literature-shaped systems:

- pure symmetric 2B associating fluid;
- one associating component plus one inert component;
- one associating component plus multiple inert components;
- asymmetric donor/acceptor site counts;
- multi-component full-matrix associating cases;
- strong-association and high-density stress cases;
- low-density and dilute-associating-component limits.

Then add Gross/Sadowski-style one-associating-component cases where local
parameter snapshots are already available or can be added under the analysis
root:

- methanol/isobutane;
- methanol/cyclohexane;
- ethanol/n-butane;
- 1-butanol/n-butane;
- 1-pentanol/benzene.

The first retained grids should cover:

- temperature;
- molar density;
- associating component mole fraction;
- association strength scale;
- site topology;
- closure variant.

## Metrics

Do not validate only site fractions. The toybox should report state-level and
thermodynamic-output-level diagnostics:

- maximum absolute site-fraction error;
- maximum relative site-fraction error where the exact site fraction is safely
  away from zero;
- mass-action residual infinity norm;
- association Helmholtz absolute and relative error;
- association compressibility contribution error;
- association residual chemical-potential contribution error;
- association fugacity-coefficient contribution error;
- closure boundedness: `0 < X_A <= 1`;
- exact baseline iteration count and residual;
- closure runtime per grid row;
- failure-region tags.

For contribution-level pressure, residual chemical-potential, and fugacity
diagnostics, use the same association derivative equations that the provider
uses where practical. If an output requires a derivative that the toybox does
not yet evaluate, leave that output out of the first grid instead of replacing
it with a weaker surrogate.

## Evidence Gate

The toybox should classify closures into evidence bands rather than return one
global pass/fail result:

```text
exact_reduction_verified:
    Closure A matches the exact Python baseline within tight numerical
    tolerance for its declared topology.

promising_eos_approximation:
    Closure error is small in association Helmholtz, pressure contribution,
    residual chemical-potential contribution, and fugacity contribution over a
    named state envelope.

diagnostic_only:
    Closure is useful for seeds, trend analysis, or stress-region discovery,
    but fails at least one thermodynamic-output metric.

reject_for_provider_path:
    Closure produces invalid site fractions, large mass-action residuals, or
    unacceptable thermodynamic-output error over target states.
```

Initial reporting should preserve the 2-3 percent thermodynamic-output target
from the existing explicit association closure spec as a visible reference
line, but the toybox must also show the full error distribution and the states
that violate that line.

## SciPy Policy Note

The user wants the option to use SciPy inside this toybox later. Current repo
guards intentionally keep SciPy out of committed package, test, and analysis
runtime imports. Therefore the first implementation plan should either:

1. keep the committed toybox on NumPy and local linear algebra helpers; or
2. include an explicit project-structure policy change that permits SciPy only
   inside `analyses/package_validation/explicit_association_toybox`.

Do not silently add a SciPy import or dependency as part of the toybox without
the guard change.

## Tradeoffs

- Python-only analysis is easier to inspect and iterate than production C++,
  but it cannot prove production performance or provider API behavior.
- An independent exact baseline reduces risk of copying provider mistakes, but
  native cross-checks are still valuable for matching package conventions.
- Including all closure families gives a useful map, but Closure D should stay
  clearly labeled as a diagnostic mean-field collapse.
- EOS diagnostics answer whether the approximation is thermodynamically
  plausible. They do not prove M4 equilibrium route suitability.
- Allowing SciPy later can speed analysis prototyping, but it requires a
  deliberate exception to current repo dependency policy.

## Non-Goals

- No provider C++ implementation changes.
- No public `epcsaft` API changes.
- No equilibrium route admission.
- No regression workflow changes.
- No production derivative claim for approximate association closures.
- No automatic promotion from toybox evidence to accepted provider behavior.
- No retained generated run payloads outside figure-owned output folders.

## Optional Milestone Linkage

- M3 - EOS: primary owner because the toybox studies provider EOS association
  equations and derivative-relevant thermodynamic outputs.
- M6 - Validation: later owner if retained grids become executable benchmark
  evidence.
- M4 - Equilibrium: later consumer only if a follow-up plan uses the toybox
  evidence to design an associating-equilibrium approximation experiment.

## Later Project-Plan Proof Candidates

These commands are candidates for a later `$project-plan`; they are not proof
that exists today:

```powershell
uv run python analyses/package_validation/explicit_association_toybox/figures/closure_accuracy/scripts/generate_data.py
uv run python analyses/package_validation/explicit_association_toybox/figures/closure_accuracy/scripts/render_figure.py
uv run python run_pytest.py analyses/package_validation/explicit_association_toybox/tests -q
uv run python run_pytest.py tests/workflows/repo/test_project_structure.py -q
uv run python scripts/dev/validate_project.py quick
```

If the SciPy policy exception is added later, include a scoped structure test
that proves SciPy imports are allowed only in this analysis toybox and nowhere
else in package, test, or analysis runtime code.

## Open Questions For Planning

- What exact thermodynamic-output thresholds should promote a closure from
  `diagnostic_only` to `promising_eos_approximation`?
- Should Gross/Sadowski parameter snapshots be copied into this analysis root
  or referenced from existing paper-validation snapshots?
- Which native provider method should be used for optional convention
  cross-checks without making the provider the only exact baseline?
- Should the first plan include the SciPy policy exception, or defer it until
  the NumPy-only toybox shows enough value?
- Should derivative-level diagnostics include second derivatives in the first
  analysis, or wait until first-order EOS diagnostics are stable?

## Recommended Next Route

Use `$project-plan` to turn this spec into an implementation plan only after
deciding whether the first implementation will stay NumPy-only or include the
explicit SciPy policy exception.
