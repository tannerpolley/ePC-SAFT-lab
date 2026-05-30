# M4 - Equilibrium

epcsaft-equilibrium, GFPE, selector/admission, Ipopt NLP, HELD/TPD, phase
discovery, and VLE/LLE/electrolyte/reactive equilibrium workflows.

## Project Field Defaults

- Package: `equilibrium`
- Capability: `vle`, `lle`, `electrolyte`, or `reactive`
- Backend: usually `Ipopt`
- Release target: `equilibrium-0.x`

## Current Open Issues

| Issue | Capability | Backend | Readiness | Summary |
| --- | --- | --- | --- | --- |
| [#145](issues/0145-associating-neutral-lle-after-held-tpd-and-associating-vle-proofs.md) | `lle` | `Ipopt` | `blocked` | Associating neutral LLE target; GitHub dependency marks it blocked by #148. |
| [#148](issues/0148-implement-held-style-neutral-phase-discovery-and-tpd-certification-for-activation-routes.md) | `lle` | `Ipopt` | `ready` | Implement HELD-style neutral phase discovery and TPD certification. |
