# Generalized Fluid-Phase Equilibrium Algorithm

## Doctrine Statement

The package equilibrium engine is a model-agnostic, activation-selected
thermodynamic constrained optimization framework for fluid-phase equilibrium.
The thermodynamic model is a provider. The core owns variables, constraints,
phase discovery, route activation, NLP assembly, derivative contracts,
postsolve certification, and result classification.

For fixed-`T`, fixed-`P` phase-split routes, the default production objective is
the pressure-transformed Helmholtz energy

```math
\Phi_{TP}
=
\sum_{\alpha \in \mathcal{A}}
\left[
A_\alpha(T^0,V_\alpha,n_\alpha,q_\alpha)
+P^0V_\alpha
\right],
```

subject to exact hard constraints and bounds. When a provider supplies a Gibbs
energy surface directly at fixed `T,P`, the equivalent objective is

```math
\Phi_G
=
\sum_{\alpha \in \mathcal{A}}
G_\alpha(T^0,P^0,n_\alpha,q_\alpha).
```

The two forms are related by the Legendre transform

```math
G(T,P,n)=\min_V [A(T,V,n)+PV],
```

with stationarity condition

```math
\frac{\partial A}{\partial V}+P=0,
\qquad
P_{\mathrm{EOS}}=-\frac{\partial A}{\partial V}=P.
```

Residual least-squares objectives are allowed only as route-declared
globalization, initialization, equation-solve, diagnostic, or certification
forms. Production acceptance is never based on optimizer status alone.

## Scope

This doctrine covers neutral VLE, neutral LLE, neutral TP flash, neutral
multiphase flash, associating VLE/LLE, strong-electrolyte LLE/VLLE, reactive
speciation, reactive VLE/LLE, and reactive electrolyte LLE. First
implementations may restrict public route exposure to two phases while
preserving the general state and certification form.

The package boundary remains generic thermodynamics infrastructure:

- `Equilibrium(mixture, route=..., ...)`
- `State(...)`
- `ParameterSet(...)`
- `TargetDataset(...)`
- future generic `ReactionSet(...)`

Do not add application-specific package APIs for lithium extraction metrics,
MEA absorption metrics, solvent screening, distribution coefficients, column
metrics, or paper-specific workflows.

This document does not make solid-liquid equilibrium, precipitation, hydrate
formation, kinetic reactors, transport, column discretization, or guaranteed
finite-time global optimization production targets. Those require separate
phase models, route specs, and ADR-level admission.

## Thermodynamic Provider Interface

For each phase `\alpha`, with phase kind `k_\alpha`, temperature `T`, volume
`V_\alpha`, mole vector `n_\alpha`, and internal state `q_\alpha`, the provider
must expose a phase-state interface.

State definitions:

```math
N_\alpha=\sum_i n_{i\alpha},
\qquad
x_{i\alpha}=\frac{n_{i\alpha}}{N_\alpha},
\qquad
\rho_\alpha=\frac{N_\alpha}{V_\alpha}.
```

Accepted provider modes:

- Helmholtz mode: `T,V,n,q`
- Gibbs mode: `T,P,n,q`
- pressure-root state mode: `T,P,x`

Pressure-root state mode is allowed for normal property calls and seed
construction. Production Ipopt routes should prefer explicit `V_\alpha` or
`\rho_\alpha` variables so the derivative contract does not hide a density-root
iteration inside a callback.

For Helmholtz mode, the provider supplies

```math
A_\alpha=A(T,V_\alpha,n_\alpha,q_\alpha),
```

```math
P_\alpha
=
-\left(
\frac{\partial A_\alpha}{\partial V_\alpha}
\right)_{T,n_\alpha,q_\alpha},
```

and

```math
\mu_{i\alpha}
=
\left(
\frac{\partial A_\alpha}{\partial n_{i\alpha}}
\right)_{T,V_\alpha,n_{j\ne i,\alpha},q_\alpha},
```

after accounting for internal-state closure. For Gibbs mode, the provider
supplies

```math
G_\alpha=G(T,P,n_\alpha,q_\alpha),
\qquad
\mu_{i\alpha}
=
\left(
\frac{\partial G_\alpha}{\partial n_{i\alpha}}
\right)_{T,P,n_{j\ne i,\alpha},q_\alpha}.
```

Where meaningful, the provider also supplies `\ln \phi_i`, `\ln f_i`,
`\ln a_i`, and `\ln \gamma_i`.

Internal variables are denoted by `q_\alpha`. Examples include association site
fractions, density roots, dielectric states, ion-pairing variables, homogeneous
speciation extents, and activity-model reference-state variables. The provider
must expose closure residuals

```math
F_\alpha^q(q_\alpha;T,V_\alpha,n_\alpha,p)=0.
```

For production derivative support, internal variables must be differentiated by
implicit sensitivities or lifted as explicit NLP variables with exact
constraint derivatives. Direct differentiation through an iterative internal
solve is not a production derivative path.

First-order implicit sensitivity:

