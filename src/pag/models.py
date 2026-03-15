"""Pydantic models for Retro Diffusion API requests and responses."""

from __future__ import annotations

from pydantic import BaseModel, Field


# ── Inference ────────────────────────────────────────────────────────────────


class InferenceRequest(BaseModel):
    """Body for POST /v1/inferences."""

    prompt: str
    width: int = Field(ge=16, le=384)
    height: int = Field(ge=16, le=384)
    prompt_style: str
    num_images: int = Field(default=1, ge=1)
    check_cost: bool = False
    seed: int | None = None
    reference_images: list[str] | None = None
    tile_x: bool = False
    tile_y: bool = False
    remove_bg: bool = False
    input_image: str | None = None
    return_spritesheet: bool | None = None
    strength: float | None = Field(default=None, ge=0.0, le=1.0)
    input_palette: str | None = None
    return_pre_palette: bool | None = None
    bypass_prompt_expansion: bool | None = None
    include_downloadable_data: bool | None = None
    return_non_bg_removed: bool | None = None
    upscale_output_factor: int | None = None
    extra_prompt: str | None = None
    extra_input_image: str | None = None
    frames_duration: int | None = None


class InferenceResponse(BaseModel):
    """Response from POST /v1/inferences."""

    created_at: int
    balance_cost: float
    base64_images: list[str]
    model: str
    remaining_balance: float


# ── Custom styles ────────────────────────────────────────────────────────────


class StyleCreateRequest(BaseModel):
    """Body for POST /v1/styles."""

    name: str
    description: str | None = None
    style_icon: str | None = None
    reference_images: list[str] | None = None
    reference_caption: str | None = None
    apply_prompt_fixer: bool | None = None
    llm_instructions: str | None = None
    expanded_llm_instructions: str | None = None
    user_prompt_template: str | None = None
    force_palette: str | None = None
    force_bg_removal: bool | None = None
    min_width: int | None = Field(default=None, ge=96, le=256)
    min_height: int | None = Field(default=None, ge=96, le=256)


class StyleUpdateRequest(BaseModel):
    """Body for PATCH /v1/styles/{style_id}."""

    name: str | None = None
    description: str | None = None
    style_icon: str | None = None
    reference_images: list[str] | None = None
    reference_caption: str | None = None
    apply_prompt_fixer: bool | None = None
    llm_instructions: str | None = None
    expanded_llm_instructions: str | None = None
    user_prompt_template: str | None = None
    force_palette: str | None = None
    force_bg_removal: bool | None = None
    min_width: int | None = Field(default=None, ge=96, le=256)
    min_height: int | None = Field(default=None, ge=96, le=256)


class StyleResponse(BaseModel):
    """Response from style CRUD operations."""

    id: str
    name: str
    description: str | None = None
