"""Tests for pag.models."""

import pytest
from pydantic import ValidationError

from pag.models import (
    EditRequest,
    EditResponse,
    InferenceRequest,
    InferenceResponse,
    StyleCreateRequest,
    StyleResponse,
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

    def test_img2img_fields(self):
        req = InferenceRequest(
            prompt="x", width=128, height=128,
            prompt_style="rd_pro__default",
            input_image="base64data",
            strength=0.8,
        )
        assert req.strength == 0.8
        assert req.input_image == "base64data"

    def test_strength_out_of_range(self):
        with pytest.raises(ValidationError):
            InferenceRequest(
                prompt="x", width=128, height=128,
                prompt_style="rd_pro__default", strength=1.5,
            )

    def test_palette_fields(self):
        req = InferenceRequest(
            prompt="x", width=128, height=128,
            prompt_style="rd_pro__default",
            input_palette="base64palette",
            return_pre_palette=True,
        )
        assert req.input_palette == "base64palette"
        assert req.return_pre_palette is True

    def test_advanced_flags(self):
        req = InferenceRequest(
            prompt="x", width=128, height=128,
            prompt_style="rd_pro__default",
            bypass_prompt_expansion=True,
            include_downloadable_data=True,
            return_non_bg_removed=True,
            upscale_output_factor=1,
        )
        assert req.bypass_prompt_expansion is True
        assert req.include_downloadable_data is True
        assert req.upscale_output_factor == 1

    def test_tileset_fields(self):
        req = InferenceRequest(
            prompt="stones", width=32, height=32,
            prompt_style="rd_tile__tileset_advanced",
            extra_prompt="green grass",
            extra_input_image="base64extra",
        )
        assert req.extra_prompt == "green grass"
        assert req.extra_input_image == "base64extra"

    def test_frames_duration(self):
        req = InferenceRequest(
            prompt="walk", width=96, height=96,
            prompt_style="rd_advanced_animation__walking",
            frames_duration=8,
        )
        assert req.frames_duration == 8


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

    def test_optional_fields_default(self):
        resp = InferenceResponse(
            created_at=1, balance_cost=0.1,
            base64_images=[], model="rd_pro", remaining_balance=99.0,
        )
        assert resp.output_images == []
        assert resp.output_urls == []
        assert resp.downloadable_data is None

    def test_downloadable_data(self):
        resp = InferenceResponse(
            created_at=1, balance_cost=0.1,
            base64_images=["x"], model="rd_pro", remaining_balance=99.0,
            downloadable_data={"downloadable_json": {"type": "item_atlas"}},
        )
        assert resp.downloadable_data["downloadable_json"]["type"] == "item_atlas"


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


class TestEditModels:
    def test_edit_request(self):
        req = EditRequest(prompt="add a hat", inputImageBase64="base64data")
        assert req.prompt == "add a hat"
        assert req.inputImageBase64 == "base64data"

    def test_edit_response(self):
        resp = EditResponse(outputImageBase64="result", remaining_credits=99.5)
        assert resp.outputImageBase64 == "result"
        assert resp.remaining_credits == 99.5


class TestStyleResponse:
    def test_minimal(self):
        resp = StyleResponse(id="s1", name="my style")
        assert resp.prompt_style is None
        assert resp.deleted is None

    def test_full_response(self):
        resp = StyleResponse(
            id="s1", name="my style",
            prompt_style="user__my_style_abc",
            type="user",
            created_at=1771557653,
            updated_at=1771557653,
        )
        assert resp.prompt_style == "user__my_style_abc"
        assert resp.type == "user"

    def test_delete_response(self):
        resp = StyleResponse(
            id="s1", name="my style",
            prompt_style="user__my_style_abc",
            deleted=True,
        )
        assert resp.deleted is True


class TestStyleUpdateRequest:
    def test_all_optional(self):
        req = StyleUpdateRequest()
        assert req.name is None
