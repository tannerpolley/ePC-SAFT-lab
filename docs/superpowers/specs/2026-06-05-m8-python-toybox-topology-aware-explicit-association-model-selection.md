# Topology-Aware Explicit Association Model Selection

## Summary

Use the M8 Python toybox to design a topology-aware association model selector
before making any M3 provider admission decision for issue 161.

The corrected interpretation of the retained stress evidence is:

- The previous M8 lanes already tested the Picard step-count and damping grid.
- The originally named candidate, fixed `n = 7` with damping `lambda = 0.5`,
  is not strong enough.
- The stress-grid evidence should not be read as a final rejection of every
  explicit association route.
- Undamped fixed-depth Picard policies, especially `n = 7`, `n = 9`, and
  `n = 11` with `lambda = 1.0`, may be much closer to the exact implicit
  association baseline while still remaining explicit.
- Topology-gated exact reductions should be used whenever the site topology and
  association assumptions prove that they are exact.
- Site-class lumped reductions should be investigated as a more scientific
  middle path between exact topology formulas and generic fixed-depth Picard.

The target design is not one universal explicit association formula. The target
design is an association evaluator that can inspect the association topology,
site classes, component/site mapping, and association-strength matrix, then use
the best proven model for that case.

This is a loose M8 spec. It is not a provider implementation plan.

## Project Context Evidence

- `docs/superpowers/PROJECT_CONTEXT.md` assigns exploratory EOS, derivative,
  property, and equilibrium-style analysis to M8 until it is ready for M3
  provider admission.
- `docs/superpowers/milestones/M8-python-toybox/README.md` says M8 is the
  Python-only toybox milestone for cross-cutting EOS/equilibrium-style
  research.
- Issue 161 remains the M3 design issue for explicit PC-SAFT association-site
  closures.
- PR 234 added the retained Picard stress evidence lane:
  `analyses/package_validation/explicit_association_toybox/figures/picard_stress_evidence/output/picard_stress_evidence.csv`.
- The retained stress evidence covers `66` stress cases, `25` Picard policies,
  and `1,716` rows with exact implicit rows and Picard rows.
- The existing stress memo selected `retire_picard`, but that decision was based
  on the stress gates and the originally emphasized Picard candidate. The
  policy-grid data also show that undamped fixed-depth Picard is much more
  accurate than the damped `n = 7`, `lambda = 0.5` candidate.
- Existing derivation context:
  `docs/latex/explicit_assocation.tex`.
- Existing paper-backed validation design:
  `docs/superpowers/specs/2026-06-03-m3-eos-paper-backed-association-closure-validation-matrix-design.md`.

## User Decisions Captured

- Treat the retained stress matrix as already having tested the step-count and
  damping policy grid.
- Do not reduce the question to whether `n = 7`, `lambda = 0.5` survives.
- Keep explicitness as the key advantage: a fixed unrolled expression may still
  be useful even if it is not dramatically faster than exact implicit
  sensitivities.
- Use topology-gated exact reductions wherever the topology and association
  assumptions prove exactness.
- Investigate site-class lumped reductions as a real candidate, not as a side
  note.
- Eventually, the association function should be able to choose the best model
  from the association case, site topology, site classes, and association
  parameters.

## Corrected Read Of The Existing Picard Policy Evidence

The previous M8 policy-grid work tested `n` and `lambda`. It showed a strong
accuracy difference between damped and undamped fixed-depth Picard.

Retained stress-grid examples:

| Fixed Picard policy | Worst stress error across scalar/property/derivative/Hessian/objective proxies | Median simulation speedup |
| --- | ---: | ---: |
| `n = 7`, `lambda = 0.5` | `1.56e-2` | `7.95x` |
| `n = 11`, `lambda = 0.5` | `2.84e-3` | `6.33x` |
| `n = 7`, `lambda = 0.8` | `1.19e-3` | `7.67x` |
| `n = 11`, `lambda = 0.8` | `3.82e-5` | `6.19x` |
| `n = 5`, `lambda = 1.0` | `1.24e-3` | `9.30x` |
| `n = 7`, `lambda = 1.0` | `8.48e-5` | `7.99x` |
| `n = 9`, `lambda = 1.0` | `4.98e-6` | `7.04x` |
| `n = 11`, `lambda = 1.0` | `4.65e-6` | `6.48x` |

Interpretation:

- Fixed `n = 7`, `lambda = 0.5` should not be the final candidate.
- Fixed `n = 7`, `lambda = 1.0` may already be accurate enough for many
  toybox stress gates.
- Fixed `n = 9`, `lambda = 1.0` appears to reach a much stronger agreement
  region while staying explicit.
