# M8 Neutral PC-SAFT Helmholtz Equilibrium Toolbox Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:executing-plans` to implement this plan task-by-task. Use `superpowers:test-driven-development` for every executable task and `superpowers:verification-before-completion` before any completion claim.

**Goal:** Add the leanest source-traced pure-Python neutral, nonassociating PC-SAFT Helmholtz evaluator needed to exercise the existing neutral HELD direct-minimization formulation against real mixture parameters without Ipopt, autodiff, native EOS calls, or public API changes.

**Architecture:** Extend the existing M8 `explicit_association_toybox` analysis instead of creating another EOS implementation. Reuse its scalar hard-chain and dispersion owners, add one strict reference-data loader and one extensive Helmholtz evaluator, and adapt that evaluator downward into the existing analysis-only equilibrium formulation kernel. Keep the manufactured equilibrium oracle unchanged. Generate retained source/model evidence in a two-step data-then-render figure workflow. This slice stops at neutral, nonassociating mixtures.

**Tech Stack:** Python 3, NumPy, SciPy where bounded scalar minimization is needed, Matplotlib, pytest, repository CSV/JSON fixtures, and the existing analysis-only equilibrium formulation kernel.

---

## Intake

- Source formulation: `docs/latex/equilibrium_formulations.tex`
- Source request: the user explicitly approved immediate plan-to-implementation execution for a lean Python EOS evaluation toolbox.
- Source analyses: `analyses/package_validation/explicit_association_toybox` and `analyses/reference_oracles/equilibrium_formulations`.
- Source literature fixture: `data/reference/equilibrium_benchmarks/neutral_lle/perfluorohexane_hexane`.
- Source fixed-state fixture: `data/reference/equilibrium_benchmarks/neutral_tp_flash/methane_ethane_propane`.
- Milestone: `M8 - Python Toybox`.
- Package owner: no package owner is modified; this is analysis-only evidence.
- Execution mode: inline on the existing isolated `codex/equilibrium-formulations-oracle` worktree; no push or publication.

## Global Constraints

- Do not edit `docs/latex/equations.tex` or `docs/latex/algorithms.tex`.
- Do not edit the July 12 M4 recovery specification or plan.
- Do not change `packages/epcsaft/**`, `packages/epcsaft-equilibrium/**`, or any public capability registry.
- Public equilibrium remains limited to `bubble_pressure`, `dew_pressure`, and the scoped methane/ethane/propane single-component VLE route.
- Do not claim published Pereira HELD, Perdomo HELD2, or production equilibrium completion.
- Keep canonical neutral HELD Stage III as direct total-free-energy minimization. Residual checks are certificates, not the primary algorithm.
- Do not add Ipopt, JAX, CppAD, native EOS, or solver substitution requirements.
- Do not duplicate the full C++ ePC-SAFT implementation. Import the existing M8 scalar hard-chain and dispersion functions.
- Do not infer scientific equations from code. Trace every PC-SAFT term to the canonical equation registry and Gross--Sadowski source record.
- Treat the ideal-mixture reference as an explicit gauge for nonreactive phase equilibrium. Do not reuse it for CE or CPE without species standard-state formation terms.
- Fail closed for missing parameters, invalid domains, failed derivative stencils, failed equilibrium certificates, or absent source evidence.
- Use deterministic seeds and retain every plotted source/model value.

## Source Evidence

