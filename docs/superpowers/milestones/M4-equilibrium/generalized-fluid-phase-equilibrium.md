# Generalized Fluid-Phase Equilibrium

This is the M4 milestone doctrine, mathematical contract, implementation
contract, and activation policy for generalized fluid-phase equilibrium in
`ePC-SAFT`. It is written for future implementers and agents, not as a
runtime API reference or an active Superpowers Project spec.

`docs/superpowers/milestones/M4-equilibrium/registries/equilibrium-benchmark-registry.yaml` is the executable
milestone registry. Its family labels are planning labels only. They are not
Python route strings, C++ selector keys, capability keys, or dictionary keys
that production code must consume.

`docs/latex/equations.tex` remains the equation source of truth for EOS
contribution details. This plan repeats only the core equilibrium,
stability, NLP, and Ipopt equations needed to implement the family plan.

`docs/superpowers/specs/2026-05-26-m4-equilibrium-stage-by-stage-implementation-plan.md` is the companion
GFPE-first execution overlay. It uses `PROJECT_CONTEXT.md` only as package
context and lists concrete pretreatment, implementation, and exit-evidence
steps for each GFPE stage.

`docs/superpowers/specs/2026-05-27-m4-equilibrium-gfpe-package-cleanup-plan.md` is the companion package cleanup
overlay. It translates this doctrine into module boundaries for selector
admission, the shared NLP core, Ipopt numerics, certified results, capability
reporting, and validation lanes.

## Source Hierarchy And Current Boundary

The current public package still exposes the existing selector-backed neutral
utility routes such as `bubble_pressure`, `bubble_temperature`,
`dew_pressure`, `dew_temperature`, `flash`, and neutral nonassociating `lle`.
This plan does not remove those routes and does not change their runtime
behavior.

The generalized equilibrium plan is stricter than the current public
surface. A route family is not generalized-production-ready until it has:

- a source-backed validation case;
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

## Plan Families

The collapsed plan has six visible family labels:

| Planning label | Scope | Current generalized status |
| --- | --- | --- |
| `PE-Neutral TP Flash` | Neutral, nonelectrolyte, nonreactive TP flash and neutral VLE/LLE validation ladder | `planned_not_public` |
| `PE-Associating TP Flash` | Neutral associating TP flash/VLE/LLE after exact association derivatives | `planned_not_public` |
| `PE-Electrolyte LLE/TP Flash` | Strong-electrolyte LLE and TP flash with charge-neutral reduced variables | `planned_not_public` |
| `PE-Generalized Multiphase` | More-than-two-phase phase discovery and phase-set certification | `neutral_public_admitted` |
| `CE Chemical Equilibrium Placeholder` | Homogeneous chemical/speciation equilibrium without phase split | `planned_not_public` |
| `CPE Combined Phase-Chemical Placeholder` | Simultaneous phase split and reaction/speciation equilibrium | `planned_not_public` |

The family labels are deliberately descriptive. They replace the old numeric
PE/CE/CPE row identifiers in the plan and registry. They are stable enough
for documentation tests and proof-case references, but they are still plan
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
Whole equilibrium result files under `packages/epcsaft-equilibrium/tests/native/results` are
guarded as opt-in sweeps.

The executable Stage 9 snapshot is
`uv run python scripts/validation/check_phase_discovery.py --json`.
That default command is the cheap phase-discovery gate: it does not run the
Stage III Ipopt route refinement solve. Run it with
`--include-route-refinement` only when current-route Stage III evidence is
needed, and with `--debug --include-route-refinement --require-complete` when
diagnosing the current TPD/Ipopt path. Debug mode enables
`EPCSAFT_EQUILIBRIUM_DEBUG`, prints continuous-TPD trace rows and route
seed-attempt markers, uses Ipopt `print_level=5`, and fails if convergence
evidence is incomplete; the diagnostics payload includes bounded Ipopt
iteration-history records so the actual primal/dual residual path is visible
without running a pytest sweep. JSON debug mode keeps the machine-readable
payload on stdout and forwards native solver output to stderr. Its current
synthetic neutral payload separates the Stage II candidate-bound audit
(`candidate_bound_gap_closed`) from the Stage II adoption status
(`dual_loop_verified`) and carries replayable candidate metadata into Stage III.
When route refinement is requested, current Ipopt `success` / `solve_succeeded`
convergence and consumption of the Stage II replay seed are required before
Stage III can be counted as current-route refinement evidence. This still does
not make the generalized family production-exposed: the source-backed neutral TP
flash fixture, full family generalization, exact derivatives, and postsolve
certification gates still control admission.

