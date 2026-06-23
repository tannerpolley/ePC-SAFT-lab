# M4 Equilibrium HELD 1.0 Full Adoption

Milestone: `M4 - Equilibrium`
Affected packages: `packages/epcsaft-equilibrium`, provider derivative
contracts where explicitly required
Affected validation milestone: `M6 - Validation`
Status: `draft`
Created: `2026-06-11`
Updated: `2026-06-13`

## Summary

This spec is the durable M4 contract for full HELD 1.0 adoption before
associating GFPE is implemented. It incorporates the comparison against Pereira
et al. 2012 and updates the local status after #187, #241, and #188 were
resolved.

The current neutral proof lane is materially stronger than the older blocked
rows suggested: after a fresh native rebuild, Stage II dual-loop replay and
Stage III route-refinement replay-consumption are verified for the current
neutral proof path. That does not yet equal full Pereira-style HELD 1.0
adoption. Pereira-style adoption also requires explicit all-phase termination,
reliable nonconvex inner-search behavior, phase-count independence, source-backed
LLE evidence, and a reliability campaign before the neutral machinery can be
treated as the pre-associating algorithm base.

The central rule remains: closed issues are evidence, not adoption. A family,
method, registry row, capability line, or validation gate may claim HELD 1.0
coverage only when its active implementation path has executable HELD-stage
evidence, exact derivative coverage where the route requires it, postsolve
certification, and registry/capability text that matches the evidence.

## Terminology Guard

`HELD` means the algorithm acronym `Helmholtz free Energy Lagrangian Dual`.
In this spec, HELD 1.0 refers to the Pereira et al. 2012 algorithmic framing for
volume-composition Helmholtz-dual phase equilibrium. It is not a reference to
the author Held in later electrolyte ePC-SAFT papers. Held 2014 and related
electrolyte papers remain validation literature for electrolyte GFPE and
HELD2.0-style work, not the source of the HELD 1.0 algorithm name.

## Project Context Evidence Used

- Verified: `docs/superpowers/PROJECT_CONTEXT.md` defines GFPE doctrine as the
  M4 organizing contract and says deterministic TPD/candidate screening is seed
  and certification support, not full HELD.
- Verified:
  `docs/superpowers/milestones/M4-equilibrium/generalized-fluid-phase-equilibrium.md`
  defines the local HELD ladder: deterministic support, continuous TPD, Stage I
  stability, Stage II dual cutting-plane phase discovery, Stage III Ipopt
  refinement, and HELD2.0 for strong electrolytes.
- Verified:
  `docs/superpowers/milestones/M4-equilibrium/registries/equilibrium-benchmark-registry.yaml`
  keeps GFPE family rows unexposed until full HELD-stage phase discovery, exact
  derivatives, and postsolve certification pass.
- Verified:
  `docs/papers/md/Equilibrium/Pereira et al. - 2012 - The HELD algorithm for multicomponent, multiphase equilibrium calculations with generic equations of.md`
  describes HELD as a PT flash algorithm in Helmholtz volume-composition space,
  with initialization/stability testing, alternating phase identification by
  linear and nonconvex optimization, acceleration/convergence, tunneling,
  multistart inner searches, mass-balance termination, and reliability testing
  over thousands of unstable conditions.
- Verified: #187 closed the shared NLP/Ipopt infrastructure gate.
- Verified: #241 closed the neutral Stage II replayable dual phase-discovery
  gate.
- Verified: #188 closed the source-backed neutral TP-flash fixture gate.
- Verified: #250 adds the source-backed neutral nonassociating LLE showcase
  fixture and retained figures for Matsuda/NIST perfluorohexane + hexane.
- Verified: after the fresh native rebuild following #241/#188, the neutral
  phase-discovery checker reported Stage II as replayable and Stage III as
  current-route refinement consuming the Stage II replay seed.
- Verified: #246 is now the ready evidence-hygiene issue for adding
  fresh-native receipts to HELD/GFPE validation artifacts.
