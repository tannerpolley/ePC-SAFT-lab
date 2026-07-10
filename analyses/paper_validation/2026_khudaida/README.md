# 2026 Khudaida Analysis

Electrolyte LLE paper-validation workflow for Khudaida et al. 2026 water + ethanol + isobutanol + NaCl salting-out data.

Scope:

- Non-reactive electrolyte LLE only.
- Internal package diagnostic: partially source-backed `electrolyte_lle` component validation; no public route is admitted.
- Parameter dataset: `2026_Khudaida`, with paper Tables 5-7 and Born SSM+DS options retained under `shared/source/`. Table 7 supplies source references for 8 of 10 required `k_ij` pairs; its Butanol/Na+ and Butanol/Cl- zero entries have no source references and remain unresolved. The paper does not supply `l_ij` or `k_hb_ij`, so no executable matrices for those families are retained.
- Figures 1-9 and Tables 9-10 have figure-owned workflows; Supporting Information Figures S2-S3 are retained as three-panel workflows covering subfigures a-c.
- Supporting Information Tables S1-S4 are retained as analysis-owned CSV inputs for distribution/separation-factor and eNRTL comparison checks.

Entry point:

```bash
uv run python analyses/paper_validation/2026_khudaida/scripts/run_all.py
```

Generated figure assets are written under each `figures/<figure_id>/results/` folder. The retained CSVs snapshot the exact plotted/source data used by each figure workflow.

Validation:

```bash
uv run --no-sync python scripts/validation/check_khudaida_2026_figure_validation.py --require-complete
```

To refresh the package model rows instead of reusing the retained
`results/data/model_tielines.csv` files:

```bash
KHUDAIDA_FORCE_RECOMPUTE=1 uv run --no-sync python analyses/paper_validation/2026_khudaida/scripts/run_all.py
```

Figures 2-7 and Supporting Information Figures S2-S3 use a private,
source-bounded component diagnostic. Parameter provenance is checked before
native mixture construction; the current unresolved interaction families
produce retained rejected model rows without executing a package solve. This
analysis is evidence for repairing and eventually re-admitting the capability,
not evidence of production exposure.

Current scientific status: the figure artifact contract is complete, but the
internal electrolyte LLE component diagnostic does not yet reproduce the Khudaida salted
tie-lines. The validation checker reports those model-fit failures separately
from the file/plot contract. Partial `k_ij` source coverage and unresolved
`l_ij` and `k_hb_ij` families are blocking model-evidence conditions; the
retained zero accepted-tieline result is not source-complete evidence.
