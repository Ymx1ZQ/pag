"""Tests for pag.models."""

import pytest
from pydantic import ValidationError

from pag.models import (
    InferenceRequest,
    InferenceResponse,
    StyleCreateRequest,
    StyleUpdateRequest,
)


class TestInferenceRequest:
    def test_minimal_valid(self):
        req = InferenceRequest(
            prompt="a cat", width=128, height=128, prompt_style="rd_pro__default"
        )
        assert req.prompt == "a cat"
        assert req.num_images == 1
        assert req.check_cost is False

    def test_all_fields(self):
        req = InferenceRequest(
            prompt="a cat",
            width=256,
            height=256,
            prompt_style="rd_pro__fantasy",
            num_images=4,
            check_cost=True,
            seed=42,
            tile_x=True,
            tile_y=True,
            remove_bg=True,
            return_spritesheet=True,
        )
        assert req.seed == 42
        assert req.tile_x is True
        assert req.return_spritesheet is True

    def test_minimum_size_16(self):
        req = InferenceRequest(
            prompt="x", width=16, height=16, prompt_style="rd_fast__low_res"
        )
        assert req.width == 16

    def test_width_too_small(self):
        with pytest.raises(ValidationError):
            InferenceRequest(
                prompt="x", width=10, height=128, prompt_style="rd_pro__default"
            )

    def test_width_too_large(self):
        with pytest.raises(ValidationError):
            InferenceRequest(
                prompt="x", width=500, height=128, prompt_style="rd_pro__default"
            )

    def test_num_images_zero(self):
        with pytest.raises(ValidationError):
            InferenceRequest(
                prompt="x", width=128, height=128,
                prompt_style="rd_pro__default", num_images=0,
            )


class TestInferenceResponse:
    def test_parse(self):
        resp = InferenceResponse(
            created_at=1733425519,
            balance_cost=0.25,
            base64_images=["abc123"],
            model="rd_pro",
            remaining_balance=100.75,
        )
        assert resp.balance_cost == 0.25
        assert len(resp.base64_images) == 1


class TestStyleCreateRequest:
    def test_minimal(self):
        req = StyleCreateRequest(name="my style")
        assert req.name == "my style"
        assert req.description is None

    def test_min_width_bounds(self):
        with pytest.raises(ValidationError):
            StyleCreateRequest(name="x", min_width=50)

    def test_min_width_upper_bound(self):
        with pytest.raises(ValidationError):
            StyleCreateRequest(name="x", min_width=300)


class TestStyleUpdateRequest:
    def test_all_optional(self):
        req = StyleUpdateRequest()
        assert req.name is None