```math
q_u = -\left(F_q^q\right)^{-1}F_u^q.
```

Production Ipopt routes must provide objective value, objective gradient,
constraint values, constraint Jacobian, and exact Lagrangian Hessian unless the
route explicitly declares a nonproduction or diagnostic limited-memory mode.
The provider must distinguish domain errors, unsupported phase kinds,
unsupported derivative paths, internal-state nonconvergence, and missing
parameters from ordinary solver failure.

## Canonical State

Let

```math
\mathcal{I}=\{1,\ldots,C\}
```

be the true-species set, and let

```math
\mathcal{A}=\{1,\ldots,\pi\}
```

be the active fluid-phase set. The canonical truth state is true species by
phase:

```math
N=\{n_{i\alpha}\}_{i\in\mathcal{I},\alpha\in\mathcal{A}}.
```

Every route-owned reduced variableization must lift into this state:

```math
N=\mathcal{T}_p(u).
```

Examples:

- neutral flash: phase amounts plus phase volumes
- bubble pressure: unknown pressure, incipient phase composition/amounts, and
  phase volumes
- electrolyte LLE: neutral species plus electroneutral reduced ionic variables
  plus volumes
- reactive speciation: conserved-basis variables or reaction extents
- reactive electrolyte LLE: phase amounts, reaction extents, electroneutral
  reduced variables, and volumes

Composition and totals are

```math
N_\alpha=\sum_i n_{i\alpha},
\qquad
x_{i\alpha}=\frac{n_{i\alpha}}{N_\alpha},
\qquad
n_{i\alpha}\ge 0.
```

The phase-eligibility mask

```math
M_{i\alpha}\in\{0,1\}
```

is structural. If `M_{i\alpha}=0`, then `n_{i\alpha}=0`. Phase restrictions
must not be enforced only through soft penalties.

## Objective Doctrine

For fixed `T,P` flash, LLE, and VLLE, use the dimensionless form

```math
\Phi_{TP}
=
\frac{1}{RT^0}
\sum_{\alpha}
\left[
A_\alpha(T^0,V_\alpha,n_\alpha,q_\alpha)
+P^0V_\alpha
\right].
```

If Gibbs energy is the natural provider output:

```math
\Phi_G
=
\frac{1}{RT^0}
\sum_\alpha G_\alpha(T^0,P^0,n_\alpha,q_\alpha).
```

Bubble/dew routes are route-specific reductions. They may use a thermodynamic
objective with hard route constraints, a square residual system that is
explicitly documented as the mathematical route formulation, or a hybrid with
thermodynamic objective plus residual certification. The project default is:
use the thermodynamic objective when phase amounts and volumes are active
variables, and use fugacity/chemical-potential residuals as hard constraints or
certification rows.

Residual objective form:

```math
\Phi_{\mathrm{res}}(u)
=
\frac{1}{2}\|W_r r_p(u)\|_2^2
+\frac{\eta_s}{2}\|W_s(u-u^{(0)})\|_2^2.
```

Allowed uses are seed polishing, homogeneous speciation solves, globalization,
diagnostic comparisons, and route formulations that explicitly declare equation
solving as the production mathematics. Do not silently replace the
thermodynamic objective for phase-split production routes, and do not accept a
result merely because a residual least-squares objective is small. Final
production phase-split solves should set `\eta_s=0` unless the route
documentation explicitly states otherwise.

## Constraint Doctrine

Nonreactive material balance:

```math
c_i^{\mathrm{mat}}(N)
=
\sum_\alpha n_{i\alpha}-n_i^F=0.
```

Reactive element or moiety balance:

```math
c^{\mathrm{cons}}(N)
=
A_{\mathrm{cons}}\operatorname{vec}(N)-b=0.
```

The conserved-basis matrix must be rank-reduced before production use.

Bounds:

```math
n_{i\alpha}\ge 0,
\qquad
N_\alpha>0,
\qquad
V_\alpha>0.
```

Trace-species lower bounds or log-variable transforms must be reported because
they affect certification.

For fixed pressure:

```math
c_\alpha^P
=
P_{\mathrm{EOS},\alpha}(T,V_\alpha,n_\alpha,q_\alpha)-P^0=0.
```

For unknown common pressure:

```math
c_{\alpha\beta}^P=P_\alpha-P_\beta=0.
```

Route specifications such as fixed `T`, fixed `P`, fixed feed `z`, fixed
liquid composition for bubble routes, fixed vapor composition for dew routes,
unknown scalar pressure, unknown scalar temperature, phase labels, and
phase-count caps are hard constraints or fixed variables.

Electrolyte phases must satisfy phase electroneutrality:

```math
z^T n_\alpha=0.
```

Strong-electrolyte production routes should enforce electroneutrality
structurally through reduced variables where possible.

For reaction `r`, with stoichiometric coefficients `\nu_{i\alpha r}`, reaction
affinity is

```math
\mathcal{A}_r
=
\sum_{\alpha,i}\nu_{i\alpha r}\mu_{i\alpha}.
```