Milestone HELD/GFPE evidence also requires a fresh-native receipt. The
phase-discovery checker emits `native_freshness_receipt` with the current git
commit, imported native module path, checker command, and equilibrium native
build-refresh command. Stage II/III status rows and milestone figures are not
completion evidence without those fields. A closed PR or issue only explains
where code came from; it does not prove the local `.pyd` imported by Python was
rebuilt from that code.

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
NLP. The plan separates thermodynamic equations from optimizer mechanics so
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
`packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/core/variable_transform.h`. Current neutral
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
   Stage II candidate-set replay, strict Stage III residual refinement, and
   public neutral nonassociating `multiphase` admission beyond two selected
   phases.
6. Associating PE:
   exact association derivative coverage or lifted mass-action variables before
   Gross/Sadowski validation cases.
7. Electrolyte PE:
   Born SSM+DS exact Hessian coverage, charge-neutral reduced variables, and
   HELD2.0 before Khudaida/Held/Ascani validation.
8. CE and CPE:
   homogeneous chemical equilibrium first, then simultaneous phase-chemical
   equilibrium after PE and CE proofs exist.

The detailed stage-by-stage execution plan is in
`docs/superpowers/specs/2026-05-26-m4-equilibrium-stage-by-stage-implementation-plan.md`. Keep this section short:
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
HELD literature context, but it is not an executable ePC-SAFT validation fixture for
the current package unless SAFT-VR support or a source-backed ePC-SAFT
reparameterization is added. Boundary-workflow validation must therefore use the
source-backed ePC-SAFT-compatible neutral TP flash mixture unless a later
implementation proves it physically unsuitable; it must not invent a synthetic
validation fixture. Do not add VLLE-specific tests in this step.

Current bubble/dew runtime routes are validated only through the
derived-boundary checker, not by ad hoc public-route success. Boundary workflow
completion requires strict Ipopt convergence for every requested boundary
point: `solver_status == success`, `application_status == solve_succeeded`,
and no selected seed attempt ending in `max_iterations_exceeded`.
Acceptable-level points, tiny steps, feasible points, postsolve-accepted finite
variables, or any iteration-limit seed path remain diagnostic evidence only.
The current hydrocarbon-workbook fixture now verifies strict bubble/dew `P-x`
and `T-x` route points when the checker is run with explicit sweep opt-in.
Routine validation must stay contract-only unless a single named debug route
point is requested; multi-point `T-x` or `P-x` route points require
`--allow-route-sweep` and an explicit `--route-point-count`.

The retained cloud/shadow source-data gate is
`uv run python scripts/validation/check_boundary_workflows.py --json
--cloud-shadow-gate --require-cloud-shadow-gate`. It checks the Matsuda/NIST
perfluorohexane + hexane neutral LLE fixture for 14 source-backed cloud-point
binodal rows and one paired cloud/shadow branch row. Passing this gate means
the cloud/shadow source-data contract is retained.

The checker-gated native cloud/shadow route-evidence command is
`uv run python scripts/validation/check_boundary_workflows.py --json
--run-cloud-shadow-route --require-cloud-shadow-route`. It first obtains the
model-refined Matsuda branch pair from the existing certified `neutral_lle`
showcase at 293.895 K and 101300 Pa, then fixes the model-refined parent-liquid
composition in the private `neutral_cloud_t_eos` route and solves the
cloud-temperature plus shadow-liquid composition. Passing this gate means one
internal native isobaric cloud/shadow route point is strict-Ipopt verified
against the source-backed fixture tolerances. It still does not add public
`cloud_temperature`, `cloud_point`, or `shadow_point` route keys.

The neutral TP flash fixture gate is explicit in
`docs/superpowers/milestones/M4-equilibrium/registries/equilibrium-benchmark-registry.yaml`. A neutral TP-flash case is
not executable until it supplies source-backed species, pure-component
parameters, binary interactions, temperature, pressure, feed composition,
expected phase count, expected phase compositions, expected phase fractions,
accepted source model family, source path, and acceptance tolerances. Local
Gross/Sadowski 2001 material is useful PC-SAFT context, but the currently
available local table is a binary VLE correlation/AAD summary rather than a
point TP-flash fixture. The local hydrocarbon workbook case is now the first
executable neutral TP flash fixture: it uses the workbook's PC-SAFT bubble-point
liquid and vapor phase split, derives a neutral TP flash feed by equal-phase
lever blending, and checks the native `neutral_tp_flash` route against the
source phase compositions and phase fractions. This is source-backed workbook
evidence, not a literature benchmark.
The Pereira source audit is retained under
`data/reference/equilibrium_benchmarks/neutral_tp_flash/ethane_carbon_dioxide`; it
captures the SAFT-VR phase-split table and parameters, and records the
published second-feed composition inconsistency as a blocker instead of
normalizing it silently. Its material-balance check file identifies which
reported points are lever-rule feasible and which need source-confirmed feed
correction before fixture promotion.

