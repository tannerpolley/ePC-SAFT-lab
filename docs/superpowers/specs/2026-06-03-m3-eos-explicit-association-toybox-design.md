# Python Toybox For Explicit Association Closure Accuracy

## Purpose

Create a Python-only analysis toybox for explicit PC-SAFT association closures.
The toybox should answer one narrow question:

```text
How accurate are the reduced explicit association equations against the exact
mass-action association model across EOS-relevant states and residual
Helmholtz outputs?
```

This is not a production EOS implementation plan. It is a source-controlled
analysis workflow for testing closure accuracy, failure regions, and promotion
evidence before any provider or equilibrium package change is proposed.

This spec was revised to include a deliberately small neutral PC-SAFT scaffold:
hard-chain and dispersion scalar residual Helmholtz contributions may be added
only so association-closure comparisons can report total `ares` differences.
They are not a density solver, property package, public API, or general-purpose
PC-SAFT implementation.

This first toybox slice is not the full validation strategy. The broader
paper-backed follow-up design lives at
`docs/superpowers/specs/2026-06-03-m3-eos-paper-backed-association-closure-validation-matrix-design.md`.
That spec adds Huang/Radosz topology formulas, real association scheme rows,
timing matrices, and a staged property-data lane. Use it before claiming that
the synthetic toybox grids cover real 2B/3B/4C association behavior.

## Project Context Evidence Used

- Verified: `docs/superpowers/PROJECT_CONTEXT.md` names the explicit
  association closure spec as the policy reference before adding approximate
  `X_A` closures or claiming exact derivatives of an approximate association
  model.
- Verified: `docs/superpowers/specs/2026-05-23-m3-eos-explicit-association-closure-for-pcsaft.md`
  defines `implicit_exact` as the solved mass-action PC-SAFT association model
  and `explicit_approx` as approximate algebraic closures.
- Verified: `docs/latex/explicit_assocation.tex` derives the full-matrix,
  seven-step damped Picard closure that underpins the active explicit
  approximation candidate.
- Verified: `docs/latex/equations.tex` owns the association site balance,
  association strength, association Helmholtz contribution, and association
  density/composition/temperature differential equations.
- Verified: `docs/latex/equations.tex` also owns `ares_hc`, `ares_disp`,
  and `ares_total`, with hard-chain and dispersion contribution equations
  kept separate from association.
- Verified: `docs/equations.md` maps hard-chain and dispersion formulas to
  provider implementation files and generated CppAD scalar helpers, confirming
  these terms are provider EOS concepts and not equilibrium or regression
  concepts.
- Verified: `packages/epcsaft/src/epcsaft/native/eos/contributions/association.cpp`
  owns the current exact association setup, mass-action site-fraction solve,
  diagnostics, and association contribution derivatives.
- Verified: `packages/epcsaft/src/epcsaft/native/eos/residual/cppad/association.h`
  currently rejects direct CppAD recording of active association and routes
  active association through implicit sensitivity helpers.
- Verified: `analyses/README.md` and `analyses/AGENTS.md` define
  `analyses/package_validation/<short_id>/` as the correct home for
  package-development analysis workflows that are not runtime package code.
- Verified: the linked legacy MEA-Thermodynamics script
  `archive/legacy_scripts/pcsaft_models_polley/pcsaft_electrolyte.py`
  contains a quick Python `pcsaft_ares(...)` style workflow that assembles
  `ares_hc`, `ares_disp`, `ares_assoc`, and total `ares`; it also imports
  SciPy optimizers, so it is reference material only for this repo's
  NumPy-first toybox.
- Verified: `docs/papers/md/ePC-SAFT-Literature/Huang and Radosz - 1990 - Equation of State for Small, Large, Polydisperse, and Associating Molecules.md`
  is the paper-backed topology source for future matrix coverage of 1, 2A,
  2B, 3A, 3B, 4A, 4B, and 4C association schemes.

## User Decisions

- Location: use `analyses/package_validation/explicit_association_toybox`.
- Baseline: build an independent Python exact mass-action baseline and allow
  optional native output cross-checks.
- First scope: EOS diagnostics only, not equilibrium route prototypes.
- Closure set: evaluate the exact 2B reduction as a baseline check and
  `damped_picard_7_05` as the only active explicit approximation candidate.
