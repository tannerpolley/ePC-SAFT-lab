# M3 Neutral EOS Derivative and Equation Reconciliation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Correct the two verified native derivative defects, reconcile the neutral/base PC-SAFT equations with their active C++ conventions and retained primary literature, and convert the remaining audit leads into explicit verified or unresolved outcomes.

**Architecture:** Keep the public provider boundary and derivative-mode contract unchanged. Repair only the incorrect internal scalar dependency in the CppAD dispersion tape and the inconsistent association-strength prefactor in the temperature derivative. Treat `docs/latex/equations.tex` as the editable equation source, regenerate its Markdown/YAML views, and leave electrolyte equations and equilibrium algorithms outside this slice.

**Tech Stack:** C++17, CppAD, Eigen, pybind11, Python 3.12, pytest, uv, LaTeX, and the repository equation-registry generator.

## Global Constraints

- Owning milestone/package: M3 provider/EOS; production ownership is `packages/epcsaft/**` plus provider-owned documentation and tests.
- Do not edit `packages/epcsaft-equilibrium/**`, M4 program specs/plans, or the source checkout at `/home/tnnrpolley21/Workspaces/Engineering/ePC-SAFT`.
- Preserve derivative mode semantics: mode `0` is analytic, mode `2` is CppAD, and mode `3` (`auto`) currently resolves neutral hard-chain/dispersion composition derivatives analytically.
- Use test-driven development: add and prove each failing regression against the pre-fix native extension before changing its C++ owner.
- Only the main task may rebuild native code, stage, commit, or run repository cleanup. Subagents may edit assigned non-overlapping files or conduct read-only review.
- Label scientific conclusions in review notes as **verified**, **inference**, **assumption**, or **unknown**.
- Retained literature authority for this slice:
  - Gross and Sadowski (2001), PC-SAFT appendix equations in the local paper records.
  - Huang and Radosz (1990), SAFT \(\sigma^3\kappa\) association-strength lineage retained by the active PC-SAFT convention in the local paper records.
  - Chapman et al. (1990), `Phase Equilibria in Polymer-Liquid 1-Liquid 2 Systems.md`, especially Eqs. 21--28 and Appendix A.6.
- Chapman Eq. 24 uses the original-SAFT convention `d_ij^3 kappa`; active PC-SAFT C++ uses `sigma_ij^3 kappa`. Document the lineage translation; do not change the active C++ baseline from `sigma_ij^3` to `d_ij^3`.
- `docs/latex/algorithms.tex` is read-only in this implementation except for broken neutral-EOS pointers or compile-only TeX corrections. Do not redesign equilibrium algorithms.
- Electrolyte/Debye--Huckel/Born equations and the full Figiel/Cameretti campaigns remain later slices. Only record dependencies that explain whether the neutral fixes can affect those results.

---

## Task 1: Repair the CppAD dispersion composition tape

**Files:**

- Modify: `packages/epcsaft/tests/native/state/test_eos_contributions.py`
- Modify: `packages/epcsaft/src/epcsaft/native/model/parameter_setup.cpp`
- Verify: `packages/epcsaft/src/epcsaft/native/eos/contributions/dispersion.cpp`
- Verify: `packages/epcsaft/src/epcsaft/native/eos/residual/cppad/hard_chain_dispersion.h`

### Step 1: Add the failing backend-parity regression

Add a test named `test_public_cppad_dispersion_composition_derivative_matches_canonical_tape` using `_neutral_args()`, `T = 310 K`, `rho = 8200 mol m^-3`, and `x = [0.35, 0.65]`.

The test must:

1. Set `args.disp_dadx_diff_mode = 2`.
2. Obtain the public contribution derivative from `NativeState.composition_derivative_residual_helmholtz_result().dadx.disp`.
3. Obtain the independent canonical CppAD row from `_native_cppad_eos_contributions`, reshape `jacobian_row_major` using `shape`, and select `outputs.index("disp")`.
4. Assert the public and canonical rows agree with `rel=1e-11`, `abs=1e-12`.
5. Assert the public derivative backend reports `"cppad"` for dispersion.

Pre-fix evidence at this state:

```text
public mode 2: [-2.29833208, -3.89921632]
canonical tape: [-2.02741726, -3.46388330]
analytic/auto:  [-2.02741726, -3.46388330]
```

### Step 2: Prove RED against the current native binary

Run:

```bash
uv run --no-sync python run_pytest.py \
  packages/epcsaft/tests/native/state/test_eos_contributions.py \
  -q -k public_cppad_dispersion_composition_derivative_matches_canonical_tape
```