The dimensionless reaction residual is

```math
c_r^{\mathrm{rxn}}
=
\frac{\mathcal{A}_r}{RT}=0.
```

If standard-state reaction constants are explicit, use

```math
c_r^{\mathrm{rxn}}
=
\ln Q_r-\ln K_r(T,P)=0.
```

For activity-based homogeneous reactions:

```math
\ln Q_r
=
\sum_i \nu_{ir}\ln(x_i\gamma_i).
```

If association site fractions are lifted, add exact mass-action constraints:

```math
F_a(X;T,\rho,x,p)
=
X_a
\left(
1+\rho\sum_b w_bX_b\Delta_{ab}
\right)-1=0.
```

Lifted internal-state constraints must provide exact Jacobian and Hessian rows.

A phase-distance constraint may be used as an anti-collapse gate:

```math
d_{\alpha\beta}
=
\|x_\alpha-x_\beta\|_\infty
\ge \tau_{\mathrm{split}}.
```

This is not a thermodynamic equilibrium equation. It is a route-specific
noncollapse, candidate-distinctness, or certification device and must be
labeled as such.

## KKT Mapping

For neutral nonreactive fixed `T,P` equilibrium in Gibbs form:

```math
\min_{\{n_{i\alpha}\}}
\sum_\alpha G_\alpha(T,P,n_\alpha)
```

subject to

```math
\sum_\alpha n_{i\alpha}=n_i^F.
```

The Lagrangian is

```math
\mathcal{L}
=
\sum_\alpha G_\alpha
+\sum_i\lambda_i
\left(n_i^F-\sum_\alpha n_{i\alpha}\right).
```

Stationarity gives

```math
\mu_{i\alpha}-\lambda_i=0,
```

so transferable species satisfy

```math
\mu_{i\alpha}=\mu_{i\beta}
\qquad
\forall i,\alpha,\beta,
```

or equivalently

```math
\ln f_{i\alpha}-\ln f_{i\beta}=0.
```

For Helmholtz form, stationarity with respect to `V_\alpha` gives mechanical
equilibrium:

```math
P_\alpha=P^0
```

for pressure-specified routes, or `P_\alpha=P_\beta` for unknown common
pressure.

For electrolyte routes, never compare raw ionic chemical potentials across
phases as if ions were neutral species. Use reduced electrochemical
potentials, charge-projected chemical-potential differences, mean ionic
combinations, or a route-owned electroneutral transformed basis.

If a charged reference species `r` is eliminated,

```math
n_{r\alpha}
=
-\sum_{i\ne r}\frac{z_i}{z_r}n_{i\alpha},
```

the reduced electrochemical potential is

```math
\mu_{i\alpha}^{el}
=
\mu_{i\alpha}
-\frac{z_i}{z_r}\mu_{r\alpha}.
```

The charged-species equilibrium residual is

```math
r_i^{el,\alpha\beta}
=
\mu_{i\alpha}^{el}-\mu_{i\beta}^{el}.
```

For reactions, the KKT condition is zero reaction affinity or the documented
standard-state form `\ln Q_r-\ln K_r=0`.

## Neutral HELD/TPD Phase Discovery

The phase-discovery layer is shared infrastructure, not a public route. It
must detect instability, generate candidate daughter phases, estimate phase
count, rank candidate phase sets, build Ipopt initial variables, certify
accepted results, and identify metastable or unstable phase sets.

HELD-style discovery reduces dependence on user-supplied phase guesses. It does
not remove the need for deterministic seeds, multistart or candidate search,
continuation, candidate ranking, and postsolve stability certification.

For a reference phase `z` at `T,P`, define dimensionless chemical potentials

```math
\hat{\mu}_i(z)=\frac{\mu_i(T,P,z)}{RT}.
```

For trial composition `w`, with `\sum_i w_i=1`,

```math
\mathrm{TPD}(w;z)
=
\sum_i w_i
\left[
\hat{\mu}_i(w)-\hat{\mu}_i(z)
\right].
```

A phase is stable if

```math
\min_{w\in\Delta}\mathrm{TPD}(w;z)
\ge -\tau_{\mathrm{TPD}}.
```

If the minimum is less than `-\tau_{\mathrm{TPD}}`, the minimizing `w` is a
candidate daughter phase.

For EOS models, a volume-composition trial problem avoids pressure-root
fragility. Let `v` be molar volume and `a(T,v,w)` be molar Helmholtz energy.
Define

```math
h(T,P^0,w,v)=a(T,v,w)+P^0v.
```

A supporting-plane trial problem may be written as

```math
\Theta(w,v;\lambda)
=
\frac{h(T,P^0,w,v)}{RT}
-\lambda_0
-\sum_{i=1}^{C-1}\lambda_iw_i,
```

with bounds on `w` and `v`. Candidate phases are minimizers that lie on or
below the current supporting plane.

Deterministic seed hierarchy:

1. previous continuation state
2. HELD/TPD negative-minimum candidates
3. pure-component and near-pure-component trial points
4. deterministic composition lattice
5. Wilson/K-value or volatility-based VLE guesses where meaningful
6. shifted-feed liquid-liquid guesses
7. binary extreme guesses
8. route-specific backup seed generators

Do not call backup seed generation a production fallback solver.

Candidate phases `p` and `q` are duplicates if

```math
\|x^{(p)}-x^{(q)}\|_\infty<\tau_x
```

and

```math
|\ln v^{(p)}-\ln v^{(q)}|<\tau_v.
```

Keep the candidate with lower transformed free energy and better domain
diagnostics.

Given candidate compositions `x^{(k)}`, solve phase-fraction feasibility:

```math
\sum_k\beta_k x_i^{(k)}=z_i,
\qquad
\sum_k\beta_k=1,
\qquad
\beta_k\ge 0.
```

If the mass-balance residual

```math
\delta_{\mathrm{mb,cand}}=\|X\beta-z\|_\infty
```

does not pass, phase discovery is incomplete.

For a multiphase result, certification must check at least:

1. each accepted phase is locally stable against an additional phase;
2. the accepted phases share the correct common tangent or supporting
   hyperplane;
3. the candidate set is mass-balance complete and no lower-free-energy phase set
   has been found.

Current implementation work should start with two-phase neutral flash/LLE and
keep the general algorithm documented for later multiphase routes. Until full
HELD/TPD discovery exists, results should label the discovery backend as
`deterministic_seed_sweep` and stability certification as `not_available` or
`postsolve_local_only`. Once available, accepted production results should
report `phase_discovery_backend = "held_tpd_volume_composition"` and
`stability_certificate = "tpd_postsolve"`.

## Electrolyte Extension

Strong electrolytes are represented as true dissociated ions unless a route
explicitly declares an apparent salt variableization and exact back-lift.
Every electrolyte phase and every electrolyte trial phase must satisfy
electroneutrality:

```math
z^Tn_\alpha=0.
```

Do not run neutral TPD over unconstrained ionic composition space.

Ascani-style cation-anion pair variables use charge-balanced increments. For a
cation `c` and anion `a`,

```math
z_c\Delta n_{c\alpha}+z_a\Delta n_{a\alpha}=0.
```

Stacking independent pair and neutral variables gives

```math
n_\alpha=B_{\mathrm{pair}}s_\alpha,
\qquad
z^Tn_\alpha=0.
```

This is useful for mixed salts, common ions, and mean ionic residuals.

Perdomo-style reduced electroneutral coordinates eliminate one charged
reference species `r`:

```math
n_{r\alpha}
=
-\sum_{i\ne r}\frac{z_i}{z_r}n_{i\alpha}.
```

The constrained phase free energy is

```math
G_\alpha^{el}(T,P,n_\alpha^{(r)})
=
G_\alpha(T,P,n_\alpha(n_\alpha^{(r)})).
```

The reduced electrochemical potentials are

```math
\mu_{i\alpha}^{el}
=
\mu_{i\alpha}
-\frac{z_i}{z_r}\mu_{r\alpha}.
```

Use this when formal strong-electrolyte TPD and HELD2.0-style phase discovery
are primary. In composition space, the independent electrolyte TPD domain is

```math
\Omega^{el}
=
\{x\ge0:\sum_i x_i=1,\ z^Tx=0\}.
```

Using reduced coordinates `y`,

```math
\mathrm{TPD}^{el}(y;y^0)
=
g^{el}(y)-g^{el}(y^0)
-\nabla g^{el}(y^0)^T(y-y^0),
```

with stability condition

```math
\min_{y\in\Omega^{el}}\mathrm{TPD}^{el}(y;y^0)
\ge -\tau_{\mathrm{TPD}}.
```

Do not assume ions are absent from vapor or organic phases unless phase
eligibility says so. Allowed strategies include log mole-number variables,
positive lower floors with reported tolerances, charge-neutral paired
perturbations, and reduced-coordinate bounds from electroneutrality.

For salt `m` with cation `c`, anion `a`, and stoichiometric coefficients
`\nu_c,\nu_a`, a mean ionic chemical-potential combination is

```math
\mu_{\pm,m,\alpha}
=
\frac{\nu_c\mu_{c\alpha}+\nu_a\mu_{a\alpha}}
{\nu_c+\nu_a}.
```

Mean ionic residuals are useful for pair formulations but do not replace full
reduced electrochemical certification when multiple independent ions and common
ions are present.

## Reactive Extension

Reactive systems use true species unless a route explicitly declares an
apparent variableization with exact lift to true species. Let `E` be the
element or moiety matrix:

```math
E\in\mathbb{R}^{B\times C}.
```

The conserved inventory is

```math
b=En^F,
```

and multiphase reactive equilibrium requires

```math
\sum_\alpha En_\alpha=b.
```

Two variableizations are allowed:

- nonstoichiometric: variables are true species `n_{i\alpha}` with conserved
  element/moiety balances and reaction-affinity stationarity;
