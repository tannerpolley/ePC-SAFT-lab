# M3 / HELD 1.0 Readiness Cleanup

Milestone: `M0 - Governance`
Affected milestones: `M3 - EOS`, `M4 - Equilibrium`
Affected packages: `packages/epcsaft`, `packages/epcsaft-equilibrium`
Issue: `none`
Status: `draft`
Last synced: `2026-06-08`

## Summary

Convert the revised `.chatgpt` Pro Review Packet v2 into a canonical
repo-local cleanup spec for M3 and HELD 1.0 readiness. The cleanup should align
tracker mirrors, milestone summaries, and dependency wording with the evidence
now present in the repo.

This is a readiness and issue/doc hygiene spec. It is not an implementation
spec for provider EOS, equilibrium, HELD/GFPE, or public route expansion.

The core direction is:

1. Treat #161 as an independent explicit-association and Picard CppAD evidence
   issue, not as a HELD, M4 equilibrium, or #208 dependency.
2. Keep #148 narrow: HELD-style neutral phase discovery and TPD certification
   evidence for current activation-matrix neutral flash/LLE route families.
3. Keep #208 blocked until a concrete M3 provider derivative bundle contract
   exists and is merged.
4. Preserve current activation-matrix exposure boundaries and avoid broad HELD,
   associating, electrolyte, reactive, or generalized multiphase claims.

## Project Context Evidence Used

- `docs/superpowers/PROJECT_CONTEXT.md` defines package ownership,
  completion standards, capability honesty, and the M3/M4 milestone envelope.
- `CONTEXT.md` defines shared domain terms, including generic package workflow,
  capability contract, selector core, native activation matrix, derivative path,
  production solver path, and completion evidence.
- `.chatgpt/pro-review-packets/2026-06-08-milestone-3-held-1-0-code-health-v2/README.md`
  supplied the incoming review packet that triggered this spec.
- `docs/superpowers/milestones/M3-eos/README.md` still lists #161 as an open
  M3 issue awaiting the M8 final Picard decision memo.
- `docs/superpowers/issues/2026-05-29-m3-eos-issue-0161-design-explicit-pc-saft-association-site-closures-for-eos-evaluation.md`
  records the final Picard and stress memo findings and keeps #161 open for
  standalone provider CppAD evidence, with fixed-depth Picard still in scope.
- `analyses/package_validation/explicit_association_toybox/docs/issue_161_picard_admission_decision.md`
  recommends `close_without_provider_implementation` for #161.
- `analyses/package_validation/explicit_association_toybox/docs/picard_stress_rescue_or_retire_decision.md`
  selects `retire_picard` and records the stress metrics behind that decision.
- `docs/superpowers/specs/2026-06-05-m8-python-toybox-topology-aware-explicit-association-model-selection.md`
  clarifies that the retired Picard framing does not reject every future
  explicit route; Picard and other future candidates need direct provider CppAD
  proof before provider admission.
- `docs/superpowers/milestones/M4-equilibrium/README.md` lists #148 and #186 as
  ready and #187/#188/#189/#190/#191/#208 as blocked.
- `docs/superpowers/issues/2026-05-24-m4-equilibrium-issue-0148-implement-held-style-neutral-phase-discovery-and-tpd-certification-for-activation-routes.md`
  defines #148 as neutral phase discovery and TPD certification evidence, with
  explicit no-new-route and no-associating/electrolyte/reactive boundaries.
- `docs/superpowers/issues/2026-06-01-m4-equilibrium-issue-0208-move-equilibrium-objective-assembly-onto-provider-derivative-bundles.md`
  defines the objective-free provider derivative bundle dependency for #208.
- `docs/superpowers/milestones/M4-equilibrium/generalized-fluid-phase-equilibrium.md`
  says deterministic TPD/candidate screening is useful support but not full
  HELD, and records the staged HELD ladder.
- `docs/superpowers/specs/2026-05-26-m4-equilibrium-stage-by-stage-implementation-plan.md`
  keeps generalized production exposure behind exact derivatives,
  route-owned scaling/bounds, HELD-stage phase discovery, postsolve
  certification, and source-backed validation.
- `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/equilibrium_activation.py`
  and `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/core/activation_matrix.h`
  expose only the current production route families and keep future families
  declared but unexposed.
- `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/workflows.py` rejects
  ionic mixtures for production selector routes and rejects associating mixtures
  for current neutral LLE and single-component VLE routes.
- `packages/epcsaft-regression/src/epcsaft_regression/capabilities.py` keeps
  associating and dielectric optimizer support conservative by separating
  derivative evidence from public production target-kind claims.

## User Decisions

- Use the narrow cleanup scope.
- Write one canonical spec in `docs/superpowers/specs/`.
- Do not create a broad HELD/GFPE implementation design from the review packet.
- Do not edit issue mirrors, source code, GitHub state, or capability registries
  as part of this brainstorm artifact.

## Verified Current State

### M3 / #161

