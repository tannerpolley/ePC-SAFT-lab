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
| [Adaptive branch tracing validation](../../specs/2026-06-24-m4-equilibrium-adaptive-branch-tracing-and-validation.md) | `association` | Add internal boundary-route branch tracing so accepted VLE paper-validation curves carry solved-anchor, segment-density, exact-Hessian, and postsolve proof. |

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
| [Issue #298 adaptive branch tracing validation plan](../../plans/2026-06-24-m4-equilibrium-adaptive-branch-tracing-validation-plan.md) | `association` | Adds the internal traced-boundary proof layer consumed by Gross 2002 Figure 2 and the full-replication checker. |
| [Issue #300 electrolyte HELD2 readiness and Born exactness gate plan](../../plans/2026-06-24-m4-equilibrium-issue-0300-electrolyte-held2-readiness-born-exactness-gate-plan.md) | `electrolyte` | Adds the next #191 child gate for reduced electroneutral variables, exact Born SSM/DS derivative receipts, and HELD2 readiness diagnostics. |
| [Issue #302 electrolyte charge-neutral TPD gate plan](../../plans/2026-06-24-m4-equilibrium-issue-0302-electrolyte-charge-neutral-tpd-gate-plan.md) | `electrolyte` | Adds the next #191 child gate for native-backed charge-neutral electrolyte TPD screening before full HELD2 dual discovery, Stage III refinement, postsolve certification, or public route admission. |
| [Issue #306 electrolyte HELD2 counterion-pair phase-discovery gate plan](../../plans/2026-06-25-m4-equilibrium-issue-0306-electrolyte-held2-counterion-pair-phase-discovery-gate-plan.md) | `electrolyte` | Closed #191 child gate for independent counterion-pair matrix construction, reduced electroneutral HELD2 phase-discovery diagnostics, and mean-ionic residual bookkeeping. |
| [Issue #312 electrolyte HELD2 Stage III refinement gate plan](../../plans/2026-06-25-m4-equilibrium-issue-0312-electrolyte-held2-stage-iii-refinement-gate-plan.md) | `electrolyte` | Closed #191 child gate for consuming the #306 candidate set in local reduced-variable Stage III electrolyte refinement while keeping postsolve certification and public admission separate. |
| [Issue #313 electrolyte postsolve phase-set certification gate plan](../../plans/2026-06-25-m4-equilibrium-issue-0313-electrolyte-postsolve-phase-set-certification-gate-plan.md) | `electrolyte` | Closed #191 child gate for explicit-ion reconstruction, charge, transfer, pressure, amount, and domain-margin certification after #312. |
| [Issue #314 electrolyte public route admission gate plan](../../plans/2026-06-25-m4-equilibrium-issue-0314-electrolyte-public-route-admission-gate-plan.md) | `electrolyte` | Adds the final #191 child gate for source-backed public electrolyte GFPE route admission after Stage III and postsolve certification close. |
| [Full HELD2 public-route phase discovery adoption plan](../../plans/2026-06-27-m4-equilibrium-held2-public-route-phase-discovery-full-adoption-plan.md) | `electrolyte` | Adds #343 through #350 for full HELD2-style public-route phase discovery: doctrine, continuous TPD, Stage I, Stage II, public route orchestration, scenario validation, and capability admission. |

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
| `scripts/validation/check_electrolyte_gfpe_gate.py --json --require-source-data --require-parameter-bundle --require-native-diagnostics --require-complete` | `electrolyte` | Source gate for #269: parses the Khudaida 2026 source fixture, records the raw paper-row closure correction before normalized explicit-ion expansion, constructs the path-based `2026_Khudaida` paper-validation parameter bundle, and runs native electrolyte and phase-charge diagnostics. |
| `scripts/validation/check_electrolyte_held2_readiness.py --json --require-source-gate --require-reduced-basis --require-born-ssm-ds --require-complete` | `electrolyte` | Prerequisite HELD2 readiness gate for #300: consumes the #269 Khudaida source gate, proves exact charge-neutral NaCl reduced amount lifting with residual <= `1.0e-10`, and records CppAD Born SSM/DS composition, ln-fugacity, activity-parameter, `d_born`, and `f_solv` derivative receipts. Electrolyte TPD screening is covered separately by #302. |
| `scripts/validation/check_electrolyte_tpd_gate.py --json --require-source-gate --require-held2-readiness --require-native-tpd --require-complete` | `electrolyte` | Charge-neutral electrolyte TPD screening gate for #302: consumes the #269 source gate and #300 readiness gate, calls native `_native_electrolyte_tpd_phase_discovery`, reports three finite source-backed candidates, selected candidate count `2`, minimum TPD `-0.010922388988229025`, and maximum charge residual `0.0`. This is screening evidence, not full HELD2 discovery, postsolve certification, or public route admission. |
| `scripts/validation/check_electrolyte_held2_phase_discovery.py --json --require-source-gate --require-readiness-gate --require-tpd-gate --require-native-held2-discovery --require-complete` | `electrolyte` | HELD2 counterion-pair phase-discovery gate for #306: consumes #269/#300/#302, calls native `_native_electrolyte_held2_phase_discovery`, proves full-rank `N_ch - 1` counterion-pair matrices for NaCl, Na/K/Cl, and K/Cl/Na/SO4 cases, reports charge-neutral lifted candidate diagnostics, finite reduced-TPD metrics, pair-based mean-ionic bookkeeping, and a Stage III handoff record. |
| `scripts/validation/check_electrolyte_stage_iii_refinement.py --json --require-source-gate --require-readiness-gate --require-tpd-gate --require-held2-discovery --require-native-stage-iii --require-complete` | `electrolyte` | Stage III refinement gate for #312: consumes #269/#300/#302/#306, calls native `_native_electrolyte_stage_iii_refinement`, records #306 candidate-set seed provenance, reduced counterion-pair residual variables/equations/scaling/bounds, exact reduced Jacobian/Hessian receipts, strict Ipopt success, and finite local phase compositions. |
| `scripts/validation/check_electrolyte_postsolve_certification.py --json --require-stage-iii --require-postsolve-certification --require-complete` | `electrolyte` | Postsolve phase-set certification gate for #313: consumes #312, calls native `_native_electrolyte_postsolve_certification`, and retains explicit-ion feed reconstruction, per-phase and total charge residuals, neutral and mean-ionic transfer residuals, pressure consistency, phase amounts, composition normalization, and domain margins. |
| `scripts/validation/check_electrolyte_public_admission.py --json --require-source-gate --require-readiness-gate --require-tpd-gate --require-held2-discovery --require-stage-iii --require-postsolve-certification --require-public-admission --require-complete` | `electrolyte` | Public electrolyte admission gate for #314: consumes #269/#300/#302/#306/#312/#313, proves `Equilibrium(..., route="electrolyte_lle")` maps to the source-backed Khudaida explicit-ion NaCl mixed-solvent LLE route, returns `liquid1` and `liquid2`, retains charge, pressure, transfer, phase-distance, exact reduced-derivative, and unsupported-surface evidence, and completes with no checker blockers. |
| `scripts/validation/check_associating_lle_gross_2002.py --json --require-source-data --require-exact-association-hessian --require-route-closed --require-complete` | `lle` | Internal exact-Hessian prerequisite proof for #145: retains Gross/Sadowski 2002 Figure 8 methanol/cyclohexane LLE branch rows, Table 1 methanol 2B association parameters, the retained cyclohexane PC-SAFT row, Table 2 `k_ij = 0.051`, verifies bounded site fractions, low mass-action residuals, exact association first/second sensitivities, objective/pressure/mass-action/Lagrangian Hessian symmetry, and certifies the source-backed internal two-liquid pair consumed by #190. |
| `scripts/validation/check_associating_gfpe_gate.py --json --require-source-data --require-public-admission --require-exact-association-hessian --require-complete` | `lle` | Public associating GFPE admission evidence for #190: consumes the #145 Gross/Sadowski 2002 proof, admits only `Equilibrium(..., route="lle")` for the source-backed methanol/cyclohexane two-phase neutral associating fixture, names `Gross2002 Figure8 methanol-cyclohexane`, `assoc_scheme=2B`, `k_ij=0.051`, and `cppad_implicit_association`, and keeps missing-proof, reactive, TP-flash, and generalized associating phase-set surfaces outside the admitted scope. |
| `scripts/validation/check_gross_2002_association_acceptance.py --json --require-complete --require-exact-association-hessian --require-fresh-native` | `association` | Gross/Sadowski 2002 paper-validation acceptance campaign for #275: retains Figure 1 pure-association AAD sanity evidence, connects Figure 8 methanol/cyclohexane source rows and exact-Hessian proof to campaign summaries, adds Figure 10 water/1-pentanol cross-association stress evidence with `k_ij = 0.016` and `cppad_implicit_association`, records Figures 2-7 and 9 as source-requirement records with no completion credit, and keeps electrolyte/reactive/generalized associating claims outside this evidence. |
| `scripts/validation/check_gross_2002_full_replication.py --json --require-foundation` | `association` | Gross/Sadowski 2002 full-replication foundation for #279: validates the Figure 1-10 manifest, required source/digitization artifact contract, score schema, source metadata schema, and planned blocker readout. This is not full figure replication until #280-#286 close. |
| `scripts/validation/check_gross_2002_full_replication.py --json --require-complete --require-exact-association-hessian --require-fresh-native --write-summary` | `association` | Gross/Sadowski 2002 complete full-replication proof with #298 Figure 2 branch tracing: all ten figures are accepted, Figure 2 records `requires_branch_trace`, the retained trace summary proves complete `bubble_line` and `dew_line` traces, exact Hessian and postsolve receipts, max coordinate gaps of `0.06851` and `0.07000`, and no checker blockers. |

## Current Open Issues

Open M4 work is split into phase-equilibrium/HELD2 and CE/CPE lanes so
standalone chemical-equilibrium work stays visible without being treated as
part of the HELD2 phase-discovery cutover.

### Phase-Equilibrium / HELD2 Open Issues

| Issue | Capability | Backend | Readiness | Summary |
| --- | --- | --- | --- | --- |
| [#191](../../issues/2026-05-30-m4-equilibrium-issue-0191-prove-electrolyte-gfpe-and-held2-0-validation-gates.md) | `electrolyte` | `Ipopt` | `blocked_by_320_343` | Umbrella closeout remains open. #314 is retained representative public-route admission evidence only; #191 cannot close until #320 proves Perdomo/Figiel HELD2 validation and #343 proves full HELD2-style public-route discovery through the remaining #346-#350 runtime and admission slices. |
| [#320](../../issues/2026-06-26-m4-equilibrium-issue-0320-khudaida-electrolyte-lle-held2-flash-validation.md) | `electrolyte` | `Ipopt` | `ready` | Active #191 validation blocker for Perdomo/Figiel HELD2 electrolyte flash evidence through the public package route. |
| [#343](../../issues/2026-06-27-m4-equilibrium-issue-0343-implement-full-held2-style-electrolyte-phase-discovery-in-the-public-route.md) | `electrolyte` | `Ipopt` | `blocked_by_346_347_348_349_350` | Full HELD2-style public-route phase-discovery adoption tracker. |
| [#346](../../issues/2026-06-27-m4-equilibrium-issue-0346-add-held2-stage-i-electrolyte-stability-certificate.md) | `electrolyte` | `Ipopt` | `ready` | Adds the HELD2 Stage I electrolyte stability certificate. |
| [#347](../../issues/2026-06-27-m4-equilibrium-issue-0347-implement-held2-stage-ii-electrolyte-dual-phase-discovery.md) | `electrolyte` | `Ipopt` | `ready` | Implements HELD2 Stage II dual/cutting-plane phase discovery. |
| [#348](../../issues/2026-06-27-m4-equilibrium-issue-0348-integrate-held2-discovery-into-electrolyte-public-route-orchestration.md) | `ready` | `Ipopt` | `blocked_by_347` | Integrates HELD2 discovery into the public electrolyte route before Stage III. |
| [#349](../../issues/2026-06-27-m4-equilibrium-issue-0349-add-held2-public-route-scenario-validation-ladder.md) | `ready` | `Ipopt` | `blocked_by_348` | Adds the public-route scenario validation ladder. |
| [#350](../../issues/2026-06-27-m4-equilibrium-issue-0350-admit-held2-public-route-capability-evidence-after-full-validation.md) | `electrolyte` | `Ipopt` | `blocked_by_349` | Admits registry and docs capability evidence only after full validation. |

### CE / CPE Open Issues

| Issue | Capability | Backend | Readiness | Summary |
| --- | --- | --- | --- | --- |
| [#321](../../issues/2026-06-26-m4-ce-issue-0321-m4-ce-standalone-chemical-speciation-equilibrium-foundation-before-cpe.md) | `ce` | `Ipopt` | `ready` | Standalone chemical/speciation equilibrium foundation before coupled CPE work. |
| [#328](../../issues/2026-06-26-m4-ce-issue-0328-m4-ce-design-standalone-speciation-public-api-and-result-schema.md) | `ce` | `Ipopt` | `ready` | Design the standalone CE public API and result schema. |
| [#329](../../issues/2026-06-26-m4-ce-issue-0329-m4-ce-build-standalone-validation-ladder.md) | `ce` | `Ipopt` | `ready` | Build the standalone CE validation ladder. |
| [#330](../../issues/2026-06-26-m4-ce-issue-0330-m4-ce-activate-standalone-ce-only-after-gates-pass.md) | `ce` | `Ipopt` | `blocked` | Activate standalone CE only after the CE foundation, API, and validation gates pass. |
| [#331](../../issues/2026-06-26-m4-ce-issue-0331-m4-cpe-define-simultaneous-phase-plus-chemistry-interface-contract.md) | `cpe` | `Ipopt` | `blocked` | Define the simultaneous phase-plus-chemistry interface contract after standalone CE is governed. |

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

#298 adds the internal adaptive boundary-route tracing layer consumed by Figure
2 validation. The retained Figure 2 proof now combines `single_component_vle`
for pure-limit endpoints with traced `bubble_pressure`/`dew_pressure` binary
branch anchors, writes the trace summary under shared Gross 2002 results, and
forces the full-replication checker to reject accepted Figure 2 records without
complete branch traces, exact-Hessian evidence, and postsolve evidence.

#269 closed through #270 with the first #191 child gate. Its retained checker
proves Khudaida source-data parsing, records the raw paper-row closure
correction before normalized explicit-ion expansion, verifies path-based
paper-validation parameter-bundle execution, and runs native
electrolyte/charge diagnostics. It is prerequisite evidence for electrolyte
TPD, HELD2 phase discovery, postsolve electrolyte phase-set certification, and
public electrolyte route admission.

#300 closed through #301 with the readiness gate needed before electrolyte
HELD2 implementation: exact reduced electroneutral amount lifting for the
Khudaida NaCl fixture, CppAD-backed Born SSM/DS derivative receipts, and a
retained HELD2 readiness payload. It keeps electrolyte TPD, HELD2 dual
discovery, Stage III electrolyte refinement, postsolve electrolyte phase-set
certification, and public electrolyte route admission closed.

#302 closes through #303 with the native-backed charge-neutral electrolyte TPD
screening child for #191. The retained checker consumes the #269 source gate and #300 readiness gate,
then reports three finite source-backed TPD candidates, selected candidate count
`2`, minimum TPD `-0.010922388988229025`, maximum charge residual `0.0`,
and readiness-only HELD2 status. The
negative TPD candidate is instability-screening evidence only; HELD2 dual
discovery, Stage III electrolyte refinement, postsolve electrolyte phase-set
certification, and public route admission remain pending.

#306 closed on 2026-06-25 with native independent counterion-pair matrix
construction, reduced electroneutral phase-discovery diagnostics,
charge-neutral candidate rows, pair-based mean-ionic residual bookkeeping, and
closed public route evidence. The retained checker consumes #269/#300/#302,
records charged species ordering, pair labels, counterion-pair matrix rank
`N_ch - 1`, transformed variable count, reduced lift/back-lift residuals,
finite TPD candidate metrics, and a Stage III handoff record. The proof covers
Na+/Cl-, Na+/K+/Cl-, and the multivalent K+/Cl-/Na+/SO4-- methodology example,
and rejects incomplete prerequisites, raw single-ion charged-transfer evidence,
and premature Stage III/postsolve/public-admission completion.

#312 closed with the retained Stage III reduced-variable electrolyte refinement gate
for #191. The checker consumes #269/#300/#302/#306, calls native
`_native_electrolyte_stage_iii_refinement`, records the #306 candidate-set seed
provenance, reports exact reduced counterion-pair Jacobian/Hessian receipts,
strict Ipopt success, finite local phase compositions, and keeps postsolve
certification plus public admission closed. #191 then moved to #313 for
postsolve certification.

#313 closes the electrolyte postsolve phase-set certification gate for #191.
The retained checker consumes #312, calls native
`_native_electrolyte_postsolve_certification`, reports `complete: true` with
`blockers: []`, explicit-ion feed reconstruction at retained tolerance,
per-phase charge residuals `0.0`, total charge residual `0.0`, pressure
consistency norm `6.984919309616089e-10`, phase distance
`2.7722252287643023e-06` above the `1.0e-8` floor, positive phase amounts
with minimum amount `0.43529509750292383`, separate neutral and mean-ionic
transfer residual families, and domain-margin evidence.

#314 is retained representative public electrolyte GFPE admission evidence. It
consumes #269/#300/#302/#306/#312/#313 and exposes only the source-backed
Khudaida explicit-ion NaCl mixed-solvent `electrolyte_lle` route, but it is not
full electrolyte LLE model reproduction.

#320 remains a #191 validation blocker for Perdomo/Figiel HELD2 electrolyte
flash evidence through the public package route.

#343 is the explicit full HELD2 public-route discovery implementation blocker
for #191. Its remaining blockers are #346 through #350 after #344 and #345
closed the doctrine and continuous reduced-electroneutral TPD substrate slices.
The remaining work covers Stage I stability certification, Stage II
dual/cutting-plane discovery, public route orchestration, scenario validation,
and registry/capability admission.

#145 closed through #273 with its internal exact-Hessian proof gate:
Gross/Sadowski 2002 Figure 8 methanol/cyclohexane LLE rows plus retained Table
1/Table 2 parameters pass `check_associating_lle_gross_2002.py
--require-source-data --require-exact-association-hessian --require-route-closed
--require-complete`. The proof stays the internal prerequisite receipt consumed
by #190.

#190 public admission evidence is now the retained
`check_associating_gfpe_gate.py --require-source-data
--require-public-admission --require-exact-association-hessian
--require-complete` gate. It admits only the source-backed Gross/Sadowski 2002
methanol/cyclohexane two-phase neutral LLE
configuration with `assoc_scheme=2B`, `k_ij=0.051`, and
`cppad_implicit_association`; missing-proof, ionic/electrolyte, reactive,
TP-flash, and generalized associating phase-set inputs remain outside that
associating admission. #190 does not claim electrolyte, reactive, LLLE,
two-associating-component, or generalized associating phase-set support.

## Closed Issues

- [https://github.com/ePC-SAFT/ePC-SAFT/issues/345](https://github.com/ePC-SAFT/ePC-SAFT/issues/345) closed by [https://github.com/ePC-SAFT/ePC-SAFT/pull/353](https://github.com/ePC-SAFT/ePC-SAFT/pull/353) on 2026-06-28T15:35:44Z
- [https://github.com/ePC-SAFT/ePC-SAFT/issues/344](https://github.com/ePC-SAFT/ePC-SAFT/issues/344) closed by [https://github.com/ePC-SAFT/ePC-SAFT/pull/352](https://github.com/ePC-SAFT/ePC-SAFT/pull/352) on 2026-06-28T04:20:05Z
- [https://github.com/ePC-SAFT/ePC-SAFT/issues/327](https://github.com/ePC-SAFT/ePC-SAFT/issues/327) closed by [https://github.com/ePC-SAFT/ePC-SAFT/pull/342](https://github.com/ePC-SAFT/ePC-SAFT/pull/342) on 2026-06-27T20:23:44Z
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