- stoichiometric: variables are extents `\xi_r`, with exact lift from feed to
  true species.

For phase-transfer reactions and extraction complexes, the framework must
support both same-species transfer residuals and cross-phase reaction residuals
in the same problem. Identical neutral species present in both phases use
chemical-potential or fugacity equality. Species that transform across phases
use reaction affinity rows.

Ascani 2023 is a useful reactive neutral CPE/LLE reference. It is not a
complete reactive-electrolyte LLE framework and must not be cited as proof that
reactive electrolyte equilibrium is solved.

## Association Extension

Exact PC-SAFT association remains the thermodynamic reference. With flattened
association site `a`, site weight `w_b`, and association strength
`\Delta_{ab}`,

```math
X_a
=
\frac{1}
{1+\rho\sum_b w_bX_b\Delta_{ab}}.
```

Residual form:

```math
F_a(X;T,\rho,x,p)
=
X_a
\left(
1+\rho\sum_b w_bX_b\Delta_{ab}
\right)-1=0.
```

Association Helmholtz contribution:

```math
a^{\mathrm{assoc}}
=
\sum_i x_i\sum_{A\in i}\nu_{iA}
\left(
\ln X_{iA}
-\frac{X_{iA}}{2}
+\frac{1}{2}
\right).
```

Production option A is eliminated exact association: solve `F(X)=0` inside the
provider and use implicit sensitivities. Required diagnostics include
`association_model = "implicit_exact"`, sensitivity backend, solve convergence,
mass-action residual norm, and site count.

Production option B is lifted exact association: include `X_{a\alpha}` in
Ipopt variables and add exact mass-action constraints. The lifted route must
provide exact Jacobian rows, exact Hessian rows, association objective Hessian
terms, site-component ownership metadata, and association-delta dependency
contracts.

Nonproduction option C is explicit approximate association:

```math
X_a \approx X_a^{\mathrm{approx}}(T,\rho,x,p),
\qquad
a^{\mathrm{assoc,approx}}=a^{\mathrm{assoc}}(X^{\mathrm{approx}}).
```

Allowed uses are seed generation, phase-discovery acceleration, continuation,
diagnostic comparison, and explicit experimental routes that are labeled
approximate. Required metadata:

```text
association_model = "explicit_approx"
association_closure = "<closure_name>"
derivative_backend = "cppad_explicit"
exact_derivative_of = "approximate_association_closure"
production_thermodynamic_model = false
```

Never report explicit approximate association as exact PC-SAFT association
unless the closure satisfies mass action at the same tolerance as the exact
solve.

Associating LLE is blocked until all of these pass:

1. neutral HELD/TPD phase discovery and full phase-set stability certification;
2. exact associating EOS values and derivatives;
3. at least one narrow one-associating-component `bubble_pressure` proof;
4. at least one additional associating VLE proof;
5. explicit approximate closures labeled as approximate diagnostics only.

## Activation Matrix Doctrine

The activation matrix is admission control, not a wish list. Each row should
declare:

- key and display name
- public routes
- production exposure and exposure status
- knowns and unknowns
- phase-count policy and phase kinds
- species-eligibility policy
- variable model and objective family
- density backend
- internal-state strategy
- phase-discovery backend and seed generators
- residual families
- constraint families
- certification families
- derivative requirement
- proof routes and benchmark evidence
- negative tests

Route-family defaults:

| Family | Objective | Variables | Discovery | Required certification |
| --- | --- | --- | --- | --- |
| `neutral_tp_flash` | `A+PV` | phase amounts plus volumes | HELD/TPD after the next roadmap step | material, pressure, fugacity, TPD, noncollapse |
| `neutral_lle` | `A+PV` | phase amounts plus volumes | HELD/TPD required before associating LLE | material, pressure, fugacity, TPD, phase distance |
| `bubble_dew_derived_routes` | route-specific `A+PV` or residual constraints | incipient phase plus scalar `P/T` plus volumes | route-seeded | fixed composition, pressure, fugacity, noncollapse |
| `electrolyte_lle` | constrained `A+PV` or `G^{el}` | electroneutral reduced variables plus volumes | electrolyte TPD | material, charge, reduced electrochemical potentials, TPD |
| `reactive_speciation` | `G` or residual stationarity | true species or extents | optional homogeneous stability | element balance, reaction affinity |
| `reactive_lle` | `A+PV` or `G` | true species by phase plus extents if used | reactive TPD | element, pressure, transfer, reaction, TPD |
| `reactive_electrolyte_lle` | constrained `A+PV` or `G^{el}` | true species, electroneutral reduced variables, reaction variables | electrolyte/reactive TPD | element, charge, reduced electrochemical, reaction, TPD |

A route may be production-exposed only if the native route exists, the public
API reaches it through the selector, activation metadata matches route
diagnostics, exact gradient and Jacobian exist, exact Hessian exists or the
route is explicitly nonproduction, postsolve certification passes, stability
certification is implemented or the route is labeled not globally certified,
proof tests pass, negative tests prevent accidental broadening, and
capabilities do not overclaim.

