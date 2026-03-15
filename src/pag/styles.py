"""Static registry of Retro Diffusion styles with valid size ranges."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class StyleInfo:
    """Metadata for a single prompt style."""

    key: str  # full prompt_style value, e.g. "rd_pro__default"
    model: str  # rd_pro | rd_fast | rd_plus | animation
    label: str  # human-readable name
    min_w: int
    max_w: int
    min_h: int
    max_h: int
    square_only: bool = False


def _pro(name: str, label: str | None = None) -> StyleInfo:
    return StyleInfo(
        key=f"rd_pro__{name}",
        model="rd_pro",
        label=label or name.replace("_", " ").title(),
        min_w=96, max_w=256, min_h=96, max_h=256,
    )


def _fast(
    name: str,
    label: str | None = None,
    *,
    min_s: int = 64,
    max_s: int = 384,
) -> StyleInfo:
    return StyleInfo(
        key=f"rd_fast__{name}",
        model="rd_fast",
        label=label or name.replace("_", " ").title(),
        min_w=min_s, max_w=max_s, min_h=min_s, max_h=max_s,
    )


def _plus(
    name: str,
    label: str | None = None,
    *,
    min_s: int = 64,
    max_s: int = 384,
) -> StyleInfo:
    return StyleInfo(
        key=f"rd_plus__{name}",
        model="rd_plus",
        label=label or name.replace("_", " ").title(),
        min_w=min_s, max_w=max_s, min_h=min_s, max_h=max_s,
    )


def _anim(
    name: str,
    w: int,
    h: int,
    *,
    label: str | None = None,
    max_w: int | None = None,
    max_h: int | None = None,
    square_only: bool = False,
) -> StyleInfo:
    return StyleInfo(
        key=f"animation__{name}",
        model="animation",
        label=label or name.replace("_", " ").title(),
        min_w=w, max_w=max_w or w,
        min_h=h, max_h=max_h or h,
        square_only=square_only,
    )


# ── Style catalogue ─────────────────────────────────────────────────────────
# Source of truth: https://github.com/Retro-Diffusion/api-examples

RD_PRO_STYLES: list[StyleInfo] = [
    _pro("default"),
    _pro("painterly"),
    _pro("fantasy"),
    _pro("ui_panel", "UI Panel"),
    _pro("horror"),
    _pro("scifi", "Sci-Fi"),
    _pro("simple"),
    _pro("isometric"),
    _pro("topdown", "Top-Down"),
    _pro("platformer"),
    _pro("dungeon_map", "Dungeon Map"),
    _pro("edit"),
    _pro("pixelate"),
    _pro("spritesheet", "Sprite Sheet"),
    _pro("typography"),
    _pro("hexagonal_tiles", "Hexagonal Tiles"),
    _pro("fps_weapon", "FPS Weapon"),
    _pro("inventory_items", "Inventory Items"),
]

RD_FAST_STYLES: list[StyleInfo] = [
    _fast("default"),
    _fast("retro"),
    _fast("simple"),
    _fast("detailed"),
    _fast("anime"),
    _fast("game_asset", "Game Asset"),
    _fast("portrait"),
    _fast("texture"),
    _fast("ui", "UI"),
    _fast("item_sheet", "Item Sheet"),
    _fast("character_turnaround", "Character Turnaround"),
    _fast("1_bit", "1-Bit"),
    _fast("low_res", "Low Res", min_s=16, max_s=128),
    _fast("mc_item", "MC Item", min_s=16, max_s=128),
    _fast("mc_texture", "MC Texture", min_s=16, max_s=128),
    _fast("no_style", "No Style"),
]

RD_PLUS_STYLES: list[StyleInfo] = [
    _plus("default"),
    _plus("retro"),
    _plus("watercolor"),
    _plus("textured"),
    _plus("cartoon"),
    _plus("ui_element", "UI Element"),
    _plus("item_sheet", "Item Sheet"),
    _plus("character_turnaround", "Character Turnaround"),
    _plus("environment"),
    _plus("topdown_map", "Top-Down Map"),
    _plus("topdown_asset", "Top-Down Asset"),
    _plus("isometric", "Isometric"),
    _plus("isometric_asset", "Isometric Asset"),
    _plus("classic", "Classic", min_s=32, max_s=192),
    _plus("low_res", "Low Res", min_s=16, max_s=128),
    _plus("mc_item", "MC Item", min_s=16, max_s=128),
    _plus("mc_texture", "MC Texture", min_s=16, max_s=128),
    _plus("topdown_item", "Top-Down Item", min_s=16, max_s=128),
    _plus("skill_icon", "Skill Icon", min_s=16, max_s=128),
]

RD_TILE_STYLES: list[StyleInfo] = [
    StyleInfo(key="rd_tile__tileset", model="rd_tile", label="Tileset",
             min_w=16, max_w=32, min_h=16, max_h=32),
    StyleInfo(key="rd_tile__tileset_advanced", model="rd_tile", label="Tileset Advanced",
             min_w=16, max_w=32, min_h=16, max_h=32),
    StyleInfo(key="rd_tile__single_tile", model="rd_tile", label="Single Tile",
             min_w=16, max_w=64, min_h=16, max_h=64),
    StyleInfo(key="rd_tile__tile_variation", model="rd_tile", label="Tile Variation",
             min_w=16, max_w=128, min_h=16, max_h=128),
    StyleInfo(key="rd_tile__tile_object", model="rd_tile", label="Tile Object",
             min_w=16, max_w=96, min_h=16, max_h=96),
    StyleInfo(key="rd_tile__scene_object", model="rd_tile", label="Scene Object",
             min_w=64, max_w=384, min_h=64, max_h=384),
]

ANIMATION_STYLES: list[StyleInfo] = [
    _anim("any_animation", 64, 64, label="Any Animation"),
    _anim("8_dir_rotation", 80, 80, label="8-Dir Rotation"),
    _anim("four_angle_walking", 48, 48, label="Four-Angle Walking"),
    _anim("walking_and_idle", 48, 48, label="Walking & Idle"),
    _anim("small_sprites", 32, 32, label="Small Sprites"),
    _anim("vfx", 24, 24, max_w=96, max_h=96, label="VFX", square_only=True),
]

ALL_STYLES: list[StyleInfo] = (
    RD_PRO_STYLES + RD_FAST_STYLES + RD_PLUS_STYLES
    + RD_TILE_STYLES + ANIMATION_STYLES
)

_STYLE_MAP: dict[str, StyleInfo] = {s.key: s for s in ALL_STYLES}


def get_style(key: str) -> StyleInfo | None:
    """Look up a style by its full key (e.g. ``rd_pro__default``)."""
    return _STYLE_MAP.get(key)


def list_styles(model: str | None = None) -> list[StyleInfo]:
    """Return styles, optionally filtered by model."""
    if model is None:
        return list(ALL_STYLES)
    return [s for s in ALL_STYLES if s.model == model]


def validate_size(style: StyleInfo, width: int, height: int) -> None:
    """Raise ``ValueError`` if *width*/*height* fall outside the style's range."""
    if not (style.min_w <= width <= style.max_w):
        raise ValueError(
            f"Width {width} out of range [{style.min_w}, {style.max_w}] "
            f"for style {style.key}"
        )
    if not (style.min_h <= height <= style.max_h):
        raise ValueError(
            f"Height {height} out of range [{style.min_h}, {style.max_h}] "
            f"for style {style.key}"
        )
    if style.square_only and width != height:
        raise ValueError(
            f"Style {style.key} requires square dimensions, "
            f"got {width}x{height}"
        )
