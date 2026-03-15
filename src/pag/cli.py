"""CLI entry point for pag."""

from __future__ import annotations

import base64
import sys
from pathlib import Path

import click

from pag import __version__
from pag.client import APIError, RetroClient
from pag.config import ConfigError, get_saved_key, mask_key, resolve_api_key, save_api_key
from pag.models import InferenceRequest, StyleCreateRequest, StyleUpdateRequest
from pag.output import decode_and_save, resolve_filename, write_stdout
from pag.styles import get_style, list_styles, validate_size


def _parse_size(size: str) -> tuple[int, int]:
    """Parse a ``WxH`` string into (width, height)."""
    try:
        w, h = size.lower().split("x")
        return int(w), int(h)
    except (ValueError, AttributeError):
        raise click.BadParameter(f"Invalid size format: {size!r}. Use WxH (e.g. 128x128)")


def _read_ref_image(path: str) -> str:
    """Read a file and return its base64-encoded content."""
    data = Path(path).read_bytes()
    return base64.b64encode(data).decode()


def _handle_error(e: Exception) -> None:
    """Print error and exit."""
    click.echo(f"Error: {e}", err=True)
    sys.exit(1)


# ── Main group ───────────────────────────────────────────────────────────────


@click.group()
@click.version_option(version=__version__, prog_name="pag")
@click.option("-v", "--verbose", is_flag=True, help="Show request/response payloads.")
@click.pass_context
def main(ctx: click.Context, verbose: bool) -> None:
    """pag — Pixel Art Generator powered by Retro Diffusion."""
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose


# ── list-styles (top-level) ──────────────────────────────────────────────────


@main.command("list-styles")
@click.option("--model", type=click.Choice(["rd_pro", "rd_fast", "rd_plus", "animation"]), default=None)
def list_styles_cmd(model: str | None) -> None:
    """List all available built-in styles."""
    for s in list_styles(model):
        click.echo(f"  {s.key:<40s}  {s.label}  ({s.min_w}x{s.min_h} → {s.max_w}x{s.max_h})")


# ── generate ─────────────────────────────────────────────────────────────────


@main.command()
@click.argument("prompt")
@click.option("--style", required=True, help="Style key (e.g. rd_pro__default). Use `pag list-styles` to see all.")
@click.option("--size", default=None, help="Image size as WxH (e.g. 128x128). Defaults to style minimum.")
@click.option("-n", "--num-images", default=1, type=int, help="Number of images to generate.")
@click.option("--seed", default=None, type=int, help="Seed for reproducibility.")
@click.option("--ref", multiple=True, type=click.Path(exists=True), help="Reference image (can be repeated).")
@click.option("--tile-x", is_flag=True, help="Enable horizontal tiling.")
@click.option("--tile-y", is_flag=True, help="Enable vertical tiling.")
@click.option("--remove-bg", is_flag=True, help="Remove background.")
@click.option("-o", "--output", default=None, help="Output file path (exact).")
@click.option("-d", "--output-dir", default=None, type=click.Path(), help="Output directory.")
@click.option("--name-pattern", default=None, help="Filename pattern with {prompt_slug}, {style}, {seed}, {n}, {timestamp}.")
@click.option("--stdout", "to_stdout", is_flag=True, help="Write base64 to stdout instead of files.")
@click.option("--api-key", default=None, envvar="RETRODIFFUSION_API_KEY", help="API key (overrides env/dotenv).")
def generate(
    prompt: str,
    style: str,
    size: str | None,
    num_images: int,
    seed: int | None,
    ref: tuple[str, ...],
    tile_x: bool,
    tile_y: bool,
    remove_bg: bool,
    output: str | None,
    output_dir: str | None,
    name_pattern: str | None,
    to_stdout: bool,
    api_key: str | None,
) -> None:
    """Generate pixel art from a text prompt."""
    verbose = click.get_current_context().obj.get("verbose", False)
    try:
        key = resolve_api_key(api_key)
    except ConfigError as e:
        _handle_error(e)

    style_info = get_style(style)
    if style_info is None:
        _handle_error(click.BadParameter(f"Unknown style: {style!r}. Use `pag list-styles`."))

    if size:
        width, height = _parse_size(size)
    else:
        width, height = style_info.min_w, style_info.min_h

    try:
        validate_size(style_info, width, height)
    except ValueError as e:
        _handle_error(e)

    ref_images = [_read_ref_image(r) for r in ref] if ref else None

    req = InferenceRequest(
        prompt=prompt,
        width=width,
        height=height,
        prompt_style=style,
        num_images=num_images,
        seed=seed,
        reference_images=ref_images,
        tile_x=tile_x,
        tile_y=tile_y,
        remove_bg=remove_bg,
    )

    try:
        with RetroClient(key, verbose=verbose) as client:
            resp = client.infer(req)
    except APIError as e:
        _handle_error(e)

    for i, b64 in enumerate(resp.base64_images):
        if to_stdout:
            write_stdout(b64)
        else:
            path = resolve_filename(
                index=i,
                num_images=num_images,
                prompt=prompt,
                style=style,
                seed=seed,
                is_animation=False,
                output=output,
                output_dir=output_dir,
                name_pattern=name_pattern,
            )
            decode_and_save(b64, path)
            click.echo(f"Saved: {path}")

    click.echo(f"Cost: {resp.balance_cost} credits (remaining: {resp.remaining_balance})", err=True)