- **verified:** `docs/latex/equilibrium_formulations.tex` owns the extensive EOS contract: total Helmholtz energy is the phase evaluator; pressure and chemical potentials are its volume and mole-number derivatives; neutral HELD Stage III minimizes the summed phase Helmholtz energy plus imposed-pressure volume work.
- **verified:** Gross and Sadowski (2001), as reconciled by canonical equation identifiers in `docs/latex/equations.tex`, owns the neutral PC-SAFT hard-chain, dispersion, mixing, compressibility, residual chemical-potential, and fugacity identities reused by this analysis.
- **verified:** Sandler (2017), Section 9.1, especially Eq. 9.1-16 and the ideal-gas equation of state, supplies the ideal-gas-mixture Helmholtz mixing basis. The implementation may choose a documented constant reference-density gauge because only nonreactive cross-phase differences are tested.
- **verified:** the Matsuda/NIST fixture retains two source-backed binary LLE branch compositions at 293.895 K and 101300 Pa, Tihic PC-SAFT-compatible pure parameters, and an explicitly source-fitted binary interaction for the repository's neutral PC-SAFT diagnostic.
- **verified:** the methane/ethane/propane workbook fixture retains fixed-state compositions, volumes, pressure, parameters, and binary interactions, but it is an internal workbook fixture rather than independent literature evidence.
- **inference:** a species-independent ideal reference-density shift changes each phase's total Helmholtz gauge consistently and leaves nonreactive phase coexistence, pressure, and chemical-potential differences invariant. Tests must prove this invariance numerically.
- **assumption:** five-point interior numerical derivative stencils are sufficient for this reference lane when their step-refinement and independent analytic pressure checks pass. This is not a production derivative policy.
- **unknown:** before execution, it is not known whether the new direct-minimization adapter will reproduce the retained Matsuda branches within the fixture thresholds. Completion is blocked if it does not; tolerances will not be weakened or refitted inside this plan.
- **unknown:** association-state, electrolyte, reaction, HELD2, counterion-pair, CE, and CPE evaluator contracts remain outside this first physical EOS slice.

## Outcome Proof

**Intent:** Prove that the unified equilibrium formulation can consume one real, extensive neutral PC-SAFT Helmholtz evaluator through the existing analysis kernel and produce auditable thermodynamic and numerical evidence without Ipopt, autodiff, or native EOS execution.

**Current Behavior:** The M8 toybox evaluates residual hard-chain, dispersion, and association contributions at fixed states, while the equilibrium formulation kernel currently runs only manufactured free-energy families; no shared extensive physical mixture evaluator joins the two.

**Expected Outcome:** A strict neutral parameter loader and an extensive nonassociating Helmholtz evaluator pass domain, extensivity, derivative, pressure, Euler, permutation, reference-gauge, and fixed-state checks; a physical neutral HELD adapter runs through the shared kernel with deterministic multistart and independent low-dimensional enumeration; retained Matsuda source/model evidence makes any pass or failure visible.

**Target Output:** Focused pytest lanes pass, the Matsuda generator emits deterministic source/model/certificate tables, and a retained SVG/PNG/PDF figure shows source branch compositions beside the computed direct-minimization result and its independent objective/certificate landscape.

**Owner:** M8 Python Toybox owns the evaluator and retained analysis evidence; M4 remains the sole owner of public equilibrium capability and production solvers.

**Interface:** `NeutralPCSAFTParameters`, `NeutralPCSAFTHelmholtzEvaluator`, `BinaryNeutralPhaseEvaluator`, `NeutralHeldEOSAdapter`, the existing `run_formulation` facade, and the retained `neutral_pcsaft_equilibrium_contract` data/figure workflow.

**Cutover:** New physical mixture tests use the extensive Helmholtz evaluator and shared formulation kernel; the old pure-only reduced chemical-potential proxy remains historical toy evidence and is not promoted or silently reused as the mixture equilibrium route.

**Replaced Path:** Ad hoc fixed-state residual checks and the pure-only `quick_phase_equilibrium.py` proxy as the only Python evidence connecting EOS terms to equilibrium behavior.

**Evidence:** Red/green test receipts, analytic-pressure versus Helmholtz-derivative closure, Euler and extensivity identities, derivative step-refinement tables, deterministic multistart results, independent one-dimensional composition enumeration, mass/volume balance checks, source-composition errors, retained plotted-data CSV, figure artifacts, plan validators, docs validation, and the repository cleanup audit.

**Acceptance Proof:** From a clean checkout, a reviewer can regenerate the Matsuda tables and plot, run the focused tests, and observe that every declared thermodynamic identity and equilibrium certificate meets its stated threshold while the computed LLE branches meet the existing source fixture composition tolerance; otherwise the workflow reports a named blocking failure without changing parameters or public claims.

