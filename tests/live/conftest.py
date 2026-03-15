"""Shared fixtures for live tests that hit the real Retro Diffusion API."""

from __future__ import annotations

import os

import pytest

from pag.client import RetroClient


def pytest_collection_modifyitems(config, items):
    """Skip all live tests if RETRODIFFUSION_API_KEY is not set."""
    if os.environ.get("RETRODIFFUSION_API_KEY"):
        return
    skip = pytest.mark.skip(reason="RETRODIFFUSION_API_KEY not set")
    for item in items:
        if "tests/live" in str(item.fspath):
            item.add_marker(skip)


@pytest.fixture(scope="session")
def api_key() -> str:
    return os.environ["RETRODIFFUSION_API_KEY"]


@pytest.fixture(scope="session")
def client(api_key: str) -> RetroClient:
    c = RetroClient(api_key)
    yield c
    c.close()
