# Equilibrium Relevance Probe For Picard Closure Error

Milestone: `M8 - Python Toybox`
Issue: `none`
Status: `draft`
Last synced: `2026-06-04`

## Summary

Create a Python-only equilibrium-style probe that tests whether Picard
association closure error matters for objective, Jacobian, and Hessian quality
before any M4 equilibrium implementation work is proposed.

This is not an equilibrium route. It is a tiny diagnostic that consumes
provider-like EOS quantities from the toybox and asks whether explicit
association error would likely damage nonlinear-program derivative quality.

## Project Context Evidence Used

- `docs/superpowers/milestones/M8-python-toybox/README.md` allows
  equilibrium-style Python analysis while keeping production M4 implementation
  separate.
- `docs/superpowers/milestones/M4-equilibrium/README.md` keeps actual
  equilibrium route behavior, Ipopt contracts, and exact derivative policy in
  M4.
- `docs/superpowers/specs/2026-05-26-m4-equilibrium-generalized-fluid-phase-equilibrium.md`
  defines the production equilibrium architecture and exact derivative
  expectations.
- `docs/latex/explicit_assocation.tex` explains why the explicit Picard model
  offers a fixed algebraic graph for ordinary chain-rule derivatives, while
  exact association requires implicit sensitivities.
- `docs/superpowers/specs/2026-06-04-m8-python-toybox-picard-autodiff-and-exact-implicit-sensitivity-baseline-hardening.md`
  is the intended prerequisite derivative baseline for this probe.

## User Decisions

- Keep this as later M8 work, not immediate M4 implementation.
- Block the probe until the M8 EOS/property derivative side is good enough.
- Do not call the probe bubble, dew, flash, LLE, HELD, or GFPE.
- Use provider-like quantities and derivative shapes, not package route APIs.

## Recommended Probe Shape

Build a small local objective such as:

```text
phi(q) = ares_total(q) + pressure_weight * pressure_proxy(q)
```

where `q` is a compact vector containing local density, temperature, and
composition-like variables. Compare:

```text
phi_exact_implicit
phi_picard
grad_phi_exact_implicit
grad_phi_picard
hess_phi_exact_implicit
hess_phi_picard
```

The objective is deliberately synthetic. It exists only to expose whether the
Picard closure creates derivative errors that would be dangerous for
IPOPT-style optimization.

## Required Outputs

```text
case_id
topology_id
state_id
objective_value_exact
objective_value_picard
gradient_norm_exact
gradient_norm_picard
gradient_absolute_error_norm
hessian_frobenius_exact
hessian_frobenius_picard
hessian_absolute_error_norm
hessian_condition_indicator
picard_mass_action_residual_norm
admission_status
```

The probe should report qualitative admission bands:

```text
passes_probe
needs_more_evidence
fails_probe
blocked_by_missing_derivative_baseline
```

## Blocking Dependencies

This spec should wait for:

- derivative baseline rows from the Picard autodiff and exact implicit
  sensitivity spec;
- pressure-density/root solving proof from the associating-compound validation
  lane when pressure proxies are used;
- closure admission decision tolerances.

## Non-Goals

- No M4 route implementation.
- No Ipopt integration.
- No public equilibrium API.
- No HELD, GFPE, bubble, dew, flash, or LLE workflow.
- No provider implementation.
- No benchmark admission.

## Open Questions

- Which exact small objective best represents equilibrium derivative stress
  without becoming route-specific?
- Should Hessian comparison use full matrices, projected tangent-space blocks,
  or selected directional Hessian-vector products?
- What failure threshold should block any future M4 Picard closure experiment?

## Proof Oracle Candidates For Later Planning

- `uv run python analyses/package_validation/explicit_association_toybox/figures/equilibrium_relevance_probe/scripts/generate_data.py`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/equilibrium_relevance_probe/scripts/render_figure.py`
- `uv run python run_pytest.py analyses/package_validation/explicit_association_toybox/tests -q`
