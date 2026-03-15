"""Tests for pag.cli using CliRunner (no real API calls)."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from pag.cli import main, _parse_size
from pag.models import InferenceResponse


@pytest.fixture()
def runner():
    return CliRunner()


# ── _parse_size ──────────────────────────────────────────────────────────────


class TestParseSize:
    def test_valid(self):
        assert _parse_size("128x128") == (128, 128)

    def test_case_insensitive(self):
        assert _parse_size("256X256") == (256, 256)

    def test_invalid_format(self):
        from click import BadParameter
        with pytest.raises(BadParameter):
            _parse_size("not-a-size")


# ── version / help ───────────────────────────────────────────────────────────


def test_version(runner):
    result = runner.invoke(main, ["--version"])
    assert result.exit_code == 0
    assert "0.1.0" in result.output


def test_help(runner):
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    assert "generate" in result.output
    assert "animate" in result.output
    assert "cost" in result.output
    assert "styles" in result.output
    assert "list-styles" in result.output


# ── list-styles ──────────────────────────────────────────────────────────────


def test_list_styles(runner):
    result = runner.invoke(main, ["list-styles"])
    assert result.exit_code == 0
    assert "rd_pro__default" in result.output


def test_list_styles_filtered(runner):
    result = runner.invoke(main, ["list-styles", "--model", "animation"])
    assert result.exit_code == 0
    assert "animation__" in result.output
    assert "rd_pro__" not in result.output


# ── generate ─────────────────────────────────────────────────────────────────


def _mock_response(**overrides):
    defaults = dict(
        created_at=1000,
        balance_cost=0.5,
        base64_images=["aGVsbG8="],  # "hello" in base64
        model="rd_pro",
        remaining_balance=99.5,
    )
    defaults.update(overrides)
    return InferenceResponse(**defaults)


@patch("pag.cli.RetroClient")
@patch("pag.cli.resolve_api_key", return_value="test-key")
def test_generate_basic(mock_key, mock_client_cls, runner, tmp_path):
    mock_client = MagicMock()
    mock_client.infer.return_value = _mock_response()
    mock_client.__enter__ = MagicMock(return_value=mock_client)
    mock_client.__exit__ = MagicMock(return_value=False)
    mock_client_cls.return_value = mock_client

    result = runner.invoke(main, [
        "generate", "a cat",
        "--style", "rd_pro__default",
        "--size", "128x128",
        "-o", str(tmp_path / "cat.png"),
    ])
    assert result.exit_code == 0
    assert "Saved:" in result.output
    assert (tmp_path / "cat.png").exists()


@patch("pag.cli.RetroClient")
@patch("pag.cli.resolve_api_key", return_value="test-key")
def test_generate_stdout(mock_key, mock_client_cls, runner):
    mock_client = MagicMock()
    mock_client.infer.return_value = _mock_response()
    mock_client.__enter__ = MagicMock(return_value=mock_client)
    mock_client.__exit__ = MagicMock(return_value=False)
    mock_client_cls.return_value = mock_client

    result = runner.invoke(main, [
        "generate", "a cat",
        "--style", "rd_pro__default",
        "--stdout",
    ])
    assert result.exit_code == 0
    assert "aGVsbG8=" in result.output


def test_generate_unknown_style(runner):
    result = runner.invoke(main, [
        "generate", "a cat",
        "--style", "nonexistent",
        "--api-key", "test",
    ])
    assert result.exit_code != 0


def test_generate_missing_style(runner):
    result = runner.invoke(main, [
        "generate", "a cat",
    ])
    assert result.exit_code != 0


@patch("pag.cli.RetroClient")
@patch("pag.cli.resolve_api_key", return_value="test-key")
def test_generate_multiple_images(mock_key, mock_client_cls, runner, tmp_path):
    mock_client = MagicMock()
    mock_client.infer.return_value = _mock_response(
        base64_images=["aGVsbG8=", "d29ybGQ="]
    )
    mock_client.__enter__ = MagicMock(return_value=mock_client)
    mock_client.__exit__ = MagicMock(return_value=False)
    mock_client_cls.return_value = mock_client

    result = runner.invoke(main, [
        "generate", "a cat",
        "--style", "rd_pro__default",
        "-n", "2",
        "-d", str(tmp_path),
    ])
    assert result.exit_code == 0
    assert result.output.count("Saved:") == 2


# ── animate ──────────────────────────────────────────────────────────────────


@patch("pag.cli.RetroClient")
@patch("pag.cli.resolve_api_key", return_value="test-key")
def test_animate_basic(mock_key, mock_client_cls, runner, tmp_path):
    mock_client = MagicMock()
    mock_client.infer.return_value = _mock_response()
    mock_client.__enter__ = MagicMock(return_value=mock_client)
    mock_client.__exit__ = MagicMock(return_value=False)
    mock_client_cls.return_value = mock_client

    result = runner.invoke(main, [
        "animate", "walking knight",
        "--style", "walking_and_idle",
        "-o", str(tmp_path / "knight.gif"),
    ])
    assert result.exit_code == 0
    assert "Saved:" in result.output


@patch("pag.cli.RetroClient")
@patch("pag.cli.resolve_api_key", return_value="test-key")
def test_animate_spritesheet(mock_key, mock_client_cls, runner, tmp_path):
    mock_client = MagicMock()
    mock_client.infer.return_value = _mock_response()
    mock_client.__enter__ = MagicMock(return_value=mock_client)
    mock_client.__exit__ = MagicMock(return_value=False)
    mock_client_cls.return_value = mock_client

    result = runner.invoke(main, [
        "animate", "walking knight",
        "--style", "walking_and_idle",
        "--spritesheet",
        "-o", str(tmp_path / "knight.png"),
    ])
    assert result.exit_code == 0
    assert (tmp_path / "knight.png").exists()


@patch("pag.cli.RetroClient")
@patch("pag.cli.resolve_api_key", return_value="test-key")
def test_animate_accepts_full_key(mock_key, mock_client_cls, runner, tmp_path):
    mock_client = MagicMock()
    mock_client.infer.return_value = _mock_response()
    mock_client.__enter__ = MagicMock(return_value=mock_client)
    mock_client.__exit__ = MagicMock(return_value=False)
    mock_client_cls.return_value = mock_client

    result = runner.invoke(main, [
        "animate", "fire",
        "--style", "animation__vfx",
        "-o", str(tmp_path / "fire.gif"),
    ])
    assert result.exit_code == 0


# ── cost ─────────────────────────────────────────────────────────────────────


@patch("pag.cli.RetroClient")
@patch("pag.cli.resolve_api_key", return_value="test-key")
def test_cost(mock_key, mock_client_cls, runner):
    mock_client = MagicMock()
    mock_client.infer.return_value = _mock_response(
        model="check_cost", base64_images=[]
    )
    mock_client.__enter__ = MagicMock(return_value=mock_client)
    mock_client.__exit__ = MagicMock(return_value=False)
    mock_client_cls.return_value = mock_client

    result = runner.invoke(main, [
        "cost", "a cat",
        "--style", "rd_pro__default",
    ])
    assert result.exit_code == 0
    assert "Estimated cost:" in result.output
    assert "0.5" in result.output


# ── styles subcommands ───────────────────────────────────────────────────────


def test_styles_list(runner):
    result = runner.invoke(main, ["styles", "list"])
    assert result.exit_code == 0
    assert "rd_pro__default" in result.output


def test_styles_list_filtered_by_model(runner):
    result = runner.invoke(main, ["styles", "list", "--model", "animation"])
    assert result.exit_code == 0
    assert "animation__" in result.output
    assert "rd_pro__" not in result.output


@patch("pag.cli.RetroClient")
@patch("pag.cli.resolve_api_key", return_value="test-key")
def test_styles_create(mock_key, mock_client_cls, runner):
    from pag.models import StyleResponse
    mock_client = MagicMock()
    mock_client.create_style.return_value = StyleResponse(
        id="s1", name="my style"
    )
    mock_client.__enter__ = MagicMock(return_value=mock_client)
    mock_client.__exit__ = MagicMock(return_value=False)
    mock_client_cls.return_value = mock_client

    result = runner.invoke(main, [
        "styles", "create", "--name", "my style",
    ])
    assert result.exit_code == 0
    assert "Created style:" in result.output


@patch("pag.cli.RetroClient")
@patch("pag.cli.resolve_api_key", return_value="test-key")
def test_styles_update(mock_key, mock_client_cls, runner):
    from pag.models import StyleResponse
    mock_client = MagicMock()
    mock_client.update_style.return_value = StyleResponse(
        id="s1", name="renamed"
    )
    mock_client.__enter__ = MagicMock(return_value=mock_client)
    mock_client.__exit__ = MagicMock(return_value=False)
    mock_client_cls.return_value = mock_client

    result = runner.invoke(main, [
        "styles", "update", "s1", "--name", "renamed",
    ])
    assert result.exit_code == 0
    assert "Updated style:" in result.output


@patch("pag.cli.RetroClient")
@patch("pag.cli.resolve_api_key", return_value="test-key")
def test_styles_delete(mock_key, mock_client_cls, runner):
    mock_client = MagicMock()
    mock_client.__enter__ = MagicMock(return_value=mock_client)
    mock_client.__exit__ = MagicMock(return_value=False)
    mock_client_cls.return_value = mock_client

    result = runner.invoke(main, [
        "styles", "delete", "s1",
    ])
    assert result.exit_code == 0
    assert "Deleted style:" in result.output
