"""Tests for pag.styles."""

import pytest

from pag.styles import (
    ALL_STYLES,
    ANIMATION_STYLES,
    RD_FAST_STYLES,
    RD_PLUS_STYLES,
    RD_PRO_STYLES,
    get_style,
    list_styles,
    validate_size,
)


def test_all_styles_count():
    total = len(RD_PRO_STYLES) + len(RD_FAST_STYLES) + len(RD_PLUS_STYLES) + len(ANIMATION_STYLES)
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
        assert s.key.startswith(("rd_pro__", "rd_fast__", "rd_plus__", "animation__"))
