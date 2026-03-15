"""Tests for pag.output."""

import base64
from pathlib import Path
from unittest.mock import patch

import pytest

from pag.output import decode_and_save, make_slug, resolve_filename, write_stdout


# ── make_slug ────────────────────────────────────────────────────────────────


class TestMakeSlug:
    def test_basic(self):
        assert make_slug("A Cool Corgi") == "a_cool_corgi"

    def test_special_chars(self):
        assert make_slug("hello! world? #1") == "hello_world_1"

    def test_truncation(self):
        result = make_slug("a" * 100, max_len=10)
        assert len(result) == 10

    def test_trailing_underscore_after_truncation(self):
        result = make_slug("hello world!!!", max_len=12)
        assert not result.endswith("_")

    def test_leading_trailing_stripped(self):
        assert make_slug("!!!hello!!!") == "hello"

    def test_empty_string(self):
        assert make_slug("") == ""


# ── resolve_filename ─────────────────────────────────────────────────────────


COMMON = dict(prompt="a cat", style="rd_pro__default", seed=None, is_animation=False)


class TestResolveFilename:
    @patch("pag.output.time")
    def test_default_single_image(self, mock_time):
        mock_time.time.return_value = 1700000000
        path = resolve_filename(index=0, num_images=1, **COMMON)
        assert path.name == "a_cat_1700000000.png"
        assert path.parent == Path.cwd()

    @patch("pag.output.time")
    def test_default_multiple_images(self, mock_time):
        mock_time.time.return_value = 1700000000
        p0 = resolve_filename(index=0, num_images=3, **COMMON)
        p1 = resolve_filename(index=1, num_images=3, **COMMON)
        assert p0.name == "a_cat_1700000000_0.png"
        assert p1.name == "a_cat_1700000000_1.png"

    def test_explicit_output_single(self):
        path = resolve_filename(
            index=0, num_images=1, output="my_art.png", **COMMON
        )
        assert path.name == "my_art.png"

    def test_explicit_output_no_ext(self):
        path = resolve_filename(
            index=0, num_images=1, output="my_art", **COMMON
        )
        assert path.suffix == ".png"

    def test_explicit_output_multiple(self):
        p0 = resolve_filename(
            index=0, num_images=2, output="art.png", **COMMON
        )
        p1 = resolve_filename(
            index=1, num_images=2, output="art.png", **COMMON
        )
        assert p0.name == "art_0.png"
        assert p1.name == "art_1.png"

    @patch("pag.output.time")
    def test_output_dir(self, mock_time, tmp_path):
        mock_time.time.return_value = 1700000000
        path = resolve_filename(
            index=0, num_images=1, output_dir=str(tmp_path), **COMMON
        )
        assert path.parent == tmp_path
        assert path.name == "a_cat_1700000000.png"

    @patch("pag.output.time")
    def test_name_pattern(self, mock_time):
        mock_time.time.return_value = 1700000000
        path = resolve_filename(
            index=0, num_images=1,
            name_pattern="{prompt_slug}_{style}_{seed}",
            **COMMON,
        )
        assert path.name == "a_cat_rd_pro_default_noseed.png"

    @patch("pag.output.time")
    def test_name_pattern_with_seed(self, mock_time):
        mock_time.time.return_value = 1700000000
        path = resolve_filename(
            index=0, num_images=1,
            name_pattern="{prompt_slug}_{seed}",
            prompt="a cat", style="rd_pro__default", seed=42,
            is_animation=False,
        )
        assert path.name == "a_cat_42.png"

    @patch("pag.output.time")
    def test_animation_uses_gif(self, mock_time):
        mock_time.time.return_value = 1700000000
        path = resolve_filename(
            index=0, num_images=1,
            prompt="fire", style="animation__vfx", seed=None,
            is_animation=True,
        )
        assert path.suffix == ".gif"


# ── decode_and_save ──────────────────────────────────────────────────────────


class TestDecodeAndSave:
    def test_writes_decoded_bytes(self, tmp_path):
        data = base64.b64encode(b"pixel data").decode()
        out = tmp_path / "test.png"
        result = decode_and_save(data, out)
        assert result == out
        assert out.read_bytes() == b"pixel data"

    def test_creates_parent_dirs(self, tmp_path):
        out = tmp_path / "sub" / "dir" / "test.png"
        data = base64.b64encode(b"x").decode()
        decode_and_save(data, out)
        assert out.exists()


# ── write_stdout ─────────────────────────────────────────────────────────────


class TestWriteStdout:
    def test_writes_to_stdout(self, capsys):
        write_stdout("aGVsbG8=")
        captured = capsys.readouterr()
        assert captured.out == "aGVsbG8=\n"