**Stop Criteria:** Stop and report a scientific blocker if the sourced neutral PC-SAFT terms cannot satisfy the extensive Helmholtz closure tests, if derivative refinement is unstable, if the shared direct-minimization route cannot be independently enumerated, or if Matsuda source thresholds fail without an already-sourced parameter correction.

**Avoid:** Do not add hidden row-specific seeds, fit parameters during validation, silently change solvers, invent defaults, copy native provider equations, add association/electrolyte/reaction logic, broaden public capabilities, or present the M8 result as production prediction evidence.

**Risk:** The principal risk is producing numerically plausible phase splits from an inconsistent total-energy gauge or a local minimum. Independent pressure/Euler identities, reference-gauge invariance, deterministic multistart, and low-dimensional global enumeration are mandatory defenses.

## Implementation Boundaries

**Files To Create:** `analyses/package_validation/explicit_association_toybox/scripts/neutral_pcsaft_inputs.py`, `analyses/package_validation/explicit_association_toybox/scripts/neutral_pcsaft_helmholtz.py`, `analyses/package_validation/explicit_association_toybox/scripts/neutral_held_eos_adapter.py`, three focused test modules for those interfaces, `analyses/package_validation/explicit_association_toybox/docs/neutral_pcsaft_equilibrium_toolbox.md`, one figure data generator, one figure renderer, one figure-workflow test, and retained CSV/SVG/PNG/PDF artifacts under `figures/neutral_pcsaft_equilibrium_contract/results`.

**Files To Modify:** `analyses/package_validation/explicit_association_toybox/README.md`, `analyses/package_validation/explicit_association_toybox/analysis.yaml`, and `.mplgallery/manifest.yaml` only if the repository gallery synchronizer registers the new figure.

**Files To Avoid:** `docs/latex/equations.tex`, `docs/latex/algorithms.tex`, July 12 M4 recovery documents, all package/native/provider files, public API docs, capability registries, source fixture values, association algorithms, electrolyte algorithms, reaction algorithms, HELD2, counterion-pair, CE, and CPE implementations.

**Source Of Truth:** `docs/latex/equilibrium_formulations.tex` for the algorithm/evaluator contract; canonical equation identifiers and Gross--Sadowski source records for PC-SAFT terms; Sandler Section 9.1 for the ideal-mixture Helmholtz basis; retained fixture metadata/CSV/JSON files for real parameters and acceptance thresholds.

**Read Path:** Load ordered species and explicit pure/binary parameter tables; evaluate ideal plus imported residual Helmholtz terms at fixed temperature, phase volume, and positive mole vector; pass a binary molar-energy view to the existing direct-minimization formulation facade; independently enumerate the pressure-shifted molar energy before accepting a result.

**Write Path:** Write only analysis code/tests/docs and deterministic retained result tables/figures. Every figure is rendered solely from the generated result tables and writes a same-stem plotted-data snapshot.

**Integration Points:** Existing `hard_chain.py`, `dispersion.py`, `pcsaft_inputs.py`, `toy_property_eos.compressibility_terms`, `analyses.reference_oracles.equilibrium_formulations.kernel.run_formulation`, neutral HELD oracle data structures where compatible, the Matsuda fixture, the workbook fixed-state fixture, pytest, and MPLGallery validation.

**Migration Or Cutover:** Additive M8 analysis integration only. The physical adapter becomes the sole new mixture path in this toybox; the manufactured oracle remains the algorithm regression owner, and the pure-only proxy is explicitly demoted from mixture proof.

**Replaced Path Handling:** Keep `quick_phase_equilibrium.py` for its existing pure toy tests, document that it is displaced for mixture proof, and forbid new neutral mixture evidence from importing it.

**Acceptance Proof Gate:** Do not claim completion or commit the final implementation until focused tests, artifact regeneration, plotted-data equality checks, source tolerances, plan validators, docs validation, MPLGallery validation when available, git diff review, and cleanup audit all pass.

## Decision Ledger

