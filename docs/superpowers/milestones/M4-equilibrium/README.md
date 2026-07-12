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
| [Generalized fluid-phase equilibrium](generalized-fluid-phase-equilibrium.md) | Short package-architecture authority, current route boundary, and links to source-faithful algorithm doctrine. |
| [Pereira HELD](algorithms/neutral-held.md) | Three-stage neutral molecular HELD identity, direct free-energy Stage III, and package status. |
| [Perdomo HELD2](algorithms/strong-electrolyte-held2.md) | Strong-electrolyte modified-mole formulation, staged controller, and independent modified-potential conditions. |
| [Ascani electrolyte equilibrium](algorithms/ascani-electrolyte-equilibrium.md) | Independent counterion-pair coordinates, mean-ionic conditions, and successive phase addition. |
| [Chemical and coupled equilibrium](algorithms/chemical-and-coupled-equilibrium.md) | Separate standalone CE and simultaneous CPE problem families. |

## Current Specs

| Spec | Capability | Summary |
| --- | --- | --- |
| [Single-component VLE route](../../specs/2026-06-04-m4-equilibrium-single-component-vle-route.md) | `vle` | Add production pure-component saturation solving to `epcsaft-equilibrium` using the modular Ipopt/NLP route discipline. |
| [Historical HELD 1.0 adoption spec](../../specs/2026-06-11-m4-equilibrium-held-1-0-full-adoption.md) | `vle`/`lle` | Retains adoption-gap history; the Stage 1 doctrine supersedes replay-as-dual-loop, local refinement as canonical Stage III, and boundary routes inheriting HELD status. |
| [Historical fresh-native receipt gate](../../specs/2026-06-11-m4-equilibrium-held-1-0-fresh-native-proof-gate.md) | `lle` | Retains native-freshness requirements without treating sampled replay or current-route refinement as completed Pereira stages. |
| [Historical neutral LLE showcase](../../specs/2026-06-11-m4-equilibrium-neutral-nonassociating-lle-source-backed-showcase.md) | `lle` | Retains the source fixture and model comparison as internal evidence, not HELD parity or public LLE admission. |
| [Gross 2002 association acceptance pass](../../specs/2026-06-18-m4-equilibrium-gross-2002-association-acceptance-pass.md) | `association` | Add a paper-validation acceptance campaign under `analyses/paper_validation/2002_gross`, with all relevant Gross/Sadowski figures and hard phase-split gates for Figures 8 and 10. |
| [Gross 2002 full figure replication](../../specs/2026-06-19-m4-equilibrium-gross-2002-full-figure-replication.md) | `association` | Require source-backed or digitized curve-level replication of Gross/Sadowski 2002 Figures 1-10, retained scorecards, and a strict full-replication checker before electrolyte work resumes. |
| [Adaptive branch tracing validation](../../specs/2026-06-24-m4-equilibrium-adaptive-branch-tracing-and-validation.md) | `association` | Add internal boundary-route branch tracing so accepted VLE paper-validation curves carry solved-anchor, segment-density, exact-Hessian, and postsolve proof. |
| [Phase-equilibrium unified certification contract](../../specs/2026-06-29-m4-phase-equilibrium-unified-certification-contract.md) | `lle`/`vle`/`electrolyte`/`reactive` | Defines one enforceable production-route certification lifecycle with family-specific residual blocks, detailed LLE subtrees, and native GitHub sub-issue hierarchy under #361. |
| [Standalone CE diagnostic repair and admission](../../specs/2026-07-10-m4-standalone-ce-diagnostic-repair-and-admission.md) | `reactive` | Separates typed request/receipt completion, independent component checking, source-qualified evidence, classification, and final admission. |
| [Canonical-owner decomposition](../../specs/2026-07-10-m4-equilibrium-canonical-owner-decomposition.md) | `equilibrium` | Decomposes existing owners behind characterization and exact route/caller gates without changing behavior or capability state. |
| [Source-faithful equilibrium recovery and curated migration](../../specs/2026-07-12-m4-equilibrium-source-faithful-recovery-and-curated-migration.md) | `equilibrium` | Corrects HELD/HELD2 algorithm identity, preserves valuable local-NLP work, and defines the guarded twelve-stage path from doctrine through curated-repository migration. |

## Current Plans

