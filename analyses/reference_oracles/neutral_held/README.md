# Neutral HELD reference oracle

This directory contains a deliberately small, non-production reference oracle
for the neutral HELD Stage III direct-minimization topology. The canonical
mathematical formulation remains
[docs/latex/equilibrium_formulations.tex](../../../docs/latex/equilibrium_formulations.tex);
this README does not duplicate its equations.

The executable scope is a binary, fixed-pressure, one-mole manufactured
problem. A smooth triple-well composition energy creates:

- a stable single-phase case;
- a stable two-phase split;
- a stationary duplicate-phase state that is locally acceptable but
  metastable;
- explicit invalid-input and infeasible-start failures.

`oracle.py` defines a small phase-evaluator protocol, analytic manufactured
Helmholtz evaluator, exact material-balance parameterization, analytic
derivatives and KKT diagnostics, deterministic multistart local minimization,
and a separate composition/volume grid enumeration with objective-only local
refinement. The local result is accepted only when it agrees with enumeration
and passes balance, pressure, stationarity, common-tangent, and tangent-plane
checks. Enumeration supplies evidence for this bounded manufactured problem;
it is not a general global optimizer.

The isobaric formulation has no imposed total-volume balance. The oracle checks
positive bounded phase volumes and pressure stationarity, and reports total
volume from the phase-fraction-weighted phase-volume definition.

## Solver availability

The declared backend is `numpy_feasible_gradient`. Ipopt is not used because
repository policy does not permit its retired Python wrapper in this analysis
area. No alternative backend or silent fallback is present.

## Run

```bash
uv run --no-sync python run_pytest.py \
  analyses/reference_oracles/neutral_held/tests/test_oracle.py -q
```

## Limits

This oracle does not implement ePC-SAFT, does not validate physical or
literature predictions, and is not imported by
`packages/epcsaft-equilibrium`. It does not cover association, electrolytes,
HELD2, standalone chemical equilibrium, or coupled phase-and-chemical
equilibrium. A future ePC-SAFT adapter would need a traceable evaluator
contract, EOS-domain handling, derivative parity, and independent physical
validation before it could use this algorithm scaffold.
