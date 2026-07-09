#!/usr/bin/env bash
set -euo pipefail

name=""
branch=""
base="HEAD"

usage() {
    echo "Usage: scripts/dev/create_dev_worktree.sh --name <name> --branch <branch> [--base <ref>]"
}

require_value() {
    local option="$1"
    local value_count="$2"
    local value="${3:-}"
    if [[ "$value_count" -lt 2 || -z "$value" || "$value" == -* ]]; then
        echo "Missing value for $option" >&2
        usage >&2
        exit 2
    fi
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --name|-n)
            require_value "$1" "$#" "${2:-}"
            name="$2"
            shift 2
            ;;
        --branch|-b)
            require_value "$1" "$#" "${2:-}"
            branch="$2"
            shift 2
            ;;
        --base)
            require_value "$1" "$#" "${2:-}"
            base="$2"
            shift 2
            ;;
        *)
            echo "Unknown argument: $1" >&2
            usage >&2
            exit 2
            ;;
    esac
done

if [[ -z "$name" || -z "$branch" ]]; then
    usage >&2
    exit 2
fi
if [[ "$name" == "." || "$name" == ".." || ! "$name" =~ ^[A-Za-z0-9][A-Za-z0-9._-]*$ ]]; then
    echo "Worktree name must be a simple directory name containing only letters, numbers, '.', '_', or '-': $name" >&2
    exit 2
fi
if ! git check-ref-format --branch "$branch" >/dev/null 2>&1; then
    echo "Invalid Git branch name: $branch" >&2
    exit 2
fi

repo_root="$(git rev-parse --show-toplevel)"
cd "$repo_root"

if ! git rev-parse --verify --quiet "${base}^{commit}" >/dev/null; then
    echo "Base ref does not resolve to a commit: $base" >&2
    exit 2
fi

if ! git check-ignore -q .worktrees/; then
    echo ".worktrees/ must stay ignored in .gitignore before creating project-local worktrees." >&2
    exit 1
fi

worktree_path="${repo_root}/.worktrees/${name}"
if [[ -e "$worktree_path" ]]; then
    echo "Worktree path already exists: $worktree_path" >&2
    exit 1
fi

mkdir -p "${repo_root}/.worktrees"
git worktree add "$worktree_path" -b "$branch" "$base"

echo "Created worktree: $worktree_path"
