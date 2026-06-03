# Explicit Association Closures For PC-SAFT

## Purpose

The exact PC-SAFT association model solves association site fractions `X_A`
from nonlinear mass-action equations. That is the thermodynamic reference
model, but it makes exact route Jacobians and Hessians more expensive because
`X_A` is a solved internal state.

This plan defines explicit reduced association closures for EOS diagnostics
and experimental associating-equilibrium work. The closures replace the solved
site fractions with algebraic expressions:

```text
X_A ~= X_A^approx(T, rho, x, parameters)
a_assoc^approx = a_assoc(X_A^approx)
```

CppAD may then differentiate the explicit expression directly. Those
derivatives are exact derivatives of the approximate Helmholtz model. They are
not exact PC-SAFT association derivatives unless the closure is proven to match
the exact mass-action solution.

The LaTeX-ready Stage 1 derivation lives at
`docs/derivation/explicit_association_closure_for_pcsaft.tex`. Keep that file
and this plan synchronized until the derivation is promoted into the main
equation source.

Use these labels consistently:

```text
implicit_exact:
    exact PC-SAFT association model
    X_A solved by mass action
    derivatives use implicit sensitivities or lifted X_A constraints

explicit_approx:
    approximate algebraic X_A model
    no nonlinear association solve
    CppAD derivatives are exact for the approximate model
```

## Source Basis

The package model is a residual Helmholtz EOS. Association is one contribution
family alongside hard-chain, dispersion, ionic, Born, and related electrolyte
terms. Fugacity coefficients, chemical potentials, pressure, and equilibrium
residuals ultimately depend on derivatives of that residual Helmholtz model.

Gross and Sadowski 2002 is the first target because it applies PC-SAFT to pure
associating components, VLE, and LLE. Its most useful staging fact is that
mixtures with only one associating compound do not require association mixing
rules; one binary `k_ij` for the dispersion term is used. That makes
one-associating-component VLE the safest first associating-equilibrium proof.

Chapman et al. and Huang/Radosz provide the SAFT association foundation:
association is represented by association site fractions, association energy,
and association volume. The current package equation ownership remains the
local LaTeX equation source and native association implementation, not this
plan.

Primary local references:

- `docs/latex/equations.tex`
- `docs/papers/md/ePC-SAFT-Literature/Gross, Sadowski - 2002 - Application of the PC-SAFT equation of state to associating systems.md`
- `docs/papers/md/ePC-SAFT-Literature/Huang and Radosz - 1990 - Equation of State for Small, Large, Polydisperse, and Associating Molecules.md`
- `docs/papers/md/Chapman et al. - 1989 - SAFT Equation-of-state solution model for associating fluids.md`
- `docs/papers/md/Chapman et al. - 1990 - Phase Equilibria in Polymer-Liquid 1-Liquid 2 Systems.md`

Related validation design:

- `docs/superpowers/specs/2026-06-03-m3-eos-paper-backed-association-closure-validation-matrix-design.md`

The validation-matrix spec extends this derivation policy with a paper-backed
analysis design for Huang/Radosz topology formulas, Gross/Sadowski associating
systems, closure timing, and fixed-state `ares` error comparisons. Do not treat
the first synthetic toybox grids as sufficient evidence for production
association-closure admission.

## Exact Association Model

Use a flattened site index `a`, where each site belongs to a component
`i(a)`. Let `w_b = x_i(b) * nu_b` be the site composition weight and let
`Delta_ab` be the association strength between site `a` and site `b`.

The exact mass-action equation is:

```math
X_a =
\frac{1}{1 + \rho \sum_b w_b X_b \Delta_{ab}}
```

Equivalently, define the residual:

```math
F_a(X; T, \rho, x, p)
= X_a \left(1 + \rho \sum_b w_b X_b \Delta_{ab}\right) - 1
```

The exact association contribution is:

```math
a^{assoc}
= \sum_i x_i \sum_{A \in i} \nu_{iA}
\left(\ln X_{iA} - \frac{X_{iA}}{2} + \frac{1}{2}\right)
```

The exact model solves `F(X) = 0`. Production exact association must not tape
the fixed-point iteration as the derivative model. It must eliminate `X_A`
with implicit sensitivities or lift `X_A` as route variables with exact
mass-action constraints.

## Closure A: One Associating Component, Two-Class 2B

This is the first closure to implement and the first one to test against Gross
2002 one-associating-component systems.

Assume:

- one associating component `s`;
- every other component is inert;
- the associating component has donor-like sites `D` and acceptor-like sites
  `A`;
- only donor-acceptor association is active.

Define:

```math
c_A = \rho x_s n_A \Delta_{DA}
```

```math
c_D = \rho x_s n_D \Delta_{DA}
```

The two coupled equations are:

```math
X_D = \frac{1}{1 + c_A X_A}
```

```math
X_A = \frac{1}{1 + c_D X_D}
```

Substitution gives:

```math
c_D X_D^2 + (1 + c_A - c_D) X_D - 1 = 0
```

The physical root is:

```math
X_D =
\frac{-(1 + c_A - c_D)
+ \sqrt{(1 + c_A - c_D)^2 + 4 c_D}}
{2 c_D}
```

Then:

```math
X_A = \frac{1}{1 + c_D X_D}
```

For symmetric 2B alcohol cases where `n_A = n_D`, set `c = c_A = c_D`:

```math
X_D = X_A = \frac{2}{1 + \sqrt{1 + 4c}}
```

