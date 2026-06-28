# M4 HELD2 Public Route Phase Discovery Full Adoption

## Purpose

Lay out the missing implementation backbone for full HELD2-style electrolyte
phase discovery in `packages/epcsaft-equilibrium`. The existing M4 electrolyte
issues prove readiness, charge-neutral screening, retained phase-discovery
diagnostics, local Stage III refinement, postsolve certification, and
representative public admission. They do not fully implement HELD2-style
global phase discovery as the production candidate-generation engine behind
the public electrolyte route.

This spec turns that remaining long-term plan into concrete M4 issue slices.

## Scope

Owner: M4 equilibrium, package `packages/epcsaft-equilibrium`.

Target public behavior:

- `Equilibrium(..., route="electrolyte_lle")` can use HELD2-style discovery to
  find and certify electrolyte phase sets without relying on one retained
  representative fixture or hand-picked candidate set.
- The public route orchestrates discovery, Stage III Ipopt refinement, and
  postsolve certification.
- The route keeps reduced electroneutral coordinates, projected
  electrochemical or mean-ionic residuals, exact derivative receipts where
  claimed, and explicit phase-set completeness diagnostics.

Out of scope:

- Reactive electrolyte LLE.
- CE/CPE coupling.
- M5 parameter regression.
- Claiming Khudaida model reproduction without an M5-fitted parameter bundle.
- Replacing all boundary workflows with HELD2 discovery.

## Verified Current Coverage

- #300 closed the reduced electroneutral variable and Born SSM/DS exactness
  readiness gate.
- #302 closed native-backed charge-neutral electrolyte TPD screening, but it
  explicitly kept full HELD2 dual discovery pending.
- #306 closed a counterion-pair phase-discovery diagnostics gate. It proved
  matrix-rank and reduced-coordinate bookkeeping, but did not cut over public
  route candidate generation.
- #312 closed retained Stage III reduced-variable refinement evidence.
- #313 closed retained postsolve certification evidence.
- #314 closed representative public electrolyte route admission only.
- #320/PR #341 validates a Perdomo/Figiel electrolyte boundary row through the
  shared `NlpProblem`/Ipopt exact-Hessian route, but keeps full public HELD2
  production discovery out of the claim.

## Gap

The project plan says deterministic TPD/candidate screening is not full HELD.
The remaining missing capability is a production-grade HELD2-style discovery
orchestrator:

1. Continuous reduced electroneutral TPD minimization in volume-composition
   space.
2. Stage I stability certification over a governed start set.
3. Stage II dual/cutting-plane candidate discovery with explicit lower and
   upper bounds, bound-gap convergence, and candidate storage.
4. Stage III Ipopt refinement driven by Stage II candidates, not by a synthetic
   or fixture-specific phase set.
5. Postsolve phase-set completeness certification tied back to the Stage II
   dual certificate.
6. Public route orchestration and result diagnostics.
7. Scenario validation across stable, unstable, boundary, phase-label
   permutation, common-ion, and mixed-salt cases.
8. Registry, capability, and documentation admission after executable evidence.

## Public-Route Doctrine

This doctrine is the acceptance contract for #344 and the implementation
boundary for #345 through #350. It is based on the Perdomo et al. 2025
HELD2.0 derivation for strong electrolytes and on the retained M4 electrolyte
gates already closed under #300, #302, #306, #312, #313, #314, and #320.

### Reduced Electroneutral State

Every electrolyte phase state used by discovery, refinement, postsolve, and
public-route admission is represented in a reduced electroneutral basis before
it is interpreted as explicit species amounts:

```text
Q^alpha = sum_i z_i n_i^alpha = 0
n_E^alpha = sum_{i in C^(E)} -(z_i / z_E) n_i^(E),alpha
bar_n_i^(E),alpha = (1 - z_i / z_E) n_i^(E),alpha
```

where `alpha` is a phase index, `E` is the eliminated charged species, and
`C^(E)` excludes that species. The eliminated species is chosen by the
implementation contract for the active reduced basis and must be recorded in
diagnostics. Lift and back-lift are accepted only when the explicit species
amounts satisfy per-phase charge, total charge, material balance, positivity,
and normalization checks.

The charged transfer residual is a reduced-space residual. Accepted evidence
must use one of these equivalent families and name which one was evaluated:

```text
r_i^(el,alpha,beta) = bar_mu_i^(el),alpha - bar_mu_i^(el),beta
r^(proj,alpha,beta) = Pi_perp (mu^alpha - mu^beta)
r_salt^(alpha,beta) = nu_+ mu_+^alpha + nu_- mu_-^alpha
                        - nu_+ mu_+^beta - nu_- mu_-^beta
```

