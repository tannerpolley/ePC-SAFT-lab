# Agent Happy Path

This is the compact Linux-first flow for coding agents working in a migrated
ePC-SAFT checkout. Read `docs/superpowers/PROJECT_CONTEXT.md` for package scope
and completion standards before changing behavior.

## 1. Check The Host

```bash
scripts/dev/check_linux_prereqs.sh --check
```

If the check reports missing tools, print install commands:

```bash
scripts/dev/check_linux_prereqs.sh --print-install
```

## 2. Remove Transfer Debris

Inspect ignored Windows/native/cache artifacts:

```bash
scripts/dev/clean_transferred_artifacts.sh --dry-run
```

Remove only those ignored artifacts when the dry run looks right:

```bash
scripts/dev/clean_transferred_artifacts.sh --apply
```

## 3. Bootstrap

```bash
uv sync --no-install-workspace
uv run --no-sync python scripts/dev/bootstrap.py
```

If bootstrap fails, run Doctor and follow its `next_command`:

```bash
uv run --no-sync python scripts/dev/doctor.py --require-provider-sdk
```

## 4. Pick A Test Slice

List slices without importing NumPy or native extensions:

```bash
python3 run_pytest.py --list-slices
```

Use the smallest relevant slice first:

```bash
uv run --no-sync python scripts/dev/validate_project.py quick
uv run --no-sync python run_pytest.py --provider-api -q
uv run --no-sync python run_pytest.py --equilibrium-api -q
uv run --no-sync python run_pytest.py --regression -q
```

## 5. Make Claims Match Evidence

Use `uv run --no-sync python scripts/dev/validate_project.py confidence` before
broad runtime claims. Heavy package, Ipopt, Ceres, release, and downstream
proof lanes stay explicit and manual until the relevant issue or release task
requires them.