| decision | source | answer | impact | deferred? | risk owner |
| --- | --- | --- | --- | --- | --- |
| Milestone and ownership | Repository invariants and user scope | Implement only under the M8 analysis toybox; do not edit M4 packages or public routes. | Prevents capability expansion and cross-milestone ownership conflicts. | no | M8 analysis owner |
| EOS implementation seam | Existing toybox inspection | Reuse scalar hard-chain and dispersion owners and add an extensive wrapper. | Avoids a duplicate full PC-SAFT implementation. | no | M8 analysis owner |
| Algorithm seam | Formal formulation and current kernel | Use the existing one-facade direct formulation kernel with a family-owned physical adapter. | Tests the shared-kernel design without changing manufactured oracles. | no | Equilibrium formulation owner |
| Ideal contribution | Sandler Section 9.1 and nonreactive scope | Use an explicit constant reference-density gauge and prove gauge invariance. | Supplies total Helmholtz closure while preventing reactive standard-state claims. | no | Thermodynamic reviewer |
| Derivative policy | User authorization and reference-lane scope | Use transparent five-point interior numerical derivatives plus analytic pressure closure and step refinement. | Removes Ipopt/autodiff dependencies while retaining independent checks. | no | Numerical reviewer |
| Physical evidence case | Matsuda/NIST and Tihic fixture | Use the retained binary LLE pair and existing thresholds without refitting. | Provides traceable real mixture evidence and a fail-closed acceptance gate. | no | Validation owner |
| Workbook evidence role | Fixture metadata | Use methane/ethane/propane only for fixed-state closure, not literature validation. | Keeps provenance claims accurate. | no | Validation owner |
| Association and charged/reactive families | User-requested lean first slice and formal family separation | Defer association, HELD2, counterion-pair, CE, and CPE until the neutral evaluator gate passes. | Preserves non-equivalence and bounds the implementation. | yes | Future family owners |
| Solver policy | User request and existing NumPy kernel | Use deterministic multistart plus independent enumeration; do not add or substitute Ipopt. | Makes local-minimum risk visible without new solver dependencies. | no | Numerical reviewer |
| Publication | User instruction | Commit locally in focused checkpoints; do not push, publish, or open a PR. | Preserves isolated local ownership. | no | Worktree owner |

## Test Complete And Metrics

Test complete requires all of the following:

- Parameter loading rejects missing species, duplicate rows, nonpositive pure parameters, incomplete interaction pairs, asymmetric matrices, and nonzero diagonals.
- Ideal-gas limiting behavior approaches compressibility one and vanishing residual energy at low density.
- Extensive Helmholtz energy scales linearly when all amounts and volume scale together.
- Pressure from the extensive volume derivative agrees with the independently implemented PC-SAFT compressibility pressure over gas-like and liquid-like fixed states.
- Chemical potentials satisfy the Euler identity within a scale-aware tolerance.
- Species permutation and reference-density gauge changes preserve pressure and equilibrium differences.
- Five-point derivative estimates are finite and show stable refinement; invalid interior stencils fail explicitly.
- Workbook fixed-state rows load without parameter invention and report pressure/chemical-potential closure metrics without being labeled literature prediction evidence.
- The shared-kernel physical neutral HELD result satisfies material and volume balances, domain guards, stationarity diagnostics, common chemical-potential differences, pressure consistency, and the independent enumeration objective gap.
- Matsuda model branch errors are no greater than the existing composition tolerance of `0.02` mole fraction; if they are larger, completion stops without refitting.
- Repeated generation with the same seed produces byte-stable CSV evidence.
- The plotted-data snapshot exactly contains the source and model values rendered in the retained figure.

## Tasks

### Task 1: Strict Source-Backed Neutral Parameter Loader

**Use Cases:**

- A reviewer needs visible proof that every physical EOS parameter came from an ordered retained table rather than an invented default.
- A missing or duplicate interaction row must fail before EOS evaluation so invalid evidence cannot reach acceptance.
- Species reordering must be deterministic and the old path of ad hoc dictionaries must be displaced for real mixture proof.

**Files:**

- Create: `analyses/package_validation/explicit_association_toybox/scripts/neutral_pcsaft_inputs.py`
- Create: `analyses/package_validation/explicit_association_toybox/tests/test_neutral_pcsaft_inputs.py`

