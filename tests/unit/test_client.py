"""Tests for pag.client using respx mocks."""

import httpx
import pytest
import respx

from pag.client import APIError, RetroClient
from pag.models import InferenceRequest, StyleCreateRequest, StyleUpdateRequest


API_BASE = "https://api.retrodiffusion.ai/v1"


@pytest.fixture()
def client():
    c = RetroClient("test-key")
    yield c
    c.close()


# ── infer ────────────────────────────────────────────────────────────────────


@respx.mock
def test_infer_success(client):
    respx.post(f"{API_BASE}/inferences").mock(
        return_value=httpx.Response(
            200,
            json={
                "created_at": 1000,
                "balance_cost": 0.5,
                "base64_images": ["aGVsbG8="],
                "model": "rd_pro",
                "remaining_balance": 99.5,
            },
        )
    )
    req = InferenceRequest(
        prompt="a cat", width=128, height=128, prompt_style="rd_pro__default"
    )
    resp = client.infer(req)
    assert resp.model == "rd_pro"
    assert resp.base64_images == ["aGVsbG8="]
    assert resp.balance_cost == 0.5


@respx.mock
def test_infer_cost_check(client):
    respx.post(f"{API_BASE}/inferences").mock(
        return_value=httpx.Response(
            200,
            json={
                "created_at": 1000,
                "balance_cost": 0.25,
                "base64_images": [],
                "model": "check_cost",
                "remaining_balance": 100.0,
            },
        )
    )
    req = InferenceRequest(
        prompt="a cat", width=128, height=128,
        prompt_style="rd_pro__default", check_cost=True,
    )
    resp = client.infer(req)
    assert resp.model == "check_cost"
    assert resp.base64_images == []


@respx.mock
def test_infer_api_error(client):
    respx.post(f"{API_BASE}/inferences").mock(
        return_value=httpx.Response(401, json={"error": "invalid token"})
    )
    req = InferenceRequest(
        prompt="a cat", width=128, height=128, prompt_style="rd_pro__default"
    )
    with pytest.raises(APIError, match="401"):
        client.infer(req)


@respx.mock
def test_infer_excludes_none_fields(client):
    route = respx.post(f"{API_BASE}/inferences").mock(
        return_value=httpx.Response(
            200,
            json={
                "created_at": 1000,
                "balance_cost": 0.5,
                "base64_images": [],
                "model": "rd_pro",
                "remaining_balance": 99.5,
            },
        )
    )
    req = InferenceRequest(
        prompt="a cat", width=128, height=128, prompt_style="rd_pro__default"
    )
    client.infer(req)
    body = route.calls[0].request.content
    import json
    parsed = json.loads(body)
    assert "seed" not in parsed
    assert "reference_images" not in parsed
    assert "return_spritesheet" not in parsed


# ── styles CRUD ──────────────────────────────────────────────────────────────


@respx.mock
def test_create_style(client):
    respx.post(f"{API_BASE}/styles").mock(
        return_value=httpx.Response(
            200,
            json={"id": "style_123", "name": "my style", "description": None},
        )
    )
    resp = client.create_style(StyleCreateRequest(name="my style"))
    assert resp.id == "style_123"
    assert resp.name == "my style"


@respx.mock
def test_update_style(client):
    respx.patch(f"{API_BASE}/styles/style_123").mock(
        return_value=httpx.Response(
            200,
            json={"id": "style_123", "name": "renamed", "description": None},
        )
    )
    resp = client.update_style("style_123", StyleUpdateRequest(name="renamed"))
    assert resp.name == "renamed"


@respx.mock
def test_delete_style(client):
    respx.delete(f"{API_BASE}/styles/style_123").mock(
        return_value=httpx.Response(204)
    )
    client.delete_style("style_123")  # should not raise


# ── context manager ─────────────────────────────────────────────────────────


def test_context_manager():
    with RetroClient("test-key") as c:
        assert c is not None


# ── auth header ──────────────────────────────────────────────────────────────


@respx.mock
def test_sends_auth_header(client):
    route = respx.post(f"{API_BASE}/inferences").mock(
        return_value=httpx.Response(
            200,
            json={
                "created_at": 1000,
                "balance_cost": 0.5,
                "base64_images": [],
                "model": "rd_pro",
                "remaining_balance": 99.5,
            },
        )
    )
    req = InferenceRequest(
        prompt="x", width=128, height=128, prompt_style="rd_pro__default"
    )
    client.infer(req)
    assert route.calls[0].request.headers["X-RD-Token"] == "test-key"


# ── non-json error body ─────────────────────────────────────────────────────


@respx.mock
def test_api_error_non_json_body(client):
    respx.post(f"{API_BASE}/inferences").mock(
        return_value=httpx.Response(500, text="Internal Server Error")
    )
    req = InferenceRequest(
        prompt="x", width=128, height=128, prompt_style="rd_pro__default"
    )
    with pytest.raises(APIError, match="500"):
        client.infer(req)
