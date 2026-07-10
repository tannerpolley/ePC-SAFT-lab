# 2026 Khudaida analysis provenance

- Tables 3 and 4 in the local Khudaida markdown/PDF are treated as the canonical experimental tie-line source for Figures 2-7 and for the salted points in Figures 8-9.
- Analysis-owned source CSVs in `shared/source/` retain paper Tables 3-7 and Supporting Information Tables S1-S4. The runtime dataset `2026_Khudaida` uses the paper's Table 5 pure-component parameters, Table 6 dielectric constants, Table 7 binary interaction parameters, and the Figiel 2025 SSM+DS Born option family.
- Figures S2 and S3 are represented as three-panel figure-owned workflows that reuse the internal electrolyte LLE component diagnostic and snapshot the exact plotted phase/feed points.
- Figure 1 salt-free data and the no-salt points in Figures 8-9 were reconstructed from the local paper figures because the Zotero baseline source remained inaccessible in this session.
- The no-salt baseline is therefore marked as `published_figure_trace` in the emitted CSV files.
- Tables 9 and 10 include package-generated ePC-SAFT AAD values and paper-copied eNRTL/ePC-SAFT reference values for comparison.
- The package model evidence is non-reactive electrolyte LLE through the internal electrolyte LLE component diagnostic with the `2026_Khudaida` Born SSM+DS dataset options.
- The current internal-validation regeneration is retained in `figures/figure_02` through `figure_07` under `results/data/model_tielines.csv`. The artifacts are complete, but the model-fit statistics do not pass the Khudaida source-data reproduction criteria.
