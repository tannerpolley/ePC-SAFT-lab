# M4 - Equilibrium

epcsaft-equilibrium, GFPE, selector/admission, Ipopt NLP, HELD/TPD, phase
discovery, and VLE/LLE/electrolyte/reactive equilibrium workflows.

## Project Field Defaults

- Package: `equilibrium`
- Capability: `vle`, `lle`, `electrolyte`, or `reactive`
- Backend: usually `Ipopt`
- Release target: `equilibrium-0.x`

## Milestone Doctrine

| Document | Summary |
| --- | --- |
| [Generalized fluid-phase equilibrium](generalized-fluid-phase-equilibrium.md) | M4 GFPE doctrine, mathematical contract, activation policy, and implementation gates. |

## Current Specs

| Spec | Capability | Summary |
| --- | --- | --- |
| [Single-component VLE route](../../specs/2026-06-04-m4-equilibrium-single-component-vle-route.md) | `vle` | Add production pure-component saturation solving to `epcsaft-equilibrium` using the modular Ipopt/NLP route discipline. |
| [HELD 1.0 full adoption](../../specs/2026-06-11-m4-equilibrium-held-1-0-full-adoption.md) | `vle`/`lle` | Define the Pereira 2012-style HELD 1.0 adoption gates that must be finished before associating GFPE borrows the neutral algorithm path. |
| [HELD 1.0 fresh-native proof gate](../../specs/2026-06-11-m4-equilibrium-held-1-0-fresh-native-proof-gate.md) | `lle` | Require fresh native build receipts before HELD/GFPE validation artifacts can claim Stage II/III completion. |
| [Neutral nonassociating LLE source-backed showcase](../../specs/2026-06-11-m4-equilibrium-neutral-nonassociating-lle-source-backed-showcase.md) | `lle` | Add the first source-backed neutral nonassociating LLE fixture and showcase after the HELD proof lane is receipt-backed. |

## Current Plans

