#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
cd "${REPO_ROOT}"

if ! command -v uv >/dev/null 2>&1; then
    echo "uv is not installed or is not on PATH. Install uv first: https://docs.astral.sh/uv/getting-started/installation/" >&2
    exit 1
fi

scripts/dev/check_linux_prereqs.sh --check
uv --version
uv python pin 3.13
uv sync --no-install-workspace
uv run --no-sync python scripts/dev/bootstrap.py
uv run --no-sync python scripts/dev/validate_project.py quick
