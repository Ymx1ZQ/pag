"""Tests for pag.config."""

import os

import pytest

from pag.config import ConfigError, resolve_api_key


def test_explicit_key_takes_precedence(monkeypatch):
    monkeypatch.setenv("RETRODIFFUSION_API_KEY", "env_key")
    assert resolve_api_key("explicit_key") == "explicit_key"


def test_env_var_used_when_no_explicit(monkeypatch):
    monkeypatch.setenv("RETRODIFFUSION_API_KEY", "env_key")
    assert resolve_api_key() == "env_key"


def test_dotenv_used_when_no_env_var(monkeypatch, tmp_path):
    monkeypatch.delenv("RETRODIFFUSION_API_KEY", raising=False)
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".env").write_text("RETRODIFFUSION_API_KEY=dotenv_key\n")
    assert resolve_api_key() == "dotenv_key"


def test_raises_when_no_key(monkeypatch, tmp_path):
    monkeypatch.delenv("RETRODIFFUSION_API_KEY", raising=False)
    monkeypatch.chdir(tmp_path)
    with pytest.raises(ConfigError, match="No API key found"):
        resolve_api_key()


def test_empty_explicit_falls_through(monkeypatch):
    monkeypatch.setenv("RETRODIFFUSION_API_KEY", "env_key")
    assert resolve_api_key("") == "env_key"


def test_empty_env_var_falls_through(monkeypatch, tmp_path):
    monkeypatch.setenv("RETRODIFFUSION_API_KEY", "")
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".env").write_text("RETRODIFFUSION_API_KEY=dotenv_key\n")
    assert resolve_api_key() == "dotenv_key"