| Plan | Capability | Summary |
| --- | --- | --- |
| [Single-component VLE route plan](../../plans/2026-06-04-m4-equilibrium-single-component-vle-route-plan.md) | `vle` | Implement production pure-component saturation solving in `epcsaft-equilibrium` as an independent M4 route plan. |
| [Fresh-native HELD/GFPE validation receipts plan](../../plans/2026-06-12-m4-equilibrium-fresh-native-held-gfpe-validation-receipts-plan.md) | `lle` | Add receipt-backed validation evidence so stale native artifacts cannot misreport HELD Stage II/III status. |
| [Pereira-style HELD neutral LLE reliability plan](../../plans/2026-06-12-m4-equilibrium-pereira-held-neutral-lle-reliability-plan.md) | `lle` | Retains the full-campaign neutral LLE reliability gate before associating GFPE borrows the neutral HELD path. |
| [Neutral nonassociating LLE source-backed showcase plan](../../plans/2026-06-13-m4-equilibrium-neutral-nonassociating-lle-source-backed-showcase-plan.md) | `lle` | Adds the first source-backed neutral nonassociating LLE fixture, checker, retained figures, and registry evidence for the current `lle` utility route. |
| [Issue #189 generalized phase-set diagnostics plan](../../plans/2026-05-30-m4-equilibrium-issue-0189-derive-boundary-workflows-and-generalized-phase-set-pe-from-neutral-gfpe-plan.md) | `lle` | Splits #189 into an umbrella plus the first AFK child issue for internal neutral generalized phase-set diagnostics. |
| [Issue #189 boundary workflow trace plan](../../plans/2026-06-13-m4-equilibrium-issue-0189-boundary-workflow-trace-contracts-plan.md) | `lle` | Defines the next #189 child for retained bubble/dew boundary traces and stricter generalized phase-set rejection diagnostics after #252. |
| [Issue #189 cloud/shadow boundary gate plan](../../plans/2026-06-15-m4-equilibrium-issue-0189-cloud-shadow-boundary-gate-plan.md) | `lle` | Defines the next #189 child for a retained Matsuda/NIST cloud/shadow source-data gate without native route admission. |
| [Issue #189 native cloud/shadow isobaric route evidence plan](../../plans/2026-06-15-m4-equilibrium-issue-0189-native-cloud-shadow-isobaric-route-admission-plan.md) | `lle` | Defines the next #189 child for checker-gated native Matsuda/NIST isobaric cloud/shadow route evidence without public route-key exposure. |
| [Issue #189 generalized phase-set certification gate plan](../../plans/2026-06-15-m4-equilibrium-issue-0189-generalized-phase-set-certification-gate-plan.md) | `lle` | Defines the next #189 child after #260 for Stage II candidate-set replay and strict Stage III Ipopt refinement of the generalized neutral multiphase phase set. |

## Retained Evidence

| Evidence | Capability | Scope |
| --- | --- | --- |
| [HELD LLE reliability campaign](../../../../analyses/package_validation/held_lle_reliability/README.md) | `lle` | Synthetic neutral LLE algorithm reliability evidence: 100 accepted two-phase conditions, 10,000 independent route-refinement repeats, zero failed repeats. This is not source-backed public LLE showcase evidence, generalized phase-set completion, or associating GFPE admission. |
| [Neutral nonassociating LLE showcase](../../../../analyses/package_validation/neutral_nonassociating_lle_showcase/README.md) | `lle` | Source-backed Matsuda/NIST perfluorohexane + hexane LLE evidence for the current neutral `route="lle"` utility. This is one binary source-backed showcase, not generalized phase-set completion or associating GFPE admission. |
| `scripts/validation/check_generalized_phase_set.py --json --require-complete` | `lle` | Internal neutral generalized phase-set diagnostic record evidence for #252: three selected candidate rows, rejected candidate rows, mass-balance feasibility, noncollapsed selected compositions, and no public `neutral_multiphase_nonassoc` exposure. This keeps `PE-Generalized Multiphase` planned-not-public. |
| `scripts/validation/check_boundary_workflows.py --json --run-current-boundary-route --allow-route-sweep --route-point-count 1 --require-complete` | `lle` | Retained derived-boundary evidence for #256: current bubble/dew `P-x` and `T-x` route points emit complete `boundary_trace` records with route, DOF swap, source fixture, selector family, shared NLP families, strict Ipopt convergence, finite residuals, and no iteration-limit seed path. Cloud and shadow remain planned-only. |
| `scripts/validation/check_boundary_workflows.py --json --cloud-shadow-gate --require-cloud-shadow-gate` | `lle` | Retained cloud/shadow source-data gate for #258: 14 Matsuda/NIST cloud-point binodal rows, one paired cloud/shadow source branch, empty source-data blockers, and explicit native route-admission blockers. This is not native cloud/shadow route admission. |

## Current Open Issues

| Issue | Capability | Backend | Readiness | Summary |
| --- | --- | --- | --- | --- |
| [#145](../../issues/2026-05-23-m4-equilibrium-issue-0145-associating-neutral-lle-after-held-tpd-and-associating-vle-proofs.md) | `ready` | `Ipopt` | `blocked` | Associating neutral LLE after HELD/TPD and associating VLE proofs. |
| [#189](../../issues/2026-05-30-m4-equilibrium-issue-0189-derive-boundary-workflows-and-generalized-phase-set-pe-from-neutral-gfpe.md) | `lle` | `Ipopt` | `ready` | HITL umbrella for boundary workflows and generalized phase-set PE after #188/#241 closed. |
| [#260](../../issues/2026-06-15-m4-equilibrium-issue-0260-checker-gated-native-cloud-shadow-isobaric-route-evidence.md) | `lle` | `Ipopt` | `ready` | AFK child for checker-gated native Matsuda/NIST isobaric cloud/shadow route evidence without public route-key exposure. |
| [#261](../../issues/2026-06-15-m4-equilibrium-issue-0261-complete-generalized-phase-set-certification-gate.md) | `lle` | `Ipopt` | `blocked` | AFK child blocked by #260 for generalized phase-set certification with Stage II candidate-set replay and strict Stage III route refinement. |
| [#190](../../issues/2026-05-30-m4-equilibrium-issue-0190-admit-associating-gfpe-through-exact-derivative-proof-gates.md) | `lle` | `Ipopt` | `blocked` | Admit associating GFPE through exact derivative proof gates. |
| [#191](../../issues/2026-05-30-m4-equilibrium-issue-0191-prove-electrolyte-gfpe-and-held2-0-validation-gates.md) | `electrolyte` | `Ipopt` | `blocked` | Prove electrolyte GFPE and HELD2.0 validation gates. |

## Queue Guard

#247 closed through #249 on 2026-06-13 after the retained synthetic neutral LLE
HELD reliability campaign accepted 100 conditions, ran 10,000 route-refinement
repeats, and recorded zero failed repeats. That evidence supports neutral HELD
algorithm reliability only; it still does not replace source-backed public LLE
showcase evidence, generalized phase-set completion, or associating GFPE
admission.

#250 adds the first source-backed neutral nonassociating LLE showcase fixture:
Matsuda/NIST perfluorohexane + hexane paired binodal branch rows, Tihic-derived
pure parameters, a source-fitted binary interaction for the current route, a
checker requiring HELD Stage II replay plus Stage III replay consumption, and
retained PNG/SVG figures. This closes the public source-backed neutral LLE
showcase gap only.

#252 closed through #255 with internal neutral generalized phase-set diagnostic
records and the retained `check_generalized_phase_set.py` checker. This keeps
`PE-Generalized Multiphase` planned-not-public and does not close #189.

#256 closed through #257 with retained boundary traces for current bubble/dew
route points and tighter generalized phase-set rejected-candidate diagnostics.
This preserves the public capability boundary and does not close #189.

#258 closed through #259 with a retained cloud/shadow source-data gate from the
Matsuda/NIST perfluorohexane + hexane neutral LLE fixture. The gate keeps
cloud/shadow native runtime routes empty and does not close #189.

#260 is the next #189 AFK child. It targets one checker-gated native isobaric
cloud/shadow route-evidence point against the retained Matsuda/NIST paired
branch while keeping public cloud/shadow route keys closed.

#261 is created but blocked by #260. It is the next #189 child after #260 and
targets generalized phase-set certification: Stage II candidate-set replay plus
strict Stage III Ipopt refinement for requested neutral multiphase phase kinds,
while keeping `neutral_multiphase_nonassoc` public route exposure closed.

#189 is unblocked after #188 and #241 closed, but it remains the HITL umbrella
for boundary workflows and generalized phase-set PE. #190 and #191 remain
blocked by their own proof gates.

## Closed Issues

- [https://github.com/ePC-SAFT/ePC-SAFT/issues/228](https://github.com/ePC-SAFT/ePC-SAFT/issues/228) closed by [https://github.com/ePC-SAFT/ePC-SAFT/pull/230](https://github.com/ePC-SAFT/ePC-SAFT/pull/230) on 2026-06-05T02:56:36Z
- [https://github.com/ePC-SAFT/ePC-SAFT/issues/208](https://github.com/ePC-SAFT/ePC-SAFT/issues/208) closed by [https://github.com/ePC-SAFT/ePC-SAFT/pull/238](https://github.com/ePC-SAFT/ePC-SAFT/pull/238) on 2026-06-10T22:22:15Z
- [https://github.com/ePC-SAFT/ePC-SAFT/issues/186](https://github.com/ePC-SAFT/ePC-SAFT/issues/186) closed by [https://github.com/ePC-SAFT/ePC-SAFT/pull/239](https://github.com/ePC-SAFT/ePC-SAFT/pull/239) on 2026-06-10T23:07:32Z
- [https://github.com/ePC-SAFT/ePC-SAFT/issues/148](https://github.com/ePC-SAFT/ePC-SAFT/issues/148) closed by [https://github.com/ePC-SAFT/ePC-SAFT/pull/240](https://github.com/ePC-SAFT/ePC-SAFT/pull/240) on 2026-06-11T00:02:53Z
- [https://github.com/ePC-SAFT/ePC-SAFT/issues/187](https://github.com/ePC-SAFT/ePC-SAFT/issues/187) closed by [https://github.com/ePC-SAFT/ePC-SAFT/pull/242](https://github.com/ePC-SAFT/ePC-SAFT/pull/242) on 2026-06-11T16:28:05Z
- [https://github.com/ePC-SAFT/ePC-SAFT/issues/241](https://github.com/ePC-SAFT/ePC-SAFT/issues/241) closed by [https://github.com/ePC-SAFT/ePC-SAFT/pull/244](https://github.com/ePC-SAFT/ePC-SAFT/pull/244) on 2026-06-11T22:02:56Z
- [https://github.com/ePC-SAFT/ePC-SAFT/issues/188](https://github.com/ePC-SAFT/ePC-SAFT/issues/188) closed by [https://github.com/ePC-SAFT/ePC-SAFT/pull/245](https://github.com/ePC-SAFT/ePC-SAFT/pull/245) on 2026-06-11T23:16:41Z
- [https://github.com/ePC-SAFT/ePC-SAFT/issues/246](https://github.com/ePC-SAFT/ePC-SAFT/issues/246) closed by [https://github.com/ePC-SAFT/ePC-SAFT/pull/248](https://github.com/ePC-SAFT/ePC-SAFT/pull/248) on 2026-06-12T19:00:55Z
- [https://github.com/ePC-SAFT/ePC-SAFT/issues/247](https://github.com/ePC-SAFT/ePC-SAFT/issues/247) closed by [https://github.com/ePC-SAFT/ePC-SAFT/pull/249](https://github.com/ePC-SAFT/ePC-SAFT/pull/249) on 2026-06-13T01:41:13Z
- [https://github.com/ePC-SAFT/ePC-SAFT/issues/250](https://github.com/ePC-SAFT/ePC-SAFT/issues/250) closed by [https://github.com/ePC-SAFT/ePC-SAFT/pull/251](https://github.com/ePC-SAFT/ePC-SAFT/pull/251) on 2026-06-13T06:01:01Z
- [https://github.com/ePC-SAFT/ePC-SAFT/issues/252](https://github.com/ePC-SAFT/ePC-SAFT/issues/252) closed by [https://github.com/ePC-SAFT/ePC-SAFT/pull/255](https://github.com/ePC-SAFT/ePC-SAFT/pull/255) on 2026-06-13T14:13:58Z
- [https://github.com/ePC-SAFT/ePC-SAFT/issues/256](https://github.com/ePC-SAFT/ePC-SAFT/issues/256) closed by [https://github.com/ePC-SAFT/ePC-SAFT/pull/257](https://github.com/ePC-SAFT/ePC-SAFT/pull/257) on 2026-06-15T17:23:27Z
- [https://github.com/ePC-SAFT/ePC-SAFT/issues/258](https://github.com/ePC-SAFT/ePC-SAFT/issues/258) closed by [https://github.com/ePC-SAFT/ePC-SAFT/pull/259](https://github.com/ePC-SAFT/ePC-SAFT/pull/259) on 2026-06-15T22:19:05Z