# ── animate ──────────────────────────────────────────────────────────────────


@main.command()
@click.argument("prompt")
@click.option("--style", required=True, help="Animation style (e.g. walking_and_idle, vfx). Use `pag list-styles --model animation`.")
@click.option("--size", default=None, help="Image size as WxH. Defaults to style default.")
@click.option("--spritesheet", is_flag=True, help="Output PNG spritesheet instead of GIF.")
@click.option("-o", "--output", default=None, help="Output file path.")
@click.option("-d", "--output-dir", default=None, type=click.Path(), help="Output directory.")
@click.option("--name-pattern", default=None, help="Filename pattern.")
@click.option("--stdout", "to_stdout", is_flag=True, help="Write base64 to stdout.")
@click.option("--api-key", default=None, envvar="RETRODIFFUSION_API_KEY", help="API key.")
def animate(
    prompt: str,
    style: str,
    size: str | None,
    spritesheet: bool,
    output: str | None,
    output_dir: str | None,
    name_pattern: str | None,
    to_stdout: bool,
    api_key: str | None,
) -> None:
    """Generate an animated sprite from a text prompt."""
    verbose = click.get_current_context().obj.get("verbose", False)
    try:
        key = resolve_api_key(api_key)
    except ConfigError as e:
        _handle_error(e)

    full_key = style if style.startswith("animation__") else f"animation__{style}"
    style_info = get_style(full_key)
    if style_info is None:
        _handle_error(click.BadParameter(f"Unknown animation style: {style!r}. Use `pag list-styles --model animation`."))

    if size:
        width, height = _parse_size(size)
    else:
        width, height = style_info.min_w, style_info.min_h

    try:
        validate_size(style_info, width, height)
    except ValueError as e:
        _handle_error(e)

    req = InferenceRequest(
        prompt=prompt,
        width=width,
        height=height,
        prompt_style=full_key,
        num_images=1,
        return_spritesheet=spritesheet or None,
    )

    try:
        with RetroClient(key, verbose=verbose) as client:
            resp = client.infer(req)
    except APIError as e:
        _handle_error(e)

    is_animation = not spritesheet

    for i, b64 in enumerate(resp.base64_images):
        if to_stdout:
            write_stdout(b64)
        else:
            path = resolve_filename(
                index=i,
                num_images=1,
                prompt=prompt,
                style=full_key,
                seed=None,
                is_animation=is_animation,
                output=output,
                output_dir=output_dir,
                name_pattern=name_pattern,
            )
            decode_and_save(b64, path)
            click.echo(f"Saved: {path}")

    click.echo(f"Cost: {resp.balance_cost} credits (remaining: {resp.remaining_balance})", err=True)


# ── cost ─────────────────────────────────────────────────────────────────────


@main.command()
@click.argument("prompt")
@click.option("--style", required=True, help="Style key.")
@click.option("--size", default=None, help="Image size as WxH.")
@click.option("-n", "--num-images", default=1, type=int, help="Number of images.")
@click.option("--api-key", default=None, envvar="RETRODIFFUSION_API_KEY", help="API key.")
def cost(
    prompt: str,
    style: str,
    size: str | None,
    num_images: int,
    api_key: str | None,
) -> None:
    """Estimate the credit cost without generating images."""
    verbose = click.get_current_context().obj.get("verbose", False)
    try:
        key = resolve_api_key(api_key)
    except ConfigError as e:
        _handle_error(e)

    style_info = get_style(style)
    if style_info is None:
        _handle_error(click.BadParameter(f"Unknown style: {style!r}"))

    if size:
        width, height = _parse_size(size)
    else:
        width, height = style_info.min_w, style_info.min_h

    req = InferenceRequest(
        prompt=prompt,
        width=width,
        height=height,
        prompt_style=style,
        num_images=num_images,
        check_cost=True,
    )

    try:
        with RetroClient(key, verbose=verbose) as client:
            resp = client.infer(req)
    except APIError as e:
        _handle_error(e)

    click.echo(f"Estimated cost: {resp.balance_cost} credits")
    click.echo(f"Remaining balance: {resp.remaining_balance} credits")


