"""Live tests for image generation."""

from __future__ import annotations

import base64

from pag.models import InferenceRequest


def test_basic_generation(client):
    """Generate a single small image with rd_fast for speed."""
    req = InferenceRequest(
        prompt="a small red mushroom",
        width=64,
        height=64,
        prompt_style="rd_fast__simple",
        num_images=1,
    )
    resp = client.infer(req)
    assert resp.model == "rd_fast"
    assert len(resp.base64_images) == 1
    assert len(resp.base64_images[0]) > 100  # non-trivial base64
    # Verify it's valid base64
    raw = base64.b64decode(resp.base64_images[0])
    assert len(raw) > 0


def test_multiple_images(client):
    """Generate 2 images in one request."""
    req = InferenceRequest(
        prompt="a blue gem",
        width=64,
        height=64,
        prompt_style="rd_fast__simple",
        num_images=2,
    )
    resp = client.infer(req)
    assert len(resp.base64_images) == 2


def test_with_seed(client):
    """Generation with a seed should succeed."""
    req = InferenceRequest(
        prompt="a green slime",
        width=64,
        height=64,
        prompt_style="rd_fast__simple",
        num_images=1,
        seed=12345,
    )
    resp = client.infer(req)
    assert len(resp.base64_images) == 1


def test_remove_bg(client):
    """Generate with background removal — should succeed."""
    req = InferenceRequest(
        prompt="a golden key",
        width=64,
        height=64,
        prompt_style="rd_fast__simple",
        num_images=1,
        remove_bg=True,
    )
    resp = client.infer(req)
    assert len(resp.base64_images) == 1


def test_tiling(client):
    """Generate with tiling enabled."""
    req = InferenceRequest(
        prompt="grass texture",
        width=64,
        height=64,
        prompt_style="rd_fast__texture",
        num_images=1,
        tile_x=True,
        tile_y=True,
    )
    resp = client.infer(req)
    assert len(resp.base64_images) == 1
