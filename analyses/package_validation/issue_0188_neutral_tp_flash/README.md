# Issue 188 Neutral TP Flash Evidence

This analysis reruns the neutral methane/ethane/propane TP-flash case used by
issue 188 and renders neutral-only figures from retained CSV outputs.

Scope:

- PC-SAFT neutral hydrocarbon TP flash only.
- No associating, electrolyte, reactive, or generalized public GFPE claim.
- No LLE readiness claim.

The source fixture is
`data/reference/equilibrium_benchmarks/neutral_tp_flash/methane_ethane_propane`.

## Figures

- `figures/neutral_tp_flash_vle_tieline/results/neutral_tp_flash_vle_tieline.png`
- `figures/neutral_tp_flash_tolerance_margins/results/neutral_tp_flash_tolerance_margins.png`
- `figures/held_1_0_gate_status/results/held_1_0_gate_status.png`

## Regeneration

```powershell
uv run --no-sync python analyses/package_validation/issue_0188_neutral_tp_flash/scripts/generate_data.py
uv run --no-sync python analyses/package_validation/issue_0188_neutral_tp_flash/scripts/render_figures.py
```
