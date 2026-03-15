"""Live tests for cost estimation."""

from __future__ import annotations

from pag.models import InferenceRequest


def test_cost_check_returns_cost(client):
    """Cost check should return a cost without generating images."""
    req = InferenceRequest(
        prompt="a dragon",
        width=128,
        height=128,
        prompt_style="rd_pro__default",
        num_images=1,
        check_cost=True,
    )
    resp = client.infer(req)
    assert resp.model == "check_cost"
    assert resp.balance_cost > 0
    assert resp.remaining_balance >= 0
    assert resp.base64_images == []


def test_cost_check_multiple_images(client):
    """Cost for multiple images should be higher than for one."""
    common = dict(
        prompt="a dragon",
        width=128,
        height=128,
        prompt_style="rd_pro__default",
        check_cost=True,
    )
    resp1 = client.infer(InferenceRequest(num_images=1, **common))
    resp2 = client.infer(InferenceRequest(num_images=4, **common))
    assert resp2.balance_cost >= resp1.balance_cost
