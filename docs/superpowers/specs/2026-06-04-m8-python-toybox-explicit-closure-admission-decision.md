# Explicit Closure Admission Decision

Milestone: `M8 - Python Toybox`
Issue: `none`
Status: `draft`
Last synced: `2026-06-04`

## Summary

Create a toybox evidence decision spec that decides whether the retained Picard
closure remains the only explicit association candidate worth testing and what
must be true before any provider EOS admission work is allowed.

The likely current answer is conservative: Picard remains the only candidate
worth continuing, and no provider implementation should be attempted until
property and derivative error gates pass.

## Project Context Evidence Used

- `docs/superpowers/milestones/M8-python-toybox/README.md` defines toybox
  evidence as pre-admission work.
- `docs/superpowers/milestones/M3-eos/README.md` still lists #161 as the
  provider-facing explicit association closure design issue.
- `docs/superpowers/specs/2026-05-23-m3-eos-explicit-association-closure-for-pcsaft.md`
  says explicit closure derivatives are exact only for the approximate model.
- `docs/superpowers/specs/2026-06-03-m3-eos-explicit-association-derivative-property-propagation-evidence.md`
  preserves the finding that `damped_picard_7_05` is the retained active
  approximation candidate.
- `docs/latex/explicit_assocation.tex` now derives only the full-matrix
  seven-step damped Picard closure and removes unrelated closure clutter.
- `docs/superpowers/specs/2026-06-04-m8-python-toybox-cppad-shaped-picard-property-derivative-evidence.md`
  defines the broad pure/mixture property and C++/CppAD-shaped derivative
  evidence lane that must be read before any provider admission claim.

## User Decisions

- Remove or ignore old diagonal-polish, collapsed-mean-field, and other
  non-retained closure lanes.
- Treat Picard as the only explicit association approximation candidate worth
  continuing for now.
- Do not promote Picard into provider EOS until property and derivative gates
  pass.
- Use M8 for toybox decision evidence; use M3 only when the decision becomes a
  provider implementation or provider-admission issue.

## Admission Decision Shape

The decision artifact should classify each closure family as:

```text
continue
historical_only
delete_from_toybox
provider_blocked
provider_candidate
```

Current expected classification:

| Closure family | Expected status | Reason |
| --- | --- | --- |
| Seven-step damped Picard | `continue` | Only retained approximation candidate with useful speed/accuracy tradeoff so far. |
| Exact implicit mass-action | `continue` | Reference baseline, not an approximation. |
| Huang/Radosz topology reductions | `continue` as validation baselines only | Exact only under source topology assumptions. |
| Diagonal polish variants | `historical_only` or `delete_from_toybox` | Did not clearly beat Picard accuracy/cost tradeoff. |
| Collapsed mean field | `delete_from_toybox` | Diagnostic-only and not provider plausible. |
| Other ad hoc closures | `delete_from_toybox` | Clutter unless a source-backed reason exists. |

## Provider Admission Gates

No M3 provider implementation should start until M8 evidence proves:

- bounded site fractions over source-backed topology rows;
- mass-action residual error stays within an agreed tolerance band;
- association `ares` error is acceptable over real associating systems;
- total neutral `ares` impact is physically small enough where claimed;
- pressure and density residuals do not hide root-selection failures;
- first and second derivative errors are acceptable for local EOS use;
- CppAD-shaped JAX proxy evidence has been compared against exact implicit
  baselines for pure and mixture association schemes, with JAX explicitly
  treated as a proxy rather than provider CppAD proof;
- equilibrium-style objective/Jacobian/Hessian probe does not show unstable
  derivative behavior.

## Relationship To Issue #161

This spec should eventually revise or supersede the design stance behind
provider issue #161. Until the toybox gates pass, #161 should remain a design
or admission issue rather than implementation-ready provider work.

## Non-Goals

- No provider implementation.
- No compatibility API aliases.
- No public package behavior changes.
- No equilibrium implementation.
- No benchmark admission.
- No old closure-family resurrection.

## Open Questions

- Should #161 be rewritten as a provider admission gate after M8 evidence
  lands, or should it be closed and replaced by a new M3 issue?
- What exact tolerance bands decide `provider_candidate` versus
  `provider_blocked`?
- Should the toybox retain historical rows in archived output, or delete
  non-retained closure code entirely?

## Proof Oracle Candidates For Later Planning

- `uv run python analyses/package_validation/explicit_association_toybox/scripts/summarize_results.py`
- `uv run python run_pytest.py analyses/package_validation/explicit_association_toybox/tests -q`
- `rg -n "collapsed|diagonal|mean_field|polish" analyses/package_validation/explicit_association_toybox`
