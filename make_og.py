#!/usr/bin/env python3
"""Generate a dedicated OpenGraph card image (1200x630) from a source image.

The source image (usually the post's feature image) is never modified: the
derivative is written to images/og/<name>-og.jpg. Run from the blog root:

    uv run --with pillow ./make_og.py images/voyagerdoc.jpg

Prints the front-matter line to paste into the post, e.g.:

    og_image: https://eve.gd/images/og/voyagerdoc-og.jpg
"""

import sys
import json
import pathlib

from PIL import Image, ImageOps

OG_SIZE = (1200, 630)
JPEG_QUALITY = 85


def _load_cfg():
    cfg_path = pathlib.Path("sequoia.json")
    if cfg_path.exists():
        return json.loads(cfg_path.read_text())
    return {}


def crop_box(width, height, target=OG_SIZE):
    """Centred crop box (left, top, right, bottom) at the target aspect."""
    target_ratio = target[0] / target[1]
    ratio = width / height
    if ratio > target_ratio:
        # too wide: keep full height, trim the sides
        crop_w = round(height * target_ratio)
        left = (width - crop_w) // 2
        return (left, 0, left + crop_w, height)
    if ratio < target_ratio:
        # too tall: keep full width, trim top and bottom
        crop_h = round(width / target_ratio)
        top = (height - crop_h) // 2
        return (0, top, width, top + crop_h)
    return (0, 0, width, height)


def output_path(src, og_dir):
    """images/foo.png -> <og_dir>/foo-og.jpg"""
    return pathlib.Path(og_dir) / f"{pathlib.Path(src).stem}-og.jpg"


def make_og(src, og_dir, target=OG_SIZE):
    """Write the derivative; return (out_path, warning_or_None).

    The source file is left untouched. A warning string is returned when the
    source is smaller than the target and had to be upscaled.
    """
    src = pathlib.Path(src)
    og_dir = pathlib.Path(og_dir)
    og_dir.mkdir(parents=True, exist_ok=True)
    out = output_path(src, og_dir)

    with Image.open(src) as im:
        im = ImageOps.exif_transpose(im)
        im = im.crop(crop_box(im.width, im.height, target))
        warning = None
        if im.width < target[0]:
            warning = (
                f"{src}: source is smaller than {target[0]}x{target[1]} "
                f"after cropping ({im.width}x{im.height}); upscaled — "
                "the card may look soft."
            )
        im = im.resize(target, Image.LANCZOS)
        if im.mode not in ("RGB", "L"):
            im = im.convert("RGB")
        im.save(out, format="JPEG", quality=JPEG_QUALITY,
                optimize=True, progressive=True)
    return out, warning


def front_matter_line(out_path, site_url):
    return f"og_image: {site_url.rstrip('/')}/{pathlib.Path(out_path).as_posix()}"


def main(argv):
    if not argv:
        print("usage: make_og.py <image> [<image> ...]", file=sys.stderr)
        return 2

    cfg = _load_cfg()
    site_url = cfg.get("siteUrl", "https://eve.gd")
    images_dir = pathlib.Path(cfg.get("imagesDir", "./images"))
    og_dir = images_dir / "og"

    status = 0
    for arg in argv:
        src = pathlib.Path(arg)
        if not src.exists():
            # allow a bare filename, resolved against imagesDir
            candidate = images_dir / arg
            if candidate.exists():
                src = candidate
            else:
                print(f"error: {arg} not found", file=sys.stderr)
                status = 1
                continue
        out, warning = make_og(src, og_dir)
        if warning:
            print(f"warning: {warning}", file=sys.stderr)
        size_kb = out.stat().st_size // 1024
        print(f"wrote {out} (1200x630, {size_kb} KB)")
        print(front_matter_line(out, site_url))
    return status


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
