# M4 Khudaida Figure Replication With Figiel Parameters

> Superseded for active figure execution by
> `docs/superpowers/specs/2026-07-02-m6-khudaida-paper-validation-with-figiel-parameters.md`.
> This M4 spec remains historical context for closed issue #405. Active
> Khudaida figure reproduction is M6 paper validation; M4 receives follow-up
> issues only for solver/API defects exposed by that validation.

## Purpose

Create a figure-by-figure M4 validation path for Khudaida 2026 using the
retained Figiel 2025 ePC-SAFT parameter snapshot. The issue set must test the
public equilibrium route and retained figure artifacts before treating
parameter regression as a blocker.

## Requirements

- Create one parent issue and one child issue per Khudaida figure folder:
  Figures 1-10, supporting Figure S2, and supporting Figure S3.
- Resolve the figures in dependency order so the next ready issue is
  unambiguous.
- Use `analyses/paper_validation/2025_figiel/parameters` as the parameter
  source of truth.
- Retain provenance if any local Khudaida parameter copy remains in the figure
  path.
- Require public package route evidence for model-comparable equilibrium rows.
- Require regenerated source/model CSVs, plots, fit statistics, and residual
  diagnostics for each accepted figure.
- Treat Figure 10 as a source/sigma-profile provenance figure rather than an
  HELD2 flash proof.

## Non-goals

- No M5 parameter fitting inside the M4 validation path.
- No private-native-only proof.
- No diagnostic-only success.
- No release or broad electrolyte capability claim from tracker creation alone.
