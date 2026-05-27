# Generalized Fluid-Phase Equilibrium

This is the canonical roadmap, mathematical doctrine, implementation contract,
and activation policy for generalized fluid-phase equilibrium in `ePC-SAFT`.
It is written for future implementers and agents, not as a runtime API
reference.

`docs/roadmaps/equilibrium_benchmark_registry.yaml` is the executable
roadmap registry. Its family labels are roadmap labels only. They are not
Python route strings, C++ selector keys, capability keys, or dictionary keys
that production code must consume.

`docs/latex/equations.tex` remains the equation source of truth for EOS
contribution details. This roadmap repeats only the core equilibrium,
stability, NLP, and Ipopt equations needed to implement the family plan.

`docs/roadmaps/stage_by_stage_implementation_plan.md` is the companion
GFPE-first execution overlay. It uses `FULL_ROADMAP.md` only as package
context and lists concrete pretreatment, implementation, and exit-evidence
steps for each GFPE stage.

## Source Hierarchy And Current Boundary

The current public package still exposes the existing selector-backed neutral
utility routes such as `bubble_pressure`, `bubble_temperature`,
`dew_pressure`, `dew_temperature`, `flash`, and neutral nonassociating `lle`.
This roadmap does not remove those routes and does not change their runtime
behavior.

The generalized equilibrium roadmap is stricter than the current public
surface. A route family is not generalized-production-ready until it has:

- a source-backed proof case;
- exact first derivatives and exact Lagrangian Hessian coverage for the active
  objective and constraints;
- route-owned bounds, scaling, smooth coordinate maps, and Ipopt barrier
  constraints;
- sparse Jacobian and Hessian contracts checked through `NlpProblem`;
- phase-discovery evidence from the staged HELD path, not only deterministic
  candidate screening;
- postsolve certification proving material balance, pressure consistency,
  phase equilibrium, stability, and phase-set completeness.

Current deterministic TPD/candidate screening is useful seed and certification
support. It must not be described as full HELD. Full HELD is the staged
algorithm described below.

## Roadmap Families

The collapsed roadmap has six visible family labels:

| Roadmap label | Scope | Current generalized status |
| --- | --- | --- |
| `PE-Neutral TP Flash` | Neutral, nonelectrolyte, nonreactive TP flash and neutral VLE/LLE proof ladder | `planned_not_public` |
| `PE-Associating TP Flash` | Neutral associating TP flash/VLE/LLE after exact association derivatives | `planned_not_public` |
| `PE-Electrolyte LLE/TP Flash` | Strong-electrolyte LLE and TP flash with charge-neutral reduced variables | `planned_not_public` |
| `PE-Generalized Multiphase` | More-than-two-phase phase discovery and phase-set certification | `planned_not_public` |
| `CE Chemical Equilibrium Placeholder` | Homogeneous chemical/speciation equilibrium without phase split | `planned_not_public` |
| `CPE Combined Phase-Chemical Placeholder` | Simultaneous phase split and reaction/speciation equilibrium | `planned_not_public` |

The family labels are deliberately descriptive. They replace the old numeric
PE/CE/CPE row identifiers in the roadmap and registry. They are stable enough
for documentation tests and proof-case references, but they are still roadmap
labels, not runtime keys.

## Core Phase-Equilibrium Form

For phases `a = 1..N_p` and true species `i = 1..N_c`, the canonical physical
variables are phase species amounts `n_{i,a}` and phase volumes `V_a`. Route
specifications may expose transformed variables, reduced charge-neutral
coordinates, reaction coordinates, or phase-fraction coordinates, but every
route must lift those coordinates into true species by phase before evaluating
the thermodynamic objective and constraints.

Basic definitions:

```text
N_a = sum_i n_{i,a}
x_{i,a} = n_{i,a} / N_a
rho_a = N_a / V_a
```

The phase NLP is a thermodynamic constrained optimization problem. For an
isothermal-isobaric TP route, the physical objective is the pressure-transformed
Helmholtz objective:

```text
Phi(T, P, n, V) = sum_a A_a(T, V_a, n_a) + P * sum_a V_a
```

where `A_a` includes the ideal and residual Helmholtz contributions selected by
the active EOS model. Detailed PC-SAFT/ePC-SAFT contribution equations live in
`docs/latex/equations.tex`.

Hard constraints for a neutral nonreactive TP flash are:

```text
sum_a n_{i,a} = z_i F                         for each species i
P_eos(T, V_a, n_a) - P = 0                    for each phase a
mu_i(T, V_a, n_a) - mu_i(T, V_b, n_b) = 0     for transferable species i
```

The KKT stationarity of this NLP is the implementation target. Residual-only
objectives may be used for route-declared diagnostics, continuation, or
equation-solve reductions, but the final production acceptance path must
certify the thermodynamic objective and constraints.

Electrolyte routes add per-phase charge balance and compare projected
electrochemical potentials in a charge-neutral reduced basis:

```text
sum_i z_i^charge n_{i,a} = 0
Pi_perp(mu_i + z_i^charge psi_a) equal across transferable phases
```

Associating routes add either complete implicit association sensitivities or
lifted association-site variables with mass-action constraints. A reduced
explicit association closure is a diagnostic approximation only unless the
route explicitly exposes it as approximate and labels acceptance accordingly.

Reactive and combined phase-chemical routes add reaction affinity constraints:

```text
sum_i nu_{r,i} mu_i = 0
```

with a declared standard-state and reaction-constant convention.

## Stability And HELD Doctrine

The neutral tangent-plane distance check is a stability and certification
problem, not a substitute for the final phase NLP. A typical neutral TPD form
is:

```text
TPD(w | z) = sum_i w_i * (mu_i(w) - mu_i(z))
```

with the route-specific volume or pressure closure included in the trial-phase
evaluation. A negative minimum proves instability of the reference phase. A
local nonnegative result is not a global proof unless the route declares and
passes a global or certified phase-discovery procedure.

The HELD implementation ladder is:

1. Preserve current deterministic TPD/candidate screening as seed and
   postsolve support.
2. Add continuous TPD minimization in volume-composition space.
3. Add HELD Stage I stability testing with multiple starts and reported
   failure modes.
4. Add HELD Stage II dual cutting-plane phase discovery with explicit upper
   and lower bounds and candidate phase storage.
5. Reuse the current Ipopt phase-amount/phase-volume NLP as Stage III primal
   refinement of the candidate phase set.
6. Add HELD2.0 for strong electrolytes with reduced electroneutral variables
   before electrolyte production validation.

The current Stage 9 neutral implementation separates these statuses in native
diagnostics: deterministic screening remains seed and certification support,
continuous TPD and HELD Stage I diagnostics are reported only when every
continuous TPD start converges, HELD Stage II reports an executable candidate
bound audit, and current Ipopt phase-amount/phase-volume solves are reported
as Stage III refinement only for the route that was actually solved. An
iteration-limit result is an incomplete continuous TPD result, not phase
discovery evidence. An open Stage II candidate bound gap is also incomplete
phase-discovery evidence, not a production HELD proof. A current-route Stage
III postsolve is not verified Stage III evidence unless Ipopt itself reports
`success` and `solve_succeeded`; acceptable-level or finite-variable postsolve
acceptance is diagnostic, not convergence proof. The current neutral LLE proof
fixture uses the route-owned `held_refinement` Ipopt profile and reports Stage
III only when the same route converges before postsolve certification.

Current public utility `flash` calls keep deterministic TPD postsolve
certification but do not request continuous TPD by default. Continuous TPD and
HELD Stage I diagnostics are proof-path evidence, not a hidden cost on every
public flash solve.

Runtime diagnosis must stay narrow. Use
`uv run python run_pytest.py --equilibrium-debug -q -s <one equilibrium
test node>` when investigating Ipopt iteration limits, seed attempts, or
continuous TPD behavior. The debug lane requires one explicit test node; it
cannot run a pytest slice. It enables verbose Ipopt output, stores Ipopt
iteration history, and prints continuous-TPD trace rows.
Whole equilibrium result files under `tests/native/equilibrium/results` are
guarded as opt-in sweeps.

The executable Stage 9 snapshot is
`uv run python scripts/validation/check_stage9_phase_discovery_evidence.py --json`.
That default command is the cheap phase-discovery gate: it does not run the
Stage III Ipopt route refinement solve. Run it with
`--include-route-refinement` only when current-route Stage III evidence is
needed, and with `--debug --include-route-refinement` when diagnosing the
current TPD/Ipopt path. Debug mode enables `EPCSAFT_EQUILIBRIUM_DEBUG`, prints
continuous-TPD trace rows, and uses Ipopt `print_level=5`; JSON debug mode keeps
the machine-readable payload on stdout and forwards native solver output to
stderr. Its current synthetic neutral payload reports HELD Stage II as
`candidate_bound_gap_closed` for the finite candidate audit. When route
refinement is requested, current Ipopt `success` / `solve_succeeded` convergence
is required before Stage III can be counted as current-route refinement
evidence. This still does not make the generalized family production-exposed:
source-backed Stage 10 proof, full family generalization, exact derivatives,
and postsolve certification gates still control admission.

