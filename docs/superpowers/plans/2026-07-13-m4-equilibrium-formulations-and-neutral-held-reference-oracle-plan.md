# Equilibrium Formulations And Neutral HELD Reference Oracle Plan

> **For agentic workers:** Use `chemical-engineer` for source and numerical
> reconciliation, `superpowers:executing-plans` for this bounded plan,
> `superpowers:test-driven-development` for the executable oracle, and
> `superpowers:verification-before-completion` at both phase gates.

**Goal:** Establish one publication-grade mathematical owner for the M4
equilibrium families, then implement a deliberately non-production neutral
HELD direct-minimization oracle on manufactured free-energy surfaces.

**Architecture:** Phase A is a standalone LaTeX specification. It distinguishes
seven non-equated formulation families, records source and implementation
status, and owns all equations introduced by this slice. Phase B is an isolated
NumPy analysis under `analyses/reference_oracles/neutral_held/`; it exposes an
evaluator protocol and manufactured solver/evidence machinery without entering
the installed package or reproducing the ePC-SAFT EOS.

**Tech Stack:** LaTeX/`latexmk`, in-file `thebibliography`, Python 3.13, NumPy,
pytest, repository text/workflow validators, and Git.

## Scope And Ownership

- Create `docs/latex/equilibrium_formulations.tex` as the only mathematical
  owner for this slice. Do not edit or include `equations.tex` or
  `algorithms.tex`.
- Do not edit the July 12 recovery specification or program plan.
- Do not modify Stage 4 resolved-input code or its stale equation registry.
- Keep public capability unchanged: `bubble_pressure`, `dew_pressure`, and the
  scoped methane/ethane/propane `single_component_vle` route only.
- Keep Phase B outside `packages/epcsaft-equilibrium` and stop after the neutral
  manufactured topology.
- Do not add SciPy or the retired Python Ipopt wrapper to the reference-oracle
  tree. Repository
  structure policy currently prohibits those analysis dependencies outside the
  separately owned explicit-association toybox. The oracle will report that
  backend decision explicitly and use deterministic NumPy local solves plus an
  independent low-dimensional enumeration.
- Do not push or publish.

## Phase A: Canonical Mathematical Specification

### Task A1: Add a document contract before the document

**Files:**

- Create: `tests/workflows/repo/test_equilibrium_formulations_document.py`

**RED requirements:**

- Require the canonical TeX file and its seven family sections.
- Require the evidence vocabulary `verified`, `inference`, `assumption`, and
  `unknown`.
- Require every local label to use the `eqform` namespace and be unique.
- Require local references/citations to resolve and local labels to remain
  disjoint from the other standalone TeX owners.
- Require source-reconciliation and consistency-review tables.
- Reject `\input`/`\include`, copied EqID metadata, and any public-capability
  expansion.

Run the focused test and retain the expected missing-document failure.

### Task A2: Author the standalone formal specification

**Files:**

- Create: `docs/latex/equilibrium_formulations.tex`

**Required contents:**

- Shared notation, evidence labels, ensembles, domains, phase topology,
  electrochemical/Galvani convention, EOS derivative contract, and common KKT
  vocabulary.
- Separate sections for public pressure boundaries and scoped pure saturation;
  Pereira neutral HELD; association-aware neutral HELD; Perdomo modified-mole
  HELD2; Ascani counterion-pair equilibrium; standalone CE; and separately
  designed CPE.
- For every family: source/status, variables, objective or residual map,
  constraints/domains, balances, phase appearance, derivatives, KKT and an
  independent certificate, scaling/initialization, multiplicity/global limits,
  acceptance/failure semantics, and non-equivalence to adjacent families.
- A source-to-formulation reconciliation table that marks every equation group
  and every unresolved point.
- A thermodynamic/numerical consistency appendix covering degrees of freedom,
  units/bases, constraint rank, certificate independence, derivative needs,
  and phase degeneracy.
