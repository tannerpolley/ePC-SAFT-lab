# 2026 Khudaida Analysis

Electrolyte LLE paper-validation workflow for Khudaida et al. 2026 water + ethanol + isobutanol + NaCl salting-out data.

Scope:

- Non-reactive electrolyte LLE only.
- Public package route: `mix.equilibrium(kind="electrolyte_lle", ...)`.
- Parameter dataset: `2026_Khudaida`, with paper Tables 5-7 and Born SSM+DS options retained under `shared/source/`.
- Figures 1-9 and Tables 9-10 have figure-owned workflows; Supporting Information Figures S2-S3 are retained as three-panel workflows covering subfigures a-c.
- Supporting Information Tables S1-S4 are retained as analysis-owned CSV inputs for distribution/separation-factor and eNRTL comparison checks.

Entry point:

```powershell
uv run python analyses\paper_validation\2026_khudaida\scripts\run_all.py
```

Generated figure assets are written under each `figures/<figure_id>/results/` folder. The retained CSVs snapshot the exact plotted/source data used by each figure workflow.

The old live-Ipopt diagnostic entry point for Figures 2-7 was removed during
the package-layout cleanup because it called retired private native symbols
from the provider module. Future Khudaida diagnostic reruns should use the
package-owned equilibrium extension API and write figure-owned outputs.