# ── styles ───────────────────────────────────────────────────────────────────


@main.group()
def styles() -> None:
    """Manage custom Retro Diffusion styles."""


@styles.command("list")
@click.option("--model", type=click.Choice(["rd_pro", "rd_fast", "rd_plus", "animation"]), default=None)
def styles_list(model: str | None) -> None:
    """List available built-in styles."""
    for s in list_styles(model):
        click.echo(f"  {s.key:<40s}  {s.label}  ({s.min_w}x{s.min_h} → {s.max_w}x{s.max_h})")


@styles.command("create")
@click.option("--name", required=True, help="Style name.")
@click.option("--description", default=None, help="Style description.")
@click.option("--ref", default=None, type=click.Path(exists=True), help="Reference image.")
@click.option("--icon", default=None, help="Style icon name.")
@click.option("--api-key", default=None, envvar="RETRODIFFUSION_API_KEY", help="API key.")
def styles_create(
    name: str,
    description: str | None,
    ref: str | None,
    icon: str | None,
    api_key: str | None,
) -> None:
    """Create a new custom style."""
    verbose = click.get_current_context().obj.get("verbose", False)
    try:
        key = resolve_api_key(api_key)
    except ConfigError as e:
        _handle_error(e)

    ref_images = [_read_ref_image(ref)] if ref else None

    req = StyleCreateRequest(
        name=name,
        description=description,
        style_icon=icon,
        reference_images=ref_images,
    )

    try:
        with RetroClient(key, verbose=verbose) as client:
            resp = client.create_style(req)
    except APIError as e:
        _handle_error(e)

    click.echo(f"Created style: {resp.id} ({resp.name})")


@styles.command("update")
@click.argument("style_id")
@click.option("--name", default=None, help="New name.")
@click.option("--description", default=None, help="New description.")
@click.option("--api-key", default=None, envvar="RETRODIFFUSION_API_KEY", help="API key.")
def styles_update(
    style_id: str,
    name: str | None,
    description: str | None,
    api_key: str | None,
) -> None:
    """Update an existing custom style."""
    verbose = click.get_current_context().obj.get("verbose", False)
    try:
        key = resolve_api_key(api_key)
    except ConfigError as e:
        _handle_error(e)

    req = StyleUpdateRequest(name=name, description=description)

    try:
        with RetroClient(key, verbose=verbose) as client:
            resp = client.update_style(style_id, req)
    except APIError as e:
        _handle_error(e)

    click.echo(f"Updated style: {resp.id} ({resp.name})")


@styles.command("delete")
@click.argument("style_id")
@click.option("--api-key", default=None, envvar="RETRODIFFUSION_API_KEY", help="API key.")
def styles_delete(style_id: str, api_key: str | None) -> None:
    """Delete a custom style."""
    verbose = click.get_current_context().obj.get("verbose", False)
    try:
        key = resolve_api_key(api_key)
    except ConfigError as e:
        _handle_error(e)

    try:
        with RetroClient(key, verbose=verbose) as client:
            client.delete_style(style_id)
    except APIError as e:
        _handle_error(e)

    click.echo(f"Deleted style: {style_id}")


# ── config ───────────────────────────────────────────────────────────────────


@main.group()
def config() -> None:
    """Manage pag configuration."""


@config.command("set-key")
@click.argument("key", required=False)
def config_set_key(key: str | None) -> None:
    """Save your API key to ~/.pag/.env.

    Pass the key as argument, or omit it for an interactive prompt.
    """
    if not key:
        key = click.prompt("Enter your Retro Diffusion API key", hide_input=True)
    path = save_api_key(key)
    click.echo(f"API key saved to {path}")


@config.command("show")
def config_show() -> None:
    """Show the current API key configuration."""
    saved = get_saved_key()
    if saved:
        click.echo(f"API key: {mask_key(saved)}")
        click.echo(f"Source:  ~/.pag/.env")
    else:
        click.echo("No API key configured. Run `pag config set-key` to set one.")
