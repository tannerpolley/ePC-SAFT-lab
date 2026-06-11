# M4 - Equilibrium

epcsaft-equilibrium, GFPE, selector/admission, Ipopt NLP, HELD/TPD, phase
discovery, and VLE/LLE/electrolyte/reactive equilibrium workflows.

## Project Field Defaults

- Package: `equilibrium`
- Capability: `vle`, `lle`, `electrolyte`, or `reactive`
- Backend: usually `Ipopt`
- Release target: `equilibrium-0.x`

## Current Specs

| Spec | Capability | Summary |
| --- | --- | --- |
| [Single-component VLE route](../../specs/2026-06-04-m4-equilibrium-single-component-vle-route.md) | `vle` | Add production pure-component saturation solving to `epcsaft-equilibrium` using the modular Ipopt/NLP route discipline. |

## Current Plans

| Plan | Capability | Summary |
| --- | --- | --- |
| [Single-component VLE route plan](../../plans/2026-06-04-m4-equilibrium-single-component-vle-route-plan.md) | `vle` | Implement production pure-component saturation solving in `epcsaft-equilibrium` as an independent M4 route plan. |

## Current Open Issues

| Issue | Capability | Backend | Readiness | Summary |
| --- | --- | --- | --- | --- |
| [#145](../../issues/2026-05-23-m4-equilibrium-issue-0145-associating-neutral-lle-after-held-tpd-and-associating-vle-proofs.md) | `lle` | `Ipopt` | `blocked` | Associating neutral LLE after HELD/TPD and associating VLE proofs. |
| [#187](../../issues/2026-05-30-m4-equilibrium-issue-0187-harden-shared-nlp-and-ipopt-infrastructure-gate.md) | `lle` | `Ipopt` | `blocked` | Harden shared NLP and Ipopt infrastructure gate. |
| [#188](../../issues/2026-05-30-m4-equilibrium-issue-0188-prove-source-backed-neutral-tp-flash-gfpe-fixture-after-held-gate.md) | `lle` | `Ipopt` | `blocked` | Prove source-backed neutral TP-flash GFPE fixture after HELD gate. |
| [#189](../../issues/2026-05-30-m4-equilibrium-issue-0189-derive-boundary-workflows-and-generalized-phase-set-pe-from-neutral-gfpe.md) | `lle` | `Ipopt` | `blocked` | Derive boundary workflows and generalized phase-set PE from neutral GFPE. |
| [#190](../../issues/2026-05-30-m4-equilibrium-issue-0190-admit-associating-gfpe-through-exact-derivative-proof-gates.md) | `lle` | `Ipopt` | `blocked` | Admit associating GFPE through exact derivative proof gates. |
| [#191](../../issues/2026-05-30-m4-equilibrium-issue-0191-prove-electrolyte-gfpe-and-held2-0-validation-gates.md) | `electrolyte` | `Ipopt` | `blocked` | Prove electrolyte GFPE and HELD2.0 validation gates. |

## Closed Issues

- [https://github.com/ePC-SAFT/ePC-SAFT/issues/228](https://github.com/ePC-SAFT/ePC-SAFT/issues/228) closed by [https://github.com/ePC-SAFT/ePC-SAFT/pull/230](https://github.com/ePC-SAFT/ePC-SAFT/pull/230) on 2026-06-05T02:56:36Z
- [https://github.com/ePC-SAFT/ePC-SAFT/issues/208](https://github.com/ePC-SAFT/ePC-SAFT/issues/208) closed by [https://github.com/ePC-SAFT/ePC-SAFT/pull/238](https://github.com/ePC-SAFT/ePC-SAFT/pull/238) on 2026-06-10T22:22:15Z
- [https://github.com/ePC-SAFT/ePC-SAFT/issues/186](https://github.com/ePC-SAFT/ePC-SAFT/issues/186) closed by [https://github.com/ePC-SAFT/ePC-SAFT/pull/239](https://github.com/ePC-SAFT/ePC-SAFT/pull/239) on 2026-06-10T23:07:32Z
- [https://github.com/ePC-SAFT/ePC-SAFT/issues/148](https://github.com/ePC-SAFT/ePC-SAFT/issues/148) closed by [https://github.com/ePC-SAFT/ePC-SAFT/pull/240](https://github.com/ePC-SAFT/ePC-SAFT/pull/240) on 2026-06-11T00:02:53Z
