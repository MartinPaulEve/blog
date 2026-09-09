"""Behavioural tests for the /pictures manage tool (run from the blog root):

    uv run --with pyyaml --with pillow --with pytest -m pytest _tests/test_pictures_manage.py
"""

import pathlib
import sys

import pytest
import yaml

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "_pictures"))

import manage


ENTRIES = [
    {
        "file": "/images/02.png",
        "description": "A picture of me on the seafront",
        "credit": "Photo: Martin Paul Eve, CC BY 4.0",
    },
    {
        "file": "/images/01.png",
        "description": "A picture of me in front of a white wall",
        "credit": "Photo: Martin Paul Eve, CC BY 4.0",
    },
]


# --- load/save -------------------------------------------------------------


def test_round_trip_preserves_entries_and_order(tmp_path):
    path = tmp_path / "pictures.yml"
    manage.save_pictures(path, ENTRIES)
    assert manage.load_pictures(path) == ENTRIES


def test_load_missing_file_is_empty_list(tmp_path):
    assert manage.load_pictures(tmp_path / "absent.yml") == []


def test_round_trip_preserves_unicode(tmp_path):
    path = tmp_path / "pictures.yml"
    entries = [{"file": "/images/café.png", "description": "Ünïcode", "credit": "©"}]
    manage.save_pictures(path, entries)
    assert manage.load_pictures(path) == entries
    assert "Ünïcode" in path.read_text(encoding="utf-8")


# --- normalize_file / find_picture ----------------------------------------


def test_bare_filename_lands_in_images():
    assert manage.normalize_file("02.png") == "/images/02.png"


def test_site_absolute_path_is_kept():
    assert manage.normalize_file("/images/sub/02.png") == "/images/sub/02.png"


def test_find_by_bare_name_and_full_path():
    assert manage.find_picture(ENTRIES, "01.png") == ENTRIES[1]
    assert manage.find_picture(ENTRIES, "/images/01.png") == ENTRIES[1]
    assert manage.find_picture(ENTRIES, "absent.png") is None


# --- add/update/remove -----------------------------------------------------


def test_add_appends_entry():
    out = manage.add_picture(ENTRIES, "new.jpg", "A new photo", "Credit line")
    assert len(out) == len(ENTRIES) + 1
    assert out[-1]["file"] == "/images/new.jpg"
    assert out[-1]["description"] == "A new photo"
    assert out[-1]["credit"] == "Credit line"
    assert ENTRIES[-1]["file"] == "/images/01.png"  # input untouched


def test_add_keeps_extra_fields():
    out = manage.add_picture([], "new.jpg", "d", "c", width=100, height=50, filesize=1234)
    assert out[0]["width"] == 100
    assert out[0]["height"] == 50
    assert out[0]["filesize"] == 1234


def test_add_refuses_duplicate_file():
    with pytest.raises(ValueError):
        manage.add_picture(ENTRIES, "02.png", "Again", "Credit")


def test_add_refuses_blank_description_or_credit():
    with pytest.raises(ValueError):
        manage.add_picture(ENTRIES, "new.jpg", "   ", "Credit")
    with pytest.raises(ValueError):
        manage.add_picture(ENTRIES, "new.jpg", "Desc", "")


def test_update_amends_only_given_fields():
    out = manage.update_picture(ENTRIES, "02.png", description="On the seafront, updated")
    assert out[0]["description"] == "On the seafront, updated"
    assert out[0]["credit"] == ENTRIES[0]["credit"]
    assert out[1] == ENTRIES[1]


def test_update_unknown_file_raises():
    with pytest.raises(ValueError):
        manage.update_picture(ENTRIES, "absent.png", description="x")


def test_remove_drops_entry_and_returns_it():
    out, removed = manage.remove_picture(ENTRIES, "02.png")
    assert removed == ENTRIES[0]
    assert [e["file"] for e in out] == ["/images/01.png"]


def test_remove_unknown_file_raises():
    with pytest.raises(ValueError):
        manage.remove_picture(ENTRIES, "absent.png")


# --- previews --------------------------------------------------------------


def test_preview_path_is_jpeg_in_previews_dir():
    assert manage.preview_path("/images/02.png") == "/images/pictures-previews/02.jpg"
    assert manage.preview_path("/images/eve_bald.jpeg") == (
        "/images/pictures-previews/eve_bald.jpg"
    )


