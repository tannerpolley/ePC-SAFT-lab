# Explicit Association Toybox HC Dispersion Extension Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Extend the existing Python-only explicit association toybox with tiny scalar hard-chain and dispersion residual Helmholtz context terms so closure studies can report total neutral `ares` error and timing against the exact implicit association baseline.

**Architecture:** Keep the toybox under `analyses/package_validation/explicit_association_toybox` and add three focused analysis modules: validated neutral PC-SAFT inputs, hard-chain scalar helpers, and dispersion scalar helpers. The existing grid and metrics path will keep exact association and closure association side by side, then add identical `ares_hc` and `ares_disp` context terms for each state so total residual Helmholtz differences isolate association-closure error.

**Tech Stack:** Python, NumPy, PyYAML, Matplotlib, pytest through `uv run python run_pytest.py`; no SciPy, package runtime API, native C++, equilibrium, or regression changes.

---

## Intake

Source spec:

- `docs/superpowers/specs/2026-06-03-m3-eos-explicit-association-toybox-design.md`
- Related follow-up spec:
  `docs/superpowers/specs/2026-06-03-m3-eos-paper-backed-association-closure-validation-matrix-design.md`

Issue mirror:

- `docs/superpowers/issues/2026-06-03-m3-eos-issue-0216-add-hc-and-dispersion-context-to-the-explicit-association-toybox.md`
- GitHub Issue: `https://github.com/ePC-SAFT/ePC-SAFT/issues/216`

Milestone and package ownership:

- Milestone: `M3 - EOS`
- Package boundary: analysis-only support for provider EOS research.
- Allowed runtime scope: `analyses/package_validation/explicit_association_toybox/**`
- Excluded runtime scope: `packages/epcsaft/**`, `packages/epcsaft-equilibrium/**`, `packages/epcsaft-regression/**`

Reference evidence:

- Local equation docs own `m_bar`, `zeta_n`, `zeta3_eta`, `ares_hs`, `ares_hc`, dispersion polynomial helpers, and `ares_disp`.
- Native reference formulas live in `packages/epcsaft/src/epcsaft/native/eos/residual/cppad/hard_chain_dispersion.h`, `packages/epcsaft/src/epcsaft/native/eos/contributions/hard_chain.cpp`, `packages/epcsaft/src/epcsaft/native/eos/contributions/dispersion.cpp`, and `packages/epcsaft/src/epcsaft/native/eos/core_internal.h`.
- The linked legacy MEA script is reference material for workflow shape only. Equations must be written from local repo docs and existing toybox conventions.

## Non-Goals

- No density solve or phase root selection.
- No pressure, fugacity, activity, chemical-potential, derivative, Jacobian, Hessian, equilibrium, regression, ionic, Born, dielectric, polar, or public package API work.
- No SciPy import or dependency.
- No provider native cross-check as a required baseline for the Python formulas.
- No broad analysis folder migration. Preserve the current toybox `figures/<figure_id>/output` convention already recorded in `analysis.yaml`.
- No full paper-backed topology matrix, real vapor-pressure/liquid-density
  parity workflow, or production evidence claim for 2B/3B/4C closures. Those
  belong to the related validation-matrix spec and a separate later plan.

## File Map

Create:

- `analyses/package_validation/explicit_association_toybox/scripts/pcsaft_inputs.py`  
  Small dataclasses and validated array helpers for neutral fixed-state PC-SAFT inputs.
- `analyses/package_validation/explicit_association_toybox/scripts/hard_chain.py`  
  Scalar `ares_hs` and `ares_hc` helpers for fixed `T`, `rho`, and `x`.
- `analyses/package_validation/explicit_association_toybox/scripts/dispersion.py`  
  Scalar dispersion polynomial helpers, mixed dispersion moments, and `ares_disp`.
- `analyses/package_validation/explicit_association_toybox/tests/test_neutral_pcsaft_scalar_terms.py`  
  Tests for input validation, hard-chain limits, dispersion finite values, and closure independence.
- `analyses/package_validation/explicit_association_toybox/tests/test_total_ares_metrics.py`  
  Tests for total residual Helmholtz metric columns and timing/speedup columns.
- `analyses/package_validation/explicit_association_toybox/figures/residual_ares_error/scripts/generate_data.py`  
  Figure data command that writes total `ares` metrics for the existing grid.
- `analyses/package_validation/explicit_association_toybox/figures/residual_ares_error/scripts/render_figure.py`  
  Figure render command for total residual Helmholtz closure error.

Modify:

- `analyses/package_validation/explicit_association_toybox/config/systems.yaml`  
  Add neutral PC-SAFT scalar state fields to each system.
- `analyses/package_validation/explicit_association_toybox/scripts/metrics.py`  
  Add optional exact/closure total `ares` fields and timing fields.
- `analyses/package_validation/explicit_association_toybox/scripts/run_grid.py`  
  Load fixed neutral PC-SAFT state inputs and pass scalar context to metrics.
- `analyses/package_validation/explicit_association_toybox/figures/closure_accuracy/scripts/render_figure.py`  
  Keep current plot intact while tolerating the expanded CSV schema.
- `analyses/package_validation/explicit_association_toybox/README.md`  
  Document the small HC/dispersion scope and commands.
- `analyses/package_validation/explicit_association_toybox/analysis.yaml`  
  Add the residual `ares` figure commands.

Test:

- `analyses/package_validation/explicit_association_toybox/tests/test_exact_2b_reduction.py`
- `analyses/package_validation/explicit_association_toybox/tests/test_mass_action_metrics.py`
- `analyses/package_validation/explicit_association_toybox/tests/test_output_schema.py`
- `analyses/package_validation/explicit_association_toybox/tests/test_neutral_pcsaft_scalar_terms.py`
- `analyses/package_validation/explicit_association_toybox/tests/test_total_ares_metrics.py`

## Data Contract

Each system entry in `config/systems.yaml` receives fixed neutral PC-SAFT state fields:

```yaml
pcsaft:
  temperature: 303.15
  density: 0.01
  segments: [2.0]
  sigma: [3.0]
  epsilon_over_k: [200.0]
  k_ij: [[0.0]]
```

For multi-component systems, all arrays must match `component_count`, `k_ij` must be square, and `composition_grid` rows must still sum to one.

The grid output keeps existing columns and adds:

```text
temperature
pcsaft_density
ares_hc
ares_disp
ares_assoc_exact
ares_assoc_closure
ares_total_exact
ares_total_closure
ares_total_abs_error
ares_total_rel_error
exact_elapsed_seconds
closure_elapsed_seconds
speedup_ratio
```

`density` remains the association mass-action density from the current toybox. `pcsaft_density` is the neutral PC-SAFT scalar density used for HC/dispersion. The first implementation should set them equal in config so the CSV makes the relationship explicit without adding density-solving behavior.

## Acceptance Criteria

- HC and dispersion scalar helpers are source-backed by local equation IDs and return finite scalar values for the configured fixed states.
- Hard-chain and dispersion terms are identical for exact and explicit association rows at the same state and do not depend on the closure name.
- The toybox reports total neutral `ares` exact/closure values, absolute and relative total `ares` error, exact solve time, closure time, and speedup ratio.
- The residual `ares` figure command writes retained plotted data, a PNG, and an PDF artifact under `figures/residual_ares_error/output`.
- The toybox contains no SciPy imports and no dependency change.
- No `packages/epcsaft`, `packages/epcsaft-equilibrium`, or `packages/epcsaft-regression` files change.

## Required Development Skills

- Use `superpowers:test-driven-development` for Tasks 1 through 6.
- Use `chemical-engineer` during equation transcription checks.
- Use `superpowers:verification-before-completion` before claiming execution complete.

## Task 1: Lock The Fixed-State Input Contract

**Files:**

- Create: `analyses/package_validation/explicit_association_toybox/scripts/pcsaft_inputs.py`
- Modify: `analyses/package_validation/explicit_association_toybox/config/systems.yaml`
- Test: `analyses/package_validation/explicit_association_toybox/tests/test_neutral_pcsaft_scalar_terms.py`

- [ ] **Step 1: Write the failing input-contract tests**

Add these tests to `analyses/package_validation/explicit_association_toybox/tests/test_neutral_pcsaft_scalar_terms.py`:

```python
from __future__ import annotations

import numpy as np
import pytest

from analyses.package_validation.explicit_association_toybox.scripts.pcsaft_inputs import (
    ToyPCSAFTState,
    state_from_config,
)


def test_state_from_config_validates_component_shapes() -> None:
    state = state_from_config(
        {
            "temperature": 303.15,
            "density": 0.01,
            "segments": [2.0, 1.0],
            "sigma": [3.0, 3.5],
            "epsilon_over_k": [200.0, 150.0],
            "k_ij": [[0.0, 0.02], [0.02, 0.0]],
        },
        component_count=2,
        composition=np.array([0.25, 0.75]),
    )

    assert isinstance(state, ToyPCSAFTState)
    assert state.component_count == 2
    assert np.allclose(state.composition, [0.25, 0.75])
    assert state.temperature == pytest.approx(303.15)
    assert state.density == pytest.approx(0.01)


def test_state_from_config_rejects_shape_mismatch() -> None:
    with pytest.raises(ValueError, match="segments length must match component_count"):
        state_from_config(
            {
                "temperature": 303.15,
                "density": 0.01,
                "segments": [2.0],
                "sigma": [3.0, 3.5],
                "epsilon_over_k": [200.0, 150.0],
                "k_ij": [[0.0, 0.02], [0.02, 0.0]],
            },
            component_count=2,
            composition=np.array([0.25, 0.75]),
        )


def test_state_from_config_rejects_non_normalized_composition() -> None:
    with pytest.raises(ValueError, match="composition must sum to one"):
        state_from_config(
            {
                "temperature": 303.15,
                "density": 0.01,
                "segments": [2.0, 1.0],
                "sigma": [3.0, 3.5],
                "epsilon_over_k": [200.0, 150.0],
                "k_ij": [[0.0, 0.02], [0.02, 0.0]],
            },
            component_count=2,
            composition=np.array([0.25, 0.70]),
        )
```

- [ ] **Step 2: Run the new test and verify the expected failure**

Run:

```powershell
uv run python run_pytest.py analyses/package_validation/explicit_association_toybox/tests/test_neutral_pcsaft_scalar_terms.py -q
```

Expected: fail during import because `scripts.pcsaft_inputs` does not exist.

- [ ] **Step 3: Add the input dataclass and validation helpers**

Create `analyses/package_validation/explicit_association_toybox/scripts/pcsaft_inputs.py` with this structure:

```python
from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

import numpy as np

N_AV = 6.02214076e23


@dataclass(frozen=True)
class ToyPCSAFTState:
    temperature: float
    density: float
    composition: np.ndarray
    segments: np.ndarray
    sigma: np.ndarray
    epsilon_over_k: np.ndarray
    k_ij: np.ndarray

    def __post_init__(self) -> None:
        object.__setattr__(self, "composition", _as_vector("composition", self.composition))
        object.__setattr__(self, "segments", _as_vector("segments", self.segments))
        object.__setattr__(self, "sigma", _as_vector("sigma", self.sigma))
        object.__setattr__(self, "epsilon_over_k", _as_vector("epsilon_over_k", self.epsilon_over_k))
        object.__setattr__(self, "k_ij", np.asarray(self.k_ij, dtype=float))
        if not np.isfinite(self.temperature) or self.temperature <= 0.0:
            raise ValueError("temperature must be positive and finite.")
        if not np.isfinite(self.density) or self.density <= 0.0:
            raise ValueError("density must be positive and finite.")
        if not np.isclose(float(np.sum(self.composition)), 1.0):
            raise ValueError("composition must sum to one.")
        if np.any(self.composition < 0.0):
            raise ValueError("composition must be nonnegative.")
        if np.any(self.segments <= 0.0):
            raise ValueError("segments must be positive.")
        if np.any(self.sigma <= 0.0):
            raise ValueError("sigma must be positive.")
        if np.any(self.epsilon_over_k <= 0.0):
            raise ValueError("epsilon_over_k must be positive.")
        n = self.component_count
        if self.k_ij.shape != (n, n):
            raise ValueError("k_ij must be square with shape (component_count, component_count).")

    @property
    def component_count(self) -> int:
        return int(self.composition.size)

    @property
    def number_density(self) -> float:
        return float(self.density * N_AV / 1.0e30)

    @property
    def m_bar(self) -> float:
        return float(np.dot(self.composition, self.segments))

    @property
    def segment_diameter(self) -> np.ndarray:
        return self.sigma * (1.0 - 0.12 * np.exp(-3.0 * self.epsilon_over_k / self.temperature))


def _as_vector(name: str, value: object) -> np.ndarray:
    array = np.asarray(value, dtype=float)
    if array.ndim != 1:
        raise ValueError(f"{name} must be one-dimensional.")
    if not np.all(np.isfinite(array)):
        raise ValueError(f"{name} must contain finite values.")
    return array


def state_from_config(
    config: Mapping[str, object],
    *,
    component_count: int,
    composition: np.ndarray,
) -> ToyPCSAFTState:
    segments = _as_vector("segments", config["segments"])
    if segments.size != component_count:
        raise ValueError("segments length must match component_count.")
    sigma = _as_vector("sigma", config["sigma"])
    if sigma.size != component_count:
        raise ValueError("sigma length must match component_count.")
    epsilon_over_k = _as_vector("epsilon_over_k", config["epsilon_over_k"])
    if epsilon_over_k.size != component_count:
        raise ValueError("epsilon_over_k length must match component_count.")
    return ToyPCSAFTState(
        temperature=float(config["temperature"]),
        density=float(config["density"]),
        composition=np.asarray(composition, dtype=float),
        segments=segments,
        sigma=sigma,
        epsilon_over_k=epsilon_over_k,
        k_ij=np.asarray(config.get("k_ij", np.zeros((component_count, component_count))), dtype=float),
    )
```

- [ ] **Step 4: Add `pcsaft` blocks to each configured system**

Modify each system in `analyses/package_validation/explicit_association_toybox/config/systems.yaml`.

Use values with the right length for the component count:

```yaml
    pcsaft:
      temperature: 303.15
      density: 0.01
      segments: [2.0]
      sigma: [3.0]
      epsilon_over_k: [200.0]
      k_ij:
        - [0.0]
```

For two-component systems use:

```yaml
    pcsaft:
      temperature: 303.15
      density: 0.01
      segments: [2.0, 1.0]
      sigma: [3.0, 3.5]
      epsilon_over_k: [200.0, 150.0]
      k_ij:
        - [0.0, 0.0]
        - [0.0, 0.0]
```

- [ ] **Step 5: Run the input tests and commit**

Run:

```powershell
uv run python run_pytest.py analyses/package_validation/explicit_association_toybox/tests/test_neutral_pcsaft_scalar_terms.py -q
```

Expected: all tests in the file pass.

Commit:

```powershell
git add analyses/package_validation/explicit_association_toybox/scripts/pcsaft_inputs.py analyses/package_validation/explicit_association_toybox/config/systems.yaml analyses/package_validation/explicit_association_toybox/tests/test_neutral_pcsaft_scalar_terms.py
git commit -m "test: add fixed pcsaft state contract"
```

## Task 2: Add Hard-Chain Scalar Helpers

**Files:**

- Create: `analyses/package_validation/explicit_association_toybox/scripts/hard_chain.py`
- Modify: `analyses/package_validation/explicit_association_toybox/tests/test_neutral_pcsaft_scalar_terms.py`

- [ ] **Step 1: Write failing hard-chain tests**

Append these tests:

```python
from analyses.package_validation.explicit_association_toybox.scripts.hard_chain import (
    ares_hc,
    ares_hs,
    hard_chain_state,
)


def test_hard_chain_reduces_to_hard_sphere_for_monomer() -> None:
    state = ToyPCSAFTState(
        temperature=303.15,
        density=0.01,
        composition=np.array([1.0]),
        segments=np.array([1.0]),
        sigma=np.array([3.0]),
        epsilon_over_k=np.array([200.0]),
        k_ij=np.array([[0.0]]),
    )
    hc = hard_chain_state(state)

    assert hc.eta > 0.0
    assert ares_hc(state, hc) == pytest.approx(ares_hs(hc))


def test_hard_chain_returns_finite_scalar_for_binary_state() -> None:
    state = state_from_config(
        {
            "temperature": 303.15,
            "density": 0.01,
            "segments": [2.0, 1.0],
            "sigma": [3.0, 3.5],
            "epsilon_over_k": [200.0, 150.0],
            "k_ij": [[0.0, 0.0], [0.0, 0.0]],
        },
        component_count=2,
        composition=np.array([0.5, 0.5]),
    )
    value = ares_hc(state, hard_chain_state(state))

    assert np.isfinite(value)
    assert value > 0.0
```

- [ ] **Step 2: Run the test and verify the expected failure**

Run:

```powershell
uv run python run_pytest.py analyses/package_validation/explicit_association_toybox/tests/test_neutral_pcsaft_scalar_terms.py -q
```

Expected: fail during import because `scripts.hard_chain` does not exist.

- [ ] **Step 3: Implement hard-chain helpers**

Create `analyses/package_validation/explicit_association_toybox/scripts/hard_chain.py`:

```python
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .pcsaft_inputs import ToyPCSAFTState


@dataclass(frozen=True)
class HardChainState:
    zeta: np.ndarray
    ghs: np.ndarray
    eta: float


def hs_contact_value(pair_diameter: float, zeta2: float, zeta3: float) -> float:
    one_minus_eta = 1.0 - zeta3
    return float(
        1.0 / one_minus_eta
        + pair_diameter * 3.0 * zeta2 / one_minus_eta**2
        + pair_diameter**2 * 2.0 * zeta2**2 / one_minus_eta**3
    )


def hard_chain_state(state: ToyPCSAFTState) -> HardChainState:
    d = state.segment_diameter
    zeta = np.zeros(4, dtype=float)
    for order in range(4):
        zeta[order] = np.pi / 6.0 * state.number_density * np.sum(
            state.composition * state.segments * d**order
        )
    ghs = np.zeros((state.component_count, state.component_count), dtype=float)
    for i in range(state.component_count):
        for j in range(state.component_count):
            pair_diameter = d[i] * d[j] / (d[i] + d[j])
            ghs[i, j] = hs_contact_value(pair_diameter, zeta[2], zeta[3])
    return HardChainState(zeta=zeta, ghs=ghs, eta=float(zeta[3]))


def ares_hs(hc: HardChainState) -> float:
    z0, z1, z2, z3 = hc.zeta
    return float(
        (
            3.0 * z1 * z2 / (1.0 - z3)
            + z2**3 / (z3 * (1.0 - z3) ** 2)
            + (z2**3 / z3**2 - z0) * np.log(1.0 - z3)
        )
        / z0
    )


def ares_hc(state: ToyPCSAFTState, hc: HardChainState) -> float:
    chain_sum = float(np.sum(state.composition * (state.segments - 1.0) * np.log(np.diag(hc.ghs))))
    return float(state.m_bar * ares_hs(hc) - chain_sum)
```

- [ ] **Step 4: Run hard-chain tests and commit**

Run:

```powershell
uv run python run_pytest.py analyses/package_validation/explicit_association_toybox/tests/test_neutral_pcsaft_scalar_terms.py -q
```

Expected: all tests in the file pass.

Commit:

```powershell
git add analyses/package_validation/explicit_association_toybox/scripts/hard_chain.py analyses/package_validation/explicit_association_toybox/tests/test_neutral_pcsaft_scalar_terms.py
git commit -m "feat: add toybox hard-chain scalar terms"
```

## Task 3: Add Dispersion Scalar Helpers

**Files:**

- Create: `analyses/package_validation/explicit_association_toybox/scripts/dispersion.py`
- Modify: `analyses/package_validation/explicit_association_toybox/tests/test_neutral_pcsaft_scalar_terms.py`

- [ ] **Step 1: Write failing dispersion tests**

Append:

```python
from analyses.package_validation.explicit_association_toybox.scripts.dispersion import (
    ares_disp,
    dispersion_polynomials,
    mixed_dispersion_moments,
)


def test_dispersion_polynomials_match_pure_monomer_leading_coefficients() -> None:
    polynomials = dispersion_polynomials(m_bar=1.0, eta=0.05)

    assert polynomials.a[0] == pytest.approx(0.9105631445)
    assert polynomials.b[0] == pytest.approx(0.7240946941)
    assert np.isfinite(polynomials.i1)
    assert np.isfinite(polynomials.i2)
    assert np.isfinite(polynomials.c1)


def test_dispersion_returns_negative_finite_scalar() -> None:
    state = state_from_config(
        {
            "temperature": 303.15,
            "density": 0.01,
            "segments": [2.0, 1.0],
            "sigma": [3.0, 3.5],
            "epsilon_over_k": [200.0, 150.0],
            "k_ij": [[0.0, 0.0], [0.0, 0.0]],
        },
        component_count=2,
        composition=np.array([0.5, 0.5]),
    )
    hc = hard_chain_state(state)
    moments = mixed_dispersion_moments(state)
    value = ares_disp(state, hc, moments)

    assert np.isfinite(value)
    assert value < 0.0
```

- [ ] **Step 2: Run the test and verify the expected failure**

Run:

```powershell
uv run python run_pytest.py analyses/package_validation/explicit_association_toybox/tests/test_neutral_pcsaft_scalar_terms.py -q
```

Expected: fail during import because `scripts.dispersion` does not exist.

- [ ] **Step 3: Implement dispersion helpers**

Create `analyses/package_validation/explicit_association_toybox/scripts/dispersion.py`:

