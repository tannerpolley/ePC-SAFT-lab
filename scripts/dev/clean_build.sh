#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
cd "${REPO_ROOT}"

echo "REPAIR-ONLY: this removes build/cache/native artifacts. Use normal build and confidence tests for routine validation." >&2

rm -rf build dist .pytest_cache .ruff_cache .mypy_cache

remove_matching_directories() {
    local directory_name="$1"
    find . \
        \( -path "./build" -o -path "./dist" -o -path "./.git" -o -path "./.venv" \) -prune \
        -o -type d -name "${directory_name}" -prune -exec rm -rf -- {} +
}

remove_matching_directories "*.egg-info"
remove_matching_directories "__pycache__"

shopt -s nullglob
native_artifacts=(
    packages/epcsaft/src/epcsaft/_core*.so
    packages/epcsaft-equilibrium/src/epcsaft_equilibrium/_native_core*.so
    packages/epcsaft-regression/src/epcsaft_regression/_native_core*.so
)
if (( ${#native_artifacts[@]} > 0 )); then
    rm -f -- "${native_artifacts[@]}"
fi