- [ ] **Step 1 — RED:** Write tests for exact ordered loading of the Matsuda and workbook parameter tables plus failures for missing species, duplicate species, invalid pure values, incomplete pair coverage, asymmetric interactions, and nonzero diagonal interactions.
- [ ] **Step 2 — Verify RED:** Run `uv run --no-sync python run_pytest.py analyses/package_validation/explicit_association_toybox/tests/test_neutral_pcsaft_inputs.py -q`; expect import or contract failures.
- [ ] **Step 3 — GREEN:** Implement immutable parameter records and strict CSV loaders using explicit species order and fail-closed validation.
- [ ] **Step 4 — Verify GREEN:** Re-run the focused test; expect all loader cases to pass.
- [ ] **Step 5 — Refactor:** Remove duplicate parsing branches and keep all validation in one constructor path.
- [ ] **Step 6 — Checkpoint commit:** Commit only Task 1 files with `analysis: add strict neutral PC-SAFT inputs`.

### Task 2: Extensive Neutral PC-SAFT Helmholtz Evaluator

**Use Cases:**

- The shared equilibrium formulation needs one evaluator that returns total extensive energy, pressure, and chemical potentials from the same state definition.
- Acceptance evidence must expose ideal, hard-chain, and dispersion contributions without duplicating their canonical scalar owners.
- The cutover from residual-only fixed-state checks to total-energy equilibrium input must preserve source tracing and fail on invalid domains.

**Files:**

- Create: `analyses/package_validation/explicit_association_toybox/scripts/neutral_pcsaft_helmholtz.py`
- Create: `analyses/package_validation/explicit_association_toybox/tests/test_neutral_pcsaft_helmholtz.py`

- [ ] **Step 1 — RED:** Add tests for low-density ideal behavior, extensivity, analytic-pressure closure, Euler closure, species permutation, reference-gauge invariance, derivative step refinement, and invalid temperature/volume/amount/packing/stencil domains.
- [ ] **Step 2 — Verify RED:** Run `uv run --no-sync python run_pytest.py analyses/package_validation/explicit_association_toybox/tests/test_neutral_pcsaft_helmholtz.py -q`; expect missing evaluator failures.
- [ ] **Step 3 — GREEN:** Implement the ideal reference gauge, imported neutral residual contributions, extensive energy, five-point volume/mole derivatives, analytic compressibility pressure, and a binary molar-energy adapter.
- [ ] **Step 4 — Verify GREEN:** Re-run the focused test; expect every thermodynamic closure metric to pass.
- [ ] **Step 5 — Refactor:** Centralize domain checks and derivative-step construction; retain contribution-level diagnostics.
- [ ] **Step 6 — Checkpoint commit:** Commit only Task 2 files with `analysis: add neutral PC-SAFT Helmholtz evaluator`.

### Task 3: Fixed-State EOS Contract Evidence

**Use Cases:**

- Maintainers need a quick no-solver proof that the evaluator is internally consistent at real retained mixture states.
- The workbook fixture must remain visibly labeled as internal fixed-state evidence rather than literature prediction proof.
- The old path of checking only residual energy must be displaced by total-energy derivative and balance evidence.

**Files:**

- Modify: `analyses/package_validation/explicit_association_toybox/tests/test_neutral_pcsaft_helmholtz.py`
- Create: `analyses/package_validation/explicit_association_toybox/docs/neutral_pcsaft_equilibrium_toolbox.md`

- [ ] **Step 1 — RED:** Add workbook phase-state tests that require finite total energy, derivative pressure, analytic pressure, chemical potentials, Euler residual, and explicit provenance labels.
- [ ] **Step 2 — Verify RED:** Run the focused evaluator test; expect missing fixed-state diagnostics or provenance failures.
- [ ] **Step 3 — GREEN:** Add the smallest diagnostic record/helper needed to expose closure metrics without adding a second evaluator.
- [ ] **Step 4 — Verify GREEN:** Re-run the focused evaluator test and record the real metric ranges in the toolbox document.
- [ ] **Step 5 — Refactor:** Keep the document qualitative about formulas and link to the canonical TeX owner rather than duplicating mathematical equations.
- [ ] **Step 6 — Checkpoint commit:** Commit only Task 3 files with `analysis: document neutral Helmholtz contract evidence`.