def _write_png(path, size, mode="RGB"):
    from PIL import Image

    img = Image.new(mode, size, (200, 50, 50) if mode == "RGB" else (200, 50, 50, 128))
    img.save(path)


def test_generate_preview_scales_down_to_max_width(tmp_path):
    from PIL import Image

    src, dest = tmp_path / "big.png", tmp_path / "big.jpg"
    _write_png(src, (2000, 1000))
    w, h = manage.generate_preview(src, dest, max_width=700)
    assert (w, h) == (700, 350)
    with Image.open(dest) as out:
        assert out.size == (700, 350)
        assert out.format == "JPEG"


def test_generate_preview_never_upscales(tmp_path):
    from PIL import Image

    src, dest = tmp_path / "small.png", tmp_path / "small.jpg"
    _write_png(src, (400, 300))
    assert manage.generate_preview(src, dest, max_width=700) == (400, 300)
    with Image.open(dest) as out:
        assert out.size == (400, 300)


def test_generate_preview_flattens_alpha(tmp_path):
    src, dest = tmp_path / "alpha.png", tmp_path / "alpha.jpg"
    _write_png(src, (800, 600), mode="RGBA")
    manage.generate_preview(src, dest, max_width=700)
    assert dest.exists()


def test_image_info_reports_dimensions_and_size(tmp_path):
    src = tmp_path / "img.png"
    _write_png(src, (640, 480))
    info = manage.image_info(src)
    assert info["width"] == 640
    assert info["height"] == 480
    assert info["filesize"] == src.stat().st_size


# --- CLI -------------------------------------------------------------------


@pytest.fixture
def site(tmp_path):
    """A miniature blog root with one image on disk."""
    (tmp_path / "_data").mkdir()
    (tmp_path / "images").mkdir()
    _write_png(tmp_path / "images" / "new.png", (1200, 900))
    return tmp_path


def test_cli_add_writes_data_and_preview(site):
    rc = manage.main(
        [
            "--root", str(site),
            "add",
            "--file", "new.png",
            "--description", "A test image",
            "--credit", "Photo: Martin Paul Eve, CC BY 4.0",
        ]
    )
    assert rc == 0
    entries = yaml.safe_load((site / "_data" / "pictures.yml").read_text(encoding="utf-8"))
    assert entries[0]["file"] == "/images/new.png"
    assert entries[0]["description"] == "A test image"
    assert entries[0]["preview"] == "/images/pictures-previews/new.jpg"
    assert entries[0]["width"] == 1200
    assert entries[0]["height"] == 900
    assert (site / "images" / "pictures-previews" / "new.jpg").exists()


def test_cli_add_missing_image_fails(site):
    rc = manage.main(
        ["--root", str(site), "add", "--file", "ghost.png", "--description", "x", "--credit", "y"]
    )
    assert rc != 0
    assert not (site / "_data" / "pictures.yml").exists()


def test_cli_edit_amends_entry(site):
    manage.main(
        ["--root", str(site), "add", "--file", "new.png", "--description", "Old", "--credit", "c"]
    )
    rc = manage.main(
        ["--root", str(site), "edit", "new.png", "--description", "New description"]
    )
    assert rc == 0
    entries = yaml.safe_load((site / "_data" / "pictures.yml").read_text(encoding="utf-8"))
    assert entries[0]["description"] == "New description"
    assert entries[0]["credit"] == "c"


def test_cli_remove_drops_entry_and_preview(site):
    manage.main(
        ["--root", str(site), "add", "--file", "new.png", "--description", "d", "--credit", "c"]
    )
    rc = manage.main(["--root", str(site), "remove", "new.png", "--yes"])
    assert rc == 0
    entries = yaml.safe_load((site / "_data" / "pictures.yml").read_text(encoding="utf-8"))
    assert entries == []
    assert not (site / "images" / "pictures-previews" / "new.jpg").exists()
    assert (site / "images" / "new.png").exists()  # original untouched


def test_cli_remove_unknown_fails(site):
    rc = manage.main(["--root", str(site), "remove", "ghost.png", "--yes"])
    assert rc != 0
