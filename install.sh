#!/usr/bin/env bash
set -euo pipefail

echo "=== pag installer ==="

# 1. Install uv if missing
if ! command -v uv &>/dev/null; then
    echo "uv not found — installing..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$PATH"
    echo "uv installed."
else
    echo "uv found: $(uv --version)"
fi

# 2. Install pag as a global CLI tool
echo "Installing pag..."
uv tool install --force .

# 3. Verify
if pag --version; then
    echo "=== pag installed successfully ==="
else
    echo "ERROR: pag --version failed. Make sure ~/.local/bin is in your PATH." >&2
    exit 1
fi