| Plan | Capability | Summary |
| --- | --- | --- |
| [Source-faithful equilibrium recovery and curated migration program](../../plans/2026-07-12-m4-equilibrium-source-faithful-recovery-and-curated-migration-plan.md) | `equilibrium` | Coordinates twelve independently gated stages; future agents select one stage and approve its bounded child plan rather than executing the program as one branch. |
| [Single-component VLE route plan](../../plans/2026-06-04-m4-equilibrium-single-component-vle-route-plan.md) | `vle` | Implement production pure-component saturation solving in `epcsaft-equilibrium` as an independent M4 route plan. |
| [Fresh-native equilibrium validation receipts plan](../../plans/2026-06-12-m4-equilibrium-fresh-native-held-gfpe-validation-receipts-plan.md) | `lle` | Retains native-freshness receipts for sampled discovery and local refinement evidence without establishing HELD stage parity. |
| [Neutral LLE local-reliability plan](../../plans/2026-06-12-m4-equilibrium-pereira-held-neutral-lle-reliability-plan.md) | `lle` | Retains the synthetic local-refinement reliability campaign as component evidence, not a Pereira HELD proof. |
| [Neutral nonassociating LLE source-backed showcase plan](../../plans/2026-06-13-m4-equilibrium-neutral-nonassociating-lle-source-backed-showcase-plan.md) | `lle` | Historical plan for the first source-backed neutral nonassociating LLE fixture, checker, and retained figures. The evidence is now internal because the public `lle` route is closed. |
| [Issue #189 generalized phase-set diagnostics plan](../../plans/2026-05-30-m4-equilibrium-issue-0189-derive-boundary-workflows-and-generalized-phase-set-pe-from-neutral-gfpe-plan.md) | `lle` | Splits #189 into an umbrella plus the first AFK child issue for internal neutral generalized phase-set diagnostics. |
| [Issue #189 boundary workflow trace plan](../../plans/2026-06-13-m4-equilibrium-issue-0189-boundary-workflow-trace-contracts-plan.md) | `lle` | Defines the next #189 child for retained bubble/dew boundary traces and stricter generalized phase-set rejection diagnostics after #252. |
| [Issue #189 cloud/shadow boundary gate plan](../../plans/2026-06-15-m4-equilibrium-issue-0189-cloud-shadow-boundary-gate-plan.md) | `lle` | Defines the next #189 child for a retained Matsuda/NIST cloud/shadow source-data gate without native route admission. |
| [Issue #189 native cloud/shadow isobaric route evidence plan](../../plans/2026-06-15-m4-equilibrium-issue-0189-native-cloud-shadow-isobaric-route-admission-plan.md) | `lle` | Defines the next #189 child for checker-gated native Matsuda/NIST isobaric cloud/shadow route evidence without public route-key exposure. |
| [Issue #189 generalized phase-set certification gate plan](../../plans/2026-06-15-m4-equilibrium-issue-0189-generalized-phase-set-certification-gate-plan.md) | `lle` | Historical #189 child plan retained for the finite sampled-candidate replay and strict local Ipopt refinement. Its former global-certification interpretation is superseded. |
| [Issue #189 strict multiphase fugacity-residual refinement plan](../../plans/2026-06-16-m4-equilibrium-issue-0189-strict-multiphase-fugacity-residual-refinement-plan.md) | `lle` | Defines #263: exact reduced fugacity-residual local refinement for the generalized neutral multiphase sampled-candidate replay. |
| [Issue #189 generalized neutral multiphase admission plan](../../plans/2026-06-16-m4-equilibrium-issue-0189-generalized-neutral-multiphase-admission-plan.md) | `lle` | Historical #264 admission plan retained as internal implementation context. Its public claim is superseded until native-selector ownership and fresh evidence pass. |
| [Issue #279 Gross 2002 full-replication foundation plan](../../plans/2026-06-19-m4-equilibrium-issue-0279-gross-2002-full-replication-checker-scoring-schema-plan.md) | `association` | Defines the strict full-replication checker, source metadata schema, score schema, manifest contract, and foundation/complete gate split before figure-family replication issues execute. |
| [Pure 2B associating single-component VLE prerequisite plan](../../plans/2026-06-19-m4-equilibrium-pure-2b-associating-single-component-vle-prerequisite-plan.md) | `association` | Splits the native pure associating `single_component_vle` route admission out of Figure 1 replication so #280 can stay focused on paper-figure artifacts. |
| [Issue #281 Gross 2002 Figures 2-5 VLE replication plan](../../plans/2026-06-20-m4-equilibrium-issue-0281-gross-2002-figures-2-5-vle-curves-plan.md) | `association` | Defines the Figure 2 identity gate plus source/model/plot/score tasks for Gross 2002 Figures 2-5 while keeping native route gaps as separate prerequisites. |
| [Issue #282 Gross 2002 Figures 6-7 supercritical VLE replication plan](../../plans/2026-06-20-m4-equilibrium-issue-0282-gross-2002-figures-6-7-supercritical-vle-curves-plan.md) | `association` | Defines the Figure 6/7 source/model/plot/score tasks while forcing public-route gaps into separate prerequisites. |
| [Issue #292 associating GFPE VLE admission prerequisite plan](../../plans/2026-06-20-m4-equilibrium-associating-vle-gfpe-admission-prerequisite-plan.md) | `association` | Opens the source-backed neutral associating binary VLE admission needed before #281-#284 can generate Gross 2002 Figures 2-9 model curves. |
| [Issue #298 adaptive branch tracing validation plan](../../plans/2026-06-24-m4-equilibrium-adaptive-branch-tracing-validation-plan.md) | `association` | Adds the internal traced-boundary proof layer consumed by Gross 2002 Figure 2 and the full-replication checker. |
| [Issue #300 electrolyte HELD2 readiness and Born exactness gate plan](../../plans/2026-06-24-m4-equilibrium-issue-0300-electrolyte-held2-readiness-born-exactness-gate-plan.md) | `electrolyte` | Adds the next #191 child gate for reduced electroneutral variables, exact Born SSM/DS derivative receipts, and HELD2 readiness diagnostics. |
| [Issue #302 electrolyte charge-neutral TPD gate plan](../../plans/2026-06-24-m4-equilibrium-issue-0302-electrolyte-charge-neutral-tpd-gate-plan.md) | `electrolyte` | Adds the next #191 child gate for native-backed charge-neutral electrolyte TPD screening before full HELD2 dual discovery, Stage III refinement, postsolve certification, or public route admission. |
| [Issue #306 Ascani-family counterion-pair component plan](../../plans/2026-06-25-m4-equilibrium-issue-0306-electrolyte-held2-counterion-pair-phase-discovery-gate-plan.md) | `electrolyte` | Retains full-rank counterion-pair construction, charge-neutral candidate rows, and mean-ionic bookkeeping as Ascani-family component evidence. |
| [Issue #312 electrolyte local-refinement plan](../../plans/2026-06-25-m4-equilibrium-issue-0312-electrolyte-held2-stage-iii-refinement-gate-plan.md) | `electrolyte` | Retains the exact reduced-variable local equation solve as correction and diagnostic evidence, not canonical Perdomo Stage III. |
| [Issue #313 electrolyte postsolve phase-set certification gate plan](../../plans/2026-06-25-m4-equilibrium-issue-0313-electrolyte-postsolve-phase-set-certification-gate-plan.md) | `electrolyte` | Closed #191 child gate for explicit-ion reconstruction, charge, transfer, pressure, amount, and domain-margin certification after #312. |
| [Issue #314 electrolyte public route admission gate plan](../../plans/2026-06-25-m4-equilibrium-issue-0314-electrolyte-public-route-admission-gate-plan.md) | `electrolyte` | Historical admission work retained as an internal repair gate. The public route is closed until native-selector integration and renewed evidence pass together. |
| [Historical HELD2 public-route adoption plan](../../plans/2026-06-27-m4-equilibrium-held2-public-route-phase-discovery-full-adoption-plan.md) | `electrolyte` | Retains #343 through #350 component history; Perdomo modified-mole HELD2 requires a new source-faithful child design and public routes remain closed. |

## Retained Evidence

| Evidence | Capability | Scope |
| --- | --- | --- |
| [HELD LLE reliability campaign](../../../../analyses/package_validation/held_lle_reliability/README.md) | `lle` | Synthetic neutral LLE algorithm reliability evidence: 100 accepted two-phase conditions, 10,000 independent route-refinement repeats, zero failed repeats. This is not source-backed public LLE showcase evidence, generalized phase-set completion, or associating GFPE admission. |
| [Neutral nonassociating LLE showcase](../../../../analyses/package_validation/neutral_nonassociating_lle_showcase/README.md) | `lle` | Source-backed Matsuda/NIST perfluorohexane + hexane internal LLE sampled-candidate evidence. The public `lle` route is closed, and one binary showcase does not establish globally complete phase discovery. |
| `scripts/validation/check_generalized_phase_set.py --json --require-complete` | `lle` | Retained neutral generalized sampled-candidate audit for #252: three selected rows, rejected rows, mass-balance feasibility, and noncollapsed selected compositions. It explicitly leaves global phase-set completeness unproven and the public route closed. |
| `scripts/validation/check_generalized_phase_set.py --json --phase-kinds liquid,liquid,liquid --run-route-refinement --require-route-refinement --require-complete` | `lle` | Internal strict local refinement evidence for #261/#263: consumes the finite sampled-candidate replay, selects 3 of 6 candidates for requested `liquid,liquid,liquid`, reports exact reduced fugacity-residual derivative metadata, and accepts the local postsolve with ln-fugacity consistency <= `1.0e-6`. It does not certify global candidate completeness. |
| `scripts/validation/check_boundary_workflows.py --json --run-current-boundary-route --allow-route-sweep --route-point-count 1 --require-complete` | `lle` | Retained derived-boundary evidence for #256: current bubble/dew `P-x` and `T-x` route points emit complete `boundary_trace` records with route, DOF swap, source fixture, selector family, shared NLP families, strict Ipopt convergence, finite residuals, and no iteration-limit seed path. Cloud and shadow remain planned-only. |
| `scripts/validation/check_boundary_workflows.py --json --cloud-shadow-gate --require-cloud-shadow-gate` | `lle` | Retained cloud/shadow source-data gate for #258: 14 Matsuda/NIST cloud-point binodal rows, one paired cloud/shadow source branch, and empty source-data blockers. |
| `scripts/validation/check_boundary_workflows.py --json --run-cloud-shadow-route --require-cloud-shadow-route` | `lle` | Checker-gated native cloud/shadow route evidence for #260: derives the model-refined Matsuda branch pair from certified `neutral_lle`, fixes the parent branch in the private `neutral_cloud_t_eos` cloud-temperature route, solves with strict Ipopt, reports source/model parent and shadow errors, and keeps public cloud/shadow route admission closed. |
| `scripts/validation/check_electrolyte_gfpe_gate.py --json --require-source-data --require-parameter-bundle --require-native-diagnostics --require-complete` | `electrolyte` | Source gate for #269: parses the Khudaida 2026 source fixture, records the raw paper-row closure correction before normalized explicit-ion expansion, constructs the path-based `2026_Khudaida` paper-validation parameter bundle, and runs native electrolyte and phase-charge diagnostics. |
| `scripts/validation/check_electrolyte_held2_readiness.py --json --require-source-gate --require-reduced-basis --require-born-ssm-ds --require-complete` | `electrolyte` | Prerequisite HELD2 readiness gate for #300: consumes the #269 Khudaida source gate, proves exact charge-neutral NaCl reduced amount lifting with residual <= `1.0e-10`, and records CppAD Born SSM/DS composition, ln-fugacity, activity-parameter, `d_born`, and `f_solv` derivative receipts. Electrolyte TPD screening is covered separately by #302. |
| `scripts/validation/check_electrolyte_tpd_gate.py --json --require-source-gate --require-held2-readiness --require-native-tpd --require-complete` | `electrolyte` | Charge-neutral electrolyte TPD screening gate for #302: consumes the #269 source gate and #300 readiness gate, calls native `_native_electrolyte_tpd_phase_discovery`, reports three finite source-backed candidates, selected candidate count `2`, minimum TPD `-0.010922388988229025`, and maximum charge residual `0.0`. This is screening evidence, not full HELD2 discovery, postsolve certification, or public route admission. |
| `scripts/validation/check_electrolyte_held2_phase_discovery.py --json --require-source-gate --require-readiness-gate --require-tpd-gate --require-native-held2-discovery --require-complete` | `electrolyte` | Historical #306 checker: retains full-rank `N_ch - 1` counterion-pair matrices, charge-neutral candidate diagnostics, reduced-TPD metrics, and mean-ionic bookkeeping as Ascani-family component evidence. The checker name does not establish Perdomo HELD2 identity. |
| `scripts/validation/check_electrolyte_stage_iii_refinement.py --json --require-source-gate --require-readiness-gate --require-tpd-gate --require-held2-discovery --require-native-stage-iii --require-complete` | `electrolyte` | Historical #312 checker: retains candidate provenance, reduced counterion-pair residual variables, exact derivative receipts, strict Ipopt diagnostics, and finite local compositions as local correction evidence. It does not execute canonical Perdomo Stage III. |
| `scripts/validation/check_electrolyte_postsolve_certification.py --json --require-stage-iii --require-postsolve-certification --require-complete` | `electrolyte` | Postsolve phase-set certification gate for #313: consumes #312, calls native `_native_electrolyte_postsolve_certification`, and retains explicit-ion feed reconstruction, per-phase and total charge residuals, neutral and mean-ionic transfer residuals, pressure consistency, phase amounts, composition normalization, and domain margins. |
| `scripts/validation/check_electrolyte_public_admission.py --json --require-source-gate --require-readiness-gate --require-tpd-gate --require-held2-discovery --require-stage-iii --require-postsolve-certification --require-public-admission --require-complete` | `electrolyte` | Explicit re-admission repair gate for #314. It is expected to return nonzero while `electrolyte_lle` remains outside the public route map; prerequisite source, discovery, refinement, charge and postsolve evidence stays available for repair. |
| `scripts/validation/check_associating_lle_gross_2002.py --json --require-source-data --require-exact-association-hessian --require-route-closed --require-complete` | `lle` | Internal exact-Hessian prerequisite proof for #145: retains Gross/Sadowski 2002 Figure 8 methanol/cyclohexane LLE branch rows, Table 1 methanol 2B association parameters, the retained cyclohexane PC-SAFT row, Table 2 `k_ij = 0.051`, verifies bounded site fractions, low mass-action residuals, exact association first/second sensitivities, objective/pressure/mass-action/Lagrangian Hessian symmetry, and certifies the source-backed internal two-liquid pair consumed by #190. |
| `scripts/validation/check_associating_gfpe_gate.py --json --require-source-data --require-internal-evidence --require-route-closed --require-exact-association-hessian --require-complete` | `lle` | Internal associating GFPE component evidence for #190: consumes the #145 Gross/Sadowski 2002 proof for methanol/cyclohexane, records `assoc_scheme=2B`, `k_ij=0.051`, and `cppad_implicit_association`, and requires the public `lle` route to remain closed because global phase discovery is unproven. |
| `scripts/validation/check_gross_2002_association_acceptance.py --json --require-complete --require-exact-association-hessian --require-fresh-native` | `association` | Gross/Sadowski 2002 paper-validation acceptance campaign for #275: retains Figure 1 pure-association AAD sanity evidence, connects Figure 8 methanol/cyclohexane source rows and exact-Hessian proof to campaign summaries, adds Figure 10 water/1-pentanol cross-association stress evidence with `k_ij = 0.016` and `cppad_implicit_association`, records Figures 2-7 and 9 as source-requirement records with no completion credit, and keeps electrolyte/reactive/generalized associating claims outside this evidence. |
| `scripts/validation/check_gross_2002_full_replication.py --json --require-foundation` | `association` | Gross/Sadowski 2002 full-replication foundation for #279: validates the Figure 1-10 manifest, required source/digitization artifact contract, score schema, source metadata schema, and planned blocker readout. This is not full figure replication until #280-#286 close. |
| `scripts/validation/check_gross_2002_full_replication.py --json --require-complete --require-exact-association-hessian --require-fresh-native --write-summary` | `association` | Gross/Sadowski 2002 complete full-replication proof with #298 Figure 2 branch tracing: all ten figures are accepted, Figure 2 records `requires_branch_trace`, the retained trace summary proves complete `bubble_line` and `dew_line` traces, exact Hessian and postsolve receipts, max coordinate gaps of `0.06851` and `0.07000`, and no checker blockers. |

## Current Open Issues

Open M4 work is split into the unified phase-equilibrium certification tree,
the remaining CE/CPE lane, the M3 resolved-input consumer, and a separate
canonical-owner decomposition tree. Certification is rooted at #361;
decomposition is rooted at #462 and never substitutes source movement for a
route acceptance proof.

### Unified Phase-Equilibrium Certification Tree

| Issue | Capability | Backend | Readiness | Summary |
| --- | --- | --- | --- | --- |
| [#361](../../issues/2026-06-29-m4-equilibrium-issue-0361-m4-pe-unify-phase-equilibrium-certification-contracts.md) | `phase-equilibrium` | `Ipopt` | `blocked` | Parent for one enforceable production-route certification contract across PE route families. |
| [#362](../../issues/2026-06-29-m4-equilibrium-issue-0362-implement-shared-production-route-certification-contract.md) | `closed` | `Ipopt` | `complete` | Historical shared certification-contract leaf; closed before the July 10 successor graph. |
| [#363](../../issues/2026-06-29-m4-equilibrium-issue-0363-m4-pe-govern-lle-family-certification.md) | `lle` | `Ipopt` | `blocked` | Parent for LLE family certification. |
| [#364](../../issues/2026-06-29-m4-equilibrium-issue-0364-govern-neutral-nonassociating-lle-certification.md) | `closed` | `Ipopt` | `complete` | Parent neutral nonassociating LLE certification closes after #365 and #366 by this proof/sync PR. |
| [#365](../../issues/2026-06-29-m4-equilibrium-issue-0365-repair-neutral-stage-ii-replay-to-stage-iii-proof-receipt.md) | `closed` | `Ipopt` | `complete` | Fixed neutral LLE Stage II replay-to-Stage III accepted-result receipt by PR #379. |
| [#366](../../issues/2026-06-30-m4-equilibrium-issue-0366-integrate-neutral-nonassociating-source-backed-tolerance-evidence.md) | `closed` | `Ipopt` | `complete` | Connected source-backed neutral nonassociating LLE evidence to the shared contract by PR #380. |
| [#367](../../issues/2026-06-29-m4-equilibrium-issue-0367-govern-associating-lle-certification.md) | `lle`/`association` | `closed` | `complete` | Parent associating LLE certification closes after #368 and #369 by this proof/sync PR. |
| [#368](../../issues/2026-06-29-m4-equilibrium-issue-0368-separate-associating-proof-applicability-from-global-route-metadata.md) | `lle`/`association` | `closed` | `complete` | Split request-specific proof applicability from global route-family proof metadata by PR #379. |
| [#369](../../issues/2026-06-30-m4-equilibrium-issue-0369-integrate-gross-2002-associating-lle-tolerance-evidence.md) | `lle`/`association` | `closed` | `complete` | Connected Gross 2002 associating LLE evidence to the shared contract by PR #383. |
| [#370](../../issues/2026-06-29-m4-equilibrium-issue-0370-govern-electrolyte-lle-certification.md) | `closed` | `Ipopt` | `complete` | Parent electrolyte LLE certification closes after closed sub-issues #191 and #371 by this proof/sync PR. |
| [#371](../../issues/2026-06-30-m4-equilibrium-issue-0371-integrate-reduced-electroneutral-electrolyte-residual-blocks.md) | `closed` | `Ipopt` | `complete` | Attached reduced-electroneutral electrolyte residual blocks to the internal validation contract; public selector admission remains separate. |
| [#372](../../issues/2026-06-29-m4-equilibrium-issue-0372-govern-reactive-electrolyte-lle-certification-boundary.md) | `electrolyte`/`reactive` | `Ipopt` | `blocked` | Boundary parent for future reactive electrolyte LLE after CE/CPE prerequisites. |
| [#373](../../issues/2026-06-29-m4-equilibrium-issue-0373-govern-vle-family-certification.md) | `closed` | `Ipopt` | `complete` | Parent VLE family certification closes after assigning VLE residual ownership under #361 by this proof/sync PR. |
| [#374](../../issues/2026-06-29-m4-equilibrium-issue-0374-govern-flash-and-multiphase-certification.md) | `closed` | `Ipopt` | `complete` | Parent flash/multiphase certification closes after assigning phase-set and postsolve ownership under #361 by this proof/sync PR. |
| [#375](../../issues/2026-06-29-m4-equilibrium-issue-0375-govern-boundary-route-certification.md) | `closed` | `Ipopt` | `complete` | Parent boundary-route certification closes after assigning trace and boundary admission ownership under #361 by this proof/sync PR. |
| [#376](../../issues/2026-06-29-m4-equilibrium-issue-0376-govern-reactive-and-coupled-phase-equilibrium-certification.md) | `cpe` | `Ipopt` | `blocked` | Parent for reactive/coupled PE certification; #331 is now a native sub-issue here. |
| [#458](../../issues/2026-07-11-m4-equilibrium-issue-0458-m4-lle-re-admit-neutral-lle-only-after-scoped-phase-discovery-proof.md) | `neutral_lle` | `Ipopt` | `needs design` | Non-executable future-admission rollup under #363; finite sampled candidates are insufficient. |
| [#459](../../issues/2026-07-11-m4-equilibrium-issue-0459-m4-lle-re-admit-electrolyte-lle-only-after-scoped-charge-neutral-proof.md) | `electrolyte_lle` | `Ipopt` | `needs design` | Non-executable charge-neutral future-admission rollup under #363. |
| [#460](../../issues/2026-07-11-m4-equilibrium-issue-0460-m4-pe-admit-neutral-multiphase-only-after-scoped-phase-set-discovery.md) | `neutral_multiphase` | `Ipopt` | `needs design` | Non-executable future-admission rollup under #361 requiring scoped complete discovery. |
| [#461](../../issues/2026-07-11-m4-equilibrium-issue-0461-m4-pe-admit-neutral-tp-flash-only-after-live-source-backed-proof.md) | `neutral_tp_flash` | `Ipopt` | `needs design` | Non-executable future-admission rollup under #361 requiring live source-backed proof. |

### Electrolyte HELD2 Closeout State

#314 and #343 are historical admission records now used as repair inputs only;
#320 retains Perdomo/Figiel validation, #191 is closed under #370, and #371
retains the internal shared-contract electrolyte residual block. The
`electrolyte_lle` public route and proof routes are closed until a new
native-selector admission change passes the complete gate.

### CE / CPE Open Issues

| Issue | Capability | Backend | Readiness | Summary |
| --- | --- | --- | --- | --- |
| [#321](../../issues/2026-06-26-m4-equilibrium-issue-0321-m4-ce-standalone-chemical-speciation-equilibrium-foundation-before-cpe.md) | `ce` | `Ipopt` | `ready` | Standalone chemical/speciation equilibrium foundation before coupled CPE work. |
| [#328](../../issues/2026-06-26-m4-equilibrium-issue-0328-m4-ce-design-standalone-speciation-public-api-and-result-schema.md) | `ce` | `Ipopt` | `ready` | Design the standalone CE public API and result schema. |
| [#329](../../issues/2026-06-26-m4-equilibrium-issue-0329-m4-ce-complete-primitive-receipts-and-independent-component-checker.md) | `ce` | `Ipopt` | `blocked` | Complete primitive receipts and an independent component checker after #328. |
| [#330](../../issues/2026-06-26-m4-equilibrium-issue-0330-m4-ce-activate-standalone-ce-only-after-gates-pass.md) | `ce` | `Ipopt` | `blocked` | Activate standalone CE only after the CE foundation, API, and validation gates pass. |
| [#331](../../issues/2026-06-26-m4-equilibrium-issue-0331-m4-cpe-define-simultaneous-phase-plus-chemistry-interface-contract.md) | `cpe` | `Ipopt` | `blocked` | Define the simultaneous phase-plus-chemistry interface contract after standalone CE is governed. |
| [#457](../../issues/2026-07-11-m4-equilibrium-issue-0457-m4-ce-classify-source-qualified-nonideal-mea-outcome-and-repair-exact-defect.md) | `ce` | `Ipopt` | `blocked` | Classify accepted M6 MEA evidence and repair only a reproduced M4 defect; rejection does not activate CE. |

### Resolved-Input Consumer And Canonical-Owner Decomposition

| Issue | Capability | Backend | Readiness | Summary |
| --- | --- | --- | --- | --- |
| [#443](../../issues/2026-07-11-m4-equilibrium-issue-0443-m4-consume-provider-resolved-input-sdk-v1.md) | `equilibrium` | `Ipopt` | `blocked` | Consume M3 resolved-input SDK v1 without a second serializer or capability change. |
| [#462](../../issues/2026-07-11-m4-equilibrium-issue-0462-m4-decompose-equilibrium-extension-around-canonical-owners.md) | `equilibrium` | `Ipopt` | `ready` | Non-executable decomposition tracker separate from #361 certification. |
| [#463](../../issues/2026-07-11-m4-equilibrium-issue-0463-m4-characterize-equilibrium-ownership-against-the-shared-ratchet-schema.md) | `equilibrium` | `Ipopt` | `blocked` | Characterize current owners against the inactive M0 schema. |
| [#464](../../issues/2026-07-11-m4-equilibrium-issue-0464-m4-extract-public-green-equilibrium-owners-without-behavior-drift.md) | `equilibrium` | `Ipopt` | `blocked` | Extract only current public-green owners after ratchet activation. |
| [#465](../../issues/2026-07-11-m4-equilibrium-issue-0465-m4-extract-route-gated-electrolyte-native-owners.md) | `electrolyte` | `Ipopt` | `blocked` | Extract gated electrolyte owners after exact charge-neutral correctness gates. |
| [#466](../../issues/2026-07-11-m4-equilibrium-issue-0466-m4-retire-route-gated-internal-binding-and-python-owners.md) | `equilibrium` | `Ipopt` | `blocked` | Retire internal owners only after CE/electrolyte/Gross caller cutovers. |

Current plans:

- [Standalone CE diagnostic repair and admission](../../plans/2026-07-10-m4-standalone-ce-diagnostic-repair-and-admission-plan.md)
- [Provider resolved-input SDK v1 consumer](../../plans/2026-07-10-m4-equilibrium-provider-resolved-input-sdk-v1-consumer-plan.md)
- [Canonical-owner decomposition](../../plans/2026-07-10-m4-equilibrium-canonical-owner-decomposition-plan.md)

## Queue Guard

#247 closed through #249 on 2026-06-13 after the retained synthetic neutral LLE
HELD reliability campaign accepted 100 conditions, ran 10,000 route-refinement
repeats, and recorded zero failed repeats. That evidence supports neutral HELD
algorithm reliability only; it still does not replace source-backed public LLE
showcase evidence, generalized phase-set completion, or associating GFPE
admission.

#250 added the first source-backed neutral nonassociating LLE showcase fixture:
Matsuda/NIST perfluorohexane + hexane paired binodal branch rows, Tihic-derived
pure parameters, a source-fitted binary interaction, finite sampled-candidate
diagnostics, and retained PNG/SVG figures. The July 2026 validation-correctness audit
supersedes the former public-admission interpretation: this fixture remains
internal and does not prove global phase-set completeness.

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

#263 closed through #265 with the strict reduced fugacity-residual local route
for the generalized neutral multiphase sampled-candidate replay. Its checker
requires exact residual derivative metadata, accepted local postsolve, replay
consumption, and no Gibbs-objective-only shortcut.

#261 closed through #266 with a generalized sampled-candidate audit. The
retained checker reports `complete: true`, `blockers: []`,
`selected_candidate_count: 3`, `rejected_candidate_count: 3`, strict Stage III
replay consumption of `sampled_candidate_set_replay`, exact residual
Jacobian/Hessian evidence, and accepted local postsolve. It also records
`global_phase_set_certified: false`; the finite replay is not global phase-set
proof. The former public generalized multiphase admission claim under #189 is
closed; any future admission requires globally complete discovery plus the
current native-selector and canonical-result contracts.

#264 and #189 retain historical multiphase implementation context, but their
former public-admission claim is superseded by the July 2026 validation-correctness audit. The
native work remains internal diagnostic evidence; `multiphase` is absent from
the public route map until the solve and canonical result acceptance are owned
by the native selector and a fresh source-backed admission gate passes.

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
future re-admission work.

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
discovery, Stage III electrolyte refinement and postsolve electrolyte phase-set
certification remain internal; public route admission remains closed.

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

#314 retains historical electrolyte GFPE implementation evidence. It consumes
#269/#300/#302/#306/#312/#313, but the former public claim is superseded and
the `electrolyte_lle` route is closed pending native-selector integration and a
fresh admission proof.

#320 closed by PR #341 with Perdomo/Figiel HELD2 electrolyte flash evidence that
is now retained as internal validation evidence.

#343 closed by PR #359 with historical HELD2 discovery work for #191. #344
through #350 retain doctrine, continuous reduced-electroneutral TPD, Stage I
stability, Stage II dual discovery, orchestration and scenario diagnostics as
internal evidence; they no longer authorize capability admission.

#145 closed through #273 with its internal exact-Hessian proof gate:
Gross/Sadowski 2002 Figure 8 methanol/cyclohexane LLE rows plus retained Table
1/Table 2 parameters pass `check_associating_lle_gross_2002.py
--require-source-data --require-exact-association-hessian --require-route-closed
--require-complete`. The proof stays the internal prerequisite receipt consumed
by #190.

#190 is retained only as internal associating component evidence through the
`check_associating_gfpe_gate.py --require-source-data
--require-internal-evidence --require-route-closed
--require-exact-association-hessian --require-complete` gate. It records the
source-backed Gross/Sadowski 2002 methanol/cyclohexane two-phase fixture with
`assoc_scheme=2B`, `k_ij=0.051`, and `cppad_implicit_association`. Global phase
discovery is unproven, so the checker requires public `lle` admission to remain
closed. #190 does not claim electrolyte, reactive, LLLE,
two-associating-component, or generalized associating phase-set support.

## Closed Issues

- [https://github.com/ePC-SAFT/ePC-SAFT/issues/343](https://github.com/ePC-SAFT/ePC-SAFT/issues/343) closed by [https://github.com/ePC-SAFT/ePC-SAFT/pull/359](https://github.com/ePC-SAFT/ePC-SAFT/pull/359) on 2026-06-29T18:31:54Z
- [https://github.com/ePC-SAFT/ePC-SAFT/issues/350](https://github.com/ePC-SAFT/ePC-SAFT/issues/350) closed by [https://github.com/ePC-SAFT/ePC-SAFT/pull/358](https://github.com/ePC-SAFT/ePC-SAFT/pull/358) on 2026-06-29T16:32:47Z
- [https://github.com/ePC-SAFT/ePC-SAFT/issues/349](https://github.com/ePC-SAFT/ePC-SAFT/issues/349) closed by [https://github.com/ePC-SAFT/ePC-SAFT/pull/357](https://github.com/ePC-SAFT/ePC-SAFT/pull/357) on 2026-06-29T02:11:17Z
- [https://github.com/ePC-SAFT/ePC-SAFT/issues/348](https://github.com/ePC-SAFT/ePC-SAFT/issues/348) closed by [https://github.com/ePC-SAFT/ePC-SAFT/pull/356](https://github.com/ePC-SAFT/ePC-SAFT/pull/356) on 2026-06-28T22:06:29Z
- [https://github.com/ePC-SAFT/ePC-SAFT/issues/347](https://github.com/ePC-SAFT/ePC-SAFT/issues/347) closed by [https://github.com/ePC-SAFT/ePC-SAFT/pull/355](https://github.com/ePC-SAFT/ePC-SAFT/pull/355) on 2026-06-28T19:53:46Z
- [https://github.com/ePC-SAFT/ePC-SAFT/issues/346](https://github.com/ePC-SAFT/ePC-SAFT/issues/346) closed by [https://github.com/ePC-SAFT/ePC-SAFT/pull/354](https://github.com/ePC-SAFT/ePC-SAFT/pull/354) on 2026-06-28T18:23:18Z
- [https://github.com/ePC-SAFT/ePC-SAFT/issues/345](https://github.com/ePC-SAFT/ePC-SAFT/issues/345) closed by [https://github.com/ePC-SAFT/ePC-SAFT/pull/353](https://github.com/ePC-SAFT/ePC-SAFT/pull/353) on 2026-06-28T15:35:44Z
- [https://github.com/ePC-SAFT/ePC-SAFT/issues/344](https://github.com/ePC-SAFT/ePC-SAFT/issues/344) closed by [https://github.com/ePC-SAFT/ePC-SAFT/pull/352](https://github.com/ePC-SAFT/ePC-SAFT/pull/352) on 2026-06-28T04:20:05Z
- [https://github.com/ePC-SAFT/ePC-SAFT/issues/320](https://github.com/ePC-SAFT/ePC-SAFT/issues/320) closed by [https://github.com/ePC-SAFT/ePC-SAFT/pull/341](https://github.com/ePC-SAFT/ePC-SAFT/pull/341) on 2026-06-29T17:15:44Z
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