```python
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .hard_chain import HardChainState
from .pcsaft_inputs import ToyPCSAFTState

A0 = np.array([0.9105631445, 0.6361281449, 2.6861347891, -26.547362491, 97.759208784, -159.59154087, 91.297774084])
A1 = np.array([-0.3084016918, 0.1860531159, -2.5030047259, 21.419793629, -65.255885330, 83.318680481, -33.746922930])
A2 = np.array([-0.0906148351, 0.4527842806, 0.5962700728, -1.7241829131, -4.1302112531, 13.776631870, -8.6728470368])
B0 = np.array([0.7240946941, 2.2382791861, -4.0025849485, -21.003576815, 26.855641363, 206.55133841, -355.60235612])
B1 = np.array([-0.5755498075, 0.6995095521, 3.8925673390, -17.215471648, 192.67226447, -161.82646165, -165.20769346])
B2 = np.array([0.0976883116, -0.2557574982, -9.1558561530, 20.642075974, -38.804430052, 93.626774077, -29.666905585])


@dataclass(frozen=True)
class DispersionPolynomials:
    a: np.ndarray
    b: np.ndarray
    i1: float
    i2: float
    c1: float


@dataclass(frozen=True)
class MixedDispersionMoments:
    m2epssigma3: float
    m2eps2sigma3: float


def dispersion_polynomials(*, m_bar: float, eta: float) -> DispersionPolynomials:
    c1_m = (m_bar - 1.0) / m_bar
    c2_m = (m_bar - 2.0) / m_bar
    a = A0 + c1_m * A1 + c1_m * c2_m * A2
    b = B0 + c1_m * B1 + c1_m * c2_m * B2
    powers = eta ** np.arange(7, dtype=float)
    i1 = float(np.dot(a, powers))
    i2 = float(np.dot(b, powers))
    c1 = float(
        1.0
        / (
            1.0
            + m_bar * (8.0 * eta - 2.0 * eta**2) / (1.0 - eta) ** 4
            + (1.0 - m_bar)
            * (20.0 * eta - 27.0 * eta**2 + 12.0 * eta**3 - 2.0 * eta**4)
            / ((1.0 - eta) * (2.0 - eta)) ** 2
        )
    )
    return DispersionPolynomials(a=a, b=b, i1=i1, i2=i2, c1=c1)


def pair_sigma_matrix(state: ToyPCSAFTState) -> np.ndarray:
    sigma = state.sigma
    return 0.5 * (sigma[:, np.newaxis] + sigma[np.newaxis, :])


def pair_epsilon_over_k_matrix(state: ToyPCSAFTState) -> np.ndarray:
    epsilon = np.sqrt(state.epsilon_over_k[:, np.newaxis] * state.epsilon_over_k[np.newaxis, :])
    return epsilon * (1.0 - state.k_ij)


def mixed_dispersion_moments(state: ToyPCSAFTState) -> MixedDispersionMoments:
    x = state.composition
    m = state.segments
    sigma_ij = pair_sigma_matrix(state)
    epsilon_ij = pair_epsilon_over_k_matrix(state)
    weights = x[:, np.newaxis] * x[np.newaxis, :] * m[:, np.newaxis] * m[np.newaxis, :]
    e_over_t = epsilon_ij / state.temperature
    sigma3 = sigma_ij**3
    return MixedDispersionMoments(
        m2epssigma3=float(np.sum(weights * e_over_t * sigma3)),
        m2eps2sigma3=float(np.sum(weights * e_over_t**2 * sigma3)),
    )


def ares_disp(state: ToyPCSAFTState, hc: HardChainState, moments: MixedDispersionMoments) -> float:
    polynomials = dispersion_polynomials(m_bar=state.m_bar, eta=hc.eta)
    return float(
        -2.0 * np.pi * state.number_density * polynomials.i1 * moments.m2epssigma3
        - np.pi * state.number_density * state.m_bar * polynomials.c1 * polynomials.i2 * moments.m2eps2sigma3
    )
```

- [ ] **Step 4: Run dispersion tests and commit**

Run:

```powershell
uv run python run_pytest.py analyses/package_validation/explicit_association_toybox/tests/test_neutral_pcsaft_scalar_terms.py -q
```

Expected: all tests in the file pass.

Commit:

```powershell
git add analyses/package_validation/explicit_association_toybox/scripts/dispersion.py analyses/package_validation/explicit_association_toybox/tests/test_neutral_pcsaft_scalar_terms.py
git commit -m "feat: add toybox dispersion scalar terms"
```

## Task 4: Extend Metrics With Total Residual Ares And Timing

**Files:**

- Modify: `analyses/package_validation/explicit_association_toybox/scripts/metrics.py`
- Modify: `analyses/package_validation/explicit_association_toybox/tests/test_total_ares_metrics.py`
- Modify: `analyses/package_validation/explicit_association_toybox/tests/test_output_schema.py`

- [ ] **Step 1: Write failing metric tests**

Create `analyses/package_validation/explicit_association_toybox/tests/test_total_ares_metrics.py`:

```python
from __future__ import annotations

import numpy as np
import pytest

from analyses.package_validation.explicit_association_toybox.scripts.association_models import AssociationSystem
from analyses.package_validation.explicit_association_toybox.scripts.closure_models import evaluate_closure
from analyses.package_validation.explicit_association_toybox.scripts.exact_baseline import solve_exact_site_fractions
from analyses.package_validation.explicit_association_toybox.scripts.metrics import metric_row


def test_metric_row_adds_total_ares_context_when_supplied() -> None:
    system = AssociationSystem(
        component_count=1,
        site_component_index=np.array([0, 0], dtype=int),
        site_kind=("D", "A"),
        active_pairs=((0, 1), (1, 0)),
    )
    density = 0.1
    composition = np.array([1.0])
    delta = system.delta_matrix(strength=2.0)
    exact = solve_exact_site_fractions(density=density, x_assoc=system.x_assoc(composition), delta=delta)
    closure = evaluate_closure(
        "damped_picard_7_05",
        system=system,
        density=density,
        composition=composition,
        delta=delta,
    )

    row = metric_row(
        system_name="symmetric_2b_pure",
        system=system,
        density=density,
        strength=2.0,
        composition=composition,
        delta=delta,
        exact=exact,
        closure=closure,
        thresholds={"thermodynamic_relative_reference": 0.03, "mass_residual_loose": 1.0e-6},
        elapsed_seconds=0.002,
        exact_elapsed_seconds=0.010,
        temperature=303.15,
        pcsaft_density=0.01,
        ares_hc=0.10,
        ares_disp=-0.30,
    )

    assert row["temperature"] == pytest.approx(303.15)
    assert row["pcsaft_density"] == pytest.approx(0.01)
    assert row["ares_hc"] == pytest.approx(0.10)
    assert row["ares_disp"] == pytest.approx(-0.30)
    assert row["ares_total_exact"] == pytest.approx(0.10 - 0.30 + row["ares_assoc_exact"])
    assert row["ares_total_closure"] == pytest.approx(0.10 - 0.30 + row["ares_assoc_closure"])
    assert row["ares_total_abs_error"] == pytest.approx(abs(row["ares_total_closure"] - row["ares_total_exact"]))
    assert row["speedup_ratio"] == pytest.approx(5.0)
```

Update `REQUIRED_COLUMNS` in `test_output_schema.py` to include the new CSV columns listed in the data contract.

- [ ] **Step 2: Run metric tests and verify the expected failure**

Run:

```powershell
uv run python run_pytest.py analyses/package_validation/explicit_association_toybox/tests/test_total_ares_metrics.py analyses/package_validation/explicit_association_toybox/tests/test_output_schema.py -q
```

Expected: fail because `metric_row` does not accept the new keyword arguments and the output schema lacks the new columns.

- [ ] **Step 3: Extend `metric_row` with optional scalar context**

Modify `metric_row(...)` in `scripts/metrics.py`:

```python
def metric_row(
    *,
    system_name: str,
    system: AssociationSystem,
    density: float,
    strength: float,
    composition: np.ndarray,
    delta: np.ndarray,
    exact: ExactAssociationResult,
    closure: ClosureResult,
    thresholds: Mapping[str, float],
    elapsed_seconds: float | None = None,
    exact_elapsed_seconds: float | None = None,
    temperature: float | None = None,
    pcsaft_density: float | None = None,
    ares_hc: float | None = None,
    ares_disp: float | None = None,
) -> dict[str, object]:
```

Inside the function, after `closure_assoc` is computed, add:

```python
    has_pcsaft_context = (
        temperature is not None
        and pcsaft_density is not None
        and ares_hc is not None
        and ares_disp is not None
    )
    if has_pcsaft_context:
        ares_total_exact = float(ares_hc + ares_disp + exact_a)
        ares_total_closure = float(ares_hc + ares_disp + closure_assoc)
        ares_total_abs_error = abs(ares_total_closure - ares_total_exact)
        ares_total_rel_error = ares_total_abs_error / max(abs(ares_total_exact), 1.0e-14)
    else:
        ares_total_exact = np.nan
        ares_total_closure = np.nan
        ares_total_abs_error = np.nan
        ares_total_rel_error = np.nan
```

Add these keys to the returned dictionary:

```python
        "temperature": temperature if temperature is not None else np.nan,
        "pcsaft_density": pcsaft_density if pcsaft_density is not None else np.nan,
        "ares_hc": ares_hc if ares_hc is not None else np.nan,
        "ares_disp": ares_disp if ares_disp is not None else np.nan,
        "ares_assoc_exact": exact_a,
        "ares_assoc_closure": closure_assoc,
        "ares_total_exact": ares_total_exact,
        "ares_total_closure": ares_total_closure,
        "ares_total_abs_error": ares_total_abs_error,
        "ares_total_rel_error": ares_total_rel_error,
        "exact_elapsed_seconds": exact_elapsed_seconds if exact_elapsed_seconds is not None else np.nan,
        "speedup_ratio": (
            exact_elapsed_seconds / elapsed_seconds
            if exact_elapsed_seconds is not None and elapsed_seconds is not None and elapsed_seconds > 0.0
            else np.nan
        ),
```

Keep the existing `assoc_helmholtz_*` keys for compatibility with the current closure-accuracy plot.

- [ ] **Step 4: Run metric tests and commit**

Run:

```powershell
uv run python run_pytest.py analyses/package_validation/explicit_association_toybox/tests/test_total_ares_metrics.py analyses/package_validation/explicit_association_toybox/tests/test_output_schema.py -q
```

Expected: selected tests pass.

Commit:

```powershell
git add analyses/package_validation/explicit_association_toybox/scripts/metrics.py analyses/package_validation/explicit_association_toybox/tests/test_total_ares_metrics.py analyses/package_validation/explicit_association_toybox/tests/test_output_schema.py
git commit -m "feat: report total toybox ares metrics"
```

## Task 5: Wire HC And Dispersion Into The Grid

**Files:**

- Modify: `analyses/package_validation/explicit_association_toybox/scripts/run_grid.py`
- Modify: `analyses/package_validation/explicit_association_toybox/tests/test_output_schema.py`
- Test: `analyses/package_validation/explicit_association_toybox/tests/test_neutral_pcsaft_scalar_terms.py`
- Test: `analyses/package_validation/explicit_association_toybox/tests/test_total_ares_metrics.py`

- [ ] **Step 1: Extend the grid test to require retained total `ares` columns**

In `test_run_grid_writes_retained_csv`, add assertions:

```python
    assert "ares_hc" in text
    assert "ares_disp" in text
    assert "ares_total_abs_error" in text
    assert "speedup_ratio" in text
```

- [ ] **Step 2: Run the grid test and verify the expected failure**

Run:

```powershell
uv run python run_pytest.py analyses/package_validation/explicit_association_toybox/tests/test_output_schema.py::test_run_grid_writes_retained_csv -q
```

Expected: fail because `run_grid` does not pass PC-SAFT scalar context.

- [ ] **Step 3: Modify imports and scalar context assembly in `run_grid.py`**

Add imports in both import branches:

```python
from analyses.package_validation.explicit_association_toybox.scripts.dispersion import ares_disp, mixed_dispersion_moments
from analyses.package_validation.explicit_association_toybox.scripts.hard_chain import ares_hc, hard_chain_state
from analyses.package_validation.explicit_association_toybox.scripts.pcsaft_inputs import state_from_config
```

and:

```python
from .dispersion import ares_disp, mixed_dispersion_moments
from .hard_chain import ares_hc, hard_chain_state
from .pcsaft_inputs import state_from_config
```

Wrap exact solve timing:

```python
                    exact, exact_elapsed = timed_closure(
                        lambda density=float(density), composition=composition, delta=delta: solve_exact_site_fractions(
                            density=density,
                            x_assoc=system.x_assoc(composition),
                            delta=delta,
                        )
                    )
```

Build scalar PC-SAFT context once per composition/density/strength state:

```python
                    pcsaft_state = state_from_config(
                        raw_system_config["pcsaft"],
                        component_count=system.component_count,
                        composition=composition,
                    )
                    hc_state = hard_chain_state(pcsaft_state)
                    ares_hc_value = ares_hc(pcsaft_state, hc_state)
                    ares_disp_value = ares_disp(
                        pcsaft_state,
                        hc_state,
                        mixed_dispersion_moments(pcsaft_state),
                    )
```

