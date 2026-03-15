"""CLI entry point for pag."""

import click

from pag import __version__


@click.group()
@click.version_option(version=__version__, prog_name="pag")
def main() -> None:
    """pag — Pixel Art Generator powered by Retro Diffusion."""


@main.command()
@click.argument("prompt")
def generate(prompt: str) -> None:
    """Generate pixel art from a text prompt."""
    click.echo(f"generate: {prompt} (not yet implemented)")


@main.command()
@click.argument("prompt")
def animate(prompt: str) -> None:
    """Generate an animated sprite from a text prompt."""
    click.echo(f"animate: {prompt} (not yet implemented)")


@main.command()
@click.argument("prompt")
def cost(prompt: str) -> None:
    """Estimate the credit cost of a generation."""
    click.echo(f"cost: {prompt} (not yet implemented)")


@main.group()
def styles() -> None:
    """Manage custom Retro Diffusion styles."""


@styles.command("list")
def styles_list() -> None:
    """List custom styles."""
    click.echo("styles list (not yet implemented)")
