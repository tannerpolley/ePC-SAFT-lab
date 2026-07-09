#!/usr/bin/env bash
set -euo pipefail

step="setup"
dry_run="0"

while [[ $# -gt 0 ]]; do
    case "$1" in
        --step|-s)
            if [[ $# -lt 2 ]]; then
                echo "Missing value for $1" >&2
                exit 2
            fi
            step="$2"
            shift 2
            ;;
        --dry-run)
            dry_run="1"
            shift
            ;;
        *)
            echo "Unknown argument: $1" >&2
            exit 2
            ;;
    esac
done

repo_root="$(git rev-parse --show-toplevel)"
cd "$repo_root"

if [[ ! -f "scripts/dev/check_linux_prereqs.sh" ]]; then
    echo "Required prerequisite checker is missing: scripts/dev/check_linux_prereqs.sh" >&2
    exit 1
fi
prereq_mode="--for-setup"
case "$step" in
    setup|build|equilibrium-native|full-native)
        prereq_mode="--check"
        ;;
esac
bash scripts/dev/check_linux_prereqs.sh "$prereq_mode"

if ! command -v uv >/dev/null 2>&1; then
    echo "uv is required for this repo workflow. Install uv, then rerun setup." >&2
    exit 1
fi

bootstrap_args=(--step "$step")
if [[ "$dry_run" == "1" ]]; then
    bootstrap_args+=(--dry-run)
    if [[ "$step" == "sync" ]]; then
        echo "Running: uv sync --no-install-workspace"
        echo "bootstrap_state: dry-run"
        exit 0
    fi
else
    uv sync --no-install-workspace
    if [[ "$step" == "sync" ]]; then
        echo "bootstrap_state: current"
        exit 0
    fi
fi
uv run --no-sync python scripts/dev/bootstrap.py "${bootstrap_args[@]}"
