# Scripts Layout

The root `scripts/` package is intentionally split between shared helper modules and runnable entrypoints.

Canonical rules:

- Keep shared helper modules at the root when analysis code imports them directly.
- Put runnable repo workflows under purpose-specific subfolders such as `dev/`, `validation/`, `docs/`, and `data/`.
- Move study-specific or figure-specific tooling into `analyses/<study>/scripts/` instead of keeping it under the repo-root `scripts/` tree.

Current layout:

- `scripts/_env.py`, `scripts/_epcsaft_oop.py`, `scripts/plot_outputs.py`: shared analysis helpers.
- `scripts/dev/`: environment setup, native build, repair, validation, and packaging entrypoints.
  Start migrated Linux checkouts with `scripts/dev/check_linux_prereqs.sh --check`.
  Use `scripts/dev/clean_transferred_artifacts.sh --dry-run` to inspect ignored
  Windows/native/cache artifacts before removing them with `--apply`.
- Benchmark and profiling entrypoints are currently not retained; add a current owned workflow before making performance or literature-coverage claims.
- `scripts/validation/`: opt-in specialty validation entrypoints.
- `scripts/docs/`: documentation, equation-registry, and LaTeX-mirror maintenance entrypoints.
- `scripts/data/`: reference-data curation helpers.