- Promotion policy: produce an evidence gate and recommendations, but do not
  admit production behavior directly from the toybox.
- Dependency policy: a later policy change may permit SciPy only inside this
  toybox. Until that guard is changed explicitly, the committed first version
  should use Python, NumPy, Matplotlib, existing package APIs, and small local
  linear algebra helpers.
- HC/dispersion extension: revise the existing toybox spec rather than create
  a separate playground spec.
- HC/dispersion scope: scalar residual Helmholtz only. The toybox receives
  temperature and density as known inputs and does not include an internal
  density solve.
- Legacy script policy: use the MEA-Thermodynamics `pcsaft_electrolyte.py`
  file as a reference for quick workflow shape only; rewrite equations cleanly
  from local repo equation docs and current toybox conventions.

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
    pcsaft_inputs.py
    hard_chain.py
    dispersion.py
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
    test_exact_2b_reduction.py
    test_mass_action_metrics.py
    test_output_schema.py
```

The toybox should be readable as a small scientific analysis package, not as a
new public package module. Keep all generated runs under
`figures/closure_accuracy/output/runs/`; retained CSV summaries, plotted data,
figures, and Matplotlib sidecars belong under the figure-owned `output/`
folder.

## Lightweight Neutral PC-SAFT Scaffold

The toybox may grow from an association-only comparison into a tiny neutral
PC-SAFT residual playground, but only for the explicit association closure
study.

Recommended module ownership:

```text
scripts/
  pcsaft_inputs.py      # small dataclasses and validated arrays for T, rho, x, m, sigma, epsilon
  hard_chain.py         # scalar ares_hs and ares_hc helpers
  dispersion.py         # scalar ares_disp helpers and Gross-style polynomial moments
  association_models.py # exact and approximate association Helmholtz helpers
```

The interface should stay simple:

```python
state = ToyPCSAFTState(
    temperature=temperature,
    density=density,
    composition=composition,
    segments=m,
    sigma=sigma,
    epsilon_over_k=epsilon_over_k,
)
```

Then each closure row can report:

```text
ares_hc
ares_disp
ares_assoc_exact
ares_assoc_closure
ares_total_exact = ares_hc + ares_disp + ares_assoc_exact
ares_total_closure = ares_hc + ares_disp + ares_assoc_closure
ares_total_abs_error
ares_total_rel_error
```

Hard-chain and dispersion are identical between the exact and explicit
association rows for a given state. Their purpose is contextual: they show how
large the association approximation is relative to the full neutral residual
Helmholtz background.

This deliberately excludes:

- internal density solving;
- vapor/liquid root selection;
- pressure, fugacity, activity, or chemical-potential prediction;
- temperature, density, or composition derivatives;
- ionic terms, Born terms, dielectric terms, polar terms, or regression logic;
- public Python package APIs.

Use `temperature` and `density` as explicit grid inputs. If later analysis
needs a density root, that should be a separate follow-up spec because it
changes the toybox from residual comparison into property solving.

## HC And Dispersion Formula Boundaries

The first HC/dispersion addition should be source-backed and small:

- read equation names from local docs: `ares_hs`, `ares_hc`, `ares_disp`, and
  supporting dispersion moments/polynomials;
- use neutral component parameters only: `m`, `sigma`, `epsilon_over_k`, and
  optional binary `k_ij`;
- keep units explicit in the README and configs;
- add enough tests to prove hard-chain and dispersion return finite scalar
  values, reduce correctly in simple one-component states, and do not depend
  on association closure choice;
- optionally add a native-provider cross-check later, but do not make provider
  output the only baseline for the Python formulas.

The legacy MEA script is useful as a quick mental map because it computes:

```text
ares = ares_hc + ares_disp + ares_assoc + other optional terms
```

For this repo, keep only:

```text
ares_neutral_toy = ares_hc + ares_disp + ares_assoc
```

and omit every optional term not needed by the explicit association closure
study.

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

The baseline should also expose a direct grouped 2B exact formula. That formula
is the simplest way to prove the toybox equations are wired correctly before
comparing the active explicit candidate.

Native provider calls may be used as cross-checks after the independent Python
baseline exists, but they should not be the only exact reference.

## Closure Candidate

Evaluate the exact baseline and the active approximation under one consistent
interface:

1. `exact_2b_reduction`
   - one associating component;
   - donor/acceptor 2B topology;
   - inert partner components;
   - expected to match the exact mass-action solution when the topology
     assumptions match the full site matrix.

2. `damped_picard_7_05`
   - full site matrix;
   - seven damped Picard steps;
   - fixed damping `omega = 0.5`;
   - the only active explicit approximate closure in this toybox.

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

For HC/dispersion context, add a second small config layer after the current
synthetic association grids:

- neutral one-component sanity states;
- one associating component plus one inert component;
- fixed `T`, fixed `rho`, and known `x`;
- compact parameter snapshots for `m`, `sigma`, `epsilon_over_k`, and optional
  `k_ij`;
- no density-root inputs and no pressure targets.

## Metrics

Do not validate only site fractions. The toybox should report state-level and
thermodynamic-output-level diagnostics:

- maximum absolute site-fraction error;
- maximum relative site-fraction error where the exact site fraction is safely
  away from zero;
- mass-action residual infinity norm;
- association Helmholtz absolute and relative error;
- hard-chain scalar residual Helmholtz value;
- dispersion scalar residual Helmholtz value;
- exact total neutral residual Helmholtz value;
- closure total neutral residual Helmholtz value;
- total neutral residual Helmholtz absolute and relative error;
- closure boundedness: `0 < X_A <= 1`;
- exact baseline iteration count and residual;
- closure runtime per grid row;
- failure-region tags.

Do not include association compressibility, residual chemical-potential, or
fugacity diagnostics in the HC/dispersion extension unless a later plan also
adds derivative formulas. For the requested light toybox, `ares` is enough:
the user will provide temperature and density, so pressure and density solving
are outside scope.

Add simulation-time comparison as a first-class metric:

- exact implicit association solve elapsed time;
- explicit closure elapsed time;
- total row elapsed time;
- speedup ratio where exact timing is safely nonzero.

Runtime timing should be used as relative analysis evidence only. It must not
be presented as provider performance proof because this is Python analysis code.

## Evidence Gate

The toybox should classify closures into evidence bands rather than return one
global pass/fail result:

```text
exact_reduction_verified:
    The 2B exact reduction matches the exact Python baseline within tight numerical
    tolerance for its declared topology.