### Task 4: Shared-Kernel Physical Neutral HELD Adapter

**Use Cases:**

- A formulation reviewer needs proof that the same direct-minimization facade can run a physical neutral EOS evaluator, not only manufactured polynomials.
- Deterministic multistart and an independent composition/volume enumeration must expose metastable or local solutions before acceptance.
- The migration must retire the pure-only proxy as mixture-equilibrium proof while leaving its historical tests intact.

**Files:**

- Create: `analyses/package_validation/explicit_association_toybox/scripts/neutral_held_eos_adapter.py`
- Create: `analyses/package_validation/explicit_association_toybox/tests/test_neutral_held_eos_adapter.py`

- [ ] **Step 1 — RED:** Add tests for adapter registration, direct-path enforcement, deterministic starts, material/volume/domain checks, formulation-matched certificates, single-phase boundary behavior, two-phase Matsuda behavior, a surfaced local/metastable start, and invalid input.
- [ ] **Step 2 — Verify RED:** Run `uv run --no-sync python run_pytest.py analyses/package_validation/explicit_association_toybox/tests/test_neutral_held_eos_adapter.py -q`; expect missing adapter failures.
- [ ] **Step 3 — GREEN:** Implement the physical direct adapter, scaled decision variables, deterministic multistart, independent low-dimensional objective enumeration, and formulation-specific certificate payload.
- [ ] **Step 4 — Verify GREEN:** Re-run the adapter test; require source tolerance, objective-gap, balance, pressure, and chemical-potential certificates to pass.
- [ ] **Step 5 — Refactor:** Keep physical-family code outside the manufactured oracle registry and preserve one-way dependency from the toybox to the shared kernel.
- [ ] **Step 6 — Checkpoint commit:** Commit only Task 4 files with `analysis: connect neutral PC-SAFT to HELD kernel`.

### Task 5: Retained Literature Evidence, Plot, And Final Verification

**Use Cases:**

- A validation reviewer needs target-visible source markers, computed branches, and the independent objective landscape in one retained artifact.
- Plot acceptance must be reproducible from retained tables and the displaced path of prose-only pass claims must be impossible.
- Final proof must preserve closed public LLE capability and clearly state the limits before any association or charged/reactive expansion.

**Files:**

- Create: `analyses/package_validation/explicit_association_toybox/figures/neutral_pcsaft_equilibrium_contract/scripts/generate_data.py`
- Create: `analyses/package_validation/explicit_association_toybox/figures/neutral_pcsaft_equilibrium_contract/scripts/render_figure.py`
- Create: `analyses/package_validation/explicit_association_toybox/figures/neutral_pcsaft_equilibrium_contract/results/neutral_pcsaft_equilibrium_contract.csv`
- Create: `analyses/package_validation/explicit_association_toybox/figures/neutral_pcsaft_equilibrium_contract/results/neutral_pcsaft_equilibrium_contract_plotted_data.csv`
- Create: `analyses/package_validation/explicit_association_toybox/figures/neutral_pcsaft_equilibrium_contract/results/neutral_pcsaft_equilibrium_contract.svg`
- Create: `analyses/package_validation/explicit_association_toybox/figures/neutral_pcsaft_equilibrium_contract/results/neutral_pcsaft_equilibrium_contract.png`
- Create: `analyses/package_validation/explicit_association_toybox/figures/neutral_pcsaft_equilibrium_contract/results/neutral_pcsaft_equilibrium_contract.pdf`
- Create: `analyses/package_validation/explicit_association_toybox/tests/test_neutral_pcsaft_equilibrium_figure.py`
- Modify: `analyses/package_validation/explicit_association_toybox/README.md`
- Modify: `analyses/package_validation/explicit_association_toybox/analysis.yaml`
- Modify if synchronized by tooling: `.mplgallery/manifest.yaml`

