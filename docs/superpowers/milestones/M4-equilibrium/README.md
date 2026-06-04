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
| [#148](../../issues/2026-05-24-m4-equilibrium-issue-0148-implement-held-style-neutral-phase-discovery-and-tpd-certification-for-activation-routes.md) | `lle` | `Ipopt` | `ready` | Implement HELD-style neutral phase discovery and TPD certification for activation routes. |
| [#186](../../issues/2026-05-30-m4-equilibrium-issue-0186-harden-gfpe-pretreatment-and-selector-admission-pipeline.md) | `lle` | `Ipopt` | `ready` | Harden GFPE pretreatment and selector admission pipeline. |
| [#187](../../issues/2026-05-30-m4-equilibrium-issue-0187-harden-shared-nlp-and-ipopt-infrastructure-gate.md) | `lle` | `Ipopt` | `blocked` | Harden shared NLP and Ipopt infrastructure gate. |
| [#188](../../issues/2026-05-30-m4-equilibrium-issue-0188-prove-source-backed-neutral-tp-flash-gfpe-fixture-after-held-gate.md) | `lle` | `Ipopt` | `blocked` | Prove source-backed neutral TP-flash GFPE fixture after HELD gate. |
| [#189](../../issues/2026-05-30-m4-equilibrium-issue-0189-derive-boundary-workflows-and-generalized-phase-set-pe-from-neutral-gfpe.md) | `lle` | `Ipopt` | `blocked` | Derive boundary workflows and generalized phase-set PE from neutral GFPE. |
| [#190](../../issues/2026-05-30-m4-equilibrium-issue-0190-admit-associating-gfpe-through-exact-derivative-proof-gates.md) | `lle` | `Ipopt` | `blocked` | Admit associating GFPE through exact derivative proof gates. |
| [#191](../../issues/2026-05-30-m4-equilibrium-issue-0191-prove-electrolyte-gfpe-and-held2-0-validation-gates.md) | `electrolyte` | `Ipopt` | `blocked` | Prove electrolyte GFPE and HELD2.0 validation gates. |
| [#208](../../issues/2026-06-01-m4-equilibrium-issue-0208-move-equilibrium-objective-assembly-onto-provider-derivative-bundles.md) | `derivatives` | `CppAD` | `blocked` | Move equilibrium objective assembly onto provider derivative bundles. |
