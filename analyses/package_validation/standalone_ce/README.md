# Standalone CE Validation Ladder

This package-validation analysis retains internal diagnostic evidence for the standalone homogeneous chemical-equilibrium formulation. It is not a public package route.

The ladder covers analytic ideal checks, charged conservation, Ascani-backed source rows, MEA speciation, Cantera comparisons, and Pope-style reference-oracle checks. The live MEA continuation currently fails final proof with `balance_inf_norm = 2.5999999998789356` and `reaction_stationarity_inf_norm = 73.79118023038392`. Re-admission requires both values to be no greater than `1.0e-8` and `1.0e-6`, respectively, with the strict checker complete. Reactive speciation, reactive LLE, reactive electrolyte LLE, and coupled phase-plus-chemistry equilibrium remain closed.

Run the retained gate from the repo root:

```bash
uv run --no-sync python scripts/validation/check_standalone_ce_gate.py --json --require-single-nlp-path --require-oracles --require-complete
```

Figure-owned artifacts live under `figures/<figure_id>/output`, while the package-level retained summary stays under `shared/results`.
