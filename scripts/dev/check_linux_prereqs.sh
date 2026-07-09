#!/usr/bin/env bash
set -euo pipefail

mode="check"

usage() {
    cat <<'EOF'
Usage: scripts/dev/check_linux_prereqs.sh [--check|--for-setup|--print-install]

Checks the Debian/Zorin host tools needed before the ePC-SAFT uv bootstrap:
uv, Python, compiler toolchain, Git, and the Ipopt development package.

Modes:
  --check          Report all prerequisites and fail when required tools are missing.
  --for-setup      Check the common environment without requiring Ipopt-only lanes.
  --print-install  Print Debian/Zorin install commands and exit.
EOF
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --check|--for-setup|--print-install)
            mode="${1#--}"
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

repo_root="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$repo_root"

apt_packages=(
    ca-certificates
    curl
    git
    build-essential
    pkg-config
    coinor-libipopt-dev
    python3
    python3-venv
    python3-pip
    cmake
    ninja-build
)

print_install_commands() {
    cat <<EOF
# Debian/Zorin host packages:
sudo apt-get update
sudo apt-get install -y ${apt_packages[*]}

# uv, installed for the current Linux user:
curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="\$HOME/.local/bin:\$PATH"

# repo Python baseline:
uv python install 3.13
uv python pin 3.13
EOF
}

if [[ "$mode" == "print-install" ]]; then
    print_install_commands
    exit 0
fi

missing_required=()
missing_optional=()

require_command() {
    local command_name="$1"
    local package_hint="$2"
    if command -v "$command_name" >/dev/null 2>&1; then
        printf 'ok: %s -> %s\n' "$command_name" "$(command -v "$command_name")"
    else
        printf 'missing: %s (install package/tool: %s)\n' "$command_name" "$package_hint"
        missing_required+=("$command_name")
    fi
}

optional_command() {
    local command_name="$1"
    local package_hint="$2"
    if command -v "$command_name" >/dev/null 2>&1; then
        printf 'ok: %s -> %s\n' "$command_name" "$(command -v "$command_name")"
    else
        printf 'optional-missing: %s (uv sync can provide repo-local tool; apt package: %s)\n' "$command_name" "$package_hint"
        missing_optional+=("$command_name")
    fi
}

echo "repo_root: $repo_root"
if [[ -r /etc/os-release ]]; then
    # This system file is intentionally optional.
    # shellcheck disable=SC1091
    . /etc/os-release
    echo "os: ${PRETTY_NAME:-unknown}"
fi

require_command git git
require_command python3 python3
require_command gcc build-essential
require_command g++ build-essential
require_command make build-essential
require_command curl curl
require_command pkg-config pkg-config
require_command uv "curl -LsSf https://astral.sh/uv/install.sh | sh"
optional_command cmake cmake
optional_command ninja ninja-build

python_check="$(python3 - <<'PY'
import sys
version = sys.version_info
print(f"{version.major}.{version.minor}.{version.micro}")
PY
)"
echo "python3_version: ${python_check:-unknown}"
if ! python3 -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 9) else 1)'; then
    missing_required+=("python3>=3.9")
fi

runtime_ipopt_root="${EPCSAFT_IPOPT_ROOT:-}"
pep517_ipopt_root="${EPCSAFT_PEP517_IPOPT_ROOT:-}"
ipopt_root=""
ipopt_root_source=""
if [[ -n "$runtime_ipopt_root" && -n "$pep517_ipopt_root" ]]; then
    runtime_ipopt_normalized="$(python3 -c 'from pathlib import Path; import sys; print(Path(sys.argv[1]).expanduser().resolve())' "$runtime_ipopt_root")"
    pep517_ipopt_normalized="$(python3 -c 'from pathlib import Path; import sys; print(Path(sys.argv[1]).expanduser().resolve())' "$pep517_ipopt_root")"
    if [[ "$runtime_ipopt_normalized" != "$pep517_ipopt_normalized" ]]; then
        echo "EPCSAFT_IPOPT_ROOT and EPCSAFT_PEP517_IPOPT_ROOT disagree:" >&2
        echo "  EPCSAFT_IPOPT_ROOT=$runtime_ipopt_normalized" >&2
        echo "  EPCSAFT_PEP517_IPOPT_ROOT=$pep517_ipopt_normalized" >&2
        exit 1
    fi
    ipopt_root="$runtime_ipopt_normalized"
    ipopt_root_source="EPCSAFT_IPOPT_ROOT/EPCSAFT_PEP517_IPOPT_ROOT"
elif [[ -n "$runtime_ipopt_root" ]]; then
    ipopt_root="$runtime_ipopt_root"
    ipopt_root_source="EPCSAFT_IPOPT_ROOT"
elif [[ -n "$pep517_ipopt_root" ]]; then
    ipopt_root="$pep517_ipopt_root"
    ipopt_root_source="EPCSAFT_PEP517_IPOPT_ROOT"
fi

if [[ -n "$ipopt_root" ]] \
    && find "$ipopt_root/include" -type f -name IpIpoptApplication.hpp -print -quit 2>/dev/null | grep -q . \
    && find "$ipopt_root" -type f \( -name 'libipopt.so' -o -name 'libipopt.so.*' \) -print -quit 2>/dev/null | grep -q .; then
    echo "ipopt_development_files: $ipopt_root_source=$ipopt_root"
elif [[ -n "$ipopt_root" ]]; then
    echo "missing: $ipopt_root_source does not contain Ipopt headers and a shared libipopt.so* library: $ipopt_root"
    if [[ "$mode" == "check" ]]; then
        missing_required+=("ipopt-development-files")
    else
        missing_optional+=("ipopt-development-files")
    fi
elif pkg-config --exists ipopt; then
    echo "ipopt_development_files: pkg-config"
else
    echo "missing: Ipopt development files (install package: coinor-libipopt-dev or set EPCSAFT_IPOPT_ROOT/EPCSAFT_PEP517_IPOPT_ROOT)"
    if [[ "$mode" == "check" ]]; then
        missing_required+=("ipopt-development-files")
    else
        missing_optional+=("ipopt-development-files")
    fi
fi

if command -v uv >/dev/null 2>&1; then
    echo "uv_version: $(uv --version)"
    if uv python find 3.13 >/dev/null 2>&1; then
        echo "uv_python_3.13: available"
    else
        echo "uv_python_3.13: missing"
        echo "uv_python_3.13_install_command: uv python install 3.13"
    fi
else
    echo "uv_install_command: curl -LsSf https://astral.sh/uv/install.sh | sh"
fi

if ((${#missing_required[@]} > 0)); then
    echo "prereq_state: missing-required"
    echo "missing_required: ${missing_required[*]}"
    echo "install_commands:"
    print_install_commands
    exit 1
fi

if ((${#missing_optional[@]} > 0)); then
    echo "prereq_state: usable-with-uv-managed-tools"
    echo "missing_optional: ${missing_optional[*]}"
else
    echo "prereq_state: ready"
fi
