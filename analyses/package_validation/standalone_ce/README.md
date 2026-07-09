# Standalone CE Validation Ladder

This package-validation analysis retains the evidence for the standalone homogeneous chemical-equilibrium workflow exposed through `reactive_speciation(...)`.

The ladder covers analytic ideal checks, charged conservation, Ascani-backed source rows, MEA speciation, Cantera comparisons, and Pope-style reference-oracle checks. It intentionally proves CE-only behavior: reactive LLE, reactive electrolyte LLE, and coupled phase-plus-chemistry equilibrium remain separate planned surfaces.

Run the retained gate from the repo root:

```bash
uv run --no-sync python scripts/validation/check_standalone_ce_gate.py --json --require-single-nlp-path --require-oracles --require-complete
```

Figure-owned artifacts live under `figures/<figure_id>/output`, while the package-level retained summary stays under `shared/results`.
