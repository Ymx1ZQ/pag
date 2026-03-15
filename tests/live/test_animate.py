"""Live tests for animation generation."""

from __future__ import annotations

import base64

from pag.models import InferenceRequest


def test_animation_gif(client):
    """Generate an animation as GIF."""
    req = InferenceRequest(
        prompt="a walking cat",
        width=48,
        height=48,
        prompt_style="animation__walking_and_idle",
        num_images=1,
    )
    resp = client.infer(req)
    assert len(resp.base64_images) >= 1
    raw = base64.b64decode(resp.base64_images[0])
    # GIF files start with "GIF"
    assert raw[:3] == b"GIF"


def test_animation_spritesheet(client):
    """Generate an animation as PNG spritesheet."""
    req = InferenceRequest(
        prompt="a walking cat",
        width=48,
        height=48,
        prompt_style="animation__walking_and_idle",
        num_images=1,
        return_spritesheet=True,
    )
    resp = client.infer(req)
    assert len(resp.base64_images) >= 1
    raw = base64.b64decode(resp.base64_images[0])
    # PNG files start with 0x89504E47
    assert raw[:4] == b"\x89PNG"