- Inference: the remaining full-adoption work is no longer "make Stage II/III
  exist" for the current neutral proof lane. The remaining work is to harden
  Pereira-style algorithm parity and expand the proof surface before
  associating GFPE borrows the neutral HELD machinery.

## Pereira 2012 Requirements Imported Into M4

The following requirements are the paper-derived gaps that must be visible in
plans and issues before associating GFPE starts.

| Pereira-style requirement | Local current state | Remaining adoption requirement |
| --- | --- | --- |
| Helmholtz volume-composition PT flash formulation | GFPE doctrine uses pressure-transformed Helmholtz amount-volume NLP | Keep this as the shared phase-equilibrium objective and reject residual-only completion claims |
| Initialization/stability testing | Continuous TPD and Stage I diagnostics exist in the neutral proof path | Require converged-start accounting and explicit incomplete-start failure state in every adoption receipt |
| Alternating outer linear and inner nonconvex phase identification | Neutral Stage II replay path is now verified for the current fixture | Record lower bound, upper bound, best incumbent, bound gap, candidate cuts, rejected candidates, and stopping reason as durable evidence |
| Nonconvex inner-search reliability | Current proof lane has replayable candidate metadata | Add a Pereira-style reliability harness for multistart/tunneling-like inner-search stress, with no hidden initial-guess carryover |
| Mass-balance termination to identify all stable phases | Current fixtures certify material balance after solve | Prove the algorithm cannot declare completion while candidate phases fail the global feed mass balance |
| More-than-two-phase readiness | Generalized phase-set PE remains planned and #189 remains blocked | Extend #189 to arbitrary phase-count feasibility, duplicate/collapsed phase rejection, and LLLE-ready completeness |
| Stage III acceleration/convergence | Current route refinement consumes Stage II replay seed and requires Ipopt success | Preserve strict `success` and `solve_succeeded`; acceptable-level, tiny-step, feasible-only, and iteration-limit paths remain incomplete evidence |
| Reliability campaign | Current proof oracles are focused checker/test receipts | Add repeated random unstable-condition and repeated point-calculation receipts before claiming Pereira-style algorithm reliability |
| Literature breadth | Source-backed neutral TP flash exists; #250 adds a source-backed neutral nonassociating LLE showcase | Use #189 for phase-count breadth before associating admission |
| Associating preparation | #145/#190 remain blocked | Associating GFPE may reuse the neutral HELD skeleton only after neutral pre-association gates and exact association derivatives are proven |

## Current Coverage Matrix

| Family or method | Required HELD adoption state | Current issue coverage | Current truth |
| --- | --- | --- | --- |
| Public `flash` utility | `held_1_admitted` for proof lane; cheap public path may remain deterministic by default | #148, #187, #241, #188, #246 | Neutral proof lane verified after fresh build; receipt hardening still open |
| Neutral nonassociating `lle` utility | `held_1_admitted` before any generalized claim | #148, #187, #241, #188, #247, #250, #189 | Synthetic route proof and source-backed Matsuda/NIST LLE showcase exist; generalized phase-set proof still missing |
| `bubble_pressure`, `bubble_temperature`, `dew_pressure`, `dew_temperature` | `derived_from_held_1` | #189 | Must be degree-of-freedom swaps over the certified GFPE core with strict per-point diagnostics |
| Cloud/shadow workflows | `derived_from_held_1` after implementation | #189 | Route contracts and executable evidence still needed |
| `single_component_vle` | direct boundary-route evidence, no borrowed HELD claim | #228 closed, #192 later | Keep separate from HELD family adoption unless registry text claims phase discovery |
| PE-Neutral TP Flash | `held_1_admitted` | #187, #241, #188, #246 | Source-backed TP-flash gate exists; fresh-native receipts and broader reliability still open |
| PE-Generalized Multiphase | `held_1_admitted` with phase-count independence | #189 | Needs all-phase mass-balance termination and LLLE-ready phase-set completeness |
| PE-Associating TP Flash | `held_variant_required` | #145, #190 | Do not start until neutral pre-association HELD parity gates and exact association derivatives are ready |
| PE-Electrolyte LLE/TP Flash | `held_variant_required` | #191 | Needs HELD2.0, reduced electroneutral basis, and Born SSM+DS exact Hessian |
| CE Chemical Equilibrium | `outside_phase_discovery` | future CE work | Must not borrow HELD completion language |
| CPE Combined Phase-Chemical | `held_variant_required` for phase part plus CE proof | future CPE work | Depends on PE and CE proof chains |