## Final Ipopt Solve

For two-phase neutral flash/LLE:

```math
u=
[n_{1,1},\ldots,n_{C,1},V_1,
 n_{1,2},\ldots,n_{C,2},V_2].
```

For `p` phases, repeat the phase amount and volume block for each phase.
Additional variables may include `T`, `P`, reaction extents, association
fractions, reduced electrolyte variables, and phase fractions.

The standard NLP form is

```math
\min_u \Phi_p(u)
```

subject to

```math
c_p(u)=0,
\qquad
g_p(u)\ge0,
\qquad
\ell_p\le u\le u_p^U.
```

Recommended dimensionless scaling:

- amounts: `n_i/N_feed`
- volumes: `V/(N_feed/rho_ref)`
- objective: `Phi/(RTN_feed)`
- chemical potentials: `mu/(RT)`
- pressure residual: `(P_EOS-P)/max(P,P_ref)`
- reaction residual: affinity divided by `RT`
- charge residual: `z^Tn/N_feed`
- association residual: raw dimensionless mass-action residual

Bounds must be route-specific and reported. For trace electrolytes, prefer log
variables or electroneutral pair variables over arbitrary independent tiny mole
lower bounds.

Warm-start metadata must include seed name, seed source, phase-discovery
backend, continuation stage, and internal-state strategy. Production Ipopt
routes must report exact gradient, exact Jacobian, exact Hessian, Hessian
backend, `eval_h` calls, derivative backend, and implicit sensitivity backend
where relevant.

## Postsolve Certification

Optimizer success is not acceptance. A production result must certify:

Conservation:

```math
\delta_{\mathrm{cons}}
=
\|A_{\mathrm{cons}}\operatorname{vec}(N)-b\|_\infty.
```

Nonreactive material balance:

```math
\delta_{\mathrm{mat}}
=
\left\|\sum_\alpha n_\alpha-n^F\right\|_\infty.
```

Pressure:

```math
\delta_P
=
\max_\alpha
\left|
\frac{P_\alpha-P^0}{P_{\mathrm{scale}}}
\right|.
```

Neutral fugacity:

```math
\delta_f
=
\max_{i,\alpha,\beta}
|\ln f_{i\alpha}-\ln f_{i\beta}|.
```

Electrolyte charge:

```math
\delta_z
=
\max_\alpha
\left|
\frac{z^Tn_\alpha}{N_\alpha}
\right|.
```

Reduced electrochemical residual:

```math
\delta_\mu^{el}
=
\max_{i,\alpha,\beta}
\left|
\left(
\frac{\mu_{i\alpha}}{RT}
-\frac{z_i}{z_r}\frac{\mu_{r\alpha}}{RT}
\right)
-
\left(
\frac{\mu_{i\beta}}{RT}
-\frac{z_i}{z_r}\frac{\mu_{r\beta}}{RT}
\right)
\right|.
```

Reaction residual:

```math
\delta_{\mathrm{rxn}}
=
\max_r
\left|
\sum_{\alpha,i}
\nu_{i\alpha r}
\frac{\mu_{i\alpha}}{RT}
-\ln K_r
\right|.
```

If `K_r` is embedded in standard chemical potentials, omit the explicit
`\ln K_r` term and document the convention.

TPD stability:

```math
\delta_{\mathrm{TPD},\alpha}
=
\min_w \mathrm{TPD}(w;x_\alpha).
```

Stable requires

```math
\delta_{\mathrm{TPD},\alpha}\ge -\tau_{\mathrm{TPD}}.
```

Electrolyte phases use the reduced electrolyte TPD over `\Omega^{el}`.

Phase distinctness:

```math
d_{\alpha\beta}
=
\max_i |x_{i\alpha}-x_{i\beta}|.
```

Association internal-state residual:

```math
\delta_X=\|F(X)\|_\infty.
```

Production results must include accepted flag, status, rejection reason,
objective, constraint norms, postsolve norms, phase labels, phase amounts,
phase compositions, phase volumes, phase densities, derivative metadata, phase
discovery metadata, stability metadata, and association/electrolyte/reaction
diagnostics when applicable.

## Result Status Taxonomy

Use exact status semantics:

- `production_accepted`: finite solver output, hard constraints pass,
  postsolve residuals pass, stability certification passes, phase distinctness
  passes, derivative contract satisfied, route is production-exposed, and no
  diagnostic-only model was used in the final accepted solve.
- `optimizer_converged_uncertified`: Ipopt converged, but at least one
  certification block is missing or was not run.
- `postsolve_rejected`: finite point returned, but one or more residuals failed.
- `unstable`: local residuals pass, but a negative TPD candidate remains.
- `metastable`: local KKT/residuals pass, but a lower-free-energy candidate
  phase set is found.
- `approximate_diagnostic_only`: final solve used an approximate thermodynamic
  model such as `explicit_approx` association.
- `blocked_missing_derivative`: exact derivative coverage required by the route
  is missing.
