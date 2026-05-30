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
| [#186](issues/0186-harden-gfpe-pretreatment-and-selector-admission-pipeline.md) | `lle` | `Ipopt` | `ready` | Harden GFPE pretreatment and selector admission before later NLP work. |
| [#187](issues/0187-harden-shared-nlp-and-ipopt-infrastructure-gate.md) | `lle` | `Ipopt` | `blocked` | Build shared NLP and Ipopt infrastructure after #186. |
| [#188](issues/0188-prove-source-backed-neutral-tp-flash-gfpe-fixture-after-held-gate.md) | `lle` | `Ipopt` | `blocked` | Prove a source-backed neutral TP-flash GFPE fixture after #148 and #187. |
| [#189](issues/0189-derive-boundary-workflows-and-generalized-phase-set-pe-from-neutral-gfpe.md) | `lle` | `Ipopt` | `blocked` | Derive boundary workflows and generalized phase-set PE from #188. |
| [#190](issues/0190-admit-associating-gfpe-through-exact-derivative-proof-gates.md) | `lle` | `Ipopt` | `blocked` | Admit associating GFPE only through exact derivative proof gates after #145. |
| [#191](issues/0191-prove-electrolyte-gfpe-and-held2-validation-gates.md) | `electrolyte` | `Ipopt` | `blocked` | Prove electrolyte GFPE and HELD2.0 gates after #189. |