## Pre-Associating HELD 1.0 Gates

These gates define the sequence that should be planned before #145/#190 begins
implementation work.

### Gate A - Fresh-Native Evidence Receipts

Issue coverage: #246, ready.

Purpose:

- prevent stale native extensions from producing false HELD status;
- record commit, native module path, build-refresh command or freshness proof,
  checker command, and pass/fail result;
- ensure retained plots and CSV/JSON evidence are regenerated from the same
  native artifact that produced the status rows.

Completion of #246 is a proof-hygiene prerequisite, not a new algorithmic
Pereira requirement.

### Gate B - Pereira-Style Neutral HELD Reliability Harness

Issue coverage: #247.

Purpose:

- stress Stage I and Stage II on random unstable neutral conditions;
- repeat point calculations without carrying hidden initial guesses between
  repeats;
- compare phase count, objective/free-energy value, material balance,
  candidate set, and postsolve certification across repeats;
- retain inner-search diagnostics sufficient to show how local minima,
  incumbent upper bounds, and rejected candidates were handled.

Retained evidence:

- `analyses/package_validation/held_lle_reliability/shared/results/held_lle_reliability_summary.json`
- `analyses/package_validation/held_lle_reliability/shared/results/held_lle_reliability_conditions.csv`
- `analyses/package_validation/held_lle_reliability/shared/results/held_lle_reliability_repeats.csv`

Gate B is complete only when the retained summary JSON reports
`complete: true`, `accepted_conditions: 100`, `attempted_repeats: 10000`, and
`failed_repeats: 0`.

Minimum acceptance:

- the reliability driver samples only neutral, nonelectrolyte, nonreactive
  conditions with declared parameter sources;
- unstable cases are identified before repeated flash attempts are counted;
- repeated solves do not reuse hidden initial guesses or prior phase sets;
- retained output records Stage I converged-start counts, Stage II bound
  history, upper/lower bound gap, candidate phases, rejected candidates, Stage
  III seed source, Ipopt status, material balance, phase count, and objective
  agreement;
- a failed repeat is loud and carries the first failing condition as a compact
  reproduction fixture;
- no associating, electrolyte, reactive, CE, CPE, or capability broadening
  occurs in this issue.

Proof candidates:

```powershell
uv run --no-sync python scripts/dev/build_epcsaft.py --profile equilibrium --build-only --parallel 4
uv run --no-sync python scripts/validation/check_phase_discovery.py --json --include-route-refinement --require-complete
uv run --no-sync python scripts/validation/check_held_reliability.py --family neutral-lle --conditions 100 --repeats 100 --seed 1729 --require-complete --json --output-dir analyses/package_validation/held_lle_reliability/shared/results
uv run --no-sync python scripts/dev/validate_project.py docs
```

### Gate C - Source-Backed Neutral Nonassociating LLE Showcase

Spec coverage:
`docs/superpowers/specs/2026-06-11-m4-equilibrium-neutral-nonassociating-lle-source-backed-showcase.md`.

Purpose:

- show neutral LLE without association, electrolyte, or reaction terms;
- use source-backed data rather than the synthetic A/B mechanics fixture;
- produce retained-data figures and diagnostic margin evidence.

This is the LLE showcase needed before associating LLE can be framed as an
extension of the neutral phase-split path.

Retained evidence after #250:

- `data/reference/equilibrium_benchmarks/neutral_lle/perfluorohexane_hexane`
- `scripts/validation/check_neutral_lle_showcase.py`
- `packages/epcsaft-equilibrium/tests/api/test_neutral_lle_showcase_fixture.py`
- `analyses/package_validation/neutral_nonassociating_lle_showcase`