- Stable DOI links in an in-file bibliography so the isolated worktree builds
  without the ignored Zotero export or unavailable `biber` backend.

### Task A3: Integrate the build entrypoint

**Files:**

- Modify: `docs/pages/development_workflows.rst`
- Modify: `tests/workflows/repo/test_workflow_entrypoints.py`

Add the literal `latexmk -pdf equilibrium_formulations.tex` beside the existing
standalone LaTeX build commands and extend the existing workflow contract.

### Task A4: Phase A review and checkpoint

Run:

```bash
cd docs/latex
latexmk -pdf -interaction=nonstopmode -halt-on-error -file-line-error equilibrium_formulations.tex
test -s builds/equilibrium_formulations.pdf
! rg -n 'LaTeX Warning:.*(undefined|multiply defined)|There were undefined references|There were undefined citations|Citation .* undefined|Label .* multiply defined' builds/equilibrium_formulations.log
pdftotext builds/equilibrium_formulations.pdf - | rg -n '\?\?' && exit 1 || true
```

Then run the focused document/workflow tests, algorithm-registry check, text
gates, `git diff --check`, scientific consistency review, and cleanup hook.
Record the pre-existing Stage 4 equation-registry drift without modifying it.
Commit Phase A as a focused local checkpoint before beginning Phase B.

## Phase B: Neutral HELD Manufactured Reference Oracle

### Task B1: Add the analysis contract and failing tests

**Files:**

- Create: `analyses/reference_oracles/neutral_held/README.md`
- Create: `analyses/reference_oracles/neutral_held/analysis.yaml`
- Create: `analyses/reference_oracles/neutral_held/tests/test_oracle.py`

The tests must fail before implementation and cover:

- a global single-phase or phase-disappearance boundary;
- an interior two-phase global solution;
- a local/metastable stationary solution rejected by enumeration/objective
  comparison;
- invalid feed/domain input;
- analytic objective gradients and constraint Jacobians against central finite
  differences;
- material and volume-related stationarity checks, KKT residuals, independent
  common-tangent/chemical-potential certificates, deterministic starts, and
  explicit backend identity.

### Task B2: Implement the minimal evaluator and oracle

**Files:**

- Create: `analyses/reference_oracles/neutral_held/oracle.py`

Implement:

- a small evaluator protocol for an extensive Helmholtz/free-energy phase
  function and analytic derivatives;
- a manufactured binary free-energy evaluator with known competing wells and
  a convex phase-volume term;
- the two-candidate-phase fixed-`T,P,N` direct total-free-energy problem with
  exact balance/domain constraints;
- a deterministic multistart NumPy local solver whose local-only status is
  explicit;
- an independent one-dimensional/two-composition enumeration and analytic
  stationary-point evidence;
- result records with objective ordering, phase topology, balance residuals,
  derivative receipts, KKT/stationarity diagnostics, independent equilibrium
  certificates, and clear rejection/failure reasons.

No package adapter, association, electrolyte, CE, CPE, SciPy fallback, or
ePC-SAFT prediction belongs in this phase.

### Task B3: Phase B verification and checkpoint

Run the focused analysis tests repeatedly to prove deterministic behavior, then
run project-structure/text tests, Ruff on the new Python files, `git diff
--check`, and the cleanup hook. Confirm no public/package files changed and no
task-owned processes or ignored artifacts remain. Commit Phase B locally and
stop before the next algorithm family.

## Completion Evidence

- Phase A and Phase B each have a focused local commit.
- The new TeX PDF builds without unresolved labels/citations.
- Every formulation equation group is source-labeled and reconciled; unknowns
  stay explicit.
- The manufactured oracle distinguishes a local solver result from independent
  evidence of the global minimum.
- Public activation and ownership maps remain unchanged.
- No push, capability admission, full EOS duplication, or cross-family oracle
  expansion occurs.
