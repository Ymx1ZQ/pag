"""API key resolution for pag.

Precedence: explicit value > RETRODIFFUSION_API_KEY env var > .env file.
"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import dotenv_values


class ConfigError(Exception):
    """Raised when configuration is invalid or missing."""


def resolve_api_key(explicit: str | None = None) -> str:
    """Return the Retro Diffusion API key.

    Resolution order:
    1. *explicit* argument (from ``--api-key`` flag)
    2. ``RETRODIFFUSION_API_KEY`` environment variable
    3. ``.env`` file in the current working directory
    """
    if explicit:
        return explicit

    from_env = os.environ.get("RETRODIFFUSION_API_KEY")
    if from_env:
        return from_env

    dot_env_path = Path.cwd() / ".env"
    if dot_env_path.is_file():
        values = dotenv_values(dot_env_path)
        from_dotenv = values.get("RETRODIFFUSION_API_KEY")
        if from_dotenv:
            return from_dotenv

    raise ConfigError(
        "No API key found. Set RETRODIFFUSION_API_KEY via --api-key, "
        "environment variable, or .env file."
    )
