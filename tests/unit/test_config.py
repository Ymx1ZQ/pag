"""Tests for pag.config."""

import pytest

from pag.config import ConfigError, get_saved_key, mask_key, resolve_api_key, save_api_key
import pag.config as config_module


@pytest.fixture(autouse=True)
def _isolate_config(tmp_path, monkeypatch):
    """Point CONFIG_DIR/CONFIG_ENV to a temp dir for every test."""
    fake_dir = tmp_path / ".pag"
    fake_env = fake_dir / ".env"
    monkeypatch.setattr(config_module, "CONFIG_DIR", fake_dir)
    monkeypatch.setattr(config_module, "CONFIG_ENV", fake_env)


# ── resolve_api_key ──────────────────────────────────────────────────────────


def test_explicit_key_wins(tmp_path):
    save_api_key("saved_key")
    assert resolve_api_key("explicit_key") == "explicit_key"


def test_saved_key_used_when_no_explicit(tmp_path):
    save_api_key("saved_key")
    assert resolve_api_key() == "saved_key"


def test_raises_when_no_key():
    with pytest.raises(ConfigError, match="No API key found"):
        resolve_api_key()


def test_empty_explicit_falls_through():
    save_api_key("saved_key")
    assert resolve_api_key("") == "saved_key"


def test_raises_when_env_file_empty(tmp_path):
    config_module.CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    config_module.CONFIG_ENV.write_text("")
    with pytest.raises(ConfigError):
        resolve_api_key()


# ── save_api_key ─────────────────────────────────────────────────────────────


def test_save_creates_file():
    path = save_api_key("my_key_123")
    assert path.exists()
    assert "my_key_123" in path.read_text()


def test_save_overwrites():
    save_api_key("old_key")
    save_api_key("new_key")
    assert resolve_api_key() == "new_key"


# ── get_saved_key ────────────────────────────────────────────────────────────


def test_get_saved_key_exists():
    save_api_key("abc123")
    assert get_saved_key() == "abc123"


def test_get_saved_key_none_when_missing():
    assert get_saved_key() is None


# ── mask_key ─────────────────────────────────────────────────────────────────


def test_mask_key_long():
    assert mask_key("rdpk-298e51066e4007c051b39ead98eeb8dd") == "rdpk...b8dd"


def test_mask_key_short():
    assert mask_key("abc") == "****"
