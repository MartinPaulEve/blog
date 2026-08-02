"""Behavioural tests for make_og.py (run from the blog root):

    uv run --with pillow --with pytest -m pytest _tests/test_make_og.py
"""

import sys
import pathlib

import pytest
from PIL import Image

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

import make_og


def _make_image(path, size, color=(120, 40, 40)):
    im = Image.new("RGB", size, color)
    im.save(path)
    return path


class TestCropBox:
    def test_wide_source_crops_sides_only(self):
        # 2:1 source -> 40:21 target crop keeps full height, trims width
        left, top, right, bottom = make_og.crop_box(2000, 1000)
        assert (top, bottom) == (0, 1000)
        assert right - left == pytest.approx(1000 * 1200 / 630, abs=1)
        # centred horizontally
        assert left == pytest.approx(2000 - right, abs=1)

    def test_tall_source_crops_top_and_bottom_only(self):
        left, top, right, bottom = make_og.crop_box(1200, 2000)
        assert (left, right) == (0, 1200)
        assert bottom - top == pytest.approx(1200 * 630 / 1200, abs=1)
        assert top == pytest.approx(2000 - bottom, abs=1)

    def test_exact_aspect_is_untouched(self):
        assert make_og.crop_box(2400, 1260) == (0, 0, 2400, 1260)


class TestOutputPath:
    def test_derives_og_jpg_name(self, tmp_path):
        out = make_og.output_path(pathlib.Path("images/voyagerdoc.jpg"), tmp_path)
        assert out == tmp_path / "voyagerdoc-og.jpg"

    def test_png_source_still_becomes_jpg(self, tmp_path):
        out = make_og.output_path(pathlib.Path("images/cover.png"), tmp_path)
        assert out == tmp_path / "cover-og.jpg"


class TestMakeOg:
    def test_output_is_exactly_1200_by_630(self, tmp_path):
        src = _make_image(tmp_path / "wide.jpg", (2000, 1000))
        out, warning = make_og.make_og(src, tmp_path / "og")
        with Image.open(out) as im:
            assert im.size == (1200, 630)
        assert warning is None

    def test_source_file_is_not_modified(self, tmp_path):
        src = _make_image(tmp_path / "wide.jpg", (2000, 1000))
        before = src.read_bytes()
        make_og.make_og(src, tmp_path / "og")
        assert src.read_bytes() == before

    def test_small_source_upscales_with_warning(self, tmp_path):
        src = _make_image(tmp_path / "small.jpg", (800, 400))
        out, warning = make_og.make_og(src, tmp_path / "og")
        with Image.open(out) as im:
            assert im.size == (1200, 630)
        assert warning is not None

    def test_tall_source_still_yields_landscape_card(self, tmp_path):
        src = _make_image(tmp_path / "tall.png", (1300, 2600))
        out, _ = make_og.make_og(src, tmp_path / "og")
        with Image.open(out) as im:
            assert im.size == (1200, 630)
            assert im.format == "JPEG"


class TestFrontMatterLine:
    def test_line_is_absolute_url(self):
        line = make_og.front_matter_line(
            pathlib.Path("images/og/voyagerdoc-og.jpg"), "https://eve.gd"
        )
        assert line == "og_image: https://eve.gd/images/og/voyagerdoc-og.jpg"
