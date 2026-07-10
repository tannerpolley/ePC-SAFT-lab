# Nonideal MEA model-input evidence gate

Status: `blocked_execution_stops_before_tasks_4_through_10`

This directory is an audit record, not an executable parameter bundle. The bounded Task 3 review found unresolved or conflicting scientific inputs. Tasks 4-10 must not execute while any ledger row is blocked.

`model_configuration.json` and `parameter_set.json` are deliberately absent. Their absence is the loud failure: no historical branch value, loose option, numeric matrix zero, or imported curve is allowed to become a current model prediction.

## Retained evidence

- `input_evidence_ledger.csv` contains 11 named pure/correlation/formulation records and 108 unique off-diagonal interaction records: 36 each for `k_ij`, `l_ij`, and `k_hb_ij`.
- `reaction_input_evidence_ledger.csv` contains separate R1-R5 records.
- The historical branch snapshot at `f3057e11` is audit evidence only.
- The water segment-size correlation is accepted from Held, Cameretti, and Sadowski (2008), Table 1 and Eq. 7, with the stated 273.15-373.15 K domain.
- Every historical interaction zero remains an unverified structural zero. Every historical nonzero still requires row-level literature or fitted provenance.
- The imported R1-R5 correlations remain non-executable because their claimed local Nasrifar source is absent and the exact nonideal standard-state mapping is not established. Baygi (2015) independently supports R3's matching coefficients over 273.15-498.15 K. R1 and R2 conflict with Baygi coefficients; R4 conflicts and ends at 323.15 K; R5 matches but ends at 323.15 K.

Resolving this gate requires traceable literature, a fitted receipt, or a cited defining model equation for every active row. It does not authorize public reactive, electrolyte-LLE, TP-flash, CPE, or multiphase capability claims.
