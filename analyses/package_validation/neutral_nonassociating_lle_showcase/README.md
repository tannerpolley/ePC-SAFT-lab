# Neutral Nonassociating LLE Showcase

This package-validation analysis retains the source-backed neutral
nonassociating LLE showcase for M4 issue #250.

The source fixture is:

```text
data/reference/equilibrium_benchmarks/neutral_lle/perfluorohexane_hexane/
```

Scope:

- neutral, nonelectrolyte, nonreactive, nonassociating binary LLE only;
- internal native TPD candidate generation and a one-pass sampled-candidate
  bound audit;
- comparison of the sampled candidates with the retained Matsuda/NIST source
  pair as diagnostic findings.

The public `lle` route is closed. This analysis does not provide a global HELD
dual-loop proof, certify phase-set completeness, or support public route
admission. It also does not cover associating, electrolyte, reactive, CE, or
CPE behavior.

Regenerate retained data:

```bash
uv run --no-sync python analyses/package_validation/neutral_nonassociating_lle_showcase/scripts/generate_data.py
```

Render figures:

```bash
uv run --no-sync python analyses/package_validation/neutral_nonassociating_lle_showcase/scripts/render_figures.py
```