Until stages 2-5 exist for the relevant family, registry rows must stay
`planned_not_public` even if existing public utility routes solve useful
limited cases.

## Shared NLP Route Contract

The current native route substrate is `NlpProblem`. It is the right seam for
generalized equilibrium work and should be deepened rather than bypassed.

Every route must declare:

- physical variable layout after any coordinate transform;
- variable lower and upper bounds;
- constraint lower and upper bounds;
- initial physical point and transformed solver point;
- objective value, gradient, sparse Jacobian structure, sparse Jacobian values,
  and Lagrangian Hessian values;
- route metadata covering variable model, density backend, residual families,
  constraint families, derivative backend, scaling, and domain margins.

Contract-level shape:

```text
NlpProblem
  bounds() -> NlpBounds
  scaling() -> NlpScaling
  objective(x_phys), gradient(x_phys)
  constraints(x_phys)
  jacobian_structure() -> rows, cols
  jacobian_values(x_phys) -> values in the same order
  hessian_values(x_phys, objective_factor, lambda)
```

The sparse Jacobian contract is explicit: `rows[k]`, `cols[k]`, and
`values[k]` describe one nonzero in a fixed route-owned order. Generic CppAD
snippets are not the repo contract. If a future route extracts sparsity from
CppAD tapes, it must still publish the same `NlpProblem` row/column/value
contract to the Ipopt adapter.

## Ipopt And Numerical Method Layer

Ipopt is the production nonlinear programming backend for the generalized phase
NLP. The roadmap separates thermodynamic equations from optimizer mechanics so
the objective remains physically interpretable.

All generalized routes must use all three domain-safety mechanisms:

1. Explicit route-owned bounds and constraints define the admissible physical
   domain.
2. A reusable `VariableTransform` wrapper maps unconstrained or lightly
   bounded solver coordinates into physical route variables and applies the
   chain rule to gradients, Jacobians, and Hessians.
3. Ipopt's internal barrier handles the declared bounds and constraints.

The barrier layer means Ipopt's interior-point barrier for explicit bounds and
constraints. It does not mean adding a permanent custom barrier term to
`Phi`. A route may use temporary continuation aids only if it later performs a
final certification solve on the unmodified thermodynamic objective.

The reusable coordinate wrapper contract is implemented at
`src/epcsaft/native/equilibrium/core/variable_transform.h`. Current neutral
routes declare the identity physical-coordinate transform; the native smoke
contract also proves a positive-log map so future positive-domain coordinates
reuse the same chain-rule path.

```text
VariableTransform
  solver_to_physical(u) -> x
  dx_du(u)
  d2x_du2(u)
```

Routes keep their equations in physical variables. The wrapper owns smooth maps
for positivity, composition-simplex coordinates, phase volumes, reduced
charge-neutral electrolyte variables, and optional log coordinates needed for
trace components.

Scaling is route-owned and mandatory. At minimum, routes must scale:

- amounts by feed total or seed phase amount;
- volumes by seed/reference phase volumes;
- pressure residuals by the pressure target or a physically comparable scale;
- material constraints by feed amounts;
- chemical-potential or fugacity residuals in dimensionless or RT-normalized
  form;
- objective values by a declared extensive scale.

Ipopt must receive the route-owned scaling as user scaling. Automatic Ipopt
scaling may remain a development comparison, but it is not the production
contract for GFPE routes. Route diagnostics must report the objective scale,
variable-scale minimum and maximum, constraint-scale minimum and maximum,
variable-scale ratio, constraint-scale ratio, scaled constraint violation,
scaled stationarity, bound complementarity, and whether the scaled numerical
acceptance gate passed. These diagnostics are separate from physical
postsolve acceptance because a numerically converged NLP can still fail phase,
stability, material-balance, or domain-certification checks.

Stage 8 owns the Ipopt option profiles used before any Stage 9 real-mixture
HELD proof case starts:

- `proof`: normal exact-derivative proof profile for the shared NLP contract.
- `continuation_trace`: longer iteration history and conservative bound-push
  defaults for branch tracking and seed-transfer debugging.
- `held_refinement`: tighter interior-bound defaults and larger iteration
  budget for HELD-discovered phase-set refinement.
- `diagnostic`: the only profile allowed to use limited-memory Hessians.

Every non-diagnostic profile must keep the exact-Hessian gate active through
the `profile_exact_hessian_gate` diagnostic. The solve payload must also record
requested and selected linear solver, bound-push and bound-fraction values,
active lower/upper/total bound counts, Ipopt barrier parameter, restoration
phase observation, regularization size, and maximum step-trial count. Stage 9
must not test real mixtures until these Stage 8 diagnostics and profile gates
are covered by focused native contract tests.

Domain diagnostics are mandatory. Route results should report the smallest
margin to amount bounds, volume/density bounds, packing-fraction limits,
composition floors, charge-neutrality constraints, and any transform saturation
threshold. Silent clipping is forbidden.

## Exact Derivative Policy

Exact gradients and exact Jacobians are required for any generalized production
claim. Exact Lagrangian Hessians are required before production exposure unless
the route is explicitly documented as an internal diagnostic.

The Born SSM+DS path is a prerequisite for electrolyte production validation.
The master Born equation path must support exact Hessian contributions for the
SSM+DS mixing form; simpler direct or constant-radius modes should reduce from
that master path. Electrolyte PE validation remains blocked until the route no
longer needs a special exact-Hessian gate for active Born phase blocks.

## Implementation Sequence

Implementation must proceed in this order:

1. Infrastructure gate:
   sparse `NlpProblem` contracts, route scaling, domain bounds, smooth
   coordinate wrapper design, Ipopt barrier constraints, diagnostics, and exact
   derivative expectations.
2. Continuous TPD and HELD:
   add staged phase-discovery evidence before treating a source-backed neutral
   proof or boundary workflow as generalized GFPE evidence.
3. Neutral TP flash:
   build on the shared amount-volume phase NLP and Stage 9 HELD diagnostics,
   then prove a source-backed ePC-SAFT-compatible neutral case before
   broadening claims.
4. Derived boundary workflows:
   bubble, dew, cloud, and shadow workflows as DOF swaps over the shared phase
   NLP, then `T-x` and `P-x` diagram generation.
5. Neutral generalized multiphase:
   full HELD stages and phase-set completeness beyond two selected phases.
6. Associating PE:
   exact association derivative coverage or lifted mass-action variables before
   Gross/Sadowski proof cases.
7. Electrolyte PE:
   Born SSM+DS exact Hessian coverage, charge-neutral reduced variables, and
   HELD2.0 before Khudaida/Held/Ascani validation.
8. CE and CPE:
   homogeneous chemical equilibrium first, then simultaneous phase-chemical
   equilibrium after PE and CE proofs exist.

The detailed stage-by-stage execution plan is in
`docs/roadmaps/stage_by_stage_implementation_plan.md`. Keep this section short:
it defines order; the companion plan defines work packages and exit evidence.

## Derived Boundary Workflows

Bubble, dew, cloud, and shadow workflows are derived subworkflows, not main
activation families. They are still planned implementation work because they
are the route to `T-x` and `P-x` diagrams after the main neutral TP flash proof.

| Workflow | Fixed variables | Free variables | Boundary meaning |
| --- | --- | --- | --- |
| Bubble point | `T` and liquid/feed composition for `P-x`; `P` and liquid/feed composition for `T-x` | incipient vapor composition, phase volumes, boundary `P` or `T` | vapor phase appears from liquid reference |
| Dew point | `T` and vapor composition for `P-x`; `P` and vapor composition for `T-x` | incipient liquid composition, phase volumes, boundary `P` or `T` | liquid phase appears from vapor reference |
| Cloud point | `T` or `P` and parent liquid composition | incipient second-liquid composition, phase volumes, boundary `P` or `T` | second liquid appears |
| Shadow point | matched cloud-point state | shadow-phase composition and volume | composition of the incipient phase |