promising_eos_approximation:
    Closure error is small in association Helmholtz and total neutral residual
    Helmholtz over a named state envelope.

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

Add a second figure or panel after HC/dispersion lands:

- x-axis: closure variant;
- y-axis: maximum or percentile total `ares` relative error;
- color or facet: state family;
- companion table: exact implicit association time, explicit closure time,
  and speedup ratio.

The existing `closure_accuracy` figure can remain focused on association
Helmholtz. The residual `ares` comparison should be explicit enough that a
reviewer can tell whether the association approximation is large in isolation
or still small relative to HC+dispersion background terms.

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
- Keeping one active explicit candidate keeps the toybox focused on property
  and derivative propagation instead of closure cataloging.
- Adding HC and dispersion makes the error scale more thermodynamically
  interpretable, but it also risks turning the analysis into a shadow package.
  Keep the scaffold scalar-only and analysis-owned.
- EOS `ares` diagnostics answer whether the approximation is thermodynamically
  plausible at fixed `T`, `rho`, and `x`. They do not prove pressure, density,
  fugacity, chemical-potential, or M4 equilibrium route suitability.
- Allowing SciPy later can speed analysis prototyping, but it requires a
  deliberate exception to current repo dependency policy.

## Non-Goals

- No provider C++ implementation changes.
- No public `epcsaft` API changes.
- No equilibrium route admission.
- No regression workflow changes.
- No production derivative claim for approximate association closures.
- No internal density solve.
- No pressure, chemical-potential, fugacity, or phase-equilibrium properties in
  the HC/dispersion extension.
- No broad PC-SAFT playground or package-like import surface.
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

For the HC/dispersion extension specifically, the recommended next plan should
stay NumPy-only and scalar-only:

1. Add toy `pcsaft_inputs.py`, `hard_chain.py`, and `dispersion.py`.
2. Add fixed-state neutral parameter configs.
3. Extend metrics with `ares_hc`, `ares_disp`, exact/closure total `ares`,
   total `ares` error, exact association timing, explicit closure timing, and
   speedup ratio.
4. Add a second residual-error figure/table without touching package runtime
   code.