- `blocked_not_exposed`: activation row exists, but production exposure is
  false.
- `failed_domain`: thermodynamic provider left its valid domain.
- `failed_solver`: optimizer failed and no finite certifiable candidate was
  produced.

## Staged Implementation Roadmap

Stage 0: roadmap/code reconciliation.

- Replace residual-NLP language with thermodynamic constrained NLP language.
- Align docs with current neutral LLE production exposure and restrictions.
- Update activation metadata expectations and algorithm registry entries.

Stage 1: neutral HELD/TPD phase discovery. Tracking issue: GitHub #148.

- Add a neutral TPD evaluator.
- Add a volume-composition trial-phase evaluator using existing EOS phase
  blocks.
- Add candidate generation, de-duplication, mass-balance selection, and
  postsolve TPD certification.
- Add activation metadata fields for phase discovery and certification.
- Add tests proving optimizer success alone is not accepted.
- Do not add new public routes.

Stage 2: neutral multiphase generalization.

- Extend two-phase candidate infrastructure toward internal LLLE/VLLE support.
- Add phase-count discovery diagnostics.

Stage 3: associating EOS and derivative proof.

- Prove exact association residual diagnostics and implicit first/second
  sensitivities.
- Run EOS-level Gross/Sadowski 2002 checks.
- Keep explicit approximate closures diagnostic only.

Stage 4: narrow associating VLE admission.

- Admit only neutral, nonelectrolyte, nonreactive `bubble_pressure` with at most
  one associating component and exact Hessian evidence.
- First proof: Gross/Sadowski 2002 methanol/isobutane.
- Keep associating LLE blocked.

Stage 5: additional associating VLE.

- Add a second one-associating-component VLE proof such as pentanol/benzene or
  propanol/benzene.
- Consider bubble-temperature only after the isothermal route is stable.

Stage 6: associating neutral LLE.

- Start only after Stages 1, 3, 4, and 5 pass.
- Candidate targets: methanol/cyclohexane, then water/butanol or
  water/isobutanol.

Stage 7: strong-electrolyte LLE.

- Implement true-ion species, phase electroneutrality, Ascani pair variables,
  Perdomo reduced-coordinate TPD, distributed ions, and trace-ion handling.

Stage 8: reactive speciation and reactive neutral LLE.

- Implement true-species reaction sets, reaction-constant conventions,
  homogeneous speciation, and reactive LLE with phase transfer.

Stage 9: reactive electrolyte LLE.

- Combine electrolyte reduced variables, phase electroneutrality, reaction
  affinities, cross-phase reactions, true species by phase, and HELD/TPD
  discovery.

Stage 10: benchmark and downstream smoke gates.

- Turn source-backed benchmarks into executable tests or scripts with
  tolerances. Inventories alone are not benchmark completion.

## Full-Flow Pseudocode

```text
solve_equilibrium(request):
    normalize public request
    classify system:
        neutral / electrolyte / reactive / reactive-electrolyte
        associating / nonassociating
        phase-restricted / unrestricted
    load activation row for requested route
    require production exposure for public production solve
    build species metadata:
        true species
        charges
        phase eligibility mask
        component or element matrix
        reaction set
        transferable species set
        internal-state requirements
    build route spec:
        knowns
        unknowns
        phase kinds
        route scalar variables
        objective family
        constraint families
        certification families
    build route-owned variableization:
        choose u
        define lift N = T_p(u)
        define volume or density variables
        define reduced electrolyte coordinates if needed
        define extents or true-species variables if reactive
        define internal-state strategy
    run pretreatment:
        validate feed and domain
        homogeneous speciation seed if reactive
        density/property seeds
        association internal-state seeds if needed
    run phase discovery:
        if backend is held_tpd_volume_composition:
            run TPD / volume-composition trial problems
            collect candidate phases
            de-duplicate candidates
            solve candidate mass-balance selection
            rank candidate sets
        else:
            run declared route seed generators
    for candidate_set in ranked_candidate_sets:
        assemble Ipopt NLP:
            objective Phi_p(u)
            constraints c_p(u)
            inequalities g_p(u)
            bounds
            scaling
            exact derivative callbacks
        solve with Ipopt from candidate_set initial variables
        if solver returns finite point:
            lift variables to canonical true species by phase
            evaluate thermodynamic phase states
            run postsolve certification:
                conservation
                pressure
                fugacity or chemical potential
                charge and reduced electrochemical residual if electrolyte
                reaction affinity if reactive
                internal-state residual
                phase distinctness
                TPD stability
                candidate completeness
            if all certification passes:
                return production_accepted result
            record rejected attempt
    if approximate diagnostic continuation exists:
        run diagnostic route
        return approximate_diagnostic_only if it converges
    return best failed or rejected result with full diagnostics
```

## LaTeX-Ready Core Block

