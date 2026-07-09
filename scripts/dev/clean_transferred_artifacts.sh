#!/usr/bin/env bash
set -euo pipefail

apply="0"

usage() {
    cat <<'EOF'
Usage: scripts/dev/clean_transferred_artifacts.sh [--dry-run|--apply]

Removes ignored artifacts commonly left after moving a checkout from Windows to
Linux: repository Python caches, Windows CMake build trees and native binaries,
stale .venv/Scripts and .venv/Lib trees, and local tool caches. It preserves
valid Linux build state and the active Linux virtual environment, and only
removes paths that are ignored by Git.
EOF
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --dry-run)
            apply="0"
            shift
            ;;
        --apply)
            apply="1"
            shift
            ;;
        --help|-h)
            usage
            exit 0
            ;;
        *)
            echo "Unknown argument: $1" >&2
            usage >&2
            exit 2
            ;;
    esac
done

repo_root="$(git rev-parse --show-toplevel)"
cd "$repo_root"

is_ignored() {
    git check-ignore -q -- "$1"
}

remove_path() {
    local path="$1"
    [[ -e "$path" ]] || return 0
    if ! is_ignored "$path"; then
        echo "skip-not-ignored: $path"
        return 0
    fi
    if [[ "$apply" == "1" ]]; then
        rm -rf -- "$path"
        echo "removed: $path"
    else
        echo "would-remove: $path"
    fi
}

is_windows_cmake_cache() {
    local cache="$1"
    grep -Eiq \
        '^(CMAKE_GENERATOR:INTERNAL=(Visual Studio|NMake|MSYS|MinGW)|CMAKE_(HOST_)?SYSTEM_NAME(:[^=]*)?=Windows|CMAKE_(C|CXX)_COMPILER(:[^=]*)?=([A-Za-z]:[\\/]|.*\.exe$))' \
        "$cache"
}

if [[ -d build ]]; then
    while IFS= read -r -d '' cache; do
        if is_windows_cmake_cache "$cache"; then
            remove_path "$(dirname "$cache")"
        fi
    done < <(find build -type f -name CMakeCache.txt -print0)

    while IFS= read -r -d '' path; do
        remove_path "$path"
    done < <(
        find build -type f \
            \( -name '*.pyc' -o -name '*.pyd' -o -name '*.dll' -o -name '*.lib' -o -name '*.exp' -o -name '*.exe' \) \
            -print0 2>/dev/null
    )
fi

while IFS= read -r -d '' path; do
    remove_path "${path#./}"
done < <(
    find . \
        \( -path './.git' -o -path './build' -o -path './.venv' -o -path './.worktrees' \) -prune -o \
        \( -type d -name '__pycache__' -o -type d -name '.pytest_cache' -o -type d -name '.ruff_cache' -o -type d -name '.mypy_cache' \) \
        -print0
)

for path in .codex_tmp graphify-out dist .venv/Scripts .venv/Lib; do
    remove_path "$path"
done

while IFS= read -r -d '' path; do
    remove_path "${path#./}"
done < <(
    find packages scripts tests \
        \( -path '*/__pycache__/*' -o -name '*.pyc' -o -name '*.pyd' -o -name '*.dll' -o -name '*.lib' -o -name '*.exp' \) \
        -print0 2>/dev/null
)

if [[ "$apply" != "1" ]]; then
    echo "artifact_cleanup_state: dry-run"
    echo "rerun_with: scripts/dev/clean_transferred_artifacts.sh --apply"
else
    echo "artifact_cleanup_state: applied"
fi
