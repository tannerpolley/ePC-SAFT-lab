# Neutral Nonassociating LLE Showcase

This package-validation analysis retains the source-backed neutral
nonassociating LLE showcase for M4 issue #250.

The source fixture is:

```text
data/reference/equilibrium_benchmarks/neutral_lle/matsuda_2011_pfhexane_hexane/
```

Scope:

- neutral, nonelectrolyte, nonreactive, nonassociating binary LLE only;
- current public `Equilibrium(..., route="lle", ...)` utility route;
- HELD Stage II replay and Stage III replay-consumption evidence from the
  current native route.

This analysis does not promote generalized phase-set admission and does not
cover associating, electrolyte, reactive, CE, or CPE behavior.

Regenerate retained data:

```powershell
uv run --no-sync python analyses/package_validation/neutral_nonassociating_lle_showcase/scripts/generate_data.py
```

Render figures:

```powershell
uv run --no-sync python analyses/package_validation/neutral_nonassociating_lle_showcase/scripts/render_figures.py
```