- [ ] **Step 1 — RED:** Add artifact tests for deterministic generation, required source/model/certificate columns, exact plotted-data retention, source threshold enforcement, and nonproduction capability labels.
- [ ] **Step 2 — Verify RED:** Run `uv run --no-sync python run_pytest.py analyses/package_validation/explicit_association_toybox/tests/test_neutral_pcsaft_equilibrium_figure.py -q`; expect missing workflow/artifact failures.
- [ ] **Step 3 — GREEN data:** Implement and run `uv run --no-sync python analyses/package_validation/explicit_association_toybox/figures/neutral_pcsaft_equilibrium_contract/scripts/generate_data.py`; require deterministic source/model and enumeration rows.
- [ ] **Step 4 — GREEN plot:** Implement and run `uv run --no-sync python analyses/package_validation/explicit_association_toybox/figures/neutral_pcsaft_equilibrium_contract/scripts/render_figure.py`; require readable source markers, model branches, certificate panel, units, and limitations note.
- [ ] **Step 5 — Verify artifacts:** Re-run the figure test, inspect SVG/PNG/PDF, compare plotted snapshot to the generated table, and validate/synchronize MPLGallery when its CLI is available.
- [ ] **Step 6 — Update front door:** Document commands, scientific labels, source status, public capability limits, and evidence required before association, HELD2, counterion-pair, CE, or CPE work.
- [ ] **Step 7 — Full proof:** Run focused toybox tests, formulation-kernel tests, plan validators, docs validation, git diff/check, and the cleanup audit.
- [ ] **Step 8 — Checkpoint commit:** Commit Task 5 and any proportional cleanup with `analysis: retain neutral PC-SAFT equilibrium evidence`.

## Proof Oracle

```bash
bash /home/tnnrpolley21/.codex/plugins/cache/personal/superpowers-project/0.3.0/scripts/validate-plan-outcome-proof.sh -PlanPath docs/superpowers/plans/2026-07-13-m8-neutral-pcsaft-helmholtz-equilibrium-toolbox-plan.md
bash /home/tnnrpolley21/.codex/plugins/cache/personal/superpowers-project/0.3.0/scripts/validate-plan-task-use-cases.sh -PlanPath docs/superpowers/plans/2026-07-13-m8-neutral-pcsaft-helmholtz-equilibrium-toolbox-plan.md
bash /home/tnnrpolley21/.codex/plugins/cache/personal/superpowers-project/0.3.0/scripts/validate-decision-ledger.sh -Path docs/superpowers/plans/2026-07-13-m8-neutral-pcsaft-helmholtz-equilibrium-toolbox-plan.md -Kind plan
uv run --no-sync python run_pytest.py analyses/package_validation/explicit_association_toybox/tests/test_neutral_pcsaft_inputs.py analyses/package_validation/explicit_association_toybox/tests/test_neutral_pcsaft_helmholtz.py analyses/package_validation/explicit_association_toybox/tests/test_neutral_held_eos_adapter.py analyses/package_validation/explicit_association_toybox/tests/test_neutral_pcsaft_equilibrium_figure.py -q
uv run --no-sync python run_pytest.py analyses/reference_oracles/equilibrium_formulations/tests analyses/reference_oracles/neutral_held/tests -q
uv run --no-sync python analyses/package_validation/explicit_association_toybox/figures/neutral_pcsaft_equilibrium_contract/scripts/generate_data.py
uv run --no-sync python analyses/package_validation/explicit_association_toybox/figures/neutral_pcsaft_equilibrium_contract/scripts/render_figure.py
uv run --no-sync python scripts/dev/validate_project.py docs
git diff --check
bash "$HOME/.codex/hooks/codex-cleanup.sh" --repo-root .
```

## Next-Family Evidence Gate

Stop after this neutral, nonassociating slice. Association may begin only after a separately sourced plan defines the implicit association-state derivative contract and proves association-state convergence/sensitivity at fixed states. HELD2 and counterion-pair equilibrium require their independent electrolyte potential certificates and Galvani convention. CE requires standard-state formation data and reaction-rank tests. CPE requires a separately designed coupled topology, not reuse of CE or neutral HELD by name.