```tex
\section{Generalized Fluid-Phase Equilibrium Formulation}
Let $\mathcal{I}=\{1,\ldots,C\}$ denote the true-species set and
$\mathcal{A}=\{1,\ldots,\pi\}$ denote the active fluid-phase set.
The canonical thermodynamic state is the true-species phase-mole tensor
\[
N=\{n_{i\alpha}\}_{i\in\mathcal{I},\alpha\in\mathcal{A}}.
\]
For phase $\alpha$,
\[
N_\alpha=\sum_i n_{i\alpha},
\qquad
x_{i\alpha}=\frac{n_{i\alpha}}{N_\alpha},
\qquad
\rho_\alpha=\frac{N_\alpha}{V_\alpha}.
\]
For pressure-specified phase-split routes, the default thermodynamic objective is
\[
\Phi_{TP}
=
\sum_{\alpha\in\mathcal{A}}
\left[
A_\alpha(T,V_\alpha,n_\alpha,q_\alpha)+P^0V_\alpha
\right].
\]
The equivalent Gibbs formulation is
\[
\Phi_G
=
\sum_{\alpha\in\mathcal{A}}G_\alpha(T,P^0,n_\alpha,q_\alpha),
\qquad
G(T,P,n)=\min_V[A(T,V,n)+PV].
\]
Stationarity with respect to $V_\alpha$ gives
\[
\frac{\partial A_\alpha}{\partial V_\alpha}+P^0=0,
\qquad
P_\alpha=-\frac{\partial A_\alpha}{\partial V_\alpha}=P^0.
\]
For a nonreactive neutral mixture,
\[
\sum_{\alpha}n_{i\alpha}=n_i^F.
\]
The Gibbs-form Lagrangian is
\[
\mathcal{L}
=
\sum_\alpha G_\alpha
+
\sum_i \lambda_i
\left(n_i^F-\sum_\alpha n_{i\alpha}\right).
\]
Stationarity gives
\[
\mu_{i\alpha}=\lambda_i,
\qquad
\mu_{i\alpha}=\mu_{i\beta}.
\]
For electrolyte phases,
\[
z^T n_\alpha=0.
\]
If a charged reference species $r$ is eliminated,
\[
n_{r\alpha}=-\sum_{i\neq r}\frac{z_i}{z_r}n_{i\alpha},
\qquad
\mu_{i\alpha}^{el}
=
\mu_{i\alpha}-\frac{z_i}{z_r}\mu_{r\alpha}.
\]
The charged-species phase-equilibrium residual is
\[
r_i^{el,\alpha\beta}
=
\mu_{i\alpha}^{el}-\mu_{i\beta}^{el}.
\]
For reaction $r$,
\[
r_r^{rxn}
=
\sum_{\alpha,i}\nu_{i\alpha r}\frac{\mu_{i\alpha}}{RT}
-\ln K_r(T,P)=0.
\]
For neutral phase stability,
\[
\mathrm{TPD}(w;z)
=
\sum_i w_i
\left[
\frac{\mu_i(T,P,w)}{RT}
-
\frac{\mu_i(T,P,z)}{RT}
\right],
\qquad
\min_{w\in\Delta}\mathrm{TPD}(w;z)\ge -\tau_{\mathrm{TPD}}.
\]
For strong-electrolyte stability, trial compositions satisfy
\[
x\ge0,
\qquad
\sum_i x_i=1,
\qquad
z^Tx=0.
\]
Using reduced electrolyte coordinates $y$,
\[
\mathrm{TPD}^{el}(y;y^0)
=
g^{el}(y)-g^{el}(y^0)-\nabla g^{el}(y^0)^T(y-y^0),
\qquad
\min_{y\in\Omega^{el}}\mathrm{TPD}^{el}(y;y^0)\ge -\tau_{\mathrm{TPD}}.
\]
For exact association,
\[
F_a(X;T,\rho,x,p)
=
X_a\left(1+\rho\sum_b w_bX_b\Delta_{ab}\right)-1=0,
\qquad
X_u=-F_X^{-1}F_u.
\]
Explicit approximate closures may define
\[
X_a\approx X_a^{approx}(T,\rho,x,p),
\]
but the resulting derivatives are exact only for the approximate association
model, not for the exact mass-action PC-SAFT association model.
```

## Local References

- `docs/roadmaps/unified_equilibrium_core_algorithm.md`
- `docs/roadmaps/FULL_ROADMAP.md`
- `docs/roadmaps/gross2002_associating_vle_redo_plan.md`
- `docs/roadmaps/explicit_association_closure_for_pcsaft.md`
- `docs/latex/algorithms.tex`
- `docs/papers/md/Pereira et al. - 2012 - The HELD algorithm for multicomponent, multiphase equilibrium calculations with generic equations of.md`
- `docs/papers/md/Ascani, Sadowski, Held - 2022 - Calculation of Multiphase Equilibria Containing Mixed Solvents and M.md`
- `docs/papers/md/Perdomo et al. - 2025 - Phase stability criteria and fluid-phase equilibria in strong-electrolyte systems.md`
- `docs/papers/md/Ascani - 2023 - Simultaneous Predictions of Chemical and Phase Equilibria in Systems with an Esterif.md`