- Fixed `n = 11`, `lambda = 1.0` does not clearly improve the retained Hessian
  proxy over `n = 9`, suggesting numerical noise or proxy limits may dominate.
- The next question should be policy selection and topology selection, not
  another broad unfiltered Picard sweep.

## Explicitness Rule

A Picard expression remains explicit when:

- the number of updates is fixed before evaluation;
- there is no convergence loop;
- there is no state-dependent stopping criterion;
- there is no internal nonlinear solve;
- all outputs are computed by a deterministic expression graph from the inputs.

Under that rule, `n = 9`, `lambda = 1.0` is still explicit. It is just a deeper
unrolled expression graph than `n = 7`, `lambda = 0.5`.

The tradeoff is graph size. Fixed-depth Picard graph cost grows roughly with:

```text
iteration_count * active_site_pair_count
```

That cost must be checked for:

- scalar EOS evaluation time;
- CppAD tape size;
- Jacobian and Hessian timing;
- memory use;
- compiler/build stress if generated into native code;
- equilibrium objective callback cost if later consumed by M4.

## Recommended Model Selector Concept

The future association evaluator should not expose many user-facing closure
choices. It should make an internal model-selection decision from the case
structure.

Suggested decision order:

1. **No association sites**
   - Return the exact zero association contribution.
   - No site-fraction solve is needed.

2. **Topology-gated exact reduction**
   - If the topology, site multiplicity, active site-pair matrix, and
     association-strength assumptions match a proven exact formula, use the
     exact closed reduction.
   - Candidate sources include Huang/Radosz-style topology reductions and
     rigorously derived 1-site or 2B forms.

3. **Site-class lumped reduction**
   - Group sites into equivalence classes when sites share component ownership,
     multiplicity, site role, and association-strength relationships.
   - Solve or reduce the smaller class-level system.
   - If the class-level system admits an exact formula, use it.
   - If it does not admit a clean exact formula, test fixed-depth explicit
     updates on the class-level system rather than the full site-level system.

4. **Fixed-depth explicit Picard candidate**
   - Use only if the topology is outside the exact/lumped exact set but within
     proven approximation bounds.
   - Candidate policies should focus on `n = 7`, `n = 9`, and possibly `n = 11`
     with `lambda = 1.0`.

5. **Exact implicit default path**
   - If no explicit route is admitted for the topology and parameter regime,
     keep the exact implicit association path as the scientifically reliable
     production behavior.

## Topology-Gated Exact Reductions

These should be treated as the highest-quality explicit route.

The toybox should classify cases by:

- component count;
- site count;
- site kind labels such as donor and acceptor;
- site component ownership;
- site multiplicity;
- active site-pair topology;
- equality or inequality structure of the association-strength matrix;
- whether `k_hb`, `epsilon_hb`, and binary terms such as `l_ij` preserve or
  break the assumptions of the reduction.

Exact reductions should be admitted only when:

- the formula is derived and documented;
- the formula is tested against exact implicit mass-action solves;
- site fractions match within strict tolerance;
- `a_assoc`, pressure-like proxies, fugacity-like proxies, and
  chemical-potential-like proxies match;
- first and second derivatives match the exact implicit sensitivities or an
  independently verified reference derivative baseline.

Important: exact reductions are not approximate closures. Where valid, they are
the preferred route.

## Site-Class Lumped Reductions

Site-class lumping is the most promising next research direction because it uses
association structure instead of blindly unrolling the full site-level Picard
map.

The core idea:

```text
site-level X_A variables -> class-level X_c variables
```

Sites can be grouped when they are equivalent under the association equations.
Possible equivalence criteria:

- same component ownership;
- same site role;
- same multiplicity;
- same active-pair pattern after accounting for class multiplicity;
- same association-strength row/column structure;
- same dependence on pure parameters and binary modifiers.

Expected benefits:

- fewer unknowns;
- smaller expression graphs;
- easier exact reductions for common topologies;
- clearer connection to literature topology formulas;
- less noisy derivative and Hessian behavior than generic full-site Picard.

Risks:

- incorrect grouping can silently change the model;
- binary modifiers may break apparent symmetry;
- temperature, density, and composition dependence can break simplified forms;
- mixtures with cross-association may require class-level matrices that are
  still nontrivial.

The toybox should intentionally test where lumping is exact, where it is an
approximation, and where it must not be used.

## Fixed-Depth Picard Candidate Policy

If Picard remains in the research path, it should be reframed as:

```text
fixed-depth explicit Picard approximation
```

not:

```text
the Picard 7, lambda 0.5 candidate
```

Candidate policies for the next lane:

- `n = 7`, `lambda = 1.0`
- `n = 9`, `lambda = 1.0`
- `n = 11`, `lambda = 1.0` only to confirm whether `n = 9` has reached the
  practical proxy floor
- optionally `n = 7` and `n = 9` with `lambda = 0.8` as stability comparisons

The next lane should not spend equal effort on weak policies that are already
dominated by retained evidence.

## Association Parameter Coverage

Future tests must cover the parameter shapes that matter for provider EOS:

- pure association energy parameters;
- pure association volume parameters;
- `k_hb`-like association volume scaling;
- binary cross-association modifiers;
- `l_ij`-like combining-rule perturbations;
- unequal donor/acceptor strengths;
- water-like multi-site association;
- alcohol-like 2B association;
- amine-like asymmetric donor/acceptor schemes where relevant.

The selector must know whether those parameters preserve exact reduction
assumptions or force a more general route.

## Evidence Required Before M3 Admission

A future plan should require retained evidence for:

- exact implicit baseline rows for every tested topology;
- model selector decision rows explaining which route was chosen and why;
- site-fraction error;
- mass-action residual;
- `a_assoc` error;
- total residual Helmholtz proxy error;
- pressure proxy error;
- chemical-potential-like and fugacity-like proxy errors;
- first derivative agreement;
- Hessian agreement;
- CppAD-shaped graph cost or JAX graph-depth proxy;
- saturation or pressure-density behavior for real associating compounds;
- equilibrium-style local objective sensitivity.

The admission question should be:

```text
Can a topology-aware selector choose exact reductions, class reductions, or a
fixed-depth explicit policy while preserving property and derivative quality?
```

not:

```text
Can one generic Picard policy replace exact implicit association everywhere?
```

## Recommended Decision Outcomes

The next plan should force one of these outcomes:

1. **Provider exact reductions only**
   - Implement topology-gated exact reductions for proven cases.
   - Keep generic association exact implicit.
   - Do not implement approximate fixed-depth Picard.

2. **Provider exact reductions plus site-class reductions**
   - Add exact reductions and class-lumped reductions where the toybox proves
     correctness.
   - Keep generic association exact implicit.
   - Delay Picard approximation.

3. **Provider exact reductions plus a narrow fixed-depth explicit approximation**
   - Use exact reductions where valid.
   - Use fixed-depth Picard only for a proven bounded domain.
   - Require strong derivative and property evidence before M3 admission.

4. **M8 research only**
   - Keep all routes in the toybox.
   - Do not open M3 provider implementation work.

## Non-Goals

- No provider EOS implementation.
- No M4 equilibrium implementation.
- No M5 regression work.
- No benchmark promotion.
- No public API redesign.
- No user-facing closure selector.
- No broad capability claims.
- No replacement of exact implicit association without topology-specific proof.

## Open Questions

- Which exact topology reductions are already derivable from the literature
  notes and which need new derivation work?
- Can site-class lumping be represented as a deterministic classification rule
  over current provider association metadata?
- What is the minimum tolerance for treating fixed-depth Picard as equivalent
  enough for provider derivatives?
- Should the selector choose models by topology only, or also by parameter
  regime such as association-strength magnitude?
- How should real compound validation be weighted against synthetic stress-grid
  derivative evidence?
- Is `n = 9`, `lambda = 1.0` sufficient once CppAD-shaped Hessian evidence is
  measured directly rather than through toybox proxies?

## Proof Oracle Candidates For Later Planning

- Regenerate the retained Picard stress evidence:
  `uv run python analyses/package_validation/explicit_association_toybox/figures/picard_stress_evidence/scripts/generate_data.py`.
- Render the stress evidence figure:
  `uv run python analyses/package_validation/explicit_association_toybox/figures/picard_stress_evidence/scripts/render_figure.py`.
- Add a selector evidence lane that records exact reduction, class reduction,
  fixed-depth Picard, and exact implicit route decisions.
- Compare `n = 7`, `n = 9`, and `n = 11` with `lambda = 1.0` against exact
  implicit rows for property and derivative gates.
- Add site-class lumping tests against exact implicit mass-action solves.
- Add real associating compound pressure-density and saturation-style checks for
  selector-chosen routes.
- Run the toybox tests:
  `uv run python run_pytest.py analyses/package_validation/explicit_association_toybox/tests -q`.
- Run project validation:
  `uv run python scripts/dev/validate_project.py quick`.

## Recommended Next Route

Use `$project:write-plan` later to turn this into one M8 plan. The plan should
produce a selector evidence packet, not provider code. Only after the selector
packet passes property and derivative gates should a narrow M3 provider issue be
created.
