# Picard Stress Rescue Or Retire Decision

## Decision: `retire_picard`

This M8 stress lane compares the exact implicit association solve against the fixed Picard policy grid across the retained topology, density, temperature, strength, and composition matrix.

| Metric | Retained stress result |
| --- | ---: |
| Max association Helmholtz relative error | 0.0312131 |
| Max pressure proxy relative error | 0.0140576 |
| Max derivative relative error | 0.0723614 |
| Max Hessian relative error | 0.150709 |
| Minimum simulation speedup vs exact implicit | 2.63585 |

The decision is analysis-only evidence for issue 161 disposition and does not change provider, equilibrium, regression, benchmark, or public API behavior.
