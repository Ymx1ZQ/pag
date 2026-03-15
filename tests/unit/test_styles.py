"""Tests for pag.styles."""

import pytest

from pag.styles import (
    ALL_STYLES,
    ANIMATION_STYLES,
    RD_ADVANCED_ANIMATION_STYLES,
    RD_FAST_STYLES,
    RD_PLUS_STYLES,
    RD_PRO_STYLES,
    RD_TILE_STYLES,
    get_style,
    list_styles,
    validate_size,
)


def test_all_styles_count():
    total = (
        len(RD_PRO_STYLES) + len(RD_FAST_STYLES) + len(RD_PLUS_STYLES)
        + len(RD_TILE_STYLES) + len(ANIMATION_STYLES)
        + len(RD_ADVANCED_ANIMATION_STYLES)
    )
    assert len(ALL_STYLES) == total


def test_no_duplicate_keys():
    keys = [s.key for s in ALL_STYLES]
    assert len(keys) == len(set(keys))


def test_get_style_found():
    style = get_style("rd_pro__default")
    assert style is not None
    assert style.model == "rd_pro"


def test_get_style_not_found():
    assert get_style("nonexistent") is None


def test_list_styles_all():
    assert list_styles() == ALL_STYLES


def test_list_styles_by_model():
    pro = list_styles("rd_pro")
    assert all(s.model == "rd_pro" for s in pro)
    assert len(pro) == len(RD_PRO_STYLES)


def test_list_styles_animation():
    anims = list_styles("animation")
    assert len(anims) == len(ANIMATION_STYLES)


def test_validate_size_valid():
    style = get_style("rd_pro__default")
    validate_size(style, 128, 128)  # should not raise


def test_validate_size_width_too_small():
    style = get_style("rd_pro__default")
    with pytest.raises(ValueError, match="Width.*out of range"):
        validate_size(style, 32, 128)


def test_validate_size_height_too_large():
    style = get_style("rd_pro__default")
    with pytest.raises(ValueError, match="Height.*out of range"):
        validate_size(style, 128, 512)


def test_validate_size_square_only():
    style = get_style("animation__vfx")
    assert style is not None
    with pytest.raises(ValueError, match="square"):
        validate_size(style, 48, 64)


def test_validate_size_square_only_valid():
    style = get_style("animation__vfx")
    validate_size(style, 48, 48)  # should not raise


def test_style_keys_prefixed():
    for s in ALL_STYLES:
        assert s.key.startswith((
            "rd_pro__", "rd_fast__", "rd_plus__", "rd_tile__",
            "animation__", "rd_advanced_animation__",
        ))


# ── Verify correct style names match official API ───────────────────────────


def test_old_style_names_removed():
    """Styles that don't exist in the official API must not be in the registry."""
    removed = [
        "rd_fast__minecraft_block",
        "rd_fast__minecraft_item",
        "rd_fast__minecraft_mob",
        "rd_plus__topdown_character",
        "rd_plus__topdown_tileset",
        "rd_plus__isometric_object",
        "rd_plus__isometric_environment",
        "rd_plus__minecraft_block",
        "rd_plus__minecraft_item",
        "rd_plus__minecraft_mob",
    ]
    for key in removed:
        assert get_style(key) is None, f"{key} should not exist"


def test_correct_style_names_present():
    """Styles renamed to match the official API must exist."""
    expected = [
        "rd_fast__mc_item",
        "rd_fast__mc_texture",
        "rd_plus__topdown_map",
        "rd_plus__topdown_asset",
        "rd_plus__isometric",
        "rd_plus__isometric_asset",
        "rd_plus__mc_item",
        "rd_plus__mc_texture",
    ]
    for key in expected:
        assert get_style(key) is not None, f"{key} should exist"


# ── Verify per-style size limits match official API ─────────────────────────


@pytest.mark.parametrize("key,min_s,max_s", [
    ("rd_fast__low_res", 16, 128),
    ("rd_fast__mc_item", 16, 128),
    ("rd_fast__mc_texture", 16, 128),
    ("rd_plus__classic", 32, 192),
    ("rd_plus__low_res", 16, 128),
    ("rd_plus__mc_item", 16, 128),
    ("rd_plus__mc_texture", 16, 128),
    ("rd_plus__topdown_item", 16, 128),
    ("rd_plus__skill_icon", 16, 128),
])
def test_per_style_size_limits(key, min_s, max_s):
    style = get_style(key)
    assert style is not None, f"{key} not found"
    assert style.min_w == min_s
    assert style.min_h == min_s
    assert style.max_w == max_s
    assert style.max_h == max_s


def test_validate_low_res_size():
    """Low-res styles should accept 16x16."""
    style = get_style("rd_fast__low_res")
    validate_size(style, 16, 16)  # should not raise


def test_validate_low_res_rejects_below_min():
    style = get_style("rd_fast__low_res")
    with pytest.raises(ValueError, match="Width.*out of range"):
        validate_size(style, 8, 16)


def test_validate_low_res_rejects_above_max():
    style = get_style("rd_fast__low_res")
    with pytest.raises(ValueError, match="Width.*out of range"):
        validate_size(style, 256, 128)


# ── Advanced animation styles ──────────────────────────────────────────────


def test_advanced_animation_styles_exist():
    expected = [
        "rd_advanced_animation__attack",
        "rd_advanced_animation__crouch",
        "rd_advanced_animation__custom_action",
        "rd_advanced_animation__destroy",
        "rd_advanced_animation__idle",
        "rd_advanced_animation__jump",
        "rd_advanced_animation__subtle_motion",
        "rd_advanced_animation__walking",
    ]
    for key in expected:
        assert get_style(key) is not None, f"{key} should exist"


def test_list_styles_rd_advanced_animation():
    adv = list_styles("rd_advanced_animation")
    assert len(adv) == len(RD_ADVANCED_ANIMATION_STYLES)
    assert all(s.model == "rd_advanced_animation" for s in adv)


def test_advanced_animation_size_range():
    style = get_style("rd_advanced_animation__walking")
    assert style.min_w == 32
    assert style.max_w == 256
    validate_size(style, 96, 96)  # should not raise


# ── Tileset styles ──────────────────────────────────────────────────────────


def test_tileset_styles_exist():
    expected = [
        "rd_tile__tileset", "rd_tile__tileset_advanced",
        "rd_tile__single_tile", "rd_tile__tile_variation",
        "rd_tile__tile_object", "rd_tile__scene_object",
    ]
    for key in expected:
        assert get_style(key) is not None, f"{key} should exist"


def test_list_styles_rd_tile():
    tiles = list_styles("rd_tile")
    assert len(tiles) == len(RD_TILE_STYLES)
    assert all(s.model == "rd_tile" for s in tiles)


@pytest.mark.parametrize("key,min_s,max_s", [
    ("rd_tile__tileset", 16, 32),
    ("rd_tile__tileset_advanced", 16, 32),
    ("rd_tile__single_tile", 16, 64),
    ("rd_tile__tile_variation", 16, 128),
    ("rd_tile__tile_object", 16, 96),
    ("rd_tile__scene_object", 64, 384),
])
def test_tileset_size_limits(key, min_s, max_s):
    style = get_style(key)
    assert style.min_w == min_s
    assert style.max_w == max_s
