# 2026 Khudaida Analysis

Electrolyte LLE paper-validation workflow for Khudaida et al. 2026 water + ethanol + isobutanol + NaCl salting-out data.

Scope:

- Non-reactive electrolyte LLE only.
- Public package route: `electrolyte_lle`.
- Parameter dataset: `2026_Khudaida`, with paper Tables 5-7 and Born SSM+DS options retained under `shared/source/`.
- Figures 1-9 and Tables 9-10 have figure-owned workflows; Supporting Information Figures S2-S3 are retained as three-panel workflows covering subfigures a-c.
- Supporting Information Tables S1-S4 are retained as analysis-owned CSV inputs for distribution/separation-factor and eNRTL comparison checks.

Entry point:

```powershell
uv run python analyses\paper_validation\2026_khudaida\scripts\run_all.py
```

Generated figure assets are written under each `figures/<figure_id>/results/` folder. The retained CSVs snapshot the exact plotted/source data used by each figure workflow.

Validation:

```powershell
uv run --no-sync python scripts\validation\check_khudaida_2026_figure_validation.py --require-complete
```

To refresh the package model rows instead of reusing the retained
`results/data/model_tielines.csv` files:

```powershell
$env:KHUDAIDA_FORCE_RECOMPUTE = "1"
uv run --no-sync python analyses\paper_validation\2026_khudaida\scripts\run_all.py
```

Figures 2-7 and Supporting Information Figures S2-S3 now call the public
`epcsaft_equilibrium.Equilibrium(..., route="electrolyte_lle")` entry point
through a per-feed isolated solve helper. The isolation is deliberate: native
solver failures are recorded as failed model points instead of aborting the
whole figure batch.

Current scientific status: the figure artifact contract is complete, but the
public electrolyte LLE route does not yet reproduce the Khudaida salted
tie-lines. The validation checker reports those model-fit failures separately
from the file/plot contract so the missing equilibrium behavior remains visible.