The fixture is checked by
`uv run python scripts/validation/check_equilibrium_benchmark_fixture.py --json`.
When phase-discovery validation is relevant, first generate
`check_phase_discovery.py --json --include-route-refinement`
and pass the payload through `--phase-discovery-json`. The same fixture command
with `--require-executable` is the closed gate for promoting a case into an
executable neutral TP flash fixture; Pereira currently fails that gate by
design. The fixture payload reports each executable field separately so a source
case cannot be promoted until PC/ePC parameters, binary interactions, feed and
phase-fraction data, accepted model family, source path, tolerances, and
phase-discovery validation are all present.

The executable neutral TP flash route check is
`uv run python scripts/validation/check_neutral_tp_flash_fixture.py --phase-discovery-json <payload> --require-complete`.
That checker reports the supplied `held_tpd_admission` gate and fails closed
unless the route postsolve also proves TPD postsolve certification, stability
acceptance, candidate completeness, a certified phase set, positive phase
distance, the expected selected-candidate count, and the material balance,
pressure, fugacity, composition, and phase-fraction tolerances.
Its JSON payload carries the same `native_freshness_receipt` shape as the
phase-discovery checker, and `--require-complete` treats a missing commit or
native module path as a failed proof.
Use `--debug --json` when diagnosing the route path: machine-readable fixture
output stays on stdout, while Ipopt iteration output and any route
seed-attempt trace rows generated by the selected path are forwarded to stderr.
The script also supports
`--generate-phase-discovery` for an intentional one-command JetBrains Services
diagnostic run; tests should prefer a supplied phase-discovery payload so
neutral TP flash coverage does not hide a second TPD/Ipopt route solve.

The boundary workflow checker is
`uv run python scripts/validation/check_boundary_workflows.py`.
Use `--json --contracts-only` for the cheap derived-workflow contract check.
Use `--json --cloud-shadow-gate --require-cloud-shadow-gate` for the retained
cloud/shadow source-data gate.
Use `--json --run-cloud-shadow-route --require-cloud-shadow-route` for the
checker-gated native cloud/shadow isobaric route-evidence point; this command
must keep public cloud/shadow runtime routes empty while reporting closed public
route admission in the private route payload.
Use `--json --run-current-boundary-route --route <route> --debug
--require-complete` only when diagnosing one current bubble/dew route; the
checker forwards Ipopt `print_level=5` output to stderr and fails closed when
the route does not strictly converge. Use
`--json --run-current-boundary-route --allow-route-sweep --route-point-count
<N> --require-complete` only for intentional boundary route-point validation; it is not a
routine validation lane.
Every requested current bubble/dew route point must carry a complete
`boundary_trace` record. The trace records the route, workflow label, diagram
target, known and free variables, solved boundary variable, fixed composition
role, phase roles, source fixture, selector family, problem name, shared NLP
residual and constraint families, strict solver/application status, seed
attempt status, and finite residual norms. Missing trace fields, mismatched
known/free variables, absent residual families, non-strict convergence, or an
iteration-limit seed path are failed boundary evidence.

## Family Validation Ladder

`PE-Neutral TP Flash`

- first validation target: source-backed ePC-SAFT-compatible neutral TP flash target;
- Pereira 2012 System III: HELD/SAFT-VR reference only until model parity or a
  source-backed ePC-SAFT reparameterization exists;
- follow-on stress: methane/H2S or another source-backed neutral case if the
  EOS/parameter set supports it;
- required before exposure: infrastructure gate, continuous TPD minimization,
  HELD Stage I/II/III, exact derivatives, and postsolve certification.

`PE-Associating TP Flash`

