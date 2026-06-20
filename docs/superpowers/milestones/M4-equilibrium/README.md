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
| [Gross 2002 association acceptance pass](../../specs/2026-06-18-m4-equilibrium-gross-2002-association-acceptance-pass.md) | `association` | Add a paper-validation acceptance campaign under `analyses/paper_validation/2002_gross`, with all relevant Gross/Sadowski figures and hard phase-split gates for Figures 8 and 10. |
| [Gross 2002 full figure replication](../../specs/2026-06-19-m4-equilibrium-gross-2002-full-figure-replication.md) | `association` | Require source-backed or digitized curve-level replication of Gross/Sadowski 2002 Figures 1-10, retained scorecards, and a strict full-replication checker before electrolyte work resumes. |

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
| [Issue #189 strict multiphase fugacity-residual refinement plan](../../plans/2026-06-16-m4-equilibrium-issue-0189-strict-multiphase-fugacity-residual-refinement-plan.md) | `lle` | Defines #263: exact reduced fugacity-residual Stage III refinement for the generalized neutral multiphase candidate-set replay before #261 resumes. |
| [Issue #189 generalized neutral multiphase admission plan](../../plans/2026-06-16-m4-equilibrium-issue-0189-generalized-neutral-multiphase-admission-plan.md) | `lle` | Defines #264: public `Equilibrium(..., route="multiphase", phase_kinds=[...]).solve()` admission for the certified neutral generalized multiphase phase set after #261 closed. |
| [Issue #279 Gross 2002 full-replication foundation plan](../../plans/2026-06-19-m4-equilibrium-issue-0279-gross-2002-full-replication-checker-scoring-schema-plan.md) | `association` | Defines the strict full-replication checker, source metadata schema, score schema, manifest contract, and foundation/complete gate split before figure-family replication issues execute. |
| [Pure 2B associating single-component VLE prerequisite plan](../../plans/2026-06-19-m4-equilibrium-pure-2b-associating-single-component-vle-prerequisite-plan.md) | `association` | Splits the native pure associating `single_component_vle` route admission out of Figure 1 replication so #280 can stay focused on paper-figure artifacts. |
| [Issue #281 Gross 2002 Figures 2-5 VLE replication plan](../../plans/2026-06-20-m4-equilibrium-issue-0281-gross-2002-figures-2-5-vle-curves-plan.md) | `association` | Defines the Figure 2 identity gate plus source/model/plot/score tasks for Gross 2002 Figures 2-5 while keeping native route gaps as separate prerequisites. |
| [Issue #282 Gross 2002 Figures 6-7 supercritical VLE replication plan](../../plans/2026-06-20-m4-equilibrium-issue-0282-gross-2002-figures-6-7-supercritical-vle-curves-plan.md) | `association` | Defines the Figure 6/7 source/model/plot/score tasks while forcing public-route gaps into separate prerequisites. |
| [Issue #292 associating GFPE VLE admission prerequisite plan](../../plans/2026-06-20-m4-equilibrium-associating-vle-gfpe-admission-prerequisite-plan.md) | `association` | Opens the source-backed neutral associating binary VLE admission needed before #281-#284 can generate Gross 2002 Figures 2-9 model curves. |

## Retained Evidence

| Evidence | Capability | Scope |
| --- | --- | --- |
| [HELD LLE reliability campaign](../../../../analyses/package_validation/held_lle_reliability/README.md) | `lle` | Synthetic neutral LLE algorithm reliability evidence: 100 accepted two-phase conditions, 10,000 independent route-refinement repeats, zero failed repeats. This is not source-backed public LLE showcase evidence, generalized phase-set completion, or associating GFPE admission. |
| [Neutral nonassociating LLE showcase](../../../../analyses/package_validation/neutral_nonassociating_lle_showcase/README.md) | `lle` | Source-backed Matsuda/NIST perfluorohexane + hexane LLE evidence for the current neutral `route="lle"` utility. This is one binary source-backed showcase, not generalized phase-set completion or associating GFPE admission. |
| `scripts/validation/check_generalized_phase_set.py --json --require-complete` | `lle` | Retained neutral generalized phase-set diagnostic record evidence for #252: three selected candidate rows, rejected candidate rows, mass-balance feasibility, and noncollapsed selected compositions. This is historical internal certification evidence, not the public-admission gate. |
| `scripts/validation/check_generalized_phase_set.py --json --phase-kinds liquid,liquid,liquid --run-route-refinement --require-route-refinement --require-complete` | `lle` | Generalized phase-set certification evidence for #261 using the #263 `strict_fugacity_residual` Stage III refinement: consumes the Stage II candidate-set replay, selects 3 of 6 candidates for requested `liquid,liquid,liquid`, reports exact reduced fugacity-residual derivative metadata, and accepts the postsolve with ln-fugacity consistency <= `1.0e-6`. |
| `scripts/validation/check_generalized_phase_set.py --json --phase-kinds liquid,liquid,liquid --run-route-refinement --require-route-refinement --require-public-admission --require-complete` | `lle` | Public generalized neutral multiphase admission evidence for #264: proves `Equilibrium(..., route="multiphase", phase_kinds=[...]).solve()` maps to `neutral_multiphase_nonassoc`, returns three named phases, reports exact Hessian evidence, accepts the postsolve, and completes with no checker blockers. |
| `scripts/validation/check_boundary_workflows.py --json --run-current-boundary-route --allow-route-sweep --route-point-count 1 --require-complete` | `lle` | Retained derived-boundary evidence for #256: current bubble/dew `P-x` and `T-x` route points emit complete `boundary_trace` records with route, DOF swap, source fixture, selector family, shared NLP families, strict Ipopt convergence, finite residuals, and no iteration-limit seed path. Cloud and shadow remain planned-only. |
| `scripts/validation/check_boundary_workflows.py --json --cloud-shadow-gate --require-cloud-shadow-gate` | `lle` | Retained cloud/shadow source-data gate for #258: 14 Matsuda/NIST cloud-point binodal rows, one paired cloud/shadow source branch, and empty source-data blockers. |
| `scripts/validation/check_boundary_workflows.py --json --run-cloud-shadow-route --require-cloud-shadow-route` | `lle` | Checker-gated native cloud/shadow route evidence for #260: derives the model-refined Matsuda branch pair from certified `neutral_lle`, fixes the parent branch in the private `neutral_cloud_t_eos` cloud-temperature route, solves with strict Ipopt, reports source/model parent and shadow errors, and keeps public cloud/shadow route admission closed. |
| `scripts/validation/check_electrolyte_gfpe_gate.py --json --require-source-data --require-parameter-bundle --require-native-diagnostics --require-public-routes-closed --require-complete` | `electrolyte` | Closed-admission source gate for #269: parses the Khudaida 2026 source fixture, records the raw paper-row closure correction before normalized explicit-ion expansion, constructs the path-based `2026_Khudaida` paper-validation parameter bundle, runs native electrolyte and phase-charge diagnostics, and keeps public electrolyte route admission closed. |
| `scripts/validation/check_associating_lle_gross_2002.py --json --require-source-data --require-exact-association-hessian --require-route-closed --require-complete` | `lle` | Internal exact-Hessian prerequisite proof for #145: retains Gross/Sadowski 2002 Figure 8 methanol/cyclohexane LLE branch rows, Table 1 methanol 2B association parameters, the retained cyclohexane PC-SAFT row, Table 2 `k_ij = 0.051`, verifies bounded site fractions, low mass-action residuals, exact association first/second sensitivities, objective/pressure/mass-action/Lagrangian Hessian symmetry, and certifies the source-backed internal two-liquid pair consumed by #190. |
| `scripts/validation/check_associating_gfpe_gate.py --json --require-source-data --require-public-admission --require-exact-association-hessian --require-electrolyte-closed --require-complete` | `lle` | Public associating GFPE admission evidence for #190: consumes the #145 Gross/Sadowski 2002 proof, admits only `Equilibrium(..., route="lle")` for the source-backed methanol/cyclohexane two-phase neutral associating fixture, names `Gross2002 Figure8 methanol-cyclohexane`, `assoc_scheme=2B`, `k_ij=0.051`, and `cppad_implicit_association`, and keeps missing-proof, ionic/electrolyte, reactive, TP-flash, and generalized associating phase-set surfaces closed. |
| `scripts/validation/check_gross_2002_association_acceptance.py --json --require-complete --require-exact-association-hessian --require-fresh-native` | `association` | Gross/Sadowski 2002 paper-validation acceptance campaign for #275: retains Figure 1 pure-association AAD sanity evidence, connects Figure 8 methanol/cyclohexane source rows and exact-Hessian proof to campaign summaries, adds Figure 10 water/1-pentanol cross-association stress evidence with `k_ij = 0.016` and `cppad_implicit_association`, records Figures 2-7 and 9 as source-requirement records with no completion credit, and keeps electrolyte/reactive/generalized associating claims outside this evidence. |
| `scripts/validation/check_gross_2002_full_replication.py --json --require-foundation` | `association` | Gross/Sadowski 2002 full-replication foundation for #279: validates the Figure 1-10 manifest, required source/digitization artifact contract, score schema, source metadata schema, and planned blocker readout. This is not full figure replication until #280-#286 close. |

## Current Open Issues

| Issue | Capability | Backend | Readiness | Summary |
| --- | --- | --- | --- | --- |
| [#292](../../issues/2026-06-20-m4-equilibrium-issue-0292-open-associating-gfpe-vle-admission-for-gross-2002-binaries.md) | `association` | `Ipopt` | `ready` | Open the source-backed associating binary VLE admission path needed before #281-#284 can generate model curves. |
| [#281](../../issues/2026-06-19-m4-equilibrium-issue-0281-fully-replicate-gross-2002-figures-2-5-self-associating-vle-curves.md) | `association` | `Ipopt` | `blocked` | Fully replicate Figures 2-5 self-associating VLE curves after #292 opens the required public VLE route admission. |
| [#282](../../issues/2026-06-19-m4-equilibrium-issue-0282-fully-replicate-gross-2002-figures-6-7-supercritical-partner-vle-curves.md) | `ready` | `Ipopt` | `blocked` | Fully replicate Figures 6-7 supercritical-partner VLE curves after #292 opens the required public VLE route admission. |
| [#283](../../issues/2026-06-19-m4-equilibrium-issue-0283-upgrade-gross-2002-figure-8-to-full-lle-vle-envelope-replication.md) | `ready` | `Ipopt` | `blocked` | Upgrade Figure 8 from hard-gate evidence to full LLE+VLE envelope replication after #292 opens the required VLE branch admission. |
| [#284](../../issues/2026-06-19-m4-equilibrium-issue-0284-fully-replicate-gross-2002-figure-9-cross-associating-vle-curve.md) | `ready` | `Ipopt` | `blocked` | Fully replicate Figure 9 cross-associating VLE curve after #292 opens the required public VLE route admission. |
| [#285](../../issues/2026-06-19-m4-equilibrium-issue-0285-upgrade-gross-2002-figure-10-to-full-vlle-lle-envelope-replication.md) | `ready` | `Ipopt` | `blocked` | Write a source plan and route-prerequisite audit before upgrading Figure 10 from stress evidence to full VLLE/LLE envelope replication. |
| [#286](../../issues/2026-06-19-m4-equilibrium-issue-0286-complete-gross-2002-full-figure-replication-campaign.md) | `ready` | `Ipopt` | `blocked` | Track full Gross 2002 Figure 1-10 completion after #280-#285 close. |
| [#191](../../issues/2026-05-30-m4-equilibrium-issue-0191-prove-electrolyte-gfpe-and-held2-0-validation-gates.md) | `electrolyte` | `Ipopt` | `blocked` | Prove electrolyte GFPE and HELD2.0 validation gates after #286 closes the full Gross 2002 replication campaign. |

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
records and the retained `check_generalized_phase_set.py` checker. This remains
historical record evidence and does not by itself close #189.

#256 closed through #257 with retained boundary traces for current bubble/dew
route points and tighter generalized phase-set rejected-candidate diagnostics.
This preserves the public capability boundary and does not close #189.

#258 closed through #259 with a retained cloud/shadow source-data gate from the
Matsuda/NIST perfluorohexane + hexane neutral LLE fixture. The gate keeps
cloud/shadow native runtime routes empty and does not close #189.

#260 closed through #262 with one checker-gated native isobaric cloud/shadow route-evidence
point. The proof derives the current model-refined Matsuda branch pair from the
certified neutral LLE source showcase, solves the private cloud-temperature
route from that parent branch, compares back to the raw source-pair tolerances,
and keeps public cloud/shadow route keys closed.

#263 closed through #265 with the strict reduced fugacity-residual Stage III
route for the generalized neutral multiphase candidate-set replay. Its checker
proof requires exact residual derivative metadata, accepted postsolve, Stage II
replay consumption, and no Gibbs-objective-only certification shortcut.

#261 closed through #266 with generalized phase-set certification proof. The
retained checker reports `complete: true`, `blockers: []`,
`selected_candidate_count: 3`, `rejected_candidate_count: 3`, strict Stage III
replay consumption of `held_stage_ii_dual_loop_candidate_set`, exact residual
Jacobian/Hessian evidence, and accepted postsolve. This closes the internal
certification child only; final public generalized multiphase admission remains
separate under #189.

#264 closed through #268 with public neutral generalized multiphase admission.
The retained public-admission checker reports `complete: true`, `blockers: []`,
public route `multiphase`, selector family `neutral_multiphase_nonassoc`, exact
Jacobian/Hessian evidence, accepted postsolve, and positive three-phase
fractions for the requested `liquid,liquid,liquid` phase-kind list.

#189 closed through #268 after the final public neutral generalized multiphase
admission child merged.

#275 closed through #278 with the strengthened Gross/Sadowski 2002
paper-validation association acceptance campaign under
`analyses/paper_validation/2002_gross`. The retained
checker accepts Figure 1 pure-association sanity evidence, Figure 8
methanol/cyclohexane source-backed exact-Hessian evidence, and Figure 10
water/1-pentanol cross-association stress evidence. Figures 2-7 and 9 remain
manifest-scoped source requirements with no completion credit until their
source points and provenance are retained. The campaign removes the first
association-confidence blocker for #191, but #286 now adds the full
Gross/Sadowski 2002 Figure 1-10 replication gate before electrolyte resumes. It
does not admit electrolyte, reactive, LLLE, or generalized associating phase
sets.

#279 closed through #288 with the strict full-replication checker,
source/digitization artifact schema, scoring thresholds, manifest contract, and
retained summary format consumed by #280 through #286. The figure-family issues
#280 through #285 are now ready and share one proof oracle and one plot-match
scoring contract.

#290 closed through #291 with the narrow pure 2B associating
`single_component_vle` prerequisite required by #280. The PR touched only
route/capability/test files, admits exactly one neutral associating component,
keeps binary associating/electrolyte/reactive/generalized surfaces closed, and
left Gross 2002 Figure 1 source/plot/score artifacts for #280.

#269 closed through #270 with the first #191 child gate. Its retained checker
proves Khudaida source-data parsing, records the raw paper-row closure
correction before normalized explicit-ion expansion, verifies path-based
paper-validation parameter-bundle execution, runs native electrolyte/charge
diagnostics, and keeps public electrolyte route state closed. It still leaves
electrolyte TPD, HELD2 phase discovery, postsolve electrolyte phase-set
certification, and public electrolyte route admission pending.

#145 closed through #273 with its internal exact-Hessian proof gate:
Gross/Sadowski 2002 Figure 8 methanol/cyclohexane LLE rows plus retained Table
1/Table 2 parameters pass `check_associating_lle_gross_2002.py
--require-source-data --require-exact-association-hessian --require-route-closed
--require-complete`. The proof stays the internal prerequisite receipt consumed
by #190.

#190 public admission evidence is now the retained
`check_associating_gfpe_gate.py --require-source-data
--require-public-admission --require-exact-association-hessian
--require-electrolyte-closed --require-complete` gate. It admits only the
source-backed Gross/Sadowski 2002 methanol/cyclohexane two-phase neutral LLE
configuration with `assoc_scheme=2B`, `k_ij=0.051`, and
`cppad_implicit_association`; missing-proof, ionic/electrolyte, reactive,
TP-flash, and generalized associating phase-set surfaces remain closed. This
clears the narrow associating public-admission blocker, but #275 now adds the
stronger Gross 2002 paper-validation acceptance pass before #191 electrolyte
work resumes. #190 does not claim electrolyte, reactive, LLLE,
two-associating-component, or generalized associating phase-set support.

## Closed Issues

- [https://github.com/ePC-SAFT/ePC-SAFT/issues/280](https://github.com/ePC-SAFT/ePC-SAFT/issues/280) closed by [https://github.com/ePC-SAFT/ePC-SAFT/pull/289](https://github.com/ePC-SAFT/ePC-SAFT/pull/289) on 2026-06-20T00:15:28Z
- [https://github.com/ePC-SAFT/ePC-SAFT/issues/290](https://github.com/ePC-SAFT/ePC-SAFT/issues/290) closed by [https://github.com/ePC-SAFT/ePC-SAFT/pull/291](https://github.com/ePC-SAFT/ePC-SAFT/pull/291) on 2026-06-19T23:32:21Z
- [https://github.com/ePC-SAFT/ePC-SAFT/issues/279](https://github.com/ePC-SAFT/ePC-SAFT/issues/279) closed by [https://github.com/ePC-SAFT/ePC-SAFT/pull/288](https://github.com/ePC-SAFT/ePC-SAFT/pull/288) on 2026-06-19T20:03:07Z
- [https://github.com/ePC-SAFT/ePC-SAFT/issues/145](https://github.com/ePC-SAFT/ePC-SAFT/issues/145) closed by [https://github.com/ePC-SAFT/ePC-SAFT/pull/273](https://github.com/ePC-SAFT/ePC-SAFT/pull/273) on 2026-06-18T07:35:51Z
- [https://github.com/ePC-SAFT/ePC-SAFT/issues/275](https://github.com/ePC-SAFT/ePC-SAFT/issues/275) closed by [https://github.com/ePC-SAFT/ePC-SAFT/pull/278](https://github.com/ePC-SAFT/ePC-SAFT/pull/278) on 2026-06-19T07:09:38Z
- [https://github.com/ePC-SAFT/ePC-SAFT/issues/269](https://github.com/ePC-SAFT/ePC-SAFT/issues/269) closed by [https://github.com/ePC-SAFT/ePC-SAFT/pull/270](https://github.com/ePC-SAFT/ePC-SAFT/pull/270) on 2026-06-18T00:45:16Z
- [https://github.com/ePC-SAFT/ePC-SAFT/issues/228](https://github.com/ePC-SAFT/ePC-SAFT/issues/228) closed by [https://github.com/ePC-SAFT/ePC-SAFT/pull/230](https://github.com/ePC-SAFT/ePC-SAFT/pull/230) on 2026-06-05T02:56:36Z
- [https://github.com/ePC-SAFT/ePC-SAFT/issues/208](https://github.com/ePC-SAFT/ePC-SAFT/issues/208) closed by [https://github.com/ePC-SAFT/ePC-SAFT/pull/238](https://github.com/ePC-SAFT/ePC-SAFT/pull/238) on 2026-06-10T22:22:15Z
- [https://github.com/ePC-SAFT/ePC-SAFT/issues/264](https://github.com/ePC-SAFT/ePC-SAFT/issues/264) closed by [https://github.com/ePC-SAFT/ePC-SAFT/pull/268](https://github.com/ePC-SAFT/ePC-SAFT/pull/268) on 2026-06-17T13:15:47Z
- [https://github.com/ePC-SAFT/ePC-SAFT/issues/189](https://github.com/ePC-SAFT/ePC-SAFT/issues/189) closed by [https://github.com/ePC-SAFT/ePC-SAFT/pull/268](https://github.com/ePC-SAFT/ePC-SAFT/pull/268) on 2026-06-17T13:15:46Z
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
- [https://github.com/ePC-SAFT/ePC-SAFT/issues/260](https://github.com/ePC-SAFT/ePC-SAFT/issues/260) closed by [https://github.com/ePC-SAFT/ePC-SAFT/pull/262](https://github.com/ePC-SAFT/ePC-SAFT/pull/262) on 2026-06-16T12:53:23Z
- [https://github.com/ePC-SAFT/ePC-SAFT/issues/261](https://github.com/ePC-SAFT/ePC-SAFT/issues/261) closed by [https://github.com/ePC-SAFT/ePC-SAFT/pull/266](https://github.com/ePC-SAFT/ePC-SAFT/pull/266) on 2026-06-16T23:13:06Z
- [https://github.com/ePC-SAFT/ePC-SAFT/issues/263](https://github.com/ePC-SAFT/ePC-SAFT/issues/263) closed by [https://github.com/ePC-SAFT/ePC-SAFT/pull/265](https://github.com/ePC-SAFT/ePC-SAFT/pull/265) on 2026-06-16T22:04:22Z
