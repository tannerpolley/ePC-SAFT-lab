# Pereira 2012 System III Source Audit

This folder records the source-backed data for Pereira et al. 2012 System III,
the ethane + carbon dioxide SAFT-VR VLE case used in the HELD paper.

Status: source-audited but not executable for the current `epcsaft` runtime.

Reasons:

- The paper case is SAFT-VR, while the package runtime currently exposes
  PC-SAFT/ePC-SAFT kernels and no SAFT-VR route.
- Table B.1 includes SAFT-VR range parameters and binary factors `xi_12` and
  `gamma_12`, which are not PC-SAFT `k_ij` inputs.
- Table 3 reports the second feed as `[0.09,0.01]`, which sums to 0.10. The
  adjacent phase compositions imply the intended second component may be 0.91,
  but this audit does not silently correct published source data.
- `material_balance_readiness.csv` records that the first System III point has
  a feasible lever-rule split from the reported feed. The second point remains
  blocked as published.
- `feed_correction_candidates.csv` records the material-balance-compatible
  `[0.09,0.91]` candidate for the second point as inferred but not
  source-confirmed.

Source locations:

- Phase splits: Pereira et al. 2012 Table 3, paper page 109, local markdown
  lines 496-522.
- Parameters: Pereira et al. 2012 Table B.1, paper page 117, local markdown
  lines 934-938.

Promotion rule: this folder can become executable Stage 10 proof only after
SAFT-VR support or source-backed ePC-SAFT/PC-SAFT model parity is implemented,
and after the second feed-composition ambiguity has a source-backed correction
policy.