Expected: one failure showing that mode-2 CppAD omits the composition dependence of the dispersion coefficients through `m_avg`.

### Step 3: Make the dispersion coefficients tape-active

In `dispersion_state_cppad_cpp`:

- Remove the `std::array<double, 7> a` and `b` members from `CppADDispersionState`.
- Do not call `scalar_value(m_avg)` while forming `a_i(m_avg)` or `b_i(m_avg)`.
- Define tape-active factors and local coefficients:

```cpp
const CppADScalar m1_factor = (m_avg - 1.0) / m_avg;
const CppADScalar m2_factor = (m_avg - 2.0) / m_avg;
for (int i = 0; i < 7; ++i) {
    const CppADScalar a_i = kDispersionA0[i]
        + m1_factor * kDispersionA1[i]
        + m1_factor * m2_factor * kDispersionA2[i];
    const CppADScalar b_i = kDispersionB0[i]
        + m1_factor * kDispersionB1[i]
        + m1_factor * m2_factor * kDispersionB2[i];
    state.I1 += a_i * scalar_pow(eta, i);
    state.I2 += b_i * scalar_pow(eta, i);
}
```

This is algebraically identical to Gross and Sadowski Eqs. A.18--A.19 while preserving `m_avg = sum_i x_i m_i` on the CppAD tape.

### Step 4: Rebuild and prove GREEN

Run, sequentially:

```bash
uv run --no-sync python scripts/dev/build_epcsaft.py --profile provider
uv run --no-sync python run_pytest.py \
  packages/epcsaft/tests/native/state/test_eos_contributions.py \
  -q -k 'cppad_eos_contribution or public_cppad_dispersion'
```

Expected: all selected tests pass; the mode-2 result equals both the canonical tape and the analytic result.

### Step 5: Confirm downstream scope and commit

Run:

```bash
uv run --no-sync python run_pytest.py \
  packages/epcsaft/tests/api/frontend/test_state_properties.py \
  -q -k cppad_state_proves_hydrocarbon_values_and_derivatives
```

Expected: the existing public `auto`-mode density, compressibility, and fugacity golden values remain unchanged because `auto` resolves this contribution analytically. Record this as **verified**, not as evidence that explicit mode 2 was correct.

Commit:

```bash
git add packages/epcsaft/tests/native/state/test_eos_contributions.py \
  packages/epcsaft/src/epcsaft/native/model/parameter_setup.cpp
git commit -m "fix: retain dispersion composition dependence on CppAD tape"
```

---

## Task 2: Repair the association temperature derivative

**Files:**

- Modify: `packages/epcsaft/tests/native/state/test_contributions.py`
- Modify: `packages/epcsaft/src/epcsaft/native/eos/contributions/association.cpp`
- Verify: `packages/epcsaft/tests/native/contracts/test_association_implicit_derivative_contract.py`

### Step 1: Add the failing fixed-density temperature-slope regression

Add `test_association_temperature_derivative_matches_centered_helmholtz_slope` using `_ionic_state()` only as a retained associating runtime fixture. The defect is in the association term, not in Debye--Huckel or Born.

At fixed density and composition:

1. Evaluate the analytic `assoc` term returned by `temperature_derivative_residual_helmholtz(return_contribution_terms=True)`.
2. Evaluate the association Helmholtz contribution at `T + 0.01 K` and `T - 0.01 K`.
3. Form the centered slope `(a_assoc(T+h)-a_assoc(T-h))/(2h)`.
4. Require a nontrivial slope and compare with `rel=2e-6`, `abs=2e-9`.

Pre-fix evidence at the retained state:

```text
analytic association d(a_res)/dT: 0.0032659862738105886 K^-1
centered finite difference:         0.026396826879748758 K^-1
analytic / finite difference:       0.12372647245401315
```

### Step 2: Prove RED

Run:

```bash
uv run --no-sync python run_pytest.py \
  packages/epcsaft/tests/native/state/test_contributions.py \
  -q -k association_temperature_derivative_matches_centered_helmholtz_slope
```

Expected: one failure with the values above.

### Step 3: Use the baseline association-strength prefactor in `dDelta/dT`

In the `include_dt` block of `association_intermediate_state_cpp`:

- Remove the local `pair_diameter_cpp(d_i, d_j)` prefactor from `ddelta_dt`.
- Use the same `sigma_ij^3 * kappa_ij` prefactor used by `association_setup_cpp`:

```cpp
const int pair_index = site_component_index[i] * ncomp + site_component_index[j];
ddelta_dt[i * num_sites + j] = std::pow(thermo.s_ij[pair_index], 3) * volABij * (
    -eABij / std::pow(t, 2) * std::exp(eABij / t) * hc_state.ghs[pair_index]
    + (*dghs_dt)[pair_index] * (std::exp(eABij / t) - 1.0)
);
```

Do not change `pair_diameter_cpp` in hard-sphere contact derivatives; there it is the required `d_i d_j/(d_i+d_j)` geometry. Do not change the active association baseline to Chapman original-SAFT `d_ij^3`.

### Step 4: Correct equation-owner metadata at the same seam

The comment `// EqID: dx_assoc_drho` currently precedes `association_site_fraction_dt_cpp` and falsely assigns the density derivative to the temperature solver. Remove it from that symbol and attach it to `association_site_fraction_density_terms_cpp`, alongside the density-chain implementation it actually represents.

Add `// EqID: ddelta_assoc_dT` immediately above the `ddelta_dt` construction after the TeX EqID is introduced in Task 3.

### Step 5: Rebuild and prove GREEN

Run:

```bash
uv run --no-sync python scripts/dev/build_epcsaft.py --profile provider
uv run --no-sync python run_pytest.py \
  packages/epcsaft/tests/native/state/test_contributions.py \
  packages/epcsaft/tests/native/contracts/test_association_implicit_derivative_contract.py \
  -q
```

Expected: the new finite-difference test and all association implicit-derivative contracts pass.

### Step 6: Prove which outputs can change and commit

At the retained state, confirm that `ares`, `z`, pressure, and fixed-temperature fugacity remain unchanged while `d(a_assoc)/dT`, `hres`, and `sres` reflect the repaired temperature chain.

Label the result:

- **Verified:** isothermal pressure/composition/fugacity curves do not call this derivative.
- **Inference:** caloric predictions and any solver explicitly consuming temperature derivatives can change.
- **Unknown:** the numerical change in a downstream workflow until that workflow is run with a rebuilt provider.

Commit:

```bash
git add packages/epcsaft/tests/native/state/test_contributions.py \
  packages/epcsaft/src/epcsaft/native/eos/contributions/association.cpp
git commit -m "fix: differentiate the PC-SAFT association strength consistently"
```

---

## Task 3: Correct the neutral/base PC-SAFT TeX source

**Files:**

- Modify: `docs/latex/equations.tex`
- Read-only: `docs/latex/algorithms.tex`
- Literature: `/home/tnnrpolley21/Workspaces/Engineering/ePC-SAFT/docs/papers/md/ePC-SAFT-Literature/Chapman et al. - 1990 - Phase Equilibria in Polymer-Liquid 1-Liquid 2 Systems.md`
- Literature: locally retained Gross/Sadowski and Huang/Radosz source records

### Step 1: Make density conventions dimensionally explicit

In the Density section, define:

```tex
\rho_m \;[\mathrm{mol\,m^{-3}}],\qquad
\rho_N=N_A\rho_m \;[\mathrm{m^{-3}}],\qquad
\hat\rho=10^{-30}\rho_N \;[\mathrm{\AA^{-3}}].
```

Use `\hat\rho` wherever the formula multiplies density by diameters or volumes in angstrom units, including:

- `zeta_n`, `zeta_n_xk`, and `zeta_n_dT`;
- the density recovered from `eta`;
- `ares_disp`, its density/composition/temperature forms, and the explicit mixed-moment prefactors;
- `rho_j_assoc` and association mass action when `Delta` is in `angstrom^3`.

Keep `\rho_m` in pressure, molar-property, and SI state equations. Add the derivative invariant

```tex
\rho_m\frac{\partial}{\partial\rho_m}
=\rho_N\frac{\partial}{\partial\rho_N}
=\hat\rho\frac{\partial}{\partial\hat\rho}.
```

Do not migrate Debye--Huckel/Born notation in this slice; add one sentence that their SI density conventions are audited separately.

### Step 2: Correct hard-sphere and hard-chain equations

- In `g_hs_contact`, replace the stray `xi_2`, `xi_3` with `zeta_2`, `zeta_3`.
- In `ghs_contact_dT`, replace the stray `xi` symbols and derivatives with `zeta`.
- Normalize composition derivative conditions to fixed `T`, fixed `hat rho`, and `x_{j != k}`.
- In `hc_ares_dxk`, insert the direct derivative term

```tex
-(m_k-1)\ln g_{kk}^{\mathrm{hs}}
```

before the indirect contact-value sum.

