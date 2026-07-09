#!/usr/bin/env bash
set -euo pipefail

action="configure"
preset="dev-native"
target=""
parallel="10"
target_set="0"
parallel_set="0"

usage() {
    cat <<'EOF'
Usage: scripts/dev/cmake_preset.sh [--action configure|build] [--preset dev-native]
       [--target <target>] [--parallel <jobs>]

--target and --parallel are valid only with --action build.
EOF
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
        --action|-a)
            require_value "$1" "$#" "${2:-}"
            action="$2"
            shift 2
            ;;
        --preset|-p)
            require_value "$1" "$#" "${2:-}"
            preset="$2"
            shift 2
            ;;
        --target|-t)
            require_value "$1" "$#" "${2:-}"
            target="$2"
            target_set="1"
            shift 2
            ;;
        --parallel|-j)
            require_value "$1" "$#" "${2:-}"
            parallel="$2"
            parallel_set="1"
            shift 2
            ;;
        *)
            echo "Unknown argument: $1" >&2
            usage >&2
            exit 2
            ;;
    esac
done

case "${action,,}" in
    configure|build) ;;
    *)
        echo "--action must be configure or build" >&2
        exit 2
        ;;
esac

if [[ "${action,,}" == "configure" && "$target_set" == "1" ]]; then
    echo "--target is only valid with --action build" >&2
    usage >&2
    exit 2
fi
if [[ "${action,,}" == "configure" && "$parallel_set" == "1" ]]; then
    echo "--parallel is only valid with --action build" >&2
    usage >&2
    exit 2
fi

if [[ "$preset" != "dev-native" ]]; then
    echo "scripts/dev/cmake_preset.sh supports only the dev-native preset; received: $preset" >&2
    exit 2
fi

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd "${script_dir}/../.." && pwd)"
cd "$repo_root"

python_exe="${repo_root}/.venv/bin/python"
ninja_exe="${repo_root}/.venv/bin/ninja"

if [[ ! -x "$python_exe" ]]; then
    echo "Required repo-local Python is missing: $python_exe. Run uv sync --no-install-workspace first." >&2
    exit 1
fi

if [[ ! -x "$ninja_exe" ]]; then
    echo "Required repo-local Ninja is missing: $ninja_exe. Run uv sync --no-install-workspace first." >&2
    exit 1
fi

if [[ -e "build/dev/.ninja_lock" ]]; then
    echo "Refusing CMake preset run because build/dev/.ninja_lock exists. Another native build may be active; run Build Status before retrying." >&2
    exit 1
fi

cmake_cmd=("$python_exe" -m cmake)

cache_value() {
    local name="$1"
    local cache="build/dev/CMakeCache.txt"
    [[ -f "$cache" ]] || return 1
    awk -F= -v prefix="${name}:" '$0 ~ "^" prefix { print $2; exit }' "$cache"
}

configure_args=(--preset "$preset" "-DCMAKE_MAKE_PROGRAM=${ninja_exe}")

if [[ "${action,,}" == "build" ]]; then
    configured_ninja="$(cache_value CMAKE_MAKE_PROGRAM || true)"
    if [[ -z "$configured_ninja" || "$configured_ninja" != "$ninja_exe" ]]; then
        echo "Refreshing ${preset} configure so CMAKE_MAKE_PROGRAM uses repo-local Ninja: ${ninja_exe}"
        "${cmake_cmd[@]}" "${configure_args[@]}"
    fi

    build_args=(--build --preset "$preset" --parallel "$parallel")
    if [[ -n "$target" ]]; then
        build_args+=(--target "$target")
    fi
    "${cmake_cmd[@]}" "${build_args[@]}"
else
    "${cmake_cmd[@]}" "${configure_args[@]}"
fi