`bar_mu_i^(el)` is the modified electrochemical potential implied by the
Perdomo et al. reduced variables. `Pi_perp` projects away the charge gauge.
`r_salt` is the mean-ionic or salt-pair residual for the active stoichiometry.
Raw single-ion chemical-potential equality is never sufficient evidence for
charged transfer because the single-ion gauge is arbitrary.

Neutral molecular transfer remains checked directly through the neutral
chemical-potential or fugacity residual family used by the public route:

```text
r_i^(0,alpha,beta) = mu_i^alpha - mu_i^beta, z_i = 0
```

### Stage Responsibilities

| Stage | Route responsibility | Required retained evidence | Rejected evidence |
| --- | --- | --- | --- |
| Stage I stability | Solve the continuous reduced-electroneutral tangent-plane-distance problem in `(V, bar_x^(EC))` space and classify the feed as stable, unstable, incomplete, or numerically suspect. | Start-set policy, eliminated species, finite objective and derivative receipts, trial-phase lift/back-lift charge checks, minimum TPD, active bounds, and start-by-start failure records. | Discrete candidate screening alone, single-start success, or a non-negative local minimum reported as global stability without coverage evidence. |
| Stage II discovery | Run the HELD2-style dual/cutting-plane loop and generate the candidate phase set from lower-level minimizers, not from hand-picked fixtures. | Upper and lower bound history, bound gap, lambda vector, lower-level minimizer records, candidate insertions, duplicate/rejected candidate reasons, and replay payload consumed by Stage III. | A synthetic phase set, a candidate set with missing provenance, or a Stage II record that cannot be replayed. |
| Stage III refinement | Refine the discovered phase set through the shared public `NlpProblem`/Ipopt route with exact derivative receipts where claimed. | Stage II payload id, reduced variables/equations/scaling/bounds, exact Jacobian/Hessian receipts, strict Ipopt status, material balance, phase amounts, and refined explicit species compositions. | Private-native-only proof, `Solve_Succeeded` without physical residuals, or a solver option that bypasses the reduced electrolyte contract. |
| Postsolve certification | Certify the refined phase set in explicit species space and tie completeness back to Stage II. | Explicit-ion reconstruction, per-phase and total charge, pressure consistency, neutral transfer residuals, projected electrochemical or mean-ionic residuals, phase-distance floor, positivity, domain margins, and completeness status. | Residual-only success, hidden charge clipping, collapsed phases, raw single-ion equality, or missing phase-set completeness evidence. |
| Public-route cutover | Admit `Equilibrium(..., route="electrolyte_lle")` only after the implementation and validation slices pass. | Public API result fields, retained per-row diagnostics, registry evidence, capability docs, and proof that the public route orchestrates Stage I through postsolve. | A capability claim based only on #314 representative admission, #320 boundary validation, diagnostic-only scripts, or route keys that skip HELD2 discovery. |

### Candidate Lifecycle

| State | Meaning | Minimum evidence |
| --- | --- | --- |
| `seed` | Start point or retained support point used by Stage I or Stage II. | Source fixture id, transformed variables, bounds, and charge-neutral lift. |
| `trial_phase` | A continuous TPD or lower-level minimizer result. | Objective value, convergence status, derivative receipt, active bounds, and lift/back-lift residuals. |
| `stage_i_certificate` | Feed stability classification from Stage I. | Minimum TPD, coverage policy, stable/unstable/incomplete/suspect label, and rejected-start details. |
| `stage_ii_candidate` | Candidate phase accepted into the HELD2 dual set. | Bound history, lambda vector, replay payload, candidate distance, and duplicate/rejection rationale. |
| `stage_iii_refined` | Stage II candidate set refined by the shared Ipopt route. | Shared `NlpProblem` receipt, exact derivative flags, phase amounts, and finite reduced residuals. |
| `postsolve_certified` | Explicit species phase set accepted by physical residual checks. | Charge, pressure, neutral transfer, charged transfer, material balance, phase distance, positivity, and domain margins. |
| `public_admitted` | Scenario accepted through the public package route. | Public result route key, retained diagnostics, registry entry, and validation command evidence. |
| `rejected` | Candidate or route result rejected before admission. | Rejection reason, failed residual family, failed tolerance, and source row or start id. |

### Acceptance Residual Families

The implementation slices may tighten these values when a checker owns a
stricter source-data tolerance. They may not omit the residual family.