The Pereira 2012 System III source audit found a SAFT-VR problem definition,
including SAFT-VR range and binary interaction parameters. It remains useful
HELD literature context, but it is not an executable ePC-SAFT proof fixture for
the current package unless SAFT-VR support or a source-backed ePC-SAFT
reparameterization is added. The shared boundary proof must therefore stop at
source selection and choose a source-backed ePC-SAFT-compatible neutral binary
rather than inventing a synthetic validation fixture. Do not add VLLE-specific
tests in this step.

The Stage 10 neutral proof gate is explicit in
`docs/roadmaps/equilibrium_benchmark_registry.yaml`. A neutral TP-flash case is
not executable proof until it supplies source-backed species, pure-component
parameters, binary interactions, temperature, pressure, feed composition,
expected phase count, expected phase compositions, expected phase fractions,
accepted source model family, source path, and acceptance tolerances. Local
Gross/Sadowski 2001 material is useful PC-SAFT context, but the currently
available local table is a binary VLE correlation/AAD summary rather than a
point TP-flash fixture. The existing hydrocarbon workbook case remains package
runtime smoke evidence until source-backed phase-split provenance is added.
The Pereira source audit is retained under
`data/reference/equilibrium_benchmarks/neutral_tp_flash/pereira_2012`; it
captures the SAFT-VR phase-split table and parameters, and records the
published second-feed composition inconsistency as a blocker instead of
normalizing it silently. Its material-balance readiness file identifies which
reported points are lever-rule feasible and which need source-confirmed feed
correction before proof promotion.

The readiness file is checked by
`uv run python scripts/validation/check_equilibrium_benchmark_readiness.py --json`.
When executable Stage 9 evidence is relevant, first generate
`check_stage9_phase_discovery_evidence.py --json --include-route-refinement`
and pass the payload through `--stage9-evidence-json`. The same readiness command with
`--require-executable` is the closed gate for promoting a case into executable
Stage 10 proof evidence; Pereira currently fails that gate by design.

## Family Proof Ladder

`PE-Neutral TP Flash`

- first proof: source-backed ePC-SAFT-compatible neutral TP flash target;
- Pereira 2012 System III: HELD/SAFT-VR reference only until model parity or a
  source-backed ePC-SAFT reparameterization exists;
- follow-on stress: methane/H2S or another source-backed neutral case if the
  EOS/parameter set supports it;
- required before exposure: infrastructure gate, continuous TPD minimization,
  HELD Stage I/II/III, exact derivatives, and postsolve certification.

`PE-Associating TP Flash`

- first proof: Gross/Sadowski 2002 methanol/cyclohexane;
- follow-on stress: water/1-pentanol or another two-associating-component case;
- required before exposure: association mass-action or implicit sensitivity
  architecture with exact Jacobian and Hessian contributions.

`PE-Electrolyte LLE/TP Flash`

- first proof: Khudaida 2026 electrolyte LLE case;
- follow-on: Held 2014 Figure 6, then Ascani/Sadowski/Held 2022;
- required before exposure: Born SSM+DS exact Hessian, reduced
  electroneutral variables, electrolyte TPD/HELD2.0, charge and
  electrochemical-potential certification.

`PE-Generalized Multiphase`

- first proof: replay representative neutral, associating, and electrolyte
  cases through the same phase-set discovery contract;
- required before exposure: complete candidate phase set, mass-balance
  feasibility, and no route-specific phase-count assumptions.

`CE Chemical Equilibrium Placeholder`

- keep as roadmap-only until homogeneous reaction/speciation equations,
  standard-state conventions, and acceptance tests are written.

`CPE Combined Phase-Chemical Placeholder`

- keep as roadmap-only until PE and CE proofs can be solved in one simultaneous
  route with both transfer equilibrium and reaction affinity certification.

## Registry And Test Acceptance

The executable registry uses schema version 2:

```text
schema_version: 2
family_rows:
  - family_label: PE-Neutral TP Flash
derived_subworkflows:
  - label: Bubble point
benchmark_cases:
  - case_label: Pereira 2012 System III
```

Registry acceptance rules:

- no visible old numeric row identifiers;
- no family row marked `production_exposed: true` before the HELD and
  derivative gates pass;
- bubble/dew/cloud/shadow appear only under `derived_subworkflows`;
- proof cases reference descriptive family labels;
- deterministic screening is not called full HELD;
- raw `docs/ChatGPT_Gemini_Responses/*` files remain uncited input artifacts.

The immediate test work is registry/test audit cleanup only. It must not add
new public routes, new solver infrastructure, or new executable proof fixtures.