- first validation target: Gross/Sadowski 2002 methanol/cyclohexane;
- retained #145 prerequisite proof: `uv run python
  scripts/validation/check_associating_lle_gross_2002.py --json
  --require-source-data --require-exact-association-hessian
  --require-route-closed --require-complete` proves the source fixture, exact
  association site sensitivities, objective/pressure/mass-action/Lagrangian
  Hessian evidence, and the source-pair internal LLE certification that #190
  consumes for public admission;
- current public admission proof: `uv run python
  scripts/validation/check_associating_gfpe_gate.py --json
  --require-source-data --require-public-admission
  --require-exact-association-hessian --require-electrolyte-closed
  --require-complete` admits only
  `Equilibrium(..., route="lle")` for the source-backed Gross/Sadowski 2002
  methanol/cyclohexane two-phase neutral associating fixture, names
  `assoc_scheme=2B`, `k_ij=0.051`, and `cppad_implicit_association`, and keeps
  missing-proof, ionic/electrolyte, reactive, TP-flash, and generalized
  associating phase-set surfaces closed;
- current paper-validation acceptance proof: `uv run --no-sync python
  scripts/validation/check_gross_2002_association_acceptance.py --json
  --require-complete --require-exact-association-hessian --require-fresh-native`
  accepts Figure 1 pure-association AAD sanity evidence, Figure 8
  methanol/cyclohexane exact-Hessian evidence, and Figure 10 water/1-pentanol
  cross-association stress evidence with `k_ij=0.016` and
  `cppad_implicit_association`; Figures 2-7 and 9 remain source-requirement
  records with no completion credit until their source points and provenance
  are retained;
- follow-on stress: broaden the accepted Gross 2002 campaign to the Figure
  2-7 and 9 VLE mirrors after source points and required nonassociating
  pure-parameter provenance are retained;
- required before exposure: association mass-action or implicit sensitivity
  architecture with exact Jacobian and Hessian contributions.

`PE-Electrolyte LLE/TP Flash`

- first validation target: Khudaida 2026 electrolyte LLE case;
- follow-on: Held 2014 Figure 6, then Ascani/Sadowski/Held 2022;
- required before exposure: Born SSM+DS exact Hessian, reduced
  electroneutral variables, electrolyte TPD/HELD2.0, charge and
  electrochemical-potential certification.

`PE-Generalized Multiphase`

- current retained internal diagnostic: `uv run --no-sync python
  scripts/validation/check_generalized_phase_set.py --json --require-complete`
  proves neutral three-candidate phase-set records, selected/rejected row
  reasons including duplicate/collapsed, infeasible, lower-free-energy omitted,
  uncertified, and generic unselected rejected candidates, mass-balance
  feasibility, and noncollapsed selected compositions;
- current retained strict route proof: `uv run --no-sync python
  scripts/validation/check_generalized_phase_set.py --json --phase-kinds
  liquid,liquid,liquid --run-route-refinement --require-route-refinement
  --require-complete` proves Stage III
  `strict_fugacity_residual` refinement for the Stage II candidate-set replay,
  exact reduced fugacity-residual derivative metadata, accepted postsolve,
  and reduced ln-fugacity consistency <= `1.0e-6`;
- current public admission proof: `uv run --no-sync python
  scripts/validation/check_generalized_phase_set.py --json --phase-kinds
  liquid,liquid,liquid --run-route-refinement --require-route-refinement
  --require-public-admission --require-complete` proves the public
  `Equilibrium(..., route="multiphase", phase_kinds=[...]).solve()` workflow
  maps to `neutral_multiphase_nonassoc`, returns three named phases, reports
  exact Hessian evidence, and accepts the postsolve;
- remaining validation target: replay associating and electrolyte cases through
  their own exact-derivative and chemistry-specific phase-set contracts;
- required before broader exposure: complete candidate phase set,
  mass-balance feasibility, no route-specific phase-count assumptions, strict
  residual Stage III certification rather than only a thermodynamic-objective
  route, and source-backed representative cases for each additional family.

`CE Chemical Equilibrium Placeholder`

- keep as planning-only until homogeneous reaction/speciation equations,
  standard-state conventions, and acceptance tests are written.

`CPE Combined Phase-Chemical Placeholder`

- keep as planning-only until PE and CE proofs can be solved in one simultaneous
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
- every family row marked `production_exposed: true` must carry a matching
  checker command and acceptance evidence; currently this is limited to
  neutral nonassociating `PE-Generalized Multiphase` public `multiphase`
  admission;
- bubble/dew/cloud/shadow appear only under `derived_subworkflows`;
- reference cases use descriptive family labels;
- deterministic screening is not called full HELD;
- raw `docs/ChatGPT_Gemini_Responses/*` files remain uncited input artifacts.

The current admitted public generalized route is neutral nonassociating
`Equilibrium(..., route="multiphase", phase_kinds=[...]).solve()`. Do not
broaden that claim to associating, electrolyte, reactive, CE, CPE, LLLE, or
VLLE without their own exact-derivative and source-backed proof gates.
