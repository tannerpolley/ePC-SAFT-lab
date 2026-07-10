# Rezaee 2025/2026 Source Evidence

This is a source-evidence-only lane for the Rezaee lithium-extraction papers.
It preserves the transcribed literature rows and basis diagnostics without
claiming a current package-model reproduction.

## Boundary

- Retained evidence: 26 supporting-information equilibrium rows, the reported
  extraction targets, and deterministic basis-inference diagnostics.
- Closed surface: the current package exposes no reactive-electrolyte
  equilibrium route.
- Excluded claim: provider-era equilibrium and regression calculations are not
  current package evidence and do not establish phase-model support.
- Source mismatch: the 2026 paper text mentions 36 equilibrium points, while
  the retained machine-readable supporting-information table contains 26.

## Command

Run from the repository root:

```bash
uv run --no-sync python analyses/paper_validation/2026_rezaee/scripts/run_all.py
```

The command regenerates only source-derived target and basis summaries. It
fails if the retained source-row counts no longer match their contract.

## Retained Outputs

- `shared/results/processed/rezaee_2025_extraction_target_summary.csv`
- `shared/results/processed/rezaee_2025_extraction_equilibrium_summary.csv`
- `shared/results/processed/rezaee_2026_section32_basis_inference_rows.csv`
- `shared/results/reaction_equilibrium/rezaee_2026_section32_basis_inference_summary.json`
- `shared/results/reaction_equilibrium/rezaee_2026_section32_basis_inference.md`
- `shared/results/reaction_equilibrium/summary.json`

The lane retains no current model-prediction plot because no supported package
route computes this reactive-electrolyte application. The summary therefore
reports `model_validation_complete: false`, `phase_models_supported: false`,
and `public_route_admitted: false`.
