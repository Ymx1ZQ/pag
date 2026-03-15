"""API key resolution for pag.

Precedence: --api-key flag > ~/.pag/.env
"""

from __future__ import annotations

from pathlib import Path

from dotenv import dotenv_values

CONFIG_DIR = Path.home() / ".pag"
CONFIG_ENV = CONFIG_DIR / ".env"


class ConfigError(Exception):
    """Raised when configuration is invalid or missing."""


def resolve_api_key(explicit: str | None = None) -> str:
    """Return the Retro Diffusion API key.

    Resolution order:
    1. *explicit* argument (from ``--api-key`` flag)
    2. ``~/.pag/.env`` file
    """
    if explicit:
        return explicit

    if CONFIG_ENV.is_file():
        values = dotenv_values(CONFIG_ENV)
        from_dotenv = values.get("RETRODIFFUSION_API_KEY")
        if from_dotenv:
            return from_dotenv

    raise ConfigError(
        "No API key found. Run `pag config set-key` or pass --api-key."
    )


def save_api_key(key: str) -> Path:
    """Save the API key to ``~/.pag/.env``. Returns the file path."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_ENV.write_text(f"RETRODIFFUSION_API_KEY={key}\n")
    return CONFIG_ENV


def get_saved_key() -> str | None:
    """Read the saved API key, or None if not configured."""
    if CONFIG_ENV.is_file():
        values = dotenv_values(CONFIG_ENV)
        return values.get("RETRODIFFUSION_API_KEY") or None
    return None


def mask_key(key: str) -> str:
    """Return a masked version of the key for display."""
    if len(key) <= 8:
        return "****"
    return f"{key[:4]}...{key[-4:]}"