Gate C remains one binary source-backed showcase. It does not prove
phase-count independence, generalized phase-set completion, associating LLE,
electrolyte LLE, reactive PE, CE, or CPE behavior.

### Gate D - Generalized All-Phase And LLLE-Ready Phase-Set Completeness

Issue coverage: #189 should own this unless planning decides to split it.

Purpose:

- prove phase-count independence rather than repeated two-phase solving;
- enforce the Pereira mass-balance termination idea: the algorithm cannot call
  phase discovery complete while the candidate phase set cannot satisfy the
  global feed balance;
- reject duplicate, collapsed, lower-free-energy, and uncertified phase sets;
- preserve the difference between neutral LLLE readiness and associating LLLE
  admission.

Recommended #189 expansion:

- boundary workflows remain derived degree-of-freedom swaps;
- generalized phase-set PE carries phase count, phase kind, source, amount,
  volume, composition, objective, feasibility, candidate origin, and status;
- LLLE-ready tests may use neutral systems only until associating derivatives
  are admitted;
- the issue must not claim associating GFPE completion.

### Gate E - Associating GFPE Preparation

Issue coverage: #145 and #190.

Purpose:

- make associating GFPE a controlled extension of the neutral HELD path, not a
  parallel shortcut;
- require exact association derivatives before associating route admission;
- require association-specific postsolve checks for site bounds, mass-action
  residuals, contribution activation, and derivative block coverage.

Start condition:

- #246 complete;
- Gate B reliability harness accepted or explicitly scoped as the first child
  of #190;
- #189 has either completed generalized all-phase readiness or documented why
  the first associating proof is a strictly two-phase route that cannot claim
  generalized phase-set adoption;
- exact association derivative evidence exists for the selected first source
  system.

## Recommended Planning Shape

### Option A - Update Existing Specs And Create One Reliability Issue

Use this spec as the umbrella, #246 as the immediate ready issue, the neutral
LLE showcase spec as the source-backed LLE issue source, #189 as the generalized
phase-set owner, and one new reliability issue for Pereira-style inner-search
and repeated-condition receipts.

Recommendation: use Option A.

Tradeoff:

- Keeps the current M4 queue readable.
- Adds only one missing issue instead of making #189 or #190 carry reliability
  work they do not naturally own.

### Option B - Fold Reliability Into #189

Expand #189 so it owns boundary workflows, generalized phase sets, LLLE
readiness, and the reliability campaign.

Tradeoff:

- Fewer issue objects.
- Too broad for one PR if reliability failures expose algorithm work.

### Option C - Defer Reliability Until Associating

Run the current neutral proof lane into #190 and add reliability only when
associating failures appear.

Tradeoff:

- Faster start on associating.
- High risk of mixing neutral algorithm gaps with association derivative gaps,
  making failures harder to diagnose.

## Non-Goals

- No source implementation in this spec.
- No new public route exposure from this spec.
- No associating, electrolyte, reactive, CE, or CPE admission from neutral HELD
  evidence.
- No capability or benchmark promotion from closed issue state alone.
- No broad issue closure by documenting remaining work.
- No downstream application metrics, wrappers, or private project behavior.

## Open Questions For Planning

- Should the Pereira-style reliability issue sample only the existing
  source-backed TP-flash fixture neighborhood first, or include a second neutral
  stress fixture such as methane/H2S only after model-parity constraints are
  resolved?
- Should #189 be split into boundary workflows and generalized phase-set
  completeness if the first planning pass shows overlapping candidate files or
  validation costs are too high?
- Should the first associating plan depend on completed generalized phase-set
  #189, or can it start as a two-phase associating route after explicitly
  excluding generalized phase-set claims?

## Self-Review

- Placeholder scan: no unresolved placeholders remain.
- Scope check: this is a broad adoption spec, but execution is split into #246,
  one recommended reliability issue, the neutral nonassociating LLE showcase,
  #189, #145/#190, #191, and #192.
- Ambiguity check: current neutral Stage II/III status is separated from full
  Pereira-style adoption.
- Capability check: no family or method receives a new production claim from
  this document.