| Residual family | Doctrine acceptance floor |
| --- | --- |
| Per-phase and total electroneutrality | `max_abs_charge_residual <= 1.0e-10` after explicit-species lift/back-lift. |
| Material balance and composition normalization | `max_abs_balance_residual <= 1.0e-10` in mole-fraction or normalized amount coordinates. |
| Neutral transfer | Scaled chemical-potential, fugacity, or ln-fugacity residual `<= 1.0e-6`. |
| Charged transfer | Projected electrochemical or mean-ionic residual `<= 1.0e-6` on the documented scale. |
| Pressure consistency | Scaled pressure residual `<= 1.0e-6` or a stricter route-owned absolute tolerance with units recorded. |
| Phase distinctness | Minimum accepted phase distance `>= 1.0e-8` unless the scenario is explicitly a boundary-limit row. |
| Stage I TPD | Stable only when the governed start set has no TPD below `-1.0e-10`; unstable when at least one certified trial phase is below that floor. |
| Stage II bound gap | Final dual/primal bound gap `<= 1.0e-6` on the stored free-energy scale, or the route must report `incomplete`. |
| Domain margins | Positive transformed variables and finite EoS calls for every accepted phase. |

### Validation Matrix

| Scenario | Purpose | Required evidence | Acceptance rejection examples |
| --- | --- | --- | --- |
| Stable feed | Prove Stage I can stop without inventing phases when no negative TPD is certified. | Governed start-set record, non-negative minimum TPD within tolerance, finite derivatives, and explicit stable classification. | Calling a single local minimizer stable or suppressing failed starts. |
| Unstable feed | Prove Stage I finds a negative reduced-electroneutral TPD and hands it to Stage II. | Negative TPD trial phase, charge-neutral lift, active bounds, and Stage II initialization payload. | Reporting unstable from a fixture label without a continuous TPD solve. |
| Boundary feed | Prove near-binodal or trace-ion cases do not collapse phases or clip charge. | Phase-distance floor or boundary-limit label, trace-coordinate handling, finite domain margins, and postsolve residuals. | Hidden ion clipping, collapsed phases counted as success, or missing trace diagnostics. |
| Phase-label permutation | Prove results are invariant to phase ordering and candidate insertion order. | Canonical matching, same physical phase set, same residual family maxima, and stable public result schema. | Hard-coding `liquid1`/`liquid2` semantics beyond labels. |
| Neutral-limit parity | Prove reduced electrolyte machinery does not degrade the neutral HELD/GFPE route as ionic strength tends to zero or when the route is neutral. | Neutral-route comparison fixture, matching phase count, neutral transfer residuals, and no charged residual family claimed when no charged species exist. | Routing neutral cases through electrolyte-only assumptions or claiming charged residuals for neutral rows. |
| Common-ion electrolyte | Prove the reduced basis handles salts sharing an ion. | Rank evidence, eliminated species, lifted explicit species, mean-ionic or projected residuals for each independent salt direction, and postsolve charge checks. | Pair bookkeeping that only supports one independent salt. |
| Mixed-salt or asymmetric electrolyte | Prove the reduced basis handles more than a symmetric 1:1 salt. | Full-rank reduced matrix, stoichiometric residual mapping, projected electrochemical residuals, finite Stage II candidates, and Stage III/postsolve receipts. | Assuming equal cation/anion counts, fixed NaCl-only pairs, or one-salt mean-ionic residuals. |

### Capability Boundary

#344 does not admit a runtime capability. It defines the doctrine and matrix
that the runtime slices must satisfy. Public electrolyte HELD2 capability stays
closed until #345, #346, #347, #348, #349, and #350 all pass with retained
public-route evidence.

## Issue Set

This spec is implemented by one tracking issue and seven vertical slices:

1. #343: full HELD2 public-route adoption tracking.
2. #344: doctrine and validation matrix.
3. #345: continuous reduced-electroneutral TPD minimizer.
4. #346: Stage I stability certificate.
5. #347: Stage II dual/cutting-plane discovery.
6. #348: public route orchestration through Stage III and postsolve.
7. #349: multi-scenario HELD2 validation ladder.
8. #350: registry, docs, and capability admission.

## Acceptance

The overall adoption is complete only when:

- the public electrolyte route uses HELD2 discovery for candidate generation;
- Stage III refinement consumes the discovered candidate set;
- postsolve certification reports phase-set completeness and physical
  residuals;
- retained tests cover stable, unstable, boundary, phase-label permutation,
  common-ion, and mixed-salt cases;
- registry/capability docs admit only the evidence-backed scope; and
- #191 can close without relying on #314 representative evidence or #320
  boundary-only evidence as a substitute for full phase discovery.
