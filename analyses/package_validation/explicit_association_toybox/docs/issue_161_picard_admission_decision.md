# Issue 161 Picard Admission Decision

This M8 toybox memo summarizes the final fixed-policy Picard evidence packet for issue #161.

| Field | Value |
| --- | --- |
| Retained rows | 52 |
| Best high-accuracy policy | picard_n11_lambda1 at methanol_293.81K |
| Fastest simulation policy | picard_n3_lambda0p8 at methanol_293.81K |
| Worst relative-error row | picard_n3_lambda0p35 at methanol_293.81K max_rel=8.221e-02 |
| Worst simulation residual row | picard_n3_lambda0p35 at methanol_293.81K max_rel=8.221e-02 |
| Issue #161 recommendation | `close_without_provider_implementation` |

Provider implementation remains blocked unless the recommendation is `close_design_complete_open_narrow_provider_admission_issue`.

JAX and Python toybox evidence remain proxy evidence; provider CppAD behavior still requires separate M3 proof.