Record this formula as **verified derived** from the hard-chain baseline (Gross and Sadowski Eq. A.4) and corroborated by Chapman Appendix A.6. Do not claim it is a verbatim match to Gross Appendix Eq. A.35, whose local print omits the direct term.

### Step 3: Correct dispersion equations and define the temperature chain

- Apply `^{-1}` to the entire parenthesis defining `C_1`.
- Correct `deta_i2_deta` to `sum_{j=0}^6 b_j(mbar)(j+1) eta^j`.
- Correct the last mixed-moment derivative in `disp_ares_dxk` to the derivative of the overlined second mixed moment, not `(bar m^2 epsilon^2 sigma^3)_{xk}`.
- Correct source metadata: first mixed moment and `I_1` to Gross Eqs. A.12 and A.16, `d(eta I_1)/deta` to A.29, `a_i` to A.18, and `b_i` to A.19.
- Add explicit EqIDs for the helper chain consumed by `disp_ares_dT`:

```tex
\left(\overline{m^2\epsilon\sigma^3}\right)_{,T}
=-\frac{1}{T}\overline{m^2\epsilon\sigma^3},
```

```tex
\left(\overline{m^2\epsilon^2\sigma^3}\right)_{,T}
=-\frac{2}{T}\overline{m^2\epsilon^2\sigma^3},
```

```tex
I_{1,T}=\sum_{i=0}^6 a_i(\bar m)i\eta^{i-1}\eta_T,
\qquad
I_{2,T}=\sum_{i=0}^6 b_i(\bar m)i\eta^{i-1}\eta_T,
```

```tex
C_{1,T}=C_2\eta_T
```

at fixed composition. Mark these helpers as derived from Gross Eqs. A.12--A.19 and A.58--A.61.

### Step 4: Reconcile association with PC-SAFT and Chapman lineage

Replace `delta_assoc` with the active PC-SAFT convention:

```tex
\Delta^{A_iB_j}
=\sigma_{ij}^{3}\kappa^{A_iB_j}g_{ij}^{\mathrm{hs}}
\left[\exp\!\left(\frac{\epsilon^{A_iB_j}}{kT}\right)-1\right].
```

Use the same prefactor in its density, composition, and new temperature derivative:

```tex
\left(\frac{\partial\Delta^{A_iB_j}}{\partial T}\right)_{\hat\rho,x}
=\sigma_{ij}^{3}\kappa^{A_iB_j}
\left[
g_{ij,T}^{\mathrm{hs}}\left(e^{\epsilon^{A_iB_j}/kT}-1\right)
-g_{ij}^{\mathrm{hs}}\frac{\epsilon^{A_iB_j}}{kT^2}e^{\epsilon^{A_iB_j}/kT}
\right].
```

Assign the new EqID `ddelta_assoc_dT`.

Metadata must distinguish:

- Huang and Radosz SAFT Eq. 19: pure-component `sigma^3 kappa` lineage retained in the active pair-indexed PC-SAFT convention.
- Chapman original-SAFT Eq. 24: `d_ij^3 kappa`, with arithmetic `d_ij`.
- Chapman Eq. 21: association Helmholtz energy.
- Chapman Eq. 22 sequence: site mass-action relation.
- Chapman Eq. 23: component density `rho_j = x_j rho`.
- Chapman Eqs. 25--28: contact value, packing moments, and hard-chain lineage.

### Step 5: Audit `algorithms.tex` without redesign

Confirm it does not independently redefine the neutral EOS or override the corrected EqIDs. If it only points readers to equation/property owners, record **documentation-only match** and leave the file unchanged. If a broken pointer is found, stop and report it before expanding this plan.

### Step 6: Run source-level checks

Run:

```bash
rg -n "\\\\xi_[23]|\\\\boldsymbol\\{\\\\rho\\}|rho_\\{j\\\\neq k\\}|bar\\{m\\}\^2" docs/latex/equations.tex
rg -n "EqID: (zeta_n|g_hs_contact|hc_ares_dxk|c1_disp|deta_i2_deta|disp_ares_dxk|ddelta_assoc_dT|delta_assoc)" docs/latex/equations.tex
```

Expected: no stale neutral-slice symbol mixups; each corrected relation has one stable EqID.

---

## Task 4: Regenerate equation views and close the unknown leads

**Files:**

- Modify by generator: `docs/equations.md`
- Modify by generator: `docs/equations_registry.yaml`
- Verify: `tests/native/contracts/test_equation_registry.py`
- Optionally modify: `packages/epcsaft/tests/native/state/test_eos_contributions.py` only if a separate hard-chain parity test is needed

