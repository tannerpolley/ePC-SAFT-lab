# M6 Khudaida Paper Validation With Figiel Parameters

## Purpose

Move the Khudaida 2026 figure-reproduction campaign into M6 validation while
preserving the M4/M5 split for defects found by the validation work.

The campaign validates retained literature artifacts, public-route evidence,
statistics, provenance, and tolerance decisions. It does not silently absorb
equilibrium solver implementation or parameter regression work.

## Issue Hierarchy

- #420: M6 paper validation campaign parent.
- #421: M6 Khudaida 2026 paper validation parent.
- #406-#417: Khudaida figure leaves under #421.

## Routing Rules

- M6 owns source/model artifact regeneration, retained plots, fit statistics,
  provenance, proof commands, and capability evidence.
- M4 owns equilibrium solver, public API, route admission, residual block, and
  Ipopt/certification defects exposed by validation.
- M5 owns parameter regression if fixed retained parameters cannot reproduce a
  figure within the accepted tolerance.
- A figure issue may close only with retained evidence or an exact blocker that
  points to the owning M4 or M5 issue.

## Requirements

- Keep Figiel 2025 parameters as the fixed source of truth for model-comparable
  Khudaida figures unless a separate M5 regression issue is opened.
- Retain the source-only classification for Figure 1 and Figure 10 where the
  paper figure does not support an ePC-SAFT model-fit claim.
- For model-comparable LLE figures, retain public package route diagnostics,
  residual summaries, row counts, tolerance basis, and exact failed rows.
- Keep local issue mirrors, source spec, source plan, and GitHub issue bodies
  aligned with the M6 validation hierarchy.

## Non-Goals

- No hidden parameter fitting inside M6 validation.
- No broad M4 equilibrium capability claim from a paper-validation issue alone.
- No private-native-only proof.
- No diagnostic-only success.