Use this closure first for:

- methanol/isobutane;
- methanol/cyclohexane;
- ethanol/n-butane;
- 1-butanol/n-butane;
- 1-pentanol/benzene.

Expected status: exact or near-exact for one-associating-component 2B cases,
depending on the package's flattened site convention and site multiplicity.

## Closure B: Full-Matrix Fixed Unroll

This is the general explicit approximation for mixtures with multiple
associating components or more site types.

Define:

```math
K_{ab} = \rho w_b \Delta_{ab}
```

Then:

```math
X_a = \frac{1}{1 + \sum_b K_{ab} X_b}
```

Start with a quadratic row-sum initializer:

```math
S_a = \sum_b K_{ab}
```

```math
X_a^{(0)} = \frac{2}{1 + \sqrt{1 + 4 S_a}}
```

For fixed `m = 1, ..., N`, unroll Picard updates:

```math
\hat X_a^{(m)}
= \frac{1}{1 + \sum_b K_{ab} X_b^{(m-1)}}
```

Without damping:

```math
X_a^{(m)} = \hat X_a^{(m)}
```

With fixed damping:

```math
X_a^{(m)}
= (1 - \omega) X_a^{(m-1)} + \omega \hat X_a^{(m)}
```

Recommended experimental variants:

- `explicit_picard_unroll_1`
- `explicit_picard_unroll_3`
- `explicit_damped_picard_unroll_3`
- `explicit_damped_picard_unroll_5`

Default first candidate: `explicit_damped_picard_unroll_3` with
`omega = 0.5`.

This closure stays full-matrix and CppAD-recordable. It does not collapse all
association into one pseudo-component.

## Closure C: Picard Plus Diagonal Newton Polish

This is the strongest first candidate for the target "2-3 percent in
thermodynamic outputs with exact derivatives of the approximate model."

After three damped Picard updates, compute:

```math
F_a = X_a \left(1 + \sum_b K_{ab} X_b\right) - 1
```

Approximate the Newton denominator by the diagonal:

```math
D_a = 1 + \sum_b K_{ab} X_b + X_a K_{aa}
```

Apply one explicit damped correction:

```math
X_a^{approx}
= X_a - \lambda \frac{F_a}{D_a}
```

Recommended variant:

```text
explicit_picard3_diag_newton1
omega = 0.5
lambda = 0.5
```

This remains explicit, avoids a linear solve, preserves the full association
matrix, and can be taped directly as an approximate Helmholtz model.

## Closure D: Collapsed Donor/Acceptor Mean Field

This closure is useful for cheap diagnostics and seeds in water/alcohol-like
systems. It should not be the first production-like VLE candidate because it
erases component-specific site fractions.

Define:

```math
C_D = \sum_i x_i n_{iD}
```

```math
C_A = \sum_i x_i n_{iA}
```

```math
\Delta_{DA}^{eff}
=
\frac{\sum_i \sum_j x_i n_{iD} x_j n_{jA} \Delta_{iD,jA}}
{C_D C_A}
```

Then:

```math
a = \rho C_A \Delta_{DA}^{eff}
```

```math
b = \rho C_D \Delta_{DA}^{eff}
```

Reuse the two-class quadratic:

```math
X_D =
\frac{-(1 + a - b) + \sqrt{(1 + a - b)^2 + 4b}}
{2b}
```

```math
X_A = \frac{1}{1 + b X_D}
```

The approximate association contribution is:

```math
a_{assoc}^{approx}
= C_D \left(\ln X_D - \frac{X_D}{2} + \frac{1}{2}\right)
+ C_A \left(\ln X_A - \frac{X_A}{2} + \frac{1}{2}\right)
```

Use this closure only as:

- an approximate diagnostic;
- an initial value generator;
- a water/alcohol screening approximation.

## Derivative Policy

For `explicit_approx` association closures, CppAD records
`a_assoc^approx(T, rho, x, p)` directly. The route can then obtain exact
gradients, Jacobians, and Hessians of the approximate association model.

Required diagnostic labels:

```text
association_model = "explicit_approx"
association_closure = "explicit_picard3_diag_newton1"
derivative_backend = "cppad_explicit"
exact_derivative_of = "approximate_association_closure"
```

Do not label these outputs as `implicit_exact`. Do not claim exact PC-SAFT
association unless the closure is tested to satisfy the full mass-action
equations at the same tolerance as the exact solver.

Implementation policy: `explicit_approx` closures may initialize, diagnose, or
continue Ipopt routes, but a production accepted result remains
`implicit_exact` unless a separate route deliberately exposes the approximate
model and labels the returned status as approximate. A route that uses
`explicit_approx` in the final thermodynamic model must not report
`production_accepted`.

## Validation Metrics

Do not validate only site fractions. The phase solver cares about the
thermodynamic outputs that receive association derivatives.

Required metrics:

- `max_abs_X_error` against `implicit_exact`;
- `a_assoc` absolute and relative error;
- pressure error;
- residual chemical potential error;
- log fugacity coefficient error;
- mass-action residual infinity norm;
- bubble/dew pressure or temperature error when used in equilibrium;
- Ipopt iterations;
- `eval_h` calls;
- callback failures.

Target the 2-3 percent error band on pressure, fugacity, and
equilibrium-relevant outputs. A component site fraction may be outside that
band in a region where it has little phase-equilibrium impact, but the
diagnostic must report it.
