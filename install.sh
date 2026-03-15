#!/usr/bin/env bash
set -euo pipefail

echo "=== pag installer ==="

# 1. Check Python version
if command -v python3 &>/dev/null; then
    PY_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
    echo "Python $PY_VERSION found."
    PY_MAJOR=$(echo "$PY_VERSION" | cut -d. -f1)
    PY_MINOR=$(echo "$PY_VERSION" | cut -d. -f2)
    if [ "$PY_MAJOR" -lt 3 ] || { [ "$PY_MAJOR" -eq 3 ] && [ "$PY_MINOR" -lt 12 ]; }; then
        echo "ERROR: Python 3.12+ is required (found $PY_VERSION)" >&2
        exit 1
    fi
else
    echo "ERROR: python3 not found. Install Python 3.12+ first." >&2
    exit 1
fi

# 2. Install uv if missing
if ! command -v uv &>/dev/null; then
    echo "uv not found — installing..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$PATH"
    echo "uv installed: $(uv --version)"
else
    echo "uv found: $(uv --version)"
fi

# 3. Install pag as a global CLI tool
echo "Installing pag..."
uv tool install --force .

# 4. Verify
if pag --version; then
    echo "=== pag installed successfully ==="
    echo ""
    echo "Get started:"
    echo "  export RETRODIFFUSION_API_KEY=your_key"
    echo "  pag generate \"a cool corgi\" --style rd_fast__simple --size 64x64"
else
    echo "ERROR: pag --version failed." >&2
    echo "Make sure ~/.local/bin is in your PATH:" >&2
    echo "  export PATH=\"\$HOME/.local/bin:\$PATH\"" >&2
    exit 1
fi
