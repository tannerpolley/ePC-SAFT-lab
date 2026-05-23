# ePC-SAFT Parameter Location

This folder is intentionally pointer-only.

The old shared parameter datasets were retired after the paper-validation
analyses were converted to analysis-owned snapshots. Use:

- `analyses/paper_validation/<paper_id>/parameters/` for full validation parameter bundles.
- Figure-specific `source/` folders for auxiliary paper parameter variants used by one figure.
- External parameter folders with the same `mixed/`, `pure/`, and `user_options.json` layout when calling `ParameterSet.from_dataset(...)` or `get_prop_dict(...)`.

Do not recreate dataset folders here.