Pass the values to `metric_row`:

```python
                                exact_elapsed_seconds=exact_elapsed,
                                temperature=pcsaft_state.temperature,
                                pcsaft_density=pcsaft_state.density,
                                ares_hc=ares_hc_value,
                                ares_disp=ares_disp_value,
```

- [ ] **Step 4: Run focused grid tests and commit**

Run:

```powershell
uv run python run_pytest.py analyses/package_validation/explicit_association_toybox/tests/test_output_schema.py analyses/package_validation/explicit_association_toybox/tests/test_total_ares_metrics.py analyses/package_validation/explicit_association_toybox/tests/test_neutral_pcsaft_scalar_terms.py -q
```

Expected: selected tests pass and the retained CSV includes total `ares` columns.

Commit:

```powershell
git add analyses/package_validation/explicit_association_toybox/scripts/run_grid.py analyses/package_validation/explicit_association_toybox/tests/test_output_schema.py
git commit -m "feat: wire pcsaft scalar context into toybox grid"
```

## Task 6: Add Residual Ares Figure Workflow

**Files:**

- Create: `analyses/package_validation/explicit_association_toybox/figures/residual_ares_error/scripts/generate_data.py`
- Create: `analyses/package_validation/explicit_association_toybox/figures/residual_ares_error/scripts/render_figure.py`
- Modify: `analyses/package_validation/explicit_association_toybox/README.md`
- Modify: `analyses/package_validation/explicit_association_toybox/analysis.yaml`

- [ ] **Step 1: Create the figure data command**

Create `figures/residual_ares_error/scripts/generate_data.py`:

```python
from __future__ import annotations

import sys
from pathlib import Path

ANALYSIS_ROOT = Path(__file__).resolve().parents[3]
REPO_ROOT = ANALYSIS_ROOT.parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from analyses.package_validation.explicit_association_toybox.scripts.run_grid import run_grid

OUTPUT = ANALYSIS_ROOT / "figures" / "residual_ares_error" / "output" / "residual_ares_metrics.csv"


def main() -> None:
    output = run_grid(output_path=OUTPUT)
    print(output)


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Create the residual `ares` render command**

Create `figures/residual_ares_error/scripts/render_figure.py`:

```python
from __future__ import annotations

import csv
from pathlib import Path

import matplotlib.pyplot as plt

ANALYSIS_ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ANALYSIS_ROOT / "figures" / "residual_ares_error" / "output"
METRICS = OUTPUT / "residual_ares_metrics.csv"
FIGURE = OUTPUT / "residual_ares_error_summary.png"
PLOTTED = OUTPUT / "residual_ares_error_summary_plotted_data.csv"
PDF = OUTPUT / "residual_ares_error_summary.pdf"


def _load_rows() -> list[dict[str, str]]:
    with METRICS.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def main() -> None:
    rows = _load_rows()
    grouped: dict[str, list[float]] = {}
    timings: dict[str, list[float]] = {}
    for row in rows:
        grouped.setdefault(row["closure"], []).append(float(row["ares_total_rel_error"]))
        timings.setdefault(row["closure"], []).append(float(row["speedup_ratio"]))
    names = sorted(grouped)
    errors = [max(grouped[name]) for name in names]
    speedups = [max(timings[name]) for name in names]

    OUTPUT.mkdir(parents=True, exist_ok=True)
    with PLOTTED.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["closure", "max_ares_total_rel_error", "max_speedup_ratio"])
        writer.writerows(zip(names, errors, speedups))

    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.bar(names, errors, color="#6f8f3a")
    ax.set_yscale("symlog", linthresh=0.03, linscale=0.8)
    ax.set_title("Explicit association total residual Helmholtz error")
    ax.set_ylabel("Max relative total ares error")
    ax.set_xlabel("Closure")
    ax.tick_params(axis="x", rotation=30)
    ax.grid(axis="y", color="#d9d9d9", linewidth=0.6)
    fig.tight_layout()
    fig.savefig(FIGURE, dpi=160)
    plt.close(fig)
    PDF.write_text(
        "\n".join(
            (
                "kind: matplotlib-figure",
                "version: 1",
                "plot_id: explicit_association_total_residual_ares_error",
                "title: Explicit association total residual Helmholtz error",
                "matplotlib:",
                "  title: Explicit association total residual Helmholtz error",
                "  x_label: Closure",
                "  y_label: Max relative total ares error",
                "  y_scale: symlog",
                "files:",
                "  figure: residual_ares_error_summary.png",
                "  source_data: residual_ares_error_summary_plotted_data.csv",
                "render:",
                "  command: uv run python analyses/package_validation/explicit_association_toybox/figures/residual_ares_error/scripts/render_figure.py",
                "",
            )
        ),
        encoding="utf-8",
    )
    print(FIGURE)


if __name__ == "__main__":
    main()
```

- [ ] **Step 3: Document the commands**

Add commands to `analysis.yaml`:

```yaml
  generate_residual_ares_data: uv run python analyses/package_validation/explicit_association_toybox/figures/residual_ares_error/scripts/generate_data.py
  render_residual_ares_plot: uv run python analyses/package_validation/explicit_association_toybox/figures/residual_ares_error/scripts/render_figure.py
```

Add README lines under Commands:

```markdown
- `uv run python analyses/package_validation/explicit_association_toybox/figures/residual_ares_error/scripts/generate_data.py`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/residual_ares_error/scripts/render_figure.py`
```

Add a short boundary note:

```markdown
HC and dispersion are scalar fixed-state context terms for total `ares`
comparison. They do not solve density, pressure, or phase roots.
```

- [ ] **Step 4: Run figure commands and commit**

Run:

```powershell
uv run python analyses/package_validation/explicit_association_toybox/figures/residual_ares_error/scripts/generate_data.py
uv run python analyses/package_validation/explicit_association_toybox/figures/residual_ares_error/scripts/render_figure.py
```

Expected:

- `analyses/package_validation/explicit_association_toybox/figures/residual_ares_error/output/residual_ares_metrics.csv`
- `analyses/package_validation/explicit_association_toybox/figures/residual_ares_error/output/residual_ares_error_summary_plotted_data.csv`
- `analyses/package_validation/explicit_association_toybox/figures/residual_ares_error/output/residual_ares_error_summary.png`
- `analyses/package_validation/explicit_association_toybox/figures/residual_ares_error/output/residual_ares_error_summary.pdf`

Commit:

```powershell
git add analyses/package_validation/explicit_association_toybox/figures/residual_ares_error analyses/package_validation/explicit_association_toybox/README.md analyses/package_validation/explicit_association_toybox/analysis.yaml
git commit -m "feat: add residual ares error figure workflow"
```

## Task 7: Full Validation And Boundary Check

**Files:**

- Verify: `analyses/package_validation/explicit_association_toybox/**`
- Verify: `packages/epcsaft/**`
- Verify: `packages/epcsaft-equilibrium/**`
- Verify: `packages/epcsaft-regression/**`

- [ ] **Step 1: Run all toybox tests**

Run:

```powershell
uv run python run_pytest.py analyses/package_validation/explicit_association_toybox/tests -q
```

Expected: all explicit association toybox tests pass.

- [ ] **Step 2: Run both toybox figure workflows**

Run:

```powershell
uv run python analyses/package_validation/explicit_association_toybox/figures/closure_accuracy/scripts/generate_data.py
uv run python analyses/package_validation/explicit_association_toybox/figures/closure_accuracy/scripts/render_figure.py
uv run python analyses/package_validation/explicit_association_toybox/figures/residual_ares_error/scripts/generate_data.py
uv run python analyses/package_validation/explicit_association_toybox/figures/residual_ares_error/scripts/render_figure.py
```

Expected: both figure output folders contain CSV data, plotted data snapshots, PNGs, and PDF artifacts.

- [ ] **Step 3: Prove SciPy and package boundaries**

Run:

```powershell
rg -n "import scipy|from scipy" analyses/package_validation/explicit_association_toybox packages tests scripts
git diff --name-only HEAD~7..HEAD
```

Expected:

- `rg` returns no matches.
- The diff file list is limited to `analyses/package_validation/explicit_association_toybox/**`.

- [ ] **Step 4: Run repo structure and quick validation**

Run:

```powershell
uv run python run_pytest.py tests/workflows/repo/test_project_structure.py -q
uv run python scripts/dev/validate_project.py quick
pwsh.exe -NoProfile -ExecutionPolicy Bypass -File "$env:USERPROFILE\.codex\hooks\codex-cleanup.ps1" -RepoRoot .
```

Expected: structure test passes, quick validation passes, cleanup hook reports no current-task leftovers.

- [ ] **Step 5: Final status**

Run:

```powershell
git status --short --branch
```

Expected: branch is clean after the final commit, or only generated retained outputs intentionally staged in the last commit.

## Proof Oracle

Required execution proof after implementation:

```powershell
uv run python run_pytest.py analyses/package_validation/explicit_association_toybox/tests -q
uv run python analyses/package_validation/explicit_association_toybox/figures/closure_accuracy/scripts/generate_data.py
uv run python analyses/package_validation/explicit_association_toybox/figures/closure_accuracy/scripts/render_figure.py
uv run python analyses/package_validation/explicit_association_toybox/figures/residual_ares_error/scripts/generate_data.py
uv run python analyses/package_validation/explicit_association_toybox/figures/residual_ares_error/scripts/render_figure.py
rg -n "import scipy|from scipy" analyses/package_validation/explicit_association_toybox packages tests scripts
uv run python run_pytest.py tests/workflows/repo/test_project_structure.py -q
uv run python scripts/dev/validate_project.py quick
pwsh.exe -NoProfile -ExecutionPolicy Bypass -File "$env:USERPROFILE\.codex\hooks\codex-cleanup.ps1" -RepoRoot .
```

Generated artifacts to verify:

- `analyses/package_validation/explicit_association_toybox/figures/closure_accuracy/output/closure_metrics.csv`
- `analyses/package_validation/explicit_association_toybox/figures/closure_accuracy/output/closure_accuracy_summary_plotted_data.csv`
- `analyses/package_validation/explicit_association_toybox/figures/closure_accuracy/output/closure_accuracy_summary.png`
- `analyses/package_validation/explicit_association_toybox/figures/closure_accuracy/output/closure_accuracy_summary.pdf`
- `analyses/package_validation/explicit_association_toybox/figures/residual_ares_error/output/residual_ares_metrics.csv`
- `analyses/package_validation/explicit_association_toybox/figures/residual_ares_error/output/residual_ares_error_summary_plotted_data.csv`
- `analyses/package_validation/explicit_association_toybox/figures/residual_ares_error/output/residual_ares_error_summary.png`
- `analyses/package_validation/explicit_association_toybox/figures/residual_ares_error/output/residual_ares_error_summary.pdf`

## Risks And Sequencing Notes

- The density naming is the main ambiguity. Keep `density` as the existing association density and add `pcsaft_density` for the fixed neutral PC-SAFT scalar state.
- The dispersion constants should be copied from `packages/epcsaft/src/epcsaft/native/eos/core_internal.h` exactly once into the analysis module and cited in comments with equation IDs.
- The figure workflows intentionally write retained outputs. Do not add run-specific timestamped files.
- The toybox should stay small. If the work starts needing pressure roots, derivatives, or native provider calls as the primary baseline, stop and create a new spec.

## Acceptance Mapping

- Scalar HC/dispersion helpers: Tasks 1, 2, and 3.
- Fixed-state, no density solve: Tasks 1, 5, and README update in Task 6.
- Total `ares` metrics and timing: Tasks 4 and 5.
- Residual `ares` figure/table: Task 6.
- No SciPy and no package runtime changes: Task 7.
- Completion verification: Task 7 proof oracle.