### Step 1: Regenerate, never hand-edit, the equation views

Run:

```bash
uv run --no-sync python scripts/docs/sync_equation_registry.py
uv run --no-sync python scripts/docs/sync_equation_registry.py \
  --check --strict-traceability --docs-only-audit
```

The regeneration is also expected to absorb the pre-existing registry drift from provider parameter-access signature changes. Review that generated diff separately from scientific equation changes.

### Step 2: Verify the four reconnaissance leads

Record the final outcomes in the implementation handoff:

1. **Molar density vs number density -- verified convention translation plus TeX defect:** C++ converts `rho_m` to `hat rho` via `rho * N_A / 1e30`; the TeX packing/dispersion equations previously used molar `rho` beside angstrom powers without showing that conversion.
2. **Zeta vs xi -- verified TeX defect:** C++ and Gross use the same packing moments; only two TeX contact-value formulas contain stray `xi` symbols.
3. **Association volume kappa in Delta -- verified TeX defect:** active C++ includes `volABij`; TeX baseline omitted it. The `sigma^3` versus Chapman `d^3` difference is a verified PC-SAFT/original-SAFT convention translation.
4. **Direct hard-chain composition term -- verified TeX defect, C++ match:** compare public analytic hard-chain derivatives with the canonical CppAD tape at unequal segment numbers and confirm the direct `-(m_k-1) ln g_kk` contribution is present in `hard_chain.cpp`.

If existing tests do not independently expose item 4, add a focused mode-0/canonical hard-chain parity assertion to `test_eos_contributions.py` using the same neutral state as Task 1.

### Step 3: Run the focused M3 verification set

Run:

```bash
uv run --no-sync python run_pytest.py \
  packages/epcsaft/tests/native/state/test_eos_contributions.py \
  packages/epcsaft/tests/native/state/test_contributions.py \
  packages/epcsaft/tests/native/contracts/test_association_implicit_derivative_contract.py \
  tests/native/contracts/test_equation_registry.py \
  -q
```

Then run the retained hydrocarbon public-property regression and provider
health check:

```bash
uv run --no-sync python run_pytest.py \
  packages/epcsaft/tests/api/frontend/test_state_properties.py \
  -q -k cppad_state_proves_hydrocarbon_values_and_derivatives

uv run --no-sync python scripts/dev/doctor.py \
  --require-provider-sdk --require-provider-native
```

Expected: all selected tests pass and the provider doctor reports a current CppAD-enabled native extension.

### Step 4: Classify remaining unknowns instead of guessing

- **Unknown:** whether Gross Appendix Eq. A.35 has a published erratum for its omitted direct hard-chain term unless a retained erratum is located. The implemented/documented formula remains justified by direct differentiation and Chapman Appendix A.6.
- **Unknown/deferred:** numerical changes in full electrolyte Figiel/Cameretti reproduction campaigns. Defect 1 does not affect current auto-mode results; defect 2 affects temperature derivatives but not the isothermal EOS values plotted by those campaigns unless they explicitly consume caloric/temperature-Jacobian outputs.
- **Deferred by scope:** Debye--Huckel, Born, and equilibrium-algorithm equation reconciliation; no edits are authorized here.
- **Build blocker if present:** a full bibliography-resolved PDF cannot be claimed unless `docs/latex/references.bib` is available in this worktree. The equation registry and LaTeX source checks remain mandatory.

### Step 5: Commit documentation and generated views

Run:

```bash
git add docs/latex/equations.tex docs/equations.md docs/equations_registry.yaml
git commit -m "docs: reconcile neutral PC-SAFT equations and conventions"
```

Do not stage `docs/latex/algorithms.tex` if the audit confirms it needs no change.

---

## Task 5: Final scientific and repository review

### Step 1: Review the complete branch diff

Run:

```bash
git diff --check
git diff --stat a5790e7c...HEAD
git status --short
```

Review every changed scientific relation against its C++ owner and retained source. The final report must label each material conclusion as verified, inference, assumption, or unknown.

### Step 2: Run the repository cleanup audit

Run:

```bash
bash "$HOME/.codex/hooks/codex-cleanup.sh" --repo-root .
```

Use explicit cleanup mode only for task-owned ignored artifacts, including failed pytest temporary directories created by this task. Do not remove user-owned or pre-existing files.

### Step 3: Stop before external integration

Report the local branch and commits, the exact verification commands and results, and any unresolved literature/build blockers. Do not push, open a pull request, merge, or modify the dirty source checkout without separate approval.
