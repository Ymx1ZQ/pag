"""Output handling: base64 decoding, filename resolution, file saving."""

from __future__ import annotations

import base64
import re
import sys
import time
from pathlib import Path


def make_slug(text: str, max_len: int = 48) -> str:
    """Convert *text* to a filesystem-safe slug.

    Lowercase, replace non-alphanumeric chars with ``_``, strip trailing
    underscores, and truncate to *max_len*.
    """
    slug = re.sub(r"[^a-z0-9]+", "_", text.lower())
    slug = slug.strip("_")
    return slug[:max_len].rstrip("_")


def resolve_filename(
    *,
    index: int,
    num_images: int,
    prompt: str,
    style: str,
    seed: int | None,
    is_animation: bool,
    output: str | None = None,
    output_dir: str | None = None,
    name_pattern: str | None = None,
) -> Path:
    """Determine the output file path for a single image.

    Priority:
    1. *output* — exact file path (used as-is for single image; index
       suffix appended for multiple).
    2. *output_dir* + *name_pattern* — template-based naming in directory.
    3. *output_dir* + default pattern — auto-generated name in directory.
    4. Default pattern in current working directory.
    """
    ext = ".gif" if is_animation else ".png"
    timestamp = str(int(time.time()))

    if output:
        p = Path(output)
        if num_images > 1:
            return p.with_stem(f"{p.stem}_{index}").with_suffix(ext)
        return p.with_suffix(ext) if p.suffix == "" else p

    pattern = name_pattern or _default_pattern(num_images)
    filename = _expand_pattern(
        pattern, prompt=prompt, style=style, seed=seed,
        n=index, timestamp=timestamp,
    ) + ext

    directory = Path(output_dir) if output_dir else Path.cwd()
    return directory / filename


def _default_pattern(num_images: int) -> str:
    if num_images > 1:
        return "{prompt_slug}_{timestamp}_{n}"
    return "{prompt_slug}_{timestamp}"


def _expand_pattern(
    pattern: str,
    *,
    prompt: str,
    style: str,
    seed: int | None,
    n: int,
    timestamp: str,
) -> str:
    return pattern.format(
        prompt=make_slug(prompt),
        prompt_slug=make_slug(prompt),
        style=style.replace("__", "_"),
        seed=seed if seed is not None else "noseed",
        n=n,
        timestamp=timestamp,
    )


def decode_and_save(b64_data: str, path: Path) -> Path:
    """Decode a base64 string and write it to *path*. Returns *path*."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(base64.b64decode(b64_data))
    return path


def write_stdout(b64_data: str) -> None:
    """Write raw base64 string to stdout (for piping)."""
    sys.stdout.write(b64_data)
    sys.stdout.write("\n")
    sys.stdout.flush()
