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
uv tool install --force --reinstall .

# 4. Verify
if ! pag --version; then
    echo "ERROR: pag --version failed." >&2
    echo "Make sure ~/.local/bin is in your PATH:" >&2
    echo "  export PATH=\"\$HOME/.local/bin:\$PATH\"" >&2
    exit 1
fi

echo "=== pag installed successfully ==="

# 5. Configure API key
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOCAL_ENV="$SCRIPT_DIR/.env"

if [ -f "$HOME/.pag/.env" ] && grep -q "RETRODIFFUSION_API_KEY=." "$HOME/.pag/.env" 2>/dev/null; then
    echo "API key already configured in ~/.pag/.env"
    read -rp "Do you want to replace it? [y/N] " answer
    answer=${answer:-N}
    if [[ "$answer" =~ ^[Yy] ]]; then
        read -rsp "Enter your new API key: " api_key
        echo ""
        echo "RETRODIFFUSION_API_KEY=$api_key" > "$HOME/.pag/.env"
        echo "API key updated in ~/.pag/.env"
    fi
elif [ -f "$LOCAL_ENV" ] && grep -q "RETRODIFFUSION_API_KEY=." "$LOCAL_ENV" 2>/dev/null; then
    # Found a .env in the repo directory — copy it to ~/.pag/
    echo "Found .env in project directory."
    mkdir -p "$HOME/.pag"
    cp "$LOCAL_ENV" "$HOME/.pag/.env"
    echo "API key copied to ~/.pag/.env"
else
    echo ""
    read -rp "Do you want to configure your Retro Diffusion API key now? [Y/n] " answer
    answer=${answer:-Y}
    if [[ "$answer" =~ ^[Yy] ]]; then
        read -rsp "Enter your API key: " api_key
        echo ""
        mkdir -p "$HOME/.pag"
        echo "RETRODIFFUSION_API_KEY=$api_key" > "$HOME/.pag/.env"
        echo "API key saved to ~/.pag/.env"
    else
        echo "Skipped. You can set it later with: pag config set-key"
    fi
fi

echo ""
echo "Get started:"
echo "  pag generate \"a cool corgi\" --style rd_fast__simple --size 64x64"