#161 remains an open M3 EOS issue, but repo-local evidence now supports
independent direct CppAD proof for explicit association and Picard rather than
HELD/M4 dependency treatment.

Verified points:

- M3 owns provider EOS/state/parameters, native SDK contract, exact
  derivatives, CppAD/implicit sensitivities, and provider-only capability
  claims.
- The M3 README still says #161 awaits the M8 final Picard decision memo.
- The #161 local mirror records that the stress memo selects `retire_picard`
  for the tested damped Picard framing.
- The final Picard admission memo recommends
  `close_without_provider_implementation`.
- The stress decision memo selects `retire_picard` and is analysis-only
  evidence; it does not change provider, equilibrium, regression, benchmark, or
  public API behavior.
- The M8 topology-aware selector spec softens the interpretation: retire the
  tested Picard framing, but keep future topology-gated exact reductions,
  site-class reductions, or narrow bounded Picard research in M8 until one earns
  provider admission.

Cleanup implication:

- Update tracker mirrors and M3 summary language so they no longer imply the
  final M8 decision is pending, that the tested Picard framing is provider
  implementation-ready, or that #161 blocks HELD/M4/#208.
- Preserve #161 as an independent direct CppAD evidence issue and preserve
  Picard as an explicit association candidate family within that issue. Preserve
  the M8 evidence as negative admission evidence for treating the tested Picard
  toybox result as sufficient provider proof.

### M4 / HELD 1.0

HELD 1.0 should mean narrow #148 evidence closure unless a later approved spec
chooses a broader scope.

Verified points:

- #148 is `ready` and scoped to HELD-style neutral phase discovery plus TPD
  certification for current activation-matrix neutral flash/LLE routes.
- #148 already says current evidence covers deterministic screening, continuous
  TPD, HELD Stage I diagnostics, finite-candidate Stage II bound audit, and
  current-route Stage III Ipopt refinement.
- #148 already forbids adding public routes, exposing associating LLE, exposing
  electrolyte/reactive routes, treating phase-distance as an equilibrium
  equation, accepting a result only because Ipopt converged, or bypassing the
  native activation matrix.
- The GFPE spec says deterministic TPD/candidate screening is seed and
  certification support, not full HELD.
- The stage-by-stage implementation plan keeps generalized production exposure
  behind exact objective gradients, exact constraint Jacobians, exact
  Lagrangian Hessians, route-owned bounds and scaling, transform chain-rule
  coverage, HELD-stage phase discovery, and postsolve certification.

Cleanup implication:

- Preserve #148 wording if it remains unambiguous.
- If #148 is edited later, keep the no-new-route and neutral-only boundary
  visible near the summary and acceptance criteria.
- Do not use #148 to claim generalized HELD production readiness.

### M4 / #208

#208 is a real architecture dependency, not a paper blocker.

Verified points:

- #208 is `blocked`.
- #208 requires `epcsaft-equilibrium` to own pressure-transformed Helmholtz
  objective assembly and exact NLP derivative payloads while consuming
  objective-free provider local phase derivative bundles.
- #208 acceptance criteria require no provider API called by equilibrium to
  require `target_pressure` or return a solver objective value as a
  provider-owned concept.
- #208 explicitly remains blocked by the M3 provider derivative bundle issue
  until that provider contract is merged.

Cleanup implication:

- If no concrete M3 issue exists for the provider derivative bundle contract,
  create one before unblocking #208.
- Update #208 mirror/plan wording only to point at the concrete M3 issue once
  it exists.

### Activation And Capability Boundaries

Verified points:

- `epcsaft-equilibrium` production-exposes `neutral_tp_flash`, `neutral_lle`,
  `single_component_vle`, and `bubble_dew_derived_routes`.
- Future or broader families such as generalized neutral multiphase,
  electrolyte LLE, reactive speciation, reactive LLE, and reactive electrolyte
  LLE are recorded as declared but unexposed.
- Exposed equilibrium families require exact gradients, Jacobians, and Hessians
  for exposed Ipopt routes.
- Public route specs map bubble/dew routes to `bubble_dew_derived_routes`,
  `flash` to `neutral_tp_flash`, `lle` to `neutral_lle`, and
  `single_component_vle` to `single_component_vle`.
- Regression capabilities claim public production support for `m`, `s`, `e`,
  `d_born`, `k_ij`, and `f_solv`; associating and dielectric target kinds are
  kept as derivative evidence or registry/pending entries, not production
  optimizer claims.

Additional cleanup flag:

- The provider-side capability evidence registry still appears to list only
  three equilibrium production families while the equilibrium extension exposes
  four, including `single_component_vle`. This should be verified in a separate
  focused cleanup issue before any route capability evidence is broadened.

## Recommended Cleanup Shape

### Option A - Tracker-Only Cleanup

Update local issue mirrors, milestone README language, and GitHub issue state
where appropriate. This is the smallest path.

Tradeoff:

- Fastest and least risky.
- Leaves #208's missing concrete M3 dependency issue unresolved unless handled
  separately.

### Option B - Tracker Cleanup Plus M3 Dependency Issue

Update the M3/#161 and M4/#148/#208 wording and create or identify the concrete
M3 provider derivative bundle issue that #208 depends on.

Tradeoff:

- Best match for the packet because it removes the fake ambiguity around #208.
- Still avoids source implementation and broad HELD scope.

Recommendation:

- Use Option B. It reaches the obvious cleanup finish line without turning the
  packet into implementation work.

## Proposed Issue/Doc Changes For A Future Plan

### #161 Local Mirror And GitHub Issue

- Keep #161 open as an independent direct CppAD evidence issue for explicit
  association, including the Picard path.
- Preserve the derivation and toybox evidence as historical design evidence.
- State that the Picard path remains present with explicit association, and that
  Picard or any other explicit association closure work requires direct provider
  CppAD evidence before any provider admission.
- Do not treat #161 as a HELD 1.0 prerequisite, M4 prerequisite, or #208
  prerequisite.

### M3 README

- Replace the current "await final M8 Picard decision memo" language with
  wording that says the M8 decision artifacts now exist, the tested damped
  Picard toybox result is not sufficient provider proof, and #161 remains open
  for independent direct provider CppAD evidence with Picard still in scope.
- Add or link the M3 provider derivative bundle issue once it exists.

### New Or Existing M3 Provider Derivative Bundle Issue

Suggested title:

```text
M3: Provide objective-free local phase derivative bundles for equilibrium objective assembly
```

Minimum acceptance criteria:

- Define a provider-owned local phase derivative bundle contract.
- Keep the bundle objective-free: no `target_pressure`, no pressure-work
  objective, and no solver objective as a provider-owned concept.
- Include Helmholtz values, gradients, Hessians, third-derivative tensors, and
  pressure derivatives as needed by current neutral nonassociating GFPE/HELD
  route requirements.
- Report unsupported associating, electrolyte, and reactive derivative gaps
  explicitly without exposing those families.
- Add provider tests proving shape, derivative labels, exact derivative status,
  and failure behavior.
- Unblock #208 only after the provider contract is merged.

### #208 Mirror And Plan

- Keep #208 blocked.
- Point #208 at the concrete M3 derivative bundle issue after it exists.
- Preserve the ownership boundary: provider supplies objective-free local phase
  derivative bundles; equilibrium owns pressure-transformed objective assembly
  and exact NLP derivative payloads.

### #148 Mirror And Plan

- Leave #148 alone if current wording remains clear.
- If edited, keep the narrow HELD 1.0 scope near the top:
  current activation-matrix neutral flash/LLE families only; no public route
  expansion; no associating/electrolyte/reactive exposure; no full generalized
  HELD claim.

### Capability Registry Follow-Up

- Verify whether provider-side capability evidence should include
  `single_component_vle` now that the equilibrium extension activation matrix
  production-exposes it.
- If yes, update the provider-side validation routing and tests in the same
  focused change.
- If no, document why provider-side capability evidence intentionally omits the
  extension route.

## Non-Goals

- No provider EOS implementation.
- No equilibrium route implementation.
- No HELD/GFPE broad implementation.
- No public route expansion.
- No associating, electrolyte, reactive, or generalized multiphase exposure.
- No capability broadening without tests and evidence.
- No GitHub issue mutation from this spec alone.
- No downstream application API or metric work.

## Open Questions

- Is there already a GitHub issue that exactly owns the M3 objective-free local
  phase derivative bundle contract, or should one be created?
- Should #161 be closed outright, or should it be converted into a design-record
  closure comment while leaving a new M8 follow-up for topology-aware explicit
  association candidates?
- Should the provider-side capability evidence registry mirror
  `single_component_vle`, or is that route intentionally extension-local?

## Proof Oracle Candidates For Later Planning

Use only the checks that match the edited surface:

```powershell
uv run python scripts/dev/validate_project.py docs
```

```powershell
uv run python run_pytest.py packages/epcsaft-equilibrium/tests/contracts/test_activation_capabilities.py -q
```

```powershell
uv run python run_pytest.py tests/workflows/repo/test_run_pytest.py -q
```

```powershell
uv run python scripts/validation/check_phase_discovery.py --json
```

For GitHub tracker changes, also verify issue state, milestone, labels, Project
fields, and dependency edges through the issue-tracker workflow before claiming
tracker completion.

## Completion Criteria For The Cleanup Plan

- #161 remains open but no longer looks provider implementation-ready or tied to
  HELD/M4/#208 in M3 summary or tracker state.
- M3 has a concrete derivative bundle issue if #208 continues to depend on one.
- #208 points to that concrete dependency and remains blocked until the provider
  contract is merged.
- #148 retains its narrow neutral HELD-style evidence boundary.
- Capability and activation evidence remain honest and synchronized.
- Validation matches the edited files and reports skipped checks explicitly.
