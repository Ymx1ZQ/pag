"""Verify basic project scaffolding."""

from click.testing import CliRunner

from pag import __version__
from pag.cli import main


def test_version_string():
    assert __version__ == "0.1.0"


def test_cli_version_flag():
    result = CliRunner().invoke(main, ["--version"])
    assert result.exit_code == 0
    assert "0.1.0" in result.output


def test_cli_help():
    result = CliRunner().invoke(main, ["--help"])
    assert result.exit_code == 0
    assert "Retro Diffusion" in result.output


def test_subcommands_exist():
    result = CliRunner().invoke(main, ["--help"])
    for cmd in ("generate", "animate", "cost", "styles"):
        assert cmd in result.output
